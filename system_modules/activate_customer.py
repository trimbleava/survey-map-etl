# standard libs
import os, sys
import importlib

# app modules
from system_modules.message_logger import logger
from system_modules import start

slugobj = None

def activate(slug):
    msg = "Entered activate\n" 
    logger.info(msg)

    # slug get set in env first time here
    customer_module_name, customer_conf = start.parse_this_customer_info(None, slug=slug)
    msg = f"Parsing {slug}'s config file {customer_conf}\n"
    logger.info(msg)

    # import module
    msg = "Starting process ........."
    logger.info(msg)
    
    # The file gets executed upon import, as expected.
    cust_module = importlib.import_module(customer_module_name)
    
    # Customer configuration file is relative to system 
    # directory structure and name dependent. Watch for it.
    slugobj = cust_module.webmain(customer_conf, slug)
    return slugobj
