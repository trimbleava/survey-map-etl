# By https://raw.githubusercontent.com/jimutt/tiles-to-tiff/v1/tiles_to_tiff.py

import math
import urllib.request
import os
import sys
import glob
import subprocess
import shutil
from osgeo import gdal
import json

from tile_convert import bbox_to_xyz, tile_edges

#---------- CONFIGURATION -----------#
# Option 1: Online source
# tile_source = "http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}"
# tile_source = "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
tile_source = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
# crs="urn:ogc:def:crs:EPSG::3857" crs="urn:ogc:def:crs:OGC:2:84" TileMatrix: dpi 0.28mm as the physical dist. of a pixel by OGC

# Option 2: Local file system source
#tile_source = "file:///D:/path_to/local_tiles/{z}/{x}/{y}.png"

temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
output_dir = os.path.join(os.path.dirname(__file__), 'OUTPUT')

# X/LON goes from 0 (left edge is 180 °W) to 2^zoom − 1 (right edge is 180 °E)
# Y/LAT goes from 0 (top edge is 85.0511 °N) to 2^zoom − 1 (bottom edge is 85.0511 °S) in a Mercator projection
# USA Bounds: Northernmost: 49.382808 Southernmost: 24.521208 Easternmost: -66.945392 Westernmost: -124.736342
zoom = 16
lon_min = -124.736342
lon_max = -66.945392
lat_min = 24.521208
lat_max = 49.382808
#-----------------------------------#
# <ows:LowerCorner>-179.9999885408441 -85.00000000000003</ows:LowerCorner>
# <ows:UpperCorner>179.9999885408441 84.99999999999994</ows:UpperCorner>

def fetch_tile(x, y, z, tile_source):
    url = tile_source.replace(
        "{x}", str(x)).replace(
        "{y}", str(y)).replace(
        "{z}", str(z))
    path = os.path.join(temp_dir, f'{x}_{y}_{z}.jpg')
    print(path)

    # path = f'{temp_dir}/{x}_{y}_{z}.png'
    urllib.request.urlretrieve(tile_source, path)
    return(path)


def merge_tiles(input_pattern, output_path):
    merge_command = ['python', 'gdal_merge.py', '-o', output_path]
    print(output_path)
    for name in glob.glob(input_pattern):
        print(name)
        merge_command.append(name)

    subprocess.call(merge_command)


def georeference_raster_tile(x, y, z, path):
    bounds = tile_edges(x, y, z)
    print(bounds)
    filename, extension = os.path.splitext(path)
    gdal.Translate(filename + '.tif',
                   path,
                   outputSRS='EPSG:4326',
                   outputBounds=bounds)


def main():

    x_min, x_max, y_min, y_max = bbox_to_xyz(lon_min, lon_max, lat_min, lat_max, zoom)
    print(f"Fetching {(x_max - x_min + 1) * (y_max - y_min + 1)} tiles")
    
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            try:
                png_path = fetch_tile(x, y, zoom, tile_source)
                print(f"{x},{y} fetched")
                georeference_raster_tile(x, y, zoom, png_path)
            except OSError:
                print(f"{x},{y} missing")
                pass

    print("Fetching of tiles complete")

    # print("Merging tiles")
    # out_tif = os.path.join(output_dir, 'merged.tif')
    # tmp_tifs = os.path.join(temp_dir, '*.tif')
    # # merge_tiles(temp_dir + '/*.tif', output_dir + '/merged.tif')
    # merge_tiles(tmp_tifs, out_tif)
    # print("Merge complete")

    # shutil.rmtree(temp_dir)
    # os.makedirs(temp_dir)


if __name__ == "__main__":
    main()


