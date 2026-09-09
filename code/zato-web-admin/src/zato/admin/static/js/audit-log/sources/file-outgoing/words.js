

// /////////////////////////////////////////////////////////////////////////////

// The file transfer presenter's config and the sentences it builds out of the backend's word table.

(function($) {

var kit = $.fn.zato.dashboard_kit;

var fileOutgoing = {

    config: {

        // The column whose value stands on its own, with no label before it.
        scheduleKey: 'schedule',

        // The column left to the pane.
        remotePathKey: 'endpoint',

        // The column read in the pane, where it links to the run's own page.
        runKey: 'current_run',

        // How many chips a row of this source carries.
        rowChipLimit: 3,

        // The event types this source writes.
        runEvent: 'run-completed',
        deliveredEvent: 'delivered',
        deliveryFailedEvent: 'delivery-failed',
        claimedEvent: 'file-claimed',
        ackedEvent: 'file-acked',
        quarantinedEvent: 'file-quarantined',
        retriedEvent: 'file-retried',
        verifyFailedEvent: 'verify-failed',
        connectionEvent: 'request-sent',

        // The events that end a delivery either way.
        deliveryEvents: {'delivered': true, 'delivery-failed': true},

        // The connection-level operations, as the operation attr names them.
        storeOperation: 'store',
        readOperation: 'read',
        moveOperation: 'move',
        deleteOperation: 'delete',

        // The statuses a store row carries once it has been checked.
        verifiedStatus: 'verified',
        verifyFailedStatus: 'verify-failed',

        // The outcomes as the rows carry them.
        okOutcome: 'ok',
        errorOutcome: 'error',
        runningOutcome: 'running',

        // The run statuses the presenter reads for itself.
        runningStatus: 'running',
        unchangedStatus: 'unchanged',
        cleanStatus: 'clean',
        partialStatus: 'partial',
        emptyStatus: 'empty',
        interruptedStatus: 'interrupted',
        listFailedStatus: 'list-failed',
        noDirectoryStatus: 'no-directory',

        // The statuses of a run that ended before it took anything, read as their status word.
        endedEarlyStatuses: {'no-directory': true, 'list-failed': true, 'interrupted': true},

        // The statuses of a run that never listed its directory, drawn as their error.
        unreachedStatuses: {'list-failed': true, 'no-directory': true},

        // The sources whose rows frame a file's steps rather than being steps.
        frameSources: {'file-outgoing': true, 'scheduler': true},
        ownSource: 'file-outgoing',

        // What the chips say.
        seenBeforeLabel: 'seen before',
        quarantinedLabel: 'quarantined',
        attemptsLabel: 'attempts',
        verifiedLabel: 'verified',
        verifyFailedLabel: 'verify failed',
        takenLabel: 'taken',
        failedLabel: 'failed',
        deliveredLabel: 'delivered',
        seenLabel: 'seen',
        overdueLabel: 'overdue',
        runWord: 'Run',
        chipSeparator: ', ',

        // The tiles of a run's summary, in order.
        tileLabels: {
            seen: 'Seen',
            taken: 'Taken',
            delivered: 'Delivered',
            failed: 'Failed',
            quarantined: 'Quarantined',
            expected: 'Expected'
        },
        expectedTileTitle: 'Expected by {expected_by} today',
        expectedOverdueTitle: 'Expected by {expected_by} today, {minutes} minutes overdue',
        expectedValue: '{delivered_today} of {expected_files}',

        // The steps of a file and the steps of a stored file.
        journeySteps: {
            claimed: 'Claimed',
            read: 'Read',
            delivered: 'Delivered',
            acked: 'Put away',
            quarantined: 'Quarantined',
            reprocessed: 'Reprocessed',
            stored: 'Stored',
            verified: 'Verified',
            moved: 'Moved',
            deleted: 'Deleted'
        },
        journeyLoadingLabel: 'Loading',

        // Where the rows of one cid are read from and where the flow page is.
        journeyURL: '/zato/message-flow/journey/',
        flowPagePath: '/zato/message-flow/',

        // Whether the page holds a drawing a step can be selected on, set by the flow page.
        selectOnDrawing: false,

        // The body kinds a run's ledger and a run's traceback are kept under.
        ledgerKind: 'run-ledger',
        errorBodyKind: 'error',

        // What the Details tab says for the things it says of its own.
        expectedOfLabel: '{delivered_today} of {expected_files} by {expected_by}',
        deliveredBeforeLabel: 'Delivered before',
        deliveredBeforeText: '{count} times, last at {when}',
        seenBeforeText: 'Same content delivered {when} as {file_name}',
        repeatsText: 'run event {event_id}, listed {when}',
        yesText: 'yes',
        noText: 'no',
        bytesSuffix: ' B',

        // What a resubmit is warned about when the same content went out before.
        resubmitWarningText: 'This content was delivered {count} times, last at {when}.',
        resubmitDeliveredOnceText: 'This file was already delivered, at {when}.',

        // How wide the progress bar of a running run is, in em, at its fullest.
        progressBarWidthEm: 6,

        // The prefix of a fold key of a run's summary and of a run's error.
        runFoldPrefix: 'run-',
        runErrorFoldPrefix: 'run-error-'
    }
};

$.fn.zato.audit_log.fileOutgoing = fileOutgoing;

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.words = function() {
    return $.fn.zato.audit_log.config.fileTransferWords;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.escapeHTML = function(value) {
    return $.fn.zato.audit_log.escapeHTML(value);
};

// /////////////////////////////////////////////////////////////////////////////

// A template with each {name} replaced by the value under that name.
fileOutgoing.fill = function(template, values) {
    var out = template;

    for (var name in values) {
        out = out.split('{' + name + '}').join(String(values[name]));
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The local time of day of a moment as HH:MM.
fileOutgoing.timeOfDay = function(iso) {
    var local = kit.format_local_time(iso);
    return local.slice(11, 16);
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.errorSummary = function(error) {
    return error.split('\n').pop();
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.isRun = function(row) {
    return row.event_type === fileOutgoing.config.runEvent;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.isStore = function(row) {
    var config = fileOutgoing.config;

    if (row.event_type !== config.connectionEvent) {
        return false;
    }

    return row.operation === config.storeOperation;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.isOwn = function(row) {
    return row.source === fileOutgoing.config.ownSource;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.entriesText = function(entries) {
    var templates = fileOutgoing.words().sentence_template;

    if (entries === 1) {
        return templates.entries_one;
    }

    return fileOutgoing.fill(templates.entries_many, {entries: entries});
};

// /////////////////////////////////////////////////////////////////////////////

// The skip reasons of a run, the most frequent first.
fileOutgoing.orderedSkips = function(skipReasons) {
    var words = fileOutgoing.words();
    var out = [];

    for (var reason in skipReasons) {
        var label = words.skip_reason_label[reason];
        out.push({reason: reason, label: label, count: skipReasons[reason]});
    }

    out.sort(function(first, second) {
        return second.count - first.count;
    });

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.skipsText = function(skipReasons) {
    var templates = fileOutgoing.words().sentence_template;
    var ordered = fileOutgoing.orderedSkips(skipReasons);
    var parts = [];

    for (var index = 0; index < ordered.length; index++) {
        var item = ordered[index];
        parts.push(fileOutgoing.fill(templates.skip_item, {count: item.count, reason: item.label}));
    }

    return parts.join(', ');
};

// /////////////////////////////////////////////////////////////////////////////

// How many minutes past the daily deadline it is now, zero before the deadline.
fileOutgoing.overdueMinutes = function(expectedBy) {
    var parts = expectedBy.split(':');
    var now = new Date();
    var hours = parseInt(parts[0], 10);
    var minutesOfHour = parseInt(parts[1], 10);
    var deadline = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hours, minutesOfHour, 0, 0);

    var minutes = Math.floor((now.getTime() - deadline.getTime()) / 60000);

    if (minutes < 0) {
        return 0;
    }

    return minutes;
};

// /////////////////////////////////////////////////////////////////////////////

// Whether the day expects files of the schedule at all.
fileOutgoing.hasExpectation = function(row) {
    if (!row.expected_files) {
        return false;
    }

    return row.expected_by !== '';
};

// /////////////////////////////////////////////////////////////////////////////

// How many minutes the day is overdue, zero when it is not short or the deadline has not passed.
fileOutgoing.overdueOf = function(row) {
    if (!fileOutgoing.hasExpectation(row)) {
        return 0;
    }

    if (row.delivered_today >= row.expected_files) {
        return 0;
    }

    return fileOutgoing.overdueMinutes(row.expected_by);
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.overdueText = function(overdue) {
    var templates = fileOutgoing.words().sentence_template;

    if (overdue === 1) {
        return templates.overdue_suffix_one;
    }

    return fileOutgoing.fill(templates.overdue_suffix_many, {overdue_minutes: overdue});
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.expectedSuffix = function(row) {
    var templates = fileOutgoing.words().sentence_template;

    if (!fileOutgoing.hasExpectation(row)) {
        return '';
    }

    var out = fileOutgoing.fill(templates.expected_suffix, {
        delivered_today: row.delivered_today,
        expected_files: row.expected_files,
        expected_by: row.expected_by
    });

    var overdue = fileOutgoing.overdueOf(row);

    if (overdue > 0) {
        out += fileOutgoing.overdueText(overdue);
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.phaseWord = function(row) {
    return fileOutgoing.words().phase_label[row.phase];
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.runningSentence = function(row) {
    var words = fileOutgoing.words();
    var templates = words.sentence_template;
    var phaseWord = fileOutgoing.phaseWord(row);

    if (words.file_phases.indexOf(row.phase) !== -1) {
        if (row.taken) {
            return fileOutgoing.fill(templates.running_progress, {
                phase: phaseWord, file: row.current_file, taken_so_far: row.taken_so_far, taken: row.taken});
        }

        return fileOutgoing.fill(templates.running_file, {phase: phaseWord, file: row.current_file});
    }

    return fileOutgoing.fill(templates.running_plain, {phase: phaseWord});
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.interruptedSentence = function(row) {
    var templates = fileOutgoing.words().sentence_template;

    if (row.current_file === '') {
        return templates.interrupted_plain;
    }

    var phaseWord = fileOutgoing.phaseWord(row);

    return fileOutgoing.fill(templates.interrupted_file, {phase: phaseWord.toLowerCase(), file: row.current_file});
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.deliveredSentence = function(row) {
    var config = fileOutgoing.config;
    var templates = fileOutgoing.words().sentence_template;
    var hasError = row.first_failed_error !== '';
    var values = {
        taken: row.taken,
        processed: row.processed,
        failed: row.failed,
        skipped: row.skipped,
        failed_file: row.first_failed_file,
        error: row.first_failed_error
    };

    var template;

    if (row.status === config.cleanStatus) {
        template = templates.clean;

        if (row.skipped) {
            template = templates.clean_with_skips;
        }
    }
    else if (row.status === config.partialStatus) {
        template = templates.partial;

        if (hasError) {
            template = templates.partial_with_error;
        }
    }
    else {
        template = templates.failed;

        if (hasError) {
            template = templates.failed_with_error;
        }
    }

    var out = fileOutgoing.fill(template, values);

    if (row.quarantined) {
        out += fileOutgoing.fill(templates.quarantined_suffix, {quarantined: row.quarantined});
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.emptySentence = function(row) {
    var templates = fileOutgoing.words().sentence_template;
    var directory = row.remote_path;

    if (!row.entries) {
        return fileOutgoing.fill(templates.empty_directory, {directory: directory});
    }

    var entries = fileOutgoing.entriesText(row.entries);
    var skips = fileOutgoing.skipsText(row.skip_reasons);

    return fileOutgoing.fill(templates.took_none, {entries: entries, directory: directory, skips: skips});
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.listFailedSentence = function(row) {
    var template = fileOutgoing.words().list_failed_phase_template[row.phase];
    return fileOutgoing.fill(template, {directory: row.remote_path, error: row.error});
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.noDirectorySentence = function(row) {
    var templates = fileOutgoing.words().sentence_template;
    return fileOutgoing.fill(templates.no_directory, {directory: row.remote_path});
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.unchangedSentence = function(row) {
    var templates = fileOutgoing.words().sentence_template;
    var since = fileOutgoing.timeOfDay(row.unchanged_since_iso);
    return fileOutgoing.fill(templates.unchanged, {directory: row.remote_path, since: since});
};

// /////////////////////////////////////////////////////////////////////////////

// The sentence of each run status.
fileOutgoing.sentenceByStatus = {
    'running': fileOutgoing.runningSentence,
    'clean': fileOutgoing.deliveredSentence,
    'partial': fileOutgoing.deliveredSentence,
    'failed': fileOutgoing.deliveredSentence,
    'empty': fileOutgoing.emptySentence,
    'unchanged': fileOutgoing.unchangedSentence,
    'no-directory': fileOutgoing.noDirectorySentence,
    'list-failed': fileOutgoing.listFailedSentence,
    'interrupted': fileOutgoing.interruptedSentence
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.runSentence = function(row) {
    var sentenceOf = fileOutgoing.sentenceByStatus[row.status];

    var out = sentenceOf(row);
    out += fileOutgoing.expectedSuffix(row);

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.sizeText = function(size) {
    return kit.format_number_full(size) + fileOutgoing.config.bytesSuffix;
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.storeSentence = function(row) {
    var config = fileOutgoing.config;
    var templates = fileOutgoing.words().sentence_template;
    var values = {
        file: row.file_name,
        size: fileOutgoing.sizeText(row.size),
        verify_ms: row.verify_ms,
        remote_size: row.remote_size,
        error: row.mismatch
    };

    if (row.status === config.verifiedStatus) {
        return fileOutgoing.fill(templates.store_verified, values);
    }

    if (row.status === config.verifyFailedStatus) {
        return fileOutgoing.fill(templates.store_verify_failed, values);
    }

    return '';
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.quarantinedSentence = function(row) {
    var templates = fileOutgoing.words().sentence_template;

    if (row.attempts === 1) {
        return fileOutgoing.fill(templates.quarantined_file_one, {error: row.error});
    }

    return fileOutgoing.fill(templates.quarantined_file_many, {attempts: row.attempts, error: row.error});
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.seenBeforeText = function(row) {
    var when = fileOutgoing.timeOfDay(row.seen_before_iso);
    return fileOutgoing.fill(fileOutgoing.config.seenBeforeText, {when: when, file_name: row.seen_before_file_name});
};

// /////////////////////////////////////////////////////////////////////////////

// The one line a row reads as, empty for a row with nothing to sum up.
fileOutgoing.sentence = function(row) {
    var config = fileOutgoing.config;
    var templates = fileOutgoing.words().sentence_template;

    if (fileOutgoing.isRun(row)) {
        return fileOutgoing.runSentence(row);
    }

    if (fileOutgoing.isStore(row)) {
        return fileOutgoing.storeSentence(row);
    }

    if (row.event_type === config.quarantinedEvent) {
        return fileOutgoing.quarantinedSentence(row);
    }

    if (row.event_type === config.retriedEvent) {
        return fileOutgoing.fill(templates.retried_file, {actor: row.actor});
    }

    if (row.event_type === config.deliveredEvent) {
        if (row.seen_before_event_id) {
            return fileOutgoing.seenBeforeText(row);
        }
    }

    return '';
};

// /////////////////////////////////////////////////////////////////////////////

fileOutgoing.attemptText = function(row) {
    var templates = fileOutgoing.words().sentence_template;

    if (row.max_attempts) {
        return fileOutgoing.fill(templates.attempt_of, {attempt: row.attempt, max_attempts: row.max_attempts});
    }

    return fileOutgoing.fill(templates.attempt_plain, {attempt: row.attempt});
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
