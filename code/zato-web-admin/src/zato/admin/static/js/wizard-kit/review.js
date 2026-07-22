// Wizard kit - card summaries and the review step renderer.
//
// Every card on a wizard step may carry a one-line summary of what is
// currently configured, recomputed from the form each time a micro-form
// closes. The review step renders the same data as grouped rows, each
// group with an Edit link that jumps back to the step the answers came
// from.
//
// ---------------------------------------------------------------
// How to use
// ---------------------------------------------------------------
//
// The instance hands its namespace over after core.setup ran:
//
//      $.fn.zato.wizard_kit.review.setup(wizard);
//
// and then builds on what setup installed:
//
//      wizard.review.setSummary('my-wizard-summary-logging', 'Errors returned');
//
//      wizard.review.render = function() {
//          wizard.review.renderGroups([
//              {label: 'Basics', step: 0, rows: [['Name', 'abc']]}
//          ]);
//      };
//
// A row is a [key, value] pair - the value is usually text but may also be
// a ready DOM Node, e.g. a badge. The instance must define render() and
// refreshSummaries() itself - the kit only provides the building blocks.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var kit = $.fn.zato.wizard_kit;
kit.review = {};

// ////////////////////////////////////////////////////////////////////////

kit.review.setup = function(wizard) {

    var review = wizard.review;
    var idPrefix = wizard.config.idPrefix;

// ////////////////////////////////////////////////////////////////////////

    // Sets a card summary, replaying its fade-in when the text changed.
    review.setSummary = function(elementId, text) {

        var element = $('#' + elementId);

        if(element.text() === text) {
            return;
        }

        element.removeClass('wizard-summary-fresh');
        element.text(text);

        // Reflowing between the class removal and re-add restarts the animation
        void element[0].offsetWidth;
        element.addClass('wizard-summary-fresh');
    };

// ////////////////////////////////////////////////////////////////////////

    // Renders the review step from a list of groups - each group is
    // {label, step, rows}, each row a [key, value] pair.
    review.renderGroups = function(groups) {

        var container = $('#' + idPrefix + '-review');
        container.empty();

        for(var groupIdx = 0; groupIdx < groups.length; groupIdx++) {
            var group = groups[groupIdx];

            var groupElement = document.createElement('div');
            groupElement.className = 'wizard-review-group';

            var header = document.createElement('div');
            header.className = 'wizard-review-group-header';

            var headerLabel = document.createElement('span');
            headerLabel.className = 'wizard-review-group-label';
            headerLabel.textContent = group.label;
            header.appendChild(headerLabel);

            var editLink = document.createElement('span');
            editLink.className = 'wizard-review-edit';
            editLink.textContent = 'Edit';
            editLink.setAttribute('data-step', group.step);
            header.appendChild(editLink);

            groupElement.appendChild(header);

            for(var rowIdx = 0; rowIdx < group.rows.length; rowIdx++) {
                var row = group.rows[rowIdx];

                var rowElement = document.createElement('div');
                rowElement.className = 'wizard-review-row';

                var key = document.createElement('span');
                key.className = 'wizard-review-key';
                key.textContent = row[0];
                rowElement.appendChild(key);

                var value = document.createElement('span');
                value.className = 'wizard-review-value';

                // A value is usually text, but rows like a badge
                // bring a ready element of their own
                if(row[1] instanceof Node) {
                    value.appendChild(row[1]);
                }
                else {
                    value.textContent = row[1];
                }
                rowElement.appendChild(value);

                groupElement.appendChild(rowElement);
            }

            container.append(groupElement);
        }

        // The Edit links jump back to the step their group came from
        container.find('.wizard-review-edit').on('click', function() {
            wizard.goToStep(parseInt(this.getAttribute('data-step')));
        });
    };

// ////////////////////////////////////////////////////////////////////////

};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
