'use strict';

(function() {

var tableModel = {

    config: {
        checkDelayMilliseconds: 300,

        defaultFilterCell: '> 0',

        filterInputMinimumWidth: 160,

        newTableName: 'Decision table',

        structuralProblemsMessage: 'Fix the structural problems first, the panel below lists them.',

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

    definitionId: null,
    currentVersion: null,

    table: null,

    checked: {condition: {}, action: {}},
    generatedNumbers: {},
    unfoldSnapshots: {},

    serverErrors: [],
    readings: {},
    conflictResult: null,
    subsumption: [],
    unreachable: [],

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

    load: function(onDone) {
        var self = this;
        var wanted = new URLSearchParams(window.location.search).get('table');

        data.get(this.config.urls.tables, function(payload) {
            var records = payload.items;
            if (wanted !== null) {
                records = records.filter(function(item) { return item.id === parseInt(wanted); });
            }

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

    actionCell: function(column, target) {
        var out = column.actions[target];
        if (out === undefined) { out = ''; }
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

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

    reading: function(column, letter) {
        var columnReadings = this.readings[String(column.number)];
        if (columnReadings === undefined) { return this.config.emptyReading; }

        var out = columnReadings[letter];
        if (out === undefined) { return this.config.emptyReading; }

        return out;
    },

// ////////////////////////////////////////////////////////////////////////

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

    moveRowByOffset: function(kind, key, offset) {
        var rows = kind === 'condition' ? this.table.conditions : this.table.actions;
        var keyName = kind === 'condition' ? 'letter' : 'target';

        var fromIndex = rows.findIndex(function(row) { return row[keyName] === key; });
        var toIndex = fromIndex + offset;

        if (toIndex < 0 || toIndex >= rows.length) { return false; }

        var moved = rows.splice(fromIndex, 1)[0];
        rows.splice(toIndex, 0, moved);
        return true;
    },

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

    addFilter: function() {
        var subject = this.table.conditions.length === 0 ? '' : this.table.conditions[0].subject;
        this.table.filter = {subject: subject, cell: this.config.defaultFilterCell};
    },

    removeFilter: function() {
        delete this.table.filter;
    },

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
