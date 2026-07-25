'use strict';

// The rule editor's alternate skins over the same token structure: the
// decision-table grid and the canonical document view. Augments the
// editorView namespace from editor-render.js.

(function() {

// ////////////////////////////////////////////////////////////////////////

// The same rule as a decision-table grid: each or-group of the sentence
// is one rule column, the and-joined conditions inside it are the rows,
// and the cells hold the exact same chips as the sentence, so an edit
// in either view lands in the same stored document
editorView.tableViewHtml = function() {
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
};

// ////////////////////////////////////////////////////////////////////////

// The stored artifact itself: the canonical document the server parsed
// out of the sentence, plus its readable text form. What export gives
// out and what versions snapshot is exactly this.
editorView.documentViewHtml = function() {
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
};

// The canonical text form comes from the server's own renderer, the
// exact inverse of its parser
editorView.fillCanonicalText = function() {
    var target = document.getElementById('editor-canonical-text');
    if (target === null) { return; }

    data.post(editorModel.config.urls.render, {documents: editorModel.serverDocuments}, function(payload) {
        target.textContent = payload.text;
    }, data.reportError);
};

// ////////////////////////////////////////////////////////////////////////

})();
