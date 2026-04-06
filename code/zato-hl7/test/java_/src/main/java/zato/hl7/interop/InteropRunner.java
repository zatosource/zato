package zato.hl7.interop;

import java.util.List;

/**
 * Sends all 30 HL7 messages over MLLP to the specified host:port
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

        try (MllpClient client = new MllpClient(host, port)) {
            for (MessageFactory.MessageEntry entry : messages) {
                String label = entry.label();
                String encoded = entry.encoded();

                // Extract control id from MSH-10
                String controlId = extractControlId(encoded);

                boolean ok = false;
                String ackCode = "";
                String error = "";

                try {
                    String ack = client.sendAndReceive(encoded);
                    ackCode = extractAckCode(ack);
                    ok = "AA".equals(ackCode);
                } catch (Exception e) {
                    error = e.getMessage().replace("\"", "'");
                }

                if (!ok) {
                    allOk = false;
                }

                System.out.printf(
                    "{\"msg_type\": \"%s\", \"control_id\": \"%s\", \"ack_code\": \"%s\", \"ok\": %s, \"error\": \"%s\"}%n",
                    label, controlId, ackCode, ok, error
                );
            }
        }

        System.exit(allOk ? 0 : 1);
    }

    private static String extractControlId(String hl7Message) {
        // MSH is the first segment, field separator is at index 3
        int firstCr = hl7Message.indexOf('\r');
        String msh = (firstCr == -1) ? hl7Message : hl7Message.substring(0, firstCr);

        char fieldSep = msh.charAt(3);
        String[] fields = msh.split("\\" + fieldSep);

        // MSH-10 is at index 9 (MSH-1 is the separator itself)
        return (fields.length > 9) ? fields[9] : "";
    }

    private static String extractAckCode(String ack) {
        // Find the MSA segment and read MSA-1
        String[] segments = ack.split("\r");
        for (String seg : segments) {
            if (seg.startsWith("MSA")) {
                char fieldSep = '|';
                // Try to get field sep from context, default to pipe
                String[] fields = seg.split("\\" + fieldSep);
                return (fields.length > 1) ? fields[1] : "";
            }
        }
        return "";
    }
}
