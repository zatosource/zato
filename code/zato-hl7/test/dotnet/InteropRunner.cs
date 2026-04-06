using System.Text;
using NHapi.Base.Parser;
using NHapiTools.Base.Net;

namespace Zato.Hl7.Interop;

/// <summary>
/// Sends all 30 HL7 messages over MLLP to the specified host:port
/// using NHapiTools SimpleMLLPClient (the standard .NET MLLP transport),
/// and prints one JSON line per message to stdout.
/// Exit code 0 = all passed, 1 = at least one failed.
/// </summary>
public static class InteropRunner
{
    public static int Main(string[] args)
    {
        if (args.Length < 2)
        {
            Console.Error.WriteLine("Usage: zato-hl7-interop <host> <port>");
            return 2;
        }

        var host = args[0];
        var port = int.Parse(args[1]);

        var factory = new MessageFactory();
        var messages = factory.BuildAll();
        var parser = new PipeParser();

        var allOk = true;

        using var client = new SimpleMLLPClient(host, port, Encoding.GetEncoding("iso-8859-1"));

        foreach (var entry in messages)
        {
            var label = entry.Label;
            var encoded = entry.Encoded;
            var controlId = ExtractControlId(encoded);

            var ok = false;
            var ackCode = "";
            var error = "";

            try
            {
                var responseStr = client.SendHL7Message(encoded);
                ackCode = ExtractAckCode(responseStr);
                ok = ackCode == "AA";
            }
            catch (Exception e)
            {
                error = (e.Message ?? "").Replace("\"", "'");
            }

            if (!ok)
                allOk = false;

            Console.WriteLine(
                $"{{\"msg_type\": \"{label}\", \"control_id\": \"{controlId}\", \"ack_code\": \"{ackCode}\", \"ok\": {(ok ? "true" : "false")}, \"error\": \"{error}\"}}"
            );
        }

        return allOk ? 0 : 1;
    }

    private static string ExtractControlId(string hl7Message)
    {
        var firstCr = hl7Message.IndexOf('\r');
        var msh = firstCr == -1 ? hl7Message : hl7Message[..firstCr];
        var fields = msh.Split('|');
        return fields.Length > 9 ? fields[9] : "";
    }

    private static string ExtractAckCode(string ack)
    {
        var segments = ack.Split('\r');
        foreach (var seg in segments)
        {
            if (seg.StartsWith("MSA"))
            {
                var fields = seg.Split('|');
                return fields.Length > 1 ? fields[1] : "";
            }
        }
        return "";
    }
}
