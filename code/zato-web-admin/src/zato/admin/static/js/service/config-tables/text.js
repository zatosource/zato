// Config tables - the words the page puts on screen.
//
// Everything a line, a status or the Try it strip reads is built here, so what
// the page says is in one place and the rest of it only decides when to say it.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;

var singleQuote = "'";

// ////////////////////////////////////////////////////////////////////////

// What a file holds, in its own words - codes are counted on their own, while
// mappings are counted together with the names they come under.
tables.buildHolds = function(kind, entryCount, sectionCount) {

    var noun = tables.config.entryNoun[kind];
    var out = tables.pluralize(entryCount, noun);

    if(kind === 'mappings') {
        out = out + ' in ' + tables.pluralize(sectionCount, 'section');
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The same, for a file on screen rather than one on the server.
tables.buildHoldsText = function(parsed) {

    var kind = tables.deriveKind(parsed);
    var out = tables.buildHolds(kind, parsed.entryCount, parsed.sectionList.length);

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The line that stopped the file from being read, and what was wrong with it.
tables.buildErrorText = function(parsed) {

    var out = 'Line ' + parsed.errorLine + ' - ' + parsed.errorText;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// How a service reaches the file - by name when the name is one Python reads as
// an attribute, by key when it is not.
tables.buildReference = function(name) {

    var isAttribute = /^[A-Za-z_][A-Za-z0-9_]*$/.test(name);
    var out = 'self.config[' + singleQuote + name + singleQuote + ']';

    if(isAttribute) {
        out = 'self.config.' + name;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A value the file has nothing for, said as the plain fact that it is.
tables.buildMissingText = function(table, fromName, code) {

    var quotedCode = singleQuote + code + singleQuote;
    var out = quotedCode + ' is not in this file';

    if(tables.isMappingSet(table)) {
        var quotedFrom = singleQuote + fromName + singleQuote;
        out = 'Nothing under ' + quotedFrom + ' maps ' + quotedCode;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What stands in the editor for a file too large to be edited in it - a comment,
// so it reads as one line of the kind of file it stands for.
tables.buildOutsideText = function(table) {

    var size = tables.formatSize(table.size);
    var out = '# ' + size + ' - too large to edit here. Download it, change it, upload it back.';

    return out;
};

// ////////////////////////////////////////////////////////////////////////

tables.formatSize = function(size) {

    var config = tables.config;
    var unitIdx = 0;
    var count = size;

    while(count >= config.sizeStep) {

        var isLastUnit = unitIdx === config.sizeUnits.length - 1;

        if(isLastUnit) {
            break;
        }

        count = count / config.sizeStep;
        unitIdx++;
    }

    var rounded = Math.round(count);
    var out = rounded + ' ' + config.sizeUnits[unitIdx];

    return out;
};

// ////////////////////////////////////////////////////////////////////////

tables.pluralize = function(count, noun) {

    var out = count + ' ' + noun;

    if(count !== 1) {
        out = out + 's';
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
