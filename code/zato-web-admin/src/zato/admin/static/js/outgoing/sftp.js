
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SFTP = new Class({
    toString: function() {
        var s = '<SFTP id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SFTP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.sftp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'username']);
    // Generic connection names are unique per connection type,
    // so the check is scoped to this page's own type.
    var uniqueConstraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name',
            filter_name: 'type_', filter_value: 'outconn-sftp'}
    ];
    $.each(uniqueConstraints, function(constraintIndex, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sftp.field_descriptions = {
    'id_name': 'A unique name for this connection.<br>Services look it up by this name<br>and the command shell runs against it.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection<br>and pings and the command shell are rejected.',
    'id_address': 'Where the SFTP server listens, as host<br>or host:port, e.g. sftp.example.com:22.',
    'id_username': 'Username to log in to the SFTP server as.<br>Leave empty if the server takes the identity<br>from the private key alone.',
    'id_secret': 'Password for the username above.<br>Leave empty when logging in<br>with a private key instead.',
    'id_private_key': 'Name of an environment variable that holds<br>the path to the private key file,<br>e.g. Zato_SFTP_Key. Used instead of a password.',
    'id_strict_host_key_checking': 'When on, the server\'s host key must already be<br>in known_hosts or the connection is rejected.<br>Turning it off accepts any host key.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sftp.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing SFTP connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.sftp.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sftp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing SFTP connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.sftp.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sftp.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var strict_host_key_checking = item.strict_host_key_checking == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address ? item.address : $.fn.zato.empty_value);

    // 2
    row += String.format('<td>{0}</td>', item.username ? item.username : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"./command-shell/{0}/cluster/{1}/{2}/?name={3}\">Command shell</a>",
        item.id, item.cluster_id, data.name_slug, item.name));
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"/zato/outgoing/file-transfer/schedules/sftp/{0}/cluster/{1}/{2}/?name={3}\">Schedules</a>",
        item.id, item.cluster_id, data.name_slug, item.name));

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.sftp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.sftp.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.address);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.username ? item.username : '');
    row += String.format("<td class='ignore'>{0}</td>", item.private_key ? item.private_key : '');
    row += String.format("<td class='ignore'>{0}</td>", strict_host_key_checking ? 'True' : 'False');

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sftp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing SFTP connection `{0}` deleted',
        'Are you sure you want to delete outgoing SFTP connection `{0}`?',
        true);
}
