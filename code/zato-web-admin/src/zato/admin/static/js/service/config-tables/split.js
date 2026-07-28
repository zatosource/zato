// Config tables - the room the three columns get, across and down.
//
// Across: the listing, the file and the Try it column each take as much of the
// panel as the line next to it is dragged to, either line goes all the way across,
// and a line dragged near the edge it belongs to pulls its own column shut rather
// than leaving a sliver of it. Where each line was left is where it opens the next
// time. The dragging itself is the shared resizer in js/shared/resizer.js.
//
// Down: the panel takes what the window has left under the navigation, less the
// same air below it as there is above it, so each column scrolls inside itself
// instead of the page scrolling as a whole.

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
    tryCollapsedClass: 'config-tables-try-collapsed',

    // Where each of the two splits is kept between visits
    browserStorageKey: 'zato.config-tables.split',
    tryStorageKey: 'zato.config-tables.split-try'
};

// ////////////////////////////////////////////////////////////////////////

split.init = function() {

    var config = split.config;

    split.fitHeight();

    // The window is the only thing that says how much room there is, so it is
    // asked again every time it changes
    $(window).on('resize', split.fitHeight);

    // The listing sits at the start of the row, so its line is on its far side
    split.wire({
        panel: tables.get('browser'),
        handle: tables.get('splitter'),
        edge: 'end',
        storageKey: config.browserStorageKey,
        collapsedClass: config.browserCollapsedClass
    });

    // The Try it column sits at the end of it, so its line is on its near side
    split.wire({
        panel: tables.get('try'),
        handle: tables.get('try-splitter'),
        edge: 'start',
        storageKey: config.tryStorageKey,
        collapsedClass: config.tryCollapsedClass
    });
};

// ////////////////////////////////////////////////////////////////////////

// How tall the page is - what the window has left under whatever sits above the
// page, which is where the navigation and the page's own heading are. How much of
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

            var isCollapsed = percent === 0;
            inputConfig.panel.classList.toggle(inputConfig.collapsedClass, isCollapsed);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
