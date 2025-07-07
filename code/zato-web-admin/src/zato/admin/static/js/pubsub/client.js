// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubClient = new Class({
    toString: function() {
        var s = '<PubSubClient id:{0} name:{1} pattern:{2} access_type:{3}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.pattern ? this.pattern : '(none)',
                                this.access_type ? this.access_type : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

// Function to show topics popup with matching results
function showTopicsAlert(pattern, event) {
    // Don't close existing popups - allow multiple

    // Get click position from event or try to find the clicked element
    var clickX, clickY;
    if (event && event.pageX !== undefined) {
        clickX = event.pageX;
        clickY = event.pageY;
    } else {
        // Fallback: find the pattern link element
        var $link = $('a[onclick*="' + pattern.replace(/'/g, "\\'") + '"]').first();
        if ($link.length) {
            var offset = $link.offset();
            clickX = offset.left + $link.outerWidth();
            clickY = offset.top;
        } else {
            clickX = 200;
            clickY = 200;
        }
    }

    // Create unique popup ID to allow multiple popups
    var popupId = 'topic-matches-popup-' + Date.now();

    // Create popup content HTML
    var popupHtml = `
        <div id="${popupId}" title="Pattern: ${pattern}" style="font-size: 11px; line-height: 1.3; background-color: #f0f0f0;">
            <div id="${popupId}-content" style="background-color: #f0f0f0; border-radius: 0; padding: 4px;">
                <div style="text-align: center; padding: 8px; color: #666; background-color: #f0f0f0;">
                    <div style="display: inline-block; width: 12px; height: 12px; border: 1px solid #ddd; border-top: 1px solid #666; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                    <div style="margin-top: 4px; font-size: 10px;">Loading...</div>
                </div>
            </div>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            #${popupId} { background-color: #f0f0f0 !important; }
            /* Only target the dialog that contains this specific popup ID */
            .ui-dialog:has(#${popupId}) {
                background-color: #f0f0f0 !important;
                width: 20em !important;
            }
        </style>
    `;

    // Add to page and create dialog
    $('body').append(popupHtml);

    // Create draggable dialog using jQuery UI
    $('#' + popupId).dialog({
        autoOpen: true,
        width: '20em',
        height: 'auto',
        maxHeight: 350,
        resizable: false,
        draggable: true,
        position: { my: "left top", at: "left+" + (clickX + 10) + " top+" + clickY, of: window },
        close: function() {
            $(this).dialog('destroy').remove();
        },
        create: function(event, ui) {
            // Target only this specific dialog with a direct selector
            $(this).parent('.ui-dialog').css('width', '20em');
        }
    });

    // Customize the close button to be a small "x" on the right
    var $dialog = $('#' + popupId).dialog('widget');
    var $titlebar = $dialog.find('.ui-dialog-titlebar');
    var $closeBtn = $titlebar.find('.ui-dialog-titlebar-close');

    // Style the close button - white background with black X
    $closeBtn.html('×').css({
        'position': 'absolute',
        'right': '4px',
        'top': '50%',
        'transform': 'translateY(-50%)',
        'width': '14px',
        'height': '14px',
        'font-size': '12px',
        'line-height': '14px',
        'text-align': 'center',
        'color': '#000000',
        'background': '#ddd',
        'border': 'none',
        'border-radius': '0',
        'box-shadow': 'none',
        'cursor': 'pointer',
        'padding': '0'
    });

    // Remove any UI widget styling
    $closeBtn.removeClass('ui-button ui-corner-all ui-widget ui-button-icon-only ui-dialog-titlebar-close');

    // Adjust title bar to make room for close button
    $titlebar.css('position', 'relative');
    $titlebar.find('.ui-dialog-title').css('padding-right', '20px');

    // Adjust position if popup would go off screen
    var $popup = $('#' + popupId);
    var dialog = $popup.dialog('widget');
    var dialogWidth = dialog.outerWidth();
    var dialogHeight = dialog.outerHeight();
    var windowWidth = $(window).width();
    var windowHeight = $(window).height();
    var scrollTop = $(window).scrollTop();

    var newPosition = {};
    if (clickX + dialogWidth > windowWidth - 20) {
        newPosition.left = Math.max(20, windowWidth - dialogWidth - 20);
    }
    if (clickY + dialogHeight > windowHeight + scrollTop - 20) {
        newPosition.top = Math.max(scrollTop + 20, clickY - dialogHeight - 10);
    }

    if (newPosition.left !== undefined || newPosition.top !== undefined) {
        dialog.css(newPosition);
    }

    // Make AJAX call to get matching topics
    var clusterIdVal = $('#cluster_id').val() || (typeof cluster_id !== 'undefined' ? cluster_id : '1');

    // Try multiple ways to find CSRF token
    var csrfToken = $('input[name=csrfmiddlewaretoken]').val() ||
                   $('input[name="csrfmiddlewaretoken"]').val() ||
                   $('[name=csrfmiddlewaretoken]').val() ||
                   $('meta[name=csrf-token]').attr('content') ||
                   window.csrfToken ||
                   $.cookie('csrftoken');

    console.log('=== TOPIC MATCHES DEBUG ===');
    console.log('Pattern:', pattern);
    console.log('Cluster ID:', clusterIdVal);
    console.log('CSRF Token:', csrfToken);
    console.log('CSRF elements found:', $('input[name=csrfmiddlewaretoken]').length);
    console.log('All CSRF inputs:', $('input[name*="csrf"]').toArray());
    console.log('All meta tokens:', $('meta[name*="csrf"]').toArray());

    // Data to be sent to server
    var requestData = {
        cluster_id: clusterIdVal,
        pattern: pattern,
        csrfmiddlewaretoken: csrfToken
    };

    console.log('AJAX Request Data:', JSON.stringify(requestData));

    $.ajax({
        url: '/zato/pubsub/topic/get-matches/',
        type: 'POST',
        data: requestData,
        beforeSend: function(xhr) {
            console.log('AJAX sending request to:', this.url);
            console.log('AJAX request data (before send):', JSON.stringify(this.data));
        },
        success: function(response) {
            console.log('AJAX Success Response:', response);
            var contentHtml = '';

            if (response.matches && response.matches.length > 0) {
                contentHtml = '<div style="margin-bottom: 6px; font-weight: bold; color: #2c5aa0; font-size: 10px; background-color: #f0f0f0;">Found ' + response.matches.length + ' match' + (response.matches.length === 1 ? '' : 'es') + ':</div>';
                contentHtml += '<div style="max-height: 250px; overflow-y: auto; background-color: #f0f0f0; padding: 5px;">';

                response.matches.forEach(function(topic, index) {
                    if (index > 0) contentHtml += '<div style="border-top: 1px solid #eee; margin: 4px 0;"></div>';
                    contentHtml += '<div style="padding: 2px 0;">';
                    contentHtml += '<div style="font-weight: bold; color: #333; font-size: 12px;">' + topic.name + '</div>';
                    if (topic.description) {
                        contentHtml += '<div style="color: #666; font-size: 11px; margin-top: 1px;">' + topic.description + '</div>';
                    }
                    contentHtml += '</div>';
                });

                contentHtml += '</div>';
            } else {
                contentHtml = '<div style="text-align: center; padding: 8px; color: #666; font-size: 10px; background-color: #f0f0f0;">';
                contentHtml += 'No matches found';
                contentHtml += '</div>';
            }

            $('#' + popupId + '-content').html(contentHtml);
        },
        error: function(xhr, status, error) {
            console.error('AJAX Error:', {
                status: status,
                error: error,
                responseText: xhr.responseText,
                statusCode: xhr.status
            });

            var errorHtml = '<div style="text-align: center; padding: 8px; color: #d32f2f; font-size: 10px; background-color: #f0f0f0;">';
            errorHtml += 'Error: ' + (error || 'Failed to load');
            if (xhr.status) {
                errorHtml += ' (' + xhr.status + ')';
            }
            errorHtml += '</div>';

            $('#' + popupId + '-content').html(errorHtml);
        }
    });
}

// Function to close the topics popup
function closeTopicMatchesOverlay() {
    // Close all topic match popups
    $('[id^="topic-matches-popup-"]').each(function() {
        if ($(this).hasClass('ui-dialog-content')) {
            $(this).dialog('close');
        }
    });
}

// Function to render pattern tables
function renderPatternTables() {
    console.log('=== PATTERN TABLE DEBUG: Starting renderPatternTables ===');
    console.log('Found pattern-display elements:', $('.pattern-display').length);

    $('.pattern-display').each(function(index) {
        var $container = $(this);
        var patterns = $container.data('patterns');

        console.log('=== PATTERN DEBUG [' + index + '] ===');
        console.log('Container element:', $container[0]);
        console.log('Raw patterns data:', patterns);
        console.log('Patterns type:', typeof patterns);
        console.log('Patterns length:', patterns ? patterns.length : 'N/A');
        console.log('Container HTML before:', $container.html());

        if (!patterns || patterns.trim() === '') {
            console.log('No patterns found, showing empty message');
            $container.html('<em>No patterns</em>');
            return;
        }

        // Decode Unicode escape sequences from Django's escapejs filter
        patterns = patterns.replace(/\\u([0-9a-fA-F]{4})/g, function(match, code) {
            return String.fromCharCode(parseInt(code, 16));
        });


        var patternLines = patterns.split('\n').filter(function(line) {
            return line.trim() !== '';
        });

        console.log('Pattern lines after split and filter:', patternLines);
        console.log('Pattern lines count:', patternLines.length);

        if (patternLines.length === 0) {
            console.log('No pattern lines after filtering');
            $container.html('<em>No patterns</em>');
            return;
        }

        var tableHtml = '<div class="pattern-display-container">';

        patternLines.forEach(function(patternLine) {
            var type, value, typeClass;

            if (patternLine.startsWith('pub=')) {
                type = 'Pub';
                value = patternLine.substring(4);
                typeClass = 'pattern-type-pub';
            } else if (patternLine.startsWith('sub=')) {
                type = 'Sub';
                value = patternLine.substring(4);
                typeClass = 'pattern-type-sub';
            } else {
                type = '?';
                value = patternLine;
                typeClass = 'pattern-type-unknown';
            }

            tableHtml += '<div class="pattern-row">';
            tableHtml += '<div class="pattern-type ' + typeClass + '">' + type + '</div>';
            tableHtml += '<div class="pattern-value">' + value + '</div>';
            tableHtml += '<div class="pattern-link-cell">';
            tableHtml += '<a href="javascript:void(0)" class="pattern-link" data-pattern="' + patternLine.replace(/"/g, '&quot;') + '">Show matches</a>';
            tableHtml += '</div>';
            tableHtml += '</div>';
        });

        tableHtml += '</div>';

        $container.html(tableHtml);

    });

}

// Initialize custom inline editing for pattern values
function initializePatternEditing() {
    $('.pattern-editable').off('click.patternEdit').on('click.patternEdit', function(e) {
        e.preventDefault();
        var $link = $(this);
        var currentValue = $link.data('value');
        var clientId = $link.data('pk');
        var prefix = $link.data('prefix');
        var original = $link.data('original');

        // Don't edit if already editing
        if ($link.hasClass('editing')) {
            return;
        }

        // Create input element
        var $input = $('<input type="text" class="pattern-edit-input">');
        $input.val(currentValue);

        // Replace link with input
        $link.addClass('editing').hide();
        $link.after($input);
        $input.focus().select();

        // Handle save on Enter or blur
        function saveEdit() {
            var newValue = $input.val().trim();

            if (newValue === currentValue) {
                // No change, just restore
                $input.remove();
                $link.removeClass('editing').show();
                return;
            }

            if (!newValue) {
                alert('Pattern value cannot be empty');
                $input.focus();
                return;
            }

            // Save via AJAX
            $.ajax({
                url: '/zato/pubsub/client/update-pattern/',
                type: 'POST',
                data: {
                    pk: clientId,
                    name: 'pattern_value',
                    value: newValue,
                    prefix: prefix,
                    original: original,
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val() || $('meta[name=csrf-token]').attr('content')
                },
                success: function(response) {
                    if (response.status === 'success') {
                        // Update the link with new value
                        var newPattern = prefix + newValue;
                        $link.text(newValue).data('value', newValue).data('original', newPattern);

                        // Update the "Show matches" link
                        var $showLink = $link.closest('.pattern-row').find('.pattern-link');
                        $showLink.attr('data-pattern', newPattern);

                        console.log('Pattern updated successfully:', newPattern);
                    } else {
                        alert('Failed to update pattern: ' + (response.message || 'Unknown error'));
                    }

                    // Restore link
                    $input.remove();
                    $link.removeClass('editing').show();
                },
                error: function(xhr, status, error) {
                    console.error('Error updating pattern:', error);
                    alert('Failed to update pattern: ' + error);

                    // Restore link
                    $input.remove();
                    $link.removeClass('editing').show();
                }
            });
        }

        // Handle cancel on Escape
        function cancelEdit() {
            $input.remove();
            $link.removeClass('editing').show();
        }

        // Bind events
        $input.on('keydown', function(e) {
            if (e.keyCode === 13) { // Enter
                e.preventDefault();
                saveEdit();
            } else if (e.keyCode === 27) { // Escape
                e.preventDefault();
                cancelEdit();
            }
        });

        $input.on('blur', function() {
            // Small delay to allow for other events
            setTimeout(saveEdit, 100);
        });
    });
}

$(document).ready(function() {
    console.log('=== PUBSUB CLIENT DEBUG: Document ready ===');
    console.log('Table HTML:', $('#data-table').html());
    console.log('Table rows count:', $('#data-table tbody tr').length);

    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubClient;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.client.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['sec_base_id', 'access_type']);

    // Call the render function after the page loads
    console.log('=== CALLING renderPatternTables ===');
    renderPatternTables();
    console.log('=== PUBSUB CLIENT DEBUG: Setup complete ===');

    // Setup form submission handlers for pattern consolidation (using event delegation)
    $(document).on('submit', '#create-form', function(e) {
        console.log('=== FORM SUBMIT DEBUG: Create form submit triggered ===');
        console.log('Form data before consolidation:', $(this).serialize());
        consolidatePatterns('create');
        console.log('Form data after consolidation:', $(this).serialize());
        console.log('Pattern hidden field value:', $('#create-pattern-hidden').val());
    });
    $(document).on('submit', '#edit-form', function(e) {
        console.log('=== FORM SUBMIT DEBUG: Edit form submit triggered ===');
        console.log('Form data before consolidation:', $(this).serialize());
        consolidatePatterns('edit');
        console.log('Form data after consolidation:', $(this).serialize());
        console.log('Pattern hidden field value:', $('#edit-pattern-hidden').val());
    });

    // Add event handlers for access type change (both create and edit forms) using event delegation
    $(document).on('change', '#id_access_type', function() {
        console.log('=== ACCESS TYPE DEBUG: Create access type changed to:', $(this).val());
        updatePatternTypeOptions('create');
    });
    $(document).on('change', '#id_edit-access_type', function() {
        console.log('=== ACCESS TYPE DEBUG: Edit access type changed to:', $(this).val());
        updatePatternTypeOptions('edit');
    });

    // Use event delegation for pattern link clicks instead of inline onclick
    $(document).on('click', '.pattern-link', function(event) {
        var pattern = $(this).data('pattern');
        showTopicsAlert(pattern, event);
    });

    console.log('=== PUBSUB CLIENT DEBUG: Event handlers attached ===');

    // Set up before_submit_hook to consolidate patterns before form submission
    $.fn.zato.data_table.before_submit_hook = function(form) {
        console.log('=== BEFORE SUBMIT HOOK: Called with form:', form.attr('id'));
        var formId = form.attr('id');
        if (formId === 'create-form') {
            console.log('=== BEFORE SUBMIT HOOK: Consolidating patterns for create ===');
            consolidatePatterns('create');
        } else if (formId === 'edit-form') {
            console.log('=== BEFORE SUBMIT HOOK: Consolidating patterns for edit ===');
            consolidatePatterns('edit');
        }
        console.log('=== BEFORE SUBMIT HOOK: Form data after consolidation:', form.serialize());
        return true; // Allow form submission to continue
    };
})

$.fn.zato.pubsub.client.create = function() {
    console.log('=== CREATE DEBUG: Create function called ===');
    $.fn.zato.data_table._create_edit('create', 'Create a new API client', null);
    console.log('=== CREATE DEBUG: _create_edit called ===');

    // Function to populate security definitions and initialize form
    function initializeCreateForm() {
        console.log('=== CREATE DEBUG: Populating security definitions and initializing pattern options ===');
        populateSecurityDefinitions('create');
        updatePatternTypeOptions('create');
    }

    // Always populate security definitions via AJAX when select element becomes available
    // Use a timeout to ensure the DOM is ready, then always make fresh AJAX call
    setTimeout(function() {
        var selectElement = $('#id_sec_base_id');
        if (selectElement.length > 0) {
            console.log('=== CREATE DEBUG: Select element found, initializing form ===');
            initializeCreateForm();
        } else {
            // Use MutationObserver to watch for the element if not immediately available
            var observer = new MutationObserver(function(mutations) {
                var selectElement = $('#id_sec_base_id');
                if (selectElement.length > 0) {
                    console.log('=== CREATE DEBUG: Select element found via observer, initializing form ===');
                    initializeCreateForm();
                    observer.disconnect();
                }
            });
            observer.observe(document.body, { childList: true, subtree: true });
        }
    }, 100);
}

$.fn.zato.pubsub.client.edit = function(id) {
    console.log('=== EDIT DEBUG: Function called with id:', id);
    console.log('=== EDIT DEBUG: Data table keys:', Object.keys($.fn.zato.data_table.data));
    console.log('=== EDIT DEBUG: Data table entry for id ' + id + ':', $.fn.zato.data_table.data[id]);
    console.log('=== EDIT DEBUG: Stack trace:', new Error().stack);

    var instance = $.fn.zato.data_table.data[id];
    console.log('=== EDIT DEBUG: Instance retrieved:', instance);

    if (instance === null) {
        console.log('=== EDIT DEBUG: Instance is null - this should not happen!');
        console.log('=== EDIT DEBUG: All data table entries:', $.fn.zato.data_table.data);
        return;
    }

    if (instance === undefined) {
        console.log('=== EDIT DEBUG: Instance is undefined - ID not found in data table');
        console.log('=== EDIT DEBUG: All data table entries:', $.fn.zato.data_table.data);
        return;
    }

    $.fn.zato.data_table._create_edit('edit', 'Update the API client', id);

    $.fn.zato.data_table.reset_form('edit');
    $('#edit-id').val(instance.id);
    $('#edit-access_type').val(instance.access_type);

    // Get pattern data from the hidden cell that contains the raw patterns
    // This cell was created in new_row function with the raw pattern data
    var $row = $('#tr_' + id);
    var patternData = $row.find('td:eq(8)').text();
    console.log('=== EDIT DEBUG: Pattern data from hidden cell:', patternData);

    // If no data found in hidden cell, try to get it from data-patterns attribute
    if (!patternData || patternData.trim() === '') {
        patternData = $row.find('.pattern-display').attr('data-patterns');
        console.log('=== EDIT DEBUG: Pattern data from data-patterns attribute:', patternData);
    }

    // If still no data, try instance.pattern as last resort
    if (!patternData || patternData.trim() === '') {
        patternData = instance.pattern;
        console.log('=== EDIT DEBUG: Pattern data from instance:', patternData);
    }

    // Decode any HTML entities in the pattern data
    if (patternData) {
        patternData = patternData.replace(/\\u003D/g, '=');
        patternData = patternData.replace(/\\u000A/g, '\n');
        console.log('=== EDIT DEBUG: Final decoded patterns:', patternData);
    }

    // Populate patterns
    populatePatterns('edit', patternData);

    // Function to populate security definitions and initialize form
    function initializeEditForm() {
        console.log('=== EDIT DEBUG: Populating security definitions and initializing pattern options ===');
        populateSecurityDefinitions('edit', instance.sec_base_id);
        updatePatternTypeOptions('edit');
    }

    // Always populate security definitions via AJAX when select element becomes available
    var selectElement = $('#id_edit-sec_base_id');
    if (selectElement.length > 0) {
        console.log('=== EDIT DEBUG: Select element found, initializing form ===');
        initializeEditForm();
    } else {
        // Wait for the select element to be added to the DOM
        var observer = new MutationObserver(function(mutations) {
            var selectElement = $('#id_edit-sec_base_id');
            if (selectElement.length > 0) {
                console.log('=== EDIT DEBUG: Select element found via observer, initializing form ===');
                initializeEditForm();
                observer.disconnect();
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    // Add extensive debugging for access type changes
    setTimeout(function() {
        var accessTypeSelect = $('#edit-access_type');
        if (accessTypeSelect.length > 0) {
            console.log('=== ACCESS TYPE DEBUG: Adding change listener to edit access type select');
            accessTypeSelect.off('change.debug').on('change.debug', function() {
                console.log('=== ACCESS TYPE CHANGE DEBUG: Event triggered ===');
                console.log('=== ACCESS TYPE DEBUG: New value:', $(this).val());
                console.log('=== ACCESS TYPE DEBUG: Previous value:', $(this).data('prev-value'));

                // Log all form fields before and after
                console.log('=== FORM FIELDS BEFORE ACCESS TYPE CHANGE:');
                logAllFormFields('edit');

                // Store new value for next comparison
                $(this).data('prev-value', $(this).val());

                // Log again after a short delay to catch any changes
                setTimeout(function() {
                    console.log('=== FORM FIELDS AFTER ACCESS TYPE CHANGE:');
                    logAllFormFields('edit');
                }, 100);
            });

            // Store initial value
            accessTypeSelect.data('prev-value', accessTypeSelect.val());
        }
    }, 500);
}

// Function to log all form fields
function logAllFormFields(prefix) {
    var form = $('#' + prefix + '-form');
    if (form.length === 0) {
        console.log('=== FORM DEBUG: Form not found with prefix:', prefix);
        return;
    }

    console.log('=== FORM DEBUG: All form fields for prefix "' + prefix + '":');

    // Log all input fields
    form.find('input').each(function() {
        var $input = $(this);
        console.log('  Input [' + ($input.attr('name') || 'no-name') + '] type=' + $input.attr('type') + ' value="' + $input.val() + '" id=' + ($input.attr('id') || 'no-id'));
    });

    // Log all select fields
    form.find('select').each(function() {
        var $select = $(this);
        console.log('  Select [' + ($select.attr('name') || 'no-name') + '] value="' + $select.val() + '" id=' + ($select.attr('id') || 'no-id') + ' options=' + $select.find('option').length);
    });

    // Log all textarea fields
    form.find('textarea').each(function() {
        var $textarea = $(this);
        console.log('  Textarea [' + ($textarea.attr('name') || 'no-name') + '] value="' + $textarea.val() + '" id=' + ($textarea.attr('id') || 'no-id'));
    });

    // Log pattern container specifically
    var patternContainer = $('#' + prefix + '-pattern-container');
    if (patternContainer.length > 0) {
        console.log('  Pattern container rows:', patternContainer.find('.pattern-row').length);
        patternContainer.find('.pattern-row').each(function(index) {
            var $row = $(this);
            var typeSelect = $row.find('select[name$="_type_' + index + '"]');
            var valueInput = $row.find('input[name$="_' + index + '"]');
            console.log('    Pattern row ' + index + ': type="' + (typeSelect.val() || 'empty') + '" value="' + (valueInput.val() || 'empty') + '"');
        });
    }

    // Log hidden pattern field
    var hiddenPattern = $('#' + prefix + '-pattern-hidden');
    if (hiddenPattern.length > 0) {
        console.log('  Hidden pattern field value:', hiddenPattern.val());
    }
}

// Add debugging for plus/minus button clicks
$(document).on('click', '.pattern-add-button', function() {
    console.log('=== PLUS BUTTON DEBUG: Add pattern button clicked ===');
    console.log('=== FORM FIELDS BEFORE ADDING PATTERN:');

    // Determine which form we're in
    var form = $(this).closest('form');
    var prefix = 'create';
    if (form.attr('id') === 'edit-form') {
        prefix = 'edit';
    }

    logAllFormFields(prefix);

    // Log after a short delay to catch the new row
    setTimeout(function() {
        console.log('=== FORM FIELDS AFTER ADDING PATTERN:');
        logAllFormFields(prefix);
    }, 100);
});

$(document).on('click', '.pattern-remove-button', function() {
    console.log('=== MINUS BUTTON DEBUG: Remove pattern button clicked ===');
    console.log('=== FORM FIELDS BEFORE REMOVING PATTERN:');

    // Determine which form we're in
    var form = $(this).closest('form');
    var prefix = 'create';
    if (form.attr('id') === 'edit-form') {
        prefix = 'edit';
    }

    logAllFormFields(prefix);

    // Log after a short delay to catch the removal
    setTimeout(function() {
        console.log('=== FORM FIELDS AFTER REMOVING PATTERN:');
        logAllFormFields(prefix);
    }, 100);
});

$.fn.zato.pubsub.client.data_table.new_row = function(item, data, include_tr) {
    console.log('=== NEW_ROW DEBUG: item:', item);
    console.log('=== NEW_ROW DEBUG: data:', data);
    console.log('=== NEW_ROW DEBUG: item.id:', item.id);
    console.log('=== NEW_ROW DEBUG: typeof item.id:', typeof item.id);

    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var access_type_label = '';

    if(item.access_type == 'publisher') {
        access_type_label = 'Publisher';
    } else if(item.access_type == 'subscriber') {
        access_type_label = 'Subscriber';
    } else if(item.access_type == 'publisher-subscriber') {
        access_type_label = 'Publisher & Subscriber';
    }

    var pattern_display = item.pattern ? item.pattern.replace(/\n/g, ', ') : '';

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', pattern_display);
    row += String.format('<td style="text-align:center">{0}</td>', access_type_label);
    row += String.format('<td><a href="javascript:$.fn.zato.pubsub.client.edit(\'{0}\')">Edit</a></td>', item.id);
    row += String.format('<td><a href="javascript:$.fn.zato.pubsub.client.delete_(\'{0}\')">Delete</a></td>', item.id);
    row += String.format('<td style="display:none">{0}</td>', item.id); // id (hidden)
    row += String.format('<td style="display:none">{0}</td>', item.pattern || ''); // _pattern (hidden)
    row += String.format('<td style="display:none">{0}</td>', item.access_type || ''); // _access_type (hidden)
    row += String.format('<td style="display:none">{0}</td>', item.sec_base_id || ''); // sec_base_id (hidden)

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.client.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'API client `{0}` deleted',
        'Are you sure you want to delete API client `{0}`?',
        true);
}

// Multi-pattern UI functions
function addPatternRow(formType) {
    var container = $('#' + formType + '-patterns-container');
    var rowCount = container.find('.pattern-row').length;

    // Get current access type to determine what pattern types are available
    var accessTypeId = formType === 'create' ? '#id_access_type' : '#id_edit-access_type';
    var accessType = $(accessTypeId).val();

    // Build options based on current access type
    var optionsHtml = '';
    var defaultValue = 'pub'; // fallback default

    if (accessType === 'publisher' || accessType === 'publisher-subscriber') {
        optionsHtml += '<option value="pub">Publish</option>';
        defaultValue = 'pub';
    }
    if (accessType === 'subscriber' || accessType === 'publisher-subscriber') {
        optionsHtml += '<option value="sub">Subscribe</option>';
        if (accessType === 'subscriber') {
            defaultValue = 'sub'; // For subscriber-only, default to sub
        }
    }

    var newRow = $('<div class="pattern-row">' +
        '<select name="pattern_type_' + rowCount + '" class="pattern-type-select">' +
        optionsHtml +
        '</select>' +
        '<input type="text" name="pattern_' + rowCount + '" class="pattern-input" style="width:50%" />' +
        '<button type="button" class="pattern-add-button" onclick="addPatternRow(\'' + formType + '\')" style="display:none">+</button>' +
        '<button type="button" class="pattern-remove-button" onclick="removePatternRow(this)">-</button>' +
        '</div>');

    container.append(newRow);

    // Set the default value for the new select
    newRow.find('.pattern-type-select').val(defaultValue);

    // Show remove buttons and hide add buttons except on last row
    container.find('.pattern-row').each(function(index) {
        var isLast = (index === container.find('.pattern-row').length - 1);
        $(this).find('.pattern-add-button').toggle(isLast);
        $(this).find('.pattern-remove-button').toggle(!isLast || container.find('.pattern-row').length > 1);
    });

    // No need to call updatePatternTypeOptions since we created the row with correct options
}

function removePatternRow(button) {
    var row = $(button).closest('.pattern-row');
    var container = row.closest('[id$="-patterns-container"]');

    if (container.find('.pattern-row').length > 1) {
        row.remove();

        // Update button visibility
        container.find('.pattern-row').each(function(index) {
            var isLast = (index === container.find('.pattern-row').length - 1);
            $(this).find('.pattern-add-button').toggle(isLast);
            $(this).find('.pattern-remove-button').toggle(!isLast || container.find('.pattern-row').length > 1);
        });
    }
}

function consolidatePatterns(formType) {
    console.log('=== CONSOLIDATE DEBUG: Starting consolidatePatterns for:', formType);
    var container = $('#' + formType + '-patterns-container');
    console.log('Container found:', container.length > 0);
    var patterns = [];

    container.find('.pattern-row').each(function(index) {
        var patternType = $(this).find('.pattern-type-select').val();
        var patternValue = $(this).find('.pattern-input').val().trim();
        console.log('Row', index, '- Type:', patternType, 'Value:', JSON.stringify(patternValue));
        if (patternValue) {
            var combined = patternType + '=' + patternValue;
            patterns.push(combined);
            console.log('Added pattern:', JSON.stringify(combined));
        }
    });

    var consolidated = patterns.join('\n');
    console.log('Final consolidated patterns:', JSON.stringify(consolidated));
    var hiddenField = $('#' + formType + '-pattern-hidden');
    console.log('Hidden field found:', hiddenField.length > 0);
    hiddenField.val(consolidated);
    console.log('Hidden field value set to:', JSON.stringify(hiddenField.val()));
}

function populatePatterns(formType, patternString) {
    var container = $('#' + formType + '-patterns-container');
    container.empty();

    if (!patternString || patternString.trim() === '') {
        patternString = '';
    }

    var patterns = patternString.split('\n').filter(function(p) { return p.trim() !== ''; });
    if (patterns.length === 0) {
        patterns = [''];
    }

    patterns.forEach(function(pattern, index) {
        var patternType = 'pub';
        var patternValue = pattern.trim();

        // Parse prefixed patterns (pub=pattern or sub=pattern)
        if (patternValue.startsWith('pub=')) {
            patternType = 'pub';
            patternValue = patternValue.substring(4);
        } else if (patternValue.startsWith('sub=')) {
            patternType = 'sub';
            patternValue = patternValue.substring(4);
        }

        var row = $('<div class="pattern-row">' +
            '<select name="pattern_type_' + index + '" class="pattern-type-select">' +
            '<option value="pub"' + (patternType === 'pub' ? ' selected' : '') + '>Publish</option>' +
            '<option value="sub"' + (patternType === 'sub' ? ' selected' : '') + '>Subscribe</option>' +
            '</select>' +
            '<input type="text" name="pattern_' + index + '" class="pattern-input" style="width:50%" value="' + patternValue + '" />' +
            '<button type="button" class="pattern-add-button" onclick="addPatternRow(\'' + formType + '\')" style="display:none">+</button>' +
            '<button type="button" class="pattern-remove-button" onclick="removePatternRow(this)" style="display:none">-</button>' +
            '</div>');
        container.append(row);
    });

    // Show appropriate buttons
    container.find('.pattern-row').each(function(index) {
        var isLast = (index === container.find('.pattern-row').length - 1);
        $(this).find('.pattern-add-button').toggle(isLast);
        $(this).find('.pattern-remove-button').toggle(!isLast || container.find('.pattern-row').length > 1);
    });

    // Update pattern type options based on access type
    updatePatternTypeOptions(formType);
}

function populateSecurityDefinitions(formType, selectedId) {
    var selectId = formType === 'create' ? '#id_sec_base_id' : '#id_edit-sec_base_id';
    var clusterId = $('#cluster_id').val();
    var select = $(selectId);
    var selectContainer = select.parent();

    console.log('=== AJAX DEBUG: Making request to get security definitions ===');
    console.log('=== AJAX DEBUG: formType:', formType, 'clusterId:', clusterId, 'selectId:', selectId);

    // Show spinner with smooth transition and minimum display time
    var startTime = Date.now();

    // Hide select and clear existing content (prevent overlay if form opened twice)
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
        url: '/zato/pubsub/client/get-security-definitions/',
        type: 'GET',
        data: {
            cluster_id: clusterId,
            form_type: formType
        },
        success: function(response) {
            console.log('=== AJAX DEBUG: Received response:', JSON.stringify(response));
            console.log('=== AJAX DEBUG: Security definitions count:', response.security_definitions ? response.security_definitions.length : 0);
            if (response.security_definitions && response.security_definitions.length > 0) {
                console.log('=== AJAX DEBUG: Security definitions details:', JSON.stringify(response.security_definitions));
            }

            // Re-declare variables for callback scope
            var select = $(selectId);
            var selectContainer = select.parent();
            var spinner = selectContainer.find('.loading-spinner');

            // Ensure minimum display time for smooth UX (prevent flicker)
            var elapsedTime = Date.now() - startTime;
            var minDisplayTime = 300; // 300ms minimum
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
                        console.log('=== AJAX DEBUG: Showing select dropdown with', response.security_definitions.length, 'definitions');

                        // Populate select with available security definitions
                        $.each(response.security_definitions, function(index, item) {
                            var option = $('<option></option>')
                                .attr('value', item.id)
                                .text(item.name);
                            if (selectedId && item.id == selectedId) {
                                option.attr('selected', 'selected');
                            } else if (index === 0 && !selectedId) {
                                option.attr('selected', 'selected');
                            }
                            select.append(option);
                        });

                        // Show the select dropdown with smooth transition
                        select.show().removeClass('hide').addClass('security-select');

                        // Enable OK button since we have security definitions
                        var okButton = select.closest('form').find('input[type="submit"]');
                        okButton.prop('disabled', false);
                    } else {
                        // No security definitions available - show appropriate message
                        var hasExistingClients = $.fn.zato.data_table.data && Object.keys($.fn.zato.data_table.data).length > 0;
                        var message = hasExistingClients ? 'No security definitions left' : 'No security definitions available';

                        // Add message with link
                        var messageElement = $('<span class="no-security-definitions-message" style="font-style: italic; color: #666;">' + message + ' - <a href="/zato/security/basic-auth/?cluster=1" target="_blank">Click to create one</a></span>');
                        selectContainer.append(messageElement);

                        // Disable OK button to prevent form submission
                        var okButton = select.closest('form').find('input[type="submit"]');
                        okButton.prop('disabled', true);
                    }
                }, 300); // Wait for fade-out transition
            }, remainingTime);
        },
        error: function(xhr, status, error) {
            console.error('Failed to load security definitions:', error);
            // Remove spinner on error
            var select = $(selectId);
            var selectContainer = select.parent();
            selectContainer.find('.loading-spinner').remove();
        }
    });
}

function updatePatternTypeOptions(formType) {
    var accessTypeId = formType === 'create' ? '#id_access_type' : '#id_edit-access_type';
    var accessType = $(accessTypeId).val();
    var container = $('#' + formType + '-patterns-container');

    container.find('.pattern-row').each(function() {
        var select = $(this).find('.pattern-type-select');
        var input = $(this).find('.pattern-input');
        var currentValue = select.val();

        // Check if current value is incompatible with new access type
        var isIncompatible = (currentValue === 'pub' && accessType === 'subscriber') ||
                           (currentValue === 'sub' && accessType === 'publisher');

        if (isIncompatible) {
            // Current value is incompatible - disable the select and input to preserve the pattern
            select.prop('disabled', true);
            input.prop('disabled', true);
            // Don't change the options or value - keep them as-is
        } else {
            // Current value is compatible - ensure it's enabled and rebuild options if needed
            select.prop('disabled', false);
            input.prop('disabled', false);

            // Always rebuild options for compatible patterns to ensure they have the right choices
            select.empty();
            if (accessType === 'publisher' || accessType === 'publisher-subscriber') {
                select.append('<option value="pub">Publish</option>');
            }
            if (accessType === 'subscriber' || accessType === 'publisher-subscriber') {
                select.append('<option value="sub">Subscribe</option>');
            }

            // Set value to current if it exists, otherwise first option
            if (select.find('option[value="' + currentValue + '"]').length > 0) {
                select.val(currentValue);
            } else {
                select.val(select.find('option:first').val());
            }
        }
    });
}
