
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.control_numbers.config = {
    set_next_url: '',
    success_message: 'Next number saved',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.control_numbers.show_message = function(is_success, message) {
    var css_class = is_success ? 'user-message-success' : 'user-message-failure';
    $('#user-message').removeClass('user-message-success user-message-failure').addClass(css_class).text(message);
    $('#user-message-div').show();
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.control_numbers.start_edit = function(row) {
    var cell = row.find('td.control-number-next');
    var current = cell.text().trim();

    // Remember the value to restore on cancel
    cell.data('previous-value', current);

    var input = $('<input type="text" class="control-number-input">').val(current);
    var save_link = $('<a href="#" class="control-number-save">Save</a>');
    var cancel_link = $('<a href="#" class="control-number-cancel">Cancel</a>');

    cell.empty().append(input, ' ', save_link, ' ', cancel_link);
    input.focus();
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.control_numbers.cancel_edit = function(row) {
    var cell = row.find('td.control-number-next');
    cell.text(cell.data('previous-value'));
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.control_numbers.save_edit = function(row) {
    var cell = row.find('td.control-number-next');
    var value = cell.find('input.control-number-input').val();

    var request = {
        'sender': row.data('sender'),
        'receiver': row.data('receiver'),
        'kind': row.data('kind'),
        'next_number': value,
    };

    $.ajax({
        type: 'POST',
        url: $.fn.zato.b2b.control_numbers.config.set_next_url,
        data: JSON.stringify(request),
        contentType: 'application/json',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            cell.text(data.next_number);
            $.fn.zato.b2b.control_numbers.show_message(true, data.message);
        },
        error: function(xhr) {
            var data = JSON.parse(xhr.responseText);
            $.fn.zato.b2b.control_numbers.cancel_edit(row);
            $.fn.zato.b2b.control_numbers.show_message(false, data.message);
        }
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.b2b.control_numbers.init = function(config) {
    $.fn.zato.b2b.control_numbers.config.set_next_url = config.set_next_url;

    $('#data-table').on('click', 'a.control-number-edit', function(e) {
        e.preventDefault();
        $.fn.zato.b2b.control_numbers.start_edit($(this).closest('tr'));
    });

    $('#data-table').on('click', 'a.control-number-cancel', function(e) {
        e.preventDefault();
        $.fn.zato.b2b.control_numbers.cancel_edit($(this).closest('tr'));
    });

    $('#data-table').on('click', 'a.control-number-save', function(e) {
        e.preventDefault();
        $.fn.zato.b2b.control_numbers.save_edit($(this).closest('tr'));
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
