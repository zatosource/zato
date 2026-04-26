
/* Dashboard kit - generic record detail and log panel component.
   All domain knowledge comes through config objects - nothing is
   hardcoded to any specific domain (scheduler, EDA, etc.). */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.record_detail = {};

    var FADE_MS = 100;

    kit.record_detail.render_log_entry = function(entry, is_last, panel) {
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

    kit.record_detail.render_tags = function(record, tag_defs, variant) {
        var tags = record.log_summary;
        var html = '';
        for (var t = 0; t < tag_defs.length; t++) {
            var def = tag_defs[t];
            var count = tags[def.key];
            if (count > 0) {
                var color = variant === 'dark' ? def.dark_color : def.color;
                var bg = variant === 'dark' ? def.dark_bg : def.bg;
                var style = 'color:' + color + ';background:' + bg;
                if (def.dimmed) style += ';opacity:0.75';
                html += '<span class="detail-tag" data-key="' + def.key + '" style="' + style + '">' +
                    def.label + ' x' + count + '</span>';
            }
        }
        return html;
    };

    kit.record_detail.render_dark_tags = function(record, tag_defs) {
        return kit.record_detail.render_tags(record, tag_defs, 'dark');
    };

    kit.record_detail.build_enabled_levels = function(tag_defs) {
        var levels = {};
        for (var t = 0; t < tag_defs.length; t++) {
            levels[tag_defs[t].key] = true;
        }
        return levels;
    };

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

    kit.record_detail._fetch_logs = function($panel_log, params, config) {
        var body = {
            action: config.log_action,
            since_idx: params.since_idx,
            cluster_id: config.cluster_id
        };
        body[config.object_id_field] = params.object_id;
        body[config.run_id_field] = params.run_id;
        $.ajax({
            type: 'POST',
            url: config.poll_url,
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
                    var entry_html = kit.record_detail.render_log_entry(entries[idx], false, config.panel);
                    var $entry = $(entry_html).addClass('kit-fade-in');
                    $panel_log.append($entry);
                    $entry.one('animationend', function() { $(this).removeClass('kit-fade-in'); });
                }
                $panel_log.children('.detail-log-line').last().css('border-bottom', '');
                $panel_log.attr('data-since-idx', params.since_idx + entries.length);
            }
        });
    };

    kit.record_detail._fetch_run = function(config, run_number, callback) {
        $.ajax({
            type: 'POST',
            url: config.poll_url,
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            data: JSON.stringify({
                action: config.run_action,
                job_id: config.record_id,
                current_run: run_number,
                cluster_id: config.cluster_id
            }),
            contentType: 'application/json',
            error: function(xhr, status, err) {
                console.error('Run detail fetch error: status=' + xhr.status + ' err=' + err);
            },
            success: function(data) {
                callback(data);
            }
        });
    };

    function render_run_nav($container, prev_run, next_run, navigate_fn) {
        var html = '<span class="detail-pagination-row">';
        if (prev_run !== null) {
            html += '<a href="#" class="detail-page-prev" data-run="' + prev_run + '">Previous run</a>';
        } else {
            html += '<span class="detail-page-prev detail-page-disabled">Previous run</span>';
        }
        html += '<span class="detail-page-sep">|</span>';
        if (next_run !== null) {
            html += '<a href="#" class="detail-page-next" data-run="' + next_run + '">Next run</a>';
        } else {
            html += '<span class="detail-page-next detail-page-disabled">Next run</span>';
        }
        html += '</span>';
        $container.html(html);
        $container.find('a[data-run]').on('click', function(e) {
            e.preventDefault();
            var target_run = parseInt($(this).attr('data-run'), 10);
            navigate_fn(target_run);
        });
    }

    function update_all_nav($tops, $bottoms, prev_run, next_run, navigate_fn) {
        if ($tops) render_run_nav($tops, prev_run, next_run, navigate_fn);
        if ($bottoms) render_run_nav($bottoms, prev_run, next_run, navigate_fn);
    }

    kit.record_detail.bind_panel_actions = function($container, tag_defs) {
        var enabled_levels = kit.record_detail.build_enabled_levels(tag_defs);
        $container.data('enabled-levels', enabled_levels);

        $container.on('click', '.detail-tag', function() {
            var key = $(this).attr('data-key');
            enabled_levels[key] = !enabled_levels[key];
            kit.record_detail.apply_level_filter($container, enabled_levels, tag_defs);
        });

        $container.on('click', '.detail-action-toggle-all', function() {
            var any_off = false;
            for (var key in enabled_levels) {
                if (!enabled_levels[key]) { any_off = true; break; }
            }
            var new_val = any_off;
            for (var key2 in enabled_levels) {
                enabled_levels[key2] = new_val;
            }
            kit.record_detail.apply_level_filter($container, enabled_levels, tag_defs);
        });

        $container.on('click', '.detail-action-copy-row', function(e) {
            e.stopPropagation();
            var $line = $(this).closest('.detail-log-line');
            var raw = $line.find('.detail-log-msg').attr('data-raw');
            if (raw && navigator.clipboard) {
                navigator.clipboard.writeText(raw);
            }
        });

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

        $container.on('click', '.detail-log-line', function(e) {
            if ($(e.target).closest('.detail-tag, .dashboard-panel-action-badge, .dashboard-outcome-badge, .detail-log-actions').length) return;
            $(this).toggleClass('detail-log-line-expanded');
        });

        return enabled_levels;
    };

    kit.record_detail.open_panel = function($panel, record, config) {
        var $panel_log = $panel.find('.detail-panel-log');
        if (!$panel_log.length) {
            $panel_log = $panel;
        }

        var mirror_html = config.render_mirror(record);
        $panel_log.prepend(mirror_html);

        var fetch_params = {
            object_id: config.record_id,
            run_id: record.current_run,
            since_idx: 0
        };
        kit.record_detail._fetch_logs($panel_log, fetch_params, config);

        var poll_timer = null;
        if (config.poll_interval_ms > 0) {
            poll_timer = setInterval(function() {
                var since_idx = parseInt($panel_log.attr('data-since-idx'), 10);
                kit.record_detail._fetch_logs($panel_log, {
                    object_id: config.record_id,
                    run_id: record.current_run,
                    since_idx: since_idx
                }, config);
            }, config.poll_interval_ms);
        }

        $panel.data('log-poll-timer', poll_timer);
    };

    kit.record_detail.close_panel = function($panel) {
        var timer = $panel.data('log-poll-timer');
        if (timer) {
            clearInterval(timer);
            $panel.data('log-poll-timer', null);
        }
        $panel.find('.detail-panel-log').children().remove();
    };

    kit.record_detail.init = function(config) {
        var $container = $(config.container);
        var $nav_top = config.nav_container_top ? $(config.nav_container_top) : null;
        var $nav_bottom = config.nav_container_bottom ? $(config.nav_container_bottom) : null;
        var record_poll_timer = null;
        var log_poll_timer = null;
        var current_run = config.run_number;
        var actions_bound = false;

        function stop_timers() {
            if (record_poll_timer) { clearInterval(record_poll_timer); record_poll_timer = null; }
            if (log_poll_timer) { clearInterval(log_poll_timer); log_poll_timer = null; }
        }

        function navigate_to(run_number) {
            stop_timers();
            var new_url = config.build_run_url(run_number);
            history.pushState({run: run_number}, '', new_url);
            current_run = run_number;
            $('#record-detail-title').text('Run ' + kit.format_number_full(run_number));
            crossfade_load(run_number);
        }

        function crossfade_load(run_number) {
            $container.css({transition: 'opacity ' + FADE_MS + 'ms', opacity: 0});
            setTimeout(function() {
                kit.record_detail._fetch_run(config, run_number, function(data) {
                    var $panel_log = $container.find('.detail-panel-log');
                    $panel_log.children().remove();
                    $panel_log.attr('data-since-idx', '0');
                    populate_run(data, run_number);
                    $container.css({opacity: 1});
                });
            }, FADE_MS);
        }

        function populate_run(data, run_number) {
            var record = data.record;
            if (record === null) {
                $container.html('<div style="padding:16px;color:#aaa">No data for this run.</div>');
                return;
            }

            var $panel_log = $container.find('.detail-panel-log');
            var mirror_html = config.render_mirror(record);
            $panel_log.prepend(mirror_html);

            if (!actions_bound) {
                kit.record_detail.bind_panel_actions($container, config.tag_defs);
                actions_bound = true;
            }

            kit.record_detail._fetch_logs($panel_log, {
                object_id: config.record_id,
                run_id: run_number,
                since_idx: 0
            }, config);

            if (config.poll_interval_ms > 0) {
                log_poll_timer = setInterval(function() {
                    var since_idx = parseInt($panel_log.attr('data-since-idx'), 10);
                    kit.record_detail._fetch_logs($panel_log, {
                        object_id: config.record_id,
                        run_id: run_number,
                        since_idx: since_idx
                    }, config);
                }, config.poll_interval_ms);
            }

            update_all_nav($nav_top, $nav_bottom, data.prev_run, data.next_run, navigate_to);

            if (record.outcome === 'running') {
                record_poll_timer = setInterval(function() {
                    kit.record_detail._fetch_run(config, run_number, function(fresh_data) {
                        var fresh = fresh_data.record;
                        if (fresh === null) return;
                        if (fresh.outcome !== 'running') {
                            clearInterval(record_poll_timer);
                            record_poll_timer = null;
                            var $badge = $container.find('.dashboard-outcome-badge').first();
                            var new_badge_html = kit.outcome.badge(fresh.outcome, config.panel.outcome_palette, fresh);
                            $badge.replaceWith($(new_badge_html).addClass('kit-puff').one('animationend', function() {
                                $(this).removeClass('kit-puff');
                            }));
                            var new_tags = kit.record_detail.render_dark_tags(fresh, config.tag_defs);
                            $container.find('.detail-log-mirror .detail-log-msg').html(new_tags);
                        }
                        update_all_nav($nav_top, $nav_bottom, fresh_data.prev_run, fresh_data.next_run, navigate_to);
                    });
                }, config.poll_interval_ms);
            }
        }

        function load_run(run_number) {
            kit.record_detail._fetch_run(config, run_number, function(data) {
                populate_run(data, run_number);
                $container.css({opacity: 1});
            });
        }

        $(window).on('popstate', function(e) {
            var state = e.originalEvent.state;
            if (state && state.run) {
                stop_timers();
                current_run = state.run;
                $('#record-detail-title').text('Run ' + kit.format_number_full(state.run));
                crossfade_load(state.run);
            }
        });

        history.replaceState({run: current_run}, '', window.location.href);

        load_run(current_run);
    };
})();
