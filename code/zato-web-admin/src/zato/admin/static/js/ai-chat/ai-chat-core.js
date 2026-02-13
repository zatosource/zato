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
        tabDragStartX: 0,
        tabDragStartY: 0,
        tabDragThreshold: 5,
        tabDragActivated: false,
        contextMenu: null,
        preMinimizePosition: null,
        preMinimizeZoom: 1.0,
        zoomScale: 1.0,
        needsConfig: true,
        configMode: 'providers',
        settingsMenu: null,
        cameFromChat: false,
        hadKeyOnEntry: false,

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

            AIChatTabState.loadFromTabs(this.tabs);

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
            console.debug('AIChat.render: rendering widget, needsConfig:', this.needsConfig, 'configMode:', this.configMode, 'selectedProvider:', AIChatConfig.selectedProvider);

            var html = AIChatRender.buildHeaderHtml(this.isMinimized);
            if (!this.needsConfig) {
                html += AIChatRender.buildTabsHtml(this.tabs, this.activeTabId);
            }
            html += AIChatRender.buildBodyHtml(this.tabs, this.activeTabId, this.needsConfig, this.configMode, AIChatConfig.selectedProvider, this.cameFromChat, this.hadKeyOnEntry);
            html += AIChatRender.buildResizeHandlesHtml();

            this.widget.innerHTML = html;

            var messagesContainer = this.widget.querySelector('.ai-chat-messages');
            var hasProviders = messagesContainer ? !!messagesContainer.querySelector('.ai-chat-config-providers') : false;
            var hasKeyInput = messagesContainer ? !!messagesContainer.querySelector('.ai-chat-config-api-key-input') : false;
            var hasEmptyState = messagesContainer ? !!messagesContainer.querySelector('.ai-chat-empty') : false;
            console.debug('AIChat.render: actual content - providers:', hasProviders, 'keyInput:', hasKeyInput, 'emptyState:', hasEmptyState);

            this.initModelDropdown();
        },

        bindEvents: function() {
            console.debug('AIChat.bindEvents: binding events');

            var self = this;

            this.widget.addEventListener('click', function(e) {
                self.handleClick(e);
            });

            this.widget.addEventListener('mouseenter', function(e) {
                self.handleMouseEnter(e);
            }, true);

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

            this.widget.addEventListener('paste', function(e) {
                self.handlePaste(e);
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
                self.hideOptionsMenu();
            });

            this.widget.addEventListener('change', function(e) {
                self.handleChange(e);
            });

            console.debug('AIChat.bindEvents: events bound');
        },

        handleChange: function(e) {
            var target = e.target;
            if (target.classList.contains('ai-chat-model-select')) {
                var tabId = target.getAttribute('data-tab-id');
                var modelId = target.value;
                console.debug('AIChat.handleChange: model selected:', modelId, 'for tab:', tabId);
                AIChatTabState.setModel(tabId, modelId);
                for (var i = 0; i < this.tabs.length; i++) {
                    if (this.tabs[i].id === tabId) {
                        AIChatTabState.saveToTab(this.tabs[i]);
                        AIChatState.saveTabs(this.tabs);
                        break;
                    }
                }
            }
        },

        initModelDropdown: function() {
            var activePanel = this.widget.querySelector('.ai-chat-tab-panel.active');
            if (!activePanel) {
                return;
            }
            var select = activePanel.querySelector('.ai-chat-model-select');
            if (select && window.ZatoDropdown) {
                var existingDropdown = activePanel.querySelector('.zato-dropdown');
                if (existingDropdown) {
                    existingDropdown.parentNode.removeChild(existingDropdown);
                }
                ZatoDropdown.init(select);
            }
        },

        handleClick: function(e) {
            var target = e.target;
            console.debug('AIChat.handleClick: target:', target.className);

            if (target.id === 'ai-chat-minimize') {
                this.toggleMinimize();
                return;
            }


            var settingsMenuItem = target.closest('.ai-chat-settings-menu-item');
            if (settingsMenuItem) {
                var action = settingsMenuItem.getAttribute('data-action');
                var providerId = settingsMenuItem.getAttribute('data-provider-id');
                this.handleSettingsAction(action, providerId);
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

            if (target.classList.contains('ai-chat-send-button') || target.closest('.ai-chat-send-button')) {
                var button = target.classList.contains('ai-chat-send-button') ? target : target.closest('.ai-chat-send-button');
                var tabId = button.getAttribute('data-tab-id');
                this.sendMessage(tabId);
                return;
            }

            if (target.classList.contains('ai-chat-options-button') || target.closest('.ai-chat-options-button')) {
                var optionsBtn = target.classList.contains('ai-chat-options-button') ? target : target.closest('.ai-chat-options-button');
                this.toggleOptionsMenu(optionsBtn);
                e.stopPropagation();
                return;
            }

            var optionsMenuItem = target.closest('.ai-chat-options-menu-item');
            if (optionsMenuItem) {
                var action = optionsMenuItem.getAttribute('data-action');
                this.handleOptionsAction(action);
                e.stopPropagation();
                return;
            }

            if (target.classList.contains('ai-chat-attachment-remove') || target.closest('.ai-chat-attachment-remove')) {
                var removeBtn = target.classList.contains('ai-chat-attachment-remove') ? target : target.closest('.ai-chat-attachment-remove');
                var attachmentId = removeBtn.getAttribute('data-attachment-id');
                var tabPanel = removeBtn.closest('.ai-chat-tab-panel');
                var tabId = tabPanel ? tabPanel.getAttribute('data-tab-id') : this.activeTabId;
                AIChatTabState.removeAttachment(tabId, attachmentId);
                this.renderAttachments(tabId);
                return;
            }

            var providerEl = target.closest('.ai-chat-config-provider');
            if (providerEl) {
                var providerId = providerEl.getAttribute('data-provider-id');
                console.debug('AIChat.handleClick: provider clicked, providerId:', providerId);
                this.showKeyInput(providerId);
                return;
            }

            var backEl = target.closest('.ai-chat-config-back');
            if (backEl) {
                this.handleBackClick();
                return;
            }

            if (target.classList.contains('ai-chat-config-save-button')) {
                var providerId = target.getAttribute('data-provider-id');
                this.saveApiKey(providerId);
                return;
            }

            if (target.classList.contains('ai-chat-config-key-remove')) {
                var providerId = target.getAttribute('data-provider-id');
                this.removeApiKey(providerId);
                return;
            }

            if (target.classList.contains('ai-chat-config-key-add')) {
                var providerId = target.getAttribute('data-provider-id');
                this.showKeyInput(providerId);
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
                console.debug('AIChat.handleMouseDown: preparing potential tab drag');
                this.isTabDragging = true;
                this.tabDragActivated = false;
                this.draggedTabId = tabElement.getAttribute('data-tab-id');
                this.draggedTabElement = tabElement;
                this.tabDragStartX = e.clientX;
                this.tabDragStartY = e.clientY;

                var tabRect = tabElement.getBoundingClientRect();
                this.tabDragOffsetX = e.clientX - tabRect.left;
                this.tabDragOffsetY = e.clientY - tabRect.top;
                this.tabOriginalWidth = tabRect.width;
                this.tabOriginalIndex = Array.from(tabElement.parentNode.children).indexOf(tabElement);

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

            if (this.isTabDragging) {
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
                    clone.style.width = tabRect.width + 'px';
                    clone.style.left = tabRect.left + 'px';
                    clone.style.top = tabRect.top + 'px';
                    clone.id = 'ai-chat-tab-drag-clone';
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
                console.debug('AIChat.handleMouseUp: ending tab drag, activated:', this.tabDragActivated);
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
                        var draggedTabIndex = AIChatTabs.getTabIndex(this.tabs, this.draggedTabId);
                        if (draggedTabIndex !== -1 && draggedTabIndex !== this.pendingDropIndex) {
                            var tab = this.tabs.splice(draggedTabIndex, 1)[0];
                            var insertAt = this.pendingDropIndex;
                            if (insertAt > draggedTabIndex) {
                                insertAt = insertAt - 1;
                            }
                            this.tabs.splice(insertAt, 0, tab);
                            console.debug('AIChatTabs: moved tab from', draggedTabIndex, 'to', insertAt);
                            this.saveState();
                            this.render();
                        }
                    }
                }

                this.draggedTabId = null;
                this.draggedTabElement = null;
                this.tabDragActivated = false;
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
            AIChatTabState.initTab(newTab.id);
            this.activeTabId = newTab.id;
            this.saveState();
            this.render();
        },

        closeTab: function(tabId) {
            AIChatTabState.removeTab(tabId);
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
            this.renderAttachments(tabId);
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
            console.debug('AIChat.showKeyInput: showing key input for', providerId, 'needsConfig:', this.needsConfig);
            var self = this;
            this.needsConfig = true;
            this.configMode = 'key-input';
            AIChatConfig.selectedProvider = providerId;
            this.render();
            requestAnimationFrame(function() {
                requestAnimationFrame(function() {
                    console.debug('AIChat.showKeyInput: double requestAnimationFrame callback fired');
                    var apiKeyInput = self.widget.querySelector('.ai-chat-config-api-key-input');
                    console.debug('AIChat.showKeyInput: apiKeyInput element:', apiKeyInput);
                    if (apiKeyInput) {
                        console.debug('AIChat.showKeyInput: calling focus()');
                        apiKeyInput.focus();
                        console.debug('AIChat.showKeyInput: document.activeElement after focus:', document.activeElement);
                    } else {
                        console.debug('AIChat.showKeyInput: apiKeyInput not found in DOM');
                    }
                });
            });
        },

        showProviderSelection: function() {
            console.debug('AIChat.showProviderSelection: showing provider selection');
            this.needsConfig = true;
            this.configMode = 'providers';
            AIChatConfig.selectedProvider = null;
            this.render();
        },

        handleBackClick: function() {
            console.debug('AIChat.handleBackClick: cameFromChat:', this.cameFromChat, 'configMode:', this.configMode, 'hadKeyOnEntry:', this.hadKeyOnEntry);
            if (this.configMode === 'key-input') {
                if (this.hadKeyOnEntry) {
                    this.cameFromChat = false;
                    this.needsConfig = false;
                    this.configMode = 'providers';
                    AIChatConfig.selectedProvider = null;
                    this.render();
                } else {
                    this.showProviderSelection();
                }
            } else if (this.configMode === 'manage-keys') {
                this.cameFromChat = false;
                this.needsConfig = false;
                this.configMode = 'providers';
                AIChatConfig.selectedProvider = null;
                this.render();
            } else if (this.configMode === 'providers' && this.cameFromChat && this.hadKeyOnEntry) {
                this.cameFromChat = false;
                this.needsConfig = false;
                this.configMode = 'providers';
                AIChatConfig.selectedProvider = null;
                this.render();
            }
        },

        saveApiKey: function(providerId) {
            console.debug('AIChat.saveApiKey: saving key for', providerId);
            var self = this;

            var input = this.widget.querySelector('.ai-chat-config-api-key-input[data-provider-id="' + providerId + '"]');
            console.debug('AIChat.saveApiKey: input element:', input);
            console.debug('AIChat.saveApiKey: input.value:', input ? input.value : 'N/A');
            console.debug('AIChat.saveApiKey: input.getAttribute("value"):', input ? input.getAttribute('value') : 'N/A');
            console.debug('AIChat.saveApiKey: all inputs:', this.widget.querySelectorAll('input'));
            if (!input) {
                console.debug('AIChat.saveApiKey: no input element found');
                return;
            }

            var apiKey = input.value.trim();
            console.debug('AIChat.saveApiKey: apiKey length:', apiKey.length);
            if (!apiKey) {
                console.debug('AIChat.saveApiKey: apiKey is empty');
                return;
            }

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

        handleMouseEnter: function(e) {
            var target = e.target;
            if (target.id === 'ai-chat-menu-button' || target.closest('#ai-chat-menu-button')) {
                this.showSettingsMenu();
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
            this.settingsMenu.innerHTML = AIChatConfig.buildSettingsMenuHtml(AIChatConfig.hasAnyKey());
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

        handleSettingsAction: function(action, providerId) {
            console.debug('AIChat.handleSettingsAction: action:', action, 'providerId:', providerId);
            this.hideSettingsMenu();

            this.hadKeyOnEntry = AIChatConfig.hasAnyKey();

            if (action === 'change-provider') {
                this.cameFromChat = true;
                this.needsConfig = true;
                this.configMode = 'providers';
                this.render();
            } else if (action === 'manage-keys') {
                this.cameFromChat = true;
                this.needsConfig = true;
                this.configMode = 'manage-keys';
                this.render();
            }
        },

        removeApiKey: function(providerId) {
            console.debug('AIChat.removeApiKey: removing key for', providerId);
            var self = this;

            AIChatConfig.deleteKey(providerId, function(success) {
                if (success) {
                    if (!AIChatConfig.hasAnyKey()) {
                        self.needsConfig = true;
                        self.configMode = 'providers';
                        self.cameFromChat = false;
                        self.hadKeyOnEntry = false;
                    }
                    self.render();
                }
            });
        },

        showFileDialog: function() {
            console.debug('AIChat.showFileDialog: opening file dialog');
            var self = this;
            var input = document.createElement('input');
            input.type = 'file';
            input.multiple = true;
            input.style.display = 'none';
            input.addEventListener('change', function(e) {
                var files = e.target.files;
                if (files && files.length > 0) {
                    console.debug('AIChat.showFileDialog: files selected:', files.length);
                    for (var i = 0; i < files.length; i++) {
                        self.addFileAttachment(files[i]);
                    }
                }
                document.body.removeChild(input);
            });
            document.body.appendChild(input);
            input.click();
        },

        handlePaste: function(e) {
            var inputElement = e.target.closest('.ai-chat-input');
            if (!inputElement) {
                return;
            }

            var self = this;
            var handled = AIChatInput.handlePaste(e, function(attachment, tabId) {
                self.renderAttachments(tabId);
            });

            if (handled) {
                console.debug('AIChat.handlePaste: paste converted to attachment');
            }
        },

        addFileAttachment: function(file) {
            var self = this;
            var tabId = this.activeTabId;
            if (!tabId) {
                console.debug('AIChat.addFileAttachment: no active tab');
                return;
            }

            var reader = new FileReader();
            reader.onload = function(e) {
                AIChatTabState.createAttachmentFromFile(tabId, file, e.target.result);
                self.renderAttachments(tabId);
            };
            reader.readAsText(file);
        },

        getAttachmentIcon: function(mimeType) {
            if (mimeType && mimeType.indexOf('image') === 0) {
                return '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>';
            }
            if (mimeType && (mimeType.indexOf('json') !== -1 || mimeType.indexOf('javascript') !== -1)) {
                return '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"/></svg>';
            }
            if (mimeType && mimeType.indexOf('html') !== -1) {
                return '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.56l-7.35 3.86 1.41-8.18L.48 7.88l8.21-1.19L12 .5l3.31 6.19 8.21 1.19-5.58 5.36 1.41 8.18z"/></svg>';
            }
            if (mimeType && mimeType.indexOf('xml') !== -1) {
                return '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.89 3L14.85 3.4 11.11 21 9.15 20.6 12.89 3M19.59 12L16 8.41 17.41 7 22 11.59V12.41L17.41 17 16 15.59 19.59 12M4.41 12L8 15.59 6.59 17 2 12.41V11.59L6.59 7 8 8.41 4.41 12Z"/></svg>';
            }
            if (mimeType && mimeType.indexOf('pdf') !== -1) {
                return '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z"/></svg>';
            }
            return '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"/></svg>';
        },

        renderAttachments: function(tabId) {
            if (!tabId) {
                tabId = this.activeTabId;
            }
            if (!tabId) {
                return;
            }

            var attachments = AIChatTabState.getAttachments(tabId);
            var tabPanel = this.widget.querySelector('.ai-chat-tab-panel[data-tab-id="' + tabId + '"]');
            if (!tabPanel) {
                return;
            }
            var container = tabPanel.querySelector('.ai-chat-attachments');

            if (attachments.length === 0) {
                if (container) {
                    container.parentNode.removeChild(container);
                }
                return;
            }

            if (!container) {
                var inputArea = tabPanel.querySelector('.ai-chat-input-area');
                if (!inputArea) {
                    return;
                }
                container = document.createElement('div');
                container.className = 'ai-chat-attachments';
                inputArea.insertBefore(container, inputArea.firstChild);
            }

            var html = '';
            for (var i = 0; i < attachments.length; i++) {
                var att = attachments[i];
                var sizeStr = att.size > 1000 ? Math.round(att.size / 1000) + ' KB' : att.size + ' B';
                var icon = this.getAttachmentIcon(att.type);
                html += '<div class="ai-chat-attachment" data-attachment-id="' + att.id + '">';
                html += '<div class="ai-chat-attachment-icon">';
                html += icon;
                html += '</div>';
                html += '<div class="ai-chat-attachment-info">';
                html += '<div class="ai-chat-attachment-name">' + att.name + '</div>';
                html += '<div class="ai-chat-attachment-size">' + sizeStr + '</div>';
                html += '</div>';
                html += '<button class="ai-chat-attachment-remove" data-attachment-id="' + att.id + '" aria-label="Remove">';
                html += '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';
                html += '</button>';
                html += '</div>';
            }
            container.innerHTML = html;
        },

        toggleOptionsMenu: function(clickedButton) {
            var existing = this.widget.querySelector('.ai-chat-options-menu');
            if (existing) {
                existing.parentNode.removeChild(existing);
                return;
            }

            var button = clickedButton;
            if (!button) {
                var activePanel = this.widget.querySelector('.ai-chat-tab-panel[data-tab-id="' + this.activeTabId + '"]');
                button = activePanel ? activePanel.querySelector('.ai-chat-options-button') : null;
            }
            if (!button) {
                return;
            }

            var menu = document.createElement('div');
            menu.className = 'ai-chat-options-menu';
            menu.innerHTML = '<div class="ai-chat-options-menu-item" data-action="add-files">Add files or images</div>' +
                '<div class="ai-chat-options-menu-separator"></div>' +
                '<div class="ai-chat-options-menu-item" data-action="connect-mcp">Connect MCP server</div>' +
                '<div class="ai-chat-options-menu-separator"></div>' +
                '<div class="ai-chat-options-menu-item" data-action="manage-keys">Manage API keys</div>';

            button.parentNode.style.position = 'relative';
            button.parentNode.appendChild(menu);
        },

        hideOptionsMenu: function() {
            var menu = this.widget.querySelector('.ai-chat-options-menu');
            if (menu) {
                menu.parentNode.removeChild(menu);
            }
        },

        handleOptionsAction: function(action) {
            console.debug('AIChat.handleOptionsAction:', action);
            this.hideOptionsMenu();

            if (action === 'manage-keys') {
                this.cameFromChat = true;
                this.hadKeyOnEntry = AIChatConfig.hasAnyKey();
                this.needsConfig = true;
                this.configMode = 'manage-keys';
                this.render();
            } else if (action === 'add-files') {
                this.showFileDialog();
            } else if (action === 'connect-mcp') {
                console.debug('AIChat.handleOptionsAction: connect-mcp not yet implemented');
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
