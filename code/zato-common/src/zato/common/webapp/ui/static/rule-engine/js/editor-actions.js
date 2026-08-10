'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

editorView.closeMenu = function() {
    if (this.menuElement !== null) {
        this.menuElement.remove();
        this.menuElement = null;
    }
};

editorView.openMenu = function(anchor, title, items, isMulti) {
    this.closeMenu();
    var rectangle = anchor.getBoundingClientRect();

    this.menuChoices = [];
    this.menuChoice = -1;
    this.menuIsMulti = isMulti;

    var menu = document.createElement('div');

    // The menu hangs off the floating root, outside the container, so it carries the scope class itself
    menu.className = 'rule-editor editor-completion-menu';

    var titleElement = document.createElement('div');
    titleElement.className = 'editor-completion-title';
    titleElement.textContent = title;
    menu.appendChild(titleElement);

    items.forEach(function(item) {
        var itemElement = document.createElement('div');
        itemElement.className = 'editor-completion-item';

        var checkElement = document.createElement('span');
        checkElement.className = 'editor-completion-check';
        if (item.checked) { checkElement.innerHTML = shared.icon('check', 12); }
        itemElement.appendChild(checkElement);

        var labelElement = document.createElement('span');
        labelElement.textContent = item.label;
        itemElement.appendChild(labelElement);

        if (item.hint !== undefined) {
            var hintElement = document.createElement('span');
            hintElement.className = 'editor-completion-hint';
            hintElement.textContent = item.hint;
            itemElement.appendChild(hintElement);
        }

        itemElement.addEventListener('mousedown', function(event) {
            event.preventDefault();
            event.stopPropagation();
            item.onPick();
            if (!isMulti) { editorView.closeMenu(); }
        });

        menu.appendChild(itemElement);
        editorView.menuChoices.push({element: itemElement, onPick: item.onPick});
    });

    shared.floatingRoot().appendChild(menu);

    var left = Math.min(rectangle.left, window.innerWidth - menu.offsetWidth - 12);
    var top = rectangle.bottom + 4;
    if (top + menu.offsetHeight > window.innerHeight - 8) { top = rectangle.top - menu.offsetHeight - 4; }
    menu.style.left = left + 'px';
    menu.style.top = top + 'px';

    this.menuElement = menu;
};

// ////////////////////////////////////////////////////////////////////////

editorView.moveMenuChoice = function(step) {
    if (this.menuChoices.length === 0) { return; }

    this.menuChoice = (this.menuChoice + step + this.menuChoices.length) % this.menuChoices.length;
    this.menuChoices.forEach(function(choice, choiceIndex) {
        choice.element.classList.toggle('editor-completion-item-active', choiceIndex === editorView.menuChoice);
    });
    this.menuChoices[this.menuChoice].element.scrollIntoView({block: 'nearest'});
};

editorView.pickMenuChoice = function() {
    if (this.menuChoice < 0 || this.menuChoice >= this.menuChoices.length) { return; }

    this.menuChoices[this.menuChoice].onPick();
    if (!this.menuIsMulti) { this.closeMenu(); }
};

// ////////////////////////////////////////////////////////////////////////

editorView.openSubjectMenu = function(event, conditionIndex) {
    event.stopPropagation();
    var items = [];

    vocabulary.entities.forEach(function(entity) {
        vocabulary.pickerAttributes(entity).forEach(function(attribute) {
            var path = entity.name + '.' + attribute.name;
            items.push({label: attribute.phrase, hint: path, checked: false, onPick: function() {
                editorView.pickSubject(conditionIndex, path);
            }});
        });
    });

    this.openMenu(event.currentTarget, 'Properties', items, false);
};

editorView.pickSubject = function(conditionIndex, path) {
    var condition = editorModel.rule.conditions[conditionIndex];
    condition.subject = path;
    condition.comparator = null;
    condition.values = [];

    this.autoOpen = 'comparator-' + conditionIndex;
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

editorView.openComparatorMenu = function(event, conditionIndex) {
    event.stopPropagation();
    var condition = editorModel.rule.conditions[conditionIndex];
    var attribute = vocabulary.attribute(condition.subject);
    var items = [];

    editorModel.comparatorsFor(condition.subject).forEach(function(comparator) {
        items.push({label: comparator, hint: editorModel.comparatorSymbols[comparator],
            checked: condition.comparator === comparator, onPick: function() {
                editorView.pickComparator(conditionIndex, comparator);
            }});
    });

    this.openMenu(event.currentTarget, 'Comparisons for ' + attribute.phrase, items, false);
};

editorView.pickComparator = function(conditionIndex, comparator) {
    var condition = editorModel.rule.conditions[conditionIndex];
    condition.comparator = comparator;
    editorModel.coerceValues(condition);

    var slots = editorModel.valueSlots(comparator);
    if (slots !== 0) {
        var firstEmpty = condition.values.indexOf('');
        if (slots === -1 && condition.values.length === 0) { this.autoOpen = 'value-condition-' + conditionIndex + '-0'; }
        if (firstEmpty > -1) { this.autoOpen = 'value-condition-' + conditionIndex + '-' + firstEmpty; }
    }
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

editorView.openSetMenu = function(event, conditionIndex) {
    event.stopPropagation();
    var condition = editorModel.rule.conditions[conditionIndex];
    var attribute = vocabulary.attribute(condition.subject);
    var anchor = event.currentTarget;
    var chipName = anchor.getAttribute('data-chip');

    if (attribute.type !== 'choice') {
        this.editFreeSet(anchor, condition);
        return;
    }

    var items = [];
    attribute.values.forEach(function(value) {
        items.push({label: value, checked: condition.values.indexOf(value) > -1, onPick: function() {
            var position = condition.values.indexOf(value);
            if (position > -1) { condition.values.splice(position, 1); } else { condition.values.push(value); }

            editorView.render();
            var freshAnchor = editorView.element('[data-chip="' + chipName + '"]');
            editorView.openSetMenu({stopPropagation: function() {}, currentTarget: freshAnchor}, conditionIndex);
        }});
    });

    this.openMenu(anchor, 'Values of ' + attribute.phrase, items, true);
};

editorView.editFreeSet = function(anchor, condition) {
    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'editor-token-input';
    input.value = condition.values.join(', ');
    anchor.replaceWith(input);
    input.focus();
    input.select();

    var commit = function() {
        condition.values = input.value.split(',')
            .map(function(part) { return part.trim(); })
            .filter(function(part) { return part !== ''; });
        editorView.render();
    };
    input.onkeydown = function(keyEvent) {
        if (keyEvent.key === 'Enter') { commit(); }
        if (keyEvent.key === 'Escape') { editorView.render(); }
    };
    input.onblur = commit;
};

// ////////////////////////////////////////////////////////////////////////

editorView.itemFor = function(listKey, itemIndex) {
    var out = listKey === 'condition' ? editorModel.rule.conditions[itemIndex] : editorModel.rule[listKey][itemIndex];
    return out;
};

editorView.editValue = function(event, listKey, itemIndex, valueIndex) {
    event.stopPropagation();
    var chip = event.currentTarget;
    var item = this.itemFor(listKey, itemIndex);

    var attribute;
    if (listKey === 'condition') {
        attribute = vocabulary.attribute(item.subject);
        if (editorModel.valueSlots(item.comparator) === -1) { this.openSetMenu(event, itemIndex); return; }
    } else {
        attribute = vocabulary.attribute(item.target);
    }

    if (attribute.type === 'choice' || attribute.type === 'yes/no') {
        var values = attribute.type === 'yes/no' ? ['true', 'false'] : attribute.values;
        var items = [];
        values.forEach(function(value) {
            items.push({label: value, checked: item.values[valueIndex] === value, onPick: function() {
                item.values[valueIndex] = value;
                editorView.render();
            }});
        });
        this.openMenu(chip, 'Values of ' + attribute.phrase, items, false);
        return;
    }

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'editor-token-input';
    input.value = item.values[valueIndex];
    chip.replaceWith(input);
    input.focus();
    input.select();

    var commit = function() {
        item.values[valueIndex] = input.value.trim();
        editorView.render();
    };
    input.onkeydown = function(keyEvent) {
        if (keyEvent.key === 'Enter') { commit(); }
        if (keyEvent.key === 'Escape') { editorView.render(); }
    };
    input.onblur = commit;
};

// ////////////////////////////////////////////////////////////////////////

editorView.openActionMenu = function(event, listName, actionIndex) {
    event.stopPropagation();
    var action = editorModel.rule[listName][actionIndex];
    var items = [];

    editorModel.actionChoices().forEach(function(choice) {
        var isCurrent = action.target === choice.target && action.values[0] === choice.values[0];
        items.push({label: choice.label, hint: choice.target, checked: isCurrent, onPick: function() {
            action.target = choice.target;
            action.values = choice.values.slice();

            if (action.values[0] === '') { editorView.autoOpen = 'value-' + listName + '-' + actionIndex + '-0'; }
            editorView.render();
        }});
    });

    this.openMenu(event.currentTarget, 'Actions', items, false);
};

// ////////////////////////////////////////////////////////////////////////

editorView.addCondition = function() {
    editorModel.rule.conditions.push({subject: null, comparator: null, values: []});
    if (editorModel.rule.conditions.length > 1) { editorModel.rule.joiners.push('and'); }

    this.autoOpen = 'subject-' + (editorModel.rule.conditions.length - 1);
    this.render();
};

editorView.addAction = function(listName) {
    editorModel.rule[listName].push({target: null, values: ['']});
    this.autoOpen = 'action-' + listName + '-' + (editorModel.rule[listName].length - 1);
    this.render();
};

editorView.removeCondition = function(event, conditionIndex) {
    event.stopPropagation();
    editorModel.rule.conditions.splice(conditionIndex, 1);

    if (editorModel.rule.joiners.length > 0) {
        var joinerIndex = conditionIndex === 0 ? 0 : conditionIndex - 1;
        editorModel.rule.joiners.splice(joinerIndex, 1);
    }
    this.render();
};

editorView.toggleJoiner = function(joinerIndex) {
    var joiners = editorModel.rule.joiners;
    joiners[joinerIndex] = joiners[joinerIndex] === 'and' ? 'or' : 'and';
    this.render();
};

editorView.removeAction = function(event, listName, actionIndex) {
    event.stopPropagation();
    editorModel.rule[listName].splice(actionIndex, 1);
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

editorView.pickVocabulary = function(path) {
    editorModel.rule.conditions.push({subject: path, comparator: null, values: []});
    if (editorModel.rule.conditions.length > 1) { editorModel.rule.joiners.push('and'); }
    this.autoOpen = 'comparator-' + (editorModel.rule.conditions.length - 1);
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

editorView.applyFix = function(problemIndex) {
    var fix = this.problems[problemIndex].fix;
    fix.values[fix.valueIndex] = fix.value;
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

// What the tab click and the address-bar restore share - the mode itself and
// the toolbar buttons, with no repaint of its own
editorView.applyView = function(mode) {
    this.viewMode = mode;
    this.expressionMode = mode === 'expression';

    var activeClass = editorModel.config.viewButtonActiveClass;

    this.elements('[data-action="set-view"]').forEach(function(button) {
        var isActive = button.getAttribute('data-view') === mode;
        button.classList.toggle(activeClass, isActive);
        button.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });
};

// The open view's place in the address bar, so a tab can be bookmarked -
// only for a host that named the parameter to keep it under
editorView.writeViewToURL = function() {
    var key = editorModel.config.viewURLKey;
    if (key === null) { return; }

    var params = new URLSearchParams(window.location.search);
    params.set(key, this.viewMode);
    history.replaceState(null, '', '?' + params.toString());
};

editorView.setView = function(mode) {
    this.applyView(mode);
    this.writeViewToURL();
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

editorView.openRuleMenu = function(event) {
    var items = [];

    Object.keys(editorModel.documents).forEach(function(key) {
        items.push({label: editorModel.documents[key].name, checked: key === editorModel.ruleKey, onPick: function() {
            editorModel.config.navigateToRule(editorModel.definitionId, key);
        }});
    });

    this.openMenu(event.currentTarget, 'Rules of ' + editorModel.rulesetName, items, false);
};

// ////////////////////////////////////////////////////////////////////////

// The open rule's place in the address bar, so a rule switched to in place
// stays bookmarkable - only for a host that named the parameter
editorView.writeRuleToURL = function() {
    var key = editorModel.config.ruleURLKey;
    if (key === null) { return; }

    var params = new URLSearchParams(window.location.search);
    params.set(key, editorModel.ruleKey);
    history.replaceState(null, '', '?' + params.toString());
};

// Opens another rule of the loaded ruleset in place - every document is already
// here, so nothing reloads and nothing flickers. Unsaved work is not lost, the
// dirty working copy sits in local storage and comes back with the rule.
editorView.openRule = function(ruleKey) {
    this.closeMenu();
    editorModel.openRuleKey(ruleKey);
    this.writeRuleToURL();
    this.render();
};

editorView.openTests = function() {
    window.location.href = editorModel.config.testsUrl + '?ruleset=' + editorModel.definitionId;
};

// ////////////////////////////////////////////////////////////////////////

// Each rule walks its own history - the stacks hold JSON snapshots of the
// rule, the last one on the undo stack being the state on screen
editorView.historyFor = function() {

    // A rule not yet saved has no key, so its history lives under its name
    var key = editorModel.ruleKey === null ? 'new ' + editorModel.config.newRuleName : editorModel.ruleKey;

    if (this.historyByRule[key] === undefined) {
        this.historyByRule[key] = {undoStack: [], redoStack: []};
    }

    return this.historyByRule[key];
};

editorView.undo = function() {
    var stacks = this.historyFor();

    // The bottom snapshot is what the rule opened with - there is nothing under it
    if (stacks.undoStack.length < 2) { return; }

    // The state on screen moves over to the redo side ..
    var current = stacks.undoStack.pop();
    stacks.redoStack.push(current);

    // .. and the one before it comes back
    this.restoreSnapshot(stacks.undoStack[stacks.undoStack.length - 1]);
};

editorView.redo = function() {
    var stacks = this.historyFor();
    if (stacks.redoStack.length === 0) { return; }

    var snapshot = stacks.redoStack.pop();
    stacks.undoStack.push(snapshot);

    this.restoreSnapshot(snapshot);
};

editorView.restoreSnapshot = function(snapshot) {
    editorModel.rule = JSON.parse(snapshot);

    // The render must not treat the restored state as a fresh edit,
    // which would wipe the redo stack
    this.restoringHistory = true;
    this.render();
    this.restoringHistory = false;
};

// ////////////////////////////////////////////////////////////////////////

editorView.save = function(button) {
    var handlers = shared.inFlight(button, function(payload) {
        shared.popover(button, 'Saved as version ' + payload.version + '.', 'green');

        // The rule is clean now - the render lets the change tracking
        // dim the Save button again and take the star off the name
        if (editorModel.config.trackChanges) { editorView.render(); }

        if (editorModel.config.onSaved !== undefined) { editorModel.config.onSaved(payload); }
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    editorModel.check(function() {
        editorModel.save(handlers.done, handlers.error);
    }, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

// What each data-action attribute in the editor's markup runs when clicked - the markup itself
// carries no inline handlers, so the editor works under a CSP that bans inline scripts
editorView.dispatch = function(event, target) {
    var action = target.getAttribute('data-action');
    var listName = target.getAttribute('data-list');
    var itemIndex = parseInt(target.getAttribute('data-item'));
    var valueIndex = parseInt(target.getAttribute('data-value'));

    // The existing handlers expect the event-like shape of an inline handler's event
    var synthetic = {
        stopPropagation: function() { event.stopPropagation(); },
        currentTarget: target,
    };

    if (action === 'edit-value') { this.editValue(synthetic, listName, itemIndex, valueIndex); }
    if (action === 'open-subject-menu') { this.openSubjectMenu(synthetic, itemIndex); }
    if (action === 'open-comparator-menu') { this.openComparatorMenu(synthetic, itemIndex); }
    if (action === 'open-set-menu') { this.openSetMenu(synthetic, itemIndex); }
    if (action === 'open-action-menu') { this.openActionMenu(synthetic, listName, itemIndex); }
    if (action === 'remove-condition') { this.removeCondition(synthetic, itemIndex); }
    if (action === 'remove-action') { this.removeAction(synthetic, listName, itemIndex); }
    if (action === 'add-condition') { this.addCondition(); }
    if (action === 'add-action') { this.addAction(listName); }
    if (action === 'toggle-joiner') { this.toggleJoiner(itemIndex); }
    if (action === 'pick-vocabulary') { this.pickVocabulary(target.getAttribute('data-path')); }
    if (action === 'apply-fix') { this.applyFix(itemIndex); }
    if (action === 'set-view') { this.setView(target.getAttribute('data-view')); }
    if (action === 'open-rule-menu') { this.openRuleMenu(synthetic); }
    if (action === 'open-tests') { this.openTests(); }
    if (action === 'save') { this.save(target); }
};

// ////////////////////////////////////////////////////////////////////////

editorView.bindListeners = function() {
    var self = this;

    this.container.addEventListener('click', function(event) {
        var target = event.target.closest('[data-action]');
        if (target === null || !self.container.contains(target)) { return; }
        self.dispatch(event, target);
    });

    document.addEventListener('keydown', function(event) {
        var tagName = event.target.tagName;
        if (tagName === 'INPUT' || tagName === 'TEXTAREA' || tagName === 'SELECT') { return; }

        if (editorView.menuElement !== null) {
            if (event.key === 'ArrowDown') { event.preventDefault(); editorView.moveMenuChoice(1); }
            if (event.key === 'ArrowUp') { event.preventDefault(); editorView.moveMenuChoice(-1); }
            if (event.key === 'Enter') { event.preventDefault(); editorView.pickMenuChoice(); }
            if (event.key === 'Escape') { editorView.closeMenu(); }
            return;
        }

        if (editorModel.rule === null) { return; }

        // Ctrl-Z and Ctrl-Y (or Ctrl-Shift-Z) walk the open rule's own history,
        // only for a host that turned change tracking on
        if (editorModel.config.trackChanges && (event.ctrlKey || event.metaKey)) {
            var keyName = event.key.toLowerCase();

            if (keyName === 'z' && !event.shiftKey) { event.preventDefault(); editorView.undo(); return; }
            if (keyName === 'y' || keyName === 'z') { event.preventDefault(); editorView.redo(); return; }
        }

        if (event.key === 'ArrowRight') { event.preventDefault(); editorView.moveToken(1); }
        if (event.key === 'ArrowLeft') { event.preventDefault(); editorView.moveToken(-1); }
        if (event.key === 'Enter' || event.key === 'ArrowDown') { event.preventDefault(); editorView.openActiveToken(); }
    });

    document.addEventListener('mousedown', function(event) {
        if (editorView.menuElement !== null && !editorView.menuElement.contains(event.target)) {
            editorView.closeMenu();
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

editorView.highlightTermFromHash = function() {
    var termToHighlight = shared.termFromHash();
    if (termToHighlight === null || editorModel.rule === null) { return; }

    var termElements = [];

    var conditionsUseTerm = editorModel.rule.conditions.some(function(condition) {
        return condition.subject === termToHighlight;
    });
    var actionsUseTerm = editorModel.rule.thenActions.concat(editorModel.rule.elseActions).some(function(action) {
        return action.target === termToHighlight;
    });
    if (conditionsUseTerm || actionsUseTerm) {
        editorView.elements('.editor-rule-sentence').forEach(function(sentence) {
            termElements.push(sentence);
        });
    }

    editorView.elements('.vocabulary-item[data-path="' + termToHighlight + '"]').forEach(function(item) {
        termElements.push(item);
    });

    shared.applyTermHighlight(termElements);
};

// ////////////////////////////////////////////////////////////////////////

// The one entry point - the host application says where the editor lives and how to reach
// its endpoints, nothing boots as a side effect of loading the scripts
editorView.init = function(container, config) {
    this.container = container;

    Object.keys(config).forEach(function(key) {
        editorModel.config[key] = config[key];
    });

    if (config.csrfToken !== undefined) { data.config.csrfToken = config.csrfToken; }

    this.bindListeners();

    // The view the address names opens first, so a bookmarked tab comes back -
    // only a view the host's toolbar actually has can open
    if (editorModel.config.viewURLKey !== null) {
        var urlParams = new URLSearchParams(window.location.search);
        var urlView = urlParams.get(editorModel.config.viewURLKey);

        if (urlView !== null && this.element('[data-view="' + urlView + '"]') !== null) {
            this.applyView(urlView);
        }
    }

    editorModel.load(function() {
        editorView.render();
        editorView.highlightTermFromHash();
    });
};

// ////////////////////////////////////////////////////////////////////////

})();
