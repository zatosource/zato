'use strict';

// A wizard - a strip of numbered steps, the decision lines of the current step,
// and a review of every answer before the wizard is completed. Completing it checks every answer first,
// and once the errors are shown, each change of an answer checks them again.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var wizard = {};

wizard.current = 0;
wizard.errors = {};
wizard.isSubmitted = false;

// ////////////////////////////////////////////////////////////////////////

wizard.stepNumber = function(stepIndex) {

    var number = stepIndex + 1;
    var out = number < 10 ? '0' + number : String(number);

    return out;
};

// ////////////////////////////////////////////////////////////////////////

wizard.renderSteps = function() {

    var strip = document.getElementById('wizard-steps');
    strip.textContent = '';

    for (var stepIndex = 0; stepIndex < wizard.data.steps.length; stepIndex++) {

        var step = wizard.data.steps[stepIndex];

        var button = portal.create('button', 'tab', '');
        button.type = 'button';
        button.setAttribute('role', 'tab');
        button.classList.toggle('tab-active', stepIndex === wizard.current);
        button.classList.toggle('tab-invalid', portal.wizardChecks.hasErrors(step, wizard.errors));

        button.appendChild(portal.create('span', 'wizard-step-number', wizard.stepNumber(stepIndex)));
        button.appendChild(portal.create('span', '', step.title));
        button.addEventListener('click', wizard.show.bind(null, stepIndex));

        strip.appendChild(button);
    }
};

// ////////////////////////////////////////////////////////////////////////

wizard.renderLines = function(body, step) {

    var grid = portal.create('div', 'decision-lines', '');

    for (var lineIndex = 0; lineIndex < step.lines.length; lineIndex++) {
        portal.wizardLines.build(grid, step.lines[lineIndex], wizard.state);
    }

    body.appendChild(grid);
};

// ////////////////////////////////////////////////////////////////////////

wizard.reviewValue = function(text) {

    var out = text
        ? portal.create('span', 'wizard-review-value', text)
        : portal.create('span', 'wizard-review-value-blank', portal.config.emptyLabel);

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Each value picked stands on a line of its own, and a list with nothing picked says what that means.
wizard.reviewList = function(line) {

    var values = wizard.state[line.name];

    if (values.length === 0) {
        var out = wizard.reviewValue(line.empty);
        return out;
    }

    var list = portal.create('div', 'wizard-review-value', '');
    var labels = portal.wizardLines.labels(line, values);

    for (var labelIndex = 0; labelIndex < labels.length; labelIndex++) {
        list.appendChild(portal.create('div', '', labels[labelIndex]));
    }

    return list;
};

// ////////////////////////////////////////////////////////////////////////

wizard.renderReview = function(body) {

    for (var stepIndex = 0; stepIndex < wizard.data.steps.length; stepIndex++) {

        var step = wizard.data.steps[stepIndex];

        if (step.is_review) {
            continue;
        }

        var group = portal.create('div', 'wizard-review-group', '');
        group.appendChild(portal.create('div', 'wizard-review-group-label', step.title));

        for (var lineIndex = 0; lineIndex < step.lines.length; lineIndex++) {

            var line = step.lines[lineIndex];
            var row = portal.create('div', 'wizard-review-row', '');
            row.appendChild(portal.create('span', 'wizard-review-key', line.label));

            if (line.kind === 'pick-many') {
                row.appendChild(wizard.reviewList(line));
            }
            else {
                row.appendChild(wizard.reviewValue(portal.wizardLines.display(line, wizard.state)));
            }

            group.appendChild(row);
        }

        body.appendChild(group);
    }
};

// ////////////////////////////////////////////////////////////////////////

wizard.show = function(stepIndex) {

    // A popover of the step that is left has nothing to belong to any longer
    window.tippy.hideAll({duration: 0});

    wizard.current = stepIndex;

    var step = wizard.data.steps[stepIndex];
    var isLast = stepIndex === wizard.data.steps.length - 1;

    var body = document.getElementById('wizard-body');
    body.textContent = '';

    if (step.is_review) {
        wizard.renderReview(body);
    }
    else {
        wizard.renderLines(body, step);
        portal.wizardLines.showErrors(body, wizard.errors);
    }

    document.getElementById('wizard-back').disabled = stepIndex === 0;
    document.getElementById('wizard-next').textContent = isLast ? wizard.data.done_label : portal.config.nextLabel;

    wizard.renderSteps();
};

// ////////////////////////////////////////////////////////////////////////

wizard.check = function() {
    wizard.errors = portal.wizardChecks.errors(wizard.data.steps, wizard.state);
};

// ////////////////////////////////////////////////////////////////////////

wizard.onChange = function() {

    // .. errors appear only once completing the wizard has been attempted ..
    if (!wizard.isSubmitted) {
        return;
    }

    wizard.check();
    portal.wizardLines.showErrors(document.getElementById('wizard-body'), wizard.errors);
    wizard.renderSteps();
};

// ////////////////////////////////////////////////////////////////////////

// The first step with an error, or -1 when every answer is valid.
wizard.firstInvalid = function() {

    for (var stepIndex = 0; stepIndex < wizard.data.steps.length; stepIndex++) {
        if (portal.wizardChecks.hasErrors(wizard.data.steps[stepIndex], wizard.errors)) {
            return stepIndex;
        }
    }

    return -1;
};

// ////////////////////////////////////////////////////////////////////////

wizard.onNext = function() {

    if (wizard.current < wizard.data.steps.length - 1) {
        wizard.show(wizard.current + 1);
        return;
    }

    wizard.isSubmitted = true;
    wizard.check();

    var invalid = wizard.firstInvalid();

    // .. an answer with an error keeps the wizard open on the step where it is ..
    if (invalid !== -1) {
        wizard.show(invalid);
        return;
    }

    // The last step completes the wizard and returns to the listing it was opened from
    window.location.href = wizard.data.list_path;
};

// ////////////////////////////////////////////////////////////////////////

wizard.init = function() {

    wizard.data = portal.readData('wizard-data');
    wizard.state = portal.wizardLines.initialState(wizard.data.steps);
    portal.wizardLines.onChange = wizard.onChange;

    document.getElementById('wizard-back').addEventListener('click', function() {
        wizard.show(wizard.current - 1);
    });

    document.getElementById('wizard-next').addEventListener('click', wizard.onNext);

    wizard.show(0);
};

// ////////////////////////////////////////////////////////////////////////

portal.wizard = wizard;

document.addEventListener('DOMContentLoaded', wizard.init);

// ////////////////////////////////////////////////////////////////////////

})();
