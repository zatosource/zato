
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Elasticsearch = new Class({
    toString: function() {
        var s = '<Elasticsearch id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Elasticsearch;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.es.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address_list', 'timeout']);
    var uniqueConstraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(uniqueConstraints, function(constraintIdx, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.es.field_descriptions = {
    'id_name': 'A unique name for this connection.<br>Services refer to it by this exact name.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',
    'id_address_list': 'ElasticSearch servers as full URLs, one per line,<br>e.g. https://localhost:9200. The scheme decides<br>whether TLS is used for each server.',
    'id_username': 'Username to authenticate with.<br>Leave empty if the server<br>does not require authentication.',
    'id_secret': 'Password matching the username above.<br>Stored encrypted in the Zato database.',
    'id_timeout': 'How many seconds to wait for a response<br>to a single request before giving up. Default is 90.',
    'id_is_tls_validation_enabled': 'When on, the server\'s certificate is verified<br>against the CA certs file below.<br>Turn it off only with test environments.',
    'id_tls_ca_certs_file': 'Path to a PEM file with CA certificates<br>used to verify the server\'s certificate.',
    'id_tls_cert_key_file': 'Path to a PEM file with the client certificate<br>and its private key combined, for mutual TLS.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.es.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing ElasticSearch connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.es.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.es.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing ElasticSearch connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.es.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.es.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var isActive = item.is_active == true;

    // The visible cell shows each address on its own line
    var addressListDisplay = item.address_list.replace(/\n/g, '<br/>');

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', isActive ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', addressListDisplay);

    // 2
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.es.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.es.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));

    // 3
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.address_list);

    // 4
    row += String.format("<td class='ignore'>{0}</td>", item.username ? item.username : '');
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.is_tls_validation_enabled);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_ca_certs_file ? item.tls_ca_certs_file : '');
    row += String.format("<td class='ignore'>{0}</td>", item.tls_cert_key_file ? item.tls_cert_key_file : '');

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.es.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing ElasticSearch connection `{0}` deleted',
        'Are you sure you want to delete outgoing ElasticSearch connection `{0}`?',
        true);
}
