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
        },

        toggleLock: function(tabs, tabId) {
            var tab = this.getTabById(tabs, tabId);
            if (tab) {
                tab.locked = !tab.locked;
                return true;
            }
            return false;
        },

        isLocked: function(tabs, tabId) {
            var tab = this.getTabById(tabs, tabId);
            return tab && tab.locked;
        },

        closeOthers: function(tabs, tabId, activeTabId) {
            var tab = this.getTabById(tabs, tabId);
            if (!tab) {
                return { tabs: tabs, activeTabId: activeTabId, closed: 0 };
            }

            var newTabs = [tab];
            var closed = 0;
            for (var i = 0; i < tabs.length; i++) {
                if (tabs[i].id !== tabId && tabs[i].locked) {
                    newTabs.push(tabs[i]);
                } else if (tabs[i].id !== tabId) {
                    closed++;
                }
            }

            return { tabs: newTabs, activeTabId: tabId, closed: closed };
        },

        closeToRight: function(tabs, tabId, activeTabId) {
            var tabIndex = this.getTabIndex(tabs, tabId);
            if (tabIndex === -1) {
                return { tabs: tabs, activeTabId: activeTabId, closed: 0 };
            }

            var newTabs = tabs.slice(0, tabIndex + 1);
            var closed = 0;
            for (var i = tabIndex + 1; i < tabs.length; i++) {
                if (tabs[i].locked) {
                    newTabs.push(tabs[i]);
                } else {
                    closed++;
                }
            }

            var newActiveTabId = activeTabId;
            if (!this.getTabById(newTabs, activeTabId)) {
                newActiveTabId = tabId;
            }

            return { tabs: newTabs, activeTabId: newActiveTabId, closed: closed };
        },

        duplicateTab: function(tabs, tabId) {
            var tab = this.getTabById(tabs, tabId);
            if (!tab) {
                return null;
            }

            var newTab = {
                id: this.generateTabId(),
                title: tab.title + ' (copy)',
                messages: JSON.parse(JSON.stringify(tab.messages)),
                model: tab.model,
                tokensIn: tab.tokensIn || 0,
                tokensOut: tab.tokensOut || 0
            };

            var tabIndex = this.getTabIndex(tabs, tabId);
            tabs.splice(tabIndex + 1, 0, newTab);

            return newTab;
        },

        countClosableToRight: function(tabs, tabId) {
            var tabIndex = this.getTabIndex(tabs, tabId);
            if (tabIndex === -1) return 0;

            var count = 0;
            for (var i = tabIndex + 1; i < tabs.length; i++) {
                if (!tabs[i].locked) {
                    count++;
                }
            }
            return count;
        },

        countClosableOthers: function(tabs, tabId) {
            var count = 0;
            for (var i = 0; i < tabs.length; i++) {
                if (tabs[i].id !== tabId && !tabs[i].locked) {
                    count++;
                }
            }
            return count;
        },

        closedTabsHistory: [],
        maxClosedTabsHistory: 20,

        addToClosedHistory: function(tab) {
            var entry = {
                tab: JSON.parse(JSON.stringify(tab)),
                closedAt: Date.now()
            };
            this.closedTabsHistory.unshift(entry);
            if (this.closedTabsHistory.length > this.maxClosedTabsHistory) {
                this.closedTabsHistory.pop();
            }
            this.saveClosedHistory();
        },

        saveClosedHistory: function() {
            try {
                localStorage.setItem('zato.ai-chat.closed-tabs', JSON.stringify(this.closedTabsHistory));
            } catch (e) {
                console.debug('AIChatTabs: failed to save closed history', e);
            }
        },

        loadClosedHistory: function() {
            try {
                var data = localStorage.getItem('zato.ai-chat.closed-tabs');
                if (data) {
                    this.closedTabsHistory = JSON.parse(data);
                }
            } catch (e) {
                console.debug('AIChatTabs: failed to load closed history', e);
            }
        },

        reopenClosedTab: function(tabs) {
            if (this.closedTabsHistory.length === 0) {
                return null;
            }
            var entry = this.closedTabsHistory.shift();
            this.saveClosedHistory();
            var tab = entry.tab;
            tab.id = this.generateTabId();
            tabs.push(tab);
            return tab;
        },

        hasClosedTabs: function() {
            return this.closedTabsHistory.length > 0;
        },

        togglePin: function(tabs, tabId) {
            var tab = this.getTabById(tabs, tabId);
            if (!tab) return false;

            var tabIndex = this.getTabIndex(tabs, tabId);
            tab.pinned = !tab.pinned;

            if (tab.pinned) {
                tabs.splice(tabIndex, 1);
                var insertIndex = 0;
                for (var i = 0; i < tabs.length; i++) {
                    if (tabs[i].pinned) {
                        insertIndex = i + 1;
                    } else {
                        break;
                    }
                }
                tabs.splice(insertIndex, 0, tab);
            }
            return true;
        },

        isPinned: function(tabs, tabId) {
            var tab = this.getTabById(tabs, tabId);
            return tab && tab.pinned;
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

        clearMessages: function(tabs, tabId) {
            var tab = this.getTabById(tabs, tabId);
            if (!tab) return false;

            if (tab.messages && tab.messages.length > 0) {
                this.addToClosedHistory({
                    id: tab.id,
                    title: tab.title + ' (cleared)',
                    messages: tab.messages,
                    model: tab.model,
                    tokensIn: tab.tokensIn,
                    tokensOut: tab.tokensOut
                });
            }

            tab.messages = [];
            tab.tokensIn = 0;
            tab.tokensOut = 0;
            return true;
        },

        copyToClipboard: function(tabs, tabId) {
            var tab = this.getTabById(tabs, tabId);
            if (!tab || !tab.messages || tab.messages.length === 0) return false;

            var text = '';
            for (var i = 0; i < tab.messages.length; i++) {
                var msg = tab.messages[i];
                var role = msg.role.charAt(0).toUpperCase() + msg.role.slice(1);
                text += role + ':\n' + msg.content + '\n\n';
            }

            navigator.clipboard.writeText(text.trim());
            return true;
        },

        exportAsMarkdown: function(tabs, tabId) {
            var tab = this.getTabById(tabs, tabId);
            if (!tab) return null;

            var md = '# ' + tab.title + '\n\n';
            if (tab.messages) {
                for (var i = 0; i < tab.messages.length; i++) {
                    var msg = tab.messages[i];
                    if (msg.role === 'user') {
                        md += '## User\n\n' + msg.content + '\n\n';
                    } else if (msg.role === 'assistant') {
                        md += '## Assistant\n\n' + msg.content + '\n\n';
                    } else {
                        md += '## ' + msg.role.charAt(0).toUpperCase() + msg.role.slice(1) + '\n\n' + msg.content + '\n\n';
                    }
                }
            }
            return md;
        },

        exportAsJson: function(tabs, tabId) {
            var tab = this.getTabById(tabs, tabId);
            if (!tab) return null;

            var data = {
                title: tab.title,
                model: tab.model,
                tokensIn: tab.tokensIn || 0,
                tokensOut: tab.tokensOut || 0,
                messages: tab.messages || [],
                exportedAt: new Date().toISOString()
            };
            return JSON.stringify(data, null, 2);
        },

        downloadFile: function(content, filename, mimeType) {
            var blob = new Blob([content], { type: mimeType });
            var url = URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    };

    window.AIChatTabs = AIChatTabs;

})();
