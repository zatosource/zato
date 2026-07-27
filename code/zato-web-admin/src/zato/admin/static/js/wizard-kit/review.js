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

kit.review.config = {

    // The word every group's link into its step is written with
    editLabel: 'Edit',

    // The pointer on a link is answered with that word and the group's own
    // label, shown the way the rest of the pages show a tooltip
    editTooltipTheme: 'dark',
    editTooltipPlacement: 'right',

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

    // The rows of one repeating kind a group opens with - a handful of them
    // read as a list, fifty of them would push the rest of the review off
    // the page, so past the configured count the list scrolls instead.
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

    // The label of a group, which is what the group marks while the pointer
    // is anywhere on it.
    review._getGroupLabel = function(groupElement) {

        var out = $(groupElement).find('.wizard-review-group-label');
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Says on the link what it goes to - the label reads as a heading over the
    // group, so in a sentence it goes on in the lower case it is spoken in.
    review._addEditTooltip = function(editLink, groupLabel) {

        var reviewConfig = kit.review.config;

        tippy(editLink, {
            content: reviewConfig.editLabel + ' ' + groupLabel.toLowerCase(),
            allowHTML: false,
            theme: reviewConfig.editTooltipTheme,
            placement: reviewConfig.editTooltipPlacement,
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

        // The step re-renders whenever it is entered, so the tooltips of the
        // links about to be thrown out go with them
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

            for(var rowIdx = 0; rowIdx < group.rows.length; rowIdx++) {
                groupElement.appendChild(review._buildRow(group.rows[rowIdx]));
            }

            container.append(groupElement);
        }

        // The pointer anywhere on a group marks that group's label with the
        // same badge the data tables put on the row an inline form belongs to.
        // What the honey behind the group does is in the stylesheet - only the
        // badge needs the wrapping a script does.
        container.find('.wizard-review-group').on('mouseenter', function() {
            $.fn.zato.highlight_badge.on(review._getGroupLabel(this));
        });

        container.find('.wizard-review-group').on('mouseleave', function() {
            $.fn.zato.highlight_badge.off(review._getGroupLabel(this));
        });

        // An Edit link goes to the step its group came from and opens
        // whatever the group named, so the answer is there to be changed
        // rather than to be looked for
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
