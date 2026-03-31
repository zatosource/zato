from __future__ import annotations

from typing import Optional

from zato_hl7v2.base import HL7Message, HL7Segment, HL7SegmentAttr, HL7GroupAttr
from zato_hl7v2.v2_9.segments import (
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
from zato_hl7v2.v2_9.groups import (
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


class Ack(HL7Message):
    _structure_id = "ACK"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )


class AdtA01(HL7Message):
    _structure_id = "ADT_A01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    oh1: Optional[list[OH1]] = HL7SegmentAttr(
        segment_id="OH1", optional=True, repeatable=True
    )
    oh2: Optional[list[OH2]] = HL7SegmentAttr(
        segment_id="OH2", optional=True, repeatable=True
    )
    oh3: Optional[OH3] = HL7SegmentAttr(
        segment_id="OH3", optional=True, repeatable=False
    )
    oh4: Optional[list[OH4]] = HL7SegmentAttr(
        segment_id="OH4", optional=True, repeatable=True
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    next_of_kin: Optional[list[AdtA01NextOfKin]] = HL7GroupAttr(
        name="NEXT_OF_KIN", optional=True, repeatable=True
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    observation: Optional[list[AdtA01Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )
    al1: Optional[list[AL1]] = HL7SegmentAttr(
        segment_id="AL1", optional=True, repeatable=True
    )
    iam: Optional[list[IAM]] = HL7SegmentAttr(
        segment_id="IAM", optional=True, repeatable=True
    )
    dg1: Optional[list[DG1]] = HL7SegmentAttr(
        segment_id="DG1", optional=True, repeatable=True
    )
    drg: Optional[DRG] = HL7SegmentAttr(
        segment_id="DRG", optional=True, repeatable=False
    )
    procedure: Optional[list[AdtA01Procedure]] = HL7GroupAttr(
        name="PROCEDURE", optional=True, repeatable=True
    )
    gt1: Optional[list[GT1]] = HL7SegmentAttr(
        segment_id="GT1", optional=True, repeatable=True
    )
    insurance: Optional[list[AdtA01Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    acc: Optional[ACC] = HL7SegmentAttr(
        segment_id="ACC", optional=True, repeatable=False
    )
    ub1: Optional[UB1] = HL7SegmentAttr(
        segment_id="UB1", optional=True, repeatable=False
    )
    ub2: Optional[UB2] = HL7SegmentAttr(
        segment_id="UB2", optional=True, repeatable=False
    )
    pda: Optional[PDA] = HL7SegmentAttr(
        segment_id="PDA", optional=True, repeatable=False
    )


class AdtA02(HL7Message):
    _structure_id = "ADT_A02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    oh1: Optional[list[OH1]] = HL7SegmentAttr(
        segment_id="OH1", optional=True, repeatable=True
    )
    oh2: Optional[list[OH2]] = HL7SegmentAttr(
        segment_id="OH2", optional=True, repeatable=True
    )
    oh3: Optional[OH3] = HL7SegmentAttr(
        segment_id="OH3", optional=True, repeatable=False
    )
    oh4: Optional[list[OH4]] = HL7SegmentAttr(
        segment_id="OH4", optional=True, repeatable=True
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    observation: Optional[list[AdtA02Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )
    pda: Optional[PDA] = HL7SegmentAttr(
        segment_id="PDA", optional=True, repeatable=False
    )


class AdtA03(HL7Message):
    _structure_id = "ADT_A03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    oh1: Optional[list[OH1]] = HL7SegmentAttr(
        segment_id="OH1", optional=True, repeatable=True
    )
    oh2: Optional[list[OH2]] = HL7SegmentAttr(
        segment_id="OH2", optional=True, repeatable=True
    )
    oh3: Optional[OH3] = HL7SegmentAttr(
        segment_id="OH3", optional=True, repeatable=False
    )
    oh4: Optional[list[OH4]] = HL7SegmentAttr(
        segment_id="OH4", optional=True, repeatable=True
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    next_of_kin: Optional[list[AdtA03NextOfKin]] = HL7GroupAttr(
        name="NEXT_OF_KIN", optional=True, repeatable=True
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    al1: Optional[list[AL1]] = HL7SegmentAttr(
        segment_id="AL1", optional=True, repeatable=True
    )
    iam: Optional[list[IAM]] = HL7SegmentAttr(
        segment_id="IAM", optional=True, repeatable=True
    )
    dg1: Optional[list[DG1]] = HL7SegmentAttr(
        segment_id="DG1", optional=True, repeatable=True
    )
    drg: Optional[DRG] = HL7SegmentAttr(
        segment_id="DRG", optional=True, repeatable=False
    )
    procedure: Optional[list[AdtA03Procedure]] = HL7GroupAttr(
        name="PROCEDURE", optional=True, repeatable=True
    )
    observation: Optional[list[AdtA03Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )
    gt1: Optional[list[GT1]] = HL7SegmentAttr(
        segment_id="GT1", optional=True, repeatable=True
    )
    insurance: Optional[list[AdtA03Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    acc: Optional[ACC] = HL7SegmentAttr(
        segment_id="ACC", optional=True, repeatable=False
    )
    pda: Optional[PDA] = HL7SegmentAttr(
        segment_id="PDA", optional=True, repeatable=False
    )


class AdtA05(HL7Message):
    _structure_id = "ADT_A05"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    oh1: Optional[list[OH1]] = HL7SegmentAttr(
        segment_id="OH1", optional=True, repeatable=True
    )
    oh2: Optional[list[OH2]] = HL7SegmentAttr(
        segment_id="OH2", optional=True, repeatable=True
    )
    oh3: Optional[OH3] = HL7SegmentAttr(
        segment_id="OH3", optional=True, repeatable=False
    )
    oh4: Optional[list[OH4]] = HL7SegmentAttr(
        segment_id="OH4", optional=True, repeatable=True
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    next_of_kin: Optional[list[AdtA05NextOfKin]] = HL7GroupAttr(
        name="NEXT_OF_KIN", optional=True, repeatable=True
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    observation: Optional[list[AdtA05Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )
    al1: Optional[list[AL1]] = HL7SegmentAttr(
        segment_id="AL1", optional=True, repeatable=True
    )
    iam: Optional[list[IAM]] = HL7SegmentAttr(
        segment_id="IAM", optional=True, repeatable=True
    )
    dg1: Optional[list[DG1]] = HL7SegmentAttr(
        segment_id="DG1", optional=True, repeatable=True
    )
    drg: Optional[DRG] = HL7SegmentAttr(
        segment_id="DRG", optional=True, repeatable=False
    )
    procedure: Optional[list[AdtA05Procedure]] = HL7GroupAttr(
        name="PROCEDURE", optional=True, repeatable=True
    )
    gt1: Optional[list[GT1]] = HL7SegmentAttr(
        segment_id="GT1", optional=True, repeatable=True
    )
    insurance: Optional[list[AdtA05Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    acc: Optional[ACC] = HL7SegmentAttr(
        segment_id="ACC", optional=True, repeatable=False
    )
    ub1: Optional[UB1] = HL7SegmentAttr(
        segment_id="UB1", optional=True, repeatable=False
    )
    ub2: Optional[UB2] = HL7SegmentAttr(
        segment_id="UB2", optional=True, repeatable=False
    )


class AdtA06(HL7Message):
    _structure_id = "ADT_A06"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    oh1: Optional[list[OH1]] = HL7SegmentAttr(
        segment_id="OH1", optional=True, repeatable=True
    )
    oh2: Optional[list[OH2]] = HL7SegmentAttr(
        segment_id="OH2", optional=True, repeatable=True
    )
    oh3: Optional[OH3] = HL7SegmentAttr(
        segment_id="OH3", optional=True, repeatable=False
    )
    oh4: Optional[list[OH4]] = HL7SegmentAttr(
        segment_id="OH4", optional=True, repeatable=True
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    mrg: Optional[MRG] = HL7SegmentAttr(
        segment_id="MRG", optional=True, repeatable=False
    )
    next_of_kin: Optional[list[AdtA06NextOfKin]] = HL7GroupAttr(
        name="NEXT_OF_KIN", optional=True, repeatable=True
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    observation: Optional[list[AdtA06Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )
    al1: Optional[list[AL1]] = HL7SegmentAttr(
        segment_id="AL1", optional=True, repeatable=True
    )
    iam: Optional[list[IAM]] = HL7SegmentAttr(
        segment_id="IAM", optional=True, repeatable=True
    )
    dg1: Optional[list[DG1]] = HL7SegmentAttr(
        segment_id="DG1", optional=True, repeatable=True
    )
    drg: Optional[DRG] = HL7SegmentAttr(
        segment_id="DRG", optional=True, repeatable=False
    )
    procedure: Optional[list[AdtA06Procedure]] = HL7GroupAttr(
        name="PROCEDURE", optional=True, repeatable=True
    )
    gt1: Optional[list[GT1]] = HL7SegmentAttr(
        segment_id="GT1", optional=True, repeatable=True
    )
    insurance: Optional[list[AdtA06Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    acc: Optional[ACC] = HL7SegmentAttr(
        segment_id="ACC", optional=True, repeatable=False
    )
    ub1: Optional[UB1] = HL7SegmentAttr(
        segment_id="UB1", optional=True, repeatable=False
    )
    ub2: Optional[UB2] = HL7SegmentAttr(
        segment_id="UB2", optional=True, repeatable=False
    )


class AdtA09(HL7Message):
    _structure_id = "ADT_A09"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    observation: Optional[list[AdtA09Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )
    dg1: Optional[list[DG1]] = HL7SegmentAttr(
        segment_id="DG1", optional=True, repeatable=True
    )


class AdtA12(HL7Message):
    _structure_id = "ADT_A12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    observation: Optional[list[AdtA12Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )
    dg1: Optional[DG1] = HL7SegmentAttr(
        segment_id="DG1", optional=True, repeatable=False
    )


class AdtA15(HL7Message):
    _structure_id = "ADT_A15"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: list[PRT] = HL7SegmentAttr(segment_id="PRT", optional=False, repeatable=True)
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    observation: Optional[list[AdtA15Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )


class AdtA16(HL7Message):
    _structure_id = "ADT_A16"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    oh1: Optional[list[OH1]] = HL7SegmentAttr(
        segment_id="OH1", optional=True, repeatable=True
    )
    oh2: Optional[list[OH2]] = HL7SegmentAttr(
        segment_id="OH2", optional=True, repeatable=True
    )
    oh3: Optional[OH3] = HL7SegmentAttr(
        segment_id="OH3", optional=True, repeatable=False
    )
    oh4: Optional[list[OH4]] = HL7SegmentAttr(
        segment_id="OH4", optional=True, repeatable=True
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    next_of_kin: Optional[list[AdtA16NextOfKin]] = HL7GroupAttr(
        name="NEXT_OF_KIN", optional=True, repeatable=True
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    observation: Optional[list[AdtA16Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )
    al1: Optional[list[AL1]] = HL7SegmentAttr(
        segment_id="AL1", optional=True, repeatable=True
    )
    iam: Optional[list[IAM]] = HL7SegmentAttr(
        segment_id="IAM", optional=True, repeatable=True
    )
    dg1: Optional[list[DG1]] = HL7SegmentAttr(
        segment_id="DG1", optional=True, repeatable=True
    )
    drg: Optional[DRG] = HL7SegmentAttr(
        segment_id="DRG", optional=True, repeatable=False
    )
    procedure: Optional[list[AdtA16Procedure]] = HL7GroupAttr(
        name="PROCEDURE", optional=True, repeatable=True
    )
    gt1: Optional[list[GT1]] = HL7SegmentAttr(
        segment_id="GT1", optional=True, repeatable=True
    )
    insurance: Optional[list[AdtA16Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    acc: Optional[ACC] = HL7SegmentAttr(
        segment_id="ACC", optional=True, repeatable=False
    )


class AdtA17(HL7Message):
    _structure_id = "ADT_A17"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    observation_result_1: Optional[list[AdtA17ObservationResult1]] = HL7GroupAttr(
        name="OBSERVATION_RESULT_1", optional=True, repeatable=True
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    observation_result_2: Optional[list[AdtA17ObservationResult2]] = HL7GroupAttr(
        name="OBSERVATION_RESULT_2", optional=True, repeatable=True
    )


class AdtA20(HL7Message):
    _structure_id = "ADT_A20"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    npu: NPU = HL7SegmentAttr(segment_id="NPU", optional=False, repeatable=False)


class AdtA21(HL7Message):
    _structure_id = "ADT_A21"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    observation: Optional[list[AdtA21Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )


class AdtA24(HL7Message):
    _structure_id = "ADT_A24"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    pv1: Optional[PV1] = HL7SegmentAttr(
        segment_id="PV1", optional=True, repeatable=False
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    pv1: Optional[PV1] = HL7SegmentAttr(
        segment_id="PV1", optional=True, repeatable=False
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )


class AdtA37(HL7Message):
    _structure_id = "ADT_A37"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    pv1: Optional[PV1] = HL7SegmentAttr(
        segment_id="PV1", optional=True, repeatable=False
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    pv1: Optional[PV1] = HL7SegmentAttr(
        segment_id="PV1", optional=True, repeatable=False
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )


class AdtA38(HL7Message):
    _structure_id = "ADT_A38"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    observation: Optional[list[AdtA38Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )
    dg1: Optional[list[DG1]] = HL7SegmentAttr(
        segment_id="DG1", optional=True, repeatable=True
    )
    drg: Optional[DRG] = HL7SegmentAttr(
        segment_id="DRG", optional=True, repeatable=False
    )


class AdtA39(HL7Message):
    _structure_id = "ADT_A39"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    patient: list[AdtA39Patient] = HL7GroupAttr(
        name="PATIENT", optional=False, repeatable=True
    )


class AdtA43(HL7Message):
    _structure_id = "ADT_A43"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    patient: list[AdtA43Patient] = HL7GroupAttr(
        name="PATIENT", optional=False, repeatable=True
    )


class AdtA44(HL7Message):
    _structure_id = "ADT_A44"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    patient: list[AdtA44Patient] = HL7GroupAttr(
        name="PATIENT", optional=False, repeatable=True
    )


class AdtA45(HL7Message):
    _structure_id = "ADT_A45"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    merge_info: list[AdtA45MergeInfo] = HL7GroupAttr(
        name="MERGE_INFO", optional=False, repeatable=True
    )


class AdtA50(HL7Message):
    _structure_id = "ADT_A50"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    mrg: MRG = HL7SegmentAttr(segment_id="MRG", optional=False, repeatable=False)
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)


class AdtA52(HL7Message):
    _structure_id = "ADT_A52"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )


class AdtA54(HL7Message):
    _structure_id = "ADT_A54"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )


class AdtA60(HL7Message):
    _structure_id = "ADT_A60"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    visit_group: Optional[AdtA60VisitGroup] = HL7GroupAttr(
        name="VISIT_GROUP", optional=True, repeatable=False
    )
    adverse_reaction_group: Optional[list[AdtA60AdverseReactionGroup]] = HL7GroupAttr(
        name="ADVERSE_REACTION_GROUP", optional=True, repeatable=True
    )


class AdtA61(HL7Message):
    _structure_id = "ADT_A61"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )


class BarP01(HL7Message):
    _structure_id = "BAR_P01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    visit: list[BarP01Visit] = HL7GroupAttr(
        name="VISIT", optional=False, repeatable=True
    )


class BarP02(HL7Message):
    _structure_id = "BAR_P02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    patient: list[BarP02Patient] = HL7GroupAttr(
        name="PATIENT", optional=False, repeatable=True
    )


class BarP05(HL7Message):
    _structure_id = "BAR_P05"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    visit: list[BarP05Visit] = HL7GroupAttr(
        name="VISIT", optional=False, repeatable=True
    )


class BarP06(HL7Message):
    _structure_id = "BAR_P06"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    patient: list[BarP06Patient] = HL7GroupAttr(
        name="PATIENT", optional=False, repeatable=True
    )


class BarP10(HL7Message):
    _structure_id = "BAR_P10"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    diagnosis: Optional[list[BarP10Diagnosis]] = HL7GroupAttr(
        name="DIAGNOSIS", optional=True, repeatable=True
    )
    gp1: GP1 = HL7SegmentAttr(segment_id="GP1", optional=False, repeatable=False)
    procedure: Optional[list[BarP10Procedure]] = HL7GroupAttr(
        name="PROCEDURE", optional=True, repeatable=True
    )


class BarP12(HL7Message):
    _structure_id = "BAR_P12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    diagnosis: Optional[list[BarP12Diagnosis]] = HL7GroupAttr(
        name="DIAGNOSIS", optional=True, repeatable=True
    )
    drg: Optional[DRG] = HL7SegmentAttr(
        segment_id="DRG", optional=True, repeatable=False
    )
    procedure: Optional[list[BarP12Procedure]] = HL7GroupAttr(
        name="PROCEDURE", optional=True, repeatable=True
    )
    obx: Optional[OBX] = HL7SegmentAttr(
        segment_id="OBX", optional=True, repeatable=False
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )


class BpsO29(HL7Message):
    _structure_id = "BPS_O29"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[BpsO29Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[BpsO29Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class BrpO30(HL7Message):
    _structure_id = "BRP_O30"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[BrpO30Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class BrtO32(HL7Message):
    _structure_id = "BRT_O32"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[BrtO32Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class BtsO31(HL7Message):
    _structure_id = "BTS_O31"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[BtsO31Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[BtsO31Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class CcfI22(HL7Message):
    _structure_id = "CCF_I22"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)


class CciI22(HL7Message):
    _structure_id = "CCI_I22"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    insurance: Optional[list[CciI22Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    appointment_history: Optional[list[CciI22AppointmentHistory]] = HL7GroupAttr(
        name="APPOINTMENT_HISTORY", optional=True, repeatable=True
    )
    clinical_history: Optional[list[CciI22ClinicalHistory]] = HL7GroupAttr(
        name="CLINICAL_HISTORY", optional=True, repeatable=True
    )
    patient_visits: list[CciI22PatientVisits] = HL7GroupAttr(
        name="PATIENT_VISITS", optional=False, repeatable=True
    )
    medication_history: Optional[list[CciI22MedicationHistory]] = HL7GroupAttr(
        name="MEDICATION_HISTORY", optional=True, repeatable=True
    )
    problem: Optional[list[CciI22Problem]] = HL7GroupAttr(
        name="PROBLEM", optional=True, repeatable=True
    )
    goal: Optional[list[CciI22Goal]] = HL7GroupAttr(
        name="GOAL", optional=True, repeatable=True
    )
    pathway: Optional[list[CciI22Pathway]] = HL7GroupAttr(
        name="PATHWAY", optional=True, repeatable=True
    )
    rel: Optional[list[REL]] = HL7SegmentAttr(
        segment_id="REL", optional=True, repeatable=True
    )


class CcmI21(HL7Message):
    _structure_id = "CCM_I21"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    insurance: Optional[list[CcmI21Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    appointment_history: Optional[list[CcmI21AppointmentHistory]] = HL7GroupAttr(
        name="APPOINTMENT_HISTORY", optional=True, repeatable=True
    )
    clinical_history: Optional[list[CcmI21ClinicalHistory]] = HL7GroupAttr(
        name="CLINICAL_HISTORY", optional=True, repeatable=True
    )
    patient_visits: list[CcmI21PatientVisits] = HL7GroupAttr(
        name="PATIENT_VISITS", optional=False, repeatable=True
    )
    medication_history: Optional[list[CcmI21MedicationHistory]] = HL7GroupAttr(
        name="MEDICATION_HISTORY", optional=True, repeatable=True
    )
    problem: Optional[list[CcmI21Problem]] = HL7GroupAttr(
        name="PROBLEM", optional=True, repeatable=True
    )
    goal: Optional[list[CcmI21Goal]] = HL7GroupAttr(
        name="GOAL", optional=True, repeatable=True
    )
    pathway: Optional[list[CcmI21Pathway]] = HL7GroupAttr(
        name="PATHWAY", optional=True, repeatable=True
    )
    rel: Optional[list[REL]] = HL7SegmentAttr(
        segment_id="REL", optional=True, repeatable=True
    )


class CcqI19(HL7Message):
    _structure_id = "CCQ_I19"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    rf1: RF1 = HL7SegmentAttr(segment_id="RF1", optional=False, repeatable=False)
    provider_contact: Optional[list[CcqI19ProviderContact]] = HL7GroupAttr(
        name="PROVIDER_CONTACT", optional=True, repeatable=True
    )
    rel: Optional[list[REL]] = HL7SegmentAttr(
        segment_id="REL", optional=True, repeatable=True
    )


class CcrI16(HL7Message):
    _structure_id = "CCR_I16"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    rf1: list[RF1] = HL7SegmentAttr(segment_id="RF1", optional=False, repeatable=True)
    provider_contact: list[CcrI16ProviderContact] = HL7GroupAttr(
        name="PROVIDER_CONTACT", optional=False, repeatable=True
    )
    clinical_order: Optional[list[CcrI16ClinicalOrder]] = HL7GroupAttr(
        name="CLINICAL_ORDER", optional=True, repeatable=True
    )
    patient: list[CcrI16Patient] = HL7GroupAttr(
        name="PATIENT", optional=False, repeatable=True
    )
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    insurance: Optional[list[CcrI16Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    appointment_history: Optional[list[CcrI16AppointmentHistory]] = HL7GroupAttr(
        name="APPOINTMENT_HISTORY", optional=True, repeatable=True
    )
    clinical_history: Optional[list[CcrI16ClinicalHistory]] = HL7GroupAttr(
        name="CLINICAL_HISTORY", optional=True, repeatable=True
    )
    patient_visits: list[CcrI16PatientVisits] = HL7GroupAttr(
        name="PATIENT_VISITS", optional=False, repeatable=True
    )
    medication_history: Optional[list[CcrI16MedicationHistory]] = HL7GroupAttr(
        name="MEDICATION_HISTORY", optional=True, repeatable=True
    )
    problem: Optional[list[CcrI16Problem]] = HL7GroupAttr(
        name="PROBLEM", optional=True, repeatable=True
    )
    goal: Optional[list[CcrI16Goal]] = HL7GroupAttr(
        name="GOAL", optional=True, repeatable=True
    )
    pathway: Optional[list[CcrI16Pathway]] = HL7GroupAttr(
        name="PATHWAY", optional=True, repeatable=True
    )
    rel: Optional[list[REL]] = HL7SegmentAttr(
        segment_id="REL", optional=True, repeatable=True
    )


class CcuI20(HL7Message):
    _structure_id = "CCU_I20"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    rf1: RF1 = HL7SegmentAttr(segment_id="RF1", optional=False, repeatable=False)
    provider_contact: Optional[list[CcuI20ProviderContact]] = HL7GroupAttr(
        name="PROVIDER_CONTACT", optional=True, repeatable=True
    )
    patient: Optional[list[CcuI20Patient]] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=True
    )
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    insurance: Optional[list[CcuI20Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    appointment_history: Optional[list[CcuI20AppointmentHistory]] = HL7GroupAttr(
        name="APPOINTMENT_HISTORY", optional=True, repeatable=True
    )
    clinical_history: Optional[list[CcuI20ClinicalHistory]] = HL7GroupAttr(
        name="CLINICAL_HISTORY", optional=True, repeatable=True
    )
    patient_visits: list[CcuI20PatientVisits] = HL7GroupAttr(
        name="PATIENT_VISITS", optional=False, repeatable=True
    )
    medication_history: Optional[list[CcuI20MedicationHistory]] = HL7GroupAttr(
        name="MEDICATION_HISTORY", optional=True, repeatable=True
    )
    problem: Optional[list[CcuI20Problem]] = HL7GroupAttr(
        name="PROBLEM", optional=True, repeatable=True
    )
    goal: Optional[list[CcuI20Goal]] = HL7GroupAttr(
        name="GOAL", optional=True, repeatable=True
    )
    pathway: Optional[list[CcuI20Pathway]] = HL7GroupAttr(
        name="PATHWAY", optional=True, repeatable=True
    )
    rel: Optional[list[REL]] = HL7SegmentAttr(
        segment_id="REL", optional=True, repeatable=True
    )


class CquI19(HL7Message):
    _structure_id = "CQU_I19"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    rf1: RF1 = HL7SegmentAttr(segment_id="RF1", optional=False, repeatable=False)
    provider_contact: Optional[list[CquI19ProviderContact]] = HL7GroupAttr(
        name="PROVIDER_CONTACT", optional=True, repeatable=True
    )
    patient: Optional[list[CquI19Patient]] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=True
    )
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    insurance: Optional[list[CquI19Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    appointment_history: Optional[list[CquI19AppointmentHistory]] = HL7GroupAttr(
        name="APPOINTMENT_HISTORY", optional=True, repeatable=True
    )
    clinical_history: Optional[list[CquI19ClinicalHistory]] = HL7GroupAttr(
        name="CLINICAL_HISTORY", optional=True, repeatable=True
    )
    patient_visits: list[CquI19PatientVisits] = HL7GroupAttr(
        name="PATIENT_VISITS", optional=False, repeatable=True
    )
    medication_history: Optional[list[CquI19MedicationHistory]] = HL7GroupAttr(
        name="MEDICATION_HISTORY", optional=True, repeatable=True
    )
    problem: Optional[list[CquI19Problem]] = HL7GroupAttr(
        name="PROBLEM", optional=True, repeatable=True
    )
    goal: Optional[list[CquI19Goal]] = HL7GroupAttr(
        name="GOAL", optional=True, repeatable=True
    )
    pathway: Optional[list[CquI19Pathway]] = HL7GroupAttr(
        name="PATHWAY", optional=True, repeatable=True
    )
    rel: Optional[list[REL]] = HL7SegmentAttr(
        segment_id="REL", optional=True, repeatable=True
    )


class CrmC01(HL7Message):
    _structure_id = "CRM_C01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    patient: list[CrmC01Patient] = HL7GroupAttr(
        name="PATIENT", optional=False, repeatable=True
    )


class CsuC09(HL7Message):
    _structure_id = "CSU_C09"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    patient: list[CsuC09Patient] = HL7GroupAttr(
        name="PATIENT", optional=False, repeatable=True
    )


class DbcO41(HL7Message):
    _structure_id = "DBC_O41"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    donor: Optional[DbcO41Donor] = HL7GroupAttr(
        name="DONOR", optional=True, repeatable=False
    )


class DbcO42(HL7Message):
    _structure_id = "DBC_O42"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    donor: Optional[DbcO42Donor] = HL7GroupAttr(
        name="DONOR", optional=True, repeatable=False
    )


class DelO46(HL7Message):
    _structure_id = "DEL_O46"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    donor: Optional[DelO46Donor] = HL7GroupAttr(
        name="DONOR", optional=True, repeatable=False
    )
    don: DON = HL7SegmentAttr(segment_id="DON", optional=False, repeatable=False)
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )


class DeoO45(HL7Message):
    _structure_id = "DEO_O45"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    donor: Optional[DeoO45Donor] = HL7GroupAttr(
        name="Donor", optional=True, repeatable=False
    )
    donation_order: list[DeoO45DonationOrder] = HL7GroupAttr(
        name="DONATION_ORDER", optional=False, repeatable=True
    )


class DerO44(HL7Message):
    _structure_id = "DER_O44"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    donor: Optional[DerO44Donor] = HL7GroupAttr(
        name="DONOR", optional=True, repeatable=False
    )
    donor_order: list[DerO44DonorOrder] = HL7GroupAttr(
        name="DONOR_ORDER", optional=False, repeatable=True
    )


class DftP03(HL7Message):
    _structure_id = "DFT_P03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    visit: Optional[DftP03Visit] = HL7GroupAttr(
        name="VISIT", optional=True, repeatable=False
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    common_order: Optional[list[DftP03CommonOrder]] = HL7GroupAttr(
        name="COMMON_ORDER", optional=True, repeatable=True
    )
    financial: list[DftP03Financial] = HL7GroupAttr(
        name="FINANCIAL", optional=False, repeatable=True
    )
    diagnosis: Optional[list[DftP03Diagnosis]] = HL7GroupAttr(
        name="DIAGNOSIS", optional=True, repeatable=True
    )
    drg: Optional[DRG] = HL7SegmentAttr(
        segment_id="DRG", optional=True, repeatable=False
    )
    gt1: Optional[list[GT1]] = HL7SegmentAttr(
        segment_id="GT1", optional=True, repeatable=True
    )
    insurance: Optional[list[DftP03Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    acc: Optional[ACC] = HL7SegmentAttr(
        segment_id="ACC", optional=True, repeatable=False
    )


class DftP11(HL7Message):
    _structure_id = "DFT_P11"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )
    visit: Optional[DftP11Visit] = HL7GroupAttr(
        name="VISIT", optional=True, repeatable=False
    )
    db1: Optional[list[DB1]] = HL7SegmentAttr(
        segment_id="DB1", optional=True, repeatable=True
    )
    common_order: Optional[list[DftP11CommonOrder]] = HL7GroupAttr(
        name="COMMON_ORDER", optional=True, repeatable=True
    )
    diagnosis: Optional[list[DftP11Diagnosis]] = HL7GroupAttr(
        name="DIAGNOSIS", optional=True, repeatable=True
    )
    drg: Optional[DRG] = HL7SegmentAttr(
        segment_id="DRG", optional=True, repeatable=False
    )
    gt1: Optional[list[GT1]] = HL7SegmentAttr(
        segment_id="GT1", optional=True, repeatable=True
    )
    insurance: Optional[list[DftP11Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    acc: Optional[ACC] = HL7SegmentAttr(
        segment_id="ACC", optional=True, repeatable=False
    )
    financial: list[DftP11Financial] = HL7GroupAttr(
        name="FINANCIAL", optional=False, repeatable=True
    )


class DprO48(HL7Message):
    _structure_id = "DPR_O48"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    donor: Optional[DprO48Donor] = HL7GroupAttr(
        name="DONOR", optional=True, repeatable=False
    )
    donation_order: list[DprO48DonationOrder] = HL7GroupAttr(
        name="DONATION_ORDER", optional=False, repeatable=True
    )
    donation: Optional[DprO48Donation] = HL7GroupAttr(
        name="DONATION", optional=True, repeatable=False
    )


class DrcO47(HL7Message):
    _structure_id = "DRC_O47"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    donor: Optional[DrcO47Donor] = HL7GroupAttr(
        name="DONOR", optional=True, repeatable=False
    )
    donation_order: list[DrcO47DonationOrder] = HL7GroupAttr(
        name="DONATION_ORDER", optional=False, repeatable=True
    )


class DrgO43(HL7Message):
    _structure_id = "DRG_O43"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    donor: Optional[DrgO43Donor] = HL7GroupAttr(
        name="DONOR", optional=True, repeatable=False
    )


class EacU07(HL7Message):
    _structure_id = "EAC_U07"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    command: list[EacU07Command] = HL7GroupAttr(
        name="COMMAND", optional=False, repeatable=True
    )
    rol: Optional[ROL] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=False
    )


class EanU09(HL7Message):
    _structure_id = "EAN_U09"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    notification: list[EanU09Notification] = HL7GroupAttr(
        name="NOTIFICATION", optional=False, repeatable=True
    )
    rol: Optional[ROL] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=False
    )


class EarU08(HL7Message):
    _structure_id = "EAR_U08"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    command_response: list[EarU08CommandResponse] = HL7GroupAttr(
        name="COMMAND_RESPONSE", optional=False, repeatable=True
    )
    rol: Optional[ROL] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=False
    )


class EhcE01(HL7Message):
    _structure_id = "EHC_E01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[list[UAC]] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=True
    )
    invoice_information_submit: EhcE01InvoiceInformationSubmit = HL7GroupAttr(
        name="INVOICE_INFORMATION_SUBMIT", optional=False, repeatable=False
    )


class EhcE02(HL7Message):
    _structure_id = "EHC_E02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[list[UAC]] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=True
    )
    invoice_information_cancel: EhcE02InvoiceInformationCancel = HL7GroupAttr(
        name="INVOICE_INFORMATION_CANCEL", optional=False, repeatable=False
    )


class EhcE04(HL7Message):
    _structure_id = "EHC_E04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[list[UAC]] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=True
    )
    reassessment_request_info: EhcE04ReassessmentRequestInfo = HL7GroupAttr(
        name="REASSESSMENT_REQUEST_INFO", optional=False, repeatable=False
    )


class EhcE10(HL7Message):
    _structure_id = "EHC_E10"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[list[UAC]] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    invoice_processing_results_info: list[EhcE10InvoiceProcessingResultsInfo] = (
        HL7GroupAttr(
            name="INVOICE_PROCESSING_RESULTS_INFO", optional=False, repeatable=True
        )
    )


class EhcE12(HL7Message):
    _structure_id = "EHC_E12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[list[UAC]] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=True
    )
    rfi: RFI = HL7SegmentAttr(segment_id="RFI", optional=False, repeatable=False)
    ctd: Optional[list[CTD]] = HL7SegmentAttr(
        segment_id="CTD", optional=True, repeatable=True
    )
    ivc: IVC = HL7SegmentAttr(segment_id="IVC", optional=False, repeatable=False)
    pss: PSS = HL7SegmentAttr(segment_id="PSS", optional=False, repeatable=False)
    psg: PSG = HL7SegmentAttr(segment_id="PSG", optional=False, repeatable=False)
    pid: Optional[PID] = HL7SegmentAttr(
        segment_id="PID", optional=True, repeatable=False
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    psl: Optional[list[PSL]] = HL7SegmentAttr(
        segment_id="PSL", optional=True, repeatable=True
    )
    request: list[EhcE12Request] = HL7GroupAttr(
        name="REQUEST", optional=False, repeatable=True
    )


class EhcE13(HL7Message):
    _structure_id = "EHC_E13"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[list[UAC]] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    rfi: RFI = HL7SegmentAttr(segment_id="RFI", optional=False, repeatable=False)
    ctd: Optional[list[CTD]] = HL7SegmentAttr(
        segment_id="CTD", optional=True, repeatable=True
    )
    ivc: IVC = HL7SegmentAttr(segment_id="IVC", optional=False, repeatable=False)
    pss: PSS = HL7SegmentAttr(segment_id="PSS", optional=False, repeatable=False)
    psg: PSG = HL7SegmentAttr(segment_id="PSG", optional=False, repeatable=False)
    pid: Optional[PID] = HL7SegmentAttr(
        segment_id="PID", optional=True, repeatable=False
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    psl: Optional[PSL] = HL7SegmentAttr(
        segment_id="PSL", optional=True, repeatable=False
    )
    request: list[EhcE13Request] = HL7GroupAttr(
        name="REQUEST", optional=False, repeatable=True
    )


class EhcE15(HL7Message):
    _structure_id = "EHC_E15"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[list[UAC]] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=True
    )
    payment_remittance_header_info: EhcE15PaymentRemittanceHeaderInfo = HL7GroupAttr(
        name="PAYMENT_REMITTANCE_HEADER_INFO", optional=False, repeatable=False
    )
    payment_remittance_detail_info: Optional[
        list[EhcE15PaymentRemittanceDetailInfo]
    ] = HL7GroupAttr(
        name="PAYMENT_REMITTANCE_DETAIL_INFO", optional=True, repeatable=True
    )
    adjustment_payee: Optional[list[EhcE15AdjustmentPayee]] = HL7GroupAttr(
        name="ADJUSTMENT_PAYEE", optional=True, repeatable=True
    )


class EhcE20(HL7Message):
    _structure_id = "EHC_E20"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[list[UAC]] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=True
    )
    authorization_request: EhcE20AuthorizationRequest = HL7GroupAttr(
        name="AUTHORIZATION_REQUEST", optional=False, repeatable=False
    )


class EhcE21(HL7Message):
    _structure_id = "EHC_E21"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[list[UAC]] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=True
    )
    authorization_request: EhcE21AuthorizationRequest = HL7GroupAttr(
        name="AUTHORIZATION_REQUEST", optional=False, repeatable=False
    )


class EhcE24(HL7Message):
    _structure_id = "EHC_E24"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[list[UAC]] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    authorization_response_info: EhcE24AuthorizationResponseInfo = HL7GroupAttr(
        name="AUTHORIZATION_RESPONSE_INFO", optional=False, repeatable=False
    )


class EsrU02(HL7Message):
    _structure_id = "ESR_U02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    rol: Optional[ROL] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=False
    )


class EsuU01(HL7Message):
    _structure_id = "ESU_U01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    isd: Optional[list[ISD]] = HL7SegmentAttr(
        segment_id="ISD", optional=True, repeatable=True
    )
    rol: Optional[ROL] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=False
    )


class InrU06(HL7Message):
    _structure_id = "INR_U06"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    inv: list[INV] = HL7SegmentAttr(segment_id="INV", optional=False, repeatable=True)
    rol: Optional[ROL] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=False
    )


class InrU14(HL7Message):
    _structure_id = "INR_U14"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    inv: Optional[list[INV]] = HL7SegmentAttr(
        segment_id="INV", optional=True, repeatable=True
    )


class InuU05(HL7Message):
    _structure_id = "INU_U05"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    inv: list[INV] = HL7SegmentAttr(segment_id="INV", optional=False, repeatable=True)
    rol: Optional[ROL] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=False
    )


class LsuU12(HL7Message):
    _structure_id = "LSU_U12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    eqp: list[EQP] = HL7SegmentAttr(segment_id="EQP", optional=False, repeatable=True)
    rol: Optional[ROL] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=False
    )


class MdmT01(HL7Message):
    _structure_id = "MDM_T01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    common_order: Optional[list[MdmT01CommonOrder]] = HL7GroupAttr(
        name="COMMON_ORDER", optional=True, repeatable=True
    )
    txa: TXA = HL7SegmentAttr(segment_id="TXA", optional=False, repeatable=False)
    con: Optional[list[CON]] = HL7SegmentAttr(
        segment_id="CON", optional=True, repeatable=True
    )


class MdmT02(HL7Message):
    _structure_id = "MDM_T02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    common_order: Optional[list[MdmT02CommonOrder]] = HL7GroupAttr(
        name="COMMON_ORDER", optional=True, repeatable=True
    )
    txa: TXA = HL7SegmentAttr(segment_id="TXA", optional=False, repeatable=False)
    con: Optional[list[CON]] = HL7SegmentAttr(
        segment_id="CON", optional=True, repeatable=True
    )
    observation: list[MdmT02Observation] = HL7GroupAttr(
        name="OBSERVATION", optional=False, repeatable=True
    )


class MfkM01(HL7Message):
    _structure_id = "MFK_M01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mfa: Optional[list[MFA]] = HL7SegmentAttr(
        segment_id="MFA", optional=True, repeatable=True
    )


class MfnM02(HL7Message):
    _structure_id = "MFN_M02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_staff: list[MfnM02MfStaff] = HL7GroupAttr(
        name="MF_STAFF", optional=False, repeatable=True
    )


class MfnM04(HL7Message):
    _structure_id = "MFN_M04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    mf_cdm: list[MfnM04MfCdm] = HL7GroupAttr(
        name="MF_CDM", optional=False, repeatable=True
    )


class MfnM05(HL7Message):
    _structure_id = "MFN_M05"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_location: list[MfnM05MfLocation] = HL7GroupAttr(
        name="MF_LOCATION", optional=False, repeatable=True
    )


class MfnM06(HL7Message):
    _structure_id = "MFN_M06"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_clin_study: list[MfnM06MfClinStudy] = HL7GroupAttr(
        name="MF_CLIN_STUDY", optional=False, repeatable=True
    )


class MfnM07(HL7Message):
    _structure_id = "MFN_M07"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_clin_study_sched: list[MfnM07MfClinStudySched] = HL7GroupAttr(
        name="MF_CLIN_STUDY_SCHED", optional=False, repeatable=True
    )


class MfnM08(HL7Message):
    _structure_id = "MFN_M08"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_test_numeric: list[MfnM08MfTestNumeric] = HL7GroupAttr(
        name="MF_TEST_NUMERIC", optional=False, repeatable=True
    )


class MfnM09(HL7Message):
    _structure_id = "MFN_M09"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_test_categorical: list[MfnM09MfTestCategorical] = HL7GroupAttr(
        name="MF_TEST_CATEGORICAL", optional=False, repeatable=True
    )


class MfnM10(HL7Message):
    _structure_id = "MFN_M10"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_test_batteries: list[MfnM10MfTestBatteries] = HL7GroupAttr(
        name="MF_TEST_BATTERIES", optional=False, repeatable=True
    )


class MfnM11(HL7Message):
    _structure_id = "MFN_M11"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_test_calculated: list[MfnM11MfTestCalculated] = HL7GroupAttr(
        name="MF_TEST_CALCULATED", optional=False, repeatable=True
    )


class MfnM12(HL7Message):
    _structure_id = "MFN_M12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_obs_attributes: list[MfnM12MfObsAttributes] = HL7GroupAttr(
        name="MF_OBS_ATTRIBUTES", optional=False, repeatable=True
    )


class MfnM13(HL7Message):
    _structure_id = "MFN_M13"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mfe: list[MFE] = HL7SegmentAttr(segment_id="MFE", optional=False, repeatable=True)


class MfnM15(HL7Message):
    _structure_id = "MFN_M15"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_inv_item: list[MfnM15MfInvItem] = HL7GroupAttr(
        name="MF_INV_ITEM", optional=False, repeatable=True
    )


class MfnM16(HL7Message):
    _structure_id = "MFN_M16"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    material_item_record: list[MfnM16MaterialItemRecord] = HL7GroupAttr(
        name="MATERIAL_ITEM_RECORD", optional=False, repeatable=True
    )


class MfnM17(HL7Message):
    _structure_id = "MFN_M17"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_drg: list[MfnM17MfDrg] = HL7GroupAttr(
        name="MF_DRG", optional=False, repeatable=True
    )


class MfnM18(HL7Message):
    _structure_id = "MFN_M18"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_payer: list[MfnM18MfPayer] = HL7GroupAttr(
        name="MF_PAYER", optional=False, repeatable=True
    )


class MfnM19(HL7Message):
    _structure_id = "MFN_M19"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    contract_record: list[MfnM19ContractRecord] = HL7GroupAttr(
        name="CONTRACT_RECORD", optional=False, repeatable=True
    )


class MfnZnn(HL7Message):
    _structure_id = "MFN_Znn"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    mfi: MFI = HL7SegmentAttr(segment_id="MFI", optional=False, repeatable=False)
    mf_site_defined: list[MfnZnnMfSiteDefined] = HL7GroupAttr(
        name="MF_SITE_DEFINED", optional=False, repeatable=True
    )


class NmdN02(HL7Message):
    _structure_id = "NMD_N02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    clock_and_stats_with_notes: list[NmdN02ClockAndStatsWithNotes] = HL7GroupAttr(
        name="CLOCK_AND_STATS_WITH_NOTES", optional=False, repeatable=True
    )


class OmbO27(HL7Message):
    _structure_id = "OMB_O27"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[OmbO27Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[OmbO27Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class OmdO03(HL7Message):
    _structure_id = "OMD_O03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[OmdO03Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order_diet: list[OmdO03OrderDiet] = HL7GroupAttr(
        name="ORDER_DIET", optional=False, repeatable=True
    )
    order_tray: Optional[list[OmdO03OrderTray]] = HL7GroupAttr(
        name="ORDER_TRAY", optional=True, repeatable=True
    )


class OmgO19(HL7Message):
    _structure_id = "OMG_O19"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[OmgO19Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[OmgO19Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )
    device: Optional[list[OmgO19Device]] = HL7GroupAttr(
        name="DEVICE", optional=True, repeatable=True
    )


class OmiO23(HL7Message):
    _structure_id = "OMI_O23"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[OmiO23Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[OmiO23Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )
    device: Optional[list[OmiO23Device]] = HL7GroupAttr(
        name="DEVICE", optional=True, repeatable=True
    )


class OmlO21(HL7Message):
    _structure_id = "OML_O21"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[OmlO21Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[OmlO21Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )
    device: Optional[list[OmlO21Device]] = HL7GroupAttr(
        name="DEVICE", optional=True, repeatable=True
    )


class OmlO33(HL7Message):
    _structure_id = "OML_O33"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[OmlO33Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    specimen: list[OmlO33Specimen] = HL7GroupAttr(
        name="SPECIMEN", optional=False, repeatable=True
    )
    device: Optional[list[OmlO33Device]] = HL7GroupAttr(
        name="DEVICE", optional=True, repeatable=True
    )


class OmlO35(HL7Message):
    _structure_id = "OML_O35"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[OmlO35Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    specimen: list[OmlO35Specimen] = HL7GroupAttr(
        name="SPECIMEN", optional=False, repeatable=True
    )
    device: Optional[list[OmlO35Device]] = HL7GroupAttr(
        name="DEVICE", optional=True, repeatable=True
    )


class OmlO39(HL7Message):
    _structure_id = "OML_O39"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[OmlO39Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[OmlO39Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )
    device: Optional[list[OmlO39Device]] = HL7GroupAttr(
        name="DEVICE", optional=True, repeatable=True
    )


class OmlO59(HL7Message):
    _structure_id = "OML_O59"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[OmlO59Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[OmlO59Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class OmnO07(HL7Message):
    _structure_id = "OMN_O07"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[OmnO07Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[OmnO07Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class OmpO09(HL7Message):
    _structure_id = "OMP_O09"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[OmpO09Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[OmpO09Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class OmqO57(HL7Message):
    _structure_id = "OMQ_O57"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[OmqO57Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[OmqO57Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class OmsO05(HL7Message):
    _structure_id = "OMS_O05"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[OmsO05Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[OmsO05Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class OplO37(HL7Message):
    _structure_id = "OPL_O37"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    prt: list[PRT] = HL7SegmentAttr(segment_id="PRT", optional=False, repeatable=True)
    guarantor: Optional[OplO37Guarantor] = HL7GroupAttr(
        name="GUARANTOR", optional=True, repeatable=False
    )
    order: list[OplO37Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class OprO38(HL7Message):
    _structure_id = "OPR_O38"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OprO38Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OpuR25(HL7Message):
    _structure_id = "OPU_R25"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[NTE] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=False
    )
    pv1: PV1 = HL7SegmentAttr(segment_id="PV1", optional=False, repeatable=False)
    pv2: Optional[PV2] = HL7SegmentAttr(
        segment_id="PV2", optional=True, repeatable=False
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    patient_visit_observation: Optional[list[OpuR25PatientVisitObservation]] = (
        HL7GroupAttr(name="PATIENT_VISIT_OBSERVATION", optional=True, repeatable=True)
    )
    accession_detail: list[OpuR25AccessionDetail] = HL7GroupAttr(
        name="ACCESSION_DETAIL", optional=False, repeatable=True
    )


class OraR33(HL7Message):
    _structure_id = "ORA_R33"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    order: Optional[OraR33Order] = HL7GroupAttr(
        name="ORDER", optional=True, repeatable=False
    )


class OraR41(HL7Message):
    _structure_id = "ORA_R41"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )


class OrbO28(HL7Message):
    _structure_id = "ORB_O28"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrbO28Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OrdO04(HL7Message):
    _structure_id = "ORD_O04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrdO04Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OrgO20(HL7Message):
    _structure_id = "ORG_O20"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrgO20Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OriO24(HL7Message):
    _structure_id = "ORI_O24"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OriO24Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OrlO22(HL7Message):
    _structure_id = "ORL_O22"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrlO22Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OrlO34(HL7Message):
    _structure_id = "ORL_O34"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrlO34Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OrlO36(HL7Message):
    _structure_id = "ORL_O36"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrlO36Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OrlO40(HL7Message):
    _structure_id = "ORL_O40"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrlO40Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OrlO53(HL7Message):
    _structure_id = "ORL_O53"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrlO53Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OrlO54(HL7Message):
    _structure_id = "ORL_O54"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrlO54Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OrlO55(HL7Message):
    _structure_id = "ORL_O55"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrlO55Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OrlO56(HL7Message):
    _structure_id = "ORL_O56"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrlO56Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OrnO08(HL7Message):
    _structure_id = "ORN_O08"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrnO08Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OrpO10(HL7Message):
    _structure_id = "ORP_O10"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrpO10Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OrsO06(HL7Message):
    _structure_id = "ORS_O06"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrsO06Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OruR01(HL7Message):
    _structure_id = "ORU_R01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    patient_result: list[OruR01PatientResult] = HL7GroupAttr(
        name="PATIENT_RESULT", optional=False, repeatable=True
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class OruR30(HL7Message):
    _structure_id = "ORU_R30"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    oh1: Optional[list[OH1]] = HL7SegmentAttr(
        segment_id="OH1", optional=True, repeatable=True
    )
    oh2: Optional[list[OH2]] = HL7SegmentAttr(
        segment_id="OH2", optional=True, repeatable=True
    )
    oh3: Optional[OH3] = HL7SegmentAttr(
        segment_id="OH3", optional=True, repeatable=False
    )
    oh4: Optional[list[OH4]] = HL7SegmentAttr(
        segment_id="OH4", optional=True, repeatable=True
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    patient_observation: Optional[list[OruR30PatientObservation]] = HL7GroupAttr(
        name="PATIENT_OBSERVATION", optional=True, repeatable=True
    )
    visit: Optional[OruR30Visit] = HL7GroupAttr(
        name="VISIT", optional=True, repeatable=False
    )
    orc: ORC = HL7SegmentAttr(segment_id="ORC", optional=False, repeatable=False)
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    obr: OBR = HL7SegmentAttr(segment_id="OBR", optional=False, repeatable=False)
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    timing_qty: Optional[list[OruR30TimingQty]] = HL7GroupAttr(
        name="TIMING_QTY", optional=True, repeatable=True
    )
    observation: list[OruR30Observation] = HL7GroupAttr(
        name="OBSERVATION", optional=False, repeatable=True
    )
    device: Optional[list[OruR30Device]] = HL7GroupAttr(
        name="DEVICE", optional=True, repeatable=True
    )


class OrxO58(HL7Message):
    _structure_id = "ORX_O58"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[OrxO58Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class OsmR26(HL7Message):
    _structure_id = "OSM_R26"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    shipment: list[OsmR26Shipment] = HL7GroupAttr(
        name="SHIPMENT", optional=False, repeatable=True
    )


class OsuO51(HL7Message):
    _structure_id = "OSU_O51"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    pid: Optional[PID] = HL7SegmentAttr(
        segment_id="PID", optional=True, repeatable=False
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    order_status: list[OsuO51OrderStatus] = HL7GroupAttr(
        name="ORDER_STATUS", optional=False, repeatable=True
    )


class OsuO52(HL7Message):
    _structure_id = "OSU_O52"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[OsuO52Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    order_status: list[OsuO52OrderStatus] = HL7GroupAttr(
        name="ORDER_STATUS", optional=False, repeatable=True
    )


class OulR22(HL7Message):
    _structure_id = "OUL_R22"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[NTE] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=False
    )
    patient: Optional[OulR22Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    specimen: list[OulR22Specimen] = HL7GroupAttr(
        name="SPECIMEN", optional=False, repeatable=True
    )
    device: Optional[list[OulR22Device]] = HL7GroupAttr(
        name="DEVICE", optional=True, repeatable=True
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class OulR23(HL7Message):
    _structure_id = "OUL_R23"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[NTE] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=False
    )
    patient: Optional[OulR23Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    specimen: list[OulR23Specimen] = HL7GroupAttr(
        name="SPECIMEN", optional=False, repeatable=True
    )
    device: Optional[list[OulR23Device]] = HL7GroupAttr(
        name="DEVICE", optional=True, repeatable=True
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class OulR24(HL7Message):
    _structure_id = "OUL_R24"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[NTE] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=False
    )
    patient: Optional[OulR24Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    order: list[OulR24Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class PexP07(HL7Message):
    _structure_id = "PEX_P07"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    visit: Optional[PexP07Visit] = HL7GroupAttr(
        name="VISIT", optional=True, repeatable=False
    )
    experience: list[PexP07Experience] = HL7GroupAttr(
        name="EXPERIENCE", optional=False, repeatable=True
    )


class PglPc6(HL7Message):
    _structure_id = "PGL_PC6"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    provider: list[PglPc6Provider] = HL7GroupAttr(
        name="PROVIDER", optional=False, repeatable=True
    )
    patient_visit: Optional[PglPc6PatientVisit] = HL7GroupAttr(
        name="PATIENT_VISIT", optional=True, repeatable=False
    )
    goal: list[PglPc6Goal] = HL7GroupAttr(name="GOAL", optional=False, repeatable=True)


class PmuB01(HL7Message):
    _structure_id = "PMU_B01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    stf: STF = HL7SegmentAttr(segment_id="STF", optional=False, repeatable=False)
    pra: Optional[list[PRA]] = HL7SegmentAttr(
        segment_id="PRA", optional=True, repeatable=True
    )
    org: Optional[list[ORG]] = HL7SegmentAttr(
        segment_id="ORG", optional=True, repeatable=True
    )
    aff: Optional[list[AFF]] = HL7SegmentAttr(
        segment_id="AFF", optional=True, repeatable=True
    )
    lan: Optional[list[LAN]] = HL7SegmentAttr(
        segment_id="LAN", optional=True, repeatable=True
    )
    edu: Optional[list[EDU]] = HL7SegmentAttr(
        segment_id="EDU", optional=True, repeatable=True
    )
    cer: Optional[list[CER]] = HL7SegmentAttr(
        segment_id="CER", optional=True, repeatable=True
    )
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    rol: Optional[list[ROL]] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=True
    )


class PmuB03(HL7Message):
    _structure_id = "PMU_B03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    stf: STF = HL7SegmentAttr(segment_id="STF", optional=False, repeatable=False)


class PmuB04(HL7Message):
    _structure_id = "PMU_B04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    stf: STF = HL7SegmentAttr(segment_id="STF", optional=False, repeatable=False)
    pra: Optional[list[PRA]] = HL7SegmentAttr(
        segment_id="PRA", optional=True, repeatable=True
    )
    org: Optional[list[ORG]] = HL7SegmentAttr(
        segment_id="ORG", optional=True, repeatable=True
    )


class PmuB07(HL7Message):
    _structure_id = "PMU_B07"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    stf: STF = HL7SegmentAttr(segment_id="STF", optional=False, repeatable=False)
    pra: Optional[PRA] = HL7SegmentAttr(
        segment_id="PRA", optional=True, repeatable=False
    )
    certificate: Optional[list[PmuB07Certificate]] = HL7GroupAttr(
        name="CERTIFICATE", optional=True, repeatable=True
    )


class PmuB08(HL7Message):
    _structure_id = "PMU_B08"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    evn: EVN = HL7SegmentAttr(segment_id="EVN", optional=False, repeatable=False)
    stf: STF = HL7SegmentAttr(segment_id="STF", optional=False, repeatable=False)
    pra: Optional[PRA] = HL7SegmentAttr(
        segment_id="PRA", optional=True, repeatable=False
    )
    cer: Optional[list[CER]] = HL7SegmentAttr(
        segment_id="CER", optional=True, repeatable=True
    )


class PpgPcg(HL7Message):
    _structure_id = "PPG_PCG"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    provider: list[PpgPcgProvider] = HL7GroupAttr(
        name="PROVIDER", optional=False, repeatable=True
    )
    patient_visit: Optional[PpgPcgPatientVisit] = HL7GroupAttr(
        name="PATIENT_VISIT", optional=True, repeatable=False
    )
    pathway: list[PpgPcgPathway] = HL7GroupAttr(
        name="PATHWAY", optional=False, repeatable=True
    )


class PppPcb(HL7Message):
    _structure_id = "PPP_PCB"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    provider: list[PppPcbProvider] = HL7GroupAttr(
        name="PROVIDER", optional=False, repeatable=True
    )
    patient_visit: Optional[PppPcbPatientVisit] = HL7GroupAttr(
        name="PATIENT_VISIT", optional=True, repeatable=False
    )
    pathway: list[PppPcbPathway] = HL7GroupAttr(
        name="PATHWAY", optional=False, repeatable=True
    )


class PprPc1(HL7Message):
    _structure_id = "PPR_PC1"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    provider: list[PprPc1Provider] = HL7GroupAttr(
        name="PROVIDER", optional=False, repeatable=True
    )
    patient_visit: Optional[PprPc1PatientVisit] = HL7GroupAttr(
        name="PATIENT_VISIT", optional=True, repeatable=False
    )
    problem: list[PprPc1Problem] = HL7GroupAttr(
        name="PROBLEM", optional=False, repeatable=True
    )


class QbpE03(HL7Message):
    _structure_id = "QBP_E03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[list[UAC]] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=True
    )
    query_information: QbpE03QueryInformation = HL7GroupAttr(
        name="QUERY_INFORMATION", optional=False, repeatable=False
    )


class QbpE22(HL7Message):
    _structure_id = "QBP_E22"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[list[UAC]] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=True
    )
    query: QbpE22Query = HL7GroupAttr(name="QUERY", optional=False, repeatable=False)


class QbpO33(HL7Message):
    _structure_id = "QBP_O33"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)


class QbpO34(HL7Message):
    _structure_id = "QBP_O34"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)


class QbpQ11(HL7Message):
    _structure_id = "QBP_Q11"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    qbp: Optional[QbpQ11Qbp] = HL7GroupAttr(name="QBP", optional=True, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class QbpQ13(HL7Message):
    _structure_id = "QBP_Q13"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    pid: Optional[PID] = HL7SegmentAttr(
        segment_id="PID", optional=True, repeatable=False
    )
    rdf: Optional[RDF] = HL7SegmentAttr(
        segment_id="RDF", optional=True, repeatable=False
    )
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    rdf: Optional[RDF] = HL7SegmentAttr(
        segment_id="RDF", optional=True, repeatable=False
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class QbpQ15(HL7Message):
    _structure_id = "QBP_Q15"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    any_hl7_segment: Optional[anyHL7Segment] = HL7SegmentAttr(
        segment_id="anyHL7Segment", optional=True, repeatable=False
    )
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class QbpQ21(HL7Message):
    _structure_id = "QBP_Q21"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class QbpQnn(HL7Message):
    _structure_id = "QBP_Qnn"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rdf: Optional[RDF] = HL7SegmentAttr(
        segment_id="RDF", optional=True, repeatable=False
    )
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class QbpZ73(HL7Message):
    _structure_id = "QBP_Z73"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)


class QcnJ01(HL7Message):
    _structure_id = "QCN_J01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    qid: QID = HL7SegmentAttr(segment_id="QID", optional=False, repeatable=False)


class QsbQ16(HL7Message):
    _structure_id = "QSB_Q16"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class QvrQ17(HL7Message):
    _structure_id = "QVR_Q17"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    qbp: Optional[QvrQ17Qbp] = HL7GroupAttr(name="QBP", optional=True, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RasO17(HL7Message):
    _structure_id = "RAS_O17"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[RasO17Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[RasO17Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class RcvO59(HL7Message):
    _structure_id = "RCV_O59"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[RcvO59Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[RcvO59Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class RdeO11(HL7Message):
    _structure_id = "RDE_O11"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[RdeO11Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[RdeO11Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class RdeO49(HL7Message):
    _structure_id = "RDE_O49"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[RdeO49Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[RdeO49Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class RdrRdr(HL7Message):
    _structure_id = "RDR_RDR"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[SFT] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=False
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    definition: list[RdrRdrDefinition] = HL7GroupAttr(
        name="DEFINITION", optional=False, repeatable=True
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RdsO13(HL7Message):
    _structure_id = "RDS_O13"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[RdsO13Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[RdsO13Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class RdyK15(HL7Message):
    _structure_id = "RDY_K15"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    dsp: Optional[list[DSP]] = HL7SegmentAttr(
        segment_id="DSP", optional=True, repeatable=True
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RdyZ80(HL7Message):
    _structure_id = "RDY_Z80"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    dsp: Optional[list[DSP]] = HL7SegmentAttr(
        segment_id="DSP", optional=True, repeatable=True
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RefI12(HL7Message):
    _structure_id = "REF_I12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    rf1: Optional[RF1] = HL7SegmentAttr(
        segment_id="RF1", optional=True, repeatable=False
    )
    authorization_contact2: Optional[RefI12AuthorizationContact2] = HL7GroupAttr(
        name="AUTHORIZATION_CONTACT2", optional=True, repeatable=False
    )
    provider_contact: list[RefI12ProviderContact] = HL7GroupAttr(
        name="PROVIDER_CONTACT", optional=False, repeatable=True
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    gt1: Optional[list[GT1]] = HL7SegmentAttr(
        segment_id="GT1", optional=True, repeatable=True
    )
    insurance: Optional[list[RefI12Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    acc: Optional[ACC] = HL7SegmentAttr(
        segment_id="ACC", optional=True, repeatable=False
    )
    dg1: Optional[list[DG1]] = HL7SegmentAttr(
        segment_id="DG1", optional=True, repeatable=True
    )
    drg: Optional[list[DRG]] = HL7SegmentAttr(
        segment_id="DRG", optional=True, repeatable=True
    )
    al1: Optional[list[AL1]] = HL7SegmentAttr(
        segment_id="AL1", optional=True, repeatable=True
    )
    procedure: Optional[list[RefI12Procedure]] = HL7GroupAttr(
        name="PROCEDURE", optional=True, repeatable=True
    )
    observation: Optional[list[RefI12Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )
    patient_visit: Optional[RefI12PatientVisit] = HL7GroupAttr(
        name="PATIENT_VISIT", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )


class RgvO15(HL7Message):
    _structure_id = "RGV_O15"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[RgvO15Patient] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=False
    )
    order: list[RgvO15Order] = HL7GroupAttr(
        name="ORDER", optional=False, repeatable=True
    )


class RpaI08(HL7Message):
    _structure_id = "RPA_I08"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    rf1: Optional[RF1] = HL7SegmentAttr(
        segment_id="RF1", optional=True, repeatable=False
    )
    authorization: Optional[RpaI08Authorization] = HL7GroupAttr(
        name="AUTHORIZATION", optional=True, repeatable=False
    )
    provider: list[RpaI08Provider] = HL7GroupAttr(
        name="PROVIDER", optional=False, repeatable=True
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    gt1: Optional[list[GT1]] = HL7SegmentAttr(
        segment_id="GT1", optional=True, repeatable=True
    )
    insurance: Optional[list[RpaI08Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    acc: Optional[ACC] = HL7SegmentAttr(
        segment_id="ACC", optional=True, repeatable=False
    )
    dg1: Optional[list[DG1]] = HL7SegmentAttr(
        segment_id="DG1", optional=True, repeatable=True
    )
    drg: Optional[list[DRG]] = HL7SegmentAttr(
        segment_id="DRG", optional=True, repeatable=True
    )
    al1: Optional[list[AL1]] = HL7SegmentAttr(
        segment_id="AL1", optional=True, repeatable=True
    )
    procedure: list[RpaI08Procedure] = HL7GroupAttr(
        name="PROCEDURE", optional=False, repeatable=True
    )
    observation: Optional[list[RpaI08Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )
    visit: Optional[RpaI08Visit] = HL7GroupAttr(
        name="VISIT", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )


class RpiI01(HL7Message):
    _structure_id = "RPI_I01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    provider: list[RpiI01Provider] = HL7GroupAttr(
        name="PROVIDER", optional=False, repeatable=True
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    guarantor_insurance: Optional[RpiI01GuarantorInsurance] = HL7GroupAttr(
        name="GUARANTOR_INSURANCE", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )


class RpiI04(HL7Message):
    _structure_id = "RPI_I04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    provider: list[RpiI04Provider] = HL7GroupAttr(
        name="PROVIDER", optional=False, repeatable=True
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    guarantor_insurance: Optional[RpiI04GuarantorInsurance] = HL7GroupAttr(
        name="GUARANTOR_INSURANCE", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )


class RplI02(HL7Message):
    _structure_id = "RPL_I02"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    provider: list[RplI02Provider] = HL7GroupAttr(
        name="PROVIDER", optional=False, repeatable=True
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    dsp: Optional[list[DSP]] = HL7SegmentAttr(
        segment_id="DSP", optional=True, repeatable=True
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RprI03(HL7Message):
    _structure_id = "RPR_I03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    provider: list[RprI03Provider] = HL7GroupAttr(
        name="PROVIDER", optional=False, repeatable=True
    )
    pid: Optional[list[PID]] = HL7SegmentAttr(
        segment_id="PID", optional=True, repeatable=True
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )


class RqaI08(HL7Message):
    _structure_id = "RQA_I08"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    rf1: Optional[RF1] = HL7SegmentAttr(
        segment_id="RF1", optional=True, repeatable=False
    )
    authorization: Optional[RqaI08Authorization] = HL7GroupAttr(
        name="AUTHORIZATION", optional=True, repeatable=False
    )
    provider: list[RqaI08Provider] = HL7GroupAttr(
        name="PROVIDER", optional=False, repeatable=True
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    guarantor_insurance: Optional[RqaI08GuarantorInsurance] = HL7GroupAttr(
        name="GUARANTOR_INSURANCE", optional=True, repeatable=False
    )
    acc: Optional[ACC] = HL7SegmentAttr(
        segment_id="ACC", optional=True, repeatable=False
    )
    dg1: Optional[list[DG1]] = HL7SegmentAttr(
        segment_id="DG1", optional=True, repeatable=True
    )
    drg: Optional[list[DRG]] = HL7SegmentAttr(
        segment_id="DRG", optional=True, repeatable=True
    )
    al1: Optional[list[AL1]] = HL7SegmentAttr(
        segment_id="AL1", optional=True, repeatable=True
    )
    procedure: Optional[list[RqaI08Procedure]] = HL7GroupAttr(
        name="PROCEDURE", optional=True, repeatable=True
    )
    observation: Optional[list[RqaI08Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )
    visit: Optional[RqaI08Visit] = HL7GroupAttr(
        name="VISIT", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )


class RqiI01(HL7Message):
    _structure_id = "RQI_I01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    provider: list[RqiI01Provider] = HL7GroupAttr(
        name="PROVIDER", optional=False, repeatable=True
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    guarantor_insurance: Optional[RqiI01GuarantorInsurance] = HL7GroupAttr(
        name="GUARANTOR_INSURANCE", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )


class RqpI04(HL7Message):
    _structure_id = "RQP_I04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    provider: list[RqpI04Provider] = HL7GroupAttr(
        name="PROVIDER", optional=False, repeatable=True
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    gt1: Optional[list[GT1]] = HL7SegmentAttr(
        segment_id="GT1", optional=True, repeatable=True
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )


class RraO18(HL7Message):
    _structure_id = "RRA_O18"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[RraO18Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class RrdO14(HL7Message):
    _structure_id = "RRD_O14"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[RrdO14Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class RreO12(HL7Message):
    _structure_id = "RRE_O12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[RreO12Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class RreO50(HL7Message):
    _structure_id = "RRE_O50"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[RreO50Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class RrgO16(HL7Message):
    _structure_id = "RRG_O16"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    response: Optional[RrgO16Response] = HL7GroupAttr(
        name="RESPONSE", optional=True, repeatable=False
    )


class RriI12(HL7Message):
    _structure_id = "RRI_I12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: Optional[MSA] = HL7SegmentAttr(
        segment_id="MSA", optional=True, repeatable=False
    )
    rf1: Optional[RF1] = HL7SegmentAttr(
        segment_id="RF1", optional=True, repeatable=False
    )
    authorization_contact2: Optional[RriI12AuthorizationContact2] = HL7GroupAttr(
        name="AUTHORIZATION_CONTACT2", optional=True, repeatable=False
    )
    provider_contact: list[RriI12ProviderContact] = HL7GroupAttr(
        name="PROVIDER_CONTACT", optional=False, repeatable=True
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    acc: Optional[ACC] = HL7SegmentAttr(
        segment_id="ACC", optional=True, repeatable=False
    )
    dg1: Optional[list[DG1]] = HL7SegmentAttr(
        segment_id="DG1", optional=True, repeatable=True
    )
    drg: Optional[list[DRG]] = HL7SegmentAttr(
        segment_id="DRG", optional=True, repeatable=True
    )
    al1: Optional[list[AL1]] = HL7SegmentAttr(
        segment_id="AL1", optional=True, repeatable=True
    )
    procedure: Optional[list[RriI12Procedure]] = HL7GroupAttr(
        name="PROCEDURE", optional=True, repeatable=True
    )
    observation: Optional[list[RriI12Observation]] = HL7GroupAttr(
        name="OBSERVATION", optional=True, repeatable=True
    )
    patient_visit: Optional[RriI12PatientVisit] = HL7GroupAttr(
        name="PATIENT_VISIT", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )


class RspE03(HL7Message):
    _structure_id = "RSP_E03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[list[UAC]] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    query_ack_ipr: RspE03QueryAckIpr = HL7GroupAttr(
        name="QUERY_ACK_IPR", optional=False, repeatable=False
    )


class RspE22(HL7Message):
    _structure_id = "RSP_E22"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[list[UAC]] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    query_ack: RspE22QueryAck = HL7GroupAttr(
        name="QUERY_ACK", optional=False, repeatable=False
    )


class RspK11(HL7Message):
    _structure_id = "RSP_K11"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    segment_pattern: Optional[RspK11SegmentPattern] = HL7GroupAttr(
        name="SEGMENT_PATTERN", optional=True, repeatable=False
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RspK21(HL7Message):
    _structure_id = "RSP_K21"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    query_response: Optional[RspK21QueryResponse] = HL7GroupAttr(
        name="QUERY_RESPONSE", optional=True, repeatable=False
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RspK22(HL7Message):
    _structure_id = "RSP_K22"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    query_response: Optional[list[RspK22QueryResponse]] = HL7GroupAttr(
        name="QUERY_RESPONSE", optional=True, repeatable=True
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RspK23(HL7Message):
    _structure_id = "RSP_K23"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    query_response: Optional[RspK23QueryResponse] = HL7GroupAttr(
        name="QUERY_RESPONSE", optional=True, repeatable=False
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RspK25(HL7Message):
    _structure_id = "RSP_K25"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    staff: list[RspK25Staff] = HL7GroupAttr(
        name="STAFF", optional=False, repeatable=True
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RspK31(HL7Message):
    _structure_id = "RSP_K31"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    response: list[RspK31Response] = HL7GroupAttr(
        name="RESPONSE", optional=False, repeatable=True
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RspK32(HL7Message):
    _structure_id = "RSP_K32"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    query_response: Optional[list[RspK32QueryResponse]] = HL7GroupAttr(
        name="QUERY_RESPONSE", optional=True, repeatable=True
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RspO33(HL7Message):
    _structure_id = "RSP_O33"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    donor: Optional[RspO33Donor] = HL7GroupAttr(
        name="DONOR", optional=True, repeatable=False
    )


class RspO34(HL7Message):
    _structure_id = "RSP_O34"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    donor: Optional[RspO34Donor] = HL7GroupAttr(
        name="DONOR", optional=True, repeatable=False
    )
    donation: Optional[RspO34Donation] = HL7GroupAttr(
        name="DONATION", optional=True, repeatable=False
    )


class RspZ82(HL7Message):
    _structure_id = "RSP_Z82"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    query_response: list[RspZ82QueryResponse] = HL7GroupAttr(
        name="QUERY_RESPONSE", optional=False, repeatable=True
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RspZ84(HL7Message):
    _structure_id = "RSP_Z84"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    row_definition: Optional[RspZ84RowDefinition] = HL7GroupAttr(
        name="ROW_DEFINITION", optional=True, repeatable=False
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RspZ86(HL7Message):
    _structure_id = "RSP_Z86"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    query_response: list[RspZ86QueryResponse] = HL7GroupAttr(
        name="QUERY_RESPONSE", optional=False, repeatable=True
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RspZ88(HL7Message):
    _structure_id = "RSP_Z88"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    query_response: list[RspZ88QueryResponse] = HL7GroupAttr(
        name="QUERY_RESPONSE", optional=False, repeatable=True
    )
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=False, repeatable=False)


class RspZ90(HL7Message):
    _structure_id = "RSP_Z90"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    rcp: RCP = HL7SegmentAttr(segment_id="RCP", optional=False, repeatable=False)
    query_response: list[RspZ90QueryResponse] = HL7GroupAttr(
        name="QUERY_RESPONSE", optional=False, repeatable=True
    )
    dsc: DSC = HL7SegmentAttr(segment_id="DSC", optional=False, repeatable=False)


class RspZnn(HL7Message):
    _structure_id = "RSP_Znn"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    any_hl7_segment: Optional[anyHL7Segment] = HL7SegmentAttr(
        segment_id="anyHL7Segment", optional=True, repeatable=False
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RtbK13(HL7Message):
    _structure_id = "RTB_K13"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    row_definition: Optional[RtbK13RowDefinition] = HL7GroupAttr(
        name="ROW_DEFINITION", optional=True, repeatable=False
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RtbKnn(HL7Message):
    _structure_id = "RTB_Knn"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[ERR] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    any_hl7_segment: anyHL7Segment = HL7SegmentAttr(
        segment_id="anyHL7Segment", optional=False, repeatable=False
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class RtbZ74(HL7Message):
    _structure_id = "RTB_Z74"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    qak: QAK = HL7SegmentAttr(segment_id="QAK", optional=False, repeatable=False)
    qpd: QPD = HL7SegmentAttr(segment_id="QPD", optional=False, repeatable=False)
    row_definition: Optional[RtbZ74RowDefinition] = HL7GroupAttr(
        name="ROW_DEFINITION", optional=True, repeatable=False
    )
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class SdrS31(HL7Message):
    _structure_id = "SDR_S31"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    anti_microbial_device_data: SdrS31AntiMicrobialDeviceData = HL7GroupAttr(
        name="ANTI-MICROBIAL_DEVICE_DATA", optional=False, repeatable=False
    )


class SdrS32(HL7Message):
    _structure_id = "SDR_S32"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    anti_microbial_device_cycle_data: SdrS32AntiMicrobialDeviceCycleData = HL7GroupAttr(
        name="ANTI-MICROBIAL_DEVICE_CYCLE_DATA", optional=False, repeatable=False
    )


class SiuS12(HL7Message):
    _structure_id = "SIU_S12"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sch: SCH = HL7SegmentAttr(segment_id="SCH", optional=False, repeatable=False)
    tq1: Optional[list[TQ1]] = HL7SegmentAttr(
        segment_id="TQ1", optional=True, repeatable=True
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[list[SiuS12Patient]] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=True
    )
    resources: list[SiuS12Resources] = HL7GroupAttr(
        name="RESOURCES", optional=False, repeatable=True
    )


class SlrS28(HL7Message):
    _structure_id = "SLR_S28"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    slt: list[SLT] = HL7SegmentAttr(segment_id="SLT", optional=False, repeatable=True)


class SrmS01(HL7Message):
    _structure_id = "SRM_S01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    arq: ARQ = HL7SegmentAttr(segment_id="ARQ", optional=False, repeatable=False)
    apr: Optional[APR] = HL7SegmentAttr(
        segment_id="APR", optional=True, repeatable=False
    )
    nte: Optional[list[NTE]] = HL7SegmentAttr(
        segment_id="NTE", optional=True, repeatable=True
    )
    patient: Optional[list[SrmS01Patient]] = HL7GroupAttr(
        name="PATIENT", optional=True, repeatable=True
    )
    resources: list[SrmS01Resources] = HL7GroupAttr(
        name="RESOURCES", optional=False, repeatable=True
    )


class SrrS01(HL7Message):
    _structure_id = "SRR_S01"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    msa: MSA = HL7SegmentAttr(segment_id="MSA", optional=False, repeatable=False)
    err: Optional[list[ERR]] = HL7SegmentAttr(
        segment_id="ERR", optional=True, repeatable=True
    )
    schedule: Optional[SrrS01Schedule] = HL7GroupAttr(
        name="SCHEDULE", optional=True, repeatable=False
    )


class SsrU04(HL7Message):
    _structure_id = "SSR_U04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    specimen_container: list[SsrU04SpecimenContainer] = HL7GroupAttr(
        name="SPECIMEN_CONTAINER", optional=False, repeatable=True
    )
    rol: Optional[ROL] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=False
    )


class SsuU03(HL7Message):
    _structure_id = "SSU_U03"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    specimen_container: list[SsuU03SpecimenContainer] = HL7GroupAttr(
        name="SPECIMEN_CONTAINER", optional=False, repeatable=True
    )
    rol: Optional[ROL] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=False
    )


class StcS33(HL7Message):
    _structure_id = "STC_S33"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    scp: list[SCP] = HL7SegmentAttr(segment_id="SCP", optional=False, repeatable=True)


class TcuU10(HL7Message):
    _structure_id = "TCU_U10"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    equ: EQU = HL7SegmentAttr(segment_id="EQU", optional=False, repeatable=False)
    test_configuration: list[TcuU10TestConfiguration] = HL7GroupAttr(
        name="TEST_CONFIGURATION", optional=False, repeatable=True
    )
    rol: Optional[ROL] = HL7SegmentAttr(
        segment_id="ROL", optional=True, repeatable=False
    )


class UdmQ05(HL7Message):
    _structure_id = "UDM_Q05"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    urd: URD = HL7SegmentAttr(segment_id="URD", optional=False, repeatable=False)
    urs: Optional[URS] = HL7SegmentAttr(
        segment_id="URS", optional=True, repeatable=False
    )
    dsp: list[DSP] = HL7SegmentAttr(segment_id="DSP", optional=False, repeatable=True)
    dsc: Optional[DSC] = HL7SegmentAttr(
        segment_id="DSC", optional=True, repeatable=False
    )


class VxuV04(HL7Message):
    _structure_id = "VXU_V04"

    msh: MSH = HL7SegmentAttr(segment_id="MSH", optional=False, repeatable=False)
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    sft: Optional[list[SFT]] = HL7SegmentAttr(
        segment_id="SFT", optional=True, repeatable=True
    )
    uac: Optional[UAC] = HL7SegmentAttr(
        segment_id="UAC", optional=True, repeatable=False
    )
    pid: PID = HL7SegmentAttr(segment_id="PID", optional=False, repeatable=False)
    pd1: Optional[PD1] = HL7SegmentAttr(
        segment_id="PD1", optional=True, repeatable=False
    )
    prt: Optional[list[PRT]] = HL7SegmentAttr(
        segment_id="PRT", optional=True, repeatable=True
    )
    nk1: Optional[list[NK1]] = HL7SegmentAttr(
        segment_id="NK1", optional=True, repeatable=True
    )
    arv: Optional[list[ARV]] = HL7SegmentAttr(
        segment_id="ARV", optional=True, repeatable=True
    )
    patient_visit: Optional[VxuV04PatientVisit] = HL7GroupAttr(
        name="PATIENT_VISIT", optional=True, repeatable=False
    )
    gt1: Optional[list[GT1]] = HL7SegmentAttr(
        segment_id="GT1", optional=True, repeatable=True
    )
    insurance: Optional[list[VxuV04Insurance]] = HL7GroupAttr(
        name="INSURANCE", optional=True, repeatable=True
    )
    person_observation: Optional[list[VxuV04PersonObservation]] = HL7GroupAttr(
        name="PERSON_OBSERVATION", optional=True, repeatable=True
    )
    order: Optional[list[VxuV04Order]] = HL7GroupAttr(
        name="ORDER", optional=True, repeatable=True
    )
