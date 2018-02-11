
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.OutgoingWMQ = new Class({
    toString: function() {
        var s = '<OutgoingWMQ id:{0} name:{1} is_active:{2} def_id:{3} content_encoding:{4}>';
        return String.format(s, this.id ? this.id : '(none)',
            this.name ? this.name : '(none)',
            this.is_active ? this.is_active : '(none)',
            this.def_id ? this.def_id : '(none)',
            this.content_encoding ? this.content_encoding : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.OutgoingWMQ;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.jms_wmq.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'delivery_mode', 'priority', 'def_id']);
})

$.fn.zato.outgoing.jms_wmq.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing IBM MQ connection', null);
}

$.fn.zato.outgoing.jms_wmq.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update outgoing IBM MQ connection', id);
}

$.fn.zato.outgoing.jms_wmq.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var expiration = item.expiration ? item.expiration : '';

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', data.def_name);
    row += String.format('<td>{0}</td>', data.delivery_mode_text);
    row += String.format('<td>{0}</td>', item.priority);
    row += String.format('<td>{0}</td>', expiration ? expiration : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"/zato/outgoing/jms-wmq/send/cluster/{0}/conn/{1}\">Send a message</a>", item.cluster_id, item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.jms_wmq.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.outgoing.jms_wmq.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.delivery_mode);
    row += String.format("<td class='ignore'>{0}</td>", item.def_id);
    row += String.format("<td class='ignore'>{0}</td>", expiration);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.jms_wmq.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing IBM MQ connection `{0}` deleted',
        'Are you sure you want to delete the outgoing IBM MQ connection `{0}`?',
        true);
}
