(function() {
    'use strict';

    Object.assign(window.ZatoIDEEditorAce, {

        setupOccurrenceHighlight: function(editor, instance) {
            var self = this;

            console.log('[Occurrences] setupOccurrenceHighlight called');

            instance.occurrenceMarkers = [];
            instance.primaryOccurrenceMarker = null;

            editor.on('click', function(e) {
                console.log('[Occurrences] click event, ctrlKey:', e.domEvent.ctrlKey);

                if (e.domEvent.ctrlKey) {
                    return;
                }

                self.clearOccurrenceHighlights(editor, instance);

                var pos = editor.getCursorPosition();
                var token = editor.session.getTokenAt(pos.row, pos.column);

                console.log('[Occurrences] pos:', JSON.stringify(pos), 'token:', JSON.stringify(token));

                if (!token || !self.isNavigableToken(token)) {
                    console.log('[Occurrences] token not navigable');
                    return;
                }

                var word = token.value;
                if (!word || !/^[A-Za-z_][A-Za-z0-9_]*$/.test(word)) {
                    console.log('[Occurrences] word invalid:', word);
                    return;
                }

                var cursorLine = pos.row + 1;

                console.log('[Occurrences] ZatoIDELocalSymbols:', typeof ZatoIDELocalSymbols, 'localSymbols:', !!instance.localSymbols);

                if (typeof ZatoIDELocalSymbols === 'undefined' || !instance.localSymbols) {
                    console.log('[Occurrences] no local symbols');
                    return;
                }

                console.log('[Occurrences] localSymbols.functions:', JSON.stringify(Object.keys(instance.localSymbols.functions)));
                console.log('[Occurrences] localSymbols.variables:', JSON.stringify(Object.keys(instance.localSymbols.variables)));
                console.log('[Occurrences] looking for word:', word, 'at line:', cursorLine);

                var definition = ZatoIDELocalSymbols.findDefinition(instance, word, cursorLine);
                console.log('[Occurrences] findDefinition result:', JSON.stringify(definition));

                var occurrences = ZatoIDELocalSymbols.findAllOccurrences(editor, instance, word, cursorLine);
                console.log('[Occurrences] found occurrences:', occurrences.length, JSON.stringify(occurrences));

                if (occurrences.length === 0) {
                    return;
                }

                self.highlightOccurrences(editor, instance, occurrences, pos.row, token.start);
            });

            editor.session.on('change', function() {
                self.clearOccurrenceHighlights(editor, instance);
            });
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
