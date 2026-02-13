(function() {
    'use strict';

    var LLMChat = {
        widget: null,
        tabs: [],
        activeTabId: null,
        isMinimized: false,
        isDragging: false,
        isResizing: false,
        resizeDirection: null,
        dragOffsetX: 0,
        dragOffsetY: 0,
        resizeState: null,
        isTabDragging: false,
        draggedTabId: null,
        draggedTabElement: null,
        dragClone: null,
        tabDragOffsetX: 0,
        tabDragOffsetY: 0,
        tabOriginalWidth: 0,
        tabOriginalIndex: 0,
        pendingDropIndex: null,
        contextMenu: null,
        preMinimizePosition: null,
        zoomScale: 1.0,

        init: function() {
            console.debug('LLMChat.init: starting initialization');

            this.loadState();
            this.createWidget();
            this.bindEvents();
            this.render();

            console.debug('LLMChat.init: initialization complete');
        },

        loadState: function() {
            console.debug('LLMChat.loadState: loading state from localStorage');

            this.tabs = LLMChatState.loadTabs();
            if (!this.tabs || this.tabs.length === 0) {
                console.debug('LLMChat.loadState: no tabs found, creating default tab');
                this.tabs = [LLMChatTabs.createDefaultTab()];
            }

            this.activeTabId = LLMChatState.loadActiveTabId();
            if (!this.activeTabId || !LLMChatTabs.getTabById(this.tabs, this.activeTabId)) {
                this.activeTabId = this.tabs[0].id;
            }

            this.isMinimized = LLMChatState.loadMinimized();
            this.preMinimizePosition = LLMChatState.loadPreMinimizePosition();
            this.zoomScale = LLMChatState.loadZoom();
        },

        saveState: function() {
            console.debug('LLMChat.saveState: saving state to localStorage');
            LLMChatState.saveTabs(this.tabs);
            LLMChatState.saveActiveTabId(this.activeTabId);
            LLMChatState.saveMinimized(this.isMinimized);
        },

        savePosition: function() {
            if (!this.widget) return;
            var rect = this.widget.getBoundingClientRect();
            LLMChatState.savePosition({ left: rect.left, top: rect.top });
        },

        saveDimensions: function() {
            if (!this.widget) return;
            LLMChatState.saveDimensions({
                width: this.widget.offsetWidth,
                height: this.widget.offsetHeight
            });
        },

        createWidget: function() {
            console.debug('LLMChat.createWidget: creating widget element');

            this.widget = document.createElement('div');
            this.widget.className = 'llm-chat-widget';
            this.widget.id = 'llm-chat-widget';

            if (this.isMinimized) {
                this.widget.classList.add('minimized');
                this.widget.style.right = '20px';
                this.widget.style.bottom = '20px';
                this.widget.style.left = 'auto';
                this.widget.style.top = 'auto';
                this.widget.style.width = '200px';
                this.widget.style.height = 'auto';
            } else {
                var position = LLMChatState.loadPosition();
                if (position) {
                    this.widget.style.left = position.left + 'px';
                    this.widget.style.top = position.top + 'px';
                    this.widget.style.right = 'auto';
                    this.widget.style.bottom = 'auto';
                }

                var dimensions = LLMChatState.loadDimensions();
                if (dimensions) {
                    this.widget.style.width = dimensions.width + 'px';
                    this.widget.style.height = dimensions.height + 'px';
                }

                if (this.zoomScale !== 1.0) {
                    LLMChatZoom.applyZoom(this.widget, this.zoomScale);
                }
            }

            document.body.appendChild(this.widget);
            console.debug('LLMChat.createWidget: widget appended to body');
        },

        render: function() {
            console.debug('LLMChat.render: rendering widget');

            var html = LLMChatRender.buildHeaderHtml(this.isMinimized);
            html += LLMChatRender.buildTabsHtml(this.tabs, this.activeTabId);
            html += LLMChatRender.buildBodyHtml(this.tabs, this.activeTabId);
            html += LLMChatRender.buildResizeHandlesHtml();

            this.widget.innerHTML = html;
            console.debug('LLMChat.render: widget html set');
        },

        bindEvents: function() {
            console.debug('LLMChat.bindEvents: binding events');

            var self = this;

            this.widget.addEventListener('click', function(e) {
                self.handleClick(e);
            });

            this.widget.addEventListener('mousedown', function(e) {
                self.handleMouseDown(e);
            });

            document.addEventListener('mousemove', function(e) {
                self.handleMouseMove(e);
            });

            document.addEventListener('mouseup', function(e) {
                self.handleMouseUp(e);
            });

            document.addEventListener('keydown', function(e) {
                self.handleKeyDown(e);
            });

            document.addEventListener('input', function(e) {
                LLMChatInput.handleInput(e);
            });

            document.addEventListener('keyup', function(e) {
                LLMChatInput.handleKeyUp(e);
            });

            this.widget.addEventListener('contextmenu', function(e) {
                self.handleContextMenu(e);
            });

            this.widget.addEventListener('wheel', function(e) {
                self.handleWheel(e);
            }, { passive: false });

            document.addEventListener('click', function(e) {
                self.hideContextMenu();
            });

            console.debug('LLMChat.bindEvents: events bound');
        },

        handleClick: function(e) {
            var target = e.target;
            console.debug('LLMChat.handleClick: target:', target.className);

            if (target.id === 'llm-chat-minimize') {
                this.toggleMinimize();
                return;
            }

            if (target.id === 'llm-chat-tab-add') {
                this.addTab();
                return;
            }

            if (target.classList.contains('llm-chat-tab-close')) {
                var tabId = target.getAttribute('data-tab-id');
                this.closeTab(tabId);
                e.stopPropagation();
                return;
            }

            var tabElement = target.closest('.llm-chat-tab');
            if (tabElement && !target.classList.contains('llm-chat-tab-close')) {
                var tabId = tabElement.getAttribute('data-tab-id');
                this.switchTab(tabId);
                return;
            }

            if (target.classList.contains('llm-chat-send-button')) {
                var tabId = target.getAttribute('data-tab-id');
                this.sendMessage(tabId);
                return;
            }
        },

        handleMouseDown: function(e) {
            var target = e.target;

            if (target.id === 'llm-chat-header' || target.closest('#llm-chat-header')) {
                if (target.classList.contains('llm-chat-header-button')) {
                    return;
                }

                if (this.isMinimized) {
                    this.toggleMinimize();
                    e.preventDefault();
                    return;
                }

                console.debug('LLMChat.handleMouseDown: starting drag');
                this.isDragging = true;
                LLMChatResize.convertToLeftTop(this.widget);

                var rect = this.widget.getBoundingClientRect();
                this.dragOffsetX = e.clientX - rect.left;
                this.dragOffsetY = e.clientY - rect.top;

                e.preventDefault();
                return;
            }

            if (target.classList.contains('llm-chat-resize-handle')) {
                console.debug('LLMChat.handleMouseDown: starting resize');
                LLMChatResize.convertToLeftTop(this.widget);
                this.resizeState = LLMChatResize.startResize(this.widget, e, target.getAttribute('data-direction'));
                this.isResizing = true;
                e.preventDefault();
                return;
            }

            var tabElement = target.closest('.llm-chat-tab');
            if (tabElement && !target.classList.contains('llm-chat-tab-close')) {
                console.debug('LLMChat.handleMouseDown: starting tab drag');
                this.isTabDragging = true;
                this.draggedTabId = tabElement.getAttribute('data-tab-id');
                this.draggedTabElement = tabElement;

                var tabRect = tabElement.getBoundingClientRect();
                this.tabDragOffsetX = e.clientX - tabRect.left;
                this.tabDragOffsetY = e.clientY - tabRect.top;
                this.tabOriginalWidth = tabRect.width;
                this.tabOriginalIndex = Array.from(tabElement.parentNode.children).indexOf(tabElement);

                var clone = tabElement.cloneNode(true);
                clone.classList.add('dragging');
                clone.style.width = tabRect.width + 'px';
                clone.style.left = tabRect.left + 'px';
                clone.style.top = tabRect.top + 'px';
                clone.id = 'llm-chat-tab-drag-clone';
                document.body.appendChild(clone);
                this.dragClone = clone;

                tabElement.style.opacity = '0.3';

                e.preventDefault();
                return;
            }
        },

        handleMouseMove: function(e) {
            if (this.isDragging) {
                LLMChatResize.handleDrag(this.widget, e, this.dragOffsetX, this.dragOffsetY);
                return;
            }

            if (this.isResizing && this.resizeState) {
                LLMChatResize.handleResize(this.widget, e, this.resizeState);
                return;
            }

            if (this.isTabDragging && this.dragClone) {
                var newLeft = e.clientX - this.tabDragOffsetX;
                var newTop = e.clientY - this.tabDragOffsetY;
                this.dragClone.style.left = newLeft + 'px';
                this.dragClone.style.top = newTop + 'px';

                this.pendingDropIndex = null;
                var tabsContainer = this.widget.querySelector('#llm-chat-tabs');
                var tabs = tabsContainer.querySelectorAll('.llm-chat-tab');

                for (var i = 0; i < tabs.length; i++) {
                    var tab = tabs[i];
                    if (tab === this.draggedTabElement) continue;
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
                return;
            }
        },

        handleMouseUp: function(e) {
            if (this.isDragging) {
                console.debug('LLMChat.handleMouseUp: ending drag');
                this.isDragging = false;
                this.savePosition();
            }

            if (this.isResizing) {
                console.debug('LLMChat.handleMouseUp: ending resize');
                this.isResizing = false;
                this.resizeState = null;
                this.saveDimensions();
                this.savePosition();
            }

            if (this.isTabDragging) {
                console.debug('LLMChat.handleMouseUp: ending tab drag');
                this.isTabDragging = false;

                if (this.dragClone && this.dragClone.parentNode) {
                    this.dragClone.parentNode.removeChild(this.dragClone);
                    this.dragClone = null;
                }

                if (this.draggedTabElement) {
                    this.draggedTabElement.style.opacity = '';
                }

                var tabsContainer = this.widget.querySelector('#llm-chat-tabs');

                if (this.pendingDropIndex !== null && this.pendingDropIndex !== undefined) {
                    var addButton = tabsContainer.querySelector('.llm-chat-tab-add');
                    var tabs = tabsContainer.querySelectorAll('.llm-chat-tab');
                    var targetIndex = this.pendingDropIndex;

                    if (targetIndex >= tabs.length) {
                        tabsContainer.insertBefore(this.draggedTabElement, addButton);
                    } else {
                        tabsContainer.insertBefore(this.draggedTabElement, tabs[targetIndex]);
                    }
                }

                var tabElements = tabsContainer.querySelectorAll('.llm-chat-tab');
                this.tabs = LLMChatTabs.reorderTabs(this.tabs, tabElements);

                this.draggedTabId = null;
                this.draggedTabElement = null;
                this.saveState();
            }
        },

        handleKeyDown: function(e) {
            var self = this;
            LLMChatInput.handleKeyDown(e, function(tabId) {
                self.sendMessage(tabId);
            });
        },

        handleWheel: function(e) {
            this.zoomScale = LLMChatZoom.handleWheel(this.widget, e, this.zoomScale);
            LLMChatState.saveZoom(this.zoomScale);
        },

        handleContextMenu: function(e) {
            var tabElement = e.target.closest('.llm-chat-tab');
            if (tabElement) {
                e.preventDefault();
                var tabId = tabElement.getAttribute('data-tab-id');
                console.debug('LLMChat.handleContextMenu: right-click on tab:', tabId);
                this.showContextMenu(e.clientX, e.clientY, tabId);
            }
        },

        showContextMenu: function(x, y, tabId) {
            console.debug('LLMChat.showContextMenu: showing context menu at:', x, y, 'for tab:', tabId);

            this.hideContextMenu();

            this.contextMenu = document.createElement('div');
            this.contextMenu.className = 'llm-chat-context-menu';
            this.contextMenu.innerHTML = LLMChatRender.buildContextMenuHtml(tabId);

            this.contextMenu.style.left = x + 'px';
            this.contextMenu.style.top = y + 'px';

            var self = this;
            this.contextMenu.addEventListener('click', function(e) {
                var item = e.target.closest('.llm-chat-context-menu-item');
                if (item) {
                    var action = item.getAttribute('data-action');
                    var tabId = item.getAttribute('data-tab-id');

                    if (action === 'rename') {
                        self.renameTab(tabId);
                    }

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

        renameTab: function(tabId) {
            var tab = LLMChatTabs.getTabById(this.tabs, tabId);
            if (!tab) return;

            var newTitle = prompt('Enter new tab name:', tab.title);
            if (LLMChatTabs.renameTab(this.tabs, tabId, newTitle)) {
                this.saveState();
                this.render();
            }
        },

        toggleMinimize: function() {
            console.debug('LLMChat.toggleMinimize: toggling minimize state');
            this.isMinimized = !this.isMinimized;

            if (this.isMinimized) {
                var rect = this.widget.getBoundingClientRect();
                this.preMinimizePosition = {
                    left: rect.left,
                    top: rect.top,
                    width: this.widget.offsetWidth,
                    height: this.widget.offsetHeight
                };
                LLMChatState.savePreMinimizePosition(this.preMinimizePosition);

                this.widget.classList.add('minimized');
                this.widget.style.right = '20px';
                this.widget.style.bottom = '20px';
                this.widget.style.left = 'auto';
                this.widget.style.top = 'auto';
                this.widget.style.width = '200px';
                this.widget.style.height = 'auto';
            } else {
                this.widget.classList.remove('minimized');

                if (this.preMinimizePosition) {
                    this.widget.style.left = this.preMinimizePosition.left + 'px';
                    this.widget.style.top = this.preMinimizePosition.top + 'px';
                    this.widget.style.right = 'auto';
                    this.widget.style.bottom = 'auto';
                    this.widget.style.width = this.preMinimizePosition.width + 'px';
                    this.widget.style.height = this.preMinimizePosition.height + 'px';
                } else {
                    var dimensions = LLMChatState.loadDimensions();
                    var position = LLMChatState.loadPosition();
                    if (position) {
                        this.widget.style.left = position.left + 'px';
                        this.widget.style.top = position.top + 'px';
                        this.widget.style.right = 'auto';
                        this.widget.style.bottom = 'auto';
                    }
                    if (dimensions) {
                        this.widget.style.width = dimensions.width + 'px';
                        this.widget.style.height = dimensions.height + 'px';
                    } else {
                        this.widget.style.width = '450px';
                        this.widget.style.height = '500px';
                    }
                }
            }

            this.saveState();
            this.render();
        },

        addTab: function() {
            var newTab = LLMChatTabs.addTab(this.tabs);
            this.activeTabId = newTab.id;
            this.saveState();
            this.render();
        },

        closeTab: function(tabId) {
            var result = LLMChatTabs.closeTab(this.tabs, tabId, this.activeTabId);
            this.tabs = result.tabs;
            this.activeTabId = result.activeTabId;
            this.saveState();
            this.render();
        },

        switchTab: function(tabId) {
            if (this.activeTabId === tabId) return;
            this.activeTabId = tabId;
            this.saveState();
            this.render();
        },

        sendMessage: function(tabId) {
            console.debug('LLMChat.sendMessage: sending message for tab:', tabId);

            var input = this.widget.querySelector('.llm-chat-input[data-tab-id="' + tabId + '"]');
            if (!input) return;

            var message = LLMChatInput.getMessageText(input);
            if (!message) return;

            var tab = LLMChatTabs.getTabById(this.tabs, tabId);
            if (!tab) return;

            LLMChatMessages.addMessage(tab, 'user', message);

            this.saveState();
            this.render();

            var newInput = this.widget.querySelector('.llm-chat-input[data-tab-id="' + tabId + '"]');
            if (newInput) {
                newInput.focus();
            }

            var messagesContainer = this.widget.querySelector('.llm-chat-messages[data-tab-id="' + tabId + '"]');
            LLMChatMessages.scrollToBottom(messagesContainer);
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            LLMChat.init();
        });
    } else {
        LLMChat.init();
    }

    window.LLMChat = LLMChat;

})();
