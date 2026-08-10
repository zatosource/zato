'use strict';

// The shared pane split bar - a bar in the flow between two panes, grabbed
// and pulled to share the room between them. The bar carries one pane's size,
// the other side takes whatever is left.
//
// options:
//   bar         - the element grabbed and pulled
//   pane        - the pane whose size the bar carries
//   container   - the element both panes share the room of
//   axis        - 'y' for a pane below the bar growing as it is pulled up,
//                 'x' for a pane at the right growing as it is pulled left
//   minSize     - the least size the pane may be pulled to
//   minOther    - the least room the other side always keeps
//   activeClass - the class the bar wears mid-drag
//   snapSize    - optional, below it the pane snaps shut to nothing
//   storageKey  - optional, where the size is kept between visits
//   apply(size) - optional, how the size lands - the default sets the pane's
//                 own height or width style
//   onSnap(isShut)
//               - optional, told with every applied size whether the pane
//                 stands shut

(function() {

// ////////////////////////////////////////////////////////////////////////

var paneSplit = {};

// ////////////////////////////////////////////////////////////////////////

paneSplit.init = function(options) {

    var bar = options.bar;
    var pane = options.pane;
    var container = options.container;
    var isVertical = options.axis === 'y';

    // What the caller left unsaid
    if (options.snapSize === undefined) { options.snapSize = 0; }
    if (options.storageKey === undefined) { options.storageKey = null; }
    if (options.onSnap === undefined) { options.onSnap = null; }

    if (options.apply === undefined) {
        options.apply = function(size) {
            if (isVertical) {
                pane.style.height = size + 'px';
            }
            else {
                pane.style.width = size + 'px';
            }
        };
    }

// ////////////////////////////////////////////////////////////////////////

    var paneSize = function() {
        var out = isVertical ? pane.offsetHeight : pane.offsetWidth;
        return out;
    };

    // A pane too small to read anything in is shut all the way rather than
    // left ajar - between shut and the least readable size there is nothing
    // to stand at - and neither side gives up the least room it needs
    var clamp = function(size) {

        var containerSize = isVertical ? container.clientHeight : container.clientWidth;
        var maxSize = containerSize - options.minOther;

        var isShut = false;

        if (options.snapSize > 0 && size < options.snapSize) {
            size = 0;
            isShut = true;
        }
        else if (size < options.minSize) {
            size = options.minSize;
        }

        if (size > maxSize) { size = maxSize; }

        var out = {size: size, isShut: isShut};
        return out;
    };

    var setSize = function(size) {
        var landed = clamp(size);

        if (options.onSnap !== null) { options.onSnap(landed.isShut); }
        options.apply(landed.size);

        return landed.size;
    };

// ////////////////////////////////////////////////////////////////////////

    var isPressed = false;
    var startPointer = 0;
    var startSize = 0;
    var currentSize = null;

    // What the pane's own styles would animate - a pane animating its size
    // would trail behind the pointer, so the animation steps aside mid-drag
    var paneTransition = '';

    bar.addEventListener('mousedown', function(event) {

        // Only the main button grabs the bar
        if (event.button !== 0) { return; }

        isPressed = true;
        startPointer = isVertical ? event.clientY : event.clientX;
        startSize = paneSize();

        paneTransition = pane.style.transition;
        pane.style.transition = 'none';

        bar.classList.add(options.activeClass);

        // The pull must not start selecting the page's text
        event.preventDefault();
    });

    window.addEventListener('mousemove', function(event) {
        if (!isPressed) { return; }

        // Pulling the bar away from the pane grows it by the pointer's travel
        var pointer = isVertical ? event.clientY : event.clientX;
        currentSize = setSize(startSize + (startPointer - pointer));
    });

    window.addEventListener('mouseup', function() {
        if (!isPressed) { return; }

        isPressed = false;
        pane.style.transition = paneTransition;
        bar.classList.remove(options.activeClass);

        // The size as pulled to is what gets kept
        if (options.storageKey !== null && currentSize !== null) {
            localStorage.setItem(options.storageKey, String(currentSize));
        }
    });

// ////////////////////////////////////////////////////////////////////////

    // The size the panes open at - what an earlier visit left behind
    if (options.storageKey !== null) {
        var stored = localStorage.getItem(options.storageKey);

        if (stored !== null) {
            currentSize = setSize(parseInt(stored, 10));
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

window.paneSplit = paneSplit;

// ////////////////////////////////////////////////////////////////////////

})();
