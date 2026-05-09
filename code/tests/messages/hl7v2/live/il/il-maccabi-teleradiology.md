# Maccabi Teleradiology - real HL7v2 ER7 messages

---

## 1. ORM^O01 - CT chest order for remote reading

```
MSH|^~\&|MACCABI_RIS|MACCABI_IMG_TA|MACCABI_TELERAD|MACCABI_REMOTE|20260301090000||ORM^O01|MTR000001|P|2.4
PID|||482371956^^^IL_MOH^NI~M10001^^^MACCABI^MR||Cohen^Hadar^Tirza^^Mrs.||19780315|F|||Hatzionut 47^^Haifa^^3303125^IL||^PRN^CP^052-418-3729
PV1||O|RAD^100^^MACCABI_IMG_TA||||44567^Friedman^Ronit^^^Dr.||||||||||||VN10001
ORC|NW|ORD6001^MACCABI_RIS|||||^^^20260301090000^^R
OBR|1|ORD6001^MACCABI_RIS||71260^CT Chest with Contrast^CPT|||20260301083000||||A|||CHEST|44567^Friedman^Ronit^^^Dr.|||1.2.826.0.1.3680043.8.1055.1.20260301083000.12345
```

---

## 2. ORU^R01 - CT chest report from remote radiologist

```
MSH|^~\&|MACCABI_TELERAD|MACCABI_REMOTE|MACCABI_RIS|MACCABI_IMG_TA|20260301140000||ORU^R01|MTR000002|P|2.4
PID|||482371956^^^IL_MOH^NI~M10001^^^MACCABI^MR||Cohen^Hadar^Tirza^^Mrs.||19780315|F|||Hatzionut 47^^Haifa^^3303125^IL||^PRN^CP^052-418-3729
PV1||O|RAD^100^^MACCABI_IMG_TA||||44567^Friedman^Ronit^^^Dr.||||||||||||VN10001
ORC|RE|ORD6001^MACCABI_RIS|RES6001^MACCABI_TELERAD
OBR|1|ORD6001^MACCABI_RIS|RES6001^MACCABI_TELERAD|71260^CT Chest with Contrast^CPT|||20260301083000|||||||||44567^Friedman^Ronit^^^Dr.||RAD20001||||||F
OBX|1|FT|71260^CT Chest Report^CPT||CT Chest with IV Contrast\.br\Clinical indication: Cough, weight loss\.br\Technique: Helical CT with IV contrast\.br\Findings: 1.8 cm spiculated nodule in right upper lobe\.br\Mediastinal lymphadenopathy, largest 2.2 cm subcarinal\.br\No pleural effusion\.br\Impression: Suspicious RUL nodule with mediastinal lymphadenopathy, recommend PET-CT||||||F
```

---

## 3. ORM^O01 - MRI knee order

```
MSH|^~\&|MACCABI_RIS|MACCABI_IMG_JLM|MACCABI_TELERAD|MACCABI_REMOTE|20260302090000||ORM^O01|MTR000003|P|2.4
PID|||561928374^^^IL_MOH^NI~M20002^^^MACCABI^MR||Mizrahi^Avi^Yaakov^^Mr.||19650722|M|||Emek Refaim 18^^Jerusalem^^9314218^IL||^PRN^CP^054-768-4321
PV1||O|RAD^100^^MACCABI_IMG_JLM||||55678^Navon^Dorit^^^Dr.||||||||||||VN20002
ORC|NW|ORD6002^MACCABI_RIS|||||^^^20260302090000^^R
OBR|1|ORD6002^MACCABI_RIS||73721^MRI Knee without Contrast^CPT|||20260302083000||||A|||KNEE|55678^Navon^Dorit^^^Dr.|||1.2.826.0.1.3680043.8.1055.1.20260302083000.23456
```

---

## 4. ORU^R01 - MRI knee report

```
MSH|^~\&|MACCABI_TELERAD|MACCABI_REMOTE|MACCABI_RIS|MACCABI_IMG_JLM|20260302150000||ORU^R01|MTR000004|P|2.4
PID|||561928374^^^IL_MOH^NI~M20002^^^MACCABI^MR||Mizrahi^Avi^Yaakov^^Mr.||19650722|M|||Emek Refaim 18^^Jerusalem^^9314218^IL||^PRN^CP^054-768-4321
PV1||O|RAD^100^^MACCABI_IMG_JLM||||55678^Navon^Dorit^^^Dr.||||||||||||VN20002
ORC|RE|ORD6002^MACCABI_RIS|RES6002^MACCABI_TELERAD
OBR|1|ORD6002^MACCABI_RIS|RES6002^MACCABI_TELERAD|73721^MRI Knee without Contrast^CPT|||20260302083000|||||||||55678^Navon^Dorit^^^Dr.||RAD20002||||||F
OBX|1|FT|73721^MRI Knee Report^CPT||MRI Right Knee without Contrast\.br\Clinical indication: Knee pain after sports injury\.br\Findings: Horizontal tear of the posterior horn of the medial meniscus\.br\Grade 2 chondral changes in medial compartment\.br\ACL and PCL intact\.br\Small joint effusion\.br\Impression: Medial meniscus tear, posterior horn||||||F
```

---

## 5. ORM^O01 - X-ray order with priority STAT

```
MSH|^~\&|MACCABI_RIS|MACCABI_IMG_HFA|MACCABI_TELERAD|MACCABI_REMOTE|20260303200000||ORM^O01|MTR000005|P|2.4
PID|||673841259^^^IL_MOH^NI~M30003^^^MACCABI^MR||Khoury^Mariam^Layla^^Mrs.||19900110|F|||Salah-a-Din 12^^Acre^^2412304^IL||^PRN^CP^050-987-3215
PV1||O|RAD^100^^MACCABI_IMG_HFA||||66789^Barak^Yonatan^^^Dr.||||||||||||VN30003
ORC|NW|ORD6003^MACCABI_RIS|||||^^^20260303200000^^S
OBR|1|ORD6003^MACCABI_RIS||71010^Chest X-Ray Single View^CPT|||20260303195000||||A|||CHEST|66789^Barak^Yonatan^^^Dr.
```

---

## 6. ORU^R01 - STAT chest X-ray report

```
MSH|^~\&|MACCABI_TELERAD|MACCABI_REMOTE|MACCABI_RIS|MACCABI_IMG_HFA|20260303210000||ORU^R01|MTR000006|P|2.4
PID|||673841259^^^IL_MOH^NI~M30003^^^MACCABI^MR||Khoury^Mariam^Layla^^Mrs.||19900110|F|||Salah-a-Din 12^^Acre^^2412304^IL||^PRN^CP^050-987-3215
PV1||O|RAD^100^^MACCABI_IMG_HFA||||66789^Barak^Yonatan^^^Dr.||||||||||||VN30003
ORC|RE|ORD6003^MACCABI_RIS|RES6003^MACCABI_TELERAD
OBR|1|ORD6003^MACCABI_RIS|RES6003^MACCABI_TELERAD|71010^Chest X-Ray Single View^CPT|||20260303195000|||||||||66789^Barak^Yonatan^^^Dr.||RAD20003||||||F
OBX|1|FT|71010^Chest X-Ray Report^CPT||Chest X-Ray AP\.br\Clinical indication: Chest pain, dyspnea\.br\Findings: Bilateral pulmonary edema\.br\Cardiomegaly with cardiothoracic ratio 0.62\.br\Small bilateral pleural effusions\.br\Impression: Congestive heart failure||||||F
```

---

## 7. ORM^O01 - ultrasound thyroid order

```
MSH|^~\&|MACCABI_RIS|MACCABI_IMG_BS|MACCABI_TELERAD|MACCABI_REMOTE|20260304090000||ORM^O01|MTR000007|P|2.4
PID|||794215683^^^IL_MOH^NI~M40004^^^MACCABI^MR||Dahan^Reuven^Yair^^Mr.||19550830|M|||King George 15^^Jerusalem^^9426215^IL||^PRN^PH^02-624-3781
PV1||O|RAD^100^^MACCABI_IMG_BS||||77890^Ben-Ari^Liat^^^Dr.||||||||||||VN40004
ORC|NW|ORD6004^MACCABI_RIS|||||^^^20260304090000^^R
OBR|1|ORD6004^MACCABI_RIS||76536^Ultrasound Thyroid^CPT|||20260304083000||||A|||THYROID|77890^Ben-Ari^Liat^^^Dr.
```

---

## 8. ORU^R01 - thyroid ultrasound report with embedded PDF (base64 ED)

```
MSH|^~\&|MACCABI_TELERAD|MACCABI_REMOTE|MACCABI_RIS|MACCABI_IMG_BS|20260304140000||ORU^R01|MTR000008|P|2.4
PID|||794215683^^^IL_MOH^NI~M40004^^^MACCABI^MR||Dahan^Reuven^Yair^^Mr.||19550830|M|||King George 15^^Jerusalem^^9426215^IL||^PRN^PH^02-624-3781
PV1||O|RAD^100^^MACCABI_IMG_BS||||77890^Ben-Ari^Liat^^^Dr.||||||||||||VN40004
ORC|RE|ORD6004^MACCABI_RIS|RES6004^MACCABI_TELERAD
OBR|1|ORD6004^MACCABI_RIS|RES6004^MACCABI_TELERAD|76536^Ultrasound Thyroid^CPT|||20260304083000|||||||||77890^Ben-Ari^Liat^^^Dr.||RAD20004||||||F
OBX|1|FT|76536^Thyroid US Report^CPT||Ultrasound of the Thyroid\.br\Right lobe: 4.5 x 1.8 x 1.5 cm. Heterogeneous 1.2 cm solid nodule, TI-RADS 4\.br\Left lobe: 4.2 x 1.7 x 1.4 cm. Normal echogenicity\.br\Isthmus: Normal\.br\Impression: Right thyroid nodule TI-RADS 4, recommend FNA||||||F
OBX|2|ED|PDF^Thyroid US Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvUmVzb3VyY2VzIDw8ID4+ID4+CmVuZG9iagp4cmVmCjAgNAowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNCAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMjE2CiUlRU9GCg==||||||F
```

---

## 9. ORU^R01 - PET-CT report with embedded PDF (base64 ED)

```
MSH|^~\&|MACCABI_TELERAD|MACCABI_REMOTE|MACCABI_RIS|MACCABI_IMG_TA|20260305160000||ORU^R01|MTR000009|P|2.4
PID|||826491357^^^IL_MOH^NI~M50005^^^MACCABI^MR||Peretz^Sarah^Leah^^Mrs.||19881205|F|||Weizmann 8^^Rehovot^^7610001^IL||^PRN^CP^058-345-7218
PV1||O|RAD^100^^MACCABI_IMG_TA||||44567^Friedman^Ronit^^^Dr.||||||||||||VN50005
ORC|RE|ORD6005^MACCABI_RIS|RES6005^MACCABI_TELERAD
OBR|1|ORD6005^MACCABI_RIS|RES6005^MACCABI_TELERAD|78816^PET-CT Whole Body^CPT|||20260305090000|||||||||44567^Friedman^Ronit^^^Dr.||RAD20005||||||F
OBX|1|FT|78816^PET-CT Report^CPT||FDG PET-CT Whole Body\.br\Clinical indication: Lung nodule staging\.br\Findings: FDG-avid 1.8 cm RUL nodule, SUVmax 8.2\.br\FDG-avid subcarinal lymph node, SUVmax 5.4\.br\No distant metastatic disease\.br\Impression: Stage IIIA NSCLC (T1cN2M0)||||||F
OBX|2|ED|PDF^PET-CT Report PDF^L||^application^pdf^Base64^JVBERi0xLjUKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvUmVzb3VyY2VzIDw8ID4+ID4+CmVuZG9iagp4cmVmCjAgNAowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNCAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMjE2CiUlRU9GCg==||||||F
```

---

## 10. ORM^O01 - DEXA bone density order

```
MSH|^~\&|MACCABI_RIS|MACCABI_IMG_NT|MACCABI_TELERAD|MACCABI_REMOTE|20260306090000||ORM^O01|MTR000010|P|2.4
PID|||915362847^^^IL_MOH^NI~M60006^^^MACCABI^MR||Azoulay^Yosef^Haim^^Mr.||19700415|M|||Kaplan 30^^Be'er Sheva^^8425503^IL||^PRN^CP^052-568-9012
PV1||O|RAD^100^^MACCABI_IMG_NT||||77891^Tadesse^Liat^^^Dr.||||||||||||VN60006
ORC|NW|ORD6006^MACCABI_RIS|||||^^^20260306090000^^R
OBR|1|ORD6006^MACCABI_RIS||77080^DEXA Bone Density^CPT|||20260306083000||||A|||BONE|77891^Tadesse^Liat^^^Dr.
```

---

## 11. ORU^R01 - DEXA result

```
MSH|^~\&|MACCABI_TELERAD|MACCABI_REMOTE|MACCABI_RIS|MACCABI_IMG_NT|20260306140000||ORU^R01|MTR000011|P|2.4
PID|||915362847^^^IL_MOH^NI~M60006^^^MACCABI^MR||Azoulay^Yosef^Haim^^Mr.||19700415|M|||Kaplan 30^^Be'er Sheva^^8425503^IL||^PRN^CP^052-568-9012
PV1||O|RAD^100^^MACCABI_IMG_NT||||77891^Tadesse^Liat^^^Dr.||||||||||||VN60006
ORC|RE|ORD6006^MACCABI_RIS|RES6006^MACCABI_TELERAD
OBR|1|ORD6006^MACCABI_RIS|RES6006^MACCABI_TELERAD|77080^DEXA Bone Density^CPT|||20260306083000|||||||||77891^Tadesse^Liat^^^Dr.||RAD20006||||||F
OBX|1|NM|DEXA_LS_BMD^Lumbar Spine BMD^L||0.85|g/cm2||||F
OBX|2|NM|DEXA_LS_TSCORE^Lumbar Spine T-Score^L||-1.8||||||F
OBX|3|NM|DEXA_FN_BMD^Femoral Neck BMD^L||0.72|g/cm2||||F
OBX|4|NM|DEXA_FN_TSCORE^Femoral Neck T-Score^L||-2.2||||||F
OBX|5|ST|DEXA_INTERP^Interpretation^L||Osteopenia at lumbar spine. Osteoporosis at femoral neck. Recommend treatment evaluation.||||||F
```

---

## 12. ORM^O01 - CT angiography coronary order

```
MSH|^~\&|MACCABI_RIS|MACCABI_IMG_TA|MACCABI_TELERAD|MACCABI_REMOTE|20260307090000||ORM^O01|MTR000012|P|2.4
PID|||374826159^^^IL_MOH^NI~M70007^^^MACCABI^MR||Stern^Devorah^Bracha^^Mrs.||19820920|F|||Jabotinsky 40^^Ramat Gan^^5252007^IL||^PRN^CP^050-113-3445
PV1||O|RAD^100^^MACCABI_IMG_TA||||44567^Friedman^Ronit^^^Dr.||||||||||||VN70007
ORC|NW|ORD6007^MACCABI_RIS|||||^^^20260307090000^^R
OBR|1|ORD6007^MACCABI_RIS||75574^CT Coronary Angiography^CPT|||20260307083000||||A|||HEART|44567^Friedman^Ronit^^^Dr.
```

---

## 13. ORU^R01 - CT coronary angiography report

```
MSH|^~\&|MACCABI_TELERAD|MACCABI_REMOTE|MACCABI_RIS|MACCABI_IMG_TA|20260307160000||ORU^R01|MTR000013|P|2.4
PID|||374826159^^^IL_MOH^NI~M70007^^^MACCABI^MR||Stern^Devorah^Bracha^^Mrs.||19820920|F|||Jabotinsky 40^^Ramat Gan^^5252007^IL||^PRN^CP^050-113-3445
PV1||O|RAD^100^^MACCABI_IMG_TA||||44567^Friedman^Ronit^^^Dr.||||||||||||VN70007
ORC|RE|ORD6007^MACCABI_RIS|RES6007^MACCABI_TELERAD
OBR|1|ORD6007^MACCABI_RIS|RES6007^MACCABI_TELERAD|75574^CT Coronary Angiography^CPT|||20260307083000|||||||||44567^Friedman^Ronit^^^Dr.||RAD20007||||||F
OBX|1|FT|75574^CTA Coronary Report^CPT||CT Coronary Angiography\.br\Calcium score: 45\.br\LAD: Mild non-obstructive plaque in proximal segment\.br\LCx: Normal\.br\RCA: Normal\.br\Impression: Mild non-obstructive CAD. CAD-RADS 2.||||||F
```

---

## 14. ORM^O01 - order modification

```
MSH|^~\&|MACCABI_RIS|MACCABI_IMG_TA|MACCABI_TELERAD|MACCABI_REMOTE|20260308090000||ORM^O01|MTR000014|P|2.4
PID|||582714639^^^IL_MOH^NI~M80008^^^MACCABI^MR||Petrov^Boris^Mikhail^^Mr.||19720618|M|||HaShachar 5^^Ashdod^^7758037^IL||^PRN^CP^054-228-3447
PV1||O|RAD^100^^MACCABI_IMG_TA||||44567^Friedman^Ronit^^^Dr.||||||||||||VN80008
ORC|XO|ORD6008^MACCABI_RIS|||||^^^20260308090000^^R
OBR|1|ORD6008^MACCABI_RIS||74177^CT Abdomen with Contrast^CPT|||20260308083000||||A|||ABD|44567^Friedman^Ronit^^^Dr.
NTE|1||Changed from non-contrast to contrast study per ordering physician request
```

---

## 15. ORU^R01 - preliminary report (wet read)

```
MSH|^~\&|MACCABI_TELERAD|MACCABI_REMOTE|MACCABI_RIS|MACCABI_IMG_HFA|20260309100000||ORU^R01|MTR000015|P|2.4
PID|||693158274^^^IL_MOH^NI~M90009^^^MACCABI^MR||Bitton^Rachel^Esther^^Mrs.||19680309|F|||HaNevi'im 14^^Jerusalem^^9423614^IL||^PRN^CP^052-876-4521
PV1||O|RAD^100^^MACCABI_IMG_HFA||||66789^Barak^Yonatan^^^Dr.||||||||||||VN90009
ORC|RE|ORD6009^MACCABI_RIS|RES6009^MACCABI_TELERAD
OBR|1|ORD6009^MACCABI_RIS|RES6009^MACCABI_TELERAD|71020^Chest X-Ray^CPT|||20260309090000|||||||||66789^Barak^Yonatan^^^Dr.||RAD20008||||||P
OBX|1|FT|71020^Chest X-Ray Preliminary^CPT||PRELIMINARY REPORT\.br\Chest X-Ray PA and Lateral\.br\Findings: Large right-sided pneumothorax\.br\Recommend urgent chest tube placement\.br\Final report to follow||||||P
```

---

## 16. ORU^R01 - finalized report replacing preliminary

```
MSH|^~\&|MACCABI_TELERAD|MACCABI_REMOTE|MACCABI_RIS|MACCABI_IMG_HFA|20260309140000||ORU^R01|MTR000016|P|2.4
PID|||693158274^^^IL_MOH^NI~M90009^^^MACCABI^MR||Bitton^Rachel^Esther^^Mrs.||19680309|F|||HaNevi'im 14^^Jerusalem^^9423614^IL||^PRN^CP^052-876-4521
PV1||O|RAD^100^^MACCABI_IMG_HFA||||66789^Barak^Yonatan^^^Dr.||||||||||||VN90009
ORC|RE|ORD6009^MACCABI_RIS|RES6009^MACCABI_TELERAD
OBR|1|ORD6009^MACCABI_RIS|RES6009^MACCABI_TELERAD|71020^Chest X-Ray^CPT|||20260309090000|||||||||66789^Barak^Yonatan^^^Dr.||RAD20008||||||F
OBX|1|FT|71020^Chest X-Ray Report^CPT||Chest X-Ray PA and Lateral\.br\Findings: Large right-sided pneumothorax with 60% lung collapse\.br\No mediastinal shift\.br\No rib fractures identified\.br\Impression: Large right pneumothorax requiring intervention||||||F
```

---

## 17. ORM^O01 - order cancellation

```
MSH|^~\&|MACCABI_RIS|MACCABI_IMG_TA|MACCABI_TELERAD|MACCABI_REMOTE|20260310090000||ORM^O01|MTR000017|P|2.4
PID|||417286953^^^IL_MOH^NI~M10010^^^MACCABI^MR||Edri^Shimon^Avraham^^Mr.||19950512|M|||Allenby 77^^Tel Aviv^^6513215^IL||^PRN^CP^053-446-5728
PV1||O|RAD^100^^MACCABI_IMG_TA||||44567^Friedman^Ronit^^^Dr.||||||||||||VN10010
ORC|CA|ORD6010^MACCABI_RIS|||||^^^20260310090000
OBR|1|ORD6010^MACCABI_RIS||70553^MRI Brain with and without Contrast^CPT|||20260310083000|||||||||44567^Friedman^Ronit^^^Dr.
```

---

## 18. ORU^R01 - critical finding notification

```
MSH|^~\&|MACCABI_TELERAD|MACCABI_REMOTE|MACCABI_RIS|MACCABI_IMG_BS|20260311110000||ORU^R01|MTR000018|P|2.4
PID|||528419367^^^IL_MOH^NI~M20011^^^MACCABI^MR||Vaknin^Oded^Eliyahu^^Mr.||19800101|M|||Arlozorov 35^^Haifa^^3301521^IL||^PRN^CP^050-668-2734
PV1||O|RAD^100^^MACCABI_IMG_BS||||77891^Tadesse^Liat^^^Dr.||||||||||||VN20011
ORC|RE|ORD6011^MACCABI_RIS|RES6011^MACCABI_TELERAD
OBR|1|ORD6011^MACCABI_RIS|RES6011^MACCABI_TELERAD|74176^CT Abdomen without Contrast^CPT|||20260311090000|||||||||77891^Tadesse^Liat^^^Dr.||RAD20009||||||F
OBX|1|FT|74176^CT Abdomen Report^CPT||CRITICAL FINDING - COMMUNICATED TO ORDERING PHYSICIAN AT 11:05\.br\CT Abdomen without Contrast\.br\Findings: 8.5 cm infrarenal abdominal aortic aneurysm\.br\Periaortic stranding suggesting contained leak\.br\Impression: Large AAA with possible contained rupture. Urgent surgical consultation.||||||F
```

---

## 19. SIU^S12 - imaging appointment scheduling

```
MSH|^~\&|MACCABI_RIS|MACCABI_IMG_TA|MACCABI_TELERAD|MACCABI_REMOTE|20260312080000||SIU^S12|MTR000019|P|2.4
PID|||618293574^^^IL_MOH^NI~M30012^^^MACCABI^MR||Aslan^Yaron^Tomer^^Mr.||19880315|M|||Balfour 22^^Bat Yam^^5930002^IL||^PRN^CP^052-218-4936
PV1||O|RAD^100^^MACCABI_IMG_TA||||44567^Friedman^Ronit^^^Dr.||||||||||||VN30012
SCH|APT60001|APT60001||||ROUTINE^Routine^HL70276|MRI^MRI Examination^L|||||45|min|^^^20260319090000^20260319094500
AIS|1||70553^MRI Brain^CPT|20260319090000|||45|min
```

---

## 20. ACK - teleradiology acknowledgment

```
MSH|^~\&|MACCABI_TELERAD|MACCABI_REMOTE|MACCABI_RIS|MACCABI_IMG_TA|20260313090100||ACK|MTR000020|P|2.4
MSA|AA|ORD6001|Order received for remote reading
```
