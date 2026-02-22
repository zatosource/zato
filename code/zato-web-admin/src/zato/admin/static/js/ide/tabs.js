(function() {
    'use strict';

    var ZatoIDETabs = {

        storageKeys: {
            tabs: 'zato.ide.tabs'
        },

        initTabs: function(instance) {
            if (typeof ZatoTabsManager === 'undefined') {
                return;
            }

            var tabsContainerId = instance.id + '-tabs';
            instance.tabsManager = ZatoTabsManager.create(tabsContainerId, {
                theme: instance.options.theme,
                onTabChange: function(tab) {
                    if (instance.onTabChange) {
                        instance.onTabChange(tab);
                    }
                }
            });

            var savedState = this.loadTabsState();
            var files;
            var activeTabId;

            if (savedState && savedState.tabs && savedState.tabs.length > 0) {
                files = savedState.tabs;
                activeTabId = savedState.activeTabId || files[0].id;
                instance.closedTabsHistory = savedState.closedTabsHistory || [];
                this.restoreFilesFromTabs(instance, files);
            } else {
                files = [];
                activeTabId = null;
                instance.closedTabsHistory = [];
            }

            instance.tabsManager.tabs = files;
            instance.tabsManager.activeTabId = activeTabId;
            instance.tabsManager.allowCloseLastTab = true;
            instance.tabsManager.container = document.getElementById(tabsContainerId);

            this.renderTabs(instance);
            this.bindTabEvents(instance);
        },

        restoreFilesFromTabs: function(instance, tabs) {
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
        },

        loadFileContent: function(instance, filePath, fileName) {
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
        },

        saveTabsState: function(instance) {
            if (!instance.tabsManager) {
                return;
            }

            var tabs = instance.tabsManager.tabs.map(function(tab) {
                var file = instance.files[tab.title];
                var tabData = {
                    id: tab.id,
                    title: tab.title,
                    filePath: tab.filePath || (file ? file.filePath : null),
                    language: tab.language || (file ? file.language : 'text')
                };
                tabData.cursorLine = file ? (file.cursorLine || 1) : 1;
                tabData.cursorCol = file ? (file.cursorCol || 1) : 1;
                tabData.scrollLine = file ? (file.scrollLine !== undefined ? file.scrollLine : null) : null;
                return tabData;
            });

            var state = {
                tabs: tabs,
                activeTabId: instance.tabsManager.activeTabId,
                closedTabsHistory: instance.closedTabsHistory || [],
                timestamp: Date.now()
            };

            try {
                localStorage.setItem(this.storageKeys.tabs, JSON.stringify(state));
            } catch (e) {
                console.warn('[ZatoIDE] Failed to save tabs state:', e);
            }
        },

        loadTabsState: function() {
            try {
                var stored = localStorage.getItem(this.storageKeys.tabs);
                if (stored) {
                    return JSON.parse(stored);
                }
            } catch (e) {
                console.warn('[ZatoIDE] Failed to load tabs state:', e);
            }
            return null;
        },

        saveCursorPosition: function(instance, fileName, line, col) {
            if (!instance.files[fileName]) {
                return;
            }
            instance.files[fileName].cursorLine = line;
            instance.files[fileName].cursorCol = col;
            this.saveTabsState(instance);
        },

        renderTabs: function(instance) {
            if (!instance.tabsManager || !instance.tabsManager.container) {
                return;
            }

            var tabsInstance = {
                containerId: instance.id + '-tabs',
                tabs: instance.tabsManager.tabs,
                activeTabId: instance.tabsManager.activeTabId,
                allowCloseLastTab: instance.tabsManager.allowCloseLastTab,
                theme: instance.options.theme,
                closedTabsHistory: instance.closedTabsHistory || [],
                clearedMessagesBuffer: instance.clearedMessagesBuffer || {}
            };

            var options = {
                theme: instance.options.theme,
                showAddButton: true,
                showCloseButton: true,
                showPinIcon: true,
                showLockIcon: true,
                addButtonTitle: 'New file',
                containerClass: 'zato-ide-tabs'
            };

            var html = ZatoTabsRenderer.buildTabsHtml(tabsInstance, options);
            instance.tabsManager.container.innerHTML = html;
        },

        bindTabEvents: function(instance) {
            var self = this;
            var container = instance.tabsManager.container;
            if (!container) {
                return;
            }

            if (!instance.closedTabsHistory) {
                instance.closedTabsHistory = [];
            }
            if (!instance.clearedMessagesBuffer) {
                instance.clearedMessagesBuffer = {};
            }

            var tabsInstance = {
                containerId: instance.id + '-tabs',
                tabs: instance.tabsManager.tabs,
                activeTabId: instance.tabsManager.activeTabId,
                allowCloseLastTab: instance.tabsManager.allowCloseLastTab,
                theme: instance.options.theme,
                closedTabsHistory: instance.closedTabsHistory,
                clearedMessagesBuffer: instance.clearedMessagesBuffer
            };

            var callbacks = {
                onTabChange: function(tab) {
                    if (tab && tab.title) {
                        if (!instance.files[tab.title]) {
                            var lang = 'text';
                            if (typeof ZatoIDEEditorAce !== 'undefined') {
                                lang = ZatoIDEEditorAce.getLanguageFromExtension(tab.title);
                            }
                            instance.files[tab.title] = {
                                content: '',
                                originalContent: '',
                                language: lang,
                                modified: false
                            };
                        }
                        ZatoIDE.switchToFile(instance, tab.title);
                    }
                    if (instance.onTabChange) {
                        instance.onTabChange(tab);
                    }
                },
                onSave: function() {
                },
                onRender: function() {
                    instance.tabsManager.activeTabId = tabsInstance.activeTabId;
                    instance.tabsManager.tabs = tabsInstance.tabs;
                    self.renderTabs(instance);
                },
                createTabData: function(tabNumber) {
                    return {
                        title: 'file-' + tabNumber + '.py'
                    };
                },
                onBeforeClose: function(tab, doClose) {
                    var filename = tab.title;
                    var file = instance.files[filename];
                    if (file && file.modified) {
                        var contentTrimmed = (file.content || '').trim();
                        if (contentTrimmed === '') {
                            file.content = '';
                            file.modified = false;
                            doClose();
                            return;
                        }
                        ZatoIDE.showSaveDialog(instance, filename, {
                            onDontSave: function() {
                                file.modified = false;
                                doClose();
                            },
                            onCancel: function() {
                            },
                            onSave: function() {
                                file.originalContent = file.content;
                                file.modified = false;
                                doClose();
                            }
                        });
                    } else {
                        doClose();
                    }
                },
                onAddToClosedHistory: function(tab) {
                    var file = instance.files[tab.title];
                    var tabData = JSON.parse(JSON.stringify(tab));
                    if (file) {
                        tabData.filePath = file.filePath;
                        tabData.language = file.language;
                        tabData.cursorLine = file.cursorLine || 1;
                        tabData.cursorCol = file.cursorCol || 1;
                    }
                    instance.closedTabsHistory.unshift({
                        tabs: [tabData],
                        closedAt: Date.now()
                    });
                    tabsInstance.closedTabsHistory = instance.closedTabsHistory;
                    self.saveTabsState(instance);
                },
                onFlushClosedHistory: function() {
                },
                onReopenClosedTabs: function() {
                    if (instance.closedTabsHistory.length === 0) {
                        return [];
                    }
                    var entry = instance.closedTabsHistory.shift();
                    var closedTabs = entry.tabs || [];
                    var reopened = [];
                    for (var i = 0; i < closedTabs.length; i++) {
                        var tab = closedTabs[i];
                        tab.id = ZatoTabsEvents.generateTabId();
                        tabsInstance.tabs.push(tab);
                        reopened.push(tab);

                        if (tab.filePath && !instance.files[tab.title]) {
                            instance.files[tab.title] = {
                                content: '',
                                originalContent: '',
                                language: tab.language || 'text',
                                filePath: tab.filePath,
                                modified: false,
                                cursorLine: tab.cursorLine || 1,
                                cursorCol: tab.cursorCol || 1
                            };
                            self.loadFileContent(instance, tab.filePath, tab.title);
                        }
                    }
                    tabsInstance.closedTabsHistory = instance.closedTabsHistory;
                    self.saveTabsState(instance);
                    return reopened;
                },
                onClearMessages: function(tabId, messages) {
                    instance.clearedMessagesBuffer[tabId] = {
                        messages: JSON.parse(JSON.stringify(messages)),
                        clearedAt: Date.now()
                    };
                    tabsInstance.clearedMessagesBuffer = instance.clearedMessagesBuffer;
                },
                onUndoClearMessages: function(tabId) {
                    var buffer = instance.clearedMessagesBuffer[tabId];
                    if (!buffer) {
                        return false;
                    }
                    var tab = ZatoTabsEvents.getTabById(tabsInstance.tabs, tabId);
                    if (tab) {
                        tab.messages = buffer.messages;
                        delete instance.clearedMessagesBuffer[tabId];
                        tabsInstance.clearedMessagesBuffer = instance.clearedMessagesBuffer;
                        return true;
                    }
                    return false;
                }
            };

            ZatoTabsEvents.bind(container, tabsInstance, callbacks);
        },

        switchToTab: function(instance, tabId) {
            if (!instance.tabsManager) {
                return;
            }

            instance.tabsManager.activeTabId = tabId;
            this.renderTabs(instance);
            this.bindTabEvents(instance);

            var tab = null;
            for (var i = 0; i < instance.tabsManager.tabs.length; i++) {
                if (instance.tabsManager.tabs[i].id === tabId) {
                    tab = instance.tabsManager.tabs[i];
                    break;
                }
            }

            if (tab && tab.title) {
                ZatoIDE.switchToFile(instance, tab.title);
            }
        },

        closeTab: function(instance, tab) {
            if (!instance.tabsManager || !instance.tabsManager.tabs) {
                return;
            }

            var tabId = tab.id;
            var filename = tab.title;
            var file = instance.files ? instance.files[filename] : null;
            var self = this;

            var doClose = function() {
                var tabs = instance.tabsManager.tabs;
                var tabIndex = -1;
                for (var i = 0; i < tabs.length; i++) {
                    if (tabs[i].id === tabId) {
                        tabIndex = i;
                        break;
                    }
                }

                if (tabIndex === -1) {
                    return;
                }

                tabs.splice(tabIndex, 1);

                if (instance.tabsManager.activeTabId === tabId) {
                    var newIndex = tabIndex > 0 ? tabIndex - 1 : 0;
                    if (tabs.length > 0) {
                        instance.tabsManager.activeTabId = tabs[newIndex].id;
                        ZatoIDE.switchToFile(instance, tabs[newIndex].title);
                    }
                }

                self.renderTabs(instance);
                self.bindTabEvents(instance);
            };

            if (file && file.modified) {
                ZatoIDE.showSaveDialog(instance, filename, {
                    onDontSave: function() {
                        file.modified = false;
                        doClose();
                    },
                    onCancel: function() {
                    },
                    onSave: function() {
                        file.originalContent = file.content;
                        file.modified = false;
                        doClose();
                    }
                });
            } else {
                doClose();
            }
        },

        updateTabModifiedState: function(instance, filename, modified) {
            if (!instance.tabsManager) {
                return;
            }
            var tabs = instance.tabsManager.tabs;
            for (var i = 0; i < tabs.length; i++) {
                if (tabs[i].title === filename) {
                    tabs[i].modified = modified;
                    this.renderTabs(instance);
                    break;
                }
            }
        },

        syncTabToFile: function(instance, filename) {
            if (!instance.tabsManager) {
                return;
            }

            var tabs = instance.tabsManager.tabs;
            for (var i = 0; i < tabs.length; i++) {
                if (tabs[i].title === filename) {
                    instance.tabsManager.activeTabId = tabs[i].id;
                    this.renderTabs(instance);
                    break;
                }
            }
        },

        findTabByPath: function(instance, filePath) {
            if (!instance.tabsManager || !instance.tabsManager.tabs) {
                return null;
            }
            for (var i = 0; i < instance.tabsManager.tabs.length; i++) {
                var tab = instance.tabsManager.tabs[i];
                if (tab.filePath === filePath) {
                    return tab;
                }
            }
            return null;
        },

        openFileFromPath: function(instance, filePath, fileName) {
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
        },

        showSaveDialog: function(instance, filename, callbacks) {
            var overlay = document.createElement('div');
            overlay.className = 'zato-tabs-save-dialog-overlay';
            var dialog = document.createElement('div');
            dialog.className = 'zato-tabs-save-dialog';
            var header = document.createElement('div');
            header.className = 'zato-tabs-save-dialog-header';
            var title = document.createElement('div');
            title.className = 'zato-tabs-save-dialog-title';
            title.textContent = 'Save changes';
            var closeBtn = document.createElement('button');
            closeBtn.className = 'zato-tabs-save-dialog-close';
            closeBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';
            header.appendChild(title);
            header.appendChild(closeBtn);
            var content = document.createElement('div');
            content.className = 'zato-tabs-save-dialog-content';
            var message = document.createElement('div');
            message.className = 'zato-tabs-save-dialog-message';
            message.innerHTML = 'Do you want to save the changes you made to <strong>' + filename + '</strong>?<br>Your changes will be lost if you don\'t save them.';
            var buttons = document.createElement('div');
            buttons.className = 'zato-tabs-save-dialog-buttons';
            var dontSaveBtn = document.createElement('button');
            dontSaveBtn.className = 'zato-tabs-save-dialog-btn zato-tabs-save-dialog-btn-secondary';
            dontSaveBtn.textContent = 'Don\'t Save';
            var cancelBtn = document.createElement('button');
            cancelBtn.className = 'zato-tabs-save-dialog-btn zato-tabs-save-dialog-btn-secondary';
            cancelBtn.textContent = 'Cancel';
            var saveBtn = document.createElement('button');
            saveBtn.className = 'zato-tabs-save-dialog-btn zato-tabs-save-dialog-btn-default';
            saveBtn.textContent = 'Save';
            buttons.appendChild(dontSaveBtn);
            buttons.appendChild(cancelBtn);
            buttons.appendChild(saveBtn);
            content.appendChild(message);
            content.appendChild(buttons);
            dialog.appendChild(header);
            dialog.appendChild(content);
            overlay.appendChild(dialog);
            document.body.appendChild(overlay);
            dialog.style.left = '50%';
            dialog.style.top = '50%';
            dialog.style.transform = 'translate(-50%, -50%)';
            this.makeDialogDraggable(dialog, header, closeBtn);
            var closeDialog = function() { document.body.removeChild(overlay); };
            closeBtn.addEventListener('click', function() { closeDialog(); if (callbacks.onCancel) { callbacks.onCancel(); } });
            dontSaveBtn.addEventListener('click', function() { closeDialog(); if (callbacks.onDontSave) { callbacks.onDontSave(); } });
            cancelBtn.addEventListener('click', function() { closeDialog(); if (callbacks.onCancel) { callbacks.onCancel(); } });
            saveBtn.addEventListener('click', function() { closeDialog(); if (callbacks.onSave) { callbacks.onSave(); } });
            overlay.addEventListener('click', function(e) {
                if (e.target === overlay) { closeDialog(); if (callbacks.onCancel) { callbacks.onCancel(); } }
            });
            var escHandler = function(e) {
                if (e.key === 'Escape') { closeDialog(); document.removeEventListener('keydown', escHandler); if (callbacks.onCancel) { callbacks.onCancel(); } }
            };
            document.addEventListener('keydown', escHandler);
            saveBtn.focus();
        },

        makeDialogDraggable: function(dialog, handle, excludeElement) {
            var isDragging = false;
            var startX, startY, startLeft, startTop;
            handle.addEventListener('mousedown', function(e) {
                if (excludeElement && e.target.closest('.zato-tabs-save-dialog-close')) { return; }
                isDragging = true;
                var rect = dialog.getBoundingClientRect();
                startLeft = rect.left;
                startTop = rect.top;
                dialog.style.transform = 'none';
                dialog.style.left = startLeft + 'px';
                dialog.style.top = startTop + 'px';
                startX = e.clientX;
                startY = e.clientY;
                e.preventDefault();
            });
            document.addEventListener('mousemove', function(e) {
                if (!isDragging) return;
                dialog.style.left = (startLeft + e.clientX - startX) + 'px';
                dialog.style.top = (startTop + e.clientY - startY) + 'px';
            });
            document.addEventListener('mouseup', function() { isDragging = false; });
        },

        openFileInNewTab: function(instance, filePath, fileName, content) {
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
        }
    };

    window.ZatoIDETabs = ZatoIDETabs;

})();
