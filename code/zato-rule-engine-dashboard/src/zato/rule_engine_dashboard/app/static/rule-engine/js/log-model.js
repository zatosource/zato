'use strict';

// Data model for the decision log screen: the stored decisions of one
// ruleset as the server pages them, the aggregate counts every card
// drills down from, one decision opened into its full story, the draft
// replay and the per-rule firing counts. No DOM access in this file.

(function() {

var logModel = {

    config: {
        // How many decisions one page of the list shows
        pageSize: 200,

        // The date ranges the toolbar offers, in days
        ranges: [1, 3, 7],
        defaultRangeDays: 7,

        // How long the search waits after the last keystroke before it
        // filters a full page of decisions again
        searchDelayMilliseconds: 120,

        // Every promoted outcome as the label its card shows
        outcomeLabels: {
            'matched': 'matched',
            'no-match': 'no match',
            'error': 'errors',
        },

        // What a scenario copied from the log is called and where it goes
        copiedSuiteName: 'Test set',
        copyComment: function(decisionId) { return 'Added decision ' + decisionId + ' as a scenario'; },

        urls: {
            rulesets: '/rules/rulesets/?object_type=ruleset',
            vocabularies: '/rules/rulesets/?object_type=vocabulary',
            vocabularyGet: function(id) { return '/rules/vocabulary/' + id + '/'; },
            suites: '/rules/test-sets/',
            preview: function(id) { return '/rules/rulesets/' + id + '/preview/'; },
            decisions: '/rules/decisions/',
            aggregates: '/rules/decisions/aggregates/',
            detail: function(id) { return '/rules/decisions/' + id + '/'; },
            toScenario: function(id) { return '/rules/decisions/' + id + '/to-scenario/'; },
            replay: function(id) { return '/rules/decisions/' + id + '/replay/'; },
            ruleCounts: function(id) { return '/rules/rulesets/' + id + '/rule-counts/'; },
            save: '/rules/editor/save/',
        },
    },

    // The ruleset whose decisions this screen shows
    rulesetId: null,
    rulesetName: '',
    currentVersion: null,
    liveVersion: null,

    // What the server answered last: the current page of decisions and
    // the aggregate counts over the same range
    items: [],
    aggregates: null,

    // The opened decision joined to the version that made it, plus the
    // optional draft replay of its input
    detail: null,
    replayResult: null,

// ////////////////////////////////////////////////////////////////////////

    // The screen opens on the ruleset the address names, or on the first
    // stored one, with the vocabulary for readable attribute phrases
    load: function(onDone) {
        var self = this;
        var wanted = new URLSearchParams(window.location.search).get('ruleset');

        data.get(this.config.urls.rulesets, function(payload) {
            var records = payload.items;
            if (wanted !== null) {
                records = records.filter(function(item) { return item.id === parseInt(wanted); });
            }

            if (records.length === 0) {
                onDone();
                return;
            }

            var record = records[0];
            self.rulesetId = record.id;
            self.rulesetName = record.name;
            self.currentVersion = record.current_version;
            self.liveVersion = record.live_version;

            self.loadVocabulary(onDone);
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

// ////////////////////////////////////////////////////////////////////////

    // The server-side filter every list and aggregate request shares:
    // the ruleset, the date range and the outcome facet
    filterQuery: function(rangeDays, outcome) {
        var since = new Date(Date.now() - rangeDays * 24 * 60 * 60 * 1000);
        var parts = ['ruleset_id=' + this.rulesetId, 'start_time=' + since.toISOString()];

        if (outcome !== null) {
            parts.push('outcome=' + encodeURIComponent(outcome));
        }

        var out = parts.join('&');
        return out;
    },

    // One refresh: the aggregates over the range and the page of
    // decisions under the outcome facet, in one sequence
    refresh: function(rangeDays, outcome, onDone) {
        var self = this;

        var aggregatesUrl = this.config.urls.aggregates + '?' + this.filterQuery(rangeDays, null);
        data.get(aggregatesUrl, function(aggregates) {
            self.aggregates = aggregates;

            var listUrl = self.config.urls.decisions + '?' + self.filterQuery(rangeDays, outcome) +
                '&limit=' + self.config.pageSize;
            data.get(listUrl, function(payload) {
                self.items = payload.items;
                onDone();
            }, data.reportError);
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    // The client-side facets over the loaded page: the loose search over
    // business keys and decision ids, and "everything for the value I
    // clicked" over the stories the page carries
    filtered: function(search, valueFilter) {
        var needle = search.trim().toLowerCase();

        var out = this.items.filter(function(record) {
            if (valueFilter !== null) {
                if (record.story === null) { return false; }

                var flat = logModel.flatten(record.story.input);
                var inInput = String(flat[valueFilter.path]) === valueFilter.value;
                var inOutput = String(record.story.outputs[valueFilter.path]) === valueFilter.value;
                if (!inInput && !inOutput) { return false; }
            }

            if (needle === '') { return true; }

            // An unkeyed decision still matches by its id
            var key = record.business_key === null ? '' : record.business_key;
            var haystack = (key + ' ' + record.decision_id).toLowerCase();
            return haystack.indexOf(needle) > -1;
        });

        return out;
    },

    itemById: function(decisionId) {
        var out = this.items.filter(function(record) { return record.decision_id === decisionId; })[0];
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // Aggregate counts as the cards read them - every promoted outcome
    // that occurred plus the total, over the searched range
    counts: function() {
        var self = this;
        var total = 0;
        var byOutcome = {};

        this.aggregates.outcomes.forEach(function(point) {
            total += point.count;
            byOutcome[point.key] = point.count;
        });

        var outcomes = Object.keys(this.config.outcomeLabels).map(function(outcome) {
            var count = byOutcome[outcome] === undefined ? 0 : byOutcome[outcome];
            return {outcome: outcome, label: self.config.outcomeLabels[outcome], count: count};
        });

        var out = {total: total, outcomes: outcomes};
        return out;
    },

    // The capture readout: how many decisions of the loaded page kept
    // their full story - errors always do, successes follow the dial
    captureReadout: function() {
        var successTotal = 0;
        var successKept = 0;

        this.items.forEach(function(record) {
            if (record.is_error) { return; }
            successTotal += 1;
            if (record.has_payload) { successKept += 1; }
        });

        var out = {successTotal: successTotal, successKept: successKept};
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // A story input nests by entity while the screen reads dotted paths
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

    // The readable phrase of one path, or the path itself when the
    // vocabulary does not know it
    phraseFor: function(path) {
        var parts = path.split('.');
        if (parts.length !== 2) { return path; }

        var entity = vocabulary.entities.filter(function(candidate) { return candidate.name === parts[0]; })[0];
        if (entity === undefined) { return path; }

        var attribute = entity.attributes.filter(function(candidate) { return candidate.name === parts[1]; })[0];
        if (attribute === undefined) { return path; }

        return attribute.phrase;
    },

    displayValue: function(value) {
        if (value === true) { return 'true'; }
        if (value === false) { return 'false'; }

        var out = String(value);
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // One decision opened into its story, joined to the exact version
    // of the rules that made it
    open: function(decisionId, onDone) {
        var self = this;
        this.replayResult = null;

        data.get(this.config.urls.detail(decisionId), function(payload) {
            self.detail = payload;
            onDone();
        }, data.reportError);
    },

    // The opened decision's input replayed against the newest stored
    // version - what the draft would decide today
    replay: function(onDone, onError) {
        var self = this;
        var decisionId = this.detail.decision.decision_id;

        data.post(this.config.urls.replay(decisionId), {version: this.currentVersion}, function(payload) {
            self.replayResult = payload.result;
            onDone();
        }, onError);
    },

// ////////////////////////////////////////////////////////////////////////

    // One click copies the opened decision into the first stored test
    // set - the input as given, the outputs as the expectations - and
    // stores the suite as a new version. Without a stored suite the
    // scenario becomes the first one of a brand-new set.
    addToTestSet: function(onDone, onError) {
        var self = this;
        var decisionId = this.detail.decision.decision_id;

        data.post(this.config.urls.toScenario(decisionId), {}, function(answer) {
            var scenario = answer.scenario;

            data.get(self.config.urls.suites, function(payload) {
                if (payload.items.length === 0) {
                    var fresh = {name: self.config.copiedSuiteName, scenarios: [scenario]};
                    self.saveSuite(fresh, null, null, decisionId, onDone, onError);
                    return;
                }

                var record = payload.items[0];
                data.get(self.config.urls.preview(record.id), function(preview) {
                    var suite = preview.document;
                    suite.scenarios.push(scenario);
                    self.saveSuite(suite, record.id, record.current_version, decisionId, onDone, onError);
                }, onError);
            }, onError);
        }, onError);
    },

    saveSuite: function(suite, suiteId, suiteVersion, decisionId, onDone, onError) {
        var body = {
            document: suite,
            comment: this.config.copyComment(decisionId),
        };

        // An existing suite gains a new optimistic version, a new one
        // comes into being together with its first version
        if (suiteId !== null) {
            body.definition_id = suiteId;
            body.expected_current_version = suiteVersion;
        } else {
            body.name = suite.name;
            body.object_type = 'test-set';
        }

        data.post(this.config.urls.save, body, function() { onDone(suite.name); }, onError);
    },

// ////////////////////////////////////////////////////////////////////////

    // Per-rule firing counts over the range, with the live rules that
    // never fired at all - the quiet ones are the interesting ones
    ruleCounts: function(rangeDays, onDone, onError) {
        var since = new Date(Date.now() - rangeDays * 24 * 60 * 60 * 1000);
        var url = this.config.urls.ruleCounts(this.rulesetId) + '?start_time=' + since.toISOString();

        data.get(url, function(payload) {
            // One total per rule across the daily buckets
            var totals = {};
            payload.fired.forEach(function(point) {
                if (totals[point.rule_id] === undefined) { totals[point.rule_id] = 0; }
                totals[point.rule_id] += point.firing_count;
            });

            onDone({totals: totals, neverFired: payload.never_fired});
        }, onError);
    },
};

window.logModel = logModel;

})();
