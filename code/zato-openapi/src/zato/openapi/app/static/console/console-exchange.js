zatoConsole.exchange = {};

zatoConsole.exchange.config = {
    requestSelector: '.console-operation-request',
    responseSelector: '.console-operation-response',
    resizerClass: 'console-exchange-resizer',
    gripClass: 'console-exchange-grip',
    resizeLabel: 'Resize',
    resizingClass: 'console-body console-resizing-exchange',
    idleClass: 'console-body',
    storageKey: 'zato.openapi.console.request.share',
    requestShareVariable: '--console-request-share',
    responseShareVariable: '--console-response-share',
    primaryButton: 0,
};

zatoConsole.exchange.drag = {
    isDragging: false,
    startY: 0,
    startHeight: 0,
    minimumHeight: 0,
    maximumHeight: 0,
    totalHeight: 0,
    share: 0,
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.exchange.init = function() {

    // The share of an earlier visit applies to every operation, localStorage returning null for a key never stored
    var stored = localStorage.getItem(zatoConsole.exchange.config.storageKey);

    if(stored !== null) {
        zatoConsole.exchange.applyShare(Number(stored));
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.exchange.applyShare = function(share) {

    var config = zatoConsole.exchange.config;
    var style = document.documentElement.style;

    // The request and the response grow in proportion to their shares, which always add up to one
    style.setProperty(config.requestShareVariable, share);
    style.setProperty(config.responseShareVariable, 1 - share);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.exchange.buildResizer = function() {

    var config = zatoConsole.exchange.config;

    var resizer = zatoConsole.panels.createElement('div', config.resizerClass);
    var grip = zatoConsole.panels.createElement('span', config.gripClass);

    resizer.setAttribute('role', 'separator');
    resizer.setAttribute('aria-orientation', 'horizontal');
    resizer.setAttribute('aria-label', config.resizeLabel);

    resizer.addEventListener('pointerdown', zatoConsole.exchange.onPointerDown);
    resizer.addEventListener('pointermove', zatoConsole.exchange.onPointerMove);
    resizer.addEventListener('pointerup', zatoConsole.exchange.onPointerUp);
    resizer.addEventListener('pointercancel', zatoConsole.exchange.onPointerUp);

    resizer.appendChild(grip);

    return resizer;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.exchange.onPointerDown = function(event) {

    var config = zatoConsole.exchange.config;
    var drag = zatoConsole.exchange.drag;

    // Only the primary button starts a drag ..
    if(event.button !== config.primaryButton) {
        return;
    }

    // .. no text is selected while the pointer crosses the page ..
    event.preventDefault();

    var resizer = event.currentTarget;
    var exchange = resizer.parentNode;
    var request = exchange.querySelector(config.requestSelector);
    var response = exchange.querySelector(config.responseSelector);

    var requestHeight = request.getBoundingClientRect().height;
    var responseHeight = response.getBoundingClientRect().height;
    var responseMinimum = parseFloat(getComputedStyle(response).minHeight);

    // .. each side keeps at least the minimum height its styles give it ..
    drag.isDragging = true;
    drag.startY = event.clientY;
    drag.startHeight = requestHeight;
    drag.totalHeight = requestHeight + responseHeight;
    drag.minimumHeight = parseFloat(getComputedStyle(request).minHeight);
    drag.maximumHeight = drag.totalHeight - responseMinimum;
    drag.share = requestHeight / drag.totalHeight;

    // .. and capturing the pointer keeps the drag going when it leaves the handle.
    resizer.setPointerCapture(event.pointerId);
    document.body.className = config.resizingClass;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.exchange.onPointerMove = function(event) {

    var drag = zatoConsole.exchange.drag;

    if(!drag.isDragging) {
        return;
    }

    var requestedHeight = drag.startHeight + event.clientY - drag.startY;
    var atLeastMinimum = Math.max(drag.minimumHeight, requestedHeight);
    var height = Math.min(drag.maximumHeight, atLeastMinimum);

    drag.share = height / drag.totalHeight;
    zatoConsole.exchange.applyShare(drag.share);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.exchange.onPointerUp = function(event) {

    var config = zatoConsole.exchange.config;
    var drag = zatoConsole.exchange.drag;

    if(!drag.isDragging) {
        return;
    }

    drag.isDragging = false;

    event.currentTarget.releasePointerCapture(event.pointerId);
    document.body.className = config.idleClass;

    localStorage.setItem(config.storageKey, drag.share);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.exchange.init();
