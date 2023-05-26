# standard libs
import sys
import os
import logging
import json

# third part libs
import arcpy
import geopandas as gpd

# app modules
from app import query_statements as qstmt
from app import message_logger

logger = message_logger.get_logger(__name__)


# class Vectran(Client, GMail, CRM):
#     def __init__(self, name, email, user, password, server, product, gateway):
#         Client.__init__(self, name, email)
#         GMail.__init__(self, user, password, server)
#         Granot.__init__(self, product, gateway)
#         logger.info('Init {} with arguments {}'.format(self.__class__.__name__,
#                                                        (name, email, user, password, server, product, gateway)))


def main(db, conn):
    # get name of registered GIS assets to process 
    sql = qstmt.getAssetsName()
    logger.info(sql)
    asset_df = db.executeQuery(conn, sql)
    print(asset_df[["Id", "AlternativeName", "GeometryType"]])
    
    return


if __name__ =='__main__':
    mxd_file = os.path.join("output", "default.mxd")     #sys.argv[1]
    main(mxd_file)