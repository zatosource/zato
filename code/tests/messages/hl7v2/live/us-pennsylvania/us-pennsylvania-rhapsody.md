# Rhapsody Integration Engine - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission at UPMC Presbyterian

```
MSH|^~\&|RHAPSODY|UPMC_PRESBYTERIAN|EPIC|UPMC_HIE|20260314082345||ADT^A01^ADT_A01|MSG20260314082345001|P|2.5.1|||AL|NE||ASCII
EVN|A01|20260314082300|||tbarlow^Barlow^Terrence^A^^MD|20260314082300
PID|1||MRN0048271^^^UPMC^MR~531-18-7642^^^SSA^SS||Wojcik^Donna^Elaine^^Mrs.^||19580923|F||2106-3^White^HL70005|4521 Walnut St^^Pittsburgh^PA^15213^US^H||^PRN^PH^^^412^6815523~^NET^Internet^^donna.wojcik@email.com|^WPN^PH^^^412^3924500|||M|||531-18-7642
PD1|||UPMC Internal Medicine^^12830001|4456781^Kapoor^Nikhil^S^^MD
NK1|1|Wojcik^Stanley^R|SPO^Spouse^HL70063|4521 Walnut St^^Pittsburgh^PA^15213^US|^PRN^PH^^^412^6815524||EC
PV1|1|I|4W^4102^01^UPMC_PRES^^^N||||1234567^Okonkwo^Chidi^N^^MD^^^NPI|9876543^Fitzgerald^Claire^M^^MD^^^NPI|CAR||||7|||1234567^Okonkwo^Chidi^N^^MD^^^NPI|IN||BCBS|||||||||||||||AI|||20260314082300
PV2|||^Acute exacerbation of congestive heart failure|||||||2|||||||||N
DG1|1|I10|I50.21^Acute systolic (congestive) heart failure^ICD10||20260314|A
IN1|1|BCBS001|BCBS OF PA|Independence Blue Cross^^PO Box 41247^^Philadelphia^PA^19101|||||GRP9928374||UPMC Faculty Practice|20250101|20261231|||Wojcik^Donna^E|Self|19580923|4521 Walnut St^^Pittsburgh^PA^15213|||1||||||||||||||XAZ928374651
GT1|1||Wojcik^Donna^Elaine||4521 Walnut St^^Pittsburgh^PA^15213^US|^PRN^PH^^^412^6815523|||||SE
AL1|1|DA|PENICILLIN^Penicillin^|SV|Anaphylaxis|20100315
```

---

## 2. ORU^R01 - Lab results from Geisinger Medical Center

```
MSH|^~\&|SUNQUEST|GEISINGER_MC|RHAPSODY|GEISINGER_HIE|20260315141022||ORU^R01^ORU_R01|LAB20260315141022889|P|2.5.1|||AL|NE||ASCII
PID|1||GMC0092817^^^GEISINGER^MR||Jankowski^Peter^Adam||19720411|M||2106-3^White^HL70005|891 Market St^^Danville^PA^17821^US^H||^PRN^PH^^^570^2754891|||M|||284-41-3309
PV1|1|O|LABDRW^001^01||||7712345^Castellano^Linda^R^^MD^^^NPI||||||||||OP|||||||||||||||||||||||||20260315140000
ORC|RE|ORD993847|LAB993847^SUNQUEST||CM||||20260315133000|^SYSTEM||7712345^Castellano^Linda^R^^MD^^^NPI|GEISINGER_MC||||GEISINGER MEDICAL CENTER^100 N ACADEMY AVE^^DANVILLE^PA^17822|^WPN^PH^^^570^2716211
OBR|1|ORD993847|LAB993847^SUNQUEST|24323-8^Comprehensive metabolic panel^LN|||20260315133000|||||||||7712345^Castellano^Linda^R^^MD^^^NPI||||||20260315140500||CH|F
OBX|1|NM|2345-7^Glucose^LN||112|mg/dL|70-100|H|||F|||20260315140000||AUTO^Automated System
OBX|2|NM|3094-0^Urea nitrogen^LN||18|mg/dL|7-20|N|||F|||20260315140000||AUTO^Automated System
OBX|3|NM|2160-0^Creatinine^LN||1.1|mg/dL|0.7-1.3|N|||F|||20260315140000||AUTO^Automated System
OBX|4|NM|17861-6^Calcium^LN||9.4|mg/dL|8.5-10.5|N|||F|||20260315140000||AUTO^Automated System
OBX|5|NM|2951-2^Sodium^LN||141|mmol/L|136-145|N|||F|||20260315140000||AUTO^Automated System
OBX|6|NM|2823-3^Potassium^LN||4.2|mmol/L|3.5-5.1|N|||F|||20260315140000||AUTO^Automated System
OBX|7|NM|2075-0^Chloride^LN||103|mmol/L|98-106|N|||F|||20260315140000||AUTO^Automated System
OBX|8|NM|2028-9^CO2^LN||24|mmol/L|21-32|N|||F|||20260315140000||AUTO^Automated System
OBX|9|NM|1751-7^Albumin^LN||4.1|g/dL|3.5-5.0|N|||F|||20260315140000||AUTO^Automated System
OBX|10|NM|1975-2^Total Bilirubin^LN||0.8|mg/dL|0.1-1.2|N|||F|||20260315140000||AUTO^Automated System
OBX|11|NM|6768-6^Alkaline Phosphatase^LN||72|U/L|44-147|N|||F|||20260315140000||AUTO^Automated System
OBX|12|NM|1742-6^ALT^LN||28|U/L|7-56|N|||F|||20260315140000||AUTO^Automated System
OBX|13|NM|1920-8^AST^LN||31|U/L|10-40|N|||F|||20260315140000||AUTO^Automated System
```

---

## 3. ORM^O01 - Radiology order from Penn Medicine Lancaster General

```
MSH|^~\&|RHAP_ENGINE|LANCASTER_GEN|PACS_RIS|LGH_RAD|20260316093015||ORM^O01^ORM_O01|ORD20260316093015442|P|2.4|||AL|NE
PID|1||LGH2038471^^^LGHP^MR||Stoltzfus^Ruth^Marie||19651204|F||2106-3^White^HL70005|2847 Columbia Ave^^Lancaster^PA^17603^US^H||^PRN^PH^^^717^3928411|||W|||195-52-3841
PV1|1|O|RADOP^RAD1^01||||3345678^Brennan^Michael^J^^MD^^^NPI||||||||||OP|||||||||||||||||||||||||20260316090000
ORC|NW|RAD28374|RAD28374^RIS||SC||||20260316090000|^clerk01||3345678^Brennan^Michael^J^^MD^^^NPI|LGH_RAD||||LANCASTER GENERAL HOSPITAL^555 N DUKE ST^^LANCASTER^PA^17602|^WPN^PH^^^717^5447211||RAD28374
OBR|1|RAD28374|RAD28374^RIS|71260^CT CHEST WITH CONTRAST^CPT4|||20260316100000||||N|||||3345678^Brennan^Michael^J^^MD^^^NPI|||||||CT|||1^^^20260316100000^^R||||||^Persistent cough and weight loss. Rule out pulmonary mass.
DG1|1|I10|R05.9^Cough, unspecified^ICD10||20260316|W
```

---

## 4. ADT^A08 - Patient information update at Lehigh Valley Health Network

```
MSH|^~\&|RHAPSODY|LVHN_MUHLENBERG|CERNER|LVHN_CDR|20260317110530||ADT^A08^ADT_A01|UPD20260317110530776|P|2.5.1|||AL|NE||ASCII
EVN|A08|20260317110530|||mgriffin^Griffin^Megan
PID|1||LVHN00571839^^^LVHN^MR||Tran^Huy^Duc||19880716|M||2028-9^Asian^HL70005|1245 Hamilton Blvd^^Allentown^PA^18101^US^H||^PRN^PH^^^610^4329871~^NET^Internet^^huy.tran@protonmail.com|^WPN^PH^^^610^7785500|||S|||221-64-9078
PD1|||LVHN Family Medicine Muhlenberg^^44820003|6678901^DiAngelo^Maria^L^^MD
NK1|1|Tran^Lan^T|MTH^Mother^HL70063|3872 Tilghman St^^Allentown^PA^18104^US|^PRN^PH^^^610^4351192||EC
PV1|1|O|FMP^201^01^LVHN_MUH|||||||||||||||OP|||||||||||||||||||||||||20260317110000
IN1|1|AET001|AETNA|Aetna Better Health^^PO Box 14079^^Lexington^KY^40512|||||GRP4421987||LEHIGH UNIVERSITY|20250901|20261231|||Tran^Huy^D|Self|19880716|1245 Hamilton Blvd^^Allentown^PA^18101|||1||||||||||||||WPA4421987003
```

---

## 5. ORU^R01 - Pathology report with embedded PDF from Penn State Hershey

```
MSH|^~\&|COPATH|PSH_PATHOLOGY|RHAPSODY|PSH_RESULTS|20260318153200||ORU^R01^ORU_R01|PATH20260318153200112|P|2.5.1|||AL|NE||ASCII
PID|1||PSHMC0283746^^^PSHMC^MR||Reyes^Gabriela^Sofia||19710328|F||2131-1^Hispanic^HL70005|567 Chocolate Ave^^Hershey^PA^17033^US^H||^PRN^PH^^^717^5330192|||M|||164-87-2301
PV1|1|I|5N^5212^01^PSH_HMC|||||||||||||||IP|||||||||||||||||||||||||20260316
ORC|RE|SURG88412|PATH88412^COPATH||CM||||20260318150000|||8823456^Hartman^Douglas^R^^MD^^^NPI|PSH_PATHOLOGY||||PENN STATE HERSHEY MEDICAL CENTER^500 UNIVERSITY DR^^HERSHEY^PA^17033|^WPN^PH^^^717^5316211
OBR|1|SURG88412|PATH88412^COPATH|88305^Surgical pathology^CPT4|||20260316120000|||||||||8823456^Hartman^Douglas^R^^MD^^^NPI||||||20260318150000||SP|F
OBX|1|FT|22634-0^Pathology report^LN||GROSS DESCRIPTION:\.br\Received fresh labeled "left breast, 12 o'clock" is an oriented lumpectomy specimen measuring 5.2 x 4.1 x 3.8 cm. The specimen is inked: superior blue, inferior black, medial red, lateral green. Serial sectioning reveals a firm, tan-white mass measuring 1.8 x 1.5 x 1.3 cm.\.br\\.br\MICROSCOPIC DESCRIPTION:\.br\Sections show invasive ductal carcinoma, Nottingham grade 2 (tubule score 3, nuclear grade 2, mitotic rate score 1). Margins are negative with closest margin (inferior) at 0.4 cm. No lymphovascular invasion identified.\.br\\.br\DIAGNOSIS:\.br\Left breast, 12 o'clock, lumpectomy:\.br\- Invasive ductal carcinoma, Nottingham grade 2, 1.8 cm\.br\- Margins negative (closest inferior at 0.4 cm)\.br\- No lymphovascular invasion||||||F|||20260318150000||8823456^Hartman^Douglas^R
OBX|2|ED|PDF^Pathology Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKFBhdGhvbG9neSBSZXBvcnQgLSBQZW5uIFN0YXRlIEhlcnNoZXkpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMxNCAwMDAwMCBuIAowMDAwMDAwNDA4IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNDkxCiUlRU9G||||||F|||20260318150000||8823456^Hartman^Douglas^R
```

---

## 6. SIU^S12 - Appointment scheduling at WellSpan York Hospital

```
MSH|^~\&|RHAPSODY|WELLSPAN_SCHED|ALLSCRIPTS|WELLSPAN_EHR|20260319084512||SIU^S12^SIU_S12|SCH20260319084512334|P|2.5|||AL|NE
SCH|APT992847|APT992847|||||ROUTINE^Routine^HL70276|FOLLOWUP^Follow-Up Visit^HL70277|30|MIN|^^30^20260326140000^20260326143000|5543210^Mehta^Arvind^P^^MD^^^NPI|^WPN^PH^^^717^8512100|CARDIOLOGY^225 S GEORGE ST^^YORK^PA^17401|jdoe@wellspan.org|5543210^Mehta^Arvind^P^^MD
PID|1||WS0847261^^^WELLSPAN^MR||Keenan^James^Bernard||19550812|M||2106-3^White^HL70005|1423 E Market St^^York^PA^17403^US^H||^PRN^PH^^^717^8431927|||M|||338-74-2209
PV1|1|O|CARD^C201^01^WS_YORK||||5543210^Mehta^Arvind^P^^MD^^^NPI||||||||||OP
RGS|1|A
AIS|1|A|99214^OFFICE VISIT LEVEL 4^CPT4|20260326140000|||30|MIN
AIG|1|A|5543210^Mehta^Arvind^P^^MD|CARDIOLOGY
AIL|1|A|CARDIOLOGY^225 S GEORGE ST^^YORK^PA^17401||20260326140000
```

---

## 7. MDM^T02 - Transcription document from Reading Hospital Tower Health

```
MSH|^~\&|MMODAL|READING_HOSP|RHAP_ENGINE|TH_CDR|20260320162845||MDM^T02^MDM_T02|DOC20260320162845991|P|2.5.1|||AL|NE||ASCII
EVN|T02|20260320162845
PID|1||RH00394821^^^TOWER^MR||Scarpelli^Dorothy^Mae||19490506|F||2106-3^White^HL70005|3892 Penn Ave^^West Reading^PA^19611^US^H||^PRN^PH^^^610^3721845|||W|||126-41-8820
PV1|1|I|3E^3214^01^READING_HOSP||||2234567^Okafor^Emeka^C^^MD^^^NPI||||||||||IP|||||||||||||||||||||||||20260318
TXA|1|HP^History and Physical^HL70270|TX^Text^HL70191|20260318||2234567^Okafor^Emeka^C^^MD^^^NPI|20260320162000||2234567^Okafor^Emeka^C^^MD^^^NPI|||DOC88234^MMODAL|||||AU||AV
OBX|1|FT|11488-4^Consultation Note^LN|1|HISTORY AND PHYSICAL\.br\\.br\PATIENT: Dorothy Mae Scarpelli\.br\DOB: 05/06/1949\.br\DATE OF ADMISSION: 03/18/2026\.br\ATTENDING: Emeka C. Okafor, MD\.br\\.br\CHIEF COMPLAINT: Increasing shortness of breath and bilateral lower extremity edema.\.br\\.br\HISTORY OF PRESENT ILLNESS:\.br\This is a 76-year-old female with a history of diastolic heart failure, hypertension, type 2 diabetes mellitus, and chronic kidney disease stage 3b who presents with a 5-day history of worsening dyspnea on exertion and lower extremity swelling. She reports sleeping on 3 pillows. She denies chest pain, palpitations, or syncope. She admits to dietary indiscretion over the past week.\.br\\.br\MEDICATIONS:\.br\1. Furosemide 40 mg daily\.br\2. Lisinopril 20 mg daily\.br\3. Metformin 1000 mg twice daily\.br\4. Amlodipine 10 mg daily\.br\5. Atorvastatin 40 mg at bedtime\.br\\.br\PHYSICAL EXAMINATION:\.br\Vitals: T 98.2, HR 88, BP 158/92, RR 22, SpO2 93% on RA\.br\General: Alert, mild respiratory distress at rest\.br\Lungs: Bibasilar crackles, no wheezing\.br\Heart: RRR, 2/6 systolic murmur at apex\.br\Extremities: 3+ pitting edema bilateral lower extremities to mid-shin\.br\\.br\ASSESSMENT AND PLAN:\.br\1. Acute on chronic diastolic heart failure exacerbation - IV furosemide, strict I&O, daily weights\.br\2. Hypertension - continue current regimen, add hydralazine PRN\.br\3. CKD stage 3b - monitor BMP daily\.br\4. Type 2 DM - hold metformin, sliding scale insulin||||||F
```

---

## 8. ACK - Acknowledgment from Abington Jefferson Health

```
MSH|^~\&|RHAPSODY|ABINGTON_JH|EPIC|AJH_PROD|20260320163001||ACK^A01^ACK|ACK20260320163001445|P|2.5.1|||AL|NE
MSA|AA|MSG20260320162958332|Message accepted and processed successfully
```

---

## 9. ADT^A04 - Patient registration at St. Luke's University Health Network

```
MSH|^~\&|RHAPSODY|STLUKES_BETH|MEDITECH|SLHN_CDR|20260321071845||ADT^A04^ADT_A01|REG20260321071845223|P|2.5.1|||AL|NE||ASCII
EVN|A04|20260321071800|||SYSTEM
PID|1||SL00283947^^^SLHN^MR||Fuentes^Miguel^Ernesto||19830219|M||2131-1^Hispanic^HL70005|2918 Easton Ave^^Bethlehem^PA^18017^US^H||^PRN^PH^^^484^8921035~^NET^Internet^^m.fuentes84@gmail.com|^WPN^PH^^^484^3265000|||M|||284-11-4490
PD1|||St Lukes Primary Care Bethlehem^^77120003|9923456^Hwang^Jennifer^S^^MD
PV1|1|O|ED^BED12^01^SLUH_BETH^^^N||||8834567^Gallagher^Robert^E^^MD^^^NPI||||||||||ER||||||||||||||||||ED||||20260321071800
PV2|||^Laceration right forearm
DG1|1|I10|S51.811A^Laceration without foreign body of right forearm, initial encounter^ICD10||20260321|A
IN1|1|HGP001|HIGHMARK|Highmark Blue Shield^^PO Box 890089^^Camp Hill^PA^17089|||||GRP7829341||SELF|20260101|20261231|||Fuentes^Miguel^E|Self|19830219|2918 Easton Ave^^Bethlehem^PA^18017|||1||||||||||||||EBH7829341002
```

---

## 10. ORU^R01 - Microbiology results from Allegheny General Hospital

```
MSH|^~\&|SOFTMIC|AGH_MICRO|RHAPSODY|AHN_RESULTS|20260321142230||ORU^R01^ORU_R01|MIC20260321142230667|P|2.5.1|||AL|NE||ASCII
PID|1||AGH0192837^^^AHN^MR||Jefferson^Karen^Monique||19670814|F||2054-5^Black or African American^HL70005|714 Federal St^^Pittsburgh^PA^15212^US^H||^PRN^PH^^^412^2317445|||D|||195-20-7843
PV1|1|I|6S^6412^01^AGH||||7745678^Abrams^Tyrone^D^^MD^^^NPI||||||||||IP|||||||||||||||||||||||||20260319
ORC|RE|MIC77234|MIC77234^SOFTMIC||CM||||20260321140000|||7745678^Abrams^Tyrone^D^^MD^^^NPI|AGH_MICRO||||ALLEGHENY GENERAL HOSPITAL^320 E NORTH AVE^^PITTSBURGH^PA^15212|^WPN^PH^^^412^3596000
OBR|1|MIC77234|MIC77234^SOFTMIC|87040^Blood Culture^CPT4|||20260319180000|||||||||7745678^Abrams^Tyrone^D^^MD^^^NPI||||||20260321140000||MB|F
OBX|1|CWE|600-7^Bacteria identified^LN||MRSA^Methicillin-resistant Staphylococcus aureus^L||||||F|||20260321100000
OBX|2|ST|29576-6^Bacterial susceptibility panel^LN||See detailed results below||||||F|||20260321120000
OBX|3|ST|18907-2^Vancomycin MIC^LN||1|ug/mL|<=2|S|||F|||20260321120000
OBX|4|ST|18993-2^Daptomycin MIC^LN||0.5|ug/mL|<=1|S|||F|||20260321120000
OBX|5|ST|18943-7^Linezolid MIC^LN||2|ug/mL|<=4|S|||F|||20260321120000
OBX|6|ST|18996-5^Trimethoprim-Sulfamethoxazole MIC^LN||<=0.5/9.5|ug/mL|<=2/38|S|||F|||20260321120000
OBX|7|ST|18878-5^Clindamycin MIC^LN||>2|ug/mL|<=0.5|R|||F|||20260321120000
OBX|8|ST|18919-7^Erythromycin MIC^LN||>4|ug/mL|<=0.5|R|||F|||20260321120000
OBX|9|ST|18961-9^Oxacillin MIC^LN||>2|ug/mL|<=2|R|||F|||20260321120000
```

---

## 11. ORM^O01 - Medication order from Crozer-Chester Medical Center

```
MSH|^~\&|RHAP_ENGINE|CROZER_PHARM|PYXIS|CROZER_MED|20260322081530||ORM^O01^ORM_O01|RX20260322081530887|P|2.4|||AL|NE
PID|1||CC0041928^^^CROZER^MR||Washington^Harold^Eugene||19440327|M||2054-5^Black or African American^HL70005|482 Providence Rd^^Media^PA^19063^US^H||^PRN^PH^^^610^5441823|||W|||131-75-5518
PV1|1|I|ICU^ICU04^01^CCMC||||6623456^Venkatesh^Anish^K^^MD^^^NPI||||||||||IP|||||||||||||||||||||||||20260321
ORC|NW|RX448821|RX448821^PHARM||SC||||20260322080000|pharm01||6623456^Venkatesh^Anish^K^^MD^^^NPI|CCMC_ICU||||CROZER-CHESTER MEDICAL CENTER^1 MEDICAL CENTER BLVD^^UPLAND^PA^19013|^WPN^PH^^^610^4472000
OBR|1|RX448821|RX448821^PHARM|PHARMACY^Pharmacy Order^L|||20260322080000|||||||||6623456^Venkatesh^Anish^K^^MD^^^NPI
RXO|312961^Vancomycin 1000 mg IV^NDC|1000|mg||IV^Intravenous^HL70162||^every 12 hours||N||||VANCOMYCIN 1 GM/200 ML NS
RXR|IV^Intravenous^HL70162|LA^Left Arm^HL70163
```

---

## 12. ADT^A01 - Admission at Main Line Health Bryn Mawr Hospital

```
MSH|^~\&|RHAPSODY|BRYN_MAWR_HOSP|EPIC|MLH_CDR|20260322134500||ADT^A01^ADT_A01|ADM20260322134500112|P|2.5.1|||AL|NE||ASCII
EVN|A01|20260322134500|||plynch^Lynch^Patricia|20260322134000
PID|1||MLH0087234^^^MLH^MR~440-26-1184^^^SSA^SS||Callahan^Siobhan^Marie^^Ms.^||19790515|F||2106-3^White^HL70005|847 Montgomery Ave^^Bryn Mawr^PA^19010^US^H||^PRN^PH^^^610^5271934~^NET^Internet^^scallahan79@outlook.com|^WPN^PH^^^610^5263200|||M|||440-26-1184
PD1|||Bryn Mawr Family Practice^^88240001|3312345^Bhandari^Priya^R^^MD
NK1|1|Callahan^Declan^P|SPO^Spouse^HL70063|847 Montgomery Ave^^Bryn Mawr^PA^19010^US|^PRN^PH^^^610^5271935||EC
NK1|2|Callahan^Bridget^A|MTH^Mother^HL70063|221 Haverford Rd^^Wynnewood^PA^19096^US|^PRN^PH^^^610^6421877||EC
PV1|1|I|3W^3108^01^BMH^^^N||||4456789^Yoon^David^S^^MD^^^NPI|5567890^Grasso^Elizabeth^R^^MD^^^NPI|ORT||||2|||4456789^Yoon^David^S^^MD^^^NPI|IN||AETNA|||||||||||||||AI|||20260322134000
PV2|||^Right knee total arthroplasty
DG1|1|I10|M17.11^Primary osteoarthritis, right knee^ICD10||20260322|A
IN1|1|AET002|AETNA|Aetna Health Inc^^PO Box 14079^^Lexington^KY^40512|||||GRP5512847||MLH EMPLOYEE PLAN|20250101|20261231|||Callahan^Siobhan^M|Self|19790515|847 Montgomery Ave^^Bryn Mawr^PA^19010|||1||||||||||||||AET5512847901
GT1|1||Callahan^Siobhan^Marie||847 Montgomery Ave^^Bryn Mawr^PA^19010^US|^PRN^PH^^^610^5271934|||||SE
AL1|1|DA|SULFA^Sulfonamides^|MO|Rash|20050212
AL1|2|DA|CODEINE^Codeine^|SV|Nausea/Vomiting|20120918
```

---

## 13. ORU^R01 - Cardiology report with embedded waveform from Temple University Hospital

```
MSH|^~\&|MUSE|TEMPLE_CARDIO|RHAPSODY|TUH_CDR|20260323091200||ORU^R01^ORU_R01|ECG20260323091200443|P|2.5.1|||AL|NE||ASCII
PID|1||TUH0293847^^^TEMPLE^MR||Banks^Marcus^Darnell||19580101|M||2054-5^Black or African American^HL70005|3419 N Broad St^^Philadelphia^PA^19140^US^H||^PRN^PH^^^215^2271934|||S|||209-52-8831
PV1|1|I|CCU^CCU08^01^TUH||||2278901^Holloway^Denise^L^^MD^^^NPI||||||||||IP|||||||||||||||||||||||||20260322
ORC|RE|ECG99281|ECG99281^MUSE||CM||||20260323090000|||2278901^Holloway^Denise^L^^MD^^^NPI|TEMPLE_CARDIO||||TEMPLE UNIVERSITY HOSPITAL^3401 N BROAD ST^^PHILADELPHIA^PA^19140|^WPN^PH^^^215^7072000
OBR|1|ECG99281|ECG99281^MUSE|93000^Electrocardiogram^CPT4|||20260323085500|||||||||2278901^Holloway^Denise^L^^MD^^^NPI||||||20260323090500||CAR|F
OBX|1|FT|8601-7^EKG impression^LN||Sinus rhythm at 72 bpm. PR interval 184ms. QRS duration 92ms. QTc 448ms. ST depression in leads V4-V6, I, aVL consistent with lateral ischemia. No acute ST elevation. Left ventricular hypertrophy by voltage criteria.||||||F|||20260323090000||2278901^Holloway^Denise^L
OBX|2|NM|8867-4^Heart rate^LN||72|bpm|60-100|N|||F|||20260323090000
OBX|3|NM|8625-6^PR interval^LN||184|ms|120-200|N|||F|||20260323090000
OBX|4|NM|8633-0^QRS duration^LN||92|ms|<120|N|||F|||20260323090000
OBX|5|NM|8636-3^QTc interval^LN||448|ms|<450|N|||F|||20260323090000
OBX|6|ED|WAVEFORM^EKG Waveform Data^L||^application^octet-stream^Base64^UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAB4nGNgGAWjYBSMglEwCkYBNQAATsAAAdTUxMTQ0MDAYG5mbmhkZGJuYGxsamxkYmBgYGBuYW5oYGRkYG5haGBsam5sYGJoYmRgbG5saGhobGJiYG5kYGRgbGBsYG5gYGBubGRoZGhkaGJkYmhkYmhoaGhqYmxiYmxoamhgYmhmaGZkZmBkYGJoZmhiYGRqZmxiaGhkZGBobGZgYGRkYGRkZmhqamJkaGhkZGBqaGRgbGxkYGhkaGhoaGBiYGxoamJqYGpsYGRkamhkaGxkYG5oZmhuZGBsbmBiYmhkYGhgYmBoaGBoYGJkYmhkaG5iaGJoZGJibGJsamRgbGBiYGZoZmRsZGhoYmxiYmxkbGRuZGBsYGBkYmhiaGJiYmpkYmRsYmBsZGJsYGJoZmxoamhqYGhgZGhkamxkaGRmYGZgZmhoaGxsYGJqZmxqamxqampkamRoZGxoaGRiYGJqYmxoamJoYGBoZGxoamhoaGhkYGBmaGRoZGxkYWBhYGJoZGhkamBsYGJiZmhoamhoaGBiaGRiaGhoaGJkYmRqYGZoaGRkYGxgZGBoZGRkaGZgYGBmZGRoZGBkYmBkYGJoYmhiaGRkaGhqampoZGRiYGBkYGBkaGJoZmRoZGhkaGJoZGBoZGBkYGRgZmBkaGRqaGZoYmhkaGRkYGRoZGJgZGJkYGpkZmhkaGRkYGRkZGBkYGRiYGBkaGRoZGhmaGhoZGhoZGhmaGRkYGRoaGhmZGZoZGhkYGhkZGRiYGBiZGJkYGhkaA==||||||F|||20260323090000||MUSE_SYSTEM
```

---

## 14. ADT^A08 - Insurance update at Chambersburg Hospital WellSpan

```
MSH|^~\&|RHAPSODY|WELLSPAN_CHAMB|MEDITECH|WS_FINREG|20260323143000||ADT^A08^ADT_A01|UPD20260323143000556|P|2.5.1|||AL|NE||ASCII
EVN|A08|20260323143000|||kwerner^Werner^Kyle
PID|1||WSC0012847^^^WELLSPAN^MR||Hershberger^Donald^Ray||19610418|M||2106-3^White^HL70005|6234 Lincoln Way E^^Chambersburg^PA^17202^US^H||^PRN^PH^^^717^2631892|||M|||180-41-9918
PV1|1|O|MED^102^01^WS_CHAMB||||3345612^Coughlin^Steven^W^^MD^^^NPI||||||||||OP|||||||||||||||||||||||||20260323140000
IN1|1|CGN001|CIGNA|Cigna Healthcare^^PO Box 188045^^Chattanooga^TN^37422|||||GRP3348921||HERSHBERGER ROOFING INC|20260101|20261231|||Hershberger^Donald^R|Self|19610418|6234 Lincoln Way E^^Chambersburg^PA^17202|||1||||||||||||||CGN3348921774
IN2|1||||||||||||||||||||||||||||||||||||||||||||Hershberger^Sandra^J|SPO
```

---

## 15. ORM^O01 - Lab order from UPMC Hamot Erie

```
MSH|^~\&|RHAP_ENGINE|UPMC_HAMOT|SUNQUEST|HAMOT_LAB|20260324061500||ORM^O01^ORM_O01|ORD20260324061500773|P|2.4|||AL|NE
PID|1||HAM0182736^^^UPMC^MR||Perez^Elena^Cristina||19910623|F||2131-1^Hispanic^HL70005|1847 Peach St^^Erie^PA^16502^US^H||^PRN^PH^^^814^4531902|||S|||295-74-4418
PV1|1|I|4N^4208^01^HAMOT||||9912345^Donnelly^Patrick^J^^MD^^^NPI||||||||||IP|||||||||||||||||||||||||20260323
ORC|NW|LAB84729|LAB84729^SUNQUEST||SC||||20260324060000|^nurse01||9912345^Donnelly^Patrick^J^^MD^^^NPI|HAMOT_LAB||||UPMC HAMOT^201 STATE ST^^ERIE^PA^16550|^WPN^PH^^^814^8776000
OBR|1|LAB84729|LAB84729^SUNQUEST|80053^Comprehensive Metabolic Panel^CPT4|||20260324063000||||N|||||9912345^Donnelly^Patrick^J^^MD^^^NPI
OBR|2|LAB84729|LAB84730^SUNQUEST|85025^CBC with Differential^CPT4|||20260324063000||||N|||||9912345^Donnelly^Patrick^J^^MD^^^NPI
OBR|3|LAB84729|LAB84731^SUNQUEST|82746^Folic Acid Level^CPT4|||20260324063000||||N|||||9912345^Donnelly^Patrick^J^^MD^^^NPI
```

---

## 16. SIU^S12 - Scheduling notification from Einstein Medical Center Philadelphia

```
MSH|^~\&|RHAPSODY|EINSTEIN_SCHED|CERNER|EMC_PHILA|20260324111500||SIU^S12^SIU_S12|SCH20260324111500891|P|2.5|||AL|NE
SCH|APT1128374|APT1128374|||||ROUTINE^Routine^HL70276|NEW^New Patient Visit^HL70277|45|MIN|^^45^20260401093000^20260401101500|8823411^Nwosu^Michelle^T^^MD^^^NPI|^WPN^PH^^^215^4563200|NEURO^5501 OLD YORK RD^^PHILADELPHIA^PA^19141|sched@einstein.edu|8823411^Nwosu^Michelle^T^^MD
PID|1||EMC0394721^^^EINSTEIN^MR||Bhatt^Fatima^Zahra||19950308|F||2029-7^Asian Indian^HL70005|4521 Rising Sun Ave^^Philadelphia^PA^19140^US^H||^PRN^PH^^^215^3291847|||S|||442-19-8897
PV1|1|O|NEURO^N102^01^EMC_PHIL||||8823411^Nwosu^Michelle^T^^MD^^^NPI||||||||||OP
RGS|1|A
AIS|1|A|99203^NEW PATIENT OFFICE VISIT LVL 3^CPT4|20260401093000|||45|MIN
AIG|1|A|8823411^Nwosu^Michelle^T^^MD|NEUROLOGY
AIL|1|A|NEURO^5501 OLD YORK RD^^PHILADELPHIA^PA^19141||20260401093000
```

---

## 17. ORU^R01 - Drug screen results from Excela Health Westmoreland Hospital

```
MSH|^~\&|TOXLAB|EXCELA_WH|RHAPSODY|EXCELA_CDR|20260325080045||ORU^R01^ORU_R01|TOX20260325080045221|P|2.5.1|||AL|NE||ASCII
PID|1||EXC0028374^^^EXCELA^MR||Mazurek^Steven^Anthony||19870912|M||2106-3^White^HL70005|529 Main St^^Greensburg^PA^15601^US^H||^PRN^PH^^^724^8321456|||S|||220-85-1137
PV1|1|E|ED^BED07^01^WH||||4423456^Giordano^Timothy^F^^MD^^^NPI||||||||||ER|||||||||||||||||||||||||20260325020000
ORC|RE|TOX44821|TOX44821^TOXLAB||CM||||20260325074500|||4423456^Giordano^Timothy^F^^MD^^^NPI|EXCELA_WH||||EXCELA HEALTH WESTMORELAND HOSPITAL^532 W PITTSBURGH ST^^GREENSBURG^PA^15601|^WPN^PH^^^724^8327000
OBR|1|TOX44821|TOX44821^TOXLAB|80307^Drug screen panel^CPT4|||20260325030000|||||||||4423456^Giordano^Timothy^F^^MD^^^NPI||||||20260325074500||TOX|F
OBX|1|CWE|3397-7^Amphetamines Urine Screen^LN||260385009^Negative^SCT||Negative|N|||F|||20260325070000
OBX|2|CWE|3398-5^Barbiturates Urine Screen^LN||260385009^Negative^SCT||Negative|N|||F|||20260325070000
OBX|3|CWE|3399-3^Benzodiazepines Urine Screen^LN||10828004^Positive^SCT||Negative|A|||F|||20260325070000
OBX|4|CWE|19659-2^Cocaine Urine Screen^LN||260385009^Negative^SCT||Negative|N|||F|||20260325070000
OBX|5|CWE|3879-4^Opiates Urine Screen^LN||10828004^Positive^SCT||Negative|A|||F|||20260325070000
OBX|6|CWE|18282-4^Cannabis Urine Screen^LN||10828004^Positive^SCT||Negative|A|||F|||20260325070000
OBX|7|CWE|19668-3^Phencyclidine Urine Screen^LN||260385009^Negative^SCT||Negative|N|||F|||20260325070000
OBX|8|CWE|19550-3^Methadone Urine Screen^LN||260385009^Negative^SCT||Negative|N|||F|||20260325070000
```

---

## 18. MDM^T02 - Operative note from Geisinger Wyoming Valley

```
MSH|^~\&|DRAGON|GWV_SURG|RHAP_ENGINE|GEISINGER_CDR|20260325163000||MDM^T02^MDM_T02|DOC20260325163000887|P|2.5.1|||AL|NE||ASCII
EVN|T02|20260325163000
PID|1||GWV0184729^^^GEISINGER^MR||Moyer^Robert^Allen||19570722|M||2106-3^White^HL70005|218 Wyoming Ave^^Kingston^PA^18704^US^H||^PRN^PH^^^570^2881934|||M|||164-30-8844
PV1|1|I|OR^OR03^01^GWV||||5534567^Xiong^Wei^Ming^^MD^^^NPI||||||||||IP|||||||||||||||||||||||||20260325
TXA|1|OP^Operative Note^HL70270|TX^Text^HL70191|20260325||5534567^Xiong^Wei^Ming^^MD^^^NPI|20260325160000||5534567^Xiong^Wei^Ming^^MD^^^NPI|||DOC99281^DRAGON|||||AU||AV
OBX|1|FT|28570-0^Procedure Note^LN|1|OPERATIVE REPORT\.br\\.br\PATIENT: Robert Allen Moyer\.br\MRN: GWV0184729\.br\DATE OF PROCEDURE: 03/25/2026\.br\SURGEON: Wei Ming Xiong, MD\.br\ASSISTANT: Jennifer Walsh, PA-C\.br\ANESTHESIA: General endotracheal\.br\\.br\PREOPERATIVE DIAGNOSIS: Right inguinal hernia\.br\POSTOPERATIVE DIAGNOSIS: Right inguinal hernia, direct type\.br\\.br\PROCEDURE PERFORMED: Laparoscopic right inguinal hernia repair with mesh (TEP).\.br\\.br\DESCRIPTION OF PROCEDURE:\.br\The patient was brought to the operating room and placed in the supine position. General anesthesia was induced. A 12mm infraumbilical incision was made and the anterior rectus sheath was opened. The rectus muscle was retracted laterally and a balloon dissector was inserted into the preperitoneal space. Under direct visualization, the balloon was inflated to create the working space. A 12mm trocar was placed and CO2 insufflation begun at 12 mmHg. Two additional 5mm trocars were placed.\.br\\.br\The direct hernia defect was identified in the floor of the inguinal canal, measuring approximately 3 cm. The cord structures were identified and mobilized. A 10 x 15 cm lightweight polypropylene mesh was introduced and positioned to cover the myopectineal orifice. The mesh was secured with absorbable tacks to Cooper's ligament and the anterior abdominal wall.\.br\\.br\The preperitoneal space was desufflated under direct vision. Hemostasis was confirmed. Fascia was closed with 0-Vicryl. Skin closed with 4-0 Monocryl subcuticular sutures. Steri-strips applied.\.br\\.br\EBL: 15 mL\.br\SPECIMENS: None\.br\DRAINS: None\.br\COMPLICATIONS: None\.br\\.br\The patient tolerated the procedure well and was transferred to PACU in stable condition.||||||F
```

---

## 19. ACK - Negative acknowledgment from Jefferson Health Northeast

```
MSH|^~\&|RHAPSODY|JH_NORTHEAST|MEDHOST|JHN_ADT|20260326094530||ACK^A08^ACK|ACK20260326094530112|P|2.5.1|||AL|NE
MSA|AE|UPD20260326094412887|Patient MRN JHN0293847 not found in master patient index - message rejected
ERR||PID^1^3|204^Unknown Key Identifier^HL70357|E||||Patient identifier does not match any record in the MPI
```

---

## 20. ORU^R01 - Radiology report with embedded image from Thomas Jefferson University Hospital

```
MSH|^~\&|PACS_POWERSCRIBE|TJUH_RAD|RHAPSODY|JEFF_CDR|20260326152200||ORU^R01^ORU_R01|RAD20260326152200445|P|2.5.1|||AL|NE||ASCII
PID|1||TJUH0482917^^^JEFFERSON^MR||Lam^William^Kwok||19681103|M||2028-9^Asian^HL70005|1923 Spruce St^^Philadelphia^PA^19103^US^H||^PRN^PH^^^215^7351928|||M|||295-08-5564
PV1|1|O|RAD^CT1^01^TJUH||||1145678^Bianchi^Michael^A^^MD^^^NPI||||||||||OP|||||||||||||||||||||||||20260326
ORC|RE|RAD28471|RAD28471^POWERSCRIBE||CM||||20260326150000|||1145678^Bianchi^Michael^A^^MD^^^NPI|TJUH_RAD||||THOMAS JEFFERSON UNIVERSITY HOSPITAL^111 S 11TH ST^^PHILADELPHIA^PA^19107|^WPN^PH^^^215^9556000
OBR|1|RAD28471|RAD28471^POWERSCRIBE|74177^CT ABDOMEN AND PELVIS WITH CONTRAST^CPT4|||20260326140000|||||||||1145678^Bianchi^Michael^A^^MD^^^NPI||||||20260326150000||RAD|F
OBX|1|FT|36643-5^Chest X-ray^LN||CT ABDOMEN AND PELVIS WITH CONTRAST\.br\\.br\CLINICAL INDICATION: Abdominal pain, elevated liver enzymes.\.br\\.br\TECHNIQUE: Helical CT of the abdomen and pelvis was performed following administration of 100 mL Omnipaque 350 IV contrast.\.br\\.br\COMPARISON: CT abdomen/pelvis dated 11/15/2025.\.br\\.br\FINDINGS:\.br\LIVER: The liver measures 18.2 cm in craniocaudal dimension, mildly enlarged. There is a 2.3 x 1.8 cm hypodense lesion in segment VII that was not present on prior study. Enhancement pattern is indeterminate. Additional sub-centimeter hypodensities in segments IV and VI are too small to characterize.\.br\\.br\GALLBLADDER AND BILIARY: Gallbladder is surgically absent. No biliary ductal dilatation. Common bile duct measures 6mm.\.br\\.br\PANCREAS: Normal in size and enhancement. No ductal dilatation.\.br\\.br\SPLEEN: Normal, 11.4 cm.\.br\\.br\KIDNEYS: Bilateral simple cortical cysts, largest 1.4 cm right kidney. No hydronephrosis or suspicious masses.\.br\\.br\BOWEL: No bowel obstruction or wall thickening. Appendix is normal.\.br\\.br\VASCULATURE: Atherosclerotic calcifications of the abdominal aorta. No aneurysm.\.br\\.br\LYMPH NODES: No pathologic lymphadenopathy.\.br\\.br\PELVIS: Urinary bladder is normal. Prostate is mildly enlarged. No free fluid.\.br\\.br\IMPRESSION:\.br\1. New 2.3 cm indeterminate liver lesion in segment VII. Recommend MRI liver with hepatocyte-specific contrast for further characterization.\.br\2. Mild hepatomegaly.\.br\3. Status post cholecystectomy without complication.||||||F|||20260326150000||1145678^Bianchi^Michael^A
OBX|2|ED|IMG^Key Image^L||^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAQABADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYI4Q/SFhSRyRXE1OCI1JjgtFKhUQ0tPAJBgMRVRkbFxY0OBpiUlJ1kJMn/9oADAMBAAIRAxEAPwC5RRRQAf/Z||||||F|||20260326150000||PACS_SYSTEM
```
