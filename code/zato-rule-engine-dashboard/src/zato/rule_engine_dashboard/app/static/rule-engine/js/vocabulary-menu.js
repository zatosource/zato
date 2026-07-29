'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

vocabularyView.openTermMenu = function(event, path) {
    event.preventDefault();
    var attribute = vocabulary.attribute(path);
    var isDeprecated = attribute.status === 'deprecated';
    var self = this;

    var editAction = function(field) {
        return function() {
            self.select(path);
            self.editField(document.querySelector('[data-field="' + field + '"]'), field);
        };
    };

    var items = [
        {label: 'Open', destructive: false,
            action: function() { self.select(path); }},
        {label: 'Rename', destructive: false,
            action: function() {
                self.select(path);
                self.openRenamePopover(document.querySelector('.vocabulary-detail-name'));
            }},
        {label: 'Copy name', destructive: false,
            action: function() {
                navigator.clipboard.writeText(path);
                var item = document.querySelector('[data-path="' + path + '"]');
                shared.popover(item, 'Copied ' + path + '.');
            }},
        null,
        {label: 'Change phrase', destructive: false,
            action: editAction('phrase')},
    ];

    if (attribute.type === 'choice') {
        items.push({label: 'Change allowed values', destructive: false,
            action: editAction('values')});
    }
    if (attribute.type === 'number range') {
        items.push({label: 'Change range', destructive: false,
            action: editAction('domain')});
    }

    items.push({label: 'Change description', destructive: false,
        action: editAction('description')});

    items.push(null);
    items.push(
        {label: isDeprecated ? 'Restore' : 'Deprecate', destructive: false,
            action: function() {
                self.select(path);
                if (isDeprecated) { self.restore(); } else { self.deprecate(); }
            }});
    items.push(
        {label: 'Delete', destructive: true,
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
