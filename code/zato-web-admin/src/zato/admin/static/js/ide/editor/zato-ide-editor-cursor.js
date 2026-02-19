(function() {
    'use strict';

    /**
     * ZatoIDEEditorCursor - cursor management for the editor.
     * Handles cursor positioning and fast blinking animation.
     * Each editor instance maintains its own cursor blink interval.
     */
    var ZatoIDEEditorCursor = {

        /**
         * Updates cursor position based on line and column.
         */
        updatePosition: function(instance, line, col) {
            var cursor = instance.elements.cursor;
            if (!cursor) {
                return;
            }

            var code = instance.elements.code;
            var codeRect = code.getBoundingClientRect();
            var codeStyle = getComputedStyle(code);
            var codePaddingLeft = parseFloat(codeStyle.paddingLeft) || 0;
            var codePaddingTop = parseFloat(codeStyle.paddingTop) || 0;

            var lineHeight = instance.options.fontSize * instance.options.lineHeight;
            var charWidth = this.measureCharWidth(instance);

            var top = codePaddingTop + (line - 1) * lineHeight;
            var left = codePaddingLeft + (col - 1) * charWidth;

            cursor.style.transform = 'translate(' + left + 'px, ' + top + 'px)';
            cursor.style.height = lineHeight + 'px';
        },

        /**
         * Measures the width of a single character in the editor font.
         */
        measureCharWidth: function(instance) {
            if (instance.charWidth) {
                return instance.charWidth;
            }

            var measurer = document.createElement('span');
            measurer.style.position = 'absolute';
            measurer.style.visibility = 'hidden';
            measurer.style.fontFamily = "'Consolas', 'Monaco', 'Courier New', monospace";
            measurer.style.fontSize = instance.options.fontSize + 'px';
            measurer.style.whiteSpace = 'pre';
            measurer.textContent = 'X';

            document.body.appendChild(measurer);
            var width = measurer.offsetWidth;
            document.body.removeChild(measurer);

            instance.charWidth = width;
            return width;
        },

        /**
         * Starts cursor blinking for the given instance.
         */
        startBlink: function(instance) {
            this.stopBlink(instance);

            var cursor = instance.elements.cursor;
            if (!cursor) {
                return;
            }

            cursor.classList.add('visible');
            var visible = true;

            instance.cursorBlinkInterval = setInterval(function() {
                visible = !visible;
                if (visible) {
                    cursor.classList.add('visible');
                } else {
                    cursor.classList.remove('visible');
                }
            }, instance.options.cursorBlinkRate);
        },

        /**
         * Stops cursor blinking for the given instance.
         */
        stopBlink: function(instance) {
            if (instance.cursorBlinkInterval) {
                clearInterval(instance.cursorBlinkInterval);
                instance.cursorBlinkInterval = null;
            }

            var cursor = instance.elements.cursor;
            if (cursor) {
                cursor.classList.remove('visible');
            }
        },

        /**
         * Shows the cursor without blinking.
         */
        show: function(instance) {
            var cursor = instance.elements.cursor;
            if (cursor) {
                cursor.classList.add('visible');
            }
        },

        /**
         * Hides the cursor.
         */
        hide: function(instance) {
            var cursor = instance.elements.cursor;
            if (cursor) {
                cursor.classList.remove('visible');
            }
        }
    };

    window.ZatoIDEEditorCursor = ZatoIDEEditorCursor;

})();
