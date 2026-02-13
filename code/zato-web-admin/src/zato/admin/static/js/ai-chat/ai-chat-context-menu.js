(function() {
    'use strict';

    var AIChatContextMenu = {
        menu: null,

        show: function(x, y, tabId, renameCallback) {
            this.hide();

            this.menu = document.createElement('div');
            this.menu.className = 'ai-chat-context-menu';
            this.menu.innerHTML = AIChatRender.buildContextMenuHtml(tabId);

            this.menu.style.left = x + 'px';
            this.menu.style.top = y + 'px';

            var self = this;
            this.menu.addEventListener('click', function(e) {
                var item = e.target.closest('.ai-chat-context-menu-item');
                if (item) {
                    var action = item.getAttribute('data-action');
                    var itemTabId = item.getAttribute('data-tab-id');

                    if (action === 'rename' && renameCallback) {
                        renameCallback(itemTabId);
                    }

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
