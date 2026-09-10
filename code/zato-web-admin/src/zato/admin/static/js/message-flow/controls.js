
// /////////////////////////////////////////////////////////////////////////////

// Message flow - the zoom and full screen controls over the canvas.

$.fn.zato.message_flow.controls = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var dashboardKit = $.fn.zato.dashboard_kit;
var controls = $.fn.zato.message_flow.controls;

// /////////////////////////////////////////////////////////////////////////////

controls.config = {

    hostIdentifier: 'message-flow-controls',
    pageSelector: '.message-flow-page',
    fullscreenButtonSelector: '.message-flow-control-fullscreen',

    fullscreenClass: 'message-flow-fullscreen',

    buttonClass: 'message-flow-control',
    fullscreenButtonClass: 'message-flow-control message-flow-control-fullscreen',
    iconClass: 'message-flow-control-icon',

    closerLabel: 'Closer',
    furtherLabel: 'Further off',
    fullscreenLabel: 'Full screen',
    leaveFullscreenLabel: 'Leave full screen',

    iconViewBox: '0 0 16 16',
    iconSize: 16,
    iconStrokeWidth: 1.5,

    icons: {
        closer: 'M8 3v10M3 8h10',
        further: 'M3 8h10',
        fullscreen: 'M6 2H3a1 1 0 0 0-1 1v3M10 2h3a1 1 0 0 1 1 1v3M6 14H3a1 1 0 0 1-1-1v-3M10 14h3a1 1 0 0 0 1-1v-3',
        leaveFullscreen: 'M2 6h3a1 1 0 0 0 1-1V2M14 6h-3a1 1 0 0 1-1-1V2M2 10h3a1 1 0 0 1 1 1v3M14 10h-3a1 1 0 0 0-1 1v3'
    }
};

// /////////////////////////////////////////////////////////////////////////////

controls.isFullscreen = false;

// /////////////////////////////////////////////////////////////////////////////

controls.host = function() {
    var out = document.getElementById(controls.config.hostIdentifier);
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

controls.newIcon = function(pathData) {
    var config = controls.config;

    var icon = dashboardKit.draw.createElement('svg');
    icon.setAttribute('viewBox', config.iconViewBox);
    icon.setAttribute('width', config.iconSize);
    icon.setAttribute('height', config.iconSize);
    icon.setAttribute('class', config.iconClass);

    var path = dashboardKit.draw.createElement('path');
    path.setAttribute('d', pathData);
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', 'currentColor');
    path.setAttribute('stroke-width', config.iconStrokeWidth);
    path.setAttribute('stroke-linecap', 'round');
    path.setAttribute('stroke-linejoin', 'round');
    icon.appendChild(path);

    var out = icon;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

controls.newButton = function(className, pathData, label) {
    var icon = controls.newIcon(pathData);

    var button = document.createElement('button');
    button.type = 'button';
    button.className = className;
    button.setAttribute('aria-label', label);
    button.appendChild(icon);

    var out = button;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

controls.updateFullscreenButton = function(button) {
    var config = controls.config;

    var label = config.fullscreenLabel;
    var pathData = config.icons.fullscreen;

    if (controls.isFullscreen) {
        label = config.leaveFullscreenLabel;
        pathData = config.icons.leaveFullscreen;
    }

    var icon = controls.newIcon(pathData);

    button.textContent = '';
    button.setAttribute('aria-label', label);
    button.appendChild(icon);
};

// /////////////////////////////////////////////////////////////////////////////

// Both branches end in a fullscreenchange event, which is where the page's own state follows.
controls.setFullscreen = function(isFullscreen) {
    var page = document.querySelector(controls.config.pageSelector);

    if (isFullscreen) {
        page.requestFullscreen();
    }
    else {
        document.exitFullscreen();
    }
};

// /////////////////////////////////////////////////////////////////////////////

controls.onFullscreenChange = function() {
    var config = controls.config;

    var page = document.querySelector(config.pageSelector);
    var host = controls.host();
    var fullscreenButton = host.querySelector(config.fullscreenButtonSelector);

    var isFullscreen = document.fullscreenElement === page;
    controls.isFullscreen = isFullscreen;

    page.classList.toggle(config.fullscreenClass, isFullscreen);
    controls.updateFullscreenButton(fullscreenButton);
};

// /////////////////////////////////////////////////////////////////////////////

controls.init = function() {
    var config = controls.config;
    var drawing = $.fn.zato.message_flow.drawing;
    var host = controls.host();

    var fullscreen = controls.newButton(config.fullscreenButtonClass, config.icons.fullscreen, config.fullscreenLabel);
    host.appendChild(fullscreen);

    fullscreen.addEventListener('click', function(event) {
        var wantsFullscreen = !controls.isFullscreen;

        controls.setFullscreen(wantsFullscreen);
        event.currentTarget.blur();
    });

    document.addEventListener('fullscreenchange', controls.onFullscreenChange);

    var closer = controls.newButton(config.buttonClass, config.icons.closer, config.closerLabel);
    host.appendChild(closer);

    closer.addEventListener('click', function(event) {
        drawing.zoom.step(true);
        event.currentTarget.blur();
    });

    var further = controls.newButton(config.buttonClass, config.icons.further, config.furtherLabel);
    host.appendChild(further);

    further.addEventListener('click', function(event) {
        drawing.zoom.step(false);
        event.currentTarget.blur();
    });
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
