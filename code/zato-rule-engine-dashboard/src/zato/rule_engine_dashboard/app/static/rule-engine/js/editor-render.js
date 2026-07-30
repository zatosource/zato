'use strict';

(function() {

var editorView = {

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

    conditionBodyHtml: function(condition, conditionIndex) {
        var parts = [];

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
        var out = '<span class="editor-group-remove" onclick="editorView.removeCondition(event, ' + conditionIndex + ')">' + shared.icon('x', 11) + '</span>';
        return out;
    },

    conditionHtml: function(condition, conditionIndex) {
        var parts = [];

        var subjectClick = 'editorView.openSubjectMenu(event, ' + conditionIndex + ')';
        if (condition.subject === null) {
            parts.push(this.placeholderHtml('subject-' + conditionIndex, editorModel.placeholders.subject, subjectClick));
        } else {
            var attribute = vocabulary.attribute(condition.subject);
            var subjectText = this.expressionMode ? condition.subject : attribute.phrase;
            parts.push(this.tokenHtml('editor-token-subject', 'subject-' + conditionIndex, subjectText, subjectClick, false));
        }

        parts.push(this.conditionBodyHtml(condition, conditionIndex));

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
                var yesNoText = this.expressionMode
                    ? action.target + ' = ' + action.values[0]
                    : 'set ' + attribute.phrase + ' to ' + action.values[0];
                parts.push(this.tokenHtml('editor-token-action', chipName, yesNoText, actionClick, false));
            } else {
                var verbText = this.expressionMode ? action.target + ' =' : 'set ' + attribute.phrase + ' to';
                parts.push(this.tokenHtml('editor-token-action', chipName, verbText, actionClick, false));
                parts.push(this.valueChipHtml(listName, actionIndex, 0, action.values[0], attribute));
            }
        }

        var removeControl = '<span class="editor-group-remove" onclick="editorView.removeAction(event, \'' + listName + '\', ' + actionIndex + ')">' + shared.icon('x', 11) + '</span>';

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
            'onclick="editorView.toggleJoiner(' + joinerIndex + ')">' + text + '</span>';
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
                var firstCondition = groups[groupIndex][0];
                out.push(self.joinerHtml(firstCondition - 1));
            }
            out.push(groupHtml);
        });

        var html = out.join(' ');
        return html;
    },

    emptyHtml: function() {
        if (editorModel.definitionId === null) {
            return '<div class="editor-view-note">No ruleset yet, see <a href="/rulesets/">rulesets</a>.</div>';
        }

        var out = '<div class="editor-view-note">No rules yet, see ' +
            '<a href="/tables/">the decision tables</a>.</div>';
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

        var built = editorModel.buildProblems();
        this.problems = built.problems.concat(editorModel.serverProblems());
        this.invalidKeys = built.invalidKeys;

        if (this.viewMode === 'table' || this.viewMode === 'document') {
            document.getElementById('editor-area').innerHTML =
                this.viewMode === 'table' ? this.tableViewHtml() : this.documentViewHtml();

            if (this.viewMode === 'document') { this.fillCanonicalText(); }

            this.finishRender();
            return;
        }

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
            list.innerHTML = '<div class="problem-item problem-none">No problems in this rule.</div>';
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
