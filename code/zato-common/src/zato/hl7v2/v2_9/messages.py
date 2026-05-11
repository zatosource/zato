from __future__ import annotations

from zato.hl7v2.base import HL7Message, HL7Segment, HL7SegmentAttr, HL7GroupAttr
from zato.hl7v2.v2_9.segments import (
    ACC,
    AFF,
    AL1,
    APR,
    ARQ,
    ARV,
    CER,
    CON,
    CTD,
    DB1,
    DG1,
    DON,
    DRG,
    DSC,
    DSP,
    EDU,
    EQP,
    EQU,
    ERR,
    EVN,
    GP1,
    GT1,
    IAM,
    INV,
    ISD,
    IVC,
    LAN,
    MFA,
    MFE,
    MFI,
    MRG,
    MSA,
    MSH,
    NK1,
    NPU,
    NTE,
    OBR,
    OBX,
    OH1,
    OH2,
    OH3,
    OH4,
    ORC,
    ORG,
    PD1,
    PDA,
    PID,
    PRA,
    PRT,
    PSG,
    PSL,
    PSS,
    PV1,
    PV2,
    QAK,
    QID,
    QPD,
    RCP,
    RDF,
    REL,
    RF1,
    RFI,
    ROL,
    SCH,
    SCP,
    SFT,
    SLT,
    STF,
    TQ1,
    TXA,
    UAC,
    UB1,
    UB2,
    URD,
    URS,
)
from zato.hl7v2.v2_9.groups import (
    AdtA01Insurance,
    AdtA01NextOfKin,
    AdtA01Observation,
    AdtA01Procedure,
    AdtA02Observation,
    AdtA03Insurance,
    AdtA03NextOfKin,
    AdtA03Observation,
    AdtA03Procedure,
    AdtA05Insurance,
    AdtA05NextOfKin,
    AdtA05Observation,
    AdtA05Procedure,
    AdtA06Insurance,
    AdtA06NextOfKin,
    AdtA06Observation,
    AdtA06Procedure,
    AdtA09Observation,
    AdtA12Observation,
    AdtA15Observation,
    AdtA16Insurance,
    AdtA16NextOfKin,
    AdtA16Observation,
    AdtA16Procedure,
    AdtA17ObservationResult1,
    AdtA17ObservationResult2,
    AdtA21Observation,
    AdtA38Observation,
    AdtA39Patient,
    AdtA43Patient,
    AdtA44Patient,
    AdtA45MergeInfo,
    AdtA60AdverseReactionGroup,
    AdtA60VisitGroup,
    BarP01Visit,
    BarP02Patient,
    BarP05Visit,
    BarP06Patient,
    BarP10Diagnosis,
    BarP10Procedure,
    BarP12Diagnosis,
    BarP12Procedure,
    BpsO29Order,
    BpsO29Patient,
    BrpO30Response,
    BrtO32Response,
    BtsO31Order,
    BtsO31Patient,
    CciI22AppointmentHistory,
    CciI22ClinicalHistory,
    CciI22Goal,
    CciI22Insurance,
    CciI22MedicationHistory,
    CciI22Pathway,
    CciI22PatientVisits,
    CciI22Problem,
    CcmI21AppointmentHistory,
    CcmI21ClinicalHistory,
    CcmI21Goal,
    CcmI21Insurance,
    CcmI21MedicationHistory,
    CcmI21Pathway,
    CcmI21PatientVisits,
    CcmI21Problem,
    CcqI19ProviderContact,
    CcrI16AppointmentHistory,
    CcrI16ClinicalHistory,
    CcrI16ClinicalOrder,
    CcrI16Goal,
    CcrI16Insurance,
    CcrI16MedicationHistory,
    CcrI16Pathway,
    CcrI16Patient,
    CcrI16PatientVisits,
    CcrI16Problem,
    CcrI16ProviderContact,
    CcuI20AppointmentHistory,
    CcuI20ClinicalHistory,
    CcuI20Goal,
    CcuI20Insurance,
    CcuI20MedicationHistory,
    CcuI20Pathway,
    CcuI20Patient,
    CcuI20PatientVisits,
    CcuI20Problem,
    CcuI20ProviderContact,
    CquI19AppointmentHistory,
    CquI19ClinicalHistory,
    CquI19Goal,
    CquI19Insurance,
    CquI19MedicationHistory,
    CquI19Pathway,
    CquI19Patient,
    CquI19PatientVisits,
    CquI19Problem,
    CquI19ProviderContact,
    CrmC01Patient,
    CsuC09Patient,
    DbcO41Donor,
    DbcO42Donor,
    DelO46Donor,
    DeoO45DonationOrder,
    DeoO45Donor,
    DerO44Donor,
    DerO44DonorOrder,
    DftP03CommonOrder,
    DftP03Diagnosis,
    DftP03Financial,
    DftP03Insurance,
    DftP03Visit,
    DftP11CommonOrder,
    DftP11Diagnosis,
    DftP11Financial,
    DftP11Insurance,
    DftP11Visit,
    DprO48Donation,
    DprO48DonationOrder,
    DprO48Donor,
    DrcO47DonationOrder,
    DrcO47Donor,
    DrgO43Donor,
    EacU07Command,
    EanU09Notification,
    EarU08CommandResponse,
    EhcE01InvoiceInformationSubmit,
    EhcE02InvoiceInformationCancel,
    EhcE04ReassessmentRequestInfo,
    EhcE10InvoiceProcessingResultsInfo,
    EhcE12Request,
    EhcE13Request,
    EhcE15AdjustmentPayee,
    EhcE15PaymentRemittanceDetailInfo,
    EhcE15PaymentRemittanceHeaderInfo,
    EhcE20AuthorizationRequest,
    EhcE21AuthorizationRequest,
    EhcE24AuthorizationResponseInfo,
    MdmT01CommonOrder,
    MdmT02CommonOrder,
    MdmT02Observation,
    MfnM02MfStaff,
    MfnM04MfCdm,
    MfnM05MfLocation,
    MfnM06MfClinStudy,
    MfnM07MfClinStudySched,
    MfnM08MfTestNumeric,
    MfnM09MfTestCategorical,
    MfnM10MfTestBatteries,
    MfnM11MfTestCalculated,
    MfnM12MfObsAttributes,
    MfnM15MfInvItem,
    MfnM16MaterialItemRecord,
    MfnM17MfDrg,
    MfnM18MfPayer,
    MfnM19ContractRecord,
    MfnZnnMfSiteDefined,
    NmdN02ClockAndStatsWithNotes,
    OmbO27Order,
    OmbO27Patient,
    OmdO03OrderDiet,
    OmdO03OrderTray,
    OmdO03Patient,
    OmgO19Device,
    OmgO19Order,
    OmgO19Patient,
    OmiO23Device,
    OmiO23Order,
    OmiO23Patient,
    OmlO21Device,
    OmlO21Order,
    OmlO21Patient,
    OmlO33Device,
    OmlO33Patient,
    OmlO33Specimen,
    OmlO35Device,
    OmlO35Patient,
    OmlO35Specimen,
    OmlO39Device,
    OmlO39Order,
    OmlO39Patient,
    OmlO59Order,
    OmlO59Patient,
    OmnO07Order,
    OmnO07Patient,
    OmpO09Order,
    OmpO09Patient,
    OmqO57Order,
    OmqO57Patient,
    OmsO05Order,
    OmsO05Patient,
    OplO37Guarantor,
    OplO37Order,
    OprO38Response,
    OpuR25AccessionDetail,
    OpuR25PatientVisitObservation,
    OraR33Order,
    OrbO28Response,
    OrdO04Response,
    OrgO20Response,
    OriO24Response,
    OrlO22Response,
    OrlO34Response,
    OrlO36Response,
    OrlO40Response,
    OrlO53Response,
    OrlO54Response,
    OrlO55Response,
    OrlO56Response,
    OrmO01Order,
    OrmO01Patient,
    OrnO08Response,
    OrpO10Response,
    OrsO06Response,
    OruR01PatientResult,
    OruR30Device,
    OruR30Observation,
    OruR30PatientObservation,
    OruR30TimingQty,
    OruR30Visit,
    OrxO58Response,
    OsmR26Shipment,
    OsuO51OrderStatus,
    OsuO52OrderStatus,
    OsuO52Patient,
    OulR22Device,
    OulR22Patient,
    OulR22Specimen,
    OulR23Device,
    OulR23Patient,
    OulR23Specimen,
    OulR24Order,
    OulR24Patient,
    PexP07Experience,
    PexP07Visit,
    PglPc6Goal,
    PglPc6PatientVisit,
    PglPc6Provider,
    PmuB07Certificate,
    PpgPcgPathway,
    PpgPcgPatientVisit,
    PpgPcgProvider,
    PppPcbPathway,
    PppPcbPatientVisit,
    PppPcbProvider,
    PprPc1PatientVisit,
    PprPc1Problem,
    PprPc1Provider,
    QbpE03QueryInformation,
    QbpE22Query,
    QbpQ11Qbp,
    QvrQ17Qbp,
    RasO17Order,
    RasO17Patient,
    RcvO59Order,
    RcvO59Patient,
    RdeO11Order,
    RdeO11Patient,
    RdeO49Order,
    RdeO49Patient,
    RdrRdrDefinition,
    RdsO13Order,
    RdsO13Patient,
    RefI12AuthorizationContact2,
    RefI12Insurance,
    RefI12Observation,
    RefI12PatientVisit,
    RefI12Procedure,
    RefI12ProviderContact,
    RgvO15Order,
    RgvO15Patient,
    RpaI08Authorization,
    RpaI08Insurance,
    RpaI08Observation,
    RpaI08Procedure,
    RpaI08Provider,
    RpaI08Visit,
    RpiI01GuarantorInsurance,
    RpiI01Provider,
    RpiI04GuarantorInsurance,
    RpiI04Provider,
    RplI02Provider,
    RprI03Provider,
    RqaI08Authorization,
    RqaI08GuarantorInsurance,
    RqaI08Observation,
    RqaI08Procedure,
    RqaI08Provider,
    RqaI08Visit,
    RqiI01GuarantorInsurance,
    RqiI01Provider,
    RqpI04Provider,
    RraO18Response,
    RrdO14Response,
    RreO12Response,
    RreO50Response,
    RrgO16Response,
    RriI12AuthorizationContact2,
    RriI12Observation,
    RriI12PatientVisit,
    RriI12Procedure,
    RriI12ProviderContact,
    RspE03QueryAckIpr,
    RspE22QueryAck,
    RspK11SegmentPattern,
    RspK21QueryResponse,
    RspK22QueryResponse,
    RspK23QueryResponse,
    RspK25Staff,
    RspK31Response,
    RspK32QueryResponse,
    RspO33Donor,
    RspO34Donation,
    RspO34Donor,
    RspZ82QueryResponse,
    RspZ84RowDefinition,
    RspZ86QueryResponse,
    RspZ88QueryResponse,
    RspZ90QueryResponse,
    RtbK13RowDefinition,
    RtbZ74RowDefinition,
    SdrS31AntiMicrobialDeviceData,
    SdrS32AntiMicrobialDeviceCycleData,
    SiuS12Patient,
    SiuS12Resources,
    SrmS01Patient,
    SrmS01Resources,
    SrrS01Schedule,
    SsrU04SpecimenContainer,
    SsuU03SpecimenContainer,
    TcuU10TestConfiguration,
    VxuV04Insurance,
    VxuV04Order,
    VxuV04PatientVisit,
    VxuV04PersonObservation,
)

anyHL7Segment = HL7Segment

class ACK(HL7Message):
    _structure_id = "ACK"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)

class ADT_A01(HL7Message):
    _structure_id = "ADT_A01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    oh1: OH1 = HL7SegmentAttr(segment_id="OH1", optional=True, repeatable=True)
    oh2: OH2 = HL7SegmentAttr(segment_id="OH2", optional=True, repeatable=True)
    oh3: OH3 = HL7SegmentAttr(segment_id="OH3", optional=True, repeatable=False)
    oh4: OH4 = HL7SegmentAttr(segment_id="OH4", optional=True, repeatable=True)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    next_of_kin: AdtA01NextOfKin = \
        HL7GroupAttr(name="NEXT_OF_KIN", optional=True, repeatable=True)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    observation: AdtA01Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)
    al1: AL1 = HL7SegmentAttr(segment_id="AL1", optional=True, repeatable=True)
    iam: IAM = HL7SegmentAttr(segment_id="IAM", optional=True, repeatable=True)
    dg1: DG1 = HL7SegmentAttr(segment_id="DG1", optional=True, repeatable=True)
    drg: DRG = HL7SegmentAttr(segment_id="DRG", optional=True, repeatable=False)
    procedure: AdtA01Procedure = \
        HL7GroupAttr(name="PROCEDURE", optional=True, repeatable=True)
    gt1: GT1 = HL7SegmentAttr(segment_id="GT1", optional=True, repeatable=True)
    insurance: AdtA01Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    acc: ACC = HL7SegmentAttr(segment_id="ACC", optional=True, repeatable=False)
    ub1: UB1 = HL7SegmentAttr(segment_id="UB1", optional=True, repeatable=False)
    ub2: UB2 = HL7SegmentAttr(segment_id="UB2", optional=True, repeatable=False)
    pda: PDA = HL7SegmentAttr(segment_id="PDA", optional=True, repeatable=False)

class ADT_A02(HL7Message):
    _structure_id = "ADT_A02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    oh1: OH1 = HL7SegmentAttr(segment_id="OH1", optional=True, repeatable=True)
    oh2: OH2 = HL7SegmentAttr(segment_id="OH2", optional=True, repeatable=True)
    oh3: OH3 = HL7SegmentAttr(segment_id="OH3", optional=True, repeatable=False)
    oh4: OH4 = HL7SegmentAttr(segment_id="OH4", optional=True, repeatable=True)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    observation: AdtA02Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)
    pda: PDA = HL7SegmentAttr(segment_id="PDA", optional=True, repeatable=False)

class ADT_A03(HL7Message):
    _structure_id = "ADT_A03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    oh1: OH1 = HL7SegmentAttr(segment_id="OH1", optional=True, repeatable=True)
    oh2: OH2 = HL7SegmentAttr(segment_id="OH2", optional=True, repeatable=True)
    oh3: OH3 = HL7SegmentAttr(segment_id="OH3", optional=True, repeatable=False)
    oh4: OH4 = HL7SegmentAttr(segment_id="OH4", optional=True, repeatable=True)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    next_of_kin: AdtA03NextOfKin = \
        HL7GroupAttr(name="NEXT_OF_KIN", optional=True, repeatable=True)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    al1: AL1 = HL7SegmentAttr(segment_id="AL1", optional=True, repeatable=True)
    iam: IAM = HL7SegmentAttr(segment_id="IAM", optional=True, repeatable=True)
    dg1: DG1 = HL7SegmentAttr(segment_id="DG1", optional=True, repeatable=True)
    drg: DRG = HL7SegmentAttr(segment_id="DRG", optional=True, repeatable=False)
    procedure: AdtA03Procedure = \
        HL7GroupAttr(name="PROCEDURE", optional=True, repeatable=True)
    observation: AdtA03Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)
    gt1: GT1 = HL7SegmentAttr(segment_id="GT1", optional=True, repeatable=True)
    insurance: AdtA03Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    acc: ACC = HL7SegmentAttr(segment_id="ACC", optional=True, repeatable=False)
    pda: PDA = HL7SegmentAttr(segment_id="PDA", optional=True, repeatable=False)

class ADT_A05(HL7Message):
    _structure_id = "ADT_A05"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    oh1: OH1 = HL7SegmentAttr(segment_id="OH1", optional=True, repeatable=True)
    oh2: OH2 = HL7SegmentAttr(segment_id="OH2", optional=True, repeatable=True)
    oh3: OH3 = HL7SegmentAttr(segment_id="OH3", optional=True, repeatable=False)
    oh4: OH4 = HL7SegmentAttr(segment_id="OH4", optional=True, repeatable=True)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    next_of_kin: AdtA05NextOfKin = \
        HL7GroupAttr(name="NEXT_OF_KIN", optional=True, repeatable=True)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    observation: AdtA05Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)
    al1: AL1 = HL7SegmentAttr(segment_id="AL1", optional=True, repeatable=True)
    iam: IAM = HL7SegmentAttr(segment_id="IAM", optional=True, repeatable=True)
    dg1: DG1 = HL7SegmentAttr(segment_id="DG1", optional=True, repeatable=True)
    drg: DRG = HL7SegmentAttr(segment_id="DRG", optional=True, repeatable=False)
    procedure: AdtA05Procedure = \
        HL7GroupAttr(name="PROCEDURE", optional=True, repeatable=True)
    gt1: GT1 = HL7SegmentAttr(segment_id="GT1", optional=True, repeatable=True)
    insurance: AdtA05Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    acc: ACC = HL7SegmentAttr(segment_id="ACC", optional=True, repeatable=False)
    ub1: UB1 = HL7SegmentAttr(segment_id="UB1", optional=True, repeatable=False)
    ub2: UB2 = HL7SegmentAttr(segment_id="UB2", optional=True, repeatable=False)

class ADT_A06(HL7Message):
    _structure_id = "ADT_A06"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    oh1: OH1 = HL7SegmentAttr(segment_id="OH1", optional=True, repeatable=True)
    oh2: OH2 = HL7SegmentAttr(segment_id="OH2", optional=True, repeatable=True)
    oh3: OH3 = HL7SegmentAttr(segment_id="OH3", optional=True, repeatable=False)
    oh4: OH4 = HL7SegmentAttr(segment_id="OH4", optional=True, repeatable=True)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    mrg: MRG = HL7SegmentAttr(segment_id="MRG", optional=True, repeatable=False)
    next_of_kin: AdtA06NextOfKin = \
        HL7GroupAttr(name="NEXT_OF_KIN", optional=True, repeatable=True)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    observation: AdtA06Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)
    al1: AL1 = HL7SegmentAttr(segment_id="AL1", optional=True, repeatable=True)
    iam: IAM = HL7SegmentAttr(segment_id="IAM", optional=True, repeatable=True)
    dg1: DG1 = HL7SegmentAttr(segment_id="DG1", optional=True, repeatable=True)
    drg: DRG = HL7SegmentAttr(segment_id="DRG", optional=True, repeatable=False)
    procedure: AdtA06Procedure = \
        HL7GroupAttr(name="PROCEDURE", optional=True, repeatable=True)
    gt1: GT1 = HL7SegmentAttr(segment_id="GT1", optional=True, repeatable=True)
    insurance: AdtA06Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    acc: ACC = HL7SegmentAttr(segment_id="ACC", optional=True, repeatable=False)
    ub1: UB1 = HL7SegmentAttr(segment_id="UB1", optional=True, repeatable=False)
    ub2: UB2 = HL7SegmentAttr(segment_id="UB2", optional=True, repeatable=False)

class ADT_A09(HL7Message):
    _structure_id = "ADT_A09"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    observation: AdtA09Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)
    dg1: DG1 = HL7SegmentAttr(segment_id="DG1", optional=True, repeatable=True)

class ADT_A12(HL7Message):
    _structure_id = "ADT_A12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    observation: AdtA12Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)
    dg1: DG1 = HL7SegmentAttr(segment_id="DG1", optional=True, repeatable=False)

class ADT_A15(HL7Message):
    _structure_id = "ADT_A15"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=False, repeatable=True)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    observation: AdtA15Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)

class ADT_A16(HL7Message):
    _structure_id = "ADT_A16"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    oh1: OH1 = HL7SegmentAttr(segment_id="OH1", optional=True, repeatable=True)
    oh2: OH2 = HL7SegmentAttr(segment_id="OH2", optional=True, repeatable=True)
    oh3: OH3 = HL7SegmentAttr(segment_id="OH3", optional=True, repeatable=False)
    oh4: OH4 = HL7SegmentAttr(segment_id="OH4", optional=True, repeatable=True)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    next_of_kin: AdtA16NextOfKin = \
        HL7GroupAttr(name="NEXT_OF_KIN", optional=True, repeatable=True)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    observation: AdtA16Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)
    al1: AL1 = HL7SegmentAttr(segment_id="AL1", optional=True, repeatable=True)
    iam: IAM = HL7SegmentAttr(segment_id="IAM", optional=True, repeatable=True)
    dg1: DG1 = HL7SegmentAttr(segment_id="DG1", optional=True, repeatable=True)
    drg: DRG = HL7SegmentAttr(segment_id="DRG", optional=True, repeatable=False)
    procedure: AdtA16Procedure = \
        HL7GroupAttr(name="PROCEDURE", optional=True, repeatable=True)
    gt1: GT1 = HL7SegmentAttr(segment_id="GT1", optional=True, repeatable=True)
    insurance: AdtA16Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    acc: ACC = HL7SegmentAttr(segment_id="ACC", optional=True, repeatable=False)

class ADT_A17(HL7Message):
    _structure_id = "ADT_A17"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    observation_result_1: AdtA17ObservationResult1 = \
        HL7GroupAttr(name="OBSERVATION_RESULT_1", optional=True, repeatable=True)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    observation_result_2: AdtA17ObservationResult2 = \
        HL7GroupAttr(name="OBSERVATION_RESULT_2", optional=True, repeatable=True)

class ADT_A20(HL7Message):
    _structure_id = "ADT_A20"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    npu: NPU = HL7SegmentAttr(segment_id="NPU", optional=False, repeatable=False)

class ADT_A21(HL7Message):
    _structure_id = "ADT_A21"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    observation: AdtA21Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)

class ADT_A24(HL7Message):
    _structure_id = "ADT_A24"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=True, repeatable=False)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=True, repeatable=False)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)

class ADT_A37(HL7Message):
    _structure_id = "ADT_A37"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=True, repeatable=False)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=True, repeatable=False)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)

class ADT_A38(HL7Message):
    _structure_id = "ADT_A38"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    observation: AdtA38Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)
    dg1: DG1 = HL7SegmentAttr(segment_id="DG1", optional=True, repeatable=True)
    drg: DRG = HL7SegmentAttr(segment_id="DRG", optional=True, repeatable=False)

class ADT_A39(HL7Message):
    _structure_id = "ADT_A39"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    patient: AdtA39Patient = \
        HL7GroupAttr(name="PATIENT", optional=False, repeatable=True)

class ADT_A43(HL7Message):
    _structure_id = "ADT_A43"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    patient: AdtA43Patient = \
        HL7GroupAttr(name="PATIENT", optional=False, repeatable=True)

class ADT_A44(HL7Message):
    _structure_id = "ADT_A44"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    patient: AdtA44Patient = \
        HL7GroupAttr(name="PATIENT", optional=False, repeatable=True)

class ADT_A45(HL7Message):
    _structure_id = "ADT_A45"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    merge_info: AdtA45MergeInfo = \
        HL7GroupAttr(name="MERGE_INFO", optional=False, repeatable=True)

class ADT_A50(HL7Message):
    _structure_id = "ADT_A50"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    mrg: MRG = HL7SegmentAttr(segment_id="MRG", optional=False, repeatable=False)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)

class ADT_A52(HL7Message):
    _structure_id = "ADT_A52"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)

class ADT_A54(HL7Message):
    _structure_id = "ADT_A54"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)

class ADT_A60(HL7Message):
    _structure_id = "ADT_A60"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    visit_group: AdtA60VisitGroup = \
        HL7GroupAttr(name="VISIT_GROUP", optional=True, repeatable=False)
    adverse_reaction_group: AdtA60AdverseReactionGroup = \
        HL7GroupAttr(name="ADVERSE_REACTION_GROUP", optional=True, repeatable=True)

class ADT_A61(HL7Message):
    _structure_id = "ADT_A61"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)

class BAR_P01(HL7Message):
    _structure_id = "BAR_P01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    visit: BarP01Visit = \
        HL7GroupAttr(name="VISIT", optional=False, repeatable=True)

class BAR_P02(HL7Message):
    _structure_id = "BAR_P02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    patient: BarP02Patient = \
        HL7GroupAttr(name="PATIENT", optional=False, repeatable=True)

class BAR_P05(HL7Message):
    _structure_id = "BAR_P05"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    visit: BarP05Visit = \
        HL7GroupAttr(name="VISIT", optional=False, repeatable=True)

class BAR_P06(HL7Message):
    _structure_id = "BAR_P06"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    patient: BarP06Patient = \
        HL7GroupAttr(name="PATIENT", optional=False, repeatable=True)

class BAR_P10(HL7Message):
    _structure_id = "BAR_P10"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    diagnosis: BarP10Diagnosis = \
        HL7GroupAttr(name="DIAGNOSIS", optional=True, repeatable=True)
    gp1: GP1 = HL7SegmentAttr(segment_id="GP1", optional=False, repeatable=False)
    procedure: BarP10Procedure = \
        HL7GroupAttr(name="PROCEDURE", optional=True, repeatable=True)

class BAR_P12(HL7Message):
    _structure_id = "BAR_P12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    diagnosis: BarP12Diagnosis = \
        HL7GroupAttr(name="DIAGNOSIS", optional=True, repeatable=True)
    drg: DRG = HL7SegmentAttr(segment_id="DRG", optional=True, repeatable=False)
    procedure: BarP12Procedure = \
        HL7GroupAttr(name="PROCEDURE", optional=True, repeatable=True)
    obx: OBX = HL7SegmentAttr(segment_id="OBX", optional=True, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)

class BPS_O29(HL7Message):
    _structure_id = "BPS_O29"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: BpsO29Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: BpsO29Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class BRP_O30(HL7Message):
    _structure_id = "BRP_O30"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: BrpO30Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class BRT_O32(HL7Message):
    _structure_id = "BRT_O32"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: BrtO32Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class BTS_O31(HL7Message):
    _structure_id = "BTS_O31"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: BtsO31Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: BtsO31Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class CCF_I22(HL7Message):
    _structure_id = "CCF_I22"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)

class CCI_I22(HL7Message):
    _structure_id = "CCI_I22"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    insurance: CciI22Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    appointment_history: CciI22AppointmentHistory = \
        HL7GroupAttr(name="APPOINTMENT_HISTORY", optional=True, repeatable=True)
    clinical_history: CciI22ClinicalHistory = \
        HL7GroupAttr(name="CLINICAL_HISTORY", optional=True, repeatable=True)
    patient_visits: CciI22PatientVisits = \
        HL7GroupAttr(name="PATIENT_VISITS", optional=False, repeatable=True)
    medication_history: CciI22MedicationHistory = \
        HL7GroupAttr(name="MEDICATION_HISTORY", optional=True, repeatable=True)
    problem: CciI22Problem = \
        HL7GroupAttr(name="PROBLEM", optional=True, repeatable=True)
    goal: CciI22Goal = \
        HL7GroupAttr(name="GOAL", optional=True, repeatable=True)
    pathway: CciI22Pathway = \
        HL7GroupAttr(name="PATHWAY", optional=True, repeatable=True)
    rel: REL = HL7SegmentAttr(segment_id="REL", optional=True, repeatable=True)

class CCM_I21(HL7Message):
    _structure_id = "CCM_I21"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    insurance: CcmI21Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    appointment_history: CcmI21AppointmentHistory = \
        HL7GroupAttr(name="APPOINTMENT_HISTORY", optional=True, repeatable=True)
    clinical_history: CcmI21ClinicalHistory = \
        HL7GroupAttr(name="CLINICAL_HISTORY", optional=True, repeatable=True)
    patient_visits: CcmI21PatientVisits = \
        HL7GroupAttr(name="PATIENT_VISITS", optional=False, repeatable=True)
    medication_history: CcmI21MedicationHistory = \
        HL7GroupAttr(name="MEDICATION_HISTORY", optional=True, repeatable=True)
    problem: CcmI21Problem = \
        HL7GroupAttr(name="PROBLEM", optional=True, repeatable=True)
    goal: CcmI21Goal = \
        HL7GroupAttr(name="GOAL", optional=True, repeatable=True)
    pathway: CcmI21Pathway = \
        HL7GroupAttr(name="PATHWAY", optional=True, repeatable=True)
    rel: REL = HL7SegmentAttr(segment_id="REL", optional=True, repeatable=True)

class CCQ_I19(HL7Message):
    _structure_id = "CCQ_I19"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    rf1: RF1 = HL7SegmentAttr(segment_id="RF1", optional=False, repeatable=False)
    provider_contact: CcqI19ProviderContact = \
        HL7GroupAttr(name="PROVIDER_CONTACT", optional=True, repeatable=True)
    rel: REL = HL7SegmentAttr(segment_id="REL", optional=True, repeatable=True)

class CCR_I16(HL7Message):
    _structure_id = "CCR_I16"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    rf1: RF1 = HL7SegmentAttr(segment_id="RF1", optional=False, repeatable=True)
    provider_contact: CcrI16ProviderContact = \
        HL7GroupAttr(name="PROVIDER_CONTACT", optional=False, repeatable=True)
    clinical_order: CcrI16ClinicalOrder = \
        HL7GroupAttr(name="CLINICAL_ORDER", optional=True, repeatable=True)
    patient: CcrI16Patient = \
        HL7GroupAttr(name="PATIENT", optional=False, repeatable=True)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    insurance: CcrI16Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    appointment_history: CcrI16AppointmentHistory = \
        HL7GroupAttr(name="APPOINTMENT_HISTORY", optional=True, repeatable=True)
    clinical_history: CcrI16ClinicalHistory = \
        HL7GroupAttr(name="CLINICAL_HISTORY", optional=True, repeatable=True)
    patient_visits: CcrI16PatientVisits = \
        HL7GroupAttr(name="PATIENT_VISITS", optional=False, repeatable=True)
    medication_history: CcrI16MedicationHistory = \
        HL7GroupAttr(name="MEDICATION_HISTORY", optional=True, repeatable=True)
    problem: CcrI16Problem = \
        HL7GroupAttr(name="PROBLEM", optional=True, repeatable=True)
    goal: CcrI16Goal = \
        HL7GroupAttr(name="GOAL", optional=True, repeatable=True)
    pathway: CcrI16Pathway = \
        HL7GroupAttr(name="PATHWAY", optional=True, repeatable=True)
    rel: REL = HL7SegmentAttr(segment_id="REL", optional=True, repeatable=True)

class CCU_I20(HL7Message):
    _structure_id = "CCU_I20"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    rf1: RF1 = HL7SegmentAttr(segment_id="RF1", optional=False, repeatable=False)
    provider_contact: CcuI20ProviderContact = \
        HL7GroupAttr(name="PROVIDER_CONTACT", optional=True, repeatable=True)
    patient: CcuI20Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=True)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    insurance: CcuI20Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    appointment_history: CcuI20AppointmentHistory = \
        HL7GroupAttr(name="APPOINTMENT_HISTORY", optional=True, repeatable=True)
    clinical_history: CcuI20ClinicalHistory = \
        HL7GroupAttr(name="CLINICAL_HISTORY", optional=True, repeatable=True)
    patient_visits: CcuI20PatientVisits = \
        HL7GroupAttr(name="PATIENT_VISITS", optional=False, repeatable=True)
    medication_history: CcuI20MedicationHistory = \
        HL7GroupAttr(name="MEDICATION_HISTORY", optional=True, repeatable=True)
    problem: CcuI20Problem = \
        HL7GroupAttr(name="PROBLEM", optional=True, repeatable=True)
    goal: CcuI20Goal = \
        HL7GroupAttr(name="GOAL", optional=True, repeatable=True)
    pathway: CcuI20Pathway = \
        HL7GroupAttr(name="PATHWAY", optional=True, repeatable=True)
    rel: REL = HL7SegmentAttr(segment_id="REL", optional=True, repeatable=True)

class CQU_I19(HL7Message):
    _structure_id = "CQU_I19"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    rf1: RF1 = HL7SegmentAttr(segment_id="RF1", optional=False, repeatable=False)
    provider_contact: CquI19ProviderContact = \
        HL7GroupAttr(name="PROVIDER_CONTACT", optional=True, repeatable=True)
    patient: CquI19Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=True)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    insurance: CquI19Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    appointment_history: CquI19AppointmentHistory = \
        HL7GroupAttr(name="APPOINTMENT_HISTORY", optional=True, repeatable=True)
    clinical_history: CquI19ClinicalHistory = \
        HL7GroupAttr(name="CLINICAL_HISTORY", optional=True, repeatable=True)
    patient_visits: CquI19PatientVisits = \
        HL7GroupAttr(name="PATIENT_VISITS", optional=False, repeatable=True)
    medication_history: CquI19MedicationHistory = \
        HL7GroupAttr(name="MEDICATION_HISTORY", optional=True, repeatable=True)
    problem: CquI19Problem = \
        HL7GroupAttr(name="PROBLEM", optional=True, repeatable=True)
    goal: CquI19Goal = \
        HL7GroupAttr(name="GOAL", optional=True, repeatable=True)
    pathway: CquI19Pathway = \
        HL7GroupAttr(name="PATHWAY", optional=True, repeatable=True)
    rel: REL = HL7SegmentAttr(segment_id="REL", optional=True, repeatable=True)

class CRM_C01(HL7Message):
    _structure_id = "CRM_C01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    patient: CrmC01Patient = \
        HL7GroupAttr(name="PATIENT", optional=False, repeatable=True)

class CSU_C09(HL7Message):
    _structure_id = "CSU_C09"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    patient: CsuC09Patient = \
        HL7GroupAttr(name="PATIENT", optional=False, repeatable=True)

class DBC_O41(HL7Message):
    _structure_id = "DBC_O41"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    donor: DbcO41Donor = \
        HL7GroupAttr(name="DONOR", optional=True, repeatable=False)

class DBC_O42(HL7Message):
    _structure_id = "DBC_O42"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    donor: DbcO42Donor = \
        HL7GroupAttr(name="DONOR", optional=True, repeatable=False)

class DEL_O46(HL7Message):
    _structure_id = "DEL_O46"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    donor: DelO46Donor = \
        HL7GroupAttr(name="DONOR", optional=True, repeatable=False)
    don: DON = HL7SegmentAttr(segment_id="DON", optional=False, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)

class DEO_O45(HL7Message):
    _structure_id = "DEO_O45"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    donor: DeoO45Donor = \
        HL7GroupAttr(name="Donor", optional=True, repeatable=False)
    donation_order: DeoO45DonationOrder = \
        HL7GroupAttr(name="DONATION_ORDER", optional=False, repeatable=True)

class DER_O44(HL7Message):
    _structure_id = "DER_O44"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    donor: DerO44Donor = \
        HL7GroupAttr(name="DONOR", optional=True, repeatable=False)
    donor_order: DerO44DonorOrder = \
        HL7GroupAttr(name="DONOR_ORDER", optional=False, repeatable=True)

class DFT_P03(HL7Message):
    _structure_id = "DFT_P03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    visit: DftP03Visit = \
        HL7GroupAttr(name="VISIT", optional=True, repeatable=False)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    common_order: DftP03CommonOrder = \
        HL7GroupAttr(name="COMMON_ORDER", optional=True, repeatable=True)
    financial: DftP03Financial = \
        HL7GroupAttr(name="FINANCIAL", optional=False, repeatable=True)
    diagnosis: DftP03Diagnosis = \
        HL7GroupAttr(name="DIAGNOSIS", optional=True, repeatable=True)
    drg: DRG = HL7SegmentAttr(segment_id="DRG", optional=True, repeatable=False)
    gt1: GT1 = HL7SegmentAttr(segment_id="GT1", optional=True, repeatable=True)
    insurance: DftP03Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    acc: ACC = HL7SegmentAttr(segment_id="ACC", optional=True, repeatable=False)

class DFT_P11(HL7Message):
    _structure_id = "DFT_P11"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)
    visit: DftP11Visit = \
        HL7GroupAttr(name="VISIT", optional=True, repeatable=False)
    db1: DB1 = HL7SegmentAttr(segment_id="DB1", optional=True, repeatable=True)
    common_order: DftP11CommonOrder = \
        HL7GroupAttr(name="COMMON_ORDER", optional=True, repeatable=True)
    diagnosis: DftP11Diagnosis = \
        HL7GroupAttr(name="DIAGNOSIS", optional=True, repeatable=True)
    drg: DRG = HL7SegmentAttr(segment_id="DRG", optional=True, repeatable=False)
    gt1: GT1 = HL7SegmentAttr(segment_id="GT1", optional=True, repeatable=True)
    insurance: DftP11Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    acc: ACC = HL7SegmentAttr(segment_id="ACC", optional=True, repeatable=False)
    financial: DftP11Financial = \
        HL7GroupAttr(name="FINANCIAL", optional=False, repeatable=True)

class DPR_O48(HL7Message):
    _structure_id = "DPR_O48"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    donor: DprO48Donor = \
        HL7GroupAttr(name="DONOR", optional=True, repeatable=False)
    donation_order: DprO48DonationOrder = \
        HL7GroupAttr(name="DONATION_ORDER", optional=False, repeatable=True)
    donation: DprO48Donation = \
        HL7GroupAttr(name="DONATION", optional=True, repeatable=False)

class DRC_O47(HL7Message):
    _structure_id = "DRC_O47"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    donor: DrcO47Donor = \
        HL7GroupAttr(name="DONOR", optional=True, repeatable=False)
    donation_order: DrcO47DonationOrder = \
        HL7GroupAttr(name="DONATION_ORDER", optional=False, repeatable=True)

class DRG_O43(HL7Message):
    _structure_id = "DRG_O43"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    donor: DrgO43Donor = \
        HL7GroupAttr(name="DONOR", optional=True, repeatable=False)

class EAC_U07(HL7Message):
    _structure_id = "EAC_U07"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    command: EacU07Command = \
        HL7GroupAttr(name="COMMAND", optional=False, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=False)

class EAN_U09(HL7Message):
    _structure_id = "EAN_U09"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    notification: EanU09Notification = \
        HL7GroupAttr(name="NOTIFICATION", optional=False, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=False)

class EAR_U08(HL7Message):
    _structure_id = "EAR_U08"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    command_response: EarU08CommandResponse = \
        HL7GroupAttr(name="COMMAND_RESPONSE", optional=False, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=False)

class EHC_E01(HL7Message):
    _structure_id = "EHC_E01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=True)
    invoice_information_submit: EhcE01InvoiceInformationSubmit = \
        HL7GroupAttr(name="INVOICE_INFORMATION_SUBMIT", optional=False, repeatable=False)

class EHC_E02(HL7Message):
    _structure_id = "EHC_E02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=True)
    invoice_information_cancel: EhcE02InvoiceInformationCancel = \
        HL7GroupAttr(name="INVOICE_INFORMATION_CANCEL", optional=False, repeatable=False)

class EHC_E04(HL7Message):
    _structure_id = "EHC_E04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=True)
    reassessment_request_info: EhcE04ReassessmentRequestInfo = \
        HL7GroupAttr(name="REASSESSMENT_REQUEST_INFO", optional=False, repeatable=False)

class EHC_E10(HL7Message):
    _structure_id = "EHC_E10"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    invoice_processing_results_info: EhcE10InvoiceProcessingResultsInfo = \
        HL7GroupAttr(name="INVOICE_PROCESSING_RESULTS_INFO", optional=False, repeatable=True)

class EHC_E12(HL7Message):
    _structure_id = "EHC_E12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=True)
    rfi: RFI = HL7SegmentAttr(segment_id="RFI", optional=False, repeatable=False)
    ctd: CTD = HL7SegmentAttr(segment_id="CTD", optional=True, repeatable=True)
    ivc: IVC = HL7SegmentAttr(segment_id="IVC", optional=False, repeatable=False)
    pss: PSS = HL7SegmentAttr(segment_id="PSS", optional=False, repeatable=False)
    psg: PSG = HL7SegmentAttr(segment_id="PSG", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=True, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    psl: PSL = HL7SegmentAttr(segment_id="PSL", optional=True, repeatable=True)
    request: EhcE12Request = \
        HL7GroupAttr(name="REQUEST", optional=False, repeatable=True)

class EHC_E13(HL7Message):
    _structure_id = "EHC_E13"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    rfi: RFI = HL7SegmentAttr(segment_id="RFI", optional=False, repeatable=False)
    ctd: CTD = HL7SegmentAttr(segment_id="CTD", optional=True, repeatable=True)
    ivc: IVC = HL7SegmentAttr(segment_id="IVC", optional=False, repeatable=False)
    pss: PSS = HL7SegmentAttr(segment_id="PSS", optional=False, repeatable=False)
    psg: PSG = HL7SegmentAttr(segment_id="PSG", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=True, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    psl: PSL = HL7SegmentAttr(segment_id="PSL", optional=True, repeatable=False)
    request: EhcE13Request = \
        HL7GroupAttr(name="REQUEST", optional=False, repeatable=True)

class EHC_E15(HL7Message):
    _structure_id = "EHC_E15"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=True)
    payment_remittance_header_info: EhcE15PaymentRemittanceHeaderInfo = \
        HL7GroupAttr(name="PAYMENT_REMITTANCE_HEADER_INFO", optional=False, repeatable=False)
    payment_remittance_detail_info: EhcE15PaymentRemittanceDetailInfo = \
        HL7GroupAttr(name="PAYMENT_REMITTANCE_DETAIL_INFO", optional=True, repeatable=True)
    adjustment_payee: EhcE15AdjustmentPayee = \
        HL7GroupAttr(name="ADJUSTMENT_PAYEE", optional=True, repeatable=True)

class EHC_E20(HL7Message):
    _structure_id = "EHC_E20"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=True)
    authorization_request: EhcE20AuthorizationRequest = \
        HL7GroupAttr(name="AUTHORIZATION_REQUEST", optional=False, repeatable=False)

class EHC_E21(HL7Message):
    _structure_id = "EHC_E21"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=True)
    authorization_request: EhcE21AuthorizationRequest = \
        HL7GroupAttr(name="AUTHORIZATION_REQUEST", optional=False, repeatable=False)

class EHC_E24(HL7Message):
    _structure_id = "EHC_E24"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    authorization_response_info: EhcE24AuthorizationResponseInfo = \
        HL7GroupAttr(name="AUTHORIZATION_RESPONSE_INFO", optional=False, repeatable=False)

class ESR_U02(HL7Message):
    _structure_id = "ESR_U02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=False)

class ESU_U01(HL7Message):
    _structure_id = "ESU_U01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    isd: ISD = HL7SegmentAttr(segment_id="ISD", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=False)

class INR_U06(HL7Message):
    _structure_id = "INR_U06"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    inv: INV = HL7SegmentAttr(segment_id="INV", optional=False, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=False)

class INR_U14(HL7Message):
    _structure_id = "INR_U14"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    inv: INV = HL7SegmentAttr(segment_id="INV", optional=True, repeatable=True)

class INU_U05(HL7Message):
    _structure_id = "INU_U05"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    inv: INV = HL7SegmentAttr(segment_id="INV", optional=False, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=False)

class LSU_U12(HL7Message):
    _structure_id = "LSU_U12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    eqp: EQP = HL7SegmentAttr(segment_id="EQP", optional=False, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=False)

class MDM_T01(HL7Message):
    _structure_id = "MDM_T01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    common_order: MdmT01CommonOrder = \
        HL7GroupAttr(name="COMMON_ORDER", optional=True, repeatable=True)
    txa: TXA = HL7SegmentAttr(segment_id="TXA", optional=False, repeatable=False)
    con: CON = HL7SegmentAttr(segment_id="CON", optional=True, repeatable=True)

class MDM_T02(HL7Message):
    _structure_id = "MDM_T02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    common_order: MdmT02CommonOrder = \
        HL7GroupAttr(name="COMMON_ORDER", optional=True, repeatable=True)
    txa: TXA = HL7SegmentAttr(segment_id="TXA", optional=False, repeatable=False)
    con: CON = HL7SegmentAttr(segment_id="CON", optional=True, repeatable=True)
    observation: MdmT02Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=False, repeatable=True)

class MFK_M01(HL7Message):
    _structure_id = "MFK_M01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mfa: MFA = HL7SegmentAttr(segment_id="MFA", optional=True, repeatable=True)

class MFN_M02(HL7Message):
    _structure_id = "MFN_M02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_staff: MfnM02MfStaff = \
        HL7GroupAttr(name="MF_STAFF", optional=False, repeatable=True)

class MFN_M04(HL7Message):
    _structure_id = "MFN_M04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    mf_cdm: MfnM04MfCdm = \
        HL7GroupAttr(name="MF_CDM", optional=False, repeatable=True)

class MFN_M05(HL7Message):
    _structure_id = "MFN_M05"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_location: MfnM05MfLocation = \
        HL7GroupAttr(name="MF_LOCATION", optional=False, repeatable=True)

class MFN_M06(HL7Message):
    _structure_id = "MFN_M06"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_clin_study: MfnM06MfClinStudy = \
        HL7GroupAttr(name="MF_CLIN_STUDY", optional=False, repeatable=True)

class MFN_M07(HL7Message):
    _structure_id = "MFN_M07"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_clin_study_sched: MfnM07MfClinStudySched = \
        HL7GroupAttr(name="MF_CLIN_STUDY_SCHED", optional=False, repeatable=True)

class MFN_M08(HL7Message):
    _structure_id = "MFN_M08"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_test_numeric: MfnM08MfTestNumeric = \
        HL7GroupAttr(name="MF_TEST_NUMERIC", optional=False, repeatable=True)

class MFN_M09(HL7Message):
    _structure_id = "MFN_M09"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_test_categorical: MfnM09MfTestCategorical = \
        HL7GroupAttr(name="MF_TEST_CATEGORICAL", optional=False, repeatable=True)

class MFN_M10(HL7Message):
    _structure_id = "MFN_M10"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_test_batteries: MfnM10MfTestBatteries = \
        HL7GroupAttr(name="MF_TEST_BATTERIES", optional=False, repeatable=True)

class MFN_M11(HL7Message):
    _structure_id = "MFN_M11"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_test_calculated: MfnM11MfTestCalculated = \
        HL7GroupAttr(name="MF_TEST_CALCULATED", optional=False, repeatable=True)

class MFN_M12(HL7Message):
    _structure_id = "MFN_M12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_obs_attributes: MfnM12MfObsAttributes = \
        HL7GroupAttr(name="MF_OBS_ATTRIBUTES", optional=False, repeatable=True)

class MFN_M13(HL7Message):
    _structure_id = "MFN_M13"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mfe: MFE = HL7SegmentAttr(segment_id="MFE", optional=False, repeatable=True)

class MFN_M15(HL7Message):
    _structure_id = "MFN_M15"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_inv_item: MfnM15MfInvItem = \
        HL7GroupAttr(name="MF_INV_ITEM", optional=False, repeatable=True)

class MFN_M16(HL7Message):
    _structure_id = "MFN_M16"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    material_item_record: MfnM16MaterialItemRecord = \
        HL7GroupAttr(name="MATERIAL_ITEM_RECORD", optional=False, repeatable=True)

class MFN_M17(HL7Message):
    _structure_id = "MFN_M17"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_drg: MfnM17MfDrg = \
        HL7GroupAttr(name="MF_DRG", optional=False, repeatable=True)

class MFN_M18(HL7Message):
    _structure_id = "MFN_M18"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_payer: MfnM18MfPayer = \
        HL7GroupAttr(name="MF_PAYER", optional=False, repeatable=True)

class MFN_M19(HL7Message):
    _structure_id = "MFN_M19"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    contract_record: MfnM19ContractRecord = \
        HL7GroupAttr(name="CONTRACT_RECORD", optional=False, repeatable=True)

class MFN_Znn(HL7Message):
    _structure_id = "MFN_Znn"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_site_defined: MfnZnnMfSiteDefined = \
        HL7GroupAttr(name="MF_SITE_DEFINED", optional=False, repeatable=True)

class NMD_N02(HL7Message):
    _structure_id = "NMD_N02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    clock_and_stats_with_notes: NmdN02ClockAndStatsWithNotes = \
        HL7GroupAttr(name="CLOCK_AND_STATS_WITH_NOTES", optional=False, repeatable=True)

class OMB_O27(HL7Message):
    _structure_id = "OMB_O27"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OmbO27Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: OmbO27Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class OMD_O03(HL7Message):
    _structure_id = "OMD_O03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OmdO03Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order_diet: OmdO03OrderDiet = \
        HL7GroupAttr(name="ORDER_DIET", optional=False, repeatable=True)
    order_tray: OmdO03OrderTray = \
        HL7GroupAttr(name="ORDER_TRAY", optional=True, repeatable=True)

class OMG_O19(HL7Message):
    _structure_id = "OMG_O19"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OmgO19Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: OmgO19Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)
    device: OmgO19Device = \
        HL7GroupAttr(name="DEVICE", optional=True, repeatable=True)

class OMI_O23(HL7Message):
    _structure_id = "OMI_O23"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OmiO23Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: OmiO23Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)
    device: OmiO23Device = \
        HL7GroupAttr(name="DEVICE", optional=True, repeatable=True)

class OML_O21(HL7Message):
    _structure_id = "OML_O21"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OmlO21Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: OmlO21Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)
    device: OmlO21Device = \
        HL7GroupAttr(name="DEVICE", optional=True, repeatable=True)

class OML_O33(HL7Message):
    _structure_id = "OML_O33"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OmlO33Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    specimen: OmlO33Specimen = \
        HL7GroupAttr(name="SPECIMEN", optional=False, repeatable=True)
    device: OmlO33Device = \
        HL7GroupAttr(name="DEVICE", optional=True, repeatable=True)

class OML_O35(HL7Message):
    _structure_id = "OML_O35"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OmlO35Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    specimen: OmlO35Specimen = \
        HL7GroupAttr(name="SPECIMEN", optional=False, repeatable=True)
    device: OmlO35Device = \
        HL7GroupAttr(name="DEVICE", optional=True, repeatable=True)

class OML_O39(HL7Message):
    _structure_id = "OML_O39"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OmlO39Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: OmlO39Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)
    device: OmlO39Device = \
        HL7GroupAttr(name="DEVICE", optional=True, repeatable=True)

class OML_O59(HL7Message):
    _structure_id = "OML_O59"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OmlO59Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: OmlO59Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class OMN_O07(HL7Message):
    _structure_id = "OMN_O07"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OmnO07Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: OmnO07Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class ORM_O01(HL7Message):
    _structure_id = "ORM_O01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OrmO01Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: OrmO01Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class OMP_O09(HL7Message):
    _structure_id = "OMP_O09"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OmpO09Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: OmpO09Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class OMQ_O57(HL7Message):
    _structure_id = "OMQ_O57"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OmqO57Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: OmqO57Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class OMS_O05(HL7Message):
    _structure_id = "OMS_O05"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OmsO05Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: OmsO05Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class OPL_O37(HL7Message):
    _structure_id = "OPL_O37"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=False, repeatable=True)
    guarantor: OplO37Guarantor = \
        HL7GroupAttr(name="GUARANTOR", optional=True, repeatable=False)
    order: OplO37Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class OPR_O38(HL7Message):
    _structure_id = "OPR_O38"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OprO38Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class OPU_R25(HL7Message):
    _structure_id = "OPU_R25"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=False)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: PV2 = HL7SegmentAttr(segment_id="PV2", optional=True, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    patient_visit_observation: OpuR25PatientVisitObservation = \
        HL7GroupAttr(name="PATIENT_VISIT_OBSERVATION", optional=True, repeatable=True)
    accession_detail: OpuR25AccessionDetail = \
        HL7GroupAttr(name="ACCESSION_DETAIL", optional=False, repeatable=True)

class ORA_R33(HL7Message):
    _structure_id = "ORA_R33"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    order: OraR33Order = \
        HL7GroupAttr(name="ORDER", optional=True, repeatable=False)

class ORA_R41(HL7Message):
    _structure_id = "ORA_R41"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)

class ORB_O28(HL7Message):
    _structure_id = "ORB_O28"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrbO28Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORD_O04(HL7Message):
    _structure_id = "ORD_O04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrdO04Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORG_O20(HL7Message):
    _structure_id = "ORG_O20"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrgO20Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORI_O24(HL7Message):
    _structure_id = "ORI_O24"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OriO24Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORL_O22(HL7Message):
    _structure_id = "ORL_O22"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrlO22Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORL_O34(HL7Message):
    _structure_id = "ORL_O34"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrlO34Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORL_O36(HL7Message):
    _structure_id = "ORL_O36"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrlO36Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORL_O40(HL7Message):
    _structure_id = "ORL_O40"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrlO40Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORL_O53(HL7Message):
    _structure_id = "ORL_O53"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrlO53Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORL_O54(HL7Message):
    _structure_id = "ORL_O54"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrlO54Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORL_O55(HL7Message):
    _structure_id = "ORL_O55"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrlO55Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORL_O56(HL7Message):
    _structure_id = "ORL_O56"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrlO56Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORN_O08(HL7Message):
    _structure_id = "ORN_O08"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrnO08Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORP_O10(HL7Message):
    _structure_id = "ORP_O10"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrpO10Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORS_O06(HL7Message):
    _structure_id = "ORS_O06"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrsO06Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class ORU_R01(HL7Message):
    _structure_id = "ORU_R01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    patient_result: OruR01PatientResult = \
        HL7GroupAttr(name="PATIENT_RESULT", optional=False, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class ORU_R30(HL7Message):
    _structure_id = "ORU_R30"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    oh1: OH1 = HL7SegmentAttr(segment_id="OH1", optional=True, repeatable=True)
    oh2: OH2 = HL7SegmentAttr(segment_id="OH2", optional=True, repeatable=True)
    oh3: OH3 = HL7SegmentAttr(segment_id="OH3", optional=True, repeatable=False)
    oh4: OH4 = HL7SegmentAttr(segment_id="OH4", optional=True, repeatable=True)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    patient_observation: OruR30PatientObservation = \
        HL7GroupAttr(name="PATIENT_OBSERVATION", optional=True, repeatable=True)
    visit: OruR30Visit = \
        HL7GroupAttr(name="VISIT", optional=True, repeatable=False)
    orc: ORC = HL7SegmentAttr(segment_id="ORC", optional=False, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    obr: OBR = HL7SegmentAttr(segment_id="OBR", optional=False, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    timing_qty: OruR30TimingQty = \
        HL7GroupAttr(name="TIMING_QTY", optional=True, repeatable=True)
    observation: OruR30Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=False, repeatable=True)
    device: OruR30Device = \
        HL7GroupAttr(name="DEVICE", optional=True, repeatable=True)

class ORX_O58(HL7Message):
    _structure_id = "ORX_O58"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: OrxO58Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class OSM_R26(HL7Message):
    _structure_id = "OSM_R26"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    shipment: OsmR26Shipment = \
        HL7GroupAttr(name="SHIPMENT", optional=False, repeatable=True)

class OSU_O51(HL7Message):
    _structure_id = "OSU_O51"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=True, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    order_status: OsuO51OrderStatus = \
        HL7GroupAttr(name="ORDER_STATUS", optional=False, repeatable=True)

class OSU_O52(HL7Message):
    _structure_id = "OSU_O52"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: OsuO52Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    order_status: OsuO52OrderStatus = \
        HL7GroupAttr(name="ORDER_STATUS", optional=False, repeatable=True)

class OUL_R22(HL7Message):
    _structure_id = "OUL_R22"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=False)
    patient: OulR22Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    specimen: OulR22Specimen = \
        HL7GroupAttr(name="SPECIMEN", optional=False, repeatable=True)
    device: OulR22Device = \
        HL7GroupAttr(name="DEVICE", optional=True, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class OUL_R23(HL7Message):
    _structure_id = "OUL_R23"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=False)
    patient: OulR23Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    specimen: OulR23Specimen = \
        HL7GroupAttr(name="SPECIMEN", optional=False, repeatable=True)
    device: OulR23Device = \
        HL7GroupAttr(name="DEVICE", optional=True, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class OUL_R24(HL7Message):
    _structure_id = "OUL_R24"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=False)
    patient: OulR24Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    order: OulR24Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class PEX_P07(HL7Message):
    _structure_id = "PEX_P07"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    visit: PexP07Visit = \
        HL7GroupAttr(name="VISIT", optional=True, repeatable=False)
    experience: PexP07Experience = \
        HL7GroupAttr(name="EXPERIENCE", optional=False, repeatable=True)

class PGL_PC6(HL7Message):
    _structure_id = "PGL_PC6"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    provider: PglPc6Provider = \
        HL7GroupAttr(name="PROVIDER", optional=False, repeatable=True)
    patient_visit: PglPc6PatientVisit = \
        HL7GroupAttr(name="PATIENT_VISIT", optional=True, repeatable=False)
    goal: PglPc6Goal = \
        HL7GroupAttr(name="GOAL", optional=False, repeatable=True)

class PMU_B01(HL7Message):
    _structure_id = "PMU_B01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    stf: STF = HL7SegmentAttr(segment_id="STF", optional=False, repeatable=False)
    pra: PRA = HL7SegmentAttr(segment_id="PRA", optional=True, repeatable=True)
    org: ORG = HL7SegmentAttr(segment_id="ORG", optional=True, repeatable=True)
    aff: AFF = HL7SegmentAttr(segment_id="AFF", optional=True, repeatable=True)
    lan: LAN = HL7SegmentAttr(segment_id="LAN", optional=True, repeatable=True)
    edu: EDU = HL7SegmentAttr(segment_id="EDU", optional=True, repeatable=True)
    cer: CER = HL7SegmentAttr(segment_id="CER", optional=True, repeatable=True)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=True)

class PMU_B03(HL7Message):
    _structure_id = "PMU_B03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    stf: STF = HL7SegmentAttr(segment_id="STF", optional=False, repeatable=False)

class PMU_B04(HL7Message):
    _structure_id = "PMU_B04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    stf: STF = HL7SegmentAttr(segment_id="STF", optional=False, repeatable=False)
    pra: PRA = HL7SegmentAttr(segment_id="PRA", optional=True, repeatable=True)
    org: ORG = HL7SegmentAttr(segment_id="ORG", optional=True, repeatable=True)

class PMU_B07(HL7Message):
    _structure_id = "PMU_B07"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    stf: STF = HL7SegmentAttr(segment_id="STF", optional=False, repeatable=False)
    pra: PRA = HL7SegmentAttr(segment_id="PRA", optional=True, repeatable=False)
    certificate: PmuB07Certificate = \
        HL7GroupAttr(name="CERTIFICATE", optional=True, repeatable=True)

class PMU_B08(HL7Message):
    _structure_id = "PMU_B08"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    stf: STF = HL7SegmentAttr(segment_id="STF", optional=False, repeatable=False)
    pra: PRA = HL7SegmentAttr(segment_id="PRA", optional=True, repeatable=False)
    cer: CER = HL7SegmentAttr(segment_id="CER", optional=True, repeatable=True)

class PPG_PCG(HL7Message):
    _structure_id = "PPG_PCG"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    provider: PpgPcgProvider = \
        HL7GroupAttr(name="PROVIDER", optional=False, repeatable=True)
    patient_visit: PpgPcgPatientVisit = \
        HL7GroupAttr(name="PATIENT_VISIT", optional=True, repeatable=False)
    pathway: PpgPcgPathway = \
        HL7GroupAttr(name="PATHWAY", optional=False, repeatable=True)

class PPP_PCB(HL7Message):
    _structure_id = "PPP_PCB"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    provider: PppPcbProvider = \
        HL7GroupAttr(name="PROVIDER", optional=False, repeatable=True)
    patient_visit: PppPcbPatientVisit = \
        HL7GroupAttr(name="PATIENT_VISIT", optional=True, repeatable=False)
    pathway: PppPcbPathway = \
        HL7GroupAttr(name="PATHWAY", optional=False, repeatable=True)

class PPR_PC1(HL7Message):
    _structure_id = "PPR_PC1"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    provider: PprPc1Provider = \
        HL7GroupAttr(name="PROVIDER", optional=False, repeatable=True)
    patient_visit: PprPc1PatientVisit = \
        HL7GroupAttr(name="PATIENT_VISIT", optional=True, repeatable=False)
    problem: PprPc1Problem = \
        HL7GroupAttr(name="PROBLEM", optional=False, repeatable=True)

class QBP_E03(HL7Message):
    _structure_id = "QBP_E03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=True)
    query_information: QbpE03QueryInformation = \
        HL7GroupAttr(name="QUERY_INFORMATION", optional=False, repeatable=False)

class QBP_E22(HL7Message):
    _structure_id = "QBP_E22"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=True)
    query: QbpE22Query = \
        HL7GroupAttr(name="QUERY", optional=False, repeatable=False)

class QBP_O33(HL7Message):
    _structure_id = "QBP_O33"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)

class QBP_O34(HL7Message):
    _structure_id = "QBP_O34"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)

class QBP_Q11(HL7Message):
    _structure_id = "QBP_Q11"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    qbp: QbpQ11Qbp = \
        HL7GroupAttr(name="QBP", optional=True, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class QBP_Q13(HL7Message):
    _structure_id = "QBP_Q13"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=True, repeatable=False)
    rdf: RDF = HL7SegmentAttr(segment_id="RDF", optional=True, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    rdf: RDF = HL7SegmentAttr(segment_id="RDF", optional=True, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class QBP_Q15(HL7Message):
    _structure_id = "QBP_Q15"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    any_hl7_segment: anyHL7Segment = HL7SegmentAttr(segment_id="anyHL7Segment", optional=True, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class QBP_Q21(HL7Message):
    _structure_id = "QBP_Q21"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class QBP_Qnn(HL7Message):
    _structure_id = "QBP_Qnn"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rdf: RDF = HL7SegmentAttr(segment_id="RDF", optional=True, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class QBP_Z73(HL7Message):
    _structure_id = "QBP_Z73"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)

class QCN_J01(HL7Message):
    _structure_id = "QCN_J01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    qid: QID = HL7SegmentAttr(segment_id="QID", optional=False, repeatable=False)

class QSB_Q16(HL7Message):
    _structure_id = "QSB_Q16"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class QVR_Q17(HL7Message):
    _structure_id = "QVR_Q17"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    qbp: QvrQ17Qbp = \
        HL7GroupAttr(name="QBP", optional=True, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RAS_O17(HL7Message):
    _structure_id = "RAS_O17"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: RasO17Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: RasO17Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class RCV_O59(HL7Message):
    _structure_id = "RCV_O59"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: RcvO59Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: RcvO59Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class RDE_O11(HL7Message):
    _structure_id = "RDE_O11"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: RdeO11Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: RdeO11Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class RDE_O49(HL7Message):
    _structure_id = "RDE_O49"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: RdeO49Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: RdeO49Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class RDR_RDR(HL7Message):
    _structure_id = "RDR_RDR"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=False)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    definition: RdrRdrDefinition = \
        HL7GroupAttr(name="DEFINITION", optional=False, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RDS_O13(HL7Message):
    _structure_id = "RDS_O13"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: RdsO13Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: RdsO13Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class RDY_K15(HL7Message):
    _structure_id = "RDY_K15"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    dsp: DSP = HL7SegmentAttr(segment_id="DSP", optional=True, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RDY_Z80(HL7Message):
    _structure_id = "RDY_Z80"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    dsp: DSP = HL7SegmentAttr(segment_id="DSP", optional=True, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class REF_I12(HL7Message):
    _structure_id = "REF_I12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    rf1: RF1 = HL7SegmentAttr(segment_id="RF1", optional=True, repeatable=False)
    authorization_contact2: RefI12AuthorizationContact2 = \
        HL7GroupAttr(name="AUTHORIZATION_CONTACT2", optional=True, repeatable=False)
    provider_contact: RefI12ProviderContact = \
        HL7GroupAttr(name="PROVIDER_CONTACT", optional=False, repeatable=True)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    gt1: GT1 = HL7SegmentAttr(segment_id="GT1", optional=True, repeatable=True)
    insurance: RefI12Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    acc: ACC = HL7SegmentAttr(segment_id="ACC", optional=True, repeatable=False)
    dg1: DG1 = HL7SegmentAttr(segment_id="DG1", optional=True, repeatable=True)
    drg: DRG = HL7SegmentAttr(segment_id="DRG", optional=True, repeatable=True)
    al1: AL1 = HL7SegmentAttr(segment_id="AL1", optional=True, repeatable=True)
    procedure: RefI12Procedure = \
        HL7GroupAttr(name="PROCEDURE", optional=True, repeatable=True)
    observation: RefI12Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)
    patient_visit: RefI12PatientVisit = \
        HL7GroupAttr(name="PATIENT_VISIT", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)

class RGV_O15(HL7Message):
    _structure_id = "RGV_O15"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: RgvO15Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=False)
    order: RgvO15Order = \
        HL7GroupAttr(name="ORDER", optional=False, repeatable=True)

class RPA_I08(HL7Message):
    _structure_id = "RPA_I08"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    rf1: RF1 = HL7SegmentAttr(segment_id="RF1", optional=True, repeatable=False)
    authorization: RpaI08Authorization = \
        HL7GroupAttr(name="AUTHORIZATION", optional=True, repeatable=False)
    provider: RpaI08Provider = \
        HL7GroupAttr(name="PROVIDER", optional=False, repeatable=True)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    gt1: GT1 = HL7SegmentAttr(segment_id="GT1", optional=True, repeatable=True)
    insurance: RpaI08Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    acc: ACC = HL7SegmentAttr(segment_id="ACC", optional=True, repeatable=False)
    dg1: DG1 = HL7SegmentAttr(segment_id="DG1", optional=True, repeatable=True)
    drg: DRG = HL7SegmentAttr(segment_id="DRG", optional=True, repeatable=True)
    al1: AL1 = HL7SegmentAttr(segment_id="AL1", optional=True, repeatable=True)
    procedure: RpaI08Procedure = \
        HL7GroupAttr(name="PROCEDURE", optional=False, repeatable=True)
    observation: RpaI08Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)
    visit: RpaI08Visit = \
        HL7GroupAttr(name="VISIT", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)

class RPI_I01(HL7Message):
    _structure_id = "RPI_I01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    provider: RpiI01Provider = \
        HL7GroupAttr(name="PROVIDER", optional=False, repeatable=True)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    guarantor_insurance: RpiI01GuarantorInsurance = \
        HL7GroupAttr(name="GUARANTOR_INSURANCE", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)

class RPI_I04(HL7Message):
    _structure_id = "RPI_I04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    provider: RpiI04Provider = \
        HL7GroupAttr(name="PROVIDER", optional=False, repeatable=True)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    guarantor_insurance: RpiI04GuarantorInsurance = \
        HL7GroupAttr(name="GUARANTOR_INSURANCE", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)

class RPL_I02(HL7Message):
    _structure_id = "RPL_I02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    provider: RplI02Provider = \
        HL7GroupAttr(name="PROVIDER", optional=False, repeatable=True)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    dsp: DSP = HL7SegmentAttr(segment_id="DSP", optional=True, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RPR_I03(HL7Message):
    _structure_id = "RPR_I03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    provider: RprI03Provider = \
        HL7GroupAttr(name="PROVIDER", optional=False, repeatable=True)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=True, repeatable=True)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)

class RQA_I08(HL7Message):
    _structure_id = "RQA_I08"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    rf1: RF1 = HL7SegmentAttr(segment_id="RF1", optional=True, repeatable=False)
    authorization: RqaI08Authorization = \
        HL7GroupAttr(name="AUTHORIZATION", optional=True, repeatable=False)
    provider: RqaI08Provider = \
        HL7GroupAttr(name="PROVIDER", optional=False, repeatable=True)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    guarantor_insurance: RqaI08GuarantorInsurance = \
        HL7GroupAttr(name="GUARANTOR_INSURANCE", optional=True, repeatable=False)
    acc: ACC = HL7SegmentAttr(segment_id="ACC", optional=True, repeatable=False)
    dg1: DG1 = HL7SegmentAttr(segment_id="DG1", optional=True, repeatable=True)
    drg: DRG = HL7SegmentAttr(segment_id="DRG", optional=True, repeatable=True)
    al1: AL1 = HL7SegmentAttr(segment_id="AL1", optional=True, repeatable=True)
    procedure: RqaI08Procedure = \
        HL7GroupAttr(name="PROCEDURE", optional=True, repeatable=True)
    observation: RqaI08Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)
    visit: RqaI08Visit = \
        HL7GroupAttr(name="VISIT", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)

class RQI_I01(HL7Message):
    _structure_id = "RQI_I01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    provider: RqiI01Provider = \
        HL7GroupAttr(name="PROVIDER", optional=False, repeatable=True)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    guarantor_insurance: RqiI01GuarantorInsurance = \
        HL7GroupAttr(name="GUARANTOR_INSURANCE", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)

class RQP_I04(HL7Message):
    _structure_id = "RQP_I04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    provider: RqpI04Provider = \
        HL7GroupAttr(name="PROVIDER", optional=False, repeatable=True)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    gt1: GT1 = HL7SegmentAttr(segment_id="GT1", optional=True, repeatable=True)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)

class RRA_O18(HL7Message):
    _structure_id = "RRA_O18"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: RraO18Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class RRD_O14(HL7Message):
    _structure_id = "RRD_O14"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: RrdO14Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class RRE_O12(HL7Message):
    _structure_id = "RRE_O12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: RreO12Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class RRE_O50(HL7Message):
    _structure_id = "RRE_O50"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: RreO50Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class RRG_O16(HL7Message):
    _structure_id = "RRG_O16"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    response: RrgO16Response = \
        HL7GroupAttr(name="RESPONSE", optional=True, repeatable=False)

class RRI_I12(HL7Message):
    _structure_id = "RRI_I12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=True, repeatable=False)
    rf1: RF1 = HL7SegmentAttr(segment_id="RF1", optional=True, repeatable=False)
    authorization_contact2: RriI12AuthorizationContact2 = \
        HL7GroupAttr(name="AUTHORIZATION_CONTACT2", optional=True, repeatable=False)
    provider_contact: RriI12ProviderContact = \
        HL7GroupAttr(name="PROVIDER_CONTACT", optional=False, repeatable=True)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    acc: ACC = HL7SegmentAttr(segment_id="ACC", optional=True, repeatable=False)
    dg1: DG1 = HL7SegmentAttr(segment_id="DG1", optional=True, repeatable=True)
    drg: DRG = HL7SegmentAttr(segment_id="DRG", optional=True, repeatable=True)
    al1: AL1 = HL7SegmentAttr(segment_id="AL1", optional=True, repeatable=True)
    procedure: RriI12Procedure = \
        HL7GroupAttr(name="PROCEDURE", optional=True, repeatable=True)
    observation: RriI12Observation = \
        HL7GroupAttr(name="OBSERVATION", optional=True, repeatable=True)
    patient_visit: RriI12PatientVisit = \
        HL7GroupAttr(name="PATIENT_VISIT", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)

class RSP_E03(HL7Message):
    _structure_id = "RSP_E03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    query_ack_ipr: RspE03QueryAckIpr = \
        HL7GroupAttr(name="QUERY_ACK_IPR", optional=False, repeatable=False)

class RSP_E22(HL7Message):
    _structure_id = "RSP_E22"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    query_ack: RspE22QueryAck = \
        HL7GroupAttr(name="QUERY_ACK", optional=False, repeatable=False)

class RSP_K11(HL7Message):
    _structure_id = "RSP_K11"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    segment_pattern: RspK11SegmentPattern = \
        HL7GroupAttr(name="SEGMENT_PATTERN", optional=True, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RSP_K21(HL7Message):
    _structure_id = "RSP_K21"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    query_response: RspK21QueryResponse = \
        HL7GroupAttr(name="QUERY_RESPONSE", optional=True, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RSP_K22(HL7Message):
    _structure_id = "RSP_K22"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    query_response: RspK22QueryResponse = \
        HL7GroupAttr(name="QUERY_RESPONSE", optional=True, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RSP_K23(HL7Message):
    _structure_id = "RSP_K23"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    query_response: RspK23QueryResponse = \
        HL7GroupAttr(name="QUERY_RESPONSE", optional=True, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RSP_K25(HL7Message):
    _structure_id = "RSP_K25"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    staff: RspK25Staff = \
        HL7GroupAttr(name="STAFF", optional=False, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RSP_K31(HL7Message):
    _structure_id = "RSP_K31"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    response: RspK31Response = \
        HL7GroupAttr(name="RESPONSE", optional=False, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RSP_K32(HL7Message):
    _structure_id = "RSP_K32"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    query_response: RspK32QueryResponse = \
        HL7GroupAttr(name="QUERY_RESPONSE", optional=True, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RSP_O33(HL7Message):
    _structure_id = "RSP_O33"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    donor: RspO33Donor = \
        HL7GroupAttr(name="DONOR", optional=True, repeatable=False)

class RSP_O34(HL7Message):
    _structure_id = "RSP_O34"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    donor: RspO34Donor = \
        HL7GroupAttr(name="DONOR", optional=True, repeatable=False)
    donation: RspO34Donation = \
        HL7GroupAttr(name="DONATION", optional=True, repeatable=False)

class RSP_Z82(HL7Message):
    _structure_id = "RSP_Z82"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    query_response: RspZ82QueryResponse = \
        HL7GroupAttr(name="QUERY_RESPONSE", optional=False, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RSP_Z84(HL7Message):
    _structure_id = "RSP_Z84"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    row_definition: RspZ84RowDefinition = \
        HL7GroupAttr(name="ROW_DEFINITION", optional=True, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RSP_Z86(HL7Message):
    _structure_id = "RSP_Z86"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    query_response: RspZ86QueryResponse = \
        HL7GroupAttr(name="QUERY_RESPONSE", optional=False, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RSP_Z88(HL7Message):
    _structure_id = "RSP_Z88"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    query_response: RspZ88QueryResponse = \
        HL7GroupAttr(name="QUERY_RESPONSE", optional=False, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=False, repeatable=False)

class RSP_Z90(HL7Message):
    _structure_id = "RSP_Z90"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    query_response: RspZ90QueryResponse = \
        HL7GroupAttr(name="QUERY_RESPONSE", optional=False, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=False, repeatable=False)

class RSP_Znn(HL7Message):
    _structure_id = "RSP_Znn"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    any_hl7_segment: anyHL7Segment = HL7SegmentAttr(segment_id="anyHL7Segment", optional=True, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RTB_K13(HL7Message):
    _structure_id = "RTB_K13"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    row_definition: RtbK13RowDefinition = \
        HL7GroupAttr(name="ROW_DEFINITION", optional=True, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RTB_Knn(HL7Message):
    _structure_id = "RTB_Knn"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    any_hl7_segment: anyHL7Segment = HL7SegmentAttr(segment_id="anyHL7Segment", optional=False, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class RTB_Z74(HL7Message):
    _structure_id = "RTB_Z74"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    row_definition: RtbZ74RowDefinition = \
        HL7GroupAttr(name="ROW_DEFINITION", optional=True, repeatable=False)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class SDR_S31(HL7Message):
    _structure_id = "SDR_S31"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    anti_microbial_device_data: SdrS31AntiMicrobialDeviceData = \
        HL7GroupAttr(name="ANTI-MICROBIAL_DEVICE_DATA", optional=False, repeatable=False)

class SDR_S32(HL7Message):
    _structure_id = "SDR_S32"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    anti_microbial_device_cycle_data: SdrS32AntiMicrobialDeviceCycleData = \
        HL7GroupAttr(name="ANTI-MICROBIAL_DEVICE_CYCLE_DATA", optional=False, repeatable=False)

class SIU_S12(HL7Message):
    _structure_id = "SIU_S12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sch: SCH = HL7SegmentAttr(segment_id="SCH", optional=False, repeatable=False)
    tq1: TQ1 = HL7SegmentAttr(segment_id="TQ1", optional=True, repeatable=True)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: SiuS12Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=True)
    resources: SiuS12Resources = \
        HL7GroupAttr(name="RESOURCES", optional=False, repeatable=True)

class SLR_S28(HL7Message):
    _structure_id = "SLR_S28"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    slt: SLT = HL7SegmentAttr(segment_id="SLT", optional=False, repeatable=True)

class SRM_S01(HL7Message):
    _structure_id = "SRM_S01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    arq: ARQ = HL7SegmentAttr(segment_id="ARQ", optional=False, repeatable=False)
    apr: APR = HL7SegmentAttr(segment_id="APR", optional=True, repeatable=False)
    nte: NTE = HL7SegmentAttr(segment_id="NTE", optional=True, repeatable=True)
    patient: SrmS01Patient = \
        HL7GroupAttr(name="PATIENT", optional=True, repeatable=True)
    resources: SrmS01Resources = \
        HL7GroupAttr(name="RESOURCES", optional=False, repeatable=True)

class SRR_S01(HL7Message):
    _structure_id = "SRR_S01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: ERR = HL7SegmentAttr(segment_id="ERR", optional=True, repeatable=True)
    schedule: SrrS01Schedule = \
        HL7GroupAttr(name="SCHEDULE", optional=True, repeatable=False)

class SSR_U04(HL7Message):
    _structure_id = "SSR_U04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    specimen_container: SsrU04SpecimenContainer = \
        HL7GroupAttr(name="SPECIMEN_CONTAINER", optional=False, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=False)

class SSU_U03(HL7Message):
    _structure_id = "SSU_U03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    specimen_container: SsuU03SpecimenContainer = \
        HL7GroupAttr(name="SPECIMEN_CONTAINER", optional=False, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=False)

class STC_S33(HL7Message):
    _structure_id = "STC_S33"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    scp: SCP = HL7SegmentAttr(segment_id="SCP", optional=False, repeatable=True)

class TCU_U10(HL7Message):
    _structure_id = "TCU_U10"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    test_configuration: TcuU10TestConfiguration = \
        HL7GroupAttr(name="TEST_CONFIGURATION", optional=False, repeatable=True)
    rol: ROL = HL7SegmentAttr(segment_id="ROL", optional=True, repeatable=False)

class UDM_Q05(HL7Message):
    _structure_id = "UDM_Q05"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    urd: URD = HL7SegmentAttr(segment_id="URD", optional=False, repeatable=False)
    urs: URS = HL7SegmentAttr(segment_id="URS", optional=True, repeatable=False)
    dsp: DSP = HL7SegmentAttr(segment_id="DSP", optional=False, repeatable=True)
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=True, repeatable=False)

class VXU_V04(HL7Message):
    _structure_id = "VXU_V04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    sft: SFT = HL7SegmentAttr(segment_id="SFT", optional=True, repeatable=True)
    uac: UAC = HL7SegmentAttr(segment_id="UAC", optional=True, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: PD1 = HL7SegmentAttr(segment_id="PD1", optional=True, repeatable=False)
    prt: PRT = HL7SegmentAttr(segment_id="PRT", optional=True, repeatable=True)
    nk1: NK1 = HL7SegmentAttr(segment_id="NK1", optional=True, repeatable=True)
    arv: ARV = HL7SegmentAttr(segment_id="ARV", optional=True, repeatable=True)
    patient_visit: VxuV04PatientVisit = \
        HL7GroupAttr(name="PATIENT_VISIT", optional=True, repeatable=False)
    gt1: GT1 = HL7SegmentAttr(segment_id="GT1", optional=True, repeatable=True)
    insurance: VxuV04Insurance = \
        HL7GroupAttr(name="INSURANCE", optional=True, repeatable=True)
    person_observation: VxuV04PersonObservation = \
        HL7GroupAttr(name="PERSON_OBSERVATION", optional=True, repeatable=True)
    order: VxuV04Order = \
        HL7GroupAttr(name="ORDER", optional=True, repeatable=True)

