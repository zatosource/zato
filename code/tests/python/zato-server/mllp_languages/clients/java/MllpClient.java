// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
//
// Sends HL7 messages to a Zato MLLP channel and reports the acknowledgments it reads back.
// The messages are taken from a file, one base64-encoded message per line, so that the carriage
// returns HL7 separates its segments with survive being passed in, and each acknowledgment is
// reported base64-encoded too so that the test reading it back gets the bytes as they arrived.
//
// The messages are spread over as many connections as --connections asks for, each of them on a
// thread of its own that sends its share down the one connection, one message at a time. No
// connection sends anything until all of them are open, so what the listener is given to do is
// held concurrently rather than by chance.
//
// Plain: java MllpClient --host H --port P --message-file F [--connections N]
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
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.TimeUnit;
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

    // How long a connection waits for the others to be open before it gives up on them. One that
    // never got there leaves the rest with a broken barrier, so a failure to connect ends the run
    // outright rather than leaving every other thread waiting for a message that is never sent.
    private static final int BARRIER_TIMEOUT_MS = 30000;

    // How many connections the messages travel over when nothing says otherwise
    private static final int DEFAULT_CONNECTION_COUNT = 1;

    // The alias the authority is stored under in the in-memory truststore
    private static final String CA_ALIAS = "zato-mllp-ca";

    // What the test reads the acknowledgments off standard output by
    private static final String ACK_PREFIX = "ACK_BASE64: ";

    // The store format the client's own key and certificate arrive in
    private static final String KEYSTORE_TYPE = "PKCS12";

    // The lowest protocol version the connection is allowed to settle on
    private static final String TLS_PROTOCOL = "TLSv1.2";

    public static void main(String[] args) {

        try {
            Map<String, String> options = parseOptions(args);
            List<byte[]> messages = readMessages(options.get("message-file"));

            if (messages.isEmpty()) {
                throw new Exception("There is nothing to send in " + options.get("message-file"));
            }

            String host = options.get("host");
            int port = Integer.parseInt(options.get("port"));
            int connectionCount = getConnectionCount(options, messages.size());

            List<Sender> senders = run(options, host, port, messages, connectionCount);

            // Every acknowledgment is reported only once all the senders are done, because two
            // threads writing to standard output as they go would interleave their lines
            for (Sender sender : senders) {
                for (byte[] ack : sender.acks) {
                    System.out.println(ACK_PREFIX + Base64.getEncoder().encodeToString(ack));
                }
            }
        } catch (Exception e) {

            // The test reads the reason off standard error, so the whole trace goes there
            System.err.println("ERROR: " + e);
            e.printStackTrace();
            System.exit(1);
        }
    }

    // Starts one thread for each connection, waits for all of them and hands back what they read.
    // The first thread that failed is raised here, so that a run nothing came back from says why.
    private static List<Sender> run(
        Map<String, String> options,
        String host,
        int port,
        List<byte[]> messages,
        int connectionCount
    ) throws Exception {

        List<Sender> senders = new ArrayList<>();
        List<Thread> threads = new ArrayList<>();
        CyclicBarrier barrier = new CyclicBarrier(connectionCount);

        for (List<byte[]> share : partition(messages, connectionCount)) {

            Sender sender = new Sender(options, host, port, share, barrier);
            Thread thread = new Thread(sender);

            senders.add(sender);
            threads.add(thread);

            thread.start();
        }

        for (Thread thread : threads) {
            thread.join();
        }

        for (Sender sender : senders) {
            if (sender.failure != null) {
                throw sender.failure;
            }
        }

        return senders;
    }

    // Deals the messages out one by one across the connections, rather than giving each connection
    // a run of neighbouring ones, so that whatever channels the messages are meant for are spread
    // over the connections instead of each connection holding to a single channel.
    private static List<List<byte[]>> partition(List<byte[]> messages, int connectionCount) {

        List<List<byte[]>> out = new ArrayList<>();

        for (int index = 0; index < connectionCount; index++) {
            out.add(new ArrayList<byte[]>());
        }

        for (int index = 0; index < messages.size(); index++) {
            out.get(index % connectionCount).add(messages.get(index));
        }

        return out;
    }

    // A connection with nothing to carry would only stall the others at the barrier, so there are
    // never more connections than there are messages to spread over them.
    private static int getConnectionCount(Map<String, String> options, int messageCount) {

        int out = DEFAULT_CONNECTION_COUNT;

        if (options.containsKey("connections")) {
            out = Integer.parseInt(options.get("connections"));
        }

        if (out > messageCount) {
            out = messageCount;
        }

        return out;
    }

    // One connection, the messages it carries and what came back for each of them.
    private static final class Sender implements Runnable {

        private final Map<String, String> options;
        private final String host;
        private final int port;
        private final List<byte[]> messages;
        private final CyclicBarrier barrier;

        // What the channel answered each of the messages with, in the order they were sent
        private final List<byte[]> acks = new ArrayList<>();

        // Why this connection got no further, left for the thread that joins it to raise
        private Exception failure;

        private Sender(
            Map<String, String> options,
            String host,
            int port,
            List<byte[]> messages,
            CyclicBarrier barrier
        ) {
            this.options = options;
            this.host = host;
            this.port = port;
            this.messages = messages;
            this.barrier = barrier;
        }

        public void run() {

            try {
                Socket socket = options.containsKey("tls") ? connectTls(options, host, port) : connectPlain(host, port);

                try {
                    socket.setSoTimeout(READ_TIMEOUT_MS);

                    // Nothing is sent until every other connection is open as well
                    barrier.await(BARRIER_TIMEOUT_MS, TimeUnit.MILLISECONDS);

                    OutputStream outgoing = socket.getOutputStream();
                    InputStream incoming = socket.getInputStream();

                    // Each message is answered before the next one is sent, which is what a sender
                    // holding one connection open for a stream of messages does
                    for (byte[] message : messages) {
                        send(outgoing, message);
                        acks.add(readFrame(incoming));
                    }
                } finally {
                    socket.close();
                }
            } catch (Exception e) {
                failure = e;

                // A thread that never reached the barrier would hold every other one there until
                // they timed out, so the barrier is broken outright instead
                barrier.reset();
            }
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

    // Reads what is to be sent, one base64-encoded message to a line.
    private static List<byte[]> readMessages(String path) throws Exception {

        List<byte[]> out = new ArrayList<>();

        for (String line : Files.readAllLines(Paths.get(path))) {

            String trimmed = line.trim();

            if (!trimmed.isEmpty()) {
                out.add(Base64.getDecoder().decode(trimmed));
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
