// First, enable JSONP in GeoServer.
// Add to this file: /tomcat/webapps/geoserver/WEB-INF/web.xml
// <context-param>
//    <param-name>ENABLE_JSONP</param-name>
//    <param-value>true</param-value>
// </context-param>
// and restart the service. Then, in your json request use format=text/javascript

// http://localhost:8080/geoserver/rest/workspaces/southwestgaslv/featuretypes.json

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

/////////////////////////// Functions //////////////////////////

function addDialog(feature, layer) {
    var props = feature.properties;
    var attrs = Object.keys(props);
    var popupString = "";

    for (var i = 0; i < attrs.length; i += 1) {
        attribute = attrs[i];
        value = props[attribute];
        popupString += attribute+":"+value+"\n";
    }
    layer.bindPopup(popupString);
};

function setLineStyle(color) {
    var style = {
        color: color,
        weight: 2,
        opacity: 1,
    };
    return style;
};

function setPointStyle(color) {
   
    var style = {
        'radius':4,
        'opacity': .5,
        'color': color,
        'fillColor':  color,
        'fillOpacity': 0.8
    };
    return style;
};

function setPolyStyle(color) {
    var style = {
        fillColor: color,
        color: color,
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8
    };
    return style;
};



//
// Operational layers - Main
//  
function addOplayersToMap(geoe_url, op_style, slug, map) {

    var oplayer_grp = [];           // dictionary of layer name and layer object
    var mycolor = ['black', 'blue', 'green', 'orange', 'cyan', 'red', 'purple'];
    var i = 0;                      // index to pick color, TODO: to be done in a better way
    var wfsUrl = geoe_url+'/wfs';
   
    for (var lyr_name in op_style) {
       
        // {'southwestgaslv_controllablefitting': ['Point', 0, 1, ['SWGUID']]
        var s = lyr_name.split("_"); 
        var lname = s[1].charAt(0).toUpperCase() + s[1].slice(1);     // TODO - generic number of split 

        var decor = op_style[lyr_name];       // user selected decoration for each layer
        var geom = decor[0];                  // geometry of the feature
        var legend = decor[1];                // boolean 1 means user wants legend for this layer
        var dialog = 1;          //decor[2];                // boolean 1 means user wants popup for this layer
        var anno = decor[3];                  // list of attributes with text label

        var ugeom = geom.toUpperCase();
        console.log(lyr_name);
        if (ugeom == "POINT" || ugeom == "MULTIPOINT"){
            var pnt_geojson = L.Geoserver.wfs(wfsUrl, {
                layers: slug+":"+lyr_name,
                srsname: 'EPSG:4326',
                async:false,
                maxFeatures: 200,
                pointToLayer: function (feature, latlng) { 
                    return L.circleMarker(latlng, setPointStyle(mycolor[i]));
                }  
            }).addTo(map);
            
            console.log(pnt_geojson);

            // add this layer only if data
            if(pnt_geojson) {
                   
                // legend
                if(legend == 1) {
                    var legend = L.Geoserver.legend(geoe_url+"/wms", {
                        layers: slug+":"+lyr_name
                        // TODO
                    }).addTo(map);
                }

                // popup dialog
                if(dialog==1) {
                    pnt_geojson.eachLayer(function (layer) {
                        layer.bindPopup('Hello');
                        console.log("this is the layer");
                        console.log(layer);
                    });
                }

                // save the layer as part of the group control
                oplayer_grp[lname] = pnt_geojson;

            } // end of data
            
        } // end of point layer (s)     

        else if (ugeom == "POLYGON" || ugeom == "MULTIPOLYGON") {

            poly_geojson = L.Geoserver.wfs(wfsUrl, {
                layers:slug+":"+lyr_name,
                srsname: 'EPSG:4326',
                async: false,
                style: getPolyStyle(mycolor[i])  
            }).addTo(map);
            
            oplayer_grp[lname] = poly_geojson;
        }
        else {
 
            line_geojson = L.Geoserver.wfs(wfsUrl, {
                layers:slug+":"+lyr_name,
                srsname: 'EPSG:4326',
                async: false,
                style: getLineStyle(mycolor[i])
            }).addTo(map);
            
            oplayer_grp[lname] = line_geojson;
        }

        // next color index
        i = i + 1;

    };  // end of for
    
    return oplayer_grp;
};

