
/* Dashboard kit - root namespace and shared helpers.
   Provides formatters, time helpers and a small utility registry used
   by every component. Nothing in here knows about the scheduler, EDA,
   or any other concrete dashboard. */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var kit = $.fn.zato.dashboard_kit;

    /* Compact number: 1234 -> "1.2K", 28937423 -> "29M". Single decimal
       when the integer part is a single digit so numbers stay short. */
    kit.format_number_compact = function(n) {
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

    /* Full thousands-separated form: 28937423 -> "28,937,423". Used as
       the authoritative display of a number in title= hover tooltips. */
    kit.format_number_full = function(n) {
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

    kit.set_number = function($el, n) {
        var compact = kit.format_number_compact(n);
        var full = kit.format_number_full(n);
        $el.text(compact);
        if (compact === full) {
            $el.removeAttr('title');
        } else {
            $el.attr('title', full);
        }
    };

    kit.format_compact_duration = function(seconds) {
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

    kit.format_ago = function(seconds) {
        if (seconds <= 0) return 'Now';
        return kit.format_compact_duration(seconds) + ' ago';
    };

    kit.format_duration_ms = function(duration_ms) {
        if (duration_ms === null || duration_ms === undefined || duration_ms === '') {
            return '-';
        }
        var ms = parseInt(duration_ms, 10);
        if (isNaN(ms)) {
            return '-';
        }
        if (ms === 0) {
            return '< 1 ms';
        }
        if (ms < 1000) {
            return ms + ' ms';
        }
        if (ms < 60000) {
            return (ms / 1000).toFixed(1) + ' s';
        }
        return (ms / 60000).toFixed(1) + ' min';
    };

    kit.relative_time_future = function(iso_string) {
        if (!iso_string) return '-';
        var target = new Date(iso_string).getTime();
        var now = Date.now();
        var diff_seconds = Math.floor((target - now) / 1000);

        if (diff_seconds <= 0) return 'Now';

        var days = Math.floor(diff_seconds / 86400);
        var hours = Math.floor((diff_seconds % 86400) / 3600);
        var minutes = Math.floor((diff_seconds % 3600) / 60);
        var seconds = diff_seconds % 60;

        if (days > 0) return 'In ' + days + 'd ' + hours + 'h';
        if (hours > 0) return 'In ' + hours + 'h ' + minutes + 'm';
        if (minutes > 0) return 'In ' + minutes + 'm ' + seconds + 's';
        return 'In ' + seconds + 's';
    };

    kit.relative_time_past = function(iso_string) {
        if (!iso_string) return '-';
        var target = new Date(iso_string).getTime();
        var now = Date.now();
        var diff_seconds = Math.floor((now - target) / 1000);

        if (diff_seconds < 0) diff_seconds = 0;
        if (diff_seconds < 60) return diff_seconds + 's ago';
        if (diff_seconds < 3600) return Math.floor(diff_seconds / 60) + 'm ago';
        if (diff_seconds < 86400) return Math.floor(diff_seconds / 3600) + 'h ago';
        return Math.floor(diff_seconds / 86400) + 'd ago';
    };

    kit.format_local_time = function(iso_string) {
        if (!iso_string) return '';
        var date = new Date(iso_string);
        var year = date.getFullYear();
        var month = ('0' + (date.getMonth() + 1)).slice(-2);
        var day = ('0' + date.getDate()).slice(-2);
        var hours = ('0' + date.getHours()).slice(-2);
        var minutes = ('0' + date.getMinutes()).slice(-2);
        var seconds = ('0' + date.getSeconds()).slice(-2);
        return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
    };

    /* Bucket `timeline` into `bucket_count` consecutive equal-width time
       slots ending at `now`, counting only records for which
       `predicate(record)` returns true. `ts_accessor(record)` must
       return the record's timestamp in milliseconds; a common accessor
       is `function(r){return new Date(r.actual_fire_time_iso).getTime();}`.
       Returns {series: [{ts, value} * bucket_count], total: N}. */
    kit.bucket_events_per_minute = function(timeline, predicate, ts_accessor, window_ms, bucket_count) {
        window_ms = window_ms || (60 * 60 * 1000);
        bucket_count = bucket_count || 60;
        var now = Date.now();
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
                var t_ms = ts_accessor(record);
                if (t_ms === null || t_ms === undefined || isNaN(t_ms)) continue;
                if (t_ms < window_start || t_ms > now) continue;
                var idx = Math.floor((t_ms - window_start) / bucket_size);
                if (idx < 0) idx = 0;
                if (idx >= bucket_count) idx = bucket_count - 1;
                series[idx].value++;
                total++;
            }
        }

        // .. drop the last (partial) bucket so the sparkline dot
        // .. sits on the last complete time slice
        if (series.length > 2) {
            series.pop();
        }

        return {series: series, total: total};
    };

    /* Tiny localStorage wrapper that silently tolerates SecurityError
       (incognito with disabled storage, blocked by extensions, etc.). */
    kit.storage_get = function(key) {
        try { return localStorage.getItem(key); } catch(e) { return null; }
    };

    kit.storage_set = function(key, value) {
        try { localStorage.setItem(key, value); } catch(e) {}
    };

    kit.storage_get_json = function(key) {
        try {
            var raw = localStorage.getItem(key);
            return raw ? JSON.parse(raw) : null;
        } catch(e) {
            return null;
        }
    };

    kit.storage_set_json = function(key, value) {
        try { localStorage.setItem(key, JSON.stringify(value)); } catch(e) {}
    };

    /* Build legend badges into a container element.
       config:
         container:       jQuery selector or element for the legend row
         series_keys:     array of all series keys in display order
         palette:         { key: dot_colour }
         labels:          { key: display_label }
         text_colors:     { key: text_colour }   (optional, falls back to palette)
         bg_colors:       { key: bg_colour }      (optional, falls back to muted grey)
         hidden:          { key: true } map of currently hidden keys
         on_toggle(key, hidden_map):  called after a badge is clicked
       Skips rebuild if skip===true. */
    kit.build_legend = function(config, skip) {
        if (skip) return;
        var $el = $(config.container);
        $el.empty();
        var keys = config.series_keys || [];
        var palette = config.palette || {};
        var labels = config.labels || {};
        var hidden = config.hidden || {};
        var text_colors = config.text_colors || {};
        var bg_colors = config.bg_colors || {};

        for (var i = 0; i < keys.length; i++) {
            var k = keys[i];
            var is_off = !!hidden[k];
            var dot = palette[k] || '#888';
            var tc = text_colors[k] || dot;
            var bg = bg_colors[k] || 'rgba(110,110,115,0.12)';
            var badge = $('<span class="dashboard-legend-badge' +
                (is_off ? ' dashboard-legend-badge-off' : '') +
                '" data-key="' + k + '"></span>');
            badge.css({'color': tc, 'background': bg});
            var dot_el = $('<span class="dashboard-legend-badge-dot"></span>');
            dot_el.css('background', dot);
            badge.append(dot_el);
            badge.append(labels[k] || k);
            $el.append(badge);
        }

        $el.off('click.toggle').on('click.toggle', '.dashboard-legend-badge', function() {
            var $badge = $(this);
            var key = $badge.data('key');
            var h = config.hidden || {};
            if (h[key]) {
                delete h[key];
                $badge.removeClass('dashboard-legend-badge-off');
            } else {
                h[key] = true;
                $badge.addClass('dashboard-legend-badge-off');
            }
            if (typeof config.on_toggle === 'function') {
                config.on_toggle(key, h);
            }
        });
    };

    /* Build and inject the hero pill group HTML from a theme object.
       theme:
         name:            dashboard label, e.g. 'Scheduler'
         pill_bg:         CSS colour for the name pill background
         pill_color:      CSS colour for the name pill text
         pill_link_bg:    CSS colour for the link pill backgrounds
         pill_link_color: CSS colour for the link pill text
         pill_links:      [{label, href}] shown below the name */
    kit.init_hero_pill = function(selector, theme) {
        var html = '<div class="dashboard-hero-pill-name" style="background:' +
            theme.pill_bg + ';color:' + theme.pill_color + '">' + theme.name + '</div>';
        if (theme.pill_links && theme.pill_links.length) {
            for (var i = 0; i < theme.pill_links.length; i++) {
                var link = theme.pill_links[i];
                html += '<a href="' + link.href +
                    '" class="dashboard-hero-pill-link" style="background:' +
                    theme.pill_link_bg + ';color:' + theme.pill_link_color + '">' +
                    link.label + '</a>';
            }
        }
        $(selector).html(html);
    };

    kit.set_fit_label = function(selector, label_text, action) {
        var el = $(selector);
        var font_size = 12;
        var action_font_size = font_size * 0.92;
        var line_height = 16;
        var pad_x = 5;
        var pad_y = 2;
        var svg_el = el.find('.stat-card-label-svg');

        if (svg_el.length === 0) {
            var svg_html = '<svg class="stat-card-label-svg" viewBox="0 0 100 ' + line_height +
                '" preserveAspectRatio="xMinYMid meet">' +
                '<text x="0" y="' + font_size + '" style="font-size:' + font_size +
                'px" class="stat-card-label-svg-text"></text>';
            if (action) {
                svg_html += '<rect class="stat-card-label-svg-action-bg" rx="2" ry="2"></rect>' +
                    '<text y="' + font_size + '" style="font-size:' + action_font_size +
                    'px;cursor:pointer" class="stat-card-label-svg-action"></text>';
            }
            svg_html += '</svg>';
            svg_el = $(svg_html);
            el.prepend(svg_el);

            if (action) {
                var action_group = svg_el.find('.stat-card-label-svg-action, .stat-card-label-svg-action-bg');
                action_group.on('click', action.on_click);
            }
        }

        var label_node = svg_el.find('.stat-card-label-svg-text');
        label_node.text(label_text);
        var label_width = label_node[0].getComputedTextLength();

        var total_width = label_width;

        if (action) {
            var action_node = svg_el.find('.stat-card-label-svg-action');
            action_node.text(action.text);
            var gap = font_size * 0.5;
            var text_width = action_node[0].getComputedTextLength();
            var action_x = label_width + gap;
            action_node.attr('x', action_x + pad_x);

            var bg = svg_el.find('.stat-card-label-svg-action-bg');
            var bg_height = action_font_size + pad_y * 2;
            var bg_y = font_size - action_font_size - pad_y + 1;
            bg.attr('x', action_x);
            bg.attr('y', bg_y);
            bg.attr('width', text_width + pad_x * 2);
            bg.attr('height', bg_height);

            total_width = action_x + text_width + pad_x * 2;
        }

        svg_el[0].setAttribute('viewBox', '0 0 ' + total_width + ' ' + line_height);
    };

    kit.set_fit_value = function(selector, text) {
        var el = $(selector);
        var is_sm = el.hasClass('stat-card-value-sm');
        var size_class = is_sm ? 'stat-card-value-svg-sm' : 'stat-card-value-svg-lg';
        var font_size = is_sm ? 14 : 22;
        var line_height = is_sm ? 16 : 24;

        var parent = el.closest('.stat-card-fit-container');
        var svg_el = parent.find('.stat-card-value-svg');
        if (svg_el.length === 0) {
            svg_el = $('<svg class="stat-card-value-svg ' + size_class +
                '" viewBox="0 0 100 ' + line_height +
                '" preserveAspectRatio="xMinYMid meet">' +
                '<text x="0" y="' + font_size + '" style="font-size:' + font_size + 'px" class="stat-card-value-svg-text"></text></svg>');
            parent.append(svg_el);
        }
        var text_node = svg_el.find('text');
        text_node.text(text);

        var svg_dom = svg_el[0];
        var text_dom = text_node[0];
        var text_width = text_dom.getComputedTextLength();
        svg_dom.setAttribute('viewBox', '0 0 ' + text_width + ' ' + line_height);
    };

    /* Fade the dashboard into view after first render. */
    kit.reveal = function(selector) {
        $(selector || '.dashboard-page').css('opacity', '1');
    };

    // ////////////////////////////////////////////////////////////////////////
    // Live countdown - ticks every second, updates elements with
    // data-countdown-target="<ISO timestamp>" using relative_time_future.
    // ////////////////////////////////////////////////////////////////////////

    kit.countdown = {};
    kit.countdown._interval_id = null;

    kit.countdown._tick = function() {
        $('[data-countdown-target]').each(function() {
            var $cell = $(this);
            var iso = $cell.attr('data-countdown-target');
            $cell.text(kit.relative_time_future(iso));
        });
    };

    kit.countdown.start = function() {
        if (kit.countdown._interval_id) return;
        kit.countdown._interval_id = setInterval(kit.countdown._tick, 1000);
    };

    kit.countdown.stop = function() {
        if (kit.countdown._interval_id) {
            clearInterval(kit.countdown._interval_id);
            kit.countdown._interval_id = null;
        }
    };

    // ////////////////////////////////////////////////////////////////////////
    // Table header sorting
    // ////////////////////////////////////////////////////////////////////////

    kit.sortable_headers = function(table_selector, col_map) {
        var $table = $(table_selector);
        var sort_state = {col: null, asc: true};

        $table.find('thead th').each(function() {
            var $th = $(this);
            var header_text = $th.text().trim();
            if (col_map[header_text] !== undefined) {
                $th.css('cursor', 'pointer');
                $th.on('click', function() {
                    var col_index = col_map[header_text];
                    if (sort_state.col === col_index) {
                        sort_state.asc = !sort_state.asc;
                    } else {
                        sort_state.col = col_index;
                        sort_state.asc = true;
                    }
                    var $tbody = $table.find('tbody');
                    var rows = $tbody.find('tr').get();
                    rows.sort(function(a, b) {
                        var a_text = $(a).children('td').eq(col_index).text().trim().toLowerCase();
                        var b_text = $(b).children('td').eq(col_index).text().trim().toLowerCase();
                        var cmp = a_text.localeCompare(b_text);
                        return sort_state.asc ? cmp : -cmp;
                    });
                    $.each(rows, function(idx, row) {
                        $tbody.append(row);
                    });
                });
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////
    // Spark buffer management
    // ////////////////////////////////////////////////////////////////////////

    kit.spark = {};

    /* Create a new spark buffer set.
       Returns a handle with push, values, seed, and data accessors.
       config:
         keys:       array of buffer names, e.g. ['total_jobs', 'active', ...]
         window_ms:  rolling window in ms (default 60 * 60 * 1000)
         bucket_count: number of time buckets for downsampling (default 60) */
    kit.spark.create = function(config) {
        var keys = config.keys || [];
        var window_ms = config.window_ms || (60 * 60 * 1000);
        var bucket_count = config.bucket_count || 60;
        var seeded = false;

        var buffers = {};
        for (var i = 0; i < keys.length; i++) {
            buffers[keys[i]] = [];
        }

        var push = function(key, value) {
            var buf = buffers[key];
            if (!buf) return;
            var now = Date.now();
            buf.push({ts: now, value: value});
            var cutoff = now - window_ms;
            while (buf.length > 0 && buf[0].ts < cutoff) {
                buf.shift();
            }
        };

        var values = function(key) {
            var data = buffers[key];
            if (!data) return [];

            if (data.length <= bucket_count) {
                var out = new Array(data.length);
                for (var i = 0; i < data.length; i++) {
                    out[i] = data[i].value;
                }
                return out;
            }

            var now = Date.now();
            var w_start = now - window_ms;
            var b_size = window_ms / bucket_count;
            var buckets = new Array(bucket_count);
            for (var b = 0; b < bucket_count; b++) {
                buckets[b] = null;
            }
            for (var d = 0; d < data.length; d++) {
                var idx = Math.floor((data[d].ts - w_start) / b_size);
                if (idx < 0) idx = 0;
                if (idx >= bucket_count) idx = bucket_count - 1;
                buckets[idx] = data[d].value;
            }
            var last_val = buckets[0] !== null ? buckets[0] : 0;
            for (var f = 0; f < bucket_count; f++) {
                if (buckets[f] === null) {
                    buckets[f] = last_val;
                } else {
                    last_val = buckets[f];
                }
            }
            return buckets;
        };

        var seed_flat = function(flat_values) {
            if (seeded) return;
            var now = Date.now();
            var b_size = window_ms / bucket_count;
            var w_start = now - window_ms;
            for (var key in flat_values) {
                if (!flat_values.hasOwnProperty(key) || !buffers.hasOwnProperty(key)) continue;
                var val = flat_values[key];
                var arr = new Array(bucket_count);
                for (var j = 0; j < bucket_count; j++) {
                    arr[j] = {ts: w_start + (j + 1) * b_size, value: val};
                }
                buffers[key] = arr;
            }
            seeded = true;
        };

        return {
            push: push,
            values: values,
            seed_flat: seed_flat,
            data: function(key) { return buffers[key] || []; },
            is_seeded: function() { return seeded; },
            set_buffer: function(key, arr) { buffers[key] = arr; },
            window_ms: function() { return window_ms; }
        };
    };

    // ////////////////////////////////////////////////////////////////////
    // Recency gradient — highlight recently-arrived table rows
    // ////////////////////////////////////////////////////////////////////

    kit.recency = {};
    kit.recency.STEPS = 10;
    kit.recency.MAX_ALPHA = 0.30;

    /* Apply a fading tint to recently-arrived rows.
       config:
         container:  jQuery selector for the parent holding <tr data-ts="...">
         recent_ts:  array of timestamp strings, newest first, length <= STEPS
         rgb:        base color as an "R, G, B" string (e.g. '218, 165, 32') */
    kit.recency.apply = function(config) {
        var $container = $(config.container);
        var ts_list = config.recent_ts || [];
        var rgb = config.rgb || '218, 165, 32';
        var steps = kit.recency.STEPS;
        var max_a = kit.recency.MAX_ALPHA;

        var ts_set = {};
        for (var j = 0; j < ts_list.length && j < steps; j++) {
            ts_set[ts_list[j]] = true;
        }

        $container.find('tr[data-ts]').each(function() {
            var $row = $(this);
            if (!ts_set[$row.attr('data-ts')]) {
                $row.css('transition', 'background 1.5s ease');
                $row.css('background', '');
            }
        });

        for (var i = 0; i < ts_list.length && i < steps; i++) {
            var alpha = max_a * (1 - i / steps);
            var $row = $container.find('tr[data-ts="' + ts_list[i] + '"]');
            if (i === 0) {
                $row.css('transition', 'none');
            } else {
                $row.css('transition', 'background 0.4s ease');
            }
            $row.css('background', 'rgba(' + rgb + ', ' + alpha.toFixed(4) + ')');
        }
    };

    // ////////////////////////////////////////////////////////////////////////
    // Clipboard copy with tippy tooltip
    // ////////////////////////////////////////////////////////////////////////

    kit.copy_to_clipboard = function(elem, text) {
        navigator.clipboard.writeText(text).then(function() {
            var tip = tippy(elem, {
                content: 'Copied to clipboard',
                trigger: 'manual',
                placement: 'right',
                duration: [100, 100]
            });
            tip.show();
            setTimeout(function() { tip.hide(); tip.destroy(); }, 600);
        });
    };

    // ////////////////////////////////////////////////////////////////////////
    // Syntax highlighting (pure JS, no deps)
    // ////////////////////////////////////////////////////////////////////////

    kit._esc_html = function(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    };

    kit._highlight_json = function(text) {
        var trimmed = text.trim();
        try {
            var parsed = JSON.parse(trimmed);
            var pretty = JSON.stringify(parsed, null, 2);
        } catch(e) {
            return null;
        }
        var out = kit._esc_html(pretty);

        // .. color JSON tokens: keys, strings, numbers, booleans, null, punctuation
        out = out.replace(
            /(&quot;)((?:[^&]|&(?!quot;))*)(&quot;)\s*:/g,
            '<span class="na">$1$2$3</span>:'
        );
        out = out.replace(
            /:\s*(&quot;)((?:[^&]|&(?!quot;))*)(&quot;)/g,
            ': <span class="s">$1$2$3</span>'
        );
        out = out.replace(
            /:\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)/g,
            ': <span class="m">$1</span>'
        );
        out = out.replace(
            /:\s*(true|false|null)/g,
            ': <span class="kc">$1</span>'
        );
        out = out.replace(
            /([{}\[\],])/g,
            '<span class="p">$1</span>'
        );
        return out;
    };

    kit._highlight_traceback = function(text) {
        var out = kit._esc_html(text);

        // .. color File "path", line N
        out = out.replace(
            /(File\s+&quot;)(.*?)(&quot;,\s+line\s+)(\d+)/g,
            '<span class="n">$1</span><span class="s">$2</span><span class="n">$3</span><span class="m">$4</span>'
        );

        // .. color exception class and message on the last line
        out = out.replace(
            /^(\w+(?:\.\w+)*(?:Error|Exception|Warning|Fault))(:.*)?$/gm,
            function(match, cls, msg) {
                var result = '<span class="ne">' + cls + '</span>';
                if (msg) result += '<span class="n">' + msg + '</span>';
                return result;
            }
        );

        return out;
    };

    kit._highlight_xml = function(text) {
        var out = kit._esc_html(text);

        // .. color XML tags, attributes, values
        out = out.replace(
            /(&lt;\/?)([\w:.-]+)/g,
            '$1<span class="nt">$2</span>'
        );
        out = out.replace(
            /([\w:.-]+)(=)(&quot;)(.*?)(&quot;)/g,
            '<span class="na">$1</span>$2<span class="s">$3$4$5</span>'
        );
        return out;
    };

    kit._highlight_mixed = function(text) {
        var parts = [];
        var remaining = text;

        while (remaining.length) {
            // .. find the first embedded JSON object or array
            var json_start = -1;
            var open_char = '';
            var close_char = '';
            var idx_obj = remaining.indexOf('{');
            var idx_arr = remaining.indexOf('[');

            if (idx_obj !== -1 && (idx_arr === -1 || idx_obj < idx_arr)) {
                json_start = idx_obj;
                open_char = '{';
                close_char = '}';
            } else if (idx_arr !== -1) {
                json_start = idx_arr;
                open_char = '[';
                close_char = ']';
            }

            if (json_start === -1) {
                parts.push(kit._esc_html(remaining));
                break;
            }

            // .. find the matching closing bracket by counting depth
            var depth = 0;
            var in_string = false;
            var escape_next = false;
            var end_pos = -1;
            for (var c = json_start; c < remaining.length; c++) {
                var ch = remaining.charAt(c);
                if (escape_next) {
                    escape_next = false;
                    continue;
                }
                if (ch === '\\' && in_string) {
                    escape_next = true;
                    continue;
                }
                if (ch === '"') {
                    in_string = !in_string;
                    continue;
                }
                if (in_string) continue;
                if (ch === open_char) depth++;
                else if (ch === close_char) {
                    depth--;
                    if (depth === 0) {
                        end_pos = c;
                        break;
                    }
                }
            }

            if (end_pos === -1) {
                parts.push(kit._esc_html(remaining));
                break;
            }

            var candidate = remaining.substring(json_start, end_pos + 1);
            var highlighted = kit._highlight_json(candidate);

            if (highlighted) {
                if (json_start > 0) {
                    parts.push(kit._esc_html(remaining.substring(0, json_start)));
                }
                parts.push(highlighted);
                remaining = remaining.substring(end_pos + 1);
            } else {
                // .. not valid JSON, skip past this bracket
                parts.push(kit._esc_html(remaining.substring(0, json_start + 1)));
                remaining = remaining.substring(json_start + 1);
            }
        }

        return parts.join('');
    };

    kit.syntax_highlight = function(text) {
        var trimmed = text.trim();
        var html = null;

        // .. try pure JSON
        if ((trimmed.charAt(0) === '{' && trimmed.charAt(trimmed.length - 1) === '}') ||
            (trimmed.charAt(0) === '[' && trimmed.charAt(trimmed.length - 1) === ']')) {
            html = kit._highlight_json(text);
        }

        // .. try Python traceback
        if (!html && (trimmed.indexOf('Traceback') !== -1 || trimmed.indexOf('File "') !== -1)) {
            html = kit._highlight_traceback(text);
        }

        // .. try XML
        if (!html && trimmed.charAt(0) === '<') {
            html = kit._highlight_xml(text);
        }

        // .. try mixed text with embedded JSON
        if (!html && (trimmed.indexOf('{') !== -1 || trimmed.indexOf('[') !== -1)) {
            html = kit._highlight_mixed(text);
        }

        // .. fallback
        if (!html) {
            html = kit._esc_html(text);
        }

        return '<span class="syntax-monokai">' + html + '</span>';
    };
})();
