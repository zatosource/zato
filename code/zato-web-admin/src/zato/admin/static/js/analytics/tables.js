
// Traffic analytics tables - the grid section of each screen. The overview
// ranks channels and consumers, the per-channel screen breaks one channel
// down by consumer and error source, the per-consumer screen lists the
// channels one credential calls.

// /////////////////////////////////////////////////////////////////////////////

(function() {

    var dash = $.fn.zato.analytics.dashboard;

    // What each error source is called on the per-channel screen
    dash.error_source_labels = {
        auth: 'Authentication',
        rate_limit: 'Rate limit',
        upstream: 'Upstream',
        gateway: 'Gateway'
    };

    // The display order of the error sources
    dash.error_source_order = ['auth', 'rate_limit', 'upstream', 'gateway'];

    // ////////////////////////////////////////////////////////////////////////

    // The name of the anonymous consumer bucket, matching the backend's display name
    dash.caller_anonymous = 'Anonymous';

    // ////////////////////////////////////////////////////////////////////////

    // Turns an hourly period like 2026-07-16T14 into its display form.
    dash.format_period = function(period) {
        if (period === '') {
            return dash.config.empty_period_text;
        }

        var display = period.replace('T', ' ') + ':00 UTC';
        return display;
    };

    // ////////////////////////////////////////////////////////////////////////

    // The address of one channel's analytics screen.
    dash.channel_href = function(name) {
        var href = dash.config.channel_page;
        href += '?cluster=' + dash.config.cluster_id;
        href += '&name=' + encodeURIComponent(name);
        href += '&range=' + encodeURIComponent(dash.config.time_range);

        return href;
    };

    // The address of one consumer's analytics screen.
    dash.consumer_href = function(name) {
        var href = dash.config.consumer_page;
        href += '?cluster=' + dash.config.cluster_id;
        href += '&name=' + encodeURIComponent(name);
        href += '&range=' + encodeURIComponent(dash.config.time_range);

        return href;
    };

    // The address of the audit log pre-filtered to one channel and, when the
    // caller is a real credential, to that caller too.
    dash.audit_href = function(row) {
        var href = dash.config.audit_log_page;
        href += '?cluster=' + dash.config.cluster_id;
        href += '&source=' + encodeURIComponent(row.source);
        href += '&object_name=' + encodeURIComponent(row.name);

        // The anonymous bucket has no credential to search for
        if (dash.config.name !== dash.caller_anonymous) {
            href += '&query=' + encodeURIComponent(dash.config.name);
        }

        return href;
    };

    // ////////////////////////////////////////////////////////////////////////

    // One cell holding a link to another screen.
    dash._link_cell = function(text, href) {
        var cell = document.createElement('td');
        var link = document.createElement('a');

        link.textContent = text;
        link.href = href;

        cell.appendChild(link);

        return cell;
    };

    // One cell holding plain text.
    dash._text_cell = function(text) {
        var cell = document.createElement('td');
        cell.textContent = text;

        return cell;
    };

    // One cell holding a sparkline holder - the sparkline itself is rendered
    // by the caller once the row is in the document.
    dash._spark_seq = 0;

    dash._spark_cell = function(points) {
        var cell = document.createElement('td');

        dash._spark_seq += 1;
        var spark_id = 'analytics-row-spark-' + dash._spark_seq;

        var holder = document.createElement('div');
        holder.id = spark_id;
        holder.className = 'dashboard-tile-spark';

        cell.appendChild(holder);

        return {cell: cell, spark_id: spark_id, points: points};
    };

    // ////////////////////////////////////////////////////////////////////////

    // One "nothing to show" row spanning the whole table.
    dash._no_data_row = function(column_count) {
        var row = document.createElement('tr');
        var cell = document.createElement('td');

        cell.colSpan = column_count;
        cell.className = 'dashboard-no-data';
        cell.textContent = dash.config.no_data_text;

        row.appendChild(cell);

        return row;
    };

    // ////////////////////////////////////////////////////////////////////////

    // Fills one entity table - the shared shape of every ranking and breakdown table.
    // Per row: name link, trend sparkline, requests, error rate, p95, and one extra
    // column the caller describes.
    dash._render_entity_table = function(body_selector, count_selector, rows, name_href, extra_cell) {
        var kit = $.fn.zato.dashboard_kit;

        var body = document.querySelector(body_selector);
        body.textContent = '';

        $(count_selector).text(rows.length);

        // Five shared columns plus however many the caller adds
        var column_count = 5 + extra_cell.length;

        if (rows.length === 0) {
            var no_data_row = dash._no_data_row(column_count);
            body.appendChild(no_data_row);
            return;
        }

        var diag_start = performance.now();
        var diag_spark_points = 0;

        // Build every row into a fragment first, so the document is touched once ..
        var fragment = document.createDocumentFragment();
        var sparks = [];

        for (var rowIdx = 0; rowIdx < rows.length; rowIdx++) {
            var rowData = rows[rowIdx];
            var row = document.createElement('tr');

            // Build each cell on its own ..
            var href = name_href(rowData.name);
            var name_cell = dash._link_cell(rowData.name, href);

            var spark = dash._spark_cell(rowData.spark);
            sparks.push(spark);

            var request_count_display = kit.format_number_full(rowData.request_count);
            var request_count_cell = dash._text_cell(request_count_display);

            var error_rate_cell = dash._text_cell(rowData.error_rate + '%');

            var p95_display = kit.format_duration_ms(rowData.p95_ms);
            var p95_cell = dash._text_cell(p95_display);

            // .. put the row together ..
            row.appendChild(name_cell);
            row.appendChild(spark.cell);
            row.appendChild(request_count_cell);
            row.appendChild(error_rate_cell);
            row.appendChild(p95_cell);

            for (var extraIdx = 0; extraIdx < extra_cell.length; extraIdx++) {
                var extra = extra_cell[extraIdx](rowData);
                row.appendChild(extra);
            }

            fragment.appendChild(row);
        }

        body.appendChild(fragment);

        var diag_rows_done = performance.now();

        // .. measure the sparkline column once - every row shares it, and measuring
        // per row would force the browser to re-layout the whole table each time ..
        var spark_width = document.getElementById(sparks[0].spark_id).clientWidth;

        if (spark_width < 20) {
            spark_width = 240;
        }

        // .. and draw the sparklines with that explicit width, so drawing them
        // never asks the document about layout again.
        for (var sparkIdx = 0; sparkIdx < sparks.length; sparkIdx++) {
            var entry = sparks[sparkIdx];

            kit.sparkline.render('#' + entry.spark_id, entry.points, {color: dash.theme.spark_color, width: spark_width});
            diag_spark_points += entry.points ? entry.points.length : 0;
        }

        console.log('[Analytics-Diag] table ' + body_selector + ': rows=' + rows.length +
            ' spark_points=' + diag_spark_points +
            ' rows_dom=' + (diag_rows_done - diag_start).toFixed(1) + 'ms' +
            ' sparklines=' + (performance.now() - diag_rows_done).toFixed(1) + 'ms' +
            ' total=' + (performance.now() - diag_start).toFixed(1) + 'ms');
    };

    // ////////////////////////////////////////////////////////////////////////

    // One extra cell holding the row's consumer count.
    dash._related_count_cell = function(rowData) {
        var cell = dash._text_cell(rowData.related_count);
        return cell;
    };

    // One extra cell holding the row's last-seen hour.
    dash._last_seen_cell = function(rowData) {
        var last_seen_display = dash.format_period(rowData.last_seen);
        var cell = dash._text_cell(last_seen_display);
        return cell;
    };

    // One extra cell holding the row's drill-down into the audit log.
    dash._audit_link_cell = function(rowData) {
        var href = dash.audit_href(rowData);
        var cell = dash._link_cell('Open', href);
        return cell;
    };

    // ////////////////////////////////////////////////////////////////////////

    dash._render_overview_tables = function(data) {

        // The busiest channels, each linking to its own screen, with its consumer count
        dash._render_entity_table(
            '#analytics-channels-table-body',
            '#analytics-channels-count',
            data.top_channels,
            dash.channel_href,
            [dash._related_count_cell]
        );

        // The busiest consumers, each linking to its own screen, with its last-seen hour
        dash._render_entity_table(
            '#analytics-consumers-table-body',
            '#analytics-consumers-count',
            data.top_consumers,
            dash.consumer_href,
            [dash._last_seen_cell]
        );
    };

    // ////////////////////////////////////////////////////////////////////////

    // The error-source split - the why behind the error count
    dash._render_error_sources = function(data) {
        var kit = $.fn.zato.dashboard_kit;
        var body = document.querySelector('#analytics-error-sources-table-body');
        body.textContent = '';

        for (var orderIdx = 0; orderIdx < dash.error_source_order.length; orderIdx++) {
            var source_key = dash.error_source_order[orderIdx];

            var label_cell = dash._text_cell(dash.error_source_labels[source_key]);

            var count_display = kit.format_number_full(data.error_sources[source_key]);
            var count_cell = dash._text_cell(count_display);

            var row = document.createElement('tr');
            row.appendChild(label_cell);
            row.appendChild(count_cell);

            body.appendChild(row);
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    dash._render_channel_tables = function(data) {

        // The consumers behind this channel's numbers
        dash._render_entity_table(
            '#analytics-consumers-table-body',
            '#analytics-consumers-count',
            data.rows,
            dash.consumer_href,
            [dash._last_seen_cell]
        );

        dash._render_error_sources(data);
    };

    // ////////////////////////////////////////////////////////////////////////

    dash._render_consumer_tables = function(data) {

        // The channels this credential calls, each with a drill-down into the audit log
        dash._render_entity_table(
            '#analytics-channels-table-body',
            '#analytics-channels-count',
            data.rows,
            dash.channel_href,
            [dash._last_seen_cell, dash._audit_link_cell]
        );

        dash._render_error_sources(data);
    };

    // ////////////////////////////////////////////////////////////////////////

    dash.render_tables = function(data) {
        if (dash.config.screen === 'overview') {
            dash._render_overview_tables(data);
        }
        else if (dash.config.screen === 'channel') {
            dash._render_channel_tables(data);
        }
        else {
            dash._render_consumer_tables(data);
        }
    };

})();
