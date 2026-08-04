

/* Dashboard kit - the stacked timeline.
   Buckets a set of records by when they happened and stacks each bucket by whatever key
   the caller reads out of a record, e.g. its outcome. A key switched off in the hidden map
   is left out of the stack, which is what makes a legend a filter. */



(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.timeline = {};

    kit.timeline.config = {
        bucket_count: 60,
        height: 44,

        // How wide a bar is drawn against the slot it sits in, so neighbours stay apart
        bar_ratio: 0.82,

        // The window a set of records that all landed at the same instant is spread over
        empty_span_ms: 60000
    };

    /* Splits records into consecutive equal-width buckets between the earliest and the
       latest of them, each bucket counting how many records of each key it holds. */
    kit.timeline.bucket = function(records, config) {
        var bucket_count = config.bucket_count;
        var keys = config.keys;
        var timestamps = [];

        for (var record_index = 0; record_index < records.length; record_index++) {
            timestamps.push(config.ts_of(records[record_index]));
        }

        var min_time = Math.min.apply(null, timestamps);
        var max_time = Math.max.apply(null, timestamps);
        var time_span = max_time - min_time;

        // A set of records with no span of its own still needs a window to spread over.
        if (time_span <= 0) {
            time_span = kit.timeline.config.empty_span_ms;
            min_time = max_time - time_span;
        }

        var bucket_ms = time_span / bucket_count;
        var buckets = [];

        for (var bucket_index = 0; bucket_index < bucket_count; bucket_index++) {
            var bucket = {total: 0, start: min_time + bucket_index * bucket_ms};

            for (var key_index = 0; key_index < keys.length; key_index++) {
                bucket[keys[key_index]] = 0;
            }

            buckets.push(bucket);
        }

        for (var target_index = 0; target_index < records.length; target_index++) {
            var offset = timestamps[target_index] - min_time;
            var target = Math.floor(offset / bucket_ms);

            // The very latest record falls exactly on the far edge of the last bucket.
            if (target > bucket_count - 1) {
                target = bucket_count - 1;
            }

            var key = config.key_of(records[target_index]);

            buckets[target][key] += 1;
            buckets[target].total += 1;
        }

        return {buckets: buckets, min_time: min_time, max_time: max_time, bucket_ms: bucket_ms};
    };

    /* The tallest stack any one bucket reaches once the hidden keys are left out,
       which is what every bar is drawn in proportion to. */
    kit.timeline._max_stack = function(buckets, keys, hidden) {
        var max_stack = 1;

        for (var bucket_index = 0; bucket_index < buckets.length; bucket_index++) {
            var stack = 0;

            for (var key_index = 0; key_index < keys.length; key_index++) {
                var key = keys[key_index];

                if (!hidden[key]) {
                    stack += buckets[bucket_index][key];
                }
            }

            if (stack > max_stack) {
                max_stack = stack;
            }
        }

        return max_stack;
    };

    /* config:
         keys:         every series in the order it stacks, bottom-most first
         key_of:       which series one record belongs to
         ts_of:        when one record happened, in milliseconds
         colors:       the bar colour of each series
         hidden:       the series currently switched off
         bucket_count: how many slots the span is cut into
         height:       how tall the chart is drawn
         empty_html:   what stands in for the chart when there is nothing to draw */
    kit.timeline.render = function($host, records, config) {
        var defaults = kit.timeline.config;

        if (config.bucket_count === undefined) {
            config.bucket_count = defaults.bucket_count;
        }

        if (config.height === undefined) {
            config.height = defaults.height;
        }

        if (records.length === 0) {
            $host.html(config.empty_html);
            return;
        }

        var keys = config.keys;
        var hidden = config.hidden;
        var height = config.height;

        var series = kit.timeline.bucket(records, config);
        var buckets = series.buckets;
        var max_stack = kit.timeline._max_stack(buckets, keys, hidden);

        var bar_slot = 100 / config.bucket_count;
        var bar_width = bar_slot * defaults.bar_ratio;

        var html = '<svg class="dashboard-timeline-svg" viewBox="0 0 100 ' + height +
            '" preserveAspectRatio="none">';

        for (var bar_index = 0; bar_index < buckets.length; bar_index++) {
            var bucket = buckets[bar_index];
            var bar_x = bar_index * bar_slot;
            var bar_bottom = height;

            for (var draw_index = 0; draw_index < keys.length; draw_index++) {
                var key = keys[draw_index];

                if (hidden[key]) {
                    continue;
                }

                var count = bucket[key];

                if (count === 0) {
                    continue;
                }

                var bar_height = (count / max_stack) * height;
                bar_bottom = bar_bottom - bar_height;

                html += '<rect x="' + bar_x.toFixed(3) + '" y="' + bar_bottom.toFixed(3) +
                    '" width="' + bar_width.toFixed(3) + '" height="' + bar_height.toFixed(3) +
                    '" fill="' + config.colors[key] + '"></rect>';
            }
        }

        html += '</svg>';

        $host.html(html);
    };
})();
