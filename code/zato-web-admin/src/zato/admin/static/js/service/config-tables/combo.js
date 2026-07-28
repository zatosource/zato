// Config tables - the fields of the Translate column offer what the file holds.
//
// All of them are editable, so anything at all may be typed into them, and pressing one
// opens what the file has to offer without a letter being typed first. What is
// offered comes off the file as it is on disk rather than off the editor, since the
// editor may hold changes that were never saved. A field only ever offers what makes
// sense in it, which is why a target is offered every system but the source's own.
//
// A file can hold thousands of values, so nothing is read until a field is opened,
// the reading is kept until the file changes underneath it, and only as much of it
// as is worth putting on screen at once is handed to the menu - the rest is said as
// a count that typing narrows down.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var combo = tables.combo;
var parse = tables.parse;

// ////////////////////////////////////////////////////////////////////////

combo.config = {

    // How many of the matches go on screen at once
    maxShown: 100,

    // What the menu says about the matches that did not fit, and the class it
    // says it in
    restClass: 'zato-autocomplete-rest',
    restPrefix: '\u2026 ',
    restSuffix: ' more, keep typing',

    // The widget opens on nothing being typed, and it answers as it is typed into
    minLength: 0,
    delay: 0
};

// ////////////////////////////////////////////////////////////////////////

combo.state = {

    // The file as it is on disk, read once and kept until that content changes
    parsed: null,
    parsedContent: null,

    // How many matches the last answer left out
    restCount: 0
};

// ////////////////////////////////////////////////////////////////////////

combo.init = function() {

    // The sections of a mapping set are what a value can come from
    combo.attach(tables.get('translate-source'), combo.getSourceList);

    // And the keys of the section named by the field above are what it can be
    combo.attach(tables.get('translate-value'), combo.getValueList);

    // A target is a system like a source, so it is the same sections again, less the one
    // the value is already coming from
    combo.attach(tables.get('translate-target'), combo.getTargetList);
};

// ////////////////////////////////////////////////////////////////////////

combo.attach = function(input, getItemList) {

    $(input).autocomplete({

        minLength: combo.config.minLength,
        delay: combo.config.delay,

        source: function(request, response) {
            response(combo.answer(getItemList(), request.term));
        },

        open: function() {
            combo.showRest($(input).autocomplete('widget'));
        }
    });

    // Pressing the field is enough to see everything it offers, whatever is in it
    // already - the arrow keys open it the same way, which the widget does itself
    $(input).on('click', function() {
        $(input).autocomplete('search', '');
    });
};

// ////////////////////////////////////////////////////////////////////////

// What the menu is given - the matches, cut down to what fits on screen, with the
// count of the ones left out kept for the note under them.
combo.answer = function(itemList, term) {

    var config = combo.config;
    var matchList = combo.filter(itemList, term);

    combo.state.restCount = matchList.length - config.maxShown;

    if(combo.state.restCount > 0) {
        return matchList.slice(0, config.maxShown);
    }

    combo.state.restCount = 0;
    return matchList;
};

// ////////////////////////////////////////////////////////////////////////

// Everything the term appears in, wherever in it it appears, so a code is found by
// its middle as well as by its start.
combo.filter = function(itemList, term) {

    var wanted = term.trim().toLowerCase();

    if(!wanted) {
        return itemList;
    }

    var out = [];

    for(var itemIdx = 0; itemIdx < itemList.length; itemIdx++) {

        var item = itemList[itemIdx];

        if(item.toLowerCase().indexOf(wanted) !== -1) {
            out.push(item);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The last line of the menu, there only while the file has more to offer than the
// menu shows.
combo.showRest = function(menu) {

    var config = combo.config;

    menu.find('.' + config.restClass).remove();

    if(combo.state.restCount === 0) {
        return;
    }

    var rest = $('<li>')
        .addClass(config.restClass)
        .text(config.restPrefix + combo.state.restCount + config.restSuffix);

    menu.append(rest);
};

// ////////////////////////////////////////////////////////////////////////

// The file as it is on disk. The reading is kept for as long as that content stays
// as it is, so opening a field costs nothing after the first time.
combo.getParsed = function() {

    var state = combo.state;
    var table = tables.getCurrent();

    if(state.parsedContent !== table.content) {
        state.parsed = parse.read(table.content);
        state.parsedContent = table.content;
    }

    return state.parsed;
};

// ////////////////////////////////////////////////////////////////////////

combo.getSourceList = function() {

    var parsed = combo.getParsed();
    var out = [];

    for(var sectionIdx = 0; sectionIdx < parsed.sectionList.length; sectionIdx++) {
        out.push(parsed.sectionList[sectionIdx].name);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The same systems a source is picked from, without the one the field above already names
// - a value going back to where it came from is no translation at all.
combo.getTargetList = function() {

    var fromName = tables.get('translate-source').value.trim();
    var sourceList = combo.getSourceList();
    var out = [];

    for(var nameIdx = 0; nameIdx < sourceList.length; nameIdx++) {

        var name = sourceList[nameIdx];

        if(name !== fromName) {
            out.push(name);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What can be looked up - the keys of the section the value would be looked up in,
// which for a code list is the one section it keeps its codes under and for a
// mapping set is the one the field above names.
combo.getValueList = function() {

    var table = tables.getCurrent();
    var sectionName = tables.config.codesSection;

    if(tables.isMappingSet(table)) {
        sectionName = tables.get('translate-source').value.trim();
    }

    var section = parse.findSection(combo.getParsed(), sectionName);
    var out = [];

    // A name that is not a section of the file has nothing to offer, which is an
    // answer of its own - the field still takes whatever is typed into it
    if(section === null) {
        return out;
    }

    for(var entryIdx = 0; entryIdx < section.entryList.length; entryIdx++) {
        out.push(section.entryList[entryIdx].key);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
