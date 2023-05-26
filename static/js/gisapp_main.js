/*window.addEventListener("map:init", function (event) {
var map = event.detail.map;
// Download GeoJSON data with Ajax
fetch(mushroom_url)
  .then(function(resp) {
    return resp.json();
  })
  .then(function(data) {
    L.geoJson(data, {
      onEachFeature: function onEachFeature(feature, layer) {
        var props = feature.properties;
        var content = `<img src="${props.picture_url}"/><h3>${props.title}</h3><p>${props.description}</p>`;
        layer.bindPopup(content);
    }}).addTo(map);
  });
});*/


/*
var mapmargin = 50;
$('#map').css("height", ($(window).height() - mapmargin));
$(window).on("resize", resize);
resize();

function resize(){
    if($(window).width()>=980){
        $('#map').css("height", ($(window).height() - mapmargin));
        $('#map').css("margin-top",50);
    }
    else{
        $('#map').css("height", ($(window).height() - (mapmargin+12)));
        $('#map').css("margin-top",-21);
    }
}
*/

/* Notes
This will handle fetching the file and creating a Leaflet layer from it in one easy step.
If you are using leaflet-ajax plugin, it should definitely be one of the two below
var geojsonLayer = new L.GeoJSON.AJAX("geojson.json");
var geojsonLayer = L.geoJson.ajax("data.json");
L.geoJSON(data.responseJSON)
var geojsonlayer = new L.GeoJSON.AJAX("data/us-states.json").addTo(map);
,
var bbTeam = L.geoJSON(null, {onEachFeature: forEachFeature, style: style});
,
var maplayers = [];
maplayers["lung"] = new L.GeoJSON(data...
maplayers["throat"] = new L.GeoJSON(data...
Then when clicking on the checkbox you can use the string value to activate the indexed layer.
function updateLayerVis(a){
   var lyr = maplayers[a];
   lyr.addTo(map);
}
mapLayers[a].addTo(map); and this worked.
*/


// example of geojson format to read
function populateMap(data){
    for (var i = 0; i < data.features.length; i++) {
        var coordinates = data.features[i].geometry.coordinates;
        var lon = coordinates[0];
        var lat = coordinates[1];
        var name = data.features[i].properties.name;
        var sid = data.features[i].properties.sid;
        // console.log(lon,lat,sid,name);

        marker = new L.Marker(new L.point(loc), {title: title} );
        marker.bindPopup('<p><a href="'+ url + '">' + title + '</a></p>');
        wl_markers.addLayer(marker);
    }
}

// http://www.gistechsolutions.com/leaflet/DEMO/Simple/indexMap1.html
function setCircleColor(color) {
    var marker = {
        'radius':4,
        'opacity': .5,
        'color': color,
        'fillColor':  color,
        'fillOpacity': 0.8
    };
    return marker
}


function setHurricanStyle() {
    var style = {
        "bubblingMouseEvents": true,
        "color": "red",
        "dashArray": null,
        "dashOffset": null,
        "fill": true,
        "fillColor": "red",
        "fillOpacity": 0.2,
        "fillRule": "evenodd",
        "lineCap": "round",
        "lineJoin": "round",
        "opacity": 1.0,
        "radius": 5,
        "stroke": true,
        "weight": 3
    };
    return style;
}


function setTropicalStormStyle(){
    var style = {
        "bubblingMouseEvents": true,
        "color": "#ffcc99",
        "dashArray": null,
        "dashOffset": null,
        "fill": true,
        "fillColor": "#ffcc99",
        "fillOpacity": 0.2,
        "fillRule": "evenodd",
        "lineCap": "round",
        "lineJoin": "round",
        "opacity": 1.0,
        "radius": 5,
        "stroke": true,
        "weight": 3
    };
    return style;
}


function setTropicalDepressionStyle(){
    var style = {

    };
    return style;
}

// html: '<i class="fa fa-truck" style="color: red"></i>',
// also see css for customDivIcon
function setCustomIcon(name, iconColor) {
    html_str = '<i class="fa ' + name + '" style="color: ' + iconColor + '"></i>'
    var icon = L.divIcon({
        html: html_str,
        iconSize: [200, 200],
        className: 'customDivIcon'
    });
    return icon;
}


function setIcon(name, iconColor, markerColor) {
    // https://github.com/lvoogdt/Leaflet.awesome-markers
    // also see css file
    var icon = L.AwesomeMarkers.icon({
        icon: name,
        iconColor: iconColor,
        markerColor: markerColor,
        //prefix: 'glyphicon',   // for bootstrap-fontawesome
        prefix: 'fa',
        extraClasses: 'fa-rotate-0',  // this rotates the icon on top of the default marker
        iconSize: [35, 46]             // leave it the default size, this is for the balloon not this icon!
    });
    return icon;
};



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


function attachPopup(feature, layer) {
    if (feature.properties) {
        var gdata =  'Name&nbsp;&nbsp;: ' + feature.properties.name + '<br />';
            gdata += 'SID&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: ' + feature.properties.sid + '<br />';
            gdata += 'Lon/Lat:&nbsp;' + feature.geometry.coordinates + '<br />';

        // var gdata = "loading ....";
        var popupString = '<div class="popup"><p><b>' + gdata + '</b></p></div>';
        var popupOptions = {maxWidth: 1000};

        layer.bindPopup(popupString, popupOptions);
        // show content on mouse over
        // layer.on('mouseover', function(e){ this.openPopup(); });
        layer.on('click', function(e){ this.openPopup(); onClickedMarker(e, feature, layer); });
        layer.on('mouseout',  function(e){ this.closePopup();});
    } // end of if properties -
}

// y.domain([d3.min(data, function(d) { return d.Storm < d['D-Flow'] ? d.Storm : d['D-Flow']; }) - 0.3, d3.max(data, function(d) { return d.Storm > d['D-Flow'] ? d.Storm : d['D-Flow']; }) + 0.3]);
// And set y.domain(-1.8, 2.6)

function bindPopup(status, title, data, layer) {
    
    var margin = {top: 10, right: 10, bottom: 90, left: 60},
        width = 800 - margin.left - margin.right,
        height = 300 - margin.top - margin.bottom;

    if (status === 'TwoLines' || status === 'OneLine' || status === 'EdgeCase') {
        var popupString = '<div class="popup" style="width:800px;">' +
            '<div class="chart-title">' + title + '</div>' +
            '<div id="chart"></div>' +
            '</div>';

        layer.getPopup().setContent(popupString);

        if (status === 'EdgeCase') { return; }  // only show the title that contains error

        // parse the date / time
        var parseTime = d3.timeParse("%Y-%m-%d %H:%M");
        var formatTime1 = d3.timeFormat("%H");
        var formatTime2 = d3.timeFormat("%Y-%m-%d");

        // set the ranges
        var x = d3.scaleTime().range([0, width]);
        var y = d3.scaleLinear().range([height, 0]);


        // define the lines
        var stormLine = d3.line()
            .x(function(d) { return x(d.Date_Time); })
            .y(function(d) { return y(d.Storm); });

        var dFlowLine = d3.line()
            .x(function(d) { return x(d.Date_Time); })
            .y(function(d) { return y(d['D-Flow']); });

        // append the svg object to the body of the page
        // appends a 'group' element to 'svg'
        // moves the 'group' element to the top left margin
        var svg = d3.select("#chart").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");

        // format the data
        data.forEach(function(d) {
            d.Date_Time = parseTime(d.Date_Time) ? parseTime(d.Date_Time) : d.Date_Time;
            d.Storm = +d.Storm;
            if (status === 'TwoLines') {
                d['D-Flow'] = +d['D-Flow'];
            }
        });

        // Scale the range of the data
        // y.domain([d3.min(data, function(d) { return d.Storm < d['D-Flow'] ? d.Storm : d['D-Flow']; }) - 0.3, d3.max(data, function(d) { return d.Storm > d['D-Flow'] ? d.Storm : d['D-Flow']; }) + 0.3]);
        // And set y.domain(-1.8, 2.6)
        x.domain(d3.extent(data, function(d) { return d.Date_Time; }));
        if (status === 'TwoLines') {
            y.domain([d3.min(data, function(d) { return -3; }) - 0.3, d3.max(data, function(d) { return 4.0; }) + 0.3]);

        } else {
            y.domain([d3.min(data, function(d) { return d.Storm ; }) - 0.3, d3.max(data, function(d) { return d.Storm; }) + 0.3]);
        }

        // Add the storm path.
        svg.append("path")
            .data([data])
            .attr("class", "storm-line")
            .attr("d", stormLine);
        if (status === 'TwoLines') {
            // Add the d-flow path.
            svg.append("path")
                .data([data])
                .attr("class", "d-flow-line")
                .attr("d", dFlowLine);
        }

        // Add the x Axis
        svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(
                d3.axisBottom(x).
                tickFormat(function(d){ return formatTime1(d);}).
                ticks(50).
                tickSizeOuter(0)
            );
        svg.append("g")
            .attr("id", "axis1")
            .attr("transform", "translate(-12," + (height + 50) + ")")
            .call(
                d3.axisBottom(x).
                tickFormat(function(d){ return formatTime2(d);}).
                ticks(20).
                tickSizeOuter(0)
            );
        svg.append("g")
            .attr("transform", "translate(0, " + 0  +")")
            .call(d3.axisTop(x).ticks(0).tickSizeOuter(0));

        // text label for the x axis
        svg.append("text")
            .attr("transform",
                "translate(" + (width/2) + " ," +
                (height + margin.top + 80) + ")")
            .style("text-anchor", "middle")
            .text("Date Time");

        // Add the y Axis
        svg.append("g")
            .call(d3.axisLeft(y).ticks(20).tickSizeOuter(0));
        svg.append("g")
            .attr("transform", "translate(" + width + ", 0)")
            .call(d3.axisRight(y).ticks(0).tickSizeOuter(0));

        // text label for the y axis
        svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 0 - margin.left)
            .attr("x",0 - (height / 2))
            .attr("dy", "2.0em")
            .style("text-anchor", "middle")
            .text("Elevation (m)");

        // legend
        var legendTitles = ['Storm'];
        var colors = ['blue'];
        if (status === 'TwoLines') {
            legendTitles.push('D-Flow');
            colors.push('red');
        }

        var linear = d3.scaleOrdinal()
            .domain(legendTitles)
            .range(colors);

        svg.append("g")
            .attr("class", "legendLinear")
            .attr("transform", "translate(20,20)");

        var legendLinear = d3.legendColor()
            .cells(2)
            .shape('line')
            .shapeWidth(25)
            .orient('vertical')
            .scale(linear);

        svg.select(".legendLinear")
            .attr("font-size","10px")
            .attr("fill","black")
            .call(legendLinear);
    }

}


function onClickedMarker(e, feature, layer) {
    const payload = {"properties": feature.properties, "lonlat": feature.geometry.coordinates};

    console.log('**************');

    // const data = mockMarkerData.slice();
    // bindPopup(data, layer);

    // var key = feature.properties.sid
    // var resp = localStorage.getItem(key);
    // if (resp !== null) {
    //     var json_resp = JSON.parse(resp);
    //     var title = json_resp.plt_title;
    //     var status = json_resp.status;
    //     var data = json_resp.graph_data.slice();
    //     bindPopup(status, title, data, layer);
    // }

    // else {
         $.ajax({
             url : "/gisapp/",
             type : "POST",
             contentType: 'application/json; charset=utf-8',
             data: JSON.stringify(payload),
             dataType: 'text',
             success : function(resp) {
                 var json_resp = JSON.parse(resp);
                 console.log(json_resp)
                 var title = json_resp.plt_title;
                 var status = json_resp.status;
                 var data = json_resp.graph_data.slice();

                 // save in cache
                 //localStorage.setItem(key, resp);

                 console.log('status = ', status);

                 bindPopup(status, title, data, layer);
             },
             complete:function(){},
             error:function (xhr, textStatus, thrownError){}
         });
    // } // end of else
}



// #009933 green,
function processJsonMarkerData(data, icon_name, icon_color, marker_color) {
    var geojson = L.geoJSON(data, {
        onEachFeature: attachPopup,
        pointToLayer: function (feature, lonlat) {
            return L.marker(lonlat, {icon: setIcon(icon_name, icon_color, marker_color)});
        }
    });
    return geojson;
}


function processJsonPointData(color) {
    var d = L.geoJSON(null, {
            onEachFeature: attachPopup,
            pointToLayer: function (feature, latlng) {
                return L.circleMarker(latlng, setCircleColor(color));
            }
    });
    return d;
};



function processJsonLineData(color) {
    var d = L.geoJSON(null, {
            onEachFeature: attachPopup,
            style: getStyle(color)
        });
    return d;
};



function getPopupFrame(){
    var status_popup = L.popup({maxWidth: '2650'});
    var status_i_frame = $('<iframe src="data:text/html;charset=utf-8;base64,??" width="795" style="border:none !important;" height="330"></iframe>')[0];
    status_popup.setContent(status_i_frame);
    return status_popup;
};



// Main ====================================================
function map_init_basic(map, options) {
    // UR: -41.391, 74.719  LL: 21.304, -80.446  [-130, 18 ], [-64,50]
    
    var bounds = L.latLngBounds([26.0, -123.0], [48, -75]);
    options.maxBounds = bounds;
    map.fitBounds(os_open_layer.getBounds());
    map.fitBounds(bounds, {padding: [50,50]});
    map.setView([37.52715,-96.877441], 4);
    map._layersMaxZoom = 19;    // for error in markerClusterGroup

    map.addControl(new L.Control.Fullscreen({
        title: {
            'false': 'View Fullscreen',
            'true': 'Exit Fullscreen'
        }

    }));

    // resetview
    map.addControl(new L.Control.ResetView(bounds));

    // Using a custom SVG icon as content
    var zoomControl = L.control.zoomBox({
        title: "Zoom box",
        addToZoomControl: true,
        modal: true,
        className: "custom-content",
        content: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><g transform="translate(0,0)"><path fill="rgba(0, 0, 0, 1)" d="M138.563 16.063C83.49 42.974 41.459 86.794 16.124 138.53l59.938 29.407c18.988-38.845 50.47-71.807 91.812-92l-29.313-59.874zm234.843.156L344 76.124c38.846 18.99 71.807 50.47 92 91.813l59.875-29.313c-26.913-55.073-70.732-97.073-122.47-122.406zm62.53 327.717c-18.982 38.865-50.53 71.673-91.873 91.875l29.437 60.125c55.116-26.925 97.085-70.76 122.375-122.562l-59.938-29.438zm-359.936.125l-60 29.375c26.928 55.097 70.776 97.082 122.563 122.375l29.406-59.937C129.122 416.885 96.192 385.4 76 344.062z"></path></g></svg>'
    });
    map.addControl(zoomControl);

    


    // Get GeoJSON data and create features.
    // =============================================

    for(i = 0; i < custlayers.length; i++){
        console.log(custlayers[i])
    };

    // AOI data
    var chesapeakebay_data = processJsonLineData("black");
    $.getJSON(chesapeakebay_url, function(data) {
        // alert(JSON.stringify(data));
        chesapeakebay_data.addData(data);
    });

    var delawarebasin_data = processJsonLineData("black");
    $.getJSON(delawarebasin_url, function(data) {
        // alert(JSON.stringify(data));
        delawarebasin_data.addData(data);
        delawarebasin_data.addTo(map);
        // map.fitBounds(delawarebasin_data.getBounds());
    });

    var delawareriver_data = processJsonLineData("#0077be");
    $.getJSON(delawareriver_url, function(data) {
        // alert(JSON.stringify(data));
        delawareriver_data.addData(data);
    });


    var pamlicosound_data = processJsonLineData("black");
    $.getJSON(pamlicosound_url, function(data) {
        // alert(JSON.stringify(data));
        pamlicosound_data.addData(data);
    });


    // CO-OPS Station Locations for Water Level
    var wl_markers = L.markerClusterGroup();
    $.getJSON(coopswaterlevel_url, function(data) {
        var wl_data = processJsonMarkerData(data, "fa-water-rise", "white", "blue");
        wl_markers.addLayer(wl_data);
        wl_markers.addTo(map);
    });


    // use context variable instead of making AJAX call
    // var wl_markers = L.markerClusterGroup();
    // var data = JSON.parse(map_coopswaterlevel);
    // var wl_data = processJsonMarkerData(data, "fa-water-rise", "white", "blue");
    // wl_markers.addLayer(wl_data);
    // wl_markers.addTo(map);


    /*
    // CO-OPS Active Meter Station Location (Sea Surface Height, Wind
    var activemeters_markers;
    $.getJSON(coopsactivemeters_url, function(data) {
        activemeters_data = processJsonMarkerData(data);
        activemeters_markers = L.markerClusterGroup();
        activemeters_markers.addLayer(activemeters_data);
        // activemeters_markers.addTo(map);
    });
    */


    // NDBC BUOY Station Location (Wind, wave)
    var ndbcobsv_markers = L.markerClusterGroup();
    $.getJSON(ndbcobsv_url, function(data) {
        ndbcobsv_data = processJsonMarkerData(data, "flag", "white", "gray");
        ndbcobsv_markers.addLayer(ndbcobsv_data);
        // ndbcobsv_markers.addTo(map);
    });


    var coastline_data = processJsonLineData("#00a7be");
    $.getJSON(worldcoastline_url, function(data) {
        coastline_data.addData(data);
        // coastline_data.addTo(map);
    });


    var dflow_landbnd_data = processJsonLineData("red");
    $.getJSON(dflow_landbnd_url, function(data) {
        dflow_landbnd_data.addData(data);
    });

    // End of data processing


    var baseLayers = {
        "Open Streets":osm,
        "World Imagery": img,
        "Creative Commons": stamen
    };

    // https://github.com/ismyrnow/leaflet-groupedlayercontrol
    // Overlay layers are grouped
    var groupedOverlays = {
        // model related regions
        "AOI": {
            "Chesapeake Bay": chesapeakebay_data,
            "Delaware River": delawareriver_data,
            "Delaware Basin": delawarebasin_data,
            "Pamlico Sound": pamlicosound_data,
            "Dflow Land Boundary": dflow_landbnd_data,
        },
        // Cooperative Observer Network
        "CO-OPS": {
            "Water Level": wl_markers,
            // "Sea Surface Height": activemeters_markers,
            // "Wind": activemeters_markers
        },
        "NDBC": {
            "Wind": ndbcobsv_markers,
        },
        "Others": {
            "Coast": coastline_data,
        }

    };

    // Make the "AOI" group exclusive (use radio inputs) - exclusiveGroups: ["AOI"],
    var options = {collapsed: false, autoZIndex: false};
    var control = L.control.groupedLayers(baseLayers, groupedOverlays, options).addTo(map);

    // Move the legend in map tab in sidebar
    // 1- Call the getContainer routine.
    var htmlObject = control.getContainer();
    // 2- Get the desired parent node.
    var a = document.getElementById('webmap-tab-inset');
    // 3- Finally append that node to the new parent, recursively searching out and re-parenting nodes.
    function setParent(el, newParent){ newParent.appendChild(el); }
    setParent(htmlObject, a);


} // end of main
