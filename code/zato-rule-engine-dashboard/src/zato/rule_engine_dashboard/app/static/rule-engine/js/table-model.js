'use strict';

// Data model for the decision table editor: loading the stored table
// document and the structure edits. How a cell reads back is the server's
// answer, never a grammar of our own, and the server-backed checks live
// in table-checks.js. No DOM access in this file.

(function() {

var tableModel = {

    config: {
        // How long an edit waits before the server validation runs
        checkDelayMilliseconds: 300,

        // What a filter starts as before the author narrows it
        defaultFilterCell: '> 0',

        // The filter editor never shrinks below this, even for a short value
        filterInputMinimumWidth: 160,

        // What a brand-new table is called before its first save
        newTableName: 'Decision table',

        // What the checks say when the table does not hold together yet
        structuralProblemsMessage: 'Fix the structural problems first, the panel below lists them.',

        // What a cell reads as before the first validation has answered, the
        // same as a cell that takes no part in its column
        emptyReading: {kind: 'any'},

        urls: {
            tables: '/rules/rulesets/?object_type=decision-table',
            validate: '/rules/tables/validate/',
            checks: '/rules/tables/checks/',
            expand: '/rules/tables/expand/',
            compress: '/rules/tables/compress/',
            save: '/rules/editor/save/',
            preview: function(id) { return '/rules/rulesets/' + id + '/preview/'; },
            vocabularies: '/rules/rulesets/?object_type=vocabulary',
            vocabularyGet: function(id) { return '/rules/vocabulary/' + id + '/'; },
        },
    },

    // The stored definition this screen edits - null until a table
    // exists, the New table button starts the first one
    definitionId: null,
    currentVersion: null,

    // The canonical table document, edited in place
    table: null,

    // Client-side state that never travels with the document
    checked: {condition: {}, action: {}},
    generatedNumbers: {},
    unfoldSnapshots: {},

    // What the server said last: structural errors from validate, how it
    // read every cell back, and the on-demand check results
    serverErrors: [],
    readings: {},
    conflictResult: null,
    subsumption: [],
    unreachable: [],

    // How a leading comparator symbol reads as words
    symbolPhrases: {
        '==': 'is',
        '!=': 'is not',
        '<': 'is less than',
        '<=': 'is at most',
        '>=': 'is at least',
        '>': 'is more than',
        '=~': 'matches',
    },

// ////////////////////////////////////////////////////////////////////////

    // The screen opens on the table the address names, or on the first
    // stored one
    load: function(onDone) {
        var self = this;
        var wanted = new URLSearchParams(window.location.search).get('table');

        data.get(this.config.urls.tables, function(payload) {
            var records = payload.items;
            if (wanted !== null) {
                records = records.filter(function(item) { return item.id === parseInt(wanted); });
            }

            // No table yet - the screen renders its empty state
            if (records.length === 0) {
                self.loadVocabulary(onDone);
                return;
            }

            var record = records[0];
            self.definitionId = record.id;
            self.currentVersion = record.current_version;

            data.get(self.config.urls.preview(record.id), function(preview) {
                self.table = preview.document;
                self.normalize();
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

// ////////////////////////////////////////////////////////////////////////

    // Every column carries a statement, an overrides list and one cell per
    // condition row, so the rendering never meets a missing key. Column 0
    // sorts first, the way the engine fires it.
    normalize: function() {
        var self = this;

        this.table.columns.sort(function(first, second) {
            var firstKey = first.number === 0 ? -1 : 1;
            var secondKey = second.number === 0 ? -1 : 1;
            return firstKey - secondKey;
        });

        this.table.columns.forEach(function(column) {
            if (column.statement === undefined) { column.statement = {text: '', severity: 'info'}; }
            if (column.overrides === undefined) { column.overrides = []; }

            self.table.conditions.forEach(function(row) {
                if (column.cells[row.letter] === undefined) { column.cells[row.letter] = '-'; }
            });
        });
    },

    // A table that does not exist yet starts as one action-only column
    startNew: function() {
        this.table = {
            name: this.config.newTableName,
            docs: '',
            conditions: [],
            actions: [],
            columns: [{number: 0, cells: {}, actions: {}, statement: {text: '', severity: 'info'}, overrides: []}],
        };
    },

// ////////////////////////////////////////////////////////////////////////

    // The Base column is column 0, every other column is a rule
    label: function(column) {
        var out = column.number === 0 ? 'Base' : String(column.number);
        return out;
    },

    columnByLabel: function(label) {
        var self = this;
        var out = this.table.columns.filter(function(column) { return self.label(column) === label; })[0];
        return out;
    },

    ruleColumns: function() {
        var out = this.table.columns.filter(function(column) { return column.number !== 0; });
        return out;
    },

    // A dotted number like 3.1 marks a sub-rule of column 3
    parentLabel: function(column) {
        var text = String(column.number);
        if (text.indexOf('.') === -1) { return ''; }

        var out = text.split('.')[0];
        return out;
    },

    hasUnfolded: function() {
        var self = this;
        var out = this.table.columns.some(function(column) { return self.parentLabel(column) !== ''; });
        return out;
    },

    conditionRow: function(letter) {
        var out = this.table.conditions.filter(function(row) { return row.letter === letter; })[0];
        return out;
    },

    actionRow: function(target) {
        var out = this.table.actions.filter(function(row) { return row.target === target; })[0];
        return out;
    },

    // The action cell of one column, blank when the column leaves the target alone
    actionCell: function(column, target) {
        var out = column.actions[target];
        if (out === undefined) { out = ''; }
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // A term of the loaded vocabulary, or null for a subject the
    // vocabulary does not know - flat subjects stay editable as free text
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

    // How the server read one condition cell back - the cell grammar lives
    // there alone, so the sentence bar and the unfold hints speak from its
    // answer. Nothing has been read yet before the first validation lands,
    // which is what the empty reading stands for.
    reading: function(column, letter) {
        var columnReadings = this.readings[String(column.number)];
        if (columnReadings === undefined) { return this.config.emptyReading; }

        var out = columnReadings[letter];
        if (out === undefined) { return this.config.emptyReading; }

        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // The condition row on which a column can unfold into sub-rules, if any
    unfoldableRow: function(column) {
        if (column.number === 0 || this.parentLabel(column) !== '') { return null; }

        var out = null;
        var self = this;
        this.table.conditions.forEach(function(row) {
            if (out !== null) { return; }
            var reading = self.reading(column, row.letter);
            if (reading.kind === 'set' && !reading.negated && reading.items.length > 1) { out = row; }
        });

        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // Rule columns number up from just past the highest whole number in use
    nextNumber: function() {
        var highest = 0;
        this.table.columns.forEach(function(column) {
            var match = /^(\d+)/.exec(String(column.number));
            if (match !== null && +match[1] > highest) { highest = +match[1]; }
        });

        var out = highest + 1;
        return out;
    },

    nextLetter: function() {
        var rows = this.table.conditions;
        if (rows.length === 0) { return 'a'; }

        var last = rows[rows.length - 1].letter;
        var out = String.fromCharCode(last.charCodeAt(0) + 1);
        return out;
    },

    addColumn: function() {
        var number = this.nextNumber();
        var cells = {};
        this.table.conditions.forEach(function(row) { cells[row.letter] = '-'; });

        this.table.columns.push({number: number, cells: cells, actions: {},
            statement: {text: '', severity: 'info'}, overrides: []});

        var out = String(number);
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    moveRow: function(kind, fromKey, toKey) {
        var rows = kind === 'condition' ? this.table.conditions : this.table.actions;
        var keyName = kind === 'condition' ? 'letter' : 'target';

        var fromIndex = rows.findIndex(function(row) { return row[keyName] === fromKey; });
        var moved = rows.splice(fromIndex, 1)[0];
        var toIndex = rows.findIndex(function(row) { return row[keyName] === toKey; });
        rows.splice(toIndex, 0, moved);
    },

    // Move a row one step up or down, for Shift with an arrow key
    moveRowByOffset: function(kind, key, offset) {
        var rows = kind === 'condition' ? this.table.conditions : this.table.actions;
        var keyName = kind === 'condition' ? 'letter' : 'target';

        var fromIndex = rows.findIndex(function(row) { return row[keyName] === key; });
        var toIndex = fromIndex + offset;

        // Clamped at the edges, the caller learns nothing moved
        if (toIndex < 0 || toIndex >= rows.length) { return false; }

        var moved = rows.splice(fromIndex, 1)[0];
        rows.splice(toIndex, 0, moved);
        return true;
    },

    // Move a rule column one step left or right, the Base column never
    // moves and nothing moves into its place
    moveColumnByOffset: function(label, offset) {
        var self = this;
        var columns = this.table.columns;
        var fromIndex = columns.findIndex(function(column) { return self.label(column) === label; });
        if (columns[fromIndex].number === 0) { return false; }

        var toIndex = fromIndex + offset;
        if (toIndex < 1 || toIndex >= columns.length) { return false; }

        var moved = columns.splice(fromIndex, 1)[0];
        columns.splice(toIndex, 0, moved);
        return true;
    },

    // Move a rule column in front of another one, the Base column never moves
    moveColumn: function(fromLabel, toLabel) {
        var self = this;
        var columns = this.table.columns;
        var fromIndex = columns.findIndex(function(column) { return self.label(column) === fromLabel; });
        var moved = columns.splice(fromIndex, 1)[0];
        var toIndex = columns.findIndex(function(column) { return self.label(column) === toLabel; });
        columns.splice(toIndex, 0, moved);
    },

// ////////////////////////////////////////////////////////////////////////

    addRowFromVocabulary: function(path, kind) {
        var out;

        if (kind === 'condition') {
            var letter = this.nextLetter();
            this.table.conditions.push({letter: letter, subject: path});
            this.table.columns.forEach(function(column) { column.cells[letter] = '-'; });
            out = letter;
        } else {
            this.table.actions.push({target: path});
            out = path;
        }

        return out;
    },

    // Delete one row and its cells in every column
    deleteRow: function(kind, key) {
        if (kind === 'condition') {
            this.table.conditions = this.table.conditions.filter(function(row) { return row.letter !== key; });
            this.table.columns.forEach(function(column) { delete column.cells[key]; });
        } else {
            this.table.actions = this.table.actions.filter(function(row) { return row.target !== key; });
            this.table.columns.forEach(function(column) { delete column.actions[key]; });
        }
        delete this.checked[kind][key];
    },

    deleteCheckedRows: function(kind) {
        var self = this;
        var keys = Object.keys(this.checked[kind]);
        keys.forEach(function(key) { self.deleteRow(kind, key); });
    },

    checkedCount: function(kind) {
        var out = Object.keys(this.checked[kind]).length;
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // The table carries at most one filter - it narrows the data every
    // rule column sees before anything runs
    addFilter: function() {
        var subject = this.table.conditions.length === 0 ? '' : this.table.conditions[0].subject;
        this.table.filter = {subject: subject, cell: this.config.defaultFilterCell};
    },

    removeFilter: function() {
        delete this.table.filter;
    },

    // Paths already used by the filter or a row, grayed out in the vocabulary pane
    usedPaths: function() {
        var out = [];
        if (this.table.filter !== undefined) { out.push(this.table.filter.subject); }
        this.table.conditions.forEach(function(row) { out.push(row.subject); });
        this.table.actions.forEach(function(row) { out.push(row.target); });

        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    save: function(onDone, onError) {
        var self = this;

        var body = {
            document: this.table,
            comment: 'Edited table ' + this.table.name,
        };

        // An existing table gains a new optimistic version, a new one
        // comes into being together with its first version
        if (this.definitionId !== null) {
            body.definition_id = this.definitionId;
            body.expected_current_version = this.currentVersion;
        } else {
            body.name = this.table.name;
            body.object_type = 'decision-table';
        }

        data.post(this.config.urls.save, body, function(payload) {
            self.definitionId = payload.definition_id;
            self.currentVersion = payload.version;
            onDone(payload);
        }, onError);
    },
};

window.tableModel = tableModel;

})();
