// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubPermission = new Class({
    toString: function() {
        var s = '<PubSubPermission id:{0} name:{1} pattern:{2} access_type:{3}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.pattern ? this.pattern : '(none)',
                                this.access_type ? this.access_type : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

// Custom delete function to handle row removal from the data table correctly.
$.fn.zato.data_table.delete_item = function(id) {
    var url = '/zato/pubsub/permission/delete/' + id;
    var instance = $.fn.zato.data_table.data[id];
    var msg = 'Are you sure you want to delete permission `' + instance.name + '`?';

    zato.modal.show_dialog(msg, function() {
        $.ajax({
            url: url,
            type: 'POST',
            success: function(data) {
                if (data.result === 'ok') {
                    var table = $('#data-table').dataTable();
                    var row = $('#tr_' + id)[0];
                    if (row) {
                        table.fnDeleteRow(row);
                    }
                    zato.modal.show_info('Permission `' + instance.name + '` has been deleted.');
                } else {
                    zato.modal.show_error(data.error);
                }
            }
        });
    });
};

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
            <div id="${popupId}-content" class="topic-popup-content" style="background-color: #f0f0f0; border-radius: 0; padding: 4px;">
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 80px; padding: 8px; color: #666; background-color: #f0f0f0;">
                    <div style="width: 12px; height: 12px; border: 1px solid #ddd; border-top: 1px solid #666; border-radius: 50%; animation: spin 1s linear infinite;"></div>
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
        height: 'auto',  // Start with auto height, will adjust based on content
        maxHeight: 400,
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

    // Data to be sent to server
    var requestData = {
        cluster_id: clusterIdVal,
        pattern: pattern,
        csrfmiddlewaretoken: csrfToken
    };

    $.ajax({
        url: '/zato/pubsub/topic/get-matches/',
        type: 'POST',
        data: requestData,
        beforeSend: function(xhr) {
        },
        success: function(response) {

            var contentHtml = '';

            if (response.matches && response.matches.length > 0) {
                var matchCount = response.matches.length;

                // Add header showing match count
                contentHtml += '<div class="topic-matches-found-header">Found ' + matchCount + ' match' + (matchCount === 1 ? '' : 'es') + '</div>';

                var minHeight = 40;
                var itemHeight = 50; // Approximate height per item
                var maxHeight = 320; // Max scrollable height
                var calculatedHeight = Math.min(minHeight + (matchCount * itemHeight), maxHeight);
                var needsScrolling = calculatedHeight >= maxHeight;

                var containerClass = needsScrolling ? 'topic-matches-scrollable' : 'topic-matches-container';
                contentHtml += '<div class="' + containerClass + '">';

                response.matches.forEach(function(topic, index) {
                    if (index > 0) contentHtml += '<div class="topic-divider"></div>';
                    contentHtml += '<div class="topic-item">';
                    contentHtml += '<div class="topic-item-name">' + topic.name + '</div>';
                    if (topic.description) {
                        contentHtml += '<div class="topic-item-description">' + topic.description + '</div>';
                    }
                    contentHtml += '</div>';
                });

                contentHtml += '</div>';
            } else {
                contentHtml += '<div class="topic-matches-header topic-matches-no-results">';
                contentHtml += 'No matching topics found';
                contentHtml += '</div>';
            }

            var $content = $('#' + popupId + '-content');

            // Fade out current content
            $content.addClass('topic-popup-fade-out');

            // Wait for fade out, then replace content and fade in
            setTimeout(function() {
                $content.html(contentHtml);
                $content.removeClass('topic-popup-fade-out');
                $content.addClass('topic-popup-fade-in');

                // Trigger fade in
                setTimeout(function() {
                    $content.addClass('topic-popup-visible');
                }, 10);
            }, 150);

            // Ensure shadow doesn't get clipped for all cases
            var $popup = $('#' + popupId);
            $popup.css('overflow', 'visible');
            $popup.parent('.ui-dialog').css('overflow', 'visible');

            var $content = $('#' + popupId + '-content');
            $content.fadeOut(100, function() {
                $content.html(contentHtml).fadeIn(100, function() {

                });
            });

        },
        error: function(xhr, status, error) {
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
    $('.pattern-display').each(function(index) {
        var $container = $(this);
        var patterns = $container.data('patterns');

        if (!patterns || patterns.trim() === '') {
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

        if (patternLines.length === 0) {
            $container.html('<em>No patterns</em>');
            return;
        }

        // Sort patterns - pub first, then sub, and alphabetically within each type
        var sortedPatternLines = sortPatternsByTypeAndValue(patternLines);

        var tableHtml = '<div class="pattern-display-container">';

        sortedPatternLines.forEach(function(patternLine) {
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
        var permissionId = $link.data('pk');
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
                url: '/zato/pubsub/permission/update-pattern/',
                type: 'POST',
                data: {
                    pk: permissionId,
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
                    } else {
                        alert('Failed to update pattern: ' + (response.message || 'Unknown error'));
                    }

                    // Restore link
                    $input.remove();
                    $link.removeClass('editing').show();
                },
                error: function(xhr, status, error) {
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
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubPermission;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.permission.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['sec_base_id', 'access_type']);

    renderPatternTables();

    $(document).on('submit', '#create-form', function(e) {
        consolidatePatterns('#create-pattern-display');
    });
    $(document).on('submit', '#edit-form', function(e) {
        consolidatePatterns('#edit-pattern-display');
    });

    // Access type change handler for both forms
    $(document).on('change', '#id_access_type, #id_edit-access_type', function() {
        // Determine form type from the ID
        var formType = $(this).attr('id').includes('edit') ? 'edit' : 'create';
        updatePatternTypeOptions(formType);
    });

    // Use event delegation for pattern link clicks instead of inline onclick
    $(document).on('click', '.pattern-link', function(event) {
        var pattern = $(this).data('pattern');
        showTopicsAlert(pattern, event);
    });

    // Set up before_submit_hook to consolidate patterns before form submission
    $.fn.zato.data_table.before_submit_hook = function(form) {
        var formId = form.attr('id');
        if (formId === 'create-form') {
            consolidatePatterns('create');
        } else if (formId === 'edit-form') {
            consolidatePatterns('edit');
        }
        return true; // Allow form submission to continue
    };
})

// Helper function to sort patterns by type (pub first, then sub) and alphabetically within each type
function sortPatternsByTypeAndValue(patterns) {
    // Group patterns by type
    var pubPatterns = [];
    var subPatterns = [];
    var otherPatterns = [];

    patterns.forEach(function(pattern) {
        if (pattern.startsWith('pub=')) {
            pubPatterns.push(pattern);
        } else if (pattern.startsWith('sub=')) {
            subPatterns.push(pattern);
        } else {
            otherPatterns.push(pattern);
        }
    });

    // Sort each group alphabetically
    pubPatterns.sort(function(a, b) {
        return a.substring(4).localeCompare(b.substring(4));
    });

    subPatterns.sort(function(a, b) {
        return a.substring(4).localeCompare(b.substring(4));
    });

    otherPatterns.sort();

    // Combine patterns in the desired order
    return [].concat(pubPatterns, subPatterns, otherPatterns);
}

$.fn.zato.pubsub.permission = {};
$.fn.zato.pubsub.permission.data_table = {};

$.fn.zato.pubsub.permission.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new permission', null);

    // Function to populate security definitions and initialize form
    function initializeCreateForm() {
        var selectId = '#id_sec_base_id';
        $.fn.zato.common.security.populateSecurityDefinitions('create', null, '/zato/pubsub/permission/get-security-definitions/', selectId);
        updatePatternTypeOptions('create');
    }

    // Always populate security definitions via AJAX when select element becomes available
    // Use a timeout to ensure the DOM is ready, then always make fresh AJAX call
    setTimeout(function() {
        var selectElement = $('#id_sec_base_id');
        if (selectElement.length > 0) {
            initializeCreateForm();
        } else {
            // Use MutationObserver to watch for the element if not immediately available
            var observer = new MutationObserver(function(mutations) {
                var selectElement = $('#id_sec_base_id');
                if (selectElement.length > 0) {
                    initializeCreateForm();
                    observer.disconnect();
                }
            });
            observer.observe(document.body, { childList: true, subtree: true });
        }
    }, 100);

    // Set callback to re-render pattern tables after successful create
    $.fn.zato.data_table.on_submit_complete_callback = function() {

        renderPatternTables();
    };
}

$.fn.zato.pubsub.permission.edit = function(id) {

    var instance = $.fn.zato.data_table.data[id];

    if (instance === null) {
        return;
    }

    if (instance === undefined) {
        return;
    }

    $.fn.zato.data_table._create_edit('edit', 'Update permission `' + instance.name + '`', id);

    // Hide the form initially to prevent flicker, it will be shown in setTimeout below.
    $('#edit-div').hide();

    $.fn.zato.data_table.reset_form('edit');
    $('#edit-id').val(instance.id);

    // Delay setting the access_type to ensure the form is fully initialized
    setTimeout(function() {
        // Get the access type select element - try all possible selectors
        var $accessTypeSelect = $('#id_edit-access_type');
        if (!$accessTypeSelect.length) {
            $accessTypeSelect = $('#edit-access_type');
        }
        if (!$accessTypeSelect.length) {
            $accessTypeSelect = $('select[name="edit-access_type"]');
        }
        // Fallback to any select in the edit form if all else fails
        if (!$accessTypeSelect.length) {
            $accessTypeSelect = $('#edit-div select').filter(function() {
                return $(this).attr('name') && $(this).attr('name').indexOf('access_type') >= 0;
            });
        }

        if ($accessTypeSelect.length) {
            // Normalize access_type to lowercase for form value matching
            var accessType = instance.access_type;
            if (accessType) {
                accessType = accessType.toLowerCase().trim();

                // Declare option found flag before using it
                var optionFound = false;

                // Special handling for Publisher-subscriber which needs to map to publisher-subscriber
                if (accessType === 'publisher-subscriber' ||
                    accessType === 'publisher & subscriber' ||
                    accessType === 'publisher&subscriber' ||
                    accessType === 'publisher-subscriber') {
                    // Find the publisher-subscriber option
                    $accessTypeSelect.find('option').each(function() {
                        var optionValue = $(this).val().toLowerCase();
                        if (optionValue === 'publisher-subscriber' ||
                            optionValue.indexOf('publisher') >= 0 && optionValue.indexOf('subscriber') >= 0) {
                            $accessTypeSelect.val($(this).val());
                            optionFound = true;
                            return false;
                        }
                    });
                } else {
                    // Standard case - find the matching option and select it
                    $accessTypeSelect.find('option').each(function() {
                        if ($(this).val() === accessType) {
                            $accessTypeSelect.val($(this).val());
                            optionFound = true;
                            return false;
                        }
                    });

                    // If exact match not found, try partial match
                    if (!optionFound) {
                        $accessTypeSelect.find('option').each(function() {
                            if (accessType.indexOf($(this).val()) >= 0 || $(this).val().indexOf(accessType) >= 0) {
                                $accessTypeSelect.val($(this).val());
                                return false;
                            }
                        });
                    }
                }

                // Trigger change event to update dependent UI elements

// Get pattern data from the hidden cell that contains the raw patterns
// This cell was created in new_row function with the raw pattern data
var $row = $('#tr_' + id);
patternData = $row.find('td:eq(9)').text();

// If no data found in hidden cell, try to get it from data-patterns attribute
if (!patternData || patternData.trim() === '') {
patternData = $row.find('.pattern-display').attr('data-patterns');
}

// If still no data, try instance.pattern as last resort
if (!patternData || patternData.trim() === '') {
patternData = instance.pattern;
}
                if (!patternData || patternData.trim() === '') {
                    patternData = instance.pattern;
                }

                // Decode any HTML entities in the pattern data
                if (patternData) {
                    patternData = patternData.replace(/\\u003D/g, '=');
                    patternData = patternData.replace(/\\u000A/g, '\n');
                }

                // Populate patterns
                populatePatterns('edit', patternData);

                // Function to populate security definitions and initialize form
                function initializeEditForm() {
                    var selectId = '#id_edit-sec_base_id';
                    $.fn.zato.common.security.populateSecurityDefinitions('edit', instance.sec_base_id, '/zato/pubsub/permission/get-security-definitions/', selectId);
                    updatePatternTypeOptions('edit');
                }

                // Always populate security definitions via AJAX when select element becomes available
                var selectElement = $('#id_edit-sec_base_id');
                if (selectElement.length > 0) {
                    initializeEditForm();
                } else {
                    // Wait for the select element to be added to the DOM
                    var observer = new MutationObserver(function(mutations) {
                        var selectElement = $('#id_edit-sec_base_id');
                        if (selectElement.length > 0) {
                            initializeEditForm();
                            observer.disconnect();
                        }
                    });
                    observer.observe(document.body, { childList: true, subtree: true });
                }
            }
        }

        // Show the form now that it's populated.
        $('#edit-div').show();

    }, 100);

    // Add extensive debugging for access type changes
    setTimeout(function() {
        var accessTypeSelect = $('#edit-access_type');
        if (accessTypeSelect.length > 0) {

            accessTypeSelect.off('change.debug').on('change.debug', function() {
                // Log all form fields before and after
                logAllFormFields('edit');

                // Store new value for next comparison
                $(this).data('prev-value', $(this).val());

                // Log again after a short delay to catch any changes
                setTimeout(function() {
                    logAllFormFields('edit');
                }, 100);
            });

            // Store initial value
            accessTypeSelect.data('prev-value', accessTypeSelect.val());
        }
    }, 500);

    // Set callback to re-render pattern tables after successful edit
    $.fn.zato.data_table.on_submit_complete_callback = function() {
        renderPatternTables();
    };
}

// Function to log all form fields
function logAllFormFields(prefix) {
    var form = $('#' + prefix + '-form');
    if (form.length === 0) {
        return;
    }

    // Log all input fields
    form.find('input').each(function() {
        var $input = $(this);
    });

    // Log all select fields
    form.find('select').each(function() {
        var $select = $(this);
    });

    // Log all textarea fields
    form.find('textarea').each(function() {
        var $textarea = $(this);
    });

    // Log pattern container specifically
    var patternContainer = $('#' + prefix + '-pattern-container');
    if (patternContainer.length > 0) {
        patternContainer.find('.pattern-row').each(function(index) {
            var $row = $(this);
            var typeSelect = $row.find('select[name$="_type_' + index + '"]');
            var valueInput = $row.find('input[name$="_' + index + '"]');
        });
    }

    // Log hidden pattern field
    var hiddenPattern = $('#' + prefix + '-pattern-hidden');
    if (hiddenPattern.length > 0) {
    }
}

// Add debugging for plus/minus button clicks
$(document).on('click', '.pattern-add-button', function() {

    // Determine which form we're in
    var form = $(this).closest('form');
    var prefix = 'create';
    if (form.attr('id') === 'edit-form') {
        prefix = 'edit';
    }

    logAllFormFields(prefix);

    // Log after a short delay to catch the new row
    setTimeout(function() {
        logAllFormFields(prefix);
    }, 100);
});

$(document).on('click', '.pattern-remove-button', function() {

    // Determine which form we're in
    var form = $(this).closest('form');
    var prefix = 'create';
    if (form.attr('id') === 'edit-form') {
        prefix = 'edit';
    }

    logAllFormFields(prefix);

    // Log after a short delay to catch the removal
    setTimeout(function() {
        logAllFormFields(prefix);
    }, 100);
});

$.fn.zato.pubsub.permission.data_table.new_row = function(item, data, include_tr) {

    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    // Normalize the access_type to lowercase for consistent comparison
    if (item.access_type) {
        item.access_type = item.access_type.toLowerCase();
    }

    var access_type_label = '';

    if(item.access_type == 'publisher') {
        access_type_label = 'Publisher';
    } else if(item.access_type == 'subscriber') {
        access_type_label = 'Subscriber';
    } else if(item.access_type == 'publisher-subscriber') {
        access_type_label = 'Publisher & Subscriber';
    }

    // Create pattern display structure to match initial rendering
    var pattern_display_html = '';
    if (item.pattern) {
        var escaped_pattern = item.pattern.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        pattern_display_html = String.format('<div class="pattern-display" data-patterns="{0}"></div>', escaped_pattern);
    } else {
        pattern_display_html = '<div class="pattern-display" data-patterns=""></div>';
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', pattern_display_html);
    row += String.format('<td style="text-align:center">{0}</td>', access_type_label);
    row += String.format('<td style="display:none" style="text-align:center">{0}</td>', item.subscription_count);
    row += String.format('<td><a href="javascript:$.fn.zato.pubsub.permission.edit(\'{0}\')">Edit</a></td>', item.id);
    row += String.format('<td><a href="javascript:$.fn.zato.pubsub.permission.delete_(\'{0}\')">Delete</a></td>', item.id);
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id); // id (hidden)
    row += String.format('<td style="display:none">{0}</td>', item.pattern); // _pattern (hidden)
    row += String.format('<td style="display:none">{0}</td>', item.access_type); // _access_type (hidden)
    row += String.format('<td style="display:none">{0}</td>', item.sec_base_id); // sec_base_id (hidden)

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.permission.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Permission `{0}` deleted',
        'Are you sure you want to delete permission `{0}`?',
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

    // Create a new row as a separate DOM element with proper styling
    var newRow = $('<div class="pattern-row">' +
        '<select name="pattern_type_' + rowCount + '" class="pattern-type-select">' +
        optionsHtml +
        '</select>' +
        '<input type="text" name="pattern_' + rowCount + '" class="pattern-input" style="width:50%" />' +
        '<button type="button" class="pattern-add-button" onclick="addPatternRow(\'' + formType + '\')" style="display:none">+</button>' +
        '<button type="button" class="pattern-remove-button" onclick="removePatternRow(this)">-</button>' +
        '</div>');

    // Prepend the new row to the top of the container
    container.prepend(newRow);

    // Set the default value for the new select
    newRow.find('.pattern-type-select').val(defaultValue);

    // Show add button on first row, remove buttons on all rows when more than one
    container.find('.pattern-row').each(function(index) {
        var isFirst = (index === 0);
        var hasMultipleRows = container.find('.pattern-row').length > 1;
        $(this).find('.pattern-add-button').toggle(isFirst);
        $(this).find('.pattern-remove-button').toggle(hasMultipleRows);
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
            var isFirst = (index === 0);
            var hasMultipleRows = container.find('.pattern-row').length > 1;
            $(this).find('.pattern-add-button').toggle(isFirst);
            $(this).find('.pattern-remove-button').toggle(hasMultipleRows);
        });
    }
}

function consolidatePatterns(formType) {
    var container = $('#' + formType + '-patterns-container');
    var patterns = [];

    container.find('.pattern-row').each(function() {
        var typeSelect = $(this).find('.pattern-type-select');
        var patternInput = $(this).find('.pattern-input');
        var patternType = typeSelect.val();
        var patternValue = patternInput.val().trim();

        // Include all non-empty patterns, even if they are disabled
        // This ensures all patterns are preserved regardless of current access type
        if (patternValue) {
            patterns.push(patternType + '=' + patternValue);
        }
    });

    // Set the consolidated patterns to the hidden field
    $('#' + formType + '-pattern-hidden').val(patterns.join('\n'));
    return patterns.join('\n');
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
    } else {
        // Sort patterns - pub first, then sub, and alphabetically within each type
        patterns = sortPatternsByTypeAndValue(patterns);
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

    // Show add button on first row, remove buttons on all rows when more than one
    container.find('.pattern-row').each(function(index) {
        var isFirst = (index === 0);
        var hasMultipleRows = container.find('.pattern-row').length > 1;
        $(this).find('.pattern-add-button').toggle(isFirst);
        $(this).find('.pattern-remove-button').toggle(hasMultipleRows);
    });

    // Update pattern type options based on access type
    updatePatternTypeOptions(formType);
}



function updatePatternTypeOptions(formType) {
    var accessTypeId = formType === 'create' ? '#id_access_type' : '#id_edit-access_type';
    var accessType = $(accessTypeId).val();
    var container = $('#' + formType + '-patterns-container');

    container.find('.pattern-row').each(function() {
        var select = $(this).find('.pattern-type-select');
        var input = $(this).find('.pattern-input');
        var currentValue = select.val();
        var patternValue = input.val().trim();

        // Check if current value is incompatible with new access type
        var isIncompatible = false;
        if (accessType !== 'publisher-subscriber') {
            isIncompatible = (currentValue === 'pub' && accessType === 'subscriber') ||
                           (currentValue === 'sub' && accessType === 'publisher');
        }

        // Only disable incompatible fields if they have content
        if (isIncompatible && patternValue !== '') {
            // Current value is incompatible and has content - disable to preserve the pattern
            select.prop('disabled', true);
            input.prop('disabled', true);
            // Don't change the options or value - keep them as-is
        } else {
            // Either compatible or empty - enable and rebuild options
            select.prop('disabled', false);
            input.prop('disabled', false);

            // Rebuild options based on access type
            select.empty();
            if (accessType === 'publisher' || accessType === 'publisher-subscriber') {
                select.append('<option value="pub">Publish</option>');
            }
            if (accessType === 'subscriber' || accessType === 'publisher-subscriber') {
                select.append('<option value="sub">Subscribe</option>');
            }

            // For empty fields, set to a compatible value
            // For non-empty compatible fields, keep current if possible
            if (patternValue === '' || !isIncompatible) {
                if (select.find('option[value="' + currentValue + '"]').length > 0) {
                    select.val(currentValue);
                } else {
                    select.val(select.find('option:first').val());
                }
            }
        }
    });
}
