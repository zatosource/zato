'use strict';

(function() {

testView.abResult = null;

testView.championVersion = null;
testView.challengerVersion = null;

// ////////////////////////////////////////////////////////////////////////

testView.abKpis = function() {
    var fields = [];
    testModel.suite.scenarios.forEach(function(scenario) {
        Object.keys(scenario.expected).forEach(function(path) {
            if (fields.indexOf(path) === -1) { fields.push(path); }
        });
    });

    var out = fields.map(function(field) {
        return {name: field, kind: 'breakdown', field: field};
    });
    return out;
};

testView.abScenarios = function() {
    var out = testModel.suite.scenarios.map(function(scenario) {
        return {name: scenario.name, input: scenario.input};
    });
    return out;
};

// ////////////////////////////////////////////////////////////////////////

testView.compare = function(button) {
    var self = this;

    if (testModel.documents === null) {
        shared.popover(button, testModel.config.noRulesetMessage);
        return;
    }
    if (testModel.suite.scenarios.length === 0) {
        shared.popover(button, 'The suite has no scenarios yet - the comparison needs inputs to run.');
        return;
    }

    this.championVersion = parseInt(document.getElementById('ab-champion-version').value);
    this.challengerVersion = parseInt(document.getElementById('ab-challenger-version').value);

    var handlers = shared.inFlight(button, function(payload) {
        self.abResult = payload;
        self.renderAb();
        shared.initTips();
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    if (this.championVersion === this.challengerVersion) {
        var single = {
            ruleset_id: testModel.rulesetId,
            version: this.championVersion,
            scenarios: this.abScenarios(),
            kpis: this.abKpis(),
        };
        data.post(testModel.config.urls.simulation, single, function(payload) {
            handlers.done({champion: payload, challenger: null, diff: null});
        }, handlers.error);
        return;
    }

    var body = {
        ruleset_id: testModel.rulesetId,
        champion_version: this.championVersion,
        challenger_version: this.challengerVersion,
        scenarios: this.abScenarios(),
        kpis: this.abKpis(),
    };
    data.post(testModel.config.urls.championChallenger, body, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

testView.resultLineHtml = function(label, valueText, share) {
    var width = Math.round(share * 100);
    var out = '<div class="test-result-line">' +
        '<span class="test-result-line-label">' + shared.escape(label) + '</span>' +
        '<span class="test-result-line-value">' + shared.escape(valueText) + '</span>' +
        '<span class="test-result-line-bar"><span class="test-result-line-fill" style="width:' + width + '%"></span></span>' +
        '</div>';
    return out;
};

testView.variantCardHtml = function(title, version, run) {
    var self = this;
    var html = '<div class="test-variant-card">';
    html += '<div class="test-variant-title">' + title +
        '<span class="test-variant-subtitle">version ' + version + '</span></div>';

    html += this.resultLineHtml('Evaluated', run.evaluated + ' of ' + run.total,
        run.total === 0 ? 0 : run.evaluated / run.total);
    if (run.errors > 0) {
        html += this.resultLineHtml('Could not run', String(run.errors), run.errors / run.total);
    }

    run.kpis.forEach(function(kpi) {
        var buckets = kpi.value;
        Object.keys(buckets).sort().forEach(function(bucket) {
            var count = buckets[bucket];
            html += self.resultLineHtml(testModel.phraseFor(kpi.name) + ': ' + bucket, String(count),
                run.evaluated === 0 ? 0 : count / run.evaluated);
        });
    });

    html += '</div>';
    return html;
};

// ////////////////////////////////////////////////////////////////////////

testView.changeText = function(change) {
    var before = change.old === null ? 'no decision' : testModel.displayValue(change.old);
    var after = change.new === null ? 'no decision' : testModel.displayValue(change.new);
    var out = testModel.phraseFor(change.field) + ': ' + before + ' becomes ' + after;
    return out;
};

testView.changedRowHtml = function(entry) {
    var self = this;
    var changeParts = entry.changes.map(function(change) { return self.changeText(change); });

    var ruleParts = [];
    entry.fired_only_old.forEach(function(name) { ruleParts.push(name + ' (champion only)'); });
    entry.fired_only_new.forEach(function(name) { ruleParts.push(name + ' (challenger only)'); });

    var out = '<tr>' +
        '<td class="test-changed-id">' + shared.escape(entry.scenario) + '</td>' +
        '<td class="test-changed-diff">' + shared.escape(changeParts.join(', ')) + '</td>' +
        '<td class="test-changed-rule">' + shared.escape(ruleParts.join(', ')) + '</td>' +
        '</tr>';
    return out;
};

// ////////////////////////////////////////////////////////////////////////

testView.versionOptionsHtml = function(selected) {
    var html = '';
    for (var version = 1; version <= testModel.rulesetCurrentVersion; version += 1) {
        var suffix = '';
        if (version === testModel.rulesetLiveVersion) { suffix = ' (live)'; }
        if (version === testModel.rulesetCurrentVersion) { suffix += ' (latest)'; }
        html += '<option value="' + version + '"' + (version === selected ? ' selected' : '') + '>' +
            'version ' + version + suffix + '</option>';
    }
    return html;
};

testView.renderAb = function() {
    var area = document.getElementById('test-ab-view');

    if (testModel.rulesetId === null) {
        area.innerHTML = '<div class="test-run-note">' + shared.escape(testModel.config.noRulesetMessage) + '</div>';
        return;
    }

    if (this.championVersion === null) {
        this.championVersion = testModel.rulesetLiveVersion;
        if (this.championVersion === null) { this.championVersion = testModel.rulesetCurrentVersion; }
        this.challengerVersion = testModel.rulesetCurrentVersion;
    }

    var html = '';
    html += '<div class="test-ab-intro">Both versions of ' + shared.escape(testModel.rulesetName) +
        ' run against the suite\'s own scenarios, results and KPI numbers side by side, and every decision ' +
        'that changes under the challenger is listed with the rules that explain it.</div>';

    html += '<div class="test-ab-pickers">' +
        '<label>Champion <select id="ab-champion-version">' + this.versionOptionsHtml(this.championVersion) + '</select></label>' +
        '<label>Challenger <select id="ab-challenger-version">' + this.versionOptionsHtml(this.challengerVersion) + '</select></label>' +
        '<button class="button-ghost" onclick="testView.compare(this)">Compare</button>' +
        '</div>';

    if (this.abResult !== null) {

        html += '<div class="test-variant-row">';
        html += this.variantCardHtml('Champion', this.championVersion, this.abResult.champion);
        if (this.abResult.challenger !== null) {
            html += this.variantCardHtml('Challenger', this.challengerVersion, this.abResult.challenger);
        }
        html += '</div>';

        if (this.abResult.diff !== null) {
            var diff = this.abResult.diff;
            var self = this;

            html += '<div class="test-grid-title">Decisions that change under the challenger (' +
                diff.changed + ' of ' + diff.total + ')</div>';

            html += '<table class="test-grid test-changed-grid"><thead><tr>' +
                '<th>Scenario</th><th>What changes</th><th>Explained by</th>' +
                '</tr></thead><tbody>';
            diff.scenarios.forEach(function(entry) {
                if (entry.status !== 'changed') { return; }
                html += self.changedRowHtml(entry);
            });
            html += '</tbody></table>';

            if (diff.changed === 0) {
                html += '<div class="test-run-note">No decision changes - both versions decide every scenario the same way.</div>';
            }
        }
    }

    area.innerHTML = html;
};

})();
