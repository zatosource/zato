// Config tables - how closely the drawing is looked at.
//
// Ctrl and the wheel over the room the answer has draws the mapping set larger or smaller. The
// drawing alone is made larger by it, nothing else on the page, so the columns stay where they
// were put and the drawing scrolls inside its own room once it no longer fits.
//
// The drawing is laid out once, by flow.js, and drawn at whatever size it is being looked at, so
// every shape and every word in it keeps its proportions. How large it was left is kept by the
// browser and is how large the next drawing comes up, here and on the next visit.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var zoom = tables.zoom;
var log = tables.log;

// ////////////////////////////////////////////////////////////////////////

zoom.config = {

    // What one turn of the wheel does to how large the drawing is drawn, and how far that may be
    // taken either way
    step: 1.1,
    least: 0.4,
    most: 3,

    // The size a drawing is drawn at until it is looked at closer, and where the browser keeps
    // the size it was left at
    plain: 1,
    storageKey: 'zato.config-tables.flow-zoom'
};

// ////////////////////////////////////////////////////////////////////////

zoom.state = {

    // How large the drawing is drawn against how large it was laid out, and the size it was laid
    // out at, which is what that is measured off
    level: 1,
    baseWidth: 0,
    baseHeight: 0
};

// ////////////////////////////////////////////////////////////////////////

zoom.init = function() {

    // The whole of the room the answer has answers to the wheel, not only the shapes in it
    tables.get('flow').addEventListener('wheel', zoom.onWheel, {passive: false});

    zoom.state.level = zoom.read();
};

// ////////////////////////////////////////////////////////////////////////

// The size the drawing was laid out at, which every size it is then drawn at is measured off.
zoom.remember = function(width, height) {

    zoom.state.baseWidth = width;
    zoom.state.baseHeight = height;
};

// ////////////////////////////////////////////////////////////////////////

// Ctrl and the wheel is how a drawing is looked at closer or further off. The browser reads that
// as the whole page being made larger, which is not what is being asked for here, so that reading
// is turned down and the drawing alone answers.
zoom.onWheel = function(event) {

    // The wheel on its own scrolls the room the drawing is in, as it does anywhere else
    if(!event.ctrlKey) {
        return;
    }

    event.preventDefault();

    var config = zoom.config;
    var isCloser = event.deltaY < 0;
    var step = isCloser ? config.step : 1 / config.step;
    var level = zoom.clamp(zoom.state.level * step);

    // As close, or as far off, as the drawing goes
    if(level === zoom.state.level) {
        return;
    }

    zoom.state.level = level;
    window.localStorage.setItem(config.storageKey, String(level));

    log.say('zoom.onWheel', {
        isCloser: isCloser,
        level: level,
        baseWidth: zoom.state.baseWidth,
        baseHeight: zoom.state.baseHeight
    });

    zoom.apply();
};

// ////////////////////////////////////////////////////////////////////////

// How large the drawing was last looked at, which is how large it is drawn on the next visit.
zoom.read = function() {

    var config = zoom.config;
    var kept = Number(window.localStorage.getItem(config.storageKey));

    // Nothing kept yet, or something kept that is no size at all
    if(!kept) {
        return config.plain;
    }

    return zoom.clamp(kept);
};

// ////////////////////////////////////////////////////////////////////////

zoom.clamp = function(level) {

    var config = zoom.config;

    if(level < config.least) {
        return config.least;
    }

    if(level > config.most) {
        return config.most;
    }

    return level;
};

// ////////////////////////////////////////////////////////////////////////

// The drawing at the size it is being looked at. The shapes are drawn to the room the drawing is
// given rather than laid out again, so what is on screen only grows or shrinks.
zoom.apply = function() {

    var state = zoom.state;
    var svg = tables.get('flow').querySelector('svg');

    // No drawing on screen, which is every answer that is not a mapping set
    if(svg === null) {
        return;
    }

    svg.style.width = (state.baseWidth * state.level) + 'px';
    svg.style.height = (state.baseHeight * state.level) + 'px';
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
