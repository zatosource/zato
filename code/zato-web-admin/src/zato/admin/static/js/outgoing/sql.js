
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SQL = new Class({
    toString: function() {
        var s = '<SQL id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = true;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SQL;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.sql.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'username', 'db_name', 'engine', 'host', 'port', 'pool_size']);
    var unique_constraints = [
        {field: 'name', entity_type: 'outgoing_sql', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sql.field_descriptions = {
    'id_name': 'A unique name for this connection.<br>Services look it up by this name<br>through self.out.sql.get.',
    'id_is_active': 'Whether this connection pool can be used.<br>Services cannot run queries<br>through an inactive connection.',
    'id_engine': 'The database type - it selects the driver<br>and SQL dialect, and picking one fills in<br>the default port and database name below.',
    'id_host': 'Host name or IP address the database server<br>listens on, with the port in the field next to it.',
    'id_db_name': 'Name of the database to connect to,<br>with the database user in the field next to it.<br>The user\'s password is set with the Change password link.',
    'id_extra': 'Extra engine options as key=value pairs,<br>one per line, e.g. echo=True or pool_pre_ping=True.<br>They are passed to the underlying SQLAlchemy engine.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sql.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing SQL connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.sql.field_descriptions
    });
}

$.fn.zato.outgoing.sql.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing SQL connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.sql.field_descriptions
    });
}

$.fn.zato.outgoing.sql.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', data.engine_display_name);
    row += String.format('<td>{0}</td>', item.host);
    row += String.format('<td>{0}</td>', item.port);
    row += String.format('<td>{0}</td>', item.db_name);
    row += String.format('<td>{0}</td>', item.username);
    row += String.format('<td>{0}</td>', item.pool_size);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.sql.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.sql.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.engine);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.sql.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing SQL connection [{0}] deleted',
        'Are you sure you want to delete the outgoing SQL connection [{0}]?',
        true);
}
