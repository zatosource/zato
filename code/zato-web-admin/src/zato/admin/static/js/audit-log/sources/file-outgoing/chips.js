

// /////////////////////////////////////////////////////////////////////////////

// The chips a file transfer row carries after its schedule or file name.

(function($) {

var fileOutgoing = $.fn.zato.audit_log.fileOutgoing;

// /////////////////////////////////////////////////////////////////////////////

// A thin bar under a running run's words, as wide as the run has come.
fileOutgoing.progressHTML = function(row) {
    var config = fileOutgoing.config;
    var text = fileOutgoing.runningSentence(row);
    var share = 0;

    if (row.taken) {
        share = row.taken_so_far / row.taken;
    }

    var widthEm = (share * config.progressBarWidthEm).toFixed(2);

    var out = '<span class="audit-log-progress">' +
        '<span class="audit-log-progress-text">' + fileOutgoing.escapeHTML(text) + '</span>' +
        '<span class="audit-log-progress-bar" style="width: ' + config.progressBarWidthEm + 'em">' +
        '<span class="audit-log-progress-fill" style="width: ' + widthEm + 'em"></span></span></span>';

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.countPair = function(firstCount, firstLabel, secondCount, secondLabel) {
    var separator = fileOutgoing.config.chipSeparator;
    return firstCount + ' ' + firstLabel + separator + secondCount + ' ' + secondLabel;
};

// /////////////////////////////////////////////////////////////////////////////

// The chip after a run's schedule, what the run did in the run's tone.
fileOutgoing.runChip = function(row) {
    var config = fileOutgoing.config;
    var words = fileOutgoing.words();
    var status = row.status;

    if (status === config.runningStatus) {
        return {key: 'progress', label: '', value: fileOutgoing.runningSentence(row),
            value_html: fileOutgoing.progressHTML(row), tone: 'running'};
    }

    if (row.failed > 0) {
        var failedText = fileOutgoing.countPair(row.taken, config.takenLabel, row.failed, config.failedLabel);
        return {key: 'summary', label: '', value: status, tone: 'bad', text: failedText};
    }

    if (status === config.unchangedStatus) {
        return {key: 'summary', label: '', value: status, tone: 'muted', text: words.run_status_label[status]};
    }

    if (config.endedEarlyStatuses[status]) {
        return {key: 'summary', label: '', value: status, tone: words.run_status_tone[status],
            text: words.run_status_label[status]};
    }

    if (row.taken > 0) {
        var takenText = fileOutgoing.countPair(row.taken, config.takenLabel, row.processed, config.deliveredLabel);
        return {key: 'summary', label: '', value: status, tone: 'neutral', text: takenText};
    }

    var seenText = fileOutgoing.countPair(row.entries, config.seenLabel, row.taken, config.takenLabel);
    return {key: 'summary', label: '', value: status, tone: 'neutral', text: seenText};
};

// /////////////////////////////////////////////////////////////////////////////

// The chip of a day short of its expectation past the deadline, null otherwise.
fileOutgoing.expectedChip = function(row) {
    var config = fileOutgoing.config;

    if (fileOutgoing.overdueOf(row) === 0) {
        return null;
    }

    var expected = fileOutgoing.fill(config.expectedValue, {
        delivered_today: row.delivered_today, expected_files: row.expected_files});
    var text = expected + config.chipSeparator + config.overdueLabel;

    return {key: 'expected', label: '', value: row.expected_by, tone: 'warn', text: text};
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.storeChip = function(row) {
    var config = fileOutgoing.config;

    if (row.status === config.verifiedStatus) {
        return {key: 'verified', label: '', value: row.status, tone: 'muted', text: config.verifiedLabel};
    }

    if (row.status === config.verifyFailedStatus) {
        return {key: 'verified', label: '', value: row.status, tone: 'bad', text: config.verifyFailedLabel};
    }

    return null;
};

// /////////////////////////////////////////////////////////////////////////////

// The chips a per-file row carries past the file's own name.
fileOutgoing.fileExtraChips = function(row) {
    var config = fileOutgoing.config;
    var separator = config.chipSeparator;
    var out = [];

    if (row.event_type === config.quarantinedEvent) {
        out.push({key: 'quarantined', label: '', value: 'quarantined', tone: 'bad',
            text: config.quarantinedLabel + separator + row.attempts + ' ' + config.attemptsLabel});
    }

    if (row.event_type === config.deliveredEvent) {
        if (row.seen_before_event_id) {
            out.push({key: 'seen_before', label: '', value: row.checksum, tone: 'warn', text: config.seenBeforeLabel});
        }
    }

    if (row.event_type === config.deliveryFailedEvent) {
        if (row.attempt) {
            out.push({key: 'attempt', label: '', value: String(row.attempt), tone: 'neutral',
                text: fileOutgoing.attemptText(row)});
        }
    }

    if (fileOutgoing.isStore(row)) {
        var storeChip = fileOutgoing.storeChip(row);

        if (storeChip !== null) {
            out.push(storeChip);
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
