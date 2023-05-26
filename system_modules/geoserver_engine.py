# -*- coding: utf-8 -*-
"""Geoserver engin module
Description: This module interfaces the package geoserver-rest in that it passes 
    application specific parameters to the rest methods.
Created Date: 2/4/2023
Credit: https://geoserver-rest.readthedocs.io/en/latest/how_to_use.html#getting-started-with-geoserver-rest
Developer: Beheen Moghaddam Trimble

Example:
    http://localhost:8080/geoserver/rest/workspaces
    http://localhost:8080/geoserver/rest/workspaces/ne/datastores/GeoPackageSample/featuretypes/populated_places.html
    Feature Type "populated_places"
    Name: populated_places
    Description: null
    Abstract: City and town points
    Enabled: true
    SRS: EPSG:4326
    Bounds: ReferencedEnvelope[-175.2205644999999 : 179.2166470999999, -41.29206799231509 : 64.14345946317033] DefaultGeographicCRS[EPSG:WGS 84] AXIS["Geodetic longitude", EAST] AXIS["Geodetic latitude", NORTH]>

Todo: 
"""

# standard libs
import os
import sys
import shutil
import glob
import httplib2
import threading
import urllib
import urllib.request
from xmltodict import parse, unparse
from urllib.parse import urlparse, urljoin


# third party libs
import requests
from bs4 import BeautifulSoup
from geo.Geoserver import Geoserver
import fiona

# app modules
from system_modules.message_logger import logger


# Custom exceptions.
class LSAGeoserverException(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        super().__init__(f"Status : {self.status} - {self.message}")


class GeoserverRestAPI(Geoserver):

    def __init__(self, 
        service_url =  os.getenv("GEOSERVER_URL", "http://127.0.0.1:8080/geoserver"),
        username = os.getenv("GEOSERVER_USERNAME", "admin"),
        password = os.getenv("GEOSERVER_PASSWORD", "geoserver")):

        super().__init__(service_url, username,  password)


    def create_workspace(self, wksp_name):
        
        """For creating workspace in geoserver

        Args:
            wksp_name (_type_): _description_
        """
        try: 
            super().create_workspace(wksp_name)
            msg = f"          Workspace {wksp_name} created"
            return msg
        except Exception as e:
            if str(e).find("already exists"):
                msg = f"          Workspace {wksp_name} already exists"
                return msg
       
           
    def coveragestore_layer(self, layer_name, path_to_tiff):
        """It is helpful for publishing the raster data to the geoserver. 
        Here if you don’t pass the lyr_name parameter, it will take the raster file name as the layer name.

        Args:
            layer_name (_type_): _description_
            path_to_tiff (_type_): _description_
        """
    
        self.create_coveragestore(layer_name=layer_name, path=path_to_tiff, workspace=self.workspace)


    def geoserver_legend(self):
        """
        http://localhost:8080/geoserver/rest/workspaces/southwestgaslv/datastores/Overlay/featuretypes/MainLines

        Example:
        https://mysite.net/geoserver/wms?request=GetMap&service=WMS&version=1.1.1
        &layers=myworkspace:buildings,myworkspace:roads
        &styles=buildings,roads&srs=EPSG%3A3765&bbox=397034%2C4909706%2C397213%2C4909832&width=600&height=600&format=image%2Fpng

        Tested:
        http://localhost:8080/geoserver/wms?REQUEST=GetMap&service=WMS&VERSION=1.1.1&layers=southwestgaslv:southwestgaslv_gasvalve&style=southwestgaslv:southwestgaslv_annual2023_gasvalve&srs=EPSG%3A4326&bbox=-115.17205855899132,36.01737758450414,-115.1720364523505,36.01737815996513&FORMAT=image/png&WIDTH=20&HEIGHT=20
        # 
        http://localhost:8080/geoserver/wms?REQUEST=GetMap
        &service=WMS
        &VERSION=1.1.1
        &layers=southwestgaslv:MainLines,southwestgaslv:Risers
        &style=southwestgaslv:MainLines,southwestgaslv:Risers
        &srs=EPSG%3A4326
        &bbox=-115.17205855899132,36.01737758450414,-115.1720364523505,36.01737815996513
        &FORMAT=image/png
        &WIDTH=767&HEIGHT=490
        # for Mainline - get the entire region bounds
        srs=EPSG%3A4326&
        minx -115.17205855899132,
        miny 36.01737758450414,
        maxx -115.1720364523505,
        maxy 36.01737815996513
        -124.736342,24.521208,-66.945392,49.382808  Nevada

        TODO - see if this is any help for legend formating
        format=application/openlayers&
        format_options=layout:legend&legend_options=countMatched:true;fontAntiAliasing:true
        """
        pass


    def shapefilestore_layer(self):
        """The create_shp datastore function will be useful for uploading the shapefile and 
        publishing the shapefile as a layer. This function will upload the data to the geoserver 
        data_dir in h2 database structure and publish it as a layer. 
        The layer name will be same as the shapefile name.

        """
        self.create_shp_datastore(path=r'path/to/zipped/shp/file.zip', store_name='store', workspace='demo')

    
    def create_geopkg_datastore(self, store_name, geopkg, workspace, overwrite):
        #
        # Example:
        # <dataStore>
            # <id>DataStoreInfoImpl--c65d3ad:1866670907c:-7fc9</id>
            # <name>Overlay</name>
            # <type>GeoPackage</type>
            # <enabled>true</enabled>
            # <workspace>
            #     <id>WorkspaceInfoImpl--c65d3ad:1866670907c:-7fe5</id>
            # </workspace>
            # <connectionParameters>
            #     <entry key="Batch insert size">1</entry>
            #     <entry key="database">file:data/southwestgaslv/Overlay.gpkg</entry>
            #     <entry key="fetch size">1000</entry>
            #     <entry key="Expose primary keys">false</entry>
            #     <entry key="read_only">true</entry>
            #     <entry key="dbtype">geopkg</entry>
            #     <entry key="namespace">http://southwestgaslv</entry>
            # </connectionParameters>
            # <__default>false</__default>
            # <dateCreated>2023-02-19 17:49:24.835 UTC</dateCreated>
            # <disableOnConnFailure>false</disableOnConnFailure>
        # </dataStore>
        #
        # assigning our own file datastore instead of geoserver data dir, overiding inside the code
        database = os.environ["OUTPUT_PATH"]     # os.environ["GEOSERVER_DATA_DIR"]
        database += "/" + geopkg
        slug = os.getenv("slug")
        try:
  
            data_url = """<entry key="fetch size">1000</entry>
            <entry key="Expose primary keys">false</entry>
            <entry key="Batch insert size">1</entry>
            <entry key="database">file:{0}</entry>
            <entry key="read_only">true</entry>
            <entry key="dbtype">geopkg</entry>""".format(database)
            
            data = """<dataStore><name>{0}</name><type>GeoPackage</type>
            <connectionParameters>{1}</connectionParameters></dataStore>""".format(store_name, data_url)
            
            headers = {"content-type": "text/xml"}

            if overwrite:
                url = "{}/rest/workspaces/{}/datastores/{}".format(
                    self.service_url, workspace, store_name
                )
                r = self._requests("put", url, data=data, headers=headers)

            else:
                url = "{}/rest/workspaces/{}/datastores".format(
                    self.service_url, workspace
                )
                
                r = requests.post(
                    url, data, auth=(self.username, self.password), headers=headers
                )
                              
            if r.status_code in [200, 201]:
                msg = "          Data store created successfully"
                logger.info(msg)
                return msg
            elif r.content.decode().find("already exists"):
                # msg = str(r.status_code) + " "
                msg = "          " + r.content.decode()
                logger.info(msg)
                return msg
            else:
                msg = "TODO - Developer to check on this error in datastore_layers\n\n"
                logger.error(msg)
                return msg
                
        except Exception as e:
            msg = "          " + str(e)
            logger.error(str(e))
            return msg


    def publish_geopkg_layer(self, store_name, layer, workspace, title, xyXY):
        #
        # layer.xml example:
        # <layer>
            # <name>ServiceLines</name>
            # <id>LayerInfoImpl--c65d3ad:1866670907c:-7fbf</id>
            # <type>VECTOR</type>
            # <defaultStyle>
            #     <id>StyleInfoImpl-37b18cc6:14d5d036d48:-8000</id>
            # </defaultStyle>
            # <resource class="featureType">
            #     <id>FeatureTypeInfoImpl--c65d3ad:1866670907c:-7fc0</id>
            # </resource>
            # <attribution>
            #     <logoWidth>0</logoWidth>
            #     <logoHeight>0</logoHeight>
            # </attribution>
            # <dateCreated>2023-02-19 17:49:25.74 UTC</dateCreated>
        # </layer>
        #
        # featuretype.xml example:
        # <featureType>
            # <id>FeatureTypeInfoImpl--c65d3ad:1866670907c:-7fc0</id>
            # <name>ServiceLines</name>
            # <nativeName>ServiceLines</nativeName>
            # <namespace>
            #     <id>NamespaceInfoImpl--c65d3ad:1866670907c:-7fe4</id>
            # </namespace>
            # <title>ServiceLines</title>
            # <keywords>
            #     <string>features</string>
            #     <string>ServiceLines</string>
            # </keywords>
            # <srs>EPSG:4326</srs>
            # <nativeBoundingBox>
            #     <minx>-115.3925316479814</minx>
            #     <maxx>-114.6129539731144</maxx>
            #     <miny>35.11984555265311</miny>
            #     <maxy>36.0673541167677</maxy>
            #     <crs>EPSG:4326</crs>
            # </nativeBoundingBox>
            # <latLonBoundingBox>
            #     <minx>-115.3925316479814</minx>
            #     <maxx>-114.6129539731144</maxx>
            #     <miny>35.11984555265311</miny>
            #     <maxy>36.0673541167677</maxy>
            #     <crs>EPSG:4326</crs>
            # </latLonBoundingBox>
            # <projectionPolicy>FORCE_DECLARED</projectionPolicy>
            # <enabled>true</enabled>
            # <store class="dataStore">
            #     <id>DataStoreInfoImpl--c65d3ad:1866670907c:-7fc9</id>
            # </store>
            # <serviceConfiguration>false</serviceConfiguration>
            # <maxFeatures>0</maxFeatures>
            # <numDecimals>0</numDecimals>
            # <padWithZeros>false</padWithZeros>
            # <forcedDecimal>false</forcedDecimal>
            # <overridingServiceSRS>false</overridingServiceSRS>
            # <skipNumberMatched>false</skipNumberMatched>
            # <circularArcPresent>false</circularArcPresent>
        # </featureType>
        #
        try:
            if workspace is None:
                workspace = "default"
            if title is None:
                title = layer

            url = "{}/rest/workspaces/{}/datastores/{}/featuretypes/".format(
                self.service_url, workspace, store_name
            )

            minx, miny, maxx, maxy = xyXY
          
            layer_xml = f"""<featureType>
                <name>{layer}</name>
                <title>{layer}</title>
                <nativeName>{layer}</nativeName>
                <keywords>
                    <string>features</string>
                    <string>{layer}</string>
                </keywords>
                <srs>EPSG:4326</srs>
                <nativeBoundingBox>
                    <minx>{minx}</minx>
                    <maxx>{maxx}</maxx>
                    <miny>{miny}</miny>
                    <maxy>{maxy}</maxy>
                    <crs>EPSG:4326</crs>
                </nativeBoundingBox>
                <latLonBoundingBox>
                    <minx>{minx}</minx>
                    <maxx>{maxx}</maxx>
                    <miny>{miny}</miny>
                    <maxy>{maxy}</maxy>
                    <crs>EPSG:4326</crs>
                </latLonBoundingBox>
                <projectionPolicy>FORCE_DECLARED</projectionPolicy>
                <enabled>true</enabled>
                <store class="dataStore"></store>
                <serviceConfiguration>false</serviceConfiguration>
                <maxFeatures>0</maxFeatures>
                <numDecimals>0</numDecimals>
                <padWithZeros>false</padWithZeros>
                <forcedDecimal>false</forcedDecimal>
                <overridingServiceSRS>false</overridingServiceSRS>
                <skipNumberMatched>false</skipNumberMatched>
                <circularArcPresent>false</circularArcPresent>
                </featureType>"""
           
            headers = {"content-type": "text/xml"}

            r = requests.post(
                url,
                data=layer_xml,
                auth=(self.username, self.password),
                headers=headers,
            )
            if r.status_code == 201:
                return r.status_code
            else:
                raise LSAGeoserverException(r.status_code, r.content)
        except Exception as e:
            raise Exception(e)


    # Note: This needs access to slugobj! Not used. Calling per layer from outside
    def publish_geopkg_layers(self, store, geopkg, workspace):
        # publish data
        slug = os.getenv("slug")

        layers = fiona.listlayers(os.path.join(os.getenv("OUTPUT_PATH", geopkg)))
        for layer in layers:
            try:
                # store_name, layer, workspace, title, srid
                self.publish_geopkg_layer(store, layer, workspace, layer)
                msg = f"          Published {layer}\n"
                logger.info(msg)
                return msg

            except Exception as e:
                if "already exists" in str(e):
                    msg = f"          Layer {layer} already exists in store {store}, workspace {workspace}\n"
                    return msg
                else:
                    logger.info(str(e))
                    msg = "          " + str(e) + "\n"
                    return msg


    def featurestore_postgis(self, storename, wrksp, overwrite, schema='public'):
        """Create a feature store storename, connecting the PostGIS with geoserver. 
        It is only useful for vector data. 
        
        Args:
            storename (string): any name for the store. Better be based on some criteria.
                                the smallest unit of a feature store is a table name in 
                                which the store name should match the table name.
                                currently, we are using a survey name as the feature store
                                where the number of layers per survey may vary.
            wrksp (string): name of the workspace where used as root directory for organizing
                            all the data belong to each customer, in this case, slug.
            overwrite (boolean): True to overwrite an existing feature store, False to create
                                 a new feature store
            schema (string): postgres database schema, in this case each schema is unique per
                             client.   
        """
        host = os.getenv("POSTGIS_HOST", "localhost")
        db = os.getenv("HEATH_LSA_DB", "heath_lsa")
        user = os.getenv("HEATH_LS_ADMIN", "heath_lsa_admin")
        passwrd = os.getenv("HEATH_LS_ADMIN_PASS", "heath_lsa_pass")
        
        try:
            msg = super().create_featurestore(store_name=storename, 
                                        workspace=wrksp, 
                                        db=db, host=host, 
                                        schema=schema,
                                        pg_user=user, pg_password=passwrd,
                                        overwrite=overwrite, expose_primary_keys="false",
                                        description="Unique survey map name",
                                        create_database="false"
                                        )
            msg += f"          {msg}\n"
            return msg
            
        except Exception as e:
            if str(e).find("already exists"):
                msg = f"          Feature store '{storename}' already exists in Workspace '{wrksp}'\n"  
                return msg 
            else:
                msg = f"          {str(e)}\n"
                return msg
    


    def featurestore_layer_postgis(self, wrksp, storename, tablename):  

        try:
            msg = super().publish_featurestore(workspace=wrksp, store_name=storename, pg_table=tablename, 
                                           title=tablename)
            if msg == 201 or msg == 202:
                return f"          Published layer {tablename}\n" 
        except Exception as e:
            if str(e).find("already exists"):
                msg = f"          Layer {tablename} already exists in '{storename}'\n"
                return msg
            else:
                msg = f"          {str(e)}\n"
                return msg
    
                    
    def layer_sld(self, sldfile, wrksp, geoserverlayer, stylename):
        # For uploading SLD file and connect it with layer
        """Given a geoserver compliance SLD file for a layer
        creates and connects the SLD to the named layer.
        Args:
            sldfile (sld xml): SLD file 
            wrksp (string): The name of the existing workspace where the style sheet will resides
            layer (string): The name of a feature class, layer, that already is published
            stylename (string): The name of the style sheet, currently same as layer name 
        """
        msg = ""
        try:
            stat = super().upload_style(path=sldfile, workspace=wrksp)
            msg = f"                Style named {stylename} created - {str(stat)}\n"
            
        except Exception as e:
            if "already exists" in str(e):
                msg = f"               Style named {stylename} already exists in workspace {wrksp}\n"        
            else:
                msg = "               " + str(e) + "\n"
        try:
            # http://localhost:8080/geoserver/wms?REQUEST=GetLegendGraphic&VERSION=1.3.0&FORMAT=image/png&WIDTH=20&HEIGHT=20&LAYER=MainLines
            # <img src='http://.....?request=getLegendGraphic'/>
            stat = super().publish_style(layer_name=geoserverlayer, style_name=stylename, workspace=wrksp)
            msg = f"               Published style {stylename} - {str(stat)}\n"
           
        except Exception as e:
            msg = "               " + str(e) + "\n"

        return msg
        


    def dynamic_raster_sld(self, raster_file, style_file):
        # For creating the style file for raster data dynamically and connect it with layer
        self.geo.create_coveragestyle(raster_path=r'path\to\raster\file.tiff', style_name='style_1', 
                                      workspace='demo', color_ramp='RdYiGn')
        self.geo.publish_style(layer_name='geoserver_layer_name', style_name='raster_file_name', workspace='demo')


    def delete_workspace(self, wrksp):
        # delete workspace
        super().delete_workspace(workspace=wrksp)


    def delete_layer(self, layer, wrksp):
        # delete layer
        msg = ""
        
        try:
            msg = super().delete_layer(layer_name=layer, workspace=wrksp)
        except Exception as e:
            logger.info(str(e))
            msg = "--- " + str(e) + "\n"
        return msg


    def delete_stylefile(self, style_name, wrksp):
        # delete style file
        slug = os.getenv("slug")
        msg ="Success\n"
        try:
            msg = super().delete_style(style_name=style_name, workspace=wrksp)
        except Exception as e:
            logger.info(str(e))
            msg = str(e) + "\n"
            
        return msg

    #
    # The OGC Web Map Service (WMS) specification defines an HTTP interface for 
    # requesting georeferenced map images from a server. 
    # GeoServer supports WMS 1.1.1, the most widely used version of WMS, 
    # as well as WMS 1.3.0.
    #
    def wms_getcapabilities(self, namespc, rootlayer="true"):
        """Retrieves metadata about the service, including supported operations and parameters, 
        and a list of the available layers. 
        http://localhost:8080/geoserver/wms?service=wms&version=1.1.1&request=GetCapabilities&namespace=southwestgaslv&filename=feature.json
        http://127.0.0.1:8080/geoserver/wms?service=wms&version=1.1.1&request=GetCapabilities&format=text/xml&namespace=southwestgaslv&rootLayer=true
        """

        service = "wms"                 # Service parameter tells the WMS server that a WMS request is forthcoming
        version = "1.3.0"               # Refers to which version of WMS is being requested. Format text/xml only 
                                        # accepts 1.1.1 version
        srequest = "GetCapabilities"    # The request parameter specifies the GetCapabilities operation
        namespace = namespc             # Limits response to layers in a given namespace
        format = "text/xml"             # Request the capabilities document in a certain format

        filename = os.path.join(os.getenv("OUTPUT_PATH"), namespc+"_features.xml")
                                        # This file is for system to get info we need such as bbox 

        rootLayer = rootlayer           # Flag to enable/disable the standard Root top level Layer element. 
                                        # Values are true or false. When false, the Root element will be 
                                        # included only if there are multiple top level layers, if there is 
                                        # only one, it will be the root layer itself. When specified, will 
                                        # override the global WMS setting or layer / group setting for the 
                                        # same behaviour.
        try:
            # payload = {"recurse": "true"}
            url = "{}/wms?service={}&version={}&request={}&namespace={}&rootLayer={}&filename={}".format(
                self.service_url, service, version, srequest, namespace, rootLayer, filename
            )
            print(f"wms_getcapabilities: {url}")

            r = requests.get(
                url, auth=(self.username, self.password)
            )
            if r.status_code == 200:
                # parses xml to dict
                return filename, parse(r.content)
            else:
                raise LSAGeoserverException(r.status_code, r.content)

        except Exception as e:
            raise Exception(e)
 

    def wms_getmap(self):
        """Retrieves a map image for a specified area and content
        """
        pass
    
    def wms_getfeatureInfo (self):
        """Retrieves the underlying data, including geometry and attribute values, for a pixel location on a map"""
        pass

    def wms_describelayer (self):
        """Indicates the WFS or WCS to retrieve additional information about the layer"""
        pass

    def wms_getlegendgraphic (self):
       """Retrieves a generated legend for a map"""
       pass

def get_color(i):
    colors = {'green': '#008000', 'purple': '#800080', 'red': '#FF0000',
              'blue': '#0000FF', 'gray': '#808080', 'cyan': '#00FFFF'}
    if i >= len(colors):
        i = 0
    keys = list(colors.keys())
    return colors.get(keys[i])


class GeoserverStyler(Geoserver):
    #
    # Using expressions in parameter values:
    # Many SLD parameters allow their values to be of mixed type. This means that the element content can be:
    # - a constant value expressed as a string
    # - a filter expression
    # - any combination of strings and filter expressions.
    # Using expressions in parameter values provides the ability to determine styling dynamically on a per-feature basis, 
    # by computing parameter values from feature properties. Using computed parameters is an alternative to using rules 
    # in some situations, and may provide a more compact SLD document.
    # GeoServer also supports using substitution variables provided in WMS requests. 
    # This is described in Variable substitution in SLD.
    #
    def __init__(self, 
        service_url =  os.getenv("GEOSERVER_URL", "http://127.0.0.1:8080/geoserver"),
        username = os.getenv("GEOSERVER_USERNAME", "admin"),
        password = os.getenv("GEOSERVER_PASSWORD", "geoserver")):

        super().__init__(service_url, username,  password)

    

    def dynamic_styler(self, sld_filename, layer, geom, anno, i):
       
        if os.path.exists(sld_filename):
            os.remove(sld_filename) 
        
        with open(sld_filename, 'w') as f: 
            lines = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
            lines += '  <StyledLayerDescriptor version="1.0.0"\n'
            lines += '  xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd"\n'
            lines += '  xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc"\n'
            lines += '  xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
            #
            lines +='  <NamedLayer>\n'
            lines +=f'    <Name>{layer}</Name>\n'
            lines +='    <UserStyle>\n'
            lines +=f'      <Title>{layer}</Title>\n'
            lines +='      <IsDefault>1</IsDefault>\n'
            lines +='      <FeatureTypeStyle>\n'
            lines +='        <Rule>\n'
            if geom.upper() == "LINE" or geom.upper() == "POLYLINE" or geom.upper() == "MULTLINE":
                # stroke_color="#0000FF" 
                line = self.line_symbolizer(stroke_color=get_color(i))
                lines += line
            elif geom.upper() == "POINT" or geom.upper() == "MULTPOINT":
                # marker_shape='square',fill_color="#FF0000"
                line = self.point_symbolizer(fill_color=get_color(i))
                lines += line
            elif geom.upper() == "POLYGON" or geom.upper() == "MULTPOLYGON":
                # stroke_color="#000000"
                line = self.polygon_symbolizer(stroke_color=get_color(i))
                lines += line
            if anno:
                line = self.text_symbolizer(anno)
                lines += line
                lines +='        </Rule>\n'
            
            lines +='      </FeatureTypeStyle>\n'  
            lines +='    </UserStyle>\n'
            lines +='  </NamedLayer>\n'
            lines +='</StyledLayerDescriptor>\n'
            f.write(lines)

            msg = f"          Created style file {sld_filename}\n"
            return msg
         

    def point_symbolizer(self, marker_shape='square',fill_color="#FF0000", marker_size=8):
        #
        # A PointSymbolizer styles features as points. 
        # Points are depicted as graphic symbols at a single location on the map.
        #
        
        lines = "          <PointSymbolizer>\n"
        lines +="            <Graphic>\n"
        lines +="              <Mark>\n"
        lines +="                <WellKnownName>\n"
        lines +=f"                 {marker_shape}\n"
        lines +="                </WellKnownName>\n"
        if fill_color is not None:
            lines +="                <Fill>\n"
            lines +='                  <CssParameter name="fill">\n'
            lines +=f"                    {fill_color}\n"
            lines +="                  </CssParameter>\n"
            lines +="                </Fill>\n"  
        lines +="              </Mark>\n"
        lines +="              <Size>\n"
        lines +=f"                {marker_size}\n"
        lines +="              </Size>\n"
        lines +="            </Graphic>\n"
        lines +="          </PointSymbolizer>\n"

        return lines


    def line_symbolizer(self, stroke_color="#0000FF", stroke_width=3, dash_array=[5,2]):
        
        lines = "          <LineSymbolizer>\n"
        lines +="             <Stroke>\n"
        lines +=f'              <CssParameter name="stroke">{stroke_color}</CssParameter>\n'
        lines +=f'              <CssParameter name="stroke-width">{stroke_width}</CssParameter>\n'
        lines +=f'              <CssParameter name="stroke-dasharray">{dash_array[0]} {dash_array[1]}</CssParameter>\n'
        lines +="             </Stroke>\n"
        lines +="          </LineSymbolizer>\n"
        return lines


    def line_symbolizer_with_offset(self, stroke_color="#000000", stroke_width=2, offset=3,
                                    color_offset="00000FF", width_offset=3, offset_array=[5,2]):
        # line symbolizer with offsetting lines
        lines +="<LineSymbolizer>\n"
        lines +="    <Stroke>\n"
        lines += f'       <CssParameter name="stroke">{stroke_color}</CssParameter>\n'
        lines +='f        <CssParameter name="stroke-width">{stroke_width}</CssParameter>\n'
        lines +="    </Stroke>\n"
        lines +="</LineSymbolizer>\n"
        lines +="<LineSymbolizer>\n"
        lines +="    <Stroke>\n"
        lines +=f'        <CssParameter name="stroke">{color_offset}</CssParameter>\n'
        lines +=f'        <CssParameter name="stroke-width">{width_offset}</CssParameter>\n'
        lines +=f'        <CssParameter name="stroke-dasharray">{offset_array[0]} {offset_array[1]}</CssParameter>\n'
        lines +="    </Stroke>\n"
        lines +=f'    <PerpendicularOffset>{offset}</PerpendicularOffset>\n'
        lines +="</LineSymbolizer>\n"
        return lines


    def polygon_symbolizer(self, stroke_color="#000000"):
        lines = "          <PolygonSymbolizer>\n"
        lines +="             <Fill>\n"
        lines +=f'                <CssParameter name="fill">{stroke_color}</CssParameter>\n'
        lines +="             </Fill>\n"
        lines +="          </PolygonSymbolizer>\n"
        return lines
            
             
    def polygon_symbolizer_with_offset(self, stroke_color="#000000", stroke_width=2, offset=-2,
                                             offset_color="#AAAAAA", offset_width=3):
        # polygon symbolizer with offset
        lines = "<PolygonSymbolizer>\n"
        lines +="    <Stroke>\n"
        lines +=f'        <CssParameter name="stroke">{stroke_color}</CssParameter>\n'
        lines +=f'        <CssParameter name="stroke-width">{stroke_width}</CssParameter>\n'
        lines +="    </Stroke>\n"
        lines +="</PolygonSymbolizer>\n"
        lines +="<LineSymbolizer>\n"
        lines +="    <Stroke>\n"
        lines +=f'        <CssParameter name="stroke">{offset_color}</CssParameter>\n'
        lines +=f'        <CssParameter name="stroke-width">{offset_width}</CssParameter>\n'
        lines +="    </Stroke>\n"
        lines +=f'    <PerpendicularOffset>{offset}</PerpendicularOffset>\n'
        lines +="</LineSymbolizer>\n"
        return lines


    def text_symbolizer(self, props, ffamily="Arial", fsize=8, fstyle="normal", fweight="bold", 
                        anchx=0.5, anchy=0.5, disx=0, disy=25, rotate=-45, fill_color="#990099"):
        #  
        # A TextSymbolizer styles features as text labels. 
        # Text labels are positioned either at points or along linear paths derived from the geometry being labelled.
        # 
        lines = "          <TextSymbolizer>\n"
        for prop in props:
            lines +="              <Label>\n"
            lines +=f"                  <ogc:PropertyName>{prop}</ogc:PropertyName>\n"
            lines +="              </Label>\n"

        lines +="              <Font>\n"
        lines +=f'                  <CssParameter name="font-family">{ffamily}</CssParameter>\n'
        lines +='                  <CssParameter name="font-size">\n'
        # lines +="            <ogc:Function name="Categorize">\n"
        # lines +="                <!-- Value to transform -->\n"
        # lines +=f'                <ogc:Function name={env}>\n'
        # lines +=f'                  <ogc:Literal>{wms_scale_denominator}</ogc:Literal>\n'
        # lines +="               </ogc:Function>\n"           
        # lines +="            </ogc:Function>\n"
        lines +=f"                    {fsize}\n"
        lines +="                  </CssParameter>\n"
        lines +=f'                  <CssParameter name="font-style">{fstyle}</CssParameter>\n'
        lines +=f'                  <CssParameter name="font-weight">{fweight}</CssParameter>\n'
        lines +="              </Font>\n"
        lines +="              <LabelPlacement>\n"
        lines +="                  <PointPlacement>\n"
        lines +="                      <AnchorPoint>\n"
        lines +=f"                          <AnchorPointX>{anchx}</AnchorPointX>\n"
        lines +=f"                          <AnchorPointY>{anchy}</AnchorPointY>\n"
        lines +="                      </AnchorPoint>\n"
        lines +="                      <Displacement>\n"
        lines +=f"                          <DisplacementX>{disx}</DisplacementX>\n"
        lines +=f"                          <DisplacementY>{disy}</DisplacementY>\n"
        lines +="                      </Displacement>\n"
        lines +="                      <Rotation>\n"
        lines +=f"                          {rotate}\n"
        lines +="                      </Rotation>\n"
        lines +="                  </PointPlacement>\n"
        lines +="              </LabelPlacement>\n"
        lines +="              <Fill>\n"
        lines +=f'                  <CssParameter name="fill">{fill_color}</CssParameter>\n'
        lines +="              </Fill>\n"
        lines +="          </TextSymbolizer>\n"
        return lines

#############################################################
class CrawlerSingleton(object):
	def __new__(cls):
		""" creates a singleton object, if it is not created,
		or else returns the previous singleton object"""
		if not hasattr(cls, 'instance'):
			cls.instance = super(CrawlerSingleton, cls).__new__(cls)
		return cls.instance


##################### functions #######################

def copy_to_datadir(path, wrksp):
    # copyies the geopkg with its layers into data directory of geoserver
    # geoserver_home = os.getenv("GEOSERVER_HOME") FYI
    geoserver_data_dir = os.getenv("GEOSERVER_DATA_DIR")
    
    dest_dir = os.path.join(geoserver_data_dir, wrksp)
    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)
    # shapefiles names
    layers = fiona.listlayers(path)
    # path to input shapefiles
    source_dir = os.path.dirname(path)
    
    for layer in layers:
        target_file = os.path.join(source_dir, layer)
        for file in glob.glob(f"{target_file}.*"):
            shutil.copyfile(file, dest_dir)
       

def upload( geopkg, url):
    test_res = requests.post(url, geopkg)
    if test_res.ok:
        print(" File uploaded successfully ! ")
        print(test_res.text)
    else:
        print(" Please Upload again ! ")


def navigate_site(max_links = 5):
	""" navigate the website using BFS algorithm, find links and
		arrange them for downloading images """

	# singleton instance
	parser_crawlersingleton = CrawlerSingleton()
	
	# During the initial stage, url_queue has the main_url.
	# Upon parsing the main_url page, new links that belong to the
	# same website is added to the url_queue until
	# it equals to max _links.
	while parser_crawlersingleton.url_queue:

		# checks whether it reached the max. link
		if len(parser_crawlersingleton.visited_url) == max_links:
			return

		# pop the url from the queue
		url = parser_crawlersingleton.url_queue.pop()

		# connect to the web page
		http = httplib2.Http()
		try:
			status, response = http.request(url)
		except Exception:
			continue
		
		# add the link to download the images
		parser_crawlersingleton.visited_url.add(url)

		# crawl the web page and fetch the links within
		# the main page
		bs = BeautifulSoup(response, "html.parser")

		for link in BeautifulSoup.findAll(bs, 'a'):
			link_url = link.get('href')
			if not link_url:
				continue

			# parse the fetched link
			parsed = urlparse(link_url)
			
			# skip the link, if it leads to an external page
			if parsed.netloc and parsed.netloc != parsed_url.netloc:
				continue

			scheme = parsed_url.scheme
			netloc = parsed.netloc or parsed_url.netloc
			path = parsed.path
			
			# construct a full url
			link_url = scheme +'://' +netloc + path

			
			# skip, if the link is already added
			if link_url in parser_crawlersingleton.visited_url:
				continue
			
			# Add the new link fetched,
			# so that the while loop continues with next iteration.
			parser_crawlersingleton.url_queue = [link_url] +\
												parser_crawlersingleton.url_queue
			
class ParallelDownloader(threading.Thread):
	""" Download the images parallelly """
	def __init__(self, thread_id, name, counter):
		threading.Thread.__init__(self)
		self.name = name

	def run(self):
		print('Starting thread', self.name)
		# function to download the images
		download_images(self.name)
		print('Finished thread', self.name)


def download_images(thread_name):
	# singleton instance
	singleton = CrawlerSingleton()
	# visited_url has a set of URLs.
	# Here we will fetch each URL and
	# download the images in it.
	while singleton.visited_url:
		# pop the url to download the images
		url = singleton.visited_url.pop()

		http = httplib2.Http()
		print(thread_name, 'Downloading images from', url)

		try:
			status, response = http.request(url)
		except Exception:
			continue

		# parse the web page to find all images
		bs = BeautifulSoup(response, "html.parser")

		# Find all <img> tags
		images = BeautifulSoup.findAll(bs, 'img')

		for image in images:
			src = image.get('src')
			src = urljoin(url, src)

			basename = os.path.basename(src)
			print('basename:', basename)

			if basename != '':
				if src not in singleton.image_downloaded:
					singleton.image_downloaded.add(src)
					print('Downloading', src)
					# Download the images to local system
					urllib.request.urlretrieve(src, os.path.join('images', basename))
					print(thread_name, 'finished downloading images from', url)

def start():
    # instatiate
    msg = "Starting GeoserverEngine\n"
    logger.info(msg)
    global geoe
    geoe = GeoserverRestAPI()

    return geoe


def start_crawler():
	# singleton instance
	crwSingltn = CrawlerSingleton()

	# adding the url to the queue for parsing
	crwSingltn.url_queue = [os]

	# initializing a set to store all visited URLs
	# for downloading images.
	crwSingltn.visited_url = set()

	# initializing a set to store path of the downloaded images
	crwSingltn.image_downloaded = set()
	
	# invoking the method to crawl the website
	navigate_site()

	## create images directory if not exists
	if not os.path.exists('images'):
		os.makedirs('images')

	thread1 = ParallelDownloader(1, "Thread-1", 1)
	thread2 = ParallelDownloader(2, "Thread-2", 2)

	# Start new threads
	thread1.start()
	thread2.start()

	
if __name__ == "__main__":
    # main_url = ("https://www.geeksforgeeks.org/")
    # parsed_url = urlparse(main_url)
    # start_crawler()
    #
    # testing getcapabilities
    #
    os.environ["OUTPUT_DIR"] = "D:\PROJECTS\heath_lsa\OUTPUT"
    print(os.environ)
    geoe = GeoserverRestAPI()
    geoe.wms_getcapabilities("southwestgaslv")





