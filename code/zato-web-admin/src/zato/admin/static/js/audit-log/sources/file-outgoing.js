

// /////////////////////////////////////////////////////////////////////////////

// What a row of a file transfer shows - the schedule that ran comes first and by its
// bare name, the way a scheduler row is known by its job, and what the run did reads
// after it as a chip of its own. The remote path is read in the pane, not on the row -
// every row of one listing walks the same directory, so it says nothing that tells
// the rows apart.

(function($) {

var fileOutgoing = {

    config: {

        // The column whose value stands on its own, with no label before it
        scheduleKey: 'schedule',

        // The column left to the pane
        remotePathKey: 'endpoint'
    }
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.sources['file-outgoing'] = {

    // The event word is a chip following the others - a row reads as the schedule,
    // then what happened to it
    eventWordAsChip: true,

    // ////////////////////////////////////////////////////////////////////////

    chips: function(row) {
        var config = fileOutgoing.config;
        var chips = $.fn.zato.audit_log.sources['default'].chips(row);
        var out = [];

        // The schedule leads whatever column order the page declares
        for (var scheduleIndex = 0; scheduleIndex < chips.length; scheduleIndex++) {
            var scheduleChip = chips[scheduleIndex];

            if (scheduleChip.key === config.scheduleKey) {
                scheduleChip.label = '';
                out.push(scheduleChip);
            }
        }

        for (var chipIndex = 0; chipIndex < chips.length; chipIndex++) {
            var chip = chips[chipIndex];

            if (chip.key === config.remotePathKey) {
                continue;
            }

            if (chip.key === config.scheduleKey) {
                continue;
            }

            out.push(chip);
        }

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    headline: function(row) {
        return $.fn.zato.audit_log.sources['default'].headline(row);
    },

    // ////////////////////////////////////////////////////////////////////////

    // A file transfer names its records the way the default presenter does
    identityLabel: $.fn.zato.audit_log.sources['default'].identityLabel,

    identity: function(row) {
        return $.fn.zato.audit_log.sources['default'].identity(row);
    }
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
