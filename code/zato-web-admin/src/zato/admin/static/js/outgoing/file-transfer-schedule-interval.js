// File transfer schedules - how often a schedule looks into its directory.
// The wizard and the schedule list edit it in the same popover micro-form.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var interval = {};
$.fn.zato.outgoing.file_transfer.interval = interval;

// ////////////////////////////////////////////////////////////////////////

// The count and the unit it is counted in.
interval.fields = ['run_every', 'run_unit'];

// The title of the popover the two are edited in.
interval.formTitle = 'How often to look';

// ////////////////////////////////////////////////////////////////////////

// The micro-form - one count with its unit select next to it.
interval.descriptor = {
    title: interval.formTitle,
    fitContent: true,
    pages: [[
        {field: 'run_every', label: 'Run every', kind: 'number', unitField: 'run_unit'}
    ]]
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
