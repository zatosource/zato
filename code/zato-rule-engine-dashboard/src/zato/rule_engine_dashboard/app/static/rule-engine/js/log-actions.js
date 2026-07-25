'use strict';

// Event handlers for the decision log screen: the business-key search,
// the date range, the card facets, selection and keyboard movement,
// the one-click copy into the test set, the draft replay and the
// capture and rule-count panels. Augments the logView namespace from
// log-render.js.

(function() {

// ////////////////////////////////////////////////////////////////////////

logView.setSearch = function(value) {
    this.search = value;
    this.render();
};

// A range change reaches the server - the list and the aggregates both
// cover exactly the chosen window
logView.setRange = function(select) {
    var self = this;
    this.rangeDays = +select.value;
    logModel.refresh(this.rangeDays, this.outcome, function() { self.render(); });
};

// A card click filters the list to the decisions behind its number,
// a second click on the same card clears the facet
logView.toggleOutcome = function(outcome) {
    var self = this;
    this.outcome = this.outcome === outcome ? null : outcome;
    logModel.refresh(this.rangeDays, this.outcome, function() { self.render(); });
};

// "Everything for the value I clicked", the facet filter of any input
// or output value, shown as a chip over the list until cleared
logView.setValueFilter = function(path, value) {
    this.valueFilter = {path: path, value: value};
    this.render();
};

logView.clearValueFilter = function() {
    this.valueFilter = null;
    this.render();
};

// ////////////////////////////////////////////////////////////////////////

logView.select = function(decisionId) {
    // Clicking the already open decision must not re-render, that is what
    // keeps double-click text selection of keys and ids alive
    if (decisionId === this.selectedId) { return; }

    var self = this;
    this.selectedId = decisionId;
    logModel.open(decisionId, function() { self.render(); });
};

logView.toggleFold = function(sectionKey) {
    this.folded[sectionKey] = this.folded[sectionKey] !== true;
    this.renderDetail();
    shared.initTips();
};

// One copy handler for ids and values everywhere on the screen
logView.copyText = function(event, text) {
    event.stopPropagation();
    navigator.clipboard.writeText(text);
    shared.popover(event.target.closest('span'), 'Copied ' + text + '.', 'green');
};

// ////////////////////////////////////////////////////////////////////////

logView.addToTestSet = function(anchor) {
    var handlers = shared.inFlight(anchor, function(suiteName) {
        shared.popover(anchor, 'Added to ' + suiteName + ' as a scenario, with what went out as the ' +
            'expectations. Yesterday\'s traffic is today\'s regression test.', 'green');
    }, function(message) { shared.popover(anchor, message, 'red'); });
    if (handlers === null) { return; }

    logModel.addToTestSet(handlers.done, handlers.error);
};

logView.replay = function(anchor) {
    var self = this;

    // A second click folds the replay away
    if (logModel.replayResult !== null) {
        logModel.replayResult = null;
        this.renderDetail();
        shared.initTips();
        return;
    }

    var handlers = shared.inFlight(anchor, function() {
        self.renderDetail();
        shared.initTips();
    }, function(message) { shared.popover(anchor, message, 'red'); });
    if (handlers === null) { return; }

    logModel.replay(handlers.done, handlers.error);
};

// ////////////////////////////////////////////////////////////////////////

// Arrows walk the filtered list, page keys jump by a screenful, Home and
// End go to the edges, slash jumps to the search box
logView.onKeyDown = function(event) {
    var target = event.target;
    var inField = target.tagName === 'INPUT' || target.tagName === 'SELECT';

    if (event.key === '/' && !inField) {
        event.preventDefault();
        document.getElementById('log-search').focus();
        return;
    }

    var steps = {ArrowUp: -1, ArrowDown: 1, PageUp: -12, PageDown: 12};
    var isEdge = event.key === 'Home' || event.key === 'End';
    if (inField || (steps[event.key] === undefined && !isEdge)) { return; }
    event.preventDefault();

    var records = logModel.filtered(this.search, this.valueFilter);
    if (records.length === 0) { return; }

    var next;
    if (isEdge) {
        next = event.key === 'Home' ? 0 : records.length - 1;
    } else {
        var self = this;
        var position = records.findIndex(function(record) { return record.decision_id === self.selectedId; });
        // Clamped at both ends, the selection never leaves the list
        next = Math.max(0, Math.min(records.length - 1, position + steps[event.key]));
    }

    if (records[next].decision_id === this.selectedId) { return; }
    this.select(records[next].decision_id);

    var row = document.querySelector('.log-row-selected');
    if (row !== null) { row.scrollIntoView({block: 'nearest'}); }
};

// ////////////////////////////////////////////////////////////////////////

// The floating panels anchored to their toolbar buttons: the capture
// readout and the per-rule firing counts
logView.panelElement = null;

logView.closePanel = function() {
    if (this.panelElement === null) { return; }
    this.panelElement.remove();
    this.panelElement = null;
};

logView.showPanel = function(button, html) {
    this.closePanel();

    var panel = document.createElement('div');
    panel.className = 'log-capture-panel';
    panel.innerHTML = html;

    document.body.appendChild(panel);
    var rectangle = button.getBoundingClientRect();
    panel.style.top = (rectangle.bottom + 6) + 'px';
    panel.style.left = Math.min(rectangle.left, window.innerWidth - panel.offsetWidth - 8) + 'px';
    this.panelElement = panel;
};

// The capture and retention readout: what the log keeps and for how
// long, read from the stored decisions themselves
logView.openCapturePanel = function(button) {
    if (this.panelElement !== null) { this.closePanel(); return; }

    var readout = logModel.captureReadout();
    var html = '<div class="log-capture-title">Capture and retention</div>' +
        '<div class="log-capture-row"><span>Searchable header of every decision</span><b>always kept</b></div>' +
        '<div class="log-capture-row"><span>Full story of every error</span><b>always kept</b></div>' +
        '<div class="log-capture-row"><span>Full stories of successes on this page</span><b>' +
            readout.successKept + ' of ' + readout.successTotal + '</b></div>' +
        '<div class="log-capture-hint">The full story is the input, the output and the rules that decided. ' +
        'The success sample and the retention window are deliberate deployment settings of the capture dial ' +
        'and the retention sweep, never hidden defaults.</div>';

    this.showPanel(button, html);
};

// The per-rule firing counts over the range, with the live rules that
// never fired at all - the quiet ones are the interesting ones
logView.openRuleCounts = function(button) {
    if (this.panelElement !== null) { this.closePanel(); return; }
    var self = this;

    logModel.ruleCounts(this.rangeDays, function(counts) {
        var html = '<div class="log-capture-title">Which rules fire</div>';

        Object.keys(counts.totals).sort().forEach(function(rule) {
            html += '<div class="log-capture-row"><span>' + shared.escape(rule) + '</span><b>' +
                counts.totals[rule] + '</b></div>';
        });

        counts.neverFired.forEach(function(rule) {
            html += '<div class="log-capture-row"><span>' + shared.escape(rule) + '</span><b>never fired</b></div>';
        });

        html += '<div class="log-capture-hint">Counts over the selected range. A live rule that never fires ' +
            'is either dead weight or waiting for traffic that has not come - either way worth a look.</div>';

        self.showPanel(button, html);
    }, function(message) { shared.popover(button, message, 'red'); });
};

// ////////////////////////////////////////////////////////////////////////

logModel.load(function() {
    if (logModel.rulesetId === null) {
        logView.render();
        return;
    }
    logModel.refresh(logView.rangeDays, logView.outcome, function() { logView.render(); });
});

document.getElementById('log-search').addEventListener('input', function(event) {
    logView.setSearch(event.target.value);
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') { logView.closePanel(); return; }
    logView.onKeyDown(event);
});

// A click anywhere else closes the open panel, the buttons themselves
// toggle their panels in their own click handlers
document.addEventListener('mousedown', function(event) {
    if (logView.panelElement === null) { return; }
    if (event.target.closest('.toolbar .button-ghost') !== null) { return; }
    if (!logView.panelElement.contains(event.target)) { logView.closePanel(); }
});

shared.attachPaneResize(document.getElementById('log-list-resizer'),
    document.getElementById('log-list-pane'), 'x');

})();
