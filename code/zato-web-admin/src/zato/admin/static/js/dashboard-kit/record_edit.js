
/* Dashboard kit - generic record edit form component.
   Renders a form from a field definition array, collects values,
   POSTs via AJAX to detail_poll with a configurable action,
   and provides status feedback. Domain-agnostic - all field
   knowledge comes through the config object. */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function($) {
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
        save_failed: 'Save failed'
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
        var html = '';

        // Render the read-only fields section ..
        html += '<div class="record-edit-readonly-section">';

        for (var readonlyIndex = 0; readonlyIndex < config.readonly_fields.length; readonlyIndex++) {
            var readonlyField = config.readonly_fields[readonlyIndex];
            var readonlyValue = data[readonlyField.name];

            if (readonlyField.format === 'time') {
                readonlyValue = kit.format_local_time(readonlyValue);
            }

            if (readonlyField.suffix) {
                readonlyValue = readonlyValue + readonlyField.suffix;
            }

            html += '<div class="record-edit-field-row record-edit-field-readonly">';
            html += '<label class="record-edit-label">' + readonlyField.label + '</label>';
            html += '<span class="record-edit-value">' + kit._esc_html(String(readonlyValue)) + '</span>';
            html += '</div>';
        }

        html += '</div>';

        // .. render the editable fields section ..
        html += '<div class="record-edit-editable-section">';

        for (var fieldIndex = 0; fieldIndex < config.fields.length; fieldIndex++) {
            var field = config.fields[fieldIndex];
            var fieldValue = data[field.name];

            if (fieldValue === null) {
                fieldValue = '';
            }
            if (fieldValue === undefined) {
                fieldValue = '';
            }

            html += '<div class="record-edit-field-row">';
            html += '<label class="record-edit-label" for="record-edit-' + field.name + '">' + field.label + '</label>';

            if (field.type === 'textarea') {
                var monoClass = field.monospace ? ' record-edit-monospace' : '';
                html += '<textarea id="record-edit-' + field.name + '" class="record-edit-input record-edit-textarea' + monoClass + '"';
                html += ' data-field="' + field.name + '">';
                html += kit._esc_html(String(fieldValue));
                html += '</textarea>';
            }
            else if (field.type === 'number') {
                html += '<input id="record-edit-' + field.name + '" class="record-edit-input" type="number"';
                html += ' data-field="' + field.name + '"';
                html += ' value="' + kit._esc_html(String(fieldValue)) + '">';
            }
            else {
                html += '<input id="record-edit-' + field.name + '" class="record-edit-input" type="text"';
                html += ' data-field="' + field.name + '"';
                html += ' value="' + kit._esc_html(String(fieldValue)) + '">';
            }

            html += '</div>';
        }

        html += '</div>';

        // .. render hidden fields ..
        for (var hiddenIndex = 0; hiddenIndex < config.hidden_fields.length; hiddenIndex++) {
            var hiddenName = config.hidden_fields[hiddenIndex];
            var hiddenValue = data[hiddenName];
            html += '<input type="hidden" data-field="' + hiddenName + '" value="' + kit._esc_html(String(hiddenValue)) + '">';
        }

        // .. render the save button and status area ..
        html += '<div class="record-edit-footer">';
        html += '<button class="action-button record-edit-save-button" type="button">' + kit.record_edit._labels.save + '</button>';
        html += '<span class="record-edit-status"></span>';
        html += '</div>';

        // .. and inject into the container.
        kit.record_edit._$container.html(html);
        kit.record_edit._$status = kit.record_edit._$container.find('.record-edit-status');
    };

// ////////////////////////////////////////////////////////////////////////

    kit.record_edit.collect = function() {

        var $container = kit.record_edit._$container;
        var out = {};

        // Collect all fields with data-field attribute ..
        $container.find('[data-field]').each(function() {
            var $field = $(this);
            var fieldName = $field.attr('data-field');
            var fieldValue = $field.val();
            out[fieldName] = fieldValue;
        });

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

                var errorMessage = kit.record_edit._labels.save_failed;
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

        $status.removeClass('record-edit-status-success record-edit-status-error record-edit-status-saving');
        $status.addClass('record-edit-status-' + type);
        $status.text(message);

        // .. auto-clear success after a delay.
        if (type === 'success') {
            setTimeout(function() {
                $status.text('');
                $status.removeClass('record-edit-status-success');
            }, 3000);
        }
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
