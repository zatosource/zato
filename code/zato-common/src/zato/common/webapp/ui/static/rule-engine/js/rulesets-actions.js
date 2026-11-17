'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

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
    if (id === this.config.autoExpandId) { return; }

    this.selectedId = id;

    if (this.expanded[id] === true) {
        delete this.expanded[id];
        this.renderList();
        shared.initTips();
        return;
    }

    this.expanded[id] = true;

    // The panel appears at once, with its spinner, and fills in when the rules arrive.
    this.renderList();
    shared.initTips();

    rulesetsModel.rules(id, function() {
        self.renderList();
        shared.initTips();
    });
};

// A host that changed a rule behind the panel refetches the set and repaints the panel,
// so the change shows without a reload
rulesetsView.refreshRules = function(id) {
    var self = this;

    rulesetsModel.dropCachedRules(id);
    rulesetsModel.rules(id, function() {
        self.renderList();
        shared.initTips();
    });
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

    this.showRules(ids[next]);
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

    if (action === 'select-ruleset') { this.showRules(id); }
    if (action === 'toggle-rules') { this.toggleRules(event, id); }
    if (action === 'clear-all') { this.clearAll(); }
    if (action === 'new') { this.config.onNew(); }

    if (action === 'rule-action') {
        this.runRuleAction(parseInt(target.getAttribute('data-index')), target.getAttribute('data-rule'), target);
    }
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.bindListeners = function() {
    var self = this;

    this.container.addEventListener('click', function(event) {
        var target = event.target.closest('[data-action]');
        if (target === null || !self.container.contains(target)) { return; }
        self.dispatch(event, target);
    });

    document.addEventListener('keydown', function(event) { self.onKeyDown(event); });
};

// ////////////////////////////////////////////////////////////////////////

// The one entry point - the host application says where the browser lives, which endpoints
// it has and how it behaves, nothing boots as a side effect of loading the scripts
rulesetsView.init = function(container, config) {
    var self = this;
    this.container = container;

    Object.keys(config).forEach(function(key) {
        if (key === 'urls') {
            rulesetsModel.config.urls = config.urls;
            return;
        }
        if (key === 'rulesetLabels') {
            rulesetsModel.config.rulesetLabels = config.rulesetLabels;
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
