(function() {
    'use strict';

    var LLMChatMessages = {

        addMessage: function(tab, role, content) {
            console.debug('LLMChatMessages.addMessage: role:', role, 'content:', content);
            tab.messages.push({
                role: role,
                content: content
            });
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

    window.LLMChatMessages = LLMChatMessages;

})();
