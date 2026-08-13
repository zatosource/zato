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

// A page is a list of entries. An entry is either one field spec, shown on
// its own line, or a list of field specs, shown side by side in one row.
$.fn.zato.wizard_kit.forms.setup(wizard, {

    descriptors: {

        'ready_stability': {
            title: 'When it stops changing',
            pages: [[
                {field: 'stability_delay', label: 'Seconds between the two looks', kind: 'number', width: '220px'}
            ]]
        },

        'ready_marker': {
            title: 'When a marker file appears',
            pages: [[
                {field: 'marker_suffix', label: 'Marker suffix', kind: 'text', width: '220px'}
            ]]
        },

        'success_move': {
            title: 'Move it away',
            pages: [[
                {field: 'move_directory', label: 'Directory', kind: 'text', width: '220px'}
            ]]
        },

        'run_every': {
            title: 'How often to look',
            pages: [[
                {field: 'run_every', label: 'Run every', kind: 'number', unitField: 'run_unit', width: '220px'}
            ]]
        }
    }
});

// ////////////////////////////////////////////////////////////////////////

forms.config_own = {

    // The two ways a file counts as ready and the two things done with one
    // once it is processed - the names are the values the hidden mode
    // fields carry and the backend reads
    readyOptions: [
        {name: 'stability', label: 'Stops changing', is_active: true},
        {name: 'marker',    label: 'Marker file',    is_active: true}
    ],

    successOptions: [
        {name: 'move',   label: 'Moved away', is_active: true},
        {name: 'delete', label: 'Deleted',    is_active: true}
    ],

    // Where the two strips are painted
    readySlotId: 'file-transfer-wizard-slot-ready',
    successSlotId: 'file-transfer-wizard-slot-success',

    // Which popover the readiness edit link opens, per mode
    readyDescriptors: {
        stability: 'ready_stability',
        marker: 'ready_marker'
    }
};

// ////////////////////////////////////////////////////////////////////////

// Wires up the decision lines of both steps - the strips repaint off the
// hidden fields, which is also what prefills the edit flow, and each edit
// link opens the popover its parameter is answered in.
forms.initLines = function() {

    forms.renderReadySegments();
    forms.renderSuccessSegments();

    $('#file-transfer-wizard-edit-ready').on('click', function() {

        // The readiness parameter is the current mode's own - the check gap
        // for stability, the suffix for the marker file
        var mode = wizard.field('ready_how').val();
        forms.open(forms.config_own.readyDescriptors[mode], this);
    });

    $('#file-transfer-wizard-edit-success').on('click', function() {
        forms.open('success_move', this);
    });

    $('#file-transfer-wizard-edit-run-every').on('click', function() {
        forms.open('run_every', this);
    });
};

// ////////////////////////////////////////////////////////////////////////

forms.renderReadySegments = function() {

    var ownConfig = forms.config_own;
    var current = wizard.field('ready_how').val();

    $.fn.zato.wizard_kit.lines.setSegments(ownConfig.readySlotId, ownConfig.readyOptions, current, function(name) {
        wizard.field('ready_how').val(name);
        forms.renderReadySegments();
        wizard.review.refreshSummaries();
    });
};

// ////////////////////////////////////////////////////////////////////////

forms.renderSuccessSegments = function() {

    var ownConfig = forms.config_own;
    var current = wizard.field('on_success').val();

    $.fn.zato.wizard_kit.lines.setSegments(ownConfig.successSlotId, ownConfig.successOptions, current, function(name) {
        wizard.field('on_success').val(name);
        forms.renderSuccessSegments();
        wizard.review.refreshSummaries();
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
