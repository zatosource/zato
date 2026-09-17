// Micro-forms - the tippy popover a micro-form is shown in, how it closes
// and how it is dragged. Loaded after micro-forms/core.js, which calls
// installPopover from setup.
//
// A popover opens under its link, or over it when it does not fit there. A
// floating one - a descriptor saying floating: true - is not anchored to its
// link at all, it opens at the point of the window its descriptor's openAt()
// returns, the top left corner as {left, top}, or in the middle of the window
// without one, and after that where it was last dragged to, which is kept in
// the browser's local storage under a key of the host's popup id and the
// form's name, the way its size is.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var microForms = $.fn.zato.micro_forms;

// ////////////////////////////////////////////////////////////////////////

microForms.popoverConfig = {

    // Where the positions of the floating popovers are kept, one entry per form
    positionPrefix: 'zato.micro-form.position.',

    // How far down the window the top of a floating popover with no point of its
    // own stands the first time, as a share of the window's height - the middle
    // of the window is where a reader looks, and a tall popover still has room
    // to grow down
    centeredTop: 0.18,

    // How a floating popover hangs off the point it opens at - centered on the
    // middle of the window, its top left corner on a point of its own
    centeredPlacement: 'bottom',
    cornerPlacement: 'bottom-start'
};

// ////////////////////////////////////////////////////////////////////////

microForms.installPopover = function(host, forms) {

    var popoverConfig = microForms.popoverConfig;

// ////////////////////////////////////////////////////////////////////////

    // Shows the given content element in a popover anchored to the target.
    // This is the one place all the host's popovers come from, so they all
    // close on Escape and on clicks outside, and only one is open at a time.
    // A popover that does not fit under its link goes over it, and one too tall
    // for either is shifted up, over the link if it comes to that, as far as it
    // takes to stay whole within the window - nothing ever runs off the page.
    // With a positionKey the popover is a floating one, opening where it was last
    // left, at the point openAt() returns, or in the middle of the window, and
    // keeping where it is dragged to.
    forms.showTippy = function(targetElement, contentElement, onHidden, maxWidth, positionKey, openAt) {

        var formsConfig = forms.config;

        forms.close();

        var props = {
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
            popperOptions: {modifiers: forms._popperModifiers(true)},
            appendTo: document.body,
            theme: formsConfig.theme,
            maxWidth: maxWidth,
            zIndex: 100001,

            onShow: function(tippyInstance) {

                // Escape closes the popover and nothing else - it is caught on the way
                // down, before the dialog a host may sit in gets to close itself on the
                // same key ..
                var handleEscape = function(event) {

                    if(event.key !== 'Escape') {
                        return;
                    }

                    // A popover open over this one goes first - the key is its
                    if(forms._isCovered(tippyInstance)) {
                        return;
                    }

                    event.preventDefault();
                    event.stopPropagation();
                    forms.close();
                };
                tippyInstance.handleEscape = handleEscape;
                document.addEventListener('keydown', handleEscape, true);

                // .. and so does a click anywhere outside of it, a menu of its own
                // controls and a popover open over it being as good as inside - a
                // popover under it, the one it opened from, is outside like the rest.
                var handleOutsideMousedown = function(event) {
                    var isInPopper = tippyInstance.popper.contains(event.target);
                    var isOnTarget = targetElement.contains(event.target);
                    var isInMenu = event.target.closest(formsConfig.menuSelector) !== null;
                    var isInPopoverAbove = forms._isInPopoverAbove(tippyInstance, event.target);

                    if(!isInPopper) {
                        if(!isOnTarget) {
                            if(!isInMenu) {
                                if(!isInPopoverAbove) {
                                    forms.close();
                                }
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

                // The side the popover opened on is its side for good, whatever its content
                // grows into - the shift keeping it within the window stays with it, or the
                // popover would jump back to where it did not fit
                var placement = tippyInstance.popperInstance.state.placement;
                tippyInstance.setProps({
                    placement: placement,
                    popperOptions: {modifiers: forms._popperModifiers(false)}
                });

                // The title is the drag handle - the whole popover follows it
                forms._makeDraggable(tippyInstance, positionKey);

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
        };

        // A floating popover hangs off a point of the window rather than off its link -
        // the corner it was last dragged to, else the corner its host names, else the
        // middle of the window - and it never flips, the point being exactly where it belongs
        if(positionKey !== null) {

            var position = forms.loadPosition(positionKey);

            if(position === null) {
                if(openAt !== null) {
                    position = openAt();
                }
            }

            var referenceRect;

            if(position === null) {
                var centerLeft = window.innerWidth / 2;
                var centerTop = window.innerHeight * popoverConfig.centeredTop;

                referenceRect = forms._pointRect(centerLeft, centerTop);
                props.placement = popoverConfig.centeredPlacement;
            }
            else {
                referenceRect = forms._pointRect(position.left, position.top);
                props.placement = popoverConfig.cornerPlacement;
            }

            props.getReferenceClientRect = function() {
                return referenceRect;
            };

            props.popperOptions = {modifiers: forms._popperModifiers(false)};
        }

        var instance = tippy(targetElement, props);

        forms._instance = instance;
        instance.show();

        var out = instance;
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // A point of the window as the rectangle popper positions against
    forms._pointRect = function(left, top) {

        var out = {
            width: 0,
            height: 0,
            top: top,
            bottom: top,
            left: left,
            right: left,
            x: left,
            y: top
        };

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // The storage key of a floating form's position
    forms.positionKey = function(descriptorName) {
        var out = popoverConfig.positionPrefix + forms.config.popupId + '.' + descriptorName;
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Where a floating form was last dragged to, its top left corner in the window,
    // or null when it was never moved. The browser is free to refuse the storage
    // altogether, in which case the form opens in the middle of the window.
    forms.loadPosition = function(positionKey) {

        var stored = null;

        try {
            stored = window.localStorage.getItem(positionKey);
        }
        catch(storageError) {
            return null;
        }

        if(stored === null) {
            return null;
        }

        var out = JSON.parse(stored);
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    forms.savePosition = function(positionKey, box) {

        var rect = box.getBoundingClientRect();

        var position = {
            left: rect.left,
            top: rect.top
        };

        try {
            window.localStorage.setItem(positionKey, JSON.stringify(position));
        }
        catch(storageError) {
            return;
        }
    };

// ////////////////////////////////////////////////////////////////////////

    // How popper places a popover - flipping to the other side while it may still
    // pick a side, and shifting along both axes, off its link if it comes to that,
    // to keep the popover whole within the window
    forms._popperModifiers = function(flipEnabled) {

        var formsConfig = forms.config;

        var out = [
            {name: 'flip', enabled: flipEnabled, options: {fallbackPlacements: formsConfig.flipPlacements}},
            {name: 'preventOverflow', options: {padding: formsConfig.viewportPadding, altAxis: true, tether: false}}
        ];

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Whether an element stands in a popover that opened over this one - popovers
    // join the page in the order they open, so such a popover follows this one on it
    forms._isInPopoverAbove = function(tippyInstance, element) {

        var popover = element.closest(forms.config.popoverSelector);

        if(popover === null) {
            return false;
        }

        var position = tippyInstance.popper.compareDocumentPosition(popover);

        var out = (position & Node.DOCUMENT_POSITION_FOLLOWING) !== 0;
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Whether another popover opened over this one - popovers join the page in the
    // order they open, so the one to open last is the last one on it
    forms._isCovered = function(tippyInstance) {

        var popovers = document.querySelectorAll(forms.config.popoverSelector);
        var lastPopover = popovers[popovers.length - 1];

        var out = !tippyInstance.popper.contains(lastPopover);
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
    // so tippy's own positioning stays untouched. A floating popover, one
    // with a positionKey, keeps where it is let go, to open there next time.
    forms._makeDraggable = function(tippyInstance, positionKey) {

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
            },

            on_end: function() {
                if(positionKey !== null) {
                    forms.savePosition(positionKey, box);
                }
            }
        });
    };

// ////////////////////////////////////////////////////////////////////////

};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
