

// /////////////////////////////////////////////////////////////////////////////

// The run summary of a file transfer run, its tiles, skip chips and ledger.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var fileOutgoing = $.fn.zato.audit_log.fileOutgoing;

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.expectedTile = function(row) {
    var config = fileOutgoing.config;
    var labels = config.tileLabels;

    var tone = 'muted';
    var title = fileOutgoing.fill(config.expectedTileTitle, {expected_by: row.expected_by});
    var overdue = fileOutgoing.overdueOf(row);

    if (overdue > 0) {
        tone = 'warn';
        title = fileOutgoing.fill(config.expectedOverdueTitle, {expected_by: row.expected_by, minutes: overdue});
    }

    var value = fileOutgoing.fill(config.expectedValue, {
        delivered_today: row.delivered_today, expected_files: row.expected_files});

    return {label: labels.expected, value: value, tone: tone, title: title};
};

// /////////////////////////////////////////////////////////////////////////////

// The tiles of a run, a count is toned only when there is something in it.
fileOutgoing.runTiles = function(row) {
    var config = fileOutgoing.config;
    var labels = config.tileLabels;
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

    out.push({label: labels.seen, value: row.entries, tone: 'neutral', title: ''});
    out.push({label: labels.taken, value: row.taken, tone: takenTone, title: ''});
    out.push({label: labels.delivered, value: row.processed, tone: deliveredTone, title: ''});
    out.push({label: labels.failed, value: row.failed, tone: failedTone, title: ''});

    if (row.quarantined > 0) {
        out.push({label: labels.quarantined, value: row.quarantined, tone: 'bad', title: ''});
    }

    if (row.expected_files) {
        out.push(fileOutgoing.expectedTile(row));
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.runSkips = function(row) {
    return fileOutgoing.orderedSkips(row.skip_reasons);
};

// /////////////////////////////////////////////////////////////////////////////

// The reason column of a ledger entry, a taken entry reads its attempt instead.
fileOutgoing.ledgerReason = function(record) {
    var words = fileOutgoing.words();
    var out = '';

    if (record.reason !== '') {
        out = words.skip_reason_label[record.reason];
    }

    if (record.attempt) {
        var attemptText = fileOutgoing.fill(words.sentence_template.attempt_plain, {attempt: record.attempt});

        if (out === '') {
            out = attemptText;
        }
        else {
            out += ', ' + attemptText;
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// How old an entry was when the run saw it.
fileOutgoing.ledgerAge = function(record, runTimeIso) {
    var runTime = new Date(runTimeIso).getTime();
    var modifiedTime = new Date(record.last_modified_iso).getTime();
    var ageMs = runTime - modifiedTime;

    if (ageMs < 0) {
        return '';
    }

    return kit.format_ago(Math.floor(ageMs / 1000));
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.ledgerEntry = function(record, runTimeIso) {
    var config = fileOutgoing.config;
    var words = fileOutgoing.words();

    var tookText = '';

    if (record.duration_ms) {
        tookText = kit.format_duration_ms(record.duration_ms);
    }

    var linkURL = '';

    if (record.file_cid !== '') {
        linkURL = config.flowPagePath + '?term=' + encodeURIComponent(record.file_cid);
    }

    return {
        name: record.name,
        sizeText: kit.format_number_full(record.size),
        ageText: fileOutgoing.ledgerAge(record, runTimeIso),
        decision: record.decision,
        decisionLabel: words.decision_label[record.decision],
        decisionTone: words.decision_tone[record.decision],
        reason: record.reason,
        reasonLabel: fileOutgoing.ledgerReason(record),
        tookText: tookText,
        linkURL: linkURL
    };
};

// /////////////////////////////////////////////////////////////////////////////

// Whether the host still holds the event the summary was asked for.
fileOutgoing.isHostAttached = function($host) {
    return $host.closest('body').length > 0;
};

// /////////////////////////////////////////////////////////////////////////////

// The summary of a run that never listed its directory, its error with the traceback behind a fold.
fileOutgoing.renderRunError = function(rowModel, $host, variant) {
    var config = fileOutgoing.config;
    var listing = $.fn.zato.audit_log.listing;
    var row = rowModel.raw;

    var errorLine = fileOutgoing.errorSummary(row.error);

    if (row.status === config.noDirectoryStatus) {
        errorLine = fileOutgoing.runSentence(row);
    }

    $host.html(kit.runSummary.renderError({
        error: errorLine,
        variant: variant,
        foldKey: config.runErrorFoldPrefix + row.schedule
    }));

    var $summary = $host.find('.dashboard-run-summary');

    if (row.body_kinds.indexOf(config.errorBodyKind) === -1) {
        return;
    }

    listing.fetchDetails(rowModel.id, config.errorBodyKind, false, function(details) {
        if (!fileOutgoing.isHostAttached($host)) {
            return;
        }

        kit.runSummary.fillError($summary, details.data);
    });
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.ledgerEntries = function(details, row) {
    var out = [];

    if (details.data === '') {
        return out;
    }

    var records = JSON.parse(details.data);

    for (var index = 0; index < records.length; index++) {
        out.push(fileOutgoing.ledgerEntry(records[index], row.event_time_iso));
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The summary drawn into a host, the tiles and skips at once and the ledger once read.
fileOutgoing.renderRunSummary = function(rowModel, $host, variant) {
    var config = fileOutgoing.config;
    var listing = $.fn.zato.audit_log.listing;
    var row = rowModel.raw;

    if (config.unreachedStatuses[row.status]) {
        fileOutgoing.renderRunError(rowModel, $host, variant);
        return;
    }

    $host.html(kit.runSummary.render({
        tiles: fileOutgoing.runTiles(row),
        skips: fileOutgoing.runSkips(row),
        variant: variant,
        foldKey: config.runFoldPrefix + row.schedule
    }));

    var $summary = $host.find('.dashboard-run-summary');

    if (row.status === config.runningStatus) {
        kit.runSummary.fillLedger($summary, [], 0);
        return;
    }

    listing.fetchDetails(rowModel.id, config.ledgerKind, false, function(details) {
        if (!fileOutgoing.isHostAttached($host)) {
            return;
        }

        var entries = fileOutgoing.ledgerEntries(details, row);
        kit.runSummary.fillLedger($summary, entries, row.ledger_overflow);
    });
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
