
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.scheduler === 'undefined') { $.fn.zato.scheduler = {}; }
$.fn.zato.scheduler.job_detail = {};

$.fn.zato.scheduler.job_detail._dashboard = function() {
    return $.fn.zato.scheduler.dashboard;
};

// ////////////////////////////////////////////////////////////////////////////
// Render header (inside the dark hero strip)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_header = function(job) {
    var dashboard = $.fn.zato.scheduler.job_detail._dashboard();
    var container = $('#dashboard-detail-header');
    var type_label = dashboard.job_type_labels[job.job_type] || job.job_type;
    var status_text = job.is_active ? 'Active' : 'Paused';

    var html = '<div class="dashboard-detail-name">';
    html += dashboard.status_dot(job) + ' ' + (job.name || 'Unknown job');
    html += '</div>';
    html += '<div class="dashboard-detail-meta">';
    html += '<span class="dashboard-detail-badge">' + type_label + '</span>';
    html += '<span class="dashboard-detail-status">' + status_text + '</span>';
    var service_name = job.service || job.service_name || '';
    if (service_name) {
        html += '<span class="dashboard-detail-service">' + service_name + '</span>';
    }
    if (job.in_flight) {
        html += '<span class="dashboard-detail-in-flight">In-flight (run #' + job.current_run + ')</span>';
    }
    html += '</div>';
    container.html(html);
};

// ////////////////////////////////////////////////////////////////////////////
// Render config
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_config = function(job, cluster_id) {
    var container = $('#dashboard-detail-config');
    var dashboard = $.fn.zato.scheduler.job_detail._dashboard();
    var html = '<div class="dashboard-config-grid">';

    var config_service = job.service || job.service_name || '';
    html += '<div class="dashboard-config-item"><span class="dashboard-config-label">Service</span>';
    html += '<a href="/zato/service/overview/' + encodeURIComponent(config_service) + '/?cluster=' + cluster_id + '">' + (config_service || '-') + '</a></div>';

    html += '<div class="dashboard-config-item"><span class="dashboard-config-label">Job type</span>' + (job.job_type || '-') + '</div>';
    html += '<div class="dashboard-config-item"><span class="dashboard-config-label">Start date</span>' + (job.start_date || '-') + '</div>';

    if (job.job_type === 'interval_based') {
        var parts = [];
        if (job.weeks) parts.push(job.weeks + ' weeks');
        if (job.days) parts.push(job.days + ' days');
        if (job.hours) parts.push(job.hours + ' hours');
        if (job.minutes) parts.push(job.minutes + ' minutes');
        if (job.seconds) parts.push(job.seconds + ' seconds');
        html += '<div class="dashboard-config-item"><span class="dashboard-config-label">Interval</span>' + (parts.join(', ') || '-') + '</div>';
    }

    if (job.repeats !== null && job.repeats !== undefined) {
        html += '<div class="dashboard-config-item"><span class="dashboard-config-label">Repeats</span>' + (job.repeats === 0 ? 'Unlimited' : job.repeats) + '</div>';
    }

    if (job.max_execution_time_ms) {
        html += '<div class="dashboard-config-item"><span class="dashboard-config-label">Max execution time</span>' + dashboard.format_duration(job.max_execution_time_ms) + '</div>';
    }

    if (job.jitter_ms) {
        html += '<div class="dashboard-config-item"><span class="dashboard-config-label">Jitter</span>' + job.jitter_ms + ' ms</div>';
    }

    html += '</div>';

    if (job.extra) {
        var extra_display = job.extra;
        try {
            var parsed = JSON.parse(job.extra);
            extra_display = JSON.stringify(parsed, null, 2);
        } catch(e) {}
        html += '<div class="dashboard-config-item dashboard-config-item-wide"><span class="dashboard-config-label">Extra data</span>';
        html += '<pre class="dashboard-config-extra">' + extra_display + '</pre></div>';
    }

    container.html(html);
};

// ////////////////////////////////////////////////////////////////////////////
// Render stats
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_stats = function(history) {
    var container = $('#dashboard-detail-stats');
    var dashboard = $.fn.zato.scheduler.job_detail._dashboard();

    var total_runs = history.length;
    var error_count = 0;
    var timeout_count = 0;
    var total_duration = 0;
    var duration_count = 0;

    for (var record_index = 0; record_index < history.length; record_index++) {
        var record = history[record_index];
        if (record.outcome === 'error') error_count++;
        if (record.outcome === 'timeout') timeout_count++;
        if (record.duration_ms !== null && record.duration_ms !== undefined) {
            total_duration += parseInt(record.duration_ms, 10) || 0;
            duration_count++;
        }
    }

    var average_duration = duration_count > 0 ? Math.round(total_duration / duration_count) : null;

    var html = '<div class="dashboard-stat-row">';
    html += '<div class="dashboard-stat"><div class="dashboard-stat-number">' + total_runs + '</div><div class="dashboard-stat-label">Total runs</div></div>';
    html += '<div class="dashboard-stat"><div class="dashboard-stat-number' + (error_count > 0 ? ' dashboard-stat-danger' : '') + '">' + error_count + '</div><div class="dashboard-stat-label">Errors</div></div>';
    html += '<div class="dashboard-stat"><div class="dashboard-stat-number' + (timeout_count > 0 ? ' dashboard-stat-warning' : '') + '">' + timeout_count + '</div><div class="dashboard-stat-label">Timeouts</div></div>';
    html += '<div class="dashboard-stat"><div class="dashboard-stat-number">' + dashboard.format_duration(average_duration) + '</div><div class="dashboard-stat-label">Avg duration</div></div>';
    html += '</div>';

    container.html(html);
};

// ////////////////////////////////////////////////////////////////////////////
// Render timeline (with SVG glow filter)
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_timeline = function(history) {
    var container = $('#dashboard-timeline');
    if (!history || history.length === 0) {
        container.html('<div class="dashboard-no-data">No execution history yet</div>');
        return;
    }

    var dashboard = $.fn.zato.scheduler.job_detail._dashboard();
    var bar_colors = dashboard.outcome_bar_colors;

    var chart_width = container.width() || 700;
    var chart_height = 60;
    var padding_left = 8;
    var padding_right = 8;
    var padding_top = 8;
    var row_height = 16;

    var timestamps = [];
    for (var record_index = 0; record_index < history.length; record_index++) {
        var record = history[record_index];
        var time_string = record.actual_fire_time_iso || record.planned_fire_time_iso;
        if (time_string) {
            timestamps.push(new Date(time_string).getTime());
        }
    }

    if (timestamps.length === 0) {
        container.html('<div class="dashboard-no-data">No execution history yet</div>');
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

    for (var entry_index = 0; entry_index < history.length; entry_index++) {
        var entry = history[entry_index];
        var entry_time_string = entry.actual_fire_time_iso || entry.planned_fire_time_iso;
        if (!entry_time_string) continue;

        var entry_time = new Date(entry_time_string).getTime();
        var entry_x = padding_left + ((entry_time - min_time) / time_range) * draw_width;
        var entry_color = bar_colors[entry.outcome] || '#ccc';
        var entry_duration = parseInt(entry.duration_ms || 0, 10);
        var bar_length = Math.max(4, (entry_duration / time_range) * draw_width);
        bar_length = Math.min(bar_length, draw_width - (entry_x - padding_left));

        var tooltip = dashboard.format_local_time(entry_time_string) + ' - ' +
                      (dashboard.outcome_labels[entry.outcome] || entry.outcome) + ' - ' +
                      dashboard.format_duration(entry.duration_ms);

        svg += '<rect x="' + entry_x.toFixed(1) + '" y="' + padding_top + '" ';
        svg += 'width="' + bar_length.toFixed(1) + '" height="' + row_height + '" ';
        svg += 'fill="' + entry_color + '" opacity="0.85" rx="3" filter="url(#timelineGlow)">';
        svg += '<title>' + tooltip + '</title>';
        svg += '</rect>';
    }

    svg += '</svg>';
    container.html(svg);
};

// ////////////////////////////////////////////////////////////////////////////
// Render history table
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_history_table = function(history) {
    var table_body = $('#dashboard-history-table-body');
    var dashboard = $.fn.zato.scheduler.job_detail._dashboard();
    table_body.empty();

    if (!history || history.length === 0) {
        table_body.append('<tr><td colspan="7" class="dashboard-no-data">No execution history</td></tr>');
        $('#dashboard-history-count').text('');
        return;
    }

    $('#dashboard-history-count').text(history.length + ' runs');

    var sorted = history.slice().sort(function(first, second) {
        return (second.actual_fire_time_iso || '').localeCompare(first.actual_fire_time_iso || '');
    });

    for (var record_index = 0; record_index < sorted.length; record_index++) {
        var record = sorted[record_index];
        var planned_time = dashboard.format_local_time(record.planned_fire_time_iso);
        var actual_time = dashboard.format_local_time(record.actual_fire_time_iso);
        var dispatch_latency = record.dispatch_latency_ms !== null && record.dispatch_latency_ms !== undefined
            ? record.dispatch_latency_ms + ' ms'
            : '-';
        var duration = dashboard.format_duration(record.duration_ms);
        var outcome = dashboard.outcome_badge(record.outcome);
        var run_number = record.current_run !== null && record.current_run !== undefined ? record.current_run : '-';
        var error_text = record.error || '';
        var error_short = error_text.length > 80 ? error_text.substring(0, 80) + '...' : error_text;

        var row = '<tr>';
        row += '<td style="font-family:monospace;font-feature-settings:\'tnum\' on;color:#6e6e73;white-space:nowrap">' + planned_time + '</td>';
        row += '<td style="font-family:monospace;font-feature-settings:\'tnum\' on;color:#6e6e73;white-space:nowrap">' + actual_time + '</td>';
        row += '<td style="font-family:monospace;font-feature-settings:\'tnum\' on">' + dispatch_latency + '</td>';
        row += '<td style="font-family:monospace;font-feature-settings:\'tnum\' on">' + duration + '</td>';
        row += '<td>' + outcome + '</td>';
        row += '<td style="font-family:monospace;font-feature-settings:\'tnum\' on">' + run_number + '</td>';
        row += '<td class="dashboard-error-cell" title="' + error_text.replace(/"/g, '&quot;') + '">' + error_short + '</td>';
        row += '</tr>';
        table_body.append(row);
    }
};

// ////////////////////////////////////////////////////////////////////////////
// Render actions
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render_actions = function(job_id, cluster_id) {
    var container = $('#dashboard-detail-actions');
    var html = '';
    html += '<a class="dashboard-action-link" href="/zato/scheduler/dashboard/?cluster=' + cluster_id + '">Back to dashboard</a>';
    html += '<a class="dashboard-action-link dashboard-action-execute" href="javascript:$.fn.zato.scheduler.dashboard.execute_job(\'' + job_id + '\')">Execute now</a>';
    container.html(html);
};

// ////////////////////////////////////////////////////////////////////////////
// Main render
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.job_detail.render = function(job, history, job_id, cluster_id) {
    $.fn.zato.scheduler.job_detail.render_header(job);
    $.fn.zato.scheduler.job_detail.render_config(job, cluster_id);
    $.fn.zato.scheduler.job_detail.render_stats(history);
    $.fn.zato.scheduler.job_detail.render_timeline(history);
    $.fn.zato.scheduler.job_detail.render_history_table(history);
    $.fn.zato.scheduler.job_detail.render_actions(job_id, cluster_id);
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
    $.fn.zato.scheduler.job_detail.render(job_data, history_data, job_id, cluster_id);
    $('.dashboard-page').css('opacity', '1');
};
