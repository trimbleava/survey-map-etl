# standard libs
import os
import sys
import json

# third part libs
import geopandas as gpd
import fiona

# app modules

if 'database_helper' not in sys.modules:    
    from system_modules import database_helper as pgdb

if 'sys_engine' not in sys.modules:
    try:
        import sys_engine        # sets up all the envs
    except:
        from system_modules import sys_engine  

from system_modules.message_logger import logger
from system_modules.messenger_engine import msgr
from system_modules.gis_engine import gise
from system_modules.geoserver_engine import geoe
from system_modules.activate_customer import slugobj
from system_modules import sys_utils

msg = f"Entered {__name__}\n"
logger.info(msg)

class ETLEngine():
    def __init__(self):
        self.overlays = {}
        self.legends = {}
        self.geopkg = None
        self.cnt = 0
    
    def extract_ovelays(self, slugobj):  
        input_path = slugobj.input_path
        input_types = slugobj.input_types
        overlay_list = slugobj.overlays  
        slug = slugobj.slug
        overlays = {}
        legends = {}
        for fc, geom,include,filter,legend in overlay_list:
            f = fc +".shp"
            legends[(fc, geom)] = legend.split(",")         # list
            overlays[f] = (include.split(","), filter)      # tuple

        # save this as msg
        msg = overlays.keys()
        msg_str = ', '.join(msg)
        msg = "    Extracting data for " + msg_str
        legend_str = "["
        for key, val in legends.items():
            legend_str += " ".join(val)
            legend_str += "], ["
        msg += "\n    With legend for fields " + legend_str[:-2]
        msgr[slug] = msg

        # get the shapefiles data
        overlays_with_path = {}

        for path, subdirs, files in os.walk(input_path):
            for file in files:
                for key, values in overlays.items():
                    if file.endswith(key) : 
                        shp = os.path.join(path,file)
                        overlays_with_path[shp] = values
                        continue

        # delete the old dict
        overlays.clear()

        # save these for later use
        self.overlays = overlays_with_path
        self.legend = legend


    def extract_else(self):
        
        input_path = slugobj.input_path
        input_types = slugobj.input_types
        overlay_list = slugobj.overlays  
        operation_list = slugobj.operations
        survey_type_dict = slugobj.survey_type_dict
        slug = slugobj.slug
        overlays = {}
        legends = {}
        for fc, geom,include,filter,legend in overlay_list:
            f = fc +".shp"
            legends[(fc, geom)] = legend.split(",")         # list
            overlays[f] = (include.split(","), filter)      # tuple

        # save this as msg
        msg = overlays.keys()
        msg_str = ', '.join(msg)
        msg = "2) Extracting data for " + msg_str
        legend_str = "["
        for key, val in legends.items():
            legend_str += " ".join(val)
            legend_str += "], ["
        msg += "\n    With legend for fields " + legend_str[:-2]
        msgr[slug] = msg
 
        # get the shapefiles data
        overlays_with_path = {}

        for path, subdirs, files in os.walk(input_path):
            for file in files:
                for key, values in overlays.items():
                    if file.endswith(key) : 
                        shp = os.path.join(path,file)
                        overlays_with_path[shp] = values
                        continue

        # delete the old dict
        overlays.clear()

        # save these for later use
        self.overlays = overlays_with_path
        self.legend = legend

    # divided into smaller functions for the webside, this head is copied over.
    def transform_overlays_head(self, slugobj):
        # save data in this file as a geopackage
        gpkg = os.path.join(slugobj.output_path, "Overlay.gpkg")

        slug = slugobj.slug

        for fc, values in self.overlays.items():
            self.transform_overlay_per_layer(slug, fc, values, slugobj, gpkg)


    def transform_overlay_per_layer(self, slug, fc, values, slugobj, gpkg):
        
        msg = f"Transform in place for {fc}:"
        msgr[slug] = msg
        logger.info(msg)

        # read shapefile into gpd and remove extra columns
        msg += f"Reading shapefiles into geopandas and removing extra columns"
        msgr[slug] = msg
        logger.info(msg)
        include_fields, filter = values
        gdf = gise.gdf_read_shp(fc, include_fields, filter)
    
        # reproject and save as geopackage
        msg += f"Re-projecting to 4326"
        msgr[slug] = msg
        logger.info(msg)
        gdf = gise.reproject_to_4326(gdf)

        # print few lines of the new data
        msg += gdf.iloc[:5,:-1].to_string()
        msg + "\n"
        msgr[slug] = msg
        logger.info(msg)

        fcname = sys_utils.filename(fc)
        msg += f"Saving overlay {fcname} into geopackage {gpkg}"
        msgr[slug] = msg
        logger.info(msg)
        gise.save_geopkg(gpkg, fcname, gdf)

        # get bounding box for use in map
        xmin, ymin, xmax, ymax = gise.bounds_simple(gdf)
        slugobj.layers[fcname] = (xmin, ymin, xmax, ymax)

        # plot the layer
        # gise.gdf_plot(gdf, fcname)
        return gpkg, msg

    def transform_overlay(self, slugobj):
        
        # save data in this file as a geopackage
        gpkg = os.path.join(slugobj.output_path, "Overlay.gpkg")
        
        slug = slugobj.slug
        for fc, values in self.overlays.items():
            msg = f"Transform in place for {fc}:\n"
            msgr[slug] = msg
            logger.info(msg)

            # read shapefile into gpd and remove extra columns
            msg = f"    Reading shapefiles into geopandas and removing extra columns\n"
            msgr[slug] = msg
            logger.info(msg)
            include_fields, filter = values
            gdf = gise.gdf_read_shp(fc, include_fields, filter)
        
            # reproject and save as geopackage
            msg = f"    Re-projecting to 4326\n"
            msgr[slug] = msg
            logger.info(msg)
            gdf = gise.reproject_to_4326(gdf)

            # print few lines of the new data
            msg = gdf.iloc[:5,:-1].to_string()
            msg + "\n"
            msgr[slug] = msg
            logger.info(msg)

            fcname = sys_utils.filename(fc)
            msg = f"    Saving overlay {fcname} into geopackage {gpkg}\n"
            msgr[slug] = msg
            logger.info(msg)
            gise.save_geopkg(gpkg, fcname, gdf)

            # get bounding box for use in map
            xmin, ymin, xmax, ymax = gise.bounds_simple(gdf)
            slugobj.layers[fcname] = (xmin, ymin, xmax, ymax)

            # plot the layer
            # gise.gdf_plot(gdf, fcname)

        self.geopkg = gpkg
        return gpkg


    def load_geopkg(self, slugobj):
  
        pkgdir, pkgfile, storename = sys_utils.disect_path(self.geopkg)

        store = storename
        if 'slug' not in os.environ or 'tenant' not in os.environ or 'schema' not in os.environ:
            msg = "slug, tenant, schema environment variables are not set!\n"
            logger.error(msg)
            raise SystemExit 

        schema = slugobj.schema        # 'southwestgaslv_1676228649'
        slug = slugobj.slug            # "southwestgaslv"
        tenant = slugobj.tenant        # South West Gas - LA"
        wrksp = slug

        # print("Pkgdir: ", pkgdir)
        # print("pkgfile: " + pkgfile)
        # print("store: " + storename)
        # print("Schema: " + schema)
        # print("wrkspace: " + wrksp)
    
        # First must copy the geopackage and shapes into data directory, got permission problem:
        # The GeoServer "daemon" must be run by a user that has write permission to the data 
        # you have specified. If it can not read & write to that file then it will switch to 
        # the default data directory. This is why your set up works when you run it as root 
        # (i.e. sudo  ./startup.sh) since root can do anything it likes - that is why it is 
        # a very dangerous thing to run a service as root so don't do this in production.
        #
        # You need to set up a user called geoserver and then run:
        # sudo chown -R geoserver /var/lib/geoserver_data to make sure it has the necessary ownership.
        # Then use this geoserver user in your startup script.
        # 
        # The binary version, not as a service, the GEOSERVER_DATA_DIR is set to webapp/geoserver/data
        # that has read/write permission. Regardless, currently, I am changing this env per client
        # to go to our own data directory. It is not portable but data is safe.
        #
      
        msg = "Instantiating geoserver object\n"
        msgr[slug] = msg
        logger.info(msg)
        geo_rest = geoe.GeoserverRestApi(slugobj)

        cnt += 1
        msg = f"{str(cnt)}) Creating workspace {wrksp}\n"
        msgr[slug] = msg
        logger.info(msg)
        geoe.create_workspace(wrksp)

        cnt +=1
        msg = f"{str(cnt)}) Creating datastore {store}\n"
        geoe.create_geopkg_datastore(store, pkgfile, wrksp, overwrite=False)
        msgr[slug] = msg
        logger.info(msg)

        cnt += 1
        msg = f"{str(cnt)}) Publishing layers:\n"
        geoe.publish_geopkg_layers(store, pkgfile, wrksp)
        msgr[slug] = msg
        logger.info(msg)

        cnt += 1
        msg = f"{str(cnt)}) Publishing legends:\n"
        msgr[slug] = msg
        logger.info(msg)

        # get sld_path
        tenant_dir = os.path.join(os.getenv("TENANT_DIR"))
        sld_path = os.path.join(tenant_dir, wrksp, "sld")      
        for layer in slugobj.layers: 
            sldfile = os.path.join(sld_path,layer+".sld")               
            if os.path.isfile(sldfile):
                msg = f"     Publishing legend for {layer}\n"
                msgr[slug] = msg
                logger.info(msg)

                # construct the geoserver style and publish
                style_name = wrksp+":"+layer 
                geoe.layer_sld(sldfile, wrksp, layer, style_name)
            
        msg = "Finished processing Overlay layers\n"
        msgr[slug] = msg
        logger.info(msg)

        # geo_rest.featurestore_layer_postgis(store, wrksp, tble_name, schema='public')

        # sldfile = "D:\\PROJECTS\\heath_lsa\\customers\\southwest_gas\\tenant_modules\\main_lines.sld" 
        # style_name = wrksp+":main_lines"
        # geo_rest.layer_sld(sldfile, wrksp, geoserver_lyrname, style_name)

        # geo_rest.publish_geopackage(pkgdir, pkgfile, wrksp, store)



def start():
    # instatiate
    msg = "Starting ETLEngine\n"
    logger.info(msg)
    global etle
    etle = ETLEngine()
    msgr[etle] = msg

    return etle
    

"""pipelines for extracting, transforming, and loading customer data."""
def extract(obj):
    input_path = obj.input_path
    input_types = obj.input_types
    overlay_list = obj.overlays      # includes geometry type
    operation_list = obj.operations
    survey_type_dict = obj.survey_type_dict
  
    # local variable
    # we need only the .shp, assume the rest of the files are within the same directory
    shp_ext = [".cpg", ".dbf", ".prj", ".sbn", ".sbx", ".shp", ".shp.xml", ".shx"]
    overlays = {}
    legends = {}

    # all data in obj (i.e.; reading config json file) is in string type, must change to correct types before processing
    for fc, geom,include,filter,legend in overlay_list:
        f = fc +".shp"
        legends[(fc, geom)] = legend.split(",")         # list
        overlays[f] = (include.split(","), filter)      # tuple

    # save this as msg
    msg = overlays.keys()
    msg_str = ', '.join(msg)
    msg = "2) Extracting data for " + msg_str
    legend_str = "["
    for key, val in legends.items():
        legend_str += " ".join(val)
        legend_str += "], ["
    msg += "\n    With legend for fields " + legend_str[:-2]
    obj.message = msg
 
    # get the shapefiles data
    overlays_with_path = {}

    for path, subdirs, files in os.walk(input_path):
        for file in files:
            for key, values in overlays.items():
                if file.endswith(key) : 
                    shp = os.path.join(path,file)
                    overlays_with_path[shp] = values
                    continue
    overlays.clear()    # delete the old dict 
    
    return overlays_with_path, legends


def transform_overlay(layer_dict, obj):
    """_summary_

    Args:
        layer_dict (_type_): _description_

    Returns:
        _type_: _description_
    """
    gpkg = os.path.join(obj.output_path, "Overlay.gpkg")
    
    global_msg = ""
    cnt = 3
    gisengine = gise.GISEngine(obj)

    for fc, values in layer_dict.items():
        msg = f"{str(cnt)}) Transform in place for {fc}:\n"
        global_msg += msg

        # read shapefile into gpd and remove extra columns
        msg = f"    Reading shapefiles into geopandas and removing extra columns\n"
        global_msg += msg
        include_fields, filter = values
        gdf = gisengine.gdf_read_shp(fc, include_fields, filter)
       
        # reproject and save as geopackage
        msg = f"    Re-projecting to 4326\n"
        global_msg += msg
        gdf = gisengine.reproject_to_4326(gdf)
        
        # print few lines of the new data
        msg = gdf.iloc[:5,:-1].to_string()
        global_msg += msg + "\n"
        
        fcname = sys_utils.filename(fc)
        msg = f"    Saving overlay {fcname} into geopackage {gpkg}\n"
        global_msg += msg
        gisengine.save_geopkg(gpkg, fcname, gdf)

        # get bounding box for use in map
        xmin, ymin, xmax, ymax = gisengine.bounds_simple(gdf)
        obj.layers[fcname] = (xmin, ymin, xmax, ymax)


        # plot the layer
        # gisengine.gdf_plot(gdf, fcname)

        cnt += 1     # for numbering steps of operation on the web

    obj.message = global_msg
    logger.info(global_msg)
    return gpkg, cnt

    
def transform_operation(layer_dict, output_path, pgdb_engin):
    for fc, values in layer_dict.items():
        msg = f"\nTransform in place for {fc}"
       
        # read shapefile into gpd and remove extra columns
        include_fields, filter = values
        gdf = gise.gdf_read_shp(fc, include_fields, filter)
     
        # reproject and save as geopackage
        gdf = gise.reproject_to_4326(gdf)
        print(gdf.head)

        # create the model
        fcname = sys_utils.filename(fc)
        table_name = fcname
        schema = 'southwestgaslv_1676228649'
        tenant_name = "southwestgaslv"
        path_to_models = os.path.join(os.getenv("TENANT_DIR"), tenant_name, "models.py")
        newshp = os.path.join(output_path, fcname + ".shp")
        gdf.to_file(newshp)
        gise.generate_model(newshp, path_to_models, table_name, 'geom', 4326)
        
        # send data to postgis database
        msg = f"\nAdding {fcname} to db schema {schema}"
        logger.info(msg)
        newgdf = gise.gdf_read_shp(newshp)
        gise.gdf_to_postgis(newgdf, tenant_name+"_"+table_name, pgdb_engin, schema=schema) 
       
        # plot the layer
        # gise.gdf_plot(gdf, fcname)





def load_geopkg(geopkg, obj, cnt):
  
    pkgdir, pkgfile, storename = sys_utils.disect_path(geopkg)
  
    store = storename
    if 'slug' not in os.environ or 'tenant' not in os.environ or 'schema' not in os.environ:
        msg = "slug, tenant, schema environment variables are not set!\n"
        logger.error(msg)
        raise SystemExit 

    # set in tenants views
    schema = os.getenv("schema")        # 'southwestgaslv_1676228649'
    slug = os.getenv("slug")            # "southwestgaslv"
    tenant = os.getenv("tenant")        # South West Gas - LA"
    wrksp = slug

    # print("Pkgdir: ", pkgdir)
    # print("pkgfile: " + pkgfile)
    # print("store: " + storename)
    # print("Schema: " + schema)
    # print("wrkspace: " + wrksp)
    
    # first copy the geopackage and shapes into data directory, permission problem:
    # The GeoServer "daemon" must be run by a user that has write permission to the data 
    # you have specified. If it can not read & write to that file then it will switch to 
    # the default data directory. This is why your set up works when you run it as root 
    # (i.e. sudo  ./startup.sh) since root can do anything it likes - that is why it is 
    # a very dangerous thing to run a service as root so don't do this in production.
    # You need to set up a user called geoserver and then run
    # sudo chown -R geoserver /var/lib/geoserver_data to make sure it has the necessary ownership.
    # Then use this geoserver user in your startup script.
    # 
    # The binary version, not as a service, the GEOSERVER_DATA_DIR is set to webapp/geoserver/data
    # that has read/write permission. Regardless, currently, I am changing this env per client
    # to go to our own data directory. It is not portable but data is safe.
    #
    msg = str(cnt) + ") "
    msg += "Instantiating geoserver object\n"
    geo_rest = geoe.GeoserverRestApi(obj)
    cnt += 1
    msg += f"{str(cnt)}) Creating workspace {wrksp}\n"
    msg += geo_rest.create_workspace(wrksp)
    cnt += 1
    msg += f"{str(cnt)}) Creating datastore {store}\n"
    msg += geo_rest.create_geopkg_datastore(store, pkgfile, wrksp, overwrite=False)
    cnt += 1
    msg += f"{str(cnt)}) Publishing layers:\n"
    msg += geo_rest.publish_geopkg_layers(store, pkgfile, wrksp)
    cnt += 1
    msg += f"{str(cnt)}) Publishing legends:\n"
    
    # get sld_path
    tenant_dir = os.path.join(os.getenv("TENANT_DIR"))
    sld_path = os.path.join(tenant_dir, wrksp, "sld")      
    for layer in obj.layers: 
        sldfile = os.path.join(sld_path,layer+".sld")               
        if os.path.isfile(sldfile):
            msg += f"     Publishing legend for {layer}\n"
            # construct the geoserver style and publish
            style_name = wrksp+":"+layer 
            msg += geo_rest.layer_sld(sldfile, wrksp, layer, style_name)
          
    msg += "Finished processing Overlay layers\n"
    obj.message = msg

    # geo_rest.featurestore_layer_postgis(store, wrksp, tble_name, schema='public')

    # sldfile = "D:\\PROJECTS\\heath_lsa\\customers\\southwest_gas\\tenant_modules\\main_lines.sld" 
    # style_name = wrksp+":main_lines"
    # geo_rest.layer_sld(sldfile, wrksp, geoserver_lyrname, style_name)

    # geo_rest.publish_geopackage(pkgdir, pkgfile, wrksp, store)


################## Main #####################
def main(obj):
    """ The job of etl is to extract data, TODO

    Args:
        obj (customer class): "An instance of the active client to do the etl for"
    """
  
    overlay_dict, legend_dict = extract(obj)
    geopkg, cnt = transform_overlay(overlay_dict, obj)
    load_geopkg(geopkg, obj, cnt)
    #
    # transform_operation(operational_dict, obj.output_path, obj.pgdb_engin)
   


    

    
        


    