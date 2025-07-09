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
        $('#rest-endpoint-edit').hide();

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
    console.log('[DEBUG] populateRestEndpoints: Called with form_type:', form_type, 'selectedId:', selectedId);

    var selectId = form_type === 'create' ? '#id_rest_push_endpoint_id' : '#id_edit-rest_push_endpoint_id';
    var $select = $(selectId);

    console.log('[DEBUG] populateRestEndpoints: Select ID:', selectId, 'element found:', $select.length > 0);

    if ($select.length === 0) {
        console.log('[DEBUG] populateRestEndpoints: Select element not found:', selectId);
        return;
    }

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
            console.log('[DEBUG] populateRestEndpoints: Received endpoints:', response.rest_endpoints);

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
        },
        error: function(xhr, status, error) {
            console.log('[DEBUG] populateRestEndpoints: Error loading endpoints:', error);
        }
    });
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
    row += String.format('<td style="text-align:center">{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.delivery_type || 'pull');
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

        // Setup delivery type visibility first, then populate REST endpoints for create form
        $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('create');
        $.fn.zato.pubsub.subscription.populateRestEndpoints('create', null);
    }, 200);
}

$.fn.zato.pubsub.subscription.edit = function(sub_key) {
    console.log('[DEBUG] pubsub.subscription.edit: Starting edit function for sub_key:', JSON.stringify(sub_key));
    console.log('[DEBUG] Full data table data:', $.fn.zato.data_table.data);

    // Hide REST endpoint span immediately to prevent flicker during form population
    console.log('[DEBUG] Edit: Hiding REST endpoint span immediately');
    $('#rest-endpoint-edit').hide();

    $.fn.zato.data_table._create_edit('edit', 'Update the pub/sub subscription', sub_key);
    // Populate topics and security definitions after form opens with current selections
    setTimeout(function() {
        // Set the sub_key in the hidden field
        $('#id_edit-sub_key').val(sub_key);
        console.log('[DEBUG] Set sub_key field to:', JSON.stringify(sub_key));

        // Get the current topic names from the data table row data
        var currentTopicNames = null;
        var rowData = $.fn.zato.data_table.data[sub_key];
        console.log('[DEBUG] Edit: Full row data for sub_key:', JSON.stringify({sub_key: sub_key, rowData: rowData}));

        if (rowData && rowData.topic_name) {
            console.log('[DEBUG] Edit: Raw topic_name:', JSON.stringify({value: rowData.topic_name, type: typeof rowData.topic_name}));
            // Convert comma-separated string to array of topic names
            currentTopicNames = rowData.topic_name.split(',').map(function(name) {
                return name.trim();
            });
            console.log('[DEBUG] Edit: Parsed topic names to array:', JSON.stringify(currentTopicNames));
        } else {
            console.log('[DEBUG] Edit: No topic names found in row data');
        }

        var currentSecId = $('#id_edit-sec_base_id').val();
        var currentRestEndpointId = $('#id_edit-rest_push_endpoint_id').val();

        // Initialize SlimSelect after topics are populated via callback
        console.log('[DEBUG] Edit: About to call populateTopics with currentTopicNames:', JSON.stringify(currentTopicNames));
        $.fn.zato.pubsub.common.populateTopics('edit', currentTopicNames, '/zato/pubsub/subscription/get-topics/', '#id_edit-topic_id', function() {
            console.log('[DEBUG] Edit: populateTopics callback triggered');
            console.log('[DEBUG] Edit: Select element HTML after populate:', JSON.stringify($('#id_edit-topic_id')[0].outerHTML));
            console.log('[DEBUG] Edit: Selected options after populate:', JSON.stringify($('#id_edit-topic_id option:selected').map(function() { return {value: this.value, text: this.text}; }).get()));

            if (window.topicSelectEdit) {
                console.log('[DEBUG] Edit: Destroying existing SlimSelect');
                window.topicSelectEdit.destroy();
            }

            try {
                $('#id_edit-topic_id').attr('multiple', true);
                console.log('[DEBUG] Edit: Set multiple attribute on select');

                console.log('[DEBUG] Edit: Creating new SlimSelect instance');
                window.topicSelectEdit = new SlimSelect({
                    select: '#id_edit-topic_id',
                    settings: {
                        searchPlaceholder: 'Search topics...',
                        placeholderText: 'Select topics',
                        closeOnSelect: false
                    }
                });
                console.log('[DEBUG] Edit: SlimSelect created successfully');
                console.log('[DEBUG] Edit: SlimSelect getSelected():', JSON.stringify(window.topicSelectEdit.getSelected()));

                // Hide the original select element
                $('#id_edit-topic_id').hide();
                console.log('[DEBUG] Edit: Original select hidden');

                // The topics should already be selected from the HTML options

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

        // Debug: Check delivery type before setup
        var currentDeliveryType = $('#id_edit-delivery_type').val();
        console.log('[DEBUG] Edit: Current delivery type before setup:', currentDeliveryType);
        console.log('[DEBUG] Edit: REST endpoint span visibility before setup:', $('#rest-endpoint-edit').css('display'));

        // Immediately hide REST endpoint span if not push to prevent flicker
        if (currentDeliveryType !== 'push') {
            console.log('[DEBUG] Edit: Pre-hiding REST endpoint span for non-push delivery type');
            $('#rest-endpoint-edit').hide();
        }

        // Setup delivery type visibility first, then conditionally populate REST endpoints
        $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('edit');

        // Debug: Check after setup
        console.log('[DEBUG] Edit: REST endpoint span visibility after setup:', $('#rest-endpoint-edit').css('display'));

        // Only populate REST endpoints if delivery type is push
        if (currentDeliveryType === 'push') {
            console.log('[DEBUG] Edit: Populating REST endpoints for push delivery type');
            $.fn.zato.pubsub.subscription.populateRestEndpoints('edit', currentRestEndpointId);
        } else {
            console.log('[DEBUG] Edit: Skipping REST endpoints population for delivery type:', currentDeliveryType);
        }
    }, 200);
}

$.fn.zato.pubsub.subscription.stripHtml = function(html) {
    var temp = document.createElement('div');
    temp.innerHTML = html;
    return temp.textContent || temp.innerText || '';
};

$.fn.zato.pubsub.subscription.delete_ = function(id) {
    var instance = $.fn.zato.data_table.data[id];

    if (!instance) {
        return;
    }

    var cleanTopicName = $.fn.zato.pubsub.subscription.stripHtml(instance.topic_name);
    var descriptor = 'Security: ' + instance.sec_name + '\nTopic: ' + cleanTopicName + '\nDelivery: ' + (instance.delivery_type || 'pull') + '\n\n';

    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Pub/sub subscription deleted:\n' + descriptor,
        'Are you sure you want to delete pub/sub subscription?\n\n' + descriptor,
        true);
}

$.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility = function(form_type) {
    console.log('[DEBUG] setupDeliveryTypeVisibility: Called with form_type:', form_type);

    var deliveryTypeId = form_type === 'create' ? '#id_delivery_type' : '#id_edit-delivery_type';
    var restEndpointSpanId = form_type === 'create' ? '#rest-endpoint-create' : '#rest-endpoint-edit';

    console.log('[DEBUG] setupDeliveryTypeVisibility: IDs - deliveryType:', deliveryTypeId, 'restEndpointSpan:', restEndpointSpanId);

    var $deliveryType = $(deliveryTypeId);
    var $restEndpointSpan = $(restEndpointSpanId);

    console.log('[DEBUG] setupDeliveryTypeVisibility: Elements found - deliveryType:', $deliveryType.length, 'restEndpointSpan:', $restEndpointSpan.length);

    if ($deliveryType.length === 0 || $restEndpointSpan.length === 0) {
        console.log('[DEBUG] setupDeliveryTypeVisibility: Missing elements, returning');
        return;
    }

    console.log('[DEBUG] setupDeliveryTypeVisibility: Current delivery type value:', $deliveryType.val());
    console.log('[DEBUG] setupDeliveryTypeVisibility: Current REST span display:', $restEndpointSpan.css('display'));

    function toggleRestEndpointVisibility() {
        var deliveryTypeValue = $deliveryType.val();
        console.log('[DEBUG] toggleRestEndpointVisibility: Called with delivery type:', deliveryTypeValue);

        if (deliveryTypeValue === 'push') {
            console.log('[DEBUG] toggleRestEndpointVisibility: Showing REST endpoint span');
            $restEndpointSpan.css('display', 'inline-block');
        } else {
            console.log('[DEBUG] toggleRestEndpointVisibility: Hiding REST endpoint span');
            $restEndpointSpan.hide();
        }

        console.log('[DEBUG] toggleRestEndpointVisibility: Final REST span display:', $restEndpointSpan.css('display'));
    }

    // Set initial state
    console.log('[DEBUG] setupDeliveryTypeVisibility: Setting initial state');
    toggleRestEndpointVisibility();
    console.log('[DEBUG] setupDeliveryTypeVisibility: Initial state set');

    // Handle delivery type changes
    console.log('[DEBUG] setupDeliveryTypeVisibility: Setting up change handler');
    $deliveryType.on('change', toggleRestEndpointVisibility);
    console.log('[DEBUG] setupDeliveryTypeVisibility: Change handler set up complete');
}
