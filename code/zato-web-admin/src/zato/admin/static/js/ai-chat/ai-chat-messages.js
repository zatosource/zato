(function() {
    'use strict';

    var AIChatMessages = {

        streamingMessages: {},

        addMessage: function(tab, role, content) {
            console.debug('AIChatMessages.addMessage: role:', role, 'content:', content);
            tab.messages.push({
                role: role,
                content: content,
                timestamp: Date.now()
            });
        },

        startStreamingMessage: function(tab, tabId) {
            console.debug('AIChatMessages.startStreamingMessage: tabId:', tabId);

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

        finishStreamingMessage: function(tab, tabId) {
            console.debug('AIChatMessages.finishStreamingMessage: tabId:', tabId);

            var streaming = this.streamingMessages[tabId];
            if (!streaming) {
                return;
            }

            for (var i = 0; i < tab.messages.length; i++) {
                if (tab.messages[i].id === streaming.messageId) {
                    tab.messages[i].content = streaming.content;
                    tab.messages[i].streaming = false;
                    delete tab.messages[i].id;
                    break;
                }
            }

            delete this.streamingMessages[tabId];
        },

        cancelStreamingMessage: function(tab, tabId) {
            console.debug('AIChatMessages.cancelStreamingMessage: tabId:', tabId);

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
