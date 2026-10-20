// File transfer schedule - the help texts behind the "How does it work?"
// badges of the schedule wizard. One entry per labeled field or control -
// the entries keyed by id_* are said again by the kit under the ids the
// popover inputs take, so one text describes a field wherever it is shown.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.file_transfer.field_descriptions = {

    // Step 1 - the file source
    'id_name': 'The unique name of the schedule, used in logs and on the list of schedules.',
    'id_is_active': 'Whether the schedule runs. ' +
        'An inactive schedule keeps its configuration and does not poll the directory.',
    'id_directory': 'The remote directory polled on each run, e.g. /incoming/invoices.',
    'id_pattern': 'The files of the directory that are processed, as shell-style wildcards, e.g. *.csv or report-*.xml. ' +
        'All other files are ignored.',
    'file-transfer-wizard-edit-ready': 'How the schedule determines that an upload is complete, ' +
        'so that no file is read while it is still being written. ' +
        'Stable size reads a file once its size and modification time no longer change between two checks. ' +
        'Marker file reads a file once the sender places a marker file next to it, ' +
        'e.g. invoices.csv is read once invoices.csv.done exists.',
    'id_stability_delay': 'The number of seconds between the two checks. ' +
        'A file whose size and modification time are the same in both checks is complete.',
    'id_marker_suffix': 'The suffix of the marker file the sender places next to each file, ' +
        'e.g. with .done, invoices.csv is read once invoices.csv.done exists. ' +
        'The marker file is removed together with the file.',
    'id_should_claim': 'When on, each file is renamed with the .processing suffix before it is read, ' +
        'so that no other environment polling the same directory processes the same file. ' +
        'Required only when more than one environment polls the directory.',

    // Step 2 - the processing
    'id_scheduler_service': 'The service invoked once for each file. ' +
        'Its input contains the data, name, size and modification time of the file.',
    'file-transfer-wizard-edit-success': 'What is done with a file after the service processes it. ' +
        'Move keeps the file in the target directory for audit purposes, Delete removes it from the remote system. ' +
        'Either way, no file is processed twice.',
    'id_move_directory': 'The subdirectory of the polled directory that processed files are moved to, e.g. processed.',
    'file-transfer-wizard-edit-retries': 'What is done with a file the service fails to process. ' +
        'Each attempt waits twice as long as the attempt before it. After the last attempt, ' +
        'the file is moved to the quarantine directory, from which it can be returned for processing.',
    'id_max_attempts': 'The number of attempts before a file is moved to the quarantine directory. ' +
        'Zero means no limit.',
    'id_retry_backoff': 'The number of seconds before the second attempt. Each later attempt waits twice as long.',
    'id_quarantine_directory': 'The directory that files are moved to after the last attempt, ' +
        'relative to the polled directory.',
    'file-transfer-wizard-edit-run-every': 'How often the directory is polled, e.g. every 5 minutes.',
    'id_run_every': 'How often the directory is polled, e.g. every 5 minutes.',
    'id_start_date': 'The date and time of the first run, in the timezone of the user profile. ' +
        'Subsequent runs follow the polling interval.',
    'file-transfer-wizard-edit-arrival-window': 'When on, an alert is raised once no file has arrived ' +
        'for the configured time.',
    'id_arrival_window': 'The number of seconds without a new file after which an alert is raised.',
    'file-transfer-wizard-edit-expectation': 'When on, an alert is raised if fewer files than expected ' +
        'have arrived by the deadline on one of the configured days of week.',
    'id_expected_files': 'The minimum number of files expected by the deadline.',
    'id_expected_by': 'The local time by which the files are expected, in the HH:MM format, e.g. 08:00.',
    'id_expected_days': 'The days of week on which the daily delivery check applies.'
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
