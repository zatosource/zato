'use strict';

// Rendering for the decision table editor: the grid itself, the problems
// panel, the vocabulary pane and the sentence bar. Event handlers live
// in table-actions.js, which augments the same namespace.

(function() {

var tableView = {

    // UI state
    phraseMode: false,
    selectedColumn: null,
    editing: false,
    columnWidths: {},    // dragged column widths, keyed by column label
    checkTimer: null,    // the debounce behind the server validation

// ////////////////////////////////////////////////////////////////////////

    // A grip on every rule column header resizes that column, the widths
    // survive re-renders
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

    cellDisplay: function(raw) {
        var value = raw.trim();
        if (value === '' || value === '-') { return '<span class="table-any-dash">-</span>'; }
        return shared.escape(value);
    },

    statementHtml: function(text) {
        var out = shared.escape(text).replace(/\{[a-zA-Z._]+\}/g, function(match) {
            return '<span class="table-statement-placeholder">' + match + '</span>';
        });
        return out;
    },

    cellClasses: function(column, raw, invalidList, rowKey) {
        var label = tableModel.label(column);
        var classes = ['table-cell'];

        var isInvalid = invalidList.some(function(cell) { return cell.column === label && cell.row === rowKey; });
        if (isInvalid) { classes.push('table-cell-invalid'); }
        if (tableModel.generatedNumbers[label] === true) { classes.push('table-cell-generated'); }
        if (tableModel.conflictLabels().indexOf(label) > -1) { classes.push('table-cell-conflict'); }
        if (this.selectedColumn === label) { classes.push('table-column-selected'); }

        var term = this.findTerm();
        if (term !== '' && raw.indexOf(term) > -1) { classes.push('table-find-hit'); }

        var out = classes.join(' ');
        return out;
    },

    // Checkbox and drag handle in front of a row, hidden in the phrase view
    rowControls: function(kind, rowKey) {
        if (this.phraseMode) { return ''; }

        var checked = tableModel.checked[kind][rowKey] === true ? ' checked' : '';
        var out = '<input type="checkbox" class="table-row-checkbox"' + checked +
            ' onchange="tableView.toggleRowCheck(\'' + kind + '\', \'' + rowKey + '\', this.checked)">' +
            '<span class="table-drag-handle" draggable="true" data-kind="' + kind + '" data-row="' + rowKey + '" ' +
            'data-tippy-content="Drag to reorder this row">' + shared.icon('grip-vertical', 11) + '</span>';

        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    columnHeadHtml: function(column) {
        var label = tableModel.label(column);
        var classes = ['table-column-head'];
        if (column.number === 0) { classes.push('table-column-zero'); }
        if (tableModel.conflictLabels().indexOf(label) > -1) { classes.push('table-cell-conflict'); }
        if (this.selectedColumn === label) { classes.push('table-column-selected'); }

        var subtitle = '';
        var tooltip = '';
        if (column.number === 0) {
            subtitle = '<span class="table-column-subtitle">always, fires first</span>';
            tooltip = ' data-tippy-content="The Base column has actions only. It always fires and it fires first."';
        }

        // A gentle indicator when the column can unfold into sub-rules,
        // or fold back when it already is a sub-rule.
        var hint = '';
        var parentLabel = tableModel.parentLabel(column);
        if (parentLabel !== '') {
            hint = '<span class="table-unfold-hint" onclick="tableView.foldColumn(event, \'' + parentLabel + '\')" ' +
                'data-tippy-content="Sub-rule of ' + parentLabel + ', a read-only view of one logical possibility. ' +
                'Click to fold the sub-rules back into one column.">' + shared.icon('chevrons-down-up', 10) + '</span>';
        } else {
            var unfoldableRow = tableModel.unfoldableRow(column);
            if (unfoldableRow !== null) {
                var parsed = tableModel.parseCondition(column, unfoldableRow.letter);
                hint = '<span class="table-unfold-hint" onclick="tableView.unfoldColumn(event, \'' + label + '\')" ' +
                    'data-tippy-content="The ' + unfoldableRow.subject + ' cell holds ' + parsed.items.length + ' values. ' +
                    'Click to unfold into sub-rules, one per value, so nothing stays bundled in one cell.">' +
                    shared.icon('chevrons-up-down', 10) + parsed.items.length + '</span>';
            }
        }

        // Rule columns can be reordered by dragging their headers, Base stays put
        var movable = column.number !== 0 && !this.phraseMode && parentLabel === '';
        var dragAttribute = movable ? ' draggable="true" data-movable="true"' : '';

        var out = '<th class="' + classes.join(' ') + '" data-column="' + label + '"' + dragAttribute + ' ' +
            'onclick="tableView.selectColumn(\'' + label + '\')"' + tooltip + '>' +
            label + subtitle + hint + '</th>';

        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    filterRowsHtml: function(columnCount) {
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
    },

// ////////////////////////////////////////////////////////////////////////

    sectionRowHtml: function(columnCount, title, hint, kind) {
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
    },

// ////////////////////////////////////////////////////////////////////////

    // The screen without a stored table yet
    emptyHtml: function() {
        var out = '<div class="table-empty-note">There is no decision table yet. ' +
            '<button class="button-ghost" onclick="tableView.startNew()">New table</button></div>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    render: function() {
        var self = this;

        if (tableModel.table === null) {
            document.getElementById('table-grid-area').innerHTML = this.emptyHtml();
            return;
        }

        var invalidList = tableModel.invalidCells();
        var columnCount = tableModel.table.columns.length;
        var html = '<table class="table-grid">';

        // Column headers ..
        html += '<tr><th class="table-expression-column" style="background:var(--background);border:none"></th>';
        tableModel.table.columns.forEach(function(column) { html += self.columnHeadHtml(column); });
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
                html += '<td class="' + self.cellClasses(column, raw, invalidList, row.letter) + '" ' + coordinates + ' ' +
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
                html += '<td class="' + self.cellClasses(column, raw, invalidList, row.target) + '" ' + coordinates + ' ' +
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
        document.getElementById('table-grid-area').innerHTML = html;

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

    // Every edit re-runs the server validation after a short pause: the
    // structural errors land in the problems panel and the invalid cells
    // shade red in the grid
    scheduleServerCheck: function() {
        var self = this;

        if (this.checkTimer !== null) { clearTimeout(this.checkTimer); }
        this.checkTimer = setTimeout(function() {
            self.checkTimer = null;

            // An unfolded table is a read-only view with dotted numbers
            // the validator does not know, the fold restores checking
            if (tableModel.hasUnfolded()) { return; }

            tableModel.check(function() {
                self.renderProblems();
                self.shadeInvalidCells();
            });
        }, tableModel.config.checkDelayMilliseconds);
    },

    // Re-shade the invalid cells in place, without a full re-render
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
            list.innerHTML = '<div class="problem-item problem-none">No problems. Conflicts, completeness, coverage ' +
                'and reachability are checked on demand from the toolbar, the cell syntax continuously.</div>';
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

    formatIntervalPhrase: function(parsed) {
        if (parsed.low === parsed.high) { return String(parsed.low); }
        var out = 'between ' + parsed.low.toLocaleString('en-US') + ' and ' + parsed.high.toLocaleString('en-US');
        return out;
    },

    actionPhrases: function(column) {
        var out = [];
        tableModel.table.actions.forEach(function(row) {
            var raw = tableModel.actionCell(column, row.target).trim();
            if (raw === '') { return; }
            out.push('set ' + shared.escape(tableModel.phraseFor(row.target)) + ' to ' + shared.escape(raw));
        });

        return out;
    },

    conditionPhrase: function(subject, parsed) {
        var phrase = shared.escape(tableModel.phraseFor(subject));

        if (parsed.kind === 'interval') { return phrase + ' is ' + this.formatIntervalPhrase(parsed); }
        if (parsed.kind === 'set') {
            var joined = shared.escape(parsed.items.join(', '));
            if (parsed.negated) { return phrase + ' is none of ' + joined; }
            if (parsed.items.length === 1) { return phrase + ' is ' + joined; }
            return phrase + ' is one of ' + joined;
        }
        if (parsed.kind === 'comparison') {
            return phrase + ' ' + tableModel.symbolPhrases[parsed.symbol] + ' ' + shared.escape(parsed.value);
        }

        var out = phrase + ' is ' + shared.escape(parsed.value);
        return out;
    },

    composeSentence: function(column) {
        var self = this;
        var keyword = function(text) { return '<span class="table-sentence-keyword">' + text + '</span>'; };

        if (column.number === 0) {
            var alwaysActions = this.actionPhrases(column);
            return keyword('Always') + ' ' + alwaysActions.join(' ' + keyword('and') + ' ') + '.';
        }

        var parts = [];
        tableModel.table.conditions.forEach(function(row) {
            var parsed = tableModel.parseCondition(column, row.letter);
            if (parsed.kind === 'any') { return; }
            parts.push(self.conditionPhrase(row.subject, parsed));
        });

        var actions = this.actionPhrases(column);
        var conditionPart = parts.length === 0 ? keyword('If') + ' anything matches' :
            keyword('If') + ' ' + parts.join(' ' + keyword('and') + ' ');
        var actionPart = actions.length === 0 ? 'do nothing yet, the actions are empty' :
            actions.join(' ' + keyword('and') + ' ');

        var out = conditionPart + ' ' + keyword('then') + ' ' + actionPart + '.';
        if (column.overrides.length > 0) {
            out += ' ' + keyword('This rule overrides rule ' + column.overrides[0] + '.');
        }

        return out;
    },

    renderSentence: function() {
        var bar = document.getElementById('table-sentence-bar');
        var column = this.selectedColumn === null ? undefined : tableModel.columnByLabel(this.selectedColumn);

        if (column === undefined) {
            bar.innerHTML = '<span class="table-sentence-tag">Rule reads</span>' +
                '<span class="table-sentence-text" style="color:var(--text4)">Click a column header to read the whole rule as a sentence.</span>';
            return;
        }

        var tag = column.number === 0 ? 'The Base rule reads' : 'Rule ' + shared.escape(this.selectedColumn) + ' reads';
        bar.innerHTML = '<span class="table-sentence-tag">' + tag + '</span>' +
            '<span class="table-sentence-text">' + this.composeSentence(column) + '</span>';
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
