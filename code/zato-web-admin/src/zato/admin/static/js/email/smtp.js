
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SMTP = new Class({
    toString: function() {
        var s = '<SMTP id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SMTP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.email.smtp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'host', 'port', 'timeout', 'mode', 'ping_address']);
    var unique_constraints = [
        {field: 'name', entity_type: 'email_smtp', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.email.smtp.field_descriptions = {
    'id_name': 'A unique name for this SMTP connection.<br>Used to identify it in services, logs and the dashboard.',
    'id_is_active': 'Whether this connection can send e-mail.<br>Services cannot send anything through<br>an inactive connection.',
    'id_host': 'Hostname of the SMTP server to connect to,<br>e.g. smtp.example.com.',
    'id_port': 'Port the SMTP server listens on.<br>Common values are 25 for plain connections,<br>465 for SSL/TLS and 587 for STARTTLS.',
    'id_timeout': 'How many seconds to wait for the server to respond<br>before a send attempt is abandoned.',
    'id_username': 'Username the connection authenticates with.<br>Leave empty if the server does not require credentials.<br>The password is set separately<br>with the Change password link.',
    'id_mode': 'How the connection is secured. Plain sends everything<br>unencrypted, SSL uses TLS from the start<br>and STARTTLS upgrades a plain connection to TLS.',
    'id_is_debug': 'When on, the full SMTP protocol conversation<br>is written out to server logs.<br>Useful when diagnosing delivery issues.',
    'id_ping_address': 'Recipient address that pings of this connection<br>send their test messages to.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.email.smtp.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new SMTP connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.email.smtp.field_descriptions
    });
}

$.fn.zato.email.smtp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the SMTP connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.email.smtp.field_descriptions
    });
}

$.fn.zato.email.smtp.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true
    var is_debug = item.is_debug == true
    var username = item.username ? item.username : "<span class='form_hint'>(None)</span>";

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? "Yes" : "No");
    row += String.format('<td>{0}</td>', item.host);
    row += String.format('<td>{0}</td>', item.port);
    row += String.format('<td>{0}</td>', username);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.email.smtp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.email.smtp.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.ping_address);
    row += String.format("<td class='ignore'>{0}</td>", is_debug);
    row += String.format("<td class='ignore'>{0}</td>", item.mode);
    row += String.format("<td class='ignore'>{0}</td>", item.username ? item.username : "");

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.email.smtp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'SMTP connection [{0}] deleted',
        'Are you sure you want to delete the SMTP connection [{0}]?',
        true);
}
