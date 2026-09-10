

// /////////////////////////////////////////////////////////////////////////////

// The facts a file transfer row adds to the pane's Summary tab, the facts a run's Summary tab is made of
// and the facts a run's Details tab opens with.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var fileOutgoing = $.fn.zato.audit_log.fileOutgoing;

// /////////////////////////////////////////////////////////////////////////////

// One fact, its label out of the word table and its value already escaped.
fileOutgoing.fact = function(key, valueHTML, copyValue, searchValue) {
    var listing = $.fn.zato.audit_log.listing;
    var label = fileOutgoing.words().default_view_labels[key];

    return listing.paneFact(label, valueHTML, copyValue, searchValue);
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.textFact = function(key, value) {
    var text = String(value);
    return fileOutgoing.fact(key, fileOutgoing.escapeHTML(text), text, '');
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.durationFact = function(key, ms) {
    var text = kit.format_duration_ms(ms);
    return fileOutgoing.fact(key, fileOutgoing.escapeHTML(text), text, '');
};

// /////////////////////////////////////////////////////////////////////////////

// A fact naming another event, which opens it.
fileOutgoing.eventFact = function(key, text, eventId) {
    var idText = String(eventId);

    var valueHTML = '<a href="javascript:void(0)" class="audit-log-lineage" data-lineage-id="' + idText + '">' +
        fileOutgoing.escapeHTML(text) + '</a>';

    return fileOutgoing.fact(key, valueHTML, idText, '');
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.yesNo = function(value) {
    var config = fileOutgoing.config;

    if (value) {
        return config.yesText;
    }

    return config.noText;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.runningFact = function(row) {
    var phaseWord = fileOutgoing.phaseWord(row);

    if (row.current_file !== '') {
        phaseWord += ' ' + row.current_file;
    }

    return fileOutgoing.textFact('phase', phaseWord);
};

// /////////////////////////////////////////////////////////////////////////////

// The directory the run listed, in full.
fileOutgoing.directoryFact = function(row) {
    return fileOutgoing.textFact('remote_path', row.endpoint);
};

// /////////////////////////////////////////////////////////////////////////////

// The tone of one file count - a count of nothing is muted, a moving count is in the running ink,
// and a settled one in the ink its kind has.
fileOutgoing.fileFilterTone = function(filter, count, isRunning) {
    if (count === 0) {
        return 'muted';
    }

    if (isRunning) {
        if (filter.movesWhileRunning) {
            return 'running';
        }
    }

    return filter.tone;
};

// /////////////////////////////////////////////////////////////////////////////

// The files of a run as chips, one to a count, each narrowing the ledger down to the entries it counts.
fileOutgoing.filesFact = function(row) {
    var config = fileOutgoing.config;
    var labels = fileOutgoing.words().default_view_labels;
    var isRunning = row.status === config.runningStatus;
    var chips = [];
    var copyParts = [];

    for (var filterIndex = 0; filterIndex < config.fileFilters.length; filterIndex++) {
        var filter = config.fileFilters[filterIndex];
        var count = row[filter.key];
        var label = labels[filter.key];

        chips.push({key: filter.key, label: label, count: count,
            tone: fileOutgoing.fileFilterTone(filter, count, isRunning), decisions: filter.decisions});

        copyParts.push(count + ' ' + label.toLowerCase());
    }

    var copyValue = copyParts.join(config.chipSeparator);

    return fileOutgoing.fact('files', kit.runSummary.filterChipsHTML(chips), copyValue, '');
};

// /////////////////////////////////////////////////////////////////////////////

// The facts of a run's Details tab - what it is doing while it runs, where it looked and what it found there.
fileOutgoing.runDetailFacts = function(row) {
    var config = fileOutgoing.config;
    var out = [];

    if (row.status === config.runningStatus) {
        out.push(fileOutgoing.runningFact(row));
    }

    out.push(fileOutgoing.directoryFact(row));
    out.push(fileOutgoing.filesFact(row));

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// What a run is as one line of chips - the kind of event, the schedule it ran for and how it went.
fileOutgoing.runEventFact = function(rowModel) {
    var config = fileOutgoing.config;
    var listing = $.fn.zato.audit_log.listing;
    var row = rowModel.raw;

    var scheduleChip = kit.chips.render_one({key: config.scheduleKey, label: '', value: row.schedule, tone: 'neutral'});

    // The row stands on the pane's dark frame, so the tag is drawn in its dark reading.
    var roleTag = kit.role.tag(rowModel.role, rowModel.eventLabel, listing.config.paneFactVariant);

    var valueHTML = '<span class="audit-log-pane-event-chips">' + roleTag + scheduleChip +
        listing.outcomeBadgeHTML(rowModel) + '</span>';

    var copyValue = [kit.role.config.labels[rowModel.role], row.schedule, rowModel.outcome].join(config.chipSeparator);

    return listing.paneFact(listing.config.eventLabel, valueHTML, copyValue, '');
};

// /////////////////////////////////////////////////////////////////////////////

// The facts of a run's Summary tab - what it is, how it went, when, what state it ended in and its
// duration, its note and its error only when it has them.
fileOutgoing.runSummaryFacts = function(rowModel) {
    var listing = $.fn.zato.audit_log.listing;
    var listingConfig = listing.config;
    var words = fileOutgoing.words();
    var row = rowModel.raw;
    var out = [fileOutgoing.runEventFact(rowModel)];

    var outcomeHTML = listing.paneAttrValueHTML(rowModel, {key: 'outcome', value: rowModel.outcome});
    out.push(listing.paneFact(listingConfig.outcomeLabel, outcomeHTML, rowModel.outcome, ''));

    out.push(listing.paneFact(listingConfig.timeLabel, kit.time_scrub.stamp(rowModel.timeIso), rowModel.timeLocal, ''));

    var statusLabel = words.run_status_label[row.status];
    out.push(listing.paneFact(listingConfig.statusLabel, fileOutgoing.escapeHTML(statusLabel), statusLabel, row.status));

    if (rowModel.durationMs > 0) {
        var durationText = kit.format_duration_ms(rowModel.durationMs);
        out.push(listing.paneFact(listingConfig.durationLabel, fileOutgoing.escapeHTML(durationText), durationText, ''));
    }

    if (row.list_ms) {
        out.push(fileOutgoing.durationFact('list_ms', row.list_ms));
    }

    if (row.note !== '') {
        out.push(fileOutgoing.textFact('note', row.note));
    }

    if (row.error !== '') {
        out.push(fileOutgoing.textFact('error', fileOutgoing.errorSummary(row.error)));
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.seenBeforeFact = function(row) {
    var text = fileOutgoing.fill(fileOutgoing.config.seenBeforeText, {
        when: kit.format_local_time(row.seen_before_iso), file_name: row.seen_before_file_name});

    return fileOutgoing.eventFact('seen_before', text, row.seen_before_event_id);
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.deliveredBeforeFact = function(row) {
    var config = fileOutgoing.config;
    var listing = $.fn.zato.audit_log.listing;

    var text = fileOutgoing.fill(config.deliveredBeforeText, {
        count: row.delivered_count_for_checksum,
        when: kit.format_local_time(row.last_delivered_iso_for_checksum)});

    return listing.paneFact(config.deliveredBeforeLabel, fileOutgoing.escapeHTML(text), text, row.checksum);
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.timingFacts = function(row) {
    var out = [];

    if (row.read_ms) {
        out.push(fileOutgoing.durationFact('read_ms', row.read_ms));
    }

    if (row.service_ms) {
        out.push(fileOutgoing.durationFact('service_ms', row.service_ms));
    }

    if (row.ack_ms) {
        out.push(fileOutgoing.durationFact('ack_ms', row.ack_ms));
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.storeFacts = function(row) {
    var out = [];

    if (row.remote_size) {
        out.push(fileOutgoing.textFact('remote_size', kit.format_number_full(row.remote_size)));
    }

    if (row.verify_how !== '') {
        out.push(fileOutgoing.textFact('verified', row.verify_how));
    }

    if (row.verify_ms) {
        out.push(fileOutgoing.durationFact('verify_ms', row.verify_ms));
    }

    if (row.mismatch !== '') {
        out.push(fileOutgoing.textFact('error', row.mismatch));
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.fileFacts = function(row) {
    var config = fileOutgoing.config;
    var out = [];

    if (row.attempt) {
        out.push(fileOutgoing.textFact('attempt', fileOutgoing.attemptText(row)));
    }

    if (row.attempts) {
        out.push(fileOutgoing.textFact('attempt', row.attempts));
    }

    out = out.concat(fileOutgoing.timingFacts(row));

    if (row.moved_to !== '') {
        out.push(fileOutgoing.textFact('moved_to', row.moved_to));
    }

    if (row.deleted !== '') {
        out.push(fileOutgoing.textFact('deleted', config.yesText));
    }

    if (row.claim_released !== '') {
        out.push(fileOutgoing.textFact('claim_released', fileOutgoing.yesNo(row.claim_released)));
    }

    if (row.seen_before_event_id) {
        out.push(fileOutgoing.seenBeforeFact(row));
    }

    if (row.delivered_count_for_checksum > 1) {
        out.push(fileOutgoing.deliveredBeforeFact(row));
    }

    if (row.quarantine_path !== '') {
        out.push(fileOutgoing.textFact('quarantine_path', row.quarantine_path));
    }

    if (row.actor !== '') {
        out.push(fileOutgoing.textFact('handed_to', row.actor));
    }

    out = out.concat(fileOutgoing.storeFacts(row));

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
