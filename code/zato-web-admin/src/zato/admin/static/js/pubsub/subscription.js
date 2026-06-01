(function($) {

// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.pubsub.subscription');

// Tri-state checkbox functionality
function setupTriStateCheckbox(checkbox) {
    var Off = 0;
    var On = 1;
    var Indeterminate = 2;

    var $checkbox = $(checkbox);

    if (!$checkbox.data('tri-state-initialized')) {
        var initialState;

        if ($checkbox.hasClass('indeterminate')) {
            initialState = Indeterminate;
        } else if ($checkbox.prop('checked')) {
            initialState = On;
        } else {
            initialState = Off;
        }

        $checkbox.data('tri-state', initialState);
        $checkbox.data('tri-state-initialized', true);

        $checkbox.off('click.tristate mousedown.tristate');

        $checkbox.on('mousedown.tristate', function(e) {
            e.preventDefault();
            e.stopPropagation();

            var currentState = $checkbox.data('tri-state');
            var actualChecked = $checkbox.prop('checked');
            var actualIndeterminate = $checkbox.hasClass('indeterminate');

            var actualState = currentState;
            if (actualIndeterminate) {
                actualState = Indeterminate;
            } else if (actualChecked) {
                actualState = On;
            } else {
                actualState = Off;
            }

            if (actualState !== currentState) {
                $checkbox.data('tri-state', actualState);
                currentState = actualState;
            }

            var newState = (currentState + 1) % 3;

            $checkbox.data('tri-state', newState);

            $checkbox.removeClass('indeterminate');

            switch(newState) {
                case Off:
                    $checkbox.prop('checked', false);
                    break;
                case On:
                    $checkbox.prop('checked', true);
                    break;
                case Indeterminate:
                    $checkbox.prop('checked', false);
                    $checkbox.addClass('indeterminate');
                    break;
            }

            return false;
        });

        $checkbox.on('click.tristate', function(e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        });
    }
}

// Constants
var Multi_Select_Empty_Message = '<table id="multi-select-table" class="multi-select-table"><tr><td colspan="2"><span class="multi-select-message">Select a security definition to see available topics</span></td></tr></table>';

$.fn.zato.data_table.PubSubSubscription = new Class({
    toString: function() {
        var template = '<PubSubSubscription id:{0} topic_link_list:{1} security:{2} pattern_matched:{3}>';
        return String.format(template, this.id, this.topic_link_list, this.security, this.pattern_matched);
    }
});

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.populate_sec_def_topics_callback = function(data, status, instance_id) {

    // Handle different response formats
    var htmlContent;
    if (typeof data === 'string') {
        htmlContent = data;
    } else if (data && data.responseText) {
        htmlContent = data.responseText;
    } else {
        var dataJson = JSON.stringify(data);
        return;
    }

    // Determine which form is active
    var isEditMode = $('#edit-div').dialog('isOpen');
    var targetDivId = isEditMode ? '#id_edit-multi-select-div' : '#multi-select-div';


    // Check current content before setting
    var beforeContent = $(targetDivId).html();

    // Set the HTML content
    $(targetDivId).html(htmlContent);

    // Convert all topic checkboxes to tri-state
    $(targetDivId + ' input[name="topic_name"]').addClass('tri-state').each(function() {
        setupTriStateCheckbox(this);
    });

    // Verify content was set
    var afterContent = $(targetDivId).html();

    // Count checkboxes
    var checkboxCount = $(targetDivId + ' input[name="topic_name"]').length;

    // Check if we're in edit mode and need to select existing topics
    var editForm = $('#edit-form');
    var isEditMode = editForm.is(':visible');

    if (isEditMode) {

        // Get the current instance data to find subscribed topics

        if (instance_id && $.fn.zato.data_table.data[instance_id]) {
            var instance = $.fn.zato.data_table.data[instance_id];

            if (instance.topic_name_list) {
                var topicNames = [];
                try {
                    topicNames = JSON.parse(instance.topic_name_list);
                } catch (e) {
                    topicNames = [instance.topic_name_list];
                }

                // Check the checkboxes for subscribed topics
                topicNames.forEach(function(topic, index) {
                    var checkbox = $(targetDivId + ' input[name="topic_name"][value="' + topic.topic_name + '"]');

                    if (checkbox.length) {
                        // Set tri-state based on pub/delivery flags
                        checkbox.addClass('tri-state');

                        if (topic.is_pub_enabled && topic.is_delivery_enabled) {
                            checkbox.prop('checked', true);
                            checkbox.removeClass('indeterminate');
                        } else if (!topic.is_pub_enabled && !topic.is_delivery_enabled) {
                            checkbox.prop('checked', false);
                            checkbox.removeClass('indeterminate');
                        } else {
                            checkbox.prop('checked', false);
                            checkbox.addClass('indeterminate');
                        }

                        setupTriStateCheckbox(checkbox[0]);
                    } else {
                    }
                });

                // Log final state of checkboxes
                var checkedCount = $('#multi-select-div input[name="topic_name"]:checked').length;
            } else {
            }
        } else {
        }
    } else {
    }

    // Add mutation observer to detect changes to multi-select-div
    var targetNode = document.getElementById('multi-select-div');
    if (targetNode && !targetNode._observer) {
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                }
            });
        });
        observer.observe(targetNode, { childList: true, subtree: true });
        targetNode._observer = observer;
    }

    // Comprehensive diagnostic logging
    var tableSelector = isEditMode ? '#id_edit-multi-select-table' : '#multi-select-table';
    var tdSelector = isEditMode ? '#id_edit-td_topic_list' : '#td_topic_list';
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.on_sec_def_changed = function() {
    var sec_base_id = $('#id_sec_base_id').val();
    if(sec_base_id) {
        var cluster_id = $('#cluster_id').val();
        var url = String.format('/zato/pubsub/subscription/sec-def-topic-sub-list/{0}/cluster/{1}/', sec_base_id, cluster_id);
        $.fn.zato.post(url, function(data, status) {
            $.fn.zato.pubsub.populate_sec_def_topics_callback(data, status, null);
        }, null, null, true);
    }
    else {
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

        // Load REST channels
        $.fn.zato.pubsub.subscription.loadRestChannels();

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

            if (instance.delivery_type !== 'push') {
                $('#rest-endpoint-edit').hide();
                $('#push-service-edit').hide();
                $('#push-type-edit').hide();
            } else {
                $('#push-type-edit').show();

                if (instance.push_type === 'rest') {
                    $('#rest-endpoint-edit').show();
                    $('#push-service-edit').hide();
                } else if (instance.push_type === 'service') {
                    $('#rest-endpoint-edit').hide();
                    $('#push-service-edit').show();
                } else {
                    $('#rest-endpoint-edit').hide();
                    $('#push-service-edit').hide();
                }
            }

            $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('edit', instance_id);

            // Load topics for the current security definition in edit mode
            if(instance.sec_base_id) {
                var cluster_id = $('#cluster_id').val();
                var url = String.format('/zato/pubsub/subscription/sec-def-topic-sub-list/{0}/cluster/{1}/', instance.sec_base_id, cluster_id);
                $.fn.zato.post(url, function(data, status) {
                    $.fn.zato.pubsub.populate_sec_def_topics_callback(data, status, instance_id);
                }, null, null, true);
            }
        }
    });

    // Override the close function to clean up spinners and selects
    var originalClose = $.fn.zato.data_table.close;
    $.fn.zato.data_table.close = function(elem) {

        // Clean up any spinners and reset visibility states
        $('.loading-spinner').remove();
        $('.security-select').removeClass('hide');
        $('#rest-endpoint-edit, #rest-endpoint-create').hide();
        $('#push-service-edit, #push-service-create').hide();
        $('#push-type-edit, #push-type-create').hide();

        // Clear the multi-select div
        $('#multi-select-div').html(Multi_Select_Empty_Message);

        // Call the original close function
        return originalClose(elem);
    };

    // Override the on_submit function to add validation
    var originalOnSubmit = $.fn.zato.data_table.on_submit;
    $.fn.zato.data_table.on_submit = function(action) {

        // Validate that at least one topic is selected or indeterminate
        var topicDivId = action === 'create' ? '#multi-select-div' : '#id_edit-multi-select-div';
        var selectedTopics = $(topicDivId + ' input[name="topic_name"]:checked');
        var indeterminateTopics = $(topicDivId + ' input[name="topic_name"].indeterminate');


        if (selectedTopics.length === 0 && indeterminateTopics.length === 0) {
            alert('At least one topic is required');
            return false;
        }

        // Validate push delivery type and clear conflicting fields
        var deliveryTypeId = action === 'create' ? '#id_delivery_type' : '#id_edit-delivery_type';
        var pushTypeId = action === 'create' ? '#id_push_type' : '#id_edit-push_type';
        var restEndpointId = action === 'create' ? '#id_rest_push_endpoint_id' : '#id_edit-rest_push_endpoint_id';
        var serviceId = action === 'create' ? '#id_push_service_name' : '#id_edit-push_service_name';

        var deliveryType = $(deliveryTypeId).val();
        var pushType = $(pushTypeId).val();


        if (deliveryType === 'push') {
            if (!pushType) {
                $.fn.zato.user_message(true, 'Push type is required when delivery type is push');
                return false;
            }
        }

        // Clear conflicting fields based on push type
        if (deliveryType === 'push') {
            if (pushType === 'rest') {
                $(serviceId).val('');
            } else if (pushType === 'service') {
                $(restEndpointId).val('');
            }
        }

        // Create hidden inputs for topic data structure
        var $form = $(topicDivId).closest('form');

        // Remove any existing topic_data inputs
        $form.find('input[name="topic_data"]').remove();

        // Add checked topics as enabled
        $(topicDivId + ' input[name="topic_name"]:checked:not(.indeterminate)').each(function() {
            var $checkbox = $(this);
            var topicName = $checkbox.val();
            var topicDataObj = {topic_name: topicName, is_pub_enabled: true, is_delivery_enabled: true};
            var topicData = JSON.stringify(topicDataObj).replace(/"/g, '&quot;');
            $form.append('<input type="hidden" name="topic_data" value="' + topicData + '">');
        });

        // Add indeterminate topics as disabled
        $(topicDivId + ' input[name="topic_name"].indeterminate').each(function() {
            var $checkbox = $(this);
            var topicName = $checkbox.val();
            var topicDataObj = {topic_name: topicName, is_pub_enabled: false, is_delivery_enabled: true};
            var topicData = JSON.stringify(topicDataObj).replace(/"/g, '&quot;');
            $form.append('<input type="hidden" name="topic_data" value="' + topicData + '">');
        });

        // Call original on_submit if validation passes
        return originalOnSubmit.call(this, action);
    };

    // Override the on_submit_complete function to add cleanup
    var originalOnSubmitComplete = $.fn.zato.data_table.on_submit_complete;
    $.fn.zato.data_table.on_submit_complete = function(data, status, action) {

        // Call the original on_submit_complete function
        return originalOnSubmitComplete(data, status, action);
    };
})

// /////////////////////////////////////////////////////////////////////////////

// Function to populate REST endpoints
$.fn.zato.pubsub.subscription.populateRestEndpoints = function(form_type, selectedId, showSpan) {
    var endpointSelectId = form_type === 'create' ? '#id_rest_push_endpoint_id' : '#id_edit-rest_push_endpoint_id';
    var endpointSpanId = form_type === 'create' ? '#rest-endpoint-create' : '#rest-endpoint-edit';


    var $endpointSelect = $(endpointSelectId);

    // Clear existing options
    $endpointSelect.empty();

    // Show loading spinner
    var $container = $endpointSelect.parent();
    $container.find('.loading-spinner').remove();
    $container.append('<span class="loading-spinner show">Loading...</span>');

    // Make AJAX call to get REST endpoints
    $.ajax({
        url: '/zato/pubsub/subscription/get-rest-endpoints/',
        type: 'GET',
        data: {
            cluster_id: '1',
            form_type: form_type
        },
        success: function(response) {
            var responseJson = JSON.stringify(response);

            // Remove loading spinner
            $container.find('.loading-spinner').remove();


            $endpointSelect.append('<option value="">Select an endpoint ...</option>');

            if (response.rest_endpoints.length > 0) {
                $.each(response.rest_endpoints, function(index, endpoint) {
                    var option = $('<option></option>')
                        .attr('value', endpoint.id)
                        .text(endpoint.name);
                    if (selectedId) {
                        if (endpoint.id == selectedId) {
                            option.prop('selected', true);
                        }
                    }
                    $endpointSelect.append(option);
                });
            }

            $endpointSelect.append('<option value="__create_new__">Create a new endpoint \u2192</option>');

            $endpointSelect.trigger('chosen:updated');

            $endpointSelect.off('change.create_new').on('change.create_new', function() {
                if ($(this).val() === '__create_new__') {
                    window.open('/zato/http-soap/?cluster=1&connection=outgoing&transport=plain_http', '_blank');
                    $(this).val('');
                    $endpointSelect.trigger('chosen:updated');
                }
            });


            // Show the span if requested
            if (showSpan) {
                var spanId = form_type === 'create' ? '#rest-endpoint-create' : '#rest-endpoint-edit';
                $(spanId).show();
            }
        },
        error: function(request, status, error) {
            // Remove loading spinner
            $container.find('.loading-spinner').remove();
            $endpointSelect.append('<option value="">Error loading endpoints</option>');
        }
    });
}

// /////////////////////////////////////////////////////////////////////////////

// Function to load REST channels using multi-checkbox component
$.fn.zato.pubsub.subscription.loadRestChannels = function() {
    var cluster_id = $('#cluster_id').val();
    var containerId = 'rest-channels-div';

    $.ajax({
        url: '/zato/pubsub/subscription/get-rest-channels/',
        type: 'GET',
        data: {
            cluster_id: cluster_id
        },
        success: function(response) {
            if (response.rest_channels.length > 0) {
                var items = [];
                for (var channelIdx = 0; channelIdx < response.rest_channels.length; channelIdx++) {
                    var channel = response.rest_channels[channelIdx];
                    items.push({
                        id: channel.id,
                        state: $.fn.zato.multi_checkbox.State.Off,
                        link: '/zato/http-soap/?cluster=' + cluster_id + '&connection=channel&transport=plain_http&query=' + encodeURIComponent(channel.name),
                        linkText: channel.name,
                        description: channel.url_path
                    });
                }

                $.fn.zato.multi_checkbox.render({
                    containerId: containerId,
                    items: items,
                    inputName: 'rest_channel_id',
                    emptyMessage: 'No REST channels available'
                });
            } else {
                $('#' + containerId).html(
                    '<table class="multi-select-table"><tr><td colspan="2">' +
                    '<span class="multi-select-message">No REST channels available</span>' +
                    '</td></tr></table>'
                );
            }
        },
        error: function(request, status, error) {
            $('#' + containerId).html(
                '<table class="multi-select-table"><tr><td colspan="2">' +
                '<span class="multi-select-message">Error loading REST channels</span>' +
                '</td></tr></table>'
            );
        }
    });
}

// /////////////////////////////////////////////////////////////////////////////

// Function to populate Services
$.fn.zato.pubsub.subscription.populateServices = function(form_type, selectedId, showSpan) {
    if (showSpan === undefined) {
        showSpan = true;
    }

    var cluster_id = '1';

    var serviceSelectId = form_type === 'create' ? '#id_push_service_name' : '#id_edit-push_service_name';
    var $serviceSelect = $(serviceSelectId);
    var serviceSpanId = form_type === 'create' ? '#push-service-create' : '#push-service-edit';
    var $serviceSpan = $(serviceSpanId);
    var pushTypeId = form_type === 'create' ? '#id_push_type' : '#id_edit-push_type';
    var currentPushType = $(pushTypeId).val();

    // Clear existing options
    $serviceSelect.empty();
    $serviceSelect.append('<option value="">Select a service</option>');

    $.get('/zato/pubsub/subscription/get-service-list/', {
        cluster_id: cluster_id,
        form_type: form_type
    })
    .done(function(response) {
        var responseJson = JSON.stringify(response);

        // Clear existing options except the first one
        $serviceSelect.find('option:not(:first)').remove();

        if (response.services.length > 0) {
            response.services.forEach(function(service) {
                var option = $('<option></option>')
                    .attr('value', service.service_name)
                    .text(service.service_name);
                if (selectedId) {
                    if (service.service_name === selectedId) {
                        option.attr('selected', 'selected');
                    } else {
                    }
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
    .fail(function(request, status, error) {
        console.error('Error loading services:', error);
    });
}

$.fn.zato.pubsub.subscription.data_table = {};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.add_row_hook = function(instance, name, html_elem, data) {

    if (name === 'sub_key') {
        instance.sub_key = data.sub_key;
    }
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_delivery_active = item.is_delivery_active == true;
    var is_pub_active = item.is_pub_active == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td style="white-space:nowrap"><a href="/zato/security/basic-auth/?cluster=1&query={0}">{1}</a></td>', encodeURIComponent(item.security), item.security);

    row += String.format('<td style="max-width:220px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;"><span class="ps-sub-key" data-sub-key="{0}">{0}</span></td>', item.sub_key);

    var delivery_css_class = is_delivery_active ? 'ps-badge-deliv-enabled' : 'ps-badge-deliv-disabled';
    var pub_css_class = is_pub_active ? 'ps-badge-pub-enabled' : 'ps-badge-pub-disabled';
    row += '<td style="text-align:center"><div class="enabled-for-inner"><div class="ps-status-cell"><span class="ps-badge ' + delivery_css_class + '">Delivery</span><span class="ps-badge ' + pub_css_class + '">Pub</span></div></div></td>';

    if(item.delivery_type === 'pull') {
        row += '<td style="text-align:center"><div class="col-center-left">Pull</div></td>';
    } else {
        if(item.push_type === 'rest' && item.rest_push_endpoint_id) {
            var endpointName = item.rest_push_endpoint_name;
            if (endpointName === null) {
                endpointName = '';
            }
            if(!endpointName) {
                var selectIds = ['#id_edit-rest_push_endpoint_id', '#id_rest_push_endpoint_id'];
                for(var selectIdx=0; selectIdx<selectIds.length; selectIdx++) {
                    $(selectIds[selectIdx] + ' option').each(function() {
                        if($(this).val() == item.rest_push_endpoint_id) {
                            endpointName = $(this).text();
                            return false;
                        }
                    });
                    if(endpointName) break;
                }
            }
            row += String.format('<td style="text-align:center"><div class="col-center-left">Push <a href="/zato/http-soap/?cluster=1&query={0}&connection=outgoing&transport=plain_http">{1}</a></div></td>',
                encodeURIComponent(endpointName), endpointName);
        } else if(item.push_type === 'service' && item.push_service_name) {
            row += String.format('<td style="text-align:center"><div class="col-center-left">Push <a href="/zato/service/?cluster=1&query={0}">{1}</a></div></td>',
                encodeURIComponent(item.push_service_name), item.push_service_name);
        } else {
            row += '<td style="text-align:center"><div class="col-center-left">Push</div></td>';
        }
    }

    row += String.format('<td>{0}</td>', item.topic_link_list);

    var pendingDepth = item.pending_depth;
    if (pendingDepth === undefined || pendingDepth === null) {
        pendingDepth = 0;
    }
    row += String.format('<td><a href="/zato/pubsub/subscription/queue/?cluster=1&sub_key={0}&queue_name={1}&state=pending">{2}</a></td>',
        encodeURIComponent(item.sub_key), encodeURIComponent(item.security), pendingDepth);

    row += String.format('<td style="text-align:center">{0}</td>', String.format("<a href=\"javascript:$.fn.zato.pubsub.subscription.edit('{0}');\">Edit</a>", item.id));
    row += String.format('<td style="text-align:center">{0}</td>', String.format("<a href=\"javascript:$.fn.zato.pubsub.subscription.delete_('{0}');\">Delete</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_delivery_active);
    row += String.format("<td class='ignore'>{0}</td>", is_pub_active);
    row += String.format("<td class='ignore'>{0}</td>", item.delivery_type);

    row += String.format("<td class='ignore'>{0}</td>", item.sec_base_id);
    row += String.format("<td class='ignore'>{0}</td>", item.push_type);
    row += String.format("<td class='ignore'>{0}</td>", item.rest_push_endpoint_id);

    row += String.format("<td class='ignore'>{0}</td>", item.rest_push_endpoint_name);
    row += String.format("<td class='ignore'>{0}</td>", item.push_service_name);
    row += String.format("<td class='ignore'>{0}</td>", item.topic_name_list);
    row += String.format("<td class='ignore'>{0}</td>", pendingDepth);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.create = function() {

    // Clear the multi-select div before opening create form
    $('#multi-select-div').html(Multi_Select_Empty_Message);

    // Log security definitions in the create form select
    var $secSelect = $('#id_sec_base_id');
    if ($secSelect.length > 0) {
        var secOptions = [];
        $secSelect.find('option').each(function() {
            var $option = $(this);
            secOptions.push({
                value: $option.val(),
                text: $option.text()
            });
        });
    } else {
    }

    $.fn.zato.data_table._create_edit('create', 'Create a new pub/sub subscription', null);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.edit = function(instance_id) {

    var instance = $.fn.zato.data_table.data[instance_id];
    var instanceJson = JSON.stringify(instance);

    var form = $('#edit-form');

    var is_delivery_active = $.fn.zato.like_bool(instance.is_delivery_active);
    form.find('#id_edit-is_delivery_active').prop('checked', is_delivery_active);

    var is_pub_active = $.fn.zato.like_bool(instance.is_pub_active);
    form.find('#id_edit-is_pub_active').prop('checked', is_pub_active);

    form.find('#id_edit-sub_key').val(instance.sub_key);
    form.find('#id_edit-delivery_type').val(instance.delivery_type);
    form.find('#id_edit-push_type').val(instance.push_type);
    form.find('#id_edit-rest_push_endpoint_id').val(instance.rest_push_endpoint_id);
    form.find('#id_edit-push_service_name').val(instance.push_service_name);


    // Handle security definition display as link instead of select
    var $container = $('#edit-sec-def-container');
    if ($container.length) {
        // Hide the select element
        $('#id_edit-sec_base_id').hide();

        // Clear all existing content from the container
        $container.empty();

        // Add hidden input for the security definition ID
        $container.append('<input type="hidden" id="id_edit-sec_base_id" name="edit-sec_base_id" value="' + instance.sec_base_id + '"/>');

        // Display the security definition name as a link
        var secName = instance.security;
        var clusterID = '1';
        var secLink = '<a href="/zato/security/basic-auth/?cluster=' + clusterID + '&query=' + encodeURIComponent(secName) + '" target="_blank">' + secName + '</a>';
        $container.append(secLink);
    } else {
        // Default to original behavior if container doesn't exist
        form.find('#id_edit-sec_base_id').val(instance.sec_base_id);
    }

    // Hide REST endpoint span immediately to prevent flicker during form population
    $('#rest-endpoint-edit').hide();

    // Store the instance_id for the dialog open callback
    $.fn.zato.pubsub.subscription._current_edit_instance_id = instance_id;

    $.fn.zato.data_table._create_edit('edit', 'Update the pub/sub subscription', instance_id, false, false);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.stripHtml = function(html) {
    var temp = document.createElement('div');
    temp.innerHTML = html;
    return temp.textContent || temp.innerText || "";
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.create_edit_submit = function(data, status, request) {
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

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.delete_ = function(id) {
    var instance = $.fn.zato.data_table.data[id];

    var descriptor = 'Security: ' + instance.security + '\nDelivery: ' + instance.delivery_type;

    // Define callback to repopulate security definitions after delete completes
    var afterDeleteCallback = function() {

        // Repopulate security definitions for the create form
        $.fn.zato.common.security.populateSecurityDefinitions(
            'create',
            null,
            '/zato/pubsub/subscription/get-security-definitions/',
            '#id_sec_base_id'
        );
    };

    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Pub/sub subscription deleted:\n' + descriptor,
        'Are you sure you want to delete pub/sub subscription?\n\n' + descriptor,
        true, null, null, null, null, afterDeleteCallback);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility = function(form_type, instance_id) {

    var $deliveryType = form_type === 'create' ? $('#id_delivery_type') : $('#id_edit-delivery_type');
    var $pushType = form_type === 'create' ? $('#id_push_type') : $('#id_edit-push_type');
    var $pushTypeSpan = form_type === 'create' ? $('#push-type-create') : '#push-type-edit';
    var $restEndpointSpan = form_type === 'create' ? '#rest-endpoint-create' : '#rest-endpoint-edit';
    var $serviceSpan = form_type === 'create' ? '#push-service-create' : '#push-service-edit';


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

    if ($deliveryType.length === 0) {
        return;
    }
    if ($pushTypeSpan.length === 0) {
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

        // Load REST endpoints if not already loaded
        if (!window.restEndpointsLoaded) {
            var selectedEndpointId = null;
            if (form_type !== 'create') {
                if (instance_id) {
                    selectedEndpointId = $.fn.zato.data_table.data[instance_id].rest_push_endpoint_id;
                }
            }
            $.fn.zato.pubsub.subscription.populateRestEndpoints(form_type, selectedEndpointId, false);
            window.restEndpointsLoaded = true;
        }

        // Load services if not already loaded
        if (!window.servicesLoaded) {
            var selectedServiceId = null;
            if (form_type !== 'create') {
                if (instance_id) {
                    selectedServiceId = $.fn.zato.data_table.data[instance_id].push_service_name;
                }
            }
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

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Live form updates registration
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.subscription._snapshot_topic_values = function(container_selector) {
    var values = {};
    $(container_selector).find('input[name="topic_name"]').each(function() {
        values[this.id] = $(this).val();
    });
    return values;
};

$.fn.zato.pubsub.subscription._puff_changed_rows = function(container_selector, old_values) {
    $(container_selector).find('input[name="topic_name"]').each(function() {
        var checkbox = $(this);
        var old_value = old_values[this.id];
        if (old_value === undefined || old_value !== checkbox.val()) {
            $.fn.zato.live_form_updates._puff(checkbox.closest('tr'));
        }
    });

    var old_ids = Object.keys(old_values);
    for (var idIdx = 0; idIdx < old_ids.length; idIdx++) {
        if (!$(container_selector).find('#' + old_ids[idIdx]).length) {
            $.fn.zato.live_form_updates._puff($(container_selector).find('.multi-select-table'));
            break;
        }
    }
};

$.fn.zato.pubsub.subscription._reload_create_topics = function() {
    var sec_base_id = $('#id_sec_base_id').val();
    if (sec_base_id) {
        var old_values = $.fn.zato.pubsub.subscription._snapshot_topic_values('#multi-select-div');
        var cluster_id = $('#cluster_id').val();
        var url = String.format('/zato/pubsub/subscription/sec-def-topic-sub-list/{0}/cluster/{1}/', sec_base_id, cluster_id);
        $.fn.zato.post(url, function(data, status) {
            $.fn.zato.pubsub.populate_sec_def_topics_callback(data, status, null);
            $.fn.zato.pubsub.subscription._puff_changed_rows('#multi-select-div', old_values);
        }, null, null, true);
    }
};

$.fn.zato.pubsub.subscription._reload_edit_topics = function() {
    var instance_id = $.fn.zato.pubsub.subscription._current_edit_instance_id;
    if (instance_id) {
        var instance = $.fn.zato.data_table.data[instance_id];
        if (instance && instance.sec_base_id) {
            var old_values = $.fn.zato.pubsub.subscription._snapshot_topic_values('#id_edit-multi-select-div');
            var cluster_id = $('#cluster_id').val();
            var url = String.format('/zato/pubsub/subscription/sec-def-topic-sub-list/{0}/cluster/{1}/', instance.sec_base_id, cluster_id);
            $.fn.zato.post(url, function(data, status) {
                $.fn.zato.pubsub.populate_sec_def_topics_callback(data, status, instance_id);
                $.fn.zato.pubsub.subscription._puff_changed_rows('#id_edit-multi-select-div', old_values);
            }, null, null, true);
        }
    }
};

$.fn.zato.live_form_updates.register('create', [
    {object_type: 'security_basic', target_select: '#id_sec_base_id'},
    {object_type: 'service', target_select: '#id_push_service_name'},
    {object_type: 'rest_outconn', target_select: '#id_rest_push_endpoint_id'},
    {object_type: 'pubsub_topic', handler: 'multi_checkbox', container: '#multi-select-div', reload_callback: function() { $.fn.zato.pubsub.subscription._reload_create_topics(); }}
]);

$.fn.zato.live_form_updates.register('edit', [
    {object_type: 'security_basic', target_select: '#id_edit-sec_base_id'},
    {object_type: 'service', target_select: '#id_edit-push_service_name'},
    {object_type: 'rest_outconn', target_select: '#id_edit-rest_push_endpoint_id'},
    {object_type: 'pubsub_topic', handler: 'multi_checkbox', container: '#id_edit-multi-select-div', reload_callback: function() { $.fn.zato.pubsub.subscription._reload_edit_topics(); }}
]);

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

})(jQuery);
