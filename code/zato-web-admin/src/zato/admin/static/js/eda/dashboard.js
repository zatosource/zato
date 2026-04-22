
/* EDA dashboard - thin adapter on top of the dashboard kit.
   Mirrors scheduler/dashboard.js's structure but with EDA-specific
   data shapes:
     - top tiles: Topics, Subscribers, Depth (gauges) and Publishes
       (per-minute counter from broker stats_window).
     - main chart: aggregate publishes/min summed across topics.
     - tabs: Queues + Recent messages.

   All time-series come pre-bucketed from the broker; this file only
   reshapes them for the kit's renderers and pushes the latest gauge
   values into rolling sparkline buffers. */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }
$.fn.zato.eda.dashboard = {};

(function() {
    var dash = $.fn.zato.eda.dashboard;
    var kit = $.fn.zato.dashboard_kit;

    dash.theme = {
        name: 'EDA',
        spark_color:  '#82ccff',
        spark_err:    '#ff6b6b',
        pill_bg:        '#1a6fa0',
        pill_color:     '#e0f0ff',
        pill_link_bg:   '#0f4a6e',
        pill_link_color: '#c0e2f5',
        pill_links: []
    };

    var PUBLISH_GREEN = '#3aaf6b';
    var DELIVERY_BLUE = '#3aa0e3';
    var PALETTE = {
        'topics':      dash.theme.spark_color,
        'subscribers': dash.theme.spark_color,
        'depth':       dash.theme.spark_color,
        'publishes':   PUBLISH_GREEN,
        'deliveries':  DELIVERY_BLUE
    };

    var SPARK_BUFFER_SIZE = 60;
    var POLL_INTERVAL_MS = 10000;
    var RECENT_MESSAGES_LIMIT = 25;

    /* Rolling buffers used by the top-tile sparklines. Each entry is
       {ts: ms, value: n}; the buffer is capped to SPARK_BUFFER_SIZE
       points and overwritten on each poll. */
    dash._buffers = {
        topics: [],
        subscribers: [],
        depth: [],
        publishes: [],
        deliveries: []
    };

    var stat_tile_handle = null;
    var main_chart_handle = null;
    var tabs_handle = null;

    var push_buffer = function(key, value) {
        var buf = dash._buffers[key];
        var now = Date.now();
        buf.push({ts: now, value: value});
        if (buf.length > SPARK_BUFFER_SIZE) buf.shift();
    };

    var seed_buffer_from_series = function(key, series) {
        if (!series || !series.length) return;
        var arr = [];
        for (var i = 0; i < series.length; i++) {
            arr.push({ts: series[i].ts * 1000, value: series[i].value});
        }
        dash._buffers[key] = arr.slice(-SPARK_BUFFER_SIZE);
    };

    var values_only = function(buf) {
        var out = [];
        for (var i = 0; i < buf.length; i++) out.push(buf[i].value);
        return out;
    };

    var sum_series = function(series) {
        var total = 0;
        if (!series) return 0;
        for (var i = 0; i < series.length; i++) {
            total += series[i].count;
        }
        return total;
    };

    /* Expand multiple per-topic counter series into a flat record list
       the main chart's bucket-by-key logic can render. Each input
       entry is `{ts, count}`; we replicate it `count` times so the
       chart's "events per bucket" math produces the right value. */
    /* Broker delivers per-minute counts: `[{ts, count}, ...]`. The
       main chart aggregates flat event lists, so we expand each bucket
       into `count` discrete events. To avoid every event landing on
       the bucket-start timestamp (which would produce a single
       vertical spike per minute on the chart, separated by flat
       zero-runs), we spread the events uniformly across the 60-second
       bucket window. This turns the visual into a continuous line
       that matches the rate the publishers / consumers actually
       sustained inside that minute. */
    var BROKER_BUCKET_MS = 60000;
    var build_chart_timeline = function(series_by_key) {
        var out = [];
        for (var key in series_by_key) {
            if (!series_by_key.hasOwnProperty(key)) continue;
            var series = series_by_key[key] || [];
            var per_bucket = {};
            for (var i = 0; i < series.length; i++) {
                var ts = series[i].ts;
                per_bucket[ts] = (per_bucket[ts] || 0) + series[i].count;
            }
            var now_ms = Date.now();
            for (var bk in per_bucket) {
                if (!per_bucket.hasOwnProperty(bk)) continue;
                var bucket_start_ms = parseInt(bk, 10) * 1000;
                var n = per_bucket[bk];
                if (n <= 0) continue;
                /* For the in-progress bucket, the events we've seen so
                   far cover only the time elapsed inside it. Anything
                   beyond `now` would be a phantom future event. */
                var bucket_end_ms = Math.min(
                    bucket_start_ms + BROKER_BUCKET_MS, now_ms,
                );
                var span = Math.max(1, bucket_end_ms - bucket_start_ms);
                var step = span / n;
                for (var j = 0; j < n; j++) {
                    out.push({
                        ts: bucket_start_ms + Math.floor(step * (j + 0.5)),
                        series: key,
                    });
                }
            }
        }
        return out;
    };

    /* Build the per-minute counter buffer for a tile's sparkline.
       Sums the input series across all topics by ts, then writes the
       resulting {ts_ms, value} list (capped to the rolling window) to
       the dashboard's buffer for `buffer_key`. */
    var rebuild_counter_buffer = function(buffer_key, series) {
        var per_bucket = {};
        if (series) {
            for (var i = 0; i < series.length; i++) {
                var ts = series[i].ts;
                per_bucket[ts] = (per_bucket[ts] || 0) + series[i].count;
            }
        }
        var keys = [];
        for (var k in per_bucket) {
            if (per_bucket.hasOwnProperty(k)) keys.push(parseInt(k, 10));
        }
        keys.sort(function(a, b) { return a - b; });
        var arr = [];
        for (var ki = 0; ki < keys.length; ki++) {
            arr.push({ts: keys[ki] * 1000, value: per_bucket[keys[ki]]});
        }
        dash._buffers[buffer_key] = arr.slice(-SPARK_BUFFER_SIZE);
    };

    /* Render a sparkline for a given tile from its rolling buffer. */
    var render_spark = function(selector, key, color) {
        var values = values_only(dash._buffers[key]);
        kit.sparkline.render(selector, values, {
            color: color,
            dot_color: color,
            dot_style: 'filled_halo',
            stroke_width: 1.6,
            min_points: 2
        });
    };

    var format_size = function(n) {
        if (n === undefined || n === null) return '\u2013';
        if (n < 1024) return n + ' B';
        if (n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB';
        return (n / (1024 * 1024)).toFixed(2) + ' MB';
    };

    var format_message_time = function(ts_seconds) {
        if (!ts_seconds) return '\u2013';
        var d = new Date(ts_seconds * 1000);
        return ('0' + d.getHours()).slice(-2) + ':' +
               ('0' + d.getMinutes()).slice(-2) + ':' +
               ('0' + d.getSeconds()).slice(-2);
    };

    /* Local helpers around Unix-epoch-seconds. The kit's
       relative_time_past/format_local_time both expect ISO strings
       and the broker hands us numbers, so we convert here rather
       than complicating the kit's API. */
    var format_relative_past_seconds = function(ts_seconds) {
        if (!ts_seconds) return '\u2013';
        var diff = Math.floor(Date.now() / 1000 - ts_seconds);
        if (diff < 0) diff = 0;
        return kit.format_compact_duration(diff) + ' ago';
    };

    var format_local_time_seconds = function(ts_seconds) {
        if (!ts_seconds) return '';
        return kit.format_local_time(new Date(ts_seconds * 1000).toISOString());
    };

    dash.render = function(data) {
        if (!data) return;
        var history = data.history_timeline || {};
        var publishes = history.publishes || [];
        var deliveries = history.deliveries || [];

        /* Top tiles. Topics/Subscribers/Depth are point-in-time gauges
           (server-walked from disk). The Publishes / Deliveries tiles
           mirror the scheduler's "Runs in last hour" semantic: the
           headline is the sum across all buckets in the rolling
           window, the sublabel is the lifetime total. We use
           total_messages (on-disk count) as the publishes sublabel
           because it persists across broker restarts; deliveries have
           no equivalent on-disk counter so we fall back to the same
           rolling-window sum for both numbers. */
        var topics_count = data.topic_count || 0;
        var subs_count = data.total_subscribers || 0;
        var depth_total = data.total_depth || 0;
        var publishes_last_hour = sum_series(publishes);
        var deliveries_last_hour = sum_series(deliveries);
        var publishes_total = data.total_messages || publishes_last_hour;
        var deliveries_total = deliveries_last_hour;

        kit.set_number($('#stat-topics'), topics_count);
        kit.set_number($('#stat-subscribers'), subs_count);
        kit.set_number($('#stat-depth'), depth_total);
        kit.set_number($('#stat-publishes'), publishes_last_hour);
        kit.set_number($('#stat-deliveries'), deliveries_last_hour);

        $('#stat-publishes-sublabel').text(
            kit.format_number_compact(publishes_total) + ' total'
        ).attr('title', kit.format_number_full(publishes_total) + ' total');
        $('#stat-deliveries-sublabel').text(
            kit.format_number_compact(deliveries_total) + ' total'
        ).attr('title', kit.format_number_full(deliveries_total) + ' total');

        /* Buffers behind the sparklines. The three gauges come from
           the server-side rolling samples; if the server hasn't
           shipped a series yet we fall back to local push so the
           sparkline still moves between polls. */
        if (history.topics_count && history.topics_count.length) {
            seed_buffer_from_series('topics', history.topics_count);
        } else {
            push_buffer('topics', topics_count);
        }
        if (history.subscribers_count && history.subscribers_count.length) {
            seed_buffer_from_series('subscribers', history.subscribers_count);
        } else {
            push_buffer('subscribers', subs_count);
        }
        if (history.depth_total && history.depth_total.length) {
            seed_buffer_from_series('depth', history.depth_total);
        } else {
            push_buffer('depth', depth_total);
        }
        rebuild_counter_buffer('publishes', publishes);
        rebuild_counter_buffer('deliveries', deliveries);

        render_spark('#spark-topics',      'topics',      PALETTE.topics);
        render_spark('#spark-subscribers', 'subscribers', PALETTE.subscribers);
        render_spark('#spark-depth',       'depth',       PALETTE.depth);
        render_spark('#spark-publishes',   'publishes',   PALETTE.publishes);
        render_spark('#spark-deliveries',  'deliveries',  PALETTE.deliveries);

        if (stat_tile_handle) stat_tile_handle.bind();

        /* Main chart - publishes (green) + deliveries (blue) overlaid. */
        if (main_chart_handle) {
            main_chart_handle.render(build_chart_timeline({
                publishes:  publishes,
                deliveries: deliveries
            }));
        }

        render_topics_table(data.topics || []);
        render_queues_table(data.queues || []);
    };

    var render_topics_table = function(topics) {
        var $body = $('#dashboard-topic-table-body');
        $body.empty();
        topics.sort(function(a, b) {
            return (b.last_pub_ts || 0) - (a.last_pub_ts || 0);
        });
        $('#dashboard-topics-count').text(
            topics.length === 1 ? '1 topic' : kit.format_number_compact(topics.length) + ' topics'
        );
        if (!topics.length) {
            $body.append('<tr><td colspan="6" class="dashboard-table-empty">No topics yet</td></tr>');
            return;
        }
        var max_topics = Math.min(topics.length, 50);
        for (var i = 0; i < max_topics; i++) {
            var t = topics[i];
            var dot = '<span class="dashboard-status-dot" style="background:' + PALETTE.publishes + '"></span>';
            var depth_html = kit.format_number_compact(t.depth || 0);
            var pub_html = kit.format_number_compact(t.total_published || 0);
            var sub_count = t.subscriber_count || 0;
            var last_pub = t.last_pub_ts && t.last_pub_ts > 0
                ? '<span title="' + format_local_time_seconds(t.last_pub_ts) + '">'
                    + format_relative_past_seconds(t.last_pub_ts) + '</span>'
                : '\u2013';

            var row = '<tr>';
            row += '<td>' + dot + '</td>';
            row += '<td><a href="/zato/eda/topic/' + encodeURIComponent(t.name)
                + '/?cluster=1">' + t.name + '</a></td>';
            row += '<td title="' + kit.format_number_full(t.depth || 0) + '">' + depth_html + '</td>';
            if ((t.total_published || 0) > 0) {
                row += '<td><a href="/zato/eda/messages/?cluster=1&topic_name='
                    + encodeURIComponent(t.name) + '" title="'
                    + kit.format_number_full(t.total_published) + '">' + pub_html + '</a></td>';
            } else {
                row += '<td>0</td>';
            }
            row += '<td>' + last_pub + '</td>';
            if (sub_count > 0) {
                row += '<td><a href="/zato/eda/topic/' + encodeURIComponent(t.name)
                    + '/?cluster=1">' + sub_count + '</a></td>';
            } else {
                row += '<td>0</td>';
            }
            row += '</tr>';
            $body.append(row);
        }
    };

    var render_queues_table = function(queues) {
        var $body = $('#dashboard-queue-table-body');
        $body.empty();
        $('#dashboard-queues-count').text(
            queues.length === 1 ? '1 queue' : kit.format_number_compact(queues.length) + ' queues'
        );
        if (!queues.length) {
            $body.append('<tr><td colspan="3" class="dashboard-table-empty">No subscriber queues</td></tr>');
            return;
        }
        var max_queues = Math.min(queues.length, 50);
        for (var i = 0; i < max_queues; i++) {
            var q = queues[i];
            var depth = q.depth || 0;
            var row = '<tr>';
            row += '<td><a href="/zato/eda/queue/' + encodeURIComponent(q.topic_name) + '/'
                + encodeURIComponent(q.sub_key) + '/?cluster=1">' + q.sub_key + '</a></td>';
            row += '<td><a href="/zato/eda/topic/' + encodeURIComponent(q.topic_name)
                + '/?cluster=1">' + q.topic_name + '</a></td>';
            row += '<td title="' + kit.format_number_full(depth) + '">'
                + kit.format_number_compact(depth) + '</td>';
            row += '</tr>';
            $body.append(row);
        }
    };

    var render_recent_messages = function(messages) {
        var $body = $('#dashboard-messages-table-body');
        $body.empty();
        $('#dashboard-messages-count').text(
            messages.length === 1 ? '1 message' : kit.format_number_compact(messages.length) + ' messages'
        );
        if (!messages.length) {
            $body.append('<tr><td colspan="4" class="dashboard-table-empty">No messages yet</td></tr>');
            return;
        }
        for (var i = 0; i < messages.length; i++) {
            var m = messages[i];
            var detail_url = '/zato/eda/message/' + encodeURIComponent(m.topic_name)
                + '/' + encodeURIComponent(m.msg_id) + '/?cluster=1';
            var topic_url = '/zato/eda/topic/' + encodeURIComponent(m.topic_name) + '/?cluster=1';
            var time_label = format_message_time(m.pub_time_ts);
            var row = '<tr>';
            row += '<td><span title="' + format_local_time_seconds(m.pub_time_ts) + '">'
                + time_label + '</span></td>';
            row += '<td><a href="' + topic_url + '">' + m.topic_name + '</a></td>';
            row += '<td><a href="' + detail_url + '"><code>' + m.msg_id + '</code></a></td>';
            row += '<td title="' + kit.format_number_full(m.size) + ' B">'
                + format_size(m.size) + '</td>';
            row += '</tr>';
            $body.append(row);
        }
    };

    var poll_recent_messages = function() {
        $.ajax({
            url: '/zato/eda/dashboard/recent-messages/',
            type: 'POST',
            data: {limit: RECENT_MESSAGES_LIMIT},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(data) {
                if (typeof data === 'string') {
                    try { data = JSON.parse(data); } catch (e) { return; }
                }
                render_recent_messages(data.messages || []);
            }
        });
    };

    dash.poll = function() {
        $.ajax({
            url: '/zato/eda/dashboard/poll/',
            type: 'POST',
            data: {},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(data) {
                if (typeof data === 'string') {
                    try { data = JSON.parse(data); } catch (e) { return; }
                }
                dash.render(data);
            }
        });
        if (tabs_handle && tabs_handle.get_tab() === 'messages') {
            poll_recent_messages();
        }
    };

    dash.init = function(initial_data) {
        if (typeof initial_data === 'string') {
            try { initial_data = JSON.parse(initial_data); } catch (e) { initial_data = {}; }
        }

        stat_tile_handle = kit.stat_tile.init({
            tile_container: 'dashboard-tile',
            tiles: [
                {sparkline_selector: '#spark-topics',      buffer_key: 'topics',
                 label: 'Topics',      color: PALETTE.topics},
                {sparkline_selector: '#spark-subscribers', buffer_key: 'subscribers',
                 label: 'Subscribers', color: PALETTE.subscribers},
                {sparkline_selector: '#spark-depth',       buffer_key: 'depth',
                 label: 'Queue depth', color: PALETTE.depth},
                {sparkline_selector: '#spark-publishes',   buffer_key: 'publishes',
                 label: 'Publishes',   color: PALETTE.publishes},
                {sparkline_selector: '#spark-deliveries',  buffer_key: 'deliveries',
                 label: 'Deliveries',  color: PALETTE.deliveries}
            ],
            get_buffer: function(key) {
                return dash._buffers[key];
            }
        });

        main_chart_handle = kit.main_chart.init({
            container: '#dashboard-bar-chart',
            legend: '#dashboard-chart-legend',
            count_pill: '#dashboard-exec-count',
            chart_type_toggle: '#dashboard-chart-type-toggle',
            tooltip_id: 'dashboard-chart-tooltip',
            series_keys: ['publishes', 'deliveries'],
            palette: PALETTE,
            labels: {publishes: 'Publishes', deliveries: 'Deliveries'},
            item_noun_singular: 'event',
            item_noun_plural: 'events',
            range_names: {
                5: 'Last 5 minutes', 15: 'Last 15 minutes', 30: 'Last 30 minutes',
                60: 'Last 1 hour'
            },
            bucket_ts: function(record) { return record.ts; },
            series_key: function(record) { return record.series; },
            hidden_storage_key: 'eda.dashboard.legend.hidden',
            bars_storage_key: 'eda.dashboard.show_bars'
        });
        main_chart_handle.set_time_range_minutes(60);

        kit.time_range.init({
            menu: '#dashboard-time-range-menu',
            pill: '#dashboard-exec-count',
            active_cls: 'dashboard-time-range-active',
            storage_key: 'eda.dashboard.time_range_minutes',
            on_change: function(minutes) {
                main_chart_handle.set_time_range_minutes(minutes);
                main_chart_handle.redraw();
            }
        });

        tabs_handle = kit.tabs.init({
            tab_selector: '.dashboard-tabs .dashboard-tab',
            panel_prefix: 'dashboard-tab-panel-',
            storage_key: 'eda.dashboard.active_tab',
            default_tab: 'queues',
            on_change: function(name) {
                if (name === 'messages') poll_recent_messages();
            }
        });

        dash.render(initial_data);
        $('.dashboard-page').css('opacity', '1');

        setInterval(dash.poll, POLL_INTERVAL_MS);
        if (tabs_handle.get_tab() === 'messages') {
            poll_recent_messages();
        }
    };
})();
