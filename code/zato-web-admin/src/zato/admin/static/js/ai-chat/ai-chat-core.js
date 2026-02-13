(function() {
    'use strict';

    var AIChat = {
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
        preMinimizeZoom: 1.0,
        zoomScale: 1.0,
        needsConfig: true,
        configMode: 'providers',
        settingsMenu: null,

        init: function() {
            console.debug('AIChat.init: starting initialization');
            var self = this;

            AIChatConfig.init();
            this.loadState();
            this.createWidget();
            this.bindEvents();

            AIChatConfig.checkConfiguredKeys(function(hasKeys) {
                self.needsConfig = !hasKeys;
                self.render();
                console.debug('AIChat.init: initialization complete, needsConfig:', self.needsConfig);
            });
        },

        loadState: function() {
            console.debug('AIChat.loadState: loading state from localStorage');

            this.tabs = AIChatState.loadTabs();
            if (!this.tabs || this.tabs.length === 0) {
                console.debug('AIChat.loadState: no tabs found, creating default tab');
                this.tabs = [AIChatTabs.createDefaultTab()];
            }

            this.activeTabId = AIChatState.loadActiveTabId();
            if (!this.activeTabId || !AIChatTabs.getTabById(this.tabs, this.activeTabId)) {
                this.activeTabId = this.tabs[0].id;
            }

            this.isMinimized = AIChatState.loadMinimized();
            this.preMinimizePosition = AIChatState.loadPreMinimizePosition();
            this.zoomScale = AIChatState.loadZoom();
        },

        saveState: function() {
            console.debug('AIChat.saveState: saving state to localStorage');
            AIChatState.saveTabs(this.tabs);
            AIChatState.saveActiveTabId(this.activeTabId);
            AIChatState.saveMinimized(this.isMinimized);
        },

        savePosition: function() {
            if (!this.widget) return;
            var rect = this.widget.getBoundingClientRect();
            AIChatState.savePosition({ left: rect.left, top: rect.top });
        },

        saveDimensions: function() {
            if (!this.widget) return;
            AIChatState.saveDimensions({
                width: this.widget.offsetWidth,
                height: this.widget.offsetHeight
            });
        },

        createWidget: function() {
            console.debug('AIChat.createWidget: creating widget element');

            this.widget = document.createElement('div');
            this.widget.className = 'ai-chat-widget';
            this.widget.id = 'ai-chat-widget';

            if (this.isMinimized) {
                this.widget.classList.add('minimized');
                this.widget.style.right = '20px';
                this.widget.style.bottom = '20px';
                this.widget.style.left = 'auto';
                this.widget.style.top = 'auto';
                this.widget.style.width = '200px';
                this.widget.style.height = 'auto';
            } else {
                var position = AIChatState.loadPosition();
                var dimensions = AIChatState.loadDimensions();

                if (position) {
                    var clampedLeft = Math.max(0, position.left);
                    var clampedTop = Math.max(0, position.top);
                    this.widget.style.left = clampedLeft + 'px';
                    this.widget.style.top = clampedTop + 'px';
                    this.widget.style.right = 'auto';
                    this.widget.style.bottom = 'auto';
                }

                if (dimensions) {
                    this.widget.style.width = dimensions.width + 'px';
                    this.widget.style.height = dimensions.height + 'px';
                }

                if (this.zoomScale !== 1.0) {
                    AIChatZoom.applyZoom(this.widget, this.zoomScale);
                }
            }

            document.body.appendChild(this.widget);
            console.debug('AIChat.createWidget: widget appended to body');
        },

        render: function() {
            console.debug('AIChat.render: rendering widget, needsConfig:', this.needsConfig, 'configMode:', this.configMode);

            var html = AIChatRender.buildHeaderHtml(this.isMinimized);
            html += AIChatRender.buildTabsHtml(this.tabs, this.activeTabId);
            html += AIChatRender.buildBodyHtml(this.tabs, this.activeTabId, this.needsConfig);
            html += AIChatRender.buildResizeHandlesHtml();

            this.widget.innerHTML = html;

            var messagesContainer = this.widget.querySelector('.ai-chat-messages');
            var hasProviders = messagesContainer ? !!messagesContainer.querySelector('.ai-chat-config-providers') : false;
            var hasKeyInput = messagesContainer ? !!messagesContainer.querySelector('.ai-chat-config-api-key-input') : false;
            var hasEmptyState = messagesContainer ? !!messagesContainer.querySelector('.ai-chat-empty') : false;
            console.debug('AIChat.render: actual content - providers:', hasProviders, 'keyInput:', hasKeyInput, 'emptyState:', hasEmptyState);
        },

        bindEvents: function() {
            console.debug('AIChat.bindEvents: binding events');

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
                AIChatInput.handleInput(e);
            });

            document.addEventListener('keyup', function(e) {
                AIChatInput.handleKeyUp(e);
            });

            this.widget.addEventListener('contextmenu', function(e) {
                self.handleContextMenu(e);
            });

            this.widget.addEventListener('wheel', function(e) {
                self.handleWheel(e);
            }, { passive: false });

            document.addEventListener('click', function(e) {
                self.hideContextMenu();
                self.hideSettingsMenu();
            });

            console.debug('AIChat.bindEvents: events bound');
        },

        handleClick: function(e) {
            var target = e.target;
            console.debug('AIChat.handleClick: target:', target.className);

            if (target.id === 'ai-chat-minimize') {
                this.toggleMinimize();
                return;
            }

            if (target.id === 'ai-chat-menu-button' || target.closest('#ai-chat-menu-button')) {
                this.toggleSettingsMenu();
                e.stopPropagation();
                return;
            }

            var settingsMenuItem = target.closest('.ai-chat-settings-menu-item');
            if (settingsMenuItem) {
                var action = settingsMenuItem.getAttribute('data-action');
                this.handleSettingsAction(action);
                e.stopPropagation();
                return;
            }

            if (target.id === 'ai-chat-tab-add') {
                this.addTab();
                return;
            }

            if (target.classList.contains('ai-chat-tab-close')) {
                var tabId = target.getAttribute('data-tab-id');
                this.closeTab(tabId);
                e.stopPropagation();
                return;
            }

            var tabElement = target.closest('.ai-chat-tab');
            if (tabElement && !target.classList.contains('ai-chat-tab-close')) {
                var tabId = tabElement.getAttribute('data-tab-id');
                this.switchTab(tabId);
                return;
            }

            if (target.classList.contains('ai-chat-send-button')) {
                var tabId = target.getAttribute('data-tab-id');
                this.sendMessage(tabId);
                return;
            }

            var providerEl = target.closest('.ai-chat-config-provider');
            if (providerEl) {
                var providerId = providerEl.getAttribute('data-provider-id');
                this.showKeyInput(providerId);
                return;
            }

            var backEl = target.closest('.ai-chat-config-back');
            if (backEl) {
                this.showProviderSelection();
                return;
            }

            if (target.classList.contains('ai-chat-config-save-button')) {
                var providerId = target.getAttribute('data-provider-id');
                this.saveApiKey(providerId);
                return;
            }
        },

        handleMouseDown: function(e) {
            var target = e.target;

            if (target.id === 'ai-chat-header' || target.closest('#ai-chat-header')) {
                if (target.classList.contains('ai-chat-header-button')) {
                    return;
                }

                if (this.isMinimized) {
                    this.toggleMinimize();
                    e.preventDefault();
                    return;
                }

                console.debug('AIChat.handleMouseDown: starting drag');
                this.isDragging = true;
                AIChatResize.convertToLeftTop(this.widget);

                var rect = this.widget.getBoundingClientRect();
                this.dragOffsetX = e.clientX - rect.left;
                this.dragOffsetY = e.clientY - rect.top;

                e.preventDefault();
                return;
            }

            if (target.classList.contains('ai-chat-resize-handle')) {
                console.debug('AIChat.handleMouseDown: starting resize');
                AIChatResize.convertToLeftTop(this.widget);
                this.resizeState = AIChatResize.startResize(this.widget, e, target.getAttribute('data-direction'));
                this.isResizing = true;
                e.preventDefault();
                return;
            }

            var tabElement = target.closest('.ai-chat-tab');
            if (tabElement && !target.classList.contains('ai-chat-tab-close')) {
                console.debug('AIChat.handleMouseDown: starting tab drag');
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
                clone.id = 'ai-chat-tab-drag-clone';
                document.body.appendChild(clone);
                this.dragClone = clone;

                tabElement.style.opacity = '0.3';

                e.preventDefault();
                return;
            }
        },

        handleMouseMove: function(e) {
            if (this.isDragging) {
                AIChatResize.handleDrag(this.widget, e, this.dragOffsetX, this.dragOffsetY, this.zoomScale);
                return;
            }

            if (this.isResizing && this.resizeState) {
                AIChatResize.handleResize(this.widget, e, this.resizeState);
                return;
            }

            if (this.isTabDragging && this.dragClone) {
                var newLeft = e.clientX - this.tabDragOffsetX;
                var newTop = e.clientY - this.tabDragOffsetY;
                this.dragClone.style.left = newLeft + 'px';
                this.dragClone.style.top = newTop + 'px';

                this.pendingDropIndex = null;
                var tabsContainer = this.widget.querySelector('#ai-chat-tabs');
                var tabs = tabsContainer.querySelectorAll('.ai-chat-tab');

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
                console.debug('AIChat.handleMouseUp: ending drag');
                this.isDragging = false;
                this.savePosition();
            }

            if (this.isResizing) {
                console.debug('AIChat.handleMouseUp: ending resize');
                this.isResizing = false;
                this.resizeState = null;
                this.saveDimensions();
                this.savePosition();
            }

            if (this.isTabDragging) {
                console.debug('AIChat.handleMouseUp: ending tab drag');
                this.isTabDragging = false;

                if (this.dragClone && this.dragClone.parentNode) {
                    this.dragClone.parentNode.removeChild(this.dragClone);
                    this.dragClone = null;
                }

                if (this.draggedTabElement) {
                    this.draggedTabElement.style.opacity = '';
                }

                var tabsContainer = this.widget.querySelector('#ai-chat-tabs');

                if (this.pendingDropIndex !== null && this.pendingDropIndex !== undefined) {
                    var addButton = tabsContainer.querySelector('.ai-chat-tab-add');
                    var tabs = tabsContainer.querySelectorAll('.ai-chat-tab');
                    var targetIndex = this.pendingDropIndex;

                    if (targetIndex >= tabs.length) {
                        tabsContainer.insertBefore(this.draggedTabElement, addButton);
                    } else {
                        tabsContainer.insertBefore(this.draggedTabElement, tabs[targetIndex]);
                    }
                }

                var tabElements = tabsContainer.querySelectorAll('.ai-chat-tab');
                this.tabs = AIChatTabs.reorderTabs(this.tabs, tabElements);

                this.draggedTabId = null;
                this.draggedTabElement = null;
                this.saveState();
            }
        },

        handleKeyDown: function(e) {
            var self = this;
            AIChatInput.handleKeyDown(e, function(tabId) {
                self.sendMessage(tabId);
            });
        },

        handleWheel: function(e) {
            this.zoomScale = AIChatZoom.handleWheel(this.widget, e, this.zoomScale);
            AIChatState.saveZoom(this.zoomScale);
        },

        handleContextMenu: function(e) {
            var tabElement = e.target.closest('.ai-chat-tab');
            if (tabElement) {
                e.preventDefault();
                var tabId = tabElement.getAttribute('data-tab-id');
                console.debug('AIChat.handleContextMenu: right-click on tab:', tabId);
                this.showContextMenu(e.clientX, e.clientY, tabId);
            }
        },

        showContextMenu: function(x, y, tabId) {
            console.debug('AIChat.showContextMenu: showing context menu at:', x, y, 'for tab:', tabId);

            this.hideContextMenu();

            this.contextMenu = document.createElement('div');
            this.contextMenu.className = 'ai-chat-context-menu';
            this.contextMenu.innerHTML = AIChatRender.buildContextMenuHtml(tabId);

            this.contextMenu.style.left = x + 'px';
            this.contextMenu.style.top = y + 'px';

            var self = this;
            this.contextMenu.addEventListener('click', function(e) {
                var item = e.target.closest('.ai-chat-context-menu-item');
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
            var tab = AIChatTabs.getTabById(this.tabs, tabId);
            if (!tab) return;

            var newTitle = prompt('Enter new tab name:', tab.title);
            if (AIChatTabs.renameTab(this.tabs, tabId, newTitle)) {
                this.saveState();
                this.render();
            }
        },

        toggleMinimize: function() {
            console.debug('AIChat.toggleMinimize: toggling minimize state, current isMinimized:', this.isMinimized);
            this.isMinimized = !this.isMinimized;

            var widgetRect = this.widget.getBoundingClientRect();
            var widgetStyles = window.getComputedStyle(this.widget);
            var headerEl = this.widget.querySelector('.ai-chat-header');
            var headerRect = headerEl ? headerEl.getBoundingClientRect() : null;
            var headerStyles = headerEl ? window.getComputedStyle(headerEl) : null;

            console.debug('AIChat.toggleMinimize: before changes:', JSON.stringify({
                isMinimized: this.isMinimized,
                widgetRect: {
                    left: widgetRect.left,
                    top: widgetRect.top,
                    right: widgetRect.right,
                    bottom: widgetRect.bottom,
                    width: widgetRect.width,
                    height: widgetRect.height
                },
                widgetOffsetWidth: this.widget.offsetWidth,
                widgetOffsetHeight: this.widget.offsetHeight,
                widgetStyleLeft: this.widget.style.left,
                widgetStyleTop: this.widget.style.top,
                widgetStyleRight: this.widget.style.right,
                widgetStyleBottom: this.widget.style.bottom,
                widgetStyleWidth: this.widget.style.width,
                widgetStyleHeight: this.widget.style.height,
                widgetComputedPosition: widgetStyles.position,
                widgetComputedOverflow: widgetStyles.overflow,
                widgetComputedTransform: widgetStyles.transform,
                widgetClassList: Array.from(this.widget.classList),
                headerRect: headerRect ? {
                    left: headerRect.left,
                    top: headerRect.top,
                    width: headerRect.width,
                    height: headerRect.height
                } : null,
                headerDisplay: headerStyles ? headerStyles.display : null,
                headerVisibility: headerStyles ? headerStyles.visibility : null,
                windowInnerWidth: window.innerWidth,
                windowInnerHeight: window.innerHeight,
                zoomScale: this.zoomScale
            }));

            if (this.isMinimized) {
                this.widget.style.transform = '';
                this.preMinimizeZoom = this.zoomScale;

                var rect = this.widget.getBoundingClientRect();
                this.preMinimizePosition = {
                    left: rect.left,
                    top: rect.top,
                    width: this.widget.offsetWidth,
                    height: this.widget.offsetHeight
                };
                AIChatState.savePreMinimizePosition(this.preMinimizePosition);

                this.widget.classList.add('minimized');
                this.widget.style.right = '20px';
                this.widget.style.bottom = '20px';
                this.widget.style.left = 'auto';
                this.widget.style.top = 'auto';
                this.widget.style.width = '200px';
                this.widget.style.height = 'auto';

                console.debug('AIChat.toggleMinimize: minimized, saved preMinimizeZoom:', this.preMinimizeZoom);
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
                    var dimensions = AIChatState.loadDimensions();
                    var position = AIChatState.loadPosition();
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

                if (this.preMinimizeZoom && this.preMinimizeZoom !== 1.0) {
                    this.zoomScale = this.preMinimizeZoom;
                    AIChatZoom.applyZoom(this.widget, this.zoomScale);
                    console.debug('AIChat.toggleMinimize: restored zoom:', this.zoomScale);
                }
            }

            this.saveState();
            this.render();

            var afterWidgetRect = this.widget.getBoundingClientRect();
            var afterWidgetStyles = window.getComputedStyle(this.widget);
            var afterHeaderEl = this.widget.querySelector('.ai-chat-header');
            var afterHeaderRect = afterHeaderEl ? afterHeaderEl.getBoundingClientRect() : null;
            var afterHeaderStyles = afterHeaderEl ? window.getComputedStyle(afterHeaderEl) : null;
            var minimizeBtn = this.widget.querySelector('#ai-chat-minimize');
            var minimizeBtnRect = minimizeBtn ? minimizeBtn.getBoundingClientRect() : null;
            var minimizeBtnStyles = minimizeBtn ? window.getComputedStyle(minimizeBtn) : null;
            var bodyEl = this.widget.querySelector('.ai-chat-body');
            var bodyStyles = bodyEl ? window.getComputedStyle(bodyEl) : null;
            var tabsEl = this.widget.querySelector('.ai-chat-tabs');
            var tabsStyles = tabsEl ? window.getComputedStyle(tabsEl) : null;

            console.debug('AIChat.toggleMinimize: after changes:', JSON.stringify({
                isMinimized: this.isMinimized,
                widgetRect: {
                    left: afterWidgetRect.left,
                    top: afterWidgetRect.top,
                    right: afterWidgetRect.right,
                    bottom: afterWidgetRect.bottom,
                    width: afterWidgetRect.width,
                    height: afterWidgetRect.height
                },
                widgetOffsetWidth: this.widget.offsetWidth,
                widgetOffsetHeight: this.widget.offsetHeight,
                widgetStyleLeft: this.widget.style.left,
                widgetStyleTop: this.widget.style.top,
                widgetStyleRight: this.widget.style.right,
                widgetStyleBottom: this.widget.style.bottom,
                widgetStyleWidth: this.widget.style.width,
                widgetStyleHeight: this.widget.style.height,
                widgetComputedPosition: afterWidgetStyles.position,
                widgetComputedOverflow: afterWidgetStyles.overflow,
                widgetComputedTransform: afterWidgetStyles.transform,
                widgetClassList: Array.from(this.widget.classList),
                headerRect: afterHeaderRect ? {
                    left: afterHeaderRect.left,
                    top: afterHeaderRect.top,
                    right: afterHeaderRect.right,
                    bottom: afterHeaderRect.bottom,
                    width: afterHeaderRect.width,
                    height: afterHeaderRect.height
                } : null,
                headerDisplay: afterHeaderStyles ? afterHeaderStyles.display : null,
                headerVisibility: afterHeaderStyles ? afterHeaderStyles.visibility : null,
                minimizeBtnRect: minimizeBtnRect ? {
                    left: minimizeBtnRect.left,
                    top: minimizeBtnRect.top,
                    right: minimizeBtnRect.right,
                    bottom: minimizeBtnRect.bottom,
                    width: minimizeBtnRect.width,
                    height: minimizeBtnRect.height
                } : null,
                minimizeBtnDisplay: minimizeBtnStyles ? minimizeBtnStyles.display : null,
                minimizeBtnVisibility: minimizeBtnStyles ? minimizeBtnStyles.visibility : null,
                minimizeBtnInnerHTML: minimizeBtn ? minimizeBtn.innerHTML : null,
                bodyDisplay: bodyStyles ? bodyStyles.display : null,
                tabsDisplay: tabsStyles ? tabsStyles.display : null,
                windowInnerWidth: window.innerWidth,
                windowInnerHeight: window.innerHeight,
                zoomScale: this.zoomScale,
                widgetInnerHTML_length: this.widget.innerHTML.length
            }));
        },

        addTab: function() {
            var newTab = AIChatTabs.addTab(this.tabs);
            this.activeTabId = newTab.id;
            this.saveState();
            this.render();
        },

        closeTab: function(tabId) {
            var result = AIChatTabs.closeTab(this.tabs, tabId, this.activeTabId);
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
            console.debug('AIChat.sendMessage: sending message for tab:', tabId);

            var input = this.widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
            if (!input) return;

            var message = AIChatInput.getMessageText(input);
            if (!message) return;

            var tab = AIChatTabs.getTabById(this.tabs, tabId);
            if (!tab) return;

            AIChatMessages.addMessage(tab, 'user', message);

            this.saveState();
            this.render();

            var newInput = this.widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
            if (newInput) {
                newInput.focus();
            }

            var messagesContainer = this.widget.querySelector('.ai-chat-messages[data-tab-id="' + tabId + '"]');
            AIChatMessages.scrollToBottom(messagesContainer);
        },

        showKeyInput: function(providerId) {
            console.debug('AIChat.showKeyInput: showing key input for', providerId);
            this.configMode = 'key-input';
            AIChatConfig.selectedProvider = providerId;

            var messagesContainer = this.widget.querySelector('.ai-chat-messages');
            if (messagesContainer) {
                var newHtml = AIChatConfig.buildKeyInputHtml(providerId);
                messagesContainer.innerHTML = newHtml;
                var actualContent = messagesContainer.querySelector('.ai-chat-config-api-key-input');
                console.debug('AIChat.showKeyInput: innerHTML set, api-key-input found:', !!actualContent);
            } else {
                console.debug('AIChat.showKeyInput: messagesContainer not found');
            }
        },

        showProviderSelection: function() {
            console.debug('AIChat.showProviderSelection: showing provider selection');
            this.configMode = 'providers';
            AIChatConfig.selectedProvider = null;

            var messagesContainer = this.widget.querySelector('.ai-chat-messages');
            if (messagesContainer) {
                var newHtml = AIChatConfig.buildProviderSelectionHtml();
                messagesContainer.innerHTML = newHtml;
                var actualContent = messagesContainer.querySelector('.ai-chat-config-providers');
                console.debug('AIChat.showProviderSelection: innerHTML set, providers found:', !!actualContent);
            } else {
                console.debug('AIChat.showProviderSelection: messagesContainer not found');
            }
        },

        saveApiKey: function(providerId) {
            console.debug('AIChat.saveApiKey: saving key for', providerId);
            var self = this;

            var input = this.widget.querySelector('.ai-chat-config-api-key-input');
            if (!input) return;

            var apiKey = input.value.trim();
            if (!apiKey) return;

            var saveButton = this.widget.querySelector('.ai-chat-config-save-button');
            if (saveButton) {
                saveButton.disabled = true;
                saveButton.textContent = 'Saving...';
            }

            AIChatConfig.saveKey(providerId, apiKey, function(success) {
                if (success) {
                    self.showConfigSuccess();
                } else {
                    if (saveButton) {
                        saveButton.disabled = false;
                        saveButton.textContent = 'Save API key';
                    }
                }
            });
        },

        showConfigSuccess: function() {
            console.debug('AIChat.showConfigSuccess: showing success');
            var self = this;

            var messagesContainer = this.widget.querySelector('.ai-chat-messages');
            if (messagesContainer) {
                var html = '<div class="ai-chat-config-container">';
                html += '<div class="ai-chat-config-success">';
                html += '<div class="ai-chat-config-success-icon">';
                html += '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>';
                html += '</div>';
                html += '<div class="ai-chat-config-success-text">API key saved</div>';
                html += '</div>';
                html += '</div>';
                messagesContainer.innerHTML = html;

                self.needsConfig = false;
                self.configMode = 'providers';

                var transitionDelay = 800;
                var startTime = Date.now();
                var checkAndRender = function() {
                    if (Date.now() - startTime >= transitionDelay) {
                        self.render();
                    } else {
                        requestAnimationFrame(checkAndRender);
                    }
                };
                requestAnimationFrame(checkAndRender);
            }
        },

        toggleSettingsMenu: function() {
            console.debug('AIChat.toggleSettingsMenu: toggling settings menu');
            if (this.settingsMenu) {
                this.hideSettingsMenu();
            } else {
                this.showSettingsMenu();
            }
        },

        showSettingsMenu: function() {
            console.debug('AIChat.showSettingsMenu: showing settings menu');
            this.hideSettingsMenu();

            var header = this.widget.querySelector('.ai-chat-header');
            if (!header) return;

            this.settingsMenu = document.createElement('div');
            this.settingsMenu.innerHTML = AIChatConfig.buildSettingsMenuHtml();
            this.settingsMenu.firstChild.style.position = 'absolute';
            this.settingsMenu.firstChild.style.top = (header.offsetHeight + 4) + 'px';
            this.settingsMenu.firstChild.style.left = '12px';

            this.widget.appendChild(this.settingsMenu.firstChild);
            this.settingsMenu = this.widget.querySelector('.ai-chat-settings-menu');
        },

        hideSettingsMenu: function() {
            if (this.settingsMenu && this.settingsMenu.parentNode) {
                this.settingsMenu.parentNode.removeChild(this.settingsMenu);
                this.settingsMenu = null;
            }
        },

        handleSettingsAction: function(action) {
            console.debug('AIChat.handleSettingsAction: action:', action);
            this.hideSettingsMenu();

            if (action === 'change-provider') {
                this.needsConfig = true;
                this.configMode = 'providers';
                this.render();
            } else if (action === 'change-api-key') {
                this.needsConfig = true;
                this.configMode = 'providers';
                this.render();
            }
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            AIChat.init();
        });
    } else {
        AIChat.init();
    }

    window.AIChat = AIChat;

})();
