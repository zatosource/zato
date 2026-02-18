(function() {
    'use strict';

    var AIChatContextMenu = {
        menu: null,
        core: null,

        show: function(x, y, tabId, core) {
            this.hide();
            this.core = core;

            this.menu = document.createElement('div');
            this.menu.className = 'ai-chat-context-menu';
            this.menu.innerHTML = AIChatRender.buildContextMenuHtml(tabId, core.tabs);

            this.menu.style.left = x + 'px';
            this.menu.style.top = y + 'px';

            var self = this;
            this.menu.addEventListener('click', function(e) {
                var item = e.target.closest('.ai-chat-context-menu-item');
                if (item && !item.classList.contains('disabled')) {
                    var action = item.getAttribute('data-action');
                    var itemTabId = item.getAttribute('data-tab-id');
                    self.handleAction(action, itemTabId);
                    self.hide();
                }
            });

            document.body.appendChild(this.menu);
        },

        hide: function() {
            if (this.menu && this.menu.parentNode) {
                this.menu.parentNode.removeChild(this.menu);
                this.menu = null;
            }
        },

        handleAction: function(action, tabId) {
            var core = this.core;
            if (!core) return;

            var result;
            var tab;

            switch (action) {
                case 'rename':
                    this.renameTab(core.tabs, tabId, function() {
                        core.saveState();
                    }, function() {
                        core.render();
                    });
                    break;

                case 'duplicate':
                    var newTab = AIChatTabs.duplicateTab(core.tabs, tabId);
                    if (newTab) {
                        core.activeTabId = newTab.id;
                        core.saveState();
                        core.render();
                    }
                    break;

                case 'pin':
                    AIChatTabs.togglePin(core.tabs, tabId);
                    core.saveState();
                    core.render();
                    break;

                case 'lock':
                    AIChatTabs.toggleLock(core.tabs, tabId);
                    core.saveState();
                    core.render();
                    break;

                case 'close':
                    tab = AIChatTabs.getTabById(core.tabs, tabId);
                    if (tab) {
                        AIChatTabs.addToClosedHistory(tab);
                    }
                    result = AIChatTabs.closeTab(core.tabs, tabId, core.activeTabId);
                    core.tabs = result.tabs;
                    core.activeTabId = result.activeTabId;
                    core.saveState();
                    core.render();
                    break;

                case 'close-to-right':
                    var toRight = [];
                    var idx = AIChatTabs.getTabIndex(core.tabs, tabId);
                    for (var i = idx + 1; i < core.tabs.length; i++) {
                        if (!core.tabs[i].locked && !core.tabs[i].pinned) {
                            toRight.push(core.tabs[i]);
                        }
                    }
                    for (var j = 0; j < toRight.length; j++) {
                        AIChatTabs.addToClosedHistory(toRight[j]);
                    }
                    result = AIChatTabs.closeToRight(core.tabs, tabId, core.activeTabId);
                    core.tabs = result.tabs;
                    core.activeTabId = result.activeTabId;
                    core.saveState();
                    core.render();
                    break;

                case 'close-others':
                    var others = [];
                    for (var k = 0; k < core.tabs.length; k++) {
                        if (core.tabs[k].id !== tabId && !core.tabs[k].locked && !core.tabs[k].pinned) {
                            others.push(core.tabs[k]);
                        }
                    }
                    for (var l = 0; l < others.length; l++) {
                        AIChatTabs.addToClosedHistory(others[l]);
                    }
                    result = AIChatTabs.closeOthers(core.tabs, tabId, core.activeTabId);
                    core.tabs = result.tabs;
                    core.activeTabId = result.activeTabId;
                    core.saveState();
                    core.render();
                    break;

                case 'close-all':
                    result = AIChatTabs.closeAll(core.tabs, core.activeTabId);
                    core.tabs = result.tabs;
                    core.activeTabId = result.activeTabId;
                    core.saveState();
                    core.render();
                    break;

                case 'reopen':
                    var reopened = AIChatTabs.reopenClosedTab(core.tabs);
                    if (reopened) {
                        core.activeTabId = reopened.id;
                        core.saveState();
                        core.render();
                    }
                    break;

                case 'clear':
                    AIChatTabs.clearMessages(core.tabs, tabId);
                    AIChatTabState.setTokensIn(tabId, 0);
                    AIChatTabState.setTokensOut(tabId, 0);
                    core.saveState();
                    core.render();
                    break;

                case 'undo-clear':
                    if (AIChatTabs.undoClearMessages(core.tabs, tabId)) {
                        tab = AIChatTabs.getTabById(core.tabs, tabId);
                        if (tab) {
                            AIChatTabState.setTokensIn(tabId, tab.tokensIn || 0);
                            AIChatTabState.setTokensOut(tabId, tab.tokensOut || 0);
                        }
                        core.saveState();
                        core.render();
                    }
                    break;

                case 'copy':
                    AIChatTabs.copyToClipboard(core.tabs, tabId);
                    break;

                case 'export-md':
                    tab = AIChatTabs.getTabById(core.tabs, tabId);
                    var md = AIChatTabs.exportAsMarkdown(core.tabs, tabId);
                    if (md && tab) {
                        var mdFilename = (tab.title || 'conversation').replace(/[^a-z0-9]/gi, '-').toLowerCase() + '.md';
                        AIChatTabs.downloadFile(md, mdFilename, 'text/markdown');
                    }
                    break;

                case 'export-json':
                    tab = AIChatTabs.getTabById(core.tabs, tabId);
                    var json = AIChatTabs.exportAsJson(core.tabs, tabId);
                    if (json && tab) {
                        var jsonFilename = (tab.title || 'conversation').replace(/[^a-z0-9]/gi, '-').toLowerCase() + '.json';
                        AIChatTabs.downloadFile(json, jsonFilename, 'application/json');
                    }
                    break;
            }
        },

        renameTab: function(tabs, tabId, saveCallback, renderCallback) {
            var tab = AIChatTabs.getTabById(tabs, tabId);
            if (!tab) return;

            var newTitle = prompt('Enter new tab name:', tab.title);
            if (AIChatTabs.renameTab(tabs, tabId, newTitle)) {
                if (saveCallback) saveCallback();
                if (renderCallback) renderCallback();
            }
        }
    };

    window.AIChatContextMenu = AIChatContextMenu;

})();
