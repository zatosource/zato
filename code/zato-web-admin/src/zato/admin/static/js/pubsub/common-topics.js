// Common topics handling utility

$.namespace('zato.pubsub.common');

/**
 * Populate topics dropdown with AJAX loading and empty state handling
 * @param {string} formType - 'create' or 'edit'
 * @param {string|Array} selectedNamesOrIds - Selected topic names/IDs or array of topic names/IDs(s)
 * @param {string} endpoint - AJAX endpoint URL
 * @param {string} selectId - CSS selector for the dropdown
 * @param {Function} callback - Optional callback to execute after topics are loaded
 */
$.fn.zato.pubsub.common.populateTopics = function(formType, selectedNamesOrIds, endpoint, selectId, callback) {
    console.log('[DEBUG] populateTopics: Called with formType:', JSON.stringify({formType: formType, selectedNamesOrIds: selectedNamesOrIds, endpoint: endpoint, selectId: selectId}));

    var clusterId = $('#cluster_id').val();
    var select = $(selectId);
    var selectContainer = select.parent();

    console.log('[DEBUG] populateTopics: clusterId:', JSON.stringify({clusterId: clusterId, selectElementFound: select.length > 0}));

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
                        console.log('[DEBUG] populateTopics: Received topics from server:', JSON.stringify(data.topics));

                        // Normalize selectedNamesOrIds to array and match to topic IDs
                        var selectedIdsArray = [];
                        if (selectedNamesOrIds) {
                            var inputArray = Array.isArray(selectedNamesOrIds) ? selectedNamesOrIds : [selectedNamesOrIds];
                            console.log('[DEBUG] populateTopics: Input array:', JSON.stringify(inputArray));

                            // Match names or IDs to topic IDs
                            inputArray.forEach(function(nameOrId) {
                                var str = nameOrId.toString();
                                // First try to find by ID
                                var topicById = data.topics.find(function(topic) { return topic.id.toString() === str; });
                                if (topicById) {
                                    selectedIdsArray.push(topicById.id.toString());
                                    console.log('[DEBUG] populateTopics: Matched by ID:', JSON.stringify({input: str, topicId: topicById.id}));
                                } else {
                                    // Try to find by name
                                    var topicByName = data.topics.find(function(topic) { return topic.name === str; });
                                    if (topicByName) {
                                        selectedIdsArray.push(topicByName.id.toString());
                                        console.log('[DEBUG] populateTopics: Matched by name:', JSON.stringify({input: str, topicId: topicByName.id}));
                                    } else {
                                        console.log('[DEBUG] populateTopics: No match found for:', JSON.stringify(str));
                                    }
                                }
                            });
                        }
                        console.log('[DEBUG] populateTopics: Final selectedIdsArray:', JSON.stringify(selectedIdsArray));

                        // Add topic options
                        var selectedCount = 0;
                        $.each(data.topics, function(index, topic) {
                            console.log('[DEBUG] populateTopics: Processing topic:', JSON.stringify({id: topic.id, name: topic.name}));

                            var option = $('<option></option>')
                                .attr('value', topic.id)
                                .text(topic.name);

                            // Select topics that are in the selectedIds array
                            var shouldSelect = false;
                            if (selectedIdsArray.length > 0 && selectedIdsArray.indexOf(topic.id.toString()) !== -1) {
                                shouldSelect = true;
                                selectedCount++;
                                console.log('[DEBUG] populateTopics: Selecting topic by ID match:', JSON.stringify({id: topic.id, name: topic.name}));
                            } else if (index === 0 && selectedIdsArray.length === 0) {
                                // Only select first option if no specific selections provided
                                shouldSelect = true;
                                console.log('[DEBUG] populateTopics: Selecting first topic as default:', JSON.stringify({id: topic.id, name: topic.name}));
                            }

                            if (shouldSelect) {
                                option.attr('selected', 'selected');
                            }

                            console.log('[DEBUG] populateTopics: Added option:', JSON.stringify(option[0].outerHTML));
                            select.append(option);
                        });

                        console.log('[DEBUG] populateTopics: Total topics processed:', JSON.stringify({total: data.topics.length, selected: selectedCount}));

                        // Don't show the select yet - let callback handle it
                        select.removeClass('hide').addClass('topic-select');

                        // Enable OK button
                        var okButton = select.closest('form').find('input[type="submit"]');
                        okButton.prop('disabled', false);

                        // Execute callback if provided
                        console.log('[DEBUG] populateTopics: About to execute callback, callback exists:', JSON.stringify({callbackExists: callback && typeof callback === 'function'}));
                        console.log('[DEBUG] populateTopics: Final select HTML before callback:', JSON.stringify(select[0].outerHTML));
                        if (callback && typeof callback === 'function') {
                            callback();
                            console.log('[DEBUG] populateTopics: Callback executed');
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
