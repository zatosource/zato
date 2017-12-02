
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubSubscription = new Class({
    toString: function() {
        var s = '<PubSubSubscription id:{0} active_status:{1} sub_key:{2} name_slug:{3}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.active_status ? this.active_status : '(none)',
                                this.sub_key ? this.sub_key : '(none)',
                                this.name_slug ? this.name_slug : '(none)',
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

    var topic_link = String.format(
        '<a href="/zato/pubsub/topic/?cluster={0}&highlight={1}">{2}</a>', data.cluster_id, data.id, data.queue_name);

    var has_gd = data.has_gd ? 'Yes' : 'No';
    var is_staging_enabled = data.is_staging_enabled ? 'Yes' : 'No';

    var total_link = $.fn.zato.pubsub.endpoint_queue.get_depth_link(
        'total', data.cluster_id, data.id, data.name_slug, data.total_depth);

    var current_link = $.fn.zato.pubsub.endpoint_queue.get_depth_link(
        'current', data.cluster_id, data.id, data.name_slug, data.current_depth);

    var staging_link = $.fn.zato.pubsub.endpoint_queue.get_depth_link(
        'staging', data.cluster_id, data.id, data.name_slug, data.staging_depth);

    var sub_key_link = String.format(
        '<a id="sub_key_{0}" href="javascript:$.fn.zato.pubsub.endpoint_queue.toggle_sub_key(\'{0}\')">Show</a>', data.id);

    var last_interaction_link = '';

    if(data.last_interaction) {
        last_interaction_link = String.format(
            '<a href="/zato/pubsub/endpoint/queue/last-interaction/cluster/{0}/queue/{1}/{2}">{3}</a>',
            data.cluster_id, data.id, data.name_slug, data.staging_depth);
    }
    else {
        last_interaction = $.fn.zato.empty_value;
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', topic_link);
    row += String.format('<td>{0}</td>', data.active_status);

    row += String.format('<td>{0}</td>', has_gd);
    row += String.format('<td>{0}</td>', is_staging_enabled);

    row += String.format('<td>{0}</td>', total_link);
    row += String.format('<td>{0}</td>', current_link);
    row += String.format('<td>{0}</td>', staging_link);

    row += String.format('<td>{0}</td>', data.creation_time);
    row += String.format('<td>{0}</td>', sub_key_link);
    row += String.format('<td>{0}</td>', last_interaction);

    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.pubsub.endpoint_queue.clear('{0}')\">Clear</a>", data.id));
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.pubsub.endpoint_queue.edit('{0}')\">Edit</a>", data.id));
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.pubsub.endpoint_queue.delete_('{0}')\">Delete</a>", data.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.id);
    row += String.format("<td class='ignore'>{0}</td>", data.sub_key);
    row += String.format("<td class='ignore'>{0}</td>", data.has_gd);
    row += String.format("<td class='ignore'>{0}</td>", data.is_staging_enabled);
    row += String.format("<td class='ignore'>{0}</td>", data.name);
    row += String.format("<td class='ignore'>{0}</td>", data.name_slug);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.endpoint_queue.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update queue', id);
}

$.fn.zato.pubsub.endpoint_queue.get_depth_link = function(link_type, cluster_id, id, name_slug, depth) {
    return String.format(
        '<a href="/zato/pubsub/endpoint/queue/{0}/cluster/{1}/queue/{2}/{3}">{4}</a>',
        link_type, cluster_id, id, name_slug, depth);
}

$.fn.zato.pubsub.endpoint_queue.clear = function(id, cluster_id) {

    var instance = $.fn.zato.data_table.data[id];

    var http_callback = function(data, status) {
        var success = status == 'success';

        if(success) {

            var total_link = $.fn.zato.pubsub.endpoint_queue.get_depth_link(
                'total', cluster_id, instance.id, instance.name_slug, 0);

            var current_link = $.fn.zato.pubsub.endpoint_queue.get_depth_link(
                'current', cluster_id, instance.id, instance.name_slug, 0);

            var staging_link = $.fn.zato.pubsub.endpoint_queue.get_depth_link(
                'staging', cluster_id, instance.id, instance.name_slug, 0);

            $('#total_depth_' + instance.id).html(total_link);
            $('#current_depth_' + instance.id).html(current_link);
            $('#staging_depth_' + instance.id).html(staging_link);

        }

        $.fn.zato.user_message(success, data.responseText);
    }

    var jq_callback = function(ok) {
        if(ok) {
            var url = String.format('/zato/pubsub/endpoint/queue/clear/cluster/{0}/queue/{1}/', cluster_id, instance.id);
            $.fn.zato.post(url, http_callback, {'queue_name': instance.name}, 'text');
        }
    }

    var q = String.format('Are you sure you want to clear sub queue `{0}`?', instance.name);
    jConfirm(q, 'Please confirm', jq_callback);
}

$.fn.zato.pubsub.endpoint_queue.delete_ = function(id) {
    var instance = $.fn.zato.data_table.data[id];
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Queue `{0}` deleted',
        'Are you sure you want to delete sub queue `{0}`?',
        true, false,
        '/zato/pubsub/endpoint/queue/delete/{0}/' + instance.sub_key + '/');
}

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
