(function() {
    'use strict';

    var AIChatTabs = {

        generateTabId: function() {
            return 'tab-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        },

        getTabById: function(tabs, tabId) {
            for (var i = 0; i < tabs.length; i++) {
                if (tabs[i].id === tabId) {
                    return tabs[i];
                }
            }
            return null;
        },

        getTabIndex: function(tabs, tabId) {
            for (var i = 0; i < tabs.length; i++) {
                if (tabs[i].id === tabId) {
                    return i;
                }
            }
            return -1;
        },

        createDefaultTab: function() {
            return {
                id: this.generateTabId(),
                title: 'Chat 1',
                messages: []
            };
        },

        createNewTab: function(tabCount) {
            return {
                id: this.generateTabId(),
                title: 'Chat ' + (tabCount + 1),
                messages: []
            };
        },

        addTab: function(tabs) {
            var newTab = this.createNewTab(tabs.length);
            tabs.push(newTab);
            return newTab;
        },

        closeTab: function(tabs, tabId, activeTabId) {

            if (tabs.length <= 1) {
                return { tabs: tabs, activeTabId: activeTabId };
            }

            var tabIndex = this.getTabIndex(tabs, tabId);
            if (tabIndex === -1) {
                return { tabs: tabs, activeTabId: activeTabId };
            }

            tabs.splice(tabIndex, 1);

            var newActiveTabId = activeTabId;
            if (activeTabId === tabId) {
                var newActiveIndex = Math.min(tabIndex, tabs.length - 1);
                newActiveTabId = tabs[newActiveIndex].id;
            }

            return { tabs: tabs, activeTabId: newActiveTabId };
        },

        renameTab: function(tabs, tabId, newTitle) {

            var tab = this.getTabById(tabs, tabId);
            if (!tab) {
                return false;
            }

            if (newTitle && newTitle.trim()) {
                tab.title = newTitle.trim();
                return true;
            }
            return false;
        },

        reorderTabs: function(tabs, tabElements) {
            var newOrder = [];
            for (var i = 0; i < tabElements.length; i++) {
                var tabId = tabElements[i].getAttribute('data-tab-id');
                var tab = this.getTabById(tabs, tabId);
                if (tab) {
                    newOrder.push(tab);
                }
            }
            return newOrder;
        }
    };

    window.AIChatTabs = AIChatTabs;

})();
