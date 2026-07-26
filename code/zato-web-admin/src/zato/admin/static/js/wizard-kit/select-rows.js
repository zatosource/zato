// Wizard kit - select rows.
//
// A select row list is a column of rows, each holding one or more selects
// with a delete link at its end, and an add link under the whole list. Both
// the security definitions a popover micro-form picks and the destinations
// a step body lists are such rows, so they share this code and the
// .wizard-select-* classes of shared/wizard-kit.css.
//
// ---------------------------------------------------------------
// How to use
// ---------------------------------------------------------------
//
// The list itself is whatever element carries .wizard-select-list - a div
// built by a micro-form or one already on the page. A row is appended by
// handing over what goes into it and what to do once it is deleted:
//
//      $.fn.zato.wizard_kit.selectRows.appendRow(list,
//          function(row) { row.appendChild(mySelect); },
//          function() { /* the row is already gone from the DOM */ }
//      );
//
// The add link under the list, for the lists that build their own:
//
//      list.after($.fn.zato.wizard_kit.selectRows.buildAddLink('Add security',
//          function() { ... }));

(function($) {

// ////////////////////////////////////////////////////////////////////////

var kit = $.fn.zato.wizard_kit;
kit.selectRows = {};

// ////////////////////////////////////////////////////////////////////////

kit.selectRows.config = {

    // What the delete link of a row says to a screen reader and on hover
    removeLabel: 'Remove'
};

// ////////////////////////////////////////////////////////////////////////

// Appends one row to a list - buildContent fills it with the caller's own
// controls, the delete link at its end is the kit's. onRemove runs after a
// deleted row is already out of the DOM.
kit.selectRows.appendRow = function(list, buildContent, onRemove) {

    var row = document.createElement('div');
    row.className = 'wizard-select-row';

    // Everything in front of the delete link belongs to the caller
    buildContent(row);

    // The icon itself is drawn by the stylesheet, from the shared close.svg
    var deleteLink = document.createElement('a');
    deleteLink.href = 'javascript:void(0)';
    deleteLink.className = 'wizard-select-delete';
    deleteLink.title = kit.selectRows.config.removeLabel;
    deleteLink.setAttribute('aria-label', kit.selectRows.config.removeLabel);

    deleteLink.addEventListener('click', function() {
        list.removeChild(row);
        onRemove();
    });

    row.appendChild(deleteLink);
    list.appendChild(row);

    var out = row;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The add link that grows a list one row at a time.
kit.selectRows.buildAddLink = function(label, onClick) {

    var link = document.createElement('a');
    link.href = 'javascript:void(0)';
    link.className = 'wizard-select-add';
    link.textContent = label;
    link.addEventListener('click', onClick);

    var out = link;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
