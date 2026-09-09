

// /////////////////////////////////////////////////////////////////////////////

// The file transfer presenter, a row reads as its schedule or file and what happened to it.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var fileOutgoing = $.fn.zato.audit_log.fileOutgoing;
var defaultPresenter = $.fn.zato.audit_log.sources['default'];

// /////////////////////////////////////////////////////////////////////////////

// The default chips with the schedule first and without the columns the pane reads.
fileOutgoing.fileChips = function(row, defaultChips) {
    var config = fileOutgoing.config;
    var out = [];

    for (var chipIndex = 0; chipIndex < defaultChips.length; chipIndex++) {
        var chip = defaultChips[chipIndex];

        if (chip.key === config.remotePathKey) {
            continue;
        }

        if (chip.key === config.scheduleKey) {
            continue;
        }

        if (chip.key === config.runKey) {
            continue;
        }

        out.push(chip);
    }

    return out.concat(fileOutgoing.fileExtraChips(row));
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.runChips = function(row) {
    var out = [];

    out.push(fileOutgoing.runChip(row));

    var expectedChip = fileOutgoing.expectedChip(row);

    if (expectedChip !== null) {
        out.push(expectedChip);
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// Whether a row has steps of its own, a run has a summary instead and a connection row other than a store has neither.
fileOutgoing.hasJourney = function(row) {
    if (row.event_type !== fileOutgoing.config.connectionEvent) {
        return true;
    }

    return fileOutgoing.isStore(row);
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.lineWord = function(row) {
    var config = fileOutgoing.config;

    if (fileOutgoing.isRun(row)) {
        return config.runWord;
    }

    if (row.event_type === config.connectionEvent) {
        return row.operation;
    }

    return $.fn.zato.audit_log.eventLabel(row.event_type);
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.sources['file-outgoing'] = $.extend({}, defaultPresenter, {

    eventWordAsChip: true,

    rowChipLimit: fileOutgoing.config.rowChipLimit,

    // ////////////////////////////////////////////////////////////////////////

    chips: function(row) {
        var config = fileOutgoing.config;
        var defaultChips = defaultPresenter.chips(row);
        var out = [];

        for (var scheduleIndex = 0; scheduleIndex < defaultChips.length; scheduleIndex++) {
            var scheduleChip = defaultChips[scheduleIndex];

            if (scheduleChip.key === config.scheduleKey) {
                scheduleChip.label = '';
                out.push(scheduleChip);
            }
        }

        if (fileOutgoing.isRun(row)) {
            return out.concat(fileOutgoing.runChips(row));
        }

        return out.concat(fileOutgoing.fileChips(row, defaultChips));
    },

    // ////////////////////////////////////////////////////////////////////////

    // A run's event word is its status word in the status tone.
    eventChip: function(rowModel, chip) {
        var words = fileOutgoing.words();
        var row = rowModel.raw;

        if (!fileOutgoing.isRun(row)) {
            return chip;
        }

        chip.text = words.run_status_label[row.status];
        chip.tone = words.run_status_tone[row.status];

        return chip;
    },

    // ////////////////////////////////////////////////////////////////////////

    sentence: fileOutgoing.sentence,

    // ////////////////////////////////////////////////////////////////////////

    // A run's remote path is the directory it walked.
    attrLabel: function(rowModel, attr) {
        var labels = fileOutgoing.words().default_view_labels;

        if (attr.key === fileOutgoing.config.remotePathKey) {
            if (fileOutgoing.isRun(rowModel.raw)) {
                return labels.remote_path;
            }
        }

        return '';
    },

    // ////////////////////////////////////////////////////////////////////////

    // A run's Status line reads the status word.
    attrValueHTML: function(rowModel, attr) {
        var words = fileOutgoing.words();

        if (attr.key !== 'status') {
            return null;
        }

        if (!fileOutgoing.isRun(rowModel.raw)) {
            return null;
        }

        return fileOutgoing.escapeHTML(words.run_status_label[attr.value]);
    },

    // ////////////////////////////////////////////////////////////////////////

    detailFacts: function(rowModel) {
        var row = rowModel.raw;

        if (fileOutgoing.isRun(row)) {
            return fileOutgoing.runFacts(row);
        }

        return fileOutgoing.fileFacts(row);
    },

    // ////////////////////////////////////////////////////////////////////////

    // The panel under the pane's head for the newest of the models.
    detailPanel: function(models, $host, variant) {
        var rowModel = models[models.length - 1];
        var row = rowModel.raw;

        if (fileOutgoing.isRun(row)) {
            fileOutgoing.renderRunSummary(rowModel, $host, variant);
            return;
        }

        if (fileOutgoing.hasJourney(row)) {
            fileOutgoing.renderJourney(rowModel, $host, variant);
            return;
        }

        $host.html('');
    },

    // ////////////////////////////////////////////////////////////////////////

    // Everything under one cid is one card.
    cardKey: function(row) {
        return row.cid;
    },

    // ////////////////////////////////////////////////////////////////////////

    // A run's card is its schedule and number, a file's is its name.
    cardTitle: function(row) {
        var config = fileOutgoing.config;

        if (fileOutgoing.isRun(row)) {
            return row.schedule + config.chipSeparator + config.runWord.toLowerCase() + ' ' + row.current_run;
        }

        if (row.file_name !== '') {
            return row.file_name;
        }

        if (row.endpoint !== '') {
            return row.endpoint.split('/').pop();
        }

        return row.object_name;
    },

    // ////////////////////////////////////////////////////////////////////////

    // What a flow line says after its chip, the step, the size and the time it took.
    lineNote: function(model) {
        var row = model.raw;
        var parts = [];

        parts.push(fileOutgoing.lineWord(row));

        if (row.size > 0) {
            parts.push(fileOutgoing.sizeText(row.size));
        }

        if (row.duration_ms > 0) {
            parts.push(kit.format_duration_ms(row.duration_ms));
        }

        return parts.join(fileOutgoing.config.chipSeparator);
    },

    // ////////////////////////////////////////////////////////////////////////

    lineTooltip: function(model) {
        var row = model.raw;

        if (row.error !== '') {
            return fileOutgoing.errorSummary(row.error);
        }

        return fileOutgoing.sentence(row);
    },

    // ////////////////////////////////////////////////////////////////////////

    // The same content having gone out before is what a resubmit is warned about.
    resubmitWarning: function(rowModel) {
        var config = fileOutgoing.config;
        var row = rowModel.raw;

        if (row.delivered_count_for_checksum > 1) {
            return fileOutgoing.fill(config.resubmitWarningText, {
                count: row.delivered_count_for_checksum,
                when: kit.format_local_time(row.last_delivered_iso_for_checksum)});
        }

        if (row.event_type === config.deliveredEvent) {
            return fileOutgoing.fill(config.resubmitDeliveredOnceText, {when: kit.format_local_time(row.event_time_iso)});
        }

        return '';
    },

    // ////////////////////////////////////////////////////////////////////////

    headline: function(row) {
        if (fileOutgoing.isRun(row)) {
            return row.schedule;
        }

        if (row.file_name !== '') {
            return row.file_name;
        }

        return defaultPresenter.headline(row);
    }
});

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
