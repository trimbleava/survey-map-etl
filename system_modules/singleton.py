#
# Singleton meta class with arguments - extend from this class
#

# standard libs
import inspect
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(message)s', level="INFO")
logger = logging.getLogger(__name__)

# class Singleton (type):
#     _instances = {}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             msg = f"Starting new Singleton {cls} \n"
# #           logger.info(msg)
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]

class Singleton:
    __instance = None
    
    def __new__(cls, *args, **kwargs):
        print(cls.__instance)
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, attr_a, attr_b, key={}):
        print('Initializing the object...')
        self.attr_a = attr_a
        self.attr_b = attr_b
        self.key = key
        

# class Singleton(type):
#     """ Simple Singleton that keep only one value for all instances
#     """
#     def __init__(cls, name, bases, dic):
#         print('Initializing the object...')
#         super(Singleton, cls).__init__(name, bases, dic)
#         cls.instance = None

#     def __call__(cls, *args, **kwargs):
#         if cls.instance is None:
#             cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls.instance


# class SingletonArgs(type):
#     """ Singleton that keep single instance for single set of arguments. E.g.:
#     assert SingletonArgs('spam') is not SingletonArgs('eggs')
#     assert SingletonArgs('spam') is SingletonArgs('spam')
#     """
#     _instances = {}
#     _init = {}

#     def __init__(cls, name, bases, dct):
#         cls._init[cls] = dct.get('__init__', None)

#     def __call__(cls, *args, **kwargs):
#         init = cls._init[cls]
#         if init is not None:
#             key = (cls, frozenset(
#                     inspect.getcallargs(init, None, *args, **kwargs).items()))
#         else:
#             key = cls
#             msg = f"Calling same Singleton {key} \n"
#             logger.info(msg)
            
#         if key not in cls._instances:
#             cls._instances[key] = super(SingletonArgs, cls).__call__(*args, **kwargs)
#             msg = f"Starting new Singleton {key} \n"
#             logger.info(msg)
#         return cls._instances[key]