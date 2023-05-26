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


class DeleteOverlayConsumer(WebsocketConsumer):
    msg = f"Entered {__name__}\n"
    logger.info(msg)

    def connect(self):
        self.accept()

        slug = self.scope["session"]["slug"]
        logger.info(slug)

        #
        # activating the customer means constructing the customer module
        # and reading its configuration file and returning this customer object
        #
        msg = f"Started LSA ETLEngine ..........\n"
        etl = etle
        slugobj = activate(slug)
        msg += f"1) Activating {slug} processor"
        logger.info(msg)
        self._send(msg)
        
        overlay_list = slugobj.overlays      # includes geometry type
        # local variable
        overlays = {}
        legends = {}        # for printing
        legend_del = []     # for deleting
        #
        for fc, geom,include,filter,legend in overlay_list:
            legends[(fc, geom)] = legend.split(",")         # list
            legend_del.append(fc)
            overlays[fc] = (include.split(","), filter)      # tuple
        keys = overlays.keys()
        msg_str = ', '.join(keys)
        msg = f"2) Following layers will be deleted permanently:\n"
        msg += "    " + msg_str
        
        legend_str = "["
        for key, val in legends.items():
            legend_str += " ".join(val)
            legend_str += "], ["
        msg += "\n    With legend for fields " + legend_str[:-2]
        logger.info(msg)
        self._send(msg)
        #
        storename = "Overlay.gpkg"
 
        # TODO - see if can be changed to session vars for consistency
        schema = self.scope["session"]["schema"]        # 'southwestgaslv_1676228649'
        slug = self.scope["session"]["slug"]            # "southwestgaslv"
        tenant = self.scope["session"]["tenant"]        # South West Gas - LA"
        #
        msg = "Started LSA GeoserverEngine\n"
        self._send(msg)
        geo_rest = geoe
        wrksp = slug
        #
        for key in overlays.keys():
             # msg = f"      Following style files will be deleted from wrokspace {wrksp}\n"
             # msg = f"      You are about to remove the following object(s): {style_name}"
             # msg += f"      Also, the following object(s) will be modified:\n"
             # msg += f"      Layer(s): {layer}"
            msg = geo_rest.delete_layer(key, wrksp)
            # self._send(msg)  use if needed, must be decoded
        msg = "3) Finished deleting layers\n"
        self._send(msg)
        #
        # get slds
        for style_name in legend_del:               
            logger.info(style_name)
            msg = geo_rest.delete_stylefile(style_name, wrksp)
            # self._send(msg)
        msg = "4) Finished deleting legends\n"
        self._send(msg)

        self.scope["session"]["modified"] = True    # not sure if needed - watch the space
        #
        # set the overlay status to READY and save the session
        #
        # self.scope["session"]["ovlayers_status"] = "READY"
        self.scope["session"].save()
    

    # TODO - see if makes adifference in login into geoserver issue  
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

