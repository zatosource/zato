'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

editorView.tableViewHtml = function() {
    var self = this;
    var rule = editorModel.rule;
    var groups = editorModel.conditionGroups();

    var rowKeys = [];
    var rowLabels = {};
    rule.conditions.forEach(function(condition, conditionIndex) {
        var key = condition.subject === null ? 'unfinished-' + conditionIndex : condition.subject;
        if (rowKeys.indexOf(key) > -1) { return; }
        rowKeys.push(key);
        rowLabels[key] = condition.subject === null
            ? self.placeholderHtml('subject-' + conditionIndex, editorModel.placeholders.subject,
                'data-action="open-subject-menu" data-item="' + conditionIndex + '"')
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

    var out = '<table class="editor-table">' + header + body + '</table>';
    return out;
};

// ////////////////////////////////////////////////////////////////////////

editorView.documentViewHtml = function() {

    // The editable flavour is two surfaces in one place - the highlighted face
    // underneath and a transparent textarea over it that does the typing -
    // with the caret's line and column read out underneath
    if (editorModel.config.documentEditable) {
        var out = '<div class="editor-document-host">' +
            '<div class="editor-document-edit">' +
            '<pre class="editor-document editor-canonical-text" aria-hidden="true"></pre>' +
            '<textarea class="editor-document-input" spellcheck="false" wrap="off"></textarea>' +
            '</div>' +
            '<div class="editor-document-status"><span class="editor-document-position"></span></div>' +
            '</div>';
        return out;
    }

    // The text itself is filled in once the pane is on the screen
    var html = '<pre class="editor-document editor-canonical-text"></pre>';
    return html;
};

editorView.fillCanonicalText = function() {
    var target = this.element('.editor-canonical-text');
    if (target === null) { return; }

    // A host with a tokenizer gets the text painted, one without keeps it plain
    var paint = function(text) {
        if (editorModel.config.documentTextHtml === null) {
            target.textContent = text;
        }
        else {
            target.innerHTML = editorModel.config.documentTextHtml(text);
        }
    };

    // The editable flavour works on the rule's own text, no server form needed
    if (editorModel.config.documentEditable) {
        var input = this.element('.editor-document-input');
        var text = editorModel.toText();
        input.value = text;
        paint(text);
        this.bindDocumentInput(input, paint);
        return;
    }

    // Without a server-side form - the rule may be incomplete or no check may
    // have run yet, straight off a bookmark - the rule's own text stands in
    if (editorModel.serverDocuments === null || Object.keys(editorModel.serverDocuments).length === 0) {
        paint(editorModel.toText());
        return;
    }

    data.post(editorModel.config.urls.render, {documents: editorModel.serverDocuments}, function(payload) {
        paint(payload.text);
    }, data.reportError);
};

// ////////////////////////////////////////////////////////////////////////

// Typing repaints the highlighted face at once and, after the same pause every
// other check waits, sends the text to the server to become the rule
editorView.bindDocumentInput = function(input, paint) {
    var self = this;
    var position = this.element('.editor-document-position');

    // Where the caret stands - everything before it, split into lines, says
    // which line it is on and how far into that line it got
    var updatePosition = function() {
        var upToCaret = input.value.slice(0, input.selectionStart);
        var lines = upToCaret.split('\n');
        var column = lines[lines.length - 1].length + 1;
        position.textContent = 'Ln ' + lines.length + ', Col ' + column;
    };

    updatePosition();

    input.addEventListener('input', function() {
        paint(input.value);
        updatePosition();
        self.scheduleDocumentParse(input);
    });

    ['click', 'keyup', 'select'].forEach(function(name) {
        input.addEventListener(name, updatePosition);
    });

    // The face follows the textarea wherever it scrolls - they are one surface
    input.addEventListener('scroll', function() {
        var face = self.element('.editor-canonical-text');
        face.scrollTop = input.scrollTop;
        face.scrollLeft = input.scrollLeft;
    });
};

editorView.scheduleDocumentParse = function(input) {
    var self = this;

    // The typed text supersedes the rule - a check of the rule's old form
    // still waiting its turn would only overwrite this parse's findings
    if (this.checkTimer !== null) { clearTimeout(this.checkTimer); this.checkTimer = null; }

    if (this.parseTimer !== null) { clearTimeout(this.parseTimer); }

    this.parseTimer = setTimeout(function() {
        self.parseTimer = null;

        editorModel.parseText(input.value, function() {

            // The problems, the dirty state and the history follow the parse -
            // the view itself stays put, the user is still typing in it
            var built = editorModel.buildProblems();
            self.problems = built.problems.concat(editorModel.serverProblems());
            self.invalidKeys = built.invalidKeys;
            self.renderProblems();
            self.recordHistory();
            self.refreshChangeState();
            editorLive.update();
        }, data.reportError);
    }, editorModel.config.checkDelayMilliseconds);
};

// ////////////////////////////////////////////////////////////////////////

})();
