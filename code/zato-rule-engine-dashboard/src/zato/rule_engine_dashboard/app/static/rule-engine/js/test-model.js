'use strict';

// Data model for the tests and simulation screen: the stored test suite,
// the ruleset its scenarios run against, the run results the server
// answers with, and the structure edits. Scenario inputs nest by entity
// the way the engine reads them, expected outcomes stay flat by the
// target path the rules assign. No DOM access in this file.

(function() {

var testModel = {

    config: {
        // How long an edit waits before the server validation runs
        checkDelayMilliseconds: 300,

        // What a brand-new suite and a brand-new scenario are called
        newSuiteName: 'Test set',
        newScenarioName: 'New scenario',

        // What a run says when no ruleset exists to run against
        noRulesetMessage: 'There is no ruleset to run against yet. Author one in the editor first.',

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

    // The stored suite this screen edits - null until one exists
    suiteId: null,
    suiteVersion: null,
    suite: null,

    // Whether the suite differs from its stored version - a modified
    // suite runs through the outcomes feed, an unmodified one through
    // the run endpoint that records the run in the ruleset's history
    modified: false,

    // The ruleset the scenarios run against
    rulesetId: null,
    rulesetName: '',
    rulesetCurrentVersion: null,
    rulesetLiveVersion: null,
    documents: null,

    // What the server said last: per-scenario run results by name,
    // the statuses of the previous full run for the delta badges, and
    // the structural findings of the suite validation
    results: {},
    previousStatuses: {},
    serverErrors: [],

// ////////////////////////////////////////////////////////////////////////

    // The screen opens on the suite the address names, or on the first
    // stored one, and runs against the first stored ruleset
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

    // A suite that does not exist yet starts empty
    startNew: function() {
        this.suite = {name: this.config.newSuiteName, scenarios: []};
        this.modified = true;
    },

// ////////////////////////////////////////////////////////////////////////

    // A scenario input nests by entity - customer.creditScore lives as
    // input.customer.creditScore - while the screen reads and edits the
    // dotted paths. These two convert between the forms.
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

        // An entity with no attributes left disappears entirely
        if (Object.keys(scenario.input[head]).length === 0) {
            delete scenario.input[head];
        }
    },

// ////////////////////////////////////////////////////////////////////////

    // Values live typed in the document - numbers as numbers, yes/no as
    // booleans - and read as text in the grids
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

    // A term of the loaded vocabulary, or null for a path the vocabulary
    // does not know - unknown paths stay editable as free text
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

    // What the last run said about one scenario, or null before any run
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

    // The output rows of one scenario: every expected path plus every
    // path the last run actually assigned, each shown once
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

    // A unique name for a new or duplicated scenario
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

    // Duplicate a scenario, the copy lands right under the original
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

    // Move a scenario one step up or down in the suite
    moveScenario: function(index, offset) {
        var toIndex = index + offset;

        // Clamped at the edges, the caller learns nothing moved
        if (toIndex < 0 || toIndex >= this.suite.scenarios.length) { return false; }

        var moved = this.suite.scenarios.splice(index, 1)[0];
        this.suite.scenarios.splice(toIndex, 0, moved);
        this.modified = true;
        return true;
    },

// ////////////////////////////////////////////////////////////////////////

    // Input validation in domain terms, marked on the offending value
    // before the server ever sees it
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

    // The server checks the suite structurally after every edit
    check: function(onDone) {
        var self = this;

        data.post(this.config.urls.validate, {test_set: this.suite}, function(payload) {
            self.serverErrors = payload.errors;
            onDone();
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    // Folds one full run's answer into the results and reports the delta
    // against the previous run - the one-glance regression signal
    ingestRun: function(payload) {
        var self = this;
        var counts = {passed: 0, failed: 0, explored: 0};
        var newFailures = [];
        var fixed = [];

        payload.scenarios.forEach(function(entry) {
            self.results[entry.scenario] = entry;
            counts[entry.status] += 1;

            var previous = self.previousStatuses[entry.scenario];
            if (entry.status === 'failed' && previous === 'passed') { newFailures.push(entry.scenario); }
            if (entry.status === 'passed' && previous === 'failed') { fixed.push(entry.scenario); }
        });

        this.previousStatuses = {};
        payload.scenarios.forEach(function(entry) {
            self.previousStatuses[entry.scenario] = entry.status;
        });

        var out = {counts: counts, newFailures: newFailures, fixed: fixed};
        return out;
    },

    // A full run: the stored suite runs through the endpoint that records
    // the run in the ruleset's history, a locally edited one through the
    // outcomes feed - the results read the same either way
    runAll: function(onDone, onError) {
        var self = this;

        if (this.documents === null) {
            onError(this.config.noRulesetMessage);
            return;
        }

        var ingest = function(payload) {
            var delta = self.ingestRun(payload);
            onDone(delta);
        };

        if (!this.modified && this.suiteId !== null) {
            data.post(this.config.urls.run(this.suiteId),
                {ruleset_id: this.rulesetId, version: this.rulesetCurrentVersion}, ingest, onError);
            return;
        }

        data.post(this.config.urls.outcomes, {documents: this.documents, test_set: this.suite}, ingest, onError);
    },

    // One scenario runs alone through the outcomes feed, the rest of the
    // suite keeps its previous results
    runOne: function(scenario, onDone, onError) {
        var self = this;

        if (this.documents === null) {
            onError(this.config.noRulesetMessage);
            return;
        }

        var single = {name: this.suite.name, scenarios: [scenario]};
        data.post(this.config.urls.outcomes, {documents: this.documents, test_set: single}, function(payload) {
            var entry = payload.scenarios[0];
            self.results[scenario.name] = entry;
            onDone(entry);
        }, onError);
    },

// ////////////////////////////////////////////////////////////////////////

    // Promoting a whole outcome turns exploration into assertion. An
    // unmodified stored suite promotes through the endpoint, which stores
    // a new version right away - a locally edited one promotes in place
    // and the Save button persists everything together.
    promote: function(scenario, onDone, onError) {
        var self = this;
        var result = this.resultOf(scenario);

        if (!this.modified && this.suiteId !== null) {
            var body = {
                scenario_name: scenario.name,
                actual: result.actual,
                expected_current_version: this.suiteVersion,
            };
            data.post(this.config.urls.promote(this.suiteId), body, function(payload) {
                self.suite = payload.test_set;
                self.suiteVersion = payload.version;
                onDone();
            }, onError);
            return;
        }

        scenario.expected = JSON.parse(JSON.stringify(result.actual));
        onDone();
    },

// ////////////////////////////////////////////////////////////////////////

    save: function(onDone, onError) {
        var self = this;

        var body = {
            document: this.suite,
            comment: 'Edited test set ' + this.suite.name,
        };

        // An existing suite gains a new optimistic version, a new one
        // comes into being together with its first version
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
