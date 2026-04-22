
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.scheduler === 'undefined') { $.fn.zato.scheduler = {}; }
$.fn.zato.scheduler.dashboard = {};

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
        {label: 'Failures', href: '#'},
        {label: 'Upcoming', href: '#'}
    ] : [],
    row_recency_color: '218, 165, 32'
};

// ////////////////////////////////////////////////////////////////////////////
// Outcome color map - tinted badge palette (uses theme accent for OK)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.outcome_colors = {
    'ok': '#2a7fbf',
    'error': '#e0226e',
    'timeout': '#b35e00',
    'skipped_already_in_flight': '#7b5ea7',
    'missed_catchup': '#9a7b5a'
};

$.fn.zato.scheduler.dashboard.outcome_bg_colors = {
    'ok': 'rgba(42, 127, 191, 0.12)',
    'error': 'rgba(224, 34, 110, 0.12)',
    'timeout': 'rgba(179, 94, 0, 0.12)',
    'skipped_already_in_flight': 'rgba(123, 94, 167, 0.12)',
    'missed_catchup': 'rgba(154, 123, 90, 0.12)'
};

$.fn.zato.scheduler.dashboard.outcome_bar_colors = {
    'ok': '#3a9ad9',
    'error': '#c0392b',
    'timeout': '#b45309',
    'skipped_already_in_flight': '#6b4d94',
    'missed_catchup': '#8a6d4f'
};

$.fn.zato.scheduler.dashboard.outcome_bar_tints = {
    'ok': '#d1e8f8',
    'error': '#f5d5d2',
    'timeout': '#fde8cd',
    'skipped_already_in_flight': '#ddd0ef',
    'missed_catchup': '#e8ddd0'
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
// Kit aliases — keep short references for code that used the old local names
// ////////////////////////////////////////////////////////////////////////////

(function() {
    var kit = $.fn.zato.dashboard_kit;
    var dash = $.fn.zato.scheduler.dashboard;

    dash._poll_interval_ms = 10000;
    dash._recent_failure_ts = [];

    // Thin aliases so job_detail.js (and any future callers that used
    // the old scheduler-level API) keep working without changes.
    dash.format_duration = kit.format_duration_ms;
    dash.format_local_time = kit.format_local_time;
    dash.relative_time_future = kit.relative_time_future;
    dash.relative_time_past = kit.relative_time_past;

    // Spark buffers via kit
    dash._spark_buffers = kit.spark.create({
        keys: ['total_jobs', 'active', 'paused', 'runs', 'failures'],
        window_ms: 60 * 60 * 1000,
        bucket_count: 60
    });

    // ////////////////////////////////////////////////////////////////////////
    // Predicates for timeline filtering
    // ////////////////////////////////////////////////////////////////////////

    dash._is_failure = function(record) {
        return record.outcome === 'error' || record.outcome === 'timeout';
    };

    dash._is_execution = function(record) {
        var outcome = record.outcome;
        return outcome === 'ok' || outcome === 'error' || outcome === 'timeout';
    };

    var _ts_accessor = function(record) {
        var iso = record.actual_fire_time_iso;
        if (!iso) return NaN;
        return new Date(iso).getTime();
    };

    dash._rebuild_failures_series = function(timeline) {
        var result = kit.bucket_events_per_minute(
            timeline, dash._is_failure, _ts_accessor,
            dash._spark_buffers.window_ms(), 60
        );
        dash._spark_buffers.set_buffer('failures', result.series);
        return result.total;
    };

    dash._rebuild_runs_series = function(timeline) {
        var result = kit.bucket_events_per_minute(
            timeline, dash._is_execution, _ts_accessor,
            dash._spark_buffers.window_ms(), 60
        );
        dash._spark_buffers.set_buffer('runs', result.series);
        return result.total;
    };

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

    dash._last_timeline = null;
    dash._time_range_minutes = 0;

    dash._filter_timeline_by_range = function(timeline) {
        var minutes = dash._time_range_minutes;
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

    dash._skip_legend_rebuild = false;

    dash._zoom_bucket_count = 0;

    dash._redraw_chart_from_cache = function() {
        if (dash._last_timeline) {
            dash._skip_legend_rebuild = true;
            dash.render_bar_chart(dash._last_timeline);
            dash._skip_legend_rebuild = false;
        }
    };

    // ////////////////////////////////////////////////////////////////////////
    // Status dot
    // ////////////////////////////////////////////////////////////////////////

    dash.status_dot = function(job) {
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

    // ////////////////////////////////////////////////////////////////////////
    // Outcome micro-chart (colored squares)
    // ////////////////////////////////////////////////////////////////////////

    dash.outcome_squares = function(recent_outcomes) {
        if (!recent_outcomes || recent_outcomes.length === 0) {
            return '<span style="color:#a0a0a5">-</span>';
        }
        var bar_colors = dash.outcome_bar_colors;
        var labels = dash.outcome_labels;
        var html = '';
        for (var index = 0; index < recent_outcomes.length; index++) {
            var outcome = recent_outcomes[index];
            var color = bar_colors[outcome] || '#ccc';
            var label = labels[outcome] || outcome;
            html += '<span class="dashboard-outcome-square" style="background:' + color + '" title="' + label + '"></span>';
        }
        return html;
    };

    // ////////////////////////////////////////////////////////////////////////
    // Outcome badge (tinted background)
    // ////////////////////////////////////////////////////////////////////////

    dash.outcome_badge = function(outcome) {
        var colors = dash.outcome_colors;
        var bg_colors = dash.outcome_bg_colors;
        var labels = dash.outcome_labels;
        var color = colors[outcome] || '#6e6e73';
        var bg = bg_colors[outcome] || 'rgba(110,110,115,0.12)';
        var label = labels[outcome] || outcome;
        return '<span class="dashboard-outcome-badge" style="color:' + color + ';background:' + bg + '">' + label + '</span>';
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
    // Bar chart
    // ////////////////////////////////////////////////////////////////////////

    dash.render_bar_chart = function(timeline) {
        dash._last_timeline = timeline;
        var container = $('#dashboard-bar-chart');
        var filtered = dash._filter_timeline_by_range(timeline);

        if (!filtered || filtered.length === 0) {
            container.html('<div class="dashboard-no-data">No run history yet</div>');
            $('#dashboard-chart-legend').empty();
            $('#dashboard-exec-count').text('');
            return;
        }

        var range_minutes = dash._time_range_minutes;
        var range_names = {5: '5 min', 15: '15 min', 30: '30 min', 60: '1 hour', 360: '6 hours', 1440: 'Today', 2880: 'Yesterday', 10080: 'This week', 43200: 'This month', 525600: 'This year'};
        var filtered_exec_count = 0;
        for (var fe = 0; fe < filtered.length; fe++) {
            var foc = filtered[fe].outcome;
            if (foc === 'ok' || foc === 'error' || foc === 'timeout') {
                filtered_exec_count++;
            }
        }
        var filtered_count_label = filtered_exec_count === 1
            ? '1 run'
            : kit.format_number_compact(filtered_exec_count) + ' runs';
        var filtered_count_full = filtered_exec_count === 1
            ? '1 run'
            : kit.format_number_full(filtered_exec_count) + ' runs';
        var range_label;
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
        var bar_colors = dash.outcome_bar_colors;
        var labels = dash.outcome_labels;
        var hidden_outcomes = dash._get_hidden_outcomes();

        var timestamps = [];
        for (var record_index = 0; record_index < filtered.length; record_index++) {
            var timestamp_string = filtered[record_index].actual_fire_time_iso;
            if (timestamp_string) {
                timestamps.push(new Date(timestamp_string).getTime());
            }
        }

        if (timestamps.length === 0) {
            container.html('<div class="dashboard-no-data">No run history yet</div>');
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
        var bucket_count = dash._zoom_bucket_count > 0
            ? Math.min(120, Math.max(4, dash._zoom_bucket_count))
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
            if (target_bucket >= bucket_count) target_bucket = bucket_count - 1;
            if (target_bucket < 0) target_bucket = 0;
            if (buckets[target_bucket][outcome] !== undefined) {
                buckets[target_bucket][outcome]++;
            }
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

        var max_stack = 0;
        if (dash.show_bars) {
            for (var ms_index = 0; ms_index < buckets.length; ms_index++) {
                var ms_sum = 0;
                for (var ms_key = 0; ms_key < visible_keys.length; ms_key++) {
                    ms_sum += (buckets[ms_index][visible_keys[ms_key]] || 0);
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

        dash._setup_chart_interactions(container, buckets, padding_left, draw_width, bucket_count, padding_top, draw_height, padding_bottom, chart_height, visible_keys, layer_points, bar_colors);

        kit.build_legend({
            container: '#dashboard-chart-legend',
            series_keys: outcome_keys,
            palette: bar_colors,
            labels: labels,
            text_colors: dash.outcome_colors,
            bg_colors: dash.outcome_bg_colors,
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
                : kit.format_number_full(total_runs) + ' runs';

            var tooltip_html = '<div class="dashboard-tooltip-header">' +
                '<div class="dashboard-tooltip-title">' + time_label + '</div>' +
                '<div class="dashboard-tooltip-subtitle">' + runs_label + '</div>' +
                '</div>';

            var body_lines = [];
            for (var key_index = 0; key_index < visible_keys.length; key_index++) {
                var key = visible_keys[key_index];
                var count = bucket[key] || 0;
                body_lines.push('<div class="dashboard-tooltip-row">' +
                    '<span class="dashboard-tooltip-dot" style="background:' + bar_colors[key] + '"></span>' +
                    (labels[key] || key) + ': <b>' + kit.format_number_full(count) + '</b></div>');
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
        var table_body = $('#dashboard-job-table-body');
        table_body.empty();

        if (!jobs || jobs.length === 0) {
            table_body.append('<tr><td colspan="5" class="dashboard-no-data">No jobs</td></tr>');
            $('#dashboard-jobs-count').text('');
            return;
        }

        var cluster_id = $(document).getUrlParam('cluster') || '1';

        kit.set_number($('#dashboard-jobs-count'), jobs.length);

        jobs.sort(function(first, second) {
            return (first.name || '').localeCompare(second.name || '');
        });

        for (var job_index = 0; job_index < jobs.length; job_index++) {
            var job = jobs[job_index];
            var next_fire_text = kit.relative_time_future(job.next_fire_utc);
            var next_fire_tooltip = kit.format_local_time(job.next_fire_utc);
            var detail_url = '/zato/scheduler/dashboard/job/' + encodeURIComponent(job.id) + '/?cluster=' + cluster_id;

            var service_name = job.service || '';
            var service_cell = '';
            if (service_name) {
                var service_url = '/zato/service/overview/' + encodeURIComponent(service_name) + '/?cluster=' + cluster_id;
                service_cell = '<a href="' + service_url + '">' + service_name + '</a>';
            }

            var row = '<tr data-href="' + detail_url + '">';
            row += '<td>' + dash.status_dot(job) + '</td>';
            row += '<td><a href="' + detail_url + '">' + job.name + '</a></td>';
            row += '<td>' + service_cell + '</td>';
            row += '<td style="font-family:monospace;font-feature-settings:\'tnum\' on;color:#6e6e73" title="' + next_fire_tooltip + '">' + next_fire_text + '</td>';
            row += '<td>' + dash.outcome_squares(job.recent_outcomes) + '</td>';
            row += '</tr>';
            table_body.append(row);
        }

        table_body.find('tr[data-href]').on('click', function(event) {
            if ($(event.target).is('a')) return;
            window.location.href = $(this).data('href');
        });
    };

    // ////////////////////////////////////////////////////////////////////////
    // Render failures
    // ////////////////////////////////////////////////////////////////////////

    dash.render_failures = function(timeline) {
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

        kit.set_number($('#dashboard-failures-count'), failures.length);

        var html = '<table class="zato-table"><thead><tr>';
        html += '<th>Time</th><th>Job</th><th>Outcome</th><th>Error</th>';
        html += '</tr></thead><tbody>';

        var max_failures = Math.min(10, failures.length);
        for (var failure_index = 0; failure_index < max_failures; failure_index++) {
            var failure = failures[failure_index];
            var time_text = kit.relative_time_past(failure.actual_fire_time_iso);
            var time_tooltip = kit.format_local_time(failure.actual_fire_time_iso);
            var error_text = failure.error || '';
            var error_short = error_text.length > 80 ? error_text.substring(0, 80) + '...' : error_text;

            var f_ts = failure.actual_fire_time_iso || '';
            html += '<tr data-ts="' + f_ts + '">';
            html += '<td style="font-family:monospace;font-feature-settings:\'tnum\' on;color:#6e6e73;white-space:nowrap" title="' + time_tooltip + '">' + time_text + '</td>';
            html += '<td><a href="/zato/scheduler/dashboard/job/' + encodeURIComponent(failure.job_id) + '/?cluster=' + cluster_id + '">' + (failure.job_name || failure.job_id) + '</a></td>';
            html += '<td>' + dash.outcome_badge(failure.outcome) + '</td>';
            html += '<td class="dashboard-error-cell" title="' + error_text.replace(/"/g, '&quot;') + '">' + error_short + '</td>';
            html += '</tr>';
        }

        html += '</tbody></table>';
        container.html(html);
    };

    // ////////////////////////////////////////////////////////////////////////
    // Render upcoming runs table
    // ////////////////////////////////////////////////////////////////////////

    dash.render_upcoming_table = function(jobs) {
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
            if (!job.is_active || !job.next_fire_utc) continue;

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
            var time_text = kit.relative_time_future(entry.time);
            var time_tooltip = kit.format_local_time(entry.time);

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

    // ////////////////////////////////////////////////////////////////////////
    // Execute job
    // ////////////////////////////////////////////////////////////////////////

    dash.execute_job = function(job_id, trigger_elem) {
        var cluster_id = $(document).getUrlParam('cluster') || '1';
        var url = '/zato/scheduler/execute/' + job_id + '/cluster/' + cluster_id + '/';

        $.ajax({
            url: url,
            type: 'POST',
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function() {
                $.fn.zato.user_message(true, 'OK, job executed');
            },
            error: function(xhr) {
                $.fn.zato.user_message(false, xhr.responseText || 'Error executing job');
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////
    // Update refresh indicator
    // ////////////////////////////////////////////////////////////////////////

    dash.update_refresh_indicator = function() {
    };

    // ////////////////////////////////////////////////////////////////////////
    // Main render
    // ////////////////////////////////////////////////////////////////////////

    dash.render = function(data) {
        if (!data) return;

        var total_jobs = data.total_jobs;
        var active_jobs = data.active_jobs;
        var paused_jobs = data.paused_jobs;

        var outcome_counts = data.outcome_counts;
        var failures_lifetime = (outcome_counts['error'] || 0) + (outcome_counts['timeout'] || 0);

        var buffers = dash._spark_buffers;
        buffers.seed_flat({
            total_jobs: total_jobs,
            active: active_jobs,
            paused: paused_jobs
        });

        buffers.push('total_jobs', total_jobs);
        buffers.push('active', active_jobs);
        buffers.push('paused', paused_jobs);

        var runs_last_hour = dash._rebuild_runs_series(data.history_timeline);
        var failures_last_hour = dash._rebuild_failures_series(data.history_timeline);

        kit.set_number($('#stat-total-jobs'), total_jobs);
        kit.set_number($('#stat-active'), active_jobs);
        kit.set_number($('#stat-paused'), paused_jobs);
        kit.set_number($('#stat-runs'), runs_last_hour);
        kit.set_number($('#stat-failures'), failures_last_hour);

        if (failures_last_hour > 0) {
            $('#stat-failures').css('color', '#ff6b6b');
        } else {
            $('#stat-failures').css('color', '#fff');
        }

        var timeline = data.history_timeline;
        var timeline_total = 0;
        for (var ti = 0; ti < timeline.length; ti++) {
            var toc = timeline[ti].outcome;
            if (toc === 'ok' || toc === 'error' || toc === 'timeout') {
                timeline_total++;
            }
        }
        var runs_sub = kit.format_number_compact(timeline_total) + ' total';
        $('#stat-runs-sublabel')
            .text(runs_sub)
            .attr('title', kit.format_number_full(timeline_total) + ' total');
        var failures_sub = kit.format_number_compact(failures_lifetime) + ' total';
        $('#stat-failures-sublabel')
            .text(failures_sub)
            .attr('title', kit.format_number_full(failures_lifetime) + ' total');

        var _theme = dash.theme;
        var base_spark = {height: 36, color: _theme.spark_color, dot_color: _theme.spark_color, dot_radius: 3.5};
        var base_spark_err = {height: 36, color: _theme.spark_err, dot_color: _theme.spark_err, dot_radius: 3.5};

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
            var values = buffers.values(spec.key);
            kit.sparkline.render(spec.sel, values, merged);
        }

        if (dash._stat_tile_handle) {
            dash._stat_tile_handle.bind();
        }

        dash.render_bar_chart(data.history_timeline);
        dash.render_job_table(data.jobs);
        dash.render_failures(data.history_timeline);
        dash.render_upcoming_table(data.jobs);

        var failures_total = 0;
        for (var fi = 0; fi < timeline.length; fi++) {
            var oc = timeline[fi].outcome;
            if (oc === 'error' || oc === 'timeout') failures_total++;
        }
        if (dash._tabs_handle) {
            dash._tabs_handle.set_tab(
                failures_total === 0 ? 'upcoming' : 'failures'
            );
        }

        dash.update_refresh_indicator();
    };

    // ////////////////////////////////////////////////////////////////////////
    // Poll
    // ////////////////////////////////////////////////////////////////////////

    dash.poll = function() {
        var old_failure_ts = {};
        $('#dashboard-failures-body tr[data-ts]').each(function() {
            var ts = $(this).attr('data-ts');
            if (ts) old_failure_ts[ts] = true;
        });
        var had_failures = Object.keys(old_failure_ts).length > 0;

        $.ajax({
            url: '/zato/scheduler/dashboard/poll/',
            type: 'POST',
            data: {},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(data) {
                if (typeof data === 'string') {
                    try { data = JSON.parse(data); } catch(parse_error) { return; }
                }
                dash.render(data);

                if (had_failures) {
                    var new_list = [];
                    $('#dashboard-failures-body tr[data-ts]').each(function() {
                        var ts = $(this).attr('data-ts');
                        if (ts && !old_failure_ts[ts]) {
                            new_list.push(ts);
                        }
                    });
                    if (new_list.length > 0) {
                        dash._recent_failure_ts = new_list.concat(dash._recent_failure_ts);
                        dash._recent_failure_ts.length = Math.min(dash._recent_failure_ts.length, kit.recency.STEPS);
                    }
                }
                kit.recency.apply({
                    container: '#dashboard-failures-body tbody',
                    recent_ts: dash._recent_failure_ts,
                    rgb: dash.theme.row_recency_color
                });
            },
            error: function() {}
        });
    };

    // ////////////////////////////////////////////////////////////////////////
    // Init
    // ////////////////////////////////////////////////////////////////////////

    dash.init = function(initial_data) {
        if (typeof initial_data === 'string') {
            try { initial_data = JSON.parse(initial_data); } catch(parse_error) { initial_data = {}; }
        }

        // Hero pill — delegated to kit
        kit.init_hero_pill('#dashboard-hero-pill-group', dash.theme);

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

        // Time range
        dash._time_range_minutes = parseInt(kit.storage_get('zato_scheduler_time_range') || '0', 10) || 0;

        var menu = $('#dashboard-time-range-menu');
        var pill = $('#dashboard-exec-count');
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
            kit.storage_set('zato_scheduler_time_range', String(minutes));
            menu.find('.dashboard-time-range-option').removeClass('dashboard-time-range-active');
            $(this).addClass('dashboard-time-range-active');
            menu.removeClass('dashboard-time-range-menu-open');
            dash._redraw_chart_from_cache();
        });

        $(document).on('click', function() {
            menu.removeClass('dashboard-time-range-menu-open');
        });

        // Wheel zoom
        var chart_container = document.getElementById('dashboard-bar-chart');
        if (chart_container && !chart_container._zato_wheel_bound) {
            chart_container._zato_wheel_bound = true;
            chart_container.addEventListener('wheel', function(event) {
                event.preventDefault();
                var current = dash._zoom_bucket_count || 0;
                if (!current) {
                    var w = chart_container.offsetWidth || 800;
                    current = Math.min(60, Math.max(12, Math.floor(w / 16)));
                }
                if (event.deltaY < 0) {
                    current = Math.max(4, Math.round(current * 0.8));
                } else {
                    current = Math.min(120, Math.round(current * 1.25));
                }
                dash._zoom_bucket_count = current;
                dash._skip_legend_rebuild = true;
                dash.render_bar_chart(dash._last_timeline);
                dash._skip_legend_rebuild = false;
            }, {passive: false});
        }

        // Stat tile hover — delegated to kit
        dash._stat_tile_handle = kit.stat_tile.init({
            tiles: [
                {sparkline_selector: '#spark-total-jobs', buffer_key: 'total_jobs', label: 'Total jobs', color: dash.theme.spark_color},
                {sparkline_selector: '#spark-active', buffer_key: 'active', label: 'Active', color: dash.theme.spark_color},
                {sparkline_selector: '#spark-paused', buffer_key: 'paused', label: 'Paused', color: dash.theme.spark_color},
                {sparkline_selector: '#spark-runs', buffer_key: 'runs', label: 'Runs', color: dash.theme.spark_color},
                {sparkline_selector: '#spark-failures', buffer_key: 'failures', label: 'Failures', color: dash.theme.spark_err}
            ],
            get_buffer: function(key) {
                return dash._spark_buffers.data(key);
            }
        });

        // Tabs — delegated to kit
        dash._tabs_handle = kit.tabs.init({
            tab_selector: '.dashboard-tab',
            panel_prefix: 'dashboard-tab-panel-',
            storage_key: 'zato_scheduler_activity_tab',
            default_tab: 'failures'
        });

        dash.render(initial_data);
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
            var refresh_val = parseInt(params.get('refresh') || '0', 10);
            if (!isNaN(refresh_val)) {
                dash._auto_refresh.set_seconds(refresh_val);
            }
        });
    };

})();
