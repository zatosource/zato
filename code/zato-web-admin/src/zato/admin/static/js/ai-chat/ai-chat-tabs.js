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

            var newTitle = this.generateDuplicateTitle(tabs, tab.title);

            var newTab = {
                id: this.generateTabId(),
                title: newTitle,
                messages: JSON.parse(JSON.stringify(tab.messages)),
                model: tab.model,
                tokensIn: tab.tokensIn || 0,
                tokensOut: tab.tokensOut || 0
            };

            var tabIndex = this.getTabIndex(tabs, tabId);
            tabs.splice(tabIndex + 1, 0, newTab);

            return newTab;
        },

        generateDuplicateTitle: function(tabs, originalTitle) {
            var baseTitle = originalTitle.replace(/\s*\(\d+\)$/, '');
            
            var existingNumbers = [];
            for (var i = 0; i < tabs.length; i++) {
                var title = tabs[i].title;
                if (title === baseTitle) {
                    existingNumbers.push(1);
                } else if (title.indexOf(baseTitle + ' (') === 0) {
                    var match = title.match(/\((\d+)\)$/);
                    if (match) {
                        existingNumbers.push(parseInt(match[1], 10));
                    }
                }
            }

            var nextNumber = 2;
            if (existingNumbers.length > 0) {
                existingNumbers.sort(function(a, b) { return a - b; });
                nextNumber = existingNumbers[existingNumbers.length - 1] + 1;
            }

            return baseTitle + ' (' + nextNumber + ')';
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
            console.log('[CLOSED-TABS] addToClosedHistory called');
            console.log('[CLOSED-TABS] tab to add:', JSON.stringify({
                id: tab.id,
                title: tab.title,
                messagesCount: tab.messages ? tab.messages.length : 0
            }));
            console.log('[CLOSED-TABS] history length before:', this.closedTabsHistory.length);

            var entry = {
                tab: JSON.parse(JSON.stringify(tab)),
                closedAt: Date.now()
            };
            this.closedTabsHistory.unshift(entry);
            if (this.closedTabsHistory.length > this.maxClosedTabsHistory) {
                console.log('[CLOSED-TABS] trimming history, exceeded max:', this.maxClosedTabsHistory);
                this.closedTabsHistory.pop();
            }
            console.log('[CLOSED-TABS] history length after:', this.closedTabsHistory.length);
            this.saveClosedHistory();
        },

        saveClosedHistory: function() {
            console.log('[CLOSED-TABS] saveClosedHistory called, entries:', this.closedTabsHistory.length);
            try {
                var data = JSON.stringify(this.closedTabsHistory);
                console.log('[CLOSED-TABS] saving to localStorage, size:', data.length, 'bytes');
                localStorage.setItem('zato.ai-chat.closed-tabs', data);
                console.log('[CLOSED-TABS] saved successfully');
            } catch (e) {
                console.log('[CLOSED-TABS] failed to save closed history:', e);
            }
        },

        loadClosedHistory: function() {
            console.log('[CLOSED-TABS] loadClosedHistory called');
            try {
                var data = localStorage.getItem('zato.ai-chat.closed-tabs');
                console.log('[CLOSED-TABS] loaded from localStorage:', data ? data.length + ' bytes' : 'null');
                if (data) {
                    this.closedTabsHistory = JSON.parse(data);
                    console.log('[CLOSED-TABS] parsed entries:', this.closedTabsHistory.length);
                    for (var i = 0; i < this.closedTabsHistory.length; i++) {
                        var entry = this.closedTabsHistory[i];
                        console.log('[CLOSED-TABS] entry ' + i + ':', JSON.stringify({
                            title: entry.tab.title,
                            closedAt: new Date(entry.closedAt).toISOString(),
                            messagesCount: entry.tab.messages ? entry.tab.messages.length : 0
                        }));
                    }
                } else {
                    console.log('[CLOSED-TABS] no saved history found');
                }
            } catch (e) {
                console.log('[CLOSED-TABS] failed to load closed history:', e);
            }
        },

        reopenClosedTab: function(tabs) {
            console.log('[CLOSED-TABS] reopenClosedTab called');
            console.log('[CLOSED-TABS] current history length:', this.closedTabsHistory.length);
            console.log('[CLOSED-TABS] current tabs count:', tabs.length);

            if (this.closedTabsHistory.length === 0) {
                console.log('[CLOSED-TABS] no closed tabs to reopen');
                return null;
            }

            var entry = this.closedTabsHistory.shift();
            console.log('[CLOSED-TABS] reopening entry:', JSON.stringify({
                title: entry.tab.title,
                closedAt: new Date(entry.closedAt).toISOString(),
                messagesCount: entry.tab.messages ? entry.tab.messages.length : 0
            }));

            this.saveClosedHistory();
            console.log('[CLOSED-TABS] history length after shift:', this.closedTabsHistory.length);

            var tab = entry.tab;
            var oldId = tab.id;
            tab.id = this.generateTabId();
            console.log('[CLOSED-TABS] generated new tab id:', tab.id, '(was:', oldId + ')');

            tabs.push(tab);
            console.log('[CLOSED-TABS] tabs count after push:', tabs.length);
            console.log('[CLOSED-TABS] reopened tab:', JSON.stringify({
                id: tab.id,
                title: tab.title,
                messagesCount: tab.messages ? tab.messages.length : 0
            }));

            return tab;
        },

        hasClosedTabs: function() {
            var has = this.closedTabsHistory.length > 0;
            console.log('[CLOSED-TABS] hasClosedTabs:', has, '(count:', this.closedTabsHistory.length + ')');
            return has;
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

        clearedMessagesBuffer: {},

        clearMessages: function(tabs, tabId) {
            var tab = this.getTabById(tabs, tabId);
            if (!tab) return false;

            if (tab.messages && tab.messages.length > 0) {
                this.clearedMessagesBuffer[tabId] = {
                    messages: JSON.parse(JSON.stringify(tab.messages)),
                    tokensIn: tab.tokensIn || 0,
                    tokensOut: tab.tokensOut || 0,
                    clearedAt: Date.now()
                };
                console.log('[CLOSED-TABS] stored cleared messages for tab:', tabId, 'count:', tab.messages.length);
            }

            tab.messages = [];
            tab.tokensIn = 0;
            tab.tokensOut = 0;
            return true;
        },

        canUndoClear: function(tabId) {
            return !!this.clearedMessagesBuffer[tabId];
        },

        undoClearMessages: function(tabs, tabId) {
            var tab = this.getTabById(tabs, tabId);
            var buffer = this.clearedMessagesBuffer[tabId];
            if (!tab || !buffer) {
                console.log('[CLOSED-TABS] undoClearMessages: no buffer for tab:', tabId);
                return false;
            }

            console.log('[CLOSED-TABS] undoClearMessages: restoring', buffer.messages.length, 'messages to tab:', tabId);
            tab.messages = buffer.messages;
            tab.tokensIn = buffer.tokensIn;
            tab.tokensOut = buffer.tokensOut;

            delete this.clearedMessagesBuffer[tabId];
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
