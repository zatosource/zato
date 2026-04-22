
/* Dashboard kit - sparkline component.
   Renders a smooth cubic-Bezier area spark under a single-row number,
   with a configurable end-dot (filled, hollow, halo). Keeps a registry
   of every rendered sparkline keyed by its container selector so
   correlated hover overlays can find xs/ys and data_points later. */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var ns = $.fn.zato.dashboard_kit;
    ns.sparkline = {};

    ns.sparkline._counter = 0;
    ns.sparkline._registry = {};

    ns.sparkline._draw_dot = function(style, cx, cy, r, color) {
        style = style || 'filled';
        var svg = '';
        if (style === 'filled') {
            svg += '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" fill="' + color + '"/>';
        } else if (style === 'hollow') {
            svg += '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" ';
            svg += 'fill="#012845" stroke="' + color + '" stroke-width="1.5"/>';
        } else if (style === 'filled_halo') {
            svg += '<circle cx="' + cx + '" cy="' + cy + '" r="' + (r + 3) + '" ';
            svg += 'fill="rgba(0,0,0,0.5)"/>';
            svg += '<circle cx="' + cx + '" cy="' + cy + '" r="' + (r + 2) + '" ';
            svg += 'fill="none" stroke="' + color + '" stroke-opacity="0.5" stroke-width="1"/>';
            svg += '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" fill="' + color + '"/>';
        } else if (style === 'hollow_halo') {
            svg += '<circle cx="' + cx + '" cy="' + cy + '" r="' + (r + 2) + '" ';
            svg += 'fill="none" stroke="' + color + '" stroke-opacity="0.3" stroke-width="1"/>';
            svg += '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" ';
            svg += 'fill="#012845" stroke="' + color + '" stroke-width="1.5"/>';
        } else if (style === 'filled_white_ring') {
            svg += '<circle cx="' + cx + '" cy="' + cy + '" r="' + (r + 0.5) + '" fill="' + color + '"/>';
            svg += '<circle cx="' + cx + '" cy="' + cy + '" r="' + (r + 0.5) + '" ';
            svg += 'fill="none" stroke="#ffffff" stroke-opacity="0.6" stroke-width="1"/>';
        } else {
            svg += '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" fill="' + color + '"/>';
        }
        return svg;
    };

    ns.sparkline._render_svg = function(data_points, opts) {
        var w = opts.pixel_width;
        var h = opts.height;
        var color = opts.color;
        var dot_color = opts.dot_color;
        var dot_r = opts.dot_radius;
        var dot_style = opts.dot_style;
        var stroke_width = opts.stroke_width;

        var halo_extra = 2;
        var pad_x = Math.max(3, dot_r + halo_extra + 1);
        var pad_top = Math.max(3, dot_r + halo_extra + 1);
        var pad_bottom = Math.max(1, dot_r + halo_extra + 1);

        var instance_id = ns.sparkline._counter++;
        var grad_id = 'sparkArea_' + instance_id;

        var max_points = Math.max(2, Math.floor(w / 9));
        if (data_points.length > max_points) {
            var last_real = data_points[data_points.length - 1];
            var step = data_points.length / max_points;
            var resampled = [];
            for (var ri = 0; ri < max_points; ri++) {
                var start_i = Math.floor(ri * step);
                var end_i = Math.floor((ri + 1) * step);
                var sum = 0;
                for (var si = start_i; si < end_i; si++) {
                    sum += data_points[si];
                }
                resampled.push(sum / (end_i - start_i));
            }
            resampled[resampled.length - 1] = last_real;
            data_points = resampled;
        }

        var min_val = Math.min.apply(null, data_points);
        var max_val = Math.max.apply(null, data_points);
        var range = max_val - min_val;

        if (range > 0) {
            var mid = (min_val + max_val) / 2;
            min_val = mid - range * 0.40;
            max_val = mid + range * 0.40;
            range = max_val - min_val;
        }

        var draw_h = h - pad_top - pad_bottom;
        var draw_w = w - 2 * pad_x;
        var n = data_points.length;

        var xs = [];
        var ys = [];
        for (var idx = 0; idx < n; idx++) {
            var xp = pad_x + (n === 1 ? draw_w / 2 : (idx / (n - 1)) * draw_w);
            var yp;
            if (range === 0) {
                yp = pad_top + draw_h * 0.5;
            } else {
                yp = pad_top + draw_h - ((data_points[idx] - min_val) / range) * draw_h;
            }
            xs.push(xp);
            ys.push(yp);
        }

        var path_d = 'M ' + xs[0].toFixed(2) + ' ' + ys[0].toFixed(2);
        for (var k = 1; k < n; k++) {
            var x0 = xs[k - 1];
            var y0 = ys[k - 1];
            var x1 = xs[k];
            var y1 = ys[k];
            var cx = (x0 + x1) / 2;
            path_d += ' C ' + cx.toFixed(2) + ' ' + y0.toFixed(2) +
                      ', ' + cx.toFixed(2) + ' ' + y1.toFixed(2) +
                      ', ' + x1.toFixed(2) + ' ' + y1.toFixed(2);
        }

        var area_d = path_d + ' L ' + xs[n - 1].toFixed(2) + ' ' + h.toFixed(2) +
                              ' L ' + xs[0].toFixed(2) + ' ' + h.toFixed(2) + ' Z';

        var svg = '<svg xmlns="http://www.w3.org/2000/svg" ';
        svg += 'width="' + w + '" height="' + h + '" ';
        svg += 'viewBox="0 0 ' + w + ' ' + h + '">';

        svg += '<defs>';
        svg += '<linearGradient id="' + grad_id + '" x1="0" y1="0" x2="0" y2="1">';
        svg += '<stop offset="0" stop-color="' + color + '" stop-opacity="0.18"/>';
        svg += '<stop offset="0.5" stop-color="' + color + '" stop-opacity="0.10"/>';
        svg += '<stop offset="1" stop-color="' + color + '" stop-opacity="0.03"/>';
        svg += '</linearGradient>';
        svg += '</defs>';

        svg += '<path d="' + area_d + '" fill="url(#' + grad_id + ')" stroke="none"/>';

        svg += '<path d="' + path_d + '" fill="none" ';
        svg += 'stroke="' + color + '" stroke-width="' + stroke_width + '" ';
        svg += 'stroke-linecap="round" stroke-linejoin="round"/>';

        if (dot_r > 0) {
            svg += ns.sparkline._draw_dot(dot_style, xs[n - 1].toFixed(2), ys[n - 1].toFixed(2), dot_r, dot_color);
        }

        svg += '</svg>';

        return {svg: svg, xs: xs, ys: ys, pad_x: pad_x};
    };

    /* Render a sparkline into `container` with the given numeric
       data_points. Accepts either a CSS selector or a jQuery/DOM
       element; the registry lookup (used by hover correlation) only
       keeps entries keyed by selector strings. */
    ns.sparkline.render = function(container, data_points, options) {
        options = options || {};
        var h = options.height || 36;
        var color = options.color || '#82ccff';
        var dot_color = options.dot_color || color;
        var dot_r = (options.dot_radius === undefined) ? 3 : options.dot_radius;
        var dot_style = options.dot_style || 'filled';
        var stroke_width = options.stroke_width || 1.6;
        var min_points = options.min_points || 2;

        var $container = $(container);
        if (!$container.length) {
            return;
        }

        if (!data_points || data_points.length < min_points) {
            var placeholder_w = options.width || $container[0].clientWidth || 240;
            if (placeholder_w < 20) {
                placeholder_w = 240;
            }
            var placeholder_y = (h / 2).toFixed(2);
            var placeholder_svg = '<svg xmlns="http://www.w3.org/2000/svg" ';
            placeholder_svg += 'width="' + placeholder_w + '" height="' + h + '" ';
            placeholder_svg += 'viewBox="0 0 ' + placeholder_w + ' ' + h + '">';
            placeholder_svg += '<line x1="0" y1="' + placeholder_y + '" ';
            placeholder_svg += 'x2="' + placeholder_w + '" y2="' + placeholder_y + '" ';
            placeholder_svg += 'stroke="' + color + '" stroke-opacity="0.25" stroke-width="1.25" ';
            placeholder_svg += 'stroke-dasharray="4,4" stroke-linecap="round"/>';
            placeholder_svg += '</svg>';
            $container.html(placeholder_svg);
            if (typeof container === 'string') {
                delete ns.sparkline._registry[container];
            }
            return;
        }

        var pixel_width = options.width || $container[0].clientWidth || 240;
        if (pixel_width < 20) {
            pixel_width = 240;
        }

        var render_opts = {
            pixel_width: pixel_width,
            height: h,
            color: color,
            dot_color: dot_color,
            dot_radius: dot_r,
            dot_style: dot_style,
            stroke_width: stroke_width
        };

        var result = ns.sparkline._render_svg(data_points, render_opts);
        $container.html(result.svg);

        if (typeof container === 'string') {
            ns.sparkline._registry[container] = {
                data_points: data_points.slice(),
                xs: result.xs,
                ys: result.ys,
                pad_x: result.pad_x,
                pixel_width: pixel_width,
                height: h
            };
        }
    };

    ns.sparkline.registry = function() {
        return ns.sparkline._registry;
    };

    ns.sparkline.clear_overlay = function(selector) {
        var $container = $(selector);
        if (!$container.length) return;
        $container.find('.dashboard-kit-spark-overlay').remove();
    };

    ns.sparkline.show_marker = function(selector, data_index, marker_color) {
        var entry = ns.sparkline._registry[selector];
        if (!entry) return;
        if (data_index < 0 || data_index >= entry.xs.length) return;

        var $container = $(selector);
        if (!$container.length) return;

        var css = $container.css('position');
        if (css !== 'relative' && css !== 'absolute' && css !== 'fixed') {
            $container.css('position', 'relative');
        }

        var $overlay = $container.find('.dashboard-kit-spark-overlay');
        if (!$overlay.length) {
            $overlay = $('<div class="dashboard-kit-spark-overlay"></div>').css({
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                'pointer-events': 'none'
            });
            $container.append($overlay);
        }

        var w = entry.pixel_width;
        var h = entry.height;
        var px = entry.xs[data_index];
        var py = entry.ys[data_index];

        var svg = '<svg xmlns="http://www.w3.org/2000/svg" ';
        svg += 'width="100%" height="100%" viewBox="0 0 ' + w + ' ' + h + '" ';
        svg += 'preserveAspectRatio="none" style="display:block">';
        svg += '<line x1="' + px.toFixed(2) + '" y1="0" x2="' + px.toFixed(2) + '" y2="' + h + '" ';
        svg += 'stroke="rgba(255,255,255,0.35)" stroke-width="1" stroke-dasharray="2,2" ';
        svg += 'vector-effect="non-scaling-stroke"/>';
        svg += '<circle cx="' + px.toFixed(2) + '" cy="' + py.toFixed(2) + '" r="3.5" ';
        svg += 'fill="' + (marker_color || '#ffffff') + '" stroke="#262630" stroke-width="1.5"/>';
        svg += '</svg>';

        $overlay.html(svg);
    };
})();
