
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Kafka = new Class({
    toString: function() {
        var s = '<Kafka id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = true;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Kafka;
    $.fn.zato.data_table.new_row_func = $.fn.zato.definition.kafka.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'server_list', 'socket_timeout', 'offset_timeout', 'broker_version']);
})

$.fn.zato.definition.kafka.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new Kafka definition', null);
}

$.fn.zato.definition.kafka.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the Kafka definition', id);
}

$.fn.zato.definition.kafka.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var should_use_zookeeper = item.should_use_zookeeper == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.server_list);

    row += String.format('<td>{0}</td>', should_use_zookeeper ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.source_address ? item.source_address : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', item.broker_version);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.definition.kafka.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.definition.kafka.delete_({0});'>Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.ping({0});'>Ping</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    // 1 -->
    row += String.format("<td class='ignore'>{0}</td>", item.should_use_zookeeper);
    row += String.format("<td class='ignore'>{0}</td>", item.should_exclude_internal_topics);
    row += String.format("<td class='ignore'>{0}</td>", item.socket_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.offset_timeout);

    // 2 -->
    row += String.format("<td class='ignore'>{0}</td>", item.is_tls_enabled);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_private_key_file);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_cert_file);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_ca_certs_file);

    // 3 -->
    row += String.format("<td class='ignore'>{0}</td>", item.tls_pem_passphrase);
    row += String.format("<td class='ignore'>{0}</td>", item.source_address);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.definition.kafka.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Kafka definition `{0}` deleted',
        'Are you sure you want to delete Kafka definition `{0}`?',
        true);
}
