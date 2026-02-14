(function() {
    'use strict';

    var AIChatStreaming = {

        sendMessage: function(widget, core, tabId) {
            var input = widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
            if (!input) return;

            var message = AIChatInput.getMessageText(input);
            if (!message) return;

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

            var newInput = widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
            if (newInput) {
                newInput.focus();
            }

            var self = this;
            AIChatAPI.streamMessage(tabId, model, apiMessages, {
                onChunk: function(text) {
                    AIChatMessages.appendToStreamingMessage(tabId, text);
                    self.updateStreamingMessage(widget, tabId);
                },
                onComplete: function(inputTokens, outputTokens) {
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
                    AIChatMessages.cancelStreamingMessage(tab, tabId);
                    AIChatMessages.addMessage(tab, 'system', 'Error: ' + error);
                    core.saveState();
                    core.render();
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

            this.highlightCodeBlocks(contentEl);

            AIChatMessages.scrollToBottom(messagesContainer);
        },

        highlightCodeBlocks: function(contentEl) {
            if (!window.AIChatHighlight) {
                return;
            }
            AIChatHighlight.highlightCodeBlocks(contentEl);
        },

        stopMessage: function(widget, core, tabId) {
            var tab = AIChatTabs.getTabById(core.tabs, tabId);
            if (!tab) return;

            AIChatAPI.cancelStream(tabId);
            AIChatMessages.finishStreamingMessage(tab, tabId);
            core.saveState();
            core.render();

            var input = widget.querySelector('.ai-chat-input[data-tab-id="' + tabId + '"]');
            if (input) {
                input.focus();
            }
        }
    };

    window.AIChatStreaming = AIChatStreaming;

})();
