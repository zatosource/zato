// File transfer schedules - the per-connection list page. Each row is one
// recurring pickup task and the wizard page creates and edits them.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.file_transfer.schedules.config = {

    tableSelector: '#data-table',
    connIdSelector: '#file-transfer-schedules-conn-id',
    editIntervalUrlSelector: '#file-transfer-schedules-edit-interval-url',
    connSelectSelector: '#file-transfer-schedules-conn-select',
    highlightParam: 'highlight',
    highlightClass: 'updated',
    rowIdPrefix: 'tr_',

    // Whether the table has a Command shell column, which the table says about itself
    hasCommandShellAttribute: 'data-has-command-shell',
    hasCommandShellValue: 'true',

    // The logical columns in the order they are shown, the Command shell one only where the table has it
    columns: ['_numbering', '_selection', 'name', '_is_active', '_interval', '_last_run', 'directory', 'pattern', 'service'],
    commandShellColumn: '_command_shell',
    actionColumns: ['_edit', '_delete'],

    saveLabel: 'Save'
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.get_columns = function() {
    var config = $.fn.zato.outgoing.file_transfer.schedules.config;
    var columns = config.columns.slice();

    var hasCommandShell = $(config.tableSelector).attr(config.hasCommandShellAttribute);
    if(hasCommandShell === config.hasCommandShellValue) {
        columns.push(config.commandShellColumn);
    }

    var out = columns.concat(config.actionColumns);
    return out;
}

// ////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    var config = $.fn.zato.outgoing.file_transfer.schedules.config;

    $.fn.zato.time_ago.init_table(config.tableSelector);

    // A row pointed to from the wizard's redirect wears the just-updated look.
    var highlight = $(document).getUrlParam(config.highlightParam);
    if(highlight) {
        $('#' + config.rowIdPrefix + highlight).addClass(config.highlightClass);
    }

    // Each option's value is the URL of that connection's own schedule list.
    $(config.connSelectSelector).change(function() {
        window.location.href = this.value;
    });
});

// ////////////////////////////////////////////////////////////////////////

// The Interval column - each row's interval is edited in the wizard's own popover,
// hosted here on two hidden fields.
$.fn.zato.outgoing.file_transfer.schedules.interval = {

    // The kit installs the popover engine here.
    forms: {},

    config: {

        // Every element the popover makes is named after this.
        idPrefix: 'file-transfer-interval',

        // Which of the micro-forms given to the kit this page opens.
        formName: 'run_every',

        // The link being edited, held while its popover is open.
        link: null
    }
};

// ////////////////////////////////////////////////////////////////////////

// The hidden fields the popover reads and writes.
$.fn.zato.outgoing.file_transfer.schedules.interval.field = function(name) {
    var out = $('#id_' + $.fn.zato.outgoing.file_transfer.schedules.interval.config.idPrefix + '-' + name);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Opens the interval popover on the link that was clicked.
$.fn.zato.outgoing.file_transfer.schedules.interval.open = function(link) {

    var interval = $.fn.zato.outgoing.file_transfer.schedules.interval;
    var fields = $.fn.zato.outgoing.file_transfer.interval.fields;

    interval.config.link = link;

    for(var fieldIdx = 0; fieldIdx < fields.length; fieldIdx++) {
        var name = fields[fieldIdx];
        interval.field(name).val(link.getAttribute('data-' + name));
    }

    interval.forms.open(interval.config.formName, link);
};

// ////////////////////////////////////////////////////////////////////////

// Posts the interval the popover answered with and redraws the link from what was saved.
$.fn.zato.outgoing.file_transfer.schedules.interval.save = function() {

    var config = $.fn.zato.outgoing.file_transfer.schedules.config;
    var interval = $.fn.zato.outgoing.file_transfer.schedules.interval;
    var fields = $.fn.zato.outgoing.file_transfer.interval.fields;
    var link = interval.config.link;
    var scheduleId = link.getAttribute('data-id');

    var data = {
        'conn_id': $(config.connIdSelector).val(),
        'id': scheduleId
    };

    for(var fieldIdx = 0; fieldIdx < fields.length; fieldIdx++) {
        var name = fields[fieldIdx];
        data[name] = interval.field(name).val();
    }

    var onSaved = function(saved) {

        link.textContent = saved.interval;

        for(var fieldIdx = 0; fieldIdx < fields.length; fieldIdx++) {
            var name = fields[fieldIdx];
            link.setAttribute('data-' + name, saved[name]);
        }

        $.fn.zato.data_table.row_updated(scheduleId);
    };

    $.fn.zato.inline_edit.post({
        link: link,
        url: $(config.editIntervalUrlSelector).val(),
        data: data,
        on_saved: onSaved
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.micro_forms.setup($.fn.zato.outgoing.file_transfer.schedules.interval, {
    descriptors: {'run_every': $.fn.zato.outgoing.file_transfer.interval.descriptor},
    showCancel: true,
    showHowItWorks: false,
    doneLabel: $.fn.zato.outgoing.file_transfer.schedules.config.saveLabel,
    onDone: $.fn.zato.outgoing.file_transfer.schedules.interval.save
});

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.file_transfer.schedules.delete_ = function(id, name) {

    var question = String.format('Are you sure you want to delete schedule `{0}`?', name);

    jConfirm(question, 'Please confirm', function(isConfirmed) {

        if(!isConfirmed) {
            return;
        }

        // Where the delete endpoint lives and which connection the schedule belongs to
        var deleteUrl = $('#file-transfer-schedules-delete-url').val();
        var connId = $($.fn.zato.outgoing.file_transfer.schedules.config.connIdSelector).val();

        var callback = function(data, status) {

            if(status === 'success') {
                var row = document.getElementById('tr_' + id);
                $(row).animate({opacity: 0}, 200, function() {
                    $(row).remove();
                });

                var message = String.format('Schedule `{0}` deleted', name);
                $.fn.zato.user_message(true, message);
            }
            else {
                $.fn.zato.user_message(false, data.responseText);
            }
        };

        $.fn.zato.post(deleteUrl, callback, {'conn_id': connId, 'id': id}, 'text');
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
