# standard libs
import sys, os

# third part libs
import arcpy

# app modules
from modules import house_keeping as setup
from modules.database_helper import DatabaseHelper
from modules.query_statements import QueryStatements as qstmt
from modules.utils import createMXD

def main(mxd_file):
    
    # instantiate db 
    db = DatabaseHelper(setup.config_file, setup.log_dir)
    conn = db.connectDB()

    msg = f"\nProcessing "
    print(msg)
    setup.logger.info(msg)

    createMXD(mxd_file)    


if __name__ =='__main__':
    mxd_file = os.path.join("output", "default.mxd")     #sys.argv[1]
    main(mxd_file)