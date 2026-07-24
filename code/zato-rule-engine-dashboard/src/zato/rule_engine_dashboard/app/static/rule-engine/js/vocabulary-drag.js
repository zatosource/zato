'use strict';

// Free drag and drop in the term tree: a ghost of the term follows the
// pointer, dashed drop areas open up between rows for reordering, and an
// entity heading is itself a drop area that moves the term into that
// entity, which changes its path and propagates everywhere like a rename.
// All listeners are delegated to the list container, so the cost never
// depends on how many terms are on screen. Augments vocabularyView.

(function() {

vocabularyView.dragPath = null;

var list = document.getElementById('vocabulary-tree-list');

// ////////////////////////////////////////////////////////////////////////

var clearDropMarks = function() {
    document.querySelectorAll('.vocabulary-drop-before, .vocabulary-drop-after, .vocabulary-drop-into')
        .forEach(function(element) {
            element.classList.remove('vocabulary-drop-before', 'vocabulary-drop-after', 'vocabulary-drop-into');
        });
};

// ////////////////////////////////////////////////////////////////////////

list.addEventListener('dragstart', function(event) {
    var item = event.target.closest('.vocabulary-tree-item');
    if (item === null) { return; }

    vocabularyView.dragPath = item.dataset.path;
    var ghost = shared.makeGhost([item.dataset.path], false);
    event.dataTransfer.setDragImage(ghost, 16, 12);
    event.dataTransfer.effectAllowed = 'move';
});

// ////////////////////////////////////////////////////////////////////////

list.addEventListener('dragover', function(event) {
    if (vocabularyView.dragPath === null) { return; }
    event.preventDefault();
    clearDropMarks();

    // Over a term: a floating dashed placeholder marks the landing spot
    // above or below it, whichever half of the row the pointer is in,
    // without shifting the rows underneath
    var item = event.target.closest('.vocabulary-tree-item');
    if (item !== null) {
        if (item.dataset.path === vocabularyView.dragPath) { shared.removeDropPlaceholder(); return; }
        var rectangle = item.getBoundingClientRect();
        var before = event.clientY < rectangle.top + rectangle.height / 2;
        item.classList.add(before ? 'vocabulary-drop-before' : 'vocabulary-drop-after');

        var thickness = shared.config.dropPlaceholderThickness;
        var boundary = before ? rectangle.top : rectangle.bottom;
        shared.showDropPlaceholder(rectangle.left, boundary - thickness / 2, rectangle.width, thickness);
        return;
    }

    // Over an entity heading: the whole heading is the drop area, the
    // term joins that entity at its end
    shared.removeDropPlaceholder();
    var heading = event.target.closest('.vocabulary-entity');
    if (heading !== null) { heading.classList.add('vocabulary-drop-into'); }
});

list.addEventListener('dragleave', function(event) {
    if (event.target === list) { clearDropMarks(); shared.removeDropPlaceholder(); }
});

// ////////////////////////////////////////////////////////////////////////

list.addEventListener('drop', function(event) {
    if (vocabularyView.dragPath === null) { return; }
    event.preventDefault();

    var dragPath = vocabularyView.dragPath;
    var targetEntityName = null;
    var targetIndex = null;

    var item = event.target.closest('.vocabulary-tree-item');
    var heading = event.target.closest('.vocabulary-entity');

    if (item !== null && item.dataset.path !== dragPath) {
        var targetPath = item.dataset.path;
        targetEntityName = targetPath.split('.')[0];
        var targetName = targetPath.split('.')[1];

        var entity = vocabulary.entities.filter(function(candidate) { return candidate.name === targetEntityName; })[0];
        targetIndex = entity.attributes.map(function(candidate) { return candidate.name; }).indexOf(targetName);
        if (item.classList.contains('vocabulary-drop-after')) { targetIndex += 1; }
    } else if (heading !== null) {
        targetEntityName = heading.dataset.entity;
        var targetEntity = vocabulary.entities.filter(function(candidate) { return candidate.name === targetEntityName; })[0];
        targetIndex = targetEntity.attributes.length;
    }

    clearDropMarks();
    shared.removeDropPlaceholder();
    if (targetEntityName === null) { return; }

    var entityChanged = targetEntityName !== dragPath.split('.')[0];

    vocabularyModel.moveTerm(dragPath, targetEntityName, targetIndex, function(newPath) {

        // A selected term stays selected under its new path
        if (vocabularyView.selectedPath === dragPath) {
            vocabularyView.selectedPath = null;
            vocabularyView.select(newPath);
        }
        vocabularyView.render();

        // Crossing entities changed the path, which landed everywhere at once
        if (entityChanged) {
            shared.popover(document.querySelector('[data-path="' + newPath + '"]'),
                'Moved to ' + targetEntityName + '. The path is now ' + newPath +
                ', every referencing ruleset was updated together, the API contract regenerated.', 'green');
        }
    });
});

// ////////////////////////////////////////////////////////////////////////

list.addEventListener('dragend', function() {
    vocabularyView.dragPath = null;
    clearDropMarks();
    shared.removeDropPlaceholder();
    shared.removeGhost();
});

})();
