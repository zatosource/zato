
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.pubsub === 'undefined') { $.fn.zato.pubsub = {}; }
$.fn.zato.pubsub.dashboard = {};

$.fn.zato.pubsub.dashboard.config = {
    cluster_id: '1',
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

(function($) {
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

        var oldest_unacked_ms = oldest_unacked * 1000;
        var oldest_unacked_label = oldest_unacked > 0 ? kit.format_duration_ms(oldest_unacked_ms) : '-';
        $('#stat-oldest-unacked').text(oldest_unacked_label);

        dash._spark_buffers.push('topics', topic_count);
        dash._spark_buffers.push('subscribers', total_subscribers);
        dash._spark_buffers.push('depth', total_depth);
        dash._spark_buffers.push('oldest_unacked', oldest_unacked);

        if (dash._stat_tile_handle) {
            dash._stat_tile_handle.bind();
        }

        // Build the topic table ..
        var topics = data.topics;
        var topic_body = $('#dashboard-topic-table-body');
        topic_body.empty();
        $('#dashboard-topics-count').text(topics.length);

        for (var topicIdx = 0; topicIdx < topics.length; topicIdx++) {
            var topic = topics[topicIdx];
            var topic_dot_class = topic.is_active ? 'dashboard-dot-ok' : 'dashboard-dot-inactive';

            var topic_row = document.createElement('tr');

            var topic_dot_cell = document.createElement('td');
            topic_dot_cell.className = 'dashboard-th-dot';
            var topic_dot_span = document.createElement('span');
            topic_dot_span.className = 'dashboard-dot ' + topic_dot_class;
            topic_dot_cell.appendChild(topic_dot_span);
            topic_row.appendChild(topic_dot_cell);

            var topic_name_cell = document.createElement('td');
            topic_name_cell.textContent = topic.name;
            topic_row.appendChild(topic_name_cell);

            var topic_sub_cell = document.createElement('td');
            topic_sub_cell.textContent = kit.format_number_compact(topic.subscriber_count);
            topic_row.appendChild(topic_sub_cell);

            var topic_depth_cell = document.createElement('td');
            topic_depth_cell.textContent = kit.format_number_compact(topic.depth);
            topic_row.appendChild(topic_depth_cell);

            var topic_rate_cell = document.createElement('td');
            topic_rate_cell.textContent = kit.format_number_compact(topic.pub_rate) + '/s';
            topic_row.appendChild(topic_rate_cell);

            topic_body.append(topic_row);
        }

        // .. build the queue table ..
        var queues = data.queues;
        var queue_body = $('#dashboard-queue-table-body');
        queue_body.empty();
        $('#dashboard-queues-count').text(queues.length);

        for (var queueIdx = 0; queueIdx < queues.length; queueIdx++) {
            var queue = queues[queueIdx];
            var queue_dot_class = queue.depth > 0 ? 'dashboard-dot-warn' : 'dashboard-dot-ok';

            var queue_age_ms = queue.oldest_msg_age_seconds * 1000;
            var queue_age_label = queue.oldest_msg_age_seconds > 0 ? kit.format_duration_ms(queue_age_ms) : '-';

            var queue_row = document.createElement('tr');

            var queue_dot_cell = document.createElement('td');
            queue_dot_cell.className = 'dashboard-th-dot';
            var queue_dot_span = document.createElement('span');
            queue_dot_span.className = 'dashboard-dot ' + queue_dot_class;
            queue_dot_cell.appendChild(queue_dot_span);
            queue_row.appendChild(queue_dot_cell);

            var queue_name_cell = document.createElement('td');
            queue_name_cell.textContent = queue.name;
            queue_row.appendChild(queue_name_cell);

            var queue_depth_cell = document.createElement('td');
            queue_depth_cell.textContent = kit.format_number_compact(queue.depth);
            queue_row.appendChild(queue_depth_cell);

            var queue_age_cell = document.createElement('td');
            queue_age_cell.textContent = queue_age_label;
            queue_row.appendChild(queue_age_cell);

            var queue_rate_cell = document.createElement('td');
            queue_rate_cell.textContent = kit.format_number_compact(queue.delivery_rate) + '/s';
            queue_row.appendChild(queue_rate_cell);

            queue_body.append(queue_row);
        }

        // .. flatten the timeline into records the kit expects ..
        var timeline = data.history_timeline;
        var records = [];
        var publishes = timeline.publishes;
        var deliveries = timeline.deliveries;

        for (var publishIdx = 0; publishIdx < publishes.length; publishIdx++) {
            records.push({ts: publishes[publishIdx].ts, series: 'published', count: publishes[publishIdx].count});
        }

        for (var deliveryIdx = 0; deliveryIdx < deliveries.length; deliveryIdx++) {
            records.push({ts: deliveries[deliveryIdx].ts, series: 'delivered', count: deliveries[deliveryIdx].count});
        }

        if (dash._chart_handle) {
            dash._chart_handle.render(records);
        }

        // .. and lock table column widths.
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
                    try { data = JSON.parse(data); } catch(parse_error) { return; }
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
        var stored_range = parseInt(kit.storage_get('zato_pubsub_time_range'), 10);
        dash._time_range_minutes = isNaN(stored_range) ? dash.config.default_time_range : stored_range;
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

})(jQuery);
