
//
// process_ovlayers.js
//
function addOvlayersToMap(geoe_url, ovlyrs, slug, copyright, map) {
    //
    // requires leaflet-geoserver-request plugins
    // that seems is not working with multiple layers
    //
    var ovlayer_grp = [];    // dictionary of layer name and layer object, 
                             // collected for group layer
    for (var i=0; i<ovlyrs.length; i+=1) {
        var lyr_name = ovlyrs[i];
        
        ovlayer_grp[lyr_name] = L.Geoserver.wms(geoe_url+"/wms", {
                layers: slug+":"+ lyr_name,
                attribution: copyright,
                srs: 'EPSG%3A4326'
            }).addTo(map);
    }; // end of for  

    return ovlayer_grp;
};


function addOvPopups() {
    //
    // TODO: add popup 
    //
    marker.on('click', function(evt) {
        map.fire('click', evt, false);
    });
};
  

function addOvLegendsToMap(geoe_url, ov_style, slug, map) {
    //
    // legend processing for overlays
    //
    var ovlegend_var = [];    
    
    // {'controllablefitting': ['Point', 0, 1, ['SWGUID']]
    for (var lyr_name in ov_style) {
        console.log(lyr_name);
        var decor = ov_style[lyr_name];
        var geom = decor[0];
        var legend = decor[1];
        var popup = decor[2];
        var anno = decor[3];

        ovlegend_var[lyr_name] = L.Geoserver.legend(geoe_url+"/wms", {
            layers: slug+":"+ lyr_name,
            style: slug+":"+ lyr_name
        });

        if (legend === 1) {ovlegend_var[lyr_name].addTo(map)};
    };
};


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
    
    // L.tileLayer.wms(<String> baseUrl, <TileLayer.WMS options> options)
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