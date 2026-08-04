

/* Dashboard kit - the outcome palette.
   Every screen that reports how something turned out reads its colours and its labels here,
   so one outcome looks the same wherever it is shown. */



(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.palette = {};

    kit.palette.outcome = {

        // The badge text colours
        colors: {
            'ok': '#2a7fbf',
            'error': '#e0226e',
            'expired': '#b35e00',
            'timeout': '#b35e00',
            'running': '#888',
            'skipped_already_in_flight': '#7b5ea7'
        },

        // The badge backgrounds behind those colours
        backgrounds: {
            'ok': 'rgba(42, 127, 191, 0.12)',
            'error': 'rgba(224, 34, 110, 0.12)',
            'expired': 'rgba(179, 94, 0, 0.12)',
            'timeout': 'rgba(179, 94, 0, 0.12)',
            'running': 'rgba(136, 136, 136, 0.12)',
            'skipped_already_in_flight': 'rgba(123, 94, 167, 0.12)'
        },

        // The stronger colours a chart draws its bars in
        bar_colors: {
            'ok': '#3a9ad9',
            'error': '#c0392b',
            'expired': '#b45309',
            'timeout': '#b45309',
            'running': '#aaa',
            'skipped_already_in_flight': '#6b4d94'
        },

        // The washed-out ends of those bars
        bar_tints: {
            'ok': '#d1e8f8',
            'error': '#f5d5d2',
            'expired': '#fde8cd',
            'timeout': '#fde8cd',
            'running': '#e0e0e0',
            'skipped_already_in_flight': '#ddd0ef'
        },

        labels: {
            'ok': 'OK',
            'error': 'Error',
            'expired': 'Expired',
            'timeout': 'Timeout',
            'running': 'Running',
            'skipped_already_in_flight': 'Skipped (already in flight)'
        },

        short_labels: {
            'skipped_already_in_flight': 'Skipped'
        },

        tooltips: {
            'skipped_already_in_flight': 'Skipped because run #{ctx} was already in flight'
        }
    };

    /* The palette in the shape kit.outcome.badge and kit.build_legend take. */
    kit.palette.outcome_palette = {
        colors: kit.palette.outcome.colors,
        backgrounds: kit.palette.outcome.backgrounds,
        bar_colors: kit.palette.outcome.bar_colors,
        labels: kit.palette.outcome.labels,
        short_labels: kit.palette.outcome.short_labels,
        tooltips: kit.palette.outcome.tooltips
    };
})();
