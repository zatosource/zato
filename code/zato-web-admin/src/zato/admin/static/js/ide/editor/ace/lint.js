(function() {
    'use strict';

    Object.assign(window.ZatoIDEEditorAce, {

        unusedMarkerIds: [],
        unusedMarkerRanges: [],
        unusedHoverBound: false,
        unusedTooltipInstance: null,

        setupLinting: function(editor, instance, opts) {
            var lintTimeout = null;
            var lintInProgress = false;
            var lintPending = false;
            var lintDelay = opts.lintDelay;
            editor.session.on('change', function() {
                console.log('[ZatoIDEEditorAce] session change event, language=' + instance.options.language);
                if (instance.options.language !== 'python') {
                    console.log('[ZatoIDEEditorAce] not python, skipping lint');
                    return;
                }
                if (lintTimeout) {
                    clearTimeout(lintTimeout);
                }
                if (lintInProgress) {
                    lintPending = true;
                    return;
                }
                lintTimeout = setTimeout(function() {
                    lintInProgress = true;
                    ZatoIDEEditorAce.lintPython(editor, function() {
                        lintInProgress = false;
                        if (lintPending) {
                            lintPending = false;
                            lintTimeout = setTimeout(function() {
                                lintInProgress = true;
                                ZatoIDEEditorAce.lintPython(editor, function() {
                                    lintInProgress = false;
                                });
                            }, lintDelay);
                        }
                    });
                }, lintDelay);
            });
        },

        lintPython: function(editor, callback) {
            var code = editor.getValue();
            if (!code.trim()) {
                editor.session.setAnnotations([]);
                if (callback) {
                    callback();
                }
                return;
            }

            var csrfToken = this.getCsrfToken();
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/zato/ide/lint/python/', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            if (csrfToken) {
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
            }
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        try {
                            var response = JSON.parse(xhr.responseText);
                            console.log('[Lint] response received, annotations=' + (response.annotations ? response.annotations.length : 0));
                            if (response.success && response.annotations) {
                                console.log('[Lint] calling setAnnotations');
                                editor.session.setAnnotations(response.annotations);
                                console.log('[Lint] setAnnotations complete, re-applying breakpoints');
                                if (typeof ZatoDebuggerGutter !== 'undefined') {
                                    var gutterInstance = ZatoDebuggerGutter.getInstanceForEditor(editor);
                                    if (gutterInstance) {
                                        console.log('[Lint] found gutter instance, calling updateBreakpointMarkers');
                                        ZatoDebuggerGutter.updateBreakpointMarkers(gutterInstance);
                                    } else {
                                        console.log('[Lint] no gutter instance found for editor');
                                    }
                                }
                            }
                            ZatoIDEEditorAce.applyUnusedMarkers(editor, response.markers || []);
                        } catch (e) {
                            console.warn('[Lint] Failed to parse response:', e);
                        }
                    }
                    if (callback) {
                        callback();
                    }
                }
            };
            xhr.send(JSON.stringify({ code: code }));
        },

        applyUnusedMarkers: function(editor, markers) {
            var session = editor.session;
            var Range = ace.require('ace/range').Range;

            for (var i = 0; i < this.unusedMarkerIds.length; i++) {
                session.removeMarker(this.unusedMarkerIds[i]);
            }
            this.unusedMarkerIds = [];
            this.unusedMarkerRanges = [];

            for (var i = 0; i < markers.length; i++) {
                var m = markers[i];
                var range = new Range(m.startRow, m.startCol, m.endRow, m.endCol);
                var markerId = session.addMarker(range, 'ace_unused_variable', 'text', true);
                this.unusedMarkerIds.push(markerId);
                this.unusedMarkerRanges.push({
                    range: range,
                    message: m.message || 'Unused'
                });
            }

            this.setupUnusedHover(editor);
        },

        setupUnusedHover: function(editor) {
            if (this.unusedHoverBound) {
                return;
            }
            this.unusedHoverBound = true;

            var self = this;

            if (typeof ZatoTooltip !== 'undefined' && !this.unusedTooltipInstance) {
                this.unusedTooltipInstance = ZatoTooltip.create(editor.container.id, { theme: 'dark' });
            }

            var lastMessage = null;
            var lastRow = -1;
            var lastCol = -1;
            var tooltipHovered = false;
            var tooltipLocked = false;

            if (self.unusedTooltipInstance && self.unusedTooltipInstance.tooltipEl) {
                var tooltipEl = self.unusedTooltipInstance.tooltipEl;
                tooltipEl.style.pointerEvents = 'auto';
                tooltipEl.style.userSelect = 'text';
                tooltipEl.style.cursor = 'pointer';

                tooltipEl.addEventListener('mouseenter', function() {
                    tooltipHovered = true;
                });

                tooltipEl.addEventListener('mouseleave', function() {
                    if (tooltipLocked) {
                        return;
                    }
                    tooltipHovered = false;
                    lastMessage = null;
                    ZatoTooltip.hide(self.unusedTooltipInstance);
                });

                tooltipEl.addEventListener('click', function() {
                    var textToCopy = tooltipEl.textContent;
                    var originalTop = parseFloat(tooltipEl.style.top);
                    var originalRect = tooltipEl.getBoundingClientRect();
                    var originalCenterX = originalRect.left + (originalRect.width / 2);

                    navigator.clipboard.writeText(textToCopy).then(function() {
                        tooltipLocked = true;
                        tooltipEl.textContent = 'Copied to clipboard';

                        var newRect = tooltipEl.getBoundingClientRect();
                        var newLeft = originalCenterX - (newRect.width / 2);
                        tooltipEl.style.left = newLeft + 'px';
                        tooltipEl.style.top = originalTop + 'px';

                        setTimeout(function() {
                            tooltipLocked = false;
                            tooltipHovered = false;
                            lastMessage = null;
                            tooltipEl.style.opacity = '0';
                            tooltipEl.style.visibility = 'hidden';
                        }, 350);
                    });
                });
            }

            editor.on('mousemove', function(e) {
                var pos = e.getDocumentPosition();
                var row = pos.row;
                var col = pos.column;

                if (row === lastRow && col === lastCol) {
                    return;
                }
                lastRow = row;
                lastCol = col;

                var foundMessage = null;

                var lineLength = editor.session.getLine(row).length;

                if (col <= lineLength) {
                    for (var i = 0; i < self.unusedMarkerRanges.length; i++) {
                        var item = self.unusedMarkerRanges[i];
                        var r = item.range;
                        if (row === r.start.row && col >= r.start.column && col < r.end.column) {
                            foundMessage = item.message;
                            break;
                        }
                    }
                }

                if (foundMessage && foundMessage !== lastMessage) {
                    lastMessage = foundMessage;
                    if (self.unusedTooltipInstance && self.unusedTooltipInstance.tooltipEl) {
                        var coords = editor.renderer.textToScreenCoordinates(row, col);

                        var tooltipEl = self.unusedTooltipInstance.tooltipEl;
                        tooltipEl.textContent = foundMessage;
                        tooltipEl.style.display = 'block';
                        var tooltipRect = tooltipEl.getBoundingClientRect();

                        var tooltipWidth = tooltipRect.width;
                        var left = coords.pageX - (tooltipWidth / 2);
                        if (left < 5) {
                            left = 5;
                        }
                        var top = coords.pageY - tooltipRect.height - 2;
                        if (top < 5) {
                            top = coords.pageY + 20;
                        }

                        tooltipEl.style.left = left + 'px';
                        tooltipEl.style.top = top + 'px';
                        tooltipEl.style.opacity = '1';
                        tooltipEl.style.visibility = 'visible';
                    }
                } else if (!foundMessage && lastMessage && !tooltipHovered) {
                    if (self.unusedTooltipInstance && self.unusedTooltipInstance.tooltipEl) {
                        var tooltipEl = self.unusedTooltipInstance.tooltipEl;
                        var rect = tooltipEl.getBoundingClientRect();
                        var mouseCoords = editor.renderer.textToScreenCoordinates(row, col);
                        if (mouseCoords.pageY >= rect.top - 5 && mouseCoords.pageY <= rect.bottom + 20) {
                            return;
                        }
                    }
                    lastMessage = null;
                    if (self.unusedTooltipInstance) {
                        ZatoTooltip.hide(self.unusedTooltipInstance);
                    }
                }
            });

            editor.container.addEventListener('mouseleave', function(e) {
                if (tooltipHovered) {
                    return;
                }
                if (self.unusedTooltipInstance && self.unusedTooltipInstance.tooltipEl) {
                    var tooltipEl = self.unusedTooltipInstance.tooltipEl;
                    var rect = tooltipEl.getBoundingClientRect();
                    var mouseX = e.clientX;
                    var mouseY = e.clientY;
                    if (mouseX >= rect.left - 10 && mouseX <= rect.right + 10 && mouseY >= rect.top - 10 && mouseY <= rect.bottom + 10) {
                        return;
                    }
                }
                lastMessage = null;
                lastRow = -1;
                lastCol = -1;
                if (self.unusedTooltipInstance) {
                    ZatoTooltip.hide(self.unusedTooltipInstance);
                }
            });
        }

    });

})();
