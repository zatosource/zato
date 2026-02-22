(function() {
    'use strict';

    Object.assign(window.ZatoIDEEditorAce, {

        storageNamespace: 'zato-ide-editor',

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

        getStorageKey: function(instance) {
            var pageId = instance.options.storageId || window.location.pathname;
            return this.storageNamespace + ':' + pageId;
        },

        saveState: function(instance) {
            var editor = instance.aceEditor;
            if (!editor) return;

            var session = editor.session;
            var state = {
                content: editor.getValue(),
                cursor: editor.getCursorPosition(),
                selection: editor.getSelectionRange(),
                scroll: {
                    top: session.getScrollTop(),
                    left: session.getScrollLeft()
                },
                folds: session.getAllFolds().map(function(fold) {
                    return {
                        start: { row: fold.start.row, column: fold.start.column },
                        end: { row: fold.end.row, column: fold.end.column }
                    };
                }),
                undoStack: session.getUndoManager().$undoStack,
                redoStack: session.getUndoManager().$redoStack,
                tabSize: session.getTabSize(),
                useSoftTabs: session.getUseSoftTabs(),
                fontSize: editor.getFontSize(),
                bookmarks: session.getBreakpoints(),
                searchOptions: editor.$search ? {
                    needle: editor.$search.$options.needle,
                    caseSensitive: editor.$search.$options.caseSensitive,
                    wholeWord: editor.$search.$options.wholeWord,
                    regExp: editor.$search.$options.regExp
                } : null,
                autocompleteOpen: editor.completer && editor.completer.activated,
                autocompletePos: editor.completer && editor.completer.activated ? editor.getCursorPosition() : null,
                timestamp: Date.now()
            };

            try {
                localStorage.setItem(this.getStorageKey(instance), JSON.stringify(state));
            } catch (e) {
                console.warn('[IDE] Failed to save state:', e);
            }
        },

        loadState: function(instance) {
            var editor = instance.aceEditor;
            if (!editor) return false;

            var key = this.getStorageKey(instance);
            var stored = localStorage.getItem(key);
            if (!stored) return false;

            try {
                var state = JSON.parse(stored);
                var session = editor.session;

                if (state.content !== undefined) {
                    editor.setValue(state.content, -1);
                }

                if (state.undoStack) {
                    var undoManager = session.getUndoManager();
                    undoManager.$undoStack = state.undoStack;
                    undoManager.$redoStack = state.redoStack || [];
                }

                if (state.folds && state.folds.length > 0) {
                    state.folds.forEach(function(fold) {
                        try {
                            session.addFold('...', new ace.Range(fold.start.row, fold.start.column, fold.end.row, fold.end.column));
                        } catch (e) {}
                    });
                }

                if (state.cursor) {
                    editor.moveCursorToPosition(state.cursor);
                }

                if (state.selection) {
                    editor.selection.setSelectionRange(state.selection);
                }

                if (state.scroll) {
                    session.setScrollTop(state.scroll.top);
                    session.setScrollLeft(state.scroll.left);
                }

                if (state.tabSize) {
                    session.setTabSize(state.tabSize);
                }

                if (state.useSoftTabs !== undefined) {
                    session.setUseSoftTabs(state.useSoftTabs);
                }

                if (state.fontSize) {
                    editor.setFontSize(state.fontSize);
                }

                if (state.bookmarks && state.bookmarks.length > 0) {
                    state.bookmarks.forEach(function(bp, row) {
                        if (bp) {
                            session.setBreakpoint(row, bp);
                        }
                    });
                }

                if (state.searchOptions && state.searchOptions.needle) {
                    editor.$search.$options.needle = state.searchOptions.needle;
                    editor.$search.$options.caseSensitive = state.searchOptions.caseSensitive;
                    editor.$search.$options.wholeWord = state.searchOptions.wholeWord;
                    editor.$search.$options.regExp = state.searchOptions.regExp;
                }

                if (state.autocompleteOpen && state.autocompletePos) {
                    setTimeout(function() {
                        editor.moveCursorToPosition(state.autocompletePos);
                        editor.execCommand('startAutocomplete');
                    }, 100);
                }

                return true;
            } catch (e) {
                console.warn('[IDE] Failed to load state:', e);
                return false;
            }
        },

        clearState: function(instance) {
            try {
                localStorage.removeItem(this.getStorageKey(instance));
            } catch (e) {}
        },

        setupAutoSave: function(instance) {
            var self = this;
            var editor = instance.aceEditor;
            if (!editor) return;

            var saveTimeout = null;
            var saveDelay = 500;

            var triggerSave = function() {
                if (saveTimeout) {
                    clearTimeout(saveTimeout);
                }
                saveTimeout = setTimeout(function() {
                    self.saveState(instance);
                }, saveDelay);
            };

            editor.session.on('change', triggerSave);
            editor.session.on('changeFold', triggerSave);
            editor.session.on('changeScrollTop', triggerSave);
            editor.session.on('changeScrollLeft', triggerSave);
            editor.selection.on('changeCursor', triggerSave);
            editor.selection.on('changeSelection', triggerSave);

            window.addEventListener('beforeunload', function() {
                self.saveState(instance);
            });
        }

    });

})();
