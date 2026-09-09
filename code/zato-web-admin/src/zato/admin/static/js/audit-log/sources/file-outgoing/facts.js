

// /////////////////////////////////////////////////////////////////////////////

// The facts a file transfer row adds to the pane's Summary tab, and the facts a run's Details tab opens with.

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

fileOutgoing.repeatsFact = function(row) {
    var text = fileOutgoing.fill(fileOutgoing.config.repeatsText, {
        event_id: row.unchanged_since_event_id,
        when: kit.format_local_time(row.unchanged_since_iso)});

    return fileOutgoing.eventFact('note', text, row.unchanged_since_event_id);
};

// /////////////////////////////////////////////////////////////////////////////

// A count in its tone, the tone carried by the value rather than said in words.
fileOutgoing.countFact = function(key, count, tone) {
    var valueHTML = kit.runSummary.valueHTML(count, tone);
    return fileOutgoing.fact(key, valueHTML, String(count), '');
};

// /////////////////////////////////////////////////////////////////////////////

// The day's count against the schedule's expectation, in warning once the deadline has passed short.
fileOutgoing.expectedFact = function(row) {
    var text = fileOutgoing.fill(fileOutgoing.config.expectedOfLabel, {
        delivered_today: row.delivered_today, expected_files: row.expected_files, expected_by: row.expected_by});

    var tone = 'muted';

    if (fileOutgoing.overdueOf(row) > 0) {
        tone = 'warn';
    }

    return fileOutgoing.fact('expected', kit.runSummary.valueHTML(text, tone), text, '');
};

// /////////////////////////////////////////////////////////////////////////////

// The skip reasons of a run as chips, each narrowing the ledger to its reason.
fileOutgoing.skippedFact = function(row) {
    var skips = fileOutgoing.orderedSkips(row.skip_reasons);
    var chips = [];

    for (var index = 0; index < skips.length; index++) {
        var skip = skips[index];
        chips.push({reason: skip.reason, label: skip.name, count: skip.count});
    }

    var copyValue = fileOutgoing.skipsText(row.skip_reasons);

    return fileOutgoing.fact('skipped', kit.runSummary.skipsHTML(chips), copyValue, '');
};

// /////////////////////////////////////////////////////////////////////////////

// The counts of a run, which is what its Details tab opens with - a count is toned only when
// there is something in it, and a running run's counts are still moving.
fileOutgoing.countFacts = function(row) {
    var config = fileOutgoing.config;
    var isRunning = row.status === config.runningStatus;
    var out = [];

    var takenTone = 'neutral';
    var deliveredTone = 'neutral';

    if (isRunning) {
        takenTone = 'running';
        deliveredTone = 'running';
    }
    else if (row.processed > 0) {
        deliveredTone = 'good';
    }

    var failedTone = 'muted';

    if (row.failed > 0) {
        failedTone = 'bad';
    }

    out.push(fileOutgoing.countFact('entries', row.entries, 'neutral'));
    out.push(fileOutgoing.countFact('taken', row.taken, takenTone));
    out.push(fileOutgoing.countFact('processed', row.processed, deliveredTone));
    out.push(fileOutgoing.countFact('failed', row.failed, failedTone));

    if (row.quarantined) {
        out.push(fileOutgoing.countFact('quarantined', row.quarantined, 'bad'));
    }

    if (row.acked) {
        out.push(fileOutgoing.countFact('acked', row.acked, 'neutral'));
    }

    if (row.ack_failed) {
        out.push(fileOutgoing.countFact('ack_failed', row.ack_failed, 'bad'));
    }

    if (row.expected_files) {
        out.push(fileOutgoing.expectedFact(row));
    }

    if (row.skipped > 0) {
        out.push(fileOutgoing.skippedFact(row));
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The facts of a run's Details tab - what it is doing while it runs, then its counts.
fileOutgoing.runDetailFacts = function(row) {
    var config = fileOutgoing.config;
    var out = [];

    if (row.status === config.runningStatus) {
        out.push(fileOutgoing.runningFact(row));
    }

    out = out.concat(fileOutgoing.countFacts(row));

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The facts of a run's Summary tab - the counts are the Details tab's.
fileOutgoing.runFacts = function(row) {
    var config = fileOutgoing.config;
    var out = [];

    if (row.status === config.runningStatus) {
        out.push(fileOutgoing.runningFact(row));
    }

    if (row.status === config.unchangedStatus) {
        out.push(fileOutgoing.repeatsFact(row));
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
