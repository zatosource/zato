
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.IMAP = new Class({
    toString: function() {
        var s = '<IMAP id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.IMAP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.email.imap.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'server_type']);
    var unique_constraints = [
        {field: 'name', entity_type: 'email_imap', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });

    // Attach date-time pickers to the scheduler start date fields in both popups
    var picker_ids = ['#id_scheduler_start_date', '#id_edit-scheduler_start_date'];
    $.each(picker_ids, function(ignored, picker_id) {
        $(picker_id).datetimepicker(
            {
                'dateFormat':$('#js_date_format').val(),
                'timeFormat':$('#js_time_format').val(),
                'ampm':$.fn.zato.to_bool($('#js_ampm').val()),
            }
        );
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.email.imap.field_descriptions = {
    'id_name': 'A unique name for this IMAP connection.<br>Used to identify it in services, logs and the dashboard.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',
    'id_server_type': 'What kind of server this is - generic IMAP<br>for any standard server or Microsoft 365<br>for cloud mailboxes accessed with OAuth2.',
    'id_username': 'User or e-mail address the connection logs in as,<br>e.g. mailbox@example.com.<br>The password or secret is set separately<br>with the link in the connection\'s row.',
    'id_host': 'Hostname of the IMAP server to connect to,<br>e.g. imap.example.com.<br>Used with generic IMAP servers only.',
    'id_port': 'Port the IMAP server listens on.<br>Default is 993, the standard port<br>for IMAP over SSL.',
    'id_mode': 'Whether the connection is encrypted with SSL<br>or sent in plaintext. Use plain only<br>with servers on trusted networks.',
    'id_timeout': 'How many seconds to wait for the server<br>when connecting and reading. Default is 10.',
    'id_debug_level': 'Verbosity of the underlying IMAP library,<br>from 0 (quiet) to 2 (detailed traffic logs).<br>Default is 0.',
    'id_get_criteria': 'IMAP search criteria selecting which messages<br>to download, e.g. UNSEEN or ALL.<br>Used with generic IMAP servers only.',
    'id_tenant_id': 'Directory (tenant) ID of the Microsoft Entra tenant<br>the mailbox belongs to.<br>Used with Microsoft 365 mailboxes only.',
    'id_client_id': 'Application (client) ID of the Azure app registration<br>the connection authenticates as.<br>Used with Microsoft 365 mailboxes only.',
    'id_filter_criteria': 'OData filter selecting which messages to download,<br>e.g. isRead ne true.<br>Used with Microsoft 365 mailboxes only.',
    'id_scheduler_run_every': 'How often the mailbox is polled for new messages.<br>Leave empty if services read the mailbox on their own<br>and no automatic polling is needed.',
    'id_scheduler_start_date': 'When the first polling run takes place.<br>Subsequent runs follow the interval above.',
    'id_scheduler_service': 'Service invoked for messages found during polling.<br>It receives each message\'s subject, body<br>and attachments on input.',
    'id_scheduler_invoke_with': 'Whether the service is invoked once per whole message<br>or once for each of a message\'s attachments.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.email.imap.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new IMAP connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.email.imap.field_descriptions
    });
}

$.fn.zato.email.imap.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the IMAP connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.email.imap.field_descriptions
    });
}

$.fn.zato.email.imap.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true
    var username = item.username ? item.username : "<span class='form_hint'>(None)</span>";

    if(item.server_type == "microsoft-365") {
        var _host = item.tenant_id || $.fn.zato.empty_value;
        var _port = $.fn.zato.empty_value;
        var _server_type_human = "Microsoft 365";
        var _change_secret_link = String.format(
            "<a href=\"javascript:$.fn.zato.data_table.change_password('{0}', 'Change secret', 'Secret', 'secret')\">Change secret</a>",
            item.id
        );
    }
    else {
        var _host = item.host || $.fn.zato.empty_value;
        var _port = item.port || $.fn.zato.empty_value;
        var _server_type_human = "Generic IMAP";
        var _change_secret_link = String.format(
            "<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>",
            item.id
        );
    }

    // 1
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);

    // 2
    row += String.format('<td>{0}</td>', is_active ? "Yes" : "No");
    row += String.format('<td>{0}</td>', _server_type_human);
    row += String.format("<td>{0}</td>", _host);

    // 3
    row += String.format('<td>{0}</td>', _port);
    row += String.format('<td>{0}</td>', username);
    row += String.format('<td>{0}</td>', _change_secret_link);

    // 4
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.email.imap.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.email.imap.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));

    // Audit log link
    row += String.format('<td><a href="/zato/audit-log/?source=email-imap&object_name={0}&cluster=1">Audit log</a></td>', encodeURIComponent(item.name));

    // 5
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);

    // 6
    row += String.format("<td class='ignore'>{0}</td>", item.debug_level);
    row += String.format("<td class='ignore'>{0}</td>", item.mode);
    row += String.format("<td class='ignore'>{0}</td>", item.get_criteria ? item.get_criteria : "");

    // 7
    row += String.format("<td class='ignore'>{0}</td>", item.username ? item.username : "");
    row += String.format("<td class='ignore'>{0}</td>", item.server_type);
    row += String.format("<td class='ignore'>{0}</td>", item.tenant_id ? item.tenant_id : "");

    // 8
    row += String.format("<td class='ignore'>{0}</td>", item.client_id ? item.client_id : "");
    row += String.format("<td class='ignore'>{0}</td>", item.host ? item.host : "");
    row += String.format("<td class='ignore'>{0}</td>", item.port ? item.port : "993");

    // 9
    row += String.format("<td class='ignore'>{0}</td>", item.filter_criteria ? item.filter_criteria : "");
    row += String.format("<td class='ignore'>{0}</td>", item.scheduler_run_every ? item.scheduler_run_every : "");
    row += String.format("<td class='ignore'>{0}</td>", item.scheduler_run_unit ? item.scheduler_run_unit : "");

    // 10
    row += String.format("<td class='ignore'>{0}</td>", item.scheduler_start_date ? item.scheduler_start_date : "");
    row += String.format("<td class='ignore'>{0}</td>", item.scheduler_service ? item.scheduler_service : "");
    row += String.format("<td class='ignore'>{0}</td>", item.scheduler_invoke_with ? item.scheduler_invoke_with : "");

    // 11
    row += String.format("<td class='ignore'>{0}</td>", item.scheduler_job_id ? item.scheduler_job_id : "");

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.email.imap.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Deleted IMAP connection `{0}`',
        'Are you sure you want to delete the IMAP connection `{0}`?',
        true);
}
