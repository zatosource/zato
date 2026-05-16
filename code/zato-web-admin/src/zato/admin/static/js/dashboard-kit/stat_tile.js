
/* Dashboard kit - stat tile group with correlated hover tooltip.
   Each tile holds a big number, an optional sublabel, and a sparkline;
   the group owns a single tooltip that shows every tile's value at the
   timestamp under the mouse, regardless of which tile the mouse is
   currently over. */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var ns = $.fn.zato.dashboard_kit;
    ns.stat_tile = {};

    var HOVER_CLEAR_MS = 80;
    var TOOLTIP_MARGIN_PX = 8;
    var TOOLTIP_GAP_PX = 10;
    var TOOLTIP_ID = 'dashboard-tile-tooltip';

    /* Initialise a group of correlated stat tiles.
       config:
         tiles: array of tile specs. Each spec:
           sparkline_selector: '#spark-runs'
           buffer_key:         identifier used to look up the raw data
                               buffer via config.get_buffer(key)
           label:              label shown in the tooltip row
           color:              marker + dot colour
           exclude_from_hover: (optional, boolean) if true, the tile's
                               sparkline still shows a hover marker but
                               its value row is omitted from the tooltip.
                               Useful for gauge-style tiles (e.g. age)
                               whose scale differs from the other tiles.
         get_buffer(key):      returns an array of {ts, value} objects,
                               in chronological order.
         tile_container:       CSS class used to locate the enclosing
                               .dashboard-tile from a sparkline element
                               (default 'dashboard-tile').
         hover_header(seconds_ago): optional formatter for the tooltip
                                    header. Default calls kit.format_ago.
         format_full(n):       formatter for each row's numeric value.
                               Defaults to kit.format_number_full. */
    ns.stat_tile.init = function(config) {
        var state = {
            ready: false,
            clear_timer: null
        };
        var tile_cls = config.tile_container || 'dashboard-tile';
        var fmt_full = config.format_full || ns.format_number_full;
        var hover_header = config.hover_header || function(seconds_ago) {
            return ns.format_ago(seconds_ago);
        };

        var clear_hover = function() {
            for (var i = 0; i < config.tiles.length; i++) {
                ns.sparkline.clear_overlay(config.tiles[i].sparkline_selector);
            }
            $('#' + TOOLTIP_ID).css('display', 'none');
        };

        var schedule_clear = function() {
            if (state.clear_timer) { clearTimeout(state.clear_timer); }
            state.clear_timer = setTimeout(function() {
                state.clear_timer = null;
                clear_hover();
            }, HOVER_CLEAR_MS);
        };

        var cancel_clear = function() {
            if (state.clear_timer) {
                clearTimeout(state.clear_timer);
                state.clear_timer = null;
            }
        };

        var show_hover = function(active_selector, mouse_event) {
            cancel_clear();
            var registry = ns.sparkline.registry();
            var active_entry = registry[active_selector];
            if (!active_entry) return;

            var $spark = $(active_selector);
            var rect = $spark[0].getBoundingClientRect();
            var mouse_x_px = mouse_event.clientX - rect.left;
            var container_px_w = rect.width;
            if (mouse_x_px < 0) mouse_x_px = 0;
            if (mouse_x_px > container_px_w) mouse_x_px = container_px_w;

            var scale = (container_px_w > 0 && active_entry.pixel_width > 0)
                ? (active_entry.pixel_width / container_px_w) : 1;
            var logical_x = mouse_x_px * scale;

            var n = active_entry.data_points.length;
            var nearest_index = 0;
            var nearest_d = Infinity;
            for (var i = 0; i < n; i++) {
                var d = Math.abs(active_entry.xs[i] - logical_x);
                if (d < nearest_d) {
                    nearest_d = d;
                    nearest_index = i;
                }
            }

            var active_spec = null;
            for (var s = 0; s < config.tiles.length; s++) {
                if (config.tiles[s].sparkline_selector === active_selector) {
                    active_spec = config.tiles[s];
                    break;
                }
            }
            if (!active_spec) return;

            var active_buffer = config.get_buffer(active_spec.buffer_key);
            if (!active_buffer || !active_buffer[nearest_index]) return;

            var target_ts = active_buffer[nearest_index].ts;
            var now_ms = Date.now();
            var seconds_ago = Math.max(0, Math.round((now_ms - target_ts) / 1000));
            var header_title = hover_header(seconds_ago);

            var tooltip_rows = [];
            tooltip_rows.push('<div class="dashboard-tooltip-header">' +
                '<div class="dashboard-tooltip-title">' + header_title + '</div>' +
                '</div>');

            for (var t = 0; t < config.tiles.length; t++) {
                var tile = config.tiles[t];
                var entry = registry[tile.sparkline_selector];
                var buffer = config.get_buffer(tile.buffer_key);

                var mapped_index = -1;
                if (buffer && buffer.length > 0) {
                    var best_d = Infinity;
                    for (var bi = 0; bi < buffer.length; bi++) {
                        var dt = Math.abs(buffer[bi].ts - target_ts);
                        if (dt < best_d) {
                            best_d = dt;
                            mapped_index = bi;
                        }
                    }
                }

                // Show the marker dot on the sparkline regardless ..
                if (mapped_index >= 0 && entry) {
                    ns.sparkline.show_marker(tile.sparkline_selector, mapped_index, tile.color);
                }

                // .. but skip this tile's row in the tooltip if it is a gauge.
                if (tile.exclude_from_hover) {
                    continue;
                }

                var value_text;
                if (mapped_index >= 0) {
                    value_text = fmt_full(buffer[mapped_index].value);
                } else {
                    value_text = '\u2013';
                }

                tooltip_rows.push('<div class="dashboard-tile-tooltip-row">' +
                    '<span class="dashboard-tile-tooltip-dot" style="background:' + tile.color + '"></span>' +
                    '<span class="dashboard-tile-tooltip-label">' + tile.label + '</span>' +
                    '<span class="dashboard-tile-tooltip-value">' + value_text + '</span>' +
                    '</div>');
            }

            var $tooltip = $('#' + TOOLTIP_ID);
            if ($tooltip.length === 0) {
                $('body').append('<div id="' + TOOLTIP_ID + '" class="dashboard-tile-tooltip"></div>');
                $tooltip = $('#' + TOOLTIP_ID);
            }
            $tooltip.html(tooltip_rows.join(''));

            /* Measurements on display:none are unreliable; promote the
               tooltip to block+hidden, measure, then place in one shot. */
            $tooltip.css({display: 'block', visibility: 'hidden', left: '0px', top: '0px'});

            var tt_w = $tooltip.outerWidth();
            var tt_h = $tooltip.outerHeight();
            var viewport_w = $(window).width();
            var viewport_h = $(window).height();

            /* Anchor above the tile itself (centred) rather than the
               mouse. Keeps the tooltip rock-steady while the mouse moves
               inside the tile. */
            var $tile = $spark.closest('.' + tile_cls);
            var tile_rect = $tile.length ? $tile[0].getBoundingClientRect() : rect;
            var tile_cx = tile_rect.left + tile_rect.width / 2;

            var left = tile_cx - tt_w / 2;
            var top = tile_rect.top - tt_h - TOOLTIP_GAP_PX;

            if (top < TOOLTIP_MARGIN_PX) {
                top = tile_rect.bottom + TOOLTIP_GAP_PX;
            }

            if (left + tt_w + TOOLTIP_MARGIN_PX > viewport_w) {
                left = viewport_w - tt_w - TOOLTIP_MARGIN_PX;
            }
            if (left < TOOLTIP_MARGIN_PX) { left = TOOLTIP_MARGIN_PX; }
            if (top + tt_h + TOOLTIP_MARGIN_PX > viewport_h) {
                top = viewport_h - tt_h - TOOLTIP_MARGIN_PX;
            }
            if (top < TOOLTIP_MARGIN_PX) { top = TOOLTIP_MARGIN_PX; }

            $tooltip.css({visibility: 'visible', left: left + 'px', top: top + 'px'});
        };

        var bind_once = function() {
            if (state.ready) return;
            var bound_any = false;
            for (var i = 0; i < config.tiles.length; i++) {
                (function(selector) {
                    var $spark = $(selector);
                    if (!$spark.length) return;
                    var $tile = $spark.closest('.' + tile_cls);
                    if (!$tile.length) return;
                    bound_any = true;
                    $tile.css('cursor', 'crosshair');
                    $tile.off('mousemove.tilehover mouseleave.tilehover');
                    $tile.on('mousemove.tilehover', function(event) {
                        show_hover(selector, event);
                    });
                    $tile.on('mouseleave.tilehover', function() {
                        schedule_clear();
                    });
                })(config.tiles[i].sparkline_selector);
            }
            if (bound_any) state.ready = true;
        };

        return {
            bind: bind_once,
            clear: clear_hover
        };
    };
})();
