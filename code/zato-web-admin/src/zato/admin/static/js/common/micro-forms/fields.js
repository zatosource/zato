// Micro-forms - the header, the help badge and the field rows of a
// micro-form page. Loaded after micro-forms/core.js, which calls
// installFields from setup.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var microForms = $.fn.zato.micro_forms;

// ////////////////////////////////////////////////////////////////////////

microForms.installFields = function(host, forms) {

// ////////////////////////////////////////////////////////////////////////

    // Builds a popover header - the shared grip glyph plus the text, acting
    // as the drag handle every micro-form shares.
    forms.buildTitle = function(text) {

        var title = document.createElement('div');
        title.className = 'zato-popup-header';
        title.appendChild($.fn.zato.popup.build_grip());
        title.appendChild(document.createTextNode(text));

        var out = title;
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // The "How does it work?" badge every popover shows next to its buttons.
    forms.buildHelpBadge = function() {

        var formsConfig = forms.config;

        var badge = document.createElement('span');
        badge.className = 'how-it-works-badge';
        badge.id = formsConfig.helpBadgeId;
        badge.textContent = formsConfig.helpBadgeLabel;

        var out = badge;
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Wires up the help badge of one popover. Tippy attaches the popover to
    // the document only when it shows, so this runs after showTippy and again
    // whenever an open popover re-renders its fields.
    forms.initHelp = function(container) {

        var formsConfig = forms.config;

        if(!formsConfig.showHowItWorks) {
            return;
        }

        if(!container.isConnected) {
            return;
        }

        // A help session left over from the page or from an earlier render
        // of this popover points at elements that just went away
        if($.fn.zato.how_it_works._state) {
            $.fn.zato.how_it_works._deactivate();
        }

        $.fn.zato.how_it_works.init({
            badgeId: formsConfig.helpBadgeId,
            divId: '#' + formsConfig.popupId,
            containerSelector: '.micro-form',
            fieldSelector: '.micro-form-field',
            placement: formsConfig.helpPlacement,
            descriptions: host.helpDescriptions()
        });
    };

// ////////////////////////////////////////////////////////////////////////

    // Keeps a unit select reading with its count - `1 hour`, `2 hours`, `1.5 millions`. An option's value is the
    // noun in the singular and its label the plural. Returns the relabel function.
    forms.bindUnitLabels = function(countInput, unitSelect) {

        var pluralAttr = forms.config.unitPluralAttr;

        // A select is as wide as its widest label, so it would shrink as `millions` turns into `million`
        // and pull the popover in with it - once it is on the page it is made as wide as its plurals
        // need and stays that wide whatever the count says
        var lockWidth = function() {

            if(unitSelect.style.width !== '') {
                return;
            }

            // A select of a kit of its own, e.g. a time slot's, has its options refilled as the slot
            // changes and sits in a popover with a width of its own, so it keeps sizing itself
            if(!unitSelect.classList.contains('micro-form-unit')) {
                return;
            }

            // Not on the page yet, so there is no width to read
            if(!unitSelect.isConnected) {
                return;
            }

            var options = unitSelect.querySelectorAll('option');

            for(var idx = 0; idx < options.length; idx++) {
                options[idx].textContent = options[idx].getAttribute(pluralAttr);
            }

            unitSelect.style.width = unitSelect.offsetWidth + 'px';
        };

        var relabel = function() {

            // An emptied input shows its placeholder, which is the count the select reads with
            var countText = countInput.value;
            if(countText === '') {
                countText = countInput.placeholder;
            }

            // One alone is singular - a fraction of one is not
            var isOne = parseFloat(countText) === 1;
            var options = unitSelect.querySelectorAll('option');

            for(var idx = 0; idx < options.length; idx++) {
                var option = options[idx];

                if(!option.hasAttribute(pluralAttr)) {
                    option.setAttribute(pluralAttr, option.textContent);
                }
            }

            lockWidth();

            for(idx = 0; idx < options.length; idx++) {
                var relabelled = options[idx];

                if(isOne) {
                    relabelled.textContent = relabelled.value;
                }
                else {
                    relabelled.textContent = relabelled.getAttribute(pluralAttr);
                }
            }
        };

        countInput.addEventListener('input', relabel);
        relabel();

        // The popover relabels every unit select once it is on the page, which is when the width can be locked
        unitSelect.relabelUnits = relabel;

        var out = relabel;
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Locks the width of every unit select of a popover that is on the page - see bindUnitLabels
    forms.lockUnitWidths = function(container) {

        container.querySelectorAll('select.micro-form-unit').forEach(function(unitSelect) {
            unitSelect.relabelUnits();
        });
    };

// ////////////////////////////////////////////////////////////////////////

    // Builds one input row of a micro-form page, seeded from the Django form.
    forms._buildFieldRow = function(fieldSpec) {

        var row = document.createElement('div');
        row.className = 'micro-form-field';

        // The kinds the instance registered come first - e.g. composite
        // rows like MLLP's security list
        var kindHandler = forms._kinds[fieldSpec.kind];
        if(kindHandler) {
            kindHandler.build(fieldSpec, row);

            var out = row;
            return out;
        }

        var formField = host.field(fieldSpec.field);
        var inputId = forms.inputId(fieldSpec.field);

        // A checkbox carries its slider at the end of the line the label takes ..
        if(fieldSpec.kind === 'checkbox') {
            if(!fieldSpec.labelAbove) {
                var checkboxLabel = document.createElement('label');
                checkboxLabel.className = 'micro-form-checkbox';
                checkboxLabel.setAttribute('for', inputId);

                var checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = inputId;
                checkbox.checked = formField.prop('checked');

                var checkboxText = document.createElement('span');
                checkboxText.className = 'micro-form-checkbox-text';
                checkboxText.textContent = fieldSpec.label;

                checkboxLabel.appendChild(checkboxText);
                checkboxLabel.appendChild(checkbox);
                row.appendChild(checkboxLabel);

                var out = row;
                return out;
            }
        }

        // .. everything else has the label above the input.
        var label = document.createElement('label');
        label.className = 'micro-form-label';
        label.setAttribute('for', inputId);
        label.textContent = fieldSpec.label;
        row.appendChild(label);

        var input;

        // A switch under a label of its own, like the inputs it shares a row with
        if(fieldSpec.kind === 'checkbox') {
            input = document.createElement('input');
            input.type = 'checkbox';
            input.id = inputId;
            input.className = 'micro-form-switch';
            input.checked = formField.prop('checked');
        }
        else if(fieldSpec.kind === 'select') {

            // The choices are cloned from the Django select, the single source of options
            input = document.createElement('select');
            input.id = inputId;

            formField.find('option').each(function() {
                var option = document.createElement('option');
                option.value = this.value;
                option.textContent = this.textContent;
                input.appendChild(option);
            });
            input.value = formField.val();
        }
        else {
            input = document.createElement('input');
            input.id = inputId;
            input.value = formField.val();

            // A count is stepped with the arrows the browser puts on a
            // number field, and it is only ever as wide as a count needs
            if(fieldSpec.kind === 'number') {
                input.type = 'number';
                input.className = 'micro-form-number';
                input.min = forms.config.numberMin;

                // A fractional count - 7.5 seconds, 2.5 millions - steps by its spec's step and may go below one
                if(fieldSpec.fractional) {
                    input.step = fieldSpec.step;
                    input.min = forms.config.fractionalMin;
                }
            }
            else {
                input.type = 'text';
            }

            if(fieldSpec.placeholder) {
                input.placeholder = fieldSpec.placeholder;
            }
        }

        // Fields like max message size keep their unit select right next to the value
        if(fieldSpec.unitField) {
            var inputRow = document.createElement('div');
            inputRow.className = 'micro-form-input-row';
            inputRow.appendChild(input);

            var unitFormField = host.field(fieldSpec.unitField);
            var unitSelect = document.createElement('select');
            unitSelect.id = forms.inputId(fieldSpec.unitField);
            unitSelect.className = 'micro-form-unit';

            unitFormField.find('option').each(function() {
                var unitOption = document.createElement('option');
                unitOption.value = this.value;
                unitOption.textContent = this.textContent;
                unitSelect.appendChild(unitOption);
            });
            unitSelect.value = unitFormField.val();
            forms.bindUnitLabels(input, unitSelect);

            inputRow.appendChild(unitSelect);
            row.appendChild(inputRow);
        }
        else {
            row.appendChild(input);
        }

        if(fieldSpec.hint) {
            var hint = document.createElement('div');
            hint.className = 'micro-form-hint';
            hint.textContent = fieldSpec.hint;
            row.appendChild(hint);
        }

        var out = row;
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
