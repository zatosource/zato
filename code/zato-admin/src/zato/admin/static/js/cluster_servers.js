
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Server = new Class({
    toString: function() {
        var s = '<Server id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Server;
    $.fn.zato.data_table.new_row_func = $.fn.zato.cluster.servers.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'old_name']);
})

$.fn.zato.cluster.servers.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the server', id);
}

$.fn.zato.cluster.servers.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Server [{0}] deleted',
        'Are you sure you want to delete the server [{0}]?',
        true);
}

$.fn.zato.cluster.servers.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }
    
    /*
    var is_active = $.fn.zato.like_bool(item.is_active) == true;
    var is_internal = $.fn.zato.like_bool(data.is_internal) == true;
    
    var cluster_id = $(document).getUrlParam('cluster');
    
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', $.fn.zato.data_table.Server_text(data.name, cluster_id));
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', data.impl_name);
    row += String.format('<td>{0}</td>', is_internal ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', data.usage_count);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cluster.servers.edit('{0}')\">Edit</a>", data.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.cluster.servers.delete_({0});'>Delete</a>", data.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", is_internal);
    */

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}