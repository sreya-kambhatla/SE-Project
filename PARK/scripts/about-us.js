//getting and storing the carousel items (larger-pfps and text) 
//doing the same for the smaller-pfps
var items = document.getElementsByClassName('carousel-item');
var smallPfps = document.getElementsByClassName('pfp');
var currentIndex = 0; // index of which item is currently displayed

// function hides all others but the current showing pfp and related text
function updateCarousel() {
    for (var i = 0; i < items.length; i++) {
        items[i].style.display = 'none';
    }
    items[currentIndex].style.display = 'block';
}

//currentIndex can be changed automatically
//by clicking the small pfp
// in essence that person's larger-pfp and text will be shown
for (let i = 0; i < smallPfps.length; i++) {
    smallPfps[i].onclick = function() {
        currentIndex = i;
        updateCarousel();
    };
}

// making left and right arrow buttons to control
// the carousel manually in numerical order
document.getElementById('prev').onclick = function() {
    currentIndex = (currentIndex > 0) ? currentIndex - 1 : items.length - 1;
    updateCarousel();
};

document.getElementById('next').onclick = function() {
    currentIndex = (currentIndex < items.length - 1) ? currentIndex + 1 : 0;
    updateCarousel();
}

updateCarousel();
