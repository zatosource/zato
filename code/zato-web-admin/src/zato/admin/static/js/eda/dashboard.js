
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }
$.fn.zato.eda.dashboard = {};

$.fn.zato.eda.dashboard._spark_data = {
    topics: [],
    messages: [],
    depth: [],
    subscribers: []
};

$.fn.zato.eda.dashboard._push_spark = function(key, value) {
    var arr = $.fn.zato.eda.dashboard._spark_data[key];
    arr.push(value);
    if (arr.length > 60) arr.shift();
};

$.fn.zato.eda.dashboard.render = function(data) {
    if (!data) return;

    var tc = data.topic_count || 0;
    var tm = data.total_messages || 0;
    var td = data.total_depth || 0;
    var tg = data.total_subscribers || 0;

    $('#stat-topics').text($.fn.zato.eda.format_number(tc));
    $('#stat-messages').text($.fn.zato.eda.format_number(tm));
    $('#stat-depth').text($.fn.zato.eda.format_number(td));
    $('#stat-subscribers').text($.fn.zato.eda.format_number(tg));

    $.fn.zato.eda.dashboard._push_spark('topics', tc);
    $.fn.zato.eda.dashboard._push_spark('messages', tm);
    $.fn.zato.eda.dashboard._push_spark('depth', td);
    $.fn.zato.eda.dashboard._push_spark('subscribers', tg);

    $.fn.zato.eda.sparkline('#spark-topics', $.fn.zato.eda.dashboard._spark_data.topics);
    $.fn.zato.eda.sparkline('#spark-messages', $.fn.zato.eda.dashboard._spark_data.messages);
    $.fn.zato.eda.sparkline('#spark-depth', $.fn.zato.eda.dashboard._spark_data.depth);
    $.fn.zato.eda.sparkline('#spark-subscribers', $.fn.zato.eda.dashboard._spark_data.subscribers);

    var $tbody = $('#topic-table-body');
    $tbody.empty();
    var topics = data.topics || [];

    topics.sort(function(a, b) {
        var a_ts = a.last_pub_ts || 0;
        var b_ts = b.last_pub_ts || 0;
        return b_ts - a_ts;
    });

    var max_topics = Math.min(topics.length, 20);
    for (var topic_idx = 0; topic_idx < max_topics; topic_idx++) {
        var topic = topics[topic_idx];
        var rel = $.fn.zato.eda.relative_time(topic.last_pub_ts);
        var row = '<tr>';
        row += '<td><a href="/zato/eda/topic/' + encodeURIComponent(topic.name) + '/?cluster=1">' + topic.name + '</a></td>';
        row += '<td>' + $.fn.zato.eda.depth_html(topic.depth || 0) + '</td>';
        var pub_count = topic.total_published || 0;
        if (pub_count > 0) {
            row += '<td><a href="/zato/eda/messages/?cluster=1&topic_name=' + encodeURIComponent(topic.name) + '">' + $.fn.zato.eda.format_number(pub_count) + '</a></td>';
        } else {
            row += '<td><span style="padding-left:1px">' + $.fn.zato.eda.format_number(pub_count) + '</span></td>';
        }
        if (topic.last_pub_ts && topic.last_pub_ts > 0) {
            row += '<td><a href="/zato/eda/messages/?cluster=1&topic_name=' + encodeURIComponent(topic.name) + '" title="' + $.fn.zato.eda.format_local_time(topic.last_pub_ts) + '">' + rel + '</a></td>';
        } else {
            row += '<td>-</td>';
        }
        var sub_count = topic.subscriber_count || 0;
        if (sub_count > 0) {
            row += '<td><a href="/zato/eda/topic/' + encodeURIComponent(topic.name) + '/?cluster=1">' + sub_count + '</a></td>';
        } else {
            row += '<td>0</td>';
        }
        row += '</tr>';
        $tbody.append(row);
    }
    if (topics.length === 0) {
        $tbody.append('<tr><td colspan="5">No topics</td></tr>');
    }

    var $qtbody = $('#queue-table-body');
    $qtbody.empty();
    var queues = data.queues || [];
    var max_queues = Math.min(queues.length, 20);
    for (var queue_idx = 0; queue_idx < max_queues; queue_idx++) {
        var queue = queues[queue_idx];
        var qrow = '<tr>';
        qrow += '<td><a href="/zato/eda/queue/' + encodeURIComponent(queue.topic_name) + '/' + encodeURIComponent(queue.sub_key) + '/?cluster=1">' + queue.sub_key + '</a></td>';
        qrow += '<td>' + $.fn.zato.eda.depth_html(queue.depth || 0) + '</td>';
        qrow += '<td><a href="/zato/eda/topic/' + encodeURIComponent(queue.topic_name) + '/?cluster=1">' + queue.topic_name + '</a></td>';
        qrow += '</tr>';
        $qtbody.append(qrow);
    }
    if (queues.length === 0) {
        $qtbody.append('<tr><td colspan="3">No subscriber queues</td></tr>');
    }

    $.fn.zato.eda.update_refresh_indicator();
};

$.fn.zato.eda.dashboard.poll = function() {
    $.ajax({
        url: '/zato/eda/dashboard/poll/',
        type: 'POST',
        data: {},
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            if (typeof data === 'string') { try { data = JSON.parse(data); } catch(e) { return; } }
            $.fn.zato.eda.dashboard.render(data);
        },
        error: function() {}
    });
};

$.fn.zato.eda.dashboard.init = function(initial_data) {
    if (typeof initial_data === 'string') { try { initial_data = JSON.parse(initial_data); } catch(e) { initial_data = {}; } }

    if (initial_data.sparkline_data) {
        var sd = initial_data.sparkline_data;
        if (sd.topics) { $.fn.zato.eda.dashboard._spark_data.topics = sd.topics.slice(); }
        if (sd.messages) { $.fn.zato.eda.dashboard._spark_data.messages = sd.messages.slice(); }
        if (sd.depth) { $.fn.zato.eda.dashboard._spark_data.depth = sd.depth.slice(); }
        if (sd.subscribers) { $.fn.zato.eda.dashboard._spark_data.subscribers = sd.subscribers.slice(); }
    }

    $.fn.zato.eda.dashboard.render(initial_data);
    setInterval($.fn.zato.eda.dashboard.poll, 10000);
};
