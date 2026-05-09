# Epic Systems - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to trauma surgery at Vanderbilt

```
MSH|^~\&|EPIC|VUMC^2.16.840.1.113883.3.1562^ISO|ADT_RECV|TN_HIE|20260501083015||ADT^A01^ADT_A01|MSG20260501083015001|P|2.5.1|||AL|NE
EVN|A01|20260501082500|||PCOLEMAN^Coleman^Patricia^J^^^MD|20260501082500
PID|1||MRN10012345^^^VUMC^MR~471-38-9204^^^USSSA^SS||Caldwell^Terrence^Marquise^^Mr.^||19870614|M||2054-5^Black or African American^CDCREC|1801 West End Ave^^Nashville^TN^37232^US^H||^PRN^PH^^1^615^5559201|^WPN^PH^^1^615^5550384||S^Single^HL70002|||471-38-9204|||N^Not Hispanic or Latino^CDCREC
PD1|||Vanderbilt University Medical Center^^^^NPI|1538274690^Whitmore^Andrea^L^^^MD^^^^NPI
NK1|1|Caldwell^Gloria^Marie^^Mrs.|MTH^Mother^HL70063|2204 Jefferson St^^Nashville^TN^37208^US|^PRN^PH^^1^615^5559202||EC^Emergency Contact^HL70131
PV1|1|I|TRAU^6204^01^VUMC^^^^N|E^Emergency^HL70007|||1647382951^Okafor^Chukwuemeka^N^^^MD^^^^NPI|1730495826^Hensley^Victoria^R^^^MD^^^^NPI|SUR^Surgery^HL70069||||||A^Accident^HL70007|||||VN20260501001^^^VUMC^VN|||||||||||||||||||||||||20260501082500
PV2|||^Motor vehicle collision with multiple injuries||||||20260501|5||||||||||||N
DG1|1||S72.001A^Fracture of unspecified part of neck of right femur initial encounter^I10||20260501|A
DG1|2||S27.0XXA^Traumatic pneumothorax initial encounter^I10||20260501|A
GT1|1||Caldwell^Terrence^Marquise^^Mr.||1801 West End Ave^^Nashville^TN^37232^US|^PRN^PH^^1^615^5559201|||||SE^Self^HL70063||||||||||||||||||||||||||||||||87654321
IN1|1|BCBS001|54321^BlueCross BlueShield of Tennessee|BCBSTN^^Chattanooga^TN^37402|||||GRP887766||||||Caldwell^Terrence^Marquise|SE^Self^HL70063|19870614|1801 West End Ave^^Nashville^TN^37232^US|Y||1||||||||||||||POL665544
```

---

## 2. ADT^A03 - Patient discharge from cardiac step-down at TriStar Centennial

```
MSH|^~\&|EPICADT|TRISTAR^2.16.840.1.113883.3.3301^ISO|ADT_RECV|TN_HIE|20260502141200||ADT^A03^ADT_A03|MSG20260502141200002|P|2.5.1|||AL|NE
EVN|A03|20260502140500|||JMORGAN^Morgan^Jennifer^A^^^MD|20260502140500
PID|1||MRN20023456^^^TRISTAR^MR||Bradshaw^Harold^Eugene^^Mr.^||19530318|M||2106-3^White^CDCREC|4408 Harding Pike^^Nashville^TN^37205^US^H||^PRN^PH^^1^615^5553847|||M^Married^HL70002|||518-73-4462|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|CSTD^3108^01^TRISTAR^^^^N|U^Urgent^HL70007|||1482637509^Mahajan^Ravi^P^^^MD^^^^NPI|1593748260^Trevino^Sandra^L^^^MD^^^^NPI|CAR^Cardiology^HL70069||||||R^Referral^HL70007|||||VN20260428002^^^TRISTAR^VN|||||||||||||||||||01^Discharged to home^HL70112||||20260428090000|20260502140500
PV2|||^Congestive heart failure exacerbation
DG1|1||I50.23^Acute on chronic systolic heart failure^I10||20260428|A
DG1|2||I10^Essential primary hypertension^I10||20260428|A
PR1|1||93306^Echocardiography transthoracic^CPT4|^Transthoracic echocardiogram|20260429100000|||||1482637509^Mahajan^Ravi^P^^^MD^^^^NPI
```

---

## 3. ORU^R01 - Comprehensive metabolic panel results from Vanderbilt pathology

```
MSH|^~\&|EPICCARE|VUMC^2.16.840.1.113883.3.1562^ISO|LAB_RECV|TN_HIE|20260503074530||ORU^R01^ORU_R01|MSG20260503074530003|P|2.5.1|||AL|NE
PID|1||MRN30034567^^^VUMC^MR||Washington^Loretta^Denise^^Mrs.^||19681109|F||2054-5^Black or African American^CDCREC|308 Broadway^^Nashville^TN^37201^US^H||^PRN^PH^^1^615^5557812|||M^Married^HL70002|||612-49-8307|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|LAB^0001^01^VUMC^^^^N|R^Routine^HL70007|||1825937460^Narayanan^Vikram^S^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260503003^^^VUMC^VN
ORC|RE|ORD30001^EPIC|FIL30001^LAB||CM^Complete^HL70038|||20260503060000|||1825937460^Narayanan^Vikram^S^^^MD^^^^NPI
OBR|1|ORD30001^EPIC|FIL30001^LAB|80053^Comprehensive metabolic panel^CPT4|||20260503060000|||||||||1825937460^Narayanan^Vikram^S^^^MD^^^^NPI||||||20260503073000|||F
OBX|1|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||98|mg/dL^milligrams per deciliter^UCUM|74-106|N|||F|||20260503073000
OBX|2|NM|3094-0^Urea nitrogen [Mass/volume] in Serum or Plasma^LN||18|mg/dL^milligrams per deciliter^UCUM|6-20|N|||F|||20260503073000
OBX|3|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||1.1|mg/dL^milligrams per deciliter^UCUM|0.7-1.3|N|||F|||20260503073000
OBX|4|NM|17861-6^Calcium [Mass/volume] in Serum or Plasma^LN||9.4|mg/dL^milligrams per deciliter^UCUM|8.5-10.5|N|||F|||20260503073000
OBX|5|NM|2951-2^Sodium [Moles/volume] in Serum or Plasma^LN||140|mmol/L^millimoles per liter^UCUM|136-145|N|||F|||20260503073000
OBX|6|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN||4.2|mmol/L^millimoles per liter^UCUM|3.5-5.1|N|||F|||20260503073000
OBX|7|NM|2075-0^Chloride [Moles/volume] in Serum or Plasma^LN||102|mmol/L^millimoles per liter^UCUM|98-106|N|||F|||20260503073000
OBX|8|NM|2028-9^Carbon dioxide total [Moles/volume] in Serum or Plasma^LN||24|mmol/L^millimoles per liter^UCUM|20-29|N|||F|||20260503073000
OBX|9|NM|1751-7^Albumin [Mass/volume] in Serum or Plasma^LN||4.0|g/dL^grams per deciliter^UCUM|3.5-5.5|N|||F|||20260503073000
OBX|10|NM|1975-2^Bilirubin total [Mass/volume] in Serum or Plasma^LN||0.8|mg/dL^milligrams per deciliter^UCUM|0.1-1.2|N|||F|||20260503073000
OBX|11|NM|6768-6^Alkaline phosphatase [Enzymatic activity/volume] in Serum or Plasma^LN||72|U/L^units per liter^UCUM|44-147|N|||F|||20260503073000
OBX|12|NM|1742-6^Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||28|U/L^units per liter^UCUM|7-56|N|||F|||20260503073000
OBX|13|NM|1920-8^Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||25|U/L^units per liter^UCUM|10-40|N|||F|||20260503073000
OBX|14|NM|2885-2^Protein [Mass/volume] in Serum or Plasma^LN||7.1|g/dL^grams per deciliter^UCUM|6.0-8.3|N|||F|||20260503073000
```

---

## 4. ORM^O01 - MRI lumbar spine order from Saint Thomas Midtown

```
MSH|^~\&|EPIC|STMID^2.16.840.1.113883.3.4150^ISO|RAD_RECV|TN_HIE|20260504101500||ORM^O01^ORM_O01|MSG20260504101500004|P|2.5.1|||AL|NE
PID|1||MRN40045678^^^STMID^MR||Hargrove^Tamara^Elise^^Ms.^||19790825|F||2106-3^White^CDCREC|4004 Hillsboro Pike^^Nashville^TN^37215^US^H||^PRN^PH^^1^615^5558193|||D^Divorced^HL70002|||283-61-7945|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^0008^01^STMID^^^^N|R^Routine^HL70007|||1946372850^Kirkland^Randall^T^^^MD^^^^NPI||ORT^Orthopedics^HL70069||||||||||VN20260504004^^^STMID^VN
ORC|NW|ORD40001^EPIC||GRP40001^EPIC|||||20260504100000|||1946372850^Kirkland^Randall^T^^^MD^^^^NPI|||||STMID^Saint Thomas Midtown Hospital
OBR|1|ORD40001^EPIC||72148^MRI lumbar spine without contrast^CPT4|||20260504100000||||||||1946372850^Kirkland^Randall^T^^^MD^^^^NPI||||||||||1^Routine^HL70065
DG1|1||M54.5^Low back pain^I10||20260504|A
DG1|2||M51.16^Intervertebral disc degeneration lumbar region^I10||20260504|A
NTE|1||Chronic low back pain with radiculopathy. Failed conservative management over 6 weeks.
```

---

## 5. ORU^R01 - Surgical pathology report with embedded PDF (ED datatype) from Vanderbilt

```
MSH|^~\&|EPICCARE|VUMC^2.16.840.1.113883.3.1562^ISO|PATH_RECV|TN_HIE|20260505160045||ORU^R01^ORU_R01|MSG20260505160045005|P|2.5.1|||AL|NE
PID|1||MRN50056789^^^VUMC^MR||Whitley^Sandra^Yvonne^^Mrs.^||19650212|F||2106-3^White^CDCREC|2115 Belcourt Ave^^Nashville^TN^37212^US^H||^PRN^PH^^1^615^5554082|||W^Widowed^HL70002|||390-52-8176|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|PATH^0003^01^VUMC^^^^N|R^Routine^HL70007|||1374926085^Anand^Priya^K^^^MD^^^^NPI||PAT^Pathology^HL70069||||||||||VN20260505005^^^VUMC^VN
ORC|RE|ORD50001^EPIC|FIL50001^PATH||CM^Complete^HL70038|||20260504110000|||1374926085^Anand^Priya^K^^^MD^^^^NPI
OBR|1|ORD50001^EPIC|FIL50001^PATH|88305^Surgical pathology^CPT4|||20260503140000|||||||||1374926085^Anand^Priya^K^^^MD^^^^NPI||||||20260505155000|||F
OBX|1|ED|PDF^Pathology Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA1OAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKFZ1bWMgU3VyZ2ljYWwgUGF0aG9sb2d5IFJlcG9ydCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCg==||||||F|||20260505155000
OBX|2|FT|22634-0^Pathology report final diagnosis^LN||Specimen: Right colon, hemicolectomy\.br\Gross: 18 cm segment of colon with a 3.2 cm polypoid mass\.br\Diagnosis: Moderately differentiated adenocarcinoma of the cecum\.br\Depth of invasion: Through muscularis propria into pericolonic adipose tissue (pT3)\.br\Lymph nodes: 0 of 22 positive for metastatic carcinoma (pN0)\.br\Margins: Proximal, distal, and radial margins negative for carcinoma\.br\Lymphovascular invasion: Not identified\.br\Perineural invasion: Not identified||||||F|||20260505155000
```

---

## 6. ADT^A08 - Patient information update at TriStar Skyline

```
MSH|^~\&|EPICADT|TRSKY^2.16.840.1.113883.3.3302^ISO|ADT_RECV|TN_HIE|20260506110000||ADT^A08^ADT_A01|MSG20260506110000006|P|2.5.1|||AL|NE
EVN|A08|20260506105500|||LHENDERSON^Henderson^Lisa^M^^^RN|20260506105500
PID|1||MRN60067890^^^TRSKY^MR||Fuentes^Ricardo^Alejandro^^Mr.^||19810524|M||2106-3^White^CDCREC|3210 Dickerson Pike^^Nashville^TN^37207^US^H||^PRN^PH^^1^615^5551894|^WPN^PH^^1^615^5557743||M^Married^HL70002|||534-29-8817|||H^Hispanic or Latino^CDCREC
PD1|||TriStar Skyline Medical Center^^^^NPI|1052738496^Ellison^Gregory^W^^^MD^^^^NPI
NK1|1|Fuentes^Lucia^Carmen^^Mrs.|SPO^Spouse^HL70063|3210 Dickerson Pike^^Nashville^TN^37207^US|^PRN^PH^^1^615^5551895||EC^Emergency Contact^HL70131
PV1|1|I|MED^2401^01^TRSKY^^^^N|E^Emergency^HL70007|||1052738496^Ellison^Gregory^W^^^MD^^^^NPI||MED^Medicine^HL70069||||||||||VN20260503006^^^TRSKY^VN|||||||||||||||||||||||||||20260503163000
IN1|1|TENN001|70098^TennCare Managed Care|TennCare^^Nashville^TN^37243|||||TCGRP445566||||||Fuentes^Ricardo^Alejandro|SE^Self^HL70063|19810524|3210 Dickerson Pike^^Nashville^TN^37207^US|Y||1||||||||||||||TCPOL998877
IN2|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||Fuentes^Ricardo^Alejandro
```

---

## 7. SIU^S12 - Appointment scheduling for cardiac catheterization at Vanderbilt

```
MSH|^~\&|EPIC|VUMC^2.16.840.1.113883.3.1562^ISO|SCHED_RECV|TN_HIE|20260507091000||SIU^S12^SIU_S12|MSG20260507091000007|P|2.5.1|||AL|NE
SCH|APPT70001^EPIC||||||CATH^Cardiac Catheterization^L|60^MIN|MIN^Minutes^ISO+|^^^20260514080000^^60^MIN|||||1463820597^Barrett^Lawrence^E^^^MD^^^^NPI|^PRN^PH^^1^615^5553210|||||1463820597^Barrett^Lawrence^E^^^MD^^^^NPI|||||Booked
PID|1||MRN70078901^^^VUMC^MR||Donovan^Clayton^Wesley^^Mr.^||19590730|M||2106-3^White^CDCREC|1009 18th Ave S^^Nashville^TN^37212^US^H||^PRN^PH^^1^615^5559471|||M^Married^HL70002|||703-28-4419|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|CATH^0002^01^VUMC^^^^N|R^Routine^HL70007|||1463820597^Barrett^Lawrence^E^^^MD^^^^NPI||CAR^Cardiology^HL70069||||||||||VN20260507007^^^VUMC^VN
RGS|1||CARD_CATH
AIS|1||93458^Left heart catheterization^CPT4|20260514080000|||60^MIN|MIN^Minutes^ISO+||Confirmed
AIG|1||1463820597^Barrett^Lawrence^E^^^MD^^^^NPI|||||20260514080000|||60^MIN
AIL|1||CATH^0002^01^VUMC|||||20260514080000|||60^MIN
NTE|1||Positive stress test. Evaluate for coronary artery disease. NPO after midnight.
```

---

## 8. RDE^O11 - Pharmacy order for warfarin at Ballad Health

```
MSH|^~\&|EPIC|BALLAD^2.16.840.1.113883.3.5501^ISO|PHARM_RECV|TN_HIE|20260507143000||RDE^O11^RDE_O11|MSG20260507143000008|P|2.5.1|||AL|NE
PID|1||MRN80089012^^^BALLAD^MR||Felton^Dorothy^Mae^^Mrs.^||19470609|F||2106-3^White^CDCREC|412 E Main St^^Johnson City^TN^37604^US^H||^PRN^PH^^1^423^5558342|||W^Widowed^HL70002|||741-56-3298|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|MED^4210^01^BALLAD^^^^N|U^Urgent^HL70007|||1285034679^Underwood^Travis^H^^^MD^^^^NPI||HEM^Hematology^HL70069||||||||||VN20260505008^^^BALLAD^VN
ORC|NW|ORD80001^EPIC||GRP80001^EPIC|||||20260507142000|||1285034679^Underwood^Travis^H^^^MD^^^^NPI
RXE|1^QD^HL70335|11289^Warfarin 5mg tablet^NDC|5|5|mg^milligrams^ISO+|TAB^Tablet^HL70292|||||30|EA^each^ISO+||1285034679^Underwood^Travis^H^^^MD^^^^NPI|||||||||||||0^No refills
RXR|PO^Oral^HL70162
DG1|1||I26.99^Other pulmonary embolism without acute cor pulmonale^I10||20260505|A
NTE|1||Target INR 2.0-3.0. Check INR in 3 days. Patient educated on dietary vitamin K interactions.
```

---

## 9. MDM^T02 - Transcribed operative note at Vanderbilt

```
MSH|^~\&|EPICCARE|VUMC^2.16.840.1.113883.3.1562^ISO|DOC_RECV|TN_HIE|20260508170000||MDM^T02^MDM_T02|MSG20260508170000009|P|2.5.1|||AL|NE
EVN|T02|20260508165500
PID|1||MRN90090123^^^VUMC^MR||Pennington^Rachel^Danielle^^Ms.^||19830417|F||2106-3^White^CDCREC|512 12th Ave S^^Nashville^TN^37203^US^H||^PRN^PH^^1^615^5556734|||S^Single^HL70002|||408-71-2563|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|SURG^4502^01^VUMC^^^^N|E^Emergency^HL70007|||1729405836^Yoon^Daniel^J^^^MD^^^^NPI||SUR^Surgery^HL70069||||||||||VN20260507009^^^VUMC^VN|||||||||||||||||||||||||||20260507210000|20260508160000
TXA|1|OP^Operative Note^HL70270|TX^Text^HL70191||20260508165000||||||DOC9001^VUMC|||||AU^Authenticated^HL70271
OBX|1|TX|11504-8^Surgical operation note^LN||OPERATIVE NOTE\.br\Patient: Pennington, Rachel Danielle\.br\DOB: 04/17/1983\.br\Date of Surgery: 05/07/2026\.br\Surgeon: Daniel J. Yoon, MD\.br\Assistant: Megan K. Ashford, MD\.br\\.br\PREOPERATIVE DIAGNOSIS: Acute appendicitis\.br\POSTOPERATIVE DIAGNOSIS: Acute perforated appendicitis with localized peritonitis\.br\\.br\PROCEDURE: Laparoscopic appendectomy converted to open appendectomy\.br\\.br\ANESTHESIA: General endotracheal\.br\\.br\FINDINGS: Appendix was perforated at the tip with purulent fluid in the right lower quadrant. No free air. Cecum appeared normal without mass.\.br\\.br\DESCRIPTION: Patient positioned supine. After induction of general anesthesia, abdomen prepped and draped in usual sterile fashion. Infraumbilical incision made and Veress needle placed. Pneumoperitoneum established to 15 mmHg. 12mm trocar placed. Laparoscope inserted revealing purulent fluid and adhesions surrounding the appendix. Due to dense adhesions, decision made to convert to open approach via McBurney incision. Appendix identified, mesoappendix divided using LigaSure. Appendix transected at base with endoGIA stapler. Specimen placed in EndoCatch bag and removed. Abdomen irrigated with warm saline. Hemostasis confirmed. Fascia closed with 0-Vicryl. Skin closed with 4-0 Monocryl subcuticular.\.br\\.br\ESTIMATED BLOOD LOSS: 75 mL\.br\SPECIMENS: Appendix to pathology\.br\DISPOSITION: To PACU in stable condition||||||F|||20260508165000
```

---

## 10. DFT^P03 - Emergency department charge posting at Erlanger Baroness

```
MSH|^~\&|EPIC|ERLANG^2.16.840.1.113883.3.6601^ISO|FIN_RECV|TN_HIE|20260509080000||DFT^P03^DFT_P03|MSG20260509080000010|P|2.5.1|||AL|NE
EVN|P03|20260509075500
PID|1||MRN01101234^^^ERLANG^MR||Strickland^Derek^Wayne^^Mr.^||19920328|M||2106-3^White^CDCREC|1400 McCallie Ave^^Chattanooga^TN^37403^US^H||^PRN^PH^^1^423^5551237|||S^Single^HL70002|||629-13-5847|||N^Not Hispanic or Latino^CDCREC
PV1|1|E|ED^0001^T5^ERLANG^^^^N|E^Emergency^HL70007|||1638502974^Odom^Cassandra^K^^^MD^^^^NPI||EM^Emergency Medicine^HL70069||||||||||VN20260508010^^^ERLANG^VN|||||||||||||||||||||||||||20260508193000|20260509020000
FT1|1|||20260508193000|20260509020000|CG^Charge^HL70017|99284^ED visit level 4^CPT4||1|||||||ED^0001^T5^ERLANG|||||1638502974^Odom^Cassandra^K^^^MD^^^^NPI
FT1|2|||20260508200000|20260508200000|CG^Charge^HL70017|73610^X-ray ankle complete 3 views^CPT4||1|||||||RAD^0001^01^ERLANG
FT1|3|||20260508210000|20260508210000|CG^Charge^HL70017|29515^Short leg splint application^CPT4||1|||||||ED^0001^T5^ERLANG
DG1|1||S82.891A^Other fracture of right lower leg initial encounter^I10||20260508|A
```

---

## 11. VXU^V04 - Infant immunization administration at UT Medical Center Knoxville

```
MSH|^~\&|EPICCARE|UTMC^2.16.840.1.113883.3.7702^ISO|TENNIIS|TN_DSHS|20260509103000||VXU^V04^VXU_V04|MSG20260509103000011|P|2.5.1|||ER|AL
PID|1||MRN11112345^^^UTMC^MR||Greer^Olivia^Faith^^Baby^||20260105|F||2106-3^White^CDCREC|5914 Western Ave^^Knoxville^TN^37920^US^H||^PRN^PH^^1^865^5553890|||S^Single^HL70002||||||N^Not Hispanic or Latino^CDCREC
PD1||||1750482936^Hammond^Stephanie^L^^^MD^^^^NPI
NK1|1|Greer^Melissa^Dawn^^Mrs.|MTH^Mother^HL70063|5914 Western Ave^^Knoxville^TN^37920^US|^PRN^PH^^1^865^5553890||EC^Emergency Contact^HL70131
PV1|1|O|PED^0001^01^UTMC^^^^N|R^Routine^HL70007|||1750482936^Hammond^Stephanie^L^^^MD^^^^NPI||PED^Pediatrics^HL70069||||||||||VN20260509011^^^UTMC^VN
ORC|RE|ORD11001^EPIC||GRP11001^EPIC|CM^Complete^HL70038|||20260509102000|||1750482936^Hammond^Stephanie^L^^^MD^^^^NPI
RXA|0|1|20260509102000||20^DTaP^CVX|0.5|mL^milliliters^ISO+||00^New immunization record^NIP001||||||49281-0510-05^^NDC|||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible Medicaid/Medicaid Managed Care^HL70064||||||F
OBX|2|TS|29768-9^Date vaccine information statement published^LN||20230401||||||F
OBX|3|TS|29769-7^Date vaccine information statement presented^LN||20260509||||||F
ORC|RE|ORD11002^EPIC||GRP11002^EPIC|CM^Complete^HL70038|||20260509102500|||1750482936^Hammond^Stephanie^L^^^MD^^^^NPI
RXA|0|1|20260509102500||10^IPV^CVX|0.5|mL^milliliters^ISO+||00^New immunization record^NIP001||||||49281-0860-10^^NDC|||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|LT^Left Thigh^HL70163
OBX|4|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible Medicaid/Medicaid Managed Care^HL70064||||||F
OBX|5|TS|29768-9^Date vaccine information statement published^LN||20231019||||||F
OBX|6|TS|29769-7^Date vaccine information statement presented^LN||20260509||||||F
```

---

## 12. ADT^A04 - Emergency department registration at Vanderbilt

```
MSH|^~\&|EPICADT|VUMC^2.16.840.1.113883.3.1562^ISO|ADT_RECV|TN_HIE|20260510020000||ADT^A04^ADT_A01|MSG20260510020000012|P|2.5.1|||AL|NE
EVN|A04|20260510015500|||TRIAGE^Collins^Amy^R^^^RN|20260510015500
PID|1||MRN12123456^^^VUMC^MR||Blackwell^Jasmine^Renee^^Ms.^||19950819|F||2054-5^Black or African American^CDCREC|2805 12th Ave N^^Nashville^TN^37208^US^H||^PRN^PH^^1^615^5559012|||S^Single^HL70002|||347-62-9105|||N^Not Hispanic or Latino^CDCREC
NK1|1|Blackwell^Denise^Arlene^^Mrs.|MTH^Mother^HL70063|2805 12th Ave N^^Nashville^TN^37208^US|^PRN^PH^^1^615^5559013||EC^Emergency Contact^HL70131
PV1|1|E|ED^0001^T12^VUMC^^^^N|E^Emergency^HL70007|||1940573628^Kendrick^Marcus^A^^^MD^^^^NPI||EM^Emergency Medicine^HL70069||||||A^Accident^HL70007|||||VN20260510012^^^VUMC^VN|||||||||||||||||||||||||20260510015500
PV2|||^Severe headache and neck stiffness, rule out meningitis|||||||||||||||||||2^Emergent^HL70217
DG1|1||R51.9^Headache unspecified^I10||20260510|A
DG1|2||R29.1^Meningismus^I10||20260510|A
```

---

## 13. ADT^A28 - New patient registration at Saint Thomas West

```
MSH|^~\&|EPICADT|STWEST^2.16.840.1.113883.3.4151^ISO|MPI_RECV|TN_HIE|20260510140000||ADT^A28^ADT_A05|MSG20260510140000013|P|2.5.1|||AL|NE
EVN|A28|20260510135500
PID|1||MRN13134567^^^STWEST^MR~652-81-4037^^^USSSA^SS||Tran^Quang^Minh^^Mr.^||19760912|M||2028-9^Asian^CDCREC|4220 Harding Rd^^Nashville^TN^37205^US^H||^PRN^PH^^1^615^5554567|^WPN^PH^^1^615^5558890||M^Married^HL70002|||652-81-4037|||N^Not Hispanic or Latino^CDCREC
PD1|||Saint Thomas West Hospital^^^^NPI|1862049357^Mansfield^Catherine^E^^^MD^^^^NPI
NK1|1|Tran^Hanh^Ngoc^^Mrs.|SPO^Spouse^HL70063|4220 Harding Rd^^Nashville^TN^37205^US|^PRN^PH^^1^615^5554568||EC^Emergency Contact^HL70131
NK1|2|Tran^Bao^Duc^^Mr.|FTH^Father^HL70063|803 Murfreesboro Pike^^Nashville^TN^37217^US|^PRN^PH^^1^615^5553201||EC^Emergency Contact^HL70131
```

---

## 14. ADT^A02 - Patient transfer from NICU to pediatric floor at Vanderbilt Children's

```
MSH|^~\&|EPICADT|VCHILD^2.16.840.1.113883.3.1563^ISO|ADT_RECV|TN_HIE|20260511143000||ADT^A02^ADT_A02|MSG20260511143000014|P|2.5.1|||AL|NE
EVN|A02|20260511142500|||NICUNRS^Taylor^Michelle^D^^^RN|20260511142500
PID|1||MRN14145678^^^VCHILD^MR||Crawford^Elijah^Tyrone^^Baby^||20260424|M||2054-5^Black or African American^CDCREC|3601 Charlotte Ave^^Nashville^TN^37209^US^H||^PRN^PH^^1^615^5552847|||S^Single^HL70002||||||N^Not Hispanic or Latino^CDCREC
NK1|1|Crawford^Latoya^Monique^^Mrs.|MTH^Mother^HL70063|3601 Charlotte Ave^^Nashville^TN^37209^US|^PRN^PH^^1^615^5552847||EC^Emergency Contact^HL70131
PV1|1|I|PEDS^3205^01^VCHILD^^^^N|U^Urgent^HL70007|||1503826794^Ingram^Kathryn^A^^^MD^^^^NPI||PED^Pediatrics^HL70069||||||T^Transfer^HL70007|||||VN20260424014^^^VCHILD^VN
PV2|||^Premature infant, corrected gestational age 37 weeks, stable for step-down
```

---

## 15. ORU^R01 - Radiology report with embedded PDF (ED datatype) from TriStar Centennial

```
MSH|^~\&|EPICCARE|TRISTAR^2.16.840.1.113883.3.3301^ISO|RAD_RECV|TN_HIE|20260512091500||ORU^R01^ORU_R01|MSG20260512091500015|P|2.5.1|||AL|NE
PID|1||MRN15156789^^^TRISTAR^MR||Stafford^Kenneth^Russell^^Mr.^||19710613|M||2106-3^White^CDCREC|907 Gallatin Ave^^Nashville^TN^37206^US^H||^PRN^PH^^1^615^5554938|||M^Married^HL70002|||581-34-7290|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^CT01^01^TRISTAR^^^^N|R^Routine^HL70007|||1427693850^Reddy^Sanjay^V^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260512015^^^TRISTAR^VN
ORC|RE|ORD15001^EPIC|FIL15001^RAD||CM^Complete^HL70038|||20260511140000|||1427693850^Reddy^Sanjay^V^^^MD^^^^NPI
OBR|1|ORD15001^EPIC|FIL15001^RAD|74178^CT abdomen and pelvis with contrast^CPT4|||20260511140000|||||||||1427693850^Reddy^Sanjay^V^^^MD^^^^NPI||||||20260512090000|||F
OBX|1|TX|36643-5^CT abdomen impression^LN||IMPRESSION:\.br\1. 2.3 cm enhancing mass in the head of the pancreas with upstream pancreatic duct dilation to 6 mm.\.br\2. Three indeterminate hepatic lesions measuring up to 1.4 cm, too small to characterize.\.br\3. No retroperitoneal lymphadenopathy.\.br\4. Mild bilateral renal cortical cysts.\.br\Recommend: MRCP for further evaluation of pancreatic mass.||||||F|||20260512090000
OBX|2|ED|PDF^Radiology Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlCi9QYXJlbnQgMiAwIFIKL0NvbnRlbnRzIDQgMCBSCi9SZXNvdXJjZXMgPDwKL0ZvbnQgPDwKL0YxIDUgMCBSCj4+Cj4+Cj4+CmVuZG9iago0IDAgb2JqCjw8Ci9MZW5ndGggNzEKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihUcmlTdGFyIENlbnRlbm5pYWwgLSBDVCBBYmRvbWVuIFJlcG9ydCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago=||||||F|||20260512090000
```

---

## 16. ORM^O01 - Troponin lab order from Memorial emergency department in Memphis

```
MSH|^~\&|EPIC|METHMC^2.16.840.1.113883.3.8801^ISO|LAB_RECV|TN_HIE|20260513043000||ORM^O01^ORM_O01|MSG20260513043000016|P|2.5.1|||AL|NE
PID|1||MRN16167890^^^METHMC^MR||Mosby^Clarence^Jerome^^Mr.^||19580211|M||2054-5^Black or African American^CDCREC|1235 Union Ave^^Memphis^TN^38103^US^H||^PRN^PH^^1^901^5558471|||M^Married^HL70002|||482-61-3057|||N^Not Hispanic or Latino^CDCREC
PV1|1|E|ED^0001^T3^METHMC^^^^N|E^Emergency^HL70007|||1394827560^Foster^Brenda^N^^^MD^^^^NPI||EM^Emergency Medicine^HL70069||||||||||VN20260513016^^^METHMC^VN
ORC|NW|ORD16001^EPIC||GRP16001^EPIC|||||20260513042000|||1394827560^Foster^Brenda^N^^^MD^^^^NPI
OBR|1|ORD16001^EPIC||49563-0^Troponin I cardiac [Mass/volume] in Serum or Plasma^LN|||20260513042000||||||||1394827560^Foster^Brenda^N^^^MD^^^^NPI||||||||||1^Stat^HL70065
DG1|1||I21.9^Acute myocardial infarction unspecified^I10||20260513|A
DG1|2||R07.9^Chest pain unspecified^I10||20260513|A
NTE|1||Stat order. Patient presenting with acute substernal chest pain radiating to left arm. Onset 2 hours ago. ECG shows ST depression in leads II, III, aVF.
```

---

## 17. ADT^A31 - Update person information at Ballad Health

```
MSH|^~\&|EPICADT|BALLAD^2.16.840.1.113883.3.5501^ISO|MPI_RECV|TN_HIE|20260513100000||ADT^A31^ADT_A05|MSG20260513100000017|P|2.5.1|||AL|NE
EVN|A31|20260513095500
PID|1||MRN17178901^^^BALLAD^MR||Pickett^Donna^Renee^^Mrs.^||19680115|F||2106-3^White^CDCREC|2018 Roan St^^Johnson City^TN^37601^US^H||^PRN^PH^^1^423^5551204|^WPN^PH^^1^423^5557788||M^Married^HL70002|||819-46-2753|||N^Not Hispanic or Latino^CDCREC
PD1|||Ballad Health Johnson City Medical Center^^^^NPI|1260847935^Shelton^Timothy^R^^^MD^^^^NPI
```

---

## 18. ORU^R01 - Troponin results back from Memphis stat order

```
MSH|^~\&|EPICCARE|METHMC^2.16.840.1.113883.3.8801^ISO|LAB_RECV|TN_HIE|20260513053000||ORU^R01^ORU_R01|MSG20260513053000018|P|2.5.1|||AL|NE
PID|1||MRN16167890^^^METHMC^MR||Mosby^Clarence^Jerome^^Mr.^||19580211|M||2054-5^Black or African American^CDCREC|1235 Union Ave^^Memphis^TN^38103^US^H||^PRN^PH^^1^901^5558471|||M^Married^HL70002|||482-61-3057|||N^Not Hispanic or Latino^CDCREC
PV1|1|E|ED^0001^T3^METHMC^^^^N|E^Emergency^HL70007|||1394827560^Foster^Brenda^N^^^MD^^^^NPI||EM^Emergency Medicine^HL70069||||||||||VN20260513016^^^METHMC^VN
ORC|RE|ORD16001^EPIC|FIL16001^LAB||CM^Complete^HL70038|||20260513042000|||1394827560^Foster^Brenda^N^^^MD^^^^NPI
OBR|1|ORD16001^EPIC|FIL16001^LAB|49563-0^Troponin I cardiac [Mass/volume] in Serum or Plasma^LN|||20260513042000|||||||||1394827560^Foster^Brenda^N^^^MD^^^^NPI||||||20260513052000|||F
OBX|1|NM|49563-0^Troponin I cardiac [Mass/volume] in Serum or Plasma^LN||2.45|ng/mL^nanograms per milliliter^UCUM|0.00-0.04|HH|||F|||20260513052000
OBX|2|NM|33762-6^NT-proBNP [Mass/volume] in Serum or Plasma^LN||1842|pg/mL^picograms per milliliter^UCUM|0-125|HH|||F|||20260513052000
OBX|3|NM|30934-4^BUN/Creatinine [Mass Ratio] in Serum or Plasma^LN||16|{ratio}^ratio^UCUM|8-20|N|||F|||20260513052000
OBX|4|NM|6690-2^Leukocytes [#/volume] in Blood^LN||11.8|10*3/uL^thousand per microliter^UCUM|4.5-11.0|H|||F|||20260513052000
```

---

## 19. ADT^A08 - Insurance update for Erlanger patient

```
MSH|^~\&|EPICADT|ERLANG^2.16.840.1.113883.3.6601^ISO|ADT_RECV|TN_HIE|20260514093000||ADT^A08^ADT_A01|MSG20260514093000019|P|2.5.1|||AL|NE
EVN|A08|20260514092500|||REGCLK^Patterson^Joyce^A^^^ADM|20260514092500
PID|1||MRN19190123^^^ERLANG^MR||Salazar^Gabriela^Cristina^^Mrs.^||19870220|F||2106-3^White^CDCREC|1507 Cowart St^^Chattanooga^TN^37403^US^H||^PRN^PH^^1^423^5553456|^WPN^PH^^1^423^5557890||M^Married^HL70002|||724-38-5190|||H^Hispanic or Latino^CDCREC
PV1|1|I|OB^2501^01^ERLANG^^^^N|U^Urgent^HL70007|||1057394826^Delgado^Ana^L^^^MD^^^^NPI||OB^Obstetrics^HL70069||||||||||VN20260512019^^^ERLANG^VN|||||||||||||||||||||||||||20260512140000
IN1|1|BCBS001|54321^BlueCross BlueShield of Tennessee|BCBSTN^^Chattanooga^TN^37402|||||GRP112233||||||Salazar^Gabriela^Cristina|SE^Self^HL70063|19870220|1507 Cowart St^^Chattanooga^TN^37403^US|Y||1||||||||||||||POL778899
IN1|2|MAID001|79321^TennCare|TennCare^^Nashville^TN^37243|||||TCGRP667788||||||Salazar^Gabriela^Cristina|SE^Self^HL70063|19870220|1507 Cowart St^^Chattanooga^TN^37403^US|Y||2||||||||||||||TCPOL445566
```

---

## 20. ORU^R01 - Complete blood count with differential from Ballad Health

```
MSH|^~\&|EPICCARE|BALLAD^2.16.840.1.113883.3.5501^ISO|LAB_RECV|TN_HIE|20260515081200||ORU^R01^ORU_R01|MSG20260515081200020|P|2.5.1|||AL|NE
PID|1||MRN20201234^^^BALLAD^MR||Winfrey^Roger^Clifton^^Mr.^||19751030|M||2106-3^White^CDCREC|809 W Walnut St^^Johnson City^TN^37604^US^H||^PRN^PH^^1^423^5556148|||M^Married^HL70002|||603-72-4918|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|LAB^0002^01^BALLAD^^^^N|R^Routine^HL70007|||1482059637^Norris^David^R^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260515020^^^BALLAD^VN
ORC|RE|ORD20001^EPIC|FIL20001^LAB||CM^Complete^HL70038|||20260515064000|||1482059637^Norris^David^R^^^MD^^^^NPI
OBR|1|ORD20001^EPIC|FIL20001^LAB|58410-2^CBC with differential^LN|||20260515064000|||||||||1482059637^Norris^David^R^^^MD^^^^NPI||||||20260515080000|||F
OBX|1|NM|6690-2^Leukocytes [#/volume] in Blood^LN||6.8|10*3/uL^thousand per microliter^UCUM|4.5-11.0|N|||F|||20260515080000
OBX|2|NM|789-8^Erythrocytes [#/volume] in Blood^LN||4.92|10*6/uL^million per microliter^UCUM|4.50-5.90|N|||F|||20260515080000
OBX|3|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||14.6|g/dL^grams per deciliter^UCUM|13.5-17.5|N|||F|||20260515080000
OBX|4|NM|4544-3^Hematocrit [Volume Fraction] of Blood^LN||43.1|%^percent^UCUM|38.3-48.6|N|||F|||20260515080000
OBX|5|NM|787-2^MCV [Entitic volume]^LN||87.6|fL^femtoliter^UCUM|80.0-100.0|N|||F|||20260515080000
OBX|6|NM|785-6^MCH [Entitic mass]^LN||29.7|pg^picogram^UCUM|27.0-33.0|N|||F|||20260515080000
OBX|7|NM|786-4^MCHC [Mass/volume]^LN||33.9|g/dL^grams per deciliter^UCUM|32.0-36.0|N|||F|||20260515080000
OBX|8|NM|21000-5^Erythrocyte distribution width [Entitic volume]^LN||13.2|%^percent^UCUM|11.5-14.5|N|||F|||20260515080000
OBX|9|NM|777-3^Platelets [#/volume] in Blood^LN||218|10*3/uL^thousand per microliter^UCUM|150-400|N|||F|||20260515080000
OBX|10|NM|770-8^Neutrophils/100 leukocytes in Blood^LN||55.2|%^percent^UCUM|40.0-70.0|N|||F|||20260515080000
OBX|11|NM|736-9^Lymphocytes/100 leukocytes in Blood^LN||32.4|%^percent^UCUM|20.0-40.0|N|||F|||20260515080000
OBX|12|NM|5905-5^Monocytes/100 leukocytes in Blood^LN||8.1|%^percent^UCUM|2.0-8.0|H|||F|||20260515080000
OBX|13|NM|713-8^Eosinophils/100 leukocytes in Blood^LN||3.2|%^percent^UCUM|1.0-4.0|N|||F|||20260515080000
OBX|14|NM|706-2^Basophils/100 leukocytes in Blood^LN||1.1|%^percent^UCUM|0.0-2.0|N|||F|||20260515080000
```
