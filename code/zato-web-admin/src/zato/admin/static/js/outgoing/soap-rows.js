
// ////////////////////////////////////////////////////////////////////////////
// Outgoing SOAP connections - the request parameter and body-credential rows of the create and edit dialogs,
// each kind read out of a hidden JSON field into rows and serialized back into it before the form is submitted.
// Loaded after soap.js, whose config and field prefix it reads.
// ////////////////////////////////////////////////////////////////////////////

(function($) {

    var config = $.fn.zato.outgoing.soap.config;
    var fieldPrefix = $.fn.zato.outgoing.soap.field_prefix;

    // ////////////////////////////////////////////////////////////////////////

    // Reads a hidden JSON field into the rows it stands for. A field that was never filled in and
    // one holding something other than JSON both mean there are no rows to build.
    function parseRowsField(selector) {

        var value = $(selector).val();

        if(!value) {
            return [];
        }

        try {
            return JSON.parse(value);
        }
        catch(parseError) {
            return [];
        }
    }

    // ////////////////////////////////////////////////////////////////////////
    // Request parameter rows - each row is a key, a value and the value's Text/JSONata mode,
    // serialized to the form's hidden JSON fields before the form is submitted.
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.add_param_row = function(action, kind, key, value, mode) {

        var row = $('<tr class="request-param-row"></tr>');

        var jsonataCell = $('<td class="request-param-jsonata-cell"></td>');
        var jsonataCheckbox = $('<input type="checkbox" class="request-param-jsonata" title="Evaluate the value as JSONata">');

        if(mode === config.jsonataMode) {
            jsonataCheckbox.prop('checked', true);
        }

        jsonataCell.append(jsonataCheckbox);

        var keyCell = $('<td class="request-param-key-cell"></td>');
        var keyInput = $('<input type="text" class="request-param-key" placeholder="Name">');

        if(key) {
            keyInput.val(key);
        }

        keyCell.append(keyInput);

        var valueCell = $('<td class="request-param-value-cell"></td>');
        var valueInput = $('<input type="text" class="request-param-value" placeholder="Value">');

        if(value) {
            valueInput.val(value);
        }

        valueCell.append(valueInput);

        var removeCell = $('<td class="request-param-remove-cell"></td>');
        var removeLink = $('<a href="javascript:void(0)" class="request-param-remove" title="Remove" aria-label="Remove"></a>');
        removeLink.append($.fn.zato.new_remove_icon());
        removeCell.append(removeLink);

        row.append(jsonataCell);
        row.append(keyCell);
        row.append(valueCell);
        row.append(removeCell);

        $('#request-' + kind + '-rows-' + action).append(row);

        // A newly added row is ready to be typed into right away
        keyInput.focus();
    };

    // ////////////////////////////////////////////////////////////////////////

    function paramRowsField(action, kind) {
        return '#id_' + fieldPrefix(action) + 'request_' + kind;
    }

    // ////////////////////////////////////////////////////////////////////////

    function populateParamRows(action) {

        $.each(config.paramKinds, function(ignored, kind) {

            var container = $('#request-' + kind + '-rows-' + action);
            container.empty();

            var items = parseRowsField(paramRowsField(action, kind));

            for(var itemIdx = 0; itemIdx < items.length; itemIdx++) {
                var item = items[itemIdx];
                $.fn.zato.outgoing.soap.add_param_row(action, kind, item.key, item.value, item.mode);
            }
        });
    }

    // ////////////////////////////////////////////////////////////////////////

    function serializeParamRows(action) {

        $.each(config.paramKinds, function(ignored, kind) {

            var rows = [];

            $('#request-' + kind + '-rows-' + action).find('.request-param-row').each(function() {

                var row = $(this);
                var key = row.find('.request-param-key').val().trim();

                // A row whose name was left blank is not a parameter at all.
                if(!key) {
                    return;
                }

                var isJsonata = row.find('.request-param-jsonata').prop('checked');
                var mode = config.textMode;

                if(isJsonata) {
                    mode = config.jsonataMode;
                }

                rows.push({
                    key: key,
                    value: row.find('.request-param-value').val(),
                    mode: mode
                });
            });

            // No rows at all is stored as nothing rather than as an empty JSON list, which is what
            // the server side reads as a connection having configured none.
            var stored = '';

            if(rows.length) {
                stored = JSON.stringify(rows);
            }

            $(paramRowsField(action, kind)).val(stored);
        });
    }

    // ////////////////////////////////////////////////////////////////////////
    // Body-credential mapping rows
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.add_body_credential_row = function(action, name, position) {

        var row = $('<div class="body-credential-row"></div>');

        var nameInput = $('<input type="text" class="body-credential-name" placeholder="Element name">');

        if(name) {
            nameInput.val(name);
        }

        var positionInput = $('<input type="number" class="body-credential-position" placeholder="Position" min="1">');

        if(position) {
            positionInput.val(position);
        }

        var removeLink = $('<a href="javascript:void(0)" class="body-credential-remove">Remove</a>');

        row.append(nameInput);
        row.append(positionInput);
        row.append(removeLink);

        $('#body-credentials-' + action).append(row);
    };

    // ////////////////////////////////////////////////////////////////////////

    function bodyCredentialsField(action) {
        return '#id_' + fieldPrefix(action) + 'body_credentials';
    }

    // ////////////////////////////////////////////////////////////////////////

    function populateBodyCredentialRows(action) {

        var container = $('#body-credentials-' + action);
        container.empty();

        var items = parseRowsField(bodyCredentialsField(action));

        for(var itemIdx = 0; itemIdx < items.length; itemIdx++) {
            var item = items[itemIdx];
            $.fn.zato.outgoing.soap.add_body_credential_row(action, item.name, item.position);
        }
    }

    // ////////////////////////////////////////////////////////////////////////

    function serializeBodyCredentialRows(action) {

        var rows = [];

        $('#body-credentials-' + action).find('.body-credential-row').each(function() {

            var row = $(this);
            var name = row.find('.body-credential-name').val().trim();

            // A mapping without an element name names nothing.
            if(!name) {
                return;
            }

            var mapping = {name: name};
            var position = row.find('.body-credential-position').val();

            // A mapping without a position prepends, which is what leaving the field empty means.
            if(position) {
                mapping.position = parseInt(position, 10);
            }

            rows.push(mapping);
        });

        var stored = '';

        if(rows.length) {
            stored = JSON.stringify(rows);
        }

        $(bodyCredentialsField(action)).val(stored);
    }

    // ////////////////////////////////////////////////////////////////////////
    // What the dialogs call - both kinds of rows populated and serialized together
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.rows = {

        populate: function(action) {
            populateBodyCredentialRows(action);
            populateParamRows(action);
        },

        serialize: function(action) {
            serializeBodyCredentialRows(action);
            serializeParamRows(action);
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    $(document).ready(function() {

        // Removing a body-credential mapping row ..
        $(document).on('click', '.body-credential-remove', function() {
            $(this).closest('.body-credential-row').remove();
            return false;
        });

        // .. and a request parameter row.
        $(document).on('click', '.request-param-remove', function() {
            $(this).closest('.request-param-row').remove();
            return false;
        });
    });

    // ////////////////////////////////////////////////////////////////////////

})(jQuery);
