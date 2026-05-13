# Orion Health Clinical Portal (Concerto) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to Auckland City Hospital

```
MSH|^~\&|CONCERTO|AUCKDHB|PAS|AUCKDHB|20250312091500||ADT^A01^ADT_A01|MSG00001|P|2.4|||AL|NE|NZL
EVN|A01|20250312091500|||JTOMASI^Tomasi^Janet^^^Dr
PID|1||XKR4128^^^NHINZ^NHI~AKL098765^^^AUCKDHB^MR||Whatuira^Aroha^Maraea^^Mrs||19780423|F|||62 Jervois Road^^Auckland^^1011^NZL^C||^PRN^PH^^64^9^3768421|^WPN^PH^^64^9^5552190||M|CE|||||||||N||NZL
PD1||||G12345^Patel^Rajiv^^^Dr^^^NZMC
NK1|1|Whatuira^James^Tane||38 Williamson Avenue^^Auckland^^1021^NZL^C|^PRN^PH^^64^21^0982746||SP
PV1|1|I|WARD4E^405^1^^^AUCKHOSP||||D78901^Henderson^Sarah^^^Dr^^^NZMC|||MED||||7|||D78901^Henderson^Sarah^^^Dr^^^NZMC|IP||GP|||||||||||||||||||AUCKDHB||A|||20250312091500
PV2|||^Chest pain - investigation required
IN1|1|SUBS01|ACC^Accident Compensation Corporation^ACC|||||||||||20250101|20251231
```

---

## 2. ADT^A04 - Patient registration at Christchurch Hospital outpatient clinic

```
MSH|^~\&|ORION_CP|CDHB|HOMER|CDHB|20250415103000||ADT^A04^ADT_A01|MSG00002|P|2.4|||AL|NE|NZL
EVN|A04|20250415103000|||REGISTRAR01
PID|1||PMD7392^^^NHINZ^NHI~CHC045678^^^CDHB^MR||Taylorson^Nikau^Hone||19650817|M|||52 Wharenui Road^^Christchurch^^8041^NZL^C||^PRN^PH^^64^3^3486391|^WPN^PH^^64^3^9871502||S|AK|||||||||N||NZL
PD1||||G54321^MacKinnon^Fiona^^^Dr^^^NZMC
PV1|1|O|OUTPAT^CARD^1^^^CHCHOSP||||D23456^Ngapuhi^Wiremu^^^Dr^^^NZMC|||CAR||||1|||D23456^Ngapuhi^Wiremu^^^Dr^^^NZMC|OP||GP|||||||||||||||||||CDHB||A|||20250415103000
PV2|||^Follow-up cardiology review
```

---

## 3. ADT^A08 - Patient information update at Waikato Hospital

```
MSH|^~\&|CONCERTO|WAIKATODHB|WEBPAS|WAIKATODHB|20250520141200||ADT^A08^ADT_A01|MSG00003|P|2.4|||AL|NE|NZL
EVN|A08|20250520141200|||ADMIN02
PID|1||CJR7812^^^NHINZ^NHI~WKT034567^^^WAIKATODHB^MR||Cooper^Hineata^Te Rina^^Ms||19900115|F|||83 Boundary Road^^Hamilton^^3204^NZL^C~PO Box 4271^^Hamilton^^3240^NZL^M||^PRN^PH^^64^7^8341968|^WPN^PH^^64^7^8567124||D|BU|||||||||N||NZL
PD1||||G67890^Singh^Anika^^^Dr^^^NZMC
PV1|1|I|WARD2B^210^1^^^WKTHOSP||||D11111^Brownlow^Matthew^^^Dr^^^NZMC|||GEN||||7|||D11111^Brownlow^Matthew^^^Dr^^^NZMC|IP||GP|||||||||||||||||||WAIKATODHB||A|||20250518090000
```

---

## 4. ADT^A03 - Patient discharge from Wellington Regional Hospital

```
MSH|^~\&|CLINICAL_PORTAL|CCDHB|CONCERTO|CCDHB|20250401160000||ADT^A03^ADT_A03|MSG00004|P|2.4|||AL|NE|NZL
EVN|A03|20250401160000|||D34567^Wallis^Karen^^^Dr^^^NZMC
PID|1||EPN4523^^^NHINZ^NHI~WGT012345^^^CCDHB^MR||Mihaere^Rawiri^Tamati||19550930|M|||74 The Terrace^^Wellington^^6011^NZL^C||^PRN^PH^^64^4^4628317||W|CE|||||||||N||NZL
PV1|1|I|WARD6A^602^1^^^WELHOSP||||D34567^Wallis^Karen^^^Dr^^^NZMC|||MED||||7|||D34567^Wallis^Karen^^^Dr^^^NZMC|IP||GP|||||||||||||||||||CCDHB||D|||20250328143000|||20250401160000
DG1|1|I10|I10^Essential hypertension^I10|||F
DG1|2|E11.9|E11.9^Type 2 diabetes mellitus without complications^I10|||F
```

---

## 5. ORU^R01 - Laboratory results from LabPLUS Auckland

```
MSH|^~\&|ORION_HEALTH|AUCKDHB|LABPLUS|AUCKDHB|20250610083000||ORU^R01^ORU_R01|MSG00005|P|2.4|||AL|NE|NZL
PID|1||FHT9012^^^NHINZ^NHI~AKL112233^^^AUCKDHB^MR||Hekenui^Maia^Whetu||19820614|F|||38 Stokes Road^^Auckland^^1024^NZL^C||^PRN^PH^^64^21^0238512||M|CE|||||||||N||NZL
PV1|1|O|ED^MAIN^1^^^AUCKHOSP||||D45678^Liu^Wei^^^Dr^^^NZMC|||EM||||1|||D45678^Liu^Wei^^^Dr^^^NZMC|OP
ORC|RE|ORD001^CONCERTO|LAB001^LABPLUS||CM||||20250610070000|||D45678^Liu^Wei^^^Dr^^^NZMC
OBR|1|ORD001^CONCERTO|LAB001^LABPLUS|FBC^Full Blood Count^NZLT||20250610070000|20250610070500||||L||||||D45678^Liu^Wei^^^Dr^^^NZMC|||||||20250610082500|||F
OBX|1|NM|WBC^White Blood Cell Count^NZLT||6.8|x10^9/L|4.0-11.0||||F|||20250610082500
OBX|2|NM|RBC^Red Blood Cell Count^NZLT||4.52|x10^12/L|3.80-5.80||||F|||20250610082500
OBX|3|NM|HGB^Haemoglobin^NZLT||132|g/L|115-165||||F|||20250610082500
OBX|4|NM|PLT^Platelet Count^NZLT||245|x10^9/L|150-400||||F|||20250610082500
OBX|5|NM|MCV^Mean Cell Volume^NZLT||88.5|fL|80-100||||F|||20250610082500
```

---

## 6. ORU^R01 - Radiology report from Canterbury DHB

```
MSH|^~\&|CONCERTO|CDHB|RIS|CDHB|20250305142000||ORU^R01^ORU_R01|MSG00006|P|2.4|||AL|NE|NZL
PID|1||GKL3456^^^NHINZ^NHI~CHC098765^^^CDHB^MR||Rosenthal^Emma^Louise||19710228|F|||94 Memorial Avenue^^Christchurch^^8053^NZL^C||^PRN^PH^^64^3^3582176||M|CE|||||||||N||NZL
PV1|1|O|RADIOL^XRAY^1^^^CHCHOSP||||D56789^Kumarasamy^Priya^^^Dr^^^NZMC|||RAD||||1|||D56789^Kumarasamy^Priya^^^Dr^^^NZMC|OP
ORC|RE|ORD002^ORION_CP|RAD002^RIS||CM||||20250305100000|||D56789^Kumarasamy^Priya^^^Dr^^^NZMC
OBR|1|ORD002^ORION_CP|RAD002^RIS|XCHEST^Chest X-Ray PA and Lateral^NZRAD||20250305100000|20250305103000||||L||||||D56789^Kumarasamy^Priya^^^Dr^^^NZMC|||||||20250305140000|||F
OBX|1|FT|XCHEST^Chest X-Ray Report^NZRAD||CHEST X-RAY PA AND LATERAL\.br\\.br\Clinical indication: Persistent cough, query pneumonia\.br\\.br\Findings:\.br\Heart size is normal. The mediastinal contours are unremarkable.\.br\The lungs are clear bilaterally with no focal consolidation, pleural effusion,\.br\or pneumothorax identified. The costophrenic angles are sharp.\.br\No bony abnormality seen.\.br\\.br\Impression: Normal chest radiograph. No evidence of pneumonia.\.br\\.br\Reported by: Dr Priya Kumarasamy, Radiologist, Canterbury||||||F|||20250305140000
```

---

## 7. ORU^R01 - Biochemistry results from Counties Manukau DHB

```
MSH|^~\&|ORION_HEALTH|CMDHB|DELPHIC|CMDHB|20250722110000||ORU^R01^ORU_R01|MSG00007|P|2.5|||AL|NE|NZL
PID|1||HRM8745^^^NHINZ^NHI~CMK056789^^^CMDHB^MR||Vaipulu^Sione^Tevita||19680511|M|||128 Mahia Road^^Manurewa^^2102^NZL^C||^PRN^PH^^64^9^2674198||M|PI|||||||||N||NZL
PV1|1|I|WARD3^301^1^^^MMHOSP||||D67890^O'Donnell^Padraig^^^Dr^^^NZMC|||MED||||7|||D67890^O'Donnell^Padraig^^^Dr^^^NZMC|IP
ORC|RE|ORD003^ORION_HEALTH|LAB003^DELPHIC||CM||||20250722060000|||D67890^O'Donnell^Padraig^^^Dr^^^NZMC
OBR|1|ORD003^ORION_HEALTH|LAB003^DELPHIC|BIOCHEM^Biochemistry Panel^NZLT||20250722060000|20250722060500||||L||||||D67890^O'Donnell^Padraig^^^Dr^^^NZMC|||||||20250722105000|||F
OBX|1|NM|NA^Sodium^NZLT||141|mmol/L|135-145||||F|||20250722105000
OBX|2|NM|K^Potassium^NZLT||4.2|mmol/L|3.5-5.0||||F|||20250722105000
OBX|3|NM|CREAT^Creatinine^NZLT||98|umol/L|60-110||||F|||20250722105000
OBX|4|NM|EGFR^eGFR^NZLT||72|mL/min/1.73m2|>90||||F|||20250722105000
OBX|5|NM|GLU^Glucose (fasting)^NZLT||8.3|mmol/L|3.0-6.0|H|||F|||20250722105000
OBX|6|NM|HBA1C^HbA1c^NZLT||62|mmol/mol|<41|H|||F|||20250722105000
```

---

## 8. ORM^O01 - Radiology order from Waitemata DHB

```
MSH|^~\&|CONCERTO|WDHB|RIS|WDHB|20250818093000||ORM^O01^ORM_O01|MSG00008|P|2.4|||AL|NE|NZL
PID|1||JNP6234^^^NHINZ^NHI~WTM034567^^^WDHB^MR||Sharma^Preethi^Anjali||19850327|F|||45 Anzac Street^^Takapuna^^0622^NZL^C||^PRN^PH^^64^21^0341827||S|HN|||||||||N||NZL
PV1|1|O|OUTPAT^ORTHO^1^^^NSHOSP||||D78123^Wilkins^Grant^^^Dr^^^NZMC|||ORT||||1|||D78123^Wilkins^Grant^^^Dr^^^NZMC|OP
ORC|NW|ORD004^CONCERTO||GRP004^CONCERTO|||||20250818093000|||D78123^Wilkins^Grant^^^Dr^^^NZMC||^WPN^PH^^64^9^4868000
OBR|1|ORD004^CONCERTO||XKNEE^X-Ray Knee AP and Lateral^NZRAD|||20250818|||||||20250818093000|||||||||||||ROUTINE
DG1|1||M17.1^Primary gonarthrosis, right knee^I10|||W
```

---

## 9. ORM^O01 - Laboratory order from Bay of Plenty DHB

```
MSH|^~\&|ORION_CP|BOPDHB|PATHLAB|BOPDHB|20250203080000||ORM^O01^ORM_O01|MSG00009|P|2.4|||AL|NE|NZL
PID|1||KQW1567^^^NHINZ^NHI~BOP078901^^^BOPDHB^MR||Walker^Tanerau^Hemi||19430722|M|||83 Fraser Street^^Tauranga^^3110^NZL^C||^PRN^PH^^64^7^5713829||W|AK|||||||||N||NZL
PV1|1|I|WARD5^503^1^^^TAUHOSP||||D89012^Chen^Daniel^^^Dr^^^NZMC|||MED||||7|||D89012^Chen^Daniel^^^Dr^^^NZMC|IP
ORC|NW|ORD005^ORION_CP||GRP005^ORION_CP|||||20250203080000|||D89012^Chen^Daniel^^^Dr^^^NZMC||^WPN^PH^^64^7^5790000
OBR|1|ORD005^ORION_CP||FBC^Full Blood Count^NZLT|||20250203|||||||20250203080000|Blood^Venous|||||||||||STAT
OBR|2|ORD005^ORION_CP||CRP^C-Reactive Protein^NZLT|||20250203|||||||20250203080000|Blood^Venous|||||||||||STAT
OBR|3|ORD005^ORION_CP||BCULT^Blood Culture^NZLT|||20250203|||||||20250203080000|Blood^Venous|||||||||||STAT
```

---

## 10. MDM^T02 - Clinical document notification with PDF from Capital and Coast DHB

```
MSH|^~\&|CONCERTO|CCDHB|EDMS|CCDHB|20250910150000||MDM^T02^MDM_T02|MSG00010|P|2.5|||AL|NE|NZL
EVN|T02|20250910150000
PID|1||LVB8901^^^NHINZ^NHI~WGT098765^^^CCDHB^MR||Parata^Hinerangi^Mereana^^Mrs||19610809|F|||29 Tinakori Road^^Wellington^^6011^NZL^C||^PRN^PH^^64^4^3892641||M|CE|||||||||N||NZL
PV1|1|I|WARD8^812^1^^^WELHOSP||||D90123^Forster^Richard^^^Dr^^^NZMC|||GEN||||7|||D90123^Forster^Richard^^^Dr^^^NZMC|IP
TXA|1|DS^Discharge Summary|TX|20250910150000|D90123^Forster^Richard^^^Dr^^^NZMC|20250910150000||||||DOC001^CONCERTO||||AU||AV
OBX|1|ED|PDF^Discharge Summary^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo=||||||F
```

---

## 11. MDM^T02 - Outpatient clinic letter from Southern DHB

```
MSH|^~\&|CLINICAL_PORTAL|SDHB|EDMS|SDHB|20250128113000||MDM^T02^MDM_T02|MSG00011|P|2.5|||AL|NE|NZL
EVN|T02|20250128113000
PID|1||MWC4567^^^NHINZ^NHI~DUN045678^^^SDHB^MR||Andersson^Craig^Reuben||19770315|M|||63 Highgate^^Dunedin^^9010^NZL^C||^PRN^PH^^64^3^4742891||M|AK|||||||||N||NZL
PV1|1|O|OUTPAT^RESP^1^^^DUNHOSP||||D12345^Te Kanawa^Mereana^^^Dr^^^NZMC|||RES||||1|||D12345^Te Kanawa^Mereana^^^Dr^^^NZMC|OP
TXA|1|CL^Clinic Letter|TX|20250128113000|D12345^Te Kanawa^Mereana^^^Dr^^^NZMC|20250128113000||||||DOC002^CLINICAL_PORTAL||||AU||AV
OBX|1|FT|CL^Clinic Letter^LN||Dear Dr McPherson,\.br\\.br\Re: Craig Reuben Andersson, DOB 15/03/1977, NHI MWC4567\.br\\.br\Thank you for referring this gentleman who I reviewed in the Respiratory\.br\Outpatient Clinic at Dunedin Hospital on 28 January 2025.\.br\\.br\He presents with a 3-month history of progressive dyspnoea on exertion\.br\and a persistent dry cough. His spirometry today shows FEV1 2.8L (78% predicted)\.br\and FVC 3.9L (85% predicted) with FEV1/FVC ratio 72%.\.br\\.br\I have arranged a CT chest and will review him in 6 weeks with results.\.br\\.br\Yours sincerely,\.br\Dr Mereana Te Kanawa\.br\Respiratory Physician\.br\Southern||||||F
```

---

## 12. ORU^R01 - Microbiology results from MidCentral DHB

```
MSH|^~\&|ORION_HEALTH|MCDHB|MEDLAB|MCDHB|20250604163000||ORU^R01^ORU_R01|MSG00012|P|2.4|||AL|NE|NZL
PID|1||NXT2389^^^NHINZ^NHI~MCD012345^^^MCDHB^MR||Ramskill^Sophie^Anne||19950620|F|||74 Featherston Street^^Palmerston North^^4410^NZL^C||^PRN^PH^^64^6^3568217||S|CE|||||||||N||NZL
PV1|1|O|ED^MAIN^1^^^PNHOSP||||D23478^MacGregor^Angus^^^Dr^^^NZMC|||EM||||1|||D23478^MacGregor^Angus^^^Dr^^^NZMC|OP
ORC|RE|ORD006^ORION_HEALTH|LAB006^MEDLAB||CM||||20250604120000|||D23478^MacGregor^Angus^^^Dr^^^NZMC
OBR|1|ORD006^ORION_HEALTH|LAB006^MEDLAB|UCULT^Urine Culture^NZLT||20250604120000|20250604121000|||Nurse01|L|||||D23478^MacGregor^Angus^^^Dr^^^NZMC|||||||20250604160000|||F
OBX|1|FT|UCULT^Urine Culture Report^NZLT||Specimen: Mid-stream urine\.br\Microscopy: WBC >100 x10^6/L, RBC 5-10 x10^6/L\.br\Culture: Escherichia coli >10^8 CFU/L (pure growth)\.br\\.br\Antibiotic susceptibilities:\.br\Amoxicillin: Resistant\.br\Trimethoprim: Sensitive\.br\Nitrofurantoin: Sensitive\.br\Ciprofloxacin: Sensitive\.br\Cephalexin: Sensitive||||||F|||20250604160000
```

---

## 13. QBP^Q22 - Patient demographics query via NHI

```
MSH|^~\&|CONCERTO|AUCKDHB|NHI|NZMOH|20250415090000||QBP^Q22^QBP_Q21|MSG00013|P|2.5|||AL|NE|NZL
QPD|Q22^Get Person Demographics^HL7nz|QRY00013|PBR6712^^^NHINZ^NHI
RCP|I|1^RD
```

---

## 14. RSP^K22 - NHI query response with patient demographics

```
MSH|^~\&|NHI|NZMOH|CONCERTO|AUCKDHB|20250415090001||RSP^K22^RSP_K21|MSG00014|P|2.5|||AL|NE|NZL
MSA|AA|MSG00013
QAK|QRY00013|OK|Q22^Get Person Demographics^HL7nz|1
QPD|Q22^Get Person Demographics^HL7nz|QRY00013|PBR6712^^^NHINZ^NHI
PID|1||PBR6712^^^NHINZ^NHI||Kingi^Arapeta^Te Aniwa||19880214|M|||83 Mt Albert Road^^Mount Roskill^^1041^NZL^C||^PRN^PH^^64^9^6304182||S|ML|||||21^NZ Maori||||N||NZL
```

---

## 15. ADT^A28 - Patient record merge notification from Hawke's Bay DHB

```
MSH|^~\&|ORION_CP|HBDHB|PAS|HBDHB|20250703140000||ADT^A28^ADT_A05|MSG00015|P|2.4|||AL|NE|NZL
EVN|A28|20250703140000|||NHIADMIN
PID|1||QFS5678^^^NHINZ^NHI~HBY023456^^^HBDHB^MR||Reedham^Kataraina^Whetu^^Ms||19920408|F|||52 Karamu Road North^^Hastings^^4122^NZL^C||^PRN^PH^^64^6^8782915|^WPN^PH^^64^6^8789138||S|CE|||||||||N||NZL
PD1||||G78901^Evanson^Thomas^^^Dr^^^NZMC
PV1|1|N|||||||||||||||||NP
```

---

## 16. ORU^R01 - Histopathology report from Waikato DHB

```
MSH|^~\&|CONCERTO|WAIKATODHB|PATHLAB|WAIKATODHB|20250225170000||ORU^R01^ORU_R01|MSG00016|P|2.4|||AL|NE|NZL
PID|1||RHL3421^^^NHINZ^NHI~WKT098765^^^WAIKATODHB^MR||Douglas^Iain^Forsyth||19600101|M|||27 Peachgrove Road^^Hamilton^^3216^NZL^C||^PRN^PH^^64^7^8492174||M|CE|||||||||N||NZL
PV1|1|I|WARD7^710^1^^^WKTHOSP||||D34521^Patel^Meera^^^Dr^^^NZMC|||SUR||||7|||D34521^Patel^Meera^^^Dr^^^NZMC|IP
ORC|RE|ORD007^CONCERTO|LAB007^PATHLAB||CM||||20250220090000|||D34521^Patel^Meera^^^Dr^^^NZMC
OBR|1|ORD007^CONCERTO|LAB007^PATHLAB|HIST^Histopathology^NZLT||20250220090000|20250220093000||||L||||||D34521^Patel^Meera^^^Dr^^^NZMC|||||||20250225163000|||F
OBX|1|FT|HIST^Histopathology Report^NZLT||HISTOPATHOLOGY REPORT\.br\\.br\Specimen: Right hemicolectomy\.br\Clinical details: Ascending colon tumour\.br\\.br\Macroscopic: Right hemicolectomy specimen measuring 28cm in length.\.br\There is an ulcerated tumour in the ascending colon measuring 4.5 x 3.8 cm.\.br\The tumour appears to extend through the muscularis propria.\.br\22 lymph nodes identified.\.br\\.br\Microscopic: Moderately differentiated adenocarcinoma of the ascending colon.\.br\Tumour invades through the muscularis propria into pericolonic fat (pT3).\.br\Margins clear - proximal 12cm, distal 8cm, radial 1.5cm.\.br\2 of 22 lymph nodes contain metastatic carcinoma (pN1a).\.br\No lymphovascular invasion. No perineural invasion.\.br\\.br\Stage: pT3 N1a M0 (AJCC 8th edition)\.br\\.br\Reported by: Dr Sarah Wong, Anatomical Pathologist, Waikato||||||F|||20250225163000
```

---

## 17. MDM^T02 - Cardiology report with embedded PDF from Auckland DHB

```
MSH|^~\&|ORION_HEALTH|AUCKDHB|EDMS|AUCKDHB|20250507120000||MDM^T02^MDM_T02|MSG00017|P|2.5|||AL|NE|NZL
EVN|T02|20250507120000
PID|1||SKT7890^^^NHINZ^NHI~AKL345678^^^AUCKDHB^MR||Ngatapere^Roimata^Aniwaniwa^^Mrs||19730619|F|||62 Victoria Avenue^^Remuera^^1050^NZL^C||^PRN^PH^^64^21^0876318||M|CE|||||||||N||NZL
PV1|1|O|OUTPAT^CARD^1^^^AUCKHOSP||||D56712^Gupta^Amitabh^^^Dr^^^NZMC|||CAR||||1|||D56712^Gupta^Amitabh^^^Dr^^^NZMC|OP
TXA|1|ECHO^Echocardiogram Report|TX|20250507120000|D56712^Gupta^Amitabh^^^Dr^^^NZMC|20250507120000||||||DOC003^ORION_HEALTH||||AU||AV
OBX|1|ED|PDF^Echocardiogram Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo=||||||F
```

---

## 18. ORM^O01 - Pathology order from Nelson Marlborough DHB

```
MSH|^~\&|CLINICAL_PORTAL|NMDHB|MEDLAB|NMDHB|20250911143000||ORM^O01^ORM_O01|MSG00018|P|2.4|||AL|NE|NZL
PID|1||TYN1234^^^NHINZ^NHI~NMB012345^^^NMDHB^MR||Sullivan^Mereana^Joelene||19810712|F|||38 Hardy Street^^Nelson^^7010^NZL^C||^PRN^PH^^64^3^5462841||D|CE|||||||||N||NZL
PV1|1|O|OUTPAT^HAEM^1^^^NELHOSP||||D90871^Fraser^Duncan^^^Dr^^^NZMC|||HEM||||1|||D90871^Fraser^Duncan^^^Dr^^^NZMC|OP
ORC|NW|ORD008^CLINICAL_PORTAL||GRP008^CLINICAL_PORTAL|||||20250911143000|||D90871^Fraser^Duncan^^^Dr^^^NZMC||^WPN^PH^^64^3^5469000
OBR|1|ORD008^CLINICAL_PORTAL||COAG^Coagulation Studies^NZLT|||20250911|||||||20250911143000|Blood^Venous|||||||||||ROUTINE
OBR|2|ORD008^CLINICAL_PORTAL||FERR^Ferritin^NZLT|||20250911|||||||20250911143000|Blood^Venous|||||||||||ROUTINE
```

---

## 19. QBP^Z01 - Clinical data query for patient via Concerto portal

```
MSH|^~\&|CONCERTO|AUCKDHB|CDR|AUCKDHB|20250620083000||QBP^Z01^QBP_Q21|MSG00019|P|2.5|||AL|NE|NZL
QPD|Z01^Clinical Data Query^ORION|QRY00019|UDM4567^^^NHINZ^NHI|20240101|20250620|ALL
RCP|I|50^RD
```

---

## 20. RSP^Z02 - Clinical data query response with patient summary

```
MSH|^~\&|CDR|AUCKDHB|CONCERTO|AUCKDHB|20250620083001||RSP^Z02^RSP_K21|MSG00020|P|2.5|||AL|NE|NZL
MSA|AA|MSG00019
QAK|QRY00019|OK|Z01^Clinical Data Query^ORION|3
QPD|Z01^Clinical Data Query^ORION|QRY00019|UDM4567^^^NHINZ^NHI|20240101|20250620|ALL
PID|1||UDM4567^^^NHINZ^NHI~AKL567890^^^AUCKDHB^MR||Tomokino^Aroha^Kahurangi^^Ms||19870303|F|||74 Williamson Avenue^^Ponsonby^^1011^NZL^C||^PRN^PH^^64^21^0568194||S|CE|||||||||N||NZL
OBX|1|FT|SUMMARY^Active Conditions^ORION||E11.9 Type 2 diabetes mellitus (diagnosed 2019)\.br\I10 Essential hypertension (diagnosed 2020)\.br\J45.0 Predominantly allergic asthma (diagnosed 2005)||||||F|||20250620
OBX|2|FT|MEDS^Current Medications^ORION||Metformin 500mg BD\.br\Cilazapril 2.5mg OD\.br\Salbutamol MDI PRN||||||F|||20250620
OBX|3|FT|ALLERGY^Allergies^ORION||Penicillin - rash (recorded 2010)\.br\Ibuprofen - angioedema (recorded 2018)||||||F|||20250620
```
