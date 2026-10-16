// MCP gateway wizard - the filter over the field list of the Data masking popover.
//
// A filter box above Select all, in the pane of every set. Each word typed is
// to be found in a field's name, a space and an underscore separating words
// alike, and the clear button empties the box. The filter is a function of
// the pane's context from masking-popover.js, and it hands context.filter a
// function of a field's name, or null to show every field.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var popover = wizard.maskingPopover;

var filters = {};

// ////////////////////////////////////////////////////////////////////////

filters.config = {

    icons: {
        search: '<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>',
        clear: '<line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>'
    },

    labels: {
        placeholder: 'Filter fields',
        clear: 'Clear'
    }
};

// ////////////////////////////////////////////////////////////////////////

filters._icon = function(iconName) {

    var icon = document.createElement('span');
    icon.className = 'mcp-masking-filter-icon mcp-masking-filter-icon-' + iconName;
    icon.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.25" ' +
        'stroke-linecap="round" stroke-linejoin="round">' + filters.config.icons[iconName] + '</svg>';

    var out = icon;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The words of a query, each to be found in a field's name.
filters._terms = function(query) {

    var words = query.toLowerCase().replace(/_/g, ' ').split(' ');
    var out = [];

    for(var wordIdx = 0; wordIdx < words.length; wordIdx++) {
        if(words[wordIdx] !== '') {
            out.push(words[wordIdx]);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The predicate of a query, or null when the query has no words.
filters._predicate = function(query) {

    var terms = filters._terms(query);

    if(terms.length === 0) {
        return null;
    }

    var out = function(fieldName) {

        for(var termIdx = 0; termIdx < terms.length; termIdx++) {
            if(fieldName.indexOf(terms[termIdx]) === -1) {
                return false;
            }
        }

        return true;
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

popover.filter = function(context) {

    var labels = filters.config.labels;

    var element = document.createElement('div');
    element.className = 'mcp-masking-search';

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'mcp-masking-search-input';
    input.placeholder = labels.placeholder;
    input.spellcheck = false;
    input.autocomplete = 'off';

    var clear = document.createElement('button');
    clear.type = 'button';
    clear.className = 'mcp-masking-search-clear mcp-masking-plain';
    clear.title = labels.clear;
    clear.appendChild(filters._icon('clear'));

    var searchIcon = filters._icon('search');

    element.appendChild(searchIcon);
    element.appendChild(input);
    element.appendChild(clear);

    context.pane.insertBefore(element, context.control);

    var update = function() {
        element.classList.toggle('mcp-masking-search-filled', input.value !== '');
        context.filter(filters._predicate(input.value));
    };

    // The icon puts the cursor in the input
    searchIcon.addEventListener('click', function() {
        input.focus();
    });

    // Enter stays with the box rather than accepting the popover
    input.addEventListener('keydown', function(event) {
        if(event.key === 'Enter') {
            event.preventDefault();
            event.stopPropagation();
        }
    });

    input.addEventListener('input', update);

    clear.addEventListener('click', function() {
        input.value = '';
        update();
        input.focus();
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
