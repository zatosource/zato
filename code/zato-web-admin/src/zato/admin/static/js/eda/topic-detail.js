
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }
$.fn.zato.eda.topic_detail = {};

$.fn.zato.eda.topic_detail._topic_name = '';
$.fn.zato.eda.topic_detail._spark_published = [];
$.fn.zato.eda.topic_detail._spark_depth = [];

$.fn.zato.eda.topic_detail.render = function(data) {
    if (!data || !data.name) return;

    $('#stat-published').text($.fn.zato.eda.format_number(data.total_published || 0));
    $('#stat-depth').text($.fn.zato.eda.format_number(data.depth || 0));

    var last_pub_text = $.fn.zato.eda.format_local_time(data.last_pub_ts);
    $('#stat-last-pub').text(last_pub_text);

    var sp = $.fn.zato.eda.topic_detail._spark_published;
    sp.push(data.total_published || 0);
    if (sp.length > 60) sp.shift();
    $.fn.zato.eda.sparkline('#spark-published', sp);

    var sd = $.fn.zato.eda.topic_detail._spark_depth;
    sd.push(data.depth || 0);
    if (sd.length > 60) sd.shift();
    $.fn.zato.eda.sparkline('#spark-depth', sd);

    var $qbody = $('#queues-body');
    $qbody.empty();
    var queues = data.queues || [];
    for (var queue_idx = 0; queue_idx < queues.length; queue_idx++) {
        var queue = queues[queue_idx];
        var row = '<tr>';
        row += '<td><a href="/zato/eda/queue/' + encodeURIComponent(data.name) + '/' + encodeURIComponent(queue.sub_key) + '/?cluster=1">' + queue.sub_key + '</a></td>';
        row += '<td>' + $.fn.zato.eda.depth_html(queue.pending_count || 0) + '</td>';
        row += '</tr>';
        $qbody.append(row);
    }
    if (queues.length === 0) {
        $qbody.append('<tr><td colspan="2">No subscriber queues</td></tr>');
    }

    var $mbody = $('#messages-body');
    $mbody.empty();
    var messages = data.messages || [];
    for (var msg_idx = 0; msg_idx < messages.length; msg_idx++) {
        var msg = messages[msg_idx];
        var mrel = $.fn.zato.eda.relative_time(msg.pub_time_ts);
        var mrow = '<tr>';
        mrow += '<td style="font-family:monospace; font-size:12px"><a href="/zato/eda/messages/' + encodeURIComponent(data.name) + '/' + encodeURIComponent(msg.msg_id) + '/?cluster=1">' + msg.msg_id + '</a></td>';
        mrow += '<td class="data-preview">' + $('<span>').text(msg.data_preview || '').html() + '</td>';
        mrow += '<td>' + (msg.size || 0) + ' B</td>';
        mrow += '<td title="' + $.fn.zato.eda.format_local_time(msg.pub_time_ts) + '">' + mrel + '</td>';
        mrow += '</tr>';
        $mbody.append(mrow);
    }
    if (messages.length === 0) {
        $mbody.append('<tr><td colspan="4">No messages</td></tr>');
    }

    $.fn.zato.eda.update_refresh_indicator();
};

$.fn.zato.eda.topic_detail.poll = function() {
    $.ajax({
        url: '/zato/eda/topic/poll/',
        type: 'POST',
        data: {topic_name: $.fn.zato.eda.topic_detail._topic_name},
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            if (typeof data === 'string') { try { data = JSON.parse(data); } catch(e) { return; } }
            $.fn.zato.eda.topic_detail.render(data);
        },
        error: function() {}
    });
};

$.fn.zato.eda.topic_detail.purge = function() {
    if (!confirm('Purge all messages from topic ' + $.fn.zato.eda.topic_detail._topic_name + '?')) return;
    $.ajax({
        url: '/zato/eda/topic/purge/',
        type: 'POST',
        data: {topic_name: $.fn.zato.eda.topic_detail._topic_name},
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function() { $.fn.zato.eda.topic_detail.poll(); },
        error: function(xhr) { alert('Error: ' + (xhr.responseJSON ? xhr.responseJSON.error : 'Unknown error')); }
    });
};

$.fn.zato.eda.topic_detail.init = function(topic_name, initial_data) {
    $.fn.zato.eda.topic_detail._topic_name = topic_name;
    if (typeof initial_data === 'string') { try { initial_data = JSON.parse(initial_data); } catch(e) { initial_data = {}; } }
    $.fn.zato.eda.topic_detail.render(initial_data);
    setInterval($.fn.zato.eda.topic_detail.poll, 10000);
};
