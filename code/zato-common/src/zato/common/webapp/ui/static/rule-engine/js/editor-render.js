'use strict';

(function() {

var editorView = {

    container: null,
    viewMode: 'sentence',
    expressionMode: false,
    autoOpen: null,
    problems: [],
    invalidKeys: {},
    menuElement: null,
    menuChoices: [],
    menuChoice: -1,
    menuIsMulti: false,
    checkTimer: null,
    parseTimer: null,

    // Undo and redo stacks per rule, and whether a render is replaying one of
    // their snapshots rather than showing a fresh edit
    historyByRule: {},
    restoringHistory: false,

// ////////////////////////////////////////////////////////////////////////

    // Every element lookup is scoped to the container the host application passed to init
    element: function(selector) {
        var out = this.container.querySelector(selector);
        return out;
    },

    elements: function(selector) {
        var out = this.container.querySelectorAll(selector);
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    keywordHtml: function(text) {
        var out = '<span class="editor-keyword">' + text + '</span>';
        return out;
    },

    tokenHtml: function(kindClass, chipName, text, actionAttributes, isInvalid) {
        var classes = 'editor-token ' + kindClass + (isInvalid ? ' editor-token-invalid' : '');
        var out = '<span class="' + classes + '" data-chip="' + chipName + '" ' + actionAttributes + '>' +
            shared.escape(text) + '</span>';
        return out;
    },

    placeholderHtml: function(chipName, text, actionAttributes) {
        var out = '<span class="editor-token editor-token-placeholder" data-chip="' + chipName + '" ' + actionAttributes + '>' +
            shared.escape(text) + '</span>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    valueChipHtml: function(listKey, itemIndex, valueIndex, value, attribute) {
        var chipName = 'value-' + listKey + '-' + itemIndex + '-' + valueIndex;
        var action = 'data-action="edit-value" data-list="' + listKey + '" data-item="' + itemIndex + '"' +
            ' data-value="' + valueIndex + '"';

        if (value === '') {
            var out = this.placeholderHtml(chipName, editorModel.valuePlaceholder(attribute), action);
            return out;
        }

        var isInvalid = this.invalidKeys[listKey + '-' + itemIndex + '-' + valueIndex] === true;
        var html = this.tokenHtml('editor-token-value', chipName, value, action, isInvalid);
        return html;
    },

// ////////////////////////////////////////////////////////////////////////

    conditionBodyHtml: function(condition, conditionIndex) {
        var parts = [];

        if (condition.subject !== null) {
            var comparatorAction = 'data-action="open-comparator-menu" data-item="' + conditionIndex + '"';
            if (condition.comparator === null) {
                parts.push(this.placeholderHtml('comparator-' + conditionIndex, editorModel.placeholders.comparator,
                    comparatorAction));
            } else {
                var comparatorText = this.expressionMode
                    ? editorModel.comparatorSymbols[condition.comparator] : condition.comparator;
                parts.push(this.tokenHtml('editor-token-comparator', 'comparator-' + conditionIndex,
                    comparatorText, comparatorAction, false));
            }
        }

        if (condition.subject !== null && condition.comparator !== null) {
            var conditionAttribute = vocabulary.attribute(condition.subject);
            var slots = editorModel.valueSlots(condition.comparator);

            if (slots === -1) {
                var setAction = 'data-action="open-set-menu" data-item="' + conditionIndex + '"';
                var setChipName = 'value-condition-' + conditionIndex + '-0';
                if (condition.values.length === 0) {
                    parts.push(this.placeholderHtml(setChipName, editorModel.placeholders.set, setAction));
                } else {
                    var setText = this.expressionMode
                        ? '[' + condition.values.join(', ') + ']' : condition.values.join(', ');
                    parts.push(this.tokenHtml('editor-token-value', setChipName, setText, setAction, false));
                }
            }

            if (slots === 1) {
                parts.push(this.valueChipHtml('condition', conditionIndex, 0, condition.values[0], conditionAttribute));
            }

            if (slots === 2) {
                var first = this.valueChipHtml('condition', conditionIndex, 0, condition.values[0], conditionAttribute);
                var second = this.valueChipHtml('condition', conditionIndex, 1, condition.values[1], conditionAttribute);
                var joiner = this.expressionMode ? '..' : ' and ';
                parts.push(first + joiner + second);
            }
        }

        var out = parts.join('');
        return out;
    },

    removeConditionHtml: function(conditionIndex) {
        var out = '<span class="editor-group-remove" data-action="remove-condition" data-item="' + conditionIndex + '">' +
            shared.icon('x', 11) + '</span>';
        return out;
    },

    conditionHtml: function(condition, conditionIndex) {
        var parts = [];

        var subjectAction = 'data-action="open-subject-menu" data-item="' + conditionIndex + '"';
        if (condition.subject === null) {
            parts.push(this.placeholderHtml('subject-' + conditionIndex, editorModel.placeholders.subject, subjectAction));
        } else {
            var attribute = vocabulary.attribute(condition.subject);
            var subjectText = this.expressionMode ? condition.subject : attribute.phrase;

            // The path pairs the token with its vocabulary card, so hovering
            // either one lights the other
            parts.push(this.tokenHtml('editor-token-subject', 'subject-' + conditionIndex, subjectText,
                subjectAction + ' data-path="' + condition.subject + '"', false));
        }

        parts.push(this.conditionBodyHtml(condition, conditionIndex));

        var out = '<span class="editor-group" data-group="conditions-' + conditionIndex + '">' +
            parts.join('') + this.removeConditionHtml(conditionIndex) + '</span>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    actionHtml: function(action, listName, actionIndex) {
        var parts = [];
        var actionAttributes = 'data-action="open-action-menu" data-list="' + listName + '" data-item="' + actionIndex + '"';
        var chipName = 'action-' + listName + '-' + actionIndex;

        if (action.target === null) {
            parts.push(this.placeholderHtml(chipName, editorModel.placeholders.action, actionAttributes));
        } else {
            var attribute = vocabulary.attribute(action.target);

            // The path pairs the token with its vocabulary card, so hovering
            // either one lights the other
            var pairedAttributes = actionAttributes + ' data-path="' + action.target + '"';

            if (attribute.type === 'yes/no') {
                var yesNoText = this.expressionMode
                    ? action.target + ' = ' + action.values[0]
                    : 'set ' + attribute.phrase + ' to ' + action.values[0];
                parts.push(this.tokenHtml('editor-token-action', chipName, yesNoText, pairedAttributes, false));
            } else {
                var verbText = this.expressionMode ? action.target + ' =' : 'set ' + attribute.phrase + ' to';
                parts.push(this.tokenHtml('editor-token-action', chipName, verbText, pairedAttributes, false));
                parts.push(this.valueChipHtml(listName, actionIndex, 0, action.values[0], attribute));
            }
        }

        var removeControl = '<span class="editor-group-remove" data-action="remove-action" data-list="' + listName + '"' +
            ' data-item="' + actionIndex + '">' + shared.icon('x', 11) + '</span>';

        var out = '<span class="editor-group" data-group="' + listName + '-' + actionIndex + '">' +
            parts.join('') + removeControl + '</span>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    addChipHtml: function(label, actionAttributes) {
        var out = '<span class="editor-add-chip" ' + actionAttributes + '>' + shared.icon('plus', 10) + label + '</span>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    joinerHtml: function(joinerIndex) {
        var text = editorModel.rule.joiners[joinerIndex];
        var out = '<span class="editor-token editor-token-joiner" data-chip="joiner-' + joinerIndex + '" ' +
            'data-action="toggle-joiner" data-item="' + joinerIndex + '">' + text + '</span>';
        return out;
    },

    // A joiner and the clause it introduces are one wrapping unit - a row
    // never ends with a dangling "and", the next row starts with it instead
    joinedHtml: function(joinerHtml, clauseHtml) {
        var out = '<span class="editor-joined">' + joinerHtml + ' ' + clauseHtml + '</span>';
        return out;
    },

    conditionsHtml: function() {
        var self = this;
        var groups = editorModel.conditionGroups();
        var hasOr = editorModel.hasOrJoiner();
        var groupParts = [];

        groups.forEach(function(group) {
            var memberParts = [];
            group.forEach(function(conditionIndex, positionInGroup) {
                var conditionHtml = self.conditionHtml(editorModel.rule.conditions[conditionIndex], conditionIndex);

                if (positionInGroup > 0) {
                    memberParts.push(self.joinedHtml(self.joinerHtml(conditionIndex - 1), conditionHtml));
                }
                else {
                    memberParts.push(conditionHtml);
                }
            });

            var groupHtml = memberParts.join(' ');
            if (hasOr) {
                var opening = self.expressionMode ? '( ' : '';
                var closing = self.expressionMode ? ' )' : '';
                groupHtml = '<span class="editor-and-group">' + opening + groupHtml + closing + '</span>';
            }
            groupParts.push(groupHtml);
        });

        var out = [];
        groupParts.forEach(function(groupHtml, groupIndex) {
            if (groupIndex > 0) {
                var firstCondition = groups[groupIndex][0];
                out.push(self.joinedHtml(self.joinerHtml(firstCondition - 1), groupHtml));
            }
            else {
                out.push(groupHtml);
            }
        });

        var html = out.join(' ');
        return html;
    },

    emptyHtml: function() {
        if (editorModel.definitionId === null) {
            if (editorModel.config.rulesetsUrl !== '') {
                return '<div class="editor-view-note">No ruleset yet, see <a href="' +
                    editorModel.config.rulesetsUrl + '">rulesets</a>.</div>';
            }
            return '<div class="editor-view-note">No ruleset yet.</div>';
        }

        if (editorModel.config.tablesUrl !== '') {
            return '<div class="editor-view-note">No rules yet, see ' +
                '<a href="' + editorModel.config.tablesUrl + '">the decision tables</a>.</div>';
        }

        var out = '<div class="editor-view-note">No rules yet.</div>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    render: function() {
        var self = this;

        if (editorModel.rule === null) {
            this.element('.editor-area').innerHTML = this.emptyHtml();
            return;
        }

        var rule = editorModel.rule;

        var built = editorModel.buildProblems();
        this.problems = built.problems.concat(editorModel.serverProblems());
        this.invalidKeys = built.invalidKeys;

        if (this.viewMode === 'table' || this.viewMode === 'document') {
            this.element('.editor-area').innerHTML =
                this.viewMode === 'table' ? this.tableViewHtml() : this.documentViewHtml();

            if (this.viewMode === 'document') { this.fillCanonicalText(); }

            this.finishRender();
            return;
        }

        var ifParts = [];
        ifParts.push(this.keywordHtml('if'));
        ifParts.push(this.conditionsHtml());
        ifParts.push(this.addChipHtml(rule.conditions.length === 0 ? 'condition' : 'and', 'data-action="add-condition"'));
        var ifLine = '<div class="editor-line" data-drop="conditions">' + ifParts.join(' ') + '</div>';

        var thenParts = [this.keywordHtml('then')];
        var thenActions = [];
        rule.thenActions.forEach(function(action, actionIndex) {
            var actionHtml = self.actionHtml(action, 'thenActions', actionIndex);
            thenActions.push(actionIndex > 0 ? self.joinedHtml(self.keywordHtml('and'), actionHtml) : actionHtml);
        });
        thenParts.push(thenActions.join(' '));
        thenParts.push(this.addChipHtml(rule.thenActions.length === 0 ? 'action' : 'and',
            'data-action="add-action" data-list="thenActions"'));
        var thenLine = '<div class="editor-line" data-drop="thenActions">' + thenParts.join(' ') + '</div>';

        var elseParts = [];
        if (rule.elseActions.length === 0) {
            elseParts.push(this.addChipHtml('else', 'data-action="add-action" data-list="elseActions"'));
        } else {
            elseParts.push(this.keywordHtml('else'));
            var elseActions = [];
            rule.elseActions.forEach(function(action, actionIndex) {
                var actionHtml = self.actionHtml(action, 'elseActions', actionIndex);
                elseActions.push(actionIndex > 0 ? self.joinedHtml(self.keywordHtml('and'), actionHtml) : actionHtml);
            });
            elseParts.push(elseActions.join(' '));
            elseParts.push(this.addChipHtml('and', 'data-action="add-action" data-list="elseActions"'));
        }
        var elseLine = '<div class="editor-line" data-drop="elseActions">' + elseParts.join(' ') + '</div>';

        var sentenceClass = 'editor-rule-sentence' + (this.expressionMode ? ' editor-expression-mode' : '');
        this.element('.editor-area').innerHTML =
            '<div class="' + sentenceClass + '">' + ifLine + thenLine + elseLine + '</div>';

        this.finishRender();
    },

    finishRender: function() {
        this.renderProblems();
        this.renderVocabulary();
        this.markActiveToken();
        this.attachVocabularyDrag();
        this.attachDropLines();
        this.attachPathHighlight();
        shared.initTips();
        this.scheduleServerCheck();
        this.openPendingChip();
        this.recordHistory();
        this.refreshChangeState();
    },

// ////////////////////////////////////////////////////////////////////////

    // One snapshot per distinct state - a render that changed nothing pushes
    // nothing, and a fresh edit starts a new future, so the redo stack empties
    recordHistory: function() {
        if (!editorModel.config.trackChanges || editorModel.rule === null) { return; }
        if (this.restoringHistory) { return; }

        var stacks = this.historyFor();
        var snapshot = JSON.stringify(editorModel.rule);

        if (stacks.undoStack.length === 0 || stacks.undoStack[stacks.undoStack.length - 1] !== snapshot) {
            stacks.undoStack.push(snapshot);
            stacks.redoStack = [];
        }
    },

    // The dirty state drives everything IDE-like - the working copy in local
    // storage and whatever star the host paints, the Save button stays live
    refreshChangeState: function() {
        if (!editorModel.config.trackChanges || editorModel.rule === null) { return; }

        var isDirty = editorModel.isDirty();

        // The working copy in local storage mirrors the dirty state - an edit
        // writes it, an undo back to the stored state removes it
        if (isDirty) {
            editorModel.writeDraft();
        }
        else {
            editorModel.clearDraft(editorModel.ruleKey);
        }

        if (editorModel.config.onDirtyChange !== null) {
            editorModel.config.onDirtyChange(isDirty, editorModel.rule.name);
        }
    },

// ////////////////////////////////////////////////////////////////////////

    scheduleServerCheck: function() {
        var self = this;

        if (this.checkTimer !== null) { clearTimeout(this.checkTimer); }
        this.checkTimer = setTimeout(function() {
            self.checkTimer = null;
            editorModel.check(function() {
                var built = editorModel.buildProblems();
                self.problems = built.problems.concat(editorModel.serverProblems());
                self.renderProblems();
                editorLive.update();
            }, data.reportError);
        }, editorModel.config.checkDelayMilliseconds);
    },

    openPendingChip: function() {
        var pending = this.autoOpen;
        this.autoOpen = null;
        if (pending !== null) {
            var chip = this.element('[data-chip="' + pending + '"]');
            if (chip !== null) { chip.click(); }
        }
    },

// ////////////////////////////////////////////////////////////////////////

    renderProblems: function() {
        var head = this.element('.problems-head');
        var list = this.element('.problems-list');
        head.textContent = 'Problems (' + this.problems.length + ')';

        if (this.problems.length === 0) {
            list.innerHTML = '<div class="problem-item problem-none">No problems in this rule.</div>';
            return;
        }

        list.innerHTML = this.problems.map(function(problem, problemIndex) {
            var dot = problem.severity === 'error' ? 'status-dot-error' : 'status-dot-information';
            var fixButton = '';
            if (problem.fix !== undefined) {
                fixButton = '<span class="problem-fix" data-action="apply-fix" data-item="' + problemIndex + '">Change to ' +
                    shared.escape(problem.fix.value) + '</span>';
            }
            return '<div class="problem-item"><span class="status-dot ' + dot + '"></span>' +
                '<span>' + shared.escape(problem.text) + '</span>' + fixButton + '</div>';
        }).join('');
    },

// ////////////////////////////////////////////////////////////////////////

    // The paths the rule already speaks of and how many places speak of each -
    // their cards wear a quiet mark telling the count
    usedPaths: function() {
        var used = {};
        if (editorModel.rule === null) { return used; }

        var countPath = function(path) {
            if (path === null) { return; }
            used[path] = used[path] === undefined ? 1 : used[path] + 1;
        };

        editorModel.rule.conditions.forEach(function(condition) {
            countPath(condition.subject);
        });

        editorModel.rule.thenActions.concat(editorModel.rule.elseActions).forEach(function(action) {
            countPath(action.target);
        });

        return used;
    },

    renderVocabulary: function() {
        var list = this.element('.vocabulary-list');

        // The host may not show the vocabulary pane at all
        if (list === null) { return; }

        var used = this.usedPaths();
        var html = '';

        vocabulary.entities.forEach(function(entity) {
            html += '<div class="vocabulary-entity">' + shared.escape(entity.name) + '</div>';
            vocabulary.pickerAttributes(entity).forEach(function(attribute) {
                var path = entity.name + '.' + attribute.name;

                // A circle out in the gutter says the rule already speaks of
                // this attribute - hovering it tells so in as many words,
                // count included
                var dot = used[path] !== undefined
                    ? '<span class="vocabulary-in-rule-dot" data-used-count="' + used[path] + '"></span>'
                    : '';

                html += '<div class="vocabulary-item vocabulary-item-clickable"' +
                    ' draggable="true" data-path="' + path + '" ' +
                    'data-action="pick-vocabulary">' + dot + shared.escape(attribute.name) +
                    '<span class="vocabulary-item-type">' + shared.escape(attribute.type) + '</span></div>';
            });
        });

        list.innerHTML = html;

        // The circles' tooltips go through whatever the host itself uses,
        // each saying its own count - "Used by this rule 2x"
        if (editorModel.config.attachUsedTip !== null) {
            list.querySelectorAll('.vocabulary-in-rule-dot').forEach(function(dotElement) {
                var text = editorModel.config.usedTipText + ' ' + dotElement.getAttribute('data-used-count') + 'x';
                editorModel.config.attachUsedTip(dotElement, text);
            });
        }
    },

// ////////////////////////////////////////////////////////////////////////

    activeToken: -1,

    markActiveToken: function() {
        var tokens = this.elements('.editor-token');
        tokens.forEach(function(token, tokenIndex) {
            token.classList.toggle('editor-token-active', tokenIndex === editorView.activeToken);
        });
    },

    moveToken: function(step) {
        var tokens = this.elements('.editor-token');
        if (tokens.length === 0) { return; }

        this.activeToken = (this.activeToken + step + tokens.length) % tokens.length;
        this.markActiveToken();
        tokens[this.activeToken].scrollIntoView({behavior: 'smooth', block: 'nearest'});
    },

    openActiveToken: function() {
        var tokens = this.elements('.editor-token');
        if (this.activeToken < 0 || this.activeToken >= tokens.length) { return; }
        tokens[this.activeToken].click();
    },
};

window.editorView = editorView;

})();
