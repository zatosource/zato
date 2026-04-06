package zato.hl7.interop;

import ca.uhn.hl7v2.DefaultHapiContext;
import ca.uhn.hl7v2.HapiContext;
import ca.uhn.hl7v2.model.Message;
import ca.uhn.hl7v2.model.v25.message.*;
import ca.uhn.hl7v2.model.v25.segment.*;
import ca.uhn.hl7v2.parser.PipeParser;

import java.util.ArrayList;
import java.util.List;

/**
 * Builds the 30 most common HL7 v2 messages with realistic field values.
 * Each entry is a (label, encoded-message) pair.
 */
public class MessageFactory {

    private final HapiContext ctx;
    private final PipeParser parser;
    private int controlSeq = 1;

    public MessageFactory() {
        ctx = new DefaultHapiContext();
        parser = ctx.getPipeParser();
    }

    private String nextControlId() {
        return String.format("JAVA%05d", controlSeq++);
    }

    private void fillMsh(MSH msh, String messageType, String triggerEvent, String controlId) throws Exception {
        msh.getFieldSeparator().setValue("|");
        msh.getEncodingCharacters().setValue("^~\\&");
        msh.getSendingApplication().getNamespaceID().setValue("JavaInterop");
        msh.getSendingFacility().getNamespaceID().setValue("TestLab");
        msh.getReceivingApplication().getNamespaceID().setValue("ZatoApp");
        msh.getReceivingFacility().getNamespaceID().setValue("ZatoFac");
        msh.getDateTimeOfMessage().getTime().setValue("20250401120000");
        msh.getMessageType().getMessageCode().setValue(messageType);
        msh.getMessageType().getTriggerEvent().setValue(triggerEvent);
        msh.getMessageControlID().setValue(controlId);
        msh.getProcessingID().getProcessingID().setValue("P");
        msh.getVersionID().getVersionID().setValue("2.5");
    }

    private void fillPid(PID pid, String mrn, String lastName, String firstName, String dob, String sex) throws Exception {
        pid.getPatientIdentifierList(0).getIDNumber().setValue(mrn);
        pid.getPatientIdentifierList(0).getAssigningAuthority().getNamespaceID().setValue("Hospital");
        pid.getPatientIdentifierList(0).getIdentifierTypeCode().setValue("PI");
        pid.getPatientName(0).getFamilyName().getSurname().setValue(lastName);
        pid.getPatientName(0).getGivenName().setValue(firstName);
        pid.getDateTimeOfBirth().getTime().setValue(dob);
        pid.getAdministrativeSex().setValue(sex);
    }

    private void fillPv1(PV1 pv1, String patientClass, String location) throws Exception {
        pv1.getPatientClass().setValue(patientClass);
        pv1.getAssignedPatientLocation().getPointOfCare().setValue(location);
        pv1.getAssignedPatientLocation().getFacility().getNamespaceID().setValue("Hospital");
    }

    public record MessageEntry(String label, String encoded) {}

    public List<MessageEntry> buildAll() throws Exception {
        List<MessageEntry> out = new ArrayList<>();

        out.add(buildAdtA01());
        out.add(buildAdtA02());
        out.add(buildAdtA03());
        out.add(buildAdtA04());
        out.add(buildAdtA08());
        out.add(buildAdtA11());
        out.add(buildAdtA13());
        out.add(buildAdtA28());
        out.add(buildAdtA31());
        out.add(buildAdtA40());
        out.add(buildOrmO01());
        out.add(buildOruR01());
        out.add(buildOmlO21());
        out.add(buildOulR22());
        out.add(buildSiuS12());
        out.add(buildRdeO11());
        out.add(buildRdsO13());
        out.add(buildDftP03());
        out.add(buildMdmT02());
        out.add(buildBarP01());
        out.add(buildVxuV04());
        out.add(buildMfnM02());
        out.add(buildQbpQ11());
        out.add(buildRspK11());
        out.add(buildPprPc1());
        out.add(buildRasO17());
        out.add(buildAck());
        out.add(buildOmgO19());
        out.add(buildOmsO05());
        out.add(buildAdtA01WithObx());

        return out;
    }

    private MessageEntry buildAdtA01() throws Exception {
        ADT_A01 msg = new ADT_A01();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "ADT", "A01", cid);
        msg.getEVN().getEventTypeCode().setValue("A01");
        msg.getEVN().getRecordedDateTime().getTime().setValue("20250401120000");
        fillPid(msg.getPID(), "100001", "Mueller", "Hans", "19750315", "M");
        fillPv1(msg.getPV1(), "I", "W-100");
        return new MessageEntry("ADT_A01", parser.encode(msg));
    }

    private MessageEntry buildAdtA02() throws Exception {
        ADT_A02 msg = new ADT_A02();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "ADT", "A02", cid);
        msg.getEVN().getEventTypeCode().setValue("A02");
        msg.getEVN().getRecordedDateTime().getTime().setValue("20250401130000");
        fillPid(msg.getPID(), "100002", "Dupont", "Marie", "19820622", "F");
        fillPv1(msg.getPV1(), "I", "E-201");
        return new MessageEntry("ADT_A02", parser.encode(msg));
    }

    private MessageEntry buildAdtA03() throws Exception {
        ADT_A03 msg = new ADT_A03();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "ADT", "A03", cid);
        msg.getEVN().getEventTypeCode().setValue("A03");
        msg.getEVN().getRecordedDateTime().getTime().setValue("20250401140000");
        fillPid(msg.getPID(), "100003", "Tanaka", "Yuki", "19901108", "F");
        fillPv1(msg.getPV1(), "I", "S-305");
        return new MessageEntry("ADT_A03", parser.encode(msg));
    }

    // HAPI reuses ADT_A01 for A04, A08, A11, A13, A28, A31 triggers
    private MessageEntry buildAdtA04() throws Exception {
        ADT_A01 msg = new ADT_A01();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "ADT", "A04", cid);
        msg.getEVN().getEventTypeCode().setValue("A04");
        msg.getEVN().getRecordedDateTime().getTime().setValue("20250401150000");
        fillPid(msg.getPID(), "100004", "Garcia", "Carlos", "19680430", "M");
        fillPv1(msg.getPV1(), "O", "OUT-1");
        return new MessageEntry("ADT_A04", parser.encode(msg));
    }

    private MessageEntry buildAdtA08() throws Exception {
        ADT_A01 msg = new ADT_A01();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "ADT", "A08", cid);
        msg.getEVN().getEventTypeCode().setValue("A08");
        msg.getEVN().getRecordedDateTime().getTime().setValue("20250401160000");
        fillPid(msg.getPID(), "100005", "Bernard", "Pierre", "19550912", "M");
        fillPv1(msg.getPV1(), "I", "ICU-2");
        return new MessageEntry("ADT_A08", parser.encode(msg));
    }

    private MessageEntry buildAdtA11() throws Exception {
        ADT_A09 msg = new ADT_A09();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "ADT", "A11", cid);
        msg.getEVN().getEventTypeCode().setValue("A11");
        msg.getEVN().getRecordedDateTime().getTime().setValue("20250401170000");
        fillPid(msg.getPID(), "100006", "Andersson", "Erik", "19970305", "M");
        fillPv1(msg.getPV1(), "I", "W-100");
        return new MessageEntry("ADT_A11", parser.encode(msg));
    }

    private MessageEntry buildAdtA13() throws Exception {
        ADT_A01 msg = new ADT_A01();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "ADT", "A13", cid);
        msg.getEVN().getEventTypeCode().setValue("A13");
        msg.getEVN().getRecordedDateTime().getTime().setValue("20250401180000");
        fillPid(msg.getPID(), "100007", "Rossi", "Lucia", "19880720", "F");
        fillPv1(msg.getPV1(), "I", "W-201");
        return new MessageEntry("ADT_A13", parser.encode(msg));
    }

    private MessageEntry buildAdtA28() throws Exception {
        ADT_A05 msg = new ADT_A05();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "ADT", "A28", cid);
        msg.getEVN().getEventTypeCode().setValue("A28");
        msg.getEVN().getRecordedDateTime().getTime().setValue("20250402090000");
        fillPid(msg.getPID(), "200001", "Kowalski", "Anna", "20010115", "F");
        fillPv1(msg.getPV1(), "N", "REG-1");
        return new MessageEntry("ADT_A28", parser.encode(msg));
    }

    private MessageEntry buildAdtA31() throws Exception {
        ADT_A05 msg = new ADT_A05();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "ADT", "A31", cid);
        msg.getEVN().getEventTypeCode().setValue("A31");
        msg.getEVN().getRecordedDateTime().getTime().setValue("20250402100000");
        fillPid(msg.getPID(), "200002", "Nakamura", "Ken", "19790825", "M");
        fillPv1(msg.getPV1(), "N", "REG-1");
        return new MessageEntry("ADT_A31", parser.encode(msg));
    }

    private MessageEntry buildAdtA40() throws Exception {
        ADT_A39 msg = new ADT_A39();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "ADT", "A40", cid);
        msg.getEVN().getEventTypeCode().setValue("A40");
        msg.getEVN().getRecordedDateTime().getTime().setValue("20250402110000");
        msg.getPATIENT().getPID().getPatientIdentifierList(0).getIDNumber().setValue("300001");
        msg.getPATIENT().getPID().getPatientName(0).getFamilyName().getSurname().setValue("OldName");
        msg.getPATIENT().getPID().getPatientName(0).getGivenName().setValue("Patient");
        msg.getPATIENT().getMRG().getPriorPatientIdentifierList(0).getIDNumber().setValue("300002");
        return new MessageEntry("ADT_A40", parser.encode(msg));
    }

    private MessageEntry buildOrmO01() throws Exception {
        ORM_O01 msg = new ORM_O01();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "ORM", "O01", cid);
        fillPid(msg.getPATIENT().getPID(), "400001", "Schmidt", "Klaus", "19650210", "M");
        fillPv1(msg.getPATIENT().getPATIENT_VISIT().getPV1(), "I", "LAB-1");
        ORC orc = msg.getORDER().getORC();
        orc.getOrderControl().setValue("NW");
        orc.getPlacerOrderNumber().getEntityIdentifier().setValue("ORD-001");
        OBR obr = msg.getORDER().getORDER_DETAIL().getOBR();
        obr.getSetIDOBR().setValue("1");
        obr.getUniversalServiceIdentifier().getIdentifier().setValue("CBC");
        obr.getUniversalServiceIdentifier().getText().setValue("Complete Blood Count");
        return new MessageEntry("ORM_O01", parser.encode(msg));
    }

    private MessageEntry buildOruR01() throws Exception {
        ORU_R01 msg = new ORU_R01();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "ORU", "R01", cid);
        fillPid(msg.getPATIENT_RESULT().getPATIENT().getPID(), "400002", "Leroy", "Sophie", "19780504", "F");
        OBR obr = msg.getPATIENT_RESULT().getORDER_OBSERVATION().getOBR();
        obr.getSetIDOBR().setValue("1");
        obr.getUniversalServiceIdentifier().getIdentifier().setValue("GLU");
        obr.getUniversalServiceIdentifier().getText().setValue("Glucose");
        OBX obx = msg.getPATIENT_RESULT().getORDER_OBSERVATION().getOBSERVATION().getOBX();
        obx.getSetIDOBX().setValue("1");
        obx.getValueType().setValue("NM");
        obx.getObservationIdentifier().getIdentifier().setValue("GLU");
        obx.getObservationIdentifier().getText().setValue("Glucose");
        obx.getUnits().getIdentifier().setValue("mg/dL");
        obx.getObservationResultStatus().setValue("F");
        var ed = obx.getObservationValue(0);
        ed.getData().parse("95");
        return new MessageEntry("ORU_R01", parser.encode(msg));
    }

    private MessageEntry buildOmlO21() throws Exception {
        OML_O21 msg = new OML_O21();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "OML", "O21", cid);
        fillPid(msg.getPATIENT().getPID(), "400003", "Martinez", "Elena", "19850917", "F");
        ORC orc = msg.getORDER().getORC();
        orc.getOrderControl().setValue("NW");
        orc.getPlacerOrderNumber().getEntityIdentifier().setValue("LAB-100");
        OBR obr = msg.getORDER().getOBSERVATION_REQUEST().getOBR();
        obr.getSetIDOBR().setValue("1");
        obr.getUniversalServiceIdentifier().getIdentifier().setValue("BMP");
        obr.getUniversalServiceIdentifier().getText().setValue("Basic Metabolic Panel");
        return new MessageEntry("OML_O21", parser.encode(msg));
    }

    private MessageEntry buildOulR22() throws Exception {
        String cid = nextControlId();
        String raw = "MSH|^~\\&|JavaInterop|TestLab|ZatoApp|ZatoFac|20250402120000||OUL^R22|" + cid + "|P|2.5\r"
                + "PID|||500001^^^Hospital^PI||Weber^Thomas||19720818|M\r"
                + "OBR|1||LAB-200|CMP^Comprehensive Metabolic Panel\r"
                + "OBX|1|NM|NA^Sodium||140|mmol/L|136-145|N|||F\r";
        return new MessageEntry("OUL_R22", raw);
    }

    private MessageEntry buildSiuS12() throws Exception {
        SIU_S12 msg = new SIU_S12();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "SIU", "S12", cid);
        msg.getSCH().getPlacerAppointmentID().getEntityIdentifier().setValue("APPT-001");
        msg.getSCH().getAppointmentReason().getIdentifier().setValue("ROUTINE");
        fillPid(msg.getPATIENT().getPID(), "500002", "Fernandez", "Diego", "19950301", "M");
        fillPv1(msg.getPATIENT().getPV1(), "O", "CLINIC-A");
        return new MessageEntry("SIU_S12", parser.encode(msg));
    }

    private MessageEntry buildRdeO11() throws Exception {
        RDE_O11 msg = new RDE_O11();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "RDE", "O11", cid);
        fillPid(msg.getPATIENT().getPID(), "600001", "Petit", "Claire", "19830614", "F");
        fillPv1(msg.getPATIENT().getPATIENT_VISIT().getPV1(), "I", "PHARM-1");
        ORC orc = msg.getORDER().getORC();
        orc.getOrderControl().setValue("NW");
        orc.getPlacerOrderNumber().getEntityIdentifier().setValue("RX-001");
        msg.getORDER().getRXE().getQuantityTiming().getQuantity().getQuantity().setValue("1");
        msg.getORDER().getRXE().getGiveCode().getIdentifier().setValue("AMOX");
        msg.getORDER().getRXE().getGiveCode().getText().setValue("Amoxicillin 500mg");
        msg.getORDER().getRXE().getGiveAmountMinimum().setValue("500");
        msg.getORDER().getRXE().getGiveUnits().getIdentifier().setValue("mg");
        return new MessageEntry("RDE_O11", parser.encode(msg));
    }

    private MessageEntry buildRdsO13() throws Exception {
        RDS_O13 msg = new RDS_O13();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "RDS", "O13", cid);
        fillPid(msg.getPATIENT().getPID(), "600002", "Dubois", "Jean", "19700228", "M");
        fillPv1(msg.getPATIENT().getPATIENT_VISIT().getPV1(), "I", "PHARM-2");
        ORC orc = msg.getORDER().getORC();
        orc.getOrderControl().setValue("RE");
        orc.getPlacerOrderNumber().getEntityIdentifier().setValue("RX-002");
        msg.getORDER().getRXD().getDispenseGiveCode().getIdentifier().setValue("IBU");
        msg.getORDER().getRXD().getDispenseGiveCode().getText().setValue("Ibuprofen 400mg");
        msg.getORDER().getRXD().getActualDispenseAmount().setValue("30");
        msg.getORDER().getRXD().getActualDispenseUnits().getIdentifier().setValue("TAB");
        return new MessageEntry("RDS_O13", parser.encode(msg));
    }

    private MessageEntry buildDftP03() throws Exception {
        DFT_P03 msg = new DFT_P03();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "DFT", "P03", cid);
        msg.getEVN().getEventTypeCode().setValue("P03");
        msg.getEVN().getRecordedDateTime().getTime().setValue("20250402130000");
        fillPid(msg.getPID(), "700001", "Laurent", "Michel", "19600101", "M");
        fillPv1(msg.getPV1(), "I", "FIN-1");
        msg.getFINANCIAL().getFT1().getSetIDFT1().setValue("1");
        msg.getFINANCIAL().getFT1().getTransactionDate().getRangeStartDateTime().getTime().setValue("20250402");
        msg.getFINANCIAL().getFT1().getTransactionType().setValue("CG");
        msg.getFINANCIAL().getFT1().getTransactionCode().getIdentifier().setValue("99213");
        msg.getFINANCIAL().getFT1().getTransactionCode().getText().setValue("Office Visit Level 3");
        return new MessageEntry("DFT_P03", parser.encode(msg));
    }

    private MessageEntry buildMdmT02() throws Exception {
        String cid = nextControlId();
        String raw = "MSH|^~\\&|JavaInterop|TestLab|ZatoApp|ZatoFac|20250402140000||MDM^T02|" + cid + "|P|2.5\r"
                + "EVN|T02|20250402140000\r"
                + "PID|||700002^^^Hospital^PI||Moreau^Isabelle||19920506|F\r"
                + "PV1||O|DOC-1^^^Hospital\r"
                + "TXA|1|HP|FT|20250402140000||||||||DOC-12345||||AU\r"
                + "OBX|1|TX|DOCTEXT^Document Text||Patient presents with mild headache|||||||F\r";
        return new MessageEntry("MDM_T02", raw);
    }

    private MessageEntry buildBarP01() throws Exception {
        BAR_P01 msg = new BAR_P01();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "BAR", "P01", cid);
        msg.getEVN().getEventTypeCode().setValue("P01");
        msg.getEVN().getRecordedDateTime().getTime().setValue("20250402150000");
        fillPid(msg.getPID(), "800001", "Blanc", "Philippe", "19500820", "M");
        fillPv1(msg.getVISIT().getPV1(), "I", "ADM-1");
        return new MessageEntry("BAR_P01", parser.encode(msg));
    }

    private MessageEntry buildVxuV04() throws Exception {
        VXU_V04 msg = new VXU_V04();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "VXU", "V04", cid);
        fillPid(msg.getPID(), "800002", "Fontaine", "Amelie", "20200315", "F");
        msg.getORDER().getORC().getOrderControl().setValue("RE");
        msg.getORDER().getRXA().getAdministrationSubIDCounter().setValue("0");
        msg.getORDER().getRXA().getDateTimeStartOfAdministration().getTime().setValue("20250402");
        msg.getORDER().getRXA().getDateTimeEndOfAdministration().getTime().setValue("20250402");
        msg.getORDER().getRXA().getAdministeredCode().getIdentifier().setValue("141");
        msg.getORDER().getRXA().getAdministeredCode().getText().setValue("Influenza seasonal injectable preservative free");
        msg.getORDER().getRXA().getAdministeredAmount().setValue("0.5");
        msg.getORDER().getRXA().getAdministeredUnits().getIdentifier().setValue("mL");
        return new MessageEntry("VXU_V04", parser.encode(msg));
    }

    private MessageEntry buildMfnM02() throws Exception {
        String cid = nextControlId();
        String raw = "MSH|^~\\&|JavaInterop|TestLab|ZatoApp|ZatoFac|20250402155000||MFN^M02|" + cid + "|P|2.5\r"
                + "MFI|PRA^Practitioner Master File|UPD|||NE\r"
                + "MFE|MAD|20250402|20250402|DR-001\r"
                + "STF|DR-001|DR-001||Martin^Robert||MD\r"
                + "PRA||^^^Hospital|MD|I|DR-001\r";
        return new MessageEntry("MFN_M02", raw);
    }

    private MessageEntry buildQbpQ11() throws Exception {
        String cid = nextControlId();
        String raw = "MSH|^~\\&|JavaInterop|TestLab|ZatoApp|ZatoFac|20250402160000||QBP^Q11|" + cid + "|P|2.5\r"
                + "QPD|Q11^Query by parameter|QRY-001|100001^^^Hospital^PI\r"
                + "RCP|I|10^RD\r";
        return new MessageEntry("QBP_Q11", raw);
    }

    private MessageEntry buildRspK11() throws Exception {
        String cid = nextControlId();
        String raw = "MSH|^~\\&|JavaInterop|TestLab|ZatoApp|ZatoFac|20250402161000||RSP^K11|" + cid + "|P|2.5\r"
                + "MSA|AA|QRY-001\r"
                + "QAK|QRY-001|OK|Q11^Query by parameter\r"
                + "QPD|Q11^Query by parameter|QRY-001|100001^^^Hospital^PI\r"
                + "PID|||100001^^^Hospital^PI||Mueller^Hans||19750315|M\r";
        return new MessageEntry("RSP_K11", raw);
    }

    private MessageEntry buildPprPc1() throws Exception {
        String cid = nextControlId();
        String raw = "MSH|^~\\&|JavaInterop|TestLab|ZatoApp|ZatoFac|20250402170000||PPR^PC1|" + cid + "|P|2.5\r"
                + "PID|||900001^^^Hospital^PI||Kim^Soo-Jin||19880401|F\r"
                + "PRB|AD|20250402|HYPERTENSION^Essential hypertension^ICD10|PRB-001\r";
        return new MessageEntry("PPR_PC1", raw);
    }

    private MessageEntry buildRasO17() throws Exception {
        String cid = nextControlId();
        String raw = "MSH|^~\\&|JavaInterop|TestLab|ZatoApp|ZatoFac|20250402180000||RAS^O17|" + cid + "|P|2.5\r"
                + "PID|||900002^^^Hospital^PI||Yamamoto^Kenji||19650715|M\r"
                + "ORC|RE|RX-100|||\r"
                + "RXA|0|1|20250402||METFORMIN^Metformin 500mg|1|TAB|||DR-001\r";
        return new MessageEntry("RAS_O17", raw);
    }

    private MessageEntry buildAck() throws Exception {
        ACK msg = new ACK();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "ACK", "A01", cid);
        msg.getMSA().getAcknowledgmentCode().setValue("AA");
        msg.getMSA().getMessageControlID().setValue("ORIG-001");
        return new MessageEntry("ACK", parser.encode(msg));
    }

    private MessageEntry buildOmgO19() throws Exception {
        OMG_O19 msg = new OMG_O19();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "OMG", "O19", cid);
        fillPid(msg.getPATIENT().getPID(), "950001", "Johansson", "Lars", "19730520", "M");
        fillPv1(msg.getPATIENT().getPATIENT_VISIT().getPV1(), "I", "RAD-1");
        ORC orc = msg.getORDER().getORC();
        orc.getOrderControl().setValue("NW");
        orc.getPlacerOrderNumber().getEntityIdentifier().setValue("RAD-500");
        OBR obr = msg.getORDER().getOBR();
        obr.getSetIDOBR().setValue("1");
        obr.getUniversalServiceIdentifier().getIdentifier().setValue("XR-CHEST");
        obr.getUniversalServiceIdentifier().getText().setValue("Chest X-Ray PA and Lateral");
        return new MessageEntry("OMG_O19", parser.encode(msg));
    }

    private MessageEntry buildOmsO05() throws Exception {
        OMS_O05 msg = new OMS_O05();
        String cid = nextControlId();
        fillMsh(msg.getMSH(), "OMS", "O05", cid);
        fillPid(msg.getPATIENT().getPID(), "950002", "Bergstrom", "Karin", "19810930", "F");
        fillPv1(msg.getPATIENT().getPATIENT_VISIT().getPV1(), "I", "SUP-1");
        ORC orc = msg.getORDER().getORC();
        orc.getOrderControl().setValue("NW");
        orc.getPlacerOrderNumber().getEntityIdentifier().setValue("SUP-001");
        msg.getORDER().getRQD().getRequisitionLineNumber().setValue("1");
        msg.getORDER().getRQD().getItemCodeInternal().getIdentifier().setValue("GLOVES-M");
        msg.getORDER().getRQD().getItemCodeInternal().getText().setValue("Exam Gloves Medium");
        return new MessageEntry("OMS_O05", parser.encode(msg));
    }

    private MessageEntry buildAdtA01WithObx() throws Exception {
        String cid = nextControlId();
        String raw = "MSH|^~\\&|JavaInterop|TestLab|ZatoApp|ZatoFac|20250403090000||ADT^A01|" + cid + "|P|2.5\r"
                + "EVN|A01|20250403090000\r"
                + "PID|||999001^^^Hospital^PI||Schneider^Lisa||19780112|F\r"
                + "PV1||E|ER-1^^^Hospital\r"
                + "OBX|1|NM|8310-5^Body Temperature||38.7|Cel|||||F\r";
        return new MessageEntry("ADT_A01_OBX", raw);
    }
}
