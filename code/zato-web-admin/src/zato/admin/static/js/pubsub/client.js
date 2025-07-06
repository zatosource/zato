// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubClient = new Class({
    toString: function() {
        var s = '<PubSubClient id:{0} name:{1} pattern:{2} access_type:{3}>';
        return String.format(s, this.id ? this.id : '(none)', 
                                this.name ? this.name : '(none)',
                                this.pattern ? this.pattern : '(none)',
                                this.access_type ? this.access_type : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubClient;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.client.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['sec_base_id', 'pattern', 'access_type']);
})

$.fn.zato.pubsub.client.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new PubSub client assignment', null);
}

$.fn.zato.pubsub.client.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Edit PubSub client assignment', id);
}

$.fn.zato.pubsub.client.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var access_type_label = '';
    
    if(item.access_type == 'publisher') {
        access_type_label = 'Publisher';
    } else if(item.access_type == 'subscriber') {
        access_type_label = 'Subscriber';
    } else if(item.access_type == 'publisher-subscriber') {
        access_type_label = 'Publisher & Subscriber';
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', item.pattern);
    row += String.format('<td style="text-align:center">{0}</td>', access_type_label);
    row += String.format('<td><a href="javascript:$.fn.zato.pubsub.client.edit(\'{0}\')">Edit</a></td>', item.id);
    row += String.format('<td><a href="javascript:$.fn.zato.pubsub.client.delete_(\'{0}\')">Delete</a></td>', item.id);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.client.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td[2]', 
        'PubSub client assignment [{0}] deleted',
        'Are you sure you want to delete the PubSub client assignment [{0}]?',
        true);
}
