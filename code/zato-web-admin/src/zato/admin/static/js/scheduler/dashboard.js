
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
    'skipped_concurrent': '#6a4c93',
    'missed_catchup': '#0077b6'
};

$.fn.zato.scheduler.dashboard.outcome_bg_colors = {
    'ok': 'rgba(27, 133, 94, 0.12)',
    'error': 'rgba(224, 34, 110, 0.12)',
    'timeout': 'rgba(179, 94, 0, 0.12)',
    'skipped_concurrent': 'rgba(106, 76, 147, 0.12)',
    'missed_catchup': 'rgba(0, 119, 182, 0.12)'
};

$.fn.zato.scheduler.dashboard.outcome_bar_colors = {
    'ok': '#2d8f45',
    'error': '#c0392b',
    'timeout': '#b45309',
    'skipped_concurrent': '#7c3aed',
    'missed_catchup': '#1a6fa0'
};

$.fn.zato.scheduler.dashboard.outcome_bar_tints = {
    'ok': '#d4edda',
    'error': '#f5d5d2',
    'timeout': '#fde8cd',
    'skipped_concurrent': '#ede5fb',
    'missed_catchup': '#d1e8f4'
};

$.fn.zato.scheduler.dashboard.outcome_labels = {
    'ok': 'OK',
    'error': 'Error',
    'timeout': 'Timeout',
    'skipped_concurrent': 'Skipped (concurrent)',
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
    var toggle = $('#scheduler-chart-type-toggle');
    if ($.fn.zato.scheduler.dashboard.show_bars) {
        toggle.html($.fn.zato.scheduler.dashboard._icon_lines);
        toggle.attr('title', 'Switch to area chart');
    } else {
        toggle.html($.fn.zato.scheduler.dashboard._icon_bars);
        toggle.attr('title', 'Switch to bar chart');
    }
};

$.fn.zato.scheduler.dashboard._spark_data = {
    total_jobs: [],
    active: [],
    paused: [],
    in_flight: [],
    failures: []
};

$.fn.zato.scheduler.dashboard._push_spark = function(key, value) {
    var data = $.fn.zato.scheduler.dashboard._spark_data[key];
    data.push(value);
    if (data.length > 60) {
        data.shift();
    }
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
        return 'overdue';
    }
    if (diff_seconds < 60) {
        return 'in ' + diff_seconds + 's';
    }
    if (diff_seconds < 3600) {
        return 'in ' + Math.floor(diff_seconds / 60) + 'm';
    }
    if (diff_seconds < 86400) {
        return 'in ' + Math.floor(diff_seconds / 3600) + 'h';
    }
    return 'in ' + Math.floor(diff_seconds / 86400) + 'd';
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
    if (job.in_flight) {
        return '<span class="scheduler-status-dot scheduler-status-in-flight" title="In-flight"></span>';
    }
    if (!job.is_active) {
        return '<span class="scheduler-status-dot scheduler-status-paused" title="Paused"></span>';
    }
    if (job.last_outcome === 'error' || job.last_outcome === 'timeout') {
        return '<span class="scheduler-status-dot scheduler-status-failed" title="Last run failed"></span>';
    }
    return '<span class="scheduler-status-dot scheduler-status-ok" title="Active"></span>';
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
        html += '<span class="scheduler-outcome-square" style="background:' + color + '" title="' + label + '"></span>';
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
    return '<span class="scheduler-outcome-badge" style="color:' + color + ';background:' + bg + '">' + label + '</span>';
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
    var container = $('#scheduler-bar-chart');
    var filtered = $.fn.zato.scheduler.dashboard._filter_timeline_by_range(timeline);

    if (!filtered || filtered.length === 0) {
        container.html('<div class="scheduler-no-data">No execution history yet</div>');
        $('#scheduler-chart-legend').empty();
        $('#scheduler-exec-count').text('');
        return;
    }

    var range_minutes = $.fn.zato.scheduler.dashboard._time_range_minutes;
    var range_names = {5: '5 min', 15: '15 min', 30: '30 min', 60: '1 hour', 360: '6 hours', 1440: 'Today', 2880: 'Yesterday', 10080: 'This week', 43200: 'This month', 525600: 'This year'};
    var range_label;
    if (range_minutes > 0 && range_names[range_minutes]) {
        range_label = range_names[range_minutes] + ' \u00b7 ' + filtered.length + ' runs';
    } else {
        range_label = 'All \u00b7 ' + filtered.length + ' runs';
    }
    $('#scheduler-exec-count').text(range_label);

    var chart_width = container.width() || 800;
    var chart_height = 200;
    var padding_left = 40;
    var padding_bottom = 28;
    var padding_top = 12;
    var padding_right = 8;

    var outcome_keys = ['ok', 'error', 'timeout', 'skipped_concurrent', 'missed_catchup'];
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
        container.html('<div class="scheduler-no-data">No execution history yet</div>');
        $('#scheduler-chart-legend').empty();
        $('#scheduler-exec-count').text('');
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
        var legend_container = $('#scheduler-chart-legend');
        var outcome_text_colors = $.fn.zato.scheduler.dashboard.outcome_colors;
        var outcome_bg = $.fn.zato.scheduler.dashboard.outcome_bg_colors;
        legend_container.empty();
        for (var legend_index = 0; legend_index < outcome_keys.length; legend_index++) {
            var legend_key = outcome_keys[legend_index];
            var is_hidden = !!hidden_outcomes[legend_key];
            var text_color = outcome_text_colors[legend_key] || '#6e6e73';
            var bg_color = outcome_bg[legend_key] || 'rgba(110,110,115,0.12)';
            var dot_color = bar_colors[legend_key];
            var item = $('<span class="scheduler-legend-badge' + (is_hidden ? ' scheduler-legend-badge-off' : '') + '" data-outcome="' + legend_key + '"></span>');
            item.css({'color': text_color, 'background': bg_color});
            item.append('<span class="scheduler-legend-badge-dot" style="background:' + dot_color + '"></span>');
            item.append(labels[legend_key]);
            legend_container.append(item);
        }
        legend_container.off('click.toggle').on('click.toggle', '.scheduler-legend-badge', function() {
            var el = $(this);
            var key = el.data('outcome');
            el.toggleClass('scheduler-legend-badge-off');
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

    var overlay = container.find('.scheduler-chart-overlay');
    if (overlay.length === 0) {
        container.css('position', 'relative');
        container.append('<div class="scheduler-chart-overlay"></div>');
        overlay = container.find('.scheduler-chart-overlay');
    }
    overlay.css({position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', 'pointer-events': 'none'});

    var tooltip = $('#scheduler-chart-tooltip');
    if (tooltip.length === 0) {
        $('body').append('<div id="scheduler-chart-tooltip" class="scheduler-chart-tooltip"></div>');
        tooltip = $('#scheduler-chart-tooltip');
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
                band_html += '<circle cx="' + pt.x.toFixed(1) + '" cy="' + pt.y.toFixed(1) + '" r="4.5" fill="#fff" stroke="' + bar_colors[dk_key] + '" stroke-width="2" />';
            }
        }
        band_html += '</svg>';
        overlay.html(band_html);

        var bucket = buckets[bucket_index];
        var tooltip_lines = [];
        var time_start = new Date(bucket.start);
        var time_label = ('0' + time_start.getHours()).slice(-2) + ':' + ('0' + time_start.getMinutes()).slice(-2) + ':' + ('0' + time_start.getSeconds()).slice(-2);
        tooltip_lines.push('<span style="font-weight:700">' + time_label + '</span>');

        for (var key_index = 0; key_index < visible_keys.length; key_index++) {
            var key = visible_keys[key_index];
            var count = bucket[key] || 0;
            tooltip_lines.push('<span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:' + bar_colors[key] + ';margin-right:5px"></span>' + (labels[key] || key) + ': <b>' + count + '</b>');
        }

        tooltip.html(tooltip_lines.join('<br>'));
        tooltip.css({
            display: 'block',
            left: (event.clientX + 14) + 'px',
            top: (event.clientY - 14) + 'px'
        });
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
    var table_body = $('#scheduler-job-table-body');
    table_body.empty();

    if (!jobs || jobs.length === 0) {
        table_body.append('<tr><td colspan="5" class="scheduler-no-data">No jobs</td></tr>');
        $('#scheduler-jobs-count').text('');
        return;
    }

    var cluster_id = $(document).getUrlParam('cluster') || '1';

    $('#scheduler-jobs-count').text(jobs.length);

    jobs.sort(function(first, second) {
        return (first.name || '').localeCompare(second.name || '');
    });

    for (var job_index = 0; job_index < jobs.length; job_index++) {
        var job = jobs[job_index];
        var type_label = $.fn.zato.scheduler.dashboard.job_type_labels[job.job_type] || job.job_type;
        var next_fire_text = $.fn.zato.scheduler.dashboard.relative_time_future(job.next_fire_utc);
        var next_fire_tooltip = $.fn.zato.scheduler.dashboard.format_local_time(job.next_fire_utc);
        var detail_url = '/zato/scheduler/dashboard/job/' + encodeURIComponent(job.id) + '/?cluster=' + cluster_id;

        var row = '<tr data-href="' + detail_url + '">';
        row += '<td>' + $.fn.zato.scheduler.dashboard.status_dot(job) + '</td>';
        row += '<td><a href="' + detail_url + '">' + job.name + '</a></td>';
        row += '<td><span class="scheduler-type-badge">' + type_label + '</span></td>';
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
    var container = $('#scheduler-failures-body');
    container.empty();

    var all_clear_html = '<div class="scheduler-all-clear"><svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="7" stroke="#1b855e" stroke-width="1.5"/><path d="M5 8l2 2 4-4" stroke="#1b855e" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>All clear</div>';

    if (!timeline || timeline.length === 0) {
        container.html(all_clear_html);
        $('#scheduler-failures-count').text('0');
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
        $('#scheduler-failures-count').text('0');
        return;
    }

    $('#scheduler-failures-count').text(failures.length);

    var html = '<table class="scheduler-failures-table"><thead><tr>';
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
        html += '<td class="scheduler-error-cell" title="' + error_text.replace(/"/g, '&quot;') + '">' + error_short + '</td>';
        html += '</tr>';
    }

    html += '</tbody></table>';
    container.html(html);
};

// ////////////////////////////////////////////////////////////////////////////
// Render upcoming runs table
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.render_upcoming_table = function(jobs) {
    var table_body = $('#scheduler-upcoming-table-body');
    table_body.empty();

    if (!jobs || jobs.length === 0) {
        table_body.append('<tr><td colspan="4" class="scheduler-no-data">No upcoming runs</td></tr>');
        return;
    }

    var cluster_id = $(document).getUrlParam('cluster') || '1';

    var upcoming = [];

    for (var job_index = 0; job_index < jobs.length; job_index++) {
        var job = jobs[job_index];
        if (!job.is_active || !job.next_fire_utc) {
            continue;
        }

        var type_label = $.fn.zato.scheduler.dashboard.job_type_labels[job.job_type] || job.job_type;

        upcoming.push({
            time: job.next_fire_utc,
            name: job.name,
            service: job.service,
            type_label: type_label,
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
                    type_label: type_label,
                    job_id: job.id
                });
            }
        }
    }

    upcoming.sort(function(first, second) {
        return first.time.localeCompare(second.time);
    });

    var max_upcoming = Math.min(15, upcoming.length);
    if (max_upcoming === 0) {
        table_body.append('<tr><td colspan="4" class="scheduler-no-data">No upcoming runs</td></tr>');
        return;
    }

    for (var upcoming_index = 0; upcoming_index < max_upcoming; upcoming_index++) {
        var entry = upcoming[upcoming_index];
        var time_text = $.fn.zato.scheduler.dashboard.relative_time_future(entry.time);
        var time_tooltip = $.fn.zato.scheduler.dashboard.format_local_time(entry.time);

        var row = '<tr>';
        row += '<td style="font-family:monospace;font-feature-settings:\'tnum\' on;color:#6e6e73;white-space:nowrap" title="' + time_tooltip + '">' + time_text + '</td>';
        row += '<td><a href="/zato/scheduler/dashboard/job/' + encodeURIComponent(entry.job_id) + '/?cluster=' + cluster_id + '">' + entry.name + '</a></td>';
        row += '<td style="color:#6e6e73">' + entry.service + '</td>';
        row += '<td><span class="scheduler-type-badge">' + entry.type_label + '</span></td>';
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
// Main render
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.render = function(data) {
    if (!data) {
        return;
    }

    var total_jobs = data.total_jobs || 0;
    var active_jobs = data.active_jobs || 0;
    var paused_jobs = data.paused_jobs || 0;
    var in_flight_count = data.in_flight_count || 0;

    var outcome_counts = data.outcome_counts || {};
    var failure_count = (outcome_counts['error'] || 0) + (outcome_counts['timeout'] || 0);

    $('#stat-total-jobs').text(total_jobs);
    $('#stat-active').text(active_jobs);
    $('#stat-paused').text(paused_jobs);
    $('#stat-in-flight').text(in_flight_count);
    $('#stat-failures').text(failure_count);

    if (failure_count > 0) {
        $('#stat-failures').css('color', '#ff6b6b');
    } else {
        $('#stat-failures').css('color', '#fff');
    }

    $.fn.zato.scheduler.dashboard._push_spark('total_jobs', total_jobs);
    $.fn.zato.scheduler.dashboard._push_spark('active', active_jobs);
    $.fn.zato.scheduler.dashboard._push_spark('paused', paused_jobs);
    $.fn.zato.scheduler.dashboard._push_spark('in_flight', in_flight_count);
    $.fn.zato.scheduler.dashboard._push_spark('failures', failure_count);

    var spark_options = {width: 100, height: 28, color: '#82ccff', dot_color: '#82ccff', dot_radius: 2.5};
    var spark_options_failures = {width: 100, height: 28, color: '#ff6b6b', dot_color: '#ff6b6b', dot_radius: 2.5};

    $.fn.zato.eda.sparkline('#spark-total-jobs', $.fn.zato.scheduler.dashboard._spark_data.total_jobs, spark_options);
    $.fn.zato.eda.sparkline('#spark-active', $.fn.zato.scheduler.dashboard._spark_data.active, spark_options);
    $.fn.zato.eda.sparkline('#spark-paused', $.fn.zato.scheduler.dashboard._spark_data.paused, spark_options);
    $.fn.zato.eda.sparkline('#spark-in-flight', $.fn.zato.scheduler.dashboard._spark_data.in_flight, spark_options);
    $.fn.zato.eda.sparkline('#spark-failures', $.fn.zato.scheduler.dashboard._spark_data.failures, spark_options_failures);

    $.fn.zato.scheduler.dashboard.render_bar_chart(data.history_timeline);
    $.fn.zato.scheduler.dashboard.render_job_table(data.jobs);
    $.fn.zato.scheduler.dashboard.render_failures(data.history_timeline);
    $.fn.zato.scheduler.dashboard.render_upcoming_table(data.jobs);

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

    $('#scheduler-chart-type-toggle').on('click', function() {
        $.fn.zato.scheduler.dashboard.show_bars = !$.fn.zato.scheduler.dashboard.show_bars;
        try { localStorage.setItem('zato_scheduler_show_bars', String($.fn.zato.scheduler.dashboard.show_bars)); } catch(e) {}
        $.fn.zato.scheduler.dashboard._update_chart_type_icon();
        $.fn.zato.scheduler.dashboard._redraw_chart_from_cache();
    });

    $.fn.zato.scheduler.dashboard._time_range_minutes = $.fn.zato.scheduler.dashboard._get_time_range_minutes();

    var menu = $('#scheduler-time-range-menu');
    var pill = $('#scheduler-exec-count');
    var stored_range = $.fn.zato.scheduler.dashboard._time_range_minutes;
    menu.find('.scheduler-time-range-option').removeClass('scheduler-time-range-active');
    menu.find('.scheduler-time-range-option[data-minutes="' + stored_range + '"]').addClass('scheduler-time-range-active');

    pill.on('click', function(event) {
        event.stopPropagation();
        menu.toggleClass('scheduler-time-range-menu-open');
    });

    menu.on('click', '.scheduler-time-range-option', function(event) {
        event.stopPropagation();
        var minutes = parseInt($(this).data('minutes'), 10);
        $.fn.zato.scheduler.dashboard._set_time_range_minutes(minutes);
        menu.find('.scheduler-time-range-option').removeClass('scheduler-time-range-active');
        $(this).addClass('scheduler-time-range-active');
        menu.removeClass('scheduler-time-range-menu-open');
        $.fn.zato.scheduler.dashboard._redraw_chart_from_cache();
    });

    $(document).on('click', function() {
        menu.removeClass('scheduler-time-range-menu-open');
    });

    var chart_container = document.getElementById('scheduler-bar-chart');
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

    $.fn.zato.scheduler.dashboard.render(initial_data);
    $('.scheduler-page').css('opacity', '1');
    setInterval($.fn.zato.scheduler.dashboard.poll, 10000);
};
