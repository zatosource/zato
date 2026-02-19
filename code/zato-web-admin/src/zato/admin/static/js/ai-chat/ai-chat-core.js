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
        cameFromManageKeys: false,

        ideEnabled: true,

        init: function() {
            var self = this;

            if (typeof markedEmoji !== 'undefined' && markedEmoji.markedEmoji) {
                marked.use(markedEmoji.markedEmoji());
            }

            AIChatConfig.init();
            AIChatMCP.init();
            AIChatZoom.init();
            if (window.AIChatIDEIntegration) {
                AIChatIDEIntegration.init(null);
                this.ideEnabled = AIChatIDEIntegration.isEnabled();
            }
            AIChatTabs.loadClosedHistory();
            this.loadState();
            this.widget = AIChatWidget.create(this.isMinimized, this.zoomScale);
            if (this.isMaximized) {
                this.widget.classList.add('maximized');
                document.documentElement.classList.add('ai-chat-maximized');
            }
            AIChatEvents.bind(this.widget, this);

            var savedConfigMode = AIChatState.loadConfigMode();
            var modelsLoaded = false;
            var keysChecked = false;
            var hasKeys = false;

            function tryRender() {
                if (!modelsLoaded || !keysChecked) {
                    return;
                }
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
                        self.focusInputIfNotMinimized();
                    });
                } else {
                    self.render();
                    self.focusInputIfNotMinimized();
                }
            }

            AIChatConfig.loadModels(function() {
                modelsLoaded = true;
                tryRender();
            });

            AIChatConfig.checkConfiguredKeys(function(result) {
                hasKeys = result;
                keysChecked = true;
                tryRender();
            });

            window.addEventListener('focus', function() {
                self.focusInputIfNotMinimized();
            });

        },

        focusInputIfNotMinimized: function() {
            if (this.isMinimized || this.needsConfig) {
                return;
            }
            AIChatTabActions.focusInput(this.widget, this.activeTabId);
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
            console.log('[AI-CHAT-RENDER] render() called');
            console.log('[AI-CHAT-RENDER] tabs.length=' + this.tabs.length + ', activeTabId=' + this.activeTabId);
            console.log('[AI-CHAT-RENDER] needsConfig=' + this.needsConfig + ', ideEnabled=' + this.ideEnabled + ', isMinimized=' + this.isMinimized);
            var existingPanels = this.widget ? this.widget.querySelectorAll('.ai-chat-tab-panel') : [];
            console.log('[AI-CHAT-RENDER] existing panels before render: ' + existingPanels.length);
            var existingInputs = this.widget ? this.widget.querySelectorAll('.ai-chat-input') : [];
            console.log('[AI-CHAT-RENDER] existing inputs before render: ' + existingInputs.length);

            if (this.needsConfig && this.configMode && this.configMode !== 'providers') {
                AIChatState.saveConfigMode(this.configMode);
            } else {
                AIChatState.saveConfigMode(null);
            }

            var html = AIChatRender.buildHeaderHtml(this.isMinimized, this.isMaximized);

            if (this.ideEnabled && !this.needsConfig && !this.isMinimized && window.AIChatIDEIntegration) {
                this.widget.classList.add('with-ide');
                html += this.buildSplitBodyHtml();
            } else {
                this.widget.classList.remove('with-ide');
                if (!this.needsConfig) {
                    html += AIChatRender.buildTabsHtml(this.tabs, this.activeTabId);
                }
                html += AIChatRender.buildBodyHtml(this.tabs, this.activeTabId, this.needsConfig, this.configMode, AIChatConfig.selectedProvider, this.cameFromChat, this.hadKeyOnEntry);
            }

            html += AIChatRender.buildResizeHandlesHtml();

            this.widget.innerHTML = html;

            var panelsAfterHtml = this.widget.querySelectorAll('.ai-chat-tab-panel');
            console.log('[AI-CHAT-RENDER] panels after innerHTML assignment: ' + panelsAfterHtml.length);
            var inputsAfterHtml = this.widget.querySelectorAll('.ai-chat-input');
            console.log('[AI-CHAT-RENDER] inputs after innerHTML assignment: ' + inputsAfterHtml.length);

            if (this.ideEnabled && !this.needsConfig && !this.isMinimized && window.AIChatIDEIntegration) {
                this.initIDESplit();
                var panelsAfterIDE = this.widget.querySelectorAll('.ai-chat-tab-panel');
                console.log('[AI-CHAT-RENDER] panels after initIDESplit: ' + panelsAfterIDE.length);
                var inputsAfterIDE = this.widget.querySelectorAll('.ai-chat-input');
                console.log('[AI-CHAT-RENDER] inputs after initIDESplit: ' + inputsAfterIDE.length);
            }

            this.bindTabsEvents();
            this.initModelDropdown();
            this.initContextBarTooltip();
            this.initConvertDropdown();
            AIChatAttachments.render(this.widget, this.activeTabId, this.tabs);
            this.scrollActiveTabToBottom();
            this.highlightCode();
            this.scrollEditDiffsToFirstHunk();
            AIChatZoom.applyAllZoneZooms(this.widget);
            this.restoreInputContent();

            var input = this.widget.querySelector('#ai-chat-mcp-endpoint') ||
                        this.widget.querySelector('#ai-chat-mcp-edit-endpoint') ||
                        this.widget.querySelector('.ai-chat-config-api-key-input');
            if (input) {
                input.focus();
            }
        },

        buildSplitBodyHtml: function() {
            var html = '<div class="ai-chat-body">';
            html += '<div id="ai-chat-split-wrapper" class="ai-chat-split-wrapper"></div>';
            html += '</div>';
            return html;
        },

        initIDESplit: function() {
            console.log('[AI-CHAT-RENDER] initIDESplit called');
            var self = this;

            if (!window.ZatoIDESplit || !window.ZatoIDE) {
                console.log('[AI-CHAT-RENDER] initIDESplit: ZatoIDESplit or ZatoIDE not available');
                return;
            }

            var splitInstance = ZatoIDESplit.create('ai-chat-split-wrapper', {
                onResize: function() {
                }
            });

            if (!splitInstance) {
                return;
            }

            var leftPanel = ZatoIDESplit.getLeftPanel(splitInstance);
            if (leftPanel) {
                leftPanel.id = 'ai-chat-ide-container';
                ZatoIDE.create('ai-chat-ide-container', {
                    theme: 'dark',
                    language: 'python'
                });
            }

            var rightPanel = ZatoIDESplit.getRightPanel(splitInstance);
            if (rightPanel) {
                console.log('[AI-CHAT-RENDER] initIDESplit: building right panel content');
                var chatTabsHtml = AIChatRender.buildTabsHtml(this.tabs, this.activeTabId);
                var chatBodyHtml = this.buildChatPanelBodyHtml();
                rightPanel.innerHTML = chatTabsHtml + chatBodyHtml;
                var panelsInRightPanel = rightPanel.querySelectorAll('.ai-chat-tab-panel');
                console.log('[AI-CHAT-RENDER] initIDESplit: panels in right panel: ' + panelsInRightPanel.length);
                this.bindTabsEvents(rightPanel);
            }
        },

        bindTabsEvents: function(container) {
            var self = this;
            container = container || this.widget;
            var tabsContainer = container.querySelector('.zato-tabs-container');
            if (!tabsContainer || !window.ZatoTabsEvents) {
                return;
            }
            var parentEl = tabsContainer.parentElement;
            if (!parentEl) {
                return;
            }
            var instance = {
                tabs: this.tabs,
                activeTabId: this.activeTabId,
                theme: 'dark'
            };
            var callbacks = {
                onTabChange: function(tab) {
                    self.activeTabId = tab.id;
                },
                onTabAdd: function(newTab) {
                    AIChatTabState.initTab(newTab.id);
                    var currentTab = AIChatTabs.getTabById(self.tabs, self.activeTabId);
                    if (currentTab && currentTab.model) {
                        newTab.model = currentTab.model;
                        AIChatTabState.setModel(newTab.id, currentTab.model);
                    }
                },
                createTabData: function(tabNumber) {
                    return { title: 'Chat ' + tabNumber };
                },
                onSave: function() {
                    self.saveState();
                },
                onRender: function() {
                    self.render();
                    AIChatTabActions.focusInput(self.widget, self.activeTabId);
                },
                onAddToClosedHistory: function(tab) {
                    AIChatTabs.addToClosedHistory(tab);
                },
                onFlushClosedHistory: function() {
                    AIChatTabs.flushClosedHistory();
                },
                onReopenClosedTabs: function() {
                    return AIChatTabs.reopenClosedTabs(self.tabs);
                },
                onClearMessages: function(tabId, messages) {
                    AIChatTabs.clearedMessagesBuffer[tabId] = messages;
                },
                onUndoClearMessages: function(tabId) {
                    var tab = AIChatTabs.getTabById(self.tabs, tabId);
                    if (tab && AIChatTabs.clearedMessagesBuffer[tabId]) {
                        tab.messages = AIChatTabs.clearedMessagesBuffer[tabId];
                        delete AIChatTabs.clearedMessagesBuffer[tabId];
                        return true;
                    }
                    return false;
                }
            };
            ZatoTabsEvents.bind(parentEl, instance, callbacks);
        },


        buildChatPanelBodyHtml: function() {
            console.log('[AI-CHAT-RENDER] buildChatPanelBodyHtml called, tabs.length=' + this.tabs.length);
            var html = '';
            for (var i = 0; i < this.tabs.length; i++) {
                var tab = this.tabs[i];
                var activeClass = tab.id === this.activeTabId ? ' active' : '';
                console.log('[AI-CHAT-RENDER] buildChatPanelBodyHtml: creating panel for tab ' + tab.id);
                html += '<div class="ai-chat-tab-panel' + activeClass + '" data-tab-id="' + tab.id + '">';
                html += AIChatRender.buildMessagesHtml(tab, false, null, null, false, false);
                html += AIChatRender.buildInputAreaHtml(tab);
                html += '</div>';
            }
            return html;
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
                select.style.display = '';
                ZatoDropdown.init(select, {theme: 'dark', tooltip: 'Choose model'});
            }
        },

        initConvertDropdown: function() {
            var activePanel = this.widget.querySelector('.ai-chat-tab-panel.active');
            if (!activePanel) return;
            var container = activePanel.querySelector('.ai-chat-convert-container');
            if (container && window.AIChatConvert) {
                container.innerHTML = '';
                AIChatConvert.init(container);
            }
        },

        initContextBarTooltip: function() {
        },

        restoreInputContent: function() {
            var inputEl = this.widget.querySelector('.ai-chat-input[data-tab-id="' + this.activeTabId + '"]');
            if (inputEl && window.AIChatInput) {
                AIChatInput.restoreInputFromStorage(inputEl);
            }
        },

        scrollEditDiffsToFirstHunk: function() {
            if (!window.AIChatDiff) return;
            var messagesContainer = this.widget.querySelector('.ai-chat-messages[data-tab-id="' + this.activeTabId + '"]');
            if (!messagesContainer) return;
            var lastMessage = messagesContainer.querySelector('.ai-chat-message:last-child');
            if (!lastMessage) return;
            var containers = lastMessage.querySelectorAll('.ai-diff-container');
            console.log('[SCROLL-HUNK] found containers:', containers.length);
            for (var i = 0; i < containers.length; i++) {
                var container = containers[i];
                var hunkCount = parseInt(container.getAttribute('data-hunk-count') || '0', 10);
                var diffContent = container.querySelector('.ai-diff-content');
                if (diffContent) {
                    diffContent.scrollTop = 0;
                }
                if (hunkCount > 0) {
                    AIChatDiff.navigateToHunk(container, 0);
                }
            }
            var firstWrapper = lastMessage.querySelector('.ai-diff-wrapper');
            if (firstWrapper) {
                var wrapperRect = firstWrapper.getBoundingClientRect();
                var containerRect = messagesContainer.getBoundingClientRect();
                var scrollOffset = wrapperRect.top - containerRect.top + messagesContainer.scrollTop - 10;
                messagesContainer.scrollTop = Math.max(0, scrollOffset);
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

