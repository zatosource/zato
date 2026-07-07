
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SMB = new Class({
    toString: function() {
        var s = '<SMB id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SMB;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.smb.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'host', 'port', 'username']);
    var uniqueConstraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(uniqueConstraints, function(constraintIdx, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.smb.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing SMB connection', null);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.smb.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing SMB connection', id);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.smb.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.host ? item.host : $.fn.zato.empty_value);

    // 2
    row += String.format('<td>{0}</td>', item.port ? item.port : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', item.username ? item.username : $.fn.zato.empty_value);

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.smb.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.smb.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.host);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.port);
    row += String.format("<td class='ignore'>{0}</td>", item.username ? item.username : '');

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.smb.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing SMB connection `{0}` deleted',
        'Are you sure you want to delete outgoing SMB connection `{0}`?',
        true);
}
