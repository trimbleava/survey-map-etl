# standard libs
import os
import json
import time

# third party libs
from channels.generic.websocket import WebsocketConsumer

# app modules
#
from system_modules.message_logger import logger
from system_modules.messenger_engine import msgr
from system_modules.etl_engine import etle
from system_modules.activate_customer import activate
from system_modules.geoserver_engine import geoe
from system_modules.gis_engine import gise
from system_modules import sys_utils

#for key, value in self.scope["session"].items():
#  print(key, value)


class OverlayConsumer(WebsocketConsumer):
    msg = f"Entered {__name__}\n"
    logger.info(msg)

    def connect(self):
        self.accept()

        slug = self.scope["session"]["slug"]
        logger.info(slug)
        
        msg = f"Started LSA ETLEngine ..........\n"
        etl = etle
        slugobj = activate(slug)
        msg += f"Activating {slug} processor"
        logger.info(msg)
        time.sleep(2)
        self._send(msg)
        
        input_path = slugobj.input_path
        input_types = slugobj.input_types
        overlay_list = slugobj.overlays      # includes geometry type
        # local variable
        overlays = {}
        legends = {}
        #
        msg = f"1) Extracting overlay geospatial files:"
        logger.info(msg)
        self._send(msg)
        for fc, geom,include,filter,legend in overlay_list:
            f = fc +".shp"
            legends[(fc, geom)] = legend.split(",")         # list
            overlays[f] = (include.split(","), filter)      # tuple
        msg = overlays.keys()
        msg_str = ', '.join(msg)
        msg = "    Extracting data for " + msg_str
        legend_str = "["
        for key, val in legends.items():
            legend_str += " ".join(val)
            legend_str += "], ["
        msg += "\n    With legend for fields " + legend_str[:-2]
        logger.info(msg)
        time.sleep(2)
        self._send(msg)
        #
        # get the shapefiles data
        overlays_with_path = {}
        for path, subdirs, files in os.walk(input_path):
            for file in files:
                for key, values in overlays.items():
                    if file.endswith(key) : 
                        shp = os.path.join(path,file)
                        overlays_with_path[shp] = values
                        continue
        overlays.clear()    # delete the old dict 
        #
        msg = f"2) Transforming overlays to web map services using geopackage:"
        logger.info(msg)
        time.sleep(2)
        self._send(msg)
        #
        gpkg = os.path.join(slugobj.output_path, "Overlay.gpkg")
        giseng = gise
        msg = f"    Started LSA GISEngine"
        logger.info(msg)
        time.sleep(2)
        self._send(msg)
        #
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
            #
            # print few lines of the new data
            msg = gdf.iloc[:5,:-1].to_string()
            logger.info(msg)
            self._send(msg)
            #
            fcname = sys_utils.filename(fc)
            msg = f"          Saving overlay {fcname} into geopackage {gpkg}\n"
            giseng.save_geopkg(gpkg, fcname, gdf)
            msg += f"          Finding closest bounding box for fast display\n" 
            # get bounding box for use in map
            xmin, ymin, xmax, ymax = giseng.bounds_simple(gdf)
            slugobj.layers[fcname] = (xmin, ymin, xmax, ymax)
            logger.info(msg)
            self._send(msg)
            #
            # plot the layer
            # gisengine.gdf_plot(gdf, fcname)

        msg = f"3) Loading geopackages and publishing overlay layers into geoserver:"
        pkgdir, pkgfile, storename = sys_utils.disect_path(gpkg)
        store = storename

        # TODO - see if can be changed to session vars for consistency
        schema = self.scope["session"]["schema"]        # 'southwestgaslv_1676228649'
        slug = self.scope["session"]["slug"]            # "southwestgaslv"
        tenant = self.scope["session"]["tenant"]        # South West Gas - LA"

        wrksp = slug
        logger.info(msg)
        time.sleep(2)
        self._send(msg) 
        #
        msg = "    Started LSA GeoserverEngine\n"
        geo_rest = geoe
        msg += f"    Creating workspace {wrksp}\n"
        msg += geo_rest.create_workspace(wrksp)
        logger.info(msg)
        time.sleep(2)
        self._send(msg) 
        #
        msg = f"    Creating datastore {store}\n"
        msg += geo_rest.create_geopkg_datastore(store, pkgfile, wrksp, overwrite=False)
        logger.info(msg)
        time.sleep(2)
        self._send(msg) 
        #
        # publish data
        for layer_str in slugobj.layers:
            msg = ""
            try:
                # store_name, layer, workspace, title, srid
                title = layer_str
                xyXY= slugobj.layers[layer_str]
                geo_rest.publish_geopkg_layer(store, layer_str, wrksp, title, xyXY)
                msg = f"    Published {layer_str}"
                logger.info(msg)
                msgr[slug] = msg
            except Exception as e:
                if "already exists" in str(e):
                    msg = f"    Layer {layer_str} already exists in store {store}, workspace {wrksp}"
                    msgr[slug] = msg
                else:
                    logger.info(str(e))
                    msg = "    " + str(e)
                    msgr[slug] = msg
            
            logger.info(msg)
            time.sleep(2)
            self._send(msg) 
        #
        # get sld_path
        tenant_dir = self.scope["session"]["tenant_dir"] 
        sld_path = os.path.join(tenant_dir, wrksp, "sld") 
        msg = ""     
        for layer in slugobj.layers: 
            sldfile = os.path.join(sld_path,layer+".sld")               
            if os.path.isfile(sldfile):
                msg += f"    Publishing legend for {layer}\n"
                # construct the geoserver style and publish
                style_name = wrksp+":"+layer 
                msg += geo_rest.layer_sld(sldfile, wrksp, layer, style_name)

        #
        # at this time layers are in geoserver and we can extract their bbox
        # this is needed in map display to fitbounds into the active layers
        # so for now we save them in session to be passed into js
        # 
        capability_xml, stat = geo_rest.wms_getcapabilities(wrksp)
        layers_union_bbox =  sys_utils.parse_getcapability(capability_xml)
        # self.scope["session"]["modified"] = True  not sure if needed - watch the space
        self.scope["session"]["ovlayers_bbox"] = layers_union_bbox
        
        #
        # set the overlay status to READY and save the session
        #
        self.scope["session"]["ovlayers_status"] = "READY"
        self.scope["session"].save()
        
        msg += "Finished processing Overlay layers\n"
        logger.info(msg)
        time.sleep(2)
        self._send(msg)
        
    def disconnect(self, close_code):
        msg = f"Entered {__name__}\n"
        logger.info(msg)
        pass

    def receive(self, text_data):
        print("Receiving: ", message)
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(text_data)
        self.send(text_data=json.dumps({"message": message}))

    def _send(self, text_data):
        msg = json.dumps({"message": text_data})
        self.send(msg)


class OverlayLegend(WebsocketConsumer):
    # sldfile = "D:\\PROJECTS\\heath_lsa\\customers\\southwest_gas\\tenant_modules\\main_lines.sld" 
    # style_name = wrksp+":main_lines"
    # geo_rest.layer_sld(sldfile, wrksp, geoserver_lyrname, style_name)
    def connect(self):
        self.accept()
        sld_path = os.path.join(os.getenv("TENANT_DIR"), self.scope["session"]["slug"], "sld")
        msg = sld_path
        self._send(msg)

    def _send(self, text_data):
        msg = json.dumps({"message": text_data})
        self.send(msg)



class SurveyMapConsumer(WebsocketConsumer):
    # A channels application is the equivalent of Django views
    # An entirely valid ASGI application you can run by themselves.
    # Channels and ASGI split up incoming connections into two components: a scope, and a series of events.
    # A consumer is the basic unit of Channels code.
    # scope["path"], the path on the request. (HTTP and WebSocket)
    # scope["headers"], raw name/value header pairs from the request (HTTP and WebSocket)
    # scope["method"], the method name used for the request. (HTTP)
    # https://github.com/django/asgiref/blob/main/specs/www.rst
    #
    msg = f"Entered {__name__}\n"
    logger.info(msg)

    def connect(self):
        self.accept()

        try:
            msg = "Under Construction"
            self._send(msg)
        except Exception as e:
            msg = str(e)
            logger.info(msg)
            

    def disconnect(self, close_code):
        pass


    def receive(self, text_data):
        print("Receiving: ", message)
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(text_data)
        self.send(text_data=json.dumps({"message": message}))


    def _send(self, text_data):
        msg = json.dumps({"message": text_data})
        self.send(msg)
