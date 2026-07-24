'use strict';

// Event handlers for the decision table editor: cell and filter editing,
// the on-demand server checks, unfold, fold and compress, find and
// replace, the keyboard cursor and the save that stores a new version.
// Augments the tableView namespace from table-render.js.

(function() {

// ////////////////////////////////////////////////////////////////////////

tableView.selectColumn = function(label) {
    this.selectedColumn = this.selectedColumn === label ? null : label;
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

tableView.wireTextInput = function(input, commit, cancel) {
    input.focus();
    input.select();
    input.onkeydown = function(event) {
        if (event.key === 'Enter') { commit(input.value.trim()); }
        if (event.key === 'Escape') { cancel(); }
    };
    input.onblur = function() {
        if (tableView.editing) { commit(input.value.trim()); }
    };
};

tableView.editCell = function(cell, columnLabel, rowKey, kind) {
    if (this.editing) { return; }
    if (tableModel.hasUnfolded()) {
        shared.popover(cell, 'The sub-rules are a read-only view of the same stored column. Fold them back to edit.');
        return;
    }

    var self = this;
    var column = tableModel.columnByLabel(columnLabel);
    var path = kind === 'condition' ? tableModel.conditionRow(rowKey).subject : rowKey;
    var term = tableModel.termFor(path);
    var raw = kind === 'condition' ? column.cells[rowKey] : tableModel.actionCell(column, rowKey);
    this.editing = true;

    // The editor takes the cell's exact box, so the grid never shifts
    cell.classList.add('cell-editing');

    var commit = function(value) {
        self.editing = false;

        // A blank condition cell is the any dash, a blank action cell
        // means the column leaves the target alone
        if (kind === 'condition') {
            column.cells[rowKey] = (value === '' ? '-' : value);
        } else if (value === '' || value === '-') {
            delete column.actions[rowKey];
        } else {
            column.actions[rowKey] = value;
        }

        // A proposed column loses its completeness highlight once it has an action ..
        var highlightCleared = false;
        if (tableModel.generatedNumbers[columnLabel] === true && Object.keys(column.actions).length > 0) {
            delete tableModel.generatedNumbers[columnLabel];
            highlightCleared = true;
        }

        self.render();

        // .. and the message appears on that column's header, not in a corner.
        if (highlightCleared) {
            shared.popover(document.querySelector('th[data-column="' + columnLabel + '"]'),
                'Rule ' + columnLabel + ' now has an action, the completeness highlight is cleared.', 'green');
        }
    };
    var cancel = function() { self.editing = false; self.render(); };

    // Choices edit through a closed pick list, with an escape hatch for sets ..
    if (term !== null && term.type === 'choice' && kind === 'condition') {
        var options = '<option value="-">- any</option>';
        term.values.forEach(function(value) {
            options += '<option value="' + value + '"' + (raw === value ? ' selected' : '') + '>' + value + '</option>';
        });
        var setLabel = /\{/.test(raw) ? raw : 'in {' + term.values.slice(0, 2).join(', ') + '}';
        options += '<option value="__set">' + shared.escape(setLabel) + ' &hellip; edit set</option>';

        cell.innerHTML = '<select>' + options + '</select>';
        var select = cell.querySelector('select');
        select.focus();
        select.onchange = function() {
            if (select.value === '__set') {
                cell.innerHTML = '<input type="text" value="' + shared.escape(/\{/.test(raw) ? raw : setLabel) + '">';
                self.wireTextInput(cell.querySelector('input'), commit, cancel);
                return;
            }
            commit(select.value);
        };
        select.onblur = function() { if (self.editing) { cancel(); } };
        return;
    }

    // .. yes/no values through a three-way pick list ..
    if (term !== null && term.type === 'yes/no') {
        var blank = kind === 'condition' ? '-' : '';
        var yesNoOptions = '<option value="' + blank + '"' + ((raw === '' || raw === '-') ? ' selected' : '') + '>-</option>' +
            '<option value="true"' + (raw === 'true' ? ' selected' : '') + '>true</option>' +
            '<option value="false"' + (raw === 'false' ? ' selected' : '') + '>false</option>';
        cell.innerHTML = '<select>' + yesNoOptions + '</select>';
        var yesNoSelect = cell.querySelector('select');
        yesNoSelect.focus();
        yesNoSelect.onchange = function() { commit(yesNoSelect.value); };
        yesNoSelect.onblur = function() { if (self.editing) { cancel(); } };
        return;
    }

    // .. and everything else through free typing, validated by the server
    // as soon as the value lands.
    var placeholder = kind === 'condition' ? '18..65, in {A, B}, >= 10, or -' : 'value';
    cell.innerHTML = '<input type="text" value="' + shared.escape(raw === '-' ? '' : raw) + '" ' +
        'placeholder="' + placeholder + '">';
    this.wireTextInput(cell.querySelector('input'), commit, cancel);
};

// ////////////////////////////////////////////////////////////////////////

// The filter edits as one line: its subject, then the cell in the same
// syntax every condition cell uses
tableView.editFilter = function(span) {
    if (this.phraseMode) {
        shared.popover(span, 'The phrase view keeps the logic closed. Switch back to edit the filter.');
        return;
    }
    if (this.editing) { return; }

    var self = this;
    var filter = tableModel.table.filter;
    this.editing = true;

    // The input inherits the expression's own footprint, so the row
    // keeps its size while the value is being typed
    var spanWidth = Math.max(tableModel.config.filterInputMinimumWidth, span.offsetWidth + 12);
    span.outerHTML = '<input type="text" id="filter-input" class="table-filter-input" ' +
        'style="width:' + spanWidth + 'px" value="' + shared.escape(filter.subject + ' ' + filter.cell) + '">';

    var commit = function(value) {
        self.editing = false;
        var separator = value.indexOf(' ');
        if (separator > 0) {
            filter.subject = value.slice(0, separator);
            filter.cell = value.slice(separator + 1).trim();
        }
        self.render();
    };

    var input = document.getElementById('filter-input');
    input.focus();
    input.onkeydown = function(event) {
        if (event.key === 'Enter') { commit(input.value.trim()); }
        if (event.key === 'Escape') { self.editing = false; self.render(); }
    };
    input.onblur = function() {
        if (self.editing) { commit(input.value.trim()); }
    };
};

tableView.addFilter = function() {
    tableModel.addFilter();
    this.render();
};

tableView.removeFilter = function(event) {
    event.stopPropagation();
    tableModel.removeFilter();
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

tableView.editStatement = function(span, columnLabel) {
    if (this.editing) { return; }

    var self = this;
    var column = tableModel.columnByLabel(columnLabel);
    var wrap = span.parentElement;
    this.editing = true;

    // The textarea starts at the exact height of the text it replaces,
    // so the row does not jump when editing begins
    var spanHeight = span.offsetHeight;
    span.outerHTML = '<textarea style="height:' + spanHeight + 'px">' + shared.escape(column.statement.text) + '</textarea>';
    var textarea = wrap.querySelector('textarea');
    textarea.focus();
    textarea.onkeydown = function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            self.editing = false;
            column.statement.text = textarea.value.trim();
            self.render();
        }
        if (event.key === 'Escape') { self.editing = false; self.render(); }
    };
    textarea.onblur = function() {
        if (self.editing) { self.editing = false; column.statement.text = textarea.value.trim(); self.render(); }
    };
};

tableView.cycleSeverity = function(columnLabel) {
    var order = ['info', 'warning', 'violation'];
    var column = tableModel.columnByLabel(columnLabel);
    var next = order[(order.indexOf(column.statement.severity) + 1) % order.length];
    column.statement.severity = next;
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

// An override is a declaration in the document: the column carries the
// numbers it wins over, never an execution ordering
tableView.setOverride = function(columnLabel, value) {
    var column = tableModel.columnByLabel(columnLabel);
    column.overrides = value === '' ? [] : [parseInt(value)];

    // A fresh conflict check answers whether the declaration resolved anything
    var anchor = document.querySelector('.table-override-cell[data-column="' + columnLabel + '"] select');
    var countBefore = tableModel.conflictLabels().length;

    var self = this;
    tableModel.runChecks(function(payload) {
        tableModel.conflictResult = payload.conflicts;
        tableModel.subsumption = payload.subsumption;
        tableModel.unreachable = payload.unreachable;

        if (value !== '' && tableModel.conflictLabels().length < countBefore) {
            shared.popover(anchor, 'The conflict is resolved: when both rules match the same data, rule ' +
                columnLabel + ' wins and rule ' + value + ' stays silent.', 'green');
        }
        self.render();
    }, function() {
        self.render();
    });
};

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
        var proposed = payload.completeness.proposed;

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
