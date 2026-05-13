# Nuance PowerScribe - real HL7v2 ER7 messages

---

## 1. ORU^R01 - CT chest with contrast final report

```
MSH|^~\&|POWERSCRIBE|VUMC_RAD^1943827650^NPI|EPIC|VUMC_HIS|20260314091523||ORU^R01^ORU_R01|MSG20260314091523001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN7291843^^^VUMC^MR||CALDWELL^EARL^VINCENT||19580412|M|||2904 WOODMONT BLVD^^NASHVILLE^TN^37215^US||^PRN^PH^^1^615^4427831|||||531-76-4498
PV1|1|O|RAD^CT1^1^^^VUMC||||1372984^DESAI^PRIYA^M^^^MD|1372984^DESAI^PRIYA^M^^^MD|||RAD||||||||OP|VN729184300|||||||||||||||||||||||||20260314080000
ORC|RE|ORD6218734^EPIC|RAD20260314001^POWERSCRIBE||CM||||20260314080000|||1372984^DESAI^PRIYA^M^^^MD
OBR|1|ORD6218734^EPIC|RAD20260314001^POWERSCRIBE|71260^CT CHEST WITH CONTRAST^CPT4|||20260314083000||||||||1372984^DESAI^PRIYA^M^^^MD||||||20260314091500|||F|||||||1372984^DESAI^PRIYA^M^^^MD
OBX|1|FT|GDT^REPORT TEXT^L||EXAMINATION: CT Chest with IV Contrast\.br\\.br\CLINICAL INDICATION: 62-year-old male with persistent cough and weight loss. Rule out malignancy.\.br\\.br\COMPARISON: CT Chest dated 2025-11-20.\.br\\.br\TECHNIQUE: Helical CT of the chest was performed from the thoracic inlet through the adrenal glands following administration of 100 mL Omnipaque 350 IV contrast.\.br\\.br\FINDINGS:\.br\LUNGS: There is a 1.8 x 1.4 cm spiculated nodule in the right upper lobe (series 4, image 67), increased from 1.2 cm on prior exam. Additional 4 mm ground-glass nodule in the left lower lobe, unchanged. No pleural effusion.\.br\MEDIASTINUM: 1.3 cm pretracheal lymph node (station 4R). Subcarinal lymph node measures 1.1 cm, previously 0.8 cm.\.br\HEART: Normal cardiac size. No pericardial effusion. Coronary artery calcifications noted.\.br\BONES: Degenerative changes of the thoracic spine. No suspicious osseous lesions.\.br\\.br\IMPRESSION:\.br\1. Enlarging 1.8 cm spiculated right upper lobe nodule, highly suspicious for primary lung malignancy. PET-CT recommended.\.br\2. Enlarging mediastinal lymphadenopathy, concerning for nodal metastatic disease.\.br\3. Stable 4 mm left lower lobe ground-glass nodule.||||||F|||20260314091500
OBX|2|ST|RAD_CODE^RADLEX CODE^L||RID28488||||||F
OBX|3|ST|ACR_CODE^ACR ACTIONABILITY^L||4 - Suspicious||||||F
```

---

## 2. ORU^R01 - MRI brain without contrast preliminary report

```
MSH|^~\&|NUANCE_PS|BAPTIST_MEM^2847193056^NPI|MEDITECH|BAPTIST_HIS|20260315142837||ORU^R01^ORU_R01|MSG20260315142837002|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN5538271^^^BMHCC^MR||WARREN^THERESA^LYNN||19720825|F|||1743 UNION AVE^^MEMPHIS^TN^38104^US||^PRN^PH^^1^901^6629174|||||284-53-7192
PV1|1|I|NEURO^MRI2^1^^^BMHCC||||1584321^OKAFOR^NELSON^E^^^MD|1584321^OKAFOR^NELSON^E^^^MD|||RAD||||||||IP|VN553827100|||||||||||||||||||||||||20260315060000
ORC|RE|ORD8837421^MEDITECH|RAD20260315002^NUANCE_PS||CM||||20260315120000|||1584321^OKAFOR^NELSON^E^^^MD
OBR|1|ORD8837421^MEDITECH|RAD20260315002^NUANCE_PS|70551^MRI BRAIN WITHOUT CONTRAST^CPT4|||20260315130000||||||||1584321^OKAFOR^NELSON^E^^^MD||||||20260315142800|||P|||||||1584321^OKAFOR^NELSON^E^^^MD
OBX|1|FT|GDT^REPORT TEXT^L||EXAMINATION: MRI Brain without Contrast\.br\\.br\CLINICAL INDICATION: 53-year-old female presenting with new onset seizure and left-sided weakness.\.br\\.br\COMPARISON: None available.\.br\\.br\TECHNIQUE: Multiplanar multisequence MRI of the brain without gadolinium contrast including DWI, FLAIR, T1, T2, SWI sequences.\.br\\.br\FINDINGS:\.br\BRAIN PARENCHYMA: There is a 3.2 x 2.8 x 2.5 cm heterogeneous mass centered in the right temporal lobe with surrounding vasogenic edema extending into the right insula and frontal operculum. The mass demonstrates mixed signal on T2 with areas of hemorrhage on SWI. There is 4 mm rightward midline shift at the level of the septum pellucidum.\.br\VENTRICLES: Mild compression of the right lateral ventricle temporal horn. Trapping of the right temporal horn suggested.\.br\EXTRA-AXIAL SPACES: No extra-axial collection. No leptomeningeal enhancement (limited without contrast).\.br\POSTERIOR FOSSA: Cerebellum and brainstem are unremarkable. No tonsillar herniation.\.br\\.br\IMPRESSION:\.br\1. Right temporal lobe mass with hemorrhagic components and surrounding edema causing 4mm midline shift. High-grade glioma versus metastasis favored. URGENT neurosurgical consultation recommended.\.br\2. Recommend contrast-enhanced MRI for further characterization and MR spectroscopy.\.br\\.br\CRITICAL RESULT: Attending physician Dr. Marcus Webb notified by telephone at 14:30 on 03/15/2026 by Dr. Okafor.||||||P|||20260315142800
OBX|2|ST|CRITICAL^CRITICAL RESULT^L||YES - NEUROSURGICAL CONSULTATION||||||F
```

---

## 3. ORM^O01 - X-ray chest PA and lateral order

```
MSH|^~\&|EPIC|ERLANGER_HIS^3192847560^NPI|PSCRIBE360|ERLANGER_RAD|20260316080145||ORM^O01^ORM_O01|MSG20260316080145003|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN6184523^^^ERLANGER^MR||HENSLEY^CURTIS^RAY||19450918|M|||508 MCCALLIE AVE^^CHATTANOOGA^TN^37403^US||^PRN^PH^^1^423^7718432|||||367-22-5841
PV1|1|E|ED^BED12^1^^^ERLANGER||||1293147^TUCKER^MELANIE^A^^^MD||||||||||||EN|VN618452300|||||||||||||||||||||||||20260316074500
ORC|NW|ORD4781293^EPIC|RAD20260316003^PSCRIBE360||SC||||20260316080100|||1293147^TUCKER^MELANIE^A^^^MD
OBR|1|ORD4781293^EPIC|RAD20260316003^PSCRIBE360|71046^XRAY CHEST PA AND LATERAL^CPT4|||20260316080100||||||SHORTNESS OF BREATH, FEVER 101.2F, PRODUCTIVE COUGH X 3 DAYS|||||||||||||||||1293147^TUCKER^MELANIE^A^^^MD
```

---

## 4. ORU^R01 - X-ray chest PA and lateral final report

```
MSH|^~\&|PSCRIBE360|ERLANGER_RAD^3192847560^NPI|EPIC|ERLANGER_HIS|20260316093012||ORU^R01^ORU_R01|MSG20260316093012004|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN6184523^^^ERLANGER^MR||HENSLEY^CURTIS^RAY||19450918|M|||508 MCCALLIE AVE^^CHATTANOOGA^TN^37403^US||^PRN^PH^^1^423^7718432|||||367-22-5841
PV1|1|E|ED^BED12^1^^^ERLANGER||||1293147^TUCKER^MELANIE^A^^^MD|1293147^TUCKER^MELANIE^A^^^MD|||RAD||||||||EN|VN618452300|||||||||||||||||||||||||20260316074500
ORC|RE|ORD4781293^EPIC|RAD20260316003^PSCRIBE360||CM||||20260316080100|||1647382^NORRIS^KEITH^D^^^MD
OBR|1|ORD4781293^EPIC|RAD20260316003^PSCRIBE360|71046^XRAY CHEST PA AND LATERAL^CPT4|||20260316082000||||||||1647382^NORRIS^KEITH^D^^^MD||||||20260316093000|||F|||||||1647382^NORRIS^KEITH^D^^^MD
OBX|1|FT|GDT^REPORT TEXT^L||EXAMINATION: PA and Lateral Chest Radiograph\.br\\.br\CLINICAL INDICATION: 80-year-old male with shortness of breath, fever, productive cough x 3 days.\.br\\.br\COMPARISON: Chest radiograph dated 2025-09-14.\.br\\.br\FINDINGS:\.br\LUNGS: Dense consolidation in the right lower lobe with air bronchograms. Small right-sided pleural effusion layering dependently. Left lung is clear. No pneumothorax.\.br\HEART: Cardiomegaly with cardiothoracic ratio of 0.58. Aortic calcifications noted.\.br\MEDIASTINUM: Widened mediastinum likely related to tortuous aorta. No acute mediastinal abnormality.\.br\BONES: Osteopenic. Old healed right rib fractures laterally (ribs 7-8).\.br\\.br\IMPRESSION:\.br\1. Right lower lobe pneumonia with small associated parapneumonic effusion.\.br\2. Cardiomegaly, stable compared to prior.||||||F|||20260316093000
```

---

## 5. MDM^T02 - Radiology addendum for CT abdomen

```
MSH|^~\&|POWERSCRIBE|VUMC_RAD^1943827650^NPI|EPIC|VUMC_HIS|20260317111542||MDM^T02^MDM_T02|MSG20260317111542005|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|T02|20260317111542
PID|1||MRN4839217^^^VUMC^MR||FUENTES^MARISOL^ADRIANA||19681103|F|||1422 DICKERSON PIKE^^NASHVILLE^TN^37207^US||^PRN^PH^^1^629^5513847|||||241-68-9305
PV1|1|O|RAD^CT2^1^^^VUMC||||1372984^DESAI^PRIYA^M^^^MD||||||||||||OP|VN483921700|||||||||||||||||||||||||20260317090000
TXA|1|RAD^RADIOLOGY REPORT|FT|20260317111500|1372984^DESAI^PRIYA^M^^^MD||20260317111542|||||DOC88234521||||||AU
OBX|1|FT|GDT^ADDENDUM TEXT^L||ADDENDUM (03/17/2026 11:15):\.br\\.br\Upon further review of the CT Abdomen and Pelvis with contrast performed on 03/16/2026, the previously described 2.1 cm hepatic lesion in segment VII demonstrates arterial phase hyperenhancement with washout on portal venous phase. This is consistent with LI-RADS 5 (definite hepatocellular carcinoma) in the setting of known hepatitis C cirrhosis.\.br\\.br\Hepatology team (Dr. Calloway) notified via secure message at 11:10 on 03/17/2026.\.br\\.br\Original report otherwise unchanged.\.br\\.br\Electronically signed by: Priya M. Desai, MD\.br\Board Certified, Abdominal Imaging||||||F|||20260317111500
```

---

## 6. ADT^A04 - Patient registration for outpatient CT

```
MSH|^~\&|EPIC|TRISTAR_HIS^4021938475^NPI|POWERSCRIBE|TRISTAR_RAD|20260318063022||ADT^A04^ADT_A04|MSG20260318063022006|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A04|20260318063022
PID|1||MRN8417263^^^TRISTAR^MR||GRAINGER^LEON^PATRICK||19790214|M|||3710 LEBANON PIKE^^HERMITAGE^TN^37076^US||^PRN^PH^^1^615^3384912||ENG|M|BAP|518-43-7762|||N||||||||N
PV1|1|O|RAD^CT3^1^^^TRISTAR||||1829374^LYNCH^DIANA^C^^^MD||||||||||||OP|VN841726300|||||||||||||||||||||||||20260318063000
PV2|||^CT ABDOMEN PELVIS WITH CONTRAST|||||||||||||||||||||||||||||||20260318070000
IN1|1|BCBS_TN^BLUECROSS BLUESHIELD OF TENNESSEE|78432|BLUECROSS BLUESHIELD OF TENNESSEE|1 CAMERON HILL CIRCLE^^CHATTANOOGA^TN^37402|||||||20260101|20261231|||IND|GRAINGER^LEON^PATRICK|SELF|19790214|3710 LEBANON PIKE^^HERMITAGE^TN^37076^US|||||||||||||||XEK551928437||||||||||M
```

---

## 7. ORU^R01 - Ultrasound thyroid final report

```
MSH|^~\&|NUANCE_PS|PARKWEST_RAD^5273849106^NPI|CERNER|PARKWEST_HIS|20260319101245||ORU^R01^ORU_R01|MSG20260319101245007|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN2874391^^^PARKWEST^MR||SUTTON^BRENDA^NICOLE||19850607|F|||8014 KINGSTON PIKE^^KNOXVILLE^TN^37919^US||^PRN^PH^^1^865^9927431|||||492-17-6638
PV1|1|O|RAD^US1^1^^^PARKWEST||||1463928^HWANG^CHRISTINE^J^^^MD|1463928^HWANG^CHRISTINE^J^^^MD|||RAD||||||||OP|VN287439100|||||||||||||||||||||||||20260319090000
ORC|RE|ORD3821947^CERNER|RAD20260319007^NUANCE_PS||CM||||20260319090000|||1463928^HWANG^CHRISTINE^J^^^MD
OBR|1|ORD3821947^CERNER|RAD20260319007^NUANCE_PS|76536^US THYROID WITH DOPPLER^CPT4|||20260319093000||||||||1463928^HWANG^CHRISTINE^J^^^MD||||||20260319101200|||F|||||||1463928^HWANG^CHRISTINE^J^^^MD
OBX|1|FT|GDT^REPORT TEXT^L||EXAMINATION: Ultrasound of the Thyroid with Doppler\.br\\.br\CLINICAL INDICATION: Palpable thyroid nodule. Evaluate.\.br\\.br\COMPARISON: None.\.br\\.br\TECHNIQUE: Real-time grayscale and color Doppler sonography of the thyroid gland and cervical lymph nodes.\.br\\.br\FINDINGS:\.br\RIGHT LOBE: Measures 5.2 x 2.1 x 1.8 cm. Contains a 2.4 x 1.8 x 1.6 cm solid hypoechoic nodule with irregular margins, microcalcifications, and taller-than-wide morphology in transverse plane. Internal vascularity on Doppler. ACR TI-RADS score: 7 (TR5 - highly suspicious).\.br\LEFT LOBE: Measures 4.8 x 1.9 x 1.7 cm. 0.6 cm isoechoic nodule with smooth margins and no calcifications. ACR TI-RADS score: 2 (TR2 - not suspicious).\.br\ISTHMUS: 3 mm, normal.\.br\LYMPH NODES: Several normal-appearing bilateral level II-III cervical lymph nodes. No suspicious morphology.\.br\\.br\IMPRESSION:\.br\1. Highly suspicious 2.4 cm right thyroid nodule (TI-RADS TR5). FNA biopsy recommended per ACR guidelines.\.br\2. Benign-appearing 0.6 cm left thyroid nodule (TI-RADS TR2). No follow-up needed.||||||F|||20260319101200
OBX|2|ST|TIRADS^ACR TI-RADS^L||TR5 - Highly Suspicious||||||F
```

---

## 8. ORU^R01 - CT head without contrast with ED encapsulated PDF report

```
MSH|^~\&|POWERSCRIBE|BMHCC_RAD^2847193056^NPI|MEDITECH|BMHCC_HIS|20260320044512||ORU^R01^ORU_R01|MSG20260320044512008|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN7493128^^^BMHCC^MR||FREEMAN^HAROLD^WAYNE||19520301|M|||4512 QUINCE RD^^MEMPHIS^TN^38117^US||^PRN^PH^^1^901^3384721|||||319-47-8825
PV1|1|E|ED^BED04^1^^^BMHCC||||1584321^OKAFOR^NELSON^E^^^MD||||||||||||EN|VN749312800|||||||||||||||||||||||||20260320040000
ORC|RE|ORD2298471^MEDITECH|RAD20260320008^POWERSCRIBE||CM||||20260320041500|||1584321^OKAFOR^NELSON^E^^^MD
OBR|1|ORD2298471^MEDITECH|RAD20260320008^POWERSCRIBE|70450^CT HEAD WITHOUT CONTRAST^CPT4|||20260320041500||||||||1584321^OKAFOR^NELSON^E^^^MD||||||20260320044500|||F|||||||1584321^OKAFOR^NELSON^E^^^MD
OBX|1|FT|GDT^REPORT TEXT^L||EXAMINATION: CT Head without Contrast\.br\\.br\CLINICAL INDICATION: 74-year-old male, fall with head strike, on Eliquis, GCS 14.\.br\\.br\COMPARISON: None available.\.br\\.br\FINDINGS:\.br\There is a 7 mm crescentic hyperdensity along the right frontoparietal convexity consistent with acute subdural hematoma. No significant midline shift. No uncal or tonsillar herniation. Gray-white matter differentiation is preserved. Ventricles and sulci are prominent consistent with age-related volume loss. Periventricular and subcortical white matter hypodensities consistent with chronic small vessel ischemic disease. No epidural hematoma. No calvarial fracture. Mastoid air cells and paranasal sinuses are clear.\.br\\.br\IMPRESSION:\.br\1. Small acute right frontoparietal subdural hematoma without midline shift. CRITICAL FINDING - neurosurgery consulted.\.br\2. Chronic small vessel ischemic disease.\.br\\.br\CRITICAL RESULT: Dr. Angela Whitmore (neurosurgery on-call) notified by telephone at 04:47 on 03/20/2026.||||||F|||20260320044500
OBX|2|ED|PDF_RPT^PDF REPORT^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAyODQKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMCA3NzAgVGQKKENUIEhlYWQgV2l0aG91dCBDb250cmFzdCAtIEZpbmFsIFJlcG9ydCkgVGoKMTAgNzUwIFRkCihQYXRpZW50OiBGUkVFTUFOLCBIQVJPTEQgV0FZTkUpIFRqCjEwIDczMCBUZAooTVJOOiA3NDkzMTI4KSBUagoxMCA3MTAgVGQKKERPQjogMDMvMDEvMTk1MikgVGoKMTAgNjkwIFRkCihEYXRlOiAwMy8yMC8yMDI2KSBUagoxMCA2NTAgVGQKKElNUFJFU1NJT046IFNtYWxsIGFjdXRlIHJpZ2h0IGZyb250b3BhcmlldGFsIHN1YmR1cmFsIGhlbWF0b21hKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTU3IDAwMDAwIG4gCjAwMDAwMDAzMTMgMDAwMDAgbiAKMDAwMDAwMDY0OCAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjcyNwolJUVPRgo=||||||F|||20260320044500
OBX|3|ST|CRITICAL^CRITICAL RESULT^L||YES - NEUROSURGERY NOTIFIED||||||F
```

---

## 9. ORM^O01 - MRI lumbar spine with and without contrast order

```
MSH|^~\&|CERNER|PARKWEST_HIS^5273849106^NPI|NUANCE_PS|PARKWEST_RAD|20260320141823||ORM^O01^ORM_O01|MSG20260320141823009|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN4618293^^^PARKWEST^MR||RIGGS^DEBORAH^ELAINE||19670923|F|||215 PAPERMILL DR^^KNOXVILLE^TN^37909^US||^PRN^PH^^1^865^4417832|||||381-64-2297
PV1|1|O|ORTHO^CLINIC2^1^^^PARKWEST||||1738294^FIELDS^GREGORY^H^^^MD||||||||||||OP|VN461829300|||||||||||||||||||||||||20260320140000
ORC|NW|ORD5594712^CERNER|RAD20260320009^NUANCE_PS||SC||||20260320141800|||1738294^FIELDS^GREGORY^H^^^MD
OBR|1|ORD5594712^CERNER|RAD20260320009^NUANCE_PS|72148^MRI LUMBAR SPINE WITHOUT CONTRAST^CPT4|STAT||20260320141800||||||WORSENING BILATERAL LOWER EXTREMITY RADICULOPATHY. PRIOR LAMINECTOMY L4-5 2023. EVALUATE FOR RECURRENT DISC HERNIATION VS EPIDURAL FIBROSIS|||||||||||||||||1738294^FIELDS^GREGORY^H^^^MD
OBR|2|ORD5594712^CERNER|RAD20260320009^NUANCE_PS|72149^MRI LUMBAR SPINE WITH CONTRAST^CPT4|STAT||20260320141800||||||SAME|||||||||||||||||1738294^FIELDS^GREGORY^H^^^MD
```

---

## 10. ORU^R01 - Mammogram bilateral screening final report

```
MSH|^~\&|POWERSCRIBE|METHODIST_RAD^6518293740^NPI|EPIC|METHODIST_HIS|20260321103422||ORU^R01^ORU_R01|MSG20260321103422010|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN8214739^^^METHODIST^MR||WHITFIELD^CAROLYN^RENEE||19730315|F|||2917 FOREST HILL IRENE RD^^GERMANTOWN^TN^38138^US||^PRN^PH^^1^901^7724518|||||271-43-8856
PV1|1|O|RAD^MAMMO1^1^^^METHODIST||||1927384^AZIZ^SAMIRA^K^^^MD|1927384^AZIZ^SAMIRA^K^^^MD|||RAD||||||||OP|VN821473900|||||||||||||||||||||||||20260321093000
ORC|RE|ORD7293148^EPIC|RAD20260321010^POWERSCRIBE||CM||||20260321093000|||1927384^AZIZ^SAMIRA^K^^^MD
OBR|1|ORD7293148^EPIC|RAD20260321010^POWERSCRIBE|77067^SCREENING MAMMOGRAM BILATERAL^CPT4|||20260321095500||||||||1927384^AZIZ^SAMIRA^K^^^MD||||||20260321103400|||F|||||||1927384^AZIZ^SAMIRA^K^^^MD
OBX|1|FT|GDT^REPORT TEXT^L||EXAMINATION: Bilateral Screening Mammogram (3D Tomosynthesis)\.br\\.br\CLINICAL INDICATION: Annual screening. No symptoms. No family history of breast cancer.\.br\\.br\COMPARISON: Screening mammogram dated 2025-03-18.\.br\\.br\BREAST COMPOSITION: The breasts are heterogeneously dense (ACR density C), which may obscure small masses.\.br\\.br\FINDINGS:\.br\RIGHT BREAST: No suspicious mass, architectural distortion, or suspicious calcifications. Stable benign-appearing calcifications in the upper outer quadrant.\.br\LEFT BREAST: No suspicious mass, architectural distortion, or suspicious calcifications. Stable oil cyst in the retroareolar region from prior biopsy (2019).\.br\AXILLARY REGIONS: No suspicious lymphadenopathy bilaterally.\.br\\.br\IMPRESSION:\.br\Negative bilateral screening mammogram.\.br\BI-RADS Category 1 - Negative.\.br\\.br\RECOMMENDATION: Continue annual screening mammography.||||||F|||20260321103400
OBX|2|ST|BIRADS^BI-RADS CATEGORY^L||1 - Negative||||||F
```

---

## 11. ADT^A08 - Patient information update for radiology encounter

```
MSH|^~\&|EPIC|VUMC_HIS^1943827650^NPI|POWERSCRIBE|VUMC_RAD|20260322091234||ADT^A08^ADT_A08|MSG20260322091234011|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A08|20260322091234
PID|1||MRN7291843^^^VUMC^MR||CALDWELL^EARL^VINCENT||19580412|M|||2904 WOODMONT BLVD^^NASHVILLE^TN^37215^US||^PRN^PH^^1^615^4427831||ENG|M|MET|531-76-4498|||N||||||||N
PV1|1|O|RAD^PET1^1^^^VUMC||||1372984^DESAI^PRIYA^M^^^MD||||||||||||OP|VN729184302|||||||||||||||||||||||||20260322080000
PV2|||^PET CT WHOLE BODY|||||||||||||||||||||||||||||||20260322090000
IN1|1|MEDICARE_A^MEDICARE|CMS001|MEDICARE|7500 SECURITY BLVD^^BALTIMORE^MD^21244|||||||20260101|20261231|||IND|CALDWELL^EARL^VINCENT|SELF|19580412|2904 WOODMONT BLVD^^NASHVILLE^TN^37215^US|||||||||||||||1EG4-TE5-MK72||||||||||M
AL1|1|DA|IODINE^IODINATED CONTRAST|SEV|ANAPHYLAXIS|20210315
AL1|2|DA|PENICILLIN^PENICILLIN|MOD|RASH|20180101
```

---

## 12. ORU^R01 - PET-CT whole body final report

```
MSH|^~\&|POWERSCRIBE|VUMC_RAD^1943827650^NPI|EPIC|VUMC_HIS|20260322153847||ORU^R01^ORU_R01|MSG20260322153847012|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN7291843^^^VUMC^MR||CALDWELL^EARL^VINCENT||19580412|M|||2904 WOODMONT BLVD^^NASHVILLE^TN^37215^US||^PRN^PH^^1^615^4427831|||||531-76-4498
PV1|1|O|RAD^PET1^1^^^VUMC||||1504829^VENKATESH^ARUN^S^^^MD|1504829^VENKATESH^ARUN^S^^^MD|||RAD||||||||OP|VN729184302|||||||||||||||||||||||||20260322080000
ORC|RE|ORD6129834^EPIC|RAD20260322012^POWERSCRIBE||CM||||20260322090000|||1504829^VENKATESH^ARUN^S^^^MD
OBR|1|ORD6129834^EPIC|RAD20260322012^POWERSCRIBE|78816^PET CT WHOLE BODY^CPT4|||20260322100000||||||||1504829^VENKATESH^ARUN^S^^^MD||||||20260322153800|||F|||||||1504829^VENKATESH^ARUN^S^^^MD
OBX|1|FT|GDT^REPORT TEXT^L||EXAMINATION: PET/CT Whole Body with 18F-FDG\.br\\.br\CLINICAL INDICATION: Known 1.8 cm spiculated right upper lobe nodule. Staging.\.br\\.br\COMPARISON: CT Chest dated 2026-03-14.\.br\\.br\TECHNIQUE: 12.1 mCi F-18 FDG administered IV. Blood glucose 102 mg/dL prior to injection. Uptake time 62 minutes. Low-dose CT for attenuation correction and anatomic correlation from vertex to mid-thighs.\.br\\.br\FINDINGS:\.br\HEAD AND NECK: No hypermetabolic lesions. Normal physiologic brain FDG uptake.\.br\CHEST: Intensely FDG-avid right upper lobe spiculated mass measuring 2.0 x 1.5 cm with SUVmax 12.4. FDG-avid right pretracheal lymph node (station 4R, 1.4 cm, SUVmax 6.8). FDG-avid subcarinal lymph node (station 7, 1.2 cm, SUVmax 5.1). No contralateral mediastinal or hilar adenopathy. Left lower lobe 4 mm ground-glass nodule is below PET resolution.\.br\ABDOMEN AND PELVIS: No FDG-avid hepatic lesions. Normal splenic and renal uptake. No retroperitoneal or pelvic lymphadenopathy. Normal bowel activity.\.br\MUSCULOSKELETAL: No FDG-avid osseous lesions. Degenerative changes noted.\.br\\.br\IMPRESSION:\.br\1. Intensely FDG-avid right upper lobe mass (SUVmax 12.4) consistent with primary lung malignancy, likely NSCLC.\.br\2. Ipsilateral mediastinal nodal metastases (stations 4R and 7). Stage IIIA (T1c N2 M0) by imaging.\.br\3. No distant metastatic disease identified.\.br\4. Recommend pulmonology referral for tissue diagnosis and multidisciplinary tumor board.||||||F|||20260322153800
OBX|2|NM|SUVMAX^MAXIMUM SUV PRIMARY^L||12.4|{SUV}|||||F
OBX|3|ST|STAGE^CLINICAL STAGE^L||IIIA (T1c N2 M0)||||||F
```

---

## 13. MDM^T02 - Radiology peer review communication

```
MSH|^~\&|NUANCE_PS|ERLANGER_RAD^3192847560^NPI|EPIC|ERLANGER_HIS|20260323084512||MDM^T02^MDM_T02|MSG20260323084512013|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|T02|20260323084512
PID|1||MRN3819274^^^ERLANGER^MR||BOWMAN^TERRENCE^DALE||19610718|M|||1427 MARKET ST^^CHATTANOOGA^TN^37402^US||^PRN^PH^^1^423^9917234|||||342-18-7796
PV1|1|I|ICU^BED08^1^^^ERLANGER||||1647382^NORRIS^KEITH^D^^^MD||||||||||||IP|VN381927400|||||||||||||||||||||||||20260322180000
TXA|1|RAD^PEER REVIEW|FT|20260323084500|1293147^TUCKER^MELANIE^A^^^MD||20260323084512|||||DOC99123478||||||AU
OBX|1|FT|GDT^PEER REVIEW NOTE^L||RADPEER SCORE: 2a (Diagnosis not made but understandable miss)\.br\\.br\ORIGINAL STUDY: CT Abdomen Pelvis (03/22/2026, read by Dr. Norris)\.br\REVIEWED BY: Dr. Melanie Tucker\.br\\.br\FINDING: A 1.2 cm hypodense lesion in the right adrenal gland was present on the original study (series 3, image 142) but not mentioned in the report. On subsequent MRI performed for worsening abdominal pain, this was confirmed as an adrenal adenoma based on chemical shift imaging. While clinically insignificant, it should have been documented.\.br\\.br\CLASSIFICATION: Minor discrepancy - unlikely to affect patient management.\.br\PEER LEARNING CASE: Submitted for departmental case conference 04/2026.||||||F|||20260323084500
```

---

## 14. ORU^R01 - Fluoroscopy upper GI series report

```
MSH|^~\&|PSCRIBE360|TRISTAR_RAD^4021938475^NPI|EPIC|TRISTAR_HIS|20260323143256||ORU^R01^ORU_R01|MSG20260323143256014|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN5729381^^^TRISTAR^MR||RAMSEY^WANDA^LUCILLE||19550829|F|||2814 NOLENSVILLE PIKE^^NASHVILLE^TN^37211^US||^PRN^PH^^1^615^8817243|||||214-57-3348
PV1|1|O|RAD^FLUORO1^1^^^TRISTAR||||1862493^CRAWFORD^DENNIS^P^^^MD|1862493^CRAWFORD^DENNIS^P^^^MD|||RAD||||||||OP|VN572938100|||||||||||||||||||||||||20260323130000
ORC|RE|ORD8374129^EPIC|RAD20260323014^PSCRIBE360||CM||||20260323130000|||1862493^CRAWFORD^DENNIS^P^^^MD
OBR|1|ORD8374129^EPIC|RAD20260323014^PSCRIBE360|74246^UPPER GI SERIES WITH KUB^CPT4|||20260323133000||||||||1862493^CRAWFORD^DENNIS^P^^^MD||||||20260323143200|||F|||||||1862493^CRAWFORD^DENNIS^P^^^MD
OBX|1|FT|GDT^REPORT TEXT^L||EXAMINATION: Upper GI Series with Small Bowel Follow-Through\.br\\.br\CLINICAL INDICATION: 70-year-old female with epigastric pain, early satiety, 15-pound weight loss over 3 months.\.br\\.br\COMPARISON: None available.\.br\\.br\TECHNIQUE: Single and double contrast upper GI examination performed with barium and effervescent granules. Spot images obtained. Small bowel follow-through with serial images at 15-minute intervals.\.br\\.br\FINDINGS:\.br\ESOPHAGUS: Normal peristalsis. No stricture, mass, or mucosal irregularity. GE junction is normally located.\.br\STOMACH: There is an irregular filling defect along the lesser curvature of the gastric antrum measuring approximately 3.5 x 2.5 cm. The lesion demonstrates mucosal destruction with shouldered margins. Proximal gastric folds are thickened.\.br\DUODENUM: Normal duodenal bulb and sweep. No mass or ulceration.\.br\SMALL BOWEL: Barium reaches the cecum at 45 minutes. Normal fold pattern. No stricture, mass, or obstruction.\.br\\.br\IMPRESSION:\.br\1. Irregular antral mass with mucosal destruction along the lesser curvature, highly suspicious for gastric carcinoma. Endoscopy with biopsy recommended urgently.\.br\2. Normal small bowel follow-through.||||||F|||20260323143200
```

---

## 15. ORM^O01 - CT angiography chest order for PE protocol

```
MSH|^~\&|MEDITECH|BMHCC_HIS^2847193056^NPI|POWERSCRIBE|BMHCC_RAD|20260324022145||ORM^O01^ORM_O01|MSG20260324022145015|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN9274183^^^BMHCC^MR||TATE^DARNELL^JEROME||19881104|M|||1578 LAMAR AVE^^MEMPHIS^TN^38114^US||^PRN^PH^^1^901^4483291|||||456-71-2938
PV1|1|E|ED^BED22^1^^^BMHCC||||1741923^ROGERS^VANESSA^T^^^MD||||||||||||EN|VN927418300|||||||||||||||||||||||||20260324020000
ORC|NW|ORD7218394^MEDITECH|RAD20260324015^POWERSCRIBE|STAT|SC||||20260324022100|||1741923^ROGERS^VANESSA^T^^^MD
OBR|1|ORD7218394^MEDITECH|RAD20260324015^POWERSCRIBE|71275^CTA CHEST PE PROTOCOL^CPT4|STAT||20260324022100||||||ACUTE DYSPNEA, TACHYCARDIA 118, SPO2 89% ON RA. D-DIMER >5000. RECENT 14-HR FLIGHT FROM TOKYO. WELLS SCORE 7.5|||||||||||||||||1741923^ROGERS^VANESSA^T^^^MD
```

---

## 16. ORU^R01 - CT angiography chest PE protocol final report

```
MSH|^~\&|POWERSCRIBE|BMHCC_RAD^2847193056^NPI|MEDITECH|BMHCC_HIS|20260324031234||ORU^R01^ORU_R01|MSG20260324031234016|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN9274183^^^BMHCC^MR||TATE^DARNELL^JEROME||19881104|M|||1578 LAMAR AVE^^MEMPHIS^TN^38114^US||^PRN^PH^^1^901^4483291|||||456-71-2938
PV1|1|E|ED^BED22^1^^^BMHCC||||1741923^ROGERS^VANESSA^T^^^MD|1584321^OKAFOR^NELSON^E^^^MD|||RAD||||||||EN|VN927418300|||||||||||||||||||||||||20260324020000
ORC|RE|ORD7218394^MEDITECH|RAD20260324015^POWERSCRIBE||CM||||20260324022100|||1584321^OKAFOR^NELSON^E^^^MD
OBR|1|ORD7218394^MEDITECH|RAD20260324015^POWERSCRIBE|71275^CTA CHEST PE PROTOCOL^CPT4|||20260324023000||||||||1584321^OKAFOR^NELSON^E^^^MD||||||20260324031200|||F|||||||1584321^OKAFOR^NELSON^E^^^MD
OBX|1|FT|GDT^REPORT TEXT^L||EXAMINATION: CT Angiography Chest - PE Protocol\.br\\.br\CLINICAL INDICATION: 37-year-old male with acute dyspnea, tachycardia, hypoxia, elevated D-dimer, recent long-haul flight. High clinical suspicion for PE.\.br\\.br\COMPARISON: None.\.br\\.br\TECHNIQUE: CT pulmonary angiography performed with 75 mL Omnipaque 350 using bolus tracking with ROI in the main pulmonary artery.\.br\\.br\FINDINGS:\.br\PULMONARY ARTERIES: Saddle embolus identified straddling the main pulmonary artery bifurcation. Extensive bilateral pulmonary emboli extending into the lobar, segmental, and subsegmental arteries of all lobes. Near-complete occlusion of the right lower lobe pulmonary artery.\.br\HEART: Right ventricle is dilated with RV/LV ratio of 1.4 (normal <1.0). Interventricular septum bowing toward the left ventricle consistent with right heart strain. Contrast reflux into the IVC and hepatic veins.\.br\LUNGS: Wedge-shaped peripheral opacities in the right lower lobe consistent with pulmonary infarction. Small bilateral pleural effusions.\.br\ADDITIONAL: No aortic dissection. No pericardial effusion.\.br\\.br\IMPRESSION:\.br\1. MASSIVE bilateral pulmonary embolism with saddle embolus. Right heart strain present. CRITICAL FINDING.\.br\2. Right lower lobe pulmonary infarction.\.br\3. Findings conveyed to Dr. Rogers at bedside at 03:08 on 03/24/2026.\.br\\.br\RECOMMENDATION: Consider thrombolysis or catheter-directed therapy given hemodynamic significance.||||||F|||20260324031200
OBX|2|ST|CRITICAL^CRITICAL RESULT^L||YES - MASSIVE PE WITH RV STRAIN||||||F
OBX|3|NM|RVLV^RV/LV RATIO^L||1.4||<1.0|HH|||F
```

---

## 17. ORU^R01 - MRI knee with encapsulated structured report (ED datatype)

```
MSH|^~\&|NUANCE_PS|METHODIST_RAD^6518293740^NPI|EPIC|METHODIST_HIS|20260325101834||ORU^R01^ORU_R01|MSG20260325101834017|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN6382917^^^METHODIST^MR||HOLLOWAY^MARCUS^TERRELL||19950512|M|||4209 COVINGTON PIKE^^MEMPHIS^TN^38128^US||^PRN^PH^^1^901^2219437|||||538-14-7723
PV1|1|O|RAD^MRI2^1^^^METHODIST||||1927384^AZIZ^SAMIRA^K^^^MD|1927384^AZIZ^SAMIRA^K^^^MD|||RAD||||||||OP|VN638291700|||||||||||||||||||||||||20260325090000
ORC|RE|ORD4917238^EPIC|RAD20260325017^NUANCE_PS||CM||||20260325090000|||1927384^AZIZ^SAMIRA^K^^^MD
OBR|1|ORD4917238^EPIC|RAD20260325017^NUANCE_PS|73721^MRI KNEE WITHOUT CONTRAST LEFT^CPT4|||20260325092000||||||||1927384^AZIZ^SAMIRA^K^^^MD||||||20260325101800|||F|||||||1927384^AZIZ^SAMIRA^K^^^MD
OBX|1|FT|GDT^REPORT TEXT^L||EXAMINATION: MRI Left Knee without Contrast\.br\\.br\CLINICAL INDICATION: 30-year-old male, basketball injury 2 weeks ago with persistent effusion and mechanical locking.\.br\\.br\COMPARISON: Knee radiographs dated 2026-03-11.\.br\\.br\TECHNIQUE: Multiplanar multisequence MRI of the left knee without contrast including proton density fat-sat, T1, T2, and gradient echo sequences.\.br\\.br\FINDINGS:\.br\MENISCI: Complex tear of the medial meniscus involving the posterior horn and body with a displaced bucket-handle fragment flipped into the intercondylar notch (double PCL sign on sagittal images). Lateral meniscus is intact.\.br\LIGAMENTS: ACL shows complete disruption with edema and fiber discontinuity. PCL is intact with normal signal. MCL shows grade II sprain with edema but intact fibers. LCL is intact.\.br\ARTICULAR CARTILAGE: Full-thickness cartilage defect over the weight-bearing surface of the medial femoral condyle measuring 1.2 x 0.8 cm. Bone marrow edema in the underlying subchondral bone. Lateral compartment cartilage is intact.\.br\BONE: Bone contusions in the posterolateral tibial plateau and mid-lateral femoral condyle (pivot-shift pattern). No fracture.\.br\EFFUSION: Large joint effusion.\.br\\.br\IMPRESSION:\.br\1. Complete ACL tear.\.br\2. Complex medial meniscus tear with displaced bucket-handle fragment.\.br\3. Full-thickness medial femoral condyle cartilage defect.\.br\4. MCL grade II sprain.\.br\5. Orthopedic surgical consultation recommended.||||||F|||20260325101800
OBX|2|ED|SR_RPT^STRUCTURED REPORT^L||^application^xml^Base64^PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHJhZGlvbG9neV9yZXBvcnQgeG1sbnM9Imh0dHA6Ly9udWFuY2UuY29tL3Bvd2Vyc2NyaWJlL3NyIiB2ZXJzaW9uPSIyLjAiPgogIDxwYXRpZW50PgogICAgPG1ybj42MzgyOTE3PC9tcm4+CiAgICA8bmFtZT5IT0xMT1dBWSwgTUFSQ1VTIFRFUlJFTEw8L25hbWU+CiAgICA8ZG9iPjE5OTUtMDUtMTI8L2RvYj4KICAgIDxzZXg+TTwvc2V4PgogIDwvcGF0aWVudD4KICA8c3R1ZHk+CiAgICA8YWNjZXNzaW9uPlJBRDIwMjYwMzI1MDE3PC9hY2Nlc3Npb24+CiAgICA8bW9kYWxpdHk+TVI8L21vZGFsaXR5PgogICAgPGJvZHlfcGFydD5MRUZUIE5FRUU8L2JvZHlfcGFydD4KICAgIDxwcm9jZWR1cmU+TVJJIE5lZSB3aXRob3V0IENvbnRyYXN0PC9wcm9jZWR1cmU+CiAgPC9zdHVkeT4KICA8ZmluZGluZ3M+CiAgICA8ZmluZGluZyBjYXRlZ29yeT0ibWVuaXNjdXMiIGxvY2F0aW9uPSJtZWRpYWwiIHNldmVyaXR5PSJzZXZlcmUiPgogICAgICA8ZGVzY3JpcHRpb24+Q29tcGxleCB0ZWFyIHdpdGggZGlzcGxhY2VkIGJ1Y2tldC1oYW5kbGUgZnJhZ21lbnQ8L2Rlc2NyaXB0aW9uPgogICAgICA8cmFkbGV4PlJJRDM0NTI8L3JhZGxleD4KICAgIDwvZmluZGluZz4KICAgIDxmaW5kaW5nIGNhdGVnb3J5PSJsaWdhbWVudCIgbG9jYXRpb249IkFDTCIgc2V2ZXJpdHk9ImNvbXBsZXRlIj4KICAgICAgPGRlc2NyaXB0aW9uPkNvbXBsZXRlIEFDTCB0ZWFyPC9kZXNjcmlwdGlvbj4KICAgICAgPHJhZGxleD5SSUQxMDQ4PC9yYWRsZXg+CiAgICA8L2ZpbmRpbmc+CiAgICA8ZmluZGluZyBjYXRlZ29yeT0iY2FydGlsYWdlIiBsb2NhdGlvbj0ibWVkaWFsX2ZlbW9yYWxfY29uZHlsZSIgc2V2ZXJpdHk9ImZ1bGxfdGhpY2tuZXNzIj4KICAgICAgPGRlc2NyaXB0aW9uPjEuMiB4IDAuOCBjbSBmdWxsLXRoaWNrbmVzcyBkZWZlY3Q8L2Rlc2NyaXB0aW9uPgogICAgICA8cmFkbGV4PlJJRDM0OTk8L3JhZGxleD4KICAgIDwvZmluZGluZz4KICA8L2ZpbmRpbmdzPgogIDxpbXByZXNzaW9uPgogICAgPGl0ZW0gcHJpb3JpdHk9IjEiPkNvbXBsZXRlIEFDTCB0ZWFyPC9pdGVtPgogICAgPGl0ZW0gcHJpb3JpdHk9IjIiPkNvbXBsZXggbWVkaWFsIG1lbmlzY3VzIHRlYXIgd2l0aCBkaXNwbGFjZWQgYnVja2V0LWhhbmRsZSBmcmFnbWVudDwvaXRlbT4KICAgIDxpdGVtIHByaW9yaXR5PSIzIj5GdWxsLXRoaWNrbmVzcyBtZWRpYWwgZmVtb3JhbCBjb25keWxlIGNhcnRpbGFnZSBkZWZlY3Q8L2l0ZW0+CiAgICA8aXRlbSBwcmlvcml0eT0iNCI+TUNMIGdyYWRlIElJIHNwcmFpbjwvaXRlbT4KICA8L2ltcHJlc3Npb24+CiAgPHJlY29tbWVuZGF0aW9uPk9ydGhvcGVkaWMgc3VyZ2ljYWwgY29uc3VsdGF0aW9uPC9yZWNvbW1lbmRhdGlvbj4KPC9yYWRpb2xvZ3lfcmVwb3J0Pgo=||||||F|||20260325101800
```

---

## 18. ADT^A04 - Patient registration for interventional radiology procedure

```
MSH|^~\&|CERNER|PARKWEST_HIS^5273849106^NPI|PSCRIBE360|PARKWEST_RAD|20260326060512||ADT^A04^ADT_A04|MSG20260326060512018|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A04|20260326060512
PID|1||MRN1748293^^^PARKWEST^MR||STANTON^CLIFFORD^WAYNE||19490606|M|||1017 N BROADWAY^^KNOXVILLE^TN^37917^US||^PRN^PH^^1^865^3384726||ENG|M|BAP|213-58-4471|||N||||||||N
PV1|1|O|IR^SUITE2^1^^^PARKWEST||||1738294^FIELDS^GREGORY^H^^^MD||||||||||||SDS|VN174829300|||||||||||||||||||||||||20260326060000
PV2|||^CT GUIDED LUNG BIOPSY|||||||||||||||||||||||||||||||20260326070000
NK1|1|STANTON^PATRICIA^FAYE|SPO|1017 N BROADWAY^^KNOXVILLE^TN^37917^US|^PRN^PH^^1^865^3384727
IN1|1|AETNA_TN^AETNA|91234|AETNA|151 FARMINGTON AVE^^HARTFORD^CT^06156|||||||20260101|20261231|||IND|STANTON^CLIFFORD^WAYNE|SELF|19490606|1017 N BROADWAY^^KNOXVILLE^TN^37917^US|||||||||||||||W338174829||||||||||M
```

---

## 19. ORU^R01 - CT-guided lung biopsy procedure report

```
MSH|^~\&|PSCRIBE360|PARKWEST_RAD^5273849106^NPI|CERNER|PARKWEST_HIS|20260326112345||ORU^R01^ORU_R01|MSG20260326112345019|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN1748293^^^PARKWEST^MR||STANTON^CLIFFORD^WAYNE||19490606|M|||1017 N BROADWAY^^KNOXVILLE^TN^37917^US||^PRN^PH^^1^865^3384726|||||213-58-4471
PV1|1|O|IR^SUITE2^1^^^PARKWEST||||1738294^FIELDS^GREGORY^H^^^MD|1738294^FIELDS^GREGORY^H^^^MD|||RAD||||||||SDS|VN174829300|||||||||||||||||||||||||20260326060000
ORC|RE|ORD2918374^CERNER|RAD20260326019^PSCRIBE360||CM||||20260326070000|||1738294^FIELDS^GREGORY^H^^^MD
OBR|1|ORD2918374^CERNER|RAD20260326019^PSCRIBE360|32405^CT GUIDED LUNG BIOPSY^CPT4|||20260326080000||||||||1738294^FIELDS^GREGORY^H^^^MD||||||20260326112300|||F|||||||1738294^FIELDS^GREGORY^H^^^MD
OBX|1|FT|GDT^REPORT TEXT^L||EXAMINATION: CT-Guided Percutaneous Lung Biopsy\.br\\.br\CLINICAL INDICATION: 76-year-old male with 2.8 cm right upper lobe spiculated mass identified on CT 2026-03-10. PET-CT showed SUVmax 9.2. Tissue diagnosis needed.\.br\\.br\PROCEDURE:\.br\INFORMED CONSENT: Risks including pneumothorax, hemorrhage, infection, and need for chest tube discussed. Written consent obtained.\.br\PATIENT POSITION: Prone.\.br\TECHNIQUE: Planning CT performed. The right upper lobe mass was targeted via a posterior approach. Following local anesthesia with 10 mL 1% lidocaine, a 19-gauge introducer needle was advanced into the lesion under intermittent CT fluoroscopy. Coaxial technique used with 20-gauge core biopsy needle (Temno). Four core samples obtained and sent to pathology. Additional fine needle aspiration performed with 22-gauge needle - cytology technician confirmed adequate cellularity on-site.\.br\COMPLICATIONS: Small anterior pneumothorax noted on immediate post-procedure CT measuring approximately 10% in volume. Patient asymptomatic with SpO2 97% on room air.\.br\POST-PROCEDURE: Upright PA chest radiograph at 2 hours showed stable small pneumothorax. No chest tube required. Patient discharged home with pneumothorax precautions at 11:15.\.br\\.br\SPECIMENS:\.br\1. Four 20-gauge core biopsies to surgical pathology.\.br\2. FNA slides to cytopathology (adequate per on-site review).\.br\\.br\IMPRESSION:\.br\1. Technically successful CT-guided biopsy of right upper lobe mass.\.br\2. Small stable pneumothorax, no intervention required.\.br\3. Pathology results pending.||||||F|||20260326112300
OBX|2|ST|COMPLICATION^PROCEDURE COMPLICATION^L||SMALL PNEUMOTHORAX - NO INTERVENTION||||||F
OBX|3|NM|FLUORO_DOSE^CT FLUOROSCOPY DOSE^L||847|mGy*cm|||||F
```

---

## 20. MDM^T02 - Final radiology report for nuclear medicine bone scan

```
MSH|^~\&|POWERSCRIBE|TRISTAR_RAD^4021938475^NPI|EPIC|TRISTAR_HIS|20260327161234||MDM^T02^MDM_T02|MSG20260327161234020|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|T02|20260327161234
PID|1||MRN3829174^^^TRISTAR^MR||BUCKNER^SHIRLEY^ELOISE||19470222|F|||1203 HARDING PIKE^^NASHVILLE^TN^37205^US||^PRN^PH^^1^615^9918472|||||178-34-6215
PV1|1|O|RAD^NM1^1^^^TRISTAR||||1862493^CRAWFORD^DENNIS^P^^^MD|1862493^CRAWFORD^DENNIS^P^^^MD|||RAD||||||||OP|VN382917400|||||||||||||||||||||||||20260327080000
TXA|1|RAD^RADIOLOGY REPORT|FT|20260327161200|1862493^CRAWFORD^DENNIS^P^^^MD||20260327161234|||||DOC11234587||||||AU
OBX|1|FT|GDT^REPORT TEXT^L||EXAMINATION: Whole Body Bone Scan (Tc-99m MDP)\.br\\.br\CLINICAL INDICATION: 79-year-old female with newly diagnosed invasive ductal carcinoma of the left breast (ER+/PR+/HER2-). Staging evaluation for osseous metastases.\.br\\.br\COMPARISON: None.\.br\\.br\TECHNIQUE: Whole body anterior and posterior planar images obtained 3 hours after IV administration of 25 mCi Tc-99m MDP. Spot views of the pelvis obtained.\.br\\.br\FINDINGS:\.br\SKULL: Normal calvarial uptake. No focal lesions.\.br\SPINE: Degenerative uptake at multiple levels of the thoracic and lumbar spine. Focal increased uptake at T8 vertebral body is suspicious and not clearly degenerative in pattern.\.br\CHEST: Increased uptake at the left 6th and 7th costochondral junctions - likely degenerative but cannot exclude metastatic disease in this clinical setting.\.br\PELVIS: Mildly increased uptake in the right sacroiliac joint, likely degenerative.\.br\EXTREMITIES: Bilateral knee uptake consistent with osteoarthritis. No suspicious long bone lesions.\.br\KIDNEYS: Symmetric renal uptake and excretion.\.br\\.br\IMPRESSION:\.br\1. Suspicious focal uptake at T8 vertebral body - recommend MRI of the thoracic spine for further evaluation to exclude osseous metastasis.\.br\2. Probable degenerative uptake at costochondral junctions and sacroiliac joint, though metastatic disease cannot be entirely excluded in this clinical context.\.br\3. No definite widespread osseous metastatic disease.||||||F|||20260327161200
OBX|2|NM|DOSE^ADMINISTERED DOSE^L||25.2|mCi|||||F
OBX|3|ST|RADPHARM^RADIOPHARMACEUTICAL^L||Tc-99m MDP||||||F
```
