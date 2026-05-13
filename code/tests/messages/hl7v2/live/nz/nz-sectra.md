# Sectra PACS/RIS - real HL7v2 ER7 messages

---

## 1. ORM^O01 - New radiology order for chest X-ray

```
MSH|^~\&|PAS|CMDHB|SECTRA_RIS|CMDHB|20260314091200||ORM^O01^ORM_O01|MSG00001|P|2.4|||AL|NE|NZL
PID|1||XKR4827^^^NZ^NHI||THOMSEN^AROHA^WAIATA||19850312|F|||52 Symonds Street^^Auckland^^1010^NZ||+6493091482|||M|||XKR4827
PV1|1|O|RAD^XRAY^01||||^HENARE^WIREMU^^^DR|||RAD||||||||V00012345|||||||||||||||||||||||||20260314090000
ORC|NW|ORD20260314-001|||||^^^20260314091200^^R||20260314091200|^HENARE^WIREMU^^^DR||^HENARE^WIREMU^^^DR|RAD^XRAY^01
OBR|1|ORD20260314-001||XCHEST^Chest X-ray PA^NZRC|||20260314091200||||||||^HENARE^WIREMU^^^DR||||||20260314091200|||1^^^20260314091200^^R||||^Cough persisting 3 weeks
```

---

## 2. ORM^O01 - CT abdomen order with clinical indication

```
MSH|^~\&|HOMER|WDHB|SECTRA_RIS|WDHB|20260315103000||ORM^O01^ORM_O01|MSG00002|P|2.4|||AL|NE|NZL
PID|1||PMD6519^^^NZ^NHI||WILLIAMSON^TANE^REWI||19720618|M|||38 Boundary Road^^Hamilton^^3204^NZ||+6478384516|||M|||PMD6519
PV1|1|I|GEN^WARD5^12||||^PATELIYA^ANITA^^^DR|||GEN||||||||V00023456|||||||||||||||||||||||||20260315080000
ORC|NW|ORD20260315-002|||||^^^20260315110000^^R||20260315103000|^PATELIYA^ANITA^^^DR||^PATELIYA^ANITA^^^DR|RAD^CT^01
OBR|1|ORD20260315-002||CTABD^CT Abdomen with contrast^NZRC|||20260315103000||||||||^PATELIYA^ANITA^^^DR||||||20260315110000|||1^^^20260315110000^^R||||^Acute abdominal pain RLQ, query appendicitis
```

---

## 3. ORU^R01 - Radiology report for chest X-ray

```
MSH|^~\&|SECTRA_RIS|CMDHB|PAS|CMDHB|20260314143000||ORU^R01^ORU_R01|MSG00003|P|2.4|||AL|NE|NZL
PID|1||XKR4827^^^NZ^NHI||THOMSEN^AROHA^WAIATA||19850312|F|||52 Symonds Street^^Auckland^^1010^NZ||+6493091482|||M|||XKR4827
PV1|1|O|RAD^XRAY^01||||^HENARE^WIREMU^^^DR|||RAD||||||||V00012345|||||||||||||||||||||||||20260314090000
ORC|RE|ORD20260314-001||FIL20260314-001||||20260314143000
OBR|1|ORD20260314-001|FIL20260314-001|XCHEST^Chest X-ray PA^NZRC|||20260314091200|||||||||^HENARE^WIREMU^^^DR|||||20260314143000|||F
OBX|1|FT|GDT^Radiology Report^NZRC||Chest X-ray PA\.br\\.br\Clinical indication: Cough persisting 3 weeks\.br\\.br\Findings: Heart size is normal. Lungs are clear with no focal consolidation, pleural effusion, or pneumothorax. Mediastinal contours are unremarkable. No bony abnormality identified.\.br\\.br\Impression: Normal chest X-ray.||||||F|||20260314142500||^MCKAY^SARAH^^^DR
```

---

## 4. ORU^R01 - CT abdomen radiology report with findings

```
MSH|^~\&|SECTRA_RIS|WDHB|HOMER|WDHB|20260315161500||ORU^R01^ORU_R01|MSG00004|P|2.4|||AL|NE|NZL
PID|1||PMD6519^^^NZ^NHI||WILLIAMSON^TANE^REWI||19720618|M|||38 Boundary Road^^Hamilton^^3204^NZ||+6478384516|||M|||PMD6519
PV1|1|I|GEN^WARD5^12||||^PATELIYA^ANITA^^^DR|||GEN||||||||V00023456|||||||||||||||||||||||||20260315080000
ORC|RE|ORD20260315-002||FIL20260315-002||||20260315161500
OBR|1|ORD20260315-002|FIL20260315-002|CTABD^CT Abdomen with contrast^NZRC|||20260315110000|||||||||^PATELIYA^ANITA^^^DR|||||20260315161500|||F
OBX|1|FT|GDT^Radiology Report^NZRC||CT Abdomen and Pelvis with IV contrast\.br\\.br\Clinical indication: Acute abdominal pain RLQ, query appendicitis\.br\\.br\Technique: Helical CT of the abdomen and pelvis performed following 100ml IV Omnipaque 350.\.br\\.br\Findings: The appendix measures 12mm in diameter with periappendiceal fat stranding and a 5mm appendicolith at the base. There is no free fluid or abscess formation. Liver, spleen, pancreas, adrenals, and kidneys are unremarkable. No lymphadenopathy.\.br\\.br\Impression: Acute appendicitis with appendicolith. No complication.||||||F|||20260315161000||^NGUYEN^DAVINDER^^^DR
```

---

## 5. ADT^A01 - Patient admission for radiology inpatient procedure

```
MSH|^~\&|PAS|CCDHB|SECTRA_RIS|CCDHB|20260316070000||ADT^A01^ADT_A01|MSG00005|P|2.4|||AL|NE|NZL
EVN|A01|20260316070000
PID|1||CFL9027^^^NZ^NHI||SMITHSON^EMMA^CHARLOTTE||19650724|F|||62 Tinakori Road^^Wellington^^6011^NZ||+6443854218|||W|||CFL9027
NK1|1|SMITHSON^JONATHAN^EDGAR||+6444729183||NOK
PV1|1|I|RAD^IR^03||||^CHEN^LILIAN^^^DR|||RAD||||||||V00034567|||||||||||||||||||||||||20260316070000
```

---

## 6. ADT^A03 - Patient discharge after interventional radiology

```
MSH|^~\&|PAS|CCDHB|SECTRA_RIS|CCDHB|20260316153000||ADT^A03^ADT_A03|MSG00006|P|2.4|||AL|NE|NZL
EVN|A03|20260316153000
PID|1||CFL9027^^^NZ^NHI||SMITHSON^EMMA^CHARLOTTE||19650724|F|||62 Tinakori Road^^Wellington^^6011^NZ||+6443854218|||W|||CFL9027
PV1|1|I|RAD^IR^03||||^CHEN^LILIAN^^^DR|||RAD||||||||V00034567|||||||||||||||||||||||||20260316070000|||||||20260316153000
```

---

## 7. SIU^S12 - New radiology appointment scheduled for MRI brain

```
MSH|^~\&|SECTRA_RIS|CDHB|PAS|CDHB|20260317080000||SIU^S12^SIU_S12|MSG00007|P|2.5|||AL|NE|NZL
SCH|SCH20260317-001|||||MRI^MRI Brain^NZRC|ROUTINE|30|MIN|^^30^20260318090000^20260318093000|||||^JONSSON^KAREN^^^DR|+6433641287|RAD^MRI^01|RAD^MRI^01|||BOOKED
PID|1||DSE3478^^^NZ^NHI||HARAWIRA^MAIA^TE RINA||19900215|F|||74 Cashel Street^^Christchurch^^8011^NZ||+6433641287|||S|||DSE3478
PV1|1|O|RAD^MRI^01||||^JONSSON^KAREN^^^DR|||RAD
RGS|1
AIS|1||MRI^MRI Brain^NZRC|20260318090000|30|MIN
AIG|1||^WALSH^PETER^^^DR|RAD
AIL|1||RAD^MRI^01^^MRI Suite 1
```

---

## 8. SIU^S14 - Radiology appointment modification

```
MSH|^~\&|SECTRA_RIS|CDHB|PAS|CDHB|20260317143000||SIU^S14^SIU_S14|MSG00008|P|2.5|||AL|NE|NZL
SCH|SCH20260317-001|||||MRI^MRI Brain^NZRC|ROUTINE|30|MIN|^^30^20260319100000^20260319103000|||||^JONSSON^KAREN^^^DR|+6433641287|RAD^MRI^01|RAD^MRI^01|||BOOKED
PID|1||DSE3478^^^NZ^NHI||HARAWIRA^MAIA^TE RINA||19900215|F|||74 Cashel Street^^Christchurch^^8011^NZ||+6433641287|||S|||DSE3478
PV1|1|O|RAD^MRI^01||||^JONSSON^KAREN^^^DR|||RAD
RGS|1
AIS|1||MRI^MRI Brain^NZRC|20260319100000|30|MIN
AIG|1||^WALSH^PETER^^^DR|RAD
AIL|1||RAD^MRI^01^^MRI Suite 1
```

---

## 9. SIU^S15 - Radiology appointment cancellation

```
MSH|^~\&|SECTRA_RIS|ADHB|PAS|ADHB|20260318110000||SIU^S15^SIU_S15|MSG00009|P|2.5|||AL|NE|NZL
SCH|SCH20260318-001|||||US^Ultrasound Abdomen^NZRC|ROUTINE|20|MIN|^^20^20260319140000^20260319142000|||||^BRENNAN^RACHEL^^^DR|+6493074982|RAD^US^01|RAD^US^01|||CANCELLED
PID|1||GHN5821^^^NZ^NHI||MAHUTA^RANGI^HONE||19480503|M|||29 Quay Street^^Auckland^^1010^NZ||+6493074982|||W|||GHN5821
PV1|1|O|RAD^US^01||||^BRENNAN^RACHEL^^^DR|||RAD
RGS|1
AIS|1||US^Ultrasound Abdomen^NZRC|20260319140000|20|MIN
```

---

## 10. ORM^O01 - Urgent MRI spine order

```
MSH|^~\&|PAS|SDHB|SECTRA_RIS|SDHB|20260319073000||ORM^O01^ORM_O01|MSG00010|P|2.4|||AL|NE|NZL
PID|1||LRX2087^^^NZ^NHI||MITCHELLSON^JAMES^REUBEN||19580911|M|||63 Tay Street^^Invercargill^^9810^NZ||+6432148914|||M|||LRX2087
PV1|1|E|ED^MAIN^01||||^KAHU^MEREANA^^^DR|||ED||||||||V00045678|||||||||||||||||||||||||20260319070000
ORC|NW|ORD20260319-003|||||^^^20260319080000^^S||20260319073000|^KAHU^MEREANA^^^DR||^KAHU^MEREANA^^^DR|RAD^MRI^01
OBR|1|ORD20260319-003||MRILSP^MRI Lumbar Spine^NZRC|||20260319073000||||||||^KAHU^MEREANA^^^DR||||||20260319080000|||1^^^20260319080000^^S||||^Acute onset bilateral lower limb weakness and urinary retention, query cauda equina syndrome
```

---

## 11. ORU^R01 - MRI brain report with findings

```
MSH|^~\&|SECTRA_RIS|CDHB|PAS|CDHB|20260319152000||ORU^R01^ORU_R01|MSG00011|P|2.4|||AL|NE|NZL
PID|1||DSE3478^^^NZ^NHI||HARAWIRA^MAIA^TE RINA||19900215|F|||74 Cashel Street^^Christchurch^^8011^NZ||+6433641287|||S|||DSE3478
PV1|1|O|RAD^MRI^01||||^JONSSON^KAREN^^^DR|||RAD
ORC|RE|ORD20260319-004||FIL20260319-004||||20260319152000
OBR|1|ORD20260319-004|FIL20260319-004|MRI^MRI Brain^NZRC|||20260319100000|||||||||^JONSSON^KAREN^^^DR|||||20260319152000|||F
OBX|1|FT|GDT^Radiology Report^NZRC||MRI Brain without and with gadolinium\.br\\.br\Clinical indication: Recurrent headaches with visual disturbance\.br\\.br\Technique: Multiplanar multisequence MRI of the brain performed before and after IV gadolinium.\.br\\.br\Findings: No intracranial mass lesion. Ventricles and sulci are normal in size and configuration. No acute infarct on diffusion-weighted imaging. No abnormal enhancement following gadolinium. White matter signal is normal. Pituitary gland is normal. Posterior fossa structures are unremarkable.\.br\\.br\Impression: Normal MRI brain.||||||F|||20260319151500||^WALSH^PETER^^^DR
```

---

## 12. ORM^O01 - Mammography screening order

```
MSH|^~\&|BSTNZ|BSTNZ|SECTRA_RIS|WDHB|20260320091500||ORM^O01^ORM_O01|MSG00012|P|2.4|||AL|NE|NZL
PID|1||TBR1064^^^NZ^NHI||REEDHAM^SARAH^JANNE||19710403|F|||58 River Road^^Hamilton^^3216^NZ||+6478393584|||M|||TBR1064
PV1|1|O|RAD^MAMMO^01||||^TAITUHA^LOUISE^^^DR|||RAD||||||||V00056789|||||||||||||||||||||||||20260320091500
ORC|NW|ORD20260320-005|||||^^^20260320100000^^R||20260320091500|^TAITUHA^LOUISE^^^DR||^TAITUHA^LOUISE^^^DR|RAD^MAMMO^01
OBR|1|ORD20260320-005||MAMMO^Bilateral Mammography^NZRC|||20260320091500||||||||^TAITUHA^LOUISE^^^DR||||||20260320100000|||1^^^20260320100000^^R||||^Routine BreastScreen NZ screening, no symptoms
```

---

## 13. ORU^R01 - Radiology report with embedded JPEG chest X-ray image

```
MSH|^~\&|SECTRA_PACS|ADHB|EMR|ADHB|20260321100000||ORU^R01^ORU_R01|MSG00013|P|2.5|||AL|NE|NZL
PID|1||VKB6172^^^NZ^NHI||WIREMU^HEMI^TAMATI||19800127|M|||45 Jervois Road^^Auckland^^1011^NZ||+6493781482|||M|||VKB6172
PV1|1|O|RAD^XRAY^01||||^BRENNAN^RACHEL^^^DR|||RAD
ORC|RE|ORD20260321-006||FIL20260321-006||||20260321100000
OBR|1|ORD20260321-006|FIL20260321-006|XCHEST^Chest X-ray PA^NZRC|||20260321083000|||||||||^BRENNAN^RACHEL^^^DR|||||20260321100000|||F
OBX|1|FT|GDT^Radiology Report^NZRC||Chest X-ray PA\.br\\.br\Findings: Cardiomegaly with cardiothoracic ratio 0.58. Bilateral small pleural effusions. Upper lobe pulmonary venous distension. Kerley B lines present. No focal consolidation.\.br\\.br\Impression: Congestive cardiac failure.||||||F|||20260321095500||^MCKAY^SARAH^^^DR
OBX|2|ED|IMG^Chest Xray^LN||^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAFBABAAAAAAAAAAAAAAAAAAAACf/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKoA/9k=||||||F
```

---

## 14. ORU^R01 - Radiology report with embedded TIFF ultrasound image

```
MSH|^~\&|SECTRA_PACS|BOPDHB|EMR|BOPDHB|20260322141500||ORU^R01^ORU_R01|MSG00014|P|2.5|||AL|NE|NZL
PID|1||SBR8159^^^NZ^NHI||NGATAI^AROHA^MERE||19670830|F|||83 Eleventh Avenue^^Tauranga^^3110^NZ||+6475788214|||W|||SBR8159
PV1|1|O|RAD^US^01||||^TAITUHA^LOUISE^^^DR|||RAD
ORC|RE|ORD20260322-007||FIL20260322-007||||20260322141500
OBR|1|ORD20260322-007|FIL20260322-007|USABD^Ultrasound Abdomen^NZRC|||20260322120000|||||||||^TAITUHA^LOUISE^^^DR|||||20260322141500|||F
OBX|1|FT|GDT^Radiology Report^NZRC||Ultrasound Abdomen\.br\\.br\Clinical indication: RUQ pain, query gallstones\.br\\.br\Findings: The gallbladder contains multiple echogenic foci with posterior acoustic shadowing consistent with gallstones. The largest measures 14mm. No gallbladder wall thickening or pericholecystic fluid. Common bile duct measures 4mm. Liver is normal in echotexture and size. No intrahepatic ductal dilatation. Pancreas, spleen, and kidneys are unremarkable.\.br\\.br\Impression: Cholelithiasis without cholecystitis.||||||F|||20260322141000||^KAPOOR^PRIYA^^^DR
OBX|2|ED|IMG^Ultrasound Abdomen^LN||^image^tiff^Base64^SUkqAAgAAAAIAAABAwABAAAAEAAAAAEBAwABAAAAEAAAABIBAwABAAAAAQAAABoBBQABAAAAcgAAABsBBQABAAAAegAAABwBAwABAAAAAQAAACgBAwABAAAAAgAAAAAAAABIAAAA||||||F
```

---

## 15. ADT^A04 - Patient registration for outpatient radiology

```
MSH|^~\&|PAS|NMDHB|SECTRA_RIS|NMDHB|20260323081000||ADT^A04^ADT_A04|MSG00015|P|2.4|||AL|NE|NZL
EVN|A04|20260323081000
PID|1||KFA2647^^^NZ^NHI||KAURI^MATIU^HONE||19950817|M|||62 Hampden Street^^Nelson^^7010^NZ||+6435468912|||S|||KFA2647
PV1|1|O|RAD^CT^01||||^CHEN^LILIAN^^^DR|||RAD||||||||V00067890|||||||||||||||||||||||||20260323081000
```

---

## 16. ADT^A08 - Patient information update for radiology patient

```
MSH|^~\&|PAS|CMDHB|SECTRA_RIS|CMDHB|20260323103000||ADT^A08^ADT_A08|MSG00016|P|2.4|||AL|NE|NZL
EVN|A08|20260323103000
PID|1||XKR4827^^^NZ^NHI||THOMSEN^AROHA^WAIATA||19850312|F|||128 Mahia Road^^Manukau^^2104^NZ||+6492625183|||M|||XKR4827
PV1|1|O|RAD^XRAY^01||||^HENARE^WIREMU^^^DR|||RAD
```

---

## 17. ORM^O01 - Ultrasound-guided biopsy order

```
MSH|^~\&|PAS|CDHB|SECTRA_RIS|CDHB|20260324094500||ORM^O01^ORM_O01|MSG00017|P|2.4|||AL|NE|NZL
PID|1||QSL7290^^^NZ^NHI||ANDERSEN^LAURA^CHARLOTTE||19831201|F|||52 Wharenui Road^^Christchurch^^8041^NZ||+6433641187|||M|||QSL7290
PV1|1|O|RAD^US^02||||^KAPOOR^PRIYA^^^DR|||RAD||||||||V00078901|||||||||||||||||||||||||20260324094500
ORC|NW|ORD20260324-008|||||^^^20260324110000^^R||20260324094500|^KAPOOR^PRIYA^^^DR||^KAPOOR^PRIYA^^^DR|RAD^US^02
OBR|1|ORD20260324-008||USBX^Ultrasound Guided Biopsy Thyroid^NZRC|||20260324094500||||||||^KAPOOR^PRIYA^^^DR||||||20260324110000|||1^^^20260324110000^^R||||^1.8cm hypoechoic thyroid nodule on prior imaging, TI-RADS 4
```

---

## 18. ORU^R01 - Preliminary radiology report (MRI lumbar spine)

```
MSH|^~\&|SECTRA_RIS|SDHB|PAS|SDHB|20260319094500||ORU^R01^ORU_R01|MSG00018|P|2.4|||AL|NE|NZL
PID|1||LRX2087^^^NZ^NHI||MITCHELLSON^JAMES^REUBEN||19580911|M|||63 Tay Street^^Invercargill^^9810^NZ||+6432148914|||M|||LRX2087
PV1|1|E|ED^MAIN^01||||^KAHU^MEREANA^^^DR|||ED
ORC|RE|ORD20260319-003||FIL20260319-003||||20260319094500
OBR|1|ORD20260319-003|FIL20260319-003|MRILSP^MRI Lumbar Spine^NZRC|||20260319080000|||||||||^KAHU^MEREANA^^^DR|||||20260319094500|||P
OBX|1|FT|GDT^Radiology Report^NZRC||PRELIMINARY REPORT\.br\\.br\MRI Lumbar Spine\.br\\.br\Clinical indication: Acute onset bilateral lower limb weakness and urinary retention, query cauda equina syndrome\.br\\.br\Findings: Large central disc extrusion at L4/L5 measuring 18mm AP causing severe compression of the cauda equina nerve roots. Significant narrowing of the central canal. The conus medullaris terminates at L1 and is normal in signal. No abnormal enhancement.\.br\\.br\Impression: Large L4/L5 central disc extrusion with cauda equina compression. Urgent neurosurgical review recommended.||||||P|||20260319094000||^NGUYEN^DAVINDER^^^DR
```

---

## 19. ORM^O01 - Radiology order cancellation

```
MSH|^~\&|PAS|ADHB|SECTRA_RIS|ADHB|20260325111500||ORM^O01^ORM_O01|MSG00019|P|2.4|||AL|NE|NZL
PID|1||YHQ4926^^^NZ^NHI||TUPAEA^NIKAU^TAMATI||19791005|M|||74 Sandringham Road^^Auckland^^1024^NZ||+6496311284|||M|||YHQ4926
PV1|1|O|RAD^CT^01||||^HENARE^WIREMU^^^DR|||RAD||||||||V00089012|||||||||||||||||||||||||20260325100000
ORC|CA|ORD20260325-009|||||^^^20260325120000^^R||20260325111500|^HENARE^WIREMU^^^DR||^HENARE^WIREMU^^^DR|RAD^CT^01
OBR|1|ORD20260325-009||CTCHEST^CT Chest^NZRC|||20260325100000||||||||^HENARE^WIREMU^^^DR||||||20260325120000|||1^^^20260325120000^^R||||^Cancelled - clinical improvement, CT no longer indicated
```

---

## 20. ADT^A02 - Patient transfer to radiology department

```
MSH|^~\&|PAS|HVDHB|SECTRA_RIS|HVDHB|20260326083000||ADT^A02^ADT_A02|MSG00020|P|2.4|||AL|NE|NZL
EVN|A02|20260326083000
PID|1||DJV5803^^^NZ^NHI||RAMIREZ^ISABELA^ROSANA||19880614|F|||27 Russell Street^^Palmerston North^^4410^NZ||+6463508914|||M|||DJV5803
PV1|1|I|RAD^CT^01||||^WALSH^PETER^^^DR|||RAD||||||||V00090123|||||||||||||||||||||||||20260325200000
PV2|||^Transfer for urgent CT head from Surgical Ward
```
