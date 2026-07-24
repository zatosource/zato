'use strict';

// The right-click menu of the term tree, the same menu machinery as
// everywhere else. Augments the vocabularyView namespace.

(function() {

// ////////////////////////////////////////////////////////////////////////

vocabularyView.openTermMenu = function(event, path) {
    event.preventDefault();
    var attribute = vocabulary.attribute(path);
    var isDeprecated = attribute.status === 'deprecated';
    var self = this;

    // Selects the term, then opens the in-place editor of one definition
    // field, the same editor a click on the field itself opens
    var editAction = function(field) {
        return function() {
            self.select(path);
            self.editField(document.querySelector('[data-field="' + field + '"]'), field);
        };
    };

    var items = [
        {label: 'Open', destructive: false,
            description: 'Opens this term\'s definition and every place it is used.',
            action: function() { self.select(path); }},
        {label: 'Rename', destructive: false,
            description: 'The impact count is on the button before anything changes, then every place updates together.',
            action: function() {
                self.select(path);
                self.openRenamePopover(document.querySelector('.vocabulary-detail-name'));
            }},
        {label: 'Copy name', destructive: false,
            description: 'Copies ' + path + ', the exact field name of the API contract too.',
            action: function() {
                navigator.clipboard.writeText(path);
                var item = document.querySelector('[data-path="' + path + '"]');
                shared.popover(item, 'Copied ' + path + '.');
            }},
        null,
        {label: 'Change phrase', destructive: false,
            description: 'How the rules read this term, edited in place, every sentence follows.',
            action: editAction('phrase')},
    ];

    if (attribute.type === 'choice') {
        items.push({label: 'Change allowed values', destructive: false,
            description: 'Add, remove or fix the values, one comma-separated list, enforced identically everywhere.',
            action: editAction('values')});
    }
    if (attribute.type === 'number range') {
        items.push({label: 'Change range', destructive: false,
            description: 'The allowed low .. high, enforced identically everywhere.',
            action: editAction('domain')});
    }

    items.push({label: 'Change description', destructive: false,
        description: 'What this term means, for the people after you.',
        action: editAction('description')});

    items.push(null);
    items.push(
        {label: isDeprecated ? 'Restore' : 'Deprecate', destructive: false,
            description: isDeprecated
                ? 'Puts the term back into every picker and the API contract.'
                : 'Existing rules keep running, the term leaves every picker. The safe way to retire a term.',
            action: function() {
                self.select(path);
                if (isDeprecated) { self.restore(); } else { self.deprecate(); }
            }});
    items.push(
        {label: 'Delete', destructive: true,
            description: 'Deleting is gated by the where-used index, only an unused term can go.',
            action: function() {
                self.select(path);
                vocabularyModel.whereUsed(path, function(usage) {
                    if (usage.canDelete) {
                        self.deleteTerm();
                    } else {
                        self.explainBlockedDelete(document.querySelector('.vocabulary-detail-name'));
                    }
                });
            }});

    shared.openContextMenu(path, items, event.clientX, event.clientY);
};

// ////////////////////////////////////////////////////////////////////////

document.getElementById('vocabulary-tree-list').addEventListener('contextmenu', function(event) {
    var item = event.target.closest('.vocabulary-tree-item');
    if (item === null) { return; }
    vocabularyView.openTermMenu(event, item.dataset.path);
});

})();
