# standard libs
import functools

# In Python, functions are first-class objects. This means that functions can be passed  
# around and used as arguments, just like any other object (string, int, float, list, and so on)
#
# Decorators provide a simple syntax for calling higher-order functions.
# By definition, a decorator is a function that takes another function and extends the 
# behavior of the latter function without explicitly modifying it.
# @ symbol, sometimes called 'pie symbol' is a syntactic sugar.
#
# Below is an example of a decorator with argument and return value
def decorator(func):
    # Introspection is the ability of an object to know about its own attributes at runtime
    # Using functools decorator helps decorator keep introspection properties
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        # Do something before
        value = func(*args, **kwargs)
        # Do something after
        return value
    return wrapper_decorator
# Usage: 
#
# SLD decorators
