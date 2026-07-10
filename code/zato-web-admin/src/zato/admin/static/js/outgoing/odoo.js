
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
    var unique_constraints = [
        {field: 'name', entity_type: 'outgoing_odoo', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.odoo.field_descriptions = {
    'id_name': 'A unique name for this connection.<br>Services look it up by this name<br>through self.out.odoo.get.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot invoke Odoo<br>through an inactive connection.',
    'id_host': 'Host name or IP address the Odoo server<br>listens on, without any protocol prefix.',
    'id_port': 'Port the Odoo server listens on.<br>The standard Odoo port is 8069.',
    'id_user': 'Odoo login of the account the connection<br>authenticates as. Its password is set<br>separately with the Change password link.',
    'id_database': 'Name of the Odoo database to work with.<br>One server may host multiple databases<br>and each connection uses exactly one.',
    'id_protocol': 'How to talk to Odoo - XML-RPC or JSON-RPC,<br>each in plain or TLS form. The TLS variants<br>require the server to expose HTTPS.',
    'id_pool_size': 'How many connections are kept open in the pool.<br>More lets concurrent services call Odoo in parallel<br>at the cost of more open sessions.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.odoo.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing Odoo connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.odoo.field_descriptions
    });
}

$.fn.zato.outgoing.odoo.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing Odoo connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.odoo.field_descriptions
    });
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
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.odoo.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.odoo.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));
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
