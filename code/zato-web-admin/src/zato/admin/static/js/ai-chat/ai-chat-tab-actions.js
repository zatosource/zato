(function() {
    'use strict';

    var AIChatTabActions = {

        addTab: function(widget, core) {
            var currentTab = AIChatTabs.getTabById(core.tabs, core.activeTabId);
            var currentModel = currentTab ? currentTab.model : null;

            var newTab = AIChatTabs.addTab(core.tabs);
            AIChatTabState.initTab(newTab.id);

            if (currentModel) {
                newTab.model = currentModel;
                AIChatTabState.setModel(newTab.id, currentModel);
            }

            core.activeTabId = newTab.id;
            core.saveState();
            core.render();
            this.focusInput(widget, newTab.id);
        },

        closeTab: function(widget, core, tabId) {
            var tab = AIChatTabs.getTabById(core.tabs, tabId);
            if (tab) {
                AIChatTabs.addToClosedHistory(tab);
                AIChatTabs.flushClosedHistory();
            }
            AIChatTabState.removeTab(tabId);
            var result = AIChatTabs.closeTab(core.tabs, tabId, core.activeTabId);
            core.tabs = result.tabs;
            core.activeTabId = result.activeTabId;
            core.saveState();
            core.render();
            this.focusInput(widget, core.activeTabId);
        },

        switchTab: function(widget, core, tabId) {
            if (core.activeTabId === tabId) return;
            core.activeTabId = tabId;
            core.saveState();
            core.render();
            AIChatAttachments.render(widget, tabId, core.tabs);
            this.focusInput(widget, tabId);
        },

        focusInput: function(widget, tabId) {
            var input = widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
            if (input) {
                input.focus();
            }
        }
    };

    window.AIChatTabActions = AIChatTabActions;

})();
