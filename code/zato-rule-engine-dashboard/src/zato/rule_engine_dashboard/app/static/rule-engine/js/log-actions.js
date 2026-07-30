'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

logView.setSearch = function(value) {
    var self = this;

    this.search = value;

    if (this.searchTimer !== null) { clearTimeout(this.searchTimer); }
    this.searchTimer = setTimeout(function() {
        self.searchTimer = null;
        self.render();
    }, logModel.config.searchDelayMilliseconds);
};

logView.setRange = function(select) {
    var self = this;
    this.rangeDays = +select.value;
    logModel.refresh(this.rangeDays, this.outcome, function() { self.render(); });
};

logView.toggleOutcome = function(outcome) {
    var self = this;
    this.outcome = this.outcome === outcome ? null : outcome;
    logModel.refresh(this.rangeDays, this.outcome, function() { self.render(); });
};

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

logView.copyText = function(event, text) {
    event.stopPropagation();
    navigator.clipboard.writeText(text);
    shared.popover(event.target.closest('span'), 'Copied ' + text + '.', 'green');
};

// ////////////////////////////////////////////////////////////////////////

logView.addToTestSet = function(anchor) {
    var handlers = shared.inFlight(anchor, function(suiteName) {
        shared.popover(anchor, 'Added to ' + suiteName + ' as a scenario', 'green');
    }, function(message) { shared.popover(anchor, message, 'red'); });
    if (handlers === null) { return; }

    logModel.addToTestSet(handlers.done, handlers.error);
};

logView.replay = function(anchor) {
    var self = this;

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
        next = Math.max(0, Math.min(records.length - 1, position + steps[event.key]));
    }

    if (records[next].decision_id === this.selectedId) { return; }
    this.select(records[next].decision_id);

    var row = document.querySelector('.log-row-selected');
    if (row !== null) { row.scrollIntoView({block: 'nearest'}); }
};

// ////////////////////////////////////////////////////////////////////////

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

logView.openCapturePanel = function(button) {
    if (this.panelElement !== null) { this.closePanel(); return; }

    var readout = logModel.captureReadout();
    var html = '<div class="log-capture-row"><span>Searchable header of every decision</span><b>always kept</b></div>' +
        '<div class="log-capture-row"><span>Full story of every error</span><b>always kept</b></div>' +
        '<div class="log-capture-row"><span>Full stories of successes on this page</span><b>' +
            readout.successKept + ' of ' + readout.successTotal + '</b></div>';

    this.showPanel(button, html);
};

logView.openRuleCounts = function(button) {
    if (this.panelElement !== null) { this.closePanel(); return; }
    var self = this;

    logModel.ruleCounts(this.rangeDays, function(counts) {
        var html = '';

        Object.keys(counts.totals).sort().forEach(function(rule) {
            html += '<div class="log-capture-row"><span>' + shared.escape(rule) + '</span><b>' +
                counts.totals[rule] + '</b></div>';
        });

        counts.neverFired.forEach(function(rule) {
            html += '<div class="log-capture-row"><span>' + shared.escape(rule) + '</span><b>never fired</b></div>';
        });

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

document.addEventListener('mousedown', function(event) {
    if (logView.panelElement === null) { return; }
    if (event.target.closest('.toolbar .button-ghost') !== null) { return; }
    if (!logView.panelElement.contains(event.target)) { logView.closePanel(); }
});

shared.attachPaneResize(document.getElementById('log-list-resizer'),
    document.getElementById('log-list-pane'), 'x');

})();
