// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
//
// Sends one HL7 message to a Zato MLLP channel and reports the acknowledgment it reads back.
// The message is taken from a file so that the carriage returns HL7 separates its segments with
// survive being passed in, and the acknowledgment is reported base64-encoded so that the test
// reading it back gets the bytes exactly as they arrived.
//
// Plain: java MllpClient --host H --port P --message-file F
// TLS:   java MllpClient --host H --port P --message-file F --tls --ca-file CA --keystore KS --keystore-password PW

import java.io.ByteArrayOutputStream;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.KeyStore;
import java.security.cert.Certificate;
import java.security.cert.CertificateFactory;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.TrustManagerFactory;

public class MllpClient {

    // The bytes MLLP wraps each message in - one to open a frame and two to close it
    private static final byte START_BLOCK = 0x0B;
    private static final byte END_BLOCK = 0x1C;
    private static final byte CARRIAGE_RETURN = 0x0D;

    // How long the channel is given to answer before the send is called a failure
    private static final int READ_TIMEOUT_MS = 30000;

    // How long the connection itself is given
    private static final int CONNECT_TIMEOUT_MS = 10000;

    // The alias the authority is stored under in the in-memory truststore
    private static final String CA_ALIAS = "zato-mllp-ca";

    // What the test reads the acknowledgment off standard output by
    private static final String ACK_PREFIX = "ACK_BASE64: ";

    // The store format the client's own key and certificate arrive in
    private static final String KEYSTORE_TYPE = "PKCS12";

    // The lowest protocol version the connection is allowed to settle on
    private static final String TLS_PROTOCOL = "TLSv1.2";

    public static void main(String[] args) {

        try {
            Map<String, String> options = parseOptions(args);
            byte[] message = Files.readAllBytes(Paths.get(options.get("message-file")));

            String host = options.get("host");
            int port = Integer.parseInt(options.get("port"));

            Socket socket = options.containsKey("tls") ? connectTls(options, host, port) : connectPlain(host, port);

            try {
                socket.setSoTimeout(READ_TIMEOUT_MS);

                send(socket.getOutputStream(), message);
                byte[] ack = readFrame(socket.getInputStream());

                System.out.println(ACK_PREFIX + Base64.getEncoder().encodeToString(ack));
            } finally {
                socket.close();
            }
        } catch (Exception e) {

            // The test reads the reason off standard error, so the whole trace goes there
            System.err.println("ERROR: " + e);
            e.printStackTrace();
            System.exit(1);
        }
    }

    // Reads the command line into a map. A flag that takes no value, which is only --tls, maps to
    // itself so that the presence of the key is all a caller has to look at.
    private static Map<String, String> parseOptions(String[] args) {

        Map<String, String> out = new HashMap<>();
        int position = 0;

        while (position < args.length) {

            String name = args[position].substring(2);

            if (name.equals("tls")) {
                out.put(name, name);
                position += 1;
            } else {
                out.put(name, args[position + 1]);
                position += 2;
            }
        }

        return out;
    }

    private static Socket connectPlain(String host, int port) throws Exception {

        Socket out = new Socket();
        out.connect(new InetSocketAddress(host, port), CONNECT_TIMEOUT_MS);

        return out;
    }

    // Connects with the client's own certificate presented and what the load balancer presents
    // verified against the authority both were issued by.
    private static Socket connectTls(Map<String, String> options, String host, int port) throws Exception {

        char[] password = options.get("keystore-password").toCharArray();

        KeyStore keyStore = KeyStore.getInstance(KEYSTORE_TYPE);

        try (InputStream keyStoreStream = new FileInputStream(options.get("keystore"))) {
            keyStore.load(keyStoreStream, password);
        }

        KeyManagerFactory keyManagers = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
        keyManagers.init(keyStore, password);

        SSLContext context = SSLContext.getInstance(TLS_PROTOCOL);
        context.init(keyManagers.getKeyManagers(), buildTrustManagers(options.get("ca-file")).getTrustManagers(), null);

        SSLSocket out = (SSLSocket) context.getSocketFactory().createSocket();
        out.connect(new InetSocketAddress(host, port), CONNECT_TIMEOUT_MS);

        // The handshake is done outright so that a certificate the other end rejects is reported
        // as the handshake failure it is, rather than later as a read that returned nothing
        out.startHandshake();

        return out;
    }

    // Builds the trust material out of the authority in PEM form. A PKCS12 file is not used for
    // this, because only keytool writes the trusted-certificate entries a Java truststore needs.
    private static TrustManagerFactory buildTrustManagers(String caFilePath) throws Exception {

        Certificate authority;

        try (InputStream caStream = new FileInputStream(caFilePath)) {
            authority = CertificateFactory.getInstance("X.509").generateCertificate(caStream);
        }

        KeyStore trustStore = KeyStore.getInstance(KeyStore.getDefaultType());
        trustStore.load(null, null);
        trustStore.setCertificateEntry(CA_ALIAS, authority);

        TrustManagerFactory out = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        out.init(trustStore);

        return out;
    }

    private static void send(OutputStream stream, byte[] message) throws Exception {

        stream.write(START_BLOCK);
        stream.write(message);
        stream.write(END_BLOCK);
        stream.write(CARRIAGE_RETURN);
        stream.flush();
    }

    // Reads one framed message off the stream and returns what was inside the frame. The opening
    // byte is dropped and the two closing bytes end the read, so what comes back is HL7 alone.
    private static byte[] readFrame(InputStream stream) throws Exception {

        ByteArrayOutputStream out = new ByteArrayOutputStream();
        boolean isStarted = false;
        int previous = -1;

        while (true) {

            int current = stream.read();

            if (current == -1) {
                throw new Exception("The channel closed the connection before it answered");
            }

            if (!isStarted) {

                if (current == START_BLOCK) {
                    isStarted = true;
                }

                // Anything before the opening byte is not part of a frame and is passed over
                continue;
            }

            if (previous == END_BLOCK && current == CARRIAGE_RETURN) {

                // The closing pair is not part of the message, so the byte held back is dropped too
                byte[] framed = out.toByteArray();
                byte[] result = new byte[framed.length - 1];
                System.arraycopy(framed, 0, result, 0, result.length);

                return result;
            }

            out.write(current);
            previous = current;
        }
    }
}
