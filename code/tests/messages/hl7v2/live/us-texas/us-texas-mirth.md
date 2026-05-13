# Mirth Connect (NextGen) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Emergency admission for stroke

```
MSH|^~\&|MIRTH|PARKLAND^2.16.840.1.113883.3.3301^ISO|ADT_RECV|TX_HIE|20260405102000||ADT^A01^ADT_A01|MIRTH20260405102000001|P|2.5.1|||AL|NE
EVN|A01|20260405101500|||EDRN^Ashmore^Danielle^P^^^RN|20260405101500
PID|1||MRN40001^^^PARKLAND^MR~831-47-6290^^^USSSA^SS||Coronado^Rafael^Emilio^^Mr.^||19670811|M||2106-3^White^CDCREC|1818 Medical District Dr^^Dallas^TX^75235^US^H||^PRN^PH^^1^214^5559876|||M^Married^HL70002|||831-47-6290|||H^Hispanic or Latino^CDCREC
PD1|||Parkland Memorial Hospital^^^^NPI|1234567001^Sterling^Kathleen^M^^^MD^^^^NPI
NK1|1|Coronado^Marisol^Adriana^^Mrs.|SPO^Spouse^HL70063|1818 Medical District Dr^^Dallas^TX^75235^US|^PRN^PH^^1^214^5559877||EC^Emergency Contact^HL70131
PV1|1|E|NEURO^5101^01^PARKLAND^^^^N|E^Emergency^HL70007|||2345678002^Winslow^David^L^^^MD^^^^NPI|3456789003^Hartwell^Jennifer^S^^^MD^^^^NPI|NEU^Neurology^HL70069||||||A^Accident^HL70007|||||VN20260405001^^^PARKLAND^VN|||||||||||||||||||||||||20260405101500
PV2|||^Acute left-sided weakness, slurred speech, facial droop
DG1|1||I63.9^Cerebral infarction unspecified^I10||20260405|A
GT1|1||Coronado^Rafael^Emilio^^Mr.||1818 Medical District Dr^^Dallas^TX^75235^US|^PRN^PH^^1^214^5559876|||||SE^Self^HL70063
IN1|1|MCARE001|00451^Medicare|Centers for Medicare^^Baltimore^MD^21244|||||MCAREGRP||||||Coronado^Rafael^Emilio|SE^Self^HL70063|19670811|1818 Medical District Dr^^Dallas^TX^75235^US|Y||1||||||||||||||MCAREPOL345678
```

---

## 2. ORU^R01 - Troponin and cardiac markers results

```
MSH|^~\&|MIRTH|METHODIST_SA^2.16.840.1.113883.3.3302^ISO|LAB_RECV|TX_HIE|20260406143000||ORU^R01^ORU_R01|MIRTH20260406143000002|P|2.5.1|||AL|NE
PID|1||MRN40002^^^METHODIST_SA^MR||Abernathy^Donna^Christine^^Mrs.^||19550630|F||2106-3^White^CDCREC|7700 Floyd Curl Dr^^San Antonio^TX^78229^US^H||^PRN^PH^^1^210^5553412|||W^Widowed^HL70002|||614-28-7753^^^USSSA^SS|||N^Not Hispanic or Latino^CDCREC
PV1|1|E|ED^0001^T4^METHODIST_SA^^^^N|E^Emergency^HL70007|||4567890004^Culpepper^Carlos^A^^^MD^^^^NPI||EM^Emergency Medicine^HL70069||||||||||VN20260406002^^^METHODIST_SA^VN
ORC|RE|ORD40002^MIRTH|FIL40002^LAB||CM^Complete^HL70038|||20260406120000|||4567890004^Culpepper^Carlos^A^^^MD^^^^NPI
OBR|1|ORD40002^MIRTH|FIL40002^LAB|49563-0^Cardiac biomarkers panel^LN|||20260406120000|||||||||4567890004^Culpepper^Carlos^A^^^MD^^^^NPI||||||20260406140000|||F
OBX|1|NM|6598-7^Troponin T cardiac [Mass/volume] in Serum or Plasma^LN||0.04|ng/mL^nanograms per milliliter^UCUM|<0.01|H|||F|||20260406140000
OBX|2|NM|33762-6^Natriuretic peptide.B prohormone N-Terminal^LN||456|pg/mL^picograms per milliliter^UCUM|<125|H|||F|||20260406140000
OBX|3|NM|2157-6^Creatine kinase [Enzymatic activity/volume] in Serum or Plasma^LN||180|U/L^units per liter^UCUM|30-200|N|||F|||20260406140000
OBX|4|NM|13969-1^Creatine kinase.MB [Mass/volume] in Serum or Plasma^LN||5.2|ng/mL^nanograms per milliliter^UCUM|0.0-6.3|N|||F|||20260406140000
OBX|5|NM|30313-1^Hemoglobin [Mass/volume] in Blood^LN||11.8|g/dL^grams per deciliter^UCUM|12.0-16.0|L|||F|||20260406140000
```

---

## 3. ADT^A03 - Discharge from pediatric unit

```
MSH|^~\&|MIRTH|COOKCH^2.16.840.1.113883.3.3303^ISO|ADT_RECV|TX_HIE|20260407161500||ADT^A03^ADT_A03|MIRTH20260407161500003|P|2.5.1|||AL|NE
EVN|A03|20260407160000|||PEDRN^Kingsley^Brittany^L^^^RN|20260407160000
PID|1||MRN40003^^^COOKCH^MR||Granados^Sofia^Valentina^^Miss^||20180302|F||2106-3^White^CDCREC|3500 W Illinois Ave^^Dallas^TX^75211^US^H||^PRN^PH^^1^214^5554893|||S^Single^HL70002||||||H^Hispanic or Latino^CDCREC
NK1|1|Granados^Hector^Antonio^^Mr.|FTH^Father^HL70063|3500 W Illinois Ave^^Dallas^TX^75211^US|^PRN^PH^^1^214^5554894||EC^Emergency Contact^HL70131
NK1|2|Granados^Claudia^Maria^^Mrs.|MTH^Mother^HL70063|3500 W Illinois Ave^^Dallas^TX^75211^US|^PRN^PH^^1^214^5554893||EC^Emergency Contact^HL70131
PV1|1|I|PED^2101^01^COOKCH^^^^N|U^Urgent^HL70007|||5678901005^Hartwell^Rachel^K^^^MD^^^^NPI||PED^Pediatrics^HL70069||||||R^Referral^HL70007|||||VN20260405003^^^COOKCH^VN|||||||||||||||||||01^Discharged to home^HL70112||||20260405120000|20260407160000
DG1|1||J21.0^Acute bronchiolitis due to respiratory syncytial virus^I10||20260405|A
```

---

## 4. ORM^O01 - Ultrasound pelvis order

```
MSH|^~\&|MIRTH|PARKLAND^2.16.840.1.113883.3.3301^ISO|RAD_RECV|TX_HIE|20260408091000||ORM^O01^ORM_O01|MIRTH20260408091000004|P|2.5.1|||AL|NE
PID|1||MRN40004^^^PARKLAND^MR||Hightower^Crystal^Denise^^Ms.^||19910415|F||2054-5^Black or African American^CDCREC|2909 Lemmon Ave^^Dallas^TX^75204^US^H||^PRN^PH^^1^469^5558271|||S^Single^HL70002|||742-53-8196|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|OBG^0003^01^PARKLAND^^^^N|R^Routine^HL70007|||6789012006^Ashmore^Lisa^A^^^MD^^^^NPI||OBG^Obstetrics and Gynecology^HL70069||||||||||VN20260408004^^^PARKLAND^VN
ORC|NW|ORD40004^MIRTH||GRP40004^MIRTH|||||20260408090000|||6789012006^Ashmore^Lisa^A^^^MD^^^^NPI|||||PARKLAND^Parkland Memorial Hospital
OBR|1|ORD40004^MIRTH||76856^Ultrasound pelvis complete^CPT4|||20260408090000||||||||6789012006^Ashmore^Lisa^A^^^MD^^^^NPI||||||||||1^Routine^HL70065
DG1|1||N92.1^Excessive and frequent menstruation with irregular cycle^I10||20260408|A
NTE|1||Evaluate for fibroids. Patient reports heavy irregular menses for 4 months.
```

---

## 5. ORU^R01 - EKG report with embedded PDF (ED datatype)

```
MSH|^~\&|MIRTH|METHODIST_SA^2.16.840.1.113883.3.3302^ISO|CARD_RECV|TX_HIE|20260409110000||ORU^R01^ORU_R01|MIRTH20260409110000005|P|2.5.1|||AL|NE
PID|1||MRN40005^^^METHODIST_SA^MR||Caldwell^George^Raymond^^Mr.^||19490320|M||2106-3^White^CDCREC|123 E Houston St^^San Antonio^TX^78205^US^H||^PRN^PH^^1^210^5556789|||M^Married^HL70002|||518-64-9302|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|CARD^0004^01^METHODIST_SA^^^^N|R^Routine^HL70007|||7890123007^Kingsley^Steven^T^^^MD^^^^NPI||CAR^Cardiology^HL70069||||||||||VN20260409005^^^METHODIST_SA^VN
ORC|RE|ORD40005^MIRTH|FIL40005^CARD||CM^Complete^HL70038|||20260409090000|||7890123007^Kingsley^Steven^T^^^MD^^^^NPI
OBR|1|ORD40005^MIRTH|FIL40005^CARD|93000^Electrocardiogram routine^CPT4|||20260409090000|||||||||7890123007^Kingsley^Steven^T^^^MD^^^^NPI||||||20260409105000|||F
OBX|1|FT|93000^EKG interpretation^L||Rate: 72 bpm\.br\Rhythm: Normal sinus rhythm\.br\Axis: Normal\.br\Intervals: PR 168ms, QRS 88ms, QTc 420ms\.br\ST/T changes: None\.br\Impression: Normal ECG||||||F|||20260409105000
OBX|2|ED|PDF^EKG Tracing^AUSPDI||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgODQyIDU5NV0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxMDIKPj4Kc3RyZWFtCkJUCi9GMSAxNCBUZgoxMDAgNTUwIFRkCihFS0cgVHJhY2luZyAtIDEyIExlYWQpIFRqCjAgLTIwIFRkCi9GMSAxMCBUZgooUGF0aWVudDogQ2FsZHdlbGwsIEdlb3JnZSkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago=||||||F|||20260409105000
```

---

## 6. ADT^A08 - Attending physician change

```
MSH|^~\&|MIRTH|COOKCH^2.16.840.1.113883.3.3303^ISO|ADT_RECV|TX_HIE|20260410090000||ADT^A08^ADT_A01|MIRTH20260410090000006|P|2.5.1|||AL|NE
EVN|A08|20260410085500|||CHNURSE^Winslow^Emily^R^^^RN|20260410085500
PID|1||MRN40006^^^COOKCH^MR||Luevano^Diego^Alejandro^^Master^||20150822|M||2106-3^White^CDCREC|4100 W Clarendon Dr^^Dallas^TX^75211^US^H||^PRN^PH^^1^214^5553291|||S^Single^HL70002||||||H^Hispanic or Latino^CDCREC
NK1|1|Luevano^Rosa^Patricia^^Mrs.|MTH^Mother^HL70063|4100 W Clarendon Dr^^Dallas^TX^75211^US|^PRN^PH^^1^214^5553291||EC^Emergency Contact^HL70131
PV1|1|I|PED^3105^01^COOKCH^^^^N|U^Urgent^HL70007|||8901234008^Sterling^James^R^^^MD^^^^NPI||PED^Pediatrics^HL70069||||||||||VN20260408006^^^COOKCH^VN
```

---

## 7. SIU^S12 - Physical therapy appointment scheduling

```
MSH|^~\&|MIRTH|PARKLAND^2.16.840.1.113883.3.3301^ISO|SCHED_RECV|TX_HIE|20260411140000||SIU^S12^SIU_S12|MIRTH20260411140000007|P|2.5.1|||AL|NE
SCH|APPT40007^MIRTH||||||PT^Physical Therapy Evaluation^L|45^MIN|MIN^Minutes^ISO+|^^^20260416100000^^45^MIN|||||9012345009^Culpepper^Catherine^L^^^DPT^^^^NPI|^PRN^PH^^1^214^5558700|||||9012345009^Culpepper^Catherine^L^^^DPT^^^^NPI|||||Booked
PID|1||MRN40007^^^PARKLAND^MR||Dunlap^James^Colton^^Mr.^||19750113|M||2106-3^White^CDCREC|5522 La Sierra Dr^^Dallas^TX^75231^US^H||^PRN^PH^^1^469^5554567|||M^Married^HL70002|||293-58-4107|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|PT^0002^01^PARKLAND^^^^N|R^Routine^HL70007|||9012345009^Culpepper^Catherine^L^^^DPT^^^^NPI||PT^Physical Therapy^HL70069||||||||||VN20260411007^^^PARKLAND^VN
RGS|1||PT_REHAB
AIS|1||97161^Physical therapy evaluation low complexity^CPT4|20260416100000|||45^MIN|MIN^Minutes^ISO+||Confirmed
AIG|1||9012345009^Culpepper^Catherine^L^^^DPT^^^^NPI|||||20260416100000|||45^MIN
AIL|1||PT^0002^01^PARKLAND|||||20260416100000|||45^MIN
NTE|1||Post-ACL reconstruction, 6 weeks post-op. Begin outpatient rehabilitation.
```

---

## 8. RDE^O11 - Warfarin anticoagulation order

```
MSH|^~\&|MIRTH|METHODIST_SA^2.16.840.1.113883.3.3302^ISO|PHARM_RECV|TX_HIE|20260412110000||RDE^O11^RDE_O11|MIRTH20260412110000008|P|2.5.1|||AL|NE
PID|1||MRN40008^^^METHODIST_SA^MR||Enfield^Martha^Diane^^Mrs.^||19460512|F||2106-3^White^CDCREC|8400 Datapoint Dr^^San Antonio^TX^78229^US^H||^PRN^PH^^1^210^5552345|||W^Widowed^HL70002|||385-71-2604|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|CARD^3201^01^METHODIST_SA^^^^N|U^Urgent^HL70007|||0123456010^Hartwell^Brian^P^^^MD^^^^NPI||CAR^Cardiology^HL70069||||||||||VN20260411008^^^METHODIST_SA^VN
ORC|NW|ORD40008^MIRTH||GRP40008^MIRTH|||||20260412103000|||0123456010^Hartwell^Brian^P^^^MD^^^^NPI
RXE|1^QD^HL70335|11289^Warfarin 5mg tablet^NDC|5|5|mg^milligrams^ISO+|TAB^Tablet^HL70292|||||30|EA^each^ISO+||0123456010^Hartwell^Brian^P^^^MD^^^^NPI|||||||||||||0^No Refills
RXR|PO^Oral^HL70162
DG1|1||I48.91^Unspecified atrial fibrillation^I10||20260411|A
NTE|1||Target INR 2.0-3.0. Baseline INR 1.1. First dose tonight at 1800.
```

---

## 9. MDM^T02 - Emergency department H and P document

```
MSH|^~\&|MIRTH|PARKLAND^2.16.840.1.113883.3.3301^ISO|DOC_RECV|TX_HIE|20260413200000||MDM^T02^MDM_T02|MIRTH20260413200000009|P|2.5.1|||AL|NE
EVN|T02|20260413195500
PID|1||MRN40009^^^PARKLAND^MR||Trinh^Khoa^Minh^^Mr.^||19830401|M||2028-9^Asian^CDCREC|2710 N Stemmons Fwy^^Dallas^TX^75207^US^H||^PRN^PH^^1^214^5551789|||M^Married^HL70002|||406-82-9153|||N^Not Hispanic or Latino^CDCREC
PV1|1|E|ED^0001^T12^PARKLAND^^^^N|E^Emergency^HL70007|||1234560011^Ashmore^Amanda^J^^^MD^^^^NPI||EM^Emergency Medicine^HL70069||||||||||VN20260413009^^^PARKLAND^VN
TXA|1|HP^History and Physical^HL70270|TX^Text^HL70191||20260413195000||||||DOC40009^PARKLAND|||||AU^Authenticated^HL70271
OBX|1|TX|11492-6^History and physical note^LN||HISTORY AND PHYSICAL\.br\Patient: Trinh, Khoa Minh\.br\DOB: 04/01/1983\.br\\.br\CHIEF COMPLAINT: Severe epigastric pain radiating to back for 6 hours\.br\\.br\HPI: 43 year old male presenting with acute onset epigastric pain radiating to the back, associated with nausea and vomiting. Pain rated 9/10. Denies fever, diarrhea, hematemesis. Reports heavy alcohol use over the weekend.\.br\\.br\EXAM: T 37.8, HR 110, BP 148/92, RR 22, SpO2 97% RA\.br\Abdomen: Tender epigastrium with guarding, decreased bowel sounds\.br\\.br\ASSESSMENT: Acute pancreatitis, likely alcohol-induced\.br\PLAN: NPO, IV fluids, pain management, lipase and CBC||||||F|||20260413195000
```

---

## 10. DFT^P03 - Outpatient radiology charges

```
MSH|^~\&|MIRTH|METHODIST_SA^2.16.840.1.113883.3.3302^ISO|FIN_RECV|TX_HIE|20260414150000||DFT^P03^DFT_P03|MIRTH20260414150000010|P|2.5.1|||AL|NE
EVN|P03|20260414145500
PID|1||MRN40010^^^METHODIST_SA^MR||Pineda^Lucia^Carmen^^Mrs.^||19720908|F||2106-3^White^CDCREC|5150 Broadway St^^San Antonio^TX^78209^US^H||^PRN^PH^^1^210^5558901|||M^Married^HL70002|||627-39-8401|||H^Hispanic or Latino^CDCREC
PV1|1|O|RAD^0003^01^METHODIST_SA^^^^N|R^Routine^HL70007|||2345670012^Winslow^Philip^C^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260414010^^^METHODIST_SA^VN
FT1|1|||20260414100000|20260414100000|CG^Charge^HL70017|77067^Screening mammography bilateral^CPT4||1|||||||RAD^0003^01^METHODIST_SA|||||2345670012^Winslow^Philip^C^^^MD^^^^NPI
FT1|2|||20260414100000|20260414100000|CG^Charge^HL70017|77063^Screening digital breast tomosynthesis bilateral^CPT4||1|||||||RAD^0003^01^METHODIST_SA
DG1|1||Z12.31^Encounter for screening mammogram for malignant neoplasm of breast^I10||20260414|A
```

---

## 11. VXU^V04 - COVID-19 booster vaccination

```
MSH|^~\&|MIRTH|PARKLAND^2.16.840.1.113883.3.3301^ISO|IMMTRAC2|TX_DSHS|20260415100000||VXU^V04^VXU_V04|MIRTH20260415100000011|P|2.5.1|||ER|AL
PID|1||MRN40011^^^PARKLAND^MR||Gifford^Sandra^Lynn^^Mrs.^||19640220|F||2106-3^White^CDCREC|6411 Mockingbird Ln^^Dallas^TX^75214^US^H||^PRN^PH^^1^214^5557890|||M^Married^HL70002|||753-90-1482|||N^Not Hispanic or Latino^CDCREC
PD1||||3456780013^Culpepper^Timothy^M^^^MD^^^^NPI
PV1|1|O|CLI^0005^01^PARKLAND^^^^N|R^Routine^HL70007|||3456780013^Culpepper^Timothy^M^^^MD^^^^NPI||FM^Family Medicine^HL70069||||||||||VN20260415011^^^PARKLAND^VN
ORC|RE|ORD40011^MIRTH||GRP40011^MIRTH|CM^Complete^HL70038|||20260415094000|||3456780013^Culpepper^Timothy^M^^^MD^^^^NPI
RXA|0|1|20260415094000||308^COVID-19 mRNA bivalent Pfizer^CVX|0.3|mL^milliliters^ISO+||00^New immunization record^NIP001||||||00069-2100-01^^NDC|||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|LD^Left Deltoid^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V01^Not VFC eligible^HL70064||||||F
OBX|2|TS|29768-9^Date vaccine information statement published^LN||20231013||||||F
OBX|3|TS|29769-7^Date vaccine information statement presented^LN||20260415||||||F
```

---

## 12. ADT^A04 - Urgent care registration

```
MSH|^~\&|MIRTH|COOKCH^2.16.840.1.113883.3.3303^ISO|ADT_RECV|TX_HIE|20260416180000||ADT^A04^ADT_A01|MIRTH20260416180000012|P|2.5.1|||AL|NE
EVN|A04|20260416175500|||TRIAGE^Kingsley^Nicole^J^^^RN|20260416175500
PID|1||MRN40012^^^COOKCH^MR||Ochoa^Isabella^Renata^^Miss^||20120715|F||2106-3^White^CDCREC|2200 W Commerce St^^Fort Worth^TX^76102^US^H||^PRN^PH^^1^817^5552345|||S^Single^HL70002||||||H^Hispanic or Latino^CDCREC
NK1|1|Ochoa^Ernesto^Manuel^^Mr.|FTH^Father^HL70063|2200 W Commerce St^^Fort Worth^TX^76102^US|^PRN^PH^^1^817^5552345||EC^Emergency Contact^HL70131
PV1|1|E|UC^0001^01^COOKCH^^^^N|U^Urgent^HL70007|||4567890014^Sterling^Maria^R^^^MD^^^^NPI||PED^Pediatrics^HL70069||||||||||VN20260416012^^^COOKCH^VN
PV2|||^High fever 104F, earache, irritability|||||||||||||||||||2^Emergent^HL70217
DG1|1||H66.91^Otitis media unspecified right ear^I10||20260416|A
```

---

## 13. ADT^A28 - New patient pre-registration

```
MSH|^~\&|MIRTH|METHODIST_SA^2.16.840.1.113883.3.3302^ISO|MPI_RECV|TX_HIE|20260417100000||ADT^A28^ADT_A05|MIRTH20260417100000013|P|2.5.1|||AL|NE
EVN|A28|20260417095500
PID|1||MRN40013^^^METHODIST_SA^MR~502-81-6347^^^USSSA^SS||Uddin^Fatima^Zahra^^Mrs.^||19870615|F||2106-3^White^CDCREC|9800 Fredericksburg Rd^^San Antonio^TX^78240^US^H||^PRN^PH^^1^210^5554567|^WPN^PH^^1^210^5559876||M^Married^HL70002|||502-81-6347|||N^Not Hispanic or Latino^CDCREC
PD1|||Methodist Hospital San Antonio^^^^NPI|5678900015^Hartwell^Angela^M^^^MD^^^^NPI
NK1|1|Uddin^Tariq^Hassan^^Mr.|SPO^Spouse^HL70063|9800 Fredericksburg Rd^^San Antonio^TX^78240^US|^PRN^PH^^1^210^5554568||EC^Emergency Contact^HL70131
```

---

## 14. ORU^R01 - Toxicology screen with embedded PDF (ED datatype)

```
MSH|^~\&|MIRTH|PARKLAND^2.16.840.1.113883.3.3301^ISO|LAB_RECV|TX_HIE|20260418130000||ORU^R01^ORU_R01|MIRTH20260418130000014|P|2.5.1|||AL|NE
PID|1||MRN40014^^^PARKLAND^MR||Massey^Marcus^Darnell^^Mr.^||19850922|M||2054-5^Black or African American^CDCREC|4510 Columbia Ave^^Dallas^TX^75226^US^H||^PRN^PH^^1^214^5556234|||S^Single^HL70002|||268-41-7503|||N^Not Hispanic or Latino^CDCREC
PV1|1|E|ED^0001^T6^PARKLAND^^^^N|E^Emergency^HL70007|||6789010016^Winslow^Stephanie^R^^^MD^^^^NPI||EM^Emergency Medicine^HL70069||||||||||VN20260418014^^^PARKLAND^VN
ORC|RE|ORD40014^MIRTH|FIL40014^TOX||CM^Complete^HL70038|||20260418100000|||6789010016^Winslow^Stephanie^R^^^MD^^^^NPI
OBR|1|ORD40014^MIRTH|FIL40014^TOX|97195^Drug screen qualitative^CPT4|||20260418100000|||||||||6789010016^Winslow^Stephanie^R^^^MD^^^^NPI||||||20260418125000|||F
OBX|1|CE|3426-4^Tetrahydrocannabinol [Presence] in Urine^LN||260373001^Detected^SCT||Negative|A|||F|||20260418125000
OBX|2|CE|3399-3^Opiates [Presence] in Urine^LN||260415000^Not detected^SCT||Negative|N|||F|||20260418125000
OBX|3|CE|3397-7^Cocaine metabolites [Presence] in Urine^LN||260415000^Not detected^SCT||Negative|N|||F|||20260418125000
OBX|4|CE|3390-2^Benzodiazepines [Presence] in Urine^LN||260415000^Not detected^SCT||Negative|N|||F|||20260418125000
OBX|5|CE|3349-8^Amphetamines [Presence] in Urine^LN||260415000^Not detected^SCT||Negative|N|||F|||20260418125000
OBX|6|ED|PDF^Toxicology Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxNDQKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihUb3hpY29sb2d5IFNjcmVlbiBSZXBvcnQpIFRqCjAgLTIwIFRkCi9GMSAxMCBUZgooUGFya2xhbmQgTWVtb3JpYWwgSG9zcGl0YWwpIFRqCjAgLTIwIFRkCihTcGVjaW1lbjogVXJpbmUpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoK||||||F|||20260418125000
```

---

## 15. ADT^A02 - Transfer from med-surg to telemetry

```
MSH|^~\&|MIRTH|METHODIST_SA^2.16.840.1.113883.3.3302^ISO|ADT_RECV|TX_HIE|20260419230000||ADT^A02^ADT_A02|MIRTH20260419230000015|P|2.5.1|||AL|NE
EVN|A02|20260419225500|||TELN^Ashmore^Patrick^J^^^RN|20260419225500
PID|1||MRN40015^^^METHODIST_SA^MR||Varma^Rajesh^Sunil^^Mr.^||19580705|M||2028-9^Asian^CDCREC|3200 W Woodlawn Ave^^San Antonio^TX^78228^US^H||^PRN^PH^^1^210^5551234|||M^Married^HL70002|||319-46-8205|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|TELE^2208^01^METHODIST_SA^^^^N|U^Urgent^HL70007|||7890120017^Kingsley^Douglas^A^^^MD^^^^NPI||MED^Medicine^HL70069||||||T^Transfer^HL70007|||||VN20260418015^^^METHODIST_SA^VN
PV2|||^New onset atrial fibrillation with rapid ventricular response, rate controlled
```

---

## 16. ADT^A40 - Patient merge due to duplicate registration

```
MSH|^~\&|MIRTH|PARKLAND^2.16.840.1.113883.3.3301^ISO|MPI_RECV|TX_HIE|20260420100000||ADT^A40^ADT_A39|MIRTH20260420100000016|P|2.5.1|||AL|NE
EVN|A40|20260420095500|||HIM^Culpepper^Karen^R^^^HIM|20260420095500
PID|1||MRN40016^^^PARKLAND^MR||Norwood^Patricia^Elaine^^Ms.^||19790314|F||2054-5^Black or African American^CDCREC|7100 Greenville Ave^^Dallas^TX^75231^US^H||^PRN^PH^^1^469^5558901|||D^Divorced^HL70002|||481-57-3920|||N^Not Hispanic or Latino^CDCREC
MRG|MRN40016DUP^^^PARKLAND^MR||||||Norwood^Patricia^E
```

---

## 17. ADT^A31 - Emergency contact update

```
MSH|^~\&|MIRTH|COOKCH^2.16.840.1.113883.3.3303^ISO|MPI_RECV|TX_HIE|20260421140000||ADT^A31^ADT_A05|MIRTH20260421140000017|P|2.5.1|||AL|NE
EVN|A31|20260421135500
PID|1||MRN40017^^^COOKCH^MR||Shimizu^Thomas^Kenji^^Mr.^||19680503|M||2028-9^Asian^CDCREC|3001 Bryan St^^Dallas^TX^75204^US^H||^PRN^PH^^1^214^5556780|||M^Married^HL70002|||592-64-8317|||N^Not Hispanic or Latino^CDCREC
NK1|1|Shimizu^Linda^Akiko^^Mrs.|SPO^Spouse^HL70063|3001 Bryan St^^Dallas^TX^75204^US|^PRN^PH^^1^214^5556781||EC^Emergency Contact^HL70131
NK1|2|Shimizu^Robert^Hiroshi^^Mr.|SON^Son^HL70063|1208 Elm St^^Dallas^TX^75202^US|^PRN^PH^^1^469^5553456||EC^Emergency Contact^HL70131
```

---

## 18. MFN^M02 - Nursing staff master file update

```
MSH|^~\&|MIRTH|PARKLAND^2.16.840.1.113883.3.3301^ISO|MF_RECV|TX_HIE|20260422090000||MFN^M02^MFN_M02|MIRTH20260422090000018|P|2.5.1|||AL|NE
MFI|PRA^Practitioner master file^HL70175||UPD^Update^HL70180|||NE
MFE|MAD^Add record to master file^HL70180|20260422085500||8901230018^Montoya^Elena^Sofia^^NP|CWE
STF|8901230018|U8901230018|Montoya^Elena^Sofia^^NP||F|19850412|A^Active^HL70183|||||^WPN^PH^^1^214^5559800
PRA|8901230018^Montoya^Elena^Sofia^^NP|PARKLAND^Parkland Memorial Hospital|I^Institution^HL70186|||||363L00000X^Nurse Practitioner^NUCC
```

---

## 19. ACK - Application accept acknowledgment

```
MSH|^~\&|LAB_RECV|TX_HIE|MIRTH|METHODIST_SA^2.16.840.1.113883.3.3302^ISO|20260423100000||ACK^R01^ACK|MIRTH20260423100000019|P|2.5.1|||AL|NE
MSA|AA|MIRTH20260406143000002||0
```

---

## 20. ORM^O01 - Stat portable chest X-ray order

```
MSH|^~\&|MIRTH|PARKLAND^2.16.840.1.113883.3.3301^ISO|RAD_RECV|TX_HIE|20260424030000||ORM^O01^ORM_O01|MIRTH20260424030000020|P|2.5.1|||AL|NE
PID|1||MRN40020^^^PARKLAND^MR||Outlaw^Robert^Dwayne^^Mr.^||19430917|M||2054-5^Black or African American^CDCREC|1500 E Illinois Ave^^Dallas^TX^75216^US^H||^PRN^PH^^1^214^5551890|||W^Widowed^HL70002|||714-62-3908|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|ICU^1004^01^PARKLAND^^^^N|E^Emergency^HL70007|||9012340019^Sterling^Angela^D^^^MD^^^^NPI||CCM^Critical Care^HL70069||||||||||VN20260423020^^^PARKLAND^VN
ORC|NW|ORD40020^MIRTH||GRP40020^MIRTH|||||20260424025000|||9012340019^Sterling^Angela^D^^^MD^^^^NPI|||||PARKLAND^Parkland Memorial Hospital
OBR|1|ORD40020^MIRTH||71045^Chest X-ray single view^CPT4|||20260424025000||||||||9012340019^Sterling^Angela^D^^^MD^^^^NPI||||||||||9^Stat^HL70065
DG1|1||J96.01^Acute respiratory failure with hypoxia^I10||20260423|A
NTE|1||ICU patient on ventilator. Check ET tube position and interval change.
```
