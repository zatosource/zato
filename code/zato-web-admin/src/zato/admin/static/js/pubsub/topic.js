
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubEndpoint = new Class({
    toString: function() {
        var s = '<PubSubTopic id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubEndpoint;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.topic.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.before_submit_hook = $.fn.zato.pubsub.topic.before_submit_hook;
    $.fn.zato.data_table.setup_forms(['name', 'max_depth']);
})


$.fn.zato.pubsub.topic.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new pub/sub topic', null);
}

$.fn.zato.pubsub.topic.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the pub/sub topic', id);
}

$.fn.zato.pubsub.topic.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var empty = '<span class="form_hint">---</span>';
    var topic_patterns_html = data.topic_patterns_html ? data.topic_patterns_html : empty;
    var queue_patterns_html = data.queue_patterns_html ? data.queue_patterns_html : empty;
    var client_html = data.client_html ? data.client_html : empty;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', data.endpoint_details_html);
    row += String.format('<td>{0}</td>', data.role);
    row += String.format('<td>{0}</td>', topic_patterns_html);
    row += String.format('<td>{0}</td>', queue_patterns_html);
    row += String.format('<td>{0}</td>', client_html);
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.pubsub.topic.edit('{0}')\">Edit</a>", data.id));
    row += String.format('<td>{0}</td>', data.delete_html);
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.id);
    row += String.format("<td class='ignore'>{0}</td>", data.is_internal);
    row += String.format("<td class='ignore'>{0}</td>", data.is_active);
    row += String.format("<td class='ignore'>{0}</td>", data.topic_patterns);
    row += String.format("<td class='ignore'>{0}</td>", data.queue_patterns);
    row += String.format("<td class='ignore'>{0}</td>", data.security_id);
    row += String.format("<td class='ignore'>{0}</td>", data.ws_channel_id);
    row += String.format("<td class='ignore'>{0}</td>", data.hook_service_id);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.topic.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Pub/sub topic `{0}` deleted',
        'Are you sure you want to delete the pub/sub topic `{0}`?',
        true);
}
