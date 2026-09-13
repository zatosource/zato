
// /////////////////////////////////////////////////////////////////////////////
//
// Alerts tab - the chips kind of its popovers, for a text field that is a list of names such as
// the status codes or the SOAP fault codes a connection alerts on. Each name is a chip with a
// cross that removes it, a new one is typed into the input after the chips and added with Enter or
// a comma, and the hidden field keeps the names joined with a comma and a space, as they were typed
// before there were chips. Loads before common/alerts-tab.js.
//
// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.alerts_tab');

$.fn.zato.alerts_tab.chipsConfig = {

    // The classes of the chips kit
    fieldClass: 'alerts-tab-chips-field',
    listClass: 'alerts-tab-chips',
    chipClass: 'alerts-tab-chip',
    chipTextClass: 'alerts-tab-chip-text',
    removeClass: 'alerts-tab-chip-remove',
    inputClass: 'alerts-tab-chips-input',

    // What the input after the chips says while it is empty
    addPlaceholder: 'Type and press Enter',

    // The cross on a chip and what it says on hover
    removeGlyph: '\u00d7',
    removeTitle: 'Remove',

    // The keys that turn what was typed into a chip
    addKeys: ['Enter', ','],

    // How the names are split when read off the hidden field and joined when written back
    splitPattern: /\s*,\s*/,
    joinText: ', '
}

// /////////////////////////////////////////////////////////////////////////////

// The names a hidden field holds, in their order, without the blanks a trailing comma leaves
$.fn.zato.alerts_tab.chipNames = function(text) {

    var config = $.fn.zato.alerts_tab.chipsConfig;
    var out = [];

    text.split(config.splitPattern).forEach(function(name) {
        var trimmed = name.trim();
        if(trimmed) {
            out.push(trimmed);
        }
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// One chip - the name and the cross that removes it
$.fn.zato.alerts_tab.buildChip = function(name, onRemove) {

    var config = $.fn.zato.alerts_tab.chipsConfig;

    var chip = document.createElement('span');
    chip.className = config.chipClass;
    chip.dataset.name = name;

    var text = document.createElement('span');
    text.className = config.chipTextClass;
    text.textContent = name;
    chip.appendChild(text);

    var remove = document.createElement('button');
    remove.type = 'button';
    remove.className = config.removeClass;
    remove.title = config.removeTitle;
    remove.setAttribute('aria-label', config.removeTitle + ' ' + name);
    remove.textContent = config.removeGlyph;

    remove.addEventListener('click', function() {
        chip.remove();
        onRemove();
    });

    chip.appendChild(remove);

    var out = chip;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The names the chips of a list currently show, in their order
$.fn.zato.alerts_tab.chipListNames = function(list) {

    var config = $.fn.zato.alerts_tab.chipsConfig;
    var out = [];

    list.querySelectorAll('.' + config.chipClass).forEach(function(chip) {
        out.push(chip.dataset.name);
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Builds the chips of a field into its row - the label, the chips and the input after them
$.fn.zato.alerts_tab.buildChipsField = function(fieldSpec, row) {

    var tab = $.fn.zato.alerts_tab;
    var config = tab.chipsConfig;
    var inputId = tab.forms.inputId(fieldSpec.field);

    row.classList.add(tab.config.slotsFieldClass);
    row.classList.add(config.fieldClass);

    var label = document.createElement('label');
    label.className = 'micro-form-label';
    label.setAttribute('for', inputId);
    label.textContent = fieldSpec.label;
    row.appendChild(label);

    var list = document.createElement('div');
    list.className = config.listClass;

    var input = document.createElement('input');
    input.type = 'text';
    input.id = inputId;
    input.className = config.inputClass;
    input.placeholder = config.addPlaceholder;
    input.autocomplete = 'off';

    // The input is the last thing in the list, the chips go in front of it
    list.appendChild(input);

    // Clicking the empty room of the list puts the cursor into the input
    list.addEventListener('click', function(event) {
        if(event.target === list) {
            input.focus();
        }
    });

    var addChip = function(name) {

        // A name already there is not added twice
        var names = tab.chipListNames(list);
        if(names.indexOf(name) !== -1) {
            return;
        }

        var chip = tab.buildChip(name, function() {
            input.focus();
        });

        list.insertBefore(chip, input);
    };

    // What was typed becomes a chip - on Enter, on a comma, and when the input loses focus
    var takeInput = function() {
        var names = tab.chipNames(input.value);
        names.forEach(addChip);
        input.value = '';
    };

    input.addEventListener('keydown', function(event) {

        if(config.addKeys.indexOf(event.key) !== -1) {

            // An empty input on Enter leaves the key to the popover, which answers with OK
            if(!input.value.trim()) {
                if(event.key === ',') {
                    event.preventDefault();
                }
                return;
            }

            event.preventDefault();
            event.stopPropagation();
            takeInput();
            return;
        }

        // Backspace in an empty input takes the last chip back into the input, to be edited
        if(event.key === 'Backspace' && !input.value) {
            var chips = list.querySelectorAll('.' + config.chipClass);
            if(chips.length) {
                var lastChip = chips[chips.length - 1];
                input.value = lastChip.dataset.name;
                lastChip.remove();
                event.preventDefault();
            }
        }
    });

    input.addEventListener('blur', takeInput);

    // The names the hidden field holds are the chips to start with
    var currentNames = tab.chipNames(tab.field(fieldSpec.field).val());
    currentNames.forEach(addChip);

    row.appendChild(list);

    tab.state.chipLists[fieldSpec.field] = list;
}

// /////////////////////////////////////////////////////////////////////////////

// Writes the chips of a field back into its hidden field, whatever is still in the input included
$.fn.zato.alerts_tab.saveChipsField = function(fieldSpec) {

    var tab = $.fn.zato.alerts_tab;
    var config = tab.chipsConfig;
    var list = tab.state.chipLists[fieldSpec.field];

    var names = tab.chipListNames(list);

    var input = list.querySelector('.' + config.inputClass);
    tab.chipNames(input.value).forEach(function(name) {
        if(names.indexOf(name) === -1) {
            names.push(name);
        }
    });

    tab.field(fieldSpec.field).val(names.join(config.joinText));
}

// /////////////////////////////////////////////////////////////////////////////

// Registers the chips kind with the micro-forms kit
$.fn.zato.alerts_tab.registerChipsKind = function() {

    var tab = $.fn.zato.alerts_tab;

    tab.state.chipLists = {};

    tab.forms.registerKind(tab.config.specChips, {

        build: function(fieldSpec, row) {
            tab.buildChipsField(fieldSpec, row);
        },

        save: function(popper, fieldSpec) {
            tab.saveChipsField(fieldSpec);
        }
    });
}

// /////////////////////////////////////////////////////////////////////////////
