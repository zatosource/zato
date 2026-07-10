
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SalesforceOutconn = new Class({
    toString: function() {
        var s = '<SalesforceOutconn id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SalesforceOutconn;
    $.fn.zato.data_table.new_row_func = $.fn.zato.cloud.salesforce.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'api_version',
        'address',
        'username',
        'password',
        'consumer_key',
        'consumer_secret',
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

$.fn.zato.cloud.salesforce.field_descriptions = {
    'id_name': 'A unique name for this Salesforce connection.<br>Used to identify it in services, logs and the dashboard.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',
    'id_api_version': 'Version of the Salesforce REST API to invoke,<br>e.g. 54.0. It decides which objects and fields<br>are available to the connection.',
    'id_address': 'Address of the Salesforce instance,<br>e.g. https://example.my.salesforce.com.<br>All API calls the connection makes go to this host.',
    'id_username': 'Username the connection logs in as.<br>Records are read and written<br>with this user\'s permissions.',
    'id_password': 'Password of the user above. Used together with<br>the consumer key and secret to obtain<br>OAuth2 access tokens from Salesforce.',
    'id_consumer_key': 'Consumer key of the connected app created<br>in Salesforce for Zato. Found under the app\'s<br>Manage Consumer Details in Salesforce setup.',
    'id_consumer_secret': 'Consumer secret of the same connected app.<br>Keep it confidential, it works like a password.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.salesforce.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new Salesforce connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.cloud.salesforce.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.salesforce.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the Salesforce connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.cloud.salesforce.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.salesforce.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;
    let cluster_id = $(document).getUrlParam('cluster');

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address);

    // 2
    row += String.format("<td>{0}</td>", item.username);
    row += String.format('<!--<td><a href="/zato/cloud/salesforce/invoke/{0}/{1}/{2}/?cluster={3}">Invoke</a></td>-->',
        item.id, item.name, $.fn.zato.slugify(item.name), cluster_id);

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cloud.salesforce.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cloud.salesforce.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    // 4
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.username);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.salesforce.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Salesforce connection `{0}` deleted',
        'Are you sure you want to delete Salesforce connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
