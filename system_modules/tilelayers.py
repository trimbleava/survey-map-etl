# standard libs
import os, sys
from os.path import dirname, abspath

# third party libs
from geo.Geoserver import Geoserver, GeoserverException
from dotenv import load_dotenv 
from bs4 import BeautifulSoup


# app modules
import house_keeping as setup

esri_titles_list = ['Esri.WorldImagery', 'Esri.WorldStreetMap', 'Esri.WorldGrayCanvas']



def main():

    geoserver_url = os.getenv("GEOSERVER_URL")
    geo_uname = os.getenv("GEOSERVER_USER")
    geo_pass = os.getenv("GEOSERVER_PASS")
    geo = Geoserver(geoserver_url, username=geo_uname, password=geo_pass)

    geo_workspace = "basemap"

    # workspace location in default installation of geoserver
    url = '{}/workspaces/{}/'.format(geoserver_url,geo_workspace)  

    status = 0
    try: 
        response = geo.create_workspace(workspace=geo_workspace)
        if response in "201 Workspace {} created!".format(geo_workspace):
          status = 1
    except Exception as e:
        response = str(e)
        soup = BeautifulSoup(response, 'html.parser')
        print(soup.title.string)
    
    if status == 1: 
        geo_store = 'TODO'
        # for uploading raster data to the geoserver
        geo.create_coveragestore(layer_name='layer1', path=r'path\to\raster\file.tif', workspace='demo')
        # geo.create_shp_datastore(path=r'path/to/zipped/shp/file.zip', store_name='store', workspace='demo')

    xmin = os.getenv("XMIN")
    ymin = os.getenv("YMIN")
    xmax = os.getenv("XMAX")
    ymax = os.getenv("YMAX")
    crs = os.getenv("CRS")
    width = os.getenv("WIDTH")
    height = os.getenv("HEIGHT")

    # raster basemap tiles, bunch or providers of xyz tiles
    # class Bunch(dict):  class TileProvider(Bunch):
    # import xyzservices.providers as xyz -> lib._load_json(f) -> Bunch=providers (<class 'xyzservices.lib.Bunch'>)
    # 

    # esri_bunch_obj = xyz.providers.filter("Esri")
    # esri_bunch_obj = esri_bunch_obj.items()  # html version
 
    # esri_dict = esri_bunch_obj.flatten()  # text version
    # esri_titles_list = ['Esri.WorldImagery', 'Esri.WorldStreetMap', 'Esri.WorldGrayCanvas']
    # for esri_key in esri_dict.keys():
    #    if esri_key in esri_titles_list:
    #        print(esri_key)
    # print("=====================================")
  
    # data_url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
    # data_url = "http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}"
    # db = gpd.read_file(data_url)
    # print(db)
    # print(type(db))
    # ax = db.plot(color="red", figsize=(9, 9))
    # cx.add_basemap(ax, crs=db.crs.to_string())
    # cx.add_basemap(ax)
    # plt.show()

    # google_titles_list = ['Esri.WorldImagery', 'Esri.WorldStreetMap', 'Esri.WorldGrayCanvas']
    # google_street_map_provider = xyz.TileProvider(
    #     name="Google Street Map",
    #     url="https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}",
    #     attribution="(Google) Street Maps",
    # )
  
    # google_street_map_tiles = xyz.Bunch(GoogleStreetMap=google_street_map_provider)
    # print(google_street_map_tiles)
 


if __name__ == '__main__':
    main()
