// "How does it work?" badge - hover tooltip, click-to-describe fields.
//
// On hover, shows a tippy explaining what the badge does.
// On click, enters help mode: walks through form fields one by one,
// showing a descriptive tooltip for each. Arrow keys navigate,
// Esc deactivates help mode (does not close the form).
// Clicking a label switches to that field's tooltip.
// Clicking outside the form deactivates help mode.

(function($) {

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.how_it_works === 'undefined') { $.fn.zato.how_it_works = {}; }

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._state = null;
$.fn.zato.how_it_works._inlineBadge = null;
$.fn.zato.how_it_works._inlineHideTimer = null;

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works.init = function(config) {

    var badge = document.getElementById(config.badgeId);
    if (!badge) {
        return;
    }

    // .. destroy any previous hover tippy ..
    if (badge._tippy) {
        badge._tippy.destroy();
    }

    // .. store config for click handler ..
    badge._howItWorksConfig = config;

    // .. bind click ..
    $(badge).off('click.how_it_works').on('click.how_it_works', function(event) {
        event.stopPropagation();
        var currentState = $.fn.zato.how_it_works._state;
        if (currentState) {
            $.fn.zato.how_it_works._deactivate();
        }
        else {
            $.fn.zato.how_it_works._activate(badge);
        }
    });

    // .. set up inline per-row badges if configured ..
    if (config.inlineBadge) {
        $.fn.zato.how_it_works._setupInlineBadges(config, badge);
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._setupInlineBadges = function(config, mainBadge) {

    var howItWorks = $.fn.zato.how_it_works;

    // .. create the shared floating badge element once ..
    if (!howItWorks._inlineBadge) {
        var element = document.createElement('span');
        element.className = 'how-it-works-badge how-it-works-badge-inline';
        element.textContent = 'How does it work?';
        document.body.appendChild(element);
        howItWorks._inlineBadge = element;

        // .. keep badge visible while mouse is over it ..
        $(element).on('mouseenter.how_it_works_inline', function() {
            clearTimeout(howItWorks._inlineHideTimer);
        });

        $(element).on('mouseleave.how_it_works_inline', function() {
            howItWorks._inlineHideTimer = setTimeout(function() {
                element.classList.remove('how-it-works-badge-visible');
            }, 120);
        });
    }

    var floatingBadge = howItWorks._inlineBadge;
    var container = document.getElementById(config.divId.replace('#', ''));
    var rowSelector = config.inlineBadgeRowSelector;
    var anchorSelector = config.inlineBadgeAnchorSelector;
    var descriptions = config.descriptions;

    // .. show badge on row hover ..
    $(container).off('mouseenter.how_it_works_inline').on('mouseenter.how_it_works_inline', rowSelector, function() {
        clearTimeout(howItWorks._inlineHideTimer);

        var row = this;
        var label = row.querySelector('label[for]');
        if (!label) {
            floatingBadge.classList.remove('how-it-works-badge-visible');
            return;
        }

        var fieldId = label.getAttribute('for');
        var lookupId = fieldId.replace('id_edit-', 'id_');
        if (!descriptions[lookupId]) {
            floatingBadge.classList.remove('how-it-works-badge-visible');
            return;
        }

        var anchor = row.querySelector(anchorSelector);
        if (!anchor) {
            floatingBadge.classList.remove('how-it-works-badge-visible');
            return;
        }

        // .. position the badge right after the anchor text, vertically centered ..
        // .. make it visible first so offsetHeight is accurate ..
        floatingBadge.classList.add('how-it-works-badge-visible');
        var boundingRectangle = anchor.getBoundingClientRect();
        var badgeHeight = floatingBadge.offsetHeight;
        var centeredTop = boundingRectangle.top + (boundingRectangle.height - badgeHeight) / 2;
        floatingBadge.style.top = (centeredTop + window.scrollY) + 'px';
        floatingBadge.style.left = (boundingRectangle.right + window.scrollX + 6) + 'px';
        floatingBadge._howItWorksFieldId = fieldId;
        floatingBadge._howItWorksConfig = config;
        floatingBadge._howItWorksMainBadge = mainBadge;
        floatingBadge.classList.add('how-it-works-badge-visible');
    });

    // .. hide badge when mouse leaves the row ..
    $(container).off('mouseleave.how_it_works_inline').on('mouseleave.how_it_works_inline', rowSelector, function() {
        howItWorks._inlineHideTimer = setTimeout(function() {
            floatingBadge.classList.remove('how-it-works-badge-visible');
        }, 120);
    });

    // .. clicking the inline badge activates help mode at that specific field ..
    $(floatingBadge).off('click.how_it_works_inline').on('click.how_it_works_inline', function(event) {
        event.stopPropagation();

        var fieldId = floatingBadge._howItWorksFieldId;
        var badge = floatingBadge._howItWorksMainBadge;

        // .. activate if not already active ..
        var currentState = howItWorks._state;
        if (!currentState) {
            howItWorks._activate(badge);
        }

        // .. jump to the specific field ..
        var state = howItWorks._state;
        if (state) {
            var fieldIndex = howItWorks._findFieldIndex(state, fieldId);
            if (fieldIndex >= 0) {
                howItWorks._showFieldTooltip(state, fieldIndex);
            }
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._activate = function(badge) {

    var config = badge._howItWorksConfig;
    var dialog = badge.closest('.ui-dialog');
    if (!dialog) {
        if (config.containerSelector) {
            dialog = badge.closest(config.containerSelector);
        }
    }
    if (!dialog) {
        dialog = document.body;
    }
    var container = document.getElementById(config.divId.replace('#', ''));

    // .. collect visible fields from the active tab ..
    var fields = $.fn.zato.how_it_works._collectFields(container, config);

    if (!fields.length) {
        return;
    }

    // .. hide the hover tippy ..
    if (badge._tippy) {
        badge._tippy.hide();
    }

    // .. set state ..
    var state = {
        badge: badge,
        config: config,
        dialog: dialog,
        container: container,
        fields: fields,
        currentIndex: 0,
        fieldTippy: null,
        lastIndexPerTab: {},
        tabObserver: null,
    };

    $.fn.zato.how_it_works._state = state;

    // .. mark badge as depressed ..
    badge.classList.add('how-it-works-active');

    // .. show first field ..
    $.fn.zato.how_it_works._showFieldTooltip(state, 0);

    // .. suppress dialog closeOnEscape while help mode is active ..
    if (dialog.classList) {
        if (dialog.classList.contains('ui-dialog')) {
            $(config.divId).dialog('option', 'closeOnEscape', false);
        }
    }

    // .. bind keyboard - on the dialog element when inside jQuery UI,
    // .. on document otherwise so Esc works without focused elements ..
    state._keydownHandler = function(event) {
        $.fn.zato.how_it_works._onKeydown(event);
    };
    var isJqueryDialog = false;
    if (dialog.classList) {
        isJqueryDialog = dialog.classList.contains('ui-dialog');
    }
    state._keydownTarget = isJqueryDialog ? dialog : document;
    state._keydownTarget.addEventListener('keydown', state._keydownHandler, true);

    // .. bind click on labels to switch field ..
    $(container).on('click.how_it_works_label', 'label[for]', function(event) {
        event.stopPropagation();
        var fieldId = $(this).attr('for');
        var fieldIndex = $.fn.zato.how_it_works._findFieldIndex(state, fieldId);
        if (fieldIndex >= 0) {
            $.fn.zato.how_it_works._showFieldTooltip(state, fieldIndex);
        }
    });

    // .. bind click on selects to switch field ..
    $(container).on('mousedown.how_it_works_select', 'select', function(event) {
        var fieldId = this.id;
        var fieldIndex = $.fn.zato.how_it_works._findFieldIndexByInput(state, fieldId);
        if (fieldIndex >= 0) {
            if (fieldIndex !== state.currentIndex) {
                $.fn.zato.how_it_works._showFieldTooltip(state, fieldIndex);
            }
        }
    });

    // .. follow focus to switch tooltip ..
    var focusinRowSelector = config.fieldSelector || 'tr';
    state._focusinHandler = function(event) {
        var row = event.target.closest(focusinRowSelector);
        if (!row) {
            return;
        }
        var label = row.querySelector('label[for]');
        if (!label) {
            return;
        }
        var fieldIndex = $.fn.zato.how_it_works._findFieldIndex(state, label.getAttribute('for'));
        if (fieldIndex >= 0) {
            if (fieldIndex !== state.currentIndex) {
                $.fn.zato.how_it_works._showFieldTooltip(state, fieldIndex);
            }
        }
    };
    container.addEventListener('focusin', state._focusinHandler, true);

    // .. watch for tab switches via hidden attribute changes on panels ..
    var panelsContainer = container.querySelector('.dashboard-tab-panel');
    if (panelsContainer) {
        var parentOfPanels = panelsContainer.parentNode;
        state.tabObserver = new MutationObserver(function(mutationList) {
            $.fn.zato.how_it_works._onTabSwitch(state);
        });
        state.tabObserver.observe(parentOfPanels, {
            attributes: true,
            attributeFilter: ['hidden'],
            subtree: true,
        });
    }

    // .. clicking anywhere except inputs/selects/labels deactivates help mode ..
    $(document).on('mousedown.how_it_works_outside', function(event) {
        var target = event.target;
        if (!dialog.contains(target)) {
            $.fn.zato.how_it_works._deactivate();
            return;
        }
        var tag = target.tagName;
        if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA' || tag === 'LABEL' || tag === 'A' || tag === 'BUTTON') {
            return;
        }
        if ($(target).closest('.how-it-works-badge').length) {
            return;
        }
        if ($(target).closest('.tippy-box').length) {
            return;
        }
        $.fn.zato.how_it_works._deactivate();
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._onTabSwitch = function(state) {

    // .. save current index for the old tab ..
    var oldTabName = $.fn.zato.how_it_works._getActiveTabName(state.container);

    // .. re-collect fields from the newly active tab ..
    var newFields = $.fn.zato.how_it_works._collectFields(state.container, state.config);

    if (!newFields.length) {
        if (state.fieldTippy) {
            state.fieldTippy.destroy();
            state.fieldTippy = null;
        }
        state.fields = newFields;
        return;
    }

    // .. destroy old tooltip ..
    if (state.fieldTippy) {
        state.fieldTippy.destroy();
        state.fieldTippy = null;
    }

    state.fields = newFields;

    // .. find the new active tab name ..
    var newTabName = $.fn.zato.how_it_works._getActiveTabName(state.container);

    // .. restore last index for this tab, or start at 0 ..
    var restoredIndex = state.lastIndexPerTab[newTabName];

    if (restoredIndex === undefined) {
        restoredIndex = 0;
    }

    if (restoredIndex >= newFields.length) {
        restoredIndex = 0;
    }

    $.fn.zato.how_it_works._showFieldTooltip(state, restoredIndex);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._getActiveTabName = function(container) {

    var buttons = container.querySelectorAll('.dashboard-tab-button');

    for (var buttonIndex = 0; buttonIndex < buttons.length; buttonIndex++) {
        if (buttons[buttonIndex].classList.contains('active')) {
            return buttons[buttonIndex].textContent.trim();
        }
    }

    return '';
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._deactivate = function() {

    var state = $.fn.zato.how_it_works._state;
    if (!state) {
        return;
    }

    // .. destroy current field tooltip ..
    if (state.fieldTippy) {
        state.fieldTippy.destroy();
    }

    // .. disconnect tab observer ..
    if (state.tabObserver) {
        state.tabObserver.disconnect();
    }

    // .. remove depressed look ..
    state.badge.classList.remove('how-it-works-active');

    // .. hide the inline badge when leaving help mode ..
    var inlineBadge = $.fn.zato.how_it_works._inlineBadge;
    if (inlineBadge) {
        inlineBadge.classList.remove('how-it-works-badge-visible');
    }

    // .. restore dialog closeOnEscape ..
    if (state.dialog.classList) {
        if (state.dialog.classList.contains('ui-dialog')) {
            $(state.config.divId).dialog('option', 'closeOnEscape', true);
        }
    }

    // .. unbind ..
    state._keydownTarget.removeEventListener('keydown', state._keydownHandler, true);
    state.container.removeEventListener('focusin', state._focusinHandler, true);
    $(document).off('mousedown.how_it_works_outside');
    $(state.container).off('click.how_it_works_label');
    $(state.container).off('mousedown.how_it_works_select');

    $.fn.zato.how_it_works._state = null;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._onKeydown = function(event) {

    var state = $.fn.zato.how_it_works._state;
    if (!state) {
        return;
    }

    if (event.key === 'Escape') {
        event.preventDefault();
        event.stopPropagation();
        $.fn.zato.how_it_works._deactivate();
        return;
    }

    if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
        event.preventDefault();
        var nextIndex = state.currentIndex + 1;
        if (nextIndex < state.fields.length) {
            $.fn.zato.how_it_works._showFieldTooltip(state, nextIndex);
        }
        return;
    }

    if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
        event.preventDefault();
        var previousIndex = state.currentIndex - 1;
        if (previousIndex >= 0) {
            $.fn.zato.how_it_works._showFieldTooltip(state, previousIndex);
        }
        return;
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._showFieldTooltip = function(state, index) {

    // .. skip if already showing this field ..
    if (state.fieldTippy) {
        if (state.currentIndex === index) {
            return;
        }
    }

    // .. destroy previous tooltip ..
    if (state.fieldTippy) {
        state.fieldTippy.destroy();
    }

    state.currentIndex = index;

    // .. remember this index for the current tab ..
    var tabName = $.fn.zato.how_it_works._getActiveTabName(state.container);
    state.lastIndexPerTab[tabName] = index;

    var field = state.fields[index];
    var target = field.element;

    // .. pre-set the inline toggle's checked state in the HTML so it renders
    // .. in the correct position immediately, without a visible slide animation ..
    var description = field.description;
    var realCheckbox = document.getElementById(field.fieldId);
    if (realCheckbox && realCheckbox.checked) {
        description = description.replace(
            'class="how-it-works-posture-toggle-input"',
            'class="how-it-works-posture-toggle-input" checked'
        );
    }

    var tooltipContent = description +
        '<div style="text-align:right;font-size:9px;font-family:monospace;opacity:0.7;margin-top:6px">' +
        'Esc, left arrow, right arrow</div>';

    var result = tippy(target, {
        content: tooltipContent,
        allowHTML: true,
        placement: state.config.placement || 'left',
        theme: 'dark',
        arrow: true,
        interactive: true,
        inertia: true,
        trigger: 'manual',
        hideOnClick: false,
        appendTo: function() { return state.dialog || document.body; },
    });

    state.fieldTippy = Array.isArray(result) ? result[0] : result;
    state.fieldTippy.show();

    // .. bind the inline toggle to sync changes back to the real checkbox ..
    var tippyBox = state.fieldTippy.popper;
    var inlineToggle = tippyBox.querySelector('.how-it-works-posture-toggle-input');
    if (inlineToggle && realCheckbox) {
        $(inlineToggle).off('change.how_it_works_sync').on('change.how_it_works_sync', function() {
            realCheckbox.checked = this.checked;
        });
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._findFieldIndex = function(state, fieldId) {

    for (var index = 0; index < state.fields.length; index++) {
        if (state.fields[index].fieldId === fieldId) {
            return index;
        }
    }

    return -1;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._findFieldIndexByInput = function(state, inputId) {

    for (var index = 0; index < state.fields.length; index++) {
        if (state.fields[index].fieldId === inputId) {
            return index;
        }
    }

    return -1;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._collectFields = function(container, config) {

    var descriptions = config.descriptions || {};
    var fields = [];

    // .. find the active tab panel ..
    var panels = container.querySelectorAll('.dashboard-tab-panel');
    var activePanel = null;

    for (var panelIndex = 0; panelIndex < panels.length; panelIndex++) {
        if (!panels[panelIndex].hidden) {
            activePanel = panels[panelIndex];
            break;
        }
    }

    if (!activePanel) {
        activePanel = container;
    }

    // .. walk each row in the form table or custom container ..
    var rowSelector = config.fieldSelector || 'table.form-data tr';
    var rows = activePanel.querySelectorAll(rowSelector);

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        var label = rows[rowIndex].querySelector('label[for]');
        if (!label) {
            continue;
        }

        var fieldId = label.getAttribute('for');
        var lookupId = fieldId.replace('id_edit-', 'id_');
        var description = descriptions[lookupId];
        if (!description) {
            continue;
        }

        // .. use a custom target element if configured, otherwise the label ..
        var targetElement = label;
        if (config.targetSelector) {
            var customTarget = rows[rowIndex].querySelector(config.targetSelector);
            if (customTarget) {
                targetElement = customTarget;
            }
        }

        fields.push({
            element: targetElement,
            fieldId: fieldId,
            description: description,
        });
    }

    return fields;
};

})(jQuery);
