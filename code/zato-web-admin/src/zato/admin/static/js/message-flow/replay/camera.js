
// /////////////////////////////////////////////////////////////////////////////

// Message flow replay - the camera. On a long drawing the pass walks off the
// screen, so the canvas drifts after it - each newly lit node pulls the room
// toward itself the way gravity pulls, the drift strongest at the start of the
// way and dying off as it arrives, never a jump. The reader's own hand always
// wins - grabbing or wheeling the canvas lets the pull go at once.

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var replay = $.fn.zato.message_flow.replay;

// /////////////////////////////////////////////////////////////////////////////

replay.cameraConfig = {

    // How much of the way left to the node the drift covers per frame - the
    // pull of the gravitation, and under how far off the drift is over
    pullShare: 0.08,
    restDistance: 0.5
};

// /////////////////////////////////////////////////////////////////////////////

replay.cameraState = {

    // Where the drift is headed, in the canvas' own scroll coordinates
    targetLeft: 0,
    targetTop: 0,

    frameHandle: null
};

// /////////////////////////////////////////////////////////////////////////////

replay.stopCamera = function() {
    var cameraState = replay.cameraState;

    if (cameraState.frameHandle !== null) {
        window.cancelAnimationFrame(cameraState.frameHandle);
        cameraState.frameHandle = null;
    }
};

// /////////////////////////////////////////////////////////////////////////////

// One frame of the drift - the canvas covers a share of the way left, so the
// closer it gets the softer it lands
replay.cameraStep = function() {
    var config = replay.cameraConfig;
    var cameraState = replay.cameraState;
    var canvas = $.fn.zato.message_flow.drawing.canvas();

    var leftLeft = cameraState.targetLeft - canvas.scrollLeft;
    var topLeft = cameraState.targetTop - canvas.scrollTop;

    canvas.scrollLeft += leftLeft * config.pullShare;
    canvas.scrollTop += topLeft * config.pullShare;

    // Close enough is arrived - anything further would be invisible
    if (Math.abs(leftLeft) < config.restDistance && Math.abs(topLeft) < config.restDistance) {
        cameraState.frameHandle = null;
        return;
    }

    cameraState.frameHandle = window.requestAnimationFrame(replay.cameraStep);
};

// /////////////////////////////////////////////////////////////////////////////

// The node the pass just lit becomes where the room drifts - the drift aims
// the node at the middle of the canvas, and a drift already under way simply
// bends toward the new node
replay.followNode = function(nodeElement) {
    var cameraState = replay.cameraState;
    var canvas = $.fn.zato.message_flow.drawing.canvas();

    var nodeRect = nodeElement.getBoundingClientRect();
    var canvasRect = canvas.getBoundingClientRect();

    var nodeCenterX = nodeRect.left + nodeRect.width / 2;
    var nodeCenterY = nodeRect.top + nodeRect.height / 2;

    var canvasCenterX = canvasRect.left + canvasRect.width / 2;
    var canvasCenterY = canvasRect.top + canvasRect.height / 2;

    cameraState.targetLeft = canvas.scrollLeft + nodeCenterX - canvasCenterX;
    cameraState.targetTop = canvas.scrollTop + nodeCenterY - canvasCenterY;

    if (cameraState.frameHandle === null) {
        cameraState.frameHandle = window.requestAnimationFrame(replay.cameraStep);
    }
};

// /////////////////////////////////////////////////////////////////////////////

replay.initCamera = function() {
    var canvas = $.fn.zato.message_flow.drawing.canvas();

    // The reader's own hand on the canvas - a grab or a wheel - lets the
    // pull go at once, so the drift never fights the reader
    canvas.addEventListener('mousedown', replay.stopCamera);
    canvas.addEventListener('wheel', replay.stopCamera, {passive: true});
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
