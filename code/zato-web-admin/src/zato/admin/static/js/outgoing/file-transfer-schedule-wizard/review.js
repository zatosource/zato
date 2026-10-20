// File transfer schedule wizard - the line summaries and the review step.
//
// Each decision line carries a one-line summary of what its popover
// currently holds, recomputed from the form each time a popover closes or
// a segment is picked. The review step says the same things again,
// grouped, each group linking back to the step its answers came from.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.outgoing.file_transfer.wizard;

$.fn.zato.wizard_kit.review.setup(wizard);

var review = wizard.review;

// ////////////////////////////////////////////////////////////////////////

review.config_own = {

    // The units a number of seconds is said in, the largest one it divides into evenly first
    durationUnits: [
        {seconds: 86400, suffix: ' d'},
        {seconds: 3600,  suffix: ' h'},
        {seconds: 60,    suffix: ' min'},
        {seconds: 1,     suffix: ' s'}
    ],

    // How many weekdays in a row read as a range, e.g. Mon-Fri
    weekdayRangeMin: 3,

    // What a check that is turned off reads as on the review
    offText: 'Off'
};

// ////////////////////////////////////////////////////////////////////////

// A number of seconds in the largest unit it divides into evenly, e.g. 3600 as 1 h.
review.durationText = function(secondsText) {

    var seconds = parseInt(secondsText);
    var units = review.config_own.durationUnits;
    var out;

    for(var unitIdx = 0; unitIdx < units.length; unitIdx++) {
        var unit = units[unitIdx];
        var isEven = seconds % unit.seconds === 0;

        if(isEven) {
            out = (seconds / unit.seconds) + unit.suffix;
            break;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A count with its noun, in the singular for one, e.g. 1 file or 3 files.
review.countText = function(count, singular, plural) {

    var noun = count === 1 ? singular : plural;
    var out = count + ' ' + noun;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The expected days by name, runs of consecutive days as ranges, e.g. Mon-Fri or Mon, Wed, Fri.
review.weekdaysText = function() {

    var formsConfig = wizard.forms.config_own;
    var weekdays = formsConfig.weekdays;
    var picked = wizard.field('expected_days').val().split(formsConfig.weekdaySeparator);
    var rangeMin = review.config_own.weekdayRangeMin;

    // The runs of consecutive picked days, each a list of day names
    var runs = [];
    var currentRun = [];

    for(var dayIdx = 0; dayIdx < weekdays.length; dayIdx++) {
        var weekday = weekdays[dayIdx];
        var isPicked = picked.indexOf(weekday.number) !== -1;

        if(isPicked) {
            currentRun.push(weekday.label);
        }
        else if(currentRun.length) {
            runs.push(currentRun);
            currentRun = [];
        }
    }

    if(currentRun.length) {
        runs.push(currentRun);
    }

    var parts = [];

    for(var runIdx = 0; runIdx < runs.length; runIdx++) {
        var run = runs[runIdx];
        var isRange = run.length >= rangeMin;

        if(isRange) {
            var lastDay = run[run.length - 1];
            parts.push(run[0] + '-' + lastDay);
        }
        else {
            parts = parts.concat(run);
        }
    }

    var out = parts.join(', ');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// How often the directory is polled, e.g. Every 5 minutes or Every 1 hour.
review.intervalText = function() {

    var runEvery = parseInt(wizard.field('run_every').val());
    var unit = wizard.field('run_unit').val();

    // The units are stored as plurals, a count of one reads with the singular
    if(runEvery === 1) {
        unit = unit.substring(0, unit.length - 1);
    }

    var out = 'Every ' + runEvery + ' ' + unit;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// How the readiness parameter reads beside its strip
review.readyText = function() {

    var readyMode = wizard.field('ready_how').val();
    var out;

    if(readyMode === 'stability') {
        out = 'Stable for ' + review.durationText(wizard.field('stability_delay').val());
    }
    else {
        out = 'Suffix ' + wizard.field('marker_suffix').val();
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// How the arrival monitoring reads - empty while it is off
review.arrivalWindowText = function() {

    var out = '';

    if(wizard.forms.isMonitoringOn('arrival_window')) {
        out = 'Alert after ' + review.durationText(wizard.field('arrival_window').val()) + ' without a file';
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// How the daily delivery check reads - empty while it is off
review.expectationText = function() {

    var out = '';

    if(wizard.forms.isMonitoringOn('expected_files')) {

        var expectedFiles = parseInt(wizard.field('expected_files').val());
        var expectedBy = wizard.field('expected_by').val();
        var weekdays = review.weekdaysText();

        out = review.countText(expectedFiles, 'file', 'files') + ' by ' + expectedBy;

        if(weekdays) {
            out = out + ', ' + weekdays;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// How the retry policy reads - zero attempts means a file is retried with no limit
review.retriesText = function() {

    var maxAttempts = parseInt(wizard.field('max_attempts').val());
    var retryDelay = review.durationText(wizard.field('retry_backoff').val());
    var out;

    if(maxAttempts) {
        var quarantineDirectory = wizard.field('quarantine_directory').val();
        out = review.countText(maxAttempts, 'attempt', 'attempts') + ', ' + retryDelay +
            ' initial delay, then to ' + quarantineDirectory + '/';
    }
    else {
        out = 'Unlimited attempts, ' + retryDelay + ' initial delay';
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The one-line summaries beside the segments and on the other lines -
// recomputed from the form each time an answer changes.
review.refreshSummaries = function() {

    review.setSummary('file-transfer-wizard-summary-ready', review.readyText());

    // A deleted file has no parameter to edit, so its line loses the
    // link - an empty summary is what takes it off the screen
    var successText = '';

    if(wizard.field('on_success').val() === 'move') {
        successText = 'To ' + wizard.field('move_directory').val() + '/';
    }

    review.setSummary('file-transfer-wizard-summary-success', successText);
    review.setSummary('file-transfer-wizard-summary-retries', review.retriesText());
    review.setSummary('file-transfer-wizard-summary-run-every', review.intervalText());
    review.setSummary('file-transfer-wizard-summary-arrival-window', review.arrivalWindowText());
    review.setSummary('file-transfer-wizard-summary-expectation', review.expectationText());
};

// ////////////////////////////////////////////////////////////////////////

// A review value carrying a path or a pattern wears the inline code look
review.codeValue = function(text) {

    var out = document.createElement('code');
    out.className = 'wizard-review-code';
    out.textContent = text;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What a check reads as on the review - its summary, or Off
review.monitoringValue = function(text) {

    var out = text;

    if(out === '') {
        out = review.config_own.offText;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Opens the named popover on the line it belongs to - what an Edit link of
// the review does once it has jumped to the step.
review._buildEdit = function(descriptorName, linkId) {

    var out = function() {
        wizard.forms.open(descriptorName, document.getElementById(linkId));
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Renders the review step from the form - invoked by the kit each time
// the last step opens
review.render = function() {

    var labels = wizard.config_own.labels;
    var groups = wizard.config_own.groups;

    // How the readiness check reads on the review ..
    var readyText;

    if(wizard.field('ready_how').val() === 'stability') {
        readyText = 'Stable size, ' + review.durationText(wizard.field('stability_delay').val()) + ' between checks';
    }
    else {
        readyText = 'Marker file with the ' + wizard.field('marker_suffix').val() + ' suffix';
    }

    // .. how the file locking reads ..
    var isLocking = wizard.field('should_claim').is(':checked');
    var lockingText = isLocking ? labels.lockingOn : labels.lockingOff;

    // .. and how the post-processing reads.
    var successText;

    if(wizard.field('on_success').val() === 'move') {
        successText = 'Move to ' + wizard.field('move_directory').val() + '/';
    }
    else {
        successText = 'Delete';
    }

    var isActive = wizard.field('is_active').is(':checked');

    review.renderGroups([
        {label: groups.source, step: 0, rows: [
            ['Name', wizard.field('name').val()],
            ['Connection', $('#file-transfer-wizard-context-badge').text()],
            ['Directory', review.codeValue(wizard.field('directory').val())],
            ['File pattern', review.codeValue(wizard.field('pattern').val())],
            ['Encoding', wizard.field('encoding').find('option:selected').text()],
            ['Readiness check', readyText],
            ['File locking', lockingText]
        ]},
        {label: groups.processing, step: 1, rows: [
            ['Service', wizard.field('scheduler_service').val()],
            ['Service input', labels.serviceInput],
            ['Post-processing', successText],
            ['Retry policy', review.retriesText()]
        ]},
        {label: groups.schedule, step: 1,
            edit: review._buildEdit('run_every', 'file-transfer-wizard-edit-run-every'),
            rows: [
            ['Polling interval', review.intervalText()],
            ['Start time', wizard.field('start_date').val()],
            ['Arrival monitoring', review.monitoringValue(review.arrivalWindowText())],
            ['Daily delivery check', review.monitoringValue(review.expectationText())],
            ['Active', isActive ? 'Yes' : 'No']
        ]}
    ]);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
