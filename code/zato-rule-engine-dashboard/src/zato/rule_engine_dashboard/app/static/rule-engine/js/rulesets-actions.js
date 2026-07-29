'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

rulesetsView.setQuery = function(value) {
    var self = this;
    this.query = value;

    document.querySelectorAll('.rulesets-saved-chip').forEach(function(chip) { chip.classList.remove('toggled'); });

    rulesetsModel.search(value, function() {
        self.renderList();
        shared.initTips();
    });
};

rulesetsView.setView = function(button, view) {
    this.view = view;
    document.querySelectorAll('.rulesets-chip').forEach(function(chip) { chip.classList.remove('toggled'); });
    button.classList.add('toggled');
    this.renderList();
    shared.initTips();
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.select = function(id) {
    if (id === this.selectedId) { return; }
    this.selectedId = id;
    shared.closePanel();
    this.renderList();
    this.renderSide();
    shared.initTips();
};

rulesetsView.open = function(id) {
    window.location.href = this.config.openUrls.editor + '?ruleset=' + id;
};

rulesetsView.pickRecent = function(id) {
    this.select(id);
    var row = document.querySelector('.rulesets-row-selected');
    if (row !== null) { row.scrollIntoView({block: 'nearest'}); }
};

// Clicking the name of a set lists the rules it is made of, right under the row.
// Nothing here walks into a rule, that is what the rules in the panel are for.
rulesetsView.toggleRules = function(event, id) {

    // A modified click keeps its plain meaning, the editor in a new tab or window.
    if (event.ctrlKey || event.metaKey || event.shiftKey) { return true; }

    event.preventDefault();
    event.stopPropagation();

    this.showRules(id);
    return false;
};

rulesetsView.showRules = function(id) {
    var self = this;
    this.selectedId = id;

    if (this.expanded[id] === true) {
        delete this.expanded[id];
        this.renderList();
        this.renderSide();
        shared.initTips();
        return;
    }

    this.expanded[id] = true;

    // The panel appears at once, with its spinner, and fills in when the rules arrive.
    this.renderList();
    this.renderSide();
    shared.initTips();

    rulesetsModel.rules(id, function() {
        self.renderList();
        shared.initTips();
    });
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.toggleFollow = function(id) {
    var self = this;
    var followed = rulesetsModel.isFollowed(id);

    var onDone = function() {
        self.renderList();
        self.renderSide();
        shared.initTips();
        shared.popover(document.querySelector('.rulesets-row[data-id="' + id + '"] .rulesets-star'),
            followed ? 'Not following.' : 'Following.');
    };

    if (followed) {
        rulesetsModel.unfollow(id, onDone);
    } else {
        rulesetsModel.follow(id, onDone);
    }
};

rulesetsView.newRuleset = function() {
    window.location.href = this.config.openUrls.vocabulary;
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.openPublishPanel = function(id, anchor) {
    if (shared.panelElement !== null) { shared.closePanel(); return; }

    var ruleset = rulesetsModel.byId(id);
    var draft = rulesetsModel.draftVersion(ruleset);

    var firstLine = ruleset.live_version === null
        ? 'Draft v' + draft + ' goes live.'
        : 'Draft v' + draft + ' replaces live v' + ruleset.live_version + '.';

    shared.openPanel(anchor,
        '<div class="test-trace-title">Publish ' + shared.escape(ruleset.name) + '</div>' +
        '<div class="floating-panel-line">' + firstLine + '</div>' +
        '<div class="floating-panel-actions">' +
        '<button class="button-primary button-mini" onclick="rulesetsView.confirmPublish(' + id + ', ' + draft + ', this)">' +
            'Publish v' + draft + '</button>' +
        '</div>');
};

rulesetsView.confirmPublish = function(id, version, button) {
    var self = this;
    var ruleset = rulesetsModel.byId(id);
    var previous = ruleset.live_version;

    var handlers = shared.inFlight(button, function(report) {

        ruleset.live_version = report.version;

        self.renderList();
        self.renderSide();
        shared.initTips();

        var previousLine = previous === null
            ? 'No version was live before.'
            : 'v' + previous + ' stays in the timeline.';

        shared.panelElement.innerHTML =
            '<div class="test-trace-title">Published, v' + report.version + ' is live</div>' +
            '<div class="rulesets-publish-line">' + previousLine + '</div>' +
            '<div class="rulesets-publish-line">' + report.rule_names.length + ' live rule' +
                (report.rule_names.length === 1 ? '' : 's') + '</div>' +
            '<div class="floating-panel-actions">' +
            '<button class="button-mini" onclick="shared.closePanel()">Close</button>' +
            '</div>';

    }, function(message) {
        shared.closePanel();
        shared.popover(document.querySelector('.rulesets-row[data-id="' + id + '"] .rulesets-publish'), message, 'red');
    });
    if (handlers === null) { return; }

    rulesetsModel.publish(id, version, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.openRenamePanel = function(id, anchor) {
    if (shared.panelElement !== null) { shared.closePanel(); return; }

    var ruleset = rulesetsModel.byId(id);

    shared.openPanel(anchor,
        '<div class="floating-panel-line">' +
        '<input id="rulesets-rename-input" type="text" value="' + shared.escape(ruleset.name) + '" ' +
            'onkeydown="rulesetsView.renameKeys(event, ' + id + ')">' +
        '<button class="button-primary button-mini" onclick="rulesetsView.previewRename(' + id + ', this)">' +
            'Preview impact</button>' +
        '</div>' +
        '<div id="rulesets-rename-impact"></div>');

    document.getElementById('rulesets-rename-input').focus();
};

rulesetsView.renameKeys = function(event, id) {
    if (event.key === 'Enter') { this.previewRename(id, event.target); }
    if (event.key === 'Escape') { shared.closePanel(); }
};

rulesetsView.renameInput = function() {
    var out = document.getElementById('rulesets-rename-input').value.trim();
    return out;
};

rulesetsView.previewRename = function(id, button) {
    var self = this;
    var newName = this.renameInput();

    if (!this.config.rulesetNamePattern.test(newName)) {
        shared.popover(button, 'A ruleset name is dotted words, letters, digits and underscores only.', 'red');
        return;
    }

    var handlers = shared.inFlight(button, function(report) {
        document.getElementById('rulesets-rename-impact').innerHTML = self.renameImpactHtml(id, report);
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    rulesetsModel.renamePreview(id, newName, handlers.done, handlers.error);
};

rulesetsView.renameImpactHtml = function(id, report) {
    var html = '<div class="rulesets-rename-line">' + report.rest_call_count + ' logged call' +
        (report.rest_call_count === 1 ? '' : 's') + ' used ' + shared.escape(report.old_name) + '</div>';

    html += '<div class="rulesets-rename-line">' + report.rules.length + ' rule' +
        (report.rules.length === 1 ? '' : 's') + ' renamed</div>';

    report.rules.slice(0, this.config.maxRenamedRules).forEach(function(entry) {
        html += '<div class="rulesets-match">' + shared.escape(entry.rule) + ' becomes ' +
            shared.escape(entry.new_rule) + '</div>';
    });

    if (report.rules.length > this.config.maxRenamedRules) {
        html += '<div class="rulesets-match-overflow">and ' + (report.rules.length - this.config.maxRenamedRules) +
            ' more rules</div>';
    }

    html += '<div class="floating-panel-actions">' +
        '<button class="button-primary button-mini" onclick="rulesetsView.confirmRename(' + id + ', this)">' +
            'Rename to ' + shared.escape(report.new_name) + '</button>' +
        '</div>';

    return html;
};

rulesetsView.confirmRename = function(id, button) {
    var self = this;
    var newName = this.renameInput();

    var handlers = shared.inFlight(button, function(report) {
        shared.closePanel();
        self.renderList();
        self.renderSide();
        shared.initTips();

        shared.popover(document.querySelector('.rulesets-row[data-id="' + id + '"]'),
            'Renamed to ' + report.new_name + ' with its ' + report.rules.length + ' rule' +
            (report.rules.length === 1 ? '' : 's') + ', draft v' + report.version + '.', 'green');
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    rulesetsModel.renameApply(id, newName, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.openSaveViewPanel = function(button) {
    if (shared.panelElement !== null) { shared.closePanel(); return; }

    if (rulesetsModel.savedViews().length >= this.config.maxSavedViews) {
        shared.popover(button, this.config.maxSavedViews + ' saved views is the cap, delete one first.', 'red');
        return;
    }

    shared.openPanel(button,
        '<div class="test-trace-title">Save this view</div>' +
        '<div class="floating-panel-line">' +
        '<input id="rulesets-view-name" type="text" placeholder="view name" ' +
            'onkeydown="rulesetsView.saveViewKeys(event)">' +
        '<button class="button-primary button-mini" onclick="rulesetsView.confirmSaveView(this)">Save</button>' +
        '</div>' +
        '<div class="floating-panel-line">' +
            this.describeView({view: this.view, query: this.query.trim()}) +
        '</div>');
};

rulesetsView.saveViewKeys = function(event) {
    if (event.key === 'Enter') { this.confirmSaveView(event.target); }
    if (event.key === 'Escape') { shared.closePanel(); }
};

rulesetsView.confirmSaveView = function(anchor) {
    var self = this;
    var name = document.getElementById('rulesets-view-name').value.trim();

    if (name === '' || /[^A-Za-z0-9 ]/.test(name)) {
        shared.popover(anchor, 'A view name is a few words, letters, digits and spaces only.', 'red');
        return;
    }

    var handlers = shared.inFlight(anchor, function() {
        shared.closePanel();
        self.renderSavedViews();
        shared.initTips();
        shared.popover(document.querySelector('.rulesets-saved-chip[data-saved-view="' + name + '"]'), 'Saved.', 'green');
    }, function(message) {
        shared.popover(anchor, message, 'red');
    });
    if (handlers === null) { return; }

    rulesetsModel.saveView(name, this.view, this.query.trim(), handlers.done, handlers.error);
};

rulesetsView.applySavedView = function(chip, name) {
    var self = this;
    var view = rulesetsModel.savedViews().filter(function(candidate) { return candidate.name === name; })[0];
    var payload = view.payload;

    this.view = payload.view;
    this.query = payload.query;
    document.getElementById('rulesets-search').value = payload.query;

    document.querySelectorAll('.rulesets-chip').forEach(function(other) { other.classList.remove('toggled'); });
    document.querySelector('.rulesets-chip[data-view="' + payload.view + '"]').classList.add('toggled');
    chip.classList.add('toggled');

    rulesetsModel.search(payload.query, function() {
        self.renderList();
        shared.initTips();
    });
};

rulesetsView.deleteSavedView = function(name) {
    var self = this;
    rulesetsModel.deleteView(name, function() {
        self.renderSavedViews();
        shared.initTips();
    });
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.visibleIds = function() {
    var out = [];
    document.querySelectorAll('.rulesets-row').forEach(function(row) { out.push(parseInt(row.dataset.id)); });
    return out;
};

rulesetsView.onKeyDown = function(event) {
    var target = event.target;
    var inField = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT';

    if (event.key === 'Escape') { shared.closePanel(); return; }
    if (event.key === '/' && !inField) {
        event.preventDefault();
        document.getElementById('rulesets-search').focus();
        return;
    }
    if (event.key === 'Enter' && !inField && this.selectedId !== null) {
        this.showRules(this.selectedId);
        return;
    }
    if (inField || (event.key !== 'ArrowUp' && event.key !== 'ArrowDown')) { return; }
    event.preventDefault();

    var ids = this.visibleIds();
    if (ids.length === 0) { return; }

    var position = ids.indexOf(this.selectedId);
    var next = Math.max(0, Math.min(ids.length - 1, position + (event.key === 'ArrowDown' ? 1 : -1)));
    if (ids[next] === this.selectedId) { return; }

    this.select(ids[next]);
    var row = document.querySelector('.rulesets-row-selected');
    if (row !== null) { row.scrollIntoView({block: 'nearest'}); }
};

// ////////////////////////////////////////////////////////////////////////

rulesetsModel.load(function() { rulesetsView.render(); });

document.getElementById('rulesets-search').addEventListener('input', function(event) {
    rulesetsView.setQuery(event.target.value);
});

document.addEventListener('keydown', function(event) { rulesetsView.onKeyDown(event); });

shared.panelToggles.push('.rulesets-publish', '#rulesets-save-view-button');

shared.attachPaneResize(document.getElementById('rulesets-side-resizer'),
    document.getElementById('rulesets-side'), 'x-right');

})();
