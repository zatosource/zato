// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.pubsub.subscription');

$.fn.zato.data_table.PubSubSubscription = new Class({
    toString: function() {
        var s = '<PubSubSubscription id:{0} topic_name:{1} sec_name:{2} pattern_matched:{3}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.topic_name ? this.topic_name : '(none)',
                                this.sec_name ? this.sec_name : '(none)',
                                this.pattern_matched ? this.pattern_matched : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubSubscription;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.subscription.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([]);
})

$.fn.zato.pubsub.subscription.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.sec_name);
    row += String.format('<td style="text-align:center">{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.delivery_type || 'pull');
    row += String.format('<td>{0}</td>', item.topic_name);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.pubsub.subscription.edit({0});'>Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.pubsub.subscription.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.subscription.create = function() {
    console.log('[DEBUG] pubsub.subscription.create: Starting create function');

    $.fn.zato.data_table._create_edit('create', 'Create a new pub/sub subscription', null);
    // Populate topics and security definitions after form opens
    setTimeout(function() {
        // Initialize SlimSelect after topics are populated via callback
        $.fn.zato.pubsub.common.populateTopics('create', null, '/zato/pubsub/subscription/get-topics/', '#id_topic_id', function() {
            if (window.topicSelectCreate) {
                window.topicSelectCreate.destroy();
            }

            try {
                $('#id_topic_id').attr('multiple', true);

                // Clear any default selections for create form
                $('#id_topic_id option').prop('selected', false);
                window.topicSelectCreate = new SlimSelect({
                    select: '#id_topic_id',
                    settings: {
                        searchPlaceholder: 'Search topics...',
                        placeholderText: 'Select topics',
                        closeOnSelect: false
                    }
                });
                // SlimSelect should automatically read from the original select element

                // Force dropdown to be clickable and visible
                setTimeout(function() {
                    $('.ss-main.topic-select').off('click').on('click', function(e) {
                        if (window.topicSelectCreate && window.topicSelectCreate.open) {
                            window.topicSelectCreate.open();
                        }
                    });

                    // Ensure dropdown content is properly styled
                    $('.ss-content.topic-select').css({
                        'display': 'block',
                        'visibility': 'visible',
                        'z-index': '9999'
                    });
                }, 100);
            } catch (error) {
                // Fallback: show the original select
                $('#id_topic_id').show();
            }
            // Force show SlimSelect container if it's hidden
            $('.ss-main').show();
        });
        $.fn.zato.common.security.populateSecurityDefinitions('create', null, '/zato/pubsub/subscription/get-security-definitions/', '#id_sec_base_id');
        $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('create');
    }, 200);
}

$.fn.zato.pubsub.subscription.edit = function(id) {
    console.log('[DEBUG] pubsub.subscription.edit: Starting edit function for id:', id);

    $.fn.zato.data_table._create_edit('edit', 'Update the pub/sub subscription', id);
    // Populate topics and security definitions after form opens with current selections
    setTimeout(function() {
        // Get the current topic ID from the hidden input field that contains the actual form data
        var currentTopicId = $('input[name="edit-topic_id"]').val();
        if (!currentTopicId) {
            // Fallback: try to get it from the data table row data
            var rowData = $.fn.zato.data_table.data[id];
            if (rowData && rowData.topic_id) {
                currentTopicId = rowData.topic_id;
            }
        }

        var currentSecId = $('#id_edit-sec_base_id').val();
        var currentRestEndpointId = $('#id_edit-rest_push_endpoint_id').val();

        // Initialize SlimSelect after topics are populated via callback
        $.fn.zato.pubsub.common.populateTopics('edit', currentTopicId, '/zato/pubsub/subscription/get-topics/', '#id_edit-topic_id', function() {
            if (window.topicSelectEdit) {
                window.topicSelectEdit.destroy();
            }

            try {
                $('#id_edit-topic_id').attr('multiple', true);

                window.topicSelectEdit = new SlimSelect({
                    select: '#id_edit-topic_id',
                    settings: {
                        searchPlaceholder: 'Search topics...',
                        placeholderText: 'Select topics',
                        closeOnSelect: false
                    }
                });

                // Force dropdown to be clickable and visible for edit form
                setTimeout(function() {
                    $('.ss-main.topic-select').off('click').on('click', function(e) {
                        if (window.topicSelectEdit && window.topicSelectEdit.open) {
                            window.topicSelectEdit.open();
                        }
                    });

                    // Ensure dropdown content is properly styled
                    $('.ss-content.topic-select').css({
                        'display': 'block',
                        'visibility': 'visible',
                        'z-index': '9999'
                    });
                }, 100);
            } catch (error) {
                // Fallback: show the original select
                $('#id_edit-topic_id').show();
            }
            // Force show SlimSelect container if it's hidden
            $('.ss-main').show();
        });
        $.fn.zato.common.security.populateSecurityDefinitions('edit', currentSecId, '/zato/pubsub/subscription/get-security-definitions/', '#id_edit-sec_base_id');
        $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('edit');
    }, 200);
}

$.fn.zato.pubsub.subscription.delete_ = function(id) {

    var instance = $.fn.zato.data_table.data[id];
    var descriptor = 'Security: ' + instance.sec_name + '\nTopic: ' + instance.topic_name + '\nDelivery: ' + (instance.delivery_type || 'pull') + '\n\n';

    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Pub/sub subscription deleted:\n' + descriptor,
        'Are you sure you want to delete pub/sub subscription?\n\n' + descriptor,
        true);
}

$.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility = function(form_type) {
    var deliveryTypeId = form_type === 'create' ? '#id_delivery_type' : '#id_edit-delivery_type';
    var restEndpointSpanId = form_type === 'create' ? '#rest-endpoint-create' : '#rest-endpoint-edit';

    var $deliveryType = $(deliveryTypeId);
    var $restEndpointSpan = $(restEndpointSpanId);

    if ($deliveryType.length === 0 || $restEndpointSpan.length === 0) {
        return;
    }

    function toggleRestEndpointVisibility() {
        if ($deliveryType.val() === 'push') {
            $restEndpointSpan.css('display', 'inline-block');
        } else {
            $restEndpointSpan.hide();
        }
    }

    // Set initial state
    toggleRestEndpointVisibility();

    // Handle delivery type changes
    $deliveryType.on('change', toggleRestEndpointVisibility);
}
