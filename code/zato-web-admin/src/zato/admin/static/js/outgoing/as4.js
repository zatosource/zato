
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
    'id_is_audit_log_active': 'Whether the exchanges of this connection<br>are recorded in the audit log - the messages,<br>the receipts and the bytes of each.',
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
    'id_as4_mpc': 'The message partition channel that pull requests<br>read from and that messages queued for the<br>partner to pull wait on.',
    'id_timeout': 'How many seconds to wait for a response<br>before the invocation times out.',
    'id_validate_tls': 'Whether the TLS certificate of the remote<br>server must be validated. Turn it off<br>only in test environments.',
    'id_as4_retry_max_attempts': 'How many times one message is delivered<br>in total while no receipt arrives,<br>the first delivery included.<br>Empty means the profile\'s own value.',
    'id_as4_retry_interval': 'How long a delivery goes unanswered<br>before it is repeated under the same<br>message id. Empty means the profile\'s own value.',
    'id_as4_missing_receipt_after': 'How long an exchange is given before its receipt<br>counts as missing - past this point the retries<br>stop and the exchange is reported instead.',

    // Security tab
    'id_as4_token_type': 'How your signing certificate travels in outgoing<br>messages - a single certificate, the whole chain,<br>or a SAML assertion. Empty means<br>what the profile prescribes.',
    'id_as4_username': 'The username outgoing messages carry in a<br>WS-Security UsernameToken, which is how some<br>networks authorize pull requests.<br>Leave empty to send no token.',
    'id_as4_password': 'The password that goes with the username above.<br>It travels in clear text inside the token, so the<br>connection has to be TLS. Stored encrypted.<br>Leave empty to keep the stored password.',
    'id_as4_signing_key': 'Your private key in PEM, pasted as text.<br>It signs every outgoing message and is<br>stored encrypted, never in plain text.<br>Leave empty to keep the stored key.',
    'id_as4_signing_cert_chain': 'The certificate chain matching the signing key,<br>in PEM - your access point certificate first,<br>then any intermediates.',
    'id_as4_decryption_key': 'The private key that decrypts messages<br>encrypted to you. Often the same<br>as the signing key. Stored encrypted.<br>Leave empty to keep the stored key.',
    'id_as4_saml_assertion': 'A SAML 2.0 assertion in XML, issued by a security<br>token service, that travels in place of a certificate<br>when the token type above is SAML.',
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

$.fn.zato.outgoing.as4.audit_log_object_name = function(item) {

    // Either party may be absent on an item saved without it.
    let from_party = item.as4_from_party ? item.as4_from_party.trim() : '';
    let to_party = item.as4_to_party ? item.as4_to_party.trim() : '';

    return from_party + ':' + to_party;
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

    // The audit log of this connection's exchanges is filed under its party pair.
    let audit_object_name = encodeURIComponent($.fn.zato.outgoing.as4.audit_log_object_name(item));
    row += String.format('<td><a href="/zato/audit-log/?source=as4&object_name={0}&cluster=1">Audit log</a></td>', audit_object_name);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.as4.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.as4.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.is_audit_log_active));
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.validate_tls);

    row += String.format("<td class='ignore'>{0}</td>", item.as4_service ? item.as4_service : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_action ? item.as4_action : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_agreement ? item.as4_agreement : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_mpc ? item.as4_mpc : '');

    row += String.format("<td class='ignore'>{0}</td>", item.as4_original_sender ? item.as4_original_sender : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_final_recipient ? item.as4_final_recipient : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_extra_pmodes ? item.as4_extra_pmodes : '');

    row += String.format("<td class='ignore'>{0}</td>", item.as4_token_type ? item.as4_token_type : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_username ? item.as4_username : '');

    // Private keys and the password never appear in the page - the backend keeps the stored ones
    // when their edit form fields are left empty.
    row += "<td class='ignore'></td>";
    row += "<td class='ignore'></td>";
    row += String.format("<td class='ignore'>{0}</td>", item.as4_signing_cert_chain ? item.as4_signing_cert_chain : '');
    row += "<td class='ignore'></td>";
    row += String.format("<td class='ignore'>{0}</td>", item.as4_saml_assertion ? item.as4_saml_assertion : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_peer_signing_cert ? item.as4_peer_signing_cert : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_peer_encryption_cert ? item.as4_peer_encryption_cert : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_trust_anchors ? item.as4_trust_anchors : '');

    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.as4_use_discovery));
    row += String.format("<td class='ignore'>{0}</td>", item.as4_sml_domain ? item.as4_sml_domain : '');

    row += String.format("<td class='ignore'>{0}</td>", item.as4_retry_max_attempts ? item.as4_retry_max_attempts : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_retry_interval ? item.as4_retry_interval : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_missing_receipt_after ? item.as4_missing_receipt_after : '');

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
