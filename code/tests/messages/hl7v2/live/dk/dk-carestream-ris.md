# Carestream RIS - real HL7v2 ER7 messages

---

## 1. ORM^O01 - Røntgenrekvisition modtaget (radiology order received)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|CARESTREAM_RIS|AAUH_RAD|20260401090000||ORM^O01|CSRIS00001|P|2.5|||AL|NE||UNICODE UTF-8
PID|||2904851778^^^CPR^NNDN||Rasmussen^Line^Viola^^||19850429|F|||Tolderlundsvej 42^^København S^^2300^DK||^^PH^+4538399026
PV1||I|AAUH^ORT^410^D1||||12001^Bruun^Mette^^^Dr.|||ORT||||||||||AAUH202604010001
ORC|NW|ORD20260401001^COLUMNA_CIS||||||20260401090000|||12001^Bruun^Mette^^^Dr.
OBR|1|ORD20260401001^COLUMNA_CIS||XHIP^Røntgen af hofte^LOCAL|||20260401090000||||||Hoftesmerter efter fald, mistanke om fraktur|12001^Bruun^Mette^^^Dr.
```

---

## 2. ORM^O01 - CT-scanning rekvisition (CT order)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|CARESTREAM_RIS|RH_RAD|20260402083000||ORM^O01|CSRIS00002|P|2.5|||AL|NE||UNICODE UTF-8
PID|||0508671155^^^CPR^NNDN||Skov^Henrik^Bo^^||19670805|M|||Gammel Kongevej 176^^Risskov^^8240^DK||^^PH^+4534278055
PV1||I|RH^LUN^L2031^S02||||22002^Søndergaard^Lisbeth^^^Dr.|||LUN||||||||||RH202604020001
ORC|NW|ORD20260402001^EPIC||||||20260402083000|||22002^Søndergaard^Lisbeth^^^Dr.
OBR|1|ORD20260402001^EPIC||CTCHEST^CT thorax med kontrast^LOCAL|||20260402083000||||||Lungeinfiltrat, mistanke om malignitet|22002^Søndergaard^Lisbeth^^^Dr.
```

---

## 3. ORM^O01 - MR-scanning rekvisition (MRI order)

```
MSH|^~\&|BCC|OUH|CARESTREAM_RIS|OUH_RAD|20260403091000||ORM^O01|CSRIS00003|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1809721083^^^CPR^NNDN||Nørgaard^Tobias^Viggo^^||19720918|M|||Borgergade 46^^Silkeborg^^8600^DK||^^PH^+4563876183
PV1||O|OUH^ORT^AMB01||||33003^Krogh^Tina^^^Dr.|||ORT||||||||||OUH202604030001
ORC|NW|ORD20260403001^BCC||||||20260403091000|||33003^Krogh^Tina^^^Dr.
OBR|1|ORD20260403001^BCC||MRKNEE^MR-scanning af knæ^LOCAL|||20260403091000||||||Kontrol efter knæalloplastik, smerter|33003^Krogh^Tina^^^Dr.
```

---

## 4. ORU^R01 - Røntgenbeskrivelse (X-ray report)

```
MSH|^~\&|CARESTREAM_RIS|AAUH_RAD|COLUMNA_CIS|AALBORG_UH|20260401141500||ORU^R01^ORU_R01|CSRIS00004|P|2.5|||AL|NE||UNICODE UTF-8
PID|||2904851778^^^CPR^NNDN||Rasmussen^Line^Viola^^||19850429|F|||Tolderlundsvej 42^^København S^^2300^DK||^^PH^+4538399026
PV1||I|AAUH^ORT^410^D1||||12001^Bruun^Mette^^^Dr.|||ORT||||||||||AAUH202604010001
ORC|RE|ORD20260401001^COLUMNA_CIS||||||20260401141500
OBR|1|ORD20260401001^COLUMNA_CIS||XHIP^Røntgen af hofte^LOCAL|||20260401090000||||||||12001^Bruun^Mette^^^Dr.|||44001^Iversen^Erik^^^Dr.||20260401141500|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||Røntgen af hø. hofte AP og lateral: Collumfraktur, Garden type III. Dislokeret. Anbefaler kirurgisk intervention.||||||F
```

---

## 5. ORU^R01 - CT-beskrivelse (CT report)

```
MSH|^~\&|CARESTREAM_RIS|RH_RAD|EPIC|RIGSHOSPITALET|20260402153000||ORU^R01^ORU_R01|CSRIS00005|P|2.5|||AL|NE||UNICODE UTF-8
PID|||0508671155^^^CPR^NNDN||Skov^Henrik^Bo^^||19670805|M|||Gammel Kongevej 176^^Risskov^^8240^DK||^^PH^+4534278055
PV1||I|RH^LUN^L2031^S02||||22002^Søndergaard^Lisbeth^^^Dr.|||LUN||||||||||RH202604020001
ORC|RE|ORD20260402001^EPIC||||||20260402153000
OBR|1|ORD20260402001^EPIC||CTCHEST^CT thorax med kontrast^LOCAL|||20260402083000||||||||22002^Søndergaard^Lisbeth^^^Dr.|||55001^Frandsen^Jonas^^^Dr.||20260402153000|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||CT thorax med iv kontrast: 3.2 cm spiculeret masse i hø. overlaps posteriore segment. Mediastinal lymfadenopati. Ingen pleuraeffusion. Ingen knoglemetastaser. RADS 4B. Anbefaler bronkoskopi med biopsi.||||||F
```

---

## 6. ORU^R01 - CT-rapport med PDF (CT report with embedded PDF)

```
MSH|^~\&|CARESTREAM_RIS|RH_RAD|EPIC|RIGSHOSPITALET|20260402160000||ORU^R01^ORU_R01|CSRIS00006|P|2.5|||AL|NE||UNICODE UTF-8
PID|||0508671155^^^CPR^NNDN||Skov^Henrik^Bo^^||19670805|M|||Gammel Kongevej 176^^Risskov^^8240^DK||^^PH^+4534278055
PV1||I|RH^LUN^L2031^S02||||22002^Søndergaard^Lisbeth^^^Dr.|||LUN||||||||||RH202604020001
ORC|RE|ORD20260402002^CARESTREAM_RIS||||||20260402160000
OBR|1|ORD20260402002^CARESTREAM_RIS||CTCHEST^CT thorax - komplet rapport^LOCAL|||20260402083000||||||||22002^Søndergaard^Lisbeth^^^Dr.|||55001^Frandsen^Jonas^^^Dr.||20260402160000|||F
OBX|1|ED|PDF^Radiologirapport^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F
```

---

## 7. ORU^R01 - MR-beskrivelse (MRI report)

```
MSH|^~\&|CARESTREAM_RIS|OUH_RAD|BCC|OUH|20260404141500||ORU^R01^ORU_R01|CSRIS00007|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1809721083^^^CPR^NNDN||Nørgaard^Tobias^Viggo^^||19720918|M|||Borgergade 46^^Silkeborg^^8600^DK||^^PH^+4563876183
PV1||O|OUH^ORT^AMB01||||33003^Krogh^Tina^^^Dr.|||ORT||||||||||OUH202604030001
ORC|RE|ORD20260403001^BCC||||||20260404141500
OBR|1|ORD20260403001^BCC||MRKNEE^MR-scanning af knæ^LOCAL|||20260403091000||||||||33003^Krogh^Tina^^^Dr.|||66001^Lund^Bjarne^^^Dr.||20260404141500|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||MR af hø. knæ: Knæalloplastik in situ uden løsning. Let ødem i omgivende bløddele. Ingen tegn på infektion. Meniskresterne normalt udseende. Konkl: Forventelige postoperative forandringer.||||||F
```

---

## 8. SIU^S12 - Røntgenaftale-booking (radiology appointment scheduling)

```
MSH|^~\&|CARESTREAM_RIS|AAUH_RAD|COLUMNA_CIS|AALBORG_UH|20260405080000||SIU^S12|CSRIS00008|P|2.5|||AL|NE||UNICODE UTF-8
SCH|RAD20260410001^CARESTREAM_RIS|||||ROUTINE^^HL70276|XTHORAX^Røntgen af thorax^^^CSRIS|15|MIN|^^15^20260410090000^20260410091500||||||44001^Iversen^Erik^^^Dr.|^^PH^+4595776110|AAUH^RAD^XR01|44001^Iversen^Erik^^^Dr.|^^PH^+4595776110|AAUH^RAD^XR01
PID|||1011922930^^^CPR^NNDN||Olsen^Louise^Ellen^^||19921110|F|||Prinsensgade 19^^Viborg^^8800^DK||^^PH^+4568614245
AIS|1||XTHORAX^Røntgen af thorax^LOCAL|20260410090000||15|MIN
AIL|1||AAUH^RAD^XR01
AIP|1||44001^Iversen^Erik^^^Dr.
```

---

## 9. SIU^S14 - Røntgenaftaleændring (radiology appointment modification)

```
MSH|^~\&|CARESTREAM_RIS|AAUH_RAD|COLUMNA_CIS|AALBORG_UH|20260406090000||SIU^S14|CSRIS00009|P|2.5|||AL|NE||UNICODE UTF-8
SCH|RAD20260410001^CARESTREAM_RIS|||||ROUTINE^^HL70276|XTHORAX^Røntgen af thorax^^^CSRIS|15|MIN|^^15^20260411100000^20260411101500||||||44001^Iversen^Erik^^^Dr.|^^PH^+4595776110|AAUH^RAD^XR01|44001^Iversen^Erik^^^Dr.|^^PH^+4595776110|AAUH^RAD^XR01
PID|||1011922930^^^CPR^NNDN||Olsen^Louise^Ellen^^||19921110|F|||Prinsensgade 19^^Viborg^^8800^DK||^^PH^+4568614245
AIS|1||XTHORAX^Røntgen af thorax^LOCAL|20260411100000||15|MIN
AIL|1||AAUH^RAD^XR01
AIP|1||44001^Iversen^Erik^^^Dr.
```

---

## 10. ORM^O01 - Ultralyd rekvisition (ultrasound order)

```
MSH|^~\&|BCC|OUH|CARESTREAM_RIS|OUH_RAD|20260407091000||ORM^O01|CSRIS00010|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1410659824^^^CPR^NNDN||Rasmussen^Julie^Margrethe^^||19651014|F|||Frederikssundsvej 100^^Odense V^^5210^DK||^^PH^+4535612249
PV1||I|OUH^MED^A305^S02||||77002^Thomsen^Clara^^^Dr.|||MED||||||||||OUH202604070001
ORC|NW|ORD20260407001^BCC||||||20260407091000|||77002^Thomsen^Clara^^^Dr.
OBR|1|ORD20260407001^BCC||ULLEVER^Ultralyd af lever og galdeveje^LOCAL|||20260407091000||||||Forhøjede levertal, udredning|77002^Thomsen^Clara^^^Dr.
```

---

## 11. ORU^R01 - Ultralydbeskrivelse (ultrasound report)

```
MSH|^~\&|CARESTREAM_RIS|OUH_RAD|BCC|OUH|20260407141500||ORU^R01^ORU_R01|CSRIS00011|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1410659824^^^CPR^NNDN||Rasmussen^Julie^Margrethe^^||19651014|F|||Frederikssundsvej 100^^Odense V^^5210^DK||^^PH^+4535612249
PV1||I|OUH^MED^A305^S02||||77002^Thomsen^Clara^^^Dr.|||MED||||||||||OUH202604070001
ORC|RE|ORD20260407001^BCC||||||20260407141500
OBR|1|ORD20260407001^BCC||ULLEVER^Ultralyd af lever og galdeveje^LOCAL|||20260407091000||||||||77002^Thomsen^Clara^^^Dr.|||88001^Nielsen^Anne^^^Dr.||20260407141500|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||UL af lever og galdeveje: Leveren let forstørret, hepatomegali. Diffust forøget ekkogenicitet forenelig med steatose. Galdeblæren normal. Ingen dilatation af galdegange. Ingen frie ascites. Konkl: Hepatomegali med steatose.||||||F
```

---

## 12. ORM^O01 - PET-CT rekvisition (PET-CT order)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|CARESTREAM_RIS|RH_RAD|20260408083000||ORM^O01|CSRIS00012|P|2.5|||AL|NE||UNICODE UTF-8
PID|||0508671155^^^CPR^NNDN||Skov^Henrik^Bo^^||19670805|M|||Gammel Kongevej 176^^Risskov^^8240^DK||^^PH^+4534278055
PV1||I|RH^LUN^L2031^S02||||22002^Søndergaard^Lisbeth^^^Dr.|||LUN||||||||||RH202604020001
ORC|NW|ORD20260408001^EPIC||||||20260408083000|||22002^Søndergaard^Lisbeth^^^Dr.
OBR|1|ORD20260408001^EPIC||PETCT^FDG PET-CT helkrop^LOCAL|||20260408083000||||||Stadieinddeling af lungekarcinom|22002^Søndergaard^Lisbeth^^^Dr.
```

---

## 13. ORU^R01 - PET-CT-beskrivelse (PET-CT report)

```
MSH|^~\&|CARESTREAM_RIS|RH_RAD|EPIC|RIGSHOSPITALET|20260409141500||ORU^R01^ORU_R01|CSRIS00013|P|2.5|||AL|NE||UNICODE UTF-8
PID|||0508671155^^^CPR^NNDN||Skov^Henrik^Bo^^||19670805|M|||Gammel Kongevej 176^^Risskov^^8240^DK||^^PH^+4534278055
PV1||I|RH^LUN^L2031^S02||||22002^Søndergaard^Lisbeth^^^Dr.|||LUN||||||||||RH202604020001
ORC|RE|ORD20260408001^EPIC||||||20260409141500
OBR|1|ORD20260408001^EPIC||PETCT^FDG PET-CT helkrop^LOCAL|||20260408083000||||||||22002^Søndergaard^Lisbeth^^^Dr.|||55001^Frandsen^Jonas^^^Dr.||20260409141500|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||FDG PET-CT helkrop: Hypermetabol masse i hø. overlaps (SUVmax 12.4). FDG-avide mediastinale lymfeknuder (stationer 4R og 7). Ingen fjernmetastaser. Lever, binyrer, knogler og hjerne uden patologisk FDG-optag. Stadie: cT2aN2M0, IIIA.||||||F
```

---

## 14. ORU^R01 - PET-CT-rapport med PDF (PET-CT report with embedded PDF)

```
MSH|^~\&|CARESTREAM_RIS|RH_RAD|EPIC|RIGSHOSPITALET|20260409150000||ORU^R01^ORU_R01|CSRIS00014|P|2.5|||AL|NE||UNICODE UTF-8
PID|||0508671155^^^CPR^NNDN||Skov^Henrik^Bo^^||19670805|M|||Gammel Kongevej 176^^Risskov^^8240^DK||^^PH^+4534278055
PV1||I|RH^LUN^L2031^S02||||22002^Søndergaard^Lisbeth^^^Dr.|||LUN||||||||||RH202604020001
ORC|RE|ORD20260409001^CARESTREAM_RIS||||||20260409150000
OBR|1|ORD20260409001^CARESTREAM_RIS||PETCT^FDG PET-CT helkrop - komplet rapport^LOCAL|||20260408083000||||||||22002^Søndergaard^Lisbeth^^^Dr.|||55001^Frandsen^Jonas^^^Dr.||20260409150000|||F
OBX|1|ED|PDF^PET-CT rapport^LN||^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdl||||||F
```

---

## 15. ORM^O01 - Mammografi rekvisition (mammography order)

```
MSH|^~\&|EPIC|HERLEV_HOSPITAL|CARESTREAM_RIS|HEH_RAD|20260410083000||ORM^O01|CSRIS00015|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1303666698^^^CPR^NNDN||Friis^Line^Asta^^||19660313|F|||Vesterbrogade 146^^Valby^^2500^DK||^^PH^+4550711199
PV1||O|HEH^RAD^MAMMO||||99001^Johansen^Clara^^^Dr.|||RAD||||||||||HEH202604100001
ORC|NW|ORD20260410001^EPIC||||||20260410083000|||99001^Johansen^Clara^^^Dr.
OBR|1|ORD20260410001^EPIC||MAMMO^Mammografi bilateral^LOCAL|||20260410083000||||||Screeningmammografi, >50 år|99001^Johansen^Clara^^^Dr.
```

---

## 16. ORU^R01 - Mammografibeskrivelse (mammography report)

```
MSH|^~\&|CARESTREAM_RIS|HEH_RAD|EPIC|HERLEV_HOSPITAL|20260410141500||ORU^R01^ORU_R01|CSRIS00016|P|2.5|||AL|NE||UNICODE UTF-8
PID|||1303666698^^^CPR^NNDN||Friis^Line^Asta^^||19660313|F|||Vesterbrogade 146^^Valby^^2500^DK||^^PH^+4550711199
PV1||O|HEH^RAD^MAMMO||||99001^Johansen^Clara^^^Dr.|||RAD||||||||||HEH202604100001
ORC|RE|ORD20260410001^EPIC||||||20260410141500
OBR|1|ORD20260410001^EPIC||MAMMO^Mammografi bilateral^LOCAL|||20260410083000||||||||99001^Johansen^Clara^^^Dr.|||99002^Holm^Rikke^^^Dr.||20260410141500|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||Mammografi bilateral: Heterogent tæt brystvæv. Ingen suspekte masser eller mikroforkalkninger. Ingen arkitekturforstyrrelser. BI-RADS 2 bilateralt. Rutinekontrol anbefales om 2 år.||||||F
```

---

## 17. ADT^A04 - Ambulant registrering - radiologi (outpatient registration for imaging)

```
MSH|^~\&|CARESTREAM_RIS|AAUH_RAD|COLUMNA_CIS|AALBORG_UH|20260411080000||ADT^A04^ADT_A01|CSRIS00017|P|2.5|||AL|NE||UNICODE UTF-8
EVN|A04|20260411080000
PID|||1011922930^^^CPR^NNDN||Olsen^Louise^Ellen^^||19921110|F|||Prinsensgade 19^^Viborg^^8800^DK||^^PH^+4568614245
PV1||O|AAUH^RAD^XR01||||44001^Iversen^Erik^^^Dr.|||RAD||||||||||AAUH202604110001||||||||||||||||||||||||20260411080000
```

---

## 18. ORM^O01 - Knogledensitometri rekvisition (DEXA scan order)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|CARESTREAM_RIS|AAUH_RAD|20260412083000||ORM^O01|CSRIS00018|P|2.5|||AL|NE||UNICODE UTF-8
PID|||0502779886^^^CPR^NNDN||Henriksen^Freja^Christina^^||19770205|F|||Park Allé 75^^Viborg^^8800^DK||^^PH^+4554254594
PV1||O|AAUH^END^AMB01||||12001^Bruun^Mette^^^Dr.|||END||||||||||AAUH202604120001
ORC|NW|ORD20260412001^COLUMNA_CIS||||||20260412083000|||12001^Bruun^Mette^^^Dr.
OBR|1|ORD20260412001^COLUMNA_CIS||DEXA^DEXA-scanning, lumbal og hofte^LOCAL|||20260412083000||||||Osteoporose-udredning|12001^Bruun^Mette^^^Dr.
```

---

## 19. ORU^R01 - Knogledensitometri-beskrivelse (DEXA scan report)

```
MSH|^~\&|CARESTREAM_RIS|AAUH_RAD|COLUMNA_CIS|AALBORG_UH|20260412141500||ORU^R01^ORU_R01|CSRIS00019|P|2.5|||AL|NE||UNICODE UTF-8
PID|||0502779886^^^CPR^NNDN||Henriksen^Freja^Christina^^||19770205|F|||Park Allé 75^^Viborg^^8800^DK||^^PH^+4554254594
PV1||O|AAUH^END^AMB01||||12001^Bruun^Mette^^^Dr.|||END||||||||||AAUH202604120001
ORC|RE|ORD20260412001^COLUMNA_CIS||||||20260412141500
OBR|1|ORD20260412001^COLUMNA_CIS||DEXA^DEXA-scanning, lumbal og hofte^LOCAL|||20260412083000||||||||12001^Bruun^Mette^^^Dr.|||44001^Iversen^Erik^^^Dr.||20260412141500|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||DEXA-scanning: L1-L4 T-score -2.8 (osteoporose). Collum femoris T-score -2.1 (osteopeni). Anbefaler behandling med bisfosfonat.||||||F
OBX|2|NM|TSCORE_L^T-score lumbal^LN||-2.8||>-1.0|L|||F
OBX|3|NM|TSCORE_H^T-score collum femoris^LN||-2.1||>-1.0|L|||F
```

---

## 20. MDM^T02 - Radiologisk konferencenotat (radiology conference note)

```
MSH|^~\&|CARESTREAM_RIS|RH_RAD|DOKUMENTDELING|NSP|20260413120000||MDM^T02|CSRIS00020|P|2.5|||AL|NE||UNICODE UTF-8
EVN|T02|20260413120000
PID|||0508671155^^^CPR^NNDN||Skov^Henrik^Bo^^||19670805|M|||Gammel Kongevej 176^^Risskov^^8240^DK||^^PH^+4534278055
PV1||I|RH^LUN^L2031^S02||||22002^Søndergaard^Lisbeth^^^Dr.|||LUN||||||||||RH202604020001
TXA|1|CN^Konferencenotat|TX|20260413120000|55001^Frandsen^Jonas^^^Dr.||20260413120000|||||DOC20260413001||||||AU
OBX|1|TX|NOTE^MDT konferencenotat^LN||Multidisciplinær tumorkonference: Pt. med verificeret NSCLC i hø. overlap, cT2aN2M0, stadie IIIA. Diskuteret kirurgisk resektion vs. kemo-strålebehandling. Konklusion: Kemo-strålebehandling anbefales grundet N2-sygdom. Henvises til onkologisk afdeling.||||||F
```
