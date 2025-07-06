// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubTopic = new Class({
    toString: function() {
        var s = '<PubSubTopic id:{0} name:{1} description:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.description ? this.description : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubTopic;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.topic.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'description']);
})

// Namespace for all pubsub-related functionality
if(!$.fn.zato.pubsub) {
    $.fn.zato.pubsub = {};
}

// Namespace for topic-related functionality
if(!$.fn.zato.pubsub.topic) {
    $.fn.zato.pubsub.topic = {};
}

// Namespace for topic data table functionality
if(!$.fn.zato.pubsub.topic.data_table) {
    $.fn.zato.pubsub.topic.data_table = {};
}

$.fn.zato.pubsub.topic.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new Pub/Sub topic', null);
}

$.fn.zato.pubsub.topic.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Edit Pub/Sub topic', id);
}

$.fn.zato.pubsub.topic.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', item.description ? item.description : '');
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.pubsub.topic.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.pubsub.topic.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.topic.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Pub/Sub topic `{0}` deleted',
        'Are you sure you want to delete Pub/Sub topic `{0}`?',
        true);
}
