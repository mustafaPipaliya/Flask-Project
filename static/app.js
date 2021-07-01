//https://developer.here.com/documentation/examples/maps-js/infobubbles/open-infobubble

const my_apiKey = "w8hwjewq-A2Zp9aZXK-vFvFly88qzPFiwa6hX3mzazo"
var platform = new H.service.Platform({'apikey': my_apiKey});
// Obtain the default map types from the platform object:
var defaultLayers = platform.createDefaultLayers();
/**
 * Creates a new marker and adds it to a group
 * @param {H.map.Group} group       The group holding the new marker
 * @param {{lng: string, lat: string}} coordinate  The location of the marker
 * @param {String} html             Data associated with the marker
 */
function addMarkerToGroup(group, coordinate, html) {
    const marker = new H.map.Marker(coordinate);
    // add custom data to the marker
    marker.setData(html);
    group.addObject(marker);
}

/**
 * Add two markers showing the position of Liverpool and Manchester City football clubs.
 * Clicking on a marker opens an infobubble which holds HTML content related to the marker.
 * @param {H.Map} map A HERE Map instance within the application
 */
function addInfoBubble(map) {
    var group = new H.map.Group();

    map.addObject(group);

    // add 'tap' event listener, that opens info bubble, to the group
    group.addEventListener('tap', function (evt) {
        // event target is the marker itself, group is a parent event target
        // for all objects that it contains
        var bubble = new H.ui.InfoBubble(evt.target.getGeometry(), {
            // read custom data
            content: evt.target.getData()
        });
        // show info bubble
        ui.addBubble(bubble);
    }, false);

    const userLat=document.getElementById('user_lat').innerHTML
    const userLong=document.getElementById('user_lng').innerHTML

    addMarkerToGroup(group, {lat: userLat, lng: userLong},
        `<div><b>My Location</b></div>`);

    const centreData = JSON.parse(document.getElementById('centreData').innerHTML)
    for (const centre of centreData) {
        addMarkerToGroup(group, {lat: centre.lat, lng: centre.lng},
            `<ul><li><b>Name: </b>${centre.name}</li><li><b>Distance:</b> ${centre.distance} km</li><li><b>Time:</b> ${centre.duration} minutes</li></ul>`);
    }

    //Get bounding box of all points instead of setting centre of map.
    map.getViewModel().setLookAtData({
        bounds: group.getBoundingBox()
    });

}

/**
 * Boilerplate map initialization code starts below:
 */



const map = new H.Map(document.getElementById('mapContainer'),
    defaultLayers.vector.normal.map, {
        zoom: 1,
        pixelRatio: window.devicePixelRatio || 1,
        padding: {top: 200, left: 200, bottom: 200, right: 200}
    });

// add a resize listener to make sure that the map occupies the whole container
window.addEventListener('resize', () => map.getViewPort().resize());

// MapEvents enables the event system
// Behavior implements default interactions for pan/zoom (also on mobile touch environments)
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));

// create default UI with layers provided by the platform
var ui = H.ui.UI.createDefault(map, defaultLayers);

// Now use the map as required...
addInfoBubble(map);