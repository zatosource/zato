(function() {
    'use strict';

    var AIChatTabs = {

        instance: null,

        init: function() {
            this.instance = ZatoTabsManager.create('ai-chat', {
                theme: 'dark',
                createTabData: function(tabNumber) {
                    return {
                        title: 'Chat ' + tabNumber
                    };
                }
            });
        },

        generateTabId: function() {
            return ZatoTabsManager.generateTabId();
        },

        getTabById: function(tabs, tabId) {
            return ZatoTabsManager.getTabById({ tabs: tabs }, tabId);
        },

        getTabIndex: function(tabs, tabId) {
            return ZatoTabsManager.getTabIndex({ tabs: tabs }, tabId);
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
            var tempInstance = { tabs: tabs, activeTabId: activeTabId };
            return ZatoTabsManager.closeTab(tempInstance, tabId);
        },

        renameTab: function(tabs, tabId, newTitle) {
            return ZatoTabsManager.renameTab({ tabs: tabs }, tabId, newTitle);
        },

        reorderTabs: function(tabs, tabElements) {
            var tempInstance = { tabs: tabs };
            return ZatoTabsManager.reorderTabs(tempInstance, tabElements);
        },

        toggleLock: function(tabs, tabId) {
            return ZatoTabsManager.toggleLock({ tabs: tabs }, tabId);
        },

        isLocked: function(tabs, tabId) {
            return ZatoTabsManager.isLocked({ tabs: tabs }, tabId);
        },

        closeOthers: function(tabs, tabId, activeTabId) {
            var tempInstance = { tabs: tabs, activeTabId: activeTabId };
            var result = ZatoTabsManager.closeOthers(tempInstance, tabId);
            return result;
        },

        closeToRight: function(tabs, tabId, activeTabId) {
            var tempInstance = { tabs: tabs, activeTabId: activeTabId };
            var result = ZatoTabsManager.closeToRight(tempInstance, tabId);
            return result;
        },

        duplicateTab: function(tabs, tabId) {
            var tempInstance = { tabs: tabs };
            return ZatoTabsManager.duplicateTab(tempInstance, tabId);
        },

        generateDuplicateTitle: function(tabs, originalTitle) {
            return ZatoTabsManager.generateDuplicateTitle({ tabs: tabs }, originalTitle);
        },

        countClosableToRight: function(tabs, tabId) {
            return ZatoTabsManager.countClosableToRight({ tabs: tabs }, tabId);
        },

        countClosableOthers: function(tabs, tabId) {
            return ZatoTabsManager.countClosableOthers({ tabs: tabs }, tabId);
        },

        closedTabsHistory: [],
        maxClosedTabsHistory: 20,
        pendingBatch: [],

        addToClosedHistory: function(tab) {
            this.pendingBatch.push(JSON.parse(JSON.stringify(tab)));
        },

        flushClosedHistory: function() {
            if (this.pendingBatch.length === 0) {
                return;
            }
            var entry = {
                tabs: this.pendingBatch,
                closedAt: Date.now()
            };
            this.closedTabsHistory.unshift(entry);
            this.pendingBatch = [];
            if (this.closedTabsHistory.length > this.maxClosedTabsHistory) {
                this.closedTabsHistory.pop();
            }
            this.saveClosedHistory();
        },

        saveClosedHistory: function() {
            try {
                var data = JSON.stringify(this.closedTabsHistory);
                localStorage.setItem('zato.ai-chat.closed-tabs', data);
            } catch (e) {
                console.log('[AIChatTabs] failed to save closed history:', e);
            }
        },

        loadClosedHistory: function() {
            try {
                var data = localStorage.getItem('zato.ai-chat.closed-tabs');
                if (data) {
                    this.closedTabsHistory = JSON.parse(data);
                }
            } catch (e) {
                console.log('[AIChatTabs] failed to load closed history:', e);
            }
        },

        reopenClosedTabs: function(tabs) {
            if (this.closedTabsHistory.length === 0) {
                return [];
            }

            var entry = this.closedTabsHistory.shift();
            var closedTabs = entry.tabs || (entry.tab ? [entry.tab] : []);

            var reopened = [];
            for (var i = 0; i < closedTabs.length; i++) {
                var tab = closedTabs[i];
                tab.id = this.generateTabId();
                tabs.push(tab);
                reopened.push(tab);
            }

            this.saveClosedHistory();
            return reopened;
        },

        hasClosedTabs: function() {
            return this.closedTabsHistory.length > 0;
        },

        togglePin: function(tabs, tabId) {
            var tempInstance = { tabs: tabs };
            return ZatoTabsManager.togglePin(tempInstance, tabId);
        },

        isPinned: function(tabs, tabId) {
            return ZatoTabsManager.isPinned({ tabs: tabs }, tabId);
        },

        closeAll: function(tabs, activeTabId) {
            var closedTabs = [];
            var newTabs = [];

            for (var i = 0; i < tabs.length; i++) {
                if (tabs[i].locked || tabs[i].pinned) {
                    newTabs.push(tabs[i]);
                } else {
                    closedTabs.push(tabs[i]);
                }
            }

            for (var j = 0; j < closedTabs.length; j++) {
                this.addToClosedHistory(closedTabs[j]);
            }

            if (newTabs.length === 0) {
                newTabs.push(this.createDefaultTab());
            }

            var newActiveTabId = newTabs[0].id;
            for (var k = 0; k < newTabs.length; k++) {
                if (newTabs[k].id === activeTabId) {
                    newActiveTabId = activeTabId;
                    break;
                }
            }

            return { tabs: newTabs, activeTabId: newActiveTabId, closed: closedTabs.length };
        },

        clearedMessagesBuffer: {},

        clearMessages: function(tabs, tabId) {
            var tempInstance = { tabs: tabs, clearedMessagesBuffer: this.clearedMessagesBuffer };
            var result = ZatoTabsManager.clearMessages(tempInstance, tabId);
            this.clearedMessagesBuffer = tempInstance.clearedMessagesBuffer;
            return result;
        },

        canUndoClear: function(tabId) {
            return !!this.clearedMessagesBuffer[tabId];
        },

        undoClearMessages: function(tabs, tabId) {
            var tempInstance = { tabs: tabs, clearedMessagesBuffer: this.clearedMessagesBuffer };
            var result = ZatoTabsManager.undoClearMessages(tempInstance, tabId);
            this.clearedMessagesBuffer = tempInstance.clearedMessagesBuffer;
            return result;
        },

        copyToClipboard: function(tabs, tabId) {
            return ZatoTabsManager.copyToClipboard({ tabs: tabs }, tabId);
        },

        exportAsMarkdown: function(tabs, tabId) {
            return ZatoTabsManager.exportAsMarkdown({ tabs: tabs }, tabId);
        },

        exportAsJson: function(tabs, tabId) {
            return ZatoTabsManager.exportAsJson({ tabs: tabs }, tabId);
        },

        downloadFile: function(content, filename, mimeType) {
            ZatoTabsManager.downloadFile(content, filename, mimeType);
        }
    };

    window.AIChatTabs = AIChatTabs;

})();
