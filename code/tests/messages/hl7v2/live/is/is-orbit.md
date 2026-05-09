# Orbit - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Surgical admission

```
MSH|^~\&|ORBIT|SKURDST_LSH|SAGA|LANDSPITALI|20250312083000||ADT^A01^ADT_A01|MSG00001|P|2.5|||AL|NE||IS
EVN|A01|20250312083000|||VEDIS_HALLDORSDOTTIR
PID|1||1709913824^^^THJODSKRA^NI||Bergsson^Hjörtur^Reynir||19910917|M|||Tjarnarstígur 4^^Seltjarnarnes^^170^IS||^PRN^PH^^354^5613472|^WPN^PH^^354^5618205|||S||VIS00100234|||||||||||IS
PV1|1|I|SKURDST^RM04^BED02^LSH^^^^SKURDST_LSH|E|||12345^Vésteinsson^Aron^^^Dr.^^^THJODSKRA||||SUR||||1|||12345^Vésteinsson^Aron^^^Dr.^^^THJODSKRA|IP||||||||||||||||||LSH||A|||20250312083000
PV2|||^Vinstri nýrnataka - Radical nephrectomy||||||20250312||||||||||||||||||||||||||N
DG1|1|I10|C64^Illkynja æxli í nýra^ICD-10|Renal cell carcinoma||A
IN1|1|SJT001|SJUKRATRYGGINGAR ISLANDS|Sjúkratryggingar Íslands^^Laugavegur 114^^Reykjavík^^105^IS|||||||||||||||||||||||||||||||||1709913824
```

---

## 2. ADT^A02 - Transfer to OR

```
MSH|^~\&|ORBIT|SKURDST_LSH|SAGA|LANDSPITALI|20250312091500||ADT^A02^ADT_A02|MSG00002|P|2.5|||AL|NE||IS
EVN|A02|20250312091500|||VEDIS_HALLDORSDOTTIR
PID|1||0408843127^^^THJODSKRA^NI||Hákonardóttir^Iðunn^Brynja||19840804|F|||Engjavegur 8^^Hafnarfjörður^^220^IS||^PRN^PH^^354^5642089||||S||VIS00100235
PV1|1|I|SKURDST^AÐGERÐARSTOFA_03^BED01^LSH^^^^SKURDST_LSH|U|||23456^Brynjólfsdóttir^Sigríður^^^Dr.^^^THJODSKRA||||SUR||||1|||23456^Brynjólfsdóttir^Sigríður^^^Dr.^^^THJODSKRA|IP||||||||||||||||||LSH||A|||20250312091500
PV2|||^Liðskiptaaðgerð á hné - Total knee replacement
```

---

## 3. ADT^A02 - Transfer to PACU (post-anesthesia care)

```
MSH|^~\&|ORBIT|SKURDST_LSH|SAGA|LANDSPITALI|20250312121500||ADT^A02^ADT_A02|MSG00003|P|2.5|||AL|NE||IS
EVN|A02|20250312121500|||LARA_HJALMARSDOTTIR
PID|1||0408843127^^^THJODSKRA^NI||Hákonardóttir^Iðunn^Brynja||19840804|F|||Engjavegur 8^^Hafnarfjörður^^220^IS||^PRN^PH^^354^5642089||||S||VIS00100235
PV1|1|I|VAKN^RM01^BED03^LSH^^^^VAKNARDEILD_LSH|U|||23456^Brynjólfsdóttir^Sigríður^^^Dr.^^^THJODSKRA||||SUR||||1|||23456^Brynjólfsdóttir^Sigríður^^^Dr.^^^THJODSKRA|IP||||||||||||||||||LSH||A|||20250312121500
PV2|||^Eftirlit eftir svæfingu - Post-anesthesia recovery
```

---

## 4. ADT^A03 - Surgical discharge

```
MSH|^~\&|ORBIT|SKURDST_LSH|SAGA|LANDSPITALI|20250315100000||ADT^A03^ADT_A03|MSG00004|P|2.5|||AL|NE||IS
EVN|A03|20250315100000|||VEDIS_HALLDORSDOTTIR
PID|1||1709913824^^^THJODSKRA^NI||Bergsson^Hjörtur^Reynir||19910917|M|||Tjarnarstígur 4^^Seltjarnarnes^^170^IS||^PRN^PH^^354^5613472||||S||VIS00100234
PV1|1|I|SKURDST^RM04^BED02^LSH^^^^SKURDST_LSH|E|||12345^Vésteinsson^Aron^^^Dr.^^^THJODSKRA||||SUR||||1|||12345^Vésteinsson^Aron^^^Dr.^^^THJODSKRA|IP||||||||||||||||||LSH||A|||20250312083000|||20250315100000
DG1|1|I10|C64^Illkynja æxli í nýra^ICD-10|Renal cell carcinoma - post nephrectomy||F
```

---

## 5. ORM^O01 - Surgical procedure order

```
MSH|^~\&|ORBIT|SKURDST_LSH|SAGA|LANDSPITALI|20250310140000||ORM^O01^ORM_O01|MSG00005|P|2.5|||AL|NE||IS
PID|1||1205773651^^^THJODSKRA^NI||Tryggvason^Magnús^Steinar||19770512|M|||Drápuhlíð 18^^Reykjavík^^105^IS||^PRN^PH^^354^5681432||||M||VIS00100236
PV1|1|I|SKURDST^RM01^BED01^LSH^^^^SKURDST_LSH|E|||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA||||SUR||||1|||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA|IP
ORC|NW|ORD202503001^ORBIT||GRP202503001^ORBIT|SC||1^ONCE^^20250312080000^^S||20250310140000|VEDIS_HALLDORSDOTTIR||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA||^WPN^PH^^354^5434000|20250310140000||SKURDST_LSH^Skurðstofa Landspítala^L
OBR|1|ORD202503001^ORBIT||49585^Laparoscopic cholecystectomy^CPT|||20250312080000||||||||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA||||||||||1^ONCE^^20250312080000^^S
DG1|1|I10|K80.2^Gallstones with cholecystitis^ICD-10|Gallsteinar með gallblöðrubólgu||A
```

---

## 6. ORM^O01 - Pre-operative lab order

```
MSH|^~\&|ORBIT|SKURDST_LSH|FLEXLAB|LANDSPITALI_LAB|20250311090000||ORM^O01^ORM_O01|MSG00006|P|2.5|||AL|NE||IS
PID|1||1205773651^^^THJODSKRA^NI||Tryggvason^Magnús^Steinar||19770512|M|||Drápuhlíð 18^^Reykjavík^^105^IS||^PRN^PH^^354^5681432||||M||VIS00100236
PV1|1|I|SKURDST^RM01^BED01^LSH^^^^SKURDST_LSH|E|||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA||||SUR
ORC|NW|ORD202503002^ORBIT||GRP202503002^ORBIT|SC||1^ONCE^^20250311^^S||20250311090000|VEDIS_HALLDORSDOTTIR||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA
OBR|1|ORD202503002^ORBIT||PREOP_PANEL^Pre-operative laboratory panel^LOCAL|||20250311100000||||||||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA|||||||||1^ONCE^^20250311^^S
OBR|2|ORD202503002^ORBIT||CBC^Complete blood count^LOCAL|||20250311100000||||||||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA
OBR|3|ORD202503002^ORBIT||BMP^Basic metabolic panel^LOCAL|||20250311100000||||||||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA
OBR|4|ORD202503002^ORBIT||COAG^Coagulation panel^LOCAL|||20250311100000||||||||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA
OBR|5|ORD202503002^ORBIT||XMATCH^Type and crossmatch^LOCAL|||20250311100000||||||||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA
```

---

## 7. ORM^O01 - Pre-operative imaging order

```
MSH|^~\&|ORBIT|SKURDST_LSH|RAFÖRNINN|LANDSPITALI_RAD|20250311110000||ORM^O01^ORM_O01|MSG00007|P|2.5|||AL|NE||IS
PID|1||1308946207^^^THJODSKRA^NI||Egilsdóttir^Ragnhildur^Thelma||19940813|F|||Sólheimar 32^^Reykjavík^^104^IS||^PRN^PH^^354^5773018||||S||VIS00100237
PV1|1|I|SKURDST^RM02^BED01^LSH^^^^SKURDST_LSH|E|||45678^Tryggvason^Steinarr^^^Dr.^^^THJODSKRA||||SUR
ORC|NW|ORD202503003^ORBIT||GRP202503003^ORBIT|SC||1^ONCE^^20250311^^S||20250311110000|ASGRIMUR_THORLAKSSON||45678^Tryggvason^Steinarr^^^Dr.^^^THJODSKRA
OBR|1|ORD202503003^ORBIT||71260^CT Chest with contrast^CPT|||20250311130000||||||||45678^Tryggvason^Steinarr^^^Dr.^^^THJODSKRA|||||||||1^ONCE^^20250311^^S
DG1|1|I10|J84.1^Lungnasjúkdómur^ICD-10|Interstitial pulmonary disease||A
```

---

## 8. SIU^S12 - Schedule surgery

```
MSH|^~\&|ORBIT|SKURDST_LSH|SAGA|LANDSPITALI|20250308100000||SIU^S12^SIU_S12|MSG00008|P|2.5|||AL|NE||IS
SCH|SCH202503001^ORBIT|APT202503001^ORBIT|||||SURG^Surgery^LOCAL|NORMAL^Normal priority^LOCAL|120^MIN|^^60^20250312080000^20250312100000|45678^Tryggvason^Steinarr^^^Dr.^^^THJODSKRA|^WPN^PH^^354^5434000|SKURDST^AÐGERÐARSTOFA_01^^LSH|45678^Tryggvason^Steinarr^^^Dr.^^^THJODSKRA||BOOKED
PID|1||1308946207^^^THJODSKRA^NI||Egilsdóttir^Ragnhildur^Thelma||19940813|F|||Sólheimar 32^^Reykjavík^^104^IS||^PRN^PH^^354^5773018
PV1|1|I|SKURDST^AÐGERÐARSTOFA_01^BED01^LSH^^^^SKURDST_LSH|E|||45678^Tryggvason^Steinarr^^^Dr.^^^THJODSKRA||||SUR
RGS|1|A
AIS|1|A|49505^Inguinal hernia repair^CPT|20250312080000|||120^MIN
AIG|1|A|45678^Tryggvason^Steinarr^^^Dr.^^^THJODSKRA|SURGEON^Surgeon^LOCAL
AIG|2|A|56789^Pétursdóttir^Ásrún^^^Dr.^^^THJODSKRA|ANESTHESIOLOGIST^Anesthesiologist^LOCAL
AIL|1|A|SKURDST^AÐGERÐARSTOFA_01^^LSH||20250312080000|||120^MIN
AIP|1|A|45678^Tryggvason^Steinarr^^^Dr.^^^THJODSKRA|SURGEON^Surgeon^LOCAL
```

---

## 9. SIU^S14 - Modify surgical schedule

```
MSH|^~\&|ORBIT|SKURDST_LSH|SAGA|LANDSPITALI|20250310150000||SIU^S14^SIU_S12|MSG00009|P|2.5|||AL|NE||IS
SCH|SCH202503001^ORBIT|APT202503001^ORBIT|||||SURG^Surgery^LOCAL|URGENT^Urgent priority^LOCAL|150^MIN|^^60^20250312060000^20250312083000|45678^Tryggvason^Steinarr^^^Dr.^^^THJODSKRA|^WPN^PH^^354^5434000|SKURDST^AÐGERÐARSTOFA_02^^LSH|45678^Tryggvason^Steinarr^^^Dr.^^^THJODSKRA||BOOKED
PID|1||1308946207^^^THJODSKRA^NI||Egilsdóttir^Ragnhildur^Thelma||19940813|F|||Sólheimar 32^^Reykjavík^^104^IS||^PRN^PH^^354^5773018
PV1|1|I|SKURDST^AÐGERÐARSTOFA_02^BED01^LSH^^^^SKURDST_LSH|U|||45678^Tryggvason^Steinarr^^^Dr.^^^THJODSKRA||||SUR
RGS|1|A
AIS|1|A|49505^Inguinal hernia repair^CPT|20250312060000|||150^MIN
AIG|1|A|45678^Tryggvason^Steinarr^^^Dr.^^^THJODSKRA|SURGEON^Surgeon^LOCAL
AIG|2|A|67890^Skúlason^Davíð^^^Dr.^^^THJODSKRA|ANESTHESIOLOGIST^Anesthesiologist^LOCAL
AIL|1|A|SKURDST^AÐGERÐARSTOFA_02^^LSH||20250312060000|||150^MIN
```

---

## 10. SIU^S12 - Schedule pre-op assessment

```
MSH|^~\&|ORBIT|SKURDST_LSH|SAGA|LANDSPITALI|20250305143000||SIU^S12^SIU_S12|MSG00010|P|2.5|||AL|NE||IS
SCH|SCH202503002^ORBIT|APT202503002^ORBIT|||||PREOP^Pre-operative assessment^LOCAL|NORMAL^Normal priority^LOCAL|45^MIN|^^30^20250311090000^20250311094500|56789^Pétursdóttir^Ásrún^^^Dr.^^^THJODSKRA|^WPN^PH^^354^5434000|DAGSKURD^STOFA_04^^LSH|56789^Pétursdóttir^Ásrún^^^Dr.^^^THJODSKRA||BOOKED
PID|1||1205773651^^^THJODSKRA^NI||Tryggvason^Magnús^Steinar||19770512|M|||Drápuhlíð 18^^Reykjavík^^105^IS||^PRN^PH^^354^5681432
PV1|1|O|DAGSKURD^STOFA_04^BED01^LSH^^^^DAGSKURDDEILD_LSH|R|||56789^Pétursdóttir^Ásrún^^^Dr.^^^THJODSKRA||||ANE
RGS|1|A
AIS|1|A|PREOP_ASSESS^Pre-operative anesthesia assessment^LOCAL|20250311090000|||45^MIN
AIG|1|A|56789^Pétursdóttir^Ásrún^^^Dr.^^^THJODSKRA|ANESTHESIOLOGIST^Anesthesiologist^LOCAL
AIL|1|A|DAGSKURD^STOFA_04^^LSH||20250311090000|||45^MIN
```

---

## 11. ORU^R01 - Pre-operative assessment result

```
MSH|^~\&|ORBIT|SKURDST_LSH|SAGA|LANDSPITALI|20250311103000||ORU^R01^ORU_R01|MSG00011|P|2.5|||AL|NE||IS
PID|1||1205773651^^^THJODSKRA^NI||Tryggvason^Magnús^Steinar||19770512|M|||Drápuhlíð 18^^Reykjavík^^105^IS||^PRN^PH^^354^5681432||||M||VIS00100236
PV1|1|I|SKURDST^RM01^BED01^LSH^^^^SKURDST_LSH|E|||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA||||SUR
ORC|RE|ORD202503004^ORBIT||GRP202503004^ORBIT|||||||56789^Pétursdóttir^Ásrún^^^Dr.^^^THJODSKRA
OBR|1|ORD202503004^ORBIT||PREOP_ASS^Pre-operative anesthesia assessment^LOCAL|||20250311093000|||||||||56789^Pétursdóttir^Ásrún^^^Dr.^^^THJODSKRA|||||||F
OBX|1|CE|ASA_CLASS^ASA Physical Status^LOCAL||III^ASA III - Severe systemic disease^LOCAL||||||F
OBX|2|TX|AIRWAY^Airway Assessment^LOCAL||Mallampati II. Þykkur háls, stuttur. Gæti þurft myndband-barkaþræðingu.||||||F
OBX|3|TX|ALLERGIES^Known Allergies^LOCAL||Penisillín - útbrot. Latex - án viðbragða en varúð ráðlögð.||||||F
OBX|4|TX|MEDS^Current Medications^LOCAL||Metoprolol 50mg daglega, Atorvastatin 20mg að kvöldi||||||F
OBX|5|CE|ANES_PLAN^Anesthesia Plan^LOCAL||GA_ETT^General anesthesia with endotracheal tube^LOCAL||||||F
OBX|6|TX|NOTES^Pre-op Notes^LOCAL||Sjúklingur hæfur til svæfingar. Blóðþrýstingur vel meðhöndlaður. Fasta frá miðnætti.||||||F
```

---

## 12. ORU^R01 - Anesthesia record

```
MSH|^~\&|ORBIT|SKURDST_LSH|CAMBIO_CIS|LANDSPITALI|20250312120000||ORU^R01^ORU_R01|MSG00012|P|2.5|||AL|NE||IS
PID|1||1205773651^^^THJODSKRA^NI||Tryggvason^Magnús^Steinar||19770512|M|||Drápuhlíð 18^^Reykjavík^^105^IS||^PRN^PH^^354^5681432||||M||VIS00100236
PV1|1|I|SKURDST^AÐGERÐARSTOFA_01^BED01^LSH^^^^SKURDST_LSH|E|||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA||||SUR
ORC|RE|ORD202503005^ORBIT||GRP202503005^ORBIT|||||||56789^Pétursdóttir^Ásrún^^^Dr.^^^THJODSKRA
OBR|1|ORD202503005^ORBIT||ANES_REC^Anesthesia Record^LOCAL|||20250312082000|20250312115000||||||||56789^Pétursdóttir^Ásrún^^^Dr.^^^THJODSKRA|||||||F
OBX|1|CE|ANES_TYPE^Anesthesia Type^LOCAL||GA^General Anesthesia^LOCAL||||||F
OBX|2|TS|INTUB_TIME^Intubation Time^LOCAL||20250312082500||||||F
OBX|3|TS|EXTUB_TIME^Extubation Time^LOCAL||20250312114500||||||F
OBX|4|TX|INDUCTION^Induction Agents^LOCAL||Propofol 200mg IV, Fentanyl 150mcg IV, Rocuronium 50mg IV||||||F
OBX|5|TX|MAINTENANCE^Maintenance^LOCAL||Sevoflurane 2% í O2/loft blöndu, Remifentanil 0.1mcg/kg/mín||||||F
OBX|6|NM|EBL^Estimated Blood Loss^LOCAL||250|mL|||||F
OBX|7|TX|FLUIDS^IV Fluids^LOCAL||Ringer laktat 2000mL, NaCl 0.9% 500mL||||||F
OBX|8|NM|URINE^Urine Output^LOCAL||450|mL|||||F
OBX|9|TX|COMPLICATIONS^Intraoperative Complications^LOCAL||Engar fylgikvillar. Stöðug lífsmörk í gegnum aðgerð.||||||F
```

---

## 13. ORU^R01 - Surgical report with base64 ED OBX (PDF operative note)

```
MSH|^~\&|ORBIT|SKURDST_LSH|SAGA|LANDSPITALI|20250312143000||ORU^R01^ORU_R01|MSG00013|P|2.5|||AL|NE||IS
PID|1||1205773651^^^THJODSKRA^NI||Tryggvason^Magnús^Steinar||19770512|M|||Drápuhlíð 18^^Reykjavík^^105^IS||^PRN^PH^^354^5681432||||M||VIS00100236
PV1|1|I|SKURDST^RM01^BED01^LSH^^^^SKURDST_LSH|E|||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA||||SUR
ORC|RE|ORD202503006^ORBIT||GRP202503006^ORBIT|||||||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA
OBR|1|ORD202503006^ORBIT||SURG_RPT^Surgical Report^LOCAL|||20250312082000|20250312115000||||||||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA|||||||F
OBX|1|TX|PROCEDURE^Procedure Performed^LOCAL||Laparoscopic cholecystectomy. Gallblaðra fjarlægð með kviðsjártækni.||||||F
OBX|2|TX|FINDINGS^Operative Findings^LOCAL||Bólgin gallblaðra með mörgum gallsteinum. Engar samvaxtar. Gallgangur greindist vel.||||||F
OBX|3|ED|PDF^Operative Note PDF^LOCAL||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKE9wZXJhdGl2ZSBOb3RlIC0gTGFwYXJvc2NvcGljIENob2xlY3lzdGVjdG9teSkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago=||||||F
```

---

## 14. MDM^T02 - Operative note

```
MSH|^~\&|ORBIT|SKURDST_LSH|SAGA|LANDSPITALI|20250312150000||MDM^T02^MDM_T02|MSG00014|P|2.5|||AL|NE||IS
EVN|T02|20250312150000|||VEDIS_HALLDORSDOTTIR
PID|1||1205773651^^^THJODSKRA^NI||Tryggvason^Magnús^Steinar||19770512|M|||Drápuhlíð 18^^Reykjavík^^105^IS||^PRN^PH^^354^5681432||||M||VIS00100236
PV1|1|I|SKURDST^RM01^BED01^LSH^^^^SKURDST_LSH|E|||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA||||SUR
TXA|1|OP^Operative Note^LOCAL|TX|20250312150000|34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA||20250312150000||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA||||DOC202503001^ORBIT||||||AU
OBX|1|TX|TITLE^Document Title^LOCAL||Aðgerðarskýrsla - Laparoscopic cholecystectomy||||||F
OBX|2|TX|PREOP_DX^Pre-operative Diagnosis^LOCAL||K80.2 Gallsteinar með bráðri gallblöðrubólgu||||||F
OBX|3|TX|POSTOP_DX^Post-operative Diagnosis^LOCAL||K80.2 Gallsteinar með langvinnri gallblöðrubólgu||||||F
OBX|4|TX|PROC_DESC^Procedure Description^LOCAL||Sjúklingur í almennri svæfingu. Fjórir trocar settir í kviðarhol. Gallblaðra greind og laus úr lifur. Cystic duct og cystic artery klippt og skorin. Gallblaðra fjarlægð í gegnum naflapoka. Blæðingastilling staðfest. Trocar fjarlægðir og sár lokuð.||||||F
OBX|5|TX|SURGEON^Surgeon^LOCAL||Dr. Þorgerður Hauksdóttir, yfirlæknir skurðlækninga||||||F
OBX|6|TX|ASSISTANT^Assistant^LOCAL||Dr. Sölvi Bárðarson, deildarlæknir||||||F
```

---

## 15. ORU^R01 - Post-operative vital signs

```
MSH|^~\&|ORBIT|VAKNARDEILD_LSH|CAMBIO_CIS|LANDSPITALI|20250312130000||ORU^R01^ORU_R01|MSG00015|P|2.5|||AL|NE||IS
PID|1||1205773651^^^THJODSKRA^NI||Tryggvason^Magnús^Steinar||19770512|M|||Drápuhlíð 18^^Reykjavík^^105^IS||^PRN^PH^^354^5681432||||M||VIS00100236
PV1|1|I|VAKN^RM01^BED02^LSH^^^^VAKNARDEILD_LSH|E|||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA||||SUR
ORC|RE|ORD202503007^ORBIT||GRP202503007^ORBIT|||||||78901^Marteinsdóttir^Hugrún^^^Hjúkr.^^^THJODSKRA
OBR|1|ORD202503007^ORBIT||VITALS^Post-operative Vital Signs^LOCAL|||20250312130000|||||||||78901^Marteinsdóttir^Hugrún^^^Hjúkr.^^^THJODSKRA|||||||F
OBX|1|NM|8480-6^Systolic BP^LN||138|mmHg|90-140||||F
OBX|2|NM|8462-4^Diastolic BP^LN||82|mmHg|60-90||||F
OBX|3|NM|8867-4^Heart Rate^LN||78|bpm|60-100||||F
OBX|4|NM|8310-5^Body Temperature^LN||36.8|Cel|36.1-37.2||||F
OBX|5|NM|9279-1^Respiratory Rate^LN||16|/min|12-20||||F
OBX|6|NM|2708-6^SpO2^LN||97|%|95-100||||F
OBX|7|NM|VAS_PAIN^VAS Pain Score^LOCAL||4|{score}|0-3|H|||F
OBX|8|TX|ALDRICH^Aldrete Score^LOCAL||9 af 10. Sjúklingur meðvitaður, öndun góð, hreyfing í öllum útlimum.||||||F
```

---

## 16. ADT^A08 - Update surgical patient

```
MSH|^~\&|ORBIT|SKURDST_LSH|SAGA|LANDSPITALI|20250313080000||ADT^A08^ADT_A01|MSG00016|P|2.5|||AL|NE||IS
EVN|A08|20250313080000|||VEDIS_HALLDORSDOTTIR
PID|1||1205773651^^^THJODSKRA^NI||Tryggvason^Magnús^Steinar||19770512|M|||Drápuhlíð 18^^Reykjavík^^105^IS||^PRN^PH^^354^5681432|^WPN^PH^^354^5681908|||M||VIS00100236
PV1|1|I|SKURDST^RM01^BED01^LSH^^^^SKURDST_LSH|E|||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA||||SUR||||1|||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA|IP||||||||||||||||||LSH||A|||20250312083000
DG1|1|I10|K80.2^Gallsteinar með gallblöðrubólgu^ICD-10|Gallstones with cholecystitis||F
DG1|2|I10|E11.9^Sykursýki tegund 2^ICD-10|Type 2 diabetes mellitus - newly identified||A
AL1|1|DA|PENICILLIN^Penicillin^LOCAL|MO|Útbrot og kláði|20200115
```

---

## 17. ORU^R01 - Pathology specimen from surgery

```
MSH|^~\&|ORBIT|MEINAFR_LSH|FLEXLAB|LANDSPITALI_PATH|20250314160000||ORU^R01^ORU_R01|MSG00017|P|2.5|||AL|NE||IS
PID|1||1205773651^^^THJODSKRA^NI||Tryggvason^Magnús^Steinar||19770512|M|||Drápuhlíð 18^^Reykjavík^^105^IS||^PRN^PH^^354^5681432||||M||VIS00100236
PV1|1|I|SKURDST^RM01^BED01^LSH^^^^SKURDST_LSH|E|||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA||||SUR
ORC|RE|ORD202503008^ORBIT||GRP202503008^ORBIT|||||||89012^Reynisson^Birkir^^^Dr.^^^THJODSKRA
OBR|1|ORD202503008^ORBIT||PATH_SURG^Surgical Pathology^LOCAL|||20250312120000|||||||||89012^Reynisson^Birkir^^^Dr.^^^THJODSKRA|||||||F
OBX|1|TX|SPECIMEN^Specimen Type^LOCAL||Gallblaðra, heil, fjarlægð með kviðsjártækni||||||F
OBX|2|TX|GROSS^Gross Description^LOCAL||Gallblaðra 8.5 x 3.2 x 2.8 cm. Veggþykkt 0.4 cm. Inniheldur þrjá gallsteina, stærsti 1.2 cm. Slímhúð eðlileg á litinn.||||||F
OBX|3|TX|MICRO^Microscopic Description^LOCAL||Langvinn gallblöðrubólga með vægu frumubólguástandi. Rokach-Aschoff holrúm sjást. Ekkert merki um illkynja breytingar.||||||F
OBX|4|CE|DIAGNOSIS^Pathological Diagnosis^LOCAL||CHRONIC_CHOLECYSTITIS^Langvinn gallblöðrubólga með gallsteinum^LOCAL||||||F
OBX|5|TX|COMMENT^Pathologist Comment^LOCAL||Góðkynja vefjafræði. Engin frekari rannsókn þörf.||||||F
```

---

## 18. ORU^R01 - Post-op report with base64 ED OBX (PDF recovery record)

```
MSH|^~\&|ORBIT|VAKNARDEILD_LSH|SAGA|LANDSPITALI|20250313140000||ORU^R01^ORU_R01|MSG00018|P|2.5|||AL|NE||IS
PID|1||0408843127^^^THJODSKRA^NI||Hákonardóttir^Iðunn^Brynja||19840804|F|||Engjavegur 8^^Hafnarfjörður^^220^IS||^PRN^PH^^354^5642089||||S||VIS00100235
PV1|1|I|VAKN^RM02^BED01^LSH^^^^VAKNARDEILD_LSH|U|||23456^Brynjólfsdóttir^Sigríður^^^Dr.^^^THJODSKRA||||SUR
ORC|RE|ORD202503009^ORBIT||GRP202503009^ORBIT|||||||78901^Marteinsdóttir^Hugrún^^^Hjúkr.^^^THJODSKRA
OBR|1|ORD202503009^ORBIT||RECOV_RPT^Post-operative Recovery Report^LOCAL|||20250312121500|20250313140000||||||||78901^Marteinsdóttir^Hugrún^^^Hjúkr.^^^THJODSKRA|||||||F
OBX|1|TX|RECOVERY^Recovery Summary^LOCAL||Sjúklingur jákvæð eftir liðskiptaaðgerð á hné. Engar fylgikvillar eftir svæfingu. Verkjameðferð vinnur vel.||||||F
OBX|2|ED|PDF^Recovery Record PDF^LOCAL||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA1MAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKFBvc3Qtb3BlcmF0aXZlIFJlY292ZXJ5IFJlY29yZCAtIFRvdGFsIEtuZWUgUmVwbGFjZW1lbnQpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmo=||||||F
```

---

## 19. ADT^A04 - Day surgery registration

```
MSH|^~\&|ORBIT|DAGSKURD_LSH|SAGA|LANDSPITALI|20250320070000||ADT^A04^ADT_A01|MSG00019|P|2.5|||AL|NE||IS
EVN|A04|20250320070000|||ASGRIMUR_THORLAKSSON
PID|1||1102884371^^^THJODSKRA^NI||Brandsdóttir^Inga^Karítas||19880211|F|||Holtsbúð 7^^Garðabær^^210^IS||^PRN^PH^^354^5670213|^WPN^PH^^354^5670214|||G||VIS00100238|||||||||||IS
PV1|1|O|DAGSKURD^STOFA_02^BED01^LSH^^^^DAGSKURDDEILD_LSH|R|||90123^Vilhjálmsson^Atli^^^Dr.^^^THJODSKRA||||SUR||||1|||90123^Vilhjálmsson^Atli^^^Dr.^^^THJODSKRA|OP||||||||||||||||||LSH||A|||20250320070000
PV2|||^Hnéliðspeglun - Knee arthroscopy||||||20250320||||||||||||||||||||||||||N
DG1|1|I10|M23.2^Liðþófsáverki í hné^ICD-10|Meniscal tear||A
```

---

## 20. ORM^O01 - Post-operative medication order

```
MSH|^~\&|ORBIT|SKURDST_LSH|SAGA|LANDSPITALI|20250312133000||ORM^O01^ORM_O01|MSG00020|P|2.5|||AL|NE||IS
PID|1||1205773651^^^THJODSKRA^NI||Tryggvason^Magnús^Steinar||19770512|M|||Drápuhlíð 18^^Reykjavík^^105^IS||^PRN^PH^^354^5681432||||M||VIS00100236
PV1|1|I|VAKN^RM01^BED02^LSH^^^^VAKNARDEILD_LSH|E|||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA||||SUR
ORC|NW|ORD202503010^ORBIT||GRP202503010^ORBIT|SC||1^Q6H^^20250312133000^^S||20250312133000|VEDIS_HALLDORSDOTTIR||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA
OBR|1|ORD202503010^ORBIT||POSTOP_MED^Post-operative medications^LOCAL|||20250312133000||||||||34567^Hauksdóttir^Þorgerður^^^Dr.^^^THJODSKRA
RXO|PARA1000^Paracetamol 1000mg^LOCAL|1000|mg||PO^Oral^HL70162||||||1^TAB
RXR|PO^Oral^HL70162
RXO|IBUP400^Ibuprofen 400mg^LOCAL|400|mg||PO^Oral^HL70162||||||1^TAB
RXR|PO^Oral^HL70162
RXO|MORPH10^Morphine 10mg^LOCAL|10|mg||IV^Intravenous^HL70162||||||1^DOSE
RXR|IV^Intravenous^HL70162
RXO|ONDANS4^Ondansetron 4mg^LOCAL|4|mg||IV^Intravenous^HL70162||||||1^DOSE
RXR|IV^Intravenous^HL70162
```
