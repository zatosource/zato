# WebReq - real HL7v2 ER7 messages

---

## 1. ORM^O01 - Laboratorierekvisition fra praktiserende læge (lab order from GP)

```
MSH|^~\&|WEBREQ|GP_KLINIK|LABKA|KBA|20260401081500||ORM^O01|WR00001|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0506842021^^^CPR^NNDN||Olsen^Mads^Aksel^^||19840605|M|||Vindegade 12^^Silkeborg^^8600^DK||^^PH^+4540183227~^^CP^+4529996165
PV1||O|GP12345^LÆGERNE_I_VALBY^AMB||||GP001^Nielsen^Lisbeth^^^Dr.|||ALMEN||||||||||GP202604010001
ORC|NW|ORD20260401001^WEBREQ||||||20260401081500|||GP001^Nielsen^Lisbeth^^^Dr.
OBR|1|ORD20260401001^WEBREQ||CBC^Komplet blodtælling^LN|||20260401081500||||||Træthed og svimmelhed|GP001^Nielsen^Lisbeth^^^Dr.
OBR|2|ORD20260401001^WEBREQ||FERR^Ferritin^LN|||20260401081500||||||||GP001^Nielsen^Lisbeth^^^Dr.
OBR|3|ORD20260401001^WEBREQ||THYR^TSH og frit T4^LN|||20260401081500||||||||GP001^Nielsen^Lisbeth^^^Dr.
```

---

## 2. ORM^O01 - Laboratorierekvisition - diabetes kontrol (diabetes monitoring order)

```
MSH|^~\&|WEBREQ|GP_KLINIK|LABKA|KBA|20260402083000||ORM^O01|WR00002|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1711625311^^^CPR^NNDN||Mortensen^Martin^Poul^^||19621117|M|||Reventlowsvej 94^^Herning^^7400^DK||^^PH^+4567873260
PV1||O|GP23456^LÆGERNE_PÅ_MUNKERISVEJ^AMB||||GP002^Lund^Tove^^^Dr.|||ALMEN||||||||||GP202604020001
ORC|NW|ORD20260402001^WEBREQ||||||20260402083000|||GP002^Lund^Tove^^^Dr.
OBR|1|ORD20260402001^WEBREQ||HBA1C^HbA1c^LN|||20260402083000||||||Diabetes mellitus type 2, årskontrol|GP002^Lund^Tove^^^Dr.
OBR|2|ORD20260402001^WEBREQ||GLUC^Faste-glukose^LN|||20260402083000||||||||GP002^Lund^Tove^^^Dr.
OBR|3|ORD20260402001^WEBREQ||LIPID^Lipidprofil^LN|||20260402083000||||||||GP002^Lund^Tove^^^Dr.
OBR|4|ORD20260402001^WEBREQ||RENAL^Kreatinin og eGFR^LN|||20260402083000||||||||GP002^Lund^Tove^^^Dr.
```

---

## 3. ORM^O01 - Røntgenrekvisition fra GP (radiology order from GP)

```
MSH|^~\&|WEBREQ|GP_KLINIK|CARESTREAM_RIS|AAUH_RAD|20260403091000||ORM^O01|WR00003|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2309687170^^^CPR^NNDN||Jørgensen^Stine^Viola^^||19680923|F|||Algade 30^^Risskov^^8240^DK||^^PH^+4548556523
PV1||O|GP34567^STRANDVEJENS_LÆGEHUS^AMB||||GP003^Bang^Kristian^^^Dr.|||ALMEN||||||||||GP202604030001
ORC|NW|ORD20260403001^WEBREQ||||||20260403091000|||GP003^Bang^Kristian^^^Dr.
OBR|1|ORD20260403001^WEBREQ||XTHORAX^Røntgen af thorax^LOCAL|||20260403091000||||||Vedvarende hoste >3 uger, ryger|GP003^Bang^Kristian^^^Dr.
```

---

## 4. ORM^O01 - Henvisning til specialist (specialist referral)

```
MSH|^~\&|WEBREQ|GP_KLINIK|BCC|OUH|20260404080000||ORM^O01|WR00004|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1903787609^^^CPR^NNDN||Poulsen^Anders^Henning^^||19780319|M|||Skovvej 13^^Hellerup^^2900^DK||^^PH^+4552219331
PV1||R|GP45678^RUGÅRDSVEJS_LÆGEHUS^AMB||||GP004^Mortensen^Peter^^^Dr.|||ALMEN||||||||||GP202604040001
ORC|NW|ORD20260404001^WEBREQ||||||20260404080000|||GP004^Mortensen^Peter^^^Dr.
OBR|1|ORD20260404001^WEBREQ||REF_KAR^Henvisning til kardiologi^LOCAL|||20260404080000||||||Brystsmerter ved anstrengelse, ønske om belastnings-EKG|GP004^Mortensen^Peter^^^Dr.
DG1|1||DI209^Angina pectoris, uspecificeret^ICD10DK|||A
```

---

## 5. ORM^O01 - Akut laboratorierekvisition (urgent lab order from GP)

```
MSH|^~\&|WEBREQ|GP_KLINIK|LABKA|KBA|20260405100000||ORM^O01|WR00005|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0103785256^^^CPR^NNDN||Jørgensen^Astrid^Gudrun^^||19780301|F|||Søndergade 39^^Slagelse^^4200^DK||^^PH^+4588827879
PV1||O|GP56789^AALBORG_MIDTBY_LÆGER^AMB||||GP005^Frandsen^Karsten^^^Dr.|||ALMEN||||||||||GP202604050001
ORC|NW|ORD20260405001^WEBREQ||||||20260405100000|||GP005^Frandsen^Karsten^^^Dr.
OBR|1|ORD20260405001^WEBREQ||CRP^C-reaktivt protein^LN|||20260405100000||||||AKUT - feber og flankesmerter|GP005^Frandsen^Karsten^^^Dr.
OBR|2|ORD20260405001^WEBREQ||UCUL^Urindyrkning^LN|||20260405100000||||||||GP005^Frandsen^Karsten^^^Dr.
OBR|3|ORD20260405001^WEBREQ||ELEC^Elektrolytter^LN|||20260405100000||||||||GP005^Frandsen^Karsten^^^Dr.
```

---

## 6. ORU^R01 - Laboratoriesvar til GP (lab result to GP)

```
MSH|^~\&|LABKA|KBA|WEBREQ|GP_KLINIK|20260401143000||ORU^R01^ORU_R01|WR00006|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0506842021^^^CPR^NNDN||Olsen^Mads^Aksel^^||19840605|M|||Vindegade 12^^Silkeborg^^8600^DK||^^PH^+4540183227
PV1||O|GP12345^LÆGERNE_I_VALBY^AMB||||GP001^Nielsen^Lisbeth^^^Dr.|||ALMEN||||||||||GP202604010001
ORC|RE|ORD20260401001^WEBREQ||||||20260401143000
OBR|1|ORD20260401001^WEBREQ||CBC^Komplet blodtælling^LN|||20260401081500||||||||GP001^Nielsen^Lisbeth^^^Dr.||||||20260401143000|||F
OBX|1|NM|HGB^Hæmoglobin^LN||6.8|mmol/L|8.3-10.5|LL|||F
OBX|2|NM|MCV^Middelcellevolumen^LN||68|fL|82-98|L|||F
OBX|3|NM|WBC^Leukocytter^LN||5.2|10*9/L|3.5-10.0|N|||F
OBX|4|NM|PLT^Trombocytter^LN||380|10*9/L|145-390|N|||F
```

---

## 7. ORU^R01 - Ferritin-svar til GP (ferritin result to GP)

```
MSH|^~\&|LABKA|KBA|WEBREQ|GP_KLINIK|20260401150000||ORU^R01^ORU_R01|WR00007|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0506842021^^^CPR^NNDN||Olsen^Mads^Aksel^^||19840605|M|||Vindegade 12^^Silkeborg^^8600^DK||^^PH^+4540183227
PV1||O|GP12345^LÆGERNE_I_VALBY^AMB||||GP001^Nielsen^Lisbeth^^^Dr.|||ALMEN||||||||||GP202604010001
ORC|RE|ORD20260401002^WEBREQ||||||20260401150000
OBR|1|ORD20260401002^WEBREQ||FERR^Ferritin^LN|||20260401081500||||||||GP001^Nielsen^Lisbeth^^^Dr.||||||20260401150000|||F
OBX|1|NM|FERR^Ferritin^LN||6|ug/L|30-400|LL|||F
```

---

## 8. ORU^R01 - Thyroideasvar til GP (thyroid result to GP)

```
MSH|^~\&|LABKA|KBA|WEBREQ|GP_KLINIK|20260401153000||ORU^R01^ORU_R01|WR00008|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0506842021^^^CPR^NNDN||Olsen^Mads^Aksel^^||19840605|M|||Vindegade 12^^Silkeborg^^8600^DK||^^PH^+4540183227
PV1||O|GP12345^LÆGERNE_I_VALBY^AMB||||GP001^Nielsen^Lisbeth^^^Dr.|||ALMEN||||||||||GP202604010001
ORC|RE|ORD20260401003^WEBREQ||||||20260401153000
OBR|1|ORD20260401003^WEBREQ||THYR^TSH og frit T4^LN|||20260401081500||||||||GP001^Nielsen^Lisbeth^^^Dr.||||||20260401153000|||F
OBX|1|NM|TSH^Thyreoideastimulerende hormon^LN||2.1|mIU/L|0.27-4.20|N|||F
OBX|2|NM|FT4^Frit thyroxin^LN||16.5|pmol/L|12.0-22.0|N|||F
```

---

## 9. ORU^R01 - Laboratoriesvar med PDF (lab result with embedded PDF to GP)

```
MSH|^~\&|LABKA|KBA|WEBREQ|GP_KLINIK|20260402143000||ORU^R01^ORU_R01|WR00009|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1711625311^^^CPR^NNDN||Mortensen^Martin^Poul^^||19621117|M|||Reventlowsvej 94^^Herning^^7400^DK||^^PH^+4567873260
PV1||O|GP23456^LÆGERNE_PÅ_MUNKERISVEJ^AMB||||GP002^Lund^Tove^^^Dr.|||ALMEN||||||||||GP202604020001
ORC|RE|ORD20260402001^WEBREQ||||||20260402143000
OBR|1|ORD20260402001^WEBREQ||MISC^Diabeteskontrol - samlet rapport^LN|||20260402083000||||||||GP002^Lund^Tove^^^Dr.||||||20260402143000|||F
OBX|1|NM|HBA1C^HbA1c^LN||55|mmol/mol|<48|H|||F
OBX|2|NM|GLUC^P-Glukose (faste)^LN||8.2|mmol/L|4.2-6.3|H|||F
OBX|3|ED|PDF^Samlet labrapport^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F
```

---

## 10. ORM^O01 - Henvisning til billeddiagnostik (imaging referral)

```
MSH|^~\&|WEBREQ|GP_KLINIK|CARESTREAM_RIS|OUH_RAD|20260406090000||ORM^O01|WR00010|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0707656590^^^CPR^NNDN||Dahl^Laura^Esther^^||19650707|F|||Strandvejen 144^^Horsens^^8700^DK||^^PH^+4532184422
PV1||O|GP67890^HUNDERUPVEJ_LÆGEPRAKSIS^AMB||||GP006^Hansen^Rasmus^^^Dr.|||ALMEN||||||||||GP202604060001
ORC|NW|ORD20260406001^WEBREQ||||||20260406090000|||GP006^Hansen^Rasmus^^^Dr.
OBR|1|ORD20260406001^WEBREQ||ULLEVER^Ultralyd af lever og galdeveje^LOCAL|||20260406090000||||||Forhøjede levertal ved blodprøvekontrol, udredning|GP006^Hansen^Rasmus^^^Dr.
```

---

## 11. ORM^O01 - Henvisning til gastroenterologi (gastroenterology referral)

```
MSH|^~\&|WEBREQ|GP_KLINIK|BCC|OUH|20260407080000||ORM^O01|WR00011|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2207739946^^^CPR^NNDN||Lund^Laura^Karoline^^||19730722|F|||Havnevej 241^^Herlev^^2730^DK||^^PH^+4536268450
PV1||R|GP67890^HUNDERUPVEJ_LÆGEPRAKSIS^AMB||||GP006^Hansen^Rasmus^^^Dr.|||ALMEN||||||||||GP202604070001
ORC|NW|ORD20260407001^WEBREQ||||||20260407080000|||GP006^Hansen^Rasmus^^^Dr.
OBR|1|ORD20260407001^WEBREQ||REF_GAS^Henvisning til gastroenterologi^LOCAL|||20260407080000||||||Ændrede afføringsvaner, vægttab 5 kg over 2 måneder, mistanke om coloncancer|GP006^Hansen^Rasmus^^^Dr.
DG1|1||DC189^Coloncancer, uspecificeret^ICD10DK|||A
```

---

## 12. ORM^O01 - Laboratorierekvisition - graviditetskontrol (pregnancy monitoring order)

```
MSH|^~\&|WEBREQ|GP_KLINIK|LABKA|KBA|20260408083000||ORM^O01|WR00012|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1203885198^^^CPR^NNDN||Skov^Birgit^Karla^^||19880312|F|||Skolegade 196^^Hillerød^^3400^DK||^^PH^+4556499781
PV1||O|GP78901^SKOLEGADE_LÆGERNE^AMB||||GP007^Jensen^Mads^^^Dr.|||ALMEN||||||||||GP202604080001
ORC|NW|ORD20260408001^WEBREQ||||||20260408083000|||GP007^Jensen^Mads^^^Dr.
OBR|1|ORD20260408001^WEBREQ||GRAV^Graviditetspakke^LN|||20260408083000||||||Graviditet uge 12, 1. trimester-screening|GP007^Jensen^Mads^^^Dr.
OBR|2|ORD20260408001^WEBREQ||CBC^Komplet blodtælling^LN|||20260408083000||||||||GP007^Jensen^Mads^^^Dr.
OBR|3|ORD20260408001^WEBREQ||BTYPE^Blodtype og antistofscreening^LN|||20260408083000||||||||GP007^Jensen^Mads^^^Dr.
```

---

## 13. ORU^R01 - Lipidprofil-svar til GP (lipid panel result to GP)

```
MSH|^~\&|LABKA|KBA|WEBREQ|GP_KLINIK|20260402160000||ORU^R01^ORU_R01|WR00013|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1711625311^^^CPR^NNDN||Mortensen^Martin^Poul^^||19621117|M|||Reventlowsvej 94^^Herning^^7400^DK||^^PH^+4567873260
PV1||O|GP23456^LÆGERNE_PÅ_MUNKERISVEJ^AMB||||GP002^Lund^Tove^^^Dr.|||ALMEN||||||||||GP202604020001
ORC|RE|ORD20260402002^WEBREQ||||||20260402160000
OBR|1|ORD20260402002^WEBREQ||LIPID^Lipidprofil^LN|||20260402083000||||||||GP002^Lund^Tove^^^Dr.||||||20260402160000|||F
OBX|1|NM|CHOL^Total kolesterol^LN||5.8|mmol/L|<5.0|H|||F
OBX|2|NM|LDL^LDL-kolesterol^LN||3.6|mmol/L|<3.0|H|||F
OBX|3|NM|HDL^HDL-kolesterol^LN||1.1|mmol/L|>1.0|N|||F
OBX|4|NM|TRIG^Triglycerider^LN||2.4|mmol/L|<2.0|H|||F
```

---

## 14. ORU^R01 - Radiologisvar til GP (radiology result to GP)

```
MSH|^~\&|CARESTREAM_RIS|AAUH_RAD|WEBREQ|GP_KLINIK|20260404141500||ORU^R01^ORU_R01|WR00014|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2309687170^^^CPR^NNDN||Jørgensen^Stine^Viola^^||19680923|F|||Algade 30^^Risskov^^8240^DK||^^PH^+4548556523
PV1||O|GP34567^STRANDVEJENS_LÆGEHUS^AMB||||GP003^Bang^Kristian^^^Dr.|||ALMEN||||||||||GP202604030001
ORC|RE|ORD20260403001^WEBREQ||||||20260404141500
OBR|1|ORD20260403001^WEBREQ||XTHORAX^Røntgen af thorax^LOCAL|||20260403091000||||||||GP003^Bang^Kristian^^^Dr.||||||20260404141500|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||Røntgen af thorax PA og lateral: Lungefelterne frie. Hjertestørrelse normal. Normale mediastinale konturer. Ingen pleuraeffusion. Normalt fund.||||||F
```

---

## 15. ORU^R01 - Radiologisvar med PDF (radiology result with embedded PDF to GP)

```
MSH|^~\&|CARESTREAM_RIS|AAUH_RAD|WEBREQ|GP_KLINIK|20260404150000||ORU^R01^ORU_R01|WR00015|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2309687170^^^CPR^NNDN||Jørgensen^Stine^Viola^^||19680923|F|||Algade 30^^Risskov^^8240^DK||^^PH^+4548556523
PV1||O|GP34567^STRANDVEJENS_LÆGEHUS^AMB||||GP003^Bang^Kristian^^^Dr.|||ALMEN||||||||||GP202604030001
ORC|RE|ORD20260403002^CARESTREAM_RIS||||||20260404150000
OBR|1|ORD20260403002^CARESTREAM_RIS||XTHORAX^Røntgen thorax - komplet rapport^LOCAL|||20260403091000||||||||GP003^Bang^Kristian^^^Dr.||||||20260404150000|||F
OBX|1|ED|PDF^Røntgenrapport^LN||^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdl||||||F
```

---

## 16. ORM^O01 - Henvisning til øjenlæge (ophthalmology referral)

```
MSH|^~\&|WEBREQ|GP_KLINIK|COLUMNA_CIS|AARHUS_UH|20260409080000||ORM^O01|WR00016|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0309552429^^^CPR^NNDN||Madsen^Niels^Poul^^||19550903|M|||Amagerbrogade 81^^Ballerup^^2750^DK||^^PH^+4562484762
PV1||R|GP89012^PARK_ALLÉ_KLINIK^AMB||||GP008^Christiansen^Niels^^^Dr.|||ALMEN||||||||||GP202604090001
ORC|NW|ORD20260409001^WEBREQ||||||20260409080000|||GP008^Christiansen^Niels^^^Dr.
OBR|1|ORD20260409001^WEBREQ||REF_EYE^Henvisning til øjenafdeling^LOCAL|||20260409080000||||||Diabetes mellitus type 2, årlig øjenscreening for diabetisk retinopati|GP008^Christiansen^Niels^^^Dr.
DG1|1||DE113A^Diabetisk retinopati^ICD10DK|||A
```

---

## 17. ORM^O01 - Laboratorierekvisition - INR-kontrol (INR monitoring order)

```
MSH|^~\&|WEBREQ|GP_KLINIK|LABKA|KBA|20260410081500||ORM^O01|WR00017|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0608716567^^^CPR^NNDN||Hald^Kristian^Aksel^^||19710806|M|||Silkeborgvej 96^^Thisted^^7700^DK||^^PH^+4583825674
PV1||O|GP90123^AMAGERBRO_LÆGER^AMB||||GP009^Olsen^Anders^^^Dr.|||ALMEN||||||||||GP202604100001
ORC|NW|ORD20260410001^WEBREQ||||||20260410081500|||GP009^Olsen^Anders^^^Dr.
OBR|1|ORD20260410001^WEBREQ||INR^INR-kontrol^LN|||20260410081500||||||Atrieflimren, warfarinbehandling|GP009^Olsen^Anders^^^Dr.
```

---

## 18. ORU^R01 - INR-svar til GP (INR result to GP)

```
MSH|^~\&|LABKA|KBA|WEBREQ|GP_KLINIK|20260410130000||ORU^R01^ORU_R01|WR00018|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0608716567^^^CPR^NNDN||Hald^Kristian^Aksel^^||19710806|M|||Silkeborgvej 96^^Thisted^^7700^DK||^^PH^+4583825674
PV1||O|GP90123^AMAGERBRO_LÆGER^AMB||||GP009^Olsen^Anders^^^Dr.|||ALMEN||||||||||GP202604100001
ORC|RE|ORD20260410001^WEBREQ||||||20260410130000
OBR|1|ORD20260410001^WEBREQ||INR^INR-kontrol^LN|||20260410081500||||||||GP009^Olsen^Anders^^^Dr.||||||20260410130000|||F
OBX|1|NM|INR^International Normalised Ratio^LN||3.5||2.0-3.0|H|||F
```

---

## 19. ORM^O01 - Laboratorierekvisition - nyrefunktion (renal function order)

```
MSH|^~\&|WEBREQ|GP_KLINIK|LABKA|KBA|20260411083000||ORM^O01|WR00019|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1509655257^^^CPR^NNDN||Bang^Simon^Børge^^||19650915|M|||Randersvej 27^^Taastrup^^2630^DK||^^PH^+4597497160
PV1||O|GP01234^BREDGADE_LÆGERNE^AMB||||GP010^Bertelsen^Niels^^^Dr.|||ALMEN||||||||||GP202604110001
ORC|NW|ORD20260411001^WEBREQ||||||20260411083000|||GP010^Bertelsen^Niels^^^Dr.
OBR|1|ORD20260411001^WEBREQ||RENAL^Kreatinin, eGFR og karbamid^LN|||20260411083000||||||Kronisk nyresygdom, halvårlig kontrol|GP010^Bertelsen^Niels^^^Dr.
OBR|2|ORD20260411001^WEBREQ||ELEC^Elektrolytter^LN|||20260411083000||||||||GP010^Bertelsen^Niels^^^Dr.
```

---

## 20. ORU^R01 - Urindyrkningssvar til GP (urine culture result to GP)

```
MSH|^~\&|MADS|SSI|WEBREQ|GP_KLINIK|20260406161500||ORU^R01^ORU_R01|WR00020|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0103785256^^^CPR^NNDN||Jørgensen^Astrid^Gudrun^^||19780301|F|||Søndergade 39^^Slagelse^^4200^DK||^^PH^+4588827879
PV1||O|GP56789^AALBORG_MIDTBY_LÆGER^AMB||||GP005^Frandsen^Karsten^^^Dr.|||ALMEN||||||||||GP202604050001
ORC|RE|ORD20260405001^MADS||||||20260406161500
OBR|1|ORD20260405001^MADS||UCUL^Urindyrkning^LN|||20260405100000||||||||GP005^Frandsen^Karsten^^^Dr.||||||20260406161500|||F
OBX|1|CE|ORGANISM^Identificeret mikroorganisme^LN||ECO^Escherichia coli^LN|||A|||F
OBX|2|NM|COLONY^Kolonital^LN||>100000|CFU/mL||||A|||F
OBX|3|ST|SUSCEPT^Følsomhed - Mecillinam^LN||S|||A|||F
OBX|4|ST|SUSCEPT^Følsomhed - Nitrofurantoin^LN||S|||A|||F
OBX|5|ST|SUSCEPT^Følsomhed - Trimethoprim^LN||R|||A|||F
OBX|6|ST|SUSCEPT^Følsomhed - Ciprofloxacin^LN||S|||A|||F
```
