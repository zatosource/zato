'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = {};

// ////////////////////////////////////////////////////////////////////////

portal.config = {

    // How long a pointer rests on an element before its tooltip opens, and how long it takes to close
    tipDelay: [350, 0],

    // How far a popover opens from the element it belongs to
    popoverOffset: [0, 6],

    // Labels of the buttons and of the empty values
    okLabel: 'OK',
    cancelLabel: 'Cancel',
    applyLabel: 'Apply',
    clearLabel: 'Clear',
    nextLabel: 'Next',
    yesLabel: 'Yes',
    noLabel: 'No',
    emptyLabel: 'Not set',
    noneLabel: 'None',
    noMatchLabel: 'No matches',
    filterPlaceholder: 'Filter'
};

// ////////////////////////////////////////////////////////////////////////

// Creates an element with the given class and text, either of them may be empty.
portal.create = function(tagName, className, text) {

    var element = document.createElement(tagName);

    if (className) {
        element.className = className;
    }

    if (text) {
        element.textContent = text;
    }

    return element;
};

// ////////////////////////////////////////////////////////////////////////

// Creates a pill of the given tone, which shows the state of something.
portal.createPill = function(text, tone) {

    var pill = portal.create('span', 'pill portal-tone-' + tone, text);
    return pill;
};

// ////////////////////////////////////////////////////////////////////////

// Creates a chip, which is a button when it reacts to a press.
portal.createChip = function(text, isButton) {

    var tagName = isButton ? 'button' : 'span';
    var chip = portal.create(tagName, 'chip', text);

    if (isButton) {
        chip.type = 'button';
    }

    return chip;
};

// ////////////////////////////////////////////////////////////////////////

// Creates a button of the card headers, popovers and wizards.
portal.createButton = function(label, isPrimary, onClick) {

    var className = isPrimary ? 'button-action' : 'button-secondary';

    var button = portal.create('button', className, label);
    button.type = 'button';
    button.addEventListener('click', onClick);

    return button;
};

// ////////////////////////////////////////////////////////////////////////

// Reads the JSON a page embeds in a script element of the given ID.
portal.readData = function(elementId) {

    var element = document.getElementById(elementId);
    var out = JSON.parse(element.textContent);

    return out;
};

// ////////////////////////////////////////////////////////////////////////

window.portal = portal;

// ////////////////////////////////////////////////////////////////////////

})();
