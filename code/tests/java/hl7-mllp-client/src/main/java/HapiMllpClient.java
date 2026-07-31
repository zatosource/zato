// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
//
// Sends one HL7 v2.5 message to an MLLP listener through HAPI, the standard Java HL7 library,
// and reports what the acknowledgment's MSA segment said. The message's routing fields all come
// from the command line, so one client covers every routing combination the tests send.
//
// Usage: HapiMllpClient --host H --port P --control-id ID --sending-app APP
//                       [--sending-facility FAC] [--message-type ADT] [--trigger-event A01]
//
// The acknowledgment is reported on standard output as three lines:
//   msa_1=...
//   msa_2=...
//   msa_3=...

import java.util.HashMap;
import java.util.Map;

import ca.uhn.hl7v2.DefaultHapiContext;
import ca.uhn.hl7v2.HapiContext;
import ca.uhn.hl7v2.app.Connection;
import ca.uhn.hl7v2.app.Initiator;
import ca.uhn.hl7v2.model.Message;
import ca.uhn.hl7v2.model.v25.message.ADT_A01;
import ca.uhn.hl7v2.model.v25.message.ORU_R01;
import ca.uhn.hl7v2.util.Terser;
import ca.uhn.hl7v2.validation.impl.ValidationContextFactory;

public class HapiMllpClient {

    // What every message built here says about its receiver
    private static final String RECEIVING_APP = "ZATO";
    private static final String RECEIVING_FACILITY = "ZATO";

    // What the routing fields are when the command line does not say otherwise
    private static final String DEFAULT_MESSAGE_TYPE = "ADT";
    private static final String DEFAULT_TRIGGER_EVENT = "A01";

    // How long the listener is given to answer before the send is called a failure
    private static final int RESPONSE_TIMEOUT_MS = 30000;

    public static void main(String[] arguments) throws Exception {

        Map<String, String> options = parseArguments(arguments);

        String host = require(options, "host");
        int port = Integer.parseInt(require(options, "port"));
        String controlId = require(options, "control-id");
        String sendingApp = require(options, "sending-app");
        String sendingFacility = options.getOrDefault("sending-facility", "");
        String messageType = options.getOrDefault("message-type", DEFAULT_MESSAGE_TYPE);
        String triggerEvent = options.getOrDefault("trigger-event", DEFAULT_TRIGGER_EVENT);

        // The context is how HAPI is configured and where its connections come from. Inbound
        // validation is off because the answer to assert on is the acknowledgment as it arrived.
        try (HapiContext context = new DefaultHapiContext()) {
            context.setValidationContext(ValidationContextFactory.noValidation());

            Message message = buildMessage(messageType, triggerEvent, controlId, sendingApp, sendingFacility);

            // One connection, one send, one acknowledgment - what a real sender does
            Connection connection = context.newClient(host, port, false);
            Initiator initiator = connection.getInitiator();
            initiator.setTimeout(RESPONSE_TIMEOUT_MS, java.util.concurrent.TimeUnit.MILLISECONDS);

            Message acknowledgment = initiator.sendAndReceive(message);

            // The MSA fields are the whole of what the test reads back
            Terser ackTerser = new Terser(acknowledgment);
            System.out.println("msa_1=" + emptyIfNull(ackTerser.get("/MSA-1")));
            System.out.println("msa_2=" + emptyIfNull(ackTerser.get("/MSA-2")));
            System.out.println("msa_3=" + emptyIfNull(ackTerser.get("/MSA-3")));

            connection.close();
        }
    }

    // Builds the message whose type the command line named, with the routing fields set on its
    // MSH segment and a body a real sender of that type would attach.
    private static Message buildMessage(
            String messageType,
            String triggerEvent,
            String controlId,
            String sendingApp,
            String sendingFacility) throws Exception {

        Message message;

        if (messageType.equals("ORU")) {
            ORU_R01 oru = new ORU_R01();
            oru.initQuickstart("ORU", triggerEvent, "P");

            // A results message carries at least one observation
            Terser oruTerser = new Terser(oru);
            oruTerser.set("/PATIENT_RESULT/PATIENT/PID-3-1", "67890");
            oruTerser.set("/PATIENT_RESULT/PATIENT/PID-5-1", "Smith");
            oruTerser.set("/PATIENT_RESULT/PATIENT/PID-5-2", "Jane");
            oruTerser.set("/PATIENT_RESULT/ORDER_OBSERVATION/OBR-1", "1");
            oruTerser.set("/PATIENT_RESULT/ORDER_OBSERVATION/OBR-4-1", "CBC");
            oruTerser.set("/PATIENT_RESULT/ORDER_OBSERVATION/OBSERVATION/OBX-1", "1");
            oruTerser.set("/PATIENT_RESULT/ORDER_OBSERVATION/OBSERVATION/OBX-2", "NM");
            oruTerser.set("/PATIENT_RESULT/ORDER_OBSERVATION/OBSERVATION/OBX-3-1", "WBC");
            oruTerser.set("/PATIENT_RESULT/ORDER_OBSERVATION/OBSERVATION/OBX-5-1", "7.5");

            message = oru;

        } else {
            ADT_A01 adt = new ADT_A01();
            adt.initQuickstart("ADT", triggerEvent, "P");

            // An admission message carries the patient it admits
            Terser adtTerser = new Terser(adt);
            adtTerser.set("/PID-3-1", "12345");
            adtTerser.set("/PID-5-1", "Doe");
            adtTerser.set("/PID-5-2", "John");

            message = adt;
        }

        // The routing fields are the caller's own, the control id included, so the test can
        // match the acknowledgment to the message it sent
        Terser terser = new Terser(message);
        terser.set("/MSH-3", sendingApp);
        terser.set("/MSH-4", sendingFacility);
        terser.set("/MSH-5", RECEIVING_APP);
        terser.set("/MSH-6", RECEIVING_FACILITY);
        terser.set("/MSH-10", controlId);

        return message;
    }

    // Reads --key value pairs off the command line
    private static Map<String, String> parseArguments(String[] arguments) {

        Map<String, String> options = new HashMap<>();

        for (int index = 0; index < arguments.length - 1; index += 2) {
            String key = arguments[index];

            if (!key.startsWith("--")) {
                throw new IllegalArgumentException("Expected an option, got: " + key);
            }

            options.put(key.substring(2), arguments[index + 1]);
        }

        return options;
    }

    // Returns an option that has to be there, or says which one is missing
    private static String require(Map<String, String> options, String name) {

        String value = options.get(name);

        if (value == null) {
            throw new IllegalArgumentException("Missing required option: --" + name);
        }

        return value;
    }

    // Terser reports an absent field as null, and an absent field is an empty answer
    private static String emptyIfNull(String value) {
        return value == null ? "" : value;
    }
}
