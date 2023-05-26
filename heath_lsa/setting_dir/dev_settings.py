# standard libs
import os
import sys

# app modules
from .base_settings import *  # noqa

DEBUG = True

# The Debug Toolbar is shown only if your IP is listed in the INTERNAL_IPS setting.
# https://docs.djangoproject.com/en/2.0/ref/settings/#internal-ips
INTERNAL_IPS = ["127.0.0.1"]


# DATABASE SETTINGS
# https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
ALLOWED_HOSTS  = os.getenv("ALLOWED_HOSTS").split(" ") 
# ALLOWED_HOSTS = ['*']
          
# DEFAULT_TABLESPACE = '/home/administrator/DJANGO/dtablespace'   todo


# CACHES = {
#     'default': {
#         # pure-Python memcached client library
#         'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
#         'LOCATION': '127.0.0.1:11211',
#         #           '172.19.26.242:11211',
#         #'KEY_FUNCTION': 'django_tenants.cache.make_key',
#         # 'OPTIONS': {
#         #     # 'serializer': <your_serializer>,
#         #     #'deserializer': <your_deserializer>,
#         # }
#     }
# }

#
# On 4/19/23 installed ubuntu on windows WSL to use Redis server in development
# On 4/30/23 integrated into base settings
# 

# for gdal/ogr/gis
if os.name == 'nt':
    VENV_BASE = os.environ['VIRTUAL_ENV']
    os.environ['PATH'] = os.path.join(VENV_BASE, 'Lib\\site-packages\\osgeo') + ';' + os.environ['PATH']
    os.environ['PROJ_LIB'] = os.path.join(VENV_BASE, 'Lib\\site-packages\\osgeo\\data\\proj') + ';' + os.environ['PATH']


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# By default, if an uploaded file is smaller than 2.5 megabytes, saves in temp in disk
# Read about file upload handler for deployment
FILE_UPLOAD_HANDLERS = ["django.core.files.uploadhandler.MemoryFileUploadHandler",
                        "django.core.files.uploadhandler.TemporaryFileUploadHandler"]