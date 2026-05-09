# eRAD RIS - real HL7v2 ER7 messages

---

## 1. ORM^O01 - CT head order

```
MSH|^~\&|CHAMELEON|SHEBA_MC|ERAD_RIS|SHEBA_RAD|20260301090000||ORM^O01|ERD000001|P|2.4
PID|||427581936^^^IL_MOH^NI||Elbaz^Ronen^Itai^^Mr.||19810223|M|||HaPalmach 7^^Tel Aviv^^6291435^IL||^PRN^CP^052-419-6738
PV1||E|ED^001^^SHEBA||||30912^Aweiss^Dalia^^^Dr.||||||||||||VN10001
ORC|NW|ORD3001^CHAMELEON|||||^^^20260301090000^^S
OBR|1|ORD3001^CHAMELEON||70450^CT Head without Contrast^CPT|||20260301085000||||A|||HEAD|30912^Aweiss^Dalia^^^Dr.||||||||||^^^20260301090000
```

---

## 2. ORM^O01 - chest X-ray order

```
MSH|^~\&|CHAMELEON|HADASSAH_MC|ERAD_RIS|HADASSAH_RAD|20260302080000||ORM^O01|ERD000002|P|2.4
PID|||658174293^^^IL_MOH^NI||Grinberg^Leonid^Arkadi^^Mr.||19620515|M|||Emek Refaim 24^^Jerusalem^^9314107^IL||^PRN^CP^054-217-8463
PV1||I|MED^201^A^HADASSAH||||50129^Tamir^Yael^^^Dr.||||||||||||VN20002
ORC|NW|ORD3002^CHAMELEON|||||^^^20260302080000^^R
OBR|1|ORD3002^CHAMELEON||71020^Chest X-Ray PA and Lateral^CPT|||20260302073000||||A|||CHEST|50129^Tamir^Yael^^^Dr.
```

---

## 3. ORU^R01 - CT head report

```
MSH|^~\&|ERAD_RIS|SHEBA_RAD|CHAMELEON|SHEBA_MC|20260301120000||ORU^R01|ERD000003|P|2.4
PID|||427581936^^^IL_MOH^NI||Elbaz^Ronen^Itai^^Mr.||19810223|M|||HaPalmach 7^^Tel Aviv^^6291435^IL||^PRN^CP^052-419-6738
PV1||E|ED^001^^SHEBA||||30912^Aweiss^Dalia^^^Dr.||||||||||||VN10001
ORC|RE|ORD3001^CHAMELEON|RES3001^ERAD_RIS
OBR|1|ORD3001^CHAMELEON|RES3001^ERAD_RIS|70450^CT Head without Contrast^CPT|||20260301085000|||||||||30912^Aweiss^Dalia^^^Dr.||RAD10001||||||F
OBX|1|FT|70450^CT Head Report^CPT||CT Head without Contrast\.br\Clinical indication: Headache, rule out CVA\.br\Technique: Axial images through the brain\.br\Findings: No acute intracranial hemorrhage\.br\No mass effect or midline shift\.br\Ventricles and sulci are normal\.br\Impression: Normal CT head||||||F
```

---

## 4. ORU^R01 - chest X-ray report

```
MSH|^~\&|ERAD_RIS|HADASSAH_RAD|CHAMELEON|HADASSAH_MC|20260302110000||ORU^R01|ERD000004|P|2.4
PID|||658174293^^^IL_MOH^NI||Grinberg^Leonid^Arkadi^^Mr.||19620515|M|||Emek Refaim 24^^Jerusalem^^9314107^IL||^PRN^CP^054-217-8463
PV1||I|MED^201^A^HADASSAH||||50129^Tamir^Yael^^^Dr.||||||||||||VN20002
ORC|RE|ORD3002^CHAMELEON|RES3002^ERAD_RIS
OBR|1|ORD3002^CHAMELEON|RES3002^ERAD_RIS|71020^Chest X-Ray PA and Lateral^CPT|||20260302073000|||||||||50129^Tamir^Yael^^^Dr.||RAD10002||||||F
OBX|1|FT|71020^Chest X-Ray Report^CPT||PA and Lateral Chest Radiograph\.br\Clinical indication: Cough, dyspnea\.br\Findings: Right lower lobe opacity consistent with pneumonia\.br\Small right pleural effusion\.br\Heart size is upper limits of normal\.br\No pneumothorax\.br\Impression: Right lower lobe pneumonia with small pleural effusion||||||F
```

---

## 5. ORM^O01 - MRI brain order

```
MSH|^~\&|CHAMELEON|RAMBAM_MC|ERAD_RIS|RAMBAM_RAD|20260303090000||ORM^O01|ERD000005|P|2.4
PID|||791536248^^^IL_MOH^NI||Jabarin^Laila^Amira^^Mrs.||19880921|F|||HaGalil 18^^Nazareth^^1610203^IL||^PRN^CP^050-836-1294
PV1||I|NEURO^600^A^RAMBAM||||10478^Zilber^Amos^^^Dr.||||||||||||VN30003
ORC|NW|ORD3003^CHAMELEON|||||^^^20260303090000^^R
OBR|1|ORD3003^CHAMELEON||70553^MRI Brain with and without Contrast^CPT|||20260303083000||||A|||BRAIN|10478^Zilber^Amos^^^Dr.
```

---

## 6. ORU^R01 - MRI brain report

```
MSH|^~\&|ERAD_RIS|RAMBAM_RAD|CHAMELEON|RAMBAM_MC|20260303150000||ORU^R01|ERD000006|P|2.4
PID|||791536248^^^IL_MOH^NI||Jabarin^Laila^Amira^^Mrs.||19880921|F|||HaGalil 18^^Nazareth^^1610203^IL||^PRN^CP^050-836-1294
PV1||I|NEURO^600^A^RAMBAM||||10478^Zilber^Amos^^^Dr.||||||||||||VN30003
ORC|RE|ORD3003^CHAMELEON|RES3003^ERAD_RIS
OBR|1|ORD3003^CHAMELEON|RES3003^ERAD_RIS|70553^MRI Brain with and without Contrast^CPT|||20260303083000|||||||||10478^Zilber^Amos^^^Dr.||RAD10003||||||F
OBX|1|FT|70553^MRI Brain Report^CPT||MRI Brain with and without Gadolinium\.br\Clinical indication: Seizures, rule out mass\.br\Technique: Multiplanar multisequence imaging\.br\Findings: 2.3 cm enhancing lesion in right temporal lobe\.br\Surrounding vasogenic edema\.br\No midline shift\.br\Impression: Right temporal lobe mass, recommend biopsy||||||F
```

---

## 7. ORM^O01 - abdominal ultrasound order

```
MSH|^~\&|CHAMELEON|ICHILOV_MC|ERAD_RIS|ICHILOV_RAD|20260304090000||ORM^O01|ERD000007|P|2.4
PID|||384917562^^^IL_MOH^NI||Shriki^Itzik^Moshe^^Mr.||19570404|M|||Yafo 28^^Jerusalem^^9426541^IL||^PRN^PH^02-538-4167
PV1||O|GASTRO^110^^ICHILOV||||40783^Levy^Shiri^^^Dr.||||||||||||VN40004
ORC|NW|ORD3004^CHAMELEON|||||^^^20260304090000^^R
OBR|1|ORD3004^CHAMELEON||76700^Abdominal Ultrasound Complete^CPT|||20260304083000||||A|||ABD|40783^Levy^Shiri^^^Dr.
```

---

## 8. ORU^R01 - abdominal ultrasound report with embedded image (base64 ED)

```
MSH|^~\&|ERAD_RIS|ICHILOV_RAD|CHAMELEON|ICHILOV_MC|20260304120000||ORU^R01|ERD000008|P|2.4
PID|||384917562^^^IL_MOH^NI||Shriki^Itzik^Moshe^^Mr.||19570404|M|||Yafo 28^^Jerusalem^^9426541^IL||^PRN^PH^02-538-4167
PV1||O|GASTRO^110^^ICHILOV||||40783^Levy^Shiri^^^Dr.||||||||||||VN40004
ORC|RE|ORD3004^CHAMELEON|RES3004^ERAD_RIS
OBR|1|ORD3004^CHAMELEON|RES3004^ERAD_RIS|76700^Abdominal Ultrasound Complete^CPT|||20260304083000|||||||||40783^Levy^Shiri^^^Dr.||RAD10004||||||F
OBX|1|FT|76700^Abdominal US Report^CPT||Abdominal Ultrasound Complete\.br\Clinical indication: RUQ pain\.br\Liver: Normal size and echogenicity\.br\Gallbladder: Multiple stones, largest 1.2 cm\.br\Wall thickening noted at 4mm\.br\CBD: Normal caliber at 5mm\.br\Impression: Cholelithiasis with wall thickening, correlate clinically||||||F
OBX|2|ED|IMG^Ultrasound Key Image^L||^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AKwA//9k=||||||F
```

---

## 9. ORM^O01 - mammography order

```
MSH|^~\&|CHAMELEON|ASSUTA_MC|ERAD_RIS|ASSUTA_RAD|20260305090000||ORM^O01|ERD000009|P|2.4
PID|||826541937^^^IL_MOH^NI||Sorokina^Yelena^Irina^^Mrs.||19850128|F|||Bialik 19^^Rishon LeZion^^7546301^IL||^PRN^CP^058-441-6293
PV1||O|RAD^100^^ASSUTA||||70125^Nachmias^Ofer^^^Dr.||||||||||||VN50005
ORC|NW|ORD3005^CHAMELEON|||||^^^20260305090000^^R
OBR|1|ORD3005^CHAMELEON||77067^Screening Mammography Bilateral^CPT|||20260305083000||||A|||BREAST|70125^Nachmias^Ofer^^^Dr.
```

---

## 10. ORU^R01 - mammography report with embedded PDF (base64 ED)

```
MSH|^~\&|ERAD_RIS|ASSUTA_RAD|CHAMELEON|ASSUTA_MC|20260305140000||ORU^R01|ERD000010|P|2.4
PID|||826541937^^^IL_MOH^NI||Sorokina^Yelena^Irina^^Mrs.||19850128|F|||Bialik 19^^Rishon LeZion^^7546301^IL||^PRN^CP^058-441-6293
PV1||O|RAD^100^^ASSUTA||||70125^Nachmias^Ofer^^^Dr.||||||||||||VN50005
ORC|RE|ORD3005^CHAMELEON|RES3005^ERAD_RIS
OBR|1|ORD3005^CHAMELEON|RES3005^ERAD_RIS|77067^Screening Mammography Bilateral^CPT|||20260305083000|||||||||70125^Nachmias^Ofer^^^Dr.||RAD10005||||||F
OBX|1|FT|77067^Mammography Report^CPT||Screening Mammography Bilateral\.br\BI-RADS Category: 1 - Negative\.br\Breast composition: Heterogeneously dense\.br\No suspicious masses or calcifications\.br\No architectural distortion\.br\Impression: Normal screening mammography||||||F
OBX|2|ED|PDF^Mammography Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvUmVzb3VyY2VzIDw8ID4+ID4+CmVuZG9iagp4cmVmCjAgNAowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNCAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMjE2CiUlRU9GCg==||||||F
```

---

## 11. ORM^O01 - CT abdomen/pelvis order

```
MSH|^~\&|CHAMELEON|BEILINSON_MC|ERAD_RIS|BEILINSON_RAD|20260306090000||ORM^O01|ERD000011|P|2.4
PID|||312594786^^^IL_MOH^NI||Darawshe^Khaled^Fares^^Mr.||19730711|M|||Ben Zvi 12^^Acre^^2412304^IL||^PRN^CP^052-603-8174
PV1||E|ED^001^^BEILINSON||||22718^Rosenfeld^Maya^^^Dr.||||||||||||VN60006
ORC|NW|ORD3006^CHAMELEON|||||^^^20260306090000^^S
OBR|1|ORD3006^CHAMELEON||74178^CT Abdomen and Pelvis with Contrast^CPT|||20260306083000||||A|||ABD|22718^Rosenfeld^Maya^^^Dr.
```

---

## 12. ORU^R01 - CT abdomen/pelvis report

```
MSH|^~\&|ERAD_RIS|BEILINSON_RAD|CHAMELEON|BEILINSON_MC|20260306140000||ORU^R01|ERD000012|P|2.4
PID|||312594786^^^IL_MOH^NI||Darawshe^Khaled^Fares^^Mr.||19730711|M|||Ben Zvi 12^^Acre^^2412304^IL||^PRN^CP^052-603-8174
PV1||E|ED^001^^BEILINSON||||22718^Rosenfeld^Maya^^^Dr.||||||||||||VN60006
ORC|RE|ORD3006^CHAMELEON|RES3006^ERAD_RIS
OBR|1|ORD3006^CHAMELEON|RES3006^ERAD_RIS|74178^CT Abdomen and Pelvis with Contrast^CPT|||20260306083000|||||||||22718^Rosenfeld^Maya^^^Dr.||RAD10006||||||F
OBX|1|FT|74178^CT Abd/Pelvis Report^CPT||CT Abdomen and Pelvis with IV Contrast\.br\Clinical indication: Acute abdominal pain\.br\Findings: Dilated appendix measuring 12mm\.br\Periappendiceal fat stranding\.br\Small amount of free fluid in the pelvis\.br\No free air\.br\Impression: Acute appendicitis||||||F
```

---

## 13. ORM^O01 - spine X-ray order

```
MSH|^~\&|CHAMELEON|SOROKA_MC|ERAD_RIS|SOROKA_RAD|20260307090000||ORM^O01|ERD000013|P|2.4
PID|||749182364^^^IL_MOH^NI||Worku^Tigist^Saron^^Mrs.||19790505|F|||Hatikva 15^^Be'er Sheva^^8425412^IL||^PRN^CP^050-271-5843
PV1||O|ORTH^601^^SOROKA||||60453^Azaria^Nir^^^Dr.||||||||||||VN70007
ORC|NW|ORD3007^CHAMELEON|||||^^^20260307090000^^R
OBR|1|ORD3007^CHAMELEON||72100^Lumbar Spine X-Ray AP and Lateral^CPT|||20260307083000||||A|||LSPINE|60453^Azaria^Nir^^^Dr.
```

---

## 14. ORU^R01 - spine X-ray report

```
MSH|^~\&|ERAD_RIS|SOROKA_RAD|CHAMELEON|SOROKA_MC|20260307120000||ORU^R01|ERD000014|P|2.4
PID|||749182364^^^IL_MOH^NI||Worku^Tigist^Saron^^Mrs.||19790505|F|||Hatikva 15^^Be'er Sheva^^8425412^IL||^PRN^CP^050-271-5843
PV1||O|ORTH^601^^SOROKA||||60453^Azaria^Nir^^^Dr.||||||||||||VN70007
ORC|RE|ORD3007^CHAMELEON|RES3007^ERAD_RIS
OBR|1|ORD3007^CHAMELEON|RES3007^ERAD_RIS|72100^Lumbar Spine X-Ray AP and Lateral^CPT|||20260307083000|||||||||60453^Azaria^Nir^^^Dr.||RAD10007||||||F
OBX|1|FT|72100^L-Spine X-Ray Report^CPT||Lumbar Spine AP and Lateral\.br\Clinical indication: Low back pain\.br\Findings: Moderate disc space narrowing at L4-L5\.br\Osteophyte formation at L3-L4 and L4-L5\.br\Alignment is maintained\.br\No fracture or listhesis\.br\Impression: Degenerative disc disease, most prominent at L4-L5||||||F
```

---

## 15. ORM^O01 - nuclear medicine bone scan order

```
MSH|^~\&|CHAMELEON|WOLFSON_MC|ERAD_RIS|WOLFSON_RAD|20260308090000||ORM^O01|ERD000015|P|2.4
PID|||531782946^^^IL_MOH^NI||Kantor^Shimon^Avi^^Mr.||19680213|M|||Sokolov 41^^Petah Tikva^^4924518^IL||^PRN^CP^054-833-6271
PV1||O|ONCO^700^^WOLFSON||||80614^Shalom^Dikla^^^Dr.||||||||||||VN80008
ORC|NW|ORD3008^CHAMELEON|||||^^^20260308090000^^R
OBR|1|ORD3008^CHAMELEON||78300^Bone Scan Whole Body^CPT|||20260308083000||||A|||BONE|80614^Shalom^Dikla^^^Dr.
```

---

## 16. ORU^R01 - bone scan report

```
MSH|^~\&|ERAD_RIS|WOLFSON_RAD|CHAMELEON|WOLFSON_MC|20260308160000||ORU^R01|ERD000016|P|2.4
PID|||531782946^^^IL_MOH^NI||Kantor^Shimon^Avi^^Mr.||19680213|M|||Sokolov 41^^Petah Tikva^^4924518^IL||^PRN^CP^054-833-6271
PV1||O|ONCO^700^^WOLFSON||||80614^Shalom^Dikla^^^Dr.||||||||||||VN80008
ORC|RE|ORD3008^CHAMELEON|RES3008^ERAD_RIS
OBR|1|ORD3008^CHAMELEON|RES3008^ERAD_RIS|78300^Bone Scan Whole Body^CPT|||20260308083000|||||||||80614^Shalom^Dikla^^^Dr.||RAD10008||||||F
OBX|1|FT|78300^Bone Scan Report^CPT||Whole Body Bone Scan (Tc-99m MDP)\.br\Clinical indication: Prostate cancer staging\.br\Findings: Increased uptake in right iliac bone\.br\Focal uptake in T12 vertebral body\.br\Degenerative changes in bilateral knees\.br\Impression: Suspicious osseous lesions in right ilium and T12, recommend correlation with CT||||||F
```

---

## 17. ORM^O01 - order cancellation

```
MSH|^~\&|CHAMELEON|KAPLAN_MC|ERAD_RIS|KAPLAN_RAD|20260309090000||ORM^O01|ERD000017|P|2.4
PID|||674218593^^^IL_MOH^NI||Nassar^Rima^Majdal^^Mrs.||19740816|F|||Ben Gurion 23^^Haifa^^3528107^IL||^PRN^CP^052-194-7326
PV1||O|RAD^100^^KAPLAN||||90217^Zoabi^Amal^^^Dr.||||||||||||VN90009
ORC|CA|ORD3009^CHAMELEON|RES3009^ERAD_RIS||||^^^20260309090000
OBR|1|ORD3009^CHAMELEON|RES3009^ERAD_RIS|73721^MRI Knee without Contrast^CPT|||20260309083000|||||||||90217^Zoabi^Amal^^^Dr.
```

---

## 18. ORU^R01 - addendum to prior report

```
MSH|^~\&|ERAD_RIS|SHEBA_RAD|CHAMELEON|SHEBA_MC|20260310100000||ORU^R01|ERD000018|P|2.4
PID|||463829175^^^IL_MOH^NI||Melamed^Ron^David^^Mr.||19930317|M|||Allenby 77^^Tel Aviv^^6513215^IL||^PRN^CP^053-892-7146
PV1||I|MED^301^A^SHEBA||||30912^Aweiss^Dalia^^^Dr.||||||||||||VN10010
ORC|RE|ORD3010^CHAMELEON|RES3010^ERAD_RIS
OBR|1|ORD3010^CHAMELEON|RES3010^ERAD_RIS|71020^Chest X-Ray^CPT|||20260310073000|||||||||30912^Aweiss^Dalia^^^Dr.||RAD10009||||||C
OBX|1|FT|71020^Chest X-Ray Addendum^CPT||ADDENDUM (20260310)\.br\Upon review with pulmonology, the previously noted right lower lobe opacity\.br\is more consistent with atelectasis than pneumonia\.br\Clinical correlation recommended\.br\Original report findings remain otherwise unchanged||||||C
```

---

## 19. SIU^S12 - radiology appointment scheduling

```
MSH|^~\&|ERAD_RIS|ASSUTA_RAD|CHAMELEON|ASSUTA_MC|20260311080000||SIU^S12|ERD000019|P|2.4
SCH|APT40001|APT40001||||ROUTINE^Routine^HL70276|MRI^MRI Examination^L|||||60|min|^^^20260318090000^20260318100000
PID|||295743816^^^IL_MOH^NI||Gabizon^Meir^Binyamin^^Mr.||19770602|M|||HaTzionut 35^^Haifa^^3301521^IL||^PRN^CP^050-561-3847
PV1||O|RAD^100^^ASSUTA||||70125^Nachmias^Ofer^^^Dr.||||||||||||VN20011
AIS|1||70553^MRI Brain^CPT|20260318090000|||60|min
```

---

## 20. ACK - acknowledgment for radiology order

```
MSH|^~\&|ERAD_RIS|SHEBA_RAD|CHAMELEON|SHEBA_MC|20260312090100||ACK|ERD000020|P|2.4
MSA|AA|ORD3001|Order received and scheduled
```
