// "How does it work?" badge - hover tooltip, click-to-describe fields.
//
// On hover, shows a tippy explaining what the badge does.
// On click, enters help mode: walks through form fields one by one,
// showing a descriptive tooltip for each. Arrow keys navigate,
// Esc deactivates help mode (does not close the form).
// Clicking a label switches to that field's tooltip.
// Clicking outside the form deactivates help mode.

(function($) {



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

    // .. mark labels that have descriptions so they get the help cursor ..
    $.fn.zato.how_it_works._markLabels(config);

    // .. clicking a marked label shows that field's tooltip,
    // .. activating help mode first if it is not active yet ..
    var container = document.getElementById(config.divId.replace('#', ''));
    $(container).off('click.how_it_works_label').on('click.how_it_works_label', 'label.how-it-works-label', function(event) {
        event.stopPropagation();

        // .. controls nested inside a wrapping label bubble their clicks here,
        // .. only clicks on the label text itself should activate help mode,
        // .. closest also covers clicks landing on option elements inside a select ..
        if (event.target.closest('input, select, textarea')) {
            return;
        }

        var fieldId = $(this).attr('for');
        var howItWorks = $.fn.zato.how_it_works;

        // .. if help mode is active for another dialog, leave it first ..
        if (howItWorks._state && howItWorks._state.container !== container) {
            howItWorks._deactivate();
        }

        // .. activate help mode on this badge if nothing is active yet ..
        if (!howItWorks._state) {
            howItWorks._activate(badge);
        }

        // .. jump to the clicked field ..
        var state = howItWorks._state;
        if (state) {
            // .. the clicked label may sit in a block expanded after activation ..
            howItWorks._refreshFields(state);
            var fieldIndex = howItWorks._findFieldIndex(state, fieldId);
            if (fieldIndex >= 0) {
                howItWorks._showFieldTooltip(state, fieldIndex);
            }
        }
    });

    // .. mark group header cells, e.g. "Pool" next to a Toggle options link ..
    $.fn.zato.how_it_works._markGroupLabels(config);

    // .. clicking an expanded group's name shows its first field's tooltip ..
    $(container).off('click.how_it_works_group').on('click.how_it_works_group', 'td.how-it-works-group-label', function(event) {
        event.stopPropagation();

        var howItWorks = $.fn.zato.how_it_works;
        var groupSelector = this._howItWorksGroupSelector;
        var groupRows = container.querySelectorAll(groupSelector);

        // .. do nothing while the group is collapsed ..
        if (!groupRows.length || groupRows[0].offsetParent === null) {
            return;
        }

        // .. if help mode is active for another dialog, leave it first ..
        if (howItWorks._state && howItWorks._state.container !== container) {
            howItWorks._deactivate();
        }

        // .. activate help mode on this badge if nothing is active yet ..
        if (!howItWorks._state) {
            howItWorks._activate(badge);
        }

        var state = howItWorks._state;
        if (!state) {
            return;
        }

        // .. the group was expanded after activation, so re-collect first ..
        howItWorks._refreshFields(state);

        // .. jump to the first described field inside the group ..
        for (var rowIndex = 0; rowIndex < groupRows.length; rowIndex++) {
            var labels = groupRows[rowIndex].querySelectorAll('label[for]');
            for (var labelIndex = 0; labelIndex < labels.length; labelIndex++) {
                var fieldIndex = howItWorks._findFieldIndex(state, labels[labelIndex].getAttribute('for'));
                if (fieldIndex >= 0) {
                    howItWorks._showFieldTooltip(state, fieldIndex);
                    return;
                }
            }
        }
    });

    // .. the help cursor on a group name only makes sense while it is expanded ..
    $(container).off('mouseenter.how_it_works_group').on('mouseenter.how_it_works_group', 'td.how-it-works-group-label', function() {
        var groupRows = container.querySelectorAll(this._howItWorksGroupSelector);
        var isExpanded = groupRows.length && groupRows[0].offsetParent !== null;
        this.classList.toggle('how-it-works-group-expanded', !!isExpanded);
    });

    // .. set up inline per-row badges if configured ..
    if (config.inlineBadge) {
        $.fn.zato.how_it_works._setupInlineBadges(config, badge);
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._markLabels = function(config) {

    var container = document.getElementById(config.divId.replace('#', ''));
    var descriptions = config.descriptions;
    var labels = container.querySelectorAll('label[for]');

    for (var labelIndex = 0; labelIndex < labels.length; labelIndex++) {
        var label = labels[labelIndex];
        var fieldId = label.getAttribute('for');
        var lookupId = fieldId.replace('id_edit-', 'id_');

        // .. only labels with a description get the help cursor ..
        if (descriptions[lookupId]) {
            label.classList.add('how-it-works-label');
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._markGroupLabels = function(config) {

    var container = document.getElementById(config.divId.replace('#', ''));

    // .. any toggle function counts, e.g. toggle_visibility or page-specific ones,
    // .. as long as it receives a class selector for the rows it expands ..
    var links = container.querySelectorAll('a[href*="toggle"]');

    for (var linkIndex = 0; linkIndex < links.length; linkIndex++) {

        var link = links[linkIndex];
        var match = link.getAttribute('href').match(/toggle\w*\('(\.[^']+)'\)/);
        if (!match) {
            continue;
        }

        var row = link.closest('tr');
        if (!row) {
            continue;
        }

        // .. the group's name is the text of the row's first cell ..
        var nameCell = row.querySelector('td');
        if (!nameCell || !nameCell.textContent.trim()) {
            continue;
        }

        nameCell.classList.add('how-it-works-group-label');
        nameCell._howItWorksGroupSelector = match[1];
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
        visibilityObserver: null,
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

    // .. label clicks are handled by the persistent handler bound in init ..

    // .. bind click on selects to switch field ..
    $(container).on('mousedown.how_it_works_select', 'select', function(event) {
        var fieldId = this.id;
        // .. the select may sit in a block expanded after activation ..
        $.fn.zato.how_it_works._refreshFields(state);
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
        // .. prefer the focused field's own label so multi-field rows
        // .. switch to the right field, not always the row's first one ..
        var label = null;
        if (event.target.id) {
            label = row.querySelector('label[for="' + event.target.id + '"]');
        }
        if (!label) {
            label = row.querySelector('label[for]');
        }
        if (!label) {
            return;
        }
        // .. the focused field may sit in a block expanded after activation ..
        $.fn.zato.how_it_works._refreshFields(state);
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

    // .. watch for anything that hides the field the tooltip points at, e.g. a collapsed
    // .. toggle block with callbacks - a tooltip must never outlive its now-invisible field ..
    state.visibilityObserver = new MutationObserver(function() {
        $.fn.zato.how_it_works._onVisibilityChange(state);
    });
    state.visibilityObserver.observe(container, {
        attributes: true,
        attributeFilter: ['style', 'class', 'hidden'],
        subtree: true,
    });

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
        // .. group name cells have their own click handling ..
        if ($(target).closest('.how-it-works-group-label').length) {
            return;
        }
        if ($(target).closest('.tippy-box').length) {
            return;
        }
        $.fn.zato.how_it_works._deactivate();
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._refreshFields = function(state) {

    // .. remember which field is currently shown ..
    var currentField = state.fields[state.currentIndex];
    var currentFieldId = currentField ? currentField.fieldId : null;

    // .. re-collect, e.g. a toggle block may have been expanded or collapsed
    // .. since activation, changing which rows are visible ..
    state.fields = $.fn.zato.how_it_works._collectFields(state.container, state.config);

    // .. keep pointing at the same field if it is still visible ..
    var newIndex = 0;
    if (currentFieldId) {
        var foundIndex = $.fn.zato.how_it_works._findFieldIndex(state, currentFieldId);
        if (foundIndex >= 0) {
            newIndex = foundIndex;
        }
    }
    state.currentIndex = newIndex;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.how_it_works._onVisibilityChange = function(state) {

    // .. nothing shown means nothing to hide ..
    if (!state.fieldTippy) {
        return;
    }

    var field = state.fields[state.currentIndex];
    if (!field) {
        return;
    }

    // .. offsetParent is null for an element that is hidden itself
    // .. or sits inside a hidden ancestor, e.g. a collapsed block ..
    if (field.element.offsetParent !== null) {
        return;
    }

    // .. a field inside a hidden tab panel means a tab switch,
    // .. which the tab observer handles on its own ..
    var panel = field.element.closest('.dashboard-tab-panel');
    if (panel && panel.hidden) {
        return;
    }

    // .. the field is gone from view, so help mode ends altogether -
    // .. the tooltip disappears and the badge pops back up ..
    $.fn.zato.how_it_works._deactivate();
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

    // .. disconnect the field visibility observer ..
    if (state.visibilityObserver) {
        state.visibilityObserver.disconnect();
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
    // .. the label click handler stays bound, it is persistent from init ..
    $(document).off('mousedown.how_it_works_outside');
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

        // .. re-collect fields first, a toggle block may have been expanded meanwhile ..
        $.fn.zato.how_it_works._refreshFields(state);

        var nextIndex = state.currentIndex + 1;
        if (nextIndex < state.fields.length) {
            $.fn.zato.how_it_works._showFieldTooltip(state, nextIndex);
        }
        return;
    }

    if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
        event.preventDefault();

        // .. re-collect fields first, a toggle block may have been expanded meanwhile ..
        $.fn.zato.how_it_works._refreshFields(state);

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
        placement: field.placement || state.config.placement || 'left',
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

        // .. skip rows that are currently hidden, e.g. fields shown only for some selections ..
        if (rows[rowIndex].offsetParent === null) {
            continue;
        }

        // .. collect every labeled field in the row so rows holding several fields,
        // .. e.g. "Active | Pool size", each become separate tooltip stops ..
        var labels = rows[rowIndex].querySelectorAll('label[for]');

        for (var labelIndex = 0; labelIndex < labels.length; labelIndex++) {

            var label = labels[labelIndex];
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

            // .. when the label wraps its own control, anchor at the control itself
            // .. so the tooltip centers on the input, not on the label plus input box ..
            if (targetElement === label) {
                var control = document.getElementById(fieldId);
                if (control && label.contains(control)) {
                    targetElement = control;
                }
            }

            fields.push({
                element: targetElement,
                fieldId: fieldId,
                description: description,

                // .. with several fields in one row the tooltip goes above the field,
                // .. otherwise it would cover the neighboring fields to the left ..
                placement: labels.length > 1 ? 'top' : null,
            });
        }
    }

    return fields;
};

})(jQuery);
