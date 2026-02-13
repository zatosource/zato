(function() {
    'use strict';

    var STORAGE_KEY_TABS = 'zato.llm-chat.tabs';
    var STORAGE_KEY_ACTIVE_TAB = 'zato.llm-chat.active-tab';
    var STORAGE_KEY_POSITION = 'zato.llm-chat.position';
    var STORAGE_KEY_DIMENSIONS = 'zato.llm-chat.dimensions';
    var STORAGE_KEY_MINIMIZED = 'zato.llm-chat.minimized';
    var STORAGE_KEY_PRE_MINIMIZE_POSITION = 'zato.llm-chat.pre-minimize-position';

    var LLMChat = {
        widget: null,
        tabs: [],
        activeTabId: null,
        isMinimized: false,
        isDragging: false,
        isResizing: false,
        resizeDirection: null,
        dragStartX: 0,
        dragStartY: 0,
        dragOffsetX: 0,
        dragOffsetY: 0,
        resizeStartX: 0,
        resizeStartY: 0,
        resizeStartWidth: 0,
        resizeStartHeight: 0,
        resizeStartLeft: 0,
        resizeStartTop: 0,
        isTabDragging: false,
        draggedTabId: null,
        draggedTabElement: null,
        contextMenu: null,
        preMinimizePosition: null,

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

            var tabsJson = localStorage.getItem(STORAGE_KEY_TABS);
            console.debug('LLMChat.loadState: tabsJson:', tabsJson);

            if (tabsJson) {
                try {
                    this.tabs = JSON.parse(tabsJson);
                    console.debug('LLMChat.loadState: parsed tabs:', JSON.stringify(this.tabs));
                } catch (e) {
                    console.debug('LLMChat.loadState: failed to parse tabs, using default');
                    this.tabs = [];
                }
            }

            if (this.tabs.length === 0) {
                console.debug('LLMChat.loadState: no tabs found, creating default tab');
                this.tabs = [{
                    id: this.generateTabId(),
                    title: 'Chat 1',
                    messages: []
                }];
            }

            this.activeTabId = localStorage.getItem(STORAGE_KEY_ACTIVE_TAB);
            console.debug('LLMChat.loadState: activeTabId from storage:', this.activeTabId);

            if (!this.activeTabId || !this.getTabById(this.activeTabId)) {
                this.activeTabId = this.tabs[0].id;
                console.debug('LLMChat.loadState: using first tab as active:', this.activeTabId);
            }

            var minimizedStr = localStorage.getItem(STORAGE_KEY_MINIMIZED);
            this.isMinimized = minimizedStr === 'true';
            console.debug('LLMChat.loadState: isMinimized:', this.isMinimized);

            var preMinPosJson = localStorage.getItem(STORAGE_KEY_PRE_MINIMIZE_POSITION);
            console.debug('LLMChat.loadState: preMinPosJson:', preMinPosJson);
            if (preMinPosJson) {
                try {
                    this.preMinimizePosition = JSON.parse(preMinPosJson);
                    console.debug('LLMChat.loadState: preMinimizePosition:', JSON.stringify(this.preMinimizePosition));
                } catch (e) {
                    console.debug('LLMChat.loadState: failed to parse preMinimizePosition');
                    this.preMinimizePosition = null;
                }
            }
        },

        saveState: function() {
            console.debug('LLMChat.saveState: saving state to localStorage');
            console.debug('LLMChat.saveState: tabs:', JSON.stringify(this.tabs));
            console.debug('LLMChat.saveState: activeTabId:', this.activeTabId);
            console.debug('LLMChat.saveState: isMinimized:', this.isMinimized);

            localStorage.setItem(STORAGE_KEY_TABS, JSON.stringify(this.tabs));
            localStorage.setItem(STORAGE_KEY_ACTIVE_TAB, this.activeTabId);
            localStorage.setItem(STORAGE_KEY_MINIMIZED, this.isMinimized.toString());
        },

        savePosition: function() {
            if (!this.widget) return;

            var rect = this.widget.getBoundingClientRect();
            var position = {
                left: rect.left,
                top: rect.top
            };
            console.debug('LLMChat.savePosition: saving position:', JSON.stringify(position));
            localStorage.setItem(STORAGE_KEY_POSITION, JSON.stringify(position));
        },

        saveDimensions: function() {
            if (!this.widget) return;

            var dimensions = {
                width: this.widget.offsetWidth,
                height: this.widget.offsetHeight
            };
            console.debug('LLMChat.saveDimensions: saving dimensions:', JSON.stringify(dimensions));
            localStorage.setItem(STORAGE_KEY_DIMENSIONS, JSON.stringify(dimensions));
        },

        loadPosition: function() {
            var positionJson = localStorage.getItem(STORAGE_KEY_POSITION);
            console.debug('LLMChat.loadPosition: positionJson:', positionJson);

            if (positionJson) {
                try {
                    return JSON.parse(positionJson);
                } catch (e) {
                    console.debug('LLMChat.loadPosition: failed to parse position');
                }
            }
            return null;
        },

        loadDimensions: function() {
            var dimensionsJson = localStorage.getItem(STORAGE_KEY_DIMENSIONS);
            console.debug('LLMChat.loadDimensions: dimensionsJson:', dimensionsJson);

            if (dimensionsJson) {
                try {
                    return JSON.parse(dimensionsJson);
                } catch (e) {
                    console.debug('LLMChat.loadDimensions: failed to parse dimensions');
                }
            }
            return null;
        },

        generateTabId: function() {
            return 'tab-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        },

        getTabById: function(tabId) {
            for (var i = 0; i < this.tabs.length; i++) {
                if (this.tabs[i].id === tabId) {
                    return this.tabs[i];
                }
            }
            return null;
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
            }

            var position = this.loadPosition();
            if (position) {
                this.widget.style.left = position.left + 'px';
                this.widget.style.top = position.top + 'px';
                this.widget.style.right = 'auto';
                this.widget.style.bottom = 'auto';
            }

            var dimensions = this.loadDimensions();
            if (dimensions) {
                this.widget.style.width = dimensions.width + 'px';
                this.widget.style.height = dimensions.height + 'px';
            }

            document.body.appendChild(this.widget);
            console.debug('LLMChat.createWidget: widget appended to body');
        },

        render: function() {
            console.debug('LLMChat.render: rendering widget');

            var html = this.buildHeaderHtml();
            html += this.buildTabsHtml();
            html += this.buildBodyHtml();
            html += this.buildResizeHandlesHtml();

            this.widget.innerHTML = html;
            console.debug('LLMChat.render: widget html set');
        },

        buildHeaderHtml: function() {
            var html = '<div class="llm-chat-header" id="llm-chat-header">';
            html += '<span class="llm-chat-header-title">LLM chat</span>';
            html += '<div class="llm-chat-header-controls">';
            var icon = this.isMinimized ? '+' : '−';
            html += '<button class="llm-chat-header-button" id="llm-chat-minimize" title="Minimize">' + icon + '</button>';
            html += '</div>';
            html += '</div>';
            return html;
        },

        buildResizeHandlesHtml: function() {
            var html = '';
            html += '<div class="llm-chat-resize-handle llm-chat-resize-nw" data-direction="nw"></div>';
            html += '<div class="llm-chat-resize-handle llm-chat-resize-ne" data-direction="ne"></div>';
            html += '<div class="llm-chat-resize-handle llm-chat-resize-sw" data-direction="sw"></div>';
            html += '<div class="llm-chat-resize-handle llm-chat-resize-se" data-direction="se"></div>';
            return html;
        },

        buildTabsHtml: function() {
            var html = '<div class="llm-chat-tabs" id="llm-chat-tabs">';

            for (var i = 0; i < this.tabs.length; i++) {
                var tab = this.tabs[i];
                var activeClass = tab.id === this.activeTabId ? ' active' : '';
                html += '<div class="llm-chat-tab' + activeClass + '" data-tab-id="' + tab.id + '" draggable="true">';
                html += '<span class="llm-chat-tab-title">' + this.escapeHtml(tab.title) + '</span>';
                if (this.tabs.length > 1) {
                    html += '<span class="llm-chat-tab-close" data-tab-id="' + tab.id + '">✕</span>';
                }
                html += '</div>';
            }

            html += '<button class="llm-chat-tab-add" id="llm-chat-tab-add" title="New chat">+</button>';
            html += '</div>';
            return html;
        },

        buildBodyHtml: function() {
            var html = '<div class="llm-chat-body">';

            for (var i = 0; i < this.tabs.length; i++) {
                var tab = this.tabs[i];
                var activeClass = tab.id === this.activeTabId ? ' active' : '';
                html += '<div class="llm-chat-tab-panel' + activeClass + '" data-tab-id="' + tab.id + '">';
                html += this.buildMessagesHtml(tab);
                html += this.buildInputAreaHtml(tab);
                html += '</div>';
            }

            html += '</div>';
            return html;
        },

        buildMessagesHtml: function(tab) {
            var html = '<div class="llm-chat-messages" data-tab-id="' + tab.id + '">';

            if (tab.messages.length === 0) {
                html += '<div class="llm-chat-empty">';
                html += '<div class="llm-chat-empty-icon">💬</div>';
                html += '<div>Start a conversation</div>';
                html += '</div>';
            } else {
                for (var i = 0; i < tab.messages.length; i++) {
                    var msg = tab.messages[i];
                    html += '<div class="llm-chat-message ' + msg.role + '">';
                    html += this.escapeHtml(msg.content);
                    html += '</div>';
                }
            }

            html += '</div>';
            return html;
        },

        buildInputAreaHtml: function(tab) {
            var html = '<div class="llm-chat-input-area">';
            html += '<textarea class="llm-chat-input" data-tab-id="' + tab.id + '" placeholder="Type a message..." rows="1"></textarea>';
            html += '<button class="llm-chat-send-button" data-tab-id="' + tab.id + '">Send</button>';
            html += '</div>';
            return html;
        },

        escapeHtml: function(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
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

            this.widget.addEventListener('keydown', function(e) {
                self.handleKeyDown(e);
            });

            this.widget.addEventListener('contextmenu', function(e) {
                self.handleContextMenu(e);
            });

            document.addEventListener('click', function(e) {
                self.hideContextMenu();
            });

            console.debug('LLMChat.bindEvents: events bound');
        },

        handleClick: function(e) {
            var target = e.target;
            console.debug('LLMChat.handleClick: target:', target.className);

            if (target.id === 'llm-chat-minimize') {
                console.debug('LLMChat.handleClick: minimize button clicked');
                this.toggleMinimize();
                return;
            }

            if (target.id === 'llm-chat-tab-add') {
                console.debug('LLMChat.handleClick: add tab button clicked');
                this.addTab();
                return;
            }

            if (target.classList.contains('llm-chat-tab-close')) {
                var tabId = target.getAttribute('data-tab-id');
                console.debug('LLMChat.handleClick: close tab clicked, tabId:', tabId);
                this.closeTab(tabId);
                e.stopPropagation();
                return;
            }

            var tabElement = target.closest('.llm-chat-tab');
            if (tabElement && !target.classList.contains('llm-chat-tab-close')) {
                var tabId = tabElement.getAttribute('data-tab-id');
                console.debug('LLMChat.handleClick: tab clicked, tabId:', tabId);
                this.switchTab(tabId);
                return;
            }

            if (target.classList.contains('llm-chat-send-button')) {
                var tabId = target.getAttribute('data-tab-id');
                console.debug('LLMChat.handleClick: send button clicked, tabId:', tabId);
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
                    console.debug('LLMChat.handleMouseDown: widget is minimized, expanding instead of dragging');
                    this.toggleMinimize();
                    e.preventDefault();
                    return;
                }

                console.debug('LLMChat.handleMouseDown: starting drag');
                this.isDragging = true;

                var rect = this.widget.getBoundingClientRect();
                this.dragOffsetX = e.clientX - rect.left;
                this.dragOffsetY = e.clientY - rect.top;

                this.widget.style.right = 'auto';
                this.widget.style.bottom = 'auto';
                this.widget.style.left = rect.left + 'px';
                this.widget.style.top = rect.top + 'px';

                e.preventDefault();
                return;
            }

            if (target.classList.contains('llm-chat-resize-handle')) {
                console.debug('LLMChat.handleMouseDown: starting resize');
                this.isResizing = true;
                this.resizeDirection = target.getAttribute('data-direction');
                this.resizeStartX = e.clientX;
                this.resizeStartY = e.clientY;
                this.resizeStartWidth = this.widget.offsetWidth;
                this.resizeStartHeight = this.widget.offsetHeight;

                var rect = this.widget.getBoundingClientRect();
                this.resizeStartLeft = rect.left;
                this.resizeStartTop = rect.top;
                this.widget.style.right = 'auto';
                this.widget.style.bottom = 'auto';
                this.widget.style.left = rect.left + 'px';
                this.widget.style.top = rect.top + 'px';

                e.preventDefault();
                return;
            }

            var tabElement = target.closest('.llm-chat-tab');
            if (tabElement && !target.classList.contains('llm-chat-tab-close')) {
                console.debug('LLMChat.handleMouseDown: starting tab drag');
                this.isTabDragging = true;
                this.draggedTabId = tabElement.getAttribute('data-tab-id');
                this.draggedTabElement = tabElement;
                tabElement.classList.add('dragging');
                e.preventDefault();
                return;
            }
        },

        handleMouseMove: function(e) {
            if (this.isDragging) {
                var newLeft = e.clientX - this.dragOffsetX;
                var newTop = e.clientY - this.dragOffsetY;

                newLeft = Math.max(0, Math.min(newLeft, window.innerWidth - this.widget.offsetWidth));
                newTop = Math.max(0, Math.min(newTop, window.innerHeight - this.widget.offsetHeight));

                this.widget.style.left = newLeft + 'px';
                this.widget.style.top = newTop + 'px';
                return;
            }

            if (this.isResizing) {
                var deltaX = e.clientX - this.resizeStartX;
                var deltaY = e.clientY - this.resizeStartY;
                var dir = this.resizeDirection;

                var newWidth = this.resizeStartWidth;
                var newHeight = this.resizeStartHeight;
                var newLeft = this.resizeStartLeft;
                var newTop = this.resizeStartTop;

                if (dir === 'se') {
                    newWidth = Math.max(300, this.resizeStartWidth + deltaX);
                    newHeight = Math.max(200, this.resizeStartHeight + deltaY);
                } else if (dir === 'sw') {
                    newWidth = Math.max(300, this.resizeStartWidth - deltaX);
                    newHeight = Math.max(200, this.resizeStartHeight + deltaY);
                    newLeft = this.resizeStartLeft + (this.resizeStartWidth - newWidth);
                } else if (dir === 'ne') {
                    newWidth = Math.max(300, this.resizeStartWidth + deltaX);
                    newHeight = Math.max(200, this.resizeStartHeight - deltaY);
                    newTop = this.resizeStartTop + (this.resizeStartHeight - newHeight);
                } else if (dir === 'nw') {
                    newWidth = Math.max(300, this.resizeStartWidth - deltaX);
                    newHeight = Math.max(200, this.resizeStartHeight - deltaY);
                    newLeft = this.resizeStartLeft + (this.resizeStartWidth - newWidth);
                    newTop = this.resizeStartTop + (this.resizeStartHeight - newHeight);
                }

                this.widget.style.width = newWidth + 'px';
                this.widget.style.height = newHeight + 'px';
                this.widget.style.left = newLeft + 'px';
                this.widget.style.top = newTop + 'px';
                return;
            }

            if (this.isTabDragging && this.draggedTabElement) {
                var tabsContainer = this.widget.querySelector('#llm-chat-tabs');
                var tabs = tabsContainer.querySelectorAll('.llm-chat-tab');
                var draggedRect = this.draggedTabElement.getBoundingClientRect();

                for (var i = 0; i < tabs.length; i++) {
                    var tab = tabs[i];
                    if (tab === this.draggedTabElement) continue;

                    var rect = tab.getBoundingClientRect();
                    var midX = rect.left + rect.width / 2;

                    if (e.clientX < midX && e.clientX > rect.left) {
                        tabsContainer.insertBefore(this.draggedTabElement, tab);
                        break;
                    } else if (e.clientX > midX && e.clientX < rect.right) {
                        if (tab.nextSibling && tab.nextSibling.classList && tab.nextSibling.classList.contains('llm-chat-tab')) {
                            tabsContainer.insertBefore(this.draggedTabElement, tab.nextSibling);
                        } else {
                            var addButton = tabsContainer.querySelector('.llm-chat-tab-add');
                            tabsContainer.insertBefore(this.draggedTabElement, addButton);
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
                this.resizeDirection = null;
                this.saveDimensions();
                this.savePosition();
            }

            if (this.isTabDragging) {
                console.debug('LLMChat.handleMouseUp: ending tab drag');
                this.isTabDragging = false;

                if (this.draggedTabElement) {
                    this.draggedTabElement.classList.remove('dragging');
                }

                var tabsContainer = this.widget.querySelector('#llm-chat-tabs');
                var tabElements = tabsContainer.querySelectorAll('.llm-chat-tab');
                var newOrder = [];

                for (var i = 0; i < tabElements.length; i++) {
                    var tabId = tabElements[i].getAttribute('data-tab-id');
                    var tab = this.getTabById(tabId);
                    if (tab) {
                        newOrder.push(tab);
                    }
                }

                this.tabs = newOrder;
                this.draggedTabId = null;
                this.draggedTabElement = null;
                this.saveState();
                console.debug('LLMChat.handleMouseUp: tabs reordered:', JSON.stringify(this.tabs.map(function(t) { return t.title; })));
            }
        },

        handleKeyDown: function(e) {
            if (e.target.classList.contains('llm-chat-input')) {
                if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey) {
                    e.preventDefault();
                    var tabId = e.target.getAttribute('data-tab-id');
                    console.debug('LLMChat.handleKeyDown: enter pressed in input, tabId:', tabId);
                    this.sendMessage(tabId);
                } else if (e.key === 'Enter' && e.ctrlKey) {
                    e.preventDefault();
                    console.debug('LLMChat.handleKeyDown: ctrl+enter pressed, expanding textarea');
                    var currentHeight = e.target.offsetHeight;
                    var newHeight = currentHeight + 50;
                    e.target.style.height = newHeight + 'px';
                    console.debug('LLMChat.handleKeyDown: textarea height changed from', currentHeight, 'to', newHeight);
                }
            }
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
            this.contextMenu.innerHTML = '<div class="llm-chat-context-menu-item" data-action="rename" data-tab-id="' + tabId + '">Rename tab</div>';

            this.contextMenu.style.left = x + 'px';
            this.contextMenu.style.top = y + 'px';

            var self = this;
            this.contextMenu.addEventListener('click', function(e) {
                var item = e.target.closest('.llm-chat-context-menu-item');
                if (item) {
                    var action = item.getAttribute('data-action');
                    var tabId = item.getAttribute('data-tab-id');
                    console.debug('LLMChat.contextMenu click: action:', action, 'tabId:', tabId);

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
            console.debug('LLMChat.renameTab: renaming tab:', tabId);

            var tab = this.getTabById(tabId);
            if (!tab) {
                console.debug('LLMChat.renameTab: tab not found');
                return;
            }

            var newTitle = prompt('Enter new tab name:', tab.title);
            if (newTitle && newTitle.trim()) {
                tab.title = newTitle.trim();
                console.debug('LLMChat.renameTab: new title:', tab.title);
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
                localStorage.setItem(STORAGE_KEY_PRE_MINIMIZE_POSITION, JSON.stringify(this.preMinimizePosition));
                console.debug('LLMChat.toggleMinimize: saved preMinimizePosition:', JSON.stringify(this.preMinimizePosition));

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
                    console.debug('LLMChat.toggleMinimize: restored to preMinimizePosition:', JSON.stringify(this.preMinimizePosition));
                } else {
                    var dimensions = this.loadDimensions();
                    var position = this.loadPosition();
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
            console.debug('LLMChat.toggleMinimize: isMinimized:', this.isMinimized);
        },

        addTab: function() {
            console.debug('LLMChat.addTab: adding new tab');

            var newTab = {
                id: this.generateTabId(),
                title: 'Chat ' + (this.tabs.length + 1),
                messages: []
            };

            this.tabs.push(newTab);
            this.activeTabId = newTab.id;

            this.saveState();
            this.render();

            console.debug('LLMChat.addTab: new tab added:', JSON.stringify(newTab));
        },

        closeTab: function(tabId) {
            console.debug('LLMChat.closeTab: closing tab:', tabId);

            if (this.tabs.length <= 1) {
                console.debug('LLMChat.closeTab: cannot close last tab');
                return;
            }

            var tabIndex = -1;
            for (var i = 0; i < this.tabs.length; i++) {
                if (this.tabs[i].id === tabId) {
                    tabIndex = i;
                    break;
                }
            }

            if (tabIndex === -1) {
                console.debug('LLMChat.closeTab: tab not found');
                return;
            }

            this.tabs.splice(tabIndex, 1);

            if (this.activeTabId === tabId) {
                var newActiveIndex = Math.min(tabIndex, this.tabs.length - 1);
                this.activeTabId = this.tabs[newActiveIndex].id;
                console.debug('LLMChat.closeTab: switched to tab:', this.activeTabId);
            }

            this.saveState();
            this.render();
        },

        switchTab: function(tabId) {
            console.debug('LLMChat.switchTab: switching to tab:', tabId);

            if (this.activeTabId === tabId) {
                console.debug('LLMChat.switchTab: already active');
                return;
            }

            this.activeTabId = tabId;
            this.saveState();
            this.render();
        },

        sendMessage: function(tabId) {
            console.debug('LLMChat.sendMessage: sending message for tab:', tabId);

            var input = this.widget.querySelector('.llm-chat-input[data-tab-id="' + tabId + '"]');
            if (!input) {
                console.debug('LLMChat.sendMessage: input not found');
                return;
            }

            var message = input.value.trim();
            console.debug('LLMChat.sendMessage: message:', JSON.stringify(message));

            if (!message) {
                console.debug('LLMChat.sendMessage: empty message, ignoring');
                return;
            }

            var tab = this.getTabById(tabId);
            if (!tab) {
                console.debug('LLMChat.sendMessage: tab not found');
                return;
            }

            tab.messages.push({
                role: 'user',
                content: message
            });

            console.debug('LLMChat.sendMessage: message added to tab');

            this.saveState();
            this.render();

            var newInput = this.widget.querySelector('.llm-chat-input[data-tab-id="' + tabId + '"]');
            if (newInput) {
                newInput.focus();
            }

            var messagesContainer = this.widget.querySelector('.llm-chat-messages[data-tab-id="' + tabId + '"]');
            if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            LLMChat.init();
        });
    } else {
        LLMChat.init();
    }

})();
