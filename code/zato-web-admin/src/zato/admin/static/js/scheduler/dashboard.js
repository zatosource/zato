
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.scheduler === 'undefined') { $.fn.zato.scheduler = {}; }
$.fn.zato.scheduler.dashboard = {};

// Dashboard configuration. Each key can be overridden by per-page dashboards.
$.fn.zato.scheduler.dashboard.config = {
    cluster_id: '1',
    base_url: '/zato/scheduler/dashboard/',
    default_time_range: 0,
    error_message: 'Error executing job',
    show_live_status: false,
    show_tab_counts: false,
    max_upcoming_rows: 100,
    ms_per_minute: 60000,
    ms_per_hour:   3600000,
    ms_per_day:    86400000,
    ms_per_week:   604800000,
    ms_per_month:  2764800000,
    ms_per_year:   31536000000,
    day_names:   ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
    month_names: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
};

$.fn.zato.scheduler.dashboard.Outcome_All = 'all';

// ////////////////////////////////////////////////////////////////////////////
// Theme - all dashboard-specific colors in one place
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.theme = {
    name: 'Scheduler',
    accent:       '#82ccff',
    accent_light: '#b0dfff',
    accent_dark:  '#2a7fbf',
    spark_color:  '#82ccff',
    spark_err:    '#ff6b6b',
    pill_bg:        '#1a6fa0',
    pill_color:     '#e0f0ff',
    pill_link_bg:   '#0f4a6e',
    pill_link_color: '#c0e2f5',
    pill_links: false ? [
        // When re-enabling, restore top:50%;transform:translateY(-50%) on .dashboard-hero-pill-group in kit.css
        {label: 'History', href: '#'},
        {label: 'Recent runs', href: '#'},
        {label: 'Upcoming', href: '#'}
    ] : [],
    row_recency_color: '218, 165, 32'
};

// ////////////////////////////////////////////////////////////////////////////
// Outcome color map - tinted badge palette (uses theme accent for OK)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.outcome_colors = {
    'ok': '#2a7fbf',
    'running': '#888',
    'error': '#e0226e',
    'timeout': '#b35e00',
    'skipped_already_in_flight': '#7b5ea7'
};

$.fn.zato.scheduler.dashboard.outcome_backgrounds = {
    'ok': 'rgba(42, 127, 191, 0.12)',
    'running': 'rgba(136, 136, 136, 0.12)',
    'error': 'rgba(224, 34, 110, 0.12)',
    'timeout': 'rgba(179, 94, 0, 0.12)',
    'skipped_already_in_flight': 'rgba(123, 94, 167, 0.12)'
};

$.fn.zato.scheduler.dashboard.outcome_bar_colors = {
    'ok': '#3a9ad9',
    'running': '#aaa',
    'error': '#c0392b',
    'timeout': '#b45309',
    'skipped_already_in_flight': '#6b4d94'
};

$.fn.zato.scheduler.dashboard.outcome_bar_tints = {
    'ok': '#d1e8f8',
    'running': '#e0e0e0',
    'error': '#f5d5d2',
    'timeout': '#fde8cd',
    'skipped_already_in_flight': '#ddd0ef'
};

$.fn.zato.scheduler.dashboard.outcome_labels = {
    'ok': 'OK',
    'running': 'Running',
    'error': 'Error',
    'timeout': 'Timeout',
    'skipped_already_in_flight': 'Skipped (already in flight)'
};

$.fn.zato.scheduler.dashboard.outcome_short_labels = {
    'skipped_already_in_flight': 'Skipped'
};

$.fn.zato.scheduler.dashboard.outcome_tooltips = {
    'skipped_already_in_flight': 'Skipped because run #{ctx} was already in flight'
};


$.fn.zato.scheduler.dashboard.outcome_palette = {
    colors: $.fn.zato.scheduler.dashboard.outcome_colors,
    backgrounds: $.fn.zato.scheduler.dashboard.outcome_backgrounds,
    bar_colors: $.fn.zato.scheduler.dashboard.outcome_bar_colors,
    labels: $.fn.zato.scheduler.dashboard.outcome_labels,
    short_labels: $.fn.zato.scheduler.dashboard.outcome_short_labels,
    tooltips: $.fn.zato.scheduler.dashboard.outcome_tooltips
};

// ////////////////////////////////////////////////////////////////////////////
// Kit aliases - keep short references for code that used the old local names
// ////////////////////////////////////////////////////////////////////////////

(function() {
    var kit = $.fn.zato.dashboard_kit;
    var dash = $.fn.zato.scheduler.dashboard;

    dash._recent_runs_ts = [];

    // Thin aliases so job_detail.js (and any future callers that used
    // the old scheduler-level API) keep working without changes.
    dash.format_duration = kit.format_duration_ms;
    dash.relative_time_future = kit.relative_time_future;
    dash.relative_time_past = kit.relative_time_past;

    // Spark buffers via kit
    dash._spark_buffers = kit.spark.create({
        keys: ['total_jobs', 'active', 'paused', 'runs', 'recent'],
        window_ms: 60 * 60 * 1000,
        bucket_count: 60
    });

    // ////////////////////////////////////////////////////////////////////////
    // Chart data cache state
    // ////////////////////////////////////////////////////////////////////////

    // ////////////////////////////////////////////////////////////////////////
    // Legend toggle persistence
    // ////////////////////////////////////////////////////////////////////////

    dash._get_hidden_outcomes = function() {
        return kit.storage_get_json('zato_scheduler_hidden_outcomes') || {};
    };

    dash._set_hidden_outcomes = function(hidden) {
        kit.storage_set_json('zato_scheduler_hidden_outcomes', hidden);
    };

    dash._toggle_outcome = function(key) {
        var hidden = dash._get_hidden_outcomes();
        if (hidden[key]) {
            delete hidden[key];
        } else {
            hidden[key] = true;
        }
        dash._set_hidden_outcomes(hidden);
        dash._redraw_chart_from_cache();
    };

    // ////////////////////////////////////////////////////////////////////////
    // Time range (uses kit for persistence, keeps scheduler-specific filter)
    // ////////////////////////////////////////////////////////////////////////

    dash._last_chart_buckets = null;
    dash._last_recent_events = [];
    dash._last_event_ts = '';
    dash._last_jobs = null;
    dash._time_range_minutes = 0;

    var _BUCKET_COUNT = 120;

    var _calendar_ranges = {
        1440: 'today',
        2880: 'yesterday',
        10080: 'this_week',
        43200: 'this_month',
        525600: 'this_year'
    };

    dash._get_chart_window = function() {
        var minutes = dash._time_range_minutes;
        if (!minutes || minutes <= 0) {
            return {since_iso: '', until_iso: ''};
        }

        var cal = _calendar_ranges[minutes];
        if (cal) {
            var now = new Date();
            var since, until;
            if (cal === 'today') {
                since = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                until = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
            } else if (cal === 'yesterday') {
                until = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                since = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
            } else if (cal === 'this_week') {
                var day = now.getDay();
                var diff = (day === 0) ? 6 : day - 1;
                since = new Date(now.getFullYear(), now.getMonth(), now.getDate() - diff);
                until = new Date(since.getFullYear(), since.getMonth(), since.getDate() + 7);
            } else if (cal === 'this_month') {
                since = new Date(now.getFullYear(), now.getMonth(), 1);
                until = new Date(now.getFullYear(), now.getMonth() + 1, 1);
            } else {
                since = new Date(now.getFullYear(), 0, 1);
                until = new Date(now.getFullYear() + 1, 0, 1);
            }
            return {since_iso: since.toISOString(), until_iso: until.toISOString()};
        }

        var range_ms = minutes * 60000;
        var bucket_size_ms = range_ms / _BUCKET_COUNT;
        var now_ms = Date.now();
        var until_ms = Math.ceil(now_ms / bucket_size_ms) * bucket_size_ms;
        var since_ms = until_ms - range_ms;
        return {since_iso: new Date(since_ms).toISOString(), until_iso: new Date(until_ms).toISOString()};
    };

    dash._filter_recent_by_range = function(events) {
        var minutes = dash._time_range_minutes;
        if (!minutes || minutes <= 0 || !events) {
            return events;
        }
        var cutoff = Date.now() - (minutes * 60 * 1000);
        var filtered = [];
        for (var i = 0; i < events.length; i++) {
            var ts = events[i].actual_fire_time_iso;
            if (ts && new Date(ts).getTime() >= cutoff) {
                filtered.push(events[i]);
            }
        }
        return filtered;
    };

    dash._skip_legend_rebuild = false;

    dash._redraw_chart_from_cache = function() {
        console.log('[redraw_from_cache] called, have buckets=' + !!dash._last_chart_buckets);
        if (dash._last_chart_buckets) {
            var _t0 = performance.now();
            dash._skip_legend_rebuild = true;
            dash.render_bar_chart(dash._last_chart_buckets);
            dash._skip_legend_rebuild = false;
            var filtered_recent = dash._filter_recent_by_range(dash._last_recent_events);
            dash.render_recent(filtered_recent, dash._last_jobs);
            console.log('[redraw_from_cache] completed in ' + (performance.now() - _t0).toFixed(0) + 'ms');
        }
    };

    // ////////////////////////////////////////////////////////////////////////
    // Status dot
    // ////////////////////////////////////////////////////////////////////////

    dash.status_dot = function(job) {
        if (job.is_running) {
            return {html: '<span class="dashboard-status-dot dashboard-status-running"></span>', tooltip: 'Running'};
        }
        if (!job.is_active) {
            return {html: '<span class="dashboard-status-dot dashboard-status-paused"></span>', tooltip: 'Paused'};
        }
        if (job.last_outcome === 'error' || job.last_outcome === 'timeout') {
            return {html: '<span class="dashboard-status-dot dashboard-status-failed"></span>', tooltip: 'Last run failed'};
        }
        return {html: '<span class="dashboard-status-idle">-</span>', tooltip: 'Waiting for next run'};
    };

    // ////////////////////////////////////////////////////////////////////////
    // Outcome micro-chart (colored squares)
    // ////////////////////////////////////////////////////////////////////////

    dash.outcome_squares = function(recent_outcomes) {
        if (!recent_outcomes || recent_outcomes.length === 0) {
            return '<span style="color:#a0a0a5">-</span>';
        }
        var bar_colors = dash.outcome_bar_colors;
        var labels = dash.outcome_labels;

        var counts = {};
        for (var index = 0; index < recent_outcomes.length; index++) {
            var outcome = recent_outcomes[index];
            counts[outcome] = (counts[outcome] || 0) + 1;
        }

        var tip_lines = [];
        for (var key in counts) {
            if (counts.hasOwnProperty(key)) {
                var run_word = counts[key] === 1 ? 'run' : 'runs';
                tip_lines.push('<div class="dashboard-tooltip-row">' +
                    '<span class="dashboard-tooltip-dot" style="background:' + bar_colors[key] + '"></span>' +
                    labels[key] + ': <b>' + counts[key] + '</b> ' + run_word + '</div>');
            }
        }
        var tip_html = '<div class="dashboard-tooltip-body">' + tip_lines.join('') + '</div>';

        var html = '<span class="dashboard-outcome-squares-group" data-tippy-content="' +
            tip_html.replace(/"/g, '&quot;') + '">';
        for (var sq_index = 0; sq_index < recent_outcomes.length; sq_index++) {
            var sq_outcome = recent_outcomes[sq_index];
            html += '<span class="dashboard-outcome-square" style="background:' + bar_colors[sq_outcome] + '"></span>';
        }
        html += '</span>';
        return html;
    };

    // ////////////////////////////////////////////////////////////////////////
    // Top-rounded bar path helper
    // ////////////////////////////////////////////////////////////////////////

    dash.top_rounded_bar = function(x, y, w, h, r) {
        if (h < r) r = h;
        if (w < 2 * r) r = w / 2;
        return 'M' + x + ',' + (y + h) +
               ' v' + (-(h - r)) +
               ' a' + r + ',' + r + ' 0 0 1 ' + r + ',' + (-r) +
               ' h' + (w - 2 * r) +
               ' a' + r + ',' + r + ' 0 0 1 ' + r + ',' + r +
               ' v' + (h - r) +
               ' z';
    };

    // ////////////////////////////////////////////////////////////////////////
    // Time label formatting
    // ////////////////////////////////////////////////////////////////////////

    dash.formatTimeLabel = function(date, timeRangeMs) {

        var hours   = ('0' + date.getHours()).slice(-2);
        var minutes = ('0' + date.getMinutes()).slice(-2);
        var seconds = ('0' + date.getSeconds()).slice(-2);

        var dayName   = dash.config.day_names[date.getDay()];
        var monthName = dash.config.month_names[date.getMonth()];
        var shortYear = String(date.getFullYear()).slice(-2);

        if (timeRangeMs < 10 * dash.config.ms_per_minute) {
            return hours + ':' + minutes + ':' + seconds;
        } else if (timeRangeMs < dash.config.ms_per_day) {
            return hours + ':' + minutes;
        } else if (timeRangeMs < dash.config.ms_per_week) {
            return dayName + ' ' + hours + ':' + minutes;
        } else if (timeRangeMs <= dash.config.ms_per_week) {
            return dayName + ' ' + monthName + ' ' + date.getDate();
        } else if (timeRangeMs < dash.config.ms_per_month) {
            return monthName + ' ' + date.getDate();
        } else if (timeRangeMs < dash.config.ms_per_year) {
            return monthName;
        } else {
            return monthName + ' ' + shortYear;
        }
    };

    // ////////////////////////////////////////////////////////////////////////
    // Monotone cubic Hermite spline (Fritsch-Carlson)
    // ////////////////////////////////////////////////////////////////////////

    // Builds an SVG path string using monotone cubic Hermite interpolation
    // (Fritsch-Carlson method, same algorithm as Grafana/uPlot).
    // Guarantees the curve never overshoots between adjacent knots,
    // so it cannot dip below zero when all input values are >= 0.
    dash.buildMonotoneCubicPath = function(points) {
        var pointCount = points.length;
        var path = 'M' + points[0].x.toFixed(1) + ',' + points[0].y.toFixed(1);

        if (pointCount === 2) {
            path += ' L' + points[1].x.toFixed(1) + ',' + points[1].y.toFixed(1);
            return path;
        }

        // .. compute segment deltas and slopes ..
        var segmentDeltaX = [];
        var segmentDeltaY = [];
        var segmentSlopes = [];

        for (var segmentIdx = 0; segmentIdx < pointCount - 1; segmentIdx++) {
            segmentDeltaX[segmentIdx] = points[segmentIdx + 1].x - points[segmentIdx].x;
            segmentDeltaY[segmentIdx] = points[segmentIdx + 1].y - points[segmentIdx].y;
            segmentSlopes[segmentIdx] = segmentDeltaX[segmentIdx] !== 0
                ? segmentDeltaY[segmentIdx] / segmentDeltaX[segmentIdx]
                : 0;
        }

        // .. compute tangent slopes using Fritsch-Carlson monotonicity constraint ..
        var tangentSlopes = [];
        tangentSlopes[0] = segmentSlopes[0];

        for (var knotIdx = 1; knotIdx < pointCount - 1; knotIdx++) {
            var slopeBefore = segmentSlopes[knotIdx - 1];
            var slopeAfter  = segmentSlopes[knotIdx];

            if (slopeAfter === 0 || slopeBefore === 0 || (slopeBefore > 0) !== (slopeAfter > 0)) {
                tangentSlopes[knotIdx] = 0;
            } else {
                var weightedHarmonicMean = 3 * (segmentDeltaX[knotIdx - 1] + segmentDeltaX[knotIdx]) / (
                    (2 * segmentDeltaX[knotIdx] + segmentDeltaX[knotIdx - 1]) / slopeBefore +
                    (segmentDeltaX[knotIdx] + 2 * segmentDeltaX[knotIdx - 1]) / slopeAfter
                );
                tangentSlopes[knotIdx] = isFinite(weightedHarmonicMean) ? weightedHarmonicMean : 0;
            }
        }

        tangentSlopes[pointCount - 1] = segmentSlopes[pointCount - 2];

        // .. emit cubic Bezier segments with control points at 1/3 of segment width ..
        for (var curveIdx = 0; curveIdx < pointCount - 1; curveIdx++) {
            var deltaX = segmentDeltaX[curveIdx];
            var controlPoint1X = points[curveIdx].x + deltaX / 3;
            var controlPoint1Y = points[curveIdx].y + tangentSlopes[curveIdx] * deltaX / 3;
            var controlPoint2X = points[curveIdx + 1].x - deltaX / 3;
            var controlPoint2Y = points[curveIdx + 1].y - tangentSlopes[curveIdx + 1] * deltaX / 3;
            path += ' C' + controlPoint1X.toFixed(1) + ',' + controlPoint1Y.toFixed(1) +
                    ' ' + controlPoint2X.toFixed(1) + ',' + controlPoint2Y.toFixed(1) +
                    ' ' + points[curveIdx + 1].x.toFixed(1) + ',' + points[curveIdx + 1].y.toFixed(1);
        }

        return path;
    };

    // ////////////////////////////////////////////////////////////////////////
    // Bar chart
    // ////////////////////////////////////////////////////////////////////////

    dash.render_bar_chart = function(chart_data) {
        var _bar_t0 = performance.now();
        dash._last_chart_buckets = chart_data;
        var container = $('#dashboard-bar-chart');

        var _dbg_minutes = dash._time_range_minutes;
        var _dbg_cutoff = (_dbg_minutes && _dbg_minutes > 0) ? new Date(Date.now() - _dbg_minutes * 60000).toISOString() : '(none)';
        console.log('[chart-debug] render_bar_chart called, _time_range_minutes=' + _dbg_minutes +
            ', server_buckets=' + (chart_data && chart_data.buckets ? chart_data.buckets.length : 0) +
            ', cutoff=' + _dbg_cutoff);

        if (!chart_data || !chart_data.buckets || chart_data.buckets.length === 0) {
            container.html('<div class="dashboard-no-data">No run history yet</div>');
            $('#dashboard-chart-legend').empty();
            $('#dashboard-data-count').text('');
            return;
        }

        var server_buckets = chart_data.buckets;
        console.log('[year-debug-6] server_buckets.length=' + server_buckets.length +
            ', first.start_iso=' + server_buckets[0].start_iso +
            ', last.end_iso=' + server_buckets[server_buckets.length - 1].end_iso);
        var chart_width = container.width();
        var chart_height = 200;
        var padding_left = 40;
        var padding_bottom = 28;
        var padding_top = 12;
        var padding_right = 8;

        var outcome_keys = ['ok', 'error', 'timeout', 'skipped_already_in_flight'];
        var bar_colors = dash.outcome_bar_colors;
        var labels = dash.outcome_labels;
        var hidden_outcomes = dash._get_hidden_outcomes();

        var _year_range_ms = dash._time_range_minutes * dash.config.ms_per_minute;
        var _is_year_range = _year_range_ms >= dash.config.ms_per_year;

        var buckets = [];

        if (_is_year_range) {
            // .. merge server buckets into 12 calendar months ..
            var _monthly = {};
            for (var sb_idx = 0; sb_idx < server_buckets.length; sb_idx++) {
                var sb_date = new Date(server_buckets[sb_idx].start_iso);
                var sb_month = sb_date.getMonth();
                if (!_monthly[sb_month]) {
                    _monthly[sb_month] = {ok: 0, error: 0, timeout: 0, skipped_already_in_flight: 0,
                        start: new Date(server_buckets[sb_idx].start_iso).getTime(), end: 0};
                }
                _monthly[sb_month].ok += server_buckets[sb_idx].ok;
                _monthly[sb_month].error += server_buckets[sb_idx].error;
                _monthly[sb_month].timeout += server_buckets[sb_idx].timeout;
                _monthly[sb_month].skipped_already_in_flight += server_buckets[sb_idx].skipped_already_in_flight;
                _monthly[sb_month].end = new Date(server_buckets[sb_idx].end_iso).getTime();
            }
            for (var month_idx = 0; month_idx < 12; month_idx++) {
                if (_monthly[month_idx]) {
                    buckets.push(_monthly[month_idx]);
                }
            }
        } else {
            var display_bucket_count = Math.min(60, Math.max(12, Math.floor(chart_width / 16)));
            var merge_factor = Math.max(1, Math.floor(server_buckets.length / display_bucket_count));
            for (var merge_index = 0; merge_index < server_buckets.length; merge_index += merge_factor) {
                var merged = {ok: 0, error: 0, timeout: 0, skipped_already_in_flight: 0, start: 0, end: 0};
                var merge_end = Math.min(merge_index + merge_factor, server_buckets.length);
                merged.start = new Date(server_buckets[merge_index].start_iso).getTime();
                merged.end = new Date(server_buckets[merge_end - 1].end_iso).getTime();
                for (var sub_index = merge_index; sub_index < merge_end; sub_index++) {
                    var source = server_buckets[sub_index];
                    merged.ok += source.ok;
                    merged.error += source.error;
                    merged.timeout += source.timeout;
                    merged.skipped_already_in_flight += source.skipped_already_in_flight;
                }
                buckets.push(merged);
            }
        }

        var bucket_count = buckets.length;

        console.log('[year-debug-4] first_bucket start=' + new Date(buckets[0].start).toISOString() +
            ', end=' + new Date(buckets[0].end).toISOString());
        console.log('[year-debug-5] last_bucket start=' + new Date(buckets[bucket_count - 1].start).toISOString() +
            ', end=' + new Date(buckets[bucket_count - 1].end).toISOString());

        console.log('[chart-debug] bucket config: server_buckets=' + server_buckets.length +
            ', merge_factor=' + merge_factor + ', display_bucket_count=' + display_bucket_count +
            ', merged_bucket_count=' + bucket_count);

        var total_exec_count = 0;
        for (var tc = 0; tc < buckets.length; tc++) {
            total_exec_count += buckets[tc].ok + buckets[tc].error + buckets[tc].timeout;
        }

        var _dbg_totals = [];
        for (var _dt = 0; _dt < buckets.length; _dt++) {
            _dbg_totals.push({i: _dt, ok: buckets[_dt].ok, error: buckets[_dt].error,
                timeout: buckets[_dt].timeout, skipped: buckets[_dt].skipped_already_in_flight,
                start: new Date(buckets[_dt].start).toISOString(), end: new Date(buckets[_dt].end).toISOString()});
        }
        console.log('[chart-debug] bucket totals: ' + JSON.stringify(_dbg_totals));

        var range_minutes = dash._time_range_minutes;
        var range_names = {5: '5 min', 15: '15 min', 30: '30 min', 60: '1 hour', 360: '6 hours', 1440: 'Today', 2880: 'Yesterday', 10080: 'This week', 43200: 'This month', 525600: 'This year'};
        var filtered_count_label = total_exec_count === 1
            ? '1 run'
            : kit.format_number_compact(total_exec_count) + ' runs';
        var filtered_count_full = total_exec_count === 1
            ? '1 run'
            : kit.format_number_full(total_exec_count) + ' runs';
        var range_label;
        if (range_minutes > 0 && range_names[range_minutes]) {
            range_label = range_names[range_minutes] + ' \u00b7 ' + filtered_count_label;
        } else {
            range_label = 'All \u00b7 ' + filtered_count_label;
        }
        $('#dashboard-data-count').text(range_label).attr(
            'title',
            (range_minutes > 0 && range_names[range_minutes] ? range_names[range_minutes] : 'All') +
            ' \u00b7 ' + filtered_count_full
        );

        if (total_exec_count === 0) {
            container.html('<div class="dashboard-no-data">No run history yet</div>');
            $('#dashboard-chart-legend').empty();
            return;
        }

        var min_time = buckets[0].start;
        var max_time = buckets[bucket_count - 1].end;
        var time_range = max_time - min_time;
        if (time_range === 0) {
            time_range = 3600000;
            min_time = max_time - time_range;
        }

        console.log('[chart-debug] time window: min_time=' + new Date(min_time).toISOString() +
            ', max_time=' + new Date(max_time).toISOString() +
            ', time_range_ms=' + time_range);

        var visible_keys = [];
        for (var vk = 0; vk < outcome_keys.length; vk++) {
            if (hidden_outcomes[outcome_keys[vk]]) continue;
            var has_data = false;
            for (var hd = 0; hd < buckets.length; hd++) {
                if (buckets[hd][outcome_keys[vk]] > 0) { has_data = true; break; }
            }
            if (has_data) visible_keys.push(outcome_keys[vk]);
        }

        var max_stack = 0;
        if (dash.show_bars) {
            for (var ms_index = 0; ms_index < buckets.length; ms_index++) {
                var ms_sum = 0;
                for (var ms_key = 0; ms_key < visible_keys.length; ms_key++) {
                    ms_sum += buckets[ms_index][visible_keys[ms_key]];
                }
                if (ms_sum > max_stack) max_stack = ms_sum;
            }
        } else {
            for (var ms_index2 = 0; ms_index2 < buckets.length; ms_index2++) {
                for (var ms_key2 = 0; ms_key2 < visible_keys.length; ms_key2++) {
                    var ms_val = buckets[ms_index2][visible_keys[ms_key2]];
                    if (ms_val > max_stack) max_stack = ms_val;
                }
            }
        }
        if (max_stack === 0) max_stack = 1;

        console.log('[chart-debug] scaling: max_stack=' + max_stack +
            ', visible_keys=' + JSON.stringify(visible_keys) +
            ', chart_width=' + chart_width + ', total_exec_count=' + total_exec_count);

        var draw_width = chart_width - padding_left - padding_right;
        var draw_height = chart_height - padding_top - padding_bottom;
        var baseline_y = padding_top + draw_height;

        var svg = '<svg width="' + chart_width + '" height="' + chart_height + '" xmlns="http://www.w3.org/2000/svg">';

        svg += '<defs>';
        for (var gd = 0; gd < visible_keys.length; gd++) {
            var gd_key = visible_keys[gd];
            svg += '<linearGradient id="areaGrad_' + gd_key + '" x1="0" y1="0" x2="0" y2="1">';
            svg += '<stop offset="0" stop-color="' + bar_colors[gd_key] + '" stop-opacity="0.10"/>';
            svg += '<stop offset="0.5" stop-color="' + bar_colors[gd_key] + '" stop-opacity="0.03"/>';
            svg += '<stop offset="1" stop-color="' + bar_colors[gd_key] + '" stop-opacity="0.0"/>';
            svg += '</linearGradient>';
        }
        svg += '</defs>';

        var _y_axis_values = [];
        var grid_line_count = Math.min(4, max_stack);
        var prev_grid_value = -1;
        for (var grid_index = 0; grid_index <= grid_line_count; grid_index++) {
            var grid_y = padding_top + draw_height - (grid_index / grid_line_count) * draw_height;
            var grid_value = Math.round((grid_index / grid_line_count) * max_stack);
            svg += '<line x1="' + padding_left + '" y1="' + grid_y.toFixed(1) + '" ';
            svg += 'x2="' + (chart_width - padding_right) + '" y2="' + grid_y.toFixed(1) + '" ';
            svg += 'stroke="rgba(0,0,0,0.05)" stroke-width="1" />';
            if (grid_value !== prev_grid_value) {
                svg += '<text x="' + (padding_left - 6) + '" y="' + (grid_y + 3).toFixed(1) + '" ';
                svg += 'text-anchor="end" font-size="10" fill="rgba(0,0,0,0.35)" font-family="Menlo, Consolas, Monaco, monospace">';
                svg += grid_value + '</text>';
                _y_axis_values.push(grid_value);
                prev_grid_value = grid_value;
            }
        }

        var bucket_slot_width = draw_width / bucket_count;
        console.log('[year-debug-8] bucket_slot_width=' + bucket_slot_width.toFixed(2) +
            ', draw_width=' + draw_width + ', chart_width=' + chart_width +
            ', padding_left=' + padding_left + ', padding_right=' + padding_right);
        var group_padding = bucket_slot_width * 0.15;
        var group_width = bucket_slot_width - group_padding * 2;
        var num_visible = visible_keys.length;
        var bar_gap = Math.max(1, group_width * 0.06);
        var bar_width = (group_width - bar_gap * (num_visible - 1)) / num_visible;

        var layer_points = {};

        for (var layer = 0; layer < visible_keys.length; layer++) {
            var layer_key = visible_keys[layer];
            layer_points[layer_key] = [];

            for (var bi = 0; bi < bucket_count; bi++) {
                var val = buckets[bi][layer_key];
                var bar_h = val > 0 ? Math.max(2, (val / max_stack) * draw_height) : 0;
                var bar_x = padding_left + bi * bucket_slot_width + group_padding + layer * (bar_width + bar_gap);
                var bar_y = baseline_y - bar_h;
                layer_points[layer_key].push({
                    x: bar_x + bar_width / 2,
                    y: val > 0 ? bar_y : baseline_y,
                    val: val
                });
            }
        }

        if (dash.show_bars) {
            var sb_inset = Math.max(1, bucket_slot_width * 0.1);
            var sb_w = bucket_slot_width - sb_inset * 2;
            var sb_sep = 1.5;

            for (var sk = 0; sk < visible_keys.length; sk++) {
                layer_points[visible_keys[sk]] = [];
            }

            for (var sbi = 0; sbi < bucket_count; sbi++) {
                var sb_x = padding_left + sbi * bucket_slot_width + sb_inset;
                var sb_cursor_y = baseline_y;

                for (var sk2 = 0; sk2 < visible_keys.length; sk2++) {
                    var sk_key = visible_keys[sk2];
                    var sk_val = buckets[sbi][sk_key];
                    var sk_h = sk_val > 0 ? Math.max(2, (sk_val / max_stack) * draw_height) : 0;

                    if (sk_val > 0) {
                        var seg_y = sb_cursor_y - sk_h;
                        svg += '<rect x="' + sb_x.toFixed(1) + '" y="' + seg_y.toFixed(1) + '" ';
                        svg += 'width="' + sb_w.toFixed(1) + '" height="' + sk_h.toFixed(1) + '" ';
                        svg += 'fill="' + bar_colors[sk_key] + '" />';
                        sb_cursor_y = seg_y - sb_sep;
                    }

                    layer_points[sk_key].push({
                        x: sb_x + sb_w / 2,
                        y: sk_val > 0 ? sb_cursor_y + sb_sep : baseline_y,
                        val: sk_val
                    });
                }
            }
        }

        var _dbg_pixels = {};
        for (var _dpk = 0; _dpk < visible_keys.length; _dpk++) {
            var _dpkey = visible_keys[_dpk];
            _dbg_pixels[_dpkey] = layer_points[_dpkey].map(function(p) { return {x: +p.x.toFixed(1), y: +p.y.toFixed(1), val: p.val}; });
        }
        console.log('[chart-debug] pixel positions: ' + JSON.stringify(_dbg_pixels));

        if (!dash.show_bars) {
            var edge_left = padding_left;
            var edge_right = padding_left + draw_width;

            for (var spline_layer = 0; spline_layer < visible_keys.length; spline_layer++) {
                var spline_key = visible_keys[spline_layer];
                var data_pts = [];
                for (var si = 0; si < bucket_count; si++) {
                    var sx = padding_left + (si + 0.5) * bucket_slot_width;
                    var sv = buckets[si][spline_key];
                    var sy = sv > 0 ? baseline_y - Math.max(2, (sv / max_stack) * draw_height) : baseline_y;
                    data_pts.push({x: sx, y: sy, bucket_index: si});
                }

                var spline_pts = [];
                spline_pts.push({x: edge_left, y: data_pts[0].y});
                for (var dp = 0; dp < data_pts.length; dp++) {
                    spline_pts.push(data_pts[dp]);
                }
                spline_pts.push({x: edge_right, y: data_pts[data_pts.length - 1].y});

                layer_points[spline_key] = [];
                for (var spi = 0; spi < bucket_count; spi++) {
                    var hover_val = buckets[spi][spline_key];
                    var hover_y = hover_val > 0 ? baseline_y - (hover_val / max_stack) * draw_height : baseline_y;
                    layer_points[spline_key].push({x: data_pts[spi].x, y: hover_y, val: hover_val});
                }

                var area_path = dash.buildMonotoneCubicPath(spline_pts);
                var area_fill = area_path +
                    ' L' + edge_right.toFixed(1) + ',' + baseline_y.toFixed(1) +
                    ' L' + edge_left.toFixed(1) + ',' + baseline_y.toFixed(1) + ' Z';

                svg += '<path d="' + area_fill + '" fill="url(#areaGrad_' + spline_key + ')" />';
                svg += '<path d="' + area_path + '" fill="none" stroke="' + bar_colors[spline_key] + '" stroke-width="1.5" stroke-opacity="0.6" stroke-linecap="round" stroke-linejoin="round" />';

                var tip_cx = edge_right;
                var tip_cy = data_pts[data_pts.length - 1].y;
                var tip_color = bar_colors[spline_key];
                svg += '<circle cx="' + tip_cx.toFixed(2) + '" cy="' + tip_cy.toFixed(2) + '" r="5.5" ';
                svg += 'fill="none" stroke="' + tip_color + '" stroke-opacity="0.35" stroke-width="1"/>';
                svg += '<circle cx="' + tip_cx.toFixed(2) + '" cy="' + tip_cy.toFixed(2) + '" r="3.5" ';
                svg += 'fill="' + tip_color + '"/>';
            }
        }

        var label_range = dash._time_range_minutes > 0
            ? dash._time_range_minutes * dash.config.ms_per_minute
            : time_range;
        var _x_axis_labels = [];
        var label_count = Math.min(6, bucket_count);
        var label_step = Math.max(1, Math.floor(bucket_count / label_count));
        for (var label_index = 0; label_index < bucket_count; label_index += label_step) {
            var label_x = padding_left + (label_index + 0.5) * bucket_slot_width;
            var label_date = new Date(buckets[label_index].start);
            var label_text = dash.formatTimeLabel(label_date, label_range);
            _x_axis_labels.push(label_text);
            svg += '<text x="' + label_x.toFixed(1) + '" y="' + (chart_height - 6) + '" text-anchor="middle" ';
            svg += 'font-size="10" fill="rgba(0,0,0,0.35)" font-family="Menlo, Consolas, Monaco, monospace">' + label_text + '</text>';
        }

        // .. always emit the final time label at the right edge ..
        var final_label_x = chart_width - padding_right;
        var final_label_date = new Date(buckets[bucket_count - 1].start);
        var final_label_text = dash.formatTimeLabel(final_label_date, label_range);
        _x_axis_labels.push(final_label_text);
        svg += '<text x="' + final_label_x.toFixed(1) + '" y="' + (chart_height - 6) + '" text-anchor="end" ';
        svg += 'font-size="10" fill="rgba(0,0,0,0.35)" font-family="Menlo, Consolas, Monaco, monospace">' + final_label_text + '</text>';

        // .. store visible chart state for the copy button ..
        dash._copy_data = {
            y_axis: _y_axis_values,
            x_axis: _x_axis_labels,
            datapoints: []
        };
        for (var cp = 0; cp < buckets.length; cp++) {
            var cp_date = new Date(buckets[cp].start);
            dash._copy_data.datapoints.push({
                label: dash.formatTimeLabel(cp_date, label_range),
                ok: buckets[cp].ok,
                error: buckets[cp].error,
                timeout: buckets[cp].timeout,
                skipped: buckets[cp].skipped_already_in_flight
            });
        }

        svg += '</svg>';
        container.html(svg);

        dash._setup_chart_interactions(container, buckets, padding_left, draw_width, bucket_count, padding_top, draw_height, padding_bottom, chart_height, visible_keys, layer_points, bar_colors);

        kit.build_legend({
            container: '#dashboard-chart-legend',
            series_keys: outcome_keys,
            palette: bar_colors,
            labels: labels,
            text_colors: dash.outcome_colors,
            backgrounds: dash.outcome_backgrounds,
            hidden: hidden_outcomes,
            on_toggle: function(_key, h) {
                dash._set_hidden_outcomes(h);
                dash._redraw_chart_from_cache();
            }
        }, dash._skip_legend_rebuild);
        console.log('[render_bar_chart] completed in ' + (performance.now() - _bar_t0).toFixed(0) + 'ms');
    };

    // ////////////////////////////////////////////////////////////////////////
    // Chart interactions (crosshair + tooltip)
    // ////////////////////////////////////////////////////////////////////////

    dash._setup_chart_interactions = function(container, buckets, padding_left, draw_width, bucket_count, padding_top, draw_height, padding_bottom, chart_height, visible_keys, layer_points, bar_colors) {
        var chart_svg = container.find('svg');
        var labels = dash.outcome_labels;

        var overlay = container.find('.dashboard-chart-overlay');
        if (overlay.length === 0) {
            container.css('position', 'relative');
            container.append('<div class="dashboard-chart-overlay"></div>');
            overlay = container.find('.dashboard-chart-overlay');
        }
        overlay.css({position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', 'pointer-events': 'none'});

        var tooltip = $('#dashboard-chart-tooltip');
        if (tooltip.length === 0) {
            $('body').append('<div id="dashboard-chart-tooltip" class="kit-tooltip"></div>');
            tooltip = $('#dashboard-chart-tooltip');
        }

        var bucket_width_px = draw_width / bucket_count;

        chart_svg.off('mousemove.chart mouseleave.chart');

        chart_svg.on('mousemove.chart', function(event) {
            var rect = this.getBoundingClientRect();
            var mouse_x = event.clientX - rect.left;
            var relative_x = mouse_x - padding_left;

            if (relative_x < 0 || relative_x > draw_width) {
                overlay.empty();
                tooltip.css('display', 'none');
                return;
            }

            var bucket_index = Math.floor((relative_x / draw_width) * bucket_count);
            if (bucket_index >= bucket_count) bucket_index = bucket_count - 1;
            if (bucket_index < 0) bucket_index = 0;

            var band_left = padding_left + bucket_index * bucket_width_px;
            var band_html = '<svg style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none" xmlns="http://www.w3.org/2000/svg">';
            band_html += '<rect x="' + band_left.toFixed(1) + '" y="' + padding_top + '" width="' + bucket_width_px.toFixed(1) + '" height="' + draw_height + '" fill="rgba(0,0,0,0.06)" rx="2" />';

            for (var dk = 0; dk < visible_keys.length; dk++) {
                var dk_key = visible_keys[dk];
                var pts = layer_points[dk_key];
                if (pts && pts[bucket_index] && pts[bucket_index].val > 0) {
                    var pt = pts[bucket_index];
                    var dot_color_main = bar_colors[dk_key];
                    band_html += '<circle cx="' + pt.x.toFixed(1) + '" cy="' + pt.y.toFixed(1) + '" r="5.5" fill="none" stroke="' + dot_color_main + '" stroke-opacity="0.35" stroke-width="1" />';
                    band_html += '<circle cx="' + pt.x.toFixed(1) + '" cy="' + pt.y.toFixed(1) + '" r="3.5" fill="' + dot_color_main + '" />';
                }
            }
            band_html += '</svg>';
            overlay.html(band_html);

            var bucket = buckets[bucket_index];
            var time_start = new Date(bucket.start);
            var time_end = new Date(bucket.end);
            var fmt_time = function(d) {
                return ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2) + ':' + ('0' + d.getSeconds()).slice(-2);
            };
            var bucket_span_s = Math.round((bucket.end - bucket.start) / 1000);
            var time_label = bucket_span_s >= 1
                ? fmt_time(time_start) + ' \u2192 ' + fmt_time(time_end)
                : fmt_time(time_start);

            var total_runs = 0;
            for (var tk = 0; tk < visible_keys.length; tk++) {
                total_runs += bucket[visible_keys[tk]];
            }
            var runs_label = total_runs === 1
                ? '1 run'
                : kit.format_number_full(total_runs) + ' runs';

            var tooltip_html = '<div class="dashboard-tooltip-header">' +
                '<div class="dashboard-tooltip-title">' + time_label + '</div>' +
                '<div class="dashboard-tooltip-subtitle">' + runs_label + '</div>' +
                '</div>';

            var body_lines = [];
            for (var key_index = 0; key_index < visible_keys.length; key_index++) {
                var key = visible_keys[key_index];
                var count = bucket[key];
                var chart_run_word = count === 1 ? 'run' : 'runs';
                body_lines.push('<div class="dashboard-tooltip-row">' +
                    '<span class="dashboard-tooltip-dot" style="background:' + bar_colors[key] + '"></span>' +
                    labels[key] + ': <b>' + kit.format_number_full(count) + '</b> ' + chart_run_word + '</div>');
            }
            tooltip_html += '<div class="dashboard-tooltip-body">' + body_lines.join('') + '</div>';

            tooltip.html(tooltip_html);
            tooltip.css({display: 'block', left: '0px', top: '0px'});
            var mc_tt_w = tooltip.outerWidth();
            var mc_tt_h = tooltip.outerHeight();
            var mc_margin = 8;
            var mc_viewport_w = $(window).width();
            var mc_viewport_h = $(window).height();
            var mc_left = event.clientX + 14;
            var mc_top = event.clientY - 14;
            if (mc_left + mc_tt_w + mc_margin > mc_viewport_w) {
                mc_left = event.clientX - mc_tt_w - 14;
            }
            if (mc_left < mc_margin) mc_left = mc_margin;
            if (mc_top + mc_tt_h + mc_margin > mc_viewport_h) {
                mc_top = mc_viewport_h - mc_tt_h - mc_margin;
            }
            if (mc_top < mc_margin) mc_top = mc_margin;
            tooltip.css({left: mc_left + 'px', top: mc_top + 'px'});
        });

        chart_svg.on('mouseleave.chart', function() {
            overlay.empty();
            tooltip.css('display', 'none');
        });
    };

    // ////////////////////////////////////////////////////////////////////////
    // Render job table
    // ////////////////////////////////////////////////////////////////////////

    dash.render_job_table = function(jobs) {
        if (!dash.config.show_live_status) {
            $('.dashboard-th-dot').hide();
        }
        var table_body = $('#dashboard-job-table-body');
        table_body.empty();

        if (!jobs || jobs.length === 0) {
            table_body.append('<tr><td colspan="5" class="dashboard-no-data">No jobs</td></tr>');
            $('#dashboard-jobs-count').text('');
            return;
        }

        var cluster_id = dash.config.cluster_id;

        kit.set_number($('#dashboard-jobs-count'), jobs.length);

        jobs.sort(function(first, second) {
            return first.name.localeCompare(second.name);
        });

        for (var job_index = 0; job_index < jobs.length; job_index++) {
            var job = jobs[job_index];
            var next_run_text = kit.relative_time_future(job.next_fire_utc);
            var next_run_tooltip = kit.format_local_time(job.next_fire_utc);
            var detail_url = kit.urls.object_detail(job.id, {outcomes: dash.Outcome_All});

            var service_name = job.service;
            var service_cell = service_name ? $.fn.zato.data_table.service_text(service_name, cluster_id) : '';

            var row = '<tr data-href="' + detail_url + '">';
            var status = dash.status_dot(job);
            row += '<td class="dashboard-td-dot" data-tippy-content="' + status.tooltip + '" data-tippy-placement="left"' +
                (dash.config.show_live_status ? '' : ' style="display:none"') + '>' + status.html + '</td>';
            row += '<td><a href="' + detail_url + '">' + job.name + '</a></td>';
            row += '<td>' + service_cell + '</td>';
            row += '<td data-countdown-target="' + (job.next_fire_utc || '') + '" style="font-family:monospace;font-feature-settings:\'tnum\' on;color:#6e6e73" title="' + next_run_tooltip + '">' + next_run_text + '</td>';
            row += '<td>' + dash.outcome_squares(job.recent_outcomes) + '</td>';
            row += '</tr>';
            table_body.append(row);
        }

        tippy(table_body.find('td[data-tippy-content]').toArray(), {
            allowHTML: false,
            theme: 'dark',
            arrow: true
        });

        tippy(table_body.find('.dashboard-outcome-squares-group[data-tippy-content]').toArray(), {
            allowHTML: true,
            theme: 'dark',
            arrow: true
        });

        table_body.find('tr[data-href]').on('click', function(event) {
            if ($(event.target).is('a')) return;
            window.location.href = $(this).data('href');
        });

        kit.sortable_headers('#dashboard-job-table', {'Job name': 1, 'Service': 2});
    };

    // ////////////////////////////////////////////////////////////////////////
    // Render recent runs table (capped to 100 rows, with Run number column)
    // ////////////////////////////////////////////////////////////////////////

    dash.render_recent = function(timeline, jobs) {
        var container = $('#dashboard-recent-body');
        container.find('.dashboard-outcome-badge').each(function() {
            if (this._tippy) {
                this._tippy.destroy();
            }
        });
        container.empty();

        if (!timeline || timeline.length === 0) {
            container.html('<div class="dashboard-no-data">No recent runs</div>');
            $('#dashboard-recent-count').text('0');
            return;
        }

        var cluster_id = dash.config.cluster_id;

        var job_service = {};
        if (jobs) {
            for (var ji = 0; ji < jobs.length; ji++) {
                job_service[jobs[ji].id] = jobs[ji].service;
            }
        }

        var exec_count = 0;
        for (var idx = 0; idx < timeline.length; idx++) {
            var outcome = timeline[idx].outcome;
            if (outcome === 'ok' || outcome === 'error' || outcome === 'timeout') {
                exec_count++;
            }
        }
        kit.set_number($('#dashboard-recent-count'), exec_count);

        var html = '<table class="zato-table"><thead><tr>';
        html += '<th>Run</th><th>Time</th><th>Job name</th><th>Service</th><th>Outcome</th>';
        html += '</tr></thead><tbody>';

        var max_rows = Math.min(100, timeline.length);
        for (var row_index = 0; row_index < max_rows; row_index++) {
            var entry = timeline[row_index];
            var time_text = kit.relative_time_past(entry.actual_fire_time_iso);
            var time_tooltip = kit.format_local_time(entry.actual_fire_time_iso);
            var run_number = entry.current_run !== undefined ? entry.current_run : '';

            var row_ts = entry.actual_fire_time_iso;
            html += '<tr data-ts="' + row_ts + '">';
            var run_href = kit.urls.run_detail(entry.job_id, entry.current_run, {outcomes: dash.Outcome_All});
            html += '<td style="font-family:monospace;font-feature-settings:\'tnum\' on;text-align:left"><a href="' + run_href + '">' + run_number + '</a></td>';
            html += '<td style="font-family:monospace;font-feature-settings:\'tnum\' on;color:#6e6e73;white-space:nowrap" title="' + time_tooltip + '">' + time_text + '</td>';
            var service_cell = $.fn.zato.data_table.service_text(job_service[entry.job_id], cluster_id);
            html += '<td><a href="' + kit.urls.object_detail(entry.job_id, {outcomes: dash.Outcome_All}) + '">' + entry.job_name + '</a></td>';
            html += '<td>' + service_cell + '</td>';
            html += '<td>' + kit.outcome.badge(entry.outcome, dash.outcome_palette, entry) + '</td>';
            html += '</tr>';
        }

        html += '</tbody></table>';
        container.html(html);

        kit.sortable_headers(container.find('table'), {'Job name': 2, 'Service': 3});

        kit.stabilize_badge_column({
            palette: {
                colors: dash.outcome_colors,
                backgrounds: dash.outcome_backgrounds,
                labels: dash.outcome_labels,
                short_labels: dash.outcome_short_labels
            },
            spinner_key: 'running',
            th_selector: '#dashboard-recent-body thead th:last-child'
        });

        container.find('.dashboard-outcome-badge[data-tippy-content]').each(function() {
            if (!this._tippy) {
                tippy(this, {placement: 'top', delay: [0, 0], theme: 'dark'});
            }
        });

        var initial_ts = [];
        for (var fi = 0; fi < max_rows && fi < kit.recency.STEPS; fi++) {
            initial_ts.push(timeline[fi].actual_fire_time_iso);
        }
        dash._recent_runs_ts = initial_ts;
        kit.recency.apply({
            container: '#dashboard-recent-body tbody',
            recent_ts: initial_ts,
            rgb: dash.theme.row_recency_color
        });
    };

    // ////////////////////////////////////////////////////////////////////////
    // Render upcoming runs table (capped to 100 rows, projects future fires)
    // ////////////////////////////////////////////////////////////////////////

    dash.render_upcoming_table = function(jobs) {
        var table_body = $('#dashboard-upcoming-table-body');
        table_body.empty();

        if (!jobs || jobs.length === 0) {
            table_body.append('<tr><td colspan="3" class="dashboard-no-data">No upcoming runs</td></tr>');
            $('#dashboard-upcoming-count').text('0');
            return;
        }

        var cluster_id = dash.config.cluster_id;

        var upcoming = [];

        for (var job_index = 0; job_index < jobs.length; job_index++) {
            var job = jobs[job_index];
            if (!job.is_active || !job.next_fire_utc) continue;

            upcoming.push({
                time: job.next_fire_utc,
                name: job.name,
                service: job.service,
                job_id: job.id
            });

            if (job.interval_ms && job.interval_ms > 0) {
                var run_time = new Date(job.next_fire_utc).getTime();
                var interval = parseInt(job.interval_ms, 10);
                for (var projection_index = 1; projection_index < dash.config.max_upcoming_rows; projection_index++) {
                    var projected_time = run_time + (projection_index * interval);
                    upcoming.push({
                        time: new Date(projected_time).toISOString(),
                        name: job.name,
                        service: job.service,
                        job_id: job.id
                    });
                }
            }
        }

        upcoming.sort(function(first, second) {
            return first.time.localeCompare(second.time);
        });

        var max_upcoming = Math.min(dash.config.max_upcoming_rows, upcoming.length);
        $('#dashboard-upcoming-count').text(upcoming.length);
        if (max_upcoming === 0) {
            table_body.append('<tr><td colspan="3" class="dashboard-no-data">No upcoming runs</td></tr>');
            return;
        }

        for (var upcoming_index = 0; upcoming_index < max_upcoming; upcoming_index++) {
            var entry = upcoming[upcoming_index];
            var time_text = kit.relative_time_future(entry.time);
            var time_tooltip = kit.format_local_time(entry.time);

            var service_cell = entry.service ? $.fn.zato.data_table.service_text(entry.service, cluster_id) : '';

            var row = '<tr data-ts="' + entry.time + '">';
            row += '<td data-countdown-target="' + entry.time + '" style="font-family:monospace;font-feature-settings:\'tnum\' on;color:#6e6e73;white-space:nowrap" title="' + time_tooltip + '">' + time_text + '</td>';
            row += '<td><a href="' + kit.urls.object_detail(entry.job_id, {outcomes: dash.Outcome_All}) + '">' + entry.name + '</a></td>';
            row += '<td>' + service_cell + '</td>';
            row += '</tr>';
            table_body.append(row);
        }

        kit.sortable_headers('#dashboard-upcoming-table', {'Job name': 1, 'Service': 2});

        var upcoming_ts = [];
        for (var ri = 0; ri < max_upcoming && ri < kit.recency.STEPS; ri++) {
            upcoming_ts.push(upcoming[ri].time);
        }
        kit.recency.apply({
            container: '#dashboard-upcoming-table-body',
            recent_ts: upcoming_ts,
            rgb: dash.theme.row_recency_color
        });
    };

    // ////////////////////////////////////////////////////////////////////////
    // Main render
    // ////////////////////////////////////////////////////////////////////////

    dash.render = function(data) {
        if (!data || !data.outcome_counts) return;
        console.log('[render] chart_buckets.buckets=' + (data.chart_buckets && data.chart_buckets.buckets ? data.chart_buckets.buckets.length : 'none') +
            ', recent_events=' + (data.recent_events ? data.recent_events.length : 'none'));

        var total_jobs = data.total_jobs;
        var active_jobs = data.active_jobs;
        var paused_jobs = data.paused_jobs;

        var outcome_counts = data.outcome_counts;
        var recent_lifetime = outcome_counts['error'] + outcome_counts['timeout'];

        var buffers = dash._spark_buffers;
        buffers.seed_flat({
            total_jobs: total_jobs,
            active: active_jobs,
            paused: paused_jobs
        });

        buffers.push('total_jobs', total_jobs);
        buffers.push('active', active_jobs);
        buffers.push('paused', paused_jobs);

        var chart_data = data.chart_buckets;
        var recent_events = data.recent_events;

        var runs_last_hour = data.runs_last_hour;
        var recent_last_hour = data.recent_last_hour;

        buffers.push('runs', runs_last_hour);
        buffers.push('recent', recent_last_hour);

        kit.set_number($('#stat-total-jobs'), total_jobs);
        kit.set_number($('#stat-active'), active_jobs);
        kit.set_number($('#stat-paused'), paused_jobs);
        kit.set_number($('#stat-runs'), runs_last_hour);
        kit.set_number($('#stat-recent'), recent_last_hour);

        if (recent_last_hour > 0) {
            $('#stat-recent').css('color', '#ff6b6b');
        } else {
            $('#stat-recent').css('color', '#fff');
        }

        var runs_sub = kit.format_number_compact(data.total_executions) + ' total';
        $('#stat-runs-sublabel')
            .text(runs_sub)
            .attr('title', kit.format_number_full(data.total_executions) + ' total');
        var recent_sub = kit.format_number_compact(recent_lifetime) + ' total';
        $('#stat-recent-sublabel')
            .text(recent_sub)
            .attr('title', kit.format_number_full(recent_lifetime) + ' total');

        var _theme = dash.theme;
        var base_spark = {height: 36, color: _theme.spark_color, dot_color: _theme.spark_color, dot_radius: 3.5};
        var base_spark_err = {height: 36, color: _theme.spark_err, dot_color: _theme.spark_err, dot_radius: 3.5};

        var tile_specs = [
            {sel: '#spark-total-jobs', key: 'total_jobs', opts: base_spark, dot_style: 'filled_halo'},
            {sel: '#spark-active', key: 'active', opts: base_spark, dot_style: 'filled_halo'},
            {sel: '#spark-paused', key: 'paused', opts: base_spark, dot_style: 'filled_halo'},
            {sel: '#spark-runs', key: 'runs', opts: base_spark, dot_style: 'filled_halo'},
            {sel: '#spark-recent', key: 'recent', opts: base_spark_err, dot_style: 'filled_halo'}
        ];

        for (var tile_i = 0; tile_i < tile_specs.length; tile_i++) {
            var spec = tile_specs[tile_i];
            var merged = $.extend({}, spec.opts, {dot_style: spec.dot_style});
            var values = buffers.values(spec.key);
            kit.sparkline.render(spec.sel, values, merged);
        }

        if (dash._stat_tile_handle) {
            dash._stat_tile_handle.bind();
        }

        dash._last_jobs = data.jobs;

        if (recent_events && recent_events.length > 0) {
            if (dash._last_event_ts) {
                var new_events = [];
                for (var ne = 0; ne < recent_events.length; ne++) {
                    if (recent_events[ne].actual_fire_time_iso > dash._last_event_ts) {
                        new_events.push(recent_events[ne]);
                    }
                }
                if (new_events.length > 0) {
                    dash._last_recent_events = new_events.concat(dash._last_recent_events);
                    if (dash._last_recent_events.length > 200) {
                        dash._last_recent_events.length = 200;
                    }
                }
            } else {
                dash._last_recent_events = recent_events;
            }
            dash._last_event_ts = dash._last_recent_events[0].actual_fire_time_iso;
        }

        dash.render_bar_chart(chart_data);
        dash.render_job_table(data.jobs);
        var filtered_recent = dash._filter_recent_by_range(dash._last_recent_events);
        dash.render_recent(filtered_recent, data.jobs);
        dash.render_upcoming_table(data.jobs);

        kit.lock_table_widths('#dashboard-job-table');
        kit.lock_table_widths('#dashboard-upcoming-table');
        kit.lock_table_widths('#dashboard-recent-body table');

    };

    // ////////////////////////////////////////////////////////////////////////
    // Poll
    // ////////////////////////////////////////////////////////////////////////

    dash._fake_data = null;

    dash.poll = function() {
        if (dash._fake_data) {
            dash.render(dash._fake_data);
            return;
        }

        var old_run_ts = {};
        $('#dashboard-recent-body tr[data-ts]').each(function() {
            var ts = $(this).attr('data-ts');
            if (ts) old_run_ts[ts] = true;
        });
        var had_runs = Object.keys(old_run_ts).length > 0;

        var _chart_window = dash._get_chart_window();
        var post_data = {
            chart_since_iso: _chart_window.since_iso,
            chart_until_iso: _chart_window.until_iso,
            recent_since_iso: dash._last_event_ts
        };

        var _poll_t0 = performance.now();
        console.log('[poll] start, chart_since_iso=' + (post_data.chart_since_iso || '(all)') +
            ', chart_until_iso=' + (post_data.chart_until_iso || '(all)') +
            ', recent_since_iso=' + (post_data.recent_since_iso || '(none)'));
        console.log('[year-debug-10] _time_range_minutes=' + dash._time_range_minutes +
            ', chart_since_iso=' + JSON.stringify(post_data.chart_since_iso) +
            ', chart_until_iso=' + JSON.stringify(post_data.chart_until_iso));

        $.ajax({
            url: dash.config.base_url + 'poll/',
            type: 'POST',
            data: post_data,
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(data) {
                var _poll_t1 = performance.now();
                console.log('[poll] response received in ' + (_poll_t1 - _poll_t0).toFixed(0) + 'ms');
                if (typeof data === 'string') {
                    try { data = JSON.parse(data); } catch(parse_error) { return; }
                }
                var _render_t0 = performance.now();
                dash.render(data);
                console.log('[poll] render() took ' + (performance.now() - _render_t0).toFixed(0) + 'ms');

                if (had_runs) {
                    var new_list = [];
                    $('#dashboard-recent-body tr[data-ts]').each(function() {
                        var ts = $(this).attr('data-ts');
                        if (ts && !old_run_ts[ts]) {
                            new_list.push(ts);
                        }
                    });
                    if (new_list.length > 0) {
                        dash._recent_runs_ts = new_list.concat(dash._recent_runs_ts);
                        dash._recent_runs_ts.length = Math.min(dash._recent_runs_ts.length, kit.recency.STEPS);
                    }
                }
                kit.recency.apply({
                    container: '#dashboard-recent-body tbody',
                    recent_ts: dash._recent_runs_ts,
                    rgb: dash.theme.row_recency_color
                });
            },
            error: function() {}
        });
    };

    // ////////////////////////////////////////////////////////////////////////
    // Init
    // ////////////////////////////////////////////////////////////////////////

    dash._generate_fake_data = function() {
        var job_names = [
            "billing.invoice.generate", "billing.payment.reconcile", "billing.dunning.notify",
            "crm.contacts.sync", "crm.leads.score", "crm.deals.update", "crm.activity.aggregate",
            "erp.inventory.reorder", "erp.shipment.track", "erp.warehouse.sync",
            "reporting.daily.summary", "reporting.weekly.kpi", "reporting.monthly.revenue",
            "reporting.executive.brief", "reporting.compliance.audit",
            "monitoring.health.check", "monitoring.uptime.ping", "monitoring.latency.measure",
            "monitoring.disk.usage", "monitoring.memory.alert",
            "etl.salesforce.ingest", "etl.hubspot.sync", "etl.snowflake.load",
            "etl.postgres.replicate", "etl.redis.warmup", "etl.s3.archive",
            "notifications.email.digest", "notifications.slack.alert", "notifications.sms.reminder",
            "notifications.webhook.retry", "notifications.push.campaign",
            "security.cert.expiry.check", "security.token.rotate", "security.audit.log.export",
            "security.ip.blocklist.refresh", "security.vulnerability.scan",
            "cache.invalidate.stale", "cache.warmup.popular", "cache.redis.compact",
            "integration.sap.orders", "integration.oracle.sync", "integration.jira.issues",
            "integration.confluence.pages", "integration.github.webhooks",
            "data.cleanup.expired", "data.archive.old.records", "data.gdpr.anonymize",
            "data.backup.incremental", "data.index.rebuild",
            "scheduler.self.check", "scheduler.queue.drain", "scheduler.metrics.export",
            "api.rate.limit.reset", "api.quota.recalculate", "api.usage.aggregate",
            "workflow.approval.escalate", "workflow.sla.check", "workflow.timeout.sweep",
            "ml.model.retrain", "ml.predictions.batch", "ml.features.compute",
            "geo.coordinates.geocode", "geo.timezone.update", "geo.address.validate",
            "messaging.queue.dlq.retry", "messaging.topic.compact", "messaging.consumer.rebalance",
            "file.transfer.outbound", "file.transfer.inbound", "file.cleanup.temp",
            "auth.session.purge", "auth.mfa.sync"
        ];
        var svc = [
            "billing.services.InvoiceGenerator", "billing.services.PaymentReconciler", "billing.services.DunningNotifier",
            "crm.services.ContactSync", "crm.services.LeadScorer", "crm.services.DealUpdater", "crm.services.ActivityAggregator",
            "erp.services.InventoryReorder", "erp.services.ShipmentTracker", "erp.services.WarehouseSync",
            "reporting.services.DailySummary", "reporting.services.WeeklyKPI", "reporting.services.MonthlyRevenue",
            "reporting.services.ExecutiveBrief", "reporting.services.ComplianceAudit",
            "monitoring.services.HealthCheck", "monitoring.services.UptimePing", "monitoring.services.LatencyMeasure",
            "monitoring.services.DiskUsage", "monitoring.services.MemoryAlert",
            "etl.services.SalesforceIngest", "etl.services.HubspotSync", "etl.services.SnowflakeLoad",
            "etl.services.PostgresReplicate", "etl.services.RedisWarmup", "etl.services.S3Archive",
            "notifications.services.EmailDigest", "notifications.services.SlackAlert", "notifications.services.SMSReminder",
            "notifications.services.WebhookRetry", "notifications.services.PushCampaign",
            "security.services.CertExpiryCheck", "security.services.TokenRotator", "security.services.AuditLogExport",
            "security.services.IPBlocklistRefresh", "security.services.VulnerabilityScan",
            "cache.services.InvalidateStale", "cache.services.WarmupPopular", "cache.services.RedisCompact",
            "integration.services.SAPOrders", "integration.services.OracleSync", "integration.services.JiraIssues",
            "integration.services.ConfluencePages", "integration.services.GitHubWebhooks",
            "data.services.CleanupExpired", "data.services.ArchiveOldRecords", "data.services.GDPRAnonymize",
            "data.services.BackupIncremental", "data.services.IndexRebuild",
            "scheduler.services.SelfCheck", "scheduler.services.QueueDrain", "scheduler.services.MetricsExport",
            "api.services.RateLimitReset", "api.services.QuotaRecalculate", "api.services.UsageAggregate",
            "workflow.services.ApprovalEscalate", "workflow.services.SLACheck", "workflow.services.TimeoutSweep",
            "ml.services.ModelRetrain", "ml.services.PredictionsBatch", "ml.services.FeaturesCompute",
            "geo.services.Geocoder", "geo.services.TimezoneUpdate", "geo.services.AddressValidator",
            "messaging.services.DLQRetry", "messaging.services.TopicCompact", "messaging.services.ConsumerRebalance",
            "file.services.TransferOutbound", "file.services.TransferInbound", "file.services.CleanupTemp",
            "auth.services.SessionPurge", "auth.services.MFASync"
        ];
        var oc_pool = ["ok","ok","ok","ok","ok","ok","ok","ok","ok","ok","ok","ok","ok","ok","ok","ok","ok","ok","ok","skipped_already_in_flight"];
        var now = Date.now();
        var job_count = 79;
        var extra_names = [
            "payment.gateway.sync", "payment.refund.process", "payment.ledger.balance",
            "inventory.forecast.run", "inventory.recount.trigger",
            "compliance.pci.scan", "compliance.sox.report", "compliance.gdpr.check"
        ];
        var extra_svc = [
            "payment.services.GatewaySync", "payment.services.RefundProcessor", "payment.services.LedgerBalance",
            "inventory.services.ForecastRunner", "inventory.services.RecountTrigger",
            "compliance.services.PCIScan", "compliance.services.SOXReport", "compliance.services.GDPRCheck"
        ];
        var all_names = job_names.concat(extra_names);
        var all_svc = svc.concat(extra_svc);
        var jobs = [];
        for (var i = 0; i < job_count; i++) {
            var recent = [];
            for (var r = 0; r < Math.floor(Math.random() * 8) + 3; r++) {
                recent.push(oc_pool[Math.floor(Math.random() * oc_pool.length)]);
            }
            var is_running = i < 75;
            jobs.push({
                id: 1000 + i, name: all_names[i], service: all_svc[i],
                is_active: true, is_running: is_running,
                next_fire_utc: new Date(now + Math.floor(Math.random() * 600000) + 5000).toISOString(),
                interval_ms: (Math.floor(Math.random() * 12) + 1) * 30000,
                last_outcome: recent[0], recent_outcomes: recent
            });
        }
        var timeline = [];
        var run_id = 351000;
        for (var t = 0; t < 3700; t++) {
            var ji = Math.floor(Math.random() * job_count);
            var outcome = oc_pool[Math.floor(Math.random() * oc_pool.length)];
            var ago = Math.floor(Math.random() * 3600000);
            timeline.push({
                job_id: 1000 + ji, job_name: all_names[ji], current_run: run_id--,
                actual_fire_time_iso: new Date(now - ago).toISOString(),
                outcome: outcome, duration_ms: Math.floor(Math.random() * 2000) + 50,
                error: null
            });
        }
        timeline.sort(function(a, b) { return b.actual_fire_time_iso.localeCompare(a.actual_fire_time_iso); });
        var oc_counts = {ok: 0, error: 0, timeout: 0, running: 0, skipped_already_in_flight: 0};
        for (var c = 0; c < timeline.length; c++) {
            if (oc_counts[timeline[c].outcome] !== undefined) oc_counts[timeline[c].outcome]++;
        }

        var fake_buckets = [];
        var bucket_duration = 3600000 / 120;
        for (var fb = 0; fb < 120; fb++) {
            fake_buckets.push({
                start_iso: new Date(now - 3600000 + fb * bucket_duration).toISOString(),
                end_iso: new Date(now - 3600000 + (fb + 1) * bucket_duration).toISOString(),
                ok: Math.floor(Math.random() * 10),
                error: Math.random() < 0.1 ? Math.floor(Math.random() * 3) : 0,
                timeout: Math.random() < 0.05 ? 1 : 0,
                skipped_already_in_flight: Math.random() < 0.03 ? 1 : 0
            });
        }

        var recent_events = timeline.slice(0, 100);

        return {
            total_jobs: 79, active_jobs: 75, paused_jobs: 4,
            total_executions: 3700,
            outcome_counts: oc_counts, jobs: jobs,
            chart_buckets: {buckets: fake_buckets, min_time_iso: new Date(now - 3600000).toISOString(), max_time_iso: new Date(now).toISOString()},
            recent_events: recent_events
        };
    };

    dash.init = function(initial_data) {
        if (typeof initial_data === 'string') {
            try { initial_data = JSON.parse(initial_data); } catch(parse_error) { initial_data = {}; }
        }
        if (kit.needsTestData) {
            dash._fake_data = dash._generate_fake_data();
            initial_data = dash._fake_data;
            var _orig_render = dash.render;
            dash.render = function(data) {
                _orig_render(data);
                $('#stat-runs-sublabel').text('793k total').attr('title', '793,000 total');
            };
        }

        kit.urls.init({
            base_url: dash.config.base_url,
            cluster_id: dash.config.cluster_id,
            object_path: 'job/{id}/',
            run_path: 'job/{id}/run/{run_id}/',
            range_minutes: parseInt(new URLSearchParams(window.location.search).get('range'), 10)
        });

        $('#dashboard-hero-pill-group').hide();

        if (!dash.config.show_tab_counts) {
            $('.dashboard-tabs .dashboard-pill').hide();
        }

        // Chart type toggle
        dash.show_bars = false;
        var _icon_lines = '<svg width="18" height="14" viewBox="0 0 18 14" fill="none" xmlns="http://www.w3.org/2000/svg">' +
            '<path d="M1 12C3 8 5.5 2 9 4C12.5 6 14 10 17 1" stroke="#012845" stroke-width="1.8" stroke-linecap="round"/>' +
            '</svg>';
        var _icon_bars = '<svg width="18" height="14" viewBox="0 0 18 14" fill="none" xmlns="http://www.w3.org/2000/svg">' +
            '<rect x="1" y="6" width="3" height="8" rx="1" fill="#012845" fill-opacity="0.85"/>' +
            '<rect x="5.5" y="2" width="3" height="12" rx="1" fill="#012845" fill-opacity="0.85"/>' +
            '<rect x="10" y="8" width="3" height="6" rx="1" fill="#012845" fill-opacity="0.85"/>' +
            '<rect x="14.5" y="4" width="3" height="10" rx="1" fill="#012845" fill-opacity="0.85"/>' +
            '</svg>';

        var _update_chart_type_icon = function() {
            var toggle = $('#dashboard-chart-type-toggle');
            if (dash.show_bars) {
                toggle.html(_icon_lines);
                toggle.attr('title', 'Switch to area chart');
            } else {
                toggle.html(_icon_bars);
                toggle.attr('title', 'Switch to bar chart');
            }
        };

        try {
            var stored_bars = localStorage.getItem('zato_scheduler_show_bars');
            if (stored_bars === 'true') dash.show_bars = true;
        } catch(e) {}
        _update_chart_type_icon();

        $('#dashboard-chart-type-toggle').on('click', function() {
            dash.show_bars = !dash.show_bars;
            try { localStorage.setItem('zato_scheduler_show_bars', String(dash.show_bars)); } catch(e) {}
            _update_chart_type_icon();
            dash._redraw_chart_from_cache();
        });

        // Copy chart data to clipboard
        $('#dashboard-chart-copy').on('click', function() {
            if (!dash._copy_data) return;

            var range_minutes = dash._time_range_minutes;
            var range_names = {5: '5 min', 15: '15 min', 30: '30 min', 60: '1 hour', 360: '6 hours', 1440: 'Today', 2880: 'Yesterday', 10080: 'This week', 43200: 'This month', 525600: 'This year'};
            var range_label = (range_minutes > 0 && range_names[range_minutes]) ? range_names[range_minutes] : 'All';

            var out = {
                range: range_label,
                chart_type: dash.show_bars ? 'bar' : 'area',
                y_axis: dash._copy_data.y_axis,
                x_axis: dash._copy_data.x_axis,
                datapoints: dash._copy_data.datapoints
            };

            var text = JSON.stringify(out, null, 2);
            navigator.clipboard.writeText(text);

            var btn = document.getElementById('dashboard-chart-copy');
            if (btn._tippy) btn._tippy.destroy();
            tippy(btn, {
                content: 'Copied to clipboard',
                placement: 'top',
                trigger: 'manual',
                theme: 'dark',
                arrow: true
            });
            btn._tippy.show();
            setTimeout(function() {
                if (btn._tippy) {
                    btn._tippy.hide();
                    setTimeout(function() { if (btn._tippy) btn._tippy.destroy(); }, 200);
                }
            }, 600);
        });

        // Time range - from URL only (templates and redirects always supply range)
        dash._time_range_minutes = parseInt(new URLSearchParams(window.location.search).get('range'), 10);
        kit.urls.set_range_minutes(dash._time_range_minutes);

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
            console.log('[time-range] changed to ' + minutes + ' minutes');
            dash._time_range_minutes = minutes;
            kit.urls.set_range_minutes(minutes);
            var url = new URL(window.location.href);
            url.searchParams.set('range', minutes);
            window.history.replaceState(null, '', url.toString());
            menu.find('.dashboard-time-range-option').removeClass('dashboard-time-range-active');
            $(this).addClass('dashboard-time-range-active');
            menu.removeClass('dashboard-time-range-menu-open');
            dash._redraw_chart_from_cache();
            console.log('[time-range] triggering immediate poll');
            dash.poll();
        });

        $(document).on('click', function() {
            menu.removeClass('dashboard-time-range-menu-open');
        });

        // Wheel zoom
        

        // Stat tile hover — delegated to kit
        dash._stat_tile_handle = kit.stat_tile.init({
            tiles: [
                {sparkline_selector: '#spark-total-jobs', buffer_key: 'total_jobs', label: 'Total jobs', color: dash.theme.spark_color},
                {sparkline_selector: '#spark-active', buffer_key: 'active', label: 'Active', color: dash.theme.spark_color},
                {sparkline_selector: '#spark-paused', buffer_key: 'paused', label: 'Paused', color: dash.theme.spark_color},
                {sparkline_selector: '#spark-runs', buffer_key: 'runs', label: 'Runs', color: dash.theme.spark_color},
                {sparkline_selector: '#spark-recent', buffer_key: 'recent', label: 'Recent runs', color: dash.theme.spark_err}
            ],
            get_buffer: function(key) {
                return dash._spark_buffers.data(key);
            }
        });

        // Tabs - delegated to kit, synced to URL
        dash._tab_locked = false;
        dash._tabs_handle = kit.tabs.init({
            tab_selector: '.dashboard-card-activity .dashboard-tab',
            panel_prefix: 'dashboard-tab-panel-',
            default_tab: 'recent',
            on_change: function(tab_name) {
                dash._tab_locked = true;
                kit.url_state.set({tab: tab_name});
            }
        });

        var url_tab = kit.url_state.get('tab');
        if (url_tab) {
            dash._tab_locked = true;
            dash._tabs_handle.set_tab(url_tab, true);
        }

        dash.render(initial_data);
        kit.countdown.start();
        kit.reveal();

        dash._auto_refresh = kit.auto_refresh.init({
            pill: '#dashboard-refresh-pill',
            menu: '#dashboard-refresh-menu',
            storage_key: 'zato_scheduler_refresh',
            url_param: 'refresh',
            default_seconds: 5,
            on_tick: dash.poll
        });

        kit.url_state.on_pop(function(params) {
            var pop_tab = params.get('tab');
            if (pop_tab) {
                dash._tabs_handle.set_tab(pop_tab, true);
            }

            var refresh_val = parseInt(params.get('refresh'), 10);
            if (!isNaN(refresh_val)) {
                dash._auto_refresh.set_seconds(refresh_val);
            }
        });
    };

})();
