# CRIS (Wellbeing Software/Magentus) - real HL7v2 ER7 messages

---

## 1. ORM^O01 - New radiology order received (chest X-ray)

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260401091000||ORM^O01^ORM_O01|CRIS20260401001|P|2.4|||AL|NE||ASCII
PID|||7012345678^^^NHS^NH~KC901234^^^RBK^MR||ACHEBE^EMEKA^CHUKWUDI||19600321|M|||73 Old Kent Road^^London^^SE1 5LQ^GBR||02072013456||||||7012345678
PV1||I|CARDIO^BAY3^BED12^KCH||||C4509876^MACKAY^ALISTAIR^^^Mr^^^GMC|||||||||||NHS|228901^^^RBK^VN
ORC|SC|RAD260401001||CRIS260401001|IP|||||||C4509876^MACKAY^ALISTAIR^^^Mr^^^GMC
OBR|1|RAD260401001|CRIS260401001|CXRPA^Chest X-Ray PA^CRIS|||20260401091000||||||||C4509876^MACKAY^ALISTAIR^^^Mr^^^GMC|||CR|||||||||1^^^20260401100000^^S
NTE|1||Pre-CABG assessment. Known cardiomegaly.
```

---

## 2. ORM^O01 - Examination scheduled (CT head)

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260401110000||ORM^O01^ORM_O01|CRIS20260401002|P|2.4|||AL|NE||ASCII
PID|||7123456789^^^NHS^NH~KC012345^^^RBK^MR||KOWALSKA^AGNIESZKA^MARIA||19510315|F|||44 Norwood Road^^London^^SE24 9AA^GBR||02086124567||||||7123456789
PV1||E|AE^RESUS^BAY1^KCH||||C9905678^FRASER^HAMISH^^^Dr^^^GMC|||||||||||NHS|889012^^^RBK^VN
ORC|SC|RAD260401002||CRIS260401002|SC|||||||C9905678^FRASER^HAMISH^^^Dr^^^GMC
OBR|1|RAD260401002|CRIS260401002|CTHEAD^CT Head Non-Contrast^CRIS|||20260401110000||||||||C9905678^FRASER^HAMISH^^^Dr^^^GMC|||CT|||||||||1^^^20260401113000^^S
NTE|1||URGENT. Acute confusion, unilateral weakness. ? stroke. GCS 13.
```

---

## 3. ORM^O01 - Examination in progress (MRI brain)

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260402140000||ORM^O01^ORM_O01|CRIS20260402003|P|2.4|||AL|NE||ASCII
PID|||7234567890^^^NHS^NH~KC123456^^^RBK^MR||MCLAUGHLIN^SIOBHAN^AISLING||19850118|F|||28 Lewisham Way^^London^^SE14 6PP^GBR||02086235678||||||7234567890
PV1||O|NEURO^CLINIC1^^KCH||||C5617890^NAVARRO^ELENA^^^Dr^^^GMC|||||||||||NHS|228902^^^RBK^VN
ORC|SC|RAD260402003||CRIS260402003|IP
OBR|1|RAD260402003|CRIS260402003|MRIBRAIN^MRI Brain with Contrast^CRIS|||20260402140000||||||||C5617890^NAVARRO^ELENA^^^Dr^^^GMC|||MR|||||||||1^^^20260402140000^^R
NTE|1||Recurrent headaches, papilloedema on fundoscopy. Exclude SOL.
```

---

## 4. ORU^R01 - Chest X-ray report

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260401143000||ORU^R01^ORU_R01|CRIS20260401004|P|2.4|||AL|NE||ASCII
PID|||7012345678^^^NHS^NH~KC901234^^^RBK^MR||ACHEBE^EMEKA^CHUKWUDI||19600321|M|||73 Old Kent Road^^London^^SE1 5LQ^GBR||02072013456||||||7012345678
PV1||I|CARDIO^BAY3^BED12^KCH||||C4509876^MACKAY^ALISTAIR^^^Mr^^^GMC|||||||||||NHS|228901^^^RBK^VN
ORC|RE|RAD260401001|CRIS260401001||CM
OBR|1|RAD260401001|CRIS260401001|CXRPA^Chest X-Ray PA^CRIS|||20260401100000|||||||20260401101000||C4509876^MACKAY^ALISTAIR^^^Mr^^^GMC|||CR||||20260401143000|||F|||C1234567^GUPTA^NEHA^^^Dr^^^GMC
OBX|1|TX|RAD_RPT^Radiology Report^CRIS||EXAMINATION: Chest X-Ray PA||||||F
OBX|2|TX|RAD_RPT^Radiology Report^CRIS||CLINICAL DETAILS: Pre-CABG. Known cardiomegaly.||||||F
OBX|3|TX|RAD_RPT^Radiology Report^CRIS||FINDINGS: The heart is enlarged with a cardiothoracic ratio of 0.58.||||||F
OBX|4|TX|RAD_RPT^Radiology Report^CRIS||Upper lobe pulmonary venous congestion suggestive of mild pulmonary oedema.||||||F
OBX|5|TX|RAD_RPT^Radiology Report^CRIS||No focal consolidation or pleural effusion. Mediastinal contour normal.||||||F
OBX|6|TX|RAD_RPT^Radiology Report^CRIS||IMPRESSION: Cardiomegaly with early pulmonary oedema. No acute lung pathology.||||||F
OBX|7|TX|RAD_RPT^Radiology Report^CRIS||Reported by: Dr Neha Gupta, Consultant Radiologist||||||F
```

---

## 5. ORU^R01 - CT head report (acute stroke)

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260401131500||ORU^R01^ORU_R01|CRIS20260401005|P|2.4|||AL|NE||ASCII
PID|||7123456789^^^NHS^NH~KC012345^^^RBK^MR||KOWALSKA^AGNIESZKA^MARIA||19510315|F|||44 Norwood Road^^London^^SE24 9AA^GBR||02086124567||||||7123456789
PV1||E|AE^RESUS^BAY1^KCH||||C9905678^FRASER^HAMISH^^^Dr^^^GMC|||||||||||NHS|889012^^^RBK^VN
ORC|RE|RAD260401002|CRIS260401002||CM
OBR|1|RAD260401002|CRIS260401002|CTHEAD^CT Head Non-Contrast^CRIS|||20260401113000|||||||20260401114000||C9905678^FRASER^HAMISH^^^Dr^^^GMC|||CT||||20260401131500|||F|||C2345678^OGUNYEMI^ADEBOLA^^^Dr^^^GMC
OBX|1|TX|RAD_RPT^Radiology Report^CRIS||EXAMINATION: CT Head Non-Contrast||||||F
OBX|2|TX|RAD_RPT^Radiology Report^CRIS||CLINICAL DETAILS: Acute confusion, R-sided weakness 2 hours. ? stroke.||||||F
OBX|3|TX|RAD_RPT^Radiology Report^CRIS||FINDINGS: Large area of hypodensity in the left MCA territory involving||||||F
OBX|4|TX|RAD_RPT^Radiology Report^CRIS||the left frontal and parietal lobes consistent with acute ischaemic infarction.||||||F
OBX|5|TX|RAD_RPT^Radiology Report^CRIS||No haemorrhagic transformation. No midline shift.||||||F
OBX|6|TX|RAD_RPT^Radiology Report^CRIS||IMPRESSION: Acute left MCA territory infarct. No haemorrhage. Discuss with stroke team.||||||F
OBX|7|TX|RAD_RPT^Radiology Report^CRIS||ADDENDUM: Telephoned to Dr Fraser in AE at 13:10 01/04/2026.||||||F
OBX|8|TX|RAD_RPT^Radiology Report^CRIS||Reported by: Dr Adebola Ogunyemi, Consultant Neuroradiologist||||||F
```

---

## 6. ORM^O01 - New order (ultrasound abdomen)

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260403090000||ORM^O01^ORM_O01|CRIS20260403006|P|2.4|||AL|NE||ASCII
PID|||7345678901^^^NHS^NH~KC234567^^^RBK^MR||PATEL^RAJAN^VIKRAM||19780504|M|||55 Bermondsey Street^^London^^SE1 3XG^GBR||02071346789||||||7345678901
PV1||I|GASTRO^WARD6^BED03^KCH||||C8927890^RAHMAN^SHABANA^^^Dr^^^GMC|||||||||||NHS|667802^^^RBK^VN
ORC|SC|RAD260403006||CRIS260403006|SC|||||||C8927890^RAHMAN^SHABANA^^^Dr^^^GMC
OBR|1|RAD260403006|CRIS260403006|USABD^Ultrasound Abdomen^CRIS|||20260403090000||||||||C8927890^RAHMAN^SHABANA^^^Dr^^^GMC|||US|||||||||1^^^20260403103000^^R
NTE|1||Obstructive jaundice. Bilirubin 89. CT showed pancreatic head mass. US for biliary detail.
```

---

## 7. ORU^R01 - MRI brain report

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260403160000||ORU^R01^ORU_R01|CRIS20260403007|P|2.4|||AL|NE||ASCII
PID|||7234567890^^^NHS^NH~KC123456^^^RBK^MR||MCLAUGHLIN^SIOBHAN^AISLING||19850118|F|||28 Lewisham Way^^London^^SE14 6PP^GBR||02086235678||||||7234567890
PV1||O|NEURO^CLINIC1^^KCH||||C5617890^NAVARRO^ELENA^^^Dr^^^GMC|||||||||||NHS|228902^^^RBK^VN
ORC|RE|RAD260402003|CRIS260402003||CM
OBR|1|RAD260402003|CRIS260402003|MRIBRAIN^MRI Brain with Contrast^CRIS|||20260402140000|||||||20260402141000||C5617890^NAVARRO^ELENA^^^Dr^^^GMC|||MR||||20260403160000|||F|||C3456789^EZEKIEL^OLUWADAMILOLA^^^Dr^^^GMC
OBX|1|TX|RAD_RPT^Radiology Report^CRIS||EXAMINATION: MRI Brain with Gadolinium||||||F
OBX|2|TX|RAD_RPT^Radiology Report^CRIS||CLINICAL DETAILS: Headaches, papilloedema. Exclude SOL.||||||F
OBX|3|TX|RAD_RPT^Radiology Report^CRIS||FINDINGS: Normal intracranial appearances. No mass lesion identified.||||||F
OBX|4|TX|RAD_RPT^Radiology Report^CRIS||No hydrocephalus. Pituitary gland normal size and morphology.||||||F
OBX|5|TX|RAD_RPT^Radiology Report^CRIS||Venous sinuses patent. No dural enhancement.||||||F
OBX|6|TX|RAD_RPT^Radiology Report^CRIS||IMPRESSION: Normal MRI brain. Consider idiopathic intracranial hypertension.||||||F
OBX|7|TX|RAD_RPT^Radiology Report^CRIS||Reported by: Dr Oluwadamilola Ezekiel, Consultant Neuroradiologist||||||F
```

---

## 8. ORM^O01 - New order (CT chest abdomen pelvis)

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260404100000||ORM^O01^ORM_O01|CRIS20260404008|P|2.4|||AL|NE||ASCII
PID|||7456789012^^^NHS^NH~KC345678^^^RBK^MR||ADEMOLA^OLUFEMI^KAYODE||19910824|M|||17 Walworth Road^^London^^SE17 1RW^GBR||02077457890||||||7456789012
PV1||O|ONCOL^CLINIC2^^KCH||||C1018901^MURPHY^CIARAN^^^Dr^^^GMC|||||||||||NHS|778901^^^RBK^VN
ORC|SC|RAD260404008||CRIS260404008|SC|||||||C1018901^MURPHY^CIARAN^^^Dr^^^GMC
OBR|1|RAD260404008|CRIS260404008|CTCAP^CT Chest Abdomen Pelvis with Contrast^CRIS|||20260404100000||||||||C1018901^MURPHY^CIARAN^^^Dr^^^GMC|||CT|||||||||1^^^20260404140000^^R
NTE|1||Staging CT. Newly diagnosed colorectal cancer. Pre-MDT.
```

---

## 9. ORU^R01 - Ultrasound abdomen report

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260403143000||ORU^R01^ORU_R01|CRIS20260403009|P|2.4|||AL|NE||ASCII
PID|||7345678901^^^NHS^NH~KC234567^^^RBK^MR||PATEL^RAJAN^VIKRAM||19780504|M|||55 Bermondsey Street^^London^^SE1 3XG^GBR||02071346789||||||7345678901
PV1||I|GASTRO^WARD6^BED03^KCH||||C8927890^RAHMAN^SHABANA^^^Dr^^^GMC|||||||||||NHS|667802^^^RBK^VN
ORC|RE|RAD260403006|CRIS260403006||CM
OBR|1|RAD260403006|CRIS260403006|USABD^Ultrasound Abdomen^CRIS|||20260403103000|||||||20260403104000||C8927890^RAHMAN^SHABANA^^^Dr^^^GMC|||US||||20260403143000|||F|||C4567890^BARNES^CHARLOTTE^^^Dr^^^GMC
OBX|1|TX|RAD_RPT^Radiology Report^CRIS||EXAMINATION: Ultrasound Abdomen||||||F
OBX|2|TX|RAD_RPT^Radiology Report^CRIS||CLINICAL DETAILS: Obstructive jaundice, pancreatic head mass on CT.||||||F
OBX|3|TX|RAD_RPT^Radiology Report^CRIS||FINDINGS: Intrahepatic biliary dilatation. CBD dilated to 14mm.||||||F
OBX|4|TX|RAD_RPT^Radiology Report^CRIS||Hypoechoic mass in pancreatic head measuring 32x28mm.||||||F
OBX|5|TX|RAD_RPT^Radiology Report^CRIS||No liver metastases identified. No ascites.||||||F
OBX|6|TX|RAD_RPT^Radiology Report^CRIS||IMPRESSION: Biliary obstruction secondary to pancreatic head mass. HPB MDT referral recommended.||||||F
OBX|7|TX|RAD_RPT^Radiology Report^CRIS||Reported by: Dr Charlotte Barnes, Consultant Radiologist||||||F
```

---

## 10. ORU^R01 - CT CAP staging report with embedded PDF

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260405100000||ORU^R01^ORU_R01|CRIS20260405010|P|2.4|||AL|NE||ASCII
PID|||7456789012^^^NHS^NH~KC345678^^^RBK^MR||ADEMOLA^OLUFEMI^KAYODE||19910824|M|||17 Walworth Road^^London^^SE17 1RW^GBR||02077457890||||||7456789012
PV1||O|ONCOL^CLINIC2^^KCH||||C1018901^MURPHY^CIARAN^^^Dr^^^GMC|||||||||||NHS|778901^^^RBK^VN
ORC|RE|RAD260404008|CRIS260404008||CM
OBR|1|RAD260404008|CRIS260404008|CTCAP^CT Chest Abdomen Pelvis with Contrast^CRIS|||20260404140000|||||||20260404141000||C1018901^MURPHY^CIARAN^^^Dr^^^GMC|||CT||||20260405100000|||F|||C5678901^OLADIPO^TEMITAYO^^^Dr^^^GMC
OBX|1|TX|RAD_RPT^Radiology Report^CRIS||EXAMINATION: CT Chest Abdomen Pelvis with IV Contrast||||||F
OBX|2|TX|RAD_RPT^Radiology Report^CRIS||CLINICAL DETAILS: Staging. Colorectal cancer sigmoid colon.||||||F
OBX|3|TX|RAD_RPT^Radiology Report^CRIS||FINDINGS: Irregular thickening of the sigmoid colon over 4cm segment.||||||F
OBX|4|TX|RAD_RPT^Radiology Report^CRIS||Two hepatic lesions (segments 6 and 7) measuring 18mm and 12mm, indeterminate.||||||F
OBX|5|TX|RAD_RPT^Radiology Report^CRIS||No pulmonary metastases. No lymphadenopathy above renal hilum.||||||F
OBX|6|TX|RAD_RPT^Radiology Report^CRIS||IMPRESSION: Sigmoid carcinoma. Indeterminate liver lesions - recommend MRI liver.||||||F
OBX|7|TX|RAD_RPT^Radiology Report^CRIS||Reported by: Dr Temitayo Oladipo, Consultant Radiologist||||||F
OBX|8|ED|RAD_PDF^Radiology Report PDF^CRIS||^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F
```

---

## 11. ORM^O01 - New order (X-ray lumbar spine)

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260406083000||ORM^O01^ORM_O01|CRIS20260406011|P|2.4|||AL|NE||ASCII
PID|||7567890123^^^NHS^NH~KC456789^^^RBK^MR||PETERSEN^ASTRID^INGRID||19670214|F|||92 Lordship Lane^^London^^SE22 8HF^GBR||02082568901||||||7567890123
PV1||O|RHEUM^CLINIC2^^KCH||||C3349012^HUSSAIN^NADIA^^^Dr^^^GMC|||||||||||NHS|334501^^^RBK^VN
ORC|SC|RAD260406011||CRIS260406011|SC|||||||C3349012^HUSSAIN^NADIA^^^Dr^^^GMC
OBR|1|RAD260406011|CRIS260406011|XRLSP^X-Ray Lumbar Spine AP and Lat^CRIS|||20260406083000||||||||C3349012^HUSSAIN^NADIA^^^Dr^^^GMC|||CR|||||||||1^^^20260406090000^^R
NTE|1||Chronic low back pain. RA on biologics. Exclude compression fracture.
```

---

## 12. ORU^R01 - X-ray lumbar spine report

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260406140000||ORU^R01^ORU_R01|CRIS20260406012|P|2.4|||AL|NE||ASCII
PID|||7567890123^^^NHS^NH~KC456789^^^RBK^MR||PETERSEN^ASTRID^INGRID||19670214|F|||92 Lordship Lane^^London^^SE22 8HF^GBR||02082568901||||||7567890123
PV1||O|RHEUM^CLINIC2^^KCH||||C3349012^HUSSAIN^NADIA^^^Dr^^^GMC|||||||||||NHS|334501^^^RBK^VN
ORC|RE|RAD260406011|CRIS260406011||CM
OBR|1|RAD260406011|CRIS260406011|XRLSP^X-Ray Lumbar Spine AP and Lat^CRIS|||20260406090000|||||||20260406091000||C3349012^HUSSAIN^NADIA^^^Dr^^^GMC|||CR||||20260406140000|||F|||C1234567^GUPTA^NEHA^^^Dr^^^GMC
OBX|1|TX|RAD_RPT^Radiology Report^CRIS||EXAMINATION: X-Ray Lumbar Spine AP and Lateral||||||F
OBX|2|TX|RAD_RPT^Radiology Report^CRIS||CLINICAL DETAILS: RA, chronic back pain, exclude compression fracture.||||||F
OBX|3|TX|RAD_RPT^Radiology Report^CRIS||FINDINGS: Mild loss of height of L1 vertebral body anteriorly (Grade 1 wedge).||||||F
OBX|4|TX|RAD_RPT^Radiology Report^CRIS||Degenerative disc disease L4/5 and L5/S1. Facet joint arthropathy.||||||F
OBX|5|TX|RAD_RPT^Radiology Report^CRIS||No destructive lesion. SI joints appear normal.||||||F
OBX|6|TX|RAD_RPT^Radiology Report^CRIS||IMPRESSION: Mild L1 wedge fracture (likely osteoporotic). DEXA recommended.||||||F
OBX|7|TX|RAD_RPT^Radiology Report^CRIS||Reported by: Dr Neha Gupta, Consultant Radiologist||||||F
```

---

## 13. ORM^O01 - New order (mammogram screening)

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260407090000||ORM^O01^ORM_O01|CRIS20260407013|P|2.4|||AL|NE||ASCII
PID|||7678901234^^^NHS^NH~KC567890^^^RBK^MR||MAHMOOD^SAMIRA^ZAHRA||19930410|F|||8 Denmark Hill^^London^^SE5 8BB^GBR||02073679012||||||7678901234
PV1||O|BREAST^CLINIC1^^KCH||||C6630123^STEWART^GRAEME^^^Mr^^^GMC|||||||||||NHS|445612^^^RBK^VN
ORC|SC|RAD260407013||CRIS260407013|SC|||||||C6630123^STEWART^GRAEME^^^Mr^^^GMC
OBR|1|RAD260407013|CRIS260407013|MAMMO^Bilateral Mammogram^CRIS|||20260407090000||||||||C6630123^STEWART^GRAEME^^^Mr^^^GMC|||MG|||||||||1^^^20260407100000^^R
NTE|1||Family history breast cancer (mother, age 45). Palpable lump R breast UOQ.
```

---

## 14. ORU^R01 - Mammogram report with embedded image

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260407153000||ORU^R01^ORU_R01|CRIS20260407014|P|2.4|||AL|NE||ASCII
PID|||7678901234^^^NHS^NH~KC567890^^^RBK^MR||MAHMOOD^SAMIRA^ZAHRA||19930410|F|||8 Denmark Hill^^London^^SE5 8BB^GBR||02073679012||||||7678901234
PV1||O|BREAST^CLINIC1^^KCH||||C6630123^STEWART^GRAEME^^^Mr^^^GMC|||||||||||NHS|445612^^^RBK^VN
ORC|RE|RAD260407013|CRIS260407013||CM
OBR|1|RAD260407013|CRIS260407013|MAMMO^Bilateral Mammogram^CRIS|||20260407100000|||||||20260407101000||C6630123^STEWART^GRAEME^^^Mr^^^GMC|||MG||||20260407153000|||F|||C7890123^ANDERSON^KIRSTY^^^Dr^^^GMC
OBX|1|TX|RAD_RPT^Radiology Report^CRIS||EXAMINATION: Bilateral Mammogram||||||F
OBX|2|TX|RAD_RPT^Radiology Report^CRIS||CLINICAL DETAILS: Palpable lump R breast UOQ. FH breast cancer.||||||F
OBX|3|TX|RAD_RPT^Radiology Report^CRIS||FINDINGS: Right breast: 15mm spiculated mass at 2 o'clock, 5cm from nipple.||||||F
OBX|4|TX|RAD_RPT^Radiology Report^CRIS||Associated microcalcifications. Left breast: No suspicious lesion.||||||F
OBX|5|TX|RAD_RPT^Radiology Report^CRIS||IMPRESSION: R breast suspicious mass - M5. Recommend US and core biopsy.||||||F
OBX|6|TX|RAD_RPT^Radiology Report^CRIS||Reported by: Dr Kirsty Anderson, Consultant Breast Radiologist||||||F
OBX|7|ED|MAMMO_IMG^Mammogram Key Image^CRIS||^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsMDQ4SEA0OEQ4LCxAWEBETFBUVFQwPFxgWFBgSFBT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wgARCABAAEADAREAAhEBAxEB/8QAGQAAAgMBAAAAAAAAAAAAAAAABgcEBQgD/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEAMQ||||||F
```

---

## 15. ORM^O01 - New order (DEXA scan)

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260408090000||ORM^O01^ORM_O01|CRIS20260408015|P|2.4|||AL|NE||ASCII
PID|||7567890123^^^NHS^NH~KC456789^^^RBK^MR||PETERSEN^ASTRID^INGRID||19670214|F|||92 Lordship Lane^^London^^SE22 8HF^GBR||02082568901||||||7567890123
PV1||O|RHEUM^CLINIC2^^KCH||||C3349012^HUSSAIN^NADIA^^^Dr^^^GMC|||||||||||NHS|334501^^^RBK^VN
ORC|SC|RAD260408015||CRIS260408015|SC|||||||C3349012^HUSSAIN^NADIA^^^Dr^^^GMC
OBR|1|RAD260408015|CRIS260408015|DEXA^DEXA Scan Hip and Spine^CRIS|||20260408090000||||||||C3349012^HUSSAIN^NADIA^^^Dr^^^GMC|||DX|||||||||1^^^20260408110000^^R
NTE|1||L1 wedge fracture on plain film. RA on biologics and prednisolone. Assess bone density.
```

---

## 16. ORU^R01 - DEXA scan report

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260408153000||ORU^R01^ORU_R01|CRIS20260408016|P|2.4|||AL|NE||ASCII
PID|||7567890123^^^NHS^NH~KC456789^^^RBK^MR||PETERSEN^ASTRID^INGRID||19670214|F|||92 Lordship Lane^^London^^SE22 8HF^GBR||02082568901||||||7567890123
PV1||O|RHEUM^CLINIC2^^KCH||||C3349012^HUSSAIN^NADIA^^^Dr^^^GMC|||||||||||NHS|334501^^^RBK^VN
ORC|RE|RAD260408015|CRIS260408015||CM
OBR|1|RAD260408015|CRIS260408015|DEXA^DEXA Scan Hip and Spine^CRIS|||20260408110000|||||||20260408111000||C3349012^HUSSAIN^NADIA^^^Dr^^^GMC|||DX||||20260408153000|||F|||C4567890^BARNES^CHARLOTTE^^^Dr^^^GMC
OBX|1|TX|RAD_RPT^Radiology Report^CRIS||EXAMINATION: DEXA Scan Lumbar Spine and Hip||||||F
OBX|2|TX|RAD_RPT^Radiology Report^CRIS||CLINICAL DETAILS: L1 fracture, RA, prednisolone. Assess BMD.||||||F
OBX|3|TX|RAD_RPT^Radiology Report^CRIS||FINDINGS: L2-L4 T-score: -2.8 (osteoporosis)||||||F
OBX|4|TX|RAD_RPT^Radiology Report^CRIS||Left femoral neck T-score: -2.3 (osteoporosis)||||||F
OBX|5|TX|RAD_RPT^Radiology Report^CRIS||Left total hip T-score: -1.9 (osteopenia)||||||F
OBX|6|TX|RAD_RPT^Radiology Report^CRIS||IMPRESSION: Osteoporosis at spine and femoral neck. Treatment recommended.||||||F
OBX|7|TX|RAD_RPT^Radiology Report^CRIS||Reported by: Dr Charlotte Barnes, Consultant Radiologist||||||F
```

---

## 17. ORM^O01 - Examination cancelled

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260409080000||ORM^O01^ORM_O01|CRIS20260409017|P|2.4|||AL|NE||ASCII
PID|||7012345678^^^NHS^NH~KC901234^^^RBK^MR||ACHEBE^EMEKA^CHUKWUDI||19600321|M|||73 Old Kent Road^^London^^SE1 5LQ^GBR||02072013456||||||7012345678
PV1||O|CARDIO^CLINIC1^^KCH||||C4509876^MACKAY^ALISTAIR^^^Mr^^^GMC|||||||||||NHS|112345^^^RBK^VN
ORC|CA|RAD260409017||CRIS260409017|CA
OBR|1|RAD260409017|CRIS260409017|CTCORON^CT Coronary Angiogram^CRIS|||20260409080000||||||||C4509876^MACKAY^ALISTAIR^^^Mr^^^GMC|||CT
NTE|1||Cancelled - patient unable to attend. Rebooked for 16/04/2026.
```

---

## 18. ORM^O01 - New order (MRI liver for characterisation)

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260410090000||ORM^O01^ORM_O01|CRIS20260410018|P|2.4|||AL|NE||ASCII
PID|||7456789012^^^NHS^NH~KC345678^^^RBK^MR||ADEMOLA^OLUFEMI^KAYODE||19910824|M|||17 Walworth Road^^London^^SE17 1RW^GBR||02077457890||||||7456789012
PV1||O|ONCOL^CLINIC2^^KCH||||C1018901^MURPHY^CIARAN^^^Dr^^^GMC|||||||||||NHS|778901^^^RBK^VN
ORC|SC|RAD260410018||CRIS260410018|SC|||||||C1018901^MURPHY^CIARAN^^^Dr^^^GMC
OBR|1|RAD260410018|CRIS260410018|MRILIV^MRI Liver with Primovist^CRIS|||20260410090000||||||||C1018901^MURPHY^CIARAN^^^Dr^^^GMC|||MR|||||||||1^^^20260411090000^^R
NTE|1||Colorectal MDT request. Two indeterminate liver lesions on staging CT. Characterise with Primovist.
```

---

## 19. ORU^R01 - MRI liver report with embedded PDF

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260412110000||ORU^R01^ORU_R01|CRIS20260412019|P|2.4|||AL|NE||ASCII
PID|||7456789012^^^NHS^NH~KC345678^^^RBK^MR||ADEMOLA^OLUFEMI^KAYODE||19910824|M|||17 Walworth Road^^London^^SE17 1RW^GBR||02077457890||||||7456789012
PV1||O|ONCOL^CLINIC2^^KCH||||C1018901^MURPHY^CIARAN^^^Dr^^^GMC|||||||||||NHS|778901^^^RBK^VN
ORC|RE|RAD260410018|CRIS260410018||CM
OBR|1|RAD260410018|CRIS260410018|MRILIV^MRI Liver with Primovist^CRIS|||20260411090000|||||||20260411091000||C1018901^MURPHY^CIARAN^^^Dr^^^GMC|||MR||||20260412110000|||F|||C5678901^OLADIPO^TEMITAYO^^^Dr^^^GMC
OBX|1|TX|RAD_RPT^Radiology Report^CRIS||EXAMINATION: MRI Liver with Primovist (Gadoxetate Disodium)||||||F
OBX|2|TX|RAD_RPT^Radiology Report^CRIS||CLINICAL DETAILS: Colorectal cancer. Two indeterminate liver lesions on CT.||||||F
OBX|3|TX|RAD_RPT^Radiology Report^CRIS||FINDINGS: Segment 6 lesion (18mm): Hyperintense on T2, arterial enhancement,||||||F
OBX|4|TX|RAD_RPT^Radiology Report^CRIS||hypointense on hepatobiliary phase - consistent with metastasis.||||||F
OBX|5|TX|RAD_RPT^Radiology Report^CRIS||Segment 7 lesion (12mm): Isointense on hepatobiliary phase - benign (FNH).||||||F
OBX|6|TX|RAD_RPT^Radiology Report^CRIS||IMPRESSION: Single hepatic metastasis segment 6. Segment 7 lesion benign.||||||F
OBX|7|TX|RAD_RPT^Radiology Report^CRIS||Reported by: Dr Temitayo Oladipo, Consultant Radiologist||||||F
OBX|8|ED|RAD_PDF^Radiology Report PDF^CRIS||^AP^^Base64^JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01ldGFkYXRhIDMgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbNCAwIFJdCi9Db3VudCAxCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9NZXRhZGF0YQ==||||||F
```

---

## 20. ORU^R01 - Addendum to previous report

```
MSH|^~\&|CRIS_RIS|RBK^KINGS_COLL|TIE|RBK|20260413090000||ORU^R01^ORU_R01|CRIS20260413020|P|2.4|||AL|NE||ASCII
PID|||7123456789^^^NHS^NH~KC012345^^^RBK^MR||KOWALSKA^AGNIESZKA^MARIA||19510315|F|||44 Norwood Road^^London^^SE24 9AA^GBR||02086124567||||||7123456789
PV1||I|STROKE^WARD8^BED02^KCH||||C9905678^FRASER^HAMISH^^^Dr^^^GMC|||||||||||NHS|889012^^^RBK^VN
ORC|RE|RAD260401002|CRIS260401002||CM
OBR|1|RAD260401002|CRIS260401002|CTHEAD^CT Head Non-Contrast^CRIS|||20260401113000|||||||20260401114000||C9905678^FRASER^HAMISH^^^Dr^^^GMC|||CT||||20260413090000|||C|||C2345678^OGUNYEMI^ADEBOLA^^^Dr^^^GMC
OBX|1|TX|RAD_ADD^Addendum^CRIS||ADDENDUM (13/04/2026): Follow-up review at MDT.||||||C
OBX|2|TX|RAD_ADD^Addendum^CRIS||Compared with follow-up CT 10/04/2026 (reported separately).||||||C
OBX|3|TX|RAD_ADD^Addendum^CRIS||Infarct evolution as expected. No haemorrhagic transformation confirmed.||||||C
OBX|4|TX|RAD_ADD^Addendum^CRIS||Addendum by: Dr Adebola Ogunyemi, Consultant Neuroradiologist||||||C
```
