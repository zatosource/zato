# Rhapsody Integration Engine - real HL7v2 ER7 messages

## 1. ADT^A01 - Patient admission to IU Health Methodist Hospital

```
MSH|^~\&|EPIC|IUHEALTH|RHAPSODY|IHIE|20250312082000-0500||ADT^A01^ADT_A01|RHP-IUH-20250312-001234|P|2.4|||AL|NE
EVN|A01|20250312082000
PID|1||MRN-10294831^^^IUHEALTH^MR||Hendricks^Clyde^Wayne^^||19670412|M||2106-3^White^CDCREC|4523 N Pennsylvania St^^Indianapolis^IN^46205^USA||^PRN^PH^^1^317^5553456|||||||441-28-7903
NK1|1|Hendricks^Brenda^Jo|SPO^Spouse^HL70063|4523 N Pennsylvania St^^Indianapolis^IN^46205^USA^H|^PRN^PH^^1^317^5553457
PV1|1|I|MED^4N^412||||1938274650^Naidu^Vikram^S^^^MD|1938274650^Naidu^Vikram^S^^^MD||MED||||1|||||I|VN-20250312-0891^^^IUHEALTH^VN|||||||||||||||||||||||||20250312082000
PV2|||^Pneumonia, community-acquired|||||||||2|||||||||||||||||||||||||20250312
DG1|1||J18.9^Pneumonia, unspecified organism^ICD10|||A
IN1|1|1^BCBS^BCBS|BC83921||Blue Cross Blue Shield of Indiana|PO Box 1234^^Indianapolis^IN^46201^USA|^WPN^PH^^1^800^5551234||GRP-41278||||20240101||||Hendricks^Clyde^Wayne^^|SEL|19670412|4523 N Pennsylvania St^^Indianapolis^IN^46205^USA|||||||||||||||HND739204817
```

---

## 2. ADT^A03 - Patient discharge from Franciscan Health Indianapolis

```
MSH|^~\&|CERNER|FRANCISCAN|RHAPSODY|IHIE|20250315143000-0500||ADT^A03^ADT_A03|RHP-FRAN-20250315-002345|P|2.4|||AL|NE
EVN|A03|20250315143000
PID|1||MRN-20481937^^^FRANCISCAN^MR||Delgado^Sofia^Valentina^^||19820925|F||2135-2^Hispanic or Latino^CDCREC|2815 E Washington St^^Indianapolis^IN^46201^USA||^PRN^PH^^1^317^5557812|||||||318-72-4590
PV1|1|I|SURG^3W^318||||2047183956^Okafor^Nkechi^R^^^MD|2047183956^Okafor^Nkechi^R^^^MD||SURG||||1|||||I|VN-20250312-0456^^^FRANCISCAN^VN|||||||||||||||||||20250312100000||||||||20250315143000
DG1|1||K80.10^Calculus of gallbladder with chronic cholecystitis without obstruction^ICD10|||A
DG1|2||K81.0^Acute cholecystitis^ICD10|||A
PR1|1||47562^Laparoscopic cholecystectomy^CPT4|20250313083000|1234
```

---

## 3. ORU^R01 - Lab result routed from Quest Diagnostics through Rhapsody

```
MSH|^~\&|QUESTLIS|QUEST_INDY|RHAPSODY|IHIE|20250418102000-0500||ORU^R01^ORU_R01|RHP-QUEST-20250418-003456|P|2.3.1|||AL|NE
PID|1||QD-MRN-30519274^^^QUEST^MR||Stinson^Kara^Nicole^^||19790815|F||2106-3^White^CDCREC|9834 Brooks School Rd^^Fishers^IN^46037^USA||^PRN^PH^^1^317^5559123|||||||227-84-3196
ORC|RE|ORD-20250417-0345^IUHEALTH|QD-RES-20250418-003456^QUEST||||1^^^20250417090000^^R||20250418102000|3819204756^Banerjee^Aniket^P^^^MD|3819204756^Banerjee^Aniket^P^^^MD|3819204756^Banerjee^Aniket^P^^^MD||^WPN^PH^^1^317^9621000||||||IUHEALTH^IU Health
OBR|1|ORD-20250417-0345^IUHEALTH|QD-RES-20250418-003456^QUEST|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN|||20250417093000-0500|||A||||Blood|3819204756^Banerjee^Aniket^P^^^MD||||||20250418095000-0500|||F
OBX|1|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN|1|6.8|%|4.0-5.6|H|||F|||20250417093000-0500
OBX|2|NM|59261-8^Hemoglobin A1c/Hemoglobin.total in Blood by IFCC protocol^LN|2|51|mmol/mol|20-38|H|||F|||20250417093000-0500
```

---

## 4. VXU^V04 - Immunization submission to Indiana CHIRP registry

```
MSH|^~\&|EPIC|CHN|RHAPSODY|CHIRP|20250505143000-0500||VXU^V04^VXU_V04|RHP-CHN-20250505-004567|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||MRN-40623178^^^CHN^MR||Prewitt^Lily^Charlotte^^||20231012|F||2106-3^White^CDCREC|8912 E 96th St^^Fishers^IN^46037^USA||^PRN^PH^^1^317^5554523|||||||||||N
NK1|1|Prewitt^Megan^R|MTH^Mother^HL70063|8912 E 96th St^^Fishers^IN^46037^USA^H|^PRN^PH^^1^317^5554524
ORC|RE|ORD-IMM-20250505-012^CHN|||||1^^^20250505140000^^R||20250505143000|4720391856^Whitfield^Derek^L^^^MD|4720391856^Whitfield^Derek^L^^^MD|4720391856^Whitfield^Derek^L^^^MD||^WPN^PH^^1^317^3557000||||||CHN^Community Health Network
RXA|0|1|20250505141500|20250505141500|08^Hep B, adolescent or pediatric^CVX|0.5|mL|IM^Intramuscular^HL70162|LA^Left Arm^HL70163||||||M4567^Merck^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN|1|V05^VFC eligible - Federally Qualified Health Center Patient^HL70064||||||F
```

---

## 5. MDM^T02 - Clinical document notification from IU Health

```
MSH|^~\&|EPIC|IUHEALTH|RHAPSODY|IHIE|20250610152000-0500||MDM^T02^MDM_T02|RHP-IUH-20250610-005678|P|2.4|||AL|NE
EVN|T02|20250610152000
PID|1||MRN-50812473^^^IUHEALTH^MR||Hargrove^Leonard^Franklin^^||19550303|M||2106-3^White^CDCREC|2234 Broadripple Ave^^Indianapolis^IN^46220^USA||^PRN^PH^^1^317^5553478|||||||674-13-8920
PV1|1|O|CARD^CLINIC^01||||5293017486^Larimore^Patricia^W^^^MD|5293017486^Larimore^Patricia^W^^^MD||CARD||||||||V|VN-20250610-0567^^^IUHEALTH^VN|||||||||||||||||||||||||20250610130000
TXA|1|HP|TX|20250610152000|5293017486^Larimore^Patricia^W^^^MD||20250610152000||5293017486^Larimore^Patricia^W^^^MD||||DOC-IUH-20250610-005678|IUHEALTH||||AU||AV
OBX|1|TX|11488-4^Consult note^LN|1|CARDIOLOGY CONSULTATION NOTE~~PATIENT: Hargrove, Leonard Franklin~~DATE: 06/10/2025~~REASON FOR CONSULTATION: Atypical chest pain, abnormal ECG.~~HISTORY: 70-year-old male with history of hypertension, hyperlipidemia, and type 2 diabetes presents with intermittent chest discomfort for 2 weeks.~~EXAMINATION: BP 142/88, HR 78, regular. Heart sounds normal, no murmur. Lungs clear. No peripheral edema.~~ECG: Normal sinus rhythm, nonspecific ST-T wave changes in lateral leads.~~ASSESSMENT AND PLAN:~1. Atypical chest pain - recommend stress echocardiogram.~2. Hypertension - continue current medications, consider dose adjustment.~3. Follow-up in 2 weeks with stress test results.||||||F
```

---

## 6. ORM^O01 - Radiology order routed through Rhapsody from Community Health Network

```
MSH|^~\&|EPIC|CHN|RHAPSODY|PACS|20250214093800-0500||ORM^O01^ORM_O01|RHP-CHN-20250214-006789|P|2.3|||AL|NE
PID|1||MRN-60942317^^^CHN^MR||Thurman^Jenna^Elise^^||19880415|F||2106-3^White^CDCREC|12345 Hazel Dell Pkwy^^Carmel^IN^46033^USA||^PRN^PH^^1^317^5556789|||||||783-50-9214
PV1|1|O|RAD^CT^03||||6184029375^Kapoor^Deepak^N^^^MD|6184029375^Kapoor^Deepak^N^^^MD||MED||||||||V|VN-20250214-0891^^^CHN^VN|||||||||||||||||||||||||20250214080000
ORC|NW|ORD-RAD-20250214-891^CHN||||||1^^^20250214090000^^R||20250214093800|6184029375^Kapoor^Deepak^N^^^MD|6184029375^Kapoor^Deepak^N^^^MD|6184029375^Kapoor^Deepak^N^^^MD||^WPN^PH^^1^317^3557000||||||CHN^Community Health Network
OBR|1|ORD-RAD-20250214-891^CHN||74177^CT ABD AND PELVIS WO CONTRAST^CPT4|||20250214100000|||A|||||6184029375^Kapoor^Deepak^N^^^MD|^WPN^PH^^1^317^3557000
```

---

## 7. ADT^A08 - Patient information update at Parkview Health, Fort Wayne

```
MSH|^~\&|EPIC|PARKVIEW|RHAPSODY|IHIE|20250723091500-0500||ADT^A08^ADT_A01|RHP-PV-20250723-007890|P|2.4|||AL|NE
EVN|A08|20250723091500
PID|1||MRN-70153928^^^PARKVIEW^MR||Caldwell^Renee^Suzanne^^||19820620|F||2106-3^White^CDCREC|4512 W Jefferson Blvd^^Fort Wayne^IN^46804^USA||^PRN^PH^^1^260^5552345|||||||896-41-2307
PV1|1|O|MED^CLINIC^01||||7042918365^Brennan^Garrett^T^^^MD|7042918365^Brennan^Garrett^T^^^MD||MED||||||||V|VN-20250723-0234^^^PARKVIEW^VN|||||||||||||||||||||||||20250723090000
```

---

## 8. ORU^R01 - Pathology result routed from LabCorp through Rhapsody

```
MSH|^~\&|LABCORPLIS|LABCORP_INDY|RHAPSODY|IHIE|20250305112000-0500||ORU^R01^ORU_R01|RHP-LC-20250305-008901|P|2.3.1|||AL|NE
PID|1||LC-MRN-80274913^^^LABCORP^MR||Gunderson^Irene^Lucille^^||19480918|F||2106-3^White^CDCREC|3456 Fall Creek Pkwy N Dr^^Indianapolis^IN^46205^USA||^PRN^PH^^1^317^5557890|||||||903-62-7148
ORC|RE|ORD-20250304-0678^FRANCISCAN|LC-RES-20250305-008901^LABCORP||||1^^^20250304080000^^R||20250305112000|8305719264^Walton^Craig^D^^^MD|8305719264^Walton^Craig^D^^^MD|8305719264^Walton^Craig^D^^^MD||^WPN^PH^^1^317^5284000||||||FRANCISCAN^Franciscan Health
OBR|1|ORD-20250304-0678^FRANCISCAN|LC-RES-20250305-008901^LABCORP|2093-3^Cholesterol [Mass/volume] in Serum or Plasma^LN|||20250304090000-0500|||A||||Blood|8305719264^Walton^Craig^D^^^MD||||||20250305110000-0500|||F
OBX|1|NM|2093-3^Cholesterol [Mass/volume] in Serum or Plasma^LN|1|232|mg/dL|0-199|H|||F|||20250304090000-0500
OBX|2|NM|2571-8^Triglyceride [Mass/volume] in Serum or Plasma^LN|2|178|mg/dL|0-149|H|||F|||20250304090000-0500
OBX|3|NM|2085-9^Cholesterol in HDL [Mass/volume] in Serum or Plasma^LN|3|48|mg/dL|40-60||||F|||20250304090000-0500
OBX|4|NM|13457-7^Cholesterol in LDL [Mass/volume] in Serum or Plasma by calculation^LN|4|148|mg/dL|0-99|H|||F|||20250304090000-0500
```

---

## 9. ADT^A04 - Patient registration at Eskenazi Health emergency department

```
MSH|^~\&|EPIC|ESKENAZI|RHAPSODY|IHIE|20250820031500-0500||ADT^A04^ADT_A01|RHP-ESK-20250820-009012|P|2.4|||AL|NE
EVN|A04|20250820031500
PID|1||MRN-90281437^^^ESKENAZI^MR||Beasley^Tamika^Denise^^||19950308|F||2054-5^Black or African American^CDCREC|2534 Dr Martin Luther King Jr St^^Indianapolis^IN^46208^USA||^PRN^PH^^1^317^5551876|||||||015-73-8246
PV1|1|E|ED^BED12^01||||9174028365^Ortega^Samuel^F^^^MD|9174028365^Ortega^Samuel^F^^^MD||MED||||||||E|VN-20250820-0345^^^ESKENAZI^VN|||||||||||||||||||||||||20250820031500
DG1|1||R10.9^Unspecified abdominal pain^ICD10|||A
```

---

## 10. VXU^V04 - Adult immunization submission from Franciscan Health to CHIRP

```
MSH|^~\&|CERNER|FRANCISCAN|RHAPSODY|CHIRP|20250415143000-0500||VXU^V04^VXU_V04|RHP-FRAN-20250415-010123|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||MRN-11394728^^^FRANCISCAN^MR||Yarbrough^Terrence^Lamar^^||19710915|M||2054-5^Black or African American^CDCREC|2812 E Washington St^^Indianapolis^IN^46201^USA||^PRN^PH^^1^317^5558901|||||||127-58-4093
ORC|RE|ORD-IMM-20250415-034^FRANCISCAN|||||1^^^20250415140000^^R||20250415143000|1093827465^Fitzgerald^Monica^E^^^MD|1093827465^Fitzgerald^Monica^E^^^MD|1093827465^Fitzgerald^Monica^E^^^MD||^WPN^PH^^1^317^5284000||||||FRANCISCAN^Franciscan Health
RXA|0|1|20250415141500|20250415141500|208^COVID-19, mRNA, LNP-S, PF, bivalent, 30 mcg/0.3 mL^CVX|0.3|mL|IM^Intramuscular^HL70162|RA^Right Arm^HL70163||||||PFR^Pfizer^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN|1|V01^Not VFC eligible^HL70064||||||F
```

---

## 11. ORU^R01 - Microbiology result routed through Rhapsody with embedded PDF

```
MSH|^~\&|BEAKER|IUHEALTH|RHAPSODY|IHIE|20250903152000-0500||ORU^R01^ORU_R01|RHP-IUH-20250903-011234|P|2.4|||AL|NE
PID|1||MRN-21508439^^^IUHEALTH^MR||Crenshaw^Doris^Elaine^^||19630318|F||2106-3^White^CDCREC|5234 E Washington St^^Indianapolis^IN^46219^USA||^PRN^PH^^1^317^5553567|||||||238-91-4067
PV1|1|I|MED^5N^512||||1362847509^Novak^Gregory^T^^^MD|1362847509^Novak^Gregory^T^^^MD||MED||||||||I|VN-20250901-0789^^^IUHEALTH^VN|||||||||||||||||||||||||20250901080000
ORC|RE|ORD-20250901-0789^IUHEALTH|BKR-RES-20250903-011234^BEAKER||||1^^^20250901090000^^R||20250903152000|1362847509^Novak^Gregory^T^^^MD|1362847509^Novak^Gregory^T^^^MD|1362847509^Novak^Gregory^T^^^MD||^WPN^PH^^1^317^9621000||||||IUHEALTH^IU Health Methodist Hospital
OBR|1|ORD-20250901-0789^IUHEALTH|BKR-RES-20250903-011234^BEAKER|600-7^Bacteria identified in Blood by Culture^LN|||20250901091500-0500|||A||||Blood|1362847509^Novak^Gregory^T^^^MD||||||20250903152000|||F
OBX|1|CWE|600-7^Bacteria identified in Blood by Culture^LN|1|3092008^Staphylococcus aureus^SCT||||||F|||20250901091500-0500
OBX|2|CWE|18900-1^Cefazolin [Susceptibility]^LN|2|S^Susceptible^L||||||F|||20250903120000-0500
OBX|3|ED|18725-2^Microbiology studies^LN|3|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 12. ADT^A02 - Patient transfer from ED to ICU at Deaconess Health, Evansville

```
MSH|^~\&|CERNER|DEACONESS|RHAPSODY|IHIE|20250122044500-0500||ADT^A02^ADT_A02|RHP-DEAC-20250122-012345|P|2.4|||AL|NE
EVN|A02|20250122044500
PID|1||MRN-31709284^^^DEACONESS^MR||Embry^Thelma^Nadine^^||19710303|F||2106-3^White^CDCREC|3812 Washington Ave^^Evansville^IN^47714^USA||^PRN^PH^^1^812^5557456|||||||894-30-7162
PV1|1|I|ICU^BED02^01||||1507294836^Marsh^Kenneth^W^^^MD|1507294836^Marsh^Kenneth^W^^^MD||MED||||1|||||I|VN-20250121-0567^^^DEACONESS^VN|||||||||||||||||||||||||20250121163000
PV2|||^Acute respiratory failure
```

---

## 13. ORM^O01 - Laboratory order routed through Rhapsody from Parkview Health

```
MSH|^~\&|EPIC|PARKVIEW|RHAPSODY|LABCORP|20250610091500-0500||ORM^O01^ORM_O01|RHP-PV-20250610-013456|P|2.3|||AL|NE
PID|1||MRN-41830926^^^PARKVIEW^MR||Richter^Eugene^Franklin^^||19590622|M||2106-3^White^CDCREC|6712 Lima Rd^^Fort Wayne^IN^46818^USA||^PRN^PH^^1^260^5551234|||||||452-09-8173
PV1|1|O|LAB^DRAW^01||||1824059371^Poole^Sandra^M^^^MD|1824059371^Poole^Sandra^M^^^MD||MED||||||||V|VN-20250610-0456^^^PARKVIEW^VN|||||||||||||||||||||||||20250610080000
ORC|NW|ORD-20250610-0456^PARKVIEW||||||1^^^20250610090000^^R||20250610091500|1824059371^Poole^Sandra^M^^^MD|1824059371^Poole^Sandra^M^^^MD|1824059371^Poole^Sandra^M^^^MD||^WPN^PH^^1^260^2666000||||||PARKVIEW^Parkview Health
OBR|1|ORD-20250610-0456^PARKVIEW||10231-5^PSA [Mass/volume] in Serum or Plasma^LN|||20250610093000-0500|||A||||Blood|1824059371^Poole^Sandra^M^^^MD
```

---

## 14. MDM^T02 - Discharge summary document routed through Rhapsody

```
MSH|^~\&|EPIC|CHN|RHAPSODY|IHIE|20250715163000-0500||MDM^T02^MDM_T02|RHP-CHN-20250715-014567|P|2.4|||AL|NE
EVN|T02|20250715163000
PID|1||MRN-51204837^^^CHN^MR||Kersey^Allison^Diane^^||19850512|F||2106-3^White^CDCREC|10234 Allisonville Rd^^Fishers^IN^46038^USA||^PRN^PH^^1^317^5553456|||||||563-27-0198
PV1|1|I|MED^3N^308||||2084173965^Shepard^Marcus^T^^^MD|2084173965^Shepard^Marcus^T^^^MD||MED||||||||I|VN-20250712-0234^^^CHN^VN|||||||||||||||||||20250712090000||||||||20250715143000
TXA|1|DS|TX|20250715163000|2084173965^Shepard^Marcus^T^^^MD||20250715163000||2084173965^Shepard^Marcus^T^^^MD||||DOC-CHN-20250715-014567|CHN||||AU||AV
OBX|1|TX|28570-0^Discharge summary^LN|1|DISCHARGE SUMMARY~~PATIENT: Kersey, Allison Diane~~ADMISSION DATE: 07/12/2025~~DISCHARGE DATE: 07/15/2025~~ADMITTING DIAGNOSIS: Acute pyelonephritis.~~HOSPITAL COURSE: Patient presented with fever, flank pain, and dysuria. Urine culture positive for E. coli. Treated with IV ceftriaxone for 72 hours with clinical improvement. Transitioned to oral ciprofloxacin.~~DISCHARGE DIAGNOSIS: Acute pyelonephritis, right kidney.~~DISCHARGE MEDICATIONS: Ciprofloxacin 500mg PO BID x 10 days.~~FOLLOW-UP: PCP in 1 week.||||||F
```

---

## 15. ADT^A01 - Patient admission to Community Health Network, Carmel

```
MSH|^~\&|EPIC|CHN|RHAPSODY|IHIE|20250505112000-0500||ADT^A01^ADT_A01|RHP-CHN-20250505-015678|P|2.4|||AL|NE
EVN|A01|20250505112000
PID|1||MRN-61037284^^^CHN^MR||Shumate^Vernon^Dale^^||19560830|M||2106-3^White^CDCREC|7234 E 10th St^^Indianapolis^IN^46219^USA||^PRN^PH^^1^317^5559567|||||||671-48-3209
NK1|1|Shumate^Carolyn^Faye|SPO^Spouse^HL70063|7234 E 10th St^^Indianapolis^IN^46219^USA^H|^PRN^PH^^1^317^5559568
PV1|1|I|ONCO^3E^312||||2493017586^Dunn^Catherine^L^^^MD|2493017586^Dunn^Catherine^L^^^MD||HEM||||1|||||I|VN-20250505-0891^^^CHN^VN|||||||||||||||||||||||||20250505112000
DG1|1||C91.10^Chronic lymphocytic leukemia of B-cell type not having achieved remission^ICD10|||A
IN1|1|2^ANTHEM^ANTHEM|AN92817||Anthem Blue Cross Blue Shield|PO Box 5678^^Indianapolis^IN^46204^USA|^WPN^PH^^1^800^5552345||GRP-53190||||20240101||||Shumate^Vernon^Dale^^|SEL|19560830|7234 E 10th St^^Indianapolis^IN^46219^USA|||||||||||||||SHU409281735
```

---

## 16. ORU^R01 - Radiology result routed through Rhapsody from Parkview to referring provider

```
MSH|^~\&|POWERSCRIBE|PARKVIEW_RAD|RHAPSODY|REFERRING_EHR|20250228043000-0500||ORU^R01^ORU_R01|RHP-PV-20250228-016789|P|2.4|||AL|NE
PID|1||MRN-71204839^^^PARKVIEW^MR||Oakley^Denise^Vivian^^||19770415|F||2106-3^White^CDCREC|8912 Coldwater Rd^^Fort Wayne^IN^46825^USA||^PRN^PH^^1^260^5558234|||||||784-62-1903
PV1|1|O|RAD^CT^01||||2810473956^Vogel^Nathan^R^^^MD|2810473956^Vogel^Nathan^R^^^MD||RAD||||||||V|VN-20250228-0456^^^PARKVIEW^VN|||||||||||||||||||||||||20250228030000
ORC|RE|ORD-RAD-20250228-456^PARKVIEW|PS-RPT-20250228-016789^POWERSCRIBE||||1^^^20250228033000^^R||20250228043000|2810473956^Vogel^Nathan^R^^^MD|2810473956^Vogel^Nathan^R^^^MD|2810473956^Vogel^Nathan^R^^^MD||^WPN^PH^^1^260^2666000||||||PARKVIEW^Parkview Health
OBR|1|ORD-RAD-20250228-456^PARKVIEW|PS-RPT-20250228-016789^POWERSCRIBE|72110^XR LUMBAR SPINE COMPLETE^CPT4|||20250228034500-0500|||||||||||2810473956^Vogel^Nathan^R^^^MD||RAD-ACC-20250228-0456||||20250228043000|||F
OBX|1|TX|72110^XR LUMBAR SPINE COMPLETE^CPT4|1|XR LUMBAR SPINE 3 VIEWS~~IMPRESSION: Degenerative changes at L4-L5 and L5-S1. No acute fracture.||||||F
```

---

## 17. VXU^V04 - Childhood immunization from IU Health Pediatrics to CHIRP

```
MSH|^~\&|EPIC|IUHEALTH|RHAPSODY|CHIRP|20250610143000-0500||VXU^V04^VXU_V04|RHP-IUH-20250610-017890|P|2.5.1|||ER|AL|||||Z22^CDCPHINVS
PID|1||MRN-81204537^^^IUHEALTH^MR||Trotter^Jaylen^Darius^^Jr||20220315|M||2054-5^Black or African American^CDCREC|1812 N Capitol Ave^^Indianapolis^IN^46202^USA||^PRN^PH^^1^317^5553987|||||||||||N
NK1|1|Trotter^Aisha^N|MTH^Mother^HL70063|1812 N Capitol Ave^^Indianapolis^IN^46202^USA^H|^PRN^PH^^1^317^5553988
ORC|RE|ORD-IMM-20250610-067^IUHEALTH|||||1^^^20250610140000^^R||20250610143000|6290481735^Pham^Linh^Q^^^MD|6290481735^Pham^Linh^Q^^^MD|6290481735^Pham^Linh^Q^^^MD||^WPN^PH^^1^317^9621000||||||IUHEALTH^IU Health
RXA|0|1|20250610141000|20250610141000|110^DTaP-Hep B-IPV^CVX|0.5|mL|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163||||||GSK^GlaxoSmithKline^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN|1|V02^VFC eligible - Medicaid/Medicaid Managed Care^HL70064||||||F
```

---

## 18. ADT^A08 - Insurance update routed through Rhapsody from Franciscan Health

```
MSH|^~\&|CERNER|FRANCISCAN|RHAPSODY|IHIE|20250903102000-0500||ADT^A08^ADT_A01|RHP-FRAN-20250903-018901|P|2.4|||AL|NE
EVN|A08|20250903102000
PID|1||MRN-91384207^^^FRANCISCAN^MR||Yoon^Jae^Hyun^^||19750812|M||2028-9^Asian^CDCREC|12345 Old Meridian St^^Carmel^IN^46032^USA||^PRN^PH^^1^317^5553901|||||||349-80-2716
PV1|1|O|MED^CLINIC^01||||1829405173^Gentry^Rebecca^H^^^MD|1829405173^Gentry^Rebecca^H^^^MD||MED||||||||V|VN-20250903-0567^^^FRANCISCAN^VN|||||||||||||||||||||||||20250903090000
IN1|1|3^UNITED^UNITED|UH42938||UnitedHealthcare of Indiana|PO Box 9012^^Indianapolis^IN^46206^USA|^WPN^PH^^1^800^5553456||GRP-81029||||20250101||||Yoon^Jae^Hyun^^|SEL|19750812|12345 Old Meridian St^^Carmel^IN^46032^USA|||||||||||||||UHC830291745
```

---

## 19. ORU^R01 - Critical lab result routed through Rhapsody with embedded PDF report

```
MSH|^~\&|BEAKER|CHN|RHAPSODY|IHIE|20250820041200-0500||ORU^R01^ORU_R01|RHP-CHN-20250820-019012|P|2.4|||AL|NE
PID|1||MRN-01293847^^^CHN^MR||Pruett^Harold^Vincent^^||19520815|M||2106-3^White^CDCREC|4567 E 56th St^^Indianapolis^IN^46220^USA||^PRN^PH^^1^317^5554321|||||||018-42-9375
PV1|1|I|MED^3N^308||||9081237465^Ingram^Leslie^C^^^MD|9081237465^Ingram^Leslie^C^^^MD||MED||||||||I|VN-20250818-0456^^^CHN^VN|||||||||||||||||||||||||20250818163000
ORC|RE|ORD-20250820-0456^CHN|BKR-RES-20250820-019012^BEAKER||||1^^^20250820030000^^S||20250820041200|9081237465^Ingram^Leslie^C^^^MD|9081237465^Ingram^Leslie^C^^^MD|9081237465^Ingram^Leslie^C^^^MD||^WPN^PH^^1^317^3557000||||||CHN^Community Health Network
OBR|1|ORD-20250820-0456^CHN|BKR-RES-20250820-019012^BEAKER|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN|||20250820033000-0500|||A||||Blood|9081237465^Ingram^Leslie^C^^^MD||||||20250820041200|||F
OBX|1|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN|1|6.2|mmol/L|3.5-5.1|HH|||F|||20250820033000-0500
OBX|2|ED|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN|2|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 20. ADT^A03 - Patient discharge from IU Health Bloomington

```
MSH|^~\&|EPIC|IUHEALTH|RHAPSODY|IHIE|20250801163000-0500||ADT^A03^ADT_A03|RHP-IUH-20250801-020123|P|2.4|||AL|NE
EVN|A03|20250801163000
PID|1||MRN-78204913^^^IUHEALTH^MR||Faulkner^Russell^Dean^^||19580920|M||2106-3^White^CDCREC|1423 E Third St^^Bloomington^IN^47401^USA||^PRN^PH^^1^812^5553234|||||||672-50-8139
PV1|1|I|MED^2W^212||||2095183746^Hess^Lorraine^B^^^MD|2095183746^Hess^Lorraine^B^^^MD||MED||||1|||||I|VN-20250728-0891^^^IUHEALTH^VN|||||||||||||||||||20250728143000||||||||20250801163000
DG1|1||J15.9^Unspecified bacterial pneumonia^ICD10|||A
DG1|2||N17.9^Acute kidney failure, unspecified^ICD10|||A
```
