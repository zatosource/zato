'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

// A panel that shows the lines of a running job as they arrive. The host creates it with a container
// and feeds it lines, each a plain string or an object with text, kind (null, 'ok' or 'error'), time
// (epoch seconds, a Date or an ISO string) and id. The panel follows its last line until the user scrolls
// away from the bottom and resumes once they scroll back, keeps only so many lines, and copies all of
// them with a button in its header. Its state - idle, live, done or failed - drives the dot in the header
// and the colour of the progress bar. The theme is light or dark.

var defaults = {
    theme: 'light',
    source: '',
    copyLabel: 'Copy',
    copiedLabel: 'Copied',
    copiedShownMs: 1200,
    linesKept: 500,
    linesAnimated: 3,
    scrollStickiness: 40,
    isHidden: false,
    hasProgressBar: false,
    hasTime: true,
};

// ////////////////////////////////////////////////////////////////////////

function padNumber(value) {
    return value < 10 ? '0' + value : '' + value;
}

// ////////////////////////////////////////////////////////////////////////

function toDate(time) {

    if(time === null || time === undefined || time === '') {
        return null;
    }

    if(time instanceof Date) {
        return time;
    }

    if(typeof time === 'number') {
        return new Date(time * 1000);
    }

    var date = new Date(time);
    return isNaN(date.getTime()) ? null : date;
}

// ////////////////////////////////////////////////////////////////////////

function formatTime(time) {

    var date = toDate(time);

    if(date === null) {
        return '';
    }

    return padNumber(date.getHours()) + ':' + padNumber(date.getMinutes()) + ':' + padNumber(date.getSeconds());
}

// ////////////////////////////////////////////////////////////////////////

function toLine(line) {

    if(typeof line === 'string') {
        return {id: null, time: null, text: line, kind: null};
    }

    return {
        id: line.id === undefined ? null : line.id,
        time: line.time === undefined ? null : line.time,
        text: line.text === undefined ? '' : line.text,
        kind: line.kind === undefined ? null : line.kind,
    };
}

// ////////////////////////////////////////////////////////////////////////

function createElement(tagName, className, parent) {

    var element = document.createElement(tagName);
    element.className = className;
    parent.appendChild(element);

    return element;
}

// ////////////////////////////////////////////////////////////////////////

function ProgressLog(config) {

    var key;

    this.config = {};

    for(key in defaults) {
        this.config[key] = defaults[key];
    }

    for(key in config) {
        this.config[key] = config[key];
    }

    this.lines = [];
    this.lastId = null;
    this.isFollowed = true;
    this.copiedTimer = null;

    this.build();
}

// ////////////////////////////////////////////////////////////////////////

ProgressLog.prototype.build = function() {

    var config = this.config;
    var root = config.container;

    root.classList.add('progress-log');
    root.setAttribute('data-theme', config.theme);
    root.setAttribute('data-state', 'idle');
    root.setAttribute('data-hidden', config.isHidden ? 'true' : 'false');

    var header = createElement('div', 'progress-log-header', root);

    this.live = createElement('span', 'progress-log-live', header);
    this.source = createElement('span', 'progress-log-source', header);
    this.percent = createElement('span', 'progress-log-percent', header);

    this.copyButton = createElement('button', 'progress-log-copy', header);
    this.copyButton.type = 'button';
    this.copyButton.textContent = config.copyLabel;

    this.bar = createElement('div', 'progress-log-bar', root);
    this.bar.setAttribute('data-hidden', config.hasProgressBar ? 'false' : 'true');
    this.barFill = createElement('div', 'progress-log-bar-fill', this.bar);

    this.linesElement = createElement('div', 'progress-log-lines', root);

    this.setSource(config.source);

    this.copyButton.addEventListener('click', this.copy.bind(this));
    this.linesElement.addEventListener('scroll', this.onScroll.bind(this));

    // The panel changes its size as the rest of the page fills in and as fonts load.
    if(window.ResizeObserver) {
        new ResizeObserver(this.follow.bind(this)).observe(this.linesElement);
    }
};

// ////////////////////////////////////////////////////////////////////////

ProgressLog.prototype.show = function() {
    this.config.container.setAttribute('data-hidden', 'false');
    this.follow();
};

// ////////////////////////////////////////////////////////////////////////

ProgressLog.prototype.hide = function() {
    this.config.container.setAttribute('data-hidden', 'true');
};

// ////////////////////////////////////////////////////////////////////////

ProgressLog.prototype.setSource = function(text) {
    this.source.textContent = text;
};

// ////////////////////////////////////////////////////////////////////////

ProgressLog.prototype.setTheme = function(theme) {
    this.config.theme = theme;
    this.config.container.setAttribute('data-theme', theme);
};

// ////////////////////////////////////////////////////////////////////////

// One of idle, live, done or failed.
ProgressLog.prototype.setState = function(state) {
    this.config.container.setAttribute('data-state', state);
};

// ////////////////////////////////////////////////////////////////////////

// A fraction from 0 to 1 fills the bar and shows the percentage, null hides both.
ProgressLog.prototype.setProgress = function(fraction) {

    if(fraction === null) {
        this.bar.setAttribute('data-hidden', 'true');
        this.percent.textContent = '';
        return;
    }

    var bounded = Math.max(0, Math.min(1, fraction));

    this.bar.setAttribute('data-hidden', 'false');
    this.barFill.style.width = (bounded * 100) + '%';
    this.percent.textContent = Math.floor(bounded * 100) + '%';
};

// ////////////////////////////////////////////////////////////////////////

ProgressLog.prototype.append = function(lines) {

    var config = this.config;
    var container = this.linesElement;

    if(!Array.isArray(lines)) {
        lines = [lines];
    }

    if(lines.length === 0) {
        return;
    }

    var isAnimated = lines.length <= config.linesAnimated;

    for(var lineIndex = 0; lineIndex < lines.length; lineIndex++) {

        var line = toLine(lines[lineIndex]);
        this.lines.push(line);

        var row = createElement('div', 'progress-log-line', container);
        if(line.kind !== null) {
            row.setAttribute('data-kind', line.kind);
        }

        var time = createElement('span', 'progress-log-line-time', row);
        time.textContent = config.hasTime ? formatTime(line.time) : '';

        var text = createElement('span', 'progress-log-line-text', row);
        text.textContent = line.text;

        if(isAnimated && row.animate) {
            row.animate([
                {opacity: 0, transform: 'translateY(6px)'},
                {opacity: 1, transform: 'none'}
            ], {duration: 300, easing: 'ease-out'});
        }

        if(line.id !== null) {
            this.lastId = line.id;
        }
    }

    while(container.childElementCount > config.linesKept) {
        container.firstElementChild.remove();
    }

    while(this.lines.length > config.linesKept) {
        this.lines.shift();
    }

    this.follow();
};

// ////////////////////////////////////////////////////////////////////////

ProgressLog.prototype.clear = function() {
    this.lines = [];
    this.lastId = null;
    this.isFollowed = true;
    this.linesElement.replaceChildren();
    this.setProgress(null);
    this.setState('idle');
};

// ////////////////////////////////////////////////////////////////////////

// Only the user's own scrolling decides whether the panel follows its last line,
// a scroll back to the bottom resumes it, and changes in the layout never stop it.
ProgressLog.prototype.onScroll = function() {

    var container = this.linesElement;
    var distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight;

    this.isFollowed = distanceFromBottom < this.config.scrollStickiness;
};

// ////////////////////////////////////////////////////////////////////////

ProgressLog.prototype.follow = function() {

    var container = this.linesElement;

    if(this.isFollowed) {
        container.scrollTop = container.scrollHeight;
    }
};

// ////////////////////////////////////////////////////////////////////////

ProgressLog.prototype.getText = function() {

    var out = [];

    for(var lineIndex = 0; lineIndex < this.lines.length; lineIndex++) {
        var line = this.lines[lineIndex];
        var time = this.config.hasTime ? formatTime(line.time) : '';
        out.push(time ? time + '  ' + line.text : line.text);
    }

    return out.join('\n');
};

// ////////////////////////////////////////////////////////////////////////

ProgressLog.prototype.copy = function() {

    var self = this;

    navigator.clipboard.writeText(this.getText()).then(function() {
        self.confirmCopied();
    });
};

// ////////////////////////////////////////////////////////////////////////

ProgressLog.prototype.confirmCopied = function() {

    var self = this;
    var config = this.config;

    if(config.onCopied) {
        config.onCopied(this.copyButton);
        return;
    }

    this.copyButton.textContent = config.copiedLabel;

    if(this.copiedTimer) {
        clearTimeout(this.copiedTimer);
    }

    this.copiedTimer = setTimeout(function() {
        self.copyButton.textContent = config.copyLabel;
        self.copiedTimer = null;
    }, config.copiedShownMs);
};

// ////////////////////////////////////////////////////////////////////////

window.progressLog = {

    create: function(config) {
        return new ProgressLog(config);
    },

    formatTime: formatTime,
};

// ////////////////////////////////////////////////////////////////////////

})();
