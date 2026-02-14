(function() {
    'use strict';

    var AIChatError = {

        show: function(message) {
            var existing = document.querySelector('.ai-chat-error-popup');
            if (existing) {
                existing.remove();
            }

            var messageText = message;
            if (typeof message === 'object') {
                messageText = message.message || JSON.stringify(message);
            }

            var popup = document.createElement('div');
            popup.className = 'ai-chat-error-popup';

            var html = '';
            html += '<div class="ai-chat-error-header">';
            html += '<span class="ai-chat-error-title">Error</span>';
            html += '<button class="ai-chat-error-close">&times;</button>';
            html += '</div>';
            html += '<div class="ai-chat-error-body">';
            html += '<textarea class="ai-chat-error-message" readonly>' + this.escapeHtml(messageText) + '</textarea>';
            html += '</div>';

            popup.innerHTML = html;
            document.body.appendChild(popup);

            var closeBtn = popup.querySelector('.ai-chat-error-close');
            closeBtn.addEventListener('click', function() {
                popup.remove();
            });

            document.addEventListener('keydown', function handler(e) {
                if (e.key === 'Escape') {
                    popup.remove();
                    document.removeEventListener('keydown', handler);
                }
            });
        },

        escapeHtml: function(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    };

    window.AIChatError = AIChatError;

})();
