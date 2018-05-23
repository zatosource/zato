
$.fn.zato.pubsub.delete_message = function(object_type, topic_id, msg_id, sub_key, has_gd, server_name, server_pid) {

    if(sub_key == null) {
        sub_key = '';
    }

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
            $.fn.zato.post(url, http_callback, {
                'object_type': object_type,
                'has_gd': has_gd,
                'sub_key': sub_key,
                'server_name': server_name,
                'server_pid': server_pid
            }, 'text');
        }
    }

    var q = String.format(
        'Are you sure you want to delete message `{0}`?<br/><center>Msg prefix `{1}`</center>', instance.id, instance.msg_prefix);
    jConfirm(q, 'Please confirm', jq_callback);
}
