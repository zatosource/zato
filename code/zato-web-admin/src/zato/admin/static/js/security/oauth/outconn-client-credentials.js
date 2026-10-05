
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.BearerToken = new Class({
    toString: function() {
        var s = '< id:{0} name:{1} username:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.username ? this.username : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.BearerToken;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.oauth.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(
        ['name', 'username', 'auth_server_url', 'client_id_field', 'client_secret_field', 'grant_type', 'data_format',
         'static_header', 'static_prefix']
    );
    var unique_constraints = [
        {field: 'name', entity_type: 'security', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });

    // .. the authentication method decides which credential rows apply ..
    $(document).on('change', '#id_client_auth_method', function() {
        $.fn.zato.security.oauth.update_auth_method_rows('create');
    });
    $(document).on('change', '#id_edit-client_auth_method', function() {
        $.fn.zato.security.oauth.update_auth_method_rows('edit');
    });
})

// /////////////////////////////////////////////////////////////////////////////
// Authentication method-dependent row visibility
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.oauth.config = {
    client_auth_method_default: 'client_secret',
    jwt_algorithm_default: 'RS384',
    private_key_stored_hint: 'A key is stored - leave empty to keep it',
    private_key_missing_hint: 'No key is stored yet',
    public_key_url: '/zato/security/oauth/outconn/client-credentials/public-key/{0}/cluster/{1}/'
};

$.fn.zato.security.oauth.update_auth_method_rows = function(action) {

    var is_edit = action === 'edit';
    var div = $(is_edit ? '#edit-div' : '#create-div');
    var method = $(is_edit ? '#id_edit-client_auth_method' : '#id_client_auth_method').val();

    // Which rows each method makes use of
    var visible_by_method = {
        'client_secret':   {client_secret: true,  private_key_jwt: false},
        'private_key_jwt': {client_secret: false, private_key_jwt: true}
    };

    var visible = visible_by_method[method];

    div.find('.bearer-auth-client-secret').toggleClass('hidden', !visible.client_secret);
    div.find('.bearer-auth-private-key-jwt').not('.bearer-provider-options').toggleClass('hidden', !visible.private_key_jwt);

    // Provider options stay behind their toggle link, and they fold away along with the rest of the private key rows
    if(!visible.private_key_jwt) {
        div.find('.bearer-provider-options').removeClass('visible options-expanded').addClass('hidden');
    }
};


$.fn.zato.security.oauth._on_tab_change = function(div_id) {
    return function(tab) {
        var $link = $(div_id).find('.bearer-get-token-link');
        if (tab === 'dynamic') {
            $link.show();
        }
        else {
            $link.hide();
        }
        $(div_id).find('input[name$="is_static_token"]').val(tab === 'static' ? 'on' : '');
    };
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.oauth.field_descriptions = {

    // Dynamic tokens tab
    'id_name': 'A unique name for this definition. ' +
        'Used to identify it in outgoing connections, logs and the dashboard.',
    'id_data_format': 'The format of token requests - JSON or form data. Most auth servers expect form data.',
    'id_auth_server_url': 'The token endpoint of your auth server, ' +
        'e.g. https://auth.example.com/oauth2/token. ' +
        'Zato requests and refreshes tokens there automatically, before they expire.',
    'id_username': 'Your OAuth client ID - the identifier sent to the auth server with each token request.',
    'id_client_auth_method': 'How Zato proves who it is at the token endpoint - with a client secret, ' +
        'or with a JWT signed by a private key that never leaves the server, as Okta, Auth0, Keycloak, ' +
        'Entra ID and SMART Backend Services accept.',
    'id_secret': 'The OAuth client secret matching the client ID. ' +
        'Sent to the auth server with each token request.',
    'id_private_key': 'The PEM private key that signs each token request. Its public half is what you register ' +
        'with the auth server - the key itself is stored encrypted and never shown again.',
    'id_jwt_algorithm': 'The signature algorithm the auth server expects - RS384 for SMART Backend Services, ' +
        'RS256 for most other providers, ES384 for EC keys.',
    'id_key_id': 'The kid header of each signed request. Needed when the auth server has more than one key ' +
        'registered for this client, otherwise it may stay empty.',
    'id_assertion_audience': 'The aud claim of each signed request. If empty, it is the auth. endpoint itself, ' +
        'which is what most providers expect - Auth0 needs its tenant URL with a trailing slash here.',
    'id_certificate': 'The PEM certificate registered with the auth server, for providers that find the key ' +
        'by its thumbprint rather than its kid, such as Entra ID.',
    'id_client_id_field': 'The field name that carries the client ID in token requests, client_id by default. ' +
        'Change it if your server expects a different one.',
    'id_client_secret_field': 'The field name that carries the client secret in token requests, ' +
        'client_secret by default.',
    'id_grant_type': 'The OAuth grant type to request, client_credentials by default.',
    'id_extra_fields': 'Additional key=value pairs to include in token requests, one per line, ' +
        'for servers that need non-standard parameters.',
    'id_scopes': 'OAuth scopes to request, one per line. ' +
        'The auth server limits the token to what these scopes allow.',

    // Static tokens tab
    'id_create_static_name': 'A unique name for this definition. ' +
        'It mirrors the name from the dynamic tab - both fields hold the same value.',
    'id_edit_static_name': 'A unique name for this definition. ' +
        'It mirrors the name from the dynamic tab - both fields hold the same value.',
    'id_static_header': 'The HTTP header the token goes into, Authorization by default.',
    'id_static_prefix': 'Text placed before the token in the header, Bearer by default. ' +
        'Leave it empty if the server expects the bare token.',
    'id_static_token': 'The fixed token sent with each request. It is never refreshed automatically - ' +
        'update it here whenever it changes.',

    // Inbound verification section
    'id_issuer': 'The issuer inbound JWTs must carry in their iss claim. ' +
        'If empty, it is derived from the auth. endpoint.',
    'id_jwks_url': 'Where to fetch the signing keys from. ' +
        'If empty, the issuer\'s well-known discovery document is used.',
    'id_audience': 'The audience inbound JWTs must carry in their aud claim. ' +
        'Required for this definition to accept inbound JWTs at all.',
    'id_claims': 'Additional claim=value pairs, one per line, that inbound JWTs must carry, ' +
        'e.g. department=Accounting.',
    'id_identity_claim': 'The claim whose value names the person behind an inbound JWT, ' +
        'e.g. preferred_username, email, oid or sub. Sessions, rate limits and the audit log ' +
        'then tell one person from another on the same definition.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.oauth.create = function() {
    $.fn.zato.form_tabs.reset({
        div_id: '#create-div',
        panel_prefix: 'bearer-create-tab-panel-',
        tab_labels: {dynamic: 'Dynamic tokens', static: 'Static tokens'},
        default_tab: 'dynamic',
        independent_tabs: true,
        on_change: $.fn.zato.security.oauth._on_tab_change('#create-div')
    });
    $.fn.zato.security.oauth._on_tab_change('#create-div')('dynamic');
    $('#id_client_auth_method').val($.fn.zato.security.oauth.config.client_auth_method_default);
    $('#id_jwt_algorithm').val($.fn.zato.security.oauth.config.jwt_algorithm_default);
    $.fn.zato.security.oauth.update_auth_method_rows('create');
    $.fn.zato.data_table._create_edit('create', 'Create a Bearer token definition', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.security.oauth.field_descriptions
    });
}

$.fn.zato.security.oauth.edit = function(id) {
    var instance = $.fn.zato.data_table.data[id];
    var is_static = $.fn.zato.to_bool(instance.is_static_token);
    var default_tab = is_static ? 'static' : 'dynamic';

    $.fn.zato.form_tabs.reset({
        div_id: '#edit-div',
        panel_prefix: 'bearer-edit-tab-panel-',
        tab_labels: {dynamic: 'Dynamic tokens', static: 'Static tokens'},
        default_tab: default_tab,
        independent_tabs: true,
        on_change: $.fn.zato.security.oauth._on_tab_change('#edit-div')
    });

    // Hide/show the Get token link based on token type
    $.fn.zato.security.oauth._on_tab_change('#edit-div')(default_tab);

    // Populate only the relevant fields before the dialog opens
    $('#id_edit-name').val(instance.name);
    $('#id_edit-id').val(instance.id);

    // The uniqueness check must know the original name, otherwise submitting
    // an edit that keeps the name would be blocked as a duplicate of itself
    $('#id_edit-name').data('zato-original-value', instance.name);

    if (is_static) {
        $('#id_edit-static_header').val(instance.static_header);
        $('#id_edit-static_prefix').val(instance.static_prefix);
        $('#id_edit_static_name').val(instance.name);
    }
    else {
        $('#id_edit-auth_server_url').val(instance.auth_server_url);
        $('#id_edit-username').val(instance.username);
        $('#id_edit-client_id_field').val(instance.client_id_field);
        $('#id_edit-client_secret_field').val(instance.client_secret_field);
        $('#id_edit-grant_type').val(instance.grant_type);
        $('#id_edit-extra_fields').val(instance.extra_fields);
        $('#id_edit-scopes').val(instance.scopes);
        $('#id_edit-data_format').val(instance.data_format);

        // Definitions created before private key JWT existed carry no method of their own
        var client_auth_method = instance.client_auth_method;
        if(!client_auth_method) {
            client_auth_method = $.fn.zato.security.oauth.config.client_auth_method_default;
        }
        var jwt_algorithm = instance.jwt_algorithm;
        if(!jwt_algorithm) {
            jwt_algorithm = $.fn.zato.security.oauth.config.jwt_algorithm_default;
        }

        $('#id_edit-client_auth_method').val(client_auth_method);
        $('#id_edit-jwt_algorithm').val(jwt_algorithm);
        $('#id_edit-key_id').val(instance.key_id);
        $('#id_edit-assertion_audience').val(instance.assertion_audience);
        $('#id_edit-certificate').val(instance.certificate);

        // The stored key is never shown - only whether there is one, and where its public half can be had
        var has_private_key = $.fn.zato.to_bool(instance.has_private_key);
        var hint = has_private_key ?
            $.fn.zato.security.oauth.config.private_key_stored_hint :
            $.fn.zato.security.oauth.config.private_key_missing_hint;
        $('#edit-private-key-hint').text(hint);

        var cluster_id = $('#id_edit-cluster_id').val();
        var public_key_url = String.format($.fn.zato.security.oauth.config.public_key_url, instance.id, cluster_id);
        $('#edit-public-key-link').attr('href', public_key_url);
        $('#edit-public-key-link-holder').toggleClass('hidden', !has_private_key);

        $.fn.zato.security.oauth.update_auth_method_rows('edit');
    }

    // Inbound verification fields apply to both token types
    $('#id_edit-issuer').val(instance.issuer);
    $('#id_edit-jwks_url').val(instance.jwks_url);
    $('#id_edit-audience').val(instance.audience);
    $('#id_edit-claims').val(instance.claims);
    $('#id_edit-identity_claim').val(instance.identity_claim);

    // Open the dialog without auto-populate
    $.fn.zato.data_table._create_edit('edit', 'Edit Bearer token definition', id, undefined, false);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.security.oauth.field_descriptions
    });
}

$.fn.zato.security.oauth.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    var is_static = $.fn.zato.to_bool(item.is_static_token);
    var token_type = is_static ? 'Static' : 'Dynamic';
    var hint = '<span class="form_hint">---</span>';

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', token_type);

    row += String.format('<td>{0}</td>', is_static ? hint : item.username);
    row += String.format("<td>{0}</td>", is_static ? hint : item.auth_server_url);
    row += String.format("<td style='text-align:center'>{0}</td>", is_static ? hint : item.client_id_field);

    row += String.format("<td style='text-align:center'>{0}</td>", is_static ? hint : item.client_secret_field);
    row += String.format("<td style='text-align:center'>{0}</td>", is_static ? hint : item.grant_type);
    if (is_static) {
        row += String.format('<td>{0}</td>', hint);
    }
    else {
        row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.security.oauth.get_token('{0}', this)\">Get token</a>", item.id));
    }
    if (is_static) {
        row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}', 'Change token', 'Token', 'token')\">Change token</a>", item.id));
    }
    else {
        row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}', 'Change secret', 'Secret', 'secret')\">Change secret</a>", item.id));
    }

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.oauth.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.oauth.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.scopes);
    row += String.format("<td class='ignore'>{0}</td>", item.extra_fields);

    row += String.format("<td class='ignore'>{0}</td>", item.data_format);

    row += String.format("<td class='ignore'>{0}</td>", item.static_header);
    row += String.format("<td class='ignore'>{0}</td>", is_static);
    row += String.format("<td class='ignore'>{0}</td>", item.static_prefix);

    row += String.format("<td class='ignore'>{0}</td>", item.issuer);
    row += String.format("<td class='ignore'>{0}</td>", item.jwks_url);
    row += String.format("<td class='ignore'>{0}</td>", item.audience);
    row += String.format("<td class='ignore'>{0}</td>", item.claims);
    row += String.format("<td class='ignore'>{0}</td>", item.identity_claim);

    row += String.format("<td class='ignore'>{0}</td>", item.client_auth_method);
    row += String.format("<td class='ignore'>{0}</td>", item.has_private_key);
    row += String.format("<td class='ignore'>{0}</td>", item.jwt_algorithm);
    row += String.format("<td class='ignore'>{0}</td>", item.key_id);
    row += String.format("<td class='ignore'>{0}</td>", item.assertion_audience);
    row += String.format("<td class='ignore'>{0}</td>", item.certificate);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.security.oauth.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Bearer token definition `{0}` deleted',
        'Are you sure you want to delete Bearer token definition `{0}`?',
        true);
}

$.fn.zato.security.oauth._get_token_parse = function(jqXHR) {
    console.log('[get_token] parse: status=' + jqXHR.status + ' responseText=' + String(jqXHR.responseText).substring(0, 500));
    var parsed = null;
    try { parsed = JSON.parse(jqXHR.responseText); } catch(e) {
        console.log('[get_token] parse: JSON parse error: ' + e);
    }
    if(parsed && parsed.is_success) {
        console.log('[get_token] parse: success, token length=' + parsed.token.length);
        return {
            is_success: true,
            label: 'OK',
            token: parsed.token,
            details_title: '',
            details_body: '',
            details_lexer: '',
            status_code: jqXHR.status
        };
    }

    // A body that was not JSON at all carries no details of its own
    var details_body = '';
    var status_code = jqXHR.status;

    if(parsed) {
        details_body = parsed.info;

        // The remote server's own status arrives only when the token request reached it
        if('status_code' in parsed) {
            status_code = parsed.status_code;
        }
    }

    var label = 'Error while obtaining token';
    console.log('[get_token] parse: failure, label=' + label);
    return {
        is_success: false,
        label: label,
        details_title: label,
        details_body: details_body,
        details_lexer: '',
        status_code: status_code
    };
};

$.fn.zato.security.oauth._get_token_success = function(instance, result) {
    console.log('[get_token] success callback, token length=' + result.token.length);
    var token = result.token;
    navigator.clipboard.writeText(token).then(function() {
        console.log('[get_token] token copied to clipboard');
    }, function(err) {
        console.log('[get_token] clipboard write failed: ' + err);
    });
    instance.setContent('<span style="display:inline-flex;align-items:center;white-space:nowrap;font-size:13px;color:#85e89d">OK, token copied to clipboard</span>');
    setTimeout(function() { instance.hide(); }, 2000);
};

$.fn.zato.security.oauth.get_token = function(id, link_elem) {
    console.log('[get_token] called with id=' + JSON.stringify(id));
    $.fn.zato.action_runner.run({
        link_elem: link_elem,
        url: '/zato/security/oauth/outconn/client-credentials/get-token/',
        data: JSON.stringify({id: id}),
        on_success: $.fn.zato.security.oauth._get_token_success,
        parse: $.fn.zato.security.oauth._get_token_parse,
        details_modal_title: 'Get token response'
    });
};

$.fn.zato.security.oauth.get_token_from_form = function(action, link_elem) {
    console.log('[get_token] get_token_from_form: action=' + action);
    var prefix = (action === 'edit') ? 'edit-' : '';

    if(action === 'edit') {
        var id = $('#id_edit-id').val();
        console.log('[get_token] edit mode, id=' + JSON.stringify(id));
        if(id) {
            $.fn.zato.security.oauth.get_token(id, link_elem);
            return;
        }
    }

    var raw_params = {
        username: $('#id_' + prefix + 'username').val() || '',
        secret: $('#id_' + prefix + 'secret').val() || '',
        auth_server_url: $('#id_' + prefix + 'auth_server_url').val() || '',
        client_id_field: $('#id_' + prefix + 'client_id_field').val() || '',
        client_secret_field: $('#id_' + prefix + 'client_secret_field').val() || '',
        grant_type: $('#id_' + prefix + 'grant_type').val() || '',
        scopes: $('#id_' + prefix + 'scopes').val() || '',
        extra_fields: $('#id_' + prefix + 'extra_fields').val() || '',
        data_format: $('#id_' + prefix + 'data_format').val() || 'json',
        client_auth_method: $('#id_' + prefix + 'client_auth_method').val(),
        private_key: $('#id_' + prefix + 'private_key').val(),
        jwt_algorithm: $('#id_' + prefix + 'jwt_algorithm').val(),
        key_id: $('#id_' + prefix + 'key_id').val(),
        assertion_audience: $('#id_' + prefix + 'assertion_audience').val(),
        certificate: $('#id_' + prefix + 'certificate').val()
    };

    console.log('[get_token] raw_params: auth_server_url=' + JSON.stringify(raw_params.auth_server_url)
        + ' username=' + JSON.stringify(raw_params.username)
        + ' secret_length=' + raw_params.secret.length
        + ' grant_type=' + JSON.stringify(raw_params.grant_type));

    $.fn.zato.action_runner.run({
        link_elem: link_elem,
        url: '/zato/security/oauth/outconn/client-credentials/get-token/',
        data: JSON.stringify({raw_params: raw_params}),
        on_success: $.fn.zato.security.oauth._get_token_success,
        parse: $.fn.zato.security.oauth._get_token_parse,
        details_modal_title: 'Get token response'
    });
};
