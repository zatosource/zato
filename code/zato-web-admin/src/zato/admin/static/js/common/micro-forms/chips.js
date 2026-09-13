// Micro-forms - the chips kind, for a text field that is a list of names, such as the
// status codes or the SOAP fault codes a connection alerts on. Each name is a chip with a
// cross that removes it, a new one is typed into the input after the chips and added with
// Enter or a comma, and the hidden field keeps the names joined with a comma and a space,
// the way they were typed before there were chips. Loaded after micro-forms/core.js, next
// to shared/micro-forms-chips.css, and registered by the host once its setup ran:
//
//      $.fn.zato.micro_forms.registerChipsKind(host);
//
// A spec of the kind is {field, label, kind: $.fn.zato.micro_forms.chipsKind}. The list
// is two rows of chips tall from the start and stays that tall, so a chip wrapping onto
// the second row moves nothing below it, and a popover with chips is given a width of its
// own by its host rather than being sized to its content.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var microForms = $.fn.zato.micro_forms;

// ////////////////////////////////////////////////////////////////////////

// The name a spec of this kind goes by
microForms.chipsKind = 'chips';

microForms.chipsConfig = {

    // The classes of the kind
    fieldClass: 'micro-form-chips-field',
    ownClass: 'micro-form-field-own',
    listClass: 'micro-form-chips',
    chipClass: 'micro-form-chip',
    chipTextClass: 'micro-form-chip-text',
    removeClass: 'micro-form-chip-remove',
    inputClass: 'micro-form-chips-input',

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
};

// ////////////////////////////////////////////////////////////////////////

// The names a hidden field holds, in their order, without the blanks a trailing comma leaves
microForms.chipNames = function(text) {

    var config = microForms.chipsConfig;
    var out = [];

    text.split(config.splitPattern).forEach(function(name) {
        var trimmed = name.trim();
        if(trimmed) {
            out.push(trimmed);
        }
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The names the chips of a list currently show, in their order
microForms.chipListNames = function(list) {

    var config = microForms.chipsConfig;
    var out = [];

    list.querySelectorAll('.' + config.chipClass).forEach(function(chip) {
        out.push(chip.dataset.name);
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One chip - the name and the cross that removes it
microForms.buildChip = function(name, onRemove) {

    var config = microForms.chipsConfig;

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
};

// ////////////////////////////////////////////////////////////////////////

// Builds the chips of a field into its row - the label, the chips and the input after them
microForms.buildChipsField = function(host, fieldSpec, row) {

    var config = microForms.chipsConfig;
    var forms = host.forms;
    var inputId = forms.inputId(fieldSpec.field);

    // The kind dresses its own controls, the popover's input styles stay off them
    row.classList.add(config.ownClass);
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
        var names = microForms.chipListNames(list);
        if(names.indexOf(name) !== -1) {
            return;
        }

        var chip = microForms.buildChip(name, function() {
            input.focus();
        });

        list.insertBefore(chip, input);
    };

    // What was typed becomes a chip - on Enter, on a comma, and when the input loses focus
    var takeInput = function() {
        var names = microForms.chipNames(input.value);
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
    var currentNames = microForms.chipNames(host.field(fieldSpec.field).val());
    currentNames.forEach(addChip);

    row.appendChild(list);

    forms._chipLists[fieldSpec.field] = list;
};

// ////////////////////////////////////////////////////////////////////////

// Writes the chips of a field back into its hidden field, whatever is still in the input included
microForms.saveChipsField = function(host, fieldSpec) {

    var config = microForms.chipsConfig;
    var list = host.forms._chipLists[fieldSpec.field];

    var names = microForms.chipListNames(list);

    var input = list.querySelector('.' + config.inputClass);
    microForms.chipNames(input.value).forEach(function(name) {
        if(names.indexOf(name) === -1) {
            names.push(name);
        }
    });

    host.field(fieldSpec.field).val(names.join(config.joinText));
};

// ////////////////////////////////////////////////////////////////////////

// Registers the chips kind with a host's forms, once the host's setup ran
microForms.registerChipsKind = function(host) {

    var forms = host.forms;

    // The chip lists of the open popover, by field
    forms._chipLists = {};

    forms.registerKind(microForms.chipsKind, {

        build: function(fieldSpec, row) {
            microForms.buildChipsField(host, fieldSpec, row);
        },

        save: function(popper, fieldSpec) {
            microForms.saveChipsField(host, fieldSpec);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
