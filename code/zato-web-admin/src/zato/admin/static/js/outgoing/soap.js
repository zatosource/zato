
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.OutgoingSOAP = new Class({
    toString: function() {
        var s = '<OutgoingSOAP id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.OutgoingSOAP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.soap.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'host',
        'timeout',
        'ping_method',
    ]);

    $.fn.zato.data_table.before_submit_hook = $.fn.zato.outgoing.soap.before_submit_hook;

    // .. removing a body-credential mapping row ..
    $(document).on('click', '.body-credential-remove', function() {
        $(this).closest('.body-credential-row').remove();
        return false;
    });

    var unique_constraints = [
        {field: 'name', entity_type: 'outgoing_soap', attr_name: 'name'},
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.tab_labels = {
    main:        'Main',
    soap:        'SOAP',
    security:    'Security',
    credentials: 'Body credentials',
    more:        'More'
};

$.fn.zato.outgoing.soap._reset_tabs = function(action) {
    var is_edit = action === 'edit';
    $.fn.zato.form_tabs.reset({
        div_id:       is_edit ? '#edit-div' : '#create-div',
        panel_prefix: is_edit ? 'out-soap-edit-tab-panel-' : 'out-soap-create-tab-panel-',
        default_tab:  'main',
        tab_labels:   $.fn.zato.outgoing.soap.tab_labels
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Body-credential mapping rows
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.add_body_credential_row = function(action, name, position) {

    var row = $('<div class="body-credential-row" style="margin-bottom:4px"></div>');

    var name_input = $('<input type="text" class="body-credential-name" placeholder="Element name" style="width:40%">');
    if(name) {
        name_input.val(name);
    }

    var position_input = $('<input type="number" class="body-credential-position" placeholder="Position" min="1" style="width:15%">');
    if(position) {
        position_input.val(position);
    }

    var remove_link = $('<a href="javascript:void(0)" class="body-credential-remove">Remove</a>');

    row.append(name_input);
    row.append('&nbsp;');
    row.append(position_input);
    row.append('&nbsp;');
    row.append(remove_link);

    $('#body-credentials-' + action).append(row);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap._body_credentials_field = function(action) {
    return action === 'edit' ? '#id_edit-body_credentials' : '#id_body_credentials';
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap._populate_body_credential_rows = function(action) {

    var container = $('#body-credentials-' + action);
    container.empty();

    var value = $($.fn.zato.outgoing.soap._body_credentials_field(action)).val();
    if(!value) {
        return;
    }

    var items = [];
    try {
        items = JSON.parse(value);
    }
    catch(e) {
        return;
    }

    for(var idx = 0; idx < items.length; idx++) {
        $.fn.zato.outgoing.soap.add_body_credential_row(action, items[idx].name, items[idx].position);
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.before_submit_hook = function(form) {

    var is_edit = $(form).attr('id') === 'edit-form';
    var action = is_edit ? 'edit' : 'create';

    var out = [];

    $('#body-credentials-' + action).find('.body-credential-row').each(function() {
        var name = ($(this).find('.body-credential-name').val() || '').trim();
        if(!name) {
            return;
        }
        var elem = {name: name};
        var position = $(this).find('.body-credential-position').val();
        if(position) {
            elem.position = parseInt(position, 10);
        }
        out.push(elem);
    });

    $($.fn.zato.outgoing.soap._body_credentials_field(action)).val(out.length ? JSON.stringify(out) : '');

    return true;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.create = function() {
    $.fn.zato.outgoing.soap._reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing SOAP connection', null);
    $.fn.zato.outgoing.soap._populate_body_credential_rows('create');
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.soap.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.field_descriptions = {

    // Main tab
    'id_name': 'A unique name for this connection.<br>Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this connection can be used.<br>Messages are not sent through<br>inactive connections.',
    'id_host': 'Address of the remote SOAP server,<br>e.g. https://example.com:8443.',
    'id_url_path': 'URL path of the SOAP endpoint<br>on the remote server,<br>e.g. /services/endpoint.',
    'id_soap_action': 'Value of the SOAPAction header<br>sent with each request. Leave empty<br>if the endpoint does not require one.',
    'id_timeout': 'How many seconds to wait for a response<br>before the invocation times out.',

    // SOAP tab
    'id_soap_version': 'SOAP protocol version the endpoint expects.<br>1.2 is the most common choice today,<br>1.1 is used by older systems.',
    'id_use_ws_addressing': 'When on, WS-Addressing headers - Action,<br>MessageID, To and ReplyTo - are added<br>to each outgoing message.',
    'id_use_mtom': 'When on, binary attachments are sent<br>as MTOM/XOP parts instead of being<br>embedded in the message as Base64.',

    // Security tab
    'id_security_id': 'Security definition applied to outgoing messages,<br>e.g. WS-Security, Basic Auth<br>or an OAuth bearer token.',
    'id_validate_tls': 'Whether the TLS certificate of the remote<br>server must be validated. Turn it off<br>only in test environments.',
    'id_tls_client_cert': 'Path to a PEM file with the client certificate<br>this connection presents to mutual-TLS endpoints.<br>The file is mounted into the container and may<br>hold both the certificate and its private key.',
    'id_tls_client_key': 'Path to the private key matching the client<br>certificate, if it lives in its own PEM file.<br>Leave empty when the certificate file<br>already contains the key.',

    // Body credentials tab
    'id_body_credentials': 'Credentials from the security definition injected<br>into the message body, for endpoints that expect<br>them there rather than in a header.<br>Each mapping is an element name with an optional<br>position among the body\'s child elements.',

    // More tab
    'id_ping_method': 'HTTP method used when pinging<br>the connection, e.g. HEAD or GET.',
    'id_content_type': 'Overrides the default Content-Type header.<br>Leave empty to use the default matching<br>the SOAP version selected.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.edit = function(id) {
    $.fn.zato.outgoing.soap._reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing SOAP connection', id);
    $.fn.zato.outgoing.soap._populate_body_credential_rows('edit');
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.soap.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;

    let security_name = '<span class="form_hint">---</span>';
    if(item.security_id && item.security_id != 'ZATO_NONE') {
        security_name = item.security_id_select;
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');

    // 2
    row += String.format('<td>{0}</td>', item.host);
    row += String.format('<td>{0}</td>', item.url_path);

    // 3
    row += String.format('<td>{0}</td>', item.soap_action ? item.soap_action : '');
    row += String.format('<td>{0}</td>', item.soap_version);
    row += String.format('<td>{0}</td>', security_name);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\" class=\"ping-link\">Ping</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.soap.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.soap.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.security_id);
    row += String.format("<td class='ignore'>{0}</td>", item.validate_tls);

    row += String.format("<td class='ignore'>{0}</td>", item.ping_method);
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);

    row += String.format("<td class='ignore'>{0}</td>", item.content_type ? item.content_type : '');
    row += String.format("<td class='ignore'>{0}</td>", item.serialization_type);

    let to_django_bool = function(value) {
        return (value === true || value == 'on' || value == 'True') ? 'True' : 'False';
    };

    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.use_ws_addressing));
    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.use_mtom));
    row += String.format("<td class='ignore'>{0}</td>", item.body_credentials ? item.body_credentials : '');
    row += String.format("<td class='ignore'>{0}</td>", item.tls_client_cert ? item.tls_client_cert : '');
    row += String.format("<td class='ignore'>{0}</td>", item.tls_client_key ? item.tls_client_key : '');

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing SOAP connection `{0}` deleted',
        'Are you sure you want to delete outgoing SOAP connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Live form updates registration
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.live_form_updates.register('create', [
    {object_type: 'security', target_select: '#id_security_id', label_format: '{sec_type_name}/{name}'}
]);

$.fn.zato.live_form_updates.register('edit', [
    {object_type: 'security', target_select: '#id_edit-security_id', label_format: '{sec_type_name}/{name}'}
]);

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
