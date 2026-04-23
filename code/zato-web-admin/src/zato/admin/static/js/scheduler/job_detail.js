
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.scheduler === 'undefined') { $.fn.zato.scheduler = {}; }
$.fn.zato.scheduler.job_detail = {};

$.fn.zato.scheduler.job_detail.config = {
    cluster_id: '1',
    default_tab: 'executions',
    default_time_range: 0,
    chart_width: 700,
    empty_history_text: 'No run history',
    fit_value_selectors: ['#stat-total-runs', '#stat-next-fire'],
    fit_label_selectors: {
        '#stat-next-fire': {
            text: 'Next fire',
            action_text: 'Execute now',
            action_target: '#btn-execute-now'
        }
    },
    detail_tags: [
        { key: 'error',  label: 'Error',  color: '#c0392b', bg: 'rgba(192, 57, 43, 0.1)',
          dark_color: '#f06060', dark_bg: 'rgba(224, 82, 82, 0.22)' },
        { key: 'warn',   label: 'Warn',   color: '#b45309', bg: 'rgba(180, 83, 9, 0.1)',
          dark_color: '#e8b830', dark_bg: 'rgba(212, 160, 23, 0.22)' },
        { key: 'info',   label: 'Info',   color: '#2a7fbf', bg: 'rgba(42, 127, 191, 0.1)',
          dark_color: '#7ab8f0', dark_bg: 'rgba(91, 155, 213, 0.22)' },
        { key: 'system', label: 'System', color: '#999',    bg: 'rgba(153, 153, 153, 0.08)', dimmed: true,
          dark_color: '#aaa', dark_bg: 'rgba(160, 160, 160, 0.15)' }
    ],
    detail_panel: {
        bg: '#232336',
        border: '1px solid #3a3a52',
        row_border: '#3a3a52',
        owner_bg: '#232336',
        owner_color: '#d0d0d8',
        owner_border: '#3a3a52',
        shadow: '0 4px 16px rgba(0, 0, 0, 0.5)',
        font_size: '12px',
        level_colors: {
            'ERROR':  { stripe: '#e05252', badge_bg: 'rgba(224, 82, 82, 0.18)', badge_fg: '#f06060' },
            'WARN':   { stripe: '#d4a017', badge_bg: 'rgba(212, 160, 23, 0.18)', badge_fg: '#e8b830' },
            'INFO':   { stripe: '#5b9bd5', badge_bg: 'rgba(91, 155, 213, 0.18)', badge_fg: '#7ab8f0' },
            'SYSTEM': { stripe: '#888',    badge_bg: 'rgba(160, 160, 160, 0.12)', badge_fg: '#aaa' }
        },
        ts_color: '#9e9eaf',
        msg_color: '#e0e0ea',
        outcome_colors: {
            'ok':      { color: '#7ab8f0', bg: 'rgba(91, 155, 213, 0.22)' },
            'error':   { color: '#f06060', bg: 'rgba(224, 82, 82, 0.22)' },
            'timeout': { color: '#e8b830', bg: 'rgba(212, 160, 23, 0.22)' },
            'running': { color: '#bbb',    bg: 'rgba(187, 187, 187, 0.15)' },
            'skipped_already_in_flight': { color: '#c4a8e8', bg: 'rgba(167, 134, 213, 0.22)' },
            'missed_catchup':            { color: '#d4b88a', bg: 'rgba(180, 150, 110, 0.22)' }
        }
    }
};

$.fn.zato.scheduler.job_detail._dashboard = function() {
    return $.fn.zato.scheduler.dashboard;
};

$.fn.zato.scheduler.job_detail._time_range_minutes = 0;
$.fn.zato.scheduler.job_detail._job_data = {};
$.fn.zato.scheduler.job_detail._pagination = null;
$.fn.zato.scheduler.job_detail._runs_rendered = false;
$.fn.zato.scheduler.job_detail._object_id = '';
$.fn.zato.scheduler.job_detail._fit_labels_applied = {};
$.fn.zato.scheduler.job_detail._poll_config = {};

$.fn.zato.scheduler.job_detail._hidden_series_key = function() {
    return 'zato_hidden_series_' + $.fn.zato.scheduler.job_detail._object_id;
};

$.fn.zato.scheduler.job_detail._get_hidden_series = function() {
    var stored = $.fn.zato.dashboard_kit.storage_get_json(
        $.fn.zato.scheduler.job_detail._hidden_series_key()
    );
    if (stored === null) {
        stored = {};
    }
    return stored;
};

$.fn.zato.scheduler.job_detail._set_hidden_series = function(hidden) {
    $.fn.zato.dashboard_kit.storage_set_json(
        $.fn.zato.scheduler.job_detail._hidden_series_key(), hidden
    );
};

// ////////////////////////////////////////////////////////////////////////////
// Outcome priority for grouping (higher = more significant)
// ////////////////////////////////////////////////////////////////////////////

// ////////////////////////////////////////////////////////////////////////////
// Filter history by time range
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail._filter_by_range = function(history) {
    var minutes = $.fn.zato.scheduler.job_detail._time_range_minutes;
    if (!minutes || minutes <= 0 || !history) return history;
    var cutoff = Date.now() - (minutes * 60 * 1000);
    var filtered = [];
    for (var i = 0; i < history.length; i++) {
        var ts = history[i].actual_fire_time_iso;
        if (new Date(ts).getTime() >= cutoff) {
            filtered.push(history[i]);
        }
    }
    return filtered;
};

// ////////////////////////////////////////////////////////////////////////////
// Filter history by hidden outcome series
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail._filter_by_outcome = function(history) {
    if (!history) return history;
    var hidden = $.fn.zato.scheduler.job_detail._get_hidden_series();
    var any_hidden = false;
    for (var k in hidden) {
        if (hidden.hasOwnProperty(k) && hidden[k]) { any_hidden = true; break; }
    }
    if (!any_hidden) return history;
    var out = [];
    for (var i = 0; i < history.length; i++) {
        if (!hidden[history[i].outcome]) out.push(history[i]);
    }
    return out;
};


// ////////////////////////////////////////////////////////////////////////////
// Render section title
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_header = function(job) {
    var title = '<a href="/zato/scheduler/dashboard/?cluster=1" class="detail-component-pill menu-link">Scheduler</a> ' +
        job.name;
    $('#detail-section-title').html(title);
};

// ////////////////////////////////////////////////////////////////////////////
// Render stats into the stat cards
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_stats = function(job) {
    var kit = $.fn.zato.dashboard_kit;
    var detail = $.fn.zato.scheduler.job_detail;
    var dashboard = detail._dashboard();

    var fit = detail.config.fit_value_selectors;
    var fit_labels = detail.config.fit_label_selectors;
    var set_value = function(selector, text) {
        if (fit.indexOf(selector) !== -1) {
            kit.set_fit_value(selector, text);
        } else {
            $(selector).text(text);
        }

        var label_cfg = fit_labels[selector];
        if (label_cfg && !detail._fit_labels_applied[selector]) {
            var container = $(selector).closest('.stat-card-fit-container');
            container.find('.stat-card-label').hide();
            kit.set_fit_label(container, label_cfg.text, {
                text: label_cfg.action_text,
                on_click: function() { $(label_cfg.action_target).trigger('click'); }
            });
            detail._fit_labels_applied[selector] = true;
        }
    };

    set_value('#stat-total-runs', kit.format_number_full(job.current_run));

    var recent = job.recent_outcomes;
    var error_count = 0;
    for (var i = 0; i < recent.length; i++) {
        if (recent[i] === 'error') error_count++;
    }
    var $errors = $('#stat-errors');
    $errors.text(kit.format_number_full(error_count));
    if (error_count > 0) {
        $errors.css('color', '#e0226e');
    } else {
        $errors.css('color', '');
    }

    $('#stat-avg-duration').text(dashboard.format_duration(job.last_duration_ms));

    var next_fire = job.next_fire_utc;
    if (next_fire) {
        set_value('#stat-next-fire', kit.format_local_time(next_fire));
    } else {
        set_value('#stat-next-fire', '-');
    }
};

// ////////////////////////////////////////////////////////////////////////////
// Render config grid
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail._highlight_extra = function(raw) {
    var esc = function(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); };

    try {
        var obj = JSON.parse(raw);
        return {type: 'json', html: $.fn.zato.scheduler.job_detail._highlight_json(obj, 0)};
    } catch(e) {}

    if (/^\s*</.test(raw) && />\s*$/.test(raw)) {
        return {type: 'xml', html: $.fn.zato.scheduler.job_detail._highlight_xml(raw)};
    }

    var lines = raw.split('\n');
    var ini_re = /^([^=\s]+)\s*=\s*(.*)$/;
    var ini_count = 0;
    for (var i = 0; i < lines.length; i++) {
        var trimmed = lines[i].trim();
        if (trimmed === '' || trimmed.charAt(0) === '#' || trimmed.charAt(0) === ';') continue;
        if (ini_re.test(trimmed)) ini_count++;
    }
    if (ini_count > 0 && ini_count >= Math.floor(lines.length * 0.5)) {
        var ini_html = '';
        for (var j = 0; j < lines.length; j++) {
            var line = lines[j];
            var m = line.match(ini_re);
            if (m) {
                ini_html += '<span class="hl-key">' + esc(m[1]) + '</span>' +
                    '<span class="hl-punct">=</span>' +
                    '<span class="hl-str">' + esc(m[2]) + '</span>\n';
            } else {
                ini_html += '<span class="hl-comment">' + esc(line) + '</span>\n';
            }
        }
        return {type: 'ini', html: ini_html};
    }

    return {type: 'text', html: esc(raw)};
};

$.fn.zato.scheduler.job_detail._highlight_json = function(val, depth) {
    var esc = function(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); };
    var indent = '';
    for (var d = 0; d < depth; d++) indent += '  ';
    var indent1 = indent + '  ';

    if (val === null) return '<span class="hl-null">null</span>';
    if (typeof val === 'boolean') return '<span class="hl-bool">' + val + '</span>';
    if (typeof val === 'number') return '<span class="hl-num">' + val + '</span>';
    if (typeof val === 'string') return '<span class="hl-str">"' + esc(val) + '"</span>';

    if (Array.isArray(val)) {
        if (val.length === 0) return '<span class="hl-punct">[]</span>';
        var arr_parts = [];
        for (var i = 0; i < val.length; i++) {
            arr_parts.push(indent1 + $.fn.zato.scheduler.job_detail._highlight_json(val[i], depth + 1));
        }
        return '<span class="hl-punct">[</span>\n' + arr_parts.join('<span class="hl-punct">,</span>\n') + '\n' + indent + '<span class="hl-punct">]</span>';
    }

    var keys = Object.keys(val);
    if (keys.length === 0) return '<span class="hl-punct">{}</span>';
    var obj_parts = [];
    for (var k = 0; k < keys.length; k++) {
        obj_parts.push(indent1 + '<span class="hl-key">"' + esc(keys[k]) + '"</span><span class="hl-punct">: </span>' +
            $.fn.zato.scheduler.job_detail._highlight_json(val[keys[k]], depth + 1));
    }
    return '<span class="hl-punct">{</span>\n' + obj_parts.join('<span class="hl-punct">,</span>\n') + '\n' + indent + '<span class="hl-punct">}</span>';
};

$.fn.zato.scheduler.job_detail._highlight_xml = function(raw) {
    var esc = function(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); };
    return raw.replace(/(<\/?[\w:-]+)((?:\s+[\w:-]+="[^"]*")*)(\/?>)/g, function(match, tag, attrs, close) {
        var result = '<span class="hl-tag">' + esc(tag) + '</span>';
        if (attrs) {
            result += attrs.replace(/([\w:-]+)(=")([^"]*")/, function(m2, name, eq, val) {
                return ' <span class="hl-key">' + esc(name) + '</span><span class="hl-punct">=</span><span class="hl-str">"' + esc(val) + '</span>';
            });
        }
        result += '<span class="hl-tag">' + esc(close) + '</span>';
        return result;
    });
};

$.fn.zato.scheduler.job_detail.render_config = function(job, cluster_id) {
    var container = $('#detail-config-grid');
    var kit = $.fn.zato.dashboard_kit;
    var dashboard = $.fn.zato.scheduler.job_detail._dashboard();

    var esc = function(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); };

    var card = function(label, value, is_html) {
        return '<div class="meta-card">' +
            '<div class="meta-label">' + esc(label) + '</div>' +
            '<div class="meta-value">' + (is_html ? value : esc(value)) + '</div>' +
            '</div>';
    };

    var has_extra = job.extra && job.extra.trim();
    var cards_class = has_extra ? 'detail-config-cards detail-metadata detail-config-cards-3col' : 'detail-config-cards detail-metadata';

    var html = has_extra ? '<div class="detail-config-row">' : '';
    html += '<div class="' + cards_class + '">';

    var config_service = job.service;
    var service_link = config_service ? $.fn.zato.data_table.service_text(config_service, cluster_id) : '-';
    html += card('Service', service_link, true);

    var type_label = dashboard.job_type_labels[job.job_type];
    html += card('Job type', type_label, false);

    var start_display = job.start_date ? kit.format_local_time(job.start_date) : '-';
    html += card('Start date', start_display, false);

    var status_html = job.is_active
        ? '<span style="color:#1b855e;font-weight:700">Active</span>'
        : '<span style="color:var(--text-muted);font-weight:700">Paused</span>';
    html += card('Status', status_html, true);

    if (job.job_type === 'interval_based') {
        var parts = [];
        if (job.weeks) parts.push(kit.format_number_full(job.weeks) + (job.weeks === 1 ? ' week' : ' weeks'));
        if (job.days) parts.push(kit.format_number_full(job.days) + (job.days === 1 ? ' day' : ' days'));
        if (job.hours) parts.push(kit.format_number_full(job.hours) + (job.hours === 1 ? ' hour' : ' hours'));
        if (job.minutes) parts.push(kit.format_number_full(job.minutes) + (job.minutes === 1 ? ' minute' : ' minutes'));
        if (job.seconds) parts.push(kit.format_number_full(job.seconds) + (job.seconds === 1 ? ' second' : ' seconds'));
        var interval_text = '-';
        if (parts.length === 1) {
            interval_text = parts[0];
        } else if (parts.length > 1) {
            interval_text = parts.slice(0, -1).join(', ') + ' and ' + parts[parts.length - 1];
        }
        html += card('Interval', interval_text, false);
    }

    if (job.repeats !== null && job.repeats !== undefined) {
        html += card('Repeats', job.repeats === 0 ? 'Unlimited' : kit.format_number_full(job.repeats), false);
    }

    if (job.max_execution_time_ms) {
        html += card('Max execution time', dashboard.format_duration(job.max_execution_time_ms), false);
    }

    if (job.jitter_ms) {
        html += card('Jitter', kit.format_number_full(job.jitter_ms) + ' ms', false);
    }

    var manage_url = '/zato/scheduler/?cluster=' + cluster_id + '&query=' + encodeURIComponent(job.name);
    html += card('Manage', '<a href="' + manage_url + '">Click to configure</a>', true);

    html += '</div>';

    if (has_extra) {
        var highlighted = $.fn.zato.scheduler.job_detail._highlight_extra(job.extra.trim());
        html += '<div class="detail-metadata detail-config-extra-card">' +
            '<div class="meta-label">Extra data</div>' +
            '<pre class="detail-config-extra">' + highlighted.html + '</pre>' +
            '</div>';
        html += '</div>';
    }

    container.html(html);
};

// ////////////////////////////////////////////////////////////////////////////
// Render timeline — Stacked Area Sparkline
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail._timeline_skip_legend = false;

$.fn.zato.scheduler.job_detail._build_legend = function() {
    var detail = $.fn.zato.scheduler.job_detail;
    var dashboard = detail._dashboard();
    var bar_colors = dashboard.outcome_bar_colors;
    var outcome_keys = ['ok', 'skipped_already_in_flight', 'missed_catchup', 'timeout', 'error'];

    $.fn.zato.dashboard_kit.build_legend({
        container: '#detail-timeline-legend',
        series_keys: outcome_keys,
        palette: bar_colors,
        labels: dashboard.outcome_labels,
        text_colors: dashboard.outcome_colors,
        bg_colors: dashboard.outcome_bg_colors,
        hidden: detail._get_hidden_series(),
        on_toggle: function(_key, h) {
            detail._set_hidden_series(h);
            detail._redraw();
        }
    }, detail._timeline_skip_legend);
};

$.fn.zato.scheduler.job_detail.render_timeline = function(history) {
    var detail = $.fn.zato.scheduler.job_detail;
    var container = $('#detail-timeline');
    var filtered = detail._filter_by_outcome(detail._filter_by_range(history));
    var kit = $.fn.zato.dashboard_kit;
    var dashboard = detail._dashboard();
    var bar_colors = dashboard.outcome_bar_colors;
    var outcome_labels = dashboard.outcome_labels;
    var outcome_keys = ['ok', 'skipped_already_in_flight', 'missed_catchup', 'timeout', 'error'];
    var hidden = detail._get_hidden_series();

    detail._build_legend();

    if (!filtered || filtered.length === 0) {
        container.html('<div class="dashboard-inline-empty">' + detail.config.empty_history_text + '</div>');
        return;
    }

    var chart_width = container.width();
    var chart_height = 28;
    var pad_top = 1;
    var pad_bot = 1;
    var draw_h = chart_height - pad_top - pad_bot;

    var timestamps = [];
    for (var i = 0; i < filtered.length; i++) {
        timestamps.push(new Date(filtered[i].actual_fire_time_iso).getTime());
    }

    if (timestamps.length === 0) {
        container.html('<div class="dashboard-inline-empty">' + detail.config.empty_history_text + '</div>');
        return;
    }

    var min_time = Math.min.apply(null, timestamps);
    var max_time = Math.max.apply(null, timestamps);
    var interval_ms = detail._job_data.interval_ms;
    var min_span = interval_ms ? interval_ms * 10 : 3600000;
    var time_span = max_time - min_time;
    if (time_span < min_span) {
        min_time = max_time - min_span;
        time_span = min_span;
    }

    var visible_keys = [];
    for (var vk = 0; vk < outcome_keys.length; vk++) {
        if (!hidden[outcome_keys[vk]]) visible_keys.push(outcome_keys[vk]);
    }

    var bucket_count = Math.min(80, Math.max(16, Math.floor(chart_width / 14)));
    var bucket_ms = time_span / bucket_count;
    var buckets = [];
    for (var b = 0; b < bucket_count; b++) {
        var bk = {total: 0, start: min_time + b * bucket_ms, end: min_time + (b + 1) * bucket_ms};
        for (var k = 0; k < outcome_keys.length; k++) bk[outcome_keys[k]] = 0;
        buckets.push(bk);
    }

    for (var r = 0; r < filtered.length; r++) {
        var row_t = new Date(filtered[r].actual_fire_time_iso).getTime();
        var bi = Math.min(bucket_count - 1, Math.max(0, Math.floor((row_t - min_time) / bucket_ms)));
        var outcome = filtered[r].outcome;
        if (buckets[bi].hasOwnProperty(outcome)) {
            buckets[bi][outcome]++;
        } else {
            buckets[bi]['ok']++;
        }
        buckets[bi].total++;
    }

    var max_stack = 0;
    for (var ms = 0; ms < buckets.length; ms++) {
        var stack_sum = 0;
        for (var sv = 0; sv < visible_keys.length; sv++) {
            stack_sum += buckets[ms][visible_keys[sv]];
        }
        if (stack_sum > max_stack) max_stack = stack_sum;
    }
    if (max_stack === 0) max_stack = 1;

    var seg_w = chart_width / bucket_count;
    var baseline = chart_height - pad_bot;

    var _bezier = function(pts) {
        if (pts.length < 2) return '';
        var d = 'M' + pts[0].x.toFixed(1) + ',' + pts[0].y.toFixed(1);
        for (var ci = 1; ci < pts.length; ci++) {
            var p = pts[ci - 1];
            var c = pts[ci];
            var cpx = (p.x + c.x) / 2;
            d += ' C' + cpx.toFixed(1) + ',' + p.y.toFixed(1) +
                ' ' + cpx.toFixed(1) + ',' + c.y.toFixed(1) +
                ' ' + c.x.toFixed(1) + ',' + c.y.toFixed(1);
        }
        return d;
    };

    var cumulative = [];
    for (var ci2 = 0; ci2 < bucket_count; ci2++) cumulative.push(0);

    var _sanitize = function(k) { return String(k).replace(/[^A-Za-z0-9_]/g, '_'); };

    var svg = '<svg width="' + chart_width + '" height="' + chart_height + '" xmlns="http://www.w3.org/2000/svg">';
    svg += '<defs>';
    for (var gd = 0; gd < visible_keys.length; gd++) {
        var gd_c = bar_colors[visible_keys[gd]];
        svg += '<linearGradient id="tlGrad_' + _sanitize(visible_keys[gd]) + '" x1="0" y1="0" x2="0" y2="1">' +
            '<stop offset="0" stop-color="' + gd_c + '" stop-opacity="0.25"/>' +
            '<stop offset="1" stop-color="' + gd_c + '" stop-opacity="0.03"/>' +
            '</linearGradient>';
    }
    svg += '</defs>';

    for (var li = 0; li < visible_keys.length; li++) {
        var okey = visible_keys[li];
        var color = bar_colors[okey];

        var has_any = false;
        for (var chk = 0; chk < bucket_count; chk++) {
            if (buckets[chk][okey] > 0) { has_any = true; break; }
        }
        if (!has_any) continue;

        var top_pts = [];
        var bot_pts = [];

        for (var si = 0; si < bucket_count; si++) {
            var x = si * seg_w + seg_w / 2;
            var val = buckets[si][okey];
            var prev_cum = cumulative[si];
            var new_cum = prev_cum + val;

            var y_bot = baseline - (prev_cum / max_stack) * draw_h;
            var y_top = baseline - (new_cum / max_stack) * draw_h;

            top_pts.push({x: x, y: y_top});
            bot_pts.push({x: x, y: y_bot});
        }

        var top_path = _bezier(top_pts);
        var bot_rev = bot_pts.slice().reverse();
        var bot_path = _bezier(bot_rev);

        var area = top_path + ' L' + bot_rev[0].x.toFixed(1) + ',' + bot_rev[0].y.toFixed(1) +
            bot_path.substring(bot_path.indexOf('C') - 1) +
            ' Z';

        svg += '<path d="' + area + '" fill="url(#tlGrad_' + _sanitize(okey) + ')" />';
        svg += '<path d="' + top_path + '" fill="none" stroke="' + color + '" stroke-width="1.5" stroke-opacity="0.7" stroke-linecap="round" stroke-linejoin="round" />';

        var last_pt = top_pts[top_pts.length - 1];
        svg += '<circle cx="' + last_pt.x.toFixed(2) + '" cy="' + last_pt.y.toFixed(2) + '" r="5.5" fill="none" stroke="' + color + '" stroke-opacity="0.35" stroke-width="1"/>';
        svg += '<circle cx="' + last_pt.x.toFixed(2) + '" cy="' + last_pt.y.toFixed(2) + '" r="3.5" fill="' + color + '"/>';

        for (var si2 = 0; si2 < bucket_count; si2++) {
            cumulative[si2] += buckets[si2][okey];
        }
    }

    for (var hi = 0; hi < bucket_count; hi++) {
        svg += '<rect class="dashboard-chart-hitrect" x="' + (hi * seg_w).toFixed(1) + '" y="0" ' +
            'width="' + seg_w.toFixed(1) + '" height="' + chart_height + '" ' +
            'fill="transparent" data-bucket="' + hi + '" />';
    }

    svg += '</svg>';
    container.html(svg);

    container.off('mousemove.timeline mouseleave.timeline');
    container.on('mousemove.timeline', function(event) {
        var target = event.target;
        if (!$(target).attr('data-bucket')) {
            kit.tooltip.hide();
            return;
        }

        var idx = parseInt($(target).attr('data-bucket'), 10);
        var bkt = buckets[idx];
        if (!bkt || bkt.total === 0) { kit.tooltip.hide(); return; }

        var t_from = kit.format_local_time(new Date(bkt.start).toISOString());
        var t_to = kit.format_local_time(new Date(bkt.end).toISOString());

        var tt = '<div class="dashboard-tooltip-header">' +
            '<div class="dashboard-tooltip-title">' + t_from + '</div>' +
            '<div class="dashboard-tooltip-subtitle">to ' + t_to + '</div>' +
            '</div>';

        tt += '<div class="dashboard-tooltip-body">';
        for (var oi = 0; oi < outcome_keys.length; oi++) {
            var ok2 = outcome_keys[oi];
            if (hidden[ok2]) continue;
            var ov = bkt[ok2];
            if (ov === 0) continue;
            var pct = Math.round((ov / bkt.total) * 100);
            tt += '<div class="dashboard-tooltip-row">' +
                '<span class="dashboard-tooltip-dot" style="background:' + bar_colors[ok2] + '"></span>' +
                outcome_labels[ok2] + ': ' + kit.format_number_full(ov) +
                ' <span class="dashboard-tooltip-muted">(' + pct + '%)</span>' +
                '</div>';
        }
        tt += '<div class="dashboard-tooltip-total">Total: ' + kit.format_number_full(bkt.total) + '</div>';
        tt += '</div>';

        kit.tooltip.show(event, tt);
    });

    container.on('mouseleave.timeline', function() {
        kit.tooltip.hide();
    });
};

// ////////////////////////////////////////////////////////////////////////////
// Fake data generator (temporary, until backend provides real data)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail._generate_fake_tags = function(run) {
    var detail = $.fn.zato.scheduler.job_detail;
    var tag_defs = detail.config.detail_tags;
    var panel_cfg = detail.config.detail_panel;

    var seed = run * 2654435761;
    var _next = function() { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed; };

    var tags = {};
    for (var t = 0; t < tag_defs.length; t++) {
        var n = _next() % 8;
        if (tag_defs[t].key === 'system') n = 2;
        if (tag_defs[t].key === 'info') n = Math.max(n, 1);
        tags[tag_defs[t].key] = n;
    }

    var levels = [];
    for (var key in tags) {
        for (var c = 0; c < tags[key]; c++) {
            levels.push(key);
        }
    }

    var messages = {
        'error': [
            'Traceback (most recent call last): File "/opt/zato/server/service.py", line 482, in _invoke File "/opt/zato/server/services/sync.py", line 137, in handle response = self.outgoing.plain_http["crm-api"].conn.post(cid, payload) File "/opt/zato/common/util/http_.py", line 94, in post raise ConnectionError("POST /api/v2/contacts failed: Connection refused (errno 111) to crm.internal:8443 after 3 retries, last attempt at 2026-04-23T22:03:14.881Z") ConnectionError: POST /api/v2/contacts failed: Connection refused',
            'Traceback (most recent call last): File "/opt/zato/server/service.py", line 482, in _invoke File "/opt/zato/server/services/etl.py", line 58, in handle rows = session.execute(text("SELECT * FROM staging.events WHERE ts > :cutoff"), {"cutoff": cutoff}).fetchall() File "/opt/zato/lib/sqlalchemy/engine/result.py", line 1491, in fetchall sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server: Connection timed out. Is the server running on host "pg-replica-03" (10.0.8.47) and accepting TCP/IP connections on port 5432?',
            'AuthenticationError: SASL SCRAM-SHA-256 authentication failed for user "zato_svc" on broker amqps://mq.prod.internal:5671/vhost_main - server says: PLAIN login refused (credentials expired at 2026-04-22T00:00:00Z), full context: {"vhost": "vhost_main", "channel": 7, "delivery_tag": null, "exchange": "events.fanout", "routing_key": "audit.login"}',
            'OSError: [Errno 28] No space left on device: "/opt/zato/server/logs/audit/2026-04-23/batch-0041.json.gz" while rotating log segment 41 of 50 (segment size: 67108864 bytes, total written today: 2748842016 bytes, partition /dev/sda1 usage: 100%)',
            'MemoryError: Unable to allocate 2.4 GiB for an array with shape (312847, 1024) and data type float64. RSS=7841MiB, VMS=15922MiB, swap_used=4093MiB. Triggered during: numpy.dot(embeddings_matrix, query_vector.T) in /opt/zato/server/services/ml_ranking.py:228'
        ],
        'warn': [
            'Slow response from downstream: POST /api/v2/inventory/sync responded in 12847ms (threshold: 5000ms), payload size: 847KB, response: {"status": "partial", "synced": 4021, "failed": 17, "retry_after": 30, "rate_limit_remaining": 12, "request_id": "req-8a3f7c21-ef90-4b12-9dc1-cc7e8843a1bf"}',
            'Retrying connection to redis-sentinel://sentinel-01:26379,sentinel-02:26379,sentinel-03:26379/mymaster (attempt 3/5, backoff 4.0s) after error: ReadOnlyError("READONLY You can not write against a read-only replica"), last master was 10.0.2.18:6379, failover may be in progress',
            'Queue depth warning: channel="orders.process" depth=84729 consumers=3 rate=142msg/s eta_drain=596s threshold=50000. Consumer lag: [{"consumer": "worker-07", "lag": 34201, "last_ack": "2026-04-23T22:01:08Z"}, {"consumer": "worker-08", "lag": 28114, "last_ack": "2026-04-23T22:01:12Z"}, {"consumer": "worker-09", "lag": 22414, "last_ack": "2026-04-23T22:01:19Z"}]',
            'TLS certificate for *.api.partner.com (CN=*.api.partner.com, issuer=DigiCert SHA2 Extended Validation Server CA, serial=0A:F2:81:E3:00:00:00:00:68:9B:4F:0E) expires in 6 days (2026-04-29T23:59:59Z), auto-renewal via ACME scheduled but last attempt failed: HTTP 429 rate limit from CA'
        ],
        'info': [
            'Processing batch: {"batch_id": "batch-2026-04-23-0041", "source": "s3://data-lake-prod/incoming/contacts/2026/04/23/", "files": 847, "total_size_mb": 2341.7, "format": "parquet", "compression": "snappy", "schema_version": "v3.2.1", "started_at": "2026-04-23T22:03:14.012Z", "workers": 8, "partitions": 32}',
            'Synced 142 records to CRM: {"endpoint": "https://crm.internal:8443/api/v2/contacts", "method": "PATCH", "created": 38, "updated": 97, "skipped": 7, "duration_ms": 3841, "avg_latency_ms": 27.0, "p99_latency_ms": 142, "rate_limited": false, "request_id": "sync-8f3a2c1e", "idempotency_key": "idem-20260423-0041"}',
            'Cache refreshed: evicted 24,817 stale entries (older than 3600s), loaded 31,204 new entries from PostgreSQL materialized view "mv_product_catalog", memory delta: +48MiB (now 1.2GiB/4GiB), refresh took 2.8s, next scheduled at 2026-04-23T23:03:15Z',
            'Checkpoint saved: {"checkpoint_id": "ckpt-0041", "offset": 847293, "partition": 7, "consumer_group": "etl-pipeline-v3", "topic": "events.enriched", "committed_at": "2026-04-23T22:03:15.441Z", "lag_after_commit": 12}',
            'Heartbeat OK: cluster=zato-prod-east-1, node=worker-07, pid=48291, uptime=847291s, cpu=12.4%, rss=2841MiB, open_fds=847, active_connections={"http": 142, "amqp": 8, "redis": 24, "pg": 16}, requests_1m=4821, errors_1m=0'
        ],
        'system': [
            'Job started: scheduler_tick=2026-04-23T22:03:14.001Z, planned_fire=2026-04-23T22:03:14.000Z, drift_ms=1, cid=zc8f3a2b, server=zato-prod-east-1/worker-07, pid=48291',
            'Job finished: duration_ms=10841, outcome=ok, next_fire=2026-04-23T22:04:14.000Z, items_processed=142, peak_memory_mb=284'
        ]
    };

    var entries = [];
    var base_ts = new Date();
    base_ts.setMinutes(base_ts.getMinutes() - run);

    for (var e = 0; e < levels.length; e++) {
        var level = levels[e];
        var ms_offset = (_next() % 5000);
        var ts = new Date(base_ts.getTime() + ms_offset);
        var h = String(ts.getHours()).length < 2 ? '0' + ts.getHours() : String(ts.getHours());
        var m = String(ts.getMinutes()).length < 2 ? '0' + ts.getMinutes() : String(ts.getMinutes());
        var s = String(ts.getSeconds()).length < 2 ? '0' + ts.getSeconds() : String(ts.getSeconds());
        var ms = String(ts.getMilliseconds());
        while (ms.length < 3) ms = '0' + ms;
        var ts_str = h + ':' + m + ':' + s + '.' + ms;

        var pool = messages[level];
        var msg = pool[_next() % pool.length];

        entries.push({ timestamp: ts_str, level: level.toUpperCase(), message: msg });
    }

    entries.sort(function(a, b) { return a.timestamp < b.timestamp ? -1 : a.timestamp > b.timestamp ? 1 : 0; });

    return { tags: tags, entries: entries };
};

// ////////////////////////////////////////////////////////////////////////////
// Render history table (grouped, paginated)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail._render_tag_badges = function(run) {
    var detail = $.fn.zato.scheduler.job_detail;
    var tag_defs = detail.config.detail_tags;
    var fake = detail._generate_fake_tags(run);
    var tags = fake.tags;
    var html = '';
    for (var t = 0; t < tag_defs.length; t++) {
        var def = tag_defs[t];
        var count = tags[def.key];
        if (count > 0) {
            var style = 'color:' + def.color + ';background:' + def.bg;
            if (def.dimmed) style += ';opacity:0.55';
            html += '<span class="detail-tag" data-key="' + def.key + '" style="' + style + '">' +
                def.label + ' x' + count + '</span>';
        }
    }
    return html;
};

$.fn.zato.scheduler.job_detail._render_dark_tag_badges = function(run) {
    var detail = $.fn.zato.scheduler.job_detail;
    var tag_defs = detail.config.detail_tags;
    var fake = detail._generate_fake_tags(run);
    var tags = fake.tags;
    var html = '';
    for (var t = 0; t < tag_defs.length; t++) {
        var def = tag_defs[t];
        var count = tags[def.key];
        if (count > 0) {
            var style = 'color:' + def.dark_color + ';background:' + def.dark_bg;
            if (def.dimmed) style += ';opacity:0.55';
            html += '<span class="detail-tag" data-key="' + def.key + '" style="' + style + '">' +
                def.label + ' x' + count + '</span>';
        }
    }
    return html;
};

$.fn.zato.scheduler.job_detail._render_mirror_row = function(record) {
    var kit = $.fn.zato.dashboard_kit;
    var detail = $.fn.zato.scheduler.job_detail;
    var cfg = detail.config.detail_panel;

    var run_number = (record.current_run !== null && record.current_run !== undefined)
        ? kit.format_number_full(record.current_run) : '-';

    // .. build outcome badge from brighter config colors
    var oc = cfg.outcome_colors[record.outcome] || cfg.outcome_colors['ok'];
    var outcome_label = record.outcome.replace(/_/g, ' ').toUpperCase();
    var outcome_html = '<span class="dashboard-outcome-badge" style="color:' + oc.color + ';background:' + oc.bg + '">' + outcome_label + '</span>';

    var tag_html = detail._render_dark_tag_badges(record.current_run);

    var html = '<div class="detail-log-line detail-log-mirror" style="border-bottom:1px solid ' + cfg.row_border + '">';
    html += '<div class="detail-log-stripe" style="background:' + cfg.owner_color + '"></div>';
    html += '<div class="detail-log-ts"><span class="detail-log-level" style="color:' + cfg.owner_color + ';background:rgba(255,255,255,0.08)">Run #' + run_number + '</span></div>';
    html += '<div class="detail-log-level-col">' + outcome_html + '</div>';
    var action_style = 'color:#aaa;background:rgba(255,255,255,0.08)';
    html += '<div class="detail-log-msg" style="color:' + cfg.owner_color + '">' + tag_html + '</div>';
    html += '<div class="detail-log-actions">';
    html += '<span class="dashboard-panel-action-badge detail-action-copy-all" style="' + action_style + '">Copy</span>';
    html += '<span class="dashboard-panel-action-badge detail-action-close" style="' + action_style + '">Close</span>';
    html += '</div>';
    html += '</div>';
    return html;
};

$.fn.zato.scheduler.job_detail._render_panel_row = function(run) {
    var kit = $.fn.zato.dashboard_kit;
    var detail = $.fn.zato.scheduler.job_detail;
    var cfg = detail.config.detail_panel;
    var fake = detail._generate_fake_tags(run);
    var entries = fake.entries;

    var html = '<tr class="detail-panel-row" data-run="' + run + '">';
    html += '<td colspan="6" style="padding:0">';
    html += '<div class="detail-panel-grid">';
    html += '<div class="detail-panel-inner">';
    html += '<div class="detail-panel-log" style="background:' + cfg.bg + ';border:' + cfg.border + ';font-size:' + cfg.font_size + '">';

    for (var e = 0; e < entries.length; e++) {
        var entry = entries[e];
        var lc = cfg.level_colors[entry.level];
        var border_style = (e < entries.length - 1) ? 'border-bottom:1px solid ' + cfg.row_border + ';' : '';

        var escaped_msg = entry.message.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        var highlighted_msg = kit.syntax_highlight(entry.message);
        html += '<div class="detail-log-line" style="' + border_style + '">';
        html += '<div class="detail-log-stripe" style="background:' + lc.stripe + '"></div>';
        html += '<div class="detail-log-ts" style="color:' + cfg.ts_color + '">' + entry.timestamp + '</div>';
        html += '<div class="detail-log-level-col"><span class="detail-log-level" style="color:' + lc.badge_fg + ';background:' + lc.badge_bg + '">' + entry.level + '</span></div>';
        html += '<div class="detail-log-msg" data-raw="' + escaped_msg + '" style="color:' + cfg.msg_color + '">' + highlighted_msg + '</div>';
        html += '<div class="detail-log-actions"><span class="dashboard-panel-action-badge detail-action-copy-row" style="color:#aaa;background:rgba(255,255,255,0.08)">Copy</span></div>';
        html += '</div>';
    }

    html += '</div>';
    html += '</div></div></td></tr>';
    return html;
};

$.fn.zato.scheduler.job_detail._render_single_row = function(record, extra_class) {
    var kit = $.fn.zato.dashboard_kit;
    var detail = $.fn.zato.scheduler.job_detail;
    var dashboard = detail._dashboard();
    var actual_time = kit.format_local_time(record.actual_fire_time_iso);
    var delay = (record.delay_ms !== null && record.delay_ms !== undefined && record.delay_ms > 0)
        ? kit.format_number_full(record.delay_ms) + ' ms'
        : '-';
    var duration = dashboard.format_duration(record.duration_ms);
    var outcome = dashboard.outcome_badge(record.outcome);
    var run_number = (record.current_run !== null && record.current_run !== undefined)
        ? kit.format_number_full(record.current_run) : '-';

    var row_ts = record.actual_fire_time_iso;
    var run_attr = (record.current_run !== null && record.current_run !== undefined) ? record.current_run : '';
    var cls = extra_class ? ' class="' + extra_class + '"' : '';
    var tag_html = detail._render_tag_badges(record.current_run);

    var row = '<tr' + cls + ' data-ts="' + row_ts + '" data-run="' + run_attr + '">';
    row += '<td class="dashboard-cell-mono-wrap dashboard-cell-center">' + run_number + '</td>';
    row += '<td class="dashboard-cell-center">' + outcome + '</td>';
    row += '<td class="dashboard-cell-mono">' + actual_time + '</td>';
    row += '<td class="dashboard-cell-mono-wrap dashboard-cell-center">' + duration + '</td>';
    row += '<td class="dashboard-cell-mono-wrap dashboard-cell-center">' + delay + '</td>';
    row += '<td class="detail-tag-cell">' + tag_html + '</td>';
    row += '</tr>';
    return row;
};


$.fn.zato.scheduler.job_detail._update_table_dim = function($body) {
    var has_expanded = $body.find('tr.detail-panel-row.expanded').length > 0;
    var $head = $('#detail-history-table-head');
    if (has_expanded) {
        $head.addClass('detail-dimmed');
        $body.addClass('detail-dimmed');
    } else {
        $head.removeClass('detail-dimmed');
        $body.removeClass('detail-dimmed');
    }
};

$.fn.zato.scheduler.job_detail._build_enabled_levels = function() {
    var levels = {};
    var tag_defs = $.fn.zato.scheduler.job_detail.config.detail_tags;
    for (var t = 0; t < tag_defs.length; t++) {
        levels[tag_defs[t].key] = true;
    }
    return levels;
};

$.fn.zato.scheduler.job_detail._apply_level_filter = function($panel) {
    var levels = $panel.data('enabled-levels');
    var tag_defs = $.fn.zato.scheduler.job_detail.config.detail_tags;
    $panel.find('.detail-log-line').not('.detail-log-mirror').each(function() {
        var $line = $(this);
        var level_text = $line.find('.detail-log-level').text().trim().toLowerCase();
        $line.css('opacity', levels[level_text] ? '' : '0.15');
    });

    // .. update badge appearance
    $panel.find('.detail-log-mirror .detail-tag').each(function() {
        var $tag = $(this);
        var key = $tag.attr('data-key');
        if (levels[key]) {
            var base_opacity = '';
            for (var t = 0; t < tag_defs.length; t++) {
                if (tag_defs[t].key === key && tag_defs[t].dimmed) {
                    base_opacity = '0.55';
                    break;
                }
            }
            $tag.css({'opacity': base_opacity, 'text-decoration': ''});
        } else {
            $tag.css({'opacity': '0.3', 'text-decoration': 'line-through'});
        }
    });
};

$.fn.zato.scheduler.job_detail._bind_panel_toggles = function($body) {
    var detail = $.fn.zato.scheduler.job_detail;
    var cfg = detail.config.detail_panel;

    $body.find('tr[data-run]').not('.detail-panel-row').off('click.panel').on('click.panel', function() {
        var $data_row = $(this);
        var run = $data_row.attr('data-run');
        var $panel = $body.find('tr.detail-panel-row[data-run="' + run + '"]');
        if ($panel.length) {
            var is_expanding = !$panel.hasClass('expanded');
            $panel.toggleClass('expanded');

            if (is_expanding) {
                var record = $data_row.data('record');
                var mirror_html = detail._render_mirror_row(record);
                $panel.find('.detail-panel-log').prepend(mirror_html);
                $panel.data('enabled-levels', detail._build_enabled_levels());
                $data_row.css('display', 'none');
                $panel.css('box-shadow', cfg.shadow);
            } else {
                $panel.find('.detail-log-mirror').remove();
                $data_row.css('display', '');
                $panel.css('box-shadow', '');
            }
            detail._update_table_dim($body);
        }
    });

    // .. level filter toggle (delegated)
    $body.off('click.levelfilter').on('click.levelfilter', '.detail-log-mirror .detail-tag', function(e) {
        e.stopPropagation();
        var $tag = $(this);
        var key = $tag.attr('data-key');
        var $panel = $tag.closest('tr.detail-panel-row');
        var levels = $panel.data('enabled-levels');
        levels[key] = !levels[key];
        detail._apply_level_filter($panel);
    });

    // .. close button (delegated)
    $body.off('click.closeaction').on('click.closeaction', '.detail-action-close', function(e) {
        e.stopPropagation();
        var $panel = $(this).closest('tr.detail-panel-row');
        var run = $panel.attr('data-run');
        var $data_row = $body.find('tr[data-run="' + run + '"]').not('.detail-panel-row');
        $panel.removeClass('expanded');
        $panel.find('.detail-log-mirror').remove();
        $data_row.css('display', '');
        $panel.css('box-shadow', '');
        detail._update_table_dim($body);
    });

    // .. copy-all badge on mirror row (delegated)
    $body.off('click.copyall').on('click.copyall', '.detail-action-copy-all', function(e) {
        e.stopPropagation();
        var kit = $.fn.zato.dashboard_kit;
        var $badge = $(this);
        var $panel = $badge.closest('tr.detail-panel-row');
        var $log = $panel.find('.detail-panel-log');
        var run = $panel.attr('data-run');
        var $data_row = $body.find('tr[data-run="' + run + '"]').not('.detail-panel-row');
        var record = $data_row.data('record');
        var dashboard = detail._dashboard();
        var levels = $panel.data('enabled-levels');

        var actual_time = kit.format_local_time(record.actual_fire_time_iso);
        var duration = dashboard.format_duration(record.duration_ms);
        var delay = (record.delay_ms !== null && record.delay_ms !== undefined && record.delay_ms > 0)
            ? kit.format_number_full(record.delay_ms) + ' ms' : '-';
        var outcome_text = record.outcome ? record.outcome.toUpperCase() : '-';

        var lines = [];
        lines.push('Run #' + record.current_run + ' - ' + outcome_text + ' - ' + actual_time + ' - ' + duration + ' - delay ' + delay);
        lines.push('---');

        $log.find('.detail-log-line').not('.detail-log-mirror').each(function() {
            var $line = $(this);
            var level = $line.find('.detail-log-level').text().trim();
            if (levels[level.toLowerCase()]) {
                var ts = $line.find('.detail-log-ts').text().trim();
                var $msg_clone = $line.find('.detail-log-msg').clone();
                $msg_clone.find('.dashboard-panel-action-badge').remove();
                lines.push(ts + '  ' + level + '  ' + $msg_clone.text().trim());
            }
        });

        kit.copy_to_clipboard($badge[0], lines.join('\n'));
    });

    // .. per-row copy badge (delegated)
    $body.off('click.copyrow').on('click.copyrow', '.detail-action-copy-row', function(e) {
        e.stopPropagation();
        var kit = $.fn.zato.dashboard_kit;
        var $badge = $(this);
        var $line = $badge.closest('.detail-log-line');
        var ts = $line.find('.detail-log-ts').text().trim();
        var level = $line.find('.detail-log-level').text().trim();
        var $msg_clone = $line.find('.detail-log-msg').clone();
        $msg_clone.find('.dashboard-panel-action-badge').remove();
        kit.copy_to_clipboard($badge[0], ts + '  ' + level + '  ' + $msg_clone.text().trim());
    });

    // .. click log line to expand/collapse (delegated)
    $body.off('click.expandline').on('click.expandline', '.detail-log-line:not(.detail-log-mirror)', function(e) {
        if ($(e.target).closest('.dashboard-panel-action-badge').length) return;
        $(this).toggleClass('detail-log-line-expanded');
    });
};

$.fn.zato.scheduler.job_detail._execution_outcomes = {'ok': true, 'error': true, 'timeout': true};

$.fn.zato.scheduler.job_detail._apply_recency_gradient = function($body) {
    var kit = $.fn.zato.dashboard_kit;
    var detail = $.fn.zato.scheduler.job_detail;
    var rgb = detail._dashboard().theme.row_recency_color;
    var max_a = kit.recency.MAX_ALPHA;
    var steps = kit.recency.STEPS;
    var limit = Math.min(detail._new_row_count, steps);
    var primaries = $body.children('tr').not('.detail-run-extras').not('.dashboard-inline-empty').not('.detail-panel-row');
    primaries.each(function(idx) {
        var $row = $(this);
        if (idx < limit) {
            var alpha = max_a * Math.pow(1 - idx / steps, 2.5);
            $row.css('background', 'rgba(' + rgb + ', ' + alpha.toFixed(4) + ')');
        } else {
            $row.css('background', '');
        }
    });
};

$.fn.zato.scheduler.job_detail._new_row_count = 0;

$.fn.zato.scheduler.job_detail.render_history_table = function() {
    var kit = $.fn.zato.dashboard_kit;
    var detail = $.fn.zato.scheduler.job_detail;
    var poll_config = detail._poll_config;

    detail._pagination = kit.pagination.init({
        poll_url: poll_config.poll_url,
        object_type: poll_config.object_type,
        object_id: detail._object_id,
        page_size: 50,
        exclude_outcomes: 'skipped_already_in_flight,missed_catchup',
        ts_field: 'actual_fire_time_iso',
        on_new_rows: function(rows) {
            if (!detail._chart_history) {
                detail._chart_history = [];
            }
            for (var i = 0; i < rows.length; i++) {
                var rec = rows[i];
                var found = false;
                for (var j = detail._chart_history.length - 1; j >= 0; j--) {
                    if (detail._chart_history[j].current_run === rec.current_run) {
                        detail._chart_history[j] = rec;
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    detail._chart_history.push(rec);
                }
            }
            detail.render_timeline(detail._chart_history);
        },
        table_body: '#detail-history-table-body',
        container_top: '#detail-history-pagination-top',
        container_bottom: '#detail-history-pagination-bottom',
        render_page: function($body, rows) {
            $body.empty();
            detail._new_row_count = 0;
            if (!rows || rows.length === 0) {
                $body.html('<tr><td colspan="6" class="dashboard-inline-empty">' + detail.config.empty_history_text + '</td></tr>');
                return;
            }
            for (var i = 0; i < rows.length; i++) {
                var rec = rows[i];
                $body.append(detail._render_single_row(rec, ''));
                var $appended = $body.find('tr[data-run="' + rec.current_run + '"]').not('.detail-panel-row');
                $appended.data('record', rec);
                if (rec.current_run !== null && rec.current_run !== undefined) {
                    $body.append(detail._render_panel_row(rec.current_run));
                }
            }
            detail._bind_panel_toggles($body);
        },
        render_new: function($body, rows, page_size) {
            var exec_outcomes = detail._execution_outcomes;
            var cfg = detail.config.detail_panel;

            $body.find('.dashboard-inline-empty').closest('tr').remove();

            for (var i = rows.length - 1; i >= 0; i--) {
                var rec = rows[i];
                var run = rec.current_run;
                var $existing = $body.find('tr[data-run="' + run + '"]').not('.detail-panel-row');
                if ($existing.length) {
                    var was_running = $existing.find('.badge-running-spinner').length > 0;
                    var is_hidden = $existing.css('display') === 'none';
                    var $panel = $existing.next('.detail-panel-row');
                    var new_html = detail._render_single_row(rec, '');
                    $existing.replaceWith(new_html);
                    var $new_data_row = $body.find('tr[data-run="' + run + '"]').not('.detail-panel-row');
                    $new_data_row.data('record', rec);

                    if (was_running && rec.outcome !== 'running') {
                        $new_data_row.find('.dashboard-outcome-badge').addClass('badge-puff')
                            .one('animationend', function() { $(this).removeClass('badge-puff'); });
                    }

                    // .. re-insert detached panel after the replaced row
                    if ($panel.length) {
                        $new_data_row.after($panel);
                        if ($panel.hasClass('expanded')) {
                            // .. row was hidden, keep it hidden and rebuild the mirror
                            $new_data_row.css('display', 'none');
                            $panel.find('.detail-log-mirror').replaceWith(detail._render_mirror_row(rec));
                            $panel.css('box-shadow', cfg.shadow);
                        }
                    }
                } else {
                    var row_html = detail._render_single_row(rec, '');
                    var panel_html = (run !== null && run !== undefined) ? detail._render_panel_row(run) : '';
                    $body.prepend(panel_html);
                    $body.prepend(row_html);
                    $body.find('tr[data-run="' + run + '"]').not('.detail-panel-row').data('record', rec);
                    detail._new_row_count++;
                }
            }

            // .. trim: count only data rows, remove panel together with its data row
            var data_rows = $body.children('tr').not('.dashboard-inline-empty').not('.detail-panel-row');
            while (data_rows.length > page_size) {
                var $last = data_rows.last();
                $last.next('.detail-panel-row').remove();
                $last.remove();
                data_rows = $body.children('tr').not('.dashboard-inline-empty').not('.detail-panel-row');
            }

            detail._bind_panel_toggles($body);
            detail._apply_recency_gradient($body);
        },
        on_page_change: function(page) {
            kit.url_state.set({page: page > 1 ? page : null});
        }
    });

};

// ////////////////////////////////////////////////////////////////////////////
// Render actions
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_actions = function(job_id) {
    $('#btn-execute-now').on('click', function() {
        var svg_action = document.querySelector('.stat-card-label-svg-action');
        var tooltip_anchor = svg_action ? svg_action : this;
        var cluster_id = $.fn.zato.scheduler.job_detail.config.cluster_id;
        var url = '/zato/scheduler/execute/' + job_id + '/cluster/' + cluster_id + '/';

        $.ajax({
            url: url,
            type: 'POST',
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function() {
                var _tooltip = tippy(tooltip_anchor, {
                    content: 'OK, job executed',
                    allowHTML: false,
                    theme: 'dark',
                    trigger: 'manual',
                    placement: 'right',
                    arrow: true,
                    interactive: false,
                    inertia: true,
                });
                var instance = Array.isArray(_tooltip) ? _tooltip[0] : _tooltip;
                if (instance) {
                    instance.show();
                    setTimeout(function() {
                        instance.hide();
                        setTimeout(function() { instance.destroy(); }, 300);
                    }, 1200);
                }
            },
            error: function(xhr) {
                $.fn.zato.user_message(false, xhr.responseText);
            }
        });
    });
};

// ////////////////////////////////////////////////////////////////////////////
// Tab switching (with URL state)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail._ensure_runs_rendered = function() {
    var detail = $.fn.zato.scheduler.job_detail;
    if (detail._runs_rendered) return;
    detail._runs_rendered = true;
    detail.render_history_table();

    var poll_config = detail._poll_config;
    $.ajax({
        url: poll_config.poll_url,
        type: 'POST',
        data: {
            object_type: poll_config.object_type,
            id: detail._object_id,
            page: 1,
            page_size: 10000
        },
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            if (typeof data === 'string') {
                try { data = JSON.parse(data); } catch(e) { return; }
            }
            detail._chart_history = data.rows;
            detail.render_timeline(detail._chart_history);
        }
    });
};

$.fn.zato.scheduler.job_detail.init_tabs = function() {
    var kit = $.fn.zato.dashboard_kit;
    var detail = $.fn.zato.scheduler.job_detail;

    var url_tab = kit.url_state.get('tab');
    if (url_tab) {
        var $target = $('.dashboard-tab[data-tab="' + url_tab + '"]');
        if ($target.length) {
            $('.dashboard-tab').removeClass('dashboard-tab-active').attr('aria-selected', 'false');
            $target.addClass('dashboard-tab-active').attr('aria-selected', 'true');
            $('.dashboard-tab-panel').attr('hidden', true);
            $('#dashboard-tab-panel-' + url_tab).removeAttr('hidden');
        }
    }

    var active_tab = url_tab ? url_tab : detail.config.default_tab;
    if (active_tab === 'executions') {
        setTimeout(function() { detail._ensure_runs_rendered(); }, 50);
    }

    $('.dashboard-tab').on('click', function() {
        var tab_name = $(this).data('tab');
        $('.dashboard-tab').removeClass('dashboard-tab-active').attr('aria-selected', 'false');
        $(this).addClass('dashboard-tab-active').attr('aria-selected', 'true');
        $('.dashboard-tab-panel').attr('hidden', true);
        $('#dashboard-tab-panel-' + tab_name).removeAttr('hidden');
        kit.url_state.set({tab: tab_name});
        if (tab_name === 'executions') {
            detail._ensure_runs_rendered();
        }
    });
};

// ////////////////////////////////////////////////////////////////////////////
// Poll - incremental new rows via pagination handle + metadata via dashboard
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.poll = function() {
    var detail = $.fn.zato.scheduler.job_detail;
    var job_id = detail._object_id;
    var job_name = detail._job_data.name;

    if (detail._pagination) {
        detail._pagination.poll_new();
    }

    $.ajax({
        url: '/zato/scheduler/dashboard/poll/',
        type: 'POST',
        data: {},
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            if (typeof data === 'string') {
                try { data = JSON.parse(data); } catch(e) { return; }
            }
            var jobs = data.jobs;
            for (var i = 0; i < jobs.length; i++) {
                var entry = jobs[i];
                if (entry.id === job_id || entry.name === job_name) {
                    detail._job_data.next_fire_utc = entry.next_fire_utc;
                    detail._job_data.is_running = entry.is_running;
                    detail._job_data.current_run = entry.current_run;
                    detail._job_data.interval_ms = entry.interval_ms;
                    detail._job_data.recent_outcomes = entry.recent_outcomes;
                    detail._job_data.last_outcome = entry.last_outcome;
                    detail._job_data.last_duration_ms = entry.last_duration_ms;
                    break;
                }
            }
            detail.render_stats(detail._job_data);
        },
        error: function() {}
    });
};

// ////////////////////////////////////////////////////////////////////////////
// Redraw timeline + history (called when time range changes)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail._redraw = function() {
    var detail = $.fn.zato.scheduler.job_detail;
    detail.render_stats(detail._job_data);
    if (detail._pagination) {
        detail._pagination.fetch_page(1);
    }
    if (detail._chart_history) {
        detail.render_timeline(detail._chart_history);
    }
};

// ////////////////////////////////////////////////////////////////////////////
// Main render
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render = function(job, job_id, cluster_id) {
    var kit = $.fn.zato.dashboard_kit;
    var detail = $.fn.zato.scheduler.job_detail;

    detail.render_header(job);
    detail._build_legend();
    detail.render_stats(job);
    detail.render_config(job, cluster_id);
    detail.render_actions(job_id);
    detail.init_tabs();

    var range_names = {
        5: 'Last 5m', 15: 'Last 15m', 30: 'Last 30m', 60: 'Last 1h',
        360: 'Last 6h', 1440: 'Today', 2880: 'Yesterday',
        10080: 'This week', 43200: 'This month', 525600: 'This year', 0: 'All'
    };

    var url_range = kit.url_state.get('range');
    var initial_range = url_range !== null ? parseInt(url_range, 10) : null;

    kit.time_range.init({
        pill: '#detail-timeline-range-pill',
        menu: '#detail-timeline-range-menu',
        storage_key: 'zato_job_detail_time_range',
        on_change: function(minutes) {
            detail._time_range_minutes = minutes;
            $('#detail-timeline-range-pill').text(range_names[minutes]);
            kit.url_state.set({range: minutes, page: null});
            detail._redraw();
        }
    });

    if (initial_range !== null && !isNaN(initial_range)) {
        detail._time_range_minutes = initial_range;
        if (range_names[initial_range]) {
            $('#detail-timeline-range-pill').text(range_names[initial_range]);
        }
        kit.storage_set('zato_job_detail_time_range', initial_range);
        var $menu = $('#detail-timeline-range-menu');
        $menu.find('.dashboard-time-range-option').removeClass('dashboard-time-range-active');
        $menu.find('.dashboard-time-range-option[data-minutes="' + initial_range + '"]').addClass('dashboard-time-range-active');
    } else {
        var stored = parseInt(kit.storage_get('zato_job_detail_time_range'), 10);
        if (isNaN(stored)) stored = detail.config.default_time_range;
        detail._time_range_minutes = stored;
        if (stored && range_names[stored]) {
            $('#detail-timeline-range-pill').text(range_names[stored]);
        }
    }

    detail._auto_refresh = kit.auto_refresh.init({
        pill: '#detail-refresh-pill',
        menu: '#detail-refresh-menu',
        storage_key: 'zato_detail_refresh_' + detail._object_id,
        url_param: 'refresh',
        default_seconds: 5,
        on_tick: detail.poll
    });

    kit.url_state.on_pop(function(params) {
        var range_val = parseInt(params.get('range'), 10);
        if (isNaN(range_val)) range_val = detail.config.default_time_range;
        detail._time_range_minutes = range_val;
        $('#detail-timeline-range-pill').text(range_names[range_val]);
        var $m = $('#detail-timeline-range-menu');
        $m.find('.dashboard-time-range-option').removeClass('dashboard-time-range-active');
        $m.find('.dashboard-time-range-option[data-minutes="' + range_val + '"]').addClass('dashboard-time-range-active');
        detail._redraw();

        var refresh_val = parseInt(params.get('refresh'), 10);
        if (!isNaN(refresh_val) && detail._auto_refresh) {
            detail._auto_refresh.set_seconds(refresh_val);
        }
    });

};

// ////////////////////////////////////////////////////////////////////////////
// Init
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.init = function(job_data, job_id, cluster_id, poll_config) {
    if (typeof job_data === 'string') {
        try { job_data = JSON.parse(job_data); } catch(parse_error) { job_data = {}; }
    }
    $.fn.zato.scheduler.job_detail._job_data = job_data;
    $.fn.zato.scheduler.job_detail._object_id = Number(job_id);
    $.fn.zato.scheduler.job_detail._poll_config = poll_config;
    $.fn.zato.scheduler.job_detail.render(job_data, job_id, cluster_id);
};
