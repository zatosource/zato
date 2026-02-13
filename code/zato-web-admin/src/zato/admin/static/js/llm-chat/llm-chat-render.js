(function() {
    'use strict';

    var LLMChatRender = {

        escapeHtml: function(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        buildHeaderHtml: function(isMinimized) {
            var html = '<div class="llm-chat-header" id="llm-chat-header">';
            html += '<span class="llm-chat-header-title">LLM chat</span>';
            html += '<div class="llm-chat-header-controls">';
            var icon = isMinimized ? '+' : '−';
            html += '<button class="llm-chat-header-button" id="llm-chat-minimize" title="Minimize">' + icon + '</button>';
            html += '</div>';
            html += '</div>';
            return html;
        },

        buildResizeHandlesHtml: function() {
            var html = '';
            html += '<div class="llm-chat-resize-handle llm-chat-resize-nw" data-direction="nw"></div>';
            html += '<div class="llm-chat-resize-handle llm-chat-resize-ne" data-direction="ne"></div>';
            html += '<div class="llm-chat-resize-handle llm-chat-resize-sw" data-direction="sw"></div>';
            html += '<div class="llm-chat-resize-handle llm-chat-resize-se" data-direction="se"></div>';
            return html;
        },

        buildTabsHtml: function(tabs, activeTabId) {
            var html = '<div class="llm-chat-tabs" id="llm-chat-tabs">';

            for (var i = 0; i < tabs.length; i++) {
                var tab = tabs[i];
                var activeClass = tab.id === activeTabId ? ' active' : '';
                html += '<div class="llm-chat-tab' + activeClass + '" data-tab-id="' + tab.id + '" draggable="true">';
                html += '<span class="llm-chat-tab-title">' + this.escapeHtml(tab.title) + '</span>';
                if (tabs.length > 1) {
                    html += '<span class="llm-chat-tab-close" data-tab-id="' + tab.id + '">✕</span>';
                }
                html += '</div>';
            }

            html += '<button class="llm-chat-tab-add" id="llm-chat-tab-add" title="New chat">+</button>';
            html += '</div>';
            return html;
        },

        buildBodyHtml: function(tabs, activeTabId) {
            var html = '<div class="llm-chat-body">';

            for (var i = 0; i < tabs.length; i++) {
                var tab = tabs[i];
                var activeClass = tab.id === activeTabId ? ' active' : '';
                html += '<div class="llm-chat-tab-panel' + activeClass + '" data-tab-id="' + tab.id + '">';
                html += this.buildMessagesHtml(tab);
                html += this.buildInputAreaHtml(tab);
                html += '</div>';
            }

            html += '</div>';
            return html;
        },

        buildMessagesHtml: function(tab) {
            var html = '<div class="llm-chat-messages" data-tab-id="' + tab.id + '">';

            if (tab.messages.length === 0) {
                html += '<div class="llm-chat-empty">';
                html += '<div class="llm-chat-empty-icon">💬</div>';
                html += '<div>Start a conversation</div>';
                html += '</div>';
            } else {
                for (var i = 0; i < tab.messages.length; i++) {
                    var msg = tab.messages[i];
                    html += '<div class="llm-chat-message ' + msg.role + '">';
                    html += this.escapeHtml(msg.content);
                    html += '</div>';
                }
            }

            html += '</div>';
            return html;
        },

        buildInputAreaHtml: function(tab) {
            var html = '<div class="llm-chat-input-area">';
            html += '<div class="llm-chat-input-wrapper">';
            html += '<div class="llm-chat-input" data-tab-id="' + tab.id + '" contenteditable="true" data-placeholder="Type a message .."></div>';
            html += '</div>';
            html += '<button class="llm-chat-send-button" data-tab-id="' + tab.id + '" aria-label="Send">';
            html += '<svg viewBox="2 2 16 16" class="llm-chat-send-icon"><path d="M2.72113 2.05149L18.0756 9.61746C18.3233 9.73952 18.4252 10.0393 18.3031 10.287C18.2544 10.3858 18.1744 10.4658 18.0756 10.5145L2.72144 18.0803C2.47374 18.2023 2.17399 18.1005 2.05193 17.8528C1.99856 17.7445 1.98619 17.6205 2.0171 17.5038L3.53835 11.7591C3.58866 11.5691 3.7456 11.4262 3.93946 11.3939L10.8204 10.2466C10.9047 10.2325 10.9744 10.1769 11.0079 10.1012L11.0259 10.0411C11.0454 9.92436 10.9805 9.81305 10.8759 9.76934L10.8204 9.7534L3.90061 8.6001C3.70668 8.56778 3.54969 8.4248 3.49942 8.23473L2.01676 2.62789C1.94612 2.36093 2.10528 2.08726 2.37224 2.01663C2.48893 1.98576 2.61285 1.99814 2.72113 2.05149Z"></path></svg>';
            html += '</button>';
            html += '</div>';
            return html;
        },

        buildContextMenuHtml: function(tabId) {
            return '<div class="llm-chat-context-menu-item" data-action="rename" data-tab-id="' + tabId + '">Rename tab</div>';
        }
    };

    window.LLMChatRender = LLMChatRender;

})();
