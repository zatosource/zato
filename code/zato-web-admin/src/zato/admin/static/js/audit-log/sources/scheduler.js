

// /////////////////////////////////////////////////////////////////////////////

// What a row of the scheduler shows - a run is named by the job that ran, so a
// reader recognizes the line without decoding any correlation id. Everything
// else reads the way the default presenter reads it.

(function($) {

$.fn.zato.audit_log.sources['scheduler'] = {

    // The scheduler's rows already wear its name on the role tag, so the source
    // chip saying it again is left out - every other chip reads the default way
    chips: function(row) {
        var chips = $.fn.zato.audit_log.sources['default'].chips(row);
        var out = [];

        for (var chipIndex = 0; chipIndex < chips.length; chipIndex++) {
            var chip = chips[chipIndex];

            if (chip.key === 'source') {
                continue;
            }

            out.push(chip);
        }

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    headline: function(row) {

        // A run is known by its job's name - a run of a job that somehow has
        // none is read the default way, by the cid it travelled under
        if (row.object_name !== '') {
            return row.object_name;
        }

        return $.fn.zato.audit_log.sources['default'].headline(row);
    },

    // ////////////////////////////////////////////////////////////////////////

    // The scheduler names its records the way the default presenter does
    identityLabel: $.fn.zato.audit_log.sources['default'].identityLabel,

    identity: function(row) {
        return $.fn.zato.audit_log.sources['default'].identity(row);
    }
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
