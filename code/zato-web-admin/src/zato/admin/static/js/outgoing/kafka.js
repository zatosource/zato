
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.KafkaOutgoing = new Class({
    toString: function() {
        var s = '<KafkaOutgoing id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.kafka.config = {
    clusterId: '1',
    noSecurityValue: 'ZATO_NONE',
    noSecurityCell: '<span class="form_hint">---</span>',
    securityHref: {
        'basic_auth': '/zato/security/basic-auth/',
        'oauth': '/zato/security/oauth/outconn/client-credentials/',
    },
};

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.KafkaOutgoing;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.kafka.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'topic']);
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
            filter_name: 'type_', filter_value: 'outconn-kafka'}
    ];
    $.each(unique_constraints, function(index, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.kafka.field_descriptions = {
    'id_name': 'A unique name for this connection. ' +
        'Services publish messages through it, referring to it by this exact name.',
    'id_is_active': 'Whether this connection can be used. Inactive connections do not publish messages.',
    'id_address': 'Bootstrap server address as host:port, e.g. localhost:9092. ' +
        'The client discovers the rest of the cluster from it.',
    'id_topic': 'Kafka topic the messages are published to. ' +
        'It must already exist on the broker unless auto-creation is enabled there.',
    'id_sasl_mechanism': 'SASL mechanism the connection authenticates with.',
    'id_security_id': 'Security definition the SASL mechanism takes its credentials from.',
    'id_ssl': 'Whether the connection uses TLS. When on, the certificate files below apply.',
    'id_ssl_ca_file': 'Path to a PEM file with the CA certificate that signed the broker\'s certificate.',
    'id_ssl_cert_file': 'Path to a PEM file with the client certificate, ' +
        'needed only when the broker requires mutual TLS.',
    'id_ssl_key_file': 'Path to the PEM private key matching the client certificate.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.kafka.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing Kafka connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.kafka.field_descriptions
    });
}

$.fn.zato.outgoing.kafka.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing Kafka connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.kafka.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

// The select's value is <sec_type>/<id>, its label <Type name>/<definition name>.
$.fn.zato.outgoing.kafka.securityCell = function(item) {
    var config = $.fn.zato.outgoing.kafka.config;

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

$.fn.zato.outgoing.kafka.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var ssl = item.ssl == true;
    var security = $.fn.zato.outgoing.kafka.securityCell(item);

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address);
    row += String.format('<td>{0}</td>', item.topic);
    row += String.format('<td>{0}</td>', security.cell);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.kafka.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.kafka.delete_('{0}');\">Delete</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", ssl);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_ca_file);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_cert_file);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_key_file);
    row += String.format("<td class='ignore'>{0}</td>", security.securityId);
    row += String.format("<td class='ignore'>{0}</td>", security.secType);
    row += String.format("<td class='ignore'>{0}</td>", item.sasl_mechanism);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.kafka.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing Kafka connection `{0}` deleted',
        'Are you sure you want to delete outgoing Kafka connection `{0}`?',
        true);
}

$.fn.zato.outgoing.kafka.import_demo_config = function() {
    var cluster_id = $(document).getUrlParam('cluster') || '1';
    var import_url = '/zato/outgoing/kafka/import-demo-config?cluster=' + cluster_id;

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
