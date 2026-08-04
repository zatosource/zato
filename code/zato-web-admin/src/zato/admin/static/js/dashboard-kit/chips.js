

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
       so whatever is listening can act on the chip by name. */
    kit.chips.render_one = function(chip) {
        var tone_class = kit.chips.tone_classes[chip.tone];
        var escaped_value = kit._esc_html(chip.value);

        var html = '<span class="detail-tag dashboard-chip ' + tone_class + '"';
        html += ' data-chip-key="' + kit._esc_html(chip.key) + '"';
        html += ' data-chip-value="' + escaped_value + '">';
        html += kit._esc_html(chip.label);
        html += '<span class="dashboard-chip-value">' + escaped_value + '</span>';
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
