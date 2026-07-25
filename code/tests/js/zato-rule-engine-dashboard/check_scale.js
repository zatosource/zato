'use strict';

// The scale smoke: the editor must stay fluid at sizes where rule editors
// are commonly reported to degrade.
//
// - Completion menus elsewhere become slow on a large vocabulary: our
//   completion list must build instantly over 5000 terms.
// - Table editors elsewhere are reported to delay every keystroke around
//   80 rows by 30 columns: our grid rendering must stay fast well past
//   that, at 120 columns by 40 rows.
//
// The live-outcomes loop runs server-side in this product, so its budget
// lives with the Python suite against the outcomes endpoint.
//
// Run with: node check_scale.js <webapp js dir> <dashboard js dir>

const fs = require('fs');
const path = require('path');
const vm = require('vm');

// The budgets, in milliseconds. These are smoke-tested numbers, not
// adjectives: a breach fails the build.
const budgets = {
    completionBuildMs: 50,
    completionFilterMs: 50,
    gridBuildMs: 250,
};

const scale = {
    vocabularyEntities: 50,
    attributesPerEntity: 100,
    gridColumns: 120,
    gridRows: 40,
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

[path.join(webappJsDir, 'shared.js'),
 path.join(dashboardJsDir, 'vocabulary.js'),
 path.join(dashboardJsDir, 'editor-model.js'),
 path.join(dashboardJsDir, 'editor-checks.js'),
 path.join(dashboardJsDir, 'editor-render.js'),
 path.join(dashboardJsDir, 'editor-views.js'),
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

if (failures > 0) {
    console.log(`${failures} scale check(s) failed`);
    process.exit(1);
}
console.log('all scale checks passed');
