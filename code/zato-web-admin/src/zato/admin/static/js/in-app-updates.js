$(document).ready(function() {
    
    $('#install-updates-button').on('click', function() {
        const button = $(this);
        const spinnerContainer = $('#spinner-container');
        const statusMessage = $('#status-message');
        
        button.prop('disabled', true);
        button.fadeOut(300, function() {
            spinnerContainer.addClass('active');
            
            const messages = [
                'Preparing installation...',
                'Downloading update package...',
                'Verifying package integrity...',
                'Installing updates...',
                'Finalizing installation...'
            ];
            
            let currentMessageIndex = 0;
            
            const updateMessage = function() {
                if (currentMessageIndex < messages.length) {
                    statusMessage.fadeOut(200, function() {
                        statusMessage.text(messages[currentMessageIndex]);
                        statusMessage.fadeIn(200);
                        currentMessageIndex++;
                        setTimeout(updateMessage, 2000);
                    });
                } else {
                    statusMessage.fadeOut(200, function() {
                        statusMessage.html('<strong>Installation complete!</strong><br>Redirecting to download page...');
                        statusMessage.fadeIn(200);
                        
                        setTimeout(function() {
                            window.location.href = 'https://zato.io/downloads/latest';
                        }, 2000);
                    });
                }
            };
            
            updateMessage();
        });
    });
    
});
