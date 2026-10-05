
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.KafkaChannel = new Class({
    toString: function() {
        var s = '<KafkaChannel id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.kafka.config = {
    clusterId: '1',
    noSecurityValue: 'ZATO_NONE',
    noSecurityCell: '<span class="form_hint">---</span>',
    securityHref: {
        'basic_auth': '/zato/security/basic-auth/',
        'oauth': '/zato/security/oauth/outconn/client-credentials/',
    },
    serviceHref: '/zato/service/ide/service/',

    // The connection type of a channel's DLQ page
    deliveryConnType: 'kafka-channel',

    topicsSeparator: ', ',
};

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {

    $.fn.zato.channel.kafka.consumer_tab.init();
    $.fn.zato.channel.kafka.routing_tab.init();
    $.fn.zato.delivery_tab.init();

    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.KafkaChannel;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.kafka.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'topics', 'group_id', 'service']);
    $.fn.zato.live_form_updates.register('create', [
        {object_type: 'security', target_select: '#id_security_id'}
    ]);
    $.fn.zato.live_form_updates.register('edit', [
        {object_type: 'security', target_select: '#id_edit-security_id'}
    ]);
    // Generic connection names are unique per connection type,
    // so the check is scoped to this page's own type.
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name',
            filter_name: 'type_', filter_value: 'channel-kafka'}
    ];
    $.each(unique_constraints, function(index, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.kafka.field_descriptions = {
    'id_name': 'A unique name for this channel. Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this channel reads messages. An inactive channel leaves its topics untouched.',
    'id_address': 'Where Kafka is, as host:port, e.g. localhost:9092. Any one address of the Kafka cluster.',
    'id_group_id': 'The consumer group this channel joins. Kafka shares a topic\'s partitions among the consumers ' +
        'of one group and remembers how far each group has read.',
    'id_service': 'The service invoked for each message, unless a rule of the Routing tab picks another one. ' +
        'The message is in self.request.payload, the topic, key, partition, offset, timestamp and each header ' +
        'of the message are in self.request.headers.',
    'id_sasl_mechanism': 'SASL mechanism the connection authenticates with.',
    'id_security_id': 'Security definition the SASL mechanism takes its credentials from.',
    'id_ssl': 'Whether the connection uses TLS. When on, the certificate files below apply.',
    'id_ssl_ca_file': 'Path to a PEM file with the CA certificate that signed Kafka\'s certificate.',
    'id_ssl_cert_file': 'Path to a PEM file with the client certificate, ' +
        'needed only when Kafka requires mutual TLS.',
    'id_ssl_key_file': 'Path to the PEM private key matching the client certificate.',
    'id_ssl_key_password': 'Password the private key is encrypted with, if it is. Leave it empty to keep the current one.',
};

// /////////////////////////////////////////////////////////////////////////////

// The tabs of a create or edit dialog
$.fn.zato.channel.kafka.tab_labels = function() {
    var out = {
        config: 'Config',
        consumer: 'Consumer',
        routing: 'Routing',
        delivery: 'Delivery'
    };
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.kafka._bind_tabs = function(action, field_prefix) {
    $.fn.zato.channel.kafka.consumer_tab.bind({
        panel_id: 'channel-kafka-' + action + '-tab-panel-consumer',
        field_prefix: field_prefix
    });
    $.fn.zato.channel.kafka.routing_tab.bind({
        panel_id: 'channel-kafka-' + action + '-tab-panel-routing',
        field_prefix: field_prefix
    });

    // A channel has no delivery queue.
    $.fn.zato.delivery_tab.bind({
        panel_id: 'channel-kafka-' + action + '-tab-panel-delivery',
        field_prefix: field_prefix,
        has_queue: false
    });
}

$.fn.zato.channel.kafka._init_how_it_works = function(action) {
    $.fn.zato.how_it_works.init({
        badgeId: action + '-how-it-works',
        divId: '#' + action + '-div',
        fieldSelector: 'table.form-data tr, .decision-line, .kafka-routing-tab-actions',
        descriptions: $.extend({},
            $.fn.zato.channel.kafka.field_descriptions,
            $.fn.zato.channel.kafka.consumer_tab.descriptions(),
            $.fn.zato.channel.kafka.routing_tab.descriptions(),
            $.fn.zato.delivery_tab.descriptions())
    });
}

// The certificate rows are hidden while the SSL switch is off.
$.fn.zato.channel.kafka._apply_ssl_rows = function(action, field_prefix) {
    var use_ssl = $('#id_' + field_prefix + 'ssl').is(':checked');
    $('.' + action + '-ssl-block').toggleClass('hidden', !use_ssl);
}

$.fn.zato.channel.kafka._bind_ssl_rows = function(action, field_prefix) {
    $('#id_' + field_prefix + 'ssl').off('change.kafka').on('change.kafka', function() {
        $.fn.zato.channel.kafka._apply_ssl_rows(action, field_prefix);
    });
    $.fn.zato.channel.kafka._apply_ssl_rows(action, field_prefix);
}

$.fn.zato.channel.kafka._reset_tabs = function(action) {
    $.fn.zato.form_tabs.reset({
        div_id:       '#' + action + '-div',
        panel_prefix: 'channel-kafka-' + action + '-tab-panel-',
        default_tab:  'config',
        tab_labels:   $.fn.zato.channel.kafka.tab_labels()
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.kafka.create = function() {
    $.fn.zato.channel.kafka._reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new Kafka channel', null);
    $.fn.zato.channel.kafka._bind_tabs('create', '');
    $.fn.zato.channel.kafka._bind_ssl_rows('create', '');
    $.fn.zato.channel.kafka._init_how_it_works('create');
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.kafka.edit = function(id) {
    $.fn.zato.channel.kafka._reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the Kafka channel', id);
    $.fn.zato.channel.kafka._bind_tabs('edit', 'edit-');
    $.fn.zato.channel.kafka._bind_ssl_rows('edit', 'edit-');
    $.fn.zato.channel.kafka._init_how_it_works('edit');
}

// /////////////////////////////////////////////////////////////////////////////

// The select's value is <sec_type>/<id>, its label <Type name>/<definition name>.
$.fn.zato.channel.kafka.securityCell = function(item) {
    var config = $.fn.zato.channel.kafka.config;

    var out = {
        cell: config.noSecurityCell,
        securityId: '',
        secType: '',
    };

    if(!item.security_id) {
        return out;
    }

    if(item.security_id == config.noSecurityValue) {
        return out;
    }

    var valueParts = item.security_id.split('/');
    var secType = valueParts[0];

    var labelParts = item.security_id_select.split('/');
    var nameParts = labelParts.slice(1);
    var securityName = nameParts.join('/');

    var baseHref = config.securityHref[secType];
    var query = encodeURIComponent(securityName);
    var href = baseHref + '?cluster=' + config.clusterId + '&query=' + query;

    out.cell = String.format('<a href="{0}">{1}</a> ({2})', href, securityName, item.sasl_mechanism);
    out.securityId = item.security_id;
    out.secType = secType;

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The topics as the list shows them
$.fn.zato.channel.kafka.topicsText = function(item) {

    var config = $.fn.zato.channel.kafka.config;
    var names = [];

    item.topics.replace(/,/g, '\n').split('\n').forEach(function(line) {
        line = line.trim();
        if(line) {
            names.push(line);
        }
    });

    var out = names.join(config.topicsSeparator);
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.kafka.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var config = $.fn.zato.channel.kafka.config;
    var is_active = item.is_active == true;
    var ssl = item.ssl == true;
    var security = $.fn.zato.channel.kafka.securityCell(item);
    var serviceHref = config.serviceHref + item.service + '/?cluster=' + config.clusterId;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address);
    row += String.format('<td>{0}</td>', $.fn.zato.channel.kafka.topicsText(item));
    row += String.format('<td>{0}</td>', item.group_id);
    row += String.format('<td><a href="{0}">{1}</a></td>', serviceHref, item.service);
    row += String.format('<td>{0}</td>', security.cell);

    // 2
    row += $.fn.zato.delivery_tab.channel_link_cell(config.deliveryConnType, item, config.clusterId);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.kafka.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.kafka.delete_('{0}');\">Delete</a>", item.id));

    // 3
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    // 4 - SSL
    row += String.format("<td class='ignore'>{0}</td>", ssl);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_ca_file);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_cert_file);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_key_file);

    // 5 - security
    row += String.format("<td class='ignore'>{0}</td>", security.securityId);
    row += String.format("<td class='ignore'>{0}</td>", security.secType);
    row += String.format("<td class='ignore'>{0}</td>", item.sasl_mechanism);

    // 6
    row += $.fn.zato.channel.kafka.consumer_tab.row_cells(item);

    // 7
    row += $.fn.zato.delivery_tab.row_cells(item);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.kafka.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Kafka channel `{0}` deleted',
        'Are you sure you want to delete Kafka channel `{0}`?',
        true);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.kafka.import_demo_config = function() {
    var cluster_id = $(document).getUrlParam('cluster') || '1';
    var import_url = '/zato/channel/kafka/import-demo-config?cluster=' + cluster_id;

    var spinner_html = '<div id="import-spinner" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border: 2px solid #ccc; border-radius: 5px; z-index: 9999;"><div style="display: inline-block; width: 16px; height: 16px; border: 2px solid #ccc; border-top: 2px solid #333; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; vertical-align: middle;"></div>Importing ...</div><style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>';
    $('body').append(spinner_html);

    $.ajax({
        url: import_url,
        method: 'GET',
        success: function() {
            $('#import-spinner').remove();
            window.location.reload();
        },
        error: function() {
            $('#import-spinner').remove();
            alert('Import failed. Check server logs.');
        }
    });
}

// /////////////////////////////////////////////////////////////////////////////
