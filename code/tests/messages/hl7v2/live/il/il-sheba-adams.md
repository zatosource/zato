# Sheba Adams Data Center - real HL7v2 ER7 messages

---

## 1. ADT^A01 - admission feed to data center

```
MSH|^~\&|CHAMELEON|SHEBA_MC|ADAMS_DC|SHEBA_CDR|20260301080000||ADT^A01^ADT_A01|ADM000001|P|2.5
EVN|A01|20260301080000
PID|||382716495^^^IL_MOH^NI~SH10001^^^SHEBA^MR||Cohen^Yael^Tirza^^Mrs.||19780315|F|||Hatzionut 47^^Haifa^^3303125^IL||^PRN^PH^04-823-4567~^PRN^CP^052-381-7264~^NET^Internet^yael.cohen@gmail.com
PV1||I|CARD^500^A^SHEBA||||30456^Khoury^Samir^^^Dr.||40567^Friedman^Sigalit^^^Dr.||CARD||||||||VN10001|||||||||||||||||||||||20260301080000
IN1|1||101|Clalit Health Services|Arlozorov 101^^Tel Aviv^^6209801^IL
DG1|1||I25.1^Atherosclerotic heart disease^ICD10||20260301||||||||||||1
```

---

## 2. ADT^A03 - discharge feed to data center

```
MSH|^~\&|CHAMELEON|SHEBA_MC|ADAMS_DC|SHEBA_CDR|20260308160000||ADT^A03^ADT_A03|ADM000002|P|2.5
EVN|A03|20260308160000
PID|||382716495^^^IL_MOH^NI~SH10001^^^SHEBA^MR||Cohen^Yael^Tirza^^Mrs.||19780315|F|||Hatzionut 47^^Haifa^^3303125^IL||^PRN^CP^052-381-7264
PV1||I|CARD^500^A^SHEBA||||30456^Khoury^Samir^^^Dr.||40567^Friedman^Sigalit^^^Dr.||CARD||||||||VN10001||||||||||||||||||||||||||20260308160000
DG1|1||I25.1^Atherosclerotic heart disease^ICD10||20260301||||||||||||1
DG1|2||I21.0^Acute transmural MI of anterior wall^ICD10||20260302||||||||||||2
```

---

## 3. ORU^R01 - laboratory result feed to CDR

```
MSH|^~\&|LABOS|SHEBA_LAB|ADAMS_DC|SHEBA_CDR|20260302140000||ORU^R01|ADM000003|P|2.5
PID|||382716495^^^IL_MOH^NI~SH10001^^^SHEBA^MR||Cohen^Yael^Tirza^^Mrs.||19780315|F|||Hatzionut 47^^Haifa^^3303125^IL||^PRN^CP^052-381-7264
PV1||I|CARD^500^A^SHEBA||||30456^Khoury^Samir^^^Dr.||||||||||||VN10001
ORC|RE|ORD7001^CHAMELEON|RES7001^LABOS
OBR|1|ORD7001^CHAMELEON|RES7001^LABOS|CARD^Cardiac Markers^L|||20260302060000|||||||||30456^Khoury^Samir^^^Dr.|||||||F
OBX|1|NM|10839-9^Troponin I^LN||2.45|ng/mL|<0.04|HH|||F
OBX|2|NM|2157-6^CK-MB^LN||42|ng/mL|0-5|HH|||F
OBX|3|NM|33762-6^NT-proBNP^LN||2800|pg/mL|<125|HH|||F
OBX|4|NM|2823-3^Potassium^LN||4.2|mmol/L|3.5-5.0|N|||F
OBX|5|NM|2160-0^Creatinine^LN||1.1|mg/dL|0.6-1.2|N|||F
```

---

## 4. ORU^R01 - radiology report feed to CDR

```
MSH|^~\&|ERAD_RIS|SHEBA_RAD|ADAMS_DC|SHEBA_CDR|20260302120000||ORU^R01|ADM000004|P|2.5
PID|||382716495^^^IL_MOH^NI~SH10001^^^SHEBA^MR||Cohen^Yael^Tirza^^Mrs.||19780315|F|||Hatzionut 47^^Haifa^^3303125^IL||^PRN^CP^052-381-7264
PV1||I|CARD^500^A^SHEBA||||30456^Khoury^Samir^^^Dr.||||||||||||VN10001
ORC|RE|ORD7002^CHAMELEON|RES7002^ERAD_RIS
OBR|1|ORD7002^CHAMELEON|RES7002^ERAD_RIS|71020^Chest X-Ray^CPT|||20260302073000|||||||||30456^Khoury^Samir^^^Dr.||RAD30001||||||F
OBX|1|FT|71020^Chest X-Ray Report^CPT||PA and Lateral Chest Radiograph\.br\Heart is mildly enlarged\.br\Mild pulmonary vascular congestion\.br\Small bilateral pleural effusions\.br\Impression: Mild congestive heart failure||||||F
```

---

## 5. ORU^R01 - ICU vitals feed from MetaVision

```
MSH|^~\&|METAVISION|SHEBA_ICU|ADAMS_DC|SHEBA_CDR|20260303080000||ORU^R01|ADM000005|P|2.5
PID|||517384926^^^IL_MOH^NI~SH20002^^^SHEBA^MR||Mizrahi^Avi^Yaakov^^Mr.||19650722|M|||Ben Yehuda 18^^Tel Aviv^^6380118^IL||^PRN^CP^054-768-4321
PV1||I|ICU^101^A^SHEBA||||30456^Khoury^Samir^^^Dr.||||||||||||VN20002
OBR|1|||VITALS^Vital Signs^MV|||20260303080000
OBX|1|NM|8867-4^Heart Rate^LN||88|/min|60-100|N|||F
OBX|2|NM|8480-6^Systolic BP^LN||105|mmHg|90-140|N|||F
OBX|3|NM|8462-4^Diastolic BP^LN||65|mmHg|60-90|N|||F
OBX|4|NM|8310-5^Temperature^LN||37.8|Cel|36.1-37.2|H|||F
OBX|5|NM|9279-1^Respiratory Rate^LN||18|/min|12-20|N|||F
OBX|6|NM|59408-5^SpO2^LN||95|%|95-100|N|||F
```

---

## 6. ORU^R01 - pharmacy dispensing feed

```
MSH|^~\&|PHARM_SYS|SHEBA_PHARM|ADAMS_DC|SHEBA_CDR|20260303090000||ORU^R01|ADM000006|P|2.5
PID|||382716495^^^IL_MOH^NI~SH10001^^^SHEBA^MR||Cohen^Yael^Tirza^^Mrs.||19780315|F|||Hatzionut 47^^Haifa^^3303125^IL||^PRN^CP^052-381-7264
PV1||I|CARD^500^A^SHEBA||||30456^Khoury^Samir^^^Dr.||||||||||||VN10001
ORC|RE|ORD7003^CHAMELEON|RES7003^PHARM_SYS
RXD|1|00006-0749-54^Aspirin 100mg^NDC|20260303090000|1|TAB|PO|||||||||30456^Khoury^Samir^^^Dr.
RXD|2|00078-0401-05^Clopidogrel 75mg^NDC|20260303090000|1|TAB|PO|||||||||30456^Khoury^Samir^^^Dr.
RXD|3|00071-0155-23^Atorvastatin 40mg^NDC|20260303210000|1|TAB|PO|||||||||30456^Khoury^Samir^^^Dr.
```

---

## 7. MDM^T02 - discharge summary with embedded PDF (base64 ED)

```
MSH|^~\&|CHAMELEON|SHEBA_MC|ADAMS_DC|SHEBA_CDR|20260308170000||MDM^T02|ADM000007|P|2.5
EVN|T02|20260308170000
PID|||382716495^^^IL_MOH^NI~SH10001^^^SHEBA^MR||Cohen^Yael^Tirza^^Mrs.||19780315|F|||Hatzionut 47^^Haifa^^3303125^IL||^PRN^CP^052-381-7264
PV1||I|CARD^500^A^SHEBA||||30456^Khoury^Samir^^^Dr.||||||||||||VN10001
TXA|1|DS^Discharge Summary^L|TX|20260308160000|30456^Khoury^Samir^^^Dr.|20260308170000||||DOC50001||||||LA
OBX|1|ED|DS^Discharge Summary PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvUmVzb3VyY2VzIDw8ID4+ID4+CmVuZG9iagp4cmVmCjAgNAowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNCAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMjE2CiUlRU9GCg==||||||F
```

---

## 8. MDM^T02 - operative note with embedded PDF (base64 ED)

```
MSH|^~\&|CHAMELEON|SHEBA_MC|ADAMS_DC|SHEBA_CDR|20260304160000||MDM^T02|ADM000008|P|2.5
EVN|T02|20260304160000
PID|||639587214^^^IL_MOH^NI~SH30003^^^SHEBA^MR||Baruch^Tamar^Shoshana^^Mrs.||19900110|F|||Rothschild 22^^Tel Aviv^^6688102^IL||^PRN^CP^050-987-6543
PV1||I|SURG^400^B^SHEBA||||50678^Friedman^Sigalit^^^Dr.||||||||||||VN30003
TXA|1|OP^Operative Note^L|TX|20260304150000|50678^Friedman^Sigalit^^^Dr.|20260304160000||||DOC50002||||||LA
OBX|1|ED|OP^Operative Note PDF^L||^application^pdf^Base64^JVBERi0xLjUKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvUmVzb3VyY2VzIDw8ID4+ID4+CmVuZG9iagp4cmVmCjAgNAowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNCAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMjE2CiUlRU9GCg==||||||F
```

---

## 9. ADT^A08 - patient update feed

```
MSH|^~\&|CHAMELEON|SHEBA_MC|ADAMS_DC|SHEBA_CDR|20260305090000||ADT^A08^ADT_A01|ADM000009|P|2.5
EVN|A08|20260305090000
PID|||741296835^^^IL_MOH^NI~SH40004^^^SHEBA^MR||Dahan^Eli^Reuven^^Mr.||19550830|M|||Arlozorov 50^^Tel Aviv^^6209304^IL||^PRN^PH^03-623-4567~^PRN^CP^054-765-4321~^NET^Internet^eli.dahan@walla.co.il
PV1||I|NEPH^501^C^SHEBA||||40567^Goldstein^Daniel^^^Dr.||||||||||||VN40004
IN1|1||102|Maccabi Healthcare Services|Hamered 27^^Tel Aviv^^6812507^IL
```

---

## 10. ADT^A02 - transfer feed

```
MSH|^~\&|CHAMELEON|SHEBA_MC|ADAMS_DC|SHEBA_CDR|20260306093000||ADT^A02^ADT_A02|ADM000010|P|2.5
EVN|A02|20260306093000
PID|||826491357^^^IL_MOH^NI~SH50005^^^SHEBA^MR||Peretz^Sarah^Leah^^Mrs.||19881205|F|||Weizmann 8^^Rehovot^^7610001^IL||^PRN^CP^058-345-7218
PV1||I|CARD^502^A^SHEBA||||30456^Khoury^Samir^^^Dr.||40567^Friedman^Sigalit^^^Dr.||ICU^101^A^SHEBA|||||||VN50005|||||||||||||||||||||||20260306093000
```

---

## 11. ORU^R01 - microbiology feed

```
MSH|^~\&|LABOS|SHEBA_LAB|ADAMS_DC|SHEBA_CDR|20260307160000||ORU^R01|ADM000011|P|2.5
PID|||915362847^^^IL_MOH^NI~SH60006^^^SHEBA^MR||Azoulay^Yosef^Haim^^Mr.||19700415|M|||Kaplan 30^^Be'er Sheva^^8425503^IL||^PRN^CP^052-568-9012
PV1||I|INF^301^A^SHEBA||||50678^Friedman^Sigalit^^^Dr.||||||||||||VN60006
ORC|RE|ORD7004^CHAMELEON|RES7004^LABOS
OBR|1|ORD7004^CHAMELEON|RES7004^LABOS|87040^Blood Culture^CPT|||20260306060000|||||||||50678^Friedman^Sigalit^^^Dr.|||||||F
OBX|1|CE|87040^Organism^CPT||KPN^Klebsiella pneumoniae^L||||||F
OBX|2|SN|18906-8^Meropenem MIC^LN||<=0.25|ug/mL||||S|||F
OBX|3|SN|18862-3^Vancomycin MIC^LN||>32|ug/mL||||R|||F
OBX|4|SN|18928-2^Ciprofloxacin MIC^LN||>4|ug/mL||||R|||F
```

---

## 12. ORU^R01 - pathology result feed

```
MSH|^~\&|PATH_SYS|SHEBA_PATH|ADAMS_DC|SHEBA_CDR|20260308150000||ORU^R01|ADM000012|P|2.5
PID|||374918526^^^IL_MOH^NI~SH70007^^^SHEBA^MR||Stern^Devorah^Bracha^^Mrs.||19820920|F|||Jabotinsky 40^^Ramat Gan^^5252007^IL||^PRN^CP^050-113-3445
PV1||I|SURG^400^A^SHEBA||||50678^Friedman^Sigalit^^^Dr.||||||||||||VN70007
ORC|RE|ORD7005^CHAMELEON|RES7005^PATH_SYS
OBR|1|ORD7005^CHAMELEON|RES7005^PATH_SYS|88305^Surgical Pathology^CPT|||20260307100000|||||||||50678^Friedman^Sigalit^^^Dr.|||||||F
OBX|1|FT|88305^Pathology Report^CPT||Specimen: Appendix\.br\Gross: Appendix 8.5 cm, dilated with wall thickening\.br\Microscopic: Transmural acute inflammation with abscess formation\.br\Periappendiceal fat involvement\.br\No malignancy identified\.br\Diagnosis: Acute gangrenous appendicitis with periappendicitis||||||F
```

---

## 13. ORU^R01 - ECG result feed

```
MSH|^~\&|MACCABI_CVIS|SHEBA_CARD|ADAMS_DC|SHEBA_CDR|20260309110000||ORU^R01|ADM000013|P|2.5
PID|||582714639^^^IL_MOH^NI~SH80008^^^SHEBA^MR||Petrov^Boris^Mikhail^^Mr.||19720618|M|||HaShachar 5^^Ashdod^^7758037^IL||^PRN^CP^054-228-3447
PV1||I|CARD^500^A^SHEBA||||30456^Khoury^Samir^^^Dr.||||||||||||VN80008
ORC|RE|ORD7006^CHAMELEON|RES7006^MACCABI_CVIS
OBR|1|ORD7006^CHAMELEON|RES7006^MACCABI_CVIS|93000^ECG^CPT|||20260309100000|||||||||30456^Khoury^Samir^^^Dr.|||||||F
OBX|1|NM|8867-4^Heart Rate^LN||78|/min|60-100|N|||F
OBX|2|ST|ECG_RHYTHM^Rhythm^L||Normal sinus rhythm||||||F
OBX|3|ST|ECG_AXIS^Axis^L||Normal axis||||||F
OBX|4|ST|ECG_INTERP^Interpretation^L||ST elevation in V1-V4, consistent with anterior STEMI||||||F
```

---

## 14. ADT^A40 - patient merge feed

```
MSH|^~\&|CHAMELEON|SHEBA_MC|ADAMS_DC|SHEBA_CDR|20260310110000||ADT^A40^ADT_A39|ADM000014|P|2.5
EVN|A40|20260310110000
PID|||693158274^^^IL_MOH^NI~SH90009^^^SHEBA^MR||Bitton^Rachel^Esther^^Mrs.||19680309|F|||HaNevi'im 14^^Jerusalem^^9423614^IL||^PRN^CP^052-876-4521
MRG|693158275^^^IL_MOH^NI~SH90010^^^SHEBA^MR||VN90009
PV1||I|GEN^202^B^SHEBA||||80901^Harari^Tomer^^^Dr.||||||||||||VN90010
```

---

## 15. ORU^R01 - blood bank feed

```
MSH|^~\&|ILEX|SHEBA_BB|ADAMS_DC|SHEBA_CDR|20260311140000||ORU^R01|ADM000015|P|2.5
PID|||417286953^^^IL_MOH^NI~SH10010^^^SHEBA^MR||Edri^Shimon^Avraham^^Mr.||19950512|M|||Allenby 77^^Tel Aviv^^6513215^IL||^PRN^CP^053-446-5728
PV1||I|SURG^400^A^SHEBA||||50678^Friedman^Sigalit^^^Dr.||||||||||||VN10010
ORC|RE|ORD7007^CHAMELEON|RES7007^ILEX
OBR|1|ORD7007^CHAMELEON|RES7007^ILEX|XMATCH^Type and Screen^L|||20260311080000|||||||||50678^Friedman^Sigalit^^^Dr.|||||||F
OBX|1|CE|882-1^ABO Group^LN||O^Group O^L||||||F
OBX|2|CE|10331-7^Rh Type^LN||POS^Positive^L||||||F
OBX|3|CE|1250-0^Antibody Screen^LN||NEG^Negative^L||||||F
```

---

## 16. ORU^R01 - nursing assessment feed

```
MSH|^~\&|CHAMELEON|SHEBA_MC|ADAMS_DC|SHEBA_CDR|20260312080000||ORU^R01|ADM000016|P|2.5
PID|||528419367^^^IL_MOH^NI~SH20011^^^SHEBA^MR||Vaknin^Oded^Eliyahu^^Mr.||19800101|M|||Arlozorov 35^^Haifa^^3301521^IL||^PRN^CP^050-668-2734
PV1||I|ONCO^700^A^SHEBA||||10234^Mansour^Khaled^^^Dr.||||||||||||VN20011
OBR|1|||NURS^Nursing Assessment^L|||20260312080000
OBX|1|NM|38208-5^Pain Score^LN||6||0-10|H|||F
OBX|2|CE|FALL_RISK^Fall Risk^L||HIGH^High Risk^L||||||F
OBX|3|NM|MORSE^Morse Fall Scale^L||55||<25|H|||F
OBX|4|CE|DIET^Diet^L||REG^Regular^L||||||F
OBX|5|CE|ALLERGY^Drug Allergy^L||PEN^Penicillin - Rash^L||||||F
```

---

## 17. SIU^S12 - appointment feed

```
MSH|^~\&|CHAMELEON|SHEBA_MC|ADAMS_DC|SHEBA_CDR|20260313080000||SIU^S12|ADM000017|P|2.5
PID|||618293574^^^IL_MOH^NI~SH30012^^^SHEBA^MR||Aslan^Yaron^Tomer^^Mr.||19880315|M|||Balfour 22^^Bat Yam^^5930002^IL||^PRN^CP^052-218-4936
PV1||O|CARD^100^^SHEBA||||30456^Khoury^Samir^^^Dr.||||||||||||VN30012
SCH|APT70001|APT70001||||ROUTINE^Routine^HL70276|FOLLOWUP^Follow-up Visit^L|||||30|min|^^^20260320100000^20260320103000
AIS|1||CARD_FU^Cardiology Follow-up^L|20260320100000|||30|min
```

---

## 18. ORU^R01 - allergy feed

```
MSH|^~\&|CHAMELEON|SHEBA_MC|ADAMS_DC|SHEBA_CDR|20260314090000||ORU^R01|ADM000018|P|2.5
PID|||357128649^^^IL_MOH^NI~SH40013^^^SHEBA^MR||Sabag^Daniel^Michael^^Mr.||19910203|M|||Herzl 100^^Be'er Sheva^^8410901^IL||^PRN^CP^058-991-2374
PV1||I|MED^301^A^SHEBA||||30456^Khoury^Samir^^^Dr.||||||||||||VN40013
AL1|1|DA^Drug Allergy^HL70127|PEN^Penicillin^L|SV^Severe^HL70128|Anaphylaxis|20220515
AL1|2|DA^Drug Allergy^HL70127|SUL^Sulfonamides^L|MO^Moderate^HL70128|Rash|20230310
```

---

## 19. ORU^R01 - consultation note feed

```
MSH|^~\&|CHAMELEON|SHEBA_MC|ADAMS_DC|SHEBA_CDR|20260315140000||ORU^R01|ADM000019|P|2.5
PID|||512837694^^^IL_MOH^NI~SH50014^^^SHEBA^MR||Tzur^Liora^Galit^^Mrs.||19850714|F|||Ben Gurion 20^^Kfar Saba^^4433501^IL||^PRN^CP^052-334-4556
PV1||I|CARD^500^A^SHEBA||||30456^Khoury^Samir^^^Dr.||||||||||||VN50014
OBR|1|||CONSULT^Cardiology Consultation^L|||20260315130000
OBX|1|FT|CONSULT^Consultation Note^L||Cardiology Consultation\.br\Reason: Preoperative cardiac evaluation\.br\History: 39F, no cardiac history\.br\Exam: Regular rhythm, no murmurs\.br\ECG: Normal sinus rhythm\.br\Assessment: Low cardiac risk for planned surgery\.br\Recommendation: Clear for surgery, no further cardiac workup needed||||||F
```

---

## 20. ACK - data center acknowledgment

```
MSH|^~\&|ADAMS_DC|SHEBA_CDR|CHAMELEON|SHEBA_MC|20260316080100||ACK|ADM000020|P|2.5
MSA|AA|ADM000001|Message processed and stored in CDR
```
