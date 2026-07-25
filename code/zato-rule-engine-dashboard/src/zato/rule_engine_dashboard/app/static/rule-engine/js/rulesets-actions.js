'use strict';

// Event handlers for the rulesets home: the search, the view chips,
// saved views, the recents strip, selection, opening, following,
// publishing from the list and the keyboard. The floating panels come
// from shared.openPanel. Augments the rulesetsView namespace from
// rulesets-render.js.

(function() {

// ////////////////////////////////////////////////////////////////////////

rulesetsView.setQuery = function(value) {
    var self = this;
    this.query = value;

    // A typed query is not the saved view's query anymore
    document.querySelectorAll('.rulesets-saved-chip').forEach(function(chip) { chip.classList.remove('toggled'); });

    // The full-text index lives on the server, the list re-renders when
    // its answer lands
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

// Opening a ruleset lands on its decision table, the other screens are
// one click away in the preview
rulesetsView.open = function(id) {
    window.location.href = this.config.openUrls.tables + '?ruleset=' + id;
};

// A recent chip selects its row again, the preview answers right away
rulesetsView.pickRecent = function(id) {
    this.select(id);
    var row = document.querySelector('.rulesets-row-selected');
    if (row !== null) { row.scrollIntoView({block: 'nearest'}); }
};

rulesetsView.openFromLink = function(event) {
    event.stopPropagation();
    return true;
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
            followed ? 'Not following anymore.' : 'Following. Its changes lead the feed.');
    };

    if (followed) {
        rulesetsModel.unfollow(id, onDone);
    } else {
        rulesetsModel.follow(id, onDone);
    }
};

// A new ruleset starts from its vocabulary: one pasted example payload
// is enough to bootstrap the terms the rules will speak in
rulesetsView.newRuleset = function() {
    window.location.href = this.config.openUrls.vocabulary;
};

// ////////////////////////////////////////////////////////////////////////

// Publishing from the list: a confirmation first, then the closing
// report in the same panel once the server answers
rulesetsView.openPublishPanel = function(id, anchor) {
    if (shared.panelElement !== null) { shared.closePanel(); return; }

    var ruleset = rulesetsModel.byId(id);
    var draft = rulesetsModel.draftVersion(ruleset);

    var firstLine = ruleset.live_version === null
        ? 'Version ' + draft + ' goes live for the first time, this ruleset has never answered requests before.'
        : 'Draft v' + draft + ' replaces live v' + ruleset.live_version + ' the moment this lands, not a second earlier.';

    shared.openPanel(anchor,
        '<div class="test-trace-title">Publish ' + shared.escape(ruleset.name) + '</div>' +
        '<div class="floating-panel-hint">' + firstLine + '</div>' +
        '<div class="floating-panel-actions">' +
        '<button class="button-primary button-mini" onclick="rulesetsView.confirmPublish(' + id + ', ' + draft + ', this)">' +
            'Publish v' + draft + '</button>' +
        '</div>' +
        '<div class="floating-panel-hint">A snapshot is taken first, so whatever is live now can come back ' +
        'as-is with one click on the versions screen.</div>');
};

rulesetsView.confirmPublish = function(id, version, button) {
    var self = this;
    var ruleset = rulesetsModel.byId(id);
    var previous = ruleset.live_version;

    var handlers = shared.inFlight(button, function(report) {

        // The list reflects the new live version without a round trip
        ruleset.live_version = report.version;

        self.renderList();
        self.renderSide();
        shared.initTips();

        var previousLine = previous === null
            ? 'This is its first live version, the endpoint answers with it from now on.'
            : 'v' + previous + ' stays in the timeline and comes back as-is if needed, nothing was renumbered.';

        // The closing report replaces the confirmation in the same panel
        shared.panelElement.innerHTML =
            '<div class="test-trace-title">Published, v' + report.version + ' is live</div>' +
            '<div class="rulesets-publish-line">The snapshot was taken. ' + previousLine + '</div>' +
            '<div class="rulesets-publish-line">' + report.rule_names.length +
                ' rules are answering requests now.</div>' +
            '<div class="rulesets-publish-line">New decisions in the log link to v' + report.version +
                ' from here forward.</div>' +
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

// Renaming a ruleset: the impact first, because the name is the REST path
// callers invoke and every rule name carries it
rulesetsView.openRenamePanel = function(id, anchor) {
    if (shared.panelElement !== null) { shared.closePanel(); return; }

    var ruleset = rulesetsModel.byId(id);

    shared.openPanel(anchor,
        '<div class="test-trace-title">Rename ' + shared.escape(ruleset.name) + '</div>' +
        '<div class="floating-panel-line">' +
        '<input id="rulesets-rename-input" type="text" value="' + shared.escape(ruleset.name) + '" ' +
            'onkeydown="rulesetsView.renameKeys(event, ' + id + ')">' +
        '<button class="button-primary button-mini" onclick="rulesetsView.previewRename(' + id + ', this)">' +
            'Preview impact</button>' +
        '</div>' +
        '<div class="floating-panel-hint">The name is the address callers invoke, so the preview says how many ' +
        'calls the current one has served. Every rule of the ruleset is renamed with it, as a new draft version.</div>' +
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

// What the preview reports: the traffic the current name has served and
// every rule name the rename rewrites
rulesetsView.renameImpactHtml = function(id, report) {
    var html = '<div class="rulesets-rename-line">' + report.rest_call_count +
        ' logged calls used ' + shared.escape(report.old_name) +
        ' - each caller has to be moved to ' + shared.escape(report.new_name) + '.</div>';

    html += '<div class="rulesets-rename-line">' + report.rules.length + ' rules are renamed with it.</div>';

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
            'Renamed to ' + report.new_name + ', its ' + report.rules.length + ' rules with it, stored as draft v' +
            report.version + '. Publish it to make the new names live.', 'green');
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    rulesetsModel.renameApply(id, newName, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

// Saving the current search and view filter as a named chip, capped so
// the view list never turns into a graveyard of stale queries
rulesetsView.openSaveViewPanel = function(button) {
    if (shared.panelElement !== null) { shared.closePanel(); return; }

    if (rulesetsModel.savedViews().length >= this.config.maxSavedViews) {
        shared.popover(button, 'Views stay few and named, ' + this.config.maxSavedViews +
            ' is the cap. Delete one first, the x on its chip, a long view list wastes more time than it saves.', 'red');
        return;
    }

    shared.openPanel(button,
        '<div class="test-trace-title">Save this view</div>' +
        '<div class="floating-panel-line">' +
        '<input id="rulesets-view-name" type="text" placeholder="view name" ' +
            'onkeydown="rulesetsView.saveViewKeys(event)">' +
        '<button class="button-primary button-mini" onclick="rulesetsView.confirmSaveView(this)">Save</button>' +
        '</div>' +
        '<div class="floating-panel-hint">Saves ' +
            this.describeView({view: this.view, query: this.query.trim()}) +
        ', as a chip next to the fixed ones.</div>');
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
        shared.popover(document.querySelector('.rulesets-saved-chip[data-saved-view="' + name + '"]'),
            'Saved. The chip brings the search and the filter back together.', 'green');
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

    // The saved chip and the fixed chip of its view filter light together
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
        this.open(this.selectedId);
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

// These controls toggle their own panels, the shared outside-click
// handler leaves them alone
shared.panelToggles.push('.rulesets-publish', '#rulesets-save-view-button');

shared.attachPaneResize(document.getElementById('rulesets-side-resizer'),
    document.getElementById('rulesets-side'), 'x-right');

})();
