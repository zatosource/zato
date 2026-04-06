using NHapi.Base.Model;
using NHapi.Base.Parser;
using NHapi.Model.V25.Datatype;
using NHapi.Model.V25.Message;
using NHapi.Model.V25.Segment;

namespace Zato.Hl7.Interop;

/// <summary>
/// Builds the 30 most common HL7 v2 messages using nHapi's typed API.
/// Each entry is a (label, encoded-message) pair.
/// </summary>
public class MessageFactory
{
    private readonly PipeParser _parser = new();
    private int _controlSeq = 1;

    private string NextControlId() => $"DOTNET{_controlSeq++:D5}";

    private static void FillMsh(MSH msh, string messageType, string triggerEvent, string controlId)
    {
        msh.FieldSeparator.Value = "|";
        msh.EncodingCharacters.Value = @"^~\&";
        msh.SendingApplication.NamespaceID.Value = "DotNetInterop";
        msh.SendingFacility.NamespaceID.Value = "TestLab";
        msh.ReceivingApplication.NamespaceID.Value = "ZatoApp";
        msh.ReceivingFacility.NamespaceID.Value = "ZatoFac";
        msh.DateTimeOfMessage.Time.Value = "20250401120000";
        msh.MessageType.MessageCode.Value = messageType;
        msh.MessageType.TriggerEvent.Value = triggerEvent;
        msh.MessageControlID.Value = controlId;
        msh.ProcessingID.ProcessingID.Value = "P";
        msh.VersionID.VersionID.Value = "2.5";
    }

    private static void FillPid(PID pid, string mrn, string lastName, string firstName, string dob, string sex)
    {
        pid.GetPatientIdentifierList(0).IDNumber.Value = mrn;
        pid.GetPatientIdentifierList(0).AssigningAuthority.NamespaceID.Value = "Hospital";
        pid.GetPatientIdentifierList(0).IdentifierTypeCode.Value = "PI";
        pid.GetPatientName(0).FamilyName.Surname.Value = lastName;
        pid.GetPatientName(0).GivenName.Value = firstName;
        pid.DateTimeOfBirth.Time.Value = dob;
        pid.AdministrativeSex.Value = sex;
    }

    private static void FillPv1(PV1 pv1, string patientClass, string location)
    {
        pv1.PatientClass.Value = patientClass;
        pv1.AssignedPatientLocation.PointOfCare.Value = location;
        pv1.AssignedPatientLocation.Facility.NamespaceID.Value = "Hospital";
    }

    private static void SetVariesSt(Varies varies, IMessage msg, string value)
    {
        var st = new ST(msg);
        st.Value = value;
        varies.Data = st;
    }

    public record MessageEntry(string Label, string Encoded);

    public List<MessageEntry> BuildAll()
    {
        var all = new List<MessageEntry>
        {
            BuildAdtA01(),
            BuildAdtA02(),
            BuildAdtA03(),
            BuildAdtA04(),
            BuildAdtA08(),
            BuildAdtA11(),
            BuildAdtA13(),
            BuildAdtA28(),
            BuildAdtA31(),
            BuildAdtA40(),
            BuildOrmO01(),
            BuildOruR01(),
            BuildOmlO21(),
            BuildOulR22(),
            BuildSiuS12(),
            BuildRdeO11(),
            BuildRdsO13(),
            BuildDftP03(),
            BuildMdmT02(),
            BuildBarP01(),
            BuildVxuV04(),
            BuildMfnM02(),
            BuildQbpQ11(),
            BuildRspK11(),
            BuildPprPc1(),
            BuildRasO17(),
            BuildAck(),
            BuildOmgO19(),
            BuildOmsO05(),
            BuildAdtA01WithObx(),
        };
        return all;
    }

    private MessageEntry BuildAdtA01()
    {
        var msg = new ADT_A01();
        var cid = NextControlId();
        FillMsh(msg.MSH, "ADT", "A01", cid);
        msg.EVN.EventTypeCode.Value = "A01";
        msg.EVN.RecordedDateTime.Time.Value = "20250401120000";
        FillPid(msg.PID, "100001", "Mueller", "Hans", "19750315", "M");
        FillPv1(msg.PV1, "I", "W-100");
        return new MessageEntry("ADT_A01", _parser.Encode(msg));
    }

    private MessageEntry BuildAdtA02()
    {
        var msg = new ADT_A02();
        var cid = NextControlId();
        FillMsh(msg.MSH, "ADT", "A02", cid);
        msg.EVN.EventTypeCode.Value = "A02";
        msg.EVN.RecordedDateTime.Time.Value = "20250401130000";
        FillPid(msg.PID, "100002", "Dupont", "Marie", "19820622", "F");
        FillPv1(msg.PV1, "I", "E-201");
        return new MessageEntry("ADT_A02", _parser.Encode(msg));
    }

    private MessageEntry BuildAdtA03()
    {
        var msg = new ADT_A03();
        var cid = NextControlId();
        FillMsh(msg.MSH, "ADT", "A03", cid);
        msg.EVN.EventTypeCode.Value = "A03";
        msg.EVN.RecordedDateTime.Time.Value = "20250401140000";
        FillPid(msg.PID, "100003", "Tanaka", "Yuki", "19901108", "F");
        FillPv1(msg.PV1, "I", "S-305");
        return new MessageEntry("ADT_A03", _parser.Encode(msg));
    }

    private MessageEntry BuildAdtA04()
    {
        var msg = new ADT_A01();
        var cid = NextControlId();
        FillMsh(msg.MSH, "ADT", "A04", cid);
        msg.EVN.EventTypeCode.Value = "A04";
        msg.EVN.RecordedDateTime.Time.Value = "20250401150000";
        FillPid(msg.PID, "100004", "Garcia", "Carlos", "19680430", "M");
        FillPv1(msg.PV1, "O", "OUT-1");
        return new MessageEntry("ADT_A04", _parser.Encode(msg));
    }

    private MessageEntry BuildAdtA08()
    {
        var msg = new ADT_A01();
        var cid = NextControlId();
        FillMsh(msg.MSH, "ADT", "A08", cid);
        msg.EVN.EventTypeCode.Value = "A08";
        msg.EVN.RecordedDateTime.Time.Value = "20250401160000";
        FillPid(msg.PID, "100005", "Bernard", "Pierre", "19550912", "M");
        FillPv1(msg.PV1, "I", "WELL-2");
        return new MessageEntry("ADT_A08", _parser.Encode(msg));
    }

    private MessageEntry BuildAdtA11()
    {
        var msg = new ADT_A09();
        var cid = NextControlId();
        FillMsh(msg.MSH, "ADT", "A11", cid);
        msg.EVN.EventTypeCode.Value = "A11";
        msg.EVN.RecordedDateTime.Time.Value = "20250401170000";
        FillPid(msg.PID, "100006", "Andersson", "Erik", "19970305", "M");
        FillPv1(msg.PV1, "I", "W-100");
        return new MessageEntry("ADT_A11", _parser.Encode(msg));
    }

    private MessageEntry BuildAdtA13()
    {
        var msg = new ADT_A01();
        var cid = NextControlId();
        FillMsh(msg.MSH, "ADT", "A13", cid);
        msg.EVN.EventTypeCode.Value = "A13";
        msg.EVN.RecordedDateTime.Time.Value = "20250401180000";
        FillPid(msg.PID, "100007", "Rossi", "Lucia", "19880720", "F");
        FillPv1(msg.PV1, "I", "W-201");
        return new MessageEntry("ADT_A13", _parser.Encode(msg));
    }

    private MessageEntry BuildAdtA28()
    {
        var msg = new ADT_A05();
        var cid = NextControlId();
        FillMsh(msg.MSH, "ADT", "A28", cid);
        msg.EVN.EventTypeCode.Value = "A28";
        msg.EVN.RecordedDateTime.Time.Value = "20250402090000";
        FillPid(msg.PID, "200001", "Kowalski", "Anna", "20010115", "F");
        FillPv1(msg.PV1, "N", "REG-1");
        return new MessageEntry("ADT_A28", _parser.Encode(msg));
    }

    private MessageEntry BuildAdtA31()
    {
        var msg = new ADT_A05();
        var cid = NextControlId();
        FillMsh(msg.MSH, "ADT", "A31", cid);
        msg.EVN.EventTypeCode.Value = "A31";
        msg.EVN.RecordedDateTime.Time.Value = "20250402100000";
        FillPid(msg.PID, "200002", "Nakamura", "Ken", "19790825", "M");
        FillPv1(msg.PV1, "N", "REG-1");
        return new MessageEntry("ADT_A31", _parser.Encode(msg));
    }

    private MessageEntry BuildAdtA40()
    {
        var msg = new ADT_A39();
        var cid = NextControlId();
        FillMsh(msg.MSH, "ADT", "A40", cid);
        msg.EVN.EventTypeCode.Value = "A40";
        msg.EVN.RecordedDateTime.Time.Value = "20250402110000";
        msg.GetPATIENT().PID.GetPatientIdentifierList(0).IDNumber.Value = "300001";
        msg.GetPATIENT().PID.GetPatientName(0).FamilyName.Surname.Value = "OldName";
        msg.GetPATIENT().PID.GetPatientName(0).GivenName.Value = "Patient";
        msg.GetPATIENT().MRG.GetPriorPatientIdentifierList(0).IDNumber.Value = "300002";
        return new MessageEntry("ADT_A40", _parser.Encode(msg));
    }

    private MessageEntry BuildOrmO01()
    {
        var msg = new ORM_O01();
        var cid = NextControlId();
        FillMsh(msg.MSH, "ORM", "O01", cid);
        FillPid(msg.PATIENT.PID, "400001", "Schmidt", "Klaus", "19650210", "M");
        FillPv1(msg.PATIENT.PATIENT_VISIT.PV1, "I", "LAB-1");
        var orc = msg.GetORDER().ORC;
        orc.OrderControl.Value = "NW";
        orc.PlacerOrderNumber.EntityIdentifier.Value = "ORD-001";
        var obr = msg.GetORDER().ORDER_DETAIL.OBR;
        obr.SetIDOBR.Value = "1";
        obr.UniversalServiceIdentifier.Identifier.Value = "CBC";
        obr.UniversalServiceIdentifier.Text.Value = "Complete Blood Count";
        return new MessageEntry("ORM_O01", _parser.Encode(msg));
    }

    private MessageEntry BuildOruR01()
    {
        var msg = new ORU_R01();
        var cid = NextControlId();
        FillMsh(msg.MSH, "ORU", "R01", cid);
        FillPid(msg.GetPATIENT_RESULT().PATIENT.PID, "400002", "Leroy", "Sophie", "19780504", "F");
        var obr = msg.GetPATIENT_RESULT().GetORDER_OBSERVATION().OBR;
        obr.SetIDOBR.Value = "1";
        obr.UniversalServiceIdentifier.Identifier.Value = "GLU";
        obr.UniversalServiceIdentifier.Text.Value = "Glucose";
        var obx = msg.GetPATIENT_RESULT().GetORDER_OBSERVATION().GetOBSERVATION().OBX;
        obx.SetIDOBX.Value = "1";
        obx.ValueType.Value = "NM";
        obx.ObservationIdentifier.Identifier.Value = "GLU";
        obx.ObservationIdentifier.Text.Value = "Glucose";
        obx.Units.Identifier.Value = "mg/dL";
        obx.ObservationResultStatus.Value = "F";
        SetVariesSt(obx.GetObservationValue(0), msg, "95");
        return new MessageEntry("ORU_R01", _parser.Encode(msg));
    }

    private MessageEntry BuildOmlO21()
    {
        var msg = new OML_O21();
        var cid = NextControlId();
        FillMsh(msg.MSH, "OML", "O21", cid);
        FillPid(msg.PATIENT.PID, "400003", "Martinez", "Elena", "19850917", "F");
        var orc = msg.GetORDER().ORC;
        orc.OrderControl.Value = "NW";
        orc.PlacerOrderNumber.EntityIdentifier.Value = "LAB-100";
        var obr = msg.GetORDER().OBSERVATION_REQUEST.OBR;
        obr.SetIDOBR.Value = "1";
        obr.UniversalServiceIdentifier.Identifier.Value = "BMP";
        obr.UniversalServiceIdentifier.Text.Value = "Basic Metabolic Panel";
        return new MessageEntry("OML_O21", _parser.Encode(msg));
    }

    private MessageEntry BuildOulR22()
    {
        var msg = new OUL_R22();
        var cid = NextControlId();
        FillMsh(msg.MSH, "OUL", "R22", cid);
        msg.MSH.DateTimeOfMessage.Time.Value = "20250402120000";
        FillPid(msg.PATIENT.PID, "500001", "Weber", "Thomas", "19720818", "M");
        var obr = msg.GetSPECIMEN().GetORDER().OBR;
        obr.SetIDOBR.Value = "1";
        obr.UniversalServiceIdentifier.Identifier.Value = "CMP";
        obr.UniversalServiceIdentifier.Text.Value = "Comprehensive Metabolic Panel";
        var obx = msg.GetSPECIMEN().GetORDER().GetRESULT().OBX;
        obx.SetIDOBX.Value = "1";
        obx.ValueType.Value = "NM";
        obx.ObservationIdentifier.Identifier.Value = "NA";
        obx.ObservationIdentifier.Text.Value = "Sodium";
        SetVariesSt(obx.GetObservationValue(0), msg, "140");
        obx.Units.Identifier.Value = "mmol/L";
        obx.ReferencesRange.Value = "136-145";
        obx.GetAbnormalFlags(0).Value = "N";
        obx.ObservationResultStatus.Value = "F";
        return new MessageEntry("OUL_R22", _parser.Encode(msg));
    }

    private MessageEntry BuildSiuS12()
    {
        var msg = new SIU_S12();
        var cid = NextControlId();
        FillMsh(msg.MSH, "SIU", "S12", cid);
        msg.SCH.PlacerAppointmentID.EntityIdentifier.Value = "APPT-001";
        msg.SCH.AppointmentReason.Identifier.Value = "ROUTINE";
        FillPid(msg.GetPATIENT().PID, "500002", "Fernandez", "Diego", "19950301", "M");
        FillPv1(msg.GetPATIENT().PV1, "O", "CLINIC-A");
        return new MessageEntry("SIU_S12", _parser.Encode(msg));
    }

    private MessageEntry BuildRdeO11()
    {
        var msg = new RDE_O11();
        var cid = NextControlId();
        FillMsh(msg.MSH, "RDE", "O11", cid);
        FillPid(msg.PATIENT.PID, "600001", "Petit", "Claire", "19830614", "F");
        FillPv1(msg.PATIENT.PATIENT_VISIT.PV1, "I", "PHARM-1");
        var orc = msg.GetORDER().ORC;
        orc.OrderControl.Value = "NW";
        orc.PlacerOrderNumber.EntityIdentifier.Value = "RX-001";
        msg.GetORDER().RXE.QuantityTiming.Quantity.Quantity.Value = "1";
        msg.GetORDER().RXE.GiveCode.Identifier.Value = "MULTIVIT";
        msg.GetORDER().RXE.GiveCode.Text.Value = "Daily Multivitamin";
        msg.GetORDER().RXE.GiveAmountMinimum.Value = "1";
        msg.GetORDER().RXE.GiveUnits.Identifier.Value = "TAB";
        return new MessageEntry("RDE_O11", _parser.Encode(msg));
    }

    private MessageEntry BuildRdsO13()
    {
        var msg = new RDS_O13();
        var cid = NextControlId();
        FillMsh(msg.MSH, "RDS", "O13", cid);
        FillPid(msg.PATIENT.PID, "600002", "Dubois", "Jean", "19700228", "M");
        FillPv1(msg.PATIENT.PATIENT_VISIT.PV1, "I", "PHARM-2");
        var orc = msg.GetORDER().ORC;
        orc.OrderControl.Value = "RE";
        orc.PlacerOrderNumber.EntityIdentifier.Value = "RX-002";
        msg.GetORDER().RXD.DispenseGiveCode.Identifier.Value = "VITD";
        msg.GetORDER().RXD.DispenseGiveCode.Text.Value = "Vitamin D3 1000 IU";
        msg.GetORDER().RXD.ActualDispenseAmount.Value = "90";
        msg.GetORDER().RXD.ActualDispenseUnits.Identifier.Value = "TAB";
        return new MessageEntry("RDS_O13", _parser.Encode(msg));
    }

    private MessageEntry BuildDftP03()
    {
        var msg = new DFT_P03();
        var cid = NextControlId();
        FillMsh(msg.MSH, "DFT", "P03", cid);
        msg.EVN.EventTypeCode.Value = "P03";
        msg.EVN.RecordedDateTime.Time.Value = "20250402130000";
        FillPid(msg.PID, "700001", "Laurent", "Michel", "19600101", "M");
        FillPv1(msg.PV1, "I", "FIN-1");
        msg.GetFINANCIAL().FT1.SetIDFT1.Value = "1";
        msg.GetFINANCIAL().FT1.TransactionDate.RangeStartDateTime.Time.Value = "20250402";
        msg.GetFINANCIAL().FT1.TransactionType.Value = "CG";
        msg.GetFINANCIAL().FT1.TransactionCode.Identifier.Value = "99213";
        msg.GetFINANCIAL().FT1.TransactionCode.Text.Value = "Office Visit Level 3";
        return new MessageEntry("DFT_P03", _parser.Encode(msg));
    }

    private MessageEntry BuildMdmT02()
    {
        var msg = new MDM_T02();
        var cid = NextControlId();
        FillMsh(msg.MSH, "MDM", "T02", cid);
        msg.MSH.DateTimeOfMessage.Time.Value = "20250402140000";
        msg.EVN.EventTypeCode.Value = "T02";
        msg.EVN.RecordedDateTime.Time.Value = "20250402140000";
        FillPid(msg.PID, "700002", "Moreau", "Isabelle", "19920506", "F");
        FillPv1(msg.PV1, "O", "DOC-1");
        msg.TXA.SetIDTXA.Value = "1";
        msg.TXA.DocumentType.Value = "HP";
        msg.TXA.DocumentContentPresentation.Value = "FT";
        msg.TXA.ActivityDateTime.Time.Value = "20250402140000";
        msg.TXA.UniqueDocumentNumber.EntityIdentifier.Value = "DOC-12345";
        msg.TXA.DocumentCompletionStatus.Value = "AU";
        var obx = msg.GetOBSERVATION().OBX;
        obx.SetIDOBX.Value = "1";
        obx.ValueType.Value = "TX";
        obx.ObservationIdentifier.Identifier.Value = "DOCTEXT";
        obx.ObservationIdentifier.Text.Value = "Document Text";
        SetVariesSt(obx.GetObservationValue(0), msg, "Annual wellness visit completed with all results within normal range");
        obx.ObservationResultStatus.Value = "F";
        return new MessageEntry("MDM_T02", _parser.Encode(msg));
    }

    private MessageEntry BuildBarP01()
    {
        var msg = new BAR_P01();
        var cid = NextControlId();
        FillMsh(msg.MSH, "BAR", "P01", cid);
        msg.EVN.EventTypeCode.Value = "P01";
        msg.EVN.RecordedDateTime.Time.Value = "20250402150000";
        FillPid(msg.PID, "800001", "Blanc", "Philippe", "19500820", "M");
        FillPv1(msg.GetVISIT().PV1, "I", "ADM-1");
        return new MessageEntry("BAR_P01", _parser.Encode(msg));
    }

    private MessageEntry BuildVxuV04()
    {
        var msg = new VXU_V04();
        var cid = NextControlId();
        FillMsh(msg.MSH, "VXU", "V04", cid);
        FillPid(msg.PID, "800002", "Fontaine", "Amelie", "20200315", "F");
        msg.GetORDER().ORC.OrderControl.Value = "RE";
        msg.GetORDER().RXA.AdministrationSubIDCounter.Value = "0";
        msg.GetORDER().RXA.DateTimeStartOfAdministration.Time.Value = "20250402";
        msg.GetORDER().RXA.DateTimeEndOfAdministration.Time.Value = "20250402";
        msg.GetORDER().RXA.AdministeredCode.Identifier.Value = "141";
        msg.GetORDER().RXA.AdministeredCode.Text.Value = "Influenza seasonal injectable preservative free";
        msg.GetORDER().RXA.AdministeredAmount.Value = "0.5";
        msg.GetORDER().RXA.AdministeredUnits.Identifier.Value = "mL";
        return new MessageEntry("VXU_V04", _parser.Encode(msg));
    }

    private MessageEntry BuildMfnM02()
    {
        var msg = new MFN_M02();
        var cid = NextControlId();
        FillMsh(msg.MSH, "MFN", "M02", cid);
        msg.MSH.DateTimeOfMessage.Time.Value = "20250402155000";
        msg.MFI.MasterFileIdentifier.Identifier.Value = "PRA";
        msg.MFI.MasterFileIdentifier.Text.Value = "Practitioner Master File";
        msg.MFI.FileLevelEventCode.Value = "UPD";
        var mfe = msg.GetMF_STAFF().MFE;
        mfe.RecordLevelEventCode.Value = "MAD";
        mfe.EffectiveDateTime.Time.Value = "20250402";
        SetVariesSt(mfe.GetPrimaryKeyValueMFE(0), msg, "DR-001");
        mfe.GetPrimaryKeyValueType(0).Value = "CE";
        msg.GetMF_STAFF().STF.PrimaryKeyValueSTF.Identifier.Value = "DR-001";
        msg.GetMF_STAFF().STF.GetStaffIdentifierList(0).IDNumber.Value = "DR-001";
        msg.GetMF_STAFF().STF.GetStaffName(0).FamilyName.Surname.Value = "Martin";
        msg.GetMF_STAFF().STF.GetStaffName(0).GivenName.Value = "Robert";
        msg.GetMF_STAFF().STF.GetStaffType(0).Value = "MD";
        return new MessageEntry("MFN_M02", _parser.Encode(msg));
    }

    private MessageEntry BuildQbpQ11()
    {
        var msg = new QBP_Q11();
        var cid = NextControlId();
        FillMsh(msg.MSH, "QBP", "Q11", cid);
        msg.MSH.DateTimeOfMessage.Time.Value = "20250402160000";
        msg.QPD.MessageQueryName.Identifier.Value = "Q11";
        msg.QPD.MessageQueryName.Text.Value = "Query by parameter";
        msg.QPD.QueryTag.Value = "QRY-001";
        SetVariesSt(msg.QPD.UserParametersInsuccessivefields, msg, "100001^^^Hospital^PI");
        msg.RCP.QueryPriority.Value = "I";
        msg.RCP.QuantityLimitedRequest.Quantity.Value = "10";
        msg.RCP.QuantityLimitedRequest.Units.Identifier.Value = "RD";
        return new MessageEntry("QBP_Q11", _parser.Encode(msg));
    }

    private MessageEntry BuildRspK11()
    {
        var msg = new RSP_K11();
        var cid = NextControlId();
        FillMsh(msg.MSH, "RSP", "K11", cid);
        msg.MSH.DateTimeOfMessage.Time.Value = "20250402161000";
        msg.MSA.AcknowledgmentCode.Value = "AA";
        msg.MSA.MessageControlID.Value = "QRY-001";
        msg.QAK.QueryTag.Value = "QRY-001";
        msg.QAK.QueryResponseStatus.Value = "OK";
        msg.QAK.MessageQueryName.Identifier.Value = "Q11";
        msg.QAK.MessageQueryName.Text.Value = "Query by parameter";
        msg.QPD.MessageQueryName.Identifier.Value = "Q11";
        msg.QPD.MessageQueryName.Text.Value = "Query by parameter";
        msg.QPD.QueryTag.Value = "QRY-001";
        SetVariesSt(msg.QPD.UserParametersInsuccessivefields, msg, "100001^^^Hospital^PI");
        msg.AddNonstandardSegment("PID");
        var pid = (PID)msg.GetStructure("PID");
        FillPid(pid, "100001", "Mueller", "Hans", "19750315", "M");
        return new MessageEntry("RSP_K11", _parser.Encode(msg));
    }

    private MessageEntry BuildPprPc1()
    {
        var msg = new PPR_PC1();
        var cid = NextControlId();
        FillMsh(msg.MSH, "PPR", "PC1", cid);
        msg.MSH.DateTimeOfMessage.Time.Value = "20250402170000";
        FillPid(msg.PID, "900001", "Kim", "Soo-Jin", "19880401", "F");
        var prb = msg.GetPROBLEM().PRB;
        prb.ActionCode.Value = "AD";
        prb.ActionDateTime.Time.Value = "20250402";
        prb.ProblemID.Identifier.Value = "Z00.00";
        prb.ProblemID.Text.Value = "Routine general health checkup";
        prb.ProblemID.NameOfCodingSystem.Value = "ICD10";
        prb.ProblemInstanceID.EntityIdentifier.Value = "PRB-001";
        return new MessageEntry("PPR_PC1", _parser.Encode(msg));
    }

    private MessageEntry BuildRasO17()
    {
        var msg = new RAS_O17();
        var cid = NextControlId();
        FillMsh(msg.MSH, "RAS", "O17", cid);
        msg.MSH.DateTimeOfMessage.Time.Value = "20250402180000";
        FillPid(msg.PATIENT.PID, "900002", "Yamamoto", "Kenji", "19650715", "M");
        msg.GetORDER().ORC.OrderControl.Value = "RE";
        msg.GetORDER().ORC.PlacerOrderNumber.EntityIdentifier.Value = "RX-100";
        var rxa = msg.GetORDER().GetADMINISTRATION().GetRXA();
        rxa.GiveSubIDCounter.Value = "0";
        rxa.AdministrationSubIDCounter.Value = "1";
        rxa.DateTimeStartOfAdministration.Time.Value = "20250402";
        rxa.AdministeredCode.Identifier.Value = "VITB12";
        rxa.AdministeredCode.Text.Value = "Vitamin B12 1000mcg";
        rxa.AdministeredAmount.Value = "1";
        rxa.AdministeredUnits.Identifier.Value = "TAB";
        return new MessageEntry("RAS_O17", _parser.Encode(msg));
    }

    private MessageEntry BuildAck()
    {
        var msg = new ACK();
        var cid = NextControlId();
        FillMsh(msg.MSH, "ACK", "A01", cid);
        msg.MSA.AcknowledgmentCode.Value = "AA";
        msg.MSA.MessageControlID.Value = "ORIG-001";
        return new MessageEntry("ACK", _parser.Encode(msg));
    }

    private MessageEntry BuildOmgO19()
    {
        var msg = new OMG_O19();
        var cid = NextControlId();
        FillMsh(msg.MSH, "OMG", "O19", cid);
        FillPid(msg.PATIENT.PID, "950001", "Johansson", "Lars", "19730520", "M");
        FillPv1(msg.PATIENT.PATIENT_VISIT.PV1, "I", "RAD-1");
        var orc = msg.GetORDER().ORC;
        orc.OrderControl.Value = "NW";
        orc.PlacerOrderNumber.EntityIdentifier.Value = "RAD-500";
        var obr = msg.GetORDER().OBR;
        obr.SetIDOBR.Value = "1";
        obr.UniversalServiceIdentifier.Identifier.Value = "XR-CHEST";
        obr.UniversalServiceIdentifier.Text.Value = "Chest X-Ray PA and Lateral";
        return new MessageEntry("OMG_O19", _parser.Encode(msg));
    }

    private MessageEntry BuildOmsO05()
    {
        var msg = new OMS_O05();
        var cid = NextControlId();
        FillMsh(msg.MSH, "OMS", "O05", cid);
        FillPid(msg.PATIENT.PID, "950002", "Bergstrom", "Karin", "19810930", "F");
        FillPv1(msg.PATIENT.PATIENT_VISIT.PV1, "I", "SUP-1");
        var orc = msg.GetORDER().ORC;
        orc.OrderControl.Value = "NW";
        orc.PlacerOrderNumber.EntityIdentifier.Value = "SUP-001";
        msg.GetORDER().RQD.RequisitionLineNumber.Value = "1";
        msg.GetORDER().RQD.ItemCodeInternal.Identifier.Value = "GLOVES-M";
        msg.GetORDER().RQD.ItemCodeInternal.Text.Value = "Exam Gloves Medium";
        return new MessageEntry("OMS_O05", _parser.Encode(msg));
    }

    private MessageEntry BuildAdtA01WithObx()
    {
        var msg = new ADT_A01();
        var cid = NextControlId();
        FillMsh(msg.MSH, "ADT", "A01", cid);
        msg.MSH.DateTimeOfMessage.Time.Value = "20250403090000";
        msg.EVN.EventTypeCode.Value = "A01";
        msg.EVN.RecordedDateTime.Time.Value = "20250403090000";
        FillPid(msg.PID, "999001", "Schneider", "Lisa", "19780112", "F");
        FillPv1(msg.PV1, "E", "WELL-1");
        msg.AddNonstandardSegment("OBX");
        var obx = (OBX)msg.GetStructure("OBX");
        obx.SetIDOBX.Value = "1";
        obx.ValueType.Value = "NM";
        obx.ObservationIdentifier.Identifier.Value = "8867-4";
        obx.ObservationIdentifier.Text.Value = "Heart Rate";
        SetVariesSt(obx.GetObservationValue(0), msg, "72");
        obx.Units.Identifier.Value = "bpm";
        obx.ObservationResultStatus.Value = "F";
        return new MessageEntry("ADT_A01_OBX", _parser.Encode(msg));
    }
}
