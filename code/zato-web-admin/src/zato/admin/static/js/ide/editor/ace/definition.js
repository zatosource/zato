(function() {
    'use strict';

    Object.assign(window.ZatoIDEEditorAce, {

        setupGotoDefinition: function(editor, instance) {
            var self = this;

            instance.definitionHighlightMarkerId = null;

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

            editor.session.on('change', function() {
                self.clearDefinitionHighlight(editor, instance);
            });

            editor.on('changeSession', function() {
                self.clearDefinitionHighlight(editor, instance);
            });
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

        gotoDefinition: function(editor, instance, line, column) {
            var self = this;
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
                                var def = response.definitions[0];
                                self.navigateToDefinition(editor, instance, def);
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
        },

        clearDefinitionHighlight: function(editor, instance) {
            if (instance.definitionHighlightMarkerId) {
                editor.session.removeMarker(instance.definitionHighlightMarkerId);
                instance.definitionHighlightMarkerId = null;
            }
        }

    });

})();
