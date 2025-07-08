// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.pubsub.subscription');

$.fn.zato.data_table.PubSubSubscription = new Class({
    toString: function() {
        var s = '<PubSubSubscription id:{0} sub_key:{1} topic_name:{2} sec_name:{3} pattern_matched:{4}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.sub_key ? this.sub_key : '(none)',
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
    row += String.format('<td>{0}</td>', item.sub_key);
    row += String.format('<td style="text-align:center">{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.sec_name);
    row += String.format('<td>{0}</td>', item.topic_name);
    row += String.format('<td>{0}</td>', item.delivery_type || 'pull');
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
    $.fn.zato.data_table._create_edit('create', 'Create a new pub/sub subscription', null);
    // Populate topics and security definitions after form opens
    setTimeout(function() {
        $.fn.zato.pubsub.common.populateTopics('create', null, '/zato/pubsub/subscription/get-topics/', '#id_topic_id');
        $.fn.zato.common.security.populateSecurityDefinitions('create', null, '/zato/pubsub/subscription/get-security-definitions/', '#id_sec_base_id');
        $.fn.zato.pubsub.subscription.populateRestEndpoints('create', null, '/zato/pubsub/subscription/get-rest-endpoints/', '#id_rest_push_endpoint_id');
        $.fn.zato.pubsub.subscription.setupDeliveryTypeHandler('create');
    }, 100);
}

$.fn.zato.pubsub.subscription.edit = function(id) {
    $.fn.zato.data_table.edit('edit', 'Update pub/sub subscription', id);
    // Populate topics and security definitions after form opens with current selections
    setTimeout(function() {
        var currentTopicId = $('#id_edit-topic_id').val();
        var currentSecId = $('#id_edit-sec_base_id').val();
        var currentRestEndpointId = $('#id_edit-rest_push_endpoint_id').val();
        $.fn.zato.pubsub.common.populateTopics('edit', currentTopicId, '/zato/pubsub/subscription/get-topics/', '#id_edit-topic_id');
        $.fn.zato.common.security.populateSecurityDefinitions('edit', currentSecId, '/zato/pubsub/subscription/get-security-definitions/', '#id_edit-sec_base_id');
        $.fn.zato.pubsub.subscription.populateRestEndpoints('edit', currentRestEndpointId, '/zato/pubsub/subscription/get-rest-endpoints/', '#id_edit-rest_push_endpoint_id');
        $.fn.zato.pubsub.subscription.setupDeliveryTypeHandler('edit');
    }, 100);
}

$.fn.zato.pubsub.subscription.delete_ = function(id) {

    var instance = $.fn.zato.data_table.data[id];
    var descriptor = 'Security: ' + instance.sec_name + '\nTopic: ' + instance.topic_name + '\nKey: ' + instance.sub_key + '\nDelivery: ' + (instance.delivery_type || 'pull') + '\n\n';

    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Pub/sub subscription deleted:\n' + descriptor,
        'Are you sure you want to delete pub/sub subscription?\n\n' + descriptor,
        true);
}

$.fn.zato.pubsub.subscription.populateRestEndpoints = function(form_type, selectedValue, url, selectId) {
    var clusterId = $("#cluster_id").val() || $("#id_edit-cluster_id").val();
    var $select = $(selectId);
    var $loadingSpinner = $('<span class="loading-spinner">Loading...</span>');

    // Show loading spinner
    $select.after($loadingSpinner);
    setTimeout(function() {
        $loadingSpinner.addClass('show');
    }, 10);

    $.get(url, {
        cluster_id: clusterId,
        form_type: form_type
    }, function(data) {
        $select.empty();
        $select.append('<option value="">-- Select REST endpoint --</option>');

        if (data.rest_endpoints && data.rest_endpoints.length > 0) {
            $.each(data.rest_endpoints, function(index, endpoint) {
                var option = $('<option></option>')
                    .attr('value', endpoint.id)
                    .text(endpoint.name);

                if (selectedValue && endpoint.id == selectedValue) {
                    option.attr('selected', 'selected');
                }

                $select.append(option);
            });
        } else {
            $select.append('<option value="" disabled>No REST endpoints available</option>');
        }

        // Remove loading spinner and show select
        $loadingSpinner.removeClass('show');
        setTimeout(function() {
            $loadingSpinner.remove();
            $select.show();
        }, 50);
    }).fail(function() {
        $select.empty();
        $select.append('<option value="" disabled>Error loading REST endpoints</option>');
        $loadingSpinner.removeClass('show');
        setTimeout(function() {
            $loadingSpinner.remove();
            $select.show();
        }, 50);
    });
}

$.fn.zato.pubsub.subscription.setupDeliveryTypeHandler = function(form_type) {
    var deliveryTypeId = form_type === 'create' ? '#id_delivery_type' : '#id_edit-delivery_type';
    var restEndpointId = form_type === 'create' ? '#id_rest_push_endpoint_id' : '#id_edit-rest_push_endpoint_id';

    var $deliveryType = $(deliveryTypeId);
    var $restEndpoint = $(restEndpointId);

    function toggleRestEndpoint() {
        if ($deliveryType.val() === 'push') {
            $restEndpoint.prop('disabled', false);
            $restEndpoint.closest('tr').show();
        } else {
            $restEndpoint.prop('disabled', true);
            $restEndpoint.val('');
            $restEndpoint.closest('tr').hide();
        }
    }

    // Set initial state
    toggleRestEndpoint();

    // Handle delivery type changes
    $deliveryType.on('change', toggleRestEndpoint);
}
