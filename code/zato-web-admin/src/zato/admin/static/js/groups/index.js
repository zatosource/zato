
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Group = new Class({
    toString: function() {
        var s = '<Group id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Group;
    $.fn.zato.data_table.new_row_func = $.fn.zato.groups.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
    ]);
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new group', null);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update an existing group', id);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', $("#group_member_count_"+item.id).text() || 0);
    row += String.format('<td>{0}</td>', String.format("<a href='/zato/groups/members/{0}/{1}/?cluster=1'>Go to members</a>", item.group_type, item.id));

    if(false) {
        row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.groups.clone('{0}')\">Clone</a>", item.id));
    }
    else {
        row += String.format('<td></td>');
    }
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.groups.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.groups.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    // 3
    row += String.format("<td class='ignore'>{0}</td>", item.group_type);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.generic_object_id);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Deleted group `{0}`',
        'Are you sure you want to delete group `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
