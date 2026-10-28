'use strict';

// The values of the editable blocks of an item. Each value of a block of fields opens a micro-form of its own,
// and each row of a table opens one micro-form holding every editable value of the row. A value that is not
// free text carries an editor in its data-edit attribute - its kind, its current value and the kind's own keys,
// such as the options of a list or the units of a duration - and is edited and shown as that kind.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var edit = {};

edit.config = {
    choiceSeparator: '|',
    toneSeparator: ':',
    fieldPrefix: 'value-'
};

// ////////////////////////////////////////////////////////////////////////

// Reads the words a chip may be changed to, given as in 'Yes:green|No:grey'.
edit.parseChoices = function(text) {

    var out = [];
    var choices = text.split(edit.config.choiceSeparator);

    for (var choiceIndex = 0; choiceIndex < choices.length; choiceIndex++) {
        var parts = choices[choiceIndex].split(edit.config.toneSeparator);
        out.push({value: parts[0], label: parts[0], tone: parts[1]});
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

edit.isPill = function(element) {
    var out = element.classList.contains('pill');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

edit.editorOf = function(element) {
    var out = JSON.parse(element.getAttribute('data-edit'));
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What the micro-form starts from - the editor's own value, or the text of a chip or of a free text value.
edit.valueOf = function(element) {

    if (element.hasAttribute('data-edit')) {
        var out = edit.editorOf(element).value;
        return out;
    }

    return element.textContent.trim();
};

// ////////////////////////////////////////////////////////////////////////

// The field of the micro-form that edits one value - a select of the words of a chip, or a text field.
edit.specOf = function(element, name, label) {

    if (edit.isPill(element)) {
        var options = edit.parseChoices(element.getAttribute('data-choices'));
        var selectSpec = {name: name, label: label, kind: 'select', options: options};
        return selectSpec;
    }

    var isMono = element.classList.contains('portal-mono');

    if (element.hasAttribute('data-edit')) {

        var editor = edit.editorOf(element);

        var editorSpec = {
            name: name,
            label: label,
            kind: editor.kind,
            input_type: editor.input_type,
            is_mono: isMono,
            options: editor.options,
            units: editor.units
        };
        return editorSpec;
    }

    var out = {
        name: name,
        label: label,
        kind: 'text',
        input_type: 'text',
        is_mono: isMono
    };
    return out;
};

// ////////////////////////////////////////////////////////////////////////

edit.apply = function(element, value) {

    // A value with an editor keeps the new value in it and reads as its kind shows it
    if (element.hasAttribute('data-edit')) {

        var editor = edit.editorOf(element);
        editor.value = value;

        element.setAttribute('data-edit', JSON.stringify(editor));
        element.textContent = portal.fields.display(editor, value);
        return;
    }

    element.textContent = value;

    if (!edit.isPill(element)) {
        return;
    }

    var choices = edit.parseChoices(element.getAttribute('data-choices'));

    for (var choiceIndex = 0; choiceIndex < choices.length; choiceIndex++) {
        if (choices[choiceIndex].value === value) {
            element.className = 'pill editable portal-tone-' + choices[choiceIndex].tone;
        }
    }

    // A tip described the word the chip had before
    element.removeAttribute('data-tip');
};

// ////////////////////////////////////////////////////////////////////////

// Opens a micro-form on the anchor for the elements given, each with its label, and writes the values back on Apply.
edit.attach = function(anchor, title, elements, labels, isCellAnchored) {

    var form = null;

    var applyForm = function(handle) {

        var values = form.read();

        for (var elementIndex = 0; elementIndex < elements.length; elementIndex++) {
            edit.apply(elements[elementIndex], values[edit.config.fieldPrefix + elementIndex]);
        }

        handle.close();
    };

    portal.popover.attach(anchor, {
        title: title,
        isCellAnchored: isCellAnchored,
        build: function(handle) {

            var rows = [];
            var values = {};

            for (var elementIndex = 0; elementIndex < elements.length; elementIndex++) {
                var name = edit.config.fieldPrefix + elementIndex;
                rows.push([edit.specOf(elements[elementIndex], name, labels[elementIndex])]);
                values[name] = edit.valueOf(elements[elementIndex]);
            }

            form = portal.fields.buildForm(rows, values);

            // Enter in any field applies the form
            form.element.addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    applyForm(handle);
                }
            });

            return form.element;
        },
        buttons: function(handle) {
            var out = [
                {label: portal.config.cancelLabel, isPrimary: false, onClick: handle.close},
                {label: portal.config.applyLabel, isPrimary: true, onClick: function() {
                    applyForm(handle);
                }}
            ];
            return out;
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

edit.initFields = function(pane) {

    var elements = pane.querySelectorAll('.fields .editable');

    for (var elementIndex = 0; elementIndex < elements.length; elementIndex++) {

        var element = elements[elementIndex];
        var label = element.closest('dd').previousElementSibling.textContent.trim();

        edit.attach(element, label, [element], [label], false);
    }
};

// ////////////////////////////////////////////////////////////////////////

edit.initRows = function(pane) {

    var rows = pane.querySelectorAll('.table-row-editable');

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {

        var row = rows[rowIndex];
        var headers = row.closest('table').querySelectorAll('th');
        var elements = row.querySelectorAll('.editable');
        var labels = [];

        for (var elementIndex = 0; elementIndex < elements.length; elementIndex++) {
            var cellIndex = elements[elementIndex].closest('td').cellIndex;
            labels.push(headers[cellIndex].textContent.trim());
        }

        // The row is named by its first value, which is what tells it from the other rows
        var title = row.cells[0].textContent.trim();

        edit.attach(row, title, elements, labels, true);
    }
};

// ////////////////////////////////////////////////////////////////////////

edit.init = function(pane) {
    edit.initFields(pane);
    edit.initRows(pane);
};

// ////////////////////////////////////////////////////////////////////////

portal.edit = edit;

// ////////////////////////////////////////////////////////////////////////

})();
