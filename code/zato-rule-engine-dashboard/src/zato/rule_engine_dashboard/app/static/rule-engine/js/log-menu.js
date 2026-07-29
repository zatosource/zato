'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

logView.openRowMenu = function(event, decisionId) {
    event.preventDefault();
    var record = logModel.itemById(decisionId);
    var self = this;

    var items = [
        {label: 'Open', destructive: false,
            action: function() { self.select(decisionId); }},
    ];

    if (record.has_payload) {
        items.push({label: 'Add to test set', destructive: false,
            action: function() {
                self.select(decisionId);
                var row = document.querySelector('.log-row-selected');
                logModel.addToTestSet(function(suiteName) {
                    shared.popover(row, 'Added to ' + suiteName + ' as a scenario.', 'green');
                }, function(message) { shared.popover(row, message, 'red'); });
            }});

        items.push({label: 'Replay against v' + logModel.currentVersion, destructive: false,
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
        action: function() {
            navigator.clipboard.writeText(decisionId);
            var row = document.querySelector('[data-decision="' + decisionId + '"]');
            shared.popover(row, 'Copied ' + decisionId + '.');
        }});

    if (record.business_key !== null) {
        items.push({label: 'Everything for ' + record.business_key, destructive: false,
            action: function() {
                document.getElementById('log-search').value = record.business_key;
                self.setSearch(record.business_key);
            }});
    }

    items.push({label: 'Everything ' + logModel.config.outcomeLabels[record.outcome], destructive: false,
        action: function() { self.toggleOutcome(record.outcome); }});

    var title = record.business_key === null
        ? logView.shortId(record.decision_id)
        : logView.shortId(record.decision_id) + ' \u00b7 ' + record.business_key;
    shared.openContextMenu(title, items, event.clientX, event.clientY);
};

// ////////////////////////////////////////////////////////////////////////

logView.openValueMenu = function(event, path, value) {
    event.preventDefault();
    var phrase = logModel.phraseFor(path);
    var self = this;

    var items = [
        {label: 'Everything for ' + value, destructive: false,
            action: function() { self.setValueFilter(path, value); }},
        {label: 'Copy value', destructive: false,
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
