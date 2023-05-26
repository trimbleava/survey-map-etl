# generate_model.py
from __future__ import print_function

# standard libs
import os, sys
import contextlib

# third party libs
from django.contrib.gis.utils import LayerMapping
from django.core.management.base import BaseCommand
from django.contrib.gis.utils import ogrinspect

# app modules


import logging
logger = logging.getLogger('lsa_jang')


if os.name == 'nt':
    VENV_BASE = os.environ['VIRTUAL_ENV']
    
    os.environ['PATH'] = os.path.join(VENV_BASE, 'Lib\\site-packages\\osgeo') + ';' + os.environ['PATH']
    os.environ['PROJ_LIB'] = os.path.join(VENV_BASE, 'Lib\\site-packages\\fiona\\proj_data')
    os.environ['GDAL_DATA'] = os.path.join(VENV_BASE, 'Lib\\site-packages\\fiona\\gdal_data')
    logger.info(f"Environ set: {os.getenv('GDAL_DATA')}")

#
# usage: manage.py ogrinspect [-h] [--blank BLANK] [--decimal DECIMAL] [--geom-name GEOM_NAME] [--layer LAYER_KEY] [--multi-geom]
#                             [--name-field NAME_FIELD] [--no-imports] [--null NULL] [--srid SRID] [--mapping] [--version] [-v {0,1,2,3}]
#                             [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color]
#                             data_source model_name
#                 
def generateModel(shpfile, path_to_models, modelname, geom_name, srid=4326, multi_geom=False):
   
    with open(path_to_models, 'a') as f:
        with contextlib.redirect_stdout(f):  
            # NOTE: do not put any print here, it writes to the models.py
            print("\n")
            print(ogrinspect(shpfile, modelname, geom_name=geom_name, srid=srid, multi_geom=multi_geom, 
                             imports=False, mapping=True))    # this version does not accept mapping!!
            
    """
        Given a data source (either a string or a DataSource object) and a string
        model name this function will generate a GeoDjango model.
        Usage:
        
        >>> from django.contrib.gis.utils import ogrinspect
        >>> ogrinspect('/path/to/shapefile.shp','NewModel')
        
        ...will print model definition to stout
        
        or put this in a python script and use to redirect the output to a new
        model like:
        
        $ python generate_model.py > myapp/models.py
        
        # generate_model.py 
        from django.contrib.gis.utils import ogrinspect
        shp_file = 'data/mapping_hacks/world_borders.shp'
        model_name = 'WorldBorders'
        print(ogrinspect(shp_file, model_name, multi_geom=True, srid=4326, geom_name='shapes', imports=False, blank=True)
                        
        Required Arguments
        `datasource` => string or DataSource object to file pointer
        
        `model name` => string of name of new model class to create
        
        Optional Keyword Arguments
        `geom_name` => For specifying the model name for the Geometry Field. 
        Otherwise will default to `geom`
        `layer_key` => The key for specifying which layer in the DataSource to use;
        defaults to 0 (the first layer).  May be an integer index or a string
        identifier for the layer.
        `srid` => The SRID to use for the Geometry Field.  If it can be determined,
        the SRID of the datasource is used.
        
        `multi_geom` => Boolean (default: False) - specify as multigeometry.
        
        `name_field` => String - specifies a field name to return for the
        `__unicode__` function (which will be generated if specified).
        
        `imports` => Boolean (default: True) - set to False to omit the 
        `from django.contrib.gis.db import models` code from the 
        autogenerated models thus avoiding duplicated imports when building
        more than one model by batching ogrinspect()
        
        `decimal` => Boolean or sequence (default: False).  When set to True
        all generated model fields corresponding to the `OFTReal` type will
        be `DecimalField` instead of `FloatField`.  A sequence of specific
        field names to generate as `DecimalField` may also be used.
        `blank` => Boolean or sequence (default: False).  When set to True all
        generated model fields will have `blank=True`.  If the user wants to 
        give specific fields to have blank, then a list/tuple of OGR field
        names may be used.
        `null` => Boolean (default: False) - When set to True all generated
        model fields will have `null=True`.  If the user wants to specify
        give specific fields to have null, then a list/tuple of OGR field
        names may be used.
        
        Note: This routine calls the _ogrinspect() helper to do the heavy lifting.
        """

#   
# python manage.py tenant_command load_gisdata --schema=public or tenant
# python manage.py ogrinspect D:/PROJECTS/survey-map-etl/INPUT/GridZones.shp GridZones --geom-name=geom --srid=4326  --mapping --multi-geom --no-imports
# python manage.py generate_model D:/PROJECTS/survey-map-etl/INPUT/GridZones.shp D:/PROJECTS/survey-map-etl/tenants/southwestgaslv/models.py GridZones geom 4326 False True
#                                 D:/PROJECTS/survey-map-etl/tenants/southwestgaslv/models.py 
#                                 GridZones geom 4326 False True
#
class Command(BaseCommand):
    
    def add_arguments(self, parser):
        # multi_geom=True, srid=4326, geom_name='shapes', imports=False, blank=True
        parser.add_argument('shapefile', type=str, help='help for shapefile')
        parser.add_argument('path_to_model', type=str)
        parser.add_argument('modelname', type=str)
        parser.add_argument('--geom_name', type=str, required=False, default='geom')
        parser.add_argument('--srid', type=int, required=False, default=4326)
        parser.add_argument('--multi_geom', type=bool, required=False, default=False)
        parser.add_argument('--imports', type=bool, required=False, default=True)
 
    def handle(self, *args, **options):
        # logger.info("Usage: <shapefile|datasource> <path_to_models> <modelname> <--geom_name> <--srid> <--multi_geom> <--imports>")
        # logger.info(options)
        shapefile = options['shapefile']
        path_to_model = options['path_to_model']
        modelname = options['modelname']
        geom_name = options['geom_name']
        srid = options['srid']
        multi_geom = options['multi_geom']
        imports = options['imports']
       
        generateModel(shapefile, path_to_model, modelname, geom_name=geom_name, 
                      srid=srid, multi_geom=multi_geom, imports=imports)