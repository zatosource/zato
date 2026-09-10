
// /////////////////////////////////////////////////////////////////////////////

// Message flow - the drawing's controls, the same three the sequence diagrams
// in the docs wear, standing in the canvas's top-right corner the way they do
// there: closer, further off, and the whole screen given to the page. Full
// screen is the browser's own - the page alone fills the screen, the top menu,
// the logo and the navigation all gone with the browser's chrome - and the
// same button, or Escape, brings everything back.

$.fn.zato.message_flow.controls = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var kit = $.fn.zato.dashboard_kit;
var controls = $.fn.zato.message_flow.controls;

// /////////////////////////////////////////////////////////////////////////////

controls.config = {

    hostId: 'message-flow-controls',
    pageSelector: '.message-flow-page',

    // The class the page wears while it has the whole screen
    fullscreenClass: 'message-flow-fullscreen',

    // What each control says of itself on hover
    closerLabel: 'Closer',
    furtherLabel: 'Further off',
    fullscreenLabel: 'Full screen',
    leaveFullscreenLabel: 'Leave full screen',

    // The strokes of the icons, drawn in a 16 by 16 box the way the docs draw them -
    // a plus, a minus, four corners reaching out and the same four corners reaching in
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
    return document.getElementById(controls.config.hostId);
};

// /////////////////////////////////////////////////////////////////////////////

// One icon of the controls, its stroke in the button's own colour
controls.newIcon = function(pathData) {
    var config = controls.config;

    var icon = kit.draw.createElement('svg');
    icon.setAttribute('viewBox', config.iconViewBox);
    icon.setAttribute('width', String(config.iconSize));
    icon.setAttribute('height', String(config.iconSize));
    icon.setAttribute('class', 'message-flow-control-icon');

    var path = kit.draw.createElement('path');
    path.setAttribute('d', pathData);
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', 'currentColor');
    path.setAttribute('stroke-width', String(config.iconStrokeWidth));
    path.setAttribute('stroke-linecap', 'round');
    path.setAttribute('stroke-linejoin', 'round');
    icon.appendChild(path);

    return icon;
};

// /////////////////////////////////////////////////////////////////////////////

// One button of the controls - its icon and what it says of itself
controls.newButton = function(pathData, label) {
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'message-flow-control';
    button.title = label;
    button.appendChild(controls.newIcon(pathData));

    return button;
};

// /////////////////////////////////////////////////////////////////////////////

// The full screen control brought to the state the page is in - reaching out
// with the page in its place, reaching in with the page over everything
controls.updateFullscreenButton = function(button) {
    var config = controls.config;

    button.textContent = '';

    if (controls.isFullscreen) {
        button.title = config.leaveFullscreenLabel;
        button.appendChild(controls.newIcon(config.icons.leaveFullscreen));
    }
    else {
        button.title = config.fullscreenLabel;
        button.appendChild(controls.newIcon(config.icons.fullscreen));
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The page asked to fill the screen, or the screen given back - the browser
// answers with a fullscreenchange either way, which is where the page follows
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

// The page brought to whatever the browser says of the screen - the button
// and the page's own class alike - whether the button or Escape asked for it
controls.onFullscreenChange = function() {
    var config = controls.config;
    var page = document.querySelector(config.pageSelector);

    controls.isFullscreen = document.fullscreenElement === page;

    page.classList.toggle(config.fullscreenClass, controls.isFullscreen);
    controls.updateFullscreenButton(controls.host().querySelector('.message-flow-control-fullscreen'));
};

// /////////////////////////////////////////////////////////////////////////////

controls.init = function() {
    var config = controls.config;
    var drawing = $.fn.zato.message_flow.drawing;
    var host = controls.host();

    var fullscreen = controls.newButton(config.icons.fullscreen, config.fullscreenLabel);
    fullscreen.classList.add('message-flow-control-fullscreen');
    host.appendChild(fullscreen);

    fullscreen.addEventListener('click', function(event) {
        controls.setFullscreen(!controls.isFullscreen);
        event.currentTarget.blur();
    });

    document.addEventListener('fullscreenchange', controls.onFullscreenChange);

    var closer = controls.newButton(config.icons.closer, config.closerLabel);
    host.appendChild(closer);

    closer.addEventListener('click', function(event) {
        drawing.zoom.step(true);
        event.currentTarget.blur();
    });

    var further = controls.newButton(config.icons.further, config.furtherLabel);
    host.appendChild(further);

    further.addEventListener('click', function(event) {
        drawing.zoom.step(false);
        event.currentTarget.blur();
    });
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
