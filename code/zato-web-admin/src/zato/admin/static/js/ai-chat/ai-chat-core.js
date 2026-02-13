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

            var attachmentEl = target.closest('.ai-chat-attachment');
            if (attachmentEl && !target.closest('.ai-chat-attachment-remove')) {
                var attId = attachmentEl.getAttribute('data-attachment-id');
                var attTabPanel = attachmentEl.closest('.ai-chat-tab-panel');
                var attTabId = attTabPanel ? attTabPanel.getAttribute('data-tab-id') : this.activeTabId;
                var attachments = AIChatTabState.getAttachments(attTabId);
                for (var i = 0; i < attachments.length; i++) {
                    if (attachments[i].id === attId) {
                        this.showPreview(attachments[i]);
                        break;
                    }
                }
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

            if (e.key === 'Escape') {
                if (this.closeTopPreview()) {
                    e.preventDefault();
                    return;
                }
            }

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

            var isImage = file.type && file.type.indexOf('image') === 0;
            var isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
            var isWord = file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || 
                         file.name.toLowerCase().endsWith('.docx');

            if (isImage || isPdf || isWord) {
                reader.readAsDataURL(file);
            } else {
                reader.readAsText(file);
            }
        },

        fileIconMap: {
            'application/json': 'JSON-1.svg',
            'application/javascript': 'JSX.svg',
            'text/javascript': 'JSX.svg',
            'application/pdf': 'Adobe-Acrobat.svg',
            'text/html': 'DOM.svg',
            'text/xml': 'Default.svg',
            'application/xml': 'Default.svg',
            'text/css': 'Stylus.svg',
            'text/plain': 'Default.svg',
            'text/markdown': 'MarkdownLint.svg',
            'text/x-python': 'Python.svg',
            'application/x-python': 'Python.svg',
            'text/x-java': 'Default.svg',
            'text/x-c': 'Default.svg',
            'text/x-c++': 'C++.svg',
            'text/x-ruby': 'RubyGems.svg',
            'text/x-go': 'Go.svg',
            'text/x-rust': 'Default.svg',
            'text/x-typescript': 'TypeScript.svg',
            'text/x-sql': 'SQLite.svg',
            'text/x-yaml': 'YAML.svg',
            'text/yaml': 'YAML.svg',
            'application/x-yaml': 'YAML.svg',
            'text/x-sh': 'Terminal.svg',
            'application/x-sh': 'Terminal.svg',
            'image/png': 'Image.svg',
            'image/jpeg': 'Image.svg',
            'image/gif': 'Image.svg',
            'image/svg+xml': 'Default.svg',
            'image/webp': 'Image.svg',
            'application/zip': 'Brotli.svg',
            'application/x-tar': 'Brotli.svg',
            'application/gzip': 'Brotli.svg',
            'application/x-rar-compressed': 'Brotli.svg',
            'video/mp4': 'Video.svg',
            'video/webm': 'Video.svg',
            'audio/mpeg': 'Audacity.svg',
            'audio/wav': 'Audacity.svg',
            'application/msword': 'Microsoft-Word.svg',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Microsoft-Word.svg',
            'application/vnd.ms-excel': 'Microsoft-Excel.svg',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Microsoft-Excel.svg',
            'application/vnd.ms-powerpoint': 'Microsoft-PowerPoint.svg',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'Microsoft-PowerPoint.svg'
        },

        extensionIconMap: {
            'js': 'JSX.svg',
            'jsx': 'JSX.svg',
            'ts': 'TypeScript.svg',
            'tsx': 'TSX.svg',
            'json': 'JSON-1.svg',
            'py': 'Python.svg',
            'rb': 'RubyGems.svg',
            'java': 'Default.svg',
            'c': 'Default.svg',
            'cpp': 'C++.svg',
            'h': 'Default.svg',
            'hpp': 'C++.svg',
            'go': 'Go.svg',
            'rs': 'Default.svg',
            'php': 'PHP.svg',
            'html': 'DOM.svg',
            'htm': 'DOM.svg',
            'css': 'Stylus.svg',
            'scss': 'Stylus.svg',
            'sass': 'Stylus.svg',
            'less': 'Stylus.svg',
            'xml': 'Default.svg',
            'yaml': 'YAML.svg',
            'yml': 'YAML.svg',
            'md': 'MarkdownLint.svg',
            'markdown': 'MarkdownLint.svg',
            'txt': 'Default.svg',
            'pdf': 'Adobe-Acrobat.svg',
            'doc': 'Microsoft-Word.svg',
            'docx': 'Microsoft-Word.svg',
            'xls': 'Microsoft-Excel.svg',
            'xlsx': 'Microsoft-Excel.svg',
            'ppt': 'Microsoft-PowerPoint.svg',
            'pptx': 'Microsoft-PowerPoint.svg',
            'sql': 'SQLite.svg',
            'sh': 'Terminal.svg',
            'bash': 'Terminal.svg',
            'zsh': 'Terminal.svg',
            'png': 'Image.svg',
            'jpg': 'Image.svg',
            'jpeg': 'Image.svg',
            'gif': 'Image.svg',
            'svg': 'Default.svg',
            'webp': 'Image.svg',
            'ico': 'Image.svg',
            'zip': 'Brotli.svg',
            'tar': 'Brotli.svg',
            'gz': 'Brotli.svg',
            'rar': 'Brotli.svg',
            '7z': 'Brotli.svg',
            'mp4': 'Video.svg',
            'webm': 'Video.svg',
            'avi': 'Video.svg',
            'mov': 'Video.svg',
            'mp3': 'Audacity.svg',
            'wav': 'Audacity.svg',
            'ogg': 'Audacity.svg',
            'vue': 'Vue.svg',
            'svelte': 'Svelte.svg',
            'dockerfile': 'Docker.svg',
            'gradle': 'Gradle.svg',
            'toml': 'TOML.svg',
            'ini': 'Config.svg',
            'cfg': 'Config.svg',
            'conf': 'Config.svg',
            'env': 'dotenv.svg',
            'eslintrc': 'ESLint.svg',
            'prettierrc': 'Prettier.svg',
            'lua': 'Lua.svg',
            'kt': 'Kotlin.svg',
            'scala': 'Default.svg',
            'groovy': 'Groovy.svg',
            'r': 'R.svg',
            'jl': 'Julia.svg',
            'ex': 'Default.svg',
            'exs': 'Default.svg',
            'erl': 'Default.svg',
            'hs': 'Default.svg',
            'elm': 'Elm.svg',
            'clj': 'ClojureJS.svg',
            'cljs': 'ClojureJS.svg'
        },

        getAttachmentIcon: function(mimeType, fileName) {
            var iconFile = 'Default.svg';

            if (fileName) {
                var ext = fileName.split('.').pop().toLowerCase();
                if (this.extensionIconMap[ext]) {
                    iconFile = this.extensionIconMap[ext];
                }
            }

            if (mimeType && this.fileIconMap[mimeType]) {
                iconFile = this.fileIconMap[mimeType];
            } else if (mimeType) {
                if (mimeType.indexOf('image') === 0) {
                    iconFile = 'Image.svg';
                } else if (mimeType.indexOf('video') === 0) {
                    iconFile = 'Video.svg';
                } else if (mimeType.indexOf('audio') === 0) {
                    iconFile = 'Audio.svg';
                } else if (mimeType.indexOf('text') === 0) {
                    iconFile = 'Default.svg';
                }
            }

            return '<img src="/static/file-icons/svg/' + iconFile + '" alt="" class="ai-chat-attachment-icon-img">';
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
                var sizeStr;
                if (att.size >= 1000000) {
                    sizeStr = (att.size / 1000000).toFixed(1) + ' MB';
                } else if (att.size >= 1000) {
                    sizeStr = Math.round(att.size / 1000) + ' KB';
                } else {
                    sizeStr = att.size + ' B';
                }
                var icon = this.getAttachmentIcon(att.type, att.name);
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
        },

        previewPopups: [],

        showPreview: function(attachment) {
            var self = this;
            var popup = document.createElement('div');
            popup.className = 'ai-chat-preview-popup';
            popup.setAttribute('data-attachment-id', attachment.id);

            var offsetX = this.previewPopups.length * 30;
            var offsetY = this.previewPopups.length * 30;
            popup.style.left = (100 + offsetX) + 'px';
            popup.style.top = (100 + offsetY) + 'px';

            var supportedImageTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp', 'image/svg+xml', 'image/bmp'];
            var isImage = attachment.type && supportedImageTypes.indexOf(attachment.type) !== -1;
            var isPdf = attachment.type === 'application/pdf' || attachment.name.toLowerCase().endsWith('.pdf');
            var isWord = attachment.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || 
                         attachment.name.toLowerCase().endsWith('.docx');
            var isEmail = attachment.name.toLowerCase().endsWith('.eml') || attachment.name.toLowerCase().endsWith('.msg');
            var isText = attachment.type && (attachment.type.indexOf('text') === 0 || 
                attachment.type === 'application/json' || 
                attachment.type === 'application/javascript' ||
                attachment.type === 'application/xml');
            var canPreview = isImage || isPdf || isWord || isEmail || isText;

            var html = '';
            html += '<div class="ai-chat-preview-header">';
            html += '<div class="ai-chat-preview-title">' + attachment.name + '</div>';
            html += '<div class="ai-chat-preview-actions">';
            if (canPreview) {
                html += '<button class="ai-chat-preview-copy-btn">Copy</button>';
            }
            html += '<button class="ai-chat-preview-close">';
            html += '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';
            html += '</button>';
            html += '</div>';
            html += '</div>';
            html += '<div class="ai-chat-preview-content">';
            if (!canPreview) {
                html += '<div class="ai-chat-preview-unavailable">Preview not available</div>';
            } else if (isImage) {
                html += '<img class="ai-chat-preview-image" src="' + attachment.content + '" alt="' + attachment.name + '">';
            } else if (isPdf) {
                html += '<div class="ai-chat-preview-pdf-container"></div>';
            } else if (isWord) {
                html += '<div class="ai-chat-preview-word"></div>';
            } else {
                html += '<pre class="ai-chat-preview-text"></pre>';
            }
            html += '</div>';

            popup.innerHTML = html;

            if (isPdf) {
                this.renderPdfPreview(popup, attachment);
            } else if (isWord) {
                this.renderWordPreview(popup, attachment);
            } else if (!isImage) {
                var preEl = popup.querySelector('.ai-chat-preview-text');
                if (preEl) {
                    preEl.textContent = attachment.content;
                }
            }

            document.body.appendChild(popup);
            this.previewPopups.push(popup);

            var header = popup.querySelector('.ai-chat-preview-header');
            this.makePreviewDraggable(popup, header);

            var closeBtn = popup.querySelector('.ai-chat-preview-close');
            closeBtn.addEventListener('click', function() {
                self.closePreview(popup);
            });

            var copyBtn = popup.querySelector('.ai-chat-preview-copy-btn');
            if (copyBtn) {
                copyBtn.addEventListener('click', function() {
                    if (isImage) {
                        var img = popup.querySelector('.ai-chat-preview-image');
                        if (img) {
                            var canvas = document.createElement('canvas');
                            canvas.width = img.naturalWidth;
                            canvas.height = img.naturalHeight;
                            var ctx = canvas.getContext('2d');
                            ctx.drawImage(img, 0, 0);
                            canvas.toBlob(function(blob) {
                                navigator.clipboard.write([new ClipboardItem({ [blob.type]: blob })]).then(function() {
                                    copyBtn.textContent = 'Copied';
                                    setTimeout(function() {
                                        copyBtn.textContent = 'Copy';
                                    }, 1500);
                                });
                            });
                        }
                    } else if (isPdf) {
                        self.extractPdfText(attachment, function(text) {
                            navigator.clipboard.writeText(text).then(function() {
                                copyBtn.textContent = 'Copied';
                                setTimeout(function() {
                                    copyBtn.textContent = 'Copy';
                                }, 1500);
                            });
                        });
                    } else if (isWord) {
                        var wordDiv = popup.querySelector('.ai-chat-preview-word');
                        var text = wordDiv ? wordDiv.innerText : '';
                        navigator.clipboard.writeText(text).then(function() {
                            copyBtn.textContent = 'Copied';
                            setTimeout(function() {
                                copyBtn.textContent = 'Copy';
                            }, 1500);
                        });
                    } else {
                        navigator.clipboard.writeText(attachment.content).then(function() {
                            copyBtn.textContent = 'Copied';
                            setTimeout(function() {
                                copyBtn.textContent = 'Copy';
                            }, 1500);
                        });
                    }
                });
            }

            popup.addEventListener('mousedown', function() {
                self.bringPreviewToFront(popup);
            });
        },

        closePreview: function(popup) {
            var idx = this.previewPopups.indexOf(popup);
            if (idx >= 0) {
                this.previewPopups.splice(idx, 1);
            }
            if (popup.parentNode) {
                popup.parentNode.removeChild(popup);
            }
        },

        closeTopPreview: function() {
            if (this.previewPopups.length > 0) {
                var topPopup = this.previewPopups[this.previewPopups.length - 1];
                this.closePreview(topPopup);
                return true;
            }
            return false;
        },

        bringPreviewToFront: function(popup) {
            var idx = this.previewPopups.indexOf(popup);
            if (idx >= 0 && idx < this.previewPopups.length - 1) {
                this.previewPopups.splice(idx, 1);
                this.previewPopups.push(popup);
            }
            var baseZ = 10001;
            for (var i = 0; i < this.previewPopups.length; i++) {
                this.previewPopups[i].style.zIndex = baseZ + i;
            }
        },

        extractPdfText: function(attachment, callback) {
            if (typeof pdfjsLib === 'undefined') {
                callback('');
                return;
            }

            var base64 = attachment.content.split(',')[1];
            var binary = atob(base64);
            var len = binary.length;
            var bytes = new Uint8Array(len);
            for (var i = 0; i < len; i++) {
                bytes[i] = binary.charCodeAt(i);
            }

            pdfjsLib.getDocument({ data: bytes }).promise.then(function(pdf) {
                var numPages = pdf.numPages;
                var textParts = [];
                var pagesProcessed = 0;

                for (var pageNum = 1; pageNum <= numPages; pageNum++) {
                    (function(pageNum) {
                        pdf.getPage(pageNum).then(function(page) {
                            page.getTextContent().then(function(textContent) {
                                var pageText = textContent.items.map(function(item) {
                                    return item.str;
                                }).join(' ');
                                textParts[pageNum - 1] = pageText;
                                pagesProcessed++;
                                if (pagesProcessed === numPages) {
                                    callback(textParts.join('\n\n'));
                                }
                            });
                        });
                    })(pageNum);
                }
            }).catch(function() {
                callback('');
            });
        },

        renderPdfPreview: function(popup, attachment) {
            var container = popup.querySelector('.ai-chat-preview-pdf-container');
            if (!container || typeof pdfjsLib === 'undefined') {
                var content = popup.querySelector('.ai-chat-preview-content');
                if (content) {
                    content.innerHTML = '<div class="ai-chat-preview-unavailable">Preview not available</div>';
                }
                return;
            }

            pdfjsLib.GlobalWorkerOptions.workerSrc = '/static/js/libs/pdf.worker.min.js';

            var base64 = attachment.content.split(',')[1];
            var binary = atob(base64);
            var len = binary.length;
            var bytes = new Uint8Array(len);
            for (var i = 0; i < len; i++) {
                bytes[i] = binary.charCodeAt(i);
            }

            pdfjsLib.getDocument({ data: bytes }).promise.then(function(pdf) {
                var numPages = pdf.numPages;
                var containerWidth = popup.querySelector('.ai-chat-preview-content').clientWidth - 24;

                for (var pageNum = 1; pageNum <= numPages; pageNum++) {
                    (function(pageNum) {
                        pdf.getPage(pageNum).then(function(page) {
                            var viewport = page.getViewport({ scale: 1.0 });
                            var scale = containerWidth / viewport.width;
                            var scaledViewport = page.getViewport({ scale: scale });

                            var canvas = document.createElement('canvas');
                            canvas.className = 'ai-chat-preview-pdf';
                            canvas.width = scaledViewport.width;
                            canvas.height = scaledViewport.height;
                            container.appendChild(canvas);

                            var ctx = canvas.getContext('2d');
                            page.render({ canvasContext: ctx, viewport: scaledViewport });
                        });
                    })(pageNum);
                }
            }).catch(function() {
                var content = popup.querySelector('.ai-chat-preview-content');
                if (content) {
                    content.innerHTML = '<div class="ai-chat-preview-unavailable">Preview not available</div>';
                }
            });
        },

        renderWordPreview: function(popup, attachment) {
            var wordDiv = popup.querySelector('.ai-chat-preview-word');
            if (!wordDiv || typeof mammoth === 'undefined') {
                var content = popup.querySelector('.ai-chat-preview-content');
                if (content) {
                    content.innerHTML = '<div class="ai-chat-preview-unavailable">Preview not available</div>';
                }
                return;
            }

            var base64 = attachment.content.split(',')[1];
            var binary = atob(base64);
            var len = binary.length;
            var bytes = new Uint8Array(len);
            for (var i = 0; i < len; i++) {
                bytes[i] = binary.charCodeAt(i);
            }

            mammoth.convertToHtml({ arrayBuffer: bytes.buffer }).then(function(result) {
                wordDiv.innerHTML = result.value;
            }).catch(function() {
                var content = popup.querySelector('.ai-chat-preview-content');
                if (content) {
                    content.innerHTML = '<div class="ai-chat-preview-unavailable">Preview not available</div>';
                }
            });
        },

        makePreviewDraggable: function(popup, handle) {
            var isDragging = false;
            var startX, startY, startLeft, startTop;

            handle.addEventListener('mousedown', function(e) {
                if (e.target.closest('.ai-chat-preview-close') || e.target.closest('.ai-chat-preview-copy-btn')) {
                    return;
                }
                isDragging = true;
                startX = e.clientX;
                startY = e.clientY;
                startLeft = popup.offsetLeft;
                startTop = popup.offsetTop;
                e.preventDefault();
            });

            document.addEventListener('mousemove', function(e) {
                if (!isDragging) return;
                var dx = e.clientX - startX;
                var dy = e.clientY - startY;
                popup.style.left = (startLeft + dx) + 'px';
                popup.style.top = (startTop + dy) + 'px';
            });

            document.addEventListener('mouseup', function() {
                isDragging = false;
            });
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
