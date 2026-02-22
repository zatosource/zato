(function() {
    'use strict';

    var ZatoIDEEditorSetup = {

        initFiles: function(instance) {
            instance.files = {};
            instance.activeFile = null;
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

        initCodeEditor: function(instance) {
            console.log('[ZatoIDE] initCodeEditor: starting, instance.id=' + instance.id);
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
                        var activeFile = instance.files[instance.activeFile];
                        activeFile.content = content;
                        var wasModified = activeFile.modified;
                        activeFile.modified = content !== activeFile.originalContent;
                        if (wasModified !== activeFile.modified) {
                            ZatoIDETabs.updateTabModifiedState(instance, instance.activeFile, activeFile.modified);
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
                        ZatoIDETabs.saveTabsState(instance);
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
                    },
                    getFilePath: function() {
                        var file = instance.files[instance.activeFile];
                        return file ? file.filePath : instance.activeFile;
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
            ZatoIDETabs.syncTabToFile(instance, filename);
            ZatoIDEDropdowns.updateSymbols(instance);
            ZatoIDETabs.saveTabsState(instance);
        }
    };

    window.ZatoIDEEditorSetup = ZatoIDEEditorSetup;

})();
