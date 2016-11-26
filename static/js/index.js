// DOM Management
$( document ).ready(function() {
    $('#searchButton').on('click', keywordSearch);
    startTweetUpdateSse()
});

// Global variables:
var currentKeyword = null;
var newTweetsSinceStarted = 0;

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
var coordinatesLat = [];
var coordinatesLng = [];
var createdAt = [];
var userNames = [];
var userScreenNames = [];
var tweets = [];
var sentiments = [];
var markers = [];
var prevInfowindow = null;


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
  currentKeyword = null;
  coordinatesLat = [];
  coordinatesLng = [];
  createdAt = [];
  tweets = [];
  userNames = [];
  userScreenNames = [];
  prevInfowindow = null;
  deleteMarkers();
  markerClusterer.clearMarkers();
}
//handle the search part
function httpGetAsync(theUrl, keyword) {
  resetVariables();
  currentKeyword = keyword;
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
      coordinatesLng.push(tweet.coordinates[0]);
      coordinatesLat.push(tweet.coordinates[1]);
      createdAt.push(tweet.created_at);
      tweets.push(tweet.text);
      createdAt.push(tweet.created_at);
      userNames.push(tweet.user_name);
      userScreenNames.push(tweet.user_screen_name);
      sentiments.push(tweet.sentiment);
  }
  generateMarkers();
}

function generateMarkers() {
  for (var i = 0; i < tweets.length; i++) {
    var location = {
      lat: parseFloat(coordinatesLat[i]),
      lng: parseFloat(coordinatesLng[i])
    };

    var contentString = '<div id="content">'+
            "<h3>" + userNames[i] + " (@" + userScreenNames[i] + ")" + "</h3>" +
            "<p>" + tweets[i] + "</p>" +
            "<p>" + "Created At: " + createdAt[i] + "</p>" +
            "</div>";

    var redMarkerIcon = 'images/pin-red.png';
    var greenMarkerIcon = 'images/pin-green.png';
    var yellowMarkerIcon = 'images/pin-yellow.png';

    var marker = new google.maps.Marker({
  		position: location
  	});

    var sentiment = sentiments[i]
    if (sentiment == 'positive') {
      marker.setIcon(redMarkerIcon);
    } else if (sentiment == 'negative') {
      marker.setIcon(greenMarkerIcon);
    } else {
      marker.setIcon(yellowMarkerIcon);
    }

    var infowindow = new google.maps.InfoWindow();
    bindInfoWindow(marker, ourMap, infowindow, contentString);
    markers.push(marker);
  }
  markerClusterer.addMarkers(markers);
}

function bindInfoWindow(marker, map, infowindow, html) {
    marker.addListener('click', function() {
        if( prevInfowindow != null ) {
            prevInfowindow.close();
        }
        prevInfowindow = infowindow;
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


// Event Source
function addMarker(tweet) {
  coordinatesLng.push(tweet.coordinates[0]);
  coordinatesLat.push(tweet.coordinates[1]);
  createdAt.push(tweet.created_at);
  tweets.push(tweet.text);
  createdAt.push(tweet.created_at);
  userNames.push(tweet.user_name);
  userScreenNames.push(tweet.user_screen_name);
  sentiments.push(tweet.sentiment);

  // BE CAREFUL: the lat and lng are different in map and tweeter
  var location = {
    lat: parseFloat(tweet.coordinates[1]),
    lng: parseFloat(tweet.coordinates[0])
  };

  var contentString = '<div id="content">'+
          "<h3>" + tweet.user_name + " (@" + tweet.user_screen_name + ")" + "</h3>" +
          "<p>" + tweet.text + "</p>" +
          "<p>" + "Created At: " + tweet.created_at + "</p>" +
          "</div>";

  var redMarkerIcon = 'images/pin-red.png';
  var greenMarkerIcon = 'images/pin-green.png';
  var yellowMarkerIcon = 'images/pin-yellow.png';

  var marker = new google.maps.Marker({
    position: location
  });

  var sentiment = tweet.sentiment;
  if (sentiment == 'positive') {
    marker.setIcon(redMarkerIcon);
  } else if (sentiment == 'negative') {
    marker.setIcon(greenMarkerIcon);
  } else {
    marker.setIcon(yellowMarkerIcon);
  }

  var infowindow = new google.maps.InfoWindow();
  bindInfoWindow(marker, ourMap, infowindow, contentString);
  markers.push(marker);
  markerClusterer.addMarker(marker);
}

function startTweetUpdateSse() {
  var source = new EventSource('/newtweetupdate/');
  source.onmessage = function(e) {
    if (e.data != "nothing") {
      newTweetsSinceStarted = newTweetsSinceStarted + 1;
      $('#updateNum')[0].innerHTML = newTweetsSinceStarted;
      if (currentKeyword != null) {
        tweetJson = JSON.parse(e.data);
        if (tweetJson.text.includes(currentKeyword)) {
          addMarker(tweetJson);
        }
      }
    }
  };
}
