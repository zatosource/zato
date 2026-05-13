# Dedalus ORBIS - real HL7v2 ER7 messages

---

## 1. ADT^A01 - stationäre Aufnahme (inpatient admission)

```
MSH|^~\&|ORBIS|KSSG_STGALLEN|LABOR|KSSG_STGALLEN|20260301080000||ADT^A01^ADT_A01|ORBIS00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A01|20260301080000
PID|||PAT500001^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR~7560222333444^^^&2.16.756.5.31&ISO^SS||Baumann^Martin^Margrit^^Herr||19620115|M|||Hauptstrasse 89^^St. Gallen^^9000^CH||^^PH^0717197068~^^CP^0798634769
PV1||I|CHIR^Zimmer 301^Bett A^Chirurgie||||ARZ100^Kaufmann^Silvia^^^Prof.^Dr.^med.||||||||||||FALL10001|||||||||||||||||||||||||||20260301080000
IN1|1|KVG|HELSANA001|Helsana Versicherungen AG|Zürichstrasse 130^^Dübendorf^^8600^CH||||||||||||||||||||||||||||||||||||||||||||756.1111.2222.33
```

---

## 2. ADT^A02 - Verlegung (patient transfer)

```
MSH|^~\&|ORBIS|KSSG_STGALLEN|LABOR|KSSG_STGALLEN|20260303100000||ADT^A02^ADT_A02|ORBIS00002|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A02|20260303100000
PID|||PAT500001^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Baumann^Martin^Margrit^^Herr||19620115|M|||Hauptstrasse 89^^St. Gallen^^9000^CH||^^PH^0717197068
PV1||I|MED^Zimmer 405^Bett B^Innere Medizin||||ARZ101^Brunner^Sandra^^^Dr.^med.||||||||||||FALL10001||||||||||||||||||||||CHIR^Zimmer 301^Bett A^Chirurgie||20260303100000
```

---

## 3. ADT^A03 - Austritt (discharge)

```
MSH|^~\&|ORBIS|KSSG_STGALLEN|LABOR|KSSG_STGALLEN|20260310140000||ADT^A03^ADT_A03|ORBIS00003|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A03|20260310140000
PID|||PAT500001^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Baumann^Martin^Margrit^^Herr||19620115|M|||Hauptstrasse 89^^St. Gallen^^9000^CH||^^PH^0717197068
PV1||I|MED^Zimmer 405^Bett B^Innere Medizin||||ARZ101^Brunner^Sandra^^^Dr.^med.||||||||||||FALL10001|||||||||||||||||||||||||||20260310140000
```

---

## 4. ADT^A04 - ambulante Registrierung (outpatient registration)

```
MSH|^~\&|ORBIS|KSSG_STGALLEN|POLIKLINIK|KSSG_STGALLEN|20260315100000||ADT^A04^ADT_A01|ORBIS00004|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A04|20260315100000
PID|||PAT500002^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Fischer^Franziska^Peter^^Frau||19780823|F|||Kornhausstrasse 2^^Horgen^^8810^CH||^^CP^0764942968
PV1||O|AMB^Sprechzimmer 7^^Ambulatorium||||ARZ102^Bieri^Susanne^^^Dr.^med.||||||||||||FALL10002|||||||||||||||||||||||||||20260315100000
```

---

## 5. ADT^A08 - Patientendaten-Änderung (patient update)

```
MSH|^~\&|ORBIS|KSSG_STGALLEN|MPI|KSSG_STGALLEN|20260318110000||ADT^A08^ADT_A01|ORBIS00005|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A08|20260318110000
PID|||PAT500002^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Fischer^Franziska^Peter^^Frau||19780823|F|||Kornhausstrasse 2^^Horgen^^8810^CH||^^CP^0764942968~^^Internet^franziska.fischer@gmx.ch
PV1||O|AMB^Sprechzimmer 7^^Ambulatorium||||ARZ102^Bieri^Susanne^^^Dr.^med.||||||||||||FALL10002|||||||||||||||||||||||||||20260318110000
```

---

## 6. ORM^O01 - Laborauftrag (laboratory order)

```
MSH|^~\&|ORBIS|KSSG_STGALLEN|LABSYS|KSSG_STGALLEN|20260320083000||ORM^O01^ORM_O01|ORBIS00006|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT500003^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Berger^Stefan^Ruth^^Herr||19880530|M|||Rosenbergstrasse 136^^Zug^^6300^CH||^^CP^0775650199
PV1||I|MED^Zimmer 210^Bett A^Innere Medizin||||ARZ103^Bachmann^Johanna^^^Dr.^med.||||||||||||FALL10003
ORC|NW|ORD500^^^ORBIS|||||^^^20260320090000^^R||20260320083000|ARZ103^Bachmann^Johanna^^^Dr.^med.
OBR|1|ORD500^^^ORBIS||CBC^Blutbild komplett^LN|||20260320083000||||A|||||ARZ103^Bachmann^Johanna^^^Dr.^med.
```

---

## 7. ORU^R01 - Laborbefund (laboratory result)

```
MSH|^~\&|LABSYS|KSSG_STGALLEN|ORBIS|KSSG_STGALLEN|20260320150000||ORU^R01^ORU_R01|LAB10001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT500003^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Berger^Stefan^Ruth^^Herr||19880530|M|||Rosenbergstrasse 136^^Zug^^6300^CH||^^CP^0775650199
PV1||I|MED^Zimmer 210^Bett A^Innere Medizin||||ARZ103^Bachmann^Johanna^^^Dr.^med.||||||||||||FALL10003
OBR|1|ORD500^^^ORBIS|RES500^^^LABSYS|CBC^Blutbild komplett^LN|||20260320083000|||||||||ARZ103^Bachmann^Johanna^^^Dr.^med.||||||20260320150000|||F
OBX|1|NM|718-7^Hämoglobin^LN||152|g/L|135-175|N|||F
OBX|2|NM|6690-2^Leukozyten^LN||6.8|10*9/L|4.0-10.0|N|||F
OBX|3|NM|789-8^Thrombozyten^LN||220|10*9/L|150-400|N|||F
OBX|4|NM|4544-3^Hämatokrit^LN||0.44|L/L|0.40-0.52|N|||F
```

---

## 8. ORU^R01 - Befundbericht mit PDF (result with embedded PDF)

```
MSH|^~\&|LABSYS|KSSG_STGALLEN|ORBIS|KSSG_STGALLEN|20260321110000||ORU^R01^ORU_R01|LAB10002|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT500004^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Senn^Cornelia^Elisabeth^^Frau||19700218|F|||Dorfstrasse 40^^Rorschach^^9400^CH||^^PH^0718380260
PV1||I|ONKO^Zimmer 601^Bett A^Onkologie||||ARZ104^Roth^Jakob^^^Prof.^Dr.^med.||||||||||||FALL10004
OBR|1|ORD501^^^ORBIS|RES501^^^LABSYS|11502-2^Laborbericht^LN|||20260321090000|||||||||ARZ104^Roth^Jakob^^^Prof.^Dr.^med.||||||20260321110000|||F
OBX|1|ED|11502-2^Laborbericht^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYmVyaWNodCkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDIKJSVFT0YK||||||F
```

---

## 9. MDM^T02 - Arztbrief mit Dokument (discharge letter with embedded document)

```
MSH|^~\&|ORBIS|KSSG_STGALLEN|ARCHIV|KSSG_STGALLEN|20260322140000||MDM^T02^MDM_T02|ORBIS00009|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|T02|20260322140000
PID|||PAT500001^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Baumann^Martin^Margrit^^Herr||19620115|M|||Hauptstrasse 89^^St. Gallen^^9000^CH||^^PH^0717197068
PV1||I|MED^Zimmer 405^Bett B^Innere Medizin||||ARZ101^Brunner^Sandra^^^Dr.^med.||||||||||||FALL10001
TXA|1|AR|AP|20260322140000|ARZ101^Brunner^Sandra^^^Dr.^med.||||||||DOC100001||||||AU
OBX|1|ED|18842-5^Austrittsbericht^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1NiA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKEF1c3RyaXR0c2JlcmljaHQpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAowMDAwMDAwMjQyIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNSAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMzQ4CiUlRU9GCg==||||||F
```

---

## 10. ORM^O01 - Radiologieauftrag (radiology order)

```
MSH|^~\&|ORBIS|KSSG_STGALLEN|RIS|KSSG_STGALLEN|20260402110000||ORM^O01^ORM_O01|ORBIS00010|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT500005^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Keller^Walter^Elisabeth^^Herr||19850411|M|||Dorfstrasse 29^^Aarau^^5000^CH||^^CP^0798389284
PV1||E|NOTFALL^Box 2^^Notfallstation||||ARZ105^Huber^Margrit^^^Dr.^med.||||||||||||FALL10005
ORC|NW|ORD502^^^ORBIS|||||^^^20260402120000^^S||20260402110000|ARZ105^Huber^Margrit^^^Dr.^med.
OBR|1|ORD502^^^ORBIS||71020^Thorax 2 Ebenen^CPT|||20260402110000||||A|||||ARZ105^Huber^Margrit^^^Dr.^med.|||XRAY
```

---

## 11. SIU^S12 - Terminbuchung (appointment scheduling)

```
MSH|^~\&|ORBIS|KSSG_STGALLEN|TERMIN|KSSG_STGALLEN|20260403090000||SIU^S12^SIU_S12|ORBIS00011|P|2.5|||AL|NE|CHE|UNICODE UTF-8
SCH|TERM001^^^ORBIS|||||ROUTINE^Routine-Termin^HL70276|KONSULTATION^Konsultation^HL70277|20|MIN|^^20^20260415140000^20260415142000|ARZ102^Bieri^Susanne^^^Dr.^med.
PID|||PAT500002^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Fischer^Franziska^Peter^^Frau||19780823|F|||Kornhausstrasse 2^^Horgen^^8810^CH||^^CP^0764942968
PV1||O|AMB^Sprechzimmer 7^^Ambulatorium||||ARZ102^Bieri^Susanne^^^Dr.^med.
RGS|1
AIS|1|A|KONSULTATION^Konsultation|||20260415140000|20|MIN
```

---

## 12. ADT^A40 - Zusammenführung (patient merge)

```
MSH|^~\&|ORBIS|KSSG_STGALLEN|MPI|KSSG_STGALLEN|20260405080000||ADT^A40^ADT_A39|ORBIS00012|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A40|20260405080000
PID|||PAT500001^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Baumann^Martin^Margrit^^Herr||19620115|M|||Hauptstrasse 89^^St. Gallen^^9000^CH||^^PH^0717197068
MRG|PAT599999^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR
```

---

## 13. ORU^R01 - Mikrobiologie-Befund (microbiology result)

```
MSH|^~\&|MIKROBIO|KSSG_STGALLEN|ORBIS|KSSG_STGALLEN|20260406160000||ORU^R01^ORU_R01|MIK10001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT500003^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Berger^Stefan^Ruth^^Herr||19880530|M|||Rosenbergstrasse 136^^Zug^^6300^CH||^^CP^0775650199
PV1||I|MED^Zimmer 210^Bett A^Innere Medizin||||ARZ103^Bachmann^Johanna^^^Dr.^med.||||||||||||FALL10003
OBR|1|ORD503^^^ORBIS|RES503^^^MIKROBIO|87186^Antibiogramm^LN|||20260406060000|||||||||ARZ103^Bachmann^Johanna^^^Dr.^med.||||||20260406160000|||F
OBX|1|ST|600-7^Bakterien identifiziert^LN||Klebsiella pneumoniae||||||F
OBX|2|ST|18862-3^Amoxicillin/Clavulansäure^LN||R||||||F
OBX|3|ST|18928-2^Gentamicin^LN||S||||||F
OBX|4|ST|18955-5^Ciprofloxacin^LN||I||||||F
OBX|5|ST|18996-9^Meropenem^LN||S||||||F
```

---

## 14. ADT^A11 - Storno Aufnahme (cancel admit)

```
MSH|^~\&|ORBIS|KSSG_STGALLEN|LABOR|KSSG_STGALLEN|20260407070000||ADT^A11^ADT_A09|ORBIS00014|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A11|20260407070000
PID|||PAT500006^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Hofmann^Thomas^Elisabeth^^Herr||19750930|M|||Stauffacherstrasse 115^^Zug^^6300^CH||^^PH^0413698179
PV1||I|CHIR^Zimmer 303^Bett A^Chirurgie||||ARZ100^Kaufmann^Silvia^^^Prof.^Dr.^med.||||||||||||FALL10006|||||||||||||||||||||||||||20260407070000
```

---

## 15. ADT^A28 - Neuanlage Person (add person)

```
MSH|^~\&|ORBIS|KSSG_STGALLEN|MPI|KSSG_STGALLEN|20260408080000||ADT^A28^ADT_A05|ORBIS00015|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A28|20260408080000
PID|||PAT500007^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR~7564567890123^^^&2.16.756.5.31&ISO^SS||Burgener^Monika^Ruth^^Frau||19910207|F|||Niederdorfstrasse 148^^Chur^^7000^CH||^^CP^0764704463~^^Internet^monika.burgener@swissonline.ch
PV1||N
```

---

## 16. ORU^R01 - Klinische Chemie (clinical chemistry result)

```
MSH|^~\&|CHEMIE|KSSG_STGALLEN|ORBIS|KSSG_STGALLEN|20260409150000||ORU^R01^ORU_R01|CHEM10001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT500005^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Keller^Walter^Elisabeth^^Herr||19850411|M|||Dorfstrasse 29^^Aarau^^5000^CH||^^CP^0798389284
PV1||E|NOTFALL^Box 2^^Notfallstation||||ARZ105^Huber^Margrit^^^Dr.^med.||||||||||||FALL10005
OBR|1|ORD504^^^ORBIS|RES504^^^CHEMIE|2160-0^Kreatinin^LN|||20260409090000|||||||||ARZ105^Huber^Margrit^^^Dr.^med.||||||20260409150000|||F
OBX|1|NM|2160-0^Kreatinin^LN||98|umol/L|62-106|N|||F
OBX|2|NM|3094-0^Harnstoff^LN||6.1|mmol/L|2.8-7.2|N|||F
OBX|3|NM|2823-3^Kalium^LN||4.5|mmol/L|3.5-5.1|N|||F
OBX|4|NM|2951-2^Natrium^LN||141|mmol/L|136-145|N|||F
OBX|5|NM|17861-6^CRP^LN||85|mg/L|0-5|HH|||F
```

---

## 17. ADT^A31 - Personendaten-Aktualisierung (update person)

```
MSH|^~\&|ORBIS|KSSG_STGALLEN|MPI|KSSG_STGALLEN|20260410120000||ADT^A31^ADT_A05|ORBIS00017|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A31|20260410120000
PID|||PAT500001^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR~7560222333444^^^&2.16.756.5.31&ISO^SS||Baumann^Martin^Margrit^^Herr||19620115|M|||Hauptstrasse 89^^St. Gallen^^9000^CH||^^PH^0717197068~^^CP^0798634769~^^Internet^martin.baumann@sunrise.ch
PV1||N
```

---

## 18. ORU^R01 - Pathologiebefund (pathology result)

```
MSH|^~\&|PATHO|KSSG_STGALLEN|ORBIS|KSSG_STGALLEN|20260411110000||ORU^R01^ORU_R01|PATH10001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT500004^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Senn^Cornelia^Elisabeth^^Frau||19700218|F|||Dorfstrasse 40^^Rorschach^^9400^CH||^^PH^0718380260
PV1||I|ONKO^Zimmer 601^Bett A^Onkologie||||ARZ104^Roth^Jakob^^^Prof.^Dr.^med.||||||||||||FALL10004
OBR|1|ORD505^^^ORBIS|RES505^^^PATHO|88305^Pathologie Gewebeuntersuchung^CPT|||20260410140000|||||||||ARZ104^Roth^Jakob^^^Prof.^Dr.^med.||||||20260411110000|||F
OBX|1|FT|22637-3^Pathologiebefund^LN||Makroskopie: Lungenresektat rechter Oberlappen, 5.3 x 4.1 x 3.8 cm\.br\Mikroskopie: Plattenepithelkarzinom, mässig differenziert (G2)\.br\Resektionsränder tumorfrei, minimaler Abstand 8mm\.br\Lymphknoten: 0/12 positiv\.br\pT2a pN0 L0 V0 R0||||||F
```

---

## 19. ORM^O01 - Medikamentenverordnung (medication order)

```
MSH|^~\&|ORBIS|KSSG_STGALLEN|PHARMA|KSSG_STGALLEN|20260412140000||ORM^O01^ORM_O01|ORBIS00019|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT500003^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Berger^Stefan^Ruth^^Herr||19880530|M|||Rosenbergstrasse 136^^Zug^^6300^CH||^^CP^0775650199
PV1||I|MED^Zimmer 210^Bett A^Innere Medizin||||ARZ103^Bachmann^Johanna^^^Dr.^med.||||||||||||FALL10003
ORC|NW|ORD506^^^ORBIS|||||^^^20260412160000^^R||20260412140000|ARZ103^Bachmann^Johanna^^^Dr.^med.
OBR|1|ORD506^^^ORBIS||RXE^Medikamentenverordnung|||20260412140000
RXE|^^^20260412160000^20260419160000|7680563860011^Amoxicillin 1000mg^GTIN||1000|mg|TABL^Tablette||0||||||||||||||1^Packung
```

---

## 20. ACK - Bestätigung (acknowledgment)

```
MSH|^~\&|LABOR|KSSG_STGALLEN|ORBIS|KSSG_STGALLEN|20260413080100||ACK^A01^ACK|ACK10001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
MSA|AA|ORBIS00001|Nachricht erfolgreich verarbeitet
```
