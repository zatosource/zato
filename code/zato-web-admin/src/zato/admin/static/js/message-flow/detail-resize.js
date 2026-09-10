
// /////////////////////////////////////////////////////////////////////////////

// Message flow - how the pane under the drawing shares the page with the drawing,
// by the bar over it.

(function($) {

var detail = $.fn.zato.message_flow.detail;

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
