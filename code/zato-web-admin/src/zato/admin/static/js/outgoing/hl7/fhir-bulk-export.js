// The Bulk exports page of one outgoing FHIR connection - the connection select and the Run now link.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.namespace('zato.outgoing.hl7.fhir.bulk_export');

var page = $.fn.zato.outgoing.hl7.fhir.bulk_export;

// ////////////////////////////////////////////////////////////////////////

page.config = {
    connSelectSelector: '#fhir-bulk-export-conn-select',
    connNameSelector: '#fhir-bulk-export-conn-name',
    runUrlSelector: '#fhir-bulk-export-run-url',
    errorCellSelector: '#data-table [data-tippy-content]',

    // How long the pointer rests on an error count before its message shows
    tooltipDelayMs: 350,

    startedMessage: 'Bulk export started, job ID `{0}`',

    // How long after a start the page reloads so the new job shows in the table
    reloadAfterMs: 1500
};

// ////////////////////////////////////////////////////////////////////////

$(document).ready(function() {

    var config = page.config;

    $('#data-table').tablesorter();

    $(config.connSelectSelector).change(function() {
        window.location.href = this.value;
    });

    tippy(config.errorCellSelector, {
        delay: [config.tooltipDelayMs, 0],
        placement: 'top'
    });
});

// ////////////////////////////////////////////////////////////////////////

page.run = function() {

    var config = page.config;
    var connName = $(config.connNameSelector).val();
    var runUrl = $(config.runUrlSelector).val();

    var callback = function(data, status) {

        if(status === 'success') {
            var response = JSON.parse(data.responseText);
            var message = String.format(config.startedMessage, response.job_id);
            $.fn.zato.user_message(true, message);

            // The job's first audit event is written by the time the page comes back
            window.setTimeout(function() {
                window.location.reload();
            }, config.reloadAfterMs);
        }
        else {
            $.fn.zato.user_message(false, data.responseText);
        }
    };

    $.fn.zato.post(runUrl, callback, {'conn_name': connName}, 'text');
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
