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
// optional unitField, width, placeholder and hint.
//
// A descriptor's keys: title, pages, plus the optional width (a CSS width
// for the popover) and fitContent (a popover no wider than its one field).
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
// when its popover is the whole of the save rather than one answer on a
// page saved later on:
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

    // How wide a popover may grow
    maxWidth: 480,

    // The lowest a number field goes - none of them counts down to nothing
    numberMin: 1,

    // Button labels inside the popovers
    backLabel: 'Back',
    nextLabel: 'Next',
    doneLabel: 'OK',
    cancelLabel: 'Cancel',

    // Whether the last page offers a way out next to the button that accepts it -
    // a wizard's popover is one answer among many on a page that is saved later on,
    // so it has nothing to back out of, while a popover that saves on its own does
    showCancel: false,

    // Whether each label stands in a column of its own to the left of its
    // input, so the fields read as a table of keys and values, rather than
    // above the input the way the wizards have theirs
    labelsLeft: false,

    // The per-field help badge label - the badge is rebuilt with every
    // page render, so one id can serve every micro-form
    helpBadgeLabel: 'How does it work?',

    // Whether the popover carries the How does it work? badge
    showHowItWorks: true,

    // A class of the host's own put on every popover it opens - the place
    // for its overrides of the --micro-form-* tokens of micro-forms.css
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

    // What accepting the last page comes to, once the answers are back in the form -
    // a wizard shows them on its review cards, a page that hosts one popover of its own
    // saves them where they belong instead
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

    // What one field is called where it is edited, the micro-forms being the one
    // place every field of theirs is named. A field no popover holds is named by
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
    // ids the popover inputs take - one text describes a field wherever it is shown.
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

    // Shows the given content element in a popover anchored to the target.
    // This is the one place all the host's popovers come from, so they all
    // close on Escape and on clicks outside, and only one is open at a time.
    forms.showTippy = function(targetElement, contentElement, onHidden) {

        var formsConfig = forms.config;

        forms.close();

        var instance = tippy(targetElement, {
            content: contentElement,
            allowHTML: true,
            trigger: 'manual',
            interactive: true,
            arrow: false,
            animation: 'fade',
            duration: [150, 150],
            placement: 'bottom-start',
            appendTo: document.body,
            theme: formsConfig.theme,
            maxWidth: formsConfig.maxWidth,
            zIndex: 100001,

            onShow: function(tippyInstance) {

                // Escape closes the popover and nothing else - it is caught on the way
                // down, before the dialog a host may sit in gets to close itself on the
                // same key, jQuery UI listening for it on the document and on the dialog ..
                var handleEscape = function(event) {
                    if(event.key === 'Escape') {
                        event.preventDefault();
                        event.stopPropagation();
                        forms.close();
                    }
                };
                tippyInstance.handleEscape = handleEscape;
                document.addEventListener('keydown', handleEscape, true);

                // .. and so does a click anywhere outside of it.
                var handleOutsideMousedown = function(event) {
                    var isInPopper = tippyInstance.popper.contains(event.target);
                    var isOnTarget = targetElement.contains(event.target);
                    if(!isInPopper && !isOnTarget) {
                        forms.close();
                    }
                };
                tippyInstance.handleOutsideMousedown = handleOutsideMousedown;
                document.addEventListener('mousedown', handleOutsideMousedown);
            },

            onHide: function(tippyInstance) {
                document.removeEventListener('keydown', tippyInstance.handleEscape, true);
                document.removeEventListener('mousedown', tippyInstance.handleOutsideMousedown);

                if(onHidden) {
                    onHidden();
                }
            },

            onShown: function(tippyInstance) {

                // The title is the drag handle - the whole popover follows it
                forms._makeDraggable(tippyInstance);

                // The input the popover was opened for takes the cursor,
                // its value left as it stands ..
                var wantedInput = null;

                if(forms._focusInputId) {
                    wantedInput = tippyInstance.popper.querySelector('#' + forms._focusInputId);
                    forms._focusInputId = null;
                }

                if(wantedInput) {
                    wantedInput.focus();
                    return;
                }

                // .. and with no field named, the first input is the one
                // ready for typing.
                var firstInput = tippyInstance.popper.querySelector('input[type="text"], select');
                if(firstInput) {
                    firstInput.focus();
                }
            }
        });

        forms._instance = instance;
        instance.show();

        var out = instance;
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    forms.close = function() {

        if(forms._instance) {
            var instance = forms._instance;
            forms._instance = null;

            // Help mode dies with the popover it explains - otherwise its
            // state would keep pointing at elements about to leave the page
            var helpState = $.fn.zato.how_it_works._state;
            if(helpState && instance.popper.contains(helpState.container)) {
                $.fn.zato.how_it_works._deactivate();
            }

            instance.destroy();
        }
    };

// ////////////////////////////////////////////////////////////////////////

    // Builds a popover header - the shared grip glyph plus the text, acting
    // as the drag handle every micro-form shares. Both the look and the grip
    // come from the shared popup chrome the IDE menus use as well.
    forms.buildTitle = function(text) {

        var title = document.createElement('div');
        title.className = 'zato-popup-header';
        title.appendChild($.fn.zato.popup.build_grip());
        title.appendChild(document.createTextNode(text));

        var out = title;
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // The "How does it work?" badge every popover shows next to its buttons.
    forms.buildHelpBadge = function() {

        var formsConfig = forms.config;

        var badge = document.createElement('span');
        badge.className = 'how-it-works-badge';
        badge.id = formsConfig.helpBadgeId;
        badge.textContent = formsConfig.helpBadgeLabel;

        var out = badge;
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Wires up the help badge of one popover. Tippy attaches the popover to
    // the document only when it shows, so this runs after showTippy and again
    // whenever an open popover re-renders its fields.
    forms.initHelp = function(container) {

        var formsConfig = forms.config;

        if(!formsConfig.showHowItWorks) {
            return;
        }

        if(!container.isConnected) {
            return;
        }

        // A help session left over from the page or from an earlier render
        // of this popover points at elements that just went away
        if($.fn.zato.how_it_works._state) {
            $.fn.zato.how_it_works._deactivate();
        }

        $.fn.zato.how_it_works.init({
            badgeId: formsConfig.helpBadgeId,
            divId: '#' + formsConfig.popupId,
            containerSelector: '.micro-form',
            fieldSelector: '.micro-form-field',

            // Several fields share one row, so a tooltip on the left would
            // cover the neighbor - above the field nothing is in the way
            placement: 'top',
            descriptions: host.helpDescriptions()
        });
    };

// ////////////////////////////////////////////////////////////////////////

    // Lets the popover be dragged around by its header, through the shared
    // popup drag machinery. The offset is applied to the tippy box itself,
    // so tippy's own positioning stays untouched.
    forms._makeDraggable = function(tippyInstance) {

        var handle = tippyInstance.popper.querySelector('.zato-popup-header');
        if(!handle) {
            return;
        }

        var box = tippyInstance.popper.querySelector('.tippy-box');
        var offsetX = 0;
        var offsetY = 0;

        $.fn.zato.popup.install_drag(handle, {

            dragging_elem: tippyInstance.popper.querySelector('.zato-popup'),

            on_start: function() {

                // The stock tippy CSS animates transform changes - the box must
                // follow the pointer instantly instead
                box.style.transitionProperty = 'visibility, opacity';

                return {'x': offsetX, 'y': offsetY};
            },

            on_move: function(x, y) {
                offsetX = x;
                offsetY = y;
                box.style.transform = 'translate(' + x + 'px, ' + y + 'px)';
            }
        });
    };

// ////////////////////////////////////////////////////////////////////////

    // Builds one input row of a micro-form page, seeded from the Django form.
    forms._buildFieldRow = function(fieldSpec) {

        var row = document.createElement('div');
        row.className = 'micro-form-field';

        // The kinds the instance registered come first - e.g. composite
        // rows like MLLP's security list
        var kindHandler = forms._kinds[fieldSpec.kind];
        if(kindHandler) {
            kindHandler.build(fieldSpec, row);

            var out = row;
            return out;
        }

        var formField = host.field(fieldSpec.field);
        var inputId = forms.inputId(fieldSpec.field);

        // A checkbox carries its slider at the end of the line the label
        // takes, so a column of switches lines up whatever the labels say ..
        if(fieldSpec.kind === 'checkbox') {
            var checkboxLabel = document.createElement('label');
            checkboxLabel.className = 'micro-form-checkbox';
            checkboxLabel.setAttribute('for', inputId);

            var checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = inputId;
            checkbox.checked = formField.prop('checked');

            var checkboxText = document.createElement('span');
            checkboxText.className = 'micro-form-checkbox-text';
            checkboxText.textContent = fieldSpec.label;

            checkboxLabel.appendChild(checkboxText);
            checkboxLabel.appendChild(checkbox);
            row.appendChild(checkboxLabel);

            var out = row;
            return out;
        }

        // .. everything else has the label above the input.
        var label = document.createElement('label');
        label.className = 'micro-form-label';
        label.setAttribute('for', inputId);
        label.textContent = fieldSpec.label;
        row.appendChild(label);

        var input;

        if(fieldSpec.kind === 'select') {

            // The choices are cloned from the Django select, the single source of options
            input = document.createElement('select');
            input.id = inputId;

            formField.find('option').each(function() {
                var option = document.createElement('option');
                option.value = this.value;
                option.textContent = this.textContent;
                input.appendChild(option);
            });
            input.value = formField.val();
        }
        else {
            input = document.createElement('input');
            input.id = inputId;
            input.value = formField.val();

            // A count is stepped with the arrows the browser puts on a
            // number field, and it is only ever as wide as a count needs
            if(fieldSpec.kind === 'number') {
                input.type = 'number';
                input.className = 'micro-form-number';
                input.min = forms.config.numberMin;
            }
            else {
                input.type = 'text';
            }

            if(fieldSpec.placeholder) {
                input.placeholder = fieldSpec.placeholder;
            }
        }

        // Fields like max message size keep their unit select right next to the value
        if(fieldSpec.unitField) {
            var inputRow = document.createElement('div');
            inputRow.className = 'micro-form-input-row';
            inputRow.appendChild(input);

            var unitFormField = host.field(fieldSpec.unitField);
            var unitSelect = document.createElement('select');
            unitSelect.id = forms.inputId(fieldSpec.unitField);
            unitSelect.className = 'micro-form-unit';

            unitFormField.find('option').each(function() {
                var unitOption = document.createElement('option');
                unitOption.value = this.value;
                unitOption.textContent = this.textContent;
                unitSelect.appendChild(unitOption);
            });
            unitSelect.value = unitFormField.val();

            inputRow.appendChild(unitSelect);
            row.appendChild(inputRow);
        }
        else {
            row.appendChild(input);
        }

        if(fieldSpec.hint) {
            var hint = document.createElement('div');
            hint.className = 'micro-form-hint';
            hint.textContent = fieldSpec.hint;
            row.appendChild(hint);
        }

        var out = row;
        return out;
    };

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

        if(descriptor.width) {
            container.style.width = descriptor.width;
        }

        // A form of one short field is only as wide as that field
        if(descriptor.fitContent) {
            container.classList.add('micro-form-fit');
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

        forms.showTippy(targetElement, container);
        forms.initHelp(container);
    };

// ////////////////////////////////////////////////////////////////////////

};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
