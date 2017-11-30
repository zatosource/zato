
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubEndpoint = new Class({
    toString: function() {
        var s = '<PubSubEndpoint id:{0} endpoint_name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.endpoint_name ? this.endpoint_name : '(none)'
                                );
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubEndpoint;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.subscription.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.before_submit_hook = $.fn.zato.pubsub.subscription.before_submit_hook;
    $.fn.zato.data_table.setup_forms([
        'endpoint_id',
        'active_status',
        'delivery_method',
        'delivery_batch_size',
        'delivery_max_retry',
        'wait_sock_err',
        'wait_non_sock_err',
    ]);
})

$.fn.zato.pubsub.subscription.before_submit_hook = function(form) {
    var form = $(form);

    var is_edit = form.attr('id').includes('edit');
    var prefix = is_edit ? 'edit-' : '';
    var endpoint_type = $('#id_' + prefix + 'endpoint_type').val();

    if(endpoint_type == 'rest' || endpoint_type == 'rest') {
        var delivery_method = $('#id_' + prefix + 'delivery_method').val();
    }

    if(endpoint_type == 'rest') {
        if(delivery_method == 'notify') {
            var out_rest_http_soap_id = $('#id_' + prefix + 'out_rest_http_soap_id');
            var rest_delivery_endpoint = $('#id_' + prefix + 'rest_delivery_endpoint');

            if(!out_rest_http_soap_id.val() && !rest_delivery_endpoint.val()) {
                form.data('bValidator').showMsg(out_rest_http_soap_id,
                    'Either REST outconn or REST callback are required if delivery method is Notify');
            return false;
            }
        }
    }

    if(endpoint_type == 'soap') {
        if(delivery_method == 'notify') {
            var out_soap_http_soap_id = $('#id_' + prefix + 'out_soap_http_soap_id');
            var rest_delivery_endpoint = $('#id_' + prefix + 'soap_delivery_endpoint');

            if(!out_rest_http_soap_id.val() && !soap_delivery_endpoint.val()) {
                form.data('bValidator').showMsg(out_soap_http_soap_id,
                    'Either SOAP outconn or SOAP callback are required if delivery method is Notify');
                return false;
            }
        }
    }

    return true;

}

$.fn.zato.pubsub.subscription.clear_forms = function() {
    // Hide everything ..
    $('tr[id^=endpoint_row_id_]').css('display', 'none');
    $('tr[id^=edit-endpoint_row_id_]').css('display', 'none');

    // .. except for WebSockets which we display by default.
    $('tr[id=endpoint_row_id_ws_channel_id]').css('display', 'table-row');
    $('tr[id=edit-endpoint_row_id_ws_channel_id]').css('display', 'table-row');
}

$.fn.zato.pubsub.subscription.create = function() {
    window.zato_run_dyn_form_handler();
    $.fn.zato.data_table._create_edit('create', 'Create new pub/sub subscriptions', null);
}

$.fn.zato.pubsub.subscription.edit = function(id) {
    window.zato_run_dyn_form_handler();
    $.fn.zato.data_table._create_edit('edit', 'Update pub/sub subscriptions', id);
}

$.fn.zato.pubsub.subscription.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var empty = '<span class="form_hint">---</span>';
    var topic_patterns_html = data.topic_patterns_html ? data.topic_patterns_html : empty;
    var client_html = data.client_html ? data.client_html : empty;

    // Update it with latest content dynamically obtained from the call to backend
    item.sub_key = data.sub_key;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', data.name);
    row += String.format('<td>{0}</td>', data.role);
    row += String.format('<td>{0}</td>', topic_patterns_html);
    row += String.format('<td>{0}</td>', client_html);
    row += String.format('<td>{0}</td>', data.endpoint_topics_html);
    row += String.format('<td>{0}</td>', data.endpoint_queues_html);
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.pubsub.subscription.edit('{0}')\">Edit</a>", data.id));
    row += String.format('<td>{0}</td>', data.delete_html);
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.id);
    row += String.format("<td class='ignore'>{0}</td>", data.is_internal);
    row += String.format("<td class='ignore'>{0}</td>", data.is_active);
    row += String.format("<td class='ignore'>{0}</td>", data.topic_patterns);
    row += String.format("<td class='ignore'>{0}</td>", data.security_id);
    row += String.format("<td class='ignore'>{0}</td>", data.ws_channel_id);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.subscription.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Pub/sub endpoint `{0}` deleted',
        'Are you sure you want to delete pub/sub endpoint `{0}`?',
        true);
}

$.fn.zato.pubsub.subscription.toggle_sub_key = function(id) {
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
