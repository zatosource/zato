zatoPortal.specification = {};

zatoPortal.specification.config = {
    storageKey: 'zato.openapi.portal.specification.size',
    positionStorageKey: 'zato.openapi.portal.specification.window',
    cardSelector: '.portal-operation',
    sidebarSelector: '.portal-sidebar',
    buttonSelector: '.portal-tool-specification',
    activeClass: 'portal-tool-active',
    placement: 'bottom-start',
    animation: 'fade',
    strategy: 'fixed',
    layer: 200,
    defaultWidth: 560,
    defaultHeight: 520,
    edgeMargin: 16,
    cascadeOffset: 32,
    minimumVisible: 64,
    escapeKey: 'Escape',
    closeText: 'Close',
    copyAsText: 'Copy as',
    copyFormats: [
        {name: 'text', label: 'Text'},
        {name: 'json', label: 'JSON'},
    ],
    jsonFormat: 'json',
    formatAttribute: 'data-format',
    menuPlacement: 'top-end',
    menuOffset: [0, 4],
    menuLayer: 300,
    unit: 'px',
    primaryButton: 0,
};

zatoPortal.specification.state = {

    // The windows in the order they were opened, which is the order Escape closes them in reverse ..
    windows: [],

    // .. and the same windows from the bottom one to the top one on the page.
    stacking: [],
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.loadSize = function() {

    var config = zatoPortal.specification.config;

    // localStorage returns null for a key that was never stored, and the window then opens with its default size
    var stored = localStorage.getItem(config.storageKey);

    if(stored === null) {
        var defaultSize = {width: config.defaultWidth, height: config.defaultHeight};
        return defaultSize;
    }

    var out = JSON.parse(stored);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.saveSize = function(specWindow) {

    var size = {width: specWindow.width, height: specWindow.height};
    localStorage.setItem(zatoPortal.specification.config.storageKey, JSON.stringify(size));
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.savePosition = function(specWindow) {

    var position = {left: specWindow.left, top: specWindow.top};
    localStorage.setItem(zatoPortal.specification.config.positionStorageKey, JSON.stringify(position));
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.clampPosition = function(left, top, width) {

    var config = zatoPortal.specification.config;

    // The bar never leaves the page, so the window can always be dragged back
    var leftMinimum = config.minimumVisible - width;
    var leftMaximum = window.innerWidth - config.minimumVisible;
    var topMaximum = window.innerHeight - config.minimumVisible;

    var out = {
        left: Math.min(leftMaximum, Math.max(leftMinimum, left)),
        top: Math.min(topMaximum, Math.max(0, top)),
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.getStartPosition = function(card, size) {

    var config = zatoPortal.specification.config;

    // localStorage returns null until the first window is moved, and the window then opens at its default place ..
    var stored = localStorage.getItem(config.positionStorageKey);

    // .. while a place it was moved to is kept, within a page that may have become smaller since.
    if(stored !== null) {
        var position = JSON.parse(stored);
        var kept = zatoPortal.specification.clampPosition(position.left, position.top, size.width);
        return kept;
    }

    // The default place starts at the middle of the sidebar and a margin below the top of the operations list
    var sidebarRect = document.querySelector(config.sidebarSelector).getBoundingClientRect();
    var cardRect = card.getBoundingClientRect();
    var sidebarMiddle = sidebarRect.left + sidebarRect.width / 2;

    var out = {left: sidebarMiddle, top: cardRect.top + config.edgeMargin};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.getNextPosition = function(card, size) {

    var config = zatoPortal.specification.config;
    var windows = zatoPortal.specification.state.windows;
    var start = zatoPortal.specification.getStartPosition(card, size);

    // The first window opens at its start position ..
    if(windows.length === 0) {
        return start;
    }

    // .. each next one opens to the right of and below the one opened before it ..
    var previous = windows[windows.length - 1];
    var left = previous.left + config.cascadeOffset;
    var top = previous.top + config.cascadeOffset;

    // .. and a window that would reach past the page starts again from the edge it would cross.
    if(left + size.width > window.innerWidth - config.edgeMargin) {
        left = start.left;
    }

    if(top + size.height > window.innerHeight - config.edgeMargin) {
        top = start.top;
    }

    var out = {left: left, top: top};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.getReferenceRect = function(specWindow) {

    // The window hangs from a point of its own, which moves with every drag
    var out = {
        x: specWindow.left,
        y: specWindow.top,
        left: specWindow.left,
        right: specWindow.left,
        top: specWindow.top,
        bottom: specWindow.top,
        width: 0,
        height: 0,
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.build = function(specWindow) {

    var config = zatoPortal.specification.config;
    var render = zatoPortal.render;

    var element = render.createElement('div', 'portal-specification');
    element.style.width = specWindow.width + config.unit;
    element.style.height = specWindow.height + config.unit;
    element.addEventListener('pointerdown', zatoPortal.specification.raise.bind(null, specWindow), true);

    // The bar moves the window, with the operation's method and path in it ..
    var bar = render.createElement('div', 'portal-specification-bar');
    bar.addEventListener('pointerdown', zatoPortal.specification.onPointerDown.bind(null, specWindow));
    bar.addEventListener('pointermove', zatoPortal.specification.onPointerMove.bind(null, specWindow));
    bar.addEventListener('pointerup', zatoPortal.specification.onPointerUp.bind(null, specWindow));
    bar.addEventListener('pointercancel', zatoPortal.specification.onPointerUp.bind(null, specWindow));

    var title = render.createElement('span', 'portal-specification-title');

    var tools = zatoPortal.panels.buildTools();
    var copyAs = render.createElement('button', 'portal-tool portal-specification-copy', config.copyAsText);
    copyAs.type = 'button';

    var onCloseClick = zatoPortal.specification.close.bind(null, specWindow);
    var close = zatoPortal.panels.buildToolButton(config.closeText, 'portal-specification-close', onCloseClick);

    tools.appendChild(copyAs);
    tools.appendChild(close);

    bar.appendChild(title);
    bar.appendChild(tools);

    // .. and what goes in and what comes out below it.
    var body = render.createElement('div', 'portal-specification-body');

    element.appendChild(bar);
    element.appendChild(body);

    specWindow.element = element;
    specWindow.title = title;
    specWindow.body = body;
    specWindow.copyAs = copyAs;
    specWindow.menu = zatoPortal.specification.buildMenu(specWindow);

    // A size changed with the corner of the window is the size the next window opens with
    specWindow.observer = new ResizeObserver(zatoPortal.specification.onResize.bind(null, specWindow));
    specWindow.observer.observe(element);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.open = function(card) {

    var config = zatoPortal.specification.config;
    var state = zatoPortal.specification.state;

    var size = zatoPortal.specification.loadSize();
    var position = zatoPortal.specification.getNextPosition(card, size);

    var specWindow = {
        entryId: card.id,
        left: position.left,
        top: position.top,
        width: size.width,
        height: size.height,
        isDragging: false,
        startX: 0,
        startY: 0,
        startLeft: 0,
        startTop: 0,
    };

    zatoPortal.specification.build(specWindow);
    zatoPortal.specification.fill(specWindow);

    // Each window hangs from an anchor of its own, outside the page, and is placed by its own point,
    // so neither flipping nor keeping it in view applies ..
    var anchor = document.createElement('span');

    specWindow.instance = tippy(anchor, {
        content: specWindow.element,
        trigger: 'manual',
        interactive: true,
        hideOnClick: false,
        arrow: false,
        placement: config.placement,
        offset: [0, 0],
        maxWidth: 'none',
        appendTo: document.body,
        theme: zatoPortal.panels.config.bareTheme,
        zIndex: config.layer,
        animation: config.animation,
        getReferenceClientRect: zatoPortal.specification.getReferenceRect.bind(null, specWindow),
        onHidden: zatoPortal.specification.onHidden.bind(null, specWindow),
        popperOptions: {
            strategy: config.strategy,
            modifiers: [
                {name: 'flip', enabled: false},
                {name: 'preventOverflow', enabled: false},
            ],
        },
    });

    state.windows.push(specWindow);
    state.stacking.push(specWindow);

    // .. and a new window always opens above the ones already open.
    specWindow.instance.show();
    zatoPortal.specification.restack();
    zatoPortal.specification.markButtons();
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.getWindow = function(entryId) {

    var windows = zatoPortal.specification.state.windows;

    for(var windowIndex = 0; windowIndex < windows.length; windowIndex++) {
        var specWindow = windows[windowIndex];

        if(specWindow.entryId === entryId) {
            return specWindow;
        }
    }

    return null;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.onButtonClick = function(event) {

    var card = event.currentTarget.closest(zatoPortal.specification.config.cardSelector);
    var specWindow = zatoPortal.specification.getWindow(card.id);

    // The button of an operation with a window open closes that window, and otherwise it opens one more
    if(specWindow === null) {
        zatoPortal.specification.open(card);
    }
    else {
        zatoPortal.specification.close(specWindow);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.close = function(specWindow) {

    var state = zatoPortal.specification.state;

    state.windows.splice(state.windows.indexOf(specWindow), 1);
    state.stacking.splice(state.stacking.indexOf(specWindow), 1);

    specWindow.menu.hide();
    specWindow.instance.hide();

    zatoPortal.specification.markButtons();
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.onHidden = function(specWindow) {

    // A closed window is never shown again, so nothing of it is kept once it fades out
    specWindow.observer.disconnect();
    specWindow.menu.destroy();
    specWindow.instance.destroy();
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.raise = function(specWindow) {

    var stacking = zatoPortal.specification.state.stacking;

    stacking.splice(stacking.indexOf(specWindow), 1);
    stacking.push(specWindow);

    zatoPortal.specification.restack();
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.restack = function() {

    var config = zatoPortal.specification.config;
    var stacking = zatoPortal.specification.state.stacking;

    // The layers are counted from the bottom window up, so they stay below the menus whatever the number of clicks
    for(var stackIndex = 0; stackIndex < stacking.length; stackIndex++) {
        var specWindow = stacking[stackIndex];
        specWindow.instance.popper.style.zIndex = config.layer + stackIndex;
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.onDocumentKeyDown = function(event) {

    var config = zatoPortal.specification.config;
    var windows = zatoPortal.specification.state.windows;

    if(event.key !== config.escapeKey) {
        return;
    }

    // Escape already used by a filter, or meant for the popover, leaves the windows as they are ..
    if(event.defaultPrevented) {
        return;
    }

    if(zatoPortal.popover.state.anchor !== null) {
        return;
    }

    if(windows.length === 0) {
        return;
    }

    // .. an open menu closes before any window ..
    for(var windowIndex = 0; windowIndex < windows.length; windowIndex++) {
        var menu = windows[windowIndex].menu;

        if(menu.state.isVisible) {
            menu.hide();
            return;
        }
    }

    // .. and the windows close from the most recently opened one back to the first.
    var latest = windows[windows.length - 1];
    zatoPortal.specification.close(latest);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.fill = function(specWindow) {

    var entry = zatoPortal.state.entriesById[specWindow.entryId];

    var chip = zatoPortal.render.createMethodChip(entry.method);
    var path = zatoPortal.render.buildPath(entry.path, 'portal-specification-path');

    specWindow.title.appendChild(chip);
    specWindow.title.appendChild(path);

    var fields = zatoPortal.fields.build(entry.operation);
    specWindow.body.appendChild(fields);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.markButtons = function() {

    var config = zatoPortal.specification.config;
    var buttons = document.querySelectorAll(config.buttonSelector);

    for(var buttonIndex = 0; buttonIndex < buttons.length; buttonIndex++) {
        var button = buttons[buttonIndex];
        var card = button.closest(config.cardSelector);
        var isOpen = zatoPortal.specification.getWindow(card.id) !== null;

        button.classList.toggle(config.activeClass, isOpen);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.buildMenu = function(specWindow) {

    var config = zatoPortal.specification.config;
    var menu = zatoPortal.render.createElement('div', 'portal-menu');

    for(var formatIndex = 0; formatIndex < config.copyFormats.length; formatIndex++) {
        var format = config.copyFormats[formatIndex];
        var item = zatoPortal.render.createElement('button', 'portal-menu-item', format.label);

        item.type = 'button';
        item.setAttribute(config.formatAttribute, format.name);
        item.addEventListener('click', zatoPortal.specification.onCopyFormatClick.bind(null, specWindow));

        menu.appendChild(item);
    }

    // The menu is placed on the page itself, above every window, so no window's edges cut it off,
    // and its button opens and closes it
    var out = tippy(specWindow.copyAs, {
        content: menu,
        trigger: 'click',
        interactive: true,
        arrow: false,
        placement: config.menuPlacement,
        offset: config.menuOffset,
        maxWidth: 'none',
        appendTo: document.body,
        theme: zatoPortal.panels.config.bareTheme,
        zIndex: config.menuLayer,
        animation: config.animation,
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.onCopyFormatClick = function(specWindow, event) {

    var config = zatoPortal.specification.config;

    var format = event.currentTarget.getAttribute(config.formatAttribute);
    var operation = zatoPortal.state.entriesById[specWindow.entryId].operation;
    var text = '';

    if(format === config.jsonFormat) {
        text = zatoPortal.fields.toJson(operation);
    }
    else {
        text = zatoPortal.fields.toText(operation);
    }

    specWindow.menu.hide();
    navigator.clipboard.writeText(text).then(zatoPortal.panels.showCopied.bind(null, specWindow.copyAs));
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.onResize = function(specWindow) {

    // A window fading out is taken out of the page and has no size of its own to keep
    if(!specWindow.element.isConnected) {
        return;
    }

    specWindow.width = specWindow.element.offsetWidth;
    specWindow.height = specWindow.element.offsetHeight;

    zatoPortal.specification.saveSize(specWindow);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.onPointerDown = function(specWindow, event) {

    var config = zatoPortal.specification.config;

    // Only the primary button starts a drag, and the buttons in the bar keep their own clicks ..
    if(event.button !== config.primaryButton) {
        return;
    }

    if(event.target.closest('button') !== null) {
        return;
    }

    // .. no text is selected while the pointer crosses the page, and a menu open in the bar would be left behind ..
    event.preventDefault();
    specWindow.menu.hide();

    specWindow.isDragging = true;
    specWindow.startX = event.clientX;
    specWindow.startY = event.clientY;
    specWindow.startLeft = specWindow.left;
    specWindow.startTop = specWindow.top;

    // .. and capturing the pointer keeps the drag going when it leaves the bar.
    event.currentTarget.setPointerCapture(event.pointerId);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.onPointerMove = function(specWindow, event) {

    if(!specWindow.isDragging) {
        return;
    }

    var requestedLeft = specWindow.startLeft + event.clientX - specWindow.startX;
    var requestedTop = specWindow.startTop + event.clientY - specWindow.startY;
    var position = zatoPortal.specification.clampPosition(requestedLeft, requestedTop, specWindow.width);

    specWindow.left = position.left;
    specWindow.top = position.top;

    specWindow.instance.popperInstance.update();
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.specification.onPointerUp = function(specWindow, event) {

    if(!specWindow.isDragging) {
        return;
    }

    specWindow.isDragging = false;
    event.currentTarget.releasePointerCapture(event.pointerId);

    // Only the first window open sets where the first window opens the next time, the others step off from it
    if(zatoPortal.specification.state.windows[0] === specWindow) {
        zatoPortal.specification.savePosition(specWindow);
    }
};

// ////////////////////////////////////////////////////////////////////////

document.addEventListener('keydown', zatoPortal.specification.onDocumentKeyDown);
