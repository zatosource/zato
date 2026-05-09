# Rhapsody Integration Engine - real HL7v2 ER7 messages

## 1. ADT^A01 - Inpatient admission at MedStar Union Memorial Hospital, Baltimore

```
MSH|^~\&|ADMISSIONS|MEDSTARUM|RHAPSODY|MEDSTAR_HIE|20250312083000||ADT^A01|RHAP-ADT-20250312-000123|P|2.3|||AL|NE
EVN|A01|20250312083000
PID|1||MED-MRN-27830257^^^MEDSTAR^MR~71794306^^^SSA^SS||MENSAH^Yosef^Gordon^^||19580422|M||B|5215 Indian Head Hwy^^Rockville^MD^20852^USA||^PRN^PH^^1^443^4409416||ENG|M|||||||N
NK1|1|MENSAH^Rochelle^D|SPO^Spouse|5215 Indian Head Hwy^^Rockville^MD^20852^USA|^PRN^PH^^1^443^4918448
NK1|2|MENSAH^Clifton^E|SON^Son|5215 Indian Head Hwy^^Rockville^MD^20852^USA|^PRN^PH^^1^443^4918448
PV1|1|I|MED^4N^12^MEDSTARUM||||9050055533^Eastwood^Aldridge^M^^^MD|5915967604^Harrington^Clementine^J^^^MD|5915967604^Harrington^Clementine^J^^^MD||MED|||1|||||5915967604^Harrington^Clementine^J^^^MD|I||||||||||||||||||20250312083000||||||||20250312083000
PV2|||R06.00^Dyspnea, unspecified^ICD10~J18.9^Pneumonia, unspecified organism^ICD10
DG1|1|ICD10|J18.9^Pneumonia, unspecified organism^ICD10||20250312|A
DG1|2|ICD10|R06.00^Dyspnea, unspecified^ICD10||20250312|A
IN1|1|BCBS-MD^^^CAREFIRST|BCBS-MD|CareFirst BlueCross BlueShield||||||MD-BCBS-GRP-72018|||20250101|20251231|||PPO|Crawford^Lamont^DeShawn|5215 Indian Head Hwy|19580422|||||||||||||CF-841203567
```

---

## 2. ADT^A08 - Patient information update at LifeBridge Sinai Hospital, Baltimore

```
MSH|^~\&|REGISTRATION|SINAIHOSP|RHAPSODY|LIFEBRIDGE_HIE|20250415141200||ADT^A08|RHAP-ADT-20250415-001456|P|2.3|||AL|NE
EVN|A08|20250415141200
PID|1||LB-MRN-28281063^^^LIFEBRIDGE^MR~69435309^^^SSA^SS||PENNINGTON^Claudette^Lucille^^||19720315|F||B|1330 Wisconsin Ave^^Bel Air^MD^21014^USA||^PRN^PH^^1^443^9412556~^PRN^CP^^1^443^5941257||ENG|D|||||||N
PV1|1|O|SINAIHOSP^CLINIC3^02||||5815737077^Whitcomb^Fitzpatrick^B^^^MD|3702025168^Radcliffe^Evangeline^P^^^MD||FP|||1|||||3702025168^Radcliffe^Evangeline^P^^^MD|OP||||||||||||||||||||||||||20250415141200
```

---

## 3. ORM^O01 - Radiology order from MedStar Harbor Hospital to RIS via Rhapsody

```
MSH|^~\&|EHR|MEDSTARHBR|RIS|MEDSTAR_RAD|20250520091500||ORM^O01|RHAP-ORM-20250520-002345|P|2.3|||AL|NE
PID|1||MED-MRN-75164769^^^MEDSTAR^MR||RIDGEWAY^Demetrius^Raymond^^||19650210|M||B|7934 Moravia Rd^^St. Leonard^MD^20685^USA||^PRN^PH^^1^410^5577369||ENG|S
PV1|1|I|MED^3S^08^MEDSTARHBR||||7441266638^Worthington^Warren^C^^^MD|8108020670^Southgate^Gwendolyn^E^^^MD||MED|||1|||||8108020670^Southgate^Gwendolyn^E^^^MD|I||||||||||||||||||20250519200000
ORC|NW|MED-ORD-20250520-001^MEDSTAR|MED-ORD-20250520-001^MEDSTAR||SC|||1^^^20250520091500^^S||20250520091500|4091837265^Ogunyemi^Babatunde^K^^^MD|7441266638^Worthington^Warren^C^^^MD|7441266638^Worthington^Warren^C^^^MD||^WPN^PH^^1^410^2917000
OBR|1|MED-ORD-20250520-001^MEDSTAR|MED-ORD-20250520-001^MEDSTAR|71046^XR CHEST 2 VIEWS^CPT4|STAT|20250520091500|||||Portable requested - patient on O2||||20250519200000|||||4091837265^Ogunyemi^Babatunde^K^^^MD||||||||||1^^^20250520091500^^S
```

---

## 4. ORU^R01 - Lab result routing from LIS through Rhapsody at LifeBridge Health

```
MSH|^~\&|LIS|LIFEBRIDGE_LAB|RHAPSODY|LIFEBRIDGE_EHR|20250618143000||ORU^R01^ORU_R01|RHAP-ORU-20250618-003456|P|2.5.1|||AL|NE
PID|1||LB-MRN-13536274^^^LIFEBRIDGE^MR||MEHTA^Genevieve^Ximena^^||19800912|F||W|1290 Pratt St^^Riverdale^MD^20737^USA||^PRN^PH^^1^240^2757480||ENG|S
PV1|1|O|SINAIHOSP^LAB^01||||5553413478^Greenfield^Prescott^M^^^MD|6271159864^Carmichael^Clementine^J^^^MD||IM|||1|||||6271159864^Carmichael^Clementine^J^^^MD|OP
ORC|RE|LB-ORD-20250617-012^LIFEBRIDGE|LB-RES-20250618-3456^LIFEBRIDGE_LAB|||||||GMERRIWE^Merriweather^Genevieve^D^^^MD|5182039476^Idowu^Adebayo^M^^^MD|||^WPN^PH^^1^410^6019000
OBR|1|LB-ORD-20250617-012^LIFEBRIDGE|LB-RES-20250618-3456^LIFEBRIDGE_LAB|24323-8^Comprehensive metabolic panel^LN|||20250617080000|||||||||||5182039476^Idowu^Adebayo^M^^^MD||LB-LAB-12345||||20250618140000|||F
OBX|1|NM|2345-7^Glucose^LN|1|98|mg/dL^milligrams per deciliter^UCUM|70-100||||F|||20250617080000|||||20250618140000||||LBLAB^LifeBridge Health Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0673412|2401 W Belvedere Ave^^Baltimore^MD^21215
OBX|2|NM|3094-0^BUN^LN|2|18|mg/dL^milligrams per deciliter^UCUM|7-20||||F|||20250617080000|||||20250618140000||||LBLAB^LifeBridge Health Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0673412|2401 W Belvedere Ave^^Baltimore^MD^21215
OBX|3|NM|2160-0^Creatinine^LN|3|0.9|mg/dL^milligrams per deciliter^UCUM|0.6-1.2||||F|||20250617080000|||||20250618140000||||LBLAB^LifeBridge Health Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0673412|2401 W Belvedere Ave^^Baltimore^MD^21215
OBX|4|NM|2951-2^Sodium^LN|4|139|mmol/L^millimoles per liter^UCUM|136-145||||F|||20250617080000|||||20250618140000||||LBLAB^LifeBridge Health Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0673412|2401 W Belvedere Ave^^Baltimore^MD^21215
OBX|5|NM|2823-3^Potassium^LN|5|4.1|mmol/L^millimoles per liter^UCUM|3.5-5.1||||F|||20250617080000|||||20250618140000||||LBLAB^LifeBridge Health Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0673412|2401 W Belvedere Ave^^Baltimore^MD^21215
```

---

## 5. SIU^S12 - Scheduling message routed from MedStar Montgomery through Rhapsody

```
MSH|^~\&|SCHEDULING|MEDSTARMTG|RHAPSODY|MEDSTAR_SCH|20250714082000||SIU^S12^SIU_S12|RHAP-SIU-20250714-004567|P|2.5.1|||AL|NE
SCH|APT-20250714-4567^MEDSTARMTG||||||ROUTINE^Routine^HL70276|FOLLOWUP^Follow-up^MMAPPT|30|min^minutes^ISO31||3776834169^Eastwood^Aldridge^B^^^MD|^WPN^PH^^1^301^7741600|1215 Twinbrook Pkwy^Eastwood^Aldridge^B^20851|3776834169^Eastwood^Aldridge^B^^^MD|^WPN^PH^^1^301^7741600|1215 Twinbrook Pkwy^Eastwood^Aldridge^B^20851||||||BOOKED
PID|1||MED-MRN-96754362^^^MEDSTAR^MR||CALDWELL^Nolan^Curtis^^||19680830|M||A|1330 Wisconsin Ave^^Chesapeake Beach^MD^20732^USA||^PRN^PH^^1^301^9624145||ENG|M
PV1|1|O|MEDSTARMTG^SURG1^01||||3776834169^Eastwood^Aldridge^B^^^MD|9004150475^Harrington^Evangeline^P^^^MD||SURG|||1|||||9004150475^Harrington^Evangeline^P^^^MD|OP
RGS|1||MEDSTARMTG^MedStar Montgomery Medical Center
AIS|1||99213^Follow-up Visit^CPT|20250721100000|30|min^minutes^ISO31
AIG|1||3776834169^Eastwood^Aldridge^B^^^MD|P
```

---

## 6. VXU^V04 - Immunization message routed to Maryland ImmuNet via Rhapsody

```
MSH|^~\&|EHR|ADVENTIST_SG|RHAPSODY|MDIMMUNET|20250320091500||VXU^V04^VXU_V04|RHAP-VXU-20250320-005678|P|2.5.1|||AL|NE
PID|1||ADV-MRN-64179143^^^ADVENTIST^MR||FAIRCHILD^Rosalind^Beatrice^^||20030415|F||W|6470 Marlboro Pike^^Ellicott City^MD^21042^USA||^PRN^PH^^1^301^9426876||SPA|S
NK1|1|FAIRCHILD^Ursula^Y|MTH^Mother|6470 Marlboro Pike^^Ellicott City^MD^21042^USA|^PRN^PH^^1^301^9539615
PV1|1|O|ADVENTIST_SG^PEDS1^01||||9651487817^Whitcomb^Fitzpatrick^C^^^MD|7884857728^Radcliffe^Gwendolyn^E^^^MD||PED|||1|||||7884857728^Radcliffe^Gwendolyn^E^^^MD|OP
RXA|0|1|20250320091500|20250320091500|08^Hepatitis B Vaccine^CVX|0.5|mL^milliliters^UCUM||00^New Record^NIP001|9651487817^Whitcomb^Fitzpatrick^C^^^MD|||Z5283|20270320|MSD^Merck^MVX|||CP^Complete^HL70322
OBX|1|CE|64994-7^Vaccine Funding Source^LN||VXC1^Private^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||08^Hepatitis B Vaccine^CVX||||||F
```

---

## 7. ORU^R01 - Electronic lab report to Maryland DHMH via Rhapsody

```
MSH|^~\&|LIS|JHHOSP_LAB|RHAPSODY|MD_DHMH_ELR|20250425101500||ORU^R01^ORU_R01|RHAP-ELR-20250425-006789|P|2.5.1|||AL|NE
PID|1||JH-MRN-43979442^^^JHHOSP^MR||ISHIKAWA^Winifred^Gertrude^^||19710815|F||B|3560 Crain Hwy^^Baltimore^MD^21201^USA||^PRN^PH^^1^410^5995707||ENG|M|||599-72-5376||N
PV1|1|I|OSLER^6108^A^JHHOSP||||7201658854^Worthington^Warren^M^^^MD||MED|||1|||||3480590786^Southgate^Clementine^J^^^MD|I
ORC|RE|JH-ORD-20250423-034^JHHOSP|JH-RES-20250425-6789^JHHOSP_LAB|||||||EYAMAMOT^Yamamoto^Eleanora^D^^^MD|8204951736^Abramowitz^Daniel^P^^^MD|||^WPN^PH^^1^410^9553000
OBR|1|JH-ORD-20250423-034^JHHOSP|JH-RES-20250425-6789^JHHOSP_LAB|87040^Blood Culture^CPT|||20250423160000|||||||||||8204951736^Abramowitz^Daniel^P^^^MD||JH-LAB-56789||||20250425100000|||F
OBX|1|CE|600-7^Blood Culture^LN|1|Salmonella enterica^Salmonella enterica^SNM||||||F|||20250425090000
OBX|2|TX|18769-0^Antibiotic Sensitivities^LN|2|Ampicillin: S, Ciprofloxacin: S, TMP-SMX: S, Ceftriaxone: S, Azithromycin: S||||||F|||20250425090000
```

---

## 8. MDM^T02 - Clinical document notification routed through Rhapsody at UMMC

```
MSH|^~\&|DOCSYS|UMMCBALT|RHAPSODY|UMMC_EHR|20250605140000||MDM^T02^MDM_T02|RHAP-MDM-20250605-007890|P|2.5.1|||AL|NE
EVN|T02|20250605140000
PID|1||UM-MRN-46721285^^^UMMC^MR||THORNTON^Tobias^Lester^^||19630712|M||W|1290 Pratt St^^Pasadena^MD^21122^USA||^PRN^PH^^1^410^3708783||ENG|M
PV1|1|I|SURG^OR3^A^UMMCBALT||||9646635894^Greenfield^Prescott^B^^^MD||SURG|||1|||||3869510222^Carmichael^Evangeline^P^^^MD|I
TXA|1|OP|TX|20250605135000|9646635894^Greenfield^Prescott^B^^^MD||20250605140000||9646635894^Greenfield^Prescott^B^^^MD||||RHAP-DOC-20250605-7890|UMMCBALT||||AU||AV
OBX|1|TX|11504-8^Operative Note^LN|1|OPERATIVE REPORT~~PROCEDURE: Laparoscopic cholecystectomy.~~DATE OF PROCEDURE: 06/05/2025.~~SURGEON: Prescott B. Greenfield, MD.~~ANESTHESIA: General endotracheal.~~PREOPERATIVE DIAGNOSIS: Symptomatic cholelithiasis.~~POSTOPERATIVE DIAGNOSIS: Same.~~FINDINGS: Gallbladder with multiple stones. No acute inflammation. Calot's triangle identified clearly. Common bile duct normal caliber.~~PROCEDURE DETAIL: Standard 4-port technique. Cystic duct and artery identified, clipped, and divided. Gallbladder removed from liver bed using electrocautery. Specimen retrieved via umbilical port. All ports closed.~~ESTIMATED BLOOD LOSS: Minimal.~~COMPLICATIONS: None.~~DISPOSITION: PACU in stable condition.||||||F
```

---

## 9. ORU^R01 - Blood culture with embedded PDF routed through Rhapsody at MedStar

```
MSH|^~\&|LIS|MEDSTARUM_LAB|RHAPSODY|MEDSTAR_EHR|20250401092000||ORU^R01^ORU_R01|RHAP-ORU-20250401-008901|P|2.5.1|||AL|NE
PID|1||MED-MRN-33371388^^^MEDSTAR^MR||LEBLANC^Gilberto^Raymond^^||19500312|M||B|5245 Bladensburg Rd^^Hyattsville^MD^20782^USA||^PRN^PH^^1^410^4551306||ENG|W
PV1|1|I|MED^2N^08^MEDSTARUM||||7637298157^Eastwood^Aldridge^C^^^MD|8264807509^Harrington^Gwendolyn^E^^^MD||MED|||1|||||8264807509^Harrington^Gwendolyn^E^^^MD|I
ORC|RE|MED-ORD-20250330-045^MEDSTAR|MED-RES-20250401-8901^MEDSTARUM_LAB|||||||RWAVERLY^Waverly^Renata^N^^^MD|3028174956^Fitzgerald^Claire^M^^^MD|||^WPN^PH^^1^410^5546000
OBR|1|MED-ORD-20250330-045^MEDSTAR|MED-RES-20250401-8901^MEDSTARUM_LAB|87040^Blood Culture^CPT|||20250330160000|||||||||||3028174956^Fitzgerald^Claire^M^^^MD||MED-LAB-78901||||20250401090000|||F
OBX|1|CE|600-7^Blood Culture^LN|1|Staphylococcus aureus^Staphylococcus aureus^SNM||||||F|||20250401085000
OBX|2|TX|18769-0^Sensitivities^LN|2|Oxacillin: S, Vancomycin: S (MIC 1.0), Cefazolin: S, Clindamycin: S, TMP-SMX: S, Doxycycline: S||||||F|||20250401085000
OBX|3|ED|600-7^Blood Culture Report PDF^LN|3|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 10. ADT^A03 - Discharge message routed through Rhapsody at MedStar Good Samaritan

```
MSH|^~\&|ADMISSIONS|MEDSTARGSAM|RHAPSODY|MEDSTAR_HIE|20250828101500||ADT^A03|RHAP-ADT-20250828-009012|P|2.3|||AL|NE
EVN|A03|20250828101500
PID|1||MED-MRN-29761214^^^MEDSTAR^MR||PADILLA^Ophelia^Ximena^^||19750920|F||W|3560 Crain Hwy^^Baltimore^MD^21225^USA||^PRN^PH^^1^410^6317602||ENG|M|||553-39-8412||N
PV1|1|I|MED^3M^01^MEDSTARGSAM||||3077807204^Whitcomb^Fitzpatrick^M^^^MD||MED|||1|||||1751746192^Radcliffe^Clementine^J^^^MD|I||||||||||||||||||01^Discharged Home|||||20250825120000||20250828101500
DG1|1|ICD10|J18.9^Pneumonia, unspecified organism^ICD10||20250825|F
DG1|2|ICD10|J96.01^Acute respiratory failure with hypoxia^ICD10||20250825|F
```

---

## 11. ORU^R01 - Lipid panel routed through Rhapsody from Adventist HealthCare lab

```
MSH|^~\&|LIS|ADVENTIST_LAB|RHAPSODY|ADVENTIST_EHR|20250720143000||ORU^R01^ORU_R01|RHAP-ORU-20250720-010123|P|2.5.1|||AL|NE
PID|1||ADV-MRN-70723380^^^ADVENTIST^MR||DONOVAN^Valentina^Corinne^^||19820714|F||W|6319 Loch Raven Blvd^^Olney^MD^20832^USA||^PRN^PH^^1^410^7544694||SPA|M
PV1|1|O|ADVENTIST_SG^LAB^01||||5878780743^Worthington^Warren^B^^^MD|9835413529^Southgate^Evangeline^P^^^MD||PCP|||1|||||9835413529^Southgate^Evangeline^P^^^MD|OP
ORC|RE|ADV-ORD-20250718-056^ADVENTIST|ADV-RES-20250720-10123^ADVENTIST_LAB|||||||PADEBAYO^Adebayo^Penelope^Z^^^MD|1593847206^Delgado^Francisco^J^^^MD|||^WPN^PH^^1^240^8263000
OBR|1|ADV-ORD-20250718-056^ADVENTIST|ADV-RES-20250720-10123^ADVENTIST_LAB|80061^Lipid Panel^CPT|||20250718080000|||||||||||1593847206^Delgado^Francisco^J^^^MD||ADV-LAB-23456||||20250720140000|||F
OBX|1|NM|2093-3^Cholesterol, Total^LN|1|208|mg/dL^milligrams per deciliter^UCUM|<200|H|||F|||20250718080000|||||20250720140000||||ADVLAB^Adventist HealthCare Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0891234|9901 Medical Center Dr^^Rockville^MD^20850
OBX|2|NM|2571-8^Triglycerides^LN|2|155|mg/dL^milligrams per deciliter^UCUM|<150|H|||F|||20250718080000|||||20250720140000||||ADVLAB^Adventist HealthCare Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0891234|9901 Medical Center Dr^^Rockville^MD^20850
OBX|3|NM|2085-9^HDL Cholesterol^LN|3|45|mg/dL^milligrams per deciliter^UCUM|>40||||F|||20250718080000|||||20250720140000||||ADVLAB^Adventist HealthCare Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0891234|9901 Medical Center Dr^^Rockville^MD^20850
OBX|4|NM|13457-7^LDL Cholesterol, Calculated^LN|4|132|mg/dL^milligrams per deciliter^UCUM|<100|H|||F|||20250718080000|||||20250720140000||||ADVLAB^Adventist HealthCare Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0891234|9901 Medical Center Dr^^Rockville^MD^20850
```

---

## 12. VXU^V04 - Childhood immunization routed to Maryland ImmuNet via Rhapsody

```
MSH|^~\&|EHR|AAMC_PED|RHAPSODY|MDIMMUNET|20250508140000||VXU^V04^VXU_V04|RHAP-VXU-20250508-011234|P|2.5.1|||AL|NE
PID|1||AAMC-MRN-59178133^^^AAMC^MR||OGUNYEMI^Kendrick^Bernard^^||20230215|M||W|8257 Erdman Ave^^Hagerstown^MD^21740^USA||^PRN^PH^^1^443^6135021||ENG|S
NK1|1|OGUNYEMI^Nadine^Y|MTH^Mother|8257 Erdman Ave^^Hagerstown^MD^21740^USA|^PRN^PH^^1^443^2829364
PV1|1|O|AAMC^PEDS1^01||||7945414406^Greenfield^Prescott^C^^^MD||PED|||1|||||9654728641^Carmichael^Gwendolyn^E^^^MD|OP
RXA|0|1|20250508140000|20250508140000|110^DTAP-HEPB-IPV (PEDIARIX)^CVX|0.5|mL^milliliters^UCUM||00^New Record^NIP001|7945414406^Greenfield^Prescott^C^^^MD|||AC52B21|20260508|GSK^GlaxoSmithKline^MVX|||CP^Complete^HL70322
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V02^VFC Eligible - Medicaid/SCHIP^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||110^DTAP-HEPB-IPV (PEDIARIX)^CVX||||||F
```

---

## 13. ORM^O01 - Lab order routed through Rhapsody from GBMC to reference lab

```
MSH|^~\&|EHR|GBMC|RHAPSODY|QUEST_LAB|20250610090000||ORM^O01^ORM_O01|RHAP-ORM-20250610-012345|P|2.5.1|||AL|NE
PID|1||GB-MRN-31698689^^^GBMC^MR||MOSLEY^Demetrius^Gordon^^||19780430|M||W|8441 Eastern Ave^^Hyattsville^MD^20782^USA||^PRN^PH^^1^410^3093500||ENG|M
PV1|1|O|GBMC^LAB^01||||3388306626^Harrington^Breckenridge^P^^^MD||PCP|||1|||||5066959592^Pemberton^Dorothea^S^^^MD|OP
ORC|NW|GB-ORD-20250610-067^GBMC||||||^^^20250610100000^^R||20250610090000|4817290365^Shapiro^Rebecca^L^^^MD|3388306626^Harrington^Breckenridge^P^^^MD|3388306626^Harrington^Breckenridge^P^^^MD||^WPN^PH^^1^443^8493000
OBR|1|GB-ORD-20250610-067^GBMC||80053^Comprehensive Metabolic Panel^CPT|||20250610100000|||||Annual wellness|20250610090000||4817290365^Shapiro^Rebecca^L^^^MD
OBR|2|GB-ORD-20250610-067^GBMC||80061^Lipid Panel^CPT|||20250610100000|||||Annual wellness|20250610090000||4817290365^Shapiro^Rebecca^L^^^MD
OBR|3|GB-ORD-20250610-067^GBMC||85025^CBC with Differential^CPT|||20250610100000|||||Annual wellness|20250610090000||4817290365^Shapiro^Rebecca^L^^^MD
```

---

## 14. ORU^R01 - Hepatitis panel for public health reporting via Rhapsody

```
MSH|^~\&|LIS|JHHOSP_LAB|RHAPSODY|MD_DHMH_ELR|20250815102000||ORU^R01^ORU_R01|RHAP-ELR-20250815-013456|P|2.5.1|||AL|NE
PID|1||JH-MRN-46730135^^^JHHOSP^MR||CHANDRA^Emory^Theodore^^||19830417|M||A|7156 Park Heights Ave^^Pikesville^MD^21208^USA||^PRN^PH^^1^443^9198974||HIN|M|||335-24-1140||N
PV1|1|O|JHHOSP^LAB^01||||6205376471^Radcliffe^Gresham^W^^^MD||PCP|||1|||||1975495070^Remington^Henrietta^G^^^MD|OP
ORC|RE|JH-ORD-20250813-078^JHHOSP|JH-RES-20250815-13456^JHHOSP_LAB|||||||FHERRERA^Herrera^Francesca^B^^^MD|5930281746^Osei^Kwame^N^^^MD|||^WPN^PH^^1^410^9553000
OBR|1|JH-ORD-20250813-078^JHHOSP|JH-RES-20250815-13456^JHHOSP_LAB|80074^Hepatitis Panel, Acute^CPT|||20250813082000|||||||||||5930281746^Osei^Kwame^N^^^MD||JH-LAB-89012||||20250815100000|||F
OBX|1|CE|5196-1^Hepatitis B Surface Antigen^LN|1|POS^Reactive^LOCAL||Non-Reactive|A|||F|||20250813082000
OBX|2|CE|5195-3^Hepatitis B Surface Antibody^LN|2|NEG^Non-Reactive^LOCAL||||||F|||20250813082000
OBX|3|CE|13955-0^Hepatitis B Core Antibody, IgM^LN|3|POS^Reactive^LOCAL||Non-Reactive|A|||F|||20250813082000
OBX|4|CE|32685-6^Hepatitis C Antibody^LN|4|NEG^Non-Reactive^LOCAL||||||F|||20250813082000
```

---

## 15. ORU^R01 - Discharge summary with embedded PDF routed through Rhapsody from LifeBridge

```
MSH|^~\&|DOCSYS|SINAIHOSP|RHAPSODY|LIFEBRIDGE_EHR|20250919153000||ORU^R01^ORU_R01|RHAP-ORU-20250919-014567|P|2.5.1|||AL|NE
PID|1||LB-MRN-58227181^^^LIFEBRIDGE^MR||WHITMORE^Rowan^Zachary^^||19720325|M||B|1120 Solomons Island Rd^^Catonsville^MD^21228^USA||^PRN^PH^^1^410^8671569||ENG|D
PV1|1|I|MED^5M^04^SINAIHOSP||||4566711354^Southgate^Conrad^R^^^MD||MED|||1|||||6189724407^Fairbanks^Josephina^M^^^MD|I||||||||||||||||||01^Discharged Home|||||20250914100000||20250919153000
ORC|RE|LB-ORD-20250919-089^LIFEBRIDGE|LB-RES-20250919-14567^SINAIHOSP|||||||HVELASQU^Velasquez^Harriet^T^^^MD|6048173295^Anyanwu^Ifeoma^C^^^MD|||^WPN^PH^^1^410^6019000
OBR|1|LB-ORD-20250919-089^LIFEBRIDGE|LB-RES-20250919-14567^SINAIHOSP|18842-5^Discharge Summary^LN|||20250919150000|||||||||||6048173295^Anyanwu^Ifeoma^C^^^MD||LB-DOC-34567||||20250919152500|||F
OBX|1|TX|18842-5^Discharge Summary^LN|1|DISCHARGE SUMMARY~~PATIENT: WHITMORE, Rowan Zachary.~~ADMISSION DATE: 09/14/2025~~DISCHARGE DATE: 09/19/2025~~PRINCIPAL DIAGNOSIS: Community-acquired pneumonia (J18.9)~~HOSPITAL COURSE: Patient admitted with productive cough, fever, and hypoxia. Chest X-ray confirmed right lower lobe infiltrate. Treated with IV ceftriaxone and azithromycin, transitioned to oral levofloxacin on day 3. Oxygen weaned to room air by day 4. Afebrile for 48 hours prior to discharge.~~DISCHARGE MEDICATIONS: Levofloxacin 750mg PO daily x 5 days.~~FOLLOW-UP: PCP in 1 week.||||||F|||20250919150000
OBX|2|ED|PDF^Discharge Summary PDF^L|2|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 16. ADT^A02 - Patient transfer routed through Rhapsody at Johns Hopkins Bayview

```
MSH|^~\&|ADMISSIONS|JHBAYVIEW|RHAPSODY|JHM_HIE|20250730143000||ADT^A02|RHAP-ADT-20250730-015678|P|2.3|||AL|NE
EVN|A02|20250730143000
PID|1||JH-MRN-59593637^^^JHBAYVIEW^MR||KIRKPATRICK^Simone^Ernestine^^||19920401|F||B|8441 Eastern Ave^^Washington^DC^20008^USA||^PRN^PH^^1^202^3632954||ENG|S|||824-91-4382||N
PV1|1|I|ICU^ICU2^A^JHBAYVIEW||||5747596191^Carmichael^Randolph^P^^^MD|6331432135^Northcutt^Dorothea^S^^^MD||CCM|||T^Transfer|3MEDSURG^3108^A^JHBAYVIEW||||6331432135^Northcutt^Dorothea^S^^^MD|I||||||||||||||||||20250728090000||20250730143000
DG1|1|ICD10|I50.23^Acute on chronic systolic heart failure^ICD10||20250728|A
```

---

## 17. ORU^R01 - COVID-19 PCR result for public health reporting via Rhapsody

```
MSH|^~\&|LIS|MEDSTARUM_LAB|RHAPSODY|MD_DHMH_ELR|20250210102000||ORU^R01^ORU_R01|RHAP-ELR-20250210-016789|P|2.5.1|||AL|NE
PID|1||MED-MRN-29390454^^^MEDSTAR^MR||YAMAMOTO^Adrienne^Diane^^||19950618|F||A|1034 Light St^^Glen Burnie^MD^21060^USA||^PRN^PH^^1^443^4414872||VIE|S|||639-80-3237||N
PV1|1|O|MEDSTARUM^LAB^01||||4899607365^Harrington^Breckenridge^W^^^MD||PCP|||1|||||5453482807^Pemberton^Henrietta^G^^^MD|OP
ORC|RE|MED-ORD-20250209-100^MEDSTAR|MED-RES-20250210-16789^MEDSTARUM_LAB|||||||MASHFORD^Ashford^Marisol^Y^^^MD|4058271930^Goldstein^Aaron^B^^^MD|||^WPN^PH^^1^410^5546000
OBR|1|MED-ORD-20250209-100^MEDSTAR|MED-RES-20250210-16789^MEDSTARUM_LAB|94500-6^SARS-CoV-2 RNA NAA^LN|||20250209100000|||||||||||4058271930^Goldstein^Aaron^B^^^MD||MED-LAB-45678||||20250210100000|||F
OBX|1|CE|94500-6^SARS-CoV-2 RNA NAA^LN|1|260373001^Detected^SCT||Not Detected|A|||F|||20250210093000
```

---

## 18. ORM^O01 - Pharmacy order routed through Rhapsody at Frederick Health

```
MSH|^~\&|EHR|FREDHOSP|RHAPSODY|FRED_PHARM|20250911082000||ORM^O01^ORM_O01|RHAP-ORM-20250911-017890|P|2.5.1|||AL|NE
PID|1||FH-MRN-14491553^^^FREDHOSP^MR||PRESCOTT^Francesca^Irene^^||19880305|F||W|3901 Roland Ave^^Laurel^MD^20708^USA||^PRN^PH^^1^443^5273136||ENG|S
PV1|1|I|MED^6M^08^FREDHOSP||||1932962369^Radcliffe^Gresham^R^^^MD||MED|||1|||||7300162544^Remington^Josephina^M^^^MD|I
ORC|NW|FH-ORD-20250911-111^FREDHOSP||||||^^^20250911090000^^R||20250911082000|5720194836^Zimmerman^Gregory^W^^^MD|1932962369^Radcliffe^Gresham^R^^^MD|1932962369^Radcliffe^Gresham^R^^^MD||^WPN^PH^^1^240^5668000
OBR|1|FH-ORD-20250911-111^FREDHOSP||RX001^Pharmacy Order^L|||20250911090000||||||Routine|20250911082000||1932962369^Radcliffe^Gresham^R^^^MD
RXO|329498^Metformin HCl 500mg tab^NDC||500|mg^milligram^ISO+||N||500|mg^milligram^ISO+|0|0||PO^Oral^HL70162|||||||BID^Twice daily^HL70335
```

---

## 19. ORU^R01 - CBC with differential routed through Rhapsody at Anne Arundel Medical Center

```
MSH|^~\&|LIS|AAMC_LAB|RHAPSODY|AAMC_EHR|20250403162000||ORU^R01^ORU_R01|RHAP-ORU-20250403-018901|P|2.5.1|||AL|NE
PID|1||AAMC-MRN-33811276^^^AAMC^MR||DURAND^Kamila^Nadya^^||19680205|F||W|7934 Moravia Rd^^Glen Burnie^MD^21060^USA||^PRN^PH^^1^240^3429589||ENG|M
PV1|1|O|AAMC^LAB^01||||6582233145^Southgate^Conrad^P^^^MD|7869481962^Fairbanks^Dorothea^S^^^MD||PCP|||1|||||7869481962^Fairbanks^Dorothea^S^^^MD|OP
ORC|RE|AAMC-ORD-20250401-122^AAMC|AAMC-RES-20250403-18901^AAMC_LAB|||||||PBELLAMY^Bellamy^Paloma^N^^^MD|6381024957^Chandra^Vikram^S^^^MD|||^WPN^PH^^1^443^4815000
OBR|1|AAMC-ORD-20250401-122^AAMC|AAMC-RES-20250403-18901^AAMC_LAB|85025^CBC with Differential^CPT|||20250401093000|||||||||||6381024957^Chandra^Vikram^S^^^MD||AAMC-LAB-56789||||20250403161500|||F
OBX|1|NM|6690-2^WBC^LN|1|7.2|10*3/uL^thousands per microliter^UCUM|4.5-11.0||||F|||20250401093000|||||20250403161500||||AAMCLAB^AAMC Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0567890|2001 Medical Pkwy^^Annapolis^MD^21401
OBX|2|NM|789-8^RBC^LN|2|4.5|10*6/uL^millions per microliter^UCUM|4.0-5.5||||F|||20250401093000|||||20250403161500||||AAMCLAB^AAMC Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0567890|2001 Medical Pkwy^^Annapolis^MD^21401
OBX|3|NM|718-7^Hemoglobin^LN|3|13.5|g/dL^grams per deciliter^UCUM|12.0-16.0||||F|||20250401093000|||||20250403161500||||AAMCLAB^AAMC Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0567890|2001 Medical Pkwy^^Annapolis^MD^21401
OBX|4|NM|4544-3^Hematocrit^LN|4|40.2|%^percent^UCUM|36.0-46.0||||F|||20250401093000|||||20250403161500||||AAMCLAB^AAMC Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0567890|2001 Medical Pkwy^^Annapolis^MD^21401
OBX|5|NM|787-2^MCV^LN|5|89.3|fL^femtoliter^UCUM|80.0-100.0||||F|||20250401093000|||||20250403161500||||AAMCLAB^AAMC Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0567890|2001 Medical Pkwy^^Annapolis^MD^21401
OBX|6|NM|777-3^Platelets^LN|6|255|10*3/uL^thousands per microliter^UCUM|150-400||||F|||20250401093000|||||20250403161500||||AAMCLAB^AAMC Laboratory^CLIA&2.16.840.1.113883.19.4.6&ISO^XX^^^24D0567890|2001 Medical Pkwy^^Annapolis^MD^21401
```

---

## 20. MDM^T02 - Radiology report document notification with embedded PDF via Rhapsody at GBMC

```
MSH|^~\&|RIS|GBMC_RAD|RHAPSODY|GBMC_EHR|20250503070000||MDM^T02^MDM_T02|RHAP-MDM-20250503-019012|P|2.5.1|||AL|NE
EVN|T02|20250503070000
PID|1||GB-MRN-97951023^^^GBMC^MR||SEVILLA^Solomon^Theodore^^||19580901|M||W|6621 Sinclair Ln^^Hyattsville^MD^20782^USA||^PRN^PH^^1^410^2805118||ENG|M|||668-81-4183||N
PV1|1|E|ED^ED02^01^GBMC||||5648204807^Carmichael^Randolph^W^^^MD||EM|||1|||||2499950539^Northcutt^Henrietta^G^^^MD|OP
TXA|1|RAD|TX|20250503063000|5648204807^Carmichael^Randolph^W^^^MD||20250503070000||5648204807^Carmichael^Randolph^W^^^MD||||RHAP-DOC-20250503-19012|GBMC_RAD||||AU||AV
OBX|1|TX|72125^CT CERVICAL SPINE WITHOUT CONTRAST^LN|1|CT CERVICAL SPINE WITHOUT CONTRAST~~CLINICAL INDICATION: Motor vehicle collision, neck pain.~~FINDINGS: No acute fracture or traumatic malalignment. Mild degenerative changes at C5-C6 and C6-C7.~~IMPRESSION: No acute fracture. Mild degenerative changes.||||||F
OBX|2|ED|PDF^Radiology Report PDF^L|2|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```
