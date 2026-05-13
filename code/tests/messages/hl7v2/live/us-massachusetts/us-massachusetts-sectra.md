# Sectra PACS/RIS - real HL7v2 ER7 messages

---

## 1. ORM^O01 - CT scan order received

```
MSH|^~\&|EHR_SYS|MASSGENBRIGHAM|SECTRA_RIS|MGB_RAD|20250310091500||ORM^O01|SEC20250310091500001|P|2.4
PID|1||MGB0044782^^^MGB^MR||CALLAHAN^BRENDA^J||19580214|F|||42 Beacon St^^Boston^MA^02108||617-555-0142
PV1|1|I|4N^^412^MGB||||2839471^RIZZO^ANTHONY^L^^^MD
ORC|NW|EHR-ORD-10234||SEC-ACC-20250310-001|IP||||20250310091400|||2839471^RIZZO^ANTHONY^L^^^MD
OBR|1|EHR-ORD-10234|SEC-ACC-20250310-001|71260^CT Chest with Contrast^L|||20250310091400|||||||20250310091400||2839471^RIZZO^ANTHONY^L^^^MD|||||||STAT
NTE|1||Clinical indication: 72F with fever, cough, hypoxia. R/O PE.
```

---

## 2. ORM^O01 - MRI brain order

```
MSH|^~\&|EHR_SYS|BIDMC|SECTRA_RIS|BIDMC_RAD|20250312142200||ORM^O01|SEC20250312142200002|P|2.4
PID|1||BIDMC0034567^^^BIDMC^MR||KESSLER^DIANE^R||19710328|F|||330 Brookline Ave^^Brookline^MA^02445||617-555-0812
PV1|1|O|NEUR^^301^BIDMC||||4718236^OSTROWSKI^HELEN^C^^^MD
ORC|NW|EHR-ORD-20345||SEC-ACC-20250312-002|IP||||20250312142100|||4718236^OSTROWSKI^HELEN^C^^^MD
OBR|1|EHR-ORD-20345|SEC-ACC-20250312-002|70553^MRI Brain with and without Contrast^L|||20250312142100|||||||20250312142100||4718236^OSTROWSKI^HELEN^C^^^MD|||||||ROUTINE
NTE|1||Clinical indication: New onset seizures. Evaluate for mass lesion.
```

---

## 3. ORU^R01 - CT chest result with findings

```
MSH|^~\&|SECTRA_RIS|MGB_RAD|EHR_SYS|MASSGENBRIGHAM|20250310120000||ORU^R01|SEC20250310120000003|P|2.4
PID|1||MGB0044782^^^MGB^MR||CALLAHAN^BRENDA^J||19580214|F|||42 Beacon St^^Boston^MA^02108||617-555-0142
ORC|RE|EHR-ORD-10234|SEC-ACC-20250310-001||CM
OBR|1|EHR-ORD-10234|SEC-ACC-20250310-001|71260^CT Chest with Contrast^L|||20250310091400|||||||20250310110000||2839471^RIZZO^ANTHONY^L^^^MD||ACC20250310001||||20250310115900|||F|||RAD001^DASGUPTA^NEIL^P^^^MD
OBX|1|FT|71260^CT Chest Findings^LN||TECHNIQUE: CT chest with IV contrast. 100mL Omnipaque 350.\.br\\.br\FINDINGS:\.br\Heart: Normal size. No pericardial effusion.\.br\Vessels: No pulmonary embolism identified. Aorta normal caliber.\.br\Lungs: Bilateral lower lobe consolidation with air bronchograms, left greater than right. Small bilateral pleural effusions.\.br\Mediastinum: Several subcentimeter mediastinal lymph nodes, largest 8mm, nonspecific.\.br\Osseous: Degenerative changes thoracic spine. No acute fracture.||||||F
OBX|2|FT|71260^CT Chest Impression^LN||IMPRESSION:\.br\1. Bilateral lower lobe pneumonia, left greater than right.\.br\2. Small bilateral pleural effusions.\.br\3. No pulmonary embolism.||||||F
```

---

## 4. ORU^R01 - Mammography result

```
MSH|^~\&|SECTRA_RIS|BIDMC_RAD|EHR_SYS|BIDMC|20250314161500||ORU^R01|SEC20250314161500004|P|2.4
PID|1||BIDMC0056789^^^BIDMC^MR||WHITFIELD^SANDRA^T||19890712|F|||55 Francis St^^Cambridge^MA^02139||857-555-0567
ORC|RE|EHR-ORD-30456|SEC-ACC-20250314-003||CM
OBR|1|EHR-ORD-30456|SEC-ACC-20250314-003|77067^Bilateral Screening Mammogram^L|||20250314140000|||||||20250314155000||5923147^PORTER^VALERIE^K^^^MD||ACC20250314003||||20250314161400|||F|||RAD002^TAVARES^IRENE^M^^^MD
OBX|1|FT|77067^Mammography Findings^LN||TECHNIQUE: Standard CC and MLO views bilateral.\.br\\.br\BREAST COMPOSITION: Heterogeneously dense (ACR C).\.br\\.br\FINDINGS: No suspicious masses, calcifications, or architectural distortion identified bilaterally. No skin thickening or axillary lymphadenopathy.||||||F
OBX|2|FT|77067^Mammography Impression^LN||IMPRESSION: Negative. BI-RADS 1.\.br\Recommend routine screening in 1 year.||||||F
```

---

## 5. ORM^O01 - Ultrasound order

```
MSH|^~\&|EHR_SYS|TUFTSMEDICAL|SECTRA_RIS|TMC_RAD|20250316103000||ORM^O01|SEC20250316103000005|P|2.4
PID|1||TMC0023456^^^TMC^MR||DELANEY^MARCUS^W||19810923|M|||78 Harrison Ave^^Somerville^MA^02143||857-555-0456
PV1|1|O|GI^^201^TMC||||8341567^KWAN^JESSICA^A^^^MD
ORC|NW|EHR-ORD-40567||SEC-ACC-20250316-004|IP||||20250316102900|||8341567^KWAN^JESSICA^A^^^MD
OBR|1|EHR-ORD-40567|SEC-ACC-20250316-004|76700^US Abdomen Complete^L|||20250316102900|||||||20250316102900||8341567^KWAN^JESSICA^A^^^MD|||||||ROUTINE
NTE|1||Clinical indication: RUQ pain, elevated LFTs. R/O cholelithiasis.
```

---

## 6. ORU^R01 - MRI brain result with embedded PDF

```
MSH|^~\&|SECTRA_RIS|BIDMC_RAD|EHR_SYS|BIDMC|20250318163000||ORU^R01|SEC20250318163000006|P|2.4
PID|1||BIDMC0034567^^^BIDMC^MR||KESSLER^DIANE^R||19710328|F|||330 Brookline Ave^^Brookline^MA^02445||617-555-0812
ORC|RE|EHR-ORD-20345|SEC-ACC-20250312-002||CM
OBR|1|EHR-ORD-20345|SEC-ACC-20250312-002|70553^MRI Brain with and without Contrast^L|||20250312142100|||||||20250318150000||4718236^OSTROWSKI^HELEN^C^^^MD||ACC20250312002||||20250318162900|||F|||RAD003^FUENTES^RAYMOND^T^^^MD
OBX|1|FT|70553^MRI Brain Findings^LN||TECHNIQUE: MRI brain without and with gadolinium (15mL Gadavist).\.br\\.br\FINDINGS:\.br\No intracranial mass, hemorrhage, or acute infarction. Normal gray-white matter differentiation. Ventricles and sulci normal for age. No abnormal enhancement. Sellar/parasellar region normal. Posterior fossa unremarkable. No restricted diffusion.||||||F
OBX|2|FT|70553^MRI Brain Impression^LN||IMPRESSION: Normal MRI of the brain without evidence of mass lesion or other acute pathology.||||||F
OBX|3|ED|PDF^MRI Brain Report^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 7. ORU^R01 - Ultrasound abdomen result

```
MSH|^~\&|SECTRA_RIS|TMC_RAD|EHR_SYS|TUFTSMEDICAL|20250320140000||ORU^R01|SEC20250320140000007|P|2.4
PID|1||TMC0023456^^^TMC^MR||DELANEY^MARCUS^W||19810923|M|||78 Harrison Ave^^Somerville^MA^02143||857-555-0456
ORC|RE|EHR-ORD-40567|SEC-ACC-20250316-004||CM
OBR|1|EHR-ORD-40567|SEC-ACC-20250316-004|76700^US Abdomen Complete^L|||20250316102900|||||||20250320133000||8341567^KWAN^JESSICA^A^^^MD||ACC20250316004||||20250320135900|||F|||RAD004^GALLAGHER^MOIRA^C^^^MD
OBX|1|FT|76700^US Abdomen Findings^LN||LIVER: Normal size and echotexture. No focal lesion.\.br\GALLBLADDER: Multiple gallstones, largest 1.2 cm. No gallbladder wall thickening. No pericholecystic fluid. Positive sonographic Murphy sign.\.br\CBD: Normal caliber (4mm).\.br\PANCREAS: Normal.\.br\SPLEEN: Normal size (10 cm).\.br\KIDNEYS: Normal bilateral. No hydronephrosis. No stones.\.br\AORTA: Normal caliber.||||||F
OBX|2|FT|76700^US Abdomen Impression^LN||IMPRESSION:\.br\1. Cholelithiasis with positive sonographic Murphy sign, consistent with biliary colic.\.br\2. No cholecystitis (no wall thickening or pericholecystic fluid).\.br\3. Remainder of abdomen unremarkable.||||||F
```

---

## 8. ORM^O01 - Fluoroscopy order

```
MSH|^~\&|EHR_SYS|UMASSMEMORIAL|SECTRA_RIS|UMM_RAD|20250322090500||ORM^O01|SEC20250322090500008|P|2.4
PID|1||UMM0098321^^^UMM^MR||HENNESSEY^CRAIG^D||19720819|M|||115 Main St^^Worcester^MA^01608||508-555-0287
PV1|1|I|5E^^504^UMM||||6152987^AGRAWAL^PRIYA^S^^^MD
ORC|NW|EHR-ORD-50678||SEC-ACC-20250322-005|IP||||20250322090400|||6152987^AGRAWAL^PRIYA^S^^^MD
OBR|1|EHR-ORD-50678|SEC-ACC-20250322-005|74246^Upper GI with Small Bowel Follow Through^L|||20250322090400|||||||20250322090400||6152987^AGRAWAL^PRIYA^S^^^MD|||||||ROUTINE
NTE|1||Clinical indication: Abdominal pain, weight loss. Evaluate for obstruction or stricture.
```

---

## 9. ORU^R01 - X-ray result with critical finding

```
MSH|^~\&|SECTRA_RIS|BH_RAD|EHR_SYS|BAYSTATE_HEALTH|20250324154500||ORU^R01|SEC20250324154500009|P|2.4
PID|1||BH0076543^^^BH^MR||VELEZ^CARMEN^A||19650411|F|||890 State St^^Springfield^MA^01109||413-555-0398
ORC|RE|EHR-ORD-60789|SEC-ACC-20250324-006||CM
OBR|1|EHR-ORD-60789|SEC-ACC-20250324-006|71046^Chest XRay 2 Views^L|||20250324140000|||||||20250324150000||7293148^FLANAGAN^DEREK^J^^^MD||ACC20250324006||||20250324154400|||F|||RAD005^BANERJEE^VIKRAM^K^^^MD
OBX|1|FT|71046^Chest XRay Findings^LN||FINDINGS: Large left-sided pleural effusion with complete opacification of the left lower lobe and partial opacification of the left upper lobe. Mediastinal shift to the right. Right lung clear. Heart obscured by effusion.||||||F
OBX|2|FT|71046^Chest XRay Impression^LN||IMPRESSION: Large left pleural effusion with mass effect and rightward mediastinal shift. CRITICAL FINDING - Dr. Flanagan notified at 1547 by Dr. Banerjee.||||||F
NTE|1||CRITICAL FINDING COMMUNICATION: Large effusion with mediastinal shift. Dr. Flanagan notified verbally at 15:47. Read-back confirmed.
```

---

## 10. ORM^O01 - Nuclear medicine order

```
MSH|^~\&|EHR_SYS|LAHEY_BURLINGTON|SECTRA_RIS|LAH_RAD|20250326110000||ORM^O01|SEC20250326110000010|P|2.4
PID|1||LAH0019876^^^LAH^MR||BEAUMONT^THERESA^N||19770623|F|||200 Mall Rd^^Burlington^MA^01803||781-555-0287
PV1|1|O|ENDO^^201^LAH||||3647821^NOLAN^CYNTHIA^W^^^MD
ORC|NW|EHR-ORD-70890||SEC-ACC-20250326-007|IP||||20250326105900|||3647821^NOLAN^CYNTHIA^W^^^MD
OBR|1|EHR-ORD-70890|SEC-ACC-20250326-007|78014^Thyroid Uptake and Scan^L|||20250326105900|||||||20250326105900||3647821^NOLAN^CYNTHIA^W^^^MD|||||||ROUTINE
NTE|1||Clinical indication: Hyperthyroidism, low TSH. Determine etiology (Graves vs toxic nodule).
```

---

## 11. ORU^R01 - PET/CT result

```
MSH|^~\&|SECTRA_RIS|MGB_RAD|EHR_SYS|MASSGENBRIGHAM|20250328151500||ORU^R01|SEC20250328151500011|P|2.4
PID|1||MGB0061234^^^MGB^MR||KENNEY^LORRAINE^E||19630912|F|||88 Commonwealth Ave^^Newton^MA^02459||617-555-1023
ORC|RE|EHR-ORD-80901|SEC-ACC-20250328-008||CM
OBR|1|EHR-ORD-80901|SEC-ACC-20250328-008|78816^PET/CT Whole Body^L|||20250328090000|||||||20250328140000||9174532^HARRINGTON^ELEANOR^M^^^MD||ACC20250328008||||20250328151400|||F|||RAD006^TRAN^CHRISTOPHER^L^^^MD
OBX|1|FT|78816^PET/CT Findings^LN||TECHNIQUE: F-18 FDG PET/CT, skull base to mid-thigh. 12.5 mCi FDG administered IV. Blood glucose 98 mg/dL at injection.\.br\\.br\FINDINGS:\.br\Known left breast cancer, post-lumpectomy.\.br\No FDG-avid residual disease in the left breast surgical bed.\.br\No FDG-avid axillary, mediastinal, or hilar lymphadenopathy.\.br\No FDG-avid hepatic or osseous metastatic disease.\.br\Lungs clear without FDG-avid nodules.\.br\Physiologic FDG activity in brain, heart, kidneys, and bladder.||||||F
OBX|2|FT|78816^PET/CT Impression^LN||IMPRESSION:\.br\No evidence of FDG-avid metastatic disease. No residual disease at surgical site. Recommend continued surveillance per oncology protocol.||||||F
```

---

## 12. ORM^O01 - Interventional radiology procedure order

```
MSH|^~\&|EHR_SYS|BOSTONMEDCTR|SECTRA_RIS|BMC_RAD|20250330080000||ORM^O01|SEC20250330080000012|P|2.4
PID|1||BMC0087654^^^BMC^MR||CROWLEY^EVELYN^M||19490305|F|||201 Albany St^^Brockton^MA^02301||508-555-0521
PV1|1|I|MED3^^305^BMC||||4561298^MEDINA^CARLOS^E^^^MD
ORC|NW|EHR-ORD-90012||SEC-ACC-20250330-009|IP||||20250330075900|||4561298^MEDINA^CARLOS^E^^^MD
OBR|1|EHR-ORD-90012|SEC-ACC-20250330-009|75989^Thoracentesis under US guidance^L|||20250330075900|||||||20250330075900||4561298^MEDINA^CARLOS^E^^^MD|||||||URGENT
NTE|1||Left-sided pleural effusion. Therapeutic drainage requested. Patient on therapeutic anticoagulation held x48hrs. INR 1.2 today.
```

---

## 13. ORU^R01 - Bone density DEXA result

```
MSH|^~\&|SECTRA_RIS|LAH_RAD|EHR_SYS|LAHEY_BURLINGTON|20250401100000||ORU^R01|SEC20250401100000013|P|2.4
PID|1||LAH0024567^^^LAH^MR||SAVCHENKO^IRINA^V||19790311|F|||55 Cambridge Park Dr^^Cambridge^MA^02140||617-555-2001
ORC|RE|EHR-ORD-10123|SEC-ACC-20250401-010||CM
OBR|1|EHR-ORD-10123|SEC-ACC-20250401-010|77080^DEXA Bone Density^L|||20250401090000|||||||20250401095000||8265134^SHAH^RAVI^S^^^MD||ACC20250401010||||20250401095900|||F|||RAD004^GALLAGHER^MOIRA^C^^^MD
OBX|1|FT|77080^DEXA Findings^LN||LUMBAR SPINE (L1-L4): BMD 0.945 g/cm2, T-score -1.2\.br\TOTAL HIP LEFT: BMD 0.854 g/cm2, T-score -1.5\.br\FEMORAL NECK LEFT: BMD 0.780 g/cm2, T-score -1.8||||||F
OBX|2|FT|77080^DEXA Impression^LN||IMPRESSION: Osteopenia at the lumbar spine and left hip. FRAX 10-year major osteoporotic fracture risk: 12%. Recommend calcium/vitamin D supplementation and repeat in 2 years.||||||F
```

---

## 14. ORU^R01 - CT abdomen/pelvis result

```
MSH|^~\&|SECTRA_RIS|UMM_RAD|EHR_SYS|UMASSMEMORIAL|20250403140000||ORU^R01|SEC20250403140000014|P|2.4
PID|1||UMM0102876^^^UMM^MR||MAZUREK^JOLANTA^M||19930602|F|||45 Lincoln St^^Worcester^MA^01605||508-555-0744
ORC|RE|EHR-ORD-20234|SEC-ACC-20250403-011||CM
OBR|1|EHR-ORD-20234|SEC-ACC-20250403-011|74178^CT Abdomen Pelvis with Contrast^L|||20250403120000|||||||20250403133000||5739214^PRESCOTT^MARK^E^^^MD||ACC20250403011||||20250403135900|||F|||RAD001^DASGUPTA^NEIL^P^^^MD
OBX|1|FT|74178^CT Abdomen Findings^LN||TECHNIQUE: CT abdomen and pelvis with IV contrast.\.br\\.br\FINDINGS:\.br\Liver, spleen, pancreas, adrenals: Unremarkable.\.br\Kidneys: Normal bilateral. No stones or hydronephrosis.\.br\Appendix: Non-visualized, status post appendectomy.\.br\Bowel: Normal. No obstruction or wall thickening.\.br\Pelvis: Small amount of free fluid in cul-de-sac, likely physiologic.\.br\Lymph nodes: No significant lymphadenopathy.\.br\Osseous: No lytic or blastic lesion.||||||F
OBX|2|FT|74178^CT Abdomen Impression^LN||IMPRESSION: Unremarkable CT abdomen and pelvis. Physiologic pelvic free fluid.||||||F
```

---

## 15. ORM^O01 - Cardiac CT angiography order

```
MSH|^~\&|EHR_SYS|MASSGENBRIGHAM|SECTRA_RIS|MGB_RAD|20250405083000||ORM^O01|SEC20250405083000015|P|2.4
PID|1||MGB0072345^^^MGB^MR||DONAHUE^WALTER^F||19550118|M|||12 Revere St^^Quincy^MA^02169||617-555-1567
PV1|1|O|CARD^^201^MGB||||1578243^CAPOBIANCO^BRIAN^T^^^MD
ORC|NW|EHR-ORD-30345||SEC-ACC-20250405-012|IP||||20250405082900|||1578243^CAPOBIANCO^BRIAN^T^^^MD
OBR|1|EHR-ORD-30345|SEC-ACC-20250405-012|75574^Cardiac CTA^L|||20250405082900|||||||20250405082900||1578243^CAPOBIANCO^BRIAN^T^^^MD|||||||ROUTINE
NTE|1||Clinical indication: Atypical chest pain, intermediate pre-test probability CAD. Evaluate coronary arteries. HR <65, hold metoprolol.
```

---

## 16. ORU^R01 - Nuclear medicine thyroid scan result

```
MSH|^~\&|SECTRA_RIS|LAH_RAD|EHR_SYS|LAHEY_BURLINGTON|20250407142200||ORU^R01|SEC20250407142200016|P|2.4
PID|1||LAH0019876^^^LAH^MR||BEAUMONT^THERESA^N||19770623|F|||200 Mall Rd^^Burlington^MA^01803||781-555-0287
ORC|RE|EHR-ORD-70890|SEC-ACC-20250326-007||CM
OBR|1|EHR-ORD-70890|SEC-ACC-20250326-007|78014^Thyroid Uptake and Scan^L|||20250326105900|||||||20250407135000||3647821^NOLAN^CYNTHIA^W^^^MD||ACC20250326007||||20250407142100|||F|||RAD007^LOMBARDI^BENJAMIN^R^^^MD
OBX|1|FT|78014^Thyroid Scan Findings^LN||TECHNIQUE: 5 mCi I-123 administered orally. Uptake and imaging at 4 and 24 hours.\.br\\.br\FINDINGS:\.br\4-hour uptake: 22% (normal 5-15%)\.br\24-hour uptake: 48% (normal 15-35%)\.br\\.br\Imaging demonstrates diffusely enlarged thyroid with homogeneously increased uptake bilaterally. No focal hot or cold nodules. Pyramidal lobe visualized.||||||F
OBX|2|FT|78014^Thyroid Scan Impression^LN||IMPRESSION: Diffusely increased uptake consistent with Graves disease. No autonomous nodule identified.||||||F
```

---

## 17. ORU^R01 - Interventional procedure result with embedded PDF

```
MSH|^~\&|SECTRA_RIS|BMC_RAD|EHR_SYS|BOSTONMEDCTR|20250409160000||ORU^R01|SEC20250409160000017|P|2.4
PID|1||BMC0087654^^^BMC^MR||CROWLEY^EVELYN^M||19490305|F|||201 Albany St^^Brockton^MA^02301||508-555-0521
ORC|RE|EHR-ORD-90012|SEC-ACC-20250330-009||CM
OBR|1|EHR-ORD-90012|SEC-ACC-20250330-009|75989^Thoracentesis under US guidance^L|||20250330075900|||||||20250330110000||4561298^MEDINA^CARLOS^E^^^MD||ACC20250330009||||20250409155900|||F|||RAD008^CONNORS^PATRICK^M^^^MD
OBX|1|FT|75989^Procedure Report^LN||PROCEDURE: Left-sided ultrasound-guided thoracentesis.\.br\INDICATION: Symptomatic pleural effusion.\.br\TECHNIQUE: Under real-time US guidance, 18G needle inserted into left pleural space at 8th intercostal space, posterior axillary line. 1500 mL of straw-colored fluid drained. Specimen sent for cell count, chemistry, culture, cytology.\.br\COMPLICATIONS: None. Post-procedure CXR shows improved aeration with small residual effusion.||||||F
OBX|2|ED|PDF^Thoracentesis Procedure Report^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 18. ORM^O01 - Portable x-ray order from ICU

```
MSH|^~\&|EHR_SYS|TUFTSMEDICAL|SECTRA_RIS|TMC_RAD|20250411033000||ORM^O01|SEC20250411033000018|P|2.4
PID|1||TMC0029876^^^TMC^MR||RAHMAN^FATIMA^S||19860214|F|||45 Kneeland St^^Lowell^MA^01852||978-555-1345
PV1|1|I|MICU^^204^TMC||||2917438^BRENNAN^KEVIN^P^^^MD
ORC|NW|EHR-ORD-40456||SEC-ACC-20250411-013|IP||||20250411032900|||2917438^BRENNAN^KEVIN^P^^^MD
OBR|1|EHR-ORD-40456|SEC-ACC-20250411-013|71045^Chest XRay Portable^L|||20250411032900|||||||20250411032900||2917438^BRENNAN^KEVIN^P^^^MD|||||||STAT
NTE|1||Post-central line placement. Verify tip position. Patient intubated, sedated.
```

---

## 19. ORU^R01 - Portable chest x-ray result

```
MSH|^~\&|SECTRA_RIS|TMC_RAD|EHR_SYS|TUFTSMEDICAL|20250411042000||ORU^R01|SEC20250411042000019|P|2.4
PID|1||TMC0029876^^^TMC^MR||RAHMAN^FATIMA^S||19860214|F|||45 Kneeland St^^Lowell^MA^01852||978-555-1345
ORC|RE|EHR-ORD-40456|SEC-ACC-20250411-013||CM
OBR|1|EHR-ORD-40456|SEC-ACC-20250411-013|71045^Chest XRay Portable^L|||20250411032900|||||||20250411040000||2917438^BRENNAN^KEVIN^P^^^MD||ACC20250411013||||20250411041900|||F|||RAD009^ROSENTHAL^NADINE^J^^^MD
OBX|1|FT|71045^Portable CXR Findings^LN||FINDINGS: ET tube with tip 3.5 cm above the carina, satisfactory position. New right subclavian central venous catheter with tip in the SVC at the cavoatrial junction, satisfactory position. NG tube with tip in the stomach. Heart size normal. Lungs: Bibasilar atelectasis. No pneumothorax.||||||F
OBX|2|FT|71045^Portable CXR Impression^LN||IMPRESSION:\.br\1. Satisfactory position of ET tube, right subclavian central line, and NG tube.\.br\2. No pneumothorax.\.br\3. Bibasilar atelectasis.||||||F
```

---

## 20. ORU^R01 - CT angiography result with embedded PDF

```
MSH|^~\&|SECTRA_RIS|MGB_RAD|EHR_SYS|MASSGENBRIGHAM|20250413150000||ORU^R01|SEC20250413150000020|P|2.4
PID|1||MGB0072345^^^MGB^MR||DONAHUE^WALTER^F||19550118|M|||12 Revere St^^Quincy^MA^02169||617-555-1567
ORC|RE|EHR-ORD-30345|SEC-ACC-20250405-012||CM
OBR|1|EHR-ORD-30345|SEC-ACC-20250405-012|75574^Cardiac CTA^L|||20250405082900|||||||20250413140000||1578243^CAPOBIANCO^BRIAN^T^^^MD||ACC20250405012||||20250413145900|||F|||RAD001^DASGUPTA^NEIL^P^^^MD
OBX|1|FT|75574^Cardiac CTA Findings^LN||TECHNIQUE: ECG-gated CT coronary angiography. 80mL Omnipaque 350. HR 58 bpm.\.br\\.br\CALCIUM SCORE: 142 Agatston units (moderate).\.br\\.br\CORONARY ARTERIES:\.br\Left Main: Patent, no stenosis.\.br\LAD: Mild calcified plaque in proximal segment, <30% stenosis.\.br\LCx: Patent, no significant disease.\.br\RCA: Mixed plaque in mid-segment, approximately 40-50% stenosis.\.br\\.br\CARDIAC CHAMBERS: Normal size and function. EF estimated 60%.||||||F
OBX|2|FT|75574^Cardiac CTA Impression^LN||IMPRESSION:\.br\1. Moderate coronary calcium score (142).\.br\2. Mild LAD disease (<30%).\.br\3. Moderate RCA stenosis (40-50%). No hemodynamically significant stenosis.\.br\4. Normal LV function.||||||F
OBX|3|ED|PDF^Cardiac CTA Full Report^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```
