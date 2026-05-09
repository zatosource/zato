# Columna CIS (Systematic) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Indlæggelse (inpatient admission)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|LANDSPATIENTREGISTERET|SST|20260401080000||ADT^A01^ADT_A01|MSG00001|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A01|20260401080000
PID|||0102857128^^^CPR^NNDN||Dahl^Camilla^Marie^^||19850201|F|||Adelgade 115^^Hellerup^^2900^DK||^^PH^+4543482061~^^CP^+4520741979
PV1||I|AAUH^MED^301^A3||||12345^Schmidt^Mathias^^^Dr.|||MED||||7|||12345^Schmidt^Mathias^^^Dr.||AAUH202604010001||||||||||||||||||||||||20260401080000
PV2|||^Pneumoni
```

---

## 2. ADT^A02 - Overflytning (patient transfer)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|LANDSPATIENTREGISTERET|SST|20260402093000||ADT^A02^ADT_A02|MSG00002|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A02|20260402093000
PID|||0102857128^^^CPR^NNDN||Dahl^Camilla^Marie^^||19850201|F|||Adelgade 115^^Hellerup^^2900^DK||^^PH^+4543482061~^^CP^+4520741979
PV1||I|AAUH^KIR^205^B1||||23456^Hansen^Jens^^^Dr.|||KIR||||7|||23456^Hansen^Jens^^^Dr.||AAUH202604010001||||||||||||||||||||||||20260402093000
PV2|||^Appendicit
```

---

## 3. ADT^A03 - Udskrivelse (discharge)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|LANDSPATIENTREGISTERET|SST|20260405140000||ADT^A03^ADT_A03|MSG00003|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A03|20260405140000
PID|||0102857128^^^CPR^NNDN||Dahl^Camilla^Marie^^||19850201|F|||Adelgade 115^^Hellerup^^2900^DK||^^PH^+4543482061~^^CP^+4520741979
PV1||I|AAUH^MED^301^A3||||12345^Schmidt^Mathias^^^Dr.|||MED||||7|||12345^Schmidt^Mathias^^^Dr.||AAUH202604010001||||||||||||||||||||||||20260405140000
PV2|||^Pneumoni
```

---

## 4. ADT^A04 - Ambulant registrering (outpatient registration)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|SUNDHED_DK|SST|20260406100000||ADT^A04^ADT_A01|MSG00004|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A04|20260406100000
PID|||1503764703^^^CPR^NNDN||Mortensen^Emil^Kaj^^||19760315|M|||Bispensgade 217^^København N^^2200^DK||^^PH^+4550829477~^^CP^+4550865816
PV1||O|AAUH^AMB^120^||||||||||||||AMB||AAUH202604060001||||||||||||||||||||||||20260406100000
PV2|||^Kontrol - diabetes mellitus type 2
```

---

## 5. ADT^A08 - Opdatering af patientdata (update patient information)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|LANDSPATIENTREGISTERET|SST|20260407091500||ADT^A08^ADT_A01|MSG00005|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A08|20260407091500
PID|||1503764703^^^CPR^NNDN||Mortensen^Emil^Kaj^^||19760315|M|||Paludan-Müllers Vej 63^^København K^^1050^DK||^^PH^+4545697416~^^CP^+4521157665
PV1||O|AAUH^AMB^120^||||||||||||||AMB||AAUH202604060001||||||||||||||||||||||||20260407091500
```

---

## 6. ADT^A31 - Opdatering af stamdata (update person information)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|CPR_REGISTERET|SST|20260408080000||ADT^A31^ADT_A05|MSG00006|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A31|20260408080000
PID|||2411908118^^^CPR^NNDN||Rasmussen^Pernille^Gudrun^^||19901124|F|||Nørregade 107^^Albertslund^^2620^DK||^^PH^+4548946335~^^CP^+4541115573
PD1||||34567^Mortensen^Brian^^^Dr.
```

---

## 7. ADT^A40 - Sammenlægning af patientidentiteter (merge patient)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|MPI|SST|20260409070000||ADT^A40^ADT_A39|MSG00007|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A40|20260409070000
PID|||0706882431^^^CPR^NNDN||Petersen^Thomas^Folmer^^||19880607|M|||Hovedvejen 136^^København SV^^2450^DK||^^PH^+4592161730
MRG|5981145855^^^CPR^NNDN||AAUH202601150001
```

---

## 8. ORM^O01 - Laboratorierekvisition (laboratory order)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|LABKA|KBA|20260410083000||ORM^O01|MSG00008|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1205733960^^^CPR^NNDN||Johansen^Anne^Vibe^^||19730512|F|||Skanderborgvej 117^^Esbjerg Ø^^6705^DK||^^PH^+4546903734
PV1||I|AAUH^MED^308^C2||||45678^Christensen^Tove^^^Dr.|||MED||||||||||AAUH202604100001
ORC|NW|ORD20260410001^COLUMNA_CIS||||||20260410083000|||45678^Christensen^Tove^^^Dr.
OBR|1|ORD20260410001^COLUMNA_CIS||CBC^Komplet blodtælling^LN|||20260410083000||||||||45678^Christensen^Tove^^^Dr.
OBR|2|ORD20260410001^COLUMNA_CIS||BMP^Basisk metabolisk panel^LN|||20260410083000||||||||45678^Christensen^Tove^^^Dr.
```

---

## 9. ORU^R01 - Laboratoriesvar (laboratory result)

```
MSH|^~\&|LABKA|KBA|COLUMNA_CIS|AALBORG_UH|20260410143000||ORU^R01^ORU_R01|MSG00009|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1205733960^^^CPR^NNDN||Johansen^Anne^Vibe^^||19730512|F|||Skanderborgvej 117^^Esbjerg Ø^^6705^DK||^^PH^+4546903734
PV1||I|AAUH^MED^308^C2||||45678^Christensen^Tove^^^Dr.|||MED||||||||||AAUH202604100001
ORC|RE|ORD20260410001^COLUMNA_CIS||||||20260410143000
OBR|1|ORD20260410001^COLUMNA_CIS||CBC^Komplet blodtælling^LN|||20260410083000||||||||45678^Christensen^Tove^^^Dr.||||||20260410143000|||F
OBX|1|NM|WBC^Leukocytter^LN||7.2|10*9/L|3.5-10.0|N|||F
OBX|2|NM|RBC^Erytrocytter^LN||4.8|10*12/L|3.9-5.5|N|||F
OBX|3|NM|HGB^Hæmoglobin^LN||8.3|mmol/L|7.3-10.0|N|||F
OBX|4|NM|PLT^Trombocytter^LN||245|10*9/L|145-390|N|||F
OBX|5|NM|MCV^Middelcellevolumen^LN||88|fL|82-98|N|||F
```

---

## 10. ORU^R01 - Laboratoriesvar med PDF (lab result with embedded PDF report)

```
MSH|^~\&|LABKA|KBA|COLUMNA_CIS|AALBORG_UH|20260411101500||ORU^R01^ORU_R01|MSG00010|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0903673749^^^CPR^NNDN||Madsen^Erik^Svend^^||19670309|M|||Hunderupvej 2^^Brønshøj^^2700^DK||^^PH^+4585554286
PV1||I|AAUH^MED^305^A1||||56789^Frandsen^Camilla^^^Dr.|||MED||||||||||AAUH202604110001
ORC|RE|ORD20260411001^COLUMNA_CIS||||||20260411101500
OBR|1|ORD20260411001^COLUMNA_CIS||MISC^Blodprøveresultater - samlet rapport^LN|||20260411080000||||||||56789^Frandsen^Camilla^^^Dr.||||||20260411101500|||F
OBX|1|ED|PDF^Laboratorierapport^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F
```

---

## 11. SIU^S12 - Aftale-booking (appointment scheduling notification)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|PATIENTPORTAL|SUNDHED_DK|20260412080000||SIU^S12|MSG00011|P|2.4|||AL|NE||UNICODE UTF-8
SCH|APT20260501001^COLUMNA_CIS|||||ROUTINE^^HL70276|Kontrol^Kontrol^^^COLUMNA|30|MIN|^^30^20260501093000^20260501100000||||||12345^Schmidt^Mathias^^^Dr.|^^PH^+4556183065|AAUH^AMB^120|12345^Schmidt^Mathias^^^Dr.|^^PH^+4556183065|AAUH^AMB^120
PID|||0102857128^^^CPR^NNDN||Dahl^Camilla^Marie^^||19850201|F|||Adelgade 115^^Hellerup^^2900^DK||^^PH^+4543482061
AIS|1||KONTROL^Ambulant kontrol^LOCAL|20260501093000||30|MIN
AIL|1||AAUH^AMB^120
AIP|1||12345^Schmidt^Mathias^^^Dr.
```

---

## 12. SIU^S14 - Aftaleændring (appointment modification)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|PATIENTPORTAL|SUNDHED_DK|20260413100000||SIU^S14|MSG00012|P|2.4|||AL|NE||UNICODE UTF-8
SCH|APT20260501001^COLUMNA_CIS|||||ROUTINE^^HL70276|Kontrol^Kontrol^^^COLUMNA|30|MIN|^^30^20260501140000^20260501143000||||||12345^Schmidt^Mathias^^^Dr.|^^PH^+4556183065|AAUH^AMB^120|12345^Schmidt^Mathias^^^Dr.|^^PH^+4556183065|AAUH^AMB^120
PID|||0102857128^^^CPR^NNDN||Dahl^Camilla^Marie^^||19850201|F|||Adelgade 115^^Hellerup^^2900^DK||^^PH^+4543482061
AIS|1||KONTROL^Ambulant kontrol^LOCAL|20260501140000||30|MIN
AIL|1||AAUH^AMB^120
AIP|1||12345^Schmidt^Mathias^^^Dr.
```

---

## 13. ORM^O01 - Røntgenrekvisition (radiology order)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|CARESTREAM_RIS|AAUH_RAD|20260414090000||ORM^O01|MSG00013|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1811929136^^^CPR^NNDN||Mortensen^Vibeke^Kristine^^||19921118|F|||Reventlowsvej 26^^København V^^1620^DK||^^PH^+4574412626
PV1||I|AAUH^ORT^410^D2||||67890^Nielsen^Kristian^^^Dr.|||ORT||||||||||AAUH202604140001
ORC|NW|ORD20260414001^COLUMNA_CIS||||||20260414090000|||67890^Nielsen^Kristian^^^Dr.
OBR|1|ORD20260414001^COLUMNA_CIS||XKNEE^Røntgen af knæ^LOCAL|||20260414090000||||||Smerter i ve. knæ efter fald|67890^Nielsen^Kristian^^^Dr.
```

---

## 14. ORU^R01 - Mikrobiologisvar (microbiology result)

```
MSH|^~\&|MADS|SSI|COLUMNA_CIS|AALBORG_UH|20260415161500||ORU^R01^ORU_R01|MSG00014|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2507835681^^^CPR^NNDN||Petersen^Bjarne^Walther^^||19830725|M|||Skovvej 229^^Thisted^^7700^DK||^^PH^+4540592023
PV1||I|AAUH^MED^302^B4||||78901^Mikkelsen^Knud^^^Dr.|||MED||||||||||AAUH202604150001
ORC|RE|ORD20260415001^MADS||||||20260415161500
OBR|1|ORD20260415001^MADS||BCUL^Bloddyrkning^LN|||20260414200000||||||||78901^Mikkelsen^Knud^^^Dr.||||||20260415161500|||F
OBX|1|CE|ORGANISM^Identificeret mikroorganisme^LN||ECO^Escherichia coli^LN|||A|||F
OBX|2|ST|SUSCEPT^Følsomhed - Ampicillin^LN||R|||A|||F
OBX|3|ST|SUSCEPT^Følsomhed - Ciprofloxacin^LN||S|||A|||F
OBX|4|ST|SUSCEPT^Følsomhed - Gentamicin^LN||S|||A|||F
```

---

## 15. MDM^T02 - Klinisk notat (clinical document notification)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|DOKUMENTDELING|NSP|20260416120000||MDM^T02|MSG00015|P|2.4|||AL|NE||UNICODE UTF-8
EVN|T02|20260416120000
PID|||0903673749^^^CPR^NNDN||Madsen^Erik^Svend^^||19670309|M|||Hunderupvej 2^^Brønshøj^^2700^DK||^^PH^+4585554286
PV1||I|AAUH^MED^305^A1||||56789^Frandsen^Camilla^^^Dr.|||MED||||||||||AAUH202604110001
TXA|1|CN^Klinisk notat|TX|20260416120000|56789^Frandsen^Camilla^^^Dr.||20260416120000|||||DOC20260416001||||||AU
OBX|1|TX|NOTE^Klinisk notat^LN||Patient indlagt med pneumoni. Behandles med iv. penicillin. Stabil tilstand, sat 96% på atmosfærisk luft. Plan: Fortsat antibiotika, kontrol af CRP og leukocytter i morgen.||||||F
```

---

## 16. ORU^R01 - Patologisvar med PDF-rapport (pathology result with embedded PDF)

```
MSH|^~\&|PATOLOGI|AAUH_PAT|COLUMNA_CIS|AALBORG_UH|20260417100000||ORU^R01^ORU_R01|MSG00016|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1406655786^^^CPR^NNDN||Dahl^Camilla^Yrsa^^||19650614|F|||Lindevej 168^^Holstebro^^7500^DK||^^PH^+4557144563
PV1||I|AAUH^KIR^206^A3||||89012^Sørensen^Sara^^^Dr.|||KIR||||||||||AAUH202604170001
ORC|RE|ORD20260417001^PATOLOGI||||||20260417100000
OBR|1|ORD20260417001^PATOLOGI||PATHBX^Biopsi - colon^LN|||20260415120000||||||||89012^Sørensen^Sara^^^Dr.||||||20260417100000|||F
OBX|1|TX|PATDIAG^Patologisk diagnose^LN||Tubulært adenom med lavgradig dysplasi. Frie resektionsrande.||||||F
OBX|2|ED|PDF^Patologirapport^LN||^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdl||||||F
```

---

## 17. ADT^A01 - Akut indlæggelse (emergency admission)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|LANDSPATIENTREGISTERET|SST|20260418020000||ADT^A01^ADT_A01|MSG00017|P|2.4|||AL|NE||UNICODE UTF-8
EVN|A01|20260418020000
PID|||0512794045^^^CPR^NNDN||Christiansen^Henrik^Ejvind^^||19791205|M|||Tagensvej 1^^Odense N^^5200^DK||^^PH^+4564278518~^^CP^+4529388864
PV1||E|AAUH^AKM^101^A1||||90123^Krogh^Inger^^^Dr.|||AKM||||1|||90123^Krogh^Inger^^^Dr.||AAUH202604180001||||||||||||||||||||||||20260418020000
PV2|||^Akut abdomen
```

---

## 18. ORM^O01 - EKG-rekvisition (ECG order)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|MUSE_ECG|AAUH_KAR|20260419083000||ORM^O01|MSG00018|P|2.4|||AL|NE||UNICODE UTF-8
PID|||0512794045^^^CPR^NNDN||Christiansen^Henrik^Ejvind^^||19791205|M|||Tagensvej 1^^Odense N^^5200^DK||^^PH^+4564278518
PV1||I|AAUH^KAR^501^B3||||01234^Christiansen^Knud^^^Dr.|||KAR||||||||||AAUH202604190001
ORC|NW|ORD20260419001^COLUMNA_CIS||||||20260419083000|||01234^Christiansen^Knud^^^Dr.
OBR|1|ORD20260419001^COLUMNA_CIS||ECG^EKG - 12 afledninger^LOCAL|||20260419083000||||||Brystsmerter og dyspnø|01234^Christiansen^Knud^^^Dr.
```

---

## 19. ORU^R01 - Blodprøvesvar - kritisk værdi (critical lab result)

```
MSH|^~\&|LABKA|KBA|COLUMNA_CIS|AALBORG_UH|20260420151500||ORU^R01^ORU_R01|MSG00019|P|2.4|||AL|NE||UNICODE UTF-8
PID|||1703941034^^^CPR^NNDN||Pedersen^Katrine^Birgitte^^||19940317|F|||Frederikssundsvej 205^^Herning^^7400^DK||^^PH^+4556159297
PV1||I|AAUH^MED^310^D1||||23456^Mikkelsen^Ida^^^Dr.|||MED||||||||||AAUH202604200001
ORC|RE|ORD20260420001^LABKA||||||20260420151500
OBR|1|ORD20260420001^LABKA||K^Kalium^LN|||20260420140000||||||||23456^Mikkelsen^Ida^^^Dr.||||||20260420151500|||F
OBX|1|NM|K^Kalium^LN||6.8|mmol/L|3.5-5.0|HH|||F
OBX|2|NM|NA^Natrium^LN||131|mmol/L|137-145|L|||F
OBX|3|NM|CREA^Kreatinin^LN||287|umol/L|45-105|HH|||F
```

---

## 20. ORU^R01 - Hæmatologisvar (hematology result)

```
MSH|^~\&|LABKA|KBA|COLUMNA_CIS|AALBORG_UH|20260421091000||ORU^R01^ORU_R01|MSG00020|P|2.4|||AL|NE||UNICODE UTF-8
PID|||2808569328^^^CPR^NNDN||Carlsen^Camilla^Viola^^||19560828|F|||Maglekildevej 232^^Esbjerg N^^6715^DK||^^PH^+4559664460
PV1||O|AAUH^HÆM^AMB||||34567^Petersen^Laura^^^Dr.|||HÆM||||||||||AAUH202604210001
ORC|RE|ORD20260421001^LABKA||||||20260421091000
OBR|1|ORD20260421001^LABKA||DIFF^Differentialtælling^LN|||20260421080000||||||||34567^Petersen^Laura^^^Dr.||||||20260421091000|||F
OBX|1|NM|WBC^Leukocytter^LN||12.4|10*9/L|3.5-10.0|H|||F
OBX|2|NM|NEUT^Neutrofile^LN||8.9|10*9/L|1.5-7.5|H|||F
OBX|3|NM|LYMPH^Lymfocytter^LN||2.1|10*9/L|1.0-4.0|N|||F
OBX|4|NM|MONO^Monocytter^LN||0.9|10*9/L|0.2-1.0|N|||F
OBX|5|NM|EOS^Eosinofile^LN||0.4|10*9/L|0.0-0.5|N|||F
OBX|6|NM|BASO^Basofile^LN||0.1|10*9/L|0.0-0.2|N|||F
```
