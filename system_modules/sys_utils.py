# standard libs
import os
import pathlib
import json
import pprint
import subprocess

# third party libs
import geopandas as gpd
import pandas as pd
import xmltodict
from bs4 import BeautifulSoup
import chardet
from chardet.universaldetector import UniversalDetector

# app modules
from system_modules import activate_customer


#
# helper functions
#
def start_engines():
    
    from system_modules.etl_engine import etle
    from system_modules.geoserver_engine import geoe
    from system_modules.gis_engine import gise

    msg = f"Starting system engines: \n"
    msg += "    LSA ETLEngine\n"
    etl = etle
    msg += "    LSA GeoserverEngine\n"
    geo_rest = geoe
    msg += "    LSA GISEngine\n"
    giseng = gise
    
    return etl, geo_rest, giseng, msg 


def load_customer_config(data_json):
    # data_json = "D:/PROJECTS/survey-map-etl/tenants/southwestgaslv/config/test.cfg"
    f = open(data_json)
    data = json.load(f)
    f.close()
    return data


def get_customer_config(slug, tenant_dir):
    path = tenant_dir
    if path:
        file = os.path.join(path, slug, "config", slug + ".cfg")
        if os.path.isfile(file):
            return file
        else:
            msg = f"Error returning config file {file}\n"
            return msg
    else:
        msg = f"Error environment variable TENANT_DIR not set\n"
        return msg    


# PureWindowsPath('c:/Program Files/').root
# '\\'
# PureWindowsPath('c:Program Files/').root
# ''
# PurePosixPath('/etc').root
FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
def explore(path):
    # explorer would choke on forward slashes
    path = os.path.normpath(path)

    if os.path.isdir(path):
        subprocess.run([FILEBROWSER_PATH, path])
    elif os.path.isfile(path):
        subprocess.run([FILEBROWSER_PATH, '/select,', path])


def detect_char(bytelike):
    usock = urllib.request.urlopen('http://yahoo.co.jp/')     # TODO
    detector = UniversalDetector()
    for line in usock.readlines():
        detector.feed(line)
        if detector.done: break
    detector.close()
    usock.close()
    print(detector.result)


def parse_getcapability(xml_file):
    with open(xml_file, 'r') as f:
        data = f.read()
 
    # Passing the stored data inside
    # the beautifulsoup parser, storing
    # the returned object
    Bs_data = BeautifulSoup(data, "xml")
    # print(Bs_data)
 
    # Finding all instances of tag
    b_layer = Bs_data.find_all('Layer')
    minxs = []
    minys = []
    xs = []
    ys = []
    for lyr in b_layer:
        name = lyr.Name.get_text()
        bbox = lyr.find('LatLonBoundingBox')
        minx = bbox['minx']
        miny = bbox['miny']
        maxx = bbox['maxx']
        maxy = bbox['maxy']
        xs.append(float(minx))
        ys.append(float(miny))
        xs.append(float(maxx))
        ys.append(float(maxy))
    maxX = max(xs)
    maxY = max(ys)
    minX = min(xs)
    minY = min(ys)
    bbox_geoserver = [maxX, maxY, minX, minY]
    bbox_leaflet = [maxY, maxX, minY, minX]
    print(f"parse_getcapability: {bbox_leaflet}")
    return bbox_leaflet
        
      
def xml_2dict(filename):
    my_xml = """
    <audience>
      <id what="attribute">123</id>
      <name>Shubham</name>
    </audience>"""
    # Service, Request, Layer nodes
    import sys
    data = None
    if os.path.isfile(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            xml_data = file.read()
        dict_data = xmltodict.parse(xml_data)
        return dict_data

        keys = ["Capability"]
        _dict = {}
        for k, v in dict_data.items():
            if type(v) is dict:
                for kk, vv in v.items():
                    if 'Capability' in kk:
                        print("Key: ", kk)
                        for kkk, vvv in vv.items():
                           if 'Request' in kkk:
                               print("Key: ", kkk)
                               print(vvv.keys())
                               for kkkk in vvv.keys():
                                   print(vvv[kkkk])

        # pprint.pprint(dict_data, indent=2)
    else:
        print("something wrong with the file", filename)


def dms2dec(value):
    """
    Degres Minutes Seconds to Decimal degres
    StationId   StationName         Latitude    Longitude ...
     60351     JIJEL- ACHOUAT      36 48 00N     05 53 00E
    """
    degres, minutes, seconds = value.split()
    seconds, direction = seconds[:-1], seconds[-1]
    dec = float(degres) + float(minutes)/60 + float(seconds)/3600
    if direction in ('S', 'W'):
        return -dec
    return dec


def json_to_pandas(data_json):
    # data_json = "D:/PROJECTS/heath_lsa/customers/southwest_gas/modules/southwest_gas.cfg"
    print(data_json)
    df = pd.read_json(data_json, lines=True)
    print(df.to_string()) 


def read_filegdb(gdb):
    gpd.read_file(gdb, driver='FileGDB', layer=1)


def read_shapefile(filename):
    path_object = pathlib.path(filename)
    gdf = gpd.read_file(gpd.datasets.get_path(path_object),
          include_fields=["pop_est", "continent", "name"],
          ignore_fields=["iso_a3", "gdp_md_est"])


def filename(file_with_path):
    # file name with extension
    file_name = os.path.basename(file_with_path)

    # file name without extension
    return os.path.splitext(file_name)[0]


def disect_path(file_with_path):
    p = pathlib.Path(file_with_path)
    file_no_ext = p.stem
    filename = p.name
    dir = p.parent
    return dir, filename, file_no_ext


if __name__ == '__main__':
    # file = r"D:\PROJECTS\heath_lsa\OUTPUT\SWG\southwestgaslv_features.xml"
    # parse_getcapability(file)
    load_customer_config("test")