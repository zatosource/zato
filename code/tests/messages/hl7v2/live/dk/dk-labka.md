# LABKA II (Dedalus) - real HL7v2 ER7 messages

---

## 1. ORU^R01 - Komplet blodtælling (complete blood count result)

```
MSH|^~\&|LABKA|KBA_AAUH|COLUMNA_CIS|AALBORG_UH|20260401140000||ORU^R01^ORU_R01|LK00001|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0103787866^^^CPR^NNDN||Krogh^Ulla^Gerda^^||19780301|F|||Skanderborgvej 149^^København K^^1050^DK||^^PH^+4544896074
PV1||I|AAUH^MED^301^A1||||12001^Mortensen^Anne^^^Dr.|||MED||||||||||AAUH202604010001
ORC|RE|ORD20260401001^COLUMNA_CIS||||||20260401140000
OBR|1|ORD20260401001^COLUMNA_CIS||CBC^Komplet blodtælling^LN|||20260401080000||||||||12001^Mortensen^Anne^^^Dr.||||||20260401140000|||F
OBX|1|NM|WBC^Leukocytter^LN||6.8|10*9/L|3.5-10.0|N|||F
OBX|2|NM|RBC^Erytrocytter^LN||4.5|10*12/L|3.9-5.5|N|||F
OBX|3|NM|HGB^Hæmoglobin^LN||8.1|mmol/L|7.3-10.0|N|||F
OBX|4|NM|HCT^Hæmatokrit^LN||0.39|L/L|0.36-0.46|N|||F
OBX|5|NM|PLT^Trombocytter^LN||210|10*9/L|145-390|N|||F
OBX|6|NM|MCV^Middelcellevolumen^LN||86|fL|82-98|N|||F
```

---

## 2. ORU^R01 - Elektrolytter (electrolyte panel result)

```
MSH|^~\&|LABKA|KBA_RH|EPIC|RIGSHOSPITALET|20260402101500||ORU^R01^ORU_R01|LK00002|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1509659693^^^CPR^NNDN||Vinther^Peter^Aage^^||19650915|M|||Skovvej 10^^København K^^1050^DK||^^PH^+4554169683
PV1||I|RH^NEF^N4021^S01||||22002^Christiansen^Anders^^^Dr.|||NEF||||||||||RH202604020001
ORC|RE|ORD20260402001^EPIC||||||20260402101500
OBR|1|ORD20260402001^EPIC||ELEC^Elektrolytter^LN|||20260402083000||||||||22002^Christiansen^Anders^^^Dr.||||||20260402101500|||F
OBX|1|NM|NA^Natrium^LN||128|mmol/L|137-145|LL|||F
OBX|2|NM|K^Kalium^LN||5.6|mmol/L|3.5-5.0|H|||F
OBX|3|NM|CL^Klorid^LN||96|mmol/L|98-107|L|||F
OBX|4|NM|CO2^Total CO2^LN||18|mmol/L|22-29|L|||F
```

---

## 3. ORU^R01 - Levertal (liver function result)

```
MSH|^~\&|LABKA|KBA_OUH|BCC|OUH|20260403143000||ORU^R01^ORU_R01|LK00003|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2207739844^^^CPR^NNDN||Bang^Trine^Yrsa^^||19730722|F|||Mejlgade 94^^København K^^1260^DK||^^PH^+4581886427
PV1||I|OUH^MED^A305^S02||||33003^Krogh^Henrik^^^Dr.|||MED||||||||||OUH202604030001
ORC|RE|ORD20260403001^BCC||||||20260403143000
OBR|1|ORD20260403001^BCC||LFT^Leverfunktionsprøver^LN|||20260403083000||||||||33003^Krogh^Henrik^^^Dr.||||||20260403143000|||F
OBX|1|NM|ALAT^Alanin-aminotransferase^LN||95|U/L|10-45|H|||F
OBX|2|NM|ASAT^Aspartat-aminotransferase^LN||78|U/L|15-35|H|||F
OBX|3|NM|ALP^Basisk fosfatase^LN||145|U/L|35-105|H|||F
OBX|4|NM|GGT^Gamma-glutamyltransferase^LN||188|U/L|10-80|H|||F
OBX|5|NM|BILIRUB^Bilirubin, total^LN||32|umol/L|5-25|H|||F
```

---

## 4. ORU^R01 - Thyroidea (thyroid function result)

```
MSH|^~\&|LABKA|KBA_AUH|COLUMNA_CIS|AARHUS_UH|20260404100000||ORU^R01^ORU_R01|LK00004|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1203884930^^^CPR^NNDN||Jensen^Signe^Frederikke^^||19880312|F|||Banegårdspladsen 58^^Skive^^7800^DK||^^PH^+4567783028
PV1||O|AUH^END^AMB01||||44004^Lund^Niels^^^Dr.|||END||||||||||AUH202604040001
ORC|RE|ORD20260404001^COLUMNA_CIS||||||20260404100000
OBR|1|ORD20260404001^COLUMNA_CIS||THYR^Thyroideatal^LN|||20260404083000||||||||44004^Lund^Niels^^^Dr.||||||20260404100000|||F
OBX|1|NM|TSH^Thyreoideastimulerende hormon^LN||8.7|mIU/L|0.27-4.20|H|||F
OBX|2|NM|FT4^Frit thyroxin^LN||9.2|pmol/L|12.0-22.0|L|||F
OBX|3|NM|FT3^Frit trijodthyronin^LN||2.8|pmol/L|3.1-6.8|L|||F
```

---

## 5. ORU^R01 - Koagulation (coagulation result)

```
MSH|^~\&|LABKA|KBA_RH|EPIC|RIGSHOSPITALET|20260405141500||ORU^R01^ORU_R01|LK00005|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0608714281^^^CPR^NNDN||Mortensen^Allan^Otto^^||19710806|M|||Engvej 123^^København SV^^2450^DK||^^PH^+4586282134
PV1||I|RH^KIR^K3041^S03||||55005^Andersen^Preben^^^Dr.|||KIR||||||||||RH202604050001
ORC|RE|ORD20260405001^EPIC||||||20260405141500
OBR|1|ORD20260405001^EPIC||KOAG^Koagulationstal^LN|||20260405083000||||||||55005^Andersen^Preben^^^Dr.||||||20260405141500|||F
OBX|1|NM|INR^International Normalised Ratio^LN||1.1||0.8-1.2|N|||F
OBX|2|NM|APTT^Aktiveret partiel tromboplastintid^LN||31|sek|25-38|N|||F
OBX|3|NM|FBLOOD^Fibrinogen^LN||3.2|g/L|1.8-4.0|N|||F
```

---

## 6. ORU^R01 - Blodsukker og HbA1c (glucose and HbA1c result)

```
MSH|^~\&|LABKA|KBA_OUH|BCC|OUH|20260406091000||ORU^R01^ORU_R01|LK00006|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1711627331^^^CPR^NNDN||Hansen^Kasper^Egon^^||19621117|M|||Strandgade 227^^Odense N^^5200^DK||^^PH^+4562505094
PV1||O|OUH^END^AMB01||||66006^Kristensen^Oliver^^^Dr.|||END||||||||||OUH202604060001
ORC|RE|ORD20260406001^BCC||||||20260406091000
OBR|1|ORD20260406001^BCC||GLUC^Faste-glukose og HbA1c^LN|||20260406080000||||||||66006^Kristensen^Oliver^^^Dr.||||||20260406091000|||F
OBX|1|NM|GLUC^P-Glukose (faste)^LN||9.8|mmol/L|4.2-6.3|H|||F
OBX|2|NM|HBA1C^HbA1c^LN||62|mmol/mol|<48|H|||F
```

---

## 7. ORU^R01 - Lipidprofil (lipid panel result)

```
MSH|^~\&|LABKA|KBA_AUH|COLUMNA_CIS|AARHUS_UH|20260407101500||ORU^R01^ORU_R01|LK00007|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0309554169^^^CPR^NNDN||Mikkelsen^Peter^Gunnar^^||19550903|M|||Mejlgade 115^^Vordingborg^^4760^DK||^^PH^+4538684090
PV1||O|AUH^KAR^AMB01||||77007^Petersen^Jørgen^^^Dr.|||KAR||||||||||AUH202604070001
ORC|RE|ORD20260407001^COLUMNA_CIS||||||20260407101500
OBR|1|ORD20260407001^COLUMNA_CIS||LIPID^Lipidprofil^LN|||20260407083000||||||||77007^Petersen^Jørgen^^^Dr.||||||20260407101500|||F
OBX|1|NM|CHOL^Total kolesterol^LN||6.8|mmol/L|<5.0|H|||F
OBX|2|NM|LDL^LDL-kolesterol^LN||4.5|mmol/L|<3.0|H|||F
OBX|3|NM|HDL^HDL-kolesterol^LN||0.9|mmol/L|>1.0|L|||F
OBX|4|NM|TRIG^Triglycerider^LN||3.2|mmol/L|<2.0|H|||F
```

---

## 8. ORU^R01 - Blodgas (blood gas result)

```
MSH|^~\&|LABKA|KBA_AAUH|COLUMNA_CIS|AALBORG_UH|20260408023000||ORU^R01^ORU_R01|LK00008|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2504906828^^^CPR^NNDN||Holm^Line^Lykke^^||19900425|F|||Munkebjergvej 81^^Charlottenlund^^2920^DK||^^CP^+4520714139
PV1||E|AAUH^AKM^101^A2||||88008^Vinther^Kasper^^^Dr.|||AKM||||||||||AAUH202604080001
ORC|RE|ORD20260408001^COLUMNA_CIS||||||20260408023000
OBR|1|ORD20260408001^COLUMNA_CIS||ABGAS^Arteriel blodgas^LN|||20260408020000||||||||88008^Vinther^Kasper^^^Dr.||||||20260408023000|||F
OBX|1|NM|PH^pH^LN||7.28||7.35-7.45|L|||F
OBX|2|NM|PCO2^pCO2^LN||8.2|kPa|4.7-6.0|HH|||F
OBX|3|NM|PO2^pO2^LN||7.5|kPa|10.0-13.3|L|||F
OBX|4|NM|HCO3^Bikarbonat^LN||28|mmol/L|22-26|H|||F
OBX|5|NM|LACT^Laktat^LN||1.2|mmol/L|0.5-2.0|N|||F
OBX|6|NM|BE^Base Excess^LN||2.5|mmol/L|-3.0-3.0|N|||F
```

---

## 9. ORU^R01 - Urinstix (urinalysis result)

```
MSH|^~\&|LABKA|KBA_RH|EPIC|RIGSHOSPITALET|20260409101500||ORU^R01^ORU_R01|LK00009|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1108802571^^^CPR^NNDN||Thomsen^Jonas^Aage^^||19800811|M|||Mejlgade 237^^Brønshøj^^2700^DK||^^PH^+4597552051
PV1||I|RH^NEF^N4021^S02||||22002^Christiansen^Anders^^^Dr.|||NEF||||||||||RH202604090001
ORC|RE|ORD20260409001^EPIC||||||20260409101500
OBR|1|ORD20260409001^EPIC||URINE^Urinstix og mikroskopi^LN|||20260409083000||||||||22002^Christiansen^Anders^^^Dr.||||||20260409101500|||F
OBX|1|ST|UGLUC^U-Glukose^LN||Negativ||Negativ|N|||F
OBX|2|ST|UPROT^U-Protein^LN||3+||Negativ|A|||F
OBX|3|ST|UBLOD^U-Blod^LN||2+||Negativ|A|||F
OBX|4|ST|ULEU^U-Leukocytter^LN||Negativ||Negativ|N|||F
OBX|5|ST|UNITR^U-Nitrit^LN||Negativ||Negativ|N|||F
```

---

## 10. ORU^R01 - Nyrefunktion med PDF (renal function result with embedded PDF)

```
MSH|^~\&|LABKA|KBA_RH|EPIC|RIGSHOSPITALET|20260410100000||ORU^R01^ORU_R01|LK00010|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1509659693^^^CPR^NNDN||Vinther^Peter^Aage^^||19650915|M|||Skovvej 10^^København K^^1050^DK||^^PH^+4554169683
PV1||I|RH^NEF^N4021^S01||||22002^Christiansen^Anders^^^Dr.|||NEF||||||||||RH202604020001
ORC|RE|ORD20260410001^LABKA||||||20260410100000
OBR|1|ORD20260410001^LABKA||MISC^Samlet nyrefunktionsrapport^LN|||20260410083000||||||||22002^Christiansen^Anders^^^Dr.||||||20260410100000|||F
OBX|1|NM|CREA^Kreatinin^LN||245|umol/L|45-105|HH|||F
OBX|2|NM|EGFR^Estimeret GFR^LN||22|mL/min/1.73m2|>60|LL|||F
OBX|3|ED|PDF^Nyrefunktionsrapport^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F
```

---

## 11. ORU^R01 - D-vitamin (vitamin D result)

```
MSH|^~\&|LABKA|KBA_AUH|COLUMNA_CIS|AARHUS_UH|20260411091000||ORU^R01^ORU_R01|LK00011|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1203884930^^^CPR^NNDN||Jensen^Signe^Frederikke^^||19880312|F|||Banegårdspladsen 58^^Skive^^7800^DK||^^PH^+4567783028
PV1||O|AUH^END^AMB01||||44004^Lund^Niels^^^Dr.|||END||||||||||AUH202604110001
ORC|RE|ORD20260411001^COLUMNA_CIS||||||20260411091000
OBR|1|ORD20260411001^COLUMNA_CIS||VITD^25-OH-vitamin D^LN|||20260411083000||||||||44004^Lund^Niels^^^Dr.||||||20260411091000|||F
OBX|1|NM|VITD^25-OH-vitamin D^LN||28|nmol/L|50-160|L|||F
```

---

## 12. ORU^R01 - Jernstatus (iron status result)

```
MSH|^~\&|LABKA|KBA_AAUH|COLUMNA_CIS|AALBORG_UH|20260412101500||ORU^R01^ORU_R01|LK00012|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0103787866^^^CPR^NNDN||Krogh^Ulla^Gerda^^||19780301|F|||Skanderborgvej 149^^København K^^1050^DK||^^PH^+4544896074
PV1||I|AAUH^MED^301^A1||||12001^Mortensen^Anne^^^Dr.|||MED||||||||||AAUH202604010001
ORC|RE|ORD20260412001^COLUMNA_CIS||||||20260412101500
OBR|1|ORD20260412001^COLUMNA_CIS||IRON^Jernstatus^LN|||20260412083000||||||||12001^Mortensen^Anne^^^Dr.||||||20260412101500|||F
OBX|1|NM|FE^S-Jern^LN||5.2|umol/L|9-30|L|||F
OBX|2|NM|FERR^Ferritin^LN||8|ug/L|15-200|L|||F
OBX|3|NM|TIBC^Total jernbindingskapacitet^LN||78|umol/L|45-72|H|||F
OBX|4|NM|TSAT^Transferrinmætning^LN||7|%|16-45|L|||F
```

---

## 13. ORU^R01 - CRP og leukocytter (CRP and WBC result)

```
MSH|^~\&|LABKA|KBA_OUH|BCC|OUH|20260413141500||ORU^R01^ORU_R01|LK00013|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0811973145^^^CPR^NNDN||Vinther^Magnus^Otto^^||19971108|M|||Skanderborgvej 21^^Aalborg Ø^^9210^DK||^^CP^+4571445690
PV1||I|OUH^MED^A302^S01||||99009^Olsen^Tina^^^Dr.|||MED||||||||||OUH202604130001
ORC|RE|ORD20260413001^BCC||||||20260413141500
OBR|1|ORD20260413001^BCC||INFLAM^Infektionstal^LN|||20260413083000||||||||99009^Olsen^Tina^^^Dr.||||||20260413141500|||F
OBX|1|NM|CRP^C-reaktivt protein^LN||185|mg/L|<10|HH|||F
OBX|2|NM|WBC^Leukocytter^LN||18.5|10*9/L|3.5-10.0|HH|||F
OBX|3|NM|NEUT^Neutrofile^LN||15.2|10*9/L|1.5-7.5|HH|||F
```

---

## 14. ORU^R01 - Troponin (cardiac marker result)

```
MSH|^~\&|LABKA|KBA_RH|EPIC|RIGSHOSPITALET|20260414024500||ORU^R01^ORU_R01|LK00014|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2801903219^^^CPR^NNDN||Berg^Magnus^Kaj^^||19900128|M|||Valby Langgade 20^^Hillerød^^3400^DK||^^CP^+4526905321
PV1||E|RH^AKM^AK101||||10010^Christiansen^Lene^^^Dr.|||AKM||||||||||RH202604140001
ORC|RE|ORD20260414001^EPIC||||||20260414024500
OBR|1|ORD20260414001^EPIC||TROP^Troponin T og I^LN|||20260414013000||||||||10010^Christiansen^Lene^^^Dr.||||||20260414024500|||F
OBX|1|NM|TNTHS^Troponin T, højsensitiv^LN||456|ng/L|<14|HH|||F
OBX|2|NM|TNIH^Troponin I, højsensitiv^LN||2100|ng/L|<26|HH|||F
```

---

## 15. ORU^R01 - Hæmoglobin A1c med PDF (HbA1c with embedded PDF report)

```
MSH|^~\&|LABKA|KBA_OUH|BCC|OUH|20260415100000||ORU^R01^ORU_R01|LK00015|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1711627331^^^CPR^NNDN||Hansen^Kasper^Egon^^||19621117|M|||Strandgade 227^^Odense N^^5200^DK||^^PH^+4562505094
PV1||O|OUH^END^AMB01||||66006^Kristensen^Oliver^^^Dr.|||END||||||||||OUH202604060001
ORC|RE|ORD20260415001^LABKA||||||20260415100000
OBR|1|ORD20260415001^LABKA||MISC^Diabeteskontrol - samlet rapport^LN|||20260415083000||||||||66006^Kristensen^Oliver^^^Dr.||||||20260415100000|||F
OBX|1|NM|HBA1C^HbA1c^LN||58|mmol/mol|<48|H|||F
OBX|2|NM|GLUC^P-Glukose (faste)^LN||8.9|mmol/L|4.2-6.3|H|||F
OBX|3|ED|PDF^Diabeteskontrolrapport^LN||^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdl||||||F
```

---

## 16. ORU^R01 - Kreatinin-clearance (creatinine clearance result)

```
MSH|^~\&|LABKA|KBA_AUH|COLUMNA_CIS|AARHUS_UH|20260416091000||ORU^R01^ORU_R01|LK00016|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0309554169^^^CPR^NNDN||Mikkelsen^Peter^Gunnar^^||19550903|M|||Mejlgade 115^^Vordingborg^^4760^DK||^^PH^+4538684090
PV1||O|AUH^NEF^AMB01||||11011^Mikkelsen^Susanne^^^Dr.|||NEF||||||||||AUH202604160001
ORC|RE|ORD20260416001^COLUMNA_CIS||||||20260416091000
OBR|1|ORD20260416001^COLUMNA_CIS||CREACL^Kreatinin-clearance^LN|||20260416060000||||||||11011^Mikkelsen^Susanne^^^Dr.||||||20260416091000|||F
OBX|1|NM|CREA^Kreatinin (serum)^LN||168|umol/L|45-105|H|||F
OBX|2|NM|UCREA^Kreatinin (urin)^LN||6.2|mmol/L|||N|||F
OBX|3|NM|UVOL^Urinvolumen (24 timer)^LN||1850|mL|800-2500|N|||F
OBX|4|NM|CREACL^Kreatinin-clearance^LN||42|mL/min|80-120|L|||F
```

---

## 17. ORM^O01 - Laboratorierekvisition - akut (urgent lab order)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|LABKA|KBA_AAUH|20260417023000||ORM^O01|LK00017|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2504906828^^^CPR^NNDN||Holm^Line^Lykke^^||19900425|F|||Munkebjergvej 81^^Charlottenlund^^2920^DK||^^CP^+4520714139
PV1||E|AAUH^AKM^101^A2||||88008^Vinther^Kasper^^^Dr.|||AKM||||||||||AAUH202604170001
ORC|NW|ORD20260417001^COLUMNA_CIS||||||20260417023000|||88008^Vinther^Kasper^^^Dr.
OBR|1|ORD20260417001^COLUMNA_CIS||ABGAS^Arteriel blodgas^LN|||20260417023000||||||AKUT|88008^Vinther^Kasper^^^Dr.
OBR|2|ORD20260417001^COLUMNA_CIS||LACT^Laktat^LN|||20260417023000||||||AKUT|88008^Vinther^Kasper^^^Dr.
```

---

## 18. ORM^O01 - Laboratorierekvisition - rutine (routine lab order)

```
MSH|^~\&|BCC|OUH|LABKA|KBA_OUH|20260418083000||ORM^O01|LK00018|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2207739844^^^CPR^NNDN||Bang^Trine^Yrsa^^||19730722|F|||Mejlgade 94^^København K^^1260^DK||^^PH^+4581886427
PV1||I|OUH^MED^A305^S02||||33003^Krogh^Henrik^^^Dr.|||MED||||||||||OUH202604030001
ORC|NW|ORD20260418001^BCC||||||20260418083000|||33003^Krogh^Henrik^^^Dr.
OBR|1|ORD20260418001^BCC||CBC^Komplet blodtælling^LN|||20260418083000||||||||33003^Krogh^Henrik^^^Dr.
OBR|2|ORD20260418001^BCC||CRP^C-reaktivt protein^LN|||20260418083000||||||||33003^Krogh^Henrik^^^Dr.
OBR|3|ORD20260418001^BCC||LFT^Leverfunktionsprøver^LN|||20260418083000||||||||33003^Krogh^Henrik^^^Dr.
```

---

## 19. ORU^R01 - Proteinelektroforese (protein electrophoresis result)

```
MSH|^~\&|LABKA|KBA_AAUH|COLUMNA_CIS|AALBORG_UH|20260419101500||ORU^R01^ORU_R01|LK00019|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0103787866^^^CPR^NNDN||Krogh^Ulla^Gerda^^||19780301|F|||Skanderborgvej 149^^København K^^1050^DK||^^PH^+4544896074
PV1||I|AAUH^MED^301^A1||||12001^Mortensen^Anne^^^Dr.|||MED||||||||||AAUH202604010001
ORC|RE|ORD20260419001^COLUMNA_CIS||||||20260419101500
OBR|1|ORD20260419001^COLUMNA_CIS||PELEC^S-Proteinelektroforese^LN|||20260419083000||||||||12001^Mortensen^Anne^^^Dr.||||||20260419101500|||F
OBX|1|NM|ALBUM^Albumin (elektroforese)^LN||32|g/L|35-50|L|||F
OBX|2|NM|ALPHA1^Alfa-1 globulin^LN||2.8|g/L|1.0-3.0|N|||F
OBX|3|NM|ALPHA2^Alfa-2 globulin^LN||9.5|g/L|6.0-10.0|N|||F
OBX|4|NM|BETA^Beta-globulin^LN||8.2|g/L|7.0-11.0|N|||F
OBX|5|NM|GAMMA^Gamma-globulin^LN||18.5|g/L|7.0-16.0|H|||F
OBX|6|TX|PELECKOMM^Kommentar^LN||M-komponent påvist i gamma-fraktionen. Anbefaler immunfixation.||||||F
```

---

## 20. ORU^R01 - B-type natriuretisk peptid (BNP result)

```
MSH|^~\&|LABKA|KBA_RH|EPIC|RIGSHOSPITALET|20260420091000||ORU^R01^ORU_R01|LK00020|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0608714281^^^CPR^NNDN||Mortensen^Allan^Otto^^||19710806|M|||Engvej 123^^København SV^^2450^DK||^^PH^+4586282134
PV1||I|RH^KAR^K5031^S02||||12012^Hald^Tove^^^Dr.|||KAR||||||||||RH202604200001
ORC|RE|ORD20260420001^EPIC||||||20260420091000
OBR|1|ORD20260420001^EPIC||BNP^NT-proBNP^LN|||20260420083000||||||||12012^Hald^Tove^^^Dr.||||||20260420091000|||F
OBX|1|NM|NTPROBNP^NT-proBNP^LN||2850|pg/mL|<125|HH|||F
```
