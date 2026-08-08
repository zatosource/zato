
// /////////////////////////////////////////////////////////////////////////////

// Weather map - the page. Builds the world out of the inventory the view
// rendered in, keeps it sized to the window, and turns the pointer's moves
// and clicks into the hover and the pinned choice the other modules read.

$.fn.zato.weather_map.map = {};

// /////////////////////////////////////////////////////////////////////////////

(function() {

var cards = $.fn.zato.weather_map.cards;
var geography = $.fn.zato.weather_map.geography;
var render = $.fn.zato.weather_map.render;
var map = $.fn.zato.weather_map.map;

// /////////////////////////////////////////////////////////////////////////////

map.config = {

    // How close to a city the pointer counts as being on it
    cityHitRadius: 16,

    // A pointer merely passing across the map paints nothing - only one
    // that rests somewhere this long does
    hoverShowDelay: 180,

    // Once painted, the way back off onto open water holds this long,
    // so walking between neighbours never blinks
    hoverClearDelay: 150
};

// /////////////////////////////////////////////////////////////////////////////

map.page = null;
map.model = null;

map.frame = null;
map.canvas = null;
map.context = null;

map.state = {

    // What the pointer rests on and what a click chose
    hover: null,
    pinned: null,

    // The pending hover-in and hover-out timers
    showTimer: 0,
    clearTimer: 0,

    // Whether a frame is already on its way to the screen
    drawScheduled: false
};

// /////////////////////////////////////////////////////////////////////////////

// Whether two hits rest on one and the same thing
map.sameHit = function(first, second) {

    if(!first) {
        return !second;
    }
    if(!second) {
        return false;
    }
    if(first.kind !== second.kind) {
        return false;
    }
    if(first.kind === 'city') {
        return first.city === second.city;
    }

    return first.continent === second.continent;
};

// /////////////////////////////////////////////////////////////////////////////

// One frame per screen refresh however many changes asked for it
map.draw = function() {

    if(map.state.drawScheduled) {
        return;
    }

    map.state.drawScheduled = true;

    requestAnimationFrame(function() {
        map.state.drawScheduled = false;
        render.drawScene(map.context, map.model, map.state);
    });
};

// /////////////////////////////////////////////////////////////////////////////

// The world rebuilt to the frame's current size - on load and whenever
// the window changes
map.rebuild = function() {
    var ratio = render.config.pixelRatio;

    var width = map.frame.clientWidth;
    var height = map.frame.clientHeight;

    map.canvas.width = width * ratio;
    map.canvas.height = height * ratio;
    map.canvas.style.width = width + 'px';
    map.canvas.style.height = height + 'px';

    map.model = geography.build(map.page.inventory, width, height);

    render.buildBase(map.model);
    map.draw();
};

// /////////////////////////////////////////////////////////////////////////////

// Where the card of one hit stands - by the city itself, or by the name
// of the continent's own share of the land
map.cardAnchor = function(hit) {

    if(hit.kind === 'city') {
        return {x: hit.city.x, y: hit.city.y};
    }

    return {x: hit.continent.labelX, y: hit.continent.labelY};
};

// /////////////////////////////////////////////////////////////////////////////

// The hover painted - the ring or the coastline, and, while nothing is
// pinned, the card
map.applyHover = function(hit) {
    map.state.hover = hit;

    if(!map.state.pinned) {

        if(hit) {
            var anchor = map.cardAnchor(hit);
            cards.show(hit, anchor.x, anchor.y);
        }
        else {
            cards.hide();
        }
    }

    map.draw();
};

// /////////////////////////////////////////////////////////////////////////////

map.cancelTimers = function() {

    if(map.state.showTimer) {
        clearTimeout(map.state.showTimer);
        map.state.showTimer = 0;
    }

    if(map.state.clearTimer) {
        clearTimeout(map.state.clearTimer);
        map.state.clearTimer = 0;
    }
};

// /////////////////////////////////////////////////////////////////////////////

// What the pointer's every move comes down to - nothing while it only
// passes through, an immediate step while something is already painted,
// and a delayed hover-in otherwise
map.onPointerMove = function(hit) {
    var config = map.config;
    var state = map.state;

    if(map.sameHit(hit, state.hover)) {

        // The pointer is back on what is painted, so any pending way out
        // is no longer wanted
        if(hit) {
            map.cancelTimers();
        }

        return;
    }

    map.cancelTimers();

    // Something is painted already, so this is a walk between neighbours
    // and the paint follows the pointer with no delay
    if(state.hover) {

        if(hit) {
            map.applyHover(hit);
        }
        else {
            state.clearTimer = setTimeout(function() {
                state.clearTimer = 0;
                map.applyHover(null);
            }, config.hoverClearDelay);
        }

        return;
    }

    // Nothing is painted yet - the pointer has to rest a moment first
    if(hit) {
        state.showTimer = setTimeout(function() {
            state.showTimer = 0;
            map.applyHover(hit);
        }, config.hoverShowDelay);
    }
};

// /////////////////////////////////////////////////////////////////////////////

// A click on something pins it, a click on open water lets go
map.onClick = function(hit) {

    map.state.pinned = hit;

    if(hit) {
        var anchor = map.cardAnchor(hit);
        cards.show(hit, anchor.x, anchor.y);
    }
    else {
        cards.hide();
    }

    map.draw();
};

// /////////////////////////////////////////////////////////////////////////////

map.pointerHit = function(event) {
    var rect = map.canvas.getBoundingClientRect();

    var pointX = event.clientX - rect.left;
    var pointY = event.clientY - rect.top;

    var out = geography.hitAt(map.model, pointX, pointY, map.config.cityHitRadius);
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

map.wireEvents = function() {

    map.canvas.addEventListener('mousemove', function(event) {
        var hit = map.pointerHit(event);

        map.canvas.style.cursor = hit ? 'pointer' : 'default';
        map.onPointerMove(hit);
    });

    map.canvas.addEventListener('mouseleave', function() {
        map.cancelTimers();

        if(map.state.hover) {
            map.applyHover(null);
        }
    });

    map.canvas.addEventListener('click', function(event) {
        var hit = map.pointerHit(event);
        map.onClick(hit);
    });

    document.addEventListener('keydown', function(event) {

        if(event.key === 'Escape') {
            if(map.state.pinned) {
                map.onClick(null);
            }
        }
    });

    window.addEventListener('resize', function() {
        map.rebuild();
    });
};

// /////////////////////////////////////////////////////////////////////////////

map.init = function(page) {
    map.page = page;

    map.frame = document.getElementById('weather-map-frame');
    map.canvas = document.getElementById('weather-map-canvas');
    map.context = map.canvas.getContext('2d');

    var card = document.getElementById('weather-map-card');
    var empty = document.getElementById('weather-map-empty');

    // A cluster with nothing configured yet has no world to draw
    if(!page.inventory.length) {
        empty.className = 'weather-map-empty weather-map-empty-visible';
        return;
    }

    cards.init(page, map.frame, card);

    map.rebuild();
    map.wireEvents();
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.weather_map.init = function(page) {
    map.init(page);
};

// /////////////////////////////////////////////////////////////////////////////

})();
