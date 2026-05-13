# Iguana Integration Engine (iNTERFACEWARE) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission via Iguana from Steward Health Care

```
MSH|^~\&|IGUANA|NORWOOD^4001^NPI|ADT_RECV|STEWARD_HIS|20250311073000||ADT^A01^ADT_A01|IG00001|P|2.4|||AL|NE
EVN|A01|20250311072900|||41928^Callahan^Derek^P^MD^^NPI
PID|1||NOR20123456^^^NOR^MR~318-52-7841^^^SSA^SS||Medeiros^Rafael^Tiago^^Mr.||19680522|M||2106-3^White^HL70005|78 Washington St^^Norwood^MA^02062^US||^PRN^PH^^^781^6429183||M||VN20012345|318-52-7841
PV1|1|I|MED^301^A^NOR^^^N|E|||41928^Callahan^Derek^P^MD^^NPI||52847^Valenzuela^Diana^M^MD^^NPI|MED|||1|||41928^Callahan^Derek^P^MD^^NPI|IN||BCBS|||||||||||||||||||NOR||||20250311072900
PV2|||^Acute kidney injury
NK1|1|Medeiros^Claudia^^Mrs.|SPO|78 Washington St^^Norwood^MA^02062^US|^PRN^PH^^^781^6429184||EC
DG1|1||N17.9^Acute kidney failure, unspecified^ICD10|||A
IN1|1|BCBS001^Blue Cross Blue Shield MA|7834|Blue Cross Blue Shield of Massachusetts|101 Huntington Ave^^Boston^MA^02199^US|^PRN^PH^^^800^2628282|GRP23456|||||||Medeiros^Rafael^Tiago|SEL|19680522|78 Washington St^^Norwood^MA^02062^US
```

---

## 2. ORU^R01 - Lab results routed through Iguana from Heywood Hospital

```
MSH|^~\&|IGUANA|HEYWOOD^4002^NPI|LAB_RECV|HH_HIS|20250313101500||ORU^R01^ORU_R01|IG00002|P|2.4|||AL|NE
PID|1||HEY30234567^^^HEY^MR||Gagnon^Denis^Armand^^Mr.||19750814|M||2106-3^White^HL70005|45 Central St^^Gardner^MA^01440^US||^PRN^PH^^^978^3418726||M||VN30023456
PV1|1|O|LAB^DRAW^A^HEYWOOD|||63917^Tierney^Brendan^J^MD^^NPI|||||||||OUT||||||||||||||||||HEY||||20250313090000
ORC|RE|ORD20002|FIL30002||CM||||20250313101500|||63917^Tierney^Brendan^J^MD^^NPI
OBR|1|ORD20002|FIL30002|80053^Comprehensive Metabolic Panel^CPT|||20250313090000|||||||||63917^Tierney^Brendan^J^MD^^NPI||||||20250313101500||CH|F
OBX|1|NM|GLU^Glucose^L||112|mg/dL|70-100|H|||F|||20250313101500
OBX|2|NM|BUN^Blood Urea Nitrogen^L||18|mg/dL|7-20||||F|||20250313101500
OBX|3|NM|CREAT^Creatinine^L||1.0|mg/dL|0.7-1.3||||F|||20250313101500
OBX|4|NM|NA^Sodium^L||141|mmol/L|136-145||||F|||20250313101500
OBX|5|NM|K^Potassium^L||4.0|mmol/L|3.5-5.1||||F|||20250313101500
OBX|6|NM|ALT^Alanine Aminotransferase^L||32|U/L|7-56||||F|||20250313101500
OBX|7|NM|AST^Aspartate Aminotransferase^L||28|U/L|10-40||||F|||20250313101500
```

---

## 3. ORM^O01 - Radiology order routed via Iguana from Good Samaritan

```
MSH|^~\&|IGUANA|GSMC^4003^NPI|RAD_RECV|STEWARD_HIS|20250315142000||ORM^O01^ORM_O01|IG00003|P|2.3|||AL|NE
PID|1||GSMC40345678^^^GSMC^MR||Soares^Daniela^Renata^^Mrs.||19820311|F||2131-1^Hispanic^HL70005|234 North Main St^^Brockton^MA^02301^US||^PRN^PH^^^508^7263914||M||VN40034567
PV1|1|E|ED^BED11^A^GSMC|||74185^Flanagan^Garrett^D^MD^^NPI|||||||||ER||||||||||||||||||GSMC||||20250315135000
ORC|NW|ORD30003||||||^^^20250315150000^^S||20250315142000|||74185^Flanagan^Garrett^D^MD^^NPI
OBR|1|ORD30003||74177^CT Abdomen with Contrast^CPT|||20250315150000|||||||S|74185^Flanagan^Garrett^D^MD^^NPI|||||||||||1^^^20250315150000^^S
DG1|1||R10.9^Unspecified abdominal pain^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||38 yo female with acute RLQ pain x 6 hours. Elevated WBC 14.2. R/O appendicitis.||||||F
```

---

## 4. ADT^A03 - Discharge message via Iguana from Norwood Hospital

```
MSH|^~\&|IGUANA|NORWOOD^4001^NPI|ADT_RECV|STEWARD_HIS|20250317153000||ADT^A03^ADT_A03|IG00004|P|2.4|||AL|NE
EVN|A03|20250317152900|||41928^Callahan^Derek^P^MD^^NPI
PID|1||NOR20123456^^^NOR^MR~318-52-7841^^^SSA^SS||Medeiros^Rafael^Tiago^^Mr.||19680522|M||2106-3^White^HL70005|78 Washington St^^Norwood^MA^02062^US||^PRN^PH^^^781^6429183||M||VN20012345|318-52-7841
PV1|1|I|MED^301^A^NOR^^^N|U|||41928^Callahan^Derek^P^MD^^NPI||52847^Valenzuela^Diana^M^MD^^NPI|MED|||1|||41928^Callahan^Derek^P^MD^^NPI|IN||BCBS|||||||||||||||||||NOR||||20250311072900|20250317153000
PV2|||^Acute kidney injury||||||20250311|20250317
DG1|1||N17.9^Acute kidney failure, unspecified^ICD10|||A
DG1|2||I10^Essential hypertension^ICD10|||S
DG1|3||E11.9^Type 2 diabetes mellitus without complications^ICD10|||S
```

---

## 5. ORU^R01 - Radiology report via Iguana from Good Samaritan

```
MSH|^~\&|IGUANA|GSMC^4003^NPI|RAD_RECV|STEWARD_HIS|20250319110000||ORU^R01^ORU_R01|IG00005|P|2.4|||AL|NE
PID|1||GSMC40345678^^^GSMC^MR||Soares^Daniela^Renata^^Mrs.||19820311|F||2131-1^Hispanic^HL70005|234 North Main St^^Brockton^MA^02301^US||^PRN^PH^^^508^7263914||M||VN40034567
PV1|1|E|ED^BED11^A^GSMC|||74185^Flanagan^Garrett^D^MD^^NPI|||||||||ER||||||||||||||||||GSMC||||20250315135000
ORC|RE|ORD30003|RAD40003||CM||||20250319110000|||74185^Flanagan^Garrett^D^MD^^NPI
OBR|1|ORD30003|RAD40003|74177^CT Abdomen with Contrast^CPT|||20250315153000|||||||||74185^Flanagan^Garrett^D^MD^^NPI||||||20250319110000||RAD|F
OBX|1|TX|RAD_RPT^Radiology Report^L||FINDINGS: The appendix measures 12mm in diameter with surrounding fat stranding~and a 5mm appendicolith at the base. No free fluid or abscess.~Mild mesenteric lymphadenopathy.~IMPRESSION: Acute uncomplicated appendicitis.||||||F|||20250319110000
```

---

## 6. MDM^T02 - Clinical document via Iguana from Heywood Healthcare

```
MSH|^~\&|IGUANA|HEYWOOD^4002^NPI|DOC_RECV|HH_HIS|20250321141500||MDM^T02^MDM_T02|IG00006|P|2.4|||AL|NE
EVN|T02|20250321141500
PID|1||HEY50456789^^^HEY^MR||Tremblay^Monique^Helene^^Mrs.||19580930|F||2106-3^White^HL70005|67 Parker St^^Gardner^MA^01440^US||^PRN^PH^^^978^2195843||W||VN50045678
PV1|1|O|PUL^CLINIC^A^HEYWOOD|||85203^Harrington^Nolan^W^MD^^NPI|||||||||OUT||||||||||||||||||HEY||||20250321130000
TXA|1|HP|TX|20250321141500|85203^Harrington^Nolan^W^MD^^NPI||20250321141500||||||DOC003456||AU||AV
OBX|1|TX|PULMNOTE^Pulmonology Note^L||CHIEF COMPLAINT: Follow-up for interstitial lung disease.~SUBJECTIVE: Patient reports stable dyspnea on exertion. No hemoptysis or chest pain.~OBJECTIVE: Lungs with bibasilar fine crackles. O2 sat 94% on room air.~PFTs show FVC 62% predicted, DLCO 48% predicted (unchanged from 3 months ago).~PLAN: Continue pirfenidone. Repeat PFTs in 3 months. Refer for pulmonary rehabilitation.||||||F
```

---

## 7. ADT^A04 - ED registration via Iguana from Holy Family Hospital

```
MSH|^~\&|IGUANA|HFH^4004^NPI|ADT_RECV|STEWARD_HIS|20250323193000||ADT^A04^ADT_A04|IG00007|P|2.4|||AL|NE
EVN|A04|20250323192900|||TRIAGE^Triage^Nurse^^^
PID|1||HFH60567890^^^HFH^MR~427-61-8935^^^SSA^SS||Tran^Minh^Duc^^Mr.||19910715|M||2028-9^Asian^HL70005|34 Jackson St^^Methuen^MA^01844^US||^PRN^PH^^^978^8417562||S||VN60056789|427-61-8935
PV1|1|E|ED^BED04^A^HFH^^^N|E|||96374^Mahoney^Colleen^R^MD^^NPI|||||||||ER||||||||||||||||||HFH||||20250323193000
PV2|||^Motor vehicle accident
NK1|1|Tran^Phuong^^Ms.|SIS|34 Jackson St^^Methuen^MA^01844^US|^PRN^PH^^^978^8417563||EC
DG1|1||V43.52XA^Car passenger injured in collision, initial encounter^ICD10|||W
```

---

## 8. ORU^R01 - Lab results with embedded PDF via Iguana from Norwood

```
MSH|^~\&|IGUANA|NORWOOD^4001^NPI|LAB_RECV|STEWARD_HIS|20250325091000||ORU^R01^ORU_R01|IG00008|P|2.4|||AL|NE
PID|1||NOR70678901^^^NOR^MR||Kowalski^Natalia^Irena^^Ms.||19790204|F||2106-3^White^HL70005|45 Dean St^^Norwood^MA^02062^US||^PRN^PH^^^781^3285941||S||VN70067890
PV1|1|I|MED^204^B^NOR|||29461^Sengupta^Vikram^A^MD^^NPI|||||||||IN||||||||||||||||||NOR||||20250323160000
ORC|RE|ORD40008|FIL50008||CM||||20250325091000|||29461^Sengupta^Vikram^A^MD^^NPI
OBR|1|ORD40008|FIL50008|86235^Nuclear Antibody Panel^CPT|||20250324080000|||||||||29461^Sengupta^Vikram^A^MD^^NPI||||||20250325091000||IM|F
OBX|1|ST|ANA^Antinuclear Antibody^L||Positive||Negative|A|||F|||20250325091000
OBX|2|NM|ANA_TITER^ANA Titer^L||1:640||<1:40|H|||F|||20250325091000
OBX|3|ST|ANA_PAT^ANA Pattern^L||Homogeneous||||||F|||20250325091000
OBX|4|NM|DSDNA^Anti-dsDNA Antibody^L||85|IU/mL|<30|H|||F|||20250325091000
OBX|5|NM|C3^Complement C3^L||52|mg/dL|90-180|L|||F|||20250325091000
OBX|6|NM|C4^Complement C4^L||8|mg/dL|10-40|L|||F|||20250325091000
OBX|7|ED|AUTOIMMUNE_RPT^Autoimmune Panel Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
NTE|1||Strongly positive ANA with anti-dsDNA and low complements. Pattern consistent with active SLE. Rheumatology consultation recommended.
```

---

## 9. ORM^O01 - Echocardiogram order via Iguana from Heywood

```
MSH|^~\&|IGUANA|HEYWOOD^4002^NPI|CARD_RECV|HH_HIS|20250327083000||ORM^O01^ORM_O01|IG00009|P|2.3|||AL|NE
PID|1||HEY80789012^^^HEY^MR||Duquette^Raymond^Arthur^^Mr.||19530618|M||2106-3^White^HL70005|89 Elm St^^Winchendon^MA^01475^US||^PRN^PH^^^978^5140872||M||VN80078901
PV1|1|O|CARD^CLINIC^A^HEYWOOD|||38521^Gallagher^Connor^T^MD^^NPI|||||||||OUT||||||||||||||||||HEY||||20250327080000
ORC|NW|ORD50009||||||^^^20250328090000^^R||20250327083000|||38521^Gallagher^Connor^T^MD^^NPI
OBR|1|ORD50009||93306^Echocardiogram Complete^CPT|||20250328090000||||||||38521^Gallagher^Connor^T^MD^^NPI|||||||||||1^^^20250328090000^^R
DG1|1||I50.9^Heart failure, unspecified^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||72 yo male with progressive dyspnea and lower extremity edema. Hx of MI 2019. On lisinopril, carvedilol, furosemide.||||||F
```

---

## 10. ADT^A08 - Insurance update via Iguana from Good Samaritan

```
MSH|^~\&|IGUANA|GSMC^4003^NPI|ADT_RECV|STEWARD_HIS|20250329101000||ADT^A08^ADT_A08|IG00010|P|2.4|||AL|NE
EVN|A08|20250329100900|||ADMIN^Admin^System^^^
PID|1||GSMC90890123^^^GSMC^MR~531-84-2067^^^SSA^SS||Villanueva^Carmen^Yolanda^^Mrs.||19750928|F||2131-1^Hispanic^HL70005|56 Court St^^Brockton^MA^02302^US||^PRN^PH^^^508^4917328||M||VN90089012|531-84-2067
PV1|1|O|OB^CLINIC^A^GSMC|||18734^Huynh^Linh^T^MD^^NPI|||||||||OUT||||||||||||||||||GSMC||||20250329093000
IN1|1|MASS001^MassHealth|1234|MassHealth|One Ashburton Place^^Boston^MA^02108^US|^PRN^PH^^^800^8414900|GRP00000|||||||Villanueva^Carmen^Yolanda|SEL|19750928|56 Court St^^Brockton^MA^02302^US|||||||||||||||||531842067
IN2|1|||||||||||||||||||||||||||||||||||19750928|F
```

---

## 11. ORU^R01 - Microbiology results via Iguana from Holy Family

```
MSH|^~\&|IGUANA|HFH^4004^NPI|LAB_RECV|STEWARD_HIS|20250331143000||ORU^R01^ORU_R01|IG00011|P|2.4|||AL|NE
PID|1||HFH01901234^^^HFH^MR||Boivin^Normand^Gerard^^Mr.||19680330|M||2106-3^White^HL70005|78 Hampshire St^^Methuen^MA^01844^US||^PRN^PH^^^978^6532841||M||VN01090123
PV1|1|I|MED^212^A^HFH|||47291^Sheehan^Erin^M^MD^^NPI|||||||||IN||||||||||||||||||HFH||||20250329200000
ORC|RE|ORD60011|MIC70011||CM||||20250331143000|||47291^Sheehan^Erin^M^MD^^NPI
OBR|1|ORD60011|MIC70011|87081^Wound Culture^CPT|||20250329220000|||||||||47291^Sheehan^Erin^M^MD^^NPI||||||20250331143000||MB|F
OBX|1|CE|CULTURE^Culture Result^L||Pseudomonas aeruginosa|||A|||F|||20250331143000
OBX|2|TX|SUSCEPT^Susceptibility^L||Piperacillin/Tazobactam: Sensitive~Cefepime: Sensitive~Meropenem: Sensitive~Ciprofloxacin: Resistant~Gentamicin: Intermediate~Tobramycin: Sensitive||||||F|||20250331143000
OBX|3|TX|COMMENT^Lab Comment^L||Heavy growth of Pseudomonas aeruginosa from right lower extremity wound.~Note ciprofloxacin resistance.||||||F|||20250331143000
```

---

## 12. MDM^T02 - Operative note via Iguana from Norwood Hospital

```
MSH|^~\&|IGUANA|NORWOOD^4001^NPI|DOC_RECV|STEWARD_HIS|20250402161000||MDM^T02^MDT_T02|IG00012|P|2.4|||AL|NE
EVN|T02|20250402161000
PID|1||NOR02012345^^^NOR^MR||Doherty^Seamus^Patrick^^Mr.||19600812|M||2106-3^White^HL70005|23 Prospect St^^Norwood^MA^02062^US||^PRN^PH^^^781^9374125||M||VN02001234
PV1|1|I|SURG^401^A^NOR|||58163^Cardoso^Mateus^E^MD^^NPI|||||||||IN||||||||||||||||||NOR||||20250402060000
TXA|1|OP|TX|20250402161000|58163^Cardoso^Mateus^E^MD^^NPI||20250402161000||||||DOC004567||AU||AV
OBX|1|TX|OPNOTE^Operative Note^L||PROCEDURE: Laparoscopic cholecystectomy~ANESTHESIA: General~FINDINGS: Chronically inflamed gallbladder with multiple calculi. Cystic duct identified and clipped.~No bile leak. Liver bed hemostatic.~ESTIMATED BLOOD LOSS: 25 mL~COMPLICATIONS: None~DISPOSITION: Patient to PACU in stable condition.||||||F
```

---

## 13. ORU^R01 - Cardiac enzymes via Iguana from Holy Family Hospital

```
MSH|^~\&|IGUANA|HFH^4004^NPI|LAB_RECV|STEWARD_HIS|20250404041500||ORU^R01^ORU_R01|IG00013|P|2.4|||AL|NE
PID|1||HFH03123456^^^HFH^MR||Kowalczyk^Stanislaw^Marek^^Mr.||19550920|M||2106-3^White^HL70005|123 Broadway^^Haverhill^MA^01832^US||^PRN^PH^^^978^2714093||M||VN03012345
PV1|1|E|ED^BED08^A^HFH|||82495^Vo^Quang^H^MD^^NPI|||||||||ER||||||||||||||||||HFH||||20250404020000
ORC|RE|ORD70013|FIL80013||CM||||20250404041500|||82495^Vo^Quang^H^MD^^NPI
OBR|1|ORD70013|FIL80013|CARDIAC^Cardiac Biomarkers^L|||20250404033000|||||||||82495^Vo^Quang^H^MD^^NPI||||||20250404041500||CH|F
OBX|1|NM|TROP^Troponin I^L||0.15|ng/mL|0.00-0.04|H|||F|||20250404041500
OBX|2|NM|BNP^Brain Natriuretic Peptide^L||580|pg/mL|0-100|HH|||F|||20250404041500
OBX|3|NM|CK^Creatine Kinase^L||312|U/L|30-200|H|||F|||20250404041500
OBX|4|NM|CKMB^CK-MB^L||22.4|ng/mL|0.0-5.0|HH|||F|||20250404041500
NTE|1||Elevated troponin and CK-MB consistent with myocardial injury. Serial troponins recommended.
```

---

## 14. ADT^A02 - Patient transfer via Iguana from Good Samaritan

```
MSH|^~\&|IGUANA|GSMC^4003^NPI|ADT_RECV|STEWARD_HIS|20250406082000||ADT^A02^ADT_A02|IG00014|P|2.4|||AL|NE
EVN|A02|20250406081900|||61843^Devereaux^Maura^A^MD^^NPI
PID|1||GSMC04234567^^^GSMC^MR||Celestin^Frantz^Wilner^^Mr.||19470515|M||2054-5^Black^HL70005|89 Pleasant St^^Brockton^MA^02301^US||^PRN^PH^^^508^3826147||M||VN04023456
PV1|1|I|ICU^BED05^A^GSMC^^^N|E|||61843^Devereaux^Maura^A^MD^^NPI||73290^Kwon^David^L^MD^^NPI|MED|||2|||61843^Devereaux^Maura^A^MD^^NPI|IN||MEDCR|||||||||||||||||||GSMC||||20250404180000
PV2|||^Acute respiratory failure requiring mechanical ventilation
DG1|1||J96.01^Acute respiratory failure with hypoxia^ICD10|||A
DG1|2||J18.9^Pneumonia, unspecified organism^ICD10|||S
```

---

## 15. ORU^R01 - Drug levels via Iguana from Heywood Healthcare

```
MSH|^~\&|IGUANA|HEYWOOD^4002^NPI|LAB_RECV|HH_HIS|20250408090000||ORU^R01^ORU_R01|IG00015|P|2.4|||AL|NE
PID|1||HEY05345678^^^HEY^MR||Chouinard^Therese^Lorraine^^Mrs.||19620413|F||2106-3^White^HL70005|34 Oak St^^Athol^MA^01331^US||^PRN^PH^^^978^7493021||M||VN05034567
PV1|1|I|MED^108^A^HEYWOOD|||49312^Herrera^Miguel^R^MD^^NPI|||||||||IN||||||||||||||||||HEY||||20250406120000
ORC|RE|ORD80015|FIL90015||CM||||20250408090000|||49312^Herrera^Miguel^R^MD^^NPI
OBR|1|ORD80015|FIL90015|80202^Vancomycin Level^CPT|||20250408060000|||||||||49312^Herrera^Miguel^R^MD^^NPI||||||20250408090000||TDM|F
OBX|1|NM|VANCO_TR^Vancomycin Trough^L||22.5|mcg/mL|15.0-20.0|H|||F|||20250408090000
OBX|2|NM|VANCO_PK^Vancomycin Peak^L||42.0|mcg/mL|25.0-40.0|H|||F|||20250408090000
OBX|3|NM|CREAT^Creatinine^L||1.4|mg/dL|0.7-1.3|H|||F|||20250408090000
NTE|1||Vancomycin trough above target range. Consider dose reduction. Monitor renal function closely.
```

---

## 16. ORM^O01 - MRI lumbar spine order via Iguana from Norwood

```
MSH|^~\&|IGUANA|NORWOOD^4001^NPI|RAD_RECV|STEWARD_HIS|20250410111500||ORM^O01^ORM_O01|IG00016|P|2.3|||AL|NE
PID|1||NOR06456789^^^NOR^MR||Almeida^Marcos^Henrique^^Mr.||19700822|M||2131-1^Hispanic^HL70005|156 Nahatan St^^Norwood^MA^02062^US||^PRN^PH^^^781^4618273||M||VN06045678
PV1|1|O|ORTH^CLINIC^A^NOR|||37294^Brennan^Declan^M^MD^^NPI|||||||||OUT||||||||||||||||||NOR||||20250410100000
ORC|NW|ORD90016||||||^^^20250412080000^^R||20250410111500|||37294^Brennan^Declan^M^MD^^NPI
OBR|1|ORD90016||72148^MRI Lumbar Spine without Contrast^CPT|||20250412080000||||||||37294^Brennan^Declan^M^MD^^NPI|||||||||||1^^^20250412080000^^R
DG1|1||M54.5^Low back pain^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||54 yo male with 6 weeks of low back pain radiating to left leg. Failed conservative therapy. R/O disc herniation.||||||F
```

---

## 17. ORU^R01 - Electrolyte panel via Iguana from Good Samaritan

```
MSH|^~\&|IGUANA|GSMC^4003^NPI|LAB_RECV|STEWARD_HIS|20250412063000||ORU^R01^ORU_R01|IG00017|P|2.4|||AL|NE
PID|1||GSMC07567890^^^GSMC^MR||Jankowski^Halina^Ewa^^Mrs.||19680505|F||2106-3^White^HL70005|78 Centre St^^Brockton^MA^02302^US||^PRN^PH^^^508^6195247||M||VN07056789
PV1|1|I|MED^3E^C^GSMC|||20583^Nassif^Tariq^H^MD^^NPI|||||||||IN||||||||||||||||||GSMC||||20250410180000
ORC|RE|ORD01017|FIL11017||CM||||20250412063000|||20583^Nassif^Tariq^H^MD^^NPI
OBR|1|ORD01017|FIL11017|80051^Electrolyte Panel^CPT|||20250412050000|||||||||20583^Nassif^Tariq^H^MD^^NPI||||||20250412063000||CH|F
OBX|1|NM|NA^Sodium^L||128|mmol/L|136-145|LL|||F|||20250412063000
OBX|2|NM|K^Potassium^L||3.0|mmol/L|3.5-5.1|L|||F|||20250412063000
OBX|3|NM|CL^Chloride^L||92|mmol/L|98-106|L|||F|||20250412063000
OBX|4|NM|CO2^Carbon Dioxide^L||30|mmol/L|23-29|H|||F|||20250412063000
OBX|5|NM|MG^Magnesium^L||1.2|mg/dL|1.7-2.2|L|||F|||20250412063000
NTE|1||Severe hyponatremia (128). Hypokalemia and hypomagnesemia also present. Urgent correction needed.
```

---

## 18. MDM^T02 - Consultation note with embedded PDF via Iguana from Heywood

```
MSH|^~\&|IGUANA|HEYWOOD^4002^NPI|DOC_RECV|HH_HIS|20250414140000||MDM^T02^MDM_T02|IG00018|P|2.4|||AL|NE
EVN|T02|20250414140000
PID|1||HEY08678901^^^HEY^MR||Lefebvre^Gaston^Roland^^Mr.||19470829|M||2106-3^White^HL70005|12 Prospect St^^Fitchburg^MA^01420^US||^PRN^PH^^^978^8421356||W||VN08067890
PV1|1|I|MED^205^B^HEYWOOD|||14829^Okafor^Emmanuel^C^MD^^NPI|||||||||IN||||||||||||||||||HEY||||20250412080000
TXA|1|CN|TX|20250414140000|27654^Driscoll^Fiona^S^MD^^NPI||20250414140000||||||DOC005678||AU||AV
OBX|1|TX|CONSULT^Cardiology Consultation^L||REASON FOR CONSULTATION: New onset atrial fibrillation~HISTORY: 77 yo male admitted for pneumonia, found to have afib with RVR.~Heart rate 128 on telemetry. No prior history of arrhythmia.~ECHO: EF 50%, mild MR, LA dilated at 4.5 cm.~ASSESSMENT: New onset atrial fibrillation, likely triggered by infection.~CHA2DS2-VASc score: 4 (age, HTN, DM, vascular disease).~PLAN: Rate control with diltiazem. Anticoagulate with apixaban once infection controlled.||||||F
OBX|2|ED|CONSULT_PDF^Cardiology Consultation PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 19. ADT^A28 - New patient via Iguana from community health center

```
MSH|^~\&|IGUANA|EMKCHC^4005^NPI|MPI_RECV|CHC_HIS|20250416090000||ADT^A28^ADT_A28|IG00019|P|2.4|||AL|NE
EVN|A28|20250416090000|||REGISTRATION^Reg^System^^^
PID|1||EMKCHC09789012^^^EMKCHC^MR~642-83-1975^^^SSA^SS||Fonseca^Adriana^Beatriz^^Ms.||19950311|F||2131-1^Hispanic^HL70005|234 Main St^^Worcester^MA^01608^US||^PRN^PH^^^508^2831497||S||VN09078901|642-83-1975
PD1||||59371^Castillo^Veronica^L^MD^^NPI
NK1|1|Fonseca^Rodrigo^^Mr.|FTH|234 Main St^^Worcester^MA^01608^US|^PRN^PH^^^508^2831498||EC
IN1|1|MASS001^MassHealth|1234|MassHealth|One Ashburton Place^^Boston^MA^02108^US|^PRN^PH^^^800^8414900|GRP00000|||||||Fonseca^Adriana^Beatriz|SEL|19950311|234 Main St^^Worcester^MA^01608^US|||||||||||||||||642831975
```

---

## 20. ORU^R01 - Hemoglobin electrophoresis via Iguana from Good Samaritan

```
MSH|^~\&|IGUANA|GSMC^4003^NPI|LAB_RECV|STEWARD_HIS|20250418100000||ORU^R01^ORU_R01|IG00020|P|2.4|||AL|NE
PID|1||GSMC10890123^^^GSMC^MR||Thermidor^Guerline^Solange^^Mrs.||19850617|F||2054-5^Black^HL70005|45 Warren Ave^^Brockton^MA^02301^US||^PRN^PH^^^508^7412938||M||VN10089012
PV1|1|O|HEM^CLINIC^A^GSMC|||84526^Okonkwo^Chisom^T^MD^^NPI|||||||||OUT||||||||||||||||||GSMC||||20250418083000
ORC|RE|ORD11020|FIL22020||CM||||20250418100000|||84526^Okonkwo^Chisom^T^MD^^NPI
OBR|1|ORD11020|FIL22020|83020^Hemoglobin Electrophoresis^CPT|||20250418083000|||||||||84526^Okonkwo^Chisom^T^MD^^NPI||||||20250418100000||HM|F
OBX|1|NM|HBA^Hemoglobin A^L||56.2|%|>95|L|||F|||20250418100000
OBX|2|NM|HBS^Hemoglobin S^L||38.5|%|0|H|||F|||20250418100000
OBX|3|NM|HBA2^Hemoglobin A2^L||3.8|%|2.0-3.3|H|||F|||20250418100000
OBX|4|NM|HBF^Hemoglobin F^L||1.5|%|<2.0||||F|||20250418100000
NTE|1||Hemoglobin electrophoresis pattern consistent with sickle cell trait (HbAS). Genetic counseling recommended.
```
