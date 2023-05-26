from __future__ import print_function
# standard libs
import logging
import os

# third party libs
from django.contrib.gis.utils import LayerMapping
from django.core.management.base import BaseCommand
from django_tenants.management.commands import tenant_command


# app modules
from customers.models import USAStates

logger = logging.getLogger('lsajang')

def loaddata(verbose=True):
    # should not need to check on env required for this 
    # update since all is setup and menu is active
    print(os.getenv('INPUT_DIR'))
    print(os.getenv('PROJECT_DIR'))
    # os.environ['PROJECT_DIR'] = "/var/www/html/survey-map-etl"
    # os.environ['INPUT_DIR'] = "INPUT"

    usa_shp = os.path.join(os.getenv('PROJECT_DIR'), os.getenv('INPUT_DIR'),'cb_2018_us_state_20m.shp')
    usaobj = USAStates()
    usa_mapping = usaobj.get_mapping()
    lm = LayerMapping(USAStates, usa_shp, usa_mapping, transform=False, encoding='utf8')
    lm.save(strict=True, verbose=verbose)
    print(lm)
    # usa_shp = os.path.join(os.environ['PROJECT_DIR'], os.environ['INPUT_DIR'],'cb_2018_us_state_20m.shp')  
    # states = gdf_read_shp(usa_shp)
    # conn_str = "postgresql://heath_lsa_admin:heath_lsa_pass@localhost:5432/heath_lsa"
    # table = "usa_states"
    # gdf_to_postgis(states, conn_str, table)
  
"""
Used this: python manage.py ogrinspect INPUT/TM_WORLD_BORDERS-0.3.shp WorldBorders  --srid=4326  --mapping --multi 
to get the mapping. Added model to the customers models, used this management command to upload into database:
python manage.py tenant_command load_data --schema=public or tenant
"""
class Command(BaseCommand):

    def add_arguments(self, parser):
        # multi_geom=True, srid=4326, geom_name='shapes', imports=False, blank=True
        parser.add_argument('shapefile', type=str, help='path to shapefile data to load')
        parser.add_argument('path_to_model', type=str)
        parser.add_argument('modelname', type=str)
        parser.add_argument('mapping', type=str)
  
    def handle(self, *args, **options):
      
        # logger.info("Usage: <shapefile|datasource> <path_to_models> <modelname> <--geom_name> <--srid> <--multi_geom> <--imports>")
        # logger.info(options)

        shapefile = options['shapefile']
        path_to_model = options['path_to_model']
        modelname = options['modelname']
        mapping = options['mapping']

        lm = LayerMapping(modelname, shapefile, mapping, transform=True, encoding='utf8')
        lm.save(strict=True, verbose=True)
        print(lm)

