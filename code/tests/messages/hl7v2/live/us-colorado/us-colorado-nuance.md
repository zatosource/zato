# Nuance PowerScribe - real HL7v2 ER7 messages

---

## 1. ORU^R01 - Chest X-ray final report

```
MSH|^~\&|POWERSCRIBE|DENVER_RADIOLOGY^1234^ISO|EPIC|UCH_DENVER^5678^ISO|20250415082314||ORU^R01^ORU_R01|MSG00001|P|2.5|||AL|NE
PID|1||MRN10234567^^^UCH^MR||ESPINOZA^RICARDO^D||19780312|M|||2145 E Colfax Ave^^Denver^CO^80206||3035519847|||S|||521-73-6148
PV1|1|O|RAD^RAD1^1^UCH_DENVER||||1834207^KRASNOV^DMITRI^A^^^MD|7265918^JOHANNSEN^BRENDA^K^^^MD||RAD|||||||1834207^KRASNOV^DMITRI^A^^^MD|OP||||||||||||||||||||||||||20250415080000
ORC|RE|ORD88123|FIL99234||CM||||20250415082300|||1834207^KRASNOV^DMITRI^A^^^MD
OBR|1|ORD88123|FIL99234|71020^CHEST 2 VIEWS^CPT4|||20250415080500|||||||||1834207^KRASNOV^DMITRI^A^^^MD||||||20250415082300|||F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||Chest PA and lateral views obtained. Heart size is normal. Lungs are clear bilaterally. No pleural effusion or pneumothorax. Osseous structures are intact.||||||F
OBX|2|FT|18748-4^Diagnostic Imaging Report^LN||IMPRESSION: Normal chest radiograph. No acute cardiopulmonary process.||||||F
```

---

## 2. ORU^R01 - CT abdomen pelvis with contrast

```
MSH|^~\&|NUANCE_PS|BOULDER_IMAGING^2345^ISO|CERNER|BCH_BOULDER^6789^ISO|20250418143022||ORU^R01^ORU_R01|MSG00002|P|2.5|||AL|NE
PID|1||MRN20345678^^^BCH^MR||LOCKHART^DANIELLE^P||19650923|F|||890 Pearl St^^Boulder^CO^80302||3035528714|||M|||614-82-3307
PV1|1|O|RAD^CT1^2^BCH_BOULDER||||2097543^YAMAMURA^HELEN^F^^^MD|8314260^SANDOVAL^DEREK^J^^^MD||RAD|||||||2097543^YAMAMURA^HELEN^F^^^MD|OP||||||||||||||||||||||||||20250418140000
ORC|RE|ORD88234|FIL99345||CM||||20250418143000|||2097543^YAMAMURA^HELEN^F^^^MD
OBR|1|ORD88234|FIL99345|74178^CT ABD PELVIS W CONTRAST^CPT4|||20250418141000|||||||||2097543^YAMAMURA^HELEN^F^^^MD||||||20250418143000|||F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||CT abdomen and pelvis with IV contrast. Liver, spleen, pancreas, and adrenal glands are unremarkable. Kidneys enhance symmetrically without hydronephrosis. No abdominal or pelvic lymphadenopathy. Appendix is normal in caliber.||||||F
OBX|2|FT|18748-4^Diagnostic Imaging Report^LN||IMPRESSION: 1. No acute intra-abdominal pathology. 2. Stable appearance of a 4mm hepatic cyst.||||||F
```

---

## 3. ORU^R01 - MRI brain without contrast

```
MSH|^~\&|NUANCERAD|SPRINGS_IMAGING^3456^ISO|MEDITECH|MEMORIAL_CS^7890^ISO|20250420091512||ORU^R01^ORU_R01|MSG00003|P|2.5|||AL|NE
PID|1||MRN30456789^^^MEMORIAL^MR||VIGIL^MARCUS^T||19820715|M|||445 N Cascade Ave^^Colorado Springs^CO^80903||7195534821|||S|||438-61-9275
PV1|1|O|RAD^MRI1^3^MEMORIAL_CS||||3726190^OKONKWO^GRACE^N^^^MD|9481035^HOLLOWAY^KEITH^R^^^MD||RAD|||||||3726190^OKONKWO^GRACE^N^^^MD|OP||||||||||||||||||||||||||20250420090000
ORC|RE|ORD88345|FIL99456||CM||||20250420091500|||3726190^OKONKWO^GRACE^N^^^MD
OBR|1|ORD88345|FIL99456|70551^MRI BRAIN WO CONTRAST^CPT4|||20250420090500|||||||||3726190^OKONKWO^GRACE^N^^^MD||||||20250420091500|||F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||MRI brain without contrast. No evidence of acute infarction on diffusion-weighted imaging. Ventricles and sulci are age-appropriate. No mass lesion or midline shift. White matter signal is within normal limits for age.||||||F
OBX|2|FT|18748-4^Diagnostic Imaging Report^LN||IMPRESSION: Normal MRI of the brain. No acute intracranial abnormality.||||||F
```

---

## 4. ORM^O01 - CT chest order

```
MSH|^~\&|EPIC|UCH_AURORA^4567^ISO|POWERSCRIBE|AURORA_RAD^8901^ISO|20250421101034||ORM^O01^ORM_O01|MSG00004|P|2.5|||AL|NE
PID|1||MRN40567890^^^UCH^MR||TRUJILLO^VERONICA^M||19720408|F|||1550 N Potomac St^^Aurora^CO^80011||7205547139|||M|||283-54-7016
PV1|1|O|RAD^CT2^1^UCH_AURORA||||4150892^FETTERMAN^CAROL^A^^^MD|1637204^QUINTANA^ANDRE^P^^^MD||RAD|||||||4150892^FETTERMAN^CAROL^A^^^MD|OP||||||||||||||||||||||||||20250421100000
ORC|NW|ORD88456||GRP01234|SC||||20250421101000|||4150892^FETTERMAN^CAROL^A^^^MD
OBR|1|ORD88456||71260^CT CHEST W CONTRAST^CPT4|||20250421101000|||||||||4150892^FETTERMAN^CAROL^A^^^MD|||||||||||^RULE OUT PULMONARY EMBOLISM
```

---

## 5. ORM^O01 - MRI lumbar spine order

```
MSH|^~\&|CERNER|POUDRE_VALLEY^5678^ISO|NUANCE_PS|FORTCOLLINS_RAD^9012^ISO|20250422114523||ORM^O01^ORM_O01|MSG00005|P|2.5|||AL|NE
PID|1||MRN50678901^^^PVH^MR||GARFIELD^LEONARD^W||19550619|M|||2222 W Drake Rd^^Fort Collins^CO^80526||9705548163|||W|||709-35-2841
PV1|1|O|RAD^MRI2^2^POUDRE_VALLEY||||5293017^CHAVEZ^RENEE^S^^^MD|2850176^NISHIMURA^GLENN^E^^^MD||RAD|||||||5293017^CHAVEZ^RENEE^S^^^MD|OP||||||||||||||||||||||||||20250422110000
ORC|NW|ORD88567||GRP01345|SC||||20250422114500|||5293017^CHAVEZ^RENEE^S^^^MD
OBR|1|ORD88567||72148^MRI LUMBAR SPINE WO CONTRAST^CPT4|||20250422114500|||||||||5293017^CHAVEZ^RENEE^S^^^MD|||||||||||^LOW BACK PAIN WITH RADICULOPATHY
```

---

## 6. ORU^R01 - Mammography screening report

```
MSH|^~\&|PS360|LAKEWOOD_IMAGING^6789^ISO|EPIC|STANTHONY^0123^ISO|20250423155612||ORU^R01^ORU_R01|MSG00006|P|2.5|||AL|NE
PID|1||MRN60789012^^^STANTHONY^MR||ARCHULETA^KRISTINE^B||19680301|F|||345 Wadsworth Blvd^^Lakewood^CO^80226||3035561432|||M|||362-90-5718
PV1|1|O|RAD^MAM1^1^STANTHONY||||6042817^LINDGREN^SHARON^E^^^MD|3918452^IBARRA^RAYMOND^C^^^MD||RAD|||||||6042817^LINDGREN^SHARON^E^^^MD|OP||||||||||||||||||||||||||20250423153000
ORC|RE|ORD88678|FIL99567||CM||||20250423155600|||6042817^LINDGREN^SHARON^E^^^MD
OBR|1|ORD88678|FIL99567|77067^SCREENING MAMMOGRAPHY^CPT4|||20250423153500|||||||||6042817^LINDGREN^SHARON^E^^^MD||||||20250423155600|||F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||Bilateral screening mammography. Breast composition: scattered areas of fibroglandular density (BI-RADS density B). No suspicious masses, architectural distortion, or microcalcifications are identified.||||||F
OBX|2|FT|18748-4^Diagnostic Imaging Report^LN||IMPRESSION: Negative. BI-RADS Category 1. Recommend routine annual screening.||||||F
```

---

## 7. ORU^R01 - Ultrasound abdomen with ED base64 PDF report

```
MSH|^~\&|POWERSCRIBE|DENVER_HEALTH^7890^ISO|EPIC|DH_MAIN^1234^ISO|20250424102845||ORU^R01^ORU_R01|MSG00007|P|2.5|||AL|NE
PID|1||MRN70890123^^^DH^MR||DOMINGUEZ^ELENA^V||19900514|F|||777 Bannock St^^Denver^CO^80204||3035573609|||S|||847-26-0391
PV1|1|O|RAD^US1^1^DH_MAIN||||7180453^STEFANOVIC^PAUL^G^^^MD|4629081^BLACKWELL^TAMARA^K^^^MD||RAD|||||||7180453^STEFANOVIC^PAUL^G^^^MD|OP||||||||||||||||||||||||||20250424100000
ORC|RE|ORD88789|FIL99678||CM||||20250424102800|||7180453^STEFANOVIC^PAUL^G^^^MD
OBR|1|ORD88789|FIL99678|76700^US ABDOMEN COMPLETE^CPT4|||20250424100500|||||||||7180453^STEFANOVIC^PAUL^G^^^MD||||||20250424102800|||F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||Ultrasound of the abdomen. Liver is normal in size and echotexture. No focal hepatic lesion. Gallbladder is normal without cholelithiasis. CBD measures 4mm. Pancreas, spleen, and kidneys are unremarkable.||||||F
OBX|2|FT|18748-4^Diagnostic Imaging Report^LN||IMPRESSION: Normal abdominal ultrasound.||||||F
OBX|3|ED|18748-4^Diagnostic Imaging Report PDF^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94||||||F
```

---

## 8. MDM^T02 - Radiology addendum document

```
MSH|^~\&|NUANCE_PS|SKY_RIDGE^8901^ISO|CERNER|SKYRIDGE_HIS^2345^ISO|20250425133456||MDM^T02^MDM_T02|MSG00008|P|2.5|||AL|NE
PID|1||MRN80901234^^^SKYRIDGE^MR||ROWAN^GARRETT^C||19750822|M|||10101 Ridge Gate Pkwy^^Lone Tree^CO^80124||3035584926|||M|||175-43-8620
PV1|1|I|RAD^RAD2^1^SKY_RIDGE||||8031647^FONG^NATALIE^W^^^MD|5720983^CALLAHAN^PETER^D^^^MD||RAD|||||||8031647^FONG^NATALIE^W^^^MD|IP||||||||||||||||||||||||||20250425120000
TXA|1|RAD|FT|20250425133400|8031647^FONG^NATALIE^W^^^MD||20250425133400|20250425133400||8031647^FONG^NATALIE^W^^^MD||DOC10234|||||AU||AD
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||ADDENDUM: Upon further review of prior comparison CT from 2024-11-15, the 4mm pulmonary nodule in the right lower lobe is unchanged. Recommend follow-up CT in 12 months per Fleischner criteria.||||||F
```

---

## 9. ORU^R01 - X-ray hand report

```
MSH|^~\&|POWERSCRIBE|PUEBLO_RAD^9012^ISO|MEDITECH|PARKVIEW_MC^3456^ISO|20250426084523||ORU^R01^ORU_R01|MSG00009|P|2.5|||AL|NE
PID|1||MRN91012345^^^PARKVIEW^MR||BACA^DESHAWN^A||19880210|M|||215 W 4th St^^Pueblo^CO^81003||7195592045|||S|||596-14-3827
PV1|1|E|ED^ED1^1^PARKVIEW_MC||||9463520^KIRKPATRICK^ANNA^R^^^MD|6182037^MONDRAGON^FELIPE^V^^^MD||ER|||||||9463520^KIRKPATRICK^ANNA^R^^^MD|ER||||||||||||||||||||||||||20250426080000
ORC|RE|ORD88890|FIL99789||CM||||20250426084500|||9463520^KIRKPATRICK^ANNA^R^^^MD
OBR|1|ORD88890|FIL99789|73120^HAND 2+ VIEWS^CPT4|||20250426081000|||||||||9463520^KIRKPATRICK^ANNA^R^^^MD||||||20250426084500|||F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||X-ray left hand 3 views. There is a non-displaced fracture of the 5th metacarpal neck (boxer's fracture). No significant angulation. Remaining osseous structures and joints are intact. No dislocation.||||||F
OBX|2|FT|18748-4^Diagnostic Imaging Report^LN||IMPRESSION: Non-displaced boxer's fracture of the left 5th metacarpal. Orthopedic follow-up recommended.||||||F
```

---

## 10. ADT^A01 - Patient admission to radiology

```
MSH|^~\&|EPIC|NATIONAL_JEWISH^0123^ISO|NUANCERAD|NJH_RAD^4567^ISO|20250427071234||ADT^A01^ADT_A01|MSG00010|P|2.5|||AL|NE
PID|1||MRN01123456^^^NJH^MR||WOLCOTT^DIANE^F||19600405|F|||1400 Jackson St^^Denver^CO^80206||3035510847|||W|||230-67-4912
PV1|1|I|RAD^IR1^1^NJH||||0271845^LUCERO^ERNESTO^J^^^MD|7093216^DIETRICH^MEGAN^S^^^MD||RAD|||||||0271845^LUCERO^ERNESTO^J^^^MD|IP||||||||||||||||||||||||||20250427070000
PV2|||^INTERVENTIONAL RADIOLOGY CONSULTATION
```

---

## 11. ORU^R01 - CT head without contrast emergency

```
MSH|^~\&|PS360|UCH_MAIN^1234^ISO|EPIC|UCH_ED^5678^ISO|20250428032156||ORU^R01^ORU_R01|MSG00011|P|2.5|||AL|NE
PID|1||MRN11234567^^^UCH^MR||SALAZAR^HECTOR^N||19500918|M|||1600 Downing St^^Denver^CO^80218||3035517243|||W|||481-09-3576
PV1|1|E|ED^ED2^1^UCH_MAIN||||1504872^NORBERG^SUSAN^T^^^MD|8219360^PLUMMER^JASON^K^^^MD||ER|||||||1504872^NORBERG^SUSAN^T^^^MD|ER||||||||||||||||||||||||||20250428030000
ORC|RE|ORD89001|FIL99890||CM||||20250428032100|||1504872^NORBERG^SUSAN^T^^^MD
OBR|1|ORD89001|FIL99890|70450^CT HEAD WO CONTRAST^CPT4|||20250428031000||||||STAT||||1504872^NORBERG^SUSAN^T^^^MD||||||20250428032100|||F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||CT head without contrast STAT. Large hyperdense collection in the right basal ganglia measuring 4.2 x 3.1 cm consistent with acute hemorrhage. Associated surrounding edema with 5mm leftward midline shift. Lateral ventricles show early hydrocephalus.||||||F
OBX|2|FT|18748-4^Diagnostic Imaging Report^LN||IMPRESSION: CRITICAL RESULT - Large right basal ganglia hemorrhage with mass effect and midline shift. Neurosurgical consultation recommended emergently.||||||F
```

---

## 12. ORM^O01 - PET-CT order

```
MSH|^~\&|EPIC|ROCKY_MTN_CANCER^2345^ISO|POWERSCRIBE|RMCC_RAD^6789^ISO|20250429091023||ORM^O01^ORM_O01|MSG00012|P|2.5|||AL|NE
PID|1||MRN12345678^^^RMCC^MR||THORNTON^BEVERLY^J||19580712|F|||1800 Williams St^^Denver^CO^80218||3035526401|||W|||753-18-4069
PV1|1|O|NM^PET1^1^RMCC||||2618703^MALEK^ARASH^S^^^MD|9054127^CONNELLY^NANCY^H^^^MD||NM|||||||2618703^MALEK^ARASH^S^^^MD|OP||||||||||||||||||||||||||20250429090000
ORC|NW|ORD89112||GRP01456|SC||||20250429091000|||2618703^MALEK^ARASH^S^^^MD
OBR|1|ORD89112||78816^PET CT IMAGING^CPT4|||20250429091000|||||||||2618703^MALEK^ARASH^S^^^MD|||||||||||^STAGING NON-SMALL CELL LUNG CANCER
```

---

## 13. ORU^R01 - Fluoroscopy upper GI

```
MSH|^~\&|NUANCE_PS|PENROSE_HOSP^3456^ISO|CERNER|PENROSE_HIS^7890^ISO|20250430110034||ORU^R01^ORU_R01|MSG00013|P|2.5|||AL|NE
PID|1||MRN13456789^^^PENROSE^MR||PACHECO^WAYNE^S||19700620|M|||2222 N Nevada Ave^^Colorado Springs^CO^80907||7195531874|||M|||318-72-5940
PV1|1|O|RAD^FL1^1^PENROSE_HOSP||||3847120^OSTERGAARD^ANGELA^M^^^MD|0539214^KIMBALL^BRUCE^L^^^MD||RAD|||||||3847120^OSTERGAARD^ANGELA^M^^^MD|OP||||||||||||||||||||||||||20250430103000
ORC|RE|ORD89223|FIL99901||CM||||20250430110000|||3847120^OSTERGAARD^ANGELA^M^^^MD
OBR|1|ORD89223|FIL99901|74240^UPPER GI SERIES^CPT4|||20250430104000|||||||||3847120^OSTERGAARD^ANGELA^M^^^MD||||||20250430110000|||F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||Upper GI series with barium. Esophageal motility is normal. No hiatal hernia. Gastric folds are normal. Duodenal bulb and loop are unremarkable. No ulceration or mass lesion identified.||||||F
OBX|2|FT|18748-4^Diagnostic Imaging Report^LN||IMPRESSION: Normal upper GI series.||||||F
```

---

## 14. MDM^T02 - Interventional radiology procedure note

```
MSH|^~\&|POWERSCRIBE|SWEDISH_MC^4567^ISO|EPIC|SWEDISH_HIS^8901^ISO|20250501141234||MDM^T02^MDM_T02|MSG00014|P|2.5|||AL|NE
PID|1||MRN14567890^^^SWEDISH^MR||KESSLER^ADRIANA^R||19850930|F|||501 E Hampden Ave^^Englewood^CO^80113||3035547281|||S|||645-03-8217
PV1|1|I|RAD^IR2^1^SWEDISH_MC||||4805132^NAKAMURA^DAVID^Q^^^MD|1379064^GUTIERREZ^KEITH^A^^^MD||RAD|||||||4805132^NAKAMURA^DAVID^Q^^^MD|IP||||||||||||||||||||||||||20250501130000
TXA|1|RAD|FT|20250501141200|4805132^NAKAMURA^DAVID^Q^^^MD||20250501141200|20250501141200||4805132^NAKAMURA^DAVID^Q^^^MD||DOC10345|||||AU||LA
OBX|1|FT|28570-0^Procedure Note^LN||PROCEDURE: CT-guided lung biopsy, right upper lobe. 18-gauge coaxial needle used. Three core samples obtained. Immediate post-procedure CT shows small pneumothorax measuring 1cm at apex. Patient stable, follow-up chest X-ray in 4 hours.||||||F
```

---

## 15. ORU^R01 - Nuclear medicine bone scan

```
MSH|^~\&|NUANCERAD|CENTURA_RAD^5678^ISO|MEDITECH|STFRANCIS^9012^ISO|20250502084523||ORU^R01^ORU_R01|MSG00015|P|2.5|||AL|NE
PID|1||MRN15678901^^^STFRANCIS^MR||ROMERO^CLIFFORD^H||19620115|M|||30 W Boulder St^^Colorado Springs^CO^80903||7195556734|||W|||902-47-1385
PV1|1|O|NM^NM1^1^STFRANCIS||||5074318^HAUGEN^DIANE^L^^^MD|2691054^EASTMAN^MARK^B^^^MD||NM|||||||5074318^HAUGEN^DIANE^L^^^MD|OP||||||||||||||||||||||||||20250502080000
ORC|RE|ORD89334|FIL00012||CM||||20250502084500|||5074318^HAUGEN^DIANE^L^^^MD
OBR|1|ORD89334|FIL00012|78300^BONE SCAN WHOLE BODY^CPT4|||20250502081000|||||||||5074318^HAUGEN^DIANE^L^^^MD||||||20250502084500|||F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||Whole body bone scan with Tc-99m MDP. Increased uptake noted in the right sacroiliac joint and left knee medial compartment. No suspicious lesions suggestive of metastatic disease. Activity in kidneys and bladder is physiologic.||||||F
OBX|2|FT|18748-4^Diagnostic Imaging Report^LN||IMPRESSION: Degenerative changes right SI joint and left knee. No findings to suggest osseous metastatic disease.||||||F
```

---

## 16. ORU^R01 - CT pulmonary angiography with ED base64 PDF

```
MSH|^~\&|POWERSCRIBE|UCH_ED_RAD^6789^ISO|EPIC|UCH_ED_MAIN^0123^ISO|20250503044512||ORU^R01^ORU_R01|MSG00016|P|2.5|||AL|NE
PID|1||MRN16789012^^^UCH^MR||FIERRO^CASSANDRA^L||19930217|F|||1055 Clermont St^^Denver^CO^80220||7205563918|||S|||574-30-8162
PV1|1|E|ED^ED3^1^UCH_MAIN||||6207451^HENRIKSEN^BRIAN^P^^^MD|3580294^DELGADO^SANDRA^T^^^MD||ER|||||||6207451^HENRIKSEN^BRIAN^P^^^MD|ER||||||||||||||||||||||||||20250503040000
ORC|RE|ORD89445|FIL00123||CM||||20250503044500|||6207451^HENRIKSEN^BRIAN^P^^^MD
OBR|1|ORD89445|FIL00123|71275^CT ANGIO CHEST PULM EMBOL^CPT4|||20250503041500||||||STAT||||6207451^HENRIKSEN^BRIAN^P^^^MD||||||20250503044500|||F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||CT pulmonary angiography STAT. Filling defect identified in the right lower lobe segmental pulmonary artery consistent with acute pulmonary embolism. No saddle embolus. RV/LV ratio is 0.9 suggesting no right heart strain. No pleural effusion.||||||F
OBX|2|FT|18748-4^Diagnostic Imaging Report^LN||IMPRESSION: CRITICAL - Acute right lower lobe pulmonary embolism. No evidence of right heart strain.||||||F
OBX|3|ED|18748-4^Diagnostic Imaging Report PDF^LN||^application^pdf^Base64^JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8IC9NYXJrZWQgdHJ1ZSA+PgovU3RydWN0VHJlZVJvb3QgMyAwIFIKPj4KZW5kb2Jq||||||F
```

---

## 17. ADT^A03 - Patient discharge from radiology observation

```
MSH|^~\&|CERNER|EXEMPLA_LUTHERAN^7890^ISO|NUANCE_PS|EXEMP_RAD^1234^ISO|20250504163412||ADT^A03^ADT_A03|MSG00017|P|2.5|||AL|NE
PID|1||MRN17890123^^^EXEMPLA^MR||MCALLISTER^JORDAN^T||19780605|M|||8300 W 38th Ave^^Wheat Ridge^CO^80033||3035549207|||M|||463-81-7024
PV1|1|O|RAD^RAD3^1^EXEMPLA_LUTH||||7025814^RICHTER^RACHEL^C^^^MD|4316079^CORDOVA^PAUL^G^^^MD||RAD|||||||7025814^RICHTER^RACHEL^C^^^MD|OP||||||||||||||||||||||||||20250504160000|||||||||||||||||||||||20250504163400
```

---

## 18. ORU^R01 - Ultrasound thyroid report

```
MSH|^~\&|PS360|BOULDER_COMMUNITY^8901^ISO|EPIC|BCH_HIS^2345^ISO|20250505091234||ORU^R01^ORU_R01|MSG00018|P|2.5|||AL|NE
PID|1||MRN18901234^^^BCH^MR||WINSLOW^THERESA^K||19710819|F|||2525 4th St^^Boulder^CO^80304||3035580473|||M|||821-54-0936
PV1|1|O|RAD^US2^1^BCH||||8946310^MEDINA^VICTOR^A^^^MD|5173028^PIERSON^JANET^R^^^MD||RAD|||||||8946310^MEDINA^VICTOR^A^^^MD|OP||||||||||||||||||||||||||20250505090000
ORC|RE|ORD89556|FIL00234||CM||||20250505091200|||8946310^MEDINA^VICTOR^A^^^MD
OBR|1|ORD89556|FIL00234|76536^US THYROID^CPT4|||20250505090500|||||||||8946310^MEDINA^VICTOR^A^^^MD||||||20250505091200|||F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||Ultrasound of the thyroid. Right lobe measures 5.2 x 2.1 x 1.8 cm. Left lobe measures 4.8 x 1.9 x 1.7 cm. A 1.2 cm predominantly cystic nodule is noted in the right lobe with a thin peripheral calcification. TI-RADS 3.||||||F
OBX|2|FT|18748-4^Diagnostic Imaging Report^LN||IMPRESSION: 1.2 cm TI-RADS 3 nodule right thyroid lobe. Follow-up ultrasound in 1-2 years recommended per ACR guidelines.||||||F
```

---

## 19. ORM^O01 - Cardiac MRI order

```
MSH|^~\&|EPIC|PORTER_ADVENT^9012^ISO|POWERSCRIBE|PORTER_RAD^3456^ISO|20250506102345||ORM^O01^ORM_O01|MSG00019|P|2.5|||AL|NE
PID|1||MRN19012345^^^PORTER^MR||STANHOPE^BRENDAN^R||19800314|M|||2525 S Downing St^^Denver^CO^80210||3035591047|||M|||137-62-8504
PV1|1|I|CARD^CARD1^1^PORTER_ADVENT||||9270314^OBERHOLTZER^ELIZABETH^H^^^MD|6138052^GALINDO^STEVEN^M^^^MD||CARD|||||||9270314^OBERHOLTZER^ELIZABETH^H^^^MD|IP||||||||||||||||||||||||||20250506100000
ORC|NW|ORD89667||GRP01567|SC||||20250506102300|||9270314^OBERHOLTZER^ELIZABETH^H^^^MD
OBR|1|ORD89667||75557^CARDIAC MRI W WO CONTRAST^CPT4|||20250506102300|||||||||9270314^OBERHOLTZER^ELIZABETH^H^^^MD|||||||||||^EVALUATE CARDIOMYOPATHY LVEF 35%
```

---

## 20. ORU^R01 - CT angiography aorta

```
MSH|^~\&|NUANCERAD|PLATTE_VALLEY^0123^ISO|CERNER|PVM_HIS^4567^ISO|20250507141234||ORU^R01^ORU_R01|MSG00020|P|2.5|||AL|NE
PID|1||MRN20123456^^^PVM^MR||WHITFIELD^GERALD^A||19550428|M|||1600 Prairie Center Pkwy^^Brighton^CO^80601||3035503861|||W|||068-49-7213
PV1|1|I|VASC^VASC1^1^PLATTE_VALLEY||||0715234^ANAYA^PATRICIA^L^^^MD|7480192^ENGSTROM^TIMOTHY^C^^^MD||SURG|||||||0715234^ANAYA^PATRICIA^L^^^MD|IP||||||||||||||||||||||||||20250507130000
ORC|RE|ORD89778|FIL00345||CM||||20250507141200|||0715234^ANAYA^PATRICIA^L^^^MD
OBR|1|ORD89778|FIL00345|75635^CT ANGIO ABDOMINAL AORTA^CPT4|||20250507133000|||||||||0715234^ANAYA^PATRICIA^L^^^MD||||||20250507141200|||F
OBX|1|FT|18748-4^Diagnostic Imaging Report^LN||CTA of the abdominal aorta. Infrarenal abdominal aortic aneurysm measuring 5.8 cm in maximum diameter. The aneurysm extends from below the renal arteries to the aortic bifurcation. Mural thrombus is present circumferentially. Iliac arteries are mildly ectatic bilaterally.||||||F
OBX|2|FT|18748-4^Diagnostic Imaging Report^LN||IMPRESSION: 5.8 cm infrarenal AAA, interval growth from 5.2 cm on prior study dated 2024-09-15. Exceeds threshold for elective repair. Vascular surgery consultation recommended.||||||F
```
