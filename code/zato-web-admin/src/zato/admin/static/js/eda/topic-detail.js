
/* EDA topic detail - per-topic sparklines for publishes, depth and
   subscribers, all backed by the broker's stats_window / stats_gauge
   series scoped to this topic. */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }
$.fn.zato.eda.topic_detail = {};

(function() {
    var detail = $.fn.zato.eda.topic_detail;
    var kit = $.fn.zato.dashboard_kit;

    var SPARK_BUFFER_SIZE = 60;
    var POLL_INTERVAL_MS = 10000;

    /* Match the EDA main dashboard's palette so a user moving between
       the overview and a topic detail does not see the colours change
       under them. Publishes is green (producer side); depth reuses
       the scheduler's tile blue since it's a gauge-style metric. */
    var COLOR_PUBLISHES = '#3aaf6b';
    var COLOR_DEPTH = '#82ccff';

    detail._topic_name = '';
    detail._buffers = {
        published: [],
        depth: []
    };

    var values_only = function(buf) {
        var out = [];
        for (var i = 0; i < buf.length; i++) out.push(buf[i].value);
        return out;
    };

    var seed_buffer_from_series = function(key, series) {
        if (!series || !series.length) return;
        var arr = [];
        for (var i = 0; i < series.length; i++) {
            arr.push({ts: series[i].ts * 1000, value: series[i].value});
        }
        detail._buffers[key] = arr.slice(-SPARK_BUFFER_SIZE);
    };

    var push_buffer = function(key, value) {
        var buf = detail._buffers[key];
        buf.push({ts: Date.now(), value: value});
        if (buf.length > SPARK_BUFFER_SIZE) buf.shift();
    };

    var format_local_time_seconds = function(ts_seconds) {
        if (!ts_seconds) return '\u2013';
        return kit.format_local_time(new Date(ts_seconds * 1000).toISOString());
    };

    var format_relative_past_seconds = function(ts_seconds) {
        if (!ts_seconds) return '\u2013';
        var diff = Math.floor(Date.now() / 1000 - ts_seconds);
        if (diff < 0) diff = 0;
        return kit.format_compact_duration(diff) + ' ago';
    };

    detail.render = function(data) {
        if (!data || !data.name) return;

        var total_published = data.total_published || 0;
        var depth = data.depth || 0;

        kit.set_number($('#stat-published'), total_published);
        kit.set_number($('#stat-depth'), depth);

        $('#stat-last-pub').text(format_local_time_seconds(data.last_pub_ts));

        /* Publishes sparkline - prefer the broker's per-topic counter
           series (a real publishes-per-minute history); fall back to
           local rolling samples of the cumulative total if the series
           hasn't appeared yet (cold start). */
        var history = data.history_timeline || {};
        if (history.publishes && history.publishes.length) {
            seed_buffer_from_series('published', history.publishes);
        } else {
            push_buffer('published', total_published);
        }

        if (history.depth && history.depth.length) {
            seed_buffer_from_series('depth', history.depth);
        } else {
            push_buffer('depth', depth);
        }

        kit.sparkline.render('#spark-published', values_only(detail._buffers.published), {
            color: COLOR_PUBLISHES,
            dot_color: COLOR_PUBLISHES,
            dot_style: 'filled_halo'
        });

        kit.sparkline.render('#spark-depth', values_only(detail._buffers.depth), {
            color: COLOR_DEPTH,
            dot_color: COLOR_DEPTH,
            dot_style: 'filled_halo'
        });

        var $qbody = $('#queues-body');
        $qbody.empty();
        var queues = data.queues || [];
        for (var qi = 0; qi < queues.length; qi++) {
            var q = queues[qi];
            var depth_html = kit.format_number_compact(q.pending_count || 0);
            var row = '<tr>';
            row += '<td><a href="/zato/eda/queue/' + encodeURIComponent(data.name) + '/'
                + encodeURIComponent(q.sub_key) + '/?cluster=1">' + q.sub_key + '</a></td>';
            row += '<td title="' + kit.format_number_full(q.pending_count || 0) + '">'
                + depth_html + '</td>';
            row += '</tr>';
            $qbody.append(row);
        }
        if (!queues.length) {
            $qbody.append('<tr><td colspan="2">No subscriber queues</td></tr>');
        }

        var $mbody = $('#messages-body');
        $mbody.empty();
        var messages = data.messages || [];
        for (var mi = 0; mi < messages.length; mi++) {
            var m = messages[mi];
            var detail_url = '/zato/eda/messages/' + encodeURIComponent(data.name) + '/'
                + encodeURIComponent(m.msg_id) + '/?cluster=1';
            var rel = format_relative_past_seconds(m.pub_time_ts);
            var mrow = '<tr>';
            mrow += '<td style="font-family:monospace; font-size:12px"><a href="' + detail_url + '">'
                + m.msg_id + '</a></td>';
            mrow += '<td class="data-preview">' + $('<span>').text(m.data_preview || '').html() + '</td>';
            mrow += '<td>' + (m.size || 0) + ' B</td>';
            mrow += '<td title="' + format_local_time_seconds(m.pub_time_ts) + '">' + rel + '</td>';
            mrow += '</tr>';
            $mbody.append(mrow);
        }
        if (!messages.length) {
            $mbody.append('<tr><td colspan="4">No messages</td></tr>');
        }

        if ($.fn.zato.eda.update_refresh_indicator) {
            $.fn.zato.eda.update_refresh_indicator();
        }
    };

    detail.poll = function() {
        $.ajax({
            url: '/zato/eda/topic/poll/',
            type: 'POST',
            data: {topic_name: detail._topic_name},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(data) {
                if (typeof data === 'string') {
                    try { data = JSON.parse(data); } catch (e) { return; }
                }
                detail.render(data);
            }
        });
    };

    detail.purge = function() {
        if (!confirm('Purge all messages from topic ' + detail._topic_name + '?')) return;
        $.ajax({
            url: '/zato/eda/topic/purge/',
            type: 'POST',
            data: {topic_name: detail._topic_name},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function() { detail.poll(); },
            error: function(xhr) {
                alert('Error: ' + (xhr.responseJSON ? xhr.responseJSON.error : 'Unknown error'));
            }
        });
    };

    detail.init = function(topic_name, initial_data) {
        detail._topic_name = topic_name;
        if (typeof initial_data === 'string') {
            try { initial_data = JSON.parse(initial_data); } catch (e) { initial_data = {}; }
        }

        $('.detail-tab').on('click', function() {
            var tab_name = $(this).data('tab');
            $('.detail-tab').removeClass('detail-tab-active').attr('aria-selected', 'false');
            $(this).addClass('detail-tab-active').attr('aria-selected', 'true');
            $('.detail-tab-panel').attr('hidden', true);
            $('#detail-tab-panel-' + tab_name).removeAttr('hidden');
        });

        detail.render(initial_data);
        setInterval(detail.poll, POLL_INTERVAL_MS);
    };
})();
