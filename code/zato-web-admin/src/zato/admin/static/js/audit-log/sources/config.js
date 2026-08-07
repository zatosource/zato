

// /////////////////////////////////////////////////////////////////////////////

// What a row of the access log shows - a view record is named by who looked at
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

    // The access log declares no chips beyond what its columns already say
    chips: function(row) {
        return $.fn.zato.audit_log.sources['default'].chips(row);
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

    // The access log names its records the way the default presenter does
    identityLabel: $.fn.zato.audit_log.sources['default'].identityLabel,

    identity: function(row) {
        return $.fn.zato.audit_log.sources['default'].identity(row);
    }
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
