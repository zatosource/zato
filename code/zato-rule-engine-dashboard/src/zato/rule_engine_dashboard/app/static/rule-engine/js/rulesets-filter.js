'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

rulesetsView.filters = function() {
    var out = {live: false, draft: false, followed: false};

    this.chosen.forEach(function(facet) { out[facet.field] = true; });

    return out;
};

rulesetsView.isChosen = function(candidate) {
    return this.chosen.some(function(facet) {
        return facet.facet === candidate.facet && facet.value === candidate.value;
    });
};

rulesetsView.chosenLabels = function() {
    var out = [];

    this.chosen.forEach(function(facet) { out.push(facet.facet + ':' + facet.value); });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.narrowed = function() {
    return this.chosen.length > 0 || this.query.trim() !== '';
};

rulesetsView.buildSuggestions = function() {
    var self = this;
    var typed = this.query.trim().toLowerCase();
    var counts = rulesetsModel.counts();
    var groups = this.config.groups;
    var out = [];

    this.config.facets.forEach(function(candidate) {
        var label = candidate.facet + ':' + candidate.value;
        if (typed !== '' && label.indexOf(typed) === -1) { return; }

        out.push({
            group: groups.facets,
            facet: candidate.facet,
            value: candidate.value,
            count: counts[candidate.field],
            token: candidate,
            view: null,
        });
    });

    rulesetsModel.savedViews().forEach(function(view) {
        if (typed !== '' && view.name.toLowerCase().indexOf(typed) === -1) { return; }

        out.push({
            group: groups.views,
            facet: 'view',
            value: view.name,
            count: null,
            token: null,
            view: view,
        });
    });

    // The typed text itself is an entry, so a search always has a row to land on
    if (typed !== '') {
        out.push({
            group: groups.text,
            facet: 'text',
            value: this.query.trim(),
            count: null,
            token: null,
            view: null,
        });
    }

    this.suggestions = out;

    if (this.suggestionIndex >= out.length) { this.suggestionIndex = 0; }
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.openSuggestions = function() {
    this.suggestOpen = true;
    this.suggestionIndex = 0;
    this.buildSuggestions();
    this.renderSuggestions();
};

rulesetsView.closeSuggestions = function() {
    this.suggestOpen = false;
    this.renderSuggestions();
};

rulesetsView.moveSuggestion = function(step) {
    var last = this.suggestions.length - 1;
    if (last < 0) { return; }

    this.suggestionIndex = Math.max(0, Math.min(last, this.suggestionIndex + step));
    this.renderSuggestions();
};

rulesetsView.pick = function(index) {
    var entry = this.suggestions[index];

    if (entry.token !== null) {
        this.toggleFacet(entry.token);
        return;
    }

    if (entry.view !== null) {
        this.applySavedView(entry.view.name);
        return;
    }

    this.closeSuggestions();
};

rulesetsView.dropSavedView = function(index) {
    this.deleteSavedView(this.suggestions[index].view.name);
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.toggleFacet = function(facet) {
    if (this.isChosen(facet)) {
        this.chosen = this.chosen.filter(function(candidate) {
            return candidate.facet !== facet.facet || candidate.value !== facet.value;
        });
    } else {
        this.chosen.push(facet);
    }

    this.applyFilters();
};

rulesetsView.clearAll = function() {
    this.chosen = [];
    this.query = '';
    document.getElementById('rulesets-search').value = '';
    this.applyFilters();
};

// Every filter change lands here: the hits come from the server, the rest is local
rulesetsView.applyFilters = function() {
    var self = this;

    rulesetsModel.search(this.query, function() {
        self.buildSuggestions();
        self.renderSuggestions();
        self.renderList();
        shared.initTips();
    });
};

rulesetsView.setQuery = function(value) {
    var self = this;

    this.query = value;
    this.suggestionIndex = 0;

    this.buildSuggestions();
    this.renderSuggestions();

    if (this.searchTimer !== null) { clearTimeout(this.searchTimer); }
    this.searchTimer = setTimeout(function() {
        self.searchTimer = null;
        self.applyFilters();
    }, this.config.searchDelayMilliseconds);
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.onFieldKeys = function(event) {
    var input = event.target;

    if (event.key === 'ArrowDown') { event.preventDefault(); this.moveSuggestion(1); return; }
    if (event.key === 'ArrowUp') { event.preventDefault(); this.moveSuggestion(-1); return; }

    if (event.key === 'Enter' || event.key === 'Tab') {
        if (this.suggestions.length === 0) { return; }
        event.preventDefault();
        this.pick(this.suggestionIndex);
        return;
    }

    if (event.key === 'Escape') {
        event.stopPropagation();
        if (this.suggestOpen) { this.closeSuggestions(); return; }
        input.blur();
    }
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.openSaveViewPanel = function(anchor) {
    if (rulesetsModel.savedViews().length >= this.config.maxSavedViews) {
        shared.popover(anchor, this.config.maxSavedViews + ' saved views is the cap, delete one first.', 'red');
        return;
    }

    shared.openPanel(anchor,
        '<div class="floating-panel-line">' +
        '<input id="rulesets-view-name" type="text" placeholder="view name" ' +
            'onkeydown="rulesetsView.saveViewKeys(event)">' +
        '<button class="button-primary button-mini" onclick="rulesetsView.confirmSaveView(this)">Save</button>' +
        '</div>');
};

rulesetsView.saveViewKeys = function(event) {
    if (event.key === 'Enter') { this.confirmSaveView(event.target); }
    if (event.key === 'Escape') { shared.closePanel(); }
};

rulesetsView.confirmSaveView = function(anchor) {
    var self = this;
    var name = document.getElementById('rulesets-view-name').value.trim();

    if (!this.config.viewNamePattern.test(name)) {
        shared.popover(anchor, 'A view name is letters, digits and spaces only.', 'red');
        return;
    }

    var handlers = shared.inFlight(anchor, function() {
        shared.closePanel();
        self.buildSuggestions();
        self.renderSuggestions();
        shared.initTips();
    }, function(message) {
        shared.popover(anchor, message, 'red');
    });
    if (handlers === null) { return; }

    var payload = {facets: this.chosenLabels(), query: this.query.trim()};
    rulesetsModel.saveView(name, payload, handlers.done, handlers.error);
};

rulesetsView.applySavedView = function(name) {
    var self = this;
    var view = rulesetsModel.savedViews().filter(function(candidate) { return candidate.name === name; })[0];
    var stored = view.payload;

    this.chosen = [];

    stored.facets.forEach(function(label) {
        var match = self.config.facets.filter(function(candidate) {
            return candidate.facet + ':' + candidate.value === label;
        })[0];

        if (match !== undefined) { self.chosen.push(match); }
    });

    this.query = stored.query;
    document.getElementById('rulesets-search').value = stored.query;

    this.closeSuggestions();
    this.applyFilters();
};

rulesetsView.deleteSavedView = function(name) {
    var self = this;

    rulesetsModel.deleteView(name, function() {
        self.buildSuggestions();
        self.renderSuggestions();
        shared.initTips();
    });
};

// ////////////////////////////////////////////////////////////////////////

var field = document.getElementById('rulesets-field');
var input = document.getElementById('rulesets-search');

document.getElementById('rulesets-clear').innerHTML = shared.icon('x', 11);

// A click anywhere in the field belongs to the input, the way a search field behaves
field.addEventListener('mousedown', function(event) {
    if (event.target.closest('button') !== null) { return; }
    if (event.target === input) { return; }

    event.preventDefault();
    input.focus();
});

input.addEventListener('focus', function() { rulesetsView.openSuggestions(); });
input.addEventListener('blur', function() { rulesetsView.closeSuggestions(); });
input.addEventListener('input', function(event) { rulesetsView.setQuery(event.target.value); });
input.addEventListener('keydown', function(event) { rulesetsView.onFieldKeys(event); });

// The screen boots from here, the last of its scripts, so every view method is in place
rulesetsModel.load(function() { rulesetsView.render(); });

})();
