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
    // Populate security definitions via AJAX and initialize pattern type options
    setTimeout(function() {
        console.log('=== CREATE DEBUG: Populating security definitions and initializing pattern options ===');
        populateSecurityDefinitions('create');
        updatePatternTypeOptions('create');
    }, 100);
}

$.fn.zato.pubsub.client.edit = function(id) {
    var instance = $.fn.zato.data_table.data[id];
    $.fn.zato.data_table._create_edit('edit', 'Update the API client', id);

    $.fn.zato.data_table.reset_form('edit');
    $('#edit-id').val(instance.id);
    $('#edit-access_type').val(instance.access_type);

    // Populate patterns
    populatePatterns('edit', instance.pattern);

    // Populate security definitions via AJAX after other fields are set
    setTimeout(function() {
        console.log('=== EDIT DEBUG: Populating security definitions ===');
        populateSecurityDefinitions('edit', instance.sec_base_id);
    }, 100);
}

$.fn.zato.pubsub.client.data_table.new_row = function(item, data, include_tr) {
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

    var newRow = $('<div class="pattern-row">' +
        '<select name="pattern_type_' + rowCount + '" class="pattern-type-select">' +
        '<option value="pub">Publish</option>' +
        '<option value="sub">Subscribe</option>' +
        '</select>' +
        '<input type="text" name="pattern_' + rowCount + '" class="pattern-input" style="width:50%" />' +
        '<button type="button" class="pattern-add-button" onclick="addPatternRow(\'' + formType + '\')" style="display:none">+</button>' +
        '<button type="button" class="pattern-remove-button" onclick="removePatternRow(this)">-</button>' +
        '</div>');

    container.append(newRow);

    // Show remove buttons and hide add buttons except on last row
    container.find('.pattern-row').each(function(index) {
        var isLast = (index === container.find('.pattern-row').length - 1);
        $(this).find('.pattern-add-button').toggle(isLast);
        $(this).find('.pattern-remove-button').toggle(!isLast || container.find('.pattern-row').length > 1);
    });

    // Update pattern type options for the new row
    updatePatternTypeOptions(formType);
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

    $.ajax({
        url: '/zato/pubsub/client/get-security-definitions/',
        type: 'GET',
        data: {
            cluster_id: clusterId
        },
        success: function(response) {
            var select = $(selectId);
            select.empty();

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
        },
        error: function(xhr, status, error) {
            console.error('Failed to load security definitions:', error);
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

        // Clear and rebuild options based on access type
        select.empty();

        if (accessType === 'publisher' || accessType === 'publisher-subscriber') {
            select.append('<option value="pub">Publish</option>');
        }
        if (accessType === 'subscriber' || accessType === 'publisher-subscriber') {
            select.append('<option value="sub">Subscribe</option>');
        }

        if (isIncompatible) {
            // Current value is incompatible - add it as a disabled option to preserve it
            select.append('<option value="' + currentValue + '" disabled>' +
                         (currentValue === 'pub' ? 'Publish' : 'Subscribe') + '</option>');
            select.val(currentValue);
            select.prop('disabled', true);
            input.prop('disabled', true);
        } else {
            // Current value is compatible or we need to set a default
            if (select.find('option[value="' + currentValue + '"]').length > 0) {
                select.val(currentValue);
            } else {
                select.val(select.find('option:first').val());
            }
            select.prop('disabled', false);
            input.prop('disabled', false);
        }
    });
}
