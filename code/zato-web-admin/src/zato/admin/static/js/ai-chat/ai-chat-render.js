(function() {
    'use strict';

    var AIChatRender = {

        escapeHtml: function(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        buildHeaderHtml: function(isMinimized) {
            var html = '<div class="ai-chat-header" id="ai-chat-header">';
            html += '<span class="ai-chat-header-title">AI chat</span>';
            html += '<div class="ai-chat-header-controls">';
            var icon = isMinimized ? '+' : '−';
            html += '<button class="ai-chat-header-button" id="ai-chat-minimize" title="Minimize">' + icon + '</button>';
            html += '</div>';
            html += '</div>';
            return html;
        },

        buildResizeHandlesHtml: function() {
            var html = '';
            html += '<div class="ai-chat-resize-handle ai-chat-resize-nw" data-direction="nw"></div>';
            html += '<div class="ai-chat-resize-handle ai-chat-resize-ne" data-direction="ne"></div>';
            html += '<div class="ai-chat-resize-handle ai-chat-resize-sw" data-direction="sw"></div>';
            html += '<div class="ai-chat-resize-handle ai-chat-resize-se" data-direction="se"></div>';
            return html;
        },

        buildTabsHtml: function(tabs, activeTabId) {
            var html = '<div class="ai-chat-tabs" id="ai-chat-tabs">';

            for (var i = 0; i < tabs.length; i++) {
                var tab = tabs[i];
                var activeClass = tab.id === activeTabId ? ' active' : '';
                html += '<div class="ai-chat-tab' + activeClass + '" data-tab-id="' + tab.id + '" draggable="true">';
                html += '<span class="ai-chat-tab-title">' + this.escapeHtml(tab.title) + '</span>';
                if (tabs.length > 1) {
                    html += '<span class="ai-chat-tab-close" data-tab-id="' + tab.id + '">✕</span>';
                }
                html += '</div>';
            }

            html += '<button class="ai-chat-tab-add" id="ai-chat-tab-add" title="New chat">+</button>';
            html += '</div>';
            return html;
        },

        buildBodyHtml: function(tabs, activeTabId, needsConfig, configMode, selectedProvider, cameFromChat, hadKeyOnEntry) {
            var html = '<div class="ai-chat-body">';

            if (needsConfig) {
                html += '<div class="ai-chat-tab-panel active">';
                html += '<div class="ai-chat-messages">';
                if (configMode === 'key-input' && selectedProvider) {
                    html += AIChatConfig.buildKeyInputHtml(selectedProvider, hadKeyOnEntry);
                } else if (configMode === 'manage-keys') {
                    html += AIChatConfig.buildManageKeysHtml(cameFromChat);
                } else {
                    var showBackOnProviders = cameFromChat && hadKeyOnEntry;
                    html += AIChatConfig.buildProviderSelectionHtml(showBackOnProviders);
                }
                html += '</div>';
                html += '</div>';
            } else {
                for (var i = 0; i < tabs.length; i++) {
                    var tab = tabs[i];
                    var activeClass = tab.id === activeTabId ? ' active' : '';
                    html += '<div class="ai-chat-tab-panel' + activeClass + '" data-tab-id="' + tab.id + '">';
                    html += this.buildMessagesHtml(tab, needsConfig, configMode, selectedProvider, cameFromChat, hadKeyOnEntry);
                    html += this.buildInputAreaHtml(tab);
                    html += '</div>';
                }
            }

            html += '</div>';
            return html;
        },

        buildMessagesHtml: function(tab, needsConfig, configMode, selectedProvider, cameFromChat, hadKeyOnEntry) {
            var html = '<div class="ai-chat-messages" data-tab-id="' + tab.id + '">';

            if (tab.messages.length === 0) {
                html += '<div class="ai-chat-empty">';
                html += '<div class="ai-chat-empty-icon">💬</div>';
                html += '<div>Start a conversation</div>';
                html += '</div>';
            } else {
                for (var i = 0; i < tab.messages.length; i++) {
                    var msg = tab.messages[i];
                    html += '<div class="ai-chat-message ' + msg.role + '">';
                    html += this.escapeHtml(msg.content);
                    html += '</div>';
                }
            }

            html += '</div>';
            return html;
        },

        buildInputAreaHtml: function(tab) {
            var html = '<div class="ai-chat-input-area">';
            html += '<div class="ai-chat-input-wrapper">';
            html += '<div class="ai-chat-input" data-tab-id="' + tab.id + '" contenteditable="true" data-placeholder="Type a message .."></div>';
            html += '</div>';
            html += this.buildInputToolbarHtml(tab);
            html += '</div>';
            return html;
        },

        buildInputToolbarHtml: function(tab) {
            var html = '<div class="ai-chat-input-toolbar">';
            html += this.buildModelSelectorHtml(tab);
            html += '<div class="ai-chat-input-toolbar-buttons">';
            html += '<button class="ai-chat-options-button" data-tab-id="' + tab.id + '" aria-label="Options">';
            html += '<svg viewBox="0 0 24 24" fill="currentColor" class="ai-chat-options-icon"><path d="M12 4v16m-8-8h16" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/></svg>';
            html += '</button>';
            html += '<button class="ai-chat-send-button" data-tab-id="' + tab.id + '" aria-label="Send">';
            html += '<svg viewBox="0 0 24 24" fill="currentColor" class="ai-chat-send-icon"><path d="M12 19V5m0 0l-7 7m7-7l7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>';
            html += '</button>';
            html += '</div>';
            html += '</div>';
            return html;
        },

        buildModelSelectorHtml: function(tab) {
            var models = AIChatConfig.getModelsForConfiguredProviders();
            if (models.length === 0) {
                return '';
            }

            var selectedModel = tab.model || (models.length > 0 ? models[0].id : '');

            var html = '<div class="ai-chat-model-selector">';
            html += '<select class="ai-chat-model-select" data-tab-id="' + tab.id + '">';
            for (var i = 0; i < models.length; i++) {
                var model = models[i];
                var selected = model.id === selectedModel ? ' selected' : '';
                var separator = model.isFirst ? ' data-separator="true"' : '';
                var disabled = model.disabled ? ' disabled data-disabled="true"' : '';
                html += '<option value="' + model.id + '"' + selected + separator + disabled + '>' + model.name + '</option>';
            }
            html += '</select>';
            html += '</div>';
            return html;
        },

        buildContextMenuHtml: function(tabId) {
            return '<div class="ai-chat-context-menu-item" data-action="rename" data-tab-id="' + tabId + '">Rename tab</div>';
        }
    };

    window.AIChatRender = AIChatRender;

})();
