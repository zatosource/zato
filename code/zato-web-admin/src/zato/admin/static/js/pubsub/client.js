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

$(document).ready(function() {
    console.log('=== PUBSUB CLIENT DEBUG: Document ready ===');
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubClient;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.client.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['sec_base_id', 'access_type']);
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

    // Populate patterns
    populatePatterns('edit', instance.pattern);

    // Populate security definitions via AJAX when select element becomes available
    var selectElement = $('#id_edit-sec_base_id');
    if (selectElement.length > 0 && selectElement.is(':visible')) {
        console.log('=== EDIT DEBUG: Populating security definitions ===');
        populateSecurityDefinitions('edit', instance.sec_base_id);
    } else {
        var observer = new MutationObserver(function(mutations) {
            var selectElement = $('#id_edit-sec_base_id');
            if (selectElement.length > 0 && selectElement.is(':visible')) {
                console.log('=== EDIT DEBUG: Populating security definitions ===');
                populateSecurityDefinitions('edit', instance.sec_base_id);
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
        'API client [{0}] deleted',
        'Are you sure you want to delete API client [{0}]?',
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

    // Clear existing content (select already hidden by CSS)
    selectContainer.find('.no-security-definitions-message').remove();
    selectContainer.find('.loading-spinner').remove();

    // Add spinner
    var spinner = $('<span class="loading-spinner" style="font-style: italic; color: #666;">Loading security definitions...</span>');
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
