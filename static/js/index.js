// DOM Management
$( document ).ready(function() {
    $('#searchButton').on('click', keywordSearch);
});

function keywordSearch(){
  var keyword = $('#searchBox').val();
  httpGetAsync("search/", keyword);
}

function dropdownListSearch(keyword){
  httpGetAsync("search/", keyword);
}

function toggleDropdownList() {
  $("#dropdownListDiv")[0].classList.toggle("show");
}


function foldTile() {
  var foldButtonDiv = $('#foldButtonDiv')[0];
  $('#searchDiv').toggle(500);
  $('#titleDiv').toggle(500);
  if (foldButtonDiv.innerHTML == "+") {
    foldButtonDiv.innerHTML = "\u2212";
  } else {
    foldButtonDiv.innerHTML = "+";
  }
}


// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {

    var dropdowns = $(".dropdownContent")
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}

// Google Map
var ourMap;
var markerClusterer = null;
var coordinates_lat = [];
var coordinates_lng = [];
var created_at = [];
var userNames = [];
var userScreenNames = [];
var tweets = [];
var markers = [];
var prev_infowindow = null;


function initMap() {
	var myLatLng = {
		lat: 39.8282,
		lng: -98.5795
	};

	ourMap = new google.maps.Map(document.getElementById('map'), {
		zoom: 3,
		center: myLatLng,
    zoomControl: true,
    zoomControlOptions: {
      position: google.maps.ControlPosition.RIGHT_CENTER
    }
	});
  markerClusterer = new MarkerClusterer(ourMap, markers);
}

function resetVariables(){
  coordinates_lat = [];
  coordinates_lng = [];
  created_at = [];
  tweets = [];
  userNames = [];
  userScreenNames = [];
  prev_infowindow = null;
  deleteMarkers();
  markerClusterer.clearMarkers();
}
//handle the search part
function httpGetAsync(theUrl, keyword) {
  resetVariables()
  $.getJSON(theUrl + keyword, function(result){
      processJsonResult(result, keyword);
  });
}

function processJsonResult(result, keyword) {
  var tweets_list = result[keyword];
  if (tweets_list == null || tweets_list.length == 0) {
    alert("No results found");
    return;
  }

  for (var i = 0; i < tweets_list.length; i++) {
      var tweet = tweets_list[i];
      coordinates_lng.push(tweet.coordinates[0]);
      coordinates_lat.push(tweet.coordinates[1]);
      created_at.push(tweet.created_at);
      tweets.push(tweet.text);
      created_at.push(tweet.created_at);
      userNames.push(tweet.user_name);
      userScreenNames.push(tweet.user_screen_name);
  }
  generateMarkers();
}

function generateMarkers() {
  for (var i = 0; i < tweets.length; i++) {
    var location = {
      lat: parseFloat(coordinates_lat[i]),
      lng: parseFloat(coordinates_lng[i])
    };

    var contentString = '<div id="content">'+
            "<h3>" + userNames[i] + " (@" + userScreenNames[i] + ")" + "</h3>" +
            "<p>" + tweets[i] + "</p>" +
            "<p>" + "Created At: " + created_at[i] + "</p>" +
            "</div>";

    var marker = new google.maps.Marker({
  		position: location,
  		title: 'Hello World!'
  	});
    var infowindow = new google.maps.InfoWindow();
    bindInfoWindow(marker, ourMap, infowindow, contentString);
    // marker.addListener('click', function() {
    //   infowindow.open(ourMap, this);
    // });
    markers.push(marker);
  }
  markerClusterer.addMarkers(markers)
}

function bindInfoWindow(marker, map, infowindow, html) {
    marker.addListener('click', function() {
        if( prev_infowindow != null ) {
            prev_infowindow.close();
        }
        prev_infowindow = infowindow;
        infowindow.setContent(html);
        infowindow.open(map, this);
    });
}

// Sets the map on all markers in the array.
function setMapOnAll(map) {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}

// Removes the markers from the map, but keeps them in the array.
function clearMarkers() {
  setMapOnAll(null);
}

// Shows any markers currently in the array.
function showMarkers() {
  setMapOnAll(ourMap);
}

// Deletes all markers in the array by removing references to them.
function deleteMarkers() {
  clearMarkers();
  markers = [];
}
