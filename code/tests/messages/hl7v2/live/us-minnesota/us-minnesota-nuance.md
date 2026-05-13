# Nuance PowerScribe - real HL7v2 ER7 messages

## 1. ORU^R01 - Chest X-ray PA and lateral report with embedded PDF from Mayo Clinic

```
MSH|^~\&|POWERSCRIBE|MAYO_RAD|EHR|MAYOCLINIC|20250312143500||ORU^R01|PS-MAYO-20250312-001234|P|2.4|||AL|NE
PID|1||MRN-44098712^^^MAYO^MR||Lindquist^Margaret^Louise^^||19580324|F||W|3215 Viola Rd NE^^Rochester^MN^55906^USA||^PRN^PH^^1^507^2893412|||||||482-71-9035
PV1|1|O|RAD^XRAY^01||||1938274^Stavros^Eric^W^^^MD|1938274^Stavros^Eric^W^^^MD||RAD||||||||V|VN-20250312-0087^^^MAYO^VN|||||||||||||||||||||||||20250312090000
ORC|RE|ORD-RAD-20250312-087^MAYO|PS-RPT-20250312-001234^POWERSCRIBE||||1^^^20250312090000^^R||20250312143500|1938274^Stavros^Eric^W^^^MD|1938274^Stavros^Eric^W^^^MD|1938274^Stavros^Eric^W^^^MD||^WPN^PH^^1^507^2845000||||||MAYO^Mayo Clinic
OBR|1|ORD-RAD-20250312-087^MAYO|PS-RPT-20250312-001234^POWERSCRIBE|71020^XR CHEST PA AND LATERAL^CPT4|||20250312091500|||||||||||1938274^Stavros^Eric^W^^^MD||RAD-ACC-20250312-0087||||20250312143500|||F|||||||4029183^Engstrom^Anna^M^^^MD^Radiology
OBX|1|ED|71020^XR CHEST PA AND LATERAL^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKENoZXN0IFgtUmF5IFBBIGFuZCBMYXRlcmFsIFJlcG9ydCkKL0F1dGhvciAoRHIuIEFubmEgTGluZGJlcmcsIE1EKQovQ3JlYXRvciAoTnVhbmNlIFBvd2VyU2NyaWJlIDM2MCkKL1Byb2R1Y2VyIChOdWFuY2UgSGVhbHRoY2FyZSkKL0NyZWF0aW9uRGF0ZSAoRDoyMDI1MDMxMjE0MzUwMC0wNjAwKQo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMyAwIFIKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFs0IDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAzIDAgUgovQ29udGVudHMgNSAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNiAwIFIKPj4KPj4KPj4KZW5kb2JqCjUgMCBvYmoKPDwKL0xlbmd0aCAxNTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgozNiA3NTYgVGQKKENoZXN0IFgtUmF5IFBBIGFuZCBMYXRlcmFsKSBUagoKMzYgNzMwIFRkCihJTVBSRVNTSU9OOiBObyBhY3V0ZSBjYXJkaW9wdWxtb25hcnkgZGlzZWFzZS4pIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNiAwIG9iago8PAovVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCnhyZWYKMCA3CjAwMDAwMDAwMDAgNjU1MzUgZgogCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDIyOCAwMDAwMCBuIAowMDAwMDAwMjc3IDAwMDAwIG4gCjAwMDAwMDAzODAgMDAwMDAgbiAKMDAwMDAwMDUzMCAwMDAwMCBuIAowMDAwMDAwNzMwIDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNwovUm9vdCAyIDAgUgo+PgpzdGFydHhyZWYKODIwCiUlRU9GCg==||||||F
OBX|2|TX|71020^XR CHEST PA AND LATERAL^CPT4|2|CHEST X-RAY PA AND LATERAL~~CLINICAL INDICATION: Cough, shortness of breath.~~COMPARISON: Chest X-ray dated 2024-11-15.~~FINDINGS:~The lungs are clear bilaterally without focal consolidation, pleural effusion, or pneumothorax. The cardiac silhouette is normal in size. The mediastinal contours are unremarkable. The osseous structures are intact without acute fracture.~~IMPRESSION: No acute cardiopulmonary disease.||||||F
```

---

## 2. ORU^R01 - CT abdomen and pelvis report with embedded PDF from Allina Health

```
MSH|^~\&|POWERSCRIBE|ALLINA_RAD|EHR|ALLINA|20250418102300||ORU^R01|PS-ALLI-20250418-003412|P|2.4|||AL|NE
PID|1||MRN-91023456^^^ALLINA^MR||Warsame^Abdirahman^Osman^^||19670815|M||B|1842 University Ave^^St. Paul^MN^55104^USA||^PRN^PH^^1^651^4829103|||||||375-42-6018
PV1|1|O|RAD^CT^03||||2810493^Bjornson^Mark^T^^^MD|2810493^Bjornson^Mark^T^^^MD||RAD||||||||V|VN-20250418-0214^^^ALLINA^VN|||||||||||||||||||||||||20250418080000
ORC|RE|ORD-RAD-20250418-214^ALLINA|PS-RPT-20250418-003412^POWERSCRIBE||||1^^^20250418080000^^R||20250418102300|2810493^Bjornson^Mark^T^^^MD|2810493^Bjornson^Mark^T^^^MD|2810493^Bjornson^Mark^T^^^MD||^WPN^PH^^1^651^2413000||||||ALLINA^Allina Health
OBR|1|ORD-RAD-20250418-214^ALLINA|PS-RPT-20250418-003412^POWERSCRIBE|74178^CT ABD AND PELVIS WITH CONTRAST^CPT4|||20250418083000|||||||||||2810493^Bjornson^Mark^T^^^MD||RAD-ACC-20250418-0214||||20250418102300|||F|||||||5047291^Solberg^Christine^E^^^MD^Radiology
OBX|1|ED|74178^CT ABD AND PELVIS WITH CONTRAST^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKENUIEFiZG9tZW4gYW5kIFBlbHZpcyB3aXRoIENvbnRyYXN0KQovQXV0aG9yIChEci4gQ2hyaXN0aW5lIERhaGwsIE1EKQovQ3JlYXRvciAoTnVhbmNlIFBvd2VyU2NyaWJlIDM2MCkKL1Byb2R1Y2VyIChOdWFuY2UgSGVhbHRoY2FyZSkKL0NyZWF0aW9uRGF0ZSAoRDoyMDI1MDQxODEwMjMwMC0wNTAwKQo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMyAwIFIKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFs0IDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAzIDAgUgovQ29udGVudHMgNSAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNiAwIFIKPj4KPj4KPj4KZW5kb2JqCjUgMCBvYmoKPDwKL0xlbmd0aCAyODAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgozNiA3NTYgVGQKKENUIEFiZG9tZW4gYW5kIFBlbHZpcyB3aXRoIENvbnRyYXN0KSBUagoKMzYgNzMwIFRkCihGSU5ESU5HUzogSGVwYXRpYyBzdGVhdG9zaXMuIE5vIGZvY2FsIGxlc2lvbi4pIFRqCgozNiA3MTAgVGQKKElNUFJFU1NJT046IE1pbGQgaGVwYXRpYyBzdGVhdG9zaXMuIE5vIGFjdXRlIGFiZG9taW5hbCBwYXRob2xvZ3kuKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjYgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNwowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDI0NSAwMDAwMCBuIAowMDAwMDAwMjk0IDAwMDAwIG4gCjAwMDAwMDAzOTcgMDAwMDAgbiAKMDAwMDAwMDU0NyAwMDAwMCBuIAowMDAwMDAwODc3IDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNwovUm9vdCAyIDAgUgo+PgpzdGFydHhyZWYKOTY3CiUlRU9GCg==||||||F
OBX|2|TX|74178^CT ABD AND PELVIS WITH CONTRAST^CPT4|2|CT ABDOMEN AND PELVIS WITH IV CONTRAST~~CLINICAL INDICATION: Abdominal pain, rule out appendicitis.~~TECHNIQUE: Helical CT of the abdomen and pelvis following administration of 100 mL Omnipaque 350 IV.~~COMPARISON: None.~~FINDINGS:~Liver: Mild hepatic steatosis. No focal lesion.~Gallbladder: Normal. No gallstones.~Pancreas: Normal in size and attenuation.~Spleen: Normal.~Kidneys: Normal bilaterally. No hydronephrosis.~Appendix: Normal in caliber measuring 5mm. No periappendiceal fat stranding.~Bowel: Normal. No obstruction or wall thickening.~Lymph nodes: No pathologically enlarged lymph nodes.~~IMPRESSION:~1. Mild hepatic steatosis.~2. No acute abdominal pathology. Normal appendix.||||||F
```

---

## 3. ORU^R01 - MRI brain with and without contrast from Fairview Health Services

```
MSH|^~\&|POWERSCRIBE|FAIRVIEW_RAD|EHR|FAIRVIEW|20250527161200||ORU^R01|PS-FV-20250527-005678|P|2.4|||AL|NE
PID|1||MRN-72034567^^^FAIRVIEW^MR||Moua^Pa^Ying^^||19790512|F||A|4518 Minnehaha Ave^^Minneapolis^MN^55406^USA||^PRN^PH^^1^612^7298034|||||||291-53-8470
PV1|1|O|RAD^MRI^02||||3195028^Overby^Anna^K^^^MD|3195028^Overby^Anna^K^^^MD||RAD||||||||V|VN-20250527-0345^^^FAIRVIEW^VN|||||||||||||||||||||||||20250527130000
ORC|RE|ORD-RAD-20250527-345^FAIRVIEW|PS-RPT-20250527-005678^POWERSCRIBE||||1^^^20250527130000^^R||20250527161200|3195028^Overby^Anna^K^^^MD|3195028^Overby^Anna^K^^^MD|3195028^Overby^Anna^K^^^MD||^WPN^PH^^1^612^2734000||||||FAIRVIEW^Fairview Health Services
OBR|1|ORD-RAD-20250527-345^FAIRVIEW|PS-RPT-20250527-005678^POWERSCRIBE|70553^MRI BRAIN W AND WO CONTRAST^CPT4|||20250527133000|||||||||||3195028^Overby^Anna^K^^^MD||RAD-ACC-20250527-0345||||20250527161200|||F|||||||6203841^Nygaard^Lars^P^^^MD^Neuroradiology
OBX|1|ED|70553^MRI BRAIN W AND WO CONTRAST^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKE1SSSBCcmFpbiB3aXRoIGFuZCB3aXRob3V0IENvbnRyYXN0KQovQXV0aG9yIChEci4gTGFycyBCZXJnbWFuLCBNRCkKL0NyZWF0b3IgKE51YW5jZSBQb3dlclNjcmliZSAzNjApCi9Qcm9kdWNlciAoTnVhbmNlIEhlYWx0aGNhcmUpCi9DcmVhdGlvbkRhdGUgKEQ6MjAyNTA1MjcxNjEyMDAtMDUwMCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbNCAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCj4+CmVuZG9iago0IDAgb2JqCjw8Ci9UeXBlIC9QYWdlCi9QYXJlbnQgMyAwIFIKL0NvbnRlbnRzIDUgMCBSCi9SZXNvdXJjZXMgPDwKL0ZvbnQgPDwKL0YxIDYgMCBSCj4+Cj4+Cj4+CmVuZG9iago1IDAgb2JqCjw8Ci9MZW5ndGggMzIwCj4+CnN0cmVhbQpCVAovRjEgMTIgVGYKMzYgNzU2IFRkCihNUkkgQnJhaW4gV2l0aCBhbmQgV2l0aG91dCBDb250cmFzdCkgVGoKCjM2IDczMCBUZAooSU1QUkVTU0lPTjogU21hbGwgbGVmdCBwYXJpZXRhbCBtZW5pbmdpb21hLiBObyBhY3V0ZSBpbnRyYWNyYW5pYWwgcGF0aG9sb2d5LikgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago2IDAgb2JqCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDcKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAyNjAgMDAwMDAgbiAKMDAwMDAwMDMwOSAwMDAwMCBuIAowMDAwMDAwNDEyIDAwMDAwIG4gCjAwMDAwMDA1NjIgMDAwMDAgbiAKMDAwMDAwMDkzMiAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDcKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjEwMjIKJSVFT0YK||||||F
OBX|2|TX|70553^MRI BRAIN W AND WO CONTRAST^CPT4|2|MRI BRAIN WITH AND WITHOUT IV CONTRAST~~CLINICAL INDICATION: Headaches, rule out intracranial pathology.~~TECHNIQUE: Multiplanar, multisequence MRI of the brain performed before and after IV administration of 15 mL Gadavist.~~COMPARISON: None.~~FINDINGS:~Brain parenchyma: Normal gray-white matter differentiation. No acute infarct on diffusion-weighted imaging. No hemorrhage.~Ventricles: Normal in size and morphology.~Extra-axial spaces: Small 8mm extra-axial mass along the left parietal convexity with homogeneous enhancement, consistent with meningioma.~Midline structures: No shift.~Posterior fossa: Normal cerebellum and brainstem.~Orbits: Normal.~~IMPRESSION:~1. Small left parietal meningioma measuring 8mm. Recommend follow-up MRI in 12 months.~2. No acute intracranial pathology.||||||F
```

---

## 4. MDM^T02 - Transcription notification for mammogram report from Mayo Clinic

```
MSH|^~\&|POWERSCRIBE|MAYO_RAD|DOCMGMT|MAYOCLINIC|20250214093800||MDM^T02|PS-MDM-MAYO-20250214-000891|P|2.4|||AL|NE
EVN|T02|20250214093800
PID|1||MRN-55098234^^^MAYO^MR||Dahlstrom^Sandra^Kay^^||19640722|F||W|5612 Silver Lake Rd NE^^Rochester^MN^55906^USA||^PRN^PH^^1^507^2894901|||||||603-81-4527
PV1|1|O|RAD^MAMMO^05||||4291038^Thorsgaard^Karen^S^^^MD|4291038^Thorsgaard^Karen^S^^^MD||RAD||||||||V|VN-20250214-0123^^^MAYO^VN|||||||||||||||||||||||||20250214080000
TXA|1|RAD|TX|20250214093800|4291038^Thorsgaard^Karen^S^^^MD||20250214093800||4291038^Thorsgaard^Karen^S^^^MD||||PS-RPT-MAYO-20250214-000891|MAYO_RAD||||AU||AV
OBX|1|TX|77067^SCREENING MAMMOGRAM BILATERAL^CPT4|1|SCREENING MAMMOGRAM BILATERAL~~CLINICAL INDICATION: Annual screening mammography. No palpable abnormality.~~TECHNIQUE: Standard CC and MLO views of both breasts were obtained using digital tomosynthesis.~~COMPARISON: Screening mammogram dated 2024-02-10.~~BREAST COMPOSITION: The breasts are heterogeneously dense (ACR density C).~~FINDINGS:~Right breast: No suspicious mass, architectural distortion, or suspicious calcifications.~Left breast: No suspicious mass, architectural distortion, or suspicious calcifications.~Axillary regions: No suspicious lymphadenopathy.~~IMPRESSION: Negative. No mammographic evidence of malignancy.~~BI-RADS: 1 - Negative.~~RECOMMENDATION: Routine annual screening mammography.||||||F
```

---

## 5. ORU^R01 - Lumbar spine X-ray report from Allina Health

```
MSH|^~\&|POWERSCRIBE|ALLINA_RAD|EHR|ALLINA|20250609151800||ORU^R01|PS-ALLI-20250609-007890|P|2.4|||AL|NE
PID|1||MRN-82034567^^^ALLINA^MR||Hegge^Richard^Allen^^||19550303|M||W|7234 Penn Ave S^^Richfield^MN^55423^USA||^PRN^PH^^1^612^8613478|||||||740-12-5839
PV1|1|O|RAD^XRAY^01||||5039182^Swanberg^Michelle^R^^^MD|5039182^Swanberg^Michelle^R^^^MD||RAD||||||||V|VN-20250609-0567^^^ALLINA^VN|||||||||||||||||||||||||20250609140000
ORC|RE|ORD-RAD-20250609-567^ALLINA|PS-RPT-20250609-007890^POWERSCRIBE||||1^^^20250609140000^^R||20250609151800|5039182^Swanberg^Michelle^R^^^MD|5039182^Swanberg^Michelle^R^^^MD|5039182^Swanberg^Michelle^R^^^MD||^WPN^PH^^1^651^2413000||||||ALLINA^Allina Health
OBR|1|ORD-RAD-20250609-567^ALLINA|PS-RPT-20250609-007890^POWERSCRIBE|72110^XR LUMBAR SPINE COMPLETE^CPT4|||20250609141500|||||||||||5039182^Swanberg^Michelle^R^^^MD||RAD-ACC-20250609-0567||||20250609151800|||F|||||||7104928^Haugen^David^A^^^MD^Radiology
OBX|1|TX|72110^XR LUMBAR SPINE COMPLETE^CPT4|1|XR LUMBAR SPINE COMPLETE (AP, LATERAL, SPOT LATERAL L5-S1)~~CLINICAL INDICATION: Low back pain, history of degenerative disc disease.~~COMPARISON: Lumbar spine X-ray dated 2023-08-22.~~FINDINGS:~Alignment: Normal lumbar lordosis. No spondylolisthesis.~Vertebral bodies: Mild anterior osteophyte formation at L3-L4 and L4-L5. No compression fracture.~Disc spaces: Moderate disc space narrowing at L4-L5 and L5-S1. Mild disc space narrowing at L3-L4.~Facet joints: Mild bilateral facet arthropathy at L4-L5 and L5-S1.~Sacroiliac joints: Normal.~Soft tissues: Unremarkable.~~IMPRESSION:~1. Multilevel degenerative changes, most pronounced at L4-L5 and L5-S1, stable compared to prior.~2. No acute fracture or malalignment.||||||F
```

---

## 6. ORU^R01 - CT pulmonary angiography report with embedded PDF from Fairview

```
MSH|^~\&|POWERSCRIBE|FAIRVIEW_RAD|EHR|FAIRVIEW|20250723042200||ORU^R01|PS-FV-20250723-009012|P|2.4|||AL|NE
PID|1||MRN-63012345^^^FAIRVIEW^MR||Abdi^Yusuf^Mohamed^^||19710918|M||B|2109 Cedar Ave^^Minneapolis^MN^55404^USA||^PRN^PH^^1^612^7297812|||||||813-50-2946
PV1|1|E|ED^ER^01||||6203841^Nygaard^Lars^P^^^MD|6203841^Nygaard^Lars^P^^^MD||RAD||||||||E|VN-20250723-0012^^^FAIRVIEW^VN|||||||||||||||||||||||||20250723030000
ORC|RE|ORD-RAD-20250723-012^FAIRVIEW|PS-RPT-20250723-009012^POWERSCRIBE||||1^^^20250723030000^^R||20250723042200|6203841^Nygaard^Lars^P^^^MD|6203841^Nygaard^Lars^P^^^MD|6203841^Nygaard^Lars^P^^^MD||^WPN^PH^^1^612^2734000||||||FAIRVIEW^Fairview Health Services
OBR|1|ORD-RAD-20250723-012^FAIRVIEW|PS-RPT-20250723-009012^POWERSCRIBE|71275^CT ANGIOGRAPHY CHEST^CPT4|||20250723031500|||||||||||6203841^Nygaard^Lars^P^^^MD||RAD-ACC-20250723-0012||||20250723042200|||F|||||||8391027^Kirscht^Ingrid^S^^^MD^Emergency Radiology
OBX|1|ED|71275^CT ANGIOGRAPHY CHEST^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKENUIFB1bG1vbmFyeSBBbmdpb2dyYXBoeSkKL0F1dGhvciAoRHIuIEluZ3JpZCBLcmFudHosIE1EKQovQ3JlYXRvciAoTnVhbmNlIFBvd2VyU2NyaWJlIDM2MCkKL1Byb2R1Y2VyIChOdWFuY2UgSGVhbHRoY2FyZSkKL0NyZWF0aW9uRGF0ZSAoRDoyMDI1MDcyMzA0MjIwMC0wNTAwKQo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMyAwIFIKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFs0IDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAzIDAgUgovQ29udGVudHMgNSAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNiAwIFIKPj4KPj4KPj4KZW5kb2JqCjUgMCBvYmoKPDwKL0xlbmd0aCAzNTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgozNiA3NTYgVGQKKENUIFB1bG1vbmFyeSBBbmdpb2dyYXBoeSkgVGoKCjM2IDczMCBUZAooQ1JJVElDQUwgRklORElORzogQmlsYXRlcmFsIHB1bG1vbmFyeSBlbWJvbGkuKSBUagoKMzYgNzEwIFRkCihTYWRkbGUgZW1ib2x1cyBhdCBtYWluIHB1bG1vbmFyeSBhcnRlcnkgYmlmdXJjYXRpb24uKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjYgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNwowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDI1MCAwMDAwMCBuIAowMDAwMDAwMjk5IDAwMDAwIG4gCjAwMDAwMDA0MDIgMDAwMDAgbiAKMDAwMDAwMDU1MiAwMDAwMCBuIAowMDAwMDAwOTUyIDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNwovUm9vdCAyIDAgUgo+PgpzdGFydHhyZWYKMTA0MgolJUVPRgo=||||||F
OBX|2|TX|71275^CT ANGIOGRAPHY CHEST^CPT4|2|CT PULMONARY ANGIOGRAPHY~~CLINICAL INDICATION: Acute onset dyspnea and pleuritic chest pain. Elevated D-dimer.~~TECHNIQUE: Helical CT angiography of the chest following IV administration of 80 mL Omnipaque 350 with bolus tracking.~~COMPARISON: None.~~FINDINGS:~Pulmonary arteries: Saddle embolus at the main pulmonary artery bifurcation extending into bilateral main, lobar, and segmental pulmonary arteries. Right ventricle is dilated with RV/LV ratio of 1.3, suggesting right heart strain.~Lungs: Small bilateral pleural effusions. Wedge-shaped peripheral opacity in the right lower lobe consistent with pulmonary infarct.~Heart: No pericardial effusion.~Mediastinum: Normal.~~IMPRESSION:~1. CRITICAL: Extensive bilateral pulmonary emboli with saddle embolus. Right ventricular strain.~2. Right lower lobe pulmonary infarct.~3. Small bilateral pleural effusions.||||||F
```

---

## 7. MDM^T02 - Addendum to ultrasound report from Mayo Clinic

```
MSH|^~\&|POWERSCRIBE|MAYO_RAD|DOCMGMT|MAYOCLINIC|20250403112000||MDM^T02|PS-MDM-MAYO-20250403-001567|P|2.4|||AL|NE
EVN|T02|20250403112000
PID|1||MRN-33098765^^^MAYO^MR||Lor^Kalia^Neng^^||19830415|F||A|2834 Salem Ave SW^^Rochester^MN^55902^USA||^PRN^PH^^1^507^2896034|||||||920-31-5847
PV1|1|O|RAD^US^04||||7081539^Harstad^David^A^^^MD|7081539^Harstad^David^A^^^MD||RAD||||||||V|VN-20250403-0234^^^MAYO^VN|||||||||||||||||||||||||20250403090000
TXA|1|RAD|TX|20250403112000|7081539^Harstad^David^A^^^MD||20250403112000||7081539^Harstad^David^A^^^MD||||PS-RPT-MAYO-20250403-001567|MAYO_RAD||||AU||AV
OBX|1|TX|76770^US ABDOMEN COMPLETE^CPT4|1|ADDENDUM TO ULTRASOUND ABDOMEN COMPLETE~~Original report dated 2025-04-02.~~After review with the clinical team, the 12mm echogenic focus in the right kidney upper pole is favored to represent a small angiomyolipoma based on its echogenicity pattern. A renal MRI is recommended for further characterization if clinically warranted.~~Addendum dictated by: Dr. David A. Harstad, MD||||||F
```

---

## 8. ORU^R01 - Knee MRI report from Allina Health

```
MSH|^~\&|POWERSCRIBE|ALLINA_RAD|EHR|ALLINA|20250815134500||ORU^R01|PS-ALLI-20250815-011234|P|2.4|||AL|NE
PID|1||MRN-51023456^^^ALLINA^MR||Jama^Ismail^Abdi^^||19890127|M||B|3412 Nicollet Ave S^^Minneapolis^MN^55408^USA||^PRN^PH^^1^612^7299456|||||||951-24-8037
PV1|1|O|RAD^MRI^02||||8391027^Kirscht^Ingrid^S^^^MD|8391027^Kirscht^Ingrid^S^^^MD||RAD||||||||V|VN-20250815-0789^^^ALLINA^VN|||||||||||||||||||||||||20250815120000
ORC|RE|ORD-RAD-20250815-789^ALLINA|PS-RPT-20250815-011234^POWERSCRIBE||||1^^^20250815120000^^R||20250815134500|8391027^Kirscht^Ingrid^S^^^MD|8391027^Kirscht^Ingrid^S^^^MD|8391027^Kirscht^Ingrid^S^^^MD||^WPN^PH^^1^651^2413000||||||ALLINA^Allina Health
OBR|1|ORD-RAD-20250815-789^ALLINA|PS-RPT-20250815-011234^POWERSCRIBE|73721^MRI KNEE WO CONTRAST LEFT^CPT4|||20250815121500|||||||||||8391027^Kirscht^Ingrid^S^^^MD||RAD-ACC-20250815-0789||||20250815134500|||F|||||||9028471^Ellingson^Robert^T^^^MD^Musculoskeletal Radiology
OBX|1|TX|73721^MRI KNEE WO CONTRAST LEFT^CPT4|1|MRI LEFT KNEE WITHOUT CONTRAST~~CLINICAL INDICATION: Left knee pain and swelling after running injury. Rule out meniscal tear.~~TECHNIQUE: Multiplanar, multisequence MRI of the left knee without IV contrast.~~COMPARISON: None.~~FINDINGS:~Menisci: Complex tear of the posterior horn of the medial meniscus extending to the inferior articular surface. Lateral meniscus is intact.~Cruciate ligaments: ACL and PCL are intact.~Collateral ligaments: MCL and LCL are intact.~Extensor mechanism: Quadriceps and patellar tendons are normal. Normal patellar tracking.~Articular cartilage: Mild chondromalacia of the medial femoral condyle, grade II.~Joint effusion: Small joint effusion.~Bone marrow: Mild bone marrow edema at the medial tibial plateau.~~IMPRESSION:~1. Complex tear of the posterior horn medial meniscus.~2. Mild grade II chondromalacia of the medial femoral condyle.~3. Small joint effusion and mild bone marrow edema at the medial tibial plateau.||||||F
```

---

## 9. ORU^R01 - Abdominal ultrasound report from Fairview

```
MSH|^~\&|POWERSCRIBE|FAIRVIEW_RAD|EHR|FAIRVIEW|20250910102400||ORU^R01|PS-FV-20250910-013456|P|2.4|||AL|NE
PID|1||MRN-84012345^^^FAIRVIEW^MR||Bjornson^Dorothy^Marie^^||19480630|F||W|1025 4th St SE^^Minneapolis^MN^55414^USA||^PRN^PH^^1^612^3793901|||||||064-28-5913
PV1|1|O|RAD^US^04||||9028471^Ellingson^Robert^T^^^MD|9028471^Ellingson^Robert^T^^^MD||RAD||||||||V|VN-20250910-0456^^^FAIRVIEW^VN|||||||||||||||||||||||||20250910090000
ORC|RE|ORD-RAD-20250910-456^FAIRVIEW|PS-RPT-20250910-013456^POWERSCRIBE||||1^^^20250910090000^^R||20250910102400|9028471^Ellingson^Robert^T^^^MD|9028471^Ellingson^Robert^T^^^MD|9028471^Ellingson^Robert^T^^^MD||^WPN^PH^^1^612^2734000||||||FAIRVIEW^Fairview Health Services
OBR|1|ORD-RAD-20250910-456^FAIRVIEW|PS-RPT-20250910-013456^POWERSCRIBE|76700^US ABDOMEN COMPLETE^CPT4|||20250910091500|||||||||||9028471^Ellingson^Robert^T^^^MD||RAD-ACC-20250910-0456||||20250910102400|||F|||||||1472930^Storlie^Patricia^E^^^MD^Radiology
OBX|1|TX|76700^US ABDOMEN COMPLETE^CPT4|1|ULTRASOUND ABDOMEN COMPLETE~~CLINICAL INDICATION: Elevated liver enzymes, right upper quadrant discomfort.~~TECHNIQUE: Real-time grayscale and color Doppler sonography of the abdomen.~~COMPARISON: CT abdomen dated 2024-12-03.~~FINDINGS:~Liver: Diffusely increased echogenicity consistent with hepatic steatosis. No focal hepatic mass. Liver measures 17.2 cm in craniocaudal dimension.~Gallbladder: Multiple small gallstones, largest measuring 8mm. No gallbladder wall thickening or pericholecystic fluid. Common bile duct measures 4mm.~Pancreas: Partially obscured by bowel gas. Visualized portions appear normal.~Right kidney: 11.3 cm. No hydronephrosis or calculi.~Left kidney: 10.8 cm. No hydronephrosis or calculi.~Spleen: Normal, measuring 10.5 cm.~Aorta: Normal caliber.~~IMPRESSION:~1. Hepatic steatosis with mild hepatomegaly.~2. Cholelithiasis without cholecystitis.||||||F
```

---

## 10. ORU^R01 - Chest CT for lung nodule follow-up with embedded PDF from Mayo Clinic

```
MSH|^~\&|POWERSCRIBE|MAYO_RAD|EHR|MAYOCLINIC|20250130161500||ORU^R01|PS-MAYO-20250130-002345|P|2.4|||AL|NE
PID|1||MRN-22098456^^^MAYO^MR||Braun^William^Robert^^||19520810|M||W|4520 Cascade Rd SE^^Rochester^MN^55904^USA||^PRN^PH^^1^507^2897890|||||||157-43-9280
PV1|1|O|RAD^CT^03||||1938274^Stavros^Eric^W^^^MD|1938274^Stavros^Eric^W^^^MD||RAD||||||||V|VN-20250130-0890^^^MAYO^VN|||||||||||||||||||||||||20250130140000
ORC|RE|ORD-RAD-20250130-890^MAYO|PS-RPT-20250130-002345^POWERSCRIBE||||1^^^20250130140000^^R||20250130161500|1938274^Stavros^Eric^W^^^MD|1938274^Stavros^Eric^W^^^MD|1938274^Stavros^Eric^W^^^MD||^WPN^PH^^1^507^2845000||||||MAYO^Mayo Clinic
OBR|1|ORD-RAD-20250130-890^MAYO|PS-RPT-20250130-002345^POWERSCRIBE|71250^CT CHEST WO CONTRAST^CPT4|||20250130141500|||||||||||1938274^Stavros^Eric^W^^^MD||RAD-ACC-20250130-0890||||20250130161500|||F|||||||4029183^Engstrom^Anna^M^^^MD^Thoracic Radiology
OBX|1|ED|71250^CT CHEST WO CONTRAST^CPT4|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKENUIENoZXN0IFdpdGhvdXQgQ29udHJhc3QgLSBMdW5nIE5vZHVsZSBGb2xsb3ctVXApCi9BdXRob3IgKERyLiBBbm5hIExpbmRiZXJnLCBNRCkKL0NyZWF0b3IgKE51YW5jZSBQb3dlclNjcmliZSAzNjApCi9Qcm9kdWNlciAoTnVhbmNlIEhlYWx0aGNhcmUpCi9DcmVhdGlvbkRhdGUgKEQ6MjAyNTAxMzAxNjE1MDAtMDYwMCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbNCAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCj4+CmVuZG9iago0IDAgb2JqCjw8Ci9UeXBlIC9QYWdlCi9QYXJlbnQgMyAwIFIKL0NvbnRlbnRzIDUgMCBSCi9SZXNvdXJjZXMgPDwKL0ZvbnQgPDwKL0YxIDYgMCBSCj4+Cj4+Cj4+CmVuZG9iago1IDAgb2JqCjw8Ci9MZW5ndGggMzgwCj4+CnN0cmVhbQpCVAovRjEgMTIgVGYKMzYgNzU2IFRkCihDVCBDaGVzdCBXaXRob3V0IENvbnRyYXN0IC0gTHVuZyBOb2R1bGUgRm9sbG93LVVwKSBUagoKMzYgNzMwIFRkCihMdW5nLVJBRFMgQ2F0ZWdvcnkgMzogU3VzcGljaW91cyA2bW0gcmlnaHQgdXBwZXIgbG9iZSBub2R1bGUuKSBUagoKMzYgNzEwIFRkCihSZWNvbW1lbmRhdGlvbjogUEVUL0NUIGluIDMgbW9udGhzLikgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago2IDAgb2JqCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDcKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAyODUgMDAwMDAgbiAKMDAwMDAwMDMzNCAwMDAwMCBuIAowMDAwMDAwNDM3IDAwMDAwIG4gCjAwMDAwMDA1ODcgMDAwMDAgbiAKMDAwMDAwMTAxNyAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDcKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjExMDcKJSVFT0YK||||||F
OBX|2|TX|71250^CT CHEST WO CONTRAST^CPT4|2|CT CHEST WITHOUT CONTRAST - LUNG NODULE FOLLOW-UP~~CLINICAL INDICATION: 6-month follow-up of right upper lobe lung nodule identified on screening LDCT. 40 pack-year smoking history.~~TECHNIQUE: Low-dose helical CT of the chest without IV contrast.~~COMPARISON: CT chest dated 2024-07-28.~~FINDINGS:~Right upper lobe: Spiculated solid nodule measuring 9mm (previously 6mm), interval growth over 6 months.~Right middle lobe: Stable 3mm ground-glass nodule, unchanged.~Left lung: Clear. No nodules.~Mediastinum: No lymphadenopathy.~Pleura: No effusion.~Osseous structures: Mild degenerative changes of the thoracic spine.~~Lung-RADS Category: 4B - Suspicious. Growing solid nodule.~~IMPRESSION:~1. Interval growth of right upper lobe spiculated solid nodule from 6mm to 9mm. Lung-RADS 4B.~2. RECOMMENDATION: PET/CT within 3 months. Consider tissue sampling.~3. Stable 3mm right middle lobe ground-glass nodule.||||||F
```

---

## 11. MDM^T02 - Preliminary notification for echocardiogram report from Fairview

```
MSH|^~\&|POWERSCRIBE|FAIRVIEW_RAD|DOCMGMT|FAIRVIEW|20250304183000||MDM^T02|PS-MDM-FV-20250304-002789|P|2.4|||AL|NE
EVN|T02|20250304183000
PID|1||MRN-71023456^^^FAIRVIEW^MR||Schultz^Harold^William^^||19430825|M||W|3814 Dupont Ave S^^Minneapolis^MN^55409^USA||^PRN^PH^^1^612^3792345|||||||284-59-7013
PV1|1|I|CARD^ICU^12||||2049371^Solberg^Christine^E^^^MD|2049371^Solberg^Christine^E^^^MD||CARD||||||||I|VN-20250304-0156^^^FAIRVIEW^VN|||||||||||||||||||||||||20250303200000
TXA|1|RAD|TX|20250304183000|2049371^Solberg^Christine^E^^^MD||20250304183000||2049371^Solberg^Christine^E^^^MD||||PS-RPT-FV-20250304-002789|FAIRVIEW_RAD||||PA||AV
OBX|1|TX|93306^ECHOCARDIOGRAM COMPLETE^CPT4|1|TRANSTHORACIC ECHOCARDIOGRAM - PRELIMINARY~~CLINICAL INDICATION: Chest pain, elevated troponin, rule out wall motion abnormality.~~FINDINGS:~Left ventricle: Mildly dilated. Estimated ejection fraction 35-40%. Hypokinesis of the inferior and inferolateral walls suggesting ischemic etiology.~Right ventricle: Normal size and function.~Left atrium: Mildly dilated.~Right atrium: Normal.~Aortic valve: Trileaflet with mild sclerosis. No stenosis. Trace regurgitation.~Mitral valve: Mild mitral regurgitation.~Tricuspid valve: Trace regurgitation. Estimated RVSP 32 mmHg.~Pericardium: No effusion.~~PRELIMINARY IMPRESSION:~1. Reduced left ventricular systolic function with EF 35-40%.~2. Regional wall motion abnormality involving inferior and inferolateral walls, concerning for ischemic cardiomyopathy.~3. Mild mitral regurgitation.~~Final read pending attending review.||||||P
```

---

## 12. ORU^R01 - Head CT without contrast from Mayo Clinic emergency

```
MSH|^~\&|POWERSCRIBE|MAYO_RAD|EHR|MAYOCLINIC|20250905021500||ORU^R01|PS-MAYO-20250905-014567|P|2.4|||AL|NE
PID|1||MRN-99087654^^^MAYO^MR||Ronning^Eugene^Walter^^||19490203|M||W|1523 Center St^^Rochester^MN^55904^USA||^PRN^PH^^1^507^2894567|||||||418-67-2930
PV1|1|E|ED^ER^02||||3571082^Storlie^Patricia^E^^^MD|3571082^Storlie^Patricia^E^^^MD||NEUR||||||||E|VN-20250905-0001^^^MAYO^VN|||||||||||||||||||||||||20250905010000
ORC|RE|ORD-RAD-20250905-001^MAYO|PS-RPT-20250905-014567^POWERSCRIBE||||1^^^20250905010000^^R||20250905021500|3571082^Storlie^Patricia^E^^^MD|3571082^Storlie^Patricia^E^^^MD|3571082^Storlie^Patricia^E^^^MD||^WPN^PH^^1^507^2845000||||||MAYO^Mayo Clinic
OBR|1|ORD-RAD-20250905-001^MAYO|PS-RPT-20250905-014567^POWERSCRIBE|70450^CT HEAD WO CONTRAST^CPT4|||20250905011000|||||||||||3571082^Storlie^Patricia^E^^^MD||RAD-ACC-20250905-0001||||20250905021500|||F|||||||5820194^Engstrom^Anna^M^^^MD^Neuroradiology
OBX|1|TX|70450^CT HEAD WO CONTRAST^CPT4|1|CT HEAD WITHOUT CONTRAST~~CLINICAL INDICATION: Sudden onset right-sided weakness and speech difficulty. Stroke alert.~~TECHNIQUE: Non-contrast helical CT of the head.~~COMPARISON: None available.~~FINDINGS:~Brain parenchyma: Hyperdense left middle cerebral artery sign suggesting acute thrombus. Loss of gray-white matter differentiation in the left insular cortex and left frontal operculum. ASPECTS score: 8.~Ventricles: Symmetric and normal in size.~Midline: No midline shift.~Extra-axial spaces: No acute extra-axial hemorrhage.~Calvarium: No fracture.~~IMPRESSION:~1. CRITICAL: Findings concerning for acute left MCA territory ischemic stroke with hyperdense MCA sign and early ischemic changes. ASPECTS 8.~2. No intracranial hemorrhage.~3. Stroke team notified at 01:15 AM.||||||F
```

---

## 13. ORU^R01 - Mammogram diagnostic bilateral from Allina Health

```
MSH|^~\&|POWERSCRIBE|ALLINA_RAD|EHR|ALLINA|20251020111500||ORU^R01|PS-ALLI-20251020-016789|P|2.4|||AL|NE
PID|1||MRN-41023456^^^ALLINA^MR||Thao^Mai^See^^||19700412|F||A|8912 Xerxes Ave S^^Bloomington^MN^55431^USA||^PRN^PH^^1^952^8917823|||||||509-72-4138
PV1|1|O|RAD^MAMMO^05||||4291038^Thorsgaard^Karen^S^^^MD|4291038^Thorsgaard^Karen^S^^^MD||RAD||||||||V|VN-20251020-0345^^^ALLINA^VN|||||||||||||||||||||||||20251020090000
ORC|RE|ORD-RAD-20251020-345^ALLINA|PS-RPT-20251020-016789^POWERSCRIBE||||1^^^20251020090000^^R||20251020111500|4291038^Thorsgaard^Karen^S^^^MD|4291038^Thorsgaard^Karen^S^^^MD|4291038^Thorsgaard^Karen^S^^^MD||^WPN^PH^^1^651^2413000||||||ALLINA^Allina Health
OBR|1|ORD-RAD-20251020-345^ALLINA|PS-RPT-20251020-016789^POWERSCRIBE|77066^DIAGNOSTIC MAMMOGRAM BILATERAL^CPT4|||20251020093000|||||||||||4291038^Thorsgaard^Karen^S^^^MD||RAD-ACC-20251020-0345||||20251020111500|||F|||||||6150293^Tveit^Jennifer^A^^^MD^Breast Imaging
OBX|1|TX|77066^DIAGNOSTIC MAMMOGRAM BILATERAL^CPT4|1|DIAGNOSTIC MAMMOGRAM BILATERAL WITH TOMOSYNTHESIS~~CLINICAL INDICATION: Palpable left breast mass at 10 o'clock position.~~TECHNIQUE: Bilateral CC and MLO views with digital tomosynthesis. Additional spot compression views of the left breast.~~COMPARISON: Screening mammogram dated 2024-10-15.~~BREAST COMPOSITION: Scattered areas of fibroglandular density (ACR density B).~~FINDINGS:~Right breast: No suspicious mass, distortion, or calcifications. Benign-appearing calcifications in the upper outer quadrant.~Left breast: Irregular hyper dense mass measuring 15mm at the 10 o'clock position, 6 cm from the nipple, corresponding to the palpable area of concern. New since prior study.~Axillary regions: No suspicious lymphadenopathy.~~IMPRESSION:~Left breast: Suspicious irregular mass at 10 o'clock. New finding.~~BI-RADS: 4C - High suspicion for malignancy.~~RECOMMENDATION: Ultrasound-guided core needle biopsy recommended. Patient and referring provider notified.||||||F
```

---

## 14. ORU^R01 - Cervical spine MRI from Fairview

```
MSH|^~\&|POWERSCRIBE|FAIRVIEW_RAD|EHR|FAIRVIEW|20250618143000||ORU^R01|PS-FV-20250618-018901|P|2.4|||AL|NE
PID|1||MRN-52098765^^^FAIRVIEW^MR||Omar^Farah^Daud^^||19750620|M||B|2917 38th Ave S^^Minneapolis^MN^55406^USA||^PRN^PH^^1^612^7291034|||||||621-83-4059
PV1|1|O|RAD^MRI^02||||5820194^Engstrom^Anna^M^^^MD|5820194^Engstrom^Anna^M^^^MD||RAD||||||||V|VN-20250618-0678^^^FAIRVIEW^VN|||||||||||||||||||||||||20250618120000
ORC|RE|ORD-RAD-20250618-678^FAIRVIEW|PS-RPT-20250618-018901^POWERSCRIBE||||1^^^20250618120000^^R||20250618143000|5820194^Engstrom^Anna^M^^^MD|5820194^Engstrom^Anna^M^^^MD|5820194^Engstrom^Anna^M^^^MD||^WPN^PH^^1^612^2734000||||||FAIRVIEW^Fairview Health Services
OBR|1|ORD-RAD-20250618-678^FAIRVIEW|PS-RPT-20250618-018901^POWERSCRIBE|72141^MRI CERVICAL SPINE WO CONTRAST^CPT4|||20250618123000|||||||||||5820194^Engstrom^Anna^M^^^MD||RAD-ACC-20250618-0678||||20250618143000|||F|||||||6203841^Nygaard^Lars^P^^^MD^Neuroradiology
OBX|1|TX|72141^MRI CERVICAL SPINE WO CONTRAST^CPT4|1|MRI CERVICAL SPINE WITHOUT CONTRAST~~CLINICAL INDICATION: Neck pain with bilateral upper extremity radiculopathy.~~TECHNIQUE: Multiplanar, multisequence MRI of the cervical spine without IV contrast.~~COMPARISON: MRI cervical spine dated 2024-03-14.~~FINDINGS:~C3-C4: Mild disc bulge. No significant stenosis.~C4-C5: Moderate disc bulge with uncovertebral joint hypertrophy causing moderate bilateral neural foraminal stenosis. Mild central stenosis.~C5-C6: Broad-based disc herniation with superimposed left paracentral protrusion. Moderate central canal stenosis with flattening of the ventral cord. Severe left neural foraminal stenosis, moderate right neural foraminal stenosis.~C6-C7: Mild disc bulge with mild bilateral foraminal stenosis.~C7-T1: Normal.~Spinal cord: No cord signal abnormality. No syrinx.~~IMPRESSION:~1. C5-C6 disc herniation with moderate central stenosis and severe left neural foraminal stenosis, progressed since prior study.~2. C4-C5 moderate bilateral neural foraminal stenosis, stable.~3. Multilevel degenerative changes as described.~4. Recommend neurosurgical consultation.||||||F
```

---

## 15. MDM^T02 - Final pathology report notification from Mayo Clinic

```
MSH|^~\&|POWERSCRIBE|MAYO_PATH|DOCMGMT|MAYOCLINIC|20251112094500||MDM^T02|PS-MDM-MAYO-20251112-003456|P|2.4|||AL|NE
EVN|T02|20251112094500
PID|1||MRN-66098234^^^MAYO^MR||Krause^Susan^Marie^^||19650930|F||W|7412 37th Ave NW^^Rochester^MN^55901^USA||^PRN^PH^^1^507^2893890|||||||730-41-5892
PV1|1|I|SURG^4N^12||||8104293^Reinhardt^Thomas^E^^^MD|8104293^Reinhardt^Thomas^E^^^MD||SURG||||||||I|VN-20251110-0345^^^MAYO^VN|||||||||||||||||||||||||20251110060000
TXA|1|PATH|TX|20251112094500|8104293^Reinhardt^Thomas^E^^^MD||20251112094500||9271054^Tveit^Eric^M^^^MD^Pathology||||PS-RPT-MAYO-20251112-003456|MAYO_PATH||||AU||AV
OBX|1|TX|88305^SURGICAL PATHOLOGY^CPT4|1|SURGICAL PATHOLOGY REPORT~~SPECIMEN: Left breast, partial mastectomy.~~CLINICAL HISTORY: Left breast mass, BI-RADS 4C, core biopsy showing invasive ductal carcinoma.~~GROSS DESCRIPTION: Partial mastectomy specimen measuring 8.5 x 6.2 x 3.8 cm, oriented with short suture superior and long suture lateral. A firm, stellate mass measuring 1.8 x 1.5 x 1.3 cm is identified in the central portion.~~MICROSCOPIC DESCRIPTION: Sections show invasive ductal carcinoma, Nottingham grade 2 (tubule score 3, nuclear grade 2, mitotic score 1). Tumor measures 1.8 cm in greatest dimension. No lymphovascular invasion identified. All surgical margins are negative, closest margin 5mm (anterior).~~DIAGNOSIS: Left breast, partial mastectomy: Invasive ductal carcinoma, Nottingham grade 2, measuring 1.8 cm. Margins negative. No lymphovascular invasion.||||||F
```

---

## 16. ORU^R01 - Bone density scan report from Allina Health

```
MSH|^~\&|POWERSCRIBE|ALLINA_RAD|EHR|ALLINA|20250224141200||ORU^R01|PS-ALLI-20250224-020123|P|2.4|||AL|NE
PID|1||MRN-30098765^^^ALLINA^MR||Engstrom^Beverly^Jean^^||19530815|F||W|5234 York Ave S^^Edina^MN^55410^USA||^PRN^PH^^1^952^8916789|||||||842-10-3567
PV1|1|O|RAD^DEXA^06||||9271054^Tveit^Eric^M^^^MD|9271054^Tveit^Eric^M^^^MD||RAD||||||||V|VN-20250224-0567^^^ALLINA^VN|||||||||||||||||||||||||20250224130000
ORC|RE|ORD-RAD-20250224-567^ALLINA|PS-RPT-20250224-020123^POWERSCRIBE||||1^^^20250224130000^^R||20250224141200|9271054^Tveit^Eric^M^^^MD|9271054^Tveit^Eric^M^^^MD|9271054^Tveit^Eric^M^^^MD||^WPN^PH^^1^651^2413000||||||ALLINA^Allina Health
OBR|1|ORD-RAD-20250224-567^ALLINA|PS-RPT-20250224-020123^POWERSCRIBE|77080^DEXA BONE DENSITY AXIAL^CPT4|||20250224131500|||||||||||9271054^Tveit^Eric^M^^^MD||RAD-ACC-20250224-0567||||20250224141200|||F|||||||1302947^Haugen^David^A^^^MD^Radiology
OBX|1|TX|77080^DEXA BONE DENSITY AXIAL^CPT4|1|DEXA BONE DENSITY - LUMBAR SPINE AND HIP~~CLINICAL INDICATION: 71-year-old female, postmenopausal, family history of osteoporosis.~~TECHNIQUE: Dual-energy X-ray absorptiometry of the lumbar spine (L1-L4) and bilateral proximal femurs.~~COMPARISON: DEXA dated 2023-02-20.~~FINDINGS:~Lumbar spine (L1-L4): BMD 0.812 g/cm2, T-score -2.6. Previous T-score -2.4.~Left femoral neck: BMD 0.654 g/cm2, T-score -2.3. Previous T-score -2.2.~Right femoral neck: BMD 0.668 g/cm2, T-score -2.2. Previous T-score -2.1.~Left total hip: BMD 0.745 g/cm2, T-score -2.0.~Right total hip: BMD 0.758 g/cm2, T-score -1.9.~~IMPRESSION:~1. Osteoporosis of the lumbar spine (T-score -2.6) and bilateral femoral necks (T-score -2.3 left, -2.2 right).~2. Interval decrease in bone density compared to 2023, most notable at the lumbar spine.~3. FRAX 10-year major osteoporotic fracture risk: 24%. Hip fracture risk: 5.8%.~4. Recommend discussion with primary care regarding treatment options.||||||F
```

---

## 17. ORU^R01 - Shoulder X-ray report from Fairview

```
MSH|^~\&|POWERSCRIBE|FAIRVIEW_RAD|EHR|FAIRVIEW|20250411155600||ORU^R01|PS-FV-20250411-022345|P|2.4|||AL|NE
PID|1||MRN-62098765^^^FAIRVIEW^MR||Her^Chue^Tong^^||19810930|M||A|4523 Bloomington Ave^^Minneapolis^MN^55407^USA||^PRN^PH^^1^612^7298901|||||||935-20-4817
PV1|1|O|RAD^XRAY^01||||1472930^Storlie^Patricia^E^^^MD|1472930^Storlie^Patricia^E^^^MD||RAD||||||||V|VN-20250411-0890^^^FAIRVIEW^VN|||||||||||||||||||||||||20250411150000
ORC|RE|ORD-RAD-20250411-890^FAIRVIEW|PS-RPT-20250411-022345^POWERSCRIBE||||1^^^20250411150000^^R||20250411155600|1472930^Storlie^Patricia^E^^^MD|1472930^Storlie^Patricia^E^^^MD|1472930^Storlie^Patricia^E^^^MD||^WPN^PH^^1^612^2734000||||||FAIRVIEW^Fairview Health Services
OBR|1|ORD-RAD-20250411-890^FAIRVIEW|PS-RPT-20250411-022345^POWERSCRIBE|73030^XR SHOULDER COMPLETE LEFT^CPT4|||20250411151000|||||||||||1472930^Storlie^Patricia^E^^^MD||RAD-ACC-20250411-0890||||20250411155600|||F|||||||2049371^Solberg^Christine^E^^^MD^Radiology
OBX|1|TX|73030^XR SHOULDER COMPLETE LEFT^CPT4|1|XR LEFT SHOULDER COMPLETE (AP INTERNAL ROTATION, AP EXTERNAL ROTATION, AXILLARY, SCAPULAR Y)~~CLINICAL INDICATION: Left shoulder pain after fall. Rule out fracture.~~COMPARISON: None.~~FINDINGS:~Bones: Nondisplaced fracture of the greater tuberosity of the left proximal humerus. The humeral head is well seated in the glenoid fossa. No glenohumeral dislocation.~Joint spaces: Moderate narrowing of the acromioclavicular joint with inferior osteophyte formation. Glenohumeral joint space is preserved.~Soft tissues: Mild soft tissue swelling overlying the left shoulder.~~IMPRESSION:~1. Nondisplaced fracture of the left humeral greater tuberosity.~2. Moderate acromioclavicular joint degenerative changes.~3. Orthopedic follow-up recommended.||||||F
```

---

## 18. ORU^R01 - Renal ultrasound with Doppler from Mayo Clinic

```
MSH|^~\&|POWERSCRIBE|MAYO_RAD|EHR|MAYOCLINIC|20250709102800||ORU^R01|PS-MAYO-20250709-024567|P|2.4|||AL|NE
PID|1||MRN-77098234^^^MAYO^MR||Mohamed^Fatima^Asha^^||19860312|F||B|1923 Riverside Ave^^Minneapolis^MN^55454^USA||^PRN^PH^^1^612^3794123|||||||957-20-3481
PV1|1|O|RAD^US^04||||2049371^Solberg^Christine^E^^^MD|2049371^Solberg^Christine^E^^^MD||RAD||||||||V|VN-20250709-0123^^^MAYO^VN|||||||||||||||||||||||||20250709090000
ORC|RE|ORD-RAD-20250709-123^MAYO|PS-RPT-20250709-024567^POWERSCRIBE||||1^^^20250709090000^^R||20250709102800|2049371^Solberg^Christine^E^^^MD|2049371^Solberg^Christine^E^^^MD|2049371^Solberg^Christine^E^^^MD||^WPN^PH^^1^507^2845000||||||MAYO^Mayo Clinic
OBR|1|ORD-RAD-20250709-123^MAYO|PS-RPT-20250709-024567^POWERSCRIBE|76775^US RETROPERITONEAL LIMITED^CPT4|||20250709091500|||||||||||2049371^Solberg^Christine^E^^^MD||RAD-ACC-20250709-0123||||20250709102800|||F|||||||3195028^Overby^Anna^K^^^MD^Radiology
OBX|1|TX|76775^US RETROPERITONEAL LIMITED^CPT4|1|RENAL ULTRASOUND WITH DOPPLER~~CLINICAL INDICATION: Elevated creatinine (2.1 mg/dL). Evaluate for obstructive uropathy.~~TECHNIQUE: Real-time grayscale and color Doppler sonography of both kidneys.~~COMPARISON: Renal ultrasound dated 2024-11-20.~~FINDINGS:~Right kidney: Measures 10.2 cm (previously 10.5 cm). Normal cortical echogenicity and thickness. No hydronephrosis. No calculi or mass. Renal artery RI 0.72.~Left kidney: Measures 10.0 cm (previously 10.3 cm). Normal cortical echogenicity and thickness. No hydronephrosis. No calculi or mass. Renal artery RI 0.70.~Bladder: Normal wall thickness. No calculi. Post-void residual not assessed.~~IMPRESSION:~1. Normal renal ultrasound bilaterally. No hydronephrosis or obstructive uropathy.~2. Renal resistive indices within normal limits.~3. Slight interval decrease in renal size bilaterally, may correlate with chronic kidney disease.||||||F
```

---

## 19. MDM^T02 - Critical result notification for CT angiography from Allina Health

```
MSH|^~\&|POWERSCRIBE|ALLINA_RAD|DOCMGMT|ALLINA|20250828234500||MDM^T02|PS-MDM-ALLI-20250828-004567|P|2.4|||AL|NE
EVN|T02|20250828234500
PID|1||MRN-19098765^^^ALLINA^MR||Hirsi^Amina^Halima^^||19730615|F||B|2812 E Lake St^^Minneapolis^MN^55406^USA||^PRN^PH^^1^612^7297234|||||||071-34-8529
PV1|1|E|ED^ER^03||||3195028^Overby^Anna^K^^^MD|3195028^Overby^Anna^K^^^MD||EMER||||||||E|VN-20250828-0901^^^ALLINA^VN|||||||||||||||||||||||||20250828220000
TXA|1|RAD|TX|20250828234500|3195028^Overby^Anna^K^^^MD||20250828234500||4291038^Thorsgaard^Karen^S^^^MD||||PS-RPT-ALLI-20250828-004567|ALLINA_RAD||||AU||AV
OBX|1|TX|74174^CT ANGIOGRAPHY ABD AND PELVIS^CPT4|1|CT ANGIOGRAPHY ABDOMEN AND PELVIS - CRITICAL RESULT~~CLINICAL INDICATION: Acute onset severe abdominal pain. Concern for mesenteric ischemia.~~CRITICAL FINDING COMMUNICATION: Dr. Overby notified at 23:30 on 2025-08-28 regarding superior mesenteric artery occlusion.~~FINDINGS:~Aorta: Normal caliber. Moderate atherosclerotic calcification.~Superior mesenteric artery: Complete occlusion approximately 3 cm from the origin. Reconstitution via collaterals distally.~Inferior mesenteric artery: Patent.~Celiac trunk: Patent with mild ostial stenosis.~Small bowel: Diffuse wall thickening and decreased enhancement of jejunal and proximal ileal loops concerning for bowel ischemia. No pneumatosis.~Large bowel: Normal.~Mesenteric veins: Patent.~~IMPRESSION:~1. CRITICAL: Superior mesenteric artery occlusion with findings concerning for acute mesenteric ischemia involving the jejunum and proximal ileum.~2. No pneumatosis or portal venous gas at this time.~3. Surgical consultation recommended urgently.||||||F
```

---

## 20. ORU^R01 - Pelvis X-ray from Mayo Clinic emergency

```
MSH|^~\&|POWERSCRIBE|MAYO_RAD|EHR|MAYOCLINIC|20251201054500||ORU^R01|PS-MAYO-20251201-026789|P|2.4|||AL|NE
PID|1||MRN-88098456^^^MAYO^MR||Pfeiffer^Gerald^Thomas^^||19460510|M||W|2917 16th Ave NW^^Rochester^MN^55901^USA||^PRN^PH^^1^507^2892134|||||||163-45-7281
PV1|1|E|ED^ER^01||||4291038^Thorsgaard^Karen^S^^^MD|4291038^Thorsgaard^Karen^S^^^MD||ORTH||||||||E|VN-20251201-0002^^^MAYO^VN|||||||||||||||||||||||||20251201040000
ORC|RE|ORD-RAD-20251201-002^MAYO|PS-RPT-20251201-026789^POWERSCRIBE||||1^^^20251201040000^^R||20251201054500|4291038^Thorsgaard^Karen^S^^^MD|4291038^Thorsgaard^Karen^S^^^MD|4291038^Thorsgaard^Karen^S^^^MD||^WPN^PH^^1^507^2845000||||||MAYO^Mayo Clinic
OBR|1|ORD-RAD-20251201-002^MAYO|PS-RPT-20251201-026789^POWERSCRIBE|72170^XR PELVIS AP^CPT4|||20251201041500|||||||||||4291038^Thorsgaard^Karen^S^^^MD||RAD-ACC-20251201-0002||||20251201054500|||F|||||||5820194^Engstrom^Anna^M^^^MD^Emergency Radiology
OBX|1|TX|72170^XR PELVIS AP^CPT4|1|XR PELVIS AP~~CLINICAL INDICATION: Fall from standing height. Hip pain bilateral.~~COMPARISON: None.~~FINDINGS:~Pelvis: Displaced fracture of the left inferior pubic ramus. Nondisplaced fracture of the left superior pubic ramus. No acetabular fracture. Sacroiliac joints are symmetric and intact.~Hips: No femoral neck fracture bilaterally. Mild bilateral hip joint space narrowing consistent with degenerative change.~Soft tissues: Soft tissue swelling overlying the left pelvis.~~IMPRESSION:~1. Displaced fracture of the left inferior pubic ramus and nondisplaced fracture of the left superior pubic ramus.~2. No acetabular or femoral neck fracture.~3. Orthopedic consultation recommended. CT pelvis may be considered if concern for additional injury.||||||F
```
