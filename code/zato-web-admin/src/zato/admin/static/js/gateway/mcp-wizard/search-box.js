// MCP gateway wizard - the search box shared by the Data masking popover and
// the filters of the Tools, Skills and Security sections.
//
// The input is as wide as the text it holds, so the count of the results and
// the button clearing the box follow the words typed directly.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var searchBox = wizard.searchBox;

// ////////////////////////////////////////////////////////////////////////

searchBox.config = {
    boxSelector: '.mcp-search-box',
    inputSelector: '.mcp-search-box-input',
    clearSelector: '.mcp-search-box-clear',
    sizerClass: 'mcp-search-box-sizer',
    fitAttribute: 'data-fit'
};

// ////////////////////////////////////////////////////////////////////////

// The sizer takes the width of the value typed, or of the placeholder while there is none, and the input fills it.
searchBox.fit = function(input) {

    var text = input.value === '' ? input.placeholder : input.value;
    input.parentNode.setAttribute(searchBox.config.fitAttribute, text);
};

// ////////////////////////////////////////////////////////////////////////

// Empties the box through an input event, so whatever filters on the box sees the change.
searchBox.clear = function(box) {

    var input = box.querySelector(searchBox.config.inputSelector);

    input.value = '';
    input.dispatchEvent(new Event('input', {bubbles: true}));
    input.focus();
};

// ////////////////////////////////////////////////////////////////////////

searchBox.attach = function(box) {

    var config = searchBox.config;
    var input = box.querySelector(config.inputSelector);
    var clear = box.querySelector(config.clearSelector);

    var sizer = document.createElement('span');
    sizer.className = config.sizerClass;

    input.parentNode.insertBefore(sizer, input);
    sizer.appendChild(input);
    searchBox.fit(input);

    input.addEventListener('input', function() {
        searchBox.fit(input);
    });

    clear.addEventListener('click', function() {
        searchBox.clear(box);
    });

    // The box is wider than its input, and a press anywhere in it outside the input and the button belongs to the input
    box.addEventListener('mousedown', function(event) {

        if(event.target === input || clear.contains(event.target)) {
            return;
        }

        event.preventDefault();
        input.focus();
    });
};

// ////////////////////////////////////////////////////////////////////////

searchBox.init = function() {

    var boxes = document.querySelectorAll(searchBox.config.boxSelector);

    for(var boxIdx = 0; boxIdx < boxes.length; boxIdx++) {
        searchBox.attach(boxes[boxIdx]);
    }
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
