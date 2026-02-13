(function() {
    'use strict';

    var LLMChatTabs = {

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
            console.debug('LLMChatTabs.addTab: adding new tab');
            var newTab = this.createNewTab(tabs.length);
            tabs.push(newTab);
            console.debug('LLMChatTabs.addTab: new tab added:', JSON.stringify(newTab));
            return newTab;
        },

        closeTab: function(tabs, tabId, activeTabId) {
            console.debug('LLMChatTabs.closeTab: closing tab:', tabId);

            if (tabs.length <= 1) {
                console.debug('LLMChatTabs.closeTab: cannot close last tab');
                return { tabs: tabs, activeTabId: activeTabId };
            }

            var tabIndex = this.getTabIndex(tabs, tabId);
            if (tabIndex === -1) {
                console.debug('LLMChatTabs.closeTab: tab not found');
                return { tabs: tabs, activeTabId: activeTabId };
            }

            tabs.splice(tabIndex, 1);

            var newActiveTabId = activeTabId;
            if (activeTabId === tabId) {
                var newActiveIndex = Math.min(tabIndex, tabs.length - 1);
                newActiveTabId = tabs[newActiveIndex].id;
                console.debug('LLMChatTabs.closeTab: switched to tab:', newActiveTabId);
            }

            return { tabs: tabs, activeTabId: newActiveTabId };
        },

        renameTab: function(tabs, tabId, newTitle) {
            console.debug('LLMChatTabs.renameTab: renaming tab:', tabId);

            var tab = this.getTabById(tabs, tabId);
            if (!tab) {
                console.debug('LLMChatTabs.renameTab: tab not found');
                return false;
            }

            if (newTitle && newTitle.trim()) {
                tab.title = newTitle.trim();
                console.debug('LLMChatTabs.renameTab: new title:', tab.title);
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
            console.debug('LLMChatTabs.reorderTabs: tabs reordered:', JSON.stringify(newOrder.map(function(t) { return t.title; })));
            return newOrder;
        }
    };

    window.LLMChatTabs = LLMChatTabs;

})();
