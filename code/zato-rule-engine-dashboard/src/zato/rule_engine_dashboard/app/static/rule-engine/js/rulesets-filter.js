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

    if (this.suggestionIndex >= out.length) { this.suggestionIndex = -1; }
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.openSuggestions = function() {
    this.suggestOpen = true;
    this.suggestionIndex = -1;
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
    this.suggestionIndex = -1;

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
        if (this.suggestionIndex < 0) { return; }
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

// The pane is moved by its header, so a long list can be pulled off whatever it covers
rulesetsView.startPaneDrag = function(event) {
    var pane = document.getElementById('rulesets-suggest');
    var paneLeft = pane.offsetLeft;
    var paneTop = pane.offsetTop;

    var startX = event.clientX;
    var startY = event.clientY;

    // A panel opened from the pane belongs to it, so it travels the same distance
    var panel = shared.panelElement;
    var panelBox = panel === null ? null : panel.getBoundingClientRect();

    var onMove = function(moveEvent) {
        var movedX = moveEvent.clientX - startX;
        var movedY = moveEvent.clientY - startY;

        pane.style.left = (paneLeft + movedX) + 'px';
        pane.style.top = (paneTop + movedY) + 'px';

        if (panel !== null) {
            panel.style.left = (panelBox.left + movedX) + 'px';
            panel.style.top = (panelBox.top + movedY) + 'px';
        }
    };

    var onUp = function() {
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
        pane.classList.remove('command-suggest-dragging');
    };

    pane.classList.add('command-suggest-dragging');
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
};

// ////////////////////////////////////////////////////////////////////////

rulesetsView.openSaveViewPanel = function(anchor) {
    if (rulesetsModel.savedViews().length >= this.config.maxSavedViews) {
        shared.popover(anchor, this.config.maxSavedViews + ' views is the cap', 'red');
        return;
    }

    shared.openPanel(anchor,
        '<div class="floating-panel-line">' +
        '<input id="rulesets-view-name" type="text" placeholder="view name" ' +
            'onkeydown="rulesetsView.saveViewKeys(event)">' +
        '<button class="button-primary button-mini" onclick="rulesetsView.confirmSaveView(this)">Create</button>' +
        '</div>');
};

rulesetsView.saveViewKeys = function(event) {
    if (event.key === 'Enter') { this.confirmSaveView(event.target); }
    if (event.key === 'Escape') { shared.closePanel(); }
};

rulesetsView.confirmSaveView = function(anchor) {
    var self = this;
    var input = document.getElementById('rulesets-view-name');
    var name = input.value.trim();

    if (!this.config.viewNamePattern.test(name)) {
        shared.requireInput(input, shared.config.requiredText.name);
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
var pane = document.getElementById('rulesets-suggest');

document.getElementById('rulesets-clear').innerHTML = shared.icon('x', 11);

// A click anywhere in the field belongs to the input, the way a search field behaves
field.addEventListener('mousedown', function(event) {
    if (event.target.closest('button') !== null) { return; }
    if (event.target === input) { return; }

    event.preventDefault();
    input.focus();
});

pane.addEventListener('mousedown', function(event) {
    if (event.target.closest('.command-suggest-drag') === null) { return; }

    event.preventDefault();
    rulesetsView.startPaneDrag(event);
});

input.addEventListener('focus', function() { rulesetsView.openSuggestions(); });

input.addEventListener('blur', function(event) {
    // A panel opened from the pane takes the focus, and the pane stays as it was
    if (event.relatedTarget !== null && event.relatedTarget.closest('.floating-panel') !== null) { return; }

    rulesetsView.closeSuggestions();
});
input.addEventListener('input', function(event) { rulesetsView.setQuery(event.target.value); });
input.addEventListener('keydown', function(event) { rulesetsView.onFieldKeys(event); });

// The pane closes from anywhere, whether or not the field still holds the focus - a panel
// opened from the pane counts as part of it, everything else is elsewhere
document.addEventListener('mousedown', function(event) {
    if (!rulesetsView.suggestOpen) { return; }
    if (event.target.closest('#rulesets-field') !== null) { return; }
    if (event.target.closest('.floating-panel') !== null) { return; }

    rulesetsView.closeSuggestions();
});

document.addEventListener('keydown', function(event) {
    if (event.key !== 'Escape') { return; }
    if (!rulesetsView.suggestOpen) { return; }

    rulesetsView.closeSuggestions();
});

// The screen boots from here, the last of its scripts, so every view method is in place
rulesetsModel.load(function() { rulesetsView.render(); });

})();
