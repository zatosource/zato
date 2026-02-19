(function() {
    'use strict';

    var AIChatTabActions = {

        addTab: function(widget, core) {
            console.log('[AI-CHAT-TAB-ACTIONS] addTab called');
            console.log('[AI-CHAT-TAB-ACTIONS] before: tabs.length=' + core.tabs.length);
            var currentTab = AIChatTabs.getTabById(core.tabs, core.activeTabId);
            var currentModel = currentTab ? currentTab.model : null;

            var newTab = AIChatTabs.addTab(core.tabs);
            AIChatTabState.initTab(newTab.id);

            if (currentModel) {
                newTab.model = currentModel;
                AIChatTabState.setModel(newTab.id, currentModel);
            }

            core.activeTabId = newTab.id;
            console.log('[AI-CHAT-TAB-ACTIONS] after: tabs.length=' + core.tabs.length + ', newTabId=' + newTab.id);
            core.saveState();
            core.render();
            var panelsAfterAdd = widget.querySelectorAll('.ai-chat-tab-panel');
            console.log('[AI-CHAT-TAB-ACTIONS] panels after addTab render: ' + panelsAfterAdd.length);
            var inputsAfterAdd = widget.querySelectorAll('.ai-chat-input');
            console.log('[AI-CHAT-TAB-ACTIONS] inputs after addTab render: ' + inputsAfterAdd.length);
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
            console.log('[AI-CHAT-TAB-ACTIONS] switchTab called, from=' + core.activeTabId + ' to=' + tabId);
            if (core.activeTabId === tabId) {
                console.log('[AI-CHAT-TAB-ACTIONS] switchTab: same tab, returning');
                return;
            }
            var panelsBefore = widget.querySelectorAll('.ai-chat-tab-panel');
            console.log('[AI-CHAT-TAB-ACTIONS] panels before switchTab: ' + panelsBefore.length);
            core.activeTabId = tabId;
            core.saveState();
            core.render();
            var panelsAfter = widget.querySelectorAll('.ai-chat-tab-panel');
            console.log('[AI-CHAT-TAB-ACTIONS] panels after switchTab render: ' + panelsAfter.length);
            var inputsAfter = widget.querySelectorAll('.ai-chat-input');
            console.log('[AI-CHAT-TAB-ACTIONS] inputs after switchTab render: ' + inputsAfter.length);
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
