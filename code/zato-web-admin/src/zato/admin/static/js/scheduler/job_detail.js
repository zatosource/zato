
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.scheduler === 'undefined') { $.fn.zato.scheduler = {}; }
$.fn.zato.scheduler.job_detail = {};

$.fn.zato.scheduler.job_detail._dashboard = function() {
    return $.fn.zato.scheduler.dashboard;
};

$.fn.zato.scheduler.job_detail._time_range_minutes = 0;
$.fn.zato.scheduler.job_detail._history_data = [];
$.fn.zato.scheduler.job_detail._job_data = {};
$.fn.zato.scheduler.job_detail._pagination = null;
$.fn.zato.scheduler.job_detail._runs_rendered = false;
$.fn.zato.scheduler.job_detail._object_id = '';

$.fn.zato.scheduler.job_detail._hidden_series_key = function() {
    return 'zato_hidden_series_' + ($.fn.zato.scheduler.job_detail._object_id || 'unknown');
};

$.fn.zato.scheduler.job_detail._get_hidden_series = function() {
    return $.fn.zato.dashboard_kit.storage_get_json(
        $.fn.zato.scheduler.job_detail._hidden_series_key()
    ) || {};
};

$.fn.zato.scheduler.job_detail._set_hidden_series = function(hidden) {
    $.fn.zato.dashboard_kit.storage_set_json(
        $.fn.zato.scheduler.job_detail._hidden_series_key(), hidden
    );
};

// ////////////////////////////////////////////////////////////////////////////
// Outcome priority for grouping (higher = more significant)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail._outcome_priority = {
    'error': 5,
    'timeout': 4,
    'ok': 3,
    'missed_catchup': 2,
    'skipped_already_in_flight': 1,
    'skipped_holiday': 0
};

// ////////////////////////////////////////////////////////////////////////////
// Filter history by time range
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail._filter_by_range = function(history) {
    var minutes = $.fn.zato.scheduler.job_detail._time_range_minutes;
    if (!minutes || minutes <= 0 || !history) return history;
    var cutoff = Date.now() - (minutes * 60 * 1000);
    var filtered = [];
    for (var i = 0; i < history.length; i++) {
        var ts = history[i].actual_fire_time_iso || history[i].planned_fire_time_iso;
        if (ts && new Date(ts).getTime() >= cutoff) {
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
        var outcome = history[i].outcome || 'ok';
        if (!hidden[outcome]) out.push(history[i]);
    }
    return out;
};

// ////////////////////////////////////////////////////////////////////////////
// Group history by run number with collapsible extras
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail._group_by_run = function(sorted) {
    var priority = $.fn.zato.scheduler.job_detail._outcome_priority;
    var groups = [];
    var run_map = {};

    for (var i = 0; i < sorted.length; i++) {
        var r = sorted[i];
        var run_key = (r.current_run !== null && r.current_run !== undefined) ? r.current_run : ('_' + i);

        if (run_map.hasOwnProperty(run_key)) {
            var group = run_map[run_key];
            var r_prio = priority[r.outcome] || 0;
            var p_prio = priority[group.primary.outcome] || 0;
            if (r_prio > p_prio) {
                group.extras.push(group.primary);
                group.primary = r;
            } else {
                group.extras.push(r);
            }
        } else {
            var new_group = {run: run_key, primary: r, extras: []};
            run_map[run_key] = new_group;
            groups.push(new_group);
        }
    }
    return groups;
};

// ////////////////////////////////////////////////////////////////////////////
// Render section title
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_header = function(job) {
    var title = '<a href="/zato/scheduler/dashboard/?cluster=1" class="detail-component-pill menu-link">Scheduler</a> ' +
        (job.name || 'Unknown job');
    $('#detail-section-title').html(title);
};

// ////////////////////////////////////////////////////////////////////////////
// Render stats into the stat cards
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_stats = function(job, history) {
    var kit = $.fn.zato.dashboard_kit;
    var detail = $.fn.zato.scheduler.job_detail;
    var dashboard = detail._dashboard();
    var filtered = detail._filter_by_outcome(detail._filter_by_range(history));

    var total_runs = filtered.length;
    var error_count = 0;
    var total_duration = 0;
    var duration_count = 0;

    for (var record_index = 0; record_index < filtered.length; record_index++) {
        var record = filtered[record_index];
        if (record.outcome === 'error') error_count++;
        if (record.duration_ms !== null && record.duration_ms !== undefined) {
            total_duration += parseInt(record.duration_ms, 10) || 0;
            duration_count++;
        }
    }

    var average_duration = duration_count > 0 ? Math.round(total_duration / duration_count) : null;

    $('#stat-total-runs').text(kit.format_number_full(total_runs));
    var $errors = $('#stat-errors');
    $errors.text(kit.format_number_full(error_count));
    if (error_count > 0) {
        $errors.css('color', '#e0226e');
    } else {
        $errors.css('color', '');
    }

    $('#stat-avg-duration').text(dashboard.format_duration(average_duration));

    var next_fire = job.next_fire_time_iso || job.next_run_time;
    if (next_fire) {
        $('#stat-next-fire').text(dashboard.format_local_time(next_fire));
    } else {
        $('#stat-next-fire').text('-');
    }
};

// ////////////////////////////////////////////////////////////////////////////
// Render config grid
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail._highlight_extra = function(raw) {
    var esc = function(s) { return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); };

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

    var esc = function(s) { return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); };

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

    var config_service = job.service || job.service_name || '';
    var service_link = config_service
        ? '<a href="/zato/service/overview/' + encodeURIComponent(config_service) + '/?cluster=' + cluster_id + '">' + esc(config_service) + '</a>'
        : '-';
    html += card('Service', service_link, true);

    var type_label = dashboard.job_type_labels[job.job_type] || job.job_type || '-';
    html += card('Job type', type_label, false);

    var start_display = job.start_date ? kit.format_local_time(job.start_date) : '-';
    html += card('Start date', start_display, false);

    var status_html = job.is_active
        ? '<span style="color:#1b855e;font-weight:700">Active</span>'
        : '<span style="color:var(--text-muted);font-weight:700">Paused</span>';
    html += card('Status', status_html, true);

    if (job.job_type === 'interval_based') {
        var parts = [];
        var _iv = function(v) { return parseInt(v, 10) || 0; };
        if (_iv(job.weeks)) parts.push(kit.format_number_full(_iv(job.weeks)) + (_iv(job.weeks) === 1 ? ' week' : ' weeks'));
        if (_iv(job.days)) parts.push(kit.format_number_full(_iv(job.days)) + (_iv(job.days) === 1 ? ' day' : ' days'));
        if (_iv(job.hours)) parts.push(kit.format_number_full(_iv(job.hours)) + (_iv(job.hours) === 1 ? ' hour' : ' hours'));
        if (_iv(job.minutes)) parts.push(kit.format_number_full(_iv(job.minutes)) + (_iv(job.minutes) === 1 ? ' minute' : ' minutes'));
        if (_iv(job.seconds)) parts.push(kit.format_number_full(_iv(job.seconds)) + (_iv(job.seconds) === 1 ? ' second' : ' seconds'));
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

    var job_name = job.name || '';
    var manage_url = '/zato/scheduler/?cluster=' + cluster_id + '&query=' + encodeURIComponent(job_name);
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
        container.html('<div class="dashboard-inline-empty">No run history in this range</div>');
        return;
    }

    var chart_width = container.width() || 700;
    var chart_height = 28;
    var pad_top = 1;
    var pad_bot = 1;
    var draw_h = chart_height - pad_top - pad_bot;

    var timestamps = [];
    for (var i = 0; i < filtered.length; i++) {
        var ts = filtered[i].actual_fire_time_iso || filtered[i].planned_fire_time_iso;
        if (ts) timestamps.push(new Date(ts).getTime());
    }

    if (timestamps.length === 0) {
        container.html('<div class="dashboard-inline-empty">No run history in this range</div>');
        return;
    }

    var min_time = Math.min.apply(null, timestamps);
    var max_time = Math.max.apply(null, timestamps);
    var time_span = max_time - min_time;
    if (time_span === 0) {
        time_span = 3600000;
        min_time = max_time - time_span;
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
        var row_ts = filtered[r].actual_fire_time_iso || filtered[r].planned_fire_time_iso;
        if (!row_ts) continue;
        var row_t = new Date(row_ts).getTime();
        var bi = Math.min(bucket_count - 1, Math.max(0, Math.floor((row_t - min_time) / bucket_ms)));
        var outcome = filtered[r].outcome || 'ok';
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
            stack_sum += (buckets[ms][visible_keys[sv]] || 0);
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

    var svg = '<svg width="' + chart_width + '" height="' + chart_height + '" xmlns="http://www.w3.org/2000/svg">';

    for (var li = 0; li < visible_keys.length; li++) {
        var okey = visible_keys[li];
        var color = bar_colors[okey] || '#ccc';

        var has_any = false;
        for (var chk = 0; chk < bucket_count; chk++) {
            if (buckets[chk][okey] > 0) { has_any = true; break; }
        }
        if (!has_any) continue;

        var top_pts = [];
        var bot_pts = [];

        for (var si = 0; si < bucket_count; si++) {
            var x = si * seg_w + seg_w / 2;
            var val = buckets[si][okey] || 0;
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

        svg += '<path d="' + area + '" fill="' + color + '" opacity="0.75" />';

        for (var si2 = 0; si2 < bucket_count; si2++) {
            cumulative[si2] += (buckets[si2][okey] || 0);
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
            var ov = bkt[ok2] || 0;
            if (ov === 0) continue;
            var pct = Math.round((ov / bkt.total) * 100);
            tt += '<div class="dashboard-tooltip-row">' +
                '<span class="dashboard-tooltip-dot" style="background:' + (bar_colors[ok2] || '#ccc') + '"></span>' +
                (outcome_labels[ok2] || ok2) + ': ' + kit.format_number_full(ov) +
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
// Render history table (grouped, paginated)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_history_table = function(history) {
    var kit = $.fn.zato.dashboard_kit;
    var detail = $.fn.zato.scheduler.job_detail;
    var dashboard = detail._dashboard();
    var filtered = detail._filter_by_outcome(detail._filter_by_range(history));

    if (!filtered || filtered.length === 0) {
        $('#detail-history-table-body').html(
            '<tr><td colspan="7" class="dashboard-inline-empty">No run history</td></tr>'
        );
        $('#detail-history-pagination-top').empty();
        $('#detail-history-pagination-bottom').empty();
        return;
    }

    var sorted = filtered.slice().sort(function(first, second) {
        return (second.actual_fire_time_iso || '').localeCompare(first.actual_fire_time_iso || '');
    });

    var groups = detail._group_by_run(sorted);

    var render_single_row = function(record, extra_class) {
        var planned_time = kit.format_local_time(record.planned_fire_time_iso);
        var actual_time = kit.format_local_time(record.actual_fire_time_iso);
        var dispatch_latency = (record.dispatch_latency_ms !== null && record.dispatch_latency_ms !== undefined)
            ? kit.format_number_full(record.dispatch_latency_ms) + ' ms'
            : '-';
        var duration = dashboard.format_duration(record.duration_ms);
        var outcome = dashboard.outcome_badge(record.outcome);
        var run_number = (record.current_run !== null && record.current_run !== undefined)
            ? kit.format_number_full(record.current_run) : '-';
        var error_text = record.error || '';
        var error_short = error_text.length > 80 ? error_text.substring(0, 80) + '...' : error_text;

        var cls = extra_class ? ' class="' + extra_class + '"' : '';
        var row = '<tr' + cls + '>';
        row += '<td class="dashboard-cell-mono">' + planned_time + '</td>';
        row += '<td class="dashboard-cell-mono">' + actual_time + '</td>';
        row += '<td class="dashboard-cell-mono-wrap dashboard-cell-center">' + dispatch_latency + '</td>';
        row += '<td class="dashboard-cell-mono-wrap dashboard-cell-center">' + duration + '</td>';
        row += '<td class="dashboard-cell-center">' + outcome + '</td>';
        row += '<td class="dashboard-cell-mono-wrap">' + run_number + '</td>';
        row += '<td title="' + error_text.replace(/"/g, '&quot;') + '">' + error_short + '</td>';
        row += '</tr>';
        return row;
    };

    var render_group = function(group) {
        var html = '';
        var primary_row = render_single_row(group.primary, '');

        if (group.extras.length > 0) {
            var toggle_id = 'extras-' + group.run;
            var label = '+ ' + group.extras.length + ' skipped';
            primary_row = primary_row.replace('</td></tr>',
                ' <span class="detail-run-extras-toggle" data-target=".' + toggle_id + '">' +
                label + '</span></td></tr>');
            html += primary_row;
            for (var e = 0; e < group.extras.length; e++) {
                html += render_single_row(group.extras[e], 'detail-run-extras ' + toggle_id).replace('<tr', '<tr style="display:none"');
            }
        } else {
            html += primary_row;
        }
        return html;
    };

    var initial_page = parseInt(kit.url_state.get('page', '1'), 10) || 1;

    $.fn.zato.scheduler.job_detail._pagination = kit.pagination.init({
        data: groups,
        page_size: 50,
        initial_page: initial_page,
        table_body: '#detail-history-table-body',
        container_top: '#detail-history-pagination-top',
        container_bottom: '#detail-history-pagination-bottom',
        render_row: function(group) {
            return render_group(group);
        },
        on_page_change: function(page) {
            kit.url_state.set({page: page > 1 ? page : null});
        }
    });

    $(document).off('click.run-extras').on('click.run-extras', '.detail-run-extras-toggle', function() {
        var target_class = $(this).data('target');
        var $rows = $(target_class);
        var visible = $rows.first().is(':visible');
        if (visible) {
            $rows.hide();
            $(this).text('+ ' + $rows.length + ' skipped');
        } else {
            $rows.show();
            $(this).text('\u2212 ' + $rows.length + ' skipped');
        }
    });
};

// ////////////////////////////////////////////////////////////////////////////
// Render actions
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_actions = function(job_id) {
    $('#btn-execute-now').on('click', function() {
        var btn = this;
        var cluster_id = $(document).getUrlParam('cluster') || '1';
        var url = '/zato/scheduler/execute/' + job_id + '/cluster/' + cluster_id + '/';

        $.ajax({
            url: url,
            type: 'POST',
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function() {
                var _tooltip = tippy(btn, {
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
                $.fn.zato.user_message(false, xhr.responseText || 'Error executing job');
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
    detail.render_timeline(detail._history_data);
    detail.render_history_table(detail._history_data);
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

    var active_tab = url_tab || 'executions';
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
// Redraw timeline + history (called when time range changes)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail._redraw = function() {
    var detail = $.fn.zato.scheduler.job_detail;
    detail.render_stats(detail._job_data, detail._history_data);
    detail._runs_rendered = false;
    var $panel = $('#dashboard-tab-panel-executions');
    if ($panel.length && !$panel.prop('hidden')) {
        detail._ensure_runs_rendered();
    }
};

// ////////////////////////////////////////////////////////////////////////////
// Main render
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render = function(job, history, job_id, cluster_id) {
    var kit = $.fn.zato.dashboard_kit;
    var detail = $.fn.zato.scheduler.job_detail;

    detail.render_header(job);
    detail._build_legend();
    detail.render_stats(job, history);
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
            $('#detail-timeline-range-pill').text(range_names[minutes] || 'All');
            kit.url_state.set({range: minutes || null, page: null});
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
        var stored = parseInt(kit.storage_get('zato_job_detail_time_range') || '0', 10) || 0;
        detail._time_range_minutes = stored;
        if (stored && range_names[stored]) {
            $('#detail-timeline-range-pill').text(range_names[stored]);
        }
    }

};

// ////////////////////////////////////////////////////////////////////////////
// Init
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.init = function(job_data, history_data, job_id, cluster_id) {
    if (typeof job_data === 'string') {
        try { job_data = JSON.parse(job_data); } catch(parse_error) { job_data = {}; }
    }
    if (typeof history_data === 'string') {
        try { history_data = JSON.parse(history_data); } catch(parse_error) { history_data = []; }
    }
    $.fn.zato.scheduler.job_detail._job_data = job_data;
    $.fn.zato.scheduler.job_detail._history_data = history_data;
    $.fn.zato.scheduler.job_detail._object_id = job_id || '';
    $.fn.zato.scheduler.job_detail.render(job_data, history_data, job_id, cluster_id);
};
