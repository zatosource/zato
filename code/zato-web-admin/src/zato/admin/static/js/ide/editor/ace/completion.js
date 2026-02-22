(function() {
    'use strict';

    Object.assign(window.ZatoIDEEditorAce, {

        setupCompletion: function(editor) {
            var self = this;

            var zubanCompleter = {
                getCompletions: function(aceEditor, session, pos, prefix, callback) {
                    console.log('[Complete] getCompletions called, pos:', pos, 'prefix:', prefix);
                    var code = aceEditor.getValue();
                    var line = pos.row + 1;
                    var column = pos.column;

                    if (!code.trim()) {
                        console.log('[Complete] Empty code, returning empty');
                        callback(null, []);
                        return;
                    }

                    var csrfToken = ZatoIDEEditorAce.getCsrfToken();
                    console.log('[Complete] Sending request to /zato/ide/complete/python/, line:', line, 'column:', column);
                    var xhr = new XMLHttpRequest();
                    xhr.open('POST', '/zato/ide/complete/python/', true);
                    xhr.setRequestHeader('Content-Type', 'application/json');
                    if (csrfToken) {
                        xhr.setRequestHeader('X-CSRFToken', csrfToken);
                    }
                    xhr.onreadystatechange = function() {
                        if (xhr.readyState === 4) {
                            console.log('[Complete] Response status:', xhr.status, 'response:', xhr.responseText.substring(0, 200));
                            if (xhr.status === 200) {
                                try {
                                    var response = JSON.parse(xhr.responseText);
                                    if (response.success && response.completions) {
                                        var results = [];
                                        for (var i = 0; i < response.completions.length; i++) {
                                            var item = response.completions[i];
                                            results.push({
                                                name: item.name,
                                                value: item.value,
                                                score: 1000 - i,
                                                meta: item.type
                                            });
                                        }
                                        console.log('[Complete] Returning', results.length, 'completions');
                                        callback(null, results);
                                        return;
                                    }
                                } catch (e) {
                                    console.warn('[Complete] Failed to parse response:', e);
                                }
                            }
                            callback(null, []);
                        }
                    };
                    var requestBody = JSON.stringify({
                        code: code,
                        line: line,
                        column: column
                    });
                    xhr.send(requestBody);
                }
            };

            var langTools = ace.require('ace/ext/language_tools');
            langTools.addCompleter(zubanCompleter);
            editor.setOptions({
                enableBasicAutocompletion: true,
                enableLiveAutocompletion: true,
                enableSnippets: false
            });
            editor.completers = [zubanCompleter];

            setInterval(function() {
                var allLines = document.querySelectorAll('.ace_autocomplete .ace_line');
                allLines.forEach(function(line) {
                    var isSelected = line.classList.contains('ace_selected');
                    var meta = line.querySelector('.ace_completion-meta');
                    var name = line.querySelector('.ace_');
                    if (isSelected) {
                        if (meta) {
                            meta.style.color = ZatoIDEEditorAce.completionMetaSelectedColor;
                            meta.style.opacity = '1';
                        }
                        if (name) {
                            name.style.color = ZatoIDEEditorAce.getCompletionNameSelectedColor();
                        }
                    } else {
                        if (meta) {
                            meta.style.color = '';
                            meta.style.opacity = '';
                        }
                        if (name) {
                            name.style.color = '';
                        }
                    }
                });
            }, 16);

            editor.commands.on('afterExec', function(e) {
                if (e.command.name === 'insertstring' && e.args === '.') {
                    console.log('[Complete] Dot pressed, triggering autocomplete');
                    editor.execCommand('startAutocomplete');
                }
            });
        }

    });

})();
