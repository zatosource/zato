
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
         'static_header', 'static_token', 'static_prefix']
    );
    var unique_constraints = [
        {field: 'name', entity_type: 'security', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})


$.fn.zato.security.oauth._on_tab_change = function(div_id) {
    return function(tab) {
        var $link = $(div_id).find('.bearer-get-token-link');
        if (tab === 'dynamic') {
            $link.show();
        }
        else {
            $link.hide();
        }
    };
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.oauth.field_descriptions = {

    // Dynamic tokens tab
    'id_name': 'A unique name for this definition.<br>Used to identify it in outgoing connections,<br>logs and the dashboard.',
    'id_data_format': 'The format of token requests - JSON or form data.<br>Most auth servers expect form data.',
    'id_auth_server_url': 'The token endpoint of your auth server,<br>e.g. https://auth.example.com/oauth2/token.<br>Zato requests and refreshes tokens there<br>automatically, before they expire.',
    'id_username': 'Your OAuth client ID -<br>the identifier sent to the auth server<br>with each token request.',
    'id_secret': 'The OAuth client secret matching the client ID.<br>Sent to the auth server with each token request.',
    'id_client_id_field': 'The field name that carries the client ID<br>in token requests, client_id by default.<br>Change it if your server expects a different one.',
    'id_client_secret_field': 'The field name that carries the client secret<br>in token requests, client_secret by default.',
    'id_grant_type': 'The OAuth grant type to request,<br>client_credentials by default.',
    'id_extra_fields': 'Additional key=value pairs to include<br>in token requests, one per line,<br>for servers that need non-standard parameters.',
    'id_scopes': 'OAuth scopes to request, one per line.<br>The auth server limits the token<br>to what these scopes allow.',

    // Static tokens tab
    'id_create_static_name': 'A unique name for this definition.<br>It mirrors the name from the dynamic tab -<br>both fields hold the same value.',
    'id_edit_static_name': 'A unique name for this definition.<br>It mirrors the name from the dynamic tab -<br>both fields hold the same value.',
    'id_static_header': 'The HTTP header the token goes into,<br>Authorization by default.',
    'id_static_prefix': 'Text placed before the token in the header,<br>Bearer by default. Leave it empty<br>if the server expects the bare token.',
    'id_static_token': 'The fixed token sent with each request.<br>It is never refreshed automatically -<br>update it here whenever it changes.',

    // Inbound verification section
    'id_issuer': 'The issuer inbound JWTs must carry in their iss claim.<br>If empty, it is derived from the auth. endpoint.',
    'id_jwks_url': 'Where to fetch the signing keys from.<br>If empty, the issuer\'s well-known<br>discovery document is used.',
    'id_audience': 'The audience inbound JWTs must carry in their aud claim.<br>Required for this definition to accept inbound JWTs at all.',
    'id_claims': 'Additional claim=value pairs, one per line,<br>that inbound JWTs must carry,<br>e.g. department=Accounting.',
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
    $.fn.zato.data_table._create_edit('create', 'Create a Bearer token definition', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.security.oauth.field_descriptions
    });
}

$.fn.zato.security.oauth.edit = function(id) {
    var instance = $.fn.zato.data_table.data[id];
    var is_static = instance.static_token ? true : false;
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
        $('#id_edit-static_token').val(instance.static_token);
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
    }

    // Inbound verification fields apply to both token types
    $('#id_edit-issuer').val(instance.issuer);
    $('#id_edit-jwks_url').val(instance.jwks_url);
    $('#id_edit-audience').val(instance.audience);
    $('#id_edit-claims').val(instance.claims);

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

    var is_static = item.static_token ? true : false;
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
    row += String.format("<td class='ignore'>{0}</td>", item.static_token);
    row += String.format("<td class='ignore'>{0}</td>", item.static_prefix);

    row += String.format("<td class='ignore'>{0}</td>", item.issuer);
    row += String.format("<td class='ignore'>{0}</td>", item.jwks_url);
    row += String.format("<td class='ignore'>{0}</td>", item.audience);
    row += String.format("<td class='ignore'>{0}</td>", item.claims);

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
    console.log('[get_token] parse: status=' + jqXHR.status + ' responseText=' + (jqXHR.responseText || '').substring(0, 500));
    var parsed = null;
    try { parsed = JSON.parse(jqXHR.responseText); } catch(e) {
        console.log('[get_token] parse: JSON parse error: ' + e);
    }
    if(parsed && parsed.is_success) {
        console.log('[get_token] parse: success, token length=' + (parsed.token || '').length);
        return {is_success: true, label: 'OK', token: parsed.token, details_body: '', details_title: ''};
    }
    var label = 'Error while obtaining token';
    var details_body = (parsed && parsed.info) || '';
    var response_content_type = (parsed && parsed.response_content_type) || '';
    var status_code = (parsed && parsed.status_code) || 0;
    console.log('[get_token] parse: failure, label=' + label);
    return {
        is_success: false,
        label: label,
        details_title: label,
        details_body: details_body,
        response_content_type: response_content_type,
        status_code: status_code
    };
};

$.fn.zato.security.oauth._get_token_success = function(instance, result) {
    console.log('[get_token] success callback, token length=' + (result.token || '').length);
    var token = result.token || '';
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
        data_format: $('#id_' + prefix + 'data_format').val() || 'json'
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
