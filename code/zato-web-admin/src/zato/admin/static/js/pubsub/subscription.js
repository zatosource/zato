
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubEndpoint = new Class({
    toString: function() {
        var s = '<PubSubEndpoint id:{0} endpoint_name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.endpoint_name ? this.endpoint_name : '(none)'
                                );
    },
    get_name: function() {
        return this.endpoint_name;
    }

});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubEndpoint;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.subscription.data_table.new_row;
    $.fn.zato.data_table.new_row_func_update_in_place = true;
    $.fn.zato.data_table.add_row_hook = $.fn.zato.pubsub.subscription.add_row_hook;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.before_populate_hook = $.fn.zato.pubsub.subscription.cleanup_hook;
    $.fn.zato.data_table.before_submit_hook = $.fn.zato.pubsub.subscription.before_submit_hook;
    $.fn.zato.data_table.setup_forms([
        'endpoint_id',
        'server_id',
        'active_status',
        'delivery_method',
        'delivery_batch_size',
        'delivery_max_retry',
        'wait_sock_err',
        'wait_non_sock_err'
    ]);

    $('#id_endpoint_id').change(function() {
        $.fn.zato.pubsub.on_endpoint_changed();
});

})



$.fn.zato.pubsub.populate_endpoint_topics = function(topic_sub_list) {
    console.log(topic_sub_list);
}

$.fn.zato.pubsub.populate_endpoint_topics_cb = function(data, status) {
    var success = status == 'success';
    if(success) {
        var topic_sub_list = $.parseJSON(data.responseText);
        $.fn.zato.pubsub.populate_endpoint_topics(topic_sub_list);
    }
    else {
        console.log(data.responseText);
    }
}

$.fn.zato.pubsub.on_endpoint_changed = function() {
    var endpoint_id = $('#id_endpoint_id').val();
    if(endpoint_id) {
        var cluster_id = $('#cluster_id').val();
        var url = String.format('/zato/pubsub/endpoint/topic-sub-list/{0}/cluster/{1}/', endpoint_id, cluster_id);
        $.fn.zato.post(url, $.fn.zato.pubsub.populate_endpoint_topics_cb, null, null, true);
    }
    else {
        var blank = '<input class="multi-select-input" id="multi-select-input" disabled="disabled"></input>';
        $('#multi-select-div').html(blank);
        $.fn.zato.pubsub.subscription.cleanup_hook($('#create-form'));
    }
}

$.fn.zato.pubsub.subscription.add_row_hook = function(instance, elem_name, html_elem) {
    if(elem_name == 'endpoint_id') {
        instance.endpoint_name = html_elem.find('option:selected').text();
    }
}

$.fn.zato.pubsub.subscription.cleanup_hook = function(form) {
    var disabled_input = $('#multi-select-input');

    if(disabled_input.length) {
        form.data('bValidator').removeMsg(disabled_input);
        disabled_input.css('background-color', '#e6e6e6');
        return true;
    }
}

$.fn.zato.pubsub.subscription.before_submit_hook = function(form) {
    var form = $(form);

    var is_edit = form.attr('id').includes('edit');
    var prefix = is_edit ? 'edit-' : '';
    var endpoint_type = $('#id_' + prefix + 'endpoint_type').val();

    if(endpoint_type == 'rest' || endpoint_type == 'soap') {
        var delivery_method = $('#id_' + prefix + 'delivery_method').val();
        var out_http_method = $('#id_' + prefix + 'out_http_method');

        if(!out_http_method.val()) {
            form.data('bValidator').showMsg(out_http_method, 'This is a required field');
            return false;
        }

    }

    if(endpoint_type == 'rest') {
        if(delivery_method == 'notify') {
            var out_rest_http_soap_id = $('#id_' + prefix + 'out_rest_http_soap_id');
            var rest_delivery_endpoint = $('#id_' + prefix + 'rest_delivery_endpoint');

            if(!out_rest_http_soap_id.val() && !rest_delivery_endpoint.val()) {
                form.data('bValidator').showMsg(out_rest_http_soap_id,
                    'This is a required field');
                return false;
            }
        }
    }

    if(endpoint_type == 'soap') {
        if(delivery_method == 'notify') {
            var out_soap_http_soap_id = $('#id_' + prefix + 'out_soap_http_soap_id');
            var rest_delivery_endpoint = $('#id_' + prefix + 'soap_delivery_endpoint');

            if(!out_soap_http_soap_id.val() && !soap_delivery_endpoint.val()) {
                form.data('bValidator').showMsg(out_soap_http_soap_id,
                    'This is a required field');
                return false;
            }
        }
    }

    var disabled_input = $('#multi-select-input');
    if(disabled_input.length) {
        disabled_input.css('background-color', '#fbffb0');
        form.data('bValidator').showMsg(disabled_input, 'No topics are available<br/>for the endpoint to subscribe to');
        return false;
    }

    return true;

}

$.fn.zato.pubsub.subscription.create = function() {
    window.zato_run_dyn_form_handler();
    $.fn.zato.pubsub.subscription.cleanup_hook($('#create-form'));
    $.fn.zato.data_table._create_edit('create', 'Create new pub/sub subscriptions', null);
}

$.fn.zato.pubsub.subscription.edit = function(id) {
    window.zato_run_dyn_form_handler();
    $.fn.zato.data_table._create_edit('edit', 'Update pub/sub subscriptions', id);
}

$.fn.zato.pubsub.subscription.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    var is_active = data.is_active ? "Yes" : "No";
    var last_seen = data.last_seen ? data.last_seen : $.fn.zato.empty_value;
    var last_deliv_time = data.last_deliv_time ? data.last_deliv_time : $.fn.zato.empty_value;

    var pubsub_endpoint_queues_link = String.format(
        '<a id="pubsub_endpoint_queues_link_{0}" href="{1}">{2}</a>', data.id, data.pubsub_endpoint_queues_link,
        data.subscription_count);

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', is_active);
    row += String.format('<td>{0}</td>', data.endpoint_name);
    row += String.format('<td>{0}</td>', data.endpoint_type);

    row += String.format('<td>{0}</td>', data.role);
    row += String.format('<td>{0}</td>', pubsub_endpoint_queues_link);

    row += String.format('<td>{0}</td>', last_seen);
    row += String.format('<td>{0}</td>', last_deliv_time);

    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.pubsub.subscription.delete_('{0}')\">Delete all subscriptions</a>", data.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.id);

    return row;
}

$.fn.zato.pubsub.subscription.on_delete_success = function(id) {
    var link = $('#pubsub_endpoint_queues_link_' + id);
    link.html(0);
}

$.fn.zato.pubsub.subscription.delete_ = function(id) {

    var on_delete_success = function() {
        $.fn.zato.pubsub.subscription.on_delete_success(id);
    }

    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Deleted subscriptions for endpoint `{0}`',
        'Are you sure you want to delete all subscriptions for endpoint `{0}`?',
        true, false, null, null, false, on_delete_success);
}
