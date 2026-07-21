
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.MicrosoftFabricOutconn = new Class({
    toString: function() {
        var s = '<MicrosoftFabricOutconn id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.MicrosoftFabricOutconn;
    $.fn.zato.data_table.new_row_func = $.fn.zato.cloud.microsoft_fabric.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'address',
        'tenant_id',
        'client_id',
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

$.fn.zato.cloud.microsoft_fabric.field_descriptions = {
    'id_name': 'A unique name for this Microsoft Fabric connection.<br>Used to identify it in services, logs and the dashboard.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',
    'id_address': 'Address of the Fabric REST API,<br>e.g. https://api.fabric.microsoft.com/v1.<br>Change it only when using a non-default cloud.',
    'id_tenant_id': 'Directory (tenant) ID of the Microsoft Entra tenant<br>the connection signs in to. Found on the overview page<br>of the app registration in the Azure portal.',
    'id_client_id': 'Application (client) ID of the Azure app registration<br>the connection authenticates as. The app needs<br>permissions to call the Fabric API.',
    'id_client_secret': 'Value of a client secret created for the app registration.<br>Note that secrets expire in Azure<br>and need to be rotated periodically.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.microsoft_fabric.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new Microsoft Fabric connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.cloud.microsoft_fabric.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.microsoft_fabric.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the Microsoft Fabric connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.cloud.microsoft_fabric.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.microsoft_fabric.data_table.new_row = function(item, data, include_tr) {
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
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cloud.microsoft_fabric.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cloud.microsoft_fabric.delete_('{0}');\">Delete</a>", item.id));

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));
    row += String.format("<td class='ignore'>{0}</td>", item.address);

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.microsoft_fabric.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Microsoft Fabric connection `{0}` deleted',
        'Are you sure you want to delete Microsoft Fabric connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
