# Epic (Bridges) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to Cleveland Clinic main campus

```
MSH|^~\&|EPICADT|CCF|RECEIVING|EXTAPP|20260415083021||ADT^A01^ADT_A01|MSG20260415083021001|P|2.5.1|||AL|NE
EVN|A01|20260415083000|||JSMITH^Smith^Jennifer^M^^^MD
PID|1||MRN4419523^^^CCF^MR~371-52-8946^^^SSA^SS||Kowalczyk^Brenda^Lucille^^Mrs.^||19680314|F||2106-3^White^CDCREC|2145 Euclid Ave^^Cleveland^OH^44115^US^H||^PRN^PH^^^216^5529847~^NET^Internet^brenda.kowalczyk@email.com||ENG|M|CHR|ACCT10045678^^^CCF^AN|371-52-8946|||N||||20260415
PD1|||Cleveland Clinic Main Campus^^^CCF||||||||N
NK1|1|Kowalczyk^Walter^R^^Mr.^||2145 Euclid Ave^^Cleveland^OH^44115^US|^PRN^PH^^^216^5529848||SPO^Spouse^HL70063
NK1|2|Kowalczyk^Renee^M^^Ms.^||8834 Ridge Rd^^North Royalton^OH^44133^US|^PRN^PH^^^440^3371256||DAU^Daughter^HL70063
PV1|1|I|5EAST^5102^A^CCF^^^^5EAST|||1482937^Okafor^Raymond^B^^^MD^^^NPI|9174628^Tran^Michelle^L^^^MD^^^NPI||MED||||7|||1482937^Okafor^Raymond^B^^^MD^^^NPI|IN||BCBS|||||||||||||||AI|||20260415083000
PV2|||^Chest pain, shortness of breath||||||20260415|||||||||||||N
DG1|1|I10|I21.0^ST elevation myocardial infarction involving left main coronary artery^ICD10|||A
DG1|2|I10|I25.10^Atherosclerotic heart disease of native coronary artery without angina pectoris^ICD10|||S
AL1|1|DA|70618^Penicillin^RxNorm|MO|Hives and difficulty breathing|20150612
AL1|2|FA|226971^Shellfish^UNII|SV|Anaphylaxis|20100303
IN1|1|001|BCBS001^BlueCross BlueShield of Ohio|Blue Cross Blue Shield^^Independence^OH^44131|^PRN^PH^^^800^2232273|||||GRP445566||FULLTIME|||Kowalczyk^Brenda^Lucille|SEL|19680314|2145 Euclid Ave^^Cleveland^OH^44115||1|||||||||||||POL778899||||||F
IN1|2|002|AETNA01^Aetna|Aetna Insurance^^Hartford^CT^06156|^PRN^PH^^^800^8721862|||||GRP112233||FULLTIME|||Kowalczyk^Brenda^Lucille|SEL|19680314|2145 Euclid Ave^^Cleveland^OH^44115||2|||||||||||||POL334455||||||F
GT1|1||Kowalczyk^Brenda^Lucille^^Mrs.^|2145 Euclid Ave^^Cleveland^OH^44115^US|^PRN^PH^^^216^5529847|^PRN^PH^^^216^5529848|19680314|F||SEL|371-52-8946
```

---

## 2. ADT^A04 - Emergency department registration at Ohio State Wexner

```
MSH|^~\&|EPICADT|OSUWMC|RECEIVING|EXTAPP|20260418142233||ADT^A04^ADT_A04|MSG20260418142233002|P|2.5|||AL|NE
EVN|A04|20260418142200|||EDREGISTRAR
PID|1||MRN7723456^^^OSUWMC^MR||Crawford^Terrence^Malik^^Mr.^||19850921|M||2054-5^Black or African American^CDCREC|456 High St Apt 3B^^Columbus^OH^43215^US^H||^PRN^PH^^^614^7728341~^PRN^CP^^^614^8813294||ENG|S|NON|ACCT30098712^^^OSUWMC^AN|418-63-5972|||N||||20260418
NK1|1|Crawford^Doris^A^^Mrs.^||890 Broad St^^Columbus^OH^43215^US|^PRN^PH^^^614^7729184||MTH^Mother^HL70063
PV1|1|E|EMED^ER04^A^OSUWMC^^^^EMED|||8293147^Kapoor^Suresh^K^^^MD^^^NPI||||EMR||||1|||8293147^Kapoor^Suresh^K^^^MD^^^NPI|EM||MCARE|||||||||||||||AA|||20260418142200
PV2|||^Fall from bicycle, left wrist pain||||||||||||||||||||N
DG1|1|I10|S62.102A^Fracture of unspecified carpal bone, left wrist, initial encounter^ICD10|||A
AL1|1|DA|2670^Codeine^RxNorm|MI|Nausea and vomiting|20200115
IN1|1|001|MCARE001^Medicare|Centers for Medicare^^Baltimore^MD^21244|^PRN^PH^^^800^6332273|||||||||Crawford^Terrence^Malik|SEL|19850921|456 High St Apt 3B^^Columbus^OH^43215||1|||||||||||||HIC418635972A||||||M
```

---

## 3. ORU^R01 - Lab results with CBC panel from UC Health Cincinnati

```
MSH|^~\&|EPICCARE|UCHEALTH|RECEIVING|LAB|20260420091545||ORU^R01^ORU_R01|MSG20260420091545003|P|2.5.1|||AL|NE
PID|1||MRN5567890^^^UCH^MR||Brennan^Colleen^Patricia^^Ms.^||19790508|F||2106-3^White^CDCREC|7834 Montgomery Rd^^Cincinnati^OH^45236^US^H||^PRN^PH^^^513^6618472||ENG|M|CAT|ACCT20056781^^^UCH^AN|529-41-7836|||N
PV1|1|O|LABDRAW^LD01^1^UCH||||3819274^Velasquez^Diana^R^^^MD^^^NPI||||LAB||||7|||3819274^Velasquez^Diana^R^^^MD^^^NPI|OP||AETNA
ORC|RE|ORD20260420001|FIL20260420001||CM||||20260420080000|||3819274^Velasquez^Diana^R^^^MD^^^NPI
OBR|1|ORD20260420001|FIL20260420001|57021-8^CBC W Auto Differential panel in Blood^LN|||20260420074500|||||||||3819274^Velasquez^Diana^R^^^MD^^^NPI||||||20260420091500|||F
OBX|1|NM|6690-2^Leukocytes [#/volume] in Blood by Automated count^LN||7.2|10*3/uL|4.5-11.0|N|||F|||20260420091500
OBX|2|NM|789-8^Erythrocytes [#/volume] in Blood by Automated count^LN||4.65|10*6/uL|4.00-5.50|N|||F|||20260420091500
OBX|3|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||13.8|g/dL|12.0-16.0|N|||F|||20260420091500
OBX|4|NM|4544-3^Hematocrit [Volume Fraction] of Blood by Automated count^LN||41.2|%|36.0-46.0|N|||F|||20260420091500
OBX|5|NM|787-2^MCV [Entitic volume] by Automated count^LN||88.6|fL|80.0-100.0|N|||F|||20260420091500
OBX|6|NM|785-6^MCH [Entitic mass] by Automated count^LN||29.7|pg|27.0-33.0|N|||F|||20260420091500
OBX|7|NM|786-4^MCHC [Mass/volume] by Automated count^LN||33.5|g/dL|32.0-36.0|N|||F|||20260420091500
OBX|8|NM|788-0^Erythrocyte distribution width [Ratio] by Automated count^LN||13.1|%|11.5-14.5|N|||F|||20260420091500
OBX|9|NM|777-3^Platelets [#/volume] in Blood by Automated count^LN||245|10*3/uL|150-400|N|||F|||20260420091500
OBX|10|NM|770-8^Neutrophils/100 leukocytes in Blood by Automated count^LN||62.3|%|40.0-70.0|N|||F|||20260420091500
OBX|11|NM|736-9^Lymphocytes/100 leukocytes in Blood by Automated count^LN||28.1|%|20.0-40.0|N|||F|||20260420091500
OBX|12|NM|5905-5^Monocytes/100 leukocytes in Blood by Automated count^LN||7.4|%|2.0-8.0|N|||F|||20260420091500
OBX|13|NM|713-8^Eosinophils/100 leukocytes in Blood by Automated count^LN||1.8|%|1.0-4.0|N|||F|||20260420091500
OBX|14|NM|706-2^Basophils/100 leukocytes in Blood by Automated count^LN||0.4|%|0.0-1.0|N|||F|||20260420091500
```

---

## 4. ORM^O01 - Radiology order for chest CT at ProMedica Toledo

```
MSH|^~\&|EPIC|PROMEDICA|RADIS|IMGCTR|20260422153045||ORM^O01^ORM_O01|MSG20260422153045004|P|2.4|||AL|NE
PID|1||MRN8834567^^^PROM^MR||Harding^Denise^Yvonne^^Mrs.^||19560212|F||2054-5^Black or African American^CDCREC|1523 Monroe St^^Toledo^OH^43604^US^H||^PRN^PH^^^419^6627381||ENG|W|BAP|ACCT40012398^^^PROM^AN|638-27-4015|||N
PV1|1|O|RADOL^RAD02^1^PROM^^^^RADOL|||5294837^Lindstrom^Gregory^W^^^MD^^^NPI||||RAD||||7|||5294837^Lindstrom^Gregory^W^^^MD^^^NPI|OP||UHCOH
IN1|1|001|UHC001^UnitedHealthcare of Ohio|UnitedHealthcare^^Minneapolis^MN^55343|^PRN^PH^^^800^3285979|||||GRP887766||FULLTIME|||Harding^Denise^Yvonne|SEL|19560212|1523 Monroe St^^Toledo^OH^43604||1|||||||||||||POL223344||||||F
ORC|NW|ORD20260422001||||||1^^^20260423080000^^R||20260422153000|RADCLERK||5294837^Lindstrom^Gregory^W^^^MD^^^NPI|RADOL|^PRN^PH^^^419^2914000||||||ProMedica Toledo Hospital^2142 N Cove Blvd^^Toledo^OH^43606
OBR|1|ORD20260422001||71260^CT CHEST WITH CONTRAST^CPT4|||20260423080000||||N|||||5294837^Lindstrom^Gregory^W^^^MD^^^NPI|||||||RAD||1^^^20260423080000^^R||||^Persistent cough, weight loss, evaluate for pulmonary mass
DG1|1|I10|R05.9^Cough, unspecified^ICD10|||A
DG1|2|I10|R63.4^Abnormal weight loss^ICD10|||S
```

---

## 5. SIU^S12 - Appointment scheduled at OhioHealth Riverside

```
MSH|^~\&|EPIC|OHIOHEALTH|SCHEDULING|EXTAPP|20260423104512||SIU^S12^SIU_S12|MSG20260423104512005|P|2.5|||AL|NE
SCH|APPT20260501001|APPT20260501001|||ROUTINE^Routine^HL70276|FOLLOWUP^Follow Up Visit^APPTREAS||30|min|^^30^20260501140000^20260501143000|7382915^Nwosu^Patricia^S^^^MD^^^NPI|^PRN^PH^^^614^5662800|3200 Olentangy River Rd^^Columbus^OH^43202^^|||7382915^Nwosu^Patricia^S^^^MD^^^NPI||BOOKED
PID|1||MRN6645234^^^OHHLTH^MR||Gutierrez^Roberto^Alejandro^^Mr.^||19720619|M||2131-1^Other Race^CDCREC|890 Livingston Ave^^Columbus^OH^43205^US^H||^PRN^PH^^^614^8813729~^PRN^CP^^^614^9927184||SPA|M|CAT|ACCT50023456^^^OHHLTH^AN|742-18-3956|||H
PV1|1|O|CARD^CARD01^1^OHHLTH^^^^CARD|||7382915^Nwosu^Patricia^S^^^MD^^^NPI||||CAR||||7|||7382915^Nwosu^Patricia^S^^^MD^^^NPI|OP||ANTHEM
RGS|1|A
AIS|1|A|CARDFOLLOW^Cardiology Follow Up^LOCAL|20260501140000|0|min|30|min
AIG|1|A|7382915^Nwosu^Patricia^S^^^MD^^^NPI
AIL|1|A|CARD^CARD01^1^OHHLTH
```

---

## 6. ADT^A03 - Patient discharge from Cleveland Clinic Akron General

```
MSH|^~\&|EPICADT|CCAG|RECEIVING|EXTAPP|20260424161234||ADT^A03^ADT_A03|MSG20260424161234006|P|2.5.1|||AL|NE
EVN|A03|20260424161000|||DCCLERK
PID|1||MRN2234567^^^CCAG^MR||Hwang^David^Sung^^Mr.^||19910803|M||2028-9^Asian^CDCREC|456 Market St Apt 12^^Akron^OH^44308^US^H||^PRN^PH^^^330^7714289~^PRN^CP^^^330^9913847||CHI|S|BUD|ACCT60034567^^^CCAG^AN|284-51-9673|||N
PV1|1|I|3WEST^3215^B^CCAG^^^^3WEST|||2847193^Fitzgerald^Patrick^J^^^MD^^^NPI|3918274^Nakamura^Susan^H^^^MD^^^NPI||MED||||7|||2847193^Fitzgerald^Patrick^J^^^MD^^^NPI|IN||ANTHEM|||||||||||||||AI|||20260420094500||||||20260424161000
PV2|||^Community acquired pneumonia||||||||20260420|||||||20260426|||||N
DG1|1|I10|J18.9^Pneumonia, unspecified organism^ICD10|||A
DG1|2|I10|J96.00^Acute respiratory failure, unspecified whether with hypoxia or hypercapnia^ICD10|||S
DG1|3|I10|E11.9^Type 2 diabetes mellitus without complications^ICD10|||S
```

---

## 7. ORU^R01 - Pathology report with embedded PDF (ED datatype) from OSU Wexner

```
MSH|^~\&|EPICCARE|OSUWMC|RECEIVING|PATHSYS|20260425103022||ORU^R01^ORU_R01|MSG20260425103022007|P|2.5.1|||AL|NE
PID|1||MRN9912345^^^OSUWMC^MR||Ruiz^Isabel^Carmen^^Mrs.^||19640427|F||2106-3^White^CDCREC|2001 Kenny Rd^^Columbus^OH^43210^US^H||^PRN^PH^^^614^8827493||SPA|M|CAT|ACCT70045678^^^OSUWMC^AN|517-38-9241|||N
PV1|1|I|7SOUTH^7405^A^OSUWMC^^^^7SOUTH|||4918273^Abernathy^Thanh^V^^^MD^^^NPI||||SUR||||7|||4918273^Abernathy^Thanh^V^^^MD^^^NPI|IN||BCBS
ORC|RE|ORD20260424001|FIL20260425001||CM||||20260424120000|||4918273^Abernathy^Thanh^V^^^MD^^^NPI
OBR|1|ORD20260424001|FIL20260425001|88305^Surgical Pathology^CPT4|||20260424120000|||||||||4918273^Abernathy^Thanh^V^^^MD^^^NPI||||||20260425103000|||F
OBX|1|TX|22634-0^Pathology report.final^LN||SURGICAL PATHOLOGY REPORT~Patient: Ruiz, Isabel C.~MRN: 9912345~DOB: 04/27/1964~Specimen: Left breast, lumpectomy~Clinical History: Left breast mass identified on screening mammography~Gross Description: Received fresh in the OR, a lumpectomy specimen measuring 6.2 x 4.8 x 3.1 cm weighing 48g.~The specimen is inked: superior-blue, inferior-green, medial-red, lateral-black.~Serially sectioned to reveal a firm, stellate, tan-white mass measuring 1.8 x 1.5 x 1.4 cm.~Microscopic Description: Sections show invasive ductal carcinoma, moderately differentiated.~Nottingham Grade: 2 (tubule formation 3, nuclear pleomorphism 2, mitotic count 1).~Margins: All surgical margins are negative. Closest margin (inferior) is 0.4 cm.~Lymphovascular invasion: Not identified.~DCIS: Present, solid and cribriform patterns, nuclear grade 2, involving <25% of tumor.~DIAGNOSIS: Left breast, lumpectomy - Invasive ductal carcinoma, moderately differentiated, 1.8 cm, margins negative.||||||F|||20260425103000
OBX|2|ED|PDF^Pathology Report PDF^LOCAL||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyMzQgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihTdXJnaWNhbCBQYXRob2xvZ3kgUmVwb3J0KSBUagowIC0yMCBUZAooUGF0aWVudDogUnVpeiwgSXNhYmVsIEMuKSBUagowIC0yMCBUZAooTVJOOiA5OTEyMzQ1KSBUagowIC0yMCBUZAooRE9COiAwNC8yNy8xOTY0KSBUagowIC0yMCBUZAooRGlhZ25vc2lzOiBJbnZhc2l2ZSBkdWN0YWwgY2FyY2lub21hKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iago=||||||F|||20260425103000
```

---

## 8. MDM^T02 - Discharge summary document from OhioHealth Grant

```
MSH|^~\&|EPIC|OHIOHEALTH|DOCMGMT|EXTAPP|20260426080145||MDM^T02^MDM_T02|MSG20260426080145008|P|2.5|||AL|NE
EVN|T02|20260426080100
PID|1||MRN1123456^^^OHHLTH^MR||Pemberton^Patricia^Elaine^^Ms.^||19480915|F||2106-3^White^CDCREC|2300 W Broad St^^Columbus^OH^43204^US^H||^PRN^PH^^^614^7729318||ENG|W|MET|ACCT80056789^^^OHHLTH^AN|318-47-6529|||N
PV1|1|I|4MED^4112^A^OHGRANT^^^^4MED|||7184293^Douglas^William^R^^^MD^^^NPI||||MED||||7|||7184293^Douglas^William^R^^^MD^^^NPI|IN||MCARE
TXA|1|DS^Discharge Summary^DOCTYPES|TX|20260426080000||20260426080000|||||7184293^Douglas^William^R^^^MD^^^NPI||DOC20260426001||||AU
OBX|1|TX|18842-5^Discharge Summary^LN||DISCHARGE SUMMARY~Patient: Pemberton, Patricia E.~MRN: 1123456~Admission Date: 04/20/2026~Discharge Date: 04/26/2026~Attending: William R. Douglas, MD~Principal Diagnosis: Acute exacerbation of COPD (J44.1)~Secondary Diagnoses: Chronic obstructive pulmonary disease (J44.9), Hypertension (I10), Atrial fibrillation (I48.91)~Hospital Course: 76-year-old female admitted with 3-day history of worsening dyspnea, productive cough with purulent sputum. Started on IV methylprednisolone, nebulized albuterol/ipratropium, azithromycin. Oxygen requirements peaked at 4L NC on day 2. Gradually improved and weaned to room air by day 5. Spirometry pre-discharge: FEV1 1.2L (58% predicted). Transitioned to oral prednisone taper.~Medications at Discharge: Prednisone 40mg daily x5 days then taper, Albuterol MDI 2 puffs q4h PRN, Tiotropium 18mcg inhaled daily, Lisinopril 10mg daily, Apixaban 5mg BID, Metoprolol succinate 50mg daily.~Follow-up: Pulmonology in 2 weeks, PCP in 1 week.~Disposition: Home with home health services.||||||F|||20260426080000
```

---

## 9. VXU^V04 - Immunization update for pediatric patient at Nationwide Children's

```
MSH|^~\&|EPIC|NCHCOLUMBUS|OHIMMREG|STATEIMM|20260427141500||VXU^V04^VXU_V04|MSG20260427141500009|P|2.5.1|||AL|NE
PID|1||MRN3345678^^^NCH^MR||Novotny^Sophia^Claire^^||20240115|F||2106-3^White^CDCREC|4567 Sawmill Rd^^Dublin^OH^43016^US^H||^PRN^PH^^^614^8819427||ENG||||ACCT90067890^^^NCH^AN||||N
NK1|1|Novotny^Daniel^J^^Mr.^||4567 Sawmill Rd^^Dublin^OH^43016^US|^PRN^PH^^^614^8819427||FTH^Father^HL70063
NK1|2|Novotny^Catherine^L^^Mrs.^||4567 Sawmill Rd^^Dublin^OH^43016^US|^PRN^PH^^^614^8819428||MTH^Mother^HL70063
PV1|1|O|PED^PED03^1^NCH^^^^PED|||8471293^Ramachandran^Amanda^J^^^MD^^^NPI||||PED||||7|||8471293^Ramachandran^Amanda^J^^^MD^^^NPI|OP||ANTHEM
ORC|RE|ORD20260427001||||||1|||8471293^Ramachandran^Amanda^J^^^MD^^^NPI
RXA|0|1|20260427141000|20260427141005|20^DTaP^CVX|0.5|mL|IM|LA^Left Arm^HL70163||||||W3456AA|20271231|SKB^GlaxoSmithKline^MVX
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible-Medicaid/Medicaid Managed Care^HL70064||||||F
ORC|RE|ORD20260427002||||||1|||8471293^Ramachandran^Amanda^J^^^MD^^^NPI
RXA|0|1|20260427141200|20260427141205|133^PCV13^CVX|0.5|mL|IM|RA^Right Arm^HL70163||||||X7890BB|20270630|PFR^Pfizer^MVX
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible-Medicaid/Medicaid Managed Care^HL70064||||||F
ORC|RE|ORD20260427003||||||1|||8471293^Ramachandran^Amanda^J^^^MD^^^NPI
RXA|0|1|20260427141400|20260427141405|10^IPV^CVX|0.5|mL|IM|LA^Left Arm^HL70163||||||P4567CC|20280131|SPM^Sanofi Pasteur^MVX
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible-Medicaid/Medicaid Managed Care^HL70064||||||F
```

---

## 10. RDE^O11 - Pharmacy order for anticoagulation at UC Health

```
MSH|^~\&|EPIC|UCHEALTH|PHARMACY|RXSYS|20260428092300||RDE^O11^RDE_O11|MSG20260428092300010|P|2.5|||AL|NE
PID|1||MRN4456789^^^UCH^MR||Calloway^Robert^Franklin^^Mr.^||19510329|M||2106-3^White^CDCREC|1234 Vine St^^Cincinnati^OH^45202^US^H||^PRN^PH^^^513^6618293||ENG|M|PRE|ACCT10078901^^^UCH^AN|641-28-5739|||N
PV1|1|I|6CARD^6204^A^UCHMC^^^^6CARD|||9274183^Abramov^Sarah^E^^^MD^^^NPI||||CAR||||7|||9274183^Abramov^Sarah^E^^^MD^^^NPI|IN||HUMANA
AL1|1|DA|8163^Aspirin^RxNorm|MI|GI bleeding|20180412
ORC|NW|ORD20260428001|||||1^^^20260428100000^^S||20260428092300|RXCLERK||9274183^Abramov^Sarah^E^^^MD^^^NPI
RXE|1^^^20260428100000^^S|854238^Enoxaparin 80mg/0.8mL Injectable Solution^RxNorm||80|mg|SC^Subcutaneous^HL70162||N||1|SYR^Syringe^HL70292||9274183^Abramov^Sarah^E^^^MD^^^NPI||||854238^Enoxaparin 80mg/0.8mL^RxNorm
RXR|SC^Subcutaneous^HL70162|ABD^Abdomen^HL70163
OBX|1|NM|3173-2^aPTT in Blood by Coagulation assay^LN||34.2|seconds|25.0-36.0|N|||F|||20260428060000
OBX|2|NM|5902-2^Prothrombin time (PT)^LN||14.8|seconds|11.0-15.0|N|||F|||20260428060000
OBX|3|NM|6301-6^INR in Platelet poor plasma by Coagulation assay^LN||1.3||0.9-1.2|H|||F|||20260428060000
OBX|4|NM|26515-7^Platelets [#/volume] in Blood^LN||198|10*3/uL|150-400|N|||F|||20260428060000
```

---

## 11. ADT^A08 - Patient information update at Cleveland Clinic

```
MSH|^~\&|EPICADT|CCF|RECEIVING|EXTAPP|20260429110034||ADT^A08^ADT_A08|MSG20260429110034011|P|2.5.1|||AL|NE
EVN|A08|20260429110000|||REGCLERK
PID|1||MRN4419523^^^CCF^MR~371-52-8946^^^SSA^SS||Kowalczyk^Brenda^Lucille^^Mrs.^||19680314|F||2106-3^White^CDCREC|2145 Euclid Ave^^Cleveland^OH^44115^US^H~890 Carnegie Ave Apt 5^^Cleveland^OH^44114^US^M||^PRN^PH^^^216^5529847~^PRN^CP^^^216^7713829~^NET^Internet^b.kowalczyk.new@email.com||ENG|M|CHR|ACCT10045678^^^CCF^AN|371-52-8946|||N||||20260429
PD1|||Cleveland Clinic Main Campus^^^CCF||||||||N
NK1|1|Kowalczyk^Walter^R^^Mr.^||890 Carnegie Ave Apt 5^^Cleveland^OH^44114^US|^PRN^PH^^^216^7713830||SPO^Spouse^HL70063
PV1|1|I|5EAST^5102^A^CCF^^^^5EAST|||1482937^Okafor^Raymond^B^^^MD^^^NPI|9174628^Tran^Michelle^L^^^MD^^^NPI||MED||||7|||1482937^Okafor^Raymond^B^^^MD^^^NPI|IN||BCBS|||||||||||||||AI|||20260415083000
IN1|1|001|BCBS001^BlueCross BlueShield of Ohio|Blue Cross Blue Shield^^Independence^OH^44131|^PRN^PH^^^800^2232273|||||GRP445566||FULLTIME|||Kowalczyk^Brenda^Lucille|SEL|19680314|890 Carnegie Ave Apt 5^^Cleveland^OH^44114||1|||||||||||||POL778899||||||F
```

---

## 12. DFT^P03 - Charge posting for cardiac catheterization at OhioHealth

```
MSH|^~\&|EPIC|OHIOHEALTH|BILLING|FINSYS|20260430143500||DFT^P03^DFT_P03|MSG20260430143500012|P|2.4|||AL|NE
EVN|P03|20260430143500
PID|1||MRN6645234^^^OHHLTH^MR||Gutierrez^Roberto^Alejandro^^Mr.^||19720619|M||2131-1^Other Race^CDCREC|890 Livingston Ave^^Columbus^OH^43205^US^H||^PRN^PH^^^614^8813729||SPA|M|CAT|ACCT50023456^^^OHHLTH^AN|742-18-3956|||H
PV1|1|I|CATH^CATH01^1^OHHLTH^^^^CATH|||7382915^Nwosu^Patricia^S^^^MD^^^NPI||||CAR||||7|||7382915^Nwosu^Patricia^S^^^MD^^^NPI|IN||ANTHEM
FT1|1|20260430|20260430143000|P|C|93458^Left heart catheterization^CPT4||1|||5200.00|||||CATH^CATH01^1^OHHLTH|7382915^Nwosu^Patricia^S^^^MD^^^NPI||I25.10^Atherosclerotic heart disease^ICD10
FT1|2|20260430|20260430143000|P|C|93571^Intravascular Doppler flow velocity^CPT4||1|||1800.00|||||CATH^CATH01^1^OHHLTH|7382915^Nwosu^Patricia^S^^^MD^^^NPI||I25.10^Atherosclerotic heart disease^ICD10
FT1|3|20260430|20260430143000|P|C|C1725^Catheter, transluminal angioplasty, non-laser^HCPCS||2|||950.00|||||CATH^CATH01^1^OHHLTH|7382915^Nwosu^Patricia^S^^^MD^^^NPI||I25.10^Atherosclerotic heart disease^ICD10
FT1|4|20260430|20260430143000|P|C|C1874^Stent, coated/covered, with delivery system^HCPCS||2|||6400.00|||||CATH^CATH01^1^OHHLTH|7382915^Nwosu^Patricia^S^^^MD^^^NPI||I25.10^Atherosclerotic heart disease^ICD10
DG1|1|I10|I25.10^Atherosclerotic heart disease of native coronary artery without angina pectoris^ICD10|||A
IN1|1|001|ANTH001^Anthem Blue Cross Blue Shield|Anthem BCBS^^Indianapolis^IN^46204|^PRN^PH^^^800^3311476|||||GRP334455||FULLTIME|||Gutierrez^Roberto^Alejandro|SEL|19720619|890 Livingston Ave^^Columbus^OH^43205||1|||||||||||||POL556677||||||M
```

---

## 13. ADT^A02 - Patient transfer at ProMedica Flower Hospital Toledo

```
MSH|^~\&|EPICADT|PROMFLWR|RECEIVING|EXTAPP|20260501091245||ADT^A02^ADT_A02|MSG20260501091245013|P|2.4|||AL|NE
EVN|A02|20260501091200|||NRSUNIT
PID|1||MRN7756789^^^PROM^MR||Desai^Arun^Vikram^^Mr.^||19780414|M||2028-9^Asian^CDCREC|3456 Sylvania Ave^^Toledo^OH^43623^US^H||^PRN^PH^^^419^6619284~^PRN^CP^^^419^7713829||HIN|M|HIN|ACCT20089012^^^PROM^AN|825-14-3967|||N
PV1|1|I|ICU^ICU03^A^PROMFLWR^^^^ICU|U||0184729^Henderson^Jonathan^M^^^MD^^^NPI|1293847^Volkov^Priya^R^^^MD^^^NPI||MED||||7|||0184729^Henderson^Jonathan^M^^^MD^^^NPI|IN||CIGNA||||||||||||||5NORTH^5202^B^PROMFLWR^^^^5NORTH|AI|||20260428150000
PV2|||^Sepsis secondary to urinary tract infection||||||||20260428|||||||||||||||ICU^ICU03^A|5NORTH^5202^B
DG1|1|I10|A41.9^Sepsis, unspecified organism^ICD10|||A
DG1|2|I10|N39.0^Urinary tract infection, site not specified^ICD10|||S
```

---

## 14. ORU^R01 - Microbiology culture results from Cleveland Clinic

```
MSH|^~\&|EPICCARE|CCF|RECEIVING|LABSYS|20260502074530||ORU^R01^ORU_R01|MSG20260502074530014|P|2.5.1|||AL|NE
PID|1||MRN8867890^^^CCF^MR||Driscoll^Thomas^Wayne^^Mr.^||19450718|M||2106-3^White^CDCREC|7890 Cedar Rd^^Cleveland Heights^OH^44118^US^H||^PRN^PH^^^216^9914827||ENG|M|PRE|ACCT30090123^^^CCF^AN|493-17-8264|||N
PV1|1|I|8WEST^8310^A^CCF^^^^8WEST|||2847193^Fitzgerald^Patrick^J^^^MD^^^NPI||||MED||||7|||2847193^Fitzgerald^Patrick^J^^^MD^^^NPI|IN||MCARE
ORC|RE|ORD20260430001|FIL20260502001||CM||||20260430140000|||2847193^Fitzgerald^Patrick^J^^^MD^^^NPI
OBR|1|ORD20260430001|FIL20260502001|87070^Culture, bacterial, any source^CPT4|||20260430140000|||||||||2847193^Fitzgerald^Patrick^J^^^MD^^^NPI||||||20260502074500|||F
OBX|1|CE|600-7^Bacteria identified in Blood by Culture^LN||112283007^Escherichia coli^SCT||||||F|||20260502074500
OBX|2|TX|19156-3^Comment^LN||BLOOD CULTURE - FINAL RESULT~Specimen: Blood, venipuncture, right antecubital~Collected: 04/30/2026 14:00~Gram Stain: Gram negative rods~Aerobic Culture: Escherichia coli isolated after 18 hours incubation.~Colony count: >100,000 CFU/mL||||||F|||20260502074500
OBX|3|CE|18907-6^Ampicillin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||R^Resistant^HL70078|ug/mL|||||F|||20260502074500
OBX|4|CE|18928-2^Gentamicin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||S^Susceptible^HL70078|ug/mL|||||F|||20260502074500
OBX|5|CE|18932-4^Ciprofloxacin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||S^Susceptible^HL70078|ug/mL|||||F|||20260502074500
OBX|6|CE|18964-7^Ceftriaxone [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||S^Susceptible^HL70078|ug/mL|||||F|||20260502074500
OBX|7|CE|18993-6^Trimethoprim+Sulfamethoxazole [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||R^Resistant^HL70078|ug/mL|||||F|||20260502074500
OBX|8|CE|18878-9^Cefazolin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||S^Susceptible^HL70078|ug/mL|||||F|||20260502074500
OBX|9|CE|20629-2^Levofloxacin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||S^Susceptible^HL70078|ug/mL|||||F|||20260502074500
OBX|10|CE|18961-3^Piperacillin+Tazobactam [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||S^Susceptible^HL70078|ug/mL|||||F|||20260502074500
```

---

## 15. ADT^A28 - New person registration (MPI) at UC Health

```
MSH|^~\&|BRIDGES|UCHEALTH|EMPI|MPISYS|20260503120045||ADT^A28^ADT_A28|MSG20260503120045015|P|2.5|||AL|NE
EVN|A28|20260503120000|||MPICLERK
PID|1||MRN1234567^^^UCH^MR~EMPI9988776^^^UCEMPI^PI||Ferreira^Maria^Cristina^^Mrs.^||19830611|F||2106-3^White^CDCREC|5678 Glenway Ave^^Cincinnati^OH^45238^US^H||^PRN^PH^^^513^6619274~^PRN^CP^^^513^8817293~^NET^Internet^mc.ferreira@email.com||POR|M|CAT|ACCT40001234^^^UCH^AN|714-29-3856|||N||||20260503
PD1|||UC Health West Chester^^^UCH||||||||N
NK1|1|Ferreira^Eduardo^P^^Mr.^||5678 Glenway Ave^^Cincinnati^OH^45238^US|^PRN^PH^^^513^6619275||SPO^Spouse^HL70063
```

---

## 16. ADT^A31 - Patient update in master patient index at OhioHealth

```
MSH|^~\&|BRIDGES|OHIOHEALTH|EMPI|MPISYS|20260504083012||ADT^A31^ADT_A31|MSG20260504083012016|P|2.5|||AL|NE
EVN|A31|20260504083000|||MPIUPDATE
PID|1||MRN5567123^^^OHHLTH^MR~EMPI4455667^^^OHEMPI^PI||Odum^Marcus^Reginald^^Mr.^Jr.||19950202|M||2054-5^Black or African American^CDCREC|1234 E Main St^^Columbus^OH^43205^US^H||^PRN^PH^^^614^7728193~^PRN^CP^^^614^9913847~^NET^Internet^marcus.odum95@email.com||ENG|S|BAP|ACCT50012345^^^OHHLTH^AN|529-17-4863|||N||||20260504
PD1|||OhioHealth Primary Care Westerville^^^OHHLTH||||||||N
NK1|1|Odum^Angela^M^^Mrs.^||7890 Sunbury Rd^^Westerville^OH^43081^US|^PRN^PH^^^614^8814729||MTH^Mother^HL70063
IN1|1|001|ANTH001^Anthem Blue Cross Blue Shield|Anthem BCBS^^Indianapolis^IN^46204|^PRN^PH^^^800^3311476|||||GRP556677||FULLTIME|||Odum^Marcus^Reginald|SEL|19950202|1234 E Main St^^Columbus^OH^43205||1|||||||||||||POL887799||||||M
IN1|2|002|DELTA01^Delta Dental of Ohio|Delta Dental^^Alpharetta^GA^30009|^PRN^PH^^^800^5242149|||||GRP556677||FULLTIME|||Odum^Marcus^Reginald|SEL|19950202|1234 E Main St^^Columbus^OH^43205||2|||||||||||||DEN445566||||||M
```

---

## 17. ORU^R01 - Radiology report with embedded CDA document (ED datatype) from ProMedica

```
MSH|^~\&|EPICCARE|PROMEDICA|RECEIVING|RADSYS|20260505111500||ORU^R01^ORU_R01|MSG20260505111500017|P|2.5.1|||AL|NE
PID|1||MRN8834567^^^PROM^MR||Harding^Denise^Yvonne^^Mrs.^||19560212|F||2054-5^Black or African American^CDCREC|1523 Monroe St^^Toledo^OH^43604^US^H||^PRN^PH^^^419^6627381||ENG|W|BAP|ACCT40012398^^^PROM^AN|638-27-4015|||N
PV1|1|O|RADOL^RAD02^1^PROM^^^^RADOL|||5294837^Lindstrom^Gregory^W^^^MD^^^NPI||||RAD||||7|||5294837^Lindstrom^Gregory^W^^^MD^^^NPI|OP||UHCOH
ORC|RE|ORD20260422001|FIL20260505001||CM||||20260423080000|||5294837^Lindstrom^Gregory^W^^^MD^^^NPI
OBR|1|ORD20260422001|FIL20260505001|71260^CT CHEST WITH CONTRAST^CPT4|||20260423083000|||||||||5294837^Lindstrom^Gregory^W^^^MD^^^NPI||||||20260505111400|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||CT CHEST WITH CONTRAST~Date: 04/23/2026~Clinical Indication: Persistent cough, weight loss, evaluate for pulmonary mass.~Technique: Helical CT of the chest was performed following administration of 100mL Omnipaque 350 IV contrast.~Comparison: Chest X-ray dated 04/10/2026.~Findings:~Lungs: There is a 2.3 x 1.8 cm spiculated mass in the right upper lobe (series 4, image 67). Mild surrounding ground-glass opacity suggests a component of lepidic growth. No additional pulmonary nodules identified. No pleural effusion. Airways are patent to the segmental level.~Mediastinum: No pathologically enlarged mediastinal or hilar lymph nodes. The largest subcarinal node measures 0.9 cm in short axis. Heart size is normal. No pericardial effusion.~Bones: Mild degenerative changes of the thoracic spine. No suspicious osseous lesions.~Impression:~1. 2.3 cm spiculated right upper lobe mass, highly suspicious for primary lung malignancy. Recommend PET/CT and tissue sampling.~2. No mediastinal lymphadenopathy by CT size criteria.||||||F|||20260505111400
OBX|2|ED|CDA^Radiology Report CDA^LOCAL||^text^xml^Base64^PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIj4KICA8cmVhbG1Db2RlIGNvZGU9IlVTIi8+CiAgPHR5cGVJZCByb290PSIyLjE2Ljg0MC4xLjExMzg4My4xLjMiIGV4dGVuc2lvbj0iUE9DRF9IRDA1MDAwMCIvPgogIDx0ZW1wbGF0ZUlkIHJvb3Q9IjIuMTYuODQwLjEuMTEzODgzLjEwLjIwLjIyLjIuMSIvPgogIDxpZCByb290PSIyLjE2Ljg0MC4xLjExMzg4My4xOS41Ljk5OTk5LjEiIGV4dGVuc2lvbj0iUkFEMjAyNjA1MDUwMDEiLz4KICA8Y29kZSBjb2RlPSIxODc0OC00IiBjb2RlU3lzdGVtPSIyLjE2Ljg0MC4xLjExMzg4My42LjEiIGRpc3BsYXlOYW1lPSJEaWFnbm9zdGljIEltYWdpbmcgUmVwb3J0Ii8+CiAgPHRpdGxlPkNUIENoZXN0IHdpdGggQ29udHJhc3QgLSBGaW5hbCBSZXBvcnQ8L3RpdGxlPgogIDxlZmZlY3RpdmVUaW1lIHZhbHVlPSIyMDI2MDUwNTExMTQwMCIvPgogIDxyZWNvcmRUYXJnZXQ+CiAgICA8cGF0aWVudFJvbGU+CiAgICAgIDxpZCByb290PSIyLjE2Ljg0MC4xLjExMzg4My4xOS41Ljk5OTk5LjIiIGV4dGVuc2lvbj0iTVJOODgzNDU2NyIvPgogICAgICA8cGF0aWVudD4KICAgICAgICA8bmFtZT48Z2l2ZW4+RGVuaXNlPC9naXZlbj48ZmFtaWx5PkhhcmRpbmc8L2ZhbWlseT48L25hbWU+CiAgICAgIDwvcGF0aWVudD4KICAgIDwvcGF0aWVudFJvbGU+CiAgPC9yZWNvcmRUYXJnZXQ+CiAgPGNvbXBvbmVudD4KICAgIDxzdHJ1Y3R1cmVkQm9keT4KICAgICAgPGNvbXBvbmVudD4KICAgICAgICA8c2VjdGlvbj4KICAgICAgICAgIDx0aXRsZT5JbXByZXNzaW9uPC90aXRsZT4KICAgICAgICAgIDx0ZXh0PlNwaWN1bGF0ZWQgUlVMIG1hc3MsIGhpZ2hseSBzdXNwaWNpb3VzIGZvciBwcmltYXJ5IGx1bmcgbWFsaWduYW5jeS48L3RleHQ+CiAgICAgICAgPC9zZWN0aW9uPgogICAgICA8L2NvbXBvbmVudD4KICAgIDwvc3RydWN0dXJlZEJvZHk+CiAgPC9jb21wb25lbnQ+CjwvQ2xpbmljYWxEb2N1bWVudD4K||||||F|||20260505111400
```

---

## 18. ORM^O01 - Laboratory order panel from Summa Health Akron

```
MSH|^~\&|EPIC|SUMMAHEALTH|LABIS|LABSYS|20260506063000||ORM^O01^ORM_O01|MSG20260506063000018|P|2.4|||AL|NE
PID|1||MRN2245678^^^SUMMA^MR||Park^Jennifer^Min-Young^^Ms.^||19880725|F||2028-9^Asian^CDCREC|2345 W Market St^^Akron^OH^44313^US^H||^PRN^PH^^^330^7718293~^PRN^CP^^^330^9917482||KOR|S|BUD|ACCT60023456^^^SUMMA^AN|482-61-7935|||N
PV1|1|I|3MED^3106^A^SUMMA^^^^3MED|||3819274^Mbeki^Christopher^D^^^MD^^^NPI||||MED||||7|||3819274^Mbeki^Christopher^D^^^MD^^^NPI|IN||MEDICAL_MUTUAL
ORC|NW|ORD20260506001||||||1^^^20260506070000^^R||20260506063000|LABCLERK||3819274^Mbeki^Christopher^D^^^MD^^^NPI
OBR|1|ORD20260506001||80053^Comprehensive Metabolic Panel^CPT4|||20260506070000||||N|||||3819274^Mbeki^Christopher^D^^^MD^^^NPI
DG1|1|I10|N18.3^Chronic kidney disease, stage 3 (moderate)^ICD10|||A
ORC|NW|ORD20260506002||||||1^^^20260506070000^^R||20260506063000|LABCLERK||3819274^Mbeki^Christopher^D^^^MD^^^NPI
OBR|2|ORD20260506002||83036^Hemoglobin A1c^CPT4|||20260506070000||||N|||||3819274^Mbeki^Christopher^D^^^MD^^^NPI
DG1|1|I10|E11.65^Type 2 diabetes mellitus with hyperglycemia^ICD10|||A
ORC|NW|ORD20260506003||||||1^^^20260506070000^^R||20260506063000|LABCLERK||3819274^Mbeki^Christopher^D^^^MD^^^NPI
OBR|3|ORD20260506003||83615^Lactate dehydrogenase (LDH)^CPT4|||20260506070000||||N|||||3819274^Mbeki^Christopher^D^^^MD^^^NPI
```

---

## 19. ORU^R01 - Comprehensive metabolic panel results from Summa Health Akron

```
MSH|^~\&|EPICCARE|SUMMAHEALTH|RECEIVING|LABSYS|20260506101200||ORU^R01^ORU_R01|MSG20260506101200019|P|2.5.1|||AL|NE
PID|1||MRN2245678^^^SUMMA^MR||Park^Jennifer^Min-Young^^Ms.^||19880725|F||2028-9^Asian^CDCREC|2345 W Market St^^Akron^OH^44313^US^H||^PRN^PH^^^330^7718293||KOR|S|BUD|ACCT60023456^^^SUMMA^AN|482-61-7935|||N
PV1|1|I|3MED^3106^A^SUMMA^^^^3MED|||3819274^Mbeki^Christopher^D^^^MD^^^NPI||||MED||||7|||3819274^Mbeki^Christopher^D^^^MD^^^NPI|IN||MEDICAL_MUTUAL
ORC|RE|ORD20260506001|FIL20260506001||CM||||20260506070000|||3819274^Mbeki^Christopher^D^^^MD^^^NPI
OBR|1|ORD20260506001|FIL20260506001|80053^Comprehensive Metabolic Panel^CPT4|||20260506070500|||||||||3819274^Mbeki^Christopher^D^^^MD^^^NPI||||||20260506101100|||F
OBX|1|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||142|mg/dL|74-106|H|||F|||20260506101100
OBX|2|NM|3094-0^Urea nitrogen [Mass/volume] in Serum or Plasma^LN||28|mg/dL|6-20|H|||F|||20260506101100
OBX|3|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||1.8|mg/dL|0.6-1.2|H|||F|||20260506101100
OBX|4|NM|33914-3^Glomerular filtration rate/1.73 sq M.predicted^LN||38|mL/min/1.73m2|>60|L|||F|||20260506101100
OBX|5|NM|2951-2^Sodium [Moles/volume] in Serum or Plasma^LN||139|mmol/L|136-145|N|||F|||20260506101100
OBX|6|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN||4.8|mmol/L|3.5-5.1|N|||F|||20260506101100
OBX|7|NM|2075-0^Chloride [Moles/volume] in Serum or Plasma^LN||101|mmol/L|98-106|N|||F|||20260506101100
OBX|8|NM|2028-9^Carbon dioxide, total [Moles/volume] in Serum or Plasma^LN||22|mmol/L|20-29|N|||F|||20260506101100
OBX|9|NM|17861-6^Calcium [Mass/volume] in Serum or Plasma^LN||9.4|mg/dL|8.5-10.5|N|||F|||20260506101100
OBX|10|NM|2885-2^Protein [Mass/volume] in Serum or Plasma^LN||7.1|g/dL|6.0-8.3|N|||F|||20260506101100
OBX|11|NM|1751-7^Albumin [Mass/volume] in Serum or Plasma^LN||3.8|g/dL|3.5-5.5|N|||F|||20260506101100
OBX|12|NM|1975-2^Bilirubin.total [Mass/volume] in Serum or Plasma^LN||0.8|mg/dL|0.1-1.2|N|||F|||20260506101100
OBX|13|NM|6768-6^Alkaline phosphatase [Enzymatic activity/volume] in Serum or Plasma^LN||72|U/L|44-147|N|||F|||20260506101100
OBX|14|NM|1742-6^Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||24|U/L|7-56|N|||F|||20260506101100
```

---

## 20. ORU^R01 - Hemoglobin A1c result from Summa Health Akron

```
MSH|^~\&|EPICCARE|SUMMAHEALTH|RECEIVING|LABSYS|20260506101500||ORU^R01^ORU_R01|MSG20260506101500020|P|2.5.1|||AL|NE
PID|1||MRN2245678^^^SUMMA^MR||Park^Jennifer^Min-Young^^Ms.^||19880725|F||2028-9^Asian^CDCREC|2345 W Market St^^Akron^OH^44313^US^H||^PRN^PH^^^330^7718293||KOR|S|BUD|ACCT60023456^^^SUMMA^AN|482-61-7935|||N
PV1|1|I|3MED^3106^A^SUMMA^^^^3MED|||3819274^Mbeki^Christopher^D^^^MD^^^NPI||||MED||||7|||3819274^Mbeki^Christopher^D^^^MD^^^NPI|IN||MEDICAL_MUTUAL
ORC|RE|ORD20260506002|FIL20260506002||CM||||20260506070000|||3819274^Mbeki^Christopher^D^^^MD^^^NPI
OBR|1|ORD20260506002|FIL20260506002|83036^Hemoglobin A1c^CPT4|||20260506070500|||||||||3819274^Mbeki^Christopher^D^^^MD^^^NPI||||||20260506101400|||F
OBX|1|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN||8.2|%|<5.7|H|||F|||20260506101400
OBX|2|NM|27353-2^Glucose mean value [Mass/volume] in Blood Estimated from glycated hemoglobin^LN||189|mg/dL|||||F|||20260506101400
NTE|1|L|HbA1c of 8.2% corresponds to estimated average glucose of 189 mg/dL. Target for most adults with diabetes is <7.0%. Consider intensification of therapy.
```
