

/* Dashboard kit - the activity strip.
   A stacked area sparkline of events over time - each series an outcome in its own
   colour, stacked, smoothed and shaded, with a hover breakdown per time bucket.
   It grew out of the scheduler's run history and serves any screen that has events
   with a time and a kind - the caller either hands over raw records with callbacks
   naming each one's time and series, or buckets already counted elsewhere.

   The legend is the caller's business - screens differ in what toggling a series
   means, so the strip only draws and reports clicks. */



(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.activity_strip = {};

    kit.activity_strip.config = {

        /* The strip's geometry - one reading-line tall, breathing room above for
           the end dots and below for the baseline stroke */
        height: 36,
        pad_top: 7,
        pad_bot: 2,

        /* How many buckets the window is cut into - one per this many pixels,
           never fewer or more than these */
        px_per_bucket: 14,
        min_buckets: 16,
        max_buckets: 80,

        /* A bucket with anything in it at all shows at least this thick, so one
           event among thousands is still a visible blip */
        min_thickness: 6,

        /* Records covering less than this stretch over it anyway, so two events
           a second apart do not draw as a whole screen of noise */
        default_min_span_ms: 3600000
    };

    /* Gradient ids carry the series key, which may hold characters an id may not */
    kit.activity_strip._sanitize = function(key) {
        return String(key).replace(/[^A-Za-z0-9_]/g, '_');
    };

    /* The smoothing - a cubic through the bucket centres, each control point
       halfway to its neighbour, so the line bends and never overshoots */
    kit.activity_strip._bezier = function(points) {
        if (points.length < 2) {
            return '';
        }

        var d = 'M' + points[0].x.toFixed(1) + ',' + points[0].y.toFixed(1);

        for (var point_index = 1; point_index < points.length; point_index++) {
            var previous = points[point_index - 1];
            var current = points[point_index];
            var control_x = (previous.x + current.x) / 2;

            d += ' C' + control_x.toFixed(1) + ',' + previous.y.toFixed(1) +
                ' ' + control_x.toFixed(1) + ',' + current.y.toFixed(1) +
                ' ' + current.x.toFixed(1) + ',' + current.y.toFixed(1);
        }

        return d;
    };

    /* Raw records cut into buckets - the window is what the records cover,
       stretched to min_span_ms so a burst does not fill the whole strip.
       A record of a series the strip was not told about counts into the first
       series, so nothing an endpoint says is ever dropped on the floor. */
    kit.activity_strip._bucket_records = function(strip) {
        var config = kit.activity_strip.config;

        var timestamps = [];

        for (var record_index = 0; record_index < strip.records.length; record_index++) {
            timestamps.push(strip.record_time(strip.records[record_index]));
        }

        var min_time = Math.min.apply(null, timestamps);
        var max_time = Math.max.apply(null, timestamps);

        var min_span = strip.min_span_ms;

        if (min_span === undefined) {
            min_span = config.default_min_span_ms;
        }

        var time_span = max_time - min_time;

        if (time_span < min_span) {
            min_time = max_time - min_span;
            time_span = min_span;
        }

        var bucket_ms = time_span / strip.bucket_count;
        var buckets = [];

        for (var bucket_index = 0; bucket_index < strip.bucket_count; bucket_index++) {
            var bucket = {
                total: 0,
                start: min_time + bucket_index * bucket_ms,
                end: min_time + (bucket_index + 1) * bucket_ms
            };

            for (var key_index = 0; key_index < strip.series_keys.length; key_index++) {
                bucket[strip.series_keys[key_index]] = 0;
            }

            buckets.push(bucket);
        }

        for (var assign_index = 0; assign_index < strip.records.length; assign_index++) {
            var record = strip.records[assign_index];
            var record_ms = strip.record_time(record);

            var target = Math.floor((record_ms - min_time) / bucket_ms);
            target = Math.min(strip.bucket_count - 1, Math.max(0, target));

            var series = strip.record_series(record);

            if (buckets[target].hasOwnProperty(series)) {
                buckets[target][series]++;
            }
            else {
                buckets[target][strip.series_keys[0]]++;
            }

            buckets[target].total++;
        }

        return buckets;
    };

    /* config:
         host:            selector of the element the strip renders into
         series_keys:     the series in stacking order, first at the bottom
         colors:          series key to its colour
         labels:          series key to the word its tooltip rows read
         hidden:          series key to whether it is drawn - hidden series still
                          hold their place in the stack, they are just not shown
         empty_text:      what stands in the strip's place with nothing to draw
         records:         the raw records, with record_time and record_series
                          saying when each one happened and which series it is,
                          and min_span_ms the least window they stretch over
         buckets:         counted elsewhere instead of records - each one holds
                          start and end in ms and a count per series key
         on_bucket_click: called with (start_iso, end_iso) of a clicked bucket */
    kit.activity_strip.render = function(strip) {
        var config = kit.activity_strip.config;
        var container = $(strip.host);

        var chart_width = container.width();
        var draw_height = config.height - config.pad_top - config.pad_bot;

        strip.bucket_count = Math.min(config.max_buckets,
            Math.max(config.min_buckets, Math.floor(chart_width / config.px_per_bucket)));

        var buckets;

        if (strip.records !== undefined) {
            if (strip.records.length === 0) {
                container.html('<div class="dashboard-inline-empty">' + strip.empty_text + '</div>');
                return;
            }

            buckets = kit.activity_strip._bucket_records(strip);
        }
        else {
            buckets = strip.buckets;
        }

        var bucket_count = buckets.length;

        /* The strip scales to its fullest bucket - all series counted, the hidden
           ones included, so toggling one does not rescale everything else */
        var max_stack = 0;
        var grand_total = 0;

        for (var stack_index = 0; stack_index < bucket_count; stack_index++) {
            var stack_sum = 0;

            for (var sum_index = 0; sum_index < strip.series_keys.length; sum_index++) {
                stack_sum += buckets[stack_index][strip.series_keys[sum_index]];
            }

            buckets[stack_index].total = stack_sum;
            grand_total += stack_sum;

            if (stack_sum > max_stack) {
                max_stack = stack_sum;
            }
        }

        if (grand_total === 0) {
            container.html('<div class="dashboard-inline-empty">' + strip.empty_text + '</div>');
            return;
        }

        if (max_stack === 0) {
            max_stack = 1;
        }

        var seg_width = chart_width / bucket_count;
        var baseline = config.height - config.pad_bot;

        /* Every series' outline, stacked - each one starts where the one under
           it ended, and anything non-zero shows at least min_thickness tall */
        var series_top = {};
        var cumulative = [];

        for (var zero_index = 0; zero_index < bucket_count; zero_index++) {
            cumulative.push(0);
        }

        for (var series_index = 0; series_index < strip.series_keys.length; series_index++) {
            var series_key = strip.series_keys[series_index];
            var tops = [];

            for (var col_index = 0; col_index < bucket_count; col_index++) {
                var x = col_index * seg_width + seg_width / 2;
                var value = buckets[col_index][series_key];

                var bottom_y = baseline - (cumulative[col_index] / max_stack) * draw_height;
                var top_y = baseline - ((cumulative[col_index] + value) / max_stack) * draw_height;

                if (value > 0 && (bottom_y - top_y) < config.min_thickness) {
                    top_y = bottom_y - config.min_thickness;
                }

                tops.push({x: x, y: top_y});
                cumulative[col_index] += value;
            }

            series_top[series_key] = tops;
        }

        var visible_keys = [];

        for (var visible_index = 0; visible_index < strip.series_keys.length; visible_index++) {
            if (!strip.hidden[strip.series_keys[visible_index]]) {
                visible_keys.push(strip.series_keys[visible_index]);
            }
        }

        var svg = '<svg width="' + chart_width + '" height="' + config.height +
            '" style="overflow:visible" xmlns="http://www.w3.org/2000/svg">';

        svg += '<defs>';

        for (var grad_index = 0; grad_index < visible_keys.length; grad_index++) {
            var grad_color = strip.colors[visible_keys[grad_index]];

            svg += '<linearGradient id="stripGrad_' + kit.activity_strip._sanitize(visible_keys[grad_index]) +
                '" x1="0" y1="0" x2="0" y2="1">' +
                '<stop offset="0" stop-color="' + grad_color + '" stop-opacity="0.25"/>' +
                '<stop offset="1" stop-color="' + grad_color + '" stop-opacity="0.03"/>' +
                '</linearGradient>';
        }

        svg += '</defs>';

        for (var draw_index = 0; draw_index < visible_keys.length; draw_index++) {
            var draw_key = visible_keys[draw_index];
            var color = strip.colors[draw_key];
            var top_points = series_top[draw_key];

            var has_any = false;

            for (var check_index = 0; check_index < bucket_count; check_index++) {
                if (buckets[check_index][draw_key] > 0) {
                    has_any = true;
                    break;
                }
            }

            if (!has_any) {
                continue;
            }

            /* An empty bucket pulls the line down to the baseline, so quiet time
               reads as quiet rather than as a plateau between two spikes */
            var stroke_points = [];

            for (var stroke_index = 0; stroke_index < bucket_count; stroke_index++) {
                if (buckets[stroke_index][draw_key] > 0) {
                    stroke_points.push(top_points[stroke_index]);
                }
                else {
                    stroke_points.push({x: top_points[stroke_index].x, y: baseline});
                }
            }

            var spline_d = kit.activity_strip._bezier(stroke_points);
            var area_d = spline_d +
                ' L' + stroke_points[stroke_points.length - 1].x.toFixed(1) + ',' + baseline.toFixed(1) +
                ' L' + stroke_points[0].x.toFixed(1) + ',' + baseline.toFixed(1) + ' Z';

            svg += '<path d="' + area_d + '" fill="url(#stripGrad_' +
                kit.activity_strip._sanitize(draw_key) + ')" />';
            svg += '<path d="' + spline_d + '" fill="none" stroke="' + color +
                '" stroke-width="1.5" stroke-opacity="0.7" stroke-linecap="round" stroke-linejoin="round" />';

            var last_point = stroke_points[stroke_points.length - 1];

            svg += '<circle cx="' + last_point.x.toFixed(2) + '" cy="' + last_point.y.toFixed(2) +
                '" r="5.5" fill="none" stroke="' + color + '" stroke-opacity="0.35" stroke-width="1"/>';
            svg += '<circle cx="' + last_point.x.toFixed(2) + '" cy="' + last_point.y.toFixed(2) +
                '" r="3.5" fill="' + color + '"/>';
        }

        for (var hit_index = 0; hit_index < bucket_count; hit_index++) {
            svg += '<rect class="dashboard-chart-hitrect" x="' + (hit_index * seg_width).toFixed(1) +
                '" y="0" width="' + seg_width.toFixed(1) + '" height="' + config.height +
                '" fill="transparent" data-bucket="' + hit_index + '" />';
        }

        svg += '</svg>';

        container.html(svg);
        container.toggleClass('dashboard-activity-strip-clickable', strip.on_bucket_click !== undefined);

        container.off('mousemove.activity_strip mouseleave.activity_strip click.activity_strip');

        container.on('mousemove.activity_strip', function(event) {
            var target = $(event.target);

            if (!target.attr('data-bucket')) {
                kit.tooltip.hide();
                return;
            }

            var bucket = buckets[parseInt(target.attr('data-bucket'), 10)];

            if (bucket.total === 0) {
                kit.tooltip.hide();
                return;
            }

            var from_label = kit.format_local_time(new Date(bucket.start).toISOString());
            var to_label = kit.format_local_time(new Date(bucket.end).toISOString());

            var html = '<div class="dashboard-tooltip-header">' +
                '<div class="dashboard-tooltip-title">' + from_label + '</div>' +
                '<div class="dashboard-tooltip-subtitle">to ' + to_label + '</div>' +
                '</div>';

            html += '<div class="dashboard-tooltip-body">';

            for (var row_index = 0; row_index < strip.series_keys.length; row_index++) {
                var row_key = strip.series_keys[row_index];

                if (strip.hidden[row_key]) {
                    continue;
                }

                var row_value = bucket[row_key];

                if (row_value === 0) {
                    continue;
                }

                var percent = Math.round((row_value / bucket.total) * 100);

                html += '<div class="dashboard-tooltip-row">' +
                    '<span class="dashboard-tooltip-dot" style="background:' + strip.colors[row_key] + '"></span>' +
                    strip.labels[row_key] + ': ' + kit.format_number_full(row_value) +
                    ' <span class="dashboard-tooltip-muted">(' + percent + '%)</span>' +
                    '</div>';
            }

            html += '<div class="dashboard-tooltip-total">Total: ' + kit.format_number_full(bucket.total) + '</div>';
            html += '</div>';

            kit.tooltip.show(event, html);
        });

        container.on('mouseleave.activity_strip', function() {
            kit.tooltip.hide();
        });

        if (strip.on_bucket_click !== undefined) {
            container.on('click.activity_strip', function(event) {
                var target = $(event.target);

                if (!target.attr('data-bucket')) {
                    return;
                }

                var bucket = buckets[parseInt(target.attr('data-bucket'), 10)];

                strip.on_bucket_click(new Date(bucket.start).toISOString(), new Date(bucket.end).toISOString());
            });
        }
    };
})();
