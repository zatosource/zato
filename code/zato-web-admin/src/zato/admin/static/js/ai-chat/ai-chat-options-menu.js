(function() {
    'use strict';

    var AIChatOptionsMenu = {

        toggle: function(widget, activeTabId, clickedButton) {
            var existing = widget.querySelector('.ai-chat-options-menu');
            if (existing) {
                existing.parentNode.removeChild(existing);
                return;
            }

            var button = clickedButton;
            if (!button) {
                var activePanel = widget.querySelector('.ai-chat-tab-panel[data-tab-id="' + activeTabId + '"]');
                button = activePanel ? activePanel.querySelector('.ai-chat-options-button') : null;
            }
            if (!button) {
                return;
            }

            var menu = document.createElement('div');
            menu.className = 'ai-chat-options-menu';
            menu.innerHTML = '<div class="ai-chat-options-menu-item" data-action="add-files">Add files or images</div>' +
                '<div class="ai-chat-options-menu-separator"></div>' +
                '<div class="ai-chat-options-menu-item" data-action="connect-mcp">Connect MCP server</div>' +
                '<div class="ai-chat-options-menu-separator"></div>' +
                '<div class="ai-chat-options-menu-item" data-action="manage-keys">Manage API keys</div>';

            button.parentNode.style.position = 'relative';
            button.parentNode.appendChild(menu);
        },

        hide: function(widget) {
            var menu = widget.querySelector('.ai-chat-options-menu');
            if (menu) {
                menu.parentNode.removeChild(menu);
            }
        },

        handleAction: function(action, callbacks) {
            if (action === 'manage-keys') {
                callbacks.onManageKeys();
            } else if (action === 'add-files') {
                callbacks.onAddFiles();
            } else if (action === 'connect-mcp') {
                console.debug('AIChatOptionsMenu: connect-mcp not yet implemented');
            }
        },

        showFileDialog: function(activeTabId, renderCallback) {
            var input = document.createElement('input');
            input.type = 'file';
            input.multiple = true;
            input.style.display = 'none';
            input.addEventListener('change', function(e) {
                var files = e.target.files;
                if (files && files.length > 0) {
                    var processed = 0;
                    for (var i = 0; i < files.length; i++) {
                        AIChatAttachments.addFile(files[i], activeTabId, function() {
                            processed++;
                            if (processed === files.length && renderCallback) {
                                renderCallback();
                            }
                        });
                    }
                }
                document.body.removeChild(input);
            });
            document.body.appendChild(input);
            input.click();
        }
    };

    window.AIChatOptionsMenu = AIChatOptionsMenu;

})();
