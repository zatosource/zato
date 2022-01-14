
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SQLNotification = new Class({
    toString: function() {
        var s = '<SQLNotification id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SQLNotification;
    $.fn.zato.data_table.new_row_func = $.fn.zato.notif.sql.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['id', 'name', 'def_id', 'interval', 'query', 'service_name']);
})


$.fn.zato.notif.sql.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? "Yes":"No");
    row += String.format('<td>{0}</td>', item.interval);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.notif.sql.edit({0});'>Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.notif.sql.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.query);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.notif.sql.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new SQL notification', null);
}

$.fn.zato.notif.sql.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update an SQL notification', id);
}

$.fn.zato.notif.sql.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'SQL notification [{0}] deleted',
        'Are you sure you want to delete the SQL notification [{0}]?',
        true);
}
