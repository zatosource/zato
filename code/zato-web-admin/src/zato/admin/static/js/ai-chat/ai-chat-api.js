(function() {
    'use strict';

    var AIChatAPI = {

        streamMessage: function(tabId, model, messages, callbacks) {
            console.debug('AIChatAPI.streamMessage: tabId:', tabId, 'model:', model);

            AIChatSSE.connect(tabId, model, messages, {
                onChunk: function(text) {
                    if (callbacks.onChunk) {
                        callbacks.onChunk(text);
                    }
                },
                onComplete: function() {
                    if (callbacks.onComplete) {
                        callbacks.onComplete();
                    }
                },
                onError: function(error) {
                    if (callbacks.onError) {
                        callbacks.onError(error);
                    }
                }
            });
        },

        cancelStream: function(tabId) {
            console.debug('AIChatAPI.cancelStream: tabId:', tabId);
            AIChatSSE.disconnect(tabId);
        },

        isStreaming: function(tabId) {
            return AIChatSSE.isConnected(tabId);
        }
    };

    window.AIChatAPI = AIChatAPI;

})();
