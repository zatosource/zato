(function() {
    'use strict';

    var AIChat = {
        widget: null,
        tabs: [],
        activeTabId: null,
        isMinimized: false,
        preMinimizePosition: null,
        preMinimizeZoom: 1.0,
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
            this.loadState();
            this.widget = AIChatWidget.create(this.isMinimized, this.zoomScale);
            this.bindEvents();

            AIChatConfig.checkConfiguredKeys(function(hasKeys) {
                self.needsConfig = !hasKeys;
                self.render();
                console.debug('AIChat.init: initialization complete, needsConfig:', self.needsConfig);
            });
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
            this.preMinimizePosition = AIChatState.loadPreMinimizePosition();
            this.zoomScale = AIChatState.loadZoom();
        },

        saveState: function() {
            for (var i = 0; i < this.tabs.length; i++) {
                AIChatTabState.saveToTab(this.tabs[i]);
            }
            AIChatState.saveTabs(this.tabs);
            AIChatState.saveActiveTabId(this.activeTabId);
            AIChatState.saveMinimized(this.isMinimized);
        },

        render: function() {
            var html = AIChatRender.buildHeaderHtml(this.isMinimized);
            if (!this.needsConfig) {
                html += AIChatRender.buildTabsHtml(this.tabs, this.activeTabId);
            }
            html += AIChatRender.buildBodyHtml(this.tabs, this.activeTabId, this.needsConfig, this.configMode, AIChatConfig.selectedProvider, this.cameFromChat, this.hadKeyOnEntry);
            html += AIChatRender.buildResizeHandlesHtml();

            this.widget.innerHTML = html;
            this.initModelDropdown();
            AIChatAttachments.render(this.widget, this.activeTabId, this.tabs);
            this.scrollActiveTabToBottom();
            this.highlightCode();
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
                self.zoomScale = AIChatZoom.handleWheel(self.widget, e, self.zoomScale);
                AIChatState.saveZoom(self.zoomScale);
            }, { passive: false });

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

            if (target.id === 'ai-chat-minimize') {
                this.toggleMinimize();
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

            if (target.classList.contains('ai-chat-config-key-remove')) {
                var providerId = target.getAttribute('data-provider-id');
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
                return;
            }

            if (target.classList.contains('ai-chat-config-key-add')) {
                var providerId = target.getAttribute('data-provider-id');
                this.needsConfig = true;
                this.configMode = 'key-input';
                AIChatSettings.showKeyInput(this.widget, providerId, function() {
                    self.render();
                });
                return;
            }
        },

        toggleMinimize: function() {
            var self = this;
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
            AIChatAttachments.render(this.widget, tabId, this.tabs);
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
                    if (inputTokens > 0) {
                        AIChatTabState.addTokensOut(tabId, inputTokens);
                    }
                    if (outputTokens > 0) {
                        AIChatTabState.addTokensIn(tabId, outputTokens);
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
            contentEl.innerHTML = marked.parse(content);

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
