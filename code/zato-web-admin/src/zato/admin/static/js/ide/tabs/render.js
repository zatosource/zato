(function() {
    'use strict';

    ZatoIDETabs.renderTabs = function(instance) {
        if (!instance.tabsManager || !instance.tabsManager.container) {
            return;
        }

        var tabsInstance = {
            containerId: instance.id + '-tabs',
            tabs: instance.tabsManager.tabs,
            activeTabId: instance.tabsManager.activeTabId,
            allowCloseLastTab: instance.tabsManager.allowCloseLastTab,
            theme: instance.options.theme,
            closedTabsHistory: instance.closedTabsHistory || [],
            clearedMessagesBuffer: instance.clearedMessagesBuffer || {}
        };

        var options = {
            theme: instance.options.theme,
            showAddButton: true,
            showCloseButton: true,
            showPinIcon: true,
            showLockIcon: true,
            addButtonTitle: 'New file',
            containerClass: 'zato-ide-tabs'
        };

        var html = ZatoTabsRenderer.buildTabsHtml(tabsInstance, options);
        instance.tabsManager.container.innerHTML = html;
    };

    ZatoIDETabs.bindTabEvents = function(instance) {
        var self = this;
        var container = instance.tabsManager.container;
        if (!container) {
            return;
        }

        if (!instance.closedTabsHistory) {
            instance.closedTabsHistory = [];
        }
        if (!instance.clearedMessagesBuffer) {
            instance.clearedMessagesBuffer = {};
        }

        var tabsInstance = {
            containerId: instance.id + '-tabs',
            tabs: instance.tabsManager.tabs,
            activeTabId: instance.tabsManager.activeTabId,
            allowCloseLastTab: instance.tabsManager.allowCloseLastTab,
            theme: instance.options.theme,
            closedTabsHistory: instance.closedTabsHistory,
            clearedMessagesBuffer: instance.clearedMessagesBuffer
        };

        var callbacks = {
            onTabChange: function(tab) {
                if (tab && tab.title) {
                    if (!instance.files[tab.title]) {
                        var lang = 'text';
                        if (typeof ZatoIDEEditorAce !== 'undefined') {
                            lang = ZatoIDEEditorAce.getLanguageFromExtension(tab.title);
                        }
                        instance.files[tab.title] = {
                            content: '',
                            originalContent: '',
                            language: lang,
                            modified: false
                        };
                    }
                    ZatoIDE.switchToFile(instance, tab.title);
                }
                if (instance.onTabChange) {
                    instance.onTabChange(tab);
                }
            },
            onSave: function() {
            },
            onRender: function() {
                instance.tabsManager.activeTabId = tabsInstance.activeTabId;
                instance.tabsManager.tabs = tabsInstance.tabs;
                self.renderTabs(instance);
            },
            createTabData: function(tabNumber) {
                return {
                    title: 'file-' + tabNumber + '.py'
                };
            },
            onBeforeClose: function(tab, doClose) {
                var filename = tab.title;
                var file = instance.files[filename];
                if (file && file.modified) {
                    var contentTrimmed = (file.content || '').trim();
                    if (contentTrimmed === '') {
                        file.content = '';
                        file.modified = false;
                        doClose();
                        return;
                    }
                    ZatoIDE.showSaveDialog(instance, filename, {
                        onDontSave: function() {
                            file.modified = false;
                            doClose();
                        },
                        onCancel: function() {
                        },
                        onSave: function() {
                            file.originalContent = file.content;
                            file.modified = false;
                            doClose();
                        }
                    });
                } else {
                    doClose();
                }
            },
            onAddToClosedHistory: function(tab) {
                var file = instance.files[tab.title];
                var tabData = JSON.parse(JSON.stringify(tab));
                if (file) {
                    tabData.filePath = file.filePath;
                    tabData.language = file.language;
                    tabData.cursorLine = file.cursorLine || 1;
                    tabData.cursorCol = file.cursorCol || 1;
                }
                instance.closedTabsHistory.unshift({
                    tabs: [tabData],
                    closedAt: Date.now()
                });
                tabsInstance.closedTabsHistory = instance.closedTabsHistory;
                self.saveTabsState(instance);
            },
            onFlushClosedHistory: function() {
            },
            onReopenClosedTabs: function() {
                if (instance.closedTabsHistory.length === 0) {
                    return [];
                }
                var entry = instance.closedTabsHistory.shift();
                var closedTabs = entry.tabs || [];
                var reopened = [];
                for (var i = 0; i < closedTabs.length; i++) {
                    var tab = closedTabs[i];
                    tab.id = ZatoTabsEvents.generateTabId();
                    tabsInstance.tabs.push(tab);
                    reopened.push(tab);

                    if (tab.filePath && !instance.files[tab.title]) {
                        instance.files[tab.title] = {
                            content: '',
                            originalContent: '',
                            language: tab.language || 'text',
                            filePath: tab.filePath,
                            modified: false,
                            cursorLine: tab.cursorLine || 1,
                            cursorCol: tab.cursorCol || 1
                        };
                        self.loadFileContent(instance, tab.filePath, tab.title);
                    }
                }
                tabsInstance.closedTabsHistory = instance.closedTabsHistory;
                self.saveTabsState(instance);
                return reopened;
            },
            onClearMessages: function(tabId, messages) {
                instance.clearedMessagesBuffer[tabId] = {
                    messages: JSON.parse(JSON.stringify(messages)),
                    clearedAt: Date.now()
                };
                tabsInstance.clearedMessagesBuffer = instance.clearedMessagesBuffer;
            },
            onUndoClearMessages: function(tabId) {
                var buffer = instance.clearedMessagesBuffer[tabId];
                if (!buffer) {
                    return false;
                }
                var tab = ZatoTabsEvents.getTabById(tabsInstance.tabs, tabId);
                if (tab) {
                    tab.messages = buffer.messages;
                    delete instance.clearedMessagesBuffer[tabId];
                    tabsInstance.clearedMessagesBuffer = instance.clearedMessagesBuffer;
                    return true;
                }
                return false;
            }
        };

        ZatoTabsEvents.bind(container, tabsInstance, callbacks);
    };

})();
