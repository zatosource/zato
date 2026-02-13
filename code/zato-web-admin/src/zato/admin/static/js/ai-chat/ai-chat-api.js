(function() {
    'use strict';

    var AIChatAPI = {

        sendMessage: function(message, tabId, onSuccess, onError) {
            console.debug('AIChatAPI.sendMessage: sending message for tab:', tabId);
            console.debug('AIChatAPI.sendMessage: message:', message);

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
            console.debug('AIChatAPI.streamMessage: streaming message for tab:', tabId);

            // TODO: implement streaming API call
            if (onComplete) {
                onComplete();
            }
        }
    };

    window.AIChatAPI = AIChatAPI;

})();
