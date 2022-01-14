
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.JSONRPC = new Class({
    toString: function() {
        var s = '<JSONRPC id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.JSONRPC;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.json_rpc.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'url_path', 'security_id', 'service_whitelist']);
})

$.fn.zato.channel.json_rpc.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new JSON-RPC channel', null);
}

$.fn.zato.channel.json_rpc.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the JSON-RPC channel', id);
}

$.fn.zato.channel.json_rpc.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true
    var is_rate_limit_active = $.fn.zato.like_bool(data.is_rate_limit_active) == true;
    var rate_limit_check_parent_def = $.fn.zato.like_bool(data.rate_limit_check_parent_def) == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.url_path);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.json_rpc.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.channel.json_rpc.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.security_id);
    row += String.format("<td class='ignore'>{0}</td>", item.service_whitelist);

    row += String.format("<td class='ignore'>{0}</td>", is_rate_limit_active);
    row += String.format("<td class='ignore'>{0}</td>", data.rate_limit_type);
    row += String.format("<td class='ignore'>{0}</td>", data.rate_limit_def);
    row += String.format("<td class='ignore'>{0}</td>", rate_limit_check_parent_def);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.channel.json_rpc.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'JSON-RPC channel `{0}` deleted',
        'Are you sure you want to delete JSON-RPC channel `{0}`?',
        true);
}
