# SYSPOWER Agile HIS - real HL7v2 ER7 messages

---

## 1. ADT^A01 - 住院登記 (inpatient admission) with NHI insurance

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|EMR-EXCHANGE|MOHW-EMR|20260509080000||ADT^A01^ADT_A01|CMUH20260509080001|P|2.5|||AL|NE||BIG5|zh-TW
EVN|A01|20260509080000
PID|||PAT200100^^^中國醫藥大學附設醫院^PI||傅^鎮宇^^^先生||19751108|M|||台中市南屯區公益路二段51號^^台中市^^40867^TW||^^PH^04-23861234~^^CP^0921345678||zh-TW|M|||C213678945^^^ROC^NNT
PV1||I|心臟內科^801^A^中國醫藥大學附設醫院||||D200100^鍾雅慧^^^醫師||||||||||VN20260509001|||||||||||||||||||||||||||20260509080000
IN1|1|NHI001|BNHI|全民健康保險|濟南路一段4-1號^^台北市^^10041^TW||02-21912006||||||||||傅^鎮宇|Self|19751108|台中市南屯區公益路二段51號^^台中市^^40867^TW
```

---

## 2. ADT^A04 - 門診報到 (outpatient registration)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|EMR-EXCHANGE|MOHW-EMR|20260509093000||ADT^A04^ADT_A01|CMUH20260509093001|P|2.5|||AL|NE||BIG5|zh-TW
EVN|A04|20260509093000
PID|||PAT200200^^^中國醫藥大學附設醫院^PI||簡^佩芸^^^女士||19900214|F|||台中市西屯區文心路二段281號^^台中市^^40758^TW||^^PH^04-24521234~^^CP^0964567890||zh-TW|S|||D324789056^^^ROC^NNT
PV1||O|新陳代謝科門診^診間12^^中國醫藥大學附設醫院||||D200200^葛明志^^^醫師||||||||||VN20260509002|||||||||||||||||||||||||||20260509093000
IN1|1|NHI001|BNHI|全民健康保險|濟南路一段4-1號^^台北市^^10041^TW||02-21912006
```

---

## 3. ADT^A03 - 出院通知 (discharge)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|EMR-EXCHANGE|MOHW-EMR|20260516100000||ADT^A03^ADT_A03|CMUH20260516100001|P|2.5|||AL|NE||BIG5|zh-TW
EVN|A03|20260516100000
PID|||PAT200100^^^中國醫藥大學附設醫院^PI||傅^鎮宇^^^先生||19751108|M|||台中市南屯區公益路二段51號^^台中市^^40867^TW||^^PH^04-23861234~^^CP^0921345678||zh-TW|M|||C213678945^^^ROC^NNT
PV1||I|心臟內科^801^A^中國醫藥大學附設醫院||||D200100^鍾雅慧^^^醫師||||||||||VN20260509001||||||||||||||||||||9||||20260516100000
DG1|1||I25.1^動脈粥樣硬化性心臟病^ICD-10-CM||20260509|F
```

---

## 4. ADT^A08 - 病患資料更新 (patient update)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|EMR-EXCHANGE|MOHW-EMR|20260510110000||ADT^A08^ADT_A01|CMUH20260510110001|P|2.5|||AL|NE||BIG5|zh-TW
EVN|A08|20260510110000
PID|||PAT200200^^^中國醫藥大學附設醫院^PI||簡^佩芸^^^女士||19900214|F|||台中市西屯區文心路二段281號^^台中市^^40758^TW||^^PH^04-24521234~^^CP^0964567890||zh-TW|S|||D324789056^^^ROC^NNT
PV1||O|新陳代謝科門診^診間12^^中國醫藥大學附設醫院||||D200200^葛明志^^^醫師||||||||||VN20260509002|||||||||||||||||||||||||||20260510110000
```

---

## 5. ADT^A02 - 轉床通知 (patient transfer)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|EMR-EXCHANGE|MOHW-EMR|20260512070000||ADT^A02^ADT_A02|CMUH20260512070001|P|2.5|||AL|NE||BIG5|zh-TW
EVN|A02|20260512070000
PID|||PAT200100^^^中國醫藥大學附設醫院^PI||傅^鎮宇^^^先生||19751108|M|||台中市南屯區公益路二段51號^^台中市^^40867^TW||^^PH^04-23861234~^^CP^0921345678||zh-TW|M|||C213678945^^^ROC^NNT
PV1||I|加護病房^ICU02^A^中國醫藥大學附設醫院||||D200100^鍾雅慧^^^醫師||||||||||VN20260509001||||||||||||||||||心臟內科^801^A^中國醫藥大學附設醫院||||20260512070000
```

---

## 6. ORM^O01 - 藥局處方開立 (pharmacy order)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|PHARMACY|中國醫藥大學附設醫院|20260509084500||ORM^O01^ORM_O01|CMUH20260509084501|P|2.5|||AL|NE||BIG5|zh-TW
PID|||PAT200100^^^中國醫藥大學附設醫院^PI||傅^鎮宇^^^先生||19751108|M|||台中市南屯區公益路二段51號^^台中市^^40867^TW
PV1||I|心臟內科^801^A^中國醫藥大學附設醫院||||D200100^鍾雅慧^^^醫師
ORC|NW|ORD20260509010|||||^^^20260509084500^^R||20260509084500|N200100^護理師馮小雲|||D200100^鍾雅慧^^^醫師
RXO|B024184100^Aspirin 100mg^NHI||100|mg|PO^口服^HL70162||^^^20260509^^QD|||||||D200100^鍾雅慧
RXR|PO^口服^HL70162
ORC|NW|ORD20260509011|||||^^^20260509084500^^R||20260509084500|N200100^護理師馮小雲|||D200100^鍾雅慧^^^醫師
RXO|C09CA01^Losartan 50mg^NHI||50|mg|PO^口服^HL70162||^^^20260509^^QD|||||||D200100^鍾雅慧
RXR|PO^口服^HL70162
ORC|NW|ORD20260509012|||||^^^20260509084500^^R||20260509084500|N200100^護理師馮小雲|||D200100^鍾雅慧^^^醫師
RXO|C10AA05^Atorvastatin 20mg^NHI||20|mg|PO^口服^HL70162||^^^20260509^^QD-HS|||||||D200100^鍾雅慧
RXR|PO^口服^HL70162
```

---

## 7. ORM^O01 - 放射檢查醫囑 (radiology order)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|RADIOLOGY|中國醫藥大學附設醫院|20260509100000||ORM^O01^ORM_O01|CMUH20260509100001|P|2.5|||AL|NE||BIG5|zh-TW
PID|||PAT200100^^^中國醫藥大學附設醫院^PI||傅^鎮宇^^^先生||19751108|M|||台中市南屯區公益路二段51號^^台中市^^40867^TW
PV1||I|心臟內科^801^A^中國醫藥大學附設醫院||||D200100^鍾雅慧^^^醫師
ORC|NW|RAD20260509010|||||^^^20260509100000^^R||20260509100000|||D200100^鍾雅慧^^^醫師
OBR|1|RAD20260509010||75571-7^心臟電腦斷層造影^LN|||20260509100000||||||||D200100^鍾雅慧^^^醫師||||||||||^ROUTINE
```

---

## 8. ORU^R01 - 實驗室檢驗報告 (lab results - cardiac markers)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|LAB|中國醫藥大學附設醫院|20260509120000||ORU^R01^ORU_R01|CMUH20260509120001|P|2.5|||AL|NE||BIG5|zh-TW
PID|||PAT200100^^^中國醫藥大學附設醫院^PI||傅^鎮宇^^^先生||19751108|M|||台中市南屯區公益路二段51號^^台中市^^40867^TW
PV1||I|心臟內科^801^A^中國醫藥大學附設醫院||||D200100^鍾雅慧^^^醫師
ORC|RE|LAB20260509010||||||||||D200100^鍾雅慧^^^醫師
OBR|1|LAB20260509010||89579-7^心臟標記檢查^LN|||20260509081000|||||||20260509081000|血液^Blood|D200100^鍾雅慧^^^醫師
OBX|1|NM|6598-7^肌鈣蛋白-I^LN||0.04|ng/mL|0.00-0.04||||F|||20260509120000
OBX|2|NM|49563-0^CK-MB質量^LN||3.2|ng/mL|0.0-5.0||||F|||20260509120000
OBX|3|NM|33762-6^NT-proBNP^LN||450|pg/mL|0-125|H|||F|||20260509120000
OBX|4|NM|30522-7^C反應蛋白(高敏感)^LN||2.8|mg/L|0.0-3.0||||F|||20260509120000
OBX|5|NM|2093-3^總膽固醇^LN||228|mg/dL|0-200|H|||F|||20260509120000
OBX|6|NM|2089-1^LDL膽固醇^LN||152|mg/dL|0-130|H|||F|||20260509120000
```

---

## 9. ORU^R01 - 糖化血色素報告 (HbA1c results)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|LAB|中國醫藥大學附設醫院|20260509150000||ORU^R01^ORU_R01|CMUH20260509150001|P|2.5|||AL|NE||BIG5|zh-TW
PID|||PAT200200^^^中國醫藥大學附設醫院^PI||簡^佩芸^^^女士||19900214|F|||台中市西屯區文心路二段281號^^台中市^^40758^TW
PV1||O|新陳代謝科門診^診間12^^中國醫藥大學附設醫院||||D200200^葛明志^^^醫師
ORC|RE|LAB20260509020||||||||||D200200^葛明志^^^醫師
OBR|1|LAB20260509020||4548-4^糖化血色素^LN|||20260509093500|||||||20260509093500|血液^Blood|D200200^葛明志^^^醫師
OBX|1|NM|4548-4^糖化血色素(HbA1c)^LN||7.2|%|4.0-5.6|H|||F|||20260509150000
OBX|2|NM|2345-7^空腹血糖^LN||145|mg/dL|70-100|H|||F|||20260509150000
OBX|3|NM|14749-6^葡萄糖(飯後2小時)^LN||198|mg/dL|70-140|H|||F|||20260509150000
```

---

## 10. ORU^R01 - 心臟超音波報告含嵌入PDF (echocardiography with embedded PDF)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|CARDIOLOGY|中國醫藥大學附設醫院|20260510160000||ORU^R01^ORU_R01|CMUH20260510160001|P|2.5|||AL|NE||BIG5|zh-TW
PID|||PAT200100^^^中國醫藥大學附設醫院^PI||傅^鎮宇^^^先生||19751108|M|||台中市南屯區公益路二段51號^^台中市^^40867^TW
PV1||I|心臟內科^801^A^中國醫藥大學附設醫院||||D200100^鍾雅慧^^^醫師
ORC|RE|ECHO20260510001||||||||||D200100^鍾雅慧^^^醫師
OBR|1|ECHO20260510001||34552-0^心臟超音波^LN|||20260510140000|||||||20260510140000||D200100^鍾雅慧^^^醫師||||||||F
OBX|1|NM|10230-1^左心室射出率^LN||55|%|55-70||||F|||20260510160000
OBX|2|NM|29468-6^左心室舒張末徑^LN||52|mm|36-56||||F|||20260510160000
OBX|3|FT|34552-0^心臟超音波結論^LN||左心室大小及功能正常, LVEF 55%。瓣膜無明顯異常。主動脈根部正常。無心包膜積液。||||||F|||20260510160000
OBX|4|ED|PDF^心臟超音波報告PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAzMDAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo5b+D6Ie96LaF6Z+z5rOi5aCx5ZGKIC0g5Lit5ZyL6Yar6Jed5aSn5a246ZmE6Kit6Yar6ZmiKSBUagowIC0yMCBUZAooTFZFRjogNTUlLCDlt6blv4PlrqTlip/og73mraPluLgpIFRqCjAgLTIwIFRkCijnk6PohJznhKHmmI7poa/nlbDluLgpIFRqCjAgLTIwIFRkCijkuLvli5Xohoh+mariueato+W4uCkgVGoKMCAtMjAgVGQKKOeEoeW/g+WMheiGnOepjea2sikgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAowMDAwMDAwMjY2IDAwMDAwIG4gCjAwMDAwMDA2MTYgMDAwMDAgbiAKdHJhaWxlcgo8PAovU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgo2ODEKJSVFT0YK||||||F|||20260510160000
```

---

## 11. RDE^O11 - 門診處方調劑 (outpatient prescription dispense)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|PHARMACY|中國醫藥大學附設醫院|20260509095500||RDE^O11^RDE_O11|CMUH20260509095501|P|2.5|||AL|NE||BIG5|zh-TW
PID|||PAT200200^^^中國醫藥大學附設醫院^PI||簡^佩芸^^^女士||19900214|F|||台中市西屯區文心路二段281號^^台中市^^40758^TW
PV1||O|新陳代謝科門診^診間12^^中國醫藥大學附設醫院||||D200200^葛明志^^^醫師
ORC|NW|RX20260509010|||||^^^20260509095500^^R||20260509095500|||D200200^葛明志^^^醫師
RXE|^^^20260509^^BID^90^Day||A10BA02^Metformin 850mg^NHI|850|mg||||||||||||||||||||2|Tab
RXR|PO^口服^HL70162
ORC|NW|RX20260509011|||||^^^20260509095500^^R||20260509095500|||D200200^葛明志^^^醫師
RXE|^^^20260509^^QD^90^Day||A10BH01^Sitagliptin 100mg^NHI|100|mg||||||||||||||||||||1|Tab
RXR|PO^口服^HL70162
```

---

## 12. SIU^S12 - 門診預約排程 (appointment scheduling)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|SCHEDULING|中國醫藥大學附設醫院|20260509161000||SIU^S12^SIU_S12|CMUH20260509161001|P|2.5|||AL|NE||BIG5|zh-TW
SCH|APT20260523001||||||||15|min|^^15^20260523100000^20260523101500||D200200^葛明志^^^醫師|^^PH^04-24521234|台中市西屯區文心路二段281號^^台中市^^40758^TW|D200200^葛明志^^^醫師
PID|||PAT200200^^^中國醫藥大學附設醫院^PI||簡^佩芸^^^女士||19900214|F|||台中市西屯區文心路二段281號^^台中市^^40758^TW||^^CP^0964567890
PV1||O|新陳代謝科門診^診間12^^中國醫藥大學附設醫院||||D200200^葛明志^^^醫師
RGS|1
AIS|1||新陳代謝科門診^Endocrinology^L|20260523100000|15|min
AIP|1||D200200^葛明志^^^醫師|||||20260523100000|15|min
```

---

## 13. DFT^P03 - NHI費用申報 (charge posting for NHI billing)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|BILLING|中國醫藥大學附設醫院|20260516120000||DFT^P03^DFT_P03|CMUH20260516120001|P|2.5|||AL|NE||BIG5|zh-TW
EVN|P03|20260516120000
PID|||PAT200100^^^中國醫藥大學附設醫院^PI||傅^鎮宇^^^先生||19751108|M|||台中市南屯區公益路二段51號^^台中市^^40867^TW
PV1||I|心臟內科^801^A^中國醫藥大學附設醫院||||D200100^鍾雅慧^^^醫師||||||||||VN20260509001
FT1|1|20260509|20260516|CG|D|^^^B024184100^Aspirin 100mg^NHI||7|100|mg||||||||||I25.1^動脈粥樣硬化性心臟病^ICD-10-CM
FT1|2|20260509|20260516|CG|D|^^^18003C^心臟電腦斷層造影^NHI||1|1|EA||||||||||I25.1^動脈粥樣硬化性心臟病^ICD-10-CM
FT1|3|20260509|20260516|CG|D|^^^09002C^心臟超音波^NHI||1|1|EA||||||||||I25.1^動脈粥樣硬化性心臟病^ICD-10-CM
FT1|4|20260509|20260516|CG|D|^^^00201A^住院診察費^NHI||7|1|EA||||||||||I25.1^動脈粥樣硬化性心臟病^ICD-10-CM
```

---

## 14. MDM^T02 - 出院摘要文件 (discharge summary document)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|EMR-EXCHANGE|MOHW-EMR|20260516110000||MDM^T02^MDM_T02|CMUH20260516110001|P|2.5|||AL|NE||BIG5|zh-TW
EVN|T02|20260516110000
PID|||PAT200100^^^中國醫藥大學附設醫院^PI||傅^鎮宇^^^先生||19751108|M|||台中市南屯區公益路二段51號^^台中市^^40867^TW
PV1||I|心臟內科^801^A^中國醫藥大學附設醫院||||D200100^鍾雅慧^^^醫師||||||||||VN20260509001
TXA|1|DS^出院摘要^L|FT|20260516110000|D200100^鍾雅慧^^^醫師||20260516110000||D200100^鍾雅慧^^^醫師||||DOC20260516001||||||AU
OBX|1|FT|18842-5^出院摘要^LN||入院日期: 2026/05/09\.br\主訴: 胸悶及活動性喘3天\.br\診斷: 動脈粥樣硬化性心臟病 (I25.1)\.br\治療: 心臟電腦斷層及超音波評估, 藥物治療\.br\心臟超音波: LVEF 55%, 瓣膜正常\.br\出院後注意: 規律服藥, 控制血脂, 避免劇烈運動\.br\回診日期: 2026/05/23||||||F|||20260516110000
```

---

## 15. ORU^R01 - 甲狀腺功能報告 (thyroid function results)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|LAB|中國醫藥大學附設醫院|20260509155000||ORU^R01^ORU_R01|CMUH20260509155001|P|2.5|||AL|NE||BIG5|zh-TW
PID|||PAT200200^^^中國醫藥大學附設醫院^PI||簡^佩芸^^^女士||19900214|F|||台中市西屯區文心路二段281號^^台中市^^40758^TW
PV1||O|新陳代謝科門診^診間12^^中國醫藥大學附設醫院||||D200200^葛明志^^^醫師
ORC|RE|LAB20260509030||||||||||D200200^葛明志^^^醫師
OBR|1|LAB20260509030||94385-7^甲狀腺功能檢查^LN|||20260509094000|||||||20260509094000|血液^Blood|D200200^葛明志^^^醫師
OBX|1|NM|3016-3^TSH^LN||2.35|mIU/L|0.27-4.20||||F|||20260509155000
OBX|2|NM|3024-7^Free T4^LN||1.18|ng/dL|0.93-1.70||||F|||20260509155000
OBX|3|NM|3053-6^Free T3^LN||3.05|pg/mL|2.00-4.40||||F|||20260509155000
```

---

## 16. OML^O33 - 檢體送檢 (specimen-based lab order)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|LAB|中國醫藥大學附設醫院|20260509073000||OML^O33^OML_O33|CMUH20260509073001|P|2.5|||AL|NE||BIG5|zh-TW
PID|||PAT200100^^^中國醫藥大學附設醫院^PI||傅^鎮宇^^^先生||19751108|M|||台中市南屯區公益路二段51號^^台中市^^40867^TW
PV1||I|心臟內科^801^A^中國醫藥大學附設醫院||||D200100^鍾雅慧^^^醫師
SPM|1|||BLD^全血^HL70487||||||||||||20260509073000|20260509073500
SAC|||TUBE20260509010||||||||||||||||||||||||BLD
ORC|NW|LAB20260509010|||||^^^20260509073000^^R||20260509073000|||D200100^鍾雅慧^^^醫師
OBR|1|LAB20260509010||89579-7^心臟標記檢查^LN|||20260509073000
ORC|NW|LAB20260509011|||||^^^20260509073000^^R||20260509073000|||D200100^鍾雅慧^^^醫師
OBR|2|LAB20260509011||24331-1^脂質檢查^LN|||20260509073000
```

---

## 17. ORU^R01 - 腎功能報告 (renal function results)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|LAB|中國醫藥大學附設醫院|20260510090000||ORU^R01^ORU_R01|CMUH20260510090001|P|2.5|||AL|NE||BIG5|zh-TW
PID|||PAT200200^^^中國醫藥大學附設醫院^PI||簡^佩芸^^^女士||19900214|F|||台中市西屯區文心路二段281號^^台中市^^40758^TW
PV1||O|新陳代謝科門診^診間12^^中國醫藥大學附設醫院||||D200200^葛明志^^^醫師
ORC|RE|LAB20260510001||||||||||D200200^葛明志^^^醫師
OBR|1|LAB20260510001||24362-6^腎功能檢查^LN|||20260509094500|||||||20260509094500|血液^Blood|D200200^葛明志^^^醫師
OBX|1|NM|2160-0^肌酸酐^LN||0.85|mg/dL|0.5-1.1||||F|||20260510090000
OBX|2|NM|3094-0^尿素氮^LN||16|mg/dL|7-20||||F|||20260510090000
OBX|3|NM|33914-3^eGFR^LN||98|mL/min/1.73m2|>60||||F|||20260510090000
OBX|4|NM|14959-1^尿微量白蛋白/肌酸酐比^LN||28|mg/g|0-30||||F|||20260510090000
```

---

## 18. ORU^R01 - 心臟電腦斷層報告含嵌入PDF (cardiac CT with embedded PDF)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|RADIOLOGY|中國醫藥大學附設醫院|20260511140000||ORU^R01^ORU_R01|CMUH20260511140001|P|2.5|||AL|NE||BIG5|zh-TW
PID|||PAT200100^^^中國醫藥大學附設醫院^PI||傅^鎮宇^^^先生||19751108|M|||台中市南屯區公益路二段51號^^台中市^^40867^TW
PV1||I|心臟內科^801^A^中國醫藥大學附設醫院||||D200100^鍾雅慧^^^醫師
ORC|RE|RAD20260509010||||||||||D200100^鍾雅慧^^^醫師
OBR|1|RAD20260509010||75571-7^心臟電腦斷層造影^LN|||20260509100000|||||||20260509100000||D200100^鍾雅慧^^^醫師||||||||F
OBX|1|FT|75571-7^心臟電腦斷層造影^LN||冠狀動脈鈣化分數: 85 (中度風險)\.br\左前降支: 近端50%狹窄, 混合斑塊\.br\左旋支: 無明顯狹窄\.br\右冠狀動脈: 近端30%狹窄, 鈣化斑塊\.br\結論: 中度冠狀動脈粥樣硬化, 建議藥物治療及密切追蹤。||||||F|||20260511140000
OBX|2|ED|PDF^心臟CT報告PDF^L||^application^pdf^Base64^JVBERi0xLjUKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo5b+D6Ie96Zu76IWm5pa35bGk5aCx5ZGKIC0g5Lit5ZyL6Yar6Jed5aSn5a246ZmE6Kit6Yar6ZmiKSBUagowIC0yMCBUZAoo5Yag54uA5YuV6ISI6Yi15YyW5YiG5pW4OiA4NSkgVGoKMCAtMjAgVGQKKOW3puWJjeemoeaUrzog6L+R56uvNTAl54uH56qqKSBUagowIC0yMCBUZAoo5bem5peL5pSvOiDnhKHmmI7poa/ni7nnqqopIFRqCjAgLTIwIFRkCijlj7PlhqDni4DliofohIg6IOi/keernTMwJeeLueeptikgVGoKMCAtMjAgVGQKKOe1kOirljog5Lit5bqm5Yag54uA5YuV6ISI57Kl5qij56Gs5YyWKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAyNjYgMDAwMDAgbiAKMDAwMDAwMDc2NiAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjgzMQolJUVPRgo=||||||F|||20260511140000
```

---

## 19. ORU^R01 - 凝血功能報告 (coagulation panel)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|LAB|中國醫藥大學附設醫院|20260509130000||ORU^R01^ORU_R01|CMUH20260509130001|P|2.5|||AL|NE||BIG5|zh-TW
PID|||PAT200100^^^中國醫藥大學附設醫院^PI||傅^鎮宇^^^先生||19751108|M|||台中市南屯區公益路二段51號^^台中市^^40867^TW
PV1||I|心臟內科^801^A^中國醫藥大學附設醫院||||D200100^鍾雅慧^^^醫師
ORC|RE|LAB20260509040||||||||||D200100^鍾雅慧^^^醫師
OBR|1|LAB20260509040||38875-1^凝血功能檢查^LN|||20260509082000|||||||20260509082000|血液^Blood|D200100^鍾雅慧^^^醫師
OBX|1|NM|5902-2^凝血酶原時間(PT)^LN||12.5|sec|11.0-13.5||||F|||20260509130000
OBX|2|NM|6301-6^INR^LN||1.05||0.85-1.15||||F|||20260509130000
OBX|3|NM|3173-2^活化部分凝血活酶時間(APTT)^LN||28.5|sec|25.0-35.0||||F|||20260509130000
OBX|4|NM|3255-7^纖維蛋白原^LN||285|mg/dL|200-400||||F|||20260509130000
```

---

## 20. ORU^R01 - 腹部超音波報告含嵌入PDF (abdominal ultrasound with embedded PDF)

```
MSH|^~\&|Agile-HIS|中國醫藥大學附設醫院|RADIOLOGY|中國醫藥大學附設醫院|20260510170000||ORU^R01^ORU_R01|CMUH20260510170001|P|2.5|||AL|NE||BIG5|zh-TW
PID|||PAT200200^^^中國醫藥大學附設醫院^PI||簡^佩芸^^^女士||19900214|F|||台中市西屯區文心路二段281號^^台中市^^40758^TW
PV1||O|新陳代謝科門診^診間12^^中國醫藥大學附設醫院||||D200200^葛明志^^^醫師
ORC|RE|US20260510001||||||||||D200200^葛明志^^^醫師
OBR|1|US20260510001||79103-8^腹部超音波^LN|||20260510150000|||||||20260510150000||D200200^葛明志^^^醫師||||||||F
OBX|1|FT|79103-8^腹部超音波^LN||肝臟大小正常, 實質回音均勻, 無局灶性病變。膽囊壁光滑, 無結石。胰臟及脾臟正常。雙腎大小正常, 無水腎。||||||F|||20260510170000
OBX|2|ED|PDF^腹部超音波報告PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAyNTAKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQoo6IWg6YOo6LaF6Z+z5rOi5aCx5ZGKIC0g5Lit5ZyL6Yar6Jed5aSn5a246ZmE6Kit6Yar6ZmiKSBUagowIC0yMCBUZAoo6IKd6IeP5aSn5bCP5q2j5bi4LCDnhKHlsYDnhabbgOaAp+eXheennSkgVGoKMCAtMjAgVGQKKOiDhuWbiuWSgOWFiea7kSwg54Sh57WQ55+zKSBUagowIC0yMCBUZAoo6Iac6Ie+5Y+K6IS+6Ie+5q2j5bi4KSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAyNjYgMDAwMDAgbiAKMDAwMDAwMDU2NiAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjYzMQolJUVPRgo=||||||F|||20260510170000
```
