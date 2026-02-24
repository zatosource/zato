(function() {
    'use strict';

    Object.assign(window.ZatoIDEEditorAce, {

        setupOccurrenceHighlight: function(editor, instance) {
            var self = this;

            instance.occurrenceMarkers = [];
            instance.primaryOccurrenceMarker = null;

            editor.on('click', function(e) {
                if (e.domEvent.ctrlKey) {
                    return;
                }

                self.clearOccurrenceHighlights(editor, instance);

                var pos = editor.getCursorPosition();
                var token = editor.session.getTokenAt(pos.row, pos.column);

                if (!token || !self.isNavigableToken(token)) {
                    return;
                }

                var word = token.value;
                if (!word || !/^[A-Za-z_][A-Za-z0-9_]*$/.test(word)) {
                    return;
                }

                var occurrences = self.findAllWordOccurrences(editor, word);
                if (occurrences.length === 0) {
                    return;
                }

                self.highlightOccurrences(editor, instance, occurrences, pos.row, token.start);
            });

            editor.session.on('change', function() {
                self.clearOccurrenceHighlights(editor, instance);
            });
        },

        findAllWordOccurrences: function(editor, word) {
            var content = editor.getValue();
            var lines = content.split('\n');
            var occurrences = [];

            var regex = new RegExp('\\b' + word + '\\b', 'g');

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                var match;
                while ((match = regex.exec(line)) !== null) {
                    occurrences.push({
                        line: i + 1,
                        column: match.index,
                        length: word.length
                    });
                }
            }

            return occurrences;
        },

        highlightOccurrences: function(editor, instance, occurrences, clickedRow, clickedColumn) {
            var self = this;
            var Range = ace.require('ace/range').Range;

            self.clearOccurrenceHighlights(editor, instance);

            for (var i = 0; i < occurrences.length; i++) {
                var occ = occurrences[i];
                var range = new Range(occ.line - 1, occ.column, occ.line - 1, occ.column + occ.length);

                var isPrimary = (occ.line - 1 === clickedRow && occ.column === clickedColumn);
                var markerClass = isPrimary ? 'ace_occurrence_primary' : 'ace_occurrence_secondary';

                var markerId = editor.session.addMarker(range, markerClass, 'text', true);

                if (isPrimary) {
                    instance.primaryOccurrenceMarker = markerId;
                } else {
                    instance.occurrenceMarkers.push(markerId);
                }
            }
        },

        clearOccurrenceHighlights: function(editor, instance) {
            if (instance.primaryOccurrenceMarker) {
                editor.session.removeMarker(instance.primaryOccurrenceMarker);
                instance.primaryOccurrenceMarker = null;
            }

            for (var i = 0; i < instance.occurrenceMarkers.length; i++) {
                editor.session.removeMarker(instance.occurrenceMarkers[i]);
            }
            instance.occurrenceMarkers = [];
        }

    });

})();
