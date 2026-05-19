/* Dashboard kit - generic metadata card renderer.
   Renders groups of read-only key-value cards from a field definition array.
   Domain-agnostic - all field knowledge comes through the config object. */

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

        for (var groupIndex = 0; groupIndex < groups.length; groupIndex++) {
            var group = groups[groupIndex];

            html += '<div class="detail-config-cards detail-metadata">';

            for (var fieldIndex = 0; fieldIndex < group.fields.length; fieldIndex++) {
                var field = group.fields[fieldIndex];
                var value = data[field.name];

                if (value === null) {
                    value = '';
                }
                if (value === undefined) {
                    value = '';
                }

                if (field.format === 'time') {
                    value = kit.format_local_time(value);
                }

                if (field.suffix) {
                    value = value + field.suffix;
                }

                html += kit.meta_cards._card(field.label, String(value), false);
            }

            html += '</div>';
        }

        $container.html(html);
    };

// ////////////////////////////////////////////////////////////////////////

    kit.meta_cards._card = function(label, value, isHtml) {

        var escapedLabel = kit._esc_html(label);
        var renderedValue = isHtml ? value : kit._esc_html(value);

        var html = '<div class="meta-card">';
        html += '<div class="meta-label">' + escapedLabel + '</div>';
        html += '<div class="meta-value">' + renderedValue + '</div>';
        html += '</div>';

        return html;
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
