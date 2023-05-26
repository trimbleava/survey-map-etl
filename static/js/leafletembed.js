var mapid;
var ajaxRequest;
var plotlist;
var plotlayers=[];

function initmap() {
	// set up the map
	map = new L.Map('mapid');

	// create the tile layer with correct attribution
	var osmUrl='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib='Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors';
	var osm = new L.TileLayer(osmUrl, {minZoom: 8, maxZoom: 12, attribution: osmAttrib});

	// start the map in South-East England
	map.setView(new L.LatLng(51.3, 0.7),9);
	map.addLayer(osm);
}

// get this per client from db
function initmap2() {
    // var map = L.map('mapid').setView([26.926968, -81.502075], 7);
    var map = L.map('mapid', {
        center: [26.926968, -81.502075],
        zoom: 7
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    L.marker([26.926968, -81.502075]).addTo(map)
        .bindPopup('center: 26.926968, -81.502075')
        .openPopup();
} // end of initmap
