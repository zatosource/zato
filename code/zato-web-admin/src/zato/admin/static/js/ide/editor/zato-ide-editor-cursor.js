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
            var lineElements = code.querySelectorAll('.zato-ide-editor-line');
            var lineEl = lineElements[line - 1];

            console.log('[CURSOR] updatePosition: line=' + line + ', col=' + col);

            if (!lineEl) {
                console.log('[CURSOR] no line element found for line ' + line);
                return;
            }

            var codeRect = code.getBoundingClientRect();
            var lineRect = lineEl.getBoundingClientRect();
            var lineHeightPx = lineRect.height;

            var top = lineRect.top - codeRect.top + code.scrollTop;
            var left = this.getCharOffsetInLine(lineEl, col - 1, codeRect);

            console.log('[CURSOR] codeRect.left=' + codeRect.left + ', codeRect.top=' + codeRect.top);
            console.log('[CURSOR] lineRect.left=' + lineRect.left + ', lineRect.top=' + lineRect.top);
            console.log('[CURSOR] calculated top=' + top + ', left=' + left + ', height=' + lineHeightPx);

            cursor.style.top = top + 'px';
            cursor.style.left = left + 'px';
            cursor.style.height = lineHeightPx + 'px';
        },

        getCharOffsetInLine: function(lineEl, charIndex, codeRect) {
            if (charIndex === 0) {
                var lineRect = lineEl.getBoundingClientRect();
                return lineRect.left - codeRect.left;
            }

            var targetTextNode = this.getTextNodeAtOffset(lineEl, charIndex);
            if (!targetTextNode.node) {
                console.log('[CURSOR] getCharOffsetInLine: no target text node found for charIndex=' + charIndex);
                var lineRect = lineEl.getBoundingClientRect();
                return lineRect.left - codeRect.left;
            }

            console.log('[CURSOR] getCharOffsetInLine: charIndex=' + charIndex + ', node.textContent="' + targetTextNode.node.textContent + '", offset=' + targetTextNode.offset);

            var range = document.createRange();
            range.setStart(targetTextNode.node, targetTextNode.offset);
            range.setEnd(targetTextNode.node, targetTextNode.offset);

            var rects = range.getClientRects();
            if (rects.length === 0) {
                range.setStart(targetTextNode.node, 0);
                range.setEnd(targetTextNode.node, targetTextNode.offset);
                rects = range.getClientRects();
            }

            if (rects.length === 0) {
                console.log('[CURSOR] getCharOffsetInLine: no rects for charIndex=' + charIndex);
                var lineRect = lineEl.getBoundingClientRect();
                return lineRect.left - codeRect.left;
            }

            var rect = rects[rects.length - 1];
            var result = rect.left - codeRect.left;
            console.log('[CURSOR] getCharOffsetInLine: rect.left=' + rect.left + ', codeRect.left=' + codeRect.left + ', result=' + result);
            return result;
        },

        getTextNodeAtOffset: function(element, charIndex) {
            var walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, null, false);
            var currentOffset = 0;
            var node;

            while ((node = walker.nextNode())) {
                var nodeLength = node.textContent.length;
                if (currentOffset + nodeLength >= charIndex) {
                    return {
                        node: node,
                        offset: charIndex - currentOffset
                    };
                }
                currentOffset += nodeLength;
            }

            return { node: null, offset: 0 };
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
