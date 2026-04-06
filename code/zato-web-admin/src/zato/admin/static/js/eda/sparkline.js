
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }

$.fn.zato.eda.sparkline = function(container, data_points, options) {
    options = options || {};
    var w = options.width || 80;
    var h = options.height || 24;
    var color = options.color || '#82ccff';
    var dot_color = options.dot_color || '#012845';
    var dot_r = options.dot_radius || 2.5;
    var pad = dot_r + 1;

    if (!data_points || data_points.length < 2) {
        $(container).html('');
        return;
    }

    var min_val = Math.min.apply(null, data_points);
    var max_val = Math.max.apply(null, data_points);
    var range = max_val - min_val || 1;

    var points = [];
    for (var i = 0; i < data_points.length; i++) {
        var x = pad + (i / (data_points.length - 1)) * (w - 2 * pad);
        var y = h - pad - ((data_points[i] - min_val) / range) * (h - 2 * pad);
        points.push(x.toFixed(1) + ',' + y.toFixed(1));
    }

    var last_x = pad + ((data_points.length - 1) / (data_points.length - 1)) * (w - 2 * pad);
    var last_y = h - pad - ((data_points[data_points.length - 1] - min_val) / range) * (h - 2 * pad);

    var svg = '<svg width="' + w + '" height="' + h + '" xmlns="http://www.w3.org/2000/svg">';
    svg += '<polyline fill="none" stroke="' + color + '" stroke-width="1.5" points="' + points.join(' ') + '" />';
    svg += '<circle cx="' + last_x.toFixed(1) + '" cy="' + last_y.toFixed(1) + '" r="' + dot_r + '" fill="' + dot_color + '" />';
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

$.fn.zato.eda.depth_class = function(d) {
    if (d === 0) return 'depth-0';
    if (d < 100) return 'depth-low';
    return 'depth-high';
};

$.fn.zato.eda.depth_html = function(d) {
    return '<span class="depth-badge ' + $.fn.zato.eda.depth_class(d) + '">' + d + '</span>';
};

$.fn.zato.eda.update_refresh_indicator = function() {
    var now = new Date();
    var hh = ('0' + now.getHours()).slice(-2);
    var mm = ('0' + now.getMinutes()).slice(-2);
    var ss = ('0' + now.getSeconds()).slice(-2);
    $('#eda-last-refresh').text('Last refreshed: ' + hh + ':' + mm + ':' + ss);
};
