
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.WSSecurity = new Class({
    toString: function() {
        var s = '<WSSecurity id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.WSSecurity;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.wss.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'username',
    ]);

    // .. the mode selector decides which tabs apply ..
    $(document).on('change', '#id_mode', function() {
        $.fn.zato.security.wss.update_mode_tabs('create');
    });
    $(document).on('change', '#id_edit-mode', function() {
        $.fn.zato.security.wss.update_mode_tabs('edit');
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.wss.tab_labels = {
    main:   'Main',
    token:  'Username token',
    saml:   'SAML',
    crypto: 'Crypto material'
};

$.fn.zato.security.wss._reset_tabs = function(action) {
    var is_edit = action === 'edit';
    $.fn.zato.form_tabs.reset({
        div_id:       is_edit ? '#edit-div' : '#create-div',
        panel_prefix: is_edit ? 'wss-edit-tab-panel-' : 'wss-create-tab-panel-',
        default_tab:  'main',
        tab_labels:   $.fn.zato.security.wss.tab_labels
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Mode-dependent tab visibility
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.wss.update_mode_tabs = function(action) {

    var is_edit = action === 'edit';
    var div = $(is_edit ? '#edit-div' : '#create-div');
    var mode = $(is_edit ? '#id_edit-mode' : '#id_mode').val();

    // Which tabs the mode makes use of - Main is always there,
    // the crypto material applies to both X.509 and SAML.
    var visible_by_mode = {
        'username_token': {token: true,  saml: false, crypto: false},
        'x509':           {token: false, saml: false, crypto: true},
        'saml':           {token: false, saml: true,  crypto: true}
    };

    var visible = visible_by_mode[mode] || {};

    div.find('.dashboard-tab').each(function() {
        var tab = $(this).attr('data-tab');
        if(tab === 'main') {
            return;
        }
        var show = !!visible[tab];
        $(this).toggle(show);

        // A tab that just went away cannot stay active - fall back to Main.
        if(!show && $(this).hasClass('dashboard-tab-active')) {
            div.find('.dashboard-tab[data-tab="main"]').click();
        }
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.wss.field_descriptions = {

    // Main tab
    'id_name': 'A unique name for this definition.<br>Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this definition can be used.<br>Connections do not apply<br>inactive definitions.',
    'id_mode': 'The credential scheme this definition carries -<br>a username token, X.509 signing and encryption<br>or a SAML assertion.',
    'id_username': 'The username the definition operates with.<br>With username tokens it goes into the message,<br>with other modes it identifies the definition.',

    // Username token tab
    'id_use_digest': 'When on, the password goes out in digest form<br>with a nonce and a timestamp instead of clear text.',

    // SAML tab
    'id_issuer': 'The entity that vouches for the assertion,<br>e.g. the URI of your organization or gateway.',
    'id_subject': 'Who the assertion is about,<br>e.g. the identity of the calling system or user.',
    'id_audience': 'Optionally, who the assertion is meant for.<br>Leave empty if the endpoint does not restrict it.',

    // Crypto material tab
    'id_sign': 'When on, outgoing messages are signed -<br>the message body with X.509,<br>the assertion itself with SAML.',
    'id_encrypt': 'When on, the message body is encrypted<br>for the recipient using their certificate.<br>Applies to the X.509 mode.',
    'id_signing_key': 'Path to a PEM file on the server<br>with your private key,<br>used to produce signatures.',
    'id_signing_certificate_chain': 'Path to a PEM file on the server<br>with the certificate matching the signing key,<br>optionally followed by its chain.<br>It travels with the message so the other side<br>can verify the signature.',
    'id_decryption_key': 'Path to a PEM file on the server<br>with the private key that decrypts<br>incoming messages. With RSA it is usually<br>the signing key again.',
    'id_peer_certificate': 'Path to a PEM file on the server<br>with the other side\'s certificate -<br>used to encrypt to them and to pin<br>their signatures.',
    'id_trust_anchors': 'Path to a PEM file on the server<br>with CA certificates that the other side\'s<br>signing certificates may chain up to,<br>as an alternative to pinning one certificate.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.wss.create = function() {
    $.fn.zato.security.wss._reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new WS-Security definition', null);
    $.fn.zato.security.wss.update_mode_tabs('create');
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.security.wss.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.wss.edit = function(id) {
    $.fn.zato.security.wss._reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the WS-Security definition', id);
    $.fn.zato.security.wss.update_mode_tabs('edit');
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.security.wss.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.wss._to_django_bool = function(value) {
    return (value === true || value == 'on' || value == 'True') ? 'True' : 'False';
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.wss.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = $.fn.zato.security.wss._to_django_bool(item.is_active) == 'True';

    let mode_labels = {
        'username_token': 'Username token',
        'x509': 'X.509',
        'saml': 'SAML'
    };

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');

    row += String.format('<td>{0}</td>', item.username);
    row += String.format('<td>{0}</td>', mode_labels[item.mode] || item.mode);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.wss.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.wss.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.mode);
    row += String.format("<td class='ignore'>{0}</td>", $.fn.zato.security.wss._to_django_bool(item.use_digest));
    row += String.format("<td class='ignore'>{0}</td>", $.fn.zato.security.wss._to_django_bool(item.sign));
    row += String.format("<td class='ignore'>{0}</td>", $.fn.zato.security.wss._to_django_bool(item.encrypt));
    row += String.format("<td class='ignore'>{0}</td>", item.issuer ? item.issuer : '');
    row += String.format("<td class='ignore'>{0}</td>", item.subject ? item.subject : '');
    row += String.format("<td class='ignore'>{0}</td>", item.audience ? item.audience : '');
    row += String.format("<td class='ignore'>{0}</td>", item.signing_key ? item.signing_key : '');
    row += String.format("<td class='ignore'>{0}</td>", item.signing_certificate_chain ? item.signing_certificate_chain : '');
    row += String.format("<td class='ignore'>{0}</td>", item.decryption_key ? item.decryption_key : '');
    row += String.format("<td class='ignore'>{0}</td>", item.peer_certificate ? item.peer_certificate : '');
    row += String.format("<td class='ignore'>{0}</td>", item.trust_anchors ? item.trust_anchors : '');

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.wss.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'WS-Security definition `{0}` deleted',
        'Are you sure you want to delete WS-Security definition `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
