'use strict';

// The order of the navigation entries, which each user sets by dragging them and which the browser keeps,
// and the width of the navigation pane, which the line at its right edge is dragged to set, and whether the pane
// is collapsed, which the toggle at its top or a drag close to its left edge sets. The browser keeps both in cookies,
// so that the server renders each next page with the same pane.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var navigation = {};

navigation.config = {
    storageKey: 'navigation-order',
    draggingClass: 'navigation-item-dragging',
    resizingClass: 'navigation-resizing',
    collapsedClass: 'navigation-collapsed',
    widthAttribute: 'data-width',
    widthCookieAttribute: 'data-width-cookie',
    collapsedCookieAttribute: 'data-collapsed-cookie',
    collapsedValueAttribute: 'data-collapsed-value',
    expandedValue: '0',
    cookieMaxAge: 31536000,
    minimumWidth: 160,
    maximumWidth: 480,

    // Narrower than this, the pane snaps shut while it is dragged, and it opens again once dragged past it
    snapWidth: 100
};

navigation.dragged = null;

// ////////////////////////////////////////////////////////////////////////

navigation.list = function() {
    var out = document.getElementById('navigation-list');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Puts the entries in the order kept from an earlier drag, entries the kept order does not name going last.
navigation.restore = function() {

    var stored = window.localStorage.getItem(navigation.config.storageKey);

    // Nothing is kept until the entries are dragged for the first time
    if (stored === null) {
        return;
    }

    var slugs = JSON.parse(stored);
    var list = navigation.list();
    var entries = list.querySelectorAll('.navigation-item');
    var ordered = [];

    for (var slugIndex = 0; slugIndex < slugs.length; slugIndex++) {
        var named = list.querySelector('[data-slug="' + slugs[slugIndex] + '"]');
        if (named) {
            ordered.push(named);
        }
    }

    for (var entryIndex = 0; entryIndex < entries.length; entryIndex++) {
        if (ordered.indexOf(entries[entryIndex]) === -1) {
            ordered.push(entries[entryIndex]);
        }
    }

    for (var orderedIndex = 0; orderedIndex < ordered.length; orderedIndex++) {
        list.appendChild(ordered[orderedIndex]);
    }
};

// ////////////////////////////////////////////////////////////////////////

navigation.save = function() {

    var entries = navigation.list().querySelectorAll('.navigation-item');
    var slugs = [];

    for (var entryIndex = 0; entryIndex < entries.length; entryIndex++) {
        slugs.push(entries[entryIndex].getAttribute('data-slug'));
    }

    window.localStorage.setItem(navigation.config.storageKey, JSON.stringify(slugs));
};

// ////////////////////////////////////////////////////////////////////////

navigation.onDragStart = function(event) {

    navigation.dragged = event.currentTarget;
    navigation.dragged.classList.add(navigation.config.draggingClass);

    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', '');
};

// ////////////////////////////////////////////////////////////////////////

// The dragged entry goes above the entry under the pointer when the pointer is in its upper half, below it otherwise.
navigation.onDragOver = function(event) {

    event.preventDefault();

    var target = event.target.closest('.navigation-item');

    if (target === null) {
        return;
    }

    if (target === navigation.dragged) {
        return;
    }

    var list = navigation.list();
    var rect = target.getBoundingClientRect();
    var middle = rect.top + rect.height / 2;

    if (event.clientY < middle) {
        list.insertBefore(navigation.dragged, target);
    }
    else {
        list.insertBefore(navigation.dragged, target.nextSibling);
    }
};

// ////////////////////////////////////////////////////////////////////////

navigation.onDragEnd = function() {
    navigation.dragged.classList.remove(navigation.config.draggingClass);
    navigation.dragged = null;
    navigation.save();
};

// ////////////////////////////////////////////////////////////////////////

navigation.pane = function() {
    var out = document.getElementById('navigation');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

navigation.isCollapsed = function() {
    var out = navigation.pane().classList.contains(navigation.config.collapsedClass);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A collapsed pane takes the width its class gives it, an open one the width it was last given, if it was ever given one.
navigation.setCollapsed = function(isCollapsed) {

    var pane = navigation.pane();
    var width = pane.getAttribute(navigation.config.widthAttribute);

    pane.classList.toggle(navigation.config.collapsedClass, isCollapsed);

    if (isCollapsed) {
        pane.style.width = '';
    }
    else if (width !== '') {
        pane.style.width = width + 'px';
    }
};

// ////////////////////////////////////////////////////////////////////////

navigation.setWidth = function(width) {

    var pane = navigation.pane();

    pane.setAttribute(navigation.config.widthAttribute, width);
    pane.style.width = width + 'px';
};

// ////////////////////////////////////////////////////////////////////////

navigation.writeCookie = function(nameAttribute, value) {

    var name = navigation.pane().getAttribute(nameAttribute);
    var suffix = '; path=/; max-age=' + navigation.config.cookieMaxAge + '; samesite=strict';

    document.cookie = name + '=' + value + suffix;
};

// ////////////////////////////////////////////////////////////////////////

// The width and the collapsed state are kept for the server, which renders every next page with them.
navigation.saveLayout = function() {

    var pane = navigation.pane();
    var width = pane.getAttribute(navigation.config.widthAttribute);
    var collapsedValue = navigation.config.expandedValue;

    if (navigation.isCollapsed()) {
        collapsedValue = pane.getAttribute(navigation.config.collapsedValueAttribute);
    }

    navigation.writeCookie(navigation.config.collapsedCookieAttribute, collapsedValue);

    // A pane never resized has no width of its own to keep
    if (width !== '') {
        navigation.writeCookie(navigation.config.widthCookieAttribute, width);
    }
};

// ////////////////////////////////////////////////////////////////////////

navigation.onToggleClick = function() {
    navigation.setCollapsed(!navigation.isCollapsed());
    navigation.saveLayout();
};

// ////////////////////////////////////////////////////////////////////////

// The line at the right edge of the pane gives the pane the width from its left edge to the pointer,
// and a pointer closer to that edge than the snap width shuts the pane until it is dragged past it again.
navigation.startResize = function(event) {

    event.preventDefault();

    var pane = navigation.pane();
    var minimum = navigation.config.minimumWidth;
    var maximum = navigation.config.maximumWidth;

    document.body.classList.add(navigation.config.resizingClass);

    var onMove = function(moveEvent) {

        var rect = pane.getBoundingClientRect();
        var width = Math.round(moveEvent.clientX - rect.left);
        var isCollapsed = width < navigation.config.snapWidth;

        navigation.setCollapsed(isCollapsed);

        if (!isCollapsed) {
            width = Math.max(minimum, Math.min(maximum, width));
            navigation.setWidth(width);
        }
    };

    var onUp = function() {
        document.body.classList.remove(navigation.config.resizingClass);
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
        navigation.saveLayout();
    };

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
};

// ////////////////////////////////////////////////////////////////////////

navigation.init = function() {

    var list = navigation.list();
    var entries = list.querySelectorAll('.navigation-item');

    document.getElementById('navigation-handle').addEventListener('mousedown', navigation.startResize);
    document.getElementById('navigation-toggle').addEventListener('click', navigation.onToggleClick);

    navigation.restore();

    for (var entryIndex = 0; entryIndex < entries.length; entryIndex++) {
        entries[entryIndex].addEventListener('dragstart', navigation.onDragStart);
        entries[entryIndex].addEventListener('dragend', navigation.onDragEnd);
    }

    list.addEventListener('dragover', navigation.onDragOver);
    list.addEventListener('drop', function(event) {
        event.preventDefault();
    });
};

// ////////////////////////////////////////////////////////////////////////

portal.navigation = navigation;

document.addEventListener('DOMContentLoaded', navigation.init);

// ////////////////////////////////////////////////////////////////////////

})();
