'use strict';

// Event handlers for the decision table editor: the on-demand server
// checks, unfold, fold and compress, find and replace, the keyboard
// cursor and the save that stores a new version. The in-place editing
// handlers live in table-edit.js. Augments the tableView namespace
// from table-render.js.

(function() {

// ////////////////////////////////////////////////////////////////////////

// The on-demand checks only run over the stored, folded columns -
// the dotted sub-rule numbers are a display artifact the server never stores
tableView.checksBlocked = function(button) {
    if (tableModel.hasUnfolded()) {
        shared.popover(button, 'Fold the sub-rules back first, checks run over the stored columns.');
        return true;
    }
    return false;
};

// A check refused for structural problems also refreshes the problems
// panel, so the message and the list under it agree
tableView.reportCheckFailure = function(button, message) {
    this.renderProblems();
    this.shadeInvalidCells();
    shared.popover(button, message, 'red');
};

tableView.checkConflicts = function() {
    var self = this;
    var button = document.getElementById('button-conflicts');
    if (this.checksBlocked(button)) { return; }

    tableModel.runChecks(function(payload) {
        tableModel.conflictResult = payload.conflicts;
        tableModel.subsumption = payload.subsumption;
        tableModel.unreachable = payload.unreachable;
        self.render();

        var conflicts = payload.conflicts.conflicts;
        if (conflicts.length === 0) {
            shared.popover(button, 'No conflicts. Every pair of rules either matches different data, ' +
                'assigns the same values, or is covered by an override.', 'green');
        } else {
            var suffix = conflicts.length === 1 ? 'conflict' : 'conflicts';
            var description = conflicts.map(function(pair) { return 'rules ' + pair.first + ' and ' + pair.second; }).join(', ');
            shared.popover(button, conflicts.length + ' ' + suffix + ' found: ' + description +
                '. Conflicting columns are shaded red, details are in the problems panel.', 'red');
        }
    }, function(message) {
        self.reportCheckFailure(button, message);
    });
};

tableView.checkCompleteness = function() {
    var self = this;
    var button = document.getElementById('button-completeness');
    if (this.checksBlocked(button)) { return; }

    tableModel.runChecks(function(payload) {
        var completeness = payload.completeness;
        var proposed = completeness.proposed;

        // A table whose rows multiply out past the ceiling is never swept, and saying
        // so is the answer - narrowing the rows is what makes the check meaningful again
        if (completeness.too_large) {
            self.render();
            shared.popover(button, 'This table asks for ' + completeness.combinations +
                ' combinations, too many to check one by one. Narrowing the values in the ' +
                'condition rows brings it back into range.', 'red');
            return;
        }

        if (proposed.length === 0) {
            self.render();
            shared.popover(button, 'No missing combinations, every value the cells speak of is handled.', 'green');
            return;
        }

        // Each gap arrives as a proposed column with the missing cells
        // and deliberately empty actions - choosing them is the author's job
        var labels = [];
        proposed.forEach(function(proposal) {
            var cells = {};
            tableModel.table.conditions.forEach(function(row) {
                var text = proposal.cells[row.letter];
                cells[row.letter] = (text === undefined ? '-' : text);
            });

            tableModel.table.columns.push({number: proposal.number, cells: cells, actions: {},
                statement: {text: '', severity: 'info'}, overrides: []});
            tableModel.generatedNumbers[String(proposal.number)] = true;
            labels.push(String(proposal.number));
        });

        self.render();
        var gapText = labels.length === 1 ? '1 missing combination was' : labels.length + ' missing combinations were';
        var ruleWord = labels.length === 1 ? 'rule ' : 'rules ';
        shared.popover(button, gapText + ' added as ' + ruleWord + labels.join(', ') +
            ', shaded green. The check only fills in the missing conditions, every action stays yours to decide.', 'green');
    }, function(message) {
        self.reportCheckFailure(button, message);
    });
};

// ////////////////////////////////////////////////////////////////////////

// Unfolding asks the server to expand one column into its dotted
// sub-rules, one per value a multi-value cell holds - a read-only view
// of the same stored column
tableView.unfoldColumn = function(event, label) {
    event.stopPropagation();
    var self = this;
    var column = tableModel.columnByLabel(label);
    var single = Object.assign({}, tableModel.table, {columns: [column]});

    tableModel.withValidTable(function() {
        data.post(tableModel.config.urls.expand, {table: single}, function(payload) {
            tableModel.unfoldSnapshots[label] = column;

            var position = tableModel.table.columns.indexOf(column);
            var columns = tableModel.table.columns;
            tableModel.table.columns = columns.slice(0, position).concat(payload.documents, columns.slice(position + 1));
            tableModel.normalize();

            self.selectedColumn = null;
            self.render();
        }, data.reportError);
    }, data.reportError);
};

tableView.foldColumn = function(event, parentLabel) {
    event.stopPropagation();

    var position = -1;
    tableModel.table.columns.forEach(function(column, columnIndex) {
        if (tableModel.parentLabel(column) === parentLabel && position === -1) { position = columnIndex; }
    });

    tableModel.table.columns = tableModel.table.columns.filter(function(column) {
        return tableModel.parentLabel(column) !== parentLabel;
    });
    tableModel.table.columns.splice(position, 0, tableModel.unfoldSnapshots[parentLabel]);
    delete tableModel.unfoldSnapshots[parentLabel];

    this.selectedColumn = null;
    this.render();
};

tableView.toggleUnfoldAll = function() {
    var self = this;
    var button = document.getElementById('button-unfold');

    if (tableModel.hasUnfolded()) {
        // Fold every unfolded parent back into its original column ..
        Object.keys(tableModel.unfoldSnapshots).forEach(function(parentLabel) {
            tableView.foldColumn({stopPropagation: function() {}}, parentLabel);
        });
        return;
    }

    // .. or unfold every column that holds more than one value.
    var unfoldable = [];
    tableModel.table.columns.forEach(function(column) {
        if (tableModel.unfoldableRow(column) !== null) { unfoldable.push(tableModel.label(column)); }
    });
    if (unfoldable.length === 0) {
        shared.popover(button, 'Nothing to unfold: no cell holds more than one value.');
        return;
    }

    // One column at a time, so each keeps its own fold-back snapshot
    var next = function() {
        if (unfoldable.length === 0) { return; }
        var label = unfoldable.shift();

        var column = tableModel.columnByLabel(label);
        var single = Object.assign({}, tableModel.table, {columns: [column]});

        data.post(tableModel.config.urls.expand, {table: single}, function(payload) {
            tableModel.unfoldSnapshots[label] = column;

            var position = tableModel.table.columns.indexOf(column);
            var columns = tableModel.table.columns;
            tableModel.table.columns = columns.slice(0, position).concat(payload.documents, columns.slice(position + 1));
            tableModel.normalize();

            self.selectedColumn = null;
            self.render();
            next();
        }, data.reportError);
    };

    tableModel.withValidTable(next, function(message) {
        self.reportCheckFailure(button, message);
    });
};

tableView.updateUnfoldAllButton = function() {
    var button = document.getElementById('button-unfold');
    var isUnfolded = tableModel.hasUnfolded();
    button.textContent = isUnfolded ? 'Fold rules' : 'Unfold rules';
    button.classList.toggle('toggled', isUnfolded);
};

// ////////////////////////////////////////////////////////////////////////

// Compression is the inverse of unfolding, done by the server on the
// stored document itself: columns differing in one row merge into
// membership cells and the survivors renumber
tableView.compress = function() {
    var self = this;
    var button = document.getElementById('button-compress');
    if (this.checksBlocked(button)) { return; }

    var countBefore = tableModel.table.columns.length;

    tableModel.withValidTable(function() {
        data.post(tableModel.config.urls.compress, {table: tableModel.table}, function(payload) {
            tableModel.table = payload.table;
            tableModel.normalize();
            tableModel.generatedNumbers = {};
            self.selectedColumn = null;
            self.render();

            var merged = countBefore - tableModel.table.columns.length;
            if (merged === 0) {
                shared.popover(button, 'Nothing to compress: no two columns differ in exactly one row with the same actions.');
            } else {
                var suffix = merged === 1 ? 'column' : 'columns';
                shared.popover(button, merged + ' ' + suffix + ' merged into membership cells, the rules renumbered.', 'green');
            }
        }, function(message) {
            shared.popover(button, message, 'red');
        });
    }, function(message) {
        self.reportCheckFailure(button, message);
    });
};

// ////////////////////////////////////////////////////////////////////////

tableView.togglePhrases = function() {
    this.phraseMode = !this.phraseMode;

    var button = document.getElementById('button-phrases');
    button.classList.toggle('toggled', this.phraseMode);
    document.getElementById('table-phrase-note').classList.toggle('visible', this.phraseMode);
    document.getElementById('button-add-column').disabled = this.phraseMode;
    document.getElementById('vocabulary-pane').classList.toggle('vocabulary-locked', this.phraseMode);
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

tableView.doReplace = function() {
    var button = document.getElementById('button-replace');
    var term = this.findTerm();
    var replacement = document.getElementById('replace-input').value;

    if (term === '') {
        shared.popover(button, 'Type something in the find box first.');
        return;
    }

    var count = 0;
    tableModel.table.columns.forEach(function(column) {
        Object.keys(column.cells).forEach(function(letter) {
            if (column.cells[letter].indexOf(term) > -1) {
                column.cells[letter] = column.cells[letter].split(term).join(replacement);
                count += 1;
            }
        });
        Object.keys(column.actions).forEach(function(target) {
            if (column.actions[target].indexOf(term) > -1) {
                column.actions[target] = column.actions[target].split(term).join(replacement);
                count += 1;
            }
        });
    });

    this.render();
    var suffix = count === 1 ? 'cell' : 'cells';
    shared.popover(button, count + ' ' + suffix + ' updated.', count > 0 ? 'green' : '');
};

// ////////////////////////////////////////////////////////////////////////

tableView.addColumn = function() {
    var label = tableModel.addColumn();
    this.selectedColumn = label;
    this.render();
    this.flashColumn(label);
};

tableView.startNew = function() {
    tableModel.startNew();
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

tableView.toggleRowCheck = function(kind, rowKey, checked) {
    if (checked) {
        tableModel.checked[kind][rowKey] = true;
    } else {
        delete tableModel.checked[kind][rowKey];
    }

    // Re-render so the delete control appears next to the checkboxes
    this.render();
};

tableView.deleteCheckedRows = function(kind) {
    tableModel.deleteCheckedRows(kind);
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

// The keyboard cursor on the grid: arrows move it, Enter edits the cell
tableView.cursor = null;

tableView.applyCursor = function() {
    document.querySelectorAll('.table-cell-cursor').forEach(function(element) {
        element.classList.remove('table-cell-cursor');
    });
    if (this.cursor === null) { return; }

    var cell = this.cursorCell();
    if (cell !== null) { cell.classList.add('table-cell-cursor'); }
};

tableView.cursorCell = function() {
    var selector = 'td[data-kind="' + this.cursor.kind + '"][data-row-id="' + this.cursor.rowKey + '"]' +
        '[data-column="' + this.cursor.column + '"]';
    var out = document.querySelector(selector);
    return out;
};

// All grid rows in keyboard order, conditions first, then actions
tableView.cursorRows = function() {
    var out = [];
    tableModel.table.conditions.forEach(function(row) { out.push({kind: 'condition', key: row.letter}); });
    tableModel.table.actions.forEach(function(row) { out.push({kind: 'action', key: row.target}); });

    return out;
};

tableView.moveCursor = function(key) {
    var rows = this.cursorRows();
    if (rows.length === 0) { return; }
    var columns = tableModel.table.columns.map(function(column) { return tableModel.label(column); });

    // The cursor starts on the first cell when nothing is focused yet ..
    if (this.cursor === null) {
        this.cursor = {kind: rows[0].kind, rowKey: rows[0].key, column: columns[0]};
        this.applyCursor();
        return;
    }

    var self = this;
    var rowIndex = rows.findIndex(function(row) { return row.kind === self.cursor.kind && row.key === self.cursor.rowKey; });
    var columnIndex = columns.indexOf(this.cursor.column);

    // .. arrows move it with clamping at the edges ..
    if (key === 'ArrowRight') { columnIndex = Math.min(columnIndex + 1, columns.length - 1); }
    if (key === 'ArrowLeft') { columnIndex = Math.max(columnIndex - 1, 0); }
    if (key === 'ArrowDown') { rowIndex = Math.min(rowIndex + 1, rows.length - 1); }
    if (key === 'ArrowUp') { rowIndex = Math.max(rowIndex - 1, 0); }

    this.cursor = {kind: rows[rowIndex].kind, rowKey: rows[rowIndex].key, column: columns[columnIndex]};
    this.applyCursor();

    var cell = this.cursorCell();
    if (cell !== null) { cell.scrollIntoView({behavior: 'smooth', block: 'nearest', inline: 'nearest'}); }

    // .. and Enter opens the focused cell for editing, readonly cells ignore it.
    if (key === 'Enter') {
        if (cell !== null && !cell.classList.contains('table-cell-readonly')) { cell.click(); }
    }
};

// Shift with an arrow moves the cursor's own row or column in the grid
tableView.reorderFromKeyboard = function(key) {
    if (this.cursor === null) { return; }
    var moved;

    if (key === 'ArrowUp' || key === 'ArrowDown') {
        moved = tableModel.moveRowByOffset(this.cursor.kind, this.cursor.rowKey, key === 'ArrowUp' ? -1 : 1);
    } else {
        moved = tableModel.moveColumnByOffset(this.cursor.column, key === 'ArrowLeft' ? -1 : 1);
    }

    if (moved) { this.render(); }
};

document.addEventListener('keydown', function(event) {
    if (tableView.editing || tableModel.table === null) { return; }
    var tagName = event.target.tagName;
    if (tagName === 'INPUT' || tagName === 'TEXTAREA' || tagName === 'SELECT') { return; }

    var keys = ['ArrowRight', 'ArrowLeft', 'ArrowUp', 'ArrowDown', 'Enter'];
    if (keys.indexOf(event.key) === -1) { return; }
    event.preventDefault();

    if (event.shiftKey && event.key !== 'Enter') {
        tableView.reorderFromKeyboard(event.key);
        return;
    }
    tableView.moveCursor(event.key);
});

// ////////////////////////////////////////////////////////////////////////

// Save stores the whole table document as a new optimistic version -
// a first save creates the definition itself
tableView.save = function(button) {
    if (tableModel.table === null) { return; }
    if (tableModel.hasUnfolded()) {
        shared.popover(button, 'Fold the sub-rules back first, the stored document holds the folded columns.');
        return;
    }

    var self = this;

    // Only a table whose cells all parse gets stored
    tableModel.withValidTable(function() {
        tableModel.save(function(payload) {
            self.renderSubtitle();
            shared.popover(button, 'Saved as version ' + payload.version + '.', 'green');
        }, function(message) {
            shared.popover(button, message, 'red');
        });
    }, function(message) {
        self.reportCheckFailure(button, message);
    });
};

tableView.openTests = function() {
    window.location.href = '/tests/';
};

// ////////////////////////////////////////////////////////////////////////

tableModel.load(function() {
    tableView.render();

    if (tableModel.table === null) { return; }

    // Arriving from the vocabulary's where-used list: every row of that
    // term glows and the first one scrolls into view
    var termToHighlight = shared.termFromHash();
    if (termToHighlight !== null) {
        var termElements = [];

        var rowKeys = [];
        tableModel.table.conditions.forEach(function(row) {
            if (row.subject === termToHighlight) { rowKeys.push(row.letter); }
        });
        tableModel.table.actions.forEach(function(row) {
            if (row.target === termToHighlight) { rowKeys.push(row.target); }
        });
        rowKeys.forEach(function(rowKey) {
            document.querySelectorAll('tr[data-row="' + rowKey + '"] > td').forEach(function(cell) {
                termElements.push(cell);
            });
        });

        if (tableModel.table.filter !== undefined && tableModel.table.filter.subject === termToHighlight) {
            document.querySelectorAll('.table-filter-row > td').forEach(function(cell) {
                termElements.push(cell);
            });
        }

        document.querySelectorAll('.vocabulary-item[data-path="' + termToHighlight + '"]').forEach(function(item) {
            termElements.push(item);
        });

        shared.applyTermHighlight(termElements);
    }
});

})();
