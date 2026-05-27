

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
    dash._chart_buckets = null;
    dash._chart_visible_keys = [];
    dash._chart_bar_colors = {};
    dash._chart_labels = {};

    // ////////////////////////////////////////////////////////////////////////
    // Grouping configuration - maps each group type to its key extractor,
    // label formatter, and y-axis suffix.
    // ////////////////////////////////////////////////////////////////////////

    dash.groupConfig = {

        minute: {
            suffix: '/min',
            extractKey: function(date) {
                return date.getMinutes();
            },
            formatLabel: function(date) {
                var paddedHours = ('0' + date.getHours()).slice(-2);
                var paddedMinutes = ('0' + date.getMinutes()).slice(-2);

                return paddedHours + ':' + paddedMinutes;
            }
        },

        hour: {
            suffix: '/hr',
            extractKey: function(date) {
                return date.getHours();
            },
            formatLabel: function(date) {

                // Build a label like "Sat 15:00 -> 16:00"
                var dayName = dash.config.day_names[date.getDay()];

                // .. format the current hour with zero-padding ..
                var currentHour = date.getHours();
                var paddedCurrentHour = ('0' + currentHour).slice(-2);

                // .. compute and format the next hour, wrapping at midnight.
                var nextHour = (currentHour + 1) % 24;
                var paddedNextHour = ('0' + nextHour).slice(-2);

                return dayName + ' ' + paddedCurrentHour + ':00 \u2192 ' + paddedNextHour + ':00';
            }
        },

        day: {
            suffix: '/day',
            extractKey: function(date) {
                return date.getDate();
            },
            formatLabel: function(date) {
                var dayName = dash.config.day_names[date.getDay()];
                var monthName = dash.config.month_names[date.getMonth()];
                var dayOfMonth = date.getDate();

                return dayName + ' ' + monthName + ' ' + dayOfMonth;
            }
        },

        month: {
            suffix: '/mo',
            extractKey: function(date) {
                return date.getMonth();
            },
            formatLabel: function(date) {
                var monthName = dash.config.month_names[date.getMonth()];
                var shortYear = String(date.getFullYear()).slice(-2);

                return monthName + ' ' + shortYear;
            }
        }
    };

    // ////////////////////////////////////////////////////////////////////////
    // formatRunsLabel - produces "1 run" or "N runs" with formatted count.
    // ////////////////////////////////////////////////////////////////////////

    dash.formatRunsLabel = function(count) {
        var formattedCount = kit.format_number_full(count);
        var suffix = count === 1 ? 'run' : 'runs';

        return formattedCount + ' ' + suffix;
    };

    // ////////////////////////////////////////////////////////////////////////
    // summarizeBucket - sums outcome counts from a bucket and returns
    // a structured summary with totals, label, and per-outcome breakdown.
    // ////////////////////////////////////////////////////////////////////////

    dash.summarizeBucket = function(bucket, visibleKeys, barColors, outcomeLabels) {

        var totalRuns = 0;
        var outcomes = [];

        for (var keyIndex = 0; keyIndex < visibleKeys.length; keyIndex++) {
            var outcomeKey = visibleKeys[keyIndex];
            var runCount = bucket[outcomeKey];
            totalRuns += runCount;

            outcomes.push({
                key: outcomeKey,
                label: outcomeLabels[outcomeKey],
                count: runCount,
                color: barColors[outcomeKey]
            });
        }

        return {
            totalRuns: totalRuns,
            runsLabel: dash.formatRunsLabel(totalRuns),
            outcomes: outcomes
        };
    };

    // ////////////////////////////////////////////////////////////////////////
    // buildTooltipHtml - assembles the tooltip HTML from a time label
    // and a bucket summary returned by summarizeBucket.
    // ////////////////////////////////////////////////////////////////////////

    dash.buildTooltipHtml = function(timeLabel, summary) {

        // Build the header with the time label and total runs ..
        var headerHtml = '<div class="dashboard-tooltip-header">' +
            '<div class="dashboard-tooltip-title">' + timeLabel + '</div>' +
            '<div class="dashboard-tooltip-subtitle">' + summary.runsLabel + '</div>' +
            '</div>';

        // .. then build one row per outcome.
        var bodyLines = [];

        for (var outcomeIndex = 0; outcomeIndex < summary.outcomes.length; outcomeIndex++) {
            var outcome = summary.outcomes[outcomeIndex];
            var outcomeRunsLabel = dash.formatRunsLabel(outcome.count);

            bodyLines.push('<div class="dashboard-tooltip-row">' +
                '<span class="dashboard-tooltip-dot" style="background:' + outcome.color + '"></span>' +
                outcome.label + ': <b>' + outcomeRunsLabel + '</b></div>');
        }

        var bodyHtml = '<div class="dashboard-tooltip-body">' + bodyLines.join('') + '</div>';

        return headerHtml + bodyHtml;
    };

    // ////////////////////////////////////////////////////////////////////////
    // get_bucket_info - returns info about a single chart bucket by index,
    // or null if the index is out of range.
    // ////////////////////////////////////////////////////////////////////////

    dash.get_bucket_info = function(bucketIndex) {

        var buckets = dash._chart_buckets;

        if (!buckets || bucketIndex < 0 || bucketIndex >= buckets.length) {
            return null;
        }

        var bucket = buckets[bucketIndex];
        var labelRange = dash._chart_label_range;

        // Build the time label from start and end dates ..
        var timeStart = new Date(bucket.start);
        var timeEnd = new Date(bucket.end);
        var bucketSpanSeconds = Math.round((bucket.end - bucket.start) / 1000);

        var timeLabel;

        if (bucketSpanSeconds >= 1) {
            var startLabel = dash.formatTimeLabel(timeStart, labelRange);
            var endLabel = dash.formatTimeLabel(timeEnd, labelRange);
            timeLabel = startLabel + ' \u2192 ' + endLabel;
        }
        else {
            timeLabel = dash.formatTimeLabel(timeStart, labelRange);
        }

        // .. then summarize the outcome counts.
        var summary = dash.summarizeBucket(bucket, dash._chart_visible_keys, dash._chart_bar_colors, dash._chart_labels);

        return {
            index: bucketIndex,
            time_label: timeLabel,
            total_runs: summary.totalRuns,
            runs_label: summary.runsLabel,
            outcomes: summary.outcomes,
            start: bucket.start,
            end: bucket.end
        };
    };

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
        if (dash._last_chart_buckets) {
            dash._skip_legend_rebuild = true;
            dash.render_bar_chart(dash._last_chart_buckets);
            dash._skip_legend_rebuild = false;
            var filtered_recent = dash._filter_recent_by_range(dash._last_recent_events);
            dash.render_recent(filtered_recent, dash._last_jobs);
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
                var outcomeRunsLabel = dash.formatRunsLabel(counts[key]);
                tip_lines.push('<div class="dashboard-tooltip-row">' +
                    '<span class="dashboard-tooltip-dot" style="background:' + bar_colors[key] + '"></span>' +
                    labels[key] + ': <b>' + outcomeRunsLabel + '</b></div>');
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
        dash._last_chart_buckets = chart_data;
        var container = $('#dashboard-bar-chart');

        if (!chart_data || !chart_data.buckets || chart_data.buckets.length === 0) {
            container.html('<div class="dashboard-no-data">No run history yet</div>');
            $('#dashboard-chart-legend').empty();
            $('#dashboard-data-count').text('');
            return;
        }

        var server_buckets = chart_data.buckets;
        var chart_width = container.width();
        var chart_height = 200;
        var padding_left = 62;
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

        var total_exec_count = 0;
        for (var tc = 0; tc < buckets.length; tc++) {
            total_exec_count += buckets[tc].ok + buckets[tc].error + buckets[tc].timeout;
        }

        var range_minutes = dash._time_range_minutes;
        var range_names = {5: '5 min', 15: '15 min', 30: '30 min', 60: '1 hour', 360: '6 hours', 1440: 'Today', 2880: 'Yesterday', 10080: 'This week', 43200: 'This month', 525600: 'This year'};
        var filteredCountSuffix = total_exec_count === 1 ? 'run' : 'runs';
        var filtered_count_label = kit.format_number_compact(total_exec_count) + ' ' + filteredCountSuffix;
        var filtered_count_full = dash.formatRunsLabel(total_exec_count);
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

        var visible_keys = [];
        for (var vk = 0; vk < outcome_keys.length; vk++) {
            if (hidden_outcomes[outcome_keys[vk]]) continue;
            var has_data = false;
            for (var hd = 0; hd < buckets.length; hd++) {
                if (buckets[hd][outcome_keys[vk]] > 0) { has_data = true; break; }
            }
            if (has_data) visible_keys.push(outcome_keys[vk]);
        }

        dash._chart_buckets = buckets;
        dash._chart_visible_keys = visible_keys;
        dash._chart_bar_colors = bar_colors;
        dash._chart_labels = labels;

        // Determine the effective range in milliseconds ..
        var rangeMilliseconds = dash._time_range_minutes * dash.config.ms_per_minute;

        if (rangeMilliseconds === 0 && buckets.length > 0) {
            rangeMilliseconds = buckets[buckets.length - 1].end - buckets[0].start;
        }

        // .. derive the group type from the range ..
        var groupType;

        if (rangeMilliseconds === 0)                            groupType = 'none';
        else if (rangeMilliseconds >= dash.config.ms_per_year)  groupType = 'month';
        else if (rangeMilliseconds >= dash.config.ms_per_week)  groupType = 'day';
        else if (rangeMilliseconds > dash.config.ms_per_hour)   groupType = 'hour';
        else                                                    groupType = 'minute';

        dash._chart_group_type = groupType;

        // .. look up the grouping configuration for this group type ..
        var groupConfig = dash.groupConfig[groupType];

        // .. build the group map, assigning each raw bucket to a group.
        dash._chart_groups = [];
        dash._chart_group_ranges = {};
        dash._chart_group_labels = {};

        for (var bucketIndex = 0; bucketIndex < buckets.length; bucketIndex++) {

            var bucketDate = new Date(buckets[bucketIndex].start);
            var groupKey;
            var groupLabel;

            // .. when we have a known group type, derive the key and label from the config ..
            if (groupConfig) {
                groupKey = groupConfig.extractKey(bucketDate);
                groupLabel = groupConfig.formatLabel(bucketDate);
            }

            // .. otherwise use the raw bucket index with no label.
            else {
                groupKey = bucketIndex;
                groupLabel = null;
            }

            dash._chart_groups.push(groupKey);

            if (dash._chart_group_ranges[groupKey] === undefined) {
                dash._chart_group_ranges[groupKey] = {first: bucketIndex, last: bucketIndex};
                dash._chart_group_labels[groupKey] = groupLabel;
            }
            else {
                dash._chart_group_ranges[groupKey].last = bucketIndex;
            }
        }

        // .. collapse raw buckets into per-group plot buckets when grouping is active ..
        // .. otherwise plot buckets is just a reference to the raw buckets.
        var plotBuckets;

        if (groupType !== 'none') {

            var seenGroupOrder = [];
            var groupEntries = {};

            for (var rawIndex = 0; rawIndex < buckets.length; rawIndex++) {

                var rawGroupKey = dash._chart_groups[rawIndex];

                // .. create a new entry when we encounter a group key for the first time ..
                if (groupEntries[rawGroupKey] === undefined) {
                    seenGroupOrder.push(rawGroupKey);

                    var newEntry = {start: buckets[rawIndex].start, end: buckets[rawIndex].end, group_key: rawGroupKey};

                    for (var initKeyIndex = 0; initKeyIndex < visible_keys.length; initKeyIndex++) {
                        newEntry[visible_keys[initKeyIndex]] = 0;
                    }

                    groupEntries[rawGroupKey] = newEntry;
                }

                // .. accumulate the raw bucket's outcome counts into the group entry.
                var targetEntry = groupEntries[rawGroupKey];
                targetEntry.end = buckets[rawIndex].end;

                for (var accumulateIndex = 0; accumulateIndex < visible_keys.length; accumulateIndex++) {
                    targetEntry[visible_keys[accumulateIndex]] += buckets[rawIndex][visible_keys[accumulateIndex]];
                }
            }

            // .. build the final array in insertion order.
            plotBuckets = [];

            for (var orderIndex = 0; orderIndex < seenGroupOrder.length; orderIndex++) {
                plotBuckets.push(groupEntries[seenGroupOrder[orderIndex]]);
            }
        }
        else {
            plotBuckets = buckets;
        }

        bucket_count = plotBuckets.length;

        // .. compute the maximum stacked value across all plot buckets for y-axis scaling.
        var maxStack = 0;

        if (dash.show_bars) {
            for (var stackIndex = 0; stackIndex < plotBuckets.length; stackIndex++) {
                var stackSum = 0;

                for (var stackKeyIndex = 0; stackKeyIndex < visible_keys.length; stackKeyIndex++) {
                    stackSum += plotBuckets[stackIndex][visible_keys[stackKeyIndex]];
                }

                if (stackSum > maxStack) {
                    maxStack = stackSum;
                }
            }
        }
        else {
            for (var lineIndex = 0; lineIndex < plotBuckets.length; lineIndex++) {
                for (var lineKeyIndex = 0; lineKeyIndex < visible_keys.length; lineKeyIndex++) {
                    var lineValue = plotBuckets[lineIndex][visible_keys[lineKeyIndex]];

                    if (lineValue > maxStack) {
                        maxStack = lineValue;
                    }
                }
            }
        }

        if (maxStack === 0) {
            maxStack = 1;
        }

        var draw_width = chart_width - padding_left - padding_right;
        var draw_height = chart_height - padding_top - padding_bottom;
        var baseline_y = padding_top + draw_height;

        var svg = '<svg width="' + chart_width + '" height="' + chart_height + '" xmlns="http://www.w3.org/2000/svg">';

        svg += '<defs>';
        for (var gradientIndex = 0; gradientIndex < visible_keys.length; gradientIndex++) {
            var gradientKey = visible_keys[gradientIndex];
            svg += '<linearGradient id="areaGrad_' + gradientKey + '" x1="0" y1="0" x2="0" y2="1">';
            svg += '<stop offset="0" stop-color="' + bar_colors[gradientKey] + '" stop-opacity="0.10"/>';
            svg += '<stop offset="0.5" stop-color="' + bar_colors[gradientKey] + '" stop-opacity="0.03"/>';
            svg += '<stop offset="1" stop-color="' + bar_colors[gradientKey] + '" stop-opacity="0.0"/>';
            svg += '</linearGradient>';
        }
        svg += '</defs>';

        // .. determine the y-axis suffix from the group config.
        var yAxisValues = [];
        var yAxisSuffix = groupConfig ? groupConfig.suffix : '';

        var gridLineCount = Math.min(4, maxStack);
        var previousGridValue = -1;

        for (var gridIndex = 0; gridIndex <= gridLineCount; gridIndex++) {

            var gridY = padding_top + draw_height - (gridIndex / gridLineCount) * draw_height;
            var gridValue = Math.round((gridIndex / gridLineCount) * maxStack);

            svg += '<line x1="' + padding_left + '" y1="' + gridY.toFixed(1) + '" ';
            svg += 'x2="' + (chart_width - padding_right) + '" y2="' + gridY.toFixed(1) + '" ';
            svg += 'stroke="rgba(0,0,0,0.05)" stroke-width="1" />';

            if (gridValue !== previousGridValue) {
                svg += '<text x="' + (padding_left - 6) + '" y="' + (gridY + 3).toFixed(1) + '" ';
                svg += 'text-anchor="end" font-size="10" fill="rgba(0,0,0,0.6)" font-family="Menlo, Consolas, Monaco, monospace" data-grid-value="' + gridValue + '">';
                svg += kit.format_number_compact(gridValue) + yAxisSuffix + '</text>';

                yAxisValues.push(gridValue);
                previousGridValue = gridValue;
            }
        }

        var bucket_slot_width = draw_width / bucket_count;
        var group_padding = bucket_slot_width * 0.15;
        var group_width = bucket_slot_width - group_padding * 2;
        var num_visible = visible_keys.length;
        var bar_gap = Math.max(1, group_width * 0.06);
        var bar_width = (group_width - bar_gap * (num_visible - 1)) / num_visible;

        var layer_points = {};

        for (var layer = 0; layer < visible_keys.length; layer++) {
            var layer_key = visible_keys[layer];
            layer_points[layer_key] = [];

            for (var pointIndex = 0; pointIndex < bucket_count; pointIndex++) {
                var pointValue = plotBuckets[pointIndex][layer_key];
                var pointHeight = pointValue > 0 ? Math.max(2, (pointValue / maxStack) * draw_height) : 0;
                var pointX = padding_left + pointIndex * bucket_slot_width + group_padding + layer * (bar_width + bar_gap);
                var pointY = baseline_y - pointHeight;

                layer_points[layer_key].push({
                    x: pointX + bar_width / 2,
                    y: pointValue > 0 ? pointY : baseline_y,
                    val: pointValue
                });
            }
        }

        if (dash.show_bars) {
            var barInset = Math.max(1, bucket_slot_width * 0.1);
            var barSlotWidth = bucket_slot_width - barInset * 2;
            var barSeparation = 1.5;

            for (var resetIndex = 0; resetIndex < visible_keys.length; resetIndex++) {
                layer_points[visible_keys[resetIndex]] = [];
            }

            for (var barBucketIndex = 0; barBucketIndex < bucket_count; barBucketIndex++) {
                var barX = padding_left + barBucketIndex * bucket_slot_width + barInset;
                var barCursorY = baseline_y;

                for (var barKeyIndex = 0; barKeyIndex < visible_keys.length; barKeyIndex++) {
                    var barOutcomeKey = visible_keys[barKeyIndex];
                    var barValue = plotBuckets[barBucketIndex][barOutcomeKey];
                    var barHeight = barValue > 0 ? Math.max(2, (barValue / maxStack) * draw_height) : 0;

                    if (barValue > 0) {
                        var segmentY = barCursorY - barHeight;
                        svg += '<rect x="' + barX.toFixed(1) + '" y="' + segmentY.toFixed(1) + '" ';
                        svg += 'width="' + barSlotWidth.toFixed(1) + '" height="' + barHeight.toFixed(1) + '" ';
                        svg += 'fill="' + bar_colors[barOutcomeKey] + '" />';
                        barCursorY = segmentY - barSeparation;
                    }

                    layer_points[barOutcomeKey].push({
                        x: barX + barSlotWidth / 2,
                        y: barValue > 0 ? barCursorY + barSeparation : baseline_y,
                        val: barValue
                    });
                }
            }
        }

        if (!dash.show_bars) {
            var edge_left = padding_left;
            var edge_right = padding_left + draw_width;

            for (var spline_layer = 0; spline_layer < visible_keys.length; spline_layer++) {
                var spline_key = visible_keys[spline_layer];
                var dataPoints = [];

                for (var splineIndex = 0; splineIndex < bucket_count; splineIndex++) {
                    var splineX = padding_left + (splineIndex + 0.5) * bucket_slot_width;
                    var splineValue = plotBuckets[splineIndex][spline_key];
                    var splineY = splineValue > 0 ? baseline_y - Math.max(2, (splineValue / maxStack) * draw_height) : baseline_y;
                    dataPoints.push({x: splineX, y: splineY, bucket_index: splineIndex});
                }

                var curvePoints = [];
                curvePoints.push({x: edge_left, y: dataPoints[0].y});

                for (var curveIndex = 0; curveIndex < dataPoints.length; curveIndex++) {
                    curvePoints.push(dataPoints[curveIndex]);
                }

                var lastDataPoint = dataPoints[dataPoints.length - 1];
                curvePoints.push({x: edge_right, y: lastDataPoint.y});

                layer_points[spline_key] = [];

                for (var hoverPointIndex = 0; hoverPointIndex < bucket_count; hoverPointIndex++) {
                    var hoverPointValue = plotBuckets[hoverPointIndex][spline_key];
                    var hoverPointY = hoverPointValue > 0 ? baseline_y - (hoverPointValue / maxStack) * draw_height : baseline_y;
                    layer_points[spline_key].push({x: dataPoints[hoverPointIndex].x, y: hoverPointY, val: hoverPointValue});
                }

                var areaPath = dash.buildMonotoneCubicPath(curvePoints);
                var areaFill = areaPath +
                    ' L' + edge_right.toFixed(1) + ',' + baseline_y.toFixed(1) +
                    ' L' + edge_left.toFixed(1) + ',' + baseline_y.toFixed(1) + ' Z';

                svg += '<path d="' + areaFill + '" fill="url(#areaGrad_' + spline_key + ')" />';
                svg += '<path d="' + areaPath + '" fill="none" stroke="' + bar_colors[spline_key] + '" stroke-width="1.5" stroke-opacity="0.6" stroke-linecap="round" stroke-linejoin="round" />';

                var tipCenterX = edge_right;
                var tipCenterY = lastDataPoint.y;
                var tipColor = bar_colors[spline_key];
                svg += '<circle cx="' + tipCenterX.toFixed(2) + '" cy="' + tipCenterY.toFixed(2) + '" r="5.5" ';
                svg += 'fill="none" stroke="' + tipColor + '" stroke-opacity="0.35" stroke-width="1"/>';
                svg += '<circle cx="' + tipCenterX.toFixed(2) + '" cy="' + tipCenterY.toFixed(2) + '" r="3.5" ';
                svg += 'fill="' + tipColor + '"/>';
            }
        }

        var label_range = dash._time_range_minutes > 0
            ? dash._time_range_minutes * dash.config.ms_per_minute
            : time_range;
        dash._chart_label_range = label_range;
        var xAxisLabels = [];
        var label_count = _is_year_range ? bucket_count : Math.min(6, bucket_count);
        var label_step = Math.max(1, Math.floor(bucket_count / label_count));
        for (var label_index = 0; label_index < bucket_count; label_index += label_step) {
            var label_x = padding_left + (label_index + 0.5) * bucket_slot_width;
            var label_date = new Date(plotBuckets[label_index].start);
            var label_text = dash.formatTimeLabel(label_date, label_range);
            xAxisLabels.push(label_text);
            svg += '<text x="' + label_x.toFixed(1) + '" y="' + (chart_height - 6) + '" text-anchor="middle" ';
            svg += 'font-size="10" fill="rgba(0,0,0,0.6)" font-family="Menlo, Consolas, Monaco, monospace">' + label_text + '</text>';
        }

        // .. emit the final time label at the right edge if it differs from the last loop label ..
        var final_label_date = new Date(plotBuckets[bucket_count - 1].start);
        var final_label_text = dash.formatTimeLabel(final_label_date, label_range);
        if (final_label_text !== xAxisLabels[xAxisLabels.length - 1]) {
            var final_label_x = chart_width - padding_right;
            xAxisLabels.push(final_label_text);
            svg += '<text x="' + final_label_x.toFixed(1) + '" y="' + (chart_height - 6) + '" text-anchor="end" ';
            svg += 'font-size="10" fill="rgba(0,0,0,0.6)" font-family="Menlo, Consolas, Monaco, monospace">' + final_label_text + '</text>';
        }

        // .. build the copy-data array from plot buckets using summarizeBucket.
        var copyBuckets = [];

        for (var copyIndex = 0; copyIndex < plotBuckets.length; copyIndex++) {

            var copyBucket = plotBuckets[copyIndex];

            // .. resolve the group label, using the config label if available ..
            var copyGroupKey;
            var copyLabel;

            if (copyBucket.group_key !== undefined) {
                copyGroupKey = copyBucket.group_key;
                copyLabel = dash._chart_group_labels[copyGroupKey];
            }
            else {
                copyGroupKey = dash._chart_groups[copyIndex];
                copyLabel = dash._chart_group_labels[copyGroupKey];
            }

            // .. if no group label was found, format it from the bucket start date.
            if (!copyLabel) {
                var copyDate = new Date(copyBucket.start);
                copyLabel = dash.formatTimeLabel(copyDate, label_range);
            }

            var copySummary = dash.summarizeBucket(copyBucket, visible_keys, bar_colors, labels);

            copyBuckets.push({
                index: copyIndex,
                time_label: copyLabel,
                total_runs: copySummary.totalRuns,
                runs_label: copySummary.runsLabel,
                outcomes: copySummary.outcomes,
                start: copyBucket.start,
                end: copyBucket.end
            });
        }

        dash._copy_data = {
            y_axis: yAxisValues,
            x_axis: xAxisLabels,
            buckets: copyBuckets
        };

        svg += '</svg>';
        container.html(svg);

        container.find('text[data-grid-value]').each(function() {
            var raw = parseInt(this.dataset.gridValue, 10);
            var compact = kit.format_number_compact(raw);
            var full = kit.format_number_full(raw);
            if (compact !== full) {
                tippy(this, {
                    content: full,
                    placement: 'left',
                    theme: 'dark',
                    arrow: true,
                    delay: [0, 0]
                });
            }
        });

        dash._setup_chart_interactions(container, plotBuckets, padding_left, draw_width, bucket_count, padding_top, draw_height, padding_bottom, chart_height, visible_keys, layer_points, bar_colors);

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

            var hoverIndex = Math.floor((relative_x / draw_width) * bucket_count);

            if (hoverIndex >= bucket_count) {
                hoverIndex = bucket_count - 1;
            }

            if (hoverIndex < 0) {
                hoverIndex = 0;
            }

            // Determine the group range and aggregate totals for this hover position ..
            var hoverBucket = buckets[hoverIndex];
            var hoverGroupKey;
            var hoverFirst;
            var hoverLast;
            var hoverTotals;

            // .. when the bucket is pre-grouped (from plotBuckets), read directly ..
            if (hoverBucket.group_key !== undefined) {
                hoverFirst = hoverIndex;
                hoverLast = hoverIndex;
                hoverGroupKey = hoverBucket.group_key;
                hoverTotals = {};

                for (var directKeyIndex = 0; directKeyIndex < visible_keys.length; directKeyIndex++) {
                    var directKey = visible_keys[directKeyIndex];
                    hoverTotals[directKey] = hoverBucket[directKey];
                }
            }

            // .. otherwise aggregate across the raw bucket range for this group.
            else {
                hoverGroupKey = dash._chart_groups[hoverIndex];
                var hoverRange = dash._chart_group_ranges[hoverGroupKey];
                hoverFirst = hoverRange.first;
                hoverLast = hoverRange.last;
                hoverTotals = {};

                for (var initIndex = 0; initIndex < visible_keys.length; initIndex++) {
                    hoverTotals[visible_keys[initIndex]] = 0;
                }

                for (var aggregateIndex = hoverFirst; aggregateIndex <= hoverLast; aggregateIndex++) {
                    for (var outcomeIndex = 0; outcomeIndex < visible_keys.length; outcomeIndex++) {
                        var outcomeKey = visible_keys[outcomeIndex];
                        hoverTotals[outcomeKey] += buckets[aggregateIndex][outcomeKey];
                    }
                }
            }

            // .. draw the highlight band over the hovered group ..
            var bandLeft = padding_left + hoverFirst * bucket_width_px;
            var bandWidth = (hoverLast - hoverFirst + 1) * bucket_width_px;
            var bandHtml = '<svg style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none" xmlns="http://www.w3.org/2000/svg">';
            bandHtml += '<rect x="' + bandLeft.toFixed(1) + '" y="' + padding_top + '" width="' + bandWidth.toFixed(1) + '" height="' + draw_height + '" fill="rgba(0,0,0,0.06)" rx="2" />';
            bandHtml += '</svg>';
            overlay.html(bandHtml);

            // .. resolve the group label for this hover ..
            var hoverLabel = dash._chart_group_labels[hoverGroupKey];

            if (!hoverLabel) {
                var hoverDate = new Date(buckets[hoverFirst].start);
                hoverLabel = dash.formatTimeLabel(hoverDate, dash._chart_label_range);
            }

            console.log('hover-group', JSON.stringify({
                index: hoverIndex,
                group_key: hoverGroupKey,
                group_type: dash._chart_group_type,
                label: hoverLabel,
                start: new Date(buckets[hoverFirst].start).toISOString(),
                end: new Date(buckets[hoverLast].end).toISOString(),
                totals: hoverTotals
            }, null, 2));

            // .. summarize the hover totals and build the tooltip.
            var hoverSummary = dash.summarizeBucket(hoverTotals, visible_keys, bar_colors, dash.outcome_labels);
            var tooltipHtml = dash.buildTooltipHtml(hoverLabel, hoverSummary);

            tooltip.html(tooltipHtml);
            tooltip.css({display: 'block', left: '0px', top: '0px'});
            var tooltipWidth = tooltip.outerWidth();
            var tooltipHeight = tooltip.outerHeight();
            var tooltipMargin = 8;
            var viewportWidth = $(window).width();
            var viewportHeight = $(window).height();

            var tooltipLeft = event.clientX + 14;
            var tooltipTop = event.clientY - 14;

            if (tooltipLeft + tooltipWidth + tooltipMargin > viewportWidth) {
                tooltipLeft = event.clientX - tooltipWidth - 14;
            }

            if (tooltipLeft < tooltipMargin) {
                tooltipLeft = tooltipMargin;
            }

            if (tooltipTop + tooltipHeight + tooltipMargin > viewportHeight) {
                tooltipTop = viewportHeight - tooltipHeight - tooltipMargin;
            }

            if (tooltipTop < tooltipMargin) {
                tooltipTop = tooltipMargin;
            }

            tooltip.css({left: tooltipLeft + 'px', top: tooltipTop + 'px'});
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
            var run_number = entry.current_run !== undefined ? kit.format_number_full(entry.current_run) : '';

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

        $.ajax({
            url: dash.config.base_url + 'poll/',
            type: 'POST',
            data: post_data,
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(data) {
                if (typeof data === 'string') {
                    try { data = JSON.parse(data); } catch(parse_error) { return; }
                }
                dash.render(data);

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
                buckets: dash._copy_data.buckets
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
            dash._time_range_minutes = minutes;
            kit.urls.set_range_minutes(minutes);
            var url = new URL(window.location.href);
            url.searchParams.set('range', minutes);
            window.history.replaceState(null, '', url.toString());
            menu.find('.dashboard-time-range-option').removeClass('dashboard-time-range-active');
            $(this).addClass('dashboard-time-range-active');
            menu.removeClass('dashboard-time-range-menu-open');
            dash._redraw_chart_from_cache();
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
