
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
    kit.record_edit._$status = null;

    kit.record_edit._labels = {
        save: 'Save',
        saving: 'Saving...',
        saved: 'Saved',
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

        // .. and bind the save button.
        kit.record_edit._$container.on('click', '.record-edit-save-button', function() {
            kit.record_edit.save();
        });
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
                var monoClass = field.monospace ? ' record-edit-monospace' : '';
                out += '<textarea id="record-edit-' + field.name + '" class="record-edit-input record-edit-textarea' + monoClass + '"';
                out += ' data-field="' + field.name + '">';
                out += kit._esc_html(String(fieldValue));
                out += '</textarea>';
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

        // .. render the save button and status area ..
        out += '<div class="record-edit-footer">';
        out += '<button class="action-button record-edit-save-button" type="button">' + kit.record_edit._labels.save + '</button>';
        out += '<span class="record-edit-status"></span>';
        out += '</div>';

        // .. and inject into the container.
        kit.record_edit._$container.html(out);
        kit.record_edit._$status = kit.record_edit._$container.find('.record-edit-status');
    };

// ////////////////////////////////////////////////////////////////////////

    kit.record_edit.collect = function() {

        var $container = kit.record_edit._$container;

        // Collect all fields with data-field attribute ..
        var out = {};

        $container.find('[data-field]').each(function() {
            var $field = $(this);
            var fieldName = $field.attr('data-field');
            var fieldValue = $field.val();
            out[fieldName] = fieldValue;
        });

        // .. and return the collected payload.
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    kit.record_edit.save = function() {

        var config = kit.record_edit._config;
        var payload = kit.record_edit.collect();
        payload.action = config.save_action;

        // Show saving status ..
        kit.record_edit.set_status('saving', kit.record_edit._labels.saving);

        // .. POST to the poll URL ..
        $.ajax({
            type: 'POST',
            url: config.poll_url,
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            data: JSON.stringify(payload),
            contentType: 'application/json',
            success: function(response) {

                // .. show success ..
                kit.record_edit.set_status('success', kit.record_edit._labels.saved);

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
                kit.record_edit.set_status('error', errorMessage);

                // .. and call the domain callback if provided.
                if (config.on_save_error) {
                    config.on_save_error(errorMessage);
                }
            }
        });
    };

// ////////////////////////////////////////////////////////////////////////

    kit.record_edit.set_status = function(type, message) {

        var $status = kit.record_edit._$status;

        // Update the status display ..
        $status.removeClass('record-edit-status-success record-edit-status-error record-edit-status-saving');
        $status.addClass('record-edit-status-' + type);
        $status.text(message);

        // .. and auto-clear success after a delay.
        if (type === 'success') {
            setTimeout(function() {
                $status.text('');
                $status.removeClass('record-edit-status-success');
            }, 3000);
        }
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
