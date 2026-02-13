(function() {
    'use strict';

    var AIChatConfig = {

        providers: {
            anthropic: {
                id: 'anthropic',
                name: 'Claude (Anthropic)',
                logo: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.304 3.541l-5.357 16.918H8.892L3.299 7.057h3.349l3.638 10.98 3.638-10.98h3.38v-3.516zm3.397 0v3.516h-3.397V3.541h3.397z"/></svg>'
            },
            openai: {
                id: 'openai',
                name: 'OpenAI',
                logo: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M22.282 9.821a5.985 5.985 0 0 0-.516-4.91 6.046 6.046 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a5.985 5.985 0 0 0-3.998 2.9 6.046 6.046 0 0 0 .743 7.097 5.98 5.98 0 0 0 .51 4.911 6.051 6.051 0 0 0 6.515 2.9A5.985 5.985 0 0 0 13.26 24a6.056 6.056 0 0 0 5.772-4.206 5.99 5.99 0 0 0 3.997-2.9 6.056 6.056 0 0 0-.747-7.073zM13.26 22.43a4.476 4.476 0 0 1-2.876-1.04l.141-.081 4.779-2.758a.795.795 0 0 0 .392-.681v-6.737l2.02 1.168a.071.071 0 0 1 .038.052v5.583a4.504 4.504 0 0 1-4.494 4.494zM3.6 18.304a4.47 4.47 0 0 1-.535-3.014l.142.085 4.783 2.759a.771.771 0 0 0 .78 0l5.843-3.369v2.332a.08.08 0 0 1-.033.062L9.74 19.95a4.5 4.5 0 0 1-6.14-1.646zM2.34 7.896a4.485 4.485 0 0 1 2.366-1.973V11.6a.766.766 0 0 0 .388.676l5.815 3.355-2.02 1.168a.076.076 0 0 1-.071 0l-4.83-2.786A4.504 4.504 0 0 1 2.34 7.896zm16.597 3.855l-5.833-3.387L15.119 7.2a.076.076 0 0 1 .071 0l4.83 2.791a4.494 4.494 0 0 1-.676 8.105v-5.678a.79.79 0 0 0-.407-.667zm2.01-3.023l-.141-.085-4.774-2.782a.776.776 0 0 0-.785 0L9.409 9.23V6.897a.066.066 0 0 1 .028-.061l4.83-2.787a4.5 4.5 0 0 1 6.68 4.66zm-12.64 4.135l-2.02-1.164a.08.08 0 0 1-.038-.057V6.075a4.5 4.5 0 0 1 7.375-3.453l-.142.08L8.704 5.46a.795.795 0 0 0-.393.681zm1.097-2.365l2.602-1.5 2.607 1.5v2.999l-2.597 1.5-2.607-1.5z"/></svg>'
            }
        },

        configuredKeys: {},
        isLoading: false,
        selectedProvider: null,

        init: function() {
            console.debug('AIChatConfig.init: initializing');
            this.configuredKeys = {};
        },

        checkConfiguredKeys: function(callback) {
            console.debug('AIChatConfig.checkConfiguredKeys: checking keys');
            var self = this;

            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/zato/ai-chat/config/get-keys/', true);
            xhr.setRequestHeader('Content-Type', 'application/json');

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        try {
                            var response = JSON.parse(xhr.responseText);
                            self.configuredKeys = response.keys || {};
                            console.debug('AIChatConfig.checkConfiguredKeys: keys loaded', self.configuredKeys);
                        } catch (e) {
                            console.debug('AIChatConfig.checkConfiguredKeys: parse error', e);
                            self.configuredKeys = {};
                        }
                    } else {
                        console.debug('AIChatConfig.checkConfiguredKeys: request failed', xhr.status);
                        self.configuredKeys = {};
                    }
                    if (callback) {
                        callback(self.hasAnyKey());
                    }
                }
            };

            xhr.send();
        },

        hasAnyKey: function() {
            return this.configuredKeys.anthropic || this.configuredKeys.openai;
        },

        saveKey: function(providerId, apiKey, callback) {
            console.debug('AIChatConfig.saveKey: saving key for', providerId);
            var self = this;

            var csrfToken = this.getCsrfToken();

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/zato/ai-chat/config/save-key/', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            if (csrfToken) {
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
            }

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        try {
                            var response = JSON.parse(xhr.responseText);
                            if (response.success) {
                                self.configuredKeys[providerId] = true;
                                console.debug('AIChatConfig.saveKey: key saved successfully');
                            }
                            if (callback) {
                                callback(response.success);
                            }
                        } catch (e) {
                            console.debug('AIChatConfig.saveKey: parse error', e);
                            if (callback) {
                                callback(false);
                            }
                        }
                    } else {
                        console.debug('AIChatConfig.saveKey: request failed', xhr.status);
                        if (callback) {
                            callback(false);
                        }
                    }
                }
            };

            xhr.send(JSON.stringify({
                provider: providerId,
                api_key: apiKey
            }));
        },

        getCsrfToken: function() {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.indexOf('csrftoken=') === 0) {
                    return cookie.substring('csrftoken='.length);
                }
            }
            return null;
        },

        buildProviderSelectionHtml: function() {
            var html = '<div class="ai-chat-config-container">';
            html += '<div class="ai-chat-config-title">Configure AI provider</div>';
            html += '<div class="ai-chat-config-subtitle">Select a provider and enter your API key</div>';
            html += '<div class="ai-chat-config-providers">';

            for (var key in this.providers) {
                var provider = this.providers[key];
                html += '<div class="ai-chat-config-provider" data-provider-id="' + provider.id + '">';
                html += '<div class="ai-chat-config-provider-logo">' + provider.logo + '</div>';
                html += '<div class="ai-chat-config-provider-name">' + provider.name + '</div>';
                html += '</div>';
            }

            html += '</div>';
            html += '</div>';
            return html;
        },

        buildKeyInputHtml: function(providerId) {
            var provider = this.providers[providerId];
            if (!provider) return '';

            var html = '<div class="ai-chat-config-back" data-action="back">';
            html += '<svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>';
            html += '<span>Back</span>';
            html += '</div>';
            html += '<div class="ai-chat-config-container">';
            html += '<div class="ai-chat-config-provider-header">';
            html += '<div class="ai-chat-config-provider-logo-large">' + provider.logo + '</div>';
            html += '<div class="ai-chat-config-provider-name-large">' + provider.name + '</div>';
            html += '</div>';
            html += '<div class="ai-chat-config-input-wrapper">';
            html += '<input type="text" class="ai-chat-config-api-key-input" placeholder="Paste your API key here" data-provider-id="' + providerId + '">';
            html += '</div>';
            html += '<button class="ai-chat-config-save-button" data-provider-id="' + providerId + '">Save API key</button>';
            html += '</div>';
            return html;
        }
    };

    window.AIChatConfig = AIChatConfig;

})();
