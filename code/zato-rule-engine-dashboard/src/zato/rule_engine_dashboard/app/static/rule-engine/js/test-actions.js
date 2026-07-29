'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

testView.selectedScenario = function() {
    var out = testModel.scenarioAt(this.selectedIndex);
    return out;
};

testView.selectScenario = function(index) {
    this.selectedIndex = index;
    this.cursor = null;
    this.render();
};

testView.startNew = function() {
    testModel.startNew();
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

testView.showView = function(viewName) {
    this.view = viewName;
    var isScenarios = viewName === 'scenarios';

    document.getElementById('test-scenarios-view').style.display = isScenarios ? 'flex' : 'none';
    document.getElementById('test-ab-view').style.display = isScenarios ? 'none' : 'block';
    document.getElementById('button-view-scenarios').classList.toggle('toggled', isScenarios);
    document.getElementById('button-view-ab').classList.toggle('toggled', !isScenarios);

    if (!isScenarios) { this.renderAb(); shared.initTips(); }
};

// ////////////////////////////////////////////////////////////////////////

testView.runAll = function(button) {
    var self = this;

    var handlers = shared.inFlight(button, function(delta) {
        self.lastDelta = delta;
        self.render();

        var counts = delta.counts;
        var text = 'Ran ' + testModel.suite.scenarios.length + ' scenarios: ' + counts.passed + ' passed, ' +
            counts.failed + ' failed, ' + counts.explored + ' explored with no expectations yet.';
        if (delta.newFailures.length > 0) {
            text += ' New failure: ' + delta.newFailures.join(', ') + '.';
            shared.popover(button, text, 'red');
            return;
        }
        shared.popover(button, text, 'green');
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    testModel.runAll(handlers.done, handlers.error);
};

testView.runOne = function(button) {
    var self = this;
    var scenario = this.selectedScenario();

    var handlers = shared.inFlight(button, function(entry) {
        shared.popover(button, 'Ran "' + scenario.name + '", ' + self.statusLabels[entry.status] + '.');
        self.render();
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    testModel.runOne(scenario, handlers.done, handlers.error);
};

testView.runFromList = function(event, index, button) {
    event.stopPropagation();
    var self = this;
    var scenario = testModel.scenarioAt(index);

    var handlers = shared.inFlight(button, function(entry) {
        shared.popover(button, 'Ran "' + scenario.name + '", ' + self.statusLabels[entry.status] + '.');
        self.render();
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    testModel.runOne(scenario, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

testView.addScenario = function() {
    if (testModel.suite === null) { testModel.startNew(); }

    testModel.addScenario();
    this.selectScenario(testModel.suite.scenarios.length - 1);
};

// ////////////////////////////////////////////////////////////////////////

testView.defaultValue = function(term) {
    if (term === null) { return ''; }
    if (term.type === 'choice') { return term.values[0]; }
    if (term.type === 'yes/no') { return true; }
    if (term.type === 'number range') { return term.domain.low; }
    return 0;
};

testView.addInput = function(path) {
    var scenario = this.selectedScenario();
    testModel.setInput(scenario, path, this.defaultValue(testModel.termFor(path)));
    testModel.modified = true;
    this.render();

    var cell = document.querySelector('[data-cell="input"][data-path="' + path + '"]');
    this.editInput(cell, path);
};

testView.pickVocabulary = function(path) {
    if (this.selectedScenario() === undefined) { this.addScenario(); }
    this.addInput(path);
};

testView.removeInput = function(event, path) {
    event.stopPropagation();
    var scenario = this.selectedScenario();
    testModel.removeInput(scenario, path);
    testModel.modified = true;
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

testView.wireEditor = function(element, commit) {
    var self = this;
    this.editing = true;

    var committed = false;
    var commitOnce = function() {
        if (committed) { return; }
        committed = true;
        commit(element.value);
    };

    element.onkeydown = function(keyEvent) {
        if (keyEvent.key === 'Enter') { commitOnce(); }
        if (keyEvent.key === 'Escape') { committed = true; self.editing = false; self.render(); }
    };
    element.onblur = commitOnce;
};

testView.buildEditor = function(cell, term, currentText, allowNone) {
    var element;
    var isClosed = term !== null && (term.type === 'choice' || term.type === 'yes/no');

    if (isClosed) {
        element = document.createElement('select');
        var choices = term.type === 'yes/no' ? ['true', 'false'] : term.values;
        if (allowNone) { choices = ['none'].concat(choices); }

        choices.forEach(function(choice) {
            var option = document.createElement('option');
            option.value = choice;
            option.textContent = choice;
            option.selected = choice === currentText;
            element.appendChild(option);
        });
    } else {
        element = document.createElement('input');
        element.type = 'text';
        element.value = currentText;
    }

    cell.classList.add('cell-editing');
    cell.textContent = '';
    cell.appendChild(element);
    element.focus();
    if (element.tagName === 'INPUT') { element.select(); }

    return element;
};

testView.editInput = function(cell, path) {
    if (this.editing) { return; }
    var self = this;
    var scenario = this.selectedScenario();
    var term = testModel.termFor(path);
    var flat = testModel.flatten(scenario.input);

    var element = this.buildEditor(cell, term, testModel.displayValue(flat[path]), false);
    this.wireEditor(element, function(value) {
        self.editing = false;
        testModel.setInput(scenario, path, testModel.typedValue(path, value.trim()));
        testModel.modified = true;
        self.render();
    });
};

testView.editExpected = function(cell, path) {
    if (this.editing) { return; }
    var self = this;
    var scenario = this.selectedScenario();
    var term = testModel.termFor(path);

    var current = scenario.expected[path];
    var currentText = current === undefined ? 'none' : testModel.displayValue(current);

    var element = this.buildEditor(cell, term, currentText, true);
    this.wireEditor(element, function(value) {
        self.editing = false;
        var trimmed = value.trim();

        if (trimmed === '' || trimmed === 'none') {
            delete scenario.expected[path];
        } else {
            scenario.expected[path] = testModel.typedValue(path, trimmed);
        }
        testModel.modified = true;
        self.render();
    });
};

testView.editName = function(span) {
    if (this.editing) { return; }
    var self = this;
    var scenario = this.selectedScenario();
    this.editing = true;

    span.outerHTML = '<input type="text" id="scenario-name-input" class="test-name-input" value="' +
        shared.escape(scenario.name) + '">';
    var input = document.getElementById('scenario-name-input');
    input.focus();
    input.select();

    this.wireEditor(input, function(value) {
        self.editing = false;
        var trimmed = value.trim();
        if (trimmed !== '' && trimmed !== scenario.name) {
            delete testModel.results[scenario.name];
            scenario.name = trimmed;
            testModel.modified = true;
        }
        self.render();
    });
};

// ////////////////////////////////////////////////////////////////////////

testView.promote = function(button) {
    var self = this;
    var scenario = this.selectedScenario();

    var handlers = shared.inFlight(button, function() {
        testModel.runOne(scenario, function() {
            self.render();
            self.renderSubtitle();
        }, data.reportError);
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    testModel.promote(scenario, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

testView.save = function(button) {
    if (testModel.suite === null) { return; }
    var self = this;

    var handlers = shared.inFlight(button, function(payload) {
        self.renderSubtitle();
        shared.popover(button, 'Saved as version ' + payload.version + '.', 'green');
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    testModel.save(handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

testView.dragState = null;

testView.attachVocabularyDrag = function() {
    var self = this;

    document.querySelectorAll('.vocabulary-item[draggable="true"]').forEach(function(element) {
        element.addEventListener('dragstart', function(event) {
            var path = element.getAttribute('data-path');
            self.dragState = {path: path};

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

testView.clearDropMarks = function() {
    document.querySelectorAll('.test-drop-target').forEach(function(element) {
        element.classList.remove('test-drop-target');
    });
};

testView.attachDropTargets = function() {
    var self = this;
    var grid = document.getElementById('test-input-grid');
    if (grid === null) { return; }

    grid.addEventListener('dragover', function(event) {
        if (self.dragState === null) { return; }
        event.preventDefault();
        grid.classList.add('test-drop-target');
    });

    grid.addEventListener('dragleave', function() {
        grid.classList.remove('test-drop-target');
    });

    grid.addEventListener('drop', function(event) {
        event.preventDefault();
        self.clearDropMarks();
        if (self.dragState === null) { return; }

        self.addInput(self.dragState.path);
        self.dragState = null;
    });
};

// ////////////////////////////////////////////////////////////////////////

testView.cursorRows = function() {
    var out = [];
    document.querySelectorAll('#test-detail-pane tr').forEach(function(tableRow) {
        var cells = tableRow.querySelectorAll('[data-cell]');
        if (cells.length > 0) { out.push(Array.prototype.slice.call(cells)); }
    });
    return out;
};

testView.applyCursor = function() {
    document.querySelectorAll('.test-cell-cursor').forEach(function(element) {
        element.classList.remove('test-cell-cursor');
    });
    if (this.cursor === null) { return; }

    var rows = this.cursorRows();
    var row = rows[this.cursor.row];
    if (row === undefined) { this.cursor = null; return; }

    var cell = row[Math.min(this.cursor.column, row.length - 1)];
    cell.classList.add('test-cell-cursor');
    cell.scrollIntoView({behavior: 'smooth', block: 'nearest'});
};

testView.moveCursor = function(key) {
    var rows = this.cursorRows();
    if (rows.length === 0) { return; }

    if (this.cursor === null) { this.cursor = {row: 0, column: 0}; this.applyCursor(); return; }

    var row = this.cursor.row;
    var column = this.cursor.column;

    if (key === 'ArrowUp') { row = Math.max(0, row - 1); }
    if (key === 'ArrowDown') { row = Math.min(rows.length - 1, row + 1); }
    if (key === 'ArrowLeft') { column = Math.max(0, column - 1); }
    if (key === 'ArrowRight') { column = Math.min(rows[row].length - 1, column + 1); }

    if (key === 'Enter') {
        var cell = rows[row][Math.min(column, rows[row].length - 1)];
        cell.click();
        return;
    }

    this.cursor = {row: row, column: column};
    this.applyCursor();
};

document.addEventListener('keydown', function(event) {
    if (testView.editing || testModel.suite === null) { return; }
    if (testView.view !== 'scenarios') { return; }

    var tagName = event.target.tagName;
    if (tagName === 'INPUT' || tagName === 'TEXTAREA' || tagName === 'SELECT') { return; }

    var keys = ['ArrowRight', 'ArrowLeft', 'ArrowUp', 'ArrowDown', 'Enter'];
    if (keys.indexOf(event.key) === -1) { return; }
    event.preventDefault();

    if (event.shiftKey && (event.key === 'ArrowUp' || event.key === 'ArrowDown')) {
        var offset = event.key === 'ArrowUp' ? -1 : 1;
        if (testModel.moveScenario(testView.selectedIndex, offset)) {
            testView.selectedIndex += offset;
            testView.render();
        }
        return;
    }
    testView.moveCursor(event.key);
});

// ////////////////////////////////////////////////////////////////////////

testModel.load(function() {
    if (testModel.suite !== null && testModel.suite.scenarios.length > 0 && testModel.documents !== null) {
        testModel.runAll(function(delta) {
            testView.lastDelta = delta;
            testView.render();
            testView.afterFirstRender();
        }, function(message) {
            testView.render();
            testView.afterFirstRender();
            data.reportError(message);
        });
        return;
    }

    testView.render();
    testView.afterFirstRender();
});

testView.afterFirstRender = function() {

    shared.attachPaneResize(document.getElementById('test-set-resizer'),
        document.getElementById('test-set-pane'), 'x');

    if (window.location.hash === '#ab') { testView.showView('ab'); }

    var termToHighlight = shared.termFromHash();
    if (termToHighlight !== null) {
        shared.applyTermHighlight(Array.from(document.querySelectorAll('[data-path="' + termToHighlight + '"]')));
    }
};

})();
