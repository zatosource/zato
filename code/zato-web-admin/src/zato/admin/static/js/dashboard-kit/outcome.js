
/* Dashboard kit - outcome helpers.
   Injectable palette-driven helpers for rendering small status dots,
   per-run outcome squares, and tinted outcome badges. Each dashboard
   plugs its own palette (colors, labels, short_labels, tooltips). */



(function() {
    var ns = $.fn.zato.dashboard_kit;
    ns.outcome = {};

    ns.outcome.css_classes = {
        'ok': 'dashboard-outcome-ok',
        'error': 'dashboard-outcome-error',
        'timeout': 'dashboard-outcome-timeout',
        'running': 'dashboard-outcome-running',
        'skipped_already_in_flight': 'dashboard-outcome-skipped'
    };

    /* Build an outcome palette object. `palette.bar_colors`, `.colors`,
       `.backgrounds`, `.labels` are plain maps keyed by outcome key, and
       every helper below closes over the palette passed in. */
    ns.outcome.make_palette = function(palette) {
        return {
            colors:       palette.colors,
            backgrounds:    palette.backgrounds,
            bar_colors:   palette.bar_colors,
            labels:       palette.labels,
            short_labels: palette.short_labels,
            tooltips:     palette.tooltips
        };
    };

    /* Render the fixed-size coloured squares showing the last N
       outcomes for a given run list. */
    ns.outcome.squares = function(recent_outcomes, palette) {
        if (!recent_outcomes || recent_outcomes.length === 0) {
            return '<span style="color:#a0a0a5">-</span>';
        }
        var bar_colors = palette.bar_colors;
        var labels = palette.labels;
        var html = '';
        for (var index = 0; index < recent_outcomes.length; index++) {
            var outcome = recent_outcomes[index];
            var color = bar_colors[outcome];
            var label = labels[outcome];
            html += '<span class="dashboard-outcome-square" style="background:' + color + '" title="' + label + '"></span>';
        }
        return html;
    };

    /* Render a pill-shaped badge with a tinted background.
       Optional record param enables short_labels and tooltips from the palette. */
    ns.outcome.badge = function(outcome, palette, record) {
        var label = palette.labels[outcome];
        var tooltip_attr = '';
        var css_class = ns.outcome.css_classes[outcome];

        if (record) {
            if (palette.short_labels[outcome]) {
                label = palette.short_labels[outcome];
            }
            if (record.outcome_ctx !== null) {
                if (palette.tooltips[outcome]) {
                    var tooltip_text = palette.tooltips[outcome].replace('{ctx}', record.outcome_ctx);
                    tooltip_attr = ' data-tippy-content="' + tooltip_text + '"';
                }
            }
        }

        var prefix = outcome === 'running' ? '<span class="badge-running-spinner"></span>' : '';
        return '<span class="dashboard-outcome-badge ' + css_class + '"' + tooltip_attr + '>' + prefix + label + '</span>';
    };

    /* Render a small status dot. `state` is one of 'running', 'paused',
       'failed', 'ok' (the caller is expected to resolve the state from
       its own domain model - e.g. is_running vs last_outcome). */
    ns.outcome.status_dot = function(state, title) {
        var cls;
        switch (state) {
            case 'running': cls = 'dashboard-status-running'; break;
            case 'paused':  cls = 'dashboard-status-paused';  break;
            case 'failed':  cls = 'dashboard-status-failed';  break;
            default:        cls = 'dashboard-status-ok';      break;
        }
        var title_attr = title ? ' title="' + title + '"' : '';
        return '<span class="dashboard-status-dot ' + cls + '"' + title_attr + '></span>';
    };
})();
