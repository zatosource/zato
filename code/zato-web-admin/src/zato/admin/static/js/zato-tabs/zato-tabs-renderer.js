(function() {
    'use strict';

    var ZatoTabsRenderer = {

        defaultOptions: {
            theme: 'dark',
            showAddButton: true,
            showCloseButton: true,
            showPinIcon: true,
            showLockIcon: true,
            addButtonTitle: 'New tab',
            containerClass: '',
            tabClass: '',
            getIcons: null
        },

        escapeHtml: function(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        getIcon: function(options, name, size) {
            if (options.getIcons && typeof options.getIcons === 'function') {
                return options.getIcons(name, size);
            }
            return this.defaultIcons(name, size);
        },

        defaultIcons: function(name, size) {
            var icons = {
                pin: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M15 12.423L16.577 14v1H12.5v5l-.5.5l-.5-.5v-5H7.423v-1L9 12.423V5H8V4h8v1h-1zM8.85 14h6.3L14 12.85V5h-4v7.85zM12 14"/></svg>',
                lock: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M5 21V9h3V7q0-1.671 1.165-2.835Q10.329 3 12 3t2.836 1.165T16 7v2h3v12zm1-1h12V10H6zm7.066-3.934q.434-.433.434-1.066t-.434-1.066T12 13.5t-1.066.434Q10.5 14.367 10.5 15t.434 1.066q.433.434 1.066.434t1.066-.434M9 9h6V7q0-1.25-.875-2.125T12 4t-2.125.875T9 7zM6 20V10z"/></svg>'
            };
            var svg = icons[name];
            if (!svg) {
                return '';
            }
            if (size) {
                svg = svg.replace(/width="24"/, 'width="' + size + '"');
                svg = svg.replace(/height="24"/, 'height="' + size + '"');
            }
            return svg;
        },

        buildTabsHtml: function(instance, options) {
            var opts = this.mergeOptions(options);
            var tabs = instance.tabs || [];
            var activeTabId = instance.activeTabId;
            var themeClass = 'zato-tabs-theme-' + opts.theme;
            var containerClass = opts.containerClass ? ' ' + opts.containerClass : '';

            var html = '<div class="' + themeClass + containerClass + '" id="' + instance.containerId + '-tabs-wrapper">';
            html += '<div class="zato-tabs-container">';

            for (var i = 0; i < tabs.length; i++) {
                var tab = tabs[i];
                var activeClass = tab.id === activeTabId ? ' active' : '';
                var pinnedClass = tab.pinned ? ' pinned' : '';
                var lockedClass = tab.locked ? ' locked' : '';
                var isDraggable = !tab.pinned && !tab.locked;
                var tabClass = opts.tabClass ? ' ' + opts.tabClass : '';

                html += '<div class="zato-tab' + activeClass + pinnedClass + lockedClass + tabClass + '" data-tab-id="' + tab.id + '" draggable="' + isDraggable + '">';

                if (opts.showPinIcon && tab.pinned) {
                    html += '<span class="zato-tab-pin-icon">' + this.getIcon(opts, 'pin', 14) + '</span>';
                }

                if (opts.showLockIcon && tab.locked) {
                    html += '<span class="zato-tab-lock-icon">' + this.getIcon(opts, 'lock', 12) + '</span>';
                }

                html += '<span class="zato-tab-title">' + this.escapeHtml(tab.title) + '</span>';

                if (opts.showCloseButton && tabs.length > 1 && !tab.locked && !tab.pinned) {
                    html += '<span class="zato-tab-close" data-tab-id="' + tab.id + '">✕</span>';
                }

                html += '</div>';
            }

            if (opts.showAddButton) {
                html += '<button class="zato-tab-add" title="' + this.escapeHtml(opts.addButtonTitle) + '">+</button>';
            }

            html += '</div>';
            html += '</div>';

            return html;
        },

        mergeOptions: function(options) {
            var opts = {};
            var key;
            for (key in this.defaultOptions) {
                if (this.defaultOptions.hasOwnProperty(key)) {
                    opts[key] = this.defaultOptions[key];
                }
            }
            if (options) {
                for (key in options) {
                    if (options.hasOwnProperty(key)) {
                        opts[key] = options[key];
                    }
                }
            }
            return opts;
        },

        render: function(instance, containerElement, options) {
            if (!containerElement) {
                return;
            }
            var html = this.buildTabsHtml(instance, options);
            containerElement.innerHTML = html;
        },

        renderInto: function(instance, containerId, options) {
            var container = document.getElementById(containerId);
            if (!container) {
                console.error('ZatoTabsRenderer: container not found:', containerId);
                return;
            }
            this.render(instance, container, options);
        },

        buildContextMenuHtml: function(instance, tabId, options) {
            var tabs = instance.tabs || [];
            var tab = this.getTabById(tabs, tabId);
            var isLocked = tab && tab.locked;
            var isPinned = tab && tab.pinned;
            var closableToRight = this.countClosableToRight(tabs, tabId);
            var closableOthers = this.countClosableOthers(tabs, tabId);
            var hasMessages = tab && tab.messages && tab.messages.length > 0;
            var closedTabsHistory = instance.closedTabsHistory || [];
            var hasClosedTabs = closedTabsHistory.length > 0;
            var canClose = tabs.length > 1 && !isLocked && !isPinned;

            var html = '';

            html += '<div class="zato-tabs-context-menu-item" data-action="rename" data-tab-id="' + tabId + '">Rename tab</div>';
            html += '<div class="zato-tabs-context-menu-item" data-action="duplicate" data-tab-id="' + tabId + '">Duplicate tab</div>';
            html += '<div class="zato-tabs-context-menu-separator"></div>';

            html += '<div class="zato-tabs-context-menu-item" data-action="pin" data-tab-id="' + tabId + '">' + (isPinned ? 'Unpin tab' : 'Pin tab') + '</div>';
            html += '<div class="zato-tabs-context-menu-item" data-action="lock" data-tab-id="' + tabId + '">' + (isLocked ? 'Unlock tab' : 'Lock tab') + '</div>';
            html += '<div class="zato-tabs-context-menu-separator"></div>';

            if (canClose) {
                html += '<div class="zato-tabs-context-menu-item" data-action="close" data-tab-id="' + tabId + '">Close tab</div>';
            } else {
                html += '<div class="zato-tabs-context-menu-item disabled">Close tab</div>';
            }

            if (closableToRight > 0) {
                html += '<div class="zato-tabs-context-menu-item" data-action="close-to-right" data-tab-id="' + tabId + '">Close tabs to the right</div>';
            } else {
                html += '<div class="zato-tabs-context-menu-item disabled">Close tabs to the right</div>';
            }

            if (closableOthers > 0) {
                html += '<div class="zato-tabs-context-menu-item" data-action="close-others" data-tab-id="' + tabId + '">Close other tabs</div>';
            } else {
                html += '<div class="zato-tabs-context-menu-item disabled">Close other tabs</div>';
            }

            html += '<div class="zato-tabs-context-menu-item" data-action="close-all" data-tab-id="' + tabId + '">Close all tabs</div>';

            html += '<div class="zato-tabs-context-menu-separator"></div>';

            if (hasClosedTabs) {
                html += '<div class="zato-tabs-context-menu-item" data-action="reopen" data-tab-id="' + tabId + '">Reopen closed tab</div>';
            } else {
                html += '<div class="zato-tabs-context-menu-item disabled">Reopen closed tab</div>';
            }

            var clearedMessagesBuffer = instance.clearedMessagesBuffer || {};
            var canUndoClear = !!clearedMessagesBuffer[tabId];

            if (hasMessages) {
                html += '<div class="zato-tabs-context-menu-item" data-action="clear" data-tab-id="' + tabId + '">Clear all messages</div>';
            } else if (canUndoClear) {
                html += '<div class="zato-tabs-context-menu-item" data-action="undo-clear" data-tab-id="' + tabId + '">Undo clear messages</div>';
            } else {
                html += '<div class="zato-tabs-context-menu-item disabled">Clear all messages</div>';
            }

            html += '<div class="zato-tabs-context-menu-separator"></div>';

            if (hasMessages) {
                html += '<div class="zato-tabs-context-menu-item" data-action="copy" data-tab-id="' + tabId + '">Copy to clipboard</div>';
                html += '<div class="zato-tabs-context-menu-item" data-action="export-md" data-tab-id="' + tabId + '">Export as markdown</div>';
                html += '<div class="zato-tabs-context-menu-item" data-action="export-json" data-tab-id="' + tabId + '">Export as JSON</div>';
            } else {
                html += '<div class="zato-tabs-context-menu-item disabled">Copy to clipboard</div>';
                html += '<div class="zato-tabs-context-menu-item disabled">Export as markdown</div>';
                html += '<div class="zato-tabs-context-menu-item disabled">Export as JSON</div>';
            }

            return html;
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

        countClosableToRight: function(tabs, tabId) {
            var tabIndex = this.getTabIndex(tabs, tabId);
            if (tabIndex === -1) {
                return 0;
            }
            var count = 0;
            for (var i = tabIndex + 1; i < tabs.length; i++) {
                if (!tabs[i].locked && !tabs[i].pinned) {
                    count++;
                }
            }
            return count;
        },

        countClosableOthers: function(tabs, tabId) {
            var count = 0;
            for (var i = 0; i < tabs.length; i++) {
                if (tabs[i].id !== tabId && !tabs[i].locked && !tabs[i].pinned) {
                    count++;
                }
            }
            return count;
        }
    };

    window.ZatoTabsRenderer = ZatoTabsRenderer;

})();
