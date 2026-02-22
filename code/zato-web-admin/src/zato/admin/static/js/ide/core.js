(function() {
    'use strict';

    var ZatoIDE = {

        defaultOptions: {
            theme: 'dark',
            language: 'python',
            tabSize: 4,
            lineNumbers: true
        },

        storageKeys: {
            tabs: 'zato.ide.tabs',
            activeTab: 'zato.ide.active-tab',
            closedTabsHistory: 'zato.ide.closed-tabs-history',
            cursorPositions: 'zato.ide.cursor-positions'
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
            this.render(instance);
            this.instances[containerId] = instance;
            return instance;
        },

        render: function(instance) {
            var themeClass = 'zato-ide-theme-' + instance.options.theme;
            var html = '';
            html += '<div class="zato-ide-container ' + themeClass + '">';
            html += '<div class="zato-ide-toolbar">';
            html += '<div class="zato-ide-toolbar-left">';
            html += '<select id="' + instance.id + '-symbol-select" class="zato-ide-symbol-select"><option value="">-- symbols --</option></select>';
            html += '<select id="' + instance.id + '-method-select" class="zato-ide-method-select" style="display: none;"><option value="">-- methods --</option></select>';
            html += '</div>';
            html += '<div class="zato-ide-toolbar-center">';
            html += '<div class="zato-ide-debug-container" id="' + instance.id + '-debug-container">';
            html += '<select class="zato-ide-debug-select zato-ide-symbol-select" id="' + instance.id + '-debug-select">';
            html += '<option value="">Debug</option>';
            html += '<option value="debug-file">Debug current file</option>';
            html += '<option value="connect-server">Connect to server</option>';
            html += '</select>';
            html += '</div>';
            html += '<span class="zato-ide-toolbar-separator"></span>';
            html += '<span class="zato-ide-search-button" title="Search"></span>';
            html += '</div></div>';
            html += '<div class="zato-ide-tabs-area"><div id="' + instance.id + '-tabs"></div></div>';
            html += '<div class="zato-ide-main-area" id="' + instance.id + '-main-split"></div>';
            html += '<div class="zato-ide-statusbar" id="' + instance.id + '-statusbar"></div>';
            html += '</div>';
            instance.container.innerHTML = html;

            console.log('[ZatoIDE] render: container set, initializing main split');
            ZatoIDEPanels.initMainSplit(instance);
            console.log('[ZatoIDE] render: main split initialized, initializing files');
            this.initFiles(instance);
            console.log('[ZatoIDE] render: files initialized, initializing code editor');
            this.initCodeEditor(instance);
            console.log('[ZatoIDE] render: code editor initialized');

            ZatoIDEDropdowns.initDropdowns(instance);

            console.log('[ZatoIDE] render: initializing tabs');
            this.initTabs(instance);

            ZatoIDEPanels.loadSearchIcon(instance);
            ZatoIDEPanels.loadSidePanel1Icons(instance);
            ZatoIDEPanels.initSidePanel1Content(instance);

            this.bindEvents(instance);

            var activeTab = this.getActiveTab(instance);
            if (activeTab && activeTab.title) {
                console.log('[ZatoIDE] render: switching to initial file ' + activeTab.title);
                this.switchToFile(instance, activeTab.title);
            }
            console.log('[ZatoIDE] render: complete');
        },

        getActiveTab: function(instance) {
            if (!instance.tabsManager || !instance.tabsManager.tabs) {
                return null;
            }
            var activeTabId = instance.tabsManager.activeTabId;
            for (var i = 0; i < instance.tabsManager.tabs.length; i++) {
                if (instance.tabsManager.tabs[i].id === activeTabId) {
                    return instance.tabsManager.tabs[i];
                }
            }
            return instance.tabsManager.tabs[0] || null;
        },

        initFiles: function(instance) {
            instance.files = {};
            instance.activeFile = null;
        },

        initCodeEditor: function(instance) {
            console.log('[ZatoIDE] initCodeEditor: starting, instance.id=' + instance.id);
            var self = this;
            var editorArea = document.getElementById(instance.id + '-editor-area');
            if (!editorArea) {
                console.log('[ZatoIDE] initCodeEditor: editor area not found, id=' + instance.id + '-editor-area');
                return;
            }
            console.log('[ZatoIDE] initCodeEditor: editor area found');
            if (typeof ZatoIDEEditorAce === 'undefined') {
                console.log('[ZatoIDE] initCodeEditor: ZatoIDEEditorAce is undefined, editor JS not loaded');
                return;
            }
            console.log('[ZatoIDE] initCodeEditor: ZatoIDEEditorAce is available');
            var file = instance.files[instance.activeFile];
            console.log('[ZatoIDE] initCodeEditor: creating editor, activeFile=' + instance.activeFile + ', language=' + (file ? file.language : 'none'));
            var editorOptions = {
                theme: instance.options.theme,
                language: file ? file.language : 'python',
                tabSize: instance.options.tabSize,
                content: file ? file.content : '',
                ideContainerId: instance.id,
                onContentChange: function(content) {
                    if (instance.activeFile && instance.files[instance.activeFile]) {
                        var file = instance.files[instance.activeFile];
                        file.content = content;
                        var wasModified = file.modified;
                        file.modified = content !== file.originalContent;
                        if (wasModified !== file.modified) {
                            self.updateTabModifiedState(instance, instance.activeFile, file.modified);
                        }
                    }
                    instance.content = content;
                },
                onCursorChange: function(line, col) {
                    ZatoIDEDropdowns.syncDropdownsToLine(instance, line);
                    if (instance.activeFile && instance.files[instance.activeFile] && !instance.isLoadingContent) {
                        instance.files[instance.activeFile].cursorLine = line;
                        instance.files[instance.activeFile].cursorCol = col;
                    }
                },
                onScrollChange: function(firstVisibleRow) {
                    if (instance.activeFile && instance.files[instance.activeFile] && !instance.isLoadingContent) {
                        instance.files[instance.activeFile].scrollLine = firstVisibleRow;
                        self.saveTabsState(instance);
                    }
                }
            };
            if (instance.options.fontSize) {
                editorOptions.fontSize = instance.options.fontSize;
            }
            instance.codeEditor = ZatoIDEEditorAce.create(editorArea, editorOptions);
            if (typeof ZatoDebuggerGutter !== 'undefined' && instance.codeEditor && instance.codeEditor.aceEditor) {
                instance.gutterInstance = ZatoDebuggerGutter.create(instance.codeEditor.aceEditor, null, {
                    getFilename: function() {
                        return instance.activeFile || 'untitled.py';
                    }
                });
            }
        },

        switchToFile: function(instance, filename) {
            if (!instance.files[filename]) {
                return;
            }
            if (instance.activeFile && instance.codeEditor) {
                instance.files[instance.activeFile].content = ZatoIDEEditorAce.getValue(instance.codeEditor);
                var cursorPos = ZatoIDEEditorAce.getCursorPosition(instance.codeEditor);
                instance.files[instance.activeFile].cursorLine = cursorPos.line;
                instance.files[instance.activeFile].cursorCol = cursorPos.col;
                var prevAceEditor = instance.codeEditor.aceEditor;
                if (prevAceEditor) {
                    instance.files[instance.activeFile].scrollLine = prevAceEditor.getFirstVisibleRow();
                }
            }
            instance.activeFile = filename;
            var file = instance.files[filename];
            if (instance.codeEditor) {
                var savedCursorLine = file.cursorLine;
                var savedCursorCol = file.cursorCol;
                var savedScrollLine = file.scrollLine;
                instance.isLoadingContent = true;
                ZatoIDEEditorAce.setLanguage(instance.codeEditor, file.language);
                ZatoIDEEditorAce.setValue(instance.codeEditor, file.content);
                if (file.content) {
                    var aceEditor = instance.codeEditor.aceEditor;
                    if (aceEditor) {
                        if (savedScrollLine !== null) {
                            aceEditor.moveCursorTo((savedCursorLine || 1) - 1, (savedCursorCol || 1) - 1);
                            aceEditor.scrollToRow(savedScrollLine);
                        } else if (savedCursorLine) {
                            aceEditor.gotoLine(savedCursorLine, (savedCursorCol || 1) - 1, false);
                        }
                    }
                }
                file.cursorLine = savedCursorLine;
                file.cursorCol = savedCursorCol;
                instance.isLoadingContent = false;
            }
            this.syncTabToFile(instance, filename);
            ZatoIDEDropdowns.updateSymbols(instance);
            this.saveTabsState(instance);
        },

        bindEvents: function(instance) {
            var self = this;
            var searchButton = instance.container.querySelector('.zato-ide-search-button');
            if (searchButton) {
                searchButton.addEventListener('click', function(e) {
                    e.stopPropagation();
                    ZatoIDEPanels.toggleSearchPopup(instance, searchButton);
                });
            }
            document.addEventListener('click', function(e) {
                var popup = instance.container.querySelector('.zato-ide-search-popup');
                if (popup && popup.classList.contains('open')) {
                    if (!popup.contains(e.target) && !searchButton.contains(e.target)) {
                        popup.classList.remove('open');
                    }
                }
            });
            window.addEventListener('beforeunload', function() {
                if (instance.activeFile && instance.codeEditor) {
                    var cursorPos = ZatoIDEEditorAce.getCursorPosition(instance.codeEditor);
                    instance.files[instance.activeFile].cursorLine = cursorPos.line;
                    instance.files[instance.activeFile].cursorCol = cursorPos.col;
                }
                self.saveTabsState(instance);
            });
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

        initTabs: function(instance) {
            ZatoIDETabs.initTabs(instance);
        },

        renderTabs: function(instance) {
            ZatoIDETabs.renderTabs(instance);
        },

        bindTabEvents: function(instance) {
            ZatoIDETabs.bindTabEvents(instance);
        },

        switchToTab: function(instance, tabId) {
            ZatoIDETabs.switchToTab(instance, tabId);
        },

        closeTab: function(instance, tab) {
            ZatoIDETabs.closeTab(instance, tab);
        },

        syncTabToFile: function(instance, filename) {
            ZatoIDETabs.syncTabToFile(instance, filename);
        },

        updateTabModifiedState: function(instance, filename, modified) {
            ZatoIDETabs.updateTabModifiedState(instance, filename, modified);
        },

        saveTabsState: function(instance) {
            ZatoIDETabs.saveTabsState(instance);
        },

        loadTabsState: function() {
            return ZatoIDETabs.loadTabsState();
        },

        findTabByPath: function(instance, filePath) {
            return ZatoIDETabs.findTabByPath(instance, filePath);
        },

        openFileInNewTab: function(instance, filePath, fileName, content) {
            ZatoIDETabs.openFileInNewTab(instance, filePath, fileName, content);
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
