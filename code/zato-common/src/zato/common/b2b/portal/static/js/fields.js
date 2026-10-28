'use strict';

// The fields of a micro-form. A form is a list of rows, each row a list of field specs shown side by side,
// and each field spec has a name, a label, a kind - text, number, duration, select, switch or chips - and the kind's
// own keys: input_type and is_mono of a text field, unit of a number, units of a duration, options of a select
// and of chips. A duration is a pair of an amount and the unit it is counted in.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var fields = {};

// ////////////////////////////////////////////////////////////////////////

// Builds the rows of a form seeded from the values given, and returns the element with a read function
// that collects what the fields hold at the time it is called.
fields.buildForm = function(rows, values) {

    var element = portal.create('div', 'micro-form', '');
    var readers = [];

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {

        var row = rows[rowIndex];
        var rowElement = portal.create('div', 'micro-form-row', '');

        for (var fieldIndex = 0; fieldIndex < row.length; fieldIndex++) {
            var spec = row[fieldIndex];
            var built = fields.build(spec, values[spec.name]);
            rowElement.appendChild(built.element);
            readers.push({name: spec.name, read: built.read});
        }

        element.appendChild(rowElement);
    }

    var read = function() {

        var out = {};

        for (var readerIndex = 0; readerIndex < readers.length; readerIndex++) {
            var reader = readers[readerIndex];
            out[reader.name] = reader.read();
        }

        return out;
    };

    var out = {element: element, read: read};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

fields.build = function(spec, value) {

    var builder = fields.builders[spec.kind];
    var out = builder(spec, value);

    return out;
};

// ////////////////////////////////////////////////////////////////////////

fields.wrap = function(spec, control, inputId) {

    var field = portal.create('div', 'micro-form-field', '');

    var label = portal.create('label', 'micro-form-label', spec.label);
    label.setAttribute('for', inputId);

    field.appendChild(label);
    field.appendChild(control);

    return field;
};

// ////////////////////////////////////////////////////////////////////////

fields.inputId = function(spec) {
    var out = 'portal-field-' + spec.name;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

fields.buildText = function(spec, value) {

    var input = portal.create('input', spec.is_mono ? 'input-mono' : '', '');
    input.type = spec.input_type;
    input.id = fields.inputId(spec);
    input.value = value;
    input.autocomplete = 'off';
    input.spellcheck = false;

    if (spec.input_type === 'date') {
        portal.calendar.attach(input);
    }

    var read = function() {
        var out = input.value.trim();
        return out;
    };

    var out = {element: fields.wrap(spec, input, input.id), read: read};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

fields.buildNumber = function(spec, value) {

    var control = portal.create('div', 'micro-form-number', '');

    var input = portal.create('input', '', '');
    input.type = 'number';
    input.min = '0';
    input.id = fields.inputId(spec);
    input.value = String(value);
    control.appendChild(input);

    if (spec.unit) {
        control.appendChild(portal.create('span', 'micro-form-unit', spec.unit));
    }

    var read = function() {

        var out = parseInt(input.value, 10);

        if (isNaN(out)) {
            out = value;
        }

        return out;
    };

    var out = {element: fields.wrap(spec, control, input.id), read: read};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

fields.buildDuration = function(spec, value) {

    var control = portal.create('div', 'micro-form-number', '');

    var input = portal.create('input', '', '');
    input.type = 'number';
    input.min = '0';
    input.id = fields.inputId(spec);
    input.value = String(value.amount);
    control.appendChild(input);

    var select = portal.create('select', '', '');

    for (var unitIndex = 0; unitIndex < spec.units.length; unitIndex++) {
        var unit = spec.units[unitIndex];
        var option = portal.create('option', '', unit.label);
        option.value = unit.value;
        select.appendChild(option);
    }

    select.value = value.unit;
    control.appendChild(select);

    var read = function() {

        var amount = parseInt(input.value, 10);

        if (isNaN(amount)) {
            amount = value.amount;
        }

        var out = {amount: amount, unit: select.value};
        return out;
    };

    var out = {element: fields.wrap(spec, control, input.id), read: read};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// An amount with the word for what it counts, in the singular for one and in the plural for any other amount.
fields.counted = function(amount, one, many) {
    var out = amount + ' ' + (amount === 1 ? one : many);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A duration as it reads - one minute, 5 minutes, or None when it is zero.
fields.durationText = function(spec, value) {

    if (value.amount === 0) {
        return portal.config.noneLabel;
    }

    var out = '';

    for (var unitIndex = 0; unitIndex < spec.units.length; unitIndex++) {
        var unit = spec.units[unitIndex];
        if (unit.value === value.unit) {
            out = fields.counted(value.amount, unit.one, unit.label);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

fields.buildSelect = function(spec, value) {

    var select = portal.create('select', '', '');
    select.id = fields.inputId(spec);

    for (var optionIndex = 0; optionIndex < spec.options.length; optionIndex++) {
        var optionSpec = spec.options[optionIndex];
        var option = portal.create('option', '', optionSpec.label);
        option.value = optionSpec.value;
        select.appendChild(option);
    }

    select.value = value;

    var read = function() {
        var out = select.value;
        return out;
    };

    var out = {element: fields.wrap(spec, select, select.id), read: read};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

fields.buildSwitch = function(spec, value) {

    var field = portal.create('div', 'micro-form-field', '');

    var label = portal.create('label', 'micro-form-checkbox', '');

    var input = portal.create('input', 'switch', '');
    input.type = 'checkbox';
    input.checked = value;

    label.appendChild(portal.create('span', 'micro-form-checkbox-text', spec.label));
    label.appendChild(input);
    field.appendChild(label);

    var read = function() {
        var out = input.checked;
        return out;
    };

    var out = {element: field, read: read};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Each option is a chip that is pressed to pick it or to let go of it.
fields.buildChips = function(spec, value) {

    var control = portal.create('div', 'micro-form-chips', '');
    var picked = value.slice();

    var toggle = function(chip, optionValue) {

        var index = picked.indexOf(optionValue);

        if (index === -1) {
            picked.push(optionValue);
        }
        else {
            picked.splice(index, 1);
        }

        chip.classList.toggle('chip-on', index === -1);
    };

    for (var optionIndex = 0; optionIndex < spec.options.length; optionIndex++) {

        var optionSpec = spec.options[optionIndex];

        var chip = portal.createChip(optionSpec.label, true);
        chip.classList.toggle('chip-on', picked.indexOf(optionSpec.value) !== -1);
        chip.addEventListener('click', toggle.bind(null, chip, optionSpec.value));

        control.appendChild(chip);
    }

    var read = function() {
        var out = picked.slice();
        return out;
    };

    var field = portal.create('div', 'micro-form-field', '');
    field.appendChild(portal.create('span', 'micro-form-label', spec.label));
    field.appendChild(control);

    var out = {element: field, read: read};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

fields.builders = {
    text: fields.buildText,
    number: fields.buildNumber,
    duration: fields.buildDuration,
    select: fields.buildSelect,
    switch: fields.buildSwitch,
    chips: fields.buildChips
};

// ////////////////////////////////////////////////////////////////////////

// The value of a field as a summary or a review shows it.
fields.display = function(spec, value) {

    var out;

    if (spec.kind === 'switch') {
        out = value ? portal.config.yesLabel : portal.config.noLabel;
    }
    else if (spec.kind === 'chips') {
        out = value.join(', ');
    }
    else if (spec.kind === 'duration') {
        out = fields.durationText(spec, value);
    }
    else if (spec.kind === 'select') {
        out = fields.optionLabel(spec.options, value);
    }
    else if (spec.kind === 'number' && spec.one) {
        out = fields.counted(value, spec.one, spec.many);
    }
    else {
        out = String(value);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

fields.optionLabel = function(options, value) {

    var out = '';

    for (var optionIndex = 0; optionIndex < options.length; optionIndex++) {
        if (options[optionIndex].value === value) {
            out = options[optionIndex].label;
            break;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

portal.fields = fields;

// ////////////////////////////////////////////////////////////////////////

})();
