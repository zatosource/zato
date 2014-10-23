
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Odoo = new Class({
    toString: function() {
        var s = '<Odoo id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = true;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Odoo;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.odoo.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'host', 'port', 'user', 'database', 'protocol', 'pool_size']);
})

$.fn.zato.outgoing.odoo.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing Odoo connection', null);
}

$.fn.zato.outgoing.odoo.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing Odoo connection', id);
}

$.fn.zato.outgoing.odoo.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;

    var protocol_to_name = {
        'xmlrpc': 'XML-RPC',
        'xmlrpcs': 'XML-RPCS',
        'jsonrpc': 'JSON-RPC',
        'jsonrpcs': 'JSON-RPCS',
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.host);
    row += String.format('<td>{0}</td>', item.port);
    row += String.format('<td>{0}</td>', item.user);
    row += String.format('<td>{0}</td>', item.database);
    row += String.format('<td>{0}</td>', protocol_to_name[item.protocol]);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.change_password({0})'>Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.odoo.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.outgoing.odoo.delete_({0});'>Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.ping('{0}')\">Ping</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.pool_size);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.odoo.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Odoo connection [{0}] deleted',
        'Are you sure you want to delete the outgoing Odoo connection [{0}]?',
        true);
}
