
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubSubscription = new Class({
    toString: function() {
        var s = '<PubSubSubscription id:{0} active_status:{1} sub_key:{2} name_slug:{3}>';
        return String.format(s, this.id ? this.id : '(none)',
            this.active_status ? this.active_status : '(none)',
            this.sub_key ? this.sub_key : '(none)',
            this.name_slug ? this.name_slug : '(none)');
    },

    get_name: function() {
        return this.topic_name;
    }


});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

var elems_required = [
    'active_status',
    'sub_key',
    'server_id',
    'active_status',
    'delivery_method',
    'delivery_batch_size',
    'delivery_max_retry',
    'wait_sock_err',
    'wait_non_sock_err',
];

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubSubscription;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.endpoint_queue.data_table.new_row;
    $.fn.zato.data_table.before_submit_hook = $.fn.zato.pubsub.subscription.before_submit_hook;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(elems_required);
})

$.fn.zato.pubsub.endpoint_queue.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var topic_link = String.format(
        '<a href="/zato/pubsub/topic/?cluster={0}&query={1}">{1}</a>', data.cluster_id, data.topic_name);

    var total_link = $.fn.zato.pubsub.endpoint_queue.get_current_depth_link(data, data.cluster_id);

    var sub_key_link = item.sub_key;
    var last_interaction_link = '';

    var clear_link = String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.pubsub.endpoint_queue.clear('{0}', '{1}', '{2}')\">Clear</a>",
        data.id, data.cluster_id, data.topic_name));
    var edit_link = String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.pubsub.endpoint_queue.edit('{0}')\">Edit</a>", data.id));
    var delete_link = String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.pubsub.endpoint_queue.delete_('{0}')\">Delete</a>", data.id));

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', topic_link);
    row += String.format('<td>{0}</td>', data.active_status);

    row += String.format('<td>{0}</td>', total_link);

    row += String.format('<td>{0}</td>', data.creation_time);
    row += String.format('<td>{0}</td>', sub_key_link);
    row += String.format('<td>{0}</td>', data.ext_client_id || $.fn.zato.empty_value);

    row += clear_link;
    row += edit_link;
    row += delete_link;

    /* -- 1 -- */
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.id);
    row += String.format("<td class='ignore'>{0}</td>", data.sub_key);
    row += String.format("<td class='ignore'>{0}</td>", data.amqp_exchange);
    row += String.format("<td class='ignore'>{0}</td>", data.amqp_routing_key);
    row += String.format("<td class='ignore'>{0}</td>", data.creation_time);

    /* -- 2 -- */
    row += String.format("<td class='ignore'>{0}</td>", data.delivery_batch_size);
    row += String.format("<td class='ignore'>{0}</td>", data.delivery_data_format);
    row += String.format("<td class='ignore'>{0}</td>", data.delivery_endpoint);
    row += String.format("<td class='ignore'>{0}</td>", data.delivery_max_retry);
    row += String.format("<td class='ignore'>{0}</td>", data.delivery_method);

    /* -- 3 -- */
    row += String.format("<td class='ignore'>{0}</td>", data.endpoint_id);
    row += String.format("<td class='ignore'>{0}</td>", data.endpoint_name);
    row += String.format("<td class='ignore'>{0}</td>", data.endpoint_type);
    row += String.format("<td class='ignore'>{0}</td>", data.ext_client_id);
    row += String.format("<td class='ignore'>{0}</td>", data.files_directory_list);

    /* -- 4 -- */
    row += String.format("<td class='ignore'>{0}</td>", data.ftp_directory_list);
    row += String.format("<td class='ignore'>{0}</td>", data.is_durable);
    row += String.format("<td class='ignore'>{0}</td>", data.is_internal);
    row += String.format("<td class='ignore'>{0}</td>", data.name);

    /* -- 5 -- */
    row += String.format("<td class='ignore'>{0}</td>", data.out_amqp_id);
    row += String.format("<td class='ignore'>{0}</td>", data.out_http_method);
    row += String.format("<td class='ignore'>{0}</td>", data.out_http_soap_id);
    row += String.format("<td class='ignore'>{0}</td>", data.server_id);
    row += String.format("<td class='ignore'>{0}</td>", data.server_name);

    /* -- 6 -- */
    row += String.format("<td class='ignore'>{0}</td>", data.service_id);
    row += String.format("<td class='ignore'>{0}</td>", data.sms_twilio_from);
    row += String.format("<td class='ignore'>{0}</td>", data.sms_twilio_to_list);
    row += String.format("<td class='ignore'>{0}</td>", data.smtp_body);

    /* -- 7 -- */
    row += String.format("<td class='ignore'>{0}</td>", data.smtp_from);
    row += String.format("<td class='ignore'>{0}</td>", data.smtp_is_html);
    row += String.format("<td class='ignore'>{0}</td>", data.smtp_subject);
    row += String.format("<td class='ignore'>{0}</td>", data.smtp_to_list);
    row += String.format("<td class='ignore'>{0}</td>", data.topic_id);

    /* -- 8 -- */
    row += String.format("<td class='ignore'>{0}</td>", data.topic_name);
    row += String.format("<td class='ignore'>{0}</td>", data.wrap_one_msg_in_list);
    row += String.format("<td class='ignore'>{0}</td>", data.wait_sock_err);
    row += String.format("<td class='ignore'>{0}</td>", data.wait_non_sock_err);
    row += String.format("<td class='ignore'>{0}</td>", data.out_rest_http_soap_id);

    /* -- 9 -- */
    row += String.format("<td class='ignore'>{0}</td>", data.out_soap_http_soap_id);
    row += String.format("<td class='ignore'>{0}</td>", data.delivery_err_should_block);
    row += String.format("<td class='ignore'>{0}</td>", data.is_staging_enabled);
    row += String.format("<td class='ignore'>{0}</td>", data.current_depth_gd);
    row += String.format("<td class='ignore'>{0}</td>", data.current_depth_non_gd);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.endpoint_queue.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update subscription', id);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.endpoint_queue.get_depth_link = function(has_gd, id, name_slug, cluster_id, depth) {
    return String.format(
        '<a href="/zato/pubsub/endpoint/queue/browser/gd/{0}/queue/{1}/{2}?cluster={3}">{4}</a>',
            has_gd, id, name_slug, cluster_id, depth || 0);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.endpoint_queue.get_current_depth_link = function(data, cluster_id) {
    var current_depth_gd = $.fn.zato.pubsub.endpoint_queue.get_depth_link('true', data.id, data.name_slug, cluster_id,
        data.current_depth_gd)

    var current_depth_non_gd = $.fn.zato.pubsub.endpoint_queue.get_depth_link('false', data.id, data.name_slug, cluster_id,
        data.current_depth_non_gd)

    return current_depth = current_depth_gd + ' / ' + data.current_depth_non_gd;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.endpoint_queue.clear = function(id, cluster_id, topic_name) {

    var instance = $.fn.zato.data_table.data[id];

    var http_callback = function(data, status) {
        var success = status == 'success';

        if(success) {
            instance.current_depth_gd = 0;
            instance.current_depth_non_gd = 0;
            $('#total_depth_' + instance.id).html($.fn.zato.pubsub.endpoint_queue.get_current_depth_link(
                instance, cluster_id));
        }

        $.fn.zato.user_message(success, data.responseText);
    }

    var jq_callback = function(ok) {
        if(ok) {
            var url = String.format('/zato/pubsub/endpoint/queue/clear/cluster/{0}/queue/{1}/', cluster_id, instance.sub_key);
            $.fn.zato.post(url, http_callback, {'queue_name': topic_name}, 'text');
        }
    }

    var q = String.format('<center>Are you sure you want to clear sub queue `{0}`\nfor sub_key `{1}`?</center>',
        instance.topic_name, instance.sub_key);
    jConfirm(q, 'Please confirm', jq_callback);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.endpoint_queue.delete_ = function(id) {
    var instance = $.fn.zato.data_table.data[id];
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Deleted subscription for `{0}`',
        'Are you sure you want to delete subscription for `{0}`?',
        true, false,
        '/zato/pubsub/endpoint/queue/delete/{0}/' + instance.sub_key + '/');
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.endpoint_queue.toggle_sub_key = function(id) {
    var hidden = 'Show';
    var instance = $.fn.zato.data_table.data[id];
    var elem = $('#sub_key_' + id);

    if(elem.html().startsWith(hidden)) {
        elem.html(instance.sub_key);
    }
    else {
        elem.html(hidden);
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
