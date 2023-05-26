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

logger = logging.getLogger('load_usa_bounds')


def run_usa_states(verbose=True):
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
python manage.py tenant_command load_usa_bounds --schema=public or tenant
"""
class Command(BaseCommand):

    def load_data(self):
        run_usa_states()
       
    def handle(self, *args, **options):
        self.load_data()

