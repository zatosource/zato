// File transfer schedule - the help texts behind the "How does it work?"
// badges of the schedule wizard. One entry per labeled field or control -
// the entries keyed by id_* are said again by the kit under the ids the
// popover inputs take, so one text describes a field wherever it is shown.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.file_transfer.field_descriptions = {

    // Step 1 - what to pick up
    'id_name': 'A unique name for this schedule. Used to identify it in logs and on the schedules list.',
    'id_is_active': 'Whether this schedule runs at all. ' +
        'An inactive schedule keeps its configuration but never scans the directory.',
    'id_directory': 'The remote directory looked into on each run, e.g. /incoming/invoices.',
    'id_pattern': 'Which files in the directory count. Shell-style wildcards, e.g. *.csv or report-*.xml. ' +
        'Everything else is ignored.',
    'file-transfer-wizard-edit-ready': 'How Zato determines that an upload is complete. ' +
        'A file still being uploaded by the other side must not be picked up halfway through. ' +
        'Either the file stops changing between two looks, or the sender confirms it by placing ' +
        'a marker file next to it - invoices.csv waits for invoices.csv.done.',
    'id_stability_delay': 'How many seconds pass between the two looks. ' +
        'If size and modification time did not change in between, the file is taken to be complete.',
    'id_marker_suffix': 'The suffix of the marker file the sender places next to each upload, ' +
        'e.g. with .done, invoices.csv waits for invoices.csv.done. ' +
        'The marker is removed together with the file.',
    'id_should_claim': 'When on, each file is renamed to name.processing before anything reads it, ' +
        'so another environment watching the same directory never takes the same file. ' +
        'Leave off when this platform is the only consumer.',

    // Step 2 - what happens next
    'id_scheduler_service': 'The service invoked once per each file received. ' +
        'It gets the file\'s data, name, size and modification time on input.',
    'file-transfer-wizard-edit-success': 'What happens to a file once the service has finished with it - ' +
        'it is either moved away or deleted, so it is never picked up twice. ' +
        'A moved file stays available for audits, a deleted one saves space on the remote side.',
    'id_move_directory': 'A subdirectory of the watched directory the processed files are moved into, ' +
        'e.g. processed.',
    'file-transfer-wizard-edit-run-every': 'How often the directory is looked into, e.g. every 5 minutes.',
    'id_run_every': 'How often the directory is looked into, e.g. every 5 minutes.',
    'id_start_date': 'When the first run takes place, in your own timezone. ' +
        'Subsequent runs follow the interval above.',
    'file-transfer-wizard-edit-arrival-window': 'Whether a file is expected to arrive regularly. ' +
        'If none arrives for this many seconds, an alert is raised. ' +
        'Zero means no expectation and no alerts about missing files.',
    'id_arrival_window': 'How many seconds may pass without a file before an alert is raised. ' +
        'Zero means no expectation.'
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
