'use strict';

// The grid of the decision table editor as html: the column headers with
// their unfold hints, the filter and section rows, and every condition,
// action, override and message cell. Nothing here touches the DOM, which
// is what lets the scale check measure a grid no browser is around for.
// Augments the tableView namespace from table-render.js.

(function() {

var tableView = window.tableView;

// ////////////////////////////////////////////////////////////////////////

tableView.cellDisplay = function(raw) {
    var value = raw.trim();
    if (value === '' || value === '-') { return '<span class="table-any-dash">-</span>'; }
    return shared.escape(value);
};

tableView.statementHtml = function(text) {
    var out = shared.escape(text).replace(/\{[a-zA-Z._]+\}/g, function(match) {
        return '<span class="table-statement-placeholder">' + match + '</span>';
    });
    return out;
};

tableView.cellClasses = function(column, raw, context, rowKey) {
    var label = tableModel.label(column);
    var classes = ['table-cell'];

    if (context.invalid[label + '|' + rowKey] === true) { classes.push('table-cell-invalid'); }
    if (tableModel.generatedNumbers[label] === true) { classes.push('table-cell-generated'); }
    if (context.conflictLabels.indexOf(label) > -1) { classes.push('table-cell-conflict'); }
    if (this.selectedColumn === label) { classes.push('table-column-selected'); }

    var term = context.findTerm;
    if (term !== '' && raw.indexOf(term) > -1) { classes.push('table-find-hit'); }

    var out = classes.join(' ');
    return out;
};

// Checkbox and drag handle in front of a row, hidden in the phrase view
tableView.rowControls = function(kind, rowKey) {
    if (this.phraseMode) { return ''; }

    var checked = tableModel.checked[kind][rowKey] === true ? ' checked' : '';
    var out = '<input type="checkbox" class="table-row-checkbox"' + checked +
        ' onchange="tableView.toggleRowCheck(\'' + kind + '\', \'' + rowKey + '\', this.checked)">' +
        '<span class="table-drag-handle" draggable="true" data-kind="' + kind + '" data-row="' + rowKey + '" ' +
        'data-tippy-content="Drag to reorder this row">' + shared.icon('grip-vertical', 11) + '</span>';

    return out;
};

// ////////////////////////////////////////////////////////////////////////

tableView.columnHeadHtml = function(column, context) {
    var label = tableModel.label(column);
    var classes = ['table-column-head'];
    if (column.number === 0) { classes.push('table-column-zero'); }
    if (context.conflictLabels.indexOf(label) > -1) { classes.push('table-cell-conflict'); }
    if (this.selectedColumn === label) { classes.push('table-column-selected'); }

    var subtitle = '';
    var tooltip = '';
    if (column.number === 0) {
        subtitle = '<span class="table-column-subtitle">always, fires first</span>';
        tooltip = ' data-tippy-content="The Base column has actions only. It always fires and it fires first."';
    }

    // Rule columns can be reordered by dragging their headers, Base stays put
    var parentLabel = tableModel.parentLabel(column);
    var movable = column.number !== 0 && !this.phraseMode && parentLabel === '';
    var dragAttribute = movable ? ' draggable="true" data-movable="true"' : '';

    // The hint sits in a wrapper of its own because it speaks from the
    // server's reading of the cells, which lands after the header is drawn
    var hint = '<span class="table-column-hint" data-column="' + label + '">' +
        this.columnHintHtml(column) + '</span>';

    var out = '<th class="' + classes.join(' ') + '" data-column="' + label + '"' + dragAttribute + ' ' +
        'onclick="tableView.selectColumn(\'' + label + '\')"' + tooltip + '>' +
        label + subtitle + hint + '</th>';

    return out;
};

// A gentle indicator when the column can unfold into sub-rules, or fold
// back when it already is a sub-rule
tableView.columnHintHtml = function(column) {
    var label = tableModel.label(column);
    var parentLabel = tableModel.parentLabel(column);

    if (parentLabel !== '') {
        var out = '<span class="table-unfold-hint" onclick="tableView.foldColumn(event, \'' + parentLabel + '\')" ' +
            'data-tippy-content="Sub-rule of ' + parentLabel + ', a read-only view of one logical possibility. ' +
            'Click to fold the sub-rules back into one column.">' + shared.icon('chevrons-down-up', 10) + '</span>';
        return out;
    }

    var unfoldableRow = tableModel.unfoldableRow(column);
    if (unfoldableRow === null) { return ''; }

    var count = tableModel.reading(column, unfoldableRow.letter).items.length;
    var result = '<span class="table-unfold-hint" onclick="tableView.unfoldColumn(event, \'' + label + '\')" ' +
        'data-tippy-content="The ' + unfoldableRow.subject + ' cell holds ' + count + ' values. ' +
        'Click to unfold into sub-rules, one per value, so nothing stays bundled in one cell.">' +
        shared.icon('chevrons-up-down', 10) + count + '</span>';

    return result;
};

// ////////////////////////////////////////////////////////////////////////

tableView.filterRowsHtml = function(columnCount) {
    var html = '';

    var addFilterButton = '';
    if (!this.phraseMode && tableModel.table.filter === undefined) {
        addFilterButton = '<button class="button-mini" onclick="tableView.addFilter()">' +
            shared.icon('plus', 9) + ' Filter</button>';
    }

    html += '<tr class="table-section-row"><td colspan="' + (columnCount + 1) + '">Filter' +
        '<span class="table-section-hint">the filter narrows the data the whole table sees, ' +
        'before any rule column runs</span>' + addFilterButton + '</td></tr>';

    var filter = tableModel.table.filter;
    if (filter !== undefined) {
        var display = filter.subject + ' ' + filter.cell;
        if (this.phraseMode) {
            display = 'Only data where ' + tableModel.phraseFor(filter.subject) + ' ' + filter.cell + ' is considered';
        }
        var displayClass = this.phraseMode ? 'table-expression-phrase' : 'table-expression';

        var removeControl = this.phraseMode ? '' :
            '<span class="table-filter-remove" onclick="tableView.removeFilter(event)" ' +
            'data-tippy-content="Remove the filter">' + shared.icon('x', 11) + '</span>';

        html += '<tr class="table-filter-row"><td class="table-expression-column">' +
            '<span class="' + displayClass + '" onclick="tableView.editFilter(this)" ' +
            'data-tippy-content="The filter is not a rule, it fires no actions, it only narrows the data the table sees.">' +
            shared.escape(display) + '</span>' + removeControl + '</td>';

        html += '<td class="table-filter-span" colspan="' + columnCount + '">applies to every rule column</td></tr>';
    }

    return html;
};

// ////////////////////////////////////////////////////////////////////////

tableView.sectionRowHtml = function(columnCount, title, hint, kind) {
    var deleteButton = '';

    // The delete control appears right where the checkboxes are, not in a toolbar
    if (!this.phraseMode && kind !== '') {
        var checkedCount = tableModel.checkedCount(kind);
        if (checkedCount > 0) {
            deleteButton = '<button class="button-mini button-mini-danger" ' +
                'onclick="tableView.deleteCheckedRows(\'' + kind + '\')">Delete selected (' + checkedCount + ')</button>';
        }
    }

    var out = '<tr class="table-section-row"><td colspan="' + (columnCount + 1) + '">' + title +
        '<span class="table-section-hint">' + hint + '</span>' + deleteButton + '</td></tr>';

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The screen without a stored table yet
tableView.emptyHtml = function() {
    var out = '<div class="table-empty-note">There is no decision table yet. ' +
        '<button class="button-ghost" onclick="tableView.startNew()">New table</button></div>';
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The whole grid as html, out of the table document and one render context
tableView.gridHtml = function(context) {
    var self = this;

    var columnCount = tableModel.table.columns.length;
    var html = '<table class="table-grid">';

    // Column headers ..
    html += '<tr><th class="table-expression-column" style="background:var(--background);border:none"></th>';
    tableModel.table.columns.forEach(function(column) { html += self.columnHeadHtml(column, context); });
    html += '</tr>';

    // .. the filter row ..
    html += this.filterRowsHtml(columnCount);

    // .. condition rows, evaluated top to bottom because conditions short-circuit ..
    html += this.sectionRowHtml(columnCount, 'Conditions',
        'evaluated top to bottom, the first failing condition stops the rule', 'condition');
    tableModel.table.conditions.forEach(function(row) {
        var label = self.phraseMode
            ? '<span class="table-expression-phrase">If ' + shared.escape(tableModel.phraseFor(row.subject)) + ' is &hellip;</span>'
            : '<span class="table-expression">' + shared.escape(row.subject) + '</span>';

        html += '<tr class="table-condition-row" data-kind="condition" data-row="' + row.letter + '"><td class="table-expression-column">' +
            self.rowControls('condition', row.letter) + label + '</td>';

        tableModel.table.columns.forEach(function(column) {
            var columnLabel = tableModel.label(column);
            var coordinates = 'data-column="' + columnLabel + '" data-kind="condition" data-row-id="' + row.letter + '"';
            if (column.number === 0) {
                html += '<td class="table-cell table-cell-readonly" ' + coordinates + '>always</td>';
                return;
            }
            var raw = column.cells[row.letter];
            html += '<td class="' + self.cellClasses(column, raw, context, row.letter) + '" ' + coordinates + ' ' +
                'onclick="tableView.editCell(this, \'' + columnLabel + '\', \'' + row.letter + '\', \'condition\')">' +
                self.cellDisplay(raw) + '</td>';
        });
        html += '</tr>';
    });

    // .. action rows ..
    html += this.sectionRowHtml(columnCount, 'Actions',
        this.phraseMode ? '' : 'drag an attribute from the vocabulary to add a row', 'action');
    tableModel.table.actions.forEach(function(row) {
        var label = self.phraseMode
            ? '<span class="table-expression-phrase">Then set ' + shared.escape(tableModel.phraseFor(row.target)) + ' to &hellip;</span>'
            : '<span class="table-expression">' + shared.escape(row.target) + ' =</span>';

        html += '<tr class="table-action-row" data-kind="action" data-row="' + row.target + '"><td class="table-expression-column">' +
            self.rowControls('action', row.target) + label + '</td>';

        tableModel.table.columns.forEach(function(column) {
            var columnLabel = tableModel.label(column);
            var coordinates = 'data-column="' + columnLabel + '" data-kind="action" data-row-id="' + row.target + '"';
            var raw = tableModel.actionCell(column, row.target);
            html += '<td class="' + self.cellClasses(column, raw, context, row.target) + '" ' + coordinates + ' ' +
                'onclick="tableView.editCell(this, \'' + columnLabel + '\', \'' + row.target + '\', \'action\')">' +
                self.cellDisplay(raw) + '</td>';
        });
        html += '</tr>';
    });

    // .. the overrides row ..
    html += this.sectionRowHtml(columnCount, 'Overrides', '', '');
    html += '<tr><td class="table-expression-column">' +
        '<span class="' + (this.phraseMode ? 'table-expression-phrase' : 'table-expression') + '" style="color:var(--text4)">' +
        (this.phraseMode ? 'this rule wins over &hellip;' : 'overrides') + '</span></td>';
    tableModel.table.columns.forEach(function(column) {
        var columnLabel = tableModel.label(column);
        if (column.number === 0) {
            html += '<td class="table-override-cell" data-column="' + columnLabel + '"></td>';
            return;
        }
        var current = column.overrides.length === 0 ? '' : String(column.overrides[0]);
        var options = '<option value="">none</option>';
        tableModel.ruleColumns().forEach(function(other) {
            if (other.number === column.number) { return; }
            var selected = current === String(other.number) ? ' selected' : '';
            options += '<option value="' + other.number + '"' + selected + '>overrides rule ' + other.number + '</option>';
        });
        html += '<td class="table-override-cell" data-column="' + columnLabel + '">' +
            '<select class="' + (current !== '' ? 'table-has-override' : '') + '" ' +
            'data-tippy-content="When both rules match the same data, only this one wins. An override never reorders anything." ' +
            'onchange="tableView.setOverride(\'' + columnLabel + '\', this.value)">' + options + '</select></td>';
    });
    html += '</tr>';

    // .. and the decision messages row.
    html += this.sectionRowHtml(columnCount, 'Decision messages',
        'one plain sentence per rule, returned with every execution and shown in the decision log', '');
    html += '<tr><td class="table-expression-column">' +
        '<span class="table-expression" style="color:var(--text4)">message</span></td>';
    tableModel.table.columns.forEach(function(column) {
        var columnLabel = tableModel.label(column);
        html += '<td class="table-statement-cell" data-column="' + columnLabel + '"><div class="table-statement-wrap">' +
            '<span class="table-statement-dot table-severity-' + column.statement.severity + '" ' +
            'data-tippy-content="Severity: ' + column.statement.severity + '. Click to cycle info, warning, violation." ' +
            'onclick="tableView.cycleSeverity(\'' + columnLabel + '\')"></span>' +
            '<span class="table-statement-text" onclick="tableView.editStatement(this, \'' + columnLabel + '\')">' +
            self.statementHtml(column.statement.text) + '</span>' +
            '</div></td>';
    });
    html += '</tr>';

    html += '</table>';
    return html;
};

// ////////////////////////////////////////////////////////////////////////

})();
