'use strict';

// The vocabulary is the data model the rules run against, declared once.
// Every screen derives its types, domains, closed pick lists and natural
// language phrasing from it. This file holds the loaded document and the
// lookups over it - vocabulary-model.js fills it from the JSON views.

(function() {

var vocabulary = {

    // The loaded document - one name, entities with typed attributes
    name: '',
    entities: [],

    // Terms the open documents use that no entity declares - rules and
    // vocabularies are edited independently, so a rule may name a flat
    // term or one whose entity is gone. The editor adopts each of them
    // at load time so that every lookup on the screen answers.
    adopted: {},

    // Whether a path resolves to a declared attribute
    isDeclared: function(path) {
        var parts = path.split('.');
        if (parts.length !== 2) { return false; }

        var entity = this.entities.filter(function(candidate) { return candidate.name === parts[0]; })[0];
        if (entity === undefined) { return false; }

        var out = entity.attributes.some(function(candidate) { return candidate.name === parts[1]; });
        return out;
    },

    // Look up an attribute by its full path, e.g. customer.creditScore
    attribute: function(path) {
        if (this.adopted[path] !== undefined) { return this.adopted[path]; }

        var parts = path.split('.');
        var entityName = parts[0];
        var attributeName = parts[1];

        var entity = this.entities.filter(function(candidate) { return candidate.name === entityName; })[0];
        var out = entity.attributes.filter(function(candidate) { return candidate.name === attributeName; })[0];

        return out;
    },

    // What the pickers on every screen offer: deprecated terms keep old
    // rules running but never appear in a picker again
    pickerAttributes: function(entity) {
        var out = entity.attributes.filter(function(attribute) { return attribute.status !== 'deprecated'; });
        return out;
    },
};

window.vocabulary = vocabulary;

})();
