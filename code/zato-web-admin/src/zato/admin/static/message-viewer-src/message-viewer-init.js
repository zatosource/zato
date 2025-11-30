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
    
    let textToDisplay = responseText;
    
    try {
        const data = JSON.parse(responseText);
        window.zato.messageViewer.setMessage(data);
        return;
    } catch (e) {
    }
    
    if (typeof responseText === 'string' && responseText.includes('ValueError: ')) {
        const lines = responseText.split('\n');
        for (const line of lines) {
            const valueErrorIndex = line.indexOf('ValueError: ');
            if (valueErrorIndex !== -1) {
                textToDisplay = line.substring(valueErrorIndex + 'ValueError: '.length).trim();
                break;
            }
        }
    }
    
    window.zato.messageViewer.setMessageFormatted(textToDisplay);
};
