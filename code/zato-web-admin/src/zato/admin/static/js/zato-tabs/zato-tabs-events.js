(function() {
    'use strict';

    var ZatoTabsEvents = {

        contextMenu: null,
        currentInstance: null,
        boundHandlers: new WeakMap(),

        isTabDragging: false,
        draggedTabId: null,
        draggedTabElement: null,
        dragClone: null,
        tabDragOffsetX: 0,
        tabDragOffsetY: 0,
        tabDragStartX: 0,
        tabDragStartY: 0,
        tabDragThreshold: 5,
        tabDragActivated: false,
        pendingDropIndex: null,

        bind: function(containerElement, instance, callbacks) {
            var self = this;
            callbacks = callbacks || {};

            this.unbind(containerElement);

            var clickHandler = function(e) {
                self.handleClick(e, containerElement, instance, callbacks);
            };
            var contextMenuHandler = function(e) {
                self.handleContextMenu(e, containerElement, instance, callbacks);
            };
            var mouseDownHandler = function(e) {
                self.handleMouseDown(e, containerElement, instance, callbacks);
            };
            var mouseMoveHandler = function(e) {
                self.handleMouseMove(e, containerElement, instance, callbacks);
            };
            var mouseUpHandler = function(e) {
                self.handleMouseUp(e, containerElement, instance, callbacks);
            };
            var docClickHandler = function(e) {
                if (self.contextMenu && !self.contextMenu.contains(e.target)) {
                    self.hideContextMenu();
                }
            };

            containerElement.addEventListener('click', clickHandler);
            containerElement.addEventListener('contextmenu', contextMenuHandler);
            containerElement.addEventListener('mousedown', mouseDownHandler);
            document.addEventListener('mousemove', mouseMoveHandler);
            document.addEventListener('mouseup', mouseUpHandler);
            document.addEventListener('click', docClickHandler);

            this.boundHandlers.set(containerElement, {
                click: clickHandler,
                contextmenu: contextMenuHandler,
                mousedown: mouseDownHandler,
                mousemove: mouseMoveHandler,
                mouseup: mouseUpHandler,
                docClick: docClickHandler
            });
        },

        unbind: function(containerElement) {
            var handlers = this.boundHandlers.get(containerElement);
            if (!handlers) {
                return;
            }
            containerElement.removeEventListener('click', handlers.click);
            containerElement.removeEventListener('contextmenu', handlers.contextmenu);
            containerElement.removeEventListener('mousedown', handlers.mousedown);
            document.removeEventListener('mousemove', handlers.mousemove);
            document.removeEventListener('mouseup', handlers.mouseup);
            document.removeEventListener('click', handlers.docClick);
            this.boundHandlers.delete(containerElement);
        },

        handleClick: function(e, containerElement, instance, callbacks) {
            var target = e.target;

            var closeWrapper = target.closest('.zato-tab-close-wrapper');
            if (closeWrapper && containerElement.contains(closeWrapper)) {
                var tabId = closeWrapper.getAttribute('data-tab-id');
                this.closeTab(instance, tabId, callbacks);
                return;
            }
            var closeButton = target.closest('.zato-tab-close');
            if (closeButton && containerElement.contains(closeButton)) {
                var tabId = closeButton.getAttribute('data-tab-id');
                if (tabId) {
                    this.closeTab(instance, tabId, callbacks);
                    return;
                }
            }

            var addButton = target.closest('.zato-tab-add');
            if (addButton && containerElement.contains(addButton)) {
                this.addTab(instance, callbacks);
                return;
            }

            var tabElement = target.closest('.zato-tab');
            if (tabElement && containerElement.contains(tabElement)) {
                var tabId = tabElement.getAttribute('data-tab-id');
                this.switchTab(instance, tabId, callbacks);
                return;
            }
        },

        handleContextMenu: function(e, containerElement, instance, callbacks) {
            var tabElement = e.target.closest('.zato-tab');
            if (tabElement && containerElement.contains(tabElement)) {
                e.preventDefault();
                var tabId = tabElement.getAttribute('data-tab-id');
                this.showContextMenu(e.clientX, e.clientY, tabId, instance, callbacks);
            }
        },

        handleMouseDown: function(e, containerElement, instance, callbacks) {
            var tabElement = e.target.closest('.zato-tab');
            if (tabElement && containerElement.contains(tabElement) && !e.target.closest('.zato-tab-close')) {
                if (tabElement.classList.contains('pinned') || tabElement.classList.contains('locked')) {
                    return;
                }
                this.isTabDragging = true;
                this.tabDragActivated = false;
                this.draggedTabId = tabElement.getAttribute('data-tab-id');
                this.draggedTabElement = tabElement;
                this.tabDragStartX = e.clientX;
                this.tabDragStartY = e.clientY;
                this.currentInstance = instance;

                var tabRect = tabElement.getBoundingClientRect();
                this.tabDragOffsetX = e.clientX - tabRect.left;
                this.tabDragOffsetY = e.clientY - tabRect.top;

                e.preventDefault();
            }
        },

        handleMouseMove: function(e, containerElement, instance, callbacks) {
            if (!this.isTabDragging) {
                return;
            }

            if (!this.tabDragActivated) {
                var dx = e.clientX - this.tabDragStartX;
                var dy = e.clientY - this.tabDragStartY;
                var distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < this.tabDragThreshold) {
                    return;
                }
                this.tabDragActivated = true;
                var tabRect = this.draggedTabElement.getBoundingClientRect();
                var clone = this.draggedTabElement.cloneNode(true);
                clone.classList.add('dragging');
                clone.classList.add('zato-tabs-theme-' + (instance.theme || 'dark'));
                clone.style.width = tabRect.width + 'px';
                clone.style.left = tabRect.left + 'px';
                clone.style.top = tabRect.top + 'px';
                clone.id = 'zato-tab-drag-clone';
                document.body.appendChild(clone);
                this.dragClone = clone;
                this.draggedTabElement.style.opacity = '0.3';
            }

            if (!this.dragClone) {
                return;
            }

            var newLeft = e.clientX - this.tabDragOffsetX;
            var newTop = e.clientY - this.tabDragOffsetY;
            this.dragClone.style.left = newLeft + 'px';
            this.dragClone.style.top = newTop + 'px';

            this.pendingDropIndex = null;
            var tabsContainer = containerElement.querySelector('.zato-tabs-container');
            if (!tabsContainer) {
                return;
            }
            var tabs = tabsContainer.querySelectorAll('.zato-tab');

            for (var i = 0; i < tabs.length; i++) {
                var tab = tabs[i];
                if (tab === this.draggedTabElement) {
                    continue;
                }
                var rect = tab.getBoundingClientRect();
                var midX = rect.left + rect.width / 2;

                if (e.clientX > rect.left && e.clientX < rect.right) {
                    if (e.clientX < midX) {
                        this.pendingDropIndex = Array.from(tabsContainer.children).indexOf(tab);
                    } else {
                        this.pendingDropIndex = Array.from(tabsContainer.children).indexOf(tab) + 1;
                    }
                    break;
                }
            }
        },

        handleMouseUp: function(e, containerElement, instance, callbacks) {
            if (!this.isTabDragging) {
                return;
            }

            this.isTabDragging = false;

            if (this.tabDragActivated) {
                if (this.dragClone && this.dragClone.parentNode) {
                    this.dragClone.parentNode.removeChild(this.dragClone);
                    this.dragClone = null;
                }

                if (this.draggedTabElement) {
                    this.draggedTabElement.style.opacity = '';
                }

                if (this.pendingDropIndex !== null && this.pendingDropIndex !== undefined) {
                    var tabs = instance.tabs;
                    var draggedTabIndex = this.getTabIndex(tabs, this.draggedTabId);
                    if (draggedTabIndex !== -1 && draggedTabIndex !== this.pendingDropIndex) {
                        var draggedTab = tabs[draggedTabIndex];

                        var pinnedCount = 0;
                        for (var i = 0; i < tabs.length; i++) {
                            if (tabs[i].pinned) {
                                pinnedCount++;
                            } else {
                                break;
                            }
                        }

                        var insertAt = this.pendingDropIndex;
                        if (insertAt > draggedTabIndex) {
                            insertAt = insertAt - 1;
                        }

                        if (!draggedTab.pinned && insertAt < pinnedCount) {
                            insertAt = pinnedCount;
                        }

                        if (draggedTabIndex !== insertAt) {
                            var tab = tabs.splice(draggedTabIndex, 1)[0];
                            tabs.splice(insertAt, 0, tab);
                            if (callbacks.onReorder) {
                                callbacks.onReorder(tabs);
                            }
                            if (callbacks.onSave) {
                                callbacks.onSave();
                            }
                            if (callbacks.onRender) {
                                callbacks.onRender();
                            }
                        }
                    }
                }
            }

            this.draggedTabId = null;
            this.draggedTabElement = null;
            this.tabDragActivated = false;
            this.currentInstance = null;
        },

        switchTab: function(instance, tabId, callbacks) {
            instance.activeTabId = tabId;
            if (callbacks.onTabChange) {
                var tab = this.getTabById(instance.tabs, tabId);
                callbacks.onTabChange(tab);
            }
            if (callbacks.onSave) {
                callbacks.onSave();
            }
            if (callbacks.onRender) {
                callbacks.onRender();
            }
        },

        closeTab: function(instance, tabId, callbacks) {
            if (instance.tabs.length <= 1 && !instance.allowCloseLastTab) {
                return;
            }

            var tab = this.getTabById(instance.tabs, tabId);
            if (tab && (tab.locked || tab.pinned)) {
                return;
            }

            var self = this;
            var doClose = function() {
                if (tab && callbacks.onAddToClosedHistory) {
                    callbacks.onAddToClosedHistory(tab);
                }

                var tabIndex = self.getTabIndex(instance.tabs, tabId);
                if (tabIndex === -1) {
                    return;
                }

                instance.tabs.splice(tabIndex, 1);

                if (instance.activeTabId === tabId) {
                    var newActiveIndex = Math.min(tabIndex, instance.tabs.length - 1);
                    instance.activeTabId = instance.tabs[newActiveIndex].id;
                    if (callbacks.onTabChange) {
                        var newActiveTab = self.getTabById(instance.tabs, instance.activeTabId);
                        callbacks.onTabChange(newActiveTab);
                    }
                }

                if (callbacks.onFlushClosedHistory) {
                    callbacks.onFlushClosedHistory();
                }
                if (callbacks.onSave) {
                    callbacks.onSave();
                }
                if (callbacks.onRender) {
                    callbacks.onRender();
                }
            };

            if (callbacks.onBeforeClose) {
                callbacks.onBeforeClose(tab, doClose);
            } else {
                doClose();
            }
        },

        addTab: function(instance, callbacks) {
            var tabNumber = instance.tabs.length + 1;
            var newTab = {
                id: this.generateTabId(),
                title: 'Tab ' + tabNumber,
                messages: []
            };
            if (callbacks.createTabData) {
                var customData = callbacks.createTabData(tabNumber);
                for (var key in customData) {
                    if (customData.hasOwnProperty(key)) {
                        newTab[key] = customData[key];
                    }
                }
            }
            instance.tabs.push(newTab);
            instance.activeTabId = newTab.id;

            if (callbacks.onTabChange) {
                callbacks.onTabChange(newTab);
            }
            if (callbacks.onTabAdd) {
                callbacks.onTabAdd(newTab);
            }
            if (callbacks.onSave) {
                callbacks.onSave();
            }
            if (callbacks.onRender) {
                callbacks.onRender();
            }
        },

        showContextMenu: function(x, y, tabId, instance, callbacks) {
            this.hideContextMenu();
            this.currentInstance = instance;

            this.contextMenu = document.createElement('div');
            this.contextMenu.className = 'zato-tabs-context-menu';
            this.contextMenu.innerHTML = ZatoTabsRenderer.buildContextMenuHtml(instance, tabId, {});

            this.contextMenu.style.left = x + 'px';
            this.contextMenu.style.top = y + 'px';

            var self = this;
            this.contextMenu.addEventListener('click', function(e) {
                var item = e.target.closest('.zato-tabs-context-menu-item');
                if (item && !item.classList.contains('disabled')) {
                    var action = item.getAttribute('data-action');
                    var itemTabId = item.getAttribute('data-tab-id');
                    self.handleContextMenuAction(action, itemTabId, instance, callbacks);
                    self.hideContextMenu();
                }
            });

            document.body.appendChild(this.contextMenu);
        },

        hideContextMenu: function() {
            if (this.contextMenu && this.contextMenu.parentNode) {
                this.contextMenu.parentNode.removeChild(this.contextMenu);
                this.contextMenu = null;
            }
        },

        handleContextMenuAction: function(action, tabId, instance, callbacks) {
            var tab;

            switch (action) {
                case 'rename':
                    tab = this.getTabById(instance.tabs, tabId);
                    if (tab) {
                        var newTitle = prompt('Enter new tab name:', tab.title);
                        if (newTitle && newTitle.trim()) {
                            tab.title = newTitle.trim();
                            if (callbacks.onSave) {
                                callbacks.onSave();
                            }
                            if (callbacks.onRender) {
                                callbacks.onRender();
                            }
                        }
                    }
                    break;

                case 'duplicate':
                    tab = this.getTabById(instance.tabs, tabId);
                    if (tab) {
                        var newTab = {
                            id: this.generateTabId(),
                            title: this.generateDuplicateTitle(instance.tabs, tab.title),
                            messages: JSON.parse(JSON.stringify(tab.messages || []))
                        };
                        var tabIndex = this.getTabIndex(instance.tabs, tabId);
                        instance.tabs.splice(tabIndex + 1, 0, newTab);
                        instance.activeTabId = newTab.id;
                        if (callbacks.onSave) {
                            callbacks.onSave();
                        }
                        if (callbacks.onRender) {
                            callbacks.onRender();
                        }
                    }
                    break;

                case 'pin':
                    tab = this.getTabById(instance.tabs, tabId);
                    if (tab) {
                        tab.pinned = !tab.pinned;
                        if (tab.pinned) {
                            var tabIndex = this.getTabIndex(instance.tabs, tabId);
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
                        if (callbacks.onSave) {
                            callbacks.onSave();
                        }
                        if (callbacks.onRender) {
                            callbacks.onRender();
                        }
                    }
                    break;

                case 'lock':
                    tab = this.getTabById(instance.tabs, tabId);
                    if (tab) {
                        tab.locked = !tab.locked;
                        if (callbacks.onSave) {
                            callbacks.onSave();
                        }
                        if (callbacks.onRender) {
                            callbacks.onRender();
                        }
                    }
                    break;

                case 'close':
                    this.closeTab(instance, tabId, callbacks);
                    break;

                case 'close-to-right':
                    this.closeTabsToRight(instance, tabId, callbacks);
                    break;

                case 'close-others':
                    this.closeOtherTabs(instance, tabId, callbacks);
                    break;

                case 'close-all':
                    this.closeAllTabs(instance, callbacks);
                    break;

                case 'reopen':
                    if (callbacks.onReopenClosedTabs) {
                        var reopened = callbacks.onReopenClosedTabs();
                        if (reopened && reopened.length > 0) {
                            instance.activeTabId = reopened[reopened.length - 1].id;
                            if (callbacks.onSave) {
                                callbacks.onSave();
                            }
                            if (callbacks.onRender) {
                                callbacks.onRender();
                            }
                        }
                    }
                    break;

                case 'clear':
                    tab = this.getTabById(instance.tabs, tabId);
                    if (tab && tab.messages && tab.messages.length > 0) {
                        if (callbacks.onClearMessages) {
                            callbacks.onClearMessages(tabId, tab.messages);
                        }
                        tab.messages = [];
                        if (callbacks.onSave) {
                            callbacks.onSave();
                        }
                        if (callbacks.onRender) {
                            callbacks.onRender();
                        }
                    }
                    break;

                case 'undo-clear':
                    if (callbacks.onUndoClearMessages) {
                        if (callbacks.onUndoClearMessages(tabId)) {
                            if (callbacks.onSave) {
                                callbacks.onSave();
                            }
                            if (callbacks.onRender) {
                                callbacks.onRender();
                            }
                        }
                    }
                    break;

                case 'copy':
                    tab = this.getTabById(instance.tabs, tabId);
                    if (tab && tab.messages && tab.messages.length > 0) {
                        var text = '';
                        for (var i = 0; i < tab.messages.length; i++) {
                            var msg = tab.messages[i];
                            var role = msg.role.charAt(0).toUpperCase() + msg.role.slice(1);
                            text += role + ':\n' + msg.content + '\n\n';
                        }
                        navigator.clipboard.writeText(text.trim());
                    }
                    break;

                case 'export-md':
                    tab = this.getTabById(instance.tabs, tabId);
                    if (tab) {
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
                        var filename = (tab.title || 'tab').replace(/[^a-z0-9]/gi, '-').toLowerCase() + '.md';
                        this.downloadFile(md, filename, 'text/markdown');
                    }
                    break;

                case 'export-json':
                    tab = this.getTabById(instance.tabs, tabId);
                    if (tab) {
                        var data = {
                            title: tab.title,
                            messages: tab.messages || [],
                            exportedAt: new Date().toISOString()
                        };
                        var json = JSON.stringify(data, null, 2);
                        var filename = (tab.title || 'tab').replace(/[^a-z0-9]/gi, '-').toLowerCase() + '.json';
                        this.downloadFile(json, filename, 'application/json');
                    }
                    break;
            }
        },

        closeTabsToRight: function(instance, tabId, callbacks) {
            var tabIndex = this.getTabIndex(instance.tabs, tabId);
            if (tabIndex === -1) {
                return;
            }

            var toClose = [];
            for (var i = tabIndex + 1; i < instance.tabs.length; i++) {
                if (!instance.tabs[i].locked && !instance.tabs[i].pinned) {
                    toClose.push(instance.tabs[i]);
                }
            }

            for (var j = 0; j < toClose.length; j++) {
                if (callbacks.onAddToClosedHistory) {
                    callbacks.onAddToClosedHistory(toClose[j]);
                }
            }

            instance.tabs = instance.tabs.filter(function(tab, idx) {
                if (idx <= tabIndex) {
                    return true;
                }
                return tab.locked || tab.pinned;
            });

            if (!this.getTabById(instance.tabs, instance.activeTabId)) {
                instance.activeTabId = tabId;
            }

            if (callbacks.onFlushClosedHistory) {
                callbacks.onFlushClosedHistory();
            }
            if (callbacks.onSave) {
                callbacks.onSave();
            }
            if (callbacks.onRender) {
                callbacks.onRender();
            }
        },

        closeOtherTabs: function(instance, tabId, callbacks) {
            var toClose = [];
            for (var i = 0; i < instance.tabs.length; i++) {
                if (instance.tabs[i].id !== tabId && !instance.tabs[i].locked && !instance.tabs[i].pinned) {
                    toClose.push(instance.tabs[i]);
                }
            }

            for (var j = 0; j < toClose.length; j++) {
                if (callbacks.onAddToClosedHistory) {
                    callbacks.onAddToClosedHistory(toClose[j]);
                }
            }

            instance.tabs = instance.tabs.filter(function(tab) {
                return tab.id === tabId || tab.locked || tab.pinned;
            });

            instance.activeTabId = tabId;

            if (callbacks.onFlushClosedHistory) {
                callbacks.onFlushClosedHistory();
            }
            if (callbacks.onSave) {
                callbacks.onSave();
            }
            if (callbacks.onRender) {
                callbacks.onRender();
            }
        },

        closeAllTabs: function(instance, callbacks) {
            var toClose = [];
            for (var i = 0; i < instance.tabs.length; i++) {
                if (!instance.tabs[i].locked && !instance.tabs[i].pinned) {
                    toClose.push(instance.tabs[i]);
                }
            }

            for (var j = 0; j < toClose.length; j++) {
                if (callbacks.onAddToClosedHistory) {
                    callbacks.onAddToClosedHistory(toClose[j]);
                }
            }

            instance.tabs = instance.tabs.filter(function(tab) {
                return tab.locked || tab.pinned;
            });

            if (instance.tabs.length === 0) {
                var newTab = {
                    id: this.generateTabId(),
                    title: 'Tab 1',
                    messages: []
                };
                if (callbacks.createTabData) {
                    var customData = callbacks.createTabData(1);
                    for (var key in customData) {
                        if (customData.hasOwnProperty(key)) {
                            newTab[key] = customData[key];
                        }
                    }
                }
                instance.tabs.push(newTab);
            }

            instance.activeTabId = instance.tabs[0].id;

            if (callbacks.onFlushClosedHistory) {
                callbacks.onFlushClosedHistory();
            }
            if (callbacks.onSave) {
                callbacks.onSave();
            }
            if (callbacks.onRender) {
                callbacks.onRender();
            }
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

        generateTabId: function() {
            return 'tab-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
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

    window.ZatoTabsEvents = ZatoTabsEvents;

})();
