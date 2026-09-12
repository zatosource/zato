// Micro-forms - the tippy popover a micro-form is shown in, how it closes
// and how it is dragged. Loaded after micro-forms/core.js, which calls
// installPopover from setup.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var microForms = $.fn.zato.micro_forms;

// ////////////////////////////////////////////////////////////////////////

microForms.installPopover = function(host, forms) {

// ////////////////////////////////////////////////////////////////////////

    // Shows the given content element in a popover anchored to the target.
    // This is the one place all the host's popovers come from, so they all
    // close on Escape and on clicks outside, and only one is open at a time.
    forms.showTippy = function(targetElement, contentElement, onHidden, maxWidth) {

        var formsConfig = forms.config;

        forms.close();

        var instance = tippy(targetElement, {
            content: contentElement,
            allowHTML: true,
            trigger: 'manual',

            // Closing is the handlers' below business, a click into a menu one of the
            // popover's controls opened outside of it must not close it
            hideOnClick: false,
            interactive: true,
            arrow: false,
            animation: 'fade',
            duration: [150, 150],
            placement: formsConfig.placement,
            popperOptions: {
                modifiers: [{name: 'flip', options: {fallbackPlacements: formsConfig.flipPlacements}}]
            },
            appendTo: document.body,
            theme: formsConfig.theme,
            maxWidth: maxWidth,
            zIndex: 100001,

            onShow: function(tippyInstance) {

                // Escape closes the popover and nothing else - it is caught on the way
                // down, before the dialog a host may sit in gets to close itself on the
                // same key ..
                var handleEscape = function(event) {
                    if(event.key === 'Escape') {
                        event.preventDefault();
                        event.stopPropagation();
                        forms.close();
                    }
                };
                tippyInstance.handleEscape = handleEscape;
                document.addEventListener('keydown', handleEscape, true);

                // .. and so does a click anywhere outside of it, a menu of its own
                // controls being as good as inside.
                var handleOutsideMousedown = function(event) {
                    var isInPopper = tippyInstance.popper.contains(event.target);
                    var isOnTarget = targetElement.contains(event.target);
                    var isInMenu = event.target.closest(formsConfig.menuSelector) !== null;

                    if(!isInPopper) {
                        if(!isOnTarget) {
                            if(!isInMenu) {
                                forms.close();
                            }
                        }
                    }
                };
                tippyInstance.handleOutsideMousedown = handleOutsideMousedown;

                // Caught on the way down, before an element that stops the event from bubbling
                document.addEventListener('mousedown', handleOutsideMousedown, true);
            },

            onHide: function(tippyInstance) {
                document.removeEventListener('keydown', tippyInstance.handleEscape, true);
                document.removeEventListener('mousedown', tippyInstance.handleOutsideMousedown, true);

                if(onHidden !== null) {
                    onHidden();
                }
            },

            onShown: function(tippyInstance) {

                // The side the popover opened on is its side for good, whatever its content grows into
                var placement = tippyInstance.popperInstance.state.placement;
                tippyInstance.setProps({
                    placement: placement,
                    popperOptions: {modifiers: [{name: 'flip', enabled: false}]}
                });

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

                var movedEvent = new CustomEvent(forms.config.movedEvent);
                document.dispatchEvent(movedEvent);
            }
        });
    };

// ////////////////////////////////////////////////////////////////////////

};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
