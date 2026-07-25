'use strict';

// Event handlers for the rule editor: the completion menu that always offers
// only the legal continuations, in-place value editing, the guided chain
// after each pick, keyboard jumps between placeholders, the rule switcher
// and the save that stores a new optimistic version.
// Augments the editorView namespace from editor-render.js.

(function() {

// ////////////////////////////////////////////////////////////////////////

editorView.closeMenu = function() {
    if (this.menuElement !== null) {
        this.menuElement.remove();
        this.menuElement = null;
    }
};

// The completion menu is anchored to the token it completes, never anywhere else.
// Items: {label, hint, checked, onPick}. A multi menu stays open across picks.
editorView.openMenu = function(anchor, title, items, isMulti) {
    this.closeMenu();
    var rectangle = anchor.getBoundingClientRect();

    // Remember the choices for keyboard navigation with the arrow keys
    this.menuChoices = [];
    this.menuChoice = -1;
    this.menuIsMulti = isMulti;

    var menu = document.createElement('div');
    menu.className = 'editor-completion-menu';

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

    document.body.appendChild(menu);

    // Position under the anchor, clamped to the viewport
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

    // Guided completion: the comparator menu opens by itself
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

    // Guided completion: an empty first value opens its own editor next
    var slots = editorModel.valueSlots(comparator);
    if (slots !== 0) {
        var firstEmpty = condition.values.indexOf('');
        if (slots === -1 && condition.values.length === 0) { this.autoOpen = 'value-condition-' + conditionIndex + '-0'; }
        if (firstEmpty > -1) { this.autoOpen = 'value-condition-' + conditionIndex + '-' + firstEmpty; }
    }
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

// The multi-select menu for the one-of comparators, a closed pick list
// with checkmarks
editorView.openSetMenu = function(event, conditionIndex) {
    event.stopPropagation();
    var condition = editorModel.rule.conditions[conditionIndex];
    var attribute = vocabulary.attribute(condition.subject);
    var anchor = event.currentTarget;
    var chipName = anchor.getAttribute('data-chip');

    // Only a closed domain has a pick list, open values type in place
    if (attribute.type !== 'choice') {
        this.editFreeSet(anchor, condition);
        return;
    }

    var items = [];
    attribute.values.forEach(function(value) {
        items.push({label: value, checked: condition.values.indexOf(value) > -1, onPick: function() {
            var position = condition.values.indexOf(value);
            if (position > -1) { condition.values.splice(position, 1); } else { condition.values.push(value); }

            // Keep the menu open across picks: re-render the sentence behind it,
            // then re-anchor to the freshly rendered chip.
            editorView.render();
            var freshAnchor = document.querySelector('[data-chip="' + chipName + '"]');
            editorView.openSetMenu({stopPropagation: function() {}, currentTarget: freshAnchor}, conditionIndex);
        }});
    });

    this.openMenu(anchor, 'Values of ' + attribute.phrase, items, true);
};

// One-of values over an open domain edit as one comma-separated line
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
        // The set chip has its own menu, this handler covers single slots
        if (editorModel.valueSlots(item.comparator) === -1) { this.openSetMenu(event, itemIndex); return; }
    } else {
        attribute = vocabulary.attribute(item.target);
    }

    // Enumerated domains edit through a closed pick list inside the sentence ..
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

    // .. numbers and text through free typing, validated on commit with a
    // red underline and a quick fix, never a save-then-fail.
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

            // Guided completion: a value-taking action opens its value editor next
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

    // Guided completion: the property menu opens on the new placeholder
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

    // The joiner in front of the removed condition goes with it,
    // the very first condition takes the joiner after it instead.
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

// A click in the vocabulary pane starts a new condition for that property
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

// The four views are renderings of the same stored document, switching
// between them changes nothing in the rule itself
editorView.setView = function(mode) {
    this.viewMode = mode;
    this.expressionMode = mode === 'expression';

    ['sentence', 'expression', 'table', 'document'].forEach(function(name) {
        document.getElementById('view-' + name).classList.toggle('toggled', name === mode);
    });
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

// The topbar line: which ruleset, which version, which rule
editorView.renderSubtitle = function() {
    var subtitle = document.getElementById('main-subtitle');

    if (editorModel.definitionId === null) {
        subtitle.textContent = 'no ruleset yet';
        return;
    }

    var text = shared.escape(editorModel.rulesetName) + ' &#183; version ' + editorModel.currentVersion;
    if (editorModel.rule !== null) {
        text += ' &#183; rule ' + shared.escape(editorModel.rule.name);
    }
    subtitle.innerHTML = text;
};

// Switching to another rule of the same ruleset goes through the address,
// so the browser history and shared links both work
editorView.openRuleMenu = function(event) {
    var items = [];

    Object.keys(editorModel.documents).forEach(function(key) {
        items.push({label: editorModel.documents[key].name, checked: key === editorModel.ruleKey, onPick: function() {
            window.location.href = '/editor/?ruleset=' + editorModel.definitionId + '&rule=' + encodeURIComponent(key);
        }});
    });

    this.openMenu(event.currentTarget, 'Rules of ' + editorModel.rulesetName, items, false);
};

editorView.openTests = function() {
    window.location.href = '/tests/?ruleset=' + editorModel.definitionId;
};

// ////////////////////////////////////////////////////////////////////////

// Save waits for the pending server check, then stores the whole ruleset
// with the edited rule swapped in, as a new optimistic version
editorView.save = function(button) {
    var handlers = shared.inFlight(button, function(payload) {
        editorView.renderSubtitle();
        shared.popover(button, 'Saved as version ' + payload.version + '.', 'green');
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    editorModel.check(function() {
        editorModel.save(handlers.done, handlers.error);
    }, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

// Keyboard navigation: arrows walk every token in the sentence, placeholders
// included, Enter or ArrowDown opens the focused token, and an open menu
// takes the arrows for its own choices.
document.addEventListener('keydown', function(event) {
    var tagName = event.target.tagName;
    if (tagName === 'INPUT' || tagName === 'TEXTAREA' || tagName === 'SELECT') { return; }

    // An open completion menu owns the keyboard first ..
    if (editorView.menuElement !== null) {
        if (event.key === 'ArrowDown') { event.preventDefault(); editorView.moveMenuChoice(1); }
        if (event.key === 'ArrowUp') { event.preventDefault(); editorView.moveMenuChoice(-1); }
        if (event.key === 'Enter') { event.preventDefault(); editorView.pickMenuChoice(); }
        if (event.key === 'Escape') { editorView.closeMenu(); }
        return;
    }

    if (editorModel.rule === null) { return; }

    // .. otherwise the arrows walk the sentence itself.
    if (event.key === 'ArrowRight') { event.preventDefault(); editorView.moveToken(1); }
    if (event.key === 'ArrowLeft') { event.preventDefault(); editorView.moveToken(-1); }
    if (event.key === 'Enter' || event.key === 'ArrowDown') { event.preventDefault(); editorView.openActiveToken(); }
});

// Any click outside the completion menu closes it
document.addEventListener('mousedown', function(event) {
    if (editorView.menuElement !== null && !editorView.menuElement.contains(event.target)) {
        editorView.closeMenu();
    }
});

// ////////////////////////////////////////////////////////////////////////

editorModel.load(function() {
    editorView.renderSubtitle();
    editorView.render();

    // Arriving from the vocabulary's where-used list: the sentence using
    // the term and the term's own picker entry glow
    var termToHighlight = shared.termFromHash();
    if (termToHighlight !== null && editorModel.rule !== null) {
        var termElements = [];

        var conditionsUseTerm = editorModel.rule.conditions.some(function(condition) {
            return condition.subject === termToHighlight;
        });
        var actionsUseTerm = editorModel.rule.thenActions.concat(editorModel.rule.elseActions).some(function(action) {
            return action.target === termToHighlight;
        });
        if (conditionsUseTerm || actionsUseTerm) {
            document.querySelectorAll('.editor-rule-sentence').forEach(function(sentence) {
                termElements.push(sentence);
            });
        }

        document.querySelectorAll('.vocabulary-item[data-path="' + termToHighlight + '"]').forEach(function(item) {
            termElements.push(item);
        });

        shared.applyTermHighlight(termElements);
    }
});

})();
