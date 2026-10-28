'use strict';

// The checks of the answers of a wizard. A text field is checked against its input type - an email address,
// a list of them, an https URL or a date later than another one - and against its pattern, a pick and a list
// of picks are checked for an answer, and a micro-form reports the first of the errors of its fields.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var checks = {};

checks.config = {
    requiredMessage: 'Required',
    pickManyMessage: 'Select at least one',
    fieldSeparator: ': ',
    emailMessage: 'Enter a valid email address',
    emailsMessage: 'Enter valid email addresses separated by commas',
    urlMessage: 'Enter a valid https URL',
    afterMessage: 'Must be later than ',
    listSeparator: ',',
    urlProtocol: 'https:',
    emailPattern: /^[^\s@,]+@[^\s@,]+\.[^\s@,]+$/
};

// ////////////////////////////////////////////////////////////////////////

// A field required only while a list holds a given value follows that list, any other field follows its own flag.
checks.isRequired = function(spec, state) {

    if (spec.required_when.length) {
        var out = state[spec.required_when[0]].indexOf(spec.required_when[1]) !== -1;
        return out;
    }

    return spec.is_required;
};

// ////////////////////////////////////////////////////////////////////////

checks.isUrl = function(value) {

    // .. the constructor is the parser of the browser, and it rejects what is not a URL ..
    try {
        var url = new URL(value);
        var out = url.protocol === checks.config.urlProtocol && url.hostname !== '';
        return out;
    }
    catch (error) {
        return false;
    }
};

// ////////////////////////////////////////////////////////////////////////

checks.emailError = function(spec, value) {

    var items = spec.is_list ? value.split(checks.config.listSeparator) : [value];

    for (var itemIndex = 0; itemIndex < items.length; itemIndex++) {
        if (!checks.config.emailPattern.test(items[itemIndex].trim())) {
            var out = spec.is_list ? checks.config.emailsMessage : checks.config.emailMessage;
            return out;
        }
    }

    return '';
};

// ////////////////////////////////////////////////////////////////////////

checks.textError = function(spec, state) {

    var value = state[spec.name];

    if (value === '') {
        var out = checks.isRequired(spec, state) ? checks.config.requiredMessage : '';
        return out;
    }

    if (spec.input_type === 'email') {
        var emailError = checks.emailError(spec, value);
        if (emailError) {
            return emailError;
        }
    }

    if (spec.input_type === 'url' && !checks.isUrl(value)) {
        return checks.config.urlMessage;
    }

    if (spec.pattern && !new RegExp(spec.pattern).test(value)) {
        return spec.pattern_message;
    }

    // .. dates in the ISO form compare as text in the order of time ..
    if (spec.after && state[spec.after] !== '' && value <= state[spec.after]) {
        return checks.config.afterMessage + spec.after_label;
    }

    return '';
};

// ////////////////////////////////////////////////////////////////////////

checks.listError = function(spec, state) {

    var isMissing = spec.is_required && state[spec.name].length === 0;
    var out = isMissing ? checks.config.pickManyMessage : '';

    return out;
};

// ////////////////////////////////////////////////////////////////////////

checks.formError = function(line, state) {

    var specs = portal.wizardLines.formSpecs(line);

    for (var specIndex = 0; specIndex < specs.length; specIndex++) {

        var spec = specs[specIndex];
        var error = '';

        if (spec.kind === 'text') {
            error = checks.textError(spec, state);
        }
        else if (spec.kind === 'chips') {
            error = checks.listError(spec, state);
        }

        if (error) {
            var out = spec.label + checks.config.fieldSeparator + error;
            return out;
        }
    }

    return '';
};

// ////////////////////////////////////////////////////////////////////////

checks.lineError = function(line, state) {

    var out = '';

    if (line.kind === 'text') {
        out = checks.textError(line, state);
    }
    else if (line.kind === 'pick') {
        out = line.is_required && state[line.name] === '' ? checks.config.requiredMessage : '';
    }
    else if (line.kind === 'pick-many') {
        out = checks.listError(line, state);
    }
    else if (line.kind === 'form') {
        out = checks.formError(line, state);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The error of each line that has one, by the name of the line.
checks.errors = function(steps, state) {

    var out = {};

    for (var stepIndex = 0; stepIndex < steps.length; stepIndex++) {

        var stepLines = steps[stepIndex].lines;

        for (var lineIndex = 0; lineIndex < stepLines.length; lineIndex++) {

            var line = stepLines[lineIndex];

            // .. a line that is not shown has no answer to check ..
            if (!portal.wizardLines.isShown(line, state)) {
                continue;
            }

            var error = checks.lineError(line, state);
            if (error) {
                out[line.name] = error;
            }
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

checks.hasErrors = function(step, errors) {

    for (var lineIndex = 0; lineIndex < step.lines.length; lineIndex++) {
        if (step.lines[lineIndex].name in errors) {
            return true;
        }
    }

    return false;
};

// ////////////////////////////////////////////////////////////////////////

portal.wizardChecks = checks;

// ////////////////////////////////////////////////////////////////////////

})();
