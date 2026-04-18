
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.scheduler === 'undefined') { $.fn.zato.scheduler = {}; }
$.fn.zato.scheduler.dashboard = {};

// ////////////////////////////////////////////////////////////////////////////
// Outcome color map - tinted badge palette
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.outcome_colors = {
    'ok': '#1b855e',
    'error': '#e0226e',
    'timeout': '#b35e00',
    'skipped_already_in_flight': '#6a4c93',
    'missed_catchup': '#0077b6'
};

$.fn.zato.scheduler.dashboard.outcome_bg_colors = {
    'ok': 'rgba(27, 133, 94, 0.12)',
    'error': 'rgba(224, 34, 110, 0.12)',
    'timeout': 'rgba(179, 94, 0, 0.12)',
    'skipped_already_in_flight': 'rgba(106, 76, 147, 0.12)',
    'missed_catchup': 'rgba(0, 119, 182, 0.12)'
};

$.fn.zato.scheduler.dashboard.outcome_bar_colors = {
    'ok': '#2d8f45',
    'error': '#c0392b',
    'timeout': '#b45309',
    'skipped_already_in_flight': '#7c3aed',
    'missed_catchup': '#1a6fa0'
};

$.fn.zato.scheduler.dashboard.outcome_bar_tints = {
    'ok': '#d4edda',
    'error': '#f5d5d2',
    'timeout': '#fde8cd',
    'skipped_already_in_flight': '#ede5fb',
    'missed_catchup': '#d1e8f4'
};

$.fn.zato.scheduler.dashboard.outcome_labels = {
    'ok': 'OK',
    'error': 'Error',
    'timeout': 'Timeout',
    'skipped_already_in_flight': 'Skipped (already in flight)',
    'missed_catchup': 'Missed catchup'
};

$.fn.zato.scheduler.dashboard.job_type_labels = {
    'one_time': 'One-time',
    'interval_based': 'Interval-based'
};

// ////////////////////////////////////////////////////////////////////////////
// Sparkline data buffers
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.show_bars = false;

$.fn.zato.scheduler.dashboard._icon_lines = '<svg width="18" height="14" viewBox="0 0 18 14" fill="none" xmlns="http://www.w3.org/2000/svg">' +
    '<path d="M1 12C3 8 5.5 2 9 4C12.5 6 14 10 17 1" stroke="#012845" stroke-width="1.8" stroke-linecap="round"/>' +
    '</svg>';

$.fn.zato.scheduler.dashboard._icon_bars = '<svg width="18" height="14" viewBox="0 0 18 14" fill="none" xmlns="http://www.w3.org/2000/svg">' +
    '<rect x="1" y="6" width="3" height="8" rx="1" fill="#012845" fill-opacity="0.85"/>' +
    '<rect x="5.5" y="2" width="3" height="12" rx="1" fill="#012845" fill-opacity="0.85"/>' +
    '<rect x="10" y="8" width="3" height="6" rx="1" fill="#012845" fill-opacity="0.85"/>' +
    '<rect x="14.5" y="4" width="3" height="10" rx="1" fill="#012845" fill-opacity="0.85"/>' +
    '</svg>';

$.fn.zato.scheduler.dashboard._update_chart_type_icon = function() {
    var toggle = $('#dashboard-chart-type-toggle');
    if ($.fn.zato.scheduler.dashboard.show_bars) {
        toggle.html($.fn.zato.scheduler.dashboard._icon_lines);
        toggle.attr('title', 'Switch to area chart');
    } else {
        toggle.html($.fn.zato.scheduler.dashboard._icon_bars);
        toggle.attr('title', 'Switch to bar chart');
    }
};

/* Tile sparklines always show the last 1 hour, independent of the main
   chart's zoom / time range. Each entry is {ts: ms, value: number}. */
$.fn.zato.scheduler.dashboard._spark_data = {
    total_jobs: [],
    active: [],
    paused: [],
    runs: [],
    failures: []
};

$.fn.zato.scheduler.dashboard._spark_seeded = false;
$.fn.zato.scheduler.dashboard._tile_window_ms = 60 * 60 * 1000;
$.fn.zato.scheduler.dashboard._poll_interval_ms = 10000;

/* Full thousands-separated form: 28937423 -> "28,937,423". Used as the
   authoritative display of a number (in title= hover tooltips). */
$.fn.zato.scheduler.dashboard._format_number_full = function(n) {
    if (n === null || n === undefined) return '-';
    var num = Number(n);
    if (!isFinite(num)) return String(n);
    try {
        return num.toLocaleString('en-US');
    } catch(e) {
        var s = String(Math.trunc(num));
        var sign = '';
        if (s.charAt(0) === '-') { sign = '-'; s = s.substring(1); }
        return sign + s.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
};

/* Compact form: 1234 -> "1.2K", 28937423 -> "29M". Keeps single-digit
   values intact; switches units at 1_000 / 1_000_000 / 1_000_000_000.
   One decimal only when the integer part is a single digit so numbers
   stay short. */
$.fn.zato.scheduler.dashboard._format_number_compact = function(n) {
    if (n === null || n === undefined) return '-';
    var num = Number(n);
    if (!isFinite(num)) return String(n);
    var abs = Math.abs(num);
    var sign = num < 0 ? '-' : '';
    if (abs < 1000) {
        return sign + (Math.round(abs * 10) / 10);
    }
    var units = [
        {v: 1e12, s: 'T'},
        {v: 1e9,  s: 'B'},
        {v: 1e6,  s: 'M'},
        {v: 1e3,  s: 'K'}
    ];
    for (var i = 0; i < units.length; i++) {
        if (abs >= units[i].v) {
            var scaled = abs / units[i].v;
            var rendered = scaled >= 10
                ? String(Math.round(scaled))
                : (Math.round(scaled * 10) / 10).toFixed(1);
            return sign + rendered + units[i].s;
        }
    }
    return sign + String(abs);
};

/* Apply compact + full-title to an element directly. Works for tile
   digits and pills where we control the text wholesale. */
$.fn.zato.scheduler.dashboard._set_number = function($el, n) {
    var dash = $.fn.zato.scheduler.dashboard;
    var compact = dash._format_number_compact(n);
    var full = dash._format_number_full(n);
    $el.text(compact);
    if (compact === full) {
        $el.removeAttr('title');
    } else {
        $el.attr('title', full);
    }
};

$.fn.zato.scheduler.dashboard._format_compact_duration = function(seconds) {
    if (seconds <= 0) return '0s';
    if (seconds < 60) return seconds + 's';
    if (seconds < 3600) {
        var mins = Math.floor(seconds / 60);
        var rem_s = seconds % 60;
        return rem_s > 0 ? mins + 'm ' + rem_s + 's' : mins + 'm';
    }
    if (seconds < 86400) {
        var hours = Math.floor(seconds / 3600);
        var rem_m = Math.floor((seconds % 3600) / 60);
        return rem_m > 0 ? hours + 'h ' + rem_m + 'm' : hours + 'h';
    }
    var days = Math.floor(seconds / 86400);
    var rem_h = Math.floor((seconds % 86400) / 3600);
    return rem_h > 0 ? days + 'd ' + rem_h + 'h' : days + 'd';
};

$.fn.zato.scheduler.dashboard._format_ago = function(seconds) {
    if (seconds <= 0) return 'Now';
    return $.fn.zato.scheduler.dashboard._format_compact_duration(seconds) + ' ago';
};

$.fn.zato.scheduler.dashboard._push_spark = function(key, value) {
    var dash = $.fn.zato.scheduler.dashboard;
    var data = dash._spark_data[key];
    var now = Date.now();
    data.push({ts: now, value: value});
    var cutoff = now - dash._tile_window_ms;
    while (data.length > 0 && data[0].ts < cutoff) {
        data.shift();
    }
};

$.fn.zato.scheduler.dashboard._spark_values = function(key) {
    var data = $.fn.zato.scheduler.dashboard._spark_data[key];
    var values = new Array(data.length);
    for (var i = 0; i < data.length; i++) {
        values[i] = data[i].value;
    }
    return values;
};

/* Shared helper: for every 1-minute bucket in the last hour, count the
   records in `timeline` whose `actual_fire_time_iso` falls in that
   bucket AND for which `predicate(record)` returns true. Returns
   {series: [{ts, value} * 60], total: N}. Both the failures and the
   runs sparklines share this exact bucketing so their x-axes stay in
   lock-step. */
$.fn.zato.scheduler.dashboard._bucket_events_per_minute = function(timeline, predicate) {
    var dash = $.fn.zato.scheduler.dashboard;
    var now = Date.now();
    var window_ms = dash._tile_window_ms;
    var bucket_count = 60;
    var bucket_size = window_ms / bucket_count;
    var window_start = now - window_ms;

    var series = new Array(bucket_count);
    for (var b = 0; b < bucket_count; b++) {
        series[b] = {
            ts: window_start + (b + 1) * bucket_size,
            value: 0
        };
    }

    var total = 0;
    if (timeline) {
        for (var r = 0; r < timeline.length; r++) {
            var record = timeline[r];
            if (!predicate(record)) continue;
            var iso = record.actual_fire_time_iso;
            if (!iso) continue;
            var t_ms = new Date(iso).getTime();
            if (isNaN(t_ms)) continue;
            if (t_ms < window_start || t_ms > now) continue;
            var idx = Math.floor((t_ms - window_start) / bucket_size);
            if (idx < 0) idx = 0;
            if (idx >= bucket_count) idx = bucket_count - 1;
            series[idx].value++;
            total++;
        }
    }

    return {series: series, total: total};
};

$.fn.zato.scheduler.dashboard._is_failure = function(record) {
    return record.outcome === 'error' || record.outcome === 'timeout';
};

$.fn.zato.scheduler.dashboard._is_execution = function(record) {
    var outcome = record.outcome;
    return outcome === 'ok' || outcome === 'error' || outcome === 'timeout';
};

$.fn.zato.scheduler.dashboard._rebuild_failures_series = function(timeline) {
    var dash = $.fn.zato.scheduler.dashboard;
    var result = dash._bucket_events_per_minute(timeline, dash._is_failure);
    dash._spark_data.failures = result.series;
    return result.total;
};

/* "Runs" = successful + failed executions that started in each minute of
   the last hour. Same bucketing as failures so the two tiles line up
   visually. Big digit = sum over the whole hour. */
$.fn.zato.scheduler.dashboard._rebuild_runs_series = function(timeline) {
    var dash = $.fn.zato.scheduler.dashboard;
    var result = dash._bucket_events_per_minute(timeline, dash._is_execution);
    dash._spark_data.runs = result.series;
    return result.total;
};

$.fn.zato.scheduler.dashboard._seed_spark_buffers = function(data) {
    var dash = $.fn.zato.scheduler.dashboard;
    if (dash._spark_seeded) {
        return;
    }

    var total_jobs = data.total_jobs || 0;
    var active_jobs = data.active_jobs || 0;
    var paused_jobs = data.paused_jobs || 0;

    var now = Date.now();
    var window_ms = dash._tile_window_ms;
    var bucket_count = 60;
    var bucket_size = window_ms / bucket_count;
    var window_start = now - window_ms;

    /* State-based metrics have no historical record (they're instantaneous
       snapshots), so seed with a flat baseline spanning the full 1 h window
       using the current value. The sparkline component places points by
       index, so we need enough anchors for the visual time-per-pixel to
       be close to the failures series (60 buckets across the hour). Real
       polls append to the tail on top of these anchors, producing a curve
       on the rightmost portion that grows toward the middle as time passes. */
    var seed_flat = function(value) {
        var arr = new Array(bucket_count);
        for (var i = 0; i < bucket_count; i++) {
            arr[i] = {
                ts: window_start + (i + 1) * bucket_size,
                value: value
            };
        }
        return arr;
    };
    dash._spark_data.total_jobs = seed_flat(total_jobs);
    dash._spark_data.active = seed_flat(active_jobs);
    dash._spark_data.paused = seed_flat(paused_jobs);

    /* Runs and failures are both rebuilt from the history timeline on every
       render via _rebuild_runs_series / _rebuild_failures_series, so no
       seeding is needed for them. */

    dash._spark_seeded = true;
};

// ////////////////////////////////////////////////////////////////////////////
// Legend toggle persistence
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard._get_hidden_outcomes = function() {
    try {
        var stored = localStorage.getItem('zato_scheduler_hidden_outcomes');
        return stored ? JSON.parse(stored) : {};
    } catch(e) {
        return {};
    }
};

$.fn.zato.scheduler.dashboard._set_hidden_outcomes = function(hidden) {
    try {
        localStorage.setItem('zato_scheduler_hidden_outcomes', JSON.stringify(hidden));
    } catch(e) {}
};

$.fn.zato.scheduler.dashboard._toggle_outcome = function(key) {
    var hidden = $.fn.zato.scheduler.dashboard._get_hidden_outcomes();
    if (hidden[key]) {
        delete hidden[key];
    } else {
        hidden[key] = true;
    }
    $.fn.zato.scheduler.dashboard._set_hidden_outcomes(hidden);
    $.fn.zato.scheduler.dashboard._redraw_chart_from_cache();
};

$.fn.zato.scheduler.dashboard._last_timeline = null;
$.fn.zato.scheduler.dashboard._time_range_minutes = 0;

$.fn.zato.scheduler.dashboard._get_time_range_minutes = function() {
    try {
        var stored = localStorage.getItem('zato_scheduler_time_range');
        return stored ? parseInt(stored, 10) : 0;
    } catch(e) {
        return 0;
    }
};

$.fn.zato.scheduler.dashboard._set_time_range_minutes = function(minutes) {
    $.fn.zato.scheduler.dashboard._time_range_minutes = minutes;
    try {
        localStorage.setItem('zato_scheduler_time_range', String(minutes));
    } catch(e) {}
};

$.fn.zato.scheduler.dashboard._filter_timeline_by_range = function(timeline) {
    var minutes = $.fn.zato.scheduler.dashboard._time_range_minutes;
    if (!minutes || minutes <= 0 || !timeline) {
        return timeline;
    }
    var cutoff = Date.now() - (minutes * 60 * 1000);
    var filtered = [];
    for (var i = 0; i < timeline.length; i++) {
        var ts = timeline[i].actual_fire_time_iso;
        if (ts && new Date(ts).getTime() >= cutoff) {
            filtered.push(timeline[i]);
        }
    }
    return filtered;
};

$.fn.zato.scheduler.dashboard._skip_legend_rebuild = false;

$.fn.zato.scheduler.dashboard._zoom_bucket_count = 0;

$.fn.zato.scheduler.dashboard._redraw_chart_from_cache = function() {
    if ($.fn.zato.scheduler.dashboard._last_timeline) {
        $.fn.zato.scheduler.dashboard._skip_legend_rebuild = true;
        $.fn.zato.scheduler.dashboard.render_bar_chart($.fn.zato.scheduler.dashboard._last_timeline);
        $.fn.zato.scheduler.dashboard._skip_legend_rebuild = false;
    }
};

// ////////////////////////////////////////////////////////////////////////////
// Formatting helpers
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.format_duration = function(duration_ms) {
    if (duration_ms === null || duration_ms === undefined || duration_ms === '') {
        return '-';
    }
    var ms = parseInt(duration_ms, 10);
    if (isNaN(ms)) {
        return '-';
    }
    if (ms < 1000) {
        return ms + ' ms';
    }
    if (ms < 60000) {
        return (ms / 1000).toFixed(1) + ' s';
    }
    return (ms / 60000).toFixed(1) + ' min';
};

$.fn.zato.scheduler.dashboard.relative_time_future = function(iso_string) {
    if (!iso_string) {
        return '-';
    }
    var target = new Date(iso_string).getTime();
    var now = Date.now();
    var diff_seconds = Math.floor((target - now) / 1000);

    if (diff_seconds < 0) {
        return 'Overdue';
    }
    if (diff_seconds === 0) {
        return 'Now';
    }
    if (diff_seconds < 60) {
        return 'In ' + diff_seconds + 's';
    }
    if (diff_seconds < 3600) {
        return 'In ' + Math.floor(diff_seconds / 60) + 'm';
    }
    if (diff_seconds < 86400) {
        return 'In ' + Math.floor(diff_seconds / 3600) + 'h';
    }
    return 'In ' + Math.floor(diff_seconds / 86400) + 'd';
};

$.fn.zato.scheduler.dashboard.relative_time_past = function(iso_string) {
    if (!iso_string) {
        return '-';
    }
    var target = new Date(iso_string).getTime();
    var now = Date.now();
    var diff_seconds = Math.floor((now - target) / 1000);

    if (diff_seconds < 0) {
        diff_seconds = 0;
    }
    if (diff_seconds < 60) {
        return diff_seconds + 's ago';
    }
    if (diff_seconds < 3600) {
        return Math.floor(diff_seconds / 60) + 'm ago';
    }
    if (diff_seconds < 86400) {
        return Math.floor(diff_seconds / 3600) + 'h ago';
    }
    return Math.floor(diff_seconds / 86400) + 'd ago';
};

$.fn.zato.scheduler.dashboard.format_local_time = function(iso_string) {
    if (!iso_string) {
        return '';
    }
    var date = new Date(iso_string);
    var year = date.getFullYear();
    var month = ('0' + (date.getMonth() + 1)).slice(-2);
    var day = ('0' + date.getDate()).slice(-2);
    var hours = ('0' + date.getHours()).slice(-2);
    var minutes = ('0' + date.getMinutes()).slice(-2);
    var seconds = ('0' + date.getSeconds()).slice(-2);
    return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
};

// ////////////////////////////////////////////////////////////////////////////
// Status dot
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.status_dot = function(job) {
    if (job.is_running) {
        return '<span class="dashboard-status-dot dashboard-status-running" title="Running"></span>';
    }
    if (!job.is_active) {
        return '<span class="dashboard-status-dot dashboard-status-paused" title="Paused"></span>';
    }
    if (job.last_outcome === 'error' || job.last_outcome === 'timeout') {
        return '<span class="dashboard-status-dot dashboard-status-failed" title="Last run failed"></span>';
    }
    return '<span class="dashboard-status-dot dashboard-status-ok" title="Active"></span>';
};

// ////////////////////////////////////////////////////////////////////////////
// Outcome micro-chart (colored squares)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.outcome_squares = function(recent_outcomes) {
    if (!recent_outcomes || recent_outcomes.length === 0) {
        return '<span style="color:#a0a0a5">-</span>';
    }
    var bar_colors = $.fn.zato.scheduler.dashboard.outcome_bar_colors;
    var labels = $.fn.zato.scheduler.dashboard.outcome_labels;
    var html = '';
    for (var index = 0; index < recent_outcomes.length; index++) {
        var outcome = recent_outcomes[index];
        var color = bar_colors[outcome] || '#ccc';
        var label = labels[outcome] || outcome;
        html += '<span class="dashboard-outcome-square" style="background:' + color + '" title="' + label + '"></span>';
    }
    return html;
};

// ////////////////////////////////////////////////////////////////////////////
// Outcome badge (tinted background)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.outcome_badge = function(outcome) {
    var colors = $.fn.zato.scheduler.dashboard.outcome_colors;
    var bg_colors = $.fn.zato.scheduler.dashboard.outcome_bg_colors;
    var labels = $.fn.zato.scheduler.dashboard.outcome_labels;
    var color = colors[outcome] || '#6e6e73';
    var bg = bg_colors[outcome] || 'rgba(110,110,115,0.12)';
    var label = labels[outcome] || outcome;
    return '<span class="dashboard-outcome-badge" style="color:' + color + ';background:' + bg + '">' + label + '</span>';
};

// ////////////////////////////////////////////////////////////////////////////
// Top-rounded bar path helper
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.top_rounded_bar = function(x, y, w, h, r) {
    if (h < r) {
        r = h;
    }
    if (w < 2 * r) {
        r = w / 2;
    }
    return 'M' + x + ',' + (y + h) +
           ' v' + (-(h - r)) +
           ' a' + r + ',' + r + ' 0 0 1 ' + r + ',' + (-r) +
           ' h' + (w - 2 * r) +
           ' a' + r + ',' + r + ' 0 0 1 ' + r + ',' + r +
           ' v' + (h - r) +
           ' z';
};

// ////////////////////////////////////////////////////////////////////////////
// Bar chart
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.render_bar_chart = function(timeline) {
    $.fn.zato.scheduler.dashboard._last_timeline = timeline;
    var container = $('#dashboard-bar-chart');
    var filtered = $.fn.zato.scheduler.dashboard._filter_timeline_by_range(timeline);

    if (!filtered || filtered.length === 0) {
        container.html('<div class="dashboard-no-data">No execution history yet</div>');
        $('#dashboard-chart-legend').empty();
        $('#dashboard-exec-count').text('');
        return;
    }

    var range_minutes = $.fn.zato.scheduler.dashboard._time_range_minutes;
    var range_names = {5: '5 min', 15: '15 min', 30: '30 min', 60: '1 hour', 360: '6 hours', 1440: 'Today', 2880: 'Yesterday', 10080: 'This week', 43200: 'This month', 525600: 'This year'};
    var range_label;
    var filtered_count_label = filtered.length === 1
        ? '1 run'
        : $.fn.zato.scheduler.dashboard._format_number_compact(filtered.length) + ' runs';
    var filtered_count_full = filtered.length === 1
        ? '1 run'
        : $.fn.zato.scheduler.dashboard._format_number_full(filtered.length) + ' runs';
    if (range_minutes > 0 && range_names[range_minutes]) {
        range_label = range_names[range_minutes] + ' \u00b7 ' + filtered_count_label;
    } else {
        range_label = 'All \u00b7 ' + filtered_count_label;
    }
    $('#dashboard-exec-count').text(range_label).attr(
        'title',
        (range_minutes > 0 && range_names[range_minutes] ? range_names[range_minutes] : 'All') +
        ' \u00b7 ' + filtered_count_full
    );

    var chart_width = container.width() || 800;
    var chart_height = 200;
    var padding_left = 40;
    var padding_bottom = 28;
    var padding_top = 12;
    var padding_right = 8;

    var outcome_keys = ['ok', 'error', 'timeout', 'skipped_already_in_flight', 'missed_catchup'];
    var bar_colors = $.fn.zato.scheduler.dashboard.outcome_bar_colors;
    var labels = $.fn.zato.scheduler.dashboard.outcome_labels;
    var hidden_outcomes = $.fn.zato.scheduler.dashboard._get_hidden_outcomes();

    var timestamps = [];
    for (var record_index = 0; record_index < filtered.length; record_index++) {
        var timestamp_string = filtered[record_index].actual_fire_time_iso;
        if (timestamp_string) {
            timestamps.push(new Date(timestamp_string).getTime());
        }
    }

    if (timestamps.length === 0) {
        container.html('<div class="dashboard-no-data">No execution history yet</div>');
        $('#dashboard-chart-legend').empty();
        $('#dashboard-exec-count').text('');
        return;
    }

    var min_time = Math.min.apply(null, timestamps);
    var max_time = Date.now();
    var time_range = max_time - min_time;

    if (time_range === 0) {
        time_range = 3600000;
        min_time = max_time - time_range;
    }

    var auto_bucket_count = Math.min(60, Math.max(12, Math.floor(chart_width / 16)));
    var bucket_count = $.fn.zato.scheduler.dashboard._zoom_bucket_count > 0
        ? Math.min(120, Math.max(4, $.fn.zato.scheduler.dashboard._zoom_bucket_count))
        : auto_bucket_count;
    var bucket_size = time_range / bucket_count;
    var buckets = [];
    for (var bucket_index = 0; bucket_index < bucket_count; bucket_index++) {
        var bucket = {};
        for (var key_index = 0; key_index < outcome_keys.length; key_index++) {
            bucket[outcome_keys[key_index]] = 0;
        }
        bucket.start = min_time + bucket_index * bucket_size;
        bucket.end = min_time + (bucket_index + 1) * bucket_size;
        buckets.push(bucket);
    }

    for (var timeline_index = 0; timeline_index < filtered.length; timeline_index++) {
        var record = filtered[timeline_index];
        var time = new Date(record.actual_fire_time_iso).getTime();
        var outcome = record.outcome || 'ok';
        var target_bucket = Math.floor((time - min_time) / bucket_size);
        if (target_bucket >= bucket_count) {
            target_bucket = bucket_count - 1;
        }
        if (target_bucket < 0) {
            target_bucket = 0;
        }
        if (buckets[target_bucket][outcome] !== undefined) {
            buckets[target_bucket][outcome]++;
        }
    }

    var visible_keys = [];
    for (var vk = 0; vk < outcome_keys.length; vk++) {
        if (hidden_outcomes[outcome_keys[vk]]) {
            continue;
        }
        var has_data = false;
        for (var hd = 0; hd < buckets.length; hd++) {
            if (buckets[hd][outcome_keys[vk]] > 0) {
                has_data = true;
                break;
            }
        }
        if (has_data) {
            visible_keys.push(outcome_keys[vk]);
        }
    }

    var max_stack = 0;
    if ($.fn.zato.scheduler.dashboard.show_bars) {
        for (var ms_index = 0; ms_index < buckets.length; ms_index++) {
            var ms_sum = 0;
            for (var ms_key = 0; ms_key < visible_keys.length; ms_key++) {
                ms_sum += (buckets[ms_index][visible_keys[ms_key]] || 0);
            }
            if (ms_sum > max_stack) max_stack = ms_sum;
        }
    } else {
        for (var ms_index = 0; ms_index < buckets.length; ms_index++) {
            for (var ms_key = 0; ms_key < visible_keys.length; ms_key++) {
                var ms_val = buckets[ms_index][visible_keys[ms_key]];
                if (ms_val > max_stack) max_stack = ms_val;
            }
        }
    }
    if (max_stack === 0) {
        max_stack = 1;
    }

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
    svg += '<linearGradient id="lollipopGrad" x1="0" y1="0" x2="0" y2="1">';
    svg += '<stop offset="0" stop-color="#9ca3af" stop-opacity="0.06"/>';
    svg += '<stop offset="0.5" stop-color="#9ca3af" stop-opacity="0.02"/>';
    svg += '<stop offset="1" stop-color="#9ca3af" stop-opacity="0.0"/>';
    svg += '</linearGradient>';
    svg += '</defs>';

    var grid_line_count = 4;
    for (var grid_index = 0; grid_index <= grid_line_count; grid_index++) {
        var grid_y = padding_top + draw_height - (grid_index / grid_line_count) * draw_height;
        var grid_value = Math.round((grid_index / grid_line_count) * max_stack);
        svg += '<line x1="' + padding_left + '" y1="' + grid_y.toFixed(1) + '" ';
        svg += 'x2="' + (chart_width - padding_right) + '" y2="' + grid_y.toFixed(1) + '" ';
        svg += 'stroke="rgba(0,0,0,0.05)" stroke-width="1" />';
        svg += '<text x="' + (padding_left - 6) + '" y="' + (grid_y + 3).toFixed(1) + '" ';
        svg += 'text-anchor="end" font-size="10" fill="rgba(0,0,0,0.35)" font-family="Menlo, Consolas, Monaco, monospace">';
        svg += grid_value + '</text>';
    }

    var bucket_slot_width = draw_width / bucket_count;
    var group_padding = bucket_slot_width * 0.15;
    var group_width = bucket_slot_width - group_padding * 2;
    var num_visible = visible_keys.length || 1;
    var bar_gap = Math.max(1, group_width * 0.06);
    var bar_width = (group_width - bar_gap * (num_visible - 1)) / num_visible;
    var bar_radius = 0;

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

    if ($.fn.zato.scheduler.dashboard.show_bars) {
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
                var sk_val = buckets[sbi][sk_key] || 0;
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

    if (!$.fn.zato.scheduler.dashboard.show_bars) {
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

            var area_path = 'M' + spline_pts[0].x.toFixed(1) + ',' + spline_pts[0].y.toFixed(1);
            for (var sp = 1; sp < spline_pts.length; sp++) {
                var sp_prev = spline_pts[sp - 1];
                var sp_curr = spline_pts[sp];
                var sp_cpx = (sp_prev.x + sp_curr.x) / 2;
                area_path += ' C' + sp_cpx.toFixed(1) + ',' + sp_prev.y.toFixed(1) +
                             ' ' + sp_cpx.toFixed(1) + ',' + sp_curr.y.toFixed(1) +
                             ' ' + sp_curr.x.toFixed(1) + ',' + sp_curr.y.toFixed(1);
            }
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

    var show_seconds = bucket_size < 120000;
    var label_count = Math.min(6, bucket_count);
    var label_step = Math.max(1, Math.floor(bucket_count / label_count));
    for (var label_index = 0; label_index < bucket_count; label_index += label_step) {
        var label_x = padding_left + (label_index + 0.5) * bucket_slot_width;
        var label_date = new Date(buckets[label_index].start);
        var label_text = ('0' + label_date.getHours()).slice(-2) + ':' + ('0' + label_date.getMinutes()).slice(-2);
        if (show_seconds) {
            label_text += ':' + ('0' + label_date.getSeconds()).slice(-2);
        }
        svg += '<text x="' + label_x.toFixed(1) + '" y="' + (chart_height - 6) + '" text-anchor="middle" ';
        svg += 'font-size="10" fill="rgba(0,0,0,0.35)" font-family="Menlo, Consolas, Monaco, monospace">' + label_text + '</text>';
    }

    svg += '</svg>';
    container.html(svg);

    $.fn.zato.scheduler.dashboard._setup_chart_interactions(container, buckets, padding_left, draw_width, bucket_count, padding_top, draw_height, padding_bottom, chart_height, visible_keys, layer_points, bar_colors);

    if (!$.fn.zato.scheduler.dashboard._skip_legend_rebuild) {
        var legend_container = $('#dashboard-chart-legend');
        var outcome_text_colors = $.fn.zato.scheduler.dashboard.outcome_colors;
        var outcome_bg = $.fn.zato.scheduler.dashboard.outcome_bg_colors;
        legend_container.empty();
        for (var legend_index = 0; legend_index < outcome_keys.length; legend_index++) {
            var legend_key = outcome_keys[legend_index];
            var is_hidden = !!hidden_outcomes[legend_key];
            var text_color = outcome_text_colors[legend_key] || '#6e6e73';
            var bg_color = outcome_bg[legend_key] || 'rgba(110,110,115,0.12)';
            var dot_color = bar_colors[legend_key];
            var item = $('<span class="dashboard-legend-badge' + (is_hidden ? ' dashboard-legend-badge-off' : '') + '" data-outcome="' + legend_key + '"></span>');
            item.css({'color': text_color, 'background': bg_color});
            item.append('<span class="dashboard-legend-badge-dot" style="background:' + dot_color + '"></span>');
            item.append(labels[legend_key]);
            legend_container.append(item);
        }
        legend_container.off('click.toggle').on('click.toggle', '.dashboard-legend-badge', function() {
            var el = $(this);
            var key = el.data('outcome');
            el.toggleClass('dashboard-legend-badge-off');
            var hidden = $.fn.zato.scheduler.dashboard._get_hidden_outcomes();
            if (hidden[key]) {
                delete hidden[key];
            } else {
                hidden[key] = true;
            }
            $.fn.zato.scheduler.dashboard._set_hidden_outcomes(hidden);
            $.fn.zato.scheduler.dashboard._redraw_chart_from_cache();
        });
    }
};

// ////////////////////////////////////////////////////////////////////////////
// Chart interactions (crosshair + tooltip)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard._setup_chart_interactions = function(container, buckets, padding_left, draw_width, bucket_count, padding_top, draw_height, padding_bottom, chart_height, visible_keys, layer_points, bar_colors) {
    var chart_svg = container.find('svg');
    var labels = $.fn.zato.scheduler.dashboard.outcome_labels;

    var overlay = container.find('.dashboard-chart-overlay');
    if (overlay.length === 0) {
        container.css('position', 'relative');
        container.append('<div class="dashboard-chart-overlay"></div>');
        overlay = container.find('.dashboard-chart-overlay');
    }
    overlay.css({position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', 'pointer-events': 'none'});

    var tooltip = $('#dashboard-chart-tooltip');
    if (tooltip.length === 0) {
        $('body').append('<div id="dashboard-chart-tooltip" class="dashboard-chart-tooltip"></div>');
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
            total_runs += (bucket[visible_keys[tk]] || 0);
        }
        var runs_label = total_runs === 1
            ? '1 run'
            : $.fn.zato.scheduler.dashboard._format_number_full(total_runs) + ' runs';

        var tooltip_html = '<div class="dashboard-tooltip-header">' +
            '<div class="dashboard-tooltip-title">' + time_label + '</div>' +
            '<div class="dashboard-tooltip-subtitle">' + runs_label + '</div>' +
            '</div>';

        var body_lines = [];
        for (var key_index = 0; key_index < visible_keys.length; key_index++) {
            var key = visible_keys[key_index];
            var count = bucket[key] || 0;
            body_lines.push('<span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:' + bar_colors[key] + ';margin-right:5px;vertical-align:middle"></span>' + (labels[key] || key) + ': <b>' + $.fn.zato.scheduler.dashboard._format_number_full(count) + '</b>');
        }
        tooltip_html += body_lines.join('<br>');

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
        if (mc_left < mc_margin) {
            mc_left = mc_margin;
        }
        if (mc_top + mc_tt_h + mc_margin > mc_viewport_h) {
            mc_top = mc_viewport_h - mc_tt_h - mc_margin;
        }
        if (mc_top < mc_margin) {
            mc_top = mc_margin;
        }
        tooltip.css({left: mc_left + 'px', top: mc_top + 'px'});
    });

    chart_svg.on('mouseleave.chart', function() {
        overlay.empty();
        tooltip.css('display', 'none');
    });

};

// ////////////////////////////////////////////////////////////////////////////
// Render job table
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.render_job_table = function(jobs) {
    var table_body = $('#dashboard-job-table-body');
    table_body.empty();

    if (!jobs || jobs.length === 0) {
        table_body.append('<tr><td colspan="5" class="dashboard-no-data">No jobs</td></tr>');
        $('#dashboard-jobs-count').text('');
        return;
    }

    var cluster_id = $(document).getUrlParam('cluster') || '1';

    $.fn.zato.scheduler.dashboard._set_number($('#dashboard-jobs-count'), jobs.length);

    jobs.sort(function(first, second) {
        return (first.name || '').localeCompare(second.name || '');
    });

    for (var job_index = 0; job_index < jobs.length; job_index++) {
        var job = jobs[job_index];
        var next_fire_text = $.fn.zato.scheduler.dashboard.relative_time_future(job.next_fire_utc);
        var next_fire_tooltip = $.fn.zato.scheduler.dashboard.format_local_time(job.next_fire_utc);
        var detail_url = '/zato/scheduler/dashboard/job/' + encodeURIComponent(job.id) + '/?cluster=' + cluster_id;

        var service_name = job.service || '';
        var service_cell = '';
        if (service_name) {
            var service_url = '/zato/service/overview/' + encodeURIComponent(service_name) + '/?cluster=' + cluster_id;
            service_cell = '<a href="' + service_url + '">' + service_name + '</a>';
        }

        var row = '<tr data-href="' + detail_url + '">';
        row += '<td>' + $.fn.zato.scheduler.dashboard.status_dot(job) + '</td>';
        row += '<td><a href="' + detail_url + '">' + job.name + '</a></td>';
        row += '<td>' + service_cell + '</td>';
        row += '<td style="font-family:monospace;font-feature-settings:\'tnum\' on;color:#6e6e73" title="' + next_fire_tooltip + '">' + next_fire_text + '</td>';
        row += '<td>' + $.fn.zato.scheduler.dashboard.outcome_squares(job.recent_outcomes) + '</td>';
        row += '</tr>';
        table_body.append(row);
    }

    table_body.find('tr[data-href]').on('click', function(event) {
        if ($(event.target).is('a')) {
            return;
        }
        window.location.href = $(this).data('href');
    });
};

// ////////////////////////////////////////////////////////////////////////////
// Render failures
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.render_failures = function(timeline) {
    var container = $('#dashboard-failures-body');
    container.empty();

    var all_clear_html = '<div class="dashboard-all-clear"><svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="7" stroke="#1b855e" stroke-width="1.5"/><path d="M5 8l2 2 4-4" stroke="#1b855e" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>All clear</div>';

    if (!timeline || timeline.length === 0) {
        container.html(all_clear_html);
        $('#dashboard-failures-count').text('0');
        return;
    }

    var cluster_id = $(document).getUrlParam('cluster') || '1';

    var failures = [];
    for (var record_index = 0; record_index < timeline.length; record_index++) {
        var record = timeline[record_index];
        if (record.outcome === 'error' || record.outcome === 'timeout') {
            failures.push(record);
        }
    }

    if (failures.length === 0) {
        container.html(all_clear_html);
        $('#dashboard-failures-count').text('0');
        return;
    }

    $.fn.zato.scheduler.dashboard._set_number($('#dashboard-failures-count'), failures.length);

    var html = '<table class="zato-table"><thead><tr>';
    html += '<th>Time</th><th>Job</th><th>Outcome</th><th>Error</th>';
    html += '</tr></thead><tbody>';

    var max_failures = Math.min(10, failures.length);
    for (var failure_index = 0; failure_index < max_failures; failure_index++) {
        var failure = failures[failure_index];
        var time_text = $.fn.zato.scheduler.dashboard.relative_time_past(failure.actual_fire_time_iso);
        var time_tooltip = $.fn.zato.scheduler.dashboard.format_local_time(failure.actual_fire_time_iso);
        var error_text = failure.error || '';
        var error_short = error_text.length > 80 ? error_text.substring(0, 80) + '...' : error_text;

        html += '<tr>';
        html += '<td style="font-family:monospace;font-feature-settings:\'tnum\' on;color:#6e6e73;white-space:nowrap" title="' + time_tooltip + '">' + time_text + '</td>';
        html += '<td><a href="/zato/scheduler/dashboard/job/' + encodeURIComponent(failure.job_id) + '/?cluster=' + cluster_id + '">' + (failure.job_name || failure.job_id) + '</a></td>';
        html += '<td>' + $.fn.zato.scheduler.dashboard.outcome_badge(failure.outcome) + '</td>';
        html += '<td class="dashboard-error-cell" title="' + error_text.replace(/"/g, '&quot;') + '">' + error_short + '</td>';
        html += '</tr>';
    }

    html += '</tbody></table>';
    container.html(html);
};

// ////////////////////////////////////////////////////////////////////////////
// Render upcoming runs table
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.render_upcoming_table = function(jobs) {
    var table_body = $('#dashboard-upcoming-table-body');
    table_body.empty();

    if (!jobs || jobs.length === 0) {
        table_body.append('<tr><td colspan="3" class="dashboard-no-data">No upcoming runs</td></tr>');
        $('#dashboard-upcoming-count').text('0');
        return;
    }

    var cluster_id = $(document).getUrlParam('cluster') || '1';

    var upcoming = [];

    for (var job_index = 0; job_index < jobs.length; job_index++) {
        var job = jobs[job_index];
        if (!job.is_active || !job.next_fire_utc) {
            continue;
        }

        upcoming.push({
            time: job.next_fire_utc,
            name: job.name,
            service: job.service,
            job_id: job.id
        });

        if (job.job_type === 'interval_based' && job.interval_ms && job.interval_ms > 0) {
            var fire_time = new Date(job.next_fire_utc).getTime();
            var interval = parseInt(job.interval_ms, 10);
            for (var projection_index = 1; projection_index < 5; projection_index++) {
                var projected_time = fire_time + (projection_index * interval);
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

    var max_upcoming = Math.min(15, upcoming.length);
    $('#dashboard-upcoming-count').text(upcoming.length);
    if (max_upcoming === 0) {
        table_body.append('<tr><td colspan="3" class="dashboard-no-data">No upcoming runs</td></tr>');
        return;
    }

    for (var upcoming_index = 0; upcoming_index < max_upcoming; upcoming_index++) {
        var entry = upcoming[upcoming_index];
        var time_text = $.fn.zato.scheduler.dashboard.relative_time_future(entry.time);
        var time_tooltip = $.fn.zato.scheduler.dashboard.format_local_time(entry.time);

        var service_cell = '';
        if (entry.service) {
            var service_url = '/zato/service/overview/' + encodeURIComponent(entry.service) + '/?cluster=' + cluster_id;
            service_cell = '<a href="' + service_url + '">' + entry.service + '</a>';
        }

        var row = '<tr>';
        row += '<td style="font-family:monospace;font-feature-settings:\'tnum\' on;color:#6e6e73;white-space:nowrap" title="' + time_tooltip + '">' + time_text + '</td>';
        row += '<td><a href="/zato/scheduler/dashboard/job/' + encodeURIComponent(entry.job_id) + '/?cluster=' + cluster_id + '">' + entry.name + '</a></td>';
        row += '<td>' + service_cell + '</td>';
        row += '</tr>';
        table_body.append(row);
    }
};

// ////////////////////////////////////////////////////////////////////////////
// Execute job
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.execute_job = function(job_id) {
    var cluster_id = $(document).getUrlParam('cluster') || '1';
    var url = '/zato/scheduler/execute/' + job_id + '/cluster/' + cluster_id + '/';

    $.ajax({
        url: url,
        type: 'POST',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function() {
            $.fn.zato.user_message(true, 'OK, request submitted');
        },
        error: function(xhr) {
            $.fn.zato.user_message(false, xhr.responseText || 'Error executing job');
        }
    });
};

// ////////////////////////////////////////////////////////////////////////////
// Update refresh indicator
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.update_refresh_indicator = function() {
};

// ////////////////////////////////////////////////////////////////////////////
// Correlated tile hover
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard._tile_hover_ready = false;

$.fn.zato.scheduler.dashboard._tile_hover_specs = [
    {sel: '#spark-total-jobs', key: 'total_jobs', label: 'Total jobs', color: '#82ccff'},
    {sel: '#spark-active', key: 'active', label: 'Active', color: '#82ccff'},
    {sel: '#spark-paused', key: 'paused', label: 'Paused', color: '#82ccff'},
    {sel: '#spark-runs', key: 'runs', label: 'Runs', color: '#82ccff'},
    {sel: '#spark-failures', key: 'failures', label: 'Failures', color: '#ff6b6b'}
];

$.fn.zato.scheduler.dashboard._clear_tile_hover = function() {
    var specs = $.fn.zato.scheduler.dashboard._tile_hover_specs;
    for (var i = 0; i < specs.length; i++) {
        $.fn.zato.dashboard_kit.sparkline.clear_overlay(specs[i].sel);
    }
    $('#dashboard-tile-tooltip').css('display', 'none');
};

$.fn.zato.scheduler.dashboard._schedule_clear_tile_hover = function() {
    var dash = $.fn.zato.scheduler.dashboard;
    dash._cancel_clear_tile_hover();
    dash._tile_hover_clear_timer = setTimeout(function() {
        dash._tile_hover_clear_timer = null;
        dash._clear_tile_hover();
    }, 80);
};

$.fn.zato.scheduler.dashboard._cancel_clear_tile_hover = function() {
    var dash = $.fn.zato.scheduler.dashboard;
    if (dash._tile_hover_clear_timer) {
        clearTimeout(dash._tile_hover_clear_timer);
        dash._tile_hover_clear_timer = null;
    }
};

$.fn.zato.scheduler.dashboard._show_tile_hover = function(active_sel, mouse_event) {
    var dash = $.fn.zato.scheduler.dashboard;
    dash._cancel_clear_tile_hover();
    var specs = dash._tile_hover_specs;
    var registry = $.fn.zato.dashboard_kit.sparkline.registry();
    var active_entry = registry[active_sel];
    if (!active_entry) return;

    var $spark = $(active_sel);
    var rect = $spark[0].getBoundingClientRect();
    var mouse_x_px = mouse_event.clientX - rect.left;
    var container_px_w = rect.width;

    if (mouse_x_px < 0) mouse_x_px = 0;
    if (mouse_x_px > container_px_w) mouse_x_px = container_px_w;

    var scale = (container_px_w > 0 && active_entry.pixel_width > 0)
        ? (active_entry.pixel_width / container_px_w) : 1;
    var logical_x = mouse_x_px * scale;

    var n = active_entry.data_points.length;
    var nearest_index = 0;
    var nearest_d = Infinity;
    for (var i = 0; i < n; i++) {
        var d = Math.abs(active_entry.xs[i] - logical_x);
        if (d < nearest_d) {
            nearest_d = d;
            nearest_index = i;
        }
    }

    var active_key = null;
    for (var ak = 0; ak < specs.length; ak++) {
        if (specs[ak].sel === active_sel) {
            active_key = specs[ak].key;
            break;
        }
    }
    var active_buffer = active_key ? dash._spark_data[active_key] : null;
    if (!active_buffer || !active_buffer[nearest_index]) return;

    /* Anchor correlation to a real timestamp on the hovered sparkline.
       Every other tile's sparkline is matched by nearest ts, which is
       correct regardless of different buffer lengths or sampling cadences. */
    var target_ts = active_buffer[nearest_index].ts;

    var now_ms = Date.now();
    var seconds_ago = Math.max(0, Math.round((now_ms - target_ts) / 1000));
    var header_title = dash._format_ago(seconds_ago);

    var tooltip_rows = [];
    tooltip_rows.push('<div class="dashboard-tooltip-header">' +
        '<div class="dashboard-tooltip-title">' + header_title + '</div>' +
        '</div>');

    for (var s2 = 0; s2 < specs.length; s2++) {
        var spec = specs[s2];
        var entry = registry[spec.sel];
        var spec_buffer = dash._spark_data[spec.key];

        var mapped_index = -1;
        if (spec_buffer && spec_buffer.length > 0) {
            var best_d = Infinity;
            for (var bi = 0; bi < spec_buffer.length; bi++) {
                var dt = Math.abs(spec_buffer[bi].ts - target_ts);
                if (dt < best_d) {
                    best_d = dt;
                    mapped_index = bi;
                }
            }
        }

        var val;
        if (mapped_index >= 0) {
            val = dash._format_number_full(spec_buffer[mapped_index].value);
            if (entry) {
                $.fn.zato.dashboard_kit.sparkline.show_marker(spec.sel, mapped_index, spec.color);
            }
        } else {
            val = '\u2013';
        }

        tooltip_rows.push('<div class="dashboard-tile-tooltip-row">' +
            '<span class="dashboard-tile-tooltip-dot" style="background:' + spec.color + '"></span>' +
            '<span class="dashboard-tile-tooltip-label">' + spec.label + '</span>' +
            '<span class="dashboard-tile-tooltip-value">' + val + '</span>' +
            '</div>');
    }

    var $tooltip = $('#dashboard-tile-tooltip');
    if ($tooltip.length === 0) {
        $('body').append('<div id="dashboard-tile-tooltip" class="dashboard-tile-tooltip"></div>');
        $tooltip = $('#dashboard-tile-tooltip');
    }

    $tooltip.html(tooltip_rows.join(''));

    /* The tooltip may still be display:none from a previous mouseleave
       cycle; measurements on a hidden element are unreliable. Make it
       renderable but invisible so outerWidth/outerHeight return stable
       values, then place it in a single css() call at the end. */
    $tooltip.css({display: 'block', visibility: 'hidden', left: '0px', top: '0px'});

    var tt_w = $tooltip.outerWidth();
    var tt_h = $tooltip.outerHeight();
    var margin = 8;
    var viewport_w = $(window).width();
    var viewport_h = $(window).height();

    /* Anchor the tooltip to the tile itself (centred above it) rather than
       to the mouse. This keeps the tooltip rock-steady while the mouse
       moves around inside the tile, and prevents the viewport clamp from
       kicking in for tiles that aren't actually near the screen edge. */
    var $tile = $spark.closest('.dashboard-tile');
    var tile_rect = $tile.length ? $tile[0].getBoundingClientRect() : rect;
    var gap = 10;
    var tile_cx = tile_rect.left + tile_rect.width / 2;

    var left = tile_cx - tt_w / 2;
    var top = tile_rect.top - tt_h - gap;

    /* If there isn't enough room above the tile, drop the tooltip below it. */
    if (top < margin) {
        top = tile_rect.bottom + gap;
    }

    /* Final viewport clamp — only fires when the tile is genuinely close
       to the screen edge, not when the mouse is moving around inside a
       centrally-located tile. */
    if (left + tt_w + margin > viewport_w) {
        left = viewport_w - tt_w - margin;
    }
    if (left < margin) {
        left = margin;
    }
    if (top + tt_h + margin > viewport_h) {
        top = viewport_h - tt_h - margin;
    }
    if (top < margin) {
        top = margin;
    }

    $tooltip.css({visibility: 'visible', left: left + 'px', top: top + 'px'});
};

$.fn.zato.scheduler.dashboard._setup_tile_hover = function() {
    var dash = $.fn.zato.scheduler.dashboard;
    if (dash._tile_hover_ready) return;

    var specs = dash._tile_hover_specs;
    var bound_any = false;

    for (var i = 0; i < specs.length; i++) {
        (function(sel) {
            var $spark = $(sel);
            if (!$spark.length) return;
            var $tile = $spark.closest('.dashboard-tile');
            if (!$tile.length) return;
            bound_any = true;
            $tile.css('cursor', 'crosshair');
            $tile.off('mousemove.tilehover mouseleave.tilehover');
            $tile.on('mousemove.tilehover', function(event) {
                dash._show_tile_hover(sel, event);
            });
            $tile.on('mouseleave.tilehover', function() {
                dash._schedule_clear_tile_hover();
            });
        })(specs[i].sel);
    }

    if (bound_any) {
        dash._tile_hover_ready = true;
    }
};

// ////////////////////////////////////////////////////////////////////////////
// Main render
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.render = function(data) {
    if (!data) {
        return;
    }

    var total_jobs = data.total_jobs || 0;
    var active_jobs = data.active_jobs || 0;
    var paused_jobs = data.paused_jobs || 0;
    var total_executions = data.total_executions || 0;

    var outcome_counts = data.outcome_counts || {};
    var failures_lifetime = (outcome_counts['error'] || 0) + (outcome_counts['timeout'] || 0);

    var dash = $.fn.zato.scheduler.dashboard;
    var set_number = dash._set_number;
    var fmt_full = dash._format_number_full;
    var fmt_compact = dash._format_number_compact;

    dash._seed_spark_buffers(data);

    dash._push_spark('total_jobs', total_jobs);
    dash._push_spark('active', active_jobs);
    dash._push_spark('paused', paused_jobs);

    /* Runs and failures are both recomputed from the fresh history on
       every render so their sparklines (last 1 h, bucketed per minute)
       and big digits (sum over the last hour) always tell the same
       story. */
    var runs_last_hour = dash._rebuild_runs_series(data.history_timeline);
    var failures_last_hour = dash._rebuild_failures_series(data.history_timeline);

    set_number($('#stat-total-jobs'), total_jobs);
    set_number($('#stat-active'), active_jobs);
    set_number($('#stat-paused'), paused_jobs);
    set_number($('#stat-runs'), runs_last_hour);
    set_number($('#stat-failures'), failures_last_hour);

    if (failures_last_hour > 0) {
        $('#stat-failures').css('color', '#ff6b6b');
    } else {
        $('#stat-failures').css('color', '#fff');
    }

    var runs_sub = fmt_compact(total_executions) + ' total';
    $('#stat-runs-sublabel')
        .text(runs_sub)
        .attr('title', fmt_full(total_executions) + ' total');
    var failures_sub = fmt_compact(failures_lifetime) + ' total';
    $('#stat-failures-sublabel')
        .text(failures_sub)
        .attr('title', fmt_full(failures_lifetime) + ' total');

    var base_spark = {height: 36, color: '#82ccff', dot_color: '#82ccff', dot_radius: 3.5};
    var base_spark_err = {height: 36, color: '#ff6b6b', dot_color: '#ff6b6b', dot_radius: 3.5};

    var tile_specs = [
        {sel: '#spark-total-jobs', key: 'total_jobs', opts: base_spark, dot_style: 'filled_halo'},
        {sel: '#spark-active', key: 'active', opts: base_spark, dot_style: 'filled_halo'},
        {sel: '#spark-paused', key: 'paused', opts: base_spark, dot_style: 'filled_halo'},
        {sel: '#spark-runs', key: 'runs', opts: base_spark, dot_style: 'filled_halo'},
        {sel: '#spark-failures', key: 'failures', opts: base_spark_err, dot_style: 'filled_halo'}
    ];

    for (var tile_i = 0; tile_i < tile_specs.length; tile_i++) {
        var spec = tile_specs[tile_i];
        var merged = $.extend({}, spec.opts, {dot_style: spec.dot_style});
        var values = $.fn.zato.scheduler.dashboard._spark_values(spec.key);
        $.fn.zato.dashboard_kit.sparkline.render(spec.sel, values, merged);
    }

    $.fn.zato.scheduler.dashboard._setup_tile_hover();

    $.fn.zato.scheduler.dashboard.render_bar_chart(data.history_timeline);
    $.fn.zato.scheduler.dashboard.render_job_table(data.jobs);
    $.fn.zato.scheduler.dashboard.render_failures(data.history_timeline);
    $.fn.zato.scheduler.dashboard.render_upcoming_table(data.jobs);

    var timeline = data.history_timeline || [];
    var failures_total = 0;
    for (var fi = 0; fi < timeline.length; fi++) {
        var oc = timeline[fi].outcome;
        if (oc === 'error' || oc === 'timeout') failures_total++;
    }
    if (typeof $.fn.zato.scheduler.dashboard._auto_activate_activity_tab === 'function') {
        $.fn.zato.scheduler.dashboard._auto_activate_activity_tab(failures_total);
    }

    $.fn.zato.scheduler.dashboard.update_refresh_indicator();
};

// ////////////////////////////////////////////////////////////////////////////
// Poll
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.poll = function() {
    $.ajax({
        url: '/zato/scheduler/dashboard/poll/',
        type: 'POST',
        data: {},
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            if (typeof data === 'string') {
                try {
                    data = JSON.parse(data);
                } catch(parse_error) {
                    return;
                }
            }
            $.fn.zato.scheduler.dashboard.render(data);
        },
        error: function() {}
    });
};

// ////////////////////////////////////////////////////////////////////////////
// Init
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.init = function(initial_data) {
    if (typeof initial_data === 'string') {
        try {
            initial_data = JSON.parse(initial_data);
        } catch(parse_error) {
            initial_data = {};
        }
    }

    try {
        var stored_bars = localStorage.getItem('zato_scheduler_show_bars');
        if (stored_bars === 'true') {
            $.fn.zato.scheduler.dashboard.show_bars = true;
        }
    } catch(e) {}
    $.fn.zato.scheduler.dashboard._update_chart_type_icon();

    $('#dashboard-chart-type-toggle').on('click', function() {
        $.fn.zato.scheduler.dashboard.show_bars = !$.fn.zato.scheduler.dashboard.show_bars;
        try { localStorage.setItem('zato_scheduler_show_bars', String($.fn.zato.scheduler.dashboard.show_bars)); } catch(e) {}
        $.fn.zato.scheduler.dashboard._update_chart_type_icon();
        $.fn.zato.scheduler.dashboard._redraw_chart_from_cache();
    });

    $.fn.zato.scheduler.dashboard._time_range_minutes = $.fn.zato.scheduler.dashboard._get_time_range_minutes();

    var menu = $('#dashboard-time-range-menu');
    var pill = $('#dashboard-exec-count');
    var stored_range = $.fn.zato.scheduler.dashboard._time_range_minutes;
    menu.find('.dashboard-time-range-option').removeClass('dashboard-time-range-active');
    menu.find('.dashboard-time-range-option[data-minutes="' + stored_range + '"]').addClass('dashboard-time-range-active');

    pill.on('click', function(event) {
        event.stopPropagation();
        menu.toggleClass('dashboard-time-range-menu-open');
    });

    menu.on('click', '.dashboard-time-range-option', function(event) {
        event.stopPropagation();
        var minutes = parseInt($(this).data('minutes'), 10);
        $.fn.zato.scheduler.dashboard._set_time_range_minutes(minutes);
        menu.find('.dashboard-time-range-option').removeClass('dashboard-time-range-active');
        $(this).addClass('dashboard-time-range-active');
        menu.removeClass('dashboard-time-range-menu-open');
        $.fn.zato.scheduler.dashboard._redraw_chart_from_cache();
    });

    $(document).on('click', function() {
        menu.removeClass('dashboard-time-range-menu-open');
    });

    var chart_container = document.getElementById('dashboard-bar-chart');
    if (chart_container && !chart_container._zato_wheel_bound) {
        chart_container._zato_wheel_bound = true;
        chart_container.addEventListener('wheel', function(event) {
            event.preventDefault();
            var current = $.fn.zato.scheduler.dashboard._zoom_bucket_count || 0;
            if (!current) {
                var w = chart_container.offsetWidth || 800;
                current = Math.min(60, Math.max(12, Math.floor(w / 16)));
            }
            if (event.deltaY < 0) {
                current = Math.max(4, Math.round(current * 0.8));
            } else {
                current = Math.min(120, Math.round(current * 1.25));
            }
            $.fn.zato.scheduler.dashboard._zoom_bucket_count = current;
            $.fn.zato.scheduler.dashboard._skip_legend_rebuild = true;
            $.fn.zato.scheduler.dashboard.render_bar_chart($.fn.zato.scheduler.dashboard._last_timeline);
            $.fn.zato.scheduler.dashboard._skip_legend_rebuild = false;
        }, {passive: false});
    }

    /* Activity card tabs. The selected tab persists across polls via a
       module-level flag so a refresh doesn't jump the user back to
       "failures". On first load we look at localStorage, defaulting to
       "failures" because that's what you want to see if anything is on
       fire; `_auto_activate_activity_tab` on the first render will flip
       to "upcoming" if there's nothing to worry about. */
    try {
        var stored_tab = localStorage.getItem('zato_scheduler_activity_tab');
        if (stored_tab === 'failures' || stored_tab === 'upcoming') {
            $.fn.zato.scheduler.dashboard._activity_tab = stored_tab;
        }
    } catch(e) {}
    if (!$.fn.zato.scheduler.dashboard._activity_tab) {
        $.fn.zato.scheduler.dashboard._activity_tab = 'failures';
    }
    $.fn.zato.scheduler.dashboard._activity_tab_user_chose = false;

    /* Mousedown: prevent the default focus behaviour that would make
       the browser scroll the clicked button into view (and also
       suppresses the global button:focus styles from formalize.css
       from flashing on). The actual tab switch still runs on click,
       so keyboard activation with Space/Enter keeps working. */
    $(document).on('mousedown', '.dashboard-tab', function(event) {
        event.preventDefault();
    });

    $(document).on('click', '.dashboard-tab', function(event) {
        event.preventDefault();
        var tab = $(this).data('tab');
        $.fn.zato.scheduler.dashboard._activity_tab = tab;
        $.fn.zato.scheduler.dashboard._activity_tab_user_chose = true;
        try { localStorage.setItem('zato_scheduler_activity_tab', tab); } catch(e) {}

        /* Capture scroll, switch panels, then keep forcing scroll back
           to the captured position for a short window. Firefox does
           scroll-anchoring style adjustments a frame or two AFTER the
           click handler returns, so a single scrollTo isn't enough.
           We install a temporary scroll listener that snaps the
           viewport back for ~300ms, which covers the entire style and
           layout commit for the panel swap. */
        var scroll_x = window.pageXOffset || document.documentElement.scrollLeft || 0;
        var scroll_y = window.pageYOffset || document.documentElement.scrollTop || 0;
        try { this.blur(); } catch(e) {}

        var locking = true;
        var snap_back = function() {
            if (!locking) return;
            if (window.pageXOffset !== scroll_x || window.pageYOffset !== scroll_y) {
                window.scrollTo(scroll_x, scroll_y);
            }
        };
        window.addEventListener('scroll', snap_back, true);

        $.fn.zato.scheduler.dashboard._apply_activity_tab();
        window.scrollTo(scroll_x, scroll_y);

        var deadline = Date.now() + 300;
        var tick = function() {
            snap_back();
            if (Date.now() < deadline) {
                window.requestAnimationFrame(tick);
            } else {
                locking = false;
                window.removeEventListener('scroll', snap_back, true);
            }
        };
        if (typeof window.requestAnimationFrame === 'function') {
            window.requestAnimationFrame(tick);
        } else {
            setTimeout(function() {
                locking = false;
                window.removeEventListener('scroll', snap_back, true);
            }, 300);
        }
    });

    $.fn.zato.scheduler.dashboard._apply_activity_tab();

    $.fn.zato.scheduler.dashboard.render(initial_data);
    $('.dashboard-page').css('opacity', '1');
    setInterval($.fn.zato.scheduler.dashboard.poll, $.fn.zato.scheduler.dashboard._poll_interval_ms);
};

$.fn.zato.scheduler.dashboard._apply_activity_tab = function() {
    var tab = $.fn.zato.scheduler.dashboard._activity_tab || 'failures';
    $('.dashboard-tab').each(function() {
        var is_active = $(this).data('tab') === tab;
        $(this).toggleClass('dashboard-tab-active', is_active);
        $(this).attr('aria-selected', is_active ? 'true' : 'false');
    });
    $('#dashboard-tab-panel-failures').prop('hidden', tab !== 'failures');
    $('#dashboard-tab-panel-upcoming').prop('hidden', tab !== 'upcoming');
};

$.fn.zato.scheduler.dashboard._auto_activate_activity_tab = function(failures_count) {
    /* On the very first render, if the user hasn't picked a tab yet and
       there are no failures, jump to Upcoming runs so the right column
       actually shows something. Any later click (user choice) locks the
       selection. */
    var dash = $.fn.zato.scheduler.dashboard;
    if (dash._activity_tab_seeded) return;
    dash._activity_tab_seeded = true;
    if (dash._activity_tab_user_chose) return;
    if (dash._activity_tab === 'failures' && failures_count === 0) {
        dash._activity_tab = 'upcoming';
        dash._apply_activity_tab();
    }
};
