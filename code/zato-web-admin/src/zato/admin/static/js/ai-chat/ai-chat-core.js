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
            var self = this;

            if (typeof markedEmoji !== 'undefined' && markedEmoji.markedEmoji) {
                marked.use(markedEmoji.markedEmoji());
            }

            AIChatConfig.init();
            AIChatMCP.init();
            AIChatZoom.init();
            this.loadState();
            this.widget = AIChatWidget.create(this.isMinimized, this.zoomScale);
            if (this.isMaximized) {
                this.widget.classList.add('maximized');
                document.documentElement.classList.add('ai-chat-maximized');
            }
            AIChatEvents.bind(this.widget, this);

            var savedConfigMode = AIChatState.loadConfigMode();

            AIChatConfig.checkConfiguredKeys(function(hasKeys) {
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
            this.initModelDropdown();
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
                ZatoDropdown.init(select);
            }
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

