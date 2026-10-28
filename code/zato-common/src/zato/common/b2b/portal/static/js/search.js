'use strict';

// The search of a listing - the search form in a popover, and a chip for each criterion in effect, which is pressed to drop it.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var search = {};

search.values = {};

// ////////////////////////////////////////////////////////////////////////

search.fieldSpecs = function() {

    var out = [];
    var rows = search.data.form.rows;

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        for (var fieldIndex = 0; fieldIndex < rows[rowIndex].length; fieldIndex++) {
            out.push(rows[rowIndex][fieldIndex]);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The values the form opens with - those of the search in effect, and an empty value for the other fields.
search.formValues = function() {

    var out = {};
    var specs = search.fieldSpecs();

    for (var specIndex = 0; specIndex < specs.length; specIndex++) {

        var name = specs[specIndex].name;
        var value = search.values[name];

        if (value === undefined) {
            value = '';
        }

        out[name] = value;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Puts a new search in effect, every value that is not empty being one criterion of it.
search.run = function(values) {

    search.values = {};

    var criteria = [];
    var specs = search.fieldSpecs();

    for (var specIndex = 0; specIndex < specs.length; specIndex++) {

        var spec = specs[specIndex];
        var value = values[spec.name];

        if (value) {
            search.values[spec.name] = value;
            criteria.push({name: spec.name, value: value, match: spec.match});
        }
    }

    portal.listing.state.criteria = criteria;
    portal.listing.apply();

    search.renderCriteria();
};

// ////////////////////////////////////////////////////////////////////////

search.dropCriterion = function(name) {

    var values = {};
    var names = Object.keys(search.values);

    for (var nameIndex = 0; nameIndex < names.length; nameIndex++) {
        if (names[nameIndex] !== name) {
            values[names[nameIndex]] = search.values[names[nameIndex]];
        }
    }

    search.run(values);
};

// ////////////////////////////////////////////////////////////////////////

search.renderCriteria = function() {

    var container = document.getElementById('criteria');
    var specs = search.fieldSpecs();

    container.textContent = '';

    for (var specIndex = 0; specIndex < specs.length; specIndex++) {

        var spec = specs[specIndex];
        var value = search.values[spec.name];

        if (value === undefined) {
            continue;
        }

        var chip = portal.createChip('', true);
        chip.appendChild(portal.create('span', 'chip-label', spec.label));
        chip.appendChild(portal.create('span', 'chip-value', portal.fields.display(spec, value)));
        chip.addEventListener('click', search.dropCriterion.bind(null, spec.name));

        container.appendChild(chip);
    }

    container.hidden = container.childElementCount === 0;
};

// ////////////////////////////////////////////////////////////////////////

search.init = function() {

    var anchor = document.getElementById('search-open');
    var form = null;

    search.data = portal.readData('search-data');

    portal.popover.attach(anchor, {
        title: search.data.form.title,
        build: function() {
            form = portal.fields.buildForm(search.data.form.rows, search.formValues());
            return form.element;
        },
        buttons: function(handle) {
            var out = [
                {label: portal.config.clearLabel, isPrimary: false, onClick: function() {
                    search.run({});
                    handle.close();
                }},
                {label: portal.config.applyLabel, isPrimary: true, onClick: function() {
                    search.run(form.read());
                    handle.close();
                }}
            ];
            return out;
        }
    });

    // Enter in any field of the form applies it
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            if (form) {
                if (form.element.contains(event.target)) {
                    search.run(form.read());
                    anchor._tippy.hide();
                }
            }
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

portal.search = search;

document.addEventListener('DOMContentLoaded', search.init);

// ////////////////////////////////////////////////////////////////////////

})();
