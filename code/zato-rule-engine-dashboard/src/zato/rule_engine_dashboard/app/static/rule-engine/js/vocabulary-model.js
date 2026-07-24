'use strict';

// Data model for the vocabulary screen: loading the stored document,
// the where-used index, rename with its impact preview, deprecate,
// delete, the paste-a-payload bootstrap and infer-from-typing - all
// against the JSON views, every document change stored as a new
// optimistic version. No DOM access here.

(function() {

var vocabularyModel = {

    config: {
        // The name a vocabulary created on this screen starts with
        newVocabularyName: 'Vocabulary',
        // The ruleset name the parser needs when infer reads typed rules
        inferRulesetName: 'proposed',

        urls: {
            vocabularies: '/rules/rulesets/?object_type=vocabulary',
            rulesets: '/rules/rulesets/?object_type=ruleset',
            whereUsed: '/rules/vocabulary/where-used/?term=',
            rename: '/rules/vocabulary/rename/',
            bootstrap: '/rules/vocabulary/bootstrap/',
            save: '/rules/editor/save/',
            get: function(id) { return '/rules/vocabulary/' + id + '/'; },
            infer: function(id) { return '/rules/vocabulary/' + id + '/infer/'; },
        },
    },

    // The stored definition this screen edits - null until a vocabulary
    // exists, the bootstrap panel creates the first one
    definitionId: null,
    currentVersion: null,

    // Ruleset names by id, for the where-used groups
    rulesetNames: {},

// ////////////////////////////////////////////////////////////////////////

    // The screen opens on the vocabulary the address names, or on the
    // first stored one
    load: function(onDone) {
        var self = this;
        var wanted = new URLSearchParams(window.location.search).get('vocabulary');

        data.get(this.config.urls.rulesets, function(payload) {
            payload.items.forEach(function(item) { self.rulesetNames[item.id] = item.name; });

            data.get(self.config.urls.vocabularies, function(inner) {
                var records = inner.items;

                if (wanted !== null) {
                    records = records.filter(function(item) { return item.id === parseInt(wanted); });
                }

                // No vocabulary yet - the screen renders its empty state
                // and the bootstrap panel creates the first one
                if (records.length === 0) {
                    onDone();
                    return;
                }

                var record = records[0];
                self.definitionId = record.id;
                self.currentVersion = record.current_version;

                data.get(self.config.urls.get(record.id), function(answer) {
                    vocabulary.name = answer.vocabulary.name;
                    vocabulary.entities = answer.vocabulary.entities;
                    onDone();
                }, data.reportError);
            }, data.reportError);
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    allPaths: function() {
        var out = [];
        vocabulary.entities.forEach(function(entity) {
            entity.attributes.forEach(function(attribute) {
                out.push(entity.name + '.' + attribute.name);
            });
        });
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // Every indexed place one term is referenced from, grouped by the
    // ruleset the reference lives in. This is what a rename shows before
    // it commits and what blocks a delete.
    whereUsed: function(path, onDone) {
        var self = this;

        data.get(this.config.urls.whereUsed + encodeURIComponent(path), function(payload) {
            var groups = [];
            var byDefinition = {};

            payload.items.forEach(function(item) {
                if (byDefinition[item.definition_id] === undefined) {
                    byDefinition[item.definition_id] = [];
                    groups.push({definitionId: item.definition_id, entries: byDefinition[item.definition_id]});
                }
                byDefinition[item.definition_id].push(item);
            });

            groups.forEach(function(group) {
                var name = self.rulesetNames[group.definitionId];
                if (name === undefined) { name = 'ruleset ' + group.definitionId; }
                group.name = name;
            });

            onDone({groups: groups, count: payload.items.length, canDelete: payload.can_delete});
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    // Every document change is stored as a new optimistic version, a
    // brand-new vocabulary comes into being with its first one
    saveDocument: function(comment, onDone) {
        var self = this;

        // A vocabulary born on this screen starts under the default name
        if (this.definitionId === null && vocabulary.name === '') {
            vocabulary.name = this.config.newVocabularyName;
        }

        var document = {name: vocabulary.name, entities: vocabulary.entities};

        var body;
        if (this.definitionId === null) {
            body = {name: this.config.newVocabularyName, object_type: 'vocabulary', document: document, comment: comment};
        } else {
            body = {definition_id: this.definitionId, expected_current_version: this.currentVersion,
                document: document, comment: comment};
        }

        data.post(this.config.urls.save, body, function(payload) {
            self.definitionId = payload.definition_id;
            self.currentVersion = payload.version;
            onDone();
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    // A rename lands everywhere at once, that is the whole point: the
    // referencing rulesets are rewritten together with the vocabulary,
    // so where-used reads the same after as before
    renamePreview: function(path, newPath, onDone) {
        data.post(this.config.urls.rename, {old_term: path, new_term: newPath, dry_run: true}, onDone, data.reportError);
    },

    renameApply: function(path, newPath, onDone) {
        data.post(this.config.urls.rename, {old_term: path, new_term: newPath, dry_run: false}, onDone, data.reportError);
    },

    rename: function(path, newName, onDone) {
        var self = this;
        var attribute = vocabulary.attribute(path);
        var newPath = path.split('.')[0] + '.' + newName;

        this.renameApply(path, newPath, function(report) {
            attribute.name = newName;
            self.saveDocument('Rename term ' + path + ' to ' + newPath, function() {
                onDone(report);
            });
        });
    },

// ////////////////////////////////////////////////////////////////////////

    // A drag in the tree: reorder within an entity, or move to another
    // entity, which is a path change and propagates like a rename does
    moveTerm: function(path, targetEntityName, targetIndex, onDone) {
        var self = this;
        var sourceEntityName = path.split('.')[0];
        var attributeName = path.split('.')[1];

        var source = vocabulary.entities.filter(function(candidate) { return candidate.name === sourceEntityName; })[0];
        var position = source.attributes.map(function(candidate) { return candidate.name; }).indexOf(attributeName);
        var attribute = source.attributes[position];

        // Taking the term out first shifts later indexes in the same entity
        source.attributes.splice(position, 1);
        if (sourceEntityName === targetEntityName && targetIndex > position) { targetIndex -= 1; }

        var target = vocabulary.entities.filter(function(candidate) { return candidate.name === targetEntityName; })[0];
        target.attributes.splice(targetIndex, 0, attribute);

        var newPath = targetEntityName + '.' + attributeName;
        var comment = newPath === path
            ? 'Reorder term ' + path
            : 'Move term ' + path + ' to ' + newPath;

        // Crossing entities changes the path, which is a rename for every
        // referencing ruleset
        if (newPath === path) {
            this.saveDocument(comment, function() { onDone(newPath); });
        } else {
            this.renameApply(path, newPath, function() {
                self.saveDocument(comment, function() { onDone(newPath); });
            });
        }
    },

// ////////////////////////////////////////////////////////////////////////

    deprecate: function(path, onDone) {
        var attribute = vocabulary.attribute(path);
        attribute.status = 'deprecated';
        this.saveDocument('Deprecate term ' + path, onDone);
    },

    restore: function(path, onDone) {
        var attribute = vocabulary.attribute(path);
        attribute.status = '';
        this.saveDocument('Restore term ' + path, onDone);
    },

    // Deleting is only ever possible when nothing uses the term, the
    // where-used index is the gate
    deleteTerm: function(path, onDone) {
        var entityName = path.split('.')[0];
        var attributeName = path.split('.')[1];
        var entity = vocabulary.entities.filter(function(candidate) { return candidate.name === entityName; })[0];
        entity.attributes = entity.attributes.filter(function(candidate) { return candidate.name !== attributeName; });

        // An entity without a single attribute left disappears with it
        vocabulary.entities = vocabulary.entities.filter(function(candidate) { return candidate.attributes.length > 0; });

        this.saveDocument('Delete term ' + path, onDone);
    },

// ////////////////////////////////////////////////////////////////////////

    // The paste-a-payload bootstrap: one example JSON payload becomes
    // terms, deterministically - names from the fields, types from the
    // values - the server does the derivation
    inferFromPayload: function(payloadText, onDone, onError) {
        var payload;
        try {
            payload = JSON.parse(payloadText);
        } catch (error) {
            onError('That is not valid JSON: ' + error.message);
            return;
        }
        if (payload === null || typeof payload !== 'object' || Array.isArray(payload)) {
            onError('The example must be one JSON object, the way one request payload looks.');
            return;
        }

        var known = this.allPaths();

        data.post(this.config.urls.bootstrap, {payload: payload}, function(answer) {
            var terms = [];

            answer.vocabulary.entities.forEach(function(entity) {
                entity.attributes.forEach(function(attribute) {
                    var path = entity.name + '.' + attribute.name;
                    terms.push({entity: entity.name, name: attribute.name, type: attribute.type,
                        phrase: attribute.phrase, exists: known.indexOf(path) > -1});
                });
            });

            onDone(terms);
        }, onError);
    },

// ////////////////////////////////////////////////////////////////////////

    // Infer-from-typing: unknown terms in pasted rules come back as
    // proposals with types inferred from how the rules use them
    inferFromRules: function(text, onDone, onError) {
        var known = this.allPaths();

        data.post(this.config.urls.infer(this.definitionId),
            {text: text, ruleset_name: this.config.inferRulesetName}, function(answer) {

            answer.proposals.forEach(function(proposal) {
                proposal.exists = known.indexOf(proposal.path) > -1;
            });

            onDone(answer.proposals, answer.errors);
        }, onError);
    },

// ////////////////////////////////////////////////////////////////////////

    // A term added by hand: the phrase and the type-specific defaults are
    // filled in and curated in place afterwards
    addTerm: function(entityName, name, type, onDone) {
        var entity = vocabulary.entities.filter(function(candidate) { return candidate.name === entityName; })[0];
        if (entity === undefined) {
            entity = {name: entityName, attributes: []};
            vocabulary.entities.push(entity);
        }

        var words = name.replace(/([A-Z])/g, ' $1').toLowerCase();
        var attribute = {name: name, type: type, phrase: 'the ' + entityName + ' ' + words, status: ''};
        if (type === 'choice') { attribute.values = []; }
        if (type === 'number range') { attribute.domain = {low: 0, high: 100}; }

        entity.attributes.push(attribute);

        var path = entityName + '.' + name;
        this.saveDocument('Add term ' + path, function() { onDone(path); });
    },

    // Terms from a payload preview or from infer proposals, known ones
    // are skipped
    addTerms: function(terms, comment, onDone) {
        var added = 0;
        var firstPath = null;

        terms.forEach(function(term) {
            if (term.exists) { return; }

            var entity = vocabulary.entities.filter(function(candidate) { return candidate.name === term.entity; })[0];
            if (entity === undefined) {
                entity = {name: term.entity, attributes: []};
                vocabulary.entities.push(entity);
            }

            entity.attributes.push({name: term.name, type: term.type, phrase: term.phrase, status: ''});
            added += 1;

            if (firstPath === null) { firstPath = term.entity + '.' + term.name; }
        });

        this.saveDocument(comment, function() { onDone(added, firstPath); });
    },
};

window.vocabularyModel = vocabularyModel;

})();
