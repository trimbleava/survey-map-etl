# -*- coding:utf-8 -*-

"""Base settings shared by all environments"""
# if you need to override something do it in local.py

# standard libs
from sys import path, exit, modules
import os, re

# third party libs
# Import global settings to make it easier to extend settings. 
# Beheen 2/17/2021 - got error: PASSWORD_RESET_TIMEOUT_DAYS/PASSWORD_RESET_TIMEOUT are 
# mutually exclusive when importing by * from global_settings. I had to import vars I 
# needed instead of using * 
from django.conf.global_settings import STATICFILES_FINDERS, AUTHENTICATION_BACKENDS   # pylint: disable=W0614,W0401
from django.template.defaultfilters import slugify

# app modules
from system_modules import sys_engine

SECRET_KEY = os.getenv("SECRET_KEY")
BASE_DIR = os.getenv("PROJECT_DIR") 

# =============================================================================

# General App settings
# =============================================================================
# @login_required(redirect_field_name='next', login_url=None)
# If the user isn’t logged in, redirect to settings.LOGIN_URL,
# passing the current absolute path in the query string, next.
# Example: /accounts/login/?next=/polls/3/
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = ""

# SMTP or Web API, SMTP is the default, if not specified
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", 'django.core.mail.backends.console.EmailBackend')  
EMAIL_HOST = os.environ.get("EMAIL_HOST", '')
EMAIL_PORT = os.environ.get("EMAIL_PORT", 587)
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", False)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", '')
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", '')


# SITE SETTINGS
# https://docs.djangoproject.com/en/2.0/ref/settings/#site-id
SITE_ID = 1

# If you want to run PostGIS add the following to your Django settings file
ORIGINAL_BACKEND = "django.contrib.gis.db.backends.postgis"

# =============================================================================
# multi-tenancy settings
# 
# absolute/path/to/your_project_dir
# ...
# static              # System-wide static files
# templates           # System-wide templates
# # Tenant-specific files below will override pre-existing system-wide files with same name.
# tenants
#     tenant_1        # Static files / templates for tenant_1
#         templates
#         static
#     tenant_2        # Static files / templates for tenant_2
#         templates
#         static
# media               # Created automatically when users upload files
#     tenant_1
#     tenant_2
# staticfiles             # Created automatically when collectstatic_schemas is run
#     tenant_1
#     tenant_2
# ...
# 
# =============================================================================
DATABASE_ROUTERS = ('django_tenants.routers.TenantSyncRouter',)
TENANT_MIDDLEWARE = 'django_tenants.middleware.main.TenantMainMiddleware'
TENANT_CONTEXT = 'django.template.context_processors.request'  
TENANT_MODEL = "customers.Client"
TENANT_DOMAIN_MODEL = "customers.Domain" 
#
# URL SETTINGS
# https://docs.djangoproject.com/en/2.0/ref/settings/#root-urlconf.
ROOT_URLCONF = 'heath_lsa.urls_tenants'
PUBLIC_SCHEMA_NAME = 'public'       # default of postgres is called public, so this can be changed here!!
PUBLIC_SCHEMA_URLCONF = 'heath_lsa.urls_public'
#
# Session security¶
# Subdomains within a site are able to set cookies on the client for the whole domain. 
# This makes session fixation possible if cookies are permitted from subdomains not controlled by trusted users.
# For example, an attacker could log into good.example.com and get a valid session for their account. 
# If the attacker has control over bad.example.com, they can use it to send their session key to you since a 
# subdomain is permitted to set cookies on *.example.com. When you visit good.example.com, you’ll be logged in 
# as the attacker and might inadvertently enter your sensitive personal data (e.g. credit card info) into the 
# attacker’s account.
#
# Another possible attack would be if good.example.com sets its SESSION_COOKIE_DOMAIN to "example.com" which would 
# cause session cookies from that site to be sent to bad.example.com.
SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN")


# PG_EXTRA_SEARCH_PATHS should be a list of schemas you want to make visible globally.
# PG_EXTRA_SEARCH_PATHS = ['gisapp']   TODO - not working as a global schema

STATICFILES_FINDERS = [
    "django_tenants.staticfiles.finders.TenantFileSystemFinder",  # Must be first
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder"
]
# ./manage.py collectstatic_schemas --schema=your_tenant_schema_name
MULTITENANT_STATICFILES_DIRS = [os.path.join(BASE_DIR, "tenants/%s/static" ), ]                               
STATICFILES_STORAGE = "django_tenants.staticfiles.storage.TenantStaticFilesStorage"
DEFAULT_FILE_STORAGE = "django_tenants.files.storage.TenantFileSystemStorage"
MULTITENANT_RELATIVE_STATIC_ROOT = ""  # (default: create sub-directory for each tenant)
MULTITENANT_RELATIVE_MEDIA_ROOT = ""   # (default: create sub-directory for each tenant)

# STATICFILES_DIRS = ( os.path.join(BASE_DIR, 'static'),)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static') 
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# TEMPLATE SETTINGS
# https://docs.djangoproject.com/en/2.0/ref/settings/#templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],   # -> Dirs used by the standard template loader
        'APP_DIRS': False,                               # -> since loader is defined
        'OPTIONS': {
            'context_processors': [
                # 'rsmgui.context_processors.navaccount_processor',
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                TENANT_CONTEXT,
                'django.contrib.auth.context_processors.auth',             # using dfault admin
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages'      # messaging
            ],
            "loaders": [
                "django_tenants.template.loaders.filesystem.Loader",       # Must be first
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            'libraries': {
               'template_tags': 'customers.templatetags.tags_extra',             
            },
        },
    },
]
# absolute/path/to/your_project_dir/tenants/%s/templates
MULTITENANT_TEMPLATE_DIRS = [os.path.join(BASE_DIR, "tenants/%s/templates"), os.path.join(BASE_DIR, "tenants/templates")] 
                           
#
# MIDDLEWARE SETTINGS
# See: https://docs.djangoproject.com/en/2.0/ref/settings/#middleware
#
MIDDLEWARE = [
    TENANT_MIDDLEWARE,
    #'heath_lsa.middleware.TenantMiddleware',                # check on this if can be used
    'django.middleware.locale.LocaleMiddleware',             # for translation to LANGUAGE_CODE - todo
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # for using session
    'django.contrib.messages.middleware.MessageMiddleware',  # The default message storage backend relies on sessions
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',             # cross-site request forgery -
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SHOW_PUBLIC_IF_NO_TENANT_FOUND = True  
TENANT_USERS_DOMAIN = os.getenv("TENANT_USERS_DOMAIN")
AUTH_USER_MODEL = 'accounts.TenantUser'
AUTHENTICATION_BACKENDS = ('tenant_users.permissions.backend.UserBackend',)
PG_EXTRA_SEARCH_PATHS = ['extensions']    # should be a list of schemas you want to make visible globally.

TENANT_APPS = (
    # your tenant-specific apps
    # can use 'myapp.apps.MyAppConfig' in INSTALLED_APP but not in SHARED_APP
    # we need this here because all of our tenants need the structure minus data!
    # we install data per tenant at the time of licensing or something!! TODO
    'tenants',
    'tenants.southwestgaslv',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    # 'django.contrib.sessions',  # if you want to use a database-backed session
    'django.contrib.messages', 
    'tenant_users.permissions', # defined in both shared apps and tenant apps
)

SHARED_APPS = (
    'django_tenants',           # mandatory
    'tenant_users.tenants',     # defined only in shared apps
    'tenant_users.permissions', # defined in both shared apps and tenant apps
    'customers',
    'accounts',                 # contains the new User Model (see below). Must NOT exist in TENANT_APPS
    # model that extends TenantMixin should be at SHARED_APPS
    # can use 'myapp.apps.MyAppConfig' in INSTALLED_APP but not in SHARED_APP
    'daphne',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',      # login/logout
    # 'django.contrib.sessions',  # if you want to use a database-backed session
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'compressor',
    #
    'crispy_forms',
    'leaflet',
    'djgeojson',
    #
    'channels'
)

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

# End multi-tenancy ************************

ORIGINAL_BACKEND = "django.contrib.gis.db.backends.postgis"

# Database
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
HOST_NAME = os.getenv("HOST_NAME")   # defined in hostfile as well, same as localhost

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',      # Used by multi-tenant app
        'NAME': os.getenv("HEATH_LS_DB", default=''),
        'USER': os.getenv("HEATH_LS_ADMIN", default=''),
        'PASSWORD': os.getenv("HEATH_LS_ADMIN_PASS", default=''),
        'HOST': DB_HOST,
        'PORT': DB_PORT
    }
}

# Python dotted path to the WSGI application used by Django's runserver.
ASGI_APPLICATION = 'heath_lsa.asgi.application'
WSGI_APPLICATION = 'heath_lsa.wsgi.application'

#
# Cache 
#
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'  # default
SERIALIZATION_MODULES = {'geojson': 'djgeojson.serializers'}
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
#
# To enable tenant aware caching you can set the KEY_FUNCTION setting 
# to use the provided make_key helper function which adds the tenants 
# schema_name as the first key prefix.
# 'KEY_FUNCTION': 'django_tenants.cache.make_key',
# 'REVERSE_KEY_FUNCTION': 'django_tenants.cache.reverse_key',
# The REVERSE_KEY_FUNCTION setting is only required if you are using 
# the django-redis cache backend.
#
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # I think /0 or /1 is for using multiple db caches!!
        # "LOCATION": "redis://35.193.244.81:6379/0",          # 35.193.244.81:6379   
        # "LOCATION": "unix:/var/run/redis/redis.sock",        # see /etc/redis.conf

        "LOCATION": "redis://127.0.0.1:6379",   # see https://awstip.com/django-caching-with-redis-c66ab2126c8a NOT TO START MANUALLY
        #
        # multitenants
        #
        # "KEY_FUNCTION": "django_tenants.cache.make_key",
        # "REVERSE_KEY_FUNCTION": "django_tenants.cache.reverse_key",
        #
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            # "COMPRESSOR": "django_redis.compressors.lz4.Lz4Compressor",   import lz4
            # "IGNORE_EXCEPTIONS": True,    # global version outside of this - DJANGO_REDIS_IGNORE_EXCEPTIONS = True
            # "retry_on_timeout": True,
            #"KEY_PREFIX": "lsa"
        }
    }
}
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 1209600    # (2 weeks, in seconds)

# Beheen 3/18 added to see the differences
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         # multitenants
#         #
#         "KEY_FUNCTION": "django_tenants.cache.make_key",
#         "REVERSE_KEY_FUNCTION": "django_tenants.cache.reverse_key",
#         #
#         "CONFIG": {
#             "hosts": ["redis://127.0.0.1:6379"],
#              #
#             "channel_capacity": {
#                 "http.request": 200,
#                 "http.response!*": 10,
#                 re.compile(r"^websocket.send\!.+"): 20,
#             },
#         },
#     },
# }
#
# LOGGING for multi_tenancy
# https://docs.djangoproject.com/en/2.0/topics/logging/
# 
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'tenant_context': {
            '()': 'django_tenants.log.TenantContextFilter'
        },
    },
    'formatters': {
        'default': {
            'format': '[%(schema_name)s:%(domain_url)s] %(levelname)-7s %(asctime)s %(message)s',
        },
    },
    'handlers': {
        'file': {
            'filters': ['tenant_context'],
            'class': 'logging.FileHandler',
            # be sure to change the 'filename' path to a location that’s 
            # writable by the user that’s running the Django application.
            'filename': os.path.join(os.getenv('LOG_DIR'), 'lsa_django.log'),
            'formatter': 'default',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['tenant_context'],
            'formatter': 'default',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
        'filters': ['tenant_context'],
    },
    'loggers': {
        'lsajang': {
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,    # if true all other loggers access the logs
            'handlers': ['file', 'console'],
        },
    },
}

#
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# DEBUG SETTINGS
DEBUG = False

# LOCALE SETTINGS
# Local time zone for this installation.
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = False
USE_TZ = False

# =============================================================================
# Third party app settings
# =============================================================================
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

#
# leaflet stuff
#
LEAFLET_CONFIG = { 
    # 'SPATIAL_EXTENT': (49.382808,-66.945392,24.521208,-124.736342),   # global map
    'DEFAULT_CENTER': (37.52715,-96.877441),                            # initial map, usa center, zoom 5, 37.09024,-95.712891
    'DEFAULT_ZOOM': 4,
    'MIN_ZOOM': 3,
    'MAX_ZOOM': 19,
    'ZOOM_SNAP': 0.25,
    'DEFAULT_PRECISION': 6,
    # 'TILES': [],
    'TILES': [
            ('WorldStreetMap','https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
                {'attribution': '&copy; ESRI WorldStreetMap', 'maxZoom': 18}),
            ('WorldImagery','https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',  
                {'attribution': '&copy; ESRI WorldImagery Map', 'maxZoom': 18}),
            ('Satellite', 'http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}',
                { 'attribution': '&copy; Google Satellite Map', 'maxZoom': 18}), 
            ('StreetMap', 'https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}',
                { 'attribution': '&copy; Google Street Maps', 'maxZoom': 18}),
            ('Hybrid','https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
                {'attribution': '&copy; Google Satellite Hybrid Map', 'maxZoom': 18})             
    ],
    # By default, a button appears below the zoom controls and, when clicked, shows the entire map. 
    # To remove this button, set to False
    'RESET_VIEW': True,
    # 'PLUGINS': {
    #     'name-of-plugin': {
    #         'css': ['relative/path/to/stylesheet.css', '/root/path/to/stylesheet.css'],
    #         'js': 'http://absolute-url.example.com/path/to/script.js',
    #         'auto-include': True,
    #      },
    #      path to all plugins: https://wordpress.org/plugins/extensions-leaflet-map/
    #      Note: as convenient as they are, we do not need to load all plugins at onces, let's see
    #  },
}


