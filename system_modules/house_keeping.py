# NOTE: This file doesn't work if you put try/except anywhere

# standard libs
import os, sys, logging
from os.path import dirname, abspath

# third party libs
from dotenv import load_dotenv

logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(message)s', level="INFO")
logger = logging.getLogger(__name__)

# set projdir environment variable
prj_dir = os.environ["PROJECT_DIR"] = dirname(dirname(abspath(__file__)))
if prj_dir not in sys.path:
     sys.path.append(prj_dir)

# app modules

from system_modules.scripts import secret
from system_modules import message_logger


# os.environ["SECRET_KEY"] = secret.do_secret()

# set tenantdir environment variable
tenant_dir = os.environ["TENANT_DIR"] = os.path.join(prj_dir, "tenants")
if tenant_dir not in sys.path:
     sys.path.append(tenant_dir)

module_dir = os.environ["MODULE_DIR"] = dirname(abspath(__file__))
if module_dir not in sys.path:
     sys.path.append(module_dir)

# load the environment variables# local variables
output_dir = config_file = log_dir = None

env_file = os.path.join(module_dir, "system_environ", "system.env")
if not os.path.exists(env_file):
    msg = f"Env file {env_file} expected\n"
    logger.error(msg)     
    sys.exit(0)
else:    
    # read the environment here, ready for use now
    stat = load_dotenv(env_file)  # returns True/False

# logger  -- overriding all the envs with path
log_dir = os.environ["LOG_DIR"] = os.path.join(prj_dir, os.getenv("LOG_DIR"))

# instantiate logger singleton here
logger = message_logger.start()

if not os.path.isdir(log_dir):
    os.makedirs(log_dir)      # has order
    msg = f"Creating log directory {log_dir}\n"
    logger.info(msg)


# config - not needed anymore after turning into web app
# config_file = os.environ["CONFIG_FILE"] = os.path.join(module_dir, os.getenv("CONFIG_FILE"))
# if not os.path.exists(config_file):
#     msg = f"Config file {config_file} expected\n"
#     logger.info(msg)      
#     sys.exit(0)

# template web dir used in copying user template to this location

# output
output_dir = os.environ["OUTPUT_DIR"] = os.path.join(prj_dir, os.getenv("OUTPUT_DIR"))
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)
    msg = f"Creating output directory {output_dir}\n"
    logger.info(msg)

# reading from secret file populated by deployment script
# put all the secrets into env for consistency
dir_path = os.path.join(module_dir,"secrets")
with open(os.path.join(dir_path, "secret_key.txt")) as f:
    lines = f.readlines()
    SECRET_KEY = lines[0].strip()
    os.environ["SECRET_KEY"] = SECRET_KEY
    DB_NAME = lines[1].strip()
    os.environ["DB_NAME"] = DB_NAME
    DB_USER = lines[2].strip()
    os.environ["DB_USER"] = DB_USER
    DB_PASSWORD = lines[3].strip()
    os.environ["DB_PASSWORD"] = DB_PASSWORD
    DB_HOST = lines[4].strip()
    os.environ["DB_HOST"] = DB_HOST
    HOST_NAME = lines[5].strip() 
    os.environ["HOST_NAME"] = HOST_NAME

os.environ["HOUSE_IS_CLEANED"] = 'True'

logger.info(os.getenv("GEOSERVER_DATA_DIR", "NO_PATH_SET"))

