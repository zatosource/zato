'use strict';

// Rendering for the rule editor in sentence form. The same token structure
// has two skins: near-natural sentences and the full expression view. The
// table view draws the same rule as a grid and the document view shows the
// canonical stored artifact the server parsed out of the sentence.
// Event handlers live in editor-actions.js, which augments this namespace.

(function() {

var editorView = {

    // UI state. The four views are renderings of the same stored rule
    // document: sentence, expression, table and the document itself.
    viewMode: 'sentence',
    expressionMode: false,
    autoOpen: null,      // data-chip name to click right after the next render
    problems: [],        // last built problem list, for applyFix
    invalidKeys: {},
    menuElement: null,
    menuChoices: [],     // menu items for keyboard navigation
    menuChoice: -1,
    menuIsMulti: false,
    checkTimer: null,    // the debounce behind the server checks

// ////////////////////////////////////////////////////////////////////////

    keywordHtml: function(text) {
        var out = '<span class="editor-keyword">' + text + '</span>';
        return out;
    },

    tokenHtml: function(kindClass, chipName, text, onClick, isInvalid) {
        var classes = 'editor-token ' + kindClass + (isInvalid ? ' editor-token-invalid' : '');
        var out = '<span class="' + classes + '" data-chip="' + chipName + '" onclick="' + onClick + '">' +
            shared.escape(text) + '</span>';
        return out;
    },

    placeholderHtml: function(chipName, text, onClick) {
        var out = '<span class="editor-token editor-token-placeholder" data-chip="' + chipName + '" onclick="' + onClick + '">' +
            shared.escape(text) + '</span>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    valueChipHtml: function(listKey, itemIndex, valueIndex, value, attribute) {
        var chipName = 'value-' + listKey + '-' + itemIndex + '-' + valueIndex;
        var onClick = 'editorView.editValue(event, \'' + listKey + '\', ' + itemIndex + ', ' + valueIndex + ')';

        if (value === '') {
            var out = this.placeholderHtml(chipName, editorModel.valuePlaceholder(attribute), onClick);
            return out;
        }

        var isInvalid = this.invalidKeys[listKey + '-' + itemIndex + '-' + valueIndex] === true;
        var html = this.tokenHtml('editor-token-value', chipName, value, onClick, isInvalid);
        return html;
    },

// ////////////////////////////////////////////////////////////////////////

    // The comparator and value chips of one condition, shared between the
    // sentence rendering and the table rendering: same chips, same handlers,
    // one stored condition behind both
    conditionBodyHtml: function(condition, conditionIndex) {
        var parts = [];

        // The comparator, only offered once a subject exists ..
        if (condition.subject !== null) {
            var comparatorClick = 'editorView.openComparatorMenu(event, ' + conditionIndex + ')';
            if (condition.comparator === null) {
                parts.push(this.placeholderHtml('comparator-' + conditionIndex, editorModel.placeholders.comparator, comparatorClick));
            } else {
                var comparatorText = this.expressionMode
                    ? editorModel.comparatorSymbols[condition.comparator] : condition.comparator;
                parts.push(this.tokenHtml('editor-token-comparator', 'comparator-' + conditionIndex,
                    comparatorText, comparatorClick, false));
            }
        }

        // .. and the values, whose shape follows the comparator.
        if (condition.subject !== null && condition.comparator !== null) {
            var conditionAttribute = vocabulary.attribute(condition.subject);
            var slots = editorModel.valueSlots(condition.comparator);

            if (slots === -1) {
                var setClick = 'editorView.openSetMenu(event, ' + conditionIndex + ')';
                var setChipName = 'value-condition-' + conditionIndex + '-0';
                if (condition.values.length === 0) {
                    parts.push(this.placeholderHtml(setChipName, editorModel.placeholders.set, setClick));
                } else {
                    var setText = this.expressionMode
                        ? '[' + condition.values.join(', ') + ']' : condition.values.join(', ');
                    parts.push(this.tokenHtml('editor-token-value', setChipName, setText, setClick, false));
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
        var out = '<span class="editor-group-remove" data-tippy-content="Remove this condition" ' +
            'onclick="editorView.removeCondition(event, ' + conditionIndex + ')">' + shared.icon('x', 11) + '</span>';
        return out;
    },

    conditionHtml: function(condition, conditionIndex) {
        var parts = [];

        // The subject, or its typed placeholder ..
        var subjectClick = 'editorView.openSubjectMenu(event, ' + conditionIndex + ')';
        if (condition.subject === null) {
            parts.push(this.placeholderHtml('subject-' + conditionIndex, editorModel.placeholders.subject, subjectClick));
        } else {
            var attribute = vocabulary.attribute(condition.subject);
            var subjectText = this.expressionMode ? condition.subject : attribute.phrase;
            parts.push(this.tokenHtml('editor-token-subject', 'subject-' + conditionIndex, subjectText, subjectClick, false));
        }

        // .. then the comparator and values shared with the table rendering.
        parts.push(this.conditionBodyHtml(condition, conditionIndex));

        // The data-group attribute makes this one condition a drop target of its own
        var out = '<span class="editor-group" data-group="conditions-' + conditionIndex + '">' +
            parts.join('') + this.removeConditionHtml(conditionIndex) + '</span>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    actionHtml: function(action, listName, actionIndex) {
        var parts = [];
        var actionClick = 'editorView.openActionMenu(event, \'' + listName + '\', ' + actionIndex + ')';
        var chipName = 'action-' + listName + '-' + actionIndex;

        if (action.target === null) {
            parts.push(this.placeholderHtml(chipName, editorModel.placeholders.action, actionClick));
        } else {
            var attribute = vocabulary.attribute(action.target);

            if (attribute.type === 'yes/no') {
                // A yes/no action is one phrase, e.g. set approved to true
                var yesNoText = this.expressionMode
                    ? action.target + ' = ' + action.values[0]
                    : 'set ' + attribute.phrase + ' to ' + action.values[0];
                parts.push(this.tokenHtml('editor-token-action', chipName, yesNoText, actionClick, false));
            } else {
                // Everything else is a set phrase plus an editable value
                var verbText = this.expressionMode ? action.target + ' =' : 'set ' + attribute.phrase + ' to';
                parts.push(this.tokenHtml('editor-token-action', chipName, verbText, actionClick, false));
                parts.push(this.valueChipHtml(listName, actionIndex, 0, action.values[0], attribute));
            }
        }

        var removeControl = '<span class="editor-group-remove" data-tippy-content="Remove this action" ' +
            'onclick="editorView.removeAction(event, \'' + listName + '\', ' + actionIndex + ')">' + shared.icon('x', 11) + '</span>';

        // The data-group attribute makes this one action a drop target of its own
        var out = '<span class="editor-group" data-group="' + listName + '-' + actionIndex + '">' +
            parts.join('') + removeControl + '</span>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    addChipHtml: function(label, onClick) {
        var out = '<span class="editor-add-chip" onclick="' + onClick + '">' + shared.icon('plus', 10) + label + '</span>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    joinerHtml: function(joinerIndex) {
        var text = editorModel.rule.joiners[joinerIndex];
        var out = '<span class="editor-token editor-token-joiner" data-chip="joiner-' + joinerIndex + '" ' +
            'data-tippy-content="Click to switch between and and or. And binds tighter than or, the boxes show how the conditions group." ' +
            'onclick="editorView.toggleJoiner(' + joinerIndex + ')">' + text + '</span>';
        return out;
    },

    // Conditions render as or-separated groups of and-joined conditions.
    // With any or present, each and-group gets a visible box, and the
    // expression view adds the equivalent parentheses.
    conditionsHtml: function() {
        var self = this;
        var groups = editorModel.conditionGroups();
        var hasOr = editorModel.hasOrJoiner();
        var groupParts = [];

        groups.forEach(function(group) {
            var memberParts = [];
            group.forEach(function(conditionIndex, positionInGroup) {
                if (positionInGroup > 0) { memberParts.push(self.joinerHtml(conditionIndex - 1)); }
                memberParts.push(self.conditionHtml(editorModel.rule.conditions[conditionIndex], conditionIndex));
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
                // The joiner in front of a group's first condition is the or
                var firstCondition = groups[groupIndex][0];
                out.push(self.joinerHtml(firstCondition - 1));
            }
            out.push(groupHtml);
        });

        var html = out.join(' ');
        return html;
    },

    // The same rule as a decision-table grid: each or-group of the sentence
    // is one rule column, the and-joined conditions inside it are the rows,
    // and the cells hold the exact same chips as the sentence, so an edit
    // in either view lands in the same stored document
    tableViewHtml: function() {
        var self = this;
        var rule = editorModel.rule;
        var groups = editorModel.conditionGroups();

        // Rows in order of first appearance: one row per subject, plus one
        // row per still-unfinished condition, which stays editable here too
        var rowKeys = [];
        var rowLabels = {};
        rule.conditions.forEach(function(condition, conditionIndex) {
            var key = condition.subject === null ? 'unfinished-' + conditionIndex : condition.subject;
            if (rowKeys.indexOf(key) > -1) { return; }
            rowKeys.push(key);
            rowLabels[key] = condition.subject === null
                ? self.placeholderHtml('subject-' + conditionIndex, editorModel.placeholders.subject,
                    'editorView.openSubjectMenu(event, ' + conditionIndex + ')')
                : shared.escape(vocabulary.attribute(condition.subject).phrase);
        });

        var columnCount = groups.length;
        var header = '<tr><th class="editor-table-corner">conditions</th>';
        groups.forEach(function(group, groupIndex) {
            header += '<th>' + (groupIndex + 1) + '</th>';
        });
        header += '</tr>';

        var body = '';
        rowKeys.forEach(function(rowKey) {
            body += '<tr><td class="editor-table-label">' + rowLabels[rowKey] + '</td>';

            groups.forEach(function(group) {
                var cellParts = [];
                group.forEach(function(conditionIndex) {
                    var condition = rule.conditions[conditionIndex];
                    var key = condition.subject === null ? 'unfinished-' + conditionIndex : condition.subject;
                    if (key !== rowKey) { return; }

                    cellParts.push('<span class="editor-group" data-group="conditions-' + conditionIndex + '">' +
                        self.conditionBodyHtml(condition, conditionIndex) +
                        self.removeConditionHtml(conditionIndex) + '</span>');
                });

                body += cellParts.length === 0
                    ? '<td class="editor-table-empty">&#183;</td>'
                    : '<td>' + cellParts.join('<br>') + '</td>';
            });

            body += '</tr>';
        });

        // The actions are shared by every column, then fires on the first
        // matching column, else when no column matches
        var thenCells = rule.thenActions.map(function(action, actionIndex) {
            var out = self.actionHtml(action, 'thenActions', actionIndex);
            return out;
        }).join(' ');
        var elseCells = rule.elseActions.map(function(action, actionIndex) {
            var out = self.actionHtml(action, 'elseActions', actionIndex);
            return out;
        }).join(' ');

        body += '<tr class="editor-table-actions"><td class="editor-table-label">then</td>' +
            '<td colspan="' + columnCount + '">' + thenCells + '</td></tr>';
        body += '<tr class="editor-table-actions"><td class="editor-table-label">else</td>' +
            '<td colspan="' + columnCount + '">' + elseCells + '</td></tr>';

        var note = '<div class="editor-view-note">The same stored rule drawn as a grid: each or-group of the ' +
            'sentence is one numbered column, a column matches when all its cells do, the first matching column ' +
            'fires the then actions. Every chip stays editable, an edit here is an edit of the sentence.</div>';

        var out = note + '<table class="editor-table">' + header + body + '</table>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // The stored artifact itself: the canonical document the server parsed
    // out of the sentence, plus its readable text form. What export gives
    // out and what versions snapshot is exactly this.
    documentViewHtml: function() {
        var note = '<div class="editor-view-note">The stored artifact itself: the canonical document the server ' +
            'parses out of the sentence, and above it the readable text form the parser reads back in. ' +
            'The sentence, the expression and the table are renderings of this document, export is this ' +
            'document, and every version is a full snapshot of it.</div>';

        if (editorModel.serverDocuments === null || Object.keys(editorModel.serverDocuments).length === 0) {
            var out = note + '<div class="editor-view-note">The rule needs at least one finished condition ' +
                'and one then action before the server can parse it into a document.</div>';
            return out;
        }

        var html = note + '<pre class="editor-document" id="editor-canonical-text"></pre>' +
            '<pre class="editor-document">' +
            shared.escape(JSON.stringify(editorModel.serverDocuments, null, 2)) + '</pre>';
        return html;
    },

    // The canonical text form comes from the server's own renderer, the
    // exact inverse of its parser
    fillCanonicalText: function() {
        var target = document.getElementById('editor-canonical-text');
        if (target === null) { return; }

        data.post(editorModel.config.urls.render, {documents: editorModel.serverDocuments}, function(payload) {
            target.textContent = payload.text;
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    // The screen without a ruleset or without any rule to edit
    emptyHtml: function() {
        if (editorModel.definitionId === null) {
            return '<div class="editor-view-note">There is no ruleset yet. ' +
                '<a href="/rulesets/">The rulesets screen</a> is where one starts.</div>';
        }

        var out = '<div class="editor-view-note">This ruleset has no rules yet. ' +
            'A rule arrives through <a href="/tables/?ruleset=' + editorModel.definitionId + '">its decision table</a> ' +
            'or through the vocabulary screen\'s add-from-rules panel.</div>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    render: function() {
        var self = this;

        if (editorModel.rule === null) {
            document.getElementById('editor-area').innerHTML = this.emptyHtml();
            return;
        }

        var rule = editorModel.rule;

        // Build the local problems first, the value chips need the invalid keys
        var built = editorModel.buildProblems();
        this.problems = built.problems.concat(editorModel.serverProblems());
        this.invalidKeys = built.invalidKeys;

        // The table and document views replace the sentence wholesale,
        // everything else on the screen stays the same
        if (this.viewMode === 'table' || this.viewMode === 'document') {
            document.getElementById('editor-area').innerHTML =
                this.viewMode === 'table' ? this.tableViewHtml() : this.documentViewHtml();

            if (this.viewMode === 'document') { this.fillCanonicalText(); }

            this.finishRender();
            return;
        }

        // Each line is a drop target for vocabulary attributes, see editor-drag.js
        var ifParts = [];
        ifParts.push(this.keywordHtml('if'));
        ifParts.push(this.conditionsHtml());
        ifParts.push(this.addChipHtml(rule.conditions.length === 0 ? 'condition' : 'and', 'editorView.addCondition()'));
        var ifLine = '<div class="editor-line" data-drop="conditions">' + ifParts.join(' ') + '</div>';

        var thenParts = [this.keywordHtml('then')];
        var thenActions = [];
        rule.thenActions.forEach(function(action, actionIndex) {
            thenActions.push(self.actionHtml(action, 'thenActions', actionIndex));
        });
        thenParts.push(thenActions.join(' ' + this.keywordHtml('and') + ' '));
        thenParts.push(this.addChipHtml(rule.thenActions.length === 0 ? 'action' : 'and', 'editorView.addAction(\'thenActions\')'));
        var thenLine = '<div class="editor-line" data-drop="thenActions">' + thenParts.join(' ') + '</div>';

        var elseParts = [];
        if (rule.elseActions.length === 0) {
            elseParts.push(this.addChipHtml('else', 'editorView.addAction(\'elseActions\')'));
        } else {
            elseParts.push(this.keywordHtml('else'));
            var elseActions = [];
            rule.elseActions.forEach(function(action, actionIndex) {
                elseActions.push(self.actionHtml(action, 'elseActions', actionIndex));
            });
            elseParts.push(elseActions.join(' ' + this.keywordHtml('and') + ' '));
            elseParts.push(this.addChipHtml('and', 'editorView.addAction(\'elseActions\')'));
        }
        var elseLine = '<div class="editor-line" data-drop="elseActions">' + elseParts.join(' ') + '</div>';

        var sentenceClass = 'editor-rule-sentence' + (this.expressionMode ? ' editor-expression-mode' : '');
        document.getElementById('editor-area').innerHTML =
            '<div class="' + sentenceClass + '">' + ifLine + thenLine + elseLine + '</div>';

        this.finishRender();
    },

    finishRender: function() {
        this.renderProblems();
        this.renderVocabulary();
        this.markActiveToken();
        this.attachVocabularyDrag();
        this.attachDropLines();
        shared.initTips();
        this.scheduleServerCheck();
        this.openPendingChip();
    },

// ////////////////////////////////////////////////////////////////////////

    // Every edit re-runs the server checks after a short pause: the parse
    // and semantic errors land in the problems panel and the live outcomes
    // panel re-runs the test set against the rule as it stands right now
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
            });
        }, editorModel.config.checkDelayMilliseconds);
    },

    // The guided completion chain: after a pick, the next menu opens by itself
    openPendingChip: function() {
        var pending = this.autoOpen;
        this.autoOpen = null;
        if (pending !== null) {
            var chip = document.querySelector('[data-chip="' + pending + '"]');
            if (chip !== null) { chip.click(); }
        }
    },

// ////////////////////////////////////////////////////////////////////////

    renderProblems: function() {
        var head = document.getElementById('problems-head');
        var list = document.getElementById('problems-list');
        head.textContent = 'Problems (' + this.problems.length + ')';

        if (this.problems.length === 0) {
            list.innerHTML = '<div class="problem-item problem-none">No problems. ' +
                'The rule is checked continuously as you write it, never on save.</div>';
            return;
        }

        list.innerHTML = this.problems.map(function(problem, problemIndex) {
            var dot = problem.severity === 'error' ? 'status-dot-error' : 'status-dot-information';
            var fixButton = '';
            if (problem.fix !== undefined) {
                fixButton = '<span class="problem-fix" onclick="editorView.applyFix(' + problemIndex + ')">Change to ' +
                    shared.escape(problem.fix.value) + '</span>';
            }
            return '<div class="problem-item"><span class="status-dot ' + dot + '"></span>' +
                '<span>' + shared.escape(problem.text) + '</span>' + fixButton + '</div>';
        }).join('');
    },

// ////////////////////////////////////////////////////////////////////////

    renderVocabulary: function() {
        var html = '';

        vocabulary.entities.forEach(function(entity) {
            html += '<div class="vocabulary-entity">' + shared.escape(entity.name) + '</div>';
            vocabulary.pickerAttributes(entity).forEach(function(attribute) {
                var path = entity.name + '.' + attribute.name;
                html += '<div class="vocabulary-item vocabulary-item-clickable" draggable="true" data-path="' + path + '" ' +
                    'onclick="editorView.pickVocabulary(\'' + path + '\')">' + shared.escape(attribute.name) +
                    '<span class="vocabulary-item-type">' + shared.escape(attribute.type) + '</span></div>';
            });
        });

        document.getElementById('vocabulary-list').innerHTML = html;
    },

// ////////////////////////////////////////////////////////////////////////

    // Arrows walk every token, placeholders included, Enter or ArrowDown
    // opens the one in focus
    activeToken: -1,

    markActiveToken: function() {
        var tokens = document.querySelectorAll('.editor-token');
        tokens.forEach(function(token, tokenIndex) {
            token.classList.toggle('editor-token-active', tokenIndex === editorView.activeToken);
        });
    },

    moveToken: function(step) {
        var tokens = document.querySelectorAll('.editor-token');
        if (tokens.length === 0) { return; }

        this.activeToken = (this.activeToken + step + tokens.length) % tokens.length;
        this.markActiveToken();
        tokens[this.activeToken].scrollIntoView({behavior: 'smooth', block: 'nearest'});
    },

    openActiveToken: function() {
        var tokens = document.querySelectorAll('.editor-token');
        if (this.activeToken < 0 || this.activeToken >= tokens.length) { return; }
        tokens[this.activeToken].click();
    },
};

window.editorView = editorView;

})();
