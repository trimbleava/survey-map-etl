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



// layer_control = L.control.groupedLayers(null, groupedOverlays, options).addTo(map);
// OR this: layer_control.addOverlay(region_layer, "newlayer", "Overlays");
//

// Main ====================================================
function map_init_basic(map, options) {
    
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
  /* map.default_zoom = 5;
  map.min_zoom = 3;
  map.max_zoom = 18;
  map.zoom_snap = 0.25;
  map.default_precision = 6; */
 
  //
  // set the full screen option
  //
  map.addControl(new L.control.fullscreen()); 
  
  //
  // resetview - always to global map, because we display all the layers on the home view
  //
  map.addControl(new L.Control.ResetView( map.getBounds()));
 
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
  /* var groupedBase = {
    "Base Layers": baseLayers
  };
  controlLayers = L.control.groupedLayers(groupedBase).addTo(map); */

  // 
  // Data processing 
  //
  var region_layer = L.geoJson.ajax(region_url, {  
    onEachFeature: addRegionPopup,
    style: getRegionStyle(),
    zIndex: 999    
  }).addTo(map);  
      
  $.getJSON( region_url, function( data ) {
    data.features.forEach(getRegionName);
    function getRegionName(item) {
      if (item.properties.name) {
        region_name = item.properties.name;   
        controlLayers.addOverlay(region_layer, item.properties.name);
      } 
    }
  });

  //
  // Operational layers - TODO
  //


// L.tileLayer.wms(<String> baseUrl, <TileLayer.WMS options> options)

/*
Note: below commented statements are the original from leaflet that works with multiple layers.
This is important for performance because each addTo(map) is a ajax/network call to geoserver. 
Howerver, for groupedLayer we need a name:layer that I do not know how to do! TODO

var ovlyrs_str = '';    // concat all the layes and send to geoserver at once

for(var i=0; i<ovlyrs.length; i+=1) {
    var lyr = ovlyrs[i];
    ovlyrs_str += slug+":"+ lyr + ","
};
ovlyrs_str = ovlyrs_str.slice(0, -1);

wms_var = L.tileLayer.wms(geoe_url+"/wms", {
    layers: ovlyrs_str,   // a string list of layers
    format: 'image/png',  // jpeg - use png for transparency
    transparent: true,
    attribution: copyright,
    srs: 'EPSG%3A4326',
    opacity: 1,          // how opac these layers are -- 0 do not show
    zIndex: 1000
}).addTo(map);  

For this reason using the plugins leaflet-geoserver-request for now! 
*/

//
// Overlay layers
//
var ovlyr_names = [];    // for groupedlayer
  
if (overlay_dict) { 

    var copyright = " | Heathus.com " + survey_copyright;
    var ovlyrs = Object.keys(overlay_dict);

    //
    // same as above with leaflet-geoserver-request plugins
    // that seems is not working with multiple layers
    //
    var overlay_var = [];
    for (var i=0; i<ovlyrs.length; i+=1) {
        var lyr_name = ovlyrs[i];
        ovlyr_names.push(lyr_name);
        overlay_var[lyr_name] = L.Geoserver.wms(geoe_url+"/wms", {
            layers: slug+":"+ lyr_name,
            attribution: copyright,
            srs: 'EPSG%3A4326'
        }).addTo(map);
    };    // end of for  

      //
      // TODO: add popup 
      //
    
      //
      // legend processing for overlays
      // TODO: if could send on one request
      //       needs to filter which legend to show, add flag to config
      //
      var overlay_legend_var = [];
      for(var i=0; i<ovlyrs.length; i+=1) {
            var lyr_name = ovlyrs[i];
            overlay_legend_var[lyr_name] = L.Geoserver.legend(geoe_url+"/wms", {
                layers: slug+":"+ lyr_name,
                style: slug+":"+ lyr_name
            });  
      };
      // TODO - add legend flag to config, we do not want to show all
      overlay_legend_var["MainLines"].addTo(map);
      overlay_legend_var["Risers"].addTo(map);

};// end of if overlay_dict
    
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
  // grouped overlay/operational layer control
  // TODO: get the group names from customer config to substitute for Overlays, Survey hardcoded
  //
  var groupedOverlays = {"Overlays":{}, "Survey": {"TODO": region_layer}};
  var lyr_grp = {};    // to be used for all groups

  if (overlay_dict) {
    for(var i = 0; i < ovlyr_names.length; i += 1) {
      var lyr_name = ovlyr_names[i];
      var lyr_var = overlay_var[lyr_name];
      lyr_grp[lyr_name] = lyr_var;
    };
    groupedOverlays["Overlays"] = lyr_grp;
  };    // end of if
  // console.log(groupedOverlays);

  //
  // add the group layers to map and zoom into layers
  // TODO: verify if we only need to zoom into operational layers because
  //       the overlay layers grow over time. which in this case we need
  //       the bbox of the union of the operational layers instead of ov.
  //
  var layer_control;
  if (overlay_dict) {
    layer_control = L.control.groupedLayers(null, groupedOverlays, options).addTo(map);
    var ur = [ov_bbox[0], ov_bbox[1]];
    var ll = [ov_bbox[2], ov_bbox[3]];
    var bounds = new L.latLngBounds(ur, ll);
    options.maxBounds = bounds;
    map.fitBounds(bounds, {padding: [50,50]});
  };    // end of if
 
  // End of data processing

  //
  // update the scale - TODO
  //
  scontrol = L.control.scale();   
} // end of callback
