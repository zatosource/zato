
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }

$.fn.zato.eda._sparkline_counter = 0;

$.fn.zato.eda.sparkline = function(container, data_points, options) {
    options = options || {};
    var h = options.height || 36;
    var w = options.width || 240;
    var color = options.color || '#82ccff';
    var dot_color = options.dot_color || color;
    var dot_r = (options.dot_radius === undefined) ? 2.5 : options.dot_radius;
    var stroke_width = options.stroke_width || 1.6;
    var min_points = options.min_points || 2;

    if (!data_points || data_points.length < min_points) {
        $(container).html('');
        return;
    }

    var pad_x = dot_r + 1;
    var pad_top = dot_r + 1;
    var pad_bottom = 1;

    var instance_id = $.fn.zato.eda._sparkline_counter++;
    var grad_id = 'sparkArea_' + instance_id;

    var min_val = Math.min.apply(null, data_points);
    var max_val = Math.max.apply(null, data_points);
    var range = max_val - min_val;

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

    var area_d = path_d + ' L ' + xs[n - 1].toFixed(2) + ' ' + (h - pad_bottom).toFixed(2) +
                          ' L ' + xs[0].toFixed(2) + ' ' + (h - pad_bottom).toFixed(2) + ' Z';

    var svg = '<svg xmlns="http://www.w3.org/2000/svg" ';
    svg += 'viewBox="0 0 ' + w + ' ' + h + '" ';
    svg += 'preserveAspectRatio="none" ';
    svg += 'width="100%" height="100%">';

    svg += '<defs>';
    svg += '<linearGradient id="' + grad_id + '" x1="0" y1="0" x2="0" y2="1">';
    svg += '<stop offset="0" stop-color="' + color + '" stop-opacity="0.45"/>';
    svg += '<stop offset="0.6" stop-color="' + color + '" stop-opacity="0.15"/>';
    svg += '<stop offset="1" stop-color="' + color + '" stop-opacity="0"/>';
    svg += '</linearGradient>';
    svg += '</defs>';

    svg += '<path d="' + area_d + '" fill="url(#' + grad_id + ')" stroke="none" ';
    svg += 'vector-effect="non-scaling-stroke" />';

    svg += '<path d="' + path_d + '" fill="none" ';
    svg += 'stroke="' + color + '" stroke-width="' + stroke_width + '" ';
    svg += 'stroke-linecap="round" stroke-linejoin="round" ';
    svg += 'vector-effect="non-scaling-stroke" />';

    if (dot_r > 0) {
        var last_x = xs[n - 1];
        var last_y = ys[n - 1];
        svg += '<circle cx="' + last_x.toFixed(2) + '" cy="' + last_y.toFixed(2) + '" ';
        svg += 'r="' + dot_r + '" fill="' + dot_color + '" />';
        svg += '<circle cx="' + last_x.toFixed(2) + '" cy="' + last_y.toFixed(2) + '" ';
        svg += 'r="' + (dot_r + 1) + '" fill="none" stroke="' + dot_color + '" stroke-opacity="0.35" stroke-width="1" />';
    }

    svg += '</svg>';
    $(container).html(svg);
};

$.fn.zato.eda.relative_time = function(ts) {
    if (!ts || ts <= 0) return '-';
    var now = Date.now() / 1000;
    var diff = now - ts;
    if (diff < 0) diff = 0;
    if (diff < 60) return Math.floor(diff) + ' sec ago';
    if (diff < 3600) return Math.floor(diff / 60) + ' min ago';
    if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
    return Math.floor(diff / 86400) + 'd ago';
};

$.fn.zato.eda.format_number = function(n) {
    if (n === null || n === undefined) return '-';
    return n.toLocaleString();
};

$.fn.zato.eda.depth_html = function(d) {
    return '<span class="eda-badge">' + d + '</span>';
};

$.fn.zato.eda.update_refresh_indicator = function() {
    var now = new Date();
    var hh = ('0' + now.getHours()).slice(-2);
    var mm = ('0' + now.getMinutes()).slice(-2);
    var ss = ('0' + now.getSeconds()).slice(-2);
    $('#eda-last-refresh').text('Last refreshed: ' + hh + ':' + mm + ':' + ss);
};

$.fn.zato.eda.pluralize = function(count, singular, plural) {
    if (!plural) {
        plural = singular + 's';
    }
    return count === 1 ? singular : plural;
};

$.fn.zato.eda.format_local_time = function(ts) {
    if (!ts || ts <= 0) return '-';
    var d = new Date(ts * 1000);
    var year = d.getFullYear();
    var month = ('0' + (d.getMonth() + 1)).slice(-2);
    var day = ('0' + d.getDate()).slice(-2);
    var hh = ('0' + d.getHours()).slice(-2);
    var mm = ('0' + d.getMinutes()).slice(-2);
    var ss = ('0' + d.getSeconds()).slice(-2);
    return year + '-' + month + '-' + day + ' ' + hh + ':' + mm + ':' + ss;
};

$.fn.zato.eda.bind_copy_targets = function() {
    $('.eda-copy-target').off('click.edacopy').on('click.edacopy', function() {
        var value = $(this).data('copy-value');
        var elem = this;
        navigator.clipboard.writeText(value).then(function() {
            var tip = tippy(elem, {
                content: 'Copied to clipboard',
                trigger: 'manual',
                placement: 'top',
                duration: [200, 200]
            });
            tip.show();
            setTimeout(function() {
                tip.hide();
                setTimeout(function() { tip.destroy(); }, 300);
            }, 600);
        });
    });
};

$.fn.zato.eda.humanize_duration = function(seconds) {
    if (seconds < 0) return 'expired';
    if (seconds < 60) return Math.floor(seconds) + ' ' + $.fn.zato.eda.pluralize(Math.floor(seconds), 'second') + ' from now';
    if (seconds < 3600) {
        var mins = Math.floor(seconds / 60);
        return mins + ' ' + $.fn.zato.eda.pluralize(mins, 'minute') + ' from now';
    }
    if (seconds < 86400) {
        var hours = Math.floor(seconds / 3600);
        return hours + ' ' + $.fn.zato.eda.pluralize(hours, 'hour') + ' from now';
    }
    var days = Math.floor(seconds / 86400);
    return days + ' ' + $.fn.zato.eda.pluralize(days, 'day') + ' from now';
};
