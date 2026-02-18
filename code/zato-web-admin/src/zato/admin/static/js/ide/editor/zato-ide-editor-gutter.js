(function() {
    'use strict';

    /**
     * ZatoIDEEditorGutter - line numbers component for the editor.
     * Handles rendering line numbers and highlighting the current line.
     * Each editor instance maintains its own gutter state.
     */
    var ZatoIDEEditorGutter = {

        /**
         * Renders line numbers for the given editor instance.
         */
        render: function(instance, lineCount) {
            var gutter = instance.elements.gutter;
            if (!gutter) {
                return;
            }

            var html = '';
            var currentLine = instance.cursorLine || 1;

            for (var i = 1; i <= lineCount; i++) {
                var activeClass = (i === currentLine) ? ' active' : '';
                html += '<div class="zato-ide-editor-gutter-line' + activeClass + '" data-line="' + i + '">' + i + '</div>';
            }

            if (lineCount === 0) {
                html = '<div class="zato-ide-editor-gutter-line active" data-line="1">1</div>';
            }

            gutter.innerHTML = html;
        },

        /**
         * Highlights the specified line number in the gutter.
         */
        highlightLine: function(instance, lineNumber) {
            var gutter = instance.elements.gutter;
            if (!gutter) {
                return;
            }

            var lines = gutter.querySelectorAll('.zato-ide-editor-gutter-line');
            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                var num = parseInt(line.getAttribute('data-line'), 10);
                if (num === lineNumber) {
                    line.classList.add('active');
                } else {
                    line.classList.remove('active');
                }
            }

            this.updateLineHighlight(instance, lineNumber);
        },

        /**
         * Updates the line highlight background for the current line.
         */
        updateLineHighlight: function(instance, lineNumber) {
            var lineHighlight = instance.elements.lineHighlight;
            if (!lineHighlight) {
                return;
            }

            var lineHeight = instance.options.fontSize * instance.options.lineHeight;
            var top = (lineNumber - 1) * lineHeight;

            lineHighlight.style.top = (top - instance.scrollTop) + 'px';
            lineHighlight.style.height = lineHeight + 'px';
        },

        /**
         * Gets the width of the gutter based on line count.
         */
        getWidth: function(lineCount) {
            var digits = String(Math.max(lineCount, 1)).length;
            var minDigits = 2;
            digits = Math.max(digits, minDigits);
            return (digits * 8) + 16;
        }
    };

    window.ZatoIDEEditorGutter = ZatoIDEEditorGutter;

})();
