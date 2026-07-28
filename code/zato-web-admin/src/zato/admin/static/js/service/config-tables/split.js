// Config tables - the room the three columns get, across and down.
//
// Across: the listing, the file and the Translate column each take as much of the
// panel as the line next to it is dragged to, either line goes all the way across,
// and a line dragged near the edge it belongs to pulls its own column shut rather
// than leaving a sliver of it. Where each line was left is where it opens the next
// time. The dragging itself is the shared resizer in js/shared/resizer.js.
//
// Down: the panel takes what the window has left under the navigation, less the
// same air below it as there is above it, so each column scrolls inside itself
// instead of the page scrolling as a whole.
//
// A listing narrowed towards nothing gives up what is around the file names before it gives
// up the names themselves, so what is left of it is still a listing of files.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var split = tables.split;

// ////////////////////////////////////////////////////////////////////////

split.config = {

    // How far either line may be dragged, and how far one arrow key press moves it
    minPercent: 0,
    maxPercent: 100,
    keyboardStepPercent: 2,

    // The class a line wears while it is being dragged
    activeClass: 'config-tables-splitter-active',

    // A drag that ends up this near a column's own edge shuts that column
    collapseAtPercent: 8,

    // The class a column wears while it is shut
    browserCollapsedClass: 'config-tables-browser-collapsed',
    translateCollapsedClass: 'config-tables-translate-collapsed',

    // How narrow the listing has to be before it gives up each part of itself, in pixels,
    // and the class it wears once it has - what a file holds goes first and the badge
    // saying what kind of file it is goes last, so the name is on screen the longest
    hideCountAtPx: 230,
    hideButtonsAtPx: 210,
    hideHeadingAtPx: 170,
    hideBadgeAtPx: 130,

    hideCountClass: 'config-tables-browser-hide-count',
    hideButtonsClass: 'config-tables-browser-hide-buttons',
    hideHeadingClass: 'config-tables-browser-hide-heading',
    hideBadgeClass: 'config-tables-browser-hide-badge',

    // Where each of the two splits is kept between visits
    browserStorageKey: 'zato.config-tables.split',
    translateStorageKey: 'zato.config-tables.split-translate'
};

// ////////////////////////////////////////////////////////////////////////

split.init = function() {

    var config = split.config;

    split.fitHeight();

    // The window is the only thing that says how much room there is, so it is
    // asked again every time it changes
    $(window).on('resize', split.onWindowResize);

    // The listing sits at the start of the row, so its line is on its far side
    split.wire({
        panel: tables.get('browser'),
        handle: tables.get('splitter'),
        edge: 'end',
        storageKey: config.browserStorageKey,
        applied: split.applyBrowser
    });

    // The Translate column sits at the end of it, so its line is on its near side
    split.wire({
        panel: tables.get('translate-panel'),
        handle: tables.get('translate-splitter'),
        edge: 'start',
        storageKey: config.translateStorageKey,
        applied: split.applyTranslate
    });

    // The listing opens at the width it was left at, which says as much about what it has
    // room for as a drag of it does
    split.applyListing();
};

// ////////////////////////////////////////////////////////////////////////

split.onWindowResize = function() {

    split.fitHeight();

    // Each column is as wide a share of the panel as it was, and the panel follows the
    // window, so the listing may have room for more or for less of itself than it had
    split.applyListing();
};

// ////////////////////////////////////////////////////////////////////////

split.applyBrowser = function(percent) {

    var panel = tables.get('browser');

    panel.classList.toggle(split.config.browserCollapsedClass, percent === 0);
    split.applyListing();
};

// ////////////////////////////////////////////////////////////////////////

split.applyTranslate = function(percent) {

    var panel = tables.get('translate-panel');

    panel.classList.toggle(split.config.translateCollapsedClass, percent === 0);
};

// ////////////////////////////////////////////////////////////////////////

// What the listing has room for at the width it is now. Everything around the names goes
// before the names do, each part of it at its own width, so the listing thins out rather
// than being cut off at the side.
split.applyListing = function() {

    var config = split.config;
    var panel = tables.get('browser');
    var width = panel.getBoundingClientRect().width;

    panel.classList.toggle(config.hideCountClass, width < config.hideCountAtPx);
    panel.classList.toggle(config.hideButtonsClass, width < config.hideButtonsAtPx);
    panel.classList.toggle(config.hideHeadingClass, width < config.hideHeadingAtPx);
    panel.classList.toggle(config.hideBadgeClass, width < config.hideBadgeAtPx);
};

// ////////////////////////////////////////////////////////////////////////

// How tall the page is - what the window has left under the navigation and the
// page's own heading, both of which sit above the panel. How much of
// that the columns themselves get is then the panel's own business.
split.fitHeight = function() {

    var container = tables.get('container');
    var top = container.getBoundingClientRect().top;

    container.style.height = (window.innerHeight - top) + 'px';
};

// ////////////////////////////////////////////////////////////////////////

split.wire = function(inputConfig) {

    var config = split.config;

    $.fn.zato.resizer.init({

        container: tables.get('content-area'),
        first: inputConfig.panel,
        handles: [inputConfig.handle],
        axis: 'x',
        edge: inputConfig.edge,

        minPercent: config.minPercent,
        maxPercent: config.maxPercent,
        keyboardStepPercent: config.keyboardStepPercent,
        activeClass: config.activeClass,

        // Browser storage is an external boundary, so an empty one is answered
        // explicitly - the column then opens at the width its styles give it
        read: function() {

            var saved = localStorage.getItem(inputConfig.storageKey);

            if(saved === null) {
                return null;
            }

            return parseFloat(saved);
        },

        write: function(percent) {
            localStorage.setItem(inputConfig.storageKey, String(percent));
        },

        // A drag that comes near the column's own edge is pulled the rest of the
        // way, so the column shuts rather than being left as a sliver. Keys step
        // where they are told, which is how a shut column is opened again.
        snap: function(percent, isDragging) {

            if(isDragging && percent < config.collapseAtPercent) {
                return 0;
            }

            return percent;
        },

        applied: function(percent) {
            inputConfig.applied(percent);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
