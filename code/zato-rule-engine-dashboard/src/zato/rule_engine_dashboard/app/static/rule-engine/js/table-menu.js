'use strict';

// Right-click menus for the decision table, the same Excel-like loop as
// the rest of the grid: one menu for column headers and one for value
// cells. Augments the tableView namespace from table-render.js.

(function() {

// ////////////////////////////////////////////////////////////////////////

tableView.columnMenuItems = function(column) {
    var self = this;
    var label = tableModel.label(column);
    var parentLabel = tableModel.parentLabel(column);
    var items = [];

    items.push({label: 'Select column', destructive: false,
        description: 'Reads the whole rule as one sentence in the bar under the grid.',
        action: function() { self.selectColumn(label); }});

    // The Base column never moves, rule columns move one step at a time
    if (column.number !== 0) {
        items.push({label: 'Move left', destructive: false,
            description: 'One step to the left. Order is only visual, it never changes which rules fire.',
            action: function() { if (tableModel.moveColumnByOffset(label, -1)) { self.render(); } }});
        items.push({label: 'Move right', destructive: false,
            description: 'One step to the right. Order is only visual, it never changes which rules fire.',
            action: function() { if (tableModel.moveColumnByOffset(label, 1)) { self.render(); } }});
    }

    // Unfold or fold, only when the column supports it
    if (parentLabel !== '') {
        items.push({label: 'Fold sub-rules', destructive: false,
            description: 'Folds the sub-rules back into the one column they came from.',
            action: function() { self.foldColumn({stopPropagation: function() {}}, parentLabel); }});
    } else if (tableModel.unfoldableRow(column) !== null) {
        items.push({label: 'Unfold into sub-rules', destructive: false,
            description: 'One sub-rule per value, numbered ' + label + '.1, ' + label +
                '.2 and so on, so nothing stays bundled in one cell.',
            action: function() { self.unfoldColumn({stopPropagation: function() {}}, label); }});
    }

    items.push(null);
    items.push({label: 'Add rule column', destructive: false,
        description: 'A new rule column at the end of the table, every cell starting as any.',
        action: function() { self.addColumn(); }});

    return items;
};

// ////////////////////////////////////////////////////////////////////////

tableView.cellMenuItems = function(cell) {
    var self = this;
    var columnLabel = cell.getAttribute('data-column');
    var kind = cell.getAttribute('data-kind');
    var rowKey = cell.getAttribute('data-row-id');
    var column = tableModel.columnByLabel(columnLabel);
    var items = [];

    items.push({label: 'Edit value', destructive: false,
        description: 'Opens the value in place: pick lists for choices and yes/no values, free typing for the rest.',
        action: function() { cell.click(); }});

    if (kind === 'condition') {
        items.push({label: 'Set to any', destructive: false,
            description: 'The dash: this condition stops constraining the rule.',
            action: function() { column.cells[rowKey] = '-'; self.render(); }});
    }

    items.push({label: 'Copy value', destructive: false,
        description: 'The value exactly as the cell holds it.',
        action: function() {
            var raw = kind === 'condition' ? column.cells[rowKey] : tableModel.actionCell(column, rowKey);
            navigator.clipboard.writeText(raw);
        }});

    items.push(null);
    items.push({label: 'Move row up', destructive: false,
        description: 'One step up within its own section. Order is only visual.',
        action: function() { if (tableModel.moveRowByOffset(kind, rowKey, -1)) { self.render(); } }});
    items.push({label: 'Move row down', destructive: false,
        description: 'One step down within its own section. Order is only visual.',
        action: function() { if (tableModel.moveRowByOffset(kind, rowKey, 1)) { self.render(); } }});

    items.push(null);
    items.push({label: 'Delete row', destructive: true,
        description: 'Removes this row and its cell from every rule column.',
        action: function() { tableModel.deleteRow(kind, rowKey); self.render(); }});

    return items;
};

// ////////////////////////////////////////////////////////////////////////

tableView.attachContextMenu = function() {
    var self = this;
    var area = document.getElementById('table-grid-area');

    area.addEventListener('contextmenu', function(event) {
        // Column headers get the column menu ..
        var header = event.target.closest('th.table-column-head');
        if (header !== null) {
            event.preventDefault();
            var column = tableModel.columnByLabel(header.getAttribute('data-column'));
            var title = column.number === 0 ? 'Base column' : 'Rule ' + tableModel.label(column);
            shared.openContextMenu(title, self.columnMenuItems(column), event.clientX, event.clientY);
            return;
        }

        // .. value cells get the cell menu, everything else keeps the
        // browser's own menu.
        var cell = event.target.closest('td.table-cell');
        if (cell !== null && !cell.classList.contains('table-cell-readonly')) {
            event.preventDefault();
            var kind = cell.getAttribute('data-kind');
            var rowKey = cell.getAttribute('data-row-id');
            var titlePath = kind === 'condition' ? tableModel.conditionRow(rowKey).subject : rowKey;
            shared.openContextMenu(titlePath, self.cellMenuItems(cell), event.clientX, event.clientY);
        }
    });
};

// The grid area itself survives re-renders, so one delegate is enough
tableView.attachContextMenu();

})();
