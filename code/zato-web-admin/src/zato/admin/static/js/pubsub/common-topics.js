(function($) {

// Common topics handling utility

$.namespace('zato.pubsub.common');

// /////////////////////////////////////////////////////////////////////////////

// Populate topics dropdown with AJAX loading and empty state handling
$.fn.zato.pubsub.common.populateTopics = function(formType, selectedNamesOrIds, endpoint, selectId, callback) {

    var clusterId = $('#cluster_id').val();
    var select = $(selectId);
    var selectContainer = select.parent();


    // Hide select and clear existing content
    select.hide();
    selectContainer.find('.no-topics-message').remove();
    selectContainer.find('.loading-spinner').remove();

    // Add spinner
    var spinner = $('<span class="loading-spinner" style="font-style: italic; color: #666;">Loading ..</span>');
    selectContainer.append(spinner);
    spinner.addClass('show');

    $.ajax({
        url: endpoint,
        type: 'GET',
        data: {
            cluster_id: clusterId,
            form_type: formType
        },
        success: function(data) {
            selectContainer.find('.loading-spinner').remove();
            select.empty();

            if (data.topics && data.topics.length > 0) {

                // Normalize selectedNamesOrIds to array and match to topic IDs
                var selectedIdsArray = [];
                if (selectedNamesOrIds) {
                    var inputArray = Array.isArray(selectedNamesOrIds) ? selectedNamesOrIds : [selectedNamesOrIds];

                    inputArray.forEach(function(nameOrId) {
                        var str = nameOrId.toString();
                        var topicById = data.topics.find(function(topic) { return topic.id.toString() === str; });
                        if (topicById) {
                            selectedIdsArray.push(topicById.id.toString());
                        } else {
                            var topicByName = data.topics.find(function(topic) { return topic.name === str; });
                            if (topicByName) {
                                selectedIdsArray.push(topicByName.id.toString());
                            }
                        }
                    });
                }

                // Add topic options
                var selectedCount = 0;
                $.each(data.topics, function(index, topic) {

                    var option = $('<option></option>')
                        .attr('value', topic.id)
                        .text(topic.name);

                    var shouldSelect = false;
                    if (selectedIdsArray.length > 0 && selectedIdsArray.indexOf(topic.id.toString()) !== -1) {
                        shouldSelect = true;
                        selectedCount++;
                    } else if (index === 0 && selectedIdsArray.length === 0) {
                        shouldSelect = true;
                    }

                    if (shouldSelect) {
                        option.attr('selected', 'selected');
                    }

                    select.append(option);
                });

                select.removeClass('hide').addClass('topic-select');

                // Enable OK button
                var okButton = select.closest('form').find('input[type="submit"]');
                okButton.prop('disabled', false);

                // Execute callback if provided
                if (callback && typeof callback === 'function') {
                    callback();
                } else {
                    select.show();
                }
            } else {
                // No topics available
                var hasExistingTopics = $.fn.zato.data_table.data && Object.keys($.fn.zato.data_table.data).length > 0;
                var message = hasExistingTopics ? 'No topics left' : 'No topics available';

                var messageElement = $('<span class="no-topics-message" style="font-style: italic; color: #666;">' + message + ' - <a href="/zato/pubsub/topic/?cluster=' + clusterId + '" target="_blank">Click to create one</a></span>');
                selectContainer.append(messageElement);

                var okButton = select.closest('form').find('input[type="submit"]');
                okButton.prop('disabled', true);
            }
        },
        error: function(xhr, status, error) {
            selectContainer.find('.loading-spinner').remove();

            var errorElement = $('<span class="no-topics-message" style="font-style: italic; color: #d00;">Error loading topics</span>');
            selectContainer.append(errorElement);

            var okButton = select.closest('form').find('input[type="submit"]');
            okButton.prop('disabled', true);
        }
    });
};

})(jQuery);
