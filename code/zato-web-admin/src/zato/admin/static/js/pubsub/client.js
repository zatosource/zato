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
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubClient;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pubsub.client.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['sec_base_id', 'access_type']);
    
    // Setup form submission handlers for pattern consolidation
    $('#create-form').on('submit', function() {
        consolidatePatterns('create');
    });
    $('#edit-form').on('submit', function() {
        consolidatePatterns('edit');
    });
})

$.fn.zato.pubsub.client.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new PubSub client assignment', null);
}

$.fn.zato.pubsub.client.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Edit PubSub client assignment', id);
    
    // Populate patterns from existing data
    var row = $('#tr_' + id);
    var patternData = row.find('td.ignore').eq(1).text(); // pattern is second ignore column
    setTimeout(function() {
        populatePatterns('edit', patternData);
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

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pubsub.client.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td[2]', 
        'PubSub client assignment [{0}] deleted',
        'Are you sure you want to delete the PubSub client assignment [{0}]?',
        true);
}

// Multi-pattern UI functions
function addPatternRow(formType) {
    var container = $('#' + formType + '-patterns-container');
    var rowCount = container.find('.pattern-row').length;
    
    var newRow = $('<div class="pattern-row">' +
        '<input type="text" name="pattern_' + rowCount + '" class="pattern-input" style="width:50%" />' +
        '<button type="button" class="pattern-add-btn" onclick="addPatternRow(\'' + formType + '\')" style="display:none">+</button>' +
        '<button type="button" class="pattern-remove-btn" onclick="removePatternRow(this)">-</button>' +
        '</div>');
    
    container.append(newRow);
    
    // Show remove buttons and hide add buttons except on last row
    container.find('.pattern-row').each(function(index) {
        var isLast = (index === container.find('.pattern-row').length - 1);
        $(this).find('.pattern-add-btn').toggle(isLast);
        $(this).find('.pattern-remove-btn').toggle(!isLast || container.find('.pattern-row').length > 1);
    });
}

function removePatternRow(button) {
    var row = $(button).closest('.pattern-row');
    var container = row.closest('[id$="-patterns-container"]');
    
    if (container.find('.pattern-row').length > 1) {
        row.remove();
        
        // Update button visibility
        container.find('.pattern-row').each(function(index) {
            var isLast = (index === container.find('.pattern-row').length - 1);
            $(this).find('.pattern-add-btn').toggle(isLast);
            $(this).find('.pattern-remove-btn').toggle(!isLast || container.find('.pattern-row').length > 1);
        });
    }
}

function consolidatePatterns(formType) {
    var container = $('#' + formType + '-patterns-container');
    var patterns = [];
    
    container.find('.pattern-input').each(function() {
        var value = $(this).val().trim();
        if (value) {
            patterns.push(value);
        }
    });
    
    $('#' + formType + '-pattern-hidden').val(patterns.join('\n'));
}

function populatePatterns(formType, patternString) {
    var container = $('#' + formType + '-patterns-container');
    container.empty();
    
    var patterns = patternString ? patternString.split('\n') : [''];
    
    patterns.forEach(function(pattern, index) {
        var row = $('<div class="pattern-row">' +
            '<input type="text" name="pattern_' + index + '" class="pattern-input" style="width:50%" value="' + pattern.trim() + '" />' +
            '<button type="button" class="pattern-add-btn" onclick="addPatternRow(\'' + formType + '\')" style="display:none">+</button>' +
            '<button type="button" class="pattern-remove-btn" onclick="removePatternRow(this)" style="display:none">-</button>' +
            '</div>');
        container.append(row);
    });
    
    // Show appropriate buttons
    container.find('.pattern-row').each(function(index) {
        var isLast = (index === container.find('.pattern-row').length - 1);
        $(this).find('.pattern-add-btn').toggle(isLast);
        $(this).find('.pattern-remove-btn').toggle(!isLast || container.find('.pattern-row').length > 1);
    });
}
