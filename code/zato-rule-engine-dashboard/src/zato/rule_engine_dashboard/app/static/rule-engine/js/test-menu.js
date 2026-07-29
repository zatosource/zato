'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

testView.scenarioMenuItems = function(index, anchor) {
    var self = this;
    var scenario = testModel.scenarioAt(index);
    var items = [];

    items.push({label: 'Run this scenario', destructive: false,
        action: function() {
            testModel.runOne(scenario, function(entry) {
                shared.popover(anchor, 'Ran "' + scenario.name + '", ' + self.statusLabels[entry.status] + '.');
                self.render();
            }, function(message) {
                shared.popover(anchor, message, 'red');
            });
        }});

    items.push({label: 'Duplicate', destructive: false,
        action: function() {
            testModel.duplicateScenario(index);
            self.selectScenario(index + 1);
        }});

    items.push(null);
    items.push({label: 'Move up', destructive: false,
        action: function() {
            if (testModel.moveScenario(index, -1)) {
                if (self.selectedIndex === index) { self.selectedIndex -= 1; }
                self.render();
            }
        }});
    items.push({label: 'Move down', destructive: false,
        action: function() {
            if (testModel.moveScenario(index, 1)) {
                if (self.selectedIndex === index) { self.selectedIndex += 1; }
                self.render();
            }
        }});

    items.push(null);
    items.push({label: 'Delete', destructive: true,
        action: function() {
            testModel.deleteScenario(index);
            if (self.selectedIndex >= testModel.suite.scenarios.length) {
                self.selectedIndex = Math.max(0, testModel.suite.scenarios.length - 1);
            }
            self.render();
        }});

    return items;
};

// ////////////////////////////////////////////////////////////////////////

testView.attachScenarioMenu = function() {
    var self = this;
    var list = document.getElementById('test-set-list');

    list.addEventListener('contextmenu', function(event) {
        var item = event.target.closest('.test-set-item');
        if (item === null) { return; }
        event.preventDefault();

        var index = parseInt(item.getAttribute('data-index'));
        var scenario = testModel.scenarioAt(index);
        shared.openContextMenu(scenario.name, self.scenarioMenuItems(index, item),
            event.clientX, event.clientY);
    });
};

testView.attachScenarioMenu();

})();
