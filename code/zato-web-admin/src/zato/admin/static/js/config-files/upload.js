// Config files kit - bringing a file in from your own machine.
//
// There is nothing to ask about, so nothing is asked - the button opens the browser's own file
// picker and the file lands where a new file lands, in the directory the files are read from. A
// file that does not read as an ini file comes in as readily as one that does, that being a file
// to fix up here, and the line under the editor says what is wrong with it.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.config_files;
var upload = tables.upload;
var parse = tables.parse;

// ////////////////////////////////////////////////////////////////////////

upload.config = {

    // What is said once a file is in, and what is said when it is in but does not read yet -
    // which line stopped it is what Check is for
    doneMessage: 'Uploaded ',
    doneErrorSuffix: ', with errors'
};

// ////////////////////////////////////////////////////////////////////////

upload.init = function() {

    tables.get('upload').addEventListener('click', upload.open);
    tables.get('upload-file').addEventListener('change', upload.apply);
};

// ////////////////////////////////////////////////////////////////////////

// The file picker of the browser, which is the one thing there is to this. What was picked last
// time is cleared first, so picking the same file again is still a change to answer to.
upload.open = function() {

    var picker = tables.get('upload-file');

    picker.value = '';
    picker.click();
};

// ////////////////////////////////////////////////////////////////////////

upload.apply = function() {

    var uploaded = upload.getPickedFile();

    // The picker was closed without anything picked
    if(uploaded === null) {
        return;
    }

    var reader = new FileReader();

    reader.addEventListener('load', function() {
        upload.addUploaded(uploaded.name, reader.result);
    });

    reader.readAsText(uploaded);
};

// ////////////////////////////////////////////////////////////////////////

upload.getPickedFile = function() {

    var out = null;
    var fileList = tables.get('upload-file').files;
    var hasFile = fileList.length > 0;

    if(hasFile) {
        out = fileList[0];
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

upload.addUploaded = function(fileName, content) {

    var name = tables.files.getStem(fileName);

    if(tables.getByName(name)) {
        tables.setStatus('There is a file called ' + name + ' already', true);
        return;
    }

    var directory = tables.state.userConfDirectory;
    var table = tables.files.buildTable(name, fileName, directory, content);
    var parsed = parse.read(content);

    tables.files.persist('upload', table, function() {

        tables.state.tableList.push(table);
        tables.state.initialContent[name] = content;

        // What is at that path now is what was brought in, so anything a file of the same name
        // once had unsaved or had its caret at is no longer about this file
        tables.draft.forget(table);
        tables.edit.forget(table);

        // Bringing a file in is one more thing the page did, taken back the same way an empty
        // file added from the listing is
        tables.stream.rememberAdd(table);

        tables.select(name);

        // A file that does not read as an ini file yet is brought in all the same, that being
        // what the editor is for
        if(parsed.errorText) {
            tables.setStatus(upload.config.doneMessage + fileName + upload.config.doneErrorSuffix, true);
            return;
        }

        tables.setStatus(upload.config.doneMessage + fileName);
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
