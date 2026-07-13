
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.OData = new Class({
    toString: function() {
        var s = '<OData id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.OData;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.odata.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'odata_version', 'auth_type']);
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.odata.field_descriptions = {
    'id_name': 'A unique name for this connection.<br>Services look it up by this name<br>to invoke the ' +
        $.fn.zato.outgoing.odata.config.label + ' API.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',
    'id_odata_version': 'OData protocol version the remote API speaks,<br>4.0 or 2.0. SAP systems commonly use 2.0.',
    'id_pool_size': 'How many client connections the pool keeps<br>for concurrent requests to this API.<br>Default is 1.',
    'id_address': 'Service root URL of the OData API,<br>e.g. https://host/sap/opu/odata/sap/API_BUSINESS_PARTNER.<br>All entity sets are addressed relative to it.',
    'id_auth_type': 'How requests authenticate - Basic with username<br>and secret, Bearer with a static token,<br>OAuth2 with tokens obtained dynamically,<br>or no authentication at all.',
    'id_needs_csrf_token': 'When on, a CSRF token is fetched first<br>and sent with each modifying request.<br>Required by SAP OData services.',
    'id_timeout': 'How many seconds to wait for a response<br>to each request. Default is 60.',
    'id_page_size': 'How many entities to request per page<br>when reading results. 0 means the server\'s<br>own default page size is used.',
    'id_username': 'Username for Basic authentication.<br>Leave empty with OAuth2 - the secret is set<br>separately with the Change secret link.',
    'id_token_url': 'OAuth2 token endpoint the connection obtains<br>access tokens from, e.g.<br>https://login.microsoftonline.com/tenant/oauth2/v2.0/token.',
    'id_tenant_id': 'Directory or tenant the OAuth2 client belongs to,<br>e.g. an Entra ID tenant with Microsoft APIs.',
    'id_client_id': 'OAuth2 client ID registered with the<br>authorization server. Its secret is set<br>with the Change secret link.',
    'id_scopes': 'OAuth2 scopes requested with each token,<br>one per line, e.g.<br>https://environment.dynamics.com/.default.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.odata.create = function() {
    var label = $.fn.zato.outgoing.odata.config.label;
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing ' + label + ' connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.odata.field_descriptions
    });
}

$.fn.zato.outgoing.odata.edit = function(id) {
    var label = $.fn.zato.outgoing.odata.config.label;
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing ' + label + ' connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.odata.field_descriptions
    });
}

$.fn.zato.outgoing.odata.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var needs_csrf_token = item.needs_csrf_token == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address);
    row += String.format('<td>{0}</td>', item.odata_version);
    row += String.format('<td>{0}</td>', item.auth_type);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change secret</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.odata.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.odata.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    // 1 -->
    row += String.format("<td class='ignore'>{0}</td>", item.username);
    row += String.format("<td class='ignore'>{0}</td>", item.token_url);
    row += String.format("<td class='ignore'>{0}</td>", item.tenant_id);
    row += String.format("<td class='ignore'>{0}</td>", item.client_id);

    // 2 -->
    row += String.format("<td class='ignore'>{0}</td>", item.scopes);
    row += String.format("<td class='ignore'>{0}</td>", needs_csrf_token);
    row += String.format("<td class='ignore'>{0}</td>", item.page_size);

    // 3 -->
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.pool_size);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.odata.delete_ = function(id) {
    var label = $.fn.zato.outgoing.odata.config.label;
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing ' + label + ' connection `{0}` deleted',
        'Are you sure you want to delete outgoing ' + label + ' connection `{0}`?',
        true);
}
