'use strict';

// In-place editing on the decision table grid: cell values through typed
// inputs and pick lists, the filter line, the plain-language statements,
// their severity and the override declarations. Augments the tableView
// namespace from table-render.js.

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

})();
