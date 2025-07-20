// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.pubsub.subscription');

// Constants
var Multi_Select_Empty_Message = '<table id="multi-select-table" class="multi-select-table"><tr><td colspan="2"><span class="multi-select-message">Select a security definition to see available topics</span></td></tr></table>';

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

$.fn.zato.pubsub.populate_sec_def_topics_callback = function(data, status, instance_id) {
    console.log('DEBUG populate_sec_def_topics_callback: status="' + status + '", data type="' + typeof data + '"');

    // Handle different response formats
    var htmlContent;
    if (typeof data === 'string') {
        htmlContent = data;
        console.log('DEBUG populate_sec_def_topics_callback: received string data, length=' + data.length);
    } else if (data && data.responseText) {
        htmlContent = data.responseText;
        console.log('DEBUG populate_sec_def_topics_callback: received responseText HTML data, length=' + data.responseText.length);
    } else {
        console.log('DEBUG populate_sec_def_topics_callback: unexpected data format, data=' + JSON.stringify(data));
        return;
    }

    // Determine which form is active
    var isEditMode = $('#edit-div').dialog('isOpen');
    var targetDivId = isEditMode ? '#id_edit-multi-select-div' : '#multi-select-div';
    console.log('DEBUG populate_sec_def_topics_callback: isEditMode=' + isEditMode + ', targeting=' + targetDivId);

    console.log('DEBUG populate_sec_def_topics_callback: setting HTML content in ' + targetDivId);
    console.log('DEBUG populate_sec_def_topics_callback: HTML content being loaded=' + htmlContent);

    // Check current content before setting
    var beforeContent = $(targetDivId).html();
    console.log('DEBUG populate_sec_def_topics_callback: current content before setting=' + beforeContent);

    // Set the HTML content
    $(targetDivId).html(htmlContent);

    // Verify content was set
    var afterContent = $(targetDivId).html();
    console.log('DEBUG populate_sec_def_topics_callback: content after setting=' + afterContent);
    console.log('DEBUG populate_sec_def_topics_callback: content was changed=' + JSON.stringify(beforeContent !== afterContent));

    // Count checkboxes
    var checkboxCount = $(targetDivId + ' input[name="topic_name"]').length;
    console.log('DEBUG populate_sec_def_topics_callback: created ' + checkboxCount + ' topic checkboxes');

    // Check if we're in edit mode and need to select existing topics
    var editForm = $('#edit-form');
    var isEditMode = editForm.is(':visible');
    console.log('DEBUG populate_sec_def_topics_callback: edit form visible=' + JSON.stringify(isEditMode));

    if (isEditMode) {
        console.log('DEBUG populate_sec_def_topics_callback: in edit mode, checking for existing topics to select');

        // Get the current instance data to find subscribed topics
        console.log('DEBUG populate_sec_def_topics_callback: looking for instanceId=' + JSON.stringify(instance_id));

        if (instance_id && $.fn.zato.data_table.data[instance_id]) {
            var instance = $.fn.zato.data_table.data[instance_id];
            console.log('DEBUG populate_sec_def_topics_callback: found instance data for edit, topic_names=' + JSON.stringify(instance.topic_names));

            if (instance.topic_names) {
                var topicNames = [];
                try {
                    topicNames = JSON.parse(instance.topic_names);
                    console.log('DEBUG populate_sec_def_topics_callback: parsed topic names=' + JSON.stringify(topicNames) + ', count=' + topicNames.length);
                } catch (e) {
                    console.log('DEBUG populate_sec_def_topics_callback: failed to parse topic_names as JSON, error=' + JSON.stringify(e.message) + ', treating as string');
                    topicNames = [instance.topic_names];
                }

                console.log('DEBUG populate_sec_def_topics_callback: attempting to check ' + topicNames.length + ' topics');
                // Check the checkboxes for subscribed topics
                topicNames.forEach(function(topicName, index) {
                    console.log('DEBUG populate_sec_def_topics_callback: processing topic ' + (index + 1) + '/' + topicNames.length + ', name=' + JSON.stringify(topicName));
                    var checkbox = $('input[name="topic_name"][value="' + topicName + '"]');
                    console.log('DEBUG populate_sec_def_topics_callback: found checkbox for topic=' + JSON.stringify(topicName) + ', exists=' + JSON.stringify(checkbox.length > 0));

                    if (checkbox.length) {
                        checkbox.prop('checked', true);
                        console.log('DEBUG populate_sec_def_topics_callback: checked topic=' + JSON.stringify(topicName));
                    } else {
                        console.log('DEBUG populate_sec_def_topics_callback: topic checkbox not found for=' + JSON.stringify(topicName));
                    }
                });

                // Log final state of checkboxes
                var checkedCount = $('#multi-select-div input[name="topic_name"]:checked').length;
                console.log('DEBUG populate_sec_def_topics_callback: final state - ' + checkedCount + ' out of ' + checkboxCount + ' checkboxes are checked');
            } else {
                console.log('DEBUG populate_sec_def_topics_callback: instance has no topic_names data');
            }
        } else {
            console.log('DEBUG populate_sec_def_topics_callback: no instance data found for instanceId=' + JSON.stringify(instance_id));
        }
    } else {
        console.log('DEBUG populate_sec_def_topics_callback: not in edit mode, no topics to pre-select');
    }

    // Add mutation observer to detect changes to multi-select-div
    var targetNode = document.getElementById('multi-select-div');
    if (targetNode && !targetNode._observer) {
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    console.log('DEBUG MutationObserver: multi-select-div content changed');
                    console.log('DEBUG MutationObserver: new content=' + targetNode.innerHTML.substring(0, 200));
                    console.log('DEBUG MutationObserver: stack trace:', new Error().stack);
                }
            });
        });
        observer.observe(targetNode, { childList: true, subtree: true });
        targetNode._observer = observer;
        console.log('DEBUG populate_sec_def_topics_callback: mutation observer attached');
    }

    // Comprehensive diagnostic logging
    console.log('DEBUG populate_sec_def_topics_callback: === DIAGNOSTIC CHECKS ===');
    console.log('DEBUG populate_sec_def_topics_callback: dialog visible=' + $('#edit-div').is(':visible'));
    console.log('DEBUG populate_sec_def_topics_callback: dialog open=' + $('#edit-div').dialog('isOpen'));
    console.log('DEBUG populate_sec_def_topics_callback: multi-select-div visible=' + $(targetDivId).is(':visible'));
    console.log('DEBUG populate_sec_def_topics_callback: multi-select-div display=' + $(targetDivId).css('display'));
    console.log('DEBUG populate_sec_def_topics_callback: multi-select-div width=' + $(targetDivId).width());
    console.log('DEBUG populate_sec_def_topics_callback: multi-select-div height=' + $(targetDivId).height());
    var tableSelector = isEditMode ? '#id_edit-multi-select-table' : '#multi-select-table';
    console.log('DEBUG populate_sec_def_topics_callback: multi-select-table visible=' + $(tableSelector).is(':visible'));
    console.log('DEBUG populate_sec_def_topics_callback: multi-select-table display=' + $(tableSelector).css('display'));
    var tdSelector = isEditMode ? '#id_edit-td_topic_list' : '#td_topic_list';
    console.log('DEBUG populate_sec_def_topics_callback: td_topic_list visible=' + $(tdSelector).is(':visible'));
    console.log('DEBUG populate_sec_def_topics_callback: topic_checkbox_1 exists=' + $('#topic_checkbox_1').length);
    console.log('DEBUG populate_sec_def_topics_callback: topic_checkbox_2 exists=' + $('#topic_checkbox_2').length);
    console.log('DEBUG populate_sec_def_topics_callback: topic_checkbox_3 exists=' + $('#topic_checkbox_3').length);
    console.log('DEBUG populate_sec_def_topics_callback: topic_checkbox_1 checked=' + $('#topic_checkbox_1').prop('checked'));
    console.log('DEBUG populate_sec_def_topics_callback: topic_checkbox_2 checked=' + $('#topic_checkbox_2').prop('checked'));
    console.log('DEBUG populate_sec_def_topics_callback: topic_checkbox_3 checked=' + $('#topic_checkbox_3').prop('checked'));

    // Check parent visibility chain
    console.log('DEBUG populate_sec_def_topics_callback: === PARENT VISIBILITY CHAIN ===');
    console.log('DEBUG populate_sec_def_topics_callback: edit-div visible=' + $('#edit-div').is(':visible'));
    console.log('DEBUG populate_sec_def_topics_callback: edit form visible=' + $('#edit-form').is(':visible'));
    console.log('DEBUG populate_sec_def_topics_callback: edit table visible=' + $('#edit-div table').first().is(':visible'));
    console.log('DEBUG populate_sec_def_topics_callback: td_topic_list parent tr visible=' + $('#id_edit-td_topic_list').parent('tr').is(':visible'));

    // Check CSS properties of td_topic_list
    console.log('DEBUG populate_sec_def_topics_callback: === TD_TOPIC_LIST CSS ===');
    console.log('DEBUG populate_sec_def_topics_callback: td_topic_list visibility=' + $('#id_edit-td_topic_list').css('visibility'));
    console.log('DEBUG populate_sec_def_topics_callback: td_topic_list opacity=' + $('#id_edit-td_topic_list').css('opacity'));
    console.log('DEBUG populate_sec_def_topics_callback: td_topic_list position=' + $('#id_edit-td_topic_list').css('position'));
    console.log('DEBUG populate_sec_def_topics_callback: td_topic_list left=' + $('#id_edit-td_topic_list').css('left'));
    console.log('DEBUG populate_sec_def_topics_callback: td_topic_list top=' + $('#id_edit-td_topic_list').css('top'));
    console.log('DEBUG populate_sec_def_topics_callback: td_topic_list overflow=' + $('#id_edit-td_topic_list').css('overflow'));

    // Check other form elements visibility for comparison
    console.log('DEBUG populate_sec_def_topics_callback: === OTHER FORM ELEMENTS ===');
    console.log('DEBUG populate_sec_def_topics_callback: delivery_type field visible=' + $('#id_edit-delivery_type').is(':visible'));
    console.log('DEBUG populate_sec_def_topics_callback: sec_def container visible=' + $('#id_edit_sec_def_container').is(':visible'));

    // Force browser repaint and check again
    $(targetDivId).hide().show();
    console.log('DEBUG populate_sec_def_topics_callback: after repaint - multi-select-div visible=' + $(targetDivId).is(':visible'));
    console.log('DEBUG populate_sec_def_topics_callback: after repaint - td_topic_list visible=' + $(tdSelector).is(':visible'));

    console.log('DEBUG populate_sec_def_topics_callback: callback complete, final DOM content=' + $(targetDivId).html().substring(0, 200));
}

$.fn.zato.pubsub.on_sec_def_changed = function() {
    var sec_base_id = $('#id_sec_base_id').val();
    console.log('DEBUG on_sec_def_changed: sec_base_id=' + JSON.stringify(sec_base_id));
    if(sec_base_id) {
        var cluster_id = $('#cluster_id').val();
        var url = String.format('/zato/pubsub/subscription/sec-def-topic-sub-list/{0}/cluster/{1}/', sec_base_id, cluster_id);
        console.log('DEBUG on_sec_def_changed: posting to url=' + JSON.stringify(url));
        $.fn.zato.post(url, function(data, status) {
            $.fn.zato.pubsub.populate_sec_def_topics_callback(data, status, null);
        }, null, null, true);
    }
    else {
        console.log('DEBUG on_sec_def_changed: no sec_base_id, calling cleanup_hook');
        $.fn.zato.pubsub.subscription.cleanup_hook($('#create-form'));
    }
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.cleanup_hook = function(form) {
    // Clear the multi-select div when no security definition is selected
    $('#multi-select-div').html(Multi_Select_Empty_Message);
}

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubSubscription;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.subscription.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([]);

    // Add open callbacks to both create and edit dialogs for proper initialization
    $('#create-div').dialog('option', 'open', function() {
        // Clean up any previous state
        $('.loading-spinner').remove();
        $('#rest-endpoint-create, #push-service-create, #push-type-create').hide();

        // Reset delivery type to pull (default)
        $('#id_delivery_type').val('pull');

        // Setup delivery type visibility and populate REST endpoints
        $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('create', null);
        $.fn.zato.pubsub.subscription.populateRestEndpoints('create', null);

        // Add event handler for security definition change
        $('#id_sec_base_id').change(function() {
            $.fn.zato.pubsub.on_sec_def_changed();
        });
    });

    $('#edit-div').dialog('option', 'open', function() {
        var instance_id = $.fn.zato.pubsub.subscription._current_edit_instance_id;
        if (instance_id) {
            var instance = $.fn.zato.data_table.data[instance_id];

            // Clean up any previous state
            $('.loading-spinner').remove();
            $('#rest-endpoint-edit, #push-service-edit, #push-type-edit').hide();

            // Use requestAnimationFrame to ensure dialog is painted before making changes
            requestAnimationFrame(function() {
                console.log('DEBUG requestAnimationFrame: starting edit dialog initialization for instance_id=' + instance_id);

                // Immediately hide REST endpoint span if not push to prevent flicker
                var currentDeliveryType = $('#id_edit-delivery_type').val();
                console.log('DEBUG requestAnimationFrame: currentDeliveryType=' + currentDeliveryType);
                if (currentDeliveryType !== 'push') {
                    $('#rest-endpoint-edit').hide();
                }

                // Set the correct push_type value from instance data
                if(instance.push_type) {
                    console.log('DEBUG requestAnimationFrame: setting push_type=' + instance.push_type);
                    $('#id_edit-push_type').val(instance.push_type);

                    // If push type is service, set the service name in the dropdown
                    if(instance.push_type === 'service' && instance.push_service_name) {
                        $('#id_edit-push_service_name').val(instance.push_service_name);
                        $('#id_edit_push_service_name_chosen span').text(instance.push_service_name);
                    }
                }

                // Setup delivery type visibility first, then conditionally populate REST endpoints
                console.log('DEBUG requestAnimationFrame: calling setupDeliveryTypeVisibility');
                $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('edit', instance_id);

                // Populate REST endpoints regardless of delivery type to avoid a flicker
                // when switching to push, but they'll remain hidden if not push type
                var currentRestEndpointId = instance.rest_push_endpoint_id || '';
                var currentServiceName = instance.push_service_name || '';
                console.log('DEBUG requestAnimationFrame: calling populateRestEndpoints and populateServices');
                $.fn.zato.pubsub.subscription.populateRestEndpoints('edit', currentRestEndpointId, true);
                $.fn.zato.pubsub.subscription.populateServices('edit', currentServiceName, true);

                // Load topics for the current security definition in edit mode
                if(instance.sec_base_id) {
                    console.log('DEBUG requestAnimationFrame: loading topics for sec_base_id=' + instance.sec_base_id);
                    var cluster_id = $('#cluster_id').val();
                    var url = String.format('/zato/pubsub/subscription/sec-def-topic-sub-list/{0}/cluster/{1}/', instance.sec_base_id, cluster_id);
                    $.fn.zato.post(url, function(data, status) {
                        console.log('DEBUG requestAnimationFrame: topics loaded, calling populate_sec_def_topics_callback');
                        $.fn.zato.pubsub.populate_sec_def_topics_callback(data, status, instance_id);
                    }, null, null, true);
                } else {
                    console.log('DEBUG requestAnimationFrame: no sec_base_id found, skipping topic loading');
                }

                console.log('DEBUG requestAnimationFrame: edit dialog initialization complete');
            });
        }
    });

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

        // Clear the multi-select div
        console.log('DEBUG close: Clearing multi-select div');
        $('#multi-select-div').html(Multi_Select_Empty_Message);

        console.log('DEBUG close: Calling original close function');
        // Call the original close function
        return originalClose(elem);
    };

    // Override the on_submit function to add validation
    var originalOnSubmit = $.fn.zato.data_table.on_submit;
    $.fn.zato.data_table.on_submit = function(action) {
        console.log('DEBUG on_submit: Starting form submission, action=' + JSON.stringify(action));

        // Validate push delivery type
        var deliveryTypeId = action === 'create' ? '#id_delivery_type' : '#id_edit-delivery_type';
        var pushTypeId = action === 'create' ? '#id_push_type' : '#id_edit-push_type';
        var restEndpointId = action === 'create' ? '#id_rest_push_endpoint_id' : '#id_edit-rest_push_endpoint_id';
        var serviceId = action === 'create' ? '#id_push_service_name' : '#id_edit-push_service_name';

        var deliveryType = $(deliveryTypeId).val();
        var pushType = $(pushTypeId).val();
        var restEndpoint = $(restEndpointId).val();
        var service = $(serviceId).val();

        console.log('DEBUG on_submit: deliveryType=' + JSON.stringify(deliveryType) + ', pushType=' + JSON.stringify(pushType));

        if (deliveryType === 'push' && !pushType) {
            console.log('DEBUG on_submit: validation failed - push type required');
            $.fn.zato.user_message(true, 'Push type is required when delivery type is push');
            return false;
        }

        // Call original on_submit if validation passes
        console.log('DEBUG on_submit: calling original on_submit');
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

    row += String.format('<td>{0}</td>', item.topic_link_list);
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
    console.log('DEBUG create: opening create form');

    // Clear the multi-select div before opening create form
    console.log('DEBUG create: Clearing multi-select div');
    $('#multi-select-div').html(Multi_Select_Empty_Message);

    $.fn.zato.data_table._create_edit('create', 'Create a new pub/sub subscription', null);
}

$.fn.zato.pubsub.subscription.edit = function(instance_id) {
    console.log('DEBUG edit: opening edit form for instance_id=' + JSON.stringify(instance_id));

    var instance = $.fn.zato.data_table.data[instance_id];
    console.log('DEBUG edit: instance data=' + JSON.stringify(instance));
    var form = $('#edit-form');

    form.find('#id_edit-sub_key').val(instance.sub_key);
    form.find('#id_edit-is_active').prop('checked', $.fn.zato.like_bool(instance.is_active) == true);
    form.find('#id_edit-delivery_type').val(instance.delivery_type);
    form.find('#id_edit-push_type').val(instance.push_type);
    form.find('#id_edit-rest_push_endpoint_id').val(instance.rest_push_endpoint_id);
    form.find('#id_edit-push_service_name').val(instance.push_service_name);

    // Handle security definition display as link instead of select
    var $container = $('#edit-sec-def-container');
    console.log('DEBUG edit: security definition container found=' + JSON.stringify($container.length > 0));
    if ($container.length) {
        // Hide the select element
        $('#id_edit-sec_base_id').hide();
        console.log('DEBUG edit: hidden security definition select');

        // Clear all existing content from the container
        $container.empty();
        console.log('DEBUG edit: cleared security definition container');

        // Add hidden input for the security definition ID
        $container.append('<input type="hidden" id="id_edit-sec_base_id" name="edit-sec_base_id" value="' + instance.sec_base_id + '"/>');
        console.log('DEBUG edit: added hidden input for sec_base_id=' + JSON.stringify(instance.sec_base_id));

        // Display the security definition name as a link
        var secName = instance.sec_name || 'Security definition ID: ' + instance.sec_base_id;
        var clusterID = $('#cluster_id').val() || '1';
        var secLink = '<a href="/zato/security/basic-auth/?cluster=' + clusterID + '&query=' + encodeURIComponent(secName) + '" target="_blank">' + secName + '</a>';
        $container.append(secLink);
        console.log('DEBUG edit: displaying security definition as link, secName=' + JSON.stringify(secName) + ', link=' + JSON.stringify(secLink));
    } else {
        // Fallback to original behavior if container doesn't exist
        console.log('DEBUG edit: security definition container not found, using fallback select behavior');
        form.find('#id_edit-sec_base_id').val(instance.sec_base_id);
        console.log('DEBUG edit: set security definition select value to=' + JSON.stringify(instance.sec_base_id));
    }

    // Hide REST endpoint span immediately to prevent flicker during form population
    $('#rest-endpoint-edit').hide();

    // Store the instance_id for the dialog open callback
    $.fn.zato.pubsub.subscription._current_edit_instance_id = instance_id;

    $.fn.zato.data_table._create_edit('edit', 'Update the pub/sub subscription', instance_id);
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
        console.log('DEBUG togglePushAndEndpointVisibility: deliveryTypeValue=' + JSON.stringify(deliveryTypeValue));

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
        console.log('DEBUG toggleEndpointTypeVisibility: pushTypeValue=' + JSON.stringify(pushTypeValue));

        // Preload both REST endpoints and services to avoid flicker when switching
        if (!window.endpointsLoaded) {
            var selectedId = form_type === 'edit' ? $.fn.zato.data_table.data[instance_id].rest_push_endpoint_id : null;
            console.log('DEBUG toggleEndpointTypeVisibility: loading REST endpoints for selectedId=' + JSON.stringify(selectedId));
            $.fn.zato.pubsub.subscription.populateRestEndpoints(form_type, selectedId, false);
            window.endpointsLoaded = true;
        }

        if (!window.servicesLoaded) {
            var selectedServiceId = form_type === 'edit' ? $.fn.zato.data_table.data[instance_id].push_service_name : null;
            console.log('DEBUG toggleEndpointTypeVisibility: loading services for selectedServiceId=' + JSON.stringify(selectedServiceId));
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
