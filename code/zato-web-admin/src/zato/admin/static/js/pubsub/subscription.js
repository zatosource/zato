// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.pubsub.subscription');

$.fn.zato.data_table.PubSubSubscription = new Class({
    toString: function() {
        var s = '<PubSubSubscription id:{0} topic_links:{1} sec_name:{2} pattern_matched:{3}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.topic_links ? this.topic_links : '(none)',
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
        $('#push-service-edit, #push-service-create').hide();
        $('#push-type-edit, #push-type-create').hide();

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

        // Ensure REST endpoint, service and push type spans are hidden before opening any form
        $('#rest-endpoint-create, #rest-endpoint-edit').hide();
        $('#push-service-create, #push-service-edit').hide();
        $('#push-type-create, #push-type-edit').hide();

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
$.fn.zato.pubsub.subscription.populateRestEndpoints = function(form_type, selectedId, showSpan) {
    // Default showSpan to true if not specified
    showSpan = (showSpan !== false);

    var selectId = form_type === 'create' ? '#id_rest_push_endpoint_id' : '#id_edit-rest_push_endpoint_id';
    var $select = $(selectId);
    var spanId = form_type === 'create' ? '#rest-endpoint-create' : '#rest-endpoint-edit';
    var $span = $(spanId);
    var pushTypeId = form_type === 'create' ? '#id_push_type' : '#id_edit-push_type';
    var currentPushType = $(pushTypeId).val();

    if ($select.length === 0) {
        return;
    }

    // Clear existing options
    $select.empty();
    $select.append('<option value="">Select a REST endpoint</option>');

    // Get cluster ID
    var clusterId = $('#cluster_id').val() || $('#id_edit-cluster_id').val();
    if (!clusterId) {
        return;
    }

    $.ajax({
        url: '/zato/pubsub/subscription/get-rest-endpoints/',
        type: 'GET',
        data: {
            cluster_id: clusterId,
            form_type: form_type
        },
        success: function(response) {
            $select.empty();
            $select.append($('<option>', {
                value: '',
                text: 'Select a REST endpoint'
            }));

            var endpoints;
            try {
                // Check if response is already an object or needs parsing
                if (typeof response === 'object') {
                    endpoints = response.rest_endpoints || [];
                } else {
                    endpoints = $.parseJSON(response).rest_endpoints || [];
                }
            } catch (e) {
                console.error('Error parsing REST endpoints:', e, 'Response:', response);
                endpoints = [];
            }

            $.each(endpoints, function(idx, endpoint) {
                $select.append($('<option>', {
                    value: endpoint.id,
                    text: endpoint.name
                }));
            });

            if(selectedId) {
                $select.val(selectedId);
            }

            // If Chosen plugin is being used
            if ($select.next('.chosen-container').length > 0) {
                // Trigger Chosen update to refresh the dropdown
                $select.trigger('chosen:updated');
            } else {
                // Initialize Chosen with the original width
                $select.chosen({width: '98%'});
            }

            // Only show the span if explicitly requested and the current push type is 'rest'
            var deliveryType = form_type === 'create' ? $('#id_delivery_type').val() : $('#id_edit-delivery_type').val();
            var shouldShow = showSpan && deliveryType === 'push' && currentPushType === 'rest';

            // Don't change visibility if we're just preloading
            if (showSpan) {
                if (shouldShow) {
                    $span.show();
                } else {
                    $span.hide();
                }
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading REST endpoints:', error);
        }
    });
};

// Function to populate Services
$.fn.zato.pubsub.subscription.populateServices = function(form_type, selectedId, showSpan) {
    // Default showSpan to true if not specified
    showSpan = (showSpan !== false);

    var cluster_id = $('#cluster_id').val() || $('#id_edit-cluster_id').val();
    if (!cluster_id) {
        return;
    }

    var serviceSelectId = form_type === 'create' ? '#id_push_service_name' : '#id_edit-push_service_name';
    var $serviceSelect = $(serviceSelectId);
    var serviceSpanId = form_type === 'create' ? '#push-service-create' : '#push-service-edit';
    var $serviceSpan = $(serviceSpanId);
    var pushTypeId = form_type === 'create' ? '#id_push_type' : '#id_edit-push_type';
    var currentPushType = $(pushTypeId).val();

    if ($serviceSelect.length === 0) {
        return;
    }

    // Clear existing options
    $serviceSelect.empty();
    $serviceSelect.append('<option value="">Select a service</option>');

    $.get('/zato/pubsub/subscription/get-service-list/', {
        cluster_id: cluster_id,
        form_type: form_type
    })
    .done(function(response) {
        if ($serviceSelect.length === 0) {
            return;
        }

        $serviceSelect.empty();
        $serviceSelect.append('<option value="">Select a service</option>');

        if (response.services && response.services.length > 0) {
            response.services.forEach(function(service) {
                var option = $('<option></option>')
                    .attr('value', service.service_name)
                    .text(service.service_name);
                if (selectedId && service.service_name === selectedId) {
                    option.attr('selected', 'selected');
                }
                $serviceSelect.append(option);
            });
        }

        // If Chosen plugin is being used
        if ($serviceSelect.next('.chosen-container').length > 0) {
            // Trigger Chosen update to refresh the dropdown
            $serviceSelect.trigger('chosen:updated');
        } else {
            // Initialize Chosen with the original width
            $serviceSelect.chosen({width: '163%'});
        }

        // Only show the span if explicitly requested and the current push type is 'service'
        var deliveryType = form_type === 'create' ? $('#id_delivery_type').val() : $('#id_edit-delivery_type').val();
        var shouldShow = showSpan && deliveryType === 'push' && currentPushType === 'service';

        // Don't change visibility if we're just preloading
        if (showSpan) {
            if (shouldShow) {
                $serviceSpan.show();
            } else {
                $serviceSpan.hide();
            }
        }
    })
    .fail(function(xhr, status, error) {
        console.error('Error loading services:', error);
    });
}

$.fn.zato.pubsub.subscription.data_table = {};

$.fn.zato.data_table.add_row_hook = function(instance, name, html_elem, data) {

    if (name === 'sub_key') {
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
    row += String.format('<td><a href="/zato/security/basic-auth/?cluster=1&query={0}">{1}</a></td>', encodeURIComponent(item.sec_name), item.sec_name);

    row += String.format('<td>{0}</td>', item.sub_key);
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
    if (item.topic_links) {
        // Check if topic_links already contains HTML links
        if (item.topic_links.indexOf('<a href=') !== -1) {
            // Use as-is, already HTML links
            topicLinksHtml = item.topic_links;
        } else {
            // Convert to HTML links
            var topicNames = item.topic_links.split(', ');
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
    row += String.format("<td class='ignore'>{0}</td>", item.delivery_type);
    row += String.format("<td class='ignore'>{0}</td>", item.rest_push_endpoint_id || '');

    row += String.format("<td class='ignore'>{0}</td>", item.rest_push_endpoint_name || '');
    row += String.format("<td class='ignore'>{0}</td>", item.sec_base_id);

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

$.fn.zato.pubsub.subscription.edit = function(instance_id) {

    // Hide REST endpoint span immediately to prevent flicker during form population
    $('#rest-endpoint-edit').hide();

    $.fn.zato.data_table._create_edit('edit', 'Update the pub/sub subscription', instance_id);

    // Populate topics and security definitions after form opens with current selections
    setTimeout(function() {

        var instance = $.fn.zato.data_table.data[instance_id];

        // Set the sub_key in the hidden field
        $('#id_edit-sub_key').val(instance.sub_key);

        // Get the current topic names from the data table row data
        var currentTopicNames = null;

        if (instance && instance.topic_links) {
            // Extract topic names from HTML links
            currentTopicNames = instance.topic_links.split(',').map(function(name) {
                return name.trim();
            });
        } else {
        }

        // Get security ID from original form field before we remove it
        var currentSecId = instance.sec_base_id;
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
        // Instead of showing a dropdown for security definition, show it as a link and keep a hidden input
        if(instance.sec_name) {
            // Remove the security definition select to prevent duplicate form fields
            $('#id_edit-sec_base_id').remove();

            // Clear any existing content in the container
            $('#edit-sec-def-container').empty();

            // Create a hidden input with the security definition ID
            var hiddenInput = $('<input>', {
                type: 'hidden',
                name: 'edit-sec_base_id',
                value: currentSecId
            });

            // Create a link to the security definition
            var secDefLink = $('<a>', {
                href: '/zato/security/basic-auth/?cluster=1&query=' + encodeURIComponent(instance.sec_name),
                target: '_blank',
                text: instance.sec_name
            });

            // Add the hidden input and link to the container
            $('#edit-sec-def-container').append(hiddenInput).append(secDefLink);
        } else {
            // If no security definition, still remove the select
            $('#id_edit-sec_base_id').remove();
            $('#edit-sec-def-container').text('(None)');
        }

        // Immediately hide REST endpoint span if not push to prevent flicker
        var currentDeliveryType = $('#id_edit-delivery_type').val();
        console.log('DEBUG edit function: Check if should hide rest endpoint span', JSON.stringify({
            currentDeliveryType: currentDeliveryType,
            shouldHide: currentDeliveryType !== 'push',
            restEndpointEditExists: $('#rest-endpoint-edit').length > 0,
            isCurrentlyVisible: $('#rest-endpoint-edit').is(':visible')
        }));
        if (currentDeliveryType !== 'push') {
            $('#rest-endpoint-edit').hide();
            console.log('DEBUG edit function: REST endpoint span hidden');
        }

        // Setup delivery type visibility first, then conditionally populate REST endpoints
        $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('edit', instance_id);

        // Populate REST endpoints regardless of delivery type to avoid a flicker
        // when switching to push, but they'll remain hidden if not push type
        $.fn.zato.pubsub.subscription.populateRestEndpoints('edit', currentRestEndpointId, true);
        $.fn.zato.pubsub.subscription.populateServices('edit', currentServiceId, true);
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

    var cleanTopicName = $.fn.zato.pubsub.subscription.stripHtml(instance.topic_links);
    var descriptor = 'Security: ' + instance.sec_name + '\nTopic: ' + cleanTopicName + '\nDelivery: ' + instance.delivery_type;

    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Pub/sub subscription deleted:\n' + descriptor,
        'Are you sure you want to delete pub/sub subscription?\n\n' + descriptor,
        true);
}

$.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility = function(form_type, instance_id) {
    var deliveryTypeId = form_type === 'create' ? '#id_delivery_type' : '#id_edit-delivery_type';
    var pushTypeSpanId = form_type === 'create' ? '#push-type-create' : '#push-type-edit';
    var pushTypeId = form_type === 'create' ? '#id_push_type' : '#id_edit-push_type';
    var restEndpointSpanId = form_type === 'create' ? '#rest-endpoint-create' : '#rest-endpoint-edit';
    var serviceSpanId = form_type === 'create' ? '#push-service-create' : '#push-service-edit';

    var $deliveryType = $(deliveryTypeId);
    var $pushTypeSpan = $(pushTypeSpanId);
    var $pushType = $(pushTypeId);
    var $restEndpointSpan = $(restEndpointSpanId);
    var $serviceSpan = $(serviceSpanId);

    // Hide spans immediately to prevent any flash
    $pushTypeSpan.hide();
    $restEndpointSpan.hide();
    $serviceSpan.hide();

    if ($deliveryType.length === 0 || $pushTypeSpan.length === 0) {
        return;
    }

    function togglePushAndEndpointVisibility() {
        var deliveryTypeValue = $deliveryType.val();

        if (deliveryTypeValue === 'push') {
            $pushTypeSpan.show();
            toggleEndpointTypeVisibility();
        } else {
            $pushTypeSpan.hide();
            $restEndpointSpan.hide();
            $serviceSpan.hide();
        }
    }

    function toggleEndpointTypeVisibility() {
        var pushTypeValue = $pushType.val();

        // Preload both REST endpoints and services to avoid flicker when switching
        if (!window.endpointsLoaded) {
            var selectedId = form_type === 'edit' ? $.fn.zato.data_table.data[instance_id].rest_push_endpoint_id : null;
            $.fn.zato.pubsub.subscription.populateRestEndpoints(form_type, selectedId, false);
            window.endpointsLoaded = true;
        }

        if (!window.servicesLoaded) {
            var selectedServiceId = form_type === 'edit' ? $.fn.zato.data_table.data[instance_id].push_service_name : null;
            $.fn.zato.pubsub.subscription.populateServices(form_type, selectedServiceId, false);
            window.servicesLoaded = true;
        }

        // Now show/hide the appropriate spans based on the push type
        if (pushTypeValue === 'rest') {
            // Hide service span first to prevent layout shift
            $serviceSpan.hide();
            $restEndpointSpan.show();
        } else if (pushTypeValue === 'service') {
            // Hide REST span first to prevent layout shift
            $restEndpointSpan.hide();
            $serviceSpan.show();
        } else {
            $restEndpointSpan.hide();
            $serviceSpan.hide();
        }
    }

    // Set initial state
    togglePushAndEndpointVisibility();

    // Handle delivery type changes
    $deliveryType.on('change', togglePushAndEndpointVisibility);

    // Handle push type changes
    $pushType.on('change', toggleEndpointTypeVisibility);
}
