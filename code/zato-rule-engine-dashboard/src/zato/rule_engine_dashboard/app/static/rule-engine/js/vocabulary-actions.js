'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

vocabularyView.select = function(path) {
    var self = this;
    if (path === this.selectedPath) { return; }

    this.selectedPath = path;
    this.usage = null;
    shared.closePanel();
    this.render();

    vocabularyModel.whereUsed(path, function(usage) {
        if (self.selectedPath !== path) { return; }
        self.usage = usage;
        self.renderDetail();
        shared.initTips();
    });
};

vocabularyView.setFilter = function(value) {
    this.filter = value;
    this.renderTree();
};

vocabularyView.visiblePaths = function() {
    var out = [];
    document.querySelectorAll('.vocabulary-tree-item').forEach(function(item) {
        out.push(item.dataset.path);
    });
    return out;
};

// ////////////////////////////////////////////////////////////////////////

vocabularyView.editField = function(cell, field) {
    if (cell.querySelector('input') !== null) { return; }

    var attribute = vocabulary.attribute(this.selectedPath);
    var current = {
        phrase: attribute.phrase,
        values: attribute.type === 'choice' ? attribute.values.join(', ') : '',
        domain: attribute.type === 'number range' ? attribute.domain.low + ' .. ' + attribute.domain.high : '',
        description: 'description' in attribute ? attribute.description : '',
    }[field];

    cell.classList.add('cell-editing');
    cell.innerHTML = '<span class="field" data-hint="">' +
        '<input type="text" placeholder=" " value="' + shared.escape(current) + '">' +
        '</span>';
    var input = cell.querySelector('input');
    input.focus();
    input.select();

    var self = this;
    var commit = function() { self.commitField(cell, field, input.value); };
    input.addEventListener('blur', commit);
    input.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') { input.blur(); }
        if (event.key === 'Escape') { input.removeEventListener('blur', commit); self.renderDetail(); shared.initTips(); }
    });
};

vocabularyView.commitField = function(cell, field, value) {
    var self = this;
    var attribute = vocabulary.attribute(this.selectedPath);
    var message = 'Changed.';

    if (field === 'phrase') { attribute.phrase = value; }
    if (field === 'description') { attribute.description = value; message = 'Saved.'; }
    if (field === 'values') {
        attribute.values = value.split(',').map(function(item) { return item.trim(); })
            .filter(function(item) { return item !== ''; });
    }
    if (field === 'domain') {
        var text = value.trim();

        // An emptied cell is a cancelled edit, which is also the way out of a rejected one
        if (text === '') {
            this.renderDetail();
            shared.initTips();
            return;
        }

        var match = /^(-?\d+(?:\.\d+)?)\s*\.\.\s*(-?\d+(?:\.\d+)?)$/.exec(text);
        if (match === null) {
            this.renderDetail();
            shared.initTips();

            var fresh = document.querySelector('[data-field="domain"]');
            this.editField(fresh, 'domain');
            shared.requireInput(fresh.querySelector('input'), shared.config.requiredText.range);
            return;
        }
        attribute.domain = {low: +match[1], high: +match[2]};
    }

    vocabularyModel.saveDocument('Change ' + field + ' of ' + this.selectedPath, function() {
        self.renderDetail();
        shared.initTips();
        shared.popover(document.querySelector('[data-field="' + field + '"]'), message, 'green');
    }, data.reportError);
};

// ////////////////////////////////////////////////////////////////////////

vocabularyView.openRenamePopover = function(anchor) {
    if (shared.panelElement !== null) { shared.closePanel(); return; }

    var attribute = vocabulary.attribute(this.selectedPath);
    var count = this.usage === null ? 0 : this.usage.count;

    shared.openPanel(anchor,
        '<div class="floating-panel-line">' +
        '<span class="field" data-hint="">' +
        '<input id="vocabulary-rename-input" type="text" placeholder=" " value="' + attribute.name + '" ' +
            'onkeydown="vocabularyView.renameKeys(event)">' +
        '</span>' +
        '<button class="button-primary button-mini" onclick="vocabularyView.confirmRename(this)">' +
            'Rename in ' + count + ' place' + (count === 1 ? '' : 's') + '</button>' +
        '</div>');
};

vocabularyView.renameKeys = function(event) {
    if (event.key === 'Enter') { this.confirmRename(event.target); }
    if (event.key === 'Escape') { shared.closePanel(); }
};

vocabularyView.confirmRename = function(anchor) {
    var self = this;
    var input = document.getElementById('vocabulary-rename-input');
    var newName = input.value.trim();

    if (newName === '' || /[^A-Za-z0-9_]/.test(newName)) {
        shared.requireInput(input, shared.config.requiredText.name);
        return;
    }

    var path = this.selectedPath;

    var handlers = shared.inFlight(anchor, function(report) {
        self.selectedPath = path.split('.')[0] + '.' + newName;
        self.usage = null;
        shared.closePanel();
        self.select(self.selectedPath);
        self.render();

        shared.popover(document.querySelector('.vocabulary-detail-name'),
            'Renamed across ' + report.definitions.length + ' ruleset' +
            (report.definitions.length === 1 ? '' : 's'), 'green');
    }, function(message) {
        shared.popover(anchor, message, 'red');
    });
    if (handlers === null) { return; }

    vocabularyModel.rename(path, newName, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

vocabularyView.deprecate = function(button) {
    var self = this;

    var handlers = shared.inFlight(button, function() {
        self.render();
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    vocabularyModel.deprecate(this.selectedPath, handlers.done, handlers.error);
};

vocabularyView.restore = function(button) {
    var self = this;

    var handlers = shared.inFlight(button, function() {
        self.render();
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    vocabularyModel.restore(this.selectedPath, handlers.done, handlers.error);
};

vocabularyView.deleteTerm = function(button) {
    var self = this;
    var path = this.selectedPath;

    var handlers = shared.inFlight(button, function() {
        var paths = vocabularyModel.allPaths();
        self.selectedPath = null;
        self.usage = null;
        if (paths.length > 0) { self.select(paths[0]); }
        self.render();
        shared.popover(document.getElementById('vocabulary-tree-list'), 'Deleted ' + path + '.', 'green');
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    vocabularyModel.deleteTerm(path, handlers.done, handlers.error);
};

vocabularyView.explainBlockedDelete = function(anchor) {
    var count = this.usage === null ? 0 : this.usage.count;
    shared.popover(anchor, 'Not deleted, ' + count + ' places still use this term.', 'red');
};

// ////////////////////////////////////////////////////////////////////////

vocabularyView.openAddPanel = function(button) {
    if (shared.panelElement !== null) { shared.closePanel(); return; }

    var entityOptions = '';
    vocabulary.entities.forEach(function(entity) {
        entityOptions += '<option value="' + entity.name + '">' + entity.name + '</option>';
    });
    entityOptions += '<option value="">New entity</option>';

    shared.openPanel(button,
        '<div class="floating-panel-line">' +
        '<select id="vocabulary-add-entity" onchange="vocabularyView.onAddEntityChange(this)">' + entityOptions + '</select>' +
        '<span class="field" id="vocabulary-add-entity-field" data-hint="Entity name" style="display:none">' +
        '<input id="vocabulary-add-entity-name" type="text" placeholder=" ">' +
        '</span>' +
        '<span class="field" data-hint="Term name">' +
        '<input id="vocabulary-add-name" type="text" placeholder=" " ' +
            'onkeydown="if (event.key === \'Enter\') { vocabularyView.confirmAddTerm(this); }">' +
        '</span>' +
        '<select id="vocabulary-add-type">' +
        '<option>number</option><option>number range</option><option>choice</option>' +
        '<option>yes/no</option><option>text</option></select>' +
        '<button class="button-primary button-mini" onclick="vocabularyView.confirmAddTerm(this)">Add</button>' +
        '</div>');

    if (vocabulary.entities.length === 0) { this.onAddEntityChange(document.getElementById('vocabulary-add-entity')); }

    document.getElementById('vocabulary-add-name').focus();
};

vocabularyView.onAddEntityChange = function(select) {
    var entityField = document.getElementById('vocabulary-add-entity-field');
    entityField.style.display = select.value === '' ? 'flex' : 'none';
    if (select.value === '') { document.getElementById('vocabulary-add-entity-name').focus(); }
};

vocabularyView.confirmAddTerm = function(anchor) {
    var self = this;
    var entityName = document.getElementById('vocabulary-add-entity').value;
    if (entityName === '') { entityName = document.getElementById('vocabulary-add-entity-name').value.trim(); }
    var name = document.getElementById('vocabulary-add-name').value.trim();
    var type = document.getElementById('vocabulary-add-type').value;

    if (entityName === '' || /[^A-Za-z0-9_]/.test(entityName)) {
        shared.requireInput(document.getElementById('vocabulary-add-entity-name'), shared.config.requiredText.entity);
        return;
    }

    if (name === '' || /[^A-Za-z0-9_]/.test(name)) {
        shared.requireInput(document.getElementById('vocabulary-add-name'), shared.config.requiredText.term);
        return;
    }

    var handlers = shared.inFlight(anchor, function(path) {
        shared.closePanel();
        self.selectedPath = null;
        self.select(path);
    }, function(message) {
        shared.popover(anchor, message, 'red');
    });
    if (handlers === null) { return; }

    vocabularyModel.addTerm(entityName, name, type, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

vocabularyView.openPayloadPanel = function(button) {
    if (shared.panelElement !== null) { shared.closePanel(); return; }

    var example = '{"applicant": {"age": 34, "employed": true, "city": "Boston"}, "requestedAmount": 25000}';
    shared.openPanel(button,
        '<textarea id="vocabulary-payload-text" spellcheck="false">' + example + '</textarea>' +
        '<div class="floating-panel-actions">' +
        '<button class="button-primary button-mini" onclick="vocabularyView.previewPayload(this)">Preview terms</button>' +
        '</div>' +
        '<div id="vocabulary-payload-preview"></div>');
};

vocabularyView.previewPayload = function(button) {
    var self = this;

    var handlers = shared.inFlight(button, function(terms) {
        self.previewedTerms = terms;
        document.getElementById('vocabulary-payload-preview').innerHTML =
            self.previewListHtml(terms, 'vocabularyView.addPayloadTerms(this)');
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    vocabularyModel.inferFromPayload(document.getElementById('vocabulary-payload-text').value,
        handlers.done, handlers.error);
};

vocabularyView.previewListHtml = function(terms, addCall) {
    var newCount = terms.filter(function(term) { return !term.exists; }).length;
    var html = '';

    terms.forEach(function(term) {
        var classes = 'vocabulary-payload-term' + (term.exists ? ' vocabulary-payload-term-known' : '');
        var note = term.exists ? 'already in the vocabulary' : term.type;
        html += '<div class="' + classes + '"><b>' + term.entity + '.' + term.name + '</b>' +
            '<span>' + shared.escape(note) + '</span></div>';
    });

    if (newCount > 0) {
        html += '<div class="floating-panel-actions">' +
            '<button class="button-primary button-mini" onclick="' + addCall + '">Add ' +
            newCount + ' term' + (newCount === 1 ? '' : 's') + '</button></div>';
    } else {
        html += '<div class="floating-panel-line">No new terms.</div>';
    }
    return html;
};

vocabularyView.addPayloadTerms = function(button) {
    var self = this;

    var handlers = shared.inFlight(button, function(added, firstPath) {
        shared.closePanel();
        if (firstPath !== null) {
            self.selectedPath = null;
            self.select(firstPath);
        }
        shared.popover(document.getElementById('vocabulary-tree-list'),
            'Added ' + added + ' term' + (added === 1 ? '' : 's') + '.', 'green');
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    vocabularyModel.addTerms(this.previewedTerms, 'Add terms from an example payload', handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

vocabularyView.openRulesPanel = function(button) {
    if (shared.panelElement !== null) { shared.closePanel(); return; }

    shared.openPanel(button,
        '<textarea id="vocabulary-rules-text" spellcheck="false" placeholder="rule&#10;    Name&#10;when&#10;    ...&#10;then&#10;    ..."></textarea>' +
        '<div class="floating-panel-actions">' +
        '<button class="button-primary button-mini" onclick="vocabularyView.previewRules(this)">Preview terms</button>' +
        '</div>' +
        '<div id="vocabulary-rules-preview"></div>');
};

vocabularyView.previewRules = function(button) {
    var self = this;

    var handlers = shared.inFlight(button, function(proposals, errors) {
        if (errors.length > 0) {
            shared.popover(button, 'The rules do not parse: ' + errors[0].message, 'red');
            return;
        }
        if (proposals.length === 0) {
            document.getElementById('vocabulary-rules-preview').innerHTML =
                '<div class="floating-panel-line">No new terms.</div>';
            return;
        }

        self.previewedProposals = proposals;
        document.getElementById('vocabulary-rules-preview').innerHTML =
            self.previewListHtml(proposals, 'vocabularyView.addRuleTerms(this)');
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    vocabularyModel.inferFromRules(document.getElementById('vocabulary-rules-text').value,
        handlers.done, handlers.error);
};

vocabularyView.addRuleTerms = function(button) {
    var self = this;

    var handlers = shared.inFlight(button, function(added, firstPath) {
        shared.closePanel();
        if (firstPath !== null) {
            self.selectedPath = null;
            self.select(firstPath);
        }
        shared.popover(document.getElementById('vocabulary-tree-list'), 'Added ' + added +
            ' proposed terms, their types came from how the rules use them.', 'green');
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    vocabularyModel.addTerms(this.previewedProposals, 'Add terms proposed from typed rules', handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

vocabularyView.onKeyDown = function(event) {
    var target = event.target;
    var inField = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT';

    if (event.key === 'Escape') { shared.closePanel(); return; }
    if (event.key === '/' && !inField) {
        event.preventDefault();
        document.getElementById('vocabulary-filter').focus();
        return;
    }
    if (inField || (event.key !== 'ArrowUp' && event.key !== 'ArrowDown')) { return; }
    event.preventDefault();

    var paths = this.visiblePaths();
    if (paths.length === 0) { return; }

    var position = paths.indexOf(this.selectedPath);
    var next = Math.max(0, Math.min(paths.length - 1, position + (event.key === 'ArrowDown' ? 1 : -1)));
    if (paths[next] === this.selectedPath) { return; }

    this.select(paths[next]);
    var item = document.querySelector('.vocabulary-tree-item-selected');
    if (item !== null) { item.scrollIntoView({block: 'nearest'}); }
};

// ////////////////////////////////////////////////////////////////////////

vocabularyModel.load(function() {

    var termToHighlight = shared.termFromHash();
    var paths = vocabularyModel.allPaths();
    var first = null;

    if (termToHighlight !== null && paths.indexOf(termToHighlight) > -1) {
        first = termToHighlight;
    } else if (paths.length > 0) {
        first = paths[0];
    }

    vocabularyView.render();
    if (first !== null) { vocabularyView.select(first); }

    if (termToHighlight !== null && first === termToHighlight) {
        shared.applyTermHighlight(Array.from(document.querySelectorAll(
            '.vocabulary-tree-item[data-path="' + termToHighlight + '"], .vocabulary-detail-name')));
    }
});

document.getElementById('vocabulary-filter').addEventListener('input', function(event) {
    vocabularyView.setFilter(event.target.value);
});

document.addEventListener('keydown', function(event) { vocabularyView.onKeyDown(event); });

shared.panelToggles.push('#vocabulary-payload-button', '#vocabulary-rules-button', '#vocabulary-add-button',
    '.vocabulary-detail-name');

shared.attachPaneResize(document.getElementById('vocabulary-tree-resizer'),
    document.getElementById('vocabulary-tree-pane'), 'x');

})();
