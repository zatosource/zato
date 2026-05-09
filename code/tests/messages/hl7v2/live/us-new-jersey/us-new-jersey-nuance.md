# Nuance PowerScribe - real HL7v2 ER7 messages

## 1. ORU^R01 - CT Head without contrast report, Hackensack University Medical Center

```
MSH|^~\&|POWERSCRIBE|HMH_HUMC|RIS_RECV|HMH|20250310084500||ORU^R01^ORU_R01|PS20250310084500001|P|2.4|||AL|AL
PID|1||MRN30012345^^^HMH^MR||GRIGORYAN^ARTUR^V||19580612|M||2106-3^White^HL70005|84 CEDAR LN^^TEANECK^NJ^07666^US^H||^PRN^PH^^^201^4439217|||M^Married^HL70002|||142-58-7631
PV1|1|I|HUMC_4N^401^A^HMH_HUMC^^^^4 NORTH NEURO||||||3301234^BRENNAN^COLLEEN^^^MD|NEU||||R|||3301234^BRENNAN^COLLEEN^^^MD|IN|||||||||||||||||||HMH_HUMC||||||||20250308190000
ORC|RE|ORD30123456|RAD40234567||CM|||||||3301234^BRENNAN^COLLEEN^^^MD
OBR|1|ORD30123456|RAD40234567|70450^CT HEAD WITHOUT CONTRAST^CPT4||20250310080000|||||||20250310080500||3412345^VOSKANIAN^LEVON^^^MD^RAD||||||20250310084500|||F
OBX|1|ED|PDF^CT Head Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKENUIEhlYWQgV2l0aG91dCBDb250cmFzdCBSZXBvcnQpCi9BdXRob3IgKERyLiBTdGV2ZW4gQ29oZW4pCi9DcmVhdG9yIChOdWFuY2UgUG93ZXJTY3JpYmUgMzYwKQovU3ViamVjdCAoQ1QgSGVhZCBXaXRob3V0IENvbnRyYXN0KQovS2V5d29yZHMgKFJhZGlvbG9neSwgQ1QsIEhlYWQsIE5ldXJvbG9neSkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbNCAwIFJdCi9Db3VudCAxCj4+CmVuZG9iago=||||||F|||20250310084500
OBX|2|FT|36643-5^CT HEAD IMPRESSION^LN||No acute intracranial hemorrhage or mass lesion. Mild small vessel ischemic changes. No midline shift. Ventricles and sulci are age-appropriate.||||||F|||20250310084500||3412345^VOSKANIAN^LEVON^^^MD^RAD
```

---

## 2. ORU^R01 - Chest X-ray PA and lateral report, Jersey Shore University Medical Center

```
MSH|^~\&|POWERSCRIBE|HMH_JSUMC|RIS_RECV|HMH|20250311102300||ORU^R01^ORU_R01|PS20250311102300002|P|2.4|||AL|AL
PID|1||MRN31023456^^^HMH^MR||OMALLEY^SIOBHAN^K||19720405|F||2106-3^White^HL70005|215 FOREST AVE^^BERGENFIELD^NJ^07621^US^H||^PRN^PH^^^551^7128463|||M^Married^HL70002|||281-43-9706
PV1|1|O|JSUMC_RAD^001^A^HMH_JSUMC||||3523456^BOULOS^NADER^^^MD|3523456^BOULOS^NADER^^^MD||RAD||||R||||||41023456||||||||||||||||||HMH_JSUMC||||||||20250311100000
ORC|RE|ORD31234567|RAD41345678||CM|||||||3523456^BOULOS^NADER^^^MD
OBR|1|ORD31234567|RAD41345678|71046^XR CHEST 2 VIEWS^CPT4||20250311100500|||||||20250311101000||3523456^BOULOS^NADER^^^MD^RAD||||||20250311102300|||F
OBX|1|FT|18748-4^CHEST XRAY REPORT^LN||EXAMINATION: Chest PA and lateral\.br\\.br\CLINICAL INDICATION: Cough, shortness of breath\.br\\.br\COMPARISON: Prior chest radiograph dated 01/15/2025\.br\\.br\FINDINGS: Heart size is normal. Mediastinal contours are unremarkable. Lungs are clear bilaterally without focal consolidation, pleural effusion, or pneumothorax. No acute osseous abnormality.\.br\\.br\IMPRESSION: No acute cardiopulmonary process.||||||F|||20250311102300||3523456^BOULOS^NADER^^^MD^RAD
```

---

## 3. ORU^R01 - MRI Lumbar Spine with embedded PDF, RWJBarnabas Health

```
MSH|^~\&|POWERSCRIBE|RWJBH_SBMC|RIS_RECV|RWJBH|20250312154500||ORU^R01^ORU_R01|PS20250312154500003|P|2.4|||AL|AL
PID|1||MRN32034567^^^RWJBH^MR||KRAVCHENKO^TARAS^D||19860719|M||2106-3^White^HL70005|47 KNICKERBOCKER RD^^DUMONT^NJ^07628^US^H||^PRN^PH^^^201^6637492|||S^Single^HL70002|||374-61-8205
PV1|1|O|SBMC_RAD^MRI^A^RWJBH_SBMC||||3634567^DIAMANTOPOULOS^HELEN^^^MD|3634567^DIAMANTOPOULOS^HELEN^^^MD||RAD||||R||||||42034567||||||||||||||||||RWJBH_SBMC||||||||20250312140000
ORC|RE|ORD32345678|RAD42456789||CM|||||||3634567^DIAMANTOPOULOS^HELEN^^^MD
OBR|1|ORD32345678|RAD42456789|72148^MRI LUMBAR SPINE WITHOUT CONTRAST^CPT4||20250312143000|||||||20250312143500||3634567^DIAMANTOPOULOS^HELEN^^^MD^RAD||||||20250312154500|||F
OBX|1|ED|PDF^MRI Lumbar Spine Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKE1SSSBMdW1iYXIgU3BpbmUgV2l0aG91dCBDb250cmFzdCkKL0F1dGhvciAoRHIuIEFuZ2VsYSBNYXJ0aW5leikKL0NyZWF0b3IgKE51YW5jZSBQb3dlclNjcmliZSAzNjApCi9TdWJqZWN0IChNUkkgTHVtYmFyIFNwaW5lKQovS2V5d29yZHMgKFJhZGlvbG9neSwgTVJJLCBMdW1iYXIsIFNwaW5lKQo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMyAwIFIKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFs0IDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCg==||||||F|||20250312154500
OBX|2|FT|36643-5^MRI LUMBAR SPINE IMPRESSION^LN||L4-L5: Mild disc bulge with mild bilateral facet hypertrophy. Mild central canal stenosis. No significant neural foraminal narrowing.\.br\L5-S1: Small disc protrusion slightly eccentric to the left. Mild left neural foraminal narrowing.\.br\No fracture or marrow signal abnormality.||||||F|||20250312154500||3634567^DIAMANTOPOULOS^HELEN^^^MD^RAD
```

---

## 4. ORU^R01 - CT Abdomen Pelvis with contrast, Morristown Medical Center

```
MSH|^~\&|POWERSCRIBE|AHS_MMC|RIS_RECV|AHS|20250313121500||ORU^R01^ORU_R01|PS20250313121500004|P|2.4|||AL|AL
PID|1||MRN33045678^^^AHS^MR||VOLOSHYNA^IRYNA^S||19650130|F||2106-3^White^HL70005|18 CLOSTER DOCK RD^^CLOSTER^NJ^07624^US^H||^PRN^PH^^^201^7750318|||D^Divorced^HL70002|||493-72-8061
PV1|1|E|MMC_ED^22^A^AHS_MMC^^^^EMERGENCY DEPT||||||3745678^GALLAGHER^BRENDAN^^^MD|EM||||E|||3745678^GALLAGHER^BRENDAN^^^MD|EM|||||||||||||||||||AHS_MMC||||||||20250313100000
ORC|RE|ORD33456789|RAD43567890||CM|||||||3745678^GALLAGHER^BRENDAN^^^MD
OBR|1|ORD33456789|RAD43567890|74177^CT ABDOMEN PELVIS WITH CONTRAST^CPT4||20250313110000|||||||20250313110500||3856789^EL-SAYED^KARIM^^^MD^RAD||||||20250313121500|||F
OBX|1|FT|36643-5^CT ABD PELVIS FINDINGS^LN||EXAMINATION: CT Abdomen and Pelvis with IV contrast\.br\\.br\CLINICAL INDICATION: Right lower quadrant pain, nausea\.br\\.br\TECHNIQUE: Axial images of the abdomen and pelvis obtained following IV contrast administration\.br\\.br\FINDINGS:\.br\LIVER: No focal lesion.\.br\GALLBLADDER: Normal. No stones.\.br\PANCREAS: Unremarkable.\.br\SPLEEN: Normal size.\.br\KIDNEYS: No hydronephrosis. Small nonobstructing calculus left kidney, 3mm.\.br\APPENDIX: Dilated to 12mm with periappendiceal fat stranding and a 6mm appendicolith. Findings consistent with acute appendicitis.\.br\NO free air. Small amount of free fluid in the pelvis.\.br\\.br\IMPRESSION:\.br\1. Acute appendicitis with appendicolith.\.br\2. Small nonobstructing left renal calculus, 3mm.||||||F|||20250313121500||3856789^EL-SAYED^KARIM^^^MD^RAD
```

---

## 5. MDM^T02 - Radiology addendum notification, Hackensack UMC

```
MSH|^~\&|POWERSCRIBE|HMH_HUMC|DOC_RECV|HMH|20250314091000||MDM^T02^MDM_T02|PS20250314091000005|P|2.4|||AL|AL
EVN|T02|20250314091000
PID|1||MRN30012345^^^HMH^MR||GRIGORYAN^ARTUR^V||19580612|M||2106-3^White^HL70005|84 CEDAR LN^^TEANECK^NJ^07666^US^H||^PRN^PH^^^201^4439217|||M^Married^HL70002|||142-58-7631
PV1|1|I|HUMC_4N^401^A^HMH_HUMC^^^^4 NORTH NEURO||||||3301234^BRENNAN^COLLEEN^^^MD|NEU||||R|||3301234^BRENNAN^COLLEEN^^^MD|IN|||||||||||||||||||HMH_HUMC||||||||20250308190000
TXA|1|RADAD^Radiology Addendum^LOCAL|TX^Text^HL70191|20250314091000||20250314091000|||||3412345^VOSKANIAN^LEVON^^^MD^RAD||DOC_20250314_001|||AU^Authenticated^HL70271||||||
OBX|1|FT|36643-5^CT HEAD ADDENDUM^LN||ADDENDUM to CT Head Without Contrast dated 03/10/2025:\.br\Upon further review and discussion with neurology, the previously described mild periventricular white matter changes are stable compared to MRI from 09/2024. No new finding to suggest acute process. Clinically correlates with known chronic small vessel disease. No further imaging recommended at this time.\.br\\.br\Levon Voskanian, MD - Attending Radiologist||||||F|||20250314091000||3412345^VOSKANIAN^LEVON^^^MD^RAD
```

---

## 6. ORU^R01 - Mammography screening report with embedded PDF, Riverview Medical Center

```
MSH|^~\&|POWERSCRIBE|HMH_RMC|RIS_RECV|HMH|20250315103000||ORU^R01^ORU_R01|PS20250315103000006|P|2.4|||AL|AL
PID|1||MRN34056789^^^HMH^MR||BENALI^FATIMA^N||19750822|F||2054-5^Black or African American^HL70005|309 WASHINGTON AVE^^HACKENSACK^NJ^07601^US^H||^PRN^PH^^^551^3085712|||M^Married^HL70002|||518-76-2049
PV1|1|O|RMC_MAMM^001^A^HMH_RMC||||3967890^EPSTEIN^MIRIAM^^^MD|3967890^EPSTEIN^MIRIAM^^^MD||RAD||||R||||||44056789||||||||||||||||||HMH_RMC||||||||20250315093000
ORC|RE|ORD34567890|RAD44678901||CM|||||||3967890^EPSTEIN^MIRIAM^^^MD
OBR|1|ORD34567890|RAD44678901|77067^SCREENING MAMMOGRAPHY BILATERAL^CPT4||20250315095000|||||||20250315095500||3967890^EPSTEIN^MIRIAM^^^MD^RAD||||||20250315103000|||F
OBX|1|ED|PDF^Mammography Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFNjcmVlbmluZyBNYW1tb2dyYXBoeSBCaWxhdGVyYWwgUmVwb3J0KQovQXV0aG9yIChEci4gTGlzYSBTY2h3YXJ0eikKL0NyZWF0b3IgKE51YW5jZSBQb3dlclNjcmliZSAzNjApCi9TdWJqZWN0IChCaWxhdGVyYWwgU2NyZWVuaW5nIE1hbW1vZ3JhcGh5KQovS2V5d29yZHMgKE1hbW1vZ3JhcGh5LCBTY3JlZW5pbmcsIEJyZWFzdCwgQkktUkFEUykKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iago=||||||F|||20250315103000
OBX|2|FT|36643-5^MAMMOGRAPHY IMPRESSION^LN||EXAMINATION: Bilateral screening mammography\.br\\.br\COMPARISON: 03/18/2024\.br\\.br\BREAST COMPOSITION: Heterogeneously dense, which may obscure small masses (ACR density C).\.br\\.br\FINDINGS: No suspicious mass, architectural distortion, or suspicious microcalcifications identified bilaterally. Stable benign-appearing calcifications right breast upper outer quadrant.\.br\\.br\IMPRESSION: Negative. Recommend routine annual screening mammography.\.br\BI-RADS Category 1 - Negative.||||||F|||20250315103000||3967890^EPSTEIN^MIRIAM^^^MD^RAD
```

---

## 7. ORU^R01 - US Abdomen complete report, Ocean University Medical Center

```
MSH|^~\&|POWERSCRIBE|HMH_OUMC|RIS_RECV|HMH|20250316140000||ORU^R01^ORU_R01|PS20250316140000007|P|2.4|||AL|AL
PID|1||MRN35067890^^^HMH^MR||OZTURK^MEHMET^F||19810303|M||2131-1^Other Race^HL70005|72 PIERMONT AVE^^CRESSKILL^NJ^07626^US^H||^PRN^PH^^^201^8364510|||M^Married^HL70002|||635-89-1247|||H^Hispanic or Latino^HL70189
PV1|1|O|OUMC_US^001^A^HMH_OUMC||||4078901^FLANAGAN^KATHLEEN^^^MD|4078901^FLANAGAN^KATHLEEN^^^MD||RAD||||R||||||45067890||||||||||||||||||HMH_OUMC||||||||20250316130000
ORC|RE|ORD35678901|RAD45789012||CM|||||||4078901^FLANAGAN^KATHLEEN^^^MD
OBR|1|ORD35678901|RAD45789012|76700^US ABDOMEN COMPLETE^CPT4||20250316132000|||||||20250316132500||4078901^FLANAGAN^KATHLEEN^^^MD^RAD||||||20250316140000|||F
OBX|1|FT|36643-5^US ABDOMEN REPORT^LN||EXAMINATION: Ultrasound Abdomen Complete\.br\\.br\CLINICAL INDICATION: Elevated LFTs, right upper quadrant pain\.br\\.br\FINDINGS:\.br\LIVER: Diffusely echogenic consistent with hepatic steatosis. No focal hepatic lesion. Liver span 17.5 cm.\.br\GALLBLADDER: Multiple gallstones, the largest measuring 1.2 cm. No gallbladder wall thickening or pericholecystic fluid. No sonographic Murphy's sign.\.br\CBD: 4mm, within normal limits.\.br\PANCREAS: Partially obscured by bowel gas, visualized portions unremarkable.\.br\RIGHT KIDNEY: 11.2 cm, normal echogenicity, no hydronephrosis.\.br\LEFT KIDNEY: 11.0 cm, normal echogenicity, no hydronephrosis.\.br\SPLEEN: Normal size at 10.8 cm.\.br\AORTA: Normal caliber.\.br\\.br\IMPRESSION:\.br\1. Hepatic steatosis.\.br\2. Cholelithiasis without acute cholecystitis.||||||F|||20250316140000||4078901^FLANAGAN^KATHLEEN^^^MD^RAD
```

---

## 8. MDM^T02 - Critical result notification, Newark Beth Israel Medical Center

```
MSH|^~\&|POWERSCRIBE|RWJBH_NBI|CRIT_RECV|RWJBH|20250317082000||MDM^T02^MDM_T02|PS20250317082000008|P|2.4|||AL|AL
EVN|T02|20250317082000
PID|1||MRN36078901^^^RWJBH^MR||PAPAZIAN^ANAHIT^L||19430728|F||2028-9^Asian^HL70005|156 ALPINE DR^^ALPINE^NJ^07620^US^H||^PRN^PH^^^551^2047893|||W^Widowed^HL70002|||726-01-4385
PV1|1|E|NBI_ED^08^A^RWJBH_NBI^^^^EMERGENCY DEPT||||||4189012^DONAHUE^PATRICK^^^MD|EM||||E|||4189012^DONAHUE^PATRICK^^^MD|EM|||||||||||||||||||RWJBH_NBI||||||||20250317070000
TXA|1|CR^Critical Result^LOCAL|TX^Text^HL70191|20250317082000||20250317082000|||||4290123^STAVRIDIS^ELENI^^^MD^RAD||DOC_20250317_001|||AU^Authenticated^HL70271||||||
OBX|1|FT|36643-5^CRITICAL RESULT^LN||CRITICAL RESULT - CT HEAD WITHOUT CONTRAST\.br\\.br\FINDING: Large left frontoparietal intraparenchymal hemorrhage measuring approximately 5.2 x 3.8 cm with surrounding edema and 6mm rightward midline shift. Intraventricular extension into the left lateral ventricle.\.br\\.br\CRITICAL VALUE COMMUNICATED TO: Dr. Patrick Donahue, ED attending physician, at 08:18 on 03/17/2025 by Dr. Eleni Stavridis, read back confirmed.||||||F|||20250317082000||4290123^STAVRIDIS^ELENI^^^MD^RAD
```

---

## 9. ORU^R01 - CT Chest PE protocol with embedded PDF, Robert Wood Johnson UH

```
MSH|^~\&|POWERSCRIBE|RWJBH_RWJ|RIS_RECV|RWJBH|20250318111500||ORU^R01^ORU_R01|PS20250318111500009|P|2.4|||AL|AL
PID|1||MRN37089012^^^RWJBH^MR||CHERNOVETSKA^OKSANA^E||19900515|F||2106-3^White^HL70005|33 MADISON AVE^^RIVER EDGE^NJ^07661^US^H||^PRN^PH^^^201^5519743|||S^Single^HL70002|||847-12-3960
PV1|1|E|RWJ_ED^15^A^RWJBH_RWJ^^^^EMERGENCY DEPT||||||4301234^MCCARTHY^SEAN^^^MD|EM||||E|||4301234^MCCARTHY^SEAN^^^MD|EM|||||||||||||||||||RWJBH_RWJ||||||||20250318090000
ORC|RE|ORD37890123|RAD47901234||CM|||||||4301234^MCCARTHY^SEAN^^^MD
OBR|1|ORD37890123|RAD47901234|71275^CT CHEST ANGIOGRAPHY PE PROTOCOL^CPT4||20250318100000|||||||20250318100500||4412345^RASHIDI^DARIUSH^^^MD^RAD||||||20250318111500|||F
OBX|1|ED|PDF^CT PE Protocol Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKENUIENoZXN0IEFuZ2lvZ3JhcGh5IFBFIFByb3RvY29sIFJlcG9ydCkKL0F1dGhvciAoRHIuIFBldGVyIE5vdmFrKQovQ3JlYXRvciAoTnVhbmNlIFBvd2VyU2NyaWJlIDM2MCkKL1N1YmplY3QgKENUIFB1bG1vbmFyeSBFbWJvbGlzbSBQcm90b2NvbCkKL0tleXdvcmRzIChSYWRpb2xvZ3ksIENULCBQdWxtb25hcnkgRW1ib2xpc20sIEFuZ2lvZ3JhcGh5KQo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMyAwIFIKPj4KZW5kb2JqCg==||||||F|||20250318111500
OBX|2|FT|36643-5^CT CHEST PE IMPRESSION^LN||EXAMINATION: CT Chest Angiography, PE Protocol\.br\\.br\CLINICAL INDICATION: Tachycardia, dyspnea, elevated D-dimer\.br\\.br\FINDINGS:\.br\PULMONARY ARTERIES: No filling defect identified within the main, lobar, segmental, or subsegmental pulmonary arteries to suggest pulmonary embolism.\.br\HEART: Normal cardiac size. No pericardial effusion.\.br\LUNGS: Bibasilar atelectasis. No consolidation or pleural effusion.\.br\MEDIASTINUM: No lymphadenopathy.\.br\\.br\IMPRESSION: No evidence of pulmonary embolism. Bibasilar atelectasis.||||||F|||20250318111500||4412345^RASHIDI^DARIUSH^^^MD^RAD
```

---

## 10. ORU^R01 - XR Knee bilateral report, CentraState Medical Center

```
MSH|^~\&|POWERSCRIBE|HMH_CSMC|RIS_RECV|HMH|20250319093000||ORU^R01^ORU_R01|PS20250319093000010|P|2.4|||AL|AL
PID|1||MRN38090123^^^HMH^MR||DELUCA^SALVATORE^A||19560210|M||2106-3^White^HL70005|89 BROADWAY^^WESTWOOD^NJ^07675^US^H||^PRN^PH^^^201^6640183|||M^Married^HL70002|||903-27-4561|||N^Non-Hispanic^HL70189
PV1|1|O|CSMC_RAD^001^A^HMH_CSMC||||4523456^HUSSAIN^AMARA^^^MD|4523456^HUSSAIN^AMARA^^^MD||RAD||||R||||||48090123||||||||||||||||||HMH_CSMC||||||||20250319090000
ORC|RE|ORD38901234|RAD48012345||CM|||||||4523456^HUSSAIN^AMARA^^^MD
OBR|1|ORD38901234|RAD48012345|73565^XR KNEE BILATERAL^CPT4||20250319091000|||||||20250319091500||4523456^HUSSAIN^AMARA^^^MD^RAD||||||20250319093000|||F
OBX|1|FT|36643-5^XR KNEE BILATERAL REPORT^LN||EXAMINATION: Bilateral Knee Radiographs, 3 views each\.br\\.br\CLINICAL INDICATION: Bilateral knee pain, osteoarthritis\.br\\.br\FINDINGS:\.br\RIGHT KNEE: Moderate medial compartment joint space narrowing with marginal osteophytes. Small suprapatellar effusion. No fracture.\.br\LEFT KNEE: Mild medial compartment joint space narrowing with small marginal osteophytes. No effusion. No fracture.\.br\\.br\IMPRESSION:\.br\1. Right knee: Moderate medial compartment osteoarthritis with small joint effusion.\.br\2. Left knee: Mild medial compartment osteoarthritis.||||||F|||20250319093000||4523456^HUSSAIN^AMARA^^^MD^RAD
```

---

## 11. ORU^R01 - MRI Brain with and without contrast with embedded PDF, Hackensack UMC

```
MSH|^~\&|POWERSCRIBE|HMH_HUMC|RIS_RECV|HMH|20250320161500||ORU^R01^ORU_R01|PS20250320161500011|P|2.4|||AL|AL
PID|1||MRN39101234^^^HMH^MR||ELBOUAZIZI^SAMIRA^M||19680923|F||2131-1^Other Race^HL70005|22 DEMAREST AVE^^DEMAREST^NJ^07627^US^H||^PRN^PH^^^551^8812046|||M^Married^HL70002|||061-34-5278|||H^Hispanic or Latino^HL70189
PV1|1|I|HUMC_5S^512^A^HMH_HUMC^^^^5 SOUTH NEURO||||||4634567^KHOURY^GABRIEL^^^MD|NEU||||R|||4634567^KHOURY^GABRIEL^^^MD|IN|||||||||||||||||||HMH_HUMC||||||||20250318100000
ORC|RE|ORD39012345|RAD49123456||CM|||||||4634567^KHOURY^GABRIEL^^^MD
OBR|1|ORD39012345|RAD49123456|70553^MRI BRAIN WITHOUT AND WITH CONTRAST^CPT4||20250320140000|||||||20250320140500||4745678^MANDELBAUM^RACHEL^^^MD^RAD||||||20250320161500|||F
OBX|1|ED|PDF^MRI Brain Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKE1SSSBCcmFpbiBXaXRob3V0IGFuZCBXaXRoIENvbnRyYXN0IFJlcG9ydCkKL0F1dGhvciAoRHIuIE1hcmlhIFJvZHJpZ3VleikKL0NyZWF0b3IgKE51YW5jZSBQb3dlclNjcmliZSAzNjApCi9TdWJqZWN0IChNUkkgQnJhaW4pCi9LZXl3b3JkcyAoTmV1cm9sb2d5LCBNUkksIEJyYWluLCBDb250cmFzdCkKL1Byb2R1Y2VyIChQb3dlclNjcmliZSAzNjAgdjQuMCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iago=||||||F|||20250320161500
OBX|2|FT|36643-5^MRI BRAIN IMPRESSION^LN||EXAMINATION: MRI Brain without and with IV contrast\.br\\.br\CLINICAL INDICATION: New onset seizure\.br\\.br\FINDINGS:\.br\BRAIN PARENCHYMA: Normal gray-white matter differentiation. No acute infarct on diffusion-weighted imaging. No abnormal enhancement following contrast administration.\.br\VENTRICLES: Normal size and configuration.\.br\EXTRA-AXIAL SPACES: No subdural or epidural collection.\.br\POSTERIOR FOSSA: Cerebellum and brainstem are normal.\.br\VASCULAR: Normal flow voids in major intracranial vessels.\.br\\.br\IMPRESSION: Normal MRI of the brain without and with contrast. No intracranial abnormality to explain seizure activity. Clinical correlation recommended.||||||F|||20250320161500||4745678^MANDELBAUM^RACHEL^^^MD^RAD
```

---

## 12. ORU^R01 - CT Cervical Spine report, Overlook Medical Center

```
MSH|^~\&|POWERSCRIBE|AHS_OMC|RIS_RECV|AHS|20250321080000||ORU^R01^ORU_R01|PS20250321080000012|P|2.4|||AL|AL
PID|1||MRN40112345^^^AHS^MR||CELIK^BURAK^T||19910415|M||2106-3^White^HL70005|14 HAWORTH AVE^^HAWORTH^NJ^07641^US^H||^PRN^PH^^^201^3872045|||S^Single^HL70002|||158-43-6729
PV1|1|E|OMC_ED^03^A^AHS_OMC^^^^EMERGENCY DEPT||||||4856789^SULLIVAN^TIMOTHY^^^MD|EM||||E|||4856789^SULLIVAN^TIMOTHY^^^MD|EM|||||||||||||||||||AHS_OMC||||||||20250321020000
ORC|RE|ORD40123456|RAD50234567||CM|||||||4856789^SULLIVAN^TIMOTHY^^^MD
OBR|1|ORD40123456|RAD50234567|72125^CT CERVICAL SPINE WITHOUT CONTRAST^CPT4||20250321030000|||||||20250321030500||4967890^NAKAMURA^KOJI^^^MD^RAD||||||20250321080000|||F
OBX|1|FT|36643-5^CT C-SPINE REPORT^LN||EXAMINATION: CT Cervical Spine without contrast\.br\\.br\CLINICAL INDICATION: MVC, neck pain\.br\\.br\TECHNIQUE: Axial images with sagittal and coronal reformats\.br\\.br\FINDINGS:\.br\ALIGNMENT: Normal cervical lordosis. No listhesis.\.br\VERTEBRAL BODIES: Normal height and morphology C1-C7. No fracture.\.br\DISC SPACES: Preserved. Mild disc osteophyte complex C5-C6.\.br\POSTERIOR ELEMENTS: Intact. No facet widening.\.br\PREVERTEBRAL SOFT TISSUES: Normal.\.br\SPINAL CANAL: No significant stenosis.\.br\\.br\IMPRESSION: No acute cervical spine fracture or malalignment. Mild degenerative change at C5-C6.||||||F|||20250321080000||4967890^NAKAMURA^KOJI^^^MD^RAD
```

---

## 13. MDM^T02 - Radiology peer review notification, Hackensack UMC

```
MSH|^~\&|POWERSCRIBE|HMH_HUMC|QA_RECV|HMH|20250322100000||MDM^T02^MDM_T02|PS20250322100000013|P|2.4|||AL|AL
EVN|T02|20250322100000
PID|1||MRN41123456^^^HMH^MR||SHEVCHUK^MYKOLA^V||19750304|M||2106-3^White^HL70005|510 PARK AVE^^ORADELL^NJ^07649^US^H||^PRN^PH^^^201^9514067|||M^Married^HL70002|||271-54-8903
PV1|1|I|HUMC_3W^308^A^HMH_HUMC^^^^3 WEST MED SURG||||||5078901^TAVITIAN^SARKIS^^^MD|MED||||R|||5078901^TAVITIAN^SARKIS^^^MD|IN|||||||||||||||||||HMH_HUMC||||||||20250320140000
TXA|1|RADPR^Radiology Peer Review^LOCAL|TX^Text^HL70191|20250322100000||20250322100000|||||5189012^GEORGIOU^ANDREAS^^^MD^RAD||DOC_20250322_001|||AU^Authenticated^HL70271||||||
OBX|1|FT|36643-5^PEER REVIEW^LN||PEER REVIEW NOTIFICATION\.br\Original Study: CT Abdomen Pelvis with Contrast, 03/20/2025\.br\Original Interpretation by: Dr. J. Kim\.br\Reviewed by: Dr. Andreas Georgiou\.br\\.br\Discrepancy: Score 2 - Diagnosis not ordinarily expected to be made, unlikely to be significant.\.br\Finding: 4mm left adrenal nodule noted on review, not mentioned in original report. This is a benign-appearing incidentaloma. No clinical significance in current context.||||||F|||20250322100000||5189012^GEORGIOU^ANDREAS^^^MD^RAD
```

---

## 14. ORU^R01 - XR Chest portable AP report, Clara Maass Medical Center

```
MSH|^~\&|POWERSCRIBE|RWJBH_CMMC|RIS_RECV|RWJBH|20250323071500||ORU^R01^ORU_R01|PS20250323071500014|P|2.4|||AL|AL
PID|1||MRN42134567^^^RWJBH^MR||FITZGERALD^DERMOT^D||19470618|M||2106-3^White^HL70005|41 NEW BRIDGE RD^^NEW MILFORD^NJ^07646^US^H||^PRN^PH^^^551^6034182|||W^Widowed^HL70002|||364-71-8905
PV1|1|I|CMMC_ICU^104^A^RWJBH_CMMC^^^^ICU||||||5290123^HADID^LAYLA^^^MD|MED||||E|||5290123^HADID^LAYLA^^^MD|IN|||||||||||||||||||RWJBH_CMMC||||||||20250322200000
ORC|RE|ORD42234567|RAD52345678||CM|||||||5290123^HADID^LAYLA^^^MD
OBR|1|ORD42234567|RAD52345678|71045^XR CHEST SINGLE VIEW^CPT4||20250323060000|||||||20250323060500||5301234^LOMBARDI^MARCO^^^MD^RAD||||||20250323071500|||F
OBX|1|FT|18748-4^CHEST XRAY PORTABLE REPORT^LN||EXAMINATION: Chest Portable AP\.br\\.br\CLINICAL INDICATION: Shortness of breath, CHF\.br\\.br\COMPARISON: 03/22/2025\.br\\.br\FINDINGS: Endotracheal tube tip 4.5 cm above the carina, appropriate position. Right subclavian central line tip in the SVC. Heart is enlarged, stable. Bilateral pleural effusions, moderate right, small left, slightly worsened. Pulmonary vascular congestion. No pneumothorax.\.br\\.br\IMPRESSION:\.br\1. Appropriately positioned endotracheal tube and right subclavian central line.\.br\2. Worsening bilateral pleural effusions and pulmonary vascular congestion consistent with decompensated heart failure.||||||F|||20250323071500||5301234^LOMBARDI^MARCO^^^MD^RAD
```

---

## 15. ORU^R01 - US Thyroid with embedded PDF, Bayshore Medical Center

```
MSH|^~\&|POWERSCRIBE|HMH_BMC|RIS_RECV|HMH|20250324143000||ORU^R01^ORU_R01|PS20250324143000015|P|2.4|||AL|AL
PID|1||MRN43145678^^^HMH^MR||HOVHANNISYAN^NARINE^S||19820711|F||2028-9^Asian^HL70005|7 HARRINGTON AVE^^HARRINGTON PARK^NJ^07640^US^H||^PRN^PH^^^201^7453021|||M^Married^HL70002|||492-78-6013
PV1|1|O|BMC_US^001^A^HMH_BMC||||5412345^CALLAHAN^MOIRA^^^MD|5412345^CALLAHAN^MOIRA^^^MD||RAD||||R||||||53145678||||||||||||||||||HMH_BMC||||||||20250324133000
ORC|RE|ORD43345678|RAD53456789||CM|||||||5412345^CALLAHAN^MOIRA^^^MD
OBR|1|ORD43345678|RAD53456789|76536^US THYROID^CPT4||20250324135000|||||||20250324135500||5412345^CALLAHAN^MOIRA^^^MD^RAD||||||20250324143000|||F
OBX|1|ED|PDF^US Thyroid Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFVsdHJhc291bmQgVGh5cm9pZCBSZXBvcnQpCi9BdXRob3IgKERyLiBTYXJhaCBPbGl2ZXIpCi9DcmVhdG9yIChOdWFuY2UgUG93ZXJTY3JpYmUgMzYwKQovU3ViamVjdCAoVGh5cm9pZCBVbHRyYXNvdW5kKQovS2V5d29yZHMgKFRoeXJvaWQsIFVsdHJhc291bmQsIE5vZHVsZSwgVEktUkFEUykKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iago=||||||F|||20250324143000
OBX|2|FT|36643-5^US THYROID IMPRESSION^LN||EXAMINATION: Ultrasound Thyroid\.br\\.br\CLINICAL INDICATION: Palpable thyroid nodule\.br\\.br\FINDINGS:\.br\RIGHT LOBE: Measures 5.2 x 2.1 x 1.8 cm. Heterogeneous echotexture. A predominantly solid, hypoechoic nodule measuring 1.4 x 1.0 x 0.9 cm in the mid pole with irregular margins and punctate echogenic foci.\.br\LEFT LOBE: Measures 4.8 x 1.9 x 1.7 cm. Homogeneous. A 0.5 cm simple cyst in the lower pole.\.br\ISTHMUS: 3mm, normal.\.br\\.br\IMPRESSION:\.br\1. Right thyroid lobe 1.4 cm solid hypoechoic nodule with suspicious features (irregular margins, microcalcifications). TI-RADS 5 - Highly suspicious. FNA biopsy recommended.\.br\2. Left thyroid lobe 0.5 cm simple cyst, benign. TI-RADS 1.||||||F|||20250324143000||5412345^CALLAHAN^MOIRA^^^MD^RAD
```

---

## 16. ORU^R01 - XR Lumbar Spine report, Jersey City Medical Center

```
MSH|^~\&|POWERSCRIBE|RWJBH_JCMC|RIS_RECV|RWJBH|20250325101500||ORU^R01^ORU_R01|PS20250325101500016|P|2.4|||AL|AL
PID|1||MRN44156789^^^RWJBH^MR||TRABELSI^YOUSSEF^A||19790405|M||2106-3^White^HL70005|128 PARK RIDGE RD^^PARK RIDGE^NJ^07656^US^H||^PRN^PH^^^973^2048713|||M^Married^HL70002|||582-90-1437
PV1|1|O|JCMC_RAD^001^A^RWJBH_JCMC||||5523456^DONOVAN^BRIGID^^^MD|5523456^DONOVAN^BRIGID^^^MD||RAD||||R||||||54156789||||||||||||||||||RWJBH_JCMC||||||||20250325093000
ORC|RE|ORD44456789|RAD54567890||CM|||||||5523456^DONOVAN^BRIGID^^^MD
OBR|1|ORD44456789|RAD54567890|72100^XR LUMBAR SPINE 2 OR 3 VIEWS^CPT4||20250325095000|||||||20250325095500||5523456^DONOVAN^BRIGID^^^MD^RAD||||||20250325101500|||F
OBX|1|FT|36643-5^XR LUMBAR SPINE REPORT^LN||EXAMINATION: Lumbar Spine 3 views\.br\\.br\CLINICAL INDICATION: Low back pain, sciatica\.br\\.br\COMPARISON: None available\.br\\.br\FINDINGS:\.br\ALIGNMENT: Normal lumbar lordosis maintained.\.br\VERTEBRAL BODIES: Normal height. No compression fracture. Mild anterior osteophytes L3-L5.\.br\DISC SPACES: Mild narrowing at L4-L5 and L5-S1.\.br\POSTERIOR ELEMENTS: No pars defect identified.\.br\SI JOINTS: Unremarkable.\.br\\.br\IMPRESSION: Mild degenerative changes L3-S1 level. No acute fracture or significant listhesis.||||||F|||20250325101500||5523456^DONOVAN^BRIGID^^^MD^RAD
```

---

## 17. MDM^T02 - Final report notification, Monmouth Medical Center

```
MSH|^~\&|POWERSCRIBE|RWJBH_MMC_LB|DOC_RECV|RWJBH|20250326120000||MDM^T02^MDM_T02|PS20250326120000017|P|2.4|||AL|AL
EVN|T02|20250326120000
PID|1||MRN45167890^^^RWJBH^MR||BENSALEM^YASMINE^A||19830917|F||2131-1^Other Race^HL70005|65 WOODCLIFF AVE^^WOODCLIFF LAKE^NJ^07677^US^H||^PRN^PH^^^201^4517832|||S^Single^HL70002|||694-80-1235|||H^Hispanic or Latino^HL70189
PV1|1|O|MMC_LB_RAD^001^A^RWJBH_MMC_LB||||5634567^ABRAMYAN^GEVORG^^^MD|5634567^ABRAMYAN^GEVORG^^^MD||RAD||||R||||||55167890||||||||||||||||||RWJBH_MMC_LB||||||||20250326110000
TXA|1|RAD^Radiology Report^LOCAL|TX^Text^HL70191|20250326120000||20250326120000|||||5634567^ABRAMYAN^GEVORG^^^MD^RAD||DOC_20250326_001|||AU^Authenticated^HL70271||||||
OBX|1|FT|36643-5^FINAL REPORT NOTIFICATION^LN||REPORT FINALIZED\.br\Study: XR Ankle Right 3 views, 03/26/2025\.br\Patient: Yasmine A. Bensalem, MRN 45167890\.br\Interpreting Radiologist: Dr. Gevorg Abramyan\.br\\.br\IMPRESSION: Nondisplaced distal fibula fracture (lateral malleolus). No talar shift. Recommend orthopedic consultation.||||||F|||20250326120000||5634567^ABRAMYAN^GEVORG^^^MD^RAD
```

---

## 18. ORU^R01 - MRI Knee report, Chilton Medical Center

```
MSH|^~\&|POWERSCRIBE|AHS_CHMC|RIS_RECV|AHS|20250327091500||ORU^R01^ORU_R01|PS20250327091500018|P|2.4|||AL|AL
PID|1||MRN46178901^^^AHS^MR||KOROLYOVA^TETIANA^M||19880120|F||2106-3^White^HL70005|53 HILLSDALE AVE^^HILLSDALE^NJ^07642^US^H||^PRN^PH^^^551^3290487|||M^Married^HL70002|||713-06-2845|||N^Non-Hispanic^HL70189
PV1|1|O|CHMC_MRI^001^A^AHS_CHMC||||5745678^FEINBERG^NATHANIEL^^^MD|5745678^FEINBERG^NATHANIEL^^^MD||RAD||||R||||||56178901||||||||||||||||||AHS_CHMC||||||||20250327083000
ORC|RE|ORD46567890|RAD56678901||CM|||||||5745678^FEINBERG^NATHANIEL^^^MD
OBR|1|ORD46567890|RAD56678901|73721^MRI KNEE WITHOUT CONTRAST LEFT^CPT4||20250327084000|||||||20250327084500||5745678^FEINBERG^NATHANIEL^^^MD^RAD||||||20250327091500|||F
OBX|1|FT|36643-5^MRI LEFT KNEE REPORT^LN||EXAMINATION: MRI Left Knee without contrast\.br\\.br\CLINICAL INDICATION: Left knee pain and locking after twisting injury\.br\\.br\FINDINGS:\.br\MENISCI: Complex tear of the medial meniscus body and posterior horn extending to the inferior articular surface. Lateral meniscus intact.\.br\LIGAMENTS: ACL and PCL intact with normal signal and tension. MCL and LCL intact.\.br\CARTILAGE: Focal full-thickness cartilage defect medial femoral condyle, 8mm.\.br\BONE: Mild bone marrow edema medial femoral condyle. No fracture.\.br\EFFUSION: Moderate joint effusion.\.br\POPLITEAL FOSSA: Small Baker's cyst.\.br\\.br\IMPRESSION:\.br\1. Complex medial meniscus tear involving body and posterior horn.\.br\2. Full-thickness cartilage defect medial femoral condyle.\.br\3. Moderate joint effusion. Small Baker's cyst.||||||F|||20250327091500||5745678^FEINBERG^NATHANIEL^^^MD^RAD
```

---

## 19. ORU^R01 - CT Sinus report, Community Medical Center

```
MSH|^~\&|POWERSCRIBE|RWJBH_CMC|RIS_RECV|RWJBH|20250328141000||ORU^R01^ORU_R01|PS20250328141000019|P|2.4|||AL|AL
PID|1||MRN47189012^^^RWJBH^MR||COSTANTINO^VINCENZO^J||19650812|M||2106-3^White^HL70005|201 EMERSON RD^^EMERSON^NJ^07630^US^H||^PRN^PH^^^201^5780694|||M^Married^HL70002|||836-14-2509|||N^Non-Hispanic^HL70189
PV1|1|O|CMC_RAD^001^A^RWJBH_CMC||||5856789^TAHERIAN^REZA^^^MD|5856789^TAHERIAN^REZA^^^MD||RAD||||R||||||57189012||||||||||||||||||RWJBH_CMC||||||||20250328133000
ORC|RE|ORD47678901|RAD57789012||CM|||||||5856789^TAHERIAN^REZA^^^MD
OBR|1|ORD47678901|RAD57789012|70486^CT SINUS WITHOUT CONTRAST^CPT4||20250328134000|||||||20250328134500||5856789^TAHERIAN^REZA^^^MD^RAD||||||20250328141000|||F
OBX|1|FT|36643-5^CT SINUS REPORT^LN||EXAMINATION: CT Sinuses without contrast\.br\\.br\CLINICAL INDICATION: Chronic sinusitis, preoperative planning\.br\\.br\FINDINGS:\.br\MAXILLARY SINUSES: Bilateral mucosal thickening, up to 8mm on the right, 5mm on the left. No air-fluid level.\.br\ETHMOID SINUSES: Partial opacification of anterior ethmoid air cells bilaterally.\.br\FRONTAL SINUSES: Clear.\.br\SPHENOID SINUSES: Clear.\.br\OSTIOMEATAL COMPLEXES: Bilateral narrowing with partial obstruction.\.br\NASAL SEPTUM: Mild leftward deviation.\.br\TURBINATES: Bilateral inferior turbinate hypertrophy.\.br\\.br\IMPRESSION:\.br\1. Chronic bilateral maxillary and anterior ethmoid sinusitis.\.br\2. Bilateral ostiomeatal complex narrowing.\.br\3. Mild nasal septal deviation to the left with bilateral inferior turbinate hypertrophy.||||||F|||20250328141000||5856789^TAHERIAN^REZA^^^MD^RAD
```

---

## 20. ORU^R01 - XR Hip bilateral report with embedded PDF, Saint Peter's University Hospital

```
MSH|^~\&|POWERSCRIBE|SPUH|RIS_RECV|SPUH|20250329103000||ORU^R01^ORU_R01|PS20250329103000020|P|2.4|||AL|AL
PID|1||MRN48190123^^^SPUH^MR||MANSOUR^HUDA^L||19401205|F||2054-5^Black or African American^HL70005|9 SADDLE RIVER RD^^SADDLE RIVER^NJ^07458^US^H||^PRN^PH^^^732^6025814|||W^Widowed^HL70002|||905-21-4673
PV1|1|O|SPUH_RAD^001^A^SPUH||||5967890^WEISSMAN^JOSHUA^^^MD|5967890^WEISSMAN^JOSHUA^^^MD||RAD||||R||||||58190123||||||||||||||||||SPUH||||||||20250329093000
ORC|RE|ORD48789012|RAD58890123||CM|||||||5967890^WEISSMAN^JOSHUA^^^MD
OBR|1|ORD48789012|RAD58890123|73522^XR HIP BILATERAL^CPT4||20250329095000|||||||20250329095500||5967890^WEISSMAN^JOSHUA^^^MD^RAD||||||20250329103000|||F
OBX|1|ED|PDF^XR Hip Bilateral Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKEJpbGF0ZXJhbCBIaXAgUmFkaW9ncmFwaCBSZXBvcnQpCi9BdXRob3IgKERyLiBEYXZpZCBLYXBsYW4pCi9DcmVhdG9yIChOdWFuY2UgUG93ZXJTY3JpYmUgMzYwKQovU3ViamVjdCAoQmlsYXRlcmFsIEhpcCBSYWRpb2dyYXBocykKL0tleXdvcmRzIChIaXAsIFJhZGlvZ3JhcGgsIE9zdGVvYXJ0aHJpdGlzLCBPcnRob3BlZGljcykKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iago=||||||F|||20250329103000
OBX|2|FT|36643-5^XR HIP BILATERAL IMPRESSION^LN||EXAMINATION: Bilateral Hip Radiographs, AP and Lateral\.br\\.br\CLINICAL INDICATION: Bilateral hip pain, difficulty ambulating\.br\\.br\FINDINGS:\.br\RIGHT HIP: Severe joint space narrowing with subchondral sclerosis, marginal osteophytes, and subchondral cyst formation. Findings consistent with advanced osteoarthritis.\.br\LEFT HIP: Moderate joint space narrowing with marginal osteophytes. Less severe than right.\.br\PELVIS: No fracture. No lytic or blastic lesion.\.br\\.br\IMPRESSION:\.br\1. Severe right hip osteoarthritis. Consider orthopedic evaluation for possible total hip arthroplasty.\.br\2. Moderate left hip osteoarthritis.||||||F|||20250329103000||5967890^WEISSMAN^JOSHUA^^^MD^RAD
```
