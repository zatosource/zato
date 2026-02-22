(function() {
    'use strict';

    ZatoIDETabs.showSaveDialog = function(instance, filename, callbacks) {
        var overlay = document.createElement('div');
        overlay.className = 'zato-tabs-save-dialog-overlay';
        var dialog = document.createElement('div');
        dialog.className = 'zato-tabs-save-dialog';
        var header = document.createElement('div');
        header.className = 'zato-tabs-save-dialog-header';
        var title = document.createElement('div');
        title.className = 'zato-tabs-save-dialog-title';
        title.textContent = 'Save changes';
        var closeBtn = document.createElement('button');
        closeBtn.className = 'zato-tabs-save-dialog-close';
        closeBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';
        header.appendChild(title);
        header.appendChild(closeBtn);
        var content = document.createElement('div');
        content.className = 'zato-tabs-save-dialog-content';
        var message = document.createElement('div');
        message.className = 'zato-tabs-save-dialog-message';
        message.innerHTML = 'Do you want to save the changes you made to <strong>' + filename + '</strong>?<br>Your changes will be lost if you don\'t save them.';
        var buttons = document.createElement('div');
        buttons.className = 'zato-tabs-save-dialog-buttons';
        var dontSaveBtn = document.createElement('button');
        dontSaveBtn.className = 'zato-tabs-save-dialog-btn zato-tabs-save-dialog-btn-secondary';
        dontSaveBtn.textContent = 'Don\'t Save';
        var cancelBtn = document.createElement('button');
        cancelBtn.className = 'zato-tabs-save-dialog-btn zato-tabs-save-dialog-btn-secondary';
        cancelBtn.textContent = 'Cancel';
        var saveBtn = document.createElement('button');
        saveBtn.className = 'zato-tabs-save-dialog-btn zato-tabs-save-dialog-btn-default';
        saveBtn.textContent = 'Save';
        buttons.appendChild(dontSaveBtn);
        buttons.appendChild(cancelBtn);
        buttons.appendChild(saveBtn);
        content.appendChild(message);
        content.appendChild(buttons);
        dialog.appendChild(header);
        dialog.appendChild(content);
        overlay.appendChild(dialog);
        document.body.appendChild(overlay);
        dialog.style.left = '50%';
        dialog.style.top = '50%';
        dialog.style.transform = 'translate(-50%, -50%)';
        this.makeDialogDraggable(dialog, header, closeBtn);
        var closeDialog = function() { document.body.removeChild(overlay); };
        closeBtn.addEventListener('click', function() { closeDialog(); if (callbacks.onCancel) { callbacks.onCancel(); } });
        dontSaveBtn.addEventListener('click', function() { closeDialog(); if (callbacks.onDontSave) { callbacks.onDontSave(); } });
        cancelBtn.addEventListener('click', function() { closeDialog(); if (callbacks.onCancel) { callbacks.onCancel(); } });
        saveBtn.addEventListener('click', function() { closeDialog(); if (callbacks.onSave) { callbacks.onSave(); } });
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) { closeDialog(); if (callbacks.onCancel) { callbacks.onCancel(); } }
        });
        var escHandler = function(e) {
            if (e.key === 'Escape') { closeDialog(); document.removeEventListener('keydown', escHandler); if (callbacks.onCancel) { callbacks.onCancel(); } }
        };
        document.addEventListener('keydown', escHandler);
        saveBtn.focus();
    };

    ZatoIDETabs.makeDialogDraggable = function(dialog, handle, excludeElement) {
        var isDragging = false;
        var startX, startY, startLeft, startTop;
        handle.addEventListener('mousedown', function(e) {
            if (excludeElement && e.target.closest('.zato-tabs-save-dialog-close')) { return; }
            isDragging = true;
            var rect = dialog.getBoundingClientRect();
            startLeft = rect.left;
            startTop = rect.top;
            dialog.style.transform = 'none';
            dialog.style.left = startLeft + 'px';
            dialog.style.top = startTop + 'px';
            startX = e.clientX;
            startY = e.clientY;
            e.preventDefault();
        });
        document.addEventListener('mousemove', function(e) {
            if (!isDragging) return;
            dialog.style.left = (startLeft + e.clientX - startX) + 'px';
            dialog.style.top = (startTop + e.clientY - startY) + 'px';
        });
        document.addEventListener('mouseup', function() { isDragging = false; });
    };

})();
