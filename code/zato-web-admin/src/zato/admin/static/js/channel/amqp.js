
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.ChannelAMQP = new Class({
    toString: function() {
        var s = '<ChannelAMQP id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)', this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.ChannelAMQP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.amqp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'username', 'password', 'queue', 'pool_size', 'service', 'prefetch_count']);
    var unique_constraints = [
        {field: 'name', entity_type: 'channel_amqp', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });

    // Open the create form right away when the URL asks for it.
    $.fn.zato.data_table.maybe_open_create_form($.fn.zato.channel.amqp.create);
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.amqp.field_descriptions = {
    'id_name': 'A unique name for this channel.<br>Used to identify it in logs and the dashboard.',
    'id_address': 'Address of the AMQP broker as host:port,<br>e.g. localhost:5672.',
    'id_username': 'Username the channel authenticates with<br>when connecting to the broker.',
    'id_password': 'Password for the username above.<br>Sent to the broker during connection setup.',
    'id_queue': 'Queue to consume messages from.<br>Each message taken off this queue<br>invokes the service below.',
    'id_service': 'Service invoked for each message from the queue.<br>The message body is in self.request.payload.',
    'id_consumer_tag_prefix': 'Prefix of the consumer tag this channel uses<br>to identify itself to the broker.<br>Makes the channel easy to spot<br>in the broker\'s management tools.',
    'id_pool_size': 'How many connections to the broker<br>this channel keeps open. More connections<br>let messages be processed in parallel.<br>The default is 10.',
    'id_data_format': 'Format of incoming message bodies, e.g. JSON.<br>With a format selected, the payload is parsed<br>before the service runs, otherwise the service<br>receives the raw message as-is.',
    'id_ack_mode': 'What to tell the broker about each message.<br>Ack confirms it so the broker deletes it,<br>Reject refuses it and the broker decides<br>whether to redeliver or discard it.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.amqp.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new AMQP channel', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.channel.amqp.field_descriptions
    });
}

$.fn.zato.channel.amqp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the AMQP channel', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.channel.amqp.field_descriptions
    });
}

$.fn.zato.channel.amqp.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var cluster_id = $(document).getUrlParam('cluster');

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td style="text-align:center">{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td style="text-align:center">{0}</td>', item.address || '');
    row += String.format('<td style="text-align:center">{0}</td>', item.username || '');
    row += String.format('<td style="text-align:center">{0}</td>', item.queue);
    row += String.format('<td style="text-align:center">{0}</td>', $.fn.zato.data_table.service_text(item.service, cluster_id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.amqp.edit('{0}')\">", item.id) + "Edit</a>");
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.amqp.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.channel.amqp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'AMQP channel `{0}` deleted',
        'Are you sure you want to delete AMQP channel [{0}]?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Live form updates registration
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.live_form_updates.register('create', [
    {object_type: 'service', target_select: '#id_service'}
]);

$.fn.zato.live_form_updates.register('edit', [
    {object_type: 'service', target_select: '#id_edit-service'}
]);
