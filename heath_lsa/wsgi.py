# Autogenerated WSGI config for southwestgaslv project.
 
 
import os,sys
import logging
from django.core.wsgi import get_wsgi_application

 
logging.basicConfig(stream=sys.stderr)
 
sys.path.insert(0, '/var/www/survey-map-etl')
 
sys.path.append('/var/www/PY_ENV/bin')
 
sys.path.append('/var/www/PY_ENV/lib/python3.10/site-packages')
 
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'
os.environ['DJANGO_SETTINGS_MODULE'] = 'heath_lsa.setting_dir.prod_settings'
 
application = get_wsgi_application()
