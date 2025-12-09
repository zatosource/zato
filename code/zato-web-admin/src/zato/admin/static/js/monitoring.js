/*
 * Monitoring functionality
 */

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.monitoring.wizard.init = function() {
    let currentStep = 1;
    const totalSteps = 3;
    let wizardData = {};

    function getURLParams() {
        const urlParams = new URLSearchParams(window.location.search);
        return {
            step: parseInt(urlParams.get('step')) || 1,
            step1: urlParams.get('step1') || '',
            step2: urlParams.get('step2') || '',
            step3: urlParams.get('step3') || ''
        };
    }

    function updateURL() {
        const params = new URLSearchParams();
        params.set('step', currentStep);
        if (wizardData.step1) params.set('step1', wizardData.step1);
        if (wizardData.step2) params.set('step2', wizardData.step2);
        if (wizardData.step3) params.set('step3', wizardData.step3);
        window.history.replaceState({}, '', '?' + params.toString());
    }

    function updateStepValues() {
        if (wizardData.step1) {
            $('#value-1 .step-value-text').text(wizardData.step1);
            $('#value-1').addClass('show');
        } else {
            $('#value-1').removeClass('show');
        }

        if (wizardData.step2) {
            const step2Text = $('#step-2 .option-item[data-value="' + wizardData.step2 + '"] .option-text').text();
            $('#value-2 .step-value-text').text(step2Text);
            $('#value-2').addClass('show');
        } else {
            $('#value-2').removeClass('show');
        }

        if (wizardData.step3) {
            const step3Text = $('#step-3 .option-item[data-value="' + wizardData.step3 + '"] .option-text').text();
            $('#value-3 .step-value-text').text(step3Text);
            $('#value-3').addClass('show');
        } else {
            $('#value-3').removeClass('show');
        }
    }

    function loadFromURL() {
        const urlData = getURLParams();
        currentStep = Math.min(Math.max(urlData.step, 1), totalSteps);
        wizardData = {
            step1: urlData.step1,
            step2: urlData.step2,
            step3: urlData.step3
        };

        if (wizardData.step1) {
            $('#step-1 input').val(wizardData.step1);
        }
        if (wizardData.step2) {
            $('#step-2 .option-item[data-value="' + wizardData.step2 + '"]').addClass('selected');
        }
        if (wizardData.step3) {
            $('#step-3 .option-item[data-value="' + wizardData.step3 + '"]').addClass('selected');
        }
        updateStepValues();
    }

    function showStep(step) {
        $('.wizard-step').hide();
        $('#step-' + step).show();

        $('.step-number').removeClass('active');
        $('.step-number').eq(step - 1).addClass('active');

        $('.step-value').removeClass('current');
        $('#value-' + step).addClass('current');

        if (step === 1) {
            $('#prev-button').hide();
            setTimeout(() => {
                $('#step-1 input, #step-1 textarea').first().focus();
            }, 100);
        } else {
            $('#prev-button').show();
        }

        if (step === totalSteps) {
            $('#next-button').text('Create Dashboard');
        } else {
            $('#next-button').text('Next');
        }

        updateURL();
    }

    $('.option-item').click(function() {
        const parent = $(this).parent();
        const stepDiv = $(this).closest('.wizard-step');
        const stepId = stepDiv.attr('id');
        const selectedValue = $(this).data('value');

        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
            if (stepId === 'step-2') {
                delete wizardData.step2;
                updateStepValues();
            } else if (stepId === 'step-3') {
                delete wizardData.step3;
                updateStepValues();
            }
        } else {
            parent.find('.option-item').removeClass('selected');
            $(this).addClass('selected');

            if (stepId === 'step-2') {
                wizardData.step2 = selectedValue;
                updateStepValues();
            } else if (stepId === 'step-3') {
                wizardData.step3 = selectedValue;
                updateStepValues();
            }
        }
    });

    function goToNextStep() {
        let isValid = false;
        let errorField = null;
        
        if (currentStep === 1) {
            const stepInput = $('#step-' + currentStep + ' input, #step-' + currentStep + ' textarea');
            if (stepInput.length && stepInput.val().trim()) {
                wizardData['step' + currentStep] = stepInput.val().trim();
                isValid = true;
            } else {
                errorField = $('#step-' + currentStep + ' .input-wrapper');
            }
        } else {
            const selectedOption = $('#step-' + currentStep + ' .option-item.selected');
            if (selectedOption.length) {
                wizardData['step' + currentStep] = selectedOption.data('value');
                isValid = true;
            } else {
                errorField = $('#step-' + currentStep + ' .option-item');
            }
        }

        if (isValid) {
            updateStepValues();

            if (currentStep < totalSteps) {
                currentStep++;
                showStep(currentStep);
            } else {
                const step1Value = $('#step-1 input').val()?.trim() || '';
                const step2Selected = $('#step-2 .option-item.selected').length > 0;
                const step3Selected = $('#step-3 .option-item.selected').length > 0;
                
                const missingSteps = [];
                if (!step1Value) missingSteps.push('▶ 1. What do you want to monitor?');
                if (!step2Selected) missingSteps.push('▶ 2. What do you want to track?');
                if (!step3Selected) missingSteps.push('▶ 3. How far back to look?');
                
                if (missingSteps.length > 0) {
                    const tooltipText = 'Please complete the following:<br>' + missingSteps.join('<br>');
                    
                    const button = document.getElementById('next-button');
                    if (button._tippy) {
                        button._tippy.destroy();
                    }
                    
                    let _tooltip = tippy(button, {
                        content: tooltipText,
                        allowHTML: true,
                        theme: "dark",
                        trigger: "manual",
                        placement: "bottom",
                        arrow: true,
                        interactive: false,
                        inertia: true,
                        role: "tooltip-draw-attention",
                    });
                    
                    _tooltip.show();
                    $('#next-button').blur();
                } else {
                    alert('Wizard Complete!');
                }
            }
        } else {
            if (currentStep === totalSteps) {
                const step1Value = $('#step-1 input').val()?.trim() || '';
                const step2Selected = $('#step-2 .option-item.selected').length > 0;
                const step3Selected = $('#step-3 .option-item.selected').length > 0;

                const missingSteps = [];
                if (!step1Value) missingSteps.push('▶ 1. What do you want to monitor?');
                if (!step2Selected) missingSteps.push('▶ 2. What do you want to track?');
                if (!step3Selected) missingSteps.push('▶ 3. How far back to look?');

                if (missingSteps.length > 0) {
                    const tooltipText = 'Please complete the following:<br>' + missingSteps.join('<br>');
                    
                    const button = document.getElementById('next-button');
                    if (button._tippy) {
                        button._tippy.destroy();
                    }
                    
                    let _tooltip = tippy(button, {
                        content: tooltipText,
                        allowHTML: true,
                        theme: "dark",
                        trigger: "manual",
                        placement: "bottom",
                        arrow: true,
                        interactive: false,
                        inertia: true,
                        role: "tooltip-draw-attention",
                    });
                    
                    _tooltip.show();
                    $('#next-button').blur();
                }
            } else if (errorField) {
                $('#next-button').blur();
                
                if (currentStep === 1) {
                    const inputField = $('#step-1 input, #step-1 textarea').first();
                    if (inputField.length) {
                        setTimeout(() => {
                            inputField.focus();
                        }, 100);
                    }
                }
                
                errorField.removeClass('field-error');
                setTimeout(() => {
                    errorField.addClass('field-error');
                }, 10);
                setTimeout(() => {
                    errorField.removeClass('field-error');
                }, 1600);
            }
        }
    }

    $('#next-button').click(goToNextStep);

    $('input.input-field').on('keypress', function(e) {
        if (e.which === 13) {
            goToNextStep();
        }
    });

    $('#step-1 input').on('input', function() {
        const value = $(this).val().trim();
        if (value) {
            wizardData.step1 = value;
            updateStepValues();
        } else {
            delete wizardData.step1;
            updateStepValues();
        }
    });

    $('#prev-button').click(function() {
        if (currentStep > 1) {
            currentStep--;
            showStep(currentStep);
        }
    });

    function focusStepInput(stepNumber) {
        if (stepNumber === 1) {
            $('#step-1 input').focus();
        } else if (stepNumber === 2 || stepNumber === 3) {
            $('#step-' + stepNumber + ' .option-group').focus();
        }
    }

    $('.step-number').click(function() {
        const stepIndex = $('.step-number').index(this) + 1;
        currentStep = stepIndex;
        showStep(currentStep);
        focusStepInput(currentStep);
    });

    $('.step-value').click(function() {
        const stepId = $(this).attr('id');
        const stepNumber = parseInt(stepId.split('-')[1]);
        currentStep = stepNumber;
        showStep(currentStep);
        focusStepInput(currentStep);
    });

    loadFromURL();
    showStep(currentStep);
};
