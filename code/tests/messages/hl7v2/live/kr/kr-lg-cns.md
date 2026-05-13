# LG CNS Healthcare HIS - real HL7v2 ER7 messages

---

## 1. ADT^A01 - inpatient admission

```
MSH|^~\&|LGCNS-HIS|서울대학교병원|KHIS|건강보험심사평가원|20260401090000||ADT^A01^ADT_A01|LG20260401090000001|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A01|20260401090000
PID|||PAT900100^^^서울대학교병원^PI||Ha^Sung-Jin^^^^^L||19640912|M|||서울특별시 종로구 대학로 101^^종로구^서울특별시^03080^KOR^H||^PRN^PH^^82^2^7638219||KOR|M|||||||||||||||||||N
PV1||I|61W^6108^1^서울대학교병원^^^^N||||D900100^Hwang^Dong-Wook^^^^^L^^^DR|||IM||||A|||V900100|||||||||||||||||||||||||||20260401090000
IN1|1||44882211|국민건강보험|강원도 원주시 건강로 32||||||||||||||||||||||||||||||||||||||||6
```

---

## 2. ADT^A04 - outpatient registration

```
MSH|^~\&|LGCNS-HIS|서울대학교병원|KHIS|건강보험심사평가원|20260402080000||ADT^A04^ADT_A01|LG20260402080000002|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A04|20260402080000
PID|||PAT900200^^^서울대학교병원^PI||Yoon^Na-Kyung^^^^^L||19890425|F|||인천광역시 남동구 구월로 233^^남동구^인천광역시^21554^KOR^H||^PRN^PH^^82^32^4579213||KOR|M
PV1||O|소화기내과외래^1^1^서울대학교병원^^^^N||||D900200^Min^So-Hyun^^^^^L^^^DR|||GI||||A|||V900200|||||||||||||||||||||||||||20260402080000
IN1|1||99335577|국민건강보험|강원도 원주시 건강로 32||||||||||||||||||||||||||||||||||||||||8
```

---

## 3. ADT^A02 - patient transfer

```
MSH|^~\&|LGCNS-HIS|서울대학교병원|KHIS|건강보험심사평가원|20260405140000||ADT^A02^ADT_A02|LG20260405140000003|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A02|20260405140000
PID|||PAT900100^^^서울대학교병원^PI||Ha^Sung-Jin^^^^^L||19640912|M|||서울특별시 종로구 대학로 101^^종로구^서울특별시^03080^KOR^H||^PRN^PH^^82^2^7638219||KOR|M
PV1||I|72W^7205^1^서울대학교병원^^^^N||||D900100^Hwang^Dong-Wook^^^^^L^^^DR|||IM||61W^6108^1^서울대학교병원^^^^N|||||||V900100|||||||||||||||||||||||||||20260405140000
```

---

## 4. ORM^O01 - pharmacy order for diabetes

```
MSH|^~\&|LGCNS-HIS|서울대학교병원|약제부|서울대학교병원|20260401100000||ORM^O01^ORM_O01|LG20260401100000004|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT900100^^^서울대학교병원^PI||Ha^Sung-Jin^^^^^L||19640912|M
PV1||I|61W^6108^1^서울대학교병원^^^^N||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
ORC|NW|ORD20260401001^LGCNS-HIS||||||||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
RXO|654800320^메트포르민정500mg^KD코드|||500||mg||PO^경구^HL70162|||||||||||||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
```

---

## 5. OML^O33 - laboratory order for cardiac panel

```
MSH|^~\&|LGCNS-HIS|서울대학교병원|진단검사의학과|서울대학교병원|20260401103000||OML^O33^OML_O33|LG20260401103000005|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT900100^^^서울대학교병원^PI||Ha^Sung-Jin^^^^^L||19640912|M
PV1||I|61W^6108^1^서울대학교병원^^^^N||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
SPM|1|||BLD^혈액^HL70487|||||||||||20260401103000
ORC|NW|LAB20260401001^LGCNS-HIS||||||||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
OBR|1|LAB20260401001^LGCNS-HIS||10839-9^Troponin I.cardiac [Mass/volume] in Serum or Plasma^LN|R||20260401103000
```

---

## 6. ORU^R01 - cardiac marker results

```
MSH|^~\&|진단검사의학과|서울대학교병원|LGCNS-HIS|서울대학교병원|20260401160000||ORU^R01^ORU_R01|LAB20260401160000006|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT900100^^^서울대학교병원^PI||Ha^Sung-Jin^^^^^L||19640912|M
PV1||I|61W^6108^1^서울대학교병원^^^^N||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
ORC|RE|LAB20260401001^LGCNS-HIS||||||||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
OBR|1|LAB20260401001^LGCNS-HIS||10839-9^Troponin I.cardiac [Mass/volume] in Serum or Plasma^LN|R||20260401103000|||||||20260401103000||D900100^Hwang^Dong-Wook^^^^^L^^^DR||||||||20260401160000|||F
OBX|1|NM|10839-9^Troponin I.cardiac [Mass/volume] in Serum or Plasma^LN||0.02|ng/mL|0.00-0.04|N|||F|||20260401160000
OBX|2|NM|33762-6^NT-proBNP [Mass/volume] in Serum or Plasma^LN||185|pg/mL|0-125|H|||F|||20260401160000
OBX|3|NM|2157-6^Creatine kinase-MB [Enzymatic activity/volume] in Serum or Plasma^LN||3.2|ng/mL|0.0-5.0|N|||F|||20260401160000
```

---

## 7. ORU^R01 - echocardiography report with embedded PDF

```
MSH|^~\&|심장초음파실|서울대학교병원|LGCNS-HIS|서울대학교병원|20260403150000||ORU^R01^ORU_R01|ECHO20260403150000007|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT900100^^^서울대학교병원^PI||Ha^Sung-Jin^^^^^L||19640912|M
PV1||I|61W^6108^1^서울대학교병원^^^^N||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
ORC|RE|ECHO20260403001^LGCNS-HIS
OBR|1|ECHO20260403001^LGCNS-HIS||93306^Transthoracic echocardiography^CPT|R||20260403100000|||||||20260403100000||D900100^Hwang^Dong-Wook^^^^^L^^^DR||||||||20260403150000|||F
OBX|1|TX|93306^Transthoracic echocardiography^CPT|1|좌심실 구혈률 62%. 판막 기능 정상. 좌심방 경미 확장(4.2cm). 벽운동 이상 없음.||||||F|||20260403150000
OBX|2|ED|PDF^심초음파보고서PDF^L|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA2NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKEVjaG9jYXJkaW9ncmFwaHkgUmVwb3J0IC0gU05VQkgpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNDIwIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTExCiUlRU9GCg==||||||F|||20260403150000
```

---

## 8. ORM^O01 - radiology order for chest CT

```
MSH|^~\&|LGCNS-HIS|서울대학교병원|영상의학과|서울대학교병원|20260402093000||ORM^O01^ORM_O01|LG20260402093000008|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT900200^^^서울대학교병원^PI||Yoon^Na-Kyung^^^^^L||19890425|F
PV1||O|소화기내과외래^1^1^서울대학교병원^^^^N||||D900200^Min^So-Hyun^^^^^L^^^DR
ORC|NW|RAD20260402001^LGCNS-HIS||||||||||D900200^Min^So-Hyun^^^^^L^^^DR
OBR|1|RAD20260402001^LGCNS-HIS||71260^CT Chest with contrast^RADLEX|R||20260402093000|||||||20260402093000||D900200^Min^So-Hyun^^^^^L^^^DR
```

---

## 9. ADT^A08 - patient information update

```
MSH|^~\&|LGCNS-HIS|서울대학교병원|KHIS|건강보험심사평가원|20260406090000||ADT^A08^ADT_A01|LG20260406090000009|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A08|20260406090000
PID|||PAT900100^^^서울대학교병원^PI||Ha^Sung-Jin^^^^^L||19640912|M|||서울특별시 종로구 대학로 101^^종로구^서울특별시^03080^KOR^H~서울특별시 중구 을지로 281^^중구^서울특별시^04564^KOR^O||^PRN^PH^^82^2^7638219~^WPN^PH^^82^2^31854720||KOR|M|||||||||||||||||||N
PV1||I|72W^7205^1^서울대학교병원^^^^N||||D900100^Hwang^Dong-Wook^^^^^L^^^DR|||IM||||||||V900100|||||||||||||||||||||||||||20260405140000
IN1|1||44882211|국민건강보험|강원도 원주시 건강로 32||||||||||||||||||||||||||||||||||||||||6
```

---

## 10. SIU^S12 - endoscopy appointment scheduled

```
MSH|^~\&|LGCNS-HIS|서울대학교병원|외래예약|서울대학교병원|20260402150000||SIU^S12^SIU_S12|LG20260402150000010|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
SCH|APT20260410001^LGCNS-HIS|APT20260410001^LGCNS-HIS|||||대장내시경^검사예약^L|||||^^40^20260410090000^20260410093000
PID|||PAT900200^^^서울대학교병원^PI||Yoon^Na-Kyung^^^^^L||19890425|F
PV1||O|소화기내과외래^1^1^서울대학교병원^^^^N||||D900200^Min^So-Hyun^^^^^L^^^DR
AIG|1||D900200^Min^So-Hyun^^^^^L^^^DR
AIL|1||내시경센터^1^1^서울대학교병원
```

---

## 11. RDE^O11 - insulin dispense event

```
MSH|^~\&|약제부|서울대학교병원|LGCNS-HIS|서울대학교병원|20260401140000||RDE^O11^RDE_O11|PH20260401140000011|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT900100^^^서울대학교병원^PI||Ha^Sung-Jin^^^^^L||19640912|M
PV1||I|61W^6108^1^서울대학교병원^^^^N||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
ORC|RE|ORD20260401001^LGCNS-HIS|DSP20260401001^약제부|||||||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
RXE|^^^20260401^^^일|654800320^메트포르민정500mg^KD코드|500||mg|정|||||||30|||||||||||PH400^Bae^Eun-Bi^^^^^L^^^RPH
RXD|1|654800320^메트포르민정500mg^KD코드|20260401140000|90|정||||||||||||||PH400^Bae^Eun-Bi^^^^^L^^^RPH
```

---

## 12. DFT^P03 - inpatient charge posting

```
MSH|^~\&|LGCNS-HIS|서울대학교병원|의무기록|서울대학교병원|20260410170000||DFT^P03^DFT_P03|LG20260410170000012|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|P03|20260410170000
PID|||PAT900100^^^서울대학교병원^PI||Ha^Sung-Jin^^^^^L||19640912|M
PV1||I|72W^7205^1^서울대학교병원^^^^N||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
FT1|1|ORD20260410001|20260401|20260410|CG|AJ100^입원료^수가코드||10|580000|||||||||||||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
FT1|2|ORD20260410002|20260401|20260410|CG|C5211^일반화학검사^수가코드||3|20520|||||||||||||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
FT1|3|ORD20260410003|20260403|20260403|CG|EB401^심초음파^수가코드||1|135000|||||||||||||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
```

---

## 13. ORU^R01 - colonoscopy report with embedded PDF

```
MSH|^~\&|내시경센터|서울대학교병원|LGCNS-HIS|서울대학교병원|20260410160000||ORU^R01^ORU_R01|ENDO20260410160000013|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT900200^^^서울대학교병원^PI||Yoon^Na-Kyung^^^^^L||19890425|F
PV1||O|소화기내과외래^1^1^서울대학교병원^^^^N||||D900200^Min^So-Hyun^^^^^L^^^DR
ORC|RE|ENDO20260410001^LGCNS-HIS
OBR|1|ENDO20260410001^LGCNS-HIS||45378^Colonoscopy diagnostic^CPT|R||20260410090000|||||||20260410090000||D900200^Min^So-Hyun^^^^^L^^^DR||||||||20260410160000|||F
OBX|1|TX|45378^Colonoscopy diagnostic^CPT|1|회맹부까지 삽입. 상행결장 5mm 용종 1개 발견, 용종절제술 시행. 나머지 대장 정상.||||||F|||20260410160000
OBX|2|ED|PDF^대장내시경보고서PDF^L|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1OCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKENvbG9ub3Njb3B5IFJlcG9ydCAtIFNOVUJIKSBUaiBFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAgbiAKMDAwMDAwMDQxNCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjUwNQolJUVPRgo=||||||F|||20260410160000
```

---

## 14. ADT^A03 - discharge

```
MSH|^~\&|LGCNS-HIS|서울대학교병원|KHIS|건강보험심사평가원|20260412100000||ADT^A03^ADT_A03|LG20260412100000014|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A03|20260412100000
PID|||PAT900100^^^서울대학교병원^PI||Ha^Sung-Jin^^^^^L||19640912|M|||서울특별시 종로구 대학로 101^^종로구^서울특별시^03080^KOR^H||^PRN^PH^^82^2^7638219||KOR|M
PV1||I|72W^7205^1^서울대학교병원^^^^N||||D900100^Hwang^Dong-Wook^^^^^L^^^DR|||IM||||||||V900100|||||||||||||||||||||||||||20260412100000
```

---

## 15. MDM^T02 - discharge summary with embedded CDA

```
MSH|^~\&|LGCNS-HIS|서울대학교병원|KHIS|건강보험심사평가원|20260412140000||MDM^T02^MDM_T02|LG20260412140000015|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|T02|20260412140000
PID|||PAT900100^^^서울대학교병원^PI||Ha^Sung-Jin^^^^^L||19640912|M
PV1||I|72W^7205^1^서울대학교병원^^^^N||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
TXA|1|DS^퇴원요약^HL70270|TX|20260412140000|D900100^Hwang^Dong-Wook^^^^^L^^^DR||20260412140000||||||DOC20260412001||||||AU
OBX|1|ED|DS^퇴원요약^HL70270|1|^text^xml^Base64^PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj4KICA8dGl0bGU+7ZOo7JuQ7JqU7JW9PC90aXRsZT4KICA8ZWZmZWN0aXZlVGltZSB2YWx1ZT0iMjAyNjA0MTIiLz4KICA8Y29tcG9uZW50PgogICAgPHN0cnVjdHVyZWRCb2R5PgogICAgICA8Y29tcG9uZW50PgogICAgICAgIDxzZWN0aW9uPgogICAgICAgICAgPHRpdGxlPuynhOuLqOuqhTwvdGl0bGU+CiAgICAgICAgICA8dGV4dD7soJzrqowg64u564u5LCDqs6DtmIjslZUg7KGw7KCI7JqUPC90ZXh0PgogICAgICAgIDwvc2VjdGlvbj4KICAgICAgPC9jb21wb25lbnQ+CiAgICA8L3N0cnVjdHVyZWRCb2R5PgogIDwvY29tcG9uZW50Pgo8L0NsaW5pY2FsRG9jdW1lbnQ+Cg==||||||F|||20260412140000
```

---

## 16. ORU^R01 - liver function test result

```
MSH|^~\&|진단검사의학과|서울대학교병원|LGCNS-HIS|서울대학교병원|20260402180000||ORU^R01^ORU_R01|LAB20260402180000016|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT900200^^^서울대학교병원^PI||Yoon^Na-Kyung^^^^^L||19890425|F
PV1||O|소화기내과외래^1^1^서울대학교병원^^^^N||||D900200^Min^So-Hyun^^^^^L^^^DR
ORC|RE|LAB20260402001^LGCNS-HIS||||||||||D900200^Min^So-Hyun^^^^^L^^^DR
OBR|1|LAB20260402001^LGCNS-HIS||24325-3^Hepatic function panel^LN|R||20260402090000|||||||20260402090000||D900200^Min^So-Hyun^^^^^L^^^DR||||||||20260402180000|||F
OBX|1|NM|1742-6^Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||32|U/L|0-41|N|||F|||20260402180000
OBX|2|NM|1920-8^Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||28|U/L|0-40|N|||F|||20260402180000
OBX|3|NM|6768-6^Alkaline phosphatase [Enzymatic activity/volume] in Serum or Plasma^LN||68|U/L|40-129|N|||F|||20260402180000
OBX|4|NM|1975-2^Bilirubin.total [Mass/volume] in Serum or Plasma^LN||0.8|mg/dL|0.1-1.2|N|||F|||20260402180000
OBX|5|NM|1751-7^Albumin [Mass/volume] in Serum or Plasma^LN||4.3|g/dL|3.5-5.2|N|||F|||20260402180000
```

---

## 17. ORM^O01 - MRI abdomen order

```
MSH|^~\&|LGCNS-HIS|서울대학교병원|영상의학과|서울대학교병원|20260408100000||ORM^O01^ORM_O01|LG20260408100000017|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT900200^^^서울대학교병원^PI||Yoon^Na-Kyung^^^^^L||19890425|F
PV1||O|소화기내과외래^1^1^서울대학교병원^^^^N||||D900200^Min^So-Hyun^^^^^L^^^DR
ORC|NW|RAD20260408001^LGCNS-HIS||||||||||D900200^Min^So-Hyun^^^^^L^^^DR
OBR|1|RAD20260408001^LGCNS-HIS||74183^MRI Abdomen with and without contrast^RADLEX|R||20260408100000|||||||20260408100000||D900200^Min^So-Hyun^^^^^L^^^DR
```

---

## 18. ORU^R01 - CBC and differential result

```
MSH|^~\&|진단검사의학과|서울대학교병원|LGCNS-HIS|서울대학교병원|20260401170000||ORU^R01^ORU_R01|LAB20260401170000018|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT900100^^^서울대학교병원^PI||Ha^Sung-Jin^^^^^L||19640912|M
PV1||I|61W^6108^1^서울대학교병원^^^^N||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
ORC|RE|LAB20260401002^LGCNS-HIS||||||||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
OBR|1|LAB20260401002^LGCNS-HIS||57021-8^CBC W Auto Differential panel - Blood^LN|R||20260401103000|||||||20260401103000||D900100^Hwang^Dong-Wook^^^^^L^^^DR||||||||20260401170000|||F
OBX|1|NM|6690-2^Leukocytes [#/volume] in Blood by Automated count^LN||8.4|10*3/uL|4.0-10.0|N|||F|||20260401170000
OBX|2|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||13.2|g/dL|13.0-17.0|N|||F|||20260401170000
OBX|3|NM|777-3^Platelets [#/volume] in Blood by Automated count^LN||210|10*3/uL|150-400|N|||F|||20260401170000
OBX|4|NM|770-8^Neutrophils/100 leukocytes in Blood by Automated count^LN||62|%|40-70|N|||F|||20260401170000
OBX|5|NM|736-9^Lymphocytes/100 leukocytes in Blood by Automated count^LN||28|%|20-40|N|||F|||20260401170000
```

---

## 19. ORM^O01 - endoscopy order

```
MSH|^~\&|LGCNS-HIS|서울대학교병원|내시경센터|서울대학교병원|20260410080000||ORM^O01^ORM_O01|LG20260410080000019|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT900200^^^서울대학교병원^PI||Yoon^Na-Kyung^^^^^L||19890425|F
PV1||O|소화기내과외래^1^1^서울대학교병원^^^^N||||D900200^Min^So-Hyun^^^^^L^^^DR
ORC|NW|ENDO20260410001^LGCNS-HIS||||||||||D900200^Min^So-Hyun^^^^^L^^^DR
OBR|1|ENDO20260410001^LGCNS-HIS||45378^Colonoscopy diagnostic^CPT|R||20260410080000|||||||20260410080000||D900200^Min^So-Hyun^^^^^L^^^DR
```

---

## 20. ORU^R01 - HbA1c and renal function result

```
MSH|^~\&|진단검사의학과|서울대학교병원|LGCNS-HIS|서울대학교병원|20260405180000||ORU^R01^ORU_R01|LAB20260405180000020|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT900100^^^서울대학교병원^PI||Ha^Sung-Jin^^^^^L||19640912|M
PV1||I|72W^7205^1^서울대학교병원^^^^N||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
ORC|RE|LAB20260405001^LGCNS-HIS||||||||||D900100^Hwang^Dong-Wook^^^^^L^^^DR
OBR|1|LAB20260405001^LGCNS-HIS||4548-4^HbA1c^LN|R||20260405090000|||||||20260405090000||D900100^Hwang^Dong-Wook^^^^^L^^^DR||||||||20260405180000|||F
OBX|1|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN||7.8|%|4.0-6.0|H|||F|||20260405180000
OBX|2|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||1.3|mg/dL|0.7-1.3|N|||F|||20260405180000
OBX|3|NM|6299-2^Urea nitrogen [Mass/volume] in Blood^LN||22|mg/dL|7-20|H|||F|||20260405180000
OBX|4|NM|33914-3^Glomerular filtration rate/1.73 sq M.predicted [Volume Rate/Area] in Serum or Plasma^LN||58|mL/min/1.73m2|>60|L|||F|||20260405180000
```
