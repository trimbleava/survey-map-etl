
# standard libs
import os, sys
import warnings
import json
import time

# third party libs
from django_tenants.utils import remove_www
from django.conf import settings
from django.db import utils
from django.core.cache import cache

# app modules
from customers.models import Client

import logging
logger = logging.getLogger('lsajang')

# 
# Using cache-based session backend:
# session is per user while cache is per application.
#
def print_sessions(request):
    logger.info("Entered print_sessions\n")

    if request.session.keys() is None:
        print("Session is empty\n")
        return
        
    print("\n")
    for key, value in request.session.items():
        msg = f"Key: {key} \tValue: {value}"
        print(msg)


def print_sessioncache(request):
       
    logger.info("Entered print_sessioncache\n")
    #  
    # The django cache key given by request.session.cache_key is for use with Django's 
    # low-level cache API. The final cache key send to backend cache (redis, memcach)
    # is the construct by make_key, <KEY_PREFIX>:<VERSION>:<KEY>. 
    #  
    
    dict = cache.get(request.session.cache_key)
    if dict is None:
        print("Cache is empty\n")
        return
    #
    # the above statements simply returns the same python dictionary for
    # all the key:values saved throughout for this tenant. So, we just have
    # to use this dictionary to get the key:value and not the cache anymore.
    # 

    print("\n") 
    for key, value in dict.items():
        print("Cache Key: ", key, "\nCached Value: ", value)
    return dict


def get_app_keys():
    # ov_layers = layer:bbox, ovlayers_bbox = ovlayers_union_bbox
    cached_session_keys = ["region", "slug", "schema", "tenant", "tenant_dir", "survey_copyright",
                           "survey_name", "surveymap_title",
                           "ov_layers", "ov_store", "ovlayers_bbox", 'ovlayers_status', 'ov_style',
                           "op_layers", "op_store", "oplayers_bbox", 'oplayers_status', 'op_style']
    return cached_session_keys

def reset_op_cache(flag):
    logger.info("Entered reset_op_cache\n")
    cache.set("modified", True)
    cachekey = get_app_keys()
    print(cache.get(cachekey))
    


def get_backend_cache(request):
    logger.info("Entered get_backend_cache\n")

    # cache.clear()  think before un-commenting this
    active_dict = {}

    # all_keys = cache.keys('*')  # these are the keys saved in backend Cache not the key per client
    # for cachekey in all_keys:
    #     print(cachekey)

    app_keys = get_app_keys()
    dict = cache.get(request.session.cache_key) 
    
    # dict = cache.get(cachekey)
    if dict:
        for key, value in dict.items():
            # we are only interested in our app_keys
            if key in app_keys:
                active_dict[key] = value
    return active_dict


def test_cache():
    logger.info("Entered test_cache\n")

    # tests ........
    # from django.core.cache import caches
        
    # print(caches['default'].make_key('test-key'))
    # cache = caches['default']
    # print(cache)
    # print(type(cache))

    # res = cache.set("test_key_nx", 442, nx=True)
    # print(res)
    # res = cache.get("test_key_nx")
    # print(res)

    # cache.set("key1", "foo_1")
    # cache.set("key2", "foo_2")
    # cache.set("key_3", "fo4")
    # keys = cache.keys("key*")
    # print(keys)
    # values = cache.delete_many(keys)
    # print(values)

    # all_keys = cache.keys('*')
    # for cachekey in all_keys:
    #    for key, value in cache.get(key).items():
    #
    # next_keys = cache.keys("django.contrib.sessions.cachefj3jc3oump8ky7jh9vlzs0zyraout2i4")  <== all_keys[0]
    # print(next_keys)
    # values = cache.get_many(next_keys)
    # print(values)


    # start the redis cache too
    # 127.0.0.1:6379> keys *
    # 1) "southwestgaslv_1681357685::1:django.contrib.sessions.cache3k0rlvnwqld5lqo48dgck7x4q5tid1bk"
    # 2) ":1:django.contrib.sessions.cachek4x8w40bs88pb0u8qspjjpnupmm2e3pj"
    # 127.0.0.1:6379> get southwestgaslv_1681357685::1:django.contrib.sessions.cache3k0rlvnwqld5lqo48dgck7x4q5tid1bk
    

def session_is_expired(request):
    #
    # set_expiry(0) means the user’s session cookie will expire when the user’s web browser is closed - default
    # get_expiry_age - returns the number of seconds until this session expires. For sessions with no custom 
    # expiration (or those set to expire at browser close), this will equal SESSION_COOKIE_AGE (1209600 seconds = 14 days)
    # 
    expires_at = request.session.get_expiry_age()
    logger.info(f"Expires in {expires_at} seconds") 
    return False if expires_at > 10 else True


def set_session(request, context=None, overwrite=True):
   
    logger.info("Entered set_session\n")

    #
    # these variables are set into environ from reading 
    # 1) customer config file in conjunction with url requests 
    # 2) system configuration file
    #
   
    # 
    # save these in environ and session for use in system_modules and map/js/html
    # Note: dict_items([('view', <tenants.views.TenantHomeView object at 0x000002276680B460>), ('region', 'Nevada')])
    # 
    # os.environ["slug"] = slug                  
    # os.environ["schema"] = schema
    # os.environ["tenant"] = name
  
    #
    # save variables received through context into session
    # which in return they get saved into cache per config
    # in settings
    #  
    for key, value in context.items():
        msg = f"{type(key)}: {key}, {type(value)}: {value}"

        #
        # we need to overwrite the cache variable upon change. 
        # to do this we have option to modify the variable only
        # or in our case we set the overwrite flag to True, where
        # any variable chaged will be updated and the others stay
        # the same. I think everytime user starts a new session
        # despite the fact cache is per application, we should have
        # overwrite=True. If we need to use any specific variable
        # to save for the future use, we should use the cache versioning
        # until otherwise we realize problem with this method.
        #
        if overwrite:
            request.session.modified = True

        if type(key) is not str:
            # logger.warning(msg + ", NOT SAVED")
            continue  
        elif 'view' in key:
            # logger.warning(msg + ", NOT SAVED")
            continue
        else:
            # logger.info(msg + ", SAVED")
            request.session[key] = value

    if overwrite:
        request.session.save() 

           
def display_helper(request, context=None):
    """This function updates the information located in the bottom navigation bar

    Args:
        request (http): http request received from web browser
        context (dictionary, optional): this context is retunred into the current page. 
        Here we either append or create the context we need. Defaults to None.

    Returns:
        http response: returns the response through the context created here to the
        current web page.
    """
    logger.info("Entered display_helper\n")

    if not context:
        context = {}

    hostname_without_port = remove_www(request.get_host().split(':')[0])
  
    try:
        public_schema = request.session.get('public_schema', None)
        if public_schema is None:
            Client.objects.get(schema_name='public')
    except utils.DatabaseError:
        context['need_sync'] = True
        context['shared_apps'] = settings.SHARED_APPS
        context['tenants_list'] = []
        return context
    except Client.DoesNotExist:
        context['no_public_tenant'] = True
        context['hostname'] = hostname_without_port

    if request.session.get('public_schema_count', 0):
        context['only_public_tenant'] = True
    else:
        if Client.objects.count() == 1:
            context['only_public_tenant'] = True
            request.session['public_schema_count'] = 1

    
    tenants_list = []
    cnt = request.session.get("num_clients", 2)
    if cnt >= 3:
        for i in range(cnt):
            tenants_list.append('client'+ str(i))
        context['tenants_list'] = tenants_list
    else:
        context['tenants_list'] = Client.objects.all()
        request.session['num_clients'] = len(context['tenants_list'])

    return context

#
# Looping over UploadedFile.chunks() instead of using read() 
# ensures that large files don’t overwhelm your system’s memory.
# The actual file data is stored in request.FILES. Each entry in 
# this dictionary is an UploadedFile object (or a subclass) – a 
# wrapper around an uploaded file (class TemporaryUploadedFile,
# class InMemoryUploadedFile, isinstance(obj, class))
#
def handle_uploaded_file(uploadedfile, out_dir):
    logger.info("Entered handle_uploaded_file")

    fname = uploadedfile.name
    full_filename = os.path.join(out_dir, fname)
    fout = open(full_filename, 'wb+')
    for chunk in uploadedfile.chunks():   # default: chunk_size=25000
        fout.write(chunk)     
    fout.close()
    msg = f"{full_filename} uploaded"
    return msg
    
#
# Cache that is not working for another time    
# 
# from django.core.cache import cache
# from pymemcache.client.base import Client
# print("oooooooooooooooooooooooooooooooo\n")
# client = ipv4_client_using_tuple = Client(('127.0.0.1', 11211))
# # client = ipv6_client_using_tuple = Client(('::1', 11211))
# result = client.get('vj4oaoezl32x5gbfz9ejao8g62z1hr6i')
# print(result) 
# result = client.get('django.contrib.sessions.cachevj4oaoezl32x5gbfz9ejao8g62z1hr6i')
# # s = self.scope['session']['vj4oaoezl32x5gbfz9ejao8g62z1hr6i']
# # s = self.scope['session'].session_key
# print(result) 
# client.set('some_key', 'some value')
# result = client.get('slug')
# print(result)
# # dict = cache.get(s.cache_key)
# # print(dict)
# print("kkkkkkkkkkkkkkkkkkkkk")


# Examples TODO
#
# {% load cache %}

# <html>
# <head>
#   <title>Recipes</title>
#   <style>
#       body {
#           background-color:yellow;
#         }
#   </style>
# </head>
# <body>

# {% cache 500 recipe %}


# {% for recipe in recipes %}
#   <h1>{{ recipe.name }}</h1>
#   {% autoescape off %}
#     <p>{{ recipe.desc }}</p>
#   {% endautoescape %}
#   <h2>Ingredients</h2>
#   <ul>
#     {% for ingredient in recipe.ingredient_set.all %}
#     <li>{{ ingredient.description }}</li>
#     {% endfor %}
#   </ul>

# {% endfor %}
# {% endcache %}
# </body>
# </html>