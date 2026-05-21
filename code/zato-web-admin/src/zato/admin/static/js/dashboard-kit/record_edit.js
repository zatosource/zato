
// ////////////////////////////////////////////////////////////////////////
// Dashboard kit - generic record edit form component.
// Renders a form from a field definition array, collects values,
// POSTs via AJAX to detail_poll with a configurable action,
// and provides status feedback. Domain-agnostic - all field
// knowledge comes through the config object.
// ////////////////////////////////////////////////////////////////////////

(function($) {

    if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
    if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

    var kit = $.fn.zato.dashboard_kit;
    kit.record_edit = {};

// ////////////////////////////////////////////////////////////////////////

    kit.record_edit._config = null;
    kit.record_edit._$container = null;
    kit.record_edit._ace_editor = null;
    kit.record_edit._ace_field_name = null;

    kit.record_edit._labels = {
        save: 'Save',
        saved: 'OK, saved',
        saveFailed: 'Save failed'
    };

// ////////////////////////////////////////////////////////////////////////

    kit.record_edit.init = function(config) {

        // Store the config for later use ..
        kit.record_edit._config = config;

        // .. resolve the container ..
        kit.record_edit._$container = $(config.container);

        // .. render the form ..
        kit.record_edit._render();

        // .. bind the save button ..
        kit.record_edit._$container.on('click', '.record-edit-save-button', function() {
            kit.record_edit.save(this);
        });

        // .. bind the copy button if enabled ..
        kit.record_edit._$container.on('click', '.record-edit-copy-button', function() {
            var text = kit.record_edit._get_copy_text();
            if (text) {
                kit.copy_to_clipboard(this, text);
            }
        });

        // .. and initialize the Ace editor if any field uses highlight.
        var $aceContainer = kit.record_edit._$container.find('.record-edit-ace-editor');
        if ($aceContainer.length) {
            var fieldName = $aceContainer.attr('data-field');
            kit.record_edit._ace_field_name = fieldName;

            var editor = ace.edit($aceContainer[0]);
            editor.setTheme('ace/theme/monokai');
            editor.setShowPrintMargin(false);
            editor.setFontSize(12);
            editor.setOptions({
                fontFamily: 'Menlo, Consolas, Monaco, monospace',
                firstLineNumber: 1
            });
            editor.renderer.setScrollMargin(10, 10, 0, 0);

            var mode = kit.record_edit._guess_ace_mode(editor.getValue());
            editor.session.setMode(mode);

            kit.record_edit._ace_editor = editor;
        }
    };

// ////////////////////////////////////////////////////////////////////////

    kit.record_edit._render = function() {

        var config = kit.record_edit._config;
        var data = config.data;

        // Build the read-only fields section ..
        var out = '';

        if (config.readonly_fields.length > 0) {
            out += '<div class="record-edit-readonly-section">';

            for (var readonlyIndex = 0; readonlyIndex < config.readonly_fields.length; readonlyIndex++) {
                var readonlyField = config.readonly_fields[readonlyIndex];
                var readonlyValue = data[readonlyField.name];

                if (readonlyField.format === 'time') {
                    readonlyValue = kit.format_local_time(readonlyValue);
                }

                if (readonlyField.suffix) {
                    readonlyValue = readonlyValue + readonlyField.suffix;
                }

                out += '<div class="record-edit-field-row record-edit-field-readonly">';
                out += '<label class="record-edit-label">' + readonlyField.label + '</label>';
                out += '<span class="record-edit-value">' + kit._esc_html(String(readonlyValue)) + '</span>';
                out += '</div>';
            }

            out += '</div>';
        }

        // .. render the editable fields section ..
        out += '<div class="record-edit-editable-section">';

        for (var fieldIndex = 0; fieldIndex < config.fields.length; fieldIndex++) {
            var field = config.fields[fieldIndex];
            var fieldValue = data[field.name];

            if (fieldValue === null) {
                fieldValue = '';
            }
            if (fieldValue === undefined) {
                fieldValue = '';
            }

            out += '<div class="record-edit-field-row">';

            if (config.show_labels !== false) {
                out += '<label class="record-edit-label" for="record-edit-' + field.name + '">' + field.label + '</label>';
            }

            if (field.type === 'textarea') {
                if (field.highlight) {
                    out += '<div id="record-edit-ace-' + field.name + '" class="record-edit-ace-editor"';
                    out += ' data-field="' + field.name + '">';
                    out += kit._esc_html(String(fieldValue));
                    out += '</div>';
                }
                else {
                    var monoClass = field.monospace ? ' record-edit-monospace' : '';
                    out += '<textarea id="record-edit-' + field.name + '" class="record-edit-input record-edit-textarea' + monoClass + '"';
                    out += ' data-field="' + field.name + '">';
                    out += kit._esc_html(String(fieldValue));
                    out += '</textarea>';
                }
            }
            else if (field.type === 'number') {
                out += '<input id="record-edit-' + field.name + '" class="record-edit-input" type="number"';
                out += ' data-field="' + field.name + '"';
                out += ' value="' + kit._esc_html(String(fieldValue)) + '">';
            }
            else {
                out += '<input id="record-edit-' + field.name + '" class="record-edit-input" type="text"';
                out += ' data-field="' + field.name + '"';
                out += ' value="' + kit._esc_html(String(fieldValue)) + '">';
            }

            out += '</div>';
        }

        out += '</div>';

        // .. render hidden fields ..
        for (var hiddenIndex = 0; hiddenIndex < config.hidden_fields.length; hiddenIndex++) {
            var hiddenName = config.hidden_fields[hiddenIndex];
            var hiddenValue = data[hiddenName];
            out += '<input type="hidden" data-field="' + hiddenName + '" value="' + kit._esc_html(String(hiddenValue)) + '">';
        }

        // .. check if any field uses highlighting ..
        var hasHighlight = false;
        for (var highlightCheckIndex = 0; highlightCheckIndex < config.fields.length; highlightCheckIndex++) {
            if (config.fields[highlightCheckIndex].highlight) {
                hasHighlight = true;
                break;
            }
        }

        // .. render the footer buttons ..
        var footerClass = hasHighlight ? 'record-edit-footer record-edit-footer-dark' : 'record-edit-footer';
        out += '<div class="' + footerClass + '">';
        if (config.show_copy_button) {
            out += '<button class="record-edit-action-button record-edit-copy-button" type="button">Copy</button>';
        }
        out += '<button class="record-edit-action-button record-edit-save-button" type="button">' + kit.record_edit._labels.save + '</button>';
        out += '</div>';

        // .. and inject into the container.
        kit.record_edit._$container.html(out);
    };

// ////////////////////////////////////////////////////////////////////////

    kit.record_edit.collect = function() {

        var $container = kit.record_edit._$container;
        var aceFieldName = kit.record_edit._ace_field_name;

        // Collect all fields with data-field attribute ..
        var out = {};

        $container.find('[data-field]').each(function() {
            var $field = $(this);
            var fieldName = $field.attr('data-field');

            // .. read from the Ace editor for highlighted fields ..
            if (fieldName === aceFieldName && kit.record_edit._ace_editor) {
                out[fieldName] = kit.record_edit._ace_editor.getValue();
            }
            else {
                out[fieldName] = $field.val();
            }
        });

        // .. and return the collected payload.
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    kit.record_edit.save = function(buttonElement) {

        var config = kit.record_edit._config;
        var payload = kit.record_edit.collect();
        payload.action = config.save_action;

        // POST to the poll URL ..
        $.ajax({
            type: 'POST',
            url: config.poll_url,
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            data: JSON.stringify(payload),
            contentType: 'application/json',
            success: function(response) {

                // .. show success ..
                kit.flash_tooltip(buttonElement, kit.record_edit._labels.saved);

                // .. and call the domain callback if provided.
                if (config.on_save_success) {
                    config.on_save_success(response);
                }
            },
            error: function(xhr) {

                var errorMessage = kit.record_edit._labels.saveFailed;
                if (xhr.responseJSON) {
                    if (xhr.responseJSON.error) {
                        errorMessage = xhr.responseJSON.error;
                    }
                }

                // .. show error ..
                kit.flash_tooltip(buttonElement, errorMessage);

                // .. and call the domain callback if provided.
                if (config.on_save_error) {
                    config.on_save_error(errorMessage);
                }
            }
        });
    };

// ////////////////////////////////////////////////////////////////////////

    kit.record_edit._get_copy_text = function() {
        var config = kit.record_edit._config;
        var field_name = config.copy_field;

        if (field_name === kit.record_edit._ace_field_name && kit.record_edit._ace_editor) {
            return kit.record_edit._ace_editor.getValue();
        }

        var $field = kit.record_edit._$container.find('[data-field="' + field_name + '"]');
        return $field.val();
    };

// ////////////////////////////////////////////////////////////////////////

    kit.record_edit._guess_ace_mode = function(text) {
        var trimmed = text.trim();

        if ((trimmed.charAt(0) === '{' && trimmed.charAt(trimmed.length - 1) === '}') ||
            (trimmed.charAt(0) === '[' && trimmed.charAt(trimmed.length - 1) === ']')) {
            try {
                JSON.parse(trimmed);
                return 'ace/mode/json';
            }
            catch (e) {
                // Not valid JSON, fall through
            }
        }

        if (trimmed.charAt(0) === '<' && trimmed.indexOf('>') !== -1) {
            return 'ace/mode/xml';
        }

        return 'ace/mode/text';
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
