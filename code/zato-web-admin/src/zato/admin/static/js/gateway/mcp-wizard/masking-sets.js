// MCP gateway wizard - the industry sets of data masking.
//
// Each set lists the fields one industry typically masks. The Data masking
// popover reads the sets through the functions below and never through the
// lists directly.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var maskingSets = wizard.maskingSets;

// ////////////////////////////////////////////////////////////////////////

maskingSets.config = {

    sets: [
        {
            name: 'common',
            label: 'Common',
            fields: ['password', 'secret', 'api_key', 'access_token', 'refresh_token', 'private_key', 'client_secret',
                'session_id', 'otp_code', 'security_answer', 'email', 'phone', 'mobile_phone', 'first_name',
                'last_name', 'full_name', 'date_of_birth', 'home_address', 'postal_code', 'ip_address', 'device_id',
                'national_id', 'signature', 'geolocation', 'username']
        },
        {
            name: 'healthcare',
            label: 'Healthcare',
            fields: ['medical_record_number', 'ssn', 'diagnosis_code', 'procedure_code', 'insurance_member_id',
                'prescription', 'lab_result', 'clinical_notes', 'allergy_list', 'emergency_contact',
                'attending_physician']
        },
        {
            name: 'banking',
            label: 'Banking',
            fields: ['account_number', 'routing_number', 'iban', 'swift_bic', 'card_number', 'cvv', 'pin', 'balance',
                'credit_score', 'transaction_memo', 'beneficiary_name', 'loan_number']
        },
        {
            name: 'payments',
            label: 'Payments',
            fields: ['card_number', 'cvv', 'expiry_date', 'cardholder_name', 'pan_token', 'track_data', 'merchant_id',
                'terminal_id', 'authorization_code']
        },
        {
            name: 'insurance',
            label: 'Insurance',
            fields: ['policy_number', 'claim_number', 'ssn', 'beneficiary_name', 'medical_history',
                'driver_license_number', 'premium_amount', 'adjuster_notes']
        },
        {
            name: 'telecom',
            label: 'Telecom',
            fields: ['imsi', 'imei', 'msisdn', 'iccid', 'sim_pin', 'puk_code', 'call_detail_record', 'cell_tower_id',
                'location', 'billing_account']
        },
        {
            name: 'retail',
            label: 'Retail',
            fields: ['card_number', 'cvv', 'gift_card_code', 'loyalty_number', 'shipping_address', 'billing_address',
                'email', 'phone', 'purchase_history']
        },
        {
            name: 'public_sector',
            label: 'Public sector',
            fields: ['ssn', 'passport_number', 'driver_license_number', 'case_number', 'voter_id', 'benefits_id',
                'criminal_record', 'immigration_status']
        },
        {
            name: 'human_resources',
            label: 'Human resources',
            fields: ['employee_id', 'ssn', 'salary', 'bank_account', 'date_of_birth', 'performance_rating',
                'disciplinary_record', 'health_condition', 'marital_status', 'background_check']
        },
        {
            name: 'identity_and_access',
            label: 'Identity and access',
            fields: ['username', 'password_hash', 'mfa_secret', 'recovery_code', 'saml_assertion', 'id_token',
                'authorization_code', 'certificate', 'ssh_key', 'login_history']
        },
        {
            name: 'payroll',
            label: 'Payroll',
            fields: ['employee_id', 'gross_pay', 'net_pay', 'bank_account', 'iban', 'deductions', 'pension_number',
                'garnishment', 'bonus_amount']
        },
        {
            name: 'finance',
            label: 'Finance',
            fields: ['account_number', 'iban', 'invoice_amount', 'credit_limit', 'vat_number', 'bank_statement',
                'ledger_entry', 'budget_line']
        },
        {
            name: 'expenses',
            label: 'Expenses',
            fields: ['corporate_card_number', 'receipt_image', 'merchant_name', 'expense_amount', 'cost_center',
                'mileage_log', 'approver_notes']
        },
        {
            name: 'sales',
            label: 'Sales and CRM',
            fields: ['contact_name', 'contact_email', 'contact_phone', 'company_revenue', 'deal_value', 'discount',
                'opportunity_notes', 'quote_amount', 'lead_source']
        },
        {
            name: 'marketing',
            label: 'Marketing',
            fields: ['email', 'subscriber_id', 'consent_status', 'campaign_response', 'audience_segment',
                'tracking_cookie', 'ad_id', 'unsubscribe_token']
        },
        {
            name: 'customer_support',
            label: 'Customer support',
            fields: ['ticket_description', 'customer_name', 'customer_email', 'customer_phone', 'chat_transcript',
                'call_recording', 'attachment', 'satisfaction_comment']
        },
        {
            name: 'procurement',
            label: 'Procurement',
            fields: ['supplier_bank_account', 'supplier_tax_number', 'contract_value', 'unit_price',
                'purchase_order_amount', 'payment_terms', 'supplier_contact']
        },
        {
            name: 'it_operations',
            label: 'IT operations',
            fields: ['hostname', 'ip_address', 'mac_address', 'asset_tag', 'caller_name', 'caller_email',
                'incident_notes', 'connection_string']
        }
    ]
};

// ////////////////////////////////////////////////////////////////////////

// Every set, in the order the popover shows them.
maskingSets.all = function() {

    var out = maskingSets.config.sets;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

maskingSets.get = function(setName) {

    var sets = maskingSets.config.sets;

    for(var setIdx = 0; setIdx < sets.length; setIdx++) {
        if(sets[setIdx].name === setName) {
            var out = sets[setIdx];
            return out;
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

maskingSets.allFieldsOf = function(setName) {

    var out = maskingSets.get(setName).fields;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The list with every name it does not hold yet appended at its end.
maskingSets.merge = function(fieldList, names) {

    var out = fieldList.slice();

    for(var nameIdx = 0; nameIdx < names.length; nameIdx++) {
        if(out.indexOf(names[nameIdx]) === -1) {
            out.push(names[nameIdx]);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

maskingSets.subtract = function(fieldList, names) {

    var out = [];

    for(var fieldIdx = 0; fieldIdx < fieldList.length; fieldIdx++) {
        if(names.indexOf(fieldList[fieldIdx]) === -1) {
            out.push(fieldList[fieldIdx]);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The fields of several sets, each field once.
maskingSets.union = function(setNames) {

    var out = [];

    for(var setIdx = 0; setIdx < setNames.length; setIdx++) {
        out = maskingSets.merge(out, maskingSets.allFieldsOf(setNames[setIdx]));
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
