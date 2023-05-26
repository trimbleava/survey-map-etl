# standard libs
import os, sys
from functools import partial
import pathlib

# third party libs
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt   # this used by geopandas


# app modules
from system_modules.messenger_engine import msgr

import logging
logger = logging.getLogger(__name__)

# Python Libraries for GIS - Source: https://gisgeography.com/python-libraries-gis-mapping/
# ========================
# 1. Arcpy
#   If you use Esri ArcGIS, then you’re probably familiar with the ArcPy library. ArcPy is meant for geoprocessing operations. 
#   But it’s not only for spatial analysis, it’s also for data conversion, management, and map production with Esri ArcGIS.
#
# 2. Geopandas
#   Geopandas is like pandas meet GIS. But instead of straightforward tabular analysis, the Geopandas library adds a geographic 
#   component. For overlay operations, Geopandas uses Fiona and Shapely, which are Python libraries of their own.
#
# 3. GDAL/OGR
#   The GDAL/OGR library is used for translating between GIS formats and extensions. QGIS, ArcGIS, ERDAS, ENVI, GRASS GIS and 
#   almost all GIS software use it for translation in some way. At this time, GDAL/OGR supports 97 vector and 162 raster drivers.
#
# GIS Formats Conversions
# ========================
# 4. RSGISLib
#   The RSGISLib library is a set of remote sensing tools for raster processing and analysis. 
#   To name a few, it classifies, filters, and performs statistics on imagery. 
#   My personal favorite is the module for object-based segmentation and classification (GEOBIA).
#
# 5. PyProj
#   The main purpose of the PyProj library is how it works with spatial referencing systems. It can project and transform 
#   coordinates with a range of geographic reference systems. PyProj can also perform geodetic calculations and distances 
#   for any given datum.
#   geopandas uses pyproj as the engine and transforms the points within the geometries.
#   Fiona and rasterio are powered by GDAL and with algorithms that consider the geometry instead of just the points the 
#   geometry contains, slower, however.
#
# Python Libraries for Data Science
# =================================
# Data science extracts insights from data. It takes data and tries to make sense of it, such as by plotting it graphically 
# or using machine learning. This list of Python libraries can do exactly this for you.
#
# 6. NumPy
#   Numerical Python (NumPy library) takes your attribute table and puts it in a structured array. Once it’s in a structured 
#   array, it’s much faster for any scientific computing. One of the best things about it is how you can work with other Python 
#   libraries like SciPy for heavy statistical operations.
#
# 7. Pandas
#   The Pandas library is immensely popular for data wrangling. It’s not only for statisticians. But it’s incredibly useful 
#   in GIS too. Computational performance is key for pandas. The success of Pandas lies in its data frame. 
#   Data frames are optimized to work with big data. They’re optimized to such a point that it’s something that Microsoft Excel 
#   wouldn’t even be able to handle.
#
# 8. Matplotlib
#   When you’re working with thousands of data points, sometimes the best thing to do is plot it all out. Enter Matplotlib. 
#   Statisticians use the matplotlib library for visual display. Matplotlib does it all. It plots graphs, charts, and maps. 
#   Even with big data, it’s decent at crunching numbers.
#
# 9. Re (regular expressions)
#   Regular expressions (Re) are the ultimate filtering tool. When there’s a specific string you want to hunt down in a table, 
#   this is your go-to library. But you can take it a bit further like detecting, extracting, and replacing with pattern matching.
#
# 10. ReportLab
#   ReportLab is one of the most satisfying libraries on this list. I say this because GIS often lacks sufficient reporting 
#   capabilities. Especially, if you want to create a report template, this is a fabulous option. I don’t know why the ReportLab 
#   library falls a bit off the radar because it shouldn’t.
#
# 11. ipyleaflet
#   If you want to create interactive maps, ipyleaflet is a fusion of Jupyter notebook and Leaflet. You can control an assortment 
#   of customizations like loading basemaps, geojson, and widgets. It also gives a wide range of map types to pick from including 
#   choropleth, velocity data, and side-by-side views.
#
# 12. Folium
#   Just like ipyleaflet, Folium allows you to leverage leaflet to build interactive web maps. It gives you the power to manipulate 
#   your data in Python, then you can visualize it with the leading open-source JavaScript library.
#
# 13. Geemap
#   Geemap is intended more for science and data analysis using Google Earth Engine (GEE). Although anyone can use this Python 
#   library, scientists and researchers specifically use it to explore the multi-petabyte catalog of satellite imagery in GEE 
#   for their specific applications and uses with remote sensing data.
#
# 14. LiDAR
#   Simply named the LiDAR Python Package, the purpose is to process and visualize Light Detection and Ranging (LiDAR) data. 
#   For example, it includes tools to smooth, filter, and extract topological properties from digital elevation models (DEMs) data.
#   Although I don’t see integration with raw LAS files, it serves its purpose for terrain and hydrological analysis.
#
# 15. Scikit
#   Lately, machine learning has been all the buzz. And with good reason. Scikit is a Python library that enables machine learning.
#   It’s built into NumPy, SciPy, and Matplotlib. So, if you want to do any data mining, classification or ML prediction, 
#   the Scikit library is a decent choice.
#
# PRO TIP: 
#   If you need a quick list of functions for Python libraries, check out https://www.datacamp.com/cheat-sheet Cheat Sheets.

# Performance: http://blog.mathieu-leplatre.info/geodjango-maps-with-leaflet.html
# A map with more than 12 000 HTML objects is not going to be snappy.
#
# Hopefully, it won't be the case for your first applications !
#
# And fortunately, there are plently of different strategies to draw such an amount of data :
#
# Use marker clusters to reduce the number of elements on the map (see result here) ;
# Draw circles instead of markers and switch to Canvas (see Leaflet documentation) ;
# Use tiled geojson ;
# Render tiles using Tilemill/Mapnik ;
############################################## Main ##############################################
class GISEngine():
    global slug
    slug = os.getenv("slug")
   
    def gdf_read_shp(self, shapefile, include_fields=None, filter=None):
        gdf = None
        msg = f"Reading shapefile {shapefile} into geopandas\n"
        logger.info(msg)
        if slug:
            msgr[slug] = msg 

        if include_fields:
            if include_fields[0] == 'All':
                gdf = gpd.read_file(shapefile, driver='ESRI Shapefile')
            else:
                gdf = gpd.read_file(shapefile, driver='ESRI Shapefile', include_fields=include_fields)

            if filter:
                pass
        else:
            gdf = gpd.read_file(shapefile, driver='ESRI Shapefile')
            if filter:
                pass

        return gdf


    def save_geopkg(self, pkg, layer, gdf):
        # save as a geopackage, all the ovelays 
        msg = f"Adding {layer} to {pkg}\n"
        logger.info(msg)
        if slug:
            msgr[slug] = msg 

        self.gdf_to_geopkg(gdf, pkg, layer)


    def gdf_read_public(self):
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'), driver='ESRI Shapefile') 


    def bounds(self, geodf):     
        # get the bounding box of the mapsheet 
        df_bounds = geodf.envelope.bounds 
        xmin, ymin, xmax, ymax = df_bounds.values[0]
        return [[ymin, xmin], [ymax, xmax]]

    def bounds_simple(self, geodf):
        df_bounds = geodf.envelope.bounds 
        xmin, ymin, xmax, ymax = df_bounds.values[0]
        return xmin, ymin, xmax, ymax
        

    def get_xy(self, geodf):
        coords = list(geodf.exterior.coords)
        return (coords)


    def exteriors(self, geodf):
        exteriors = geodf[geodf.geometry.map(lambda z: True if not z.is_empty else False)].geometry.map(lambda z: z.exterior.xy)
        print(exteriors)


    def center(self, geodf):
        # calculate the centroid 
        x = geodf.geometry.centroid.x
        y = geodf.geometry.centroid.y
        return [y[0], x[0]]


    def expand_geometry(self, gdf):
        # expand the co-ordinates
        vals = gdf["geometry"].apply(lambda p: list(p.exterior.coords)).explode().apply(pd.Series).rename(columns=({0:"x", 1:"y"}))
        return vals


    # def get_tenant():
    #     # from django.db import connection
    #     # os.environ["DJANGO_SETTINGS_MODULE"] = "heath_lsa.setting_dir.dev_settings"
    #     # schema_name = connection.get_schema()
    #     # print(schema_name) 
    #     # tenant = connection.get_tenant()
    #     # print(tenant)
    #     # print(type(tenant))
    #     pass

    # def wkt_geofield(df):  # todo when needed
    #     df['mygeometry'] = df.WKT.apply(wkt.loads)
    #     df.drop('WKT', axis=1, inplace=True) # Drop WKT column
    #     # Geopandas GeoDataFrame
    #     gdf = gpd.GeoDataFrame(df, geometry='mygeometry')
    #     return gdf

    # Geopackage format offers a variety of features for scalability.  TODO
    # And that’s why you need to use Geopackage files instead of shapefile or GeoJSON.
    # https://towardsdatascience.com/why-you-need-to-use-geopackage-files-instead-of-shapefile-or-geojson-7cb24fe56416
    # Some Conversions
    # Using GDAL from the command line
    #
    # convert a shapefile to geopackage
    # $ ogr2ogr -f GPKG filename.gpkg abc.shp
    # all the files (shapefile/geopackage) will be added to one geopackage.
    # $ ogr2ogr -f GPKG filename.gpkg ./path/to/dir
    # add geopackage to postgres database
    # $ ogr2ogr -f PostgreSQL PG:"host=localhost user=user dbname=testdb password=pwd" filename.gpkg layer_name
    #
    def gdf_to_geopkg(self, gdf, pkg, fc):   # TODO spatial index this
        # note: shape file does not support datetime that we need
        # to_file_fiona(df, filename, driver, schema, crs, mode, **kwargs)
        gdf.to_file(pkg, layer=fc, driver="GPKG") 
 
    
    def gdf_by_bbox(fc, bbox):
        # bbox = (1031051.7879884212, 224272.49231459625, 1047224.3104931959, 244317.30894023244)
        gdf = gpd.read_file(gpd.datasets.get_path(fc), bbox=bbox,)
        return gdf


    def gdf_to_postgis(self, gdf, table_name, conn_str, schema=None, if_exists='append', index=False, 
                            index_label=None, chunksize=None, dtype=None):

        # Quoting an identifier also makes it case-sensitive, whereas unquoted names are always folded 
        # to lower case. For example, the identifiers FOO, foo, and "foo" are considered the same by 
        # PostgreSQL, but "Foo" and "FOO" are different from these three and each other.

        msg = ""
        try:
            # GeoDataFrame.to_postgis(name, con, schema=None, if_exists='fail', 
            # index=False, index_label=None, chunksize=None, dtype=None)
            gdf.to_postgis(table_name, conn_str, schema=schema, if_exists=if_exists, 
                        index=index, index_label=index_label, chunksize=chunksize, dtype=dtype)
        except Exception as e:
            msg = f"Connection could not be made due to the following {str(e)}\n"
            logger.warning(msg)
           
        return msg
    
   
    def reproject_to_4326(self, gdf):
        default_authority_code = default_crs = "EPSG:4326"
        new_gdf = gdf.to_crs(default_crs) 
        return new_gdf


    def gdf_plot(self, gdf, fc):

        # plot to see how it looks like
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # add roads to the plot
        # madera_roads.plot(cmap='Greys', ax=ax, alpha=.5)
        # ax.set(xlim=[-125, -116], ylim=[35, 40])

        # find out what type of geometry is this
        geom_type = gdf.geom_type
        logger.info("\n")
        logger.info(geom_type)

        # TODO - not working
        # if 'LineString' in geom_type:
        #     ax.get_lines().set_color("yellow")    

        # if 'Point' in geom_type:
        #     ax.get_points()[0].set_color("red")

        # if 'Polygon' in geom_type:
        #     ax.get_polygon()[0].set_color("blue")
        
        # add the gdf to the plot
        gdf.plot(ax=ax, color="black")

        # add a title for the plot
        ax.set_title(fc);

        # show the plot
        plt.show(block=True)   # False is not working!!
    
    
# use of pyproj
# def todo2():
#     from functools import partial
#     from pyproj.transformer import TransformerGroup
#     from shapely.geometry import Point
#     from shapely.ops import transform
#     import geopandas as gpd


#     transformer = TransformerGroup(4326, 22092).transformers[0]
#     transformer = partial(transform, transformer.transform)

#     d = {'col1': ['name1'], 'geometry': [Point(-11.5, 12.5)]}
#     gdf = gpd.GeoDataFrame(d, crs=4326)
#     gdf.set_geometry(gdf.geometry.apply(transformer),  inplace=True, crs=22092)

#     print(gdf)

#     from shapely.geometry import Point
#     s = geopandas.GeoSeries([Point(1, 1), Point(2, 2), Point(3, 3)], crs=4326)
#     s
#     0    POINT (1.00000 1.00000)
#     1    POINT (2.00000 2.00000)
#     2    POINT (3.00000 3.00000)
#     dtype: geometry
#     s.crs  
#     <Geographic 2D CRS: EPSG:4326>
#     Name: WGS 84
#     Axis Info [ellipsoidal]:
#     - Lat[north]: Geodetic latitude (degree)
#     - Lon[east]: Geodetic longitude (degree)
#     Area of Use:
#     - name: World
#     - bounds: (-180.0, -90.0, 180.0, 90.0)
#     Datum: World Geodetic System 1984
#     - Ellipsoid: WGS 84
#     - Prime Meridian: Greenwich
#     ##########
#     s = s.to_crs(3857)
#     s
#     0    POINT (111319.491 111325.143)
#     1    POINT (222638.982 222684.209)
#     2    POINT (333958.472 334111.171)
#     dtype: geometry
#     s.crs  
#     <Projected CRS: EPSG:3857>
#     Name: WGS 84 / Pseudo-Mercator
#     Axis Info [cartesian]:
#     - X[east]: Easting (metre)
#     - Y[north]: Northing (metre)
#     Area of Use:
#     - name: World - 85°S to 85°N
#     - bounds: (-180.0, -85.06, 180.0, 85.06)
#     Coordinate Operation:
#     - name: Popular Visualisation Pseudo-Mercator
#     - method: Popular Visualisation Pseudo Mercator
#     Datum: World Geodetic System 1984
#     - Ellipsoid: WGS 84
#     - Prime Meridian: Greenwich


# # set up Fiona transformer - examples to be used later
# def crs_to_fiona(proj_crs):
#     proj_crs = CRS.from_user_input(proj_crs)
#     if version.parse(fiona.__gdal_version__) < version.parse("3.0.0"):
#         fio_crs = proj_crs.to_wkt(WktVersion.WKT1_GDAL)
#     else:
#         # GDAL 3+ can use WKT2
#         fio_crs = proj_crs.to_wkt()
#     return fio_crs

# def base_transformer(geom, src_crs, dst_crs):
#     return shape(
#         transform_geom(
#             src_crs=crs_to_fiona(src_crs),
#             dst_crs=crs_to_fiona(dst_crs),
#             geom=mapping(geom),
#             antimeridian_cutting=True,
#         )
#     )

# # load example data
# world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

# destination_crs = "EPSG:3395"
# forward_transformer = partial(base_transformer, src_crs=world.crs, dst_crs=destination_crs)

# # Reproject to Mercator (after dropping Antartica)
# world = world[(world.name != "Antarctica") & (world.name != "Fr. S. Antarctic Lands")]
# with fiona.Env(OGR_ENABLE_PARTIAL_REPROJECTION="YES"):
#     mercator_world = world.set_geometry(world.geometry.apply(forward_transformer), crs=destination_crs)


# # Rasterio Example. This example requires rasterio 1.2+ and GDAL 3+.

# import geopandas
# import rasterio.warp
# from shapely.geometry import shape

# # load example data
# world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
# # Reproject to Mercator (after dropping Antartica)
# world = world[(world.name != "Antarctica") & (world.name != "Fr. S. Antarctic Lands")]

# destination_crs = "EPSG:3395"
# geometry = rasterio.warp.transform_geom(
#     src_crs=world.crs,
#     dst_crs=destination_crs,
#     geom=world.geometry.values,
# )
# mercator_world = world.set_geometry(
#     [shape(geom) for geom in geometry],
#     crs=destination_crs,
# )

# def todo3():
#     # I also tried ogr2ogr
#     # ogr2ogr out.gpkg -t_srs "EPSG:4326" in.gpkg
#     pass

# def data_from_xy():
#     x = [2.5, 5, -3.0]
#     y = [0.5, 1, 1.5]
#     s = geopandas.GeoSeries.from_xy(x, y, crs="EPSG:4326")
#     s
#     0    POINT (2.50000 0.50000)
#     1    POINT (5.00000 1.00000)
#     2    POINT (-3.00000 1.50000)
#     dtype: geometry


def start():
    # instatiate
    msg = "Starting GISEngine\n"
    logger.info(msg)
    global gise
    gise = GISEngine()
    msgr[gise] = msg

    return gise


if __name__ =="__main__":
    shapefile = "D:\PROJECTS\heath_lsa\INPUT\cb_2018_us_state_20m.shp"
    states = gdf_read_shp(shapefile)
    conn_str = "postgresql://heath_lsa_admin:heath_lsa_pass@localhost:5432/heath_lsa"
    table = "usa_states"
    gdf_to_postgis(states, conn_str, table)