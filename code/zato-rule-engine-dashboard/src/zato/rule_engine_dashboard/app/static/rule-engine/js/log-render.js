'use strict';

// Rendering for the decision log screen: the aggregate cards that drill
// down into the list, the searchable decision list with the caller
// column, and one decision opened into its readable story with the
// draft replay in place. Event handlers live in log-actions.js, the
// right-click menu in log-menu.js, both augment this namespace.

(function() {

var logView = {

    // UI state
    search: '',
    rangeDays: logModel.config.defaultRangeDays,
    outcome: null,          // the active card facet, null shows everything
    valueFilter: null,      // "everything for the value I clicked": {path, value}
    selectedId: null,
    columnWidths: {},
    folded: {},             // which detail sections are folded shut
    searchTimer: null,      // the debounce behind the search

    outcomeDots: {
        'matched': 'status-dot-pass',
        'no-match': 'status-dot-no-expectations',
        'error': 'status-dot-fail',
    },

// ////////////////////////////////////////////////////////////////////////

    render: function() {
        this.renderSubtitle();
        this.renderAggregates();
        this.renderList();
        this.renderDetail();
        this.renderProblems();
        this.attachColumnResizers();
        shared.initTips();
    },

    renderSubtitle: function() {
        var text = logModel.rulesetName === ''
            ? 'no ruleset stored yet'
            : logModel.rulesetName + ' \u00b7 every decision keeps its searchable header \u00b7 the id is the handle for support';
        document.getElementById('main-subtitle').textContent = text;
    },

    attachColumnResizers: function() {
        var self = this;
        document.querySelectorAll('#log-list .log-grid thead th').forEach(function(cell, cellIndex) {
            shared.attachColumnResize(cell, 'list-' + cellIndex, self.columnWidths);
        });
    },

// ////////////////////////////////////////////////////////////////////////

    // Timestamps come from the views as ISO strings, the list shows the
    // readable date-and-minute part
    whenText: function(iso) {
        return iso.slice(0, 16).replace('T', ' ');
    },

// ////////////////////////////////////////////////////////////////////////

    // The cards: every number on the screen is clickable and filters the
    // list to the individual decisions behind it
    renderAggregates: function() {
        if (logModel.aggregates === null) {
            document.getElementById('log-aggregates').innerHTML = '';
            return;
        }

        var counts = logModel.counts();
        var self = this;
        var html = '';

        var card = function(outcome, label, count) {
            var active = self.outcome === outcome ? ' log-card-active' : '';
            var tip = outcome === null ? 'Show every decision in the range'
                : 'Only the ' + label + ' decisions, click again to clear';
            html += '<div class="log-card' + active + '" data-tippy-content="' + tip + '" ' +
                'onclick="logView.toggleOutcome(' + (outcome === null ? 'null' : '\'' + outcome + '\'') + ')">' +
                '<span class="log-card-number">' + count + '</span>' +
                '<span class="log-card-label">' + label + '</span></div>';
        };

        card(null, 'decisions', counts.total);
        counts.outcomes.forEach(function(entry) { card(entry.outcome, entry.label, entry.count); });

        // The duration readout, not a filter - there is nothing to drill into
        var average = logModel.aggregates.average_duration_ms;
        if (average !== null) {
            html += '<div class="log-card log-card-readout" data-tippy-content="The average decision time over the range.">' +
                '<span class="log-card-number">' + Math.round(average) + ' ms</span>' +
                '<span class="log-card-label">average</span></div>';
        }

        document.getElementById('log-aggregates').innerHTML = html;
    },

// ////////////////////////////////////////////////////////////////////////

    renderList: function() {
        var records = logModel.filtered(this.search, this.valueFilter);
        var self = this;

        // Selection follows the filter, the detail never shows a hidden row
        var stillVisible = records.some(function(record) { return record.decision_id === self.selectedId; });
        if (!stillVisible) {
            this.selectedId = null;
            logModel.detail = null;
            if (records.length > 0) { this.select(records[0].decision_id); }
        }

        // The value filter is always visible as a chip, one click clears it
        var head = document.getElementById('log-list-head');
        var headHtml = records.length + ' decisions';
        if (this.valueFilter !== null) {
            var phrase = logModel.phraseFor(this.valueFilter.path);
            headHtml += '<span class="log-filter-chip" data-tippy-content="Click to clear this filter" ' +
                'onclick="logView.clearValueFilter()">' + shared.escape(phrase + ' = ' + this.valueFilter.value) +
                ' ' + shared.icon('x', 9) + '</span>';
        }
        head.innerHTML = headHtml;

        document.getElementById('log-list').innerHTML = this.listHtml(records);
    },

// ////////////////////////////////////////////////////////////////////////

    // The decision list as html, out of the records alone - no DOM is read
    // here, which is what lets the scale check measure a full page of them
    listHtml: function(records) {
        var self = this;

        var html = '<table class="log-grid"><thead><tr>' +
            '<th>Decision</th><th>Key</th><th>Caller</th><th>When</th><th>Outcome</th>' +
            '</tr></thead><tbody>';

        records.forEach(function(record) {
            var id = record.decision_id;
            var classes = 'log-row' + (id === self.selectedId ? ' log-row-selected' : '');

            // The quiet copy of the id, visible when the row is hovered
            var copy = '<span class="log-row-copy" data-tippy-content="Copy the decision id" ' +
                'onclick="logView.copyText(event, \'' + id + '\')">' + shared.icon('copy', 10) + '</span>';

            var key = record.business_key === null ? '' : shared.escape(record.business_key);
            var caller = record.caller === null ? '' : shared.escape(record.caller);

            html += '<tr class="' + classes + '" data-decision="' + id + '" ' +
                'onclick="logView.select(\'' + id + '\')">' +
                '<td class="log-id">' + shared.escape(self.shortId(id)) + copy + '</td>' +
                '<td class="log-customer">' + key + '</td>' +
                '<td class="log-customer">' + caller + '</td>' +
                '<td class="log-when">' + self.whenText(record.occurred_at) + '</td>' +
                '<td class="log-outcome"><span class="status-dot ' + self.outcomeDots[record.outcome] + '"></span>' +
                logModel.config.outcomeLabels[record.outcome] + '</td>' +
                '</tr>';
        });

        html += '</tbody></table>';
        if (records.length === 0) {
            html = '<div class="log-empty">Nothing matches. Widen the date range or clear the search.</div>';
        }

        return html;
    },

    // Decision ids are long opaque handles, the list shows the readable
    // prefix and the copy control carries the whole thing
    shortId: function(decisionId) {
        return decisionId.slice(0, 12);
    },

// ////////////////////////////////////////////////////////////////////////

    // One decision opened into its story: who asked, what came in, what
    // went out, why, and the rules exactly as the deciding version knew them
    renderDetail: function() {
        var pane = document.getElementById('log-detail-pane');
        if (logModel.detail === null) { pane.innerHTML = ''; return; }

        var decision = logModel.detail.decision;
        var html = '';

        var keyText = decision.business_key === null ? this.shortId(decision.decision_id) : decision.business_key;
        var callerText = decision.caller === null ? '' : ' \u00b7 ' + shared.escape(decision.caller);

        html += '<div class="log-detail-head">' +
            '<span class="status-dot ' + this.outcomeDots[decision.outcome] + '"></span>' +
            '<span class="log-detail-name">' + shared.escape(keyText) + '</span>' +
            '<span class="log-detail-meta">' + shared.escape(this.shortId(decision.decision_id)) + ' \u00b7 ' +
                this.whenText(decision.occurred_at) + callerText + ' \u00b7 ' + decision.duration_ms + ' ms</span>' +
            '<span class="log-copy-quiet" data-tippy-content="Copy the decision id" ' +
                'onclick="logView.copyText(event, \'' + decision.decision_id + '\')">' + shared.icon('copy', 11) + '</span>';

        // Only a decision that kept its story can be copied or replayed
        if (decision.has_payload) {
            html += '<button class="button-mini" onclick="logView.addToTestSet(this)" ' +
                'data-tippy-content="One click turns this stored decision into a scenario in the test set, ' +
                'outputs as the expectations.">Add to test set</button>' +
                '<button class="button-mini" onclick="logView.replay(this)" ' +
                'data-tippy-content="Runs this same input against v' + logModel.currentVersion +
                ', the newest stored version, and shows what would come out differently now.">Replay against v' +
                logModel.currentVersion + '</button>';
        }

        html += '</div>';

        // The version link survives later edits, it points at the snapshot
        html += '<div class="log-version-line">Decided by ' + shared.escape(logModel.rulesetName) +
            ' version ' + decision.rules_version +
            '. <a class="log-version-link" href="/versions/?ruleset=' + decision.ruleset_id + '" ' +
            'data-tippy-content="Opens the rules exactly as version ' + decision.rules_version +
            ' knew them. The link points at the version snapshot, so later edits never change what you see here.">' +
            'Open the rules as they were</a></div>';

        // A sampled-away story shows its headers and says so, never a blank
        if (!decision.has_payload) {
            html += '<div class="test-run-note">This decision kept headers only - the capture dial sampled its ' +
                'full story away. The outcome, the timing and the caller above are everything that was stored.</div>';
            pane.innerHTML = html;
            return;
        }

        html += this.inputSectionHtml(decision);

        if (decision.is_error) {
            html += this.errorSectionHtml(decision);
        } else {
            html += this.outcomeSectionHtml(decision);
            if (logModel.replayResult !== null) { html += this.replaySectionHtml(decision); }
            html += this.firedSectionHtml(decision);
        }

        html += this.rulesSectionHtml();

        pane.innerHTML = html;
    },

// ////////////////////////////////////////////////////////////////////////

    // Every section folds shut, long inputs never push the rules off
    // the screen
    foldTitleHtml: function(key, label) {
        var isFolded = this.folded[key] === true;
        var chevron = shared.icon(isFolded ? 'chevron-right' : 'chevron-down', 11);
        var out = '<div class="test-grid-title log-fold-title" onclick="logView.toggleFold(\'' + key + '\')">' +
            chevron + ' ' + label + '</div>';
        return out;
    },

    // The quiet per-value copy, visible when the cell is hovered
    cellCopyHtml: function(value) {
        var out = '<span class="log-cell-copy" data-tippy-content="Copy this value" ' +
            'onclick="logView.copyText(event, \'' + shared.escape(value) + '\')">' + shared.icon('copy', 10) + '</span>';
        return out;
    },

    inputSectionHtml: function(decision) {
        var self = this;
        var html = this.foldTitleHtml('input', 'What came in');
        if (this.folded['input'] === true) { return html; }
        html += '<table class="test-grid"><tbody>';

        var flat = logModel.flatten(decision.story.input);
        Object.keys(flat).forEach(function(path) {
            var value = logModel.displayValue(flat[path]);
            html += '<tr><td class="test-label-cell">' + shared.escape(logModel.phraseFor(path)) + '</td>' +
                '<td class="test-value-cell log-value-readonly" ' +
                'oncontextmenu="logView.openValueMenu(event, \'' + shared.escape(path) + '\', \'' +
                shared.escape(value) + '\')">' + shared.escape(value) + self.cellCopyHtml(value) + '</td></tr>';
        });

        html += '</tbody></table>';
        return html;
    },

    outcomeSectionHtml: function(decision) {
        var self = this;
        var html = this.foldTitleHtml('output', 'What went out');
        if (this.folded['output'] === true) { return html; }

        var outputs = decision.story.outputs;
        var paths = Object.keys(outputs);

        if (paths.length === 0) {
            html += '<div class="test-run-note">No rule matched, so nothing was assigned - the caller received ' +
                'an empty outcome, not an error.</div>';
            return html;
        }

        html += '<table class="test-grid"><tbody>';
        paths.forEach(function(path) {
            var value = logModel.displayValue(outputs[path]);
            html += '<tr><td class="test-label-cell">' + shared.escape(logModel.phraseFor(path)) + '</td>' +
                '<td class="test-value-cell log-value-readonly test-changed-by-rules" ' +
                'oncontextmenu="logView.openValueMenu(event, \'' + shared.escape(path) + '\', \'' +
                shared.escape(value) + '\')">' + shared.escape(value) + self.cellCopyHtml(value) + '</td></tr>';
        });
        html += '</tbody></table>';
        return html;
    },

    // The readable failure: the exact message the caller received,
    // in domain terms, never a bare status code
    errorSectionHtml: function(decision) {
        var html = '<div class="test-grid-title">What the caller was told</div>';
        html += '<div class="test-fired-item"><span class="status-dot test-severity-violation"></span>' +
            '<span class="test-fired-statement">' + shared.escape(decision.story.error) + '</span></div>';
        html += '<div class="test-run-note">Nothing was assigned: the message above went back to the caller ' +
            'as the response, not a bare status code.</div>';
        return html;
    },

    firedSectionHtml: function(decision) {
        var statements = decision.story.statements;
        var html = this.foldTitleHtml('why', 'Why, rule by rule (' + statements.length + ')');
        if (this.folded['why'] === true) { return html; }

        if (statements.length === 0) {
            html += '<div class="test-run-note">No rule matched this input.</div>';
            return html;
        }

        statements.forEach(function(entry) {
            html += '<div class="test-fired-item">' +
                '<span class="status-dot test-severity-' + entry.severity + '"></span>' +
                '<span class="test-fired-name">' + shared.escape(entry.rule) + '</span>' +
                '<span class="test-fired-statement">' + shared.escape(entry.statement) + '</span>' +
                '</div>';
        });
        return html;
    },

    // The rules exactly as the deciding version knew them - the rendered
    // snapshot, never the rules as they read today
    rulesSectionHtml: function() {
        var decision = logModel.detail.decision;
        var rendered = logModel.detail.version.rendered;
        if (rendered === null) { return ''; }

        var html = this.foldTitleHtml('rules', 'The rules as version ' + decision.rules_version + ' knew them');
        if (this.folded['rules'] === true) { return html; }

        html += '<div class="log-rules-snapshot">' +
            rendered.split('\n').map(function(line) { return shared.escape(line); }).join('<br>') + '</div>';
        return html;
    },

// ////////////////////////////////////////////////////////////////////////

    // The stored decision replayed against the newest version: would it
    // come out differently today, value by value
    replaySectionHtml: function(decision) {
        var replayed = logModel.replayResult;
        var html = '<div class="test-grid-title">Replayed against v' + logModel.currentVersion + '</div>';

        // A replay that errors is its own readable answer
        if (replayed.error !== '') {
            html += '<div class="test-fired-item"><span class="status-dot test-severity-violation"></span>' +
                '<span class="test-fired-statement">' + shared.escape(replayed.error) + '</span></div>';
            return html;
        }

        var before = decision.story.outputs;
        var after = replayed.actual;

        var paths = Object.keys(before);
        Object.keys(after).forEach(function(path) {
            if (paths.indexOf(path) === -1) { paths.push(path); }
        });
        paths.sort();

        var anythingChanged = false;
        html += '<table class="test-grid"><thead><tr><th></th><th>Version ' + decision.rules_version +
            ' decided</th><th>v' + logModel.currentVersion + ' would decide</th></tr></thead><tbody>';

        paths.forEach(function(path) {
            var beforeHas = path in before;
            var afterHas = path in after;
            var differs = !beforeHas || !afterHas || before[path] !== after[path];
            if (differs) { anythingChanged = true; }

            var beforeHtml = beforeHas ? shared.escape(logModel.displayValue(before[path]))
                : '<span class="test-no-value">no decision</span>';
            var afterHtml = afterHas ? shared.escape(logModel.displayValue(after[path]))
                : '<span class="test-no-value">no decision</span>';
            var afterClasses = 'test-value-cell log-value-readonly' + (differs ? ' log-replay-differs' : '');

            html += '<tr><td class="test-label-cell">' + shared.escape(logModel.phraseFor(path)) + '</td>' +
                '<td class="test-value-cell log-value-readonly">' + beforeHtml + '</td>' +
                '<td class="' + afterClasses + '">' + afterHtml + '</td></tr>';
        });

        html += '</tbody></table>';
        if (!anythingChanged) {
            html += '<div class="test-run-note">v' + logModel.currentVersion + ' decides this one exactly the same.</div>';
        }
        return html;
    },

// ////////////////////////////////////////////////////////////////////////

    renderProblems: function() {
        var head = document.getElementById('problems-head');
        var list = document.getElementById('problems-list');
        var items = [];
        var problemCount = 0;

        if (logModel.aggregates !== null) {
            var errors = 0;
            logModel.aggregates.outcomes.forEach(function(point) {
                if (point.key === 'error') { errors = point.count; }
            });

            if (errors > 0) {
                problemCount += 1;
                items.push('<div class="problem-item"><span class="status-dot status-dot-error"></span>' +
                    '<span>' + errors + ' decision(s) in the range ended in an input error. ' +
                    'Click the errors card to see every one of them.</span></div>');
            }
        }

        // The capture readout is a fact of the log, never a problem
        if (logModel.items.length > 0) {
            var readout = logModel.captureReadout();
            items.push('<div class="problem-item"><span class="status-dot status-dot-information"></span>' +
                '<span>Capture: the searchable header of every decision is always kept, the full story is kept ' +
                'for every error and for ' + readout.successKept + ' of the ' + readout.successTotal +
                ' successes on this page - the dial\'s sample. Set deliberately, never a hidden default.</span></div>');
        }

        head.textContent = 'Problems (' + problemCount + ')';
        list.innerHTML = items.join('');
    },
};

window.logView = logView;

})();
