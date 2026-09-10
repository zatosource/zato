

// /////////////////////////////////////////////////////////////////////////////

// The file transfer presenter, a row reads as its schedule or file and what happened to it.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var fileOutgoing = $.fn.zato.audit_log.fileOutgoing;
var defaultPresenter = $.fn.zato.audit_log.sources['default'];

// /////////////////////////////////////////////////////////////////////////////

// The chips of a file past the connection and the schedule, without the columns the pane reads
// and without the ones the row has already said - the tag names the source and the first chip the connection.
fileOutgoing.fileChips = function(row, defaultChips) {
    var config = fileOutgoing.config;
    var out = [];

    var saidAlready = {};
    saidAlready[config.remotePathKey] = true;
    saidAlready[config.scheduleKey] = true;
    saidAlready[config.runKey] = true;
    saidAlready[config.connectionKey] = true;
    saidAlready[config.sourceKey] = true;

    for (var chipIndex = 0; chipIndex < defaultChips.length; chipIndex++) {
        var chip = defaultChips[chipIndex];

        if (saidAlready[chip.key] === true) {
            continue;
        }

        out.push(chip);
    }

    return out.concat(fileOutgoing.fileExtraChips(row));
};

// /////////////////////////////////////////////////////////////////////////////

// The connection the row belongs to, which every row of this source leads with.
fileOutgoing.connectionChip = function(row) {
    var config = fileOutgoing.config;
    return {key: config.connectionKey, label: '', value: row.object_name, tone: 'neutral'};
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

// What a run is called on the flow page, from the general to the particular - the kind of
// event, the connection and the schedule, since a schedule's name alone names nothing.
fileOutgoing.runTitle = function(row) {
    var parts = [$.fn.zato.audit_log.sourceLabel(row.source), row.object_name, row.schedule];
    return parts.join(fileOutgoing.config.chipSeparator);
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.sources['file-outgoing'] = $.extend({}, defaultPresenter, {

    eventWordAsChip: true,

    rowChipLimit: fileOutgoing.config.rowChipLimit,

    // ////////////////////////////////////////////////////////////////////////

    role: function(_row) {
        return fileOutgoing.config.transferRole;
    },

    // ////////////////////////////////////////////////////////////////////////

    // The row reads from the general to the particular - the connection, its schedule, then what happened.
    chips: function(row) {
        var config = fileOutgoing.config;
        var defaultChips = defaultPresenter.chips(row);
        var out = [fileOutgoing.connectionChip(row)];

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
        return fileOutgoing.fileFacts(rowModel.raw);
    },

    // ////////////////////////////////////////////////////////////////////////

    // A run's Summary is the run's own, a file's is the one every event has.
    summaryFacts: function(rowModel) {
        if (fileOutgoing.isRun(rowModel.raw)) {
            return fileOutgoing.runSummaryFacts(rowModel);
        }

        return defaultPresenter.summaryFacts(rowModel);
    },

    // ////////////////////////////////////////////////////////////////////////

    // A file transfer document is JSON, read once as it stands rather than twice.
    payloadTabs: function() {
        var config = $.fn.zato.audit_log.listing.config;

        var out = [
            {label: config.rawTabLabel, kind: '', parsed: false}
        ];

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    // A run has its files to show and a file has its journey, any other event has nothing more to say.
    hasDetails: function(rowModel) {
        var row = rowModel.raw;

        if (fileOutgoing.isRun(row)) {
            return true;
        }

        return fileOutgoing.hasJourney(row);
    },

    // ////////////////////////////////////////////////////////////////////////

    // The Details tab for the newest of the models.
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

    // A run's card is the run's title and its number, a file's is its name.
    cardTitle: function(row) {
        var config = fileOutgoing.config;

        if (fileOutgoing.isRun(row)) {
            return fileOutgoing.runTitle(row) + config.chipSeparator + config.runWord.toLowerCase() + ' ' + row.current_run;
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

    // What a flow line says after its chip, the step, the size and its duration.
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

    // A run's flow is rooted in the run's title, a file's in its headline.
    hubTitle: function(rowModel) {
        if (fileOutgoing.isRun(rowModel.raw)) {
            return fileOutgoing.runTitle(rowModel.raw);
        }

        return rowModel.headline;
    },

    // A file moving is no exchange - nothing answers a run or a delivery, so there is no reply side to show.
    isExchange: function(_rowModel) {
        return false;
    },

    // ////////////////////////////////////////////////////////////////////////

    // A run's root wears its title as chips - the kind of event in its own ink, the connection and the schedule.
    hubChips: function(rowModel) {
        var config = fileOutgoing.config;
        var row = rowModel.raw;

        if (!fileOutgoing.isRun(row)) {
            return [];
        }

        return [
            {label: $.fn.zato.audit_log.sourceLabel(row.source), kind: config.transferRole},
            {label: row.object_name, kind: config.hubChipKind},
            {label: row.schedule, kind: config.hubChipKind}
        ];
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
