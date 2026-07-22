// File transfer schedule - the help texts behind the "How does it work?"
// badges of the schedule wizard. One entry per labeled field or control.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.file_transfer.field_descriptions = {

    // Step 1 - what to pick up
    'id_name': 'A unique name for this schedule.<br>Used to identify it in logs<br>and on the schedules list.',
    'id_is_active': 'Whether this schedule runs at all.<br>An inactive schedule keeps its configuration<br>but never looks into the directory.',
    'id_directory': 'The remote directory looked into on each run,<br>e.g. /incoming/invoices.',
    'id_pattern': 'Which files in the directory count.<br>Shell-style wildcards, e.g. *.csv<br>or report-*.xml. Everything else is ignored.',
    'file-transfer-wizard-ready-title': 'How the platform decides that an upload is complete.<br>A file still being uploaded by the other side<br>must not be picked up halfway through.',
    'id_stability_check_gap': 'How many seconds pass between the two looks.<br>If size and modification time did not change<br>in between, the file is taken to be complete.',
    'id_marker_suffix': 'The suffix of the marker file the sender places<br>next to each upload, e.g. with .done,<br>invoices.csv waits for invoices.csv.done.',
    'id_should_claim': 'When on, each file is renamed to name.processing<br>before anything reads it, so another environment<br>watching the same directory never takes the same file.<br>Leave off when this platform is the only consumer.',

    // Step 2 - what happens next
    'id_scheduler_service': 'The service invoked once per each file received.<br>It gets the file\'s data, name, size<br>and modification time on input.',
    'file-transfer-wizard-success-title': 'What happens to a file once the service<br>has finished with it - it is either moved away<br>or deleted, so it is never picked up twice.',
    'id_move_directory': 'A subdirectory of the watched directory<br>the processed files are moved into,<br>e.g. processed.',
    'id_run_every': 'How often the directory is looked into,<br>e.g. every 5 minutes.',
    'id_start_date': 'When the first run takes place, in your own timezone.<br>Subsequent runs follow the interval above.'
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
