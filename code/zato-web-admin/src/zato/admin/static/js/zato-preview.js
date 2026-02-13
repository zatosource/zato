(function() {
    'use strict';

    var ZatoPreview = {
        popups: [],

        show: function(options) {
            var self = this;
            var id = options.id || 'preview-' + Date.now();
            var title = options.title || 'Preview';
            var content = options.content || '';
            var type = options.type || 'text';
            var onCopy = options.onCopy || null;

            for (var i = 0; i < this.popups.length; i++) {
                if (this.popups[i].getAttribute('data-preview-id') === id) {
                    this.bringToFront(this.popups[i]);
                    return this.popups[i];
                }
            }

            var popup = document.createElement('div');
            popup.className = 'zato-preview-popup';
            popup.setAttribute('data-preview-id', id);

            var offsetX = this.popups.length * 30;
            var offsetY = this.popups.length * 30;
            popup.style.left = (100 + offsetX) + 'px';
            popup.style.top = (100 + offsetY) + 'px';

            var canPreview = type !== 'none';

            var html = '';
            html += '<div class="zato-preview-header">';
            html += '<div class="zato-preview-title">' + this.escapeHtml(title) + '</div>';
            html += '<div class="zato-preview-actions">';
            if (canPreview && onCopy) {
                html += '<button class="zato-preview-copy-btn">Copy</button>';
            }
            html += '<button class="zato-preview-close">';
            html += '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';
            html += '</button>';
            html += '</div>';
            html += '</div>';
            html += '<div class="zato-preview-content">';

            if (type === 'none') {
                html += '<div class="zato-preview-unavailable">Preview not available</div>';
            } else if (type === 'image') {
                html += '<img class="zato-preview-image" src="' + content + '" alt="' + this.escapeHtml(title) + '">';
            } else if (type === 'pdf') {
                html += '<div class="zato-preview-pdf-container"></div>';
            } else if (type === 'word') {
                html += '<div class="zato-preview-word"></div>';
            } else {
                html += '<pre class="zato-preview-text"></pre>';
            }
            html += '</div>';

            popup.innerHTML = html;

            if (type === 'pdf') {
                this.renderPdf(popup, content);
            } else if (type === 'word') {
                this.renderWord(popup, content);
            } else if (type === 'text') {
                var preEl = popup.querySelector('.zato-preview-text');
                if (preEl) {
                    preEl.textContent = content;
                }
            }

            document.body.appendChild(popup);
            this.popups.push(popup);

            var header = popup.querySelector('.zato-preview-header');
            this.makeDraggable(popup, header);

            var closeBtn = popup.querySelector('.zato-preview-close');
            closeBtn.addEventListener('click', function() {
                self.close(popup);
            });

            var copyBtn = popup.querySelector('.zato-preview-copy-btn');
            if (copyBtn && onCopy) {
                copyBtn.addEventListener('click', function() {
                    onCopy(popup, function() {
                        copyBtn.textContent = 'Copied';
                        setTimeout(function() {
                            copyBtn.textContent = 'Copy';
                        }, 1500);
                    });
                });
            }

            popup.addEventListener('mousedown', function() {
                self.bringToFront(popup);
            });

            return popup;
        },

        close: function(popup) {
            var idx = this.popups.indexOf(popup);
            if (idx >= 0) {
                this.popups.splice(idx, 1);
            }
            if (popup.parentNode) {
                popup.parentNode.removeChild(popup);
            }
        },

        closeTop: function() {
            if (this.popups.length > 0) {
                var topPopup = this.popups[this.popups.length - 1];
                this.close(topPopup);
                return true;
            }
            return false;
        },

        bringToFront: function(popup) {
            var idx = this.popups.indexOf(popup);
            if (idx >= 0 && idx < this.popups.length - 1) {
                this.popups.splice(idx, 1);
                this.popups.push(popup);
            }
            var baseZ = 10001;
            for (var i = 0; i < this.popups.length; i++) {
                this.popups[i].style.zIndex = baseZ + i;
            }
        },

        escapeHtml: function(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        renderPdf: function(popup, dataUrl) {
            var container = popup.querySelector('.zato-preview-pdf-container');
            if (!container || typeof pdfjsLib === 'undefined') {
                var content = popup.querySelector('.zato-preview-content');
                if (content) {
                    content.innerHTML = '<div class="zato-preview-unavailable">Preview not available</div>';
                }
                return;
            }

            pdfjsLib.GlobalWorkerOptions.workerSrc = '/static/js/libs/pdf.worker.min.js';

            var base64 = dataUrl.split(',')[1];
            var binary = atob(base64);
            var len = binary.length;
            var bytes = new Uint8Array(len);
            for (var i = 0; i < len; i++) {
                bytes[i] = binary.charCodeAt(i);
            }

            pdfjsLib.getDocument({ data: bytes }).promise.then(function(pdf) {
                var numPages = pdf.numPages;
                var containerWidth = popup.querySelector('.zato-preview-content').clientWidth - 24;

                for (var pageNum = 1; pageNum <= numPages; pageNum++) {
                    (function(pageNum) {
                        pdf.getPage(pageNum).then(function(page) {
                            var viewport = page.getViewport({ scale: 1.0 });
                            var scale = containerWidth / viewport.width;
                            var scaledViewport = page.getViewport({ scale: scale });

                            var canvas = document.createElement('canvas');
                            canvas.className = 'zato-preview-pdf';
                            canvas.width = scaledViewport.width;
                            canvas.height = scaledViewport.height;
                            container.appendChild(canvas);

                            var ctx = canvas.getContext('2d');
                            page.render({ canvasContext: ctx, viewport: scaledViewport });
                        });
                    })(pageNum);
                }
            }).catch(function() {
                var content = popup.querySelector('.zato-preview-content');
                if (content) {
                    content.innerHTML = '<div class="zato-preview-unavailable">Preview not available</div>';
                }
            });
        },

        renderWord: function(popup, dataUrl) {
            var wordDiv = popup.querySelector('.zato-preview-word');
            if (!wordDiv || typeof mammoth === 'undefined') {
                var content = popup.querySelector('.zato-preview-content');
                if (content) {
                    content.innerHTML = '<div class="zato-preview-unavailable">Preview not available</div>';
                }
                return;
            }

            var base64 = dataUrl.split(',')[1];
            var binary = atob(base64);
            var len = binary.length;
            var bytes = new Uint8Array(len);
            for (var i = 0; i < len; i++) {
                bytes[i] = binary.charCodeAt(i);
            }

            mammoth.convertToHtml({ arrayBuffer: bytes.buffer }).then(function(result) {
                wordDiv.innerHTML = result.value;
            }).catch(function() {
                var content = popup.querySelector('.zato-preview-content');
                if (content) {
                    content.innerHTML = '<div class="zato-preview-unavailable">Preview not available</div>';
                }
            });
        },

        extractPdfText: function(dataUrl, callback) {
            if (typeof pdfjsLib === 'undefined') {
                callback('');
                return;
            }

            var base64 = dataUrl.split(',')[1];
            var binary = atob(base64);
            var len = binary.length;
            var bytes = new Uint8Array(len);
            for (var i = 0; i < len; i++) {
                bytes[i] = binary.charCodeAt(i);
            }

            pdfjsLib.getDocument({ data: bytes }).promise.then(function(pdf) {
                var numPages = pdf.numPages;
                var textParts = [];
                var pagesProcessed = 0;

                for (var pageNum = 1; pageNum <= numPages; pageNum++) {
                    (function(pageNum) {
                        pdf.getPage(pageNum).then(function(page) {
                            page.getTextContent().then(function(textContent) {
                                var pageText = textContent.items.map(function(item) {
                                    return item.str;
                                }).join(' ');
                                textParts[pageNum - 1] = pageText;
                                pagesProcessed++;
                                if (pagesProcessed === numPages) {
                                    callback(textParts.join('\n\n'));
                                }
                            });
                        });
                    })(pageNum);
                }
            }).catch(function() {
                callback('');
            });
        },

        makeDraggable: function(popup, handle) {
            var isDragging = false;
            var startX, startY, startLeft, startTop;

            handle.addEventListener('mousedown', function(e) {
                if (e.target.closest('.zato-preview-close') || e.target.closest('.zato-preview-copy-btn') || e.target.closest('.zato-preview-title')) {
                    return;
                }
                isDragging = true;
                startX = e.clientX;
                startY = e.clientY;
                startLeft = popup.offsetLeft;
                startTop = popup.offsetTop;
                e.preventDefault();
            });

            document.addEventListener('mousemove', function(e) {
                if (!isDragging) return;
                var dx = e.clientX - startX;
                var dy = e.clientY - startY;
                popup.style.left = (startLeft + dx) + 'px';
                popup.style.top = (startTop + dy) + 'px';
            });

            document.addEventListener('mouseup', function() {
                isDragging = false;
            });
        }
    };

    window.ZatoPreview = ZatoPreview;

})();
