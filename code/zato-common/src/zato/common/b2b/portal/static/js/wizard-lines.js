'use strict';

// The decision lines of a wizard step. Each line has a label and the control that answers it - a text input,
// a date field with its calendar, a pick chip opening a pick panel, a select, a switch, or a summary link
// opening a micro-form in a popover. Every line reads its value from the state of the wizard, writes it back
// there and then calls lines.onChange, which the wizard sets to check the answers again.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var lines = {};

// ////////////////////////////////////////////////////////////////////////

// The state a wizard starts with - the value of each line and of each field of its micro-forms.
lines.initialState = function(steps) {

    var out = {};

    for (var stepIndex = 0; stepIndex < steps.length; stepIndex++) {

        var stepLines = steps[stepIndex].lines;

        for (var lineIndex = 0; lineIndex < stepLines.length; lineIndex++) {

            var line = stepLines[lineIndex];

            if (line.kind === 'form') {
                var specs = lines.formSpecs(line);
                for (var specIndex = 0; specIndex < specs.length; specIndex++) {
                    out[specs[specIndex].name] = specs[specIndex].value;
                }
            }
            else {
                out[line.name] = line.value;
            }
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

lines.formSpecs = function(line) {

    var out = [];
    var rows = line.form.rows;

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        for (var fieldIndex = 0; fieldIndex < rows[rowIndex].length; fieldIndex++) {
            out.push(rows[rowIndex][fieldIndex]);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A line bound to the value of another line is shown only while that line holds it, any other line always is.
lines.isShown = function(line, state) {

    if (line.shown_when.length === 0) {
        return true;
    }

    var out = state[line.shown_when[0]] === line.shown_when[1];
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Lines of one name shown for different values of another line each have a control of their own,
// so the value a line is shown for is a part of the id of its control.
lines.elementId = function(line) {

    var out = 'line-' + line.name;

    if (line.shown_when.length) {
        out = out + '-' + line.shown_when[1];
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

lines.isBoundTo = function(line, name) {

    if (line.shown_when.length === 0) {
        return false;
    }

    var out = line.shown_when[0] === name;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The rows of a step, each a list of the lines that share it. Lines bound to the same other line follow
// one another, and the n-th line of each of its values shares the n-th row of the run, so a change
// of that value replaces lines in their rows.
lines.slots = function(stepLines) {

    var out = [];
    var lineIndex = 0;

    while (lineIndex < stepLines.length) {

        var first = stepLines[lineIndex];

        if (first.shown_when.length === 0) {
            out.push([first]);
            lineIndex += 1;
            continue;
        }

        var name = first.shown_when[0];
        var runStart = out.length;
        var positions = {};

        while (lineIndex < stepLines.length) {

            var line = stepLines[lineIndex];

            if (!lines.isBoundTo(line, name)) {
                break;
            }

            var value = line.shown_when[1];

            if (!(value in positions)) {
                positions[value] = 0;
            }

            var slotIndex = runStart + positions[value];
            positions[value] += 1;

            if (slotIndex === out.length) {
                out.push([]);
            }

            out[slotIndex].push(line);
            lineIndex += 1;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

lines.optionNote = function(options, value) {

    var out = '';

    for (var optionIndex = 0; optionIndex < options.length; optionIndex++) {
        if (options[optionIndex].value === value) {
            out = options[optionIndex].note;
            break;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The summary of a micro-form, each name in braces replaced with what its field holds.
lines.summary = function(line, state) {

    var specs = lines.formSpecs(line);
    var bySpecName = {};
    var isAnySet = false;

    for (var specIndex = 0; specIndex < specs.length; specIndex++) {
        bySpecName[specs[specIndex].name] = specs[specIndex];
    }

    var out = line.summary.replace(/\{([a-z_]+)\}/g, function(match, name) {
        var text = portal.fields.display(bySpecName[name], state[name]);
        if (text) {
            isAnySet = true;
        }
        return text;
    });

    if (!isAnySet) {
        out = '';
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

lines.labels = function(line, values) {

    var out = [];

    for (var valueIndex = 0; valueIndex < values.length; valueIndex++) {
        out.push(portal.fields.optionLabel(line.options, values[valueIndex]));
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What a line of a single value holds, as a review shows it, and an empty string when it holds nothing.
lines.display = function(line, state) {

    var value = state[line.name];
    var out;

    if (line.kind === 'form') {
        out = lines.summary(line, state);
    }
    else if (line.kind === 'switch') {
        out = value ? portal.config.yesLabel : portal.config.noLabel;
    }
    else if (line.kind === 'select' || line.kind === 'pick') {
        out = portal.fields.optionLabel(line.options, value);
    }
    else {
        out = value;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

lines.buildText = function(line, state) {

    var input = portal.create('input', line.is_mono ? 'input-mono' : '', '');
    input.type = line.input_type;
    input.id = lines.elementId(line);
    input.value = state[line.name];
    input.autocomplete = 'off';
    input.spellcheck = false;

    if (line.input_type === 'date') {
        portal.calendar.attach(input);
    }

    input.addEventListener('input', function() {
        state[line.name] = input.value.trim();
        lines.onChange();
    });

    return input;
};

// ////////////////////////////////////////////////////////////////////////

lines.buildPick = function(line, state) {

    var chip = portal.create('button', 'decision-chip', '');
    chip.type = 'button';

    var render = function() {

        var value = state[line.name];
        chip.textContent = '';

        if (value) {
            chip.classList.remove('decision-chip-blank');
            chip.appendChild(portal.create('span', '', portal.fields.optionLabel(line.options, value)));
            var note = lines.optionNote(line.options, value);
            if (note) {
                chip.appendChild(portal.create('span', 'decision-chip-note', note));
            }
        }
        else {
            chip.classList.add('decision-chip-blank');
            chip.appendChild(portal.create('span', '', portal.config.emptyLabel));
        }
    };

    portal.pickPanel.attach(chip, {
        title: line.label,
        options: line.options,
        hasFilter: line.has_filter,
        isMulti: false,
        read: function() {
            return state[line.name];
        },
        onPick: function(value) {
            state[line.name] = value;
            render();
            lines.onChange();
        }
    });

    render();

    return chip;
};

// ////////////////////////////////////////////////////////////////////////

// The chip names each value picked on a line of its own, and says what the line means when there is none.
lines.buildPickMany = function(line, state) {

    var chip = portal.create('button', 'decision-chip decision-chip-many', '');
    chip.type = 'button';

    var render = function() {

        var values = state[line.name];
        chip.textContent = '';
        chip.classList.toggle('decision-chip-blank', values.length === 0);

        if (values.length === 0) {
            chip.appendChild(portal.create('div', '', line.empty));
            return;
        }

        var labels = lines.labels(line, values);

        for (var labelIndex = 0; labelIndex < labels.length; labelIndex++) {
            chip.appendChild(portal.create('div', '', labels[labelIndex]));
        }
    };

    portal.pickPanel.attach(chip, {
        title: line.label,
        options: line.options,
        hasFilter: line.has_filter,
        isMulti: true,
        read: function() {
            return state[line.name];
        },
        onPick: function(values) {
            state[line.name] = values;
            render();
            lines.onChange();
        }
    });

    render();

    return chip;
};

// ////////////////////////////////////////////////////////////////////////

lines.buildSelect = function(line, state) {

    var select = portal.create('select', '', '');
    select.id = lines.elementId(line);

    for (var optionIndex = 0; optionIndex < line.options.length; optionIndex++) {
        var optionSpec = line.options[optionIndex];
        var option = portal.create('option', '', optionSpec.label);
        option.value = optionSpec.value;
        select.appendChild(option);
    }

    select.value = state[line.name];

    select.addEventListener('change', function() {
        state[line.name] = select.value;
        lines.onChange();
    });

    return select;
};

// ////////////////////////////////////////////////////////////////////////

lines.buildSwitch = function(line, state) {

    var input = portal.create('input', 'switch', '');
    input.type = 'checkbox';
    input.id = lines.elementId(line);
    input.checked = state[line.name];

    input.addEventListener('change', function() {
        state[line.name] = input.checked;
        lines.onChange();
    });

    return input;
};

// ////////////////////////////////////////////////////////////////////////

lines.buildForm = function(line, state) {

    var link = portal.create('button', 'link summary-link', '');
    link.type = 'button';

    var form = null;

    var render = function() {
        var text = lines.summary(line, state);
        link.textContent = text ? text : portal.config.emptyLabel;
        link.classList.toggle('summary-link-blank', !text);
    };

    portal.popover.attach(link, {
        title: line.form.title,
        build: function() {
            form = portal.fields.buildForm(line.form.rows, state);
            return form.element;
        },
        buttons: function(handle) {
            var out = [
                {label: portal.config.cancelLabel, isPrimary: false, onClick: handle.close},
                {label: portal.config.okLabel, isPrimary: true, onClick: function() {
                    Object.assign(state, form.read());
                    render();
                    handle.close();
                    lines.onChange();
                }}
            ];
            return out;
        }
    });

    render();

    return link;
};

// ////////////////////////////////////////////////////////////////////////

// A file line is the button that opens the file chooser, with the name of the file chosen beside it.
// Closing the chooser without a file leaves the line with no answer.
lines.buildFile = function(line, state) {

    var holder = portal.create('div', 'decision-file', '');
    var button = portal.create('label', 'button-secondary', line.button_label);
    var fileName = portal.create('span', 'decision-file-name', state[line.name]);

    var input = portal.create('input', '', '');
    input.type = 'file';
    input.id = lines.elementId(line);
    input.accept = line.accept;
    input.hidden = true;

    input.addEventListener('change', function() {
        state[line.name] = '';
        if (input.files.length) {
            state[line.name] = input.files[0].name;
        }
        fileName.textContent = state[line.name];
        lines.onChange();
    });

    button.appendChild(input);
    holder.appendChild(button);
    holder.appendChild(fileName);

    return holder;
};

// ////////////////////////////////////////////////////////////////////////

lines.builders = {
    'text': lines.buildText,
    'file': lines.buildFile,
    'pick': lines.buildPick,
    'pick-many': lines.buildPickMany,
    'select': lines.buildSelect,
    'switch': lines.buildSwitch,
    'form': lines.buildForm
};

// ////////////////////////////////////////////////////////////////////////

lines.bindLayer = function(element, line) {

    if (line.shown_when.length) {
        element.setAttribute('data-shown-name', line.shown_when[0]);
        element.setAttribute('data-shown-value', line.shown_when[1]);
    }
};

// ////////////////////////////////////////////////////////////////////////

// Builds the labels and the controls of the lines of one row into the grid of the step, each control with
// the place for its error below it. The lines of a row are stacked in one cell, which is as large as the largest of them.
lines.buildSlot = function(grid, slot, state) {

    var labelCell = portal.create('div', 'decision-layers', '');
    var controlCell = portal.create('div', 'decision-layers', '');

    for (var lineIndex = 0; lineIndex < slot.length; lineIndex++) {

        var line = slot[lineIndex];

        var label = portal.create('label', 'decision-line-label', line.label);
        label.setAttribute('for', lines.elementId(line));
        lines.bindLayer(label, line);

        var lineSlot = portal.create('div', 'decision-line-slot', '');
        lineSlot.setAttribute('data-line', line.name);
        lineSlot.appendChild(lines.builders[line.kind](line, state));
        lines.bindLayer(lineSlot, line);

        var error = portal.create('div', 'decision-error', '');
        error.hidden = true;
        lineSlot.appendChild(error);

        labelCell.appendChild(label);
        controlCell.appendChild(lineSlot);
    }

    grid.appendChild(labelCell);
    grid.appendChild(controlCell);
};

// ////////////////////////////////////////////////////////////////////////

// Shows each line under the root that the state shows, and keeps every other one in its row unseen.
// A row with no line shown is left out of the grid altogether.
lines.applyVisibility = function(root, state) {

    var elements = root.querySelectorAll('[data-shown-name]');

    for (var elementIndex = 0; elementIndex < elements.length; elementIndex++) {
        var element = elements[elementIndex];
        var value = state[element.getAttribute('data-shown-name')];
        element.classList.toggle('decision-layer-hidden', element.getAttribute('data-shown-value') !== value);
    }

    var cells = root.querySelectorAll('.decision-layers');

    for (var cellIndex = 0; cellIndex < cells.length; cellIndex++) {
        var cell = cells[cellIndex];
        var isEmpty = cell.querySelector(':scope > :not(.decision-layer-hidden)') === null;
        cell.classList.toggle('decision-layers-empty', isEmpty);
    }
};

// ////////////////////////////////////////////////////////////////////////

// Shows the error of each line under the root that has one, and hides it for each line that has none.
lines.showErrors = function(root, errors) {

    var slots = root.querySelectorAll('.decision-line-slot');

    for (var slotIndex = 0; slotIndex < slots.length; slotIndex++) {

        var slot = slots[slotIndex];
        var name = slot.getAttribute('data-line');
        var isInvalid = name in errors;
        var error = slot.querySelector('.decision-error');

        error.textContent = isInvalid ? errors[name] : '';
        error.hidden = !isInvalid;
        slot.classList.toggle('decision-line-slot-invalid', isInvalid);
    }
};

// ////////////////////////////////////////////////////////////////////////

portal.wizardLines = lines;

// ////////////////////////////////////////////////////////////////////////

})();
