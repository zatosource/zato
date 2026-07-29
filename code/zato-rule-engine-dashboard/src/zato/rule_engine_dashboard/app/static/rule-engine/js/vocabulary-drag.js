'use strict';

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

        if (vocabularyView.selectedPath === dragPath) {
            vocabularyView.selectedPath = null;
            vocabularyView.select(newPath);
        }
        vocabularyView.render();

        if (entityChanged) {
            shared.popover(document.querySelector('[data-path="' + newPath + '"]'),
                'Moved to ' + targetEntityName + '. The path is now ' + newPath +
                ', every referencing ruleset was updated together, the API contract regenerated.', 'green');
        }
    }, data.reportError);
});

// ////////////////////////////////////////////////////////////////////////

list.addEventListener('dragend', function() {
    vocabularyView.dragPath = null;
    clearDropMarks();
    shared.removeDropPlaceholder();
    shared.removeGhost();
});

})();
