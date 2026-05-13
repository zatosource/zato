# INFINITT PACS/RIS - real HL7v2 ER7 messages

---

## 1. ORM^O01 - chest X-ray order

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|PACS|고려대학교 안암병원|20260401083000||ORM^O01^ORM_O01|INF20260401083000001|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT700100^^^고려대학교 안암병원^PI||Lim^Jae-Sung^^^^^L||19790805|M|||서울특별시 성북구 안암로 145^^성북구^서울특별시^02841^KOR^H||^PRN^PH^^82^2^9201847||KOR|M
PV1||I|51W^5102^1^고려대학교 안암병원^^^^N||||D700100^Choi^Seung-Hwan^^^^^L^^^DR|||IM||||A|||V700100|||||||||||||||||||||||||||20260401083000
ORC|NW|RAD20260401001^INFINITT-RIS||||||||||D700100^Choi^Seung-Hwan^^^^^L^^^DR
OBR|1|RAD20260401001^INFINITT-RIS||71046^Chest X-ray 2 views^RADLEX|R||20260401083000|||||||20260401083000||D700100^Choi^Seung-Hwan^^^^^L^^^DR
```

---

## 2. ORM^O01 - abdominal CT order with contrast

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|PACS|고려대학교 안암병원|20260401100000||ORM^O01^ORM_O01|INF20260401100000002|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT700100^^^고려대학교 안암병원^PI||Lim^Jae-Sung^^^^^L||19790805|M|||서울특별시 성북구 안암로 145^^성북구^서울특별시^02841^KOR^H||^PRN^PH^^82^2^9201847||KOR|M
PV1||I|51W^5102^1^고려대학교 안암병원^^^^N||||D700100^Choi^Seung-Hwan^^^^^L^^^DR
ORC|NW|RAD20260401002^INFINITT-RIS||||||||||D700100^Choi^Seung-Hwan^^^^^L^^^DR
OBR|1|RAD20260401002^INFINITT-RIS||74178^CT Abdomen and Pelvis with contrast^RADLEX|R||20260401100000|||||||20260401100000||D700100^Choi^Seung-Hwan^^^^^L^^^DR
```

---

## 3. ORU^R01 - chest X-ray result report

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|HIS|고려대학교 안암병원|20260401110000||ORU^R01^ORU_R01|INF20260401110000003|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT700100^^^고려대학교 안암병원^PI||Lim^Jae-Sung^^^^^L||19790805|M
PV1||I|51W^5102^1^고려대학교 안암병원^^^^N||||D700100^Choi^Seung-Hwan^^^^^L^^^DR
ORC|RE|RAD20260401001^INFINITT-RIS
OBR|1|RAD20260401001^INFINITT-RIS||71046^Chest X-ray 2 views^RADLEX|R||20260401083000|||||||20260401083000||D700100^Choi^Seung-Hwan^^^^^L^^^DR||||||||20260401110000|||F
OBX|1|TX|71046^Chest X-ray 2 views^RADLEX|1|심비대 소견 없음. 양측 폐야 깨끗함. 양측 횡격막 정상. 골격 이상 소견 없음.||||||F|||20260401110000
```

---

## 4. ORU^R01 - CT abdomen result with embedded PDF report

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|HIS|고려대학교 안암병원|20260401170000||ORU^R01^ORU_R01|INF20260401170000004|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT700100^^^고려대학교 안암병원^PI||Lim^Jae-Sung^^^^^L||19790805|M
PV1||I|51W^5102^1^고려대학교 안암병원^^^^N||||D700100^Choi^Seung-Hwan^^^^^L^^^DR
ORC|RE|RAD20260401002^INFINITT-RIS
OBR|1|RAD20260401002^INFINITT-RIS||74178^CT Abdomen and Pelvis with contrast^RADLEX|R||20260401100000|||||||20260401100000||D700100^Choi^Seung-Hwan^^^^^L^^^DR||||||||20260401170000|||F
OBX|1|TX|74178^CT Abdomen and Pelvis with contrast^RADLEX|1|간 실질 균일. 담석 없음. 비장 정상 크기. 양측 신장 정상. 대동맥 석회화 경미. 복수 없음.||||||F|||20260401170000
OBX|2|ED|PDF^CT판독보고서PDF^L|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA2MiA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKENUIEFiZG9tZW4gUmVwb3J0IC0gU2V2ZXJhbmNlKSBUaiBFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAgbiAKMDAwMDAwMDQxOCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjUwOQolJUVPRgo=||||||F|||20260401170000
```

---

## 5. ADT^A01 - inpatient admission

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|KHIS|건강보험심사평가원|20260401080000||ADT^A01^ADT_A01|INF20260401080000005|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A01|20260401080000
PID|||PAT700100^^^고려대학교 안암병원^PI||Lim^Jae-Sung^^^^^L||19790805|M|||서울특별시 성북구 안암로 145^^성북구^서울특별시^02841^KOR^H||^PRN^PH^^82^2^9201847||KOR|M|||||||||||||||||||N
PV1||I|51W^5102^1^고려대학교 안암병원^^^^N||||D700100^Choi^Seung-Hwan^^^^^L^^^DR|||IM||||A|||V700100|||||||||||||||||||||||||||20260401080000
IN1|1||55998877|국민건강보험|강원도 원주시 건강로 32||||||||||||||||||||||||||||||||||||||||6
```

---

## 6. ADT^A04 - outpatient registration

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|KHIS|건강보험심사평가원|20260403080000||ADT^A04^ADT_A01|INF20260403080000006|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A04|20260403080000
PID|||PAT700200^^^고려대학교 안암병원^PI||Song^Hye-Won^^^^^L||19930214|F|||부산광역시 남구 수영로 312^^남구^부산광역시^48460^KOR^H||^PRN^PH^^82^51^6384729||KOR|S
PV1||O|영상의학과외래^1^1^고려대학교 안암병원^^^^N||||D700200^Park^Ye-Rin^^^^^L^^^DR|||RD||||A|||V700200|||||||||||||||||||||||||||20260403080000
IN1|1||33114466|국민건강보험|강원도 원주시 건강로 32||||||||||||||||||||||||||||||||||||||||8
```

---

## 7. ORM^O01 - brain MRI order

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|PACS|고려대학교 안암병원|20260403090000||ORM^O01^ORM_O01|INF20260403090000007|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT700200^^^고려대학교 안암병원^PI||Song^Hye-Won^^^^^L||19930214|F
PV1||O|영상의학과외래^1^1^고려대학교 안암병원^^^^N||||D700200^Park^Ye-Rin^^^^^L^^^DR
ORC|NW|RAD20260403001^INFINITT-RIS||||||||||D700200^Park^Ye-Rin^^^^^L^^^DR
OBR|1|RAD20260403001^INFINITT-RIS||70553^MRI Brain with and without contrast^RADLEX|R||20260403090000|||||||20260403090000||D700200^Park^Ye-Rin^^^^^L^^^DR
```

---

## 8. ORU^R01 - MRI brain result with embedded PDF

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|HIS|고려대학교 안암병원|20260403170000||ORU^R01^ORU_R01|INF20260403170000008|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT700200^^^고려대학교 안암병원^PI||Song^Hye-Won^^^^^L||19930214|F
PV1||O|영상의학과외래^1^1^고려대학교 안암병원^^^^N||||D700200^Park^Ye-Rin^^^^^L^^^DR
ORC|RE|RAD20260403001^INFINITT-RIS
OBR|1|RAD20260403001^INFINITT-RIS||70553^MRI Brain with and without contrast^RADLEX|R||20260403090000|||||||20260403090000||D700200^Park^Ye-Rin^^^^^L^^^DR||||||||20260403170000|||F
OBX|1|TX|70553^MRI Brain with and without contrast^RADLEX|1|뇌실질 정상 신호강도. 뇌실 크기 정상. 뇌간 및 소뇌 이상 소견 없음. 경미한 부비동염.||||||F|||20260403170000
OBX|2|ED|PDF^MRI판독보고서PDF^L|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1NiA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKE1SSSBCcmFpbiBSZXBvcnQgLSBTZXZlcmFuY2UpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNDEyIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTAzCiUlRU9GCg==||||||F|||20260403170000
```

---

## 9. ADT^A08 - patient information update

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|KHIS|건강보험심사평가원|20260404090000||ADT^A08^ADT_A01|INF20260404090000009|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A08|20260404090000
PID|||PAT700200^^^고려대학교 안암병원^PI||Song^Hye-Won^^^^^L||19930214|F|||부산광역시 남구 수영로 312^^남구^부산광역시^48460^KOR^H~부산광역시 해운대구 센텀중앙로 48^^해운대구^부산광역시^48058^KOR^O||^PRN^PH^^82^51^6384729~^WPN^PH^^82^10^39127458||KOR|S|||||||||||||||||||N
PV1||O|영상의학과외래^1^1^고려대학교 안암병원^^^^N||||D700200^Park^Ye-Rin^^^^^L^^^DR
```

---

## 10. ORM^O01 - mammography order

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|PACS|고려대학교 안암병원|20260405090000||ORM^O01^ORM_O01|INF20260405090000010|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT700200^^^고려대학교 안암병원^PI||Song^Hye-Won^^^^^L||19930214|F
PV1||O|영상의학과외래^1^1^고려대학교 안암병원^^^^N||||D700200^Park^Ye-Rin^^^^^L^^^DR
ORC|NW|RAD20260405001^INFINITT-RIS||||||||||D700200^Park^Ye-Rin^^^^^L^^^DR
OBR|1|RAD20260405001^INFINITT-RIS||77067^Screening mammography bilateral^RADLEX|R||20260405090000|||||||20260405090000||D700200^Park^Ye-Rin^^^^^L^^^DR
```

---

## 11. ORU^R01 - mammography result

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|HIS|고려대학교 안암병원|20260405140000||ORU^R01^ORU_R01|INF20260405140000011|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT700200^^^고려대학교 안암병원^PI||Song^Hye-Won^^^^^L||19930214|F
PV1||O|영상의학과외래^1^1^고려대학교 안암병원^^^^N||||D700200^Park^Ye-Rin^^^^^L^^^DR
ORC|RE|RAD20260405001^INFINITT-RIS
OBR|1|RAD20260405001^INFINITT-RIS||77067^Screening mammography bilateral^RADLEX|R||20260405090000|||||||20260405090000||D700200^Park^Ye-Rin^^^^^L^^^DR||||||||20260405140000|||F
OBX|1|TX|77067^Screening mammography bilateral^RADLEX|1|양측 유방 BI-RADS 1: 정상. 석회화 또는 종괴 없음.||||||F|||20260405140000
```

---

## 12. SIU^S12 - radiology appointment scheduled

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|외래예약|고려대학교 안암병원|20260402150000||SIU^S12^SIU_S12|INF20260402150000012|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
SCH|APT20260405001^INFINITT-RIS|APT20260405001^INFINITT-RIS|||||유방촬영^영상검사예약^L|||||^^20^20260405090000^20260405091000
PID|||PAT700200^^^고려대학교 안암병원^PI||Song^Hye-Won^^^^^L||19930214|F
PV1||O|영상의학과외래^1^1^고려대학교 안암병원^^^^N||||D700200^Park^Ye-Rin^^^^^L^^^DR
AIG|1||D700200^Park^Ye-Rin^^^^^L^^^DR
AIL|1||영상의학과외래^1^1^고려대학교 안암병원
```

---

## 13. ORM^O01 - lumbar spine X-ray order

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|PACS|고려대학교 안암병원|20260406093000||ORM^O01^ORM_O01|INF20260406093000013|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT700100^^^고려대학교 안암병원^PI||Lim^Jae-Sung^^^^^L||19790805|M
PV1||I|51W^5102^1^고려대학교 안암병원^^^^N||||D700100^Choi^Seung-Hwan^^^^^L^^^DR
ORC|NW|RAD20260406001^INFINITT-RIS||||||||||D700100^Choi^Seung-Hwan^^^^^L^^^DR
OBR|1|RAD20260406001^INFINITT-RIS||72100^Lumbar spine X-ray AP and lateral^RADLEX|R||20260406093000|||||||20260406093000||D700100^Choi^Seung-Hwan^^^^^L^^^DR
```

---

## 14. ORU^R01 - lumbar spine X-ray result with embedded PDF

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|HIS|고려대학교 안암병원|20260406130000||ORU^R01^ORU_R01|INF20260406130000014|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT700100^^^고려대학교 안암병원^PI||Lim^Jae-Sung^^^^^L||19790805|M
PV1||I|51W^5102^1^고려대학교 안암병원^^^^N||||D700100^Choi^Seung-Hwan^^^^^L^^^DR
ORC|RE|RAD20260406001^INFINITT-RIS
OBR|1|RAD20260406001^INFINITT-RIS||72100^Lumbar spine X-ray AP and lateral^RADLEX|R||20260406093000|||||||20260406093000||D700100^Choi^Seung-Hwan^^^^^L^^^DR||||||||20260406130000|||F
OBX|1|TX|72100^Lumbar spine X-ray AP and lateral^RADLEX|1|요추 4-5 번간 추간판 간격 감소. 경미한 골극 형성. 압박골절 소견 없음.||||||F|||20260406130000
OBX|2|ED|PDF^요추X선판독보고서PDF^L|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA2MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKEx1bWJhciBTcGluZSBYLXJheSBSZXBvcnQpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNDE2IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTA3CiUlRU9GCg==||||||F|||20260406130000
```

---

## 15. DFT^P03 - radiology charge posting

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|의무기록|고려대학교 안암병원|20260401180000||DFT^P03^DFT_P03|INF20260401180000015|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|P03|20260401180000
PID|||PAT700100^^^고려대학교 안암병원^PI||Lim^Jae-Sung^^^^^L||19790805|M
PV1||I|51W^5102^1^고려대학교 안암병원^^^^N||||D700100^Choi^Seung-Hwan^^^^^L^^^DR
FT1|1|RAD20260401001|20260401|20260401|CG|HA041^흉부X선촬영^수가코드||1|12800|||||||||||||||D700100^Choi^Seung-Hwan^^^^^L^^^DR
FT1|2|RAD20260401002|20260401|20260401|CG|HA471^복부CT조영^수가코드||1|198000|||||||||||||||D700100^Choi^Seung-Hwan^^^^^L^^^DR
```

---

## 16. ADT^A03 - discharge

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|KHIS|건강보험심사평가원|20260408100000||ADT^A03^ADT_A03|INF20260408100000016|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A03|20260408100000
PID|||PAT700100^^^고려대학교 안암병원^PI||Lim^Jae-Sung^^^^^L||19790805|M|||서울특별시 성북구 안암로 145^^성북구^서울특별시^02841^KOR^H||^PRN^PH^^82^2^9201847||KOR|M
PV1||I|51W^5102^1^고려대학교 안암병원^^^^N||||D700100^Choi^Seung-Hwan^^^^^L^^^DR|||IM||||||||V700100|||||||||||||||||||||||||||20260408100000
```

---

## 17. RDE^O11 - contrast media dispense

```
MSH|^~\&|약제부|고려대학교 안암병원|INFINITT-RIS|고려대학교 안암병원|20260401095000||RDE^O11^RDE_O11|PH20260401095000017|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT700100^^^고려대학교 안암병원^PI||Lim^Jae-Sung^^^^^L||19790805|M
PV1||I|51W^5102^1^고려대학교 안암병원^^^^N||||D700100^Choi^Seung-Hwan^^^^^L^^^DR
ORC|RE|RAD20260401002^INFINITT-RIS|DSP20260401001^약제부|||||||||D700100^Choi^Seung-Hwan^^^^^L^^^DR
RXE|^^^20260401^^^일|649300010^이오프로마이드370주^KD코드|100||mL|바이알|||||||1|||||||||||PH200^Jung^Min-Gyu^^^^^L^^^RPH
RXD|1|649300010^이오프로마이드370주^KD코드|20260401095000|100|mL||||||||||||||PH200^Jung^Min-Gyu^^^^^L^^^RPH
```

---

## 18. MDM^T02 - radiology summary document

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|KHIS|건강보험심사평가원|20260408140000||MDM^T02^MDM_T02|INF20260408140000018|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|T02|20260408140000
PID|||PAT700100^^^고려대학교 안암병원^PI||Lim^Jae-Sung^^^^^L||19790805|M
PV1||I|51W^5102^1^고려대학교 안암병원^^^^N||||D700100^Choi^Seung-Hwan^^^^^L^^^DR
TXA|1|RA^영상검사종합보고서^HL70270|TX|20260408140000|D700100^Choi^Seung-Hwan^^^^^L^^^DR||20260408140000||||||DOC20260408001||||||AU
OBX|1|TX|RA^영상검사종합보고서^HL70270|1|흉부X선: 정상. 복부CT: 대동맥 경미 석회화 외 정상. 요추X선: L4-5 추간판 간격 감소.||||||F|||20260408140000
```

---

## 19. ADT^A02 - patient transfer

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|KHIS|건강보험심사평가원|20260404140000||ADT^A02^ADT_A02|INF20260404140000019|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A02|20260404140000
PID|||PAT700100^^^고려대학교 안암병원^PI||Lim^Jae-Sung^^^^^L||19790805|M|||서울특별시 성북구 안암로 145^^성북구^서울특별시^02841^KOR^H||^PRN^PH^^82^2^9201847||KOR|M
PV1||I|72W^7203^1^고려대학교 안암병원^^^^N||||D700100^Choi^Seung-Hwan^^^^^L^^^DR|||IM||51W^5102^1^고려대학교 안암병원^^^^N|||||||V700100|||||||||||||||||||||||||||20260404140000
```

---

## 20. ORM^O01 - ultrasound abdomen order

```
MSH|^~\&|INFINITT-RIS|고려대학교 안암병원|PACS|고려대학교 안암병원|20260407100000||ORM^O01^ORM_O01|INF20260407100000020|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT700200^^^고려대학교 안암병원^PI||Song^Hye-Won^^^^^L||19930214|F
PV1||O|영상의학과외래^1^1^고려대학교 안암병원^^^^N||||D700200^Park^Ye-Rin^^^^^L^^^DR
ORC|NW|RAD20260407001^INFINITT-RIS||||||||||D700200^Park^Ye-Rin^^^^^L^^^DR
OBR|1|RAD20260407001^INFINITT-RIS||76700^Ultrasound abdomen complete^RADLEX|R||20260407100000|||||||20260407100000||D700200^Park^Ye-Rin^^^^^L^^^DR
```
