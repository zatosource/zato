'use strict';

// A pick panel is a popover with a list of options to pick from, narrowed down by a filter.
// A single pick closes the panel at once, while a pick of many toggles each row and is applied with OK.
//
// spec:
//   title     - what the header says
//   options   - a list of {value, label, note}
//   hasFilter - whether the panel has a filter over the options
//   isMulti   - whether more than one option can be picked
//   read()    - returns what is picked now, a value or a list of values
//   onPick(value) - called with the new value or the new list of values

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var pickPanel = {};

// ////////////////////////////////////////////////////////////////////////

pickPanel.attach = function(anchor, spec) {

    var picked = [];

    var out = portal.popover.attach(anchor, {
        title: spec.title,
        build: function(handle) {
            picked = spec.isMulti ? spec.read().slice() : [spec.read()];
            var body = pickPanel.buildBody(spec, picked, handle);
            return body;
        },
        buttons: function(handle) {
            var buttons = [{label: portal.config.cancelLabel, isPrimary: false, onClick: handle.close}];
            if (spec.isMulti) {
                buttons.push({label: portal.config.okLabel, isPrimary: true, onClick: function() {
                    spec.onPick(picked.slice());
                    handle.close();
                }});
            }
            return buttons;
        }
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

pickPanel.buildBody = function(spec, picked, handle) {

    var body = portal.create('div', '', '');
    var list = portal.create('div', 'pick-list', '');
    var empty = portal.create('div', 'pick-empty', portal.config.noMatchLabel);
    var rows = [];

    empty.hidden = true;

    for (var optionIndex = 0; optionIndex < spec.options.length; optionIndex++) {
        var option = spec.options[optionIndex];
        var row = pickPanel.buildRow(spec, option, picked, handle);
        rows.push({element: row, text: (option.label + ' ' + option.note).toLowerCase()});
        list.appendChild(row);
    }

    if (spec.hasFilter) {

        var filter = portal.create('input', 'pick-filter', '');
        filter.type = 'search';
        filter.placeholder = portal.config.filterPlaceholder;
        filter.autocomplete = 'off';
        filter.spellcheck = false;

        filter.addEventListener('input', function() {
            pickPanel.applyFilter(rows, empty, filter.value.trim().toLowerCase());
        });

        body.appendChild(filter);
    }

    body.appendChild(list);
    body.appendChild(empty);

    return body;
};

// ////////////////////////////////////////////////////////////////////////

pickPanel.buildRow = function(spec, option, picked, handle) {

    var row = portal.create('div', 'pick-row', '');
    var mark = portal.create('span', 'pick-mark', '');

    mark.classList.toggle('pick-mark-on', picked.indexOf(option.value) !== -1);

    row.appendChild(mark);
    row.appendChild(portal.create('span', 'pick-name', option.label));

    if (option.note) {
        row.appendChild(portal.create('span', 'pick-note', option.note));
    }

    // A pick of many toggles each row ..
    if (spec.isMulti) {
        row.addEventListener('click', function() {
            pickPanel.toggle(picked, option.value);
            mark.classList.toggle('pick-mark-on', picked.indexOf(option.value) !== -1);
        });
    }

    // .. while a single pick is complete with the first press.
    else {
        row.addEventListener('click', function() {
            spec.onPick(option.value);
            handle.close();
        });
    }

    return row;
};

// ////////////////////////////////////////////////////////////////////////

pickPanel.toggle = function(picked, value) {

    var index = picked.indexOf(value);

    if (index === -1) {
        picked.push(value);
    }
    else {
        picked.splice(index, 1);
    }
};

// ////////////////////////////////////////////////////////////////////////

pickPanel.applyFilter = function(rows, empty, text) {

    var shownCount = 0;

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        var row = rows[rowIndex];
        var isShown = row.text.indexOf(text) !== -1;
        row.element.hidden = !isShown;
        if (isShown) {
            shownCount += 1;
        }
    }

    empty.hidden = shownCount !== 0;
};

// ////////////////////////////////////////////////////////////////////////

portal.pickPanel = pickPanel;

// ////////////////////////////////////////////////////////////////////////

})();
