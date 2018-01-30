
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.ChannelWMQ = new Class({
    toString: function() {
        var s = '<ChannelWMQ id:{0} name:{1} is_active:{2} def_id:{3} queue:{4} service:{5}>';
        return String.format(s, this.id ? this.id : '(none)',
            this.name ? this.name : '(none)',
            this.is_active ? this.is_active : '(none)',
            this.def_id ? this.def_id : '(none)',
            this.queue ? this.queue: '(none)',
            this.service ? this.service: '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.ChannelWMQ;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.jms_wmq.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'def_id', 'queue', 'consumer_tag_prefix', 'service']);
})

$.fn.zato.channel.jms_wmq.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new IBM MQ channel', null);
}

$.fn.zato.channel.jms_wmq.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update IBM MQ channel', id);
}

$.fn.zato.channel.jms_wmq.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var cluster_id = $(document).getUrlParam('cluster');

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', data.def_name);
    row += String.format('<td>{0}</td>', item.queue);
    row += String.format('<td>{0}</td>', $.fn.zato.data_table.service_text(item.service, cluster_id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.jms_wmq.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.channel.jms_wmq.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.def_id);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.channel.jms_wmq.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'IBM MQ channel `{0}` deleted',
        'Are you sure you want to delete IBM MQ channel `{0}`?',
        true);
}
