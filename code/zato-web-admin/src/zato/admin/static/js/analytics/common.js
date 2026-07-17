
// Traffic analytics dashboard - the shared core of the overview, per-channel
// and per-consumer screens. Each screen embeds its initial data in the page
// and polls its own endpoint on range changes and auto-refresh ticks.

// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.analytics.dashboard');

$.fn.zato.analytics.dashboard.config = {
    cluster_id: '1',
    screen: '',
    poll_url: '',
    csv_url: '',
    time_range: 'week',
    name: '',
    channel_page: '/zato/analytics/channel/',
    consumer_page: '/zato/analytics/consumer/',
    audit_log_page: '/zato/audit-log/',
    default_refresh_seconds: 60,
    no_data_text: 'No data yet',
    empty_period_text: '-'
};

$.fn.zato.analytics.dashboard.theme = {
    ok_color: '#2e7d32',
    error_color: '#c62828',
    marker_color: '#e65100',
    spark_color: '#5b8db8',
    error_spark_color: '#c62828'
};

// How each range is presented in the chart pill, keyed by its minute equivalent
$.fn.zato.analytics.dashboard.range_minutes = {
    day: 1440,
    week: 10080,
    month: 43200,
    quarter: 129600
};

$.fn.zato.analytics.dashboard.range_names = {
    1440: 'Last 24 hours',
    10080: 'Last 7 days',
    43200: 'Last 30 days',
    129600: 'Last 90 days'
};

// /////////////////////////////////////////////////////////////////////////////

(function() {

    var kit = null;
    var dash = $.fn.zato.analytics.dashboard;

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

        var request_points = [];
        var error_rate_points = [];

        for (var keyIdx = 0; keyIdx < keys.length; keyIdx++) {
            var period_key = keys[keyIdx];
            var period_total = totals[period_key];
            var period_errors = errors[period_key];

            var period_error_rate = 100.0 * period_errors / period_total;

            request_points.push(period_total);
            error_rate_points.push(period_error_rate);
        }

        return {requests: request_points, error_rates: error_rate_points};
    };

    // ////////////////////////////////////////////////////////////////////////

    dash.render_tiles = function(data) {
        var totals = data.totals;

        kit.set_number($('#stat-requests'), totals.request_count);
        $('#stat-error-rate').text(totals.error_rate + '%');
        $('#stat-p95').text(kit.format_duration_ms(totals.p95_ms));
        kit.set_number($('#stat-related'), totals.related_count);

        var p50 = kit.format_duration_ms(totals.p50_ms);
        var p99 = kit.format_duration_ms(totals.p99_ms);
        $('#stat-p95-sublabel').text('p50 ' + p50 + ' \u00b7 p99 ' + p99);

        // The consumer screen additionally says when the credential was last seen
        if (dash.config.screen === 'consumer') {
            if (totals.last_seen) {
                $('#stat-related-sublabel').text('Last seen ' + totals.last_seen + ' UTC');
            } else {
                $('#stat-related-sublabel').text('');
            }
        }

        // The tile sparklines show the window's own trend
        var points = dash.period_totals(data.timeline);

        kit.sparkline.render('#spark-requests', points.requests, {color: dash.theme.spark_color});
        kit.sparkline.render('#spark-error-rate', points.error_rates, {color: dash.theme.error_spark_color});
    };

    // ////////////////////////////////////////////////////////////////////////

    dash.render = function(data) {
        dash.last_data = data;

        var diag_start = performance.now();

        dash.render_tiles(data);
        var diag_tiles = performance.now();

        dash.chart.render(data.timeline);
        var diag_chart = performance.now();

        dash.render_tables(data);
        var diag_tables = performance.now();

        console.log('[Analytics-Diag] render: timeline=' + data.timeline.length +
            ' tiles=' + (diag_tiles - diag_start).toFixed(1) + 'ms' +
            ' chart=' + (diag_chart - diag_tiles).toFixed(1) + 'ms' +
            ' tables=' + (diag_tables - diag_chart).toFixed(1) + 'ms' +
            ' total=' + (diag_tables - diag_start).toFixed(1) + 'ms');
    };

    // ////////////////////////////////////////////////////////////////////////

    dash.poll = function() {
        var body = {
            range: dash.config.time_range,
            name: dash.config.name
        };

        $.ajax({
            url: dash.config.poll_url,
            type: 'POST',
            data: JSON.stringify(body),
            contentType: 'application/json',
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(data) {
                var diag_start = performance.now();
                if (typeof data === 'string') {
                    data = JSON.parse(data);
                }
                var diag_parsed = performance.now();
                dash.render(data);

                console.log('[Analytics-Diag] poll: parse=' + (diag_parsed - diag_start).toFixed(1) + 'ms' +
                    ' render=' + (performance.now() - diag_parsed).toFixed(1) + 'ms');
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    // The address of this screen's CSV export, with the current filters applied.
    dash.csv_href = function() {
        var href = dash.config.csv_url + '?range=' + encodeURIComponent(dash.config.time_range);
        href += '&cluster=' + dash.config.cluster_id;

        if (dash.config.name) {
            href += '&name=' + encodeURIComponent(dash.config.name);
        }

        return href;
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

            $('#analytics-csv-pill').attr('href', dash.csv_href());

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
            tooltip_id: 'analytics-chart-tooltip',
            series_keys: ['ok', 'error'],
            palette: {ok: dash.theme.ok_color, error: dash.theme.error_color},
            labels: {ok: 'OK', error: 'Errors'},
            item_noun_singular: 'request',
            item_noun_plural: 'requests',
            range_names: dash.range_names,
            bucket_ts: function(record) { return record.ts_ms; },
            series_key: function(record) { return record.series; },
            hidden_storage_key: 'zato_analytics_chart_hidden',
            bars_storage_key: 'zato_analytics_chart_bars',
            record_marker: function(record) { return record.is_anomaly; },
            marker_color: dash.theme.marker_color,
            marker_label: 'Unusual for this hour of the week'
        };

        // A click on the per-channel chart drills down into the audit log
        // pre-filtered to this channel and the clicked time window.
        if (dash.config.screen === 'channel') {
            chart_config.on_bucket_click = function(bucket) {
                var data = dash.last_data;

                if (!data.source) {
                    return;
                }

                var href = dash.config.audit_log_page;
                href += '?source=' + encodeURIComponent(data.source);
                href += '&object_name=' + encodeURIComponent(dash.config.name);
                href += '&cluster=' + dash.config.cluster_id;
                href += '&time_from=' + encodeURIComponent(dash.to_iso_second(bucket.start));
                href += '&time_to=' + encodeURIComponent(dash.to_iso_second(bucket.end));

                window.location.href = href;
            };
        }

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

        var diag_start = performance.now();

        dash.setup_chart();
        dash.setup_time_range();
        dash.setup_copy();

        $('#analytics-csv-pill').attr('href', dash.csv_href());

        var diag_setup = performance.now();

        dash.render(initial_data);

        console.log('[Analytics-Diag] init: setup=' + (diag_setup - diag_start).toFixed(1) + 'ms' +
            ' initial_render=' + (performance.now() - diag_setup).toFixed(1) + 'ms');

        dash.auto_refresh = kit.auto_refresh.init({
            pill: '#dashboard-refresh-pill',
            menu: '#dashboard-refresh-menu',
            storage_key: 'zato_analytics_refresh',
            url_param: 'refresh',
            default_seconds: dash.config.default_refresh_seconds,
            on_tick: dash.poll
        });

        kit.reveal();
    };

})();
