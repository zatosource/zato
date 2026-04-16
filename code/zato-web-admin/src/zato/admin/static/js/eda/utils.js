
/* EDA page utilities - helpers shared by the EDA overview dashboard and
   the topic/queue/publish/messages/message-detail pages. Sparkline
   rendering itself lives in js/dashboard-kit/sparkline.js; the shims
   at the bottom of this file keep older call sites ($.fn.zato.eda.sparkline,
   sparkline_registry, sparkline_clear_overlay, sparkline_show_marker)
   working against the kit implementation. */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }

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

/* Back-compat shims for the old $.fn.zato.eda.sparkline* surface. Any
   page still calling these will transparently land on the dashboard-kit
   implementation. */
$.fn.zato.eda.sparkline = function(container, data_points, options) {
    $.fn.zato.dashboard_kit.sparkline.render(container, data_points, options);
};

$.fn.zato.eda.sparkline_registry = function() {
    return $.fn.zato.dashboard_kit.sparkline.registry();
};

$.fn.zato.eda.sparkline_clear_overlay = function(selector) {
    $.fn.zato.dashboard_kit.sparkline.clear_overlay(selector);
};

$.fn.zato.eda.sparkline_show_marker = function(selector, data_index, marker_color) {
    $.fn.zato.dashboard_kit.sparkline.show_marker(selector, data_index, marker_color);
};
