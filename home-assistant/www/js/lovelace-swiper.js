//Config
const swiperWrapAround = true;
const swiperHorizontalSwipeIgnore = 20;

var xDown = null;
var xUp = null;
var yDown = null;
var yUp = null;

const paperTabs = document.querySelectorAll('home-assistant')[0].shadowRoot.querySelector('home-assistant-main').shadowRoot.querySelector('app-drawer-layout').querySelector('ha-panel-lovelace').shadowRoot.querySelector('hui-root').shadowRoot.querySelectorAll('paper-tab');
const numberOfTabs = paperTabs.length;

document.body.addEventListener('touchstart', handleTouchStart, false);
document.body.addEventListener('touchmove', storeTouchMove, false);
document.body.addEventListener('touchend', handleTouchEnd, false);

function getCurrentTabIndex() {
  for (let i = 0; i < numberOfTabs; i++) { 
    if(paperTabs[i].classList.contains('iron-selected')) {
      return i;
    }
  }
}

function getTouches(evt) {
  return evt.touches ||        // browser API
    evt.originalEvent.touches; // jQuery
}

function handleTouchStart(evt) {
  xDown = getTouches(evt)[0].clientX;
  yDown = getTouches(evt)[0].clientY;
  xUp = xDown;
  yUp = yDown;
}

function storeTouchMove(evt) {
  xUp = getTouches(evt)[0].clientX;
  yUp = getTouches(evt)[0].clientY;
}

function handleTouchEnd(evt) {
    if(!xUp || !yUp) {
      return;
    }
    evt.stopPropagation();
    var xDiff = xDown - xUp;
    var yDiff = yDown - yUp;
    if (Math.abs(xDiff) < swiperHorizontalSwipeIgnore) {
      //ignore minor swipe horizontal
      return;
    }
    if (Math.abs(xDiff) > Math.abs(yDiff)) {
    var currentIndex = getCurrentTabIndex();
    var targetIndex = currentIndex;
    if (xDiff > 0) {
      /* right to left swipe */
      if(currentIndex === numberOfTabs-1) {
		if(!swiperWrapAround) {
		  return;
		}
		targetIndex = 0;
      } else {
        targetIndex = currentIndex+1;
      }
    } else {
      /* left to right swipe */
      if(currentIndex === 0) {
		if(!swiperWrapAround) {
		  return;
		}
		targetIndex = numberOfTabs-1;
      } else {
        targetIndex = currentIndex-1;
      }
    }
    paperTabs[targetIndex].dispatchEvent(new MouseEvent('click', {shiftKey: true}));
  }
  xDown = null;
  xUp = null;
  yDown = null;
  yUp = null;
}