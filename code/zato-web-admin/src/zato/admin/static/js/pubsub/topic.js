(function($) {

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.config = {
    backendTypeBuiltin: 'builtin',
    backendTypeAMQP: 'amqp',
    backendBadgeLabels: {
        'builtin': 'Built-in',
        'amqp': 'AMQP',
    },
    backendBadgeClasses: {
        'builtin': 'zato-topic-backend-badge zato-topic-backend-badge-builtin',
        'amqp': 'zato-topic-backend-badge zato-topic-backend-badge-amqp',
    },
    requiredFieldMessage: 'This field is required',
    createNewValue: 'zato-create-new',
    createOutconnURL: '/zato/outgoing/amqp/?cluster=1&create=1',
    createChannelURL: '/zato/channel/amqp/?cluster=1&create=1',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.highlight = function(text) {
    return '<span class="how-it-works-highlight">' + text + '</span>';
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.fieldDescriptions = {

    'id_name': 'A unique name for this topic.<br>' +
        $.fn.zato.pubsub.topic.highlight('Publishers and subscribers refer to the topic by this name') + '.',

    'id_description': 'An optional, free-form description.<br>' +
        $.fn.zato.pubsub.topic.highlight('It has no effect on how messages flow') + '.',

    'id_backend_type': 'Where messages of this topic live.<br>' +
        'Built-in keeps them inside Zato.<br>' +
        'AMQP hands them over to an external broker.<br>' +
        $.fn.zato.pubsub.topic.highlight('Publishers and subscribers use the topic the same way in both cases') + '.',

    'id_amqp_outconn_name': 'The outgoing AMQP connection that publishes<br>' +
        'messages of this topic to the broker.<br>' +
        $.fn.zato.pubsub.topic.highlight('Required for AMQP topics') + '.',

    'id_amqp_exchange': 'The exchange in the broker that messages<br>' +
        'of this topic are published to.<br>' +
        $.fn.zato.pubsub.topic.highlight('The exchange must already exist in the broker') + '.',

    'id_amqp_routing_key': 'The routing key the broker uses to route<br>' +
        'messages of this topic to queues.<br>' +
        $.fn.zato.pubsub.topic.highlight('The topic name is used when this is empty') + '.',

    'id_amqp_channel_name': 'An AMQP channel that consumes messages<br>' +
        'from a queue in the broker.<br>' +
        $.fn.zato.pubsub.topic.highlight("Messages received by the channel are delivered to this topic's subscribers") + '.',
};

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

    // .. show or hide the AMQP fields whenever the backend type changes ..
    $('#id_backend_type').on('change', function() {
        $.fn.zato.pubsub.topic.toggleAMQPRows('create');
    });

    $('#id_edit-backend_type').on('change', function() {
        $.fn.zato.pubsub.topic.toggleAMQPRows('edit');
    });

    // .. let the create-new option in the AMQP selects open the relevant page ..
    var config = $.fn.zato.pubsub.topic.config;

    $.fn.zato.pubsub.topic.wireCreateNewOption('#id_amqp_outconn_name', config.createOutconnURL);
    $.fn.zato.pubsub.topic.wireCreateNewOption('#id_edit-amqp_outconn_name', config.createOutconnURL);
    $.fn.zato.pubsub.topic.wireCreateNewOption('#id_amqp_channel_name', config.createChannelURL);
    $.fn.zato.pubsub.topic.wireCreateNewOption('#id_edit-amqp_channel_name', config.createChannelURL);

    // .. and block form submission when the name is invalid.
    $.fn.zato.data_table.before_submit_hook = $.fn.zato.pubsub.topic.beforeSubmitHook;
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.wireCreateNewOption = function(fieldId, url) {

    $(fieldId).on('change', function() {

        // Only the create-new option is of interest here ..
        var select = $(this);
        var isCreateNew = select.val() === $.fn.zato.pubsub.topic.config.createNewValue;

        if(!isCreateNew) {
            return;
        }

        // .. open the page where the definition can be created in a new tab ..
        window.open(url, '_blank');

        // .. and reset the select back to its empty option.
        select.val('');
        select.trigger('chosen:updated');
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new pub/sub topic', null);

    // The form may have been reset since it was last open, so sync the AMQP rows with the select ..
    $.fn.zato.pubsub.topic.toggleAMQPRows('create');

    // .. and wire up the field help badge.
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.pubsub.topic.fieldDescriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Edit pub/sub topic', id);

    // The form was just populated with this topic's data, so sync the AMQP rows with the select ..
    $.fn.zato.pubsub.topic.toggleAMQPRows('edit');

    // .. and wire up the field help badge.
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.pubsub.topic.fieldDescriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.toggleAMQPRows = function(action) {

    // Read the current backend type from the form the action refers to ..
    var prefix = action === 'edit' ? 'edit-' : '';
    var backendType = $('#id_' + prefix + 'backend_type').val();

    // .. show the AMQP rows only when the AMQP backend is selected ..
    var isAMQP = backendType === $.fn.zato.pubsub.topic.config.backendTypeAMQP;
    var rows = $('.zato-topic-amqp-row-' + action);
    rows.toggle(isAMQP);

    // .. and let any Chosen selects in the rows recompute their width,
    // .. they render with no width when initialized while hidden.
    if(isAMQP) {
        rows.find('select').trigger('chosen:updated');
    }
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    // Build the backend badge from the topic's backend type ..
    var config = $.fn.zato.pubsub.topic.config;
    var backendBadgeLabel = config.backendBadgeLabels[item.backend_type];
    var backendBadgeClass = config.backendBadgeClasses[item.backend_type];
    var backendBadge = String.format('<span class="{0}">{1}</span>', backendBadgeClass, backendBadgeLabel);

    // .. and assemble the whole row.
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format("<td style='text-align:center'>{0}</td>", backendBadge);
    row += String.format('<td>{0}</td>', item.description || $.fn.zato.empty_value);
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
    row += String.format("<td class='ignore'>{0}</td>", item.backend_type);
    row += String.format("<td class='ignore'>{0}</td>", item.amqp_outconn_name);
    row += String.format("<td class='ignore'>{0}</td>", item.amqp_exchange);
    row += String.format("<td class='ignore'>{0}</td>", item.amqp_routing_key);
    row += String.format("<td class='ignore'>{0}</td>", item.amqp_channel_name);

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

$.fn.zato.pubsub.topic.showFieldRequired = function(field) {

    // Remove any existing indicator first ..
    $.fn.zato.pubsub.topic.clearNameInvalid(field);

    // .. create and insert the indicator.
    var message = $.fn.zato.pubsub.topic.config.requiredFieldMessage;
    var indicator = String.format('<span class="zato-name-invalid">{0}</span>', message);
    field.after(indicator);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.topic.validateAMQPFields = function(prefix) {

    // Only the AMQP backend has required fields to check ..
    var backendType = $('#id_' + prefix + 'backend_type').val();
    var isAMQP = backendType === $.fn.zato.pubsub.topic.config.backendTypeAMQP;

    if(!isAMQP) {
        return true;
    }

    // .. the connection and exchange are both required ..
    var isValid = true;
    var requiredFields = ['amqp_outconn_name', 'amqp_exchange'];

    $.each(requiredFields, function(fieldIdx, fieldName) {

        var field = $('#id_' + prefix + fieldName);
        var value = field.val().trim();

        // .. clear any previous indicator ..
        $.fn.zato.pubsub.topic.clearNameInvalid(field);

        // .. and flag the field if it is empty.
        if(!value) {
            $.fn.zato.pubsub.topic.showFieldRequired(field);
            isValid = false;
        }
    });

    return isValid;
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

    // .. with the name valid, check the AMQP fields too.
    var isAMQPValid = $.fn.zato.pubsub.topic.validateAMQPFields(prefix);

    return isAMQPValid;
}

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
