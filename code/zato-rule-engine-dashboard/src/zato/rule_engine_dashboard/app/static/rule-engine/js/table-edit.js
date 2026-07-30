'use strict';

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
        shared.popover(cell, 'Fold the sub-rules back to edit.');
        return;
    }

    var self = this;
    var column = tableModel.columnByLabel(columnLabel);
    var path = kind === 'condition' ? tableModel.conditionRow(rowKey).subject : rowKey;
    var term = tableModel.termFor(path);
    var raw = kind === 'condition' ? column.cells[rowKey] : tableModel.actionCell(column, rowKey);
    this.editing = true;

    cell.classList.add('cell-editing');

    var commit = function(value) {
        self.editing = false;

        if (kind === 'condition') {
            column.cells[rowKey] = (value === '' ? '-' : value);
        } else if (value === '' || value === '-') {
            delete column.actions[rowKey];
        } else {
            column.actions[rowKey] = value;
        }

        var highlightCleared = false;
        if (tableModel.generatedNumbers[columnLabel] === true && Object.keys(column.actions).length > 0) {
            delete tableModel.generatedNumbers[columnLabel];
            highlightCleared = true;
        }

        self.render();

        if (highlightCleared) {
            shared.popover(document.querySelector('th[data-column="' + columnLabel + '"]'),
                'Rule ' + columnLabel + ' has an action now', 'green');
        }
    };
    var cancel = function() { self.editing = false; self.render(); };

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

    var placeholder = kind === 'condition' ? '18..65, in {A, B}, >= 10, or -' : 'value';
    cell.innerHTML = '<input type="text" value="' + shared.escape(raw === '-' ? '' : raw) + '" ' +
        'placeholder="' + placeholder + '">';
    this.wireTextInput(cell.querySelector('input'), commit, cancel);
};

// ////////////////////////////////////////////////////////////////////////

tableView.editFilter = function(span) {
    if (this.phraseMode) {
        shared.popover(span, 'Switch off the phrase view to edit');
        return;
    }
    if (this.editing) { return; }

    var self = this;
    var filter = tableModel.table.filter;
    this.editing = true;

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

tableView.setOverride = function(columnLabel, value) {
    var column = tableModel.columnByLabel(columnLabel);
    column.overrides = value === '' ? [] : [parseInt(value)];

    var anchor = document.querySelector('.table-override-cell[data-column="' + columnLabel + '"] select');
    var countBefore = tableModel.conflictLabels().length;

    var self = this;
    tableModel.runChecks(function(payload) {
        tableModel.conflictResult = payload.conflicts;
        tableModel.subsumption = payload.subsumption;
        tableModel.unreachable = payload.unreachable;

        if (value !== '' && tableModel.conflictLabels().length < countBefore) {
            shared.popover(anchor, 'Rule ' + columnLabel + ' wins over rule ' + value, 'green');
        }
        self.render();
    }, function() {
        self.render();
    });
};

// ////////////////////////////////////////////////////////////////////////

})();
