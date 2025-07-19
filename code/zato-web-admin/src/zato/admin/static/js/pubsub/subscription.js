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

        // Ensure REST endpoint, service and push type spans are hidden before opening any form
        $('#rest-endpoint-create, #rest-endpoint-edit').hide();
        $('#push-service-create, #push-service-edit').hide();
        $('#push-type-create, #push-type-edit').hide();

        // Reset delivery type to pull (default)
        if (form_type === 'create') {
            $('#id_delivery_type').val('pull');
        }

        // Call the original create_edit function
        var result = originalCreateEdit(form_type, title, id);

        // Initialize Chosen for topic select elements immediately
        var topicSelectId = form_type === 'create' ? '#id_topic_id' : '#id_edit-topic_id';
        var $topicSelect = $(topicSelectId);

        if ($topicSelect.length > 0) {
            $topicSelect.chosen({
                placeholder_text_multiple: 'Select topics...',
                search_contains: true,
                width: '100%',
                hide_results_on_select: false
            });
        }

        // Initialize security definition change handler and set initial state
        setTimeout(function() {
            $.fn.zato.pubsub.subscription.setupSecurityDefinitionChangeHandler(form_type);

            // Set initial state for topic dropdown (only for create form)
            if (form_type === 'create') {
                $topicSelect.parent().find('.no-topics-message').remove();
            }
        }, 100);

        return result;
    };

    // Override the on_submit function to add validation
    var originalOnSubmit = $.fn.zato.data_table.on_submit;
    $.fn.zato.data_table.on_submit = function(action) {
        // Validate push delivery type
        var deliveryTypeId = action === 'create' ? '#id_delivery_type' : '#id_edit-delivery_type';
        var pushTypeId = action === 'create' ? '#id_push_type' : '#id_edit-push_type';
        var restEndpointId = action === 'create' ? '#id_rest_push_endpoint_id' : '#id_edit-rest_push_endpoint_id';
        var serviceId = action === 'create' ? '#id_push_service_name' : '#id_edit-push_service_name';

        var deliveryType = $(deliveryTypeId).val();
        var pushType = $(pushTypeId).val();
        var restEndpoint = $(restEndpointId).val();
        var service = $(serviceId).val();

        if (deliveryType === 'push') {
            if (pushType === 'rest' && (!restEndpoint || restEndpoint === '')) {
                alert('Please select a push REST endpoint.');
                return false;
            } else if (pushType === 'service' && (!service || service === '')) {
                alert('Please select a push service.');
                return false;
            }
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

            // Completely destroy any existing Chosen instance
            if ($select.next('.chosen-container').length > 0) {
                $select.chosen('destroy');
            }

            // Remove the selected attribute from all options
            $select.find('option').prop('selected', false);

            // Set selected attribute directly on the HTML option element
            if (selectedId) {
                $select.find('option[value="' + selectedId + '"]').prop('selected', true);
            } else {
                // If no specific ID, select the first option (the default one)
                $select.find('option:first').prop('selected', true);
            }

            // Initialize Chosen on the properly prepared select element
            $select.chosen({width: '98%'});

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
                    console.log('DEBUG Service Selection: MATCH! service.service_name=', JSON.stringify(service.service_name), 'selectedId=', JSON.stringify(selectedId));
                } else if (selectedId) {
                    console.log('DEBUG Service Selection: NO MATCH! service.service_name=', JSON.stringify(service.service_name), 'selectedId=', JSON.stringify(selectedId));
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

    // For Push delivery type, display information based on push_type
    if(item.delivery_type === 'pull') {
        row += String.format('<td>{0}</td>', 'Pull');
    } else {
        // Push delivery type - check push_type to determine what to show
        if(item.push_type === 'rest' && item.rest_push_endpoint_id) {
            var endpointName = item.rest_push_endpoint_name || '';
            if(!endpointName) {
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
            }

            // Add the endpoint link to the row
            row += String.format('<td>Push <a href="/zato/http-soap/?cluster=1&query={0}&connection=outgoing&transport=plain_http">{1}</a></td>',
                encodeURIComponent(endpointName), endpointName);
        } else if(item.push_type === 'service' && item.push_service_name) {
            // For service push type, show the service name
            row += String.format('<td>Push <a href="/zato/service/?cluster=1&query={0}">{1}</a></td>',
                encodeURIComponent(item.push_service_name), item.push_service_name);
        } else {
            // Generic push with no details
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

    row += String.format("<td class='ignore'>{0}</td>", item.sec_base_id);
    row += String.format("<td class='ignore'>{0}</td>", item.push_type);
    row += String.format("<td class='ignore'>{0}</td>", item.rest_push_endpoint_id);

    row += String.format("<td class='ignore'>{0}</td>", item.rest_push_endpoint_name);
    row += String.format("<td class='ignore'>{0}</td>", item.push_service_name);
    row += String.format("<td class='ignore'>{0}</td>", item.topic_names);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.subscription.create = function() {
    // Hide REST endpoint span immediately before form opens
    $('#rest-endpoint-create').hide();

    $.fn.zato.data_table._create_edit('create', 'Create a pub/sub subscription', null);
    // Populate security definitions after form opens
    setTimeout(function() {
        // Clear topic dropdown immediately to prevent showing previous topics
        $('#id_topic_id').empty();

        // Prepare topic select for SlimSelect but don't populate yet
        $('#id_topic_id').attr('multiple', true);

        $.fn.zato.common.security.populateSecurityDefinitions('create', null, '/zato/pubsub/subscription/get-security-definitions/', '#id_sec_base_id');

        // Add security definition change handler for topic filtering
        $.fn.zato.pubsub.subscription.setupSecurityDefinitionChangeHandler('create');

        // Setup delivery type visibility first, then populate REST endpoints for create form
        $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('create');
        $.fn.zato.pubsub.subscription.populateRestEndpoints('create', null);

        // Trigger initial topic load after security definitions are populated
        setTimeout(function() {
            var $securitySelect = $('#id_sec_base_id');
            if ($securitySelect.val()) {
                $securitySelect.trigger('change.security-filter');
            }
        }, 100);
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

        var currentTopicNames = JSON.parse(instance.topic_names);

        console.log('[DEBUG] edit: Got topic_names:', JSON.stringify(currentTopicNames));

        // Get security ID from original form field before we remove it
        var currentSecId = instance.sec_base_id;
        var currentRestEndpointId = instance.rest_push_endpoint_id || '';
        var currentServiceName = instance.push_service_name || '';
        console.log('DEBUG Service Selection: instance.push_service_name=', JSON.stringify(instance.push_service_name));

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

        // Set the correct push_type value from instance data
        if(instance.push_type) {
            $('#id_edit-push_type').val(instance.push_type);

            // If push type is service, set the service name in the dropdown
            if(instance.push_type === 'service' && instance.push_service_name) {
                $('#id_edit-push_service_name').val(instance.push_service_name);
                $('#id_edit_push_service_name_chosen span').text(instance.push_service_name);
            }
        }

        // Setup delivery type visibility first, then conditionally populate REST endpoints
        $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('edit', instance_id);

        // Populate REST endpoints regardless of delivery type to avoid a flicker
        // when switching to push, but they'll remain hidden if not push type
        $.fn.zato.pubsub.subscription.populateRestEndpoints('edit', currentRestEndpointId, true);
        $.fn.zato.pubsub.subscription.populateServices('edit', currentServiceName, true);
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

$.fn.zato.pubsub.subscription.setupSecurityDefinitionChangeHandler = function(form_type) {
    var securitySelectId = form_type === 'create' ? '#id_sec_base_id' : '#id_edit-sec_base_id';
    var $securitySelect = $(securitySelectId);

    if ($securitySelect.length === 0) {
        // For edit form, security definition is shown as a link, not a select
        // The topic filtering is not needed since security definition cannot be changed
        return;
    }

    // Remove any existing change handlers to prevent duplicates
    $securitySelect.off('change.security-filter');

    // Add change handler for security definition dropdown
    $securitySelect.on('change.security-filter', function() {
        var secBaseId = $(this).val();
        var clusterId = $('#cluster_id').val();

        if (!secBaseId || !clusterId) {
            // Clear topics if no security definition selected
            var topicSelectId = form_type === 'create' ? '#id_topic_id' : '#id_edit-topic_id';
            var $topicSelect = $(topicSelectId);
            $topicSelect.empty();
            $topicSelect.trigger('chosen:updated');
            $topicSelect.parent().find('.no-topics-message').remove();
            return;
        }

        // Use the existing populateTopics function with the security-filtered endpoint
        var topicSelectId = form_type === 'create' ? '#id_topic_id' : '#id_edit-topic_id';
        // Make direct AJAX call to get filtered topics
        $.ajax({
            url: '/zato/pubsub/subscription/get-topics-by-security/',
            type: 'GET',
            data: {
                cluster_id: clusterId,
                sec_base_id: secBaseId
            },
            success: function(response) {
                var $topicSelect = $(topicSelectId);
                var $container = $topicSelect.parent();

                // Clear any existing messages
                $container.find('.no-topics-message').remove();

                if (response.topics && response.topics.length > 0) {
                    // Clear existing options and populate with filtered topics
                    $topicSelect.empty();

                    $.each(response.topics, function(index, topic) {
                        var option = $('<option></option>')
                            .attr('value', topic.id)
                            .text(topic.name);
                        $topicSelect.append(option);
                    });

                    // For create form, clear any default selections
                    if (form_type === 'create') {
                        $topicSelect.find('option').prop('selected', false);
                    }

                    // Show the Chosen select
                    $topicSelect.next('.chosen-container').show();

                    // Refresh Chosen after populating options
                    $topicSelect.trigger('chosen:updated');
                } else {
                    // No matching topics - clear select and hide it
                    $topicSelect.empty();

                    // Hide the Chosen select
                    $topicSelect.next('.chosen-container').hide();

                    // Refresh Chosen after clearing options
                    $topicSelect.trigger('chosen:updated');

                    $container.append('<span class="no-topics-message" style="font-style: italic; color: #666;">No matching topics - <a href="/zato/pubsub/permission/?cluster=1" target="_blank">Click to manage permissions</a></span>');
                }
            },
            error: function(xhr, status, error) {
                var $topicSelect = $(topicSelectId);
                var $container = $topicSelect.parent();

                // Clear any existing messages
                $container.find('.no-topics-message').remove();

                $topicSelect.empty();

                // Refresh Chosen after clearing options
                $topicSelect.trigger('chosen:updated');

                $container.append('<span class="no-topics-message" style="font-style: italic; color: #666;">Error loading topics</span>');
            }
        });
    });

    // Trigger initial load if security definition is already selected
    var initialSecBaseId = $securitySelect.val();
    if (initialSecBaseId) {
        $securitySelect.trigger('change.security-filter');
    }
}
