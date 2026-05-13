# MEDITECH Expanse - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to medical-surgical unit

```
MSH|^~\&|MT_EXPANSE|UPMC_PRESBYTERIAN^2.16.840.1.113883.3.1234^ISO|RHAPSODY|UPMC_HIE|20250312084523||ADT^A01^ADT_A01|MSG20250312084523001|P|2.5.1|||AL|NE||ASCII|||
EVN|A01|20250312084500|||LMURPHY^Murphy^Loretta^J^^^RN|20250312083000
PID|1||MRN4471823^^^UPMC_PRESBYTERIAN^MR~312-58-4790^^^SSA^SS||Wójcik^Stanislaw^R^^Jr||19580214|M|||1433 Penn Ave^^Pittsburgh^PA^15222^US^H||^PRN^PH^^^412^5539017|^WPN^PH^^^412^5538244||M|CAT|ACCT72018345|||||||||||N
PD1|||UPMC Presbyterian^^1234567|NPI2837465019^Calloway^Nathan^E^^^MD
NK1|1|Wójcik^Halina^M|SPO^Spouse^HL70063|1433 Penn Ave^^Pittsburgh^PA^15222^US|^PRN^PH^^^412^5539017||EC
PV1|1|I|4WEST^4W12^A^UPMC_PRESBYTERIAN^^^^4WEST|E|||ATT7789^Delgado^Emilio^F^^^MD^NPI^L^^^NPI^3819264750|REF3345^Brennan^Siobhan^M^^^MD^NPI^L^^^NPI^4920178365||MED||||7|||ATT7789^Delgado^Emilio^F^^^MD^NPI^L^^^NPI^3819264750|IN||SI|||||||||||||||||||UPMC_PRESBYTERIAN|||||20250312083000||||||V
PV2|||^Chest pain, rule out MI||||||||2|||||||||N|||||||||||||||||||N
IN1|1|BCBS_PA^Blue Cross Blue Shield PA|4567|Blue Cross Blue Shield of Pennsylvania|1901 Market St^^Philadelphia^PA^19103^US|^PRN^PH^^^215^5531234||GRP44521||Keystone Fabricators Inc|||20240101|20251231|||Wójcik^Stanislaw^R|SEL|19580214|1433 Penn Ave^^Pittsburgh^PA^15222^US||||||||||||||||XYZ334521001
DG1|1|I10|I20.9^Angina pectoris, unspecified^I10|||A
GT1|1||Wójcik^Stanislaw^R^^Jr||1433 Penn Ave^^Pittsburgh^PA^15222^US|^PRN^PH^^^412^5539017||19580214|M||SEL|312-58-4790
```

---

## 2. ADT^A04 - Emergency department registration

```
MSH|^~\&|MEDEXP|GEISINGER_DANVILLE^2.16.840.1.113883.3.5678^ISO|CENTRICITY|GHS_EDW|20250415153201||ADT^A04^ADT_A04|MSG20250415153201002|P|2.5.1|||AL|NE||ASCII|||
EVN|A04|20250415153100|||KTHOMPSON^Thompson^Keisha^D^^^RN|20250415152800
PID|1||MRN6238974^^^GEISINGER_DANVILLE^MR~178-34-9256^^^SSA^SS||Stoltzfus^Hannah^Mae||19760923|F|||284 Mill St^^Danville^PA^17821^US^H||^PRN^PH^^^570^5537812|^WPN^PH^^^570^5534509||S|LUT|ACCT53028974|||||||||||N
NK1|1|Stoltzfus^Elmer^W|FAT^Father^HL70063|RR2 Box 118^^Danville^PA^17821^US|^PRN^PH^^^570^5537499||EC
PV1|1|E|ED^TRIAGE^T3^GEISINGER_DANVILLE^^^^ED|U|||ATT2234^Chakraborty^Priya^N^^^MD^NPI^L^^^NPI^5017382946||||EM||||1|||ATT2234^Chakraborty^Priya^N^^^MD^NPI^L^^^NPI^5017382946|ER||ER|||||||||||||||||||GEISINGER_DANVILLE|||||20250415152800||||||V
PV2|||^Acute abdominal pain||||||||3|||||||||N
IN1|1|GEIS_HP^Geisinger Health Plan|7890|Geisinger Health Plan|100 N Academy Ave^^Danville^PA^17822^US|^PRN^PH^^^570^5531000||GRP98321||Montour Valley Farms|||20250101|20251231|||Stoltzfus^Hannah^Mae|SEL|19760923|284 Mill St^^Danville^PA^17821^US||||||||||||||||GHP887654001
DG1|1|I10|R10.9^Unspecified abdominal pain^I10|||A
```

---

## 3. ORM^O01 - Lab order for comprehensive metabolic panel

```
MSH|^~\&|MT_EXPANSE|READING_HOSPITAL^2.16.840.1.113883.3.9012^ISO|SUNQUEST|RH_LAB|20250228110345||ORM^O01^ORM_O01|MSG20250228110345003|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN7395214^^^READING_HOSPITAL^MR||Feliciano^Marco^A||19831107|M|||822 Cherry St^^Reading^PA^19601^US^H||^PRN^PH^^^610^5536184||||ACCT61095214
PV1|1|I|3SOUTH^3S08^B^READING_HOSPITAL^^^^3SOUTH|R|||ORD5567^Tanaka^Yuki^H^^^MD^NPI^L^^^NPI^6284019537||||MED||||2|||ORD5567^Tanaka^Yuki^H^^^MD^NPI^L^^^NPI^6284019537|IN||SI|||||||||||||||||||READING_HOSPITAL|||||20250227140000
ORC|NW|ORD2025022801^MT_EXPANSE|||||^^^20250228120000^^R||20250228110300|JKROL^Krol^Joanna^F^^^RN|||ORD5567^Tanaka^Yuki^H^^^MD^NPI^L^^^NPI^6284019537|^WPN^PH^^^610^5539471||||||READING_HOSPITAL^Reading Hospital^L
OBR|1|ORD2025022801^MT_EXPANSE||80053^Comprehensive Metabolic Panel^CPT4|||20250228110300|||||||||ORD5567^Tanaka^Yuki^H^^^MD^NPI^L^^^NPI^6284019537|^WPN^PH^^^610^5539471|||||||||^^^20250228120000^^R
DG1|1|I10|E11.9^Type 2 diabetes mellitus without complications^I10|||A
```

---

## 4. ORU^R01 - Chemistry results with critical potassium value

```
MSH|^~\&|MT_EXPANSE|LEHIGH_VALLEY^2.16.840.1.113883.3.3456^ISO|EPIC_CARE|LVHN_HIE|20250319141230||ORU^R01^ORU_R01|MSG20250319141230004|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN8412976^^^LEHIGH_VALLEY^MR||Rinaldi^Constance^T||19450618|F|||1204 Hamilton Blvd^^Allentown^PA^18103^US^H||^PRN^PH^^^610^5534297||||ACCT42012976
PV1|1|I|ICU^ICU04^A^LEHIGH_VALLEY^^^^ICU|E|||ATT8890^Okafor^Chinedu^B^^^MD^NPI^L^^^NPI^7395018264||||CCM||||1|||ATT8890^Okafor^Chinedu^B^^^MD^NPI^L^^^NPI^7395018264|IN||AI|||||||||||||||||||LEHIGH_VALLEY|||||20250318220000
ORC|RE|ORD2025031901^MT_EXPANSE|RES20250319001^LAB|||^^^20250319130000^^S||20250319141200|LAB_TECH^Huynh^Patricia||||||||||LEHIGH_VALLEY^Lehigh Valley Hospital^L
OBR|1|ORD2025031901^MT_EXPANSE|RES20250319001^LAB|80048^Basic Metabolic Panel^CPT4|||20250319130000|||||||||ATT8890^Okafor^Chinedu^B^^^MD^NPI^L^^^NPI^7395018264||||||20250319141200|||F
OBX|1|NM|2951-2^Sodium^LN||138|mmol/L|136-145|N|||F|||20250319140500||LAB_AUTO^Automated Analyzer
OBX|2|NM|2823-3^Potassium^LN||6.2|mmol/L|3.5-5.0|HH|||F|||20250319140500||LAB_AUTO^Automated Analyzer
OBX|3|NM|2075-0^Chloride^LN||101|mmol/L|98-106|N|||F|||20250319140500||LAB_AUTO^Automated Analyzer
OBX|4|NM|1963-8^Bicarbonate^LN||22|mmol/L|22-29|N|||F|||20250319140500||LAB_AUTO^Automated Analyzer
OBX|5|NM|3094-0^BUN^LN||28|mg/dL|7-20|H|||F|||20250319140500||LAB_AUTO^Automated Analyzer
OBX|6|NM|2160-0^Creatinine^LN||1.8|mg/dL|0.6-1.2|H|||F|||20250319140500||LAB_AUTO^Automated Analyzer
OBX|7|NM|2345-7^Glucose^LN||142|mg/dL|70-100|H|||F|||20250319140500||LAB_AUTO^Automated Analyzer
OBX|8|NM|17861-6^Calcium^LN||9.1|mg/dL|8.5-10.5|N|||F|||20250319140500||LAB_AUTO^Automated Analyzer
NTE|1||CRITICAL VALUE: Potassium 6.2 mmol/L. Verified by repeat analysis. Physician notified at 1413 by RN T. McBride.
```

---

## 5. ADT^A03 - Discharge with disposition to skilled nursing facility

```
MSH|^~\&|MEDITECH|MAIN_LINE_HEALTH^2.16.840.1.113883.3.7891^ISO|NTIERGY|MLH_HIE|20250405163012||ADT^A03^ADT_A03|MSG20250405163012005|P|2.5.1|||AL|NE||ASCII|||
EVN|A03|20250405162500|||NWATSON^Watson^Nadine^C^^^RN|20250405160000
PID|1||MRN5017342^^^MAIN_LINE_HEALTH^MR||Gallagher^Declan^P||19380502|M|||710 Montgomery Ave^^Bryn Mawr^PA^19010^US^H||^PRN^PH^^^610^5532781||||ACCT37017342
PV1|1|I|5NORTH^5N03^A^LANKENAU^^^^5NORTH|E|||ATT4432^Adebayo^Folake^N^^^MD^NPI^L^^^NPI^8204917563|CON2211^Rao^Vikram^S^^^MD||||MED||||1|||ATT4432^Adebayo^Folake^N^^^MD^NPI^L^^^NPI^8204917563|IN||SI||||||||||||04^Skilled Nursing Facility^HL70112|||||||MAIN_LINE_HEALTH|||||20250331080000|20250405160000|||||V
PV2|||^CHF exacerbation||||||||5|||||||||N
DG1|1|I10|I50.9^Heart failure, unspecified^I10|||A
DG1|2|I10|J18.9^Pneumonia, unspecified organism^I10|||A
DG1|3|I10|N18.3^Chronic kidney disease, stage 3^I10|||A
```

---

## 6. ORU^R01 - Radiology report with embedded PDF (ED datatype, base64)

```
MSH|^~\&|MT_EXPANSE|PENN_MEDICINE_CHESTER^2.16.840.1.113883.3.4321^ISO|PACS_ARCHIVE|PENNMED_RADIOLOGY|20250422091545||ORU^R01^ORU_R01|MSG20250422091545006|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN3028564^^^PENN_MEDICINE_CHESTER^MR||Odom^Shanice^R||19670830|F|||415 Rose Tree Rd^^Media^PA^19063^US^H||^PRN^PH^^^484^5533147||||ACCT28028564
PV1|1|O|RAD^XR01^A^PENN_MEDICINE_CHESTER^^^^RAD|R|||REF6678^Hargrove^Cynthia^A^^^MD^NPI^L^^^NPI^9182037465||||RAD||||1|||RAD2210^Liang^Wei^M^^^MD^NPI^L^^^NPI^9182037466|OUT||AM
ORC|RE|ORD2025042201^MT_EXPANSE|RES20250422001^RAD|||^^^20250422083000^^S||20250422091500|RAD_TECH^Kowalczyk^Derek||||||||||PENN_MEDICINE_CHESTER^Penn Medicine Chester County^L
OBR|1|ORD2025042201^MT_EXPANSE|RES20250422001^RAD|71046^Chest X-ray 2 views^CPT4|||20250422083500|||||||||REF6678^Hargrove^Cynthia^A^^^MD^NPI^L^^^NPI^9182037465||||||20250422091500|||F
OBX|1|TX|18748-4^Diagnostic Imaging Report^LN||CHEST PA AND LATERAL: Clinical indication: cough, shortness of breath. Comparison: Chest radiograph dated 2025-02-10. Findings: The lungs are clear bilaterally without focal consolidation, pleural effusion, or pneumothorax. The cardiac silhouette is mildly enlarged, stable compared to prior. The mediastinal contours are normal. No acute osseous abnormality. Impression: 1. No acute cardiopulmonary disease. 2. Stable mild cardiomegaly.||||||F|||20250422091200||RAD2210^Liang^Wei^M^^^MD
OBX|2|ED|18748-4^Diagnostic Imaging Report^LN|PDF|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyMzQgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihDaGVzdCBYLVJheSBSZXBvcnQgLSBQZW5uIE1lZGljaW5lIENoZXN0ZXIgQ291bnR5KSBUagowIC0yMCBUZAooUGF0aWVudDogV2FzaGluZ3RvbiwgRGVuaXNlIEwpIFRqCjAgLTIwIFRkCihEYXRlOiAyMDI1LTA0LTIyKSBUagowIC0yMCBUZAooSW1wcmVzc2lvbjogTm8gYWN1dGUgY2FyZGlvcHVsbW9uYXJ5IGRpc2Vhc2UuKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iago=||||||F|||20250422091200||RAD2210^Liang^Wei^M^^^MD
```

---

## 7. MDM^T02 - Cardiology consultation note

```
MSH|^~\&|MT_EXPANSE|ABINGTON_JEFFERSON^2.16.840.1.113883.3.6543^ISO|DOCMAN|AJH_TRANSCRIPTION|20250310152034||MDM^T02^MDM_T02|MSG20250310152034007|P|2.5.1|||AL|NE||ASCII|||
EVN|T02|20250310152000
PID|1||MRN7304581^^^ABINGTON_JEFFERSON^MR||Cieslak^Walter^H||19520711|M|||518 Old York Rd^^Jenkintown^PA^19046^US^H||^PRN^PH^^^215^5537841||||ACCT19004581
PV1|1|I|CCU^CCU02^A^ABINGTON_JEFFERSON^^^^CCU|U|||ATT9012^Espinoza^Gabriela^L^^^MD^NPI^L^^^NPI^2740198356||||CAR||||1|||CON4456^Roth^Bernard^S^^^MD^NPI^L^^^NPI^2740198357|IN||AI
TXA|1|CN^Consultation Note^HL70270|TX^Text^HL70191|20250310150000||20250310152000|||||CON4456^Roth^Bernard^S^^^MD|REP20250310001||||AU^Authenticated^HL70271||
OBX|1|TX|11488-4^Consultation Note^LN|1|CARDIOLOGY CONSULTATION NOTE~Patient: Cieslak, Walter H~DOB: 07/11/1952~Date of Consultation: 03/10/2025~Referring Physician: Dr. Gabriela Espinoza~~REASON FOR CONSULTATION: Evaluation of new-onset atrial fibrillation with rapid ventricular response.~~HISTORY OF PRESENT ILLNESS: Mr. Cieslak is a 72-year-old male admitted to the CCU with palpitations and dyspnea on exertion for 2 days. ECG on admission showed atrial fibrillation with ventricular rate of 142 bpm. He was started on IV diltiazem drip with rate now controlled at 78 bpm.~~PAST MEDICAL HISTORY: Hypertension, hyperlipidemia, type 2 diabetes, prior TIA 2022.~~MEDICATIONS: Metformin 1000mg BID, Lisinopril 20mg daily, Atorvastatin 40mg daily, Aspirin 81mg daily.~~PHYSICAL EXAMINATION: BP 128/76, HR 78 irregular, RR 16, O2 sat 96% RA. Cardiac exam: irregular rhythm, no murmurs, rubs, or gallops. JVP not elevated. Lungs clear. No peripheral edema.~~ASSESSMENT AND PLAN:~1. New-onset atrial fibrillation - CHA2DS2-VASc score 5. Recommend anticoagulation with apixaban 5mg BID.~2. Rate control - transition diltiazem drip to oral diltiazem 120mg ER daily.~3. Echocardiogram to assess LV function and left atrial size.~4. TSH level to rule out thyroid-related etiology.~~Bernard S. Roth, MD, FACC~Division of Cardiology~Abington-Jefferson Health||||||F|||20250310152000||CON4456^Roth^Bernard^S^^^MD
```

---

## 8. DFT^P03 - Charge posting for surgical procedure

```
MSH|^~\&|MEDITECH|WPAHS_ALLEGHENY^2.16.840.1.113883.3.8765^ISO|INVISION|AGH_BILLING|20250501094512||DFT^P03^DFT_P03|MSG20250501094512008|P|2.5.1|||AL|NE||ASCII|||
EVN|P03|20250501094500
PID|1||MRN4291583^^^WPAHS_ALLEGHENY^MR||Lombardi^Vincent^G||19710315|M|||907 Forbes Ave^^Pittsburgh^PA^15219^US^H||^PRN^PH^^^412^5538176||||ACCT39091583
PV1|1|I|OR^OR03^A^ALLEGHENY_GENERAL^^^^OR|E|||SUR3345^Donahue^Brendan^T^^^MD^NPI^L^^^NPI^1593028476||||SUR||||1|||SUR3345^Donahue^Brendan^T^^^MD^NPI^L^^^NPI^1593028476|IN||SI|||||||||||||||||||WPAHS_ALLEGHENY|||||20250430060000
FT1|1|20250501||20250501|CG|47562^Laparoscopic cholecystectomy^CPT4||1|||||||OR^OR03^A|SUR3345^Donahue^Brendan^T^^^MD^NPI^L^^^NPI^1593028476||K80.20^Calculus of gallbladder without cholecystitis without obstruction^I10|||||||||47562
FT1|2|20250501||20250501|CG|00790^Anesthesia for intraperitoneal procedures upper abdomen^CPT4||1|||||||OR^OR03^A|ANE7789^Tran^Linh^M^^^MD^NPI^L^^^NPI^1593028477||K80.20||||||||00790
FT1|3|20250501||20250501|CG|99232^Subsequent hospital care^CPT4||1|||||||4EAST^4E11^A|SUR3345^Donahue^Brendan^T^^^MD^NPI^L^^^NPI^1593028476||K80.20||||||||99232
DG1|1|I10|K80.20^Calculus of gallbladder without cholecystitis without obstruction^I10|||A
IN1|1|AETNA_PA^Aetna PA|2345|Aetna|151 Farmington Ave^^Hartford^CT^06156^US|^PRN^PH^^^800^5531234||GRP77234||Monongahela Steel Works|||20250101|20251231|||Lombardi^Vincent^G|SEL|19710315|907 Forbes Ave^^Pittsburgh^PA^15219^US||||||||||||||||AET567890123
```

---

## 9. ADT^A02 - Patient transfer from ICU to step-down unit

```
MSH|^~\&|MT_EXPANSE|HERSHEY_MED_CTR^2.16.840.1.113883.3.2345^ISO|CLOVERLEAF|HMC_ADT|20250327071523||ADT^A02^ADT_A02|MSG20250327071523009|P|2.5.1|||AL|NE||ASCII|||
EVN|A02|20250327071500|||AWRIGHT^Wright^Alisha^N^^^RN|20250327070000
PID|1||MRN6153708^^^HERSHEY_MED_CTR^MR||Brubaker^Levi^J||19640428|M|||22 Cocoa Ave^^Hershey^PA^17033^US^H||^PRN^PH^^^717^5534289||||ACCT85053708
PV1|1|I|SDU^SDU06^A^HERSHEY_MED_CTR^^^^SDU|U|||ATT6677^Figueroa^Andres^M^^^MD^NPI^L^^^NPI^3708194265||||MED||||1|||ATT6677^Figueroa^Andres^M^^^MD^NPI^L^^^NPI^3708194265|IN||SI|||||||||||||||||||HERSHEY_MED_CTR|||||20250322143000
PV2|||^Post CABG recovery||||||||5|||||||||N
ZBE|MVEVT20250327001|20250327070000||TRANSFER|N
```

---

## 10. BAR^P01 - Billing account registration for outpatient surgery

```
MSH|^~\&|MEDEXP|ST_LUKES_BETHLEHEM^2.16.840.1.113883.3.5432^ISO|PATCOM|SLHN_BILLING|20250218130245||BAR^P01^BAR_P01|MSG20250218130245010|P|2.5.1|||AL|NE||ASCII|||
EVN|P01|20250218130200
PID|1||MRN8047231^^^ST_LUKES_BETHLEHEM^MR||Marek^Adriana^K||19880612|F|||3710 Broadway^^Bethlehem^PA^18015^US^H||^PRN^PH^^^484^5539247||||ACCT76047231
PV1|1|O|SDS^SDS02^A^ST_LUKES_BETHLEHEM^^^^SDS|E|||SUR5544^Obermiller^Craig^D^^^MD^NPI^L^^^NPI^4815926370||||SUR||||1|||SUR5544^Obermiller^Craig^D^^^MD^NPI^L^^^NPI^4815926370|OUT||AM|||||||||||||||||||ST_LUKES_BETHLEHEM|||||20250218060000
DG1|1|I10|M23.21^Derangement of anterior horn of medial meniscus, right knee^I10|||A
GT1|1||Marek^Adriana^K||3710 Broadway^^Bethlehem^PA^18015^US|^PRN^PH^^^484^5539247||19880612|F||FT|471-28-5903
IN1|1|UNITEDHC^UnitedHealthcare|5678|UnitedHealthcare|9900 Bren Rd^^Minnetonka^MN^55343^US|^PRN^PH^^^800^5534321||GRP55123||Bethlehem Orthodontics LLC|||20250101|20251231|||Marek^Adriana^K|SEL|19880612|3710 Broadway^^Bethlehem^PA^18015^US||||||||||||||||UHC998877001
IN2||471-28-5903|||||||||||||||||||||||||||||||||||||||||||||||||||||||Marek^Roman^T|SPO
```

---

## 11. ORM^O01 - Radiology order for CT abdomen with contrast

```
MSH|^~\&|MT_EXPANSE|JEFFERSON_PHILA^2.16.840.1.113883.3.1111^ISO|RADIANT|TJU_RADIOLOGY|20250508143022||ORM^O01^ORM_O01|MSG20250508143022011|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN5183907^^^JEFFERSON_PHILA^MR||Bui^Khanh^D||19790405|M|||1232 Spruce St^^Philadelphia^PA^19107^US^H||^PRN^PH^^^215^5533892||||ACCT63083907
PV1|1|I|6TOWER^6T14^A^JEFFERSON_PHILA^^^^6TOWER|U|||ATT1122^Whitfield^Denise^M^^^MD^NPI^L^^^NPI^5926481073||||MED||||1|||ATT1122^Whitfield^Denise^M^^^MD^NPI^L^^^NPI^5926481073|IN||SI|||||||||||||||||||JEFFERSON_PHILA|||||20250506180000
ORC|NW|ORD2025050801^MT_EXPANSE|||||^^^20250508160000^^R||20250508143000|PNURSE^Guzman^Noelia^V^^^RN|||ATT1122^Whitfield^Denise^M^^^MD^NPI^L^^^NPI^5926481073|^WPN^PH^^^215^5539713||||||JEFFERSON_PHILA^Thomas Jefferson University Hospital^L
OBR|1|ORD2025050801^MT_EXPANSE||74178^CT Abdomen and Pelvis with Contrast^CPT4|||20250508143000|||||Creatinine 0.9 mg/dL on 05/07. No contrast allergy.||||ATT1122^Whitfield^Denise^M^^^MD^NPI^L^^^NPI^5926481073|^WPN^PH^^^215^5539713|||||||||^^^20250508160000^^R
DG1|1|I10|R19.00^Intra-abdominal and pelvic swelling, mass and lump, unspecified site^I10|||A
```

---

## 12. ADT^A08 - Patient information update (insurance change)

```
MSH|^~\&|MEDITECH|TEMPLE_UNIV_HOSP^2.16.840.1.113883.3.2222^ISO|XACTIMED|TUH_REG|20250412101534||ADT^A08^ADT_A08|MSG20250412101534012|P|2.5.1|||AL|NE||ASCII|||
EVN|A08|20250412101500|||CFUENTES^Fuentes^Carmen^L^^^REG|20250412101200
PID|1||MRN2948163^^^TEMPLE_UNIV_HOSP^MR||Robinson^Darnell^L||19910220|M|||2817 N Broad St Apt 4B^^Philadelphia^PA^19140^US^H||^PRN^PH^^^215^5538219||||ACCT47048163
PV1|1|I|7SOUTH^7S09^A^TEMPLE_UNIV_HOSP^^^^7SOUTH|U|||ATT3344^Hennessy^Colin^W^^^MD^NPI^L^^^NPI^6039271485||||MED||||1|||ATT3344^Hennessy^Colin^W^^^MD^NPI^L^^^NPI^6039271485|IN||SI|||||||||||||||||||TEMPLE_UNIV_HOSP|||||20250410090000
IN1|1|KEYSTONE_HMO^Keystone Health Plan East|3456|Keystone Health Plan East|1901 Market St^^Philadelphia^PA^19103^US|^PRN^PH^^^215^5531000||GRP33445||City of Philadelphia|||20250101|20251231|||Robinson^Darnell^L|SEL|19910220|2817 N Broad St Apt 4B^^Philadelphia^PA^19140^US||||||||||||||||KEY445566001
IN1|2|MEDICAID_PA^PA Medical Assistance|7891|PA Department of Human Services|625 Forster St^^Harrisburg^PA^17120^US|^PRN^PH^^^717^5535000||MAIND||||20250101|20251231|||Robinson^Darnell^L|SEL|19910220|2817 N Broad St Apt 4B^^Philadelphia^PA^19140^US||||||||||||||||MA998877665
```

---

## 13. ORU^R01 - Microbiology culture and sensitivity results

```
MSH|^~\&|MT_EXPANSE|CROZER_CHESTER^2.16.840.1.113883.3.3333^ISO|SUNQUEST|CCM_LAB|20250403162845||ORU^R01^ORU_R01|MSG20250403162845013|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN3851704^^^CROZER_CHESTER^MR||Hawkins^Lorraine^D||19480919|F|||309 W State St^^Media^PA^19063^US^H||^PRN^PH^^^610^5532087||||ACCT48051704
PV1|1|I|3WEST^3W07^A^CROZER_CHESTER^^^^3WEST|U|||ATT5566^Yun^Jennifer^H^^^MD^NPI^L^^^NPI^7150284936||||MED||||1|||ATT5566^Yun^Jennifer^H^^^MD^NPI^L^^^NPI^7150284936|IN||SI|||||||||||||||||||CROZER_CHESTER|||||20250401110000
ORC|RE|ORD2025040101^MT_EXPANSE|RES20250403001^MICRO|||^^^20250401120000^^R||20250403162800|MICRO_TECH^Gruber^Stefan||||||||||CROZER_CHESTER^Crozer-Chester Medical Center^L
OBR|1|ORD2025040101^MT_EXPANSE|RES20250403001^MICRO|87070^Culture, Bacterial, Any Source^CPT4|||20250401113000|||||||||ATT5566^Yun^Jennifer^H^^^MD^NPI^L^^^NPI^7150284936||||||20250403162800|||F
OBX|1|ST|6463-4^Bacteria Identified^LN||Escherichia coli||||||F|||20250403160000||MICRO_TECH^Gruber^Stefan
OBX|2|ST|18769-0^Source^LN||Urine, clean catch||||||F|||20250403160000||MICRO_TECH^Gruber^Stefan
OBX|3|NM|564-5^Colony Count^LN||100000|CFU/mL|||||F|||20250403160000||MICRO_TECH^Gruber^Stefan
OBX|4|ST|18907-6^Ampicillin Susceptibility^LN||R||||||F|||20250403155000||MICRO_TECH^Gruber^Stefan
OBX|5|ST|18879-7^Ciprofloxacin Susceptibility^LN||S||||||F|||20250403155000||MICRO_TECH^Gruber^Stefan
OBX|6|ST|18932-4^Nitrofurantoin Susceptibility^LN||S||||||F|||20250403155000||MICRO_TECH^Gruber^Stefan
OBX|7|ST|18996-9^Trimethoprim-Sulfamethoxazole Susceptibility^LN||R||||||F|||20250403155000||MICRO_TECH^Gruber^Stefan
OBX|8|ST|18865-6^Ceftriaxone Susceptibility^LN||S||||||F|||20250403155000||MICRO_TECH^Gruber^Stefan
NTE|1||E. coli >100,000 CFU/mL. Susceptibility testing performed by VITEK 2. Recommend ciprofloxacin or nitrofurantoin based on sensitivity profile.
```

---

## 14. MDM^T02 - Discharge summary transcription

```
MSH|^~\&|MEDEXP|TOWER_HEALTH_READING^2.16.840.1.113883.3.4444^ISO|MMODAL|TH_TRANSCRIPTION|20250420183056||MDM^T02^MDM_T02|MSG20250420183056014|P|2.5.1|||AL|NE||ASCII|||
EVN|T02|20250420183000
PID|1||MRN9204738^^^TOWER_HEALTH_READING^MR||Moretti^Antonia^V||19560303|F|||1508 Penn Ave^^Wyomissing^PA^19610^US^H||^PRN^PH^^^610^5536423||||ACCT54004738
PV1|1|I|4EAST^4E02^A^TOWER_HEALTH_READING^^^^4EAST|U|||ATT7788^Reddy^Arjun^P^^^MD^NPI^L^^^NPI^8261043975||||MED||||1|||ATT7788^Reddy^Arjun^P^^^MD^NPI^L^^^NPI^8261043975|IN||SI|||||||||||||||||||TOWER_HEALTH_READING|||||20250414120000|20250420160000
TXA|1|DS^Discharge Summary^HL70270|TX^Text^HL70191|20250420170000||20250420183000|||||ATT7788^Reddy^Arjun^P^^^MD|REP20250420001||||AU^Authenticated^HL70271||
OBX|1|TX|18842-5^Discharge Summary^LN|1|DISCHARGE SUMMARY~Patient: Moretti, Antonia V~MRN: 9204738~Admission Date: 04/14/2025~Discharge Date: 04/20/2025~Attending: Arjun P. Reddy, MD~~PRINCIPAL DIAGNOSIS: Acute exacerbation of COPD (J44.1)~~SECONDARY DIAGNOSES:~1. Type 2 diabetes mellitus (E11.9)~2. Essential hypertension (I10)~3. Osteoporosis (M81.0)~~HOSPITAL COURSE: Mrs. Moretti presented to the ED with worsening dyspnea, productive cough with yellow sputum, and oxygen saturation of 86% on room air. She was admitted to 4 East and started on IV methylprednisolone, nebulized albuterol/ipratropium q4h, and azithromycin 500mg daily. Blood cultures were negative. Sputum culture grew normal flora. Pulmonary function improved over 6 days. She was transitioned to oral prednisone taper and home nebulizer treatments.~~CONDITION AT DISCHARGE: Stable, O2 sat 93% on 2L NC.~~DISCHARGE MEDICATIONS:~1. Prednisone 40mg daily x 5 days, then taper~2. Azithromycin 250mg daily x 2 more days~3. Albuterol neb q4h PRN~4. Tiotropium 18mcg inhaler daily~5. Metformin 500mg BID~6. Lisinopril 10mg daily~~FOLLOW-UP: Dr. Reddy office in 7 days. Pulmonology referral placed.~~Arjun P. Reddy, MD~Department of Internal Medicine~Tower Health Reading Hospital||||||F|||20250420183000||ATT7788^Reddy^Arjun^P^^^MD
```

---

## 15. ORU^R01 - Pathology report with embedded base64 document (ED datatype)

```
MSH|^~\&|MT_EXPANSE|UPMC_MAGEE^2.16.840.1.113883.3.5555^ISO|COPATH|UPMC_PATHOLOGY|20250225144512||ORU^R01^ORU_R01|MSG20250225144512015|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN6720491^^^UPMC_MAGEE^MR||Jankowski^Irena^W||19720814|F|||2309 Murray Ave^^Pittsburgh^PA^15217^US^H||^PRN^PH^^^412^5531742||||ACCT52020491
PV1|1|I|SURG^SU04^A^UPMC_MAGEE^^^^SURG|E|||SUR8899^Bhatt^Neela^R^^^MD^NPI^L^^^NPI^9374150826||||SUR||||1|||SUR8899^Bhatt^Neela^R^^^MD^NPI^L^^^NPI^9374150826|IN||SI|||||||||||||||||||UPMC_MAGEE|||||20250224070000
ORC|RE|ORD2025022401^MT_EXPANSE|PATH20250225001^PATHOLOGY|||^^^20250224100000^^S||20250225144500|PATH_TECH^Krause^Heidi||||||||||UPMC_MAGEE^UPMC Magee-Womens Hospital^L
OBR|1|ORD2025022401^MT_EXPANSE|PATH20250225001^PATHOLOGY|88305^Surgical Pathology^CPT4|||20250224093000|||||||||SUR8899^Bhatt^Neela^R^^^MD^NPI^L^^^NPI^9374150826||||||20250225144500|||F
OBX|1|TX|22634-0^Pathology Report^LN|1|SURGICAL PATHOLOGY REPORT~Specimen: Right breast lumpectomy~Clinical History: 52-year-old female with mammographic abnormality, right breast, BIRADS 5.~Gross Description: Specimen received fresh for intraoperative consultation, consists of a 4.2 x 3.1 x 2.8 cm oriented breast tissue. A 1.4 cm firm, stellate, tan-white mass is identified.~Microscopic Description: Sections show invasive ductal carcinoma, grade 2 (Nottingham score 6/9: tubule formation 2, nuclear pleomorphism 2, mitotic count 2). Margins are negative, closest margin 0.4 cm (deep). No lymphovascular invasion identified. DCIS component present, solid and cribriform patterns, nuclear grade 2, spanning 0.8 cm.~FINAL DIAGNOSIS:~Right breast, lumpectomy:~- Invasive ductal carcinoma, grade 2, measuring 1.4 cm~- Margins negative (closest 0.4 cm, deep)~- No lymphovascular invasion~- DCIS present, 0.8 cm extent~Synoptic report to follow.~~Vivian C. Escalante, MD~Department of Pathology~UPMC Magee-Womens Hospital||||||F|||20250225144000||PATH3321^Escalante^Vivian^C^^^MD
OBX|2|ED|22634-0^Pathology Report^LN|SYNOPTIC|^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDIgMCBSID4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9QYWdlcyAvS2lkcyBbMyAwIFJdIC9Db3VudCAxID4+CmVuZG9iagozIDAgb2JqCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMiAwIFIgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0gL0NvbnRlbnRzIDQgMCBSIC9SZXNvdXJjZXMgPDwgL0ZvbnQgPDwgL0YxIDUgMCBSID4+ID4+ID4+CmVuZG9iago0IDAgb2JqCjw8IC9MZW5ndGggNDEyID4+CnN0cmVhbQpCVAovRjEgMTAgVGYKNzIgNzIwIFRkCihDQVAgU3lub3B0aWMgUmVwb3J0IC0gQnJlYXN0KSBUagowIC0xNiBUZAooUHJvY2VkdXJlOiBMdW1wZWN0b215KSBUagowIC0xNiBUZAooU3BlY2ltZW4gTGF0ZXJhbGl0eTogUmlnaHQpIFRqCjAgLTE2IFRkCihUdW1vciBTaXRlOiBVcHBlciBvdXRlciBxdWFkcmFudCkgVGoKMCAtMTYgVGQKKEhpc3RvbG9naWMgVHlwZTogSW52YXNpdmUgZHVjdGFsIGNhcmNpbm9tYSkgVGoKMCAtMTYgVGQKKFR1bW9yIFNpemU6IDEuNCBjbSkgVGoKMCAtMTYgVGQKKE5vdHRpbmdoYW0gR3JhZGU6IDIpIFRqCjAgLTE2IFRkCihNYXJnaW5zOiBOZWdhdGl2ZSwgY2xvc2VzdCAwLjQgY20pIFRqCjAgLTE2IFRkCihMVkk6IE5vdCBpZGVudGlmaWVkKSBUagowIC0xNiBUZAooRENJUzogUHJlc2VudCwgMC44IGNtKSBUagowIC0xNiBUZAooU3RhZ2U6IHBUMWMgcE5YKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvQ291cmllciA+PgplbmRvYmoK||||||F|||20250225144000||PATH3321^Escalante^Vivian^C^^^MD
```

---

## 16. ADT^A01 - Obstetric admission to labor and delivery

```
MSH|^~\&|MT_EXPANSE|MOSES_TAYLOR_SCRANTON^2.16.840.1.113883.3.6666^ISO|RHAPSODY|CMC_ADT|20250509021534||ADT^A01^ADT_A01|MSG20250509021534016|P|2.5.1|||AL|NE||ASCII|||
EVN|A01|20250509021500|||TWASHINGTON^Washington^Tanya^E^^^RN|20250509020000
PID|1||MRN4609218^^^MOSES_TAYLOR_SCRANTON^MR||Kaczynski^Bridget^N||19950818|F|||147 Linden St^^Scranton^PA^18503^US^H||^PRN^PH^^^570^5537021||||ACCT71009218
NK1|1|Kaczynski^Derek^M|HUS^Husband^HL70063|147 Linden St^^Scranton^PA^18503^US|^PRN^PH^^^570^5537022||EC
PV1|1|I|LD^LD04^A^MOSES_TAYLOR_SCRANTON^^^^LD|M|||ATT2233^Flanagan^Maeve^T^^^MD^NPI^L^^^NPI^1048273956||||OBG||||1|||ATT2233^Flanagan^Maeve^T^^^MD^NPI^L^^^NPI^1048273956|IN||OB|||||||||||||||||||MOSES_TAYLOR_SCRANTON|||||20250509020000
PV2|||^Active labor, G2P1 at 39w2d||||||||0|||||||||N
IN1|1|HIGHMARK_PA^Highmark Blue Cross Blue Shield|1234|Highmark Blue Cross Blue Shield|1800 Center St^^Camp Hill^PA^17089^US|^PRN^PH^^^800^5534567||GRP22178||Lackawanna County Schools|||20240901|20250831|||Kaczynski^Bridget^N|SEL|19950818|147 Linden St^^Scranton^PA^18503^US||||||||||||||||HM334455001
DG1|1|I10|O80^Encounter for full-term uncomplicated delivery^I10|||A
```

---

## 17. ORM^O01 - Pharmacy order for IV antibiotic

```
MSH|^~\&|MEDEXP|EASTON_HOSPITAL^2.16.840.1.113883.3.7777^ISO|PHARMNET|EH_PHARMACY|20250115084523||ORM^O01^ORM_O01|MSG20250115084523017|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN7814502^^^EASTON_HOSPITAL^MR||Sokolowski^Henryk^T||19550102|M|||612 Northampton St^^Easton^PA^18042^US^H||^PRN^PH^^^610^5533847||||ACCT28014502
PV1|1|I|3NORTH^3N11^A^EASTON_HOSPITAL^^^^3NORTH|U|||ATT4455^Maguire^Declan^F^^^MD^NPI^L^^^NPI^2061385947||||MED||||1|||ATT4455^Maguire^Declan^F^^^MD^NPI^L^^^NPI^2061385947|IN||SI|||||||||||||||||||EASTON_HOSPITAL|||||20250114160000
ORC|NW|ORD2025011501^MEDEXP|||||^^^20250115090000^^R||20250115084500|PHRN^Owens^Latasha^R^^^RN|||ATT4455^Maguire^Declan^F^^^MD^NPI^L^^^NPI^2061385947|^WPN^PH^^^610^5539104||||||EASTON_HOSPITAL^Easton Hospital^L
RXO|vancomycin^Vancomycin^NDC||1250|mg||IV||^^^20250115090000^^R~^^^20250115210000^^R|||||ATT4455^Maguire^Declan^F^^^MD^NPI^L^^^NPI^2061385947
RXR|IV^Intravenous^HL70162||IV^IV Push^HL70165
DG1|1|I10|L03.115^Cellulitis of right lower limb^I10|||A
NTE|1||Vancomycin 1250 mg IV q12h. Trough level before 4th dose. CrCl 52 mL/min, dose adjusted per pharmacy protocol.
```

---

## 18. ORU^R01 - Cardiac catheterization results

```
MSH|^~\&|MT_EXPANSE|PENN_HIGHLANDS_DUBOIS^2.16.840.1.113883.3.8888^ISO|CENTRICITY|PHD_CARDIOLOGY|20250306111234||ORU^R01^ORU_R01|MSG20250306111234018|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN5038271^^^PENN_HIGHLANDS_DUBOIS^MR||Sadowski^Chester^A||19600927|M|||310 Brady St^^DuBois^PA^15801^US^H||^PRN^PH^^^814^5534108||||ACCT63038271
PV1|1|I|CATH^CL01^A^PENN_HIGHLANDS_DUBOIS^^^^CATH|E|||ATT6677^Abramowitz^Eli^D^^^MD^NPI^L^^^NPI^4182059637||||CAR||||1|||ATT6677^Abramowitz^Eli^D^^^MD^NPI^L^^^NPI^4182059637|IN||AI|||||||||||||||||||PENN_HIGHLANDS_DUBOIS|||||20250306060000
ORC|RE|ORD2025030601^MT_EXPANSE|RES20250306001^CATH|||^^^20250306080000^^S||20250306111200|CATH_TECH^Novak^Gregory||||||||||PENN_HIGHLANDS_DUBOIS^Penn Highlands DuBois^L
OBR|1|ORD2025030601^MT_EXPANSE|RES20250306001^CATH|93458^Left Heart Catheterization with Ventriculography^CPT4|||20250306083000|||||||||ATT6677^Abramowitz^Eli^D^^^MD^NPI^L^^^NPI^4182059637||||||20250306111200|||F
OBX|1|TX|18745-0^Cardiac Catheterization Report^LN|1|LEFT HEART CATHETERIZATION~Operator: Eli D. Abramowitz, MD~Date: 03/06/2025~~ACCESS: Right femoral artery, 6 French sheath.~~HEMODYNAMICS: LVEDP 18 mmHg. Aortic pressure 142/78 mmHg. No gradient across aortic valve.~~LEFT VENTRICULOGRAPHY: Mild hypokinesis of the inferolateral wall. Estimated LVEF 45%.~~CORONARY ANGIOGRAPHY:~Left Main: Normal.~LAD: 80% stenosis in mid-segment with TIMI 3 flow.~LCx: 50% stenosis in proximal segment.~RCA: Dominant. 40% stenosis in mid-segment.~~IMPRESSION:~1. Significant single-vessel CAD with 80% mid-LAD stenosis.~2. Mild LV systolic dysfunction, EF 45%.~3. Elevated LVEDP consistent with diastolic dysfunction.~~RECOMMENDATION: PCI to mid-LAD with drug-eluting stent. Continue dual antiplatelet therapy.||||||F|||20250306110000||ATT6677^Abramowitz^Eli^D^^^MD
OBX|2|NM|8867-4^Heart Rate^LN||72|bpm|60-100|N|||F|||20250306083500||CATH_TECH^Novak^Gregory
OBX|3|NM|8480-6^Systolic Blood Pressure^LN||142|mmHg|90-140|H|||F|||20250306083500||CATH_TECH^Novak^Gregory
OBX|4|NM|8462-4^Diastolic Blood Pressure^LN||78|mmHg|60-90|N|||F|||20250306083500||CATH_TECH^Novak^Gregory
OBX|5|NM|10230-1^LVEF^LN||45|%|55-70|L|||F|||20250306100000||ATT6677^Abramowitz^Eli^D^^^MD
```

---

## 19. DFT^P03 - Emergency department professional fee charges

```
MSH|^~\&|MEDITECH|CONEMAUGH_MEMORIAL^2.16.840.1.113883.3.9999^ISO|EMDEON|CM_BILLING|20250128201534||DFT^P03^DFT_P03|MSG20250128201534019|P|2.5.1|||AL|NE||ASCII|||
EVN|P03|20250128201500
PID|1||MRN3704928^^^CONEMAUGH_MEMORIAL^MR||Pavlovic^Milan^W||19870704|M|||420 Somerset St^^Johnstown^PA^15901^US^H||^PRN^PH^^^814^5538604||||ACCT81004928
PV1|1|E|ED^ED08^A^CONEMAUGH_MEMORIAL^^^^ED|E|||ATT8899^Osei^Abena^K^^^MD^NPI^L^^^NPI^5270381946||||EM||||1|||ATT8899^Osei^Abena^K^^^MD^NPI^L^^^NPI^5270381946|ER||ER|||||||||||||||||||CONEMAUGH_MEMORIAL|||||20250128173000|20250128200000
FT1|1|20250128||20250128|CG|99284^ED Visit Level 4^CPT4||1|||||||ED^ED08^A|ATT8899^Osei^Abena^K^^^MD^NPI^L^^^NPI^5270381946||S62.101A^Fracture of unspecified carpal bone, right wrist, initial encounter^I10|||||||||99284
FT1|2|20250128||20250128|CG|73110^X-ray Wrist Complete^CPT4||1|||||||RAD^XR02^A|RAD5577^Castillo^Elena^R^^^MD^NPI^L^^^NPI^5270381947||S62.101A||||||||73110
FT1|3|20250128||20250128|CG|29125^Application of short arm splint^CPT4||1|||||||ED^ED08^A|ATT8899^Osei^Abena^K^^^MD^NPI^L^^^NPI^5270381946||S62.101A||||||||29125
DG1|1|I10|S62.101A^Fracture of unspecified carpal bone, right wrist, initial encounter^I10|||A
IN1|1|HIGHMARK_PA^Highmark Blue Shield|4567|Highmark Blue Shield|1800 Center St^^Camp Hill^PA^17089^US|^PRN^PH^^^800^5534567||GRP88901||Cambria Iron and Rail LLC|||20250101|20251231|||Pavlovic^Milan^W|SEL|19870704|420 Somerset St^^Johnstown^PA^15901^US||||||||||||||||HBS778899001
```

---

## 20. ADT^A08 - Patient demographic update with allergy documentation

```
MSH|^~\&|MT_EXPANSE|WVHCS_ERIE^2.16.840.1.113883.3.1010^ISO|RHAPSODY|WVHCS_MPI|20250323091212||ADT^A08^ADT_A08|MSG20250323091212020|P|2.5.1|||AL|NE||ASCII|||
EVN|A08|20250323091200|||JPEREZ^Perez^Jasmine^M^^^RN|20250323090800
PID|1||MRN1937284^^^WVHCS_ERIE^MR||Szymanski^Wanda^E||19680516|F|||1405 Peach St^^Erie^PA^16508^US^H||^PRN^PH^^^814^5536190|^WPN^PH^^^814^5539452||M|CAT|ACCT62037284|||||||||||N
PV1|1|I|5WEST^5W02^A^WVHCS_ERIE^^^^5WEST|U|||ATT9900^Villarreal^Oscar^C^^^MD^NPI^L^^^NPI^3059481726||||MED||||1|||ATT9900^Villarreal^Oscar^C^^^MD^NPI^L^^^NPI^3059481726|IN||SI|||||||||||||||||||WVHCS_ERIE|||||20250321140000
AL1|1|DA|70618^Penicillin^RxNorm|SV^Severe^HL70128|Anaphylaxis|20100315
AL1|2|DA|2670^Codeine^RxNorm|MO^Moderate^HL70128|Nausea and vomiting|20150722
AL1|3|DA|161^Acetaminophen^RxNorm|MI^Mild^HL70128|Rash|20200910
AL1|4|FA|226749^Latex^RxNorm|SV^Severe^HL70128|Contact dermatitis, respiratory distress|20180401
IN1|1|UPMC_HP^UPMC Health Plan|6789|UPMC Health Plan|600 Grant St^^Pittsburgh^PA^15219^US|^PRN^PH^^^888^5531234||GRP11223||Erie Indemnity Group|||20250101|20251231|||Szymanski^Wanda^E|SEL|19680516|1405 Peach St^^Erie^PA^16508^US||||||||||||||||UPMC556677001
```
