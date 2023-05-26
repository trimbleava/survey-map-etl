// First, enable JSONP in GeoServer.
// Add to this file: /tomcat/webapps/geoserver/WEB-INF/web.xml
// <context-param>
//    <param-name>ENABLE_JSONP</param-name>
//    <param-value>true</param-value>
// </context-param>
// and restart the service. Then, in your json request use format=text/javascript

// http://www.yourgeoserver.com/geoserver/rest/workspaces/myws/featuretypes.json

// Then form your data requests like this:
// var owsrootUrl = 'https://<GEOSERVER URL - CHANGEME>/geoserver/ows';

// var defaultParameters = {
//     service : 'WFS',
//     version : '2.0',
//     request : 'GetFeature',
//     typeName : '<WORKSPACE:LAYERNAME - CHANGEME>',
//     outputFormat : 'text/javascript',
//     format_options : 'callback:getJson',
//     SrsName : 'EPSG:4326'
// };

// var parameters = L.Util.extend(defaultParameters);
// var URL = owsrootUrl + L.Util.getParamString(parameters);

// var WFSLayer = null;
// var ajax = $.ajax({
//     url : URL,
//     dataType : 'jsonp',
//     jsonpCallback : 'getJson',
//     success : function (response) {
//         WFSLayer = L.geoJson(response, {
//             style: function (feature) {
//                 return {
//                     stroke: false,
//                     fillColor: 'FFFFFF',
//                     fillOpacity: 0
//                 };
//             },
//             onEachFeature: function (feature, layer) {
//                 popupOptions = {maxWidth: 200};
//                 layer.bindPopup("Popup text, access attributes with feature.properties.ATTRIBUTE_NAME"
//                     ,popupOptions);
//             }
//         }).addTo(map);
//     }
// });


//
// Operational layers - 
//
function load_wfs(geoe_url, slug, lyr_name) {

    // if (map.getZoom() > start_at_zoom) {

    var wfsUrl = geoe_url+'/wfs';

    var defaultParameters = {
        service: 'WFS',
        version: '2.0.0',
        request: 'GetFeature',
        typeName: slug+":"+lyr_name,
        maxFeatures: 3000,
        outputFormat: 'text/javascript',
        format_options: 'callback: getJson',
        srsName: 'EPSG:4326'
    };

    var customParams = {
        // bbox: map.getBounds().toBBoxString()
    };
        
    var parameters = L.Util.extend(defaultParameters, customParams);
    console.log(wfsUrl + L.Util.getParamString(parameters));

    $.ajax({
        // jsonp: false,  why??
        url: wfsUrl + L.Util.getParamString(parameters),
        dataType: 'jsonp',
        jsonpCallback: 'getJson',
        success: loadGeoJson
    });
    
    // } else {
    //     alert("please zoom in to see the polygons!");
    //    featureLayer.clearLayers();
    // }
}

function onEachFeature(feature, layer) {
    props = feature.properties,
        attrs = Object.keys(props),
        attribute, value;

    for (var i = 0; i < attrs.length; i += 1) {
        attribute = attrs[i];
        value = props[attribute];
        // use the value to do something...
    }
    if (feature.properties && feature.properties.geometry) {
        layer.bindPopup(feature.properties.geometry);
    }
}

function loadGeoJson(data) {
    console.log(data);
    var len = data.features.length;
    console.log(len);
    // featureLayer.clearLayers();

    featureLayer.addData(data);
};

var myStyle = `
<?xml version="1.0" encoding="ISO-8859-1"?>
<StyledLayerDescriptor version="1.0.0"
xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd"
xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc"
xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<NamedLayer>
<Name>southwestgaslv:southwestgaslv_controllablefitting</Name>
<UserStyle>
<Title>southwestgaslv:southwestgaslv_controllablefitting</Title>
<IsDefault>1</IsDefault>
<FeatureTypeStyle>
<Rule>
  <PointSymbolizer>
    <Graphic>
      <Mark>
        <WellKnownName>
         square
        </WellKnownName>
        <Fill>
          <CssParameter name="fill">
            #008000
          </CssParameter>
        </Fill>
      </Mark>
      <Size>
        8
      </Size>
    </Graphic>
  </PointSymbolizer>
  <TextSymbolizer>
      <Label>
          <ogc:PropertyName>SWGUID</ogc:PropertyName>
      </Label>
      <Font>
          <CssParameter name="font-family">Arial</CssParameter>
          <CssParameter name="font-size">
            8
          </CssParameter>
          <CssParameter name="font-style">normal</CssParameter>
          <CssParameter name="font-weight">bold</CssParameter>
      </Font>
      <LabelPlacement>
          <PointPlacement>
              <AnchorPoint>
                  <AnchorPointX>0.5</AnchorPointX>
                  <AnchorPointY>0.5</AnchorPointY>
              </AnchorPoint>
              <Displacement>
                  <DisplacementX>0</DisplacementX>
                  <DisplacementY>25</DisplacementY>
              </Displacement>
              <Rotation>
                  -45
              </Rotation>
          </PointPlacement>
      </LabelPlacement>
      <Fill>
          <CssParameter name="fill">#990099</CssParameter>
      </Fill>
  </TextSymbolizer>
</Rule>
</FeatureTypeStyle>
</UserStyle>
</NamedLayer>
</StyledLayerDescriptor>`;

var geojsonPointOptions = {
    radius: 8,
    fillColor: "#ff7800",
    color: "#000",
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
};

var geojsonLineOptions = {
    radius: 8,
    fillColor: "#ff7800",
    color: "#000",
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
};

var geojsonPolyOptions = {
    radius: 8,
    fillColor: "#ff7800",
    color: "#000",
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
};

function parseXml(xmlContent) {
    console.log(xmlContent);
    var xmlDoc = $.parseXML(xmlContent);
    var shape = $(xmlDoc).find("sld:StyledLayerDescriptor");
    console.log($(xmlDoc).find("sld:Title").text());

    // var x = "<?xml version='1.0' encoding='utf-8'?><export> <Article URL='test'>   <DisplayName>test</DisplayName> <Summary>test</Summary><ThumbNail ID='test' URL='test' /></Article></export>";
    // var xmlDoc = $.parseXML(x);
    // $(xmlDoc).find('Article').each(function() {
    //     console.log($(this).attr('URL'));
    //     console.log($(this).find('DisplayName').text());
    //     console.log($(this).find('Summary').text());
    //     console.log($(this).find('ThumbNail').attr('URL'));
    // });
}


function parseGeoSLD(geoe_url, slug, sldfile, lyr_name, geom, anno) {
    //
    // http://localhost:8080/geoserver/rest/workspaces/southwestgaslv/styles/southwestgaslv_annual2023_controllablefitting.sld
    //
    // var sld = 'southwestgaslv/styles/southwestgaslv_annual2023_controllablefitting.sld';
    var sld_url = geoe_url+'/rest/workspaces/'+slug+'/styles/';
    $.ajax({
        type: "GET",
        url: sld_url+sldfile,
        dataType: "xml",
        async: false,
        headers: {
            'Authorization': "Basic " + btoa('admin' + ":" + 'geoserver')
        },
        success: parseXml
    });
};
            
function addOplayersToMap(geoe_url, op_style, slug, map) {

    // http://localhost:8080/geoserver/wfs?service=wfs&request=GetFeature&version=1.1.0
    // &typeName=southwestgaslv:southwestgaslv_regulatorstation
    // http://localhost:8080/geoserver/southwestgaslv/wms?service=WMS&version=1.1.0
    // &request=GetMap&layers=southwestgaslv%3Asouthwestgaslv_controllablefitting
    // &bbox=-115.18363952636719%2C35.9561767578125%2C-114.83199310302734%2C36.0631103515625
    // &width=20&height=20&srs=EPSG%3A4326&styles=&format=application/openlayers

    var oplayer_grp = [];           // dictionary of layer name and layer object
    var wfsUrl = geoe_url+'/wfs';
    
    for (var lyr_name in op_style) {

        // southwestgaslv_annual2023_controllablefitting
        var s = lyr_name.split("_"); 
        var lname = s[1].charAt(0).toUpperCase() + s[1].slice(1);       
        //console.log(lname);

        // {'controllablefitting': ['Point', 0, 1, ['SWGUID']]
        var decor = op_style[lyr_name];
        var geom = decor[0];
        var legend = decor[1];
        var popup = decor[2];
        var anno = decor[3];
        var sldfile = s[0]+"_annual2023_"+s[1]+".sld";

        var style = parseGeoSLD(geoe_url, slug, sldfile, lyr_name, geom, anno);

        oplayer_grp[lname] = L.Geoserver.wfs(wfsUrl, {
            layers:slug+":"+lyr_name,
            srsName: 'EPSG:4326',
            //pointToLayer: function (feature, latlng) { return L.circleMarker(latlng, myStyle);}
            style: style
            // sld_body: myStyle,
        }).addTo(map);
    };

    return oplayer_grp;
};


$.ajax({
    url: data_url,
    dataType: 'jsonp',
    jsonpCallback: callback_str,
    async: false,
    crossDomain: true,
    username: 'admin',
    password: 'geoserver',
    success: function(data) {
        oplayer_grp[lname] = L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                return L.circleMarker(latlng, setPointStyle(color[i]));
            },
            onEachFeature: addDialog
        }).addTo(map);
        i += 1;
    }
}).fail(function (jqXHR, textStatus, error) {
    console.log(error);
    return oplayer_grp;
});

$.ajax({
    url: data_url,
    dataType: 'jsonp',
    jsonpCallback: callback_str,
    async: false,
    crossDomain: true,
    username: 'admin',
    password: 'geoserver',
    success: function(data) {
        oplayer_grp[lname] = L.geoJSON(data, {
            style: setPolyStyle(color[i]),
            onEachFeature: addDialog
        }).addTo(map);
        i += 1;
    },
}).fail(function (jqXHR, textStatus, error) {
        console.log(error);
        return oplayer_grp;
});


// function addOvPopups() {
//     //
//     // TODO: add popup 
//     //
//     marker.on('click', function(evt) {
//         map.fire('click', evt, false);
//     });
//     var myLayer = new L.geoJson(null,{
//         onEachFeature: function 
//         (feature, layer) 
//         {layer.bindPopup(feature.properties.comment);} 
//         }).addTo(map);
// };
  

function addOpLegendsToMap(geoe_url, op_style, slug, map) {
    //
    // legend processing for overlays
    //
    var oplegend_var = [];    
    
    // {'controllablefitting': ['Point', 0, 1, ['SWGUID']]
    for (var lyr_name in op_style) {
        var s = lyr_name.split("_");
        console.log(lyr_name);
        var decor = op_style[lyr_name];
        var geom = decor[0];
        var legend = decor[1];
        var popup = decor[2];
        var anno = decor[3];

        oplegend_var[lyr_name] = L.Geoserver.legend(geoe_url+"/wms", {
            layers: slug+":"+ lyr_name,
            style: slug+":"+ s[0]+"_annual2023_"+s[1]
        });

        if (legend === 0) {oplegend_var[lyr_name].addTo(map)};
    };
};


//
// Instantiates a Popup object given an optional options object that describes 
// its appearance and location and an optional source object that is used to 
// tag the popup with a reference to the Layer to which it refers.
// L.popup(<Popup options> options?, <Layer> source?)
// marker.bindPopup(popupContent).openPopup();
// 	
function getPopup (latlng, content, map) {
    var popup = L.popup()
        .setLatLng(latlng)
        .setContent('<p>Hello world!<br />This is a nice popup.</p>')
        .openOn(map);
};

function setCircleColor(color) {
    var marker = {
        'radius':4,
        'opacity': .5,
        'color': color,
        'fillColor':  color,
        'fillOpacity': 0.8
    };
    return marker
};

var rootUrl = geoe_url+'/wfs';

var defaultParameters = {
    service: 'WFS',
    version: '2.0.0',
    request: 'GetFeature',
    typeName: 'acme:pand',
    maxFeatures: 200,
    outputFormat: 'application/json',
    srsName:'EPSG:28992',
    opacity: 1,

};

var parameters = L.Util.extend(defaultParameters);
var URL = rootUrl + L.Util.getParamString(parameters);
// TODO
// There are two things you need to change in GeoServer to makes wfs transactional.
// Enable Transactional under the WFS tab on GeoServer
// Under the Data tab on GeoServer you need to edit the rule ..w to enable the role ROLE_ANONYMOUS
// After doing these two things I was able to get rid of this error and post data to GeoServer.
//
// var sldfile = s[0]+"_annual2023_"+s[1]+".sld";   get style from geoserver counter part stylefile


function addOvPopups() {
    //
    // TODO: add popup 
    //
    marker.on('click', function(evt) {
        map.fire('click', evt, false);
    });
    var myLayer = new L.geoJson(null,{
        onEachFeature: function 
        (feature, layer) 
        {layer.bindPopup(feature.properties.comment);} 
        }).addTo(map);
};
  

function addOpLegendsToMap(geoe_url, op_style, slug, map) {
    //
    // legend processing for overlays
    //
    var oplegend_var = [];    
    
    // {'controllablefitting': ['Point', 0, 1, ['SWGUID']]
    for (var lyr_name in op_style) {
        var s = lyr_name.split("_");
        console.log(lyr_name);
        var decor = op_style[lyr_name];
        var geom = decor[0];
        var legend = decor[1];
        var popup = decor[2];
        var anno = decor[3];

        oplegend_var[lyr_name] = L.Geoserver.legend(geoe_url+"/wms", {
            layers: slug+":"+ lyr_name,
            style: slug+":"+ s[0]+"_annual2023_"+s[1]
        });

        if (legend === 0) {oplegend_var[lyr_name].addTo(map)};
    };
};


//
// Instantiates a Popup object given an optional options object that describes 
// its appearance and location and an optional source object that is used to 
// tag the popup with a reference to the Layer to which it refers.
// L.popup(<Popup options> options?, <Layer> source?)
// marker.bindPopup(popupContent).openPopup();
// 	
function getPopup (latlng, content, map) {
    var popup = L.popup()
        .setLatLng(latlng)
        .setContent('<p>Hello world!<br />This is a nice popup.</p>')
        .openOn(map);
};

function setCircleColor(color) {
    var marker = {
        'radius':4,
        'opacity': .5,
        'color': color,
        'fillColor':  color,
        'fillOpacity': 0.8
    };
    return marker
};
var map = L.map('map', {
    center: [33.578659, -7.615443],
    zoom: 13,
    layers: [googleStreets]
});

var geojsonLayer = new L.GeoJSON();

function handleJson(data) {
    console.log(data)
    geojsonLayer.addData(data);
}

var geoJsonUrl = "http://localhost:8080/geoserver/Gestion-proprete/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=Gestion-proprete:borne&maxFeatures=50&outputFormat=text/javascript&format_options=callback:getJson"
$.ajax({
    url: geoJsonUrl,
    dataType: 'json',
    jsonpCallback: 'getJson',
    success: handleJson
});

map.addLayer(geojsonLayer);