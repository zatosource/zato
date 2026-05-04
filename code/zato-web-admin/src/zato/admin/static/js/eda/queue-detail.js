
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }
$.fn.zato.eda.queue_detail = {};

$.fn.zato.eda.queue_detail._topic_name = '';
$.fn.zato.eda.queue_detail._sub_key = '';
$.fn.zato.eda.queue_detail._spark_depth = [];

$.fn.zato.eda.queue_detail.render = function(data) {
    if (!data) return;

    var depth = data.depth || 0;
    $('#stat-depth').text($.fn.zato.eda.format_number(depth));

    var sd = $.fn.zato.eda.queue_detail._spark_depth;
    sd.push(depth);
    if (sd.length > 60) sd.shift();
    $.fn.zato.eda.sparkline('#spark-depth', sd);

    var $mbody = $('#messages-body');
    $mbody.empty();
    var messages = data.messages || [];
    for (var msg_idx = 0; msg_idx < messages.length; msg_idx++) {
        var msg = messages[msg_idx];
        var rel = $.fn.zato.eda.relative_time(msg.pub_time_ts);
        var row = '<tr>';
        row += '<td style="font-family:monospace; font-size:12px"><a href="/zato/eda/messages/' + encodeURIComponent($.fn.zato.eda.queue_detail._topic_name) + '/' + encodeURIComponent(msg.msg_id) + '/?cluster=1">' + msg.msg_id + '</a></td>';
        row += '<td class="data-preview">' + $('<span>').text(msg.data_preview || '').html() + '</td>';
        row += '<td>' + (msg.size || 0) + ' B</td>';
        row += '<td title="' + $.fn.zato.eda.format_local_time(msg.pub_time_ts) + '">' + rel + '</td>';
        row += '</tr>';
        $mbody.append(row);
    }
    if (messages.length === 0) {
        var label = $.fn.zato.eda.pluralize(0, 'message');
        $mbody.append('<tr><td colspan="4">No pending ' + label + '</td></tr>');
    }

    $.fn.zato.eda.update_refresh_indicator();
};

$.fn.zato.eda.queue_detail.poll = function() {
    $.ajax({
        url: '/zato/eda/queue/poll/',
        type: 'POST',
        data: {
            topic_name: $.fn.zato.eda.queue_detail._topic_name,
            sub_key: $.fn.zato.eda.queue_detail._sub_key
        },
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            if (typeof data === 'string') { try { data = JSON.parse(data); } catch(e) { return; } }
            $.fn.zato.eda.queue_detail.render(data);
        },
        error: function() {}
    });
};

$.fn.zato.eda.queue_detail.purge = function() {
    if (!confirm('Purge all pending messages from this queue?')) return;
    $.ajax({
        url: '/zato/eda/queue/purge/',
        type: 'POST',
        data: {
            topic_name: $.fn.zato.eda.queue_detail._topic_name,
            sub_key: $.fn.zato.eda.queue_detail._sub_key
        },
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function() { $.fn.zato.eda.queue_detail.poll(); },
        error: function(xhr) { alert('Error: ' + (xhr.responseJSON ? xhr.responseJSON.error : 'Unknown error')); }
    });
};

$.fn.zato.eda.queue_detail.init = function(topic_name, sub_key, initial_data) {
    $.fn.zato.eda.queue_detail._topic_name = topic_name;
    $.fn.zato.eda.queue_detail._sub_key = sub_key;
    if (typeof initial_data === 'string') { try { initial_data = JSON.parse(initial_data); } catch(e) { initial_data = {}; } }
    $.fn.zato.eda.queue_detail.render(initial_data);
    setInterval($.fn.zato.eda.queue_detail.poll, 10000);
};
