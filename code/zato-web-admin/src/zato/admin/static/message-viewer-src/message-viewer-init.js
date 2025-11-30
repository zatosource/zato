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
        return;
    } catch (e) {
    }
    
    if (typeof responseText === 'string' && responseText.includes('ValueError: ')) {
        const lines = responseText.split('\n');
        for (const line of lines) {
            const valueErrorIndex = line.indexOf('ValueError: ');
            if (valueErrorIndex !== -1) {
                let textToDisplay = line.substring(valueErrorIndex + 'ValueError: '.length).trim();
                if ((textToDisplay.startsWith("'") && textToDisplay.endsWith("'")) ||
                    (textToDisplay.startsWith('"') && textToDisplay.endsWith('"'))) {
                    textToDisplay = textToDisplay.slice(1, -1);
                }
                window.zato.messageViewer.setMessageFormatted(textToDisplay);
                return;
            }
        }
    }
    
    window.zato.messageViewer.setMessagePlainText(responseText);
};
