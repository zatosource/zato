'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

rulesetsView.openRowMenu = function(event, id) {
    event.preventDefault();
    var ruleset = rulesetsModel.byId(id);
    var draft = rulesetsModel.draftVersion(ruleset);
    var self = this;

    var goTo = function(screen) {
        return function() {
            window.location.href = self.config.openUrls[screen] + '?ruleset=' + id;
        };
    };

    var items = [
        {label: 'Open', destructive: false,
            action: function() { self.open(id); }},
    ];

    // The screens beyond the editor show only when the host has them
    if (this.config.openUrls.tests !== undefined) {
        items.push({label: 'Tests and A/B', destructive: false, action: goTo('tests')});
    }
    if (this.config.openUrls.versions !== undefined) {
        items.push({label: 'Versions', destructive: false, action: goTo('versions')});
    }
    if (this.config.openUrls.log !== undefined) {
        items.push({label: 'Decision log', destructive: false, action: goTo('log')});
    }

    items.push(null);

    if (this.config.showPublish && draft !== null) {
        items.push({label: 'Publish draft v' + draft, destructive: false,
            action: function() {
                self.openPublishPanel(id,
                    self.element('.rulesets-row[data-id="' + id + '"] .rulesets-publish'));
            }});
    }

    if (this.config.showFollows) {
        var followed = rulesetsModel.isFollowed(id);

        items.push({label: followed ? 'Unfollow' : 'Follow', destructive: false,
            action: function() { self.toggleFollow(id); }});

        if (followed) {
            items.push({label: 'Mark seen', destructive: false,
                action: function() {
                    rulesetsModel.markSeen(id, function() {
                        self.renderSide();
                        shared.initTips();
                    });
                }});
        }
    }

    if (this.config.showRename) {
        items.push({label: 'Rename', destructive: false,
            action: function() {
                self.openRenamePanel(id,
                    self.element('.rulesets-row[data-id="' + id + '"] .rulesets-open-link'));
            }});
    }

    items.push({label: 'Copy name', destructive: false,
        action: function() {
            navigator.clipboard.writeText(ruleset.name);
            shared.popover(self.element('.rulesets-row[data-id="' + id + '"] .rulesets-open-link'),
                'Copied ' + ruleset.name + '.');
        }});

    shared.openContextMenu(ruleset.name, items, event.clientX, event.clientY);
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.initMenu = function() {
    var self = this;

    this.element('#rulesets-list').addEventListener('contextmenu', function(event) {
        var row = event.target.closest('.rulesets-row');
        if (row === null) { return; }
        self.openRowMenu(event, parseInt(row.dataset.id));
    });
};

// ////////////////////////////////////////////////////////////////////////

})();
