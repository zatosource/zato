# Sectra PACS - real HL7v2 ER7 messages

---

## 1. ORM^O01 - CT abdomen order from ED

```
MSH|^~\&|SECTRA|MARY_WASH_RAD^9012^DNS|RIS_SYS|VAHIE|20260401083000||ORM^O01^ORM_O01|SEC00001|P|2.5.1|||AL|NE
PID|1||MRN71234567^^^MARY_WASH^MR||WHITMORE^Brendan^Allen||19770504|M|||1515 Fall Hill Ave^^Fredericksburg^VA^22401^US||^PRN^PH^^1^540^5553182||||M||ACCT7112233^^^MARY_WASH^AN
PV1|1|E|ED^BED09^1^MARY_WASH_MED||||ORDERING^Okafor^Adaeze^^^^MD^STAFF|||EM
ORC|NW|ORD80123^^RIS||GRP018|IP||||20260401082500|||ORDERING^Okafor^Adaeze^^^^MD^STAFF
OBR|1|ORD80123^^RIS||74178^CT Abdomen Pelvis with contrast^CPT|||20260401093000||||STAT|||||ORDERING^Okafor^Adaeze^^^^MD^STAFF|^WPN^PH^^1^540^5559012|||||||||1^^^^^S
DG1|1||R10.9^Unspecified abdominal pain^ICD10|||W
```

---

## 2. ORM^O01 - MRI knee order from orthopedics

```
MSH|^~\&|SECTRA|CHESAPEAKE_RAD^9013^DNS|RIS_SYS|VAHIE|20260402101500||ORM^O01^ORM_O01|SEC00002|P|2.5.1|||AL|NE
PID|1||MRN72345678^^^CHESAPEAKE^MR||SALAZAR^Gabriela^Denise||19900821|F|||3315 Western Branch Blvd^^Chesapeake^VA^23321^US||^PRN^PH^^1^757^5554293||||S||ACCT7223344^^^CHESAPEAKE^AN
PV1|1|O|RAD^WAIT^1^CHESAPEAKE_RAD||||ORDERING^Nakamura^Toshiro^^^^MD^STAFF|||ORT
ORC|NW|ORD81234^^RIS||GRP019|IP||||20260402101000|||ORDERING^Nakamura^Toshiro^^^^MD^STAFF
OBR|1|ORD81234^^RIS||73721^MRI Knee without contrast^CPT|||20260404080000|||||||||ORDERING^Nakamura^Toshiro^^^^MD^STAFF|^WPN^PH^^1^757^5559876|||||||||1^^^^^R
DG1|1||M23.51^Chronic instability of knee right^ICD10|||W
```

---

## 3. ORU^R01 - CT abdomen findings report

```
MSH|^~\&|SECTRA|MARY_WASH_RAD^9012^DNS|EHR_SYS|VAHIE|20260401120000||ORU^R01^ORU_R01|SEC00003|P|2.5.1|||AL|NE
PID|1||MRN71234567^^^MARY_WASH^MR||WHITMORE^Brendan^Allen||19770504|M|||1515 Fall Hill Ave^^Fredericksburg^VA^22401^US||^PRN^PH^^1^540^5553182||||M||ACCT7112233^^^MARY_WASH^AN
PV1|1|E|ED^BED09^1^MARY_WASH_MED||||READING^Petrov^Svetlana^^^^MD^STAFF|||RAD
ORC|RE|ORD80123^^RIS|FIL90234^^SECTRA||CM||||20260401083000|||READING^Petrov^Svetlana^^^^MD^STAFF
OBR|1|ORD80123^^RIS|FIL90234^^SECTRA|74178^CT Abdomen Pelvis with contrast^CPT|||20260401094500|||||||||ORDERING^Okafor^Adaeze^^^^MD^STAFF||||||20260401115500|||F
OBX|1|FT|18782-3^Radiology Study Observation^LN||CT Abdomen and Pelvis with IV Contrast:\.br\\.br\Findings: Acute appendicitis with periappendiceal inflammatory stranding. Appendix measures 12mm in diameter. No evidence of perforation. No free fluid. No bowel obstruction.\.br\\.br\Impression: Acute uncomplicated appendicitis.||||||F|||20260401115500
```

---

## 4. ORU^R01 - MRI knee report with embedded PDF

```
MSH|^~\&|SECTRA|CHESAPEAKE_RAD^9013^DNS|EHR_SYS|VAHIE|20260404111500||ORU^R01^ORU_R01|SEC00004|P|2.5.1|||AL|NE
PID|1||MRN72345678^^^CHESAPEAKE^MR||SALAZAR^Gabriela^Denise||19900821|F|||3315 Western Branch Blvd^^Chesapeake^VA^23321^US||^PRN^PH^^1^757^5554293||||S||ACCT7223344^^^CHESAPEAKE^AN
PV1|1|O|RAD^READ^1^CHESAPEAKE_RAD||||READING^Subramaniam^Lalitha^^^^MD^STAFF|||RAD
ORC|RE|ORD81234^^RIS|FIL91345^^SECTRA||CM||||20260402101500|||READING^Subramaniam^Lalitha^^^^MD^STAFF
OBR|1|ORD81234^^RIS|FIL91345^^SECTRA|73721^MRI Knee without contrast^CPT|||20260404083000|||||||||ORDERING^Nakamura^Toshiro^^^^MD^STAFF||||||20260404111000|||F
OBX|1|FT|18782-3^Radiology Study Observation^LN||MRI Right Knee without Contrast:\.br\\.br\Findings: Complete tear of the anterior cruciate ligament with associated bone bruising of the lateral femoral condyle and posterolateral tibial plateau. Small joint effusion. Intact menisci. Intact collateral ligaments.\.br\\.br\Impression: ACL tear with bone contusions. No meniscal injury.||||||F|||20260404111000
OBX|2|ED|PDF^Radiology Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxMDIKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihNUkkgUmlnaHQgS25lZSBSZXBvcnQpIFRqCjAgLTIwIFRkCihJbXByZXNzaW9uOiBBQ0wgVGVhciBXaXRoIEJvbmUgQ29udHVzaW9ucykgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago=|||F|||20260404111000
```

---

## 5. ORM^O01 - Chest X-ray order pre-surgery

```
MSH|^~\&|SECTRA|MARY_WASH_RAD^9012^DNS|RIS_SYS|VAHIE|20260405071000||ORM^O01^ORM_O01|SEC00005|P|2.5.1|||AL|NE
PID|1||MRN73456789^^^MARY_WASH^MR||OGLETREE^Mildred^Margaret||19531016|F|||3315 Plank Rd^^Fredericksburg^VA^22407^US||^PRN^PH^^1^540^5555314||||W||ACCT7334455^^^MARY_WASH^AN
PV1|1|I|SURG^PRE^1^MARY_WASH_MED||||ORDERING^Castellano^Diego^^^^MD^STAFF|||SUR
ORC|NW|ORD82345^^RIS||GRP020|IP||||20260405070500|||ORDERING^Castellano^Diego^^^^MD^STAFF
OBR|1|ORD82345^^RIS||71046^Chest X-ray 2 views^CPT|||20260405080000|||||||||ORDERING^Castellano^Diego^^^^MD^STAFF|||||||||||||PRE-OP
DG1|1||K80.20^Calculus of gallbladder^ICD10|||W
```

---

## 6. ORU^R01 - Chest X-ray normal result

```
MSH|^~\&|SECTRA|MARY_WASH_RAD^9012^DNS|EHR_SYS|VAHIE|20260405100000||ORU^R01^ORU_R01|SEC00006|P|2.5.1|||AL|NE
PID|1||MRN73456789^^^MARY_WASH^MR||OGLETREE^Mildred^Margaret||19531016|F|||3315 Plank Rd^^Fredericksburg^VA^22407^US||^PRN^PH^^1^540^5555314||||W||ACCT7334455^^^MARY_WASH^AN
PV1|1|I|SURG^PRE^1^MARY_WASH_MED||||READING^Petrov^Svetlana^^^^MD^STAFF|||RAD
ORC|RE|ORD82345^^RIS|FIL92456^^SECTRA||CM||||20260405071000|||READING^Petrov^Svetlana^^^^MD^STAFF
OBR|1|ORD82345^^RIS|FIL92456^^SECTRA|71046^Chest X-ray 2 views^CPT|||20260405081500|||||||||ORDERING^Castellano^Diego^^^^MD^STAFF||||||20260405095500|||F
OBX|1|FT|18782-3^Radiology Study Observation^LN||Chest PA and Lateral:\.br\\.br\Findings: Lungs are clear. No focal consolidation or pleural effusion. Heart size and mediastinal contours are normal. No acute osseous abnormality identified.\.br\\.br\Impression: Normal chest radiograph. Patient cleared for surgery.||||||F|||20260405095500
```

---

## 7. ORM^O01 - Mammogram screening order

```
MSH|^~\&|SECTRA|FREDERICKSBURG_IMG^9014^DNS|RIS_SYS|VAHIE|20260406130000||ORM^O01^ORM_O01|SEC00007|P|2.5.1|||AL|NE
PID|1||MRN74567890^^^MARY_WASH^MR||DANFORTH^Lorraine^Marie||19701104|F|||5715 Bragg Rd^^Fredericksburg^VA^22407^US||^PRN^PH^^1^540^5556425||||M||ACCT7445566^^^MARY_WASH^AN
PV1|1|O|MAM^WAIT^1^FREDERICKSBURG_IMG||||ORDERING^Obi^Chiamaka^^^^MD^STAFF|||GEN
ORC|NW|ORD83456^^RIS||GRP021|IP||||20260406125500|||ORDERING^Obi^Chiamaka^^^^MD^STAFF
OBR|1|ORD83456^^RIS||77067^Screening Mammogram Bilateral^CPT|||20260406140000|||||||||ORDERING^Obi^Chiamaka^^^^MD^STAFF
```

---

## 8. ORU^R01 - Mammogram result with BI-RADS

```
MSH|^~\&|SECTRA|FREDERICKSBURG_IMG^9014^DNS|EHR_SYS|VAHIE|20260406160000||ORU^R01^ORU_R01|SEC00008|P|2.5.1|||AL|NE
PID|1||MRN74567890^^^MARY_WASH^MR||DANFORTH^Lorraine^Marie||19701104|F|||5715 Bragg Rd^^Fredericksburg^VA^22407^US||^PRN^PH^^1^540^5556425||||M||ACCT7445566^^^MARY_WASH^AN
PV1|1|O|MAM^READ^1^FREDERICKSBURG_IMG||||READING^Vasquez^Catalina^^^^MD^STAFF|||RAD
ORC|RE|ORD83456^^RIS|FIL93567^^SECTRA||CM||||20260406130000|||READING^Vasquez^Catalina^^^^MD^STAFF
OBR|1|ORD83456^^RIS|FIL93567^^SECTRA|77067^Screening Mammogram Bilateral^CPT|||20260406141500|||||||||ORDERING^Obi^Chiamaka^^^^MD^STAFF||||||20260406155500|||F
OBX|1|FT|18782-3^Radiology Study Observation^LN||Bilateral Screening Mammogram:\.br\\.br\Breast composition: Scattered areas of fibroglandular density.\.br\\.br\Findings: No suspicious masses, calcifications, or architectural distortion identified bilaterally.\.br\\.br\Impression: Negative. BI-RADS Category 1.\.br\Recommendation: Routine annual screening mammography.||||||F|||20260406155500
OBX|2|CWE|36625-2^BI-RADS Assessment^LN||BIRADS1^Category 1 Negative^BIRADS||||||F|||20260406155500
```

---

## 9. ORM^O01 - Ultrasound abdomen order

```
MSH|^~\&|SECTRA|CHESAPEAKE_RAD^9013^DNS|RIS_SYS|VAHIE|20260407091500||ORM^O01^ORM_O01|SEC00009|P|2.5.1|||AL|NE
PID|1||MRN75678901^^^CHESAPEAKE^MR||FUENTES^Hector^Paul||19810809|M|||4215 Portsmouth Blvd^^Chesapeake^VA^23321^US||^PRN^PH^^1^757^5557536||||M||ACCT7556677^^^CHESAPEAKE^AN
PV1|1|O|US^WAIT^1^CHESAPEAKE_RAD||||ORDERING^Oyelaran^Babatunde^^^^MD^STAFF|||GI
ORC|NW|ORD84567^^RIS||GRP022|IP||||20260407091000|||ORDERING^Oyelaran^Babatunde^^^^MD^STAFF
OBR|1|ORD84567^^RIS||76700^US Abdomen Complete^CPT|||20260407103000|||||||||ORDERING^Oyelaran^Babatunde^^^^MD^STAFF
DG1|1||R16.0^Hepatomegaly not elsewhere classified^ICD10|||W
```

---

## 10. ORU^R01 - Ultrasound abdomen report

```
MSH|^~\&|SECTRA|CHESAPEAKE_RAD^9013^DNS|EHR_SYS|VAHIE|20260407131500||ORU^R01^ORU_R01|SEC00010|P|2.5.1|||AL|NE
PID|1||MRN75678901^^^CHESAPEAKE^MR||FUENTES^Hector^Paul||19810809|M|||4215 Portsmouth Blvd^^Chesapeake^VA^23321^US||^PRN^PH^^1^757^5557536||||M||ACCT7556677^^^CHESAPEAKE^AN
PV1|1|O|US^READ^1^CHESAPEAKE_RAD||||READING^Subramaniam^Lalitha^^^^MD^STAFF|||RAD
ORC|RE|ORD84567^^RIS|FIL94678^^SECTRA||CM||||20260407091500|||READING^Subramaniam^Lalitha^^^^MD^STAFF
OBR|1|ORD84567^^RIS|FIL94678^^SECTRA|76700^US Abdomen Complete^CPT|||20260407104500|||||||||ORDERING^Oyelaran^Babatunde^^^^MD^STAFF||||||20260407131000|||F
OBX|1|FT|18782-3^Radiology Study Observation^LN||Ultrasound Abdomen Complete:\.br\\.br\Liver: Mildly enlarged measuring 18cm in craniocaudal dimension. Diffusely increased echogenicity consistent with hepatic steatosis. No focal hepatic lesions.\.br\Gallbladder: Normal appearance. No stones or wall thickening.\.br\Pancreas: Normal.\.br\Spleen: Normal size.\.br\Kidneys: Normal bilateral.\.br\Aorta: Normal caliber.\.br\\.br\Impression: Hepatic steatosis with mild hepatomegaly. No focal lesion.||||||F|||20260407131000
```

---

## 11. ADT^A04 - Patient registration for imaging

```
MSH|^~\&|SECTRA|MARY_WASH_RAD^9012^DNS|REG_SYS|VAHIE|20260408072000||ADT^A04^ADT_A04|SEC00011|P|2.5.1|||AL|NE
EVN|A04|20260408072000|||REG^Mason^Kelly^A^^^CLERK
PID|1||MRN76789012^^^MARY_WASH^MR||HAYWOOD^Clifton^Edward||19650618|M|||2815 Cowan Blvd^^Fredericksburg^VA^22401^US||^PRN^PH^^1^540^5558647||||M||ACCT7667788^^^MARY_WASH^AN
PV1|1|O|RAD^WAIT^1^MARY_WASH_RAD||||ORDERING^Okafor^Adaeze^^^^MD^STAFF|||RAD
IN1|1|AETNA001|Aetna|151 Farmington Ave^^Hartford^CT^06156|||||GRP12345||PRINCE WILLIAM COUNTY SCHOOLS|||20250601|20261231|||HAYWOOD^Clifton^E|SELF|19650618|2815 Cowan Blvd^^Fredericksburg^VA^22401^US
```

---

## 12. ORM^O01 - CT head order for trauma

```
MSH|^~\&|SECTRA|MARY_WASH_RAD^9012^DNS|RIS_SYS|VAHIE|20260409022000||ORM^O01^ORM_O01|SEC00012|P|2.5.1|||AL|NE
PID|1||MRN77890123^^^MARY_WASH^MR||KWON^Brian^Wayne||19940212|M|||1915 Princess Anne St^^Fredericksburg^VA^22401^US||^PRN^PH^^1^540^5559758||||S||ACCT7778899^^^MARY_WASH^AN
PV1|1|E|ED^BED03^1^MARY_WASH_MED||||ORDERING^Okafor^Adaeze^^^^MD^STAFF|||EM
ORC|NW|ORD85678^^RIS||GRP023|IP||||20260409021500|||ORDERING^Okafor^Adaeze^^^^MD^STAFF
OBR|1|ORD85678^^RIS||70450^CT Head without contrast^CPT|||20260409023000||||STAT|||||ORDERING^Okafor^Adaeze^^^^MD^STAFF|||||||||||||TRAUMA
DG1|1||S06.0X0A^Concussion without loss of consciousness initial encounter^ICD10|||W
```

---

## 13. ORU^R01 - CT head report with embedded PDF

```
MSH|^~\&|SECTRA|MARY_WASH_RAD^9012^DNS|EHR_SYS|VAHIE|20260409040000||ORU^R01^ORU_R01|SEC00013|P|2.5.1|||AL|NE
PID|1||MRN77890123^^^MARY_WASH^MR||KWON^Brian^Wayne||19940212|M|||1915 Princess Anne St^^Fredericksburg^VA^22401^US||^PRN^PH^^1^540^5559758||||S||ACCT7778899^^^MARY_WASH^AN
PV1|1|E|ED^BED03^1^MARY_WASH_MED||||READING^Petrov^Svetlana^^^^MD^STAFF|||RAD
ORC|RE|ORD85678^^RIS|FIL95789^^SECTRA||CM||||20260409022000|||READING^Petrov^Svetlana^^^^MD^STAFF
OBR|1|ORD85678^^RIS|FIL95789^^SECTRA|70450^CT Head without contrast^CPT|||20260409025000|||||||||ORDERING^Okafor^Adaeze^^^^MD^STAFF||||||20260409035500|||F
OBX|1|FT|18782-3^Radiology Study Observation^LN||CT Head without Contrast:\.br\\.br\Findings: No acute intracranial hemorrhage. No midline shift. No skull fracture. Ventricles and sulci are normal in size and configuration. Gray-white matter differentiation is preserved.\.br\\.br\Impression: No acute intracranial pathology.||||||F|||20260409035500
OBX|2|ED|PDF^Radiology Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA3NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKENUIEhlYWQgV2l0aG91dCBDb250cmFzdCAtIE5vIEFjdXRlIFBhdGhvbG9neSkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago=|||F|||20260409035500
```

---

## 14. ORM^O01 - Bone density scan order

```
MSH|^~\&|SECTRA|FREDERICKSBURG_IMG^9014^DNS|RIS_SYS|VAHIE|20260410090000||ORM^O01^ORM_O01|SEC00014|P|2.5.1|||AL|NE
PID|1||MRN78901234^^^MARY_WASH^MR||PEMBERTON^Gladys^Ellen||19551007|F|||4515 Mine Rd^^Fredericksburg^VA^22408^US||^PRN^PH^^1^540^5551869||||W||ACCT7889900^^^MARY_WASH^AN
PV1|1|O|DEXA^WAIT^1^FREDERICKSBURG_IMG||||ORDERING^Obi^Chiamaka^^^^MD^STAFF|||GEN
ORC|NW|ORD86789^^RIS||GRP024|IP||||20260410085500|||ORDERING^Obi^Chiamaka^^^^MD^STAFF
OBR|1|ORD86789^^RIS||77080^DEXA Bone Density^CPT|||20260410100000|||||||||ORDERING^Obi^Chiamaka^^^^MD^STAFF
DG1|1||M81.0^Age-related osteoporosis without current pathological fracture^ICD10|||W
```

---

## 15. ORU^R01 - DEXA scan results

```
MSH|^~\&|SECTRA|FREDERICKSBURG_IMG^9014^DNS|EHR_SYS|VAHIE|20260410130000||ORU^R01^ORU_R01|SEC00015|P|2.5.1|||AL|NE
PID|1||MRN78901234^^^MARY_WASH^MR||PEMBERTON^Gladys^Ellen||19551007|F|||4515 Mine Rd^^Fredericksburg^VA^22408^US||^PRN^PH^^1^540^5551869||||W||ACCT7889900^^^MARY_WASH^AN
PV1|1|O|DEXA^READ^1^FREDERICKSBURG_IMG||||READING^Vasquez^Catalina^^^^MD^STAFF|||RAD
ORC|RE|ORD86789^^RIS|FIL96890^^SECTRA||CM||||20260410090000|||READING^Vasquez^Catalina^^^^MD^STAFF
OBR|1|ORD86789^^RIS|FIL96890^^SECTRA|77080^DEXA Bone Density^CPT|||20260410101500|||||||||ORDERING^Obi^Chiamaka^^^^MD^STAFF||||||20260410125500|||F
OBX|1|NM|38263-0^Lumbar Spine T-score^LN||-2.8||>-1.0|L|||F|||20260410125500
OBX|2|NM|38264-8^Left Femoral Neck T-score^LN||-2.3||>-1.0|L|||F|||20260410125500
OBX|3|FT|18782-3^Radiology Study Observation^LN||DEXA Bone Density:\.br\\.br\Lumbar Spine L1-L4 T-score: -2.8 (Osteoporosis range)\.br\Left Femoral Neck T-score: -2.3 (Osteopenia range)\.br\\.br\Impression: Osteoporosis at the lumbar spine. Osteopenia at the left femoral neck.\.br\Recommendation: Consider pharmacologic therapy. Follow-up DEXA in 2 years.||||||F|||20260410125500
```

---

## 16. ADT^A08 - Patient weight update for contrast dosing

```
MSH|^~\&|SECTRA|CHESAPEAKE_RAD^9013^DNS|RIS_SYS|VAHIE|20260411081000||ADT^A08^ADT_A08|SEC00016|P|2.5.1|||AL|NE
EVN|A08|20260411081000|||TECH^Henderson^Paul^R^^^RT
PID|1||MRN79012345^^^CHESAPEAKE^MR||ASHWORTH^Deborah^Lynn||19731123|F|||2615 Taylor Rd^^Chesapeake^VA^23321^US||^PRN^PH^^1^757^5552971||||M||ACCT7900112^^^CHESAPEAKE^AN
PV1|1|O|CT^SCAN1^1^CHESAPEAKE_RAD||||ORDERING^Oyelaran^Babatunde^^^^MD^STAFF|||RAD
OBX|1|NM|29463-7^Body Weight^LN||72.5|kg||N|||F|||20260411081000
OBX|2|NM|8302-2^Body Height^LN||165|cm||N|||F|||20260411081000
```

---

## 17. ORM^O01 - Fluoroscopy guided injection order

```
MSH|^~\&|SECTRA|MARY_WASH_RAD^9012^DNS|RIS_SYS|VAHIE|20260412100000||ORM^O01^ORM_O01|SEC00017|P|2.5.1|||AL|NE
PID|1||MRN80123456^^^MARY_WASH^MR||FUENTES^Roberto^Miguel||19670421|M|||6815 Harrison Rd^^Fredericksburg^VA^22407^US||^PRN^PH^^1^540^5553182||||M||ACCT8011223^^^MARY_WASH^AN
PV1|1|O|FLUORO^PROC^1^MARY_WASH_RAD||||ORDERING^Castellano^Diego^^^^MD^STAFF|||PM
ORC|NW|ORD87890^^RIS||GRP025|IP||||20260412095500|||ORDERING^Castellano^Diego^^^^MD^STAFF
OBR|1|ORD87890^^RIS||27096^Lumbar Epidural Steroid Injection Fluoro^CPT|||20260412110000|||||||||ORDERING^Castellano^Diego^^^^MD^STAFF
DG1|1||M54.16^Radiculopathy lumbar region^ICD10|||W
```

---

## 18. ORU^R01 - Fluoroscopy procedure report

```
MSH|^~\&|SECTRA|MARY_WASH_RAD^9012^DNS|EHR_SYS|VAHIE|20260412133000||ORU^R01^ORU_R01|SEC00018|P|2.5.1|||AL|NE
PID|1||MRN80123456^^^MARY_WASH^MR||FUENTES^Roberto^Miguel||19670421|M|||6815 Harrison Rd^^Fredericksburg^VA^22407^US||^PRN^PH^^1^540^5553182||||M||ACCT8011223^^^MARY_WASH^AN
PV1|1|O|FLUORO^PROC^1^MARY_WASH_RAD||||PERFORMING^Castellano^Diego^^^^MD^STAFF|||PM
ORC|RE|ORD87890^^RIS|FIL97901^^SECTRA||CM||||20260412100000|||PERFORMING^Castellano^Diego^^^^MD^STAFF
OBR|1|ORD87890^^RIS|FIL97901^^SECTRA|27096^Lumbar Epidural Steroid Injection Fluoro^CPT|||20260412111500|||||||||ORDERING^Castellano^Diego^^^^MD^STAFF||||||20260412132500|||F
OBX|1|FT|18782-3^Radiology Study Observation^LN||Fluoroscopy-Guided L4-L5 Interlaminar Epidural Steroid Injection:\.br\\.br\Procedure: Under fluoroscopic guidance, a 20-gauge Tuohy needle was advanced to the L4-L5 interlaminar space. Loss of resistance technique confirmed epidural placement. Contrast injection confirmed epidural spread. 80mg Depo-Medrol and 1mL 0.25% bupivacaine injected.\.br\\.br\Complications: None. Patient tolerated procedure well.\.br\Fluoroscopy time: 45 seconds.||||||F|||20260412132500
```

---

## 19. ADT^A03 - Patient discharged from imaging observation

```
MSH|^~\&|SECTRA|CHESAPEAKE_RAD^9013^DNS|ADT_RECV|VAHIE|20260413150000||ADT^A03^ADT_A03|SEC00019|P|2.5.1|||AL|NE
EVN|A03|20260413150000|||NURSE^Adams^Theresa^J^^^RN
PID|1||MRN81234567^^^CHESAPEAKE^MR||THORNBURG^Clifford^Henry||19600607|M|||2015 Battlefield Blvd^^Chesapeake^VA^23320^US||^PRN^PH^^1^757^5554293||||M||ACCT8122334^^^CHESAPEAKE^AN
PV1|1|O|RAD^OBS^1^CHESAPEAKE_RAD||||PROVIDER^Subramaniam^Lalitha^^^^MD^STAFF|||RAD||||OBS|||PROVIDER^Subramaniam^Lalitha^^^^MD^STAFF|OP||SELF|||||||||||||||||||CHESAPEAKE_RAD|||||20260413080000|||||||20260413150000
```

---

## 20. ACK - Acknowledgment for radiology order

```
MSH|^~\&|RIS_SYS|VAHIE|SECTRA|MARY_WASH_RAD^9012^DNS|20260414080100||ACK^O01^ACK|ACK_SEC00017|P|2.5.1|||AL|NE
MSA|AA|SEC00017|Order received and scheduled
```
