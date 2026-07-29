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

    if (editorModel.serverDocuments === null || Object.keys(editorModel.serverDocuments).length === 0) {
        var out = '<div class="editor-view-note">No finished rule yet.</div>';
        return out;
    }

    var html = '<pre class="editor-document" id="editor-canonical-text"></pre>' +
        '<pre class="editor-document">' +
        shared.escape(JSON.stringify(editorModel.serverDocuments, null, 2)) + '</pre>';
    return html;
};

editorView.fillCanonicalText = function() {
    var target = document.getElementById('editor-canonical-text');
    if (target === null) { return; }

    data.post(editorModel.config.urls.render, {documents: editorModel.serverDocuments}, function(payload) {
        target.textContent = payload.text;
    }, data.reportError);
};

// ////////////////////////////////////////////////////////////////////////

})();
