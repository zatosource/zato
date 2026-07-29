'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

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
