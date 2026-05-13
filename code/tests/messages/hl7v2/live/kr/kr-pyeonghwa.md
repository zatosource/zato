# Pyeonghwa IS (Catholic HIS) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - inpatient admission

```
MSH|^~\&|Catholic-HIS|이화여자대학교 목동병원|KHIS|건강보험심사평가원|20260401090000||ADT^A01^ADT_A01|CATH20260401090000001|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A01|20260401090000
PID|||PAT600100^^^이화여자대학교 목동병원^PI||Yang^Hyun-Woo^^^^^L||19720830|M|||서울특별시 양천구 목동동로 221^^양천구^서울특별시^07985^KOR^H||^PRN^PH^^82^2^26497813||KOR|M|||||||||||||||||||N
PV1||I|71W^7108^1^이화여자대학교 목동병원^^^^N||||D600100^Ahn^Jae-Won^^^^^L^^^DR|||IM||||A|||V600100|||||||||||||||||||||||||||20260401090000
IN1|1||67823451|국민건강보험|강원도 원주시 건강로 32||||||||||||||||||||||||||||||||||||||||6
```

---

## 2. ADT^A04 - outpatient registration

```
MSH|^~\&|Catholic-HIS|이화여자대학교 목동병원|KHIS|건강보험심사평가원|20260402080000||ADT^A04^ADT_A01|CATH20260402080000002|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A04|20260402080000
PID|||PAT600200^^^이화여자대학교 목동병원^PI||Go^Seo-Hyun^^^^^L||19850617|F|||경기도 고양시 일산서구 킨텍스로 217^^일산서구^경기도^10326^KOR^H||^PRN^PH^^82^31^9172845||KOR|S
PV1||O|내과외래^1^1^이화여자대학교 목동병원^^^^N||||D600200^Ryu^Da-Young^^^^^L^^^DR|||IM||||A|||V600200|||||||||||||||||||||||||||20260402080000
IN1|1||32178654|국민건강보험|강원도 원주시 건강로 32||||||||||||||||||||||||||||||||||||||||8
```

---

## 3. ADT^A02 - patient transfer

```
MSH|^~\&|Catholic-HIS|이화여자대학교 목동병원|KHIS|건강보험심사평가원|20260405140000||ADT^A02^ADT_A02|CATH20260405140000003|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A02|20260405140000
PID|||PAT600100^^^이화여자대학교 목동병원^PI||Yang^Hyun-Woo^^^^^L||19720830|M|||서울특별시 양천구 목동동로 221^^양천구^서울특별시^07985^KOR^H||^PRN^PH^^82^2^26497813||KOR|M
PV1||I|82W^8205^1^이화여자대학교 목동병원^^^^N||||D600100^Ahn^Jae-Won^^^^^L^^^DR|||IM||71W^7108^1^이화여자대학교 목동병원^^^^N|||||||V600100|||||||||||||||||||||||||||20260405140000
```

---

## 4. ORM^O01 - pharmacy order

```
MSH|^~\&|Catholic-HIS|이화여자대학교 목동병원|약제부|이화여자대학교 목동병원|20260401100000||ORM^O01^ORM_O01|CATH20260401100000004|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT600100^^^이화여자대학교 목동병원^PI||Yang^Hyun-Woo^^^^^L||19720830|M
PV1||I|71W^7108^1^이화여자대학교 목동병원^^^^N||||D600100^Ahn^Jae-Won^^^^^L^^^DR
ORC|NW|ORD20260401001^Catholic-HIS||||||||||D600100^Ahn^Jae-Won^^^^^L^^^DR
RXO|652600570^아토르바스타틴정20mg^KD코드|||20||mg||PO^경구^HL70162|||||||||||||||D600100^Ahn^Jae-Won^^^^^L^^^DR
```

---

## 5. OML^O33 - laboratory order

```
MSH|^~\&|Catholic-HIS|이화여자대학교 목동병원|진단검사의학과|이화여자대학교 목동병원|20260401103000||OML^O33^OML_O33|CATH20260401103000005|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT600100^^^이화여자대학교 목동병원^PI||Yang^Hyun-Woo^^^^^L||19720830|M
PV1||I|71W^7108^1^이화여자대학교 목동병원^^^^N||||D600100^Ahn^Jae-Won^^^^^L^^^DR
SPM|1|||BLD^혈액^HL70487|||||||||||20260401103000
ORC|NW|LAB20260401001^Catholic-HIS||||||||||D600100^Ahn^Jae-Won^^^^^L^^^DR
OBR|1|LAB20260401001^Catholic-HIS||4548-4^HbA1c^LN|R||20260401103000
```

---

## 6. ORU^R01 - laboratory result with multiple analytes

```
MSH|^~\&|진단검사의학과|이화여자대학교 목동병원|Catholic-HIS|이화여자대학교 목동병원|20260401160000||ORU^R01^ORU_R01|LAB20260401160000006|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT600100^^^이화여자대학교 목동병원^PI||Yang^Hyun-Woo^^^^^L||19720830|M
PV1||I|71W^7108^1^이화여자대학교 목동병원^^^^N||||D600100^Ahn^Jae-Won^^^^^L^^^DR
ORC|RE|LAB20260401001^Catholic-HIS||||||||||D600100^Ahn^Jae-Won^^^^^L^^^DR
OBR|1|LAB20260401001^Catholic-HIS||4548-4^HbA1c^LN|R||20260401103000|||||||20260401103000||D600100^Ahn^Jae-Won^^^^^L^^^DR||||||||20260401160000|||F
OBX|1|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN||7.2|%|4.0-6.0|H|||F|||20260401160000
OBX|2|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||142|mg/dL|74-106|H|||F|||20260401160000
OBX|3|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||1.1|mg/dL|0.7-1.3|N|||F|||20260401160000
OBX|4|NM|6299-2^Urea nitrogen [Mass/volume] in Blood^LN||18|mg/dL|7-20|N|||F|||20260401160000
```

---

## 7. ORU^R01 - pathology report with embedded PDF

```
MSH|^~\&|병리과|이화여자대학교 목동병원|Catholic-HIS|이화여자대학교 목동병원|20260408150000||ORU^R01^ORU_R01|PATH20260408150000007|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT600200^^^이화여자대학교 목동병원^PI||Go^Seo-Hyun^^^^^L||19850617|F
PV1||O|내과외래^1^1^이화여자대학교 목동병원^^^^N||||D600200^Ryu^Da-Young^^^^^L^^^DR
ORC|RE|PATH20260408001^Catholic-HIS
OBR|1|PATH20260408001^Catholic-HIS||88305^Surgical pathology^CPT|R||20260407090000|||||||20260407090000||D600200^Ryu^Da-Young^^^^^L^^^DR||||||||20260408150000|||F
OBX|1|TX|88305^Surgical pathology^CPT|1|자궁경부 생검: 만성 경부염, 악성 소견 없음.||||||F|||20260408150000
OBX|2|ED|PDF^병리보고서PDF^L|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKFBhdGhvbG9neSBSZXBvcnQpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNDAwIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNDk3CiUlRU9GCg==||||||F|||20260408150000
```

---

## 8. ADT^A08 - patient information update

```
MSH|^~\&|Catholic-HIS|이화여자대학교 목동병원|KHIS|건강보험심사평가원|20260406090000||ADT^A08^ADT_A01|CATH20260406090000008|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A08|20260406090000
PID|||PAT600100^^^이화여자대학교 목동병원^PI||Yang^Hyun-Woo^^^^^L||19720830|M|||서울특별시 양천구 목동동로 221^^양천구^서울특별시^07985^KOR^H~서울특별시 강서구 화곡로 268^^강서구^서울특별시^07549^KOR^O||^PRN^PH^^82^2^26497813~^WPN^PH^^82^2^38915427||KOR|M|||||||||||||||||||N
PV1||I|82W^8205^1^이화여자대학교 목동병원^^^^N||||D600100^Ahn^Jae-Won^^^^^L^^^DR|||IM||||||||V600100|||||||||||||||||||||||||||20260405140000
IN1|1||67823451|국민건강보험|강원도 원주시 건강로 32||||||||||||||||||||||||||||||||||||||||6
```

---

## 9. ORM^O01 - radiology order

```
MSH|^~\&|Catholic-HIS|이화여자대학교 목동병원|영상의학과|이화여자대학교 목동병원|20260402093000||ORM^O01^ORM_O01|CATH20260402093000009|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT600200^^^이화여자대학교 목동병원^PI||Go^Seo-Hyun^^^^^L||19850617|F
PV1||O|내과외래^1^1^이화여자대학교 목동병원^^^^N||||D600200^Ryu^Da-Young^^^^^L^^^DR
ORC|NW|RAD20260402001^Catholic-HIS||||||||||D600200^Ryu^Da-Young^^^^^L^^^DR
OBR|1|RAD20260402001^Catholic-HIS||71046^흉부X선 양방향^RADLEX|R||20260402093000|||||||20260402093000||D600200^Ryu^Da-Young^^^^^L^^^DR
```

---

## 10. SIU^S12 - appointment scheduled

```
MSH|^~\&|Catholic-HIS|이화여자대학교 목동병원|외래예약|이화여자대학교 목동병원|20260403150000||SIU^S12^SIU_S12|CATH20260403150000010|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
SCH|APT20260410001^Catholic-HIS|APT20260410001^Catholic-HIS|||||외래진료^외래예약^L|||||^^30^20260410090000^20260410093000
PID|||PAT600200^^^이화여자대학교 목동병원^PI||Go^Seo-Hyun^^^^^L||19850617|F
PV1||O|내과외래^1^1^이화여자대학교 목동병원^^^^N||||D600200^Ryu^Da-Young^^^^^L^^^DR
AIG|1||D600200^Ryu^Da-Young^^^^^L^^^DR
AIL|1||내과외래^1^1^이화여자대학교 목동병원
```

---

## 11. RDE^O11 - pharmacy dispense event

```
MSH|^~\&|약제부|이화여자대학교 목동병원|Catholic-HIS|이화여자대학교 목동병원|20260401140000||RDE^O11^RDE_O11|PH20260401140000011|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT600100^^^이화여자대학교 목동병원^PI||Yang^Hyun-Woo^^^^^L||19720830|M
PV1||I|71W^7108^1^이화여자대학교 목동병원^^^^N||||D600100^Ahn^Jae-Won^^^^^L^^^DR
ORC|RE|ORD20260401001^Catholic-HIS|DSP20260401001^약제부|||||||||D600100^Ahn^Jae-Won^^^^^L^^^DR
RXE|^^^20260401^^^일|652600570^아토르바스타틴정20mg^KD코드|20||mg|정|||||||30|||||||||||PH100^Shin^Eun-Hee^^^^^L^^^RPH
RXD|1|652600570^아토르바스타틴정20mg^KD코드|20260401140000|30|정||||||||||||||PH100^Shin^Eun-Hee^^^^^L^^^RPH
```

---

## 12. DFT^P03 - charge posting

```
MSH|^~\&|Catholic-HIS|이화여자대학교 목동병원|의무기록|이화여자대학교 목동병원|20260410170000||DFT^P03^DFT_P03|CATH20260410170000012|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|P03|20260410170000
PID|||PAT600200^^^이화여자대학교 목동병원^PI||Go^Seo-Hyun^^^^^L||19850617|F
PV1||O|내과외래^1^1^이화여자대학교 목동병원^^^^N||||D600200^Ryu^Da-Young^^^^^L^^^DR
FT1|1|ORD20260410001|20260410|20260410|CG|AA157^초진진찰료^수가코드||1|18600|||||||||||||||D600200^Ryu^Da-Young^^^^^L^^^DR
FT1|2|ORD20260410002|20260410|20260410|CG|C5211^일반화학검사^수가코드||1|6840|||||||||||||||D600200^Ryu^Da-Young^^^^^L^^^DR
```

---

## 13. ADT^A03 - discharge

```
MSH|^~\&|Catholic-HIS|이화여자대학교 목동병원|KHIS|건강보험심사평가원|20260412100000||ADT^A03^ADT_A03|CATH20260412100000013|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A03|20260412100000
PID|||PAT600100^^^이화여자대학교 목동병원^PI||Yang^Hyun-Woo^^^^^L||19720830|M|||서울특별시 양천구 목동동로 221^^양천구^서울특별시^07985^KOR^H||^PRN^PH^^82^2^26497813||KOR|M
PV1||I|82W^8205^1^이화여자대학교 목동병원^^^^N||||D600100^Ahn^Jae-Won^^^^^L^^^DR|||IM||||||||V600100|||||||||||||||||||||||||||20260412100000
```

---

## 14. ORU^R01 - chemistry panel result

```
MSH|^~\&|진단검사의학과|이화여자대학교 목동병원|Catholic-HIS|이화여자대학교 목동병원|20260402180000||ORU^R01^ORU_R01|LAB20260402180000014|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT600200^^^이화여자대학교 목동병원^PI||Go^Seo-Hyun^^^^^L||19850617|F
PV1||O|내과외래^1^1^이화여자대학교 목동병원^^^^N||||D600200^Ryu^Da-Young^^^^^L^^^DR
ORC|RE|LAB20260402001^Catholic-HIS||||||||||D600200^Ryu^Da-Young^^^^^L^^^DR
OBR|1|LAB20260402001^Catholic-HIS||24323-8^Comprehensive metabolic panel^LN|R||20260402100000|||||||20260402100000||D600200^Ryu^Da-Young^^^^^L^^^DR||||||||20260402180000|||F
OBX|1|NM|2951-2^Sodium [Moles/volume] in Serum or Plasma^LN||140|mmol/L|136-145|N|||F|||20260402180000
OBX|2|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN||4.2|mmol/L|3.5-5.1|N|||F|||20260402180000
OBX|3|NM|1742-6^Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||22|U/L|0-41|N|||F|||20260402180000
OBX|4|NM|1920-8^Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||28|U/L|0-40|N|||F|||20260402180000
OBX|5|NM|1751-7^Albumin [Mass/volume] in Serum or Plasma^LN||4.1|g/dL|3.5-5.2|N|||F|||20260402180000
```

---

## 15. MDM^T02 - discharge summary with embedded CDA

```
MSH|^~\&|Catholic-HIS|이화여자대학교 목동병원|KHIS|건강보험심사평가원|20260412140000||MDM^T02^MDM_T02|CATH20260412140000015|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|T02|20260412140000
PID|||PAT600100^^^이화여자대학교 목동병원^PI||Yang^Hyun-Woo^^^^^L||19720830|M
PV1||I|82W^8205^1^이화여자대학교 목동병원^^^^N||||D600100^Ahn^Jae-Won^^^^^L^^^DR
TXA|1|DS^퇴원요약^HL70270|TX|20260412140000|D600100^Ahn^Jae-Won^^^^^L^^^DR||20260412140000||||||DOC20260412001||||||AU
OBX|1|ED|DS^퇴원요약^HL70270|1|^text^xml^Base64^PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj4KICA8dGl0bGU+7LC07JuQ7JqU7JW9PC90aXRsZT4KICA8ZWZmZWN0aXZlVGltZSB2YWx1ZT0iMjAyNjA0MTIiLz4KICA8Y29tcG9uZW50PgogICAgPHN0cnVjdHVyZWRCb2R5PgogICAgICA8Y29tcG9uZW50PgogICAgICAgIDxzZWN0aW9uPgogICAgICAgICAgPHRpdGxlPuynhOuLqOuqhTwvdGl0bGU+CiAgICAgICAgICA8dGV4dD7soJzrqowg64u564u5LCDslb3rrLwg7KGw7KCI7JqUPC90ZXh0PgogICAgICAgIDwvc2VjdGlvbj4KICAgICAgPC9jb21wb25lbnQ+CiAgICA8L3N0cnVjdHVyZWRCb2R5PgogIDwvY29tcG9uZW50Pgo8L0NsaW5pY2FsRG9jdW1lbnQ+Cg==||||||F|||20260412140000
```

---

## 16. ORU^R01 - CBC result

```
MSH|^~\&|진단검사의학과|이화여자대학교 목동병원|Catholic-HIS|이화여자대학교 목동병원|20260401170000||ORU^R01^ORU_R01|LAB20260401170000016|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT600100^^^이화여자대학교 목동병원^PI||Yang^Hyun-Woo^^^^^L||19720830|M
PV1||I|71W^7108^1^이화여자대학교 목동병원^^^^N||||D600100^Ahn^Jae-Won^^^^^L^^^DR
ORC|RE|LAB20260401002^Catholic-HIS||||||||||D600100^Ahn^Jae-Won^^^^^L^^^DR
OBR|1|LAB20260401002^Catholic-HIS||58410-2^CBC panel - Blood by Automated count^LN|R||20260401103000|||||||20260401103000||D600100^Ahn^Jae-Won^^^^^L^^^DR||||||||20260401170000|||F
OBX|1|NM|6690-2^Leukocytes [#/volume] in Blood by Automated count^LN||7.2|10*3/uL|4.0-10.0|N|||F|||20260401170000
OBX|2|NM|789-8^Erythrocytes [#/volume] in Blood by Automated count^LN||4.8|10*6/uL|4.5-5.5|N|||F|||20260401170000
OBX|3|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||14.5|g/dL|13.0-17.0|N|||F|||20260401170000
OBX|4|NM|777-3^Platelets [#/volume] in Blood by Automated count^LN||245|10*3/uL|150-400|N|||F|||20260401170000
```

---

## 17. ORM^O01 - CT scan order

```
MSH|^~\&|Catholic-HIS|이화여자대학교 목동병원|영상의학과|이화여자대학교 목동병원|20260403100000||ORM^O01^ORM_O01|CATH20260403100000017|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT600100^^^이화여자대학교 목동병원^PI||Yang^Hyun-Woo^^^^^L||19720830|M
PV1||I|82W^8205^1^이화여자대학교 목동병원^^^^N||||D600100^Ahn^Jae-Won^^^^^L^^^DR
ORC|NW|RAD20260403001^Catholic-HIS||||||||||D600100^Ahn^Jae-Won^^^^^L^^^DR
OBR|1|RAD20260403001^Catholic-HIS||74177^복부CT조영^RADLEX|R||20260403100000|||||||20260403100000||D600100^Ahn^Jae-Won^^^^^L^^^DR
```

---

## 18. ORU^R01 - radiology report with embedded PDF

```
MSH|^~\&|영상의학과|이화여자대학교 목동병원|Catholic-HIS|이화여자대학교 목동병원|20260403160000||ORU^R01^ORU_R01|RAD20260403160000018|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT600100^^^이화여자대학교 목동병원^PI||Yang^Hyun-Woo^^^^^L||19720830|M
PV1||I|82W^8205^1^이화여자대학교 목동병원^^^^N||||D600100^Ahn^Jae-Won^^^^^L^^^DR
ORC|RE|RAD20260403001^Catholic-HIS
OBR|1|RAD20260403001^Catholic-HIS||74177^복부CT조영^RADLEX|R||20260403100000|||||||20260403100000||D600100^Ahn^Jae-Won^^^^^L^^^DR||||||||20260403160000|||F
OBX|1|TX|74177^복부CT조영^RADLEX|1|간, 담낭, 비장, 양측 신장 정상 소견. 췌장 두부에 1.2cm 낭성 병변 관찰됨, 추적관찰 권장.||||||F|||20260403160000
OBX|2|ED|PDF^영상판독보고서PDF^L|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKFJhZGlvbG9neSBSZXBvcnQgLSBDVCkgVGogRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZldGljYSA+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAowMDAwMDAwMzA2IDAwMDAwIG4gCjAwMDAwMDA0MDYgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo0OTcKJSVFT0YK||||||F|||20260403160000
```

---

## 19. ORM^O01 - endoscopy order

```
MSH|^~\&|Catholic-HIS|이화여자대학교 목동병원|내시경센터|이화여자대학교 목동병원|20260407080000||ORM^O01^ORM_O01|CATH20260407080000019|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT600200^^^이화여자대학교 목동병원^PI||Go^Seo-Hyun^^^^^L||19850617|F
PV1||O|내과외래^1^1^이화여자대학교 목동병원^^^^N||||D600200^Ryu^Da-Young^^^^^L^^^DR
ORC|NW|ENDO20260407001^Catholic-HIS||||||||||D600200^Ryu^Da-Young^^^^^L^^^DR
OBR|1|ENDO20260407001^Catholic-HIS||43239^상부위장관내시경^CPT|R||20260407080000|||||||20260407080000||D600200^Ryu^Da-Young^^^^^L^^^DR
```

---

## 20. ORU^R01 - urinalysis result

```
MSH|^~\&|진단검사의학과|이화여자대학교 목동병원|Catholic-HIS|이화여자대학교 목동병원|20260402190000||ORU^R01^ORU_R01|LAB20260402190000020|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT600200^^^이화여자대학교 목동병원^PI||Go^Seo-Hyun^^^^^L||19850617|F
PV1||O|내과외래^1^1^이화여자대학교 목동병원^^^^N||||D600200^Ryu^Da-Young^^^^^L^^^DR
ORC|RE|LAB20260402002^Catholic-HIS||||||||||D600200^Ryu^Da-Young^^^^^L^^^DR
OBR|1|LAB20260402002^Catholic-HIS||24356-8^Urinalysis complete panel in Urine^LN|R||20260402100000|||||||20260402100000||D600200^Ryu^Da-Young^^^^^L^^^DR||||||||20260402190000|||F
OBX|1|ST|5811-5^Specific gravity of Urine by Test strip^LN||1.020||1.005-1.030|N|||F|||20260402190000
OBX|2|NM|5803-2^pH of Urine by Test strip^LN||6.0||5.0-8.0|N|||F|||20260402190000
OBX|3|ST|5804-0^Protein [Mass/volume] in Urine by Test strip^LN||Negative||Negative|N|||F|||20260402190000
OBX|4|ST|5792-7^Glucose [Mass/volume] in Urine by Test strip^LN||Negative||Negative|N|||F|||20260402190000
OBX|5|ST|5794-3^Hemoglobin [Presence] in Urine by Test strip^LN||Negative||Negative|N|||F|||20260402190000
```
