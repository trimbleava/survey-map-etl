# standard libs
import os, sys, time
import json

# third party libs
from channels.generic.websocket import WebsocketConsumer

# app modules
from system_modules import activate_customer
from system_modules import sys_utils
from system_modules.geoserver_engine import GeoserverStyler
from heath_lsa import django_utils as djutils

import logging
logger = logging.getLogger("lsajang")

class SurveyMapConsumer(WebsocketConsumer):

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

            # get operational part of config file
            #
            # fc, geom, include, filter, legend in slugobj.operations
            #
            # operationals[f] = (include.split(","), filter)
            # {'MHPSurvey.shp': (['All', ''], {'filter': 'TODO'})}
            #
            # legend = "Legend:N|Dialog:N|Anno:SWGUID,"
            # decoration = legend.split("|")
            # op_legends[(fc, geom)] = decoration 
            # {('MHPSurvey', 'Polygon'): [False, False, ['SWGUID']]}
            #
            #
            operationals, legends, msg = slugobj.read_operational_data()
            logger.info(msg)
            self._send(msg) 
        
            # get sld filenames syntax
            opsld_filenames = slugobj.opsld_filenames()
            # {'MHPSurvey': 'D:/PROJECTS/survey-map-etl/OUTPUT/SWG/SLD/southwestgaslv_annual2023_mhpsurvey.sld'}
    
            #
            ############################ Operational data #########################
            #
            # find the operational input shapefiles - TODO: if they don't exist
            schema = self.scope["session"]["schema"] 
            input_path = slugobj.input_path
            operationals_with_path = {}
            for path, subdirs, files in os.walk(input_path):
                for file in files:
                    for key, value in operationals.items():
                        if file.endswith(key) :
                            shp = os.path.join(path,file)
                            operationals_with_path[shp] = value
                            continue
            
            msg = f"Transforming operational layers to web feature services"
            logger.info(msg)
            self._send(msg)

            conn_str = slugobj.pgdb_engin
            chunk_size = 10000    # seems to be optimal

            layer_dict = operationals_with_path
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
                msg = f"          Finding closest bounding box for fast display" 
                # get bounding box for use in map
                xmin, ymin, xmax, ymax = giseng.bounds_simple(gdf)
                slugobj.op_layers[fcname] = (xmin, ymin, xmax, ymax)

                logger.info(msg)
                self._send(msg)
                
                # plot the layer
                # gisengine.gdf_plot(gdf, fcname)
            
                tablename = slug+"_"+fcname.lower()
                msg = f"          Loading data into table {tablename}\n"
                
                # load data
                giseng.gdf_to_postgis(gdf, tablename, conn_str, schema=schema, 
                                        if_exists='append', chunksize=chunk_size)
                self._send(msg)
        
            msg = f"    Finished transforming operational layers\n"
            logger.info(msg)
            self._send(msg)

            wrksp = slug 
            msg = geo_rest.create_workspace(wrksp)
            logger.info(msg)  
            # do not display
            
            storename = slugobj.survey_name.lower()
            msg = f"    Creating feature store {storename}\n"
            # TODO: if exists 
            msg += geo_rest.featurestore_postgis(storename, wrksp, overwrite=False, schema=schema)
            msg += "    Finished creating feature store\n"
            logger.info(msg)
            self._send(msg)

            # save into session
            self.scope["session"]["op_store"] = storename       

            #
            # parse the display constraints from config file
            # and create sld files based on legend from config file
            #
            geostyler = GeoserverStyler() 
            temp_op_decoration = {}
                    
            msg = "    Creating style files for operational layers\n"
            i = 0      # start color number index, see geoserver engine
            for key, value in legends.items():
                legend, dialog, anno = value
                fc, geom = key
                tablename = slug+"_"+fc.lower()
                # tablename = slug + "_" + storename + "_" + fc.lower()
                # style_name = wrksp+":"+ slug + "_" + storename + "_" + fc.lower()
                msg += geostyler.dynamic_styler(opsld_filenames[fc], tablename, geom, anno, i)
                temp_op_decoration[tablename] = [geom, legend, dialog, anno]
                i += 1

            msg += "    Finished creating style files for operational layers\n"
            logger.info(msg)
            self._send(msg)
            # save in session cache
            self.scope["session"]["op_style"] = temp_op_decoration

            msg = "    Publishing feature store layers"
            logger.info(msg)
            self._send(msg)
            
            op_layers = {}    # collecting tablenames for the cache
            msg = ""
            for layer, bbox in slugobj.op_layers.items():  
                # this table name should be in sync with postgis table name
                tablename = slug+"_"+layer.lower()  
                op_layers[tablename] = bbox       
                msg += geo_rest.featurestore_layer_postgis(wrksp, storename, tablename) 
            
            msg += "    Finished publishing feature store layers\n"
            logger.info(msg)
            self._send(msg)

            # save into session
            self.scope["session"]["op_layers"] = op_layers
           
            # get sld_path
            msg = "    Publishing styles for operational layers"
            logger.info(msg)
            self._send(msg)

            msg = ""     
            for layer in opsld_filenames.keys(): 
                sldfile = opsld_filenames[layer]            
                if os.path.isfile(sldfile):
                    msg += f"          Publishing style for {layer}\n"
                    # construct the geoserver style and publish
                    
                    tablename = slug+"_"+layer.lower()
                    style_name = wrksp+":"+ slug + "_" + storename + "_" + layer.lower()
                    msg += geo_rest.layer_sld(sldfile, wrksp, tablename, style_name)
                
            msg += "    Finished publishing style for operational layers"
            logger.info(msg)
            self._send(msg) 

            # TODO
            capability_xml, stat = geo_rest.wms_getcapabilities(wrksp)
            layers_union_bbox =  sys_utils.parse_getcapability(capability_xml)
            
            # save to session
            self.scope["session"]["oplayers_bbox"] = layers_union_bbox

            msg = "Processing Operational layers completed ..........\n"
            logger.info(msg)
            self._send(msg)

            # save the session itself   
            self.scope["session"]["oplayers_status"] = 1         # need this for first time js not to give error 
            self.scope["session"].save()

        except Exception as e:            # TODO: not tested
            msg = f"Some exception happend! {str(e)}\nReversing operations!"
            djutils.reset_op_cache("op")
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
