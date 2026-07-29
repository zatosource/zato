'use strict';

(function() {

var testView = {

    view: 'scenarios',
    selectedIndex: 0,
    editing: false,
    cursor: null,
    lastDelta: null,
    columnWidths: {},
    checkTimer: null,

// ////////////////////////////////////////////////////////////////////////

    statusLabels: {
        passed: 'passed',
        failed: 'failed',
        explored: 'explored, no expectations yet',
        notRun: 'not run yet',
    },

    statusDots: {
        passed: 'status-dot-pass',
        failed: 'status-dot-fail',
        explored: 'status-dot-no-expectations',
        notRun: 'status-dot-information',
    },

// ////////////////////////////////////////////////////////////////////////

    render: function() {
        if (testModel.suite === null) {
            document.getElementById('test-set-list').innerHTML = '<div class="test-empty-note">' +
                'There is no test set yet. <button class="button-ghost" onclick="testView.startNew()">New test set</button></div>';
            return;
        }

        this.renderSubtitle();
        this.renderSuite();
        this.renderDetail();
        this.renderProblems();
        this.renderVocabulary();
        this.attachVocabularyDrag();
        this.attachDropTargets();
        this.attachColumnResizers();
        this.applyCursor();
        shared.initTips();
        this.scheduleServerCheck();
    },

    renderSubtitle: function() {
        var text = shared.escape(testModel.suite.name);

        if (testModel.suiteId === null) {
            text += ' &#183; not saved yet';
        } else {
            text += ' &#183; version ' + testModel.suiteVersion;
        }
        if (testModel.rulesetId !== null) {
            text += ' &#183; runs against ' + shared.escape(testModel.rulesetName) +
                ' version ' + testModel.rulesetCurrentVersion;
        }

        document.getElementById('main-subtitle').innerHTML = text;
    },

// ////////////////////////////////////////////////////////////////////////

    scheduleServerCheck: function() {
        var self = this;

        if (this.checkTimer !== null) { clearTimeout(this.checkTimer); }
        this.checkTimer = setTimeout(function() {
            self.checkTimer = null;
            testModel.check(function() {
                self.renderProblems();
            }, data.reportError);
        }, testModel.config.checkDelayMilliseconds);
    },

// ////////////////////////////////////////////////////////////////////////

    attachColumnResizers: function() {
        var self = this;
        document.querySelectorAll('#test-detail-pane .test-grid thead th').forEach(function(cell, cellIndex) {
            shared.attachColumnResize(cell, 'outcome-' + cellIndex, self.columnWidths);
        });
    },

// ////////////////////////////////////////////////////////////////////////

    renderSuite: function() {
        var self = this;
        var head = document.getElementById('test-set-head');
        head.textContent = testModel.suite.scenarios.length + ' scenarios';

        var html = '';
        testModel.suite.scenarios.forEach(function(scenario, index) {
            var classes = 'test-set-item' + (index === self.selectedIndex ? ' test-set-item-selected' : '');
            var status = testModel.statusOf(scenario);

            var badge = '';
            if (self.lastDelta !== null) {
                if (self.lastDelta.newFailures.indexOf(scenario.name) > -1) {
                    badge = '<span class="test-delta-badge test-delta-broke">new failure</span>';
                }
                if (self.lastDelta.fixed.indexOf(scenario.name) > -1) {
                    badge = '<span class="test-delta-badge test-delta-fixed">fixed</span>';
                }
            }

            var play = '<span class="test-set-play" data-tippy-content="Run this scenario" ' +
                'onclick="testView.runFromList(event, ' + index + ', this)">' + shared.icon('play', 10) + '</span>';

            html += '<div class="' + classes + '" data-index="' + index + '" ' +
                'onclick="testView.selectScenario(' + index + ')">' +
                '<span class="status-dot ' + self.statusDots[status] + '" data-tippy-content="' + self.statusLabels[status] + '"></span>' +
                '<span class="test-set-name">' + shared.escape(scenario.name) + '</span>' + badge + play +
                '</div>';
        });

        document.getElementById('test-set-list').innerHTML = html;
    },

// ////////////////////////////////////////////////////////////////////////

    inputRowHtml: function(scenario, path, inputErrors) {
        var flat = testModel.flatten(scenario.input);

        var isInvalid = inputErrors.some(function(error) { return error.path === path; });
        var cellClasses = 'test-value-cell' + (isInvalid ? ' test-cell-invalid' : '');

        var removeControl = '<span class="test-row-remove" data-tippy-content="Remove this input" ' +
            'onclick="testView.removeInput(event, \'' + path + '\')">' + shared.icon('x', 11) + '</span>';

        var out = '<tr>' +
            '<td class="test-label-cell">' + shared.escape(testModel.phraseFor(path)) + removeControl + '</td>' +
            '<td class="' + cellClasses + '" data-cell="input" data-path="' + path + '" ' +
                'onclick="testView.editInput(this, \'' + path + '\')">' +
                shared.escape(testModel.displayValue(flat[path])) + '</td>' +
            '</tr>';
        return out;
    },

    outcomeRowHtml: function(scenario, path) {
        var result = testModel.resultOf(scenario);
        var expected = scenario.expected[path];
        var actual = result === null ? undefined : result.actual[path];

        var expectedHtml;
        if (expected === undefined) {
            expectedHtml = '<span class="test-no-value">none</span>';
        } else {
            expectedHtml = shared.escape(testModel.displayValue(expected));
        }

        var actualHtml;
        var actualClasses = 'test-value-cell test-actual-cell';
        if (result === null) {
            actualHtml = '<span class="test-no-value">not run</span>';
        } else if (actual === undefined) {
            actualHtml = '<span class="test-no-value">no decision</span>';
        } else {
            actualHtml = shared.escape(testModel.displayValue(actual));
            actualClasses += ' test-changed-by-rules';
        }
        if (expected !== undefined && result !== null && expected !== actual) {
            actualClasses += ' test-difference';
        }

        var out = '<tr>' +
            '<td class="test-label-cell">' + shared.escape(testModel.phraseFor(path)) + '</td>' +
            '<td class="test-value-cell" data-cell="expected" data-path="' + path + '" ' +
                'onclick="testView.editExpected(this, \'' + path + '\')">' + expectedHtml + '</td>' +
            '<td class="' + actualClasses + '">' + actualHtml + '</td>' +
            '</tr>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    firedRuleHtml: function(entry) {
        var out = '<div class="test-fired-item">' +
            '<span class="status-dot test-severity-' + entry.severity + '"></span>' +
            '<span class="test-fired-name">' + shared.escape(entry.rule) + '</span>' +
            '<span class="test-fired-statement">' + shared.escape(entry.statement) + '</span>' +
            '</div>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    renderDetail: function() {
        var self = this;
        var scenario = testModel.scenarioAt(this.selectedIndex);
        var pane = document.getElementById('test-detail-pane');

        if (scenario === undefined) {
            pane.innerHTML = '<div class="test-run-note">No scenario yet.</div>';
            return;
        }

        var result = testModel.resultOf(scenario);
        var status = testModel.statusOf(scenario);
        var inputErrors = testModel.validateInput(scenario);
        var html = '';

        html += '<div class="test-detail-head">' +
            '<span class="status-dot ' + this.statusDots[status] + '"></span>' +
            '<span class="test-detail-name" onclick="testView.editName(this)" ' +
                'data-tippy-content="Click to rename this scenario">' + shared.escape(scenario.name) + '</span>' +
            '<span class="test-detail-status">' + this.statusLabels[status] + '</span>' +
            '<button class="button-mini" onclick="testView.runOne(this)">' + shared.icon('play', 10) + ' Run</button>';

        if (result !== null && Object.keys(result.actual).length > 0) {
            html += '<button class="button-mini" onclick="testView.promote(this)" ' +
                'data-tippy-content="Promote the actual outcome to expected">' +
                'Promote actual to expected</button>';
        }
        html += '</div>';

        html += '<div class="test-grid-title">Input</div>';
        var inputRows = '';
        testModel.inputPaths(scenario).forEach(function(path) {
            inputRows += self.inputRowHtml(scenario, path, inputErrors);
        });
        if (inputRows === '') {
            inputRows = '<tr><td class="test-empty-hint" colspan="2">No input yet</td></tr>';
        }
        html += '<table class="test-grid" id="test-input-grid"><tbody>' + inputRows + '</tbody></table>';

        html += '<div class="test-grid-title">Outcome</div>';
        html += '<table class="test-grid"><thead><tr>' +
            '<th></th><th>Expected</th><th>Actual</th>' +
            '</tr></thead><tbody>';
        var outputPaths = testModel.outputPaths(scenario);
        outputPaths.forEach(function(path) {
            html += self.outcomeRowHtml(scenario, path);
        });
        if (outputPaths.length === 0) {
            html += '<tr><td class="test-empty-hint" colspan="3">No expectations yet</td></tr>';
        }
        html += '</tbody></table>';

        if (result !== null && result.error !== '') {
            html += '<div class="test-run-note">' + shared.escape(result.error) + '</div>';
        }

        if (result !== null) {
            html += '<div class="test-grid-title">Rules fired in this run (' + result.fired.length + ')</div>';
            if (result.fired.length === 0) {
                html += '<div class="test-run-note">Nothing fired - no rule matched this input.</div>';
            }
            result.fired.forEach(function(entry) {
                html += self.firedRuleHtml(entry);
            });
        }

        pane.innerHTML = html;
    },

// ////////////////////////////////////////////////////////////////////////

    renderProblems: function() {
        var head = document.getElementById('problems-head');
        var list = document.getElementById('problems-list');
        var items = [];

        testModel.serverErrors.forEach(function(error) {
            items.push('<div class="problem-item"><span class="status-dot status-dot-error"></span>' +
                '<span>' + shared.escape(error.message) + '</span></div>');
        });

        var scenario = testModel.scenarioAt(this.selectedIndex);
        if (scenario !== undefined) {

            testModel.validateInput(scenario).forEach(function(error) {
                items.push('<div class="problem-item"><span class="status-dot status-dot-error"></span>' +
                    '<span>' + shared.escape(error.text) + '</span></div>');
            });

            var result = testModel.resultOf(scenario);
            if (result !== null && result.status === 'failed') {
                if (result.error !== '') {
                    items.push('<div class="problem-item"><span class="status-dot status-dot-error"></span>' +
                        '<span>' + shared.escape(result.error) + '</span></div>');
                }
                result.diffs.forEach(function(diff) {
                    if (diff.status === 'matched') { return; }
                    var actualText = diff.actual === null ? 'no rule decided it' : testModel.displayValue(diff.actual);
                    items.push('<div class="problem-item"><span class="status-dot status-dot-error"></span>' +
                        '<span>' + shared.escape(testModel.phraseFor(diff.field)) + ': expected ' +
                        shared.escape(testModel.displayValue(diff.expected)) + ', got ' +
                        shared.escape(actualText) + '</span></div>');
                });
            }
        }

        if (this.lastDelta !== null) {
            var counts = this.lastDelta.counts;
            var deltaText = counts.passed + ' passed, ' + counts.failed + ' failed, ' +
                counts.explored + ' explored.';
            if (this.lastDelta.newFailures.length > 0) {
                deltaText += ' New failures: ' + this.lastDelta.newFailures.join(', ') + '.';
            }
            if (this.lastDelta.fixed.length > 0) {
                deltaText += ' Fixed: ' + this.lastDelta.fixed.join(', ') + '.';
            }
            items.push('<div class="problem-item"><span class="status-dot status-dot-information"></span>' +
                '<span>' + shared.escape(deltaText) + '</span></div>');
        }

        head.textContent = 'Problems (' + items.length + ')';
        if (items.length === 0) {
            list.innerHTML = '<div class="problem-item problem-none">No problems in this suite.</div>';
            return;
        }
        list.innerHTML = items.join('');
    },

// ////////////////////////////////////////////////////////////////////////

    renderVocabulary: function() {
        var scenario = testModel.scenarioAt(this.selectedIndex);
        var used = scenario === undefined ? [] : testModel.inputPaths(scenario);
        var html = '';

        vocabulary.entities.forEach(function(entity) {
            html += '<div class="vocabulary-entity">' + shared.escape(entity.name) + '</div>';
            vocabulary.pickerAttributes(entity).forEach(function(attribute) {
                var path = entity.name + '.' + attribute.name;

                var isUsed = used.indexOf(path) > -1;
                var classes = 'vocabulary-item' + (isUsed ? ' vocabulary-item-used' : ' vocabulary-item-clickable');
                var draggable = isUsed ? 'false' : 'true';
                var onClick = isUsed ? '' : ' onclick="testView.pickVocabulary(\'' + path + '\')"';

                html += '<div class="' + classes + '" draggable="' + draggable + '" data-path="' + path + '"' + onClick + '>' +
                    shared.escape(attribute.name) +
                    '<span class="vocabulary-item-type">' + shared.escape(attribute.type) + '</span></div>';
            });
        });

        document.getElementById('vocabulary-list').innerHTML = html;
    },
};

window.testView = testView;

})();
