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
//
// A group's rows are written as if every question were answered - the ones
// still open are marked by the renderer itself, out of the missing targets
// the instance declared in its core config.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var kit = $.fn.zato.wizard_kit;
kit.review = {};

// ////////////////////////////////////////////////////////////////////////

kit.review.config = {

    // The word every group's link into its step is written with
    editLabel: 'Edit',

    // What an answer the wizard cannot be saved without reads as, and what it wears
    missingLabel: 'Missing',
    missingValueClass: 'wizard-review-missing',

    // How the tooltip on a link is shown
    editTooltipTheme: 'dark',
    editTooltipPlacement: 'right',

    // How far off the link the tooltip stands
    editTooltipOffset: [0, 13],

    // How many rows of a group's leading list are on screen before the
    // list scrolls - an instance that wants more or fewer sets this
    listScrollAfter: 2,

    // What the scroll box's height is counted in rows with
    visibleRowsProperty: '--wizard-review-visible-rows'
};

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

    // One [key, value] pair as a row.
    review._buildRow = function(row) {

        var out = document.createElement('div');
        out.className = 'wizard-review-row';

        var key = document.createElement('span');
        key.className = 'wizard-review-key';
        key.textContent = row[0];
        out.appendChild(key);

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
        out.appendChild(value);

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // How the review writes an answer it is waiting for
    review._missingValue = function() {

        var reviewConfig = kit.review.config;
        var out = document.createElement('span');

        out.className = reviewConfig.missingValueClass;
        out.textContent = reviewConfig.missingLabel;

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // The rows of one group with the questions it leaves open said in place -
    // a row already asking one of them says Missing instead of the value it
    // has none of, a question no row mentions is added at the end of the group.
    review._withMissing = function(group, missingList) {

        var out = group.rows.slice();

        for(var entryIdx = 0; entryIdx < missingList.length; entryIdx++) {

            var entry = missingList[entryIdx];

            if(entry.group !== group.label) {
                continue;
            }

            var isRowFound = false;

            for(var rowIdx = 0; rowIdx < out.length; rowIdx++) {
                if(out[rowIdx][0] === entry.label) {
                    out[rowIdx] = [entry.label, review._missingValue()];
                    isRowFound = true;
                }
            }

            if(!isRowFound) {
                out.push([entry.label, review._missingValue()]);
            }
        }

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // The rows of one repeating kind a group opens with - past the configured
    // count they go into a box that scrolls.
    review._buildRowList = function(listRows) {

        var reviewConfig = kit.review.config;
        var visibleCount = reviewConfig.listScrollAfter;

        var out = document.createElement('div');

        if(listRows.length > visibleCount) {
            out.className = 'wizard-review-list';
            out.style.setProperty(reviewConfig.visibleRowsProperty, visibleCount);
        }

        for(var rowIdx = 0; rowIdx < listRows.length; rowIdx++) {
            out.appendChild(review._buildRow(listRows[rowIdx]));
        }

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // The tooltip on a link - Edit and the group the link goes to.
    review._addEditTooltip = function(editLink, groupLabel) {

        var reviewConfig = kit.review.config;

        tippy(editLink, {
            content: reviewConfig.editLabel + ' ' + groupLabel.toLowerCase(),
            allowHTML: false,
            theme: reviewConfig.editTooltipTheme,
            placement: reviewConfig.editTooltipPlacement,
            offset: reviewConfig.editTooltipOffset,
            arrow: true
        });
    };

// ////////////////////////////////////////////////////////////////////////

    // Renders the review step from a list of groups. A group is
    // {label, step, rows}, each row a [key, value] pair, and may also carry:
    //
    //   listRows - rows of one repeating kind, e.g. one per destination,
    //              shown before the rest of the group and scrolling once
    //              there are more of them than the config shows at once
    //   edit     - what to open on the step the Edit link goes to, for a
    //              group whose answers are given in a form rather than on
    //              the step itself
    review.renderGroups = function(groups) {

        var container = $('#' + idPrefix + '-review');

        // Whatever the wizard is still waiting for is read in the section it belongs to
        var missingList = wizard.missingList();

        // The step re-renders on entry, so the old links take their tooltips out
        container.find('.wizard-review-edit').each(function() {
            this._tippy.destroy();
        });

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
            editLink.textContent = kit.review.config.editLabel;
            editLink.setAttribute('data-group', groupIdx);
            header.appendChild(editLink);

            review._addEditTooltip(editLink, group.label);

            groupElement.appendChild(header);

            if(group.listRows && group.listRows.length) {
                groupElement.appendChild(review._buildRowList(group.listRows));
            }

            var rows = review._withMissing(group, missingList);

            for(var rowIdx = 0; rowIdx < rows.length; rowIdx++) {
                groupElement.appendChild(review._buildRow(rows[rowIdx]));
            }

            container.append(groupElement);
        }

        // An Edit link goes to the step its group came from and opens
        // whatever the group named
        container.find('.wizard-review-edit').on('click', function() {

            var group = groups[parseInt(this.getAttribute('data-group'))];
            wizard.goToStep(group.step);

            if(group.edit) {
                group.edit();
            }
        });
    };

// ////////////////////////////////////////////////////////////////////////

};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
