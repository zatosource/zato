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
    console.log('DEBUG: Create function called');
    console.log('DEBUG: SlimSelect available at function start?', typeof SlimSelect);
    console.log('DEBUG: Window SlimSelect type:', typeof window.SlimSelect);

    $.fn.zato.data_table._create_edit('create', 'Create a new pub/sub subscription', null);
    // Populate topics and security definitions after form opens
    setTimeout(function() {
        // Initialize SlimSelect after topics are populated via callback
        $.fn.zato.pubsub.common.populateTopics('create', null, '/zato/pubsub/subscription/get-topics/', '#id_topic_id', function() {
            console.log('DEBUG: populateTopics callback executed for create');
            console.log('DEBUG: SlimSelect available?', typeof SlimSelect);
            console.log('DEBUG: Select element exists?', $('#id_topic_id').length);
            console.log('DEBUG: Select element tag:', $('#id_topic_id')[0] ? $('#id_topic_id')[0].tagName : 'none');
            console.log('DEBUG: Select element options count:', $('#id_topic_id option').length);
            console.log('DEBUG: CSS files loaded count:', $('link[href*="slimselect"]').length);

            if (window.topicSelectCreate) {
                console.log('DEBUG: Destroying existing topicSelectCreate');
                window.topicSelectCreate.destroy();
            }

            try {
                console.log('DEBUG: Creating new SlimSelect for create form');
                window.topicSelectCreate = new SlimSelect({
                    select: '#id_topic_id',
                    settings: {
                        multiple: true,
                        closeOnSelect: false,
                        searchPlaceholder: 'Search topics...',
                        placeholderText: 'Select topics'
                    }
                });
                console.log('DEBUG: SlimSelect created successfully, type:', typeof window.topicSelectCreate);
                console.log('DEBUG: SlimSelect container classes:', $('.ss-main').length);
                console.log('DEBUG: Original select display:', $('#id_topic_id').css('display'));
                console.log('DEBUG: Original select visibility:', $('#id_topic_id').css('visibility'));
                console.log('DEBUG: SlimSelect main elements:', $('.ss-main').length);
            } catch (error) {
                console.error('DEBUG: Error creating SlimSelect:', error);
            }

            // Don't show original select - SlimSelect handles its own visibility
            console.log('DEBUG: SlimSelect container visibility:', $('.ss-main').css('display'));
            console.log('DEBUG: SlimSelect container position:', $('.ss-main').css('position'));
            console.log('DEBUG: Original select should be hidden:', $('#id_topic_id').css('display'));
            // Force show SlimSelect container if it's hidden
            $('.ss-main').show();
            console.log('DEBUG: After forcing SlimSelect show:', $('.ss-main').css('display'));
        });
        $.fn.zato.common.security.populateSecurityDefinitions('create', null, '/zato/pubsub/subscription/get-security-definitions/', '#id_sec_base_id');
        $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('create');
    }, 200);
}

$.fn.zato.pubsub.subscription.edit = function(id) {
    console.log('DEBUG: Edit function called');
    console.log('DEBUG: SlimSelect available at edit function start?', typeof SlimSelect);
    console.log('DEBUG: Window SlimSelect type:', typeof window.SlimSelect);

    $.fn.zato.data_table.edit('edit', 'Update pub/sub subscription', id);
    // Populate topics and security definitions after form opens with current selections
    setTimeout(function() {
        var currentTopicId = $('#id_edit-topic_id').val();
        var currentSecId = $('#id_edit-sec_base_id').val();
        var currentRestEndpointId = $('#id_edit-rest_push_endpoint_id').val();
        // Initialize SlimSelect after topics are populated via callback
        $.fn.zato.pubsub.common.populateTopics('edit', currentTopicId, '/zato/pubsub/subscription/get-topics/', '#id_edit-topic_id', function() {
            console.log('DEBUG: populateTopics callback executed for edit');
            console.log('DEBUG: SlimSelect available?', typeof SlimSelect);
            console.log('DEBUG: Edit select element exists?', $('#id_edit-topic_id').length);
            console.log('DEBUG: Edit select element tag:', $('#id_edit-topic_id')[0] ? $('#id_edit-topic_id')[0].tagName : 'none');
            console.log('DEBUG: Edit select element options count:', $('#id_edit-topic_id option').length);

            if (window.topicSelectEdit) {
                console.log('DEBUG: Destroying existing topicSelectEdit');
                window.topicSelectEdit.destroy();
            }

            try {
                console.log('DEBUG: Creating new SlimSelect for edit form');
                window.topicSelectEdit = new SlimSelect({
                    select: '#id_edit-topic_id',
                    settings: {
                        multiple: true,
                        closeOnSelect: false,
                        searchPlaceholder: 'Search topics...',
                        placeholderText: 'Select topics'
                    }
                });
                console.log('DEBUG: SlimSelect edit created successfully, type:', typeof window.topicSelectEdit);
            } catch (error) {
                console.error('DEBUG: Error creating SlimSelect edit:', error);
            }

            // Don't show original select - SlimSelect handles its own visibility
            console.log('DEBUG: Edit SlimSelect container visibility:', $('.ss-main').css('display'));
            console.log('DEBUG: Edit original select should be hidden:', $('#id_edit-topic_id').css('display'));
            // Force show SlimSelect container if it's hidden
            $('.ss-main').show();
            console.log('DEBUG: Edit after forcing SlimSelect show:', $('.ss-main').css('display'));
        });
        $.fn.zato.common.security.populateSecurityDefinitions('edit', currentSecId, '/zato/pubsub/subscription/get-security-definitions/', '#id_edit-sec_base_id');
        $.fn.zato.pubsub.subscription.setupDeliveryTypeVisibility('edit');
    }, 200);
}

$.fn.zato.pubsub.subscription.delete_ = function(id) {

    var instance = $.fn.zato.data_table.data[id];
    var descriptor = 'Security: ' + instance.sec_name + '\nTopic: ' + instance.topic_name + '\nKey: ' + instance.sub_key + '\nDelivery: ' + (instance.delivery_type || 'pull') + '\n\n';

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
