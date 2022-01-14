
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
        row += String.format("<tr id='tr_{0}' class='updated'>", data.id);
    }
    
    var in_lb = $.fn.zato.like_bool(data.in_lb) == true;
    var in_lb_link = '';
    var action = '';
    var action_text = '';
    
    if(in_lb) {
        action = 'remove';
        action_text = 'Remove from LB';
    }
    else {
        action = 'add';
        action_text = 'Add to LB';
    }
    
    in_lb_link += String.format("<a href=\"javascript:$.fn.zato.cluster.servers.add_remove_lb('{0}', '{1}', '{2}')\">{3}</a>", 
        action, data.id, data.cluster_id, action_text);
    
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

$.fn.zato.cluster.servers.add_remove_lb = function(action, id, cluster_id) {

    var _callback = function(data, status) {
        var json = $.parseJSON(data.responseText);
        $.fn.zato.data_table.on_submit_complete(data, status, 'edit');
        $.fn.zato.data_table.data[json.id].name = json.name;
    }
    $.fn.zato.post(String.format('./load-balancer/{0}/{1}/', action, id), _callback, {'cluster_id':cluster_id});
}
