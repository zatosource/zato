# ACK LIS - real HL7v2 ER7 messages

---

## 1. OML^O33 - specimen receipt and laboratory order

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|HIS|한국중앙의학검사센터|20260401083000||OML^O33^OML_O33|ACK20260401083000001|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT1000100^^^한국중앙의학검사센터^PI||Kwon^Dong-Hyun^^^^^L||19780315|M|||대전광역시 유성구 대학로 99^^유성구^대전광역시^34134^KOR^H||^PRN^PH^^82^42^8213677||KOR|M
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
SPM|1|SPM20260401001^ACK-LIS||BLD^혈액^HL70487|||||||||||20260401083000||||한국중앙의학검사센터 본원
ORC|NW|LAB20260401001^ACK-LIS||||||||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
OBR|1|LAB20260401001^ACK-LIS||24323-8^Comprehensive metabolic panel^LN|R||20260401083000
```

---

## 2. OML^O33 - microbiology specimen order

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|HIS|한국중앙의학검사센터|20260401090000||OML^O33^OML_O33|ACK20260401090000002|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT1000200^^^한국중앙의학검사센터^PI||Bae^Su-Yeon^^^^^L||19910708|F|||대구광역시 수성구 범어로 155^^수성구^대구광역시^42188^KOR^H||^PRN^PH^^82^53^7429815||KOR|S
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000200^Noh^Eun-Seo^^^^^L^^^DR
SPM|1|SPM20260401002^ACK-LIS||UR^소변^HL70487|||||||||||20260401090000||||한국중앙의학검사센터 본원
ORC|NW|LAB20260401002^ACK-LIS||||||||||D1000200^Noh^Eun-Seo^^^^^L^^^DR
OBR|1|LAB20260401002^ACK-LIS||630-4^Bacteria identified in Urine by Culture^LN|R||20260401090000
```

---

## 3. ORU^R01 - comprehensive metabolic panel result

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|HIS|한국중앙의학검사센터|20260401160000||ORU^R01^ORU_R01|ACK20260401160000003|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT1000100^^^한국중앙의학검사센터^PI||Kwon^Dong-Hyun^^^^^L||19780315|M
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
ORC|RE|LAB20260401001^ACK-LIS||||||||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
OBR|1|LAB20260401001^ACK-LIS||24323-8^Comprehensive metabolic panel^LN|R||20260401083000|||||||20260401083000||D1000100^Moon^Ji-Hwan^^^^^L^^^DR||||||||20260401160000|||F
OBX|1|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||105|mg/dL|74-106|N|||F|||20260401160000
OBX|2|NM|2951-2^Sodium [Moles/volume] in Serum or Plasma^LN||141|mmol/L|136-145|N|||F|||20260401160000
OBX|3|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN||4.0|mmol/L|3.5-5.1|N|||F|||20260401160000
OBX|4|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||0.95|mg/dL|0.7-1.3|N|||F|||20260401160000
OBX|5|NM|1742-6^Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||35|U/L|0-41|N|||F|||20260401160000
OBX|6|NM|1920-8^Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||30|U/L|0-40|N|||F|||20260401160000
```

---

## 4. ORU^R01 - microbiology culture result

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|HIS|한국중앙의학검사센터|20260403160000||ORU^R01^ORU_R01|ACK20260403160000004|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT1000200^^^한국중앙의학검사센터^PI||Bae^Su-Yeon^^^^^L||19910708|F
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000200^Noh^Eun-Seo^^^^^L^^^DR
ORC|RE|LAB20260401002^ACK-LIS||||||||||D1000200^Noh^Eun-Seo^^^^^L^^^DR
OBR|1|LAB20260401002^ACK-LIS||630-4^Bacteria identified in Urine by Culture^LN|R||20260401090000|||||||20260401090000||D1000200^Noh^Eun-Seo^^^^^L^^^DR||||||||20260403160000|||F
OBX|1|ST|630-4^Bacteria identified in Urine by Culture^LN|1|Escherichia coli||||||F|||20260403160000
OBX|2|ST|18769-0^Ampicillin [Susceptibility] by Minimum inhibitory concentration^LN|1|R||||||F|||20260403160000
OBX|3|ST|18862-3^Amikacin [Susceptibility] by Minimum inhibitory concentration^LN|1|S||||||F|||20260403160000
OBX|4|ST|18906-8^Ciprofloxacin [Susceptibility] by Minimum inhibitory concentration^LN|1|S||||||F|||20260403160000
OBX|5|ST|18932-4^Imipenem [Susceptibility] by Minimum inhibitory concentration^LN|1|S||||||F|||20260403160000
```

---

## 5. OML^O33 - thyroid function panel order

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|HIS|한국중앙의학검사센터|20260402083000||OML^O33^OML_O33|ACK20260402083000005|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT1000200^^^한국중앙의학검사센터^PI||Bae^Su-Yeon^^^^^L||19910708|F
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000200^Noh^Eun-Seo^^^^^L^^^DR
SPM|1|SPM20260402001^ACK-LIS||BLD^혈액^HL70487|||||||||||20260402083000||||한국중앙의학검사센터 본원
ORC|NW|LAB20260402001^ACK-LIS||||||||||D1000200^Noh^Eun-Seo^^^^^L^^^DR
OBR|1|LAB20260402001^ACK-LIS||24348-5^Free T4 and TSH panel^LN|R||20260402083000
```

---

## 6. ORU^R01 - thyroid function result

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|HIS|한국중앙의학검사센터|20260402160000||ORU^R01^ORU_R01|ACK20260402160000006|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT1000200^^^한국중앙의학검사센터^PI||Bae^Su-Yeon^^^^^L||19910708|F
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000200^Noh^Eun-Seo^^^^^L^^^DR
ORC|RE|LAB20260402001^ACK-LIS||||||||||D1000200^Noh^Eun-Seo^^^^^L^^^DR
OBR|1|LAB20260402001^ACK-LIS||24348-5^Free T4 and TSH panel^LN|R||20260402083000|||||||20260402083000||D1000200^Noh^Eun-Seo^^^^^L^^^DR||||||||20260402160000|||F
OBX|1|NM|3016-3^Thyrotropin [Units/volume] in Serum or Plasma^LN||3.5|mIU/L|0.27-4.20|N|||F|||20260402160000
OBX|2|NM|3024-7^Thyroxine (T4) free [Mass/volume] in Serum or Plasma^LN||1.1|ng/dL|0.93-1.70|N|||F|||20260402160000
OBX|3|NM|3053-6^Triiodothyronine (T3) free [Mass/volume] in Serum or Plasma^LN||3.2|pg/mL|2.0-4.4|N|||F|||20260402160000
```

---

## 7. ORU^R01 - CBC with differential result

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|HIS|한국중앙의학검사센터|20260401170000||ORU^R01^ORU_R01|ACK20260401170000007|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT1000100^^^한국중앙의학검사센터^PI||Kwon^Dong-Hyun^^^^^L||19780315|M
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
ORC|RE|LAB20260401003^ACK-LIS||||||||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
OBR|1|LAB20260401003^ACK-LIS||57021-8^CBC W Auto Differential panel - Blood^LN|R||20260401083000|||||||20260401083000||D1000100^Moon^Ji-Hwan^^^^^L^^^DR||||||||20260401170000|||F
OBX|1|NM|6690-2^Leukocytes [#/volume] in Blood by Automated count^LN||6.8|10*3/uL|4.0-10.0|N|||F|||20260401170000
OBX|2|NM|789-8^Erythrocytes [#/volume] in Blood by Automated count^LN||5.1|10*6/uL|4.5-5.5|N|||F|||20260401170000
OBX|3|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||15.2|g/dL|13.0-17.0|N|||F|||20260401170000
OBX|4|NM|4544-3^Hematocrit [Volume Fraction] of Blood by Automated count^LN||45.1|%|38.0-52.0|N|||F|||20260401170000
OBX|5|NM|777-3^Platelets [#/volume] in Blood by Automated count^LN||198|10*3/uL|150-400|N|||F|||20260401170000
OBX|6|NM|770-8^Neutrophils/100 leukocytes in Blood by Automated count^LN||58|%|40-70|N|||F|||20260401170000
```

---

## 8. ADT^A04 - outpatient registration

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|KHIS|건강보험심사평가원|20260401080000||ADT^A04^ADT_A01|ACK20260401080000008|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A04|20260401080000
PID|||PAT1000100^^^한국중앙의학검사센터^PI||Kwon^Dong-Hyun^^^^^L||19780315|M|||대전광역시 유성구 대학로 99^^유성구^대전광역시^34134^KOR^H||^PRN^PH^^82^42^8213677||KOR|M
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR|||IM||||A|||V1000100|||||||||||||||||||||||||||20260401080000
IN1|1||4821573960|국민건강보험|서울특별시 마포구 염리동 168||||||||||||||||||||||||||||||||||||||||8
```

---

## 9. ADT^A01 - inpatient admission

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|KHIS|건강보험심사평가원|20260403080000||ADT^A01^ADT_A01|ACK20260403080000009|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A01|20260403080000
PID|||PAT1000200^^^한국중앙의학검사센터^PI||Bae^Su-Yeon^^^^^L||19910708|F|||대구광역시 수성구 범어로 155^^수성구^대구광역시^42188^KOR^H||^PRN^PH^^82^53^7429815||KOR|S
PV1||I|검사실^101^1^한국중앙의학검사센터^^^^N||||D1000200^Noh^Eun-Seo^^^^^L^^^DR|||IM||||A|||V1000200|||||||||||||||||||||||||||20260403080000
IN1|1||7139258046|국민건강보험|서울특별시 마포구 염리동 168||||||||||||||||||||||||||||||||||||||||8
```

---

## 10. ORU^R01 - HbA1c and lipid panel result with embedded PDF

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|HIS|한국중앙의학검사센터|20260401180000||ORU^R01^ORU_R01|ACK20260401180000010|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT1000100^^^한국중앙의학검사센터^PI||Kwon^Dong-Hyun^^^^^L||19780315|M
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
ORC|RE|LAB20260401004^ACK-LIS||||||||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
OBR|1|LAB20260401004^ACK-LIS||4548-4^HbA1c^LN|R||20260401083000|||||||20260401083000||D1000100^Moon^Ji-Hwan^^^^^L^^^DR||||||||20260401180000|||F
OBX|1|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN||6.2|%|4.0-6.0|H|||F|||20260401180000
OBX|2|NM|2093-3^Cholesterol [Mass/volume] in Serum or Plasma^LN||198|mg/dL|0-200|N|||F|||20260401180000
OBX|3|NM|2571-8^Triglyceride [Mass/volume] in Serum or Plasma^LN||145|mg/dL|0-150|N|||F|||20260401180000
OBX|4|NM|2085-9^HDL Cholesterol [Mass/volume] in Serum or Plasma^LN||52|mg/dL|40-60|N|||F|||20260401180000
OBX|5|ED|PDF^종합검사보고서PDF^L|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA2NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYXRvcnkgU3VtbWFyeSBSZXBvcnQgLSBTQ0wpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNDIwIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTExCiUlRU9GCg==||||||F|||20260401180000
```

---

## 11. OML^O33 - blood gas analysis order

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|HIS|한국중앙의학검사센터|20260403090000||OML^O33^OML_O33|ACK20260403090000011|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT1000100^^^한국중앙의학검사센터^PI||Kwon^Dong-Hyun^^^^^L||19780315|M
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
SPM|1|SPM20260403001^ACK-LIS||ABLD^동맥혈^HL70487|||||||||||20260403090000||||한국중앙의학검사센터 본원
ORC|NW|LAB20260403001^ACK-LIS||||||||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
OBR|1|LAB20260403001^ACK-LIS||24336-0^Gas panel - Arterial blood^LN|R||20260403090000
```

---

## 12. ORU^R01 - arterial blood gas result

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|HIS|한국중앙의학검사센터|20260403100000||ORU^R01^ORU_R01|ACK20260403100000012|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT1000100^^^한국중앙의학검사센터^PI||Kwon^Dong-Hyun^^^^^L||19780315|M
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
ORC|RE|LAB20260403001^ACK-LIS||||||||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
OBR|1|LAB20260403001^ACK-LIS||24336-0^Gas panel - Arterial blood^LN|R||20260403090000|||||||20260403090000||D1000100^Moon^Ji-Hwan^^^^^L^^^DR||||||||20260403100000|||F
OBX|1|NM|2744-1^pH of Arterial blood^LN||7.42||7.35-7.45|N|||F|||20260403100000
OBX|2|NM|2019-8^Carbon dioxide [Partial pressure] in Arterial blood^LN||38|mmHg|35-45|N|||F|||20260403100000
OBX|3|NM|2703-7^Oxygen [Partial pressure] in Arterial blood^LN||92|mmHg|80-100|N|||F|||20260403100000
OBX|4|NM|1960-4^Bicarbonate [Moles/volume] in Arterial blood^LN||24|mmol/L|22-26|N|||F|||20260403100000
```

---

## 13. SIU^S12 - laboratory appointment scheduled

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|외래예약|한국중앙의학검사센터|20260401140000||SIU^S12^SIU_S12|ACK20260401140000013|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
SCH|APT20260415001^ACK-LIS|APT20260415001^ACK-LIS|||||재검사^검사예약^L|||||^^15^20260415083000^20260415084500
PID|||PAT1000100^^^한국중앙의학검사센터^PI||Kwon^Dong-Hyun^^^^^L||19780315|M
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
AIG|1||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
AIL|1||외래^1^1^한국중앙의학검사센터
```

---

## 14. DFT^P03 - laboratory charge posting

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|의무기록|한국중앙의학검사센터|20260401170000||DFT^P03^DFT_P03|ACK20260401170000014|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|P03|20260401170000
PID|||PAT1000100^^^한국중앙의학검사센터^PI||Kwon^Dong-Hyun^^^^^L||19780315|M
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
FT1|1|LAB20260401001|20260401|20260401|CG|C5211^일반화학검사^수가코드||1|6840|||||||||||||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
FT1|2|LAB20260401003|20260401|20260401|CG|C5301^혈액학검사^수가코드||1|5120|||||||||||||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
FT1|3|LAB20260401004|20260401|20260401|CG|C5271^당화혈색소^수가코드||1|8900|||||||||||||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
```

---

## 15. ADT^A08 - patient information update

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|KHIS|건강보험심사평가원|20260404090000||ADT^A08^ADT_A01|ACK20260404090000015|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A08|20260404090000
PID|||PAT1000200^^^한국중앙의학검사센터^PI||Bae^Su-Yeon^^^^^L||19910708|F|||대구광역시 수성구 범어로 155^^수성구^대구광역시^42188^KOR^H~대구광역시 달서구 월배로 283^^달서구^대구광역시^42611^KOR^O||^PRN^PH^^82^53^7429815~^WPN^PH^^82^10^59274163||KOR|S|||||||||||||||||||N
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000200^Noh^Eun-Seo^^^^^L^^^DR
```

---

## 16. ORU^R01 - coagulation panel result

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|HIS|한국중앙의학검사센터|20260403170000||ORU^R01^ORU_R01|ACK20260403170000016|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT1000100^^^한국중앙의학검사센터^PI||Kwon^Dong-Hyun^^^^^L||19780315|M
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
ORC|RE|LAB20260403002^ACK-LIS||||||||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
OBR|1|LAB20260403002^ACK-LIS||5902-2^Prothrombin time (PT)^LN|R||20260403083000|||||||20260403083000||D1000100^Moon^Ji-Hwan^^^^^L^^^DR||||||||20260403170000|||F
OBX|1|NM|5902-2^Prothrombin time (PT)^LN||12.5|seconds|10.0-13.5|N|||F|||20260403170000
OBX|2|NM|6301-6^INR in Platelet poor plasma by Coagulation assay^LN||1.05||0.85-1.15|N|||F|||20260403170000
OBX|3|NM|3173-2^aPTT in Blood by Coagulation assay^LN||28|seconds|25-35|N|||F|||20260403170000
```

---

## 17. ORM^O01 - external lab referral order

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|외부검사실|한국중앙의학검사센터|20260404100000||ORM^O01^ORM_O01|ACK20260404100000017|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT1000200^^^한국중앙의학검사센터^PI||Bae^Su-Yeon^^^^^L||19910708|F
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000200^Noh^Eun-Seo^^^^^L^^^DR
ORC|NW|LAB20260404001^ACK-LIS||||||||||D1000200^Noh^Eun-Seo^^^^^L^^^DR
OBR|1|LAB20260404001^ACK-LIS||5196-1^Hepatitis B surface Ag [Presence] in Serum^LN|R||20260404100000|||||||20260404100000||D1000200^Noh^Eun-Seo^^^^^L^^^DR
```

---

## 18. MDM^T02 - quality control document with embedded PDF

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|KHIS|건강보험심사평가원|20260405140000||MDM^T02^MDM_T02|ACK20260405140000018|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|T02|20260405140000
PID|||PAT1000100^^^한국중앙의학검사센터^PI||Kwon^Dong-Hyun^^^^^L||19780315|M
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000100^Moon^Ji-Hwan^^^^^L^^^DR
TXA|1|QC^정도관리보고서^HL70270|TX|20260405140000|D1000100^Moon^Ji-Hwan^^^^^L^^^DR||20260405140000||||||DOC20260405001||||||AU
OBX|1|ED|QC^정도관리보고서^HL70270|1|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA2MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKFF1YWxpdHkgQ29udHJvbCBSZXBvcnQgLSBTQ0wpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNDE2IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTA3CiUlRU9GCg==||||||F|||20260405140000
```

---

## 19. ADT^A03 - discharge

```
MSH|^~\&|ACK-LIS|한국중앙의학검사센터|KHIS|건강보험심사평가원|20260405100000||ADT^A03^ADT_A03|ACK20260405100000019|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
EVN|A03|20260405100000
PID|||PAT1000200^^^한국중앙의학검사센터^PI||Bae^Su-Yeon^^^^^L||19910708|F|||대구광역시 수성구 범어로 155^^수성구^대구광역시^42188^KOR^H||^PRN^PH^^82^53^7429815||KOR|S
PV1||I|검사실^101^1^한국중앙의학검사센터^^^^N||||D1000200^Noh^Eun-Seo^^^^^L^^^DR|||IM||||||||V1000200|||||||||||||||||||||||||||20260405100000
```

---

## 20. RDE^O11 - antibiotic dispense

```
MSH|^~\&|약제부|한국중앙의학검사센터|ACK-LIS|한국중앙의학검사센터|20260404110000||RDE^O11^RDE_O11|PH20260404110000020|P|2.5|||AL|NE|KOR|UNICODE UTF-8|||KOR
PID|||PAT1000200^^^한국중앙의학검사센터^PI||Bae^Su-Yeon^^^^^L||19910708|F
PV1||O|외래^1^1^한국중앙의학검사센터^^^^N||||D1000200^Noh^Eun-Seo^^^^^L^^^DR
ORC|RE|ORD20260404001^ACK-LIS|DSP20260404001^약제부|||||||||D1000200^Noh^Eun-Seo^^^^^L^^^DR
RXE|^^^20260404^^^일|642100480^시프로플록사신정500mg^KD코드|500||mg|정|||||||7|||||||||||PH500^Gil^Hye-Ran^^^^^L^^^RPH
RXD|1|642100480^시프로플록사신정500mg^KD코드|20260404110000|14|정||||||||||||||PH500^Gil^Hye-Ran^^^^^L^^^RPH
```
