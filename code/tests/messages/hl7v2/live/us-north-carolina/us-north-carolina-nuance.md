# Nuance PowerScribe - real HL7v2 ER7 messages

---

## 1. ORU^R01 - Final chest X-ray report

```
MSH|^~\&|POWERSCRIBE|UNC_REX|EPIC|UNC_REX|UNCREX||ORU^R01^ORU_R01|MSG20260415083022001|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN93641096^^^UNCREX^MR||SIGMON^FELICIA^MAE||19810212|F|||2244 SPRING FOREST RD^^WINSTON SALEM^NC^27104||9195551234|||M|||568-49-5683|||N||||||||N
PV1|1|O|RAD^^^UNCREX^WAKEMED|||||||RAD||||||||OP|VN20260408019|||||||||||||||||||WAKEMED||||20260415080000
ORC|RE|ORD9923871|FIL2026041500123||CM||||20260415083000|||HSTRO^Strother^Hugo^D^^^MD|||||UNCREX_PHARM^UNC Rex Healthcare Pharmacy^^UNCREX^^828^3087220^27610
OBR|1|ORD9923871|FIL2026041500123|71020^CHEST 2 VIEWS^CPT4|||20260415080500|||||||||1826079802^OGBURN^JULIAN^C^^^MD||||||20260415083000|||F|||||||1176347176^MOSTELLER^ALICIA^T^^^MD&ATTENDING
OBX|1|FT|GDT^REPORT TEXT^LOCAL||CHEST, 2 VIEWS\.br\\.br\CLINICAL INDICATION: Cough for 3 weeks\.br\\.br\COMPARISON: Chest radiograph dated 2025-11-02\.br\\.br\FINDINGS:\.br\The lungs are clear bilaterally without focal consolidation, pleural effusion, or pneumothorax. The cardiac silhouette is normal in size. The mediastinal contours are unremarkable. No acute osseous abnormality is identified.\.br\\.br\IMPRESSION:\.br\1. No acute cardiopulmonary disease.\.br\2. Stable examination compared to prior.||||||F|||20260415083000||1176347176^MOSTELLER^ALICIA^T^^^MD
OBX|2|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Joyce W. Ashworth, MD\.br\Radiology Department, Wake Medical Center\.br\Date: 2026-04-15 08:30||||||F
```

---

## 2. ORU^R01 - CT abdomen/pelvis with contrast

```
MSH|^~\&|NUANCE_PS|CAPE_FEAR|CAPEFEAR|CAPE_FEAR|CAPEFEAR||ORU^R01^ORU_R01|MSG20260422141507002|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN48051805^^^CAPEFEAR^MR||BULLARD^HOPE^GAIL||19770702|F|||666 FRIENDLY AVE^^ASHEVILLE^NC^28801||9195559876|||F|||609-20-8865|||N||||||||N
PV1|1|I|4WEST^412^A^CAPEFEAR|||||||RAD||||||||IP|VN20260406023|||||||||||||||||||DUKE||||20260420140000
ORC|RE|ORD5578234|FIL2026042200456||CM||||20260422141500|||ERAVE^Ravenscroft^Eileen^N^^^MD|||||CAPEFEAR_PHARM^Cape Fear Valley Medical Center Pharmacy^^CAPEFEAR^^910^7488509^27710
OBR|1|ORD5578234|FIL2026042200456|74178^CT ABD PELVIS W CONTRAST^CPT4|||20260422130000|||||||||1237781607^OKONKWO^KENT^E^^^MD||||||20260422141500|||F|||||||1354648606^DUNLAP^NIGEL^J^^^MD&ATTENDING
OBX|1|FT|GDT^REPORT TEXT^LOCAL||CT ABDOMEN AND PELVIS WITH IV CONTRAST\.br\\.br\CLINICAL INDICATION: Right lower quadrant pain, rule out appendicitis\.br\\.br\TECHNIQUE: Axial images obtained from the lung bases through the pelvis following administration of 100 mL Omnipaque 350 IV contrast.\.br\\.br\COMPARISON: None available\.br\\.br\FINDINGS:\.br\LIVER: Normal in size and attenuation. No focal lesion.\.br\GALLBLADDER: Normal. No stones or wall thickening.\.br\PANCREAS: Normal in size and enhancement.\.br\SPLEEN: Normal.\.br\KIDNEYS: Normal bilaterally. No hydronephrosis or stones.\.br\ADRENALS: Normal.\.br\APPENDIX: The appendix measures 11 mm in diameter with periappendiceal fat stranding and a 6 mm appendicolith at the base. Mild free fluid in the pelvis.\.br\BOWEL: No obstruction. No free air.\.br\LYMPH NODES: No pathologic lymphadenopathy.\.br\OSSEOUS: No acute fracture.\.br\\.br\IMPRESSION:\.br\1. Acute appendicitis with appendicolith. Surgical consultation recommended.\.br\2. Small amount of pelvic free fluid likely reactive.||||||F|||20260422141500||1354648606^DUNLAP^NIGEL^J^^^MD
OBX|2|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Fiona M. Reddick, MD\.br\Department of Radiology, Duke University Hospital\.br\Date: 2026-04-22 14:15||||||F
```

---

## 3. ORU^R01 - MRI brain without contrast

```
MSH|^~\&|PSCRIBE360|NOVANT_PSB|NOVANTPSB|NOVANT_PSB|NOVANTPSB||ORU^R01^ORU_R01|MSG20260501092345003|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN14570527^^^NOVANTPSB^MR||FRYE^GILBERT^LEWIS||19890105|M|||1190 MARKET ST^^FAYETTEVILLE^NC^28303||7045551122|||M|||430-59-1167|||N||||||||N
PV1|1|O|MRISC^^^NOVANTPSB^ATRIUM_CMC|||||||RAD||||||||OP|VN20260429014|||||||||||||||||||ATRIUM||||20260501085000
ORC|RE|ORD7734512|FIL2026050100789||CM||||20260501092300|||OLATT^Lattimore^Owen^Q^^^MD|||||NOVANTPSB_PHARM^Novant Health Presbyterian Pharmacy^^NOVANTPSB^^336^4401250^28203
OBR|1|ORD7734512|FIL2026050100789|70551^MRI BRAIN WO CONTRAST^CPT4|||20260501085500|||||||||1892057215^ABERNATHY^OWEN^V^^^MD||||||20260501092300|||F|||||||1624177020^OGBURN^ALAN^K^^^MD&ATTENDING
OBX|1|FT|GDT^REPORT TEXT^LOCAL||MRI BRAIN WITHOUT CONTRAST\.br\\.br\CLINICAL INDICATION: New onset seizure. Rule out mass.\.br\\.br\TECHNIQUE: Multiplanar multisequence MRI of the brain without IV contrast including DWI, T1, T2, FLAIR, and GRE sequences.\.br\\.br\COMPARISON: None\.br\\.br\FINDINGS:\.br\PARENCHYMA: No acute infarction on diffusion-weighted imaging. No intracranial mass or abnormal enhancement. A few scattered punctate T2/FLAIR hyperintensities in the periventricular white matter, nonspecific but likely representing mild chronic small vessel ischemic changes. No hemorrhage on GRE sequences.\.br\VENTRICLES: Normal in size and morphology. No hydrocephalus.\.br\MIDLINE STRUCTURES: No midline shift.\.br\EXTRA-AXIAL SPACES: No extra-axial collection.\.br\CALVARIUM: Normal.\.br\\.br\IMPRESSION:\.br\1. No acute intracranial abnormality. No mass.\.br\2. Mild nonspecific periventricular white matter changes, likely chronic microvascular ischemic disease.||||||F|||20260501092300||1624177020^OGBURN^ALAN^K^^^MD
OBX|2|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Ingrid G. Bostwick, MD\.br\Neuroradiology, Atrium Health Carolinas Medical Center\.br\Date: 2026-05-01 09:23||||||F
```

---

## 4. MDM^T02 - Transcribed ultrasound report document

```
MSH|^~\&|POWERSCRIBE|MISSION_HOSP|EPIC|MISSION_HOSP|MISSIONH||MDM^T02^MDM_T02|MSG20260318110045004|P|2.5.1|||AL|NE||ASCII|||
EVN|T02|20260318110045
PID|1||MRN50543036^^^MISSIONH^MR||PEACOCK^FLORINE^CAROL||19581124|F|||1405 BROOKWOOD DR^^HIGH POINT^NC^27260||2525553344|||F|||685-88-4514|||N||||||||N
PV1|1|O|USOUND^^^MISSIONH^VIDANT_MC|||||||RAD||||||||OP|VN20260413002|||||||||||||||||||VIDANT||||20260318100000
TXA|1|US|FT|20260318110000|1882340677^UNDERWOOD^FRANCIS^L^^^MD|AU|||||DOC20260318001||||CM||AV|||
OBR|1|ORD3345678|FIL2026031800234|76856^US PELVIS COMPLETE^CPT4|||20260318100500|||||||||1882340677^UNDERWOOD^FRANCIS^L^^^MD||||||20260318110000|||F
OBX|1|FT|GDT^REPORT TEXT^LOCAL||ULTRASOUND PELVIS, COMPLETE\.br\\.br\CLINICAL INDICATION: Pelvic pain, irregular menses\.br\\.br\COMPARISON: Pelvic ultrasound 2025-06-14\.br\\.br\FINDINGS:\.br\UTERUS: Anteverted, measures 8.2 x 4.1 x 5.0 cm. Normal myometrial echotexture. Endometrial stripe measures 6 mm, within normal limits. No focal mass.\.br\RIGHT OVARY: Measures 3.1 x 2.0 x 2.2 cm. Contains a simple cyst measuring 1.8 cm, likely physiologic follicle. Normal vascular flow.\.br\LEFT OVARY: Measures 2.9 x 1.8 x 2.0 cm. Normal appearance. No mass or cyst.\.br\CUL-DE-SAC: No free fluid.\.br\\.br\IMPRESSION:\.br\1. Small simple right ovarian cyst, likely physiologic. Recommend follow-up ultrasound in 6-8 weeks if clinically indicated.\.br\2. Otherwise normal pelvic ultrasound.||||||F|||20260318110000||1882340677^UNDERWOOD^FRANCIS^L^^^MD
OBX|2|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Francis T. Jernigan, MD\.br\Radiology, Vidant Medical Center\.br\Date: 2026-03-18 11:00||||||F
```

---

## 5. ORU^R01 - Mammography screening report with BI-RADS

```
MSH|^~\&|POWERSCRIBE|NOVANT_PSB|EPIC|NOVANT_PSB|NOVANTPSB||ORU^R01^ORU_R01|MSG20260407155230005|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN61250300^^^NOVANTPSB^MR||BROYHILL^DWAYNE^THOMAS||19750521|M|||6700 FAIRVIEW RD^^HICKORY^NC^28601||3365554455|||F|||488-31-8236|||N||||||||N
PV1|1|O|MAMMO^^^NOVANTPSB^CONE_WOMENS|||||||RAD||||||||OP|VN20260408030|||||||||||||||||||CONE||||20260407150000
ORC|RE|ORD6612789|FIL2026040700567||CM||||20260407155200|||OMOST^Mosteller^Owen^L^^^MD|||||NOVANTPSB_PHARM^Novant Health Presbyterian Pharmacy^^NOVANTPSB^^910^4236313^27401
OBR|1|ORD6612789|FIL2026040700567|77067^SCREENING MAMMOGRAPHY BILATERAL^CPT4|||20260407150500|||||||||1176347176^UNDERWOOD^NIGEL^P^^^MD||||||20260407155200|||F|||||||1595454923^ABERNATHY^EVAN^V^^^MD&ATTENDING
OBX|1|FT|GDT^REPORT TEXT^LOCAL||SCREENING MAMMOGRAPHY, BILATERAL\.br\\.br\CLINICAL INDICATION: Annual screening. No symptoms. No family history of breast cancer.\.br\\.br\TECHNIQUE: Standard CC and MLO views of both breasts. Tomosynthesis performed bilaterally.\.br\\.br\COMPARISON: Screening mammogram 2025-04-10\.br\\.br\FINDINGS:\.br\BREAST COMPOSITION: The breasts are heterogeneously dense, which may obscure small masses (ACR density category C).\.br\RIGHT BREAST: No suspicious mass, architectural distortion, or suspicious calcifications.\.br\LEFT BREAST: No suspicious mass, architectural distortion, or suspicious calcifications. Stable benign-appearing calcifications in the upper outer quadrant.\.br\AXILLAE: No suspicious lymphadenopathy.\.br\\.br\IMPRESSION:\.br\BI-RADS 1 - Negative\.br\Normal screening mammogram. Annual screening recommended.||||||F|||20260407155200||1595454923^ABERNATHY^EVAN^V^^^MD
OBX|2|FT|GDT^BIRADS^LOCAL||1||||||F
OBX|3|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Brenda C. Reddick, MD\.br\Breast Imaging, Cone Health Women's Center\.br\Date: 2026-04-07 15:52||||||F
```

---

## 6. ORM^O01 - New CT head order from ED

```
MSH|^~\&|EPIC|DUKE_UNIV_HOSP|DUKEHOSP|DUKE_UNIV_HOSP|DUKEHOSP||ORM^O01^ORM_O01|MSG20260510063012006|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN30745861^^^DUKEHOSP^MR||ZACHARY^SYLVIA^WANDA||19590510|F|||3801 LAKE BOONE TRL^^RALEIGH^NC^27606||9105556677|||M|||683-78-7279|||N||||||||N
PV1|1|E|ED^^^DUKEHOSP^MOORE_REG|||||||EM||||||||ER|VN20260404003|||||||||||||||||||FIRSTHLTH||||20260510055000
ORC|NW|ORD1123456||FIL2026051000012||SC||||20260510063000|||1160011934^VANDERBURG^LINUS^J^^^MD|||||3340 SILAS CREEK PKWY^^CHARLOTTE^NC^28202^PINEHURST^NC^28374
OBR|1|ORD1123456||70450^CT HEAD WO CONTRAST^CPT4|||20260510063000|||||||||1783391018^MOSTELLER^PIERCE^H^^^MD|||||||||||1||||||||||STAT
NTE|1||Fall from standing height, loss of consciousness, on Coumadin
```

---

## 7. ORU^R01 - CT head final read from ED order

```
MSH|^~\&|NUANCE_PS|MISSION_HOSP|EPIC|MISSION_HOSP|MISSIONH||ORU^R01^ORU_R01|MSG20260510072145007|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN98175935^^^MISSIONH^MR||SHUFORD^MARCUS^SAMUEL||19450816|M|||3156 LAWNDALE DR^^STATESVILLE^NC^28677||9105556677|||M|||322-85-1093|||N||||||||N
PV1|1|E|ED^^^MISSIONH^MOORE_REG|||||||RAD||||||||ER|VN20260422007|||||||||||||||||||FIRSTHLTH||||20260510055000
ORC|RE|ORD1123456|FIL2026051000012||CM||||20260510072100|||GHARG^Hargrove^Greta^J^^^MD|||||MISSIONH_PHARM^Mission Hospital Asheville Pharmacy^^MISSIONH^^919^5131298^28374
OBR|1|ORD1123456|FIL2026051000012|70450^CT HEAD WO CONTRAST^CPT4|||20260510065500|||||||||1299943571^CARRAWAY^GRETA^T^^^MD||||||20260510072100|||F|||||||1783391018^MOSTELLER^PIERCE^H^^^MD&ATTENDING
OBX|1|FT|GDT^REPORT TEXT^LOCAL||CT HEAD WITHOUT CONTRAST\.br\\.br\CLINICAL INDICATION: Fall, loss of consciousness, anticoagulated (Coumadin)\.br\\.br\TECHNIQUE: Noncontrast axial CT of the head.\.br\\.br\COMPARISON: None\.br\\.br\FINDINGS:\.br\PARENCHYMA: No acute intracranial hemorrhage. No mass effect or midline shift. Gray-white matter differentiation is preserved. Mild generalized cerebral atrophy appropriate for age.\.br\VENTRICLES: Normal in size and configuration.\.br\EXTRA-AXIAL: No epidural, subdural, or subarachnoid hemorrhage.\.br\CALVARIUM: No fracture. Small right frontal subgaleal soft tissue swelling at the site of impact.\.br\PARANASAL SINUSES: Clear.\.br\MASTOIDS: Clear.\.br\\.br\IMPRESSION:\.br\1. No acute intracranial hemorrhage or fracture.\.br\2. Right frontal subgaleal soft tissue swelling consistent with site of impact.\.br\3. Mild cerebral atrophy.||||||F|||20260510072100||1299943571^CARRAWAY^GRETA^T^^^MD
OBX|2|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Karen M. Ellerbe, MD\.br\Radiology, FirstHealth Moore Regional Hospital\.br\Date: 2026-05-10 07:21||||||F
```

---

## 8. ADT^A04 - Patient registration for radiology visit

```
MSH|^~\&|EPIC|NOVANT_PSB|NOVANTPSB|NOVANT_PSB|NOVANTPSB||ADT^A04^ADT_A01|MSG20260325134500008|P|2.5.1|||AL|NE||ASCII|||
EVN|A04|20260325134500
PID|1||MRN58862393^^^NOVANTPSB^MR||HONEYCUTT^RAMONA^OPAL||19520204|F|||3801 LAKE BOONE TRL^^CHARLOTTE^NC^28205||9195558899|||F|||327-93-9810|||N||||||||N
PV1|1|O|RAD^^^NOVANTPSB^UNC_HOSP|||||||RAD||||||||OP|VN20260426016|||||||||||||||||||UNCHLTH||||20260325134500
PV2||||||||20260325140000|||||||||||||||||||||||||||||N
DG1|1||R10.9^Unspecified abdominal pain^ICD10|||A
IN1|1|BCBSNC001|WELLPATH007|WELLPATH OF CAROLINA|||||GRP445566|||20260101||||HOYLE^WANDA^I|SELF|19750907|5010 SOUTH BLVD^^ASHEVILLE^NC^28803||||||||||||||||SMG7789012||||||F
```

---

## 9. ADT^A08 - Patient information update

```
MSH|^~\&|CERNER|ATRIUM_CMC|ATRIUMCMC|ATRIUM_CMC|ATRIUMCMC||ADT^A08^ADT_A01|MSG20260412091230009|P|2.5.1|||AL|NE||ASCII|||
EVN|A08|20260412091230
PID|1||MRN60167359^^^ATRIUMCMC^MR||STRICKLAND^ANDRE^OWEN||19661123|M|||7600 PINEVILLE-MATTHEWS RD^^FAYETTEVILLE^NC^28301||7045552233|||M|||453-26-1064|||N||||||||N
PV1|1|I|5N^501^B^ATRIUMCMC|||||||RAD||||||||IP|VN20260413028|||||||||||||||||||NOVANTH||||20260410120000
PV2||||||||||||||||20260413||||||||||||||||||||N
DG1|1||C34.11^Malignant neoplasm of upper lobe, right bronchus or lung^ICD10|||A
DG1|2||J91.0^Malignant pleural effusion^ICD10|||A
```

---

## 10. ORU^R01 - Preliminary report (resident read) with addendum

```
MSH|^~\&|PSCRIBE360|IREDELL_MEM|EPIC|IREDELL_MEM|IREDELLMH||ORU^R01^ORU_R01|MSG20260428021530010|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN10836739^^^IREDELLMH^MR||PREVATTE^CANDACE^CAROL||19711104|F|||1812 EASTCHESTER DR^^DURHAM^NC^27701||9195553344|||M|||699-10-9177|||N||||||||N
PV1|1|E|ED^^^IREDELLMH^WAKEMED|||||||RAD||||||||ER|VN20260421003|||||||||||||||||||WAKEMED||||20260428013000
ORC|RE|ORD4456123|FIL2026042800345||CM||||20260428021500|||LREDD^Reddick^Linus^L^^^MD|||||IREDELLMH_PHARM^Iredell Memorial Hospital Pharmacy^^IREDELLMH^^336^4409921^27610
OBR|1|ORD4456123|FIL2026042800345|71046^CHEST 2 VIEWS^CPT4|||20260428014500|||||||||1237781607^HARGROVE^EVAN^P^^^MD||||||20260428021500|||F|||||||1892057215^HARGROVE^LINUS^N^^^MD&ATTENDING
OBX|1|FT|GDT^REPORT TEXT^LOCAL||CHEST, 2 VIEWS\.br\\.br\CLINICAL INDICATION: Shortness of breath, fever\.br\\.br\COMPARISON: None\.br\\.br\FINDINGS:\.br\LUNGS: Patchy airspace opacity in the right lower lobe consistent with pneumonia. Left lung is clear. No pleural effusion. No pneumothorax.\.br\HEART: Normal cardiac silhouette.\.br\MEDIASTINUM: Unremarkable.\.br\BONES: No acute osseous abnormality.\.br\\.br\IMPRESSION:\.br\1. Right lower lobe pneumonia.\.br\\.br\PRELIMINARY REPORT by Julian V. Tuttle, MD (PGY-4) at 02:15 2026-04-28\.br\ATTENDING ADDENDUM by Graham S. Blackmon, MD at 07:30 2026-04-28: Agree with resident interpretation. Findings communicated to ED physician Dr. Lattimore at 02:16 by phone per ACR guidelines for critical results.||||||F|||20260428021500||1892057215^HARGROVE^LINUS^N^^^MD
OBX|2|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Evan M. Ashworth, MD\.br\Radiology, Wake Medical Center\.br\Date: 2026-04-28 07:30||||||F
```

---

## 11. ORU^R01 - Nuclear medicine thyroid scan

```
MSH|^~\&|POWERSCRIBE|CATAWBA_VAL|EPIC|CATAWBA_VAL|CATAWBAMC||ORU^R01^ORU_R01|MSG20260303143500011|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN89977736^^^CATAWBAMC^MR||SHOFFNER^SYLVIA^FAYE||19560418|F|||2244 SPRING FOREST RD^^FAYETTEVILLE^NC^28303||2525557788|||F|||372-71-4627|||N||||||||N
PV1|1|O|NUCMED^^^CATAWBAMC^ECU_MC|||||||RAD||||||||OP|VN20260410021|||||||||||||||||||ECUHLTH||||20260303130000
ORC|RE|ORD2234567|FIL2026030300678||CM||||20260303143400|||HINGR^Ingram^Hugo^S^^^MD|||||CATAWBAMC_PHARM^Catawba Valley Medical Center Pharmacy^^CATAWBAMC^^336^3538353^27834
OBR|1|ORD2234567|FIL2026030300678|78013^THYROID IMAGING W UPTAKE^CPT4|||20260303130500|||||||||1845873282^ASHWORTH^EVAN^M^^^MD||||||20260303143400|||F|||||||1176347176^RAVENSCROFT^LYDIA^S^^^MD&ATTENDING
OBX|1|FT|GDT^REPORT TEXT^LOCAL||THYROID SCAN WITH UPTAKE\.br\\.br\CLINICAL INDICATION: Hyperthyroidism, elevated free T4, suppressed TSH\.br\\.br\RADIOPHARMACEUTICAL: 5.2 mCi Tc-99m pertechnetate IV\.br\\.br\COMPARISON: None\.br\\.br\FINDINGS:\.br\UPTAKE: 4-hour uptake 18% (normal 5-15%). 24-hour uptake 52% (normal 15-35%). Markedly elevated.\.br\IMAGING: The thyroid gland is diffusely enlarged. Homogeneous tracer uptake throughout both lobes without focal hot or cold nodules. No significant pyramidal lobe activity. Background salivary gland activity is suppressed.\.br\\.br\IMPRESSION:\.br\1. Diffusely elevated thyroid uptake with homogeneous distribution, consistent with Graves disease.\.br\2. No focal nodular disease.||||||F|||20260303143400||1176347176^RAVENSCROFT^LYDIA^S^^^MD
OBX|2|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Cynthia C. Ellerbe, MD\.br\Nuclear Medicine, ECU Health Medical Center\.br\Date: 2026-03-03 14:34||||||F
```

---

## 12. ORU^R01 - Fluoroscopy upper GI series

```
MSH|^~\&|NUANCE_PS|CAPE_FEAR|CAPEFEAR|CAPE_FEAR|CAPEFEAR||ORU^R01^ORU_R01|MSG20260219101200012|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN80503342^^^CAPEFEAR^MR||OVERCASH^CANDACE^GAIL||19980212|F|||2501 RANDLEMAN RD^^CHARLOTTE^NC^28202||3365559900|||F|||222-21-5371|||N||||||||N
PV1|1|O|FLUORO^^^CAPEFEAR^NOVANT_FMC|||||||RAD||||||||OP|VN20260427028|||||||||||||||||||NOVANTH||||20260219093000
ORC|RE|ORD8891234|FIL2026021900890||CM||||20260219101100|||JTUTT^Tuttle^Julian^V^^^MD|||||CAPEFEAR_PHARM^Cape Fear Valley Medical Center Pharmacy^^CAPEFEAR^^828^5407934^27103
OBR|1|ORD8891234|FIL2026021900890|74241^UGI SERIES WITH AIR^CPT4|||20260219093500|||||||||1354648606^HOLLOWELL^KENT^Q^^^MD||||||20260219101100|||F|||||||1624177020^NESBITT^KENT^J^^^MD&ATTENDING
OBX|1|FT|GDT^REPORT TEXT^LOCAL||UPPER GI SERIES WITH AIR CONTRAST\.br\\.br\CLINICAL INDICATION: Dysphagia, weight loss\.br\\.br\TECHNIQUE: Double-contrast upper GI examination performed with barium and effervescent granules.\.br\\.br\COMPARISON: None\.br\\.br\FINDINGS:\.br\ESOPHAGUS: Normal caliber and mucosal pattern. No stricture, mass, or ulceration. Normal peristalsis. No hiatal hernia.\.br\STOMACH: Normal distensibility. Regular areae gastricae pattern. No mass or ulcer. Normal rugal folds.\.br\DUODENUM: Normal bulb and loop. No mass or ulceration.\.br\\.br\IMPRESSION:\.br\1. Normal upper GI series. No evidence of mass, stricture, or ulceration to explain dysphagia.\.br\2. Recommend ENT evaluation or esophageal motility study if symptoms persist.||||||F|||20260219101100||1624177020^NESBITT^KENT^J^^^MD
OBX|2|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Nigel S. Yarborough, MD\.br\Radiology, Novant Health Forsyth Medical Center\.br\Date: 2026-02-19 10:11||||||F
```

---

## 13. ORU^R01 - Encapsulated PDF radiology report (ED datatype)

```
MSH|^~\&|POWERSCRIBE|IREDELL_MEM|EPIC|IREDELL_MEM|IREDELLMH||ORU^R01^ORU_R01|MSG20260508160000013|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN11670943^^^IREDELLMH^MR||CALDWELL^RODERICK^REID||19960502|M|||308 TIMBER RIDGE LN^^GASTONIA^NC^28052||9195551144|||M|||286-42-9675|||N||||||||N
PV1|1|I|7E^712^A^IREDELLMH|||||||RAD||||||||IP|VN20260418007|||||||||||||||||||DUKE||||20260506090000
ORC|RE|ORD9901234|FIL2026050800901||CM||||20260508155900|||CUNDE^Underwood^Curtis^A^^^MD|||||IREDELLMH_PHARM^Iredell Memorial Hospital Pharmacy^^IREDELLMH^^980^2132672^27710
OBR|1|ORD9901234|FIL2026050800901|71260^CT CHEST W CONTRAST^CPT4|||20260508140000|||||||||1826079802^OKONKWO^KENT^E^^^MD||||||20260508155900|||F|||||||1237781607^OGBURN^JULIAN^C^^^MD&ATTENDING
OBX|1|FT|GDT^REPORT TEXT^LOCAL||CT CHEST WITH IV CONTRAST\.br\\.br\CLINICAL INDICATION: Staging for known right upper lobe non-small cell lung cancer.\.br\\.br\TECHNIQUE: Axial images of the chest with 80 mL Isovue 370 IV contrast.\.br\\.br\COMPARISON: CT chest 2026-03-15\.br\\.br\FINDINGS:\.br\LUNGS: Known 3.2 cm spiculated mass in the right upper lobe, previously 2.8 cm. New 8 mm nodule in the right lower lobe (series 4, image 187). Left lung clear.\.br\MEDIASTINUM: New subcarinal lymph node measuring 1.8 cm short axis, previously 0.9 cm. Right hilar lymphadenopathy measuring 2.1 cm.\.br\PLEURA: Small right pleural effusion, new.\.br\HEART/GREAT VESSELS: Normal cardiac size. No pericardial effusion.\.br\CHEST WALL: No osseous metastatic disease.\.br\\.br\IMPRESSION:\.br\1. Interval growth of right upper lobe mass, now 3.2 cm (previously 2.8 cm). Progressive disease.\.br\2. New right lower lobe pulmonary nodule suspicious for metastasis.\.br\3. Progressive mediastinal and hilar lymphadenopathy.\.br\4. New small right pleural effusion.\.br\5. Overall findings consistent with progressive stage IIIA to possible stage IV disease. Recommend PET/CT and multidisciplinary tumor board.||||||F|||20260508155900||1237781607^OGBURN^JULIAN^C^^^MD
OBX|2|ED|PDF^FORMATTED REPORT^LOCAL||DUKEHEALTH^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2Jq CjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlh Qm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1Bh cmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEg NSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxMjMKPj4Kc3RyZWFt CkJUCi9GMSAxMiBUZgoyNTAgNzAwIFRkCihDVCBDSEVTVCBXSVRIIElWIENPTlRSQVNUKSBU agoyNTAgNjgwIFRkCihGaW5hbCBSZXBvcnQgLSBEdWtlIFJhZGlvbG9neSkgVGoKRVQKZW5k c3RyZWFtCmVuZG9iago1IDAgb2JqCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQov QmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUz NSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNjUgMDAwMDAgbiAKMDAwMDAwMDE1 MCAwMDAwMCBuIAowMDAwMDAwMzAxIDAwMDAwIG4gCjAwMDAwMDA0NzcgMDAwMDAgbiAKdHJh aWxlcgo8PAovU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgo1NTgKJSVFT0YK||||||F|||20260508155900
OBX|3|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Evan W. Blackmon, MD\.br\Thoracic Radiology, Duke University Hospital\.br\Date: 2026-05-08 15:59||||||F
```

---

## 14. MDM^T02 - Interventional radiology procedure note

```
MSH|^~\&|PSCRIBE360|UNC_MED_CTR|UNCMC|UNC_MED_CTR|UNCMC||MDM^T02^MDM_T02|MSG20260401163045014|P|2.5.1|||AL|NE||ASCII|||
EVN|T02|20260401163045
PID|1||MRN66122023^^^UNCMC^MR||CALDWELL^LATASHA^ANN||19560202|F|||2501 RANDLEMAN RD^^MOORESVILLE^NC^28115||7045556611|||M|||207-69-1004|||N||||||||N
PV1|1|I|IR^^^UNCMC^ATRIUM_CMC|||||||RAD||||||||IP|VN20260418023|||||||||||||||||||ATRIUM||||20260401080000
TXA|1|IR|FT|20260401163000|1595454923^INGRAM^EVAN^L^^^MD|AU|||||DOC20260401002||||CM||AV|||
OBR|1|ORD5567890|FIL2026040100345|75984^CHANGE BILIARY DRAINAGE CATHETER^CPT4|||20260401140000|||||||||1595454923^INGRAM^EVAN^L^^^MD||||||20260401163000|||F
OBX|1|FT|GDT^REPORT TEXT^LOCAL||INTERVENTIONAL RADIOLOGY PROCEDURE NOTE\.br\\.br\PROCEDURE: Exchange of right-sided internal/external biliary drainage catheter\.br\\.br\CLINICAL INDICATION: Malignant biliary obstruction, cholangiocarcinoma. Catheter due for scheduled exchange.\.br\\.br\CONSENT: Written informed consent obtained after discussion of risks, benefits, and alternatives.\.br\\.br\TECHNIQUE:\.br\The patient was placed supine on the angiography table. The right upper quadrant was prepped and draped in sterile fashion. Moderate sedation was administered with midazolam 2 mg and fentanyl 100 mcg IV, with continuous monitoring.\.br\\.br\The existing 10F Ring biliary catheter was accessed. A cholangiogram demonstrated patent internal/external drainage with the catheter tip in the duodenum. The catheter was exchanged over a stiff Amplatz guidewire for a new 10F Ring internal/external biliary drainage catheter. Position was confirmed fluoroscopically. Good flow of bile was noted. The catheter was secured to the skin with a StatLock device.\.br\\.br\COMPLICATIONS: None\.br\BLOOD LOSS: Minimal (<5 mL)\.br\SEDATION: Midazolam 2 mg IV, Fentanyl 100 mcg IV\.br\\.br\IMPRESSION:\.br\1. Successful exchange of right biliary drainage catheter.\.br\2. Patent biliary system without evidence of interval progression of obstruction.||||||F|||20260401163000||1595454923^INGRAM^EVAN^L^^^MD
OBX|2|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Marshall D. Plummer, MD\.br\Interventional Radiology, Atrium Health Carolinas Medical Center\.br\Date: 2026-04-01 16:30||||||F
```

---

## 15. ORU^R01 - Bone density DEXA scan

```
MSH|^~\&|POWERSCRIBE|NOVANT_FMC|EPIC|NOVANT_FMC|NOVANTFMC||ORU^R01^ORU_R01|MSG20260227104500015|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN21237479^^^NOVANTFMC^MR||GRIGGS^DEXTER^OSCAR||19741109|M|||5010 SOUTH BLVD^^RALEIGH^NC^27610||9195552277|||F|||552-85-9346|||N||||||||N
PV1|1|O|DEXA^^^NOVANTFMC^UNC_HOSP|||||||RAD||||||||OP|VN20260422021|||||||||||||||||||UNCHLTH||||20260227100000
ORC|RE|ORD7789012|FIL2026022700456||CM||||20260227104400|||LREDD^Reddick^Linus^L^^^MD|||||NOVANTFMC_PHARM^Novant Health Forsyth Medical Center Pharmacy^^NOVANTFMC^^704^9121643^27514
OBR|1|ORD7789012|FIL2026022700456|77080^DEXA BONE DENSITY AXIAL^CPT4|||20260227100500|||||||||1892057215^FAIRCLOTH^BRENDA^G^^^MD||||||20260227104400|||F|||||||1845873282^JERNIGAN^GRETA^C^^^MD&ATTENDING
OBX|1|FT|GDT^REPORT TEXT^LOCAL||BONE DENSITY (DEXA) - AXIAL SKELETON\.br\\.br\CLINICAL INDICATION: 66-year-old postmenopausal female, family history of osteoporosis, for baseline screening.\.br\\.br\TECHNIQUE: Dual-energy X-ray absorptiometry of the lumbar spine (L1-L4) and bilateral proximal femora. Hologic Horizon DXA system.\.br\\.br\COMPARISON: None (baseline study)\.br\\.br\RESULTS:\.br\LUMBAR SPINE (L1-L4):\.br\  BMD: 0.842 g/cm2\.br\  T-score: -2.1\.br\  Z-score: -0.8\.br\\.br\LEFT FEMORAL NECK:\.br\  BMD: 0.695 g/cm2\.br\  T-score: -1.8\.br\  Z-score: -0.5\.br\\.br\LEFT TOTAL HIP:\.br\  BMD: 0.812 g/cm2\.br\  T-score: -1.5\.br\  Z-score: -0.4\.br\\.br\RIGHT FEMORAL NECK:\.br\  BMD: 0.710 g/cm2\.br\  T-score: -1.7\.br\  Z-score: -0.4\.br\\.br\RIGHT TOTAL HIP:\.br\  BMD: 0.825 g/cm2\.br\  T-score: -1.4\.br\  Z-score: -0.3\.br\\.br\FRAX 10-YEAR FRACTURE RISK (without BMD):\.br\  Major osteoporotic: 12%\.br\  Hip fracture: 2.8%\.br\\.br\IMPRESSION:\.br\1. Osteopenia at the lumbar spine (T-score -2.1) and bilateral femoral necks.\.br\2. WHO classification: Osteopenia. Lowest T-score -2.1 at lumbar spine.\.br\3. Recommend calcium/vitamin D supplementation and weight-bearing exercise. Follow-up DEXA in 2 years.||||||F|||20260227104400||1845873282^JERNIGAN^GRETA^C^^^MD
OBX|2|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Lisa M. White, MD\.br\Radiology, UNC Health\.br\Date: 2026-02-27 10:44||||||F
```

---

## 16. ORM^O01 - MRI lumbar spine order

```
MSH|^~\&|CERNER|CATAWBA_VAL|CATAWBAMC|CATAWBA_VAL|CATAWBAMC||ORM^O01^ORM_O01|MSG20260320082000016|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN72043161^^^CATAWBAMC^MR||BURRIS^HENRIETTA^NORMA||19780221|F|||2718 MCGEE RD^^WILMINGTON^NC^28401||3365553388|||M|||588-67-4856|||N||||||||N
PV1|1|O|ORTHO^^^CATAWBAMC^NOVANT_FMC|||||||ORT||||||||OP|VN20260411014|||||||||||||||||||NOVANTH||||20260320080000
ORC|NW|ORD4456789||FIL2026032000567||SC||||20260320082000|||1155069777^RAVENSCROFT^OWEN^K^^^MD|||||603 SHAMROCK DR^^WILMINGTON^NC^28401^WINSTON-SALEM^NC^27103
OBR|1|ORD4456789||72148^MRI LUMBAR SPINE WO CONTRAST^CPT4|||20260320082000|||||||||1176347176^TRUESDALE^NIGEL^N^^^MD|||||||||||3||||||||||ROUTINE
NTE|1||Low back pain radiating to left leg x 6 weeks, failed conservative therapy
```

---

## 17. ORU^R01 - Encapsulated PDF with embedded image report (ED datatype)

```
MSH|^~\&|NUANCE_PS|VIDANT_MC|EPIC|VIDANT_MC|VIDANTMC||ORU^R01^ORU_R01|MSG20260502181500017|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN65685892^^^VIDANTMC^MR||BLACKWOOD^VALERIE^DIANE||19450228|F|||1844 WEAVER DAIRY RD^^FAYETTEVILLE^NC^28303||9195554455|||F|||227-30-6276|||N||||||||N
PV1|1|O|RAD^^^VIDANTMC^WAKEMED|||||||RAD||||||||OP|VN20260416012|||||||||||||||||||WAKEMED||||20260502170000
ORC|RE|ORD6678901|FIL2026050200678||CM||||20260502181400|||FUNDE^Underwood^Francis^K^^^MD|||||VIDANTMC_PHARM^Vidant Medical Center Pharmacy^^VIDANTMC^^828^3354507^27610
OBR|1|ORD6678901|FIL2026050200678|73721^MRI KNEE WO CONTRAST LT^CPT4|||20260502170500|||||||||1624177020^MOSTELLER^ALICIA^T^^^MD||||||20260502181400|||F|||||||1595454923^OGBURN^JULIAN^C^^^MD&ATTENDING
OBX|1|FT|GDT^REPORT TEXT^LOCAL||MRI LEFT KNEE WITHOUT CONTRAST\.br\\.br\CLINICAL INDICATION: Knee pain and locking after twisting injury\.br\\.br\TECHNIQUE: Multiplanar multisequence MRI of the left knee without IV contrast.\.br\\.br\COMPARISON: Left knee radiographs 2026-04-28\.br\\.br\FINDINGS:\.br\MENISCI: Complex tear of the posterior horn and body of the medial meniscus with a displaced bucket-handle fragment extending into the intercondylar notch. Lateral meniscus intact.\.br\LIGAMENTS: ACL is intact with normal signal and morphology. PCL intact. MCL and LCL intact.\.br\CARTILAGE: Focal full-thickness chondral defect of the medial femoral condyle weight-bearing surface measuring approximately 12 x 8 mm. Mild patellofemoral chondromalacia.\.br\BONE: No fracture. Mild bone marrow edema in the medial femoral condyle adjacent to the chondral defect.\.br\JOINT: Small joint effusion. No loose bodies other than the displaced meniscal fragment.\.br\EXTENSOR MECHANISM: Intact.\.br\\.br\IMPRESSION:\.br\1. Complex tear of the medial meniscus with displaced bucket-handle fragment. Surgical consultation recommended.\.br\2. Full-thickness chondral defect of the medial femoral condyle.\.br\3. Small joint effusion.||||||F|||20260502181400||1595454923^OGBURN^JULIAN^C^^^MD
OBX|2|ED|PDF^ANNOTATED REPORT WITH KEY IMAGE^LOCAL||WAKEMED^application^pdf^Base64^JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIK Pj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50 IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUg L1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u dCA8PAovRjEgNSAwIFIKPj4KL1hPYmplY3QgPDwKL0ltZzEgNiAwIFIKPj4KPj4KPj4KZW5k b2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAyMTUKPj4Kc3RyZWFtCkJUCi9GMSAxNCBUZgo1MCA3 NDAgVGQKKE1SSSBMRUZUIEtORUUgLSBLRVkgSU1BR0UgUkVQT1JUKSBUago1MCA3MTAgVGQK KEJ1Y2tldC1IYW5kbGUgVGVhciBNZWRpYWwgTWVuaXNjdXMpIFRqCjUwIDY4MCBUZAooV2Fr ZSBNZWRpY2FsIENlbnRlciBSYWRpb2xvZ3kpIFRqCkVUCnEKMzAwIDAgMCBzMDAgMTUwIDEw MCBjbQovSW1nMSBEbwpRCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PAovVHlwZSAvRm9u dAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EtQm9sZAo+PgplbmRvYmoK NiAwIG9iago8PAovVHlwZSAvWE9iamVjdAovU3VidHlwZSAvSW1hZ2UKL1dpZHRoIDMwMAov SGVpZ2h0IDMwMAovQ29sb3JTcGFjZSAvRGV2aWNlR3JheQovQml0c1BlckNvbXBvbmVudCA4 Ci9GaWx0ZXIgL0RDVERlY29kZQovTGVuZ3RoIDEyOAo+PgpzdHJlYW0K/9j/4AAQSkZJRgAB AQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIs IxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDIAEAgICAYKBgYAAAAAAAAAAAECAxEAITFBElFhcYGR ofDxwdHh/9oADAMBAAIRAxEAPwDuaKKKACiiigBaSiigBaKKKACiiigD/9kKZW5kc3RyZWFt CmVuZG9iago3IDAgb2JqCjw8Ci9TaXplIDcKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjEw MjAKJSVFT0YK||||||F|||20260502181400
OBX|3|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Evan W. Blackmon, MD\.br\Musculoskeletal Radiology, Wake Medical Center\.br\Date: 2026-05-02 18:14||||||F
```

---

## 18. ORU^R01 - Doppler ultrasound carotids

```
MSH|^~\&|PSCRIBE360|CATAWBA_VAL|EPIC|CATAWBA_VAL|CATAWBAMC||ORU^R01^ORU_R01|MSG20260114153000018|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN27317824^^^CATAWBAMC^MR||ZACHARY^WILSON^HENRY||19820914|M|||4010 CAPITAL BLVD^^DURHAM^NC^27701||3365551188|||M|||355-88-3610|||N||||||||N
PV1|1|O|USVASC^^^CATAWBAMC^CONE_MOSES|||||||RAD||||||||OP|VN20260426009|||||||||||||||||||CONE||||20260114143000
ORC|RE|ORD1145678|FIL2026011400234||CM||||20260114152900|||BDUNL^Dunlap^Brent^S^^^MD|||||CATAWBAMC_PHARM^Catawba Valley Medical Center Pharmacy^^CATAWBAMC^^336^9379412^27401
OBR|1|ORD1145678|FIL2026011400234|93880^DOPPLER CAROTIDS BILATERAL^CPT4|||20260114143500|||||||||1783391018^FAIRCLOTH^BRENDA^G^^^MD||||||20260114152900|||F|||||||1299943571^NESBITT^FRANCIS^S^^^MD&ATTENDING
OBX|1|FT|GDT^REPORT TEXT^LOCAL||CAROTID DUPLEX ULTRASOUND, BILATERAL\.br\\.br\CLINICAL INDICATION: TIA symptoms, left-sided weakness, slurred speech resolved\.br\\.br\COMPARISON: None\.br\\.br\FINDINGS:\.br\RIGHT INTERNAL CAROTID ARTERY:\.br\  Peak systolic velocity: 185 cm/s\.br\  End diastolic velocity: 72 cm/s\.br\  ICA/CCA ratio: 2.8\.br\  Interpretation: 50-69% stenosis (SRU criteria)\.br\  Plaque: Heterogeneous plaque at the bifurcation extending into the proximal ICA\.br\\.br\LEFT INTERNAL CAROTID ARTERY:\.br\  Peak systolic velocity: 320 cm/s\.br\  End diastolic velocity: 125 cm/s\.br\  ICA/CCA ratio: 4.6\.br\  Interpretation: 70-99% stenosis (SRU criteria)\.br\  Plaque: Large heterogeneous plaque with irregular surface at the bifurcation\.br\\.br\BILATERAL COMMON CAROTID ARTERIES: Patent with mild atherosclerotic changes\.br\BILATERAL EXTERNAL CAROTID ARTERIES: Patent\.br\BILATERAL VERTEBRAL ARTERIES: Antegrade flow bilaterally\.br\\.br\IMPRESSION:\.br\1. High-grade (70-99%) stenosis of the left internal carotid artery. Vascular surgery consultation recommended urgently given clinical symptoms.\.br\2. Moderate (50-69%) stenosis of the right internal carotid artery.||||||F|||20260114152900||1299943571^NESBITT^FRANCIS^S^^^MD
OBX|2|FT|GDT^CRITICAL^LOCAL||Critical result communicated to Dr. Okonkwo (Neurology) at 15:32 by phone per ACR Practice Parameter for Communication of Diagnostic Imaging Findings.||||||F
OBX|3|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Pierce S. Dunlap, MD\.br\Vascular Imaging, Cone Health Moses Cone Hospital\.br\Date: 2026-01-14 15:29||||||F
```

---

## 19. ORU^R01 - Pediatric abdominal X-ray

```
MSH|^~\&|POWERSCRIBE|UNC_MED_CTR|EPIC|UNC_MED_CTR|UNCMC||ORU^R01^ORU_R01|MSG20260223193012019|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN72768313^^^UNCMC^MR||WHITLEY^BERNICE^ROSE||19950706|F|||1190 MARKET ST^^GREENSBORO^NC^27405||3365557722|||||||||N||||||||N
PV1|1|E|PEDED^^^UNCMC^BRENNER_CH|||||||PED||||||||ER|VN20260430025|||||||||||||||||||BRENNER||||20260223183000
ORC|RE|ORD3356789|FIL2026022300890||CM||||20260223193000|||JNESB^Nesbitt^Julian^W^^^MD|||||UNCMC_PHARM^UNC Medical Center Pharmacy^^UNCMC^^919^3847785^27157
OBR|1|ORD3356789|FIL2026022300890|74000^ABDOMEN 1 VIEW^CPT4|||20260223185000|||||||||1299943571^JERNIGAN^NINA^B^^^MD||||||20260223193000|||F|||||||1826079802^REDDICK^HOLLY^D^^^MD&ATTENDING
OBX|1|FT|GDT^REPORT TEXT^LOCAL||ABDOMEN, SINGLE VIEW (SUPINE)\.br\\.br\CLINICAL INDICATION: 6-year-old male with abdominal pain and vomiting x 12 hours\.br\\.br\COMPARISON: None\.br\\.br\FINDINGS:\.br\BOWEL GAS PATTERN: Mildly dilated loops of small bowel centrally measuring up to 3.0 cm. No definite transition point identified on single view. Air is present in the colon and rectum.\.br\SOFT TISSUES: Unremarkable. No mass effect.\.br\OSSEOUS: No acute abnormality.\.br\FREE AIR: None identified.\.br\\.br\IMPRESSION:\.br\1. Mild small bowel dilation which may represent early or partial small bowel obstruction versus ileus.\.br\2. Recommend clinical correlation and consideration of additional imaging (CT or repeat radiographs with upright/decubitus views) if symptoms persist or worsen.||||||F|||20260223193000||1826079802^REDDICK^HOLLY^D^^^MD
OBX|2|FT|GDT^SIGNATURE^LOCAL||Electronically signed by: Lydia P. Ashworth, MD\.br\Pediatric Radiology, Brenner Children's Hospital\.br\Date: 2026-02-23 19:30||||||F
```

---

## 20. ADT^A04 - Outpatient registration for interventional procedure

```
MSH|^~\&|EPIC|IREDELL_MEM|IREDELLMH|IREDELL_MEM|IREDELLMH||ADT^A04^ADT_A01|MSG20260509070000020|P|2.5.1|||AL|NE||ASCII|||
EVN|A04|20260509070000
PID|1||MRN66417037^^^IREDELLMH^MR||TURNAGE^QUINTON^BERNARD||19760725|M|||7209 CREEDMOOR RD^^HICKORY^NC^28601||9195553399|||M|||358-86-9970|||N||||||||N
PV1|1|O|IR^^^IREDELLMH^DUKE_UNIVERSITY_HOSP|||||||RAD||||||||OP|VN20260429023|||||||||||||||||||DUKE||||20260509070000
PV2||||||||20260509080000|||||||||||||||||||||||||||||N
DG1|1||I83.10^Varicose veins of unspecified lower extremity with inflammation^ICD10|||A
DG1|2||I87.2^Venous insufficiency (chronic)(peripheral)^ICD10|||A
IN1|1|AETNA001|MEDICARE006|MEDICARE PART A|||||GRP998877|||20260101||||PEACOCK^QUINTON^K|SELF|19560414|3340 SILAS CREEK PKWY^^HIGH POINT^NC^27260||||||||||||||||VEN4456012||||||M
AL1|1|DA|IODINE^IODINATED CONTRAST^LOCAL|SV||RASH HIVES
```
