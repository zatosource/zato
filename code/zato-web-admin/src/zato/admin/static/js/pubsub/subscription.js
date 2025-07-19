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

$.fn.zato.pubsub.populate_sec_def_topics_callback = function(data, status) {
    if(data && typeof data === 'string') {
        $('#multi-select-div').html(data);
    }
    else if(data && data.responseText) {
        $('#multi-select-div').html(data.responseText);
    }
    else {
        $('#multi-select-div').html('<span style="font-style: italic; color: #666;">Error loading topics</span>');
    }
}

$.fn.zato.pubsub.on_sec_def_changed = function() {
    var sec_base_id = $('#id_sec_base_id').val();
    if(sec_base_id) {
        var cluster_id = $('#cluster_id').val();
        var url = String.format('/zato/pubsub/subscription/sec-def-topic-sub-list/{0}/cluster/{1}/', sec_base_id, cluster_id);
        $.fn.zato.post(url, $.fn.zato.pubsub.populate_sec_def_topics_callback, null, null, true);
    }
    else {
        $.fn.zato.pubsub.subscription.cleanup_hook($('#create-form'));
    }
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.cleanup_hook = function(form) {
    // Clear the multi-select div when no security definition is selected
    $('#multi-select-div').html('<em>Select a security definition to see available topics</em>');
}

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
        console.log('DEBUG close: Starting form close');

        // Clean up any spinners and reset visibility states
        $('.loading-spinner').remove();
        $('.security-select').removeClass('hide');
        $('#rest-endpoint-edit, #rest-endpoint-create').hide();
        $('#push-service-edit, #push-service-create').hide();
        $('#push-type-edit, #push-type-create').hide();

        console.log('DEBUG close: Calling original close function');
        // Call the original close function
        return originalClose(elem);
    };



    // Override the create_edit function to ensure proper cleanup before opening a new form
    var originalCreateEdit = $.fn.zato.data_table._create_edit;
    $.fn.zato.data_table._create_edit = function(form_type, title, id) {
        console.log('DEBUG _create_edit: Starting form open, type:', form_type, 'id:', id);

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

        console.log('DEBUG _create_edit: Calling original create_edit function');
        // Call the original create_edit function
        var result = originalCreateEdit.call(this, form_type, title, id);

        // After opening the form, set up handlers
        setTimeout(function() {
            console.log('DEBUG _create_edit: Setting up handlers after form open');
            // Set up delivery type visibility
            $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility(form_type, id);
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

    // Override the on_submit_complete function to add cleanup
    var originalOnSubmitComplete = $.fn.zato.data_table.on_submit_complete;
    $.fn.zato.data_table.on_submit_complete = function(data, status, action) {
        console.log('DEBUG on_submit_complete: Starting cleanup after form submission');

        // Call the original on_submit_complete function
        return originalOnSubmitComplete(data, status, action);
    };
})

// Function to populate REST endpoints
$.fn.zato.pubsub.subscription.populateRestEndpoints = function(form_type, selectedId, showSpan) {
    console.log('DEBUG populateRestEndpoints: Starting, form_type:', form_type, 'selectedId:', selectedId, 'showSpan:', showSpan);

    var endpointSelectId = form_type === 'create' ? '#id_rest_push_endpoint_id' : '#id_edit_rest_push_endpoint_id';
    var $endpointSelect = $(endpointSelectId);

    if (!$endpointSelect.length) {
        console.log('DEBUG populateRestEndpoints: Endpoint select not found:', endpointSelectId);
        return;
    }

    // Clear existing options
    $endpointSelect.empty();
    $endpointSelect.append('<option value="">Select an endpoint...</option>');

    // Show loading spinner
    var $container = $endpointSelect.parent();
    $container.find('.loading-spinner').remove();
    $container.append('<span class="loading-spinner show">Loading...</span>');

    // Make AJAX call to get REST endpoints
    $.ajax({
        url: '/zato/pubsub/subscription/get-rest-endpoints/',
        type: 'GET',
        data: {
            cluster_id: $('#cluster_id').val() || $('#id_edit-cluster_id').val()
        },
        success: function(response) {
            console.log('DEBUG populateRestEndpoints: AJAX success, response:', response);

            // Remove loading spinner
            $container.find('.loading-spinner').remove();

            if (response.endpoints && response.endpoints.length > 0) {
                console.log('DEBUG populateRestEndpoints: Populating', response.endpoints.length, 'endpoints');
                $.each(response.endpoints, function(index, endpoint) {
                    var option = $('<option></option>')
                        .attr('value', endpoint.id)
                        .text(endpoint.name);
                    if (selectedId && endpoint.id == selectedId) {
                        option.prop('selected', true);
                    }
                    $endpointSelect.append(option);
                });
            } else {
                console.log('DEBUG populateRestEndpoints: No endpoints found');
                $endpointSelect.append('<option value="">No endpoints available</option>');
            }

            // Refresh Chosen if it's initialized
            if ($endpointSelect.hasClass('chosen-select')) {
                $endpointSelect.trigger('chosen:updated');
            }

            // Show the span if requested
            if (showSpan) {
                var spanId = form_type === 'create' ? '#rest-endpoint-create' : '#rest-endpoint-edit';
                $(spanId).show();
            }
        },
        error: function(xhr, status, error) {
            console.log('DEBUG populateRestEndpoints: AJAX error:', status, error);
            // Remove loading spinner
            $container.find('.loading-spinner').remove();
            $endpointSelect.append('<option value="">Error loading endpoints</option>');
        }
    });
}

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

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.subscription.create = function() {
    // Hide REST endpoint span immediately before form opens
    $('#rest-endpoint-create').hide();

    $.fn.zato.data_table._create_edit('create', 'Create a pub/sub subscription', null);

    setTimeout(function() {
        // Setup delivery type visibility first, then populate REST endpoints for create form
        $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('create');
        $.fn.zato.pubsub.subscription.populateRestEndpoints('create', null);

        // Add event handler for security definition change
        $('#id_sec_base_id').change(function() {
            $.fn.zato.pubsub.on_sec_def_changed();
        });
    }, 200);
}

$.fn.zato.pubsub.subscription.edit = function(instance_id) {

    // Hide REST endpoint span immediately to prevent flicker during form population
    $('#rest-endpoint-edit').hide();

    $.fn.zato.data_table._create_edit('edit', 'Update the pub/sub subscription', instance_id);

    setTimeout(function() {

        var instance = $.fn.zato.data_table.data[instance_id];

        // Set the sub_key in the hidden field
        $('#id_edit-sub_key').val(instance.sub_key);

        var currentSecId = instance.sec_base_id;
        var currentRestEndpointId = instance.rest_push_endpoint_id || '';
        var currentServiceName = instance.push_service_name || '';

        // Add hidden input for security definition ID
        if (currentSecId && !$('#id_edit-sec_base_id').length) {
            $('#edit-form').append('<input type="hidden" id="id_edit-sec_base_id" name="edit-sec_base_id" value="' + currentSecId + '" />');
        }

        // Immediately hide REST endpoint span if not push to prevent flicker
        var currentDeliveryType = $('#id_edit-delivery_type').val();
        if (currentDeliveryType !== 'push') {
            $('#rest-endpoint-edit').hide();
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

        // Load topics for the current security definition in edit mode
        if(instance.sec_base_id) {
            var cluster_id = $('#cluster_id').val();
            var url = String.format('/zato/pubsub/subscription/sec-def-topic-sub-list/{0}/cluster/{1}/', instance.sec_base_id, cluster_id);
            $.fn.zato.post(url, $.fn.zato.pubsub.populate_sec_def_topics_callback, null, null, true);
        }
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

    var descriptor = 'Security: ' + instance.sec_name + '\nDelivery: ' + instance.delivery_type;

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
