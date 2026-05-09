# Rhapsody Integration Engine - real HL7v2 ER7 messages

## 1. ADT^A01 - Inpatient admission at Essentia Health St. Mary's Medical Center, Duluth

```
MSH|^~\&|ADMISSIONS|ESSENTIA_SMMC|RHAPSODY|ESSENTIA_HIE|20250312083000||ADT^A01|RHAP-ADT-20250312-000123|P|2.3|||AL|NE
EVN|A01|20250312083000
PID|1||ESS-MRN-12034567^^^ESSENTIA^MR~555-12-3456^^^SSA^SS||Thorsgaard^Robert^James^^||19580422|M||W|1524 E 3rd St^^Duluth^MN^55812^USA||^PRN^PH^^1^218^5553412||ENG|M|||||||N
NK1|1|Thorsgaard^Carol^Marie|SPO^Spouse|1524 E 3rd St^^Duluth^MN^55812^USA|^PRN^PH^^1^218^5553413
NK1|2|Thorsgaard^Michael^R|SON^Son|4523 London Rd^^Duluth^MN^55804^USA|^PRN^PH^^1^218^5559012
PV1|1|I|MED^4N^12^SMMC||||1234567890^Harstad^Karl^L^^^MD|1234567890^Harstad^Karl^L^^^MD|1122334455^Pfeiffer^Sarah^M^^^MD||MED|||1|||||1234567890^Harstad^Karl^L^^^MD|I||||||||||||||||||20250312083000||||||||20250312083000
PV2|||R06.00^Dyspnea, unspecified^ICD10~J18.9^Pneumonia, unspecified organism^ICD10
DG1|1|ICD10|J18.9^Pneumonia, unspecified organism^ICD10||20250312|A
DG1|2|ICD10|R06.00^Dyspnea, unspecified^ICD10||20250312|A
IN1|1|BCBS-MN^^^BCBSMN|BCBS-MN|Blue Cross Blue Shield of Minnesota||||||MN-BCBS-GRP-33412|||20250101|20251231|||PPO|Thorsgaard^Robert^James|01|19580422|||||||||||||XYZ-567890123
```

---

## 2. ADT^A08 - Patient information update at CentraCare, St. Cloud

```
MSH|^~\&|REGISTRATION|CENTRACARE_SCH|RHAPSODY|CENTRACARE_HIE|20250415141200||ADT^A08|RHAP-ADT-20250415-001456|P|2.3|||AL|NE
EVN|A08|20250415141200
PID|1||CC-MRN-23045678^^^CENTRACARE^MR~444-56-7891^^^SSA^SS||Swanberg^Jennifer^Ann^^||19720315|F||W|3214 Clearwater Rd^^St. Cloud^MN^56301^USA||^PRN^PH^^1^320^5554567~^PRN^CP^^1^320^5559234||ENG|D|||||||N
PV1|1|O|CENTRACARE^CLINIC3^02||||2233445566^Ostlund^Sarah^M^^^MD|2233445566^Ostlund^Sarah^M^^^MD||FP|||1|||||2233445566^Ostlund^Sarah^M^^^MD|OP||||||||||||||||||||||||||20250415141200
```

---

## 3. ORM^O01 - Radiology order from Essentia Health to RIS via Rhapsody

```
MSH|^~\&|EHR|ESSENTIA_SMMC|RIS|ESSENTIA_RAD|20250520091500||ORM^O01|RHAP-ORM-20250520-002345|P|2.3|||AL|NE
PID|1||ESS-MRN-34056789^^^ESSENTIA^MR||Warsame^Daud^Ismail^^||19650730|M||W|823 Woodland Ave^^Duluth^MN^55803^USA||^PRN^PH^^1^218^5556012||ENG|M
PV1|1|I|MED^3S^08^SMMC||||3344556677^Braun^Anna^K^^^MD|3344556677^Braun^Anna^K^^^MD||MED|||1|||||3344556677^Braun^Anna^K^^^MD|I||||||||||||||||||20250519200000
ORC|NW|ESS-ORD-20250520-001^ESSENTIA|ESS-ORD-20250520-001^ESSENTIA||SC|||1^^^20250520091500^^S||20250520091500|3344556677^Braun^Anna^K^^^MD|3344556677^Braun^Anna^K^^^MD|3344556677^Braun^Anna^K^^^MD||^WPN^PH^^1^218^7868000
OBR|1|ESS-ORD-20250520-001^ESSENTIA|ESS-ORD-20250520-001^ESSENTIA|71046^XR CHEST 2 VIEWS^CPT4|STAT|20250520091500|||||Portable requested - patient on O2||||20250519200000|||||3344556677^Braun^Anna^K^^^MD||||||||||1^^^20250520091500^^S
```

---

## 4. ORU^R01 - Lab result routing from LIS through Rhapsody at CentraCare

```
MSH|^~\&|LIS|CENTRACARE_LAB|RHAPSODY|CENTRACARE_EHR|20250618143000||ORU^R01^ORU_R01|RHAP-ORU-20250618-003456|P|2.5.1|||AL|NE
PID|1||CC-MRN-45067890^^^CENTRACARE^MR||Yang^Kou^Mee^^||19800912|F||W|1812 9th Ave N^^St. Cloud^MN^56303^USA||^PRN^PH^^1^320^5553789||ENG|S
PV1|1|O|CENTRACARE^LAB^01||||4455667788^Schultz^Mark^T^^^MD|4455667788^Schultz^Mark^T^^^MD||IM|||1|||||4455667788^Schultz^Mark^T^^^MD|OP
ORC|RE|CC-ORD-20250617-012^CENTRACARE|CC-RES-20250618-3456^CENTRACARE_LAB|||||||4455667788^Schultz^Mark^T^^^MD|4455667788^Schultz^Mark^T^^^MD|||^WPN^PH^^1^320^2518000
OBR|1|CC-ORD-20250617-012^CENTRACARE|CC-RES-20250618-3456^CENTRACARE_LAB|24323-8^Comprehensive metabolic panel^LN|||20250617080000|||||||||||4455667788^Schultz^Mark^T^^^MD||CC-LAB-12345||||20250618140000|||F
OBX|1|NM|2345-7^Glucose^LN|1|98|mg/dL^milligrams per deciliter^UCUM|70-100||||F|||20250617080000|||||20250618140000||||CCLAB^CentraCare Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0673412|1406 6th Ave N^^St. Cloud^MN^56303
OBX|2|NM|3094-0^BUN^LN|2|18|mg/dL^milligrams per deciliter^UCUM|7-20||||F|||20250617080000|||||20250618140000||||CCLAB^CentraCare Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0673412|1406 6th Ave N^^St. Cloud^MN^56303
OBX|3|NM|2160-0^Creatinine^LN|3|0.9|mg/dL^milligrams per deciliter^UCUM|0.6-1.2||||F|||20250617080000|||||20250618140000||||CCLAB^CentraCare Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0673412|1406 6th Ave N^^St. Cloud^MN^56303
OBX|4|NM|2951-2^Sodium^LN|4|139|mmol/L^millimoles per liter^UCUM|136-145||||F|||20250617080000|||||20250618140000||||CCLAB^CentraCare Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0673412|1406 6th Ave N^^St. Cloud^MN^56303
OBX|5|NM|2823-3^Potassium^LN|5|4.1|mmol/L^millimoles per liter^UCUM|3.5-5.1||||F|||20250617080000|||||20250618140000||||CCLAB^CentraCare Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0673412|1406 6th Ave N^^St. Cloud^MN^56303
```

---

## 5. SIU^S12 - Scheduling message routed from Essentia Health through Rhapsody

```
MSH|^~\&|SCHEDULING|ESSENTIA_SCHED|RHAPSODY|ESSENTIA_EHR|20250724103000||SIU^S12^SIU_S12|RHAP-SIU-20250724-004567|P|2.5.1|||AL|NE
SCH|APT-ESS-20250724-4567|APT-ESS-20250724-4567|||||ROUTINE^Routine^HL70276|FOLLOWUP^Follow-up^HL70277|30|min||5566778899^Stavros^Patricia^E^^^MD|^WPN^PH^^1^218^7868000|502 E Second St^^Duluth^MN^55805|5566778899^Stavros^Patricia^E^^^MD|^WPN^PH^^1^218^7868000|502 E Second St^^Duluth^MN^55805||||||BOOKED
PID|1||ESS-MRN-56078901^^^ESSENTIA^MR||Farah^Amina^Sagal^^||19710605|F||W|4521 Jay St^^Duluth^MN^55804^USA||^PRN^PH^^1^218^5554321||ENG|M
PV1|1|O|ESSENTIA^CARDIO^02||||5566778899^Stavros^Patricia^E^^^MD|5566778899^Stavros^Patricia^E^^^MD||CARD|||1|||||5566778899^Stavros^Patricia^E^^^MD|OP
RGS|1||ESSENTIA^Essentia Health Cardiology
AIS|1||FOLLOWUP^Follow-up visit^ESS_APPT|20250807143000|30|min
AIG|1||5566778899^Stavros^Patricia^E^^^MD|P
AIL|1||ESSENTIA^CARDIO^02^Essentia Health Cardiology Duluth
```

---

## 6. ADT^A01 - Emergency admission at CentraCare St. Cloud Hospital

```
MSH|^~\&|ADMISSIONS|CENTRACARE_SCH|RHAPSODY|CENTRACARE_HIE|20250830021500||ADT^A01|RHAP-ADT-20250830-005678|P|2.3|||AL|NE
EVN|A01|20250830021500
PID|1||CC-MRN-67089012^^^CENTRACARE^MR~333-44-5568^^^SSA^SS||Bjornson^Gerald^Thomas^^||19470210|M||W|5812 County Rd 75^^St. Cloud^MN^56301^USA||^PRN^PH^^1^320^5556234||ENG|M|||||||N
NK1|1|Bjornson^Margaret^L|SPO^Spouse|5812 County Rd 75^^St. Cloud^MN^56301^USA|^PRN^PH^^1^320^5556235
PV1|1|E|ED^ER^03^SCH||||6677889900^Kiefer^Lisa^C^^^MD|6677889900^Kiefer^Lisa^C^^^MD||EM|||1|||||6677889900^Kiefer^Lisa^C^^^MD|E||||||||||||||||||20250830021500||||||||20250830021500
PV2|||I21.9^Acute myocardial infarction, unspecified^ICD10~I25.10^Atherosclerotic heart disease of native coronary artery without angina pectoris^ICD10
DG1|1|ICD10|I21.9^Acute myocardial infarction, unspecified^ICD10||20250830|A
IN1|1|MEDICARE^^^CMS|MEDICARE|Centers for Medicare and Medicaid Services||||||||||20240101||||MC|Bjornson^Gerald^Thomas|01|19470210|||||||||||||1EG4-RM2-JK89
```

---

## 7. ORU^R01 - Troponin result routed through Rhapsody at CentraCare

```
MSH|^~\&|LIS|CENTRACARE_LAB|RHAPSODY|CENTRACARE_EHR|20250830032000||ORU^R01^ORU_R01|RHAP-ORU-20250830-006789|P|2.5.1|||AL|NE
PID|1||CC-MRN-67089012^^^CENTRACARE^MR||Bjornson^Gerald^Thomas^^||19470210|M||W|5812 County Rd 75^^St. Cloud^MN^56301^USA||^PRN^PH^^1^320^5556234||ENG|M
PV1|1|E|ED^ER^03^SCH||||6677889900^Kiefer^Lisa^C^^^MD|6677889900^Kiefer^Lisa^C^^^MD||EM|||1|||||6677889900^Kiefer^Lisa^C^^^MD|E
ORC|RE|CC-ORD-20250830-001^CENTRACARE|CC-RES-20250830-6789^CENTRACARE_LAB|||||||6677889900^Kiefer^Lisa^C^^^MD|6677889900^Kiefer^Lisa^C^^^MD|||^WPN^PH^^1^320^2518000
OBR|1|CC-ORD-20250830-001^CENTRACARE|CC-RES-20250830-6789^CENTRACARE_LAB|49563-0^Troponin I cardiac [Mass/volume] in Serum or Plasma by High sensitivity method^LN|||20250830022000|||||||||||6677889900^Kiefer^Lisa^C^^^MD||CC-LAB-12345||||20250830031500|||F
OBX|1|NM|49563-0^Troponin I cardiac [Mass/volume] in Serum or Plasma by High sensitivity method^LN|1|2450|ng/L^nanograms per liter^UCUM|<34|H|||F|||20250830022000|||||20250830031500||||CCLAB^CentraCare Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0673412|1406 6th Ave N^^St. Cloud^MN^56303
```

---

## 8. ORM^O01 - Lab order from Essentia Health EHR to LIS via Rhapsody

```
MSH|^~\&|EHR|ESSENTIA_SMMC|LIS|ESSENTIA_LAB|20250903114500||ORM^O01|RHAP-ORM-20250903-007890|P|2.3|||AL|NE
PID|1||ESS-MRN-78090123^^^ESSENTIA^MR||Isse^Mohamed^Abdullahi^^||19630415|M||W|2317 E 5th St^^Duluth^MN^55812^USA||^PRN^PH^^1^218^5557890||ENG|M
PV1|1|I|SURG^5W^04^SMMC||||7788990011^Ellingson^Jennifer^A^^^MD|7788990011^Ellingson^Jennifer^A^^^MD||SURG|||1|||||7788990011^Ellingson^Jennifer^A^^^MD|I||||||||||||||||||20250902180000
ORC|NW|ESS-ORD-20250903-008^ESSENTIA|ESS-ORD-20250903-008^ESSENTIA||SC|||1^^^20250903114500^^R||20250903114500|7788990011^Ellingson^Jennifer^A^^^MD|7788990011^Ellingson^Jennifer^A^^^MD|7788990011^Ellingson^Jennifer^A^^^MD||^WPN^PH^^1^218^7868000
OBR|1|ESS-ORD-20250903-008^ESSENTIA|ESS-ORD-20250903-008^ESSENTIA|24323-8^Comprehensive metabolic panel^LN|ROUTINE|20250903114500|||||Pre-op labs for scheduled knee replacement||||20250902180000|^Serum||7788990011^Ellingson^Jennifer^A^^^MD||||||||||1^^^20250903114500^^R
OBR|2|ESS-ORD-20250903-008^ESSENTIA|ESS-ORD-20250903-008^ESSENTIA|58410-2^CBC with Auto Differential panel^LN|ROUTINE|20250903114500||||||||||^Blood||7788990011^Ellingson^Jennifer^A^^^MD||||||||||1^^^20250903114500^^R
OBR|3|ESS-ORD-20250903-008^ESSENTIA|ESS-ORD-20250903-008^ESSENTIA|34714-6^INR in Platelet poor plasma by Coagulation assay^LN|ROUTINE|20250903114500||||||||||^Plasma||7788990011^Ellingson^Jennifer^A^^^MD||||||||||1^^^20250903114500^^R
```

---

## 9. MDM^T02 - Document notification for discharge summary routed through Rhapsody

```
MSH|^~\&|DICTATION|ESSENTIA_SMMC|RHAPSODY|ESSENTIA_HIE|20250318142000||MDM^T02|RHAP-MDM-20250318-008901|P|2.4|||AL|NE
EVN|T02|20250318142000
PID|1||ESS-MRN-12034567^^^ESSENTIA^MR||Thorsgaard^Robert^James^^||19580422|M||W|1524 E 3rd St^^Duluth^MN^55812^USA||^PRN^PH^^1^218^5553412||ENG|M
PV1|1|I|MED^4N^12^SMMC||||1234567890^Harstad^Karl^L^^^MD|1234567890^Harstad^Karl^L^^^MD||MED|||1|||||1234567890^Harstad^Karl^L^^^MD|I||||||||||||||||||20250312083000||||||||20250318100000
TXA|1|DS^Discharge Summary|TX|20250318142000|1234567890^Harstad^Karl^L^^^MD||20250318142000||1234567890^Harstad^Karl^L^^^MD||||RHAP-RPT-ESS-20250318-008901|ESSENTIA_SMMC||||AU||AV
OBX|1|TX|18842-5^Discharge Summary^LN|1|DISCHARGE SUMMARY~~PATIENT: Thorsgaard, Robert James~MRN: ESS-MRN-12034567~ADMISSION DATE: 2025-03-12~DISCHARGE DATE: 2025-03-18~~ADMITTING DIAGNOSIS: Community-acquired pneumonia, dyspnea.~~HOSPITAL COURSE: 66-year-old male admitted with productive cough, fever, and dyspnea. Chest X-ray showed right lower lobe consolidation. Started on IV ceftriaxone and azithromycin. Blood cultures negative. Sputum culture grew Streptococcus pneumoniae. Transitioned to oral amoxicillin-clavulanate on hospital day 4. Oxygen supplementation weaned by hospital day 5.~~DISCHARGE DIAGNOSES:~1. Community-acquired pneumonia, Streptococcus pneumoniae.~2. Type 2 diabetes mellitus, well controlled.~3. Hypertension, controlled.~~DISCHARGE MEDICATIONS:~1. Amoxicillin-clavulanate 875/125 mg PO BID x 5 days~2. Metformin 1000 mg PO BID~3. Lisinopril 20 mg PO daily~4. Metoprolol succinate 50 mg PO daily~~FOLLOW-UP: PCP in 1 week. Repeat chest X-ray in 6 weeks.||||||F
```

---

## 10. ADT^A08 - Bed transfer notification at Essentia Health via Rhapsody

```
MSH|^~\&|BEDMGMT|ESSENTIA_SMMC|RHAPSODY|ESSENTIA_HIE|20250520183000||ADT^A08|RHAP-ADT-20250520-009012|P|2.3|||AL|NE
EVN|A08|20250520183000
PID|1||ESS-MRN-89101234^^^ESSENTIA^MR||Lor^Choua^Mai^^||19530828|F||W|7234 Arrowhead Rd^^Duluth^MN^55811^USA||^PRN^PH^^1^218^5558123||ENG|W|||||||N
PV1|1|I|ICU^ICU1^02^SMMC||||8899001122^Osman^Khalid^E^^^MD|8899001122^Osman^Khalid^E^^^MD||MED|||1|||||8899001122^Osman^Khalid^E^^^MD|I||||||||||||||||||20250518140000||||||||20250518140000
PV2|||N18.6^End stage renal disease^ICD10~E11.22^Type 2 diabetes mellitus with diabetic chronic kidney disease^ICD10
```

---

## 11. ORU^R01 - Blood culture result with embedded PDF from Essentia Health Lab

```
MSH|^~\&|LIS|ESSENTIA_LAB|RHAPSODY|ESSENTIA_EHR|20250401092000||ORU^R01^ORU_R01|RHAP-ORU-20250401-010123|P|2.5.1|||AL|NE
PID|1||ESS-MRN-90112345^^^ESSENTIA^MR||Samatar^Hawa^Asha^^||19440315|F||W|3412 Mesabi Ave^^Hibbing^MN^55746^USA||^PRN^PH^^1^218^5553456||ENG|W
PV1|1|I|MED^3N^07^SMMC||||1234567890^Harstad^Karl^L^^^MD|1234567890^Harstad^Karl^L^^^MD||MED|||1|||||1234567890^Harstad^Karl^L^^^MD|I||||||||||||||||||20250329210000
ORC|RE|ESS-ORD-20250330-003^ESSENTIA|ESS-RES-20250401-0123^ESSENTIA_LAB|||||||1234567890^Harstad^Karl^L^^^MD|1234567890^Harstad^Karl^L^^^MD|||^WPN^PH^^1^218^7868000
OBR|1|ESS-ORD-20250330-003^ESSENTIA|ESS-RES-20250401-0123^ESSENTIA_LAB|600-7^Bacteria identified in Blood by Culture^LN|||20250329213000|||||||||||1234567890^Harstad^Karl^L^^^MD||ESS-LAB-56789||||20250401090000|||F
OBX|1|ED|600-7^Blood Culture Report^LN|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKEJsb29kIEN1bHR1cmUgUmVwb3J0KQovQXV0aG9yIChFc3NlbnRpYSBIZWFsdGggTGFib3JhdG9yeSkKL0NyZWF0b3IgKEVzc2VudGlhIExJUyBSZXBvcnQgR2VuZXJhdG9yKQovUHJvZHVjZXIgKEVzc2VudGlhIEhlYWx0aCkKL0NyZWF0aW9uRGF0ZSAoRDoyMDI1MDQwMTA5MjAwMC0wNTAwKQo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMyAwIFIKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFs0IDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAzIDAgUgovQ29udGVudHMgNSAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNiAwIFIKPj4KPj4KPj4KZW5kb2JqCjUgMCBvYmoKPDwKL0xlbmd0aCAzMDAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgozNiA3NTYgVGQKKEJsb29kIEN1bHR1cmUgUmVwb3J0IC0gRXNzZW50aWEgSGVhbHRoIExhYm9yYXRvcnkpIFRqCgozNiA3MzAgVGQKKE9yZ2FuaXNtOiBFc2NoZXJpY2hpYSBjb2xpLiBTZW5zaXRpdml0aWVzIGluY2x1ZGVkLikgVGoKCjM2IDcxMCBUZAooQW1waWNpbGxpbjogUiwgQ2VmdmlheG9uZTogUywgR2VudGFtaWNpbjogUywgQ2lwcm9mbG94YWNpbjogUykgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago2IDAgb2JqCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDcKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAyNDUgMDAwMDAgbiAKMDAwMDAwMDI5NCAwMDAwMCBuIAowMDAwMDAwMzk3IDAwMDAwIG4gCjAwMDAwMDA1NDcgMDAwMDAgbiAKMDAwMDAwMDg5NyAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDcKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjk4NwolJUVPRgo=||||||F
OBX|2|CWE|600-7^Bacteria identified in Blood by Culture^LN|2|112283007^Escherichia coli^SCT||||||F|||20250329213000|||||20250401090000||||ESSLAB^Essentia Health Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0562341|502 E Second St^^Duluth^MN^55805
OBX|3|CWE|18864-9^Ampicillin [Susceptibility]^LN|3|R^Resistant^HL70078||S||||F|||20250329213000|||||20250401090000||||ESSLAB^Essentia Health Laboratory
OBX|4|CWE|18886-2^Ceftriaxone [Susceptibility]^LN|4|S^Susceptible^HL70078||S||||F|||20250329213000|||||20250401090000||||ESSLAB^Essentia Health Laboratory
OBX|5|CWE|18928-2^Gentamicin [Susceptibility]^LN|5|S^Susceptible^HL70078||S||||F|||20250329213000|||||20250401090000||||ESSLAB^Essentia Health Laboratory
```

---

## 12. ADT^A01 - Obstetric admission at Essentia Health, Duluth

```
MSH|^~\&|ADMISSIONS|ESSENTIA_SMMC|RHAPSODY|ESSENTIA_HIE|20250615043000||ADT^A01|RHAP-ADT-20250615-011234|P|2.3|||AL|NE
EVN|A01|20250615043000
PID|1||ESS-MRN-01123456^^^ESSENTIA^MR~222-33-4457^^^SSA^SS||Vue^Kazoua^Paj^^||19940820|F||W|1823 London Rd^^Duluth^MN^55812^USA||^PRN^PH^^1^218^5559234~^PRN^CP^^1^218^5551234||ENG|M|||||||N
NK1|1|Vue^Tou^J|SPO^Spouse|1823 London Rd^^Duluth^MN^55812^USA|^PRN^PH^^1^218^5559235
PV1|1|I|OB^LD^03^SMMC||||9900112233^Engel^Michelle^R^^^MD|9900112233^Engel^Michelle^R^^^MD||OB|||1|||||9900112233^Engel^Michelle^R^^^MD|I||||||||||||||||||20250615043000||||||||20250615043000
PV2|||O80^Encounter for full-term uncomplicated delivery^ICD10~Z3A.39^39 weeks gestation of pregnancy^ICD10
DG1|1|ICD10|O80^Encounter for full-term uncomplicated delivery^ICD10||20250615|A
```

---

## 13. ORM^O01 - Pharmacy order from CentraCare EHR to pharmacy system via Rhapsody

```
MSH|^~\&|EHR|CENTRACARE_SCH|PHARMACY|CENTRACARE_PHARM|20250830025000||ORM^O01|RHAP-ORM-20250830-012345|P|2.3|||AL|NE
PID|1||CC-MRN-67089012^^^CENTRACARE^MR||Bjornson^Gerald^Thomas^^||19470210|M||W|5812 County Rd 75^^St. Cloud^MN^56301^USA||^PRN^PH^^1^320^5556234||ENG|M
PV1|1|E|ED^ER^03^SCH||||6677889900^Kiefer^Lisa^C^^^MD|6677889900^Kiefer^Lisa^C^^^MD||EM|||1|||||6677889900^Kiefer^Lisa^C^^^MD|E
ORC|NW|CC-ORD-20250830-002^CENTRACARE|CC-ORD-20250830-002^CENTRACARE||SC|||1^^^20250830025000^^S||20250830025000|6677889900^Kiefer^Lisa^C^^^MD|6677889900^Kiefer^Lisa^C^^^MD|6677889900^Kiefer^Lisa^C^^^MD||^WPN^PH^^1^320^2518000
OBR|1|CC-ORD-20250830-002^CENTRACARE|CC-ORD-20250830-002^CENTRACARE|PHARM^Pharmacy Order|||20250830025000
RXO|Heparin^Heparin sodium^NDC|5000|U^Units|IV^Intravenous||G||||0|BOLUS^Bolus injection
```

---

## 14. ORU^R01 - Pathology result routed through Rhapsody at CentraCare

```
MSH|^~\&|LIS|CENTRACARE_PATH|RHAPSODY|CENTRACARE_EHR|20251005151500||ORU^R01^ORU_R01|RHAP-ORU-20251005-013456|P|2.5.1|||AL|NE
PID|1||CC-MRN-78101234^^^CENTRACARE^MR||Thao^Neng^Blong^^||19680422|F||W|1524 Oak Grove Rd^^St. Cloud^MN^56301^USA||^PRN^PH^^1^320^5557890||ENG|M
PV1|1|I|SURG^3E^10^SCH||||2233445566^Ostlund^Sarah^M^^^MD|2233445566^Ostlund^Sarah^M^^^MD||SURG|||1|||||2233445566^Ostlund^Sarah^M^^^MD|I
ORC|RE|CC-ORD-20251003-015^CENTRACARE|CC-RES-20251005-3456^CENTRACARE_PATH|||||||2233445566^Ostlund^Sarah^M^^^MD|2233445566^Ostlund^Sarah^M^^^MD|||^WPN^PH^^1^320^2518000
OBR|1|CC-ORD-20251003-015^CENTRACARE|CC-RES-20251005-3456^CENTRACARE_PATH|88305^Level IV Surgical Pathology^CPT4|||20251003140000|||||||||||2233445566^Ostlund^Sarah^M^^^MD||CC-PATH-34567||||20251005150000|||F
OBX|1|TX|22637-3^Pathology report final diagnosis^LN|1|SURGICAL PATHOLOGY REPORT~~SPECIMEN: Gallbladder, cholecystectomy.~~CLINICAL HISTORY: Chronic cholecystitis with cholelithiasis. Elective laparoscopic cholecystectomy.~~GROSS DESCRIPTION: Gallbladder measuring 9.5 x 3.5 x 2.8 cm. Serosal surface smooth and glistening. Wall thickness 3mm. Mucosa is green and velvety. Multiple faceted yellow-brown gallstones present, largest measuring 12mm.~~MICROSCOPIC DESCRIPTION: Sections show chronic cholecystitis with Rokitansky-Aschoff sinuses. Mild mural fibrosis. No dysplasia or malignancy identified.~~DIAGNOSIS: Gallbladder, cholecystectomy - Chronic cholecystitis with cholelithiasis. No malignancy.||||||F
```

---

## 15. SIU^S12 - Radiology scheduling routed through Rhapsody at CentraCare

```
MSH|^~\&|SCHEDULING|CENTRACARE_SCHED|RHAPSODY|CENTRACARE_RIS|20250908100000||SIU^S12^SIU_S12|RHAP-SIU-20250908-014567|P|2.5.1|||AL|NE
SCH|APT-CC-20250908-4567|APT-CC-20250908-4567|||||ROUTINE^Routine^HL70276|IMAGING^Imaging study^HL70277|60|min||4455667788^Schultz^Mark^T^^^MD|^WPN^PH^^1^320^2518000|1406 6th Ave N^^St. Cloud^MN^56303|4455667788^Schultz^Mark^T^^^MD|^WPN^PH^^1^320^2518000|1406 6th Ave N^^St. Cloud^MN^56303||||||BOOKED
PID|1||CC-MRN-89112345^^^CENTRACARE^MR||Jama^Fartun^Sahra^^||19550730|F||W|2812 Stearns County Rd 136^^Sauk Centre^MN^56378^USA||^PRN^PH^^1^320^5551234||ENG|W
PV1|1|O|CENTRACARE^RAD^01||||4455667788^Schultz^Mark^T^^^MD|4455667788^Schultz^Mark^T^^^MD||RAD|||1|||||4455667788^Schultz^Mark^T^^^MD|OP
RGS|1||CENTRACARE^CentraCare Radiology
AIS|1||CT_ABD^CT Abdomen Pelvis^CC_APPT|20250915083000|60|min
AIG|1||4455667788^Schultz^Mark^T^^^MD|P
AIL|1||CENTRACARE^CT^01^CentraCare Imaging St. Cloud
```

---

## 16. ADT^A08 - Allergy update routed through Rhapsody at Essentia Health

```
MSH|^~\&|EHR|ESSENTIA_SMMC|RHAPSODY|ESSENTIA_HIE|20250710094500||ADT^A08|RHAP-ADT-20250710-015678|P|2.3|||AL|NE
EVN|A08|20250710094500
PID|1||ESS-MRN-01234567^^^ESSENTIA^MR||Lindquist^William^James^^||19690318|M||W|4812 Grand Ave^^Duluth^MN^55807^USA||^PRN^PH^^1^218^5553890||ENG|M|||||||N
PV1|1|O|ESSENTIA^PCP^01||||1234567890^Harstad^Karl^L^^^MD|1234567890^Harstad^Karl^L^^^MD||FP|||1|||||1234567890^Harstad^Karl^L^^^MD|OP||||||||||||||||||||||||||20250710094500
AL1|1|DA|70618^Penicillin^RXNORM|MO^Moderate^HL70128|Rash, hives
AL1|2|DA|2670^Codeine^RXNORM|SV^Severe^HL70128|Anaphylaxis
AL1|3|DA|161^Aspirin^RXNORM|MI^Mild^HL70128|GI upset
```

---

## 17. ORU^R01 - Radiology result routed from RIS through Rhapsody at Essentia

```
MSH|^~\&|RIS|ESSENTIA_RAD|RHAPSODY|ESSENTIA_EHR|20250520143000||ORU^R01^ORU_R01|RHAP-ORU-20250520-016789|P|2.5.1|||AL|NE
PID|1||ESS-MRN-34056789^^^ESSENTIA^MR||Warsame^Daud^Ismail^^||19650730|M||W|823 Woodland Ave^^Duluth^MN^55803^USA||^PRN^PH^^1^218^5556012||ENG|M
PV1|1|I|MED^3S^08^SMMC||||3344556677^Braun^Anna^K^^^MD|3344556677^Braun^Anna^K^^^MD||MED|||1|||||3344556677^Braun^Anna^K^^^MD|I
ORC|RE|ESS-ORD-20250520-001^ESSENTIA|ESS-RES-20250520-6789^ESSENTIA_RAD|||||||3344556677^Braun^Anna^K^^^MD|3344556677^Braun^Anna^K^^^MD|||^WPN^PH^^1^218^7868000
OBR|1|ESS-ORD-20250520-001^ESSENTIA|ESS-RES-20250520-6789^ESSENTIA_RAD|71046^XR CHEST 2 VIEWS^CPT4|||20250520100000|||||||||||3344556677^Braun^Anna^K^^^MD||RAD-ACC-ESS-20250520-0001||||20250520143000|||F|||||||5566778899^Stavros^Patricia^E^^^MD^Radiology
OBX|1|TX|71046^XR CHEST 2 VIEWS^CPT4|1|PORTABLE CHEST X-RAY AP~~INDICATION: Pneumonia follow-up. Patient on supplemental oxygen.~~COMPARISON: Portable chest X-ray dated 2025-05-19.~~FINDINGS: Persistent right lower lobe consolidation, slightly improved compared to prior. Small right pleural effusion, stable. Heart size is normal. Left lung is clear. No pneumothorax.~~IMPRESSION: Improving right lower lobe pneumonia. Stable small right pleural effusion.||||||F
```

---

## 18. MDM^T02 - Operative note routed through Rhapsody at CentraCare

```
MSH|^~\&|DICTATION|CENTRACARE_SCH|RHAPSODY|CENTRACARE_HIE|20251005170000||MDM^T02|RHAP-MDM-20251005-017890|P|2.4|||AL|NE
EVN|T02|20251005170000
PID|1||CC-MRN-78101234^^^CENTRACARE^MR||Thao^Neng^Blong^^||19680422|F||W|1524 Oak Grove Rd^^St. Cloud^MN^56301^USA||^PRN^PH^^1^320^5557890||ENG|M
PV1|1|I|SURG^3E^10^SCH||||2233445566^Ostlund^Sarah^M^^^MD|2233445566^Ostlund^Sarah^M^^^MD||SURG|||1|||||2233445566^Ostlund^Sarah^M^^^MD|I
TXA|1|OP^Operative Note|TX|20251005170000|2233445566^Ostlund^Sarah^M^^^MD||20251005170000||2233445566^Ostlund^Sarah^M^^^MD||||RHAP-RPT-CC-20251005-017890|CENTRACARE_SCH||||AU||AV
OBX|1|TX|28570-0^Procedure note^LN|1|OPERATIVE NOTE~~SURGEON: Dr. Sarah M. Ostlund, MD~ASSISTANT: Dr. Anna K. Braun, MD~DATE OF PROCEDURE: 2025-10-03~~PREOPERATIVE DIAGNOSIS: Chronic cholecystitis with cholelithiasis.~POSTOPERATIVE DIAGNOSIS: Same.~~PROCEDURE: Laparoscopic cholecystectomy.~~ANESTHESIA: General endotracheal.~~FINDINGS: Chronically thickened gallbladder with multiple gallstones. No acute inflammation. Common bile duct normal caliber.~~DESCRIPTION: The patient was placed in supine position under general anesthesia. Standard 4-port laparoscopic approach was used. The critical view of safety was achieved. The cystic duct and cystic artery were identified, clipped, and divided. The gallbladder was dissected from the liver bed using electrocautery. The gallbladder was extracted through the umbilical port in a retrieval bag. Hemostasis was confirmed. All instruments were removed and ports closed.~~ESTIMATED BLOOD LOSS: Minimal, less than 25 mL.~SPECIMENS: Gallbladder to pathology.~COMPLICATIONS: None.~DISPOSITION: Patient to PACU in stable condition.||||||F
```

---

## 19. ADT^A01 - Transfer admission at Essentia Health from rural clinic

```
MSH|^~\&|ADMISSIONS|ESSENTIA_SMMC|RHAPSODY|ESSENTIA_HIE|20251120142000||ADT^A01|RHAP-ADT-20251120-018901|P|2.3|||AL|NE
EVN|A01|20251120142000
PID|1||ESS-MRN-12345678^^^ESSENTIA^MR~111-22-3346^^^SSA^SS||Musse^Abdikadir^Hassan^^||19600125|M||W|13524 Highway 53^^Virginia^MN^55792^USA||^PRN^PH^^1^218^5557234||ENG|M|||||||N
NK1|1|Musse^Halimo^J|SPO^Spouse|13524 Highway 53^^Virginia^MN^55792^USA|^PRN^PH^^1^218^5557235
PV1|1|I|MED^5N^02^SMMC||||8899001122^Osman^Khalid^E^^^MD|8899001122^Osman^Khalid^E^^^MD||MED|||4|||||8899001122^Osman^Khalid^E^^^MD|I||||||||||||||||||20251120142000||||||||20251120142000
PV2|||K85.9^Acute pancreatitis, unspecified^ICD10~K86.1^Other chronic pancreatitis^ICD10
DG1|1|ICD10|K85.9^Acute pancreatitis, unspecified^ICD10||20251120|A
IN1|1|BCBS-MN^^^BCBSMN|BCBS-MN|Blue Cross Blue Shield of Minnesota||||||MN-BCBS-GRP-56234|||20250101|20251231|||PPO|Musse^Abdikadir^Hassan|01|19600125|||||||||||||XYZ-890123456
```

---

## 20. ORU^R01 - HbA1c with embedded PDF report routed through Rhapsody at Essentia

```
MSH|^~\&|LIS|ESSENTIA_LAB|RHAPSODY|ESSENTIA_EHR|20251112141500||ORU^R01^ORU_R01|RHAP-ORU-20251112-019078|P|2.5.1|||AL|NE
PID|1||ESS-MRN-45678901^^^ESSENTIA^MR||Ali^Yusuf^Hirsi^^||19550803|M||W|4521 London Rd^^Duluth^MN^55804^USA||^PRN^PH^^1^218^5553456||ENG|M
PV1|1|O|ESSENTIA^LAB^02||||5566778899^Stavros^Patricia^E^^^MD|5566778899^Stavros^Patricia^E^^^MD||IM|||1|||||5566778899^Stavros^Patricia^E^^^MD|OP
ORC|RE|ESS-ORD-20251111-012^ESSENTIA|ESS-RES-20251112-9078^ESSENTIA_LAB|||||||5566778899^Stavros^Patricia^E^^^MD|5566778899^Stavros^Patricia^E^^^MD|||^WPN^PH^^1^218^7868000
OBR|1|ESS-ORD-20251111-012^ESSENTIA|ESS-RES-20251112-9078^ESSENTIA_LAB|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN|||20251111074500|||||||||||5566778899^Stavros^Patricia^E^^^MD||ESS-LAB-78901||||20251112140000|||F
OBX|1|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN|1|8.2|%^percent^UCUM|<5.7|H|||F|||20251111074500|||||20251112140000||||ESSLAB^Essentia Health Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0562341|502 E Second St^^Duluth^MN^55805
OBX|2|ED|4548-4^HbA1c Lab Report PDF^LN|2|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKEhiQTFjIExhYm9yYXRvcnkgUmVwb3J0KQovQXV0aG9yIChFc3NlbnRpYSBIZWFsdGggTGFib3JhdG9yeSkKL0NyZWF0b3IgKFJoYXBzb2R5IFJlcG9ydCBHZW5lcmF0b3IpCi9Qcm9kdWNlciAoUmhhcHNvZHkgSW50ZWdyYXRpb24gRW5naW5lKQovQ3JlYXRpb25EYXRlIChEOjIwMjUxMTEyMTQxNTAwLTA2MDApCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9DYXRhbG9nCi9QYWdlcyAzIDAgUgo+PgplbmRvYmoKMyAwIG9iago8PAovVHlwZSAvUGFnZXMKL0tpZHMgWzQgMCBSXQovQ291bnQgMQovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQo+PgplbmRvYmoKNCAwIG9iago8PAovVHlwZSAvUGFnZQovUGFyZW50IDMgMCBSCi9Db250ZW50cyA1IDAgUgo+PgplbmRvYmoK||||||F|||20251111074500|||||20251112140000||||ESSLAB^Essentia Health Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0562341|502 E Second St^^Duluth^MN^55805
```
