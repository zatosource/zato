
/* Dashboard kit - stacked / overlaid main chart.
   A configurable time-bucketed chart with:
     - spline+gradient or grouped-bar rendering modes
     - per-series toggle legend (persisted to localStorage)
     - mouse-wheel zoom (reversed from the browser default: up to zoom in)
     - crosshair tooltip with full-per-series breakdown
     - a "chart type" toggle and a linked "N items" pill

   The caller supplies the palette/labels/series keys so the same code
   drives scheduler outcomes, EDA per-topic counts, and whatever else
   a future dashboard needs. */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var ns = $.fn.zato.dashboard_kit;
    ns.main_chart = {};

    var PADDING_LEFT = 40;
    var PADDING_BOTTOM = 28;
    var PADDING_TOP = 12;
    var PADDING_RIGHT = 8;
    var CHART_HEIGHT = 200;
    var GRID_LINE_COUNT = 4;
    var MIN_BUCKETS = 4;
    var MAX_BUCKETS = 120;
    var DEFAULT_MIN_AUTO_BUCKETS = 12;
    var DEFAULT_MAX_AUTO_BUCKETS = 60;
    var PX_PER_BUCKET = 16;

    var ICON_LINES = '<svg width="18" height="14" viewBox="0 0 18 14" fill="none" xmlns="http://www.w3.org/2000/svg">' +
        '<path d="M1 12C3 8 5.5 2 9 4C12.5 6 14 10 17 1" stroke="#012845" stroke-width="1.8" stroke-linecap="round"/>' +
        '</svg>';

    var ICON_BARS = '<svg width="18" height="14" viewBox="0 0 18 14" fill="none" xmlns="http://www.w3.org/2000/svg">' +
        '<rect x="1" y="6" width="3" height="8" rx="1" fill="#012845" fill-opacity="0.85"/>' +
        '<rect x="5.5" y="2" width="3" height="12" rx="1" fill="#012845" fill-opacity="0.85"/>' +
        '<rect x="10" y="8" width="3" height="6" rx="1" fill="#012845" fill-opacity="0.85"/>' +
        '<rect x="14.5" y="4" width="3" height="10" rx="1" fill="#012845" fill-opacity="0.85"/>' +
        '</svg>';

    var format_hhmmss = function(d) {
        return ('0' + d.getHours()).slice(-2) + ':' +
               ('0' + d.getMinutes()).slice(-2) + ':' +
               ('0' + d.getSeconds()).slice(-2);
    };

    /* Initialise a chart instance. Returns a handle with
       `render(timeline)` and `redraw()`. Config:
         container:           DOM id, e.g. '#dashboard-bar-chart'
         legend:               selector for the legend container
         count_pill:           selector for the "N runs / N messages" pill
         chart_type_toggle:    selector for the line/bar toggle button
         tooltip_id:           DOM id for the chart tooltip (created if absent)
         series_keys:          array of series keys in draw order
         palette:              { <key>: colour }
         labels:               { <key>: display label }
         item_noun_singular:   '1 run', '1 message'
         item_noun_plural:     '2 runs', '2 messages'
         range_names:          { <minutes>: label } - labels shown in the pill
         bucket_ts(record):    returns the record's timestamp in ms
         series_key(record):   returns the record's series key
         hidden_storage_key:   localStorage key for the hidden-series map
         bars_storage_key:     localStorage key for the bar/line mode flag
         zoom_bucket_state:    optional { get_buckets(), set_buckets(n) }
                               to share zoom with another component */
    ns.main_chart.init = function(config) {
        var state = {
            last_timeline: null,
            hidden_storage_key: config.hidden_storage_key,
            bars_storage_key: config.bars_storage_key,
            skip_legend_rebuild: false,
            zoom_bucket_count: 0,
            show_bars: false,
            time_range_minutes: 0
        };

        var get_hidden = function() {
            var stored = ns.storage_get_json(state.hidden_storage_key);
            return stored || {};
        };

        var set_hidden = function(hidden) {
            ns.storage_set_json(state.hidden_storage_key, hidden);
        };

        var update_chart_type_icon = function() {
            var $toggle = $(config.chart_type_toggle);
            if (!$toggle.length) return;
            if (state.show_bars) {
                $toggle.html(ICON_LINES);
                $toggle.attr('title', 'Switch to area chart');
            } else {
                $toggle.html(ICON_BARS);
                $toggle.attr('title', 'Switch to bar chart');
            }
        };

        var count_label = function(n) {
            if (n === 1) return '1 ' + config.item_noun_singular;
            return ns.format_number_compact(n) + ' ' + config.item_noun_plural;
        };

        var count_label_full = function(n) {
            if (n === 1) return '1 ' + config.item_noun_singular;
            return ns.format_number_full(n) + ' ' + config.item_noun_plural;
        };

        var render = function(timeline) {
            state.last_timeline = timeline;
            var $container = $(config.container);
            var $count = $(config.count_pill);
            var $legend = $(config.legend);
            var filtered = timeline || [];

            if (!filtered || filtered.length === 0) {
                $container.html('<div class="dashboard-no-data">No data yet</div>');
                $legend.empty();
                $count.text('');
                return;
            }

            var range_minutes = state.time_range_minutes;
            var range_names = config.range_names || {};
            var name_prefix = range_minutes > 0 && range_names[range_minutes]
                ? range_names[range_minutes]
                : 'All';
            $count.text(name_prefix + ' \u00b7 ' + count_label(filtered.length));
            $count.attr('title', name_prefix + ' \u00b7 ' + count_label_full(filtered.length));

            var chart_width = $container.width() || 800;
            var series_keys = config.series_keys;
            var palette = config.palette || {};
            var labels = config.labels || {};
            var hidden = get_hidden();

            var timestamps = [];
            for (var ri = 0; ri < filtered.length; ri++) {
                var t = config.bucket_ts(filtered[ri]);
                if (t !== null && t !== undefined && !isNaN(t)) {
                    timestamps.push(t);
                }
            }

            if (timestamps.length === 0) {
                $container.html('<div class="dashboard-no-data">No data yet</div>');
                $legend.empty();
                $count.text('');
                return;
            }

            var min_time = Math.min.apply(null, timestamps);
            var max_time = Date.now();
            var time_range = max_time - min_time;
            if (time_range === 0) {
                time_range = 3600000;
                min_time = max_time - time_range;
            }

            var auto_bucket_count = Math.min(
                DEFAULT_MAX_AUTO_BUCKETS,
                Math.max(DEFAULT_MIN_AUTO_BUCKETS, Math.floor(chart_width / PX_PER_BUCKET))
            );
            var bucket_count = state.zoom_bucket_count > 0
                ? Math.min(MAX_BUCKETS, Math.max(MIN_BUCKETS, state.zoom_bucket_count))
                : auto_bucket_count;
            var bucket_size = time_range / bucket_count;
            var buckets = [];
            for (var bi = 0; bi < bucket_count; bi++) {
                var bucket = {};
                for (var ki = 0; ki < series_keys.length; ki++) {
                    bucket[series_keys[ki]] = 0;
                }
                bucket.start = min_time + bi * bucket_size;
                bucket.end = min_time + (bi + 1) * bucket_size;
                buckets.push(bucket);
            }

            for (var idx = 0; idx < filtered.length; idx++) {
                var record = filtered[idx];
                var ts = config.bucket_ts(record);
                var skey = config.series_key(record);
                var target_bucket = Math.floor((ts - min_time) / bucket_size);
                if (target_bucket >= bucket_count) target_bucket = bucket_count - 1;
                if (target_bucket < 0) target_bucket = 0;
                if (buckets[target_bucket][skey] !== undefined) {
                    buckets[target_bucket][skey]++;
                }
            }

            var visible_keys = [];
            for (var vk = 0; vk < series_keys.length; vk++) {
                if (hidden[series_keys[vk]]) continue;
                var has_data = false;
                for (var hd = 0; hd < buckets.length; hd++) {
                    if (buckets[hd][series_keys[vk]] > 0) { has_data = true; break; }
                }
                if (has_data) visible_keys.push(series_keys[vk]);
            }

            var max_stack = 0;
            if (state.show_bars) {
                for (var ms_index = 0; ms_index < buckets.length; ms_index++) {
                    var ms_sum = 0;
                    for (var ms_key = 0; ms_key < visible_keys.length; ms_key++) {
                        ms_sum += (buckets[ms_index][visible_keys[ms_key]] || 0);
                    }
                    if (ms_sum > max_stack) max_stack = ms_sum;
                }
            } else {
                for (var ox = 0; ox < buckets.length; ox++) {
                    for (var oy = 0; oy < visible_keys.length; oy++) {
                        var v = buckets[ox][visible_keys[oy]];
                        if (v > max_stack) max_stack = v;
                    }
                }
            }
            if (max_stack === 0) max_stack = 1;

            var draw_width = chart_width - PADDING_LEFT - PADDING_RIGHT;
            var draw_height = CHART_HEIGHT - PADDING_TOP - PADDING_BOTTOM;
            var baseline_y = PADDING_TOP + draw_height;

            var svg = '<svg width="' + chart_width + '" height="' + CHART_HEIGHT + '" xmlns="http://www.w3.org/2000/svg">';
            svg += '<defs>';
            for (var gd = 0; gd < visible_keys.length; gd++) {
                var gd_key = visible_keys[gd];
                svg += '<linearGradient id="areaGrad_' + sanitize(gd_key) + '" x1="0" y1="0" x2="0" y2="1">';
                svg += '<stop offset="0" stop-color="' + (palette[gd_key] || '#888') + '" stop-opacity="0.10"/>';
                svg += '<stop offset="0.5" stop-color="' + (palette[gd_key] || '#888') + '" stop-opacity="0.03"/>';
                svg += '<stop offset="1" stop-color="' + (palette[gd_key] || '#888') + '" stop-opacity="0.0"/>';
                svg += '</linearGradient>';
            }
            svg += '</defs>';

            for (var gi = 0; gi <= GRID_LINE_COUNT; gi++) {
                var grid_y = PADDING_TOP + draw_height - (gi / GRID_LINE_COUNT) * draw_height;
                var grid_value = Math.round((gi / GRID_LINE_COUNT) * max_stack);
                svg += '<line x1="' + PADDING_LEFT + '" y1="' + grid_y.toFixed(1) + '" ';
                svg += 'x2="' + (chart_width - PADDING_RIGHT) + '" y2="' + grid_y.toFixed(1) + '" ';
                svg += 'stroke="rgba(0,0,0,0.05)" stroke-width="1" />';
                svg += '<text x="' + (PADDING_LEFT - 6) + '" y="' + (grid_y + 3).toFixed(1) + '" ';
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
                for (var lbi = 0; lbi < bucket_count; lbi++) {
                    var val = buckets[lbi][layer_key];
                    var bar_h = val > 0 ? Math.max(2, (val / max_stack) * draw_height) : 0;
                    var bar_x = PADDING_LEFT + lbi * bucket_slot_width + group_padding + layer * (bar_width + bar_gap);
                    var bar_y = baseline_y - bar_h;
                    layer_points[layer_key].push({
                        x: bar_x + bar_width / 2,
                        y: val > 0 ? bar_y : baseline_y,
                        val: val
                    });
                }
            }

            if (state.show_bars) {
                var sb_inset = Math.max(1, bucket_slot_width * 0.1);
                var sb_w = bucket_slot_width - sb_inset * 2;
                var sb_sep = 1.5;
                for (var sk = 0; sk < visible_keys.length; sk++) {
                    layer_points[visible_keys[sk]] = [];
                }
                for (var sbi = 0; sbi < bucket_count; sbi++) {
                    var sb_x = PADDING_LEFT + sbi * bucket_slot_width + sb_inset;
                    var sb_cursor_y = baseline_y;
                    for (var sk2 = 0; sk2 < visible_keys.length; sk2++) {
                        var sk_key = visible_keys[sk2];
                        var sk_val = buckets[sbi][sk_key] || 0;
                        var sk_h = sk_val > 0 ? Math.max(2, (sk_val / max_stack) * draw_height) : 0;
                        if (sk_val > 0) {
                            var seg_y = sb_cursor_y - sk_h;
                            svg += '<rect x="' + sb_x.toFixed(1) + '" y="' + seg_y.toFixed(1) + '" ';
                            svg += 'width="' + sb_w.toFixed(1) + '" height="' + sk_h.toFixed(1) + '" ';
                            svg += 'fill="' + (palette[sk_key] || '#888') + '" />';
                            sb_cursor_y = seg_y - sb_sep;
                        }
                        layer_points[sk_key].push({
                            x: sb_x + sb_w / 2,
                            y: sk_val > 0 ? sb_cursor_y + sb_sep : baseline_y,
                            val: sk_val
                        });
                    }
                }
            } else {
                var edge_left = PADDING_LEFT;
                var edge_right = PADDING_LEFT + draw_width;
                for (var sl = 0; sl < visible_keys.length; sl++) {
                    var skey2 = visible_keys[sl];
                    var data_pts = [];
                    for (var di = 0; di < bucket_count; di++) {
                        var dx = PADDING_LEFT + (di + 0.5) * bucket_slot_width;
                        var dv = buckets[di][skey2];
                        var dy = dv > 0 ? baseline_y - Math.max(2, (dv / max_stack) * draw_height) : baseline_y;
                        data_pts.push({x: dx, y: dy, bucket_index: di});
                    }

                    var spline_pts = [];
                    spline_pts.push({x: edge_left, y: data_pts[0].y});
                    for (var dp = 0; dp < data_pts.length; dp++) spline_pts.push(data_pts[dp]);
                    spline_pts.push({x: edge_right, y: data_pts[data_pts.length - 1].y});

                    layer_points[skey2] = [];
                    for (var hpi = 0; hpi < bucket_count; hpi++) {
                        var hval = buckets[hpi][skey2];
                        var hy = hval > 0 ? baseline_y - (hval / max_stack) * draw_height : baseline_y;
                        layer_points[skey2].push({x: data_pts[hpi].x, y: hy, val: hval});
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

                    svg += '<path d="' + area_fill + '" fill="url(#areaGrad_' + sanitize(skey2) + ')" />';
                    svg += '<path d="' + area_path + '" fill="none" stroke="' + (palette[skey2] || '#888') + '" stroke-width="1.5" stroke-opacity="0.6" stroke-linecap="round" stroke-linejoin="round" />';

                    var tip_cx = edge_right;
                    var tip_cy = data_pts[data_pts.length - 1].y;
                    var tip_color = palette[skey2] || '#888';
                    svg += '<circle cx="' + tip_cx.toFixed(2) + '" cy="' + tip_cy.toFixed(2) + '" r="5.5" ';
                    svg += 'fill="none" stroke="' + tip_color + '" stroke-opacity="0.35" stroke-width="1"/>';
                    svg += '<circle cx="' + tip_cx.toFixed(2) + '" cy="' + tip_cy.toFixed(2) + '" r="3.5" ';
                    svg += 'fill="' + tip_color + '"/>';
                }
            }

            var show_seconds = bucket_size < 120000;
            var label_count = Math.min(6, bucket_count);
            var label_step = Math.max(1, Math.floor(bucket_count / label_count));
            for (var li = 0; li < bucket_count; li += label_step) {
                var lx = PADDING_LEFT + (li + 0.5) * bucket_slot_width;
                var label_date = new Date(buckets[li].start);
                var label_text = ('0' + label_date.getHours()).slice(-2) + ':' + ('0' + label_date.getMinutes()).slice(-2);
                if (show_seconds) {
                    label_text += ':' + ('0' + label_date.getSeconds()).slice(-2);
                }
                svg += '<text x="' + lx.toFixed(1) + '" y="' + (CHART_HEIGHT - 6) + '" text-anchor="middle" ';
                svg += 'font-size="10" fill="rgba(0,0,0,0.35)" font-family="Menlo, Consolas, Monaco, monospace">' + label_text + '</text>';
            }

            svg += '</svg>';
            $container.html(svg);

            setup_interactions($container, buckets, draw_width, bucket_count, draw_height, visible_keys, layer_points);

            ns.build_legend({
                container: config.legend,
                series_keys: series_keys,
                palette: palette,
                labels: labels,
                text_colors: config.legend_text_colors,
                bg_colors: config.legend_bg_colors,
                hidden: hidden,
                on_toggle: function(_key, h) {
                    set_hidden(h);
                    redraw();
                }
            }, state.skip_legend_rebuild);
        };

        var redraw = function() {
            if (state.last_timeline) {
                state.skip_legend_rebuild = true;
                render(state.last_timeline);
                state.skip_legend_rebuild = false;
            }
        };

        var setup_interactions = function($container, buckets, draw_width, bucket_count, draw_height, visible_keys, layer_points) {
            var $svg = $container.find('svg');
            var overlay = $container.find('.dashboard-chart-overlay');
            if (overlay.length === 0) {
                $container.css('position', 'relative');
                $container.append('<div class="dashboard-chart-overlay"></div>');
                overlay = $container.find('.dashboard-chart-overlay');
            }
            overlay.css({position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', 'pointer-events': 'none'});

            var tooltip_id = config.tooltip_id || 'dashboard-chart-tooltip';
            var $tooltip = $('#' + tooltip_id);
            if ($tooltip.length === 0) {
                $('body').append('<div id="' + tooltip_id + '" class="dashboard-chart-tooltip"></div>');
                $tooltip = $('#' + tooltip_id);
            }

            var bucket_width_px = draw_width / bucket_count;
            var palette = config.palette || {};
            var labels = config.labels || {};

            $svg.off('mousemove.chart mouseleave.chart');

            $svg.on('mousemove.chart', function(event) {
                var rect = this.getBoundingClientRect();
                var mouse_x = event.clientX - rect.left;
                var relative_x = mouse_x - PADDING_LEFT;

                if (relative_x < 0 || relative_x > draw_width) {
                    overlay.empty();
                    $tooltip.css('display', 'none');
                    return;
                }

                var bucket_index = Math.floor((relative_x / draw_width) * bucket_count);
                if (bucket_index >= bucket_count) bucket_index = bucket_count - 1;
                if (bucket_index < 0) bucket_index = 0;

                var band_left = PADDING_LEFT + bucket_index * bucket_width_px;
                var band_html = '<svg style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none" xmlns="http://www.w3.org/2000/svg">';
                band_html += '<rect x="' + band_left.toFixed(1) + '" y="' + PADDING_TOP + '" width="' + bucket_width_px.toFixed(1) + '" height="' + draw_height + '" fill="rgba(0,0,0,0.06)" rx="2" />';

                for (var dk = 0; dk < visible_keys.length; dk++) {
                    var dk_key = visible_keys[dk];
                    var pts = layer_points[dk_key];
                    if (pts && pts[bucket_index] && pts[bucket_index].val > 0) {
                        var pt = pts[bucket_index];
                        var dot_color_main = palette[dk_key] || '#888';
                        band_html += '<circle cx="' + pt.x.toFixed(1) + '" cy="' + pt.y.toFixed(1) + '" r="5.5" fill="none" stroke="' + dot_color_main + '" stroke-opacity="0.35" stroke-width="1" />';
                        band_html += '<circle cx="' + pt.x.toFixed(1) + '" cy="' + pt.y.toFixed(1) + '" r="3.5" fill="' + dot_color_main + '" />';
                    }
                }
                band_html += '</svg>';
                overlay.html(band_html);

                var bucket = buckets[bucket_index];
                var time_start = new Date(bucket.start);
                var time_end = new Date(bucket.end);
                var bucket_span_s = Math.round((bucket.end - bucket.start) / 1000);
                var time_label = bucket_span_s >= 1
                    ? format_hhmmss(time_start) + ' \u2192 ' + format_hhmmss(time_end)
                    : format_hhmmss(time_start);

                var total = 0;
                for (var tk = 0; tk < visible_keys.length; tk++) {
                    total += (bucket[visible_keys[tk]] || 0);
                }
                var items_label = total === 1
                    ? '1 ' + config.item_noun_singular
                    : ns.format_number_full(total) + ' ' + config.item_noun_plural;

                var tooltip_html = '<div class="dashboard-tooltip-header">' +
                    '<div class="dashboard-tooltip-title">' + time_label + '</div>' +
                    '<div class="dashboard-tooltip-subtitle">' + items_label + '</div>' +
                    '</div>';

                var body_lines = [];
                for (var ki = 0; ki < visible_keys.length; ki++) {
                    var k = visible_keys[ki];
                    var count = bucket[k] || 0;
                    body_lines.push('<span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:' + (palette[k] || '#888') + ';margin-right:5px;vertical-align:middle"></span>' +
                        (labels[k] || k) + ': <b>' + ns.format_number_full(count) + '</b>');
                }
                tooltip_html += body_lines.join('<br>');

                $tooltip.html(tooltip_html);
                $tooltip.css({display: 'block', left: '0px', top: '0px'});
                var tt_w = $tooltip.outerWidth();
                var tt_h = $tooltip.outerHeight();
                var margin = 8;
                var viewport_w = $(window).width();
                var viewport_h = $(window).height();
                var left = event.clientX + 14;
                var top = event.clientY - 14;
                if (left + tt_w + margin > viewport_w) { left = event.clientX - tt_w - 14; }
                if (left < margin) { left = margin; }
                if (top + tt_h + margin > viewport_h) { top = viewport_h - tt_h - margin; }
                if (top < margin) { top = margin; }
                $tooltip.css({left: left + 'px', top: top + 'px'});
            });

            $svg.on('mouseleave.chart', function() {
                overlay.empty();
                $tooltip.css('display', 'none');
            });
        };

        var sanitize = function(key) {
            return String(key).replace(/[^A-Za-z0-9_]/g, '_');
        };

        /* Load persisted UI state on init. */
        if (state.bars_storage_key && ns.storage_get(state.bars_storage_key) === 'true') {
            state.show_bars = true;
        }
        update_chart_type_icon();

        if (config.chart_type_toggle) {
            $(config.chart_type_toggle).on('click', function() {
                state.show_bars = !state.show_bars;
                if (state.bars_storage_key) {
                    ns.storage_set(state.bars_storage_key, String(state.show_bars));
                }
                update_chart_type_icon();
                redraw();
            });
        }

        var chart_dom = document.querySelector(config.container);
        if (chart_dom && !chart_dom._zato_wheel_bound) {
            chart_dom._zato_wheel_bound = true;
            chart_dom.addEventListener('wheel', function(event) {
                event.preventDefault();
                var current = state.zoom_bucket_count || 0;
                if (!current) {
                    var w = chart_dom.offsetWidth || 800;
                    current = Math.min(DEFAULT_MAX_AUTO_BUCKETS,
                        Math.max(DEFAULT_MIN_AUTO_BUCKETS, Math.floor(w / PX_PER_BUCKET)));
                }
                if (event.deltaY < 0) {
                    current = Math.max(MIN_BUCKETS, Math.round(current * 0.8));
                } else {
                    current = Math.min(MAX_BUCKETS, Math.round(current * 1.25));
                }
                state.zoom_bucket_count = current;
                state.skip_legend_rebuild = true;
                render(state.last_timeline);
                state.skip_legend_rebuild = false;
            }, {passive: false});
        }

        return {
            render: function(timeline) { render(timeline); },
            redraw: redraw,
            set_time_range_minutes: function(minutes) {
                state.time_range_minutes = minutes;
            },
            get_time_range_minutes: function() {
                return state.time_range_minutes;
            }
        };
    };
})();
