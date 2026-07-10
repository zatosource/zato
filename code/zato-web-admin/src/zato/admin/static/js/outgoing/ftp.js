
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.FTP = new Class({
    toString: function() {
        var s = '<FTP id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = true;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.FTP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.ftp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'host', 'port']);
    var unique_constraints = [
        {field: 'name', entity_type: 'outgoing_ftp', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ftp.field_descriptions = {
    'id_name': 'A unique name for this connection.<br>Services refer to it by this exact name.',
    'id_is_active': 'Whether this connection can be used.<br>Inactive connections cannot be used by services.',
    'id_dircache': 'When on, directory listings are cached<br>for faster repeated access. Turn off if other<br>systems change the directories often.',
    'id_host': 'Hostname or IP address of the FTP server,<br>e.g. ftp.example.com.',
    'id_port': 'TCP port the FTP server listens on.<br>The standard FTP port is 21.',
    'id_timeout': 'How many seconds to wait for the server<br>during network operations before giving up.',
    'id_user': 'Username to log in with.<br>Leave empty for anonymous FTP.<br>The password is set separately<br>with the Change password link.',
    'id_acct': 'Account information sent with the FTP ACCT<br>command. Most servers do not use it,<br>leave empty unless yours requires it.',
    'id_default_directory': 'Directory to change to right after logging in.<br>Relative paths are then resolved against it.',
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

$.fn.zato.outgoing.ftp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing FTP connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.ftp.field_descriptions
    });
}

$.fn.zato.outgoing.ftp.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var dircache = item.dircache == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.host);

    // 2
    row += String.format('<td>{0}</td>', item.user || '<span class="form_hint">---</span>');
    row += String.format('<td>{0}</td>', item.acct || '<span class="form_hint">---</span>');
    row += String.format('<td>{0}</td>', item.timeout || '<span class="form_hint">---</span>');

    // 3
    row += String.format('<td>{0}</td>', item.port);
    row += String.format('<td>{0}</td>', item.default_directory || '<span class="form_hint">---</span>');
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>", item.id));

    // 4
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.ftp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.ftp.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.dircache);
    row += String.format("<td class='ignore'>{0}</td>", item.default_directory);

    // 6
    row += String.format("<td class='ignore'>{0}</td>", item.user || '');
    row += String.format("<td class='ignore'>{0}</td>", item.acct || '');
    row += String.format("<td class='ignore'>{0}</td>", item.timeout || '');

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.ftp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing FTP connection `{0}` deleted',
        'Are you sure you want to delete outgoing FTP connection `{0}`?',
        true);
}
