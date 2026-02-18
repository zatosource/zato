(function() {
    'use strict';

    var AIChatContextHelp = {
        popup: null,

        tokensToWords: function(tokens) {
            var words = Math.round(tokens * 0.75);
            if (words >= 1000000) {
                return '~' + (words / 1000000).toFixed(1) + 'M';
            } else if (words >= 1000) {
                return '~' + Math.round(words / 1000) + 'k';
            }
            return '~' + words;
        },

        getCurrentValues: function() {
            var tokIn = 0;
            var tokOut = 0;
            var ctxSize = 200000;
            var used = '0.0%';

            if (window.AIChat && window.AIChatTabState && window.AIChatRender) {
                var tabId = AIChat.activeTabId;
                var tab = null;
                for (var i = 0; i < AIChat.tabs.length; i++) {
                    if (AIChat.tabs[i].id === tabId) {
                        tab = AIChat.tabs[i];
                        break;
                    }
                }
                tokIn = AIChatTabState.getTokensIn(tabId);
                tokOut = AIChatTabState.getTokensOut(tabId);
                var modelId = tab ? (tab.model || 'claude-opus-4-6') : 'claude-opus-4-6';
                ctxSize = AIChatRender.getModelContextSize(modelId);
                var totalTokens = tokIn + tokOut;
                var usagePercent = Math.min(100, (totalTokens / ctxSize) * 100);
                used = usagePercent.toFixed(1) + '%';
            }

            return {
                ctxSize: AIChatTabState ? AIChatTabState.humanizeNumber(ctxSize) : ctxSize,
                ctxSizeWords: this.tokensToWords(ctxSize),
                used: used,
                tokOut: AIChatTabState ? AIChatTabState.humanizeNumber(tokOut) : tokOut,
                tokIn: AIChatTabState ? AIChatTabState.humanizeNumber(tokIn) : tokIn
            };
        },

        show: function() {
            if (this.popup) {
                this.bringToFront();
                return;
            }

            var currentValues = this.getCurrentValues();

            var popup = document.createElement('div');
            popup.className = 'ai-chat-context-help-popup';

            var html = '';
            html += '<div class="ai-chat-context-help-header">';
            html += '<div class="ai-chat-context-help-title">Context window</div>';
            html += '<button class="ai-chat-context-help-close">';
            html += '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';
            html += '</button>';
            html += '</div>';
            html += '<div class="ai-chat-context-help-content">';
            html += '<p>The <strong>context window</strong> is the amount of text an AI model can process in a single conversation.</p>';
            html += '<table>';
            html += '<tr><td><strong>Ctx size</strong></td><td>Maximum tokens</td><td>' + currentValues.ctxSize + ' <span class="ai-chat-help-grey">(' + currentValues.ctxSizeWords + ' words)</span></td></tr>';
            html += '<tr><td><strong>Used</strong></td><td>Percentage of context currently in use</td><td>' + currentValues.used + '</td></tr>';
            html += '<tr><td><strong>Tok out</strong></td><td>Tokens sent to the model</td><td>' + currentValues.tokOut + '</td></tr>';
            html += '<tr><td><strong>Tok in</strong></td><td>Tokens received from the model</td><td>' + currentValues.tokIn + '</td></tr>';
            html += '</table>';
            html += '<p><strong>When approaching the limit:</strong></p>';
            html += '<ul>';
            html += '<li>Start a new tab for a fresh conversation</li>';
            html += '<li>Summarize key points before continuing</li>';
            html += '<li>Remove large attachments no longer needed</li>';
            html += '<li>Switch to a model with a larger context window</li>';
            html += '</ul>';
            html += '</div>';

            popup.innerHTML = html;
            document.body.appendChild(popup);
            this.popup = popup;

            popup.style.left = '50%';
            popup.style.top = '50%';
            popup.style.transform = 'translate(-50%, -50%)';

            var self = this;
            var header = popup.querySelector('.ai-chat-context-help-header');
            this.makeDraggable(popup, header);
            this.makeResizable(popup);

            var closeBtn = popup.querySelector('.ai-chat-context-help-close');
            closeBtn.addEventListener('click', function() {
                self.close();
            });

            popup.style.zIndex = '10100';
        },

        close: function() {
            if (this.popup && this.popup.parentNode) {
                this.popup.parentNode.removeChild(this.popup);
            }
            this.popup = null;
        },

        bringToFront: function() {
            if (this.popup) {
                this.popup.style.zIndex = '10100';
            }
        },

        makeDraggable: function(popup, handle) {
            var isDragging = false;
            var startX, startY, startLeft, startTop;

            handle.addEventListener('mousedown', function(e) {
                if (e.target.closest('.ai-chat-context-help-close')) {
                    return;
                }
                isDragging = true;
                popup.style.transform = 'none';
                startX = e.clientX;
                startY = e.clientY;
                startLeft = popup.offsetLeft;
                startTop = popup.offsetTop;
                e.preventDefault();
            });

            document.addEventListener('mousemove', function(e) {
                if (!isDragging) return;
                var dx = e.clientX - startX;
                var dy = e.clientY - startY;
                popup.style.left = (startLeft + dx) + 'px';
                popup.style.top = (startTop + dy) + 'px';
            });

            document.addEventListener('mouseup', function() {
                isDragging = false;
            });
        },

        makeResizable: function(popup) {
            var resizer = document.createElement('div');
            resizer.className = 'ai-chat-context-help-resizer';
            popup.appendChild(resizer);

            var isResizing = false;
            var startX, startY, startWidth, startHeight;

            resizer.addEventListener('mousedown', function(e) {
                isResizing = true;
                startX = e.clientX;
                startY = e.clientY;
                startWidth = popup.offsetWidth;
                startHeight = popup.offsetHeight;
                e.preventDefault();
                e.stopPropagation();
            });

            document.addEventListener('mousemove', function(e) {
                if (!isResizing) return;
                var dx = e.clientX - startX;
                var dy = e.clientY - startY;
                popup.style.width = Math.max(280, startWidth + dx) + 'px';
                popup.style.height = Math.max(200, startHeight + dy) + 'px';
            });

            document.addEventListener('mouseup', function() {
                isResizing = false;
            });
        }
    };

    window.AIChatContextHelp = AIChatContextHelp;

})();
