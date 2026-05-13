# Nuance PowerScribe - real HL7v2 ER7 messages

---

## 1. ORU^R01 - Chest X-ray report from Inova Fairfax radiology

```
MSH|^~\&|POWERSCRIBE|INOVA_RAD|INOVA_RIS|INOVA_FAIRFAX|20260509083000||ORU^R01^ORU_R01|PS20260509083000001|P|2.5.1|||AL|NE
PID|1||MRN20012345^^^INOVA^MR||CHOWDHURY^Lakshmi^Priya||19670618|F||2106-3^White^CDCREC|2418 Gallows Rd^^Vienna^VA^22180^US||^PRN^PH^^^703^5554829||M||ACCT20260509020|312-44-7856|||N^Non-Hispanic^HL70189
PV1|1|O|RAD^001^A^INOVA_FAIRFAX||||1111234567^Oyelaran^Babatunde^MD^^Dr.|||RAD||||PHY
ORC|RE|ORD20260509010|RAD20260509010||CM||||20260509080000|||1111234567^Oyelaran^Babatunde^MD^^Dr.
OBR|1|ORD20260509010|RAD20260509010|71046-8^Chest X-ray 2 views^LN|||20260509075000|||||||||1111234567^Oyelaran^Babatunde^MD^^Dr.||||||20260509082500||RAD|F
OBX|1|FT|71046-8^Chest X-ray 2 views^LN||CHEST X-RAY, PA AND LATERAL\.br\\.br\CLINICAL HISTORY: Persistent cough for 2 weeks.\.br\\.br\TECHNIQUE: PA and lateral views of the chest.\.br\\.br\COMPARISON: None available.\.br\\.br\FINDINGS:\.br\Heart size is within normal limits. Mediastinal contours are normal.\.br\Lungs are clear bilaterally. No focal consolidation, pleural effusion,\.br\or pneumothorax. Bony structures are intact.\.br\\.br\IMPRESSION:\.br\Normal chest radiograph. No acute cardiopulmonary disease.\.br\\.br\Electronically signed by: Babatunde Oyelaran, MD\.br\Date: 05/09/2026 08:25||||||F|||20260509082500
```

---

## 2. ORU^R01 - CT abdomen/pelvis report from Sentara Norfolk

```
MSH|^~\&|POWERSCRIBE|SENTARA_RAD|SENTARA_RIS|SENTARA_NORFOLK|20260509102000||ORU^R01^ORU_R01|PS20260509102000002|P|2.5.1|||AL|NE
PID|1||MRN20023456^^^SENTARA^MR||PHAM^Quang^Duc^^Mr.||19790823|M||2028-9^Asian^CDCREC|941 W 21st St^^Norfolk^VA^23517^US||^PRN^PH^^^757^5556193||M||ACCT20260509021|423-55-8967|||N^Non-Hispanic^HL70189
PV1|1|O|RAD^CT1^A^SENTARA_NORFOLK||||2222345678^Subramaniam^Meera^MD^^Dr.|||RAD||||PHY
ORC|RE|ORD20260509011|RAD20260509011||CM||||20260509093000|||2222345678^Subramaniam^Meera^MD^^Dr.
OBR|1|ORD20260509011|RAD20260509011|74177-2^CT abdomen and pelvis with contrast^LN|||20260509091500|||||||||2222345678^Subramaniam^Meera^MD^^Dr.||||||20260509101500||RAD|F
OBX|1|FT|74177-2^CT abdomen and pelvis with contrast^LN||CT ABDOMEN AND PELVIS WITH IV CONTRAST\.br\\.br\CLINICAL HISTORY: Abdominal pain, rule out appendicitis.\.br\\.br\TECHNIQUE: Helical CT of the abdomen and pelvis with 100 mL Omnipaque 350\.br\IV contrast. Oral contrast was administered.\.br\\.br\COMPARISON: None available.\.br\\.br\FINDINGS:\.br\LIVER: Normal size and attenuation. No focal lesions.\.br\GALLBLADDER: Normal. No gallstones.\.br\PANCREAS: Normal. No peripancreatic fluid.\.br\SPLEEN: Normal size. No focal lesions.\.br\KIDNEYS: Normal bilaterally. No hydronephrosis or stones.\.br\APPENDIX: Mildly dilated to 8mm with periappendiceal fat stranding.\.br\No appendicolith identified. Findings consistent with acute appendicitis.\.br\BOWEL: No obstruction. No free air.\.br\LYMPH NODES: No significant lymphadenopathy.\.br\PELVIS: Urinary bladder is normal. No free fluid.\.br\\.br\IMPRESSION:\.br\1. Acute appendicitis.\.br\2. No other acute abdominal pathology.\.br\\.br\Electronically signed by: Meera Subramaniam, MD\.br\Date: 05/09/2026 10:15||||||F|||20260509101500
```

---

## 3. ORU^R01 - MRI brain report with embedded PDF from VCU Health

```
MSH|^~\&|POWERSCRIBE|VCU_RAD|VCU_RIS|VCU_MEDICAL|20260508163000||ORU^R01^ORU_R01|PS20260508163000003|P|2.5.1|||AL|NE
PID|1||MRN20034567^^^VCU^MR||OGLETREE^Tamara^Renee||19840917|F||2054-5^Black or African American^CDCREC|3518 Brook Rd^^Richmond^VA^23227^US||^PRN^PH^^^804^5557284||S||ACCT20260508022|534-66-9178|||N^Non-Hispanic^HL70189
PV1|1|I|NEURO^204^A^VCU_MEDICAL||||3333456789^Petrov^Andrei^MD^^Dr.||4444567890^Castellano^Sofia^MD^^Dr.|NEU||||ADM|||3333456789^Petrov^Andrei^MD^^Dr.|IN
ORC|RE|ORD20260508012|RAD20260508012||CM||||20260508150000|||3333456789^Petrov^Andrei^MD^^Dr.
OBR|1|ORD20260508012|RAD20260508012|70553-0^MRI Brain with and without contrast^LN|||20260508143000|||||||||3333456789^Petrov^Andrei^MD^^Dr.||||||20260508162500||RAD|F
OBX|1|FT|70553-0^MRI Brain with and without contrast^LN||MRI BRAIN WITH AND WITHOUT IV CONTRAST\.br\\.br\CLINICAL HISTORY: New onset seizures, headaches.\.br\\.br\TECHNIQUE: Multiplanar multisequence MRI of the brain without and with\.br\15 mL Gadavist IV contrast.\.br\\.br\COMPARISON: None.\.br\\.br\FINDINGS:\.br\There is a 2.3 x 1.8 cm enhancing mass in the right temporal lobe\.br\with surrounding vasogenic edema. Mass effect on the right lateral ventricle.\.br\No midline shift. No hemorrhage. Remaining brain parenchyma is unremarkable.\.br\Ventricles and sulci are age-appropriate. No restricted diffusion.\.br\Major intracranial vessels demonstrate normal flow voids.\.br\\.br\IMPRESSION:\.br\1. Right temporal lobe enhancing mass with surrounding edema,\.br\suspicious for primary neoplasm. Recommend neurosurgical consultation\.br\and consideration of biopsy.\.br\2. No acute infarct or hemorrhage.\.br\\.br\Electronically signed by: Andrei Petrov, MD\.br\Date: 05/08/2026 16:25||||||F|||20260508162500
OBX|2|ED|PDF^Radiology Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyOTggPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihSYWRpb2xvZ3kgUmVwb3J0IC0gTVJJIEJyYWluKSBUagowIC0yMCBUZAooUGF0aWVudDogV2FzaGluZ3RvbiwgRGVuaXNlIFJlbmVlKSBUagowIC0yMCBUZAooRmluZGluZzogMi4zIHggMS44IGNtIGVuaGFuY2luZyBtYXNzIHJpZ2h0IHRlbXBvcmFsIGxvYmUpIFRqCjAgLTIwIFRkCihJbXByZXNzaW9uOiBTdXNwaWNpb3VzIGZvciBwcmltYXJ5IG5lb3BsYXNtKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAgbiAKMDAwMDAwMDY1NiAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjczNQolJUVPRgo=||||||F
```

---

## 4. ORU^R01 - Mammography report from Carilion Roanoke

```
MSH|^~\&|POWERSCRIBE|CARILION_RAD|CARILION_RIS|CARILION_ROANOKE|20260509111500||ORU^R01^ORU_R01|PS20260509111500004|P|2.5.1|||AL|NE
PID|1||MRN20045678^^^CARILION^MR||MCALLISTER^Dawn^Elizabeth||19730524|F||2106-3^White^CDCREC|2815 Franklin Rd SW^^Roanoke^VA^24014^US||^PRN^PH^^^540^5558395||M||ACCT20260509023|645-77-1289|||N^Non-Hispanic^HL70189
PV1|1|O|RAD^MAMMO1^A^CARILION_ROANOKE||||5555678901^Obi^Chiamaka^MD^^Dr.|||RAD||||PHY
ORC|RE|ORD20260509013|RAD20260509013||CM||||20260509103000|||5555678901^Obi^Chiamaka^MD^^Dr.
OBR|1|ORD20260509013|RAD20260509013|24606-6^Mammogram screening bilateral^LN|||20260509100000|||||||||5555678901^Obi^Chiamaka^MD^^Dr.||||||20260509111000||RAD|F
OBX|1|FT|24606-6^Mammogram screening bilateral^LN||BILATERAL SCREENING MAMMOGRAM\.br\\.br\CLINICAL HISTORY: Annual screening. No palpable masses or nipple discharge.\.br\\.br\TECHNIQUE: Standard CC and MLO views of both breasts. Tomosynthesis performed.\.br\\.br\COMPARISON: Mammogram dated 05/12/2025.\.br\\.br\FINDINGS:\.br\BREAST COMPOSITION: Heterogeneously dense (ACR density C).\.br\RIGHT BREAST: No suspicious masses, calcifications, or architectural distortion.\.br\LEFT BREAST: No suspicious masses, calcifications, or architectural distortion.\.br\AXILLARY REGIONS: Normal bilaterally.\.br\\.br\ASSESSMENT: BI-RADS 1 - Negative.\.br\\.br\RECOMMENDATION: Annual screening mammography.\.br\\.br\Electronically signed by: Chiamaka Obi, MD\.br\Date: 05/09/2026 11:10||||||F|||20260509111000
```

---

## 5. ORU^R01 - Ultrasound abdomen report from UVA Health

```
MSH|^~\&|POWERSCRIBE|UVA_RAD|UVA_RIS|UVA_HEALTH|20260508141000||ORU^R01^ORU_R01|PS20260508141000005|P|2.5.1|||AL|NE
PID|1||MRN20056789^^^UVA^MR||FITZGERALD^Bernard^Lewis||19620218|M||2106-3^White^CDCREC|1120 W Main St^^Charlottesville^VA^22903^US||^PRN^PH^^^434^5559416||M||ACCT20260508024|756-88-2391|||N^Non-Hispanic^HL70189
PV1|1|O|RAD^US1^A^UVA_HEALTH||||6666789012^Nakamura^Yuki^MD^^Dr.|||RAD||||PHY
ORC|RE|ORD20260508013|RAD20260508013||CM||||20260508133000|||6666789012^Nakamura^Yuki^MD^^Dr.
OBR|1|ORD20260508013|RAD20260508013|76700-0^Ultrasound abdomen complete^LN|||20260508130000|||||||||6666789012^Nakamura^Yuki^MD^^Dr.||||||20260508140500||RAD|F
OBX|1|FT|76700-0^Ultrasound abdomen complete^LN||ULTRASOUND ABDOMEN, COMPLETE\.br\\.br\CLINICAL HISTORY: Right upper quadrant pain, nausea.\.br\\.br\COMPARISON: None.\.br\\.br\FINDINGS:\.br\LIVER: Normal size and echotexture. No focal lesions.\.br\GALLBLADDER: Multiple echogenic foci with posterior acoustic shadowing\.br\consistent with cholelithiasis. No gallbladder wall thickening or\.br\pericholecystic fluid. Positive sonographic Murphy sign.\.br\COMMON BILE DUCT: 4mm, within normal limits.\.br\PANCREAS: Visualized portions are normal.\.br\RIGHT KIDNEY: 11.2 cm. Normal cortical thickness. No hydronephrosis.\.br\LEFT KIDNEY: 11.5 cm. Normal cortical thickness. No hydronephrosis.\.br\SPLEEN: Normal size at 10.8 cm.\.br\AORTA: Normal caliber.\.br\\.br\IMPRESSION:\.br\1. Cholelithiasis with positive Murphy sign, suggestive of acute cholecystitis.\.br\Clinical correlation recommended.\.br\2. No biliary ductal dilation.\.br\\.br\Electronically signed by: Yuki Nakamura, MD\.br\Date: 05/08/2026 14:05||||||F|||20260508140500
```

---

## 6. ORU^R01 - CT head without contrast from Riverside Regional

```
MSH|^~\&|POWERSCRIBE|RIVERSIDE_RAD|RIVERSIDE_RIS|RIVERSIDE_REGIONAL|20260509023000||ORU^R01^ORU_R01|PS20260509023000006|P|2.5.1|||AL|NE
PID|1||MRN20067890^^^RIVERSIDE^MR||WHITMORE^Lloyd^Henry||19560429|M||2106-3^White^CDCREC|930 J Clyde Morris Blvd^^Newport News^VA^23601^US||^PRN^PH^^^757^5551527||W||ACCT20260509025|867-99-3412|||N^Non-Hispanic^HL70189
PV1|1|E|ED^TRAUMA1^A^RIVERSIDE_REG||||7777890123^Afolabi^Olumide^MD^^Dr.|||EM||||PHY
ORC|RE|ORD20260509014|RAD20260509014||CM||||20260509020000|||7777890123^Afolabi^Olumide^MD^^Dr.
OBR|1|ORD20260509014|RAD20260509014|70450-0^CT Head without contrast^LN|||20260509014500|||||||||7777890123^Afolabi^Olumide^MD^^Dr.||||||20260509022500||RAD|F
OBX|1|FT|70450-0^CT Head without contrast^LN||CT HEAD WITHOUT CONTRAST\.br\\.br\CLINICAL HISTORY: Fall from standing height, altered mental status.\.br\\.br\TECHNIQUE: Axial CT of the head without IV contrast.\.br\\.br\COMPARISON: None.\.br\\.br\FINDINGS:\.br\There is a thin right-sided subdural hematoma measuring up to 5mm in\.br\maximal thickness along the right frontoparietal convexity.\.br\Mild rightward-to-leftward midline shift of approximately 3mm.\.br\No intraparenchymal hemorrhage. No skull fracture identified.\.br\Ventricles are mildly prominent consistent with age-related atrophy.\.br\No acute large territory infarct.\.br\\.br\IMPRESSION:\.br\1. Acute right frontoparietal subdural hematoma with mild midline shift.\.br\Neurosurgical consultation recommended.\.br\2. No skull fracture.\.br\\.br\CRITICAL RESULT communicated to Dr. Afolabi by phone at 02:28 on 05/09/2026.\.br\\.br\Electronically signed by: Olumide Afolabi, MD\.br\Date: 05/09/2026 02:25||||||F|||20260509022500
```

---

## 7. ORU^R01 - CT pulmonary angiography from Mary Washington

```
MSH|^~\&|POWERSCRIBE|MWHC_RAD|MWHC_RIS|MARY_WASHINGTON|20260508184500||ORU^R01^ORU_R01|PS20260508184500007|P|2.5.1|||AL|NE
PID|1||MRN20078901^^^MWHC^MR||ASHWORTH^Melinda^Kay||19900811|F||2106-3^White^CDCREC|718 William St^^Fredericksburg^VA^22401^US||^PRN^PH^^^540^5552638||S||ACCT20260508026|978-11-4523|||N^Non-Hispanic^HL70189
PV1|1|E|ED^BED7^A^MWHC||||8888901234^Vasquez^Catalina^MD^^Dr.|||EM||||PHY
ORC|RE|ORD20260508014|RAD20260508014||CM||||20260508180000|||8888901234^Vasquez^Catalina^MD^^Dr.
OBR|1|ORD20260508014|RAD20260508014|36147-2^CT Pulmonary Angiography^LN|||20260508174500|||||||||8888901234^Vasquez^Catalina^MD^^Dr.||||||20260508184000||RAD|F
OBX|1|FT|36147-2^CT Pulmonary Angiography^LN||CT PULMONARY ANGIOGRAPHY\.br\\.br\CLINICAL HISTORY: Acute onset shortness of breath, pleuritic chest pain,\.br\elevated D-dimer.\.br\\.br\TECHNIQUE: CT pulmonary angiography with 80 mL Omnipaque 350 IV contrast.\.br\\.br\COMPARISON: None.\.br\\.br\FINDINGS:\.br\PULMONARY ARTERIES: Large filling defects within the right main pulmonary\.br\artery extending into the right upper and lower lobe segmental branches.\.br\Smaller filling defect in the left lower lobe segmental pulmonary artery.\.br\RV/LV ratio is 1.3, suggestive of right heart strain.\.br\LUNGS: Peripheral wedge-shaped opacity in the right lower lobe consistent\.br\with pulmonary infarct. No pneumothorax.\.br\PLEURA: Small right pleural effusion.\.br\\.br\IMPRESSION:\.br\1. Bilateral pulmonary emboli, extensive on the right with right heart strain.\.br\2. Right lower lobe pulmonary infarct.\.br\3. Small right pleural effusion.\.br\\.br\CRITICAL RESULT communicated to Dr. Vasquez by phone at 18:42 on 05/08/2026.\.br\\.br\Electronically signed by: Catalina Vasquez, MD\.br\Date: 05/08/2026 18:40||||||F|||20260508184000
```

---

## 8. ADT^A01 - Patient admission triggering radiology workflow at Augusta Health

```
MSH|^~\&|AUGUSTA_ADT|AUGUSTA_HEALTH|POWERSCRIBE|AUGUSTA_RAD|20260509070000||ADT^A01^ADT_A01|ADT20260509070000001|P|2.5.1|||AL|NE
EVN|A01|20260509070000|||DR_OKAFOR^Chisom^Okafor^MD
PID|1||MRN20089012^^^AUGUSTA^MR||DANFORTH^Eldon^Ray^^Mr.||19490806|M||2106-3^White^CDCREC|214 N Augusta St^^Staunton^VA^24401^US||^PRN^PH^^^540^5553749||W||ACCT20260509027|189-22-5634|||N^Non-Hispanic^HL70189
NK1|1|DANFORTH^Gladys^Ann^^Mrs.|SPO^Spouse^HL70063||^PRN^PH^^^540^5553750
PV1|1|I|MED^203^A^AUGUSTA_HEALTH^^^^NURS|||9012345678^Okafor^Chisom^MD^^Dr.|||MED||||ADM|||9012345678^Okafor^Chisom^MD^^Dr.|IN||||||||||||||||||AI||A|||20260509070000
DG1|1||J18.9^Pneumonia, unspecified organism^I10|||A
IN1|1|MEDICARE^Medicare|CMS001|Medicare|PO Box 100141^^Columbia^SC^29202||GRP-MCARE|||||||DANFORTH^Eldon^Ray|SEL|19490806|214 N Augusta St^^Staunton^VA^24401^US|||||||||||||||||1AB2-CD3-EF45
```

---

## 9. ORU^R01 - Bone density scan report from Centra Health

```
MSH|^~\&|POWERSCRIBE|CENTRA_RAD|CENTRA_RIS|CENTRA_HEALTH|20260508151500||ORU^R01^ORU_R01|PS20260508151500009|P|2.5.1|||AL|NE
PID|1||MRN20090123^^^CENTRA^MR||PEMBERTON^Wilma^Ann||19541104|F||2106-3^White^CDCREC|4120 Old Forest Rd^^Lynchburg^VA^24501^US||^PRN^PH^^^434^5554851||W||ACCT20260508028|291-33-6745|||N^Non-Hispanic^HL70189
PV1|1|O|RAD^DEXA1^A^CENTRA_HEALTH||||1010123456^Nakamura^Aiko^MD^^Dr.|||RAD||||PHY
ORC|RE|ORD20260508015|RAD20260508015||CM||||20260508143000|||1010123456^Nakamura^Aiko^MD^^Dr.
OBR|1|ORD20260508015|RAD20260508015|38269-7^DEXA Bone Density^LN|||20260508140000|||||||||1010123456^Nakamura^Aiko^MD^^Dr.||||||20260508151000||RAD|F
OBX|1|FT|38269-7^DEXA Bone Density^LN||BONE DENSITY (DEXA) - LUMBAR SPINE AND LEFT HIP\.br\\.br\CLINICAL HISTORY: 73-year-old female, postmenopausal, screening for osteoporosis.\.br\\.br\COMPARISON: DEXA dated 05/15/2024.\.br\\.br\FINDINGS:\.br\LUMBAR SPINE (L1-L4):\.br\BMD: 0.782 g/cm2\.br\T-score: -2.6\.br\Change from prior: -2.1%\.br\\.br\LEFT FEMORAL NECK:\.br\BMD: 0.598 g/cm2\.br\T-score: -2.8\.br\Change from prior: -1.8%\.br\\.br\LEFT TOTAL HIP:\.br\BMD: 0.701 g/cm2\.br\T-score: -2.1\.br\Change from prior: -1.5%\.br\\.br\ASSESSMENT:\.br\Osteoporosis at the lumbar spine and left femoral neck per WHO criteria.\.br\Bone loss progressing compared to prior study.\.br\\.br\RECOMMENDATION:\.br\Consider pharmacologic therapy. FRAX assessment recommended.\.br\\.br\Electronically signed by: Aiko Nakamura, MD\.br\Date: 05/08/2026 15:10||||||F|||20260508151000
```

---

## 10. ORU^R01 - MRI lumbar spine with embedded PDF from Bon Secours

```
MSH|^~\&|POWERSCRIBE|BS_RAD|BS_RIS|BS_STMARYS|20260509133000||ORU^R01^ORU_R01|PS20260509133000010|P|2.5.1|||AL|NE
PID|1||MRN20101234^^^BONSECOURS^MR||LATTIMORE^Curtis^Joseph||19710405|M||2106-3^White^CDCREC|7115 Forest Ave^^Richmond^VA^23226^US||^PRN^PH^^^804^5555962||M||ACCT20260509029|312-44-7856|||N^Non-Hispanic^HL70189
PV1|1|O|RAD^MRI2^A^BS_STMARYS||||1111234567^Subramaniam^Venkat^MD^^Dr.|||RAD||||PHY
ORC|RE|ORD20260509015|RAD20260509015||CM||||20260509123000|||1111234567^Subramaniam^Venkat^MD^^Dr.
OBR|1|ORD20260509015|RAD20260509015|72148-2^MRI Lumbar Spine without contrast^LN|||20260509120000|||||||||1111234567^Subramaniam^Venkat^MD^^Dr.||||||20260509132500||RAD|F
OBX|1|FT|72148-2^MRI Lumbar Spine without contrast^LN||MRI LUMBAR SPINE WITHOUT CONTRAST\.br\\.br\CLINICAL HISTORY: Low back pain radiating to left leg for 6 weeks.\.br\\.br\TECHNIQUE: Multiplanar multisequence MRI of the lumbar spine without contrast.\.br\\.br\COMPARISON: None.\.br\\.br\FINDINGS:\.br\L3-L4: Mild disc bulge without significant canal or foraminal stenosis.\.br\L4-L5: Broad-based disc protrusion with left paracentral component\.br\contacting and mildly displacing the left L5 nerve root. Mild bilateral\.br\facet arthropathy. Mild central canal stenosis.\.br\L5-S1: Small central disc protrusion without significant nerve root\.br\compression. Mild bilateral facet arthropathy.\.br\Vertebral body heights and marrow signal are normal.\.br\Conus medullaris terminates normally at L1.\.br\\.br\IMPRESSION:\.br\1. L4-L5 disc protrusion with left L5 nerve root contact, correlating\.br\with clinical symptoms.\.br\2. Mild degenerative changes at L3-L4 and L5-S1.\.br\\.br\Electronically signed by: Venkat Subramaniam, MD\.br\Date: 05/09/2026 13:25||||||F|||20260509132500
OBX|2|ED|PDF^Radiology Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAzNDUgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihNUkkgTHVtYmFyIFNwaW5lIFJlcG9ydCkgVGoKMCAtMjAgVGQKKFBhdGllbnQ6IFJlZWQsIERhbmllbCBKb3NlcGgpIFRqCjAgLTIwIFRkCihGaW5kaW5nOiBMNC1MNSBkaXNjIHByb3RydXNpb24gd2l0aCBsZWZ0IEw1IG5lcnZlIHJvb3QgY29udGFjdCkgVGoKMCAtMjAgVGQKKEltcHJlc3Npb246IEw0LUw1IGRpc2MgcHJvdHJ1c2lvbiBjb3JyZWxhdGluZyB3aXRoIHN5bXB0b21zKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAgbiAKMDAwMDAwMDcwMyAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjc4MgolJUVPRgo=||||||F
```

---

## 11. ADT^A04 - ED registration feeding PowerScribe at Chesapeake Regional

```
MSH|^~\&|CHESAPEAKE_ADT|CHESAPEAKE_REG|POWERSCRIBE|CHESAPEAKE_RAD|20260509054500||ADT^A04^ADT_A01|ADT20260509054500011|P|2.5.1|||AL|NE
EVN|A04|20260509054500|||CLERK_MORGAN^Lisa^Morgan
PID|1||MRN20112345^^^CHESAPEAKE^MR||DUBOIS^Andre^Marcel^^Mr.||19770213|M||2054-5^Black or African American^CDCREC|1415 S Military Hwy^^Chesapeake^VA^23320^US||^PRN^PH^^^757^5556173||M||ACCT20260509030|423-55-8967|||N^Non-Hispanic^HL70189
PV1|1|E|ED^BED3^A^CHESAPEAKE_REG||||1212345678^Petrov^Katarina^MD^^Dr.|||EM||||PHY|||1212345678^Petrov^Katarina^MD^^Dr.|EM
DG1|1||S52.501A^Unspecified fracture of lower end of right radius, initial encounter^I10|||A
```

---

## 12. ORM^O01 - Radiology order from Winchester Medical Center

```
MSH|^~\&|WINCHESTER_OE|WINCHESTER_MED|POWERSCRIBE|WINCHESTER_RAD|20260508160000||ORM^O01^ORM_O01|ORM20260508160000012|P|2.5.1|||AL|NE
PID|1||MRN20123456^^^WINCHESTER^MR||WHITFIELD^Alma^Mae||19631122|F||2106-3^White^CDCREC|508 S Cameron St^^Winchester^VA^22601^US||^PRN^PH^^^540^5557284||W||ACCT20260508031|534-66-9178|||N^Non-Hispanic^HL70189
PV1|1|O|RAD^001^A^WINCHESTER_MED||||1313456789^Oyelaran^Funmi^MD^^Dr.|||RAD||||PHY
ORC|NW|ORD20260508016||||||20260508155500|||1313456789^Oyelaran^Funmi^MD^^Dr.
OBR|1|ORD20260508016||71046-8^Chest X-ray 2 views^LN|||20260508155500|||||||^Persistent cough and low grade fever|1313456789^Oyelaran^Funmi^MD^^Dr.||||||||RAD
```

---

## 13. ORU^R01 - CT angiography aorta from Inova Alexandria

```
MSH|^~\&|POWERSCRIBE|INOVA_ALEX_RAD|INOVA_RIS|INOVA_ALEXANDRIA|20260509150000||ORU^R01^ORU_R01|PS20260509150000013|P|2.5.1|||AL|NE
PID|1||MRN20134567^^^INOVA^MR||THORNBURG^Eugene^Allen^^Mr.||19581017|M||2106-3^White^CDCREC|4775 Kenmore Ave^^Alexandria^VA^22304^US||^PRN^PH^^^703^5558395||M||ACCT20260509032|645-77-1289|||N^Non-Hispanic^HL70189
PV1|1|O|RAD^CT2^A^INOVA_ALEXANDRIA||||1414567890^Castellano^Andres^MD^^Dr.|||RAD||||PHY
ORC|RE|ORD20260509016|RAD20260509016||CM||||20260509140000|||1414567890^Castellano^Andres^MD^^Dr.
OBR|1|ORD20260509016|RAD20260509016|72191-7^CT Angiography Aorta^LN|||20260509133000|||||||||1414567890^Castellano^Andres^MD^^Dr.||||||20260509145500||RAD|F
OBX|1|FT|72191-7^CT Angiography Aorta^LN||CT ANGIOGRAPHY OF THE AORTA\.br\\.br\CLINICAL HISTORY: Known abdominal aortic aneurysm, surveillance.\.br\\.br\TECHNIQUE: CT angiography from thoracic inlet to femoral heads with\.br\120 mL Omnipaque 350.\.br\\.br\COMPARISON: CTA dated 11/10/2025.\.br\\.br\FINDINGS:\.br\THORACIC AORTA: Normal caliber. No dissection.\.br\ABDOMINAL AORTA: Infrarenal fusiform aneurysm measuring 5.2 cm in\.br\maximal diameter (previously 4.8 cm). Mural thrombus present.\.br\No evidence of rupture or contained leak.\.br\ILIAC ARTERIES: Mild ectasia of bilateral common iliac arteries,\.br\right 1.5 cm, left 1.4 cm.\.br\\.br\IMPRESSION:\.br\1. Infrarenal AAA measuring 5.2 cm, increased from 4.8 cm 6 months ago.\.br\Size now approaching surgical threshold. Vascular surgery consultation\.br\recommended.\.br\2. Mild bilateral common iliac ectasia, stable.\.br\\.br\Electronically signed by: Andres Castellano, MD\.br\Date: 05/09/2026 14:55||||||F|||20260509145500
```

---

## 14. SIU^S12 - Scheduling radiology appointment at Carilion

```
MSH|^~\&|CARILION_SCHED|CARILION_ROANOKE|POWERSCRIBE|CARILION_RAD|20260509140000||SIU^S12^SIU_S12|SIU20260509140000014|P|2.5.1|||AL|NE
SCH|APPT2026051200456||||||ROUTINE^Routine^HL70277|NEW^New^HL70276|45|MIN|^^45^20260512090000^20260512093000|5555678901^Obi^Chiamaka^MD^^Dr.
PID|1||MRN20145678^^^CARILION^MR||HARRINGTON^Joyce^Elaine||19850416|F||2106-3^White^CDCREC|1730 Electric Rd^^Salem^VA^24153^US||^PRN^PH^^^540^5559416||M||ACCT20260509033|756-88-2391|||N^Non-Hispanic^HL70189
PV1|1|O|RAD^MRI1^A^CARILION_ROANOKE||||5555678901^Obi^Chiamaka^MD^^Dr.|||RAD||||PHY
AIS|1||MRI_BRAIN^MRI Brain with Contrast^LOCAL|20260512090000|45|MIN
AIG|1||5555678901^Obi^Chiamaka^MD^^Dr.
AIL|1||RAD^MRI1^A^CARILION_ROANOKE
```

---

## 15. ORU^R01 - Fluoroscopy upper GI report from Sentara

```
MSH|^~\&|POWERSCRIBE|SENTARA_RAD|SENTARA_RIS|SENTARA_NORFOLK|20260508110000||ORU^R01^ORU_R01|PS20260508110000015|P|2.5.1|||AL|NE
PID|1||MRN20156789^^^SENTARA^MR||KWON^Eunice^Yvonne||19760318|F||2054-5^Black or African American^CDCREC|5215 E Princess Anne Rd^^Norfolk^VA^23502^US||^PRN^PH^^^757^5551527||D||ACCT20260508034|867-99-3412|||N^Non-Hispanic^HL70189
PV1|1|O|RAD^FLUORO1^A^SENTARA_NORFOLK||||1515678901^Afolabi^Segun^MD^^Dr.|||RAD||||PHY
ORC|RE|ORD20260508017|RAD20260508017||CM||||20260508100000|||1515678901^Afolabi^Segun^MD^^Dr.
OBR|1|ORD20260508017|RAD20260508017|72125-3^Upper GI Series^LN|||20260508093000|||||||||1515678901^Afolabi^Segun^MD^^Dr.||||||20260508105500||RAD|F
OBX|1|FT|72125-3^Upper GI Series^LN||UPPER GI SERIES\.br\\.br\CLINICAL HISTORY: Dysphagia and heartburn.\.br\\.br\TECHNIQUE: Single contrast upper GI series with barium.\.br\\.br\FINDINGS:\.br\SWALLOWING MECHANISM: Normal oropharyngeal phase. No aspiration.\.br\ESOPHAGUS: Normal peristalsis. Small sliding hiatal hernia measuring\.br\approximately 3 cm. No stricture or mass. Mild gastroesophageal reflux\.br\observed in supine position.\.br\STOMACH: Normal mucosal pattern. No ulcer crater or mass.\.br\DUODENUM: Normal duodenal bulb and loop. No obstruction.\.br\\.br\IMPRESSION:\.br\1. Small sliding hiatal hernia with mild GE reflux.\.br\2. Otherwise normal upper GI series.\.br\\.br\Electronically signed by: Segun Afolabi, MD\.br\Date: 05/08/2026 10:55||||||F|||20260508105500
```

---

## 16. ADT^A03 - Discharge notification closing radiology encounter at VCU

```
MSH|^~\&|VCU_ADT|VCU_MEDICAL|POWERSCRIBE|VCU_RAD|20260509170000||ADT^A03^ADT_A03|ADT20260509170000016|P|2.5.1|||AL|NE
EVN|A03|20260509170000|||DR_PETROV^Andrei^Petrov^MD
PID|1||MRN20034567^^^VCU^MR||OGLETREE^Tamara^Renee||19840917|F||2054-5^Black or African American^CDCREC|3518 Brook Rd^^Richmond^VA^23227^US||^PRN^PH^^^804^5557284||S||ACCT20260508022|534-66-9178|||N^Non-Hispanic^HL70189
PV1|1|I|NEURO^204^A^VCU_MEDICAL||||3333456789^Petrov^Andrei^MD^^Dr.||4444567890^Castellano^Sofia^MD^^Dr.|NEU||||ADM|||3333456789^Petrov^Andrei^MD^^Dr.|IN||||||||||||||||||DC||A|||20260507100000|20260509170000
DG1|1||D43.1^Neoplasm of uncertain behavior of brain, supratentorial^I10|||A
```

---

## 17. ORU^R01 - Nuclear medicine thyroid scan from Augusta Health

```
MSH|^~\&|POWERSCRIBE|AUGUSTA_RAD|AUGUSTA_RIS|AUGUSTA_HEALTH|20260509143000||ORU^R01^ORU_R01|PS20260509143000017|P|2.5.1|||AL|NE
PID|1||MRN20167890^^^AUGUSTA^MR||MCALLISTER^Fern^Rose||19700818|F||2106-3^White^CDCREC|1025 Greenville Ave^^Staunton^VA^24401^US||^PRN^PH^^^540^5552638||M||ACCT20260509035|978-11-4523|||N^Non-Hispanic^HL70189
PV1|1|O|RAD^NM1^A^AUGUSTA_HEALTH||||1616789012^Vasquez^Ramon^MD^^Dr.|||RAD||||PHY
ORC|RE|ORD20260509017|RAD20260509017||CM||||20260509130000|||1616789012^Vasquez^Ramon^MD^^Dr.
OBR|1|ORD20260509017|RAD20260509017|39812-5^Thyroid scan with uptake^LN|||20260509110000|||||||||1616789012^Vasquez^Ramon^MD^^Dr.||||||20260509142500||RAD|F
OBX|1|FT|39812-5^Thyroid scan with uptake^LN||THYROID SCAN WITH UPTAKE\.br\\.br\CLINICAL HISTORY: Hyperthyroidism, weight loss, tremor.\.br\\.br\TECHNIQUE: 10 mCi Tc-99m pertechnetate IV. Planar images of the thyroid\.br\obtained at 20 minutes.\.br\\.br\FINDINGS:\.br\The thyroid gland is diffusely enlarged. Tracer uptake is diffusely\.br\increased and homogeneous throughout both lobes. No focal cold or hot\.br\nodules identified. 24-hour I-123 uptake: 58% (normal 10-30%).\.br\\.br\IMPRESSION:\.br\Diffusely enlarged thyroid with markedly elevated uptake, consistent\.br\with Graves disease.\.br\\.br\Electronically signed by: Ramon Vasquez, MD\.br\Date: 05/09/2026 14:25||||||F|||20260509142500
```

---

## 18. ACK - Acknowledgment for ORU result delivery

```
MSH|^~\&|INOVA_RIS|INOVA_FAIRFAX|POWERSCRIBE|INOVA_RAD|20260509083005||ACK^R01^ACK|ACK20260509083005001|P|2.5.1|||AL|NE
MSA|AA|PS20260509083000001||
```

---

## 19. MDM^T02 - Radiology addendum notification from Sentara

```
MSH|^~\&|POWERSCRIBE|SENTARA_RAD|SENTARA_RIS|SENTARA_NORFOLK|20260509153000||MDM^T02^MDM_T02|PS20260509153000019|P|2.5.1|||AL|NE
EVN|T02|20260509153000
PID|1||MRN20023456^^^SENTARA^MR||PHAM^Quang^Duc^^Mr.||19790823|M||2028-9^Asian^CDCREC|941 W 21st St^^Norfolk^VA^23517^US||^PRN^PH^^^757^5556193||M||ACCT20260509021|423-55-8967|||N^Non-Hispanic^HL70189
PV1|1|O|RAD^CT1^A^SENTARA_NORFOLK||||2222345678^Subramaniam^Meera^MD^^Dr.|||RAD||||PHY
TXA|1|ADDENDUM^Addendum^HL70270|TX^Text^HL70191||20260509152800|||||2222345678^Subramaniam^Meera^MD^^Dr.|||||AU^Authenticated^HL70271||AV^Available^HL70273
OBX|1|ST|18782-3^Radiology study observation^LN||ADDENDUM to CT Abdomen and Pelvis dated 05/09/2026: Upon further review with surgery team, periappendiceal abscess component measuring 2.1 cm is also noted adjacent to the inflamed appendix tip. Recommend IV antibiotics prior to surgical intervention. - Meera Subramaniam, MD||||||F
```

---

## 20. ADT^A08 - Patient update at Bon Secours triggering worklist refresh

```
MSH|^~\&|BS_ADT|BS_STMARYS|POWERSCRIBE|BS_RAD|20260509161500||ADT^A08^ADT_A01|ADT20260509161500020|P|2.5.1|||AL|NE
EVN|A08|20260509161500|||CLERK_BROOKS^Amy^Brooks
PID|1||MRN20101234^^^BONSECOURS^MR||LATTIMORE^Curtis^Joseph||19710405|M||2106-3^White^CDCREC|7115 Forest Ave^^Richmond^VA^23226^US||^PRN^PH^^^804^5555962|^WPN^PH^^^804^5500456||M||ACCT20260509029|312-44-7856|||N^Non-Hispanic^HL70189
PV1|1|O|RAD^MRI2^A^BS_STMARYS||||1111234567^Subramaniam^Venkat^MD^^Dr.|||RAD||||PHY
IN1|1|AETNA_VA^Aetna Virginia|78901|Aetna|151 Farmington Ave^^Hartford^CT^06156||GRP-AET8899|||||||LATTIMORE^Curtis^Joseph|SEL|19710405|7115 Forest Ave^^Richmond^VA^23226^US|||||||||||||||||AET-VA-334455
```
