

/* Dashboard kit - chips.
   A chip is one small labelled value a record carries - a message type, a patient number,
   an acknowledgment code. Its tone says what it means and its colours live in the stylesheet,
   so nothing here writes a colour of its own. */



(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.chips = {};

    /* The tone a chip is given, and the class that colours it. */
    kit.chips.tone_classes = {
        'neutral': 'dashboard-tag-neutral',
        'accent': 'dashboard-tag-accent',
        'good': 'dashboard-tag-good',
        'bad': 'dashboard-tag-bad',
        'warn': 'dashboard-tag-warn',
        'muted': 'dashboard-tag-muted'
    };

    /* One chip - {label, value, tone, key}. The key and the value travel on the element
       so whatever is listening can act on the chip by name. A chip whose label is empty
       shows its value alone, `text` shows in place of the value when the value is a code
       the reader is not to be shown, and `value_html` is pre-rendered display markup
       (already escaped by its maker) for values with markup of their own inside. */
    kit.chips.render_one = function(chip) {
        var tone_class = kit.chips.tone_classes[chip.tone];
        var escaped_value = kit._esc_html(chip.value);

        var display_html;

        if (chip.value_html !== undefined) {
            display_html = chip.value_html;
        }
        else if (chip.text !== undefined) {
            display_html = kit._esc_html(chip.text);
        }
        else {
            display_html = escaped_value;
        }

        var html = '<span class="detail-tag dashboard-chip ' + tone_class + '"';
        html += ' data-chip-key="' + kit._esc_html(chip.key) + '"';
        html += ' data-chip-value="' + escaped_value + '">';

        // The space is part of the markup, not a margin, so the label and the value
        // stay apart on any page whatever stylesheets it happens to load
        if (chip.label !== '') {
            html += kit._esc_html(chip.label) + ' ';
        }

        html += '<span class="dashboard-chip-value">' + display_html + '</span>';
        html += '</span>';

        return html;
    };

    kit.chips.render = function(chips) {
        var html = '';

        for (var chip_index = 0; chip_index < chips.length; chip_index++) {
            html += kit.chips.render_one(chips[chip_index]);
        }

        return html;
    };
})();
