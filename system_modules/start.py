# standard modules
import sys
import os
import logging
from datetime import datetime
import importlib

# app modules

# if 'sys_engine' not in sys.modules:
#     try:
#         import sys_engine        # sets up all the envs
#     except:
#         from system_modules import sys_engine    


from system_modules.message_logger import logger

#
# add the new customer module here
#
customers = ["Southwest Gas - LasVagas : tenants.southwestgaslv.start",
             "Southwest Gas - Phoenix : tenants.southwestgasph.start",
             "Southwest Gas - Tucson : tenants.southwestgastu.start",
             "Vectren : tenants.vectren.start"
            ]


def parse_this_customer_info(customer, slug=None):

    """given a set of pr-defined module constructs on the command line,
       user selects an integer number connected to the module of interest
       where this function dynamically finds the module's (i.e., customer) 
       class and its configuration file to the calling program to execute.   
    Args:
        customer (array): A pre-defined array of customer's modules(class).
        Per new customer, this array needs to be updated and the corresponding
        class and configuration file must be implemented prior to calling this
        script. See below in __main__.
    Returns:
        string: a tuple of string corresponding to the class name and the
                customer's configuration file. 
    """
    #
    # Construct the class name and the configuration file
    #
    full_module_name = customer
    if slug:
        result = [v for v in customers if slug in v]
        if result:
            customer = result[0] 
    
    full_module_name = customer
    arr = full_module_name.split(":")
    module_arr = arr[1].strip().split(".")
    module_name = f"{module_arr[0]}.{module_arr[1]}.{module_arr[2]}"

    #
    # All envs are set during the import of house_keeping module at the 
    # beginning of this script
    #
    parent = os.getenv("PROJECT_DIR")

    #
    # when running from command line needs these envs
    #
    os.environ["schema"] = module_arr[1]
    os.environ["tenant"] = arr[0]
    os.environ["slug"] = module_arr[1]

    #
    # Customer's configuration file is relative to project directory
    # Example: heath_lsa/tenants/southwestgaslc/config/southwestgaslv.cfg
    #     
    customer_conf =  os.path.join(parent, module_arr[0], module_arr[1], "config", module_arr[1] + ".cfg")
   
    return module_name, customer_conf 
   

if __name__ == "__main__":
    """This is the main program to execute this application from the
       command line. A web version of this app is also available that
       is using modules in concert with this version. Be carefull.

       To run while in project directory (i.e., heath_lsa) type:
       1) python ..\PY-ENV\Scripts\activate  - activate python environment 
       2) python system_modules\start.py     - to see the options
       3) python system_modules\start.py 1   - the intger of the customer of interest
    """

    where = '\n'
    for i, customer in enumerate(customers):
        name = customer.split(':')
        where += f"({str(i+1)})\t{name[0].strip()}\n"
    
    if len(sys.argv) < 2:
        msg = "Usage: python start.py customer_module_number (i.e 3)"
        logger.info(msg)
        logger.info(where)
        sys.exit(0)
    try:
        index = int(sys.argv[1]) - 1
        customer_module_name, customer_conf = parse_this_customer_info(customers[index])
        slug = os.getenv("slug", customer_module_name)
        msg = f"Parsing {slug}'s config file {customer_conf}\n"
        logger.info(msg)

    except Exception:
        # traceback.print_exc()
        msg = f"Error: Only values from 1 to {len(customers)} is allowed!\n"
        logger.error(msg)
        sys.exit(0)

    msg = "Starting process interactively ........."
    logger.info(msg)

    # The file gets executed upon import, as expected.
    cust_module = importlib.import_module(customer_module_name)
    
    # Customer configuration file is relative to system 
    # directory structure and name dependent. Watch for it.
    global slugobj
    slugobj = cust_module.main(customer_conf, slug)