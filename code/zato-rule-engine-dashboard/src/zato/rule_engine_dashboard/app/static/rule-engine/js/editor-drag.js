'use strict';

// Drag and drop for the rule editor: vocabulary attributes dropped onto the
// if line become conditions, attributes dropped onto the then or else line
// become actions. The dragged attribute travels as a ghost and the drop
// areas light up while a drag is in flight.
// Augments the editorView namespace from editor-render.js.

(function() {

// State of an in-flight vocabulary drag
editorView.dragState = null;

// ////////////////////////////////////////////////////////////////////////

editorView.clearDropMarks = function() {
    document.querySelectorAll('.editor-line-drop, .editor-group-drop').forEach(function(element) {
        element.classList.remove('editor-line-drop');
        element.classList.remove('editor-group-drop');
    });
};

// While a drag is in flight, every drop area shows itself as a dashed box,
// so the choice is visible before the pointer reaches it
editorView.markPossibleDrops = function() {
    document.querySelectorAll('.editor-line, .editor-group').forEach(function(element) {
        element.classList.add('editor-drop-possible');
    });
};

editorView.clearPossibleDrops = function() {
    document.querySelectorAll('.editor-drop-possible').forEach(function(element) {
        element.classList.remove('editor-drop-possible');
    });
};

// ////////////////////////////////////////////////////////////////////////

editorView.attachVocabularyDrag = function() {
    var self = this;

    document.querySelectorAll('.vocabulary-item[draggable="true"]').forEach(function(element) {
        element.addEventListener('dragstart', function(event) {
            var path = element.getAttribute('data-path');
            self.dragState = {path: path};

            // The ghost is the attribute's phrase, the same words the sentence will use
            var attribute = vocabulary.attribute(path);
            var ghost = shared.makeGhost([attribute.phrase], false);
            event.dataTransfer.setDragImage(ghost, 16, 12);
            event.dataTransfer.setData('text/plain', 'vocabulary');
            self.markPossibleDrops();
        });

        element.addEventListener('dragend', function() {
            self.dragState = null;
            self.clearDropMarks();
            self.clearPossibleDrops();
            shared.removeGhost();
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

// Dropping on the line itself appends at the end, dropping on one of its
// conditions or actions inserts right after that item, whose right edge
// lights up as the insertion point
editorView.attachDropLines = function() {
    var self = this;

    document.querySelectorAll('.editor-line').forEach(function(line) {
        var dropName = line.getAttribute('data-drop');

        line.addEventListener('dragover', function(event) {
            if (self.dragState === null) { return; }
            event.preventDefault();
            self.clearDropMarks();
            line.classList.add('editor-line-drop');
        });

        line.addEventListener('dragleave', function() {
            line.classList.remove('editor-line-drop');
        });

        line.addEventListener('drop', function(event) {
            event.preventDefault();
            self.clearDropMarks();
            if (self.dragState === null) { return; }

            self.dropAt(dropName, self.dragState.path, self.listLength(dropName));
            self.dragState = null;
        });
    });

    document.querySelectorAll('.editor-group').forEach(function(group) {
        var groupName = group.getAttribute('data-group');
        var separator = groupName.lastIndexOf('-');
        var dropName = groupName.slice(0, separator);
        var itemIndex = +groupName.slice(separator + 1);

        group.addEventListener('dragover', function(event) {
            if (self.dragState === null) { return; }
            event.preventDefault();
            // The group mark wins over the whole-line mark
            event.stopPropagation();
            self.clearDropMarks();
            group.classList.add('editor-group-drop');
        });

        group.addEventListener('drop', function(event) {
            event.preventDefault();
            event.stopPropagation();
            self.clearDropMarks();
            if (self.dragState === null) { return; }

            self.dropAt(dropName, self.dragState.path, itemIndex + 1);
            self.dragState = null;
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

editorView.listLength = function(dropName) {
    var out = dropName === 'conditions' ? editorModel.rule.conditions.length : editorModel.rule[dropName].length;
    return out;
};

// A dropped attribute lands at the given position: on the if line it starts
// a condition whose comparator menu opens by itself, on the then and else
// lines it becomes an action, yes/no attributes arriving already set to true
editorView.dropAt = function(dropName, path, position) {
    if (dropName === 'conditions') {
        editorModel.rule.conditions.splice(position, 0, {subject: path, comparator: null, values: []});

        // A new condition brings one new and-joiner with it
        if (editorModel.rule.conditions.length > 1) {
            var joinerIndex = position === 0 ? 0 : position - 1;
            editorModel.rule.joiners.splice(joinerIndex, 0, 'and');
        }
        this.autoOpen = 'comparator-' + position;
        this.render();
        return;
    }

    var attribute = vocabulary.attribute(path);
    var values = attribute.type === 'yes/no' ? ['true'] : [''];
    editorModel.rule[dropName].splice(position, 0, {target: path, values: values});

    if (attribute.type !== 'yes/no') {
        this.autoOpen = 'value-' + dropName + '-' + position + '-0';
    }
    this.render();
};

})();
