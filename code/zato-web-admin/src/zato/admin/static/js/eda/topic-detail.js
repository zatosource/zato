
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }
$.fn.zato.eda.topic_detail = {};

$.fn.zato.eda.topic_detail._topic_name = '';
$.fn.zato.eda.topic_detail._spark_published = [];
$.fn.zato.eda.topic_detail._spark_depth = [];

$.fn.zato.eda.topic_detail.render = function(data) {
    if (!data || !data.name) return;

    $('#topic-total-published').text($.fn.zato.eda.format_number(data.total_published || 0));
    $('#topic-depth').text($.fn.zato.eda.format_number(data.depth || 0));
    $('#stat-published').text($.fn.zato.eda.format_number(data.total_published || 0));
    $('#stat-depth').text($.fn.zato.eda.format_number(data.depth || 0));

    var rel = $.fn.zato.eda.relative_time(data.last_pub_ts);
    $('#topic-last-pub').text(rel);

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
    for (var i = 0; i < queues.length; i++) {
        var q = queues[i];
        var row = '<tr>';
        row += '<td><a href="/zato/eda/queue/' + encodeURIComponent(data.name) + '/' + encodeURIComponent(q.group_name) + '/?cluster=1">' + q.group_name + '</a></td>';
        row += '<td>' + $.fn.zato.eda.depth_html(q.pending_count || 0) + '</td>';
        row += '</tr>';
        $qbody.append(row);
    }
    if (queues.length === 0) {
        $qbody.append('<tr><td colspan="2">No subscriber queues</td></tr>');
    }

    var $mbody = $('#messages-body');
    $mbody.empty();
    var messages = data.messages || [];
    for (var j = 0; j < messages.length; j++) {
        var m = messages[j];
        var mrel = $.fn.zato.eda.relative_time(m.pub_time_ts);
        var mrow = '<tr>';
        mrow += '<td><a href="/zato/eda/messages/' + encodeURIComponent(data.name) + '/' + encodeURIComponent(m.msg_id) + '/?cluster=1">' + m.msg_id.substring(0, 15) + '...</a></td>';
        mrow += '<td class="data-preview">' + $('<span>').text(m.data_preview || '').html() + '</td>';
        mrow += '<td>' + (m.size || 0) + ' B</td>';
        mrow += '<td title="' + (m.pub_time_ts ? new Date(m.pub_time_ts * 1000).toISOString() : '') + '">' + mrel + '</td>';
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
            $.fn.zato.eda.topic_detail.render(data);
        },
        error: function() {}
    });
};

$.fn.zato.eda.topic_detail.show_publish_dialog = function() {
    $('#publish-dialog').dialog({
        modal: true,
        width: 500,
        buttons: {
            'Publish': function() {
                var topic = $('#publish-topic').val();
                var data = $('#publish-data').val();
                var priority = $('#publish-priority').val();
                $.ajax({
                    url: '/zato/eda/publish/submit/',
                    type: 'POST',
                    data: {topic_name: topic, data: data, priority: priority, expiration: 86400},
                    headers: {'X-CSRFToken': $.cookie('csrftoken')},
                    success: function() {
                        $('#publish-dialog').dialog('close');
                        $.fn.zato.eda.topic_detail.poll();
                    },
                    error: function(xhr) {
                        alert('Error: ' + (xhr.responseJSON ? xhr.responseJSON.error : 'Unknown error'));
                    }
                });
            },
            'Cancel': function() {
                $(this).dialog('close');
            }
        }
    });
};

$.fn.zato.eda.topic_detail.purge = function() {
    if (!confirm('Purge all messages from topic ' + $.fn.zato.eda.topic_detail._topic_name + '?')) return;
    $.ajax({
        url: '/zato/eda/topic/purge/',
        type: 'POST',
        data: {topic_name: $.fn.zato.eda.topic_detail._topic_name},
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            $.fn.zato.eda.topic_detail.poll();
        },
        error: function(xhr) {
            alert('Error: ' + (xhr.responseJSON ? xhr.responseJSON.error : 'Unknown error'));
        }
    });
};

$.fn.zato.eda.topic_detail.init = function(topic_name, initial_data) {
    $.fn.zato.eda.topic_detail._topic_name = topic_name;
    $.fn.zato.eda.topic_detail.render(initial_data);
    setInterval($.fn.zato.eda.topic_detail.poll, 10000);
};
