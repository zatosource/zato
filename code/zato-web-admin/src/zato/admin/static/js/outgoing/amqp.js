
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.OutgoingAMQP = new Class({
    toString: function() {
        var s = '<OutgoingAMQP id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                            );
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.OutgoingAMQP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.amqp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'username', 'password', 'delivery_mode', 'priority', 'pool_size']);
})

$.fn.zato.outgoing.amqp.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing AMQP connection', null);
}

$.fn.zato.outgoing.amqp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update outgoing AMQP connection', id);
}

$.fn.zato.outgoing.amqp.data_table.new_row = function(item, data, include_tr) {
    var row = '';
    let cluster_id = $(document).getUrlParam('cluster');

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;

    // Numbering and checkbox
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // Visible columns: name, active, address, username, app ID
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td style="text-align:center">{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td style="text-align:center">{0}</td>', item.address || $.fn.zato.empty_value);
    row += String.format('<td style="text-align:center">{0}</td>', item.username || $.fn.zato.empty_value);
    row += String.format('<td style="text-align:center">{0}</td>', item.app_id || $.fn.zato.empty_value);

    // Action buttons
    row += String.format('<td><a href="/zato/outgoing/amqp/invoke/{0}/{1}/{2}/?cluster={3}">Publish</a></td>',
        item.id, item.name, $.fn.zato.slugify(item.name), cluster_id);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.amqp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.outgoing.amqp.delete_({0});'>Delete</a>", item.id));

    // Hidden columns
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.delivery_mode || '');
    row += String.format("<td class='ignore'>{0}</td>", item.priority || '');
    row += String.format("<td class='ignore'>{0}</td>", item.content_type || '');
    row += String.format("<td class='ignore'>{0}</td>", item.content_encoding || '');
    row += String.format("<td class='ignore'>{0}</td>", item.expiration || '');
    row += String.format("<td class='ignore'>{0}</td>", item.pool_size || '');
    row += String.format("<td class='ignore'>{0}</td>", item.user_id || '');
    row += String.format("<td class='ignore'>{0}</td>", item.app_id || '---');

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.amqp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing AMQP connection `{0}` deleted',
        'Are you sure you want to delete outgoing AMQP connection `{0}`?',
        true);
}
