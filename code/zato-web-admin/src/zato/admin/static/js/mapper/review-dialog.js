
// Mapper kit - the review dialog.
// One modal for every change that must never apply silently: auto-map
// suggestions, field renames propagating into expressions and schema
// re-import diffs. Each item carries its own checkbox for per-item
// accept, a toggle-all button covers the bulk case, and nothing at
// all happens on Cancel.

(function($) {

    zato.mapper.reviewDialog = {};

// ////////////////////////////////////////////////////////////////////////

    function buildChangeLine(before, after) {

        var change = document.createElement('div');
        change.className = 'mapper-review-item-change';

        var beforeText = document.createElement('span');
        beforeText.className = 'mapper-review-item-before';
        beforeText.textContent = before;
        change.appendChild(beforeText);

        var arrow = document.createElement('span');
        arrow.className = 'mapper-review-item-arrow';
        var arrowIcon = document.createElement('i');
        arrowIcon.setAttribute('data-lucide', 'arrow-right');
        arrow.appendChild(arrowIcon);
        change.appendChild(arrow);

        var afterText = document.createElement('span');
        afterText.className = 'mapper-review-item-after';
        afterText.textContent = after;
        change.appendChild(afterText);

        return change;
    }

// ////////////////////////////////////////////////////////////////////////

    // Builds one item row. Bindings collect {checkbox, item} pairs so
    // the accept handler can read the final checked states back.
    function buildItem(item, bindings) {

        var row = document.createElement('li');
        row.className = 'mapper-review-item';

        var label = document.createElement('label');
        label.className = 'mapper-review-item-header';

        var checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'mapper-review-checkbox';
        checkbox.checked = item.checked;
        label.appendChild(checkbox);

        var labelText = document.createElement('span');
        labelText.className = 'mapper-review-item-label';

        // An item carries either a source-to-target pair, drawn with
        // an SVG arrow between the two, or one plain label.
        if (item.source !== undefined) {
            var sourceText = document.createElement('span');
            sourceText.textContent = item.source;
            labelText.appendChild(sourceText);

            var arrowIcon = document.createElement('i');
            arrowIcon.setAttribute('data-lucide', 'arrow-right');
            labelText.appendChild(arrowIcon);

            var targetText = document.createElement('span');
            targetText.textContent = item.target;
            labelText.appendChild(targetText);
        }
        else {
            labelText.textContent = item.label;
        }

        label.appendChild(labelText);

        if (item.note !== '') {
            var note = document.createElement('span');
            note.className = 'dashboard-outcome-badge mapper-review-item-note';
            note.textContent = item.note;
            label.appendChild(note);
        }

        row.appendChild(label);

        bindings.push({checkbox: checkbox, item: item});

        if (item.before !== '') {
            row.appendChild(buildChangeLine(item.before, item.after));
        }

        for (var detailIdx = 0; detailIdx < item.details.length; detailIdx++) {
            var detail = document.createElement('div');
            detail.className = 'mapper-review-item-detail';
            detail.textContent = item.details[detailIdx];
            row.appendChild(detail);
        }

        // Child items live and die with their parent - unchecking the
        // parent disables them, since they cannot apply without it.
        if (item.children.length > 0) {
            var childList = document.createElement('ul');
            childList.className = 'mapper-review-children';

            var childCheckboxes = [];
            for (var childIdx = 0; childIdx < item.children.length; childIdx++) {
                var childRow = buildItem(item.children[childIdx], bindings);
                childList.appendChild(childRow);

                var lastBinding = bindings[bindings.length - 1];
                childCheckboxes.push(lastBinding.checkbox);
            }

            row.appendChild(childList);

            $(checkbox).on('change', function() {
                for (var boxIdx = 0; boxIdx < childCheckboxes.length; boxIdx++) {
                    childCheckboxes[boxIdx].disabled = !checkbox.checked;
                }
                $(childList).toggleClass('mapper-review-children-disabled', !checkbox.checked);
            });
        }

        return row;
    }

// ////////////////////////////////////////////////////////////////////////

    // Fills in the keys an item may omit, so the renderer and the
    // accept handler always see one complete shape.
    function normalizeItem(item) {

        if (item.note === undefined) {
            item.note = '';
        }
        if (item.before === undefined) {
            item.before = '';
        }
        if (item.after === undefined) {
            item.after = '';
        }
        if (item.details === undefined) {
            item.details = [];
        }
        if (item.checked === undefined) {
            item.checked = true;
        }
        if (item.children === undefined) {
            item.children = [];
        }

        for (var childIdx = 0; childIdx < item.children.length; childIdx++) {
            normalizeItem(item.children[childIdx]);
        }
    }

// ////////////////////////////////////////////////////////////////////////

    // Opens the review dialog.
    // reviewConfig:
    //   title:     heading text
    //   intro:     one explanatory line under the heading, or ''
    //   emptyText: shown instead of the list when there are no items -
    //              the dialog then only offers Close
    //   okLabel:   text of the accept button
    //   items:     [{label, note, before, after, details, checked, children}]
    //   onAccept:  called with the items, their checked flags updated
    zato.mapper.reviewDialog.open = function(reviewConfig) {

        var overlay = document.createElement('div');
        overlay.className = 'mapper-dialog-overlay';

        var dialog = document.createElement('div');
        dialog.className = 'mapper-dialog mapper-review-dialog';
        dialog.setAttribute('role', 'dialog');

        var title = document.createElement('h2');
        title.className = 'mapper-dialog-title';
        title.textContent = reviewConfig.title;
        dialog.appendChild(title);

        var buttons = document.createElement('div');
        buttons.className = 'mapper-dialog-buttons';

        function close() {
            $(overlay).remove();
        }

        // With nothing to review the dialog says so and only closes -
        // a designed empty state, never a blank pane.
        if (reviewConfig.items.length === 0) {

            var empty = document.createElement('p');
            empty.className = 'mapper-review-empty';
            empty.textContent = reviewConfig.emptyText;
            dialog.appendChild(empty);

            var closeButton = document.createElement('button');
            closeButton.className = 'mapper-button zato-action-button mapper-button-confirm';
            closeButton.type = 'button';
            closeButton.textContent = 'Close';
            buttons.appendChild(closeButton);

            dialog.appendChild(buttons);
            overlay.appendChild(dialog);
            document.body.appendChild(overlay);

            $(closeButton).on('click', close);
            closeButton.focus();

            $(overlay).on('keydown', function(event) {
                if (event.key === 'Escape') {
                    close();
                }
            });

            return;
        }

        if (reviewConfig.intro !== '') {
            var intro = document.createElement('p');
            intro.className = 'mapper-review-intro';
            intro.textContent = reviewConfig.intro;
            dialog.appendChild(intro);
        }

        for (var itemIdx = 0; itemIdx < reviewConfig.items.length; itemIdx++) {
            normalizeItem(reviewConfig.items[itemIdx]);
        }

        // Toggle all serves the bulk case - one click checks or
        // unchecks every box, children included.
        var toggleAll = document.createElement('button');
        toggleAll.className = 'mapper-button zato-action-button mapper-review-toggle-all';
        toggleAll.type = 'button';
        toggleAll.textContent = 'Toggle all';
        dialog.appendChild(toggleAll);

        var list = document.createElement('ul');
        list.className = 'mapper-review-list';

        var bindings = [];
        for (var rowIdx = 0; rowIdx < reviewConfig.items.length; rowIdx++) {
            list.appendChild(buildItem(reviewConfig.items[rowIdx], bindings));
        }

        dialog.appendChild(list);

        var cancelButton = document.createElement('button');
        cancelButton.className = 'mapper-button zato-action-button';
        cancelButton.type = 'button';
        cancelButton.textContent = 'Cancel';
        buttons.appendChild(cancelButton);

        var okButton = document.createElement('button');
        okButton.className = 'mapper-button zato-action-button mapper-button-confirm';
        okButton.type = 'button';
        okButton.textContent = reviewConfig.okLabel;
        buttons.appendChild(okButton);

        dialog.appendChild(buttons);
        overlay.appendChild(dialog);
        document.body.appendChild(overlay);

        // The change-line arrow placeholders become inline SVGs.
        lucide.createIcons();

        $(toggleAll).on('click', function() {

            // The first box decides the direction for all of them.
            var newChecked = !bindings[0].checkbox.checked;

            for (var bindingIdx = 0; bindingIdx < bindings.length; bindingIdx++) {
                var box = bindings[bindingIdx].checkbox;
                box.checked = newChecked;
                box.disabled = false;
                $(box).trigger('change');
            }
        });

        $(cancelButton).on('click', close);

        $(okButton).on('click', function() {

            // The checked flags flow back into the items - a disabled
            // child counts as unchecked, it cannot apply on its own.
            for (var bindingIdx = 0; bindingIdx < bindings.length; bindingIdx++) {
                var binding = bindings[bindingIdx];
                binding.item.checked = binding.checkbox.checked && !binding.checkbox.disabled;
            }

            zato.mapper.log('review-dialog', 'accepted', {title: reviewConfig.title});

            close();
            reviewConfig.onAccept(reviewConfig.items);
        });

        // Escape cancels, exactly like the Cancel button.
        $(overlay).on('keydown', function(event) {
            if (event.key === 'Escape') {
                close();
            }
        });

        okButton.focus();
    };

})(jQuery);
