# standard libs
import os, sys
import json
import time
from io import StringIO, BytesIO
import re
import fileinput
import unicodedata

# third party libs
from django.contrib import messages
from channels.generic.websocket import WebsocketConsumer
from django.core.management import call_command
from django.contrib.gis.utils import LayerMapping
# from django.core.management.base import BaseCommand
from django.contrib.gis.utils import ogrinspect
# from django.core.management.commands import loaddata


import logging
logger = logging.getLogger("lsajang")

# app modules
from heath_lsa.django_utils import print_pymemcache
#
from system_modules.messenger_engine import msgr
from system_modules.etl_engine import etle
from system_modules.activate_customer import activate
from system_modules.geoserver_engine import geoe
from system_modules.gis_engine import gise
from system_modules import sys_utils

#
# To make this consumer easier to read, we define few functions here to call
#
def start_engines():
    msg = f"Starting system engines: \n"
    msg += "    LSA ETLEngine\n"
    etl = etle
    msg += "    LSA GeoserverEngine\n"
    geo_rest = geoe
    msg += "    LSA GISEngine\n"
    giseng = gise
    
    return etl, geo_rest, giseng, msg 


def activate_processor(slug):
    """Calling the customer generic class where this customer's configuration
    information, as deterined by slug, is parsed and saved into this customer's object.

    Args:
        slug (string): the unique identifier for this client

    Returns:
        slugobj: the reference to the object
        operations: the dictionary of operational layer names as key and attributes, etc as values
        legends: the dictionary of the legends with layer name and geometry type as keys and
        other information as values, per layer
        msg: string of messages
    """
    msgs = f"Activating {slug} processor\n"

    slugobj = activate(slug)
    
    operational_list = slugobj.operations      # includes geometry type
    
    # local variable
    operationals = {}
    legends = {}

    #
    # we need to get the operational information to process the
    # data for this customer.
    #
    for fc, geom, include, filter,legend in operational_list:
        f = fc +".shp"
        legends[(fc, geom)] = legend.split(",")             # list
        operationals[f] = (include.split(","), filter)      # tuple
       
    msg = operationals.keys()
    msg_str = ', '.join(msg)
    msg = "    Extracting data for " + msg_str
    legend_str = "["
    for key, val in legends.items():
        legend_str += " ".join(val)
        legend_str += "], ["
    msg += "\n    With legend for fields " + legend_str[:-2] + "\n"
    msgs += msg    
   
    return slugobj, operationals, legends, msgs


def process_layers(slugobj, operationals, giseng):
    """Extra data attributes are removed from the shapefiles and 
    reprojected to the 4326 geographic coordinate system and 
    the bounding box of each layer is saved in the slugobj for
    later on display of the data. The new data sets are transfered
    back from geopandas format to shapefile in output directory.
    Args:
        slugobj (object): an instance of the customer object
        operationals (dictionary): operational layer names as key with etc.. as value
        giseng (gis engine object): an instance of gis engine
    Returns:
        string: messages 
    """
    input_path = slugobj.input_path
    
    operationals_with_path = {}
    for path, subdirs, files in os.walk(input_path):
        for file in files:
            for key, value in operationals.items():
                if file.endswith(key) : 
                    shp = os.path.join(path,file)
                    operationals_with_path[shp] = value
                    continue

    input_types = slugobj.input_types
    output_path = slugobj.output_path

    layer_dict = operationals_with_path

    for f, values in layer_dict.items():
        msg = f"Transform in place for {f}:\n"

        # read shapefile into gpd and remove extra columns
        msg += f"      Reading shapefiles into geopandas and removing extra columns\n"
        include_fields, filter = values
        gdf = giseng.gdf_read_shp(f, include_fields, filter)
       
        # reproject 
        msg += f"      Re-projecting to 4326\n"
        gdf = giseng.reproject_to_4326(gdf)
               
        # print few lines of the new data
        msg += "      Displaying geopandas cleaned up data:\n"        
        msg += ",".join(str(s) for s in gdf.columns.tolist())         # gdf.iloc[:5,:-1].to_string()
        msg += "\n"

        # remove the path and extension, just the shape file name
        fcname = sys_utils.filename(f)
 
        # get bounding box for use in map
        msg += "      Finding closest bounding box for fast display\n"
        xmin, ymin, xmax, ymax = giseng.bounds_simple(gdf)
        slugobj.layers[fcname] = (xmin, ymin, xmax, ymax)
        
        # re-shape the new layers and save in output dir
        shapefile = os.path.join(output_path, fcname+".shp")
        gdf.to_file(shapefile)
        msg+= f"      Cleaned up shape file is created: {shapefile}\n"

        yield msg 
    

def create_legends(legends):
    for key in legends.keys():
        pass


def generate_model(fcname, geom, slug):
    """ creates a models.py file with table schemas per layer

    Args:
        fcname (string): feature layer or model name or table name
        geom (string): geometry type of this layer such as Poly, point, ...
        all of which are represented by the column "geometry".
        slug (string): unique identifier of the customer
    """
    #
    # To run from command line for testing:
    # generate_model D:/PROJECTS/survey-map-etl/INPUT/GridZones.shp D:/PROJECTS/survey-map-etl/tenants/southwestgaslv/models.py GridZones geom 4326 False True
    #                D:/PROJECTS/survey-map-etl/tenants/southwestgaslv/models.py 
    #                GridZones geom 4326 False True

    # the location of the models.py within each customer's django app
    path_to_models = os.path.join(os.getenv('TENANT_DIR'), slug, "models.py")
   
    srid = 4326 

    multi_geom = False
    if geom.lower().startswith("multi"):
        multi_geom = True
           
    geom_name = "geometry"
    imports = False

    modelname = fcname
    shapefile = os.path.join(os.getenv("OUTPUT_PATH"), fcname+".shp")

    err = StringIO()
   
    msg = f"      Model generated for {modelname}"
    errs = ""
    
    # ogrinfo -so OUTPUT\SWG\RegulatorStation.shp RegulatorStation
    with open(path_to_models, 'a') as f:
        # Valid options are: blank, data_source, decimal, force_color, geom_name, help, 
        # layer, layer_key, mapping, model_name, multi_geom, name_field, no_color, 
        # no_imports, null, pythonpath, settings, srid, stderr, stdout, traceback, verbosity, version.
        call_command('ogrinspect', shapefile, modelname, imports=False, mapping=True, 
                      srid=srid, stdout=f, stderr=err, verbosity=False, no_color=True,
                      multi_geom=multi_geom, geom_name=geom_name)

    # this management command does not accepts mapping option -- kept for example
    # call_command('generate_model', shapefile, path_to_models, modelname, geom_name=geom_name, 
    #               srid=srid, multi_geom=multi_geom, stdout=out, stderr=err, no_color=True)

    e = err.getvalue()
    err.close()

    if e:
        errs = f"      Model failed to generate for {modelname}\n"
        errs += e
 
    return msg, errs



def make_migrations(slugobj, schema):
    """ Invokes django's makemigration on the models.py file and creates migration file
    to be loaded into database as the schema of the table.

    Args:
        slugobj (customer object): an instance of a customer
        schema (string): unique customer schema name in database 

    """
    out = StringIO()
    err = StringIO()

    python_path = os.getenv("VIRTUAL_ENV")
    settings = os.getenv("DJANGO_SETTINGS_MODULE")
    surveyname = slugobj.survey_name.lower()
    app_label = slug = slugobj.slug
    
    msg = ""
    errs = ""

    # this is a django provided management command running from here instead of command line.
    # upon running, a migration file is created with information captured in stdout in order
    # to capture the "entire name" of the migration file.
    #
    # Named argument similar to the command line minus the initial dashes and
    # with internal dashes replaced by underscores (--natural-foreign)
    # management.call_command("dumpdata", natural_foreign=True)
    # TODO: migrate books zero
    call_command('makemigrations', app_label, name=surveyname,  pythonpath=python_path, 
                  settings=settings, stdout=out, stderr=err, no_color=True)
    
    e = err.getvalue()
    s = out.getvalue()

    if e:
        errs = f"Make migration failed for {surveyname}\n"
        errs += e
        return msg, errs

    msg = f"Make migration succeeded for {surveyname}\n" 
        
    # 
    # Migration file name format:
    # p = re.compile(r'\w+.py')
    # find string that starts with 2 zeros (00) followed by zero or more zeros ([0]*)
    # followed by one or more digits in the range of 1 through 9 ([1-9]+)
    # followed by one under score (_)
    # followed by any alphanumeric charachters [\w]+
    # followed by extension (.py)
    #
    p = re.compile(r'00[0]*[1-9]+_[\w]+.py', re.MULTILINE)
    m = p.search(s)
    if m is None:
        errs = f"Searching for migration name failed\n"
        if s:
            msg += s
        return msg, errs  

    #
    migration_name = m.group()
    msg += f"Search for migration name {migration_name} succeeded\n"

    file = os.path.join(os.getenv("TENANT_DIR"), app_label, 'migrations', migration_name)
    found = os.path.isfile(file)
    if not found:
        errs = f"Migration file, {file}, does not exist on the disk.\n"
        return msg, errs
         
    call_command('migrate_schemas', app_label, migration_name[:-4], schema=schema, pythonpath=python_path, 
                  settings=settings, stdout=out, stderr=err, no_color=True)
    e = err.getvalue()
    o = out.getvalue()

    err.close()
    out.close()

    if e:
        errs = f"Migrate schemas failed for {schema}\n"
        errs += e
        if o:
            msg += o
        return msg, errs    
    
    msg += f"Migrate schemas succeeded for {schema}\n"
    if o:
        msg += o
    
    return msg, errs


def publish(geo_rest, legends, schema, wrksp):
    #
    # watch for the case when legends and shapes are not one-to-one in config file
    for key in legends.keys():
        fcname, geom = key
        storename = fcname.lower()
        tablename = fcname
        msg += f"Loading layer {tablename} into geodatabase\n"
        msg += geo_rest.featurestore_layer_postgis(storename, wrksp, tablename, schema=schema)
        msg += "\n"    
        yield msg



class SurveyMapModelsConsumer(WebsocketConsumer):
    # A channels application is the equivalent of Django views
    # An entirely valid ASGI application you can run by themselves.
    # Channels and ASGI split up incoming connections into two components: a scope, and a series of events.
    # A consumer is the basic unit of Channels code.
    # scope["path"], the path on the request. (HTTP and WebSocket)
    # scope["headers"], raw name/value header pairs from the request (HTTP and WebSocket)
    # scope["method"], the method name used for the request. (HTTP)
    # https://github.com/django/asgiref/blob/main/specs/www.rst
    #
    msg = "Entered SurveyMapConsumer\n"
    logger.info(msg)
   

    def connect(self):

        self.accept()

        # starts the system engines required by this consumer
        etl, geo_rest, giseng, msg = start_engines()
        logger.info(msg)
        self._send(msg)
     
        slug = self.scope['session']['slug']    # "southwestgaslv"
        slugobj, operationals, legends, msg = activate_processor(slug)  # can not pickle local connection

        #
        msg = "Processing layers ..........\n"
        self._send(msg)
        msg_gen = process_layers(slugobj, operationals, giseng)
        for msg in msg_gen:
            logger.info(msg)
            self._send(msg)
        msg = "Finished processing layers ..........\n"
        self._send(msg)

        #
        # create_legends(legends)
        #
        msg = "Creating legends TODO ..........\n"
        logger.info(msg)
        self._send(msg)
        msg = "Finished creating legends TODO ..........\n"
        logger.info(msg)
        self._send(msg)

        # watch for the case when legends and shapes are not one-to-one in config file
        msg = "Generating models .........."
        self._send(msg)
        for key in legends.keys():
            fc, geom = key
            msg, msg_err = generate_model(fc, geom, slug)
            msg += msg_err
            logger.info(msg)
            self._send(msg)    
        msg = "Finished generating models ..........\n"
        self._send(msg)

        # do not put inside generate_model
        #
        # change the models.py file content
        #
        sub1 = "from django.contrib.gis.db import models"
        sub2 = "from django.contrib.gis.db import models as gismodels"
        sub3 = "geometry = models"
        sub4 = "geometry = gismodels"
       
        path_to_models = os.path.join(os.getenv('TENANT_DIR'), slug, "models.py")
        msg = "Modifying models.py ..........\n"
        msg += f"      Replacing '{sub1}' with '{sub2}'\n"
        msg += f"      Replacing '{sub3}' with '{sub4}'"
        logger.info(msg)
        self._send(msg)

        with fileinput.FileInput(path_to_models, inplace=True, backup='.bak') as file:
            # DO NOT ADD ANY PRINT IN FOR LOOP!!
            for line in file:
                # print(line.replace(text_to_search, replacement_text), end='')
                if sub1 in line and sub2 not in line: 
                    print(line.replace(sub1, sub2), end='\nfrom django.db import models\n\n')
                    continue
                print(line.replace(sub3, sub4), end='')
                
        msg = "Finished modifying models.py ..........\n"
        logger.info(msg)
        self._send(msg)

        #
        # register_with_admin
        #
        msg = "Registering models with admin TODO ..........\n"
        logger.info(msg)
        self._send(msg)
        msg = "Finished registering models with admin TODO ..........\n"
        logger.info(msg)
        self._send(msg)

    
    def disconnect(self, close_code):
        msg = "Entered disconnect\n"
        logger.info(msg)
        pass


    def receive(self, text_data):

        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
 
        self.send(text_data=json.dumps({"message": message}))

    def _send(self, text_data):
        msg = json.dumps({"message": text_data})
        self.send(msg)


class SurveyMapMigrationsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()  

        # starts the system engines required by this consumer
        etl, geo_rest, giseng, msg = start_engines()
        logger.info(msg)
        self._send(msg)
        
        slug = self.scope['session']['slug']    # "southwestgaslv"
        slugobj, operationals, legends, msg = activate_processor(slug)  # can not pickle local connection
        schema = self.scope["session"]["schema"]        # 'southwestgaslv_1676228649'
      
        msg = f"Create DB tables for {slug} .........."
        logger.info(msg)
        self._send(msg)

        msg, errs = make_migrations(slugobj, schema)
    
        if errs:
            logger.error(errs)
            msg += errs            # regardless send both into consumer
            self._send(msg)

        msg += f"Finished create DB tables for {slug} ..........\n"
        logger.info(msg)
        self._send(msg)

    def _send(self, text_data):
        msg = json.dumps({"message": text_data})
        self.send(msg)


