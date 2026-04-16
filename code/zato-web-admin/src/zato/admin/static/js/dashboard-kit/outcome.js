
/* Dashboard kit - outcome helpers.
   Injectable palette-driven helpers for rendering small status dots,
   per-run outcome squares, and tinted outcome badges. The scheduler
   dashboard uses them with its {ok, error, timeout, skipped_concurrent,
   missed_catchup} palette; any other dashboard can plug its own. */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var ns = $.fn.zato.dashboard_kit;
    ns.outcome = {};

    /* Build an outcome palette object. `palette.bar_colors`, `.colors`,
       `.bg_colors`, `.labels` are plain maps keyed by outcome key, and
       every helper below closes over the palette passed in. */
    ns.outcome.make_palette = function(palette) {
        return {
            colors:     palette.colors     || {},
            bg_colors:  palette.bg_colors  || {},
            bar_colors: palette.bar_colors || {},
            labels:     palette.labels     || {}
        };
    };

    /* Render the fixed-size coloured squares showing the last N
       outcomes for a given run list. Unknown keys fall back to a neutral
       grey. */
    ns.outcome.squares = function(recent_outcomes, palette) {
        if (!recent_outcomes || recent_outcomes.length === 0) {
            return '<span style="color:#a0a0a5">-</span>';
        }
        var bar_colors = palette.bar_colors || {};
        var labels = palette.labels || {};
        var html = '';
        for (var index = 0; index < recent_outcomes.length; index++) {
            var outcome = recent_outcomes[index];
            var color = bar_colors[outcome] || '#ccc';
            var label = labels[outcome] || outcome;
            html += '<span class="dashboard-outcome-square" style="background:' + color + '" title="' + label + '"></span>';
        }
        return html;
    };

    /* Render a pill-shaped badge with a tinted background (used in the
       Recent failures table). */
    ns.outcome.badge = function(outcome, palette) {
        var colors = palette.colors || {};
        var bg_colors = palette.bg_colors || {};
        var labels = palette.labels || {};
        var color = colors[outcome] || '#6e6e73';
        var bg = bg_colors[outcome] || 'rgba(110,110,115,0.12)';
        var label = labels[outcome] || outcome;
        return '<span class="dashboard-outcome-badge" style="color:' + color + ';background:' + bg + '">' + label + '</span>';
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
