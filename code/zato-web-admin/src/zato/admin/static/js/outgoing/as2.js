
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.OutgoingAS2 = new Class({
    toString: function() {
        var s = '<OutgoingAS2 id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = true;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.OutgoingAS2;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.as2.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'endpoint_url',
        'as2_from',
        'as2_to',
    ]);

    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'},
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as2.tab_labels = {
    main:     'Main',
    edi:      'EDI',
    security: 'Security',
    partner:  'Partner',
    keys:     'Keys',
    delivery: 'Delivery',
    more:     'More'
};

$.fn.zato.outgoing.as2._reset_tabs = function(action) {
    var is_edit = action === 'edit';
    $.fn.zato.form_tabs.reset({
        div_id:       is_edit ? '#edit-div' : '#create-div',
        panel_prefix: is_edit ? 'out-as2-edit-tab-panel-' : 'out-as2-create-tab-panel-',
        default_tab:  'main',
        tab_labels:   $.fn.zato.outgoing.as2.tab_labels
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as2.create = function() {
    $.fn.zato.outgoing.as2._reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing AS2 connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.as2.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as2.field_descriptions = {

    // Main tab
    'id_name': 'A unique name for this connection.<br>Used to identify the partner in logs<br>and the dashboard.',
    'id_is_active': 'Whether this connection can be used.<br>Messages are not sent through<br>inactive connections.',
    'id_endpoint_url': 'The partner\'s AS2 endpoint,<br>e.g. https://as2.example.com/exchange.',
    'id_as2_from': 'Your own AS2 identifier,<br>sent in the AS2-From header<br>of every outgoing message.',
    'id_as2_to': 'The partner\'s AS2 identifier,<br>sent in the AS2-To header<br>of every outgoing message.',
    'id_subject': 'The Subject header of outgoing messages.<br>Leave empty for the default.',

    // EDI tab
    'id_isa_qualifier': 'The partner\'s ISA qualifier, e.g. ZZ or 01.<br>Used for X12 routing, control numbers<br>and reconciliation.',
    'id_isa_id': 'The partner\'s ISA interchange identifier,<br>the way it appears in ISA06 or ISA08.',
    'id_gs_id': 'The partner\'s GS application identifier,<br>the way it appears in GS02 or GS03.',
    'id_unb_id': 'The partner\'s UNB identifier,<br>for partners that exchange EDIFACT<br>rather than X12.',
    'id_content_type': 'The Content-Type outgoing payloads<br>are sent with, matching what<br>the partner expects.',
    'id_inbound_topic': 'The topic this partner\'s inbound documents<br>are published to. Leave empty<br>for the default inbound topic.',
    'id_inbound_service': 'A service to invoke with this partner\'s<br>inbound documents. Takes precedence<br>over the inbound topic.',

    // Security tab
    'id_sign': 'Whether outgoing messages are signed<br>with your signing key. The select picks<br>the digest algorithm of signatures and MIC values -<br>SHA-256 is the standard, SHA-1 only<br>for partners that require it.',
    'id_encrypt': 'Whether outgoing messages are encrypted<br>to the partner\'s certificate. The select picks<br>the content encryption algorithm -<br>AES-CBC is the interop baseline,<br>GCM only for partners that accept it.',
    'id_compress': 'Whether outgoing messages are compressed<br>and whether compression runs before signing.<br>Both orders exist in the wild,<br>the partner\'s setup decides.',
    'id_mdn_mode': 'How the partner returns its receipt -<br>on the HTTP response, asynchronously<br>to a separate URL, or not at all.<br>The toggle decides if the receipt<br>must be signed.',
    'id_async_mdn_url': 'Where the partner delivers asynchronous<br>receipts. Meaningful only when the MDN mode<br>is asynchronous.',

    // Partner tab
    'id_as2_partner_cert': 'The partner\'s current certificate in PEM.<br>It verifies their signatures and encrypts<br>messages sent to them.',
    'id_as2_partner_next_cert': 'The partner\'s next certificate in PEM,<br>staged ahead of a rotation. Both certificates<br>are accepted during the overlap window<br>and one day after the activation date<br>this certificate becomes the current one.',
    'id_as2_partner_next_cert_from': 'The date the next certificate starts<br>being accepted, e.g. 2026-08-01.<br>With no date, the pasted certificate<br>is accepted right away.<br>With a date, the rotation completes<br>automatically one day after it.',
    'id_as2_peer_signing_cert': 'A pinned partner signing certificate in PEM.<br>Leave empty to verify against<br>the partner certificate above.',
    'id_as2_peer_encryption_cert': 'A pinned partner encryption certificate in PEM.<br>Leave empty to encrypt to<br>the partner certificate above.',
    'id_as2_trust_anchors': 'CA certificates in PEM that partner<br>certificates must chain up to.<br>An alternative to pinning one certificate.',

    // Keys tab
    'id_as2_signing_key': 'Your private key in PEM, pasted as text.<br>It signs every outgoing message and is<br>stored encrypted, never in plain text.',
    'id_as2_signing_cert_chain': 'The certificate chain matching the signing key,<br>in PEM - your certificate first,<br>then any intermediates.',
    'id_as2_decryption_key': 'The private key that decrypts messages<br>encrypted to you. Often the same<br>as the signing key. Stored encrypted.',
    'id_as2_next_decryption_key': 'Your next private key, staged ahead<br>of your own rotation. Messages encrypted<br>to either key decrypt during the overlap.',
    'id_as2_next_decryption_cert': 'The certificate of the next decryption key,<br>in PEM - it matches incoming messages<br>to the right key.',

    // Delivery tab
    'id_verify_tls': 'Whether the TLS certificate of the partner\'s<br>endpoint must be validated. Turn it off<br>only in test environments.',
    'id_username': 'The username for HTTP basic authentication,<br>if the partner requires it. The password<br>is set through Change password.',
    'id_http_timeout_seconds': 'How many seconds to wait for a response<br>before the delivery times out.<br>Zero keeps the default.',
    'id_http_transfer_mode': 'How the HTTP request body is framed -<br>with a Content-Length header, chunked,<br>or chunked only above the threshold.',
    'id_chunked_threshold_bytes': 'Above this many bytes the threshold<br>transfer mode switches to chunked framing.<br>Zero keeps the default.',
    'id_preserve_filename': 'Whether outgoing payloads carry their<br>filename in a Content-Disposition header.',
    'id_ack_overdue_after': 'After how many seconds a missing receipt<br>or acknowledgment counts as overdue.<br>Zero keeps the default.',
    'id_resend_max_retries': 'How many times an overdue receipt triggers<br>a resend of the original message.<br>Zero keeps the default.',

    // More tab
    'id_as2_version': 'The AS2-Version header of outgoing messages.<br>Pin it to 1.1 only for partners<br>that require the older value.',
    'id_content_transfer_encoding': 'The transfer encoding of outgoing payloads.<br>Binary is the standard, Base64 only<br>for partners that require it.',
    'id_force_base64': 'Forces Base64 encoding of outgoing payloads<br>regardless of the transfer encoding.<br>An escape hatch for stubborn peers.',
    'id_prevent_canonicalization': 'Prevents line-ending canonicalization<br>of text payloads. An escape hatch<br>for peers that disagree about it.',
    'id_warn_on_duplicate_filename': 'Whether an already-seen filename gets<br>a processed/warning receipt<br>with explicit free text.',
    'id_pool_size': 'How many pooled connections<br>this partner\'s messages are<br>delivered over.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as2.edit = function(id) {
    $.fn.zato.outgoing.as2._reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing AS2 connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.as2.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as2.data_table.new_row = function(item, data, include_tr) {
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
    row += String.format('<td>{0}</td>', item.endpoint_url);
    row += String.format('<td>{0}</td>', item.as2_from);
    row += String.format('<td>{0}</td>', item.as2_to);

    // The expiry of the partner's certificate is computed server-side,
    // so a fresh row shows a placeholder until the page is reloaded.
    row += "<td><span class='form_hint'>---</span></td>";

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\" class=\"ping-link\">Ping</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" data-name=\"{0}\" onclick=\"$.fn.zato.outgoing.as2.send_test_message(this)\" class=\"send-test-link\">Send test</a>", item.name));

    // The audit log of this connection's exchanges is filed under its AS2 identity pair.
    var audit_object_name = encodeURIComponent(item.as2_from.trim() + ':' + item.as2_to.trim());
    row += String.format('<td><a href="/zato/audit-log/?source=as2&object_name={0}&cluster=1">Audit log</a></td>', audit_object_name);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.as2.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.as2.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);

    row += String.format("<td class='ignore'>{0}</td>", item.isa_qualifier ? item.isa_qualifier : '');
    row += String.format("<td class='ignore'>{0}</td>", item.isa_id ? item.isa_id : '');
    row += String.format("<td class='ignore'>{0}</td>", item.gs_id ? item.gs_id : '');
    row += String.format("<td class='ignore'>{0}</td>", item.unb_id ? item.unb_id : '');
    row += String.format("<td class='ignore'>{0}</td>", item.subject ? item.subject : '');
    row += String.format("<td class='ignore'>{0}</td>", item.content_type ? item.content_type : '');
    row += String.format("<td class='ignore'>{0}</td>", item.inbound_topic ? item.inbound_topic : '');
    row += String.format("<td class='ignore'>{0}</td>", item.inbound_service ? item.inbound_service : '');

    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.sign));
    row += String.format("<td class='ignore'>{0}</td>", item.sign_algorithm ? item.sign_algorithm : '');
    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.encrypt));
    row += String.format("<td class='ignore'>{0}</td>", item.encryption_algorithm ? item.encryption_algorithm : '');
    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.compress));
    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.compress_before_signing));
    row += String.format("<td class='ignore'>{0}</td>", item.mdn_mode ? item.mdn_mode : '');
    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.mdn_signed));
    row += String.format("<td class='ignore'>{0}</td>", item.async_mdn_url ? item.async_mdn_url : '');

    row += String.format("<td class='ignore'>{0}</td>", item.as2_partner_cert ? item.as2_partner_cert : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as2_partner_next_cert ? item.as2_partner_next_cert : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as2_partner_next_cert_from ? item.as2_partner_next_cert_from : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as2_signing_key ? item.as2_signing_key : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as2_signing_cert_chain ? item.as2_signing_cert_chain : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as2_decryption_key ? item.as2_decryption_key : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as2_next_decryption_key ? item.as2_next_decryption_key : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as2_next_decryption_cert ? item.as2_next_decryption_cert : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as2_peer_signing_cert ? item.as2_peer_signing_cert : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as2_peer_encryption_cert ? item.as2_peer_encryption_cert : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as2_trust_anchors ? item.as2_trust_anchors : '');

    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.verify_tls));
    row += String.format("<td class='ignore'>{0}</td>", item.username ? item.username : '');
    row += String.format("<td class='ignore'>{0}</td>", item.http_timeout_seconds ? item.http_timeout_seconds : '0');
    row += String.format("<td class='ignore'>{0}</td>", item.http_transfer_mode ? item.http_transfer_mode : '');
    row += String.format("<td class='ignore'>{0}</td>", item.chunked_threshold_bytes ? item.chunked_threshold_bytes : '0');
    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.preserve_filename));
    row += String.format("<td class='ignore'>{0}</td>", item.ack_overdue_after ? item.ack_overdue_after : '0');
    row += String.format("<td class='ignore'>{0}</td>", item.resend_max_retries ? item.resend_max_retries : '0');

    row += String.format("<td class='ignore'>{0}</td>", item.as2_version ? item.as2_version : '');
    row += String.format("<td class='ignore'>{0}</td>", item.content_transfer_encoding ? item.content_transfer_encoding : '');
    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.force_base64));
    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.prevent_canonicalization));
    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.warn_on_duplicate_filename));
    row += String.format("<td class='ignore'>{0}</td>", item.pool_size);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as2.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing AS2 connection `{0}` deleted',
        'Are you sure you want to delete outgoing AS2 connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as2.send_test_config = {
    url: '/zato/outgoing/as2/send-test-message/',
    modal_title: 'Test message result',
    no_mdn_label: 'No MDN received',
    error_label: 'Test message could not be sent',
    signed_label: 'signature verified',
    unsigned_label: 'unsigned',
    mic_matched_label: 'MIC matched',
    mic_mismatch_label: 'MIC mismatch'
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as2.build_send_test_label = function(report) {
    var config = $.fn.zato.outgoing.as2.send_test_config;

    // A delivery that raised an exception carries its traceback in the details ..
    if(report.error) {
        return config.error_label;
    }

    // .. one that came back without an MDN is reported by its transport outcome ..
    if(!report.has_mdn) {
        return config.no_mdn_label + ' (HTTP ' + report.http_status + ')';
    }

    // .. and an MDN is reported by its disposition, signature and MIC comparison.
    var parts = [report.disposition];

    parts.push(report.mdn_signed ? config.signed_label : config.unsigned_label);

    if(report.mic_matched !== null) {
        parts.push(report.mic_matched ? config.mic_matched_label : config.mic_mismatch_label);
    }

    return parts.join('; ');
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as2.parse_send_test_response = function(jqXHR, textStatus) {
    var config = $.fn.zato.outgoing.as2.send_test_config;
    var body = jqXHR.responseText;

    // A non-2xx response carries an exception message rather than a report ..
    var is_http_ok = (jqXHR.status >= 200 && jqXHR.status < 300);

    if(!is_http_ok) {
        return {
            is_success: false,
            label: config.error_label,
            details_title: config.error_label,
            details_body: body
        };
    }

    // .. a report is JSON with the MDN outcome inside.
    var report = JSON.parse(body);
    var label = $.fn.zato.outgoing.as2.build_send_test_label(report);

    return {
        is_success: report.is_ok,
        label: label,
        details_title: label,
        details_body: JSON.stringify(report, null, 2)
    };
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.as2.send_test_message = function(link_elem) {
    var config = $.fn.zato.outgoing.as2.send_test_config;
    var name = link_elem.getAttribute('data-name');

    $.fn.zato.action_runner.run({
        link_elem: link_elem,
        url: config.url,
        data: 'name=' + encodeURIComponent(name),
        parse: $.fn.zato.outgoing.as2.parse_send_test_response,
        details_modal_title: config.modal_title
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
