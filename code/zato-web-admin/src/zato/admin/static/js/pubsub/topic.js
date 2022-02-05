
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubTopic = new Class({
    toString: function() {
        var s = '<PubSubTopic id:{0} name:{1} hook_service_id:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.hook_service_id ? this.hook_service_id : '(none)'
                                );
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubTopic;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.topic.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.before_submit_hook = $.fn.zato.pubsub.topic.before_submit_hook;
    $.fn.zato.data_table.setup_forms(['name', 'max_depth_gd', 'max_depth_non_gd', 'depth_check_freq',
        'pub_buffer_size_gd', 'pub_buffer_size_non_gd', 'deliv_task_sync_interv_gd',
        'deliv_task_sync_interv_non_gd', 'limit_retention', 'limit_expiry']);
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

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    var has_gd = data.has_gd ? "Yes" : "No";
    var last_pub_time = data.last_pub_time ? data.last_pub_time : empty;

    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', has_gd);
    row += String.format('<td>{0} / {1}</td>', item.max_depth_gd, item.max_depth_non_gd);
    row += String.format('<td>{0}</td>', data.current_depth_link);
    row += String.format('<td>{0}</td>', last_pub_time);

    row += String.format('<td>{0}</td>',
        String.format("<a href=\"/zato/pubsub/subscription/?cluster={0}&topic_id={1}\">Subscriptions</a>",
        item.cluster_id, data.id));

    row += String.format('<td>{0}</td>',
        String.format("<a href=\"/zato/pubsub/message/publish/cluster/{0}/topic/{1}\">Publish</a>", item.cluster_id, data.id));

    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.pubsub.topic.clear('{0}')\">Clear</a>", data.id));

    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.pubsub.topic.edit('{0}')\">Edit</a>", data.id));

    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.pubsub.topic.delete_('{0}')\">Delete</a>", data.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.id);
    row += String.format("<td class='ignore'>{0}</td>", data.is_internal);
    row += String.format("<td class='ignore'>{0}</td>", data.is_active);
    row += String.format("<td class='ignore'>{0}</td>", data.has_gd);

    row += String.format("<td class='ignore'>{0}</td>", data.is_api_sub_allowed);
    row += String.format("<td class='ignore'>{0}</td>", data.max_depth_gd);
    row += String.format("<td class='ignore'>{0}</td>", data.max_depth_non_gd);
    row += String.format("<td class='ignore'>{0}</td>", data.depth_check_freq);

    row += String.format("<td class='ignore'>{0}</td>", data.hook_service_id);
    row += String.format("<td class='ignore'>{0}</td>", data.pub_buffer_size_gd);
    row += String.format("<td class='ignore'>{0}</td>", data.task_sync_interval);
    row += String.format("<td class='ignore'>{0}</td>", data.task_delivery_interval);

    row += String.format("<td class='ignore'>{0}</td>", data.limit_retention);
    row += String.format("<td class='ignore'>{0}</td>", data.limit_expiry);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.topic.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Pub/sub topic `{0}` deleted',
        'Are you sure you want to delete pub/sub topic `{0}`?',
        true);
}

$.fn.zato.pubsub.topic.clear = function(id) {

    var instance = $.fn.zato.data_table.data[id];

    var http_callback = function(data, status) {
        var success = status == 'success';
        $('#current_depth_' + instance.id).html('0 / 0');
        $.fn.zato.user_message(success, data.responseText);
    }

    var jq_callback = function(ok) {
        if(ok) {
            var url = String.format('./clear/cluster/{0}/topic/{1}/', $(document).getUrlParam('cluster'), instance.id);
            $.fn.zato.post(url, http_callback, '', 'text');
        }
    }

    var q = String.format('Are you sure you want to clear topic `{0}`?', instance.name);
    jConfirm(q, 'Please confirm', jq_callback);
}

$.fn.zato.pubsub.topic.delete_message = function(topic_id, msg_id, has_gd, server_name, server_pid) {

    if(server_name == null) {
        server_name = '';
    }

    if(server_pid == null) {
        server_pid = '';
    }

    var instance = $.fn.zato.data_table.data[msg_id];

    var http_callback = function(data, status) {
        var success = status == 'success';
        if(success) {
            $.fn.zato.data_table.remove_row('td.item_id_', msg_id);
        }
        $.fn.zato.user_message(success, data.responseText);
    }

    var jq_callback = function(ok) {
        if(ok) {
            var url = String.format('/zato/pubsub/message/delete/cluster/{0}/msg/{1}',
                $(document).getUrlParam('cluster'), instance.id);
            $.fn.zato.post(url, http_callback, {'has_gd':has_gd ,'server_name':server_name, 'server_pid':server_pid}, 'text');
        }
    }

    var q = String.format(
        'Are you sure you want to delete message `{0}`?<br/><center>Msg prefix `{1}`</center>', instance.id, instance.msg_prefix);
    jConfirm(q, 'Please confirm', jq_callback);
}
