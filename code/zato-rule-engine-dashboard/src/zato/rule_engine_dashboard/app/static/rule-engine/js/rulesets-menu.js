'use strict';

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
            action: function() { self.open(id); }},
        {label: 'Tests and A/B', destructive: false,
            action: goTo('tests')},
        {label: 'Versions', destructive: false,
            action: goTo('versions')},
        {label: 'Decision log', destructive: false,
            action: goTo('log')},
        null,
    ];

    if (draft !== null) {
        items.push({label: 'Publish draft v' + draft, destructive: false,
            action: function() {
                self.openPublishPanel(id,
                    document.querySelector('.rulesets-row[data-id="' + id + '"] .rulesets-publish'));
            }});
    }

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

    items.push({label: 'Copy name', destructive: false,
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
