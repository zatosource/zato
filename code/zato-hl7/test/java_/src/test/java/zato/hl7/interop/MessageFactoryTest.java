package zato.hl7.interop;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Validates that all 30 messages are constructed without errors
 * and contain valid MSH headers.
 */
class MessageFactoryTest {

    @Test
    void allMessagesAreBuilt() throws Exception {
        MessageFactory factory = new MessageFactory();
        List<MessageFactory.MessageEntry> messages = factory.buildAll();
        assertEquals(30, messages.size(), "Expected 30 messages");
    }

    @Test
    void eachMessageStartsWithMsh() throws Exception {
        MessageFactory factory = new MessageFactory();
        List<MessageFactory.MessageEntry> messages = factory.buildAll();

        for (MessageFactory.MessageEntry entry : messages) {
            assertTrue(
                entry.encoded().startsWith("MSH|"),
                entry.label() + " does not start with MSH|"
            );
        }
    }

    @Test
    void eachMessageHasUniqueControlId() throws Exception {
        MessageFactory factory = new MessageFactory();
        List<MessageFactory.MessageEntry> messages = factory.buildAll();

        long distinctCount = messages.stream()
            .map(e -> extractControlId(e.encoded()))
            .distinct()
            .count();

        assertEquals(30, distinctCount, "Expected 30 unique control ids");
    }

    private String extractControlId(String hl7) {
        int firstCr = hl7.indexOf('\r');
        String msh = (firstCr == -1) ? hl7 : hl7.substring(0, firstCr);
        String[] fields = msh.split("\\|");
        return (fields.length > 9) ? fields[9] : "";
    }
}
