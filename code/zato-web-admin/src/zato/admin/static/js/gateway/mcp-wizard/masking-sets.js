// MCP gateway wizard - the industry sets of data masking.
//
// Each set lists the personal and confidential field names used by the APIs
// of widely adopted products in one category, ordered by the number of those
// products that use each name. Field names are compared without regard to
// case, which is why every name is held in lowercase and only once. The Data
// masking popover reads the sets through the functions below and never
// through the lists directly.

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
            fields: ['email', 'phone', 'mobilephone', 'password', 'fax', 'firstname', 'lastname', 'givenname', 'city',
                'addresses', 'name', 'address', 'homephone', 'middlename', 'birthdate', 'mailingstreet', 'mailingcity',
                'mailingpostalcode', 'otherphone', 'assistantphone', 'photourl', 'mail', 'businessphones', 'faxnumber',
                'surname', 'displayname', 'birthday', 'streetaddress', 'postalcode', 'userprincipalname', 'othermails',
                'passwordprofile', 'employeeid', 'primaryemail', 'recoveryemail', 'recoveryphone', 'familyname',
                'fullname', 'phones', 'emails', 'gender', 'sshpublickeys', 'individual_name', 'business_name',
                'shipping', 'tax_ids', 'phone_number', 'given_name', 'family_name', 'nickname', 'username', 'picture',
                'password_hash', 'last_ip', 'identities', 'zip', 'company', 'first_name', 'last_name',
                'default_address', 'note']
        },
        {
            name: 'healthcare',
            label: 'Healthcare',
            fields: ['birthdate', 'gender', 'maritalstatus', 'identifier', 'name', 'telecom', 'address', 'contact',
                'photo', 'deceasedboolean', 'deceaseddatetime', 'birthdatetime', 'names', 'aliases', 'addresses',
                'telecoms', 'birthsex', 'ethnicities', 'races', 'dateofdeath', 'sourceidentifier', 'firstname',
                'lastname', 'dob', 'ssn', 'sex', 'email', 'homephone', 'mobilephone', 'workphone', 'address1',
                'address2', 'city', 'zip', 'guarantorssn', 'contactname', 'contacthomephone', 'contactmobilephone']
        },
        {
            name: 'banking',
            label: 'Banking',
            fields: ['email', 'lastname', 'addresses', 'iban', 'bban', 'bic', 'customermnemonic', 'givenname',
                'dateofbirth', 'gender', 'communicationdevices', 'phonenumber', 'smsnumber', 'postcode',
                'nationalityid', 'residenceid', 'employdetails', 'salaryamount', 'firstname', 'phone', 'taxident',
                'personpartyinfo', 'residencecode', 'accountnumber', 'routingnumber', 'accountholdername', 'swiftcode',
                'bankname', 'availablebalance', 'currentbalance', 'accountid', 'accountname', 'dob', 'city', 'names',
                'phone_numbers', 'emails', 'routing', 'verification_name', 'wire_routing', 'pan', 'maskedpan', 'msisdn',
                'ownername', 'name', 'displayname', 'balances']
        },
        {
            name: 'payments',
            label: 'Payments',
            fields: ['cvc', 'phone', 'name', 'exp_month', 'exp_year', 'cvv', 'cardholdername', 'postalcode', 'email',
                'line1', 'postal_code', 'last4', 'routing_number', 'iban', 'holdername', 'expirymonth', 'expiryyear',
                'encryptedcardnumber', 'shopperemail', 'shoppername', 'billingaddress', 'deliveryaddress',
                'telephonenumber', 'expirationdate', 'expirationmonth', 'expirationyear', 'streetaddress', 'firstname',
                'lastname', 'cardnumber', 'address1', 'city', 'lastfour', 'paymentaccountreference', 'expiry_month',
                'expiry_year', 'pin', 'address_line1', 'zip', 'email_address', 'phone_number', 'given_name',
                'family_name', 'birthday', 'address', 'cardholder_name', 'last_4', 'bin', 'expdate', 'chname', 'cvn',
                'payerref']
        },
        {
            name: 'insurance',
            label: 'Insurance',
            fields: ['firstname', 'lastname', 'dateofbirth', 'city', 'phonenumber', 'taxid', 'primaryphone', 'email',
                'phone', 'name', 'street1', 'postalcode', 'mailingaddress', 'emailaddress', 'socialsecuritynumber',
                'emailaddress1', 'emailaddress2', 'primaryaddress', 'companyname', 'workphone', 'ssn', 'street2',
                'zipcode', 'taxidentificationnumber', 'addressline1', 'driverslicensenumber', 'email1', 'address',
                'birthdt', 'emailaddr', 'givenname', 'surname', 'addr', 'taxidentity']
        },
        {
            name: 'telecom',
            label: 'Telecom',
            fields: ['phonenumber', 'birthdate', 'emailaddress', 'givenname', 'familyname', 'contactmedium', 'msisdn',
                'email', 'phone', 'accountnumber', 'firstname', 'lastname', 'companyname', 'address', 'iccid', 'imsi',
                'imei', 'request_source_ip', 'preferredgivenname', 'placeofbirth', 'nationality', 'customername',
                'street', 'streetsecondary', 'postalcode', 'city', 'phone_number', 'email_address', 'target_api_key']
        },
        {
            name: 'retail',
            label: 'Retail',
            fields: ['email', 'phone', 'password', 'city', 'firstname', 'lastname', 'first_name', 'last_name',
                'company', 'address1', 'address2', 'middlename', 'fax', 'login', 'password_confirmation', 'zip', 'note',
                'multipass_identifier', 'dob', 'telephone', 'taxvat', 'gender', 'street', 'postcode', 'vat_id',
                'second_name', 'phone_home', 'phone_business', 'phone_mobile', 'birthday', 'company_name', 'holder',
                'masked_number', 'number_last_digits', 'bank_routing_number', 'uid', 'displayuid', 'name',
                'defaultaddress', 'paymentdetails', 'registration_ip_address', 'postal_code', 'last_4', 'expiry_month',
                'expiry_year', 'token', 'dateofbirth', 'vatid', 'companyname', 'streetname', 'streetnumber',
                'postalcode', 'mobile', 'daytimetelephonenumber', 'shippingaddress']
        },
        {
            name: 'public_sector',
            label: 'Public sector',
            fields: ['firstname', 'lastname', 'fax', 'email', 'phone', 'mobilephone', 'birthdate', 'dob', 'ssn', 'dl',
                'address1', 'city', 'zip', 'homephone', 'mailingstreet', 'mailingcity', 'mailingpostalcode',
                'suppliedemail', 'suppliedphone', 'suppliedname', 'contactemail', 'contactphone', 'contactmobile',
                'emailaddress1', 'telephone1', 'address1_line1', 'address1_city', 'address1_postalcode', 'governmentid',
                'phone1', 'phone2', 'phone3', 'driverlicensenumber', 'addressline1', 'postalcode', 'user_email',
                'email_address', 'mobile_number', 'phone_number', 'persongivenname', 'personsurname', 'personbirthdate',
                'personssnidentification', 'identificationid', 'contactemailid', 'contacttelephonenumber']
        },
        {
            name: 'human_resources',
            label: 'Human resources',
            fields: ['dateofbirth', 'emailaddress', 'firstname', 'lastname', 'phonenumber', 'legalname', 'addressline1',
                'zipcode', 'city', 'ssn', 'homephone', 'email', 'preferredname', 'homephones', 'workphones',
                'homeemails', 'workemails', 'personidexternal', 'personnumber', 'displayname', 'fullname', 'birthdate',
                'emailuri', 'formattednumber', 'idvalue', 'legaladdress', 'worknumber', 'addresscity', 'addresszipcode',
                'nationalid', 'homeemail', 'workemail', 'address1', 'first_name', 'last_name', 'preferred_name',
                'gender', 'date_of_birth', 'iban', 'fix_salary', 'hourly_salary']
        },
        {
            name: 'identity_and_access',
            label: 'Identity and access',
            fields: ['email', 'streetaddress', 'username', 'givenname', 'displayname', 'mobilephone', 'postalcode',
                'firstname', 'lastname', 'name', 'mail', 'primaryphone', 'familyname', 'emails', 'phonenumbers',
                'userprincipalname', 'surname', 'businessphones', 'city', 'employeeid', 'birthday', 'passwordprofile',
                'othermails', 'login', 'secondemail', 'employeenumber', 'locality', 'given_name', 'family_name',
                'phone_number', 'password', 'password_hash', 'picture', 'last_ip', 'identities', 'emailaddress',
                'phone', 'workphone', 'personalemail', 'identificationnumber', 'mobilenumber', 'officenumber',
                'homenumber', 'credentials']
        },
        {
            name: 'payroll',
            label: 'Payroll',
            fields: ['firstname', 'lastname', 'birthdate', 'middlename', 'phone', 'homephone', 'givenname',
                'communications', 'dateofbirth', 'email', 'socialsecuritynumber', 'electronicaddress', 'ssn',
                'emailaddress', 'governmentids', 'idvalue', 'legalname', 'familyname1', 'workerid', 'primaryworkemail',
                'primaryworkphone', 'primaryworkaddresstext', 'familyname', 'legalid', 'legalidvalue', 'employeeid',
                'emailaddressalternate', 'cellphone', 'addressline1', 'addressline2', 'city', 'zipcode', 'loginid',
                'displayname', 'maidenname', 'national_id_card', 'direct_deposit', 'payment_information',
                'pernationalid', 'peremail', 'perpersonal', 'perphone', 'first_name', 'last_name', 'work_email',
                'date_of_birth', 'home_address', 'routing_number', 'account_number', 'middle_initial',
                'preferred_first_name']
        },
        {
            name: 'finance',
            label: 'Finance',
            fields: ['firstname', 'lastname', 'emailaddress', 'phonenumber', 'email', 'companyname', 'bankaccount',
                'iban', 'businesspartnerbank', 'streetname', 'cityname', 'postalcode', 'businesspartnertaxnumber',
                'to_emailaddress', 'to_phonenumber', 'phone', 'taxregistrationnumber', 'vatregnumber', 'creditlimit',
                'addressbook', 'mobilenumber', 'taxpayerid', 'primarycontactemail', 'primarycontactphone',
                'personfirstname', 'personmiddlename', 'personlastname', 'organizationname', 'customeraccount',
                'addresscity', 'addresszipcode', 'primaryemailaddr', 'primaryphone', 'givenname', 'familyname',
                'billaddr', 'mobile', 'fax', 'alternatephone', 'taxnumber', 'bankaccountdetails', 'bankaccountnumber',
                'phones', 'addresses', 'email1', 'email2', 'phone1', 'cellphone', 'taxid', 'displaycontact',
                'mailaddress', 'billto', 'shipto']
        },
        {
            name: 'expenses',
            label: 'Expenses',
            fields: ['email', 'firstname', 'lastname', 'username', 'givenname', 'familyname', 'first_name', 'last_name',
                'manageremail', 'employeeid', 'emails', 'name', 'employeenumber', 'phonenumbers', 'dateofbirth',
                'emergencycontacts', 'displayname', 'accountnumber', 'accountname', 'bankname', 'banknumber',
                'postaladdressline1', 'employee_id', 'user_email', 'user_full_name', 'login', 'employee-number',
                'phone-mobile', 'phone-work', 'bank-account-number', 'employeeemail', 'externalemployeeid',
                'cardnumber', 'partnerusersecret', 'primaryemailaddress', 'alternateemailaddresses', 'cvv',
                'expiration_date', 'holder_name']
        },
        {
            name: 'sales',
            label: 'Sales and CRM',
            fields: ['phone', 'fax', 'email', 'firstname', 'lastname', 'mobilephone', 'mobile', 'birthdate',
                'homephone', 'mailingstreet', 'mailingcity', 'mailingpostalcode', 'assistantphone', 'emailaddress1',
                'emailaddress2', 'emailaddress3', 'telephone1', 'telephone2', 'telephone3', 'address1_line1',
                'address1_city', 'address1_postalcode', 'address', 'city', 'zip', 'emailaddress', 'personfirstname',
                'personlastname', 'workphonenumber', 'primaryaddress', 'owneremailaddress', 'normalisedphone',
                'normalisedmobile', 'first_name', 'last_name', 'home_phone', 'other_phone', 'mailing_street',
                'mailing_city', 'mailing_zip', 'secondary_email', 'date_of_birth', 'name', 'postal_address', 'birthday']
        },
        {
            name: 'marketing',
            label: 'Marketing',
            fields: ['email', 'phone', 'city', 'firstname', 'lastname', 'mobilephone', 'address', 'emailaddress',
                'sms_phone_number', 'zip', 'fax', 'postalcode', 'address1', 'address2', 'first_name', 'last_name',
                'contactkey', 'subscriberkey', 'mobilenumber', 'mainphone', 'dateofbirth', 'businessphone',
                'email_address', 'fname', 'lname', 'birthday', 'phone_number', 'ip', 'dob', 'home_city']
        },
        {
            name: 'customer_support',
            label: 'Customer support',
            fields: ['email', 'phone', 'name', 'address', 'description', 'city', 'zip', 'firstname', 'lastname',
                'notes', 'signature', 'suppliedemail', 'suppliedphone', 'suppliedname', 'contactemail', 'contactphone',
                'contactmobile', 'contactfax', 'comments', 'mobile', 'other_emails', 'twitter_id', 'cc_emails',
                'bcc_emails', 'from_email', 'to_emails', 'mobile_phone', 'business_phone', 'home_phone', 'first_name',
                'last_name', 'user_name', 'street', 'avatar', 'mobilephone', 'fax', 'workemail', 'personalemail',
                'workphone', 'homephone', 'cellphone']
        },
        {
            name: 'procurement',
            label: 'Procurement',
            fields: ['email', 'bankaccountnumber', 'iban', 'firstname', 'lastname', 'bankaccountstandardid',
                'accountnumber', 'bankaccountexternalid', 'partytaxid', 'longpartytaxid', 'vatregistrationnumber',
                'line1', 'city', 'postalcode', 'primary-contact', 'po-email', 'account-number', 'duns',
                'cxml-http-password', 'cxml-http-username', 'cxml-secret', 'cxml-invoice-secret', 'invoice-emails',
                'display-name', 'phonenumber', 'taxpayerid', 'nationalinsurancenumber', 'providedbyemail',
                'providedbycontactname', 'bic', 'addressee', 'suppliername', 'phone', 'emailaddress', 'username',
                'swift_bic', 'bankkey_aba', 'beneficiaryname', 'addressline1', 'phoneno', 'faxno', 'name',
                'accountholdername', 'linkedbbanoriban']
        },
        {
            name: 'it_operations',
            label: 'IT operations',
            fields: ['email', 'name', 'description', 'phone', 'caller_id', 'comments', 'work_notes', 'close_notes',
                'short_description', 'mobile_phone', 'user_name', 'first_name', 'last_name', 'emailaddress',
                'displayname', 'profilefullname', 'alternatecontactemail', 'owneremail', 'ownerteamemail', 'symptom',
                'resolution', 'loginid', 'handle', 'ip_addresses', 'mac_address', 'realname', 'password',
                'http_cal_url', 'web_cal_url', 'avatar_url']
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

// Whether the list holds the name, in any case.
maskingSets.holds = function(fieldList, name) {

    var nameLower = name.toLowerCase();

    for(var fieldIdx = 0; fieldIdx < fieldList.length; fieldIdx++) {
        if(fieldList[fieldIdx].toLowerCase() === nameLower) {
            return true;
        }
    }

    return false;
};

// ////////////////////////////////////////////////////////////////////////

// The list with every name it does not hold yet appended at its end.
maskingSets.merge = function(fieldList, names) {

    var out = fieldList.slice();

    for(var nameIdx = 0; nameIdx < names.length; nameIdx++) {
        if(!maskingSets.holds(out, names[nameIdx])) {
            out.push(names[nameIdx]);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

maskingSets.subtract = function(fieldList, names) {

    var out = [];

    for(var fieldIdx = 0; fieldIdx < fieldList.length; fieldIdx++) {
        if(!maskingSets.holds(names, fieldList[fieldIdx])) {
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
