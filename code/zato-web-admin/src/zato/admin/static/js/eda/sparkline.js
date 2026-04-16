
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }

$.fn.zato.eda._sparkline_counter = 0;

$.fn.zato.eda.sparkline = function(container, data_points, options) {
    options = options || {};
    var w = options.width || 80;
    var h = options.height || 24;
    var color = options.color || '#82ccff';
    var dot_color = options.dot_color || color;
    var dot_r = options.dot_radius || 2.5;
    var pad = dot_r + 2;

    if (!data_points || data_points.length === 0) {
        $(container).html('');
        return;
    }

    var instance_id = $.fn.zato.eda._sparkline_counter++;
    var glow_id = 'sparkGlow_' + instance_id;
    var grad_id = 'sparkArea_' + instance_id;

    var defs = '<defs>';
    defs += '<filter id="' + glow_id + '">';
    defs += '<feGaussianBlur stdDeviation="3" result="blur"/>';
    defs += '<feMerge>';
    defs += '<feMergeNode in="blur"/>';
    defs += '<feMergeNode in="blur"/>';
    defs += '<feMergeNode in="SourceGraphic"/>';
    defs += '</feMerge>';
    defs += '</filter>';
    defs += '<linearGradient id="' + grad_id + '" x1="0" y1="0" x2="0" y2="1">';
    defs += '<stop offset="0" stop-color="' + color + '" stop-opacity="0.25"/>';
    defs += '<stop offset="0.3" stop-color="' + color + '" stop-opacity="0.12"/>';
    defs += '<stop offset="1" stop-color="' + color + '" stop-opacity="0"/>';
    defs += '</linearGradient>';
    defs += '</defs>';

    var svg = '<svg width="' + w + '" height="' + h + '" xmlns="http://www.w3.org/2000/svg">';
    svg += defs;

    if (data_points.length === 1) {
        svg += '<circle cx="' + (w / 2) + '" cy="' + (h / 2) + '" r="' + dot_r + '" fill="' + dot_color + '" filter="url(#' + glow_id + ')" />';
        svg += '</svg>';
        $(container).html(svg);
        return;
    }

    var min_val = Math.min.apply(null, data_points);
    var max_val = Math.max.apply(null, data_points);
    var range = max_val - min_val;

    if (range === 0) {
        var baseline_y = h * 0.6;
        var points = [];
        var area_points = pad + ',' + h;
        for (var flat_idx = 0; flat_idx < data_points.length; flat_idx++) {
            var flat_x = pad + (flat_idx / (data_points.length - 1)) * (w - 2 * pad);
            points.push(flat_x.toFixed(1) + ',' + baseline_y.toFixed(1));
            area_points += ' ' + flat_x.toFixed(1) + ',' + baseline_y.toFixed(1);
        }
        area_points += ' ' + (w - pad) + ',' + h;
        svg += '<polygon fill="url(#' + grad_id + ')" points="' + area_points + '" />';
        svg += '<polyline fill="none" stroke="' + color + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="' + points.join(' ') + '" filter="url(#' + glow_id + ')" />';
        var last_flat_x = (w - pad);
        svg += '<circle cx="' + last_flat_x.toFixed(1) + '" cy="' + baseline_y.toFixed(1) + '" r="' + dot_r + '" fill="' + dot_color + '" filter="url(#' + glow_id + ')" />';
        svg += '</svg>';
        $(container).html(svg);
        return;
    }

    var points = [];
    var area_points = pad + ',' + h;
    for (var idx = 0; idx < data_points.length; idx++) {
        var x = pad + (idx / (data_points.length - 1)) * (w - 2 * pad);
        var y = h - pad - ((data_points[idx] - min_val) / range) * (h - 2 * pad);
        points.push(x.toFixed(1) + ',' + y.toFixed(1));
        area_points += ' ' + x.toFixed(1) + ',' + y.toFixed(1);
    }
    area_points += ' ' + (w - pad) + ',' + h;

    var last_x = (w - pad);
    var last_y = h - pad - ((data_points[data_points.length - 1] - min_val) / range) * (h - 2 * pad);

    svg += '<polygon fill="url(#' + grad_id + ')" points="' + area_points + '" />';
    svg += '<polyline fill="none" stroke="' + color + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="' + points.join(' ') + '" filter="url(#' + glow_id + ')" />';
    svg += '<circle cx="' + last_x.toFixed(1) + '" cy="' + last_y.toFixed(1) + '" r="' + dot_r + '" fill="' + dot_color + '" filter="url(#' + glow_id + ')" />';
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
