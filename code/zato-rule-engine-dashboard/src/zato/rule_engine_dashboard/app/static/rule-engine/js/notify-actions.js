'use strict';

// Event handlers for the notifications screen: the ruleset switch, the
// live target picker, adding and removing destinations, saving and
// testing credentials, and the event matrix panel. Augments the
// notifyView namespace from notify-render.js.

(function() {

// ////////////////////////////////////////////////////////////////////////

notifyView.setRuleset = function(select) {
    var record = notifyModel.rulesets.filter(function(item) { return item.id === +select.value; })[0];
    notifyModel.rulesetId = record.id;
    notifyModel.rulesetName = record.name;

    notifyModel.loadDestinations(function() { notifyView.render(); });
};

// ////////////////////////////////////////////////////////////////////////

// Choosing the platform asks it for its channels right away - the picker
// only ever offers channels that exist right now
notifyView.setAddKind = function(select) {
    var self = this;

    if (select.value === '') {
        this.addKind = null;
        notifyModel.targets = [];
        this.renderDestinations();
        shared.initTips();
        return;
    }

    this.addKind = select.value;
    this.isLoadingTargets = true;
    this.renderDestinations();
    shared.initTips();

    notifyModel.loadTargets(this.addKind, function() {
        self.isLoadingTargets = false;
        self.renderDestinations();
        shared.initTips();
    }, function(message) {
        self.isLoadingTargets = false;
        self.renderDestinations();
        shared.initTips();
        shared.popover(document.getElementById('notify-add-kind'), message, 'red');
    });
};

notifyView.addDestination = function(anchor) {
    var self = this;
    var target = document.getElementById('notify-add-target').value;

    if (this.addKind === null || target === '') {
        shared.popover(anchor, 'Pick the platform and one of its channels first.', 'red');
        return;
    }

    notifyModel.addDestination(this.addKind, target, function() {
        self.render();
    }, function(message) { shared.popover(anchor, message, 'red'); });
};

notifyView.deleteDestination = function(destinationId) {
    var self = this;
    notifyModel.deleteDestination(destinationId, function() { self.render(); });
};

// ////////////////////////////////////////////////////////////////////////

// Saving reads the card's inputs and clears them on success - the values
// never linger on the screen once they are stored
notifyView.saveCredentials = function(anchor, kind) {
    var self = this;
    var values = {};

    notifyModel.config.credentialFields[kind].forEach(function(field) {
        values[field.name] = document.getElementById('notify-field-' + kind + '-' + field.name).value.trim();
    });

    notifyModel.saveCredentials(kind, values, function() {
        self.render();
        shared.popover(document.getElementById('notify-credentials-pane'),
            notifyModel.config.kindLabels[kind] + ' credentials stored, encrypted at rest.', 'green');
    }, function(message) { shared.popover(anchor, message, 'red'); });
};

notifyView.sendTest = function(anchor, kind) {
    var target = document.getElementById('notify-test-' + kind).value.trim();

    if (target === '') {
        shared.popover(anchor, 'Name the channel the test message goes to.', 'red');
        return;
    }

    notifyModel.sendTest(kind, target, function() {
        shared.popover(anchor, 'Delivered to ' + target + ' - the credentials work.', 'green');
    }, function(message) { shared.popover(anchor, message, 'red'); });
};

// ////////////////////////////////////////////////////////////////////////

// The event matrix, a read-only panel anchored to its toolbar button:
// every event a destination hears about, each with a lived-in example
notifyView.panelElement = null;

notifyView.closePanel = function() {
    if (this.panelElement === null) { return; }
    this.panelElement.remove();
    this.panelElement = null;
};

notifyView.openMatrix = function(button) {
    if (this.panelElement !== null) { this.closePanel(); return; }
    var self = this;

    notifyModel.loadMatrix(function() {
        var html = '<div class="log-capture-title">What destinations are told about</div>';

        notifyModel.matrix.forEach(function(entry) {
            html += '<div class="notify-matrix-item">' +
                '<div class="notify-matrix-name">' + shared.escape(entry.name) + '</div>' +
                '<div class="notify-matrix-description">' + shared.escape(entry.description) + '</div>' +
                '<div class="notify-matrix-example">' + shared.escape(entry.example) + '</div>' +
                '</div>';
        });

        html += '<div class="log-capture-hint">The matrix is fixed - every destination of a ruleset hears ' +
            'about every event here, there is nothing to subscribe to or opt out of.</div>';

        var panel = document.createElement('div');
        panel.className = 'log-capture-panel notify-matrix-panel';
        panel.innerHTML = html;

        document.body.appendChild(panel);
        var rectangle = button.getBoundingClientRect();
        panel.style.top = (rectangle.bottom + 6) + 'px';
        panel.style.left = Math.min(rectangle.left, window.innerWidth - panel.offsetWidth - 8) + 'px';
        self.panelElement = panel;
    });
};

// ////////////////////////////////////////////////////////////////////////

shared.initShell();

// The credentials pane is rendered into the page for admins alone,
// its presence is what tells the model who it works for
notifyModel.isAdmin = document.getElementById('notify-credentials-pane') !== null;

notifyModel.load(function() { notifyView.render(); });

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') { notifyView.closePanel(); }
});

// A click anywhere else closes the open panel, the button itself toggles
// it in its own click handler
document.addEventListener('mousedown', function(event) {
    if (notifyView.panelElement === null) { return; }
    if (event.target.closest('.toolbar .button-ghost') !== null) { return; }
    if (!notifyView.panelElement.contains(event.target)) { notifyView.closePanel(); }
});

})();
