

// /////////////////////////////////////////////////////////////////////////////

// What a row of the MLLP audit log shows - the trigger and the patient the message is about,
// the facility it came from, and what the receiver acknowledged it with. The channel and
// outgoing sides read the same way, so one presenter serves them both.

(function($) {

var mllp = {

    config: {

        messageTypeLabel: 'Type',
        patientLabel: 'MRN',
        facilityLabel: 'Facility',
        ackLabel: 'ACK',

        // The acknowledgment codes HL7 defines, and what each of them says about the message
        ackTones: {
            'AA': 'good',
            'CA': 'good',
            'AE': 'bad',
            'CE': 'bad',
            'AR': 'bad',
            'CR': 'bad'
        }
    },

    // ////////////////////////////////////////////////////////////////////////

    ackTone: function(ackStatus) {
        var tone = mllp.config.ackTones[ackStatus];

        // A receiver may answer with a code of its own that HL7 itself does not define.
        if (tone === undefined) {
            tone = 'warn';
        }

        return tone;
    }
};

// /////////////////////////////////////////////////////////////////////////////

var presenter = {

    chips: function(row) {
        var config = mllp.config;
        var out = [];

        if (row.msg_type !== '') {
            out.push({key: 'msg_type', label: config.messageTypeLabel, value: row.msg_type, tone: 'accent'});
        }

        if (row.mrn !== '') {
            out.push({key: 'mrn', label: config.patientLabel, value: row.mrn, tone: 'neutral'});
        }

        if (row.facility !== '') {
            out.push({key: 'facility', label: config.facilityLabel, value: row.facility, tone: 'muted'});
        }

        if (row.ack_status !== '') {
            out.push({key: 'ack_status', label: config.ackLabel, value: row.ack_status,
                tone: mllp.ackTone(row.ack_status)});
        }

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    headline: function(row) {
        if (row.msg_type === '') {
            return row.msg_id;
        }

        if (row.msg_id === '') {
            return row.msg_type;
        }

        return row.msg_type + ' ' + row.msg_id;
    },

    // ////////////////////////////////////////////////////////////////////////

    // An HL7 message is named by its control id, MSH-10
    identityLabel: 'Control id',

    identity: function(row) {
        return row.msg_id;
    }
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.sources['mllp-channel'] = presenter;
$.fn.zato.audit_log.sources['mllp-outgoing'] = presenter;

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
