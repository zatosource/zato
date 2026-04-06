
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }
$.fn.zato.eda.dashboard = {};

$.fn.zato.eda.dashboard._spark_data = {
    topics: [],
    messages: [],
    depth: [],
    groups: []
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
    var tg = data.total_groups || 0;

    $('#stat-topics').text($.fn.zato.eda.format_number(tc));
    $('#stat-messages').text($.fn.zato.eda.format_number(tm));
    $('#stat-depth').text($.fn.zato.eda.format_number(td));
    $('#stat-groups').text($.fn.zato.eda.format_number(tg));

    $.fn.zato.eda.dashboard._push_spark('topics', tc);
    $.fn.zato.eda.dashboard._push_spark('messages', tm);
    $.fn.zato.eda.dashboard._push_spark('depth', td);
    $.fn.zato.eda.dashboard._push_spark('groups', tg);

    $.fn.zato.eda.sparkline('#spark-topics', $.fn.zato.eda.dashboard._spark_data.topics);
    $.fn.zato.eda.sparkline('#spark-messages', $.fn.zato.eda.dashboard._spark_data.messages);
    $.fn.zato.eda.sparkline('#spark-depth', $.fn.zato.eda.dashboard._spark_data.depth);
    $.fn.zato.eda.sparkline('#spark-groups', $.fn.zato.eda.dashboard._spark_data.groups);

    var $tbody = $('#topic-table-body');
    $tbody.empty();
    var topics = data.topics || [];
    var max_topics = Math.min(topics.length, 20);
    for (var i = 0; i < max_topics; i++) {
        var t = topics[i];
        var rel = $.fn.zato.eda.relative_time(t.last_pub_ts);
        var row = '<tr>';
        row += '<td><a href="/zato/eda/topic/' + encodeURIComponent(t.name) + '/?cluster=1">' + t.name + '</a></td>';
        row += '<td>' + $.fn.zato.eda.depth_html(t.depth || 0) + '</td>';
        row += '<td>' + $.fn.zato.eda.format_number(t.total_published || 0) + '</td>';
        row += '<td title="' + (t.last_pub_ts ? new Date(t.last_pub_ts * 1000).toISOString() : '') + '">' + rel + '</td>';
        row += '<td>' + (t.subscriber_count || 0) + '</td>';
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
    for (var j = 0; j < max_queues; j++) {
        var q = queues[j];
        var qrow = '<tr>';
        qrow += '<td><a href="/zato/eda/queue/' + encodeURIComponent(q.stream_name) + '/' + encodeURIComponent(q.group_name) + '/?cluster=1">' + q.group_name + '</a></td>';
        qrow += '<td>' + $.fn.zato.eda.depth_html(q.depth || 0) + '</td>';
        qrow += '<td>' + q.stream_name + '</td>';
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
            $.fn.zato.eda.dashboard.render(data);
        },
        error: function() {}
    });
};

$.fn.zato.eda.dashboard.init = function(initial_data) {
    $.fn.zato.eda.dashboard.render(initial_data);
    setInterval($.fn.zato.eda.dashboard.poll, 10000);
};
