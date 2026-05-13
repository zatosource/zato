# KISIM (CISTEC) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - stationäre Aufnahme (inpatient admission)

```
MSH|^~\&|KISIM|USZ_ZUERICH|LABOR|USZ_ZUERICH|20260301080000||ADT^A01^ADT_A01|KISIM00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A01|20260301080000
PID|||PAT123456^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR~7560123456789^^^&2.16.756.5.31&ISO^SS||Burgener^Manfred^Heinz^^Herr||19650312|M|||Gerechtigkeitsgasse 169^^Chur^^7000^CH||^^PH^0815908760~^^CP^0763528981
PV1||I|MED^Zimmer 301^Bett A^Innere Medizin||||ARZ001^Senn^Sabine^^^Dr.^med.|ARZ002^Glaus^Otto^^^Dr.^med.||||||||FALL00123|||||||||||||||||||||||||||20260301080000
IN1|1|UVG|CSS001|CSS Versicherung|Tribschenstrasse 21^^Luzern^^6005^CH||||||||||||||||||||||||||||||||||||||||||||756.1234.5678.97
```

---

## 2. ADT^A02 - Verlegung (patient transfer)

```
MSH|^~\&|KISIM|USZ_ZUERICH|LABOR|USZ_ZUERICH|20260302090000||ADT^A02^ADT_A02|KISIM00002|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A02|20260302090000
PID|||PAT123456^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Burgener^Manfred^Heinz^^Herr||19650312|M|||Gerechtigkeitsgasse 169^^Chur^^7000^CH||^^PH^0815908760~^^CP^0763528981
PV1||I|CHIR^Zimmer 405^Bett B^Chirurgie||||ARZ003^Marti^Andreas^^^Prof.^Dr.^med.||||||||||||FALL00123||||||||||||||||||||||MED^Zimmer 301^Bett A^Innere Medizin||20260302090000
```

---

## 3. ADT^A03 - Austritt (discharge)

```
MSH|^~\&|KISIM|USZ_ZUERICH|LABOR|USZ_ZUERICH|20260310140000||ADT^A03^ADT_A03|KISIM00003|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A03|20260310140000
PID|||PAT123456^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Burgener^Manfred^Heinz^^Herr||19650312|M|||Gerechtigkeitsgasse 169^^Chur^^7000^CH||^^PH^0815908760~^^CP^0763528981
PV1||I|CHIR^Zimmer 405^Bett B^Chirurgie||||ARZ003^Marti^Andreas^^^Prof.^Dr.^med.||||||||||||FALL00123|||||||||||||||||||||||||||20260310140000
```

---

## 4. ADT^A04 - ambulante Registrierung (outpatient registration)

```
MSH|^~\&|KISIM|INSEL_BERN|POLIKLINIK|INSEL_BERN|20260315100000||ADT^A04^ADT_A01|KISIM00004|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A04|20260315100000
PID|||PAT789012^^^INSEL&2.16.756.5.30.1.128.1&ISO^MR~7561234567890^^^&2.16.756.5.31&ISO^SS||Vogel^Esther^Rosa^^Frau||19781105|F|||Kirchstrasse 89^^Bern^^3001^CH||^^PH^0318136974~^^CP^0792262217
PV1||O|AMB^Sprechzimmer 12^^Ambulatorium||||ARZ004^Mueller^Monika^^^Dr.^med.||||||||||||FALL00456|||||||||||||||||||||||||||20260315100000
```

---

## 5. ADT^A08 - Patientendaten-Aktualisierung (patient update)

```
MSH|^~\&|KISIM|KSW_WINTERTHUR|PDMS|KSW_WINTERTHUR|20260318110000||ADT^A08^ADT_A01|KISIM00005|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A08|20260318110000
PID|||PAT345678^^^KSW&2.16.756.5.30.1.129.1&ISO^MR||Baumann^Erika^Verena^^Frau||19520708|F|||Stauffacherstrasse 141^^Nidau^^2560^CH||^^PH^0327054233~^^CP^0791556982
PV1||I|GERI^Zimmer 201^Bett A^Geriatrie||||ARZ005^Frei^Sandra^^^Dr.^med.||||||||||||FALL00789|||||||||||||||||||||||||||20260318110000
IN1|1|KVG|SWICA001|SWICA Gesundheitsorganisation|Römerstrasse 38^^Winterthur^^8401^CH||||||||||||||||||||||||||||||||||||||||||||756.9876.5432.10
```

---

## 6. ORM^O01 - Laborauftrag (laboratory order)

```
MSH|^~\&|KISIM|USZ_ZUERICH|LABSYS|USZ_ZUERICH|20260320083000||ORM^O01^ORM_O01|KISIM00006|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT555111^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Eberle^Christian^Elisabeth^^Herr||19880420|M|||Bahnhofstrasse 67^^Horgen^^8810^CH||^^CP^0795677000
PV1||I|MED^Zimmer 510^Bett A^Innere Medizin||||ARZ006^Wyss^Paul^^^Dr.^med.||||||||||||FALL01234|||||||||||||||||||||||||||20260320083000
ORC|NW|ORD789^^^KISIM|||||^^^20260320090000^^R||20260320083000|ARZ006^Wyss^Paul^^^Dr.^med.
OBR|1|ORD789^^^KISIM||CBC^Blutbild komplett^LN|||20260320083000||||A|||||ARZ006^Wyss^Paul^^^Dr.^med.
```

---

## 7. ORU^R01 - Laborbefund (laboratory result)

```
MSH|^~\&|LABSYS|USZ_ZUERICH|KISIM|USZ_ZUERICH|20260320150000||ORU^R01^ORU_R01|LAB00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT555111^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Eberle^Christian^Elisabeth^^Herr||19880420|M|||Bahnhofstrasse 67^^Horgen^^8810^CH||^^CP^0795677000
PV1||I|MED^Zimmer 510^Bett A^Innere Medizin||||ARZ006^Wyss^Paul^^^Dr.^med.||||||||||||FALL01234
OBR|1|ORD789^^^KISIM|RES789^^^LABSYS|CBC^Blutbild komplett^LN|||20260320083000|||||||||ARZ006^Wyss^Paul^^^Dr.^med.||||||20260320150000|||F
OBX|1|NM|718-7^Hämoglobin^LN||148|g/L|135-175|N|||F
OBX|2|NM|6690-2^Leukozyten^LN||7.2|10*9/L|4.0-10.0|N|||F
OBX|3|NM|787-2^Erythrozyten^LN||4.9|10*12/L|4.3-5.8|N|||F
OBX|4|NM|789-8^Thrombozyten^LN||245|10*9/L|150-400|N|||F
```

---

## 8. ORU^R01 - Befund mit PDF (result with embedded PDF report)

```
MSH|^~\&|LABSYS|USZ_ZUERICH|KISIM|USZ_ZUERICH|20260321100000||ORU^R01^ORU_R01|LAB00002|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT667788^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Gerber^Ottilia^Fritz^^Frau||19710903|F|||Tannenstrasse 180^^Zurich^^8001^CH||^^CP^0783003964
PV1||I|ONKO^Zimmer 702^Bett A^Onkologie||||ARZ007^Fischer^Felix^^^Prof.^Dr.^med.||||||||||||FALL02345
OBR|1|ORD890^^^KISIM|RES890^^^LABSYS|11502-2^Laborbericht^LN|||20260321090000|||||||||ARZ007^Fischer^Felix^^^Prof.^Dr.^med.||||||20260321100000|||F
OBX|1|ED|11502-2^Laborbericht^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSA+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDQgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjI0MwolJUVPRgo=||||||F
```

---

## 9. MDM^T02 - Arztbrief (medical document notification with base64)

```
MSH|^~\&|KISIM|INSEL_BERN|ARCHIV|INSEL_BERN|20260322140000||MDM^T02^MDM_T02|KISIM00009|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|T02|20260322140000
PID|||PAT998877^^^INSEL&2.16.756.5.30.1.128.1&ISO^MR||Suter^Bruno^Margrit^^Herr||19451220|M|||Kirchstrasse 26^^Baden^^5400^CH||^^PH^0563683168
PV1||I|KARD^Zimmer 108^Bett B^Kardiologie||||ARZ008^Widmer^Heinrich^^^Prof.^Dr.^med.||||||||||||FALL03456
TXA|1|AR|AP|20260322140000|ARZ008^Widmer^Heinrich^^^Prof.^Dr.^med.||||||||DOC456789||||||AU
OBX|1|ED|18842-5^Arztbrief^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKEFyenRicmllZikgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozMzcKJSVFT0YK||||||F
```

---

## 10. ADT^A28 - Neuanlage Person (add person information)

```
MSH|^~\&|KISIM|KSW_WINTERTHUR|MPI|KSW_WINTERTHUR|20260325080000||ADT^A28^ADT_A05|KISIM00010|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A28|20260325080000
PID|||PAT112233^^^KSW&2.16.756.5.30.1.129.1&ISO^MR~7569876543210^^^&2.16.756.5.31&ISO^SS||Stauffer^Heidi^Anna^^Frau||19901115|F|||Kornhausstrasse 197^^Winterthur^^8400^CH||^^PH^0528047105~^^CP^0771779237~^^Internet^heidi.stauffer@bluewin.ch
PV1||N
```

---

## 11. SIU^S12 - Terminbuchung (appointment scheduling)

```
MSH|^~\&|KISIM|USZ_ZUERICH|TERMIN|USZ_ZUERICH|20260401090000||SIU^S12^SIU_S12|KISIM00011|P|2.5|||AL|NE|CHE|UNICODE UTF-8
SCH|APPT001^^^KISIM|||||ROUTINE^Routine-Termin^HL70276|KONSULTATION^Konsultation^HL70277|30|MIN|^^30^20260410100000^20260410103000|ARZ009^Kaufmann^Elisabeth^^^Dr.^med.
PID|||PAT445566^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Bachmann^Peter^Walter^^Herr||19950622|M|||Junkerngasse 16^^Horgen^^8810^CH||^^CP^0798390003
PV1||O|AMB^Sprechzimmer 5^^Ambulatorium||||ARZ009^Kaufmann^Elisabeth^^^Dr.^med.
RGS|1
AIS|1|A|KONSULTATION^Konsultation|||20260410100000|30|MIN
AIL|1|A|AMB^Sprechzimmer 5^^Ambulatorium
AIP|1|A|ARZ009^Kaufmann^Elisabeth^^^Dr.^med.
```

---

## 12. ORM^O01 - Radiologieauftrag (radiology order)

```
MSH|^~\&|KISIM|INSEL_BERN|RIS|INSEL_BERN|20260402110000||ORM^O01^ORM_O01|KISIM00012|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT778899^^^INSEL&2.16.756.5.30.1.128.1&ISO^MR||Fournier^Sophie^Pierre^^Mme||19830917|F|||Avenue d Ouchy 164^^Martigny^^1920^CH||^^CP^0783484455
PV1||I|ORTHO^Zimmer 212^Bett A^Orthopädie||||ARZ010^Steiner^Niklaus^^^Dr.^med.||||||||||||FALL04567
ORC|NW|ORD111^^^KISIM|||||^^^20260402130000^^R||20260402110000|ARZ010^Steiner^Niklaus^^^Dr.^med.
OBR|1|ORD111^^^KISIM||71020^Thorax 2 Ebenen^CPT|||20260402110000||||A|||||ARZ010^Steiner^Niklaus^^^Dr.^med.|||XRAY
```

---

## 13. ORU^R01 - Mikrobiologie-Befund (microbiology result)

```
MSH|^~\&|MIKROBIO|USZ_ZUERICH|KISIM|USZ_ZUERICH|20260403160000||ORU^R01^ORU_R01|MIK00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT334455^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Huber^Christine^Fritz^^Frau||19600102|F|||Eichenstrasse 148^^Frauenfeld^^8500^CH||^^PH^0522084463
PV1||I|MED^Zimmer 310^Bett B^Innere Medizin||||ARZ006^Wyss^Paul^^^Dr.^med.||||||||||||FALL05678
OBR|1|ORD222^^^KISIM|RES222^^^MIKROBIO|87040^Blutkultur^LN|||20260403060000|||||||||ARZ006^Wyss^Paul^^^Dr.^med.||||||20260403160000|||F
OBX|1|ST|600-7^Bakterien identifiziert^LN||Staphylococcus aureus||||||F
OBX|2|ST|18907-6^Methicillin-Resistenz^LN||MSSA||||||F
OBX|3|ST|18900-1^Cefazolin^LN||S||||||F
OBX|4|ST|18961-3^Vancomycin^LN||S||||||F
OBX|5|ST|18964-7^Oxacillin^LN||S||||||F
```

---

## 14. ADT^A31 - Personendaten-Aktualisierung (update person)

```
MSH|^~\&|KISIM|USZ_ZUERICH|MPI|USZ_ZUERICH|20260405120000||ADT^A31^ADT_A05|KISIM00014|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A31|20260405120000
PID|||PAT123456^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR~7560123456789^^^&2.16.756.5.31&ISO^SS||Burgener^Manfred^Heinz^^Herr||19650312|M|||Gerechtigkeitsgasse 169^^Chur^^7000^CH||^^PH^0815908760~^^CP^0763528981~^^Internet^manfred.burgener@swissonline.ch
PV1||N
```

---

## 15. ADT^A40 - Zusammenführung (patient merge)

```
MSH|^~\&|KISIM|USZ_ZUERICH|MPI|USZ_ZUERICH|20260406080000||ADT^A40^ADT_A39|KISIM00015|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A40|20260406080000
PID|||PAT123456^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Burgener^Manfred^Heinz^^Herr||19650312|M|||Gerechtigkeitsgasse 169^^Chur^^7000^CH||^^PH^0815908760
MRG|PAT999888^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR
```

---

## 16. ORM^O01 - Medikamentenverordnung (medication order)

```
MSH|^~\&|KISIM|INSEL_BERN|PHARMA|INSEL_BERN|20260407140000||ORM^O01^ORM_O01|KISIM00016|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT667788^^^INSEL&2.16.756.5.30.1.128.1&ISO^MR||Gerber^Ottilia^Fritz^^Frau||19710903|F|||Tannenstrasse 180^^Zurich^^8001^CH||^^CP^0783003964
PV1||I|ONKO^Zimmer 702^Bett A^Onkologie||||ARZ007^Fischer^Felix^^^Prof.^Dr.^med.||||||||||||FALL02345
ORC|NW|ORD333^^^KISIM|||||^^^20260407160000^^R||20260407140000|ARZ007^Fischer^Felix^^^Prof.^Dr.^med.
OBR|1|ORD333^^^KISIM||RXE^Medikamentenverordnung|||20260407140000
RXE|^^^20260407160000^20260414160000|68079^Paracetamol 1000mg^GTIN||1000|mg|TABL^Tablette||0||||||||||||||1^Packung
```

---

## 17. ADT^A11 - Storno Aufnahme (cancel admit)

```
MSH|^~\&|KISIM|KSW_WINTERTHUR|PDMS|KSW_WINTERTHUR|20260408070000||ADT^A11^ADT_A09|KISIM00017|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A11|20260408070000
PID|||PAT445566^^^KSW&2.16.756.5.30.1.129.1&ISO^MR||Bachmann^Peter^Walter^^Herr||19580817|M|||Junkerngasse 16^^Horgen^^8810^CH||^^PH^0444321934
PV1||I|CHIR^Zimmer 303^Bett A^Chirurgie||||ARZ011^Schneider^Margrit^^^Dr.^med.||||||||||||FALL06789|||||||||||||||||||||||||||20260408070000
```

---

## 18. ORU^R01 - Pathologie-Befund (pathology result)

```
MSH|^~\&|PATHO|USZ_ZUERICH|KISIM|USZ_ZUERICH|20260409110000||ORU^R01^ORU_R01|PATH00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT889900^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Egger^Nicole^Hans^^Frau||19550930|F|||Tessinerplatz 116^^Solothurn^^4500^CH||^^PH^0324243751
PV1||I|CHIR^Zimmer 501^Bett A^Chirurgie||||ARZ012^Meyer^Martin^^^Prof.^Dr.^med.||||||||||||FALL07890
OBR|1|ORD444^^^KISIM|RES444^^^PATHO|88305^Pathologie Gewebeuntersuchung^CPT|||20260408140000|||||||||ARZ012^Meyer^Martin^^^Prof.^Dr.^med.||||||20260409110000|||F
OBX|1|FT|22637-3^Pathologiebefund^LN||Makroskopie: Tumorexzisat linke Mamma, 3.2 x 2.1 x 1.8 cm\.br\Mikroskopie: Invasives duktales Karzinom, Grad 2\.br\Resektionsränder frei, minimaler Abstand 4mm\.br\pT1c pN0 (0/3) L0 V0 R0||||||F
OBX|2|NM|85319-2^Her2/neu Score^LN||2+||||||F
OBX|3|NM|85337-4^Ki-67 Proliferationsindex^LN||15|%|||||F
```

---

## 19. ORU^R01 - Radiologiebefund mit Bild (radiology result with embedded image)

```
MSH|^~\&|RIS|INSEL_BERN|KISIM|INSEL_BERN|20260410160000||ORU^R01^ORU_R01|RAD00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT778899^^^INSEL&2.16.756.5.30.1.128.1&ISO^MR||Fournier^Sophie^Pierre^^Mme||19830917|F|||Avenue d Ouchy 164^^Martigny^^1920^CH||^^CP^0783484455
PV1||I|ORTHO^Zimmer 212^Bett A^Orthopädie||||ARZ010^Steiner^Niklaus^^^Dr.^med.||||||||||||FALL04567
OBR|1|ORD111^^^KISIM|RES111^^^RIS|71020^Thorax 2 Ebenen^CPT|||20260402130000|||||||||ARZ010^Steiner^Niklaus^^^Dr.^med.||||||20260410160000|||F
OBX|1|FT|18782-3^Radiologiebefund^LN||Thorax in 2 Ebenen:\.br\Herz normal konfiguriert\.br\Lunge beidseits frei belüftet, keine Infiltrate\.br\Keine Pleuraergüsse\.br\Kein Pneumothorax\.br\Beurteilung: Normalbefund||||||F
OBX|2|ED|18782-3^Radiologiebefund^LN|IMG|^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM
DhAQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQU
FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAACAAIDASIAAhEBAxEB/8QAHwAA
AQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcI||||||F
```

---

## 20. ACK - Bestätigung (acknowledgment)

```
MSH|^~\&|LABOR|USZ_ZUERICH|KISIM|USZ_ZUERICH|20260411080100||ACK^A01^ACK|ACK00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
MSA|AA|KISIM00001|Nachricht erfolgreich verarbeitet
```
