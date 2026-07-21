
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Microsoft365Outconn = new Class({
    toString: function() {
        var s = '<Microsoft365Outconn id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Microsoft365Outconn;
    $.fn.zato.data_table.new_row_func = $.fn.zato.cloud.microsoft_365.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'tenant_id',
        'client_id',
        'scopes',
    ]);

    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.microsoft_365.field_descriptions = {
    'id_name': 'A unique name for this Microsoft 365 connection.<br>Used to identify it in services, logs and the dashboard.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',
    'id_tenant_id': 'Directory (tenant) ID of the Microsoft Entra tenant<br>the connection signs in to. Found on the overview page<br>of the app registration in the Azure portal.',
    'id_client_id': 'Application (client) ID of the Azure app registration<br>the connection authenticates as. The app\'s API permissions<br>decide what the connection can access.',
    'id_secret_value': 'Value of a client secret created for the app registration.<br>Note that secrets expire in Azure<br>and need to be rotated periodically.',
    'id_scopes': 'OAuth2 scopes the connection requests, one per line.<br>The default https://graph.microsoft.com/.default<br>grants all permissions assigned to the app in Azure.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.microsoft_365.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new Microsoft 365 connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.cloud.microsoft_365.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.microsoft_365.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the Microsoft 365 connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.cloud.microsoft_365.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.microsoft_365.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.tenant_id);
    row += String.format('<td>{0}</td>', item.client_id);

    // 2
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}', 'Change secret')\">Change secret</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cloud.microsoft_365.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cloud.microsoft_365.delete_('{0}');\">Delete</a>", item.id));

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));
    row += String.format("<td class='ignore'>{0}</td>", item.scopes);

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.microsoft_365.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Microsoft 365 connection `{0}` deleted',
        'Are you sure you want to delete Microsoft 365 connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
