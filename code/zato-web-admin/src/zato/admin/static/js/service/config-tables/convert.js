// Config tables - a csv file turned into an ini file.
//
// A file of codes handed over by another system is usually a csv file, and what a service reads
// through self.config is an ini file, so the link beside Check makes one out of the other - every
// row becomes a line under a single table, the first field of a row being what the row is called
// and the rest of it being what it says.
//
// Nothing is saved by this. What comes out lands in the editor as though it had been typed there,
// so it is read over first, saved when it looks right and taken back with Ctrl-Z when it does not.
// The file keeps the name it came in under - renaming it is a separate thing to do, off the
// listing's own menu.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var convert = tables.convert;
var log = tables.log;

// ////////////////////////////////////////////////////////////////////////

convert.config = {

    // The files this is offered for, and what the offer says
    suffix: '.csv',

    // The one table everything a csv file holds goes under, there being nothing in such a file
    // that says which table any of it belongs to
    tableName: 'data',

    // What separates one field of a row from the next, and what sits between a name and what it
    // says on a line of an ini file
    fieldSeparator: ',',
    valueSeparator: ' = ',

    // The quotes a field may be wrapped in by whatever wrote the file, which are the file's own
    // punctuation rather than part of what the field says
    quoteList: ['"', "'"],

    // What is said once the file has been made over, and what is said when there was nothing in
    // it to make anything of
    doneMessage: 'Converted to ini - read it over and save it',
    emptyMessage: 'There is nothing in this file to convert',

    // What one row of a csv file with a single field to it says - a name on its own says nothing
    // about what it maps to, and a line of an ini file has both sides to it
    blankValue: ''
};

// ////////////////////////////////////////////////////////////////////////

convert.init = function() {

    tables.get('convert').addEventListener('click', convert.run);
};

// ////////////////////////////////////////////////////////////////////////

// The offer stands for a csv file the browser edits in place, and for nothing else.
convert.render = function(table) {

    tables.get('convert').hidden = !convert.isOffered(table);
};

// ////////////////////////////////////////////////////////////////////////

convert.isOffered = function(table) {

    var suffix = convert.config.suffix;
    var name = table.file_name.toLowerCase();
    var out = table.is_editable && name.lastIndexOf(suffix) === name.length - suffix.length;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

convert.run = function() {

    var table = tables.getCurrent();
    var content = tables.get('content').value;
    var wanted = convert.build(content);

    log.say('convert.run', {
        path: table.path,
        length: content.length,
        wantedLength: wanted.length
    });

    // A file of nothing but blank lines is left as it is rather than replaced by a table with
    // nothing under it
    if(wanted === '') {
        tables.setStatus(convert.config.emptyMessage, true);
        return;
    }

    tables.putContent(table, wanted);
    tables.setStatus(convert.config.doneMessage);
};

// ////////////////////////////////////////////////////////////////////////

// The ini file that a csv file amounts to - one table with a line under it per row of the file.
// A blank row says nothing, so it is left out, and everything else goes in whether it reads as a
// pair or not, since a file being made over here is a file to be read over afterwards.
convert.build = function(content) {

    var config = convert.config;
    var lineList = content.split('\n');
    var out = [];

    for(var lineIdx = 0; lineIdx < lineList.length; lineIdx++) {

        var line = lineList[lineIdx].trim();

        if(line === '') {
            continue;
        }

        out.push(convert.buildLine(line));
    }

    if(!out.length) {
        return '';
    }

    var name = '[' + config.tableName + ']';

    return name + '\n' + out.join('\n') + '\n';
};

// ////////////////////////////////////////////////////////////////////////

// One row as one line of an ini file - what the row is called is its first field, and what it says
// is the rest of the row as it stands, commas of its own included, so a value that has commas in
// it is not taken apart into fields it never had.
convert.buildLine = function(line) {

    var config = convert.config;
    var atIdx = line.indexOf(config.fieldSeparator);

    if(atIdx === -1) {
        return convert.unquote(line) + config.valueSeparator + config.blankValue;
    }

    var key = convert.unquote(line.substring(0, atIdx).trim());
    var value = convert.unquote(line.substring(atIdx + 1).trim());

    return key + config.valueSeparator + value;
};

// ////////////////////////////////////////////////////////////////////////

// A field without the quotes it was wrapped in, those being how the csv file was written rather
// than part of what the field says.
convert.unquote = function(field) {

    var quoteList = convert.config.quoteList;

    for(var quoteIdx = 0; quoteIdx < quoteList.length; quoteIdx++) {

        var quote = quoteList[quoteIdx];
        var isWrapped = field.length > 1 && field.charAt(0) === quote &&
            field.charAt(field.length - 1) === quote;

        if(isWrapped) {
            return field.substring(1, field.length - 1);
        }
    }

    return field;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
