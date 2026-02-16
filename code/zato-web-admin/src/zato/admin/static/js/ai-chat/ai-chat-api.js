(function() {
    'use strict';

    var AIChatAPI = {

        streamMessage: function(tabId, model, messages, callbacks) {
            AIChatSSE.connect(tabId, model, messages, {
                onChunk: function(text) {
                    if (callbacks.onChunk) {
                        callbacks.onChunk(text);
                    }
                },
                onToolProgress: function(data) {
                    if (callbacks.onToolProgress) {
                        callbacks.onToolProgress(data);
                    }
                },
                onComplete: function(inputTokens, outputTokens) {
                    if (callbacks.onComplete) {
                        callbacks.onComplete(inputTokens, outputTokens);
                    }
                },
                onError: function(error) {
                    if (callbacks.onError) {
                        callbacks.onError(error);
                    }
                },
                onWaiting: function(data) {
                    if (callbacks.onWaiting) {
                        callbacks.onWaiting(data);
                    }
                }
            });
        },

        cancelStream: function(tabId) {
            AIChatSSE.disconnect(tabId);
        },

        isStreaming: function(tabId) {
            return AIChatSSE.isConnected(tabId);
        }
    };

    window.AIChatAPI = AIChatAPI;

})();
