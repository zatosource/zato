# Maccabi Cardiovascular Information System - real HL7v2 ER7 messages

---

## 1. ORM^O01 - resting ECG order

```
MSH|^~\&|MACCABI_EMR|MACCABI_CL|MACCABI_CVIS|MACCABI_CARD|20260301090000||ORM^O01|MCV000001|P|2.4
PID|||472916385^^^IL_MOH^NI~M10001^^^MACCABI^MR||Cohen^Maya^Adina^^Mrs.||19780315|F|||Hatzionut 47^^Haifa^^3303125^IL||^PRN^CP^052-417-3829
PV1||O|CARD^100^^MACCABI_CL||||44567^Gershon^Tamar^^^Dr.||||||||||||VN10001
ORC|NW|ORD4001^MACCABI_EMR|||||^^^20260301090000^^R
OBR|1|ORD4001^MACCABI_EMR||93000^Resting ECG^CPT|||20260301083000||||A|||||44567^Gershon^Tamar^^^Dr.
```

---

## 2. ORU^R01 - resting ECG result

```
MSH|^~\&|MACCABI_CVIS|MACCABI_CARD|MACCABI_EMR|MACCABI_CL|20260301110000||ORU^R01|MCV000002|P|2.4
PID|||472916385^^^IL_MOH^NI~M10001^^^MACCABI^MR||Cohen^Maya^Adina^^Mrs.||19780315|F|||Hatzionut 47^^Haifa^^3303125^IL||^PRN^CP^052-417-3829
PV1||O|CARD^100^^MACCABI_CL||||44567^Gershon^Tamar^^^Dr.||||||||||||VN10001
ORC|RE|ORD4001^MACCABI_EMR|RES4001^MACCABI_CVIS
OBR|1|ORD4001^MACCABI_EMR|RES4001^MACCABI_CVIS|93000^Resting ECG^CPT|||20260301083000|||||||||44567^Gershon^Tamar^^^Dr.|||||||F
OBX|1|NM|8867-4^Heart Rate^LN||72|/min|60-100|N|||F
OBX|2|NM|8633-0^QRS Duration^LN||88|ms|<120|N|||F
OBX|3|NM|8625-6^PR Interval^LN||168|ms|120-200|N|||F
OBX|4|NM|8634-8^QTc Interval^LN||420|ms|<450|N|||F
OBX|5|ST|ECG_RHYTHM^Rhythm^L||Normal sinus rhythm||||||F
OBX|6|ST|ECG_INTERP^Interpretation^L||Normal ECG||||||F
```

---

## 3. ORM^O01 - echocardiography order

```
MSH|^~\&|MACCABI_EMR|MACCABI_CL|MACCABI_CVIS|MACCABI_CARD|20260302090000||ORM^O01|MCV000003|P|2.4
PID|||528637194^^^IL_MOH^NI~M20002^^^MACCABI^MR||Mizrahi^Yaakov^Eitan^^Mr.||19650722|M|||HaShalom 21^^Tel Aviv^^6789307^IL||^PRN^CP^054-768-2843
PV1||O|CARD^100^^MACCABI_CL||||44568^Shapira^Doron^^^Dr.||||||||||||VN20002
ORC|NW|ORD4002^MACCABI_EMR|||||^^^20260302090000^^R
OBR|1|ORD4002^MACCABI_EMR||93306^Transthoracic Echocardiography^CPT|||20260302083000||||A|||||44568^Shapira^Doron^^^Dr.
```

---

## 4. ORU^R01 - echocardiography result

```
MSH|^~\&|MACCABI_CVIS|MACCABI_CARD|MACCABI_EMR|MACCABI_CL|20260302140000||ORU^R01|MCV000004|P|2.4
PID|||528637194^^^IL_MOH^NI~M20002^^^MACCABI^MR||Mizrahi^Yaakov^Eitan^^Mr.||19650722|M|||HaShalom 21^^Tel Aviv^^6789307^IL||^PRN^CP^054-768-2843
PV1||O|CARD^100^^MACCABI_CL||||44568^Shapira^Doron^^^Dr.||||||||||||VN20002
ORC|RE|ORD4002^MACCABI_EMR|RES4002^MACCABI_CVIS
OBR|1|ORD4002^MACCABI_EMR|RES4002^MACCABI_CVIS|93306^Transthoracic Echocardiography^CPT|||20260302083000|||||||||44568^Shapira^Doron^^^Dr.|||||||F
OBX|1|NM|18043-0^LVEF^LN||55|%|55-70|N|||F
OBX|2|NM|29430-7^LVEDD^LN||48|mm|35-56|N|||F
OBX|3|NM|29434-9^LVESD^LN||32|mm|20-40|N|||F
OBX|4|NM|18148-7^LA Diameter^LN||38|mm|19-40|N|||F
OBX|5|ST|ECHO_MV^Mitral Valve^L||Mild regurgitation||||||F
OBX|6|ST|ECHO_AV^Aortic Valve^L||Normal||||||F
OBX|7|ST|ECHO_INTERP^Impression^L||Normal LV systolic function. Mild mitral regurgitation. No pericardial effusion.||||||F
```

---

## 5. ORM^O01 - exercise stress test order

```
MSH|^~\&|MACCABI_EMR|MACCABI_CL|MACCABI_CVIS|MACCABI_CARD|20260303090000||ORM^O01|MCV000005|P|2.4
PID|||639148275^^^IL_MOH^NI~M30003^^^MACCABI^MR||Khoury^Layla^Mariam^^Mrs.||19900110|F|||Salah-a-Din 8^^Nazareth^^1610421^IL||^PRN^CP^050-986-3274
PV1||O|CARD^100^^MACCABI_CL||||44569^Bar-Lev^Roni^^^Dr.||||||||||||VN30003
ORC|NW|ORD4003^MACCABI_EMR|||||^^^20260303090000^^R
OBR|1|ORD4003^MACCABI_EMR||93015^Exercise Stress Test^CPT|||20260303083000||||A|||||44569^Bar-Lev^Roni^^^Dr.
```

---

## 6. ORU^R01 - exercise stress test result

```
MSH|^~\&|MACCABI_CVIS|MACCABI_CARD|MACCABI_EMR|MACCABI_CL|20260303120000||ORU^R01|MCV000006|P|2.4
PID|||639148275^^^IL_MOH^NI~M30003^^^MACCABI^MR||Khoury^Layla^Mariam^^Mrs.||19900110|F|||Salah-a-Din 8^^Nazareth^^1610421^IL||^PRN^CP^050-986-3274
PV1||O|CARD^100^^MACCABI_CL||||44569^Bar-Lev^Roni^^^Dr.||||||||||||VN30003
ORC|RE|ORD4003^MACCABI_EMR|RES4003^MACCABI_CVIS
OBR|1|ORD4003^MACCABI_EMR|RES4003^MACCABI_CVIS|93015^Exercise Stress Test^CPT|||20260303083000|||||||||44569^Bar-Lev^Roni^^^Dr.|||||||F
OBX|1|NM|STRESS_HR_REST^Resting HR^L||68|/min||||F
OBX|2|NM|STRESS_HR_PEAK^Peak HR^L||162|/min||||F
OBX|3|NM|STRESS_BP_REST^Resting BP^L||128/78|mmHg||||F
OBX|4|NM|STRESS_BP_PEAK^Peak BP^L||180/85|mmHg||||F
OBX|5|NM|STRESS_DURATION^Exercise Duration^L||9.5|min||||F
OBX|6|NM|STRESS_METS^METs Achieved^L||10.2|METs||||F
OBX|7|CE|STRESS_RESULT^Test Result^L||NEG^Negative for ischemia^L||||||F
OBX|8|ST|STRESS_INTERP^Interpretation^L||Adequate exercise tolerance. No ECG changes suggestive of ischemia. Normal blood pressure response.||||||F
```

---

## 7. ORM^O01 - Holter monitor order

```
MSH|^~\&|MACCABI_EMR|MACCABI_CL|MACCABI_CVIS|MACCABI_CARD|20260304090000||ORM^O01|MCV000007|P|2.4
PID|||748295163^^^IL_MOH^NI~M40004^^^MACCABI^MR||Dahan^Yair^Reuven^^Mr.||19550830|M|||Emek Refaim 41^^Jerusalem^^9314512^IL||^PRN^PH^02-624-3781
PV1||O|CARD^100^^MACCABI_CL||||44570^Levi^Adi^^^Dr.||||||||||||VN40004
ORC|NW|ORD4004^MACCABI_EMR|||||^^^20260304090000^^R
OBR|1|ORD4004^MACCABI_EMR||93224^24-Hour Holter Monitor^CPT|||20260304083000||||A|||||44570^Levi^Adi^^^Dr.
```

---

## 8. ORU^R01 - Holter monitor result with embedded PDF (base64 ED)

```
MSH|^~\&|MACCABI_CVIS|MACCABI_CARD|MACCABI_EMR|MACCABI_CL|20260306140000||ORU^R01|MCV000008|P|2.4
PID|||748295163^^^IL_MOH^NI~M40004^^^MACCABI^MR||Dahan^Yair^Reuven^^Mr.||19550830|M|||Emek Refaim 41^^Jerusalem^^9314512^IL||^PRN^PH^02-624-3781
PV1||O|CARD^100^^MACCABI_CL||||44570^Levi^Adi^^^Dr.||||||||||||VN40004
ORC|RE|ORD4004^MACCABI_EMR|RES4004^MACCABI_CVIS
OBR|1|ORD4004^MACCABI_EMR|RES4004^MACCABI_CVIS|93224^24-Hour Holter Monitor^CPT|||20260304083000|||||||||44570^Levi^Adi^^^Dr.|||||||F
OBX|1|NM|HOLTER_HR_MIN^Minimum HR^L||48|/min||||F
OBX|2|NM|HOLTER_HR_MAX^Maximum HR^L||118|/min||||F
OBX|3|NM|HOLTER_HR_AVG^Average HR^L||72|/min||||F
OBX|4|NM|HOLTER_PVC^PVC Count^L||245|beats/24hr||||F
OBX|5|NM|HOLTER_PAC^PAC Count^L||89|beats/24hr||||F
OBX|6|ST|HOLTER_INTERP^Interpretation^L||Predominant sinus rhythm. Occasional PVCs, isolated. No sustained arrhythmia. No significant pauses.||||||F
OBX|7|ED|PDF^Holter Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvUmVzb3VyY2VzIDw8ID4+ID4+CmVuZG9iagp4cmVmCjAgNAowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNCAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMjE2CiUlRU9GCg==||||||F
```

---

## 9. ORU^R01 - cardiac catheterization result with embedded PDF (base64 ED)

```
MSH|^~\&|MACCABI_CVIS|MACCABI_CARD|MACCABI_EMR|MACCABI_CL|20260307160000||ORU^R01|MCV000009|P|2.4
PID|||825637419^^^IL_MOH^NI~M50005^^^MACCABI^MR||Peretz^Sarah^Leah^^Mrs.||19881205|F|||Weizmann 8^^Rehovot^^7610001^IL||^PRN^CP^058-345-7218
PV1||I|CARD^500^^MACCABI_HOSP||||44571^Cohen-Goldberg^Yael^^^Dr.||||||||||||VN50005
ORC|RE|ORD4005^MACCABI_EMR|RES4005^MACCABI_CVIS
OBR|1|ORD4005^MACCABI_EMR|RES4005^MACCABI_CVIS|93458^Cardiac Catheterization^CPT|||20260307100000|||||||||44571^Cohen-Goldberg^Yael^^^Dr.|||||||F
OBX|1|ST|CATH_LAD^LAD^L||80% stenosis mid-segment||||||F
OBX|2|ST|CATH_LCX^LCx^L||Normal||||||F
OBX|3|ST|CATH_RCA^RCA^L||50% stenosis proximal||||||F
OBX|4|NM|CATH_LVEF^LVEF^L||50|%||||F
OBX|5|NM|CATH_LVEDP^LVEDP^L||18|mmHg||||F
OBX|6|ST|CATH_INTERP^Impression^L||Significant single-vessel disease (LAD). PCI to LAD recommended.||||||F
OBX|7|ED|PDF^Cath Report PDF^L||^application^pdf^Base64^JVBERi0xLjUKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvUmVzb3VyY2VzIDw8ID4+ID4+CmVuZG9iagp4cmVmCjAgNAowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNCAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMjE2CiUlRU9GCg==||||||F
```

---

## 10. ORM^O01 - ambulatory blood pressure monitoring order

```
MSH|^~\&|MACCABI_EMR|MACCABI_CL|MACCABI_CVIS|MACCABI_CARD|20260308090000||ORM^O01|MCV000010|P|2.4
PID|||916482573^^^IL_MOH^NI~M60006^^^MACCABI^MR||Azoulay^Yosef^Haim^^Mr.||19700415|M|||Kaplan 30^^Be'er Sheva^^8425503^IL||^PRN^CP^052-568-9012
PV1||O|CARD^100^^MACCABI_CL||||44572^Mendel^Hagai^^^Dr.||||||||||||VN60006
ORC|NW|ORD4006^MACCABI_EMR|||||^^^20260308090000^^R
OBR|1|ORD4006^MACCABI_EMR||93784^Ambulatory BP Monitoring 24hr^CPT|||20260308083000||||A|||||44572^Mendel^Hagai^^^Dr.
```

---

## 11. ORU^R01 - ABPM result

```
MSH|^~\&|MACCABI_CVIS|MACCABI_CARD|MACCABI_EMR|MACCABI_CL|20260310140000||ORU^R01|MCV000011|P|2.4
PID|||916482573^^^IL_MOH^NI~M60006^^^MACCABI^MR||Azoulay^Yosef^Haim^^Mr.||19700415|M|||Kaplan 30^^Be'er Sheva^^8425503^IL||^PRN^CP^052-568-9012
PV1||O|CARD^100^^MACCABI_CL||||44572^Mendel^Hagai^^^Dr.||||||||||||VN60006
ORC|RE|ORD4006^MACCABI_EMR|RES4006^MACCABI_CVIS
OBR|1|ORD4006^MACCABI_EMR|RES4006^MACCABI_CVIS|93784^Ambulatory BP Monitoring 24hr^CPT|||20260308083000|||||||||44572^Mendel^Hagai^^^Dr.|||||||F
OBX|1|NM|ABPM_SBP_DAY^Daytime Mean SBP^L||142|mmHg|<135|H|||F
OBX|2|NM|ABPM_DBP_DAY^Daytime Mean DBP^L||88|mmHg|<85|H|||F
OBX|3|NM|ABPM_SBP_NIGHT^Nighttime Mean SBP^L||128|mmHg|<120|H|||F
OBX|4|NM|ABPM_DBP_NIGHT^Nighttime Mean DBP^L||75|mmHg|<70|H|||F
OBX|5|NM|ABPM_DIP^Nocturnal Dip^L||10|%|10-20|N|||F
OBX|6|ST|ABPM_INTERP^Interpretation^L||Daytime and nighttime hypertension. Borderline dipper pattern.||||||F
```

---

## 12. ORM^O01 - nuclear stress test order

```
MSH|^~\&|MACCABI_EMR|MACCABI_CL|MACCABI_CVIS|MACCABI_CARD|20260311090000||ORM^O01|MCV000012|P|2.4
PID|||374918526^^^IL_MOH^NI~M70007^^^MACCABI^MR||Stern^Devorah^Bracha^^Mrs.||19820920|F|||Jabotinsky 40^^Ramat Gan^^5252007^IL||^PRN^CP^050-113-3445
PV1||O|CARD^100^^MACCABI_CL||||44573^Friedman^Eyal^^^Dr.||||||||||||VN70007
ORC|NW|ORD4007^MACCABI_EMR|||||^^^20260311090000^^R
OBR|1|ORD4007^MACCABI_EMR||78452^Myocardial Perfusion SPECT^CPT|||20260311083000||||A|||||44573^Friedman^Eyal^^^Dr.
```

---

## 13. ORU^R01 - nuclear stress test result

```
MSH|^~\&|MACCABI_CVIS|MACCABI_CARD|MACCABI_EMR|MACCABI_CL|20260311160000||ORU^R01|MCV000013|P|2.4
PID|||374918526^^^IL_MOH^NI~M70007^^^MACCABI^MR||Stern^Devorah^Bracha^^Mrs.||19820920|F|||Jabotinsky 40^^Ramat Gan^^5252007^IL||^PRN^CP^050-113-3445
PV1||O|CARD^100^^MACCABI_CL||||44573^Friedman^Eyal^^^Dr.||||||||||||VN70007
ORC|RE|ORD4007^MACCABI_EMR|RES4007^MACCABI_CVIS
OBR|1|ORD4007^MACCABI_EMR|RES4007^MACCABI_CVIS|78452^Myocardial Perfusion SPECT^CPT|||20260311083000|||||||||44573^Friedman^Eyal^^^Dr.|||||||F
OBX|1|ST|SPECT_REST^Rest Perfusion^L||Normal perfusion throughout||||||F
OBX|2|ST|SPECT_STRESS^Stress Perfusion^L||Reversible defect in inferior wall||||||F
OBX|3|NM|SPECT_LVEF_REST^Rest LVEF^L||58|%||||F
OBX|4|NM|SPECT_LVEF_STRESS^Stress LVEF^L||52|%||||F
OBX|5|NM|SPECT_SSS^Summed Stress Score^L||8||||||F
OBX|6|NM|SPECT_SRS^Summed Rest Score^L||2||||||F
OBX|7|ST|SPECT_INTERP^Interpretation^L||Moderate reversible ischemia in the inferior wall, consistent with RCA territory. Mildly reduced stress LVEF.||||||F
```

---

## 14. ORU^R01 - pacemaker interrogation

```
MSH|^~\&|MACCABI_CVIS|MACCABI_CARD|MACCABI_EMR|MACCABI_CL|20260312110000||ORU^R01|MCV000014|P|2.4
PID|||582736941^^^IL_MOH^NI~M80008^^^MACCABI^MR||Petrov^Boris^Mikhail^^Mr.||19720618|M|||HaShachar 5^^Ashdod^^7758037^IL||^PRN^CP^054-228-3447
PV1||O|CARD^100^^MACCABI_CL||||44574^Ben-Ami^Tal^^^Dr.||||||||||||VN80008
ORC|RE|ORD4008^MACCABI_EMR|RES4008^MACCABI_CVIS
OBR|1|ORD4008^MACCABI_EMR|RES4008^MACCABI_CVIS|93288^Pacemaker Interrogation^CPT|||20260312090000|||||||||44574^Ben-Ami^Tal^^^Dr.|||||||F
OBX|1|CE|PM_TYPE^Device Type^L||DDD^Dual-Chamber Pacemaker^L||||||F
OBX|2|ST|PM_MODEL^Device Model^L||Medtronic Azure XT DR||||||F
OBX|3|NM|PM_BATT^Battery Voltage^L||2.78|V||||F
OBX|4|NM|PM_LEAD_A^Atrial Lead Impedance^L||520|ohms||||F
OBX|5|NM|PM_LEAD_V^Ventricular Lead Impedance^L||480|ohms||||F
OBX|6|NM|PM_PCT_PACE_A^Atrial Pacing %^L||45|%||||F
OBX|7|NM|PM_PCT_PACE_V^Ventricular Pacing %^L||12|%||||F
OBX|8|ST|PM_INTERP^Interpretation^L||Device functioning normally. Battery adequate. No lead issues detected.||||||F
```

---

## 15. ORM^O01 - transesophageal echo order

```
MSH|^~\&|MACCABI_EMR|MACCABI_CL|MACCABI_CVIS|MACCABI_CARD|20260313090000||ORM^O01|MCV000015|P|2.4
PID|||693158274^^^IL_MOH^NI~M90009^^^MACCABI^MR||Bitton^Rachel^Esther^^Mrs.||19680309|F|||HaNevi'im 14^^Jerusalem^^9423614^IL||^PRN^CP^052-876-4521
PV1||I|CARD^500^^MACCABI_HOSP||||44575^Tadesse^Yonatan^^^Dr.||||||||||||VN90009
ORC|NW|ORD4009^MACCABI_EMR|||||^^^20260313090000^^R
OBR|1|ORD4009^MACCABI_EMR||93312^Transesophageal Echocardiography^CPT|||20260313083000||||A|||||44575^Tadesse^Yonatan^^^Dr.
```

---

## 16. ORU^R01 - TEE result

```
MSH|^~\&|MACCABI_CVIS|MACCABI_CARD|MACCABI_EMR|MACCABI_CL|20260313140000||ORU^R01|MCV000016|P|2.4
PID|||693158274^^^IL_MOH^NI~M90009^^^MACCABI^MR||Bitton^Rachel^Esther^^Mrs.||19680309|F|||HaNevi'im 14^^Jerusalem^^9423614^IL||^PRN^CP^052-876-4521
PV1||I|CARD^500^^MACCABI_HOSP||||44575^Tadesse^Yonatan^^^Dr.||||||||||||VN90009
ORC|RE|ORD4009^MACCABI_EMR|RES4009^MACCABI_CVIS
OBR|1|ORD4009^MACCABI_EMR|RES4009^MACCABI_CVIS|93312^Transesophageal Echocardiography^CPT|||20260313083000|||||||||44575^Tadesse^Yonatan^^^Dr.|||||||F
OBX|1|NM|TEE_LVEF^LVEF^L||60|%|55-70|N|||F
OBX|2|ST|TEE_LAA^Left Atrial Appendage^L||No thrombus visualized||||||F
OBX|3|ST|TEE_MV^Mitral Valve^L||Moderate regurgitation, posterior leaflet prolapse||||||F
OBX|4|ST|TEE_AV^Aortic Valve^L||Normal trileaflet valve||||||F
OBX|5|ST|TEE_INTERP^Impression^L||Moderate MR due to posterior leaflet prolapse. No LAA thrombus. Normal LV function.||||||F
```

---

## 17. ORU^R01 - cardiac CT calcium score

```
MSH|^~\&|MACCABI_CVIS|MACCABI_CARD|MACCABI_EMR|MACCABI_CL|20260314110000||ORU^R01|MCV000017|P|2.4
PID|||417283659^^^IL_MOH^NI~M10010^^^MACCABI^MR||Edri^Shimon^Avraham^^Mr.||19950512|M|||Allenby 77^^Tel Aviv^^6513215^IL||^PRN^CP^053-446-5728
PV1||O|CARD^100^^MACCABI_CL||||44576^Rabinovich^Igor^^^Dr.||||||||||||VN10010
ORC|RE|ORD4010^MACCABI_EMR|RES4010^MACCABI_CVIS
OBR|1|ORD4010^MACCABI_EMR|RES4010^MACCABI_CVIS|75571^CT Coronary Calcium Score^CPT|||20260314090000|||||||||44576^Rabinovich^Igor^^^Dr.|||||||F
OBX|1|NM|CACS_TOTAL^Total Agatston Score^L||185||||||F
OBX|2|NM|CACS_LAD^LAD Score^L||110||||||F
OBX|3|NM|CACS_LCX^LCx Score^L||25||||||F
OBX|4|NM|CACS_RCA^RCA Score^L||50||||||F
OBX|5|NM|CACS_PCTL^Percentile for Age/Sex^L||75|%||||F
OBX|6|ST|CACS_INTERP^Interpretation^L||Moderate coronary artery calcification. 75th percentile for age and sex.||||||F
```

---

## 18. ORU^R01 - event monitor (30-day) result

```
MSH|^~\&|MACCABI_CVIS|MACCABI_CARD|MACCABI_EMR|MACCABI_CL|20260315140000||ORU^R01|MCV000018|P|2.4
PID|||528419367^^^IL_MOH^NI~M20011^^^MACCABI^MR||Vaknin^Oded^Eliyahu^^Mr.||19800101|M|||Arlozorov 35^^Haifa^^3301521^IL||^PRN^CP^050-668-2734
PV1||O|CARD^100^^MACCABI_CL||||44577^Mansour^Sami^^^Dr.||||||||||||VN20011
ORC|RE|ORD4011^MACCABI_EMR|RES4011^MACCABI_CVIS
OBR|1|ORD4011^MACCABI_EMR|RES4011^MACCABI_CVIS|93270^30-Day Event Monitor^CPT|||20260215083000|||||||||44577^Mansour^Sami^^^Dr.|||||||F
OBX|1|NM|EM_EVENTS^Total Events Recorded^L||12||||||F
OBX|2|NM|EM_AF_EPISODES^AF Episodes^L||3||||||F
OBX|3|NM|EM_AF_BURDEN^AF Burden^L||4.2|%||||F
OBX|4|NM|EM_MAX_PAUSE^Maximum Pause^L||2.1|sec||||F
OBX|5|ST|EM_INTERP^Interpretation^L||Paroxysmal atrial fibrillation with 4.2% burden. No significant pauses. Consider anticoagulation per CHA2DS2-VASc.||||||F
```

---

## 19. SIU^S12 - cardiology appointment scheduling

```
MSH|^~\&|MACCABI_CVIS|MACCABI_CARD|MACCABI_EMR|MACCABI_CL|20260316080000||SIU^S12|MCV000019|P|2.4
PID|||618293574^^^IL_MOH^NI~M30012^^^MACCABI^MR||Aslan^Yaron^Tomer^^Mr.||19880315|M|||Balfour 22^^Bat Yam^^5930002^IL||^PRN^CP^052-218-4936
PV1||O|CARD^100^^MACCABI_CL||||44578^Goldberg^Ariel^^^Dr.||||||||||||VN30012
SCH|APT50001|APT50001||||ROUTINE^Routine^HL70276|ECHO^Echocardiography^L|||||45|min|^^^20260323090000^20260323094500
AIS|1||93306^Transthoracic Echo^CPT|20260323090000|||45|min
```

---

## 20. ACK - acknowledgment

```
MSH|^~\&|MACCABI_CVIS|MACCABI_CARD|MACCABI_EMR|MACCABI_CL|20260317090100||ACK|MCV000020|P|2.4
MSA|AA|ORD4001|Order received and scheduled
```
