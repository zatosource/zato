
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Consumer = new Class({
    toString: function() {
        var s = '<Consumer id:{0} is_active:{1}>';
        return String.format(
            s,
            this.id ? this.id : '(none)',
            this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Consumer;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.consumers.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['client_id', 'delivery_mode', 'max_depth']);
})

$.fn.zato.pubsub.consumers.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new consumer', null);
}

$.fn.zato.pubsub.consumers.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the consumer', id);
}

$.fn.zato.pubsub.consumers.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    $.fn.zato.data_table.data[data.id].name = data.name;
    $.fn.zato.data_table.data[data.id].is_active = data.is_active == true;

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", data.id);
    }

    var is_active = data.is_active == true;

    var last_seen = data.last_seen ? data.last_seen : "(Never)";
    var last_seen_css_class = data.last_seen ? "" : "form_hint";

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', data.topic_name);
    row += String.format('<td>{0}</td>', data.name);
    row += String.format('<td>{0}</td>', data.sub_key);
    row += String.format('<td>{0}</td>', is_active ? "Yes": "No");
    row += String.format('<td>{0}</td>', item.delivery_mode);
    row += String.format('<td>{0}</td>', data.current_depth);
    row += String.format('<td>{0}</td>', data.in_flight_depth ? data.in_flight_depth : "0");
    row += String.format('<td>{0}</td>', item.max_depth);
    row += String.format('<td><span class="{0}">{1}</span></td>', last_seen_css_class, last_seen);

    row += String.format('<td>{0}</td>', String.format(
        "<a href=\"javascript:$.fn.zato.pubsub.consumers.clear('{0}', 'message', '{1}', '{2}')\">Clear msg queue</a>",
        data.client_id, data.sub_key, data.topic_name));

    row += String.format('<td>{0}</td>', String.format(
        "<a href=\"javascript:$.fn.zato.pubsub.consumers.clear('{0}', 'in-flight', '{1}', '{2}')\">Clear in-flight</a>",
        data.client_id, data.sub_key, data.topic_name));

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.pubsub.consumers.edit('{0}')\">Edit</a>", data.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.pubsub.consumers.delete_('{0}')\">Delete</a>", data.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", data.callback);
    row += String.format("<td class='ignore'>{0}</td>", data.client_id);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.consumers.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Consumer [{0}] deleted',
        'Are you sure you want to delete the consumer [{0}]?',
        true, false, '/zato/pubsub/consumers/delete/{0}/');
}

$.fn.zato.pubsub.consumers.clear = function(client_id, type, sub_key, topic_name) {

    var cluster_id = $('#cluster_id').val();

    var on_post_callback_done = function(success) {
        if(success) {
            var cell = null;
            if(type == 'in-flight') {
                cell = $('#in_flight_depth_' + sub_key)
                cell.text('0');
            }
            else {
                cell = $('#current_depth_' + sub_key)
                cell.html(String.format(
                    '<a href="/zato/pubsub/message/cluster/{0}/consumer-queue/{1}/{2}">0</a>', cluster_id, sub_key, topic_name));
            }
        }
    }

    var callback = function(ok) {
        if(ok) {
            $.fn.zato.post_with_user_message(
                String.format('/zato/pubsub/consumers/clear/{0}/{1}/cluster/{2}/', type, client_id, cluster_id),
                on_post_callback_done)
        }
    }

    jConfirm(String.format('Are you sure you want to clear the {0} queue<br/>for `{1}`?', type, sub_key), 'Please confirm', callback);
}
