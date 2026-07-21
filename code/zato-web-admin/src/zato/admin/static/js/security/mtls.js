
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.MTLS = new Class({
    toString: function() {
        var s = '<MTLS id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.MTLS;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.mtls.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name']);
    var unique_constraints = [
        {field: 'name', entity_type: 'security', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(index, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.mtls.field_descriptions = {
    'id_name': 'A unique name for this definition.<br>Used to identify it in channels, outgoing connections,<br>logs and the dashboard.',
    'id_cert_path': 'Path to a PEM file on the server<br>with the client certificate that outgoing<br>connections present during the TLS handshake.',
    'id_key_path': 'Path to a PEM file on the server<br>with the private key matching the certificate.<br>Leave empty if the certificate file<br>contains the key too.',
    'id_ca_certs_path': 'Path to a PEM file on the server<br>with the CA certificates that the remote<br>server\'s certificate must chain up to.<br>Leave empty to use the system trust store.',
    'id_client_cert_fingerprint': 'For channels - the SHA256 fingerprint<br>of the client certificate that is allowed<br>to invoke channels using this definition.',
    'id_client_cert_subject_dn': 'For channels - the subject DN<br>of the client certificate that is allowed<br>to invoke channels using this definition.<br>The fingerprint takes precedence if both are given.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.mtls.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create an mTLS definition', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.security.mtls.field_descriptions
    });
}

$.fn.zato.security.mtls.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Edit mTLS definition', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.security.mtls.field_descriptions
    });
}

$.fn.zato.security.mtls.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', item.cert_path ? item.cert_path : '');
    row += String.format('<td>{0}</td>', item.client_cert_fingerprint ? item.client_cert_fingerprint : '');
    row += String.format('<td>{0}</td>', item.client_cert_subject_dn ? item.client_cert_subject_dn : '');
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.mtls.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.mtls.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.key_path ? item.key_path : '');
    row += String.format("<td class='ignore'>{0}</td>", item.ca_certs_path ? item.ca_certs_path : '');

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.security.mtls.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'mTLS definition `{0}` deleted',
        'Are you sure you want to delete mTLS definition `{0}`?',
        true);
}
