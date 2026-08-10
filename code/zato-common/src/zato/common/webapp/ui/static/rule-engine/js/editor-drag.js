'use strict';

(function() {

editorView.dragState = null;

// ////////////////////////////////////////////////////////////////////////

editorView.clearDropMarks = function() {
    this.elements('.editor-line-drop, .editor-group-drop').forEach(function(element) {
        element.classList.remove('editor-line-drop');
        element.classList.remove('editor-group-drop');
    });
};

editorView.markPossibleDrops = function() {

    // The page itself explains the gesture - the legal landing places light
    // up and everything that cannot take the drop steps back a step
    this.container.classList.add('editor-dragging');

    this.elements('.editor-line, .editor-group').forEach(function(element) {
        element.classList.add('editor-drop-possible');
    });
};

editorView.clearPossibleDrops = function() {
    this.container.classList.remove('editor-dragging');

    this.elements('.editor-drop-possible').forEach(function(element) {
        element.classList.remove('editor-drop-possible');
    });
};

// ////////////////////////////////////////////////////////////////////////

editorView.attachVocabularyDrag = function() {
    var self = this;

    this.elements('.vocabulary-item[draggable="true"]').forEach(function(element) {
        element.addEventListener('dragstart', function(event) {
            var path = element.getAttribute('data-path');
            self.dragState = {path: path};

            var attribute = vocabulary.attribute(path);

            // The ghost under the pointer is the token the drop will leave
            // in the rule, not a copy of the list row
            var ghost = shared.makeGhost([attribute.phrase], false);
            ghost.firstChild.classList.add('drag-ghost-token');

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

// Hovering either side of the same fact lights both - a token in the canvas
// and the vocabulary card it came from answer each other
editorView.attachPathHighlight = function() {
    var self = this;

    var mark = function(path, isOn) {
        self.elements('[data-path="' + path + '"]').forEach(function(element) {
            element.classList.toggle('editor-path-match', isOn);
        });
    };

    this.elements('.editor-token[data-path], .vocabulary-item[data-path]').forEach(function(element) {
        var path = element.getAttribute('data-path');

        element.addEventListener('mouseenter', function() { mark(path, true); });
        element.addEventListener('mouseleave', function() { mark(path, false); });
    });
};

// ////////////////////////////////////////////////////////////////////////

editorView.attachDropLines = function() {
    var self = this;

    this.elements('.editor-line').forEach(function(line) {
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

    this.elements('.editor-group').forEach(function(group) {
        var groupName = group.getAttribute('data-group');
        var separator = groupName.lastIndexOf('-');
        var dropName = groupName.slice(0, separator);
        var itemIndex = +groupName.slice(separator + 1);

        group.addEventListener('dragover', function(event) {
            if (self.dragState === null) { return; }
            event.preventDefault();
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

editorView.dropAt = function(dropName, path, position) {
    if (dropName === 'conditions') {
        editorModel.rule.conditions.splice(position, 0, {subject: path, comparator: null, values: []});

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
