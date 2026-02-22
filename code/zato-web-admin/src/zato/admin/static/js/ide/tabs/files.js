(function() {
    'use strict';

    ZatoIDETabs.restoreFilesFromTabs = function(instance, tabs) {
        var self = this;
        tabs.forEach(function(tab) {
            if (tab.filePath && !instance.files[tab.title]) {
                instance.files[tab.title] = {
                    content: tab.content || '',
                    originalContent: tab.content || '',
                    language: tab.language || 'text',
                    filePath: tab.filePath,
                    modified: false,
                    cursorLine: tab.cursorLine || 1,
                    cursorCol: tab.cursorCol || 1,
                    scrollLine: tab.scrollLine !== undefined ? tab.scrollLine : null
                };
                if (tab.content === undefined && tab.filePath) {
                    self.loadFileContent(instance, tab.filePath, tab.title);
                }
            }
        });
    };

    ZatoIDETabs.loadFileContent = function(instance, filePath, fileName) {
        var self = this;
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/zato/ide/explorer/read/?path=' + encodeURIComponent(filePath), true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success && instance.files[fileName]) {
                    var file = instance.files[fileName];
                    var savedCursorLine = file.cursorLine;
                    var savedCursorCol = file.cursorCol;

                    file.content = response.content;
                    file.originalContent = response.content;

                    if (instance.activeFile === fileName && instance.codeEditor) {
                        var savedScrollLine = file.scrollLine;
                        instance.isLoadingContent = true;
                        ZatoIDEEditorAce.setValue(instance.codeEditor, response.content);
                        var aceEditor = instance.codeEditor.aceEditor;
                        if (aceEditor) {
                            requestAnimationFrame(function() {
                                requestAnimationFrame(function() {
                                    file.cursorLine = savedCursorLine;
                                    file.cursorCol = savedCursorCol;
                                    if (instance.activeFile === fileName) {
                                        aceEditor.resize(true);
                                        if (savedScrollLine !== null) {
                                            aceEditor.moveCursorTo((savedCursorLine || 1) - 1, (savedCursorCol || 1) - 1);
                                            aceEditor.scrollToRow(savedScrollLine);
                                        } else if (savedCursorLine) {
                                            aceEditor.gotoLine(savedCursorLine, (savedCursorCol || 1) - 1, false);
                                        }
                                    }
                                    instance.isLoadingContent = false;
                                });
                            });
                        } else {
                            file.cursorLine = savedCursorLine;
                            file.cursorCol = savedCursorCol;
                            instance.isLoadingContent = false;
                        }
                    }
                }
            }
        };
        xhr.send();
    };

    ZatoIDETabs.openFileFromPath = function(instance, filePath, fileName) {
        var self = this;
        var existingTab = this.findTabByPath(instance, filePath);
        if (existingTab) {
            this.switchToTab(instance, existingTab.id);
            return;
        }
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/zato/ide/explorer/read/?path=' + encodeURIComponent(filePath), true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    if (response.success) {
                        self.openFileInNewTab(instance, filePath, fileName, response.content);
                    }
                }
            }
        };
        xhr.send();
    };

    ZatoIDETabs.openFileInNewTab = function(instance, filePath, fileName, content) {
        var tabId = 'file-' + Date.now();
        var language = 'text';
        if (typeof ZatoIDEEditorAce !== 'undefined') {
            language = ZatoIDEEditorAce.getLanguageFromExtension(fileName);
        }

        var newTab = {
            id: tabId,
            title: fileName,
            filePath: filePath,
            language: language
        };

        if (!instance.tabsManager.tabs) {
            instance.tabsManager.tabs = [];
        }
        instance.tabsManager.tabs.push(newTab);

        if (!instance.files) {
            instance.files = {};
        }
        instance.files[fileName] = {
            content: content,
            originalContent: content,
            language: language,
            filePath: filePath,
            modified: false,
            cursorLine: 1,
            cursorCol: 1
        };

        this.renderTabs(instance);
        this.bindTabEvents(instance);
        this.switchToTab(instance, tabId);
        this.saveTabsState(instance);
    };

})();
