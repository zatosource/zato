
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.OutgoingAS4 = new Class({
    toString: function() {
        var s = '<OutgoingAS4 id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.OutgoingAS4;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.as4.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'host',
        'timeout',
    ]);

    var unique_constraints = [
        {field: 'name', entity_type: 'outgoing_as4', attr_name: 'name'},
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as4.tab_labels = {
    main:     'Main',
    delivery: 'Delivery',
    security: 'Security',
    more:     'More'
};

$.fn.zato.outgoing.as4._reset_tabs = function(action) {
    var is_edit = action === 'edit';
    $.fn.zato.form_tabs.reset({
        div_id:       is_edit ? '#edit-div' : '#create-div',
        panel_prefix: is_edit ? 'out-as4-edit-tab-panel-' : 'out-as4-create-tab-panel-',
        default_tab:  'main',
        tab_labels:   $.fn.zato.outgoing.as4.tab_labels
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as4.create = function() {
    $.fn.zato.outgoing.as4._reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing AS4 connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.as4.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as4.field_descriptions = {

    // Main tab
    'id_name': 'A unique name for this connection.<br>Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this connection can be used.<br>Messages are not sent through<br>inactive connections.',
    'id_as4_profile': 'The AS4 profile of the network you exchange<br>messages with - it selects the correct<br>signing, encryption and packaging settings.',
    'id_as4_from_party': 'Your own party identifier, the way<br>the receiving side knows you,<br>e.g. your access point certificate name.',
    'id_as4_to_party': 'The receiving side\'s party identifier.<br>With discovery it is filled in automatically<br>from the receiver\'s certificate.',
    'id_as4_service': 'The ebMS service of outgoing messages,<br>e.g. a process identifier. Filled in<br>automatically when discovery is used.',
    'id_as4_action': 'The ebMS action of outgoing messages,<br>e.g. a document type identifier. Filled in<br>automatically when discovery is used.',
    'id_as4_agreement': 'The agreement reference of outgoing messages,<br>e.g. the Peppol TIA identifier.<br>The profile preset supplies the usual value.',

    // Delivery tab
    'id_host': 'Address of the receiving access point,<br>e.g. https://ap.example.com.<br>Ignored when discovery is on.',
    'id_url_path': 'URL path of the AS4 endpoint<br>on the receiving access point,<br>e.g. /as4. Ignored when discovery is on.',
    'id_as4_use_discovery': 'When on, the receiver\'s endpoint is looked up<br>dynamically through SML and SMP<br>instead of using the configured address.',
    'id_as4_sml_domain': 'The SML domain that discovery queries,<br>e.g. edelivery.tech.ec.europa.eu for production<br>or acc.edelivery.tech.ec.europa.eu for tests.',
    'id_as4_mpc': 'The message partition channel that pull<br>requests read from. Leave empty<br>unless the network assigns you one.',
    'id_timeout': 'How many seconds to wait for a response<br>before the invocation times out.',
    'id_validate_tls': 'Whether the TLS certificate of the remote<br>server must be validated. Turn it off<br>only in test environments.',

    // Security tab
    'id_as4_signing_key': 'Your private key in PEM, pasted as text.<br>It signs every outgoing message and is<br>stored encrypted, never in plain text.',
    'id_as4_signing_cert_chain': 'The certificate chain matching the signing key,<br>in PEM - your access point certificate first,<br>then any intermediates.',
    'id_as4_decryption_key': 'The private key that decrypts messages<br>encrypted to you. Often the same<br>as the signing key. Stored encrypted.',
    'id_as4_peer_signing_cert': 'The certificate the peer signs with, in PEM.<br>Used to verify receipts and incoming messages.<br>With discovery it comes from the SMP.',
    'id_as4_peer_encryption_cert': 'The certificate outgoing messages are<br>encrypted to, in PEM. With discovery<br>it comes from the SMP.',
    'id_as4_trust_anchors': 'CA certificates in PEM that peer certificates<br>must chain up to, e.g. the Peppol root CA.<br>An alternative to pinning one peer certificate.',

    // More tab
    'id_as4_original_sender': 'The participant identifier of the original sender,<br>e.g. your Peppol participant id.<br>send_to uses it when no sender is given.',
    'id_as4_final_recipient': 'The participant identifier of the final recipient.<br>send_to fills it in per message,<br>set it here only for fixed bilateral exchanges.',
    'id_as4_extra_pmodes': 'Additional service and action pairs served<br>under otherwise the same settings,<br>one per line, as service|action.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as4.edit = function(id) {
    $.fn.zato.outgoing.as4._reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing AS4 connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.as4.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as4.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;

    let to_django_bool = function(value) {
        return (value === true || value == 'on' || value == 'True') ? 'True' : 'False';
    };

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');

    // 2
    row += String.format('<td>{0}</td>', item.as4_profile ? item.as4_profile : '');
    row += String.format('<td>{0}</td>', item.host);
    row += String.format('<td>{0}</td>', item.url_path);

    // 3
    row += String.format('<td>{0}</td>', item.as4_from_party ? item.as4_from_party : '');
    row += String.format('<td>{0}</td>', item.as4_to_party ? item.as4_to_party : '');
    row += "<td><span class='form_hint'>---</span></td>";

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\" class=\"ping-link\">Test</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.as4.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.as4.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.validate_tls);

    row += String.format("<td class='ignore'>{0}</td>", item.as4_service ? item.as4_service : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_action ? item.as4_action : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_agreement ? item.as4_agreement : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_mpc ? item.as4_mpc : '');

    row += String.format("<td class='ignore'>{0}</td>", item.as4_original_sender ? item.as4_original_sender : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_final_recipient ? item.as4_final_recipient : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_extra_pmodes ? item.as4_extra_pmodes : '');

    row += String.format("<td class='ignore'>{0}</td>", item.as4_signing_key ? item.as4_signing_key : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_signing_cert_chain ? item.as4_signing_cert_chain : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_decryption_key ? item.as4_decryption_key : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_peer_signing_cert ? item.as4_peer_signing_cert : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_peer_encryption_cert ? item.as4_peer_encryption_cert : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_trust_anchors ? item.as4_trust_anchors : '');

    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.as4_use_discovery));
    row += String.format("<td class='ignore'>{0}</td>", item.as4_sml_domain ? item.as4_sml_domain : '');

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as4.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing AS4 connection `{0}` deleted',
        'Are you sure you want to delete outgoing AS4 connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
