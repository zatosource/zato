(function() {
    'use strict';

    ZatoIDETabs.saveTabsState = function(instance) {
        if (!instance.tabsManager) {
            return;
        }

        var tabs = instance.tabsManager.tabs.map(function(tab) {
            var file = instance.files[tab.title];
            var tabData = {
                id: tab.id,
                title: tab.title,
                filePath: tab.filePath || (file ? file.filePath : null),
                language: tab.language || (file ? file.language : 'text')
            };
            tabData.cursorLine = file ? (file.cursorLine || 1) : 1;
            tabData.cursorCol = file ? (file.cursorCol || 1) : 1;
            tabData.scrollLine = file ? (file.scrollLine !== undefined ? file.scrollLine : null) : null;
            return tabData;
        });

        var state = {
            tabs: tabs,
            activeTabId: instance.tabsManager.activeTabId,
            closedTabsHistory: instance.closedTabsHistory || [],
            timestamp: Date.now()
        };

        try {
            localStorage.setItem(ZatoIDETabs.storageKeys.tabs, JSON.stringify(state));
        } catch (e) {
            console.warn('[ZatoIDE] Failed to save tabs state:', e);
        }
    };

    ZatoIDETabs.loadTabsState = function() {
        try {
            var stored = localStorage.getItem(ZatoIDETabs.storageKeys.tabs);
            if (stored) {
                return JSON.parse(stored);
            }
        } catch (e) {
            console.warn('[ZatoIDE] Failed to load tabs state:', e);
        }
        return null;
    };

    ZatoIDETabs.saveCursorPosition = function(instance, fileName, line, col) {
        if (!instance.files[fileName]) {
            return;
        }
        instance.files[fileName].cursorLine = line;
        instance.files[fileName].cursorCol = col;
        this.saveTabsState(instance);
    };

})();
