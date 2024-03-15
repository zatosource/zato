
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubEndpoint = new Class({
    toString: function() {
        var s = '<PubSubEndpoint id:{0} name:{1} sub_key:{2} type:{3}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.sub_key ? this.sub_key : '(none)',
                                this.endpoint_type ? this.endpoint_type : '(none)',
                                );
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubEndpoint;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.endpoint.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'role']);

    // Maps values from selects to IDs of elements that should be made required
    const required_map = {
        "rest": ["#id_security_id",   "#id_edit-security_id"],
        "wsx":  ["#id_ws_channel_id", "#id_edit-ws_channel_id"],
        "srv":  ["#id_service_id",    "#id_edit-service_id"],
    }

    $("#id_endpoint_type").on("change", function() {
        $.fn.zato.toggle_tr_blocks(true, this.value, true);
        $.fn.zato.make_field_required_on_change(required_map, this.value);
    });

    $("#id_edit-endpoint_type").on("change", function() {
        $.fn.zato.toggle_tr_blocks(false, this.value, true);
        $.fn.zato.make_field_required_on_change(required_map, this.value);
    });

})

$.fn.zato.pubsub.endpoint.clear_forms = function() {
    // Hide everything ..
    $('tr[id^=endpoint_row_id_]').css('display', 'none');
    $('tr[id^=edit-endpoint_row_id_]').css('display', 'none');

    // .. except for WebSockets which we display by default.
    $('tr[id=endpoint_row_id_ws_channel_id]').css('display', 'table-row');
    $('tr[id=edit-endpoint_row_id_ws_channel_id]').css('display', 'table-row');
}

$.fn.zato.pubsub.endpoint.create = function() {
    $.fn.zato.pubsub.endpoint.clear_forms();
    $.fn.zato.data_table._create_edit('create', 'Create a new pub/sub endpoint', null);
}

$.fn.zato.pubsub.endpoint.edit = function(id) {
    $.fn.zato.pubsub.endpoint.clear_forms();
    var instance = $.fn.zato.data_table.data[id];
    $.fn.zato.toggle_tr_blocks(false, instance.endpoint_type, false);
    $.fn.zato.data_table._create_edit('edit', 'Update pub/sub endpoint', id);
}

$.fn.zato.pubsub.endpoint.data_table.new_row = function(item, data, include_tr) {
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
        String.format("<a href=\"javascript:$.fn.zato.pubsub.endpoint.edit('{0}')\">Edit</a>", data.id));
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

$.fn.zato.pubsub.endpoint.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Pub/sub endpoint `{0}` deleted',
        'Are you sure you want to delete the pub/sub endpoint `{0}`?',
        true);
}

$.fn.zato.pubsub.endpoint.toggle_sub_key = function(id) {
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
