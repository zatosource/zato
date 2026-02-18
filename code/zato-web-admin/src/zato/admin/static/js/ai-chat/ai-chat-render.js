(function() {
    'use strict';

    var AIChatRender = {

        escapeHtml: function(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        formatTime: function(timestamp) {
            if (!timestamp) {
                return '';
            }
            var date = new Date(timestamp);
            var pad = function(n) { return n < 10 ? '0' + n : n; };
            var year = date.getFullYear();
            var month = pad(date.getMonth() + 1);
            var day = pad(date.getDate());
            var hours = pad(date.getHours());
            var minutes = pad(date.getMinutes());
            var seconds = pad(date.getSeconds());
            return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
        },

        buildHeaderHtml: function(isMinimized, isMaximized) {
            var html = '<div class="ai-chat-header" id="ai-chat-header">';
            html += '<div class="ai-chat-header-tags">';
            if (isMinimized) {
                html += '<span class="ai-chat-header-tag ai-chat-header-tag-primary">AI</span>';
            }
            if (typeof ZatoEnvName !== 'undefined' && ZatoEnvName) {
                html += '<span class="ai-chat-header-tag ai-chat-header-tag-env">' + ZatoEnvName + '</span>';
            }
            html += '</div>';
            html += '<div class="ai-chat-header-controls">';
            var minIcon = isMinimized ? '+' : '−';
            html += '<button class="ai-chat-header-button" id="ai-chat-minimize" title="Minimize">' + minIcon + '</button>';
            html += '<button class="ai-chat-header-button" id="ai-chat-maximize" title="Maximize">□</button>';
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
                } else if (configMode === 'manage-mcp') {
                    html += AIChatMCP.buildManageServersHtml();
                } else if (configMode === 'add-mcp') {
                    html += AIChatMCP.buildAddServerHtml();
                } else if (configMode === 'mcp-detail') {
                    if (AIChatMCP.selectedServer) {
                        html += AIChatMCP.buildServerDetailHtml(AIChatMCP.selectedServer, AIChatMCP.selectedServerTools, AIChatMCP.loadingTools);
                    } else {
                        html += AIChatMCP.buildManageServersHtml();
                    }
                } else if (configMode === 'edit-mcp') {
                    if (AIChatMCP.selectedServer) {
                        html += AIChatMCP.buildEditServerHtml(AIChatMCP.selectedServer);
                    } else {
                        html += AIChatMCP.buildManageServersHtml();
                    }
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
                html += '<div>Chat with AI</div>';
                html += '</div>';
            } else {
                for (var i = 0; i < tab.messages.length; i++) {
                    var msg = tab.messages[i];
                    var streamingContent = msg.streaming ? AIChatMessages.getStreamingContent(tab.id) : '';
                    var hasContent = streamingContent && streamingContent.trim().length > 0;
                    var streamingClass = '';
                    if (msg.streaming) {
                        streamingClass = hasContent ? ' streaming has-content' : ' streaming';
                    }
                    var timestamp = msg.timestamp || '';
                    html += '<div class="ai-chat-message ' + msg.role + streamingClass + '" data-timestamp="' + timestamp + '">';
                    html += '<div class="ai-chat-message-content">';
                    if (msg.streaming) {
                        if (hasContent) {
                            var parsedHtml = marked.parse(streamingContent);
                            if (typeof markedEmoji !== 'undefined' && markedEmoji.wrapUnicodeEmojis) {
                                parsedHtml = markedEmoji.wrapUnicodeEmojis(parsedHtml);
                            }
                            html += parsedHtml;
                        } else {
                            html += AIChatWaiting.buildWaitingHtml();
                        }
                    } else if (msg.role === 'assistant') {
                        var parsedHtml = marked.parse(msg.content);
                        if (typeof markedEmoji !== 'undefined') {
                            if (markedEmoji.convertAsciiEmoticons) {
                                parsedHtml = markedEmoji.convertAsciiEmoticons(parsedHtml);
                            }
                            if (markedEmoji.wrapUnicodeEmojis) {
                                parsedHtml = markedEmoji.wrapUnicodeEmojis(parsedHtml);
                            }
                        }
                        if (parsedHtml.indexOf('LLM is temporarily unavailable') !== -1) {
                            parsedHtml = parsedHtml.replace(/Please try again\./, 'Please try again. <button class="ai-chat-retry-btn" data-tab-id="' + tab.id + '">Retry</button>');
                        }
                        var toolDoneRegex = /\[TOOL_DONE:([^|]+)\|([A-Za-z0-9+/=]+)\]/g;
                        var toolDoneMatch;
                        while ((toolDoneMatch = toolDoneRegex.exec(parsedHtml)) !== null) {
                            var doneMessage = toolDoneMatch[1];
                            var itemsJsonBase64 = toolDoneMatch[2];
                            var itemsJson = '';
                            try { itemsJson = decodeURIComponent(escape(atob(itemsJsonBase64))); } catch (e) {}
                            var items = [];
                            try { items = JSON.parse(itemsJson); } catch (e) {}
                            var inlineTags = '';
                            var diffHtml = '';
                            var showBtn = '';
                            if (items.length > 0) {
                                var isServiceDeploy = items.every(function(item) { return item.type === 'Service'; });
                                if (isServiceDeploy) {
                                    inlineTags = '<span class="ai-tool-tags">';
                                    for (var j = 0; j < items.length; j++) {
                                        var item = items[j];
                                        var tagData = JSON.stringify({
                                            name: item.name,
                                            old_content: item.old_content || '',
                                            new_content: item.new_content || '',
                                            is_new: item.is_new !== false
                                        });
                                        inlineTags += '<span class="ai-tool-tag active" data-diff=\'' + tagData.replace(/'/g, '&#39;') + '\'>' + item.name + '</span>';
                                    }
                                    inlineTags += '</span>';
                                    if (window.AIChatDiff) {
                                        for (var j = 0; j < items.length; j++) {
                                            var item = items[j];
                                            var isNew = item.is_new !== false;
                                            diffHtml += '<div class="ai-diff-wrapper" data-file="' + item.name + '">';
                                            diffHtml += AIChatDiff.renderDiff(item.old_content || '', item.new_content || '', isNew, item.name);
                                            diffHtml += '</div>';
                                        }
                                    }
                                } else {
                                    showBtn = '<button class="ai-tool-show-btn" data-items=\'' + itemsJson.replace(/'/g, '&#39;') + '\'>Show</button>';
                                }
                            }
                            var toolDoneHtml = '<div class="ai-tool-progress ai-tool-done"><span><span class="ai-tool-checkmark">✓</span> ' + doneMessage + '</span>' + inlineTags + showBtn + diffHtml + '</div>';
                            parsedHtml = parsedHtml.replace(toolDoneMatch[0], toolDoneHtml);
                            parsedHtml = parsedHtml.replace('<p>' + toolDoneHtml + '</p>', toolDoneHtml);
                        }
                        html += parsedHtml;
                    } else {
                        var userHtml = this.escapeHtml(msg.content);
                        if (typeof markedEmoji !== 'undefined') {
                            if (markedEmoji.convertShortcodes) {
                                userHtml = markedEmoji.convertShortcodes(userHtml);
                            }
                            if (markedEmoji.convertAsciiEmoticons) {
                                userHtml = markedEmoji.convertAsciiEmoticons(userHtml);
                            }
                            if (markedEmoji.wrapUnicodeEmojis) {
                                userHtml = markedEmoji.wrapUnicodeEmojis(userHtml);
                            }
                        }
                        html += userHtml;
                    }
                    html += '</div>';
                    if (msg.streaming) {
                        html += '<div class="ai-chat-message-footer">';
                        html += '<button class="ai-chat-message-stop" data-tab-id="' + tab.id + '">';
                        html += '<svg viewBox="0 0 24 24" width="14" height="14"><rect x="5" y="5" width="14" height="14" fill="currentColor"/></svg>';
                        html += '</button>';
                        html += '</div>';
                    } else {
                        html += '<div class="ai-chat-message-footer">';
                        if (timestamp) {
                            html += '<span class="ai-chat-message-time">' + this.formatTime(timestamp) + '</span>';
                        }
                        html += '<button class="ai-chat-message-copy">Copy</button>';
                        html += '</div>';
                        if (msg.interrupted) {
                            html += '<span class="ai-chat-message-continue" data-message-index="' + i + '">Continue</span>';
                        }
                    }
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
            html += this.buildInputFooterHtml(tab);
            html += '</div>';
            return html;
        },

        buildInputFooterHtml: function(tab) {
            var isStreaming = AIChatMessages.isStreaming(tab.id);
            var html = '<div class="ai-chat-input-footer">';
            html += this.buildModelSelectorHtml(tab);
            html += '<div class="ai-chat-input-footer-buttons">';
            html += '<button class="ai-chat-options-button" data-tab-id="' + tab.id + '" aria-label="Options">';
            html += '<svg viewBox="0 0 24 24" fill="currentColor" class="ai-chat-options-icon"><path d="M12 4v16m-8-8h16" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/></svg>';
            html += '</button>';
            if (isStreaming) {
                html += '<button class="ai-chat-send-button ai-chat-stop-button" data-tab-id="' + tab.id + '" aria-label="Stop">';
                html += '<svg viewBox="0 0 24 24" fill="currentColor" class="ai-chat-send-icon"><rect x="5" y="5" width="14" height="14" fill="currentColor"/></svg>';
                html += '</button>';
            } else {
                html += '<button class="ai-chat-send-button" data-tab-id="' + tab.id + '" aria-label="Send">';
                html += '<svg viewBox="0 0 24 24" fill="currentColor" class="ai-chat-send-icon"><path d="M12 19V5m0 0l-7 7m7-7l7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>';
                html += '</button>';
            }
            html += '</div>';
            html += '</div>';
            return html;
        },

        buildModelSelectorHtml: function(tab) {
            var models = AIChatConfig.getModelsForConfiguredProviders();
            if (models.length === 0) {
                return '';
            }

            var selectedModel = tab.model || '';
            var selectedModelValid = false;
            var firstEnabledModel = null;

            for (var i = 0; i < models.length; i++) {
                if (!models[i].disabled) {
                    if (firstEnabledModel === null) {
                        firstEnabledModel = models[i].id;
                    }
                    if (models[i].id === selectedModel) {
                        selectedModelValid = true;
                    }
                }
            }

            if (!selectedModelValid && firstEnabledModel) {
                selectedModel = firstEnabledModel;
            }

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
            html += this.buildTokenCountersHtml(tab);
            html += '</div>';
            return html;
        },

        buildTokenCountersHtml: function(tab) {
            console.log('[TOKEN-TRACE] buildTokenCountersHtml called for tabId=' + tab.id);
            var tokensIn = AIChatTabState.getTokensIn(tab.id);
            var tokensOut = AIChatTabState.getTokensOut(tab.id);
            console.log('[TOKEN-TRACE] buildTokenCountersHtml: tokensIn=' + tokensIn + ', tokensOut=' + tokensOut);
            var html = '<span class="ai-chat-token-counters" data-tab-id="' + tab.id + '">';
            html += '<span class="ai-chat-token-out">Tok out: ' + AIChatTabState.humanizeNumber(tokensOut) + '</span>';
            html += '<span class="ai-chat-token-in">Tok in: ' + AIChatTabState.humanizeNumber(tokensIn) + '</span>';
            html += '</span>';
            return html;
        },

        buildContextMenuHtml: function(tabId) {
            return '<div class="ai-chat-context-menu-item" data-action="rename" data-tab-id="' + tabId + '">Rename tab</div>';
        }
    };

    window.AIChatRender = AIChatRender;

})();
