
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
    $('#data-table').tablesorter();
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

$.fn.zato.outgoing.ftp.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing FTP connection', null);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ftp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing FTP connection', id);
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
    row += String.format('<td>{0}</td>', host);

    // 2
    row += String.format('<td>{0}</td>', port);
    row += String.format('<td>{0}</td>', username);
    row += String.format('<td>{0}</td>',
        String.format('<a href="/zato/outgoing/ftp/command-shell/{0}/cluster/{1}/{2}/?name={3}">Command shell</a>',
        item.id, item.cluster_id, data.name_slug, encodeURIComponent(item.name)));
    row += String.format('<td>{0}</td>',
        String.format('<a href="/zato/outgoing/file-transfer/schedules/ftp/{0}/cluster/{1}/{2}/?name={3}">Schedules</a>',
        item.id, item.cluster_id, data.name_slug, item.name));
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
