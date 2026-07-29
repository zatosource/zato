'use strict';

(function() {

var tableView = {

    phraseMode: false,
    selectedColumn: null,
    editing: false,
    columnWidths: {},
    checkTimer: null,

// ////////////////////////////////////////////////////////////////////////

    attachColumnResizers: function() {
        var self = this;
        document.querySelectorAll('th.table-column-head').forEach(function(cell) {
            shared.attachColumnResize(cell, cell.getAttribute('data-column'), self.columnWidths);
        });
    },

// ////////////////////////////////////////////////////////////////////////

    findTerm: function() {
        var out = document.getElementById('find-input').value.trim();
        return out;
    },

    renderContext: function() {
        var invalid = {};
        tableModel.invalidCells().forEach(function(cell) { invalid[cell.column + '|' + cell.row] = true; });

        var out = {
            invalid: invalid,
            conflictLabels: tableModel.conflictLabels(),
            findTerm: this.findTerm(),
        };
        return out;
    },

    renderReadings: function() {
        var self = this;

        document.querySelectorAll('#table-grid-area .table-column-hint').forEach(function(wrapper) {
            var column = tableModel.columnByLabel(wrapper.getAttribute('data-column'));
            wrapper.innerHTML = self.columnHintHtml(column);
        });

        this.renderSentence();
        this.updateUnfoldAllButton();
    },

// ////////////////////////////////////////////////////////////////////////

    render: function() {
        if (tableModel.table === null) {
            document.getElementById('table-grid-area').innerHTML = this.emptyHtml();
            return;
        }

        document.getElementById('table-grid-area').innerHTML = this.gridHtml(this.renderContext());

        this.attachColumnHover();
        this.attachDropTargets();
        this.attachColumnDrag();
        this.attachColumnResizers();
        this.renderSubtitle();
        this.renderProblems();
        this.renderVocabulary();
        this.renderSentence();
        this.updateUnfoldAllButton();
        this.applyCursor();
        shared.initTips();
        this.scheduleServerCheck();
    },

// ////////////////////////////////////////////////////////////////////////

    scheduleServerCheck: function() {
        var self = this;

        if (this.checkTimer !== null) { clearTimeout(this.checkTimer); }
        this.checkTimer = setTimeout(function() {
            self.checkTimer = null;

            if (tableModel.hasUnfolded()) { return; }

            tableModel.check(function() {
                self.renderProblems();
                self.shadeInvalidCells();
                self.renderReadings();
                shared.initTips();
            }, data.reportError);
        }, tableModel.config.checkDelayMilliseconds);
    },

    shadeInvalidCells: function() {
        var invalidList = tableModel.invalidCells();

        document.querySelectorAll('td.table-cell').forEach(function(cell) {
            var column = cell.getAttribute('data-column');
            var row = cell.getAttribute('data-row-id');
            var isInvalid = invalidList.some(function(entry) { return entry.column === column && entry.row === row; });
            cell.classList.toggle('table-cell-invalid', isInvalid);
        });
    },

// ////////////////////////////////////////////////////////////////////////

    renderSubtitle: function() {
        var subtitle = document.getElementById('main-subtitle');
        var text = shared.escape(tableModel.table.name);

        if (tableModel.definitionId === null) {
            text += ' &#183; not saved yet';
        } else {
            text += ' &#183; version ' + tableModel.currentVersion;
        }
        subtitle.innerHTML = text;
    },

// ////////////////////////////////////////////////////////////////////////

    renderProblems: function() {
        var problems = tableModel.buildProblems();
        var head = document.getElementById('problems-head');
        var list = document.getElementById('problems-list');
        head.textContent = 'Problems (' + problems.length + ')';

        if (problems.length === 0) {
            list.innerHTML = '<div class="problem-item problem-none">No problems in this table.</div>';
            return;
        }

        list.innerHTML = problems.map(function(problem) {
            var dots = {error: 'status-dot-error', warning: 'status-dot-warning', information: 'status-dot-information'};
            return '<div class="problem-item" onclick="tableView.flashColumn(\'' + problem.column + '\')">' +
                '<span class="status-dot ' + dots[problem.severity] + '"></span><span>' + shared.escape(problem.text) + '</span>' +
                '<span class="problem-where">' + problem.column + '</span></div>';
        }).join('');
    },

// ////////////////////////////////////////////////////////////////////////

    renderVocabulary: function() {
        var used = tableModel.usedPaths();
        var html = '';

        vocabulary.entities.forEach(function(entity) {
            html += '<div class="vocabulary-entity">' + shared.escape(entity.name) + '</div>';
            vocabulary.pickerAttributes(entity).forEach(function(attribute) {
                var path = entity.name + '.' + attribute.name;
                var isUsed = used.indexOf(path) > -1;
                html += '<div class="vocabulary-item' + (isUsed ? ' vocabulary-item-used' : '') +
                    '" draggable="' + (isUsed ? 'false' : 'true') + '" ' +
                    'data-path="' + path + '">' + shared.escape(attribute.name) +
                    '<span class="vocabulary-item-type">' + shared.escape(attribute.type) + '</span></div>';
            });
        });

        document.getElementById('vocabulary-list').innerHTML = html;
        this.attachVocabularyDrag();
    },

// ////////////////////////////////////////////////////////////////////////

    attachColumnHover: function() {
        var self = this;
        document.querySelectorAll('[data-column]').forEach(function(element) {
            element.addEventListener('mouseenter', function() { self.setColumnHover(element.getAttribute('data-column'), true); });
            element.addEventListener('mouseleave', function() { self.setColumnHover(element.getAttribute('data-column'), false); });
        });
    },

    setColumnHover: function(label, isOn) {
        document.querySelectorAll('[data-column="' + label + '"]').forEach(function(element) {
            if (element.classList.contains('table-cell-readonly')) { return; }
            element.classList.toggle('table-column-hover', isOn);
        });
    },

    flashColumn: function(label) {
        var cells = document.querySelectorAll('[data-column="' + label + '"]');
        if (cells.length > 0) { cells[0].scrollIntoView({behavior: 'smooth', block: 'nearest', inline: 'nearest'}); }

        cells.forEach(function(cell) {
            cell.classList.remove('table-flash');
            void cell.offsetWidth;
            cell.classList.add('table-flash');
            cell.addEventListener('animationend', function handler() {
                cell.classList.remove('table-flash');
                cell.removeEventListener('animationend', handler);
            });
        });
    },
};

window.tableView = tableView;

})();
