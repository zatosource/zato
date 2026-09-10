

// /////////////////////////////////////////////////////////////////////////////

// The Details tab of a file transfer run, its fact rows and the ledger of what it saw.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var fileOutgoing = $.fn.zato.audit_log.fileOutgoing;

// /////////////////////////////////////////////////////////////////////////////

// The reason column of a ledger entry, a picked up entry reads its attempt instead.
fileOutgoing.ledgerReason = function(record) {
    var words = fileOutgoing.words();
    var out = '';

    if (record.reason !== '') {
        out = words.skip_reason_name[record.reason];
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

fileOutgoing.ledgerEntry = function(record) {
    var words = fileOutgoing.words();

    var durationText = '';

    if (record.duration_ms) {
        durationText = kit.format_duration_ms(record.duration_ms);
    }

    var linkURL = '';

    if (record.file_cid !== '') {
        linkURL = $.fn.zato.audit_log.flowPageURL(record.file_cid);
    }

    return {
        name: record.name,
        sizeText: kit.format_number_full(record.size),
        modifiedText: kit.format_local_time(record.last_modified_iso),
        decision: record.decision,
        decisionLabel: words.decision_label[record.decision],
        decisionTone: words.decision_tone[record.decision],
        reason: record.reason,
        reasonLabel: fileOutgoing.ledgerReason(record),
        durationText: durationText,
        linkURL: linkURL
    };
};

// /////////////////////////////////////////////////////////////////////////////

// Whether the host still holds the event the summary was asked for.
fileOutgoing.isHostAttached = function($host) {
    return $host.closest('body').length > 0;
};

// /////////////////////////////////////////////////////////////////////////////

// The fact rows of a run's Details tab, in the variant the panel is drawn in.
fileOutgoing.runDetailFactsHTML = function(row, variant) {
    var facts = fileOutgoing.runDetailFacts(row);
    return kit.fact_rows.render(facts, variant);
};

// /////////////////////////////////////////////////////////////////////////////

// The Details of a run that never listed its directory - its error as a fact, the traceback behind a fold under it.
fileOutgoing.renderRunError = function(rowModel, $host, variant) {
    var config = fileOutgoing.config;
    var listing = $.fn.zato.audit_log.listing;
    var row = rowModel.raw;

    // A directory that is not there is the whole of the error, the row itself carries none.
    var errorLine = fileOutgoing.errorSummary(row.error);

    if (row.status === config.noDirectoryStatus) {
        errorLine = fileOutgoing.noDirectorySentence(row);
    }

    var facts = [fileOutgoing.textFact('error', errorLine)];

    $host.html(kit.runSummary.renderError({
        factsHTML: kit.fact_rows.render(facts, variant),
        variant: variant,
        foldKey: config.runErrorFoldPrefix + row.schedule
    }));

    var $summary = $host.find('.dashboard-run-summary');

    if (row.body_kinds.indexOf(config.errorBodyKind) === -1) {
        return;
    }

    // On the flow page the traceback has a tab of its own beside the reply
    if (config.tracebackInPane) {
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

fileOutgoing.ledgerEntries = function(details) {
    var out = [];

    if (details.data === '') {
        return out;
    }

    var records = JSON.parse(details.data);

    for (var index = 0; index < records.length; index++) {
        out.push(fileOutgoing.ledgerEntry(records[index]));
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The Details drawn into a host, the facts at once and the ledger once read. A running run
// has no ledger yet, its facts alone are redrawn at every poll.
fileOutgoing.renderRunSummary = function(rowModel, $host, variant) {
    var config = fileOutgoing.config;
    var listing = $.fn.zato.audit_log.listing;
    var row = rowModel.raw;

    if (config.unreachedStatuses[row.status]) {
        fileOutgoing.renderRunError(rowModel, $host, variant);
        return;
    }

    var factsHTML = fileOutgoing.runDetailFactsHTML(row, variant);

    if (row.status === config.runningStatus) {
        $host.html(kit.runSummary.frameHTML({variant: variant, foldKey: config.runFoldPrefix + row.schedule}, factsHTML));
        return;
    }

    $host.html(kit.runSummary.render({
        factsHTML: factsHTML,
        variant: variant,
        foldKey: config.runFoldPrefix + row.schedule
    }));

    var $summary = $host.find('.dashboard-run-summary');

    // A run that saw the same listing as the one before it writes no ledger of its own - the
    // entries it saw are the ones the first run of that listing wrote down, so they are read from there.
    var ledgerEventId = rowModel.id;

    if (row.status === config.unchangedStatus) {
        ledgerEventId = row.unchanged_since_event_id;
    }

    listing.fetchDetails(ledgerEventId, config.ledgerKind, false, function(details) {
        if (!fileOutgoing.isHostAttached($host)) {
            return;
        }

        var entries = fileOutgoing.ledgerEntries(details);
        kit.runSummary.fillLedger($summary, entries, row.ledger_overflow, row.entries);
    });
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
