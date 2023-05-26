import os
from .base_settings import *  # noqa

DEBUG = False

# DATABASE SETTINGS
# https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
ALLOWED_HOSTS  = os.getenv("ALLOWED_HOSTS").split(" ")

#
# On 4/30/23 integrated into base settings 
# 
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         # "LOCATION": "redis://35.193.244.81:6379/0",          # 35.193.244.81:6379   
#         # "LOCATION": "unix:/var/run/redis/redis.sock",        # see /etc/redis.conf
#         "LOCATION": "redis://127.0.0.1:6379/0",
#         #
#         'KEY_FUNCTION': 'django_tenants.cache.make_key',
#         'REVERSE_KEY_FUNCTION': 'django_tenants.cache.reverse_key',
#         #
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             # "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
#             # "COMPRESSOR": "django_redis.compressors.lz4.Lz4Compressor",   import lz4
#             # "IGNORE_EXCEPTIONS": True,    # global version outside of this - DJANGO_REDIS_IGNORE_EXCEPTIONS = True
#             # "retry_on_timeout": True,
#             #"KEY_PREFIX": "lsa"
#         }
#     }
# }

