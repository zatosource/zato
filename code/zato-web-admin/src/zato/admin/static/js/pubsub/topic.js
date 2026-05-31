(function($) {

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubTopic = new Class({
    toString: function() {
        var template = '<PubSubTopic id:{0} name:{1} description:{2} publisher_count:{3} subscriber_count:{4}>';
        return String.format(template, this.id, this.name, this.description, this.publisher_count, this.subscriber_count);
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubTopic;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.topic.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name']);
    var unique_constraints = [
        {field: 'name', entity_type: 'pubsub_topic', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(constraintIdx, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new pub/sub topic', null);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Edit pub/sub topic', id);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', item.description);
    row += String.format("<td class='ignore' style='text-align:center'>{0}</td>", item.publisher_count);
    row += String.format("<td class='ignore' style='text-align:center'>{0}</td>", item.subscriber_count);
    // row += String.format('<td><a href="/zato/pubsub/topic/{0}/?cluster=1">View</a></td>', encodeURIComponent(item.name));
    row += String.format('<td>{0}</td>', String.format('<a href="javascript:$.fn.zato.pubsub.topic.edit(\'{0}\')">Edit</a>', item.id));
    row += String.format('<td>{0}</td>', String.format('<a href="javascript:$.fn.zato.pubsub.topic.delete_(\'{0}\');">Delete</a>', item.id));
    row += String.format('<td>{0}</td>', String.format('<a href="javascript:$.fn.zato.pubsub.topic.publishMessage(\'{0}\')">Publish a message</a>', item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.description);
    row += String.format("<td class='ignore'>{0}</td>", item.publisher_count);
    row += String.format("<td class='ignore'>{0}</td>", item.subscriber_count);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Pub/sub topic `{0}` deleted',
        'Are you sure you want to delete pub/sub topic `{0}`?',
        true);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.getPublishUrl = function(id) {
    return '/zato/pubsub/topic/publish/' + id + '/';
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.publishMessage = function(id) {

    // Get the item from the data table ..
    var item = $.fn.zato.data_table.data[id];

    // .. and open the invoker overlay.
    $.fn.zato.invoker.open_overlay({
        id: id,
        name: item.name,
        title_prefix: 'Publish a message',
        action_label: 'Publish',
        show_more_options: false,
        history_key: 'zato.pubsub.topic.publish.' + id,
        get_invoke_url_func: $.fn.zato.pubsub.topic.getPublishUrl,
        collect_form_data_func: $.fn.zato.pubsub.topic.collectPublishFormData(item),
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.collectPublishFormData = function(item) {
    return function() {
        var formData = $.fn.zato.invoker.collect_form_data();
        formData['topic_name'] = item.name;
        return formData;
    };
}

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
