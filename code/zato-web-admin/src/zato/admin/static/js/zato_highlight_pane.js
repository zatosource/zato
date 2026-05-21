
// ////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.highlight_pane');

    var uiHelpers = $.fn.zato.ui_helpers;

    var _labels = {
        copy: 'Copy',
        save: 'Save',
        saved: 'OK, saved',
        saveFailed: 'Save failed'
    };

// ////////////////////////////////////////////////////////////////////////

    function _guess_ace_mode(text) {
        var trimmed = text.trim();
        var firstChar = trimmed.charAt(0);
        var lastChar = trimmed.charAt(trimmed.length - 1);

        var out = 'ace/mode/text';

        // Check if the text looks like JSON ..
        if (firstChar === '{') {
            if (lastChar === '}') {
                try {
                    JSON.parse(trimmed);
                    out = 'ace/mode/json';
                    return out;
                }
                catch (error) {
                    // .. not valid JSON, fall through.
                }
            }
        }

        if (firstChar === '[') {
            if (lastChar === ']') {
                try {
                    JSON.parse(trimmed);
                    out = 'ace/mode/json';
                    return out;
                }
                catch (error) {
                    // .. not valid JSON, fall through.
                }
            }
        }

        // .. check if the text looks like XML ..
        if (firstChar === '<') {
            var hasClosingBracket = trimmed.indexOf('>') !== -1;

            if (hasClosingBracket) {
                out = 'ace/mode/xml';
                return out;
            }
        }

        // .. otherwise, use plain text.
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    function _bindButtonClick(buttonElement, clickHandler, pane) {
        function handleClick() {
            clickHandler(buttonElement, pane);
        }
        buttonElement.addEventListener('click', handleClick);
    }

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.highlight_pane.init = function(config) {

        var $container = $(config.container);

        // Determine if the editor should be editable ..
        var editable = true;

        if (config.editable === false) {
            editable = false;
        }

        // .. build the editor element ..
        var editorElement = document.createElement('div');
        editorElement.className = 'zato-highlight-pane-editor';
        $container.append(editorElement);

        // .. set up the Ace editor ..
        var editor = ace.edit(editorElement);
        editor.setTheme('ace/theme/monokai');
        editor.setShowPrintMargin(false);
        editor.setFontSize(12);
        editor.setOptions({
            fontFamily: 'Menlo, Consolas, Monaco, monospace',
            firstLineNumber: 1
        });
        editor.renderer.setScrollMargin(7, 7, 0, 0);
        editor.setReadOnly(!editable);

        // .. apply any custom Ace options ..
        if (config.ace_options) {

            if (config.ace_options.theme) {
                editor.setTheme(config.ace_options.theme);
            }

            if (config.ace_options.fontSize) {
                editor.setFontSize(config.ace_options.fontSize);
            }
        }

        // .. set the initial text and detect the mode ..
        editor.setValue(config.text, -1);
        var mode = _guess_ace_mode(config.text);
        editor.session.setMode(mode);

        if (config.on_mode_detected) {
            config.on_mode_detected(mode);
        }

        // .. build the pane instance that callers interact with ..
        var pane = {

            getValue: function() {
                return editor.getValue();
            },

            setValue: function(text) {
                editor.setValue(text, -1);
                var detectedMode = _guess_ace_mode(text);
                editor.session.setMode(detectedMode);

                if (config.on_mode_detected) {
                    config.on_mode_detected(detectedMode);
                }
            },

            getEditor: function() {
                return editor;
            },

            destroy: function() {
                editor.destroy();
                $container.empty();
            }
        };

        // .. render the footer buttons if any were configured ..
        if (config.buttons) {
            if (config.buttons.length > 0) {

                var footer = document.createElement('div');
                footer.className = 'zato-highlight-pane-footer';

                for (var buttonIndex = 0; buttonIndex < config.buttons.length; buttonIndex++) {
                    var buttonConfig = config.buttons[buttonIndex];
                    var buttonElement = document.createElement('button');
                    buttonElement.className = 'zato-highlight-pane-button';
                    buttonElement.setAttribute('type', 'button');
                    buttonElement.textContent = buttonConfig.label;

                    if (buttonConfig.id) {
                        buttonElement.id = buttonConfig.id;
                    }

                    _bindButtonClick(buttonElement, buttonConfig.on_click, pane);

                    footer.appendChild(buttonElement);
                }

                $container.append(footer);
            }
        }

        // .. and return the pane instance.
        return pane;
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.highlight_pane.buttons = {};

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.highlight_pane.buttons.copy = function() {
        return {
            id: 'zato-highlight-pane-copy',
            label: _labels.copy,
            on_click: function(buttonElement, pane) {
                var selected = pane.getEditor().getSelectedText();
                var text = selected;

                if (!selected) {
                    text = pane.getValue();
                }

                uiHelpers.copy_to_clipboard(buttonElement, text);
            }
        };
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.highlight_pane.buttons.save = function(config) {
        return {
            id: 'zato-highlight-pane-save',
            label: _labels.save,
            on_click: function(buttonElement, pane) {

                // Collect the payload from the editor and hidden fields ..
                var editorValue = pane.getValue();

                var payload = {
                    action: config.save_action,
                    data: editorValue
                };

                if (config.hidden_fields) {
                    for (var fieldName in config.hidden_fields) {
                        payload[fieldName] = config.hidden_fields[fieldName];
                    }
                }

                // .. and POST it.
                $.ajax({
                    type: 'POST',
                    url: config.poll_url,
                    headers: {'X-CSRFToken': $.cookie('csrftoken')},
                    data: JSON.stringify(payload),
                    contentType: 'application/json',
                    success: function(response) {
                        uiHelpers.flash_tooltip(buttonElement, _labels.saved);

                        if (config.on_success) {
                            config.on_success(response, pane);
                        }
                    },
                    error: function(xhr) {
                        var errorMessage = _labels.saveFailed;

                        if (xhr.responseJSON) {
                            if (xhr.responseJSON.error) {
                                errorMessage = xhr.responseJSON.error;
                            }
                        }

                        uiHelpers.flash_tooltip(buttonElement, errorMessage);

                        if (config.on_error) {
                            config.on_error(errorMessage, pane);
                        }
                    }
                });
            }
        };
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
