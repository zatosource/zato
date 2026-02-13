(function() {
    'use strict';

    var AIChatPreview = {
        popups: [],

        show: function(attachment) {
            var self = this;

            for (var i = 0; i < this.popups.length; i++) {
                if (this.popups[i].getAttribute('data-attachment-id') === attachment.id) {
                    this.bringToFront(this.popups[i]);
                    return;
                }
            }

            var popup = document.createElement('div');
            popup.className = 'ai-chat-preview-popup';
            popup.setAttribute('data-attachment-id', attachment.id);

            var offsetX = this.popups.length * 30;
            var offsetY = this.popups.length * 30;
            popup.style.left = (100 + offsetX) + 'px';
            popup.style.top = (100 + offsetY) + 'px';

            var supportedImageTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp', 'image/svg+xml', 'image/bmp'];
            var isImage = attachment.type && supportedImageTypes.indexOf(attachment.type) !== -1;
            var isPdf = attachment.type === 'application/pdf' || attachment.name.toLowerCase().endsWith('.pdf');
            var isWord = attachment.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || 
                         attachment.name.toLowerCase().endsWith('.docx');
            var isEmail = attachment.name.toLowerCase().endsWith('.eml') || attachment.name.toLowerCase().endsWith('.msg');
            var isText = attachment.type && (attachment.type.indexOf('text') === 0 || 
                attachment.type === 'application/json' || 
                attachment.type === 'application/javascript' ||
                attachment.type === 'application/xml');
            var canPreview = isImage || isPdf || isWord || isEmail || isText;

            var html = '';
            html += '<div class="ai-chat-preview-header">';
            html += '<div class="ai-chat-preview-title">' + attachment.name + '</div>';
            html += '<div class="ai-chat-preview-actions">';
            if (canPreview) {
                html += '<button class="ai-chat-preview-copy-btn">Copy</button>';
            }
            html += '<button class="ai-chat-preview-close">';
            html += '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';
            html += '</button>';
            html += '</div>';
            html += '</div>';
            html += '<div class="ai-chat-preview-content">';
            if (!canPreview) {
                html += '<div class="ai-chat-preview-unavailable">Preview not available</div>';
            } else if (isImage) {
                html += '<img class="ai-chat-preview-image" src="' + attachment.content + '" alt="' + attachment.name + '">';
            } else if (isPdf) {
                html += '<div class="ai-chat-preview-pdf-container"></div>';
            } else if (isWord) {
                html += '<div class="ai-chat-preview-word"></div>';
            } else {
                html += '<pre class="ai-chat-preview-text"></pre>';
            }
            html += '</div>';

            popup.innerHTML = html;

            if (isPdf) {
                this.renderPdf(popup, attachment);
            } else if (isWord) {
                this.renderWord(popup, attachment);
            } else if (!isImage && canPreview) {
                var preEl = popup.querySelector('.ai-chat-preview-text');
                if (preEl) {
                    preEl.textContent = attachment.content;
                }
            }

            document.body.appendChild(popup);
            this.popups.push(popup);

            var header = popup.querySelector('.ai-chat-preview-header');
            this.makeDraggable(popup, header);

            var closeBtn = popup.querySelector('.ai-chat-preview-close');
            closeBtn.addEventListener('click', function() {
                self.close(popup);
            });

            var copyBtn = popup.querySelector('.ai-chat-preview-copy-btn');
            if (copyBtn) {
                copyBtn.addEventListener('click', function() {
                    if (isImage) {
                        var img = popup.querySelector('.ai-chat-preview-image');
                        if (img) {
                            var canvas = document.createElement('canvas');
                            canvas.width = img.naturalWidth;
                            canvas.height = img.naturalHeight;
                            var ctx = canvas.getContext('2d');
                            ctx.drawImage(img, 0, 0);
                            canvas.toBlob(function(blob) {
                                navigator.clipboard.write([new ClipboardItem({ [blob.type]: blob })]).then(function() {
                                    copyBtn.textContent = 'Copied';
                                    setTimeout(function() {
                                        copyBtn.textContent = 'Copy';
                                    }, 1500);
                                });
                            });
                        }
                    } else if (isPdf) {
                        self.extractPdfText(attachment, function(text) {
                            navigator.clipboard.writeText(text).then(function() {
                                copyBtn.textContent = 'Copied';
                                setTimeout(function() {
                                    copyBtn.textContent = 'Copy';
                                }, 1500);
                            });
                        });
                    } else if (isWord) {
                        var wordDiv = popup.querySelector('.ai-chat-preview-word');
                        var text = wordDiv ? wordDiv.innerText : '';
                        navigator.clipboard.writeText(text).then(function() {
                            copyBtn.textContent = 'Copied';
                            setTimeout(function() {
                                copyBtn.textContent = 'Copy';
                            }, 1500);
                        });
                    } else {
                        navigator.clipboard.writeText(attachment.content).then(function() {
                            copyBtn.textContent = 'Copied';
                            setTimeout(function() {
                                copyBtn.textContent = 'Copy';
                            }, 1500);
                        });
                    }
                });
            }

            popup.addEventListener('mousedown', function() {
                self.bringToFront(popup);
            });
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

        extractPdfText: function(attachment, callback) {
            if (typeof pdfjsLib === 'undefined') {
                callback('');
                return;
            }

            var base64 = attachment.content.split(',')[1];
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

        renderPdf: function(popup, attachment) {
            var container = popup.querySelector('.ai-chat-preview-pdf-container');
            if (!container || typeof pdfjsLib === 'undefined') {
                var content = popup.querySelector('.ai-chat-preview-content');
                if (content) {
                    content.innerHTML = '<div class="ai-chat-preview-unavailable">Preview not available</div>';
                }
                return;
            }

            pdfjsLib.GlobalWorkerOptions.workerSrc = '/static/js/libs/pdf.worker.min.js';

            var base64 = attachment.content.split(',')[1];
            var binary = atob(base64);
            var len = binary.length;
            var bytes = new Uint8Array(len);
            for (var i = 0; i < len; i++) {
                bytes[i] = binary.charCodeAt(i);
            }

            pdfjsLib.getDocument({ data: bytes }).promise.then(function(pdf) {
                var numPages = pdf.numPages;
                var containerWidth = popup.querySelector('.ai-chat-preview-content').clientWidth - 24;

                for (var pageNum = 1; pageNum <= numPages; pageNum++) {
                    (function(pageNum) {
                        pdf.getPage(pageNum).then(function(page) {
                            var viewport = page.getViewport({ scale: 1.0 });
                            var scale = containerWidth / viewport.width;
                            var scaledViewport = page.getViewport({ scale: scale });

                            var canvas = document.createElement('canvas');
                            canvas.className = 'ai-chat-preview-pdf';
                            canvas.width = scaledViewport.width;
                            canvas.height = scaledViewport.height;
                            container.appendChild(canvas);

                            var ctx = canvas.getContext('2d');
                            page.render({ canvasContext: ctx, viewport: scaledViewport });
                        });
                    })(pageNum);
                }
            }).catch(function() {
                var content = popup.querySelector('.ai-chat-preview-content');
                if (content) {
                    content.innerHTML = '<div class="ai-chat-preview-unavailable">Preview not available</div>';
                }
            });
        },

        renderWord: function(popup, attachment) {
            var wordDiv = popup.querySelector('.ai-chat-preview-word');
            if (!wordDiv || typeof mammoth === 'undefined') {
                var content = popup.querySelector('.ai-chat-preview-content');
                if (content) {
                    content.innerHTML = '<div class="ai-chat-preview-unavailable">Preview not available</div>';
                }
                return;
            }

            var base64 = attachment.content.split(',')[1];
            var binary = atob(base64);
            var len = binary.length;
            var bytes = new Uint8Array(len);
            for (var i = 0; i < len; i++) {
                bytes[i] = binary.charCodeAt(i);
            }

            mammoth.convertToHtml({ arrayBuffer: bytes.buffer }).then(function(result) {
                wordDiv.innerHTML = result.value;
            }).catch(function() {
                var content = popup.querySelector('.ai-chat-preview-content');
                if (content) {
                    content.innerHTML = '<div class="ai-chat-preview-unavailable">Preview not available</div>';
                }
            });
        },

        makeDraggable: function(popup, handle) {
            var isDragging = false;
            var startX, startY, startLeft, startTop;

            handle.addEventListener('mousedown', function(e) {
                if (e.target.closest('.ai-chat-preview-close') || e.target.closest('.ai-chat-preview-copy-btn') || e.target.closest('.ai-chat-preview-title')) {
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

    window.AIChatPreview = AIChatPreview;

})();
