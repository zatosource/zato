
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
        var copyable = config.copy_as_json;

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

                var copyKey = copyable ? field.copy_key : null;
                out += kit.meta_cards._card(field.label, String(value), false, copyKey);
            }

            out += '</div>';
        }

        // .. inject into the container ..
        $container.html(out);

        // .. and bind click handlers for copyable cards.
        if (copyable) {
            $container.on('click', '.meta-card-copyable', function() {
                var cardKey = $(this).attr('data-copy-key');
                var cardValue = $(this).attr('data-copy-value');
                var jsonObject = {};
                jsonObject[cardKey] = cardValue;
                var jsonString = JSON.stringify(jsonObject);
                kit.copy_to_clipboard(this, jsonString);
            });
        }
    };

// ////////////////////////////////////////////////////////////////////////

    kit.meta_cards._card = function(label, value, isHtml, copyKey) {

        // Build a single meta-card element ..
        var escapedLabel = kit._esc_html(label);
        var renderedValue = isHtml ? value : kit._esc_html(value);

        if (copyKey) {
            var escapedCopyKey = kit._esc_html(copyKey);
            var escapedCopyValue = kit._esc_html(value);
            var out = '<div class="meta-card meta-card-copyable" data-copy-key="' + escapedCopyKey + '" data-copy-value="' + escapedCopyValue + '">';
        }
        else {
            var out = '<div class="meta-card">';
        }

        out += '<div class="meta-label">' + escapedLabel + '</div>';
        out += '<div class="meta-value">' + renderedValue + '</div>';
        out += '</div>';

        // .. and return it.
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
