// Config files kit - how closely the drawing is looked at.
//
// Ctrl and the wheel over the room the answer has draws the mapping set larger or smaller. The
// mechanics of that are the kit's draw_zoom - this file only says which room answers to the
// wheel, where the browser keeps the size the drawing was left at, and that what the zoom does
// is logged the way everything else on this page is.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.config_files;
var log = tables.log;

// ////////////////////////////////////////////////////////////////////////

tables.zoom = $.fn.zato.dashboard_kit.draw_zoom.create({

    // The whole of the room the answer has answers to the wheel, not only the shapes in it
    host: function() {
        return tables.get('flow');
    },

    // Where the browser keeps the size the drawing was left at. The drawing belongs to the
    // Translate column, which only the Config tables screen has, so the key is that screen's.
    storage_key: 'zato.config-tables.flow-zoom',

    log: log.say
});

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
