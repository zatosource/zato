
/* Dashboard kit - generic record detail page.
   Renders a single execution record with its log entries in a
   dark-themed panel. Everything is configurable via the config object
   passed to init() - nothing is hardcoded to any specific domain. */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.record_detail = {};

    var _cfg = null;
    var _poll_timer = null;

    /* Render a single log entry line.
       entry: {level, timestamp_iso, message}
       is_last: if true, omit the bottom border. */
    kit.record_detail.render_log_entry = function(entry, is_last) {
        var panel = _cfg.panel;
        var level_key = entry.level.toUpperCase();
        if (level_key === 'WARNING') level_key = 'WARN';
        if (level_key === 'CRITICAL') level_key = 'ERROR';
        var lc = panel.level_colors[level_key];
        var border_style = is_last ? '' : 'border-bottom:1px solid ' + panel.row_border + ';';

        var escaped_msg = entry.message.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        var highlighted_msg = kit.syntax_highlight(entry.message);
        var html = '<div class="detail-log-line" style="' + border_style + '">';
        html += '<div class="detail-log-stripe" style="background:' + lc.stripe + '"></div>';
        html += '<div class="detail-log-ts" style="color:' + panel.ts_color + '">' + kit.format_local_time(entry.timestamp_iso) + '</div>';
        html += '<div class="detail-log-level-col"><span class="detail-log-level" style="color:' + lc.badge_fg + ';background:' + lc.badge_bg + '">' + entry.level + '</span></div>';
        html += '<div class="detail-log-msg" data-raw="' + escaped_msg + '" style="color:' + panel.msg_color + '">' + highlighted_msg + '</div>';
        html += '<div class="detail-log-actions"><span class="dashboard-panel-action-badge detail-action-copy-row" style="color:#aaa;background:rgba(255,255,255,0.08)">Copy</span></div>';
        html += '</div>';
        return html;
    };

    /* Render the mirror row - a summary line at the top of the log panel
       showing run number, outcome badge, and tag badges.
       record: execution record object
       Requires config.render_mirror(record) to return the HTML. */
    kit.record_detail.render_mirror = function(record) {
        return _cfg.render_mirror(record);
    };

    /* Render tag badges for the dark panel.
       record: execution record with log_summary
       tag_defs: array of {key, label, dark_color, dark_bg, dimmed} */
    kit.record_detail.render_dark_tags = function(record, tag_defs) {
        var tags = record.log_summary;
        var html = '';
        for (var t = 0; t < tag_defs.length; t++) {
            var def = tag_defs[t];
            var count = tags[def.key];
            if (count > 0) {
                var style = 'color:' + def.dark_color + ';background:' + def.dark_bg;
                if (def.dimmed) style += ';opacity:0.75';
                html += '<span class="detail-tag" data-key="' + def.key + '" style="' + style + '">' +
                    def.label + ' x' + count + '</span>';
            }
        }
        return html;
    };

    /* Build the initial enabled-levels map from tag_defs. */
    kit.record_detail.build_enabled_levels = function(tag_defs) {
        var levels = {};
        for (var t = 0; t < tag_defs.length; t++) {
            levels[tag_defs[t].key] = true;
        }
        return levels;
    };

    /* Apply level filtering on a container. */
    kit.record_detail.apply_level_filter = function($container, levels, tag_defs) {
        $container.find('.detail-log-line').not('.detail-log-mirror').each(function() {
            var $line = $(this);
            var level_text = $line.find('.detail-log-level').text().trim().toLowerCase();
            $line.css('opacity', levels[level_text] ? '' : '0.15');
        });

        $container.find('.detail-log-mirror .detail-tag').each(function() {
            var $tag = $(this);
            var key = $tag.attr('data-key');
            if (levels[key]) {
                var base_opacity = '';
                for (var t = 0; t < tag_defs.length; t++) {
                    if (tag_defs[t].key === key && tag_defs[t].dimmed) {
                        base_opacity = '0.75';
                        break;
                    }
                }
                $tag.css('opacity', base_opacity);
            } else {
                $tag.css('opacity', '0.15');
            }
        });
    };

    /* Fetch and append log entries into the panel container.
       $panel_log: jQuery element for the log container
       params: {object_id, run_id, since_idx} */
    kit.record_detail._fetch_logs = function($panel_log, params) {
        var body = {
            action: _cfg.log_action,
            since_idx: params.since_idx,
            cluster_id: _cfg.cluster_id
        };
        body[_cfg.object_id_field || 'object_id'] = params.object_id;
        body[_cfg.run_id_field || 'run_id'] = params.run_id;
        $.ajax({
            type: 'POST',
            url: _cfg.poll_url,
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            data: JSON.stringify(body),
            contentType: 'application/json',
            error: function(xhr, status, err) {
                console.error('Log fetch error: status=' + xhr.status + ' err=' + err);
            },
            success: function(data) {
                var entries = data.entries;
                if (entries.length === 0) return;
                for (var idx = 0; idx < entries.length; idx++) {
                    var entry_html = kit.record_detail.render_log_entry(entries[idx], false);
                    var $entry = $(entry_html).addClass('kit-fade-in');
                    $panel_log.append($entry);
                    $entry.one('animationend', function() { $(this).removeClass('kit-fade-in'); });
                }
                $panel_log.children('.detail-log-line').last().css('border-bottom', '');
                $panel_log.attr('data-since-idx', params.since_idx + entries.length);
            }
        });
    };

    /* Fetch the execution record (history) for a specific run.
       The service returns paginated results, so we request a large
       enough window to find the target run. */
    kit.record_detail._fetch_record = function(callback) {
        $.ajax({
            type: 'POST',
            url: _cfg.poll_url,
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            data: JSON.stringify({
                action: _cfg.history_action,
                id: _cfg.record_id,
                cluster_id: _cfg.cluster_id
            }),
            contentType: 'application/json',
            error: function(xhr, status, err) {
                console.error('Record fetch error: status=' + xhr.status + ' err=' + err);
            },
            success: function(data) {
                callback(data);
            }
        });
    };

    /* Initialise the record detail page.
       config: {
           cluster_id, record_id, run_number, record_name,
           poll_url, history_action, log_action,
           object_id_field, run_id_field,
           panel: {bg, border, row_border, mirror_accent, owner_color,
                   font_size, ts_color, msg_color,
                   level_colors: {ERROR: {stripe, badge_bg, badge_fg}, ...},
                   outcome_colors: {ok: {color, bg}, ...}},
           tag_defs: [{key, label, dark_color, dark_bg, dimmed}, ...],
           render_mirror: function(record) -> html,
           find_record: function(data, run_number) -> record or null
       } */
    kit.record_detail.init = function(config) {
        _cfg = config;

        var $container = $('#record-detail-log');

        kit.record_detail._fetch_record(function(data) {
            var record = _cfg.find_record(data, _cfg.run_number);
            if (!record) {
                $container.html('<div style="padding:16px;color:#aaa">No data for this run.</div>');
                return;
            }

            var $panel_log = $container.find('.detail-panel-log');

            // .. render the mirror row (summary header)
            var mirror_html = kit.record_detail.render_mirror(record);
            $panel_log.prepend(mirror_html);

            // .. set up level filtering
            var enabled_levels = kit.record_detail.build_enabled_levels(_cfg.tag_defs);
            $container.data('enabled-levels', enabled_levels);

            // .. tag click toggles level filter
            $container.on('click', '.detail-tag', function() {
                var key = $(this).attr('data-key');
                enabled_levels[key] = !enabled_levels[key];
                kit.record_detail.apply_level_filter($container, enabled_levels, _cfg.tag_defs);
            });

            // .. "Toggle all" action
            $container.on('click', '.detail-action-toggle-all', function() {
                var any_off = false;
                for (var key in enabled_levels) {
                    if (!enabled_levels[key]) { any_off = true; break; }
                }
                var new_val = any_off;
                for (var key2 in enabled_levels) {
                    enabled_levels[key2] = new_val;
                }
                kit.record_detail.apply_level_filter($container, enabled_levels, _cfg.tag_defs);
            });

            // .. "Copy" for single row
            $container.on('click', '.detail-action-copy-row', function(e) {
                e.stopPropagation();
                var $line = $(this).closest('.detail-log-line');
                var raw = $line.find('.detail-log-msg').attr('data-raw');
                if (raw && navigator.clipboard) {
                    navigator.clipboard.writeText(raw);
                }
            });

            // .. "Copy all" action
            $container.on('click', '.detail-action-copy-all', function(e) {
                e.stopPropagation();
                var lines = [];
                $container.find('.detail-log-line').not('.detail-log-mirror').each(function() {
                    var raw = $(this).find('.detail-log-msg').attr('data-raw');
                    if (raw) lines.push(raw);
                });
                if (lines.length && navigator.clipboard) {
                    navigator.clipboard.writeText(lines.join('\n'));
                }
            });

            // .. log line expand/collapse on click
            $container.on('click', '.detail-log-line', function(e) {
                if ($(e.target).closest('.detail-tag, .dashboard-panel-action-badge, .dashboard-outcome-badge, .detail-log-actions').length) return;
                $(this).toggleClass('detail-log-line-expanded');
            });

            // .. initial log fetch
            var fetch_params = {
                object_id: _cfg.record_id,
                run_id: _cfg.run_number,
                since_idx: 0
            };
            kit.record_detail._fetch_logs($panel_log, fetch_params);

            // .. periodic polling for new entries
            if (_cfg.poll_interval_ms > 0) {
                _poll_timer = setInterval(function() {
                    var since_idx = parseInt($panel_log.attr('data-since-idx'), 10);
                    kit.record_detail._fetch_logs($panel_log, {
                        object_id: _cfg.record_id,
                        run_id: _cfg.run_number,
                        since_idx: since_idx
                    });
                }, _cfg.poll_interval_ms);
            }
        });
    };
})();
