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

            // Debug all options in the select
            var options = [];
            $('#id_topic_id option').each(function() {
                options.push({
                    value: $(this).val(),
                    text: $(this).text(),
                    selected: $(this).prop('selected')
                });
            });
            console.log('DEBUG: Select options:', JSON.stringify(options));
            console.log('DEBUG: Select HTML:', $('#id_topic_id')[0].outerHTML);

            if (window.topicSelectCreate) {
                console.log('DEBUG: Destroying existing topicSelectCreate');
                window.topicSelectCreate.destroy();
            }

            try {
                console.log('DEBUG: Setting multiple attribute on select');
                $('#id_topic_id').attr('multiple', true);

                console.log('DEBUG: Creating new SlimSelect for create form');
                window.topicSelectCreate = new SlimSelect({
                    select: '#id_topic_id',
                    settings: {
                        searchPlaceholder: 'Search topics...',
                        placeholderText: 'Select topics',
                        closeOnSelect: false
                    }
                });
                console.log('DEBUG: SlimSelect created successfully, type:', typeof window.topicSelectCreate);
                console.log('DEBUG: SlimSelect container classes:', $('.ss-main').length);
                console.log('DEBUG: Original select display:', $('#id_topic_id').css('display'));
                console.log('DEBUG: Original select visibility:', $('#id_topic_id').css('visibility'));
                console.log('DEBUG: SlimSelect main elements:', $('.ss-main').length);

                // Debug SlimSelect data
                if (window.topicSelectCreate && window.topicSelectCreate.getData) {
                    console.log('DEBUG: SlimSelect data:', JSON.stringify(window.topicSelectCreate.getData()));
                }

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
                console.error('DEBUG: Error creating SlimSelect:', error);
            }

            // Don't show original select - SlimSelect handles its own visibility
            console.log('DEBUG: SlimSelect container visibility:', $('.ss-main').css('display'));
            console.log('DEBUG: SlimSelect container position:', $('.ss-main').css('position'));
            console.log('DEBUG: Original select should be hidden:', $('#id_topic_id').css('display'));
            // Force show SlimSelect container if it's hidden
            $('.ss-main').show();
            console.log('DEBUG: After forcing SlimSelect show:', $('.ss-main').css('display'));

            // Debug SlimSelect dropdown interaction
            console.log('DEBUG: SlimSelect single element found:', $('.ss-single').length);
            console.log('DEBUG: SlimSelect multi element found:', $('.ss-multi').length);
            console.log('DEBUG: SlimSelect content found:', $('.ss-content').length);
            console.log('DEBUG: SlimSelect list found:', $('.ss-list').length);
            console.log('DEBUG: SlimSelect options found:', $('.ss-option').length);

            // Debug SlimSelect container structure in detail
            var ssMain = $('.ss-main');
            console.log('DEBUG: ss-main found:', ssMain.length);
            if (ssMain.length > 0) {
                console.log('DEBUG: ss-main HTML:', ssMain[0].outerHTML.substring(0, 500));
                console.log('DEBUG: ss-main children:', ssMain.children().length);
                var mainChildren = [];
                ssMain.children().each(function(i, el) {
                    mainChildren.push({
                        index: i,
                        className: el.className,
                        tagName: el.tagName,
                        id: el.id,
                        style: el.style.cssText,
                        innerHTML: el.innerHTML.substring(0, 100)
                    });
                });
                console.log('DEBUG: ss-main children details:', JSON.stringify(mainChildren));
            }

            // Debug SlimSelect values container
            var ssValues = $('.ss-values');
            console.log('DEBUG: ss-values found:', ssValues.length);
            if (ssValues.length > 0) {
                console.log('DEBUG: ss-values HTML:', ssValues[0].outerHTML.substring(0, 300));
                var valuesChildren = [];
                ssValues.children().each(function(i, el) {
                    valuesChildren.push({
                        index: i,
                        className: el.className,
                        tagName: el.tagName,
                        textContent: el.textContent
                    });
                });
                console.log('DEBUG: ss-values children:', JSON.stringify(valuesChildren));
            }

            // Debug all SlimSelect related elements
            var allSsElements = $('[class*="ss-"]');
            console.log('DEBUG: All ss- elements found:', allSsElements.length);
            var ssElementsInfo = [];
            allSsElements.each(function(i, el) {
                ssElementsInfo.push({
                    index: i,
                    className: el.className,
                    tagName: el.tagName,
                    id: el.id,
                    display: $(el).css('display'),
                    visibility: $(el).css('visibility')
                });
            });
            console.log('DEBUG: All ss- elements info:', JSON.stringify(ssElementsInfo));

            // Debug SlimSelect instance properties
            if (window.topicSelectCreate) {
                console.log('DEBUG: SlimSelect settings:', JSON.stringify({
                    isMultiple: window.topicSelectCreate.settings ? window.topicSelectCreate.settings.isMultiple : 'no settings',
                    closeOnSelect: window.topicSelectCreate.settings ? window.topicSelectCreate.settings.closeOnSelect : 'no settings',
                    disabled: window.topicSelectCreate.settings ? window.topicSelectCreate.settings.disabled : 'no settings'
                }));
            }

            // Add click listener to debug dropdown opening for multi-select
            $('.ss-multi').on('click', function() {
                console.log('DEBUG: SlimSelect multi clicked');
                setTimeout(function() {
                    console.log('DEBUG: After click - ss-list display:', $('.ss-list').css('display'));
                    console.log('DEBUG: After click - ss-option count:', $('.ss-option').length);
                }, 100);
            });
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

            // Debug all options in the edit select
            var editOptions = [];
            $('#id_edit-topic_id option').each(function() {
                editOptions.push({
                    value: $(this).val(),
                    text: $(this).text(),
                    selected: $(this).prop('selected')
                });
            });
            console.log('DEBUG: Edit select options:', JSON.stringify(editOptions));
            console.log('DEBUG: Edit select HTML:', $('#id_edit-topic_id')[0].outerHTML);

            if (window.topicSelectEdit) {
                console.log('DEBUG: Destroying existing topicSelectEdit');
                window.topicSelectEdit.destroy();
            }

            try {
                console.log('DEBUG: Setting multiple attribute on edit select');
                $('#id_edit-topic_id').attr('multiple', true);

                console.log('DEBUG: Creating new SlimSelect for edit form');
                window.topicSelectEdit = new SlimSelect({
                    select: '#id_edit-topic_id',
                    settings: {
                        searchPlaceholder: 'Search topics...',
                        placeholderText: 'Select topics',
                        closeOnSelect: false
                    }
                });
                console.log('DEBUG: SlimSelect edit created successfully, type:', typeof window.topicSelectEdit);

                // Debug SlimSelect edit data
                if (window.topicSelectEdit && window.topicSelectEdit.getData) {
                    console.log('DEBUG: SlimSelect edit data:', JSON.stringify(window.topicSelectEdit.getData()));
                }

                // SlimSelect reads from the original select element automatically

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
