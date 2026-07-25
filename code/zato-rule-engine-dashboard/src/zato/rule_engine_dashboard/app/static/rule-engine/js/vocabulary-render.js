'use strict';

// Rendering for the vocabulary screen: the term tree with its filter,
// one term opened into its definition and the where-used list, and the
// rename flow that shows its impact before it commits. Event handlers
// live in vocabulary-actions.js, the right-click menu in
// vocabulary-menu.js, both augment this namespace.

(function() {

var vocabularyView = {

    config: {
        // The tree never materializes more rows than this, no matter how
        // many terms the vocabulary holds: past the cap the filter is the
        // way in, so render cost stops depending on vocabulary size
        maxVisibleTerms: 200,
        // Where a usage entry opens into
        editorUrl: '/editor/',
    },

    // UI state
    filter: '',
    selectedPath: null,

    // The where-used answer for the selected term, fetched on selection
    usage: null,

// ////////////////////////////////////////////////////////////////////////

    render: function() {
        var subtitle = vocabulary.name === ''
            ? 'one definition serves the rules, the tests, the log and the API'
            : vocabulary.name + ' - one definition serves the rules, the tests, the log and the API';
        document.getElementById('main-subtitle').textContent = subtitle;

        this.renderTree();
        this.renderDetail();
        this.renderProblems();
        shared.initTips();
    },

// ////////////////////////////////////////////////////////////////////////

    renderTree: function() {
        var self = this;
        var needle = this.filter.trim().toLowerCase();
        var cap = this.config.maxVisibleTerms;
        var html = '';
        var total = 0;
        var shown = 0;

        vocabulary.entities.forEach(function(entity) {
            var rows = '';
            entity.attributes.forEach(function(attribute) {
                var path = entity.name + '.' + attribute.name;
                if (needle !== '' && (path + ' ' + attribute.phrase).toLowerCase().indexOf(needle) === -1) { return; }

                // Everything is counted, only the capped window is built
                total += 1;
                if (shown >= cap) { return; }
                shown += 1;

                var classes = 'vocabulary-tree-item' + (path === self.selectedPath ? ' vocabulary-tree-item-selected' : '');
                var flag = attribute.status === 'deprecated'
                    ? '<span class="vocabulary-flag" data-tippy-content="Deprecated: existing rules keep running, every picker hides it.">deprecated</span>'
                    : '';

                var pathText = shared.escape(path);

                rows += '<div class="' + classes + '" draggable="true" data-path="' + pathText + '" ' +
                    'onclick="vocabularyView.select(\'' + pathText + '\')">' +
                    '<span class="vocabulary-tree-name">' + shared.escape(attribute.name) + '</span>' + flag +
                    '<span class="vocabulary-item-type">' + shared.escape(attribute.type) + '</span>' +
                    '</div>';
            });

            if (rows !== '') {
                var entityText = shared.escape(entity.name);
                html += '<div class="vocabulary-entity" data-entity="' + entityText + '">' +
                    entityText + '</div>' + rows;
            }
        });

        if (html === '') {
            html = vocabulary.entities.length === 0
                ? '<div class="vocabulary-tree-empty">No vocabulary yet. Add from example above turns one pasted ' +
                  'JSON payload into the first terms.</div>'
                : '<div class="vocabulary-tree-empty">Nothing matches the filter.</div>';
        }
        if (total > shown) {
            html += '<div class="vocabulary-tree-more">Showing the first ' + shown + ' of ' + total +
                ' matching terms, the filter above narrows this down.</div>';
        }
        document.getElementById('vocabulary-tree-count').textContent = total + ' terms';
        document.getElementById('vocabulary-tree-list').innerHTML = html;
    },

// ////////////////////////////////////////////////////////////////////////

    renderDetail: function() {
        var pane = document.getElementById('vocabulary-detail-pane');
        if (this.selectedPath === null) { pane.innerHTML = ''; return; }

        var path = this.selectedPath;
        var attribute = vocabulary.attribute(path);
        var html = '';

        html += this.headHtml(path, attribute);
        html += this.definitionHtml(path, attribute);
        html += this.usageHtml(path, attribute);

        pane.innerHTML = html;
    },

// ////////////////////////////////////////////////////////////////////////

    // The name itself is the rename control, right where the eye already is
    headHtml: function(path, attribute) {
        var flag = attribute.status === 'deprecated'
            ? '<span class="vocabulary-flag" data-tippy-content="Existing rules keep running, every picker hides it.">deprecated</span>' : '';

        var out = '<div class="vocabulary-detail-head">' +
            '<span class="vocabulary-detail-name" onclick="vocabularyView.openRenamePopover(this)" ' +
                'data-tippy-content="Click to rename. Every place it is used updates together, nothing is left behind to break.">' +
                shared.escape(path) + '</span>' + flag +
            '</div>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    definitionHtml: function(path, attribute) {
        var html = '<div class="test-grid-title">Definition</div>';
        html += '<table class="test-grid"><tbody>';

        var row = function(label, field, valueHtml, editable) {
            var editAttributes = editable
                ? ' onclick="vocabularyView.editField(this, \'' + field + '\')" data-tippy-content="Click to edit"' : '';
            var classes = 'test-value-cell' + (editable ? '' : ' log-value-readonly');
            html += '<tr><td class="test-label-cell">' + label + '</td>' +
                '<td class="' + classes + '" data-field="' + field + '"' + editAttributes + '>' + valueHtml + '</td></tr>';
        };

        row('phrase, how rules read it', 'phrase', shared.escape(attribute.phrase), true);
        row('type', 'type', shared.escape(attribute.type), false);

        if (attribute.type === 'choice') {
            row('allowed values, everywhere at once', 'values', shared.escape(attribute.values.join(', ')), true);
        }
        if (attribute.type === 'number range') {
            row('allowed range', 'domain', attribute.domain.low + ' .. ' + attribute.domain.high, true);
        }

        var description = 'description' in attribute ? attribute.description : '';
        row('description', 'description', shared.escape(description), true);

        html += '</tbody></table>';
        html += '<div class="vocabulary-definition-note">The same definition drives the editor dropdowns, the table ' +
            'cells, the scenario forms and the API validation, one change lands everywhere at once.</div>';
        return html;
    },

// ////////////////////////////////////////////////////////////////////////

    // The centerpiece: every place this term lives, grouped by the
    // ruleset it is referenced from, each entry opening the editor with
    // the term highlighted there. Retiring a term lives here too, next
    // to the places it would touch.
    usageHtml: function(path, attribute) {
        var self = this;
        var usage = this.usage;

        if (usage === null) {
            return '<div class="test-grid-title vocabulary-usage-title">Used in ...</div>';
        }

        var deprecateButton = attribute.status === 'deprecated'
            ? '<button class="button-mini" onclick="vocabularyView.restore()" ' +
              'data-tippy-content="Back into every picker.">Restore</button>'
            : '<button class="button-mini" onclick="vocabularyView.deprecate()" ' +
              'data-tippy-content="Existing rules keep running, the term leaves every picker and the API contract. The safe way to retire a term, deleting is only for unused ones.">Deprecate</button>';

        // Delete is gated by the where-used index, never a landmine
        var deleteButton = usage.canDelete
            ? '<button class="button-mini vocabulary-delete-enabled" onclick="vocabularyView.deleteTerm()" ' +
              'data-tippy-content="Nothing uses this term, deleting is safe.">Delete</button>'
            : '<button class="button-mini vocabulary-delete-blocked" onclick="vocabularyView.explainBlockedDelete(this)" ' +
              'data-tippy-content="Blocked: ' + usage.count + ' places listed here still use this term. Deprecate instead, or clear them first.">Delete</button>';

        var html = '<div class="test-grid-title vocabulary-usage-title">Used in ' + usage.count + ' places' +
            '<span class="vocabulary-usage-buttons">' + deprecateButton + deleteButton + '</span></div>';

        if (usage.groups.length === 0) {
            html += '<div class="test-run-note">Nothing uses this term, it can be deleted safely.</div>';
        }

        usage.groups.forEach(function(group) {
            html += '<div class="vocabulary-usage-group">' + shared.escape(group.name) + '</div>';
            group.entries.forEach(function(entry) {
                html += '<a class="vocabulary-usage-entry vocabulary-usage-link" ' +
                    'href="' + self.config.editorUrl + '?ruleset=' + group.definitionId + '#term=' +
                        encodeURIComponent(path) + '" ' +
                    'data-tippy-content="Opens the rule with this term highlighted in it.">' +
                    shared.escape(self.entryText(entry)) + shared.icon('external-link', 10) + '</a>';
            });
        });

        // Deprecated terms leave the API contract too, everything else
        // is a field in the generated endpoint documentation
        if (attribute.status !== 'deprecated') {
            html += '<div class="vocabulary-usage-group">Generated API contract</div>' +
                '<div class="vocabulary-usage-entry">Field ' + shared.escape(path) +
                ' in the endpoint documentation and sample payloads</div>';
        }

        return html;
    },

    // One where-used index entry as the sentence a person reads
    entryText: function(entry) {
        var out = 'Rule ' + entry.rule_name + ', ' + entry.role + ' in its ' + entry.block + ' block';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // Deprecated terms are the problems panel's business: still-used ones
    // are warnings, unused ones are one delete away
    renderProblems: function() {
        var self = this;
        var list = document.getElementById('problems-list');
        var deprecated = [];

        vocabularyModel.allPaths().forEach(function(path) {
            if (vocabulary.attribute(path).status === 'deprecated') { deprecated.push(path); }
        });

        if (deprecated.length === 0) {
            list.innerHTML = '<div class="problem-item problem-none">No problems in the vocabulary.</div>';
            return;
        }

        // Each deprecated term's usage count comes from the index
        var items = [];
        var remaining = deprecated.length;

        deprecated.forEach(function(path) {
            vocabularyModel.whereUsed(path, function(usage) {
                var pathText = shared.escape(path);
                if (usage.count > 0) {
                    items.push('<div class="problem-item"><span class="status-dot status-dot-warning"></span>' +
                        '<span>' + pathText + ' is deprecated but still used in ' + usage.count +
                        ' places, they keep working, move them over when convenient.</span></div>');
                } else {
                    items.push('<div class="problem-item"><span class="status-dot status-dot-information"></span>' +
                        '<span>' + pathText + ' is deprecated and nothing uses it, deleting it is safe.</span></div>');
                }

                remaining -= 1;
                if (remaining === 0) { list.innerHTML = items.join(''); }
            });
        });
    },
};

window.vocabularyView = vocabularyView;

})();
