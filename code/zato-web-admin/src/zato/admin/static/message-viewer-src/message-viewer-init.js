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
    
    let data;
    let isJSON = false;
    try {
        data = JSON.parse(responseText);
        isJSON = true;
    } catch (e) {
        data = { response: responseText };
    }
    
    window.zato.messageViewer.setMessage(data);
};
