import { MessageViewerManager } from './message-viewer-manager.js';

window.zato = window.zato || {};
window.zato.messageViewer = new MessageViewerManager();

window.zato.initializeMessageViewer = function() {
    window.zato.messageViewer.initialize('message-viewer-wrapper');
};

window.zato.updateMessageViewer = function(responseText) {
    if (!responseText) {
        return;
    }
    
    try {
        const data = JSON.parse(responseText);
        window.zato.messageViewer.setMessage(data);
    } catch (e) {
        window.zato.messageViewer.setMessagePlainText(responseText);
    }
};
