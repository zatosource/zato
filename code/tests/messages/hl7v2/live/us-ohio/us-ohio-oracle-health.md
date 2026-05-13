# Oracle Health (Cerner Millennium) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to OhioHealth Riverside Methodist

```
MSH|^~\&|CERNERPM|OHIOHEALTH_RMH|EPIC|STATE_HIE|20260314082315||ADT^A01^ADT_A01|MSG20260314082315001|P|2.5.1|||AL|NE||ASCII|||
EVN|A01|20260314082200|||KFIELDS^Fields^Karen^^^RN||OHIOHEALTH_RMH
PID|1||MRN10482736^^^OHIOHEALTH^MR~555-32-8871^^^SSA^SS||Vasquez^Maria^Cristina^^Mrs.^||19780422|F||2106-3^White^HL70005|4821 Olentangy River Rd^^Columbus^OH^43214^US^H||^PRN^PH^^^614^5558923|^WPN^PH^^^614^5551847|ENG^English^HL70296|M^Married^HL70002|||432-18-9927|||N^Not Hispanic^HL70189||||||||||
PD1|||Riverside Methodist Hospital^^10001^^^OHIOHEALTH|1842937650^Raghavan^Sunil^K^^^MD^^NPI||||||||||||
PV1|1|I|4W^4210^01^OHIOHEALTH_RMH^^^^4 West Cardiac|||1842937650^Raghavan^Sunil^K^^^MD^^NPI|8876543210^Whitmore^Lisa^M^^^MD^^NPI|9912345678^Banerjee^Ravi^^^MD^^NPI|CAR|||R|||1842937650^Raghavan^Sunil^K^^^MD^^NPI|IN||BCBS|||||||||||||||||||OHIOHEALTH_RMH|A|||20260314082200||||||
PV2|||^Chest pain, rule out acute coronary syndrome||||||||||||||||AI|||||||||||||||||||||||||
NK1|1|Vasquez^Carlos^Javier^^Mr.||^PRN^PH^^^614^5553847|SPO^Spouse^HL70063||EC^Emergency Contact^HL70131
IN1|1|BCBS-OH|4510023|Anthem Blue Cross Blue Shield of Ohio|4361 Irwin Simpson Rd^^Mason^OH^45040^US|^PRN^PH^^^800^5551234|GRP-OH-88421|||OHIOHEALTH||||20250101|20261231|||Vasquez^Maria^Cristina|SEL^Self^HL70063|19780422|4821 Olentangy River Rd^^Columbus^OH^43214^US|||1||||||||||||||XYZ773219880|||||||F
DG1|1||I25.10^Atherosclerotic heart disease of native coronary artery without angina pectoris^ICD10|||A|||||||||1|
GT1|1||Vasquez^Maria^Cristina^^Mrs.||4821 Olentangy River Rd^^Columbus^OH^43214^US|^PRN^PH^^^614^5558923||19780422|F||SEL^Self^HL70063|432-18-9927
```

---

## 2. ADT^A04 - Patient registration at University Hospitals Cleveland emergency department

```
MSH|^~\&|CERNERPM|UH_CMC|RHAPSODY|UH_INTEGRATION|20260402143022||ADT^A04^ADT_A01|MSG20260402143022002|P|2.5.1|||AL|NE||ASCII|||
EVN|A04|20260402142900|||TBROWN^Brown^Tamika^^^REG||UH_CMC
PID|1||MRN20198734^^^UH^MR||Jefferson^Darnell^Tyrone^^Mr.^||19650911|M||2054-5^Black or African American^HL70005|1127 E 79th St^^Cleveland^OH^44103^US^H||^PRN^PH^^^216^5556234||ENG^English^HL70296|S^Single^HL70002|||298-44-1023|||N^Not Hispanic^HL70189||||||||||
PV1|1|E|ED^ED12^01^UH_CMC^^^^Emergency Dept|||9988776655^Thornton^Rebecca^L^^^MD^^NPI||||||R|||9988776655^Thornton^Rebecca^L^^^MD^^NPI|ER||MEDICARE|||||||||||||||||||UH_CMC|A|||20260402142900||||||
PV2|||^Acute onset shortness of breath||||||||||||||||AI|||||||||||||||||||||||||
NK1|1|Jefferson^Sandra^Renee^^Ms.||^PRN^PH^^^216^5553190|SIS^Sister^HL70063||EC^Emergency Contact^HL70131
IN1|1|MCARE-A|5520019|Medicare Part A|7500 Security Blvd^^Baltimore^MD^21244^US||||||||20240101|20261231|||Jefferson^Darnell^Tyrone|SEL^Self^HL70063|19650911|1127 E 79th St^^Cleveland^OH^44103^US|||1||||||||||||||1EG4-TE5-MK72|||||||M
DG1|1||J96.00^Acute respiratory failure, unspecified whether with hypoxia or hypercapnia^ICD10|||A|||||||||1|
```

---

## 3. ADT^A03 - Patient discharge from Mercy Health St. Vincent Medical Center

```
MSH|^~\&|CERNERPM|MERCY_STVINCENT|CLOVERLEAF|MERCY_HIE|20260419161545||ADT^A03^ADT_A03|MSG20260419161545003|P|2.5.1|||AL|NE||ASCII|||
EVN|A03|20260419161000|||KPARKER^Parker^Karen^^^RN||MERCY_STVINCENT
PID|1||MRN30876234^^^MERCY^MR||Kowalczyk^Stanley^Edward^^Mr.^||19520318|M||2106-3^White^HL70005|2930 W Sylvania Ave^^Toledo^OH^43613^US^H||^PRN^PH^^^419^5557812||ENG^English^HL70296|W^Widowed^HL70002|||187-56-3421|||N^Not Hispanic^HL70189||||||||||
PV1|1|I|3N^318^01^MERCY_STVINCENT^^^^3 North Med/Surg|||5566778899^Calloway^Thomas^R^^^MD^^NPI|||||MED||R||5566778899^Calloway^Thomas^R^^^MD^^NPI|IN||AETNA|||||||||||||||||||MERCY_STVINCENT|D|||20260415093000|20260419161000|||||
PV2|||^COPD exacerbation with acute bronchitis|||||||||||||||||||||||||||||||||||||||
DG1|1||J44.1^Chronic obstructive pulmonary disease with (acute) exacerbation^ICD10|||A|||||||||1|
DG1|2||J20.9^Acute bronchitis, unspecified^ICD10|||A|||||||||2|
```

---

## 4. ORM^O01 - Lab order from OhioHealth Grant Medical Center

```
MSH|^~\&|POWERCHART|OHIOHEALTH_GMC|SUNQUEST|OHIOHEALTH_LAB|20260507091823||ORM^O01^ORM_O01|MSG20260507091823004|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN40293187^^^OHIOHEALTH^MR||Kapoor^Priya^Nalini^^Ms.^||19900715|F||2028-9^Asian^HL70005|891 S High St^^Columbus^OH^43206^US^H||^PRN^PH^^^614^5554091||ENG^English^HL70296|S^Single^HL70002|||612-78-4532|||N^Not Hispanic^HL70189||||||||||
PV1|1|I|ICU^ICU04^01^OHIOHEALTH_GMC^^^^Intensive Care|||7766554433^Delgado^Miguel^A^^^MD^^NPI||||||R|||7766554433^Delgado^Miguel^A^^^MD^^NPI|IN||UHCOH|||||||||||||||||||OHIOHEALTH_GMC|A|||20260506220000||||||
ORC|NW|ORD-2026050709001^POWERCHART|||||^^^20260507092000^^R||20260507091800|JANDERSON^Anderson^Julia^^^RN|||||OHIOHEALTH_GMC^Grant Medical Center^HL70362||||
OBR|1|ORD-2026050709001^POWERCHART||80053^Comprehensive Metabolic Panel^CPT4|||20260507091500|||||||||7766554433^Delgado^Miguel^A^^^MD^^NPI||||||||||^^^20260507092000^^R||||||||||||||||
OBR|2|ORD-2026050709002^POWERCHART||85025^Complete Blood Count with Differential^CPT4|||20260507091500|||||||||7766554433^Delgado^Miguel^A^^^MD^^NPI||||||||||^^^20260507092000^^R||||||||||||||||
OBR|3|ORD-2026050709003^POWERCHART||82374^Carbon Dioxide (Bicarbonate)^CPT4|||20260507091500|||||||||7766554433^Delgado^Miguel^A^^^MD^^NPI||||||||||^^^20260507092000^^R||||||||||||||||
```

---

## 5. ORU^R01 - Lab results from ProMedica Toledo Hospital

```
MSH|^~\&|MILLENNIUM|PROMEDICA_TH|MIRTH|PROMEDICA_HIE|20260328104532||ORU^R01^ORU_R01|MSG20260328104532005|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN50182934^^^PROMEDICA^MR||Reyes^Elena^Sofia^^Mrs.^||19830209|F||2106-3^White^HL70005|3415 Airport Hwy^^Toledo^OH^43609^US^H||^PRN^PH^^^419^5552847||SPA^Spanish^HL70296|M^Married^HL70002|||278-91-6534|||2135-2^Hispanic or Latino^HL70189||||||||||
PV1|1|O|LAB^DRAW01^01^PROMEDICA_TH^^^^Outpatient Lab|||3344556677^Montoya^Sofia^C^^^MD^^NPI||||||R|||3344556677^Montoya^Sofia^C^^^MD^^NPI|OUT||MEDICAID|||||||||||||||||||PROMEDICA_TH|A|||20260328100000||||||
ORC|RE|ORD-2026032810001^MILLENNIUM||||||||||3344556677^Montoya^Sofia^C^^^MD^^NPI||||||||
OBR|1|ORD-2026032810001^MILLENNIUM|RES-2026032810001^PROMEDICA_LAB|80048^Basic Metabolic Panel^CPT4|||20260328100500|||||||20260328101000|119364003^Serum^SCT|3344556677^Montoya^Sofia^C^^^MD^^NPI||||||20260328104500|||F||||||||||||||||
OBX|1|NM|2345-7^Glucose^LN||98|mg/dL|74-106||||F|||20260328103000||LAB-AUTO^Automated Analyzer||
OBX|2|NM|3094-0^Urea nitrogen^LN||14|mg/dL|6-20||||F|||20260328103000||LAB-AUTO^Automated Analyzer||
OBX|3|NM|2160-0^Creatinine^LN||0.9|mg/dL|0.7-1.3||||F|||20260328103000||LAB-AUTO^Automated Analyzer||
OBX|4|NM|2951-2^Sodium^LN||140|mmol/L|136-145||||F|||20260328103000||LAB-AUTO^Automated Analyzer||
OBX|5|NM|2823-3^Potassium^LN||4.2|mmol/L|3.5-5.1||||F|||20260328103000||LAB-AUTO^Automated Analyzer||
OBX|6|NM|2075-0^Chloride^LN||102|mmol/L|98-106||||F|||20260328103000||LAB-AUTO^Automated Analyzer||
OBX|7|NM|2028-9^Carbon dioxide, total^LN||24|mmol/L|21-32||||F|||20260328103000||LAB-AUTO^Automated Analyzer||
OBX|8|NM|17861-6^Calcium^LN||9.4|mg/dL|8.6-10.3||||F|||20260328103000||LAB-AUTO^Automated Analyzer||
```

---

## 6. ORU^R01 - Radiology report with base64 PDF from Cleveland Clinic Akron General

```
MSH|^~\&|MILLENNIUM|CCAG|MIRTH|CC_INTEGRATION|20260215134221||ORU^R01^ORU_R01|MSG20260215134221006|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN60493827^^^CCAG^MR||Brennan^Robert^Lee^^Mr.^||19710824|M||2106-3^White^HL70005|1542 Market St^^Akron^OH^44313^US^H||^PRN^PH^^^330^5559182||ENG^English^HL70296|M^Married^HL70002|||334-72-8190|||N^Not Hispanic^HL70189||||||||||
PV1|1|O|RAD^CT01^01^CCAG^^^^Radiology|||2233445566^Okonkwo^David^M^^^MD^^NPI||||||R|||2233445566^Okonkwo^David^M^^^MD^^NPI|OUT||ANTHEM|||||||||||||||||||CCAG|A|||20260215130000||||||
ORC|RE|ORD-2026021513001^MILLENNIUM||||||||||2233445566^Okonkwo^David^M^^^MD^^NPI||||||||
OBR|1|ORD-2026021513001^MILLENNIUM|RES-2026021513001^CCAG_RAD|71260^CT Chest with contrast^CPT4|||20260215130500|||||||20260215131500|119364003^Serum^SCT|2233445566^Okonkwo^David^M^^^MD^^NPI||ACCN-20260215-0042||||20260215134200|||F||||||||||||||||
OBX|1|TX|71260^CT Chest with contrast^CPT4|1|CT CHEST WITH CONTRAST - FINAL REPORT~Patient: Brennan, Robert L. DOB: 08/24/1971 MRN: 60493827~Clinical History: Persistent cough for 6 weeks, weight loss. R/O malignancy.~Technique: Helical CT of the chest performed with 80mL Omnipaque 350 IV contrast.~Findings:~Lungs: No pulmonary nodules or masses identified. No consolidation or ground glass opacity.~Airways: Trachea and mainstem bronchi are patent. No endobronchial lesion.~Mediastinum: No lymphadenopathy. Heart size is normal. No pericardial effusion.~Pleura: No pleural effusion or pneumothorax. No pleural thickening.~Chest Wall: No osseous lesions. Mild degenerative changes of the thoracic spine.~Upper Abdomen: Visualized portions of the liver, spleen, and adrenal glands are unremarkable.~Impression: 1. No evidence of pulmonary malignancy. 2. Mild thoracic spondylosis.||||||F|||20260215133000||RAD-OKON^Okonkwo^David^M^^^MD||
OBX|2|ED|71260^CT Chest with contrast^CPT4|2|^application^pdf^Base64^JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NDIgPj4Kc3RyZWFtCkJUCi9GMSAxNCBUZgoxMDAgNzAwIFRkCihDVCBDSEVTVCBXSVRIIENPTlRSQVNUIC0gRklOQUwgUkVQT1JUKSBUagovRjEgMTIgVGYKMTAwIDY4MCBUZAooUGF0aWVudDogVGhvbXBzb24sIFJvYmVydCBMLikgVGoKMTAwIDY2MCBUZAooRE9COiAwOC8yNC8xOTcxIE1STjogNjA0OTM4MjcpIFRqCjEwMCA2MjAgVGQKKEltcHJlc3Npb246KSBUagovRjEgMTIgVGYKMTAwIDYwMCBUZAooMS4gTm8gZXZpZGVuY2Ugb2YgcHVsbW9uYXJ5IG1hbGlnbmFuY3kuKSBUagoxMDAgNTgwIFRkCigyLiBNaWxkIHRob3JhY2ljIHNwb25keWxvc2lzLikgVGoKMTAwIDU0MCBUZAooRGljdGF0ZWQgYnk6IERhdmlkIE0uIEZpdHpnZXJhbGQsIE1EKSBUagoxMDAgNTIwIFRkCihFbGVjdHJvbmljYWxseSBzaWduZWQgMDIvMTUvMjAyNiAxMzozMCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZldGljYSA+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDE1IDAwMDAwIG4gCjAwMDAwMDAwNjggMDAwMDAgbiAKMDAwMDAwMDEyNSAwMDAwMCBuIAowMDAwMDAwMzI0IDAwMDAwIG4gCjAwMDAwMDA4MTcgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo5MDQKJSVFT0YK||||||F|||20260215134100||RAD-OKON^Okonkwo^David^M^^^MD||
```

---

## 7. ADT^A08 - Patient information update at Kettering Health Main Campus

```
MSH|^~\&|CERNERPM|KHMAIN|CLOVERLEAF|KH_HIE|20260123110430||ADT^A08^ADT_A01|MSG20260123110430007|P|2.5.1|||AL|NE||ASCII|||
EVN|A08|20260123110400|||MLOPEZ^Lopez^Maria^^^REG||KHMAIN
PID|1||MRN70384921^^^KETTERING^MR||O'Malley^Patrick^Declan^^Mr.^||19880603|M||2106-3^White^HL70005|4120 Far Hills Ave^^Kettering^OH^45429^US^H||^PRN^PH^^^937^5558341|^WPN^PH^^^937^5551122|ENG^English^HL70296|M^Married^HL70002|||445-93-2817|||N^Not Hispanic^HL70189||||||||||
PD1|||Kettering Health Main Campus^^20001^^^KETTERING|6655443322^Strickland^Colleen^M^^^MD^^NPI||||||||||||
PV1|1|I|5E^512^01^KHMAIN^^^^5 East Ortho|||6655443322^Strickland^Colleen^M^^^MD^^NPI||||||R|||6655443322^Strickland^Colleen^M^^^MD^^NPI|IN||UNITED|||||||||||||||||||KHMAIN|A|||20260121140000||||||
NK1|1|O'Malley^Shannon^Marie^^Mrs.||^PRN^PH^^^937^5558342|SPO^Spouse^HL70063||EC^Emergency Contact^HL70131
IN1|1|UHC-OH|7720034|UnitedHealthcare of Ohio|185 Asylum St^^Hartford^CT^06103^US|^PRN^PH^^^800^5559876|GRP-OH-19283|||KETTERING||||20260101|20261231|||O'Malley^Patrick^Declan|SEL^Self^HL70063|19880603|4120 Far Hills Ave^^Kettering^OH^45429^US|||1||||||||||||||UHC88201934|||||||M
```

---

## 8. SIU^S12 - Appointment scheduling at Aultman Hospital Canton

```
MSH|^~\&|MILLENNIUM|AULTMAN_MAIN|MIRTH|AULTMAN_SCHED|20260610083045||SIU^S12^SIU_S12|MSG20260610083045008|P|2.5.1|||AL|NE||ASCII|||
SCH|APPT-2026061008001^MILLENNIUM|||||MOD^Modifier^HL70277|ROUTINE^Routine^HL70277|OFFICE^Office visit^HL70277|30|MIN^Minutes^HL70277||4455667788^Novotny^Mark^J^^^MD^^NPI|^WPN^PH^^^330^5554200||4455667788^Novotny^Mark^J^^^MD^^NPI|^WPN^PH^^^330^5554200|||||BOOKED^Booked^HL70278|
PID|1||MRN80293746^^^AULTMAN^MR||Hubbard^Kevin^Wayne^^Mr.^||19960112|M||2106-3^White^HL70005|2987 Tuscarawas St W^^Canton^OH^44708^US^H||^PRN^PH^^^330^5553719||ENG^English^HL70296|S^Single^HL70002|||621-83-4912|||N^Not Hispanic^HL70189||||||||||
PV1|1|O|CARDCLINIC^EXAM3^01^AULTMAN_MAIN^^^^Cardiology Clinic|||4455667788^Novotny^Mark^J^^^MD^^NPI||||||R|||4455667788^Novotny^Mark^J^^^MD^^NPI|OUT||BCBS|||||||||||||||||||AULTMAN_MAIN|P|||20260617140000||||||
RGS|1||CARDCLINIC^Cardiology Clinic^HL70069
AIS|1||CARDCONS^Cardiology Consultation^HL70088|20260617140000|30|MIN^Minutes^HL70277||30|MIN^Minutes^HL70277|||||
AIG|1||4455667788^Novotny^Mark^J^^^MD^^NPI|PHYSICIAN^Physician^HL70337|||||20260617140000|30|MIN^Minutes^HL70277||
AIL|1||CARDCLINIC^EXAM3^01^AULTMAN_MAIN|CLINIC^Clinic^HL70305||||20260617140000|30|MIN^Minutes^HL70277||
```

---

## 9. DFT^P03 - Charge posting from Summa Health Akron City Hospital

```
MSH|^~\&|MILLENNIUM|SUMMA_ACH|MIRTH|SUMMA_BILLING|20260225153712||DFT^P03^DFT_P03|MSG20260225153712009|P|2.5.1|||AL|NE||ASCII|||
EVN|P03|20260225153700|||BILLING_SYS||SUMMA_ACH
PID|1||MRN90127483^^^SUMMA^MR||Washington^Terrence^Alan^^Mr.^||19750430|M||2054-5^Black or African American^HL70005|498 W Market St^^Akron^OH^44303^US^H||^PRN^PH^^^330^5557283||ENG^English^HL70296|D^Divorced^HL70002|||519-28-7341|||N^Not Hispanic^HL70189||||||||||
PV1|1|I|6S^608^01^SUMMA_ACH^^^^6 South Surgical|||7788990011^Prescott^Angela^R^^^MD^^NPI||||||R|||7788990011^Prescott^Angela^R^^^MD^^NPI|IN||HUMANA|||||||||||||||||||SUMMA_ACH|A|||20260223070000||||||
FT1|1|20260224||CG|47562^Laparoscopic cholecystectomy^CPT4||1|||47562^Laparoscopic cholecystectomy^CPT4|||||SUMMA_ACH^Summa Health Akron City Hospital||||||7788990011^Prescott^Angela^R^^^MD^^NPI||47562^Laparoscopic cholecystectomy^CPT4|K80.20^Calculus of gallbladder without cholecystitis^ICD10|||||||||
FT1|2|20260224||CG|36556^Insertion of non-tunneled centrally inserted central venous catheter^CPT4||1|||36556^Central venous catheter insertion^CPT4|||||SUMMA_ACH^Summa Health Akron City Hospital||||||7788990011^Prescott^Angela^R^^^MD^^NPI||36556^Central venous catheter^CPT4|K80.20^Calculus of gallbladder without cholecystitis^ICD10|||||||||
FT1|3|20260224||CG|99223^Initial hospital care, high complexity^CPT4||1|||99223^Initial hospital care^CPT4|||||SUMMA_ACH^Summa Health Akron City Hospital||||||7788990011^Prescott^Angela^R^^^MD^^NPI||99223^Initial hospital care^CPT4|K80.20^Calculus of gallbladder without cholecystitis^ICD10|||||||||
DG1|1||K80.20^Calculus of gallbladder without cholecystitis^ICD10|||A|||||||||1|
```

---

## 10. ADT^A02 - Patient transfer at Mount Carmel East Hospital

```
MSH|^~\&|CERNERPM|MCE|CLOVERLEAF|TRINITY_HIE|20260511172200||ADT^A02^ADT_A02|MSG20260511172200010|P|2.5.1|||AL|NE||ASCII|||
EVN|A02|20260511172100|||RNELSON^Nelson^Rita^^^RN||MCE
PID|1||MRN11029384^^^MOUNTCARMEL^MR||Sawicki^Diane^Marie^^Ms.^||19610719|F||2106-3^White^HL70005|6712 Livingston Ave^^Reynoldsburg^OH^43068^US^H||^PRN^PH^^^614^5554823||ENG^English^HL70296|W^Widowed^HL70002|||278-45-9123|||N^Not Hispanic^HL70189||||||||||
PV1|1|I|ICU^ICU08^01^MCE^^^^ICU|||1122334455^Feldstein^Jonathan^D^^^MD^^NPI||||||R|||1122334455^Feldstein^Jonathan^D^^^MD^^NPI|IN||AETNA||||||||||||||||||20260511172100|MCE|T|||20260509083000||||||
PV2|||^Post-operative respiratory compromise following total knee arthroplasty||||||||||||||||AI|||||||||||||||||||||||||
ZPV|3S^304^01^MCE^^^^3 South Ortho|20260509083000|20260511172100|Transferred from 3 South Ortho to ICU per Dr. Feldstein due to desaturation event
```

---

## 11. MDM^T02 - Transcription document from Fairfield Medical Center Lancaster

```
MSH|^~\&|POWERCHART|FMC|MIRTH|FMC_DOCUMENTS|20260305091422||MDM^T02^MDM_T02|MSG20260305091422011|P|2.5.1|||AL|NE||ASCII|||
EVN|T02|20260305091400|||TRANS_SYS||FMC
PID|1||MRN12093847^^^FMC^MR||Harmon^Nancy^Louise^^Mrs.^||19570812|F||2106-3^White^HL70005|1283 N Memorial Dr^^Lancaster^OH^43130^US^H||^PRN^PH^^^740^5558274||ENG^English^HL70296|M^Married^HL70002|||432-91-7823|||N^Not Hispanic^HL70189||||||||||
PV1|1|O|CARD^EXAM1^01^FMC^^^^Cardiology Clinic|||8899001122^Ellsworth^Richard^G^^^MD^^NPI||||||R|||8899001122^Ellsworth^Richard^G^^^MD^^NPI|OUT||BCBS|||||||||||||||||||FMC|A|||20260305090000||||||
TXA|1|HP^History and Physical^HL70270|TX^Text^HL70191|20260305091400||20260305091400|||||8899001122^Ellsworth^Richard^G^^^MD^^NPI|DOC-20260305-0019^POWERCHART||||||AV^Available^HL70271||||||
OBX|1|TX|HP^History and Physical^HL70270|1|HISTORY AND PHYSICAL~Date of Service: 03/05/2026~Patient: Harmon, Nancy L. DOB: 08/12/1957 MRN: 12093847~Referring Physician: Richard G. Ellsworth, MD~Chief Complaint: Follow-up evaluation of atrial fibrillation.~History of Present Illness: Mrs. Harmon is a 68-year-old female with a history of paroxysmal~atrial fibrillation diagnosed in 2023, currently on apixaban 5mg twice daily and metoprolol~succinate 50mg daily. She reports occasional palpitations occurring approximately twice per~month, each lasting less than 30 minutes. She denies syncope, presyncope, chest pain, or~dyspnea on exertion. She remains physically active, walking 2 miles daily.~Past Medical History: Paroxysmal atrial fibrillation, hypertension, hyperlipidemia,~osteoarthritis bilateral knees.~Current Medications: Apixaban 5mg BID, metoprolol succinate 50mg daily, lisinopril 20mg~daily, atorvastatin 40mg daily, acetaminophen 500mg PRN.~Physical Examination: BP 128/78, HR 72 regular, RR 16, O2 sat 98% on RA. Heart RRR,~no murmurs, gallops, or rubs. Lungs CTA bilaterally.~Assessment and Plan: 1. Paroxysmal atrial fibrillation - well controlled on current regimen.~Continue apixaban and metoprolol. Repeat Holter monitor in 6 months. 2. Hypertension -~at goal. Continue lisinopril. 3. Return visit in 6 months or sooner if symptoms worsen.~Electronically signed by Richard G. Ellsworth, MD on 03/05/2026 09:14||||||F|||20260305091400||8899001122^Ellsworth^Richard^G^^^MD||
```

---

## 12. ORU^R01 - Microbiology culture results from Adena Health System Chillicothe

```
MSH|^~\&|MILLENNIUM|ADENA_RMC|MIRTH|ADENA_HIE|20260418162334||ORU^R01^ORU_R01|MSG20260418162334012|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN13847291^^^ADENA^MR||Gruber^James^Robert^^Mr.^||19480226|M||2106-3^White^HL70005|72 Paint Creek Rd^^Chillicothe^OH^45601^US^H||^PRN^PH^^^740^5553294||ENG^English^HL70296|M^Married^HL70002|||287-43-9128|||N^Not Hispanic^HL70189||||||||||
PV1|1|I|4E^410^01^ADENA_RMC^^^^4 East Med/Surg|||9900112233^Beasley^William^E^^^MD^^NPI||||||R|||9900112233^Beasley^William^E^^^MD^^NPI|IN||MEDICARE|||||||||||||||||||ADENA_RMC|A|||20260416100000||||||
ORC|RE|ORD-2026041610001^MILLENNIUM||||||||||9900112233^Beasley^William^E^^^MD^^NPI||||||||
OBR|1|ORD-2026041610001^MILLENNIUM|RES-2026041816001^ADENA_LAB|87086^Urine Culture^CPT4|||20260416103000|||||||20260416110000|446131000124102^Urine specimen^SCT|9900112233^Beasley^William^E^^^MD^^NPI||||||20260418162300|||F||||||||||||||||
OBX|1|TX|87086^Urine Culture^CPT4|1|URINE CULTURE - FINAL REPORT||||||F|||20260418160000||LAB-MICRO^Microbiology||
OBX|2|TX|87086^Urine Culture^CPT4|2|Source: Clean catch midstream urine||||||F|||20260418160000||LAB-MICRO^Microbiology||
OBX|3|TX|87086^Urine Culture^CPT4|3|Colony Count: >100,000 CFU/mL||||||F|||20260418160000||LAB-MICRO^Microbiology||
OBX|4|TX|87086^Urine Culture^CPT4|4|Organism: Escherichia coli||||||F|||20260418160000||LAB-MICRO^Microbiology||
OBX|5|TX|87086^Urine Culture^CPT4|5|SENSITIVITY RESULTS:||||||F|||20260418160000||LAB-MICRO^Microbiology||
OBX|6|TX|87086^Urine Culture^CPT4|6|Ampicillin ............. R (MIC >= 32)||||||F|||20260418160000||LAB-MICRO^Microbiology||
OBX|7|TX|87086^Urine Culture^CPT4|7|Ceftriaxone ............ S (MIC <= 1)||||||F|||20260418160000||LAB-MICRO^Microbiology||
OBX|8|TX|87086^Urine Culture^CPT4|8|Ciprofloxacin .......... S (MIC <= 0.25)||||||F|||20260418160000||LAB-MICRO^Microbiology||
OBX|9|TX|87086^Urine Culture^CPT4|9|Nitrofurantoin ......... S (MIC <= 16)||||||F|||20260418160000||LAB-MICRO^Microbiology||
OBX|10|TX|87086^Urine Culture^CPT4|10|Trimethoprim/Sulfa ..... R (MIC >= 8/152)||||||F|||20260418160000||LAB-MICRO^Microbiology||
```

---

## 13. ORM^O01 - Radiology order from Mercy Health Anderson Hospital Cincinnati

```
MSH|^~\&|POWERCHART|MERCY_ANDERSON|CLOVERLEAF|MERCY_RAD|20260719141530||ORM^O01^ORM_O01|MSG20260719141530013|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN14928374^^^MERCY^MR||Tran^Linh^Ngoc^^Ms.^||19920318|F||2028-9^Asian^HL70005|8391 Beechmont Ave^^Cincinnati^OH^45255^US^H||^PRN^PH^^^513^5557821||ENG^English^HL70296|S^Single^HL70002|||612-84-2931|||N^Not Hispanic^HL70189||||||||||
PV1|1|E|ED^ED05^01^MERCY_ANDERSON^^^^Emergency Dept|||3344998877^Kavanaugh^Emre^T^^^MD^^NPI||||||R|||3344998877^Kavanaugh^Emre^T^^^MD^^NPI|ER||ANTHEM|||||||||||||||||||MERCY_ANDERSON|A|||20260719135500||||||
ORC|NW|ORD-2026071914001^POWERCHART|||||^^^20260719142000^^S||20260719141500|DNGUYEN^Nguyen^Donna^^^RN|||||MERCY_ANDERSON^Mercy Health Anderson Hospital^HL70362||||
OBR|1|ORD-2026071914001^POWERCHART||71046^Chest X-ray, 2 views^CPT4|||20260719141500||||||^Acute right-sided chest pain, shortness of breath|119364003^Serum^SCT|3344998877^Kavanaugh^Emre^T^^^MD^^NPI||||||||||^^^20260719142000^^S||||||||||||||||
DG1|1||R07.1^Chest pain on breathing^ICD10|||A|||||||||1|
DG1|2||R06.00^Dyspnea, unspecified^ICD10|||A|||||||||2|
```

---

## 14. ADT^A01 - Newborn admission at Nationwide Children's Hospital Columbus

```
MSH|^~\&|CERNERPM|NCH|MIRTH|NCH_HIE|20260801064512||ADT^A01^ADT_A01|MSG20260801064512014|P|2.5.1|||AL|NE||ASCII|||
EVN|A01|20260801064000|||LGARCIA^Garcia^Laura^^^RN||NCH
PID|1||MRN15002938^^^NCH^MR||Westbrook^Baby Girl^^^^^||20260801|F||2106-3^White^HL70005|4520 Reed Rd^^Columbus^OH^43220^US^H||^PRN^PH^^^614^5559432||ENG^English^HL70296|S^Single^HL70002|||||||N^Not Hispanic^HL70189||||||||||
PD1|||Nationwide Children's Hospital^^30001^^^NCH|5544332211^Venkatesh^Deepa^S^^^MD^^NPI||||||||||||
NK1|1|Westbrook^Jessica^Anne^^Mrs.||^PRN^PH^^^614^5559432|MTH^Mother^HL70063||EC^Emergency Contact^HL70131
NK1|2|Westbrook^Brian^Michael^^Mr.||^PRN^PH^^^614^5559433|FTH^Father^HL70063||EC^Emergency Contact^HL70131
PV1|1|I|NICU^NICU12^01^NCH^^^^Neonatal ICU|||5544332211^Venkatesh^Deepa^S^^^MD^^NPI||||||R|||5544332211^Venkatesh^Deepa^S^^^MD^^NPI|IN||ANTHEM|||||||||||||||||||NCH|A|||20260801064000||||||
PV2|||^Premature infant, 34 weeks gestational age, respiratory distress||||||||||||||||AI|||||||||||||||||||||||||
IN1|1|BCBS-OH|4510023|Anthem Blue Cross Blue Shield of Ohio|4361 Irwin Simpson Rd^^Mason^OH^45040^US|^PRN^PH^^^800^5551234|GRP-OH-44219|||NCH||||20260101|20261231|||Westbrook^Jessica^Anne|MTH^Mother^HL70063|19940312|4520 Reed Rd^^Columbus^OH^43220^US|||1||||||||||||||ANTH-92834711|||||||F
DG1|1||P07.38^Other preterm infants, gestational age 34 completed weeks^ICD10|||A|||||||||1|
DG1|2||P22.0^Respiratory distress syndrome of newborn^ICD10|||A|||||||||2|
```

---

## 15. ORU^R01 - Pathology report with base64 embedded image from OhioHealth Dublin Methodist

```
MSH|^~\&|MILLENNIUM|OHIOHEALTH_DMH|MIRTH|OHIOHEALTH_HIE|20260922114507||ORU^R01^ORU_R01|MSG20260922114507015|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN16384729^^^OHIOHEALTH^MR||Gallagher^Colleen^Ann^^Mrs.^||19690305|F||2106-3^White^HL70005|6293 Avery Rd^^Dublin^OH^43016^US^H||^PRN^PH^^^614^5551823||ENG^English^HL70296|M^Married^HL70002|||387-21-9456|||N^Not Hispanic^HL70189||||||||||
PV1|1|O|PATH^PROC01^01^OHIOHEALTH_DMH^^^^Pathology|||6677889900^Ishikawa^Kenji^H^^^MD^^NPI||||||R|||6677889900^Ishikawa^Kenji^H^^^MD^^NPI|OUT||UHC|||||||||||||||||||OHIOHEALTH_DMH|A|||20260920100000||||||
ORC|RE|ORD-2026092010001^MILLENNIUM||||||||||6677889900^Ishikawa^Kenji^H^^^MD^^NPI||||||||
OBR|1|ORD-2026092010001^MILLENNIUM|RES-2026092211001^OHIOHEALTH_PATH|88305^Surgical Pathology^CPT4|||20260920100500|||||||20260920103000||6677889900^Ishikawa^Kenji^H^^^MD^^NPI||SURG-PATH-2026-04182||||20260922114500|||F||||||||||||||||
OBX|1|TX|88305^Surgical Pathology^CPT4|1|SURGICAL PATHOLOGY REPORT~Accession: SURG-PATH-2026-04182~Patient: Gallagher, Colleen A. DOB: 03/05/1969 MRN: 16384729~Specimen: Left breast, excisional biopsy~Clinical History: 52-year-old female with palpable left breast mass identified on~mammography as BI-RADS 4B. Core biopsy showed atypical ductal hyperplasia.~Gross Description: Received fresh is an oriented excisional biopsy specimen from the left~breast measuring 4.2 x 3.1 x 2.8 cm. The specimen is inked: superior-blue, inferior-green,~medial-red, lateral-black. Serial sectioning reveals a firm, tan-white, stellate mass~measuring 1.4 x 1.2 x 1.0 cm. Representative sections submitted in cassettes A1-A6.~Microscopic Description: Sections show a well-differentiated invasive ductal carcinoma,~Nottingham grade I (tubule formation 2, nuclear pleomorphism 1, mitotic count 1).~The tumor measures 1.4 cm in greatest dimension. No lymphovascular invasion identified.~All surgical margins are negative, with the closest margin (inferior) at 0.4 cm.~Immunohistochemistry: ER positive (95%, strong), PR positive (80%, strong),~HER2 negative (1+ by IHC), Ki-67 proliferative index 8%.~Final Diagnosis: Left breast excisional biopsy - Invasive ductal carcinoma, well~differentiated (Nottingham grade I), measuring 1.4 cm. Margins negative.~ER/PR positive, HER2 negative.~Electronically signed by Kenji H. Ishikawa, MD on 09/22/2026 11:45||||||F|||20260922114500||PATH-ISHI^Ishikawa^Kenji^H^^^MD||
OBX|2|ED|88305^Surgical Pathology^CPT4|2|^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/4gIcSUNDX1BST0ZJTEUAAQEAAAIMbGNtcwIQAABtbnRyUkdCIFhZWiAH3AABABkAAwApADlhY3NwQVBQTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPbWAAEAAAAA0y1sY21zAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARY3BydAAAAVAAAAAzZGVzYwAAAYQAAABsd3RwdAAAAfAAAAAUYmtwdAAAAgQAAAAUclhZWgAAAhgAAAAUZ1hZWgAAAiwAAAAUYlhZWgAAAkAAAAAUZG1uZAAAAlQAAABwZG1kZAAAAsQAAACIdnVlZAAAA0wAAACGdmlldwAAA9QAAACKZGV2cwAABHAAAAByY3VydgAABMQAAAAjY3VydgAABMQAAAAjY3VydgAABMQAAAAjdmNndAAABOgAAAAwAAEzRDI0LjIuMjkAAAAAAAAAAAAAABFTdXJnaWNhbCBQYXRob2xvZ3kAAAAAAAAAAAD/2wBDAAoHBwgHBgoICAgLCgoLDhgQDg0NDh0VFhEYIx8lJCIfIiEmKzcvJik0KSEiMEExNDk7Pj4+JS5ESUM8SDc9Pjv/2wBDAQoLCw4NDhwQEBw7KCIoOzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozv/wAARCAAQABADASIAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABQQG/8QAIxAAAgEDBAIDAQAAAAAAAAAAAQIDBAURACExQRIiBhNR/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAcEQACAgIDAAAAAAAAAAAAAAABAgARAzEhQaH/2gAMAwEAAhEDEEA/AMJ8WvV1t1ypnip5GhLspkUjGRjg/utPNdy05YhmOckk89nWY+KFfo7iUJIBQ8e+dazUadQ5C5Wl1A8ZNmZmf//Z||||||F|||20260922114400||PATH-ISHI^Ishikawa^Kenji^H^^^MD||
```

---

## 16. ADT^A08 - Insurance update at University Hospitals Parma Medical Center

```
MSH|^~\&|CERNERPM|UH_PARMA|RHAPSODY|UH_INTEGRATION|20260113094817||ADT^A08^ADT_A01|MSG20260113094817016|P|2.5.1|||AL|NE||ASCII|||
EVN|A08|20260113094800|||JKOWALSKI^Kowalski^Jennifer^^^REG||UH_PARMA
PID|1||MRN17293847^^^UH^MR||Abdelrahman^Fatima^Zahra^^Ms.^||19850917|F||2106-3^White^HL70005|5431 Ridge Rd^^Parma^OH^44129^US^H||^PRN^PH^^^440^5558372||ARA^Arabic^HL70296|M^Married^HL70002|||534-82-1739|||N^Not Hispanic^HL70189||||||||||
PV1|1|I|3W^312^01^UH_PARMA^^^^3 West Med/Surg|||2233998877^Lindquist^Robert^A^^^MD^^NPI||||||R|||2233998877^Lindquist^Robert^A^^^MD^^NPI|IN||MEDICAL_MUTUAL|||||||||||||||||||UH_PARMA|A|||20260111083000||||||
IN1|1|MMOH-STD|6630045|Medical Mutual of Ohio|2060 E 9th St^^Cleveland^OH^44115^US|^PRN^PH^^^800^5554321|GRP-OH-55182|||UH||||20260101|20261231|||Abdelrahman^Fatima^Zahra|SEL^Self^HL70063|19850917|5431 Ridge Rd^^Parma^OH^44129^US|||1||||||||||||||MMOH-887342910|||||||F
IN2|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
```

---

## 17. SIU^S12 - Surgical scheduling at Akron Children's Hospital

```
MSH|^~\&|MILLENNIUM|AKRON_CH|MIRTH|AKRON_CH_SCHED|20260504102244||SIU^S12^SIU_S12|MSG20260504102244017|P|2.5.1|||AL|NE||ASCII|||
SCH|APPT-2026050410001^MILLENNIUM|||||MOD^Modifier^HL70277|ROUTINE^Routine^HL70277|SURGERY^Surgical^HL70277|120|MIN^Minutes^HL70277||1199887766^Chowdhury^Anika^R^^^MD^^NPI|^WPN^PH^^^330^5553400||1199887766^Chowdhury^Anika^R^^^MD^^NPI|^WPN^PH^^^330^5553400|||||BOOKED^Booked^HL70278|
PID|1||MRN18374829^^^AKRON_CH^MR||Huang^Emily^Mei^^||20180614|F||2028-9^Asian^HL70005|1842 Merriman Rd^^Akron^OH^44313^US^H||^PRN^PH^^^330^5552918||ENG^English^HL70296|S^Single^HL70002|||||||N^Not Hispanic^HL70189||||||||||
NK1|1|Huang^Wei^Lin^^Mr.||^PRN^PH^^^330^5552918|FTH^Father^HL70063||EC^Emergency Contact^HL70131
NK1|2|Huang^Mei^Hua^^Mrs.||^PRN^PH^^^330^5552919|MTH^Mother^HL70063||EC^Emergency Contact^HL70131
PV1|1|O|SURG^OR3^01^AKRON_CH^^^^Surgery|||1199887766^Chowdhury^Anika^R^^^MD^^NPI||||||R|||1199887766^Chowdhury^Anika^R^^^MD^^NPI|OUT||ANTHEM|||||||||||||||||||AKRON_CH|P|||20260520080000||||||
RGS|1||SURG^Surgery^HL70069
AIS|1||42820^Tonsillectomy and adenoidectomy^CPT4|20260520080000|120|MIN^Minutes^HL70277||120|MIN^Minutes^HL70277|||||
AIG|1||1199887766^Chowdhury^Anika^R^^^MD^^NPI|SURGEON^Surgeon^HL70337|||||20260520080000|120|MIN^Minutes^HL70277||
AIL|1||SURG^OR3^01^AKRON_CH|OR^Operating Room^HL70305||||20260520080000|120|MIN^Minutes^HL70277||
DG1|1||J35.3^Hypertrophy of tonsils with hypertrophy of adenoids^ICD10|||A|||||||||1|
```

---

## 18. MDM^T02 - Operative note from Genesis Healthcare System Zanesville

```
MSH|^~\&|POWERCHART|GENESIS_MC|MIRTH|GENESIS_DOCUMENTS|20260618154023||MDM^T02^MDM_T02|MSG20260618154023018|P|2.5.1|||AL|NE||ASCII|||
EVN|T02|20260618154000|||TRANS_SYS||GENESIS_MC
PID|1||MRN19283746^^^GENESIS^MR||Barnett^Walter^Eugene^^Mr.^||19550127|M||2106-3^White^HL70005|3910 Maple Ave^^Zanesville^OH^43701^US^H||^PRN^PH^^^740^5554827||ENG^English^HL70296|M^Married^HL70002|||312-78-4591|||N^Not Hispanic^HL70189||||||||||
PV1|1|I|SURG^401^01^GENESIS_MC^^^^Surgical|||5566221133^Lockhart^Gregory^P^^^MD^^NPI||||||R|||5566221133^Lockhart^Gregory^P^^^MD^^NPI|IN||MEDICARE|||||||||||||||||||GENESIS_MC|A|||20260618060000||||||
TXA|1|OP^Operative Note^HL70270|TX^Text^HL70191|20260618154000||20260618154000|||||5566221133^Lockhart^Gregory^P^^^MD^^NPI|DOC-20260618-0037^POWERCHART||||||AV^Available^HL70271||||||
OBX|1|TX|OP^Operative Note^HL70270|1|OPERATIVE REPORT~Date of Procedure: 06/18/2026~Patient: Barnett, Walter E. DOB: 01/27/1955 MRN: 19283746~Surgeon: Gregory P. Lockhart, MD~Assistant: None~Anesthesia: General endotracheal~Preoperative Diagnosis: Right inguinal hernia~Postoperative Diagnosis: Right inguinal hernia, direct type~Procedure: Open right inguinal hernia repair with mesh (Lichtenstein technique)~Indications: Mr. Barnett is a 71-year-old male presenting with a symptomatic right~inguinal hernia causing intermittent groin pain and bulging with activity. Conservative~management has failed. Risks, benefits, and alternatives discussed. Informed consent obtained.~Description of Procedure: The patient was brought to the operating room, placed supine,~and general anesthesia was induced. The right groin was prepped and draped in sterile~fashion. An oblique incision was made over the right inguinal canal. Scarpa's fascia was~divided. The external oblique aponeurosis was opened through the external ring. The~ilioinguinal nerve was identified and preserved. The spermatic cord was mobilized. A~direct hernia sac was identified arising from the floor of the inguinal canal. The sac was~reduced and the floor was reconstructed. A 3x5 inch polypropylene mesh was fashioned~and placed over the floor of the inguinal canal, secured with interrupted 2-0 Prolene~sutures to the pubic tubercle, inguinal ligament, and conjoint tendon. A slit was made in~the lateral aspect of the mesh to accommodate the spermatic cord. Hemostasis was~confirmed. The external oblique was closed with 2-0 Vicryl. Skin was closed with~subcuticular 4-0 Monocryl. Steri-Strips and a sterile dressing were applied.~Estimated Blood Loss: Minimal (<10 mL)~Specimens: None~Complications: None~Disposition: The patient tolerated the procedure well and was transferred to the PACU~in stable condition.~Electronically signed by Gregory P. Lockhart, MD on 06/18/2026 15:40||||||F|||20260618154000||SURG-LOCK^Lockhart^Gregory^P^^^MD||
```

---

## 19. DFT^P03 - Professional fee posting from TriHealth Bethesda North Cincinnati

```
MSH|^~\&|MILLENNIUM|TRIHEALTH_BN|MIRTH|TRIHEALTH_BILLING|20260310162918||DFT^P03^DFT_P03|MSG20260310162918019|P|2.5.1|||AL|NE||ASCII|||
EVN|P03|20260310162900|||BILLING_SYS||TRIHEALTH_BN
PID|1||MRN20182934^^^TRIHEALTH^MR||Kessler^Margaret^Rose^^Mrs.^||19680824|F||2106-3^White^HL70005|10234 Montgomery Rd^^Cincinnati^OH^45242^US^H||^PRN^PH^^^513^5556823||ENG^English^HL70296|M^Married^HL70002|||428-73-1892|||N^Not Hispanic^HL70189||||||||||
PV1|1|I|5N^518^01^TRIHEALTH_BN^^^^5 North Ortho|||4433221100^Holcomb^Laura^K^^^MD^^NPI||||||R|||4433221100^Holcomb^Laura^K^^^MD^^NPI|IN||CIGNA|||||||||||||||||||TRIHEALTH_BN|A|||20260308110000||||||
FT1|1|20260309||CG|27447^Total knee arthroplasty, right^CPT4||1|||27447^Total knee arthroplasty^CPT4|||||TRIHEALTH_BN^TriHealth Bethesda North Hospital||||||4433221100^Holcomb^Laura^K^^^MD^^NPI||27447^Total knee arthroplasty^CPT4|M17.11^Primary osteoarthritis, right knee^ICD10|||||||||
FT1|2|20260309||CG|01402^Anesthesia for total knee replacement^CPT4||1|||01402^Anesthesia total knee^CPT4|||||TRIHEALTH_BN^TriHealth Bethesda North Hospital||||||7788441100^Estrada^Daniel^R^^^MD^^NPI||01402^Anesthesia total knee^CPT4|M17.11^Primary osteoarthritis, right knee^ICD10|||||||||
FT1|3|20260310||CG|99232^Subsequent hospital care, moderate complexity^CPT4||1|||99232^Subsequent hospital care^CPT4|||||TRIHEALTH_BN^TriHealth Bethesda North Hospital||||||4433221100^Holcomb^Laura^K^^^MD^^NPI||99232^Subsequent hospital care^CPT4|M17.11^Primary osteoarthritis, right knee^ICD10|||||||||
FT1|4|20260310||CG|97161^Physical therapy evaluation, low complexity^CPT4||1|||97161^PT evaluation^CPT4|||||TRIHEALTH_BN^TriHealth Bethesda North Hospital||||||9911223344^Colvin^Karen^L^^^DPT^^NPI||97161^PT evaluation^CPT4|M17.11^Primary osteoarthritis, right knee^ICD10|||||||||
DG1|1||M17.11^Primary osteoarthritis, right knee^ICD10|||A|||||||||1|
```

---

## 20. ADT^A04 - Emergency registration at Firelands Regional Medical Center Sandusky

```
MSH|^~\&|CERNERPM|FIRELANDS_RMC|MIRTH|FIRELANDS_HIE|20260823193445||ADT^A04^ADT_A01|MSG20260823193445020|P|2.5.1|||AL|NE||ASCII|||
EVN|A04|20260823193300|||AHOLMES^Holmes^Andrea^^^REG||FIRELANDS_RMC
PID|1||MRN21093847^^^FIRELANDS^MR||Dietrich^Carl^David^^Mr.^||19440611|M||2106-3^White^HL70005|1027 Columbus Ave^^Sandusky^OH^44870^US^H||^PRN^PH^^^419^5554192||ENG^English^HL70296|M^Married^HL70002|||198-34-7612|||N^Not Hispanic^HL70189||||||||||
NK1|1|Dietrich^Dorothy^Mae^^Mrs.||^PRN^PH^^^419^5554192|SPO^Spouse^HL70063||EC^Emergency Contact^HL70131
PV1|1|E|ED^ED03^01^FIRELANDS_RMC^^^^Emergency Dept|||8877665544^Callahan^Patrick^M^^^MD^^NPI||||||R|||8877665544^Callahan^Patrick^M^^^MD^^NPI|ER||MEDICARE|||||||||||||||||||FIRELANDS_RMC|A|||20260823193300||||||
PV2|||^Sudden onset left-sided weakness and slurred speech, NIHSS 8, stroke alert activated||||||||||||||||AI|||||||||||||||||||||||||
IN1|1|MCARE-B|5520020|Medicare Part B|7500 Security Blvd^^Baltimore^MD^21244^US||||||||20240101|20261231|||Dietrich^Carl^David|SEL^Self^HL70063|19440611|1027 Columbus Ave^^Sandusky^OH^44870^US|||1||||||||||||||1AB2-CD3-EF45|||||||M
IN1|2|MMOH-SUP|6630046|Medical Mutual of Ohio - Supplement|2060 E 9th St^^Cleveland^OH^44115^US|^PRN^PH^^^800^5554321|GRP-SUP-8821|||FIRELANDS||||20260101|20261231|||Dietrich^Carl^David|SEL^Self^HL70063|19440611|1027 Columbus Ave^^Sandusky^OH^44870^US|||2||||||||||||||MMOH-SUP-443219|||||||M
DG1|1||I63.9^Cerebral infarction, unspecified^ICD10|||A|||||||||1|
DG1|2||R47.1^Dysarthria and anarthria^ICD10|||A|||||||||2|
DG1|3||G81.90^Hemiplegia, unspecified affecting unspecified side^ICD10|||A|||||||||3|
```
