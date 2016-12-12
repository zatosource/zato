
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Cluster = new Class({
    toString: function() {
        var s = '<Cluster id:{0} name:{1} odb_type:{2}>';
        return String.format(s, this.id ? this.id : '(none)', 
                                this.name ? this.name : '(none)',
                                this.odb_type ? this.odb_type : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() { 
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Cluster;
    $.fn.zato.data_table.new_row_func = $.fn.zato.cluster.data_table.new_row;
    $.fn.zato.data_table.parse();
    var attrs = ['name', 'odb_host', 'odb_port', 'odb_db_name', 'odb_user',
        'lb_host', 'lb_agent_port', 'broker_host', 'broker_start_port', 'broker_token'];
    $.fn.zato.data_table.setup_forms(attrs);
})

$.fn.zato.cluster.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new cluster', null);
}

$.fn.zato.cluster.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', "Update the cluster's definition", id);
}


$.fn.zato.cluster.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated attention'>", item.id);
    }

    var name_desc = item.name;
    if(item.description) {
        name_desc += '<br/><pre>' + item.description + '</pre>';
    }
    if(!data.has_lb_config) {
        name_desc += "<br/><br/>Could not fetch the load balancer's configuration";
    }

    var manage_lb = '';
    var servers = '';

    if(data.has_lb_config) {
        manage_lb = String.format("<a href='/zato/load-balancer/manage/cluster/{0}/'>Load balancer</a>", data.id);
        servers = String.format("<a href='javascript:$.fn.zato.cluster.add_remove_servers({0})'>Add/remove servers</a>", item.id);
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', name_desc);
    row += String.format('<td>{0}</td>', data.addresses);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.cluster.edit({0})'>Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.cluster.delete_({0});'>Delete</a>", item.id));
    row += String.format('<td>{0}</td>', manage_lb);
    row += String.format('<td>{0}</td>', servers);
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", '');

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.cluster.delete_ = function(id) {
    var confirm_pattern = 'Are you sure you want to <b>delete</b> the cluster <b>[{0}]</b>?';
    confirm_pattern += '<br/><br/>This is <b>an irreversible action</b>, the whole cluster';
    confirm_pattern += ', including any configuration associated with it will be deleted.';
    confirm_pattern += '<br/><br/>Please type {1} (all uppercase) to proceed.';

    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Cluster [{0}] deleted',  confirm_pattern, false, 'GO AHEAD');
}
