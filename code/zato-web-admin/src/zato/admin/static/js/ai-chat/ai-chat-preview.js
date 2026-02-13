(function() {
    'use strict';

    var AIChatPreview = {

        getType: function(attachment) {
            var supportedImageTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp', 'image/svg+xml', 'image/bmp'];
            var isImage = attachment.type && supportedImageTypes.indexOf(attachment.type) !== -1;
            var isPdf = attachment.type === 'application/pdf' || attachment.name.toLowerCase().endsWith('.pdf');
            var isWord = attachment.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || 
                         attachment.name.toLowerCase().endsWith('.docx');
            var isText = attachment.type && (attachment.type.indexOf('text') === 0 || 
                attachment.type === 'application/json' || 
                attachment.type === 'application/javascript' ||
                attachment.type === 'application/xml');

            if (isImage) return 'image';
            if (isPdf) return 'pdf';
            if (isWord) return 'word';
            if (isText) return 'text';
            return 'none';
        },

        show: function(attachment) {
            var type = this.getType(attachment);

            var popup = ZatoPreview.show({
                id: attachment.id,
                title: attachment.name,
                content: attachment.content,
                type: type,
                onCopy: this.createCopyHandler(attachment, type)
            });

            if (popup) {
                popup.setAttribute('data-attachment-id', attachment.id);
            }
        },

        createCopyHandler: function(attachment, type) {
            return function(popup, onSuccess) {
                if (type === 'image') {
                    var img = popup.querySelector('.zato-preview-image');
                    if (img) {
                        var canvas = document.createElement('canvas');
                        canvas.width = img.naturalWidth;
                        canvas.height = img.naturalHeight;
                        var ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0);
                        canvas.toBlob(function(blob) {
                            navigator.clipboard.write([new ClipboardItem({ [blob.type]: blob })]).then(onSuccess);
                        });
                    }
                } else if (type === 'pdf') {
                    ZatoPreview.extractPdfText(attachment.content, function(text) {
                        navigator.clipboard.writeText(text).then(onSuccess);
                    });
                } else if (type === 'word') {
                    var wordDiv = popup.querySelector('.zato-preview-word');
                    var text = wordDiv ? wordDiv.innerText : '';
                    navigator.clipboard.writeText(text).then(onSuccess);
                } else {
                    navigator.clipboard.writeText(attachment.content).then(onSuccess);
                }
            };
        },

        closeTop: function() {
            return ZatoPreview.closeTop();
        }
    };

    window.AIChatPreview = AIChatPreview;

})();
