
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.ChannelAS4 = new Class({
    toString: function() {
        var s = '<ChannelAS4 id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.ChannelAS4;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.as4.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'url_path',
    ]);

    var unique_constraints = [
        {field: 'name', entity_type: 'channel_as4', attr_name: 'name'},
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.as4.tab_labels = {
    main:         'Main',
    security:     'Security',
    participants: 'Participants',
    routing:      'Routing'
};

$.fn.zato.channel.as4._reset_tabs = function(action) {
    var is_edit = action === 'edit';
    $.fn.zato.form_tabs.reset({
        div_id:       is_edit ? '#edit-div' : '#create-div',
        panel_prefix: is_edit ? 'channel-as4-edit-tab-panel-' : 'channel-as4-create-tab-panel-',
        default_tab:  'main',
        tab_labels:   $.fn.zato.channel.as4.tab_labels
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.as4.create = function() {
    $.fn.zato.channel.as4._reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new AS4 channel', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.channel.as4.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.as4.field_descriptions = {

    // Main tab
    'id_name': 'A unique name for this channel.<br>Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this channel accepts messages.<br>Requests to inactive channels are rejected.',
    'id_url_path': 'The URL path this channel listens on,<br>e.g. /as4 or /peppol - the address<br>counterparties send their messages to.',
    'id_security_id': 'Optional HTTP-level security on top of AS4\'s<br>own message-level security. Counterparties<br>authenticate cryptographically, so this<br>is usually left as no security.',
    'id_as4_profile': 'The AS4 profile of the network this channel<br>serves - it selects the correct signature,<br>encryption and packaging checks.',
    'id_as4_from_party': 'The party identifier expected in incoming<br>messages as the sender. Leave empty<br>to accept any sender party.',
    'id_as4_to_party': 'Your own party identifier - the one incoming<br>messages must be addressed to,<br>e.g. your access point certificate name.',
    'id_as4_service': 'The ebMS service accepted by this channel,<br>e.g. a process identifier.<br>The profile preset supplies the usual value.',
    'id_as4_action': 'The ebMS action accepted by this channel,<br>e.g. a document type identifier.<br>The profile preset supplies the usual value.',
    'id_as4_agreement': 'The agreement reference accepted<br>by this channel, e.g. the Peppol TIA identifier.',
    'id_as4_mpc': 'The message partition channel incoming<br>messages are assigned to. Leave empty<br>unless the network assigns you one.',
    'id_as4_extra_pmodes': 'Additional service and action pairs accepted<br>under otherwise the same settings,<br>one per line, as service|action.',

    // Security tab
    'id_as4_signing_key': 'Your private key in PEM, pasted as text.<br>It signs receipts and error signals and is<br>stored encrypted, never in plain text.',
    'id_as4_signing_cert_chain': 'The certificate chain matching the signing key,<br>in PEM - your access point certificate first,<br>then any intermediates.',
    'id_as4_decryption_key': 'The private key that decrypts incoming<br>encrypted messages. Often the same<br>as the signing key. Stored encrypted.',
    'id_as4_peer_signing_cert': 'The certificate incoming messages must be<br>signed with, in PEM. Use trust anchors instead<br>when many counterparties send to this channel.',
    'id_as4_peer_encryption_cert': 'The certificate the peer encrypts to, in PEM.<br>Only needed when this channel\'s responses<br>carry encrypted payloads.',
    'id_as4_trust_anchors': 'CA certificates in PEM that the signatures<br>of incoming messages must chain up to,<br>e.g. the Peppol root CA.',

    // Participants tab
    'id_as4_serviced_participants': 'The participant identifiers this access point<br>serves, one per line, e.g. 0192:991825827.<br>Peppol documents addressed to anyone else<br>are rejected. Empty means everyone is accepted.',
    'id_as4_original_sender': 'The original sender expected in message<br>properties. Leave empty to accept any.',
    'id_as4_final_recipient': 'The final recipient expected in message<br>properties. Leave empty to accept any.',

    // Routing tab
    'id_service': 'The service that receives each accepted<br>message directly. Leave empty to publish<br>to the inbound topic instead.',
    'id_as4_inbound_topic': 'The pub/sub topic accepted messages are<br>published to when no service is configured.<br>Empty means the default zato.as4.inbound topic.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.as4.edit = function(id) {
    $.fn.zato.channel.as4._reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the AS4 channel', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.channel.as4.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.as4.data_table.new_row = function(item, data, include_tr) {
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
    row += String.format('<td>{0}</td>', item.url_path);
    row += String.format('<td>{0}</td>', item.as4_profile ? item.as4_profile : '');

    // 3
    row += String.format('<td>{0}</td>', item.service ? item.service : '<span class="form_hint">---</span>');
    row += String.format('<td>{0}</td>', security_name);
    row += "<td><span class='form_hint'>---</span></td>";

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.as4.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.as4.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.security_id);
    row += String.format("<td class='ignore'>{0}</td>", item.service ? item.service : '');

    row += String.format("<td class='ignore'>{0}</td>", item.as4_from_party ? item.as4_from_party : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_to_party ? item.as4_to_party : '');
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

    row += String.format("<td class='ignore'>{0}</td>", item.as4_serviced_participants ? item.as4_serviced_participants : '');
    row += String.format("<td class='ignore'>{0}</td>", item.as4_inbound_topic ? item.as4_inbound_topic : '');

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.as4.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'AS4 channel `{0}` deleted',
        'Are you sure you want to delete AS4 channel `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Live form updates registration
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.live_form_updates.register('create', [
    {object_type: 'security', target_select: '#id_security_id'}
]);

$.fn.zato.live_form_updates.register('edit', [
    {object_type: 'security', target_select: '#id_edit-security_id'}
]);

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
