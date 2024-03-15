
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

var elems_required = [
    'endpoint_id',
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
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubEndpoint;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.subscription.data_table.new_row;
    $.fn.zato.data_table.new_row_func_update_in_place = true;
    $.fn.zato.data_table.add_row_hook = $.fn.zato.pubsub.subscription.add_row_hook;
    $.fn.zato.data_table.before_populate_hook = $.fn.zato.pubsub.subscription.cleanup_hook;
    $.fn.zato.data_table.before_submit_hook = $.fn.zato.pubsub.subscription.before_submit_hook;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(elems_required);

    // Maps values from selects to IDs of elements that should be made required
    const required_map = {
        "rest": ["#id_out_http_method", "#id_out_rest_http_soap_id"],
        "srv":  ["#id_service_id",      "#id_edit-service_id"],
    }

    $('#id_endpoint_id').change(function() {
        $.fn.zato.pubsub.on_endpoint_changed();
    });

    $('#id_endpoint_type').change(function() {
        $.fn.zato.pubsub.subscription.cleanup_hook($('#create-form'));
        $.fn.zato.toggle_tr_blocks(true, this.value, true);
        $.fn.zato.make_field_required_on_change(required_map, this.value);
        $.fn.zato.pubsub.set_current_endpoints(true);
        $.fn.zato.pubsub.on_endpoint_changed();
    });

    // Populate initial endpoints
    $.fn.zato.pubsub.set_current_endpoints(false);
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.set_current_endpoints = function(needs_blink) {
    $.fn.zato.set_select_values_on_source_change(
        window.zato_select_data_source_id,
        window.zato_select_data_target_id,
        window.zato_select_data_target_items,
        needs_blink,
    )
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.populate_endpoint_topics = function(item_list) {

    let item_html_prefix = "topic_checkbox_";
    let id_field = "topic_id";
    let name_field = "topic_name";
    let is_taken_field = "is_subscribed";
    let url_template = "/zato/pubsub/topic/?cluster={0}&query={1}";
    let html_table_id = "multi-select-table";
    let html_elem_id_selector = "#multi-select-div";
    let checkbox_field_name = "name";
    let disable_if_is_taken = false;

    $.fn.zato.populate_multi_checkbox(
        item_list,
        item_html_prefix,
        id_field,
        name_field,
        is_taken_field,
        url_template,
        html_table_id,
        html_elem_id_selector,
        checkbox_field_name,
        disable_if_is_taken
    );
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.populate_endpoint_topics_callback = function(data, status) {
    var success = status == 'success';
    if(success) {
        var item_list = $.parseJSON(data.responseText);
        if(item_list.length) {
            $.fn.zato.pubsub.populate_endpoint_topics(item_list);
        }
        else {
            $.fn.zato.pubsub.subscription.cleanup_hook($('#create-form'));
        }
    }
    else {
        console.log(data.responseText);
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.on_endpoint_changed = function() {
    var endpoint_id = $('#id_endpoint_id').val();
    if(endpoint_id) {
        var cluster_id = $('#cluster_id').val();
        var url = String.format('/zato/pubsub/endpoint/topic-sub-list/{0}/cluster/{1}/', endpoint_id, cluster_id);
        $.fn.zato.post(url, $.fn.zato.pubsub.populate_endpoint_topics_callback, null, null, true);
    }
    else {
        $.fn.zato.pubsub.subscription.cleanup_hook($('#create-form'));
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.add_row_hook = function(instance, elem_name, html_elem, data) {
    if(elem_name == 'endpoint_id') {
        instance.endpoint_name = html_elem.find('option:selected').text();
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.cleanup_hook = function(form, _unused_prefix) {

    var blank = '<input class="multi-select-input" id="multi-select-input" disabled="disabled"></input>';
    $('#multi-select-div').html(blank);

    return true;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.create = function() {
    $.fn.zato.pubsub.subscription.cleanup_hook($('#create-form'));
    $.fn.zato.data_table._create_edit('create', 'Create pub/sub subscriptions', null);
    $("#id_endpoint_id").val($("#id_endpoint_id option:first").val());
    $.fn.zato.pubsub.on_endpoint_changed();
    $.fn.zato.pubsub.set_current_endpoints(false);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.data_table.new_row = function(item, data, include_tr) {

    var row = '';

    var is_active = data.is_active ? "Yes" : "No";
    var cluster_id = $('#cluster_id').val();
    var endpoint_type_human = '';

    if(data.endpoint_type == 'srv') {
        endpoint_type_human = 'Service';
    }
    else if(data.endpoint_type == 'rest') {
        endpoint_type_human = 'REST';
    }
    else {
        endpoint_type_human = data.endpoint_type;
    }

    // var last_pub_time = data.last_pub_time ? data.last_pub_time : $.fn.zato.empty_value;
    // var last_seen = data.last_seen ? data.last_seen : $.fn.zato.empty_value;
    // var last_deliv_time = data.last_deliv_time ? data.last_deliv_time : $.fn.zato.empty_value;

    var pubsub_endpoint_queues_link = String.format(
        '<a id="pubsub_endpoint_queues_link_{0}" href="{1}?cluster={2}">{3}</a>',
        data.id,
        data.pubsub_endpoint_queues_link,
        cluster_id,
        data.subscription_count,
    );

    var endpoint_name_link = String.format(
        '<a href="/zato/pubsub/endpoint/?cluster={0}&query={1}">{1}</a>',
        cluster_id,
        data.endpoint_name,
    );

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', is_active);
    row += String.format('<td>{0}</td>', endpoint_name_link);
    row += String.format('<td>{0}</td>', endpoint_type_human);

    row += String.format('<td>{0}</td>', data.role);
    row += String.format('<td>{0}</td>', pubsub_endpoint_queues_link);

    // row += String.format('<td>{0}</td>', last_pub_time);
    // row += String.format('<td>{0}</td>', last_seen);
    // row += String.format('<td>{0}</td>', last_deliv_time);

    if(data.is_internal) {
        row += '<td><span class="form_hint">Delete all subscriptions</span></td>';
    }
    else {
        row += String.format('<td>{0}</td>',
            String.format("<a href=\"javascript:$.fn.zato.pubsub.subscription.delete_('{0}')\">Delete all subscriptions</a>",
            data.id));
    }


    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.id);

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.on_delete_success = function(id) {
    var link = $('#pubsub_endpoint_queues_link_' + id);
    link.html(0);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.delete_ = function(id) {

    var on_delete_success = function() {
        $.fn.zato.pubsub.subscription.on_delete_success(id);
    }

    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Deleted subscriptions for endpoint `{0}`',
        'Are you sure you want to delete all subscriptions for endpoint `{0}`?',
        true, false, null, null, false, on_delete_success);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
