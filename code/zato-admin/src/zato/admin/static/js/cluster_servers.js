
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
    $.fn.zato.data_table.setup_forms(['name', 'old_name', 'lb_state', 'lb_address', 'in_lb']);
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
    
    var in_lb = $.fn.zato.like_bool(data.in_lb) == true;
    var in_lb_link = '';
    
    if(in_lb) {
        in_lb_link += String.format("<a href=\"javascript:$.fn.zato.cluster.servers.remove_from_lb('{0}')\">Remove from LB</a>", data.id);
    }
    else {
        in_lb_link += String.format("<a href=\"javascript:$.fn.zato.cluster.servers.add_to_lb('{0}')\">Add to LB</a>", data.id);
    }
    
    row += "<td class='numbering'>&nbsp;</td>";
    row += String.format('<td>{0}</td>', data.name);
    row += String.format('<td>{0}</td>', data.host);
    row += String.format('<td>{0}</td>', data.up_status);
    row += String.format('<td>{0}</td>', data.up_mod_date);
    row += String.format('<td>{0}</td>', data.lb_state);
    row += String.format('<td>{0}</td>', data.lb_address);
    
    row += String.format('<td>{0}</td>', in_lb_link);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cluster.servers.edit('{0}')\">Edit</a>", data.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cluster.servers.delete_('{0}')\">Delete</a>", data.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.id);
    row += String.format("<td class='ignore'>{0}</td>", data.name);
    row += String.format("<td class='ignore'>{0}</td>", data.in_lb);

    if(include_tr) {
        row += '</tr>';
    }
    
    $.fn.zato.data_table.data[data.id].old_name = data.name;

    return row;
}