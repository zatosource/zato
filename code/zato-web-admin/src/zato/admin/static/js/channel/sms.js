
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SMSChannel = new Class({
    toString: function() {
        var s = '<SMSChannel id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.sms.config = {
    clusterId: '1',
    configId: 'channel-sms-config',
    noWebhookCell: '<span class="form_hint">---</span>',
    serviceHref: '/zato/service/ide/service/',

    // The channel type of a row's DLQ page link
    deliveryConnType: 'sms-channel',

    receiveModeHuman: {
        'webhook': 'Webhook',
        'polling': 'Polling',
    },
};

// /////////////////////////////////////////////////////////////////////////////

// The channel data of the view - the provider data, the receive modes and the webhook path prefix
$.fn.zato.channel.sms.serverConfig = function() {
    var config = $.fn.zato.channel.sms.config;
    var out = JSON.parse(document.getElementById(config.configId).textContent);
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {

    // The Config and Delivery tabs' popovers are set up once for both popups
    $.fn.zato.sms.init({config_id: $.fn.zato.channel.sms.config.configId});
    $.fn.zato.delivery_tab.init();

    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SMSChannel;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.sms.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'service']);
    $.fn.zato.live_form_updates.register('create', [
        {object_type: 'service', target_select: '#id_service'}
    ]);
    $.fn.zato.live_form_updates.register('edit', [
        {object_type: 'service', target_select: '#id_edit-service'}
    ]);

    // Generic connection names are unique per connection type,
    // so the check is scoped to this page's own type.
    var uniqueConstraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name',
            filter_name: 'type_', filter_value: 'channel-sms'}
    ];
    $.each(uniqueConstraints, function(index, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.sms.field_descriptions = {
    'id_name': 'A unique name for this channel. It is also the last part of the channel\'s webhook path.',
    'id_is_active': 'Whether this channel receives anything. An inactive channel answers callbacks and polls with nothing.',
    'id_service': 'The service each incoming text and each delivery report is passed to.',
};

// /////////////////////////////////////////////////////////////////////////////

// The two tabs of a create or edit dialog - the channel's own fields and the Delivery tab
$.fn.zato.channel.sms.tab_labels = function() {
    var out = {
        config: 'Config',
        delivery: 'Delivery'
    };
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The Config and Delivery tabs read and write the rendered Django form of one dialog at a time
$.fn.zato.channel.sms._bind_tabs = function(action, fieldPrefix) {
    $.fn.zato.sms.bind({
        panel_id: 'channel-sms-' + action + '-tab-panel-config',
        field_prefix: fieldPrefix,
        is_outgoing: false
    });
    $.fn.zato.delivery_tab.bind({
        panel_id: 'channel-sms-' + action + '-tab-panel-delivery',
        field_prefix: fieldPrefix,
        has_queue: true
    });
}

// The walk includes the two tabs' lines
$.fn.zato.channel.sms._init_how_it_works = function(action) {
    $.fn.zato.how_it_works.init({
        badgeId: action + '-how-it-works',
        divId: '#' + action + '-div',
        fieldSelector: '.decision-line',
        descriptions: $.extend({},
            $.fn.zato.channel.sms.field_descriptions,
            $.fn.zato.sms.descriptions(),
            $.fn.zato.delivery_tab.descriptions())
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.sms._reset_tabs = function(action) {
    $.fn.zato.form_tabs.reset({
        div_id:       '#' + action + '-div',
        panel_prefix: 'channel-sms-' + action + '-tab-panel-',
        default_tab:  'config',
        tab_labels:   $.fn.zato.channel.sms.tab_labels()
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.sms.create = function() {
    $.fn.zato.channel.sms._reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new SMS channel', null);
    $.fn.zato.channel.sms._bind_tabs('create', '');
    $.fn.zato.channel.sms._init_how_it_works('create');
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.sms.edit = function(id) {
    $.fn.zato.channel.sms._reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the SMS channel', id);
    $.fn.zato.channel.sms._bind_tabs('edit', 'edit-');
    $.fn.zato.channel.sms._init_how_it_works('edit');
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.sms.webhookCell = function(item) {
    var config = $.fn.zato.channel.sms.config;
    var serverConfig = $.fn.zato.channel.sms.serverConfig();

    if(item.receive_mode === serverConfig.receive_mode_polling) {
        return config.noWebhookCell;
    }

    var out = serverConfig.webhook_path_prefix + item.name;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.sms.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var config = $.fn.zato.channel.sms.config;
    var serverConfig = $.fn.zato.channel.sms.serverConfig();
    var isActive = item.is_active == true;

    // The outgoing connection is created or renamed along with the channel, so the response names it
    item.outconn_id = data.outconn_id;
    item.outconn_name = data.outconn_name;
    var receiveModeHuman = config.receiveModeHuman[item.receive_mode];
    var providerHuman = serverConfig.provider_human[item.provider];

    var serviceHref = config.serviceHref + item.service + '/?cluster=' + config.clusterId;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', isActive ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', providerHuman);
    row += String.format('<td><a href="{0}">{1}</a></td>', serviceHref, item.service);
    row += String.format('<td>{0}</td>', receiveModeHuman);
    row += String.format("<td class='channel-sms-webhook-path-cell'>{0}</td>", $.fn.zato.channel.sms.webhookCell(item));

    // 2
    row += $.fn.zato.delivery_tab.channel_link_cell(config.deliveryConnType, item, config.clusterId);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.sms.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.sms.delete_('{0}');\">Delete</a>", item.id));

    // 3
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", isActive);
    row += String.format("<td class='ignore'>{0}</td>", item.receive_mode);
    row += String.format("<td class='ignore'>{0}</td>", item.scheduler_run_every);
    row += String.format("<td class='ignore'>{0}</td>", item.scheduler_run_unit);
    row += String.format("<td class='ignore'>{0}</td>", item.outconn_name);
    row += String.format("<td class='ignore'>{0}</td>", item.outconn_id);
    row += String.format("<td class='ignore'>{0}</td>", item.provider);
    row += String.format("<td class='ignore'>{0}</td>", item.host);
    row += String.format("<td class='ignore'>{0}</td>", item.username);
    row += String.format("<td class='ignore'>{0}</td>", item.sender);

    // 4 - the Delivery tab's fields are stored in the row for the edit form
    row += $.fn.zato.delivery_tab.row_cells(item);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.sms.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'SMS channel `{0}` deleted',
        'Are you sure you want to delete SMS channel `{0}`?',
        true);
}

// /////////////////////////////////////////////////////////////////////////////
