'use strict';

(function() {

var editorModel = {

    config: {
        checkDelayMilliseconds: 300,

        // The host application fills all of these in through editorView.init
        urls: {},
        ruleset: null,
        rule: null,
        newRuleName: '',
        showLivePanel: false,
        navigateToRule: null,
        rulesetsUrl: '',
        tablesUrl: '',
        testsUrl: '',
    },

    definitionId: null,
    currentVersion: null,
    rulesetName: '',
    documents: {},
    ruleKey: null,

    vocabularyId: null,
    completionTerms: {},

    testSet: null,

    serverDocuments: null,
    serverErrors: [],

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

    placeholders: {
        subject: 'pick a property',
        comparator: 'how it compares',
        action: 'pick an action',
        number: 'a number',
        value: 'a value',
        set: 'one or more values',
    },

// ////////////////////////////////////////////////////////////////////////

    newRule: function(name) {
        var out = {
            name: name,
            docs: '',
            conditions: [],
            joiners: [],
            thenActions: [],
            elseActions: [],
        };
        return out;
    },

    load: function(onDone) {
        var self = this;
        var wantedRuleset = this.config.ruleset;
        var wantedRule = this.config.rule;

        data.get(this.config.urls.rulesets, function(payload) {
            var records = payload.items;
            if (wantedRuleset !== null) {
                records = records.filter(function(item) { return item.id === parseInt(wantedRuleset); });
            }

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
                } else if (self.config.newRuleName === '' && keys.length > 0) {
                    self.ruleKey = keys[0];
                }

                if (self.ruleKey !== null) {
                    self.rule = self.fromDocument(self.documents[self.ruleKey]);
                } else if (self.config.newRuleName !== '') {
                    self.rule = self.newRule(self.config.newRuleName);
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

        // Test sets only feed the live outcomes panel, which the host may not show at all
        if (!this.config.showLivePanel) {
            onDone();
            return;
        }

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

    valueText: function(node) {
        if (node.kind === 'reference') { return node.term; }
        if (node.value === true) { return 'true'; }
        if (node.value === false) { return 'false'; }
        var out = String(node.value);
        return out;
    },

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

    check: function(onDone, onError) {
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
        }, onError);
    },

// ////////////////////////////////////////////////////////////////////////

    mergedDocuments: function() {
        if (this.serverDocuments === null || Object.keys(this.serverDocuments).length === 0) { return null; }

        var out = {};
        var self = this;
        Object.keys(this.documents).forEach(function(key) {
            if (key !== self.ruleKey) { out[key] = self.documents[key]; }
        });
        Object.keys(this.serverDocuments).forEach(function(key) {
            out[key] = self.serverDocuments[key];

            // A freshly parsed document knows nothing of the stored one's active state,
            // so an editor save never silently reactivates a deactivated rule
            if (self.documents[key] !== undefined && self.documents[key].is_active !== undefined) {
                out[key].is_active = self.documents[key].is_active;
            }
        });
        return out;
    },

    save: function(onDone, onError) {
        var self = this;
        var merged = this.mergedDocuments();

        if (merged === null) {
            onError('A rule needs a finished condition and a then action.');
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

    comparatorsFor: function(path) {
        var out = this.completionTerms[path].comparators;
        return out;
    },

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

window.editorModel = editorModel;

})();
