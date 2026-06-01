(function($) {

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubTopic = new Class({
    toString: function() {
        var template = '<PubSubTopic id:{0} name:{1} description:{2} publisher_count:{3} subscriber_count:{4}>';
        return String.format(template, this.id, this.name, this.description, this.publisher_count, this.subscriber_count);
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubTopic;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.topic.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name']);
    var unique_constraints = [
        {field: 'name', entity_type: 'pubsub_topic', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(constraintIdx, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name);
    });

    // Wire up live name validation on both create and edit fields ..
    $.fn.zato.pubsub.topic.wireNameValidation('#id_name');
    $.fn.zato.pubsub.topic.wireNameValidation('#id_edit-name');

    // .. and block form submission when the name is invalid.
    $.fn.zato.data_table.before_submit_hook = $.fn.zato.pubsub.topic.beforeSubmitHook;
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new pub/sub topic', null);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Edit pub/sub topic', id);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', item.description);
    row += String.format("<td class='ignore' style='text-align:center'>{0}</td>", item.publisher_count);
    row += String.format("<td class='ignore' style='text-align:center'>{0}</td>", item.subscriber_count);
    // row += String.format('<td><a href="/zato/pubsub/topic/{0}/?cluster=1">View</a></td>', encodeURIComponent(item.name));
    row += String.format('<td>{0}</td>', String.format('<a href="javascript:$.fn.zato.pubsub.topic.edit(\'{0}\')">Edit</a>', item.id));
    row += String.format('<td>{0}</td>', String.format('<a href="javascript:$.fn.zato.pubsub.topic.delete_(\'{0}\');">Delete</a>', item.id));
    row += String.format('<td>{0}</td>', String.format('<a href="javascript:$.fn.zato.pubsub.topic.publishMessage(\'{0}\')">Publish a message</a>', item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.description);
    row += String.format("<td class='ignore'>{0}</td>", item.publisher_count);
    row += String.format("<td class='ignore'>{0}</td>", item.subscriber_count);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Pub/sub topic `{0}` deleted',
        'Are you sure you want to delete pub/sub topic `{0}`?',
        true);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.getPublishUrl = function(id) {
    return '/zato/pubsub/topic/publish/' + id + '/';
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.publishMessage = function(id) {

    // Get the item from the data table ..
    var item = $.fn.zato.data_table.data[id];

    // .. and open the invoker overlay.
    $.fn.zato.invoker.open_overlay({
        id: id,
        name: item.name,
        title_prefix: 'Publish a message',
        action_label: 'Publish',
        show_more_options: false,
        history_key: 'zato.pubsub.topic.publish.' + id,
        get_invoke_url_func: $.fn.zato.pubsub.topic.getPublishUrl,
        collect_form_data_func: $.fn.zato.pubsub.topic.collectPublishFormData(item),
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.collectPublishFormData = function(item) {
    return function() {
        var formData = $.fn.zato.invoker.collect_form_data();
        formData['topic_name'] = item.name;
        return formData;
    };
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.wireNameValidation = function(fieldId) {

    var field = $(fieldId);
    if(!field.length) {
        return;
    }

    var timer = null;

    field.on('input', function() {

        // Clear any existing indicator ..
        $.fn.zato.pubsub.topic.clearNameInvalid(field);

        if(timer) {
            clearTimeout(timer);
        }

        var value = field.val().trim();
        if(!value) {
            return;
        }

        // .. debounce at 300ms, same as the uniqueness check ..
        timer = setTimeout(function() {
            $.ajax({
                type: 'POST',
                url: '/zato/pubsub/topic/validate-name/',
                data: {'name': value},
                headers: {'X-CSRFToken': $.cookie('csrftoken')},
                dataType: 'json',
                success: function(response) {
                    if(!response.valid) {
                        $.fn.zato.pubsub.topic.showNameInvalid(field);
                    }
                }
            });
        }, 300);
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.showNameInvalid = function(field) {

    // Remove any existing indicator first ..
    $.fn.zato.pubsub.topic.clearNameInvalid(field);

    // .. create and insert the indicator.
    var indicator = '<span class="zato-name-invalid">Name cannot be used</span>';
    field.after(indicator);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.clearNameInvalid = function(field) {
    field.siblings('.zato-name-invalid').remove();
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.beforeSubmitHook = function(form) {

    var formId = form.attr('id');
    var prefix = formId === 'edit-form' ? 'edit-' : '';
    var field = $('#id_' + prefix + 'name');
    var value = field.val().trim();

    // Clear any previous indicator ..
    $.fn.zato.pubsub.topic.clearNameInvalid(field);

    // .. empty name is handled by the required-field check, but we also validate it here ..
    if(!value) {
        $.fn.zato.pubsub.topic.showNameInvalid(field);
        return false;
    }

    // .. call the backend synchronously to check the name ..
    var isValid = true;

    $.ajax({
        type: 'POST',
        url: '/zato/pubsub/topic/validate-name/',
        data: {'name': value},
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        dataType: 'json',
        async: false,
        success: function(response) {
            if(!response.valid) {
                isValid = false;
            }
        }
    });

    // .. if invalid, show the indicator and block submission.
    if(!isValid) {
        $.fn.zato.pubsub.topic.showNameInvalid(field);
        return false;
    }

    return true;
}

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
