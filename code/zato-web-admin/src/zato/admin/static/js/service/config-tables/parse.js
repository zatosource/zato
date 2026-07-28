// Config tables - reading a file the way the server reads it.
//
// A file is sections of key and value pairs. A code list keeps every code under
// the one section, a mapping set keeps one section per name the values come
// from. Nothing here touches the page - it only says what a file holds, which is
// what the editor reports while it is typed in and what the Try it strip answers
// from.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var parse = tables.parse;

// ////////////////////////////////////////////////////////////////////////

// The file as sections of key and value pairs. The first line that does not
// belong stops the reading, so a file that would not load on the server is not
// saved from here either.
parse.read = function(content) {

    var out = {sectionList: [], entryCount: 0, errorLine: 0, errorText: ''};
    var lineList = content.split('\n');
    var section = null;

    for(var lineIdx = 0; lineIdx < lineList.length; lineIdx++) {

        var line = lineList[lineIdx].trim();
        var lineNumber = lineIdx + 1;

        if(!line) {
            continue;
        }

        // Comments are the file's own notes, e.g. where a list came from
        if(parse.isComment(line)) {
            continue;
        }

        if(line.charAt(0) === '[') {

            if(line.charAt(line.length - 1) !== ']') {
                out.errorLine = lineNumber;
                out.errorText = 'a section name is missing its closing bracket';
                return out;
            }

            section = {name: line.substring(1, line.length - 1).trim(), entryList: []};
            out.sectionList.push(section);
            continue;
        }

        var separatorIdx = line.indexOf('=');

        if(separatorIdx === -1) {
            out.errorLine = lineNumber;
            out.errorText = 'no = sign, so there is nothing to read as a value';
            return out;
        }

        if(!section) {
            out.errorLine = lineNumber;
            out.errorText = 'this value is not under any section';
            return out;
        }

        var key = line.substring(0, separatorIdx).trim();
        var value = line.substring(separatorIdx + 1).trim();

        section.entryList.push({key: key, value: value});
        out.entryCount++;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

parse.isComment = function(line) {

    var out = false;
    var first = line.charAt(0);

    if(first === '#') {
        out = true;
    }

    if(first === ';') {
        out = true;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What one value is read as - the display name for a code list, the value it
// maps to for a mapping set. Nothing found comes back as null, since a value
// missing from a file is an answer of its own.
parse.lookup = function(table, content, fromName, code) {

    var out = null;
    var parsed = parse.read(content);
    var sectionName = tables.config.codesSection;

    // A mapping set keeps one section per name the values come from, a code
    // list keeps all of its codes under the one section
    if(tables.isMappingSet(table)) {
        sectionName = fromName;
    }

    var section = parse.findSection(parsed, sectionName);

    if(section) {
        out = parse.findValue(section, code);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

parse.findSection = function(parsed, sectionName) {

    var out = null;

    for(var sectionIdx = 0; sectionIdx < parsed.sectionList.length; sectionIdx++) {

        var section = parsed.sectionList[sectionIdx];

        if(section.name === sectionName) {
            out = section;
            break;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

parse.findValue = function(section, code) {

    var out = null;

    for(var entryIdx = 0; entryIdx < section.entryList.length; entryIdx++) {

        var entry = section.entryList[entryIdx];

        if(entry.key === code) {
            out = entry.value;
            break;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What a target sends one value as - every key it keeps that value under, since a
// target may well keep it under more than one. A name that is no section of the file
// comes back as null, which is not the same answer as a target that has no key for
// the value.
parse.findTargetKeys = function(content, targetName, value) {

    var parsed = parse.read(content);
    var section = parse.findSection(parsed, targetName);

    if(section === null) {
        return null;
    }

    var out = parse.findKeys(section, value);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Which sections hold the value and under which keys each of them holds it, which is
// what says whether a value is one that only one system knows or one that most of the
// file agrees on. Sections that do not hold it are left out.
parse.findValueSpread = function(content, value) {

    var parsed = parse.read(content);
    var out = [];

    for(var sectionIdx = 0; sectionIdx < parsed.sectionList.length; sectionIdx++) {

        var section = parsed.sectionList[sectionIdx];
        var keyList = parse.findKeys(section, value);

        if(keyList.length) {
            out.push({name: section.name, keyList: keyList});
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Read the other way round - the keys a value is under rather than the value a key
// holds, in name order, so what comes back reads the same way every time.
parse.findKeys = function(section, value) {

    var out = [];

    for(var entryIdx = 0; entryIdx < section.entryList.length; entryIdx++) {

        var entry = section.entryList[entryIdx];

        if(entry.value === value) {
            out.push(entry.key);
        }
    }

    out.sort();
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The first value the file holds, which is what the Try it strip starts from -
// the section it is under and the key it goes by. An empty file has neither.
parse.getFirstEntry = function(content) {

    var out = {sectionName: '', key: ''};
    var parsed = parse.read(content);
    var hasSection = parsed.sectionList.length > 0;

    if(hasSection) {

        var section = parsed.sectionList[0];
        out.sectionName = section.name;
        var hasEntry = section.entryList.length > 0;

        if(hasEntry) {
            var entry = section.entryList[0];
            out.key = entry.key;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
