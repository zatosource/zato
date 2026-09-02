'use strict';

// The scale smoke: the editor must stay fluid at sizes where rule editors
// are commonly reported to degrade.
//
// - Completion menus elsewhere become slow on a large vocabulary: our
//   completion list must build instantly over 5000 terms.
// - Table editors elsewhere are reported to delay every keystroke around
//   80 rows by 30 columns: our grid rendering must stay fast well past
//   that, at 120 columns by 40 rows - both in the sentence editor's own
//   table view and in the decision table grid, which is the screen an
//   author of a table that size actually types into.
// - The decision log filters a full page of decisions on every keystroke,
//   and the versions diff walks a whole ruleset word by word, so both
//   carry a budget of their own.
//
// The live-outcomes loop runs server-side in this product, so its budget
// lives with the Python suite against the outcomes endpoint.
//
// Run with: node check_scale.js <webapp js dir> <dashboard js dir> <shared rule-engine js dir>

const fs = require('fs');
const path = require('path');
const vm = require('vm');

// The budgets, in milliseconds. These are smoke-tested numbers, not
// adjectives: a breach fails the build.
const budgets = {
    completionBuildMs: 50,
    completionFilterMs: 50,
    gridBuildMs: 250,
    tableGridBuildMs: 250,
    logListBuildMs: 50,
    logFilterMs: 50,
    versionsDiffMs: 500,
};

const scale = {
    vocabularyEntities: 50,
    attributesPerEntity: 100,
    gridColumns: 120,
    gridRows: 40,

    // A full page of the decision log, the size logModel.config.pageSize asks
    // the server for, and the number of rules one diffed ruleset holds
    logDecisions: 200,
    diffRules: 40,
};

// ////////////////////////////////////////////////////////////////////////

// The browser scripts assign onto window and call bare globals, so window
// is the node global itself and document is the minimal stub the scripts
// touch at load time.
global.window = global;
global.document = {addEventListener: function() {}};
global.localStorage = {getItem: function() { return null; }, setItem: function() {}};
window.localStorage = global.localStorage;
window.location = {hash: '', search: ''};

const webappJsDir = process.argv[2];
const dashboardJsDir = process.argv[3];

// The editor core ships with the shared UI kit in zato-common while the
// dashboard keeps its own screens, so the scripts load from both places
const sharedRuleEngineJsDir = process.argv[4];

[path.join(webappJsDir, 'shared.js'),
 path.join(sharedRuleEngineJsDir, 'vocabulary.js'),
 path.join(sharedRuleEngineJsDir, 'editor-model.js'),
 path.join(sharedRuleEngineJsDir, 'editor-checks.js'),
 path.join(sharedRuleEngineJsDir, 'editor-render.js'),
 path.join(sharedRuleEngineJsDir, 'editor-views.js'),
 path.join(dashboardJsDir, 'table-model.js'),
 path.join(dashboardJsDir, 'table-checks.js'),
 path.join(dashboardJsDir, 'table-render.js'),
 path.join(dashboardJsDir, 'table-grid.js'),
 path.join(dashboardJsDir, 'log-model.js'),
 path.join(dashboardJsDir, 'log-render.js'),
 path.join(dashboardJsDir, 'versions-model.js'),
].forEach(filePath => {
    const source = fs.readFileSync(filePath, 'utf8');
    vm.runInThisContext(source, {filename: path.basename(filePath)});
});

// ////////////////////////////////////////////////////////////////////////

let failures = 0;

function check(name, milliseconds, budget) {
    const status = milliseconds <= budget ? 'ok' : 'FAIL';
    if (milliseconds > budget) { failures += 1; }
    console.log(`${status.padEnd(4)} ${name}: ${milliseconds.toFixed(1)} ms (budget ${budget} ms)`);
}

function measure(action) {
    const start = process.hrtime.bigint();
    action();
    const out = Number(process.hrtime.bigint() - start) / 1e6;
    return out;
}

// ////////////////////////////////////////////////////////////////////////

// A vocabulary large enough to break lesser completion menus: 50 entities
// with 100 number attributes each, 5000 terms in total
const bigEntities = [];
for (let entityIndex = 0; entityIndex < scale.vocabularyEntities; entityIndex += 1) {
    const attributes = [];
    for (let attributeIndex = 0; attributeIndex < scale.attributesPerEntity; attributeIndex += 1) {
        attributes.push({
            name: 'attribute' + attributeIndex,
            type: 'number range',
            domain: {low: 0, high: 1000000},
            phrase: 'the entity' + entityIndex + ' attribute ' + attributeIndex,
            setPhrase: 'set the entity' + entityIndex + ' attribute ' + attributeIndex + ' to',
            status: '',
        });
    }
    bigEntities.push({name: 'entity' + entityIndex, attributes: attributes});
}
vocabulary.entities = bigEntities;

// ////////////////////////////////////////////////////////////////////////

// 1. The completion list over 5000 terms, the loop the subject menu runs
let completionItems = null;
const completionMs = measure(() => {
    completionItems = [];
    vocabulary.entities.forEach(entity => {
        vocabulary.pickerAttributes(entity).forEach(attribute => {
            const itemPath = entity.name + '.' + attribute.name;
            completionItems.push({label: attribute.phrase, hint: itemPath});
        });
    });
});
check(`completion list over ${completionItems.length} terms`, completionMs, budgets.completionBuildMs);

// 2. Type-to-filter over the full list, one keystroke's worth of work
let filtered = null;
const filterMs = measure(() => {
    filtered = completionItems.filter(item => item.label.indexOf('attribute 7') > -1);
});
check(`type-to-filter down to ${filtered.length} matches`, filterMs, budgets.completionFilterMs);

// ////////////////////////////////////////////////////////////////////////

// 3. The grid at 120 columns by 40 rows, well past the sizes where table
// editors are reported to collapse: or-joined groups become columns,
// and-joined conditions the rows
const conditions = [];
const joiners = [];
for (let columnIndex = 0; columnIndex < scale.gridColumns; columnIndex += 1) {
    for (let rowIndex = 0; rowIndex < scale.gridRows; rowIndex += 1) {
        conditions.push({
            subject: 'entity0.attribute' + rowIndex,
            comparator: 'is at least',
            values: [String(columnIndex * rowIndex)],
        });
        if (conditions.length > 1) {
            joiners.push(rowIndex === 0 ? 'or' : 'and');
        }
    }
}
editorModel.rule = {
    conditions: conditions,
    joiners: joiners,
    thenActions: [{target: 'entity0.attribute0', values: ['1']}],
    elseActions: [{target: 'entity0.attribute1', values: ['2']}],
};

let gridHtml = null;
const gridMs = measure(() => {
    gridHtml = editorView.tableViewHtml();
});
check(`grid html at ${scale.gridColumns} columns by ${scale.gridRows} rows (${conditions.length} cells)`,
    gridMs, budgets.gridBuildMs);

if (gridHtml.indexOf('<table') === -1) {
    console.log('FAIL the grid html has no table in it');
    failures += 1;
}

// ////////////////////////////////////////////////////////////////////////

// 4. The decision table grid at the same size, the screen an author of a
// table that large actually types into: one rule column per grid column,
// its condition rows shared by all of them
const tableColumns = [{number: 0, cells: {}, actions: {}, statement: {text: '', severity: 'info'}, overrides: []}];
const tableConditions = [];
const tableActions = [{target: 'entity0.attribute0'}];

for (let rowIndex = 0; rowIndex < scale.gridRows; rowIndex += 1) {
    tableConditions.push({letter: 'row' + rowIndex, subject: 'entity0.attribute' + rowIndex});
}

for (let columnIndex = 1; columnIndex <= scale.gridColumns; columnIndex += 1) {
    const cells = {};
    tableConditions.forEach((row, rowIndex) => { cells[row.letter] = String(columnIndex * rowIndex) + '..1000000'; });

    tableColumns.push({
        number: columnIndex,
        cells: cells,
        actions: {'entity0.attribute0': String(columnIndex)},
        statement: {text: 'Rule ' + columnIndex + ' fired for {entity0.attribute0}', severity: 'info'},
        overrides: [],
    });
}

tableModel.table = {
    name: 'Scale',
    docs: '',
    conditions: tableConditions,
    actions: tableActions,
    columns: tableColumns,
};

// What the toolbar and the last validation would say on a table being typed
// into: nothing is invalid, nothing conflicts and the find box is empty
const tableContext = {invalid: {}, conflictLabels: [], findTerm: ''};

let tableGridHtml = null;
const tableGridMs = measure(() => {
    tableGridHtml = tableView.gridHtml(tableContext);
});
check(`decision table grid at ${scale.gridColumns} columns by ${scale.gridRows} rows`,
    tableGridMs, budgets.tableGridBuildMs);

if (tableGridHtml.indexOf('<table') === -1) {
    console.log('FAIL the decision table grid html has no table in it');
    failures += 1;
}

// ////////////////////////////////////////////////////////////////////////

// 5. The decision log: one full page of decisions, filtered and rendered -
// this is the work every keystroke in the search box triggers
const decisions = [];
for (let decisionIndex = 0; decisionIndex < scale.logDecisions; decisionIndex += 1) {
    decisions.push({
        decision_id: 'decision-' + decisionIndex + '-0123456789abcdef',
        business_key: 'customer-' + decisionIndex,
        caller: 'service.loans',
        occurred_at: '2026-07-25T11:22:33.000000+00:00',
        outcome: decisionIndex % 3 === 0 ? 'matched' : (decisionIndex % 3 === 1 ? 'no-match' : 'error'),
        story: null,
    });
}
logModel.items = decisions;

let matching = null;
const logFilterMs = measure(() => {
    matching = logModel.filtered('customer-1', null);
});
check(`log search over ${decisions.length} decisions down to ${matching.length}`, logFilterMs, budgets.logFilterMs);

let logHtml = null;
const logListMs = measure(() => {
    logHtml = logView.listHtml(decisions);
});
check(`log list of ${decisions.length} decisions`, logListMs, budgets.logListBuildMs);

if (logHtml.indexOf('<table') === -1) {
    console.log('FAIL the log list html has no table in it');
    failures += 1;
}

// ////////////////////////////////////////////////////////////////////////

// 6. The versions diff, word by word over a whole ruleset: its cost is the
// product of both sides, so the budget is what keeps that visible
const oldLines = [];
const newLines = [];
for (let ruleIndex = 0; ruleIndex < scale.diffRules; ruleIndex += 1) {
    oldLines.push('If entity0.attribute' + ruleIndex + ' is at least ' + ruleIndex +
        ' then set entity0.attribute0 to ' + ruleIndex);

    // Every other rule differs, which is the shape a review actually reads
    const changed = ruleIndex % 2 === 0 ? ruleIndex : ruleIndex + 1;
    newLines.push('If entity0.attribute' + ruleIndex + ' is at least ' + changed +
        ' then set entity0.attribute0 to ' + changed);
}

let segments = null;
const diffMs = measure(() => {
    segments = versionsModel.wordDiff(oldLines.join('\n'), newLines.join('\n'));
});
check(`versions diff over ${scale.diffRules} rules (${segments.length} segments)`, diffMs, budgets.versionsDiffMs);

// ////////////////////////////////////////////////////////////////////////

if (failures > 0) {
    console.log(`${failures} scale check(s) failed`);
    process.exit(1);
}
console.log('all scale checks passed');
