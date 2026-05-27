
// ////////////////////////////////////////////////////////////////////////
// Dashboard kit - generic metadata card renderer.
// Renders groups of read-only key-value cards from a field definition array.
// Domain-agnostic - all field knowledge comes through the config object.
// ////////////////////////////////////////////////////////////////////////

(function($) {

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

        // .. render the Copy all button if copyable ..
        if (copyable) {
            out += '<div class="meta-cards-footer">';
            out += '<button class="record-edit-action-button meta-cards-copy-all-button" type="button">Copy all</button>';
            out += '</div>';
        }

        // .. inject into the container ..
        $container.html(out);

        // .. and bind click handlers for copyable cards.
        if (copyable) {
            var followCursor = config.copy_tooltip_follows_cursor;

            // .. single card copies just the value ..
            $container.on('click', '.meta-card-copyable', function(event) {
                var cardValue = $(this).attr('data-copy-value');

                if (followCursor) {
                    var clickX = event.clientX;
                    var clickY = event.clientY;
                    navigator.clipboard.writeText(cardValue).then(function() {
                        var anchor = document.createElement('span');
                        anchor.style.position = 'fixed';
                        anchor.style.left = clickX + 'px';
                        anchor.style.top = clickY + 'px';
                        anchor.style.width = '0';
                        anchor.style.height = '0';
                        anchor.style.pointerEvents = 'none';
                        document.body.appendChild(anchor);
                        kit.flash_tooltip(anchor, 'Copied to clipboard');
                        setTimeout(function() { anchor.remove(); }, 700);
                    });
                }
                else {
                    kit.copy_to_clipboard(this, cardValue);
                }
            });

            // .. Copy all builds a complete JSON object from all cards.
            $container.on('click', '.meta-cards-copy-all-button', function() {
                var allData = {};
                $container.find('.meta-card-copyable').each(function() {
                    var cardKey = $(this).attr('data-copy-key');
                    var cardValue = $(this).attr('data-copy-value');
                    allData[cardKey] = cardValue;
                });
                var jsonString = JSON.stringify(allData, null, 4);
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
