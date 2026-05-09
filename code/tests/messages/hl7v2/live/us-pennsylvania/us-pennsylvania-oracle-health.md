# Oracle Health (Cerner Millennium) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to medical-surgical unit

```
MSH|^~\&|CERNERPM|UPMC PRESBYTERIAN^1234567890^NPI|EPIC|PA_HIE|20260314082315||ADT^A01^ADT_A01|MSG20260314082315001|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A01|20260314082300|||TBARNES^Barnes^Theresa^L^^^MD|20260314080000
PID|1||MRN10482956^^^UPMC^MR~183-42-7691^^^SSA^SS||Jankowski^Clarence^Reginald^^Jr^Mr||19580322|M||2054-5^Black or African American^HL70005|1847 Forbes Avenue^^Pittsburgh^PA^15213^USA^H||^PRN^PH^^1^412^6815500~^NET^Internet^cjankowski@email.com|^WPN^PH^^1^412^6479000|ENG^English^HL70296|M^Married^HL70002|CHR^Christian^HL70006|ACCT2026031401^^^UPMC^AN|183-42-7691^^^PA^DL||N^Non-Hispanic^HL70189||1|||||N
PD1|||UPMC PRIMARY CARE ASSOCIATES^^12345678|1637284950^Rosetti^Frank^A^^^MD^NPI
NK1|1|Jankowski^Lorraine^Therese|SPO^Spouse^HL70063|1847 Forbes Avenue^^Pittsburgh^PA^15213^USA^H|^PRN^PH^^1^412^6810322||EC^Emergency Contact^HL70131
NK1|2|Jankowski^Mitchell^R|SON^Son^HL70063||^PRN^PH^^1^412^5551234||NK^Next of Kin^HL70131
PV1|1|I|4NORTH^4N12^A^UPMC PRESBYTERIAN^^^^4 NORTH MED SURG|E^Emergency^HL70007|||1637284950^Rosetti^Frank^A^^^MD^NPI|9182736450^Okonkwo^Adaeze^N^^^MD^NPI|MED^Medicine^HL70069||N|||7451238906^Hartman^Gail^E^^^RN^NPI|EM^Emergency^HL70004||SELF^^^UPMC^FI|||||||||||||||||ADM||AI^Accident - Industrial^HL70023|20260314082300||||||V
PV2|||^Chest pain, unspecified|||||20260315|20260318||||||||||||N
IN1|1|BCBS001^Blue Cross Blue Shield of PA^LOCAL|710001^BCBS Western PA|Blue Cross Blue Shield^^Pittsburgh^PA^15222|^PRN^PH^^1^800^5532563||GRP001234|UPMC Employee Plan|||20260101|20261231|||Jankowski^Clarence^Reginald|SEL^Self^HL70063|19580322|1847 Forbes Avenue^^Pittsburgh^PA^15213^USA|||1||||||||||||||XYZ12345678
IN2||183-42-7691|||||||||||||||||||||||||||||||||||Jankowski^Lorraine^Therese|SPO^Spouse^HL70063
DG1|1||R07.9^Chest pain, unspecified^ICD10|||A^Admitting^HL70052||||||||||1637284950^Rosetti^Frank^A^^^MD^NPI
GT1|1||Jankowski^Clarence^Reginald^^Jr^Mr||1847 Forbes Avenue^^Pittsburgh^PA^15213^USA|^PRN^PH^^1^412^6815500||19580322|M||SEL^Self^HL70063|183-42-7691
```

---

## 2. ADT^A04 - Emergency department registration

```
MSH|^~\&|CERNERPM|PENN PRESBYTERIAN MED CTR^1417188218^NPI|RHAPSODY|PA_HIE|20260412143022||ADT^A04^ADT_A04|MSG20260412143022002|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A04|20260412143000|||LPADILLA^Padilla^Lucia^F^^^RN
PID|1||MRN20483712^^^PENNMED^MR||Delgado^Sofia^Valentina^^^Mrs||19870615|F||2106-3^White^HL70005|2340 South Broad Street^^Philadelphia^PA^19145^USA^H||^PRN^PH^^1^215^5559876~^NET^Internet^sdelgado87@email.com||SPA^Spanish^HL70296|M^Married^HL70002||ACCT2026041201^^^PENNMED^AN|||N^Non-Hispanic^HL70189
NK1|1|Delgado^Mateo^Andres|SPO^Spouse^HL70063|2340 South Broad Street^^Philadelphia^PA^19145^USA^H|^PRN^PH^^1^215^5554321||EC^Emergency Contact^HL70131
PV1|1|E|EMED^ER07^A^PENN PRESBYTERIAN^^^^EMERGENCY DEPT|U^Urgent^HL70007|||2819405637^Quezada^Ramon^E^^^MD^NPI||EM^Emergency Medicine^HL70069||N|||3950174826^Tolliver^Monique^R^^^RN^NPI|EM^Emergency^HL70004||AETNA^^^AETNA^FI|||||||||||||||||REG||||||||||V
DG1|1||R10.9^Unspecified abdominal pain^ICD10|||A^Admitting^HL70052
```

---

## 3. ADT^A02 - Patient transfer to ICU

```
MSH|^~\&|CERNERPM|GEISINGER MED CTR^1205839572^NPI|CLOVERLEAF|PA_HIE|20260509101545||ADT^A02^ADT_A02|MSG20260509101545003|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A02|20260509101500|||ATURNER^Turner^Andrea^J^^^RN|20260509100000
PID|1||MRN30567821^^^GEISINGER^MR||Wozniak^Stanley^Bernard^^^Mr||19710918|M||2106-3^White^HL70005|456 Market Street^^Danville^PA^17821^USA^H||^PRN^PH^^1^570^2715500||ENG^English^HL70296|D^Divorced^HL70002||ACCT2026050901^^^GEISINGER^AN|||N^Non-Hispanic^HL70189
PV1|1|I|MICU^M03^A^GEISINGER MED CTR^^^^MEDICAL ICU|U^Urgent^HL70007|||3846192750^Bhandari^Vikram^S^^^MD^NPI|4150983267^Cromwell^Howard^T^^^MD^NPI|MED^Medicine^HL70069||N|||5093821746^Fitzgerald^Colleen^M^^^RN^NPI|EM^Emergency^HL70004||SELF|||||||||||||||||||20260507142300||||||V
PV2|||^Acute respiratory failure|||||20260509||20260516
```

---

## 4. ORM^O01 - Laboratory order for comprehensive metabolic panel

```
MSH|^~\&|POWERCHART|LEHIGH VALLEY HOSP^1639172445^NPI|SUNQUEST|LAB_SYS|20260228091200||ORM^O01^ORM_O01|MSG20260228091200004|P|2.5.1|||ER|ER||UNICODE UTF-8
PID|1||MRN40291034^^^LVHN^MR||Callahan^Siobhan^Brigid^^^Ms||19930411|F||2106-3^White^HL70005|721 Hamilton Street^^Allentown^PA^18101^USA^H||^PRN^PH^^1^610^4025000||ENG^English^HL70296|S^Single^HL70002||ACCT2026022801^^^LVHN^AN
PV1|1|I|5EAST^5E08^A^LEHIGH VALLEY HOSP^^^^5 EAST MED SURG|R^Routine^HL70007|||5291068347^Marchetti^Victor^G^^^MD^NPI||MED^Medicine^HL70069||||||IP^Inpatient^HL70004
ORC|NW|ORD2026022801^POWERCHART|||||^^^20260228091200^^R||20260228091200|KDOBBS^Dobbs^Kristen^N^^^RN|5EAST^5E08^A|^PRN^PH^^1^610^4025000|20260228091200||||||LEHIGH VALLEY HOSP^1639172445^NPI
OBR|1|ORD2026022801^POWERCHART||80053^Comprehensive Metabolic Panel^CPT4|||20260228091200||||A||^Routine^HL70064|^^^Blood&Serum||5291068347^Marchetti^Victor^G^^^MD^NPI||||||20260228091200|||F
```

---

## 5. ORU^R01 - Complete blood count results

```
MSH|^~\&|MILLENNIUM|WELLSPAN YORK HOSP^1417188330^NPI|CLOVERLEAF|PA_HIE|20260119154530||ORU^R01^ORU_R01|MSG20260119154530005|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN50382947^^^WELLSPAN^MR||Broadnax^Terrence^Lamont^^III^Mr||19650728|M||2054-5^Black or African American^HL70005|89 East Market Street^^York^PA^17401^USA^H||^PRN^PH^^1^717^8511000||ENG^English^HL70296|M^Married^HL70002||ACCT2026011901^^^WELLSPAN^AN
PV1|1|I|3WEST^3W14^A^WELLSPAN YORK HOSP||||6073914285^Steinfeld^Miriam^J^^^MD^NPI||MED^Medicine^HL70069||||||IP^Inpatient^HL70004
ORC|RE|ORD2026011901^POWERCHART|LAB2026011901^SUNQUEST||CM||||20260119150000|LAB_TECH^Truong^Binh^K
OBR|1|ORD2026011901^POWERCHART|LAB2026011901^SUNQUEST|85025^Complete Blood Count with Differential^CPT4|||20260119140000||||A||^Routine|^^^Blood&Whole Blood||6073914285^Steinfeld^Miriam^J^^^MD^NPI||||||20260119154500|||F
OBX|1|NM|6690-2^Leukocytes [#/volume] in Blood^LN||11.2|10*3/uL^thousand per microliter^UCUM|4.5-11.0|H|||F|||20260119154500||AUTO^Automated^HL70202
OBX|2|NM|789-8^Erythrocytes [#/volume] in Blood^LN||4.85|10*6/uL^million per microliter^UCUM|4.50-5.90|N|||F|||20260119154500||AUTO^Automated^HL70202
OBX|3|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||14.1|g/dL^grams per deciliter^UCUM|13.5-17.5|N|||F|||20260119154500||AUTO^Automated^HL70202
OBX|4|NM|4544-3^Hematocrit [Volume Fraction] of Blood^LN||42.3|%^percent^UCUM|38.0-50.0|N|||F|||20260119154500||AUTO^Automated^HL70202
OBX|5|NM|787-2^Mean Corpuscular Volume^LN||87.2|fL^femtoliter^UCUM|80.0-100.0|N|||F|||20260119154500||AUTO^Automated^HL70202
OBX|6|NM|785-6^Mean Corpuscular Hemoglobin^LN||29.1|pg^picogram^UCUM|27.0-33.0|N|||F|||20260119154500||AUTO^Automated^HL70202
OBX|7|NM|786-4^Mean Corpuscular Hemoglobin Concentration^LN||33.3|g/dL^grams per deciliter^UCUM|32.0-36.0|N|||F|||20260119154500||AUTO^Automated^HL70202
OBX|8|NM|777-3^Platelets [#/volume] in Blood^LN||245|10*3/uL^thousand per microliter^UCUM|150-400|N|||F|||20260119154500||AUTO^Automated^HL70202
OBX|9|NM|770-8^Neutrophils/100 leukocytes in Blood^LN||68.5|%^percent^UCUM|40.0-70.0|N|||F|||20260119154500||AUTO^Automated^HL70202
OBX|10|NM|736-9^Lymphocytes/100 leukocytes in Blood^LN||22.1|%^percent^UCUM|20.0-40.0|N|||F|||20260119154500||AUTO^Automated^HL70202
OBX|11|NM|5905-5^Monocytes/100 leukocytes in Blood^LN||6.8|%^percent^UCUM|2.0-8.0|N|||F|||20260119154500||AUTO^Automated^HL70202
OBX|12|NM|713-8^Eosinophils/100 leukocytes in Blood^LN||2.1|%^percent^UCUM|1.0-4.0|N|||F|||20260119154500||AUTO^Automated^HL70202
OBX|13|NM|706-2^Basophils/100 leukocytes in Blood^LN||0.5|%^percent^UCUM|0.0-1.0|N|||F|||20260119154500||AUTO^Automated^HL70202
```

---

## 6. ADT^A03 - Patient discharge with disposition

```
MSH|^~\&|CERNERPM|READING HOSP^1194710603^NPI|RHAPSODY|PA_HIE|20260405161200||ADT^A03^ADT_A03|MSG20260405161200006|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A03|20260405161200|||MYAMADA^Yamada^Michelle^S^^^RN
PID|1||MRN60493821^^^TOWERHEALTH^MR||Schumacher^Gerald^Alvin^^^Mr||19480205|M||2106-3^White^HL70005|312 Penn Street^^Reading^PA^19601^USA^H||^PRN^PH^^1^484^6281000||ENG^English^HL70296|W^Widowed^HL70002||ACCT2026040301^^^TOWERHEALTH^AN
PV1|1|I|6SOUTH^6S04^A^READING HOSP^^^^6 SOUTH TELEMETRY|E^Emergency^HL70007|||7204518396^Feinberg^Nathan^M^^^MD^NPI||CAR^Cardiology^HL70069|||N||||||SS^^^MEDICARE^FI|||||||||||||||||DIS||01^Home^HL70112|20260405161200|20260403084500|||||V
DG1|1||I25.10^Atherosclerotic heart disease of native coronary artery without angina pectoris^ICD10|||F^Final^HL70052
DG1|2||I10^Essential (primary) hypertension^ICD10|||F^Final^HL70052
DG1|3||E11.9^Type 2 diabetes mellitus without complications^ICD10|||F^Final^HL70052
```

---

## 7. ORU^R01 - Radiology chest X-ray report with encapsulated PDF

```
MSH|^~\&|MILLENNIUM|UPMC SHADYSIDE^1982759361^NPI|XCELERA|PA_HIE|20260322110045||ORU^R01^ORU_R01|MSG20260322110045007|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN70582136^^^UPMC^MR||Nguyen^Thanh^Duc^^^Mr||19820914|M||2028-9^Asian^HL70005|5230 Centre Avenue^^Pittsburgh^PA^15232^USA^H||^PRN^PH^^1^412^6232500||VIE^Vietnamese^HL70296|M^Married^HL70002||ACCT2026032201^^^UPMC^AN
PV1|1|I|7TOWER^7T09^A^UPMC SHADYSIDE||||8126593470^DiLorenzo^Philip^J^^^MD^NPI||PUL^Pulmonology^HL70069||||||IP^Inpatient^HL70004
ORC|RE|ORD2026032201^POWERCHART|RAD2026032201^RADIOLOGY||CM
OBR|1|ORD2026032201^POWERCHART|RAD2026032201^RADIOLOGY|71046^Chest X-ray, 2 views^CPT4|||20260322090000||||A||^Stat|^^^Chest||8126593470^DiLorenzo^Philip^J^^^MD^NPI|||||20260322110000|||F|||||||9503172648^Kowalski^Alicia^R^^^MD^NPI
OBX|1|FT|18748-4^Diagnostic Imaging Study^LN||CHEST X-RAY, 2 VIEWS\.br\\.br\CLINICAL INDICATION: Shortness of breath, rule out pneumonia\.br\\.br\COMPARISON: Chest X-ray dated 20260215\.br\\.br\FINDINGS:\.br\Heart size is within normal limits. Mediastinal contours are unremarkable.\.br\The lungs demonstrate a patchy opacity in the right lower lobe consistent with\.br\consolidation. No pleural effusion is identified. No pneumothorax.\.br\Osseous structures are intact without acute fracture.\.br\\.br\IMPRESSION:\.br\1. Right lower lobe consolidation, concerning for pneumonia in the\.br\appropriate clinical setting.\.br\2. No pleural effusion or pneumothorax.||||||F|||20260322110000||9503172648^Kowalski^Alicia^R^^^MD^NPI
OBX|2|ED|18748-4^Diagnostic Imaging Study^LN|PDF|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQKL0YxIDE4IFRmCjEwMCAzMDAgVGQKKFVQTUMgQ2hlc3QgWC1SYXkgUmVwb3J0KSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAgbiAKMDAwMDAwMDQwMCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjQ5MgolJUVPRgo=||||||F|||20260322110000||9503172648^Kowalski^Alicia^R^^^MD^NPI
```

---

## 8. ADT^A08 - Patient information update

```
MSH|^~\&|CERNERPM|ABINGTON HOSP^1568437902^NPI|RHAPSODY|PA_HIE|20260127093012||ADT^A08^ADT_A08|MSG20260127093012008|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A08|20260127093000|||JGRANT^Grant^Jacqueline^D^^^REG
PID|1||MRN80123456^^^JEFFERSON^MR||Hennessey^Colleen^Patricia^^^Mrs||19760830|F||2106-3^White^HL70005|1245 Old York Road^^Abington^PA^19001^USA^H||^PRN^PH^^1^215^4816000~^NET^Internet^chennessey76@email.com||ENG^English^HL70296|M^Married^HL70002||ACCT2026012501^^^JEFFERSON^AN|||N^Non-Hispanic^HL70189
NK1|1|Hennessey^Martin^Joseph|SPO^Spouse^HL70063|1245 Old York Road^^Abington^PA^19001^USA^H|^PRN^PH^^1^215^5557890||EC^Emergency Contact^HL70131
PV1|1|I|4WEST^4W02^A^ABINGTON HOSP||||0492581637^Calabrese^Regina^T^^^MD^NPI||ORT^Orthopedics^HL70069||||||IP^Inpatient^HL70004
IN1|1|UHC001^UnitedHealthcare^LOCAL|720001^UHC Pennsylvania|UnitedHealthcare^^King of Prussia^PA^19406|^PRN^PH^^1^800^3281000||GRP005678|Employer Plan|||20260101|20261231|||Hennessey^Colleen^Patricia|SEL^Self^HL70063|19760830|1245 Old York Road^^Abington^PA^19001^USA|||1||||||||||||||UHC98765432
```

---

## 9. SIU^S12 - Outpatient cardiology appointment scheduling

```
MSH|^~\&|MILLENNIUM|PENN STATE HEALTH MILTON S HERSHEY^1003842148^NPI|CADENCE|SCHEDULING|20260618140000||SIU^S12^SIU_S12|MSG20260618140000009|P|2.5.1|||AL|NE||UNICODE UTF-8
SCH|APT2026061801^MILLENNIUM|||||FOLLOWUP^Follow-up Visit^HL70276|CARDIOLOGY^Cardiology Follow-up^LOCAL|30^MIN|^^30^20260625093000^20260625100000||1538297064^Nagarajan^Deepak^R^^^MD^NPI|^PRN^PH^^1^717^5316000|500 University Drive^^Hershey^PA^17033|||||MHALL^Hall^Melissa^C^^^SCHED||BOOKED^Booked^HL70278
PID|1||MRN90234567^^^PSHMC^MR||Zimmermann^Elmer^Otto^^^Mr||19550312|M||2106-3^White^HL70005|78 Main Street^^Palmyra^PA^17078^USA^H||^PRN^PH^^1^717^8381234||ENG^English^HL70296|M^Married^HL70002||ACCT2026061801^^^PSHMC^AN
PV1|1|O|CARDCLIN^CC01^A^HERSHEY MED CTR^^^^CARDIOLOGY CLINIC|R^Routine^HL70007|||1538297064^Nagarajan^Deepak^R^^^MD^NPI||CAR^Cardiology^HL70069||||||OP^Outpatient^HL70004
RGS|1||CARDCLIN^Cardiology Clinic^LOCAL
AIS|1||CARDFU^Cardiology Follow-up^LOCAL|20260625093000|30^MIN
AIP|1||1538297064^Nagarajan^Deepak^R^^^MD^NPI|ATTENDING^Attending Physician^HL70286|20260625093000|30^MIN
AIL|1||CARDCLIN^CC01^A^HERSHEY MED CTR|Exam Room 1
```

---

## 10. ORM^O01 - MRI brain order with contrast

```
MSH|^~\&|POWERCHART|MAIN LINE HOSP LANKENAU^1265435793^NPI|RADNET|RAD_SYS|20260203083045||ORM^O01^ORM_O01|MSG20260203083045010|P|2.5.1|||ER|ER||UNICODE UTF-8
PID|1||MRN10345678^^^MAINLINE^MR||McGinley^Declan^Francis^^^Mr||19790524|M||2106-3^White^HL70005|401 East Lancaster Avenue^^Wynnewood^PA^19096^USA^H||^PRN^PH^^1^484^4761000||ENG^English^HL70296|M^Married^HL70002||ACCT2026020301^^^MAINLINE^AN
PV1|1|I|NEURO^N05^A^LANKENAU MED CTR||||2750194683^Acharya^Sunita^P^^^MD^NPI||NEU^Neurology^HL70069||||||IP^Inpatient^HL70004
ORC|NW|ORD2026020301^POWERCHART|||||^^^20260203090000^^S||20260203083045|PVOSS^Voss^Patricia^E^^^RN|NEURO^N05^A|||||||||LANKENAU MED CTR^1265435793^NPI
OBR|1|ORD2026020301^POWERCHART||70553^MRI Brain with and without Contrast^CPT4|||20260203090000||||A||^Stat|^^^Brain||2750194683^Acharya^Sunita^P^^^MD^NPI
NTE|1||Patient reports new onset severe headaches with visual disturbance for 3 days. Rule out intracranial mass or vascular malformation.
```

---

## 11. DFT^P03 - Charge posting for inpatient surgical procedure

```
MSH|^~\&|CERNERPM|CROZER CHESTER MED CTR^1417187984^NPI|BILLING_SYS|FINANCE|20260311160030||DFT^P03^DFT_P03|MSG20260311160030011|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|P03|20260311160030
PID|1||MRN11456789^^^CROZER^MR||Okafor^Keisha^Monique^^^Mrs||19850719|F||2054-5^Black or African American^HL70005|500 East 15th Street^^Chester^PA^19013^USA^H||^PRN^PH^^1^610^4475000||ENG^English^HL70296|M^Married^HL70002||ACCT2026031001^^^CROZER^AN
PV1|1|I|OR3^OR03^A^CROZER CHESTER^^^^OPERATING ROOM 3|E^Elective^HL70007|||3617290845^Gallagher^Brendan^W^^^MD^NPI||SUR^Surgery^HL70069||||||IP^Inpatient^HL70004
FT1|1||20260310|20260310|CG^Charge^HL70017|47562^Laparoscopic Cholecystectomy^CPT4||1|||3617290845^Gallagher^Brendan^W^^^MD^NPI||||||K80.20^Calculus of gallbladder without cholecystitis^ICD10||||CROZER CHESTER|||||SUR^Surgery
FT1|2||20260310|20260310|CG^Charge^HL70017|00790^Anesthesia for intra-abdominal procedures^CPT4||1|||4083621975^Lindquist^Helene^A^^^MD^NPI||||||K80.20^Calculus of gallbladder without cholecystitis^ICD10||||CROZER CHESTER|||||ANES^Anesthesia
FT1|3||20260310|20260310|CG^Charge^HL70017|99232^Subsequent hospital care, moderate complexity^CPT4||1|||3617290845^Gallagher^Brendan^W^^^MD^NPI||||||K80.20^Calculus of gallbladder without cholecystitis^ICD10||||CROZER CHESTER|||||SUR^Surgery
```

---

## 12. MDM^T02 - Clinical document notification with transcribed operative note

```
MSH|^~\&|POWERCHART|ST LUKES UNIV HOSP BETHLEHEM^1376534289^NPI|DOC_MGMT|PA_HIE|20260422134500||MDM^T02^MDM_T02|MSG20260422134500012|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|T02|20260422134500
PID|1||MRN12567890^^^STLUKES^MR||Fuentes^Alejandro^Miguel^^^Mr||19690303|M||2106-3^White^HL70005|824 Wyandotte Street^^Bethlehem^PA^18015^USA^H||^PRN^PH^^1^484^5265000||SPA^Spanish^HL70296|M^Married^HL70002||ACCT2026042201^^^STLUKES^AN
PV1|1|I|5NORTH^5N11^A^ST LUKES BETHLEHEM^^^^5 NORTH SURGICAL|E^Elective^HL70007|||5041827396^Hwang^Christopher^S^^^MD^NPI||ORT^Orthopedic Surgery^HL70069||||||IP^Inpatient^HL70004
TXA|1|OP^Operative Note^HL70270|TX^Text^HL70191||20260422120000||||||5041827396^Hwang^Christopher^S^^^MD^NPI|||||AU^Authenticated^HL70271||AV^Available^HL70273
OBX|1|FT|11504-8^Surgical Operation Note^LN||OPERATIVE NOTE\.br\\.br\PATIENT: Fuentes, Alejandro Miguel\.br\DATE OF PROCEDURE: 04/22/2026\.br\SURGEON: Christopher S. Hwang, MD\.br\ASSISTANT: Rebecca Stoll, PA-C\.br\ANESTHESIA: General endotracheal\.br\\.br\PREOPERATIVE DIAGNOSIS: Right knee osteoarthritis\.br\POSTOPERATIVE DIAGNOSIS: Right knee osteoarthritis\.br\PROCEDURE: Right total knee arthroplasty\.br\\.br\FINDINGS: Grade IV chondromalacia of the medial and lateral compartments\.br\with significant osteophyte formation. The patellofemoral joint showed\.br\Grade III changes. The ACL was intact, PCL was attenuated.\.br\\.br\PROCEDURE IN DETAIL:\.br\The patient was brought to the operating room and placed supine on the\.br\operating table. After induction of general anesthesia, the right lower\.br\extremity was prepped and draped in the usual sterile fashion. A midline\.br\incision was made over the anterior aspect of the right knee. A medial\.br\parapatellar arthrotomy was performed. The patella was everted laterally.\.br\Tibial and femoral cuts were made using measured resection technique.\.br\Trial components were placed and the knee was taken through a range of\.br\motion with satisfactory alignment and stability. Final components were\.br\cemented into position. The wound was irrigated copiously and closed in\.br\layers. Sterile dressing applied.\.br\\.br\ESTIMATED BLOOD LOSS: 200 mL\.br\SPECIMENS: Bone and cartilage to pathology\.br\DRAINS: One hemovac drain to right knee\.br\\.br\DISPOSITION: Patient tolerated procedure well and was transferred to\.br\PACU in stable condition.||||||F|||20260422134500||5041827396^Hwang^Christopher^S^^^MD^NPI
```

---

## 13. ORU^R01 - Pathology report with encapsulated base64 document

```
MSH|^~\&|MILLENNIUM|TEMPLE UNIV HOSP^1972525372^NPI|COPATH|PA_HIE|20260516091530||ORU^R01^ORU_R01|MSG20260516091530013|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN13678901^^^TEMPLE^MR||Robinson^Darnell^Marquis^^^Mr||19770611|M||2054-5^Black or African American^HL70005|3401 North Broad Street^^Philadelphia^PA^19140^USA^H||^PRN^PH^^1^215^7072000||ENG^English^HL70296|S^Single^HL70002||ACCT2026051601^^^TEMPLE^AN
PV1|1|I|8WEST^8W06^A^TEMPLE UNIV HOSP||||6284019573^Whitfield^Tamara^E^^^MD^NPI||HEM^Hematology^HL70069||||||IP^Inpatient^HL70004
ORC|RE|ORD2026051601^POWERCHART|PATH2026051601^COPATH||CM
OBR|1|ORD2026051601^POWERCHART|PATH2026051601^COPATH|88305^Surgical Pathology Level IV^CPT4|||20260514100000||||A||^Routine|^^^Lymph Node&Right Axillary||6284019573^Whitfield^Tamara^E^^^MD^NPI|||||20260516091500|||F|||||||7319504826^Espinoza^Rodrigo^A^^^MD^NPI
OBX|1|FT|22634-0^Pathology Report^LN||SURGICAL PATHOLOGY REPORT\.br\\.br\PATIENT: Robinson, Darnell Marquis\.br\ACCESSION: SP-2026-04521\.br\DATE COLLECTED: 05/14/2026\.br\DATE REPORTED: 05/16/2026\.br\PATHOLOGIST: Rodrigo A. Espinoza, MD\.br\\.br\CLINICAL HISTORY: Palpable right axillary mass. Rule out lymphoma.\.br\\.br\SPECIMEN: Right axillary lymph node, excisional biopsy\.br\\.br\GROSS DESCRIPTION:\.br\Received in formalin is a tan-pink lymph node measuring 3.2 x 2.1 x 1.8 cm.\.br\The cut surface is tan-white and homogeneous. Representative sections submitted\.br\in 3 cassettes.\.br\\.br\MICROSCOPIC DESCRIPTION:\.br\Sections show effacement of normal lymph node architecture by a diffuse\.br\proliferation of large atypical lymphoid cells with vesicular nuclei,\.br\prominent nucleoli, and moderate cytoplasm. Mitotic figures are frequent.\.br\Immunohistochemistry shows the cells are positive for CD20, CD10, BCL6,\.br\and MUM1, with a Ki-67 proliferation index of approximately 80%.\.br\BCL2 is negative. CD3 highlights scattered background T cells.\.br\\.br\DIAGNOSIS:\.br\Right axillary lymph node, excisional biopsy:\.br\- Diffuse large B-cell lymphoma, germinal center B-cell subtype\.br\\.br\COMMENT: Flow cytometry correlation is recommended. Results will be\.br\reported separately under accession FC-2026-01234.||||||F|||20260516091500||7319504826^Espinoza^Rodrigo^A^^^MD^NPI
OBX|2|ED|22634-0^Pathology Report^LN|DOCUMENT|^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDIgMCBSID4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9QYWdlcyAvS2lkcyBbMyAwIFJdIC9Db3VudCAxID4+CmVuZG9iagozIDAgb2JqCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMiAwIFIgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0gL0NvbnRlbnRzIDQgMCBSIC9SZXNvdXJjZXMgPDwgL0ZvbnQgPDwgL0YxIDUgMCBSID4+ID4+ID4+CmVuZG9iago0IDAgb2JqCjw8IC9MZW5ndGggMTIwID4+CnN0cmVhbQpCVAovRjEgMTIgVGYKNzIgNzIwIFRkCihURU1QTEUgVU5JVkVSU0lUWSBIT1NQSVRBTCkgVGoKMCA0MCBUZAooU3VyZ2ljYWwgUGF0aG9sb2d5IFJlcG9ydCkgVGoKMCAtMjAgVGQKKFNQLTIwMjYtMDQ1MjEgLSBKYWNrc29uLCBUeXJvbmUgTC4pIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxNSAwMDAwMCBuIAowMDAwMDAwMDY0IDAwMDAwIG4gCjAwMDAwMDAxMjEgMDAwMDAgbiAKMDAwMDAwMDMxOSAwMDAwMCBuIAowMDAwMDAwNDkxIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTc4CiUlRU9GCg==||||||F|||20260516091500||7319504826^Espinoza^Rodrigo^A^^^MD^NPI
```

---

## 14. ADT^A01 - Neonatal admission to NICU

```
MSH|^~\&|CERNERPM|MAGEE WOMENS HOSP UPMC^1790784752^NPI|CLOVERLEAF|PA_HIE|20260701032215||ADT^A01^ADT_A01|MSG20260701032215014|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A01|20260701032200|||DSHEPPARD^Sheppard^Donna^R^^^RN|20260701031500
PID|1||MRN14789012^^^UPMC^MR||Baby Boy Velasquez^^^^Baby||20260701|M||2106-3^White^HL70005|1548 Smallman Street^^Pittsburgh^PA^15222^USA^H||^PRN^PH^^1^412^6418000||ENG^English^HL70296|S^Single^HL70002||ACCT2026070101^^^UPMC^AN|||H^Hispanic or Latino^HL70189
NK1|1|Velasquez^Adriana^Camila|MTH^Mother^HL70063|1548 Smallman Street^^Pittsburgh^PA^15222^USA^H|^PRN^PH^^1^412^6418000||EC^Emergency Contact^HL70131
NK1|2|Velasquez^Ernesto^Rafael|FTH^Father^HL70063|1548 Smallman Street^^Pittsburgh^PA^15222^USA^H|^PRN^PH^^1^412^5551847||NK^Next of Kin^HL70131
PV1|1|I|NICU^N12^A^MAGEE WOMENS HOSP^^^^NICU LEVEL III|N^Newborn^HL70007|||8351946720^Yamamoto^Cynthia^L^^^MD^NPI|9027415386^Osei^Kwame^D^^^MD^NPI|PED^Neonatology^HL70069||N|||0174295836^Maldonado^Teresa^A^^^RN^NPI|NB^Newborn^HL70004||MEDICAID^^^PA_MEDICAID^FI|||||||||||||||||ADM||||||||||V
DG1|1||P07.38^Other preterm newborn, gestational age 33 completed weeks^ICD10|||A^Admitting^HL70052
DG1|2||P22.0^Respiratory distress syndrome of newborn^ICD10|||A^Admitting^HL70052
```

---

## 15. ORU^R01 - Troponin I result critical high

```
MSH|^~\&|MILLENNIUM|ALLEGHENY GENERAL HOSP^1306816624^NPI|SUNQUEST|PA_HIE|20260818220145||ORU^R01^ORU_R01|MSG20260818220145015|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN15890123^^^AHN^MR||Kowalewski^Florence^Irene^^^Mrs||19540416|F||2106-3^White^HL70005|200 Lothrop Street^^Pittsburgh^PA^15213^USA^H||^PRN^PH^^1^412^3592000||ENG^English^HL70296|W^Widowed^HL70002||ACCT2026081801^^^AHN^AN
PV1|1|E|ED^ER03^A^ALLEGHENY GENERAL^^^^EMERGENCY DEPT|E^Emergency^HL70007|||0851374296^Obianwu^Chukwudi^N^^^MD^NPI||EM^Emergency Medicine^HL70069||||||EM^Emergency^HL70004
ORC|RE|ORD2026081801^POWERCHART|LAB2026081801^SUNQUEST||CM||||20260818220100|LAB_TECH^Pham^Linh^T
OBR|1|ORD2026081801^POWERCHART|LAB2026081801^SUNQUEST|93971^Troponin Panel^LOCAL|||20260818213000||||A||^Stat|^^^Blood&Serum||0851374296^Obianwu^Chukwudi^N^^^MD^NPI||||||20260818220100|||F
OBX|1|NM|49563-0^Troponin I, cardiac [Mass/volume] in Serum or Plasma^LN||2.47|ng/mL^nanograms per milliliter^UCUM|0.00-0.04|HH|||F|||20260818220100||AUTO^Automated^HL70202
OBX|2|NM|33762-6^NT-proBNP [Mass/volume] in Serum or Plasma^LN||1842|pg/mL^picograms per milliliter^UCUM|0-125|HH|||F|||20260818220100||AUTO^Automated^HL70202
NTE|1||CRITICAL VALUE: Troponin I 2.47 ng/mL. Physician notified at 2202 by RN S. Kravitz. Read back confirmed.
```

---

## 16. ORM^O01 - Medication order for IV antibiotics

```
MSH|^~\&|POWERCHART|GEISINGER WYOMING VALLEY^1487653024^NPI|PHARMNET|PHARMACY|20260924111500||ORM^O01^ORM_O01|MSG20260924111500016|P|2.5.1|||ER|ER||UNICODE UTF-8
PID|1||MRN16901234^^^GEISINGER^MR||Sokolowski^Edward^Casimir^^^Mr||19620108|M||2106-3^White^HL70005|312 Scott Street^^Wilkes-Barre^PA^18702^USA^H||^PRN^PH^^1^570^8087000||ENG^English^HL70296|M^Married^HL70002||ACCT2026092401^^^GEISINGER^AN
PV1|1|I|7SOUTH^7S08^A^GEISINGER WYO VALLEY^^^^7 SOUTH MED SURG|U^Urgent^HL70007|||1950427638^Iyengar^Priya^M^^^MD^NPI||MED^Medicine^HL70069||||||IP^Inpatient^HL70004
ORC|NW|ORD2026092401^POWERCHART|||||^^^20260924120000^^R||20260924111500|WCARTER^Carter^William^J^^^PharmD|7SOUTH^7S08^A|||||||||GEISINGER WYO VALLEY^1487653024^NPI
OBR|1|ORD2026092401^POWERCHART||RX001^Pharmacy Order^LOCAL|||20260924120000
RXO|1|0009-0321-02^Piperacillin-Tazobactam 3.375g^NDC||3.375|g^gram^UCUM|||||||IV^Intravenous^HL70162
RXR|IV^Intravenous^HL70162|LA^Left Arm^HL70163
RXE|^^^20260924120000^^R|0009-0321-02^Piperacillin-Tazobactam 3.375g^NDC|3.375|3.375|g^gram^UCUM||Q6H^Every 6 Hours^HL70335|||||||||||||||||||30^MIN^Infusion Duration
NTE|1||Indication: Community-acquired pneumonia. CrCl 62 mL/min. No known drug allergies. Duration: 7 days.
```

---

## 17. SIU^S12 - Surgical scheduling for hip replacement

```
MSH|^~\&|MILLENNIUM|UPMC HAMOT^1225043166^NPI|CADENCE|SCHEDULING|20260803100000||SIU^S12^SIU_S12|MSG20260803100000017|P|2.5.1|||AL|NE||UNICODE UTF-8
SCH|APT2026080301^MILLENNIUM|||||SURGERY^Surgical Procedure^HL70276|TOTHIPREP^Total Hip Replacement^LOCAL|180^MIN|^^180^20260815073000^20260815103000||2081743596^Rutkowski^Stefan^J^^^MD^NPI|^PRN^PH^^1^814^8770000|201 State Street^^Erie^PA^16550|||||SCHEDULR^Pfeffer^Rita^M^^^SCHED||BOOKED^Booked^HL70278
PID|1||MRN17012345^^^UPMC^MR||Grabowski^Chester^Tadeusz^^^Mr||19571122|M||2106-3^White^HL70005|945 West 26th Street^^Erie^PA^16508^USA^H||^PRN^PH^^1^814^4565000||ENG^English^HL70296|M^Married^HL70002||ACCT2026080301^^^UPMC^AN
PV1|1|P|ORSUITE^OR02^A^UPMC HAMOT^^^^OPERATING ROOM 2|E^Elective^HL70007|||2081743596^Rutkowski^Stefan^J^^^MD^NPI||ORT^Orthopedic Surgery^HL70069||||||PRE^Preadmit^HL70004
RGS|1||ORSUITE^Operating Room Suite^LOCAL
AIS|1||27447^Total Hip Arthroplasty^CPT4|20260815073000|180^MIN
AIP|1||2081743596^Rutkowski^Stefan^J^^^MD^NPI|SURGEON^Primary Surgeon^HL70286|20260815073000|180^MIN
AIP|2||3720596184^Gupta^Anand^V^^^MD^NPI|ANES^Anesthesiologist^HL70286|20260815073000|180^MIN
AIL|1||ORSUITE^OR02^A^UPMC HAMOT|Operating Room 2
```

---

## 18. ADT^A08 - Insurance update for existing patient

```
MSH|^~\&|CERNERPM|CHRISTIANA CARE HOSP^POCONO^1609822435^NPI|RHAPSODY|PA_HIE|20261002140530||ADT^A08^ADT_A08|MSG20261002140530018|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A08|20261002140500|||BFIELDS^Fields^Brenda^K^^^REG
PID|1||MRN18123456^^^LVHN^MR||Kravchenko^Dmitri^Yevgeni^^^Mr||19830227|M||2106-3^White^HL70005|1210 Main Street^^Stroudsburg^PA^18360^USA^H||^PRN^PH^^1^570^4213000||ENG^English^HL70296|M^Married^HL70002||ACCT2026100201^^^LVHN^AN|||N^Non-Hispanic^HL70189
PV1|1|I|3NORTH^3N06^A^POCONO MED CTR||||4260839175^Novotny^Karl^P^^^MD^NPI||MED^Medicine^HL70069||||||IP^Inpatient^HL70004
IN1|1|CIGNA001^Cigna^LOCAL|730001^Cigna Pennsylvania|Cigna^^Bloomfield^CT^06002|^PRN^PH^^1^800^2441247||GRP009012|Employer PPO Plan|||20260101|20261231|||Kravchenko^Dmitri^Yevgeni|SEL^Self^HL70063|19830227|1210 Main Street^^Stroudsburg^PA^18360^USA|||1||||||||||||||CIGNA55667788
IN1|2|MCARE001^Medicare Part A^LOCAL|740001^CMS|Centers for Medicare and Medicaid^^Baltimore^MD^21244|^PRN^PH^^1^800^6334227||||||20250101|||||Kravchenko^Dmitri^Yevgeni|SEL^Self^HL70063|19830227|1210 Main Street^^Stroudsburg^PA^18360^USA|||2||||||||||||||1EG4-TE5-MK72
```

---

## 19. ORU^R01 - Microbiology blood culture result

```
MSH|^~\&|MILLENNIUM|THOMAS JEFFERSON UNIV HOSP^1316909432^NPI|SUNQUEST|PA_HIE|20260607183000||ORU^R01^ORU_R01|MSG20260607183000019|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN19234567^^^JEFFERSON^MR||Cartwright^Jasmine^Elaine^^^Ms||19910803|F||2054-5^Black or African American^HL70005|1020 Walnut Street^^Philadelphia^PA^19107^USA^H||^PRN^PH^^1^215^9556000||ENG^English^HL70296|S^Single^HL70002||ACCT2026060701^^^JEFFERSON^AN
PV1|1|I|MICU^M08^A^THOMAS JEFFERSON^^^^MEDICAL ICU|U^Urgent^HL70007|||5491720638^Rosen^Howard^B^^^MD^NPI||MED^Internal Medicine^HL70069||||||IP^Inpatient^HL70004
ORC|RE|ORD2026060701^POWERCHART|MICRO2026060701^SUNQUEST||CM||||20260607182500|LAB_TECH^Choi^Soo-Yeon^M
OBR|1|ORD2026060701^POWERCHART|MICRO2026060701^SUNQUEST|87040^Blood Culture, Aerobic^CPT4|||20260605140000||||A||^Routine|^^^Blood&Whole Blood||5491720638^Rosen^Howard^B^^^MD^NPI||||||20260607182500|||F
OBX|1|CWE|600-7^Bacteria identified in Blood by Culture^LN||3092008^Staphylococcus aureus^SCT||||||F|||20260607182500||LAB_TECH^Choi^Soo-Yeon^M
OBX|2|ST|29576-6^Bacterial susceptibility panel^LN||See Susceptibility Results Below||||||F|||20260607182500
OBX|3|SN|18907-6^Oxacillin [Susceptibility]^LN||<=^0.25|ug/mL^microgram per milliliter^UCUM|<=2|S|||F|||20260607182500
OBX|4|SN|18964-7^Vancomycin [Susceptibility]^LN||<=^1|ug/mL^microgram per milliliter^UCUM|<=2|S|||F|||20260607182500
OBX|5|SN|18878-9^Gentamicin [Susceptibility]^LN||<=^0.5|ug/mL^microgram per milliliter^UCUM|<=4|S|||F|||20260607182500
OBX|6|SN|18993-6^Trimethoprim-Sulfamethoxazole [Susceptibility]^LN||<=^0.5/9.5|ug/mL^microgram per milliliter^UCUM|<=2/38|S|||F|||20260607182500
OBX|7|SN|18903-5^Clindamycin [Susceptibility]^LN||<=^0.25|ug/mL^microgram per milliliter^UCUM|<=0.5|S|||F|||20260607182500
OBX|8|SN|18919-1^Erythromycin [Susceptibility]^LN||>^8|ug/mL^microgram per milliliter^UCUM|<=0.5|R|||F|||20260607182500
NTE|1||METHICILLIN-SUSCEPTIBLE STAPHYLOCOCCUS AUREUS (MSSA). Two of two aerobic bottles positive at 18 hours. Anaerobic culture negative.
```

---

## 20. DFT^P03 - Emergency department professional fee charges

```
MSH|^~\&|CERNERPM|MOSES TAYLOR HOSP^1205835594^NPI|BILLING_SYS|FINANCE|20261115093045||DFT^P03^DFT_P03|MSG20261115093045020|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|P03|20261115093045
PID|1||MRN20345678^^^COMMONWEALTH^MR||Flannery^Cormac^Seamus^^^Mr||19880512|M||2106-3^White^HL70005|540 Madison Avenue^^Scranton^PA^18510^USA^H||^PRN^PH^^1^570^7708100||ENG^English^HL70296|S^Single^HL70002||ACCT2026111401^^^COMMONWEALTH^AN
PV1|1|E|ED^ER11^A^MOSES TAYLOR^^^^EMERGENCY DEPT|E^Emergency^HL70007|||6950341827^Petrosyan^Armen^G^^^MD^NPI||EM^Emergency Medicine^HL70069||||||EM^Emergency^HL70004
FT1|1||20261114|20261114|CG^Charge^HL70017|99284^ED Visit, High Complexity^CPT4||1|||6950341827^Petrosyan^Armen^G^^^MD^NPI||||||S62.102A^Fracture of unspecified carpal bone, left wrist, initial encounter^ICD10||||MOSES TAYLOR|||||EM^Emergency Medicine
FT1|2||20261114|20261114|CG^Charge^HL70017|73110^X-ray Wrist, 3 views^CPT4||1|||6950341827^Petrosyan^Armen^G^^^MD^NPI||||||S62.102A^Fracture of unspecified carpal bone, left wrist, initial encounter^ICD10||||MOSES TAYLOR|||||RAD^Radiology
FT1|3||20261114|20261114|CG^Charge^HL70017|29075^Application of Short Arm Cast^CPT4||1|||6950341827^Petrosyan^Armen^G^^^MD^NPI||||||S62.102A^Fracture of unspecified carpal bone, left wrist, initial encounter^ICD10||||MOSES TAYLOR|||||EM^Emergency Medicine
FT1|4||20261114|20261114|CG^Charge^HL70017|J1885^Ketorolac tromethamine injection^HCPCS||1|||6950341827^Petrosyan^Armen^G^^^MD^NPI||||||S62.102A^Fracture of unspecified carpal bone, left wrist, initial encounter^ICD10||||MOSES TAYLOR|||||EM^Emergency Medicine
```
