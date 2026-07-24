'use strict';

// Event handlers for the versions and changes screen: picking versions
// to compare, the view toggles, viewed tracking, anchored comments,
// restore, publish and the approval gate. Augments the versionsView
// namespace from versions-render.js.

(function() {

// ////////////////////////////////////////////////////////////////////////

versionsView.setCompare = function() {
    versionsModel.fromNumber = +document.getElementById('versions-from').value;
    versionsModel.toNumber = +document.getElementById('versions-to').value;

    var self = this;
    versionsModel.compare(function() { self.render(); });
};

// Clicking a timeline entry makes it the older side of the comparison,
// the newer side stays on the version under review
versionsView.pickVersion = function(number) {
    if (number === versionsModel.toNumber) { return; }
    versionsModel.fromNumber = number;

    var self = this;
    versionsModel.compare(function() { self.render(); });
};

// ////////////////////////////////////////////////////////////////////////

versionsView.toggleChangesOnly = function() {
    this.changesOnly = !this.changesOnly;
    document.getElementById('button-changes-only').classList.toggle('toggled', this.changesOnly);
    this.render();
};

versionsView.toggleSplit = function() {
    this.splitView = !this.splitView;
    document.getElementById('button-split-view').classList.toggle('toggled', this.splitView);
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

versionsView.toggleViewed = function(key, isViewed) {
    if (isViewed) {
        versionsModel.viewed[key] = true;
    } else {
        delete versionsModel.viewed[key];
    }
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

// A new comment lands in the store as a review event and comes back
// with the reloaded feed, anchored to the rule it is about
versionsView.addComment = function(button) {
    var self = this;
    var anchor = document.getElementById('versions-comment-anchor').value;
    var text = document.getElementById('versions-comment-text').value.trim();

    if (text === '') {
        shared.popover(button, 'Type the comment first.');
        return;
    }

    var body = {version: versionsModel.toNumber, anchor: anchor, text: text};
    data.post(versionsModel.config.urls.comment(versionsModel.rulesetId), body, function() {
        versionsModel.loadTimeline(function() { self.render(); });
    }, function(message) { shared.popover(button, message, 'red'); });
};

// ////////////////////////////////////////////////////////////////////////

// An approval is immutable and binds to this exact version and the
// content hash of its stored snapshot
versionsView.approve = function(button) {
    var self = this;
    var url = versionsModel.config.urls.approve(versionsModel.rulesetId, versionsModel.toNumber);

    data.post(url, {}, function(payload) {
        shared.popover(button, 'v' + payload.version + ' is approved, bound to its exact content. ' +
            'Publishing it is one click now.', 'green');
        versionsModel.loadTimeline(function() {
            versionsModel.loadApproval(function() { self.render(); });
        });
    }, function(message) { shared.popover(button, message, 'red'); });
};

versionsView.publish = function(button) {
    var self = this;
    var url = versionsModel.config.urls.publish(versionsModel.rulesetId);

    data.post(url, {version: versionsModel.toNumber}, function(payload) {
        shared.popover(button, 'v' + payload.version + ' is live, hot-reloaded without a restart. ' +
            'A snapshot exists, going back is one click on any older version.', 'green');
        versionsModel.loadTimeline(function() {
            versionsModel.loadApproval(function() { self.render(); });
        });
    }, function(message) { shared.popover(button, message, 'red'); });
};

// ////////////////////////////////////////////////////////////////////////

versionsView.setGate = function(button, enabled) {
    var self = this;
    var url = versionsModel.config.urls.setGate(versionsModel.rulesetId);

    data.post(url, {enabled: enabled}, function() {
        versionsModel.loadTimeline(function() {
            versionsModel.loadApproval(function() { self.render(); });
        });
    }, function(message) { shared.popover(button, message, 'red'); });
};

versionsView.setSelfApproval = function(button, allowed) {
    var self = this;
    var url = versionsModel.config.urls.setSelfApproval(versionsModel.rulesetId);

    data.post(url, {allowed: allowed}, function() {
        versionsModel.loadTimeline(function() {
            versionsModel.loadApproval(function() { self.render(); });
        });
    }, function(message) { shared.popover(button, message, 'red'); });
};

// ////////////////////////////////////////////////////////////////////////

// Restore appends a new version built from the old state and publishes
// it - the timeline only ever grows and no version is ever renumbered
versionsView.restore = function(event, number, button) {
    event.stopPropagation();
    var self = this;

    var body = {
        source_version: number,
        expected_current_version: versionsModel.currentVersion,
        comment: versionsModel.config.restoreComment(number),
    };

    data.post(versionsModel.config.urls.rollback(versionsModel.rulesetId), body, function(payload) {
        shared.popover(button, 'Version ' + payload.version + ' was created from v' + number +
            ' and is live. The history stays linear.', 'green');

        // The restored state becomes the newer side of the comparison
        versionsModel.toNumber = payload.version;
        versionsModel.fromNumber = number;
        versionsModel.loadTimeline(function() {
            versionsModel.compare(function() { self.render(); });
        });
    }, function(message) { shared.popover(button, message, 'red'); });
};

// ////////////////////////////////////////////////////////////////////////

shared.initShell();
shared.attachPaneResize(document.getElementById('versions-timeline-resizer'),
    document.getElementById('versions-timeline-pane'), 'x');
document.getElementById('button-split-view').classList.add('toggled');

versionsModel.load(function() {
    if (versionsModel.rulesetId === null) {
        versionsView.render();
        return;
    }
    versionsModel.compare(function() { versionsView.render(); });
});

})();
