#
# This file injects all needed system wide objects at the django
# settings startup. Nothing of django application itself is called 
# here. This file also, starts all the singleton objects.
#
import os, sys
import importlib
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(message)s', level="INFO")
logger = logging.getLogger(__name__)
logger.info(f"Entered {__name__}\n")

# app modules
try:
    from system_modules import house_keeping
    logger.info("House keeper is called (1)\n")
except:
    from . import house_keeping
    logger.info("House keeper is called (2)\n")
#
# House keeping sets all the environment variables ready 
# for all other module to use and reads the system config
# file. The config file is in system_modules/system_configs
#  HAS ORDER .......
if 'message_logger' not in sys.modules:
    from system_modules import message_logger 
    logger = message_logger.start()
else:
    logger = house_keeping.logger 

if 'messenger_engine' not in sys.modules:
    from system_modules import messenger_engine
    msgr = messenger_engine.start()
else:
    msgr = messenger_engine.start()

if 'gis_engine' not in sys.modules:
    from system_modules import gis_engine  
    gise = gis_engine.start()
else:
    gise = gis_engine.start()

if 'geoserver_engine' not in sys.modules:
    from system_modules import geoserver_engine 
    geoe = geoserver_engine.start()
else:
    geoe = geoserver_engine.start()

# this must be at the end for the dependencies - HAS ORDER
if 'etl_engine' not in sys.modules:
    from system_modules import etl_engine
    etle = etl_engine.start()
else:
    etle = etl_engine.start()
