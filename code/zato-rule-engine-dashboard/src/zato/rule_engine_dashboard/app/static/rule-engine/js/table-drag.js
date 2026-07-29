'use strict';

(function() {

tableView.dragState = null;

// ////////////////////////////////////////////////////////////////////////

tableView.clearDropMarks = function() {
    var marks = ['table-drop-target', 'table-drop-above',
        'table-row-dragging', 'table-column-dragging'];
    marks.forEach(function(mark) {
        document.querySelectorAll('.' + mark).forEach(function(element) { element.classList.remove(mark); });
    });
    shared.removeDropPlaceholder();
};

// ////////////////////////////////////////////////////////////////////////

tableView.attachVocabularyDrag = function() {
    var self = this;
    document.querySelectorAll('.vocabulary-item[draggable="true"]').forEach(function(element) {
        element.addEventListener('dragstart', function(event) {
            var path = element.getAttribute('data-path');
            self.dragState = {type: 'vocabulary', path: path};

            var ghost = shared.makeGhost([path], false);
            event.dataTransfer.setDragImage(ghost, 16, 12);
            event.dataTransfer.setData('text/plain', 'vocabulary');
        });
        element.addEventListener('dragend', function() {
            self.dragState = null;
            self.clearDropMarks();
            shared.removeGhost();
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

tableView.startRowDrag = function(handle, event) {
    var kind = handle.getAttribute('data-kind');
    var rowKey = handle.getAttribute('data-row');
    this.dragState = {type: 'row', kind: kind, key: rowKey};

    var expression = kind === 'condition' ? tableModel.conditionRow(rowKey).subject : rowKey;

    var cellTexts = [expression];
    tableModel.table.columns.forEach(function(column) {
        if (kind === 'condition') {
            cellTexts.push(column.number === 0 ? 'always' : column.cells[rowKey]);
        } else {
            cellTexts.push(tableModel.actionCell(column, rowKey));
        }
    });

    var ghost = shared.makeGhost(cellTexts, false);
    event.dataTransfer.setDragImage(ghost, 20, 14);
    event.dataTransfer.setData('text/plain', 'row');

    handle.closest('tr').classList.add('table-row-dragging');
};

tableView.attachDropTargets = function() {
    if (this.phraseMode) { return; }

    var self = this;
    this.wireDropGroup(document.querySelectorAll('.table-condition-row'), 'condition');
    this.wireDropGroup(document.querySelectorAll('.table-action-row'), 'action');

    document.querySelectorAll('.table-drag-handle').forEach(function(handle) {
        handle.addEventListener('dragstart', function(event) { self.startRowDrag(handle, event); });
        handle.addEventListener('dragend', function() {
            self.dragState = null;
            self.clearDropMarks();
            shared.removeGhost();
        });
    });
};

tableView.wireDropGroup = function(tableRows, kind) {
    var self = this;

    tableRows.forEach(function(tableRow) {
        tableRow.addEventListener('dragover', function(event) {
            if (self.dragState === null) { return; }
            if (self.dragState.type === 'column') { return; }
            if (self.dragState.type === 'row' && self.dragState.kind !== kind) { return; }
            event.preventDefault();
            self.clearDropMarks();

            if (self.dragState.type === 'vocabulary') {
                tableRows.forEach(function(target) { target.classList.add('table-drop-target'); });
            } else {
                tableRow.classList.add('table-drop-above');
                var rectangle = tableRow.getBoundingClientRect();
                var thickness = shared.config.dropPlaceholderThickness;
                shared.showDropPlaceholder(rectangle.left, rectangle.top - thickness / 2, rectangle.width, thickness);
            }
        });

        tableRow.addEventListener('drop', function(event) {
            event.preventDefault();
            self.clearDropMarks();
            if (self.dragState === null) { return; }

            if (self.dragState.type === 'vocabulary') {
                var newRowKey = tableModel.addRowFromVocabulary(self.dragState.path, kind);
                self.render();
                var kindText = kind === 'condition' ? 'A condition' : 'An action';
                var startText = kind === 'condition' ? ' Every rule starts with any (-).' : '';
                shared.popover(document.querySelector('tr[data-kind="' + kind + '"][data-row="' + newRowKey + '"] .table-expression-column'),
                    kindText + ' row was added for ' + self.dragState.path + '.' + startText);
            } else if (self.dragState.kind === kind) {
                if (self.dragState.key !== tableRow.getAttribute('data-row')) {
                    tableModel.moveRow(kind, self.dragState.key, tableRow.getAttribute('data-row'));
                    self.render();
                }
            }
            self.dragState = null;
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

tableView.startColumnDrag = function(header, event) {
    var label = header.getAttribute('data-column');
    this.dragState = {type: 'column', label: label};

    var column = tableModel.columnByLabel(label);
    var cellTexts = [label];
    tableModel.table.conditions.forEach(function(row) { cellTexts.push(column.cells[row.letter]); });
    tableModel.table.actions.forEach(function(row) { cellTexts.push(tableModel.actionCell(column, row.target)); });

    var ghost = shared.makeGhost(cellTexts, true);
    event.dataTransfer.setDragImage(ghost, 30, 14);
    event.dataTransfer.setData('text/plain', 'column');

    document.querySelectorAll('[data-column="' + label + '"]').forEach(function(element) {
        element.classList.add('table-column-dragging');
    });
};

tableView.attachColumnDrag = function() {
    var self = this;

    document.querySelectorAll('th[data-movable="true"]').forEach(function(header) {
        header.addEventListener('dragstart', function(event) { self.startColumnDrag(header, event); });
        header.addEventListener('dragend', function() {
            self.dragState = null;
            self.clearDropMarks();
            shared.removeGhost();
        });

        header.addEventListener('dragover', function(event) {
            if (self.dragState === null) { return; }
            if (self.dragState.type !== 'column') { return; }
            event.preventDefault();
            self.clearDropMarks();

            var targetLabel = header.getAttribute('data-column');
            var top = null;
            var bottom = null;
            document.querySelectorAll('[data-column="' + targetLabel + '"]').forEach(function(element) {
                var rectangle = element.getBoundingClientRect();
                if (top === null || rectangle.top < top) { top = rectangle.top; }
                if (bottom === null || rectangle.bottom > bottom) { bottom = rectangle.bottom; }
            });
            var headerRectangle = header.getBoundingClientRect();
            var thickness = shared.config.dropPlaceholderThickness;
            shared.showDropPlaceholder(headerRectangle.left - thickness / 2, top, thickness, bottom - top);
        });

        header.addEventListener('drop', function(event) {
            event.preventDefault();
            self.clearDropMarks();
            if (self.dragState === null) { return; }
            if (self.dragState.type !== 'column') { return; }

            var targetLabel = header.getAttribute('data-column');
            if (self.dragState.label !== targetLabel) {
                tableModel.moveColumn(self.dragState.label, targetLabel);
                self.render();
            }
            self.dragState = null;
        });
    });
};

})();
