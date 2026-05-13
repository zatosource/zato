# Nuance PowerScribe - real HL7v2 ER7 messages

---

## 1. ORU^R01 - Chest X-ray PA/lateral final report from UPMC Presbyterian

```
MSH|^~\&|POWERSCRIBE|UPMC_PRESBYTERIAN|EPIC_RADIANT|UPMC|20260508143022||ORU^R01|PS2026050814302201|P|2.3
PID|||MRN7218340^^^UPMC||ZIELINSKI^WANDA^FRANCES||19571023|F|||1934 Brownsville Rd^^Pittsburgh^PA^15210||412-555-8271|||||||321-76-9048
PV1||O|RAD^XR01^1||||RAD10234^KWON^DANIEL^S.^^DR.^MD|REF90821^MCLAUGHLIN^BRIDGET^A.^^DR.^MD||RAD||||||||V20260508001
ORC|RE|ORD7839201
OBR||ORD7839201|RAD4420183|71020^CHEST PA AND LATERAL^CPT||||20260508100000||||||||RAD10234^KWON^DANIEL^S.^^DR.^MD|412-555-7000||||||F|||||||RAD10234^KWON^DANIEL^S.^^DR.^MD
OBX|1|FT|GDT^REPORT TEXT^PS360||EXAMINATION: Chest PA and lateral\.br\\.br\CLINICAL INDICATION: Cough, rule out pneumonia\.br\\.br\COMPARISON: Chest radiograph dated 2026-03-15\.br\\.br\TECHNIQUE: PA and lateral views of the chest\.br\\.br\FINDINGS:\.br\The lungs are clear bilaterally. No focal consolidation, pleural effusion, or pneumothorax. The cardiac silhouette is normal in size. The mediastinal contours are unremarkable. No acute osseous abnormality.\.br\\.br\IMPRESSION:\.br\1. No acute cardiopulmonary disease.\.br\2. Unchanged from prior examination.||||||F
ZBR|12|1|RAD10234^KWON^DANIEL^S.^^^^^Dict|RAD10234^KWON^DANIEL^S.^^^^Sign^Dict||||2^Final|NOR
ZBX|1|12|1|EXAMINATION: Chest PA and lateral\.br\CLINICAL INDICATION: Cough, rule out pneumonia\.br\COMPARISON: Chest radiograph dated 2026-03-15\.br\TECHNIQUE: PA and lateral views of the chest\.br\FINDINGS:\.br\The lungs are clear bilaterally. No focal consolidation, pleural effusion, or pneumothorax. The cardiac silhouette is normal in size. The mediastinal contours are unremarkable. No acute osseous abnormality.\.br\IMPRESSION:\.br\1. No acute cardiopulmonary disease.\.br\2. Unchanged from prior examination.
```

---

## 2. ORM^O01 - CT abdomen/pelvis with contrast order from Penn Medicine HUP

```
MSH|^~\&|EPIC_RADIANT|HUP|PSCRIBE360|HUP_RAD|20260509071500||ORM^O01|EP2026050907150001|P|2.3
PID|||MRN4601839^^^PENNMED||DIAZ^CARLOS^MIGUEL||19680419|M|||2218 Lombard St^^Philadelphia^PA^19146||215-555-3927|||||||482-19-7653
PV1||I|MED^4E^412A||||ATT20031^OKONKWO^CHIOMA^R.^^DR.^MD|REF30045^BRANNIGAN^NEIL^P.^^DR.^MD||MED||||||||ACCT44829001
ORC|NW|ORD9920381
OBR||ORD9920381||74178^CT ABDOMEN PELVIS WITH CONTRAST^CPT||||20260509080000||||||||ATT20031^OKONKWO^CHIOMA^R.^^DR.^MD|215-555-4000||||||||||||||Abdominal pain, weight loss
```

---

## 3. ORU^R01 - MRI brain with and without contrast final report from Geisinger Danville

```
MSH|^~\&|NUANCE_PS|GEISINGER_DANVILLE|CERNER_RAD|GEISINGER|20260507161230||ORU^R01|NPS20260507161230A|P|2.3
PID|||MRN5839021^^^GMC||CALLAHAN^TERRENCE^JOSEPH||19820711|M|||208 Iron St^^Danville^PA^17821||570-555-4493|||||||710-38-2564
PV1||O|RAD^MRI02^1||||NR40092^MUKHOPADHYAY^SUNITA^R.^^DR.^MD|REF55210^GALLAGHER^BRENDAN^T.^^DR.^MD||RAD||||||||V20260507002
ORC|RE|ORD6612044
OBR||ORD6612044|RAD5590321|70553^MRI BRAIN W AND WO CONTRAST^CPT||||20260507110000||||||||NR40092^MUKHOPADHYAY^SUNITA^R.^^DR.^MD|570-555-1000||||||F|||||||NR40092^MUKHOPADHYAY^SUNITA^R.^^DR.^MD
OBX|1|FT|GDT^REPORT TEXT^PS360||EXAMINATION: MRI Brain with and without contrast\.br\\.br\CLINICAL INDICATION: Persistent headaches, rule out intracranial mass\.br\\.br\COMPARISON: None available\.br\\.br\TECHNIQUE: Multiplanar, multisequence MRI of the brain was performed before and after intravenous administration of 15 mL Gadavist.\.br\\.br\FINDINGS:\.br\Brain parenchyma demonstrates normal signal intensity on all pulse sequences. No evidence of acute infarct on diffusion-weighted imaging. No intracranial mass, mass effect, or midline shift. The ventricles and sulci are normal in size and configuration. No abnormal intracranial enhancement following contrast administration. The major intracranial flow voids are preserved. Visualized paranasal sinuses and mastoid air cells are clear. The orbits are unremarkable.\.br\\.br\IMPRESSION:\.br\1. Normal MRI of the brain with and without contrast.\.br\2. No evidence of intracranial mass or acute infarction.||||||F
ZBR|18|1|NR40092^MUKHOPADHYAY^SUNITA^R.^^^^^Dict|NR40092^MUKHOPADHYAY^SUNITA^R.^^^^Sign^Dict||||2^Final|NOR
ZBX|1|18|1|EXAMINATION: MRI Brain with and without contrast\.br\CLINICAL INDICATION: Persistent headaches, rule out intracranial mass\.br\COMPARISON: None available\.br\TECHNIQUE: Multiplanar, multisequence MRI of the brain was performed before and after intravenous administration of 15 mL Gadavist.\.br\FINDINGS:\.br\Brain parenchyma demonstrates normal signal intensity on all pulse sequences. No evidence of acute infarct on diffusion-weighted imaging. No intracranial mass, mass effect, or midline shift. The ventricles and sulci are normal in size and configuration. No abnormal intracranial enhancement following contrast administration.\.br\IMPRESSION:\.br\1. Normal MRI of the brain with and without contrast.\.br\2. No evidence of intracranial mass or acute infarction.
```

---

## 4. ADT^A04 - Outpatient registration for mammography at Lehigh Valley Hospital

```
MSH|^~\&|EPIC_ADT|LVHN|POWERSCRIBE|LVHN_RAD|20260506084500||ADT^A04|ADT20260506084500A|P|2.3
EVN|A04|20260506084500
PID|||MRN2930471^^^LVHN||FUENTES^MARISOL^ADRIANA||19750318|F|||819 Allen St^^Allentown^PA^18102||610-555-6139|||||||593-41-8702
PV1||O|RAD^MAMM01^1||||RAD30011^TRIEU^LINH^T.^^DR.^MD|||RAD||||||||V20260506003|||||||||||||||||||||||||||20260506084500
IN1|1||INS200|GEISINGER HEALTH PLAN|100 N Academy Ave^^Danville^PA^17822||||||||||||||||||||||||||||||||||||||||||||42
```

---

## 5. ORU^R01 - CT head without contrast with critical finding from Reading Hospital

```
MSH|^~\&|POWERSCRIBE|READING_HOSPITAL|MEDITECH|TOWER_HEALTH|20260505223015||ORU^R01|PS2026050522301501|P|2.3
PID|||MRN6104829^^^TOWER||WASHINGTON^JEROME^ALLEN||19490812|M|||457 Schuylkill Ave^^Reading^PA^19601||484-555-7104|||||||834-26-1097
PV1||E|ED^BED07^1||||ER80032^PIRETTI^VINCENT^J.^^DR.^MD|REF40019^DONNELLY^COLLEEN^L.^^DR.^MD||EM||||||||V20260505010
ORC|RE|ORD3381092
OBR||ORD3381092|RAD2280194|70450^CT HEAD WITHOUT CONTRAST^CPT||||20260505214500||||||||NR50011^BHATT^ANIL^K.^^DR.^MD|484-555-6000||||||F|||||||NR50011^BHATT^ANIL^K.^^DR.^MD
OBX|1|FT|GDT^REPORT TEXT^PS360||EXAMINATION: CT Head without contrast\.br\\.br\CLINICAL INDICATION: Fall with loss of consciousness, anticoagulation therapy\.br\\.br\COMPARISON: None\.br\\.br\TECHNIQUE: Axial CT images of the head were obtained without intravenous contrast.\.br\\.br\FINDINGS:\.br\There is a crescent-shaped hyperdense extra-axial collection along the right frontoparietal convexity measuring up to 12 mm in maximal thickness, consistent with acute subdural hematoma. Associated 6 mm leftward midline shift is present. There is effacement of the right lateral ventricle. No uncal herniation. Scattered periventricular hypodensities likely represent chronic small vessel ischemic changes. No skull fracture identified.\.br\\.br\IMPRESSION:\.br\1. CRITICAL: Acute right frontoparietal subdural hematoma with 6 mm midline shift. Neurosurgical consultation recommended.\.br\2. Chronic small vessel ischemic changes.||||||F
OBX|2|FT|GDT^CRITICAL RESULT^PS360||CRITICAL RESULT COMMUNICATED: Dr. Vincent Piretti, ED attending, notified by phone at 22:35 on 2026-05-05. Read back confirmed.||||||F
ZBR|25|1|NR50011^BHATT^ANIL^K.^^^^^Dict|NR50011^BHATT^ANIL^K.^^^^Sign^Dict||||2^Final|ABN
ZBX|1|25|1|CRITICAL: Acute right frontoparietal subdural hematoma with 6 mm midline shift. Neurosurgical consultation recommended.
```

---

## 6. ORM^O01 - Ultrasound abdomen complete order from St. Luke's Bethlehem

```
MSH|^~\&|CERNER_ORM|SLUHN_BETHLEHEM|POWERSCRIBE|SLUHN_RAD|20260504110030||ORM^O01|CE20260504110030B|P|2.3
PID|||MRN8392014^^^SLUHN||KESSLER^JOAN^ELAINE||19630927|F|||211 Broad St^^Bethlehem^PA^18018||610-555-2047|||||||249-81-3560
PV1||O|RAD^US02^1||||REF60044^STANZIONE^DOMINIC^M.^^DR.^MD|||RAD||||||||V20260504004
ORC|NW|ORD5540912
OBR||ORD5540912||76700^US ABDOMEN COMPLETE^CPT||||20260504113000||||||||REF60044^STANZIONE^DOMINIC^M.^^DR.^MD|610-555-2000||||||||||||||RUQ pain, cholelithiasis evaluation
```

---

## 7. ORU^R01 - Mammography screening bilateral final report from UPMC Magee

```
MSH|^~\&|PSCRIBE360|UPMC_MAGEE|EPIC_RADIANT|UPMC|20260503152200||ORU^R01|PS36_20260503152200C|P|2.3
PID|||MRN3417520^^^UPMC||LIANG^JESSICA^MEI||19780514|F|||2405 Penn Ave^^Pittsburgh^PA^15222||412-555-4908|||||||102-57-4839
PV1||O|RAD^MAMM03^1||||RAD20089^FERRARO^GINA^E.^^DR.^MD|REF70032^BRADY^MOIRA^K.^^DR.^MD||RAD||||||||V20260503005
ORC|RE|ORD2291034
OBR||ORD2291034|RAD1192045|77067^SCREENING MAMMOGRAPHY BILATERAL^CPT||||20260503100000||||||||RAD20089^FERRARO^GINA^E.^^DR.^MD|412-555-3000||||||F|||||||RAD20089^FERRARO^GINA^E.^^DR.^MD
OBX|1|FT|GDT^REPORT TEXT^PS360||EXAMINATION: Screening mammography, bilateral\.br\\.br\CLINICAL INDICATION: Annual screening, no symptoms, no prior history of breast cancer\.br\\.br\COMPARISON: Screening mammography dated 2025-04-22\.br\\.br\TECHNIQUE: Standard CC and MLO views of both breasts were obtained with digital mammography. Computer-aided detection (CAD) was utilized.\.br\\.br\FINDINGS:\.br\The breast tissue is heterogeneously dense, which may obscure small masses (ACR density category C). There are no suspicious masses, calcifications, or architectural distortion in either breast. Bilateral axillary regions are unremarkable. No skin thickening or retraction.\.br\\.br\IMPRESSION:\.br\1. Negative screening mammography. BI-RADS 1.\.br\2. Recommend continued annual screening mammography.||||||F
ZBR|30|1|RAD20089^FERRARO^GINA^E.^^^^^Dict|RAD20089^FERRARO^GINA^E.^^^^Sign^Dict||||2^Final|NOR
ZBX|1|30|1|Negative screening mammography. BI-RADS 1. Recommend continued annual screening mammography.
```

---

## 8. MDM^T02 - Radiology report document notification from Penn State Hershey

```
MSH|^~\&|NUANCE_PS|PSH_HERSHEY|CERNER_MDA|PSHMC|20260502091545||MDM^T02|MDM20260502091545D|P|2.3
EVN|T02|20260502091545
PID|||MRN7201384^^^PSHMC||NOVAK^RAYMOND^JOSEPH||19550630|M|||312 Chocolate Ave^^Hershey^PA^17033||717-555-2618|||||||428-60-9173
PV1||I|MED^3W^308||||ATT10098^OSEI^ABENA^M.^^DR.^MD|REF80056^FLANNERY^THOMAS^P.^^DR.^MD||MED||||||||ACCT88320015
TXA|1|RAD^RADIOLOGY REPORT|FT|20260502091500|NR60034^SAXENA^VIKRAM^N.^^DR.^MD|20260502091545|||||NR60034^SAXENA^VIKRAM^N.^^DR.^MD|DOC33920184|||AU||AV
OBR||ORD8830291|RAD7710293|71260^CT CHEST WITH CONTRAST^CPT||||20260502070000||||||||NR60034^SAXENA^VIKRAM^N.^^DR.^MD|717-555-8300||||||F
OBX|1|FT|GDT^REPORT TEXT^PS360||EXAMINATION: CT Chest with contrast\.br\\.br\CLINICAL INDICATION: Hemoptysis, history of smoking\.br\\.br\COMPARISON: CT Chest 2025-11-18\.br\\.br\TECHNIQUE: Axial CT images of the chest were obtained following intravenous administration of 80 mL Omnipaque 350.\.br\\.br\FINDINGS:\.br\A 2.3 cm spiculated nodule is identified in the right upper lobe (series 4, image 67). This has increased from 1.5 cm on prior examination. Mediastinal lymphadenopathy is present with a 1.8 cm pretracheal node and 1.4 cm right hilar node. No pleural effusion. The heart and pericardium are normal. Visualized upper abdomen is unremarkable.\.br\\.br\IMPRESSION:\.br\1. Enlarging 2.3 cm spiculated right upper lobe nodule highly suspicious for malignancy. PET/CT recommended.\.br\2. Mediastinal and right hilar lymphadenopathy suggesting possible nodal metastatic disease.||||||F
```

---

## 9. ADT^A08 - Patient information update at UPMC Shadyside

```
MSH|^~\&|EPIC_ADT|UPMC_SHADYSIDE|POWERSCRIBE|UPMC_RAD|20260501140200||ADT^A08|ADT20260501140200E|P|2.3
EVN|A08|20260501140200
PID|||MRN7218340^^^UPMC||ZIELINSKI^WANDA^FRANCES||19571023|F|||1934 Brownsville Rd^Apt 3B^Pittsburgh^PA^15210||412-555-8271~412-555-6002|||||||321-76-9048
PV1||O|RAD^XR01^1||||RAD10234^KWON^DANIEL^S.^^DR.^MD|||RAD||||||||V20260508001|||||||||||||||||||||||||||20260501140200
```

---

## 10. ORU^R01 - Lumbar spine X-ray final report from Abington Hospital

```
MSH|^~\&|POWERSCRIBE|ABINGTON_HOSPITAL|EPIC_RADIANT|JEFFERSON_HEALTH|20260430101800||ORU^R01|PS2026043010180002|P|2.3
PID|||MRN9480217^^^JEFFERSON||MCGINLEY^DECLAN^PATRICK||19810905|M|||724 Old Welsh Rd^^Abington^PA^19001||267-555-3610|||||||615-40-8293
PV1||O|RAD^XR03^1||||RAD40055^TAKAHASHI^KENJI^H.^^DR.^MD|REF20078^KOWALCZYK^IRENA^K.^^DR.^MD||RAD||||||||V20260430006
ORC|RE|ORD1150293
OBR||ORD1150293|RAD9903812|72110^XRAY LUMBAR SPINE 3 VIEWS^CPT||||20260430090000||||||||RAD40055^TAKAHASHI^KENJI^H.^^DR.^MD|215-555-5100||||||F|||||||RAD40055^TAKAHASHI^KENJI^H.^^DR.^MD
OBX|1|FT|GDT^REPORT TEXT^PS360||EXAMINATION: X-ray lumbar spine, 3 views\.br\\.br\CLINICAL INDICATION: Low back pain radiating to left leg\.br\\.br\COMPARISON: Lumbar spine radiographs dated 2025-09-10\.br\\.br\TECHNIQUE: AP, lateral, and cone-down lateral views of the lumbar spine were obtained.\.br\\.br\FINDINGS:\.br\There is moderate degenerative disc disease at L4-L5 and L5-S1 with disc space narrowing and endplate sclerosis. Mild anterior osteophyte formation is noted at L3-L4 through L5-S1. Facet joint hypertrophy is present bilaterally at L4-L5. There is grade 1 anterolisthesis of L4 on L5, measuring approximately 4 mm, unchanged from prior. Vertebral body heights are maintained. No acute fracture or destructive lesion. The sacroiliac joints appear normal.\.br\\.br\IMPRESSION:\.br\1. Multilevel degenerative changes most pronounced at L4-L5 and L5-S1.\.br\2. Stable grade 1 anterolisthesis of L4 on L5.\.br\3. Consider MRI if radiculopathy symptoms persist.||||||F
ZBR|33|1|RAD40055^TAKAHASHI^KENJI^H.^^^^^Dict|RAD40055^TAKAHASHI^KENJI^H.^^^^Sign^Dict||||2^Final|NOR
ZBX|1|33|1|Multilevel degenerative changes most pronounced at L4-L5 and L5-S1. Stable grade 1 anterolisthesis of L4 on L5. Consider MRI if radiculopathy symptoms persist.
```

---

## 11. ORM^O01 - MRI knee without contrast order from Geisinger Wyoming Valley

```
MSH|^~\&|CERNER_ORM|GEISINGER_WV|NUANCE_PS|GEISINGER_RAD|20260429133000||ORM^O01|CE20260429133000F|P|2.3
PID|||MRN4029831^^^GMC||DELUCA^MARIA^ROSA||19900213|F|||142 S Main St^^Wilkes-Barre^PA^18701||570-555-8817|||||||376-52-0941
PV1||O|RAD^MRI01^1||||REF45033^CZYKOWSKI^ADAM^M.^^DR.^MD|||RAD||||||||V20260429007
ORC|NW|ORD4490821
OBR||ORD4490821||73721^MRI KNEE WITHOUT CONTRAST LEFT^CPT||||20260429140000||||||||REF45033^CZYKOWSKI^ADAM^M.^^DR.^MD|570-555-8500||||||||||||||Left knee pain, meniscal tear evaluation
```

---

## 12. ORU^R01 - CT pulmonary angiography with critical PE finding from Lehigh Valley Cedar Crest

```
MSH|^~\&|PSCRIBE360|LVHN_CEDAR_CREST|EPIC_RADIANT|LVHN|20260428180500||ORU^R01|PS36_20260428180500G|P|2.3
PID|||MRN8291035^^^LVHN||ROBINSON^DENISE^LORRAINE||19650804|F|||517 Linden St^^Allentown^PA^18101||484-555-3298|||||||201-87-4536
PV1||E|ED^BED14^1||||ER90045^SANTIAGO^RAFAEL^R.^^DR.^MD|REF10092^MCALLISTER^JAMES^T.^^DR.^MD||EM||||||||V20260428008
ORC|RE|ORD7729034
OBR||ORD7729034|RAD6601285|71275^CTA CHEST PULMONARY EMBOLISM^CPT||||20260428170000||||||||NR70023^YOON^GRACE^Y.^^DR.^MD|610-555-4500||||||F|||||||NR70023^YOON^GRACE^Y.^^DR.^MD
OBX|1|FT|GDT^REPORT TEXT^PS360||EXAMINATION: CT Pulmonary Angiography\.br\\.br\CLINICAL INDICATION: Acute dyspnea, tachycardia, elevated D-dimer\.br\\.br\COMPARISON: None\.br\\.br\TECHNIQUE: CT angiography of the chest was performed following intravenous administration of 75 mL Isovue 370 with bolus tracking technique.\.br\\.br\FINDINGS:\.br\There are large filling defects within the right main pulmonary artery extending into the right upper and lower lobe segmental branches, consistent with acute pulmonary embolism. A smaller filling defect is present in the left lower lobe segmental artery. The right ventricle is dilated with an RV/LV ratio of 1.4, suggesting right heart strain. Reflux of contrast into the hepatic veins is noted. The main pulmonary artery measures 3.2 cm. No pleural effusion or pneumothorax. No acute parenchymal abnormality.\.br\\.br\IMPRESSION:\.br\1. CRITICAL: Extensive bilateral pulmonary embolism with right heart strain. Interventional radiology or cardiology consultation for catheter-directed therapy recommended.\.br\2. Main pulmonary artery enlargement suggesting pulmonary hypertension.||||||F
OBX|2|FT|GDT^CRITICAL RESULT^PS360||CRITICAL RESULT COMMUNICATED: Dr. Rafael Santiago, ED attending, notified by phone at 18:10 on 2026-04-28. Read back confirmed.||||||F
ZBR|38|1|NR70023^YOON^GRACE^Y.^^^^^Dict|NR70023^YOON^GRACE^Y.^^^^Sign^Dict||||2^Final|ABN
ZBX|1|38|1|CRITICAL: Extensive bilateral pulmonary embolism with right heart strain. Interventional radiology or cardiology consultation for catheter-directed therapy recommended.
```

---

## 13. ADT^A04 - Outpatient registration for CT scan at Crozer-Chester Medical Center

```
MSH|^~\&|MEDITECH_ADT|CROZER_CHESTER|POWERSCRIBE|CROZER_RAD|20260427093000||ADT^A04|ADT20260427093000H|P|2.3
EVN|A04|20260427093000
PID|||MRN3810294^^^CROZER||STANKIEWICZ^HALINA^DOROTA||19720115|F|||290 Chester Pike^^Ridley Park^PA^19078||610-555-9482|||||||748-30-2159
PV1||O|RAD^CT01^1||||REF38021^GENTRY^PHILLIP^G.^^DR.^MD|||RAD||||||||V20260427009|||||||||||||||||||||||||||20260427093000
IN1|1||INS305|INDEPENDENCE BLUE CROSS|1901 Market St^^Philadelphia^PA^19103||||||||||||||||||||||||||||||||||||||||||||42
```

---

## 14. ORU^R01 - Chest X-ray with ED (encapsulated data) base64-encoded PDF report from UPMC Mercy

```
MSH|^~\&|POWERSCRIBE|UPMC_MERCY|EPIC_RADIANT|UPMC|20260426144500||ORU^R01|PS2026042614450003|P|2.3
PID|||MRN5923014^^^UPMC||MORETTI^SALVATORE^ANTHONY||19430321|M|||1710 Carson St^^Pittsburgh^PA^15203||412-555-1647|||||||509-82-3714
PV1||I|MED^6N^614||||ATT30021^HUTTON^KENDRA^C.^^DR.^MD|REF50067^NAVARRO^DIEGO^R.^^DR.^MD||MED||||||||V20260426010
ORC|RE|ORD8821093
OBR||ORD8821093|RAD3320145|71046^CHEST XRAY 2 VIEWS^CPT||||20260426120000||||||||NR80034^VOLKOV^NINA^A.^^DR.^MD|412-555-9000||||||F|||||||NR80034^VOLKOV^NINA^A.^^DR.^MD
OBX|1|FT|GDT^REPORT TEXT^PS360||EXAMINATION: Chest X-ray, 2 views\.br\\.br\CLINICAL INDICATION: Postoperative day 2, CABG, evaluate for effusion\.br\\.br\COMPARISON: Chest X-ray dated 2026-04-25\.br\\.br\FINDINGS:\.br\Median sternotomy wires are intact. Small bilateral pleural effusions, left greater than right, slightly increased compared to prior. Bibasilar atelectasis. No pneumothorax. Cardiac silhouette is mildly enlarged but stable. Mediastinal drains have been removed.\.br\\.br\IMPRESSION:\.br\1. Small bilateral pleural effusions, slightly increased, left greater than right.\.br\2. Bibasilar atelectasis, likely postoperative.\.br\3. Stable mild cardiomegaly.||||||F
OBX|2|ED|PDF^REPORT PDF^PS360||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyMzQgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihSQURJT0xPR1kgUkVQT1JUKSBUIDE3IFRMCjEwMCA2ODAgVGQKKFVQTUMgTWVyY3kgLSBDaGVzdCBYLXJheSAyIFZpZXdzKSBUagoxMDAgNjUwIFRkCihQYXRpZW50OiBSZXlub2xkcywgVGhvbWFzIEouKSBUagoxMDAgNjMwIFRkCihNUk46IDc3NDUwMjEpIFRqCjEwMCA2MDAgVGQKKERhdGU6IDA0LzI2LzIwMjYpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZg0KMDAwMDAwMDAwOSAwMDAwMCBuDQowMDAwMDAwMDYyIDAwMDAwIG4NCjAwMDAwMDAxMjIgMDAwMDAgbg0KMDAwMDAwMDMwMiAwMDAwMCBuDQowMDAwMDAwNTkwIDAwMDAwIG4NCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNjc2CiUlRU9GCg==||||||F
ZBR|40|1|NR80034^VOLKOV^NINA^A.^^^^^Dict|NR80034^VOLKOV^NINA^A.^^^^Sign^Dict||||2^Final|NOR
ZBX|1|40|1|Small bilateral pleural effusions, slightly increased, left greater than right. Bibasilar atelectasis, likely postoperative. Stable mild cardiomegaly.
```

---

## 15. ORM^O01 - Fluoroscopy upper GI series order from WellSpan York Hospital

```
MSH|^~\&|EPIC_ORM|WELLSPAN_YORK|PSCRIBE360|WELLSPAN_RAD|20260425080000||ORM^O01|EP20260425080000I|P|2.3
PID|||MRN2018394^^^WELLSPAN||GUTIERREZ^ELENA^VICTORIA||19880622|F|||188 W Market St^^York^PA^17401||717-555-4031|||||||863-12-5407
PV1||O|RAD^FL01^1||||REF25044^HERSHBERGER^KARL^W.^^DR.^MD|||RAD||||||||V20260425011
ORC|NW|ORD6690234
OBR||ORD6690234||74240^FLUOROSCOPY UPPER GI SERIES^CPT||||20260425090000||||||||REF25044^HERSHBERGER^KARL^W.^^DR.^MD|717-555-1000||||||||||||||Dysphagia, GERD evaluation
```

---

## 16. ORU^R01 - Bone density DEXA scan final report from Einstein Medical Center Philadelphia

```
MSH|^~\&|NUANCE_PS|EINSTEIN_PHILA|CERNER_RAD|EINSTEIN_HEALTH|20260424113000||ORU^R01|NPS20260424113000J|P|2.3
PID|||MRN6140283^^^EINSTEIN||JENKINS^DOROTHY^RUTH||19520907|F|||4320 N Broad St^^Philadelphia^PA^19140||215-555-2093|||||||927-04-6183
PV1||O|RAD^DEXA01^1||||RAD50067^BENEDETTO^CARLO^M.^^DR.^MD|REF60078^MCNAMARA^SIOBHAN^E.^^DR.^MD||RAD||||||||V20260424012
ORC|RE|ORD9901284
OBR||ORD9901284|RAD8801392|77080^DEXA BONE DENSITY AXIAL^CPT||||20260424100000||||||||RAD50067^BENEDETTO^CARLO^M.^^DR.^MD|215-555-8200||||||F|||||||RAD50067^BENEDETTO^CARLO^M.^^DR.^MD
OBX|1|FT|GDT^REPORT TEXT^PS360||EXAMINATION: DEXA Bone Density, Axial Skeleton\.br\\.br\CLINICAL INDICATION: 73-year-old female, postmenopausal, family history of hip fracture\.br\\.br\COMPARISON: DEXA dated 2024-04-15\.br\\.br\TECHNIQUE: Dual-energy X-ray absorptiometry of the lumbar spine (L1-L4) and bilateral proximal femora.\.br\\.br\FINDINGS:\.br\Lumbar spine (L1-L4): BMD 0.782 g/cm2, T-score -2.6\.br\Left femoral neck: BMD 0.621 g/cm2, T-score -2.8\.br\Right femoral neck: BMD 0.635 g/cm2, T-score -2.7\.br\Left total hip: BMD 0.698 g/cm2, T-score -2.3\.br\Right total hip: BMD 0.710 g/cm2, T-score -2.2\.br\\.br\The lumbar spine T-score has decreased from -2.3 to -2.6 since prior examination. The left femoral neck T-score has decreased from -2.5 to -2.8.\.br\\.br\IMPRESSION:\.br\1. Osteoporosis by WHO criteria at the lumbar spine and bilateral femoral necks.\.br\2. Interval decrease in bone mineral density compared to 2024 examination.\.br\3. FRAX 10-year fracture probability should be calculated for treatment decision.||||||F
ZBR|42|1|RAD50067^BENEDETTO^CARLO^M.^^^^^Dict|RAD50067^BENEDETTO^CARLO^M.^^^^Sign^Dict||||2^Final|NOR
ZBX|1|42|1|Osteoporosis by WHO criteria at the lumbar spine and bilateral femoral necks. Interval decrease in bone mineral density compared to 2024 examination.
```

---

## 17. MDM^T02 - Interventional radiology procedure note from Thomas Jefferson University Hospital

```
MSH|^~\&|POWERSCRIBE|TJUH|EPIC_MDA|JEFFERSON_HEALTH|20260423154500||MDM^T02|MDM20260423154500K|P|2.3
EVN|T02|20260423154500
PID|||MRN4710283^^^JEFFERSON||BOYD^TERRANCE^WAYNE||19590128|M|||917 Walnut St^^Philadelphia^PA^19107||215-555-6038|||||||180-47-9352
PV1||I|IR^SUITE02^1||||IR20034^STRZELECKI^MAREK^M.^^DR.^MD|REF90023^PRITCHARD^DANA^F.^^DR.^MD||IR||||||||ACCT66510028
TXA|1|RAD^INTERVENTIONAL RADIOLOGY NOTE|FT|20260423150000|IR20034^STRZELECKI^MAREK^M.^^DR.^MD|20260423154500|||||IR20034^STRZELECKI^MAREK^M.^^DR.^MD|DOC55930281|||AU||AV
OBR||ORD5540192|RAD4401293|36247^SELECTIVE CATHETER PLACEMENT ARTERIAL 2ND ORDER^CPT||||20260423130000||||||||IR20034^STRZELECKI^MAREK^M.^^DR.^MD|215-555-5300||||||F
OBX|1|FT|GDT^REPORT TEXT^PS360||PROCEDURE: Hepatic artery chemoembolization (TACE)\.br\\.br\CLINICAL INDICATION: Hepatocellular carcinoma, segment 6, BCLC stage B\.br\\.br\COMPARISON: MRI Abdomen dated 2026-03-30\.br\\.br\PROCEDURE DETAILS:\.br\After obtaining informed consent, the patient was placed supine on the angiography table. The right common femoral artery was accessed using a 5-French micropuncture set under ultrasound guidance. A 5-French Cobra catheter was advanced into the celiac trunk. Celiac arteriography demonstrated a hypervascular mass in segment 6 measuring 3.8 cm supplied by a branch of the right hepatic artery. A 2.7-French Progreat microcatheter was advanced superselectively into the feeding artery. A mixture of 50 mg doxorubicin loaded onto 100-300 micron DC Bead was administered followed by embolization with 300-500 micron Embosphere particles to near stasis. Completion angiography demonstrated devascularization of the tumor. The catheter and sheath were removed and hemostasis achieved with an Angio-Seal device.\.br\\.br\FINDINGS:\.br\Successful superselective TACE of segment 6 HCC.\.br\\.br\COMPLICATIONS: None\.br\\.br\ESTIMATED BLOOD LOSS: Less than 10 mL\.br\\.br\IMPRESSION:\.br\1. Successful transarterial chemoembolization of segment 6 hepatocellular carcinoma.\.br\2. Follow-up MRI abdomen in 4-6 weeks recommended to assess treatment response.||||||F
```

---

## 18. ORU^R01 - CT head with ED (encapsulated data) base64-encoded RTF report from Lancaster General Hospital

```
MSH|^~\&|PSCRIBE360|LGH|EPIC_RADIANT|PENN_MEDICINE_LGH|20260422201500||ORU^R01|PS36_20260422201500L|P|2.3
PID|||MRN8302941^^^LGH||PFEIFFER^GERTRUDE^HELEN||19470516|F|||315 E King St^^Lancaster^PA^17602||717-555-3840|||||||641-28-0793
PV1||E|ED^BED22^1||||ER40098^SANTOS^MARCO^A.^^DR.^MD|REF70034^FITZPATRICK^SHEILA^M.^^DR.^MD||EM||||||||V20260422013
ORC|RE|ORD2290183
OBR||ORD2290183|RAD1130294|70450^CT HEAD WITHOUT CONTRAST^CPT||||20260422193000||||||||NR30045^WHITFIELD^CYRUS^W.^^DR.^MD|717-555-5511||||||F|||||||NR30045^WHITFIELD^CYRUS^W.^^DR.^MD
OBX|1|FT|GDT^REPORT TEXT^PS360||EXAMINATION: CT Head without contrast\.br\\.br\CLINICAL INDICATION: Acute onset left-sided weakness, rule out CVA\.br\\.br\COMPARISON: None\.br\\.br\TECHNIQUE: Axial CT images of the head were obtained without intravenous contrast.\.br\\.br\FINDINGS:\.br\No acute intracranial hemorrhage. No large territory infarct or mass effect. Mild generalized cerebral atrophy appropriate for age. Periventricular white matter hypodensities consistent with chronic small vessel ischemic disease. No extra-axial collection. Visualized paranasal sinuses and mastoid air cells are clear.\.br\\.br\IMPRESSION:\.br\1. No acute intracranial hemorrhage or large territory infarct.\.br\2. Chronic small vessel ischemic changes.\.br\3. CTA head and neck and/or MRI brain recommended given clinical concern for acute stroke.||||||F
OBX|2|ED|RTF^REPORT RTF^PS360||^application^rtf^Base64^e1xydGYxXGFuc2lcYW5zaWNwZzEyNTIKe1xmb250dGJsCntcZjBcZnN3aXNzIEhlbHZldGljYTt9fQp7XGNvbG9ydGJsIDtccmVkMFxncmVlbjBcYmx1ZTA7fQpccGFyZFxmMFxmczI0ClxiIFJBRElPTE9HWSBSRVBPUlRcYjBccGFyCkxhbmNhc3RlciBHZW5lcmFsIEhvc3BpdGFsXHBhcgpccGFyClxiIFBhdGllbnQ6XGIwICBIZW5zbGV5LCBNYXJnYXJldCBMLlxwYXIKXGIgTVJOOlxiMCAgNTU5MDIzNFxwYXIKXGIgRGF0ZTpcYjAgIDA0LzIyLzIwMjZccGFyClxiIEV4YW1pbmF0aW9uOlxiMCAgQ1QgSGVhZCB3aXRob3V0IGNvbnRyYXN0XHBhcgpccGFyClxiIEZJTkRJTkdTOlxiMFxwYXIKTm8gYWN1dGUgaW50cmFjcmFuaWFsIGhlbW9ycmhhZ2UuIE5vIGxhcmdlIHRlcnJpdG9yeSBpbmZhcmN0IG9yIG1hc3MgZWZmZWN0LiBNaWxkIGdlbmVyYWxpemVkIGNlcmVicmFsIGF0cm9waHkuXHBhcgpccGFyClxiIElNUFJFU1NJT046XGIwXHBhcgoxLiBObyBhY3V0ZSBpbnRyYWNyYW5pYWwgaGVtb3JyaGFnZSBvciBsYXJnZSB0ZXJyaXRvcnkgaW5mYXJjdC5ccGFyCjIuIENocm9uaWMgc21hbGwgdmVzc2VsIGlzY2hlbWljIGNoYW5nZXMuXHBhcgozLiBDVEEgaGVhZCBhbmQgbmVjayByZWNvbW1lbmRlZC5ccGFyCn0=||||||F
ZBR|45|1|NR30045^WHITFIELD^CYRUS^W.^^^^^Dict|NR30045^WHITFIELD^CYRUS^W.^^^^Sign^Dict||||2^Final|NOR
ZBX|1|45|1|No acute intracranial hemorrhage or large territory infarct. Chronic small vessel ischemic changes. CTA head and neck and/or MRI brain recommended given clinical concern for acute stroke.
```

---

## 19. ADT^A08 - Insurance update for radiology patient at Allegheny General Hospital

```
MSH|^~\&|CERNER_ADT|AGH|NUANCE_PS|AHN_RAD|20260421112000||ADT^A08|ADT20260421112000M|P|2.3
EVN|A08|20260421112000
PID|||MRN3019482^^^AHN||TUCKER^LAMAR^DARNELL||19700306|M|||408 Western Ave^^Pittsburgh^PA^15212||412-555-5709|||||||532-90-4178
PV1||O|RAD^CT02^1||||REF80012^KONOPKA^SYLVIA^L.^^DR.^MD|||RAD||||||||V20260421014|||||||||||||||||||||||||||20260421112000
IN1|1||INS410|HIGHMARK BLUE CROSS BLUE SHIELD|1800 Center St^^Camp Hill^PA^17011||||||||||||||||||||||||||||||||||||||||||||42
```

---

## 20. ORU^R01 - CT abdomen pelvis with diagnosis codes from Hershey Medical Center

```
MSH|^~\&|POWERSCRIBE|PSH_HERSHEY|CERNER_RAD|PSHMC|20260420163000||ORU^R01|PS2026042016300004|P|2.3
PID|||MRN9230148^^^PSHMC||SCHAEFER^OTTO^DANIEL||19791118|M|||740 Cocoa Ave^^Hershey^PA^17033||717-555-6012|||||||305-71-8924
PV1||I|SURG^5E^518||||ATT40056^NWOSU^ADAEZE^A.^^DR.^MD|REF30089^KILPATRICK^MARK^J.^^DR.^MD||SURG||||||||ACCT99210031
ORC|RE|ORD3390182
OBR||ORD3390182|RAD2290381|74178^CT ABDOMEN PELVIS WITH CONTRAST^CPT||||20260420140000||||||||NR20078^RADEMACHER^ERIC^T.^^DR.^MD|717-555-8300||||||F|||||||NR20078^RADEMACHER^ERIC^T.^^DR.^MD
OBX|1|FT|GDT^REPORT TEXT^PS360||EXAMINATION: CT Abdomen and Pelvis with IV contrast\.br\\.br\CLINICAL INDICATION: Postoperative day 5 appendectomy, fever and elevated WBC\.br\\.br\COMPARISON: CT Abdomen/Pelvis dated 2026-04-15\.br\\.br\TECHNIQUE: Axial CT images of the abdomen and pelvis were obtained following intravenous administration of 100 mL Omnipaque 350 in the portal venous phase.\.br\\.br\FINDINGS:\.br\ABDOMEN: The liver, spleen, pancreas, adrenal glands, and kidneys are unremarkable. No biliary dilatation. The stomach and visualized small bowel are normal.\.br\\.br\PELVIS: There is a 4.2 x 3.1 cm rim-enhancing fluid collection in the right lower quadrant at the appendectomy site with surrounding inflammatory fat stranding. A small amount of free fluid is present in the pelvis. The urinary bladder is normal. No inguinal lymphadenopathy.\.br\\.br\IMPRESSION:\.br\1. 4.2 cm rim-enhancing fluid collection at the right lower quadrant appendectomy site, concerning for postoperative abscess. Percutaneous drainage recommended.\.br\2. Small amount of pelvic free fluid.||||||F
ZDG|74178^CT ABDOMEN PELVIS WITH CONTRAST^CPT|K35.80^ACUTE APPENDICITIS, UNSPECIFIED^I10~K65.0^GENERALIZED PERITONITIS^I10~T81.49XA^INFECTION FOLLOWING A PROCEDURE, INITIAL ENCOUNTER^I10
ZBR|48|1|NR20078^RADEMACHER^ERIC^T.^^^^^Dict|NR20078^RADEMACHER^ERIC^T.^^^^Sign^Dict||||2^Final|ABN
ZBX|1|48|1|4.2 cm rim-enhancing fluid collection at the right lower quadrant appendectomy site, concerning for postoperative abscess. Percutaneous drainage recommended. Small amount of pelvic free fluid.
```
