
// /////////////////////////////////////////////////////////////////////////////

// Defaults the page falls back to when a value is absent
$.fn.zato.outgoing.ftp.config = {
    noValueLabel: '(none)',
    emptyCellText: ''
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.FTP = new Class({
    toString: function() {
        var template = '<FTP id:{0} name:{1} is_active:{2}';
        var config = $.fn.zato.outgoing.ftp.config;

        var id = this.id;
        if(!id) {
            id = config.noValueLabel;
        }

        var name = this.name;
        if(!name) {
            name = config.noValueLabel;
        }

        var isActive = this.is_active;
        if(!isActive) {
            isActive = config.noValueLabel;
        }

        return String.format(template, id, name, isActive);
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $.fn.zato.time_ago.init_table('#data-table');
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.FTP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.ftp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'host', 'port', 'username']);
    // Generic connection names are unique per connection type
    var uniqueConstraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name',
            filter_name: 'type_', filter_value: 'outconn-ftp'}
    ];
    $.each(uniqueConstraints, function(constraintIndex, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ftp.field_descriptions = {
    'id_name': 'A unique name for this connection. Services look it up by this name through self.ftp[name], ' +
        'and the command shell and the schedules run against it.',
    'id_is_active': 'Whether this connection can be used. Services cannot look up an inactive connection ' +
        'and pings and the command shell are rejected.',
    'id_host': 'Host name or IP address of the FTP server, e.g. ftp.example.com. ' +
        'The port is set in the field next to it.',
    'id_port': 'Port the FTP server listens on. The default of 21 is the standard FTP control port.',
    'id_username': 'Username the connection logs in as. Files are read and written with this user\'s permissions.',
    'id_secret': 'Password for the username above. Stored encrypted in the Zato database.',
    'id_use_ssl': 'When on, the connection uses SSL, which for FTP is called FTPS - the login and ' +
        'the file transfers that follow are encrypted. When off, both travel in plain text. ' +
        'Zato does not validate the server certificate, so SSL protects the traffic here ' +
        'rather than confirming the identity of the server.',
    'id_verify_how': 'How a stored file is checked against what was sent - by its remote size, ' +
        'or by reading it back and comparing checksums.',
    'id_should_store_content': 'Whether the audit log additionally keeps the bytes of the files ' +
        'this connection moves, so they can be reread and downloaded later. Off by default.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ftp.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing FTP connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.ftp.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ftp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing FTP connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.ftp.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ftp.data_table.new_row = function(item, data, includeTr) {
    var row = '';
    var config = $.fn.zato.outgoing.ftp.config;

    if(includeTr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var isActive = item.is_active == true;

    var host = item.host;
    if(!host) {
        host = $.fn.zato.empty_value;
    }

    var port = item.port;
    if(!port) {
        port = $.fn.zato.empty_value;
    }

    var username = item.username;
    if(!username) {
        username = $.fn.zato.empty_value;
    }

    var usernameCell = item.username;
    if(!usernameCell) {
        usernameCell = config.emptyCellText;
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', isActive ? 'Yes' : 'No');
    row += String.format('<td class="zato-time-ago" data-time-ago-id="{0}" data-time-utc="{1}" data-duration-ms="{2}"></td>',
        data.last_run_job_ids, data.last_run_utc, data.last_duration_ms);
    row += String.format('<td>{0}</td>', host);

    // 2
    row += String.format('<td>{0}</td>', port);
    row += String.format('<td>{0}</td>', username);
    row += String.format('<td>{0}</td>',
        String.format('<a href="/zato/outgoing/file-transfer/schedules/ftp/{0}/cluster/{1}/{2}/?name={3}">{4}</a>',
        item.id, item.cluster_id, data.name_slug, item.name,
        $.fn.zato.count_text(data.scheduler_schedule_count, 'schedule', 'schedules')));
    row += String.format('<td class="action"><a href="{0}">Command shell</a></td>', data.command_shell_url);
    row += String.format('<td><a href="/zato/audit-log/?source=file-outgoing&object_name={0}&cluster={1}">Audit log</a></td>',
        encodeURIComponent(item.name), item.cluster_id);

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.ftp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.ftp.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.host);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.port);
    row += String.format("<td class='ignore'>{0}</td>", usernameCell);
    row += String.format("<td class='ignore'>{0}</td>", item.use_ssl == true);
    row += String.format("<td class='ignore'>{0}</td>", item.should_store_content == true);
    row += String.format("<td class='ignore'>{0}</td>", item.verify_how);

    if(includeTr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ftp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing FTP connection `{0}` deleted',
        'Are you sure you want to delete outgoing FTP connection `{0}`?',
        true);
}
