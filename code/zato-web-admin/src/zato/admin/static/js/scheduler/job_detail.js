
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
    var dashboard = $.fn.zato.scheduler.job_detail._dashboard();
    var type_label = dashboard.job_type_labels[job.job_type] || job.job_type;
    var status_text = job.is_active ? 'Active' : 'Paused';
    var title = '<a href="/zato/scheduler/dashboard/?cluster=1" class="detail-component-pill" style="background:#1a6fa0;color:#e0f0ff">Scheduler</a> ' +
        (job.name || 'Unknown job') +
        ' <span style="font-weight:400;font-size:13px;color:var(--text-muted)">' +
        type_label + ' \u00b7 ' + status_text + '</span>';
    $('#detail-section-title').html(title);
};

// ////////////////////////////////////////////////////////////////////////////
// Render stats into the stat cards
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_stats = function(job, history) {
    var kit = $.fn.zato.dashboard_kit;
    var dashboard = $.fn.zato.scheduler.job_detail._dashboard();
    var filtered = $.fn.zato.scheduler.job_detail._filter_by_range(history);

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

$.fn.zato.scheduler.job_detail.render_config = function(job, cluster_id) {
    var container = $('#detail-config-grid');
    var kit = $.fn.zato.dashboard_kit;
    var dashboard = $.fn.zato.scheduler.job_detail._dashboard();
    var html = '';

    var config_service = job.service || job.service_name || '';
    html += '<div><strong>Service</strong><br>';
    html += '<a href="/zato/service/overview/' + encodeURIComponent(config_service) + '/?cluster=' + cluster_id + '">' + (config_service || '-') + '</a></div>';

    html += '<div><strong>Job type</strong><br>' + (job.job_type || '-') + '</div>';
    html += '<div><strong>Start date</strong><br>' + (job.start_date || '-') + '</div>';
    html += '<div><strong>Status</strong><br>' + (job.is_active ? 'Active' : 'Paused') + '</div>';

    if (job.job_type === 'interval_based') {
        var parts = [];
        if (job.weeks) parts.push(kit.format_number_full(job.weeks) + ' weeks');
        if (job.days) parts.push(kit.format_number_full(job.days) + ' days');
        if (job.hours) parts.push(kit.format_number_full(job.hours) + ' hours');
        if (job.minutes) parts.push(kit.format_number_full(job.minutes) + ' minutes');
        if (job.seconds) parts.push(kit.format_number_full(job.seconds) + ' seconds');
        html += '<div><strong>Interval</strong><br>' + (parts.join(', ') || '-') + '</div>';
    }

    if (job.repeats !== null && job.repeats !== undefined) {
        html += '<div><strong>Repeats</strong><br>' + (job.repeats === 0 ? 'Unlimited' : kit.format_number_full(job.repeats)) + '</div>';
    }

    if (job.max_execution_time_ms) {
        html += '<div><strong>Max execution time</strong><br>' + dashboard.format_duration(job.max_execution_time_ms) + '</div>';
    }

    if (job.jitter_ms) {
        html += '<div><strong>Jitter</strong><br>' + kit.format_number_full(job.jitter_ms) + ' ms</div>';
    }

    if (job.extra) {
        var extra_display = job.extra;
        try {
            var parsed = JSON.parse(job.extra);
            extra_display = JSON.stringify(parsed, null, 2);
        } catch(e) {}
        html += '<div style="grid-column:1/-1"><strong>Extra data</strong>';
        html += '<pre class="detail-config-extra">' + extra_display + '</pre></div>';
    }

    container.html(html);
};

// ////////////////////////////////////////////////////////////////////////////
// Render timeline (with SVG glow filter and interactive tooltip)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_timeline = function(history) {
    var container = $('#detail-timeline');
    var filtered = $.fn.zato.scheduler.job_detail._filter_by_range(history);

    if (!filtered || filtered.length === 0) {
        container.html('<div style="color:var(--text-muted);font-size:13px;padding:8px 0">No execution history in this range</div>');
        return;
    }

    var kit = $.fn.zato.dashboard_kit;
    var dashboard = $.fn.zato.scheduler.job_detail._dashboard();
    var bar_colors = dashboard.outcome_bar_colors;

    var chart_width = container.width() || 700;
    var chart_height = 60;
    var padding_left = 8;
    var padding_right = 8;
    var padding_top = 8;
    var row_height = 16;

    var timestamps = [];
    for (var record_index = 0; record_index < filtered.length; record_index++) {
        var record = filtered[record_index];
        var time_string = record.actual_fire_time_iso || record.planned_fire_time_iso;
        if (time_string) {
            timestamps.push(new Date(time_string).getTime());
        }
    }

    if (timestamps.length === 0) {
        container.html('<div style="color:var(--text-muted);font-size:13px;padding:8px 0">No execution history in this range</div>');
        return;
    }

    var min_time = Math.min.apply(null, timestamps);
    var max_time = Math.max.apply(null, timestamps);
    var time_range = max_time - min_time;

    if (time_range === 0) {
        time_range = 3600000;
        min_time = max_time - time_range;
    }

    var draw_width = chart_width - padding_left - padding_right;

    var svg = '<svg width="' + chart_width + '" height="' + chart_height + '" xmlns="http://www.w3.org/2000/svg">';

    svg += '<defs>';
    svg += '<filter id="timelineGlow">';
    svg += '<feGaussianBlur stdDeviation="2" result="blur"/>';
    svg += '<feMerge>';
    svg += '<feMergeNode in="blur"/>';
    svg += '<feMergeNode in="SourceGraphic"/>';
    svg += '</feMerge>';
    svg += '</filter>';
    svg += '</defs>';

    svg += '<line x1="' + padding_left + '" y1="' + (padding_top + row_height / 2) + '" ';
    svg += 'x2="' + (chart_width - padding_right) + '" y2="' + (padding_top + row_height / 2) + '" ';
    svg += 'stroke="rgba(0,0,0,0.06)" stroke-width="2" />';

    for (var entry_index = 0; entry_index < filtered.length; entry_index++) {
        var entry = filtered[entry_index];
        var entry_time_string = entry.actual_fire_time_iso || entry.planned_fire_time_iso;
        if (!entry_time_string) continue;

        var entry_time = new Date(entry_time_string).getTime();
        var entry_x = padding_left + ((entry_time - min_time) / time_range) * draw_width;
        var entry_color = bar_colors[entry.outcome] || '#ccc';
        var entry_duration = parseInt(entry.duration_ms || 0, 10);
        var bar_length = Math.max(4, (entry_duration / time_range) * draw_width);
        bar_length = Math.min(bar_length, draw_width - (entry_x - padding_left));

        var esc = function(s) { return String(s || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;'); };

        svg += '<rect x="' + entry_x.toFixed(1) + '" y="' + padding_top + '" ';
        svg += 'width="' + bar_length.toFixed(1) + '" height="' + row_height + '" ';
        svg += 'fill="' + entry_color + '" opacity="0.85" rx="3" filter="url(#timelineGlow)" ';
        svg += 'data-time="' + esc(entry_time_string) + '" ';
        svg += 'data-outcome="' + esc(entry.outcome) + '" ';
        svg += 'data-duration="' + esc(entry.duration_ms) + '" ';
        svg += 'data-latency="' + esc(entry.dispatch_latency_ms) + '" ';
        svg += 'data-run="' + esc(entry.current_run) + '" ';
        svg += 'data-error="' + esc(entry.error) + '" ';
        svg += 'style="cursor:pointer" />';
    }

    svg += '</svg>';
    container.html(svg);

    container.off('mousemove.timeline mouseleave.timeline');
    container.on('mousemove.timeline', function(event) {
        var target = event.target;
        if (target.tagName !== 'rect' || !$(target).attr('data-outcome')) {
            kit.tooltip.hide();
            return;
        }
        var $r = $(target);
        var outcome_key = $r.attr('data-outcome');
        var outcome_label = dashboard.outcome_labels[outcome_key] || outcome_key;
        var outcome_color = bar_colors[outcome_key] || '#ccc';
        var time_str = $r.attr('data-time');
        var run_num = $r.attr('data-run');
        var duration_val = $r.attr('data-duration');
        var latency_val = $r.attr('data-latency');
        var error_val = $r.attr('data-error');

        var time_display = kit.format_local_time(time_str);
        var run_display = (run_num && run_num !== 'null' && run_num !== 'undefined')
            ? '#' + kit.format_number_full(parseInt(run_num, 10))
            : '';

        var tt_html = '<div class="dashboard-tooltip-header">' +
            '<div class="dashboard-tooltip-title">' + time_display + '</div>';
        if (run_display) {
            tt_html += '<div class="dashboard-tooltip-subtitle">Run ' + run_display + '</div>';
        }
        tt_html += '</div>';
        tt_html += '<span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:' +
            outcome_color + ';margin-right:5px;vertical-align:middle"></span>' + outcome_label;

        if (duration_val && duration_val !== 'null' && duration_val !== 'undefined') {
            tt_html += '<br>Duration: ' + dashboard.format_duration(parseInt(duration_val, 10));
        }
        if (latency_val && latency_val !== 'null' && latency_val !== 'undefined') {
            tt_html += '<br>Latency: ' + kit.format_number_full(parseInt(latency_val, 10)) + ' ms';
        }
        if (error_val && error_val.length > 0 && error_val !== 'null' && error_val !== 'undefined') {
            var short_err = error_val.length > 60 ? error_val.substring(0, 60) + '...' : error_val;
            tt_html += '<br><span style="color:#ff6b6b">Error: ' + short_err + '</span>';
        }

        kit.tooltip.show(event, tt_html);
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
    var dashboard = $.fn.zato.scheduler.job_detail._dashboard();
    var filtered = $.fn.zato.scheduler.job_detail._filter_by_range(history);

    if (!filtered || filtered.length === 0) {
        $('#detail-history-table-body').html(
            '<tr><td colspan="7" style="color:var(--text-muted);padding:16px 12px">No execution history</td></tr>'
        );
        $('#detail-history-count').text('');
        $('#detail-history-pagination-top').empty();
        $('#detail-history-pagination-bottom').empty();
        return;
    }

    var sorted = filtered.slice().sort(function(first, second) {
        return (second.actual_fire_time_iso || '').localeCompare(first.actual_fire_time_iso || '');
    });

    var groups = $.fn.zato.scheduler.job_detail._group_by_run(sorted);
    $('#detail-history-count').text(kit.format_number_full(filtered.length) + ' runs');

    var mono_style = 'font-family:monospace;font-feature-settings:\'tnum\' on;white-space:nowrap';
    var mono_wrap = 'font-family:monospace;font-feature-settings:\'tnum\' on';
    var center_style = 'text-align:center';

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
        row += '<td style="' + mono_style + '">' + planned_time + '</td>';
        row += '<td style="' + mono_style + '">' + actual_time + '</td>';
        row += '<td style="' + mono_wrap + ';' + center_style + '">' + dispatch_latency + '</td>';
        row += '<td style="' + mono_wrap + ';' + center_style + '">' + duration + '</td>';
        row += '<td style="' + center_style + '">' + outcome + '</td>';
        row += '<td style="' + mono_wrap + '">' + run_number + '</td>';
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
                    placement: 'left',
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

$.fn.zato.scheduler.job_detail.init_tabs = function() {
    var kit = $.fn.zato.dashboard_kit;

    var url_tab = kit.url_state.get('tab');
    if (url_tab) {
        var $target = $('.detail-tab[data-tab="' + url_tab + '"]');
        if ($target.length) {
            $('.detail-tab').removeClass('detail-tab-active').attr('aria-selected', 'false');
            $target.addClass('detail-tab-active').attr('aria-selected', 'true');
            $('.detail-tab-panel').attr('hidden', true);
            $('#detail-tab-panel-' + url_tab).removeAttr('hidden');
        }
    }

    $('.detail-tab').on('click', function() {
        var tab_name = $(this).data('tab');
        $('.detail-tab').removeClass('detail-tab-active').attr('aria-selected', 'false');
        $(this).addClass('detail-tab-active').attr('aria-selected', 'true');
        $('.detail-tab-panel').attr('hidden', true);
        $('#detail-tab-panel-' + tab_name).removeAttr('hidden');
        kit.url_state.set({tab: tab_name});
    });
};

// ////////////////////////////////////////////////////////////////////////////
// Redraw timeline + history (called when time range changes)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail._redraw = function() {
    var detail = $.fn.zato.scheduler.job_detail;
    detail.render_stats(detail._job_data, detail._history_data);
    detail.render_timeline(detail._history_data);
    detail.render_history_table(detail._history_data);
};

// ////////////////////////////////////////////////////////////////////////////
// Main render
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render = function(job, history, job_id, cluster_id) {
    var kit = $.fn.zato.dashboard_kit;
    var detail = $.fn.zato.scheduler.job_detail;

    detail.render_header(job);
    detail.render_stats(job, history);
    detail.render_config(job, cluster_id);
    detail.render_timeline(history);
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

    setTimeout(function() {
        detail.render_history_table(history);
    }, 50);
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
    $.fn.zato.scheduler.job_detail.render(job_data, history_data, job_id, cluster_id);
};
