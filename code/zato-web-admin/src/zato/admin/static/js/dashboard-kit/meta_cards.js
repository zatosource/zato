
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function($) {
    var kit = $.fn.zato.dashboard_kit;
    kit.meta_cards = {};

// ////////////////////////////////////////////////////////////////////////

    kit.meta_cards.render = function(config) {

        var $container = $(config.container);
        var data = config.data;
        var groups = config.groups;
        var html = '';

        for (var groupIdx = 0; groupIdx < groups.length; groupIdx++) {
            var group = groups[groupIdx];

            html += '<div class="detail-config-cards detail-metadata">';

            for (var idx = 0; idx < group.fields.length; idx++) {
                var field = group.fields[idx];
                var value = data[field.name];

                if (field.format === 'time') {
                    value = kit.format_local_time(value);
                }

                if (field.suffix) {
                    value = value + field.suffix;
                }

                if (field.format === 'mono') {
                    value = '<span style="font-family:monospace; font-size:12px">' + kit._esc_html(String(value)) + '</span>';
                    html += kit.meta_cards._card(field.label, value, true);
                }
                else {
                    html += kit.meta_cards._card(field.label, String(value), false);
                }
            }

            html += '</div>';
        }

        $container.html(html);
    };

// ////////////////////////////////////////////////////////////////////////

    kit.meta_cards._card = function(label, value, is_html) {

        var escaped_label = kit._esc_html(label);
        var rendered_value = is_html ? value : kit._esc_html(value);

        var html = '<div class="meta-card">';
        html += '<div class="meta-label">' + escaped_label + '</div>';
        html += '<div class="meta-value">' + rendered_value + '</div>';
        html += '</div>';

        return html;
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
