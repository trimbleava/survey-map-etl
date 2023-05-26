
# standard libs
import os

# app modules
from system_modules.message_logger import logger
from system_modules import generic_customer as gc


class SouthwestGasLasVegas(gc.Utility):
    # json_config file contains query statemants as well
    pass

#
# if we do not start the application from "start.py",
# we must call this def main(conf) 
#
def main(customer_json_cfg, slug):
    slugobj =  SouthwestGasLasVegas(customer_json_cfg, slug)
    msg = f"Customer {slugobj} started from stdmain\n"
    logger.info(msg)

    return slugobj

    # call the etl engine  -- TODO 
    # etl_engine.main(obj)

#
# for use by django web - must add one main per new customer
# also must add to start.py
#
def webmain(customer_json_cfg, slug):
    slugobj =  SouthwestGasLasVegas(customer_json_cfg, slug)
    msg = f"Customer {slugobj} started from webmain\n"
    logger.info(msg)

    return slugobj

 
if __name__ =='__main__':

    tenant_dir = os.path.dirname(__file__)
    cfg = os.path.join("config", tenant_dir + ".cfg")
    
    # mxd_file = os.path.join("output", "default.mxd")     #sys.argv[1]
    # main(mxd_file)
    # import petl as etl
    # import cdata.msteams as mod    # MS teams connector
    # import fiona
    # fiona.listlayers('https://heathus.sharepoint.com/sites/GISServicesADMINONLY/Shared%20Documents/Forms/AllItems.aspx?FolderCTID=0x012000E47EAE68D6538A478AA16E77E63C95E9&id=%2Fsites%2FGISServicesADMINONLY%2FShared%20Documents%2FReceived%20From%20Customer%2F2023%2FVECT%20%2D%20Vectren%2FHeath%2Egdb%2FHeath%2Egdb&viewid=90af0514%2D3c2e%2D49f7%2Dadd8%2D8291c19abf15')
    # gpd.read_file(gdb, driver='FileGDB', layer=1)
    # createMXD(mxd_file)  