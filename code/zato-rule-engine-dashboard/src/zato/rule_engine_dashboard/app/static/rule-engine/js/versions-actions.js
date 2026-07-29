'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

versionsView.setCompare = function() {
    versionsModel.fromNumber = +document.getElementById('versions-from').value;
    versionsModel.toNumber = +document.getElementById('versions-to').value;

    var self = this;
    versionsModel.compare(function() { self.render(); });
};

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

versionsView.addComment = function(button) {
    var self = this;
    var anchor = document.getElementById('versions-comment-anchor').value;
    var text = document.getElementById('versions-comment-text').value.trim();

    if (text === '') {
        shared.popover(button, 'Type the comment first.');
        return;
    }

    var handlers = shared.inFlight(button, function() {
        versionsModel.loadTimeline(function() { self.render(); });
    }, function(message) { shared.popover(button, message, 'red'); });
    if (handlers === null) { return; }

    var body = {version: versionsModel.toNumber, anchor: anchor, text: text};
    data.post(versionsModel.config.urls.comment(versionsModel.rulesetId), body, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

versionsView.approve = function(button) {
    var self = this;
    var url = versionsModel.config.urls.approve(versionsModel.rulesetId, versionsModel.toNumber);

    var handlers = shared.inFlight(button, function(payload) {
        shared.popover(button, 'v' + payload.version + ' is approved.', 'green');
        versionsModel.loadTimeline(function() {
            versionsModel.loadApproval(function() { self.render(); });
        });
    }, function(message) { shared.popover(button, message, 'red'); });
    if (handlers === null) { return; }

    data.post(url, {}, handlers.done, handlers.error);
};

versionsView.publish = function(button) {
    var self = this;
    var url = versionsModel.config.urls.publish(versionsModel.rulesetId);

    var handlers = shared.inFlight(button, function(payload) {
        shared.popover(button, 'v' + payload.version + ' is live.', 'green');
        versionsModel.loadTimeline(function() {
            versionsModel.loadApproval(function() { self.render(); });
        });
    }, function(message) { shared.popover(button, message, 'red'); });
    if (handlers === null) { return; }

    data.post(url, {version: versionsModel.toNumber}, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

versionsView.setGate = function(button, enabled) {
    var self = this;
    var url = versionsModel.config.urls.setGate(versionsModel.rulesetId);

    var handlers = shared.inFlight(button, function() {
        versionsModel.loadTimeline(function() {
            versionsModel.loadApproval(function() { self.render(); });
        });
    }, function(message) { shared.popover(button, message, 'red'); });
    if (handlers === null) { return; }

    data.post(url, {enabled: enabled}, handlers.done, handlers.error);
};

versionsView.setSelfApproval = function(button, allowed) {
    var self = this;
    var url = versionsModel.config.urls.setSelfApproval(versionsModel.rulesetId);

    var handlers = shared.inFlight(button, function() {
        versionsModel.loadTimeline(function() {
            versionsModel.loadApproval(function() { self.render(); });
        });
    }, function(message) { shared.popover(button, message, 'red'); });
    if (handlers === null) { return; }

    data.post(url, {allowed: allowed}, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

versionsView.restore = function(event, number, button) {
    event.stopPropagation();
    var self = this;

    var body = {
        source_version: number,
        expected_current_version: versionsModel.currentVersion,
        comment: versionsModel.config.restoreComment(number),
    };

    var handlers = shared.inFlight(button, function(payload) {
        shared.popover(button, 'Version ' + payload.version + ' was created from v' + number +
            ' and is live. The history stays linear.', 'green');

        versionsModel.toNumber = payload.version;
        versionsModel.fromNumber = number;
        versionsModel.loadTimeline(function() {
            versionsModel.compare(function() { self.render(); });
        });
    }, function(message) { shared.popover(button, message, 'red'); });
    if (handlers === null) { return; }

    data.post(versionsModel.config.urls.rollback(versionsModel.rulesetId), body, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

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
