'use strict';

(function() {

var testModel = {

    config: {
        checkDelayMilliseconds: 300,

        newSuiteName: 'Test set',
        newScenarioName: 'New scenario',

        noRulesetMessage: 'No ruleset to run against yet',

        urls: {
            suites: '/rules/test-sets/',
            rulesets: '/rules/rulesets/?object_type=ruleset',
            validate: '/rules/test-sets/validate/',
            outcomes: '/rules/editor/outcomes/',
            save: '/rules/editor/save/',
            simulation: '/rules/simulation/',
            championChallenger: '/rules/champion-challenger/',
            run: function(id) { return '/rules/test-sets/' + id + '/run/'; },
            promote: function(id) { return '/rules/test-sets/' + id + '/promote/'; },
            preview: function(id) { return '/rules/rulesets/' + id + '/preview/'; },
            vocabularies: '/rules/rulesets/?object_type=vocabulary',
            vocabularyGet: function(id) { return '/rules/vocabulary/' + id + '/'; },
        },
    },

    suiteId: null,
    suiteVersion: null,
    suite: null,

    modified: false,

    rulesetId: null,
    rulesetName: '',
    rulesetCurrentVersion: null,
    rulesetLiveVersion: null,
    documents: null,

    results: {},
    previousStatuses: {},
    serverErrors: [],

// ////////////////////////////////////////////////////////////////////////

    load: function(onDone) {
        var self = this;
        var wanted = new URLSearchParams(window.location.search).get('suite');

        data.get(this.config.urls.suites, function(payload) {
            var records = payload.items;
            if (wanted !== null) {
                records = records.filter(function(item) { return item.id === parseInt(wanted); });
            }

            if (records.length === 0) {
                self.loadRuleset(onDone);
                return;
            }

            var record = records[0];
            self.suiteId = record.id;
            self.suiteVersion = record.current_version;

            data.get(self.config.urls.preview(record.id), function(preview) {
                self.suite = preview.document;
                self.loadRuleset(onDone);
            }, data.reportError);
        }, data.reportError);
    },

    loadRuleset: function(onDone) {
        var self = this;

        data.get(this.config.urls.rulesets, function(payload) {
            if (payload.items.length === 0) {
                self.loadVocabulary(onDone);
                return;
            }

            var record = payload.items[0];
            self.rulesetId = record.id;
            self.rulesetName = record.name;
            self.rulesetCurrentVersion = record.current_version;
            self.rulesetLiveVersion = record.live_version;

            data.get(self.config.urls.preview(record.id), function(preview) {
                self.documents = preview.document.documents;
                self.loadVocabulary(onDone);
            }, data.reportError);
        }, data.reportError);
    },

    loadVocabulary: function(onDone) {
        var self = this;

        data.get(this.config.urls.vocabularies, function(payload) {
            if (payload.items.length === 0) {
                onDone();
                return;
            }

            data.get(self.config.urls.vocabularyGet(payload.items[0].id), function(answer) {
                vocabulary.name = answer.vocabulary.name;
                vocabulary.entities = answer.vocabulary.entities;
                onDone();
            }, data.reportError);
        }, data.reportError);
    },

    startNew: function() {
        this.suite = {name: this.config.newSuiteName, scenarios: []};
        this.modified = true;
    },

// ////////////////////////////////////////////////////////////////////////

    flatten: function(mapping) {
        var out = {};

        Object.keys(mapping).forEach(function(key) {
            var value = mapping[key];
            if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
                Object.keys(value).forEach(function(sub) {
                    out[key + '.' + sub] = value[sub];
                });
            } else {
                out[key] = value;
            }
        });

        return out;
    },

    setInput: function(scenario, path, value) {
        var separator = path.indexOf('.');
        if (separator === -1) {
            scenario.input[path] = value;
            return;
        }

        var head = path.slice(0, separator);
        if (scenario.input[head] === undefined) { scenario.input[head] = {}; }
        scenario.input[head][path.slice(separator + 1)] = value;
    },

    removeInput: function(scenario, path) {
        var separator = path.indexOf('.');
        if (separator === -1) {
            delete scenario.input[path];
            return;
        }

        var head = path.slice(0, separator);
        delete scenario.input[head][path.slice(separator + 1)];

        if (Object.keys(scenario.input[head]).length === 0) {
            delete scenario.input[head];
        }
    },

// ////////////////////////////////////////////////////////////////////////

    displayValue: function(value) {
        if (value === true) { return 'true'; }
        if (value === false) { return 'false'; }

        var out = String(value);
        return out;
    },

    typedValue: function(path, text) {
        var term = this.termFor(path);
        if (term === null) { return text; }

        if (term.type === 'yes/no') { return text === 'true'; }

        var isNumeric = term.type === 'number' || term.type === 'number range';
        if (isNumeric && /^-?\d+(?:\.\d+)?$/.test(text)) { return +text; }

        return text;
    },

// ////////////////////////////////////////////////////////////////////////

    termFor: function(path) {
        var parts = path.split('.');
        if (parts.length !== 2) { return null; }

        var entity = vocabulary.entities.filter(function(candidate) { return candidate.name === parts[0]; })[0];
        if (entity === undefined) { return null; }

        var attribute = entity.attributes.filter(function(candidate) { return candidate.name === parts[1]; })[0];
        if (attribute === undefined) { return null; }

        return attribute;
    },

    phraseFor: function(path) {
        var term = this.termFor(path);
        var out = term === null ? path : term.phrase;
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    scenarioAt: function(index) {
        var out = this.suite.scenarios[index];
        return out;
    },

    resultOf: function(scenario) {
        var out = this.results[scenario.name];
        if (out === undefined) { out = null; }
        return out;
    },

    statusOf: function(scenario) {
        var result = this.resultOf(scenario);
        var out = result === null ? 'notRun' : result.status;
        return out;
    },

    hasExpectations: function(scenario) {
        var out = Object.keys(scenario.expected).length > 0;
        return out;
    },

    inputPaths: function(scenario) {
        var out = Object.keys(this.flatten(scenario.input));
        return out;
    },

    outputPaths: function(scenario) {
        var out = Object.keys(scenario.expected);

        var result = this.resultOf(scenario);
        if (result !== null) {
            Object.keys(result.actual).forEach(function(path) {
                if (out.indexOf(path) === -1) { out.push(path); }
            });
        }

        out.sort();
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    uniqueName: function(base) {
        var names = this.suite.scenarios.map(function(scenario) { return scenario.name; });
        if (names.indexOf(base) === -1) { return base; }

        var counter = 2;
        while (names.indexOf(base + ' ' + counter) > -1) { counter += 1; }

        var out = base + ' ' + counter;
        return out;
    },

    addScenario: function() {
        var scenario = {name: this.uniqueName(this.config.newScenarioName), input: {}, expected: {}};
        this.suite.scenarios.push(scenario);
        this.modified = true;
        return scenario;
    },

    duplicateScenario: function(index) {
        var original = this.suite.scenarios[index];
        var copy = JSON.parse(JSON.stringify(original));
        copy.name = this.uniqueName(original.name + ' (copy)');

        this.suite.scenarios.splice(index + 1, 0, copy);
        this.modified = true;
        return copy;
    },

    deleteScenario: function(index) {
        var removed = this.suite.scenarios.splice(index, 1)[0];
        delete this.results[removed.name];
        this.modified = true;
    },

    moveScenario: function(index, offset) {
        var toIndex = index + offset;

        if (toIndex < 0 || toIndex >= this.suite.scenarios.length) { return false; }

        var moved = this.suite.scenarios.splice(index, 1)[0];
        this.suite.scenarios.splice(toIndex, 0, moved);
        this.modified = true;
        return true;
    },

// ////////////////////////////////////////////////////////////////////////

    validateInput: function(scenario) {
        var self = this;
        var errors = [];
        var flat = this.flatten(scenario.input);

        Object.keys(flat).forEach(function(path) {
            var term = self.termFor(path);
            if (term === null) { return; }

            var value = flat[path];

            if (term.type === 'number range') {
                if (value < term.domain.low || value > term.domain.high) {
                    errors.push({path: path, text: term.phrase + ' must be between ' + term.domain.low +
                        ' and ' + term.domain.high + ', got ' + self.displayValue(value) + '.'});
                }
            }

            if (term.type === 'choice' && term.values.indexOf(value) === -1) {
                errors.push({path: path, text: '"' + self.displayValue(value) + '" is not a known value of ' +
                    term.phrase + '. Known values: ' + term.values.join(', ') + '.'});
            }
        });

        return errors;
    },

// ////////////////////////////////////////////////////////////////////////

    check: function(onDone, onError) {
        var self = this;

        data.post(this.config.urls.validate, {test_set: this.suite}, function(payload) {
            self.serverErrors = payload.errors;
            onDone();
        }, onError);
    },

// ////////////////////////////////////////////////////////////////////////

    save: function(onDone, onError) {
        var self = this;

        var body = {
            document: this.suite,
            comment: 'Edited test set ' + this.suite.name,
        };

        if (this.suiteId !== null) {
            body.definition_id = this.suiteId;
            body.expected_current_version = this.suiteVersion;
        } else {
            body.name = this.suite.name;
            body.object_type = 'test-set';
        }

        data.post(this.config.urls.save, body, function(payload) {
            self.suiteId = payload.definition_id;
            self.suiteVersion = payload.version;
            self.modified = false;
            onDone(payload);
        }, onError);
    },
};

window.testModel = testModel;

})();
