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

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)

class ADT_A01(HL7Message):
    _structure_id = "ADT_A01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    oh1 = HL7SegmentAttr[OH1](segment_id="OH1", optional=True, repeatable=True)
    oh2 = HL7SegmentAttr[OH2](segment_id="OH2", optional=True, repeatable=True)
    oh3 = HL7SegmentAttr[OH3](segment_id="OH3", optional=True, repeatable=False)
    oh4 = HL7SegmentAttr[OH4](segment_id="OH4", optional=True, repeatable=True)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    next_of_kin = \
        HL7GroupAttr[AdtA01NextOfKin](name="NEXT_OF_KIN", optional=True, repeatable=True)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[AdtA01Observation](name="OBSERVATION", optional=True, repeatable=True)
    al1 = HL7SegmentAttr[AL1](segment_id="AL1", optional=True, repeatable=True)
    iam = HL7SegmentAttr[IAM](segment_id="IAM", optional=True, repeatable=True)
    dg1 = HL7SegmentAttr[DG1](segment_id="DG1", optional=True, repeatable=True)
    drg = HL7SegmentAttr[DRG](segment_id="DRG", optional=True, repeatable=False)
    procedure = \
        HL7GroupAttr[AdtA01Procedure](name="PROCEDURE", optional=True, repeatable=True)
    gt1 = HL7SegmentAttr[GT1](segment_id="GT1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[AdtA01Insurance](name="INSURANCE", optional=True, repeatable=True)
    acc = HL7SegmentAttr[ACC](segment_id="ACC", optional=True, repeatable=False)
    ub1 = HL7SegmentAttr[UB1](segment_id="UB1", optional=True, repeatable=False)
    ub2 = HL7SegmentAttr[UB2](segment_id="UB2", optional=True, repeatable=False)
    pda = HL7SegmentAttr[PDA](segment_id="PDA", optional=True, repeatable=False)

class ADT_A02(HL7Message):
    _structure_id = "ADT_A02"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    oh1 = HL7SegmentAttr[OH1](segment_id="OH1", optional=True, repeatable=True)
    oh2 = HL7SegmentAttr[OH2](segment_id="OH2", optional=True, repeatable=True)
    oh3 = HL7SegmentAttr[OH3](segment_id="OH3", optional=True, repeatable=False)
    oh4 = HL7SegmentAttr[OH4](segment_id="OH4", optional=True, repeatable=True)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[AdtA02Observation](name="OBSERVATION", optional=True, repeatable=True)
    pda = HL7SegmentAttr[PDA](segment_id="PDA", optional=True, repeatable=False)

class ADT_A03(HL7Message):
    _structure_id = "ADT_A03"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    oh1 = HL7SegmentAttr[OH1](segment_id="OH1", optional=True, repeatable=True)
    oh2 = HL7SegmentAttr[OH2](segment_id="OH2", optional=True, repeatable=True)
    oh3 = HL7SegmentAttr[OH3](segment_id="OH3", optional=True, repeatable=False)
    oh4 = HL7SegmentAttr[OH4](segment_id="OH4", optional=True, repeatable=True)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    next_of_kin = \
        HL7GroupAttr[AdtA03NextOfKin](name="NEXT_OF_KIN", optional=True, repeatable=True)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    al1 = HL7SegmentAttr[AL1](segment_id="AL1", optional=True, repeatable=True)
    iam = HL7SegmentAttr[IAM](segment_id="IAM", optional=True, repeatable=True)
    dg1 = HL7SegmentAttr[DG1](segment_id="DG1", optional=True, repeatable=True)
    drg = HL7SegmentAttr[DRG](segment_id="DRG", optional=True, repeatable=False)
    procedure = \
        HL7GroupAttr[AdtA03Procedure](name="PROCEDURE", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[AdtA03Observation](name="OBSERVATION", optional=True, repeatable=True)
    gt1 = HL7SegmentAttr[GT1](segment_id="GT1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[AdtA03Insurance](name="INSURANCE", optional=True, repeatable=True)
    acc = HL7SegmentAttr[ACC](segment_id="ACC", optional=True, repeatable=False)
    pda = HL7SegmentAttr[PDA](segment_id="PDA", optional=True, repeatable=False)

class ADT_A05(HL7Message):
    _structure_id = "ADT_A05"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    oh1 = HL7SegmentAttr[OH1](segment_id="OH1", optional=True, repeatable=True)
    oh2 = HL7SegmentAttr[OH2](segment_id="OH2", optional=True, repeatable=True)
    oh3 = HL7SegmentAttr[OH3](segment_id="OH3", optional=True, repeatable=False)
    oh4 = HL7SegmentAttr[OH4](segment_id="OH4", optional=True, repeatable=True)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    next_of_kin = \
        HL7GroupAttr[AdtA05NextOfKin](name="NEXT_OF_KIN", optional=True, repeatable=True)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[AdtA05Observation](name="OBSERVATION", optional=True, repeatable=True)
    al1 = HL7SegmentAttr[AL1](segment_id="AL1", optional=True, repeatable=True)
    iam = HL7SegmentAttr[IAM](segment_id="IAM", optional=True, repeatable=True)
    dg1 = HL7SegmentAttr[DG1](segment_id="DG1", optional=True, repeatable=True)
    drg = HL7SegmentAttr[DRG](segment_id="DRG", optional=True, repeatable=False)
    procedure = \
        HL7GroupAttr[AdtA05Procedure](name="PROCEDURE", optional=True, repeatable=True)
    gt1 = HL7SegmentAttr[GT1](segment_id="GT1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[AdtA05Insurance](name="INSURANCE", optional=True, repeatable=True)
    acc = HL7SegmentAttr[ACC](segment_id="ACC", optional=True, repeatable=False)
    ub1 = HL7SegmentAttr[UB1](segment_id="UB1", optional=True, repeatable=False)
    ub2 = HL7SegmentAttr[UB2](segment_id="UB2", optional=True, repeatable=False)

class ADT_A06(HL7Message):
    _structure_id = "ADT_A06"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    oh1 = HL7SegmentAttr[OH1](segment_id="OH1", optional=True, repeatable=True)
    oh2 = HL7SegmentAttr[OH2](segment_id="OH2", optional=True, repeatable=True)
    oh3 = HL7SegmentAttr[OH3](segment_id="OH3", optional=True, repeatable=False)
    oh4 = HL7SegmentAttr[OH4](segment_id="OH4", optional=True, repeatable=True)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    mrg = HL7SegmentAttr[MRG](segment_id="MRG", optional=True, repeatable=False)
    next_of_kin = \
        HL7GroupAttr[AdtA06NextOfKin](name="NEXT_OF_KIN", optional=True, repeatable=True)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[AdtA06Observation](name="OBSERVATION", optional=True, repeatable=True)
    al1 = HL7SegmentAttr[AL1](segment_id="AL1", optional=True, repeatable=True)
    iam = HL7SegmentAttr[IAM](segment_id="IAM", optional=True, repeatable=True)
    dg1 = HL7SegmentAttr[DG1](segment_id="DG1", optional=True, repeatable=True)
    drg = HL7SegmentAttr[DRG](segment_id="DRG", optional=True, repeatable=False)
    procedure = \
        HL7GroupAttr[AdtA06Procedure](name="PROCEDURE", optional=True, repeatable=True)
    gt1 = HL7SegmentAttr[GT1](segment_id="GT1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[AdtA06Insurance](name="INSURANCE", optional=True, repeatable=True)
    acc = HL7SegmentAttr[ACC](segment_id="ACC", optional=True, repeatable=False)
    ub1 = HL7SegmentAttr[UB1](segment_id="UB1", optional=True, repeatable=False)
    ub2 = HL7SegmentAttr[UB2](segment_id="UB2", optional=True, repeatable=False)

class ADT_A09(HL7Message):
    _structure_id = "ADT_A09"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[AdtA09Observation](name="OBSERVATION", optional=True, repeatable=True)
    dg1 = HL7SegmentAttr[DG1](segment_id="DG1", optional=True, repeatable=True)

class ADT_A12(HL7Message):
    _structure_id = "ADT_A12"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[AdtA12Observation](name="OBSERVATION", optional=True, repeatable=True)
    dg1 = HL7SegmentAttr[DG1](segment_id="DG1", optional=True, repeatable=False)

class ADT_A15(HL7Message):
    _structure_id = "ADT_A15"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=False, repeatable=True)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[AdtA15Observation](name="OBSERVATION", optional=True, repeatable=True)

class ADT_A16(HL7Message):
    _structure_id = "ADT_A16"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    oh1 = HL7SegmentAttr[OH1](segment_id="OH1", optional=True, repeatable=True)
    oh2 = HL7SegmentAttr[OH2](segment_id="OH2", optional=True, repeatable=True)
    oh3 = HL7SegmentAttr[OH3](segment_id="OH3", optional=True, repeatable=False)
    oh4 = HL7SegmentAttr[OH4](segment_id="OH4", optional=True, repeatable=True)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    next_of_kin = \
        HL7GroupAttr[AdtA16NextOfKin](name="NEXT_OF_KIN", optional=True, repeatable=True)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[AdtA16Observation](name="OBSERVATION", optional=True, repeatable=True)
    al1 = HL7SegmentAttr[AL1](segment_id="AL1", optional=True, repeatable=True)
    iam = HL7SegmentAttr[IAM](segment_id="IAM", optional=True, repeatable=True)
    dg1 = HL7SegmentAttr[DG1](segment_id="DG1", optional=True, repeatable=True)
    drg = HL7SegmentAttr[DRG](segment_id="DRG", optional=True, repeatable=False)
    procedure = \
        HL7GroupAttr[AdtA16Procedure](name="PROCEDURE", optional=True, repeatable=True)
    gt1 = HL7SegmentAttr[GT1](segment_id="GT1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[AdtA16Insurance](name="INSURANCE", optional=True, repeatable=True)
    acc = HL7SegmentAttr[ACC](segment_id="ACC", optional=True, repeatable=False)

class ADT_A17(HL7Message):
    _structure_id = "ADT_A17"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    observation_result_1 = \
        HL7GroupAttr[AdtA17ObservationResult1](name="OBSERVATION_RESULT_1", optional=True, repeatable=True)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    observation_result_2 = \
        HL7GroupAttr[AdtA17ObservationResult2](name="OBSERVATION_RESULT_2", optional=True, repeatable=True)

class ADT_A20(HL7Message):
    _structure_id = "ADT_A20"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    npu = HL7SegmentAttr[NPU](segment_id="NPU", optional=False, repeatable=False)

class ADT_A21(HL7Message):
    _structure_id = "ADT_A21"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[AdtA21Observation](name="OBSERVATION", optional=True, repeatable=True)

class ADT_A24(HL7Message):
    _structure_id = "ADT_A24"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=True, repeatable=False)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=True, repeatable=False)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)

class ADT_A37(HL7Message):
    _structure_id = "ADT_A37"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=True, repeatable=False)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=True, repeatable=False)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)

class ADT_A38(HL7Message):
    _structure_id = "ADT_A38"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[AdtA38Observation](name="OBSERVATION", optional=True, repeatable=True)
    dg1 = HL7SegmentAttr[DG1](segment_id="DG1", optional=True, repeatable=True)
    drg = HL7SegmentAttr[DRG](segment_id="DRG", optional=True, repeatable=False)

class ADT_A39(HL7Message):
    _structure_id = "ADT_A39"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    patient = \
        HL7GroupAttr[AdtA39Patient](name="PATIENT", optional=False, repeatable=True)

class ADT_A43(HL7Message):
    _structure_id = "ADT_A43"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    patient = \
        HL7GroupAttr[AdtA43Patient](name="PATIENT", optional=False, repeatable=True)

class ADT_A44(HL7Message):
    _structure_id = "ADT_A44"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    patient = \
        HL7GroupAttr[AdtA44Patient](name="PATIENT", optional=False, repeatable=True)

class ADT_A45(HL7Message):
    _structure_id = "ADT_A45"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    merge_info = \
        HL7GroupAttr[AdtA45MergeInfo](name="MERGE_INFO", optional=False, repeatable=True)

class ADT_A50(HL7Message):
    _structure_id = "ADT_A50"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    mrg = HL7SegmentAttr[MRG](segment_id="MRG", optional=False, repeatable=False)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)

class ADT_A52(HL7Message):
    _structure_id = "ADT_A52"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)

class ADT_A54(HL7Message):
    _structure_id = "ADT_A54"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)

class ADT_A60(HL7Message):
    _structure_id = "ADT_A60"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    visit_group = \
        HL7GroupAttr[AdtA60VisitGroup](name="VISIT_GROUP", optional=True, repeatable=False)
    adverse_reaction_group = \
        HL7GroupAttr[AdtA60AdverseReactionGroup](name="ADVERSE_REACTION_GROUP", optional=True, repeatable=True)

class ADT_A61(HL7Message):
    _structure_id = "ADT_A61"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)

class BAR_P01(HL7Message):
    _structure_id = "BAR_P01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    visit = \
        HL7GroupAttr[BarP01Visit](name="VISIT", optional=False, repeatable=True)

class BAR_P02(HL7Message):
    _structure_id = "BAR_P02"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    patient = \
        HL7GroupAttr[BarP02Patient](name="PATIENT", optional=False, repeatable=True)

class BAR_P05(HL7Message):
    _structure_id = "BAR_P05"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    visit = \
        HL7GroupAttr[BarP05Visit](name="VISIT", optional=False, repeatable=True)

class BAR_P06(HL7Message):
    _structure_id = "BAR_P06"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    patient = \
        HL7GroupAttr[BarP06Patient](name="PATIENT", optional=False, repeatable=True)

class BAR_P10(HL7Message):
    _structure_id = "BAR_P10"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    diagnosis = \
        HL7GroupAttr[BarP10Diagnosis](name="DIAGNOSIS", optional=True, repeatable=True)
    gp1 = HL7SegmentAttr[GP1](segment_id="GP1", optional=False, repeatable=False)
    procedure = \
        HL7GroupAttr[BarP10Procedure](name="PROCEDURE", optional=True, repeatable=True)

class BAR_P12(HL7Message):
    _structure_id = "BAR_P12"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    diagnosis = \
        HL7GroupAttr[BarP12Diagnosis](name="DIAGNOSIS", optional=True, repeatable=True)
    drg = HL7SegmentAttr[DRG](segment_id="DRG", optional=True, repeatable=False)
    procedure = \
        HL7GroupAttr[BarP12Procedure](name="PROCEDURE", optional=True, repeatable=True)
    obx = HL7SegmentAttr[OBX](segment_id="OBX", optional=True, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)

class BPS_O29(HL7Message):
    _structure_id = "BPS_O29"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[BpsO29Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[BpsO29Order](name="ORDER", optional=False, repeatable=True)

class BRP_O30(HL7Message):
    _structure_id = "BRP_O30"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[BrpO30Response](name="RESPONSE", optional=True, repeatable=False)

class BRT_O32(HL7Message):
    _structure_id = "BRT_O32"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[BrtO32Response](name="RESPONSE", optional=True, repeatable=False)

class BTS_O31(HL7Message):
    _structure_id = "BTS_O31"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[BtsO31Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[BtsO31Order](name="ORDER", optional=False, repeatable=True)

class CCF_I22(HL7Message):
    _structure_id = "CCF_I22"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)

class CCI_I22(HL7Message):
    _structure_id = "CCI_I22"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[CciI22Insurance](name="INSURANCE", optional=True, repeatable=True)
    appointment_history = \
        HL7GroupAttr[CciI22AppointmentHistory](name="APPOINTMENT_HISTORY", optional=True, repeatable=True)
    clinical_history = \
        HL7GroupAttr[CciI22ClinicalHistory](name="CLINICAL_HISTORY", optional=True, repeatable=True)
    patient_visits = \
        HL7GroupAttr[CciI22PatientVisits](name="PATIENT_VISITS", optional=False, repeatable=True)
    medication_history = \
        HL7GroupAttr[CciI22MedicationHistory](name="MEDICATION_HISTORY", optional=True, repeatable=True)
    problem = \
        HL7GroupAttr[CciI22Problem](name="PROBLEM", optional=True, repeatable=True)
    goal = \
        HL7GroupAttr[CciI22Goal](name="GOAL", optional=True, repeatable=True)
    pathway = \
        HL7GroupAttr[CciI22Pathway](name="PATHWAY", optional=True, repeatable=True)
    rel = HL7SegmentAttr[REL](segment_id="REL", optional=True, repeatable=True)

class CCM_I21(HL7Message):
    _structure_id = "CCM_I21"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[CcmI21Insurance](name="INSURANCE", optional=True, repeatable=True)
    appointment_history = \
        HL7GroupAttr[CcmI21AppointmentHistory](name="APPOINTMENT_HISTORY", optional=True, repeatable=True)
    clinical_history = \
        HL7GroupAttr[CcmI21ClinicalHistory](name="CLINICAL_HISTORY", optional=True, repeatable=True)
    patient_visits = \
        HL7GroupAttr[CcmI21PatientVisits](name="PATIENT_VISITS", optional=False, repeatable=True)
    medication_history = \
        HL7GroupAttr[CcmI21MedicationHistory](name="MEDICATION_HISTORY", optional=True, repeatable=True)
    problem = \
        HL7GroupAttr[CcmI21Problem](name="PROBLEM", optional=True, repeatable=True)
    goal = \
        HL7GroupAttr[CcmI21Goal](name="GOAL", optional=True, repeatable=True)
    pathway = \
        HL7GroupAttr[CcmI21Pathway](name="PATHWAY", optional=True, repeatable=True)
    rel = HL7SegmentAttr[REL](segment_id="REL", optional=True, repeatable=True)

class CCQ_I19(HL7Message):
    _structure_id = "CCQ_I19"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    rf1 = HL7SegmentAttr[RF1](segment_id="RF1", optional=False, repeatable=False)
    provider_contact = \
        HL7GroupAttr[CcqI19ProviderContact](name="PROVIDER_CONTACT", optional=True, repeatable=True)
    rel = HL7SegmentAttr[REL](segment_id="REL", optional=True, repeatable=True)

class CCR_I16(HL7Message):
    _structure_id = "CCR_I16"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    rf1 = HL7SegmentAttr[RF1](segment_id="RF1", optional=False, repeatable=True)
    provider_contact = \
        HL7GroupAttr[CcrI16ProviderContact](name="PROVIDER_CONTACT", optional=False, repeatable=True)
    clinical_order = \
        HL7GroupAttr[CcrI16ClinicalOrder](name="CLINICAL_ORDER", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[CcrI16Patient](name="PATIENT", optional=False, repeatable=True)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[CcrI16Insurance](name="INSURANCE", optional=True, repeatable=True)
    appointment_history = \
        HL7GroupAttr[CcrI16AppointmentHistory](name="APPOINTMENT_HISTORY", optional=True, repeatable=True)
    clinical_history = \
        HL7GroupAttr[CcrI16ClinicalHistory](name="CLINICAL_HISTORY", optional=True, repeatable=True)
    patient_visits = \
        HL7GroupAttr[CcrI16PatientVisits](name="PATIENT_VISITS", optional=False, repeatable=True)
    medication_history = \
        HL7GroupAttr[CcrI16MedicationHistory](name="MEDICATION_HISTORY", optional=True, repeatable=True)
    problem = \
        HL7GroupAttr[CcrI16Problem](name="PROBLEM", optional=True, repeatable=True)
    goal = \
        HL7GroupAttr[CcrI16Goal](name="GOAL", optional=True, repeatable=True)
    pathway = \
        HL7GroupAttr[CcrI16Pathway](name="PATHWAY", optional=True, repeatable=True)
    rel = HL7SegmentAttr[REL](segment_id="REL", optional=True, repeatable=True)

class CCU_I20(HL7Message):
    _structure_id = "CCU_I20"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    rf1 = HL7SegmentAttr[RF1](segment_id="RF1", optional=False, repeatable=False)
    provider_contact = \
        HL7GroupAttr[CcuI20ProviderContact](name="PROVIDER_CONTACT", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[CcuI20Patient](name="PATIENT", optional=True, repeatable=True)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[CcuI20Insurance](name="INSURANCE", optional=True, repeatable=True)
    appointment_history = \
        HL7GroupAttr[CcuI20AppointmentHistory](name="APPOINTMENT_HISTORY", optional=True, repeatable=True)
    clinical_history = \
        HL7GroupAttr[CcuI20ClinicalHistory](name="CLINICAL_HISTORY", optional=True, repeatable=True)
    patient_visits = \
        HL7GroupAttr[CcuI20PatientVisits](name="PATIENT_VISITS", optional=False, repeatable=True)
    medication_history = \
        HL7GroupAttr[CcuI20MedicationHistory](name="MEDICATION_HISTORY", optional=True, repeatable=True)
    problem = \
        HL7GroupAttr[CcuI20Problem](name="PROBLEM", optional=True, repeatable=True)
    goal = \
        HL7GroupAttr[CcuI20Goal](name="GOAL", optional=True, repeatable=True)
    pathway = \
        HL7GroupAttr[CcuI20Pathway](name="PATHWAY", optional=True, repeatable=True)
    rel = HL7SegmentAttr[REL](segment_id="REL", optional=True, repeatable=True)

class CQU_I19(HL7Message):
    _structure_id = "CQU_I19"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    rf1 = HL7SegmentAttr[RF1](segment_id="RF1", optional=False, repeatable=False)
    provider_contact = \
        HL7GroupAttr[CquI19ProviderContact](name="PROVIDER_CONTACT", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[CquI19Patient](name="PATIENT", optional=True, repeatable=True)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[CquI19Insurance](name="INSURANCE", optional=True, repeatable=True)
    appointment_history = \
        HL7GroupAttr[CquI19AppointmentHistory](name="APPOINTMENT_HISTORY", optional=True, repeatable=True)
    clinical_history = \
        HL7GroupAttr[CquI19ClinicalHistory](name="CLINICAL_HISTORY", optional=True, repeatable=True)
    patient_visits = \
        HL7GroupAttr[CquI19PatientVisits](name="PATIENT_VISITS", optional=False, repeatable=True)
    medication_history = \
        HL7GroupAttr[CquI19MedicationHistory](name="MEDICATION_HISTORY", optional=True, repeatable=True)
    problem = \
        HL7GroupAttr[CquI19Problem](name="PROBLEM", optional=True, repeatable=True)
    goal = \
        HL7GroupAttr[CquI19Goal](name="GOAL", optional=True, repeatable=True)
    pathway = \
        HL7GroupAttr[CquI19Pathway](name="PATHWAY", optional=True, repeatable=True)
    rel = HL7SegmentAttr[REL](segment_id="REL", optional=True, repeatable=True)

class CRM_C01(HL7Message):
    _structure_id = "CRM_C01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    patient = \
        HL7GroupAttr[CrmC01Patient](name="PATIENT", optional=False, repeatable=True)

class CSU_C09(HL7Message):
    _structure_id = "CSU_C09"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    patient = \
        HL7GroupAttr[CsuC09Patient](name="PATIENT", optional=False, repeatable=True)

class DBC_O41(HL7Message):
    _structure_id = "DBC_O41"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    donor = \
        HL7GroupAttr[DbcO41Donor](name="DONOR", optional=True, repeatable=False)

class DBC_O42(HL7Message):
    _structure_id = "DBC_O42"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    donor = \
        HL7GroupAttr[DbcO42Donor](name="DONOR", optional=True, repeatable=False)

class DEL_O46(HL7Message):
    _structure_id = "DEL_O46"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    donor = \
        HL7GroupAttr[DelO46Donor](name="DONOR", optional=True, repeatable=False)
    don = HL7SegmentAttr[DON](segment_id="DON", optional=False, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)

class DEO_O45(HL7Message):
    _structure_id = "DEO_O45"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    donor = \
        HL7GroupAttr[DeoO45Donor](name="Donor", optional=True, repeatable=False)
    donation_order = \
        HL7GroupAttr[DeoO45DonationOrder](name="DONATION_ORDER", optional=False, repeatable=True)

class DER_O44(HL7Message):
    _structure_id = "DER_O44"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    donor = \
        HL7GroupAttr[DerO44Donor](name="DONOR", optional=True, repeatable=False)
    donor_order = \
        HL7GroupAttr[DerO44DonorOrder](name="DONOR_ORDER", optional=False, repeatable=True)

class DFT_P03(HL7Message):
    _structure_id = "DFT_P03"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    visit = \
        HL7GroupAttr[DftP03Visit](name="VISIT", optional=True, repeatable=False)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    common_order = \
        HL7GroupAttr[DftP03CommonOrder](name="COMMON_ORDER", optional=True, repeatable=True)
    financial = \
        HL7GroupAttr[DftP03Financial](name="FINANCIAL", optional=False, repeatable=True)
    diagnosis = \
        HL7GroupAttr[DftP03Diagnosis](name="DIAGNOSIS", optional=True, repeatable=True)
    drg = HL7SegmentAttr[DRG](segment_id="DRG", optional=True, repeatable=False)
    gt1 = HL7SegmentAttr[GT1](segment_id="GT1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[DftP03Insurance](name="INSURANCE", optional=True, repeatable=True)
    acc = HL7SegmentAttr[ACC](segment_id="ACC", optional=True, repeatable=False)

class DFT_P11(HL7Message):
    _structure_id = "DFT_P11"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)
    visit = \
        HL7GroupAttr[DftP11Visit](name="VISIT", optional=True, repeatable=False)
    db1 = HL7SegmentAttr[DB1](segment_id="DB1", optional=True, repeatable=True)
    common_order = \
        HL7GroupAttr[DftP11CommonOrder](name="COMMON_ORDER", optional=True, repeatable=True)
    diagnosis = \
        HL7GroupAttr[DftP11Diagnosis](name="DIAGNOSIS", optional=True, repeatable=True)
    drg = HL7SegmentAttr[DRG](segment_id="DRG", optional=True, repeatable=False)
    gt1 = HL7SegmentAttr[GT1](segment_id="GT1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[DftP11Insurance](name="INSURANCE", optional=True, repeatable=True)
    acc = HL7SegmentAttr[ACC](segment_id="ACC", optional=True, repeatable=False)
    financial = \
        HL7GroupAttr[DftP11Financial](name="FINANCIAL", optional=False, repeatable=True)

class DPR_O48(HL7Message):
    _structure_id = "DPR_O48"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    donor = \
        HL7GroupAttr[DprO48Donor](name="DONOR", optional=True, repeatable=False)
    donation_order = \
        HL7GroupAttr[DprO48DonationOrder](name="DONATION_ORDER", optional=False, repeatable=True)
    donation = \
        HL7GroupAttr[DprO48Donation](name="DONATION", optional=True, repeatable=False)

class DRC_O47(HL7Message):
    _structure_id = "DRC_O47"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    donor = \
        HL7GroupAttr[DrcO47Donor](name="DONOR", optional=True, repeatable=False)
    donation_order = \
        HL7GroupAttr[DrcO47DonationOrder](name="DONATION_ORDER", optional=False, repeatable=True)

class DRG_O43(HL7Message):
    _structure_id = "DRG_O43"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    donor = \
        HL7GroupAttr[DrgO43Donor](name="DONOR", optional=True, repeatable=False)

class EAC_U07(HL7Message):
    _structure_id = "EAC_U07"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    equ = HL7SegmentAttr[EQU](segment_id="EQU", optional=False, repeatable=False)
    command = \
        HL7GroupAttr[EacU07Command](name="COMMAND", optional=False, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=False)

class EAN_U09(HL7Message):
    _structure_id = "EAN_U09"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    equ = HL7SegmentAttr[EQU](segment_id="EQU", optional=False, repeatable=False)
    notification = \
        HL7GroupAttr[EanU09Notification](name="NOTIFICATION", optional=False, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=False)

class EAR_U08(HL7Message):
    _structure_id = "EAR_U08"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    equ = HL7SegmentAttr[EQU](segment_id="EQU", optional=False, repeatable=False)
    command_response = \
        HL7GroupAttr[EarU08CommandResponse](name="COMMAND_RESPONSE", optional=False, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=False)

class EHC_E01(HL7Message):
    _structure_id = "EHC_E01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=True)
    invoice_information_submit = \
        HL7GroupAttr[EhcE01InvoiceInformationSubmit](name="INVOICE_INFORMATION_SUBMIT", optional=False, repeatable=False)

class EHC_E02(HL7Message):
    _structure_id = "EHC_E02"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=True)
    invoice_information_cancel = \
        HL7GroupAttr[EhcE02InvoiceInformationCancel](name="INVOICE_INFORMATION_CANCEL", optional=False, repeatable=False)

class EHC_E04(HL7Message):
    _structure_id = "EHC_E04"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=True)
    reassessment_request_info = \
        HL7GroupAttr[EhcE04ReassessmentRequestInfo](name="REASSESSMENT_REQUEST_INFO", optional=False, repeatable=False)

class EHC_E10(HL7Message):
    _structure_id = "EHC_E10"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    invoice_processing_results_info = \
        HL7GroupAttr[EhcE10InvoiceProcessingResultsInfo](name="INVOICE_PROCESSING_RESULTS_INFO", optional=False, repeatable=True)

class EHC_E12(HL7Message):
    _structure_id = "EHC_E12"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=True)
    rfi = HL7SegmentAttr[RFI](segment_id="RFI", optional=False, repeatable=False)
    ctd = HL7SegmentAttr[CTD](segment_id="CTD", optional=True, repeatable=True)
    ivc = HL7SegmentAttr[IVC](segment_id="IVC", optional=False, repeatable=False)
    pss = HL7SegmentAttr[PSS](segment_id="PSS", optional=False, repeatable=False)
    psg = HL7SegmentAttr[PSG](segment_id="PSG", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=True, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    psl = HL7SegmentAttr[PSL](segment_id="PSL", optional=True, repeatable=True)
    request = \
        HL7GroupAttr[EhcE12Request](name="REQUEST", optional=False, repeatable=True)

class EHC_E13(HL7Message):
    _structure_id = "EHC_E13"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    rfi = HL7SegmentAttr[RFI](segment_id="RFI", optional=False, repeatable=False)
    ctd = HL7SegmentAttr[CTD](segment_id="CTD", optional=True, repeatable=True)
    ivc = HL7SegmentAttr[IVC](segment_id="IVC", optional=False, repeatable=False)
    pss = HL7SegmentAttr[PSS](segment_id="PSS", optional=False, repeatable=False)
    psg = HL7SegmentAttr[PSG](segment_id="PSG", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=True, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    psl = HL7SegmentAttr[PSL](segment_id="PSL", optional=True, repeatable=False)
    request = \
        HL7GroupAttr[EhcE13Request](name="REQUEST", optional=False, repeatable=True)

class EHC_E15(HL7Message):
    _structure_id = "EHC_E15"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=True)
    payment_remittance_header_info = \
        HL7GroupAttr[EhcE15PaymentRemittanceHeaderInfo](name="PAYMENT_REMITTANCE_HEADER_INFO", optional=False, repeatable=False)
    payment_remittance_detail_info = \
        HL7GroupAttr[EhcE15PaymentRemittanceDetailInfo](name="PAYMENT_REMITTANCE_DETAIL_INFO", optional=True, repeatable=True)
    adjustment_payee = \
        HL7GroupAttr[EhcE15AdjustmentPayee](name="ADJUSTMENT_PAYEE", optional=True, repeatable=True)

class EHC_E20(HL7Message):
    _structure_id = "EHC_E20"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=True)
    authorization_request = \
        HL7GroupAttr[EhcE20AuthorizationRequest](name="AUTHORIZATION_REQUEST", optional=False, repeatable=False)

class EHC_E21(HL7Message):
    _structure_id = "EHC_E21"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=True)
    authorization_request = \
        HL7GroupAttr[EhcE21AuthorizationRequest](name="AUTHORIZATION_REQUEST", optional=False, repeatable=False)

class EHC_E24(HL7Message):
    _structure_id = "EHC_E24"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    authorization_response_info = \
        HL7GroupAttr[EhcE24AuthorizationResponseInfo](name="AUTHORIZATION_RESPONSE_INFO", optional=False, repeatable=False)

class ESR_U02(HL7Message):
    _structure_id = "ESR_U02"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    equ = HL7SegmentAttr[EQU](segment_id="EQU", optional=False, repeatable=False)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=False)

class ESU_U01(HL7Message):
    _structure_id = "ESU_U01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    equ = HL7SegmentAttr[EQU](segment_id="EQU", optional=False, repeatable=False)
    isd = HL7SegmentAttr[ISD](segment_id="ISD", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=False)

class INR_U06(HL7Message):
    _structure_id = "INR_U06"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    equ = HL7SegmentAttr[EQU](segment_id="EQU", optional=False, repeatable=False)
    inv = HL7SegmentAttr[INV](segment_id="INV", optional=False, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=False)

class INR_U14(HL7Message):
    _structure_id = "INR_U14"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    equ = HL7SegmentAttr[EQU](segment_id="EQU", optional=False, repeatable=False)
    inv = HL7SegmentAttr[INV](segment_id="INV", optional=True, repeatable=True)

class INU_U05(HL7Message):
    _structure_id = "INU_U05"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    equ = HL7SegmentAttr[EQU](segment_id="EQU", optional=False, repeatable=False)
    inv = HL7SegmentAttr[INV](segment_id="INV", optional=False, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=False)

class LSU_U12(HL7Message):
    _structure_id = "LSU_U12"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    equ = HL7SegmentAttr[EQU](segment_id="EQU", optional=False, repeatable=False)
    eqp = HL7SegmentAttr[EQP](segment_id="EQP", optional=False, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=False)

class MDM_T01(HL7Message):
    _structure_id = "MDM_T01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    common_order = \
        HL7GroupAttr[MdmT01CommonOrder](name="COMMON_ORDER", optional=True, repeatable=True)
    txa = HL7SegmentAttr[TXA](segment_id="TXA", optional=False, repeatable=False)
    con = HL7SegmentAttr[CON](segment_id="CON", optional=True, repeatable=True)

class MDM_T02(HL7Message):
    _structure_id = "MDM_T02"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    common_order = \
        HL7GroupAttr[MdmT02CommonOrder](name="COMMON_ORDER", optional=True, repeatable=True)
    txa = HL7SegmentAttr[TXA](segment_id="TXA", optional=False, repeatable=False)
    con = HL7SegmentAttr[CON](segment_id="CON", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[MdmT02Observation](name="OBSERVATION", optional=False, repeatable=True)

class MFK_M01(HL7Message):
    _structure_id = "MFK_M01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mfa = HL7SegmentAttr[MFA](segment_id="MFA", optional=True, repeatable=True)

class MFN_M02(HL7Message):
    _structure_id = "MFN_M02"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mf_staff = \
        HL7GroupAttr[MfnM02MfStaff](name="MF_STAFF", optional=False, repeatable=True)

class MFN_M04(HL7Message):
    _structure_id = "MFN_M04"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    mf_cdm = \
        HL7GroupAttr[MfnM04MfCdm](name="MF_CDM", optional=False, repeatable=True)

class MFN_M05(HL7Message):
    _structure_id = "MFN_M05"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mf_location = \
        HL7GroupAttr[MfnM05MfLocation](name="MF_LOCATION", optional=False, repeatable=True)

class MFN_M06(HL7Message):
    _structure_id = "MFN_M06"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mf_clin_study = \
        HL7GroupAttr[MfnM06MfClinStudy](name="MF_CLIN_STUDY", optional=False, repeatable=True)

class MFN_M07(HL7Message):
    _structure_id = "MFN_M07"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mf_clin_study_sched = \
        HL7GroupAttr[MfnM07MfClinStudySched](name="MF_CLIN_STUDY_SCHED", optional=False, repeatable=True)

class MFN_M08(HL7Message):
    _structure_id = "MFN_M08"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mf_test_numeric = \
        HL7GroupAttr[MfnM08MfTestNumeric](name="MF_TEST_NUMERIC", optional=False, repeatable=True)

class MFN_M09(HL7Message):
    _structure_id = "MFN_M09"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mf_test_categorical = \
        HL7GroupAttr[MfnM09MfTestCategorical](name="MF_TEST_CATEGORICAL", optional=False, repeatable=True)

class MFN_M10(HL7Message):
    _structure_id = "MFN_M10"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mf_test_batteries = \
        HL7GroupAttr[MfnM10MfTestBatteries](name="MF_TEST_BATTERIES", optional=False, repeatable=True)

class MFN_M11(HL7Message):
    _structure_id = "MFN_M11"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mf_test_calculated = \
        HL7GroupAttr[MfnM11MfTestCalculated](name="MF_TEST_CALCULATED", optional=False, repeatable=True)

class MFN_M12(HL7Message):
    _structure_id = "MFN_M12"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mf_obs_attributes = \
        HL7GroupAttr[MfnM12MfObsAttributes](name="MF_OBS_ATTRIBUTES", optional=False, repeatable=True)

class MFN_M13(HL7Message):
    _structure_id = "MFN_M13"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mfe = HL7SegmentAttr[MFE](segment_id="MFE", optional=False, repeatable=True)

class MFN_M15(HL7Message):
    _structure_id = "MFN_M15"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mf_inv_item = \
        HL7GroupAttr[MfnM15MfInvItem](name="MF_INV_ITEM", optional=False, repeatable=True)

class MFN_M16(HL7Message):
    _structure_id = "MFN_M16"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    material_item_record = \
        HL7GroupAttr[MfnM16MaterialItemRecord](name="MATERIAL_ITEM_RECORD", optional=False, repeatable=True)

class MFN_M17(HL7Message):
    _structure_id = "MFN_M17"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mf_drg = \
        HL7GroupAttr[MfnM17MfDrg](name="MF_DRG", optional=False, repeatable=True)

class MFN_M18(HL7Message):
    _structure_id = "MFN_M18"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mf_payer = \
        HL7GroupAttr[MfnM18MfPayer](name="MF_PAYER", optional=False, repeatable=True)

class MFN_M19(HL7Message):
    _structure_id = "MFN_M19"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    contract_record = \
        HL7GroupAttr[MfnM19ContractRecord](name="CONTRACT_RECORD", optional=False, repeatable=True)

class MFN_Znn(HL7Message):
    _structure_id = "MFN_Znn"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    mfi = HL7SegmentAttr[MFI](segment_id="MFI", optional=False, repeatable=False)
    mf_site_defined = \
        HL7GroupAttr[MfnZnnMfSiteDefined](name="MF_SITE_DEFINED", optional=False, repeatable=True)

class NMD_N02(HL7Message):
    _structure_id = "NMD_N02"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    clock_and_stats_with_notes = \
        HL7GroupAttr[NmdN02ClockAndStatsWithNotes](name="CLOCK_AND_STATS_WITH_NOTES", optional=False, repeatable=True)

class OMB_O27(HL7Message):
    _structure_id = "OMB_O27"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OmbO27Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[OmbO27Order](name="ORDER", optional=False, repeatable=True)

class OMD_O03(HL7Message):
    _structure_id = "OMD_O03"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OmdO03Patient](name="PATIENT", optional=True, repeatable=False)
    order_diet = \
        HL7GroupAttr[OmdO03OrderDiet](name="ORDER_DIET", optional=False, repeatable=True)
    order_tray = \
        HL7GroupAttr[OmdO03OrderTray](name="ORDER_TRAY", optional=True, repeatable=True)

class OMG_O19(HL7Message):
    _structure_id = "OMG_O19"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OmgO19Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[OmgO19Order](name="ORDER", optional=False, repeatable=True)
    device = \
        HL7GroupAttr[OmgO19Device](name="DEVICE", optional=True, repeatable=True)

class OMI_O23(HL7Message):
    _structure_id = "OMI_O23"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OmiO23Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[OmiO23Order](name="ORDER", optional=False, repeatable=True)
    device = \
        HL7GroupAttr[OmiO23Device](name="DEVICE", optional=True, repeatable=True)

class OML_O21(HL7Message):
    _structure_id = "OML_O21"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OmlO21Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[OmlO21Order](name="ORDER", optional=False, repeatable=True)
    device = \
        HL7GroupAttr[OmlO21Device](name="DEVICE", optional=True, repeatable=True)

class OML_O33(HL7Message):
    _structure_id = "OML_O33"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OmlO33Patient](name="PATIENT", optional=True, repeatable=False)
    specimen = \
        HL7GroupAttr[OmlO33Specimen](name="SPECIMEN", optional=False, repeatable=True)
    device = \
        HL7GroupAttr[OmlO33Device](name="DEVICE", optional=True, repeatable=True)

class OML_O35(HL7Message):
    _structure_id = "OML_O35"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OmlO35Patient](name="PATIENT", optional=True, repeatable=False)
    specimen = \
        HL7GroupAttr[OmlO35Specimen](name="SPECIMEN", optional=False, repeatable=True)
    device = \
        HL7GroupAttr[OmlO35Device](name="DEVICE", optional=True, repeatable=True)

class OML_O39(HL7Message):
    _structure_id = "OML_O39"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OmlO39Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[OmlO39Order](name="ORDER", optional=False, repeatable=True)
    device = \
        HL7GroupAttr[OmlO39Device](name="DEVICE", optional=True, repeatable=True)

class OML_O59(HL7Message):
    _structure_id = "OML_O59"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OmlO59Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[OmlO59Order](name="ORDER", optional=False, repeatable=True)

class OMN_O07(HL7Message):
    _structure_id = "OMN_O07"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OmnO07Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[OmnO07Order](name="ORDER", optional=False, repeatable=True)

class ORM_O01(HL7Message):
    _structure_id = "ORM_O01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OrmO01Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[OrmO01Order](name="ORDER", optional=False, repeatable=True)

class OMP_O09(HL7Message):
    _structure_id = "OMP_O09"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OmpO09Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[OmpO09Order](name="ORDER", optional=False, repeatable=True)

class OMQ_O57(HL7Message):
    _structure_id = "OMQ_O57"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OmqO57Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[OmqO57Order](name="ORDER", optional=False, repeatable=True)

class OMS_O05(HL7Message):
    _structure_id = "OMS_O05"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OmsO05Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[OmsO05Order](name="ORDER", optional=False, repeatable=True)

class OPL_O37(HL7Message):
    _structure_id = "OPL_O37"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=False, repeatable=True)
    guarantor = \
        HL7GroupAttr[OplO37Guarantor](name="GUARANTOR", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[OplO37Order](name="ORDER", optional=False, repeatable=True)

class OPR_O38(HL7Message):
    _structure_id = "OPR_O38"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OprO38Response](name="RESPONSE", optional=True, repeatable=False)

class OPU_R25(HL7Message):
    _structure_id = "OPU_R25"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=False)
    pv1 = HL7SegmentAttr[PV1](segment_id="PV1", optional=False, repeatable=False)
    pv2 = HL7SegmentAttr[PV2](segment_id="PV2", optional=True, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    patient_visit_observation = \
        HL7GroupAttr[OpuR25PatientVisitObservation](name="PATIENT_VISIT_OBSERVATION", optional=True, repeatable=True)
    accession_detail = \
        HL7GroupAttr[OpuR25AccessionDetail](name="ACCESSION_DETAIL", optional=False, repeatable=True)

class ORA_R33(HL7Message):
    _structure_id = "ORA_R33"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    order = \
        HL7GroupAttr[OraR33Order](name="ORDER", optional=True, repeatable=False)

class ORA_R41(HL7Message):
    _structure_id = "ORA_R41"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)

class ORB_O28(HL7Message):
    _structure_id = "ORB_O28"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrbO28Response](name="RESPONSE", optional=True, repeatable=False)

class ORD_O04(HL7Message):
    _structure_id = "ORD_O04"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrdO04Response](name="RESPONSE", optional=True, repeatable=False)

class ORG_O20(HL7Message):
    _structure_id = "ORG_O20"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrgO20Response](name="RESPONSE", optional=True, repeatable=False)

class ORI_O24(HL7Message):
    _structure_id = "ORI_O24"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OriO24Response](name="RESPONSE", optional=True, repeatable=False)

class ORL_O22(HL7Message):
    _structure_id = "ORL_O22"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrlO22Response](name="RESPONSE", optional=True, repeatable=False)

class ORL_O34(HL7Message):
    _structure_id = "ORL_O34"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrlO34Response](name="RESPONSE", optional=True, repeatable=False)

class ORL_O36(HL7Message):
    _structure_id = "ORL_O36"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrlO36Response](name="RESPONSE", optional=True, repeatable=False)

class ORL_O40(HL7Message):
    _structure_id = "ORL_O40"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrlO40Response](name="RESPONSE", optional=True, repeatable=False)

class ORL_O53(HL7Message):
    _structure_id = "ORL_O53"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrlO53Response](name="RESPONSE", optional=True, repeatable=False)

class ORL_O54(HL7Message):
    _structure_id = "ORL_O54"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrlO54Response](name="RESPONSE", optional=True, repeatable=False)

class ORL_O55(HL7Message):
    _structure_id = "ORL_O55"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrlO55Response](name="RESPONSE", optional=True, repeatable=False)

class ORL_O56(HL7Message):
    _structure_id = "ORL_O56"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrlO56Response](name="RESPONSE", optional=True, repeatable=False)

class ORN_O08(HL7Message):
    _structure_id = "ORN_O08"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrnO08Response](name="RESPONSE", optional=True, repeatable=False)

class ORP_O10(HL7Message):
    _structure_id = "ORP_O10"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrpO10Response](name="RESPONSE", optional=True, repeatable=False)

class ORS_O06(HL7Message):
    _structure_id = "ORS_O06"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrsO06Response](name="RESPONSE", optional=True, repeatable=False)

class ORU_R01(HL7Message):
    _structure_id = "ORU_R01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    patient_result = \
        HL7GroupAttr[OruR01PatientResult](name="PATIENT_RESULT", optional=False, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class ORU_R30(HL7Message):
    _structure_id = "ORU_R30"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    oh1 = HL7SegmentAttr[OH1](segment_id="OH1", optional=True, repeatable=True)
    oh2 = HL7SegmentAttr[OH2](segment_id="OH2", optional=True, repeatable=True)
    oh3 = HL7SegmentAttr[OH3](segment_id="OH3", optional=True, repeatable=False)
    oh4 = HL7SegmentAttr[OH4](segment_id="OH4", optional=True, repeatable=True)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    patient_observation = \
        HL7GroupAttr[OruR30PatientObservation](name="PATIENT_OBSERVATION", optional=True, repeatable=True)
    visit = \
        HL7GroupAttr[OruR30Visit](name="VISIT", optional=True, repeatable=False)
    orc = HL7SegmentAttr[ORC](segment_id="ORC", optional=False, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    obr = HL7SegmentAttr[OBR](segment_id="OBR", optional=False, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    timing_qty = \
        HL7GroupAttr[OruR30TimingQty](name="TIMING_QTY", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[OruR30Observation](name="OBSERVATION", optional=False, repeatable=True)
    device = \
        HL7GroupAttr[OruR30Device](name="DEVICE", optional=True, repeatable=True)

class ORX_O58(HL7Message):
    _structure_id = "ORX_O58"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[OrxO58Response](name="RESPONSE", optional=True, repeatable=False)

class OSM_R26(HL7Message):
    _structure_id = "OSM_R26"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    shipment = \
        HL7GroupAttr[OsmR26Shipment](name="SHIPMENT", optional=False, repeatable=True)

class OSU_O51(HL7Message):
    _structure_id = "OSU_O51"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=True, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    order_status = \
        HL7GroupAttr[OsuO51OrderStatus](name="ORDER_STATUS", optional=False, repeatable=True)

class OSU_O52(HL7Message):
    _structure_id = "OSU_O52"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[OsuO52Patient](name="PATIENT", optional=True, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    order_status = \
        HL7GroupAttr[OsuO52OrderStatus](name="ORDER_STATUS", optional=False, repeatable=True)

class OUL_R22(HL7Message):
    _structure_id = "OUL_R22"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=False)
    patient = \
        HL7GroupAttr[OulR22Patient](name="PATIENT", optional=True, repeatable=False)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    specimen = \
        HL7GroupAttr[OulR22Specimen](name="SPECIMEN", optional=False, repeatable=True)
    device = \
        HL7GroupAttr[OulR22Device](name="DEVICE", optional=True, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class OUL_R23(HL7Message):
    _structure_id = "OUL_R23"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=False)
    patient = \
        HL7GroupAttr[OulR23Patient](name="PATIENT", optional=True, repeatable=False)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    specimen = \
        HL7GroupAttr[OulR23Specimen](name="SPECIMEN", optional=False, repeatable=True)
    device = \
        HL7GroupAttr[OulR23Device](name="DEVICE", optional=True, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class OUL_R24(HL7Message):
    _structure_id = "OUL_R24"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=False)
    patient = \
        HL7GroupAttr[OulR24Patient](name="PATIENT", optional=True, repeatable=False)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    order = \
        HL7GroupAttr[OulR24Order](name="ORDER", optional=False, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class PEX_P07(HL7Message):
    _structure_id = "PEX_P07"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    visit = \
        HL7GroupAttr[PexP07Visit](name="VISIT", optional=True, repeatable=False)
    experience = \
        HL7GroupAttr[PexP07Experience](name="EXPERIENCE", optional=False, repeatable=True)

class PGL_PC6(HL7Message):
    _structure_id = "PGL_PC6"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    provider = \
        HL7GroupAttr[PglPc6Provider](name="PROVIDER", optional=False, repeatable=True)
    patient_visit = \
        HL7GroupAttr[PglPc6PatientVisit](name="PATIENT_VISIT", optional=True, repeatable=False)
    goal = \
        HL7GroupAttr[PglPc6Goal](name="GOAL", optional=False, repeatable=True)

class PMU_B01(HL7Message):
    _structure_id = "PMU_B01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    stf = HL7SegmentAttr[STF](segment_id="STF", optional=False, repeatable=False)
    pra = HL7SegmentAttr[PRA](segment_id="PRA", optional=True, repeatable=True)
    org = HL7SegmentAttr[ORG](segment_id="ORG", optional=True, repeatable=True)
    aff = HL7SegmentAttr[AFF](segment_id="AFF", optional=True, repeatable=True)
    lan = HL7SegmentAttr[LAN](segment_id="LAN", optional=True, repeatable=True)
    edu = HL7SegmentAttr[EDU](segment_id="EDU", optional=True, repeatable=True)
    cer = HL7SegmentAttr[CER](segment_id="CER", optional=True, repeatable=True)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=True)

class PMU_B03(HL7Message):
    _structure_id = "PMU_B03"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    stf = HL7SegmentAttr[STF](segment_id="STF", optional=False, repeatable=False)

class PMU_B04(HL7Message):
    _structure_id = "PMU_B04"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    stf = HL7SegmentAttr[STF](segment_id="STF", optional=False, repeatable=False)
    pra = HL7SegmentAttr[PRA](segment_id="PRA", optional=True, repeatable=True)
    org = HL7SegmentAttr[ORG](segment_id="ORG", optional=True, repeatable=True)

class PMU_B07(HL7Message):
    _structure_id = "PMU_B07"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    stf = HL7SegmentAttr[STF](segment_id="STF", optional=False, repeatable=False)
    pra = HL7SegmentAttr[PRA](segment_id="PRA", optional=True, repeatable=False)
    certificate = \
        HL7GroupAttr[PmuB07Certificate](name="CERTIFICATE", optional=True, repeatable=True)

class PMU_B08(HL7Message):
    _structure_id = "PMU_B08"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    evn = HL7SegmentAttr[EVN](segment_id="EVN", optional=False, repeatable=False)
    stf = HL7SegmentAttr[STF](segment_id="STF", optional=False, repeatable=False)
    pra = HL7SegmentAttr[PRA](segment_id="PRA", optional=True, repeatable=False)
    cer = HL7SegmentAttr[CER](segment_id="CER", optional=True, repeatable=True)

class PPG_PCG(HL7Message):
    _structure_id = "PPG_PCG"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    provider = \
        HL7GroupAttr[PpgPcgProvider](name="PROVIDER", optional=False, repeatable=True)
    patient_visit = \
        HL7GroupAttr[PpgPcgPatientVisit](name="PATIENT_VISIT", optional=True, repeatable=False)
    pathway = \
        HL7GroupAttr[PpgPcgPathway](name="PATHWAY", optional=False, repeatable=True)

class PPP_PCB(HL7Message):
    _structure_id = "PPP_PCB"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    provider = \
        HL7GroupAttr[PppPcbProvider](name="PROVIDER", optional=False, repeatable=True)
    patient_visit = \
        HL7GroupAttr[PppPcbPatientVisit](name="PATIENT_VISIT", optional=True, repeatable=False)
    pathway = \
        HL7GroupAttr[PppPcbPathway](name="PATHWAY", optional=False, repeatable=True)

class PPR_PC1(HL7Message):
    _structure_id = "PPR_PC1"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    provider = \
        HL7GroupAttr[PprPc1Provider](name="PROVIDER", optional=False, repeatable=True)
    patient_visit = \
        HL7GroupAttr[PprPc1PatientVisit](name="PATIENT_VISIT", optional=True, repeatable=False)
    problem = \
        HL7GroupAttr[PprPc1Problem](name="PROBLEM", optional=False, repeatable=True)

class QBP_E03(HL7Message):
    _structure_id = "QBP_E03"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=True)
    query_information = \
        HL7GroupAttr[QbpE03QueryInformation](name="QUERY_INFORMATION", optional=False, repeatable=False)

class QBP_E22(HL7Message):
    _structure_id = "QBP_E22"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=True)
    query = \
        HL7GroupAttr[QbpE22Query](name="QUERY", optional=False, repeatable=False)

class QBP_O33(HL7Message):
    _structure_id = "QBP_O33"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)

class QBP_O34(HL7Message):
    _structure_id = "QBP_O34"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)

class QBP_Q11(HL7Message):
    _structure_id = "QBP_Q11"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    qbp = \
        HL7GroupAttr[QbpQ11Qbp](name="QBP", optional=True, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class QBP_Q13(HL7Message):
    _structure_id = "QBP_Q13"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=True, repeatable=False)
    rdf = HL7SegmentAttr[RDF](segment_id="RDF", optional=True, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)
    rdf = HL7SegmentAttr[RDF](segment_id="RDF", optional=True, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class QBP_Q15(HL7Message):
    _structure_id = "QBP_Q15"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    any_hl7_segment = HL7SegmentAttr[anyHL7Segment](segment_id="anyHL7Segment", optional=True, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class QBP_Q21(HL7Message):
    _structure_id = "QBP_Q21"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class QBP_Qnn(HL7Message):
    _structure_id = "QBP_Qnn"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    rdf = HL7SegmentAttr[RDF](segment_id="RDF", optional=True, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class QBP_Z73(HL7Message):
    _structure_id = "QBP_Z73"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)

class QCN_J01(HL7Message):
    _structure_id = "QCN_J01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    qid = HL7SegmentAttr[QID](segment_id="QID", optional=False, repeatable=False)

class QSB_Q16(HL7Message):
    _structure_id = "QSB_Q16"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class QVR_Q17(HL7Message):
    _structure_id = "QVR_Q17"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    qbp = \
        HL7GroupAttr[QvrQ17Qbp](name="QBP", optional=True, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RAS_O17(HL7Message):
    _structure_id = "RAS_O17"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[RasO17Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[RasO17Order](name="ORDER", optional=False, repeatable=True)

class RCV_O59(HL7Message):
    _structure_id = "RCV_O59"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[RcvO59Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[RcvO59Order](name="ORDER", optional=False, repeatable=True)

class RDE_O11(HL7Message):
    _structure_id = "RDE_O11"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[RdeO11Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[RdeO11Order](name="ORDER", optional=False, repeatable=True)

class RDE_O49(HL7Message):
    _structure_id = "RDE_O49"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[RdeO49Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[RdeO49Order](name="ORDER", optional=False, repeatable=True)

class RDR_RDR(HL7Message):
    _structure_id = "RDR_RDR"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=False)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    definition = \
        HL7GroupAttr[RdrRdrDefinition](name="DEFINITION", optional=False, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RDS_O13(HL7Message):
    _structure_id = "RDS_O13"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[RdsO13Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[RdsO13Order](name="ORDER", optional=False, repeatable=True)

class RDY_K15(HL7Message):
    _structure_id = "RDY_K15"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    dsp = HL7SegmentAttr[DSP](segment_id="DSP", optional=True, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RDY_Z80(HL7Message):
    _structure_id = "RDY_Z80"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    dsp = HL7SegmentAttr[DSP](segment_id="DSP", optional=True, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class REF_I12(HL7Message):
    _structure_id = "REF_I12"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    rf1 = HL7SegmentAttr[RF1](segment_id="RF1", optional=True, repeatable=False)
    authorization_contact2 = \
        HL7GroupAttr[RefI12AuthorizationContact2](name="AUTHORIZATION_CONTACT2", optional=True, repeatable=False)
    provider_contact = \
        HL7GroupAttr[RefI12ProviderContact](name="PROVIDER_CONTACT", optional=False, repeatable=True)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    gt1 = HL7SegmentAttr[GT1](segment_id="GT1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[RefI12Insurance](name="INSURANCE", optional=True, repeatable=True)
    acc = HL7SegmentAttr[ACC](segment_id="ACC", optional=True, repeatable=False)
    dg1 = HL7SegmentAttr[DG1](segment_id="DG1", optional=True, repeatable=True)
    drg = HL7SegmentAttr[DRG](segment_id="DRG", optional=True, repeatable=True)
    al1 = HL7SegmentAttr[AL1](segment_id="AL1", optional=True, repeatable=True)
    procedure = \
        HL7GroupAttr[RefI12Procedure](name="PROCEDURE", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[RefI12Observation](name="OBSERVATION", optional=True, repeatable=True)
    patient_visit = \
        HL7GroupAttr[RefI12PatientVisit](name="PATIENT_VISIT", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)

class RGV_O15(HL7Message):
    _structure_id = "RGV_O15"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[RgvO15Patient](name="PATIENT", optional=True, repeatable=False)
    order = \
        HL7GroupAttr[RgvO15Order](name="ORDER", optional=False, repeatable=True)

class RPA_I08(HL7Message):
    _structure_id = "RPA_I08"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    rf1 = HL7SegmentAttr[RF1](segment_id="RF1", optional=True, repeatable=False)
    authorization = \
        HL7GroupAttr[RpaI08Authorization](name="AUTHORIZATION", optional=True, repeatable=False)
    provider = \
        HL7GroupAttr[RpaI08Provider](name="PROVIDER", optional=False, repeatable=True)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    gt1 = HL7SegmentAttr[GT1](segment_id="GT1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[RpaI08Insurance](name="INSURANCE", optional=True, repeatable=True)
    acc = HL7SegmentAttr[ACC](segment_id="ACC", optional=True, repeatable=False)
    dg1 = HL7SegmentAttr[DG1](segment_id="DG1", optional=True, repeatable=True)
    drg = HL7SegmentAttr[DRG](segment_id="DRG", optional=True, repeatable=True)
    al1 = HL7SegmentAttr[AL1](segment_id="AL1", optional=True, repeatable=True)
    procedure = \
        HL7GroupAttr[RpaI08Procedure](name="PROCEDURE", optional=False, repeatable=True)
    observation = \
        HL7GroupAttr[RpaI08Observation](name="OBSERVATION", optional=True, repeatable=True)
    visit = \
        HL7GroupAttr[RpaI08Visit](name="VISIT", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)

class RPI_I01(HL7Message):
    _structure_id = "RPI_I01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    provider = \
        HL7GroupAttr[RpiI01Provider](name="PROVIDER", optional=False, repeatable=True)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    guarantor_insurance = \
        HL7GroupAttr[RpiI01GuarantorInsurance](name="GUARANTOR_INSURANCE", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)

class RPI_I04(HL7Message):
    _structure_id = "RPI_I04"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    provider = \
        HL7GroupAttr[RpiI04Provider](name="PROVIDER", optional=False, repeatable=True)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    guarantor_insurance = \
        HL7GroupAttr[RpiI04GuarantorInsurance](name="GUARANTOR_INSURANCE", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)

class RPL_I02(HL7Message):
    _structure_id = "RPL_I02"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    provider = \
        HL7GroupAttr[RplI02Provider](name="PROVIDER", optional=False, repeatable=True)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    dsp = HL7SegmentAttr[DSP](segment_id="DSP", optional=True, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RPR_I03(HL7Message):
    _structure_id = "RPR_I03"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    provider = \
        HL7GroupAttr[RprI03Provider](name="PROVIDER", optional=False, repeatable=True)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=True, repeatable=True)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)

class RQA_I08(HL7Message):
    _structure_id = "RQA_I08"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    rf1 = HL7SegmentAttr[RF1](segment_id="RF1", optional=True, repeatable=False)
    authorization = \
        HL7GroupAttr[RqaI08Authorization](name="AUTHORIZATION", optional=True, repeatable=False)
    provider = \
        HL7GroupAttr[RqaI08Provider](name="PROVIDER", optional=False, repeatable=True)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    guarantor_insurance = \
        HL7GroupAttr[RqaI08GuarantorInsurance](name="GUARANTOR_INSURANCE", optional=True, repeatable=False)
    acc = HL7SegmentAttr[ACC](segment_id="ACC", optional=True, repeatable=False)
    dg1 = HL7SegmentAttr[DG1](segment_id="DG1", optional=True, repeatable=True)
    drg = HL7SegmentAttr[DRG](segment_id="DRG", optional=True, repeatable=True)
    al1 = HL7SegmentAttr[AL1](segment_id="AL1", optional=True, repeatable=True)
    procedure = \
        HL7GroupAttr[RqaI08Procedure](name="PROCEDURE", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[RqaI08Observation](name="OBSERVATION", optional=True, repeatable=True)
    visit = \
        HL7GroupAttr[RqaI08Visit](name="VISIT", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)

class RQI_I01(HL7Message):
    _structure_id = "RQI_I01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    provider = \
        HL7GroupAttr[RqiI01Provider](name="PROVIDER", optional=False, repeatable=True)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    guarantor_insurance = \
        HL7GroupAttr[RqiI01GuarantorInsurance](name="GUARANTOR_INSURANCE", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)

class RQP_I04(HL7Message):
    _structure_id = "RQP_I04"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    provider = \
        HL7GroupAttr[RqpI04Provider](name="PROVIDER", optional=False, repeatable=True)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    gt1 = HL7SegmentAttr[GT1](segment_id="GT1", optional=True, repeatable=True)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)

class RRA_O18(HL7Message):
    _structure_id = "RRA_O18"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[RraO18Response](name="RESPONSE", optional=True, repeatable=False)

class RRD_O14(HL7Message):
    _structure_id = "RRD_O14"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[RrdO14Response](name="RESPONSE", optional=True, repeatable=False)

class RRE_O12(HL7Message):
    _structure_id = "RRE_O12"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[RreO12Response](name="RESPONSE", optional=True, repeatable=False)

class RRE_O50(HL7Message):
    _structure_id = "RRE_O50"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[RreO50Response](name="RESPONSE", optional=True, repeatable=False)

class RRG_O16(HL7Message):
    _structure_id = "RRG_O16"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    response = \
        HL7GroupAttr[RrgO16Response](name="RESPONSE", optional=True, repeatable=False)

class RRI_I12(HL7Message):
    _structure_id = "RRI_I12"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=True, repeatable=False)
    rf1 = HL7SegmentAttr[RF1](segment_id="RF1", optional=True, repeatable=False)
    authorization_contact2 = \
        HL7GroupAttr[RriI12AuthorizationContact2](name="AUTHORIZATION_CONTACT2", optional=True, repeatable=False)
    provider_contact = \
        HL7GroupAttr[RriI12ProviderContact](name="PROVIDER_CONTACT", optional=False, repeatable=True)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    acc = HL7SegmentAttr[ACC](segment_id="ACC", optional=True, repeatable=False)
    dg1 = HL7SegmentAttr[DG1](segment_id="DG1", optional=True, repeatable=True)
    drg = HL7SegmentAttr[DRG](segment_id="DRG", optional=True, repeatable=True)
    al1 = HL7SegmentAttr[AL1](segment_id="AL1", optional=True, repeatable=True)
    procedure = \
        HL7GroupAttr[RriI12Procedure](name="PROCEDURE", optional=True, repeatable=True)
    observation = \
        HL7GroupAttr[RriI12Observation](name="OBSERVATION", optional=True, repeatable=True)
    patient_visit = \
        HL7GroupAttr[RriI12PatientVisit](name="PATIENT_VISIT", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)

class RSP_E03(HL7Message):
    _structure_id = "RSP_E03"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    query_ack_ipr = \
        HL7GroupAttr[RspE03QueryAckIpr](name="QUERY_ACK_IPR", optional=False, repeatable=False)

class RSP_E22(HL7Message):
    _structure_id = "RSP_E22"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    query_ack = \
        HL7GroupAttr[RspE22QueryAck](name="QUERY_ACK", optional=False, repeatable=False)

class RSP_K11(HL7Message):
    _structure_id = "RSP_K11"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    segment_pattern = \
        HL7GroupAttr[RspK11SegmentPattern](name="SEGMENT_PATTERN", optional=True, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RSP_K21(HL7Message):
    _structure_id = "RSP_K21"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    query_response = \
        HL7GroupAttr[RspK21QueryResponse](name="QUERY_RESPONSE", optional=True, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RSP_K22(HL7Message):
    _structure_id = "RSP_K22"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    query_response = \
        HL7GroupAttr[RspK22QueryResponse](name="QUERY_RESPONSE", optional=True, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RSP_K23(HL7Message):
    _structure_id = "RSP_K23"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    query_response = \
        HL7GroupAttr[RspK23QueryResponse](name="QUERY_RESPONSE", optional=True, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RSP_K25(HL7Message):
    _structure_id = "RSP_K25"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)
    staff = \
        HL7GroupAttr[RspK25Staff](name="STAFF", optional=False, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RSP_K31(HL7Message):
    _structure_id = "RSP_K31"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)
    response = \
        HL7GroupAttr[RspK31Response](name="RESPONSE", optional=False, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RSP_K32(HL7Message):
    _structure_id = "RSP_K32"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    query_response = \
        HL7GroupAttr[RspK32QueryResponse](name="QUERY_RESPONSE", optional=True, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RSP_O33(HL7Message):
    _structure_id = "RSP_O33"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    donor = \
        HL7GroupAttr[RspO33Donor](name="DONOR", optional=True, repeatable=False)

class RSP_O34(HL7Message):
    _structure_id = "RSP_O34"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    donor = \
        HL7GroupAttr[RspO34Donor](name="DONOR", optional=True, repeatable=False)
    donation = \
        HL7GroupAttr[RspO34Donation](name="DONATION", optional=True, repeatable=False)

class RSP_Z82(HL7Message):
    _structure_id = "RSP_Z82"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)
    query_response = \
        HL7GroupAttr[RspZ82QueryResponse](name="QUERY_RESPONSE", optional=False, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RSP_Z84(HL7Message):
    _structure_id = "RSP_Z84"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    row_definition = \
        HL7GroupAttr[RspZ84RowDefinition](name="ROW_DEFINITION", optional=True, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RSP_Z86(HL7Message):
    _structure_id = "RSP_Z86"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    query_response = \
        HL7GroupAttr[RspZ86QueryResponse](name="QUERY_RESPONSE", optional=False, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RSP_Z88(HL7Message):
    _structure_id = "RSP_Z88"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)
    query_response = \
        HL7GroupAttr[RspZ88QueryResponse](name="QUERY_RESPONSE", optional=False, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=False, repeatable=False)

class RSP_Z90(HL7Message):
    _structure_id = "RSP_Z90"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    rcp = HL7SegmentAttr[RCP](segment_id="RCP", optional=False, repeatable=False)
    query_response = \
        HL7GroupAttr[RspZ90QueryResponse](name="QUERY_RESPONSE", optional=False, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=False, repeatable=False)

class RSP_Znn(HL7Message):
    _structure_id = "RSP_Znn"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    any_hl7_segment = HL7SegmentAttr[anyHL7Segment](segment_id="anyHL7Segment", optional=True, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RTB_K13(HL7Message):
    _structure_id = "RTB_K13"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    row_definition = \
        HL7GroupAttr[RtbK13RowDefinition](name="ROW_DEFINITION", optional=True, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RTB_Knn(HL7Message):
    _structure_id = "RTB_Knn"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    any_hl7_segment = HL7SegmentAttr[anyHL7Segment](segment_id="anyHL7Segment", optional=False, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class RTB_Z74(HL7Message):
    _structure_id = "RTB_Z74"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    qak = HL7SegmentAttr[QAK](segment_id="QAK", optional=False, repeatable=False)
    qpd = HL7SegmentAttr[QPD](segment_id="QPD", optional=False, repeatable=False)
    row_definition = \
        HL7GroupAttr[RtbZ74RowDefinition](name="ROW_DEFINITION", optional=True, repeatable=False)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class SDR_S31(HL7Message):
    _structure_id = "SDR_S31"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    anti_microbial_device_data = \
        HL7GroupAttr[SdrS31AntiMicrobialDeviceData](name="ANTI-MICROBIAL_DEVICE_DATA", optional=False, repeatable=False)

class SDR_S32(HL7Message):
    _structure_id = "SDR_S32"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    anti_microbial_device_cycle_data = \
        HL7GroupAttr[SdrS32AntiMicrobialDeviceCycleData](name="ANTI-MICROBIAL_DEVICE_CYCLE_DATA", optional=False, repeatable=False)

class SIU_S12(HL7Message):
    _structure_id = "SIU_S12"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sch = HL7SegmentAttr[SCH](segment_id="SCH", optional=False, repeatable=False)
    tq1 = HL7SegmentAttr[TQ1](segment_id="TQ1", optional=True, repeatable=True)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[SiuS12Patient](name="PATIENT", optional=True, repeatable=True)
    resources = \
        HL7GroupAttr[SiuS12Resources](name="RESOURCES", optional=False, repeatable=True)

class SLR_S28(HL7Message):
    _structure_id = "SLR_S28"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    slt = HL7SegmentAttr[SLT](segment_id="SLT", optional=False, repeatable=True)

class SRM_S01(HL7Message):
    _structure_id = "SRM_S01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    arq = HL7SegmentAttr[ARQ](segment_id="ARQ", optional=False, repeatable=False)
    apr = HL7SegmentAttr[APR](segment_id="APR", optional=True, repeatable=False)
    nte = HL7SegmentAttr[NTE](segment_id="NTE", optional=True, repeatable=True)
    patient = \
        HL7GroupAttr[SrmS01Patient](name="PATIENT", optional=True, repeatable=True)
    resources = \
        HL7GroupAttr[SrmS01Resources](name="RESOURCES", optional=False, repeatable=True)

class SRR_S01(HL7Message):
    _structure_id = "SRR_S01"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    msa = HL7SegmentAttr[MSA](segment_id="MSA", optional=False, repeatable=False)
    err = HL7SegmentAttr[ERR](segment_id="ERR", optional=True, repeatable=True)
    schedule = \
        HL7GroupAttr[SrrS01Schedule](name="SCHEDULE", optional=True, repeatable=False)

class SSR_U04(HL7Message):
    _structure_id = "SSR_U04"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    equ = HL7SegmentAttr[EQU](segment_id="EQU", optional=False, repeatable=False)
    specimen_container = \
        HL7GroupAttr[SsrU04SpecimenContainer](name="SPECIMEN_CONTAINER", optional=False, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=False)

class SSU_U03(HL7Message):
    _structure_id = "SSU_U03"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    equ = HL7SegmentAttr[EQU](segment_id="EQU", optional=False, repeatable=False)
    specimen_container = \
        HL7GroupAttr[SsuU03SpecimenContainer](name="SPECIMEN_CONTAINER", optional=False, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=False)

class STC_S33(HL7Message):
    _structure_id = "STC_S33"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    scp = HL7SegmentAttr[SCP](segment_id="SCP", optional=False, repeatable=True)

class TCU_U10(HL7Message):
    _structure_id = "TCU_U10"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    equ = HL7SegmentAttr[EQU](segment_id="EQU", optional=False, repeatable=False)
    test_configuration = \
        HL7GroupAttr[TcuU10TestConfiguration](name="TEST_CONFIGURATION", optional=False, repeatable=True)
    rol = HL7SegmentAttr[ROL](segment_id="ROL", optional=True, repeatable=False)

class UDM_Q05(HL7Message):
    _structure_id = "UDM_Q05"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    urd = HL7SegmentAttr[URD](segment_id="URD", optional=False, repeatable=False)
    urs = HL7SegmentAttr[URS](segment_id="URS", optional=True, repeatable=False)
    dsp = HL7SegmentAttr[DSP](segment_id="DSP", optional=False, repeatable=True)
    dsc = HL7SegmentAttr[DSC](segment_id="DSC", optional=True, repeatable=False)

class VXU_V04(HL7Message):
    _structure_id = "VXU_V04"

    msh = HL7SegmentAttr[MSH](segment_id="MSH", optional=False, repeatable=False)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    sft = HL7SegmentAttr[SFT](segment_id="SFT", optional=True, repeatable=True)
    uac = HL7SegmentAttr[UAC](segment_id="UAC", optional=True, repeatable=False)
    pid = HL7SegmentAttr[PID](segment_id="PID", optional=False, repeatable=False)
    pd1 = HL7SegmentAttr[PD1](segment_id="PD1", optional=True, repeatable=False)
    prt = HL7SegmentAttr[PRT](segment_id="PRT", optional=True, repeatable=True)
    nk1 = HL7SegmentAttr[NK1](segment_id="NK1", optional=True, repeatable=True)
    arv = HL7SegmentAttr[ARV](segment_id="ARV", optional=True, repeatable=True)
    patient_visit = \
        HL7GroupAttr[VxuV04PatientVisit](name="PATIENT_VISIT", optional=True, repeatable=False)
    gt1 = HL7SegmentAttr[GT1](segment_id="GT1", optional=True, repeatable=True)
    insurance = \
        HL7GroupAttr[VxuV04Insurance](name="INSURANCE", optional=True, repeatable=True)
    person_observation = \
        HL7GroupAttr[VxuV04PersonObservation](name="PERSON_OBSERVATION", optional=True, repeatable=True)
    order = \
        HL7GroupAttr[VxuV04Order](name="ORDER", optional=True, repeatable=True)

