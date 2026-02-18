(function() {
    'use strict';

    var ZatoTabsManager = {

        instances: {},

        create: function(containerId, options) {
            var instance = {
                containerId: containerId,
                container: null,
                tabs: [],
                activeTabId: null,
                theme: (options && options.theme) || 'dark',
                closedTabsHistory: [],
                maxClosedTabsHistory: 20,
                pendingBatch: [],
                clearedMessagesBuffer: {},
                onTabChange: (options && options.onTabChange) || null,
                onTabClose: (options && options.onTabClose) || null,
                onTabAdd: (options && options.onTabAdd) || null,
                onTabRename: (options && options.onTabRename) || null,
                onTabReorder: (options && options.onTabReorder) || null,
                createTabData: (options && options.createTabData) || null
            };

            this.instances[containerId] = instance;
            return instance;
        },

        getInstance: function(containerId) {
            return this.instances[containerId] || null;
        },

        generateTabId: function() {
            return 'tab-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        },

        getTabById: function(instance, tabId) {
            for (var i = 0; i < instance.tabs.length; i++) {
                if (instance.tabs[i].id === tabId) {
                    return instance.tabs[i];
                }
            }
            return null;
        },

        getTabIndex: function(instance, tabId) {
            for (var i = 0; i < instance.tabs.length; i++) {
                if (instance.tabs[i].id === tabId) {
                    return i;
                }
            }
            return -1;
        },

        createDefaultTab: function(instance) {
            var tabData = {
                id: this.generateTabId(),
                title: 'Tab 1',
                messages: []
            };
            if (instance.createTabData) {
                var customData = instance.createTabData(1);
                for (var key in customData) {
                    if (customData.hasOwnProperty(key)) {
                        tabData[key] = customData[key];
                    }
                }
            }
            return tabData;
        },

        createNewTab: function(instance, tabCount) {
            var tabData = {
                id: this.generateTabId(),
                title: 'Tab ' + (tabCount + 1),
                messages: []
            };
            if (instance.createTabData) {
                var customData = instance.createTabData(tabCount + 1);
                for (var key in customData) {
                    if (customData.hasOwnProperty(key)) {
                        tabData[key] = customData[key];
                    }
                }
            }
            return tabData;
        },

        addTab: function(instance) {
            var newTab = this.createNewTab(instance, instance.tabs.length);
            instance.tabs.push(newTab);
            if (instance.onTabAdd) {
                instance.onTabAdd(newTab);
            }
            return newTab;
        },

        closeTab: function(instance, tabId) {
            if (instance.tabs.length <= 1) {
                return { tabs: instance.tabs, activeTabId: instance.activeTabId };
            }

            var tabIndex = this.getTabIndex(instance, tabId);
            if (tabIndex === -1) {
                return { tabs: instance.tabs, activeTabId: instance.activeTabId };
            }

            var closedTab = instance.tabs[tabIndex];
            instance.tabs.splice(tabIndex, 1);

            var newActiveTabId = instance.activeTabId;
            if (instance.activeTabId === tabId) {
                var newActiveIndex = Math.min(tabIndex, instance.tabs.length - 1);
                newActiveTabId = instance.tabs[newActiveIndex].id;
            }

            if (instance.onTabClose) {
                instance.onTabClose(closedTab);
            }

            return { tabs: instance.tabs, activeTabId: newActiveTabId };
        },

        renameTab: function(instance, tabId, newTitle) {
            var tab = this.getTabById(instance, tabId);
            if (!tab) {
                return false;
            }

            if (newTitle && newTitle.trim()) {
                tab.title = newTitle.trim();
                if (instance.onTabRename) {
                    instance.onTabRename(tab);
                }
                return true;
            }
            return false;
        },

        reorderTabs: function(instance, tabElements) {
            var newOrder = [];
            for (var i = 0; i < tabElements.length; i++) {
                var tabId = tabElements[i].getAttribute('data-tab-id');
                var tab = this.getTabById(instance, tabId);
                if (tab) {
                    newOrder.push(tab);
                }
            }
            instance.tabs = newOrder;
            if (instance.onTabReorder) {
                instance.onTabReorder(newOrder);
            }
            return newOrder;
        },

        toggleLock: function(instance, tabId) {
            var tab = this.getTabById(instance, tabId);
            if (tab) {
                tab.locked = !tab.locked;
                return true;
            }
            return false;
        },

        isLocked: function(instance, tabId) {
            var tab = this.getTabById(instance, tabId);
            return tab && tab.locked;
        },

        closeOthers: function(instance, tabId) {
            var tab = this.getTabById(instance, tabId);
            if (!tab) {
                return { tabs: instance.tabs, activeTabId: instance.activeTabId, closed: 0 };
            }

            var newTabs = [tab];
            var closed = 0;
            for (var i = 0; i < instance.tabs.length; i++) {
                if (instance.tabs[i].id !== tabId && instance.tabs[i].locked) {
                    newTabs.push(instance.tabs[i]);
                } else if (instance.tabs[i].id !== tabId) {
                    closed++;
                }
            }

            instance.tabs = newTabs;
            return { tabs: newTabs, activeTabId: tabId, closed: closed };
        },

        closeToRight: function(instance, tabId) {
            var tabIndex = this.getTabIndex(instance, tabId);
            if (tabIndex === -1) {
                return { tabs: instance.tabs, activeTabId: instance.activeTabId, closed: 0 };
            }

            var newTabs = instance.tabs.slice(0, tabIndex + 1);
            var closed = 0;
            for (var i = tabIndex + 1; i < instance.tabs.length; i++) {
                if (instance.tabs[i].locked) {
                    newTabs.push(instance.tabs[i]);
                } else {
                    closed++;
                }
            }

            var newActiveTabId = instance.activeTabId;
            if (!this.getTabById({ tabs: newTabs }, instance.activeTabId)) {
                newActiveTabId = tabId;
            }

            instance.tabs = newTabs;
            return { tabs: newTabs, activeTabId: newActiveTabId, closed: closed };
        },

        duplicateTab: function(instance, tabId) {
            var tab = this.getTabById(instance, tabId);
            if (!tab) {
                return null;
            }

            var newTitle = this.generateDuplicateTitle(instance, tab.title);

            var newTab = {
                id: this.generateTabId(),
                title: newTitle,
                messages: JSON.parse(JSON.stringify(tab.messages || [])),
                model: tab.model,
                tokensIn: tab.tokensIn || 0,
                tokensOut: tab.tokensOut || 0
            };

            var tabIndex = this.getTabIndex(instance, tabId);
            instance.tabs.splice(tabIndex + 1, 0, newTab);

            return newTab;
        },

        generateDuplicateTitle: function(instance, originalTitle) {
            var baseTitle = originalTitle.replace(/\s*\(\d+\)$/, '');

            var existingNumbers = [];
            for (var i = 0; i < instance.tabs.length; i++) {
                var title = instance.tabs[i].title;
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

        countClosableToRight: function(instance, tabId) {
            var tabIndex = this.getTabIndex(instance, tabId);
            if (tabIndex === -1) return 0;

            var count = 0;
            for (var i = tabIndex + 1; i < instance.tabs.length; i++) {
                if (!instance.tabs[i].locked) {
                    count++;
                }
            }
            return count;
        },

        countClosableOthers: function(instance, tabId) {
            var count = 0;
            for (var i = 0; i < instance.tabs.length; i++) {
                if (instance.tabs[i].id !== tabId && !instance.tabs[i].locked) {
                    count++;
                }
            }
            return count;
        },

        addToClosedHistory: function(instance, tab) {
            instance.pendingBatch.push(JSON.parse(JSON.stringify(tab)));
        },

        flushClosedHistory: function(instance) {
            if (instance.pendingBatch.length === 0) {
                return;
            }
            var entry = {
                tabs: instance.pendingBatch,
                closedAt: Date.now()
            };
            instance.closedTabsHistory.unshift(entry);
            instance.pendingBatch = [];
            if (instance.closedTabsHistory.length > instance.maxClosedTabsHistory) {
                instance.closedTabsHistory.pop();
            }
        },

        reopenClosedTabs: function(instance) {
            if (instance.closedTabsHistory.length === 0) {
                return [];
            }

            var entry = instance.closedTabsHistory.shift();
            var closedTabs = entry.tabs || (entry.tab ? [entry.tab] : []);

            var reopened = [];
            for (var i = 0; i < closedTabs.length; i++) {
                var tab = closedTabs[i];
                tab.id = this.generateTabId();
                instance.tabs.push(tab);
                reopened.push(tab);
            }

            return reopened;
        },

        hasClosedTabs: function(instance) {
            return instance.closedTabsHistory.length > 0;
        },

        togglePin: function(instance, tabId) {
            var tab = this.getTabById(instance, tabId);
            if (!tab) return false;

            var tabIndex = this.getTabIndex(instance, tabId);
            tab.pinned = !tab.pinned;

            if (tab.pinned) {
                instance.tabs.splice(tabIndex, 1);
                var insertIndex = 0;
                for (var i = 0; i < instance.tabs.length; i++) {
                    if (instance.tabs[i].pinned) {
                        insertIndex = i + 1;
                    } else {
                        break;
                    }
                }
                instance.tabs.splice(insertIndex, 0, tab);
            }
            return true;
        },

        isPinned: function(instance, tabId) {
            var tab = this.getTabById(instance, tabId);
            return tab && tab.pinned;
        },

        closeAll: function(instance) {
            var closedTabs = [];
            var newTabs = [];

            for (var i = 0; i < instance.tabs.length; i++) {
                if (instance.tabs[i].locked || instance.tabs[i].pinned) {
                    newTabs.push(instance.tabs[i]);
                } else {
                    closedTabs.push(instance.tabs[i]);
                }
            }

            for (var j = 0; j < closedTabs.length; j++) {
                this.addToClosedHistory(instance, closedTabs[j]);
            }

            if (newTabs.length === 0) {
                newTabs.push(this.createDefaultTab(instance));
            }

            var newActiveTabId = newTabs[0].id;
            for (var k = 0; k < newTabs.length; k++) {
                if (newTabs[k].id === instance.activeTabId) {
                    newActiveTabId = instance.activeTabId;
                    break;
                }
            }

            instance.tabs = newTabs;
            return { tabs: newTabs, activeTabId: newActiveTabId, closed: closedTabs.length };
        },

        clearMessages: function(instance, tabId) {
            var tab = this.getTabById(instance, tabId);
            if (!tab) return false;

            if (tab.messages && tab.messages.length > 0) {
                instance.clearedMessagesBuffer[tabId] = {
                    messages: JSON.parse(JSON.stringify(tab.messages)),
                    tokensIn: tab.tokensIn || 0,
                    tokensOut: tab.tokensOut || 0,
                    clearedAt: Date.now()
                };
            }

            tab.messages = [];
            tab.tokensIn = 0;
            tab.tokensOut = 0;
            return true;
        },

        canUndoClear: function(instance, tabId) {
            return !!instance.clearedMessagesBuffer[tabId];
        },

        undoClearMessages: function(instance, tabId) {
            var tab = this.getTabById(instance, tabId);
            var buffer = instance.clearedMessagesBuffer[tabId];
            if (!tab || !buffer) {
                return false;
            }

            tab.messages = buffer.messages;
            tab.tokensIn = buffer.tokensIn;
            tab.tokensOut = buffer.tokensOut;

            delete instance.clearedMessagesBuffer[tabId];
            return true;
        },

        setActiveTab: function(instance, tabId) {
            var tab = this.getTabById(instance, tabId);
            if (tab) {
                instance.activeTabId = tabId;
                if (instance.onTabChange) {
                    instance.onTabChange(tab);
                }
                return true;
            }
            return false;
        },

        getActiveTab: function(instance) {
            return this.getTabById(instance, instance.activeTabId);
        },

        copyToClipboard: function(instance, tabId) {
            var tab = this.getTabById(instance, tabId);
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

        exportAsMarkdown: function(instance, tabId) {
            var tab = this.getTabById(instance, tabId);
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

        exportAsJson: function(instance, tabId) {
            var tab = this.getTabById(instance, tabId);
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
        },

        getThemeClass: function(instance) {
            return 'zato-tabs-theme-' + instance.theme;
        },

        setTheme: function(instance, theme) {
            instance.theme = theme;
        }
    };

    window.ZatoTabsManager = ZatoTabsManager;

})();
