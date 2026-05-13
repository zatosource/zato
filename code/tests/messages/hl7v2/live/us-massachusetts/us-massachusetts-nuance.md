# Nuance PowerScribe - real HL7v2 ER7 messages

---

## 1. ORU^R01 - Chest X-ray report from MGH radiology

```
MSH|^~\&|POWERSCRIBE|MGH^5001^NPI|RAD_RECV|MGB_HIS|20250310143000||ORU^R01^ORU_R01|PS00001|P|2.4|||AL|NE
PID|1||MRN30012345^^^MGB^MR||Callahan^Derek^Anthony^^Mr.||19580214|M||2106-3^White^HL70005|91 Chestnut St^^Boston^MA^02108^US||^PRN^PH^^^617^5481923||M||VN30001234
PV1|1|I|MED^5W^A^MGH|||18273^Pearson^Gregory^T^MD^^NPI|||||||||IN||||||||||||||||||MGH||||20250308140000
ORC|RE|ORD10001|RAD20001||CM||||20250310143000|||29384^Kapoor^Vivek^S^MD^^NPI
OBR|1|ORD10001|RAD20001|71046^Chest X-Ray 2 Views^CPT|||20250310130000||||||||||29384^Kapoor^Vivek^S^MD^^NPI|||||20250310143000||RAD|F|||18273^Pearson^Gregory^T^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||CHEST X-RAY, 2 VIEWS~CLINICAL HISTORY: 66-year-old male with cough and fever.~COMPARISON: Chest X-ray dated 2025-02-15.~FINDINGS:~Heart size is mildly enlarged. Mediastinal contours are normal.~There is a new left lower lobe consolidation with air bronchograms.~Small left pleural effusion. Right lung is clear.~No pneumothorax.~IMPRESSION:~1. Left lower lobe pneumonia.~2. Small left pleural effusion.~3. Mild cardiomegaly, stable.||||||F|||20250310143000
OBX|2|TX|RAD_ADDENDUM^Addendum^L||||||||F
```

---

## 2. ORM^O01 - CT chest order received by PowerScribe from BWH

```
MSH|^~\&|EPIC|BWH^5002^NPI|POWERSCRIBE|BWH_RAD|20250312091500||ORM^O01^ORM_O01|PS00002|P|2.3|||AL|NE
PID|1||MRN40123456^^^MGB^MR||Whitfield^Rachel^Denise^^Mrs.||19710405|F||2106-3^White^HL70005|214 Commonwealth Ave^^Newton^MA^02459^US||^PRN^PH^^^857^6293741||M||VN40012345
PV1|1|O|PUL^CLINIC^A^BWH|||37491^Delgado^Carmen^E^MD^^NPI|||||||||OUT||||||||||||||||||BWH||||20250312083000
ORC|NW|ORD20002||||||^^^20250313080000^^R||20250312091500|||37491^Delgado^Carmen^E^MD^^NPI
OBR|1|ORD20002||71260^CT Chest with Contrast^CPT|||20250313080000||||||||37491^Delgado^Carmen^E^MD^^NPI|||||||||||1^^^20250313080000^^R
DG1|1||R91.1^Solitary pulmonary nodule^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||53 yo female with 12mm pulmonary nodule on prior CXR. Ex-smoker (20 pack-years, quit 2015). Follow-up imaging per Fleischner guidelines.||||||F
```

---

## 3. ORU^R01 - CT chest report with embedded PDF from BWH

```
MSH|^~\&|POWERSCRIBE|BWH^5002^NPI|RAD_RECV|MGB_HIS|20250313140000||ORU^R01^ORU_R01|PS00003|P|2.4|||AL|NE
PID|1||MRN40123456^^^MGB^MR||Whitfield^Rachel^Denise^^Mrs.||19710405|F||2106-3^White^HL70005|214 Commonwealth Ave^^Newton^MA^02459^US||^PRN^PH^^^857^6293741||M||VN40012345
PV1|1|O|PUL^CLINIC^A^BWH|||37491^Delgado^Carmen^E^MD^^NPI|||||||||OUT||||||||||||||||||BWH||||20250312083000
ORC|RE|ORD20002|RAD30002||CM||||20250313140000|||48562^Liang^Mei^R^MD^^NPI
OBR|1|ORD20002|RAD30002|71260^CT Chest with Contrast^CPT|||20250313083000||||||||||48562^Liang^Mei^R^MD^^NPI|||||20250313140000||RAD|F|||37491^Delgado^Carmen^E^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||CT CHEST WITH CONTRAST~CLINICAL HISTORY: Follow-up 12mm pulmonary nodule. Ex-smoker.~COMPARISON: Chest X-ray dated 2025-02-28.~TECHNIQUE: Helical CT of the chest with 80mL Omnipaque 350 IV contrast.~FINDINGS:~Right upper lobe: 14mm part-solid nodule (previously 12mm), with 8mm solid component.~Interval growth noted. No calcification or fat density.~No mediastinal or hilar lymphadenopathy.~No pleural effusion. Heart and great vessels normal.~Visualized upper abdomen unremarkable.~IMPRESSION:~1. Growing part-solid nodule in right upper lobe, now 14mm with 8mm solid component.~High suspicion for malignancy (Lung-RADS 4B).~2. Recommend PET-CT and tissue sampling.||||||F|||20250313140000
OBX|2|ED|RAD_PDF^Radiology Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 4. ORU^R01 - MRI brain report from BIDMC radiology

```
MSH|^~\&|POWERSCRIBE|BIDMC^5003^NPI|RAD_RECV|BIDMC_HIS|20250315161500||ORU^R01^ORU_R01|PS00004|P|2.4|||AL|NE
PID|1||MRN50234567^^^BIDMC^MR||Tran^Roger^Binh^^Mr.||19690818|M||2028-9^Asian^HL70005|47 Lancaster Terr^^Brookline^MA^02446^US||^PRN^PH^^^617^8324567||M||VN50023456
PV1|1|O|NEUR^CLINIC^A^BIDMC|||59124^Kowalczyk^Stefan^D^MD^^NPI|||||||||OUT||||||||||||||||||BIDMC||||20250315140000
ORC|RE|ORD30004|RAD40004||CM||||20250315161500|||63278^Hargrove^Timothy^J^MD^^NPI
OBR|1|ORD30004|RAD40004|70553^MRI Brain with and without Contrast^CPT|||20250315143000||||||||||63278^Hargrove^Timothy^J^MD^^NPI|||||20250315161500||RAD|F|||59124^Kowalczyk^Stefan^D^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||MRI BRAIN WITH AND WITHOUT CONTRAST~CLINICAL HISTORY: 55-year-old male with new onset seizures.~COMPARISON: None.~TECHNIQUE: Multiplanar multisequence MRI of the brain without and with 15mL Gadavist IV.~FINDINGS:~There is a 2.3 x 1.8 cm heterogeneously enhancing mass in the left temporal lobe~with surrounding vasogenic edema and mild mass effect on the left lateral ventricle.~No midline shift. No hemorrhage.~The remainder of the brain parenchyma is normal.~No restricted diffusion. Major intracranial vessels patent.~IMPRESSION:~1. Left temporal lobe enhancing mass (2.3 cm), concerning for primary brain neoplasm~or solitary metastasis. Recommend neurosurgery consultation for biopsy.~2. Surrounding edema with mild mass effect but no herniation.||||||F|||20250315161500
```

---

## 5. ORM^O01 - Ultrasound order received by PowerScribe from Baystate

```
MSH|^~\&|MEDITECH|BAYS^5004^NPI|POWERSCRIBE|BAYS_RAD|20250317090000||ORM^O01^ORM_O01|PS00005|P|2.3|||AL|NE
PID|1||BAY60345678^^^BAYS^MR||Novak^Brenda^Louise^^Mrs.||19800922|F||2106-3^White^HL70005|312 Worthington St^^Springfield^MA^01103^US||^PRN^PH^^^413^7829134||M||VN60034567
PV1|1|O|OB^CLINIC^A^BAYS|||71845^Cardenas^Lucia^M^MD^^NPI|||||||||OUT||||||||||||||||||BAYS||||20250317083000
ORC|NW|ORD40005||||||^^^20250318080000^^R||20250317090000|||71845^Cardenas^Lucia^M^MD^^NPI
OBR|1|ORD40005||76817^Transvaginal Ultrasound^CPT|||20250318080000||||||||71845^Cardenas^Lucia^M^MD^^NPI|||||||||||1^^^20250318080000^^R
DG1|1||N92.0^Excessive and frequent menstruation with regular cycle^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||44 yo female with menorrhagia and pelvic pressure. Prior US 6 months ago showed small fibroids.||||||F
```

---

## 6. ORU^R01 - Abdominal CT report from Baystate Health

```
MSH|^~\&|POWERSCRIBE|BAYS^5004^NPI|RAD_RECV|BAYS_HIS|20250319103000||ORU^R01^ORU_R01|PS00006|P|2.4|||AL|NE
PID|1||BAY70456789^^^BAYS^MR||Pelletier^Wayne^Douglas^^Mr.||19620730|M||2106-3^White^HL70005|145 Chestnut St^^Springfield^MA^01104^US||^PRN^PH^^^413^5928471||M||VN70045678
PV1|1|E|ED^BED06^A^BAYS|||82319^Harrington^Nolan^B^MD^^NPI|||||||||ER||||||||||||||||||BAYS||||20250319080000
ORC|RE|ORD50006|RAD60006||CM||||20250319103000|||94527^Desai^Ritu^N^MD^^NPI
OBR|1|ORD50006|RAD60006|74178^CT Abdomen and Pelvis with Contrast^CPT|||20250319090000||||||||||94527^Desai^Ritu^N^MD^^NPI|||||20250319103000||RAD|F|||82319^Harrington^Nolan^B^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||CT ABDOMEN AND PELVIS WITH CONTRAST~CLINICAL HISTORY: 62-year-old male with acute RLQ pain and elevated WBC.~COMPARISON: None available.~TECHNIQUE: Helical CT with 100mL Omnipaque 350 IV contrast.~FINDINGS:~ABDOMEN: Liver, spleen, pancreas, and adrenal glands are normal.~Kidneys enhance symmetrically without hydronephrosis.~No free fluid.~PELVIS: The appendix is dilated to 13mm with periappendiceal fat stranding~and a 7mm appendicolith. No abscess or perforation.~Small amount of free fluid in the pelvis.~Bladder and prostate are normal.~IMPRESSION:~1. Acute appendicitis with appendicolith. No perforation or abscess.~2. Surgical consultation recommended.||||||F|||20250319103000
```

---

## 7. ORU^R01 - Mammography report from MGH radiology

```
MSH|^~\&|POWERSCRIBE|MGH^5001^NPI|RAD_RECV|MGB_HIS|20250321110000||ORU^R01^ORU_R01|PS00007|P|2.4|||AL|NE
PID|1||MRN80567890^^^MGB^MR||Driscoll^Fiona^Margaret^^Mrs.||19650318|F||2106-3^White^HL70005|72 Myrtle St^^Boston^MA^02114^US||^PRN^PH^^^617^4381256||M||VN80056789
PV1|1|O|BRST^SCREEN^A^MGH|||15482^Acharya^Sunita^L^MD^^NPI|||||||||OUT||||||||||||||||||MGH||||20250321090000
ORC|RE|ORD60007|RAD70007||CM||||20250321110000|||26593^Ostrowski^Marta^F^MD^^NPI
OBR|1|ORD60007|RAD70007|77067^Bilateral Screening Mammogram^CPT|||20250321093000||||||||||26593^Ostrowski^Marta^F^MD^^NPI|||||20250321110000||RAD|F|||15482^Acharya^Sunita^L^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||BILATERAL SCREENING MAMMOGRAM~CLINICAL HISTORY: 59-year-old female, annual screening. No symptoms.~COMPARISON: Mammogram dated 2024-03-15.~BREAST COMPOSITION: Heterogeneously dense (Category C).~FINDINGS:~RIGHT BREAST: A new 8mm irregular mass with spiculated margins in the~upper outer quadrant at 10 o'clock position, middle third depth.~Not present on prior examination.~LEFT BREAST: Stable scattered benign-appearing calcifications. No mass or distortion.~IMPRESSION:~RIGHT BREAST: New suspicious spiculated mass.~BI-RADS 0 - Incomplete. Recommend diagnostic mammogram with spot compression~and targeted ultrasound of right breast.||||||F|||20250321110000
```

---

## 8. ORM^O01 - PET-CT order received by PowerScribe from Dana-Farber

```
MSH|^~\&|EPIC|DFCI^5005^NPI|POWERSCRIBE|DFCI_RAD|20250323081000||ORM^O01^ORM_O01|PS00008|P|2.4|||AL|NE
PID|1||MRN90678901^^^DFCI^MR||Hwang^Ji-Yeon^Allison^^Ms.||19720612|F||2028-9^Asian^HL70005|58 Brattle St^^Cambridge^MA^02138^US||^PRN^PH^^^617^7294583||S||VN90067890
PV1|1|O|ONC^CLINIC^A^DFCI|||28461^Calloway^Patricia^K^MD^^NPI|||||||||OUT||||||||||||||||||DFCI||||20250323073000
ORC|NW|ORD70008||||||^^^20250325080000^^R||20250323081000|||28461^Calloway^Patricia^K^MD^^NPI
OBR|1|ORD70008||78816^PET-CT Whole Body^CPT|||20250325080000||||||||28461^Calloway^Patricia^K^MD^^NPI|||||||||||1^^^20250325080000^^R
DG1|1||C34.11^Malignant neoplasm of upper lobe, right bronchus or lung^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||52 yo female with newly diagnosed right upper lobe lung adenocarcinoma (biopsy proven). Staging PET-CT prior to treatment planning.||||||F
```

---

## 9. ORU^R01 - PET-CT report with embedded PDF from Dana-Farber

```
MSH|^~\&|POWERSCRIBE|DFCI^5005^NPI|RAD_RECV|MGB_HIS|20250325160000||ORU^R01^ORU_R01|PS00009|P|2.4|||AL|NE
PID|1||MRN90678901^^^DFCI^MR||Hwang^Ji-Yeon^Allison^^Ms.||19720612|F||2028-9^Asian^HL70005|58 Brattle St^^Cambridge^MA^02138^US||^PRN^PH^^^617^7294583||S||VN90067890
PV1|1|O|ONC^CLINIC^A^DFCI|||28461^Calloway^Patricia^K^MD^^NPI|||||||||OUT||||||||||||||||||DFCI||||20250323073000
ORC|RE|ORD70008|RAD80008||CM||||20250325160000|||39572^Epstein^Nathan^W^MD^^NPI
OBR|1|ORD70008|RAD80008|78816^PET-CT Whole Body^CPT|||20250325083000||||||||||39572^Epstein^Nathan^W^MD^^NPI|||||20250325160000||RAD|F|||28461^Calloway^Patricia^K^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||PET-CT WHOLE BODY~CLINICAL HISTORY: Newly diagnosed right upper lobe lung adenocarcinoma. Staging.~RADIOPHARMACEUTICAL: 12.5 mCi FDG-18. Blood glucose 92 mg/dL.~COMPARISON: CT Chest dated 2025-03-10.~FINDINGS:~PRIMARY TUMOR: 3.2 cm FDG-avid mass in right upper lobe (SUVmax 12.4).~LYMPH NODES: FDG-avid right hilar lymph node, 1.5 cm (SUVmax 8.2).~FDG-avid subcarinal lymph node, 1.2 cm (SUVmax 6.5).~No contralateral mediastinal or supraclavicular activity.~DISTANT: No FDG-avid hepatic, adrenal, or osseous lesions.~Brain not included in field of view.~IMPRESSION:~1. FDG-avid right upper lobe mass consistent with known primary (SUVmax 12.4).~2. Ipsilateral hilar and subcarinal lymphadenopathy (N2 disease).~3. No distant metastases identified. Clinical stage IIIA (T2aN2M0).~4. Recommend brain MRI to complete staging.||||||F|||20250325160000
OBX|2|ED|RAD_PDF^PET-CT Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 10. ORU^R01 - Ultrasound report from BIDMC radiology

```
MSH|^~\&|POWERSCRIBE|BIDMC^5003^NPI|RAD_RECV|BIDMC_HIS|20250327143000||ORU^R01^ORU_R01|PS00010|P|2.4|||AL|NE
PID|1||MRN01789012^^^BIDMC^MR||Petrov^Svetlana^Yurievna^^Ms.||19850509|F||2106-3^White^HL70005|119 Babcock St^^Brookline^MA^02446^US||^PRN^PH^^^857^3481962||S||VN01078901
PV1|1|O|GYN^CLINIC^A^BIDMC|||42873^Obeng^Abena^F^MD^^NPI|||||||||OUT||||||||||||||||||BIDMC||||20250327130000
ORC|RE|ORD80010|RAD90010||CM||||20250327143000|||51694^Marquez^Diego^P^MD^^NPI
OBR|1|ORD80010|RAD90010|76856^Pelvic Ultrasound^CPT|||20250327133000||||||||||51694^Marquez^Diego^P^MD^^NPI|||||20250327143000||RAD|F|||42873^Obeng^Abena^F^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||PELVIC ULTRASOUND, TRANSABDOMINAL AND TRANSVAGINAL~CLINICAL HISTORY: 39-year-old female with pelvic pain and heavy menstrual bleeding.~COMPARISON: Pelvic ultrasound dated 2024-09-20.~FINDINGS:~UTERUS: Anteverted, enlarged measuring 12.4 x 8.2 x 7.8 cm (previously 10.1 x 7.0 x 6.5 cm).~Multiple fibroids identified:~- Intramural posterior wall: 4.2 cm (previously 3.5 cm)~- Subserosal fundal: 2.8 cm (previously 2.5 cm)~- Submucosal anterior wall: 1.5 cm (new)~Endometrium: 6mm, normal appearance.~OVARIES: Right ovary 3.2 x 2.1 cm, normal. Left ovary 2.8 x 1.9 cm, normal.~No free fluid.~IMPRESSION:~1. Interval growth of uterine fibroids with new submucosal fibroid.~2. Clinical correlation for GnRH agonist therapy or surgical planning.||||||F|||20250327143000
```

---

## 11. ORU^R01 - Spine MRI report from MGH radiology

```
MSH|^~\&|POWERSCRIBE|MGH^5001^NPI|RAD_RECV|MGB_HIS|20250329150000||ORU^R01^ORU_R01|PS00011|P|2.4|||AL|NE
PID|1||MRN02890123^^^MGB^MR||Hennessy^Colin^William^^Mr.||19600425|M||2106-3^White^HL70005|38 Revere St^^Boston^MA^02114^US||^PRN^PH^^^617^2918374||M||VN02089012
PV1|1|O|NEUR^SPINE^A^MGH|||64185^DiNapoli^Victor^A^MD^^NPI|||||||||OUT||||||||||||||||||MGH||||20250329130000
ORC|RE|ORD90011|RAD01011||CM||||20250329150000|||75296^Kim^Janet^S^MD^^NPI
OBR|1|ORD90011|RAD01011|72148^MRI Lumbar Spine without Contrast^CPT|||20250329133000||||||||||75296^Kim^Janet^S^MD^^NPI|||||20250329150000||RAD|F|||64185^DiNapoli^Victor^A^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||MRI LUMBAR SPINE WITHOUT CONTRAST~CLINICAL HISTORY: 64-year-old male with bilateral lower extremity radiculopathy.~COMPARISON: MRI dated 2023-11-05.~TECHNIQUE: Multiplanar multisequence MRI without contrast.~FINDINGS:~L3-L4: Mild disc bulge with bilateral facet hypertrophy. Mild central stenosis.~L4-L5: Broad-based disc protrusion with bilateral foraminal extension.~Moderate central stenosis (AP diameter 8mm). Moderate bilateral foraminal stenosis.~L5-S1: Moderate disc desiccation. Left paracentral disc protrusion contacting the~traversing left S1 nerve root. Mild left foraminal stenosis.~Conus terminates at L1, normal signal. No compression fracture.~IMPRESSION:~1. L4-L5: Moderate central and bilateral foraminal stenosis, worse than prior.~2. L5-S1: Left paracentral protrusion with S1 nerve root contact.~3. Recommend spine surgery consultation.||||||F|||20250329150000
```

---

## 12. ORM^O01 - Bone density order received by PowerScribe from BIDMC

```
MSH|^~\&|EPIC|BIDMC^5003^NPI|POWERSCRIBE|BIDMC_RAD|20250331082000||ORM^O01^ORM_O01|PS00012|P|2.4|||AL|NE
PID|1||MRN03901234^^^BIDMC^MR||Kozlov^Galina^Dmitrievna^^Mrs.||19550712|F||2106-3^White^HL70005|85 Walnut St^^Watertown^MA^02472^US||^PRN^PH^^^781^6392814||W||VN03090123
PV1|1|O|RHEUM^CLINIC^A^BIDMC|||86413^Steinfeld^Judith^C^MD^^NPI|||||||||OUT||||||||||||||||||BIDMC||||20250331075000
ORC|NW|ORD01012||||||^^^20250401090000^^R||20250331082000|||86413^Steinfeld^Judith^C^MD^^NPI
OBR|1|ORD01012||77080^DEXA Bone Density^CPT|||20250401090000||||||||86413^Steinfeld^Judith^C^MD^^NPI|||||||||||1^^^20250401090000^^R
DG1|1||M81.0^Age-related osteoporosis without current pathological fracture^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||69 yo female on prednisone for rheumatoid arthritis. History of vertebral compression fracture 2023. On alendronate.||||||F
```

---

## 13. ORU^R01 - DEXA scan report from BIDMC

```
MSH|^~\&|POWERSCRIBE|BIDMC^5003^NPI|RAD_RECV|BIDMC_HIS|20250401130000||ORU^R01^ORU_R01|PS00013|P|2.4|||AL|NE
PID|1||MRN03901234^^^BIDMC^MR||Kozlov^Galina^Dmitrievna^^Mrs.||19550712|F||2106-3^White^HL70005|85 Walnut St^^Watertown^MA^02472^US||^PRN^PH^^^781^6392814||W||VN03090123
PV1|1|O|RHEUM^CLINIC^A^BIDMC|||86413^Steinfeld^Judith^C^MD^^NPI|||||||||OUT||||||||||||||||||BIDMC||||20250331075000
ORC|RE|ORD01012|RAD11012||CM||||20250401130000|||97324^Nakamura^Yumi^A^MD^^NPI
OBR|1|ORD01012|RAD11012|77080^DEXA Bone Density^CPT|||20250401093000||||||||||97324^Nakamura^Yumi^A^MD^^NPI|||||20250401130000||RAD|F|||86413^Steinfeld^Judith^C^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||DEXA BONE DENSITY~CLINICAL HISTORY: 69-year-old female on chronic prednisone. History of vertebral fracture.~COMPARISON: DEXA dated 2023-04-10.~FINDINGS:~LUMBAR SPINE (L1-L4): BMD 0.782 g/cm2, T-score -2.8 (previously -2.5).~TOTAL HIP: BMD 0.658 g/cm2, T-score -2.4 (previously -2.2).~FEMORAL NECK: BMD 0.612 g/cm2, T-score -2.9 (previously -2.6).~IMPRESSION:~1. Osteoporosis at all measured sites with interval decline from 2023.~2. FRAX 10-year major osteoporotic fracture probability: 28%.~3. Current therapy may need reassessment given progressive bone loss.||||||F|||20250401130000
```

---

## 14. ORU^R01 - Abdominal ultrasound from Baystate Health

```
MSH|^~\&|POWERSCRIBE|BAYS^5004^NPI|RAD_RECV|BAYS_HIS|20250403093000||ORU^R01^ORU_R01|PS00014|P|2.4|||AL|NE
PID|1||BAY04012345^^^BAYS^MR||Mensah^Adwoa^Serwa^^Mrs.||19780204|F||2054-5^Black^HL70005|73 Belmont Ave^^Springfield^MA^01108^US||^PRN^PH^^^413^2748193||M||VN04001234
PV1|1|O|GI^CLINIC^A^BAYS|||14527^Bergeron^Marc^E^MD^^NPI|||||||||OUT||||||||||||||||||BAYS||||20250403080000
ORC|RE|ORD11014|RAD21014||CM||||20250403093000|||25638^Vargas^Andrea^L^MD^^NPI
OBR|1|ORD11014|RAD21014|76700^Abdominal Ultrasound Complete^CPT|||20250403083000||||||||||25638^Vargas^Andrea^L^MD^^NPI|||||20250403093000||RAD|F|||14527^Bergeron^Marc^E^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||ABDOMINAL ULTRASOUND, COMPLETE~CLINICAL HISTORY: 47-year-old female with RUQ pain and elevated liver enzymes.~COMPARISON: None.~FINDINGS:~LIVER: Increased echogenicity consistent with hepatic steatosis.~No focal hepatic lesion. Liver measures 17.5 cm (mildly enlarged).~GALLBLADDER: Multiple shadowing gallstones, largest 1.2 cm.~Gallbladder wall mildly thickened at 4mm. No pericholecystic fluid.~CBD: 5mm, normal caliber.~PANCREAS: Partially visualized, normal where seen.~RIGHT KIDNEY: 11.2 cm, normal. No hydronephrosis.~LEFT KIDNEY: 10.8 cm, normal. No hydronephrosis.~SPLEEN: 11.5 cm, normal.~AORTA: Normal caliber.~IMPRESSION:~1. Cholelithiasis with mild gallbladder wall thickening. Correlate with Murphy sign.~2. Hepatic steatosis with mild hepatomegaly.||||||F|||20250403093000
```

---

## 15. ORU^R01 - Knee MRI report from BWH radiology

```
MSH|^~\&|POWERSCRIBE|BWH^5002^NPI|RAD_RECV|MGB_HIS|20250405160000||ORU^R01^ORU_R01|PS00015|P|2.4|||AL|NE
PID|1||MRN05123456^^^MGB^MR||Flanagan^Liam^Patrick^^Mr.||19850916|M||2106-3^White^HL70005|267 Walden St^^Cambridge^MA^02140^US||^PRN^PH^^^857^5183926||S||VN05012345
PV1|1|O|ORTH^SPORT^A^BWH|||31748^Reeves^Harrison^C^MD^^NPI|||||||||OUT||||||||||||||||||BWH||||20250405140000
ORC|RE|ORD21015|RAD31015||CM||||20250405160000|||42859^Chung^Esther^V^MD^^NPI
OBR|1|ORD21015|RAD31015|73721^MRI Right Knee without Contrast^CPT|||20250405143000||||||||||42859^Chung^Esther^V^MD^^NPI|||||20250405160000||RAD|F|||31748^Reeves^Harrison^C^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||MRI RIGHT KNEE WITHOUT CONTRAST~CLINICAL HISTORY: 39-year-old male with acute knee injury during basketball.~COMPARISON: None.~TECHNIQUE: Multiplanar multisequence MRI without contrast.~FINDINGS:~ACL: Complete tear with abnormal morphology and signal. No residual intact fibers.~PCL: Intact, normal signal.~MENISCI: Bucket-handle tear of the medial meniscus with fragment displaced into~the intercondylar notch. Lateral meniscus intact.~MCL: Grade 2 sprain with partial thickness tearing of the deep fibers.~LCL: Intact.~CARTILAGE: Focal grade 3 chondral defect medial femoral condyle.~Large joint effusion.~IMPRESSION:~1. Complete ACL tear.~2. Bucket-handle tear of medial meniscus with displaced fragment.~3. Grade 2 MCL sprain.~4. Recommend orthopedic surgery consultation for reconstruction.||||||F|||20250405160000
```

---

## 16. ORU^R01 - Coronary CT angiography report from MGH

```
MSH|^~\&|POWERSCRIBE|MGH^5001^NPI|RAD_RECV|MGB_HIS|20250407141500||ORU^R01^ORU_R01|PS00016|P|2.5.1|||AL|NE
PID|1||MRN06234567^^^MGB^MR||Connolly^Ronan^James^^Mr.||19630118|M||2106-3^White^HL70005|18 Hancock St^^Quincy^MA^02171^US||^PRN^PH^^^617^4827163||M||VN06023456
PV1|1|O|CARD^CTA^A^MGH|||53176^Raghavan^Pradeep^V^MD^^NPI|||||||||OUT||||||||||||||||||MGH||||20250407120000
ORC|RE|ORD31016|RAD41016||CM||||20250407141500|||64287^Watanabe^Akira^T^MD^^NPI
OBR|1|ORD31016|RAD41016|75574^Coronary CT Angiography^CPT|||20250407123000||||||||||64287^Watanabe^Akira^T^MD^^NPI|||||20250407141500||RAD|F|||53176^Raghavan^Pradeep^V^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||CORONARY CT ANGIOGRAPHY~CLINICAL HISTORY: 62-year-old male with atypical chest pain. Intermediate pre-test probability.~TECHNIQUE: Retrospective ECG-gated CT with 75mL Visipaque 320.~Heart rate: 58 bpm. Calcium score: 245 (moderate).~FINDINGS:~LEFT MAIN: No stenosis.~LAD: Mixed plaque in proximal segment with 50-60% stenosis. Non-calcified plaque in mid-segment with 40% stenosis.~LCX: Calcified plaque in proximal segment, <30% stenosis.~RCA: Calcified plaque in mid-segment, 30-40% stenosis.~Left ventricular function normal. No pericardial effusion.~IMPRESSION:~1. Moderate stenosis of proximal LAD (50-60%), likely hemodynamically significant.~2. Calcium score 245 (moderate atherosclerotic burden).~3. Recommend functional testing (stress MRI or FFR-CT) or invasive angiography.||||||F|||20250407141500
```

---

## 17. ORM^O01 - Chest CT order from Tufts Medical Center

```
MSH|^~\&|EPIC|TMC^5006^NPI|POWERSCRIBE|TMC_RAD|20250409100000||ORM^O01^ORM_O01|PS00017|P|2.4|||AL|NE
PID|1||MRN07345678^^^TMC^MR||Lindqvist^Erik^Matthias^^Mr.||19670930|M||2106-3^White^HL70005|84 Waltham St^^Burlington^MA^01803^US||^PRN^PH^^^781^3827451||M||VN07034567
PV1|1|I|PUL^3N^A^TMC|||61824^Mitchell^Sandra^R^MD^^NPI|||||||||IN||||||||||||||||||TMC||||20250408200000
ORC|NW|ORD41017||||||^^^20250410080000^^R||20250409100000|||61824^Mitchell^Sandra^R^MD^^NPI
OBR|1|ORD41017||71250^CT Chest without Contrast^CPT|||20250410080000||||||||61824^Mitchell^Sandra^R^MD^^NPI|||||||||||1^^^20250410080000^^R
DG1|1||J84.10^Pulmonary fibrosis, unspecified^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||57 yo male with progressive dyspnea, known IPF on pirfenidone. Baseline CT for monitoring.||||||F
```

---

## 18. ORU^R01 - Chest CT report from Tufts Medical Center

```
MSH|^~\&|POWERSCRIBE|TMC^5006^NPI|RAD_RECV|TMC_HIS|20250410140000||ORU^R01^ORU_R01|PS00018|P|2.4|||AL|NE
PID|1||MRN07345678^^^TMC^MR||Lindqvist^Erik^Matthias^^Mr.||19670930|M||2106-3^White^HL70005|84 Waltham St^^Burlington^MA^01803^US||^PRN^PH^^^781^3827451||M||VN07034567
PV1|1|I|PUL^3N^A^TMC|||61824^Mitchell^Sandra^R^MD^^NPI|||||||||IN||||||||||||||||||TMC||||20250408200000
ORC|RE|ORD41017|RAD51017||CM||||20250410140000|||72935^Banerjee^Arun^M^MD^^NPI
OBR|1|ORD41017|RAD51017|71250^CT Chest without Contrast^CPT|||20250410083000||||||||||72935^Banerjee^Arun^M^MD^^NPI|||||20250410140000||RAD|F|||61824^Mitchell^Sandra^R^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||CT CHEST WITHOUT CONTRAST~CLINICAL HISTORY: Known IPF, baseline monitoring.~COMPARISON: CT Chest dated 2024-10-15.~TECHNIQUE: Helical CT without contrast, including prone imaging.~FINDINGS:~Bilateral subpleural and basal predominant reticulation with honeycombing,~consistent with UIP pattern. Traction bronchiectasis in lower lobes.~Interval mild progression compared to prior with new areas of honeycombing~in the right middle lobe.~No ground glass opacities to suggest acute exacerbation.~No pleural effusion. No pneumothorax.~Mediastinal lymph nodes subcentimeter, unchanged.~Heart size normal. No pericardial effusion.~IMPRESSION:~1. UIP pattern consistent with IPF, mild interval progression.~2. New honeycombing in right middle lobe.~3. No evidence of acute exacerbation.~4. Pulmonology follow-up for treatment reassessment.||||||F|||20250410140000
```

---

## 19. ORU^R01 - Carotid ultrasound report with embedded PDF from Baystate

```
MSH|^~\&|POWERSCRIBE|BAYS^5004^NPI|RAD_RECV|BAYS_HIS|20250412110000||ORU^R01^ORU_R01|PS00019|P|2.4|||AL|NE
PID|1||BAY08456789^^^BAYS^MR||Bouchard^Roland^Henri^^Mr.||19540607|M||2106-3^White^HL70005|192 Dwight St^^Springfield^MA^01103^US||^PRN^PH^^^413^8291543||M||VN08045678
PV1|1|O|VASC^CLINIC^A^BAYS|||83614^Delaney^Brendan^K^MD^^NPI|||||||||OUT||||||||||||||||||BAYS||||20250412090000
ORC|RE|ORD51019|RAD61019||CM||||20250412110000|||94725^Sorensen^Ingrid^R^MD^^NPI
OBR|1|ORD51019|RAD61019|93880^Carotid Duplex Ultrasound^CPT|||20250412093000||||||||||94725^Sorensen^Ingrid^R^MD^^NPI|||||20250412110000||RAD|F|||83614^Delaney^Brendan^K^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||CAROTID DUPLEX ULTRASOUND~CLINICAL HISTORY: 70-year-old male with right-sided TIA. Evaluate for carotid stenosis.~COMPARISON: None.~FINDINGS:~RIGHT INTERNAL CAROTID ARTERY:~Peak systolic velocity: 285 cm/s. End diastolic velocity: 112 cm/s.~ICA/CCA ratio: 4.2. Heterogeneous plaque at the bifurcation.~Estimated stenosis: 70-79% (NASCET criteria).~LEFT INTERNAL CAROTID ARTERY:~Peak systolic velocity: 95 cm/s. End diastolic velocity: 28 cm/s.~ICA/CCA ratio: 1.3. Mild calcified plaque.~Estimated stenosis: <50%.~VERTEBRAL ARTERIES: Antegrade flow bilaterally.~IMPRESSION:~1. High-grade right ICA stenosis (70-79%) with heterogeneous plaque.~2. Mild left ICA stenosis (<50%).~3. Given symptomatic high-grade stenosis, recommend vascular surgery consultation~for carotid endarterectomy evaluation.||||||F|||20250412110000
OBX|2|ED|RAD_PDF^Carotid Ultrasound Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 20. ORU^R01 - Shoulder MRI report from MGH radiology

```
MSH|^~\&|POWERSCRIBE|MGH^5001^NPI|RAD_RECV|MGB_HIS|20250414153000||ORU^R01^ORU_R01|PS00020|P|2.4|||AL|NE
PID|1||MRN09567890^^^MGB^MR||Galvin^Kieran^Thomas^^Mr.||19720303|M||2106-3^White^HL70005|57 Summer St^^Somerville^MA^02143^US||^PRN^PH^^^617^3914728||M||VN09056789
PV1|1|O|ORTH^SPORT^A^MGH|||17342^Lombardi^Craig^W^MD^^NPI|||||||||OUT||||||||||||||||||MGH||||20250414133000
ORC|RE|ORD61020|RAD71020||CM||||20250414153000|||28453^Takahashi^Emiko^N^MD^^NPI
OBR|1|ORD61020|RAD71020|73221^MRI Right Shoulder without Contrast^CPT|||20250414140000||||||||||28453^Takahashi^Emiko^N^MD^^NPI|||||20250414153000||RAD|F|||17342^Lombardi^Craig^W^MD^^NPI
OBX|1|TX|RAD_RPT^Radiology Report^L||MRI RIGHT SHOULDER WITHOUT CONTRAST~CLINICAL HISTORY: 52-year-old male with chronic shoulder pain, failed physical therapy.~COMPARISON: None.~TECHNIQUE: Multiplanar multisequence MRI without contrast.~FINDINGS:~ROTATOR CUFF: Full-thickness tear of the supraspinatus tendon, measuring~1.8 cm in the AP dimension with 1.2 cm retraction. Infraspinatus tendon intact.~Subscapularis tendon intact.~BICEPS: Long head biceps tendon subluxed medially out of the bicipital groove,~consistent with subscapularis pulley disruption.~LABRUM: Superior labral tear from 10 to 2 o'clock position (SLAP tear).~GLENOHUMERAL JOINT: Moderate effusion. No loose bodies.~ACROMIOCLAVICULAR JOINT: Moderate degenerative changes with inferior osteophytes.~MUSCLE: Mild fatty infiltration of supraspinatus (Goutallier grade 2).~IMPRESSION:~1. Full-thickness supraspinatus tear with mild retraction and Goutallier 2 atrophy.~2. Medial subluxation of long head biceps with pulley disruption.~3. Superior labral (SLAP) tear.~4. Surgical consultation recommended for rotator cuff repair.||||||F|||20250414153000
```
