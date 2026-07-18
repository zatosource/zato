
// The HL7 channel dashboard - health tiles, the hourly traffic chart and the
// per-channel table. The page embeds its initial data and polls its endpoint
// on range changes and auto-refresh ticks. History comes from the audit
// database, health and live counters from the get-current-state service.

// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.channel.hl7.dashboard');

$.fn.zato.channel.hl7.dashboard.config = {
    cluster_id: '1',
    poll_url: '',
    time_range: 'week',
    audit_log_page: '/zato/audit-log/',
    default_refresh_seconds: 60,
    no_data_text: 'No data yet',
    no_value_text: '-'
};

$.fn.zato.channel.hl7.dashboard.theme = {
    ok_color: '#2e7d32',
    error_color: '#c62828',
    spark_color: '#5b8db8',
    error_spark_color: '#c62828'
};

// The colors and labels of the health states
$.fn.zato.channel.hl7.dashboard.health = {
    colors: {
        green: '#2e7d32',
        amber: '#e65100',
        red: '#c62828',
        unknown: '#a0a0a5'
    },
    labels: {
        green: 'Healthy',
        amber: 'Degraded',
        red: 'Down',
        unknown: 'Unknown'
    }
};

// How each range is presented in the chart pill, keyed by its minute equivalent
$.fn.zato.channel.hl7.dashboard.range_minutes = {
    day: 1440,
    week: 10080,
    month: 43200,
    quarter: 129600
};

$.fn.zato.channel.hl7.dashboard.range_names = {
    1440: 'Last 24 hours',
    10080: 'Last 7 days',
    43200: 'Last 30 days',
    129600: 'Last 90 days'
};

// /////////////////////////////////////////////////////////////////////////////

(function() {

    var kit = null;
    var dash = $.fn.zato.channel.hl7.dashboard;

    // ////////////////////////////////////////////////////////////////////////

    // Turns a millisecond timestamp into the second-precision ISO form
    // the audit log's time filters compare against.
    dash.to_iso_second = function(ts_ms) {
        var when = new Date(ts_ms);
        var iso = when.toISOString();

        var iso_second = iso.slice(0, 19);
        return iso_second;
    };

    // ////////////////////////////////////////////////////////////////////////

    // The per-period totals of the timeline, for the tile sparklines.
    dash.period_totals = function(timeline) {
        var totals = {};
        var errors = {};

        for (var recordIdx = 0; recordIdx < timeline.length; recordIdx++) {
            var record = timeline[recordIdx];
            var key = record.ts_ms;

            if (!(key in totals)) {
                totals[key] = 0;
                errors[key] = 0;
            }

            totals[key] += record.count;

            if (record.series === 'error') {
                errors[key] += record.count;
            }
        }

        var keys = Object.keys(totals).sort(function(left, right) { return left - right; });

        var message_points = [];
        var error_rate_points = [];

        for (var keyIdx = 0; keyIdx < keys.length; keyIdx++) {
            var period_key = keys[keyIdx];
            var period_total = totals[period_key];
            var period_errors = errors[period_key];

            var period_error_rate = 100.0 * period_errors / period_total;

            message_points.push(period_total);
            error_rate_points.push(period_error_rate);
        }

        return {messages: message_points, error_rates: error_rate_points};
    };

    // ////////////////////////////////////////////////////////////////////////

    // The address of the audit log pre-filtered to one channel.
    dash.audit_href = function(name) {
        var href = dash.config.audit_log_page;
        href += '?source=hl7';
        href += '&object_name=' + encodeURIComponent(name);
        href += '&cluster=' + dash.config.cluster_id;

        return href;
    };

    // ////////////////////////////////////////////////////////////////////////

    dash.render_tiles = function(data) {
        var totals = data.totals;
        var health_counts = data.health_counts;

        kit.set_number($('#stat-messages'), totals.message_count);
        $('#stat-error-rate').text(totals.error_rate + '%');

        // How many channels are on the board and how many of them listen right now
        var channel_count = data.channels.length;
        var listening_count = 0;

        for (var channelIdx = 0; channelIdx < data.channels.length; channelIdx++) {
            var channel = data.channels[channelIdx];

            if (channel.live !== null && channel.live.is_listening) {
                listening_count += 1;
            }
        }

        $('#stat-channels').text(channel_count);
        $('#stat-channels-sublabel').text(listening_count + ' listening');

        // The health tile leads with the green count and details the rest
        $('#stat-health').text(health_counts.green + ' / ' + channel_count);
        $('#stat-health-sublabel').text(
            health_counts.amber + ' degraded \u00b7 ' + health_counts.red + ' down \u00b7 ' +
            health_counts.unknown + ' unknown');

        // The tile sparklines show the window's own trend
        var points = dash.period_totals(data.timeline);

        kit.sparkline.render('#spark-messages', points.messages, {color: dash.theme.spark_color});
        kit.sparkline.render('#spark-error-rate', points.error_rates, {color: dash.theme.error_spark_color});
    };

    // ////////////////////////////////////////////////////////////////////////

    // One cell holding plain text.
    dash._text_cell = function(text) {
        var cell = document.createElement('td');
        cell.textContent = text;

        return cell;
    };

    // One cell holding a link.
    dash._link_cell = function(text, href) {
        var cell = document.createElement('td');
        var link = document.createElement('a');

        link.textContent = text;
        link.href = href;

        cell.appendChild(link);

        return cell;
    };

    // One cell holding this channel's health dot.
    dash._health_cell = function(health) {
        var cell = document.createElement('td');
        var dot = document.createElement('span');

        dot.className = 'dashboard-status-dot';
        dot.style.background = dash.health.colors[health];
        dot.title = dash.health.labels[health];

        cell.appendChild(dot);
        cell.appendChild(document.createTextNode(' ' + dash.health.labels[health]));

        return cell;
    };

    // One cell holding a sparkline holder - rendered once the row is in the document.
    dash._spark_seq = 0;

    dash._spark_cell = function(points) {
        var cell = document.createElement('td');

        dash._spark_seq += 1;
        var spark_id = 'hl7-row-spark-' + dash._spark_seq;

        var holder = document.createElement('div');
        holder.id = spark_id;
        holder.className = 'dashboard-tile-spark';

        cell.appendChild(holder);

        return {cell: cell, spark_id: spark_id, points: points};
    };

    // ////////////////////////////////////////////////////////////////////////

    // The live-counter summary of one channel - received, acked, nacked and errored.
    // A null means no server reported this channel's live state.
    dash._live_summary = function(live) {
        if (live === null) {
            return dash.config.no_value_text;
        }

        var summary = live.received + ' in \u00b7 ' + live.acked + ' ack';

        if (live.nacked) {
            summary += ' \u00b7 ' + live.nacked + ' nack';
        }

        if (live.errored) {
            summary += ' \u00b7 ' + live.errored + ' err';
        }

        return summary;
    };

    // The last-message display of one channel - the live time wins over the history.
    dash._last_message = function(channel) {
        var last = channel.last_event_iso;

        // The live time is empty until the channel sees its first message
        if (channel.live !== null && channel.live.last_message_time_iso !== '') {
            last = channel.live.last_message_time_iso;
        }

        if (last === '') {
            return dash.config.no_value_text;
        }

        var display = last.slice(0, 19).replace('T', ' ') + ' UTC';
        return display;
    };

    // ////////////////////////////////////////////////////////////////////////

    dash.render_channels = function(data) {
        var body = document.querySelector('#hl7-channels-table-body');
        body.textContent = '';

        $('#hl7-channels-count').text(data.channels.length);

        if (data.channels.length === 0) {
            var no_data_row = document.createElement('tr');
            var no_data_cell = document.createElement('td');

            no_data_cell.colSpan = 8;
            no_data_cell.className = 'dashboard-no-data';
            no_data_cell.textContent = dash.config.no_data_text;

            no_data_row.appendChild(no_data_cell);
            body.appendChild(no_data_row);
            return;
        }

        // Build every row into a fragment first, so the document is touched once ..
        var fragment = document.createDocumentFragment();
        var sparks = [];

        for (var channelIdx = 0; channelIdx < data.channels.length; channelIdx++) {
            var channel = data.channels[channelIdx];
            var row = document.createElement('tr');

            var spark = dash._spark_cell(channel.spark);
            sparks.push(spark);

            row.appendChild(dash._health_cell(channel.health));
            row.appendChild(dash._link_cell(channel.name, dash.audit_href(channel.name)));
            row.appendChild(spark.cell);
            row.appendChild(dash._text_cell(kit.format_number_full(channel.received)));
            row.appendChild(dash._text_cell(channel.error_rate + '%'));
            row.appendChild(dash._text_cell(dash._live_summary(channel.live)));
            row.appendChild(dash._text_cell(dash._last_message(channel)));
            row.appendChild(dash._link_cell('Audit log', dash.audit_href(channel.name)));

            fragment.appendChild(row);
        }

        body.appendChild(fragment);

        // .. measure the sparkline column once and draw with an explicit width,
        // so drawing never re-asks the document about layout.
        var spark_width = document.getElementById(sparks[0].spark_id).clientWidth;

        if (spark_width < 20) {
            spark_width = 240;
        }

        for (var sparkIdx = 0; sparkIdx < sparks.length; sparkIdx++) {
            var entry = sparks[sparkIdx];
            kit.sparkline.render('#' + entry.spark_id, entry.points, {color: dash.theme.spark_color, width: spark_width});
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    dash.render = function(data) {
        dash.last_data = data;

        dash.render_tiles(data);
        dash.chart.render(data.timeline);
        dash.render_channels(data);
    };

    // ////////////////////////////////////////////////////////////////////////

    dash.poll = function() {
        var body = {
            range: dash.config.time_range
        };

        $.ajax({
            url: dash.config.poll_url,
            type: 'POST',
            data: JSON.stringify(body),
            contentType: 'application/json',
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(data) {
                if (typeof data === 'string') {
                    data = JSON.parse(data);
                }
                dash.render(data);
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    dash.setup_time_range = function() {

        // Show the menu on click ..
        $('#dashboard-data-count').on('click', function(event) {
            event.stopPropagation();
            $('#dashboard-time-range-menu').toggleClass('dashboard-time-range-menu-open');
        });

        $(document).on('click', function() {
            $('#dashboard-time-range-menu').removeClass('dashboard-time-range-menu-open');
        });

        // .. and let each option switch the window and poll anew.
        $('.dashboard-time-range-option').on('click', function(event) {
            event.stopPropagation();

            var option = $(this);
            var range = option.attr('data-range');

            $('.dashboard-time-range-option').removeClass('dashboard-time-range-active');
            option.addClass('dashboard-time-range-active');
            $('#dashboard-time-range-menu').removeClass('dashboard-time-range-menu-open');

            dash.config.time_range = range;
            dash.chart.set_time_range_minutes(dash.range_minutes[range]);

            var urlParams = new URLSearchParams(window.location.search);
            urlParams.set('range', range);
            history.replaceState(null, '', '?' + urlParams.toString());

            dash.poll();
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    dash.setup_chart = function() {

        var chart_config = {
            container: '#dashboard-bar-chart',
            legend: '#dashboard-chart-legend',
            count_pill: '#dashboard-data-count',
            chart_type_toggle: '#dashboard-chart-type-toggle',
            tooltip_id: 'hl7-chart-tooltip',
            series_keys: ['ok', 'error'],
            palette: {ok: dash.theme.ok_color, error: dash.theme.error_color},
            labels: {ok: 'OK', error: 'Errors'},
            item_noun_singular: 'message',
            item_noun_plural: 'messages',
            range_names: dash.range_names,
            bucket_ts: function(record) { return record.ts_ms; },
            series_key: function(record) { return record.series; },
            hidden_storage_key: 'zato_hl7_chart_hidden',
            bars_storage_key: 'zato_hl7_chart_bars'
        };

        dash.chart = kit.main_chart.init(chart_config);
        dash.chart.set_time_range_minutes(dash.range_minutes[dash.config.time_range]);
    };

    // ////////////////////////////////////////////////////////////////////////

    dash.setup_copy = function() {
        $('#dashboard-chart-copy').on('click', function() {
            var data = dash.last_data;
            var text = JSON.stringify(data.timeline, null, 2);

            navigator.clipboard.writeText(text);

            var pill = $(this);
            pill.text('Copied');

            pill.one('mouseleave', function() {
                pill.text('Copy');
            });
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    dash.init = function(initial_data) {
        kit = $.fn.zato.dashboard_kit;

        dash.setup_chart();
        dash.setup_time_range();
        dash.setup_copy();

        dash.render(initial_data);

        dash.auto_refresh = kit.auto_refresh.init({
            pill: '#dashboard-refresh-pill',
            menu: '#dashboard-refresh-menu',
            storage_key: 'zato_hl7_dashboard_refresh',
            url_param: 'refresh',
            default_seconds: dash.config.default_refresh_seconds,
            on_tick: dash.poll
        });

        kit.reveal();
    };

})();
