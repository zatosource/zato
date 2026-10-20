// File transfer schedule wizard - the decision lines and the micro-forms
// they open.
//
// The popover engine and the segments come from the wizard kit - this file
// declares which micro-forms the schedule wizard has, paints the segments
// strips off the hidden mode fields and wires the edit links beside them.
// The summaries the links carry are recomputed in review.js.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.outgoing.file_transfer.wizard;
var forms = wizard.forms;

// ////////////////////////////////////////////////////////////////////////

forms.config_own = {

    // The two ways a file counts as ready and the two things done with one
    // once it is processed - the names are the values the hidden mode
    // fields carry and the backend reads
    readyOptions: [
        {name: 'stability', label: 'Stable size', is_active: true},
        {name: 'marker',    label: 'Marker file', is_active: true}
    ],

    successOptions: [
        {name: 'move',   label: 'Move',   is_active: true},
        {name: 'delete', label: 'Delete', is_active: true}
    ],

    // The arrival monitoring and the daily delivery check are off while
    // their count is zero
    monitoringOptions: [
        {name: 'off', label: 'Off', is_active: true},
        {name: 'on',  label: 'On',  is_active: true}
    ],

    // What a check that is turned on starts out with
    monitoringDefaults: {
        arrival_window: '3600',
        expected_files: '1',
        expected_by: '08:00'
    },

    // The ISO weekday numbers the expected days are stored as, with the names they read as
    weekdays: [
        {number: '1', label: 'Mon'},
        {number: '2', label: 'Tue'},
        {number: '3', label: 'Wed'},
        {number: '4', label: 'Thu'},
        {number: '5', label: 'Fri'},
        {number: '6', label: 'Sat'},
        {number: '7', label: 'Sun'}
    ],

    // What separates the weekday numbers in the stored field
    weekdaySeparator: ',',

    // The attribute a weekday option keeps its number in
    weekdayAttr: 'data-weekday',

    // Where the strips are painted
    readySlotId: 'file-transfer-wizard-slot-ready',
    successSlotId: 'file-transfer-wizard-slot-success',
    arrivalSlotId: 'file-transfer-wizard-slot-arrival-window',
    expectationSlotId: 'file-transfer-wizard-slot-expectation',

    // Which popover the readiness edit link opens, per mode
    readyDescriptors: {
        stability: 'ready_stability',
        marker: 'ready_marker'
    }
};

// ////////////////////////////////////////////////////////////////////////

// A page is a list of entries. An entry is either one field spec, shown on
// its own line, or a list of field specs, shown side by side in one row.
$.fn.zato.micro_forms.setup(wizard, {

    // The class the popovers wear, under which wizard-kit.css sizes their switches
    popupClass: 'wizard-micro-form',

    // A count set to zero in a popover turns its check off, so the strips repaint with the summaries
    onDone: function() {
        forms.renderArrivalSegments();
        forms.renderExpectationSegments();
        wizard.review.refreshSummaries();
    },

    descriptors: {

        'ready_stability': {
            title: 'Stable size check',
            pages: [[
                {field: 'stability_delay', label: 'Check interval (seconds)', kind: 'number'}
            ]]
        },

        'ready_marker': {
            title: 'Marker file',
            pages: [[
                {field: 'marker_suffix', label: 'Marker file suffix', kind: 'text'}
            ]]
        },

        'success_move': {
            title: 'Move after processing',
            pages: [[
                {field: 'move_directory', label: 'Target directory', kind: 'text'}
            ]]
        },

        // Shared with the schedule list
        'run_every': $.fn.zato.outgoing.file_transfer.interval.descriptor,

        'arrival_window': {
            title: 'Arrival monitoring',
            pages: [[
                {field: 'arrival_window', label: 'Maximum time without a file (seconds)', kind: 'number'}
            ]]
        },

        'expectation': {
            title: 'Daily delivery check',
            width: '360px',
            pages: [[
                [
                    {field: 'expected_files', label: 'Minimum file count', kind: 'number'},
                    {field: 'expected_by', label: 'Deadline (local time)', kind: 'text', placeholder: 'HH:MM'}
                ],
                {field: 'expected_days', label: 'Days of week', kind: 'weekdays'}
            ]]
        },

        'retries': {
            title: 'Retry policy',
            width: '360px',
            pages: [[
                [
                    {field: 'max_attempts', label: 'Maximum attempts', kind: 'number', min: 0},
                    {field: 'retry_backoff', label: 'Initial delay (seconds)', kind: 'number'}
                ],
                {field: 'quarantine_directory', label: 'Quarantine directory', kind: 'text'}
            ]]
        }
    }
});

// ////////////////////////////////////////////////////////////////////////

// The days of the week as an option strip in which any number of days may be picked,
// stored as the comma-separated ISO numbers of the days picked.
forms.registerKind('weekdays', {

    build: function(fieldSpec, row) {

        var ownConfig = forms.config_own;
        var stripId = forms.inputId(fieldSpec.field);
        var picked = wizard.field(fieldSpec.field).val().split(ownConfig.weekdaySeparator);

        var label = document.createElement('label');
        label.className = 'micro-form-label';
        label.setAttribute('for', stripId);
        label.textContent = fieldSpec.label;
        row.appendChild(label);

        var strip = document.createElement('div');
        strip.className = 'decision-segments dashboard-tabs file-transfer-wizard-weekdays';
        strip.id = stripId;

        ownConfig.weekdays.forEach(function(weekday) {

            var button = document.createElement('button');
            button.type = 'button';
            button.className = 'decision-segment dashboard-tab';
            button.setAttribute(ownConfig.weekdayAttr, weekday.number);
            button.textContent = weekday.label;

            if(picked.indexOf(weekday.number) !== -1) {
                button.className = button.className + ' decision-segment-active dashboard-tab-active';
            }

            button.addEventListener('click', function() {
                button.classList.toggle('decision-segment-active');
                button.classList.toggle('dashboard-tab-active');
            });

            strip.appendChild(button);
        });

        row.appendChild(strip);
    },

    save: function(popper, fieldSpec) {

        var ownConfig = forms.config_own;
        var strip = popper.querySelector('#' + forms.inputId(fieldSpec.field));
        var pickedButtons = strip.querySelectorAll('.decision-segment-active');
        var numbers = [];

        for(var buttonIdx = 0; buttonIdx < pickedButtons.length; buttonIdx++) {
            var number = pickedButtons[buttonIdx].getAttribute(ownConfig.weekdayAttr);
            numbers.push(number);
        }

        wizard.field(fieldSpec.field).val(numbers.join(ownConfig.weekdaySeparator));
    }
});

// ////////////////////////////////////////////////////////////////////////

// Wires up the decision lines of both steps - the strips repaint off the
// hidden fields, which is also what prefills the edit flow, and each edit
// link opens the popover its parameter is answered in.
forms.initLines = function() {

    forms.renderReadySegments();
    forms.renderSuccessSegments();
    forms.renderArrivalSegments();
    forms.renderExpectationSegments();

    $('#file-transfer-wizard-edit-ready').on('click', function() {

        // The readiness parameter is the current mode's own - the check interval
        // for a stable size, the suffix for a marker file
        var mode = wizard.field('ready_how').val();
        forms.open(forms.config_own.readyDescriptors[mode], this);
    });

    $('#file-transfer-wizard-edit-success').on('click', function() {
        forms.open('success_move', this);
    });

    $('#file-transfer-wizard-edit-run-every').on('click', function() {
        forms.open('run_every', this);
    });

    $('#file-transfer-wizard-edit-arrival-window').on('click', function() {
        forms.open('arrival_window', this);
    });

    $('#file-transfer-wizard-edit-expectation').on('click', function() {
        forms.open('expectation', this);
    });

    $('#file-transfer-wizard-edit-retries').on('click', function() {
        forms.open('retries', this);
    });
};

// ////////////////////////////////////////////////////////////////////////

forms.renderReadySegments = function() {

    var ownConfig = forms.config_own;
    var current = wizard.field('ready_how').val();

    $.fn.zato.decision_lines.setSegments(ownConfig.readySlotId, ownConfig.readyOptions, current, function(name) {
        wizard.field('ready_how').val(name);
        forms.renderReadySegments();
        wizard.review.refreshSummaries();
    });
};

// ////////////////////////////////////////////////////////////////////////

forms.renderSuccessSegments = function() {

    var ownConfig = forms.config_own;
    var current = wizard.field('on_success').val();

    $.fn.zato.decision_lines.setSegments(ownConfig.successSlotId, ownConfig.successOptions, current, function(name) {
        wizard.field('on_success').val(name);
        forms.renderSuccessSegments();
        wizard.review.refreshSummaries();
    });
};

// ////////////////////////////////////////////////////////////////////////

// Whether the check whose count is in the given field is on - a count of zero turns it off.
forms.isMonitoringOn = function(countField) {

    var count = parseInt(wizard.field(countField).val());
    var out = count > 0;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Paints the Off and On strip of one check. Turning it on gives every field
// of the check that is still empty or zero its default, turning it off zeroes its count.
forms.renderMonitoringSegments = function(slotId, countField, defaultFields, renderSelf) {

    var ownConfig = forms.config_own;
    var current = forms.isMonitoringOn(countField) ? 'on' : 'off';

    $.fn.zato.decision_lines.setSegments(slotId, ownConfig.monitoringOptions, current, function(name) {

        if(name === 'on') {
            defaultFields.forEach(function(fieldName) {
                var field = wizard.field(fieldName);
                var value = field.val();

                if(value === '' || value === '0') {
                    field.val(ownConfig.monitoringDefaults[fieldName]);
                }
            });
        }
        else {
            wizard.field(countField).val('0');
        }

        renderSelf();
        wizard.review.refreshSummaries();
    });
};

// ////////////////////////////////////////////////////////////////////////

forms.renderArrivalSegments = function() {
    forms.renderMonitoringSegments(forms.config_own.arrivalSlotId, 'arrival_window',
        ['arrival_window'], forms.renderArrivalSegments);
};

// ////////////////////////////////////////////////////////////////////////

forms.renderExpectationSegments = function() {
    forms.renderMonitoringSegments(forms.config_own.expectationSlotId, 'expected_files',
        ['expected_files', 'expected_by'], forms.renderExpectationSegments);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
