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

    // Override the close function to clean up spinners and selects
    var originalClose = $.fn.zato.data_table.close;
    $.fn.zato.data_table.close = function(elem) {
        // Clean up any spinners and reset visibility states
        $('.loading-spinner').remove();
        $('.topic-select, .security-select').removeClass('hide');
        $('#id_topic_id, #id_edit-topic_id, #id_sec_base_id, #id_edit-sec_base_id').hide();
        $('#rest-endpoint-edit, #rest-endpoint-create').hide();

        // Call the original close function
        return originalClose(elem);
    };

    // Override the create_edit function to ensure proper cleanup before opening a new form
    var originalCreateEdit = $.fn.zato.data_table._create_edit;
    $.fn.zato.data_table._create_edit = function(form_type, title, id) {
        // Clean up any previous state completely
        $('.loading-spinner').remove();
        $('.ss-main').remove();

        // Destroy any existing SlimSelect instances
        if (window.topicSelectCreate) {
            try { window.topicSelectCreate.destroy(); } catch (e) {}
            window.topicSelectCreate = null;
        }
        if (window.topicSelectEdit) {
            try { window.topicSelectEdit.destroy(); } catch (e) {}
            window.topicSelectEdit = null;
        }

        // Reset select element visibility
        $('#id_topic_id, #id_edit-topic_id, #id_sec_base_id, #id_edit-sec_base_id').hide();

        // Ensure REST endpoint spans are hidden before opening any form
        $('#rest-endpoint-create, #rest-endpoint-edit').hide();

        // Reset delivery type to pull (default)
        if (form_type === 'create') {
            $('#id_delivery_type').val('pull');
        }

        // Call the original create_edit function
        return originalCreateEdit(form_type, title, id);
    };

    // Override the on_submit function to add validation
    var originalOnSubmit = $.fn.zato.data_table.on_submit;
    $.fn.zato.data_table.on_submit = function(action) {
        // Validate push delivery type
        var deliveryTypeId = action === 'create' ? '#id_delivery_type' : '#id_edit-delivery_type';
        var restEndpointId = action === 'create' ? '#id_rest_push_endpoint_id' : '#id_edit-rest_push_endpoint_id';

        var deliveryType = $(deliveryTypeId).val();
        var restEndpoint = $(restEndpointId).val();

        if (deliveryType === 'push' && (!restEndpoint || restEndpoint === '')) {
            alert('Please select a REST endpoint when using Push delivery type.');
            return false;
        }

        // Call original on_submit if validation passes
        return originalOnSubmit.call(this, action);
    };
})

// Function to populate REST endpoints
$.fn.zato.pubsub.subscription.populateRestEndpoints = function(form_type, selectedId) {
    var selectId = form_type === 'create' ? '#id_rest_push_endpoint_id' : '#id_edit-rest_push_endpoint_id';
    var $select = $(selectId);
    var spanId = form_type === 'create' ? '#rest-endpoint-create' : '#rest-endpoint-edit';
    var $span = $(spanId);

    if ($select.length === 0) {
        return;
    }

    // Hide span to prevent flicker during loading
    $span.hide();

    // Clear existing options
    $select.empty();
    $select.append('<option value="">Select a REST endpoint</option>');

    // Get cluster ID
    var clusterId = $('#cluster_id').val();

    $.ajax({
        url: '/zato/pubsub/subscription/get-rest-endpoints/',
        type: 'GET',
        data: {
            cluster_id: clusterId,
            form_type: form_type
        },
        success: function(response) {
            if (response.rest_endpoints && response.rest_endpoints.length > 0) {
                $.each(response.rest_endpoints, function(index, endpoint) {
                    var selected = selectedId && selectedId == endpoint.id ? 'selected="selected"' : '';
                    $select.append('<option value="' + endpoint.id + '" ' + selected + '>' + endpoint.name + '</option>');
                });
            }

            // Trigger chosen update if using chosen plugin
            if ($select.hasClass('chosen-select') || $select.next('.chosen-container').length > 0) {
                $select.trigger('chosen:updated');
            }

            // Show the span only if this is a push delivery type and we have a selected value
            var deliveryType = form_type === 'create' ? $('#id_delivery_type').val() : $('#id_edit-delivery_type').val();
            if (deliveryType === 'push') {
                $span.show();
            }
        },
        error: function(xhr, status, error) {
            console.log('Error loading endpoints:', error);
        }
    });
};

$.fn.zato.pubsub.subscription.data_table = {};

// Hook to ensure the UUID sub_key is properly preserved in the data
$.fn.zato.data_table.add_row_hook = function(instance, name, html_elem, data) {
    // Make sure to preserve the real UUID sub_key from server response
    if (name === 'sub_key' && data && data.sub_key && typeof data.sub_key === 'string' && data.sub_key.indexOf('-') > -1) {
        instance.sub_key = data.sub_key;
    }
};

$.fn.zato.pubsub.subscription.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.sec_name);
    // Use the UUID sub_key if available, otherwise show the ID
    var displaySubKey = (typeof item.sub_key === 'string' && item.sub_key.indexOf('-') > -1) ? item.sub_key : item.id;
    row += String.format('<td>{0}</td>', displaySubKey);
    row += String.format('<td style="text-align:center">{0}</td>', is_active ? 'Yes' : 'No');

    // For Push delivery type, add a link to the REST endpoint if available
    if(item.delivery_type === 'pull') {
        row += String.format('<td>{0}</td>', 'Pull');
    } else {
        // Push delivery type with endpoint
        if(item.rest_push_endpoint_id) {
            var endpointName = '';
            var selectIds = ['#id_edit-rest_push_endpoint_id', '#id_rest_push_endpoint_id'];

            // Check both selects for the endpoint name
            for(var i=0; i<selectIds.length; i++) {
                $(selectIds[i] + ' option').each(function() {
                    if($(this).val() == item.rest_push_endpoint_id) {
                        endpointName = $(this).text();
                        return false;
                    }
                });

                if(endpointName) break;
            }

            // Add the endpoint link to the row
            row += String.format('<td>Push <a href="/zato/http-soap/?cluster=1&query={0}&connection=outgoing&transport=plain_http">{1}</a></td>',
                encodeURIComponent(endpointName), endpointName);
        } else {
            row += String.format('<td>Push</td>');
        }
    }
    // Convert topic names to links (only if not already HTML links)
    var topicLinksHtml = '';
    if (item.topic_name) {
        // Check if topic_name already contains HTML links
        if (item.topic_name.indexOf('<a href=') !== -1) {
            // Already contains HTML links, use as-is
            topicLinksHtml = item.topic_name;
        } else {
            // Plain text topic names, convert to links
            var topicNames = item.topic_name.split(', ');
            var topicLinks = topicNames.map(function(topicName) {
                var trimmedName = topicName.trim();
                return String.format('<a href="/zato/pubsub/topic/?cluster=1&query={0}">{1}</a>',
                                    encodeURIComponent(trimmedName), trimmedName);
            });
            topicLinksHtml = topicLinks.join(', ');
        }
    }
    row += String.format('<td>{0}</td>', topicLinksHtml);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.pubsub.subscription.edit({0});\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.pubsub.subscription.delete_({0});\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.delivery_type || '');
    row += String.format("<td class='ignore'>{0}</td>", item.rest_push_endpoint_id || '');
    row += String.format("<td class='ignore'>{0}</td>", (typeof item.sub_key === 'string' && item.sub_key.indexOf('-') > -1) ? item.sub_key : '');

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.subscription.create = function() {
    // Hide REST endpoint span immediately before form opens
    $('#rest-endpoint-create').hide();

    $.fn.zato.data_table._create_edit('create', 'Create a pub/sub subscription', null);
    // Populate topics and security definitions after form opens
    setTimeout(function() {
        // Initialize SlimSelect after topics are populated via callback
        $.fn.zato.pubsub.common.populateTopics('create', null, '/zato/pubsub/subscription/get-topics/', '#id_topic_id', function() {
            if (window.topicSelectCreate) {
                window.topicSelectCreate.destroy();
            }

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
            // Force show SlimSelect container if it's hidden
            $('.ss-main').show();
        });
        $.fn.zato.common.security.populateSecurityDefinitions('create', null, '/zato/pubsub/subscription/get-security-definitions/', '#id_sec_base_id');

        // Setup delivery type visibility first, then populate REST endpoints for create form
        $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('create');
        $.fn.zato.pubsub.subscription.populateRestEndpoints('create', null);
    }, 200);
}

$.fn.zato.pubsub.subscription.edit = function(sub_key) {
    // Convert sub_key to numeric ID if it's a string but contains numeric ID
    var id = sub_key;
    if (typeof sub_key === 'string' && sub_key.match(/^\d+$/)) {
        id = parseInt(sub_key, 10);
    }

    // Hide REST endpoint span immediately to prevent flicker during form population
    $('#rest-endpoint-edit').hide();

    $.fn.zato.data_table._create_edit('edit', 'Update the pub/sub subscription', id);
    // Populate topics and security definitions after form opens with current selections
    setTimeout(function() {
        // Set the sub_key in the hidden field
        $('#id_edit-sub_key').val(sub_key);

        // Get the current topic names from the data table row data
        var currentTopicNames = null;

        var instance = $.fn.zato.data_table.data[id];

        if (instance && instance.topic_name) {
            // Convert comma-separated string to array of topic names
            currentTopicNames = instance.topic_name.split(',').map(function(name) {
                return name.trim();
            });
        } else {
        }

        var currentSecId = $('#id_edit-sec_base_id').val();
        var currentRestEndpointId = instance ? (instance.rest_push_endpoint_id || '') : '';



        // Initialize SlimSelect after topics are populated via callback
        $.fn.zato.pubsub.common.populateTopics('edit', currentTopicNames, '/zato/pubsub/subscription/get-topics/', '#id_edit-topic_id', function() {
            if (window.topicSelectEdit) {
                window.topicSelectEdit.destroy();
            }

            $('#id_edit-topic_id').attr('multiple', true);

            window.topicSelectEdit = new SlimSelect({
                select: '#id_edit-topic_id',
                settings: {
                    searchPlaceholder: 'Search topics...',
                    placeholderText: 'Select topics',
                    closeOnSelect: false
                }
            });

            // Hide the original select element
            $('#id_edit-topic_id').hide();

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
            // Force show SlimSelect container if it's hidden
            $('.ss-main').show();
        });
        $.fn.zato.common.security.populateSecurityDefinitions('edit', currentSecId, '/zato/pubsub/subscription/get-security-definitions/', '#id_edit-sec_base_id');

        // Immediately hide REST endpoint span if not push to prevent flicker
        var currentDeliveryType = $('#id_edit-delivery_type').val();
        if (currentDeliveryType !== 'push') {
            $('#rest-endpoint-edit').hide();
        }

        // Setup delivery type visibility first, then conditionally populate REST endpoints
        $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('edit');

        // Populate REST endpoints regardless of delivery type to avoid a flicker
        // when switching to push, but they'll remain hidden if not push type
        $.fn.zato.pubsub.subscription.populateRestEndpoints('edit', currentRestEndpointId);
    }, 200);
}

$.fn.zato.pubsub.subscription.stripHtml = function(html) {
    var temp = document.createElement('div');
    temp.innerHTML = html;
    return temp.textContent || temp.innerText || "";
};

// Callback function for create/edit forms
$.fn.zato.pubsub.subscription.create_edit_submit = function(data, status, xhr) {
    var ret_data = $.parseJSON(data.responseText);

    // Publish message to status_msg topic
    $.fn.zato.user_message(ret_data.message);

    if(ret_data.has_error) {
        return false;
    } else {
        $.fn.zato.data_table.refresh();
        return true;
    }
}

$.fn.zato.pubsub.subscription.delete_ = function(id) {
    var instance = $.fn.zato.data_table.data[id];

    if (!instance) {
        return;
    }

    var cleanTopicName = $.fn.zato.pubsub.subscription.stripHtml(instance.topic_name);
    var descriptor = 'Security: ' + instance.sec_name + '\nTopic: ' + cleanTopicName + '\nDelivery: ' + (instance.delivery_type || 'pull');

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

    // Hide the span immediately to prevent any flash
    $restEndpointSpan.hide();

    if ($deliveryType.length === 0 || $restEndpointSpan.length === 0) {
        return;
    }

    function toggleRestEndpointVisibility() {
        var deliveryTypeValue = $deliveryType.val();

        // Instead of immediately showing, prepare for showing but let the populateRestEndpoints function
        // handle the actual visibility after endpoints are loaded
        if (deliveryTypeValue === 'push') {
            // Call populateRestEndpoints which will handle the visibility
            var selectedId = form_type === 'edit' ? $.fn.zato.data_table.data[$("#id_edit-sub_key").val()].rest_push_endpoint_id : null;
            $.fn.zato.pubsub.subscription.populateRestEndpoints(form_type, selectedId);
        } else {
            $restEndpointSpan.hide();
        }
    }

    // Set initial state
    toggleRestEndpointVisibility();

    // Handle delivery type changes
    $deliveryType.on('change', toggleRestEndpointVisibility);
}
