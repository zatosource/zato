// File transfer schedule wizard - the wizard kit instance.
//
// The page is rendered by zato/outgoing/file-transfer-schedule-wizard.html
// and one set of code serves both SFTP and SMB schedules. The generic
// machinery - the step strip, the name badge, the footer and the save -
// comes from the wizard kit, configured here. This file holds only what
// the schedule wizard has of its own: the required fields, the help texts,
// the wizard-wide overview and the live name check against the schedules
// the connection already has. The micro-forms and the decision lines live
// in forms.js and the summaries plus the review step in review.js.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.outgoing.file_transfer.wizard;

// ////////////////////////////////////////////////////////////////////////

wizard.config_own = {

    // What the button ending the action says
    saveLabel: 'Save',

    // The sections the review is read in, each group of answers under its own -
    // the missing targets below name them too, which is why they are here rather
    // than in the review module, loaded after this one
    groups: {
        source: 'File source',
        processing: 'Processing',
        schedule: 'Schedule and monitoring'
    },

    // The fixed labels of the review step
    labels: {
        serviceInput: 'File data, name, size and modification time, one invocation per file',
        lockingOn: 'On, each file is renamed with the .processing suffix before it is read',
        lockingOff: 'Off'
    },

    // Where the live name check sends its questions, together with the
    // connection whose schedules the name has to be unique among and the
    // schedule that keeps its own name on edit - all three filled in by
    // init from what the template resolved
    nameCheckUrl: '',
    connId: '',
    scheduleId: ''
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.wizard_kit.core.setup(wizard, {

    idPrefix: 'file-transfer-wizard',
    formSelector: '#create-form',

    // How many steps the wizard has
    stepCount: 3,
    finishLabel: wizard.config_own.saveLabel,

    // The rows the "How does it work?" badge walks through - the card
    // header with the wizard-wide overview, then anything on a step
    // body holding a labeled field
    helpRowSelector: '.dashboard-card-header, .wizard-name-row, .wizard-field-row, .decision-line',

    // Fields that must not be empty on submit - the ones edited only in
    // popovers always carry their defaults, so they are safe to require outright
    requiredFields: [
        'name',
        'directory',
        'pattern',
        'stability_delay',
        'marker_suffix',
        'scheduler_service',
        'move_directory',
        'run_every',
        'start_date',
        'arrival_window',
        'max_attempts',
        'retry_backoff',
        'quarantine_directory',
        'expected_files',
        'expected_days'
    ],

    // Where each of them is read on the review and answered on its step - the
    // fields edited in popovers are answered where their popover opens, so the
    // line opening it is what a refused save points at
    missingTargets: {
        name:              {group: wizard.config_own.groups.source, label: 'Name'},
        directory:         {group: wizard.config_own.groups.source, label: 'Directory'},
        pattern:           {group: wizard.config_own.groups.source, label: 'File pattern'},
        stability_delay:   {group: wizard.config_own.groups.source, label: 'Readiness check',
                            anchorSelector: '#file-transfer-wizard-line-ready'},
        marker_suffix:     {group: wizard.config_own.groups.source, label: 'Readiness check',
                            anchorSelector: '#file-transfer-wizard-line-ready'},
        scheduler_service: {group: wizard.config_own.groups.processing, label: 'Service',
                            anchorSelector: '#file-transfer-wizard-service-row'},
        move_directory:    {group: wizard.config_own.groups.processing, label: 'Post-processing',
                            anchorSelector: '#file-transfer-wizard-line-success'},
        max_attempts:      {group: wizard.config_own.groups.processing, label: 'Retry policy',
                            anchorSelector: '#file-transfer-wizard-line-retries'},
        retry_backoff:     {group: wizard.config_own.groups.processing, label: 'Retry policy',
                            anchorSelector: '#file-transfer-wizard-line-retries'},
        quarantine_directory: {group: wizard.config_own.groups.processing, label: 'Retry policy',
                            anchorSelector: '#file-transfer-wizard-line-retries'},
        run_every:         {group: wizard.config_own.groups.schedule, label: 'Polling interval',
                            anchorSelector: '#file-transfer-wizard-line-run-every'},
        start_date:        {group: wizard.config_own.groups.schedule, label: 'Start time'},
        arrival_window:    {group: wizard.config_own.groups.schedule, label: 'Arrival monitoring',
                            anchorSelector: '#file-transfer-wizard-line-arrival-window'},
        expected_files:    {group: wizard.config_own.groups.schedule, label: 'Daily delivery check',
                            anchorSelector: '#file-transfer-wizard-line-expectation'},
        expected_days:     {group: wizard.config_own.groups.schedule, label: 'Daily delivery check',
                            anchorSelector: '#file-transfer-wizard-line-expectation'}
    },

// ////////////////////////////////////////////////////////////////////////

    onInit: function() {

        // The decision lines of both steps and the popovers behind them ..
        wizard.forms.initLines();

        // .. the searchable select for services ..
        $.fn.zato.turn_selects_into_chosen('#file-transfer-wizard-service-row');

        // .. keep the services fresh while the page is open -
        // no reloading to pick up new ones ..
        $.fn.zato.live_form_updates.register('create', [
            {object_type: 'service', target_select: '#id_scheduler_service'}
        ]);
        $.fn.zato.live_form_updates.start('create');

        // .. the date-time picker for the first run, in the
        // user profile's own date and time format ..
        $('#id_start_date').datetimepicker({
            'dateFormat': $('#js_date_format').val(),
            'timeFormat': $('#js_time_format').val(),
            'ampm': $.fn.zato.to_bool($('#js_ampm').val())
        });

        // .. and the live check of the name against the connection's own
        // schedules, which live with the connection rather than in a table
        // of their own, so the check goes to a page-specific endpoint with
        // the name badge in the header following its verdicts.
        $.fn.zato.validate_unique(wizard.fieldSelector('name'), 'file_transfer_schedule', 'name',
            wizard.nameCheckFilter, wizard.onNameCheckResult, wizard.config_own.nameCheckUrl);
    }
});

// ////////////////////////////////////////////////////////////////////////

// What the name check carries along - which connection's schedules to look
// among and which schedule keeps its own name on edit.
wizard.nameCheckFilter = function() {

    var ownConfig = wizard.config_own;

    var out = {
        'conn_id': ownConfig.connId,
        'schedule_id': ownConfig.scheduleId
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The page hands its resolved urls and ids over once the DOM is ready,
// and the kit's own init does the rest.
wizard._kitInit = wizard.init;

wizard.init = function(options) {

    var ownConfig = wizard.config_own;

    ownConfig.nameCheckUrl = options.name_check_url;
    ownConfig.connId = options.conn_id;
    ownConfig.scheduleId = options.schedule_id;

    wizard._kitInit(options);
};

// ////////////////////////////////////////////////////////////////////////

// The help texts behind every "How does it work?" badge on the page - the
// shared map, re-keyed for the popover inputs, plus the wizard-wide overview.
wizard.helpDescriptions = function() {

    var shared = $.fn.zato.outgoing.file_transfer.field_descriptions;

    // The popover micro-forms name their inputs after the fields they mirror,
    // so the kit says each text again under the id its input takes
    var out = wizard.forms.helpDescriptions(shared);

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

        '<p>A schedule polls a directory of this connection at a fixed interval ' +
        'and invokes a service once for each new file found there.</p>' +

        '<p><span class="wizard-title-help-step">01</span> defines the file source - ' +
        'the directory, the file pattern and the readiness check that determines when an upload is complete. ' +
        '<span class="wizard-title-help-step">02</span> defines the processing - the service, ' +
        'the post-processing, the retry policy, the polling interval and the monitoring of deliveries. ' +
        '<span class="wizard-title-help-step">03</span> lists the configuration before the schedule is saved.</p>' +

        '<details class="wizard-title-help-details">' +
        '<summary>File transfer overview</summary>' +
        '<div class="wizard-title-help-primer">' +

        '<p>External systems deliver files such as invoices, orders and reports to a directory, ' +
        'and the schedule collects them at each polling interval.</p>' +

        '<p>A file is read only after the readiness check confirms that its upload is complete. ' +
        'After processing, the file is moved to the target directory or deleted, ' +
        'so that no file is processed twice.</p>' +

        '<p>A schedule requires a name, a directory and a service, ' +
        'and every other setting has a default value.</p>' +

        '</div>' +
        '</details>' +
        '</div>';

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
