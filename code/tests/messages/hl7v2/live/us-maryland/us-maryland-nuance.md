# Nuance PowerScribe - real HL7v2 ER7 messages

## 1. ORU^R01 - Chest X-ray PA and lateral report with embedded PDF from Johns Hopkins

```
MSH|^~\&|POWERSCRIBE|JH_RAD|EHR|JHHOSP|20250312143500||ORU^R01|PS-JH-20250312-001234|P|2.4|||AL|NE
PID|1||MRN-40029644^^^JHHOSP^MR||BLACKWELL^Ursula^Christine^^||19580324|F||W|6435 Democracy Blvd^^Smithsburg^MD^21783^USA||^PRN^PH^^1^410^9354425|||||||538-41-6720
PV1|1|O|RAD^XRAY^01||||5470949932^Middleton^Ingham^G^^^MD|3428570058^Blackstone^Rosemary^F^^^MD||RAD||||||||V|VN-20250312-0087^^^JHHOSP^VN|||||||||||||||||||||||||20250312090000
ORC|RE|ORD-RAD-20250312-087^JHHOSP|PS-RPT-20250312-001234^POWERSCRIBE||||1^^^20250312090000^^R||20250312143500|VVENKATE^Venkatesh^Vivienne^Y^^^MD|1847205936^Okafor^Emeka^N^^^MD|5470949932^Middleton^Ingham^G^^^MD||^WPN^PH^^1^410^9553000||||||JHHOSP^Johns Hopkins Hospital
OBR|1|ORD-RAD-20250312-087^JHHOSP|PS-RPT-20250312-001234^POWERSCRIBE|71020^XR CHEST PA AND LATERAL^CPT4|||20250312091500|||||||||||1847205936^Okafor^Emeka^N^^^MD||RAD-ACC-20250312-0087||||20250312143500|||F|||||||3920184756^Whitfield^Carolyn^J^^^MD^Radiology
OBX|1|ED|71020^XR CHEST PA AND LATERAL^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
OBX|2|TX|71020^XR CHEST PA AND LATERAL^CPT4|2|CHEST X-RAY PA AND LATERAL~~CLINICAL INDICATION: Cough, shortness of breath.~~COMPARISON: Chest X-ray dated 2024-11-15.~~FINDINGS:~The lungs are clear bilaterally without focal consolidation, pleural effusion, or pneumothorax. The cardiac silhouette is normal in size. The mediastinal contours are unremarkable. The osseous structures are intact without acute fracture.~~IMPRESSION: No acute cardiopulmonary disease.||||||F
```

---

## 2. ORU^R01 - CT abdomen and pelvis report with embedded PDF from MedStar Georgetown

```
MSH|^~\&|POWERSCRIBE|MEDSTAR_RAD|EHR|MEDSTARGTWN|20250418102300||ORU^R01|PS-MG-20250418-003412|P|2.4|||AL|NE
PID|1||MRN-65689057^^^MEDSTARGTWN^MR||ADEBAYO^Quinton^Harrison^^||19670815|M||W|5210 River Rd^^Owings Mills^MD^21117^USA||^PRN^PH^^1^443^6535470|||||||271-83-4590
PV1|1|O|RAD^CT^03||||9923849799^Haverford^Hartley^N^^^MD|5813356427^Westmoreland^Prudence^L^^^MD||RAD||||||||V|VN-20250418-0214^^^MEDSTARGTWN^VN|||||||||||||||||||||||||20250418080000
ORC|RE|ORD-RAD-20250418-214^MEDSTARGTWN|PS-RPT-20250418-003412^POWERSCRIBE||||1^^^20250418080000^^R||20250418102300|FXIONG^Xiong^Felicity^W^^^MD|2093847561^Kapoor^Vivek^S^^^MD|9923849799^Haverford^Hartley^N^^^MD||^WPN^PH^^1^202^4447000||||||MEDSTARGTWN^MedStar Georgetown University Hospital
OBR|1|ORD-RAD-20250418-214^MEDSTARGTWN|PS-RPT-20250418-003412^POWERSCRIBE|74178^CT ABD AND PELVIS WITH CONTRAST^CPT4|||20250418083000|||||||||||2093847561^Kapoor^Vivek^S^^^MD||RAD-ACC-20250418-0214||||20250418102300|||F|||||||4718293056^Yamamoto^Kenji^A^^^MD^Radiology
OBX|1|ED|74178^CT ABD AND PELVIS WITH CONTRAST^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
OBX|2|TX|74178^CT ABD AND PELVIS WITH CONTRAST^CPT4|2|CT ABDOMEN AND PELVIS WITH IV CONTRAST~~CLINICAL INDICATION: Abdominal pain, rule out appendicitis.~~TECHNIQUE: Helical CT of the abdomen and pelvis following administration of 100 mL Omnipaque 350 IV.~~COMPARISON: None.~~FINDINGS:~Liver: Mild hepatic steatosis. No focal lesion.~Gallbladder: Normal. No gallstones.~Pancreas: Normal in size and attenuation.~Spleen: Normal.~Kidneys: Normal bilaterally. No hydronephrosis.~Appendix: Normal in caliber measuring 5mm. No periappendiceal fat stranding.~Bowel: Normal. No obstruction or wall thickening.~Lymph nodes: No pathologically enlarged lymph nodes.~~IMPRESSION:~1. Mild hepatic steatosis.~2. No acute abdominal pathology. Normal appendix.||||||F
```

---

## 3. ORU^R01 - MRI brain with and without contrast from University of Maryland

```
MSH|^~\&|POWERSCRIBE|UMMC_RAD|EHR|UMMCBALT|20250527161200||ORU^R01|PS-UM-20250527-005678|P|2.4|||AL|NE
PID|1||MRN-32156632^^^UMMCBALT^MR||HENDRICKS^Helena^Marian^^||19790512|F||W|7645 Georgia Ave^^Rockville^MD^20852^USA||^PRN^PH^^1^240^7586516|||||||614-29-8053
PV1|1|O|RAD^MRI^02||||6446161215^Alderman^Thurmond^A^^^MD|3609764116^Stratford^Georgiana^R^^^MD||RAD||||||||V|VN-20250527-0345^^^UMMCBALT^VN|||||||||||||||||||||||||20250527130000
ORC|RE|ORD-RAD-20250527-345^UMMCBALT|PS-RPT-20250527-005678^POWERSCRIBE||||1^^^20250527130000^^R||20250527161200|EKINGSLE^Kingsley^Estelle^V^^^MD|5029183746^Lindstrom^Erik^W^^^MD|6446161215^Alderman^Thurmond^A^^^MD||^WPN^PH^^1^410^3285000||||||UMMCBALT^University of Maryland Medical Center
OBR|1|ORD-RAD-20250527-345^UMMCBALT|PS-RPT-20250527-005678^POWERSCRIBE|70553^MRI BRAIN W AND WO CONTRAST^CPT4|||20250527133000|||||||||||5029183746^Lindstrom^Erik^W^^^MD||RAD-ACC-20250527-0345||||20250527161200|||F|||||||6183920475^Adesanya^Folake^O^^^MD^Neuroradiology
OBX|1|ED|70553^MRI BRAIN W AND WO CONTRAST^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
OBX|2|TX|70553^MRI BRAIN W AND WO CONTRAST^CPT4|2|MRI BRAIN WITH AND WITHOUT IV CONTRAST~~CLINICAL INDICATION: Headaches, rule out intracranial pathology.~~TECHNIQUE: Multiplanar, multisequence MRI of the brain performed before and after IV administration of 15 mL Gadavist.~~COMPARISON: None.~~FINDINGS:~Brain parenchyma: Normal gray-white matter differentiation. No acute infarct on diffusion-weighted imaging. No hemorrhage.~Ventricles: Normal in size and morphology.~Extra-axial spaces: Small 8mm extra-axial mass along the left parietal convexity with homogeneous enhancement, consistent with meningioma.~Midline structures: No shift.~Posterior fossa: Normal cerebellum and brainstem.~Orbits: Normal.~~IMPRESSION:~1. Small left parietal meningioma measuring 8mm. Recommend follow-up MRI in 12 months.~2. No acute intracranial pathology.||||||F
```

---

## 4. MDM^T02 - Transcription notification for mammogram report from MedStar Union Memorial

```
MSH|^~\&|POWERSCRIBE|MEDSTAR_RAD|DOCMGMT|MEDSTARUM|20250214093800||MDM^T02|PS-MDM-MU-20250214-000891|P|2.4|||AL|NE
EVN|T02|20250214093800
PID|1||MRN-21580688^^^MEDSTARUM^MR||KINNEY^Marisol^Suzanne^^||19640722|F||W|9105 New Hampshire Ave^^Rockville^MD^20852^USA||^PRN^PH^^1^301^3236727|||||||723-40-1589
PV1|1|O|RAD^MAMMO^05||||8108396162^Mcgowan^Dashiell^G^^^MD|6905582716^Buchanan^Rosemary^F^^^MD||RAD||||||||V|VN-20250214-0123^^^MEDSTARUM^VN|||||||||||||||||||||||||20250214080000
TXA|1|RAD|TX|20250214093800|8108396162^Mcgowan^Dashiell^G^^^MD||20250214093800||8108396162^Mcgowan^Dashiell^G^^^MD||||PS-RPT-MU-20250214-000891|MEDSTAR_RAD||||AU||AV
OBX|1|TX|77067^SCREENING MAMMOGRAM BILATERAL^CPT4|1|SCREENING MAMMOGRAM BILATERAL~~CLINICAL INDICATION: Annual screening mammography. No palpable abnormality.~~TECHNIQUE: Standard CC and MLO views of both breasts were obtained using digital tomosynthesis.~~COMPARISON: Screening mammogram dated 2024-02-10.~~BREAST COMPOSITION: The breasts are heterogeneously dense (ACR density C).~~FINDINGS:~Right breast: No suspicious mass, architectural distortion, or suspicious calcifications.~Left breast: No suspicious mass, architectural distortion, or suspicious calcifications.~Axillary regions: No suspicious lymphadenopathy.~~IMPRESSION: Negative. No mammographic evidence of malignancy.~~BI-RADS: 1 - Negative.~~RECOMMENDATION: Routine annual screening mammography.||||||F
```

---

## 5. ORU^R01 - Lumbar spine X-ray report from LifeBridge Sinai Hospital

```
MSH|^~\&|POWERSCRIBE|SINAI_RAD|EHR|SINAIHOSP|20250605091200||ORU^R01|PS-SH-20250605-002345|P|2.4|||AL|NE
PID|1||MRN-50455372^^^SINAIHOSP^MR||VANG^Vernon^Yancy^^||19720315|M||B|4892 Edmondson Ave^^Baltimore^MD^21213^USA||^PRN^PH^^1^410^2343641|||||||841-36-2097
PV1|1|O|RAD^XRAY^02||||9362926410^Middleton^Ingham^N^^^MD|2223364742^Blackstone^Prudence^L^^^MD||RAD||||||||V|VN-20250605-0156^^^SINAIHOSP^VN|||||||||||||||||||||||||20250605080000
ORC|RE|ORD-RAD-20250605-156^SINAIHOSP|PS-RPT-20250605-002345^POWERSCRIBE||||1^^^20250605080000^^R||20250605091200|MDIALLO^Diallo^Marisol^Q^^^MD|8294017563^Delgado^Fernando^V^^^MD|9362926410^Middleton^Ingham^N^^^MD||^WPN^PH^^1^410^6019000||||||SINAIHOSP^Sinai Hospital of Baltimore
OBR|1|ORD-RAD-20250605-156^SINAIHOSP|PS-RPT-20250605-002345^POWERSCRIBE|72100^XR LUMBAR SPINE 2 OR 3 VIEWS^CPT4|||20250605082000|||||||||||8294017563^Delgado^Fernando^V^^^MD||RAD-ACC-20250605-0156||||20250605091200|||F|||||||1047382956^Johansson^Ingrid^K^^^MD^Radiology
OBX|1|TX|72100^XR LUMBAR SPINE 2 OR 3 VIEWS^CPT4|1|LUMBAR SPINE X-RAY, 3 VIEWS~~CLINICAL INDICATION: Low back pain, radiculopathy.~~COMPARISON: None.~~FINDINGS:~Five lumbar vertebral bodies are normal in height and alignment. Moderate degenerative disc disease at L4-L5 and L5-S1 with disc space narrowing and endplate sclerosis. Mild facet hypertrophy at L4-L5. No spondylolisthesis. No compression fracture. The sacroiliac joints appear normal.~~IMPRESSION:~1. Moderate degenerative disc disease at L4-L5 and L5-S1.~2. Mild facet arthropathy at L4-L5.~3. No acute osseous abnormality.||||||F
```

---

## 6. ORM^O01 - CT head order from MedStar Harbor Hospital ED

```
MSH|^~\&|EHR|MEDSTARHBR|POWERSCRIBE|MEDSTARHBR_RAD|20250710041500||ORM^O01|ORD-HB-20250710-001234|P|2.4|||AL|NE
PID|1||MRN-25140287^^^MEDSTARHBR^MR||SIZEMORE^Darnell^Duane^^||19650210|M||B|8870 Colesville Rd^^Rockville^MD^20852^USA||^PRN^PH^^1^240^2436408|||||||482-07-3916
PV1|1|E|ED^ED03^01||||4088493269^Haverford^Hartley^A^^^MD|6763419858^Westmoreland^Georgiana^R^^^MD||EM||||||||V|VN-20250710-0034^^^MEDSTARHBR^VN|||||||||||||||||||||||||20250710040000
ORC|NW|ORD-RAD-20250710-034^MEDSTARHBR||||||1^^^20250710041500^^S||20250710041500|6150293847^Nazari^Farhan^M^^^MD|4088493269^Haverford^Hartley^A^^^MD|4088493269^Haverford^Hartley^A^^^MD||^WPN^PH^^1^410^3505000||||||MEDSTARHBR^MedStar Harbor Hospital
OBR|1|ORD-RAD-20250710-034^MEDSTARHBR||70450^CT HEAD WITHOUT CONTRAST^CPT4|STAT|20250710041500|||||Fall with head strike, loss of consciousness||||||||6150293847^Nazari^Farhan^M^^^MD||||||||||1^^^20250710041500^^S
```

---

## 7. ORU^R01 - CT head without contrast report from MedStar Harbor Hospital

```
MSH|^~\&|POWERSCRIBE|MEDSTARHBR_RAD|EHR|MEDSTARHBR|20250710054500||ORU^R01|PS-HB-20250710-001567|P|2.4|||AL|NE
PID|1||MRN-82599450^^^MEDSTARHBR^MR||REEVES^Roderick^Charles^^||19650210|M||B|6470 Marlboro Pike^^Laurel^MD^20708^USA||^PRN^PH^^1^410^2375024|||||||482-07-3916
PV1|1|E|ED^ED03^01||||3376506268^Alderman^Thurmond^G^^^MD|4999041162^Stratford^Rosemary^F^^^MD||EM||||||||V|VN-20250710-0034^^^MEDSTARHBR^VN|||||||||||||||||||||||||20250710040000
ORC|RE|ORD-RAD-20250710-034^MEDSTARHBR|PS-RPT-20250710-001567^POWERSCRIBE||||1^^^20250710040000^^S||20250710054500|VMOSLEY^Mosley^Valentina^Y^^^MD|6150293847^Nazari^Farhan^M^^^MD|3376506268^Alderman^Thurmond^G^^^MD||^WPN^PH^^1^410^3505000||||||MEDSTARHBR^MedStar Harbor Hospital
OBR|1|ORD-RAD-20250710-034^MEDSTARHBR|PS-RPT-20250710-001567^POWERSCRIBE|70450^CT HEAD WITHOUT CONTRAST^CPT4|||20250710043000|||||||||||6150293847^Nazari^Farhan^M^^^MD||RAD-ACC-20250710-0034||||20250710054500|||F|||||||9384720156^Castellano^Bianca^R^^^MD^Radiology
OBX|1|TX|70450^CT HEAD WITHOUT CONTRAST^CPT4|1|CT HEAD WITHOUT CONTRAST~~CLINICAL INDICATION: Fall with head strike, loss of consciousness.~~TECHNIQUE: Non-contrast helical CT of the head.~~COMPARISON: None.~~FINDINGS:~No acute intracranial hemorrhage. No midline shift. The ventricles are normal in size and configuration. Gray-white matter differentiation is preserved. Periventricular white matter hypodensities consistent with chronic small vessel ischemic disease. No acute territorial infarct. Mild mucosal thickening in the right maxillary sinus. The visualized orbits are unremarkable. No calvarial fracture.~~IMPRESSION:~1. No acute intracranial abnormality.~2. Chronic small vessel ischemic disease.||||||F
```

---

## 8. ORU^R01 - Knee MRI report from Johns Hopkins Bayview

```
MSH|^~\&|POWERSCRIBE|JHBV_RAD|EHR|JHBAYVIEW|20250818141000||ORU^R01|PS-BV-20250818-004567|P|2.4|||AL|NE
PID|1||MRN-59587909^^^JHBAYVIEW^MR||SUBRAMANIAM^Aldric^Harrison^^||19830920|M||W|3770 East-West Hwy^^Chesapeake Beach^MD^20732^USA||^PRN^PH^^1^240^2377754|||||||309-72-4185
PV1|1|O|RAD^MRI^04||||3656861132^Mcgowan^Dashiell^N^^^MD|6693312439^Buchanan^Prudence^L^^^MD||RAD||||||||V|VN-20250818-0267^^^JHBAYVIEW^VN|||||||||||||||||||||||||20250818120000
ORC|RE|ORD-RAD-20250818-267^JHBAYVIEW|PS-RPT-20250818-004567^POWERSCRIBE||||1^^^20250818120000^^R||20250818141000|DPADILLA^Padilla^Delphine^E^^^MD|4817290365^Chandra^Rajesh^P^^^MD|3656861132^Mcgowan^Dashiell^N^^^MD||^WPN^PH^^1^410^5505000||||||JHBAYVIEW^Johns Hopkins Bayview Medical Center
OBR|1|ORD-RAD-20250818-267^JHBAYVIEW|PS-RPT-20250818-004567^POWERSCRIBE|73721^MRI KNEE WITHOUT CONTRAST^CPT4|||20250818123000|||||||||||4817290365^Chandra^Rajesh^P^^^MD||RAD-ACC-20250818-0267||||20250818141000|||F|||||||7503928146^Obeng^Kwame^D^^^MD^Musculoskeletal Radiology
OBX|1|TX|73721^MRI KNEE WITHOUT CONTRAST^CPT4|1|MRI RIGHT KNEE WITHOUT CONTRAST~~CLINICAL INDICATION: Right knee pain and swelling, rule out meniscal tear.~~TECHNIQUE: Multiplanar, multisequence MRI of the right knee without contrast.~~COMPARISON: None.~~FINDINGS:~Menisci: Complex tear of the posterior horn of the medial meniscus extending to the inferior articular surface. Lateral meniscus intact.~Ligaments: ACL and PCL intact. MCL and LCL intact.~Cartilage: Grade 2 chondromalacia of the medial femoral condyle.~Effusion: Small joint effusion.~Bones: No fracture or bone marrow edema.~~IMPRESSION:~1. Complex tear, posterior horn medial meniscus.~2. Grade 2 chondromalacia, medial femoral condyle.~3. Small joint effusion.||||||F
```

---

## 9. ORU^R01 - Ultrasound abdomen report from Adventist HealthCare Shady Grove

```
MSH|^~\&|POWERSCRIBE|ADVENT_RAD|EHR|ADVENTIST_SG|20250422101500||ORU^R01|PS-AG-20250422-003456|P|2.4|||AL|NE
PID|1||MRN-25912899^^^ADVENTIST_SG^MR||FITZSIMMONS^Josephine^Marian^^||19820714|F||W|8441 Eastern Ave^^Baltimore^MD^21201^USA||^PRN^PH^^1^301^5953781|||||||603-28-9147
PV1|1|O|RAD^US^01||||6187416916^Middleton^Ingham^A^^^MD|2184831875^Blackstone^Georgiana^R^^^MD||RAD||||||||V|VN-20250422-0198^^^ADVENTIST_SG^VN|||||||||||||||||||||||||20250422090000
ORC|RE|ORD-RAD-20250422-198^ADVENTIST_SG|PS-RPT-20250422-003456^POWERSCRIBE||||1^^^20250422090000^^R||20250422101500|LBELLAMY^Bellamy^Liliana^Z^^^MD|3928105746^Petrov^Andrei^G^^^MD|6187416916^Middleton^Ingham^A^^^MD||^WPN^PH^^1^240^8263000||||||ADVENTIST_SG^Adventist HealthCare Shady Grove
OBR|1|ORD-RAD-20250422-198^ADVENTIST_SG|PS-RPT-20250422-003456^POWERSCRIBE|76700^US ABDOMEN COMPLETE^CPT4|||20250422091500|||||||||||3928105746^Petrov^Andrei^G^^^MD||RAD-ACC-20250422-0198||||20250422101500|||F|||||||8140273956^Blackwell^Sonia^T^^^MD^Radiology
OBX|1|TX|76700^US ABDOMEN COMPLETE^CPT4|1|ULTRASOUND ABDOMEN COMPLETE~~CLINICAL INDICATION: Right upper quadrant pain.~~TECHNIQUE: Real-time grayscale and color Doppler sonography of the abdomen.~~COMPARISON: None.~~FINDINGS:~Liver: Normal in size and echogenicity. No focal hepatic lesion.~Gallbladder: Multiple gallstones, largest measuring 1.2 cm. No gallbladder wall thickening or pericholecystic fluid. No sonographic Murphy sign.~Common bile duct: Normal caliber, 4mm.~Pancreas: Partially visualized, normal.~Kidneys: Right kidney 10.8 cm, left kidney 11.2 cm. Normal cortical thickness. No hydronephrosis or renal calculi.~Spleen: Normal.~Aorta: Normal caliber.~~IMPRESSION:~1. Cholelithiasis without evidence of acute cholecystitis.~2. Otherwise normal abdominal ultrasound.||||||F
```

---

## 10. ORM^O01 - CT pulmonary angiography order from UMMC ED

```
MSH|^~\&|EHR|UMMCBALT|POWERSCRIBE|UMMC_RAD|20250830022000||ORM^O01|ORD-UM-20250830-002345|P|2.4|||AL|NE
PID|1||MRN-26556426^^^UMMCBALT^MR||OKONKWO^Vincent^Stanley^^||19630712|M||W|1345 Dual Hwy^^Washington^DC^20016^USA||^PRN^PH^^1^202^7487667|||||||716-04-2839
PV1|1|E|ED^ED07^01||||1198104984^Haverford^Hartley^G^^^MD|8744758078^Westmoreland^Rosemary^F^^^MD||EM||||||||V|VN-20250830-0089^^^UMMCBALT^VN|||||||||||||||||||||||||20250830020000
ORC|NW|ORD-RAD-20250830-089^UMMCBALT||||||1^^^20250830022000^^S||20250830022000|2740918365^Obi^Chidinma^A^^^MD|1198104984^Haverford^Hartley^G^^^MD|1198104984^Haverford^Hartley^G^^^MD||^WPN^PH^^1^410^3285000||||||UMMCBALT^University of Maryland Medical Center
OBR|1|ORD-RAD-20250830-089^UMMCBALT||71275^CTA CHEST PULMONARY EMBOLISM^CPT4|STAT|20250830022000|||||Chest pain, tachycardia, elevated D-dimer, rule out PE||||||||2740918365^Obi^Chidinma^A^^^MD||||||||||1^^^20250830022000^^S
```

---

## 11. ORU^R01 - CTA chest for pulmonary embolism from UMMC

```
MSH|^~\&|POWERSCRIBE|UMMC_RAD|EHR|UMMCBALT|20250830034500||ORU^R01|PS-UM-20250830-002567|P|2.4|||AL|NE
PID|1||MRN-22191449^^^UMMCBALT^MR||STRICKLAND^Horace^Yancy^^||19630712|M||W|6045 Hillen Rd^^Bel Air^MD^21014^USA||^PRN^PH^^1^301^9789910|||||||716-04-2839
PV1|1|E|ED^ED07^01||||7942343148^Alderman^Thurmond^N^^^MD|8484533043^Stratford^Prudence^L^^^MD||EM||||||||V|VN-20250830-0089^^^UMMCBALT^VN|||||||||||||||||||||||||20250830020000
ORC|RE|ORD-RAD-20250830-089^UMMCBALT|PS-RPT-20250830-002567^POWERSCRIBE||||1^^^20250830020000^^S||20250830034500|LMOUA^Moua^Liliana^V^^^MD|2740918365^Obi^Chidinma^A^^^MD|7942343148^Alderman^Thurmond^N^^^MD||^WPN^PH^^1^410^3285000||||||UMMCBALT^University of Maryland Medical Center
OBR|1|ORD-RAD-20250830-089^UMMCBALT|PS-RPT-20250830-002567^POWERSCRIBE|71275^CTA CHEST PULMONARY EMBOLISM^CPT4|||20250830025000|||||||||||2740918365^Obi^Chidinma^A^^^MD||RAD-ACC-20250830-0089||||20250830034500|||F|||||||5029183746^Lindstrom^Erik^W^^^MD^Cardiothoracic Radiology
OBX|1|TX|71275^CTA CHEST PULMONARY EMBOLISM^CPT4|1|CTA CHEST - PULMONARY EMBOLISM PROTOCOL~~CLINICAL INDICATION: Chest pain, tachycardia, elevated D-dimer. Rule out pulmonary embolism.~~TECHNIQUE: CTA of the chest performed following administration of 80 mL Omnipaque 350 IV with bolus tracking.~~COMPARISON: None.~~FINDINGS:~Pulmonary arteries: Acute filling defect identified in the right lower lobe segmental pulmonary artery. No saddle embolus. Left pulmonary arteries are patent.~Heart: Normal in size. No pericardial effusion.~Lungs: Subsegmental atelectasis at the right base. No consolidation or pleural effusion.~Mediastinum: Normal. No lymphadenopathy.~~IMPRESSION:~1. Acute pulmonary embolism involving the right lower lobe segmental pulmonary artery.~2. No evidence of right heart strain.||||||F
```

---

## 12. ORU^R01 - Shoulder X-ray from Anne Arundel Medical Center

```
MSH|^~\&|POWERSCRIBE|AAMC_RAD|EHR|AAMC|20250915111500||ORU^R01|PS-AA-20250915-005678|P|2.4|||AL|NE
PID|1||MRN-98175360^^^AAMC^MR||CLAYBORNE^Chantal^Darlene^^||19680205|F||W|3795 Virginia Ave^^Clear Spring^MD^21722^USA||^PRN^PH^^1^410^9022073|||||||852-19-3740
PV1|1|O|RAD^XRAY^01||||6031883822^Mcgowan^Dashiell^A^^^MD|2677517409^Buchanan^Georgiana^R^^^MD||RAD||||||||V|VN-20250915-0312^^^AAMC^VN|||||||||||||||||||||||||20250915100000
ORC|RE|ORD-RAD-20250915-312^AAMC|PS-RPT-20250915-005678^POWERSCRIBE||||1^^^20250915100000^^R||20250915111500|FKAPOOR^Kapoor^Francesca^A^^^MD|1593728406^Mbeki^Thandiwe^N^^^MD|6031883822^Mcgowan^Dashiell^A^^^MD||^WPN^PH^^1^443^4815000||||||AAMC^Anne Arundel Medical Center
OBR|1|ORD-RAD-20250915-312^AAMC|PS-RPT-20250915-005678^POWERSCRIBE|73030^XR SHOULDER 2 VIEWS^CPT4|||20250915102000|||||||||||1593728406^Mbeki^Thandiwe^N^^^MD||RAD-ACC-20250915-0312||||20250915111500|||F|||||||4261839507^Russo^Vincent^M^^^MD^Radiology
OBX|1|TX|73030^XR SHOULDER 2 VIEWS^CPT4|1|LEFT SHOULDER X-RAY, 2 VIEWS~~CLINICAL INDICATION: Left shoulder pain after fall.~~COMPARISON: None.~~FINDINGS:~Moderate to severe degenerative changes of the acromioclavicular joint with inferior osteophyte formation. Superior migration of the humeral head suggesting chronic rotator cuff tear. No acute fracture or dislocation. The glenohumeral joint space is maintained.~~IMPRESSION:~1. Severe acromioclavicular degenerative disease.~2. Superior humeral head migration suggesting chronic rotator cuff pathology.~3. No acute fracture or dislocation.||||||F
```

---

## 13. ORU^R01 - CT cervical spine from GBMC emergency

```
MSH|^~\&|POWERSCRIBE|GBMC_RAD|EHR|GBMC|20250503063000||ORU^R01|PS-GB-20250503-001890|P|2.4|||AL|NE
PID|1||MRN-51108665^^^GBMC^MR||KAPOOR^Dominic^Charles^^||19580901|M||W|9615 Pulaski Hwy^^Wheaton^MD^20902^USA||^PRN^PH^^1^301^6974709|||||||940-51-2387
PV1|1|E|ED^ED02^01||||5822865003^Blackstone^Jarrett^T^^^MD|6679387442^Worthington^Constance^N^^^MD||EM||||||||V|VN-20250503-0015^^^GBMC^VN|||||||||||||||||||||||||20250503055000
ORC|RE|ORD-RAD-20250503-015^GBMC|PS-RPT-20250503-001890^POWERSCRIBE||||1^^^20250503055000^^S||20250503063000|GBHATIA^Bhatia^Genevieve^Z^^^MD|8073921465^Stankowicz^Halina^V^^^MD|5822865003^Blackstone^Jarrett^T^^^MD||^WPN^PH^^1^443^8493000||||||GBMC^Greater Baltimore Medical Center
OBR|1|ORD-RAD-20250503-015^GBMC|PS-RPT-20250503-001890^POWERSCRIBE|72125^CT CERVICAL SPINE WITHOUT CONTRAST^CPT4|||20250503060000|||||||||||8073921465^Stankowicz^Halina^V^^^MD||RAD-ACC-20250503-0015||||20250503063000|||F|||||||2093847561^Kapoor^Vivek^S^^^MD^Neuroradiology
OBX|1|TX|72125^CT CERVICAL SPINE WITHOUT CONTRAST^CPT4|1|CT CERVICAL SPINE WITHOUT CONTRAST~~CLINICAL INDICATION: Motor vehicle collision, neck pain.~~TECHNIQUE: Helical CT of the cervical spine without contrast with sagittal and coronal reformations.~~COMPARISON: None.~~FINDINGS:~Alignment: Normal cervical lordosis. No malalignment or listhesis.~Vertebral bodies: Normal height. No compression fracture.~Disc spaces: Mild degenerative disc disease at C5-C6 and C6-C7 with small anterior osteophytes.~Spinal canal: No significant canal stenosis.~Neural foramina: Mild bilateral foraminal narrowing at C5-C6.~Prevertebral soft tissues: Normal. No prevertebral swelling to suggest ligamentous injury.~~IMPRESSION:~1. No acute fracture or traumatic malalignment.~2. Mild degenerative changes at C5-C6 and C6-C7.||||||F
```

---

## 14. ORU^R01 - Chest CT with contrast from Johns Hopkins with embedded PDF

```
MSH|^~\&|POWERSCRIBE|JH_RAD|EHR|JHHOSP|20250620143000||ORU^R01|PS-JH-20250620-006789|P|2.4|||AL|NE
PID|1||MRN-40179792^^^JHHOSP^MR||CRAWFORD^Omar^Otis^^||19550930|M||B|6435 Democracy Blvd^^Severna Park^MD^21146^USA||^PRN^PH^^1^443^9944627|||||||425-81-6039
PV1|1|I|ONCW^4210^01||||5574546335^Westmoreland^Osborn^L^^^MD|5590385667^Greenfield^Arabella^T^^^MD||ONC||||||||V|VN-20250620-0456^^^JHHOSP^VN|||||||||||||||||||||||||20250619080000
ORC|RE|ORD-RAD-20250620-456^JHHOSP|PS-RPT-20250620-006789^POWERSCRIBE||||1^^^20250619080000^^R||20250620143000|JKIRKPAT^Kirkpatrick^Jolene^Q^^^MD|9481027365^Schuster^Helena^B^^^MD|5574546335^Westmoreland^Osborn^L^^^MD||^WPN^PH^^1^410^9553000||||||JHHOSP^Johns Hopkins Hospital
OBR|1|ORD-RAD-20250620-456^JHHOSP|PS-RPT-20250620-006789^POWERSCRIBE|71260^CT CHEST WITH CONTRAST^CPT4|||20250620100000|||||||||||9481027365^Schuster^Helena^B^^^MD||RAD-ACC-20250620-0456||||20250620143000|||F|||||||3920184756^Whitfield^Carolyn^J^^^MD^Thoracic Radiology
OBX|1|ED|71260^CT CHEST WITH CONTRAST^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
OBX|2|TX|71260^CT CHEST WITH CONTRAST^CPT4|2|CT CHEST WITH IV CONTRAST~~CLINICAL INDICATION: Known lung adenocarcinoma, restaging.~~TECHNIQUE: Helical CT of the chest following administration of 100 mL Omnipaque 350 IV.~~COMPARISON: CT chest dated 2025-03-15.~~FINDINGS:~Right upper lobe: The previously identified 2.8 cm spiculated mass now measures 2.2 cm, representing interval decrease. No new pulmonary nodules.~Mediastinum: Previously noted subcarinal lymph node now measures 1.0 cm, decreased from 1.5 cm.~Pleura: No effusion.~Heart: Normal.~Bones: No suspicious osseous lesion.~~IMPRESSION:~1. Interval decrease in right upper lobe mass, now 2.2 cm (previously 2.8 cm), consistent with partial treatment response.~2. Decreased subcarinal lymphadenopathy.||||||F
```

---

## 15. ORM^O01 - MRI lumbar spine order from MedStar Montgomery

```
MSH|^~\&|EHR|MEDSTARMTG|POWERSCRIBE|MEDSTARMTG_RAD|20250722090000||ORM^O01|ORD-MM-20250722-003456|P|2.4|||AL|NE
PID|1||MRN-71564125^^^MEDSTARMTG^MR||BAKARE^Wendell^Ulysses^^||19680830|M||A|2555 University Blvd^^Silver Spring^MD^20906^USA||^PRN^PH^^1^301^7854609|||||||359-62-0814
PV1|1|O|RAD^MRI^03||||2940312836^Stratford^Whitaker^K^^^MD|8889729195^Eastwood^Cordelia^H^^^MD||RAD||||||||V|VN-20250722-0234^^^MEDSTARMTG^VN|||||||||||||||||||||||||20250722080000
ORC|NW|ORD-RAD-20250722-234^MEDSTARMTG||||||1^^^20250722093000^^R||20250722090000|6839201547^Fitzgerald^Moira^C^^^MD|2940312836^Stratford^Whitaker^K^^^MD|2940312836^Stratford^Whitaker^K^^^MD||^WPN^PH^^1^301^7741600||||||MEDSTARMTG^MedStar Montgomery Medical Center
OBR|1|ORD-RAD-20250722-234^MEDSTARMTG||72148^MRI LUMBAR SPINE WITHOUT CONTRAST^CPT4|ROUTINE|20250722093000|||||Low back pain with left leg radiculopathy x 6 weeks||||||||6839201547^Fitzgerald^Moira^C^^^MD||||||||||1^^^20250722093000^^R
```

---

## 16. ORU^R01 - Echocardiogram report from MedStar Union Memorial

```
MSH|^~\&|POWERSCRIBE|MEDSTARUM_RAD|EHR|MEDSTARUM|20250405153000||ORU^R01|PS-MU-20250405-007890|P|2.4|||AL|NE
PID|1||MRN-46065252^^^MEDSTARUM^MR||GENTRY^Clifton^Alvin^^||19480705|M||W|6435 Democracy Blvd^^Glen Burnie^MD^21060^USA||^PRN^PH^^1^301^2725179|||||||190-47-8263
PV1|1|O|RAD^ECHO^02||||9792929703^Buchanan^Everett^T^^^MD|5066865322^Whitcomb^Constance^N^^^MD||CAR||||||||V|VN-20250405-0345^^^MEDSTARUM^VN|||||||||||||||||||||||||20250405130000
ORC|RE|ORD-RAD-20250405-345^MEDSTARUM|PS-RPT-20250405-007890^POWERSCRIBE||||1^^^20250405130000^^R||20250405153000|OHARDING^Harding^Ophelia^P^^^MD|7150482936^Aguilar^Roberto^H^^^MD|9792929703^Buchanan^Everett^T^^^MD||^WPN^PH^^1^410^5546000||||||MEDSTARUM^MedStar Union Memorial Hospital
OBR|1|ORD-RAD-20250405-345^MEDSTARUM|PS-RPT-20250405-007890^POWERSCRIBE|93306^ECHOCARDIOGRAM COMPLETE^CPT4|||20250405133000|||||||||||7150482936^Aguilar^Roberto^H^^^MD||RAD-ACC-20250405-0345||||20250405153000|||F|||||||5820417396^Deshpande^Nikhil^V^^^MD^Cardiology
OBX|1|TX|93306^ECHOCARDIOGRAM COMPLETE^CPT4|1|ECHOCARDIOGRAM - TRANSTHORACIC, COMPLETE~~CLINICAL INDICATION: Heart failure follow-up. History of ischemic cardiomyopathy.~~TECHNIQUE: Standard 2D, M-mode, spectral and color Doppler echocardiography.~~COMPARISON: Echocardiogram dated 2024-10-12.~~FINDINGS:~Left ventricle: Mildly dilated. Moderate global hypokinesis. Estimated LVEF 35% (previously 38%). Akinesis of the inferior wall.~Right ventricle: Normal size and function.~Left atrium: Mildly dilated.~Valves: Mild mitral regurgitation. Mild tricuspid regurgitation. No aortic stenosis.~Pericardium: No effusion.~~IMPRESSION:~1. Moderate LV systolic dysfunction, LVEF 35%, mildly decreased from prior.~2. Inferior wall akinesis, consistent with prior infarct territory.~3. Mild mitral and tricuspid regurgitation.||||||F
```

---

## 17. ORU^R01 - Thyroid ultrasound from Suburban Hospital Bethesda

```
MSH|^~\&|POWERSCRIBE|SUBURB_RAD|EHR|SUBURBHOSP|20250310094500||ORU^R01|PS-SU-20250310-003456|P|2.4|||AL|NE
PID|1||MRN-35898136^^^SUBURBHOSP^MR||JENNINGS^Yvette^Faye^^||19750415|F||W|5210 River Rd^^Baltimore^MD^21217^USA||^PRN^PH^^1^410^3995177|||||||381-62-9047
PV1|1|O|RAD^US^02||||6323005389^Blackstone^Jarrett^L^^^MD|6077908362^Worthington^Arabella^T^^^MD||RAD||||||||V|VN-20250310-0156^^^SUBURBHOSP^VN|||||||||||||||||||||||||20250310090000
ORC|RE|ORD-RAD-20250310-156^SUBURBHOSP|PS-RPT-20250310-003456^POWERSCRIBE||||1^^^20250310090000^^R||20250310094500|CPRUITT^Pruitt^Claudette^K^^^MD|9274018356^Volkov^Dmitri^L^^^MD|6323005389^Blackstone^Jarrett^L^^^MD||^WPN^PH^^1^301^8962000||||||SUBURBHOSP^Suburban Hospital
OBR|1|ORD-RAD-20250310-156^SUBURBHOSP|PS-RPT-20250310-003456^POWERSCRIBE|76536^US THYROID^CPT4|||20250310091500|||||||||||9274018356^Volkov^Dmitri^L^^^MD||RAD-ACC-20250310-0156||||20250310094500|||F|||||||1629483057^Santiago^Isabel^F^^^MD^Radiology
OBX|1|TX|76536^US THYROID^CPT4|1|ULTRASOUND THYROID~~CLINICAL INDICATION: Palpable thyroid nodule.~~TECHNIQUE: Real-time grayscale and color Doppler sonography of the thyroid gland.~~COMPARISON: None.~~FINDINGS:~Right lobe: Measures 5.2 x 2.0 x 1.8 cm. A solid, hypoechoic nodule measuring 1.5 x 1.2 x 1.1 cm is identified in the mid right lobe. The nodule has irregular margins and microcalcifications. TI-RADS category 5 (highly suspicious).~Left lobe: Measures 4.8 x 1.8 x 1.6 cm. Homogeneous echogenicity. No focal nodule.~Isthmus: Normal, 3mm.~Cervical lymph nodes: No suspicious cervical lymphadenopathy.~~IMPRESSION:~1. Right thyroid nodule, 1.5 cm, TI-RADS 5 (highly suspicious). FNA biopsy recommended.~2. Normal left thyroid lobe.||||||F
```

---

## 18. ORM^O01 - CT abdomen pelvis order from Frederick Health ED

```
MSH|^~\&|EHR|FREDHOSP|POWERSCRIBE|FREDHOSP_RAD|20250901181500||ORM^O01|ORD-FH-20250901-004567|P|2.4|||AL|NE
PID|1||MRN-27174008^^^FREDHOSP^MR||KHOURY^Felicity^Estella^^||19880305|F||W|9502 Old Court Rd^^Baltimore^MD^21215^USA||^PRN^PH^^1^410^8734653|||||||527-81-4063
PV1|1|E|ED^ED05^01||||1673932749^Westmoreland^Osborn^K^^^MD|6543200573^Greenfield^Cordelia^H^^^MD||EM||||||||V|VN-20250901-0078^^^FREDHOSP^VN|||||||||||||||||||||||||20250901180000
ORC|NW|ORD-RAD-20250901-078^FREDHOSP||||||1^^^20250901181500^^S||20250901181500|4501829376^Richter^Klaus^D^^^MD|1673932749^Westmoreland^Osborn^K^^^MD|1673932749^Westmoreland^Osborn^K^^^MD||^WPN^PH^^1^240^5668000||||||FREDHOSP^Frederick Health Hospital
OBR|1|ORD-RAD-20250901-078^FREDHOSP||74178^CT ABD AND PELVIS WITH CONTRAST^CPT4|STAT|20250901181500|||||RLQ pain, rebound tenderness, WBC 15.2, rule out appendicitis||||||||4501829376^Richter^Klaus^D^^^MD||||||||||1^^^20250901181500^^S
```

---

## 19. ORU^R01 - Bone density DEXA scan from MedStar Good Samaritan

```
MSH|^~\&|POWERSCRIBE|MEDSTARGSAM_RAD|EHR|MEDSTARGSAM|20250225110000||ORU^R01|PS-GS-20250225-002345|P|2.4|||AL|NE
PID|1||MRN-31155251^^^MEDSTARGSAM^MR||FULTON^Katharine^Jacqueline^^||19580620|F||W|5547 Eutaw St^^Owings Mills^MD^21117^USA||^PRN^PH^^1^410^4255344|||||||264-90-5187
PV1|1|O|RAD^DEXA^01||||7205082658^Stratford^Whitaker^T^^^MD|8893218270^Eastwood^Constance^N^^^MD||RAD||||||||V|VN-20250225-0234^^^MEDSTARGSAM^VN|||||||||||||||||||||||||20250225100000
ORC|RE|ORD-RAD-20250225-234^MEDSTARGSAM|PS-RPT-20250225-002345^POWERSCRIBE||||1^^^20250225100000^^R||20250225110000|ECOVINGT^Covington^Eleanora^O^^^MD|3017492856^Novak^Irena^P^^^MD|7205082658^Stratford^Whitaker^T^^^MD||^WPN^PH^^1^443^4443000||||||MEDSTARGSAM^MedStar Good Samaritan Hospital
OBR|1|ORD-RAD-20250225-234^MEDSTARGSAM|PS-RPT-20250225-002345^POWERSCRIBE|77080^DEXA BONE DENSITY^CPT4|||20250225101500|||||||||||3017492856^Novak^Irena^P^^^MD||RAD-ACC-20250225-0234||||20250225110000|||F|||||||8140273956^Blackwell^Sonia^T^^^MD^Radiology
OBX|1|TX|77080^DEXA BONE DENSITY^CPT4|1|DEXA BONE DENSITY~~CLINICAL INDICATION: Postmenopausal female, age 66, screening for osteoporosis.~~TECHNIQUE: Dual-energy X-ray absorptiometry of the lumbar spine (L1-L4) and bilateral proximal femora.~~COMPARISON: DEXA dated 2023-03-10.~~FINDINGS:~Lumbar spine L1-L4: BMD 0.812 g/cm2, T-score -2.6 (osteoporosis range).~Left femoral neck: BMD 0.680 g/cm2, T-score -2.1 (osteopenia range).~Right femoral neck: BMD 0.695 g/cm2, T-score -1.9 (osteopenia range).~Left total hip: BMD 0.780 g/cm2, T-score -1.8 (osteopenia range).~~IMPRESSION:~1. Osteoporosis of the lumbar spine (T-score -2.6), worsened from prior (T-score -2.3 in 2023).~2. Osteopenia of the bilateral femoral necks and total hips.~3. Recommend pharmacologic treatment and follow-up DEXA in 2 years.||||||F
```

---

## 20. ORU^R01 - Abdominal X-ray from Meritus Medical Center with embedded PDF

```
MSH|^~\&|POWERSCRIBE|MERITUS_RAD|EHR|MERITUSMC|20250812091500||ORU^R01|PS-MR-20250812-008901|P|2.4|||AL|NE
PID|1||MRN-16350749^^^MERITUSMC^MR||GARNER^Penelope^Opal^^||19680115|F||W|2570 Potomac Ave^^Columbia^MD^21046^USA||^PRN^PH^^1^301^9772097|||||||803-14-6729
PV1|1|E|ED^ED03^01||||1468024249^Buchanan^Everett^L^^^MD|7468949615^Whitcomb^Arabella^T^^^MD||EM||||||||V|VN-20250812-0156^^^MERITUSMC^VN|||||||||||||||||||||||||20250812080000
ORC|RE|ORD-RAD-20250812-156^MERITUSMC|PS-RPT-20250812-008901^POWERSCRIBE||||1^^^20250812080000^^S||20250812091500|CBLACKWE^Blackwell^Cornelia^T^^^MD|5738201946^Balogun^Adeyemi^F^^^MD|1468024249^Buchanan^Everett^L^^^MD||^WPN^PH^^1^301^7906000||||||MERITUSMC^Meritus Medical Center
OBR|1|ORD-RAD-20250812-156^MERITUSMC|PS-RPT-20250812-008901^POWERSCRIBE|74000^XR ABDOMEN 1 VIEW^CPT4|||20250812083000|||||||||||5738201946^Balogun^Adeyemi^F^^^MD||RAD-ACC-20250812-0156||||20250812091500|||F|||||||2093847561^Kapoor^Vivek^S^^^MD^Radiology
OBX|1|ED|74000^XR ABDOMEN 1 VIEW^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
OBX|2|TX|74000^XR ABDOMEN 1 VIEW^CPT4|2|ABDOMINAL X-RAY, SUPINE~~CLINICAL INDICATION: Abdominal pain, nausea, vomiting.~~TECHNIQUE: Single supine view of the abdomen.~~COMPARISON: None.~~FINDINGS:~Bowel gas pattern: Mildly dilated loops of small bowel in the central abdomen with air-fluid levels suggesting early small bowel obstruction. No free intraperitoneal air. The colon is decompressed. No calcified gallstones or renal calculi identified. The osseous structures are unremarkable.~~IMPRESSION:~1. Findings suggestive of early small bowel obstruction. Recommend CT abdomen and pelvis with IV contrast for further evaluation.||||||F
```
