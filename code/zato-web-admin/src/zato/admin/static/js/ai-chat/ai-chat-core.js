(function() {
    'use strict';

    var AIChat = {
        widget: null,
        tabs: [],
        activeTabId: null,
        isMinimized: false,
        isMaximized: false,
        preMinimizePosition: null,
        preMinimizeZoom: 1.0,
        preMaximizeState: null,
        zoomScale: 1.0,
        needsConfig: true,
        configMode: 'providers',
        cameFromChat: false,
        hadKeyOnEntry: false,

        init: function() {
            console.debug('AIChat.init: starting initialization');
            var self = this;

            if (typeof markedEmoji !== 'undefined' && markedEmoji.markedEmoji) {
                marked.use(markedEmoji.markedEmoji());
            }

            AIChatConfig.init();
            AIChatZoom.init();
            this.loadState();
            this.widget = AIChatWidget.create(this.isMinimized, this.zoomScale);
            if (this.isMaximized) {
                this.widget.classList.add('maximized');
                document.documentElement.classList.add('ai-chat-maximized');
            }
            this.bindEvents();

            var savedConfigMode = AIChatState.loadConfigMode();
            console.log('AIChat.init: savedConfigMode=', savedConfigMode);

            AIChatConfig.checkConfiguredKeys(function(hasKeys) {
                console.log('AIChat.init: hasKeys=', hasKeys, 'savedConfigMode=', savedConfigMode);
                if (savedConfigMode) {
                    self.needsConfig = true;
                    self.configMode = savedConfigMode;
                    self.cameFromChat = true;
                } else {
                    self.needsConfig = !hasKeys;
                }

                if (self.configMode === 'manage-mcp' || self.configMode === 'add-mcp' || self.configMode === 'manage-keys') {
                    AIChatMCP.loadServers(function() {
                        self.render();
                        console.debug('AIChat.init: initialization complete, needsConfig:', self.needsConfig);
                        self.focusInputIfNotMinimized();
                    });
                } else {
                    self.render();
                    console.debug('AIChat.init: initialization complete, needsConfig:', self.needsConfig);
                    self.focusInputIfNotMinimized();
                }
            });

            window.addEventListener('focus', function() {
                self.focusInputIfNotMinimized();
            });

        },

        focusInputIfNotMinimized: function() {
            if (this.isMinimized || this.needsConfig) {
                return;
            }
            this.focusInput(this.activeTabId);
        },

        loadState: function() {
            this.tabs = AIChatState.loadTabs();
            if (!this.tabs || this.tabs.length === 0) {
                this.tabs = [AIChatTabs.createDefaultTab()];
            }

            AIChatTabState.loadFromTabs(this.tabs);

            this.activeTabId = AIChatState.loadActiveTabId();
            if (!this.activeTabId || !AIChatTabs.getTabById(this.tabs, this.activeTabId)) {
                this.activeTabId = this.tabs[0].id;
            }

            this.isMinimized = AIChatState.loadMinimized();
            this.isMaximized = AIChatState.loadMaximized();
            this.preMinimizePosition = AIChatState.loadPreMinimizePosition();
            this.preMaximizeState = AIChatState.loadPreMaximizeState();
            this.zoomScale = AIChatState.loadZoom();
        },

        saveState: function() {
            for (var i = 0; i < this.tabs.length; i++) {
                AIChatTabState.saveToTab(this.tabs[i]);
            }
            AIChatState.saveTabs(this.tabs);
            AIChatState.saveActiveTabId(this.activeTabId);
            AIChatState.saveMinimized(this.isMinimized);
            AIChatState.saveMaximized(this.isMaximized);
            AIChatState.savePreMaximizeState(this.preMaximizeState);
        },

        render: function() {
            console.log('AIChatCore.render: needsConfig=', this.needsConfig, 'configMode=', this.configMode, 'cameFromChat=', this.cameFromChat);

            if (this.needsConfig && this.configMode && this.configMode !== 'providers') {
                AIChatState.saveConfigMode(this.configMode);
            } else {
                AIChatState.saveConfigMode(null);
            }

            var html = AIChatRender.buildHeaderHtml(this.isMinimized, this.isMaximized);
            if (!this.needsConfig) {
                html += AIChatRender.buildTabsHtml(this.tabs, this.activeTabId);
            }
            html += AIChatRender.buildBodyHtml(this.tabs, this.activeTabId, this.needsConfig, this.configMode, AIChatConfig.selectedProvider, this.cameFromChat, this.hadKeyOnEntry);
            html += AIChatRender.buildResizeHandlesHtml();

            this.widget.innerHTML = html;
            console.log('AIChatCore.render: innerHTML set, checking for MCP elements:', this.widget.querySelector('#ai-chat-mcp-add'), this.widget.querySelector('#ai-chat-mcp-back'));
            this.initModelDropdown();
            AIChatAttachments.render(this.widget, this.activeTabId, this.tabs);
            this.scrollActiveTabToBottom();
            this.highlightCode();
            AIChatZoom.applyAllZoneZooms(this.widget);
        },

        highlightCode: function() {
            var messagesContainer = this.widget.querySelector('.ai-chat-messages[data-tab-id="' + this.activeTabId + '"]');
            if (messagesContainer && window.AIChatHighlight) {
                AIChatHighlight.highlightCodeBlocks(messagesContainer);
            }
        },

        scrollActiveTabToBottom: function() {
            var messagesContainer = this.widget.querySelector('.ai-chat-messages[data-tab-id="' + this.activeTabId + '"]');
            AIChatMessages.scrollToBottom(messagesContainer);
        },

        initModelDropdown: function() {
            var activePanel = this.widget.querySelector('.ai-chat-tab-panel.active');
            if (!activePanel) return;
            var select = activePanel.querySelector('.ai-chat-model-select');
            if (select && window.ZatoDropdown) {
                var existingDropdown = activePanel.querySelector('.zato-dropdown');
                if (existingDropdown) {
                    existingDropdown.parentNode.removeChild(existingDropdown);
                }
                ZatoDropdown.init(select);
            }
        },

        bindEvents: function() {
            var self = this;

            this.widget.addEventListener('click', function(e) {
                self.handleClick(e);
            });

            this.widget.addEventListener('mouseenter', function(e) {
                if (e.target.id === 'ai-chat-menu-button' || e.target.closest('#ai-chat-menu-button')) {
                    AIChatSettings.showMenu(self.widget);
                }
            }, true);

            this.widget.addEventListener('mousedown', function(e) {
                AIChatDrag.handleMouseDown(e, self.widget, self.isMinimized, self.zoomScale, function() {
                    self.toggleMinimize();
                });
            });

            this.widget.addEventListener('dblclick', function(e) {
                var header = e.target.closest('#ai-chat-header');
                if (header && !e.target.closest('.ai-chat-header-button')) {
                    self.toggleMaximize();
                }
            });

            this.widget.addEventListener('dragover', function(e) {
                e.preventDefault();
                e.stopPropagation();
                self.widget.classList.add('drag-over');
            });

            this.widget.addEventListener('dragleave', function(e) {
                e.preventDefault();
                e.stopPropagation();
                self.widget.classList.remove('drag-over');
            });

            this.widget.addEventListener('drop', function(e) {
                e.preventDefault();
                e.stopPropagation();
                self.widget.classList.remove('drag-over');
                var files = e.dataTransfer.files;
                if (files && files.length > 0) {
                    for (var i = 0; i < files.length; i++) {
                        AIChatAttachments.addFile(files[i], self.activeTabId, function() {
                            AIChatAttachments.render(self.widget, self.activeTabId, self.tabs);
                        });
                    }
                }
            });

            document.addEventListener('mousemove', function(e) {
                AIChatDrag.handleMouseMove(e, self.widget, self.zoomScale);
            });

            document.addEventListener('mouseup', function(e) {
                var result = AIChatDrag.handleMouseUp(self.widget, self.tabs, function() {
                    self.saveState();
                }, function() {
                    self.render();
                });
                if (result.tabsChanged) {
                    self.tabs = result.tabs;
                    self.saveState();
                    self.render();
                }
            });

            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    if (AIChatPreview.closeTop()) {
                        e.preventDefault();
                        return;
                    }
                }

                if (e.key === 'Enter' && !e.shiftKey) {
                    var mcpEndpoint = e.target.closest('#ai-chat-mcp-endpoint');
                    if (mcpEndpoint) {
                        e.preventDefault();
                        var saveBtn = self.widget.querySelector('#ai-chat-mcp-save');
                        if (saveBtn) {
                            saveBtn.click();
                        }
                        return;
                    }
                }

                if (e.key === 'Backspace') {
                    var isInput = e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable;
                    if (!isInput) {
                        var backBtn = self.widget.querySelector('.ai-chat-config-back');
                        if (backBtn) {
                            e.preventDefault();
                            backBtn.click();
                        }
                    }
                }

                AIChatInput.handleKeyDown(e, function(tabId) {
                    self.sendMessage(tabId);
                });
            });

            this.widget.addEventListener('paste', function(e) {
                var inputElement = e.target.closest('.ai-chat-input');
                if (!inputElement) return;
                var handled = AIChatInput.handlePaste(e, function(attachment, tabId) {
                    AIChatAttachments.render(self.widget, tabId, self.tabs);
                });
            });

            document.addEventListener('input', function(e) {
                AIChatInput.handleInput(e);
            });

            document.addEventListener('keyup', function(e) {
                AIChatInput.handleKeyUp(e);
            });

            this.widget.addEventListener('contextmenu', function(e) {
                var tabElement = e.target.closest('.ai-chat-tab');
                if (tabElement) {
                    e.preventDefault();
                    var tabId = tabElement.getAttribute('data-tab-id');
                    AIChatContextMenu.show(e.clientX, e.clientY, tabId, function(tid) {
                        AIChatContextMenu.renameTab(self.tabs, tid, function() {
                            self.saveState();
                        }, function() {
                            self.render();
                        });
                    });
                }
            });

            this.widget.addEventListener('wheel', function(e) {
                if (e.ctrlKey) {
                    e.preventDefault();
                }
                self.zoomScale = AIChatZoom.handleWheel(self.widget, e, self.zoomScale);
                AIChatState.saveZoom(self.zoomScale);
            }, { passive: false, capture: true });

            document.addEventListener('click', function(e) {
                AIChatContextMenu.hide();
                AIChatSettings.hideMenu();
                AIChatOptionsMenu.hide(self.widget);
            });

            this.widget.addEventListener('change', function(e) {
                var target = e.target;
                if (target.classList.contains('ai-chat-model-select')) {
                    var tabId = target.getAttribute('data-tab-id');
                    var modelId = target.value;
                    AIChatTabState.setModel(tabId, modelId);
                    for (var i = 0; i < self.tabs.length; i++) {
                        if (self.tabs[i].id === tabId) {
                            AIChatTabState.saveToTab(self.tabs[i]);
                            AIChatState.saveTabs(self.tabs);
                            break;
                        }
                    }
                }
            });
        },

        handleClick: function(e) {
            var target = e.target;
            var self = this;

            console.log('AIChatCore.handleClick: target=', target, 'target.id=', target.id, 'target.className=', target.className, 'configMode=', this.configMode);

            if (target.id === 'ai-chat-minimize') {
                this.toggleMinimize();
                return;
            }

            if (target.id === 'ai-chat-maximize') {
                this.toggleMaximize();
                return;
            }

            var settingsMenuItem = target.closest('.ai-chat-settings-menu-item');
            if (settingsMenuItem) {
                var action = settingsMenuItem.getAttribute('data-action');
                AIChatSettings.handleAction(action, null, {
                    onChangeProvider: function(hadKey) {
                        self.hadKeyOnEntry = hadKey;
                        self.cameFromChat = true;
                        self.needsConfig = true;
                        self.configMode = 'providers';
                        self.render();
                    },
                    onManageKeys: function(hadKey) {
                        self.hadKeyOnEntry = hadKey;
                        self.cameFromChat = true;
                        self.needsConfig = true;
                        self.configMode = 'manage-keys';
                        self.render();
                    }
                });
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
                AIChatOptionsMenu.toggle(this.widget, this.activeTabId, optionsBtn);
                e.stopPropagation();
                return;
            }

            var optionsMenuItem = target.closest('.ai-chat-options-menu-item');
            if (optionsMenuItem) {
                var action = optionsMenuItem.getAttribute('data-action');
                AIChatOptionsMenu.hide(this.widget);
                AIChatOptionsMenu.handleAction(action, {
                    onManageKeys: function() {
                        self.cameFromChat = true;
                        self.hadKeyOnEntry = AIChatConfig.hasAnyKey();
                        self.needsConfig = true;
                        self.configMode = 'manage-keys';
                        self.render();
                    },
                    onAddFiles: function() {
                        AIChatOptionsMenu.showFileDialog(self.activeTabId, function() {
                            AIChatAttachments.render(self.widget, self.activeTabId, self.tabs);
                        });
                    },
                    onManageMCP: function() {
                        self.cameFromChat = true;
                        self.needsConfig = true;
                        self.configMode = 'manage-mcp';
                        AIChatMCP.loadServers(function() {
                            self.render();
                        });
                    }
                });
                e.stopPropagation();
                return;
            }


            if (target.classList.contains('ai-chat-message-copy')) {
                var messageEl = target.closest('.ai-chat-message');
                if (messageEl) {
                    var contentEl = messageEl.querySelector('.ai-chat-message-content');
                    if (contentEl) {
                        var text = contentEl.textContent || contentEl.innerText;
                        navigator.clipboard.writeText(text).then(function() {
                            target.textContent = 'Copied';
                            setTimeout(function() {
                                target.textContent = 'Copy';
                            }, 1000);
                        });
                    }
                }
                return;
            }

            if (target.classList.contains('ai-chat-attachment-remove') || target.closest('.ai-chat-attachment-remove')) {
                var removeBtn = target.classList.contains('ai-chat-attachment-remove') ? target : target.closest('.ai-chat-attachment-remove');
                var attachmentId = removeBtn.getAttribute('data-attachment-id');
                var tabPanel = removeBtn.closest('.ai-chat-tab-panel');
                var tabId = tabPanel ? tabPanel.getAttribute('data-tab-id') : this.activeTabId;
                AIChatTabState.removeAttachment(tabId, attachmentId);
                AIChatAttachments.render(this.widget, tabId, this.tabs);
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
                        AIChatPreview.show(attachments[i]);
                        break;
                    }
                }
                return;
            }

            var providerEl = target.closest('.ai-chat-config-provider');
            if (providerEl) {
                var providerId = providerEl.getAttribute('data-provider-id');
                this.needsConfig = true;
                this.configMode = 'key-input';
                AIChatSettings.showKeyInput(this.widget, providerId, function() {
                    self.render();
                });
                return;
            }

            var mcpBack = target.closest('#ai-chat-mcp-back');
            if (mcpBack) {
                console.log('AIChatCore.handleClick: mcp-back clicked, target=', target, 'mcpBack=', mcpBack);
                this.needsConfig = false;
                this.configMode = 'providers';
                this.render();
                return;
            }

            var mcpDetailBack = target.closest('#ai-chat-mcp-detail-back');
            if (mcpDetailBack) {
                console.log('AIChatCore.handleClick: mcp-detail-back clicked');
                AIChatMCP.selectedServer = null;
                AIChatMCP.selectedServerTools = [];
                this.configMode = 'manage-mcp';
                this.render();
                return;
            }

            var mcpEditBack = target.closest('#ai-chat-mcp-edit-back');
            if (mcpEditBack) {
                console.log('AIChatCore.handleClick: mcp-edit-back clicked');
                AIChatMCP.selectedServer = null;
                this.configMode = 'manage-mcp';
                this.render();
                return;
            }

            var backEl = target.closest('.ai-chat-config-back');
            if (backEl) {
                AIChatSettings.handleBackClick(this.configMode, this.cameFromChat, this.hadKeyOnEntry, {
                    onReturnToChat: function() {
                        self.cameFromChat = false;
                        self.needsConfig = false;
                        self.configMode = 'providers';
                        AIChatConfig.selectedProvider = null;
                        self.render();
                    },
                    onShowProviders: function() {
                        self.needsConfig = true;
                        self.configMode = 'providers';
                        AIChatConfig.selectedProvider = null;
                        self.render();
                    }
                });
                return;
            }

            var mcpAdd = target.closest('#ai-chat-mcp-add');
            if (mcpAdd) {
                console.log('AIChatCore.handleClick: mcp-add clicked, target=', target, 'mcpAdd=', mcpAdd);
                this.configMode = 'add-mcp';
                this.render();
                return;
            }

            var mcpAddBack = target.closest('#ai-chat-mcp-add-back');
            if (mcpAddBack) {
                console.log('AIChatCore.handleClick: mcp-add-back clicked, target=', target, 'mcpAddBack=', mcpAddBack);
                this.configMode = 'manage-mcp';
                this.render();
                return;
            }

            var mcpSave = target.closest('#ai-chat-mcp-save');
            if (mcpSave) {
                console.log('AIChatCore.handleClick: mcp-save clicked, target=', target, 'mcpSave=', mcpSave);
                var endpointInput = this.widget.querySelector('#ai-chat-mcp-endpoint');

                var endpoint = endpointInput ? endpointInput.value.trim() : '';

                if (!endpoint) {
                    console.log('AIChatCore.handleClick: mcp-save missing endpoint');
                    return;
                }

                var name = AIChatMCP.extractNameFromUrl(endpoint);
                var serverId = AIChatMCP.generateServerId(name);
                var serverConfig = {
                    id: serverId,
                    type: serverId,
                    name: name,
                    endpoint: endpoint,
                    auth_type: 'none',
                    auth_data: {},
                    enabled: true
                };

                console.log('AIChatCore.handleClick: mcp-save adding server', serverConfig);
                AIChatMCP.addServer(serverConfig, function() {
                    self.configMode = 'manage-mcp';
                    self.render();
                });
                return;
            }

            var mcpRemoveBtn = target.closest('.ai-chat-mcp-remove-btn');
            if (mcpRemoveBtn) {
                ZatoConfirmButton.handleClick(mcpRemoveBtn, function(serverId) {
                    console.log('AIChatCore.handleClick: mcp-remove confirmed, serverId=', serverId);
                    AIChatMCP.removeServer(serverId, function() {
                        self.render();
                    });
                });
                return;
            }

            if (target.classList.contains('ai-chat-mcp-enabled')) {
                var serverEl = target.closest('.ai-chat-mcp-server-row');
                var serverId = serverEl ? serverEl.getAttribute('data-server-id') : null;
                if (serverId) {
                    var enabled = target.checked;
                    console.log('AIChatCore.handleClick: mcp-enabled toggled, serverId=', serverId, 'enabled=', enabled);
                    AIChatMCP.updateServer(serverId, { enabled: enabled }, function() {
                        self.render();
                    });
                }
                return;
            }

            var mcpServerNameLink = target.closest('.ai-chat-mcp-server-name-link');
            if (mcpServerNameLink) {
                var serverId = mcpServerNameLink.getAttribute('data-server-id');
                console.log('AIChatCore.handleClick: mcp-server-name clicked, serverId=', serverId);
                AIChatMCP.selectedServer = AIChatMCP.getServerById(serverId);
                AIChatMCP.loadingTools = true;
                AIChatMCP.selectedServerTools = [];
                this.configMode = 'mcp-detail';
                this.render();
                AIChatMCP.loadToolsForServer(serverId, function() {
                    self.render();
                });
                return;
            }

            var mcpEditBtn = target.closest('.ai-chat-mcp-edit-btn');
            if (mcpEditBtn) {
                var serverId = mcpEditBtn.getAttribute('data-item-id');
                console.log('AIChatCore.handleClick: mcp-edit clicked, serverId=', serverId);
                AIChatMCP.selectedServer = AIChatMCP.getServerById(serverId);
                this.configMode = 'edit-mcp';
                this.render();
                return;
            }

            var mcpEditSave = target.closest('#ai-chat-mcp-edit-save');
            if (mcpEditSave) {
                var serverId = mcpEditSave.getAttribute('data-server-id');
                var endpointInput = this.widget.querySelector('#ai-chat-mcp-edit-endpoint');
                var newEndpoint = endpointInput ? endpointInput.value.trim() : '';

                if (!newEndpoint) {
                    console.log('AIChatCore.handleClick: mcp-edit-save missing endpoint');
                    return;
                }

                var newName = AIChatMCP.extractNameFromUrl(newEndpoint);
                console.log('AIChatCore.handleClick: mcp-edit-save updating server', serverId, 'endpoint=', newEndpoint, 'name=', newName);

                AIChatMCP.updateServer(serverId, { endpoint: newEndpoint, name: newName }, function() {
                    AIChatMCP.selectedServer = null;
                    self.configMode = 'manage-mcp';
                    self.render();
                });
                return;
            }

            if (target.classList.contains('ai-chat-config-save-button')) {
                var providerId = target.getAttribute('data-provider-id');
                AIChatSettings.saveApiKey(this.widget, providerId, function() {
                    self.needsConfig = false;
                    self.configMode = 'providers';
                    AIChatSettings.showConfigSuccess(self.widget, function() {
                        self.render();
                    });
                });
                return;
            }

            var configKeyRemove = target.closest('.ai-chat-config-key-remove');
            if (configKeyRemove) {
                ZatoConfirmButton.handleClick(configKeyRemove, function(providerId) {
                    console.log('AIChatCore.handleClick: config-key-remove confirmed, providerId=', providerId);
                    AIChatSettings.removeApiKey(providerId, {
                        onNoKeysLeft: function() {
                            self.needsConfig = true;
                            self.configMode = 'providers';
                            self.cameFromChat = false;
                            self.hadKeyOnEntry = false;
                        },
                        onSuccess: function() {
                            self.render();
                        }
                    });
                });
                return;
            }

            var configKeyAdd = target.closest('.ai-chat-config-key-add');
            if (configKeyAdd) {
                var providerId = configKeyAdd.getAttribute('data-item-id');
                this.needsConfig = true;
                this.configMode = 'key-input';
                AIChatConfig.selectedProvider = providerId;
                this.render();
                return;
            }

            var configKeyEdit = target.closest('.ai-chat-config-key-edit');
            if (configKeyEdit) {
                var providerId = configKeyEdit.getAttribute('data-item-id');
                this.needsConfig = true;
                this.configMode = 'key-input';
                AIChatConfig.selectedProvider = providerId;
                this.render();
                return;
            }
        },

        toggleMinimize: function() {
            var self = this;

            if (this.isMaximized && !this.isMinimized) {
                if (this.preMaximizeState) {
                    this.widget.style.left = this.preMaximizeState.left;
                    this.widget.style.top = this.preMaximizeState.top;
                    this.widget.style.width = this.preMaximizeState.width;
                    this.widget.style.height = this.preMaximizeState.height;
                }
                if (this.preMaximizeZoomScale) {
                    this.zoomScale = this.preMaximizeZoomScale;
                    this.widget.style.transform = 'scale(' + this.zoomScale + ')';
                }
                this.widget.classList.remove('maximized');
                document.documentElement.classList.remove('ai-chat-maximized');
                this.isMaximized = false;
            }

            var result = AIChatWidget.toggleMinimize(
                this.widget,
                this.isMinimized,
                this.preMinimizePosition,
                this.zoomScale,
                function() { self.saveState(); }
            );
            this.isMinimized = result.isMinimized;
            this.preMinimizePosition = result.preMinimizePosition;
            this.zoomScale = result.zoomScale;
            this.preMinimizeZoom = result.preMinimizeZoom;
            this.saveState();
            this.render();
        },

        toggleMaximize: function() {
            if (this.isMinimized) {
                this.toggleMinimize();
            }

            if (this.isMaximized) {
                if (this.preMaximizeState) {
                    this.widget.style.left = this.preMaximizeState.left;
                    this.widget.style.top = this.preMaximizeState.top;
                    this.widget.style.width = this.preMaximizeState.width;
                    this.widget.style.height = this.preMaximizeState.height;
                }
                if (this.preMaximizeZoomScale) {
                    this.zoomScale = this.preMaximizeZoomScale;
                    this.widget.style.transform = 'scale(' + this.zoomScale + ')';
                }
                this.widget.classList.remove('maximized');
                document.documentElement.classList.remove('ai-chat-maximized');
                this.isMaximized = false;
            } else {
                this.preMaximizeState = {
                    left: this.widget.style.left,
                    top: this.widget.style.top,
                    width: this.widget.style.width,
                    height: this.widget.style.height
                };
                this.preMaximizeZoomScale = this.zoomScale;
                this.zoomScale = 1;
                this.widget.classList.add('maximized');
                document.documentElement.classList.add('ai-chat-maximized');
                this.isMaximized = true;
            }
            this.saveState();
            this.render();
            this.focusInput(this.activeTabId);
        },

        addTab: function() {
            var newTab = AIChatTabs.addTab(this.tabs);
            AIChatTabState.initTab(newTab.id);
            this.activeTabId = newTab.id;
            this.saveState();
            this.render();
            this.focusInput(newTab.id);
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
            AIChatAttachments.render(this.widget, tabId, this.tabs);
            this.focusInput(tabId);
        },

        focusInput: function(tabId) {
            var input = this.widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
            if (input) {
                input.focus();
            }
        },

        sendMessage: function(tabId) {
            var self = this;

            var input = this.widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
            if (!input) return;

            var message = AIChatInput.getMessageText(input);
            if (!message) return;

            var tab = AIChatTabs.getTabById(this.tabs, tabId);
            if (!tab) return;

            if (AIChatMessages.isStreaming(tabId)) {
                console.debug('AIChat.sendMessage: already streaming for tab:', tabId);
                return;
            }

            AIChatMessages.addMessage(tab, 'user', message);

            var model = AIChatTabState.getModel(tabId);
            if (!model) {
                var models = AIChatConfig.getModelsForConfiguredProviders();
                for (var i = 0; i < models.length; i++) {
                    if (!models[i].disabled) {
                        model = models[i].id;
                        break;
                    }
                }
            }

            if (!model) {
                AIChatMessages.addMessage(tab, 'system', 'No model selected');
                this.saveState();
                this.render();
                return;
            }

            var apiMessages = this.buildApiMessages(tab);

            AIChatMessages.startStreamingMessage(tab, tabId);

            this.saveState();
            this.render();

            var newInput = this.widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
            if (newInput) {
                newInput.focus();
            }

            AIChatAPI.streamMessage(tabId, model, apiMessages, {
                onChunk: function(text) {
                    AIChatMessages.appendToStreamingMessage(tabId, text);
                    self.updateStreamingMessage(tabId);
                },
                onComplete: function(inputTokens, outputTokens) {
                    console.log('onComplete: inputTokens=' + inputTokens + ' outputTokens=' + outputTokens);
                    if (inputTokens > 0) {
                        AIChatTabState.addTokensOut(tabId, inputTokens);
                        console.log('after addTokensOut: ' + AIChatTabState.getTokensOut(tabId));
                    }
                    if (outputTokens > 0) {
                        AIChatTabState.addTokensIn(tabId, outputTokens);
                        console.log('after addTokensIn: ' + AIChatTabState.getTokensIn(tabId));
                    }

                    AIChatMessages.finishStreamingMessage(tab, tabId);
                    self.saveState();
                    self.render();

                    var input = self.widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
                    if (input) {
                        input.focus();
                    }
                },
                onError: function(error) {
                    AIChatMessages.cancelStreamingMessage(tab, tabId);
                    AIChatMessages.addMessage(tab, 'system', 'Error: ' + error);
                    self.saveState();
                    self.render();
                }
            });
        },

        buildApiMessages: function(tab) {
            var out = [];

            for (var i = 0; i < tab.messages.length; i++) {
                var msg = tab.messages[i];
                if (msg.role === 'user' || msg.role === 'assistant') {
                    if (!msg.streaming) {
                        out.push({
                            role: msg.role,
                            content: msg.content
                        });
                    }
                }
            }

            return out;
        },

        updateStreamingMessage: function(tabId) {
            var messagesContainer = this.widget.querySelector('.ai-chat-messages[data-tab-id="' + tabId + '"]');
            if (!messagesContainer) return;

            var streamingEl = messagesContainer.querySelector('.ai-chat-message.streaming');
            if (!streamingEl) return;

            var contentEl = streamingEl.querySelector('.ai-chat-message-content');
            if (!contentEl) return;

            var content = AIChatMessages.getStreamingContent(tabId);
            var html = marked.parse(content);
            if (typeof markedEmoji !== 'undefined') {
                if (markedEmoji.convertAsciiEmoticons) {
                    html = markedEmoji.convertAsciiEmoticons(html);
                }
                if (markedEmoji.wrapUnicodeEmojis) {
                    html = markedEmoji.wrapUnicodeEmojis(html);
                }
            }
            contentEl.innerHTML = html;

            AIChatMessages.scrollToBottom(messagesContainer);
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
