// Config tables - what is marked in the file and what is brought on screen in it.
//
// A run of lines can be washed over, the way a marker goes over paper - what a press beside a
// line number would take a copy of while the cursor is there, and what a part of the drawing in
// the Translate column stands for while the cursor is on that. The wash is held for the second
// of those, since the cursor is elsewhere on the page by then and has nothing to say about it.
//
// Bringing a line on screen belongs here as well, both of these being about the file's own box
// rather than about the numbers beside it. A line is either kept on screen, which moves the file
// as little as it takes, or the reader is brought to it, which puts it in the middle of the view.
//
// How tall a line is and what the file keeps above its first one are measured by gutter.js,
// which is where the numbers are laid out by the same figures.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var wash = tables.wash;

// ////////////////////////////////////////////////////////////////////////

wash.config = {

    // The classes the wash wears, and the one that brings it on
    elemClass: 'config-tables-copy-target',
    visibleClass: 'config-tables-copy-target-visible'
};

// ////////////////////////////////////////////////////////////////////////

wash.state = {

    // What the wash is over, so it can be put back where it belongs once the file is scrolled,
    // and whether something other than the cursor on a number is holding it there
    block: null,
    isHeld: false
};

// ////////////////////////////////////////////////////////////////////////

// The wash is the first thing in the box the file is read in, which leaves the overlay the file
// is colored on where it was - the one right in front of the textarea, since that is the one the
// textarea is found by.
wash.init = function() {

    var elem = document.createElement('div');
    elem.className = wash.config.elemClass;

    var wrapper = tables.get('content').parentNode;
    wrapper.insertBefore(elem, wrapper.firstChild);

    wash.elem = elem;
};

// ////////////////////////////////////////////////////////////////////////

// The wash over a block of the file, level with the first line of it. Held, it stays until
// whoever put it there takes it away - that is the drawing pointing at a line rather than the
// cursor resting on a number.
wash.show = function(block, isHeld) {

    var height = block.count * tables.gutter.state.lineHeight;

    wash.state.block = block;
    wash.state.isHeld = isHeld;

    wash.elem.style.height = height + 'px';
    wash.elem.classList.add(wash.config.visibleClass);

    wash.position();
};

// ////////////////////////////////////////////////////////////////////////

// Where the wash goes is where the first line of its block is, which moves as the file is
// scrolled under it.
wash.position = function() {

    var geometry = tables.gutter.state;
    var scrollTop = tables.get('content').scrollTop;
    var top = geometry.paddingTop + wash.state.block.start * geometry.lineHeight - scrollTop;

    wash.elem.style.top = top + 'px';
};

// ////////////////////////////////////////////////////////////////////////

wash.hide = function() {

    wash.state.block = null;
    wash.state.isHeld = false;
    wash.elem.classList.remove(wash.config.visibleClass);
};

// ////////////////////////////////////////////////////////////////////////
// Bringing a line on screen
// ////////////////////////////////////////////////////////////////////////

// The file is scrolled only as far as it takes for a line to be on screen, so a line that is
// there already is left where it is.
wash.scrollToLine = function(lineIdx) {

    var geometry = tables.gutter.state;
    var content = tables.get('content');

    // Where the line is inside the file's own box, the room it keeps above its first
    // line counted in
    var top = geometry.contentPadding + lineIdx * geometry.lineHeight;
    var bottom = top + geometry.lineHeight;

    if(top < content.scrollTop) {
        content.scrollTop = top;
        return;
    }

    if(bottom > content.scrollTop + content.clientHeight) {
        content.scrollTop = bottom - content.clientHeight;
    }
};

// ////////////////////////////////////////////////////////////////////////

// A line the reader is being brought to rather than one being kept on screen - a line already on
// screen is left where it is, and one that is not lands in the middle of the view, which is where
// a line is read from. The ends of the file come as close to the middle as they can.
wash.showLine = function(lineIdx) {

    var geometry = tables.gutter.state;
    var content = tables.get('content');

    var top = geometry.contentPadding + lineIdx * geometry.lineHeight;
    var bottom = top + geometry.lineHeight;

    var isOnScreen = top >= content.scrollTop && bottom <= content.scrollTop + content.clientHeight;

    if(isOnScreen) {
        return;
    }

    var wanted = top - (content.clientHeight - geometry.lineHeight) / 2;
    var furthest = content.scrollHeight - content.clientHeight;

    if(wanted < 0) {
        wanted = 0;
    }

    if(wanted > furthest) {
        wanted = furthest;
    }

    content.scrollTop = wanted;
};

// ////////////////////////////////////////////////////////////////////////

// A block is brought on screen from its start, so a table taller than the room there is for it
// is read from its name down rather than from its last line up.
wash.scrollToBlock = function(block) {

    wash.scrollToLine(block.start + block.count - 1);
    wash.scrollToLine(block.start);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
