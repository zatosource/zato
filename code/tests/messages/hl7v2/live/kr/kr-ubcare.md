# UBcare EMR - real HL7v2 ER7 messages

---

## 1. ADT^A04 - outpatient registration

```
MSH|^~\&|UBcare-EMR|서울특별시 강남구 의료법인 미래의원|KHIS|건강보험심사평가원|20260401080000||ADT^A04^ADT_A01|UBC20260401080000001|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A04|20260401080000
PID|||PAT800100^^^미래의원^PI||Jang^Woo-Jin^^^^^L||19820307|M|||서울특별시 강남구 테헤란로 521^^강남구^서울특별시^06164^KOR^H||^PRN^PH^^82^2^5578219||KOR|M
PV1||O|내과^1^1^미래의원^^^^N||||D800100^Lee^Chang-Ho^^^^^L^^^DR|||IM||||A|||V800100|||||||||||||||||||||||||||20260401080000
IN1|1||78563412|국민건강보험|강원도 원주시 건강로 32||||||||||||||||||||||||||||||||||||||||8
```

---

## 2. ADT^A04 - outpatient registration for patient 2

```
MSH|^~\&|UBcare-EMR|서울특별시 강남구 의료법인 미래의원|KHIS|건강보험심사평가원|20260401083000||ADT^A04^ADT_A01|UBC20260401083000002|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A04|20260401083000
PID|||PAT800200^^^미래의원^PI||Na^Hye-Soo^^^^^L||19970416|F|||서울특별시 서초구 서초대로 397^^서초구^서울특별시^06616^KOR^H||^PRN^PH^^82^2^5381467||KOR|S
PV1||O|가정의학과^1^1^미래의원^^^^N||||D800200^Kim^Ye-Na^^^^^L^^^DR|||FM||||A|||V800200|||||||||||||||||||||||||||20260401083000
IN1|1||21436587|국민건강보험|강원도 원주시 건강로 32||||||||||||||||||||||||||||||||||||||||8
```

---

## 3. ORM^O01 - pharmacy order for hypertension

```
MSH|^~\&|UBcare-EMR|서울특별시 강남구 의료법인 미래의원|약국|미래의원|20260401090000||ORM^O01^ORM_O01|UBC20260401090000003|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT800100^^^미래의원^PI||Jang^Woo-Jin^^^^^L||19820307|M
PV1||O|내과^1^1^미래의원^^^^N||||D800100^Lee^Chang-Ho^^^^^L^^^DR
ORC|NW|ORD20260401001^UBcare-EMR||||||||||D800100^Lee^Chang-Ho^^^^^L^^^DR
RXO|657200840^암로디핀정5mg^KD코드|||5||mg||PO^경구^HL70162|||||||||||||||D800100^Lee^Chang-Ho^^^^^L^^^DR
```

---

## 4. OML^O33 - laboratory order for health screening

```
MSH|^~\&|UBcare-EMR|서울특별시 강남구 의료법인 미래의원|진단검사|미래의원|20260401091000||OML^O33^OML_O33|UBC20260401091000004|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT800100^^^미래의원^PI||Jang^Woo-Jin^^^^^L||19820307|M
PV1||O|내과^1^1^미래의원^^^^N||||D800100^Lee^Chang-Ho^^^^^L^^^DR
SPM|1|||BLD^혈액^HL70487|||||||||||20260401091000
ORC|NW|LAB20260401001^UBcare-EMR||||||||||D800100^Lee^Chang-Ho^^^^^L^^^DR
OBR|1|LAB20260401001^UBcare-EMR||24323-8^Comprehensive metabolic panel^LN|R||20260401091000
```

---

## 5. ORU^R01 - health screening laboratory results

```
MSH|^~\&|진단검사|서울특별시 강남구 의료법인 미래의원|UBcare-EMR|미래의원|20260401150000||ORU^R01^ORU_R01|LAB20260401150000005|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT800100^^^미래의원^PI||Jang^Woo-Jin^^^^^L||19820307|M
PV1||O|내과^1^1^미래의원^^^^N||||D800100^Lee^Chang-Ho^^^^^L^^^DR
ORC|RE|LAB20260401001^UBcare-EMR||||||||||D800100^Lee^Chang-Ho^^^^^L^^^DR
OBR|1|LAB20260401001^UBcare-EMR||24323-8^Comprehensive metabolic panel^LN|R||20260401091000|||||||20260401091000||D800100^Lee^Chang-Ho^^^^^L^^^DR||||||||20260401150000|||F
OBX|1|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||98|mg/dL|74-106|N|||F|||20260401150000
OBX|2|NM|2093-3^Cholesterol [Mass/volume] in Serum or Plasma^LN||215|mg/dL|0-200|H|||F|||20260401150000
OBX|3|NM|2571-8^Triglyceride [Mass/volume] in Serum or Plasma^LN||168|mg/dL|0-150|H|||F|||20260401150000
OBX|4|NM|2085-9^HDL Cholesterol [Mass/volume] in Serum or Plasma^LN||48|mg/dL|40-60|N|||F|||20260401150000
OBX|5|NM|13457-7^LDL Cholesterol [Mass/volume] in Serum or Plasma^LN||134|mg/dL|0-130|H|||F|||20260401150000
```

---

## 6. ORU^R01 - thyroid function test result with embedded PDF

```
MSH|^~\&|진단검사|서울특별시 강남구 의료법인 미래의원|UBcare-EMR|미래의원|20260402160000||ORU^R01^ORU_R01|LAB20260402160000006|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT800200^^^미래의원^PI||Na^Hye-Soo^^^^^L||19970416|F
PV1||O|가정의학과^1^1^미래의원^^^^N||||D800200^Kim^Ye-Na^^^^^L^^^DR
ORC|RE|LAB20260402001^UBcare-EMR||||||||||D800200^Kim^Ye-Na^^^^^L^^^DR
OBR|1|LAB20260402001^UBcare-EMR||24348-5^Free T4 and TSH panel^LN|R||20260402090000|||||||20260402090000||D800200^Kim^Ye-Na^^^^^L^^^DR||||||||20260402160000|||F
OBX|1|NM|3016-3^Thyrotropin [Units/volume] in Serum or Plasma^LN||2.8|mIU/L|0.27-4.20|N|||F|||20260402160000
OBX|2|NM|3024-7^Thyroxine (T4) free [Mass/volume] in Serum or Plasma^LN||1.2|ng/dL|0.93-1.70|N|||F|||20260402160000
OBX|3|ED|PDF^갑상선기능검사보고서PDF^L|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1OCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKFRoeXJvaWQgRnVuY3Rpb24gVGVzdCBSZXBvcnQpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNDE0IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTA1CiUlRU9GCg==||||||F|||20260402160000
```

---

## 7. ADT^A08 - patient information update

```
MSH|^~\&|UBcare-EMR|서울특별시 강남구 의료법인 미래의원|KHIS|건강보험심사평가원|20260403090000||ADT^A08^ADT_A01|UBC20260403090000007|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A08|20260403090000
PID|||PAT800100^^^미래의원^PI||Jang^Woo-Jin^^^^^L||19820307|M|||서울특별시 강남구 테헤란로 521^^강남구^서울특별시^06164^KOR^H~서울특별시 송파구 올림픽로 300^^송파구^서울특별시^05551^KOR^O||^PRN^PH^^82^2^5578219~^WPN^PH^^82^10^59273841||KOR|M|||||||||||||||||||N
PV1||O|내과^1^1^미래의원^^^^N||||D800100^Lee^Chang-Ho^^^^^L^^^DR
```

---

## 8. ORM^O01 - referral radiology order

```
MSH|^~\&|UBcare-EMR|서울특별시 강남구 의료법인 미래의원|영상센터|미래의원|20260403100000||ORM^O01^ORM_O01|UBC20260403100000008|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT800100^^^미래의원^PI||Jang^Woo-Jin^^^^^L||19820307|M
PV1||O|내과^1^1^미래의원^^^^N||||D800100^Lee^Chang-Ho^^^^^L^^^DR
ORC|NW|RAD20260403001^UBcare-EMR||||||||||D800100^Lee^Chang-Ho^^^^^L^^^DR
OBR|1|RAD20260403001^UBcare-EMR||71046^Chest X-ray 2 views^RADLEX|R||20260403100000|||||||20260403100000||D800100^Lee^Chang-Ho^^^^^L^^^DR
```

---

## 9. SIU^S12 - follow-up appointment scheduled

```
MSH|^~\&|UBcare-EMR|서울특별시 강남구 의료법인 미래의원|외래예약|미래의원|20260401140000||SIU^S12^SIU_S12|UBC20260401140000009|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
SCH|APT20260415001^UBcare-EMR|APT20260415001^UBcare-EMR|||||재진^외래예약^L|||||^^15^20260415100000^20260415101500
PID|||PAT800100^^^미래의원^PI||Jang^Woo-Jin^^^^^L||19820307|M
PV1||O|내과^1^1^미래의원^^^^N||||D800100^Lee^Chang-Ho^^^^^L^^^DR
AIG|1||D800100^Lee^Chang-Ho^^^^^L^^^DR
AIL|1||내과^1^1^미래의원
```

---

## 10. RDE^O11 - pharmacy dispense for hypertension medication

```
MSH|^~\&|약국|서울특별시 강남구 의료법인 미래의원|UBcare-EMR|미래의원|20260401110000||RDE^O11^RDE_O11|PH20260401110000010|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT800100^^^미래의원^PI||Jang^Woo-Jin^^^^^L||19820307|M
PV1||O|내과^1^1^미래의원^^^^N||||D800100^Lee^Chang-Ho^^^^^L^^^DR
ORC|RE|ORD20260401001^UBcare-EMR|DSP20260401001^약국|||||||||D800100^Lee^Chang-Ho^^^^^L^^^DR
RXE|^^^20260401^^^일|657200840^암로디핀정5mg^KD코드|5||mg|정|||||||30|||||||||||PH300^Choi^Ji-Hwan^^^^^L^^^RPH
RXD|1|657200840^암로디핀정5mg^KD코드|20260401110000|30|정||||||||||||||PH300^Choi^Ji-Hwan^^^^^L^^^RPH
```

---

## 11. DFT^P03 - outpatient visit charge posting

```
MSH|^~\&|UBcare-EMR|서울특별시 강남구 의료법인 미래의원|의무기록|미래의원|20260401170000||DFT^P03^DFT_P03|UBC20260401170000011|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|P03|20260401170000
PID|||PAT800100^^^미래의원^PI||Jang^Woo-Jin^^^^^L||19820307|M
PV1||O|내과^1^1^미래의원^^^^N||||D800100^Lee^Chang-Ho^^^^^L^^^DR
FT1|1|ORD20260401010|20260401|20260401|CG|AA200^재진진찰료^수가코드||1|12100|||||||||||||||D800100^Lee^Chang-Ho^^^^^L^^^DR
FT1|2|ORD20260401011|20260401|20260401|CG|C5211^일반화학검사^수가코드||1|6840|||||||||||||||D800100^Lee^Chang-Ho^^^^^L^^^DR
FT1|3|ORD20260401012|20260401|20260401|CG|BB101^처방료^수가코드||1|4200|||||||||||||||D800100^Lee^Chang-Ho^^^^^L^^^DR
```

---

## 12. ORM^O01 - influenza vaccination order

```
MSH|^~\&|UBcare-EMR|서울특별시 강남구 의료법인 미래의원|예방접종|미래의원|20260403090000||ORM^O01^ORM_O01|UBC20260403090000012|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT800200^^^미래의원^PI||Na^Hye-Soo^^^^^L||19970416|F
PV1||O|가정의학과^1^1^미래의원^^^^N||||D800200^Kim^Ye-Na^^^^^L^^^DR
ORC|NW|VAX20260403001^UBcare-EMR||||||||||D800200^Kim^Ye-Na^^^^^L^^^DR
RXO|670500120^인플루엔자백신^KD코드|||0.5||mL||IM^근육주사^HL70162|||||||||||||||D800200^Kim^Ye-Na^^^^^L^^^DR
```

---

## 13. ORU^R01 - CBC result

```
MSH|^~\&|진단검사|서울특별시 강남구 의료법인 미래의원|UBcare-EMR|미래의원|20260402170000||ORU^R01^ORU_R01|LAB20260402170000013|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT800200^^^미래의원^PI||Na^Hye-Soo^^^^^L||19970416|F
PV1||O|가정의학과^1^1^미래의원^^^^N||||D800200^Kim^Ye-Na^^^^^L^^^DR
ORC|RE|LAB20260402002^UBcare-EMR||||||||||D800200^Kim^Ye-Na^^^^^L^^^DR
OBR|1|LAB20260402002^UBcare-EMR||58410-2^CBC panel - Blood by Automated count^LN|R||20260402090000|||||||20260402090000||D800200^Kim^Ye-Na^^^^^L^^^DR||||||||20260402170000|||F
OBX|1|NM|6690-2^Leukocytes [#/volume] in Blood by Automated count^LN||5.8|10*3/uL|4.0-10.0|N|||F|||20260402170000
OBX|2|NM|789-8^Erythrocytes [#/volume] in Blood by Automated count^LN||4.3|10*6/uL|3.8-5.1|N|||F|||20260402170000
OBX|3|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||12.8|g/dL|12.0-16.0|N|||F|||20260402170000
OBX|4|NM|777-3^Platelets [#/volume] in Blood by Automated count^LN||278|10*3/uL|150-400|N|||F|||20260402170000
```

---

## 14. MDM^T02 - health screening summary with embedded PDF

```
MSH|^~\&|UBcare-EMR|서울특별시 강남구 의료법인 미래의원|KHIS|건강보험심사평가원|20260403140000||MDM^T02^MDM_T02|UBC20260403140000014|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|T02|20260403140000
PID|||PAT800100^^^미래의원^PI||Jang^Woo-Jin^^^^^L||19820307|M
PV1||O|내과^1^1^미래의원^^^^N||||D800100^Lee^Chang-Ho^^^^^L^^^DR
TXA|1|HP^건강검진결과보고서^HL70270|TX|20260403140000|D800100^Lee^Chang-Ho^^^^^L^^^DR||20260403140000||||||DOC20260403001||||||AU
OBX|1|ED|HP^건강검진결과보고서^HL70270|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA2MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKEhlYWx0aCBTY3JlZW5pbmcgUmVwb3J0IC0gTWlyYWUpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNDE2IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTA3CiUlRU9GCg==||||||F|||20260403140000
```

---

## 15. ADT^A01 - inpatient admission for minor procedure

```
MSH|^~\&|UBcare-EMR|서울특별시 강남구 의료법인 미래의원|KHIS|건강보험심사평가원|20260405080000||ADT^A01^ADT_A01|UBC20260405080000015|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A01|20260405080000
PID|||PAT800200^^^미래의원^PI||Na^Hye-Soo^^^^^L||19970416|F|||서울특별시 서초구 서초대로 397^^서초구^서울특별시^06616^KOR^H||^PRN^PH^^82^2^5381467||KOR|S
PV1||I|병실^201^1^미래의원^^^^N||||D800200^Kim^Ye-Na^^^^^L^^^DR|||GS||||A|||V800200|||||||||||||||||||||||||||20260405080000
IN1|1||21436587|국민건강보험|강원도 원주시 건강로 32||||||||||||||||||||||||||||||||||||||||8
```

---

## 16. ADT^A03 - discharge after minor procedure

```
MSH|^~\&|UBcare-EMR|서울특별시 강남구 의료법인 미래의원|KHIS|건강보험심사평가원|20260405170000||ADT^A03^ADT_A03|UBC20260405170000016|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A03|20260405170000
PID|||PAT800200^^^미래의원^PI||Na^Hye-Soo^^^^^L||19970416|F|||서울특별시 서초구 서초대로 397^^서초구^서울특별시^06616^KOR^H||^PRN^PH^^82^2^5381467||KOR|S
PV1||I|병실^201^1^미래의원^^^^N||||D800200^Kim^Ye-Na^^^^^L^^^DR|||GS||||||||V800200|||||||||||||||||||||||||||20260405170000
```

---

## 17. ORM^O01 - prescription order for cold symptoms

```
MSH|^~\&|UBcare-EMR|서울특별시 강남구 의료법인 미래의원|약국|미래의원|20260407090000||ORM^O01^ORM_O01|UBC20260407090000017|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT800200^^^미래의원^PI||Na^Hye-Soo^^^^^L||19970416|F
PV1||O|가정의학과^1^1^미래의원^^^^N||||D800200^Kim^Ye-Na^^^^^L^^^DR
ORC|NW|ORD20260407001^UBcare-EMR||||||||||D800200^Kim^Ye-Na^^^^^L^^^DR
RXO|645300080^타이레놀정500mg^KD코드|||500||mg||PO^경구^HL70162|||||||||||||||D800200^Kim^Ye-Na^^^^^L^^^DR
```

---

## 18. ORU^R01 - HbA1c follow-up result

```
MSH|^~\&|진단검사|서울특별시 강남구 의료법인 미래의원|UBcare-EMR|미래의원|20260415160000||ORU^R01^ORU_R01|LAB20260415160000018|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT800100^^^미래의원^PI||Jang^Woo-Jin^^^^^L||19820307|M
PV1||O|내과^1^1^미래의원^^^^N||||D800100^Lee^Chang-Ho^^^^^L^^^DR
ORC|RE|LAB20260415001^UBcare-EMR||||||||||D800100^Lee^Chang-Ho^^^^^L^^^DR
OBR|1|LAB20260415001^UBcare-EMR||4548-4^HbA1c^LN|R||20260415100000|||||||20260415100000||D800100^Lee^Chang-Ho^^^^^L^^^DR||||||||20260415160000|||F
OBX|1|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN||5.6|%|4.0-6.0|N|||F|||20260415160000
OBX|2|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||92|mg/dL|74-106|N|||F|||20260415160000
```

---

## 19. SIU^S12 - annual check-up appointment

```
MSH|^~\&|UBcare-EMR|서울특별시 강남구 의료법인 미래의원|외래예약|미래의원|20260407150000||SIU^S12^SIU_S12|UBC20260407150000019|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
SCH|APT20260501001^UBcare-EMR|APT20260501001^UBcare-EMR|||||연간건강검진^외래예약^L|||||^^30^20260501090000^20260501093000
PID|||PAT800200^^^미래의원^PI||Na^Hye-Soo^^^^^L||19970416|F
PV1||O|가정의학과^1^1^미래의원^^^^N||||D800200^Kim^Ye-Na^^^^^L^^^DR
AIG|1||D800200^Kim^Ye-Na^^^^^L^^^DR
AIL|1||가정의학과^1^1^미래의원
```

---

## 20. ORU^R01 - urinalysis result

```
MSH|^~\&|진단검사|서울특별시 강남구 의료법인 미래의원|UBcare-EMR|미래의원|20260401160000||ORU^R01^ORU_R01|LAB20260401160000020|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT800200^^^미래의원^PI||Na^Hye-Soo^^^^^L||19970416|F
PV1||O|가정의학과^1^1^미래의원^^^^N||||D800200^Kim^Ye-Na^^^^^L^^^DR
ORC|RE|LAB20260401002^UBcare-EMR||||||||||D800200^Kim^Ye-Na^^^^^L^^^DR
OBR|1|LAB20260401002^UBcare-EMR||24356-8^Urinalysis complete panel in Urine^LN|R||20260401090000|||||||20260401090000||D800200^Kim^Ye-Na^^^^^L^^^DR||||||||20260401160000|||F
OBX|1|ST|5811-5^Specific gravity of Urine by Test strip^LN||1.018||1.005-1.030|N|||F|||20260401160000
OBX|2|NM|5803-2^pH of Urine by Test strip^LN||6.5||5.0-8.0|N|||F|||20260401160000
OBX|3|ST|5804-0^Protein [Mass/volume] in Urine by Test strip^LN||Negative||Negative|N|||F|||20260401160000
OBX|4|ST|5792-7^Glucose [Mass/volume] in Urine by Test strip^LN||Negative||Negative|N|||F|||20260401160000
```
