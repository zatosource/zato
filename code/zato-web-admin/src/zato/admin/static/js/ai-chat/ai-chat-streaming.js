(function() {
    'use strict';

    var AIChatStreaming = {

        sendMessage: function(widget, core, tabId) {
            var input = widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
            if (!input) return;

            var message = AIChatInput.getMessageText(input);
            if (!message) return;

            AIChatInput.clearInputStorage(tabId);

            var tab = AIChatTabs.getTabById(core.tabs, tabId);
            if (!tab) return;

            if (AIChatMessages.isStreaming(tabId)) {
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
                core.saveState();
                core.render();
                return;
            }

            var apiMessages = this.buildApiMessages(tab);

            AIChatMessages.startStreamingMessage(tab, tabId);

            core.saveState();
            core.render();

            var waitingEl = widget.querySelector('.ai-chat-waiting-indicator');
            if (waitingEl) {
                AIChatWaiting.startCycling(tabId, waitingEl);
            }

            var newInput = widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
            if (newInput) {
                newInput.focus();
            }

            var self = this;
            var messagesContainer = widget.querySelector('.ai-chat-messages[data-tab-id="' + tabId + '"]');
            console.log('[IDLE-TRACE] messagesContainer:', !!messagesContainer);
            if (messagesContainer) {
                var streamingEl = messagesContainer.querySelector('.ai-chat-message.streaming');
                console.log('[IDLE-TRACE] streamingEl:', !!streamingEl);
                if (streamingEl) {
                    var contentEl = streamingEl.querySelector('.ai-chat-message-content');
                    console.log('[IDLE-TRACE] contentEl:', !!contentEl);
                    if (contentEl) {
                        var waitingEl = contentEl.querySelector('.ai-chat-waiting-indicator');
                        console.log('[IDLE-TRACE] waitingEl:', !!waitingEl);
                        console.log('[IDLE-TRACE] calling startIdleWatch for tabId:', tabId);
                        AIChatWaiting.startIdleWatch(tabId, contentEl);
                    }
                }
            } else {
                console.log('[IDLE-TRACE] no messagesContainer found');
            }

            AIChatAPI.streamMessage(tabId, model, apiMessages, {
                onChunk: function(text) {
                    AIChatWaiting.recordActivity(tabId);
                    AIChatMessages.appendToStreamingMessage(tabId, text);
                    self.updateStreamingMessage(widget, tabId);
                },
                onToolProgress: function(data) {
                    AIChatWaiting.recordActivity(tabId);
                    self.handleToolProgress(widget, tabId, data);
                },
                onToolPreview: function(data) {
                    AIChatWaiting.recordActivity(tabId);
                    self.handleToolPreview(widget, tabId, data);
                },
                onComplete: function(inputTokens, outputTokens) {
                    AIChatWaiting.stopIdleWatch(tabId);

                    if (inputTokens > 0) {
                        AIChatTabState.addTokensOut(tabId, inputTokens);
                    }
                    if (outputTokens > 0) {
                        AIChatTabState.addTokensIn(tabId, outputTokens);
                    }

                    AIChatMessages.finishStreamingMessage(tab, tabId);
                    core.saveState();
                    core.render();

                    var input = widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
                    if (input) {
                        input.focus();
                    }
                },
                onError: function(error) {
                    AIChatWaiting.stopIdleWatch(tabId);
                    AIChatMessages.cancelStreamingMessage(tab, tabId);
                    AIChatMessages.addMessage(tab, 'system', 'Error: ' + error);
                    core.saveState();
                    core.render();
                },
                onWaiting: function(data) {
                    if (data && data.waiting_type === 'code') {
                        AIChatWaiting.startCodeCycling(tabId);
                    }
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

        updateStreamingMessage: function(widget, tabId) {
            var messagesContainer = widget.querySelector('.ai-chat-messages[data-tab-id="' + tabId + '"]');
            if (!messagesContainer) {
                return;
            }

            var streamingEl = messagesContainer.querySelector('.ai-chat-message.streaming');
            if (!streamingEl) {
                return;
            }

            var contentEl = streamingEl.querySelector('.ai-chat-message-content');
            if (!contentEl) {
                return;
            }

            var content = AIChatMessages.getStreamingContent(tabId);

            AIChatWaiting.stopCycling(tabId);

            if (!streamingEl.classList.contains('has-content')) {
                streamingEl.classList.add('has-content');
            }

            var progressEl = contentEl.querySelector('.ai-tool-progress');
            var progressOuterHTML = progressEl ? progressEl.outerHTML : null;

            var html = marked.parse(content);
            if (typeof markedEmoji !== 'undefined') {
                if (markedEmoji.convertAsciiEmoticons) {
                    html = markedEmoji.convertAsciiEmoticons(html);
                }
                if (markedEmoji.wrapUnicodeEmojis) {
                    html = markedEmoji.wrapUnicodeEmojis(html);
                }
            }

            var toolDoneRegex = /\[TOOL_DONE:([^|]+)\|(\[.*?\])\]/g;
            var toolDoneMatch;
            while ((toolDoneMatch = toolDoneRegex.exec(html)) !== null) {
                var doneMessage = toolDoneMatch[1];
                var itemsJsonRaw = toolDoneMatch[2];
                var itemsJson = itemsJsonRaw.replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&');
                var items = [];
                try { items = JSON.parse(itemsJson); } catch (e) { console.log('[TOOL_DONE] JSON parse error:', e); }
                var inlineTags = '';
                var diffHtml = '';
                var showBtn = '';
                if (items.length > 0) {
                    var isServiceDeploy = items.every(function(item) { return item.type === 'Service'; });
                    if (isServiceDeploy) {
                        inlineTags = '<span class="ai-tool-tags">';
                        for (var i = 0; i < items.length; i++) {
                            var item = items[i];
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
                            for (var i = 0; i < items.length; i++) {
                                var item = items[i];
                                var isNew = item.is_new !== false;
                                diffHtml += '<div class="ai-diff-wrapper" data-file="' + item.name + '">';
                                diffHtml += '<div class="ai-diff-filename">' + item.name + '</div>';
                                diffHtml += AIChatDiff.renderDiff(item.old_content || '', item.new_content || '', isNew);
                                diffHtml += '</div>';
                            }
                        }
                    } else {
                        showBtn = '<button class="ai-tool-show-btn" data-items=\'' + itemsJson.replace(/'/g, '&#39;') + '\'>Show</button>';
                    }
                }
                var toolDoneHtml = '<div class="ai-tool-progress ai-tool-done"><span><span class="ai-tool-checkmark">✓</span> ' + doneMessage + '</span>' + inlineTags + showBtn + diffHtml + '</div>';
                html = html.replace(toolDoneMatch[0], toolDoneHtml);
                html = html.replace('<p>' + toolDoneHtml + '</p>', toolDoneHtml);
            }

            contentEl.innerHTML = html;

            this.highlightCodeBlocks(contentEl);

            AIChatMessages.scrollToBottom(messagesContainer);
        },

        highlightCodeBlocks: function(contentEl) {
            if (!window.AIChatHighlight) {
                return;
            }
            AIChatHighlight.highlightCodeBlocks(contentEl);
        },

        handleToolProgress: function(widget, tabId, data) {
            console.log('[SSE-TRACE] handleToolProgress called with data:', JSON.stringify(data));
            console.log('[SSE-TRACE] widget:', !!widget, 'tabId:', tabId);
            
            var messagesContainer = widget.querySelector('.ai-chat-messages[data-tab-id="' + tabId + '"]');
            console.log('[SSE-TRACE] messagesContainer found:', !!messagesContainer);
            if (!messagesContainer) {
                return;
            }

            var streamingEl = messagesContainer.querySelector('.ai-chat-message.streaming');
            console.log('[SSE-TRACE] streamingEl found:', !!streamingEl);
            if (!streamingEl) {
                return;
            }

            var contentEl = streamingEl.querySelector('.ai-chat-message-content');
            console.log('[SSE-TRACE] contentEl found:', !!contentEl);
            if (!contentEl) {
                return;
            }

            var progressEl;
            if (data.status === 'start') {
                var allProgress = contentEl.querySelectorAll('.ai-tool-progress.ai-tool-running');
                var lastRunning = allProgress.length > 0 ? allProgress[allProgress.length - 1] : null;
                if (lastRunning) {
                    progressEl = lastRunning;
                    console.log('[SSE-TRACE] updating existing running progressEl');
                } else {
                    progressEl = document.createElement('div');
                    progressEl.className = 'ai-tool-progress';
                    contentEl.appendChild(progressEl);
                    console.log('[SSE-TRACE] created new progressEl for start');
                }
            } else {
                var allProgress = contentEl.querySelectorAll('.ai-tool-progress');
                progressEl = allProgress.length > 0 ? allProgress[allProgress.length - 1] : null;
                console.log('[SSE-TRACE] found last progressEl:', !!progressEl);
                if (!progressEl) {
                    return;
                }
            }

            if (data.status === 'start') {
                var startHtml = '<span class="ai-tool-spinner"></span> ';
                var deployMatch = data.message.match(/^Deploying (.+?)\.\.\.$/);
                if (deployMatch) {
                    var fileList = deployMatch[1];
                    var fileNames = fileList.split(', ');
                    startHtml += 'Deploying <span class="ai-tool-tags">';
                    for (var i = 0; i < fileNames.length; i++) {
                        startHtml += '<span class="ai-tool-tag">' + fileNames[i] + '</span>';
                    }
                    startHtml += '</span>';
                } else {
                    startHtml += data.message;
                }
                progressEl.innerHTML = startHtml;
                progressEl.classList.remove('ai-tool-done');
                progressEl.classList.add('ai-tool-running');
                streamingEl.classList.add('hide-cursor');
                console.log('[SSE-TRACE] set progressEl to running state, hid cursor');

                var existingWaiting = contentEl.querySelector('.ai-chat-waiting-indicator');
                if (existingWaiting) {
                    existingWaiting.remove();
                }
            } else if (data.status === 'done') {
                var itemsJson = data.items ? JSON.stringify(data.items) : '[]';
                var inlineTags = '';
                var diffHtml = '';
                var showBtn = '';
                if (data.items && data.items.length > 0) {
                    var isServiceDeploy = data.items.every(function(item) { return item.type === 'Service'; });
                    if (isServiceDeploy) {
                        inlineTags = '<span class="ai-tool-tags">';
                        for (var i = 0; i < data.items.length; i++) {
                            var item = data.items[i];
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
                            for (var i = 0; i < data.items.length; i++) {
                                var item = data.items[i];
                                var isNew = item.is_new !== false;
                                diffHtml += '<div class="ai-diff-wrapper" data-file="' + item.name + '">';
                                diffHtml += '<div class="ai-diff-filename">' + item.name + '</div>';
                                diffHtml += AIChatDiff.renderDiff(item.old_content || '', item.new_content || '', isNew);
                                diffHtml += '</div>';
                            }
                        }
                    } else {
                        showBtn = '<button class="ai-tool-show-btn" data-items=\'' + itemsJson.replace(/'/g, '&#39;') + '\'>Show</button>';
                    }
                }
                console.log('[SSE-TRACE] showBtn:', showBtn, 'inlineTags:', inlineTags, 'items:', data.items);
                progressEl.innerHTML = '<span><span class="ai-tool-checkmark">✓</span> ' + data.message + '</span>' + inlineTags + showBtn + diffHtml;
                progressEl.classList.remove('ai-tool-running');
                progressEl.classList.add('ai-tool-done');
                streamingEl.classList.remove('hide-cursor');

                var marker = '[TOOL_DONE:' + data.message + '|' + itemsJson + ']';
                AIChatMessages.appendToStreamingMessage(tabId, '\n\n' + marker);
                console.log('[SSE-TRACE] set progressEl to done state, cursor restored');

                if (window.AIChatDiff && data.items && data.items.length > 0) {
                    for (var i = 0; i < data.items.length; i++) {
                        var item = data.items[i];
                        if (item.is_new === false) {
                            var container = progressEl.querySelector('.ai-diff-wrapper[data-file="' + item.name + '"] .ai-diff-container');
                            console.log('[SSE-TRACE] scrolling to first hunk for:', item.name, 'container:', container);
                            if (container) {
                                AIChatDiff.navigateToHunk(container, 0);
                            }
                        }
                    }
                }
            }

            AIChatMessages.scrollToBottom(messagesContainer);
        },

        handleToolPreview: function(widget, tabId, data) {
            console.log('[SSE-TRACE] handleToolPreview called with data:', JSON.stringify(data));

            var messagesContainer = widget.querySelector('.ai-chat-messages[data-tab-id="' + tabId + '"]');
            if (!messagesContainer) return;

            var streamingEl = messagesContainer.querySelector('.ai-chat-message.streaming');
            if (!streamingEl) return;

            var contentEl = streamingEl.querySelector('.ai-chat-message-content');
            if (!contentEl) return;

            var progressEl = contentEl.querySelector('.ai-tool-progress.ai-tool-running');
            if (!progressEl) return;

            var fileName = data.file_path;
            var code = data.code;
            var isNew = data.is_new !== false;

            var existingWrapper = progressEl.querySelector('.ai-diff-wrapper[data-file="' + fileName + '"]');
            if (existingWrapper) return;

            var tagsContainer = progressEl.querySelector('.ai-tool-tags');
            if (!tagsContainer) {
                var firstSpan = progressEl.querySelector('span');
                if (firstSpan) {
                    tagsContainer = document.createElement('span');
                    tagsContainer.className = 'ai-tool-tags';
                    firstSpan.insertAdjacentElement('afterend', tagsContainer);
                }
            }

            if (tagsContainer) {
                var tagData = JSON.stringify({
                    name: fileName,
                    old_content: '',
                    new_content: code,
                    is_new: isNew
                });
                var tagHtml = '<span class="ai-tool-tag active" data-diff=\'' + tagData.replace(/'/g, '&#39;') + '\'>' + fileName + '</span>';
                tagsContainer.insertAdjacentHTML('beforeend', tagHtml);
            }

            if (window.AIChatDiff) {
                var diffHtml = '<div class="ai-diff-wrapper" data-file="' + fileName + '">';
                diffHtml += '<div class="ai-diff-filename">' + fileName + '</div>';
                diffHtml += AIChatDiff.renderDiff('', code, isNew);
                diffHtml += '</div>';
                progressEl.insertAdjacentHTML('beforeend', diffHtml);
            }

            AIChatMessages.scrollToBottom(messagesContainer);
        },

        stopMessage: function(widget, core, tabId) {
            var tab = AIChatTabs.getTabById(core.tabs, tabId);
            if (!tab) return;

            AIChatWaiting.stopIdleWatch(tabId);
            AIChatAPI.cancelStream(tabId);

            var content = AIChatMessages.getStreamingContent(tabId);
            if (content && content.trim()) {
                AIChatMessages.finishStreamingMessage(tab, tabId, true);
            } else {
                AIChatMessages.cancelStreamingMessage(tab, tabId);
            }

            core.saveState();
            core.render();

            var input = widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
            if (input) {
                input.focus();
            }
        },

        continueMessage: function(widget, core, tabId, messageIndex) {
            var tab = AIChatTabs.getTabById(core.tabs, tabId);
            if (!tab) return;

            var msg = tab.messages[messageIndex];
            if (!msg || !msg.interrupted) return;

            if (AIChatMessages.isStreaming(tabId)) {
                return;
            }

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
                return;
            }

            msg.interrupted = false;
            msg.streaming = true;
            msg.id = 'streaming-' + tabId;

            AIChatMessages.streamingMessages[tabId] = {
                messageId: msg.id,
                content: msg.content
            };

            core.saveState();
            core.render();

            var self = this;
            var apiMessages = this.buildApiMessages(tab);

            var messagesContainer = widget.querySelector('.ai-chat-messages[data-tab-id="' + tabId + '"]');
            if (messagesContainer) {
                var streamingEl = messagesContainer.querySelector('.ai-chat-message.streaming');
                if (streamingEl) {
                    var contentEl = streamingEl.querySelector('.ai-chat-message-content');
                    if (contentEl) {
                        AIChatWaiting.startIdleWatch(tabId, contentEl);
                    }
                }
            }

            AIChatAPI.streamMessage(tabId, model, apiMessages, {
                onChunk: function(text) {
                    AIChatWaiting.recordActivity(tabId);
                    AIChatMessages.appendToStreamingMessage(tabId, text);
                    self.updateStreamingMessage(widget, tabId);
                },
                onToolProgress: function(data) {
                    AIChatWaiting.recordActivity(tabId);
                    self.handleToolProgress(widget, tabId, data);
                },
                onToolPreview: function(data) {
                    AIChatWaiting.recordActivity(tabId);
                    self.handleToolPreview(widget, tabId, data);
                },
                onComplete: function(inputTokens, outputTokens) {
                    AIChatWaiting.stopIdleWatch(tabId);

                    if (inputTokens > 0) {
                        AIChatTabState.addTokensOut(tabId, inputTokens);
                    }
                    if (outputTokens > 0) {
                        AIChatTabState.addTokensIn(tabId, outputTokens);
                    }

                    AIChatMessages.finishStreamingMessage(tab, tabId);
                    core.saveState();
                    core.render();

                    var input = widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
                    if (input) {
                        input.focus();
                    }
                },
                onError: function(error) {
                    AIChatWaiting.stopIdleWatch(tabId);
                    AIChatMessages.finishStreamingMessage(tab, tabId, true);
                    core.saveState();
                    core.render();
                },
                onWaiting: function(data) {
                    if (data && data.waiting_type === 'code') {
                        AIChatWaiting.startCodeCycling(tabId);
                    }
                }
            });
        }
    };

    window.AIChatStreaming = AIChatStreaming;

})();
