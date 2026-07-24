'use strict';

// Live test data in the editing loop: every edit re-runs the whole ruleset,
// with the rule being written swapped in, against the stored test set, and
// a panel under the sentence shows the per-scenario outcomes live. This is
// the mechanism that catches the rule that is syntactically perfect but
// passes for nothing, or breaks a scenario that used to pass.

(function() {

var editorLive = {

    config: {
        maximumErrorLines: 3,
    },

// ////////////////////////////////////////////////////////////////////////

    barSegmentHtml: function(kind, count, total) {
        if (count === 0) { return ''; }
        var out = '<span class="live-bar-segment live-bar-' + kind + '" style="width:' +
            (count * 100 / total) + '%"></span>';
        return out;
    },

    scenarioChipHtml: function(scenario) {
        var title = '';
        if (scenario.error !== '') {
            title = ' data-tippy-content="' + shared.escape(scenario.error) + '"';
        }

        var out = '<span class="live-scenario live-scenario-' + scenario.status + '"' + title + '>' +
            shared.escape(scenario.scenario) +
            '<span class="live-scenario-badge">' + scenario.status + '</span></span>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    headHtml: function(hint) {
        var out = '<div class="live-head">Live outcomes' +
            '<span class="live-head-hint">' + hint + '</span></div>';
        return out;
    },

    resultHtml: function(result) {
        var parts = [];
        var total = result.total;

        parts.push(this.headHtml(shared.escape(result.name) + ' re-run on every edit, ' +
            total + ' scenario' + (total === 1 ? '' : 's')));

        // The distribution bar: passed, failed and explored shares of the run
        parts.push('<div class="live-bar">' +
            this.barSegmentHtml('passed', result.passed, total) +
            this.barSegmentHtml('failed', result.failed, total) +
            this.barSegmentHtml('explored', result.explored, total) + '</div>');

        // The counts in words
        var countParts = [];
        countParts.push('<span class="live-count live-count-passed">' + result.passed + ' passed</span>');
        countParts.push('<span class="live-count live-count-explored">' + result.explored + ' explored</span>');
        if (result.failed > 0) {
            countParts.push('<span class="live-count live-count-failed">' + result.failed + ' failed</span>');
        }
        parts.push('<div class="live-counts">' + countParts.join('<span class="live-count-separator">&#183;</span>') + '</div>');

        // Errors are loud and readable, never a null that flows onward
        var errorLines = 0;
        result.scenarios.forEach(function(scenario) {
            if (scenario.error === '' || errorLines >= editorLive.config.maximumErrorLines) { return; }
            errorLines += 1;
            parts.push('<div class="live-error">' + shared.escape(scenario.scenario) + ': ' +
                shared.escape(scenario.error) + '</div>');
        });

        // Every scenario as a chip with the status it came back with
        parts.push('<div class="live-scenarios">' + result.scenarios.map(function(scenario) {
            var out = editorLive.scenarioChipHtml(scenario);
            return out;
        }).join('') + '</div>');

        var out = parts.join('');
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // Re-render the live panel, called after every server check
    update: function() {
        var self = this;
        var panel = document.getElementById('live-panel');

        if (editorModel.testSet === null) {
            panel.innerHTML = this.headHtml('there is no test set yet, ' +
                '<a href="/tests/">the tests screen</a> is where one starts');
            return;
        }

        var documents = editorModel.mergedDocuments();
        if (documents === null) {
            panel.innerHTML = this.headHtml('the outcomes appear once the rule has ' +
                'a finished condition and a then action');
            return;
        }

        var body = {documents: documents, test_set: editorModel.testSet};
        data.post(editorModel.config.urls.outcomes, body, function(result) {
            panel.innerHTML = self.resultHtml(result);
            shared.initTips();
        }, data.reportError);
    },
};

window.editorLive = editorLive;

})();
