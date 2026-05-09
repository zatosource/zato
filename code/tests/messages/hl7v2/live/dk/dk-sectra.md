# Sectra PACS/VNA - real HL7v2 ER7 messages

---

## 1. ORM^O01 - Billedrekvisition fra RIS (image order from RIS)

```
MSH|^~\&|CARESTREAM_RIS|AAUH_RAD|SECTRA_PACS|AAUH_RAD|20260401091000||ORM^O01|SEC00001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|||0803853928^^^CPR^NNDN||Bruun^Sofie^Esther^^||19850308|F|||Marselis Boulevard 1^^Roskilde^^4000^DK||^^PH^+4556117681
PV1||I|AAUH^ORT^410^D1||||12001^Bang^Andreas^^^Dr.|||ORT||||||||||AAUH202604010001
ORC|NW|ORD20260401001^CARESTREAM_RIS||||||20260401091000|||12001^Bang^Andreas^^^Dr.
OBR|1|ORD20260401001^CARESTREAM_RIS||XHIP^Røntgen af hofte^LOCAL|||20260401091000||||||Collumfraktur, garden III|12001^Bang^Andreas^^^Dr.
```

---

## 2. ORM^O01 - CT-rekvisition (CT order to PACS)

```
MSH|^~\&|CARESTREAM_RIS|RH_RAD|SECTRA_PACS|RH_RAD|20260402090000||ORM^O01|SEC00002|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|||1205672217^^^CPR^NNDN||Hansen^Morten^Henning^^||19670512|M|||Valby Langgade 141^^Aalborg Ø^^9210^DK||^^PH^+4560835930
PV1||I|RH^LUN^L2031^S02||||22002^Christensen^Jørgen^^^Dr.|||LUN||||||||||RH202604020001
ORC|NW|ORD20260402001^CARESTREAM_RIS||||||20260402090000|||22002^Christensen^Jørgen^^^Dr.
OBR|1|ORD20260402001^CARESTREAM_RIS||CTCHEST^CT thorax med kontrast^LOCAL|||20260402090000||||||Lungeinfiltrat, stadieinddeling|22002^Christensen^Jørgen^^^Dr.
```

---

## 3. ORU^R01 - Billedrapport tilknyttet (image availability notification)

```
MSH|^~\&|SECTRA_PACS|AAUH_RAD|CARESTREAM_RIS|AAUH_RAD|20260401100000||ORU^R01^ORU_R01|SEC00003|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|||0803853928^^^CPR^NNDN||Bruun^Sofie^Esther^^||19850308|F|||Marselis Boulevard 1^^Roskilde^^4000^DK||^^PH^+4556117681
PV1||I|AAUH^ORT^410^D1||||12001^Bang^Andreas^^^Dr.|||ORT||||||||||AAUH202604010001
ORC|RE|ORD20260401001^CARESTREAM_RIS||||||20260401100000
OBR|1|ORD20260401001^CARESTREAM_RIS||XHIP^Røntgen af hofte^LOCAL|||20260401091000||||||||12001^Bang^Andreas^^^Dr.||||||20260401100000|||F
OBX|1|TX|IMGSTATUS^Billedstatus^LN||Billeder tilgængelige i PACS. Studienummer: 1.2.826.0.1.3680043.8.1055.1.20260401.1001||||||F
```

---

## 4. ORU^R01 - Foreløbig beskrivelse (preliminary report)

```
MSH|^~\&|SECTRA_PACS|RH_RAD|EPIC|RIGSHOSPITALET|20260402140000||ORU^R01^ORU_R01|SEC00004|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|||1205672217^^^CPR^NNDN||Hansen^Morten^Henning^^||19670512|M|||Valby Langgade 141^^Aalborg Ø^^9210^DK||^^PH^+4560835930
PV1||I|RH^LUN^L2031^S02||||22002^Christensen^Jørgen^^^Dr.|||LUN||||||||||RH202604020001
ORC|RE|ORD20260402001^CARESTREAM_RIS||||||20260402140000
OBR|1|ORD20260402001^CARESTREAM_RIS||CTCHEST^CT thorax med kontrast^LOCAL|||20260402090000||||||||22002^Christensen^Jørgen^^^Dr.|||55001^Thomsen^Birgit^^^Dr.||20260402140000|||P
OBX|1|TX|RADRPT^Foreløbig beskrivelse^LN||Foreløbig: Suspekt masse i hø. overlaps posteriore segment ca. 3 cm. Mediastinal lymfadenopati. Endelig beskrivelse følger.||||||P
```

---

## 5. ORU^R01 - Endelig beskrivelse (final report)

```
MSH|^~\&|SECTRA_PACS|RH_RAD|EPIC|RIGSHOSPITALET|20260402160000||ORU^R01^ORU_R01|SEC00005|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|||1205672217^^^CPR^NNDN||Hansen^Morten^Henning^^||19670512|M|||Valby Langgade 141^^Aalborg Ø^^9210^DK||^^PH^+4560835930
PV1||I|RH^LUN^L2031^S02||||22002^Christensen^Jørgen^^^Dr.|||LUN||||||||||RH202604020001
ORC|RE|ORD20260402001^CARESTREAM_RIS||||||20260402160000
OBR|1|ORD20260402001^CARESTREAM_RIS||CTCHEST^CT thorax med kontrast^LOCAL|||20260402090000||||||||22002^Christensen^Jørgen^^^Dr.|||55001^Thomsen^Birgit^^^Dr.||20260402160000|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||CT thorax med iv kontrast: 3.2 cm spiculeret masse i hø. overlaps posteriore segment. Mediastinale lymfeknuder op til 18 mm i station 4R og 7. Ingen pleuraeffusion. Ingen knoglemetastaser i scannet område. Lever og binyrer normalt udseende. Lung-RADS 4B.||||||F
```

---

## 6. ORU^R01 - Radiologirapport med PDF (radiology report with embedded PDF)

```
MSH|^~\&|SECTRA_PACS|RH_RAD|EPIC|RIGSHOSPITALET|20260402163000||ORU^R01^ORU_R01|SEC00006|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|||1205672217^^^CPR^NNDN||Hansen^Morten^Henning^^||19670512|M|||Valby Langgade 141^^Aalborg Ø^^9210^DK||^^PH^+4560835930
PV1||I|RH^LUN^L2031^S02||||22002^Christensen^Jørgen^^^Dr.|||LUN||||||||||RH202604020001
ORC|RE|ORD20260402003^SECTRA_PACS||||||20260402163000
OBR|1|ORD20260402003^SECTRA_PACS||CTCHEST^CT thorax - endelig rapport^LOCAL|||20260402090000||||||||22002^Christensen^Jørgen^^^Dr.|||55001^Thomsen^Birgit^^^Dr.||20260402163000|||F
OBX|1|ED|PDF^CT thorax rapport^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F
```

---

## 7. ADT^A04 - Ambulant registrering - billeddiagnostik (outpatient registration for imaging)

```
MSH|^~\&|SECTRA_PACS|OUH_RAD|BCC|OUH|20260403080000||ADT^A04^ADT_A01|SEC00007|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A04|20260403080000
PID|||2608729035^^^CPR^NNDN||Svendsen^Jonas^Carsten^^||19720826|M|||Strandgade 170^^Aalborg Ø^^9210^DK||^^PH^+4585801969
PV1||O|OUH^RAD^MR01||||66001^Bach^Morten^^^Dr.|||RAD||||||||||OUH202604030001||||||||||||||||||||||||20260403080000
```

---

## 8. ORM^O01 - MR-rekvisition (MRI order to PACS)

```
MSH|^~\&|CARESTREAM_RIS|OUH_RAD|SECTRA_PACS|OUH_RAD|20260403091000||ORM^O01|SEC00008|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|||2608729035^^^CPR^NNDN||Svendsen^Jonas^Carsten^^||19720826|M|||Strandgade 170^^Aalborg Ø^^9210^DK||^^PH^+4585801969
PV1||O|OUH^RAD^MR01||||66001^Bach^Morten^^^Dr.|||RAD||||||||||OUH202604030001
ORC|NW|ORD20260403001^CARESTREAM_RIS||||||20260403091000|||33003^Søndergaard^Karen^^^Dr.
OBR|1|ORD20260403001^CARESTREAM_RIS||MRKNEE^MR-scanning af knæ^LOCAL|||20260403091000||||||Postoperativ kontrol|33003^Søndergaard^Karen^^^Dr.
```

---

## 9. ORU^R01 - MR-billedtilgængelighed (MRI image availability)

```
MSH|^~\&|SECTRA_PACS|OUH_RAD|CARESTREAM_RIS|OUH_RAD|20260403110000||ORU^R01^ORU_R01|SEC00009|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|||2608729035^^^CPR^NNDN||Svendsen^Jonas^Carsten^^||19720826|M|||Strandgade 170^^Aalborg Ø^^9210^DK||^^PH^+4585801969
PV1||O|OUH^RAD^MR01||||66001^Bach^Morten^^^Dr.|||RAD||||||||||OUH202604030001
ORC|RE|ORD20260403001^CARESTREAM_RIS||||||20260403110000
OBR|1|ORD20260403001^CARESTREAM_RIS||MRKNEE^MR-scanning af knæ^LOCAL|||20260403091000||||||||33003^Søndergaard^Karen^^^Dr.||||||20260403110000|||F
OBX|1|TX|IMGSTATUS^Billedstatus^LN||MR-serier tilgængelige i PACS. 4 serier, 256 billeder. Studienummer: 1.2.826.0.1.3680043.8.1055.1.20260403.2001||||||F
```

---

## 10. ORU^R01 - MR-endelig rapport med PDF (MRI final report with embedded PDF)

```
MSH|^~\&|SECTRA_PACS|OUH_RAD|BCC|OUH|20260404150000||ORU^R01^ORU_R01|SEC00010|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|||2608729035^^^CPR^NNDN||Svendsen^Jonas^Carsten^^||19720826|M|||Strandgade 170^^Aalborg Ø^^9210^DK||^^PH^+4585801969
PV1||O|OUH^ORT^AMB01||||33003^Søndergaard^Karen^^^Dr.|||ORT||||||||||OUH202604030001
ORC|RE|ORD20260403002^SECTRA_PACS||||||20260404150000
OBR|1|ORD20260403002^SECTRA_PACS||MRKNEE^MR knæ - komplet rapport^LOCAL|||20260403091000||||||||33003^Søndergaard^Karen^^^Dr.|||66001^Bach^Morten^^^Dr.||20260404150000|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||MR af hø. knæ: Knæalloplastik in situ. Let periprostetisk ødem. Ingen løsning. Ingen tegn på infektion. Resterende meniskvæv normalt. Forventelige postoperative forandringer.||||||F
OBX|2|ED|PDF^MR knæ rapport^LN||^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdl||||||F
```

---

## 11. SIU^S12 - Undersøgelsestid booket (examination time scheduled)

```
MSH|^~\&|SECTRA_PACS|AAUH_RAD|CARESTREAM_RIS|AAUH_RAD|20260405080000||SIU^S12|SEC00011|P|2.5.1|||AL|NE||UNICODE UTF-8
SCH|IMG20260410001^SECTRA_PACS|||||ROUTINE^^HL70276|CTABD^CT abdomen^^^SECTRA|30|MIN|^^30^20260410100000^20260410103000||||||55002^Vinther^Magnus^^^Dr.|^^PH^+4570535539|AAUH^RAD^CT01|55002^Vinther^Magnus^^^Dr.|^^PH^+4570535539|AAUH^RAD^CT01
PID|||1811929976^^^CPR^NNDN||Holm^Ida^Edith^^||19921118|F|||Klosterstræde 218^^Helsingør^^3000^DK||^^PH^+4558869941
AIS|1||CTABD^CT abdomen med kontrast^LOCAL|20260410100000||30|MIN
AIL|1||AAUH^RAD^CT01
AIP|1||55002^Vinther^Magnus^^^Dr.
```

---

## 12. SIU^S14 - Undersøgelsestid ændret (examination time modified)

```
MSH|^~\&|SECTRA_PACS|AAUH_RAD|CARESTREAM_RIS|AAUH_RAD|20260406090000||SIU^S14|SEC00012|P|2.5.1|||AL|NE||UNICODE UTF-8
SCH|IMG20260410001^SECTRA_PACS|||||ROUTINE^^HL70276|CTABD^CT abdomen^^^SECTRA|30|MIN|^^30^20260411100000^20260411103000||||||55002^Vinther^Magnus^^^Dr.|^^PH^+4570535539|AAUH^RAD^CT01|55002^Vinther^Magnus^^^Dr.|^^PH^+4570535539|AAUH^RAD^CT01
PID|||1811929976^^^CPR^NNDN||Holm^Ida^Edith^^||19921118|F|||Klosterstræde 218^^Helsingør^^3000^DK||^^PH^+4558869941
AIS|1||CTABD^CT abdomen med kontrast^LOCAL|20260411100000||30|MIN
AIL|1||AAUH^RAD^CT01
AIP|1||55002^Vinther^Magnus^^^Dr.
```

---

## 13. ADT^A08 - Opdatering af patientdata i PACS (patient data update in PACS)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|SECTRA_PACS|AAUH_RAD|20260407091500||ADT^A08^ADT_A01|SEC00013|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A08|20260407091500
PID|||0803853928^^^CPR^NNDN||Bruun^Sofie^Esther^^||19850308|F|||Boulevarden 6^^København N^^2200^DK||^^PH^+4587591439~^^CP^+4521353195
PV1||I|AAUH^ORT^410^D1||||12001^Bang^Andreas^^^Dr.|||ORT||||||||||AAUH202604010001||||||||||||||||||||||||20260407091500
```

---

## 14. ADT^A40 - Sammenlægning i PACS (patient merge in PACS)

```
MSH|^~\&|COLUMNA_CIS|AALBORG_UH|SECTRA_PACS|AAUH_RAD|20260408060000||ADT^A40^ADT_A39|SEC00014|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A40|20260408060000
PID|||0803853928^^^CPR^NNDN||Bruun^Sofie^Esther^^||19850308|F|||Boulevarden 6^^København N^^2200^DK||^^PH^+4587591439
MRG|2124752087^^^CPR^NNDN||AAUH202602010001
```

---

## 15. ORM^O01 - Ultralyd rekvisition (ultrasound order to PACS)

```
MSH|^~\&|CARESTREAM_RIS|OUH_RAD|SECTRA_PACS|OUH_RAD|20260409091000||ORM^O01|SEC00015|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|||0707651428^^^CPR^NNDN||Iversen^Line^Edith^^||19650707|F|||Hasserisgade 83^^Aarhus V^^8210^DK||^^PH^+4534956124
PV1||I|OUH^MED^A305^S02||||77002^Jensen^Kasper^^^Dr.|||MED||||||||||OUH202604070001
ORC|NW|ORD20260409001^CARESTREAM_RIS||||||20260409091000|||77002^Jensen^Kasper^^^Dr.
OBR|1|ORD20260409001^CARESTREAM_RIS||ULLEVER^Ultralyd lever og galdeveje^LOCAL|||20260409091000||||||Steatose-kontrol|77002^Jensen^Kasper^^^Dr.
```

---

## 16. ORU^R01 - Ultralyd rapport (ultrasound report)

```
MSH|^~\&|SECTRA_PACS|OUH_RAD|BCC|OUH|20260409141500||ORU^R01^ORU_R01|SEC00016|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|||0707651428^^^CPR^NNDN||Iversen^Line^Edith^^||19650707|F|||Hasserisgade 83^^Aarhus V^^8210^DK||^^PH^+4534956124
PV1||I|OUH^MED^A305^S02||||77002^Jensen^Kasper^^^Dr.|||MED||||||||||OUH202604070001
ORC|RE|ORD20260409001^CARESTREAM_RIS||||||20260409141500
OBR|1|ORD20260409001^CARESTREAM_RIS||ULLEVER^Ultralyd lever og galdeveje^LOCAL|||20260409091000||||||||77002^Jensen^Kasper^^^Dr.|||88001^Svendsen^Niels^^^Dr.||20260409141500|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||UL af lever: Leveren normalstørrelse, 14.5 cm. Let forøget ekkogenicitet forenelig med let steatose, uændret sammenlignet med undersøgelse fra 20251015. Ingen fokale læsioner. Galdeblæren normal. Galdegange ikke dilaterede. Konkl: Stationær let steatose.||||||F
```

---

## 17. ORM^O01 - PET-CT rekvisition til PACS (PET-CT order to PACS)

```
MSH|^~\&|CARESTREAM_RIS|RH_RAD|SECTRA_PACS|RH_RAD|20260410083000||ORM^O01|SEC00017|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|||1205672217^^^CPR^NNDN||Hansen^Morten^Henning^^||19670512|M|||Valby Langgade 141^^Aalborg Ø^^9210^DK||^^PH^+4560835930
PV1||I|RH^LUN^L2031^S02||||22002^Christensen^Jørgen^^^Dr.|||LUN||||||||||RH202604020001
ORC|NW|ORD20260410001^CARESTREAM_RIS||||||20260410083000|||22002^Christensen^Jørgen^^^Dr.
OBR|1|ORD20260410001^CARESTREAM_RIS||PETCT^FDG PET-CT helkrop^LOCAL|||20260410083000||||||Lungecancer stadieinddeling|22002^Christensen^Jørgen^^^Dr.
```

---

## 18. ORU^R01 - PET-CT-rapport (PET-CT report)

```
MSH|^~\&|SECTRA_PACS|RH_RAD|EPIC|RIGSHOSPITALET|20260411141500||ORU^R01^ORU_R01|SEC00018|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|||1205672217^^^CPR^NNDN||Hansen^Morten^Henning^^||19670512|M|||Valby Langgade 141^^Aalborg Ø^^9210^DK||^^PH^+4560835930
PV1||I|RH^LUN^L2031^S02||||22002^Christensen^Jørgen^^^Dr.|||LUN||||||||||RH202604020001
ORC|RE|ORD20260410001^CARESTREAM_RIS||||||20260411141500
OBR|1|ORD20260410001^CARESTREAM_RIS||PETCT^FDG PET-CT helkrop^LOCAL|||20260410083000||||||||22002^Christensen^Jørgen^^^Dr.|||55001^Thomsen^Birgit^^^Dr.||20260411141500|||F
OBX|1|TX|RADRPT^Radiologibeskrivelse^LN||FDG PET-CT helkrop: Hypermetabol masse i hø. overlaps (SUVmax 11.8). FDG-avide mediastinale lymfeknuder station 4R (SUVmax 8.2) og 7 (SUVmax 7.6). Ingen fjernmetastaser. Stadie: cT2aN2M0, IIIA.||||||F
```

---

## 19. MDM^T02 - Addendum til beskrivelse (addendum to report)

```
MSH|^~\&|SECTRA_PACS|AAUH_RAD|COLUMNA_CIS|AALBORG_UH|20260412120000||MDM^T02|SEC00019|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|T02|20260412120000
PID|||0803853928^^^CPR^NNDN||Bruun^Sofie^Esther^^||19850308|F|||Boulevarden 6^^København N^^2200^DK||^^PH^+4587591439
PV1||I|AAUH^ORT^410^D1||||12001^Bang^Andreas^^^Dr.|||ORT||||||||||AAUH202604010001
TXA|1|AD^Addendum|TX|20260412120000|44001^Vinther^Magnus^^^Dr.||20260412120000|||||DOC20260412001||||||AU
OBX|1|TX|NOTE^Addendum til røntgenbeskrivelse^LN||Addendum: Ved fornyet gennemgang af røntgen hofte bemærkes desuden let osteoporotisk knoglestruktur i proximale femur. Anbefaler DEXA-scanning til vurdering af knogletæthed.||||||F
```

---

## 20. ADT^A01 - Indlæggelse med PACS-notifikation (admission notification to PACS)

```
MSH|^~\&|EPIC|RIGSHOSPITALET|SECTRA_PACS|RH_RAD|20260413070000||ADT^A01^ADT_A01|SEC00020|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A01|20260413070000
PID|||2406873706^^^CPR^NNDN||Jensen^Britt^Ellen^^||19870624|F|||Park Allé 130^^Odense V^^5210^DK||^^PH^+4586449935~^^CP^+4551529964
PV1||I|RH^NEU^N1041^S02||||33003^Berg^Flemming^^^Dr.|||NEU||||7|||33003^Berg^Flemming^^^Dr.||RH202604130001||||||||||||||||||||||||20260413070000
PV2|||^Subaraknoidal blødning
```
