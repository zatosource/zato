// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
//
// The minimal foreign-runtime component of the live end-to-end suite - a Java TCP server
// that answers each line with its own pid prepended, which is how tests prove that
// a killed helper process was restarted. Build with: ./build.sh

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;

public class EchoServer {

    public static void main(String[] args) throws Exception {

        int port = Integer.parseInt(args[0]);
        long pid = ProcessHandle.current().pid();

        ServerSocket server = new ServerSocket(port, 50, InetAddress.getByName("127.0.0.1"));

        while (true) {
            Socket socket = server.accept();

            new Thread(() -> {
                try {
                    BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream(), "UTF-8"));
                    PrintWriter out = new PrintWriter(new OutputStreamWriter(socket.getOutputStream(), "UTF-8"), true);

                    String line;
                    while ((line = in.readLine()) != null) {
                        out.println("jar " + pid + " " + line);
                    }

                    socket.close();
                } catch (Exception e) {
                    // The connection is gone, nothing to do.
                }
            }).start();
        }
    }
}
