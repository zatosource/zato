

// /////////////////////////////////////////////////////////////////////////////

// What a row of the log access listing shows - a view record is named by who looked at
// what, so a reader recognizes the line without decoding any event id. Every
// other config event reads the way the default presenter reads it.

(function($) {

var presenterConfig = {

    // The one event type that is a person reading rather than a message moving
    viewEventType: 'content-viewed',

    // The word between the viewer and what they viewed
    viewedWord: 'viewed'
};

$.fn.zato.audit_log.sources['config'] = {

    // The log access rows declare no chips beyond what their columns already say - except
    // the source chip, which the row's own tag already reads, so it is left out
    chips: function(row) {
        var out = [];
        var defaultChips = $.fn.zato.audit_log.sources['default'].chips(row);

        for (var chipIndex = 0; chipIndex < defaultChips.length; chipIndex++) {
            if (defaultChips[chipIndex].key === 'source') {
                continue;
            }

            out.push(defaultChips[chipIndex]);
        }

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    headline: function(row) {

        // A view record written by older code carries no actor - then, like any
        // other config event, it is read the default way. A record that names
        // no viewed object is read that way too - its own object name is the
        // screen the reading happened on, and a screen is not what was viewed.
        if (row.event_type === presenterConfig.viewEventType && row.actor !== '' && row.viewed_object_name !== '') {
            return row.actor + ' ' + presenterConfig.viewedWord + ' ' + row.viewed_object_name;
        }

        return $.fn.zato.audit_log.sources['default'].headline(row);
    },

    // ////////////////////////////////////////////////////////////////////////

    // The log access rows name their records the way the default presenter does
    identityLabel: $.fn.zato.audit_log.sources['default'].identityLabel,

    identity: function(row) {
        return $.fn.zato.audit_log.sources['default'].identity(row);
    }
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
