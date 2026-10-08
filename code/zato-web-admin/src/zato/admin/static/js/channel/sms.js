
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
    outconnHref: '/zato/outgoing/sms/',
    outconnType: 'outconn-sms',
    serviceHref: '/zato/service/ide/service/',

    // The DLQ page link in a row names the channel type the page reads
    deliveryConnType: 'sms-channel',

    receiveModeHuman: {
        'webhook': 'Webhook',
        'polling': 'Polling',
    },
};

// /////////////////////////////////////////////////////////////////////////////

// What the view hands over about the channel - the receive modes and where the webhook URL opens
$.fn.zato.channel.sms.serverConfig = function() {
    var config = $.fn.zato.channel.sms.config;
    var out = JSON.parse(document.getElementById(config.configId).textContent);
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {

    // The Delivery tab's popovers are set up once for both popups
    $.fn.zato.delivery_tab.init();

    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SMSChannel;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.sms.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'outconn_name', 'service', 'receive_mode']);
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
    'id_name': 'A unique name for this channel. It is also the last part of the channel\'s webhook URL.',
    'id_is_active': 'Whether this channel receives anything. An inactive channel answers callbacks and polls with nothing.',
    'id_outconn_name': 'The outgoing SMS connection whose provider and credentials the channel reads messages with.',
    'id_service': 'The service each incoming text and each delivery report is passed to.',
    'id_receive_mode': 'Webhook has the provider push each event to the channel\'s URL, ' +
        'polling has the channel ask the provider on a schedule.',
    'id_scheduler_run_every': 'How often a polling channel asks the provider for new texts and reports.',
    'id_webhook_url': 'The URL to configure in the provider\'s console for a channel in webhook mode.',
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

// The Delivery tab reads and writes the rendered Django form of one dialog at a time
$.fn.zato.channel.sms._bind_tabs = function(action, fieldPrefix) {
    $.fn.zato.delivery_tab.bind({
        panel_id: 'channel-sms-' + action + '-tab-panel-delivery',
        field_prefix: fieldPrefix,
        has_queue: true
    });
}

// The Delivery tab's lines are not table rows, so the walk covers them as well
$.fn.zato.channel.sms._init_how_it_works = function(action) {
    $.fn.zato.how_it_works.init({
        badgeId: action + '-how-it-works',
        divId: '#' + action + '-div',
        fieldSelector: 'table.form-data tr, .decision-line',
        descriptions: $.extend({},
            $.fn.zato.channel.sms.field_descriptions,
            $.fn.zato.delivery_tab.descriptions())
    });
}

// /////////////////////////////////////////////////////////////////////////////

// The webhook URL follows the channel's name, the schedule row shows for a polling channel and the URL row for a webhook one
$.fn.zato.channel.sms._apply_receive_mode = function(action, fieldPrefix) {
    var serverConfig = $.fn.zato.channel.sms.serverConfig();

    var receiveMode = $('#id_' + fieldPrefix + 'receive_mode').val();
    var isPolling = receiveMode === serverConfig.receive_mode_polling;

    $('.' + action + '-polling-block').toggleClass('hidden', !isPolling);
    $('.' + action + '-webhook-block').toggleClass('hidden', isPolling);

    var name = $('#id_' + fieldPrefix + 'name').val();
    $('#id_' + fieldPrefix + 'webhook_url').val(serverConfig.webhook_url_prefix + name);
}

$.fn.zato.channel.sms._bind_receive_mode = function(action, fieldPrefix) {
    $('#id_' + fieldPrefix + 'receive_mode').off('change.sms').on('change.sms', function() {
        $.fn.zato.channel.sms._apply_receive_mode(action, fieldPrefix);
    });
    $('#id_' + fieldPrefix + 'name').off('input.sms').on('input.sms', function() {
        $.fn.zato.channel.sms._apply_receive_mode(action, fieldPrefix);
    });
    $.fn.zato.channel.sms._apply_receive_mode(action, fieldPrefix);
}

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
    $.fn.zato.channel.sms._bind_receive_mode('create', '');
    $.fn.zato.channel.sms._init_how_it_works('create');
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.sms.edit = function(id) {
    $.fn.zato.channel.sms._reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the SMS channel', id);
    $.fn.zato.channel.sms._bind_tabs('edit', 'edit-');
    $.fn.zato.channel.sms._bind_receive_mode('edit', 'edit-');
    $.fn.zato.channel.sms._init_how_it_works('edit');
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.sms.webhookCell = function(item) {
    var config = $.fn.zato.channel.sms.config;
    var serverConfig = $.fn.zato.channel.sms.serverConfig();

    if(item.receive_mode === serverConfig.receive_mode_polling) {
        return config.noWebhookCell;
    }

    var out = serverConfig.webhook_url_prefix + item.name;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.sms.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var config = $.fn.zato.channel.sms.config;
    var isActive = item.is_active == true;
    var receiveModeHuman = config.receiveModeHuman[item.receive_mode];

    var outconnQuery = encodeURIComponent(item.outconn_name);
    var outconnHref = config.outconnHref + '?cluster=' + config.clusterId + '&type_=' + config.outconnType + '&query=' + outconnQuery;
    var serviceHref = config.serviceHref + item.service + '/?cluster=' + config.clusterId;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', isActive ? 'Yes' : 'No');
    row += String.format('<td><a href="{0}">{1}</a></td>', outconnHref, item.outconn_name);
    row += String.format('<td><a href="{0}">{1}</a></td>', serviceHref, item.service);
    row += String.format('<td>{0}</td>', receiveModeHuman);
    row += String.format("<td class='channel-sms-webhook-url-cell'>{0}</td>", $.fn.zato.channel.sms.webhookCell(item));

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

    // 4 - the Delivery tab's fields ride in the row for the edit form to read
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
