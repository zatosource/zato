

// Dashboard kit - the journey strip, one thing's steps read left to right with the time each took and the time between them.

(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.journey = {};

    kit.journey.config = {

        stateClasses: {
            'done': 'dashboard-journey-step-done',
            'failed': 'dashboard-journey-step-failed',
            'skipped': 'dashboard-journey-step-skipped',
            'pending': 'dashboard-journey-step-pending',
            'warn': 'dashboard-journey-step-warning',
            'running': 'dashboard-journey-step-running'
        },

        variantClasses: {
            'light': 'dashboard-journey-light',
            'dark': 'dashboard-journey-dark'
        },

        // Past this many foldable steps the rest fold into one step that opens on click.
        foldAfter: 3,
        foldLabel: '+{count} more'
    };

    // ////////////////////////////////////////////////////////////////////////

    // One step of {label, state, durationText, eventId, title, isFoldable}, a step with an event is selectable.
    kit.journey.stepHTML = function(step, isHidden) {
        var config = kit.journey.config;

        var classes = 'dashboard-journey-step ' + config.stateClasses[step.state];

        if (step.eventId !== 0) {
            classes += ' dashboard-journey-step-selectable';
        }

        var out = '<span class="' + classes + '" data-event-id="' + step.eventId + '"';

        if (isHidden) {
            out += ' hidden data-folded="1"';
        }

        if (step.title !== '') {
            out += ' title="' + kit._esc_html(step.title) + '"';
        }

        out += '>';
        out += '<span class="dashboard-journey-step-label">' + kit._esc_html(step.label) + '</span>';

        if (step.durationText !== '') {
            out += '<span class="dashboard-journey-step-duration">' + kit._esc_html(step.durationText) + '</span>';
        }

        out += '</span>';

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    // The connector between two steps, gapText is how long passed between them.
    kit.journey.connectorHTML = function(gapText, isHidden) {
        var out = '<span class="dashboard-journey-connector"';

        if (isHidden) {
            out += ' hidden data-folded="1"';
        }

        out += '>';

        if (gapText !== '') {
            out += '<span class="dashboard-journey-gap">' + kit._esc_html(gapText) + '</span>';
        }

        out += '</span>';

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    // The strip of {steps, variant}, every step carries gapText and isFoldable.
    kit.journey.render = function(journey) {
        var config = kit.journey.config;

        var out = '<div class="dashboard-journey ' + config.variantClasses[journey.variant] + '">';

        var foldableSeen = 0;
        var foldedCount = 0;

        for (var stepIndex = 0; stepIndex < journey.steps.length; stepIndex++) {
            var step = journey.steps[stepIndex];
            var isHidden = false;

            if (step.isFoldable) {
                foldableSeen += 1;

                if (foldableSeen > config.foldAfter) {
                    isHidden = true;
                    foldedCount += 1;
                }
            }

            if (stepIndex > 0) {
                out += kit.journey.connectorHTML(step.gapText, isHidden);
            }

            out += kit.journey.stepHTML(step, isHidden);
        }

        if (foldedCount > 0) {
            out += kit.journey.connectorHTML('', false);
            out += '<span class="dashboard-journey-step dashboard-journey-step-pending dashboard-journey-fold">' +
                '<span class="dashboard-journey-step-label">' +
                config.foldLabel.replace('{count}', String(foldedCount)) + '</span></span>';
        }

        out += '</div>';

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    // The folded steps open and the fold goes away.
    $(document).on('click', '.dashboard-journey-fold', function(event) {
        event.stopPropagation();

        var $fold = $(this);
        var $journey = $fold.closest('.dashboard-journey');

        $journey.find('[data-folded="1"]').prop('hidden', false);
        $fold.prev('.dashboard-journey-connector').remove();
        $fold.remove();
    });
})();
