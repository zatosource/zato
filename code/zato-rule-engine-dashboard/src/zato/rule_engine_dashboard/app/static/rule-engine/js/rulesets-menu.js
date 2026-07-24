'use strict';

// The right-click menu of the rulesets list, the same menu machinery as
// everywhere else. Augments the rulesetsView namespace.

(function() {

// ////////////////////////////////////////////////////////////////////////

rulesetsView.openRowMenu = function(event, id) {
    event.preventDefault();
    var ruleset = rulesetsModel.byId(id);
    var draft = rulesetsModel.draftVersion(ruleset);
    var followed = rulesetsModel.isFollowed(id);
    var self = this;

    var goTo = function(screen) {
        return function() {
            window.location.href = self.config.openUrls[screen] + '?ruleset=' + id;
        };
    };

    var items = [
        {label: 'Open', destructive: false,
            description: 'The decision table of this ruleset.',
            action: function() { self.open(id); }},
        {label: 'Tests and A/B', destructive: false,
            description: 'Scenarios and the A/B view for this ruleset.',
            action: goTo('tests')},
        {label: 'Versions', destructive: false,
            description: 'Its history, drafts and publishing.',
            action: goTo('versions')},
        {label: 'Decision log', destructive: false,
            description: 'Every decision this ruleset answered, searchable.',
            action: goTo('log')},
        null,
    ];

    // Publishing is only ever offered where a draft exists
    if (draft !== null) {
        items.push({label: 'Publish draft v' + draft, destructive: false,
            description: 'A confirmation first, a snapshot is taken and the new version starts answering.',
            action: function() {
                self.openPublishPanel(id,
                    document.querySelector('.rulesets-row[data-id="' + id + '"] .rulesets-publish'));
            }});
    }

    items.push({label: followed ? 'Unfollow' : 'Follow', destructive: false,
        description: followed
            ? 'Stop leading the feed with its changes.'
            : 'Its changes lead the feed on this screen.',
        action: function() { self.toggleFollow(id); }});

    // Marking seen empties the feed of what already happened here
    if (followed) {
        items.push({label: 'Mark seen', destructive: false,
            description: 'Moves the feed clock past everything that already happened to this ruleset.',
            action: function() {
                rulesetsModel.markSeen(id, function() {
                    self.renderSide();
                    shared.initTips();
                });
            }});
    }

    items.push({label: 'Copy name', destructive: false,
        description: 'Copies ' + ruleset.name + '.',
        action: function() {
            navigator.clipboard.writeText(ruleset.name);
            shared.popover(document.querySelector('.rulesets-row[data-id="' + id + '"] .rulesets-open-link'),
                'Copied ' + ruleset.name + '.');
        }});

    shared.openContextMenu(ruleset.name, items, event.clientX, event.clientY);
};

// ////////////////////////////////////////////////////////////////////////

document.getElementById('rulesets-list').addEventListener('contextmenu', function(event) {
    var row = event.target.closest('.rulesets-row');
    if (row === null) { return; }
    rulesetsView.openRowMenu(event, parseInt(row.dataset.id));
});

})();
