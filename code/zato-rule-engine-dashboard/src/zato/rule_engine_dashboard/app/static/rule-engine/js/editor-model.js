'use strict';

// Data model for the rule editor in sentence form: loading one ruleset's
// documents, converting one canonical rule document into the editable
// sentence structure and back into rule text, server-side validation with
// its structured errors, saving as a new optimistic version, and the local
// checks with quick fixes. No DOM access in this file.

(function() {

var editorModel = {

    config: {
        // How long an edit waits before the server checks run
        checkDelayMilliseconds: 300,

        urls: {
            rulesets: '/rules/rulesets/?object_type=ruleset',
            vocabularies: '/rules/rulesets/?object_type=vocabulary',
            testSets: '/rules/test-sets/',
            validate: '/rules/editor/validate/',
            render: '/rules/editor/render/',
            save: '/rules/editor/save/',
            outcomes: '/rules/editor/outcomes/',
            preview: function(id) { return '/rules/rulesets/' + id + '/preview/'; },
            vocabularyGet: function(id) { return '/rules/vocabulary/' + id + '/'; },
            completion: function(id) { return '/rules/editor/completion/' + id + '/'; },
        },
    },

    // The ruleset this screen edits and the one rule inside it
    definitionId: null,
    currentVersion: null,
    rulesetName: '',
    documents: {},
    ruleKey: null,

    // The vocabulary and its completion payload - only legal continuations
    // are ever offered, the server decides what is legal
    vocabularyId: null,
    completionTerms: {},

    // The first stored test set, for the live outcomes panel
    testSet: null,

    // What the server said about the rule as it stands right now
    serverDocuments: null,
    serverErrors: [],

    // The editable structure behind every view. A null subject, comparator
    // or target renders as a typed placeholder. Joiners sit between
    // consecutive conditions, and binds tighter than or.
    rule: null,

    comparatorSymbols: {
        'is': '==',
        'is not': '!=',
        'is less than': '<',
        'is at most': '<=',
        'is at least': '>=',
        'is more than': '>',
        'is between': 'in',
        'is one of': 'in',
        'is not one of': 'not in',
        'matches': '=~',
        'is true': '== true',
        'is false': '== false',
    },

    // Placeholder wording for the unfinished parts of a sentence, rendered
    // as dashed chips, the dashes alone say "still empty"
    placeholders: {
        subject: 'pick a property',
        comparator: 'how it compares',
        action: 'pick an action',
        number: 'a number',
        value: 'a value',
        set: 'one or more values',
    },

// ////////////////////////////////////////////////////////////////////////

    // The screen opens on the ruleset and rule the address names, or on
    // the first stored ones
    load: function(onDone) {
        var self = this;
        var search = new URLSearchParams(window.location.search);
        var wantedRuleset = search.get('ruleset');
        var wantedRule = search.get('rule');

        data.get(this.config.urls.rulesets, function(payload) {
            var records = payload.items;
            if (wantedRuleset !== null) {
                records = records.filter(function(item) { return item.id === parseInt(wantedRuleset); });
            }

            // No ruleset yet - the screen renders its empty state
            if (records.length === 0) {
                onDone();
                return;
            }

            var record = records[0];
            self.definitionId = record.id;
            self.currentVersion = record.current_version;
            self.rulesetName = record.name;

            data.get(self.config.urls.preview(record.id), function(preview) {
                self.documents = preview.document.documents;

                var keys = Object.keys(self.documents);
                if (wantedRule !== null && keys.indexOf(wantedRule) > -1) {
                    self.ruleKey = wantedRule;
                } else if (keys.length > 0) {
                    self.ruleKey = keys[0];
                }
                if (self.ruleKey !== null) {
                    self.rule = self.fromDocument(self.documents[self.ruleKey]);
                }

                self.loadVocabulary(onDone);
            }, data.reportError);
        }, data.reportError);
    },

    loadVocabulary: function(onDone) {
        var self = this;

        data.get(this.config.urls.vocabularies, function(payload) {
            if (payload.items.length === 0) {
                self.adoptRuleTerms();
                self.loadTestSet(onDone);
                return;
            }

            self.vocabularyId = payload.items[0].id;

            data.get(self.config.urls.vocabularyGet(self.vocabularyId), function(answer) {
                vocabulary.name = answer.vocabulary.name;
                vocabulary.entities = answer.vocabulary.entities;

                data.get(self.config.urls.completion(self.vocabularyId), function(completion) {
                    completion.terms.forEach(function(term) {
                        self.completionTerms[term.path] = term;
                    });
                    self.adoptRuleTerms();
                    self.loadTestSet(onDone);
                }, data.reportError);
            }, data.reportError);
        }, data.reportError);
    },

    loadTestSet: function(onDone) {
        var self = this;

        data.get(this.config.urls.testSets, function(payload) {
            if (payload.items.length === 0) {
                onDone();
                return;
            }

            data.get(self.config.urls.preview(payload.items[0].id), function(preview) {
                self.testSet = preview.document;
                onDone();
            }, data.reportError);
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    // One value node of the canonical document as the editable string
    // the chips show
    valueText: function(node) {
        if (node.kind === 'reference') { return node.term; }
        if (node.value === true) { return 'true'; }
        if (node.value === false) { return 'false'; }
        var out = String(node.value);
        return out;
    },

    // The canonical stored document as the editable sentence structure
    fromDocument: function(document) {
        var self = this;

        var conditions = document.conditions.map(function(condition) {
            var out = {
                subject: condition.subject,
                comparator: condition.comparator,
                values: condition.values.map(function(node) { return self.valueText(node); }),
            };
            return out;
        });

        var toAction = function(action) {
            var out = {target: action.target, values: [self.valueText(action.value)]};
            return out;
        };

        var out = {
            name: document.name,
            docs: document.docs,
            conditions: conditions,
            joiners: document.joiners.slice(),
            thenActions: document.then.map(toAction),
            elseActions: document['else'].map(toAction),
        };
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // How a typed value goes back into rule text: known terms stay bare
    // references, choice and text values travel quoted, everything else raw
    valueSource: function(path, value) {
        if (this.completionTerms[value] !== undefined) { return value; }

        var term = this.completionTerms[path];
        if (term !== undefined && (term.type === 'choice' || term.type === 'text')) {
            var escaped = value.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
            return "'" + escaped + "'";
        }

        return value;
    },

    conditionSource: function(condition) {
        var self = this;
        var slots = this.valueSlots(condition.comparator);

        if (slots === 0) {
            return condition.subject + ' ' + condition.comparator;
        }

        if (slots === 2) {
            var lower = this.valueSource(condition.subject, condition.values[0]);
            var upper = this.valueSource(condition.subject, condition.values[1]);
            return condition.subject + ' ' + condition.comparator + ' ' + lower + ' and ' + upper;
        }

        var parts = condition.values.map(function(value) {
            var out = self.valueSource(condition.subject, value);
            return out;
        });
        var out = condition.subject + ' ' + condition.comparator + ' ' + parts.join(', ');
        return out;
    },

    // The whole rule as the text form the parser reads - only the finished
    // parts go in, the unfinished ones stay local placeholders
    toText: function() {
        var self = this;
        var lines = ['rule', '    ' + this.rule.name];

        if (this.rule.docs !== '') {
            lines.push('docs');
            this.rule.docs.split('\n').forEach(function(docLine) {
                lines.push('    ' + docLine);
            });
        }

        lines.push('when');
        var complete = [];
        this.rule.conditions.forEach(function(condition, conditionIndex) {
            if (self.conditionIsComplete(condition)) { complete.push(conditionIndex); }
        });
        complete.forEach(function(conditionIndex, position) {
            var line = '    ' + self.conditionSource(self.rule.conditions[conditionIndex]);

            // The joiner in front of the next finished condition closes this line
            if (position < complete.length - 1) {
                line += ' ' + self.rule.joiners[complete[position + 1] - 1];
            }
            lines.push(line);
        });

        var pushActions = function(keyword, actions) {
            var finished = actions.filter(function(action) { return self.actionIsComplete(action); });
            if (finished.length === 0) { return; }

            lines.push(keyword);
            finished.forEach(function(action) {
                lines.push('    ' + action.target + ' = ' + self.valueSource(action.target, action.values[0]));
            });
        };
        pushActions('then', this.rule.thenActions);
        pushActions('else', this.rule.elseActions);

        var out = lines.join('\n') + '\n';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    conditionIsComplete: function(condition) {
        if (condition.subject === null || condition.comparator === null) { return false; }

        var slots = this.valueSlots(condition.comparator);
        if (slots === -1) { return condition.values.length > 0; }

        var out = condition.values.slice(0, slots).every(function(value) { return value !== ''; });
        return out;
    },

    actionIsComplete: function(action) {
        var out = action.target !== null && action.values[0] !== '';
        return out;
    },

    ruleIsRunnable: function() {
        var self = this;
        var anyCondition = this.rule.conditions.some(function(condition) {
            return self.conditionIsComplete(condition);
        });
        var anyThen = this.rule.thenActions.some(function(action) { return self.actionIsComplete(action); });

        var out = anyCondition && anyThen;
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // The server parses the text form and checks its semantics against the
    // vocabulary - the canonical documents come back alongside the errors
    check: function(onDone) {
        var self = this;

        if (!this.ruleIsRunnable()) {
            this.serverDocuments = null;
            this.serverErrors = [];
            onDone();
            return;
        }

        var body = {text: this.toText(), ruleset_name: this.rulesetName};
        if (this.vocabularyId !== null) { body.vocabulary_id = this.vocabularyId; }

        data.post(this.config.urls.validate, body, function(payload) {
            self.serverDocuments = payload.documents;
            self.serverErrors = payload.errors;
            onDone();
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    // The whole ruleset with the edited rule swapped in - what save stores
    // and what the live outcomes run against
    mergedDocuments: function() {
        if (this.serverDocuments === null || Object.keys(this.serverDocuments).length === 0) { return null; }

        var out = {};
        var self = this;
        Object.keys(this.documents).forEach(function(key) {
            if (key !== self.ruleKey) { out[key] = self.documents[key]; }
        });
        Object.keys(this.serverDocuments).forEach(function(key) {
            out[key] = self.serverDocuments[key];
        });
        return out;
    },

    save: function(onDone, onError) {
        var self = this;
        var merged = this.mergedDocuments();

        if (merged === null) {
            onError('The rule needs at least one finished condition and one then action before it can be saved.');
            return;
        }

        var body = {
            definition_id: this.definitionId,
            expected_current_version: this.currentVersion,
            document: {documents: merged},
            comment: 'Edited rule ' + this.rule.name,
        };
        data.post(this.config.urls.save, body, function(payload) {
            self.currentVersion = payload.version;
            self.documents = merged;
            self.ruleKey = Object.keys(self.serverDocuments)[0];
            onDone(payload);
        }, onError);
    },

// ////////////////////////////////////////////////////////////////////////

    // Only the comparators the server offers for the term are ever shown,
    // so unreachable phrases never appear in the completion menu
    comparatorsFor: function(path) {
        var out = this.completionTerms[path].comparators;
        return out;
    },

    // How many value slots a comparator needs: 0 for yes/no phrases, 2 for
    // between, -1 for any number (the one-of pair), 1 for everything else
    valueSlots: function(comparator) {
        if (comparator === 'is true' || comparator === 'is false') { return 0; }
        if (comparator === 'is between') { return 2; }
        if (comparator === 'is one of' || comparator === 'is not one of') { return -1; }
        return 1;
    },

    valuePlaceholder: function(attribute) {
        if (attribute.type === 'number' || attribute.type === 'number range') { return this.placeholders.number; }
        return this.placeholders.value;
    },

    // Keep whatever values still fit when the comparator changes
    coerceValues: function(condition) {
        var slots = this.valueSlots(condition.comparator);

        if (slots === 0) { condition.values = []; }
        if (slots === 1) { condition.values = condition.values.slice(0, 1); }
        if (slots === 2) {
            condition.values = condition.values.slice(0, 2);
            while (condition.values.length < 2) { condition.values.push(''); }
        }

        if (condition.values.length === 0 && slots === 1) { condition.values = ['']; }
    },

// ////////////////////////////////////////////////////////////////////////

    // Consecutive and-joined conditions form one group, or separates groups,
    // the standard precedence where and binds tighter than or
    conditionGroups: function() {
        var out = [];
        if (this.rule.conditions.length === 0) { return out; }

        var current = [0];
        this.rule.joiners.forEach(function(joiner, joinerIndex) {
            if (joiner === 'and') {
                current.push(joinerIndex + 1);
            } else {
                out.push(current);
                current = [joinerIndex + 1];
            }
        });
        out.push(current);

        return out;
    },

    hasOrJoiner: function() {
        var out = this.rule.joiners.indexOf('or') > -1;
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // Everything the "then" and "else" parts can do, derived from the
    // vocabulary: yes/no attributes give their two settings, the rest a
    // set phrase with an editable value
    actionChoices: function() {
        var out = [];

        vocabulary.entities.forEach(function(entity) {
            vocabulary.pickerAttributes(entity).forEach(function(attribute) {
                var path = entity.name + '.' + attribute.name;
                if (attribute.type === 'yes/no') {
                    out.push({label: 'set ' + attribute.phrase + ' to true', target: path, values: ['true']});
                    out.push({label: 'set ' + attribute.phrase + ' to false', target: path, values: ['false']});
                } else {
                    out.push({label: 'set ' + attribute.phrase, target: path, values: ['']});
                }
            });
        });

        return out;
    },

// ////////////////////////////////////////////////////////////////////////
};

// The adoption of undeclared terms, the typed-value checks and the
// problems list live in editor-checks.js, which augments this namespace.
window.editorModel = editorModel;

})();
