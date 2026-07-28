// Config tables - bringing a file in from your own machine.
//
// Uploading is the one thing with a question of its own - where the file goes -
// so it is the one thing that opens a dialog. A file that does not parse is not
// put anywhere and the dialog stays open saying which line stopped it.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var upload = tables.upload;
var parse = tables.parse;

// ////////////////////////////////////////////////////////////////////////

upload.config = {

    // What the dialog says while it has nothing to show yet
    blank: '-',

    // What the dialog is titled
    uploadTitle: 'Upload a file',

    // How far down the window the dialog opens, before it is dragged anywhere
    openTopPercent: 12,

    // The key that puts the dialog away
    closeKey: 'Escape'
};

// ////////////////////////////////////////////////////////////////////////

upload.init = function() {

    var directory = tables.get('dialog-directory');
    var directoryList = tables.state.directoryList;

    for(var directoryIdx = 0; directoryIdx < directoryList.length; directoryIdx++) {

        var option = document.createElement('option');
        option.value = directoryList[directoryIdx];
        option.textContent = directoryList[directoryIdx];
        directory.appendChild(option);
    }

    // There is nothing to pick while the server reports the one directory
    var hasChoice = directoryList.length > 1;
    tables.get('dialog-directory-field').hidden = !hasChoice;

    tables.get('upload').addEventListener('click', upload.open);

    tables.get('dialog-file').addEventListener('change', upload.refresh);
    directory.addEventListener('change', upload.refresh);
    tables.get('dialog-cancel').addEventListener('click', upload.close);
    tables.get('dialog-upload').addEventListener('click', upload.apply);

    upload.wireDialog();
};

// ////////////////////////////////////////////////////////////////////////

// The dialog behaves the way every popup in the dashboard does - it is dragged by
// its header, and Escape or a press next to it rather than on it puts it away.
upload.wireDialog = function() {

    var dialog = tables.get('dialog');
    var header = tables.get('dialog-header');
    var overlay = tables.get('overlay');

    header.insertBefore($.fn.zato.popup.build_grip(), header.firstChild);

    $.fn.zato.popup.install_drag(header, {

        dragging_elem: dialog,

        on_start: function() {
            return {x: dialog.offsetLeft, y: dialog.offsetTop};
        },

        on_move: function(x, y) {
            dialog.style.left = x + 'px';
            dialog.style.top = y + 'px';
        }
    });

    overlay.addEventListener('mousedown', function(event) {

        // Only the dim itself, never anything on the dialog standing on it
        if(event.target === overlay) {
            upload.close();
        }
    });

    document.addEventListener('keydown', upload.onKeyDown);
};

// ////////////////////////////////////////////////////////////////////////

upload.onKeyDown = function(event) {

    if(tables.get('overlay').hidden) {
        return;
    }

    if(event.key === upload.config.closeKey) {
        upload.close();
    }
};

// ////////////////////////////////////////////////////////////////////////

upload.open = function() {

    tables.get('dialog-title').textContent = upload.config.uploadTitle;
    tables.get('dialog-file').value = '';
    tables.get('dialog-status').textContent = '';

    upload.refresh();
    tables.get('overlay').hidden = false;
    upload.place();
};

// ////////////////////////////////////////////////////////////////////////

// The dialog opens in the middle of the window and a little above the middle of
// it, which is where a question is looked for. It is placed once it is on screen,
// since its own width is what the middle is worked out from.
upload.place = function() {

    var dialog = tables.get('dialog');
    var left = (window.innerWidth - dialog.offsetWidth) / 2;
    var top = window.innerHeight * upload.config.openTopPercent / 100;

    dialog.style.left = left + 'px';
    dialog.style.top = top + 'px';
};

// ////////////////////////////////////////////////////////////////////////

upload.close = function() {

    tables.get('overlay').hidden = true;
};

// ////////////////////////////////////////////////////////////////////////

// Where the file would end up, kept up with what has been picked so far.
upload.refresh = function() {

    var uploaded = upload.getPickedFile();
    var path = upload.config.blank;

    if(uploaded) {
        var directory = upload.getPickedDirectory();
        path = directory + uploaded.name;
    }

    tables.get('dialog-path').textContent = path;
};

// ////////////////////////////////////////////////////////////////////////

upload.getPickedFile = function() {

    var out = null;
    var fileList = tables.get('dialog-file').files;
    var hasFile = fileList.length > 0;

    if(hasFile) {
        out = fileList[0];
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

upload.getPickedDirectory = function() {

    var out = tables.get('dialog-directory').value;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The name a service reads the file under - the file name without what it is
// written in.
upload.buildNameFromFile = function(fileName) {

    var out = fileName;
    var dotIdx = fileName.lastIndexOf('.');

    if(dotIdx > 0) {
        out = fileName.substring(0, dotIdx);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

upload.apply = function() {

    var uploaded = upload.getPickedFile();

    if(!uploaded) {
        tables.get('dialog-status').textContent = 'Pick a file first';
        return;
    }

    var reader = new FileReader();

    reader.addEventListener('load', function() {
        upload.readUploaded(uploaded.name, reader.result);
    });

    reader.readAsText(uploaded);
};

// ////////////////////////////////////////////////////////////////////////

upload.readUploaded = function(fileName, content) {

    var parsed = parse.read(content);

    if(parsed.errorText) {
        tables.get('dialog-status').textContent = tables.buildErrorText(parsed);
        return;
    }

    upload.addUploaded(fileName, content);
};

// ////////////////////////////////////////////////////////////////////////

upload.addUploaded = function(fileName, content) {

    var name = upload.buildNameFromFile(fileName);

    if(tables.getByName(name)) {
        tables.get('dialog-status').textContent = 'There is a file called ' + name + ' already';
        return;
    }

    var directory = upload.getPickedDirectory();
    var table = tables.files.buildTable(name, fileName, directory, content);

    tables.files.persist('upload', table, function() {

        tables.state.tableList.push(table);
        tables.state.initialContent[name] = content;

        upload.close();
        tables.select(name);
        tables.setStatus('Uploaded ' + fileName);
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
