'use strict';

(function() {

var vocabulary = {

    name: '',
    entities: [],

    adopted: {},

    isDeclared: function(path) {
        var parts = path.split('.');
        if (parts.length !== 2) { return false; }

        var entity = this.entities.filter(function(candidate) { return candidate.name === parts[0]; })[0];
        if (entity === undefined) { return false; }

        var out = entity.attributes.some(function(candidate) { return candidate.name === parts[1]; });
        return out;
    },

    attribute: function(path) {
        if (this.adopted[path] !== undefined) { return this.adopted[path]; }

        var parts = path.split('.');
        var entityName = parts[0];
        var attributeName = parts[1];

        var entity = this.entities.filter(function(candidate) { return candidate.name === entityName; })[0];
        var out = entity.attributes.filter(function(candidate) { return candidate.name === attributeName; })[0];

        return out;
    },

    pickerAttributes: function(entity) {
        var out = entity.attributes.filter(function(attribute) { return attribute.status !== 'deprecated'; });
        return out;
    },
};

window.vocabulary = vocabulary;

})();
