// Micro-forms - the popover forms of a few fields that open off a link or
// a chip and read and write the hidden inputs of the page's own Django form.
//
// A micro-form is a tippy popover wearing the shared popup chrome - the dark
// draggable header, the sandy body - with its fields under the header and
// a buttons row at the end. Wizards open them off their summary links,
// listing pages off their inline-edit links, dialog tabs off the summary
// links of their decision lines. The look is static/css/shared/micro-forms.css,
// loaded next to shared/popup.css, and a host tunes it through the
// --micro-form-* tokens under the popupClass it passes to setup.
//
// Each micro-form is described by a descriptor - a list of pages, each page
// a list of entries. An entry is either one field spec, shown on its own
// line, or a list of field specs, shown side by side in one row. A field
// spec points at one of the hidden Django form inputs by name, so opening
// a micro-form seeds its inputs from the form and pressing OK writes the
// answers back. Selects clone their choices from the underlying Django
// select, which keeps the popover and the matching full-page editor on the
// same single list of options.
//
// A spec's keys: field (the Django form field name), label, kind - one of
// text, number, select, checkbox or a kind the host registered - plus the
// optional unitField, width, placeholder, hint and labelAbove.
//
// A descriptor's keys: title, pages, plus the optional width (a CSS width
// for the popover) and fitContent (a popover as wide as its content).
//
// A registered kind that styles its own controls puts the class
// micro-form-field-own on the row it builds into. A menu such a kind opens
// outside of the popover is matched by config.menuSelector.
//
// The engine is in four files, loaded in this order: micro-forms/core.js
// (this file - the defaults, setup and the pages), micro-forms/popover.js
// (the tippy popover, its closing and dragging), micro-forms/fields.js
// (the header, the help badge and the field rows) and micro-forms/resize.js
// (the corner grip and the size a form is kept at, next to
// shared/micro-forms-resize.css).
//
// ---------------------------------------------------------------
// How to use
// ---------------------------------------------------------------
//
// The host hands itself over, a wizard after its core.setup ran:
//
//      $.fn.zato.micro_forms.setup(wizard, {
//          popupClass: 'wizard-micro-form',
//          descriptors: {
//              'logging': {
//                  title: 'Logging and errors',
//                  pages: [[
//                      {field: 'logging_level', label: 'Log level', kind: 'select'}
//                  ]]
//              }
//          }
//      });
//
// Field kinds beyond the built-in ones come from the host:
//
//      wizard.forms.registerKind('securityList', {
//          build: function(fieldSpec, row) { ... },
//          save: function(popper, fieldSpec) { ... }
//      });
//
// setup installs on host.forms: config, descriptors, registerKind,
// showTippy, close, buildTitle, buildHelpBadge, initHelp, helpDescriptions,
// inputId, open, plus the internal builders the host's own popovers may reuse.
//
// ---------------------------------------------------------------
// The host contract
// ---------------------------------------------------------------
//
// setup asks its host for config.idPrefix, field(name) returning the jQuery
// input of a Django form field, helpDescriptions() returning the per-input
// help texts, an empty forms object to install into and, unless the host
// says otherwise, a review to refresh - so any page with a few hidden inputs
// can host one of these popovers. A page that is not a wizard hands over
// onDone, what accepting the last page comes to, and turns on showCancel
// when its popover is the whole of the save:
//
//      $.fn.zato.micro_forms.setup(host, {
//          descriptors: {'routing': sharedDescriptor},
//          popupClass: 'schedule-micro-form',
//          showCancel: true,
//          doneLabel: 'Save',
//          onDone: host.save
//      });
//
// The popover's id is idPrefix + '-popup' and each input's id is
// idPrefix + '-tippy-' + field, which is what a host's help descriptions
// are keyed by.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var microForms = $.fn.zato.micro_forms;

// ////////////////////////////////////////////////////////////////////////

microForms.defaults = {

    // The tippy theme all the micro-forms share
    theme: 'micro-form',

    // How wide a popover may grow, and the cap of one sized to its content
    maxWidth: 480,
    fitMaxWidth: 'none',

    // A menu one of the popover's controls opens outside of it
    menuSelector: '.zato-dropdown-menu',

    // Where a popover opens relative to its link, and where it goes when it does not fit there
    placement: 'bottom-start',
    flipPlacements: ['top-start'],

    // The attribute an option of a unit select keeps its plural label in
    unitPluralAttr: 'data-plural',

    // Fired on the document as a popover is dragged
    movedEvent: 'zato:popup-moved',

    // The lowest a number field goes
    numberMin: 1,

    // Button labels inside the popovers
    backLabel: 'Back',
    nextLabel: 'Next',
    doneLabel: 'OK',
    cancelLabel: 'Cancel',

    // Whether the last page offers a way out next to the button that accepts it
    showCancel: false,

    // Whether each label stands in a column of its own to the left of its input
    labelsLeft: false,

    // The per-field help badge label
    helpBadgeLabel: 'How does it work?',

    // Whether the popover carries the How does it work? badge
    showHowItWorks: true,

    // A class of the host's own put on every popover it opens
    popupClass: ''
};

// ////////////////////////////////////////////////////////////////////////

microForms.setup = function(host, config) {

    var forms = host.forms;
    var idPrefix = host.config.idPrefix;

    forms.config = $.extend({}, microForms.defaults, {

        // One popover is open at a time, so one id serves them all
        helpBadgeId: idPrefix + '-popup-how-it-works',
        popupId: idPrefix + '-popup'

    }, config);

    forms.descriptors = config.descriptors ? config.descriptors : {};

    // What accepting the last page comes to, once the answers are back in the form
    forms.onDone = config.onDone ? config.onDone : function() {
        host.review.refreshSummaries();
    };

    // The currently open popover, if any
    forms._instance = null;

    // The input the next popover puts the cursor into, when the caller named one
    forms._focusInputId = null;

    // The field kinds the instance registered on top of the built-in ones
    forms._kinds = {};

// ////////////////////////////////////////////////////////////////////////

    // Adds an instance-specific field kind - build makes the row's DOM,
    // save writes the row's answers back on OK.
    forms.registerKind = function(kindName, kindHandler) {
        forms._kinds[kindName] = kindHandler;
    };

// ////////////////////////////////////////////////////////////////////////

    // The id a micro-form input derives from the field it mirrors
    forms.inputId = function(fieldName) {
        var out = idPrefix + '-tippy-' + fieldName;
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // What one field is called where it is edited. A field no popover holds is named by
    // whoever asks for it instead.
    forms.fieldLabel = function(fieldName) {

        var out = '';

        for(var descriptorName in forms.descriptors) {

            var pages = forms.descriptors[descriptorName].pages;

            for(var pageIdx = 0; pageIdx < pages.length; pageIdx++) {

                var page = pages[pageIdx];

                for(var entryIdx = 0; entryIdx < page.length; entryIdx++) {

                    // An entry is either one field or a row of them shown side by side
                    var entry = page[entryIdx];
                    var specList = entry.length ? entry : [entry];

                    for(var specIdx = 0; specIdx < specList.length; specIdx++) {

                        var spec = specList[specIdx];

                        // A field carrying a unit is edited under one label with it
                        if(spec.field === fieldName || spec.unitField === fieldName) {
                            out = spec.label;
                        }
                    }
                }
            }
        }

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // The help texts a page keeps under its Django field ids, said again under the
    // ids the popover inputs take.
    forms.helpDescriptions = function(shared) {

        var out = $.extend({}, shared);

        for(var key in shared) {
            if(key.indexOf('id_') === 0) {
                out[forms.inputId(key.substring(3))] = shared[key];
            }
        }

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    microForms.installPopover(host, forms);
    microForms.installFields(host, forms);
    microForms.installResize(host, forms);

// ////////////////////////////////////////////////////////////////////////

    // The flat list of field specs on a page - row entries contribute
    // each of their fields.
    forms._pageFieldList = function(page) {

        var out = [];

        for(var entryIdx = 0; entryIdx < page.length; entryIdx++) {
            var entry = page[entryIdx];

            if(Array.isArray(entry)) {
                out = out.concat(entry);
            }
            else {
                out.push(entry);
            }
        }

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Writes the answers of one rendered page back into the Django form.
    forms._savePage = function(popper, page) {

        var pageFields = forms._pageFieldList(page);

        for(var fieldIdx = 0; fieldIdx < pageFields.length; fieldIdx++) {
            var fieldSpec = pageFields[fieldIdx];

            // A registered kind knows how to save itself ..
            var kindHandler = forms._kinds[fieldSpec.kind];
            if(kindHandler) {
                kindHandler.save(popper, fieldSpec);
                continue;
            }

            // .. everything else maps straight onto a form field.
            var input = popper.querySelector('#' + forms.inputId(fieldSpec.field));
            var formField = host.field(fieldSpec.field);

            if(fieldSpec.kind === 'checkbox') {
                formField.prop('checked', input.checked);
            }
            else {
                formField.val(input.value);
            }

            if(fieldSpec.unitField) {
                var unitInput = popper.querySelector('#' + forms.inputId(fieldSpec.unitField));
                host.field(fieldSpec.unitField).val(unitInput.value);
            }
        }
    };

// ////////////////////////////////////////////////////////////////////////

    // Opens the named micro-form anchored to the given element. The optional
    // focusFieldName says which input takes the cursor once the popover is on
    // screen - a page whose every value opens the same popover names the very
    // field that was clicked.
    forms.open = function(descriptorName, targetElement, focusFieldName) {

        var formsConfig = forms.config;
        var descriptor = forms.descriptors[descriptorName];

        forms._focusInputId = focusFieldName ? forms.inputId(focusFieldName) : null;

        var container = document.createElement('div');
        container.className = 'micro-form zato-popup';
        container.id = formsConfig.popupId;

        // The host's own class, which is where it overrides the micro-form
        // tokens - the popover is appended to document.body, so no container
        // of the host's page is above it
        if(formsConfig.popupClass) {
            container.classList.add(formsConfig.popupClass);
        }

        if(formsConfig.labelsLeft) {
            container.classList.add('micro-form-labels-left');
        }

        // A form with a width of its own is exactly that wide ..
        var maxWidth = formsConfig.maxWidth;

        if(descriptor.width) {
            container.style.width = descriptor.width;
            container.style.maxWidth = descriptor.width;
            maxWidth = descriptor.width;
        }

        // .. and a form sized to its content is exactly as wide as that content
        if(descriptor.fitContent) {
            container.classList.add('micro-form-fit');
            maxWidth = formsConfig.fitMaxWidth;
        }

        container.appendChild(forms.buildTitle(descriptor.title));

        var pageContainer = document.createElement('div');
        pageContainer.className = 'micro-form-body';
        container.appendChild(pageContainer);

        var pageIndex = 0;

        // The button the page is answered with, whichever page is on show at the time
        var forwardButton = null;

        // Enter answers the page the way that button does - whoever has just typed the last
        // matcher of a form is done with it and has no reason to reach for the mouse
        container.addEventListener('keydown', function(event) {

            if(event.key !== 'Enter') {
                return;
            }

            // A button answers to Enter on its own, and a multi-line field takes it as text
            var tagName = event.target.tagName;

            if(tagName === 'BUTTON' || tagName === 'TEXTAREA') {
                return;
            }

            event.preventDefault();
            forwardButton.click();
        });

        var renderPage = function() {

            pageContainer.innerHTML = '';
            var page = descriptor.pages[pageIndex];

            for(var entryIdx = 0; entryIdx < page.length; entryIdx++) {
                var entry = page[entryIdx];

                // A list entry is several fields sharing one row ..
                if(Array.isArray(entry)) {
                    var rowContainer = document.createElement('div');
                    rowContainer.className = 'micro-form-row';

                    for(var fieldIdx = 0; fieldIdx < entry.length; fieldIdx++) {
                        var rowField = forms._buildFieldRow(entry[fieldIdx]);
                        if(entry[fieldIdx].width) {
                            rowField.style.flex = '0 0 ' + entry[fieldIdx].width;
                        }
                        rowContainer.appendChild(rowField);
                    }
                    pageContainer.appendChild(rowContainer);
                }

                // .. everything else takes a line of its own.
                else {
                    var fieldRow = forms._buildFieldRow(entry);
                    if(entry.width) {
                        fieldRow.style.width = entry.width;
                    }
                    pageContainer.appendChild(fieldRow);
                }
            }

            var buttons = document.createElement('div');
            buttons.className = 'micro-form-buttons';

            // The per-field help sits to the left of the buttons ..
            if(formsConfig.showHowItWorks) {
                buttons.appendChild(forms.buildHelpBadge());
            }

            // .. multi-page micro-forms navigate with Back and Next ..
            if(pageIndex > 0) {
                var backButton = document.createElement('button');
                backButton.type = 'button';
                backButton.className = 'secondary-button';
                backButton.textContent = formsConfig.backLabel;

                backButton.addEventListener('click', function() {
                    forms._savePage(pageContainer, descriptor.pages[pageIndex]);
                    pageIndex--;
                    renderPage();
                });
                buttons.appendChild(backButton);
            }

            var hasMorePages = pageIndex < descriptor.pages.length - 1;

            // .. a popover that saves by itself lets the reader leave it alone,
            // nothing being written back until the button next to this one is pressed ..
            if(formsConfig.showCancel && !hasMorePages) {
                var cancelButton = document.createElement('button');
                cancelButton.type = 'button';
                cancelButton.className = 'secondary-button';
                cancelButton.textContent = formsConfig.cancelLabel;

                cancelButton.addEventListener('click', function() {
                    forms.close();
                });
                buttons.appendChild(cancelButton);
            }

            forwardButton = document.createElement('button');
            forwardButton.type = 'button';
            forwardButton.className = 'action-button';
            forwardButton.textContent = hasMorePages ? formsConfig.nextLabel : formsConfig.doneLabel;

            forwardButton.addEventListener('click', function() {
                forms._savePage(pageContainer, descriptor.pages[pageIndex]);

                if(hasMorePages) {
                    pageIndex++;
                    renderPage();
                }

                // .. and the last button writes everything back and closes the popover.
                else {
                    forms.close();
                    forms.onDone();
                }
            });
            buttons.appendChild(forwardButton);

            pageContainer.appendChild(buttons);

            // Each render brings a fresh badge, so its help needs rewiring -
            // before the first show the popover is not attached yet and the
            // wiring happens right after showTippy instead
            forms.initHelp(container);
        };

        renderPage();

        // A form left at a size of its own opens at that size, however wide that is
        var sizeKey = forms.sizeKey(descriptorName);

        if(forms.restoreSize(container, sizeKey)) {
            maxWidth = formsConfig.fitMaxWidth;
        }

        var instance = forms.showTippy(targetElement, container, null, maxWidth);
        forms.initHelp(container);
        forms.makeResizable(instance, sizeKey);
    };

// ////////////////////////////////////////////////////////////////////////

};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
