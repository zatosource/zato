# Epic EHR - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to MGH cardiology

```
MSH|^~\&|EPIC|MGH^1234^NPI|ADT_RECV|MGB_HIS|20250312084523||ADT^A01^ADT_A01|MSG00001|P|2.4|||AL|NE
EVN|A01|20250312084500|||TGRADY^Grady^Thomas^E^MD^^NPI
PID|1||MRN10234567^^^MGB^MR~999-52-3187^^^SSA^SS||Callahan^Deirdre^Noreen^^Mrs.||19670423|F||2106-3^White^HL70005|45 Beacon Street^^Boston^MA^02108^US||^PRN^PH^^^617^5551234|^WPN^PH^^^617^5559876||M||VN00123456|999-52-3187
PV1|1|I|CARD^4102^A^MGH^^^N|E|||18234^Harrington^Owen^F^MD^^NPI||72091^Leung^Sandra^M^MD^^NPI|CAR|||1|||18234^Harrington^Owen^F^MD^^NPI|IN||BCBS|||||||||||||||||||MGH||||20250312084500
PV2|||^Acute myocardial infarction||||||20250312|20250319
IN1|1|BCBS001^Blue Cross Blue Shield MA|7834|Blue Cross Blue Shield of Massachusetts|101 Huntington Ave^^Boston^MA^02199^US|^PRN^PH^^^800^2628282|GRP71483|||||||Callahan^Deirdre^Noreen|SEL|19670423|45 Beacon Street^^Boston^MA^02108^US|||||||||||||||||993521870
NK1|1|Callahan^Brendan^^Mr.|SPO|45 Beacon Street^^Boston^MA^02108^US|^PRN^PH^^^617^5551235||EC
DG1|1||I21.0^Acute transmural MI of anterior wall^ICD10|||A
GT1|1||Callahan^Deirdre^Noreen||45 Beacon Street^^Boston^MA^02108^US|^PRN^PH^^^617^5551234||19670423|F||SEL|999-52-3187
```

---

## 2. ORU^R01 - Cardiology lab results

```
MSH|^~\&|EPIC|BWH^5678^NPI|LAB_RECV|MGB_HIS|20250315102345||ORU^R01^ORU_R01|MSG00002|P|2.4|||AL|NE
PID|1||MRN20345678^^^MGB^MR||Flanagan^Declan^Thomas^^Mr.||19580917|M||2106-3^White^HL70005|128 Commonwealth Ave^^Boston^MA^02116^US||^PRN^PH^^^617^5552345||S||VN00234567
PV1|1|O|CARD^CATH^A^BWH|||29471^Mukherjee^Arjun^K^MD^^NPI||||||||||OUT||||||||||||||||||BWH||||20250315090000
ORC|RE|ORD12345|FIL67890||CM||||20250315102300|||29471^Mukherjee^Arjun^K^MD^^NPI
OBR|1|ORD12345|FIL67890|BNP^Brain Natriuretic Peptide^L|||20250315090000|||||||||29471^Mukherjee^Arjun^K^MD^^NPI||||||20250315102300||LAB|F
OBX|1|NM|BNP^Brain Natriuretic Peptide^L||450|pg/mL|0-100|HH|||F|||20250315102300
OBX|2|NM|TROP^Troponin I^L||0.08|ng/mL|0.00-0.04|H|||F|||20250315102300
OBX|3|NM|CK^Creatine Kinase^L||245|U/L|30-200|H|||F|||20250315102300
OBX|4|NM|CKMB^CK-MB^L||18.5|ng/mL|0.0-5.0|HH|||F|||20250315102300
NTE|1||Elevated cardiac biomarkers consistent with myocardial injury. Clinical correlation recommended.
```

---

## 3. ORM^O01 - Radiology order for chest CT

```
MSH|^~\&|EPIC|BWH^5678^NPI|RAD_RECV|MGB_HIS|20250318143022||ORM^O01^ORM_O01|MSG00003|P|2.3|||AL|NE
PID|1||MRN30456789^^^MGB^MR||Medeiros^Cristina^Lucia^^Ms.||19750611|F||2106-3^White^HL70005|77 Marlborough St^^Boston^MA^02116^US||^PRN^PH^^^857^5553456||M||VN00345678
PV1|1|O|PUL^CLINIC^B^BWH|||38214^Tremblay^Nicole^R^MD^^NPI|||||||||OUT||||||||||||||||||BWH||||20250318140000
ORC|NW|ORD23456||||||^^^20250319080000^^R||20250318143000|||38214^Tremblay^Nicole^R^MD^^NPI
OBR|1|ORD23456||71260^CT Chest with Contrast^CPT|||20250319080000||||||||38214^Tremblay^Nicole^R^MD^^NPI|||||||||||1^^^20250319080000^^R
DG1|1||R91.1^Solitary pulmonary nodule^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||History of smoking. Follow-up of 8mm pulmonary nodule detected on prior CXR.||||||F
```

---

## 4. SIU^S12 - Surgical scheduling at MGH

```
MSH|^~\&|EPIC|MGH^1234^NPI|SCHED_RECV|MGB_HIS|20250320091500||SIU^S12^SIU_S12|MSG00004|P|2.4|||AL|NE
SCH|SCH78901|||||SURGERY|ORTHO^Orthopedic Surgery^L|45|MIN|^^45^20250401080000^20250401084500||51738^Ostrowski^Marek^J^MD^^NPI|^^^MGH^OR12|||51738^Ostrowski^Marek^J^MD^^NPI||BOOKED
PID|1||MRN40567890^^^MGB^MR||Sweeney^Colin^Patrick^^Mr.||19820214|M||2106-3^White^HL70005|234 Harvard St^^Cambridge^MA^02139^US||^PRN^PH^^^617^5554567||S||VN00456789
PV1|1|O|ORTH^SURG^A^MGH|||51738^Ostrowski^Marek^J^MD^^NPI|||||||||OUT||||||||||||||||||MGH||||20250401080000
RGS|1
AIS|1||27447^Total Knee Arthroplasty^CPT|20250401080000||45|MIN|||BOOKED
AIG|1||51738^Ostrowski^Marek^J^MD^^NPI|SURGEON
AIL|1||MGH^OR12^^OPERATING ROOM 12|||20250401080000||45|MIN
```

---

## 5. MDM^T02 - Clinical document notification from Dana-Farber

```
MSH|^~\&|EPIC|DFCI^9012^NPI|DOC_RECV|MGB_HIS|20250322161200||MDM^T02^MDM_T02|MSG00005|P|2.4|||AL|NE
EVN|T02|20250322161200
PID|1||MRN50678901^^^DFCI^MR||Tran^Bao^Minh^^Mr.||19690805|M||2028-9^Asian^HL70005|56 Garden St^^Cambridge^MA^02138^US||^PRN^PH^^^617^5555678||M||VN00567890
PV1|1|O|ONC^3B^A^DFCI|||63290^Cavanaugh^Eileen^R^MD^^NPI|||||||||OUT||||||||||||||||||DFCI||||20250322150000
TXA|1|CN|TX|20250322161200|63290^Cavanaugh^Eileen^R^MD^^NPI||20250322161200||||||DOC001234||AU||AV
OBX|1|TX|ONCNOTE^Oncology Progress Note^L||Patient seen for cycle 4 of FOLFOX chemotherapy for Stage III colon cancer.~Tolerating treatment well. Mild peripheral neuropathy grade 1.~Labs stable. Neutrophils 2.1, platelets 185.~Plan: Continue current regimen. Recheck labs in 2 weeks.||||||F
```

---

## 6. VXU^V04 - Immunization update at Boston Children's

```
MSH|^~\&|EPIC|BCH^3456^NPI|MIIS|MADPH|20250325090100||VXU^V04^VXU_V04|MSG00006|P|2.5.1|||AL|NE
PID|1||MRN60789012^^^BCH^MR||Correia^Lucas^Gabriel^^||20200115|M||2106-3^White^HL70005|89 Newbury St^^Boston^MA^02116^US||^PRN^PH^^^617^5556789|||||||||||N
PD1||||74812^Delaney^Kathleen^A^MD^^NPI
NK1|1|Correia^Ana^^Mrs.|MTH|89 Newbury St^^Boston^MA^02116^US|^PRN^PH^^^617^5556789
ORC|RE|IMM34567||||||||||74812^Delaney^Kathleen^A^MD^^NPI||||||BCH
RXA|0|1|20250325090000||208^Pfizer-BioNTech COVID-19 Vaccine^CVX|0.2|mL||00^New Immunization Record^NIP001||||||EW8243|20260101|PMC^Pfizer Inc.^MVX
RXR|C28161^Intramuscular^NCIT|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Program Eligibility^LN||V02^VFC eligible - Medicaid/Medicaid managed care^HL70064||||||F
OBX|2|DT|29768-9^Date Vaccine Information Statement Published^LN||20230112||||||F
```

---

## 7. ADT^A08 - Patient information update at Tufts Medical Center

```
MSH|^~\&|EPIC|TMC^7890^NPI|ADT_RECV|TUFTS_HIS|20250327112233||ADT^A08^ADT_A08|MSG00007|P|2.4|||AL|NE
EVN|A08|20250327112200|||ADMIN^Admin^System^^^
PID|1||MRN70890123^^^TMC^MR~999-74-6218^^^SSA^SS||Krawczyk^Halina^Zofia^^Ms.||19830319|F||2106-3^White^HL70005|412 Boylston St^^Boston^MA^02116^US||^PRN^PH^^^617^5557890|^WPN^PH^^^617^5558901||S||VN00678901|999-74-6218
PV1|1|O|NEUR^CLINIC^A^TMC|||84503^Banerjee^Sunil^K^MD^^NPI|||||||||OUT||||||||||||||||||TMC||||20250327110000
IN1|1|HVRD001^Harvard Pilgrim Health Care|4521|Harvard Pilgrim Health Care|1600 Crown Colony Dr^^Quincy^MA^02169^US|^PRN^PH^^^888^8884742|GRP45678|||||||Krawczyk^Halina^Zofia|SEL|19830319|412 Boylston St^^Boston^MA^02116^US|||||||||||||||||997462180
```

---

## 8. ORU^R01 - Pathology report with embedded PDF from BWH

```
MSH|^~\&|EPIC|BWH^5678^NPI|PATH_RECV|MGB_HIS|20250401093045||ORU^R01^ORU_R01|MSG00008|P|2.4|||AL|NE
PID|1||MRN80901234^^^MGB^MR||Nakamura^Yuki^Akiko^^Ms.||19710622|F||2028-9^Asian^HL70005|18 Brattle St^^Cambridge^MA^02138^US||^PRN^PH^^^617^5558012||M||VN00789012
PV1|1|I|SURG^6N^B^BWH|||91247^Fitzpatrick^Ronan^D^MD^^NPI|||||||||IN||||||||||||||||||BWH||||20250329140000
ORC|RE|ORD34567|PATH89012||CM||||20250401093000|||91247^Fitzpatrick^Ronan^D^MD^^NPI
OBR|1|ORD34567|PATH89012|88305^Surgical Pathology^CPT|||20250329160000|||||||||91247^Fitzpatrick^Ronan^D^MD^^NPI||||||20250401093000||PATH|F
OBX|1|TX|PATH_DX^Pathology Diagnosis^L||BREAST, LEFT, LUMPECTOMY:~Invasive ductal carcinoma, grade 2, measuring 1.8 cm.~Margins negative (closest margin 0.4 cm).~Lymphovascular invasion not identified.~ER positive (95%), PR positive (80%), HER2 negative (IHC 1+).||||||F
OBX|2|TX|PATH_GROSS^Gross Description^L||Received in formalin labeled "left breast lumpectomy" is a 4.2 x 3.1 x 2.8 cm specimen.~Serially sectioned to reveal a firm, tan-white mass measuring 1.8 x 1.5 x 1.4 cm.||||||F
OBX|3|ED|PATH_PDF^Pathology Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 9. ADT^A03 - Patient discharge from UMass Memorial

```
MSH|^~\&|EPIC|UMMC^2345^NPI|ADT_RECV|UMASS_HIS|20250403153000||ADT^A03^ADT_A03|MSG00009|P|2.4|||AL|NE
EVN|A03|20250403152900|||95381^Whitfield^Laura^J^MD^^NPI
PID|1||MRN90012345^^^UMMC^MR~999-83-4516^^^SSA^SS||Baptiste^Reginald^Clarence^^Mr.||19550108|M||2054-5^Black^HL70005|340 Main St^^Worcester^MA^01608^US||^PRN^PH^^^508^5551234||M||VN00890123|999-83-4516
PV1|1|I|MED^3W^C^UMMC^^^N|U|||95381^Whitfield^Laura^J^MD^^NPI||06712^Almeida^Rafael^P^MD^^NPI|MED|||1|||95381^Whitfield^Laura^J^MD^^NPI|IN||MEDCR|||||||||||||||||||UMMC||||20250330100000|20250403153000
PV2|||^Community acquired pneumonia||||||20250330|20250403
DG1|1||J18.9^Pneumonia, unspecified organism^ICD10|||A
DG1|2||E11.9^Type 2 diabetes mellitus without complications^ICD10|||S
```

---

## 10. ORM^O01 - Lab order from Beth Israel Deaconess

```
MSH|^~\&|EPIC|BIDMC^4567^NPI|LAB_RECV|BIDMC_HIS|20250405081500||ORM^O01^ORM_O01|MSG00010|P|2.3|||AL|NE
PID|1||MRN01123456^^^BIDMC^MR||Vasquez^Gabriela^Renata^^Mrs.||19880730|F||2131-1^Hispanic^HL70005|67 Longwood Ave^^Boston^MA^02115^US||^PRN^PH^^^617^5559123||M||VN00901234
PV1|1|O|ENDO^CLINIC^A^BIDMC|||07193^Narayan^Deepa^S^MD^^NPI|||||||||OUT||||||||||||||||||BIDMC||||20250405080000
ORC|NW|ORD45678||||||^^^20250405090000^^R||20250405081500|||07193^Narayan^Deepa^S^MD^^NPI
OBR|1|ORD45678||83036^Hemoglobin A1c^CPT|||20250405090000||||||||07193^Narayan^Deepa^S^MD^^NPI
OBR|2|ORD45678||80053^Comprehensive Metabolic Panel^CPT|||20250405090000||||||||07193^Narayan^Deepa^S^MD^^NPI
OBR|3|ORD45678||85025^Complete Blood Count with Differential^CPT|||20250405090000||||||||07193^Narayan^Deepa^S^MD^^NPI
DG1|1||E11.65^Type 2 DM with hyperglycemia^ICD10
```

---

## 11. ORU^R01 - Microbiology culture results from MGH

```
MSH|^~\&|EPIC|MGH^1234^NPI|LAB_RECV|MGB_HIS|20250407141500||ORU^R01^ORU_R01|MSG00011|P|2.4|||AL|NE
PID|1||MRN11234567^^^MGB^MR||Galvin^Niall^Patrick^^Mr.||19450612|M||2106-3^White^HL70005|201 Charles St^^Boston^MA^02114^US||^PRN^PH^^^617^5550234||W||VN01012345
PV1|1|I|MED^7E^A^MGH|||18234^Harrington^Owen^F^MD^^NPI|||||||||IN||||||||||||||||||MGH||||20250405080000
ORC|RE|ORD56789|MIC12345||CM||||20250407141500|||18234^Harrington^Owen^F^MD^^NPI
OBR|1|ORD56789|MIC12345|87040^Blood Culture^CPT|||20250405100000|||||||||18234^Harrington^Owen^F^MD^^NPI||||||20250407141500||MB|F
OBX|1|CE|CULTURE^Culture Result^L||Staphylococcus aureus|||A|||F|||20250407141500
OBX|2|TX|SUSCEPT^Susceptibility^L||Oxacillin: Resistant (MRSA)~Vancomycin: Sensitive (MIC 1.0)~Daptomycin: Sensitive~Linezolid: Sensitive~TMP/SMX: Sensitive||||||F|||20250407141500
OBX|3|TX|COMMENT^Lab Comment^L||Two of two blood culture bottles positive at 18 hours.~Gram stain: Gram positive cocci in clusters.||||||F|||20250407141500
```

---

## 12. ADT^A04 - Patient registration at Baystate Health

```
MSH|^~\&|EPIC|BAYS^6789^NPI|ADT_RECV|BAYSTATE_HIS|20250409070000||ADT^A04^ADT_A04|MSG00012|P|2.4|||AL|NE
EVN|A04|20250409065900|||REGNURSE^Reg^Nurse^^^
PID|1||MRN12345678^^^BAYS^MR~999-61-4923^^^SSA^SS||Nowak^Tomasz^Piotr^^Mr.||19920505|M||2106-3^White^HL70005|789 State St^^Springfield^MA^01109^US||^PRN^PH^^^413^5551234||S||VN01123456|999-61-4923
PV1|1|E|ED^BED03^A^BAYS^^^N|E|||28319^Achebe^Ngozi^E^MD^^NPI|||||||||ER||||||||||||||||||BAYS||||20250409070000
PV2|||^Chest pain, unspecified
NK1|1|Nowak^Elzbieta^^Mrs.|MTH|789 State St^^Springfield^MA^01109^US|^PRN^PH^^^413^5551235||EC
DG1|1||R07.9^Chest pain, unspecified^ICD10|||W
IN1|1|BCBS001^Blue Cross Blue Shield MA|7834|Blue Cross Blue Shield of Massachusetts|101 Huntington Ave^^Boston^MA^02199^US|^PRN^PH^^^800^2628282|GRP12345|||||||Nowak^Tomasz^Piotr|SEL|19920505|789 State St^^Springfield^MA^01109^US
```

---

## 13. SIU^S14 - Appointment modification at Dana-Farber

```
MSH|^~\&|EPIC|DFCI^9012^NPI|SCHED_RECV|MGB_HIS|20250410143000||SIU^S14^SIU_S12|MSG00013|P|2.4|||AL|NE
SCH|SCH89012|SCH89012||||CLINIC|RADONC^Radiation Oncology^L|30|MIN|^^30^20250420093000^20250420100000||41658^Fong^Bradley^H^MD^^NPI|^^^DFCI^RADONC_SIM|||41658^Fong^Bradley^H^MD^^NPI||BOOKED
PID|1||MRN13456789^^^DFCI^MR||Rizzo^Concetta^Lucia^^Mrs.||19630218|F||2106-3^White^HL70005|15 Hanover St^^Boston^MA^02113^US||^PRN^PH^^^617^5553210||M||VN01234567
PV1|1|O|RADONC^SIM^A^DFCI|||41658^Fong^Bradley^H^MD^^NPI|||||||||OUT||||||||||||||||||DFCI||||20250420093000
RGS|1
AIS|1||77014^CT Simulation for Radiation Therapy^CPT|20250420093000||30|MIN|||BOOKED
AIL|1||DFCI^RADONC_SIM^^RADIATION ONCOLOGY SIMULATION|||20250420093000||30|MIN
```

---

## 14. ORU^R01 - Comprehensive metabolic panel from BIDMC

```
MSH|^~\&|EPIC|BIDMC^4567^NPI|LAB_RECV|BIDMC_HIS|20250412101500||ORU^R01^ORU_R01|MSG00014|P|2.4|||AL|NE
PID|1||MRN14567890^^^BIDMC^MR||Oliveira^Henrique^Mateus^^Mr.||19780314|M||2131-1^Hispanic^HL70005|250 Brookline Ave^^Boston^MA^02215^US||^PRN^PH^^^617^5554321||M||VN01345678
PV1|1|O|MED^INT^A^BIDMC|||53024^Donnelly^Fiona^C^MD^^NPI|||||||||OUT||||||||||||||||||BIDMC||||20250412090000
ORC|RE|ORD67890|FIL23456||CM||||20250412101500|||53024^Donnelly^Fiona^C^MD^^NPI
OBR|1|ORD67890|FIL23456|80053^Comprehensive Metabolic Panel^CPT|||20250412090000|||||||||53024^Donnelly^Fiona^C^MD^^NPI||||||20250412101500||CH|F
OBX|1|NM|GLU^Glucose^L||98|mg/dL|70-100||||F|||20250412101500
OBX|2|NM|BUN^Blood Urea Nitrogen^L||15|mg/dL|7-20||||F|||20250412101500
OBX|3|NM|CREAT^Creatinine^L||1.1|mg/dL|0.7-1.3||||F|||20250412101500
OBX|4|NM|NA^Sodium^L||140|mmol/L|136-145||||F|||20250412101500
OBX|5|NM|K^Potassium^L||4.2|mmol/L|3.5-5.1||||F|||20250412101500
OBX|6|NM|CL^Chloride^L||102|mmol/L|98-106||||F|||20250412101500
OBX|7|NM|CO2^Carbon Dioxide^L||24|mmol/L|23-29||||F|||20250412101500
OBX|8|NM|ALT^Alanine Aminotransferase^L||28|U/L|7-56||||F|||20250412101500
OBX|9|NM|AST^Aspartate Aminotransferase^L||22|U/L|10-40||||F|||20250412101500
OBX|10|NM|ALKP^Alkaline Phosphatase^L||72|U/L|44-147||||F|||20250412101500
```

---

## 15. MDM^T02 - Discharge summary with embedded PDF from MGH

```
MSH|^~\&|EPIC|MGH^1234^NPI|DOC_RECV|MGB_HIS|20250414160000||MDM^T02^MDM_T02|MSG00015|P|2.4|||AL|NE
EVN|T02|20250414160000
PID|1||MRN15678901^^^MGB^MR||Shaughnessy^Maeve^Patricia^^Ms.||19480930|F||2106-3^White^HL70005|55 Fruit St^^Boston^MA^02114^US||^PRN^PH^^^617^5556543||W||VN01456789
PV1|1|I|MED^5W^A^MGH|||60347^Ibarra^Marcos^G^MD^^NPI|||||||||IN||||||||||||||||||MGH||||20250408120000|20250414153000
TXA|1|DS|TX|20250414160000|60347^Ibarra^Marcos^G^MD^^NPI||20250414160000||||||DOC002345||AU||AV
OBX|1|TX|DCSUMMARY^Discharge Summary^L||DISCHARGE DIAGNOSIS: Heart failure with reduced ejection fraction (HFrEF)~HOSPITAL COURSE: 78-year-old woman admitted with acute decompensated heart failure.~Treated with IV diuresis, achieved 4L net negative fluid balance.~Echocardiogram showed EF 30%, moderate MR.~Discharged on optimized GDMT.||||||F
OBX|2|ED|DCSUMPDF^Discharge Summary PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 16. ADT^A02 - Patient transfer within Boston Children's

```
MSH|^~\&|EPIC|BCH^3456^NPI|ADT_RECV|BCH_HIS|20250416082000||ADT^A02^ADT_A02|MSG00016|P|2.4|||AL|NE
EVN|A02|20250416081900|||74812^Delaney^Kathleen^A^MD^^NPI
PID|1||MRN16789012^^^BCH^MR||Feliciano^Sofia^Valentina^^||20180907|F||2131-1^Hispanic^HL70005|123 Longwood Ave^^Boston^MA^02115^US||^PRN^PH^^^617^5557654
PV1|1|I|PICU^BED08^A^BCH^^^N|U|||74812^Delaney^Kathleen^A^MD^^NPI||82064^Sarkisian^Lena^V^MD^^NPI|PED|||1|||74812^Delaney^Kathleen^A^MD^^NPI|IN||MEDCAID|||||||||||||||||||BCH||||20250414220000
PV2|||^Status asthmaticus
NK1|1|Feliciano^Carmen^Alicia^Mrs.|MTH|123 Longwood Ave^^Boston^MA^02115^US|^PRN^PH^^^617^5557654||EC
```

---

## 17. ORU^R01 - Genetic testing results from Dana-Farber

```
MSH|^~\&|EPIC|DFCI^9012^NPI|LAB_RECV|MGB_HIS|20250418134500||ORU^R01^ORU_R01|MSG00017|P|2.5.1|||AL|NE
PID|1||MRN17890123^^^DFCI^MR||Hwang^Sung-Ho^Jae^^Mr.||19650411|M||2028-9^Asian^HL70005|78 Mt Auburn St^^Cambridge^MA^02138^US||^PRN^PH^^^617^5558765||M||VN01678901
PV1|1|O|GENM^CLINIC^A^DFCI|||87415^Lindstrom^Ingrid^M^MD^^NPI|||||||||OUT||||||||||||||||||DFCI||||20250418120000
ORC|RE|ORD78901|GEN45678||CM||||20250418134500|||87415^Lindstrom^Ingrid^M^MD^^NPI
OBR|1|ORD78901|GEN45678|81455^Comprehensive Genomic Profiling^CPT|||20250404120000|||||||||87415^Lindstrom^Ingrid^M^MD^^NPI||||||20250418134500||GN|F
OBX|1|TX|GENE_SUMM^Genomic Summary^L||Tumor Type: Non-small cell lung cancer, adenocarcinoma~Specimen: Core needle biopsy, right upper lobe~Tumor Mutational Burden: 8.2 mutations/Mb (Intermediate)~Microsatellite Status: Stable (MSS)||||||F|||20250418134500
OBX|2|TX|GENE_ALT^Genomic Alterations^L||EGFR L858R - Activating mutation (Tier I)~TP53 R248W - Loss of function (Tier II)~CDKN2A/B - Homozygous deletion (Tier II)~PD-L1 TPS: 45%||||||F|||20250418134500
OBX|3|TX|GENE_THER^Therapeutic Implications^L||FDA-approved therapies: Osimertinib (EGFR L858R)~Clinical trials available for TP53 mutant tumors.~Checkpoint inhibitor may be considered given PD-L1 45%.||||||F|||20250418134500
NTE|1||Results reviewed and discussed with patient on 2025-04-18.
```

---

## 18. ORM^O01 - Pharmacy order from Tufts Medical Center

```
MSH|^~\&|EPIC|TMC^7890^NPI|PHARM_RECV|TUFTS_HIS|20250420091000||ORM^O01^ORM_O01|MSG00018|P|2.3|||AL|NE
PID|1||MRN18901234^^^TMC^MR||Sokolov^Maxim^Andreyevich^^Mr.||19710903|M||2106-3^White^HL70005|500 Washington St^^Boston^MA^02111^US||^PRN^PH^^^617^5559876||M||VN01789012
PV1|1|I|MED^4N^A^TMC|||93650^Tsai^Lillian^W^MD^^NPI|||||||||IN||||||||||||||||||TMC||||20250419180000
ORC|NW|ORD89012||||||^^^20250420093000^^R||20250420091000|||93650^Tsai^Lillian^W^MD^^NPI
OBR|1|ORD89012||RX001^Pharmacy Order^L|||20250420093000||||||||93650^Tsai^Lillian^W^MD^^NPI
RXO|vancomycin^Vancomycin^RxNorm|1250|mg||IV|Q12H|||G|||30
RXR|IV^Intravenous^HL70162
DG1|1||A41.9^Sepsis, unspecified organism^ICD10
OBX|1|NM|WT^Patient Weight^L||85|kg|||||F
OBX|2|NM|CRCLR^Creatinine Clearance^L||72|mL/min|||||F
```

---

## 19. ORU^R01 - Cardiology echo report from BWH

```
MSH|^~\&|EPIC|BWH^5678^NPI|CARD_RECV|MGB_HIS|20250422110000||ORU^R01^ORU_R01|MSG00019|P|2.4|||AL|NE
PID|1||MRN19012345^^^MGB^MR||Driscoll^Eileen^Veronica^^Mrs.||19520715|F||2106-3^White^HL70005|92 Chestnut Hill Ave^^Brookline^MA^02445^US||^PRN^PH^^^617^5550198||W||VN01890123
PV1|1|O|CARD^ECHO^A^BWH|||04872^Ramachandran^Vivek^N^MD^^NPI|||||||||OUT||||||||||||||||||BWH||||20250422090000
ORC|RE|ORD90123|ECHO56789||CM||||20250422110000|||04872^Ramachandran^Vivek^N^MD^^NPI
OBR|1|ORD90123|ECHO56789|93306^Echocardiogram Complete^CPT|||20250422090000|||||||||04872^Ramachandran^Vivek^N^MD^^NPI||||||20250422110000||CAR|F
OBX|1|TX|ECHO_FIND^Echo Findings^L||LV: Mildly dilated with moderately reduced systolic function. EF 35% by biplane Simpson's.~RV: Normal size and function.~Valves: Moderate mitral regurgitation, mild tricuspid regurgitation.~Diastolic function: Grade II (pseudonormal pattern).~Pericardium: No effusion.||||||F|||20250422110000
OBX|2|NM|EF^Ejection Fraction^L||35|%|55-70|L|||F|||20250422110000
OBX|3|NM|LVIDD^LV Internal Diameter Diastole^L||5.8|cm|3.5-5.6|H|||F|||20250422110000
OBX|4|NM|LA_VOL^Left Atrial Volume Index^L||38|mL/m2|16-34|H|||F|||20250422110000
OBX|5|TX|ECHO_IMP^Impression^L||Moderately reduced LV systolic function (EF 35%). Moderate MR likely functional.~Recommend optimization of heart failure therapy and follow-up echo in 3 months.||||||F|||20250422110000
```

---

## 20. ADT^A28 - New patient registration at Mass General Brigham

```
MSH|^~\&|EPIC|MGB^0001^NPI|MPI_RECV|MGB_HIS|20250425080000||ADT^A28^ADT_A28|MSG00020|P|2.4|||AL|NE
EVN|A28|20250425080000|||REGISTRATION^Reg^System^^^
PID|1||MRN20123456^^^MGB^MR~999-38-7104^^^SSA^SS||Mensah^Abena^Serwa^^Ms.||19950822|F||2054-5^Black^HL70005|34 Tremont St^^Boston^MA^02108^US||^PRN^PH^^^617^5550345|^WPN^PH^^^617^5550346||S||VN01901234|999-38-7104
PD1||||18234^Harrington^Owen^F^MD^^NPI
NK1|1|Mensah^Kwame^^Mr.|FTH|34 Tremont St^^Boston^MA^02108^US|^PRN^PH^^^617^5550347||EC
IN1|1|TFT001^Tufts Health Plan|8901|Tufts Health Plan|705 Mt Auburn St^^Watertown^MA^02472^US|^PRN^PH^^^800^4624476|GRP56789|||||||Mensah^Abena^Serwa|SEL|19950822|34 Tremont St^^Boston^MA^02108^US|||||||||||||||||993871040
```
