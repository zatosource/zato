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

// The one-line summaries beside the segments and on the Runs line -
// recomputed from the form each time an answer changes.
review.refreshSummaries = function() {

    // How the readiness parameter reads beside its strip ..
    var readyMode = wizard.field('ready_how').val();
    var readyText;

    if(readyMode === 'stability') {
        readyText = 'checked twice, ' + wizard.field('stability_delay').val() + 's apart';
    }
    else {
        readyText = 'suffix ' + wizard.field('marker_suffix').val();
    }

    review.setSummary('file-transfer-wizard-summary-ready', readyText);

    // .. a deleted file has no parameter to edit, so its line loses the
    // link - an empty summary is what takes it off the screen ..
    var onSuccess = wizard.field('on_success').val();
    var successText = '';

    if(onSuccess === 'move') {
        successText = 'to ' + wizard.field('move_directory').val() + '/';
    }

    review.setSummary('file-transfer-wizard-summary-success', successText);

    // .. how often the directory is looked into ..
    var runEvery = 'Every ' + wizard.field('run_every').val() + ' ' + wizard.field('run_unit').val();
    review.setSummary('file-transfer-wizard-summary-run-every', runEvery);

    // .. and whether a file is expected within some window at all.
    review.setSummary('file-transfer-wizard-summary-arrival-window', review.arrivalWindowText());
};

// ////////////////////////////////////////////////////////////////////////

// How the arrival expectation reads - a window of zero means none was declared
review.arrivalWindowText = function() {

    var arrivalWindow = parseInt(wizard.field('arrival_window').val());
    var out;

    if(arrivalWindow) {
        out = 'Alert after ' + arrivalWindow + 's without one';
    }
    else {
        out = 'No expectation';
    }

    return out;
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

    // How the readiness pick reads on the review ..
    var readyMode = wizard.field('ready_how').val();
    var readyText;

    if(readyMode === 'stability') {
        var checkGap = wizard.field('stability_delay').val();
        readyText = 'When it stops changing - checked twice, ' + checkGap + ' seconds apart';
    }
    else {
        var markerSuffix = wizard.field('marker_suffix').val();
        readyText = 'When a marker file with the ' + markerSuffix + ' suffix appears';
    }

    // .. how the claim toggle reads ..
    var isClaim = wizard.field('should_claim').is(':checked');
    var claimText = isClaim ? labels.claimYes : labels.claimNo;

    // .. and how the post-processing pick reads.
    var onSuccess = wizard.field('on_success').val();
    var successText;

    if(onSuccess === 'move') {
        var moveDirectory = wizard.field('move_directory').val();
        successText = 'Moved to ' + moveDirectory + '/';
    }
    else {
        successText = 'Deleted';
    }

    var isActive = wizard.field('is_active').is(':checked');
    var runEvery = wizard.field('run_every').val() + ' ' + wizard.field('run_unit').val();

    review.renderGroups([
        {label: groups.pickup, step: 0, rows: [
            ['Name', wizard.field('name').val()],
            ['Connection', $('#file-transfer-wizard-context-badge').text()],
            ['Directory', review.codeValue(wizard.field('directory').val())],
            ['File pattern', review.codeValue(wizard.field('pattern').val())],
            ['A file is ready', readyText],
            ['Claim before processing', claimText]
        ]},
        {label: groups.processing, step: 1, rows: [
            ['Service', wizard.field('scheduler_service').val()],
            ['Invoked with', labels.invokedWith],
            ['After success', successText],
            ['After failure', labels.afterFailure]
        ]},
        {label: groups.schedule, step: 1,
            edit: review._buildEdit('run_every', 'file-transfer-wizard-edit-run-every'),
            rows: [
            ['Run every', runEvery],
            ['Start time', wizard.field('start_date').val()],
            ['Expects a file', review.arrivalWindowText()],
            ['Active', isActive ? 'Yes' : 'No']
        ]}
    ]);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
