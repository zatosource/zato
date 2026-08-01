// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
//
// An MLLP listener built on HAPI, the standard Java HL7 v2 library. It is the receiving side an
// outgoing connection is pointed at when a test has to know that what Zato sends is read by the
// reference implementation rather than by another copy of Zato's own parser.
//
// Usage: HapiMllpServer --port P [--ack-code AA] [--delay-ms 0] [--tls false]
//
// What it says on standard output, one line each:
//   READY:<port>                 once the listener is bound and taking connections
//   RECEIVED:<message>           for every message that arrived, segment separators written as \r
//   ERROR:<text>                 for anything that went wrong inside the listener

import java.io.IOException;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

import ca.uhn.hl7v2.AcknowledgmentCode;
import ca.uhn.hl7v2.DefaultHapiContext;
import ca.uhn.hl7v2.HL7Exception;
import ca.uhn.hl7v2.HapiContext;
import ca.uhn.hl7v2.app.HL7Service;
import ca.uhn.hl7v2.model.Message;
import ca.uhn.hl7v2.protocol.ReceivingApplication;
import ca.uhn.hl7v2.protocol.ReceivingApplicationException;
import ca.uhn.hl7v2.validation.impl.ValidationContextFactory;

public class HapiMllpServer {

    // What the acknowledgment code is when the command line does not name one - the answer a
    // receiving system gives to a message it took
    private static final String DEFAULT_ACK_CODE = "AA";

    // How long the listener takes over a message when the command line does not say - answering
    // straight away is what a healthy receiver does
    private static final long DEFAULT_DELAY_MS = 0;

    // What a listener asked to never answer waits instead, which outlives any test that points
    // a send timeout at it
    private static final long NEVER_ANSWER_DELAY_MS = 3600000;

    // How often the main thread checks whether the listener has bound its port yet
    private static final long READY_POLL_MS = 50;

    // How long the listener is given to bind before this reports that it did not
    private static final long READY_TIMEOUT_MS = 30000;

    // Everything is written in UTF-8 rather than in whatever the machine's own default is, so that
    // a message carrying non-ASCII names reaches the test process as it reached the listener
    private static final PrintStream OUTPUT = new PrintStream(System.out, true, StandardCharsets.UTF_8);

    public static void main(String[] arguments) throws Exception {

        Map<String, String> options = parseArguments(arguments);

        int port = Integer.parseInt(require(options, "port"));
        String ackCode = options.getOrDefault("ack-code", DEFAULT_ACK_CODE);
        long delayMs = Long.parseLong(options.getOrDefault("delay-ms", String.valueOf(DEFAULT_DELAY_MS)));
        boolean isTls = Boolean.parseBoolean(options.getOrDefault("tls", "false"));
        boolean isNeverAnswering = Boolean.parseBoolean(options.getOrDefault("never-answer", "false"));

        // A listener that never answers is one that takes longer over a message than any test waits,
        // which is the same thing from the sending side and needs no separate code path here
        if (isNeverAnswering) {
            delayMs = NEVER_ANSWER_DELAY_MS;
        }

        // The context is how HAPI is configured and where the listener comes from. Inbound validation
        // is off because what a test asserts on is the message as it arrived, not HAPI's opinion of it.
        HapiContext context = new DefaultHapiContext();
        context.setValidationContext(ValidationContextFactory.noValidation());

        // TLS is the JVM's own, so the key store the listener presents is set through the standard
        // system properties by whoever launched this
        HL7Service service = context.newServer(port, isTls);

        service.registerApplication("*", "*", new RecordingApplication(ackCode, delayMs));

        service.start();
        waitUntilRunning(service, port);

        // Whoever launched this waits on this line before it sends anything
        OUTPUT.println("READY:" + port);

        // The listener runs on threads of its own, so this one only has to stay alive
        Thread.currentThread().join();
    }

    // Waits for the listener to bind its port, so that READY is only ever printed by a listener
    // something can actually connect to.
    private static void waitUntilRunning(HL7Service service, int port) throws Exception {

        long deadline = System.currentTimeMillis() + READY_TIMEOUT_MS;

        while (System.currentTimeMillis() < deadline) {

            if (service.isRunning()) {
                return;
            }

            Thread.sleep(READY_POLL_MS);
        }

        throw new IllegalStateException("The listener did not bind port " + port + " within " + READY_TIMEOUT_MS + "ms");
    }

    // What every message that arrives is handed to - it reports the message on standard output and
    // answers it with the code this listener was started with.
    private static class RecordingApplication implements ReceivingApplication<Message> {

        private final String ackCode;
        private final long delayMs;

        RecordingApplication(String ackCode, long delayMs) {
            this.ackCode = ackCode;
            this.delayMs = delayMs;
        }

        @Override
        public boolean canProcess(Message message) {
            return true;
        }

        @Override
        public Message processMessage(Message message, Map<String, Object> metadata)
                throws ReceivingApplicationException, HL7Exception {

            // The message is reported before the delay, so that a test of a slow receiver can tell
            // a message that arrived and is being worked on from one that never arrived at all
            report(message);

            // A slow receiver is one that takes its time before answering, which is what a send
            // timeout on the other end is measured against
            if (this.delayMs > 0) {
                try {
                    Thread.sleep(this.delayMs);
                } catch (InterruptedException exception) {
                    Thread.currentThread().interrupt();
                    throw new ReceivingApplicationException(exception);
                }
            }

            // An acceptance is HAPI's own acknowledgment of the message, and a rejection carries
            // the code the listener was started with, which is how a sender's handling of a refusal
            // is exercised against a real implementation of the receiving side. Building either of
            // them reads the message back, so a failure there is one of the listener's own.
            try {

                if (this.ackCode.equals("AA")) {
                    return message.generateACK();
                }

                AcknowledgmentCode code = AcknowledgmentCode.valueOf(this.ackCode);
                HL7Exception reason = new HL7Exception("Refused by the test listener with " + this.ackCode);

                return message.generateACK(code, reason);

            } catch (IOException exception) {
                throw new ReceivingApplicationException(exception);
            }
        }

        // Writes one received message out as a single line, which is what lets the test process read
        // messages back one at a time from a stream several senders are writing into at once.
        private void report(Message message) throws HL7Exception {

            String encoded = message.encode();
            String escaped = encoded.replace("\r", "\\r").replace("\n", "\\n");

            OUTPUT.println("RECEIVED:" + escaped);
        }
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
}
