
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

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.KafkaChannel;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.kafka.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'topic', 'group_id', 'service']);
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

$.fn.zato.channel.kafka.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new Kafka channel', null);
}

$.fn.zato.channel.kafka.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the Kafka channel', id);
}

$.fn.zato.channel.kafka.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var ssl = item.ssl == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address);
    row += String.format('<td>{0}</td>', item.topic);
    row += String.format('<td>{0}</td>', item.group_id);
    row += String.format('<td>{0}</td>', item.service);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.kafka.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.kafka.delete_('{0}');\">Delete</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", ssl);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_ca_file);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_cert_file);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_key_file);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.channel.kafka.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Kafka channel `{0}` deleted',
        'Are you sure you want to delete Kafka channel `{0}`?',
        true);
}

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
