# Epic (Bridges) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to Hospital of the University of Pennsylvania

```
MSH|^~\&|EPICADT|HUP|RECEIVING|EXTAPP|20260502083045||ADT^A01^ADT_A01|MSG20260502083045001|P|2.5.1|||AL|NE
EVN|A01|20260502083000|||JKRAWCZYK^Krawczyk^Joanna^M^^^MD
PID|1||MRN6612345^^^HUP^MR~482-71-3906^^^SSA^SS||Fitzpatrick^Erin^Colleen^^Mrs.^||19710218|F||2106-3^White^CDCREC|1847 Pine St Apt 4B^^Philadelphia^PA^19103^US^H||^PRN^PH^^^215^6829341~^NET^Internet^erin.fitzpatrick@email.com||ENG|M|CHR|ACCT80012345^^^HUP^AN|482-71-3906|||N||||20260502
PD1|||Hospital of the University of Pennsylvania^^^HUP||||||||N
NK1|1|Fitzpatrick^Sean^Patrick^^Mr.^||1847 Pine St Apt 4B^^Philadelphia^PA^19103^US|^PRN^PH^^^215^6829342||SPO^Spouse^HL70063
NK1|2|Fitzpatrick^Bridget^Anne^^Ms.^||2310 Lombard St^^Philadelphia^PA^19146^US|^PRN^PH^^^215^7934518||SIS^Sister^HL70063
PV1|1|I|6SOUTH^6204^A^HUP^^^^6SOUTH|||1834521^Caruso^Gianna^L^^^MD^^^NPI|2947613^Banerjee^Arun^S^^^MD^^^NPI||MED||||7|||1834521^Caruso^Gianna^L^^^MD^^^NPI|IN||IBCBS|||||||||||||||AI|||20260502083000
PV2|||^Worsening dyspnea on exertion, bilateral lower extremity edema||||||20260502|||||||||||||N
DG1|1|I10|I50.33^Acute on chronic diastolic heart failure^ICD10|||A
DG1|2|I10|I10^Essential (primary) hypertension^ICD10|||S
AL1|1|DA|70618^Penicillin^RxNorm|MO|Hives and facial swelling|20080315
AL1|2|DA|2670^Codeine^RxNorm|MI|Nausea|20150722
IN1|1|001|IBCBS001^Independence Blue Cross|Independence Blue Cross^^Philadelphia^PA^19103|^PRN^PH^^^800^2753242|||||GRP667788||FULLTIME|||Fitzpatrick^Erin^Colleen|SEL|19710218|1847 Pine St Apt 4B^^Philadelphia^PA^19103||1|||||||||||||POL889900||||||F
IN1|2|002|AETNA01^Aetna|Aetna Insurance^^Hartford^CT^06156|^PRN^PH^^^800^8721862|||||GRP223344||FULLTIME|||Fitzpatrick^Erin^Colleen|SEL|19710218|1847 Pine St Apt 4B^^Philadelphia^PA^19103||2|||||||||||||POL556677||||||F
GT1|1||Fitzpatrick^Erin^Colleen^^Mrs.^|1847 Pine St Apt 4B^^Philadelphia^PA^19103^US|^PRN^PH^^^215^6829341|^PRN^PH^^^215^6829342|19710218|F||SEL|482-71-3906
```

---

## 2. ADT^A04 - Emergency department registration at UPMC Presbyterian

```
MSH|^~\&|EPICADT|UPMCPRESBY|RECEIVING|EXTAPP|20260503144512||ADT^A04^ADT_A04|MSG20260503144512002|P|2.5|||AL|NE
EVN|A04|20260503144500|||EDREGISTRAR
PID|1||MRN7734567^^^UPMC^MR||Jackson^Terrence^Lamar^^Mr.^||19870613|M||2054-5^Black or African American^CDCREC|2714 Centre Ave Apt 8^^Pittsburgh^PA^15213^US^H||^PRN^PH^^^412^7623891~^PRN^CP^^^412^9457712||ENG|S|NON|ACCT30067890^^^UPMC^AN|518-42-9037|||N||||20260503
NK1|1|Jackson^Diane^Renee^^Mrs.^||1842 Penn Ave^^Pittsburgh^PA^15222^US|^PRN^PH^^^412^6832234||MTH^Mother^HL70063
PV1|1|E|EMED^ER08^A^UPMCPRESBY^^^^EMED|||3519872^Kowalski^Thomas^J^^^MD^^^NPI||||EMR||||1|||3519872^Kowalski^Thomas^J^^^MD^^^NPI|EM||UPMCHP|||||||||||||||AA|||20260503144500
PV2|||^Acute onset chest pain radiating to left arm, diaphoresis||||||||||||||||||||N
DG1|1|I10|R07.9^Chest pain, unspecified^ICD10|||A
AL1|1|DA|8163^Aspirin^RxNorm|MI|GI bleeding|20190812
IN1|1|001|UPMCHP01^UPMC Health Plan|UPMC Health Plan^^Pittsburgh^PA^15222|^PRN^PH^^^888^8764357|||||GRP445566||FULLTIME|||Jackson^Terrence^Lamar|SEL|19870613|2714 Centre Ave Apt 8^^Pittsburgh^PA^15213||1|||||||||||||POL334455||||||M
```

---

## 3. ORU^R01 - Lab results with CBC panel from Geisinger Medical Center

```
MSH|^~\&|EPICCARE|GEISINGER|RECEIVING|LAB|20260504091230||ORU^R01^ORU_R01|MSG20260504091230003|P|2.5.1|||AL|NE
PID|1||MRN8845678^^^GMC^MR||Novak^Catherine^Theresa^^Mrs.^||19650822|F||2106-3^White^CDCREC|187 N Academy Ave^^Danville^PA^17822^US^H||^PRN^PH^^^570^4129421||ENG|M|LUT|ACCT40078901^^^GMC^AN|623-81-4907|||N
PV1|1|O|LABDRAW^LD01^1^GMC||||4081736^Hoffman^Daniel^M^^^MD^^^NPI||||LAB||||7|||4081736^Hoffman^Daniel^M^^^MD^^^NPI|OP||GEISINGERHP
ORC|RE|ORD20260504001|FIL20260504001||CM||||20260504080000|||4081736^Hoffman^Daniel^M^^^MD^^^NPI
OBR|1|ORD20260504001|FIL20260504001|57021-8^CBC W Auto Differential panel in Blood^LN|||20260504074500|||||||||4081736^Hoffman^Daniel^M^^^MD^^^NPI||||||20260504091200|||F
OBX|1|NM|6690-2^Leukocytes [#/volume] in Blood by Automated count^LN||6.8|10*3/uL|4.5-11.0|N|||F|||20260504091200
OBX|2|NM|789-8^Erythrocytes [#/volume] in Blood by Automated count^LN||4.42|10*6/uL|4.00-5.50|N|||F|||20260504091200
OBX|3|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||13.1|g/dL|12.0-16.0|N|||F|||20260504091200
OBX|4|NM|4544-3^Hematocrit [Volume Fraction] of Blood by Automated count^LN||39.8|%|36.0-46.0|N|||F|||20260504091200
OBX|5|NM|787-2^MCV [Entitic volume] by Automated count^LN||90.0|fL|80.0-100.0|N|||F|||20260504091200
OBX|6|NM|785-6^MCH [Entitic mass] by Automated count^LN||29.6|pg|27.0-33.0|N|||F|||20260504091200
OBX|7|NM|786-4^MCHC [Mass/volume] by Automated count^LN||32.9|g/dL|32.0-36.0|N|||F|||20260504091200
OBX|8|NM|788-0^Erythrocyte distribution width [Ratio] by Automated count^LN||12.8|%|11.5-14.5|N|||F|||20260504091200
OBX|9|NM|777-3^Platelets [#/volume] in Blood by Automated count^LN||218|10*3/uL|150-400|N|||F|||20260504091200
OBX|10|NM|770-8^Neutrophils/100 leukocytes in Blood by Automated count^LN||58.4|%|40.0-70.0|N|||F|||20260504091200
OBX|11|NM|736-9^Lymphocytes/100 leukocytes in Blood by Automated count^LN||31.2|%|20.0-40.0|N|||F|||20260504091200
OBX|12|NM|5905-5^Monocytes/100 leukocytes in Blood by Automated count^LN||6.9|%|2.0-8.0|N|||F|||20260504091200
OBX|13|NM|713-8^Eosinophils/100 leukocytes in Blood by Automated count^LN||2.8|%|1.0-4.0|N|||F|||20260504091200
OBX|14|NM|706-2^Basophils/100 leukocytes in Blood by Automated count^LN||0.7|%|0.0-1.0|N|||F|||20260504091200
```

---

## 4. ORM^O01 - Radiology order for MRI brain at Lehigh Valley Hospital

```
MSH|^~\&|EPIC|LVHN|RADIS|IMGCTR|20260505153012||ORM^O01^ORM_O01|MSG20260505153012004|P|2.4|||AL|NE
PID|1||MRN2256789^^^LVHN^MR||Castellano^Vincent^Anthony^^Mr.^||19530907|M||2106-3^White^CDCREC|1200 S Cedar Crest Blvd^^Allentown^PA^18103^US^H||^PRN^PH^^^610^4826734||ENG|M|CAT|ACCT50034567^^^LVHN^AN|741-58-2093|||N
PV1|1|O|RADOL^RAD04^1^LVHN^^^^RADOL|||5193847^Brennan^Michael^K^^^MD^^^NPI||||RAD||||7|||5193847^Brennan^Michael^K^^^MD^^^NPI|OP||IBCBS
IN1|1|001|IBCBS001^Independence Blue Cross|Independence Blue Cross^^Philadelphia^PA^19103|^PRN^PH^^^800^2753242|||||GRP998877||FULLTIME|||Castellano^Vincent^Anthony|SEL|19530907|1200 S Cedar Crest Blvd^^Allentown^PA^18103||1|||||||||||||POL112233||||||M
ORC|NW|ORD20260505001||||||1^^^20260506080000^^R||20260505153000|RADCLERK||5193847^Brennan^Michael^K^^^MD^^^NPI|RADOL|^PRN^PH^^^610^4028000||||||Lehigh Valley Hospital-Cedar Crest^1200 S Cedar Crest Blvd^^Allentown^PA^18103
OBR|1|ORD20260505001||70553^MRI BRAIN WITH AND WITHOUT CONTRAST^CPT4|||20260506080000||||N|||||5193847^Brennan^Michael^K^^^MD^^^NPI|||||||RAD||1^^^20260506080000^^R||||^New onset seizure activity, evaluate for intracranial pathology
DG1|1|I10|R56.9^Unspecified convulsions^ICD10|||A
DG1|2|I10|R51.9^Headache, unspecified^ICD10|||S
```

---

## 5. SIU^S12 - Appointment scheduled at Penn Medicine Cherry Hill

```
MSH|^~\&|EPIC|PENNMED|SCHEDULING|EXTAPP|20260506104530||SIU^S12^SIU_S12|MSG20260506104530005|P|2.5|||AL|NE
SCH|APPT20260520001|APPT20260520001|||ROUTINE^Routine^HL70276|FOLLOWUP^Follow Up Visit^APPTREAS||30|min|^^30^20260520100000^20260520103000|6274918^Okonkwo^Chidinma^N^^^MD^^^NPI|^PRN^PH^^^215^6625900|3400 Spruce St^^Philadelphia^PA^19104^^|||6274918^Okonkwo^Chidinma^N^^^MD^^^NPI||BOOKED
PID|1||MRN3345678^^^PENNMED^MR||Delgado^Maria^Guadalupe^^Mrs.^||19800425|F||2131-1^Other Race^CDCREC|2319 S Broad St^^Philadelphia^PA^19148^US^H||^PRN^PH^^^215^3947823~^PRN^CP^^^267^5021290||SPA|M|CAT|ACCT60045678^^^PENNMED^AN|831-46-7209|||H
PV1|1|O|ENDO^ENDO01^1^PENNMED^^^^ENDO|||6274918^Okonkwo^Chidinma^N^^^MD^^^NPI||||END||||7|||6274918^Okonkwo^Chidinma^N^^^MD^^^NPI|OP||IBCBS
RGS|1|A
AIS|1|A|ENDOFOLLOW^Endocrinology Follow Up^LOCAL|20260520100000|0|min|30|min
AIG|1|A|6274918^Okonkwo^Chidinma^N^^^MD^^^NPI
AIL|1|A|ENDO^ENDO01^1^PENNMED
```

---

## 6. ADT^A03 - Patient discharge from UPMC Shadyside

```
MSH|^~\&|EPICADT|UPMCSHADY|RECEIVING|EXTAPP|20260507161045||ADT^A03^ADT_A03|MSG20260507161045006|P|2.5.1|||AL|NE
EVN|A03|20260507161000|||DCCLERK
PID|1||MRN4456789^^^UPMC^MR||Kowalczyk^Stefan^Andrzej^^Mr.^||19580316|M||2106-3^White^CDCREC|5401 Walnut St^^Pittsburgh^PA^15232^US^H||^PRN^PH^^^412^6813378~^PRN^CP^^^412^9728845||POL|M|CAT|ACCT70056789^^^UPMC^AN|317-62-8904|||N
PV1|1|I|4WEST^4210^B^UPMCSHADY^^^^4WEST|||7261438^DiStefano^Anthony^R^^^MD^^^NPI|8394512^Tran^Linh^T^^^MD^^^NPI||MED||||7|||7261438^DiStefano^Anthony^R^^^MD^^^NPI|IN||UPMCHP|||||||||||||||AI|||20260503092000||||||20260507161000
PV2|||^Acute exacerbation of chronic obstructive pulmonary disease||||||||20260503|||||||20260509|||||N
DG1|1|I10|J44.1^Chronic obstructive pulmonary disease with acute exacerbation^ICD10|||A
DG1|2|I10|J96.00^Acute respiratory failure, unspecified whether with hypoxia or hypercapnia^ICD10|||S
DG1|3|I10|I48.91^Unspecified atrial fibrillation^ICD10|||S
```

---

## 7. ORU^R01 - Pathology report with embedded PDF (ED datatype) from Penn Medicine

```
MSH|^~\&|EPICCARE|HUP|RECEIVING|PATHSYS|20260508103045||ORU^R01^ORU_R01|MSG20260508103045007|P|2.5.1|||AL|NE
PID|1||MRN5567890^^^HUP^MR||Washington^Denise^Lorraine^^Mrs.^||19670512|F||2054-5^Black or African American^CDCREC|4200 Chester Ave^^Philadelphia^PA^19104^US^H||^PRN^PH^^^215^3924490||ENG|M|BAP|ACCT80067890^^^HUP^AN|429-63-8105|||N
PV1|1|I|8NORTH^8312^A^HUP^^^^8NORTH|||9517234^Mehta^Priya^K^^^MD^^^NPI||||SUR||||7|||9517234^Mehta^Priya^K^^^MD^^^NPI|IN||IBCBS
ORC|RE|ORD20260507001|FIL20260508001||CM||||20260507110000|||9517234^Mehta^Priya^K^^^MD^^^NPI
OBR|1|ORD20260507001|FIL20260508001|88305^Surgical Pathology^CPT4|||20260507110000|||||||||9517234^Mehta^Priya^K^^^MD^^^NPI||||||20260508103000|||F
OBX|1|TX|22634-0^Pathology report.final^LN||SURGICAL PATHOLOGY REPORT~Patient: Washington, Denise L.~MRN: 5567890~DOB: 05/12/1967~Specimen: Right colon, right hemicolectomy~Clinical History: Cecal mass identified on screening colonoscopy with biopsy showing adenocarcinoma~Gross Description: Received fresh, a right hemicolectomy specimen measuring 22.5 cm in length with an attached segment of terminal ileum measuring 5.8 cm. A firm, ulcerated mass is identified in the cecum measuring 4.2 x 3.8 x 2.1 cm. The mass penetrates through the muscularis propria into the pericolonic fat. Twenty-three lymph nodes are identified.~Microscopic Description: Sections show moderately differentiated adenocarcinoma arising in the cecum. Tumor invades through muscularis propria into pericolonic adipose tissue (pT3). Lymphovascular invasion present. Perineural invasion not identified. Margins: Proximal, distal, and radial margins are negative. Lymph nodes: 2 of 23 lymph nodes positive for metastatic adenocarcinoma (pN1b).~Immunohistochemistry: MLH1 intact, MSH2 intact, MSH6 intact, PMS2 intact (mismatch repair proficient).~DIAGNOSIS: Right colon, right hemicolectomy - Moderately differentiated adenocarcinoma, pT3 N1b, margins negative, 2/23 lymph nodes positive.||||||F|||20260508103000
OBX|2|ED|PDF^Pathology Report PDF^LOCAL||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyNjggPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihTdXJnaWNhbCBQYXRob2xvZ3kgUmVwb3J0IC0gUmlnaHQgSGVtaWNvbGVjdG9teSkgVGoKMCAtMjAgVGQKKFBhdGllbnQ6IFdhc2hpbmd0b24sIERlbmlzZSBSLikgVGoKMCAtMjAgVGQKKE1STjogNTU2Nzg5MCkgVGoKMCAtMjAgVGQKKERPQjogMDUvMTIvMTk2NykgVGoKMCAtMjAgVGQKKERpYWdub3NpczogTW9kZXJhdGVseSBkaWZmZXJlbnRpYXRlZCBhZGVub2NhcmNpbm9tYSwgcFQzIE4xYikgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZldGljYSA+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAowMDAwMDAwMzA2IDAwMDAwIG4gCjAwMDAwMDA2MjcgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo3MTYKJSVFT0YK||||||F|||20260508103000
```

---

## 8. MDM^T02 - Discharge summary document from Geisinger Medical Center

```
MSH|^~\&|EPIC|GEISINGER|DOCMGMT|EXTAPP|20260509080200||MDM^T02^MDM_T02|MSG20260509080200008|P|2.5|||AL|NE
EVN|T02|20260509080100
PID|1||MRN6678901^^^GMC^MR||Hershberger^Donald^Raymond^^Mr.^||19490320|M||2106-3^White^CDCREC|412 Bloom St^^Danville^PA^17822^US^H||^PRN^PH^^^570^3185312||ENG|W|LUT|ACCT90078901^^^GMC^AN|504-71-8923|||N
PV1|1|I|5MED^5108^A^GMC^^^^5MED|||0184523^Yoder^Rebecca^L^^^MD^^^NPI||||MED||||7|||0184523^Yoder^Rebecca^L^^^MD^^^NPI|IN||GEISINGERHP
TXA|1|DS^Discharge Summary^DOCTYPES|TX|20260509080000||20260509080000|||||0184523^Yoder^Rebecca^L^^^MD^^^NPI||DOC20260509001||||AU
OBX|1|TX|18842-5^Discharge Summary^LN||DISCHARGE SUMMARY~Patient: Hershberger, Donald R.~MRN: 6678901~Admission Date: 05/03/2026~Discharge Date: 05/09/2026~Attending: Rebecca L. Yoder, MD~Principal Diagnosis: Acute pancreatitis (K85.90)~Secondary Diagnoses: Cholelithiasis (K80.20), Type 2 diabetes mellitus (E11.9), Hypertension (I10), Hyperlipidemia (E78.5)~Hospital Course: 77-year-old male admitted with severe epigastric pain radiating to back, nausea, and vomiting. Lipase 1,845 U/L on admission. CT abdomen showed acute interstitial pancreatitis with peripancreatic fat stranding and multiple gallstones. Managed with aggressive IV fluid resuscitation, NPO then diet advancement, IV morphine PCA transitioning to oral oxycodone. MRCP confirmed common bile duct stones, ERCP with sphincterotomy and stone extraction performed on day 3. General surgery consulted for interval cholecystectomy as outpatient. Diet tolerated, pain controlled on oral medications by day 6.~Medications at Discharge: Oxycodone 5mg q6h PRN pain, Pantoprazole 40mg daily, Metformin 1000mg BID, Lisinopril 20mg daily, Atorvastatin 40mg daily.~Follow-up: General surgery in 4 weeks for cholecystectomy, GI in 2 weeks, PCP in 1 week.~Disposition: Home.||||||F|||20260509080000
```

---

## 9. VXU^V04 - Immunization update for pediatric patient at Children's Hospital of Philadelphia

```
MSH|^~\&|EPIC|CHOP|PAIMMSYS|STATEIMM|20260510141500||VXU^V04^VXU_V04|MSG20260510141500009|P|2.5.1|||AL|NE
PID|1||MRN1123456^^^CHOP^MR||Nguyen^Aiden^Duc^^||20240801|M||2028-9^Asian^CDCREC|1900 South St^^Philadelphia^PA^19146^US^H||^PRN^PH^^^215^8429056||VIE||||ACCT10089012^^^CHOP^AN||||N
NK1|1|Nguyen^Thanh^V^^Mr.^||1900 South St^^Philadelphia^PA^19146^US|^PRN^PH^^^215^8429056||FTH^Father^HL70063
NK1|2|Nguyen^Linh^T^^Mrs.^||1900 South St^^Philadelphia^PA^19146^US|^PRN^PH^^^215^8429057||MTH^Mother^HL70063
PV1|1|O|PED^PED05^1^CHOP^^^^PED|||1472839^Rivera^Carmen^A^^^MD^^^NPI||||PED||||7|||1472839^Rivera^Carmen^A^^^MD^^^NPI|OP||KEYSTONE
ORC|RE|ORD20260510001||||||1|||1472839^Rivera^Carmen^A^^^MD^^^NPI
RXA|0|1|20260510141000|20260510141005|20^DTaP^CVX|0.5|mL|IM|LA^Left Arm^HL70163||||||V8901AA|20271130|SKB^GlaxoSmithKline^MVX
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible-Medicaid/Medicaid Managed Care^HL70064||||||F
ORC|RE|ORD20260510002||||||1|||1472839^Rivera^Carmen^A^^^MD^^^NPI
RXA|0|1|20260510141200|20260510141205|133^PCV13^CVX|0.5|mL|IM|RA^Right Arm^HL70163||||||W2345BB|20270831|PFR^Pfizer^MVX
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible-Medicaid/Medicaid Managed Care^HL70064||||||F
ORC|RE|ORD20260510003||||||1|||1472839^Rivera^Carmen^A^^^MD^^^NPI
RXA|0|1|20260510141400|20260510141405|10^IPV^CVX|0.5|mL|IM|LA^Left Arm^HL70163||||||P6789CC|20280228|SPM^Sanofi Pasteur^MVX
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible-Medicaid/Medicaid Managed Care^HL70064||||||F
ORC|RE|ORD20260510004||||||1|||1472839^Rivera^Carmen^A^^^MD^^^NPI
RXA|0|1|20260510141500|20260510141505|48^HIB PRP-T^CVX|0.5|mL|IM|RA^Right Arm^HL70163||||||H3456DD|20270930|MSD^Merck^MVX
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible-Medicaid/Medicaid Managed Care^HL70064||||||F
```

---

## 10. RDE^O11 - Pharmacy order for anticoagulation at UPMC Magee-Womens

```
MSH|^~\&|EPIC|UPMCMAGEE|PHARMACY|RXSYS|20260511092300||RDE^O11^RDE_O11|MSG20260511092300010|P|2.5|||AL|NE
PID|1||MRN2234567^^^UPMC^MR||Santoro^Angela^Francesca^^Mrs.^||19760814|F||2106-3^White^CDCREC|3012 Forbes Ave^^Pittsburgh^PA^15213^US^H||^PRN^PH^^^412^7826712||ITA|M|CAT|ACCT20090123^^^UPMC^AN|742-18-5603|||N
PV1|1|I|7CARD^7302^A^UPMCMAGEE^^^^7CARD|||2841567^Petrov^Nikolai^A^^^MD^^^NPI||||CAR||||7|||2841567^Petrov^Nikolai^A^^^MD^^^NPI|IN||UPMCHP
AL1|1|DA|70618^Penicillin^RxNorm|SV|Anaphylaxis|20050918
ORC|NW|ORD20260511001|||||1^^^20260511100000^^S||20260511092300|RXCLERK||2841567^Petrov^Nikolai^A^^^MD^^^NPI
RXE|1^^^20260511100000^^S|854238^Enoxaparin 60mg/0.6mL Injectable Solution^RxNorm||60|mg|SC^Subcutaneous^HL70162||N||1|SYR^Syringe^HL70292||2841567^Petrov^Nikolai^A^^^MD^^^NPI||||854238^Enoxaparin 60mg/0.6mL^RxNorm
RXR|SC^Subcutaneous^HL70162|ABD^Abdomen^HL70163
OBX|1|NM|3173-2^aPTT in Blood by Coagulation assay^LN||32.6|seconds|25.0-36.0|N|||F|||20260511060000
OBX|2|NM|5902-2^Prothrombin time (PT)^LN||13.2|seconds|11.0-15.0|N|||F|||20260511060000
OBX|3|NM|6301-6^INR in Platelet poor plasma by Coagulation assay^LN||1.1||0.9-1.2|N|||F|||20260511060000
OBX|4|NM|26515-7^Platelets [#/volume] in Blood^LN||212|10*3/uL|150-400|N|||F|||20260511060000
```

---

## 11. ADT^A08 - Patient information update at Penn State Hershey Medical Center

```
MSH|^~\&|EPICADT|PSUHMC|RECEIVING|EXTAPP|20260512110045||ADT^A08^ADT_A08|MSG20260512110045011|P|2.5.1|||AL|NE
EVN|A08|20260512110000|||REGCLERK
PID|1||MRN3345678^^^PSUHMC^MR~609-24-8371^^^SSA^SS||Becker^Jonathan^Frederick^^Mr.^||19820723|M||2106-3^White^CDCREC|500 University Dr^^Hershey^PA^17033^US^H~2340 Market St^^Harrisburg^PA^17101^US^M||^PRN^PH^^^717^5313221~^PRN^CP^^^717^4829988~^NET^Internet^jw.becker@email.com||ENG|M|LUT|ACCT30001234^^^PSUHMC^AN|609-24-8371|||N||||20260512
PD1|||Penn State Health Milton S. Hershey Medical Center^^^PSUHMC||||||||N
NK1|1|Becker^Laura^Christine^^Mrs.^||2340 Market St^^Harrisburg^PA^17101^US|^PRN^PH^^^717^4829989||SPO^Spouse^HL70063
PV1|1|O|ORTHO^ORT02^1^PSUHMC^^^^ORTHO|||3692147^Zimmerman^Craig^T^^^MD^^^NPI||||ORT||||7|||3692147^Zimmerman^Craig^T^^^MD^^^NPI|OP||CAPITALBCBS
IN1|1|001|CAPBC001^Capital BlueCross|Capital BlueCross^^Harrisburg^PA^17101|^PRN^PH^^^800^9622242|||||GRP778899||FULLTIME|||Becker^Jonathan^Frederick|SEL|19820723|2340 Market St^^Harrisburg^PA^17101||1|||||||||||||POL445566||||||M
```

---

## 12. DFT^P03 - Charge posting for cardiac catheterization at UPMC Presbyterian

```
MSH|^~\&|EPIC|UPMCPRESBY|BILLING|FINSYS|20260513143500||DFT^P03^DFT_P03|MSG20260513143500012|P|2.4|||AL|NE
EVN|P03|20260513143500
PID|1||MRN7734567^^^UPMC^MR||Jackson^Terrence^Lamar^^Mr.^||19870613|M||2054-5^Black or African American^CDCREC|2714 Centre Ave Apt 8^^Pittsburgh^PA^15213^US^H||^PRN^PH^^^412^7623891||ENG|S|NON|ACCT30067890^^^UPMC^AN|518-42-9037|||N
PV1|1|I|CATH^CATH02^1^UPMCPRESBY^^^^CATH|||4813926^Romano^David^S^^^MD^^^NPI||||CAR||||7|||4813926^Romano^David^S^^^MD^^^NPI|IN||UPMCHP
FT1|1|20260513|20260513143000|P|C|93458^Left heart catheterization^CPT4||1|||4800.00|||||CATH^CATH02^1^UPMCPRESBY|4813926^Romano^David^S^^^MD^^^NPI||I25.10^Atherosclerotic heart disease^ICD10
FT1|2|20260513|20260513143000|P|C|92928^Percutaneous transcatheter placement of intracoronary stent^CPT4||1|||7200.00|||||CATH^CATH02^1^UPMCPRESBY|4813926^Romano^David^S^^^MD^^^NPI||I25.10^Atherosclerotic heart disease^ICD10
FT1|3|20260513|20260513143000|P|C|C1874^Stent, coated/covered, with delivery system^HCPCS||1|||6800.00|||||CATH^CATH02^1^UPMCPRESBY|4813926^Romano^David^S^^^MD^^^NPI||I25.10^Atherosclerotic heart disease^ICD10
FT1|4|20260513|20260513143000|P|C|93571^Intravascular Doppler flow velocity^CPT4||1|||1650.00|||||CATH^CATH02^1^UPMCPRESBY|4813926^Romano^David^S^^^MD^^^NPI||I25.10^Atherosclerotic heart disease^ICD10
DG1|1|I10|I25.10^Atherosclerotic heart disease of native coronary artery without angina pectoris^ICD10|||A
IN1|1|001|UPMCHP01^UPMC Health Plan|UPMC Health Plan^^Pittsburgh^PA^15222|^PRN^PH^^^888^8764357|||||GRP445566||FULLTIME|||Jackson^Terrence^Lamar|SEL|19870613|2714 Centre Ave Apt 8^^Pittsburgh^PA^15213||1|||||||||||||POL334455||||||M
```

---

## 13. ADT^A02 - Patient transfer at Temple University Hospital

```
MSH|^~\&|EPICADT|TUHPHILA|RECEIVING|EXTAPP|20260514091200||ADT^A02^ADT_A02|MSG20260514091200013|P|2.4|||AL|NE
EVN|A02|20260514091100|||NRSUNIT
PID|1||MRN4456789^^^TUH^MR||Rivera^Luis^Enrique^^Mr.^||19690901|M||2131-1^Other Race^CDCREC|3401 N Broad St^^Philadelphia^PA^19140^US^H||^PRN^PH^^^215^6728234~^PRN^CP^^^267^4091123||SPA|D|CAT|ACCT40012345^^^TUH^AN|853-29-4170|||H
PV1|1|I|ICU^ICU06^A^TUH^^^^ICU|U||5837201^Santiago^Maria^E^^^MD^^^NPI|6924103^Ahmed^Farhan^K^^^MD^^^NPI||MED||||7|||5837201^Santiago^Maria^E^^^MD^^^NPI|IN||KEYSTONE||||||||||||||3EAST^3112^B^TUH^^^^3EAST|AI|||20260511143000
PV2|||^Septic shock secondary to pneumonia||||||||20260511|||||||||||||||ICU^ICU06^A|3EAST^3112^B
DG1|1|I10|R65.21^Severe sepsis with septic shock^ICD10|||A
DG1|2|I10|J18.9^Pneumonia, unspecified organism^ICD10|||S
```

---

## 14. ORU^R01 - Microbiology culture results from Lehigh Valley Hospital

```
MSH|^~\&|EPICCARE|LVHN|RECEIVING|LABSYS|20260515074500||ORU^R01^ORU_R01|MSG20260515074500014|P|2.5.1|||AL|NE
PID|1||MRN5567890^^^LVHN^MR||Mueller^Katherine^Elisabeth^^Mrs.^||19431105|F||2106-3^White^CDCREC|812 Hamilton St^^Allentown^PA^18101^US^H||^PRN^PH^^^610^3742289||GER|W|LUT|ACCT50023456^^^LVHN^AN|905-38-2164|||N
PV1|1|I|6WEST^6304^A^LVHN^^^^6WEST|||7148293^Singh^Amrit^P^^^MD^^^NPI||||MED||||7|||7148293^Singh^Amrit^P^^^MD^^^NPI|IN||MCARE
ORC|RE|ORD20260513001|FIL20260515001||CM||||20260513100000|||7148293^Singh^Amrit^P^^^MD^^^NPI
OBR|1|ORD20260513001|FIL20260515001|87070^Culture, bacterial, any source^CPT4|||20260513100000|||||||||7148293^Singh^Amrit^P^^^MD^^^NPI||||||20260515074400|||F
OBX|1|CE|600-7^Bacteria identified in Blood by Culture^LN||3092008^Staphylococcus aureus^SCT||||||F|||20260515074400
OBX|2|TX|19156-3^Comment^LN||BLOOD CULTURE - FINAL RESULT~Specimen: Blood, venipuncture, left antecubital~Collected: 05/13/2026 10:00~Gram Stain: Gram positive cocci in clusters~Aerobic Culture: Methicillin-susceptible Staphylococcus aureus (MSSA) isolated after 14 hours incubation.~Colony count: >100,000 CFU/mL||||||F|||20260515074400
OBX|3|CE|18907-6^Ampicillin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||R^Resistant^HL70078|ug/mL|||||F|||20260515074400
OBX|4|CE|18961-3^Oxacillin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||S^Susceptible^HL70078|ug/mL|||||F|||20260515074400
OBX|5|CE|18928-2^Gentamicin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||S^Susceptible^HL70078|ug/mL|||||F|||20260515074400
OBX|6|CE|18996-9^Vancomycin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||S^Susceptible^HL70078|ug/mL|||||F|||20260515074400
OBX|7|CE|18878-9^Cefazolin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||S^Susceptible^HL70078|ug/mL|||||F|||20260515074400
OBX|8|CE|18993-6^Trimethoprim+Sulfamethoxazole [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||S^Susceptible^HL70078|ug/mL|||||F|||20260515074400
OBX|9|CE|18969-6^Clindamycin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||S^Susceptible^HL70078|ug/mL|||||F|||20260515074400
OBX|10|CE|23640-5^Erythromycin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||S^Susceptible^HL70078|ug/mL|||||F|||20260515074400
```

---

## 15. ADT^A28 - New person registration (MPI) at Geisinger Health

```
MSH|^~\&|BRIDGES|GEISINGER|EMPI|MPISYS|20260516120030||ADT^A28^ADT_A28|MSG20260516120030015|P|2.5|||AL|NE
EVN|A28|20260516120000|||MPICLERK
PID|1||MRN6678901^^^GMC^MR~EMPI7788990^^^GEMPI^PI||Stankiewicz^Anna^Katarzyna^^Mrs.^||19750318|F||2106-3^White^CDCREC|234 Mill St^^Danville^PA^17822^US^H||^PRN^PH^^^570^2814490~^PRN^CP^^^570^9378823~^NET^Internet^anna.stank@email.com||POL|M|CAT|ACCT60034567^^^GMC^AN|163-52-7840|||N||||20260516
PD1|||Geisinger Medical Center^^^GMC||||||||N
NK1|1|Stankiewicz^Piotr^Janusz^^Mr.^||234 Mill St^^Danville^PA^17822^US|^PRN^PH^^^570^2814491||SPO^Spouse^HL70063
```

---

## 16. ADT^A31 - Patient update in master patient index at Lehigh Valley Health Network

```
MSH|^~\&|BRIDGES|LVHN|EMPI|MPISYS|20260517083000||ADT^A31^ADT_A31|MSG20260517083000016|P|2.5|||AL|NE
EVN|A31|20260517082900|||MPIUPDATE
PID|1||MRN7789012^^^LVHN^MR~EMPI5566778^^^LVEMPI^PI||Thompson^Marcus^Darnell^^Mr.^Jr.||19930815|M||2054-5^Black or African American^CDCREC|412 Turner St^^Allentown^PA^18101^US^H||^PRN^PH^^^610^5193345~^PRN^CP^^^484^7627789~^NET^Internet^marcus.thompson93@email.com||ENG|S|BAP|ACCT70045678^^^LVHN^AN|271-84-6930|||N||||20260517
PD1|||LVHN Primary Care Bethlehem^^^LVHN||||||||N
NK1|1|Thompson^Gloria^Annette^^Mrs.^||890 Broad St^^Bethlehem^PA^18018^US|^PRN^PH^^^610^4172278||MTH^Mother^HL70063
IN1|1|001|IBCBS001^Independence Blue Cross|Independence Blue Cross^^Philadelphia^PA^19103|^PRN^PH^^^800^2753242|||||GRP334455||FULLTIME|||Thompson^Marcus^Darnell|SEL|19930815|412 Turner St^^Allentown^PA^18101||1|||||||||||||POL667788||||||M
IN1|2|002|DELTA01^Delta Dental of PA|Delta Dental^^Mechanicsburg^PA^17055|^PRN^PH^^^800^9320629|||||GRP334455||FULLTIME|||Thompson^Marcus^Darnell|SEL|19930815|412 Turner St^^Allentown^PA^18101||2|||||||||||||DEN889900||||||M
```

---

## 17. ORU^R01 - Radiology report with embedded CDA document (ED datatype) from UPMC

```
MSH|^~\&|EPICCARE|UPMCPRESBY|RECEIVING|RADSYS|20260518111500||ORU^R01^ORU_R01|MSG20260518111500017|P|2.5.1|||AL|NE
PID|1||MRN8890123^^^UPMC^MR||Okafor^Chioma^Adaeze^^Ms.^||19880224|F||2054-5^Black or African American^CDCREC|4912 Penn Ave^^Pittsburgh^PA^15224^US^H||^PRN^PH^^^412^3816601||ENG|S|NON|ACCT80056789^^^UPMC^AN|407-29-6183|||N
PV1|1|O|RADOL^RAD03^1^UPMCPRESBY^^^^RADOL|||8527413^Volkov^Elena^S^^^MD^^^NPI||||RAD||||7|||8527413^Volkov^Elena^S^^^MD^^^NPI|OP||UPMCHP
ORC|RE|ORD20260516001|FIL20260518001||CM||||20260517090000|||8527413^Volkov^Elena^S^^^MD^^^NPI
OBR|1|ORD20260516001|FIL20260518001|70553^MRI BRAIN WITH AND WITHOUT CONTRAST^CPT4|||20260517091500|||||||||8527413^Volkov^Elena^S^^^MD^^^NPI||||||20260518111400|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||MRI BRAIN WITH AND WITHOUT CONTRAST~Date: 05/17/2026~Clinical Indication: Recurrent headaches with visual disturbance, evaluate for intracranial pathology.~Technique: Multiplanar multisequence MRI of the brain was performed before and after administration of 15mL gadavist IV contrast.~Comparison: None available.~Findings:~Brain Parenchyma: There is a 1.4 x 1.2 cm enhancing extra-axial mass along the left sphenoid wing, isointense on T1, isointense on T2, with homogeneous enhancement and a dural tail sign. Findings are consistent with a meningioma. No associated mass effect or midline shift. No restricted diffusion. No surrounding edema.~Ventricles: Normal in size and configuration. No hydrocephalus.~Posterior Fossa: Cerebellar hemispheres and brainstem are normal. No tonsillar herniation.~Vasculature: Flow voids in major intracranial vessels are preserved. No aneurysm.~Orbits and Sinuses: Mild mucosal thickening in bilateral maxillary sinuses. Orbits are unremarkable.~Impression:~1. 1.4 cm left sphenoid wing meningioma. No mass effect or edema. Recommend neurosurgical consultation and surveillance MRI in 6 months.~2. Mild maxillary sinusitis.||||||F|||20260518111400
OBX|2|ED|CDA^Radiology Report CDA^LOCAL||^text^xml^Base64^PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIj4KICA8cmVhbG1Db2RlIGNvZGU9IlVTIi8+CiAgPHR5cGVJZCByb290PSIyLjE2Ljg0MC4xLjExMzg4My4xLjMiIGV4dGVuc2lvbj0iUE9DRF9IRDA1MDAwMCIvPgogIDx0ZW1wbGF0ZUlkIHJvb3Q9IjIuMTYuODQwLjEuMTEzODgzLjEwLjIwLjIyLjIuMSIvPgogIDxpZCByb290PSIyLjE2Ljg0MC4xLjExMzg4My4xOS41Ljk5OTk5LjEiIGV4dGVuc2lvbj0iUkFEMjAyNjA1MTgwMDEiLz4KICA8Y29kZSBjb2RlPSIxODc0OC00IiBjb2RlU3lzdGVtPSIyLjE2Ljg0MC4xLjExMzg4My42LjEiIGRpc3BsYXlOYW1lPSJEaWFnbm9zdGljIEltYWdpbmcgUmVwb3J0Ii8+CiAgPHRpdGxlPk1SSCBCcmFpbiB3aXRoIGFuZCB3aXRob3V0IENvbnRyYXN0IC0gRmluYWwgUmVwb3J0PC90aXRsZT4KICA8ZWZmZWN0aXZlVGltZSB2YWx1ZT0iMjAyNjA1MTgxMTE0MDAiLz4KICA8cmVjb3JkVGFyZ2V0PgogICAgPHBhdGllbnRSb2xlPgogICAgICA8aWQgcm9vdD0iMi4xNi44NDAuMS4xMTM4ODMuMTkuNS45OTk5OS4yIiBleHRlbnNpb249Ik1STjg4OTAxMjMiLz4KICAgICAgPHBhdGllbnQ+CiAgICAgICAgPG5hbWU+PGdpdmVuPkNoaW9tYTwvZ2l2ZW4+PGZhbWlseT5Pa2Fmb3I8L2ZhbWlseT48L25hbWU+CiAgICAgIDwvcGF0aWVudD4KICAgIDwvcGF0aWVudFJvbGU+CiAgPC9yZWNvcmRUYXJnZXQ+CiAgPGNvbXBvbmVudD4KICAgIDxzdHJ1Y3R1cmVkQm9keT4KICAgICAgPGNvbXBvbmVudD4KICAgICAgICA8c2VjdGlvbj4KICAgICAgICAgIDx0aXRsZT5JbXByZXNzaW9uPC90aXRsZT4KICAgICAgICAgIDx0ZXh0PkxlZnQgc3BoZW5vaWQgd2luZyBtZW5pbmdpb21hLCAxLjQgY20uIE5vIG1hc3MgZWZmZWN0LjwvdGV4dD4KICAgICAgICA8L3NlY3Rpb24+CiAgICAgIDwvY29tcG9uZW50PgogICAgPC9zdHJ1Y3R1cmVkQm9keT4KICA8L2NvbXBvbmVudD4KPC9DbGluaWNhbERvY3VtZW50Pgo=||||||F|||20260518111400
```

---

## 18. ORM^O01 - Laboratory order panel from Penn State Hershey Medical Center

```
MSH|^~\&|EPIC|PSUHMC|LABIS|LABSYS|20260519063000||ORM^O01^ORM_O01|MSG20260519063000018|P|2.4|||AL|NE
PID|1||MRN9901234^^^PSUHMC^MR||Patel^Meera^Sunita^^Mrs.^||19710102|F||2028-9^Asian^CDCREC|1245 Fishburn Rd^^Hershey^PA^17033^US^H||^PRN^PH^^^717^5316678~^PRN^CP^^^717^2489945||HIN|M|HIN|ACCT90067890^^^PSUHMC^AN|836-59-1247|||N
PV1|1|I|4MED^4208^A^PSUHMC^^^^4MED|||9283614^Gruber^Matthew^E^^^MD^^^NPI||||MED||||7|||9283614^Gruber^Matthew^E^^^MD^^^NPI|IN||CAPITALBCBS
ORC|NW|ORD20260519001||||||1^^^20260519070000^^R||20260519063000|LABCLERK||9283614^Gruber^Matthew^E^^^MD^^^NPI
OBR|1|ORD20260519001||80053^Comprehensive Metabolic Panel^CPT4|||20260519070000||||N|||||9283614^Gruber^Matthew^E^^^MD^^^NPI
DG1|1|I10|E11.65^Type 2 diabetes mellitus with hyperglycemia^ICD10|||A
ORC|NW|ORD20260519002||||||1^^^20260519070000^^R||20260519063000|LABCLERK||9283614^Gruber^Matthew^E^^^MD^^^NPI
OBR|2|ORD20260519002||83036^Hemoglobin A1c^CPT4|||20260519070000||||N|||||9283614^Gruber^Matthew^E^^^MD^^^NPI
DG1|1|I10|E11.65^Type 2 diabetes mellitus with hyperglycemia^ICD10|||A
ORC|NW|ORD20260519003||||||1^^^20260519070000^^R||20260519063000|LABCLERK||9283614^Gruber^Matthew^E^^^MD^^^NPI
OBR|3|ORD20260519003||2093-3^Cholesterol [Mass/volume] in Serum or Plasma^LN|||20260519070000||||N|||||9283614^Gruber^Matthew^E^^^MD^^^NPI
DG1|1|I10|E78.5^Hyperlipidemia, unspecified^ICD10|||A
```

---

## 19. ORU^R01 - Comprehensive metabolic panel results from Penn State Hershey

```
MSH|^~\&|EPICCARE|PSUHMC|RECEIVING|LABSYS|20260519101200||ORU^R01^ORU_R01|MSG20260519101200019|P|2.5.1|||AL|NE
PID|1||MRN9901234^^^PSUHMC^MR||Patel^Meera^Sunita^^Mrs.^||19710102|F||2028-9^Asian^CDCREC|1245 Fishburn Rd^^Hershey^PA^17033^US^H||^PRN^PH^^^717^5316678||HIN|M|HIN|ACCT90067890^^^PSUHMC^AN|836-59-1247|||N
PV1|1|I|4MED^4208^A^PSUHMC^^^^4MED|||9283614^Gruber^Matthew^E^^^MD^^^NPI||||MED||||7|||9283614^Gruber^Matthew^E^^^MD^^^NPI|IN||CAPITALBCBS
ORC|RE|ORD20260519001|FIL20260519001||CM||||20260519070000|||9283614^Gruber^Matthew^E^^^MD^^^NPI
OBR|1|ORD20260519001|FIL20260519001|80053^Comprehensive Metabolic Panel^CPT4|||20260519070500|||||||||9283614^Gruber^Matthew^E^^^MD^^^NPI||||||20260519101100|||F
OBX|1|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||168|mg/dL|74-106|H|||F|||20260519101100
OBX|2|NM|3094-0^Urea nitrogen [Mass/volume] in Serum or Plasma^LN||18|mg/dL|6-20|N|||F|||20260519101100
OBX|3|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||0.9|mg/dL|0.6-1.2|N|||F|||20260519101100
OBX|4|NM|33914-3^Glomerular filtration rate/1.73 sq M.predicted^LN||78|mL/min/1.73m2|>60|N|||F|||20260519101100
OBX|5|NM|2951-2^Sodium [Moles/volume] in Serum or Plasma^LN||141|mmol/L|136-145|N|||F|||20260519101100
OBX|6|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN||4.2|mmol/L|3.5-5.1|N|||F|||20260519101100
OBX|7|NM|2075-0^Chloride [Moles/volume] in Serum or Plasma^LN||103|mmol/L|98-106|N|||F|||20260519101100
OBX|8|NM|2028-9^Carbon dioxide, total [Moles/volume] in Serum or Plasma^LN||24|mmol/L|20-29|N|||F|||20260519101100
OBX|9|NM|17861-6^Calcium [Mass/volume] in Serum or Plasma^LN||9.6|mg/dL|8.5-10.5|N|||F|||20260519101100
OBX|10|NM|2885-2^Protein [Mass/volume] in Serum or Plasma^LN||7.3|g/dL|6.0-8.3|N|||F|||20260519101100
OBX|11|NM|1751-7^Albumin [Mass/volume] in Serum or Plasma^LN||4.1|g/dL|3.5-5.5|N|||F|||20260519101100
OBX|12|NM|1975-2^Bilirubin.total [Mass/volume] in Serum or Plasma^LN||0.6|mg/dL|0.1-1.2|N|||F|||20260519101100
OBX|13|NM|6768-6^Alkaline phosphatase [Enzymatic activity/volume] in Serum or Plasma^LN||85|U/L|44-147|N|||F|||20260519101100
OBX|14|NM|1742-6^Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||31|U/L|7-56|N|||F|||20260519101100
```

---

## 20. ORU^R01 - Hemoglobin A1c and lipid panel results from Penn State Hershey

```
MSH|^~\&|EPICCARE|PSUHMC|RECEIVING|LABSYS|20260519101500||ORU^R01^ORU_R01|MSG20260519101500020|P|2.5.1|||AL|NE
PID|1||MRN9901234^^^PSUHMC^MR||Patel^Meera^Sunita^^Mrs.^||19710102|F||2028-9^Asian^CDCREC|1245 Fishburn Rd^^Hershey^PA^17033^US^H||^PRN^PH^^^717^5316678||HIN|M|HIN|ACCT90067890^^^PSUHMC^AN|836-59-1247|||N
PV1|1|I|4MED^4208^A^PSUHMC^^^^4MED|||9283614^Gruber^Matthew^E^^^MD^^^NPI||||MED||||7|||9283614^Gruber^Matthew^E^^^MD^^^NPI|IN||CAPITALBCBS
ORC|RE|ORD20260519002|FIL20260519002||CM||||20260519070000|||9283614^Gruber^Matthew^E^^^MD^^^NPI
OBR|1|ORD20260519002|FIL20260519002|83036^Hemoglobin A1c^CPT4|||20260519070500|||||||||9283614^Gruber^Matthew^E^^^MD^^^NPI||||||20260519101400|||F
OBX|1|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN||9.1|%|<5.7|H|||F|||20260519101400
OBX|2|NM|27353-2^Glucose mean value [Mass/volume] in Blood Estimated from glycated hemoglobin^LN||214|mg/dL|||||F|||20260519101400
NTE|1|L|HbA1c of 9.1% corresponds to estimated average glucose of 214 mg/dL. Target for most adults with diabetes is <7.0%. Strongly recommend intensification of glycemic therapy.
ORC|RE|ORD20260519003|FIL20260519003||CM||||20260519070000|||9283614^Gruber^Matthew^E^^^MD^^^NPI
OBR|2|ORD20260519003|FIL20260519003|2093-3^Cholesterol [Mass/volume] in Serum or Plasma^LN|||20260519070500|||||||||9283614^Gruber^Matthew^E^^^MD^^^NPI||||||20260519101400|||F
OBX|3|NM|2093-3^Cholesterol [Mass/volume] in Serum or Plasma^LN||234|mg/dL|<200|H|||F|||20260519101400
OBX|4|NM|2571-8^Triglycerides [Mass/volume] in Serum or Plasma^LN||198|mg/dL|<150|H|||F|||20260519101400
OBX|5|NM|2085-9^Cholesterol in HDL [Mass/volume] in Serum or Plasma^LN||38|mg/dL|>40|L|||F|||20260519101400
OBX|6|NM|13457-7^Cholesterol in LDL [Mass/volume] in Serum or Plasma by calculation^LN||156|mg/dL|<100|H|||F|||20260519101400
NTE|2|L|Lipid panel shows elevated total cholesterol, LDL, and triglycerides with low HDL. High cardiovascular risk profile. Recommend statin therapy initiation or dose adjustment.
```
