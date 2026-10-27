zatoPortal.exchange = {};

zatoPortal.exchange.config = {
    requestSelector: '.portal-operation-request',
    responseSelector: '.portal-operation-response',
    resizerClass: 'portal-exchange-resizer',
    gripClass: 'portal-exchange-grip',
    resizeLabel: 'Resize',
    resizingClass: 'portal-body portal-resizing-exchange',
    idleClass: 'portal-body',
    storageKey: 'zato.openapi.portal.request.share',
    requestShareVariable: '--portal-request-share',
    responseShareVariable: '--portal-response-share',
    primaryButton: 0,
};

zatoPortal.exchange.drag = {
    isDragging: false,
    startY: 0,
    startHeight: 0,
    minimumHeight: 0,
    maximumHeight: 0,
    totalHeight: 0,
    share: 0,
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.exchange.init = function() {

    // The share of an earlier visit applies to every operation, localStorage returning null for a key never stored
    var stored = localStorage.getItem(zatoPortal.exchange.config.storageKey);

    if(stored !== null) {
        zatoPortal.exchange.applyShare(Number(stored));
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.exchange.applyShare = function(share) {

    var config = zatoPortal.exchange.config;
    var style = document.documentElement.style;

    // The request and the response grow in proportion to their shares, which always add up to one
    style.setProperty(config.requestShareVariable, share);
    style.setProperty(config.responseShareVariable, 1 - share);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.exchange.buildResizer = function() {

    var config = zatoPortal.exchange.config;

    var resizer = zatoPortal.panels.createElement('div', config.resizerClass);
    var grip = zatoPortal.panels.createElement('span', config.gripClass);

    resizer.setAttribute('role', 'separator');
    resizer.setAttribute('aria-orientation', 'horizontal');
    resizer.setAttribute('aria-label', config.resizeLabel);

    resizer.addEventListener('pointerdown', zatoPortal.exchange.onPointerDown);
    resizer.addEventListener('pointermove', zatoPortal.exchange.onPointerMove);
    resizer.addEventListener('pointerup', zatoPortal.exchange.onPointerUp);
    resizer.addEventListener('pointercancel', zatoPortal.exchange.onPointerUp);

    resizer.appendChild(grip);

    return resizer;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.exchange.onPointerDown = function(event) {

    var config = zatoPortal.exchange.config;
    var drag = zatoPortal.exchange.drag;

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

zatoPortal.exchange.onPointerMove = function(event) {

    var drag = zatoPortal.exchange.drag;

    if(!drag.isDragging) {
        return;
    }

    var requestedHeight = drag.startHeight + event.clientY - drag.startY;
    var atLeastMinimum = Math.max(drag.minimumHeight, requestedHeight);
    var height = Math.min(drag.maximumHeight, atLeastMinimum);

    drag.share = height / drag.totalHeight;
    zatoPortal.exchange.applyShare(drag.share);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.exchange.onPointerUp = function(event) {

    var config = zatoPortal.exchange.config;
    var drag = zatoPortal.exchange.drag;

    if(!drag.isDragging) {
        return;
    }

    drag.isDragging = false;

    event.currentTarget.releasePointerCapture(event.pointerId);
    document.body.className = config.idleClass;

    localStorage.setItem(config.storageKey, drag.share);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.exchange.init();
