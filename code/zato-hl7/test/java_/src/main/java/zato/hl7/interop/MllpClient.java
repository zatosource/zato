package zato.hl7.interop;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

/**
 * Thin MLLP client that connects to a server, sends framed HL7 messages,
 * and reads framed ACK responses.
 */
public class MllpClient implements AutoCloseable {

    private static final byte SB = 0x0B;
    private static final byte EB = 0x1C;
    private static final byte CR = 0x0D;

    private final Socket socket;
    private final InputStream in;
    private final OutputStream out;

    public MllpClient(String host, int port) throws IOException {
        socket = new Socket(host, port);
        socket.setSoTimeout(10_000);
        in = socket.getInputStream();
        out = socket.getOutputStream();
    }

    /**
     * Sends an HL7 message wrapped in MLLP framing and returns the unframed ACK response.
     */
    public String sendAndReceive(String hl7Message) throws IOException {
        byte[] payload = hl7Message.getBytes(StandardCharsets.ISO_8859_1);

        // Frame: SB + payload + EB + CR
        byte[] framed = new byte[payload.length + 3];
        framed[0] = SB;
        System.arraycopy(payload, 0, framed, 1, payload.length);
        framed[framed.length - 2] = EB;
        framed[framed.length - 1] = CR;

        out.write(framed);
        out.flush();

        // Read until we see EB + CR
        byte[] buf = new byte[65536];
        int total = 0;
        while (total < buf.length) {
            int n = in.read(buf, total, buf.length - total);
            if (n == -1) {
                break;
            }
            total += n;

            // Check for end of MLLP frame
            if (total >= 2 && buf[total - 2] == EB && buf[total - 1] == CR) {
                break;
            }
        }

        // Unframe: strip SB prefix and EB+CR suffix
        int start = (total > 0 && buf[0] == SB) ? 1 : 0;
        int end = (total >= 2 && buf[total - 2] == EB && buf[total - 1] == CR) ? total - 2 : total;

        return new String(buf, start, end - start, StandardCharsets.ISO_8859_1);
    }

    @Override
    public void close() throws IOException {
        socket.close();
    }
}
