'use strict';

// The right-click menu of the decision list, the same menu machinery
// as everywhere else. Augments the logView namespace.

(function() {

// ////////////////////////////////////////////////////////////////////////

logView.openRowMenu = function(event, decisionId) {
    event.preventDefault();
    var record = logModel.itemById(decisionId);
    var self = this;

    var items = [
        {label: 'Open', destructive: false,
            description: 'Opens this decision\'s full story in the pane on the right.',
            action: function() { self.select(decisionId); }},
    ];

    // Only a decision that kept its story can be copied or replayed
    if (record.has_payload) {
        items.push({label: 'Add to test set', destructive: false,
            description: 'Turns this stored decision into a scenario, what went out becomes the expectations.',
            action: function() {
                self.select(decisionId);
                var row = document.querySelector('.log-row-selected');
                logModel.addToTestSet(function(suiteName) {
                    shared.popover(row, 'Added to ' + suiteName + ' as a scenario.', 'green');
                }, function(message) { shared.popover(row, message, 'red'); });
            }});

        items.push({label: 'Replay against v' + logModel.currentVersion, destructive: false,
            description: 'Runs this same input against the newest stored version and shows what would change.',
            action: function() {
                self.select(decisionId);
                var row = document.querySelector('.log-row-selected');
                logModel.replay(function() {
                    self.renderDetail();
                    shared.initTips();
                }, function(message) { shared.popover(row, message, 'red'); });
            }});
    }

    items.push(null);

    items.push({label: 'Copy decision id', destructive: false,
        description: 'The id is the handle for support: paste it anywhere, search it here later.',
        action: function() {
            navigator.clipboard.writeText(decisionId);
            var row = document.querySelector('[data-decision="' + decisionId + '"]');
            shared.popover(row, 'Copied ' + decisionId + '.');
        }});

    if (record.business_key !== null) {
        items.push({label: 'Everything for ' + record.business_key, destructive: false,
            description: 'Filters the list to every decision keyed to ' + record.business_key + '.',
            action: function() {
                document.getElementById('log-search').value = record.business_key;
                self.setSearch(record.business_key);
            }});
    }

    items.push({label: 'Everything ' + logModel.config.outcomeLabels[record.outcome], destructive: false,
        description: 'Filters the list to every decision with this outcome, same as clicking its card above.',
        action: function() { self.toggleOutcome(record.outcome); }});

    var title = record.business_key === null
        ? logView.shortId(record.decision_id)
        : logView.shortId(record.decision_id) + ' \u00b7 ' + record.business_key;
    shared.openContextMenu(title, items, event.clientX, event.clientY);
};

// ////////////////////////////////////////////////////////////////////////

// The menu of a value cell in the opened decision: "show me everything
// for the value I clicked", plus the copy
logView.openValueMenu = function(event, path, value) {
    event.preventDefault();
    var phrase = logModel.phraseFor(path);
    var self = this;

    var items = [
        {label: 'Everything for ' + value, destructive: false,
            description: 'Filters the list to every decision where ' + phrase + ' is ' + value +
                ', coming in or going out.',
            action: function() { self.setValueFilter(path, value); }},
        {label: 'Copy value', destructive: false,
            description: 'Copies ' + value + ' to the clipboard.',
            action: function() {
                navigator.clipboard.writeText(value);
                shared.popover(event.target, 'Copied ' + value + '.');
            }},
    ];

    shared.openContextMenu(phrase + ' = ' + value, items, event.clientX, event.clientY);
};

// ////////////////////////////////////////////////////////////////////////

document.getElementById('log-list').addEventListener('contextmenu', function(event) {
    var row = event.target.closest('.log-row');
    if (row === null) { return; }
    logView.openRowMenu(event, row.dataset.decision);
});

})();
