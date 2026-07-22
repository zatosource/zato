// Wizard kit - the popover micro-form engine.
//
// Each micro-form is described by a descriptor - a list of pages, each page
// a list of entries. An entry is either one field spec, shown on its own
// line, or a list of field specs, shown side by side in one row. A field
// spec points at one of the hidden Django form inputs by name, so opening
// a micro-form seeds its inputs from the form and pressing OK writes the
// answers back. Selects clone their choices from the underlying Django
// select, which keeps the wizard and the matching full-page editor on the
// same single list of options.
//
// A spec's keys: field (the Django form field name), label, kind - one of
// text, select, checkbox or a kind the instance registered - plus the
// optional unitField, width, placeholder and hint.
//
// ---------------------------------------------------------------
// How to use
// ---------------------------------------------------------------
//
// The instance hands its namespace over after core.setup ran:
//
//      $.fn.zato.wizard_kit.forms.setup(wizard, {
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
// Field kinds beyond text, select and checkbox come from the instance:
//
//      wizard.forms.registerKind('securityList', {
//          build: function(fieldSpec, row) { ... },
//          save: function(popper, fieldSpec) { ... }
//      });
//
// setup installs on wizard.forms: config, descriptors, registerKind,
// showTippy, close, buildTitle, buildHelpBadge, initHelp, open, plus the
// internal builders the instance's own popovers may reuse.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var kit = $.fn.zato.wizard_kit;
kit.forms = {};

// ////////////////////////////////////////////////////////////////////////

kit.forms.defaults = {

    // The tippy theme all the micro-forms share
    theme: 'wizard',

    // How wide a popover may grow
    maxWidth: 480,

    // Button labels inside the popovers
    backLabel: 'Back',
    nextLabel: 'Next',
    doneLabel: 'OK',

    // The per-field help badge label - the badge is rebuilt with every
    // page render, so one id can serve every micro-form
    helpBadgeLabel: 'How does it work?'
};

// ////////////////////////////////////////////////////////////////////////

kit.forms.setup = function(wizard, config) {

    var forms = wizard.forms;
    var idPrefix = wizard.config.idPrefix;

    forms.config = $.extend({}, kit.forms.defaults, {

        // One popover is open at a time, so one id serves them all
        helpBadgeId: idPrefix + '-popup-how-it-works',
        popupId: idPrefix + '-popup'

    }, config);

    forms.descriptors = config.descriptors ? config.descriptors : {};

    // The currently open popover, if any
    forms._instance = null;

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

    // Shows the given content element in a popover anchored to the target.
    // This is the one place all the wizard's popovers come from, so they all
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

                // Escape closes the popover ..
                var handleEscape = function(event) {
                    if(event.key === 'Escape') {
                        forms.close();
                    }
                };
                tippyInstance.handleEscape = handleEscape;
                document.addEventListener('keydown', handleEscape);

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
                document.removeEventListener('keydown', tippyInstance.handleEscape);
                document.removeEventListener('mousedown', tippyInstance.handleOutsideMousedown);

                if(onHidden) {
                    onHidden();
                }
            },

            onShown: function(tippyInstance) {

                // The title is the drag handle - the whole popover follows it
                forms._makeDraggable(tippyInstance);

                // The first input is ready for typing right away
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
            containerSelector: '.wizard-tippy-form',
            fieldSelector: '.wizard-tippy-field',

            // Several fields share one row, so a tooltip on the left would
            // cover the neighbor - above the field nothing is in the way
            placement: 'top',
            descriptions: wizard.helpDescriptions()
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
        row.className = 'wizard-tippy-field';

        // The kinds the instance registered come first - e.g. composite
        // rows like MLLP's security list
        var kindHandler = forms._kinds[fieldSpec.kind];
        if(kindHandler) {
            kindHandler.build(fieldSpec, row);

            var out = row;
            return out;
        }

        var formField = wizard.field(fieldSpec.field);
        var inputId = forms.inputId(fieldSpec.field);

        // A checkbox carries its slider after the label it acts on ..
        if(fieldSpec.kind === 'checkbox') {
            var checkboxLabel = document.createElement('label');
            checkboxLabel.className = 'wizard-tippy-checkbox';
            checkboxLabel.setAttribute('for', inputId);

            var checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = inputId;
            checkbox.checked = formField.prop('checked');

            checkboxLabel.appendChild(document.createTextNode(fieldSpec.label + ' '));
            checkboxLabel.appendChild(checkbox);
            row.appendChild(checkboxLabel);

            var out = row;
            return out;
        }

        // .. everything else has the label above the input.
        var label = document.createElement('label');
        label.className = 'wizard-tippy-label';
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
            input.type = 'text';
            input.id = inputId;
            input.value = formField.val();

            if(fieldSpec.placeholder) {
                input.placeholder = fieldSpec.placeholder;
            }
        }

        // Fields like max message size keep their unit select right next to the value
        if(fieldSpec.unitField) {
            var inputRow = document.createElement('div');
            inputRow.className = 'wizard-tippy-input-row';
            inputRow.appendChild(input);

            var unitFormField = wizard.field(fieldSpec.unitField);
            var unitSelect = document.createElement('select');
            unitSelect.id = forms.inputId(fieldSpec.unitField);
            unitSelect.className = 'wizard-tippy-unit';

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
            hint.className = 'wizard-tippy-hint';
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
            var formField = wizard.field(fieldSpec.field);

            if(fieldSpec.kind === 'checkbox') {
                formField.prop('checked', input.checked);
            }
            else {
                formField.val(input.value);
            }

            if(fieldSpec.unitField) {
                var unitInput = popper.querySelector('#' + forms.inputId(fieldSpec.unitField));
                wizard.field(fieldSpec.unitField).val(unitInput.value);
            }
        }
    };

// ////////////////////////////////////////////////////////////////////////

    // Opens the named micro-form anchored to the given element.
    forms.open = function(descriptorName, targetElement) {

        var formsConfig = forms.config;
        var descriptor = forms.descriptors[descriptorName];

        var container = document.createElement('div');
        container.className = 'wizard-tippy-form zato-popup';
        container.id = formsConfig.popupId;

        if(descriptor.width) {
            container.style.width = descriptor.width;
        }

        container.appendChild(forms.buildTitle(descriptor.title));

        var pageContainer = document.createElement('div');
        pageContainer.className = 'wizard-tippy-body';
        container.appendChild(pageContainer);

        var pageIndex = 0;

        var renderPage = function() {

            pageContainer.innerHTML = '';
            var page = descriptor.pages[pageIndex];

            for(var entryIdx = 0; entryIdx < page.length; entryIdx++) {
                var entry = page[entryIdx];

                // A list entry is several fields sharing one row ..
                if(Array.isArray(entry)) {
                    var rowContainer = document.createElement('div');
                    rowContainer.className = 'wizard-tippy-row';

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
            buttons.className = 'wizard-tippy-buttons';

            // The per-field help sits to the left of the buttons ..
            buttons.appendChild(forms.buildHelpBadge());

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

            var forwardButton = document.createElement('button');
            forwardButton.type = 'button';
            forwardButton.className = 'action-button';
            forwardButton.textContent = hasMorePages ? formsConfig.nextLabel : formsConfig.doneLabel;

            forwardButton.addEventListener('click', function() {
                forms._savePage(pageContainer, descriptor.pages[pageIndex]);

                if(hasMorePages) {
                    pageIndex++;
                    renderPage();
                }

                // .. and OK writes everything back and closes the popover.
                else {
                    forms.close();
                    wizard.review.refreshSummaries();
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
