'use strict';

// The order of the navigation entries, which each user sets by dragging them and which the browser keeps.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var navigation = {};

navigation.config = {
    storageKey: 'navigation-order',
    draggingClass: 'navigation-item-dragging'
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

navigation.init = function() {

    var list = navigation.list();
    var entries = list.querySelectorAll('.navigation-item');

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
