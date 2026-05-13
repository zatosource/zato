# MetaVision (iMDsoft) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - ICU admission from HIS

```
MSH|^~\&|CHAMELEON|SHEBA_MC|METAVISION|SHEBA_ICU|20260301080000||ADT^A01^ADT_A01|MV000001|P|2.4
EVN|A01|20260301080000
PID|||382716495^^^IL_MOH^NI||Cohen^Yael^Tirza^^Mrs.||19780315|F|||Hatzionut 47^^Haifa^^3303125^IL||^PRN^CP^052-381-7264
PV1||I|ICU^101^A^SHEBA||||30456^Khoury^Samir^^^Dr.||40567^Friedman^Sigalit^^^Dr.||ICU||||||||VN10001|||||||||||||||||||||||20260301080000
```

---

## 2. ADT^A03 - ICU discharge to ward

```
MSH|^~\&|METAVISION|SHEBA_ICU|CHAMELEON|SHEBA_MC|20260305140000||ADT^A03^ADT_A03|MV000002|P|2.4
EVN|A03|20260305140000
PID|||382716495^^^IL_MOH^NI||Cohen^Yael^Tirza^^Mrs.||19780315|F|||Hatzionut 47^^Haifa^^3303125^IL||^PRN^CP^052-381-7264
PV1||I|MED^301^A^SHEBA||||30456^Khoury^Samir^^^Dr.||40567^Friedman^Sigalit^^^Dr.||ICU^101^A^SHEBA||||||||VN10001||||||||||||||||||||||||||20260305140000
```

---

## 3. ORU^R01 - ventilator parameters

```
MSH|^~\&|METAVISION|SHEBA_ICU|CHAMELEON|SHEBA_MC|20260301120000||ORU^R01|MV000003|P|2.4
PID|||382716495^^^IL_MOH^NI||Cohen^Yael^Tirza^^Mrs.||19780315|F|||Hatzionut 47^^Haifa^^3303125^IL||^PRN^CP^052-381-7264
PV1||I|ICU^101^A^SHEBA||||30456^Khoury^Samir^^^Dr.||||||||||||VN10001
OBR|1|||VENT^Ventilator Parameters^MV|||20260301120000
OBX|1|NM|VENT_MODE^Ventilation Mode^MV||SIMV^SIMV^MV||||||F
OBX|2|NM|VENT_TV^Tidal Volume^MV||450|mL||||F
OBX|3|NM|VENT_RR^Respiratory Rate^MV||14|/min||||F
OBX|4|NM|VENT_PEEP^PEEP^MV||8|cmH2O||||F
OBX|5|NM|VENT_FIO2^FiO2^MV||0.45||||||F
OBX|6|NM|VENT_PIP^Peak Inspiratory Pressure^MV||22|cmH2O||||F
```

---

## 4. ORU^R01 - hemodynamic monitoring

```
MSH|^~\&|METAVISION|HADASSAH_ICU|CHAMELEON|HADASSAH_MC|20260302100000||ORU^R01|MV000004|P|2.4
PID|||517624893^^^IL_MOH^NI||Mizrahi^Avi^Yaakov^^Mr.||19650722|M|||Ben Yehuda 18^^Tel Aviv^^6380118^IL||^PRN^CP^054-768-4321
PV1||I|ICU^201^B^HADASSAH||||50678^Bitton^Ronen^^^Dr.||||||||||||VN20002
OBR|1|||HEMO^Hemodynamic Monitoring^MV|||20260302100000
OBX|1|NM|HR^Heart Rate^MV||92|/min|60-100|N|||F
OBX|2|NM|SBP^Systolic BP^MV||118|mmHg|90-140|N|||F
OBX|3|NM|DBP^Diastolic BP^MV||72|mmHg|60-90|N|||F
OBX|4|NM|MAP^Mean Arterial Pressure^MV||87|mmHg|70-105|N|||F
OBX|5|NM|CVP^Central Venous Pressure^MV||8|mmHg|2-8|N|||F
OBX|6|NM|SPO2^Oxygen Saturation^MV||96|%|95-100|N|||F
```

---

## 5. ORU^R01 - fluid balance summary

```
MSH|^~\&|METAVISION|RAMBAM_ICU|CHAMELEON|RAMBAM_MC|20260303060000||ORU^R01|MV000005|P|2.4
PID|||692415738^^^IL_MOH^NI||Mansour^Fatima^Aisha^^Mrs.||19900110|F|||HaGalil 18^^Nazareth^^1610203^IL||^PRN^CP^050-249-7163
PV1||I|ICU^301^A^RAMBAM||||10234^Levi^Yaakov^^^Dr.||||||||||||VN30003
OBR|1|||FLUID^Fluid Balance 24hr^MV|||20260303060000
OBX|1|NM|INTAKE_IV^IV Intake^MV||2450|mL||||F
OBX|2|NM|INTAKE_PO^PO Intake^MV||350|mL||||F
OBX|3|NM|OUTPUT_URINE^Urine Output^MV||1850|mL||||F
OBX|4|NM|OUTPUT_DRAIN^Drain Output^MV||220|mL||||F
OBX|5|NM|BALANCE^Net Fluid Balance^MV||+730|mL||||F
```

---

## 6. ORU^R01 - neurological assessment (GCS)

```
MSH|^~\&|METAVISION|ICHILOV_ICU|CHAMELEON|ICHILOV_MC|20260304080000||ORU^R01|MV000006|P|2.4
PID|||741296835^^^IL_MOH^NI||Dahan^Eli^Reuven^^Mr.||19550830|M|||King George 15^^Jerusalem^^9426215^IL||^PRN^PH^02-624-3781
PV1||I|ICU^401^A^ICHILOV||||40567^Goldstein^Daniel^^^Dr.||||||||||||VN40004
OBR|1|||NEURO^Neurological Assessment^MV|||20260304080000
OBX|1|NM|9267-6^GCS Total^LN||11||||||F
OBX|2|NM|9268-4^GCS Eye^LN||3||||||F
OBX|3|NM|9270-0^GCS Verbal^LN||4||||||F
OBX|4|NM|9269-2^GCS Motor^LN||4||||||F
OBX|5|NM|PUPIL_L^Left Pupil Size^MV||3|mm||||F
OBX|6|NM|PUPIL_R^Right Pupil Size^MV||3|mm||||F
OBX|7|CE|PUPIL_REACT^Pupil Reactivity^MV||BRISK^Brisk bilateral^MV||||||F
```

---

## 7. ORM^O01 - medication infusion order

```
MSH|^~\&|METAVISION|SHEBA_ICU|PHARM_SYS|SHEBA_PHARM|20260305090000||ORM^O01|MV000007|P|2.4
PID|||826491357^^^IL_MOH^NI||Peretz^Sarah^Leah^^Mrs.||19881205|F|||Weizmann 8^^Rehovot^^7610001^IL||^PRN^CP^058-345-7218
PV1||I|ICU^101^A^SHEBA||||30456^Khoury^Samir^^^Dr.||||||||||||VN50005
ORC|NW|ORD2001^METAVISION|||||^^^20260305090000^^R
RXO|1|00409-1176-10^Norepinephrine 4mg/250mL D5W^NDC||mcg/min|IV|||CONT|||2||20260305090000
RXR|IV^Intravenous^HL70162||CVC^Central Venous Catheter^MV
```

---

## 8. ORU^R01 - sedation assessment (RASS)

```
MSH|^~\&|METAVISION|HADASSAH_ICU|CHAMELEON|HADASSAH_MC|20260306140000||ORU^R01|MV000008|P|2.4
PID|||915362847^^^IL_MOH^NI||Azoulay^Yosef^Haim^^Mr.||19700415|M|||Kaplan 30^^Be'er Sheva^^8425503^IL||^PRN^CP^052-568-9012
PV1||I|ICU^201^B^HADASSAH||||50678^Bitton^Ronen^^^Dr.||||||||||||VN60006
OBR|1|||SEDAT^Sedation Assessment^MV|||20260306140000
OBX|1|NM|RASS^Richmond Agitation-Sedation Scale^MV||-2||||||F
OBX|2|NM|CPOT^Critical-Care Pain Observation Tool^MV||3||||||F
OBX|3|CE|SEDAT_DRUG^Sedation Agent^MV||PROP^Propofol^MV||||||F
OBX|4|NM|SEDAT_RATE^Infusion Rate^MV||30|mcg/kg/min||||F
```

---

## 9. ORU^R01 - arterial blood gas with embedded PDF (base64 ED)

```
MSH|^~\&|METAVISION|RAMBAM_ICU|CHAMELEON|RAMBAM_MC|20260307063000||ORU^R01|MV000009|P|2.4
PID|||374918526^^^IL_MOH^NI||Stern^Devorah^Bracha^^Mrs.||19820920|F|||Jabotinsky 40^^Ramat Gan^^5252007^IL||^PRN^CP^050-113-3445
PV1||I|ICU^301^A^RAMBAM||||10234^Levi^Yaakov^^^Dr.||||||||||||VN70007
OBR|1|||ABG^Arterial Blood Gas^MV|||20260307063000
OBX|1|NM|2744-1^pH^LN||7.25||7.35-7.45|LL|||F
OBX|2|NM|2019-8^pCO2^LN||62|mmHg|35-45|HH|||F
OBX|3|NM|2703-7^pO2^LN||58|mmHg|80-100|LL|||F
OBX|4|NM|1959-6^HCO3^LN||26|mmol/L|22-26|N|||F
OBX|5|NM|2713-6^Base Excess^LN||-2|mmol/L|-2 to +2|N|||F
OBX|6|NM|2708-6^O2 Sat^LN||87|%|95-100|LL|||F
OBX|7|ED|PDF^ABG Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvUmVzb3VyY2VzIDw8ID4+ID4+CmVuZG9iagp4cmVmCjAgNAowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNCAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMjE2CiUlRU9GCg==||||||F
```

---

## 10. ORU^R01 - ICU daily summary with embedded PDF (base64 ED)

```
MSH|^~\&|METAVISION|SHEBA_ICU|CHAMELEON|SHEBA_MC|20260308060000||ORU^R01|MV000010|P|2.4
PID|||582714639^^^IL_MOH^NI||Petrov^Boris^Mikhail^^Mr.||19720618|M|||HaShachar 5^^Ashdod^^7758037^IL||^PRN^CP^054-228-3447
PV1||I|ICU^101^A^SHEBA||||30456^Khoury^Samir^^^Dr.||||||||||||VN80008
OBR|1|||DAILY^ICU Daily Summary^MV|||20260308060000
OBX|1|NM|APACHE^APACHE II Score^MV||18||||||F
OBX|2|NM|SOFA^SOFA Score^MV||7||||||F
OBX|3|NM|ICU_DAY^ICU Day^MV||5||||||F
OBX|4|ED|PDF^ICU Daily Summary PDF^L||^application^pdf^Base64^JVBERi0xLjUKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvUmVzb3VyY2VzIDw8ID4+ID4+CmVuZG9iagp4cmVmCjAgNAowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNCAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMjE2CiUlRU9GCg==||||||F
```

---

## 11. ADT^A02 - intra-ICU bed transfer

```
MSH|^~\&|METAVISION|ICHILOV_ICU|CHAMELEON|ICHILOV_MC|20260309100000||ADT^A02^ADT_A02|MV000011|P|2.4
EVN|A02|20260309100000
PID|||693158274^^^IL_MOH^NI||Bitton^Rachel^Esther^^Mrs.||19680309|F|||HaNevi'im 14^^Jerusalem^^9423614^IL||^PRN^CP^052-876-4521
PV1||I|ICU^402^B^ICHILOV||||40567^Goldstein^Daniel^^^Dr.||50678^Bitton^Ronen^^^Dr.||ICU^401^A^ICHILOV||||||||VN90009|||||||||||||||||||||||20260309100000
```

---

## 12. ORU^R01 - nutrition assessment

```
MSH|^~\&|METAVISION|HADASSAH_ICU|CHAMELEON|HADASSAH_MC|20260310080000||ORU^R01|MV000012|P|2.4
PID|||417286953^^^IL_MOH^NI||Edri^Shimon^Avraham^^Mr.||19950512|M|||Allenby 77^^Tel Aviv^^6513215^IL||^PRN^CP^053-446-5728
PV1||I|ICU^201^B^HADASSAH||||50678^Bitton^Ronen^^^Dr.||||||||||||VN10010
OBR|1|||NUTR^Nutrition Assessment^MV|||20260310080000
OBX|1|NM|KCAL_GOAL^Caloric Goal^MV||1800|kcal/day||||F
OBX|2|NM|KCAL_ACTUAL^Calories Delivered^MV||1200|kcal/day||||F
OBX|3|NM|PROT_GOAL^Protein Goal^MV||90|g/day||||F
OBX|4|NM|PROT_ACTUAL^Protein Delivered^MV||60|g/day||||F
OBX|5|CE|FEED_ROUTE^Feeding Route^MV||NGT^Nasogastric Tube^MV||||||F
```

---

## 13. ORU^R01 - pressure injury assessment

```
MSH|^~\&|METAVISION|RAMBAM_ICU|CHAMELEON|RAMBAM_MC|20260311080000||ORU^R01|MV000013|P|2.4
PID|||528419367^^^IL_MOH^NI||Vaknin^Oded^Eliyahu^^Mr.||19800101|M|||Arlozorov 35^^Haifa^^3301521^IL||^PRN^CP^050-668-2734
PV1||I|ICU^301^A^RAMBAM||||10234^Levi^Yaakov^^^Dr.||||||||||||VN10011
OBR|1|||BRADEN^Braden Scale Assessment^MV|||20260311080000
OBX|1|NM|BRADEN_TOTAL^Braden Total Score^MV||12||||||F
OBX|2|NM|BRADEN_SENS^Sensory Perception^MV||2||||||F
OBX|3|NM|BRADEN_MOIST^Moisture^MV||2||||||F
OBX|4|NM|BRADEN_ACT^Activity^MV||1||||||F
OBX|5|NM|BRADEN_MOB^Mobility^MV||2||||||F
OBX|6|NM|BRADEN_NUTR^Nutrition^MV||2||||||F
OBX|7|NM|BRADEN_FRIC^Friction and Shear^MV||3||||||F
```

---

## 14. ORU^R01 - vasopressor titration record

```
MSH|^~\&|METAVISION|SHEBA_ICU|CHAMELEON|SHEBA_MC|20260312100000||ORU^R01|MV000014|P|2.4
PID|||618293574^^^IL_MOH^NI||Aslan^Yaron^Tomer^^Mr.||19880315|M|||Balfour 22^^Bat Yam^^5930002^IL||^PRN^CP^052-218-4936
PV1||I|ICU^101^A^SHEBA||||30456^Khoury^Samir^^^Dr.||||||||||||VN40012
OBR|1|||VASO^Vasopressor Management^MV|||20260312100000
OBX|1|CE|VASO_DRUG1^Vasopressor 1^MV||NOREPI^Norepinephrine^MV||||||F
OBX|2|NM|VASO_RATE1^Norepinephrine Rate^MV||0.15|mcg/kg/min||||F
OBX|3|NM|MAP_TARGET^MAP Target^MV||65|mmHg||||F
OBX|4|NM|MAP_ACTUAL^MAP Actual^MV||68|mmHg||||F
OBX|5|NM|LACTATE^Lactate^MV||3.2|mmol/L|<2.0|H|||F
```

---

## 15. ADT^A08 - patient weight update

```
MSH|^~\&|METAVISION|ICHILOV_ICU|CHAMELEON|ICHILOV_MC|20260313060000||ADT^A08^ADT_A01|MV000015|P|2.4
EVN|A08|20260313060000
PID|||357128649^^^IL_MOH^NI||Sabag^Daniel^Michael^^Mr.||19910203|M|||Herzl 100^^Be'er Sheva^^8410901^IL||^PRN^CP^058-991-2374
PV1||I|ICU^401^A^ICHILOV||||40567^Goldstein^Daniel^^^Dr.||||||||||||VN50013
OBX|1|NM|3141-9^Body Weight^LN||78.5|kg||||F
OBX|2|NM|3137-7^Body Height^LN||175|cm||||F
OBX|3|NM|39156-5^BMI^LN||25.6|kg/m2||||F
```

---

## 16. ORU^R01 - renal replacement therapy record

```
MSH|^~\&|METAVISION|HADASSAH_ICU|CHAMELEON|HADASSAH_MC|20260314080000||ORU^R01|MV000016|P|2.4
PID|||512837694^^^IL_MOH^NI||Tzur^Liora^Galit^^Mrs.||19850714|F|||Ben Gurion 20^^Kfar Saba^^4433501^IL||^PRN^CP^052-334-4556
PV1||I|ICU^201^B^HADASSAH||||50678^Bitton^Ronen^^^Dr.||||||||||||VN60014
OBR|1|||CRRT^Continuous Renal Replacement Therapy^MV|||20260314080000
OBX|1|CE|CRRT_MODE^CRRT Mode^MV||CVVHDF^CVVHDF^MV||||||F
OBX|2|NM|CRRT_BFR^Blood Flow Rate^MV||200|mL/min||||F
OBX|3|NM|CRRT_EFF^Effluent Rate^MV||35|mL/kg/hr||||F
OBX|4|NM|CRRT_UF^Ultrafiltration Rate^MV||100|mL/hr||||F
OBX|5|NM|CRRT_LIFE^Filter Life^MV||18|hours||||F
```

---

## 17. ORU^R01 - ventilator weaning trial

```
MSH|^~\&|METAVISION|RAMBAM_ICU|CHAMELEON|RAMBAM_MC|20260315100000||ORU^R01|MV000017|P|2.4
PID|||248619375^^^IL_MOH^NI||Tadesse^Abebe^Yonatan^^Mr.||19630510|M|||HaTikva 11^^Petah Tikva^^4924518^IL||^PRN^CP^050-336-4583
PV1||I|ICU^301^A^RAMBAM||||10234^Levi^Yaakov^^^Dr.||||||||||||VN70015
OBR|1|||SBT^Spontaneous Breathing Trial^MV|||20260315100000
OBX|1|NM|SBT_DURATION^Trial Duration^MV||30|min||||F
OBX|2|NM|SBT_RR^Respiratory Rate^MV||22|/min||||F
OBX|3|NM|SBT_TV^Tidal Volume^MV||380|mL||||F
OBX|4|NM|SBT_RSBI^Rapid Shallow Breathing Index^MV||58|breaths/min/L||||F
OBX|5|CE|SBT_RESULT^SBT Outcome^MV||PASS^Passed^MV||||||F
```

---

## 18. ORU^R01 - central line bundle compliance

```
MSH|^~\&|METAVISION|SHEBA_ICU|CHAMELEON|SHEBA_MC|20260316080000||ORU^R01|MV000018|P|2.4
PID|||783619425^^^IL_MOH^NI||Bar-On^Yael^Naomi^^Mrs.||19790305|F|||HaAtzmaut 60^^Rehovot^^7610302^IL||^PRN^CP^054-557-6783
PV1||I|ICU^101^A^SHEBA||||30456^Khoury^Samir^^^Dr.||||||||||||VN80016
OBR|1|||CLABSI^Central Line Bundle^MV|||20260316080000
OBX|1|CE|CL_HAND^Hand Hygiene^MV||Y^Yes^MV||||||F
OBX|2|CE|CL_BARRIER^Full Barrier^MV||Y^Yes^MV||||||F
OBX|3|CE|CL_CHLOR^Chlorhexidine Prep^MV||Y^Yes^MV||||||F
OBX|4|CE|CL_SITE^Optimal Site^MV||SUBCL^Subclavian^MV||||||F
OBX|5|CE|CL_REVIEW^Daily Review^MV||Y^Yes^MV||||||F
OBX|6|NM|CL_DAYS^Line Days^MV||3||||||F
```

---

## 19. ADT^A04 - perioperative registration

```
MSH|^~\&|CHAMELEON|ICHILOV_MC|METAVISION|ICHILOV_OR|20260317070000||ADT^A04^ADT_A01|MV000019|P|2.4
EVN|A04|20260317070000
PID|||891372456^^^IL_MOH^NI||Naor^Gilad^Ariel^^Mr.||19750905|M|||Dizengoff 120^^Tel Aviv^^6433701^IL||^PRN^CP^050-778-9012
PV1||O|OR^201^^ICHILOV||||40567^Goldstein^Daniel^^^Dr.||||SURG||||||||VN90017|||||||||||||||||||||||20260317070000
```

---

## 20. ORU^R01 - anesthesia induction record

```
MSH|^~\&|METAVISION|ICHILOV_OR|CHAMELEON|ICHILOV_MC|20260317080000||ORU^R01|MV000020|P|2.4
PID|||891372456^^^IL_MOH^NI||Naor^Gilad^Ariel^^Mr.||19750905|M|||Dizengoff 120^^Tel Aviv^^6433701^IL||^PRN^CP^050-778-9012
PV1||O|OR^201^^ICHILOV||||40567^Goldstein^Daniel^^^Dr.||||SURG||||||||VN90017
OBR|1|||ANES^Anesthesia Induction^MV|||20260317080000
OBX|1|CE|ANES_TYPE^Anesthesia Type^MV||GA^General Anesthesia^MV||||||F
OBX|2|CE|ANES_AIRWAY^Airway^MV||ETT^Endotracheal Tube^MV||||||F
OBX|3|NM|ANES_ETT_SIZE^ETT Size^MV||7.5|mm||||F
OBX|4|CE|ANES_INDUC^Induction Agent^MV||PROP^Propofol^MV||||||F
OBX|5|NM|ANES_PROP_DOSE^Propofol Dose^MV||200|mg||||F
OBX|6|CE|ANES_NMB^Neuromuscular Blocker^MV||ROC^Rocuronium^MV||||||F
OBX|7|NM|ANES_ROC_DOSE^Rocuronium Dose^MV||50|mg||||F
```
