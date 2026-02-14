(function() {
    'use strict';

    var AIChatMessages = {

        streamingMessages: {},

        addMessage: function(tab, role, content) {
            tab.messages.push({
                role: role,
                content: content,
                timestamp: Date.now()
            });
        },

        startStreamingMessage: function(tab, tabId) {
            var messageId = 'streaming-' + tabId;

            tab.messages.push({
                id: messageId,
                role: 'assistant',
                content: '',
                streaming: true,
                timestamp: Date.now()
            });

            this.streamingMessages[tabId] = {
                messageId: messageId,
                content: ''
            };

            return messageId;
        },

        appendToStreamingMessage: function(tabId, text) {
            var streaming = this.streamingMessages[tabId];
            if (!streaming) {
                return;
            }

            streaming.content += text;
        },

        getStreamingContent: function(tabId) {
            var streaming = this.streamingMessages[tabId];
            if (!streaming) {
                return '';
            }
            return streaming.content;
        },

        finishStreamingMessage: function(tab, tabId, interrupted) {
            var streaming = this.streamingMessages[tabId];
            if (!streaming) {
                return;
            }

            for (var i = 0; i < tab.messages.length; i++) {
                if (tab.messages[i].id === streaming.messageId) {
                    tab.messages[i].content = streaming.content;
                    tab.messages[i].streaming = false;
                    if (interrupted) {
                        tab.messages[i].interrupted = true;
                    }
                    delete tab.messages[i].id;
                    break;
                }
            }

            delete this.streamingMessages[tabId];
        },

        cancelStreamingMessage: function(tab, tabId) {
            var streaming = this.streamingMessages[tabId];
            if (!streaming) {
                return;
            }

            for (var i = tab.messages.length - 1; i >= 0; i--) {
                if (tab.messages[i].id === streaming.messageId) {
                    tab.messages.splice(i, 1);
                    break;
                }
            }

            delete this.streamingMessages[tabId];
        },

        isStreaming: function(tabId) {
            return !!this.streamingMessages[tabId];
        },

        scrollToBottom: function(messagesContainer) {
            if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        },

        clearMessages: function(tab) {
            tab.messages = [];
        }
    };

    window.AIChatMessages = AIChatMessages;

})();
