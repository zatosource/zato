
// ////////////////////////////////////////////////////////////////////////
// Dashboard kit - generic metadata card renderer.
// Renders groups of read-only key-value cards from a field definition array.
// Domain-agnostic - all field knowledge comes through the config object.
// ////////////////////////////////////////////////////////////////////////

(function($) {

    if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
    if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

    var kit = $.fn.zato.dashboard_kit;
    kit.meta_cards = {};

// ////////////////////////////////////////////////////////////////////////

    kit.meta_cards.render = function(config) {

        var $container = $(config.container);
        var data = config.data;
        var groups = config.groups;

        // Build the HTML for all groups ..
        var out = '';

        for (var groupIndex = 0; groupIndex < groups.length; groupIndex++) {
            var group = groups[groupIndex];

            out += '<div class="detail-config-cards detail-metadata">';

            // .. render each field in the group ..
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

                out += kit.meta_cards._card(field.label, String(value), false);
            }

            out += '</div>';
        }

        // .. and inject into the container.
        $container.html(out);
    };

// ////////////////////////////////////////////////////////////////////////

    kit.meta_cards._card = function(label, value, isHtml) {

        // Build a single meta-card element ..
        var escapedLabel = kit._esc_html(label);
        var renderedValue = isHtml ? value : kit._esc_html(value);

        var out = '<div class="meta-card">';
        out += '<div class="meta-label">' + escapedLabel + '</div>';
        out += '<div class="meta-value">' + renderedValue + '</div>';
        out += '</div>';

        // .. and return it.
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
