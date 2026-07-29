'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

tableView.columnMenuItems = function(column) {
    var self = this;
    var label = tableModel.label(column);
    var parentLabel = tableModel.parentLabel(column);
    var items = [];

    items.push({label: 'Select column', destructive: false,
        action: function() { self.selectColumn(label); }});

    if (column.number !== 0) {
        items.push({label: 'Move left', destructive: false,
            action: function() { if (tableModel.moveColumnByOffset(label, -1)) { self.render(); } }});
        items.push({label: 'Move right', destructive: false,
            action: function() { if (tableModel.moveColumnByOffset(label, 1)) { self.render(); } }});
    }

    if (parentLabel !== '') {
        items.push({label: 'Fold sub-rules', destructive: false,
            action: function() { self.foldColumn({stopPropagation: function() {}}, parentLabel); }});
    } else if (tableModel.unfoldableRow(column) !== null) {
        items.push({label: 'Unfold into sub-rules', destructive: false,
            action: function() { self.unfoldColumn({stopPropagation: function() {}}, label); }});
    }

    items.push(null);
    items.push({label: 'Add rule column', destructive: false,
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
        action: function() { cell.click(); }});

    if (kind === 'condition') {
        items.push({label: 'Set to any', destructive: false,
            action: function() { column.cells[rowKey] = '-'; self.render(); }});
    }

    items.push({label: 'Copy value', destructive: false,
        action: function() {
            var raw = kind === 'condition' ? column.cells[rowKey] : tableModel.actionCell(column, rowKey);
            navigator.clipboard.writeText(raw);
        }});

    items.push(null);
    items.push({label: 'Move row up', destructive: false,
        action: function() { if (tableModel.moveRowByOffset(kind, rowKey, -1)) { self.render(); } }});
    items.push({label: 'Move row down', destructive: false,
        action: function() { if (tableModel.moveRowByOffset(kind, rowKey, 1)) { self.render(); } }});

    items.push(null);
    items.push({label: 'Delete row', destructive: true,
        action: function() { tableModel.deleteRow(kind, rowKey); self.render(); }});

    return items;
};

// ////////////////////////////////////////////////////////////////////////

tableView.attachContextMenu = function() {
    var self = this;
    var area = document.getElementById('table-grid-area');

    area.addEventListener('contextmenu', function(event) {
        var header = event.target.closest('th.table-column-head');
        if (header !== null) {
            event.preventDefault();
            var column = tableModel.columnByLabel(header.getAttribute('data-column'));
            var title = column.number === 0 ? 'Base column' : 'Rule ' + tableModel.label(column);
            shared.openContextMenu(title, self.columnMenuItems(column), event.clientX, event.clientY);
            return;
        }

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

tableView.attachContextMenu();

})();
