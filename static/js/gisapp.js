//   var region_layer = processJsonLineData("red");
//   $.getJSON(region_url, function(data) {
//     region_layer.addData(data);
//   });

// download GeoJSON data with Ajax
//   fetch(region_url).then(function(resp) {
//     return resp.json();
//   }).then(function(data) {
//     var region_layer =  L.geoJson(data, {
//       onEachFeature: function onEachFeature(feature, layer) {
//         var props = feature.properties;
//         var content = `<h5>${props.name}</h5><p>USPS: ${props.stusps}<br>State Geoid: ${props.geoid}</p>`;
//           layer.bindPopup(content);
//       },
//       style: getRegionStyle()
//     }).addTo(map);   // end of data
//     controlLayers.addOverlay(region_layer, 'Nevada');
//   }); // end of then

function getPolyStyle(){
    var style = {
        "color": "#D3D3D3",
        "weight": 1,
        "opacity": 0.8 
    };
    return style;
};

// region style
function getRegionStyle(){
    var style = {
        "color": "#ff7800",             // #D3D3D3 #ff7800",
        "weight": 2,
        "opacity": 1,                   // 0.25
        "fill": false
    };
    return style;
};

function addRegionPopup(feature, layer) {   
    var props = feature.properties;
    var content = `<h5>${props.name}</h5><p>USPS: ${props.stusps}<br>State Geoid: ${props.geoid}</p>`;
    layer.bindPopup(content);
}
  

function getStyle(color) {
    var linestyle = {
        'opacity': 1,
        "fill": false,
        'color': color,
        'fillOpacity': 0.5,
        'weight': 3
    };
    return linestyle;
};

function processJsonLineData(color) {
    var d = L.geoJSON(null, {
        style: getStyle(color)
    });
    return d;
};

function getMapBounds(map) {
    var sw = map.options.crs.project(map.getBounds().getSouthWest());
    var ne = map.options.crs.project(map.getBounds().getNorthEast());
    var BBOX = sw.x + "," + sw.y + "," + ne.x + "," + ne.y;
    return BBOX;
};

function getMapsize(map){
    var width = map.getSize().x;
    var height = map.getSize().y; 
    // return values
    return {
        'WIDTH': width,
        'HEIGHT': height
    };
};

function adjustView(map) {
    //
    // display adjustments options after layer inclusion - NOT USED - keeping for examples
    //

    // test case
    var ur = [37.746880, -84.301460];
    var ll = [31.284788, -92.471176];
    var bounds = new L.latLngBounds(ur, ll);
    //console.log(bounds);

    // overriding global options setin django settings
    // options.maxBounds = bounds;
    // alert(JSON.stringify(map.options["maxZoom"]));

    //map.fitBounds(bounds, {padding: [50,50]});
    //map.setView([37.52715,-96.877441], 4);               // usa center
    //map._layersMaxZoom = 19;                             // for error in markerClusterGroup
    // map.spatial_extent =  (49.382808,-66.945392,24.521208,-124.736342);   
    // map.default_center = (37.09024,-95.712891);          // initial map, usa center, zoom 5
};

function getUnionBounds(lyr_bounds){
    //
    // NOT USED: kept for example
    // set the bounds for union of layers, but keep the rest view to global usa bounds
    //

    // <LatLonBoundingBox minx="-123.042" miny="42.251" maxx="-122.772" maxy="42.438" />  where this comes from??
    // <BoundingBox SRS="EPSG:4326" minx="-123.042" miny="42.251" maxx="-122.772" maxy="42.438" /> 

    // var bounds = new L.LatLngBounds([[Math.max(lat, borneLat), Math.max(lng, borneLng)], 
    //                                  [Math.min(lat, borneLat), Math.min(lng, borneLng)]]);

    console.log(lyr_bounds);
    var ll_lat = lyr_bounds["_southWest"]["lat"];   
    var ll_lng = lyr_bounds["_southWest"]["lng"];  // lat: 45.1510532655634, lng: -66.26953125000001
    var ur = lyr_bounds["_northEast"];
    var ur_lat = lyr_bounds["_northEast"]["lat"];
    var ur_lng = lyr_bounds["_northEast"]["lng"];   
};


//
// Main ====================================================
//
function map_init_basic(map, options) {
     
    //
    // layer_control = L.control.groupedLayers(null, groupedOverlays, options).addTo(map);
    // OR layer_control.addOverlay(region_layer, "newlayer", "Overlays");
    //
    // get layer control from settings file
    // map.layerscontrol is the attribute that the Tiles from the settings.py are added to
    //
    var controlLayers = map.layerscontrol;
    
    //
    // At each zoom level, each tile is divided in four, and its size (length of the edge, given by
    // the tileSize option) doubles, quadrupling the area. (In other words, the width and height of
    // the world is 256·2zoomlevel pixels). This goes on and on. Most tile services offer tiles up to 
    // zoom level 18, depending on their coverage. This is enough to see a few city blocks per tile.
    // All below variables are set in global settings, just for ref.
    //
    /*  map.default_zoom = 5;
        map.min_zoom = 3;
        map.max_zoom = 18;
        map.zoom_snap = 0.25;
        map.default_precision = 6; 
    */
 
    //
    // Set the full screen option
    //
    map.addControl(new L.control.fullscreen()); 
  
    //
    // resetview - always to global map, because we display all the layers on the home view
    //
    map.addControl(new L.Control.ResetView (map.getBounds()));
 
    // 
    // add the grouped tile layers to the control: layerGroup(<Layer[]> layers?, <Object> options?)
    // base layers not working due to lack of provider and not being able to get the tiles from settings.
    // L.layerGroup(baseLayers).addTo(map);
    // TODO: implement the base layers into checkbox for zooming limitation.
    //       L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    //       attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
    //       maxZoom: 18,
    //       id: 'your.mapbox.project.id',
    //       accessToken: 'your.mapbox.public.access.token'
    //       }).addTo(map);
    // 
    /* 
        var groupedBase = {
            "Base Layers": baseLayers
        };
        controlLayers = L.control.groupedLayers(groupedBase).addTo(map); 
    */

    // 
    // Region data
    //
    var region_layer = L.geoJson.ajax(region_url, {  
        onEachFeature: addRegionPopup,
        style: getRegionStyle(),
        zIndex: 9999    
    }).addTo(map);  
      
    //
    // Add popup for the region
    //
    $.getJSON( region_url, function( data ) {
        data.features.forEach(getRegionName);
        function getRegionName(item) {
            if (item.properties.name) {
                region_name = item.properties.name;   
                controlLayers.addOverlay(region_layer, item.properties.name);
            } 
        }
    });

    
    function addDialog(feature, layer) {
        var props = feature.properties;
        var attrs = Object.keys(props);
        var name = "Layer Table";
        var popupContent =  '<h4 class = "text-primary">' + name + '</h4>' +
        '<div class="container"><table class="table table-striped">'+
        '<thead><tr><th>Properties</th><th>Value</th></tr></thead>';
  
        for (var i = 0; i < attrs.length; i += 1) {
            attribute = attrs[i];
            value = props[attribute];
            popupContent += '<tbody><tr><td>' +  attribute + '</td><td>' + value + '</td></tr>';
        }
        popupContent += ';' ;
        // console.log(popupContent);
        layer.bindPopup(popupContent);
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

    function setPointStyle(color) {
        // var colors = ['black', 'blue', 'green', 'orange', 'cyan', 'red', 'purple'];
        var style = {
            'radius':4,
            'opacity': .5,
            'color': color,
            'fillColor':  color,
            'fillOpacity': 0.8
        };
        console.log("color is .........." + color);
        return style;
    };

    // http://127.0.0.1:8080/geoserver/rest/workspaces/southwestgaslv/datastores/annual2023/featuretypes/southwestgaslv_mhpsurvey.html
    // southwestgaslv_noncontrollablefitting&wsName=southwestgaslv
    // var url = `${that.baseLayerUrl}/wms?REQUEST=GetLegendGraphic&VERSION=1.1.0&FORMAT=image/png&LAYER=${that.options.layers}&style=${that.options.style}`;
    // <img src='http://server:8080/geoserver/wms?REQUEST=GetLegendGraphic&VERSION=1.0.0&FORMAT=image/png&WIDTH=20&HEIGHT=20&STRICT=false&style=southwestgaslv_noncontrollablefitting&wsName=southwestgaslv'>
    // var imageUrl = 'https://maps.lib.utexas.edu/maps/historical/newark_nj_1922.jpg';
    // const geoserverRESTAPI = 'http://localhost:8080/geoserver/rest/';
    // const options = {
    //     url: `${geoserverRESTAPI}styles`,
    //     method: 'POST',
    //     headers: { 'Content-type': 'application/vnd.ogc.sld+xml' },
    //     body: sldString, //in string format
    //     auth: {
    //     user: '<username>',
    //     pass: '<password>'
    //     }
    // }


    var groupedOverlays = {"Overlay":{}, "Operational": {}};
    var layer_control = null;
    
    //
    // Overlay layers
    //
    if (ov_status) { 
        console.log(ov_status);

        var copyright = " | Heathus.com " + survey_copyright;
        var ovlyrs = Object.keys(ov_style)
        console.log(ovlyrs);
        var ovlyr_grp = [];
       
        
        // add data
        var ovlyr_grp = addOvlayersToMap(geoe_url, ovlyrs, slug, copyright, map)
       
        // add popup
        
        // add legends
        addOvLegendsToMap(geoe_url, ov_style, slug, map)

       
        // add to layer group
        groupedOverlays["Overlay"] = ovlyr_grp;
    }


    //
    // Operational layers
    //
    if (op_status) {

        var oplyr_grp = []; 

        // add data
        // oplyr_grp = addOplayersToMap(geoe_url, op_style, slug, map);

        var wfsUrl = geoe_url+'/wfs';
  
        var wfscont = L.Geoserver.wfs(wfsUrl, {
            layers: "southwestgaslv:southwestgaslv_controllablefitting",
            srsname: 'EPSG:4326',
            // async:true,
            pointToLayer: function (feature, latlng) { 
                return L.circleMarker(latlng, setPointStyle('black'));
            },
            onEachFeature: addDialog
        }).addTo(map);

        L.Geoserver.legend(geoe_url+"/wms", {
            layers: "southwestgaslv:southwestgaslv_controllablefitting"
            //style: "southwestgaslv:southwestgaslv_annual2023_controllablefitting"
        }).addTo(map); 
        oplyr_grp["Controllablefitting"] = wfscont;

        var wfsreg = L.Geoserver.wfs(wfsUrl, {
            layers: "southwestgaslv:southwestgaslv_regulatorstation",
            srsname: 'EPSG:4326',
            // async:true,
            pointToLayer: function (feature, latlng) { 
                return L.circleMarker(latlng, setPointStyle('red'));
            },
            onEachFeature: addDialog
        }).addTo(map);
        L.Geoserver.legend(geoe_url+"/wms", {
            layers: "southwestgaslv:southwestgaslv_regulatorstation"
            // style: "southwestgaslv:southwestgaslv_annual2023_regulatorstation"
        }).addTo(map); 
        oplyr_grp["Regulatorstation"] = wfsreg;

        var wfsmh = L.Geoserver.wfs(wfsUrl, {
            layers: "southwestgaslv:southwestgaslv_mhpsurvey",
            srsname: 'EPSG:4326',
            // async:true,
            style: setPolyStyle("cyan"),
            onEachFeature: addDialog
        }).addTo(map);
        var mhlegend = L.Geoserver.legend(geoe_url+"/wms", {
            layers: "southwestgaslv:southwestgaslv_mhpsurvey",
            // style: "southwestgaslv:southwestgaslv_annual2023_mhpsurvey"
        });
        mhlegend.addTo(map); 

        oplyr_grp["Mhpsurvey"] = wfsmh;

        // add popup
        
        // add legends
        // op_legend_var = addOpLegendsToMap(geoe_url, oplyrs, slug, map)

        // add to layer group
        groupedOverlays["Operational"] = oplyr_grp;
    }

    //
    // options for grouped layers both overlay and operational
    //
    var options = {
      // Make the "Landmarks" group exclusive (use radio inputs)
      // exclusiveGroups: ["Landmarks"],
      // Show a checkbox next to non-exclusive group labels for toggling all
      groupCheckboxes: false,
      collapsed: false
    };

    //
    // add the group layers to map, if available
    //
    layer_control = L.control.groupedLayers(null, groupedOverlays, options).addTo(map);

    //
    // change the attribution color to orange
    //
    // varName = L.control.attribution({prefix: '<span class="AttributionClass">some text</span>'}).addTo(map);
    //    "color": "#ff7800",             // #D3D3D3 #ff7800",
        

    //
    // Zoom into layers
    // TODO: verify if we only need to zoom into operational layers because
    //       the overlay layers grow over time. which in this case we need
    //       the bbox of the union of the operational layers instead of ov.
    // if (ov_bbox) {
    //     var ur = [ov_bbox[0], ov_bbox[1]];
    //     var ll = [ov_bbox[2], ov_bbox[3]];
    //     var bounds = new L.latLngBounds(ur, ll);
    //     options.maxBounds = bounds;
    //     map.fitBounds(bounds, {padding: [50,50]});
    // }

    //
    // update the scale - TODO
    //
    scontrol = L.control.scale();  
 

} // end of callback
