
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SMSOutgoing = new Class({
    toString: function() {
        var s = '<SMSOutgoing id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sms.config = {
    clusterId: '1',
    configId: 'out-sms-config',
    alertsConfigId: 'out-sms-alerts-tab-config',
    noChannelCell: '<span class="form_hint">---</span>',
    channelHref: '/zato/channel/sms/',
    channelType: 'channel-sms',

    // The delivery page link in a row names the connection type the page reads
    deliveryConnType: 'sms',

    // The Invoke dialog
    invokeUrlPrefix: '/zato/outgoing/sms/invoke/',
    invokeHistoryKeyPrefix: 'zato.invoke-history.outconn-sms.',
    invokeTitlePrefix: 'Send a message',
    invokeActionLabel: 'Send',
    invokeRequestMode: 'ace/mode/text',
    invokeFromId: 'invoker-modal-from',
    invokeToId: 'invoker-modal-to',
    invokeRequestKey: 'data-request',
    invokeFromKey: 'from_',
    invokeToKey: 'to',

    // What each provider calls its credentials and what its host defaults to
    providerLabels: {
        'twilio': {username: 'Account SID', password: 'Auth token'},
        'vonage': {username: 'API key', password: 'API secret'},
        'infobip': {username: 'Username', password: 'API key'},
        'africas-talking': {username: 'Username', password: 'API key'},
    },
    hostLabel: 'Host',
    hostLabelRequired: 'Host (required)',
};

// /////////////////////////////////////////////////////////////////////////////

// What the view hands over about the providers - their names, default hosts and which of them have a signature secret
$.fn.zato.outgoing.sms.serverConfig = function() {
    var config = $.fn.zato.outgoing.sms.config;
    var out = JSON.parse(document.getElementById(config.configId).textContent);
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {

    // The Delivery and Alerts tabs' popovers are set up once for both popups
    $.fn.zato.delivery_tab.init();
    $.fn.zato.alerts_tab.init({config_id: $.fn.zato.outgoing.sms.config.alertsConfigId});

    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SMSOutgoing;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.sms.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'provider', 'username', 'sender']);
    $.fn.zato.live_form_updates.register('create', $.fn.zato.alerts_tab.live_configs(''));
    $.fn.zato.live_form_updates.register('edit', $.fn.zato.alerts_tab.live_configs('edit-'));

    // Generic connection names are unique per connection type,
    // so the check is scoped to this page's own type.
    var uniqueConstraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name',
            filter_name: 'type_', filter_value: 'outconn-sms'}
    ];
    $.each(uniqueConstraints, function(index, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sms.field_descriptions = {
    'id_name': 'A unique name for this connection. ' +
        'Services send messages through it, referring to it by this exact name.',
    'id_is_active': 'Whether this connection can be used. Inactive connections do not send messages.',
    'id_provider': 'The SMS provider the connection sends through. The labels of the credentials follow it.',
    'id_host': 'The provider\'s API address. Each provider has a default except Infobip, whose address is specific to the account.',
    'id_username': 'The account identifier the provider authenticates the connection with.',
    'id_secret': 'The secret the provider authenticates the connection with. ' +
        'Stored encrypted and never shown again, leave it empty to keep the current one.',
    'id_signature_secret': 'The Vonage signature secret that incoming callbacks are verified with. ' +
        'Stored encrypted and never shown again, leave it empty to keep the current one.',
    'id_sender': 'The number or alphanumeric sender ID messages are sent from, unless a service names another one.',
    'id_channel_name': 'The SMS channel whose webhook URL each message names as its status callback, ' +
        'so that delivery reports reach that channel.',
    'id_pool_size': 'How many HTTP connections to the provider are kept open at most.',
    'id_timeout': 'How many seconds a request to the provider may take before it is given up.',
};

// /////////////////////////////////////////////////////////////////////////////

// The three tabs of a create or edit dialog - the connection's own fields, the Delivery tab and the Alerts tab
$.fn.zato.outgoing.sms.tab_labels = function() {
    var out = {
        config: 'Config',
        delivery: 'Delivery',
        alerts: $.fn.zato.alerts_tab.tab_label()
    };
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The Delivery and Alerts tabs read and write the rendered Django form of one dialog at a time
$.fn.zato.outgoing.sms._bind_tabs = function(action, fieldPrefix) {
    $.fn.zato.delivery_tab.bind({
        panel_id: 'out-sms-' + action + '-tab-panel-delivery',
        field_prefix: fieldPrefix,
        has_queue: true
    });
    $.fn.zato.alerts_tab.bind({
        panel_id: 'out-sms-' + action + '-tab-panel-alerts',
        field_prefix: fieldPrefix
    });
}

// The Delivery and Alerts tabs' lines are not table rows, so the walk covers them as well
$.fn.zato.outgoing.sms._init_how_it_works = function(action) {
    $.fn.zato.how_it_works.init({
        badgeId: action + '-how-it-works',
        divId: '#' + action + '-div',
        fieldSelector: 'table.form-data tr, .decision-line',
        descriptions: $.extend({},
            $.fn.zato.outgoing.sms.field_descriptions,
            $.fn.zato.delivery_tab.descriptions(),
            $.fn.zato.alerts_tab.descriptions())
    });
}

// /////////////////////////////////////////////////////////////////////////////

// The credential labels, the host and the signature secret row follow the provider selected
$.fn.zato.outgoing.sms._apply_provider = function(action, fieldPrefix, shouldFillHost) {
    var config = $.fn.zato.outgoing.sms.config;
    var serverConfig = $.fn.zato.outgoing.sms.serverConfig();

    var provider = $('#id_' + fieldPrefix + 'provider').val();
    var labels = config.providerLabels[provider];

    $('#' + action + '-username-label').text(labels.username);
    $('#' + action + '-password-label').text(labels.password);

    var hasSignatureSecret = serverConfig.providers_with_signature_secret.indexOf(provider) !== -1;
    $('.' + action + '-signature-secret-block').toggleClass('hidden', !hasSignatureSecret);

    var isHostRequired = serverConfig.providers_requiring_host.indexOf(provider) !== -1;
    var hostLabel = config.hostLabel;
    if(isHostRequired) {
        hostLabel = config.hostLabelRequired;
    }
    $('#' + action + '-host-label').text(hostLabel);

    if(shouldFillHost) {
        $('#id_' + fieldPrefix + 'host').val(serverConfig.default_host[provider]);
    }
}

// A change of provider fills in that provider's default host, opening a dialog keeps the host it has
$.fn.zato.outgoing.sms._bind_provider = function(action, fieldPrefix) {
    $('#id_' + fieldPrefix + 'provider').off('change.sms').on('change.sms', function() {
        $.fn.zato.outgoing.sms._apply_provider(action, fieldPrefix, true);
    });
    $.fn.zato.outgoing.sms._apply_provider(action, fieldPrefix, false);
}

$.fn.zato.outgoing.sms._reset_tabs = function(action) {
    $.fn.zato.form_tabs.reset({
        div_id:       '#' + action + '-div',
        panel_prefix: 'out-sms-' + action + '-tab-panel-',
        default_tab:  'config',
        tab_labels:   $.fn.zato.outgoing.sms.tab_labels()
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sms.create = function() {
    $.fn.zato.outgoing.sms._reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing SMS connection', null);
    $.fn.zato.outgoing.sms._bind_tabs('create', '');
    $.fn.zato.outgoing.sms._bind_provider('create', '');
    $.fn.zato.outgoing.sms._init_how_it_works('create');
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sms.edit = function(id) {
    $.fn.zato.outgoing.sms._reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing SMS connection', id);
    $.fn.zato.outgoing.sms._bind_tabs('edit', 'edit-');
    $.fn.zato.outgoing.sms._bind_provider('edit', 'edit-');
    $.fn.zato.outgoing.sms._init_how_it_works('edit');
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sms.channelCell = function(item) {
    var config = $.fn.zato.outgoing.sms.config;

    if(!item.channel_name) {
        return config.noChannelCell;
    }

    var query = encodeURIComponent(item.channel_name);
    var href = config.channelHref + '?cluster=' + config.clusterId + '&type_=' + config.channelType + '&query=' + query;

    var out = String.format('<a href="{0}">{1}</a>', href, item.channel_name);
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sms.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var config = $.fn.zato.outgoing.sms.config;
    var serverConfig = $.fn.zato.outgoing.sms.serverConfig();
    var isActive = item.is_active == true;
    var providerHuman = serverConfig.provider_human[item.provider];

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', isActive ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', providerHuman);
    row += String.format('<td>{0}</td>', item.username);
    row += String.format('<td>{0}</td>', item.sender);
    row += String.format('<td>{0}</td>', $.fn.zato.outgoing.sms.channelCell(item));

    // 2
    row += String.format("<td class='out-sms-invoke-cell'>{0}</td>", String.format("<a href=\"javascript:$.fn.zato.outgoing.sms.invoke('{0}')\">Invoke</a>", item.id));
    row += $.fn.zato.delivery_tab.link_cell(config.deliveryConnType, item, config.clusterId);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.sms.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.sms.delete_('{0}');\">Delete</a>", item.id));

    // 3
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", isActive);
    row += String.format("<td class='ignore'>{0}</td>", item.provider);
    row += String.format("<td class='ignore'>{0}</td>", item.host);
    row += String.format("<td class='ignore'>{0}</td>", item.pool_size);
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);

    // 4 - the Delivery tab's fields ride in the row for the edit form to read ..
    row += $.fn.zato.delivery_tab.row_cells(item);

    // 5 - .. and so do the Alerts tab's.
    row += $.fn.zato.alerts_tab.hidden_cells(item);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sms.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing SMS connection `{0}` deleted',
        'Are you sure you want to delete outgoing SMS connection `{0}`?',
        true);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sms.getInvokeUrl = function(id) {
    var config = $.fn.zato.outgoing.sms.config;
    var out = config.invokeUrlPrefix + id + '/';
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// What the Invoke dialog posts - the message from the request pane, the sender and the recipient from the fields above it
$.fn.zato.outgoing.sms.collectInvokeFormData = function() {
    var config = $.fn.zato.outgoing.sms.config;

    var out = {};
    out[config.invokeRequestKey] = $.fn.zato.invoker._request_pane.getValue();
    out[config.invokeFromKey] = $('#' + config.invokeFromId).val();
    out[config.invokeToKey] = $('#' + config.invokeToId).val();

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sms.invokeFieldsHtml = function() {
    var config = $.fn.zato.outgoing.sms.config;

    var out = '<div class="invoker-more-options-row invoker-more-options-row-compact">'
        + '<label>From</label>'
        + '<input type="text" id="' + config.invokeFromId + '" />'
        + '</div>'
        + '<div class="invoker-more-options-row invoker-more-options-row-compact">'
        + '<label>To</label>'
        + '<input type="text" id="' + config.invokeToId + '" />'
        + '</div>';

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sms.invoke = function(id) {
    var config = $.fn.zato.outgoing.sms.config;
    var item = $.fn.zato.data_table.data[id];

    $.fn.zato.invoker.open_overlay({
        id: id,
        name: item.name,
        title_prefix: config.invokeTitlePrefix,
        action_label: config.invokeActionLabel,
        show_more_options: false,
        history_key: config.invokeHistoryKeyPrefix + id,
        request_mode: config.invokeRequestMode,
        extra_fields_html: $.fn.zato.outgoing.sms.invokeFieldsHtml(),
        get_invoke_url_func: $.fn.zato.outgoing.sms.getInvokeUrl,
        collect_form_data_func: $.fn.zato.outgoing.sms.collectInvokeFormData
    });

    // The sender always opens as the connection's own, whatever the last send changed it to
    $('#' + config.invokeFromId).val(item.sender);
}

// /////////////////////////////////////////////////////////////////////////////
