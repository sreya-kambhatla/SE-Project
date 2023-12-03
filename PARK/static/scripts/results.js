// hourly and monthly buttons that change search parameters
document.addEventListener('DOMContentLoaded', (event) => {
  const hourlyBtn = document.getElementsByClassName('hourly')[0];
  const monthlyBtn = document.getElementsByClassName('monthly')[0];
  const startTime = document.getElementById('start-time');
  const endTime = document.getElementById('end-time');

  hourlyBtn.addEventListener('click', function() {
    hourlyBtn.classList.add('active');
    monthlyBtn.classList.remove('active');
    startTime.style.display = 'inline-block';
    endTime.style.display = 'inline-block';
  });

  monthlyBtn.addEventListener('click', function() {
    monthlyBtn.classList.add('active');
    hourlyBtn.classList.remove('active');
    startTime.style.display = 'none';
    endTime.style.display = 'none';
  });
});




// initalization of map
var bingMap;
// my API key
const BINGKEY = 'AnZmfnNOjVj5o61isXoOcep8SpaYqk3Tpye9-Mgu7iPCGjXntIKrNehxtWSUVzGe';
var locationString; // holds location like 'New York, NY' or just 'New York' as a city

function getLocation() {
  var locationValue = document.getElementById('flaskLocation').getAttribute('flaskLocation');
  var entry = document.getElementById('flaskLocation').getAttribute('userEntry');

  console.log("locationValue:", locationValue, "entry:", entry);
  if (entry === 'False') {
    // Set default values if Flask wasn't used
    locationValue = 'New York, NY';
    entry = 'False';
  } else {
    // If a location was entered, set the value of the location input field
    document.getElementById('location').value = locationValue;
  }
  locationString = locationValue;
  console.log("locationString", locationString);

  // function call to initiate map creation
  processing(locationString);
}
//this code section is for the Update Search and Cancel buttons 
const locationInput = document.getElementById('location');
const updateSearchBtn = document.getElementById('update-search');
const cancelText = document.getElementById('cancel');
const searchContainer = document.querySelector('.search-container');
// can print out these variables if needed

  // making event for when the user changes the location
  // and presses enter/return 
  // causes update search & cancel buttons to appear
  locationInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') { 
      event.preventDefault();
      updateSearchBtn.classList.remove('hidden');
      cancelText.classList.remove('hidden');
      searchContainer.classList.add('show-btn');  

      // if Update Search is pressed, the map is updated
      // and then the new search and cancel buttons and 
      // their containers are then hidden again
      updateSearchBtn.addEventListener('click', function () {
        const enteredLocation = locationInput.value;
        console.log('Updating map based on location:', enteredLocation);
        requestURL = getURL(enteredLocation);

        fetch(requestURL)
          .then(handleResponse)
          .then(handleData)
          .catch(handleError);

        updateSearchBtn.classList.add('hidden');
        cancelText.classList.add('hidden');
        searchContainer.classList.remove('show-btn');
      });

      // if Cancel button is pressed, nothing happens
      // and the Update Search and Cancel buttons are hidden again
      cancelText.addEventListener('click', function () {
        updateSearchBtn.classList.add('hidden');
        cancelText.classList.add('hidden');
        searchContainer.classList.remove('show-btn');
      });
    }
  });

// Function to get the URL for a given location
function getURL(locationString) {
  // construct the URL in a different way as a string
    return `https://dev.virtualearth.net/REST/v1/Locations/${locationString}?include=queryParse&o=json&key=${BINGKEY}`;
}

// function for creation or updating or map
function getMap(coordinates) {
  if (!coordinates) {
    console.error('Cannot update map with undefined coordinates.');
    return;
  }
  console.log('Latitude:', coordinates.latitude);
  console.log('Longitude:', coordinates.longitude);

  // either map will be created here or updated
  if (coordinates.latitude !== undefined && coordinates.longitude !== undefined) {
    // Check if the map is already initialized
    if (bingMap !== undefined) {
      console.log("Map exists")
      // if map exists, update the map view without refreshing
      bingMap.setView({
        center: new Microsoft.Maps.Location(coordinates.latitude, coordinates.longitude),
        zoom: 12
      });
    } else {
      console.log("Map creation")
      // Initialize the map with the initial coordinates
      bingMap = new Microsoft.Maps.Map('#map', {
        credentials: BINGKEY,
        center: new Microsoft.Maps.Location(coordinates.latitude, coordinates.longitude),
        zoom: 12
      });
    }
  } else {
    console.error('Invalid coordinates format for map update.');
  }
}


// Function to handle the response data
function handleData(data) {
  const coordinates = getCoord(data);
  console.log('JSON Response:', data);
  console.log('Coordinates:', coordinates);
  if (coordinates) {
    // Call function to use coordinates, e.g., update the map
    getMap(coordinates);
  } else {
    console.error('Coordinates are undefined.');
  }
}

// Function to handle the JSON response
function handleResponse(response) {
  // Check if the request was successful 
  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }
  // Parse the response as JSON
  return response.json();
}

// Function to handle errors
function handleError(error) {
  console.error('Error:', error);
}

// Function to extract coordinates from the Bing Maps response
function getCoord(data) {
  const firstLocation = data.resourceSets[0]?.resources[0];
  if (firstLocation) {
    const latitude = firstLocation.point.coordinates[0];
    const longitude = firstLocation.point.coordinates[1];
    return { latitude, longitude };
  } else {
    return null;
  }
}

/*
function that essentially handles turning
city,state to coord, to use coord to create map.
*/
function processing(locationString) {
  let requestURL = getURL(locationString);
  console.log('URL: ', requestURL);

// Make an asynchronous request using fetch 
fetch(requestURL)
  .then(handleResponse) 
  .then(handleData)
  .catch(handleError);
}
