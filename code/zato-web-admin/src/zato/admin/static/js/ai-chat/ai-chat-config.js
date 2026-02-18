(function() {
    'use strict';

    var AIChatConfig = {

        providers: {
            anthropic: {
                id: 'anthropic',
                name: '<strong>Claude</strong> · Anthropic',
                logo: '<svg viewBox="0 0 1200 1200" fill="#d97757"><path d="M 233.959793 800.214905 L 468.644287 668.536987 L 472.590637 657.100647 L 468.644287 650.738403 L 457.208069 650.738403 L 417.986633 648.322144 L 283.892639 644.69812 L 167.597321 639.865845 L 54.926208 633.825623 L 26.577238 627.785339 L 3.3e-05 592.751709 L 2.73832 575.27533 L 26.577238 559.248352 L 60.724873 562.228149 L 136.187973 567.382629 L 249.422867 575.194763 L 331.570496 580.026978 L 453.261841 592.671082 L 472.590637 592.671082 L 475.328857 584.859009 L 468.724915 580.026978 L 463.570557 575.194763 L 346.389313 495.785217 L 219.543671 411.865906 L 153.100723 363.543762 L 117.181267 339.060425 L 99.060455 316.107361 L 91.248367 266.01355 L 123.865784 230.093994 L 167.677887 233.073853 L 178.872513 236.053772 L 223.248367 270.201477 L 318.040283 343.570496 L 441.825592 434.738342 L 459.946411 449.798706 L 467.194672 444.64447 L 468.080597 441.020203 L 459.946411 427.409485 L 392.617493 305.718323 L 320.778564 181.932983 L 288.80542 130.630859 L 280.348999 99.865845 C 277.369171 87.221436 275.194641 76.590698 275.194641 63.624268 L 312.322174 13.20813 L 332.8591 6.604126 L 382.389313 13.20813 L 403.248352 31.328979 L 434.013519 101.71814 L 483.865753 212.537048 L 561.181274 363.221497 L 583.812134 407.919434 L 595.892639 449.315491 L 600.40271 461.959839 L 608.214783 461.959839 L 608.214783 454.711609 L 614.577271 369.825623 L 626.335632 265.61084 L 637.771851 131.516846 L 641.718201 93.745117 L 660.402832 48.483276 L 697.530334 24.000122 L 726.52356 37.852417 L 750.362549 72 L 747.060486 94.067139 L 732.886047 186.201416 L 705.100708 330.52356 L 686.979919 427.167847 L 697.530334 427.167847 L 709.61084 415.087341 L 758.496704 350.174561 L 840.644348 247.490051 L 876.885925 206.738342 L 919.167847 161.71814 L 946.308838 140.29541 L 997.61084 140.29541 L 1035.38269 196.429626 L 1018.469849 254.416199 L 965.637634 321.422852 L 921.825562 378.201538 L 859.006714 462.765259 L 819.785278 530.41626 L 823.409424 535.812073 L 832.75177 534.92627 L 974.657776 504.724915 L 1051.328979 490.872559 L 1142.818848 475.167786 L 1184.214844 494.496582 L 1188.724854 514.147644 L 1172.456421 554.335693 L 1074.604126 578.496765 L 959.838989 601.449829 L 788.939636 641.879272 L 786.845764 643.409485 L 789.261841 646.389343 L 866.255127 653.637634 L 899.194702 655.409424 L 979.812134 655.409424 L 1129.932861 666.604187 L 1169.154419 692.537109 L 1192.671265 724.268677 L 1188.724854 748.429688 L 1128.322144 779.194641 L 1046.818848 759.865845 L 856.590759 714.604126 L 791.355774 698.335754 L 782.335693 698.335754 L 782.335693 703.731567 L 836.69812 756.885986 L 936.322205 846.845581 L 1061.073975 962.81897 L 1067.436279 991.490112 L 1051.409424 1014.120911 L 1034.496704 1011.704712 L 924.885986 929.234924 L 882.604126 892.107544 L 786.845764 811.48999 L 780.483276 811.48999 L 780.483276 819.946289 L 802.550415 852.241699 L 919.087341 1027.409424 L 925.127625 1081.127686 L 916.671204 1098.604126 L 886.469849 1109.154419 L 853.288696 1103.114136 L 785.073914 1007.355835 L 714.684631 899.516785 L 657.906067 802.872498 L 650.979858 806.81897 L 617.476624 1167.704834 L 601.771851 1186.147705 L 565.530212 1200 L 535.328857 1177.046997 L 519.302124 1139.919556 L 535.328857 1066.550537 L 554.657776 970.792053 L 570.362488 894.68457 L 584.536926 800.134277 L 592.993347 768.724976 L 592.429626 766.630859 L 585.503479 767.516968 L 514.22821 865.369263 L 405.825531 1011.865906 L 320.053711 1103.677979 L 299.516815 1111.812256 L 263.919525 1093.369263 L 267.221497 1060.429688 L 287.114136 1031.114136 L 405.825531 880.107361 L 477.422913 786.52356 L 523.651062 732.483276 L 523.328918 724.671265 L 520.590698 724.671265 L 205.288605 929.395935 L 149.154434 936.644409 L 124.993355 914.01355 L 127.973183 876.885986 L 139.409409 864.80542 L 234.201385 799.570435 L 233.879227 799.8927 Z"/></svg>'
            },
            openai: {
                id: 'openai',
                name: '<strong>GPT</strong> · OpenAI',
                logo: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M22.282 9.821a5.985 5.985 0 0 0-.516-4.91 6.046 6.046 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a5.985 5.985 0 0 0-3.998 2.9 6.046 6.046 0 0 0 .743 7.097 5.98 5.98 0 0 0 .51 4.911 6.051 6.051 0 0 0 6.515 2.9A5.985 5.985 0 0 0 13.26 24a6.056 6.056 0 0 0 5.772-4.206 5.99 5.99 0 0 0 3.997-2.9 6.056 6.056 0 0 0-.747-7.073zM13.26 22.43a4.476 4.476 0 0 1-2.876-1.04l.141-.081 4.779-2.758a.795.795 0 0 0 .392-.681v-6.737l2.02 1.168a.071.071 0 0 1 .038.052v5.583a4.504 4.504 0 0 1-4.494 4.494zM3.6 18.304a4.47 4.47 0 0 1-.535-3.014l.142.085 4.783 2.759a.771.771 0 0 0 .78 0l5.843-3.369v2.332a.08.08 0 0 1-.033.062L9.74 19.95a4.5 4.5 0 0 1-6.14-1.646zM2.34 7.896a4.485 4.485 0 0 1 2.366-1.973V11.6a.766.766 0 0 0 .388.676l5.815 3.355-2.02 1.168a.076.076 0 0 1-.071 0l-4.83-2.786A4.504 4.504 0 0 1 2.34 7.896zm16.597 3.855l-5.833-3.387L15.119 7.2a.076.076 0 0 1 .071 0l4.83 2.791a4.494 4.494 0 0 1-.676 8.105v-5.678a.79.79 0 0 0-.407-.667zm2.01-3.023l-.141-.085-4.774-2.782a.776.776 0 0 0-.785 0L9.409 9.23V6.897a.066.066 0 0 1 .028-.061l4.83-2.787a4.5 4.5 0 0 1 6.68 4.66zm-12.64 4.135l-2.02-1.164a.08.08 0 0 1-.038-.057V6.075a4.5 4.5 0 0 1 7.375-3.453l-.142.08L8.704 5.46a.795.795 0 0 0-.393.681zm1.097-2.365 2.602-1.5 2.607 1.5v2.999l-2.597 1.5-2.607-1.5z"/></svg>'
            },
            google: {
                id: 'google',
                name: '<strong>Gemini</strong> · Google',
                logo: '<svg viewBox="0 0 24 24" fill="url(#gemini-gradient)"><defs><linearGradient id="gemini-gradient" x1="0%" y1="100%" x2="100%" y2="0%"><stop offset="0%" stop-color="#1a73e8"/><stop offset="50%" stop-color="#6c47ff"/><stop offset="100%" stop-color="#f28b82"/></linearGradient></defs><path d="M12 0c.3 0 .55.2.62.49a16.8 16.8 0 00.86 2.55c.93 2.16 2.2 4.05 3.82 5.67 1.62 1.62 3.51 2.9 5.67 3.83.85.37 1.72.67 2.55.86.29.07.48.32.48.62s-.2.55-.49.62a16.8 16.8 0 00-2.55.86c-2.16.93-4.05 2.2-5.67 3.82-1.62 1.62-2.9 3.51-3.82 5.67-.37.85-.67 1.72-.86 2.55-.07.29-.32.48-.62.48s-.55-.2-.62-.49a16.8 16.8 0 00-.86-2.55c-.93-2.16-2.2-4.05-3.82-5.67-1.62-1.62-3.51-2.9-5.67-3.82a16.8 16.8 0 00-2.55-.86A.64.64 0 010 12c0-.3.2-.55.49-.62a16.8 16.8 0 002.55-.86c2.16-.93 4.05-2.2 5.67-3.82 1.62-1.62 2.9-3.51 3.83-5.67.36-.85.66-1.72.85-2.55A.64.64 0 0112 0z"/></svg>'
            },
        },

        configuredKeys: {},
        isLoading: false,
        selectedProvider: null,
        models: {},
        selectedModel: null,

        buildBackButtonHtml: function(id) {
            var html = '<div class="ai-chat-config-back"';
            if (id) {
                html += ' id="' + id + '"';
            }
            html += '>';
            html += '<svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>';
            html += '<span>Back</span>';
            html += '</div>';
            return html;
        },

        wrapWithBackButton: function(id, contentHtml) {
            var html = '<div class="ai-chat-config-content-wrapper">';
            html += this.buildBackButtonHtml(id);
            html += contentHtml;
            html += '</div>';
            return html;
        },

        init: function() {
            this.configuredKeys = {};
            this.models = {};
            this.loadModels();
        },

        loadModels: function() {
            var self = this;

            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/zato/ai-chat/config/get-models/', true);
            xhr.setRequestHeader('Content-Type', 'application/json');

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        try {
                            self.models = JSON.parse(xhr.responseText);
                        } catch (e) {
                            self.models = {};
                        }
                    } else {
                        self.models = {};
                    }
                }
            };

            xhr.send();
        },

        getModelsForConfiguredProviders: function() {
            var result = [];
            var providerOrder = ['anthropic', 'openai', 'google'];
            for (var p = 0; p < providerOrder.length; p++) {
                var provider = providerOrder[p];
                if (this.models[provider]) {
                    for (var i = 0; i < this.models[provider].length; i++) {
                        var model = this.models[provider][i];
                        model.provider = provider;
                        model.isFirst = (i === 0 && p > 0);
                        model.disabled = !this.configuredKeys[provider];
                        result.push(model);
                    }
                }
            }
            return result;
        },

        checkConfiguredKeys: function(callback) {
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
                        } catch (e) {
                            self.configuredKeys = {};
                        }
                    } else {
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
            return this.configuredKeys.anthropic || this.configuredKeys.openai || this.configuredKeys.google;
        },

        saveKey: function(providerId, apiKey, callback) {
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
                            }
                            if (callback) {
                                callback(response.success);
                            }
                        } catch (e) {
                            if (callback) {
                                callback(false);
                            }
                        }
                    } else {
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

        deleteKey: function(providerId, callback) {
            var self = this;

            var csrfToken = this.getCsrfToken();

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/zato/ai-chat/config/delete-key/', true);
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
                                self.configuredKeys[providerId] = false;
                            }
                            if (callback) {
                                callback(response.success);
                            }
                        } catch (e) {
                            if (callback) {
                                callback(false);
                            }
                        }
                    } else {
                        if (callback) {
                            callback(false);
                        }
                    }
                }
            };

            xhr.send(JSON.stringify({
                provider: providerId
            }));
        },

        buildProviderSelectionHtml: function(showBackButton) {
            var html = '';
            html += '<div class="ai-chat-config-container">';
            html += '<div class="ai-chat-config-content-wrapper ai-chat-config-content-wrapper-providers">';
            if (showBackButton) {
                html += this.buildBackButtonHtml();
            }
            html += '<div class="ai-chat-config-title">Configure your AI providers</div>';
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
            html += '</div>';
            return html;
        },

        buildKeyInputHtml: function(providerId, hadKeyOnEntry) {
            var provider = this.providers[providerId];
            if (!provider) return '';

            var html = '';
            html += '<div class="ai-chat-config-container">';
            html += '<div class="ai-chat-config-content-wrapper ai-chat-config-content-wrapper-key-input">';
            html += this.buildBackButtonHtml();
            html += '<div class="ai-chat-config-provider-header">';
            html += '<div class="ai-chat-config-provider-logo-large">' + provider.logo + '</div>';
            html += '<div class="ai-chat-config-provider-name-large">' + provider.name + '</div>';
            html += '</div>';
            html += '<div class="ai-chat-config-input-wrapper">';
            html += '<input type="text" class="ai-chat-config-api-key-input" placeholder="Paste your API key here" data-provider-id="' + providerId + '" tabindex="0" autofocus>';
            html += '</div>';
            html += '<button class="ai-chat-config-save-button" data-provider-id="' + providerId + '">Save API key</button>';
            html += '</div>';
            html += '</div>';
            return html;
        },

        buildSettingsMenuHtml: function(hasKey) {
            var html = '<div class="ai-chat-settings-menu">';
            if (hasKey) {
                html += '<div class="ai-chat-settings-menu-item" data-action="manage-keys">';
                html += '<span>Manage API keys</span>';
                html += '</div>';
            } else {
                html += '<div class="ai-chat-settings-menu-item" data-action="change-provider">';
                html += '<span>Configure provider</span>';
                html += '</div>';
            }
            html += '</div>';
            return html;
        },

        buildManageKeysHtml: function(cameFromChat) {
            var html = '';
            html += '<div class="ai-chat-config-container">';
            html += '<div class="ai-chat-config-content-wrapper">';
            if (cameFromChat) {
                html += this.buildBackButtonHtml();
            }
            html += '<div class="ai-chat-config-title">Manage API keys</div>';
            html += '<div class="ai-chat-config-keys-list">';

            for (var key in this.providers) {
                var provider = this.providers[key];
                var isConfigured = this.configuredKeys[key];
                html += '<div class="ai-chat-config-key-row" data-provider-id="' + key + '">';
                html += '<div class="ai-chat-config-key-info">';
                html += '<div class="ai-chat-config-key-logo">' + provider.logo + '</div>';
                html += '<div class="ai-chat-config-key-provider">' + provider.name + '</div>';
                html += '</div>';
                html += '<div class="ai-chat-config-key-actions">';
                if (isConfigured) {
                    html += ZatoConfirmButton.buildEditHtml(key, 'ai-chat-config-key-edit');
                    html += ZatoConfirmButton.buildRemoveHtml(key, 'ai-chat-config-key-remove');
                } else {
                    html += '<button class="zato-confirm-btn ai-chat-config-key-add" data-item-id="' + key + '"><span class="zato-confirm-text">Add</span></button>';
                }
                html += '</div>';
                html += '</div>';
            }

            html += '</div>';
            html += '</div>';
            html += '</div>';
            return html;
        }
    };

    window.AIChatConfig = AIChatConfig;

})();
