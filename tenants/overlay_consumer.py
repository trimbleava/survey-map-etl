# standard libs
import os, sys, time
import json

# third party libs
from channels.generic.websocket import WebsocketConsumer

# app modules
from system_modules import activate_customer
from system_modules import sys_utils 

import logging
logger = logging.getLogger("lsajang")

class OverlayConsumer(WebsocketConsumer):

    def connect(self):
        self.accept() 
        try:
            #
            # starts the system engines required by this consumer
            #
            etl, geo_rest, giseng, msg = sys_utils.start_engines()
            logger.info(msg)
            self._send(msg)

            #
            # activate the customer class to parse important data into its data members 
            #
            slug = self.scope['session']['slug']
            msg = f"Activating {slug} processor\n"
            logger.info(msg)
            self._send(msg)

            slugobj = activate_customer.activate(slug)

            cfg = slugobj.config_file()
            msg = f"Reading active config file {cfg}"
            logger.info(msg)
            self._send(msg)

            # get general part of config file
            region           = slugobj.customer_region
            survey_copyright = slugobj.survey_copyright
            survey_name      = slugobj.survey_name

            # mark session as modified
            self.scope["session"]["modified"] = True 

            # save in the cache
            self.scope['session']['region'] = region
            self.scope['session']['survey_copyright'] = survey_copyright
            self.scope['session']['survey_name'] = survey_name

            #
            # legend = "Legend:N|Dialog:N|Anno:SWGUID,"
            # decoration = legend.split("|")
            # legends[(fc, geom)] = decoration 
            # {('MHPSurvey', 'Polygon'): [False, False, ['SWGUID']]}
            #
            # get overlay part of config file 
            overlays, legends, msg = slugobj.read_overlay_data()
            print(legends)
            print(overlays)
            print("cccccccccccccccccccccccccccccccc")
            logger.info(msg)
            self._send(msg)

            # constructed sld filenames later down
            ovsld_filenames = {}
        
            #
            ############################ Process Overlay data #########################
            #
            # get the shapefiles data
            input_path = slugobj.input_path
            overlays_with_path = {}
            for path, subdirs, files in os.walk(input_path):
                for file in files:
                    for key, values in overlays.items():
                        if file.endswith(key) : 
                            shp = os.path.join(path,file)
                            overlays_with_path[shp] = values
                            continue

            # delete the old dict 
            overlays.clear()    
            
            msg = "Transforming overlays to web map services using geopackage"
            logger.info(msg)
            self._send(msg)
            
            gpkg = os.path.join(slugobj.output_path, "Overlay.gpkg")
            try:
                if os.path.exists(gpkg):
                    os.remove(gpkg)
            except Exception as e:
                self._send(str(e))
                
            layer_dict = overlays_with_path
            for fc, values in layer_dict.items():
                msg = f"    Transform in place for {fc}:\n"

                # read shapefile into gpd and remove extra columns
                msg += f"          Reading shapefiles into geopandas and removing extra columns\n"
                include_fields, filter = values
                gdf = giseng.gdf_read_shp(fc, include_fields, filter)
            
                # reproject and save as geopackage
                msg += f"          Re-projecting to 4326"
                gdf = giseng.reproject_to_4326(gdf)
                logger.info(msg)
                self._send(msg)
                
                # print few lines of the new data
                df_str = gdf.iloc[:5,1:-1].to_string()    
                df_rows = df_str.split("\n") 
                msg = "          Printing few lines of the new data\n"
                for row in df_rows:
                    msg += "          " + row + "\n"
                logger.info(msg)
                self._send(msg[:-1])

                fcname = sys_utils.filename(fc)
                msg = f"          Saving overlay {fcname} into geopackage {gpkg}\n"
                giseng.save_geopkg(gpkg, fcname, gdf)
                msg += f"          Finding closest bounding box for fast display\n" 
                # get bounding box for use in map
                xmin, ymin, xmax, ymax = giseng.bounds_simple(gdf)

                # first time populated here
                slugobj.ov_layers[fcname] = (xmin, ymin, xmax, ymax)

                logger.info(msg)
                self._send(msg)
                
                # plot the layer
                # gisengine.gdf_plot(gdf, fcname)

            msg = "Loading geopackage and publishing overlay layers into geoserver"
            logger.info(msg)
            self._send(msg) 

            pkgdir, pkgfile, storename = sys_utils.disect_path(gpkg)
            store = storename
            wrksp = slug
            
            msg = f"    Creating workspace {wrksp}\n"
            msg += geo_rest.create_workspace(wrksp)
            logger.info(msg)
            self._send(msg) 
            #
            msg = f"    Creating datastore {store}\n"
            msg += geo_rest.create_geopkg_datastore(store, pkgfile, wrksp, overwrite=False)
            logger.info(msg)
            self._send(msg) 

            # save to session
            self.scope["session"]["ov_store"] = store

            #
            # publish data
            msg = f"    Publishing geopackage layers"
            logger.info(msg)
            self._send(msg)

            msg = ""
            ov_layers = {}    # collecting layers for the cache

            for layer, bbox in slugobj.ov_layers.items():  
        
                try:
                    # store_name, layer, workspace, title, srid
                    title = layer
                    xyXY= bbox
                    ov_layers[layer] = bbox 

                    geo_rest.publish_geopkg_layer(store, layer, wrksp, title, xyXY)
                    msg = f"          Published {layer}"
                except Exception as e:
                    if "already exists" in str(e):
                        msg = f"          Layer {layer} already exists in store {store}, workspace {wrksp}"
                    else:
                        logger.info(str(e))
                        msg = "          " + str(e)
                
                logger.info(msg)
                self._send(msg) 

            msg = f"    Finished publishing geopackage layers\n"
            logger.info(msg)
            self._send(msg)

            # save to session  
            self.scope["session"]["ov_layers"] = ov_layers 
            

            #
            # legend = "Legend:N|Dialog:N|Anno:SWGUID,"
            # decoration = legend.split("|")
            # legends[(fc, geom)] = decoration 
            # {('MHPSurvey', 'Polygon'): [False, False, ['SWGUID']]}
            #         
            # get sld_path
            msg = "    Publishing styles for overlay layers"
            logger.info(msg)
            self._send(msg)

            #
            # these slds are pre-pared in this dirctory
            # directory tenants_dir/slug/sld/layer.sld
            #
            tenant_dir = self.scope["session"]["tenant_dir"] 
            sld_path = os.path.join(tenant_dir, wrksp, "sld")

            temp_ov_decoration = {} 
            msg = "" 

            for key, value in legends.items():
                legend, dialog, anno = value
                fc, geom = key
                sldfile = os.path.join(sld_path,fc+".sld") 
                #  
                # Note: assumes all the ovlayers has a style file already prepared
                # TODO re think to make it more like dynamic style, see how to 
                # incorporate geoserver default style file
                #
                if os.path.isfile(sldfile):
                    msg += f"          Publishing style for {fc}\n"
                    # construct the geoserver stylefile syntax and publish
                    style_name = wrksp+":"+fc 
                    msg += geo_rest.layer_sld(sldfile, wrksp, fc, style_name)
                    # save for cache
                    temp_ov_decoration[fc] = [geom, legend, dialog, anno]      

            msg += "    Finished publishing styles for overlay layers"
            logger.info(msg)
            self._send(msg)

            # save to session
            # {'southwestgaslv_controllablefitting': ['Point', 0, 1, ['SWGUID']]
            self.scope["session"]["ov_style"] = temp_ov_decoration
            
            #
            # at this time layers are in geoserver and we can extract their bbox
            # this is needed in map display to fitbounds into the active layers
            # so for now we save them in session to be passed into js
            # 
            capability_xml, stat = geo_rest.wms_getcapabilities(wrksp)
            layers_union_bbox =  sys_utils.parse_getcapability(capability_xml)
        
            # save to session
            self.scope["session"]["ovlayers_bbox"] = layers_union_bbox

            # save the session itself
            self.scope["session"]["ovlayers_status"] = 1         # need this for first time js not to give error
            self.scope["session"].save()   
            
            msg = "Processing Overlay layers completed ..........\n"
            logger.info(msg)
            self._send(msg)

        except Exception as e:
            msg = f"Some exception happend! {str(e)}\nReversing operations!"
            self.scope["session"]["modified"] = False
            self.scope["session"]["ovlayers_status"] = 0
            self._send(msg)
            return
        
    def _send(self, text_data):
        msg = json.dumps({"message": text_data})
        self.send(msg)

    # TODO - see if makes a difference in login into geoserver issue  
    def disconnect(self, close_code):
        msg = "Entered disconnect\n"
        logger.info(msg)
        pass


    def receive(self, text_data=None, bytes_data=None, **kwargs):
        msg = "Entered receive\n"
        logger.info(msg)

        error_code = 4011  # Daphne prohibits using 1011 / Server Error

        try:
            # super().receive() will call our receive_json()
            super().receive(text_data=text_data, bytes_data=bytes_data, **kwargs)
        except Exception:
            self.disconnect({'code': error_code})
            # Or, if you need websocket_disconnect (eg. for autogroups), try this:
            #
            # try:
            #     self.websocket_disconnect({'code': error_code})
            # except StopConsumer:
            #     pass

            # Try and close cleanly
            self.close(error_code)

            raise