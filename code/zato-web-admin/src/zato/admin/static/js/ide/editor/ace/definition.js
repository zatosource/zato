(function() {
    'use strict';

    Object.assign(window.ZatoIDEEditorAce, {

        setupGotoDefinition: function(editor, instance) {
            var self = this;

            instance.definitionHighlightMarkerId = null;
            instance.ctrlPressed = false;
            instance.prefetchedDefinition = null;
            instance.prefetchLine = null;
            instance.prefetchColumn = null;
            instance.prefetchXhr = null;

            editor.container.addEventListener('click', function(e) {
                if (!e.ctrlKey) {
                    return;
                }

                e.preventDefault();
                e.stopPropagation();

                var pos = editor.getCursorPosition();
                var token = editor.session.getTokenAt(pos.row, pos.column);

                if (!token) {
                    return;
                }

                var word = self.getWordAtPosition(editor, pos);
                if (!word) {
                    return;
                }

                self.gotoDefinition(editor, instance, pos.row + 1, pos.column);
            });

            document.addEventListener('keydown', function(e) {
                if (e.key === 'Control' && !instance.ctrlPressed) {
                    instance.ctrlPressed = true;
                    editor.container.classList.add('zato-ctrl-hover-mode');
                }
            });

            document.addEventListener('keyup', function(e) {
                if (e.key === 'Control') {
                    instance.ctrlPressed = false;
                    editor.container.classList.remove('zato-ctrl-hover-mode');
                    self.clearHoverHighlight(editor, instance);
                }
            });

            editor.container.addEventListener('mousemove', function(e) {
                if (!instance.ctrlPressed) {
                    return;
                }

                var pos = editor.renderer.screenToTextCoordinates(e.clientX, e.clientY);
                var token = editor.session.getTokenAt(pos.row, pos.column);

                if (token && self.isNavigableToken(token)) {
                    self.showHoverHighlight(editor, instance, pos.row, token);
                    self.prefetchDefinition(editor, instance, pos.row + 1, token.start);
                } else {
                    self.clearHoverHighlight(editor, instance);
                    self.clearPrefetch(instance);
                }
            });

            editor.container.addEventListener('mouseleave', function() {
                self.clearHoverHighlight(editor, instance);
            });

        },

        isNavigableToken: function(token) {
            if (!token || !token.type) {
                return false;
            }
            return token.type === 'identifier' ||
                   token.type === 'entity.name.function' ||
                   token.type === 'support.function' ||
                   token.type === 'variable' ||
                   token.type.indexOf('identifier') !== -1 ||
                   token.type.indexOf('variable') !== -1;
        },

        showHoverHighlight: function(editor, instance, row, token) {
            var self = this;

            if (instance.hoverRow === row && instance.hoverTokenStart === token.start) {
                return;
            }

            self.clearHoverHighlight(editor, instance);

            instance.hoverRow = row;
            instance.hoverTokenStart = token.start;

            var textLayer = editor.renderer.$textLayer;
            var lineElement = textLayer.element.children[row - editor.renderer.getFirstVisibleRow()];
            if (lineElement) {
                var tokens = lineElement.querySelectorAll('span');
                var charCount = 0;
                for (var i = 0; i < tokens.length; i++) {
                    var span = tokens[i];
                    var spanText = span.textContent;
                    var spanStart = charCount;
                    var spanEnd = charCount + spanText.length;
                    if (spanStart <= token.start && token.start < spanEnd) {
                        span.classList.add('ace_definition_hover_text');
                        instance.hoverTextElement = span;
                        break;
                    }
                    charCount = spanEnd;
                }
            }
        },

        clearHoverHighlight: function(editor, instance) {
            if (instance.hoverTextElement) {
                instance.hoverTextElement.classList.remove('ace_definition_hover_text');
                instance.hoverTextElement = null;
            }
            instance.hoverRow = null;
            instance.hoverTokenStart = null;
        },

        getWordAtPosition: function(editor, pos) {
            var token = editor.session.getTokenAt(pos.row, pos.column);
            if (!token) {
                return null;
            }
            if (token.type === 'identifier' || token.type === 'entity.name.function' ||
                token.type === 'support.function' || token.type === 'variable' ||
                token.type.indexOf('identifier') !== -1 || token.type.indexOf('variable') !== -1) {
                return token.value;
            }
            return null;
        },

        prefetchDefinition: function(editor, instance, line, column) {
            var self = this;

            if (instance.prefetchLine === line && instance.prefetchColumn === column) {
                return;
            }

            self.clearPrefetch(instance);

            instance.prefetchLine = line;
            instance.prefetchColumn = column;

            var code = editor.getValue();
            if (!code.trim()) {
                return;
            }

            var csrfToken = this.getCsrfToken();
            var xhr = new XMLHttpRequest();
            instance.prefetchXhr = xhr;

            xhr.open('POST', '/zato/ide/definition/python/', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            if (csrfToken) {
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
            }

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        try {
                            var response = JSON.parse(xhr.responseText);
                            if (response.success && response.definitions && response.definitions.length > 0) {
                                instance.prefetchedDefinition = response.definitions[0];
                            }
                        } catch (e) {
                            instance.prefetchedDefinition = null;
                        }
                    }
                    instance.prefetchXhr = null;
                }
            };

            var requestBody = JSON.stringify({
                code: code,
                line: line,
                column: column
            });
            xhr.send(requestBody);
        },

        clearPrefetch: function(instance) {
            if (instance.prefetchXhr) {
                instance.prefetchXhr.abort();
                instance.prefetchXhr = null;
            }
            instance.prefetchedDefinition = null;
            instance.prefetchLine = null;
            instance.prefetchColumn = null;
        },

        gotoDefinition: function(editor, instance, line, column) {
            var self = this;

            if (instance.prefetchedDefinition && instance.prefetchLine === line) {
                var def = instance.prefetchedDefinition;
                self.clearPrefetch(instance);
                self.navigateToDefinition(editor, instance, def);
                return;
            }

            self.clearPrefetch(instance);

            var code = editor.getValue();
            if (!code.trim()) {
                return;
            }

            var csrfToken = this.getCsrfToken();
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/zato/ide/definition/python/', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            if (csrfToken) {
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
            }

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        try {
                            var response = JSON.parse(xhr.responseText);
                            if (response.success && response.definitions && response.definitions.length > 0) {
                                self.navigateToDefinition(editor, instance, response.definitions[0]);
                            }
                        } catch (e) {
                            console.warn('[GotoDefinition] Failed to parse response:', e);
                        }
                    }
                }
            };

            var requestBody = JSON.stringify({
                code: code,
                line: line,
                column: column
            });
            xhr.send(requestBody);
        },

        navigateToDefinition: function(editor, instance, definition) {
            var self = this;
            var filePath = definition.file_path;
            var targetLine = definition.line;
            var targetColumn = definition.column;

            var currentFilePath = null;
            if (instance.options && instance.options.getFilePath) {
                currentFilePath = instance.options.getFilePath();
            }

            var isSameFile = false;
            if (currentFilePath && filePath) {
                isSameFile = currentFilePath === filePath ||
                             filePath.indexOf('_ide_temp_service.py') !== -1;
            }

            if (isSameFile || filePath.indexOf('_ide_temp_service.py') !== -1) {
                editor.gotoLine(targetLine, targetColumn, true);
                self.highlightDefinition(editor, instance, targetLine, targetColumn);
            } else {
                if (instance.options && instance.options.onGotoDefinition) {
                    instance.options.onGotoDefinition(filePath, targetLine, targetColumn);
                }
            }
        },

        highlightDefinition: function(editor, instance, line, column) {
            var self = this;

            self.clearDefinitionHighlight(editor, instance);

            var Range = ace.require('ace/range').Range;
            var lineContent = editor.session.getLine(line - 1);

            var wordStart = column;
            var wordEnd = column;

            while (wordStart > 0 && /\w/.test(lineContent.charAt(wordStart - 1))) {
                wordStart--;
            }
            while (wordEnd < lineContent.length && /\w/.test(lineContent.charAt(wordEnd))) {
                wordEnd++;
            }

            var range = new Range(line - 1, wordStart, line - 1, wordEnd);
            instance.definitionHighlightMarkerId = editor.session.addMarker(range, 'ace_definition_highlight', 'text', true);

            instance.definitionFlashTimeout = window.setTimeout(function() {
                self.clearDefinitionHighlight(editor, instance);
            }, 550);
        },

        clearDefinitionHighlight: function(editor, instance) {
            if (instance.definitionFlashTimeout) {
                window.clearTimeout(instance.definitionFlashTimeout);
                instance.definitionFlashTimeout = null;
            }
            if (instance.definitionHighlightMarkerId) {
                editor.session.removeMarker(instance.definitionHighlightMarkerId);
                instance.definitionHighlightMarkerId = null;
            }
        }

    });

})();
