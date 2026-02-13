(function() {
    'use strict';

    var LLMChatAPI = {

        sendMessage: function(message, tabId, onSuccess, onError) {
            console.debug('LLMChatAPI.sendMessage: sending message for tab:', tabId);
            console.debug('LLMChatAPI.sendMessage: message:', message);

            // TODO: implement actual API call to backend
            // for now, just log and call success callback
            if (onSuccess) {
                onSuccess({
                    role: 'assistant',
                    content: 'API not yet implemented'
                });
            }
        },

        streamMessage: function(message, tabId, onChunk, onComplete, onError) {
            console.debug('LLMChatAPI.streamMessage: streaming message for tab:', tabId);

            // TODO: implement streaming API call
            if (onComplete) {
                onComplete();
            }
        }
    };

    window.LLMChatAPI = LLMChatAPI;

})();
