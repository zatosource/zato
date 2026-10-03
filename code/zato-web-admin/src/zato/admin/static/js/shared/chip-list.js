// Chip list - a text input whose value is a list of names, each of them shown as a chip.
//
// The input keeps the whole list as one line - the names joined with the separator - which
// is what the form submits and what the server hands back, so the field needs nothing of the
// backend. The chips are built in Chosen's markup, so the look every chip in the app shares,
// from shared/chips.css, dresses them too, and shared/chip-list.css lays out the box they sit in.
//
// ---------------------------------------------------------------
// How to use
// ---------------------------------------------------------------
//
//      <link rel="stylesheet" href="/static/css/shared/chip-list.css">
//      <script src="/static/js/shared/chip-list.js"></script>
//
//      $.fn.zato.chip_list.init(document.getElementById('id_resource_types'));
//
// A second call on the same input does nothing, so a dialog may call init every time it opens.
// Once the input's value was set from outside - a row's data read into an edit form - the chips
// follow it after:
//
//      $.fn.zato.chip_list.refresh(input);
//
// Options, each with a default from the config below:
//
//      splitPattern - the regex the input's line is split on
//      separator    - what the names are joined with on the way back into the input
//      commitKeys   - the keys that turn what was typed into a chip

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.namespace('zato.chip_list');

var chipList = $.fn.zato.chip_list;

// ////////////////////////////////////////////////////////////////////////

chipList.config = {
    containerClass: 'chosen-container chosen-container-multi zato-chip-list',
    choicesClass: 'chosen-choices',
    searchFieldClass: 'search-field',
    chipClass: 'search-choice',
    chipRemoveClass: 'search-choice-close',
    activeClass: 'chosen-container-active',
    disabledClass: 'chosen-disabled',
    valueAttribute: 'data-value',
    builtKey: 'chip-list-built',
    stateKey: 'chip-list-state',
    splitPattern: /,/,
    separator: ', ',
    commitKeys: ['Enter', ',']
};

// ////////////////////////////////////////////////////////////////////////

// The parts of a line that are not blank, in the order they came in.
chipList.split = function(text, splitPattern) {

    var out = [];
    var parts = text.split(splitPattern);

    for(var partIdx = 0; partIdx < parts.length; partIdx++) {
        var value = parts[partIdx].trim();
        if(value) {
            out.push(value);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

chipList.values = function(input, options) {
    var out = chipList.split(input.value, options.splitPattern);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Redraws the chips from the input, keeping the text field last.
chipList.render = function(input, state) {

    var config = chipList.config;
    var chips = state.choices.getElementsByClassName(config.chipClass);

    while(chips.length) {
        chips[0].remove();
    }

    var values = chipList.values(input, state.options);

    for(var valueIdx = 0; valueIdx < values.length; valueIdx++) {

        var chip = document.createElement('li');
        chip.className = config.chipClass;

        var text = document.createElement('span');
        text.textContent = values[valueIdx];
        chip.appendChild(text);

        var remove = document.createElement('a');
        remove.className = config.chipRemoveClass;
        remove.setAttribute(config.valueAttribute, values[valueIdx]);
        chip.appendChild(remove);

        state.choices.insertBefore(chip, state.searchField);
    }
};

// ////////////////////////////////////////////////////////////////////////

// The container follows the disabled state of the input it wraps.
chipList.syncDisabled = function(input, state) {
    var isDisabled = input.disabled;
    state.container.classList.toggle(chipList.config.disabledClass, isDisabled);
    state.textField.disabled = isDisabled;
};

// ////////////////////////////////////////////////////////////////////////

chipList.refresh = function(input) {
    var state = $(input).data(chipList.config.stateKey);
    chipList.render(input, state);
    chipList.syncDisabled(input, state);
};

// ////////////////////////////////////////////////////////////////////////

chipList.commit = function(input, state) {

    var values = chipList.values(input, state.options);
    var typed = chipList.split(state.textField.value, state.options.splitPattern);
    var added = false;

    for(var typedIdx = 0; typedIdx < typed.length; typedIdx++) {
        var value = typed[typedIdx];
        if(values.indexOf(value) === -1) {
            values.push(value);
            added = true;
        }
    }

    state.textField.value = '';

    if(added) {
        input.value = values.join(state.options.separator);
        chipList.render(input, state);
        $(input).trigger('change');
    }
};

// ////////////////////////////////////////////////////////////////////////

chipList.remove = function(input, state, value) {

    var values = chipList.values(input, state.options);
    var valueIdx = values.indexOf(value);

    values.splice(valueIdx, 1);
    input.value = values.join(state.options.separator);
    chipList.render(input, state);
    $(input).trigger('change');
};

// ////////////////////////////////////////////////////////////////////////

chipList.init = function(input, options) {

    var config = chipList.config;
    var jqueryInput = $(input);

    if(jqueryInput.data(config.builtKey)) {
        return;
    }
    jqueryInput.data(config.builtKey, true);

    var state = {
        options: $.extend({
            splitPattern: config.splitPattern,
            separator: config.separator,
            commitKeys: config.commitKeys
        }, options)
    };

    var container = document.createElement('div');
    container.className = config.containerClass;

    var choices = document.createElement('ul');
    choices.className = config.choicesClass;

    var searchField = document.createElement('li');
    searchField.className = config.searchFieldClass;

    var textField = document.createElement('input');
    textField.type = 'text';
    textField.setAttribute('autocomplete', 'off');
    textField.placeholder = input.placeholder;

    searchField.appendChild(textField);
    choices.appendChild(searchField);
    container.appendChild(choices);

    // The widget stands in for the input, which keeps the value out of sight
    input.style.display = 'none';
    input.insertAdjacentElement('afterend', container);

    state.container = container;
    state.choices = choices;
    state.searchField = searchField;
    state.textField = textField;

    jqueryInput.data(config.stateKey, state);

    // The commit keys add what was typed - the event stops here so the form-wide Enter
    // handling stays out of it - and Backspace in an empty field takes the last chip back
    textField.onkeydown = function(event) {

        if(state.options.commitKeys.indexOf(event.key) !== -1) {
            event.preventDefault();
            event.stopPropagation();
            chipList.commit(input, state);
            return;
        }

        if(event.key === 'Backspace') {
            if(!textField.value) {
                var values = chipList.values(input, state.options);
                if(values.length) {
                    event.preventDefault();
                    chipList.remove(input, state, values[values.length - 1]);
                }
            }
        }
    };

    textField.onfocus = function() {
        container.classList.add(config.activeClass);
    };

    // Leaving the field commits what was typed, so nothing is lost to a click on OK
    textField.onblur = function() {
        container.classList.remove(config.activeClass);
        chipList.commit(input, state);
    };

    // A chip's remove mark removes it, a click anywhere else in the box invites typing
    choices.onclick = function(event) {

        var removeMark = event.target.closest('.' + config.chipRemoveClass);

        if(removeMark) {
            chipList.remove(input, state, removeMark.getAttribute(config.valueAttribute));
        }
        else if(event.target === choices) {
            textField.focus();
        }
    };

    chipList.refresh(input);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
