
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubSubscription = new Class({
    toString: function() {
        var s = '<PubSubSubscription id:{0} active_status:{1} sub_key:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.active_status ? this.active_status : '(none)',
                                this.sub_key ? this.sub_key : '(none)'
                                );
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubSubscription;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.endpoint_queue.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['active_status', 'sub_key']);
})

$.fn.zato.pubsub.endpoint_queue.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var empty = '<span class="form_hint">---</span>';
    var topic_patterns_html = data.topic_patterns_html ? data.topic_patterns_html : empty;
    var client_html = data.client_html ? data.client_html : empty;

    var has_sub_key = data.role.contains('sub');
    var sub_key_html;

    if(has_sub_key) {
        sub_key_html = String.format(
            '<a id="sub_key_{0}" href="javascript:$.fn.zato.pubsub.endpoint_queue.toggle_sub_key(\'{0}\')">Show</a>',
            data.id);
    }
    else {
        sub_key_html = '<span class="form_hint">---</span>';
    }

    // Update it with latest content dynamically obtained from the call to backend
    item.sub_key = data.sub_key;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', data.name);
    row += String.format('<td>{0}</td>', data.role);
    row += String.format('<td>{0}</td>', topic_patterns_html);
    row += String.format('<td>{0}</td>', client_html);
    row += String.format('<td>{0}</td>', sub_key_html);
    row += String.format('<td>{0}</td>', data.endpoint_topics_html);
    row += String.format('<td>{0}</td>', data.endpoint_queues_html);
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.pubsub.endpoint_queue.edit('{0}')\">Edit</a>", data.id));
    row += String.format('<td>{0}</td>', data.delete_html);
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.id);
    row += String.format("<td class='ignore'>{0}</td>", data.is_internal);
    row += String.format("<td class='ignore'>{0}</td>", data.is_active);
    row += String.format("<td class='ignore'>{0}</td>", data.topic_patterns);
    row += String.format("<td class='ignore'>{0}</td>", data.security_id);
    row += String.format("<td class='ignore'>{0}</td>", data.ws_channel_id);
    row += String.format("<td class='ignore'>{0}</td>", data.hook_service_id);
    row += String.format("<td class='ignore'>{0}</td>", data.sub_key);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.endpoint_queue.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the pub/sub queue', id);
}

$.fn.zato.pubsub.endpoint_queue.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Pub/sub endpoint `{0}` deleted',
        'Are you sure you want to delete the pub/sub queue `{0}`?',
        true);
}

$.fn.zato.pubsub.endpoint_queue.toggle_sub_key = function(id) {
    var hidden = 'Show';
    var instance = $.fn.zato.data_table.data[id];
    var span = $('#sub_key_' + id);

    if(span.html().startsWith(hidden)) {
        span.html(instance.sub_key);
    }
    else {
        span.html(hidden);
    }
}

$.fn.zato.pubsub.endpoint_queue.get_new_sub_key = function() {
    var sub_key = '';
    var array = new Uint8Array(24);
    var alphabet = 'abcdef0123456789'

    window.crypto.getRandomValues(array);

    for(let i = 0; i < array.length; i++) {
        sub_key += alphabet.charAt(array[i] % 16);
    }

    $('#id_edit-sub_key').val('zpsk' + sub_key);
}
