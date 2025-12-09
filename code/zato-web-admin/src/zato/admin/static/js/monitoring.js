/*
 * Monitoring functionality
 */

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.monitoring.wizard.generateHTML = function() {
    // Wizard configuration - shared with init function
    const wizardConfig = {
        steps: [
            {
                id: 'step1',
                question: 'What do you want to monitor?',
                type: 'input',
                placeholder: 'Enter what you want to monitor...'
            },
            {
                id: 'step2',
                question: 'What do you want to track?',
                type: 'options',
                options: [
                    { value: 'current-status', text: 'Current status' },
                    { value: 'error-rate', text: 'Error rate' },
                    { value: 'uptime', text: 'Uptime' },
                    { value: 'activity', text: 'Activity' }
                ]
            },
            {
                id: 'step3',
                question: 'How far back to look?',
                type: 'options',
                options: [
                    { value: 'real-time', text: 'Right now' },
                    { value: 'last-hour', text: 'Last hour' },
                    { value: 'last-day', text: 'Last day' },
                    { value: 'last-week', text: 'Last week' },
                    { value: 'last-month', text: 'Last month' }
                ]
            }
        ]
    };

    // Generate complete stepper structure in original order
    let stepperHTML = '';
    
    // Add step values first
    wizardConfig.steps.forEach((step, index) => {
        const stepNum = index + 1;
        stepperHTML += `<div class="step-value" id="value-${stepNum}"><div class="step-value-text"></div><div class="step-arrow">▶</div></div>`;
    });
    
    // Add title
    stepperHTML += '<h1 class="wizard-title">Is it working?</h1>';
    
    // Add step numbers with connectors
    wizardConfig.steps.forEach((step, index) => {
        const stepNum = index + 1;
        stepperHTML += `<div class="step"><div class="step-number">${stepNum}</div></div>`;
        if (index < wizardConfig.steps.length - 1) {
            stepperHTML += '<div class="step-connector"></div>';
        }
    });
    
    $('#stepper-container').html(stepperHTML);

    // Generate wizard steps content
    let stepsHTML = '';
    wizardConfig.steps.forEach((stepConfig, index) => {
        const stepNum = index + 1;
        const displayStyle = stepNum === 1 ? '' : 'style="display: none;"';
        
        stepsHTML += `<div id="step-${stepNum}" class="wizard-step" ${displayStyle}>`;
        stepsHTML += `<h1 class="question-title">${stepNum}. ${stepConfig.question}</h1>`;
        
        if (stepConfig.type === 'input') {
            stepsHTML += `<div class="input-wrapper">`;
            stepsHTML += `<input type="text" class="input-field" placeholder="${stepConfig.placeholder}" />`;
            stepsHTML += `</div>`;
        } else if (stepConfig.type === 'options') {
            stepsHTML += `<div class="option-group">`;
            stepConfig.options.forEach(option => {
                stepsHTML += `<div class="option-item" data-value="${option.value}">`;
                stepsHTML += `<div class="option-radio"></div>`;
                stepsHTML += `<div class="option-text">${option.text}</div>`;
                stepsHTML += `</div>`;
            });
            stepsHTML += `</div>`;
        }
        
        stepsHTML += `</div>`;
    });
    $('#wizard-steps-container').html(stepsHTML);

    // Store config in the namespace for use by init function
    $.fn.zato.monitoring.wizard.config = wizardConfig;
    
    // Position step values to align with step numbers after DOM is ready
    setTimeout(() => {
        $('.step-number').each(function(index) {
            const stepNumber = $(this);
            const stepValue = $(`#value-${index + 1}`);
            const position = stepNumber.offset();
            const containerOffset = $('.stepper').offset();
            const relativeTop = position.top - containerOffset.top;
            stepValue.css('top', relativeTop + 'px');
        });
    }, 0);
};

$.fn.zato.monitoring.wizard.init = function() {
    // Use the config stored by generateHTML function
    const wizardConfig = $.fn.zato.monitoring.wizard.config;
    
    let currentStep = 1;
    const totalSteps = wizardConfig.steps.length;
    let wizardData = {};

    function getURLParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const params = {
            step: parseInt(urlParams.get('step')) || 1
        };
        
        wizardConfig.steps.forEach((step, index) => {
            const stepKey = `step${index + 1}`;
            params[stepKey] = urlParams.get(stepKey) || '';
        });
        
        return params;
    }

    function updateURL() {
        const params = new URLSearchParams();
        params.set('step', currentStep);
        
        wizardConfig.steps.forEach((step, index) => {
            const stepKey = `step${index + 1}`;
            if (wizardData[stepKey]) {
                params.set(stepKey, wizardData[stepKey]);
            }
        });
        
        window.history.replaceState({}, '', '?' + params.toString());
    }

    function updateStepValues() {
        wizardConfig.steps.forEach((stepConfig, index) => {
            const stepNum = index + 1;
            const stepKey = `step${stepNum}`;
            const valueElement = $(`#value-${stepNum}`);
            const textElement = $(`#value-${stepNum} .step-value-text`);
            
            if (wizardData[stepKey]) {
                if (stepConfig.type === 'input') {
                    textElement.text(wizardData[stepKey]);
                } else if (stepConfig.type === 'options') {
                    const optionText = $(`#step-${stepNum} .option-item[data-value="${wizardData[stepKey]}"] .option-text`).text();
                    textElement.text(optionText);
                }
                valueElement.addClass('show');
            } else {
                valueElement.removeClass('show');
            }
        });
    }

    function loadFromURL() {
        const urlData = getURLParams();
        currentStep = Math.min(Math.max(urlData.step, 1), totalSteps);
        
        wizardConfig.steps.forEach((stepConfig, index) => {
            const stepKey = `step${index + 1}`;
            wizardData[stepKey] = urlData[stepKey];
            
            if (wizardData[stepKey]) {
                if (stepConfig.type === 'input') {
                    $(`#step-${index + 1} input`).val(wizardData[stepKey]);
                } else if (stepConfig.type === 'options') {
                    $(`#step-${index + 1} .option-item[data-value="${wizardData[stepKey]}"]`).addClass('selected');
                }
            }
        });
        
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
            const stepNumber = parseInt(stepId.replace('step-', ''));
            const stepKey = `step${stepNumber}`;
            delete wizardData[stepKey];
            updateStepValues();
        } else {
            parent.find('.option-item').removeClass('selected');
            $(this).addClass('selected');

            const stepNumber = parseInt(stepId.replace('step-', ''));
            const stepKey = `step${stepNumber}`;
            wizardData[stepKey] = selectedValue;
            updateStepValues();
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
                const missingSteps = [];
                
                wizardConfig.steps.forEach((stepConfig, index) => {
                    const stepNum = index + 1;
                    const stepKey = `step${stepNum}`;
                    
                    if (stepConfig.type === 'input') {
                        const value = $(`#step-${stepNum} input`).val()?.trim() || '';
                        if (!value) {
                            missingSteps.push(`▶ ${stepNum}. ${stepConfig.question}`);
                        }
                    } else if (stepConfig.type === 'options') {
                        const selected = $(`#step-${stepNum} .option-item.selected`).length > 0;
                        if (!selected) {
                            missingSteps.push(`▶ ${stepNum}. ${stepConfig.question}`);
                        }
                    }
                });

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
                const missingSteps = [];
                
                wizardConfig.steps.forEach((stepConfig, index) => {
                    const stepNum = index + 1;
                    
                    if (stepConfig.type === 'input') {
                        const value = $(`#step-${stepNum} input`).val()?.trim() || '';
                        if (!value) {
                            missingSteps.push(`▶ ${stepNum}. ${stepConfig.question}`);
                        }
                    } else if (stepConfig.type === 'options') {
                        const selected = $(`#step-${stepNum} .option-item.selected`).length > 0;
                        if (!selected) {
                            missingSteps.push(`▶ ${stepNum}. ${stepConfig.question}`);
                        }
                    }
                });

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

    $('input.input-field').on('input', function() {
        const stepDiv = $(this).closest('.wizard-step');
        const stepId = stepDiv.attr('id');
        const stepNumber = parseInt(stepId.replace('step-', ''));
        const stepKey = `step${stepNumber}`;
        const value = $(this).val().trim();
        
        if (value) {
            wizardData[stepKey] = value;
            updateStepValues();
        } else {
            delete wizardData[stepKey];
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
