(function() {
    'use strict';

    var AIChatIDEIntegration = {

        splitInstance: null,
        ideInstance: null,
        enabled: true,
        storageKeyEnabled: 'zato.ai-chat.ide-enabled',

        init: function(widget) {
            this.enabled = this.loadEnabledState();
        },

        loadEnabledState: function() {
            try {
                var saved = localStorage.getItem(this.storageKeyEnabled);
                if (saved !== null) {
                    return saved === 'true';
                }
            } catch (e) {
                console.warn('AIChatIDEIntegration: failed to load enabled state:', e);
            }
            return true;
        },

        saveEnabledState: function(enabled) {
            try {
                localStorage.setItem(this.storageKeyEnabled, enabled.toString());
            } catch (e) {
                console.warn('AIChatIDEIntegration: failed to save enabled state:', e);
            }
        },

        isEnabled: function() {
            return this.enabled;
        },

        setEnabled: function(enabled) {
            this.enabled = enabled;
            this.saveEnabledState(enabled);
        },

        createSplitContainer: function(bodyElement) {
            if (!this.enabled || !window.ZatoIDESplit) {
                return null;
            }

            var splitWrapper = document.createElement('div');
            splitWrapper.id = 'ai-chat-split-wrapper';
            splitWrapper.className = 'ai-chat-split-wrapper';

            bodyElement.appendChild(splitWrapper);

            this.splitInstance = ZatoIDESplit.create('ai-chat-split-wrapper', {
                onResize: function() {
                }
            });

            return this.splitInstance;
        },

        initIDE: function() {
            if (!this.splitInstance || !window.ZatoIDE) {
                return null;
            }

            var idePanel = ZatoIDESplit.getIDEPanel(this.splitInstance);
            if (!idePanel) {
                return null;
            }

            idePanel.id = 'zato-ide-panel';

            this.ideInstance = ZatoIDE.create('zato-ide-panel', {
                theme: 'dark',
                language: 'python'
            });

            return this.ideInstance;
        },

        getChatPanel: function() {
            if (!this.splitInstance) {
                return null;
            }
            return ZatoIDESplit.getChatPanel(this.splitInstance);
        },

        getIDEPanel: function() {
            if (!this.splitInstance) {
                return null;
            }
            return ZatoIDESplit.getIDEPanel(this.splitInstance);
        },

        destroy: function() {
            if (this.ideInstance && window.ZatoIDE) {
                ZatoIDE.destroy(this.ideInstance.id);
                this.ideInstance = null;
            }
            if (this.splitInstance && window.ZatoIDESplit) {
                ZatoIDESplit.destroy(this.splitInstance.id);
                this.splitInstance = null;
            }
        }
    };

    window.AIChatIDEIntegration = AIChatIDEIntegration;

})();
