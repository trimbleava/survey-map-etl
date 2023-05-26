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


class OverlayLegendConsumer(WebsocketConsumer):
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
