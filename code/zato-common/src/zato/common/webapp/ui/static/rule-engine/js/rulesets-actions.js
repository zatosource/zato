'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

rulesetsView.select = function(id) {

    // With no side pane there is nothing to select for - the click expands the rules instead
    if (!this.config.showSidePane) {
        this.showRules(id);
        return;
    }

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

    // A locked row is expanded for good - there is nothing to toggle
    if (this.config.lockExpanded && id === this.config.autoExpandId) { return; }

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

// A host that changed a rule behind the panel refetches the set and repaints both the
// panel and the preview, so the change shows without a reload
rulesetsView.refreshRules = function(id) {
    var self = this;

    rulesetsModel.dropCachedRules(id);
    rulesetsModel.rules(id, function() {
        self.renderList();
        self.renderSide();
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
    };

    if (followed) {
        rulesetsModel.unfollow(id, onDone);
    } else {
        rulesetsModel.follow(id, onDone);
    }
};

// ////////////////////////////////////////////////////////////////////////

// Panels attach to the floating root, outside the container, so each one gets its own
// dispatcher - the markup inside carries data-action attributes, never inline handlers
rulesetsView.openActionPanel = function(anchor, html) {
    var self = this;

    shared.openPanel(anchor, html);

    shared.panelElement.addEventListener('click', function(event) {
        var target = event.target.closest('[data-action]');
        if (target === null) { return; }
        self.dispatchPanel(event, target);
    });
};

rulesetsView.dispatchPanel = function(event, target) {
    var action = target.getAttribute('data-action');
    var id = parseInt(target.getAttribute('data-id'));

    if (action === 'confirm-publish') { this.confirmPublish(id, parseInt(target.getAttribute('data-version')), target); }
    if (action === 'preview-rename') { this.previewRename(id, target); }
    if (action === 'confirm-rename') { this.confirmRename(id, target); }
    if (action === 'confirm-save-view') { this.confirmSaveView(target); }
    if (action === 'close-panel') { shared.closePanel(); }
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.openPublishPanel = function(id, anchor) {
    if (shared.panelElement !== null) { shared.closePanel(); return; }

    var ruleset = rulesetsModel.byId(id);
    var draft = rulesetsModel.draftVersion(ruleset);

    var firstLine = ruleset.live_version === null
        ? 'Draft v' + draft + ' goes live.'
        : 'Draft v' + draft + ' replaces live v' + ruleset.live_version + '.';

    this.openActionPanel(anchor,
        '<div class="floating-panel-line">' + firstLine + '</div>' +
        '<div class="floating-panel-actions">' +
        '<button class="button-primary button-mini" data-action="confirm-publish" ' +
            'data-id="' + id + '" data-version="' + draft + '">' +
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
            '<div class="test-grid-title">Published, v' + report.version + ' is live</div>' +
            '<div class="rulesets-publish-line">' + previousLine + '</div>' +
            '<div class="rulesets-publish-line">' + report.rule_names.length + ' live rule' +
                (report.rule_names.length === 1 ? '' : 's') + '</div>' +
            '<div class="floating-panel-actions">' +
            '<button class="button-mini" data-action="close-panel">Close</button>' +
            '</div>';

    }, function(message) {
        shared.closePanel();
        shared.popover(self.element('.rulesets-row[data-id="' + id + '"] .rulesets-publish'), message, 'red');
    });
    if (handlers === null) { return; }

    rulesetsModel.publish(id, version, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.openRenamePanel = function(id, anchor) {
    if (shared.panelElement !== null) { shared.closePanel(); return; }

    var self = this;
    var ruleset = rulesetsModel.byId(id);

    this.openActionPanel(anchor,
        '<div class="floating-panel-line">' +
        '<span class="field" data-hint="">' +
        '<input id="rulesets-rename-input" type="text" placeholder=" " value="' + shared.escape(ruleset.name) + '">' +
        '</span>' +
        '<button class="button-primary button-mini" data-action="preview-rename" data-id="' + id + '">' +
            'Preview impact</button>' +
        '</div>' +
        '<div id="rulesets-rename-impact"></div>');

    var input = document.getElementById('rulesets-rename-input');
    input.addEventListener('keydown', function(event) { self.renameKeys(event, id); });
    input.focus();
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
        shared.requireInput(document.getElementById('rulesets-rename-input'), shared.config.requiredText.name);
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
        '<button class="button-primary button-mini" data-action="confirm-rename" data-id="' + id + '">' +
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

        shared.popover(self.element('.rulesets-row[data-id="' + id + '"]'),
            'Renamed to ' + report.new_name + ' with its ' + report.rules.length + ' rule' +
            (report.rules.length === 1 ? '' : 's') + ', draft v' + report.version + '.', 'green');
    }, function(message) {
        shared.popover(button, message, 'red');
    });
    if (handlers === null) { return; }

    rulesetsModel.renameApply(id, newName, handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.visibleIds = function() {
    var out = [];
    this.elements('.rulesets-row').forEach(function(row) { out.push(parseInt(row.dataset.id)); });
    return out;
};

rulesetsView.onKeyDown = function(event) {
    var target = event.target;
    var inField = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT';

    if (event.key === 'Escape') { shared.closePanel(); return; }
    if (event.key === '/' && !inField) {
        event.preventDefault();
        this.element('#rulesets-search').focus();
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
    var row = this.element('.rulesets-row-selected');
    if (row !== null) { row.scrollIntoView({block: 'nearest'}); }
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.runRuleAction = function(actionIndex, ruleKey, target) {
    this.config.ruleActions[actionIndex].onRun(ruleKey, target);
};

// ////////////////////////////////////////////////////////////////////////

// What each data-action attribute in the browser's markup runs when clicked - the markup
// itself carries no inline handlers, so the browser works under a CSP that bans them
rulesetsView.dispatch = function(event, target) {
    var action = target.getAttribute('data-action');
    var id = parseInt(target.getAttribute('data-id'));

    if (action === 'select-ruleset') { this.select(id); }
    if (action === 'toggle-rules') { this.toggleRules(event, id); }
    if (action === 'toggle-follow') { this.toggleFollow(id); }
    if (action === 'open-publish') { this.openPublishPanel(id, target); }
    if (action === 'open-rename') { this.openRenamePanel(id, target); }
    if (action === 'clear-all') { this.clearAll(); }
    if (action === 'new') { this.config.onNew(); }

    if (action === 'rule-action') {

        // The action sits inside the rule's own link to the editor, which must not follow
        event.preventDefault();
        event.stopPropagation();
        this.runRuleAction(parseInt(target.getAttribute('data-index')), target.getAttribute('data-rule'), target);
    }
};

// The suggest pane acts on mousedown so the search field never loses its focus - the two
// buttons also stop the press so an open panel is not dismissed by the very press that acts
rulesetsView.dispatchMouse = function(event, target) {
    var action = target.getAttribute('data-mouse-action');

    event.preventDefault();

    if (action === 'pick') { this.pick(parseInt(target.getAttribute('data-index'))); }
    if (action === 'drop-view') { event.stopPropagation(); this.dropSavedView(parseInt(target.getAttribute('data-index'))); }
    if (action === 'open-save-view') { event.stopPropagation(); this.openSaveViewPanel(target); }
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.bindListeners = function() {
    var self = this;

    this.container.addEventListener('click', function(event) {
        var target = event.target.closest('[data-action]');
        if (target === null || !self.container.contains(target)) { return; }
        self.dispatch(event, target);
    });

    this.container.addEventListener('dblclick', function(event) {
        if (!self.config.openOnDoubleClick) { return; }
        var row = event.target.closest('[data-action="select-ruleset"]');
        if (row === null) { return; }
        self.open(parseInt(row.dataset.id));
    });

    this.container.addEventListener('mousedown', function(event) {
        var target = event.target.closest('[data-mouse-action]');
        if (target === null || !self.container.contains(target)) { return; }
        self.dispatchMouse(event, target);
    });

    document.addEventListener('keydown', function(event) { self.onKeyDown(event); });
};

// ////////////////////////////////////////////////////////////////////////

// The one entry point - the host application says where the browser lives, which endpoints
// it has and which features show, nothing boots as a side effect of loading the scripts
rulesetsView.init = function(container, config) {
    var self = this;
    this.container = container;

    Object.keys(config).forEach(function(key) {
        if (key === 'urls') {
            rulesetsModel.config.urls = config.urls;
            return;
        }
        if (key === 'listLimit') {
            rulesetsModel.config.listLimit = config.listLimit;
            return;
        }
        if (key === 'rulesetLabels') {
            rulesetsModel.config.rulesetLabels = config.rulesetLabels;
            return;
        }
        if (key === 'matchRulesetNames') {
            rulesetsModel.config.matchRulesetNames = config.matchRulesetNames;
            return;
        }
        if (key === 'csrfToken') {
            data.config.csrfToken = config.csrfToken;
            return;
        }
        rulesetsView.config[key] = config[key];
    });

    this.element('[data-action="new"]').textContent = this.config.newLabel;

    this.bindListeners();
    this.initFilter();
    if (this.config.showRowMenu) { this.initMenu(); }

    // A query the address bar carries comes back into the box before the first
    // paint, so a bookmarked filter opens already filtered
    if (this.config.queryURLKey !== null) {
        var urlParams = new URLSearchParams(window.location.search);
        var urlQuery = urlParams.get(this.config.queryURLKey);

        if (urlQuery !== null && urlQuery !== '') {
            this.query = urlQuery;
            this.element('#rulesets-search').value = urlQuery;
        }
    }

    shared.panelToggles.push('.rulesets-publish', '#rulesets-save-view', '.command-suggest-drag');

    if (this.config.showSidePane) {
        shared.attachPaneResize(this.element('#rulesets-side-resizer'), this.element('#rulesets-side'), 'x-right');
    }

    rulesetsModel.load(function() {

        // The one set the host opens onto is expanded and selected before the first paint,
        // so its rules are the first thing on the screen
        if (self.config.autoExpandId !== null) {
            self.selectedId = self.config.autoExpandId;
            self.expanded[self.config.autoExpandId] = true;

            rulesetsModel.rules(self.config.autoExpandId, function() {
                self.renderList();
                shared.initTips();
            });
        }

        self.render();

        // A query restored from the address needs its server hits before the
        // list can mark and narrow by it
        if (self.query !== '') { self.applyFilters(); }
    });
};

// ////////////////////////////////////////////////////////////////////////

})();
