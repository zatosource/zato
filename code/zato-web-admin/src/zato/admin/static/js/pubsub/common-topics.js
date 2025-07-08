// Common topics handling utility

$.namespace('zato.pubsub.common');

/**
 * Populate topics dropdown with AJAX loading and empty state handling
 * @param {string} formType - 'create' or 'edit'
 * @param {string} selectedId - Previously selected topic ID
 * @param {string} endpoint - AJAX endpoint URL
 * @param {string} selectId - CSS selector for the dropdown
 * @param {Function} callback - Optional callback to execute after topics are loaded
 */
$.fn.zato.pubsub.common.populateTopics = function(formType, selectedId, endpoint, selectId, callback) {
    var clusterId = $('#cluster_id').val();
    var select = $(selectId);
    var selectContainer = select.parent();

    // Show spinner with smooth transition and minimum display time
    var startTime = Date.now();

    // Hide select and clear existing content
    select.hide();
    selectContainer.find('.no-topics-message').remove();
    selectContainer.find('.loading-spinner').remove();

    // Add spinner
    var spinner = $('<span class="loading-spinner" style="font-style: italic; color: #666;">Loading ..</span>');
    selectContainer.append(spinner);

    // Smooth fade-in for spinner
    setTimeout(function() {
        spinner.addClass('show');
    }, 50);

    $.ajax({
        url: endpoint,
        type: 'GET',
        data: {
            cluster_id: clusterId,
            form_type: formType
        },
        success: function(data) {
            // Ensure minimum spinner display time for smooth UX
            var elapsedTime = Date.now() - startTime;
            var remainingTime = Math.max(300 - elapsedTime, 0);

            setTimeout(function() {
                // Remove spinner with fade-out
                setTimeout(function() {
                    selectContainer.find('.loading-spinner').remove();

                    // Clear existing options
                    select.empty();

                    if (data.topics && data.topics.length > 0) {
                        // Add topic options
                        $.each(data.topics, function(index, topic) {
                            var option = $('<option></option>')
                                .attr('value', topic.id)
                                .text(topic.name);

                            // Select the previously selected topic or first one
                            if (selectedId && topic.id == selectedId) {
                                option.attr('selected', 'selected');
                            } else if (index === 0 && !selectedId) {
                                option.attr('selected', 'selected');
                            }
                            select.append(option);
                        });

                        // Don't show the select yet - let callback handle it
                        select.removeClass('hide').addClass('topic-select');

                        // Enable OK button
                        var okButton = select.closest('form').find('input[type="submit"]');
                        okButton.prop('disabled', false);

                        // Execute callback if provided (callback will show the select)
                        if (callback && typeof callback === 'function') {
                            callback();
                        } else {
                            // If no callback, show the select (fallback for non-SlimSelect usage)
                            select.show();
                        }
                    } else {
                        // No topics available - show message
                        var hasExistingTopics = $.fn.zato.data_table.data && Object.keys($.fn.zato.data_table.data).length > 0;
                        var message = hasExistingTopics ? 'No topics left' : 'No topics available';

                        // Add message with link
                        var messageElement = $('<span class="no-topics-message" style="font-style: italic; color: #666;">' + message + ' - <a href="/zato/pubsub/topic/?cluster=' + clusterId + '" target="_blank">Click to create one</a></span>');
                        selectContainer.append(messageElement);

                        // Disable OK button
                        var okButton = select.closest('form').find('input[type="submit"]');
                        okButton.prop('disabled', true);
                    }
                }, 300);
            }, remainingTime);
        },
        error: function(xhr, status, error) {
            // Remove spinner on error
            selectContainer.find('.loading-spinner').remove();

            // Show error message
            var errorElement = $('<span class="no-topics-message" style="font-style: italic; color: #d00;">Error loading topics</span>');
            selectContainer.append(errorElement);

            // Disable OK button
            var okButton = select.closest('form').find('input[type="submit"]');
            okButton.prop('disabled', true);
        }
    });
};
