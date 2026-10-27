zatoPortal.layouts = {};

zatoPortal.layouts.config = {
    layoutEntryAttribute: 'data-layout-entry',
    cardSelector: '.portal-operation',
    sectionSelector: '.portal-group',
    masterSelector: '.portal-layout-master',
    detailSelector: '.portal-layout-detail',
    activeCardSelector: '.portal-operation.portal-layout-active',
    activeClass: 'portal-layout-active',
    rowScrollBlock: 'nearest',
    listSelector: '.portal-layout-list',
    rowSelector: '.portal-layout-row',
    excludedClass: 'portal-layout-excluded',
    filterPlaceholder: 'Filter',
    clearLabel: 'Clear',
    filterIconCircle: {'cx': '11', 'cy': '11', 'r': '7'},
    filterIconHandle: 'm20 20-3.5-3.5',
    clearIconStrokes: ['M18 6 6 18', 'm6 6 12 12'],
    escapeKey: 'Escape',
    enterKey: 'Enter',
    resizerClass: 'portal-layout-resizer',
    gripClass: 'portal-layout-grip',
    resizeLabel: 'Resize',
    resizingClass: 'portal-body portal-resizing-layout',
    idleClass: 'portal-body',
    storageKey: 'zato.openapi.portal.master.width',
    widthVariable: '--portal-layout-master-width',
    widthUnit: 'px',
    widthMinimum: 240,
    widthMaximumShare: 0.6,
    primaryButton: 0,
    masterTopClass: 'portal-layout-master-top',
    toggleClass: 'portal-sidebar-toggle portal-layout-toggle',
    toggleSelector: '.portal-layout-toggle',
    contentId: 'portal-content',
    collapsedContentClass: 'portal-content portal-layout-master-collapsed',
    expandedContentClass: 'portal-content',
    collapsedStorageKey: 'zato.openapi.portal.master.collapsed',
    collapsedValue: '1',
    expandedValue: '0',
    collapseLabel: 'Collapse',
    expandLabel: 'Expand',
    iconCollapseClass: 'portal-sidebar-icon portal-layout-icon-collapse',
    iconExpandClass: 'portal-sidebar-icon portal-layout-icon-expand',
};

zatoPortal.layouts.collapse = {
    isCollapsed: false,
};

zatoPortal.layouts.drag = {
    isDragging: false,
    startX: 0,
    startWidth: 0,
    maximumWidth: 0,
    width: 0,
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.init = function() {

    var config = zatoPortal.layouts.config;

    // The width of an earlier visit applies to every group, localStorage returning null for a key never stored
    var stored = localStorage.getItem(config.storageKey);

    if(stored !== null) {
        document.documentElement.style.setProperty(config.widthVariable, stored + config.widthUnit);
    }

    // The list is collapsed or not in every group alike, as it was left on an earlier visit
    var storedCollapsed = localStorage.getItem(config.collapsedStorageKey);
    zatoPortal.layouts.collapse.isCollapsed = storedCollapsed === config.collapsedValue;

    zatoPortal.layouts.applyCollapsed();
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.applyCollapsed = function() {

    var config = zatoPortal.layouts.config;
    var isCollapsed = zatoPortal.layouts.collapse.isCollapsed;

    var content = document.getElementById(config.contentId);
    content.className = isCollapsed ? config.collapsedContentClass : config.expandedContentClass;

    var toggles = document.querySelectorAll(config.toggleSelector);

    for(var toggleIndex = 0; toggleIndex < toggles.length; toggleIndex++) {
        zatoPortal.layouts.markToggle(toggles[toggleIndex]);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.markToggle = function(toggle) {

    var config = zatoPortal.layouts.config;
    var isCollapsed = zatoPortal.layouts.collapse.isCollapsed;
    var label = isCollapsed ? config.expandLabel : config.collapseLabel;

    toggle.setAttribute('aria-expanded', isCollapsed ? 'false' : 'true');
    toggle.setAttribute('aria-label', label);
    toggle.title = label;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.buildToggle = function() {

    var config = zatoPortal.layouts.config;

    var toggle = zatoPortal.render.createElement('button', config.toggleClass);
    toggle.type = 'button';
    toggle.addEventListener('click', zatoPortal.layouts.onToggleClick);

    var collapseIcon = zatoPortal.sidebar.buildIcon(zatoPortal.sidebar.config.iconCollapseChevron, config.iconCollapseClass);
    var expandIcon = zatoPortal.sidebar.buildIcon(zatoPortal.sidebar.config.iconExpandChevron, config.iconExpandClass);

    toggle.appendChild(collapseIcon);
    toggle.appendChild(expandIcon);

    zatoPortal.layouts.markToggle(toggle);

    return toggle;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.onToggleClick = function() {

    var config = zatoPortal.layouts.config;
    var collapse = zatoPortal.layouts.collapse;

    collapse.isCollapsed = !collapse.isCollapsed;
    localStorage.setItem(config.collapsedStorageKey, collapse.isCollapsed ? config.collapsedValue : config.expandedValue);

    zatoPortal.layouts.applyCollapsed();
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.apply = function(section, group) {

    var frame = zatoPortal.render.createElement('div', 'portal-layout-frame');
    var master = zatoPortal.layouts.buildEntryButtons(group);
    var resizer = zatoPortal.layouts.buildResizer();
    var detail = zatoPortal.render.createElement('div', 'portal-layout-detail');

    // The list of operations stands next to the detail column that holds the cards ..
    var cards = zatoPortal.layouts.getCards(section);
    zatoPortal.layouts.moveCards(cards, detail);

    frame.appendChild(master);
    frame.appendChild(resizer);
    frame.appendChild(detail);
    section.appendChild(frame);

    // .. of which the first one is shown.
    zatoPortal.layouts.showOnly(section, cards[0]);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.activate = function(entryId) {

    var config = zatoPortal.layouts.config;
    var card = document.getElementById(entryId);
    var section = card.closest(config.sectionSelector);

    zatoPortal.layouts.showOnly(section, card);

    // A card shown anew starts at its top ..
    var detail = section.querySelector(config.detailSelector);
    detail.scrollTop = 0;

    // .. its row is brought into view in the list, which matters when the card is chosen from the navigation ..
    var row = section.querySelector('[' + config.layoutEntryAttribute + '="' + entryId + '"]');
    row.scrollIntoView({block: config.rowScrollBlock});

    // .. and the address and the specification window follow it.
    zatoPortal.layouts.onCardShown(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.onGroupShown = function(section) {

    var card = section.querySelector(zatoPortal.layouts.config.activeCardSelector);
    zatoPortal.layouts.onCardShown(card.id);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.onCardShown = function(entryId) {
    zatoPortal.links.update(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.getCards = function(section) {

    var config = zatoPortal.layouts.config;
    var found = section.querySelectorAll(config.cardSelector);
    var out = [];

    for(var cardIndex = 0; cardIndex < found.length; cardIndex++) {
        out.push(found[cardIndex]);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.setEntryVisible = function(entryId, isVisible) {

    var config = zatoPortal.layouts.config;
    var selector = '[' + config.layoutEntryAttribute + '="' + entryId + '"]';
    var elements = document.querySelectorAll(selector);

    // The navigation's filter excludes rows apart from the list's own filter, which hides them
    for(var elementIndex = 0; elementIndex < elements.length; elementIndex++) {
        elements[elementIndex].classList.toggle(config.excludedClass, !isVisible);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.buildEntryButton = function(entry) {

    var config = zatoPortal.layouts.config;

    var button = zatoPortal.render.createElement('button', 'portal-layout-row');
    button.type = 'button';
    button.setAttribute(config.layoutEntryAttribute, entry.id);
    button.addEventListener('click', zatoPortal.layouts.onEntryButtonClick);

    var chip = zatoPortal.render.createMethodChip(entry.method);
    var path = zatoPortal.render.buildPath(entry.path, 'portal-layout-entry-path');

    button.appendChild(chip);
    button.appendChild(path);

    return button;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.buildEntryButtons = function(group) {

    var config = zatoPortal.layouts.config;
    var container = zatoPortal.render.createElement('div', 'portal-layout-master');

    // The filter and the button that collapses the list stay above the rows while they scroll
    var masterTop = zatoPortal.render.createElement('div', config.masterTopClass);
    var filter = zatoPortal.layouts.buildFilter();
    var toggle = zatoPortal.layouts.buildToggle();
    var list = zatoPortal.render.createElement('div', 'portal-layout-list');

    masterTop.appendChild(filter);
    masterTop.appendChild(toggle);

    for(var entryIndex = 0; entryIndex < group.entries.length; entryIndex++) {
        var entry = group.entries[entryIndex];
        var button = zatoPortal.layouts.buildEntryButton(entry);
        list.appendChild(button);
    }

    container.appendChild(masterTop);
    container.appendChild(list);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.buildFilter = function() {

    var config = zatoPortal.layouts.config;
    var panels = zatoPortal.panels;
    var viewBox = panels.config.iconViewBox;

    var box = zatoPortal.render.createElement('div', 'portal-filter-box portal-layout-filter');

    var icon = panels.createSvgElement('svg', {'class': 'portal-filter-icon', 'viewBox': viewBox});
    var circle = panels.createSvgElement('circle', config.filterIconCircle);
    var handle = panels.createSvgElement('path', {'d': config.filterIconHandle});

    icon.appendChild(circle);
    icon.appendChild(handle);

    var input = zatoPortal.render.createElement('input', 'portal-filter');
    input.type = 'text';
    input.placeholder = config.filterPlaceholder;
    input.autocomplete = 'off';
    input.spellcheck = false;
    input.addEventListener('input', zatoPortal.layouts.onFilterInput);
    input.addEventListener('keydown', zatoPortal.layouts.onFilterKeyDown);

    var clear = zatoPortal.render.createElement('button', 'portal-filter-clear');
    clear.type = 'button';
    clear.hidden = true;
    clear.setAttribute('aria-label', config.clearLabel);
    clear.addEventListener('click', zatoPortal.layouts.onFilterClearClick);

    var clearIcon = panels.createSvgElement('svg', {'class': 'portal-filter-clear-icon', 'viewBox': viewBox});

    for(var strokeIndex = 0; strokeIndex < config.clearIconStrokes.length; strokeIndex++) {
        var stroke = panels.createSvgElement('path', {'d': config.clearIconStrokes[strokeIndex]});
        clearIcon.appendChild(stroke);
    }

    clear.appendChild(clearIcon);

    box.appendChild(icon);
    box.appendChild(input);
    box.appendChild(clear);

    return box;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.onFilterInput = function(event) {

    var config = zatoPortal.layouts.config;
    var input = event.target;
    var box = input.parentNode;
    var master = input.closest(config.masterSelector);

    var query = input.value.trim().toLowerCase();
    var rows = master.querySelectorAll(config.rowSelector);

    var clear = box.querySelector('button');
    clear.hidden = input.value === '';

    // A row stays when its operation matches the way it matches in the navigation's filter
    for(var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        var row = rows[rowIndex];
        var entryId = row.getAttribute(config.layoutEntryAttribute);
        var entry = zatoPortal.state.entriesById[entryId];
        var searchText = zatoPortal.render.getSearchText(entry);

        row.hidden = !searchText.includes(query);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.onFilterKeyDown = function(event) {

    var config = zatoPortal.layouts.config;
    var input = event.target;

    // Escape empties the filter ..
    if(event.key === config.escapeKey) {
        input.value = '';
        input.dispatchEvent(new Event('input'));
        return;
    }

    if(event.key !== config.enterKey) {
        return;
    }

    // .. and Enter shows the first operation that is still listed.
    var master = input.closest(config.masterSelector);
    var rows = master.querySelectorAll(config.rowSelector);

    for(var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        var row = rows[rowIndex];

        if(row.hidden) {
            continue;
        }

        if(row.classList.contains(config.excludedClass)) {
            continue;
        }

        row.click();
        return;
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.onFilterClearClick = function(event) {

    var input = event.currentTarget.parentNode.querySelector('input');

    // The filter is cleared the same way typing changes it, so the rows and the clear button both follow
    input.value = '';
    input.dispatchEvent(new Event('input'));
    input.focus();
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.onEntryButtonClick = function(event) {

    var config = zatoPortal.layouts.config;
    var entryId = event.currentTarget.getAttribute(config.layoutEntryAttribute);

    zatoPortal.layouts.activate(entryId);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.showOnly = function(section, card) {

    var config = zatoPortal.layouts.config;
    var cards = zatoPortal.layouts.getCards(section);
    var buttonSelector = '[' + config.layoutEntryAttribute + ']';
    var buttons = section.querySelectorAll(buttonSelector);

    // The card shown and the button that stands for it are marked, all the other ones are not
    for(var cardIndex = 0; cardIndex < cards.length; cardIndex++) {
        cards[cardIndex].classList.toggle(config.activeClass, cards[cardIndex] === card);
    }

    for(var buttonIndex = 0; buttonIndex < buttons.length; buttonIndex++) {
        var button = buttons[buttonIndex];
        var isActive = button.getAttribute(config.layoutEntryAttribute) === card.id;
        button.classList.toggle(config.activeClass, isActive);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.moveCards = function(cards, target) {

    for(var cardIndex = 0; cardIndex < cards.length; cardIndex++) {
        target.appendChild(cards[cardIndex]);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.buildResizer = function() {

    var config = zatoPortal.layouts.config;

    var resizer = zatoPortal.render.createElement('div', config.resizerClass);
    var grip = zatoPortal.render.createElement('span', config.gripClass);

    resizer.setAttribute('role', 'separator');
    resizer.setAttribute('aria-orientation', 'vertical');
    resizer.setAttribute('aria-label', config.resizeLabel);

    resizer.addEventListener('pointerdown', zatoPortal.layouts.onPointerDown);
    resizer.addEventListener('pointermove', zatoPortal.layouts.onPointerMove);
    resizer.addEventListener('pointerup', zatoPortal.layouts.onPointerUp);
    resizer.addEventListener('pointercancel', zatoPortal.layouts.onPointerUp);

    resizer.appendChild(grip);

    return resizer;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.onPointerDown = function(event) {

    var config = zatoPortal.layouts.config;
    var drag = zatoPortal.layouts.drag;

    // Only the primary button starts a drag ..
    if(event.button !== config.primaryButton) {
        return;
    }

    // .. no text is selected while the pointer crosses the page ..
    event.preventDefault();

    var resizer = event.currentTarget;
    var frame = resizer.parentNode;
    var master = frame.querySelector(config.masterSelector);

    var frameWidth = frame.getBoundingClientRect().width;

    drag.isDragging = true;
    drag.startX = event.clientX;
    drag.startWidth = master.getBoundingClientRect().width;
    drag.maximumWidth = frameWidth * config.widthMaximumShare;
    drag.width = drag.startWidth;

    // .. and capturing the pointer keeps the drag going when it leaves the handle.
    resizer.setPointerCapture(event.pointerId);
    document.body.className = config.resizingClass;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.onPointerMove = function(event) {

    var config = zatoPortal.layouts.config;
    var drag = zatoPortal.layouts.drag;

    if(!drag.isDragging) {
        return;
    }

    var requestedWidth = drag.startWidth + event.clientX - drag.startX;
    var atLeastMinimum = Math.max(config.widthMinimum, requestedWidth);

    drag.width = Math.min(drag.maximumWidth, atLeastMinimum);
    document.documentElement.style.setProperty(config.widthVariable, drag.width + config.widthUnit);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.onPointerUp = function(event) {

    var config = zatoPortal.layouts.config;
    var drag = zatoPortal.layouts.drag;

    if(!drag.isDragging) {
        return;
    }

    drag.isDragging = false;

    event.currentTarget.releasePointerCapture(event.pointerId);
    document.body.className = config.idleClass;

    localStorage.setItem(config.storageKey, Math.round(drag.width));
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.layouts.init();
