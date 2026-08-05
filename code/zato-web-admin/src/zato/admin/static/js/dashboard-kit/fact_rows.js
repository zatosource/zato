

/* Dashboard kit - the fact rows.
   What is known about one thing, a fact to a line - what it is called on the left, what it says
   on the right, and a way of taking that away which only shows itself once the line is being
   read. Two variants, one for a light panel and one for a dark one. */



(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.fact_rows = {};

    kit.fact_rows.config = {
        copy_label: 'Copy',

        // Offered beside a value other records can be looked up by, as a badge rather than by
        // turning the value into a link
        search_label: 'Search',
        search_title: 'Look for the records carrying this value',

        // Which side of the badge the word saying a value has been taken appears on - beside it,
        // so the line being read is not covered by it
        copy_flash_placement: 'right',

        // The badge each variant wears, so an action on a light panel is not a light badge on
        // a dark one
        badge_classes: {
            'light': 'dashboard-panel-action-badge-light',
            'dark': 'dashboard-panel-action-badge-dark'
        },

        variant_classes: {
            'light': 'dashboard-fact-rows-light',
            'dark': 'dashboard-fact-rows-dark'
        }
    };

    /* One fact - what it is called, what it says as HTML the caller has already made safe,
       what taking it away puts on the clipboard, and what other records can be looked up by
       from it, which is empty for a value nothing is to be found by. */
    kit.fact_rows.row = function(fact, variant) {
        var config = kit.fact_rows.config;

        var out = '<div class="dashboard-fact-row">';

        out += '<div class="dashboard-fact-row-label">' + kit._esc_html(fact.label) + '</div>';
        out += '<div class="dashboard-fact-row-value">';
        out += '<span class="dashboard-fact-row-text">' + fact.value_html + '</span>';

        out += '<span class="dashboard-panel-action-badge ' + config.badge_classes[variant] +
            ' dashboard-fact-row-copy" data-copy-value="' + kit._esc_html(fact.copy_value) + '">' +
            config.copy_label + '</span>';

        // Copy comes first, being offered for every fact, so the row reads the same all the way down
        if (fact.search_value !== '') {
            out += '<span class="dashboard-panel-action-badge ' + config.badge_classes[variant] +
                ' dashboard-fact-row-search" data-search-value="' + kit._esc_html(fact.search_value) +
                '" title="' + config.search_title + '">' + config.search_label + '</span>';
        }

        out += '</div>';
        out += '</div>';

        return out;
    };

    /* A set of facts, read down. `variant` is 'light' or 'dark'. */
    kit.fact_rows.render = function(facts, variant) {
        var config = kit.fact_rows.config;

        var out = '<div class="dashboard-fact-rows ' + config.variant_classes[variant] + '">';

        for (var fact_index = 0; fact_index < facts.length; fact_index++) {
            out += kit.fact_rows.row(facts[fact_index], variant);
        }

        out += '</div>';

        return out;
    };

    $(document).on('click', '.dashboard-fact-row-copy', function(event) {
        event.stopPropagation();

        var value = $(this).attr('data-copy-value');
        kit.copy_to_clipboard(this, value, kit.fact_rows.config.copy_flash_placement);
    });
})();
