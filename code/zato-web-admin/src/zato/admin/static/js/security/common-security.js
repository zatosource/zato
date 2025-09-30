// Common security definitions handling utility

$.namespace('zato.common.security');

/**
 * Populate security definitions dropdown with AJAX loading and empty state handling
 * @param {string} formType - 'create' or 'edit'
 * @param {string} selectedId - Previously selected security definition ID
 * @param {string} endpoint - AJAX endpoint URL
 * @param {string} selectId - CSS selector for the dropdown
 */
$.fn.zato.common.security.populateSecurityDefinitions = function(formType, selectedId, endpoint, selectId) {
    var clusterId = $('#cluster_id').val();
    var select = $(selectId);
    var selectContainer = select.parent();

    // Show spinner with smooth transition and minimum display time
    var startTime = Date.now();

    // Hide select and clear existing content
    select.hide();
    selectContainer.find('.no-security-definitions-message').remove();
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
        success: function(response) {
            // Re-declare variables for callback scope
            var select = $(selectId);
            var selectContainer = select.parent();
            var spinner = selectContainer.find('.loading-spinner');

            // Ensure minimum display time for smooth UX
            var elapsedTime = Date.now() - startTime;
            var minDisplayTime = 300;
            var remainingTime = Math.max(0, minDisplayTime - elapsedTime);

            setTimeout(function() {
                // Fade out spinner
                spinner.removeClass('show');

                setTimeout(function() {
                    // Remove spinner and clear any existing messages
                    selectContainer.find('.loading-spinner').remove();
                    selectContainer.find('.no-security-definitions-message').remove();
                    select.empty();

                    if (response.security_definitions && response.security_definitions.length > 0) {
                        // Add placeholder option for create forms
                        if (formType === 'create') {
                            var placeholderOption = $('<option></option>')
                                .attr('value', '')
                                .attr('selected', 'selected')
                                .text('Select a security definition');
                            select.append(placeholderOption);
                        }

                        // Populate select with available security definitions
                        $.each(response.security_definitions, function(index, item) {
                            var option = $('<option></option>')
                                .attr('value', item.id)
                                .text(item.name);
                            if (selectedId && item.id == selectedId) {
                                option.attr('selected', 'selected');
                            } else if (index === 0 && !selectedId && formType !== 'create') {
                                option.attr('selected', 'selected');
                            }
                            select.append(option);
                        });

                        // Show the select dropdown
                        select.show().removeClass('hide').addClass('security-select');

                        // Enable OK button
                        var okButton = select.closest('form').find('input[type="submit"]');
                        okButton.prop('disabled', false);
                    } else {
                        // No security definitions available - show message
                        var hasExistingClients = $.fn.zato.data_table.data && Object.keys($.fn.zato.data_table.data).length > 0;
                        var message = hasExistingClients ? 'No security definitions left' : 'No security definitions available';

                        // Add message with link
                        var messageElement = $('<span class="no-security-definitions-message" style="font-style: italic; color: #666;">' + message + ' - <a href="/zato/security/basic-auth/?cluster=' + clusterId + '" target="_blank">Click to create one</a></span>');
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
            var errorElement = $('<span class="no-security-definitions-message" style="font-style: italic; color: #cc0000;">Error loading security definitions</span>');
            selectContainer.append(errorElement);

            // Disable OK button
            var okButton = $(selectId).closest('form').find('input[type="submit"]');
            okButton.prop('disabled', true);
        }
    });
};
