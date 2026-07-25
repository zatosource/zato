'use strict';

// Running test scenarios against the rules: the full run, the single
// scenario run and promoting an explored outcome into an assertion.
// Augments the testModel namespace from test-model.js. No DOM access
// in this file.

(function() {

// ////////////////////////////////////////////////////////////////////////

// Folds one full run's answer into the results and reports the delta
// against the previous run - the one-glance regression signal
testModel.ingestRun = function(payload) {
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
};

// A full run: the stored suite runs through the endpoint that records
// the run in the ruleset's history, a locally edited one through the
// outcomes feed - the results read the same either way
testModel.runAll = function(onDone, onError) {
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
};

// One scenario runs alone through the outcomes feed, the rest of the
// suite keeps its previous results
testModel.runOne = function(scenario, onDone, onError) {
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
};

// ////////////////////////////////////////////////////////////////////////

// Promoting a whole outcome turns exploration into assertion. An
// unmodified stored suite promotes through the endpoint, which stores
// a new version right away - a locally edited one promotes in place
// and the Save button persists everything together.
testModel.promote = function(scenario, onDone, onError) {
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
};

// ////////////////////////////////////////////////////////////////////////

})();
