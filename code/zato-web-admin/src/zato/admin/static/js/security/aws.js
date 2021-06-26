
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.AWS = new Class({
    toString: function() {
        var s = '<AWS id:{0} name:{1} username:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.username ? this.username : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.AWS;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.aws.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'username']);
})


$.fn.zato.security.aws.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new AWS security definition', null);
}

$.fn.zato.security.aws.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the AWS security definition', id);
}

$.fn.zato.security.aws.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', item.username);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.change_password({0})'>Change access key</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.aws.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.aws.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.security.aws.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'AWS definition `{0}` deleted',
        'Are you sure you want to delete the AWS definition `{0}`?',
        true);
}
