package zato.hl7.interop;

import ca.uhn.hl7v2.DefaultHapiContext;
import ca.uhn.hl7v2.HapiContext;
import ca.uhn.hl7v2.app.Connection;
import ca.uhn.hl7v2.app.Initiator;
import ca.uhn.hl7v2.model.Message;
import ca.uhn.hl7v2.parser.PipeParser;
import ca.uhn.hl7v2.validation.impl.NoValidation;

import java.util.List;

/**
 * Sends all 30 HL7 messages over MLLP to the specified host:port
 * using HAPI's built-in Connection and Initiator (the standard MLLP transport),
 * and prints one JSON line per message to stdout.
 * Exit code 0 = all passed, 1 = at least one failed.
 */
public class InteropRunner {

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: InteropRunner <host> <port>");
            System.exit(2);
        }

        String host = args[0];
        int port = Integer.parseInt(args[1]);

        MessageFactory factory = new MessageFactory();
        List<MessageFactory.MessageEntry> messages = factory.buildAll();

        boolean allOk = true;

        try (HapiContext context = new DefaultHapiContext()) {
            context.setValidationContext(new NoValidation());
            PipeParser parser = context.getPipeParser();
            Connection connection = context.newClient(host, port, false);

            try {
                Initiator initiator = connection.getInitiator();

                for (MessageFactory.MessageEntry entry : messages) {
                    String label = entry.label();
                    String encoded = entry.encoded();
                    String controlId = extractControlId(encoded);

                    boolean ok = false;
                    String ackCode = "";
                    String error = "";

                    try {
                        Message parsed = parser.parse(encoded);
                        Message response = initiator.sendAndReceive(parsed);
                        String responseStr = parser.encode(response);
                        ackCode = extractAckCode(responseStr);
                        ok = "AA".equals(ackCode);
                    } catch (Exception e) {
                        error = e.getMessage() != null ? e.getMessage().replace("\"", "'") : "unknown error";
                    }

                    if (!ok) {
                        allOk = false;
                    }

                    System.out.printf(
                        "{\"msg_type\": \"%s\", \"control_id\": \"%s\", \"ack_code\": \"%s\", \"ok\": %s, \"error\": \"%s\"}%n",
                        label, controlId, ackCode, ok, error
                    );
                }
            } finally {
                connection.close();
            }
        }

        System.exit(allOk ? 0 : 1);
    }

    private static String extractControlId(String hl7Message) {
        int firstCr = hl7Message.indexOf('\r');
        String msh = (firstCr == -1) ? hl7Message : hl7Message.substring(0, firstCr);
        String[] fields = msh.split("\\|");
        return (fields.length > 9) ? fields[9] : "";
    }

    private static String extractAckCode(String ack) {
        String[] segments = ack.split("\r");
        for (String seg : segments) {
            if (seg.startsWith("MSA")) {
                String[] fields = seg.split("\\|");
                return (fields.length > 1) ? fields[1] : "";
            }
        }
        return "";
    }
}
