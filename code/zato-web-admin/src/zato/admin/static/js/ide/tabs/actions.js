(function() {
    'use strict';

    ZatoIDETabs.switchToTab = function(instance, tabId) {
        if (!instance.tabsManager) {
            return;
        }

        instance.tabsManager.activeTabId = tabId;
        this.renderTabs(instance);
        this.bindTabEvents(instance);

        var tab = null;
        for (var i = 0; i < instance.tabsManager.tabs.length; i++) {
            if (instance.tabsManager.tabs[i].id === tabId) {
                tab = instance.tabsManager.tabs[i];
                break;
            }
        }

        if (tab && tab.title) {
            ZatoIDE.switchToFile(instance, tab.title);
        }
    };

    ZatoIDETabs.closeTab = function(instance, tab) {
        if (!instance.tabsManager || !instance.tabsManager.tabs) {
            return;
        }

        var tabId = tab.id;
        var filename = tab.title;
        var file = instance.files ? instance.files[filename] : null;
        var self = this;

        var doClose = function() {
            var tabs = instance.tabsManager.tabs;
            var tabIndex = -1;
            for (var i = 0; i < tabs.length; i++) {
                if (tabs[i].id === tabId) {
                    tabIndex = i;
                    break;
                }
            }

            if (tabIndex === -1) {
                return;
            }

            tabs.splice(tabIndex, 1);

            if (instance.tabsManager.activeTabId === tabId) {
                var newIndex = tabIndex > 0 ? tabIndex - 1 : 0;
                if (tabs.length > 0) {
                    instance.tabsManager.activeTabId = tabs[newIndex].id;
                    ZatoIDE.switchToFile(instance, tabs[newIndex].title);
                }
            }

            self.renderTabs(instance);
            self.bindTabEvents(instance);
        };

        if (file && file.modified) {
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
    };

    ZatoIDETabs.updateTabModifiedState = function(instance, filename, modified) {
        if (!instance.tabsManager) {
            return;
        }
        var tabs = instance.tabsManager.tabs;
        for (var i = 0; i < tabs.length; i++) {
            if (tabs[i].title === filename) {
                tabs[i].modified = modified;
                this.renderTabs(instance);
                break;
            }
        }
    };

    ZatoIDETabs.syncTabToFile = function(instance, filename) {
        if (!instance.tabsManager) {
            return;
        }

        var tabs = instance.tabsManager.tabs;
        for (var i = 0; i < tabs.length; i++) {
            if (tabs[i].title === filename) {
                instance.tabsManager.activeTabId = tabs[i].id;
                this.renderTabs(instance);
                break;
            }
        }
    };

    ZatoIDETabs.findTabByPath = function(instance, filePath) {
        if (!instance.tabsManager || !instance.tabsManager.tabs) {
            return null;
        }
        for (var i = 0; i < instance.tabsManager.tabs.length; i++) {
            var tab = instance.tabsManager.tabs[i];
            if (tab.filePath === filePath) {
                return tab;
            }
        }
        return null;
    };

})();
