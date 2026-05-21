
// ////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.highlight_pane');

    var helpers = $.fn.zato.ui_helpers;

// ////////////////////////////////////////////////////////////////////////

    function _guess_ace_mode(text) {
        var trimmed = text.trim();

        // Check if the text looks like JSON ..
        var firstChar = trimmed.charAt(0);
        var lastChar = trimmed.charAt(trimmed.length - 1);

        if ((firstChar === '{' && lastChar === '}') ||
            (firstChar === '[' && lastChar === ']')) {
            try {
                JSON.parse(trimmed);
                return 'ace/mode/json';
            }
            catch (error) {
                // .. not valid JSON, fall through.
            }
        }

        // .. check if the text looks like XML ..
        if (firstChar === '<' && trimmed.indexOf('>') !== -1) {
            return 'ace/mode/xml';
        }

        // .. otherwise, use plain text.
        return 'ace/mode/text';
    }

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.highlight_pane.init = function(config) {

        var $container = $(config.container);
        var editable = config.editable !== false;

        // Build the editor element ..
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
                var newMode = _guess_ace_mode(text);
                editor.session.setMode(newMode);

                if (config.on_mode_detected) {
                    config.on_mode_detected(newMode);
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

                    (function(clickHandler) {
                        buttonElement.addEventListener('click', function() {
                            clickHandler(this, pane);
                        });
                    })(buttonConfig.on_click);

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
            label: 'Copy',
            on_click: function(buttonElement, pane) {
                var selected = pane.getEditor().getSelectedText();
                var text = selected ? selected : pane.getValue();
                helpers.copy_to_clipboard(buttonElement, text);
            }
        };
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.highlight_pane.buttons.save = function(config) {
        return {
            id: 'zato-highlight-pane-save',
            label: 'Save',
            on_click: function(buttonElement, pane) {

                // Collect the payload from the editor and hidden fields ..
                var payload = {
                    action: config.save_action,
                    data: pane.getValue()
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
                        helpers.flash_tooltip(buttonElement, 'OK, saved');

                        if (config.on_success) {
                            config.on_success(response, pane);
                        }
                    },
                    error: function(xhr) {
                        var errorMessage = 'Save failed';

                        if (xhr.responseJSON) {
                            if (xhr.responseJSON.error) {
                                errorMessage = xhr.responseJSON.error;
                            }
                        }

                        helpers.flash_tooltip(buttonElement, errorMessage);

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
