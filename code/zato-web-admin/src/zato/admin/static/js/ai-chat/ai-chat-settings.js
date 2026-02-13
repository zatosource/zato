(function() {
    'use strict';

    var AIChatSettings = {
        menu: null,

        showMenu: function(widget) {
            this.hideMenu();

            var header = widget.querySelector('.ai-chat-header');
            if (!header) return;

            var menuWrapper = document.createElement('div');
            menuWrapper.innerHTML = AIChatConfig.buildSettingsMenuHtml(AIChatConfig.hasAnyKey());
            menuWrapper.firstChild.style.position = 'absolute';
            menuWrapper.firstChild.style.top = (header.offsetHeight + 4) + 'px';
            menuWrapper.firstChild.style.left = '12px';

            widget.appendChild(menuWrapper.firstChild);
            this.menu = widget.querySelector('.ai-chat-settings-menu');
        },

        hideMenu: function() {
            if (this.menu && this.menu.parentNode) {
                this.menu.parentNode.removeChild(this.menu);
                this.menu = null;
            }
        },

        handleAction: function(action, providerId, callbacks) {
            this.hideMenu();

            var hadKeyOnEntry = AIChatConfig.hasAnyKey();

            if (action === 'change-provider') {
                callbacks.onChangeProvider(hadKeyOnEntry);
            } else if (action === 'manage-keys') {
                callbacks.onManageKeys(hadKeyOnEntry);
            }
        },

        showKeyInput: function(widget, providerId, renderCallback) {
            AIChatConfig.selectedProvider = providerId;
            renderCallback();
            
            requestAnimationFrame(function() {
                requestAnimationFrame(function() {
                    var apiKeyInput = widget.querySelector('.ai-chat-config-api-key-input');
                    if (apiKeyInput) {
                        apiKeyInput.focus();
                    }
                });
            });
        },

        saveApiKey: function(widget, providerId, successCallback, errorCallback) {
            var input = widget.querySelector('.ai-chat-config-api-key-input[data-provider-id="' + providerId + '"]');
            if (!input) {
                return;
            }

            var apiKey = input.value.trim();
            if (!apiKey) {
                return;
            }

            var saveButton = widget.querySelector('.ai-chat-config-save-button');
            if (saveButton) {
                saveButton.disabled = true;
                saveButton.textContent = 'Saving...';
            }

            AIChatConfig.saveKey(providerId, apiKey, function(success) {
                if (success) {
                    successCallback();
                } else {
                    if (saveButton) {
                        saveButton.disabled = false;
                        saveButton.textContent = 'Save API key';
                    }
                    if (errorCallback) errorCallback();
                }
            });
        },

        showConfigSuccess: function(widget, renderCallback) {
            var messagesContainer = widget.querySelector('.ai-chat-messages');
            if (messagesContainer) {
                var html = '<div class="ai-chat-config-container">';
                html += '<div class="ai-chat-config-success">';
                html += '<div class="ai-chat-config-success-icon">';
                html += '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>';
                html += '</div>';
                html += '<div class="ai-chat-config-success-text">API key saved</div>';
                html += '</div>';
                html += '</div>';
                messagesContainer.innerHTML = html;

                var transitionDelay = 800;
                var startTime = Date.now();
                var checkAndRender = function() {
                    if (Date.now() - startTime >= transitionDelay) {
                        renderCallback();
                    } else {
                        requestAnimationFrame(checkAndRender);
                    }
                };
                requestAnimationFrame(checkAndRender);
            }
        },

        removeApiKey: function(providerId, callbacks) {
            AIChatConfig.deleteKey(providerId, function(success) {
                if (success) {
                    if (!AIChatConfig.hasAnyKey()) {
                        callbacks.onNoKeysLeft();
                    }
                    callbacks.onSuccess();
                }
            });
        },

        handleBackClick: function(configMode, cameFromChat, hadKeyOnEntry, callbacks) {
            if (configMode === 'key-input') {
                if (hadKeyOnEntry) {
                    callbacks.onReturnToChat();
                } else {
                    callbacks.onShowProviders();
                }
            } else if (configMode === 'manage-keys') {
                callbacks.onReturnToChat();
            } else if (configMode === 'providers' && cameFromChat && hadKeyOnEntry) {
                callbacks.onReturnToChat();
            }
        }
    };

    window.AIChatSettings = AIChatSettings;

})();
