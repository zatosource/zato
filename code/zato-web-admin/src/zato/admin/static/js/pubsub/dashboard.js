
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.pubsub === 'undefined') { $.fn.zato.pubsub = {}; }
$.fn.zato.pubsub.dashboard = {};

$.fn.zato.pubsub.dashboard.config = {
    cluster_id: '1',
    base_url: '/zato/pubsub/dashboard/',
    default_time_range: 0
};

// ////////////////////////////////////////////////////////////////////////////
// Theme
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.dashboard.theme = {
    name: 'Pub/sub',
    accent:       '#4db8a0',
    accent_light: '#8fd4c4',
    accent_dark:  '#2a7a68',
    spark_color:  '#4db8a0',
    spark_warn:   '#e6a817',
    spark_err:    '#ff6b6b',
    pill_bg:        '#1a6e5e',
    pill_color:     '#e0f5f0',
    pill_link_bg:   '#0f4a3e',
    pill_link_color: '#c0e8df',
    pill_links: [],
    row_recency_color: '77, 184, 160'
};

// ////////////////////////////////////////////////////////////////////////////
// Series palette
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.dashboard.series_colors = {
    'published': '#4db8a0',
    'delivered': '#2a7a68'
};

$.fn.zato.pubsub.dashboard.series_labels = {
    'published': 'Published',
    'delivered': 'Delivered'
};

// ////////////////////////////////////////////////////////////////////////////
// Kit aliases
// ////////////////////////////////////////////////////////////////////////////

(function() {
    var kit = $.fn.zato.dashboard_kit;
    var dash = $.fn.zato.pubsub.dashboard;

    dash._spark_buffers = kit.spark.create({
        keys: ['topics', 'subscribers', 'depth', 'oldest_unacked'],
        window_ms: 60 * 60 * 1000,
        bucket_count: 60
    });

    // ////////////////////////////////////////////////////////////////////////
    // Render
    // ////////////////////////////////////////////////////////////////////////

    dash.render = function(data) {

        var topic_count = data.topic_count;
        var total_subscribers = data.total_subscribers;
        var total_depth = data.total_depth;
        var oldest_unacked = data.oldest_unacked_age_seconds;

        kit.set_number($('#stat-topics'), topic_count);
        kit.set_number($('#stat-subscribers'), total_subscribers);
        kit.set_number($('#stat-depth'), total_depth);
        $('#stat-oldest-unacked').text(oldest_unacked > 0 ? kit.format_duration_ms(oldest_unacked * 1000) : '-');

        var now = Date.now();
        dash._spark_buffers.push('topics', now, topic_count);
        dash._spark_buffers.push('subscribers', now, total_subscribers);
        dash._spark_buffers.push('depth', now, total_depth);
        dash._spark_buffers.push('oldest_unacked', now, oldest_unacked);

        if (dash._stat_tile_handle) {
            dash._stat_tile_handle.bind();
        }

        // Topic table
        var topics = data.topics;
        var topic_body = $('#dashboard-topic-table-body');
        topic_body.empty();
        $('#dashboard-topics-count').text(topics.length);

        for (var i = 0; i < topics.length; i++) {
            var t = topics[i];
            var dot_class = t.is_active ? 'dashboard-dot-ok' : 'dashboard-dot-inactive';
            topic_body.append(
                '<tr>' +
                '<td class="dashboard-th-dot"><span class="dashboard-dot ' + dot_class + '"></span></td>' +
                '<td>' + t.name + '</td>' +
                '<td>' + kit.format_number_compact(t.subscriber_count) + '</td>' +
                '<td>' + kit.format_number_compact(t.depth) + '</td>' +
                '<td>' + kit.format_number_compact(t.pub_rate) + '/s</td>' +
                '</tr>'
            );
        }

        // Queue table
        var queues = data.queues;
        var queue_body = $('#dashboard-queue-table-body');
        queue_body.empty();
        $('#dashboard-queues-count').text(queues.length);

        for (var j = 0; j < queues.length; j++) {
            var q = queues[j];
            var q_dot_class = q.depth > 0 ? 'dashboard-dot-warn' : 'dashboard-dot-ok';
            queue_body.append(
                '<tr>' +
                '<td class="dashboard-th-dot"><span class="dashboard-dot ' + q_dot_class + '"></span></td>' +
                '<td>' + q.name + '</td>' +
                '<td>' + kit.format_number_compact(q.depth) + '</td>' +
                '<td>' + (q.oldest_msg_age_seconds > 0 ? kit.format_duration_ms(q.oldest_msg_age_seconds * 1000) : '-') + '</td>' +
                '<td>' + kit.format_number_compact(q.delivery_rate) + '/s</td>' +
                '</tr>'
            );
        }

        // Main chart - flatten the timeline into records the kit expects
        var timeline = data.history_timeline;
        var records = [];
        var publishes = timeline.publishes;
        var deliveries = timeline.deliveries;

        for (var pi = 0; pi < publishes.length; pi++) {
            records.push({ts: publishes[pi].ts, series: 'published', count: publishes[pi].count});
        }
        for (var di = 0; di < deliveries.length; di++) {
            records.push({ts: deliveries[di].ts, series: 'delivered', count: deliveries[di].count});
        }

        if (dash._chart_handle) {
            dash._chart_handle.render(records);
        }

        kit.lock_table_widths('#dashboard-topic-table');
        kit.lock_table_widths('#dashboard-queue-table');
    };

    // ////////////////////////////////////////////////////////////////////////
    // Poll
    // ////////////////////////////////////////////////////////////////////////

    dash.poll = function() {
        $.ajax({
            url: dash.config.base_url + 'poll/',
            type: 'POST',
            data: {},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(data) {
                if (typeof data === 'string') {
                    try { data = JSON.parse(data); } catch(e) { return; }
                }
                dash.render(data);
            },
            error: function() {}
        });
    };

    // ////////////////////////////////////////////////////////////////////////
    // Init
    // ////////////////////////////////////////////////////////////////////////

    dash.init = function(initial_data) {

        // Hero pill
        kit.init_hero_pill('#dashboard-hero-pill-group', dash.theme);

        // Main chart via kit
        dash._chart_handle = kit.main_chart.init({
            container: '#dashboard-bar-chart',
            legend: '#dashboard-chart-legend',
            count_pill: '#dashboard-data-count',
            chart_type_toggle: '#dashboard-chart-type-toggle',
            series_keys: ['published', 'delivered'],
            palette: dash.series_colors,
            labels: dash.series_labels,
            item_noun_singular: 'message',
            item_noun_plural: 'messages',
            range_names: {5: '5 min', 15: '15 min', 30: '30 min', 60: '1 hour', 360: '6 hours', 1440: 'Today'},
            bucket_ts: function(record) { return record.ts; },
            series_key: function(record) { return record.series; },
            hidden_storage_key: 'zato_pubsub_hidden_series',
            bars_storage_key: 'zato_pubsub_show_bars'
        });

        // Time range
        var _stored_range = parseInt(kit.storage_get('zato_pubsub_time_range'), 10);
        dash._time_range_minutes = isNaN(_stored_range) ? dash.config.default_time_range : _stored_range;
        dash._chart_handle.set_time_range_minutes(dash._time_range_minutes);

        var menu = $('#dashboard-time-range-menu');
        var pill = $('#dashboard-data-count');
        menu.find('.dashboard-time-range-option').removeClass('dashboard-time-range-active');
        menu.find('.dashboard-time-range-option[data-minutes="' + dash._time_range_minutes + '"]').addClass('dashboard-time-range-active');

        pill.on('click', function(event) {
            event.stopPropagation();
            menu.toggleClass('dashboard-time-range-menu-open');
        });

        menu.on('click', '.dashboard-time-range-option', function(event) {
            event.stopPropagation();
            var minutes = parseInt($(this).data('minutes'), 10);
            dash._time_range_minutes = minutes;
            kit.storage_set('zato_pubsub_time_range', String(minutes));
            dash._chart_handle.set_time_range_minutes(minutes);
            menu.find('.dashboard-time-range-option').removeClass('dashboard-time-range-active');
            $(this).addClass('dashboard-time-range-active');
            menu.removeClass('dashboard-time-range-menu-open');
            dash._chart_handle.redraw();
        });

        $(document).on('click', function() {
            menu.removeClass('dashboard-time-range-menu-open');
        });

        // Stat tile hover
        dash._stat_tile_handle = kit.stat_tile.init({
            tiles: [
                {sparkline_selector: '#spark-topics', buffer_key: 'topics', label: 'Topics', color: dash.theme.spark_color},
                {sparkline_selector: '#spark-subscribers', buffer_key: 'subscribers', label: 'Subscribers', color: dash.theme.spark_color},
                {sparkline_selector: '#spark-depth', buffer_key: 'depth', label: 'Depth', color: dash.theme.spark_warn},
                {sparkline_selector: '#spark-oldest-unacked', buffer_key: 'oldest_unacked', label: 'Oldest unacked', color: dash.theme.spark_err}
            ],
            get_buffer: function(key) {
                return dash._spark_buffers.data(key);
            }
        });

        dash.render(initial_data);
        kit.countdown.start();
        kit.reveal();

        dash._auto_refresh = kit.auto_refresh.init({
            pill: '#dashboard-refresh-pill',
            menu: '#dashboard-refresh-menu',
            storage_key: 'zato_pubsub_refresh',
            url_param: 'refresh',
            default_seconds: 5,
            on_tick: dash.poll
        });

        kit.url_state.on_pop(function(params) {
            var refresh_val = parseInt(params.get('refresh'), 10);
            if (!isNaN(refresh_val)) {
                dash._auto_refresh.set_seconds(refresh_val);
            }
        });
    };

})();
