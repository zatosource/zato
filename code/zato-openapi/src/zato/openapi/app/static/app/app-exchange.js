zatoApp.exchange = {};

zatoApp.exchange.config = {
    requestSelector: '.app-operation-request',
    responseSelector: '.app-operation-response',
    resizerClass: 'app-exchange-resizer',
    gripClass: 'app-exchange-grip',
    resizeLabel: 'Resize',
    resizingClass: 'app-body app-resizing-exchange',
    idleClass: 'app-body',
    storageKey: 'zato.openapi.app.request.share',
    requestShareVariable: '--app-request-share',
    responseShareVariable: '--app-response-share',
    primaryButton: 0,
};

zatoApp.exchange.drag = {
    isDragging: false,
    startY: 0,
    startHeight: 0,
    minimumHeight: 0,
    maximumHeight: 0,
    totalHeight: 0,
    share: 0,
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.exchange.init = function() {

    // The share of an earlier visit applies to every operation, localStorage returning null for a key never stored
    var stored = localStorage.getItem(zatoApp.exchange.config.storageKey);

    if(stored !== null) {
        zatoApp.exchange.applyShare(Number(stored));
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.exchange.applyShare = function(share) {

    var config = zatoApp.exchange.config;
    var style = document.documentElement.style;

    // The request and the response grow in proportion to their shares, which always add up to one
    style.setProperty(config.requestShareVariable, share);
    style.setProperty(config.responseShareVariable, 1 - share);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.exchange.buildResizer = function() {

    var config = zatoApp.exchange.config;

    var resizer = zatoApp.panels.createElement('div', config.resizerClass);
    var grip = zatoApp.panels.createElement('span', config.gripClass);

    resizer.setAttribute('role', 'separator');
    resizer.setAttribute('aria-orientation', 'horizontal');
    resizer.setAttribute('aria-label', config.resizeLabel);

    resizer.addEventListener('pointerdown', zatoApp.exchange.onPointerDown);
    resizer.addEventListener('pointermove', zatoApp.exchange.onPointerMove);
    resizer.addEventListener('pointerup', zatoApp.exchange.onPointerUp);
    resizer.addEventListener('pointercancel', zatoApp.exchange.onPointerUp);

    resizer.appendChild(grip);

    return resizer;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.exchange.onPointerDown = function(event) {

    var config = zatoApp.exchange.config;
    var drag = zatoApp.exchange.drag;

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

zatoApp.exchange.onPointerMove = function(event) {

    var drag = zatoApp.exchange.drag;

    if(!drag.isDragging) {
        return;
    }

    var requestedHeight = drag.startHeight + event.clientY - drag.startY;
    var atLeastMinimum = Math.max(drag.minimumHeight, requestedHeight);
    var height = Math.min(drag.maximumHeight, atLeastMinimum);

    drag.share = height / drag.totalHeight;
    zatoApp.exchange.applyShare(drag.share);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.exchange.onPointerUp = function(event) {

    var config = zatoApp.exchange.config;
    var drag = zatoApp.exchange.drag;

    if(!drag.isDragging) {
        return;
    }

    drag.isDragging = false;

    event.currentTarget.releasePointerCapture(event.pointerId);
    document.body.className = config.idleClass;

    localStorage.setItem(config.storageKey, drag.share);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.exchange.init();
