
// /////////////////////////////////////////////////////////////////////////////

// Message flow - how the pane under the drawing shares its room. The bar between
// the pane's two sides shares the pane's width between the request and the reply,
// and the bar over the pane shares the page between the drawing and the pane.

(function($) {

var detail = $.fn.zato.message_flow.detail;

// /////////////////////////////////////////////////////////////////////////////

// How the two sides share the pane - the remembered share put back on every
// opening, the default an even split
detail.applySplit = function(split) {
    var kept = window.localStorage.getItem(detail.config.splitStorageKey);
    var percent = detail.config.splitDefaultPercent;

    if (kept !== null) {
        percent = Number(kept);
    }

    split.style.setProperty('--message-flow-detail-split', percent + '%');
};

// /////////////////////////////////////////////////////////////////////////////

// The bar between the two sides - a press and a pull shares the pane's width
// between the request and the reply, neither side ever pushed below its least
// share. Wired once, through the document, because the bar itself is built
// anew with every opened node.
detail.wireSplit = function() {
    var config = detail.config;

    var isPressed = false;
    var split = null;
    var splitBar = null;

    document.addEventListener('mousedown', function(event) {

        // Only the main button grabs the bar
        if (event.button !== 0) {
            return;
        }

        if (!event.target.classList.contains('message-flow-detail-split-bar')) {
            return;
        }

        isPressed = true;
        splitBar = event.target;
        split = splitBar.parentElement;

        splitBar.classList.add('message-flow-detail-splitting');

        // The pull must not start selecting the page's text
        event.preventDefault();
    });

    window.addEventListener('mousemove', function(event) {
        if (!isPressed) {
            return;
        }

        var rect = split.getBoundingClientRect();
        var percent = (event.clientX - rect.left) / rect.width * 100;

        if (percent < config.splitMinPercent) {
            percent = config.splitMinPercent;
        }

        if (percent > 100 - config.splitMinPercent) {
            percent = 100 - config.splitMinPercent;
        }

        split.style.setProperty('--message-flow-detail-split', percent + '%');
        window.localStorage.setItem(config.splitStorageKey, String(Math.round(percent)));
    });

    window.addEventListener('mouseup', function() {
        if (isPressed) {
            isPressed = false;
            splitBar.classList.remove('message-flow-detail-splitting');
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

// The bar between the drawing and the pane - a press on it and a pull shares
// the page between the two, neither side ever pushed below what it needs.
// The pulling itself is the shared pane split bar, this is where the page's
// own limits, its snap and its shut state meet it.
detail.wireResize = function() {
    var config = detail.config;

    var page = document.querySelector(config.pageSelector);

    paneSplit.init({
        bar: document.getElementById(config.resizeBarId),
        pane: detail.host(),
        container: page,
        axis: 'y',
        minSize: config.detailMinHeight,
        minOther: config.canvasMinHeight,
        snapSize: config.detailSnapHeight,
        activeClass: config.resizeActiveClass,

        // The pane's height lives in the page's own variable, its stylesheet
        // reads the layout out of it
        apply: function(height) {
            page.style.setProperty('--message-flow-detail-height', height + 'px');
        },

        // With no height the pane is fully gone, its border included - a shut
        // pane must not linger as a seam over the page's bottom edge
        onSnap: function(isShut) {
            page.classList.toggle('message-flow-detail-shut', isShut);
        },
    });
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
