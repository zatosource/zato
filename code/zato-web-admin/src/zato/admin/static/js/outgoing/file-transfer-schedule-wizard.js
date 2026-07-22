// File transfer schedule wizard - the wizard kit instance.
//
// The page is rendered by zato/outgoing/file-transfer-schedule-wizard.html.
// The generic machinery - the step strip, the name badge, the choice cards,
// the footer and the save - comes from the wizard kit, configured here.
// This file holds only what the schedule wizard has of its own: the
// required fields, the readiness and post-processing choices, the help
// texts and the review step.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.outgoing.file_transfer.wizard;

// The fixed labels of the review step
wizard.labels = {

    invokedWith: 'One invocation per file - data, name, size and modification time',
    afterFailure: 'The file stays in place and is retried on the next run',

    claimYes: 'Yes - renamed to name.processing first',
    claimNo: 'No - this platform is the only consumer'
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.wizard_kit.core.setup(wizard, {

    idPrefix: 'file-transfer-wizard',
    formSelector: '#create-form',

    // How many steps the wizard has
    stepCount: 3,

    // The rows the "How does it work?" badge walks through - the card
    // header with the wizard-wide overview, then anything on a step
    // body holding a labeled field
    helpRowSelector: '.dashboard-card-header, .wizard-name-row, .wizard-field-row, ' +
        '.wizard-section-title, .wizard-claim-row',

    // Fields that must not be empty on submit - the conditional ones
    // always carry their defaults, so they are safe to require outright
    requiredFields: [
        'name',
        'directory',
        'pattern',
        'stability_delay',
        'marker_suffix',
        'scheduler_service',
        'move_directory',
        'run_every',
        'start_date'
    ],

// ////////////////////////////////////////////////////////////////////////

    onInit: function() {

        // The readiness cards write their pick into the hidden mode field ..
        var readyChoices = $.fn.zato.wizard_kit.choices.init({
            group: 'ready',
            onChange: function(choiceId) {
                wizard.field('ready_how').val(choiceId);
                wizard.review.refreshSummaries();
            }
        });

        // .. and so do the post-processing cards on step 2 ..
        var successChoices = $.fn.zato.wizard_kit.choices.init({
            group: 'success',
            onChange: function(choiceId) {
                wizard.field('on_success').val(choiceId);
                wizard.review.refreshSummaries();
            }
        });

        // .. the cards follow the hidden fields, which matters when the wizard
        // opens with an existing schedule whose picks differ from the defaults ..
        readyChoices.set(wizard.field('ready_how').val());
        successChoices.set(wizard.field('on_success').val());

        // .. the card summaries follow their inline fields as the user types ..
        wizard.field('stability_delay').on('input', wizard.review.refreshSummaries);
        wizard.field('marker_suffix').on('input', wizard.review.refreshSummaries);
        wizard.field('move_directory').on('input', wizard.review.refreshSummaries);

        // .. the searchable select for services ..
        $.fn.zato.turn_selects_into_chosen('#file-transfer-wizard-service-row');

        // .. keep the services fresh while the page is open -
        // no reloading to pick up new ones ..
        $.fn.zato.live_form_updates.register('create', [
            {object_type: 'service', target_select: '#id_scheduler_service'}
        ]);
        $.fn.zato.live_form_updates.start('create');

        // .. and the date-time picker for the first run, in the
        // user profile's own date and time format.
        $('#id_start_date').datetimepicker({
            'dateFormat': $('#js_date_format').val(),
            'timeFormat': $('#js_time_format').val(),
            'ampm': $.fn.zato.to_bool($('#js_ampm').val())
        });
    }
});

// ////////////////////////////////////////////////////////////////////////

// The popover micro-form engine - this wizard keeps everything inline
// on its steps, so no descriptors, but the kit's close hook still runs
// on each step change.
$.fn.zato.wizard_kit.forms.setup(wizard, {
    descriptors: {}
});

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.wizard_kit.review.setup(wizard);

// ////////////////////////////////////////////////////////////////////////

// The help texts behind every "How does it work?" badge on the page
wizard.helpDescriptions = function() {

    var out = $.extend({}, $.fn.zato.outgoing.file_transfer.field_descriptions);

    // The page title carries the wizard-wide overview
    out['file-transfer-wizard-title'] = wizard.titleHelp();

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The wizard-wide overview shown when the page title is clicked - one of
// the regular "How does it work?" stops. Everyone gets the short pitch,
// and the file transfer primer waits folded inside for those who want
// the background.
wizard.titleHelp = function() {

    var out =
        '<div class="wizard-title-help">' +

        '<p>This wizard creates a schedule - a recurring task that looks into ' +
        'a directory of this connection and hands each new file to a service.</p>' +

        '<p><span class="wizard-title-help-step">01</span> decides what to pick up - ' +
        'which directory, which files and when a file counts as ready. ' +
        '<span class="wizard-title-help-step">02</span> picks the service that handles ' +
        'each file, what happens to it afterwards and how often to look. ' +
        '<span class="wizard-title-help-step">03</span> is a review before the schedule is created.</p>' +

        '<details class="wizard-title-help-details">' +
        '<summary>New to file transfer? A 30-second primer</summary>' +
        '<div class="wizard-title-help-primer">' +

        '<p>Other systems drop files into a directory - invoices, orders, reports - ' +
        'and this platform picks them up on a schedule, so nothing needs to be ' +
        'watched by hand.</p>' +

        '<p>The one thing to get right is not reading a file while it is still ' +
        'being uploaded, which is what the readiness choice on step 01 is for. ' +
        'Once a file is processed, it is moved away or deleted, so it is never ' +
        'picked up twice.</p>' +

        '<p>If in doubt, name the schedule, point it at a directory, pick a ' +
        'service on step 02 and keep the defaults.</p>' +

        '</div>' +
        '</details>' +
        '</div>';

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The one-line summaries in the choice card headers - recomputed from
// the form each time a pick or an inline field changes
wizard.review.refreshSummaries = function() {

    var review = wizard.review;

    var checkGap = wizard.field('stability_delay').val();
    review.setSummary('file-transfer-wizard-summary-stability', 'checked twice, ' + checkGap + 's apart');

    var markerSuffix = wizard.field('marker_suffix').val();
    review.setSummary('file-transfer-wizard-summary-marker', 'suffix ' + markerSuffix);

    var moveDirectory = wizard.field('move_directory').val();
    review.setSummary('file-transfer-wizard-summary-move', 'to ' + moveDirectory + '/');
};

// ////////////////////////////////////////////////////////////////////////

// A review value carrying a path or a pattern wears the inline code look
wizard.review.codeValue = function(text) {

    var out = document.createElement('code');
    out.className = 'wizard-review-code';
    out.textContent = text;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Renders the review step from the form - invoked by the kit each time
// the last step opens
wizard.review.render = function() {

    var review = wizard.review;
    var labels = wizard.labels;

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
        {label: 'Pickup', step: 0, rows: [
            ['Name', wizard.field('name').val()],
            ['Connection', $('#file-transfer-wizard-context-badge').text()],
            ['Directory', review.codeValue(wizard.field('directory').val())],
            ['File pattern', review.codeValue(wizard.field('pattern').val())],
            ['A file is ready', readyText],
            ['Claim before processing', claimText]
        ]},
        {label: 'Processing', step: 1, rows: [
            ['Service', wizard.field('scheduler_service').val()],
            ['Invoked with', labels.invokedWith],
            ['After success', successText],
            ['After failure', labels.afterFailure]
        ]},
        {label: 'Schedule', step: 1, rows: [
            ['Run every', runEvery],
            ['Start time', wizard.field('start_date').val()],
            ['Active', isActive ? 'Yes' : 'No']
        ]}
    ]);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
