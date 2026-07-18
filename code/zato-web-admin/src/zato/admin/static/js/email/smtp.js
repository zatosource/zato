
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SMTP = new Class({
    toString: function() {
        var s = '<SMTP id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SMTP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.email.smtp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'host', 'port', 'timeout', 'mode']);
    var unique_constraints = [
        {field: 'name', entity_type: 'email_smtp', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });

    // Wire up the provider presets and the mode-to-port synchronization
    $('#id_provider').on('change', $.fn.zato.email.smtp.on_provider_changed);
    $('#id_mode').on('change', function() {
        $.fn.zato.email.smtp.on_mode_changed('');
    });
    $('#id_edit-mode').on('change', function() {
        $.fn.zato.email.smtp.on_mode_changed('edit-');
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.email.smtp.field_descriptions = {
    'id_name': 'A unique name for this SMTP connection.<br>Used to identify it in services, logs and the dashboard.',
    'id_is_active': 'Whether this connection can send e-mail.<br>Services cannot send anything through<br>an inactive connection.',
    'id_needs_tls_verify': 'Whether the server\'s TLS certificate is verified.<br>Turn it off only for servers<br>with self-signed certificates.',
    'id_is_debug': 'When on, the full SMTP protocol conversation<br>is written out to server logs.<br>Useful when diagnosing delivery issues.',
    'id_provider': 'Pre-fills the connection details<br>for a well-known e-mail provider.<br>Pick Generic to fill everything in yourself.',
    'id_mode': 'How the connection is secured. STARTTLS upgrades<br>a plain connection to TLS, SSL uses TLS<br>from the start and Plain sends everything unencrypted.',
    'id_host': 'Hostname of the SMTP server to connect to,<br>e.g. smtp.example.com.',
    'id_port': 'Port the SMTP server listens on.<br>Common values are 587 for STARTTLS,<br>465 for SSL/TLS and 25 for plain connections.',
    'id_username': 'Username the connection authenticates with.<br>Leave empty if the server does not require credentials.<br>The password is set separately<br>with the Change password link.',
    'id_from_address': 'Default From address for messages<br>sent through this connection,<br>e.g. notifications@example.com.',
    'id_timeout': 'How many seconds to wait for the server to respond<br>before a send attempt is abandoned.',
    'id_helo_hostname': 'Hostname announced to the server<br>in the EHLO command.<br>Leave empty to use the local hostname.',
    'id_ca_certs_path': 'Path to a CA certificate bundle on the server<br>used to verify the SMTP server\'s certificate.<br>Leave empty to use the system-wide bundle.',
    'id_ping_address': 'Optional recipient that pings of this connection<br>send their test messages to.<br>When empty, pings check the connection<br>without sending anything.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.email.smtp.get_provider = function(providerName) {
    var providers = $.fn.zato.email.smtp.config.providers;
    var out = null;

    for(var providerIdx = 0; providerIdx < providers.length; providerIdx++) {
        if(providers[providerIdx].name == providerName) {
            out = providers[providerIdx];
            break;
        }
    }

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.email.smtp.on_provider_changed = function() {
    var preset = $.fn.zato.email.smtp.get_provider($('#id_provider').val());

    // The generic preset has no host and does not overwrite what is already filled in ..
    if(preset.host) {
        $('#id_host').val(preset.host);
    }

    // .. whereas port and mode always follow the preset ..
    $('#id_port').val(preset.port);
    $('#id_mode').val(preset.mode);
    $.fn.zato.email.smtp.update_port_hint('');

    // .. and the username hint tells the user what kind of credentials the provider expects.
    $('#create-username-hint').text(preset.username_hint);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.email.smtp.update_port_hint = function(fieldPrefix) {
    var mode = $('#id_' + fieldPrefix + 'mode').val();
    var defaultPort = $.fn.zato.email.smtp.config.mode_port[mode];
    var hintId = fieldPrefix ? '#edit-port-hint' : '#create-port-hint';

    $(hintId).text('Default port for ' + mode + ': ' + defaultPort);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.email.smtp.on_mode_changed = function(fieldPrefix) {
    var modePort = $.fn.zato.email.smtp.config.mode_port;
    var portField = $('#id_' + fieldPrefix + 'port');
    var portValue = portField.val();

    // The port follows the mode only if it is empty or still holds one of the default values ..
    var isDefaultPort = !portValue;

    for(var mode in modePort) {
        if(String(modePort[mode]) == portValue) {
            isDefaultPort = true;
        }
    }

    if(isDefaultPort) {
        var newMode = $('#id_' + fieldPrefix + 'mode').val();
        portField.val(modePort[newMode]);
    }

    // .. and the hint always reflects the newly selected mode.
    $.fn.zato.email.smtp.update_port_hint(fieldPrefix);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.email.smtp.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new SMTP connection', null);
    $.fn.zato.email.smtp.update_port_hint('');
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.email.smtp.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.email.smtp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the SMTP connection', id);
    $.fn.zato.email.smtp.update_port_hint('edit-');

    // Expand the advanced block if any of its fields differs from the defaults
    var hasAdvanced = false;

    if($('#id_edit-timeout').val() != $.fn.zato.email.smtp.config.default_timeout) {
        hasAdvanced = true;
    }
    if($('#id_edit-helo_hostname').val()) {
        hasAdvanced = true;
    }
    if($('#id_edit-ca_certs_path').val()) {
        hasAdvanced = true;
    }
    if($('#id_edit-ping_address').val()) {
        hasAdvanced = true;
    }

    $.fn.zato.toggle_visible_hidden('.smtp-advanced-edit', hasAdvanced);

    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.email.smtp.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.email.smtp.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true
    var is_debug = item.is_debug == true
    var needs_tls_verify = item.needs_tls_verify == true
    var username = item.username ? item.username : "<span class='form_hint'>(None)</span>";

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? "Yes" : "No");
    row += String.format('<td>{0}</td>', item.host);
    row += String.format('<td>{0}</td>', item.port);
    row += String.format('<td>{0}</td>', username);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.email.smtp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.email.smtp.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.ping_address);
    row += String.format("<td class='ignore'>{0}</td>", is_debug);
    row += String.format("<td class='ignore'>{0}</td>", item.mode);
    row += String.format("<td class='ignore'>{0}</td>", item.username ? item.username : "");
    row += String.format("<td class='ignore'>{0}</td>", needs_tls_verify);
    row += String.format("<td class='ignore'>{0}</td>", item.ca_certs_path);
    row += String.format("<td class='ignore'>{0}</td>", item.helo_hostname);
    row += String.format("<td class='ignore'>{0}</td>", item.from_address);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.email.smtp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'SMTP connection [{0}] deleted',
        'Are you sure you want to delete the SMTP connection [{0}]?',
        true);
}
