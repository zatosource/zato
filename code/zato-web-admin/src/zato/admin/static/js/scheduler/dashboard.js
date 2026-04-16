
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.scheduler === 'undefined') { $.fn.zato.scheduler = {}; }
$.fn.zato.scheduler.dashboard = {};

// ////////////////////////////////////////////////////////////////////////////
// Outcome color map
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.outcome_colors = {
    'executed': '#4caf50',
    'error': '#e53935',
    'timeout': '#ff9800',
    'skipped_concurrent': '#78909c',
    'skipped_holiday': '#5c6bc0',
    'missed_catchup': '#ffc107'
};

$.fn.zato.scheduler.dashboard.outcome_labels = {
    'executed': 'Executed',
    'error': 'Error',
    'timeout': 'Timeout',
    'skipped_concurrent': 'Skipped (concurrent)',
    'skipped_holiday': 'Skipped (holiday)',
    'missed_catchup': 'Missed catchup'
};

$.fn.zato.scheduler.dashboard.job_type_labels = {
    'one_time': 'One-time',
    'interval_based': 'Interval-based'
};

// ////////////////////////////////////////////////////////////////////////////
// Sparkline data buffers
// ////////////////////////////////////////////////////////////////////////////

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
        return '<span style="color:#adb5bd">-</span>';
    }
    var colors = $.fn.zato.scheduler.dashboard.outcome_colors;
    var labels = $.fn.zato.scheduler.dashboard.outcome_labels;
    var html = '';
    for (var index = 0; index < recent_outcomes.length; index++) {
        var outcome = recent_outcomes[index];
        var color = colors[outcome] || '#ccc';
        var label = labels[outcome] || outcome;
        html += '<span class="scheduler-outcome-square" style="background:' + color + '" title="' + label + '"></span>';
    }
    return html;
};

// ////////////////////////////////////////////////////////////////////////////
// Outcome badge
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.outcome_badge = function(outcome) {
    var colors = $.fn.zato.scheduler.dashboard.outcome_colors;
    var labels = $.fn.zato.scheduler.dashboard.outcome_labels;
    var color = colors[outcome] || '#ccc';
    var label = labels[outcome] || outcome;
    return '<span class="scheduler-outcome-badge" style="background:' + color + '">' + label + '</span>';
};

// ////////////////////////////////////////////////////////////////////////////
// Bar chart
// ////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.dashboard.render_bar_chart = function(timeline) {
    var container = $('#scheduler-bar-chart');
    if (!timeline || timeline.length === 0) {
        container.html('<div class="scheduler-no-data">No execution history yet</div>');
        $('#scheduler-chart-legend').empty();
        $('#scheduler-exec-count').text('');
        return;
    }

    var chart_width = container.width() || 800;
    var chart_height = 180;
    var padding_left = 40;
    var padding_bottom = 28;
    var padding_top = 8;
    var padding_right = 8;

    var outcome_keys = ['executed', 'error', 'timeout', 'skipped_concurrent', 'skipped_holiday', 'missed_catchup'];
    var colors = $.fn.zato.scheduler.dashboard.outcome_colors;
    var labels = $.fn.zato.scheduler.dashboard.outcome_labels;

    var timestamps = [];
    for (var record_index = 0; record_index < timeline.length; record_index++) {
        var timestamp_string = timeline[record_index].actual_fire_time_iso;
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

    $('#scheduler-exec-count').text(timeline.length + ' runs');

    var min_time = Math.min.apply(null, timestamps);
    var max_time = Math.max.apply(null, timestamps);
    var time_range = max_time - min_time;

    if (time_range === 0) {
        time_range = 3600000;
        min_time = max_time - time_range;
    }

    var bucket_count = Math.min(40, Math.max(8, Math.floor(chart_width / 22)));
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

    for (var timeline_index = 0; timeline_index < timeline.length; timeline_index++) {
        var record = timeline[timeline_index];
        var time = new Date(record.actual_fire_time_iso).getTime();
        var outcome = record.outcome || 'executed';
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

    var max_bucket_total = 0;
    for (var total_index = 0; total_index < buckets.length; total_index++) {
        var total = 0;
        for (var total_key_index = 0; total_key_index < outcome_keys.length; total_key_index++) {
            total += buckets[total_index][outcome_keys[total_key_index]];
        }
        if (total > max_bucket_total) {
            max_bucket_total = total;
        }
    }
    if (max_bucket_total === 0) {
        max_bucket_total = 1;
    }

    var draw_width = chart_width - padding_left - padding_right;
    var draw_height = chart_height - padding_top - padding_bottom;
    var bar_width = Math.max(4, (draw_width / bucket_count) - 3);

    var svg = '<svg width="' + chart_width + '" height="' + chart_height + '" xmlns="http://www.w3.org/2000/svg">';

    svg += '<line x1="' + padding_left + '" y1="' + (chart_height - padding_bottom) + '" ';
    svg += 'x2="' + (chart_width - padding_right) + '" y2="' + (chart_height - padding_bottom) + '" ';
    svg += 'stroke="#e9ecef" stroke-width="1" />';

    for (var bar_index = 0; bar_index < buckets.length; bar_index++) {
        var bar_x = padding_left + (bar_index / bucket_count) * draw_width + 1.5;
        var bar_y_offset = 0;

        var bucket_start_label = $.fn.zato.scheduler.dashboard.format_local_time(new Date(buckets[bar_index].start).toISOString());

        for (var stack_index = 0; stack_index < outcome_keys.length; stack_index++) {
            var outcome_key = outcome_keys[stack_index];
            var count = buckets[bar_index][outcome_key];
            if (count === 0) {
                continue;
            }

            var segment_height = (count / max_bucket_total) * draw_height;
            var segment_y = chart_height - padding_bottom - bar_y_offset - segment_height;

            svg += '<rect x="' + bar_x.toFixed(1) + '" y="' + segment_y.toFixed(1) + '" ';
            svg += 'width="' + bar_width.toFixed(1) + '" height="' + segment_height.toFixed(1) + '" ';
            svg += 'fill="' + colors[outcome_key] + '" rx="3">';
            svg += '<title>' + bucket_start_label + ' - ' + (labels[outcome_key] || outcome_key) + ': ' + count + '</title>';
            svg += '</rect>';

            bar_y_offset += segment_height;
        }
    }

    var label_count = Math.min(6, bucket_count);
    var label_step = Math.max(1, Math.floor(bucket_count / label_count));
    for (var label_index = 0; label_index < bucket_count; label_index += label_step) {
        var label_x = padding_left + (label_index / bucket_count) * draw_width;
        var label_date = new Date(buckets[label_index].start);
        var label_text = ('0' + label_date.getHours()).slice(-2) + ':' + ('0' + label_date.getMinutes()).slice(-2);
        svg += '<text x="' + label_x.toFixed(1) + '" y="' + (chart_height - 6) + '" ';
        svg += 'font-size="11" fill="#adb5bd" font-family="Menlo, Consolas, Monaco, monospace">' + label_text + '</text>';
    }

    svg += '</svg>';
    container.html(svg);

    var legend_html = '';
    for (var legend_index = 0; legend_index < outcome_keys.length; legend_index++) {
        var legend_key = outcome_keys[legend_index];
        legend_html += '<span class="scheduler-legend-item">';
        legend_html += '<span class="scheduler-legend-dot" style="background:' + colors[legend_key] + '"></span>';
        legend_html += labels[legend_key];
        legend_html += '</span>';
    }
    $('#scheduler-chart-legend').html(legend_html);
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
        row += '<td style="font-family:monospace;color:#6c757d" title="' + next_fire_tooltip + '">' + next_fire_text + '</td>';
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

    if (!timeline || timeline.length === 0) {
        container.html('<div class="scheduler-all-clear"><svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="7" stroke="#4caf50" stroke-width="1.5"/><path d="M5 8l2 2 4-4" stroke="#4caf50" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>All clear</div>');
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
        container.html('<div class="scheduler-all-clear"><svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="7" stroke="#4caf50" stroke-width="1.5"/><path d="M5 8l2 2 4-4" stroke="#4caf50" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>All clear</div>');
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
        html += '<td style="font-family:monospace;color:#6c757d;white-space:nowrap" title="' + time_tooltip + '">' + time_text + '</td>';
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
        row += '<td style="font-family:monospace;color:#6c757d;white-space:nowrap" title="' + time_tooltip + '">' + time_text + '</td>';
        row += '<td><a href="/zato/scheduler/dashboard/job/' + encodeURIComponent(entry.job_id) + '/?cluster=' + cluster_id + '">' + entry.name + '</a></td>';
        row += '<td style="color:#6c757d">' + entry.service + '</td>';
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
    var now = new Date();
    var hours = ('0' + now.getHours()).slice(-2);
    var minutes = ('0' + now.getMinutes()).slice(-2);
    var seconds = ('0' + now.getSeconds()).slice(-2);
    $('#scheduler-last-refresh').text(hours + ':' + minutes + ':' + seconds);
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

    var spark_options = {width: 100, height: 28, color: '#82ccff', dot_color: '#fff', dot_radius: 2};
    var spark_options_failures = {width: 100, height: 28, color: '#ff6b6b', dot_color: '#fff', dot_radius: 2};

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
    $.fn.zato.scheduler.dashboard.render(initial_data);
    setInterval($.fn.zato.scheduler.dashboard.poll, 10000);
};
