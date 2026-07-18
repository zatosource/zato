(function($) {

// ////////////////////////////////////////////////////////////////////////
// State
// ////////////////////////////////////////////////////////////////////////

// All the destinations, grouped by vendor.
$.fn.zato.logging.destinations._data = {};

// The id of the destination being edited, per vendor, null means a new one.
$.fn.zato.logging.destinations._editingId = {};

// ////////////////////////////////////////////////////////////////////////
// Rendering
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.destinations._renderList = function(vendor) {
    var destinations = $.fn.zato.logging.destinations;
    var items = destinations._data[vendor];
    var $container = $('#logging-list-' + vendor);

    $container.empty();

    // An empty list gets a placeholder ..
    if (!items.length) {
        var placeholder = document.createElement('div');
        placeholder.className = 'logging-destination-empty';
        placeholder.textContent = 'No destinations yet';
        $container.append(placeholder);
        return;
    }

    // .. otherwise, build one row per destination.
    for (var itemIdx = 0; itemIdx < items.length; itemIdx++) {
        var item = items[itemIdx];

        var row = document.createElement('div');
        row.className = 'logging-destination-item';
        row.setAttribute('data-id', item.id);
        row.setAttribute('data-vendor', vendor);

        if (!item.is_active) {
            row.className = 'logging-destination-item logging-destination-inactive';
        }

        // The name and the address ..
        var text = document.createElement('div');
        text.className = 'logging-destination-text';

        var name = document.createElement('div');
        name.className = 'logging-destination-name';
        name.textContent = item.name;

        var address = document.createElement('span');
        address.className = 'logging-destination-address';
        address.textContent = item.address;

        text.appendChild(name);
        text.appendChild(address);

        // .. the row actions ..
        var controls = document.createElement('div');
        controls.className = 'logging-destination-controls';

        var actionNames = ['Edit', 'Ping', 'Delete'];

        for (var actionIdx = 0; actionIdx < actionNames.length; actionIdx++) {
            var actionName = actionNames[actionIdx];

            var action = document.createElement('a');
            action.className = 'logging-destination-action';
            action.setAttribute('data-action', actionName.toLowerCase());
            action.href = '#';
            action.textContent = actionName;

            controls.appendChild(action);
        }

        // .. and the active toggle.
        var toggle = document.createElement('input');
        toggle.className = 'logging-destination-toggle';
        toggle.type = 'checkbox';
        toggle.checked = item.is_active;

        controls.appendChild(toggle);

        row.appendChild(text);
        row.appendChild(controls);
        $container.append(row);
    }
};

// ////////////////////////////////////////////////////////////////////////
// Form handling
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.destinations._showForm = function(vendor, item) {
    var config = $.fn.zato.logging.config;

    var $form = $('#logging-form-' + vendor);

    // Fill in the fields, either from the destination being edited or with the defaults ..
    $form.find('[data-field]').each(function() {
        var $field = $(this);
        var fieldName = $field.data('field');

        if ($field.attr('type') === 'checkbox') {
            $field.prop('checked', item ? item[fieldName] : true);
        }
        else {
            $field.val(item ? item[fieldName] : '');
        }
    });

    // .. a new Datadog destination starts with the public intake URL ..
    if (!item && vendor === 'datadog') {
        $form.find('[data-field="address"]').val(config.datadogDefaultAddress);
    }

    // .. and switch the footer buttons to the form mode.
    $form.prop('hidden', false);
    $('#logging-add-' + vendor).prop('hidden', true);
    $('#logging-save-' + vendor).prop('hidden', false);
    $('#logging-cancel-' + vendor).prop('hidden', false);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.destinations._hideForm = function(vendor) {
    $('#logging-form-' + vendor).prop('hidden', true);
    $('#logging-add-' + vendor).prop('hidden', false);
    $('#logging-save-' + vendor).prop('hidden', true);
    $('#logging-cancel-' + vendor).prop('hidden', true);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.destinations._collectForm = function(vendor) {
    var out = {};

    $('#logging-form-' + vendor).find('[data-field]').each(function() {
        var $field = $(this);
        var fieldName = $field.data('field');

        if ($field.attr('type') === 'checkbox') {
            out[fieldName] = $field.is(':checked');
        }
        else {
            out[fieldName] = $field.val();
        }
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////
// Server calls
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.destinations._post = function(url, payload, onSuccess, vendor) {
    var logging = $.fn.zato.logging;

    $.ajax({
        type: 'POST',
        url: url,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        data: JSON.stringify(payload),
        contentType: 'application/json',
        dataType: 'json',
        success: onSuccess,
        error: function(jqXHR) {
            var response = JSON.parse(jqXHR.responseText);
            logging.setStatus(vendor, response.error, 'logging-status-error');
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.destinations._save = function(vendor, destination) {
    var logging = $.fn.zato.logging;
    var destinations = logging.destinations;
    var config = logging.config;

    var payload = {vendor: vendor, destination: destination};

    destinations._post(config.destinationSaveUrl, payload, function(response) {
        destinations._data = response.destinations;
        destinations._renderList(vendor);
        destinations._hideForm(vendor);
        logging.setStatus(vendor, 'Destination saved', 'logging-status-saved');
    }, vendor);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.destinations._delete = function(vendor, destinationId) {
    var logging = $.fn.zato.logging;
    var destinations = logging.destinations;
    var config = logging.config;

    var payload = {vendor: vendor, destination_id: destinationId};

    destinations._post(config.destinationDeleteUrl, payload, function(response) {
        destinations._data = response.destinations;
        destinations._renderList(vendor);
        logging.setStatus(vendor, 'Destination deleted', 'logging-status-saved');
    }, vendor);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.destinations._ping = function(vendor, destinationId) {
    var logging = $.fn.zato.logging;
    var destinations = logging.destinations;
    var config = logging.config;

    logging.setStatus(vendor, 'Pinging...');

    var payload = {vendor: vendor, destination_id: destinationId};

    destinations._post(config.destinationPingUrl, payload, function(response) {
        var statusClass = response.success ? 'logging-status-saved' : 'logging-status-error';
        logging.setStatus(vendor, response.details, statusClass);
    }, vendor);
};

// ////////////////////////////////////////////////////////////////////////
// Row lookups
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.destinations._findItem = function(vendor, destinationId) {
    var destinations = $.fn.zato.logging.destinations;
    var items = destinations._data[vendor];

    for (var itemIdx = 0; itemIdx < items.length; itemIdx++) {
        if (items[itemIdx].id === destinationId) {
            return items[itemIdx];
        }
    }
};

// ////////////////////////////////////////////////////////////////////////
// Initialization
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.destinations.init = function(data) {
    var logging = $.fn.zato.logging;
    var destinations = logging.destinations;
    var config = logging.config;

    destinations._data = data;

    for (var vendorIdx = 0; vendorIdx < config.vendors.length; vendorIdx++) {
        var vendor = config.vendors[vendorIdx];

        destinations._editingId[vendor] = null;
        destinations._renderList(vendor);
    }

    // The footer buttons of each vendor tab ..
    $('.logging-card').on('click', '[id^="logging-add-"]', function() {
        var vendor = this.id.replace('logging-add-', '');
        destinations._editingId[vendor] = null;
        destinations._showForm(vendor, null);
    });

    $('.logging-card').on('click', '[id^="logging-cancel-"]', function() {
        var vendor = this.id.replace('logging-cancel-', '');
        destinations._hideForm(vendor);
    });

    $('.logging-card').on('click', '[id^="logging-save-"]', function() {
        var vendor = this.id.replace('logging-save-', '');
        var destination = destinations._collectForm(vendor);

        var editingId = destinations._editingId[vendor];
        if (editingId !== null) {
            destination.id = editingId;
        }

        destinations._save(vendor, destination);
    });

    // .. the per-row action links ..
    $('.logging-card').on('click', '.logging-destination-action', function(event) {
        event.preventDefault();

        var $row = $(this).closest('.logging-destination-item');
        var vendor = $row.data('vendor');
        var destinationId = $row.data('id');
        var actionName = $(this).data('action');

        if (actionName === 'edit') {
            var item = destinations._findItem(vendor, destinationId);
            destinations._editingId[vendor] = destinationId;
            destinations._showForm(vendor, item);
        }
        else if (actionName === 'ping') {
            destinations._ping(vendor, destinationId);
        }
        else if (actionName === 'delete') {
            destinations._delete(vendor, destinationId);
        }
    });

    // .. and the per-row active toggles.
    $('.logging-card').on('change', '.logging-destination-toggle', function() {
        var $row = $(this).closest('.logging-destination-item');
        var vendor = $row.data('vendor');
        var destinationId = $row.data('id');

        var item = destinations._findItem(vendor, destinationId);
        item.is_active = $(this).is(':checked');

        destinations._save(vendor, item);
    });
};

})(jQuery);
