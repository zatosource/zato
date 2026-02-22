(function() {
    'use strict';

    var ZatoIDE = {

        defaultOptions: {
            theme: 'dark',
            language: 'python',
            tabSize: 4,
            lineNumbers: true
        },

        instances: {},

        create: function(containerId, options) {
            var opts = {};
            var key;
            for (key in this.defaultOptions) {
                opts[key] = this.defaultOptions[key];
            }
            for (key in options) {
                opts[key] = options[key];
            }
            var container = document.getElementById(containerId);
            if (!container) {
                console.error('ZatoIDE: container not found:', containerId);
                return null;
            }
            var instance = {
                id: containerId,
                container: container,
                options: opts,
                editor: null,
                codeEditor: null,
                content: '',
                files: {},
                activeFile: null,
                isLoadingContent: false
            };
            ZatoIDELayout.render(instance);
            this.instances[containerId] = instance;
            return instance;
        },

        getInstance: function(containerId) {
            return this.instances[containerId] || null;
        },

        destroy: function(containerId) {
            var instance = this.instances[containerId];
            if (instance) {
                if (instance.codeEditor) {
                    ZatoIDEEditorAce.destroy(instance.codeEditor);
                }
                instance.container.innerHTML = '';
                delete this.instances[containerId];
            }
        },

        getValue: function(instance) {
            if (instance && instance.codeEditor) {
                return ZatoIDEEditorAce.getValue(instance.codeEditor);
            }
            return '';
        },

        setValue: function(instance, value) {
            if (instance && instance.codeEditor) {
                ZatoIDEEditorAce.setValue(instance.codeEditor, value);
                instance.content = value;
            }
        },

        setTheme: function(instance, theme) {
            if (!instance) { return; }
            instance.options.theme = theme;
            var container = instance.container.querySelector('.zato-ide-container');
            if (container) {
                container.className = 'zato-ide-container zato-ide-theme-' + theme;
            }
            if (instance.codeEditor) {
                instance.codeEditor.aceEditor.setTheme(theme === 'dark' ? 'ace/theme/zato-dark' : 'ace/theme/zato');
            }
        },

        setLanguage: function(instance, language) {
            if (instance && instance.codeEditor) {
                ZatoIDEEditorAce.setLanguage(instance.codeEditor, language);
            }
        },

        focus: function(instance) {
            if (instance && instance.codeEditor) {
                ZatoIDEEditorAce.focus(instance.codeEditor);
            }
        },

        switchToFile: function(instance, filename) {
            ZatoIDEEditorSetup.switchToFile(instance, filename);
        },

        closeTab: function(instance, tab) {
            ZatoIDETabs.closeTab(instance, tab);
        },

        openFileFromPath: function(instance, filePath, fileName) {
            ZatoIDETabs.openFileFromPath(instance, filePath, fileName);
        },

        showSaveDialog: function(instance, filename, callbacks) {
            ZatoIDETabs.showSaveDialog(instance, filename, callbacks);
        },

        handleDebugAction: function(instance, action) {
            ZatoIDEDebug.handleDebugAction(instance, action);
        },

        connectToServer: function(instance) {
            ZatoIDEDebug.connectToServer(instance);
        }
    };

    window.ZatoIDE = ZatoIDE;

})();
