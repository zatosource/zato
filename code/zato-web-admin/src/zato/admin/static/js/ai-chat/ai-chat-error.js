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

            var header = popup.querySelector('.ai-chat-error-header');
            var isDragging = false;
            var dragOffsetX = 0;
            var dragOffsetY = 0;

            header.addEventListener('mousedown', function(e) {
                if (e.target === closeBtn) return;
                isDragging = true;
                var rect = popup.getBoundingClientRect();
                dragOffsetX = e.clientX - rect.left;
                dragOffsetY = e.clientY - rect.top;
                popup.style.transform = 'none';
                popup.style.left = rect.left + 'px';
                popup.style.top = rect.top + 'px';
            });

            document.addEventListener('mousemove', function(e) {
                if (!isDragging) return;
                popup.style.left = (e.clientX - dragOffsetX) + 'px';
                popup.style.top = (e.clientY - dragOffsetY) + 'px';
            });

            document.addEventListener('mouseup', function() {
                isDragging = false;
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
