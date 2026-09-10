
// /////////////////////////////////////////////////////////////////////////////

// Message flow - the bar between the drawing and the detail pane.

(function($) {

var detail = $.fn.zato.message_flow.detail;

// /////////////////////////////////////////////////////////////////////////////

// The pane's height is published as a CSS variable on the page, which is what pane.css lays the pane out by.
detail.wireResize = function() {
    var config = detail.config;

    var page = document.querySelector(config.pageSelector);
    var bar = document.getElementById(config.resizeBarId);
    var pane = detail.host();

    var applyHeight = function(height) {
        var heightValue = height + 'px';
        page.style.setProperty('--message-flow-detail-height', heightValue);
    };

    var onSnap = function(isShut) {
        page.classList.toggle('message-flow-detail-shut', isShut);
    };

    var splitConfig = {
        bar: bar,
        pane: pane,
        container: page,
        axis: 'y',
        minSize: config.detailMinHeight,
        minOther: config.canvasMinHeight,
        snapSize: config.detailSnapHeight,
        activeClass: config.resizeActiveClass,
        apply: applyHeight,
        onSnap: onSnap
    };

    paneSplit.init(splitConfig);
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
