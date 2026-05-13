# Nuance PowerScribe - real HL7v2 ER7 messages

## 1. ORU^R01 - Chest X-ray PA and lateral report with embedded PDF from IU Health

```
MSH|^~\&|POWERSCRIBE|IUHEALTH_RAD|EHR|IUHEALTH|20250312143500||ORU^R01|PS-IUH-20250312-004871|P|2.4|||AL|NE
PID|1||MRN-73140286^^^IUHEALTH^MR||Hargrove^Sandra^Elaine^^||19580324|F||W|2917 N Delaware St^^Indianapolis^IN^46205^USA||^PRN^PH^^1^317^4429081|||||||482-31-6750
PV1|1|O|RAD^XRAY^01||||3847201^Kowalski^Brian^E^^^MD|3847201^Kowalski^Brian^E^^^MD||RAD||||||||V|VN-20250312-0087^^^IUHEALTH^VN|||||||||||||||||||||||||20250312090000
ORC|RE|ORD-RAD-20250312-087^IUHEALTH|PS-RPT-20250312-004871^POWERSCRIBE||||1^^^20250312090000^^R||20250312143500|3847201^Kowalski^Brian^E^^^MD|3847201^Kowalski^Brian^E^^^MD|3847201^Kowalski^Brian^E^^^MD||^WPN^PH^^1^317^9621000||||||IUHEALTH^IU Health
OBR|1|ORD-RAD-20250312-087^IUHEALTH|PS-RPT-20250312-004871^POWERSCRIBE|71020^XR CHEST PA AND LATERAL^CPT4|||20250312091500|||||||||||3847201^Kowalski^Brian^E^^^MD||RAD-ACC-20250312-0087||||20250312143500|||F|||||||5924103^Tremaine^Victoria^J^^^MD^Radiology
OBX|1|ED|71020^XR CHEST PA AND LATERAL^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
OBX|2|TX|71020^XR CHEST PA AND LATERAL^CPT4|2|CHEST X-RAY PA AND LATERAL~~CLINICAL INDICATION: Cough, shortness of breath.~~COMPARISON: Chest X-ray dated 2024-11-15.~~FINDINGS:~The lungs are clear bilaterally without focal consolidation, pleural effusion, or pneumothorax. The cardiac silhouette is normal in size. The mediastinal contours are unremarkable. The osseous structures are intact without acute fracture.~~IMPRESSION: No acute cardiopulmonary disease.||||||F
```

---

## 2. ORU^R01 - CT abdomen and pelvis report with embedded PDF from Community Health Network

```
MSH|^~\&|POWERSCRIBE|CHN_RAD|EHR|CHN|20250418102300||ORU^R01|PS-CHN-20250418-006218|P|2.4|||AL|NE
PID|1||MRN-61843290^^^CHN^MR||Calloway^Terrence^Darnell^^||19670815|M||W|1534 Prospect St^^Indianapolis^IN^46203^USA||^PRN^PH^^1^317^6629413|||||||315-72-4086
PV1|1|O|RAD^CT^03||||4201837^Reinhart^Catherine^E^^^MD|4201837^Reinhart^Catherine^E^^^MD||RAD||||||||V|VN-20250418-0214^^^CHN^VN|||||||||||||||||||||||||20250418080000
ORC|RE|ORD-RAD-20250418-214^CHN|PS-RPT-20250418-006218^POWERSCRIBE||||1^^^20250418080000^^R||20250418102300|4201837^Reinhart^Catherine^E^^^MD|4201837^Reinhart^Catherine^E^^^MD|4201837^Reinhart^Catherine^E^^^MD||^WPN^PH^^1^317^3557000||||||CHN^Community Health Network
OBR|1|ORD-RAD-20250418-214^CHN|PS-RPT-20250418-006218^POWERSCRIBE|74178^CT ABD AND PELVIS WITH CONTRAST^CPT4|||20250418083000|||||||||||4201837^Reinhart^Catherine^E^^^MD||RAD-ACC-20250418-0214||||20250418102300|||F|||||||6382041^Lucero^Andrea^L^^^MD^Radiology
OBX|1|ED|74178^CT ABD AND PELVIS WITH CONTRAST^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
OBX|2|TX|74178^CT ABD AND PELVIS WITH CONTRAST^CPT4|2|CT ABDOMEN AND PELVIS WITH IV CONTRAST~~CLINICAL INDICATION: Abdominal pain, rule out appendicitis.~~TECHNIQUE: Helical CT of the abdomen and pelvis following administration of 100 mL Omnipaque 350 IV.~~COMPARISON: None.~~FINDINGS:~Liver: Mild hepatic steatosis. No focal lesion.~Gallbladder: Normal. No gallstones.~Pancreas: Normal in size and attenuation.~Spleen: Normal.~Kidneys: Normal bilaterally. No hydronephrosis.~Appendix: Normal in caliber measuring 5mm. No periappendiceal fat stranding.~Bowel: Normal. No obstruction or wall thickening.~Lymph nodes: No pathologically enlarged lymph nodes.~~IMPRESSION:~1. Mild hepatic steatosis.~2. No acute abdominal pathology. Normal appendix.||||||F
```

---

## 3. ORU^R01 - MRI brain with and without contrast from IU Health

```
MSH|^~\&|POWERSCRIBE|IUHEALTH_RAD|EHR|IUHEALTH|20250527161200||ORU^R01|PS-IUH-20250527-008934|P|2.4|||AL|NE
PID|1||MRN-40295817^^^IUHEALTH^MR||Whitaker^Pamela^Jolene^^||19790512|F||W|5318 Brookville Rd^^Indianapolis^IN^46219^USA||^PRN^PH^^1^317^7728014|||||||249-61-8035
PV1|1|O|RAD^MRI^02||||5173920^Calderon^Jonathan^A^^^MD|5173920^Calderon^Jonathan^A^^^MD||RAD||||||||V|VN-20250527-0345^^^IUHEALTH^VN|||||||||||||||||||||||||20250527130000
ORC|RE|ORD-RAD-20250527-345^IUHEALTH|PS-RPT-20250527-008934^POWERSCRIBE||||1^^^20250527130000^^R||20250527161200|5173920^Calderon^Jonathan^A^^^MD|5173920^Calderon^Jonathan^A^^^MD|5173920^Calderon^Jonathan^A^^^MD||^WPN^PH^^1^317^9621000||||||IUHEALTH^IU Health
OBR|1|ORD-RAD-20250527-345^IUHEALTH|PS-RPT-20250527-008934^POWERSCRIBE|70553^MRI BRAIN W AND WO CONTRAST^CPT4|||20250527133000|||||||||||5173920^Calderon^Jonathan^A^^^MD||RAD-ACC-20250527-0345||||20250527161200|||F|||||||7210384^Kirkland^Elaine^N^^^MD^Neuroradiology
OBX|1|TX|70553^MRI BRAIN W AND WO CONTRAST^CPT4|1|MRI BRAIN WITH AND WITHOUT IV CONTRAST~~CLINICAL INDICATION: Headaches, rule out intracranial pathology.~~TECHNIQUE: Multiplanar, multisequence MRI of the brain performed before and after IV administration of 15 mL Gadavist.~~COMPARISON: None.~~FINDINGS:~Brain parenchyma: Normal gray-white matter differentiation. No acute infarct on diffusion-weighted imaging. No hemorrhage.~Ventricles: Normal in size and morphology.~Extra-axial spaces: Small 8mm extra-axial mass along the left parietal convexity with homogeneous enhancement, consistent with meningioma.~Midline structures: No shift.~Posterior fossa: Normal cerebellum and brainstem.~Orbits: Normal.~~IMPRESSION:~1. Small left parietal meningioma measuring 8mm. Recommend follow-up MRI in 12 months.~2. No acute intracranial pathology.||||||F
```

---

## 4. ORM^O01 - Radiology order for CT chest from Franciscan Health, Indianapolis

```
MSH|^~\&|EHR|FRANCISCAN|POWERSCRIBE|FRANCISCAN_RAD|20250214093800||ORM^O01|ORM-FRAN-20250214-002749|P|2.4|||AL|NE
PID|1||MRN-58302914^^^FRANCISCAN^MR||Pennington^Gloria^Lorraine^^||19640722|F||W|2743 Kentucky Ave^^Indianapolis^IN^46221^USA||^PRN^PH^^1^317^8814203|||||||537-82-1094
PV1|1|O|RAD^CT^01||||6281039^Overstreet^Raymond^K^^^MD|6281039^Overstreet^Raymond^K^^^MD||RAD||||||||V|VN-20250214-0123^^^FRANCISCAN^VN|||||||||||||||||||||||||20250214080000
ORC|NW|ORD-RAD-20250214-123^FRANCISCAN||||||1^^^20250214090000^^R||20250214093800|6281039^Overstreet^Raymond^K^^^MD|6281039^Overstreet^Raymond^K^^^MD|6281039^Overstreet^Raymond^K^^^MD||^WPN^PH^^1^317^5284000||||||FRANCISCAN^Franciscan Health
OBR|1|ORD-RAD-20250214-123^FRANCISCAN||71260^CT CHEST WITH CONTRAST^CPT4|||20250214100000|||A|||||6281039^Overstreet^Raymond^K^^^MD|^WPN^PH^^1^317^5284000
```

---

## 5. ORU^R01 - CT chest report from Franciscan Health

```
MSH|^~\&|POWERSCRIBE|FRANCISCAN_RAD|EHR|FRANCISCAN|20250214153000||ORU^R01|PS-FRAN-20250214-005391|P|2.4|||AL|NE
PID|1||MRN-58302914^^^FRANCISCAN^MR||Pennington^Gloria^Lorraine^^||19640722|F||W|2743 Kentucky Ave^^Indianapolis^IN^46221^USA||^PRN^PH^^1^317^8814203|||||||537-82-1094
PV1|1|O|RAD^CT^01||||6281039^Overstreet^Raymond^K^^^MD|6281039^Overstreet^Raymond^K^^^MD||RAD||||||||V|VN-20250214-0123^^^FRANCISCAN^VN|||||||||||||||||||||||||20250214080000
ORC|RE|ORD-RAD-20250214-123^FRANCISCAN|PS-RPT-20250214-005391^POWERSCRIBE||||1^^^20250214090000^^R||20250214153000|6281039^Overstreet^Raymond^K^^^MD|6281039^Overstreet^Raymond^K^^^MD|6281039^Overstreet^Raymond^K^^^MD||^WPN^PH^^1^317^5284000||||||FRANCISCAN^Franciscan Health
OBR|1|ORD-RAD-20250214-123^FRANCISCAN|PS-RPT-20250214-005391^POWERSCRIBE|71260^CT CHEST WITH CONTRAST^CPT4|||20250214103000|||||||||||6281039^Overstreet^Raymond^K^^^MD||RAD-ACC-20250214-0123||||20250214153000|||F|||||||8041729^Griswold^Melinda^T^^^MD^Radiology
OBX|1|TX|71260^CT CHEST WITH CONTRAST^CPT4|1|CT CHEST WITH IV CONTRAST~~CLINICAL INDICATION: Persistent cough, weight loss, former smoker.~~TECHNIQUE: Helical CT of the chest with IV contrast.~~COMPARISON: Chest X-ray dated 2025-01-28.~~FINDINGS:~Lungs: 12mm spiculated nodule in the right upper lobe (series 3, image 45). No additional pulmonary nodules. No consolidation.~Pleura: No effusion or thickening.~Mediastinum: No significant lymphadenopathy. Heart size normal.~Bones: Degenerative changes of the thoracic spine. No lytic or blastic lesions.~~IMPRESSION:~1. Suspicious 12mm spiculated right upper lobe pulmonary nodule. Recommend PET-CT for further evaluation.~2. No mediastinal lymphadenopathy.||||||F
```

---

## 6. ORU^R01 - Mammogram with embedded PDF from Community Health Network

```
MSH|^~\&|POWERSCRIBE|CHN_RAD|EHR|CHN|20250609151800||ORU^R01|PS-CHN-20250609-009412|P|2.4|||AL|NE
PID|1||MRN-92410538^^^CHN^MR||Rutherford^Christine^Denise^^||19750303|F||W|4730 Allisonville Rd^^Indianapolis^IN^46205^USA||^PRN^PH^^1^317^2219384|||||||648-30-7125
PV1|1|O|RAD^MAMMO^05||||7103824^Norwood^Dennis^W^^^MD|7103824^Norwood^Dennis^W^^^MD||RAD||||||||V|VN-20250609-0567^^^CHN^VN|||||||||||||||||||||||||20250609140000
ORC|RE|ORD-RAD-20250609-567^CHN|PS-RPT-20250609-009412^POWERSCRIBE||||1^^^20250609140000^^R||20250609151800|7103824^Norwood^Dennis^W^^^MD|7103824^Norwood^Dennis^W^^^MD|7103824^Norwood^Dennis^W^^^MD||^WPN^PH^^1^317^3557000||||||CHN^Community Health Network
OBR|1|ORD-RAD-20250609-567^CHN|PS-RPT-20250609-009412^POWERSCRIBE|77067^SCREENING MAMMOGRAM BILATERAL^CPT4|||20250609141500|||||||||||7103824^Norwood^Dennis^W^^^MD||RAD-ACC-20250609-0567||||20250609151800|||F|||||||9281047^Pemberton^Laura^K^^^MD^Radiology
OBX|1|ED|77067^SCREENING MAMMOGRAM BILATERAL^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
OBX|2|TX|77067^SCREENING MAMMOGRAM BILATERAL^CPT4|2|SCREENING MAMMOGRAM BILATERAL~~CLINICAL INDICATION: Annual screening mammography. No palpable abnormality.~~TECHNIQUE: Standard CC and MLO views of both breasts were obtained using digital tomosynthesis.~~COMPARISON: Screening mammogram dated 2024-06-10.~~BREAST COMPOSITION: The breasts are heterogeneously dense (ACR density C).~~FINDINGS:~Right breast: No suspicious mass, architectural distortion, or suspicious calcifications.~Left breast: No suspicious mass, architectural distortion, or suspicious calcifications.~Axillary regions: No suspicious lymphadenopathy.~~IMPRESSION: Negative. No mammographic evidence of malignancy.~~BI-RADS: 1 - Negative.~~RECOMMENDATION: Routine annual screening mammography.||||||F
```

---

## 7. ORU^R01 - Lumbar spine X-ray report from Parkview Health, Fort Wayne

```
MSH|^~\&|POWERSCRIBE|PARKVIEW_RAD|EHR|PARKVIEW|20250723042200||ORU^R01|PS-PV-20250723-011583|P|2.4|||AL|NE
PID|1||MRN-63029481^^^PARKVIEW^MR||Burkhart^Gerald^Raymond^^||19550303|M||W|5108 Covington Rd^^Fort Wayne^IN^46804^USA||^PRN^PH^^1^260^4419372|||||||170-84-3291
PV1|1|O|RAD^XRAY^01||||8204913^Ashworth^Teresa^B^^^MD|8204913^Ashworth^Teresa^B^^^MD||RAD||||||||V|VN-20250723-0891^^^PARKVIEW^VN|||||||||||||||||||||||||20250723020000
ORC|RE|ORD-RAD-20250723-891^PARKVIEW|PS-RPT-20250723-011583^POWERSCRIBE||||1^^^20250723020000^^R||20250723042200|8204913^Ashworth^Teresa^B^^^MD|8204913^Ashworth^Teresa^B^^^MD|8204913^Ashworth^Teresa^B^^^MD||^WPN^PH^^1^260^2666000||||||PARKVIEW^Parkview Health
OBR|1|ORD-RAD-20250723-891^PARKVIEW|PS-RPT-20250723-011583^POWERSCRIBE|72110^XR LUMBAR SPINE COMPLETE^CPT4|||20250723023000|||||||||||8204913^Ashworth^Teresa^B^^^MD||RAD-ACC-20250723-0891||||20250723042200|||F|||||||9302814^Whitmore^Philip^G^^^MD^Radiology
OBX|1|TX|72110^XR LUMBAR SPINE COMPLETE^CPT4|1|XR LUMBAR SPINE COMPLETE (AP, LATERAL, SPOT LATERAL L5-S1)~~CLINICAL INDICATION: Low back pain, history of degenerative disc disease.~~COMPARISON: Lumbar spine X-ray dated 2023-08-22.~~FINDINGS:~Alignment: Normal lumbar lordosis. No spondylolisthesis.~Vertebral bodies: Mild anterior osteophyte formation at L3-L4 and L4-L5. No compression fracture.~Disc spaces: Moderate disc space narrowing at L4-L5 and L5-S1. Mild disc space narrowing at L3-L4.~Facet joints: Mild bilateral facet arthropathy at L4-L5 and L5-S1.~Sacroiliac joints: Normal.~Soft tissues: Unremarkable.~~IMPRESSION:~1. Multilevel degenerative changes, most pronounced at L4-L5 and L5-S1, stable compared to prior.~2. No acute fracture or malalignment.||||||F
```

---

## 8. ORU^R01 - CT pulmonary angiography report from IU Health Methodist emergency

```
MSH|^~\&|POWERSCRIBE|IUHEALTH_RAD|EHR|IUHEALTH|20250305022000||ORU^R01|PS-IUH-20250305-013290|P|2.4|||AL|NE
PID|1||MRN-38471025^^^IUHEALTH^MR||Ochoa^Natalie^Simone^^||19770415|F||W|2630 Central Ave^^Indianapolis^IN^46205^USA||^PRN^PH^^1^317^9948107|||||||418-93-2067
PV1|1|E|ED^BED08^01||||9201384^Ellsworth^Grant^P^^^MD|9201384^Ellsworth^Grant^P^^^MD||RAD||||||||E|VN-20250305-0234^^^IUHEALTH^VN|||||||||||||||||||||||||20250305010000
ORC|RE|ORD-RAD-20250305-234^IUHEALTH|PS-RPT-20250305-013290^POWERSCRIBE||||1^^^20250305013000^^S||20250305022000|9201384^Ellsworth^Grant^P^^^MD|9201384^Ellsworth^Grant^P^^^MD|9201384^Ellsworth^Grant^P^^^MD||^WPN^PH^^1^317^9621000||||||IUHEALTH^IU Health Methodist Hospital
OBR|1|ORD-RAD-20250305-234^IUHEALTH|PS-RPT-20250305-013290^POWERSCRIBE|71275^CT ANGIOGRAPHY CHEST^CPT4|||20250305014500|||||||||||9201384^Ellsworth^Grant^P^^^MD||RAD-ACC-20250305-0234||||20250305022000|||F|||||||1042793^Lindquist^Sharon^D^^^MD^Radiology
OBX|1|TX|71275^CT ANGIOGRAPHY CHEST^CPT4|1|CT PULMONARY ANGIOGRAPHY~~CLINICAL INDICATION: Acute onset dyspnea, pleuritic chest pain, elevated D-dimer.~~TECHNIQUE: CT angiography of the chest with 80 mL Omnipaque 350 IV, timed bolus.~~COMPARISON: None.~~FINDINGS:~Pulmonary arteries: Filling defect in the right lower lobe segmental pulmonary artery and subsegmental branches, consistent with acute pulmonary embolism. No saddle embolus. Left pulmonary arteries are patent.~Heart: Normal size. No pericardial effusion. RV/LV ratio 0.9 (normal).~Lungs: Small right-sided pleural effusion. No consolidation. No pneumothorax.~Mediastinum: No lymphadenopathy.~~IMPRESSION:~1. Acute pulmonary embolism involving right lower lobe segmental and subsegmental arteries.~2. Small right pleural effusion.~3. No evidence of right heart strain.||||||F
```

---

## 9. ORU^R01 - Abdominal ultrasound report from Franciscan Health, South Bend

```
MSH|^~\&|POWERSCRIBE|FRANCISCAN_RAD|EHR|FRANCISCAN|20250415102000||ORU^R01|PS-FRAN-20250415-014821|P|2.4|||AL|NE
PID|1||MRN-49280713^^^FRANCISCAN^MR||Buckner^Heather^Jolene^^||19920830|F||W|3814 Grape Rd^^South Bend^IN^46614^USA||^PRN^PH^^1^574^2219384|||||||451-70-8293
PV1|1|O|RAD^US^04||||2048139^Pruitt^Douglas^V^^^MD|2048139^Pruitt^Douglas^V^^^MD||RAD||||||||V|VN-20250415-0456^^^FRANCISCAN^VN|||||||||||||||||||||||||20250415090000
ORC|RE|ORD-RAD-20250415-456^FRANCISCAN|PS-RPT-20250415-014821^POWERSCRIBE||||1^^^20250415090000^^R||20250415102000|2048139^Pruitt^Douglas^V^^^MD|2048139^Pruitt^Douglas^V^^^MD|2048139^Pruitt^Douglas^V^^^MD||^WPN^PH^^1^574^3353000||||||FRANCISCAN^Franciscan Health
OBR|1|ORD-RAD-20250415-456^FRANCISCAN|PS-RPT-20250415-014821^POWERSCRIBE|76700^US ABD COMPLETE^CPT4|||20250415093000|||||||||||2048139^Pruitt^Douglas^V^^^MD||RAD-ACC-20250415-0456||||20250415102000|||F|||||||1472903^Ventura^Craig^H^^^MD^Radiology
OBX|1|TX|76700^US ABD COMPLETE^CPT4|1|ULTRASOUND ABDOMEN COMPLETE~~CLINICAL INDICATION: Right upper quadrant pain, nausea.~~TECHNIQUE: Real-time gray scale and color Doppler ultrasound of the abdomen.~~COMPARISON: None.~~FINDINGS:~Liver: Normal size and echogenicity. No focal lesion.~Gallbladder: Multiple gallstones present, largest measuring 1.2 cm. No gallbladder wall thickening. No pericholecystic fluid. Positive sonographic Murphy sign.~Common bile duct: Normal caliber measuring 4mm.~Pancreas: Normal. Not obscured by bowel gas.~Right kidney: Normal, measuring 11.2 cm. No hydronephrosis or calculi.~Left kidney: Normal, measuring 10.8 cm. No hydronephrosis or calculi.~Aorta: Normal caliber.~Spleen: Normal, measuring 10.5 cm.~~IMPRESSION:~1. Cholelithiasis with positive sonographic Murphy sign. Findings suggestive of acute cholecystitis. Clinical correlation recommended.~2. Otherwise normal abdominal ultrasound.||||||F
```

---

## 10. ORU^R01 - Knee X-ray report from Parkview Health

```
MSH|^~\&|POWERSCRIBE|PARKVIEW_RAD|EHR|PARKVIEW|20250118102000||ORU^R01|PS-PV-20250118-016204|P|2.4|||AL|NE
PID|1||MRN-57130482^^^PARKVIEW^MR||Dalton^Shirley^Vivian^^||19680918|F||W|4903 W Jefferson Blvd^^Fort Wayne^IN^46804^USA||^PRN^PH^^1^260^7714820|||||||583-02-4197
PV1|1|O|RAD^XRAY^01||||1483027^Farrell^Allan^M^^^MD|1483027^Farrell^Allan^M^^^MD||RAD||||||||V|VN-20250118-0567^^^PARKVIEW^VN|||||||||||||||||||||||||20250118090000
ORC|RE|ORD-RAD-20250118-567^PARKVIEW|PS-RPT-20250118-016204^POWERSCRIBE||||1^^^20250118090000^^R||20250118102000|1483027^Farrell^Allan^M^^^MD|1483027^Farrell^Allan^M^^^MD|1483027^Farrell^Allan^M^^^MD||^WPN^PH^^1^260^2666000||||||PARKVIEW^Parkview Health
OBR|1|ORD-RAD-20250118-567^PARKVIEW|PS-RPT-20250118-016204^POWERSCRIBE|73562^XR KNEE 3 VIEWS^CPT4|||20250118093000|||||||||||1483027^Farrell^Allan^M^^^MD||RAD-ACC-20250118-0567||||20250118102000|||F|||||||2813049^Gutierrez^Nancy^F^^^MD^Radiology
OBX|1|TX|73562^XR KNEE 3 VIEWS^CPT4|1|XR LEFT KNEE 3 VIEWS (AP, LATERAL, SUNRISE)~~CLINICAL INDICATION: Left knee pain, history of osteoarthritis.~~COMPARISON: Left knee X-ray dated 2024-01-15.~~FINDINGS:~Joint spaces: Moderate medial compartment joint space narrowing. Mild lateral compartment and patellofemoral compartment narrowing.~Alignment: Normal. No varus or valgus deformity.~Osseous structures: Marginal osteophyte formation medially and laterally. Small suprapatellar joint effusion. No fracture.~Soft tissues: No significant soft tissue swelling.~~IMPRESSION:~1. Moderate tricompartmental osteoarthritis, slightly progressed compared to prior.~2. Small suprapatellar joint effusion.||||||F
```

---

## 11. ORM^O01 - Radiology order for MRI lumbar spine from IU Health

```
MSH|^~\&|EHR|IUHEALTH|POWERSCRIBE|IUHEALTH_RAD|20250505081500||ORM^O01|ORM-IUH-20250505-006839|P|2.4|||AL|NE
PID|1||MRN-70284913^^^IUHEALTH^MR||Marsh^Kevin^Russell^^||19830722|M||W|3620 Winthrop Ave^^Indianapolis^IN^46220^USA||^PRN^PH^^1^317^6641028|||||||685-01-3724
PV1|1|O|RAD^MRI^02||||2573018^Yoder^Carolyn^J^^^MD|2573018^Yoder^Carolyn^J^^^MD||RAD||||||||V|VN-20250505-0678^^^IUHEALTH^VN|||||||||||||||||||||||||20250505070000
ORC|NW|ORD-RAD-20250505-678^IUHEALTH||||||1^^^20250505080000^^R||20250505081500|2573018^Yoder^Carolyn^J^^^MD|2573018^Yoder^Carolyn^J^^^MD|2573018^Yoder^Carolyn^J^^^MD||^WPN^PH^^1^317^9621000||||||IUHEALTH^IU Health
OBR|1|ORD-RAD-20250505-678^IUHEALTH||72148^MRI LUMBAR SPINE WO CONTRAST^CPT4|||20250505100000|||A|||||2573018^Yoder^Carolyn^J^^^MD|^WPN^PH^^1^317^9621000
```

---

## 12. ORU^R01 - MRI lumbar spine report from IU Health

```
MSH|^~\&|POWERSCRIBE|IUHEALTH_RAD|EHR|IUHEALTH|20250505152000||ORU^R01|PS-IUH-20250505-017493|P|2.4|||AL|NE
PID|1||MRN-70284913^^^IUHEALTH^MR||Marsh^Kevin^Russell^^||19830722|M||W|3620 Winthrop Ave^^Indianapolis^IN^46220^USA||^PRN^PH^^1^317^6641028|||||||685-01-3724
PV1|1|O|RAD^MRI^02||||2573018^Yoder^Carolyn^J^^^MD|2573018^Yoder^Carolyn^J^^^MD||RAD||||||||V|VN-20250505-0678^^^IUHEALTH^VN|||||||||||||||||||||||||20250505070000
ORC|RE|ORD-RAD-20250505-678^IUHEALTH|PS-RPT-20250505-017493^POWERSCRIBE||||1^^^20250505080000^^R||20250505152000|2573018^Yoder^Carolyn^J^^^MD|2573018^Yoder^Carolyn^J^^^MD|2573018^Yoder^Carolyn^J^^^MD||^WPN^PH^^1^317^9621000||||||IUHEALTH^IU Health
OBR|1|ORD-RAD-20250505-678^IUHEALTH|PS-RPT-20250505-017493^POWERSCRIBE|72148^MRI LUMBAR SPINE WO CONTRAST^CPT4|||20250505103000|||||||||||2573018^Yoder^Carolyn^J^^^MD||RAD-ACC-20250505-0678||||20250505152000|||F|||||||4628103^Kirkland^Elaine^N^^^MD^Radiology
OBX|1|TX|72148^MRI LUMBAR SPINE WO CONTRAST^CPT4|1|MRI LUMBAR SPINE WITHOUT CONTRAST~~CLINICAL INDICATION: Radiculopathy, left lower extremity weakness.~~TECHNIQUE: Multiplanar, multisequence MRI of the lumbar spine without IV contrast.~~COMPARISON: Lumbar spine X-ray dated 2025-03-15.~~FINDINGS:~L1-L2: No disc herniation or stenosis.~L2-L3: Mild disc bulge without significant stenosis.~L3-L4: Moderate disc bulge with mild bilateral foraminal narrowing.~L4-L5: Large left posterolateral disc extrusion measuring 8mm, causing severe left lateral recess stenosis and compression of the left L5 nerve root. Moderate central canal stenosis.~L5-S1: Mild disc bulge with mild bilateral foraminal narrowing.~Conus medullaris: Normal in position and signal, terminating at L1.~Vertebral bodies: Normal marrow signal. No compression fracture.~~IMPRESSION:~1. Large left posterolateral disc extrusion at L4-L5 with severe left lateral recess stenosis and left L5 nerve root compression.~2. Multilevel degenerative disc disease.||||||F
```

---

## 13. ORU^R01 - CT head without contrast from Deaconess Health, Evansville with embedded PDF

```
MSH|^~\&|POWERSCRIBE|DEACONESS_RAD|EHR|DEACONESS|20250820031500||ORU^R01|PS-DEAC-20250820-018374|P|2.4|||AL|NE
PID|1||MRN-82041937^^^DEACONESS^MR||Mcintyre^Lawrence^Franklin^^||19580920|M||W|4512 Washington Ave^^Evansville^IN^47714^USA||^PRN^PH^^1^812^3319482|||||||762-40-8193
PV1|1|E|ED^BED06^01||||2791034^Shelton^Gregory^T^^^MD|2791034^Shelton^Gregory^T^^^MD||RAD||||||||E|VN-20250820-0234^^^DEACONESS^VN|||||||||||||||||||||||||20250820020000
ORC|RE|ORD-RAD-20250820-234^DEACONESS|PS-RPT-20250820-018374^POWERSCRIBE||||1^^^20250820023000^^S||20250820031500|2791034^Shelton^Gregory^T^^^MD|2791034^Shelton^Gregory^T^^^MD|2791034^Shelton^Gregory^T^^^MD||^WPN^PH^^1^812^4501000||||||DEACONESS^Deaconess Health
OBR|1|ORD-RAD-20250820-234^DEACONESS|PS-RPT-20250820-018374^POWERSCRIBE|70450^CT HEAD WO CONTRAST^CPT4|||20250820024500|||||||||||2791034^Shelton^Gregory^T^^^MD||RAD-ACC-20250820-0234||||20250820031500|||F|||||||2894031^Compton^Rebecca^S^^^MD^Radiology
OBX|1|ED|70450^CT HEAD WO CONTRAST^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
OBX|2|TX|70450^CT HEAD WO CONTRAST^CPT4|2|CT HEAD WITHOUT CONTRAST~~CLINICAL INDICATION: Acute onset left-sided weakness, rule out stroke.~~TECHNIQUE: Non-contrast helical CT of the head.~~COMPARISON: None.~~FINDINGS:~Brain parenchyma: No acute intracranial hemorrhage. No large territory infarct identified. Mild periventricular white matter hypodensities consistent with chronic small vessel ischemic disease.~Ventricles: Normal in size and configuration.~Midline: No shift.~Extra-axial spaces: No extra-axial collection.~Calvarium: Intact. No fracture.~Paranasal sinuses: Clear.~Mastoids: Aerated.~~IMPRESSION:~1. No acute intracranial hemorrhage or large territory infarct.~2. Chronic small vessel ischemic disease.~3. Consider MRI with diffusion for further evaluation of acute ischemia.||||||F
```

---

## 14. ORU^R01 - Renal ultrasound from IU Health Bloomington

```
MSH|^~\&|POWERSCRIBE|IUHEALTH_RAD|EHR|IUHEALTH|20250610142000||ORU^R01|PS-IUH-20250610-019285|P|2.4|||AL|NE
PID|1||MRN-94201738^^^IUHEALTH^MR||Underwood^Dale^Vernon^^||19650415|M||W|1215 W Kirkwood Ave^^Bloomington^IN^47404^USA||^PRN^PH^^1^812^3394201|||||||893-04-2716
PV1|1|O|RAD^US^04||||3094821^Hensley^Monica^A^^^MD|3094821^Hensley^Monica^A^^^MD||RAD||||||||V|VN-20250610-0789^^^IUHEALTH^VN|||||||||||||||||||||||||20250610130000
ORC|RE|ORD-RAD-20250610-789^IUHEALTH|PS-RPT-20250610-019285^POWERSCRIBE||||1^^^20250610130000^^R||20250610142000|3094821^Hensley^Monica^A^^^MD|3094821^Hensley^Monica^A^^^MD|3094821^Hensley^Monica^A^^^MD||^WPN^PH^^1^812^3532000||||||IUHEALTH^IU Health Bloomington
OBR|1|ORD-RAD-20250610-789^IUHEALTH|PS-RPT-20250610-019285^POWERSCRIBE|76770^US RETROPERITONEAL COMPLETE^CPT4|||20250610133000|||||||||||3094821^Hensley^Monica^A^^^MD||RAD-ACC-20250610-0789||||20250610142000|||F|||||||3410982^Maxwell^Jonathan^R^^^MD^Radiology
OBX|1|TX|76770^US RETROPERITONEAL COMPLETE^CPT4|1|ULTRASOUND KIDNEYS AND RETROPERITONEUM~~CLINICAL INDICATION: Elevated creatinine, rule out obstruction.~~TECHNIQUE: Real-time gray scale and color Doppler ultrasound of the kidneys.~~COMPARISON: None.~~FINDINGS:~Right kidney: Measures 10.5 cm in length. Normal cortical echogenicity. No hydronephrosis. No renal calculi. No solid mass.~Left kidney: Measures 10.8 cm in length. Mild increased cortical echogenicity. No hydronephrosis. A 1.5 cm simple cyst in the lower pole. No solid mass.~Bladder: Normal distension. No wall thickening.~Aorta: Not well visualized due to body habitus.~~IMPRESSION:~1. Mild increased left renal cortical echogenicity, which may be seen with medical renal disease.~2. 1.5 cm simple left renal cyst, benign.~3. No hydronephrosis or obstructing calculi bilaterally.||||||F
```

---

## 15. ORM^O01 - Radiology order for hip X-ray from Community Health Network

```
MSH|^~\&|EHR|CHN|POWERSCRIBE|CHN_RAD|20250901091500||ORM^O01|ORM-CHN-20250901-007394|P|2.4|||AL|NE
PID|1||MRN-13482079^^^CHN^MR||Hutchinson^Walter^Clifford^^||19520815|M||W|5107 N Keystone Ave^^Indianapolis^IN^46220^USA||^PRN^PH^^1^317^4438291|||||||091-28-5374
PV1|1|O|RAD^XRAY^01||||3804129^Sparks^Lorraine^T^^^MD|3804129^Sparks^Lorraine^T^^^MD||RAD||||||||V|VN-20250901-0891^^^CHN^VN|||||||||||||||||||||||||20250901080000
ORC|NW|ORD-RAD-20250901-891^CHN||||||1^^^20250901090000^^R||20250901091500|3804129^Sparks^Lorraine^T^^^MD|3804129^Sparks^Lorraine^T^^^MD|3804129^Sparks^Lorraine^T^^^MD||^WPN^PH^^1^317^3557000||||||CHN^Community Health Network
OBR|1|ORD-RAD-20250901-891^CHN||73502^XR HIP 2 VIEWS^CPT4|||20250901100000|||A|||||3804129^Sparks^Lorraine^T^^^MD|^WPN^PH^^1^317^3557000
```

---

## 16. ORU^R01 - Hip X-ray report from Community Health Network

```
MSH|^~\&|POWERSCRIBE|CHN_RAD|EHR|CHN|20250901113000||ORU^R01|PS-CHN-20250901-020481|P|2.4|||AL|NE
PID|1||MRN-13482079^^^CHN^MR||Hutchinson^Walter^Clifford^^||19520815|M||W|5107 N Keystone Ave^^Indianapolis^IN^46220^USA||^PRN^PH^^1^317^4438291|||||||091-28-5374
PV1|1|O|RAD^XRAY^01||||3804129^Sparks^Lorraine^T^^^MD|3804129^Sparks^Lorraine^T^^^MD||RAD||||||||V|VN-20250901-0891^^^CHN^VN|||||||||||||||||||||||||20250901080000
ORC|RE|ORD-RAD-20250901-891^CHN|PS-RPT-20250901-020481^POWERSCRIBE||||1^^^20250901090000^^R||20250901113000|3804129^Sparks^Lorraine^T^^^MD|3804129^Sparks^Lorraine^T^^^MD|3804129^Sparks^Lorraine^T^^^MD||^WPN^PH^^1^317^3557000||||||CHN^Community Health Network
OBR|1|ORD-RAD-20250901-891^CHN|PS-RPT-20250901-020481^POWERSCRIBE|73502^XR HIP 2 VIEWS^CPT4|||20250901100000|||||||||||3804129^Sparks^Lorraine^T^^^MD||RAD-ACC-20250901-0891||||20250901113000|||F|||||||3801294^Quintero^Nathan^D^^^MD^Radiology
OBX|1|TX|73502^XR HIP 2 VIEWS^CPT4|1|XR RIGHT HIP 2 VIEWS (AP AND LATERAL)~~CLINICAL INDICATION: Right hip pain, rule out fracture.~~COMPARISON: None.~~FINDINGS:~Right hip: Moderate degenerative changes with joint space narrowing superolaterally. Marginal osteophytes of the femoral head and acetabulum. Subchondral sclerosis. No acute fracture or dislocation.~Pelvis: Degenerative changes of the bilateral sacroiliac joints. No lytic or blastic lesions.~Soft tissues: No significant soft tissue abnormality.~~IMPRESSION:~1. Moderate right hip osteoarthritis.~2. No acute fracture or dislocation.||||||F
```

---

## 17. ORU^R01 - Shoulder MRI report with embedded PDF from Franciscan Health, Carmel

```
MSH|^~\&|POWERSCRIBE|FRANCISCAN_RAD|EHR|FRANCISCAN|20250715163000||ORU^R01|PS-FRAN-20250715-021308|P|2.4|||AL|NE
PID|1||MRN-20493817^^^FRANCISCAN^MR||Blackwell^Harold^Wayne^^||19720612|M||W|7315 Shelborne Rd^^Carmel^IN^46032^USA||^PRN^PH^^1^317^8824019|||||||951-40-2837
PV1|1|O|RAD^MRI^02||||4092138^Hoffman^Kenneth^W^^^MD|4092138^Hoffman^Kenneth^W^^^MD||RAD||||||||V|VN-20250715-0345^^^FRANCISCAN^VN|||||||||||||||||||||||||20250715140000
ORC|RE|ORD-RAD-20250715-345^FRANCISCAN|PS-RPT-20250715-021308^POWERSCRIBE||||1^^^20250715140000^^R||20250715163000|4092138^Hoffman^Kenneth^W^^^MD|4092138^Hoffman^Kenneth^W^^^MD|4092138^Hoffman^Kenneth^W^^^MD||^WPN^PH^^1^317^5284000||||||FRANCISCAN^Franciscan Health
OBR|1|ORD-RAD-20250715-345^FRANCISCAN|PS-RPT-20250715-021308^POWERSCRIBE|73221^MRI SHOULDER WO CONTRAST^CPT4|||20250715143000|||||||||||4092138^Hoffman^Kenneth^W^^^MD||RAD-ACC-20250715-0345||||20250715163000|||F|||||||4194028^Espinoza^Martha^C^^^MD^Radiology
OBX|1|ED|73221^MRI SHOULDER WO CONTRAST^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
OBX|2|TX|73221^MRI SHOULDER WO CONTRAST^CPT4|2|MRI RIGHT SHOULDER WITHOUT CONTRAST~~CLINICAL INDICATION: Right shoulder pain, limited range of motion.~~TECHNIQUE: Multiplanar, multisequence MRI of the right shoulder without IV contrast.~~COMPARISON: Right shoulder X-ray dated 2025-05-20.~~FINDINGS:~Rotator cuff: Full-thickness tear of the supraspinatus tendon measuring 1.5 cm in the AP dimension with 1.2 cm of retraction. Mild fatty infiltration of the supraspinatus muscle (Goutallier grade 2). Infraspinatus and subscapularis tendons intact.~Biceps tendon: Long head of the biceps is subluxed medially from the bicipital groove.~Labrum: Superior labral tear extending from 10 o'clock to 2 o'clock position (SLAP type II).~Glenohumeral joint: Small joint effusion. No loose bodies.~Acromioclavicular joint: Moderate degenerative changes with inferior osteophyte.~~IMPRESSION:~1. Full-thickness supraspinatus tear with mild retraction and early fatty infiltration.~2. Medial subluxation of the long head of the biceps tendon.~3. Superior labral tear (SLAP type II).~4. Moderate AC joint degenerative changes.||||||F
```

---

## 18. ORU^R01 - Cervical spine X-ray from Parkview Health emergency department

```
MSH|^~\&|POWERSCRIBE|PARKVIEW_RAD|EHR|PARKVIEW|20250228043000||ORU^R01|PS-PV-20250228-022719|P|2.4|||AL|NE
PID|1||MRN-31047289^^^PARKVIEW^MR||Grimes^Tyler^Bennett^^||19890722|M||W|2503 S Calhoun St^^Fort Wayne^IN^46807^USA||^PRN^PH^^1^260^7713029|||||||904-21-5083
PV1|1|E|ED^BED03^01||||4501382^Cantrell^Roger^M^^^MD|4501382^Cantrell^Roger^M^^^MD||RAD||||||||E|VN-20250228-0456^^^PARKVIEW^VN|||||||||||||||||||||||||20250228030000
ORC|RE|ORD-RAD-20250228-456^PARKVIEW|PS-RPT-20250228-022719^POWERSCRIBE||||1^^^20250228033000^^S||20250228043000|4501382^Cantrell^Roger^M^^^MD|4501382^Cantrell^Roger^M^^^MD|4501382^Cantrell^Roger^M^^^MD||^WPN^PH^^1^260^2666000||||||PARKVIEW^Parkview Health
OBR|1|ORD-RAD-20250228-456^PARKVIEW|PS-RPT-20250228-022719^POWERSCRIBE|72040^XR CERVICAL SPINE 2-3 VIEWS^CPT4|||20250228034500|||||||||||4501382^Cantrell^Roger^M^^^MD||RAD-ACC-20250228-0456||||20250228043000|||F|||||||4702918^Whitmore^Philip^G^^^MD^Radiology
OBX|1|TX|72040^XR CERVICAL SPINE 2-3 VIEWS^CPT4|1|XR CERVICAL SPINE 3 VIEWS~~CLINICAL INDICATION: Motor vehicle accident, neck pain.~~COMPARISON: None.~~FINDINGS:~Alignment: Normal cervical lordosis maintained. No subluxation.~Vertebral bodies: Normal height and alignment from C1 through C7. No fracture.~Disc spaces: Mild disc space narrowing at C5-C6 and C6-C7 with anterior osteophyte formation.~Prevertebral soft tissues: Normal. No prevertebral soft tissue swelling.~Atlantoaxial relationship: Normal.~~IMPRESSION:~1. No acute cervical spine fracture or malalignment.~2. Mild degenerative changes at C5-C6 and C6-C7.||||||F
```

---

## 19. ORM^O01 - Radiology order for pelvic ultrasound from Franciscan Health

```
MSH|^~\&|EHR|FRANCISCAN|POWERSCRIBE|FRANCISCAN_RAD|20250903091500||ORM^O01|ORM-FRAN-20250903-008291|P|2.4|||AL|NE
PID|1||MRN-42098371^^^FRANCISCAN^MR||Robles^Megan^Alicia^^||19920830|F||W|3910 E 10th St^^Indianapolis^IN^46201^USA||^PRN^PH^^1^317^9938204|||||||120-53-4897
PV1|1|O|RAD^US^04||||4819302^Harmon^Sandra^L^^^MD|4819302^Harmon^Sandra^L^^^MD||RAD||||||||V|VN-20250903-0567^^^FRANCISCAN^VN|||||||||||||||||||||||||20250903080000
ORC|NW|ORD-RAD-20250903-567^FRANCISCAN||||||1^^^20250903090000^^R||20250903091500|4819302^Harmon^Sandra^L^^^MD|4819302^Harmon^Sandra^L^^^MD|4819302^Harmon^Sandra^L^^^MD||^WPN^PH^^1^317^5284000||||||FRANCISCAN^Franciscan Health
OBR|1|ORD-RAD-20250903-567^FRANCISCAN||76856^US PELVIC COMPLETE^CPT4|||20250903100000|||A|||||4819302^Harmon^Sandra^L^^^MD|^WPN^PH^^1^317^5284000
```

---

## 20. ORU^R01 - Pelvic ultrasound report with embedded PDF from Franciscan Health

```
MSH|^~\&|POWERSCRIBE|FRANCISCAN_RAD|EHR|FRANCISCAN|20250903143000||ORU^R01|PS-FRAN-20250903-023104|P|2.4|||AL|NE
PID|1||MRN-42098371^^^FRANCISCAN^MR||Robles^Megan^Alicia^^||19920830|F||W|3910 E 10th St^^Indianapolis^IN^46201^USA||^PRN^PH^^1^317^9938204|||||||120-53-4897
PV1|1|O|RAD^US^04||||4819302^Harmon^Sandra^L^^^MD|4819302^Harmon^Sandra^L^^^MD||RAD||||||||V|VN-20250903-0567^^^FRANCISCAN^VN|||||||||||||||||||||||||20250903080000
ORC|RE|ORD-RAD-20250903-567^FRANCISCAN|PS-RPT-20250903-023104^POWERSCRIBE||||1^^^20250903090000^^R||20250903143000|4819302^Harmon^Sandra^L^^^MD|4819302^Harmon^Sandra^L^^^MD|4819302^Harmon^Sandra^L^^^MD||^WPN^PH^^1^317^5284000||||||FRANCISCAN^Franciscan Health
OBR|1|ORD-RAD-20250903-567^FRANCISCAN|PS-RPT-20250903-023104^POWERSCRIBE|76856^US PELVIC COMPLETE^CPT4|||20250903103000|||||||||||4819302^Harmon^Sandra^L^^^MD||RAD-ACC-20250903-0567||||20250903143000|||F|||||||5029183^Brennan^Kathleen^V^^^MD^Radiology
OBX|1|ED|76856^US PELVIC COMPLETE^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
OBX|2|TX|76856^US PELVIC COMPLETE^CPT4|2|ULTRASOUND PELVIS COMPLETE~~CLINICAL INDICATION: Abnormal uterine bleeding, pelvic pain.~~TECHNIQUE: Transabdominal and transvaginal ultrasound of the pelvis.~~COMPARISON: Pelvic ultrasound dated 2024-09-15.~~FINDINGS:~Uterus: Anteverted, measuring 10.2 x 5.8 x 6.1 cm. Heterogeneous myometrium with a 3.2 cm intramural fibroid in the posterior wall (previously 2.8 cm). Endometrial stripe measures 8mm, normal for proliferative phase.~Right ovary: Normal, measuring 3.1 x 2.0 x 1.8 cm. Normal follicular pattern. No dominant mass.~Left ovary: Measures 3.4 x 2.2 x 2.0 cm. Contains a 2.0 cm simple cyst, likely functional.~Cul-de-sac: No free fluid.~~IMPRESSION:~1. 3.2 cm posterior intramural fibroid, slightly increased from prior (2.8 cm).~2. Left ovarian simple cyst, likely functional. Recommend follow-up in 6-8 weeks.~3. Normal endometrial stripe.||||||F
```
