# Nuance PowerScribe - real HL7v2 ER7 messages

---

## 1. ORU^R01 - CT head without contrast final report

```
MSH|^~\&|POWERSCRIBE|CCF^2.16.840.1.113883.3.3225^ISO|RIS_RECV|OH_HIE|20260502091200||ORU^R01^ORU_R01|PS20260502091200001|P|2.5.1|||AL|NE
PID|1||MRN7012345^^^CCF^MR||Blackwell^Denise^Yvonne^^Mrs.^||19671023|F||2106-3^White^CDCREC|4718 Superior Ave^^Cleveland^OH^44103^US^H||^PRN^PH^^1^216^5529184|||M^Married^HL70002|||298-41-6753|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^CT01^01^CCF^^^^N|R^Routine^HL70007|||1834926750^Raghavan^Anil^K^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260502001^^^CCF^VN
ORC|RE|ORD80001^RIS|FIL80001^PSCRIBE||CM^Complete^HL70038|||20260502080000|||1834926750^Raghavan^Anil^K^^^MD^^^^NPI
OBR|1|ORD80001^RIS|FIL80001^PSCRIBE|70450^CT head without contrast^CPT4|||20260502080000|||||||||1834926750^Raghavan^Anil^K^^^MD^^^^NPI||||||20260502091000|||F
OBX|1|FT|18747-6^CT Report^LN||EXAM: CT HEAD WITHOUT CONTRAST\.br\\.br\CLINICAL INDICATION: Acute onset headache, rule out intracranial hemorrhage\.br\\.br\COMPARISON: MRI brain dated 2025-11-14\.br\\.br\TECHNIQUE: Helical CT of the head was performed without intravenous contrast.\.br\\.br\FINDINGS:\.br\No acute intracranial hemorrhage, mass effect, or midline shift. The ventricles and sulci are normal in size and configuration for age. Gray-white matter differentiation is preserved. No extra-axial fluid collection. The visualized paranasal sinuses and mastoid air cells are clear. Osseous structures are intact.\.br\\.br\IMPRESSION:\.br\1. No acute intracranial abnormality.\.br\2. No evidence of hemorrhage or mass effect.||||||F|||20260502091000
OBX|2|FT|18747-6^CT Report Addendum^LN||Electronically signed by: Anil K. Raghavan, MD\.br\Cleveland Clinic Foundation, Department of Radiology\.br\9500 Euclid Ave, Cleveland, OH 44195\.br\Dictated via Nuance PowerScribe 360||||||F|||20260502091200
```

---

## 2. ORU^R01 - Chest X-ray two views final report

```
MSH|^~\&|NUANCE_PS|OSUWMC^2.16.840.1.113883.3.6140^ISO|RIS_RECV|OH_HIE|20260503102045||ORU^R01^ORU_R01|PS20260503102045002|P|2.5.1|||AL|NE
PID|1||MRN8023456^^^OSUWMC^MR||Carter^Darnell^Lamont^^Mr.^||19810315|M||2054-5^Black or African American^CDCREC|1192 Indianola Ave^^Columbus^OH^43201^US^H||^PRN^PH^^1^614^5523871|||S^Single^HL70002|||417-63-8290|||N^Not Hispanic or Latino^CDCREC
PV1|1|E|ED^RAD02^01^OSUWMC^^^^N|E^Emergency^HL70007|||2491378056^Ito^Kenji^T^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260503002^^^OSUWMC^VN
ORC|RE|ORD80002^RIS|FIL80002^PSCRIBE||CM^Complete^HL70038|||20260503093000|||2491378056^Ito^Kenji^T^^^MD^^^^NPI
OBR|1|ORD80002^RIS|FIL80002^PSCRIBE|71046^Chest X-ray 2 views^CPT4|||20260503093000|||||||||2491378056^Ito^Kenji^T^^^MD^^^^NPI||||||20260503101500|||F
OBX|1|FT|18748-4^Chest X-ray Report^LN||EXAM: CHEST X-RAY PA AND LATERAL\.br\\.br\CLINICAL INDICATION: Cough and fever for 5 days, rule out pneumonia\.br\\.br\COMPARISON: None available\.br\\.br\FINDINGS:\.br\Heart size is normal. The mediastinal contours are unremarkable. There is patchy airspace opacity in the right lower lobe consistent with consolidation. No pleural effusion or pneumothorax. The left lung is clear. No osseous abnormality identified.\.br\\.br\IMPRESSION:\.br\1. Right lower lobe consolidation, compatible with pneumonia in the appropriate clinical setting.\.br\2. No pleural effusion or pneumothorax.||||||F|||20260503101500
OBX|2|FT|18748-4^Chest X-ray Signature^LN||Electronically signed by: Kenji T. Ito, MD\.br\OSU Wexner Medical Center, Department of Radiology\.br\410 W 10th Ave, Columbus, OH 43210\.br\Dictated via Nuance PowerScribe||||||F|||20260503102045
```

---

## 3. ORU^R01 - MRI lumbar spine with and without contrast

```
MSH|^~\&|PSCRIBE360|UH^2.16.840.1.113883.3.7890^ISO|RIS_RECV|OH_HIE|20260504143322||ORU^R01^ORU_R01|PS20260504143322003|P|2.5.1|||AL|NE
PID|1||MRN9034567^^^UH^MR||Adewale^Tokunbo^Olumide^^Mr.^||19750829|M||2054-5^Black or African American^CDCREC|2580 Noble Rd^^Cleveland^OH^44121^US^H||^PRN^PH^^1^216^5527412|||M^Married^HL70002|||538-72-4901|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^MRI03^01^UH^^^^N|R^Routine^HL70007|||3019847562^Lindstrom^Karen^E^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260504003^^^UH^VN
ORC|RE|ORD80003^RIS|FIL80003^PSCRIBE||CM^Complete^HL70038|||20260504130000|||3019847562^Lindstrom^Karen^E^^^MD^^^^NPI
OBR|1|ORD80003^RIS|FIL80003^PSCRIBE|72148^MRI lumbar spine without contrast^CPT4~72149^MRI lumbar spine with contrast^CPT4|||20260504130000|||||||||3019847562^Lindstrom^Karen^E^^^MD^^^^NPI||||||20260504142500|||F
OBX|1|FT|18747-6^MRI Report^LN||EXAM: MRI LUMBAR SPINE WITHOUT AND WITH CONTRAST\.br\\.br\CLINICAL INDICATION: Low back pain radiating to left leg for 6 weeks, rule out disc herniation\.br\\.br\COMPARISON: CT lumbar spine dated 2025-09-20\.br\\.br\TECHNIQUE: Multiplanar, multisequence MRI of the lumbar spine was performed without and with intravenous gadolinium contrast.\.br\\.br\FINDINGS:\.br\L3-L4: Mild disc bulge without significant central canal stenosis. Mild bilateral facet arthropathy.\.br\L4-L5: Broad-based disc protrusion with left paracentral component measuring 6 mm, causing moderate left lateral recess stenosis and impingement on the traversing left L5 nerve root. Moderate bilateral facet arthropathy with ligamentum flavum hypertrophy.\.br\L5-S1: Mild disc desiccation without significant herniation. Mild bilateral facet arthropathy.\.br\Conus medullaris terminates at the L1-L2 level and is normal in signal. No abnormal enhancement.\.br\\.br\IMPRESSION:\.br\1. L4-L5 broad-based disc protrusion with left paracentral component causing moderate left lateral recess stenosis and left L5 nerve root impingement. This correlates with the patient's left-sided radiculopathy.\.br\2. Multilevel degenerative changes as described above.\.br\3. No evidence of infection, neoplasm, or compression fracture.||||||F|||20260504142500
OBX|2|FT|18747-6^MRI Signature^LN||Electronically signed by: Karen E. Lindstrom, MD\.br\University Hospitals Cleveland Medical Center\.br\11100 Euclid Ave, Cleveland, OH 44106\.br\Dictated via Nuance PowerScribe 360||||||F|||20260504143322
```

---

## 4. ORM^O01 - CT chest with contrast order for pulmonary embolism

```
MSH|^~\&|POWERSCRIBE|OHIOHEALTH^2.16.840.1.113883.3.5501^ISO|RIS_RECV|OH_HIE|20260505081530||ORM^O01^ORM_O01|PS20260505081530004|P|2.5.1|||AL|NE
PID|1||MRN1045678^^^OHRVMC^MR||Novotny^Patricia^Elaine^^Mrs.^||19590218|F||2106-3^White^CDCREC|3821 Riverside Dr^^Columbus^OH^43221^US^H||^PRN^PH^^1^614^5528923|||W^Widowed^HL70002|||641-83-7012|||N^Not Hispanic or Latino^CDCREC
PV1|1|E|ED^RAD04^01^OHRVMC^^^^N|E^Emergency^HL70007|||4182739560^Dominguez^Hector^D^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260505004^^^OHRVMC^VN
ORC|NW|ORD80004^RIS||GRP80004^RIS|||||20260505080000|||4182739560^Dominguez^Hector^D^^^MD^^^^NPI|||||OHRVMC^OhioHealth Riverside Methodist Hospital
OBR|1|ORD80004^RIS||71275^CT angiography chest^CPT4|||20260505080000||||||||4182739560^Dominguez^Hector^D^^^MD^^^^NPI||||||||||1^STAT^HL70065
DG1|1||I26.99^Other pulmonary embolism without acute cor pulmonale^I10||20260505|A
NTE|1||66-year-old female presenting with acute onset dyspnea and pleuritic chest pain. D-dimer elevated at 2.4 mcg/mL. STAT CTA chest for PE evaluation.
```

---

## 5. ORU^R01 - CT abdomen pelvis with contrast final report

```
MSH|^~\&|NUANCE_PS|PROMEDICA^2.16.840.1.113883.3.6620^ISO|RIS_RECV|OH_HIE|20260505153010||ORU^R01^ORU_R01|PS20260505153010005|P|2.5.1|||AL|NE
PID|1||MRN2056789^^^PTMC^MR||Saleem^Nadia^Fatima^^Ms.^||19880611|F||2106-3^White^CDCREC|3417 Monroe St^^Toledo^OH^43606^US^H||^PRN^PH^^1^419^5523647|||S^Single^HL70002|||762-94-3018|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^CT05^01^PTMC^^^^N|R^Routine^HL70007|||5293814076^Landers^Gregory^M^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260505005^^^PTMC^VN
ORC|RE|ORD80005^RIS|FIL80005^PSCRIBE||CM^Complete^HL70038|||20260505140000|||5293814076^Landers^Gregory^M^^^MD^^^^NPI
OBR|1|ORD80005^RIS|FIL80005^PSCRIBE|74178^CT abdomen and pelvis with contrast^CPT4|||20260505140000|||||||||5293814076^Landers^Gregory^M^^^MD^^^^NPI||||||20260505152500|||F
OBX|1|FT|18747-6^CT Report^LN||EXAM: CT ABDOMEN AND PELVIS WITH IV CONTRAST\.br\\.br\CLINICAL INDICATION: Right lower quadrant pain for 2 days with nausea\.br\\.br\COMPARISON: None\.br\\.br\TECHNIQUE: Helical CT of the abdomen and pelvis was performed with intravenous contrast in the portal venous phase.\.br\\.br\FINDINGS:\.br\ABDOMEN: Liver, gallbladder, spleen, pancreas, and adrenal glands are unremarkable. Kidneys enhance symmetrically without hydronephrosis or calculi. No free fluid.\.br\PELVIS: The appendix measures 11 mm in diameter with periappendiceal fat stranding and a 5 mm appendicolith at the base. Adjacent reactive mesenteric lymphadenopathy. No free air. Uterus and adnexa are unremarkable.\.br\\.br\IMPRESSION:\.br\1. Acute appendicitis with appendicolith. Surgical consultation recommended.\.br\2. No evidence of perforation or abscess formation.||||||F|||20260505152500
OBX|2|FT|18747-6^CT Signature^LN||Electronically signed by: Gregory M. Landers, MD\.br\ProMedica Toledo Hospital, Department of Radiology\.br\2142 N Cove Blvd, Toledo, OH 43606\.br\Dictated via Nuance PowerScribe||||||F|||20260505153010
```

---

## 6. MDM^T02 - Radiology report document notification for ultrasound abdomen

```
MSH|^~\&|POWERSCRIBE|CCF^2.16.840.1.113883.3.3225^ISO|EHR_RECV|OH_HIE|20260506111500||MDM^T02^MDM_T02|PS20260506111500006|P|2.5.1|||AL|NE
EVN|T02|20260506111500
PID|1||MRN3067890^^^CCF^MR||Kovalenko^Dmitri^Aleksandrovich^^Mr.^||19700404|M||2106-3^White^CDCREC|1485 E 9th St^^Cleveland^OH^44114^US^H||^PRN^PH^^1^216^5524193|||M^Married^HL70002|||873-06-9234|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^US06^01^CCF^^^^N|R^Routine^HL70007|||6104852739^Chow^Vivian^W^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260506006^^^CCF^VN
TXA|1|RAD^Radiology Report|TX|20260506110000||20260506111500|||||6104852739^Chow^Vivian^W^^^MD^^^^NPI|DOC90001^^CCF|||||AU^Authenticated^HL70271
OBX|1|FT|18747-6^US Report^LN||EXAM: ULTRASOUND ABDOMEN COMPLETE\.br\\.br\CLINICAL INDICATION: Elevated liver enzymes, rule out hepatobiliary pathology\.br\\.br\COMPARISON: None\.br\\.br\FINDINGS:\.br\LIVER: Mildly increased echogenicity consistent with hepatic steatosis. No focal hepatic lesion. The liver measures 17.2 cm in craniocaudal dimension.\.br\GALLBLADDER: Multiple gallstones, the largest measuring 12 mm. No gallbladder wall thickening or pericholecystic fluid. No sonographic Murphy sign.\.br\COMMON BILE DUCT: 4 mm, within normal limits.\.br\PANCREAS: Partially obscured by bowel gas but visualized portions are unremarkable.\.br\SPLEEN: Normal size at 11 cm.\.br\KIDNEYS: Right kidney 10.8 cm, left kidney 11.1 cm. No hydronephrosis or calculi bilaterally.\.br\AORTA: Normal caliber.\.br\\.br\IMPRESSION:\.br\1. Cholelithiasis without evidence of acute cholecystitis.\.br\2. Hepatic steatosis.||||||F|||20260506111500
```

---

## 7. ADT^A04 - Patient registration for outpatient mammogram

```
MSH|^~\&|POWERSCRIBE|KETMC^2.16.840.1.113883.3.8120^ISO|ADT_RECV|OH_HIE|20260506140000||ADT^A04^ADT_A01|PS20260506140000007|P|2.5.1|||AL|NE
EVN|A04|20260506135500|||KWILSON^Wilson^Karen^R^^^RN|20260506135500
PID|1||MRN4078901^^^KETMC^MR||Engel^Theresa^Lorraine^^Mrs.^||19720816|F||2106-3^White^CDCREC|4102 Wilmington Pike^^Kettering^OH^45440^US^H||^PRN^PH^^1^937^5527621|^WPN^PH^^1^937^5520198||M^Married^HL70002|||984-17-2035|||N^Not Hispanic or Latino^CDCREC
PD1|||Kettering Medical Center^^^^NPI|7293148065^Okafor^Emmanuel^A^^^MD^^^^NPI
NK1|1|Engel^David^Robert^^Mr.|SPO^Spouse^HL70063|4102 Wilmington Pike^^Kettering^OH^45440^US|^PRN^PH^^1^937^5527622||EC^Emergency Contact^HL70131
PV1|1|O|RAD^MAM07^01^KETMC^^^^N|R^Routine^HL70007|||7293148065^Okafor^Emmanuel^A^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260506007^^^KETMC^VN
IN1|1|ANT001|60065^Anthem Blue Cross Blue Shield Ohio|ANTHEM^^Mason^OH^45040|||||GRPABC123||||||Engel^Theresa^Lorraine|SE^Self^HL70063|19720816|4102 Wilmington Pike^^Kettering^OH^45440^US|Y||1||||||||||||||POL334455
```

---

## 8. ADT^A08 - Patient information update for radiology follow-up

```
MSH|^~\&|NUANCE_PS|OSUWMC^2.16.840.1.113883.3.6140^ISO|ADT_RECV|OH_HIE|20260507090000||ADT^A08^ADT_A01|PS20260507090000008|P|2.5.1|||AL|NE
EVN|A08|20260507085500|||DMORRIS^Morris^Donna^S^^^RN|20260507085500
PID|1||MRN5089012^^^OSUWMC^MR||Fuentes^Miguel^Alejandro^^Mr.^||19630927|M||2106-3^White^CDCREC|2738 Summit St^^Columbus^OH^43202^US^H||^PRN^PH^^1^614^5522847|^WPN^PH^^1^614^5529173||M^Married^HL70002|||093-28-4561|||H^Hispanic or Latino^CDCREC
PD1|||OSU Wexner Medical Center^^^^NPI|8475031926^Callahan^Maureen^M^^^MD^^^^NPI
NK1|1|Fuentes^Lucia^Maria^^Mrs.|SPO^Spouse^HL70063|2738 Summit St^^Columbus^OH^43202^US|^PRN^PH^^1^614^5522848||EC^Emergency Contact^HL70131
PV1|1|O|RAD^CT08^01^OSUWMC^^^^N|R^Routine^HL70007|||8475031926^Callahan^Maureen^M^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260507008^^^OSUWMC^VN
IN1|1|UHC001|60054^UnitedHealthcare of Ohio|UHC^^Dublin^OH^43017|||||GRPDEF456||||||Fuentes^Miguel^Alejandro|SE^Self^HL70063|19630927|2738 Summit St^^Columbus^OH^43202^US|Y||1||||||||||||||POL556677
IN2|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||Fuentes^Miguel^Alejandro
```

---

## 9. ORU^R01 - X-ray knee two views with comparison

```
MSH|^~\&|PSCRIBE360|ACMC^2.16.840.1.113883.3.4950^ISO|RIS_RECV|OH_HIE|20260507114530||ORU^R01^ORU_R01|PS20260507114530009|P|2.5.1|||AL|NE
PID|1||MRN6090123^^^ACMC^MR||Franklin^Monique^Renee^^Ms.^||19841107|F||2054-5^Black or African American^CDCREC|1215 Tuscarawas St W^^Canton^OH^44702^US^H||^PRN^PH^^1^330^5528142|||D^Divorced^HL70002|||104-39-7562|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^XR09^01^ACMC^^^^N|R^Routine^HL70007|||9381250476^Bergman^Scott^J^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260507009^^^ACMC^VN
ORC|RE|ORD80009^RIS|FIL80009^PSCRIBE||CM^Complete^HL70038|||20260507103000|||9381250476^Bergman^Scott^J^^^MD^^^^NPI
OBR|1|ORD80009^RIS|FIL80009^PSCRIBE|73562^X-ray knee 3 views^CPT4|||20260507103000|||||||||9381250476^Bergman^Scott^J^^^MD^^^^NPI||||||20260507114000|||F
OBX|1|FT|18747-6^XR Report^LN||EXAM: X-RAY LEFT KNEE TWO VIEWS\.br\\.br\CLINICAL INDICATION: Chronic left knee pain, evaluate for osteoarthritis\.br\\.br\COMPARISON: X-ray left knee dated 2025-06-10\.br\\.br\FINDINGS:\.br\Moderate narrowing of the medial joint compartment with subchondral sclerosis. Small marginal osteophytes at the medial tibial plateau and medial femoral condyle. Mild narrowing of the patellofemoral compartment. No joint effusion. No acute fracture or dislocation. Soft tissues are unremarkable.\.br\\.br\IMPRESSION:\.br\1. Moderate medial compartment osteoarthritis of the left knee, progressed compared to prior study.\.br\2. Mild patellofemoral degenerative changes.||||||F|||20260507114000
OBX|2|FT|18747-6^XR Signature^LN||Electronically signed by: Scott J. Bergman, MD\.br\Aultman Medical Center, Department of Radiology\.br\2600 Sixth St SW, Canton, OH 44710\.br\Dictated via Nuance PowerScribe 360||||||F|||20260507114530
```

---

## 10. ORM^O01 - MRI brain with and without contrast order

```
MSH|^~\&|POWERSCRIBE|UH^2.16.840.1.113883.3.7890^ISO|RIS_RECV|OH_HIE|20260507161000||ORM^O01^ORM_O01|PS20260507161000010|P|2.5.1|||AL|NE
PID|1||MRN7101234^^^UH^MR||Yoon^Minji^Sooyoung^^Ms.^||19920514|F||2028-9^Asian^CDCREC|8134 Chagrin Blvd^^Chagrin Falls^OH^44023^US^H||^PRN^PH^^1^440^5529381|||S^Single^HL70002|||214-49-5073|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^MRI10^01^UH^^^^N|U^Urgent^HL70007|||0572914836^Voss^Jennifer^L^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260507010^^^UH^VN
ORC|NW|ORD80010^RIS||GRP80010^RIS|||||20260507155000|||0572914836^Voss^Jennifer^L^^^MD^^^^NPI|||||UH^University Hospitals Cleveland Medical Center
OBR|1|ORD80010^RIS||70553^MRI brain with and without contrast^CPT4|||20260507155000||||||||0572914836^Voss^Jennifer^L^^^MD^^^^NPI||||||||||2^Urgent^HL70065
DG1|1||G43.909^Migraine unspecified not intractable without status migrainosus^I10||20260507|A
NTE|1||30-year-old female with new onset severe headaches and visual disturbance. Papilledema noted on fundoscopic exam. Urgent MRI to evaluate for intracranial mass or idiopathic intracranial hypertension.
```

---

## 11. ORU^R01 - Mammogram bilateral screening final report

```
MSH|^~\&|NUANCE_PS|KETMC^2.16.840.1.113883.3.8120^ISO|RIS_RECV|OH_HIE|20260508083000||ORU^R01^ORU_R01|PS20260508083000011|P|2.5.1|||AL|NE
PID|1||MRN8112345^^^KETMC^MR||Okafor^Chidinma^Amaka^^Mrs.^||19770320|F||2054-5^Black or African American^CDCREC|5419 Salem Ave^^Dayton^OH^45426^US^H||^PRN^PH^^1^937^5526283|||M^Married^HL70002|||318-52-6047|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^MAM11^01^KETMC^^^^N|R^Routine^HL70007|||1728304955^Nguyen^Thanh^N^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260508011^^^KETMC^VN
ORC|RE|ORD80011^RIS|FIL80011^PSCRIBE||CM^Complete^HL70038|||20260508070000|||1728304955^Nguyen^Thanh^N^^^MD^^^^NPI
OBR|1|ORD80011^RIS|FIL80011^PSCRIBE|77067^Screening mammography bilateral^CPT4|||20260508070000|||||||||1728304955^Nguyen^Thanh^N^^^MD^^^^NPI||||||20260508082500|||F
OBX|1|FT|18747-6^Mammography Report^LN||EXAM: SCREENING MAMMOGRAPHY BILATERAL\.br\\.br\CLINICAL INDICATION: Routine screening mammography, age 49\.br\\.br\COMPARISON: Screening mammography dated 2025-05-12\.br\\.br\BREAST COMPOSITION: Heterogeneously dense, which may obscure small masses (ACR density category C).\.br\\.br\FINDINGS:\.br\RIGHT BREAST: No suspicious mass, architectural distortion, or suspicious calcifications. Benign-appearing calcifications in the upper outer quadrant, stable.\.br\LEFT BREAST: No suspicious mass, architectural distortion, or suspicious calcifications.\.br\\.br\IMPRESSION:\.br\BI-RADS 1: Negative. Recommend routine screening in 1 year.\.br\\.br\A letter has been mailed to the patient regarding results.||||||F|||20260508082500
OBX|2|FT|18747-6^Mammography Signature^LN||Electronically signed by: Thanh N. Nguyen, MD\.br\Kettering Medical Center, Breast Imaging Center\.br\3535 Southern Blvd, Kettering, OH 45429\.br\Dictated via Nuance PowerScribe||||||F|||20260508083000
```

---

## 12. ORU^R01 - CT chest abdomen pelvis with contrast with ED segment containing base64 PDF report

```
MSH|^~\&|POWERSCRIBE|CCF^2.16.840.1.113883.3.3225^ISO|EHR_RECV|OH_HIE|20260508141200||ORU^R01^ORU_R01|PS20260508141200012|P|2.5.1|||AL|NE
PID|1||MRN9123456^^^CCF^MR||Kowalczyk^Stanley^Raymond^^Mr.^||19530722|M||2106-3^White^CDCREC|16205 Waterloo Rd^^Cleveland^OH^44110^US^H||^PRN^PH^^1^216^5523960|||M^Married^HL70002|||429-61-8793|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|ONC^3401^01^CCF^^^^N|U^Urgent^HL70007|||2647193058^Desai^Priya^S^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260508012^^^CCF^VN
ORC|RE|ORD80012^RIS|FIL80012^PSCRIBE||CM^Complete^HL70038|||20260508120000|||2647193058^Desai^Priya^S^^^MD^^^^NPI
OBR|1|ORD80012^RIS|FIL80012^PSCRIBE|74178^CT chest abdomen pelvis with contrast^CPT4|||20260508120000|||||||||2647193058^Desai^Priya^S^^^MD^^^^NPI||||||20260508140500|||F
OBX|1|ED|PDF^Radiology Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjUNCjEgMCBvYmoNCjw8DQovVHlwZSAvQ2F0YWxvZw0KL1BhZ2VzIDIgMCBSDQo+Pg0KZW5kb2JqDQoyIDAgb2JqDQo8PA0KL1R5cGUgL1BhZ2VzDQovS2lkcyBbMyAwIFJdDQovQ291bnQgMQ0KL01lZGlhQm94IFswIDAgNjEyIDc5Ml0NCj4+DQplbmRvYmoNCjMgMCBvYmoNCjw8DQovVHlwZSAvUGFnZQ0KL1BhcmVudCAyIDAgUg0KL0NvbnRlbnRzIDQgMCBSDQovUmVzb3VyY2VzIDw8IC9Gb250IDw8IC9GMSA1IDAgUiA+PiA+Pg0KPj4NCmVuZG9iag0KNCAwIG9iag0KPDwNCi9MZW5ndGggMzUwDQo+Pg0Kc3RyZWFtDQpCVA0KL0YxIDE0IFRmDQo1MCA3NDAgVGQNCihDVCBDaGVzdCBBYmRvbWVuIFBlbHZpcyBXaXRoIENvbnRyYXN0KSBUag0KMCAtMjAgVGQNCi9GMSAxMCBUZg0KKFBhdGllbnQ6IFRob21wc29uLCBHZXJhbGQgVykgVGoNCjAgLTIwIFRkDQooTVJOOiA5MTIzNDU2ICAgRE9COiAwNy8yMi8xOTUzKSBUag0KMCAtMzAgVGQNCi9GMSAxMiBUZg0KKEZJTkRJTkdTOikgVGoNCjAgLTIwIFRkDQovRjEgMTAgVGYNCihDaGVzdDogMi4xIGNtIHNwaWN1bGF0ZWQgbm9kdWxlIHJpZ2h0IHVwcGVyIGxvYmUuKSBUag0KMCAtMjAgVGQNCihNZWRpYXN0aW51bTogU3VicGVjdG9yYWwgbHltcGhhZGVub3BhdGh5LikgVGoNCjAgLTIwIFRkDQooQWJkb21lbjogTm8gaGVwYXRpYyBtZXRhc3Rhc2VzLikgVGoNCjAgLTMwIFRkDQooSU1QUkVTU0lPTjogU3VzcGljaW91cyBSSUwgbm9kdWxlLikgVGoNCkVUDQplbmRzdHJlYW0NCmVuZG9iag0KNSAwIG9iag0KPDwNCi9UeXBlIC9Gb250DQovU3VidHlwZSAvVHlwZTENCi9CYXNlRm9udCAvSGVsdmV0aWNhDQo+Pg0KZW5kb2JqDQp4cmVmDQowIDYNCjAwMDAwMDAwMDAgNjU1MzUgZiANCg==||||||F|||20260508140500
OBX|2|FT|18747-6^CT Report^LN||EXAM: CT CHEST ABDOMEN PELVIS WITH IV CONTRAST\.br\\.br\CLINICAL INDICATION: Staging workup for newly diagnosed right upper lobe lung mass\.br\\.br\COMPARISON: CT chest dated 2026-04-15\.br\\.br\FINDINGS:\.br\CHEST: A 2.1 cm spiculated nodule in the right upper lobe, increased from 1.4 cm on prior study. Mediastinal lymphadenopathy with a 1.5 cm subcarinal node and 1.2 cm right hilar node. No pleural effusion. Heart size normal.\.br\ABDOMEN: Liver, spleen, pancreas, and adrenal glands unremarkable. No hepatic metastases. Kidneys unremarkable.\.br\PELVIS: No pelvic lymphadenopathy. Bladder and prostate are unremarkable.\.br\BONES: No suspicious osseous lesions.\.br\\.br\IMPRESSION:\.br\1. Enlarging 2.1 cm spiculated right upper lobe nodule, highly suspicious for primary lung malignancy. Recommend tissue sampling.\.br\2. Mediastinal lymphadenopathy concerning for nodal involvement.\.br\3. No evidence of distant metastatic disease.||||||F|||20260508140500
OBX|3|FT|18747-6^CT Signature^LN||Electronically signed by: Priya S. Desai, MD\.br\Cleveland Clinic, Department of Thoracic Radiology\.br\9500 Euclid Ave, Cleveland, OH 44195\.br\Dictated via Nuance PowerScribe 360||||||F|||20260508141200
```

---

## 13. MDM^T02 - Radiology addendum for fluoroscopy-guided lumbar puncture

```
MSH|^~\&|PSCRIBE360|OHIOHEALTH^2.16.840.1.113883.3.5501^ISO|EHR_RECV|OH_HIE|20260508163000||MDM^T02^MDM_T02|PS20260508163000013|P|2.5.1|||AL|NE
EVN|T02|20260508163000
PID|1||MRN0134567^^^OHGMC^MR||Vasquez^Elena^Cristina^^Mrs.^||19780512|F||2106-3^White^CDCREC|1247 Parsons Ave^^Columbus^OH^43206^US^H||^PRN^PH^^1^614^5524837|||M^Married^HL70002|||540-73-1892|||H^Hispanic or Latino^CDCREC
PV1|1|I|NEUR^2105^01^OHGMC^^^^N|U^Urgent^HL70007|||3691527804^Flaherty^Brendan^P^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260508013^^^OHGMC^VN
TXA|1|RAD^Radiology Report Addendum|TX|20260508160000||20260508163000|||||3691527804^Flaherty^Brendan^P^^^MD^^^^NPI|DOC90013^^OHGMC|||||AU^Authenticated^HL70271
OBX|1|FT|18747-6^Fluoro Report^LN||EXAM: FLUOROSCOPY-GUIDED LUMBAR PUNCTURE\.br\\.br\CLINICAL INDICATION: Suspected idiopathic intracranial hypertension, elevated opening pressure on prior LP attempt unsuccessful in ED\.br\\.br\PROCEDURE: After obtaining informed consent, the patient was placed in prone position. Under fluoroscopic guidance, a 22-gauge spinal needle was advanced into the L3-L4 interspinous space using a paramedian approach. CSF was obtained with an opening pressure of 32 cm H2O. A total of 15 mL of CSF was collected and sent for analysis. Closing pressure was 18 cm H2O. The needle was removed and a sterile bandage applied.\.br\\.br\FINDINGS: Opening pressure elevated at 32 cm H2O. CSF was clear and colorless.\.br\\.br\IMPRESSION:\.br\1. Technically successful fluoroscopy-guided lumbar puncture.\.br\2. Elevated opening pressure at 32 cm H2O, consistent with intracranial hypertension.\.br\\.br\ADDENDUM: Patient tolerated the procedure well. No immediate post-procedural complications. The patient has been instructed to remain supine for 2 hours.||||||F|||20260508163000
```

---

## 14. ORM^O01 - Ultrasound-guided thyroid biopsy order

```
MSH|^~\&|NUANCE_PS|SUMMAHEALTH^2.16.840.1.113883.3.7250^ISO|RIS_RECV|OH_HIE|20260509071500||ORM^O01^ORM_O01|PS20260509071500014|P|2.5.1|||AL|NE
PID|1||MRN1145678^^^SHMC^MR||Polanski^Marek^Tadeusz^^Mr.^||19860903|M||2106-3^White^CDCREC|731 E Market St^^Akron^OH^44305^US^H||^PRN^PH^^1^330^5523719|||M^Married^HL70002|||651-84-2913|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^IR14^01^SHMC^^^^N|R^Routine^HL70007|||4019836275^Steinberg^Rachel^A^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260509014^^^SHMC^VN
ORC|NW|ORD80014^RIS||GRP80014^RIS|||||20260509070000|||4019836275^Steinberg^Rachel^A^^^MD^^^^NPI|||||SHMC^Summa Health System - Akron Campus
OBR|1|ORD80014^RIS||76942^Ultrasound guidance for needle biopsy^CPT4~60100^Thyroid biopsy percutaneous^CPT4|||20260509070000||||||||4019836275^Steinberg^Rachel^A^^^MD^^^^NPI||||||||||1^Routine^HL70065
DG1|1||E04.1^Nontoxic single thyroid nodule^I10||20260509|A
NTE|1||1.8 cm solid hypoechoic nodule in the right thyroid lobe with irregular margins and microcalcifications (TI-RADS 5). FNA biopsy recommended per ACR guidelines.
```

---

## 15. ORU^R01 - CT angiography chest PE study with ED segment containing base64 PDF

```
MSH|^~\&|POWERSCRIBE|OHRVMC^2.16.840.1.113883.3.5501^ISO|EHR_RECV|OH_HIE|20260509101500||ORU^R01^ORU_R01|PS20260509101500015|P|2.5.1|||AL|NE
PID|1||MRN2156789^^^OHRVMC^MR||Caldwell^Howard^Eugene^^Mr.^||19470310|M||2106-3^White^CDCREC|5813 E Main St^^Columbus^OH^43213^US^H||^PRN^PH^^1^614^5528472|||W^Widowed^HL70002|||762-95-4018|||N^Not Hispanic or Latino^CDCREC
PV1|1|E|ED^CT15^01^OHRVMC^^^^N|E^Emergency^HL70007|||5174926308^Espinoza^Sandra^C^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260509015^^^OHRVMC^VN
ORC|RE|ORD80015^RIS|FIL80015^PSCRIBE||CM^Complete^HL70038|||20260509090000|||5174926308^Espinoza^Sandra^C^^^MD^^^^NPI
OBR|1|ORD80015^RIS|FIL80015^PSCRIBE|71275^CT angiography chest^CPT4|||20260509090000|||||||||5174926308^Espinoza^Sandra^C^^^MD^^^^NPI||||||20260509101000|||F
OBX|1|ED|PDF^Radiology Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjQNCjEgMCBvYmoNCjw8DQovVHlwZSAvQ2F0YWxvZw0KL1BhZ2VzIDIgMCBSDQo+Pg0KZW5kb2JqDQoyIDAgb2JqDQo8PA0KL1R5cGUgL1BhZ2VzDQovS2lkcyBbMyAwIFJdDQovQ291bnQgMQ0KL01lZGlhQm94IFswIDAgNjEyIDc5Ml0NCj4+DQplbmRvYmoNCjMgMCBvYmoNCjw8DQovVHlwZSAvUGFnZQ0KL1BhcmVudCAyIDAgUg0KL0NvbnRlbnRzIDQgMCBSDQovUmVzb3VyY2VzIDw8IC9Gb250IDw8IC9GMSA1IDAgUiA+PiA+Pg0KPj4NCmVuZG9iag0KNCAwIG9iag0KPDwNCi9MZW5ndGggNDIwDQo+Pg0Kc3RyZWFtDQpCVA0KL0YxIDE0IFRmDQo1MCA3NDAgVGQNCihDVCBBbmdpb2dyYXBoeSBDaGVzdCAtIFBFIFN0dWR5KSBUag0KMCAtMjAgVGQNCi9GMSAxMCBUZg0KKFBhdGllbnQ6IEJha2VyLCBUaG9tYXMgRSkgVGoNCjAgLTIwIFRkDQooTVJOOiAyMTU2Nzg5ICAgRE9COiAwMy8xMC8xOTQ3KSBUag0KMCAtMzAgVGQNCi9GMSAxMiBUZg0KKEZJTkRJTkdTOikgVGoNCjAgLTIwIFRkDQovRjEgMTAgVGYNCihCaWxhdGVyYWwgcHVsbW9uYXJ5IGVtYm9saSBpZGVudGlmaWVkLikgVGoNCjAgLTIwIFRkDQooU2FkZGxlIGVtYm9sdXMgYXQgbWFpbiBQQSBiaWZ1cmNhdGlvbi4pIFRqDQowIC0yMCBUZA0KKFJWIHRvIExWIHJhdGlvOiAxLjQgc3VnZ2VzdGluZyBSSCBzdHJhaW4uKSBUag0KMCAtMzAgVGQNCihJTVBSRVNTSU9OOiBBY3V0ZSBzYWRkbGUgUEUsIFJIIHN0cmFpbi4pIFRqDQpFVA0KZW5kc3RyZWFtDQplbmRvYmoNCjUgMCBvYmoNCjw8DQovVHlwZSAvRm9udA0KL1N1YnR5cGUgL1R5cGUxDQovQmFzZUZvbnQgL0hlbHZldGljYQ0KPj4NCmVuZG9iag0KeHJlZg0KMCAxDQowMDAwMDAwMDAwIDY1NTM1IGYgDQo=||||||F|||20260509101000
OBX|2|FT|18747-6^CTA Report^LN||EXAM: CT ANGIOGRAPHY CHEST (PE PROTOCOL)\.br\\.br\CLINICAL INDICATION: 79-year-old male with acute dyspnea and tachycardia, D-dimer 4.8 mcg/mL\.br\\.br\COMPARISON: CT chest dated 2026-01-20\.br\\.br\TECHNIQUE: CT angiography of the chest performed with 80 mL Omnipaque 350 via power injection at 4 mL/sec using bolus tracking technique.\.br\\.br\FINDINGS:\.br\PULMONARY ARTERIES: Large saddle embolus at the main pulmonary artery bifurcation extending into bilateral main, lobar, and segmental pulmonary arteries. Near-complete occlusion of the right lower lobe segmental arteries.\.br\HEART: Right ventricle to left ventricle ratio of 1.4, suggesting right heart strain. Interventricular septum bowing toward the left ventricle. Reflux of contrast into the hepatic veins and IVC.\.br\LUNGS: Peripheral wedge-shaped opacities in the right lower lobe suggestive of pulmonary infarction. No pneumothorax.\.br\PLEURA: Small right-sided pleural effusion.\.br\\.br\IMPRESSION:\.br\1. Acute saddle pulmonary embolus with extensive bilateral clot burden.\.br\2. Signs of right heart strain with RV/LV ratio of 1.4.\.br\3. Probable right lower lobe pulmonary infarction.\.br\4. CRITICAL RESULT communicated to Dr. Dominguez by telephone at 10:05 AM.||||||F|||20260509101000
OBX|3|FT|18747-6^CTA Signature^LN||Electronically signed by: Sandra C. Espinoza, MD\.br\OhioHealth Riverside Methodist Hospital, Department of Radiology\.br\3535 Olentangy River Rd, Columbus, OH 43214\.br\Dictated via Nuance PowerScribe 360||||||F|||20260509101500
```

---

## 16. ADT^A04 - Patient registration for outpatient PET-CT

```
MSH|^~\&|PSCRIBE360|OSUWMC^2.16.840.1.113883.3.6140^ISO|ADT_RECV|OH_HIE|20260509130000||ADT^A04^ADT_A01|PS20260509130000016|P|2.5.1|||AL|NE
EVN|A04|20260509125500|||LBROWN^Brown^Linda^M^^^RN|20260509125500
PID|1||MRN3167890^^^OSUWMC^MR||Sandhu^Gurmeet^Kaur^^Mrs.^||19650419|F||2028-9^Asian^CDCREC|4782 Kenny Rd^^Columbus^OH^43220^US^H||^PRN^PH^^1^614^5523194|^WPN^PH^^1^614^5520472||M^Married^HL70002|||871-06-4235|||N^Not Hispanic or Latino^CDCREC
PD1|||OSU Wexner Medical Center^^^^NPI|6250481937^Klein^Matthew^J^^^MD^^^^NPI
NK1|1|Sandhu^Ravinder^^Mr.|SPO^Spouse^HL70063|4782 Kenny Rd^^Columbus^OH^43220^US|^PRN^PH^^1^614^5523195||EC^Emergency Contact^HL70131
PV1|1|O|RAD^PET16^01^OSUWMC^^^^N|R^Routine^HL70007|||6250481937^Klein^Matthew^J^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260509016^^^OSUWMC^VN
IN1|1|AET001|60054^Aetna Better Health of Ohio|AETNA^^Blue Ash^OH^45242|||||GRPGHI789||||||Sandhu^Gurmeet^Kaur|SE^Self^HL70063|19650419|4782 Kenny Rd^^Columbus^OH^43220^US|Y||1||||||||||||||POL778899
```

---

## 17. ORU^R01 - Nuclear medicine bone scan whole body final report

```
MSH|^~\&|NUANCE_PS|UCMC^2.16.840.1.113883.3.9430^ISO|RIS_RECV|OH_HIE|20260509152200||ORU^R01^ORU_R01|PS20260509152200017|P|2.5.1|||AL|NE
PID|1||MRN4178901^^^UCMC^MR||Brennan^Patrick^Declan^^Mr.^||19590815|M||2106-3^White^CDCREC|4419 Vine St^^Cincinnati^OH^45217^US^H||^PRN^PH^^1^513^5527841|||M^Married^HL70002|||982-17-5346|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^NM17^01^UCMC^^^^N|R^Routine^HL70007|||7052948316^Castillo^Alejandra^M^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260509017^^^UCMC^VN
ORC|RE|ORD80017^RIS|FIL80017^PSCRIBE||CM^Complete^HL70038|||20260509130000|||7052948316^Castillo^Alejandra^M^^^MD^^^^NPI
OBR|1|ORD80017^RIS|FIL80017^PSCRIBE|78300^Bone scan whole body^CPT4|||20260509130000|||||||||7052948316^Castillo^Alejandra^M^^^MD^^^^NPI||||||20260509151500|||F
OBX|1|FT|18747-6^NM Report^LN||EXAM: WHOLE BODY BONE SCAN\.br\\.br\CLINICAL INDICATION: Newly diagnosed prostate cancer, Gleason 4+3, PSA 18.2. Staging evaluation for osseous metastases.\.br\\.br\COMPARISON: None\.br\\.br\TECHNIQUE: Following intravenous administration of 25 mCi Tc-99m MDP, delayed whole body anterior and posterior planar images were obtained at 3 hours.\.br\\.br\FINDINGS:\.br\There is asymmetrically increased radiotracer uptake in the right posterior 8th rib and left sacral ala. Degenerative changes noted in the thoracolumbar spine and bilateral knees with expected uptake patterns. The kidneys are visualized bilaterally with normal excretion. No other focal areas of abnormal uptake.\.br\\.br\IMPRESSION:\.br\1. Focal uptake in the right posterior 8th rib and left sacral ala, indeterminate but suspicious for osseous metastatic disease in the setting of newly diagnosed prostate cancer. Correlation with MRI pelvis or dedicated CT is recommended.\.br\2. Degenerative changes in the thoracolumbar spine and bilateral knees.||||||F|||20260509151500
OBX|2|FT|18747-6^NM Signature^LN||Electronically signed by: Alejandra M. Castillo, MD\.br\University of Cincinnati Medical Center, Department of Nuclear Medicine\.br\234 Goodman St, Cincinnati, OH 45219\.br\Dictated via Nuance PowerScribe||||||F|||20260509152200
```

---

## 18. MDM^T02 - Interventional radiology procedure note for port placement

```
MSH|^~\&|POWERSCRIBE|CCF^2.16.840.1.113883.3.3225^ISO|EHR_RECV|OH_HIE|20260509170500||MDM^T02^MDM_T02|PS20260509170500018|P|2.5.1|||AL|NE
EVN|T02|20260509170500
PID|1||MRN5189012^^^CCF^MR||Whitaker^Sandra^Jean^^Mrs.^||19680225|F||2106-3^White^CDCREC|3975 Warrensville Center Rd^^Warrensville Heights^OH^44122^US^H||^PRN^PH^^1^216^5524291|||M^Married^HL70002|||091-28-3457|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|IR^1202^01^CCF^^^^N|U^Urgent^HL70007|||8503261974^Park^David^S^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260509018^^^CCF^VN
TXA|1|RAD^Interventional Radiology Procedure Note|TX|20260509163000||20260509170500|||||8503261974^Park^David^S^^^MD^^^^NPI|DOC90018^^CCF|||||AU^Authenticated^HL70271
OBX|1|FT|18747-6^IR Procedure Report^LN||PROCEDURE: FLUOROSCOPY-GUIDED IMPLANTATION OF SUBCUTANEOUS PORT CATHETER\.br\\.br\CLINICAL INDICATION: Stage IIIA breast cancer requiring chemotherapy access\.br\\.br\CONSENT: Written informed consent obtained. Risks including bleeding, infection, pneumothorax, air embolism, and catheter malposition were discussed.\.br\\.br\PROCEDURE DETAILS: Time out performed. The right chest was prepped and draped in sterile fashion. Under ultrasound guidance, the right internal jugular vein was accessed using a 21-gauge micropuncture needle. A guidewire was advanced into the SVC under fluoroscopy. A subcutaneous pocket was created inferior to the right clavicle. A 10 French peel-away sheath was placed and a single-lumen PowerPort was inserted with the catheter tip positioned at the cavoatrial junction.\.br\\.br\FLUOROSCOPY TIME: 2.3 minutes. ESTIMATED DOSE: 18.4 mGy.\.br\\.br\POST-PROCEDURE: Port accessed and flushed with heparinized saline. Good blood return confirmed. Post-procedure chest radiograph confirms catheter tip at the cavoatrial junction with no pneumothorax.\.br\\.br\IMPRESSION:\.br\1. Technically successful placement of right-sided subcutaneous port catheter with tip at the cavoatrial junction.\.br\2. No immediate complications.||||||F|||20260509170500
```

---

## 19. ORM^O01 - MRI breast bilateral with and without contrast order

```
MSH|^~\&|PSCRIBE360|PROMEDICA^2.16.840.1.113883.3.6620^ISO|RIS_RECV|OH_HIE|20260509083000||ORM^O01^ORM_O01|PS20260509083000019|P|2.5.1|||AL|NE
PID|1||MRN6190123^^^PTMC^MR||Henderson^Loretta^Denise^^Mrs.^||19730108|F||2054-5^Black or African American^CDCREC|3814 Secor Rd^^Toledo^OH^43623^US^H||^PRN^PH^^1^419^5526193|||M^Married^HL70002|||107-36-4568|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^MRI19^01^PTMC^^^^N|R^Routine^HL70007|||9471052386^Abrams^Lisa^K^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260509019^^^PTMC^VN
ORC|NW|ORD80019^RIS||GRP80019^RIS|||||20260509080000|||9471052386^Abrams^Lisa^K^^^MD^^^^NPI|||||PTMC^ProMedica Toledo Hospital
OBR|1|ORD80019^RIS||77049^MRI breast bilateral without and with contrast^CPT4|||20260509080000||||||||9471052386^Abrams^Lisa^K^^^MD^^^^NPI||||||||||1^Routine^HL70065
DG1|1||Z80.3^Family history of malignant neoplasm of breast^I10||20260509|A
DG1|2||Z15.01^Genetic susceptibility to malignant neoplasm of breast^I10||20260509|A
NTE|1||50-year-old female with BRCA1 mutation and strong family history of breast cancer (mother and maternal aunt). Annual screening MRI breast per NCCN guidelines. No palpable masses on clinical exam.
```

---

## 20. ADT^A08 - Patient insurance update for radiology pre-authorization

```
MSH|^~\&|NUANCE_PS|SUMMAHEALTH^2.16.840.1.113883.3.7250^ISO|ADT_RECV|OH_HIE|20260509143000||ADT^A08^ADT_A01|PS20260509143000020|P|2.5.1|||AL|NE
EVN|A08|20260509142500|||TCLARK^Clark^Tamara^T^^^CLERK|20260509142500
PID|1||MRN7201234^^^SHMC^MR||Wozniak^Jenna^Marie^^Mrs.^||19810630|F||2106-3^White^CDCREC|2105 W Market St^^Akron^OH^44313^US^H||^PRN^PH^^1^330^5529428|^WPN^PH^^1^330^5520871||M^Married^HL70002|||217-40-5679|||N^Not Hispanic or Latino^CDCREC
PD1|||Summa Health System - Akron Campus^^^^NPI|0384719265^Patel^Anita^R^^^MD^^^^NPI
NK1|1|Wozniak^Brian^Michael^^Mr.|SPO^Spouse^HL70063|2105 W Market St^^Akron^OH^44313^US|^PRN^PH^^1^330^5529429||EC^Emergency Contact^HL70131
PV1|1|O|RAD^MRI20^01^SHMC^^^^N|R^Routine^HL70007|||0384719265^Patel^Anita^R^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260509020^^^SHMC^VN
IN1|1|MMO001|60054^Medical Mutual of Ohio|MedMutual^^Cleveland^OH^44114|||||GRPJKL012||||||Wozniak^Jenna^Marie|SE^Self^HL70063|19810630|2105 W Market St^^Akron^OH^44313^US|Y||1||||||||||||||POL889900
IN2|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||Wozniak^Jenna^Marie
```
