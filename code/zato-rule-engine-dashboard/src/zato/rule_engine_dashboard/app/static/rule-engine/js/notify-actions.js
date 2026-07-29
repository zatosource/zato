'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

notifyView.setRuleset = function(select) {
    var record = notifyModel.rulesets.filter(function(item) { return item.id === +select.value; })[0];
    notifyModel.rulesetId = record.id;
    notifyModel.rulesetName = record.name;

    notifyModel.loadDestinations(function() { notifyView.render(); });
};

// ////////////////////////////////////////////////////////////////////////

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

    var handlers = shared.inFlight(anchor, function() {
        self.render();
    }, function(message) { shared.popover(anchor, message, 'red'); });
    if (handlers === null) { return; }

    notifyModel.addDestination(this.addKind, target, handlers.done, handlers.error);
};

notifyView.deleteDestination = function(destinationId) {
    var self = this;
    notifyModel.deleteDestination(destinationId, function() { self.render(); });
};

// ////////////////////////////////////////////////////////////////////////

notifyView.saveCredentials = function(anchor, kind) {
    var self = this;
    var values = {};

    notifyModel.config.credentialFields[kind].forEach(function(field) {
        values[field.name] = document.getElementById('notify-field-' + kind + '-' + field.name).value.trim();
    });

    var handlers = shared.inFlight(anchor, function() {
        self.render();
        shared.popover(document.getElementById('notify-credentials-pane'),
            notifyModel.config.kindLabels[kind] + ' credentials stored, encrypted at rest.', 'green');
    }, function(message) { shared.popover(anchor, message, 'red'); });
    if (handlers === null) { return; }

    notifyModel.saveCredentials(kind, values, handlers.done, handlers.error);
};

notifyView.sendTest = function(anchor, kind) {
    var target = document.getElementById('notify-test-' + kind).value.trim();

    if (target === '') {
        shared.popover(anchor, 'Name the channel the test message goes to.', 'red');
        return;
    }

    var handlers = shared.inFlight(anchor, function() {
        shared.popover(anchor, 'Delivered to ' + target + ' - the credentials work.', 'green');
    }, function(message) { shared.popover(anchor, message, 'red'); });
    if (handlers === null) { return; }

    notifyModel.sendTest(kind, target, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

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

notifyModel.isAdmin = document.getElementById('notify-credentials-pane') !== null;

notifyModel.load(function() { notifyView.render(); });

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') { notifyView.closePanel(); }
});

document.addEventListener('mousedown', function(event) {
    if (notifyView.panelElement === null) { return; }
    if (event.target.closest('.toolbar .button-ghost') !== null) { return; }
    if (!notifyView.panelElement.contains(event.target)) { notifyView.closePanel(); }
});

})();
