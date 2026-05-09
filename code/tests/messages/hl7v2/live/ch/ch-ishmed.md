# i.s.h.med (Oracle Cerner/SAP) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - stationäre Aufnahme (inpatient admission)

```
MSH|^~\&|ISHMED|LUKS_LUZERN|LABOR|LUKS_LUZERN|20260301080000||ADT^A01^ADT_A01|ISH00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A01|20260301080000
PID|||PAT600001^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR~7560333444555^^^&2.16.756.5.31&ISO^SS||Egger^Martin^Erika^^Herr||19580722|M|||Dorfstrasse 118^^Solothurn^^4500^CH||^^PH^0327645608~^^CP^0786447745
PV1||I|MED^Zimmer 301^Bett A^Innere Medizin||||ARZ200^Vogel^Heidi^^^Prof.^Dr.^med.|ARZ201^Hess^Andreas^^^Dr.^med.||||||||||||FALL20001|||||||||||||||||||||||||||20260301080000
IN1|1|KVG|CONCORDIA001|Concordia Versicherungen|Bundesplatz 15^^Luzern^^6002^CH||||||||||||||||||||||||||||||||||||||||||||756.2222.3333.44
```

---

## 2. ADT^A02 - Verlegung (patient transfer)

```
MSH|^~\&|ISHMED|LUKS_LUZERN|LABOR|LUKS_LUZERN|20260303090000||ADT^A02^ADT_A02|ISH00002|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A02|20260303090000
PID|||PAT600001^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR||Egger^Martin^Erika^^Herr||19580722|M|||Dorfstrasse 118^^Solothurn^^4500^CH||^^PH^0327645608
PV1||I|KARD^Zimmer 501^Bett B^Kardiologie||||ARZ202^Walder^Helene^^^Dr.^med.||||||||||||FALL20001||||||||||||||||||||||MED^Zimmer 301^Bett A^Innere Medizin||20260303090000
```

---

## 3. ADT^A03 - Austritt (discharge)

```
MSH|^~\&|ISHMED|LUKS_LUZERN|LABOR|LUKS_LUZERN|20260310150000||ADT^A03^ADT_A03|ISH00003|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A03|20260310150000
PID|||PAT600001^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR||Egger^Martin^Erika^^Herr||19580722|M|||Dorfstrasse 118^^Solothurn^^4500^CH||^^PH^0327645608
PV1||I|KARD^Zimmer 501^Bett B^Kardiologie||||ARZ202^Walder^Helene^^^Dr.^med.||||||||||||FALL20001|||||||||||||||||||||||||||20260310150000
```

---

## 4. ADT^A04 - ambulante Registrierung (outpatient registration)

```
MSH|^~\&|ISHMED|KSA_AARAU|POLIKLINIK|KSA_AARAU|20260315100000||ADT^A04^ADT_A01|ISH00004|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A04|20260315100000
PID|||PAT600002^^^KSA&2.16.756.5.30.1.161.1&ISO^MR||Schneider^Ottilia^Sophie^^Frau||19820614|F|||Dorfstrasse 36^^Chur^^7000^CH||^^CP^0783616590
PV1||O|AMB^Sprechzimmer 5^^Ambulatorium||||ARZ203^Fischer^Petra^^^Dr.^med.||||||||||||FALL20002|||||||||||||||||||||||||||20260315100000
```

---

## 5. ADT^A08 - Patientendaten-Änderung (patient update)

```
MSH|^~\&|ISHMED|LUKS_LUZERN|MPI|LUKS_LUZERN|20260318110000||ADT^A08^ADT_A01|ISH00005|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A08|20260318110000
PID|||PAT600001^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR||Egger^Martin^Erika^^Herr||19580722|M|||Dorfstrasse 118^^Solothurn^^4500^CH||^^PH^0327645608~^^CP^0786447745~^^Internet^martin.egger@netplus.ch
PV1||I|KARD^Zimmer 501^Bett B^Kardiologie||||ARZ202^Walder^Helene^^^Dr.^med.||||||||||||FALL20001|||||||||||||||||||||||||||20260318110000
IN1|1|KVG|CONCORDIA001|Concordia Versicherungen|Bundesplatz 15^^Luzern^^6002^CH||||||||||||||||||||||||||||||||||||||||||||756.2222.3333.44
```

---

## 6. ORM^O01 - Laborauftrag (laboratory order)

```
MSH|^~\&|ISHMED|LUKS_LUZERN|LABSYS|LUKS_LUZERN|20260320083000||ORM^O01^ORM_O01|ISH00006|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT600003^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR||Meier^Thomas^Hans^^Herr||19700905|M|||Birkenstrasse 120^^Basel^^4001^CH||^^CP^0789209747
PV1||I|NEURO^Zimmer 402^Bett A^Neurologie||||ARZ204^Studer^Werner^^^Dr.^med.||||||||||||FALL20003
ORC|NW|ORD600^^^ISHMED|||||^^^20260320090000^^R||20260320083000|ARZ204^Studer^Werner^^^Dr.^med.
OBR|1|ORD600^^^ISHMED||24356-8^Liquordiagnostik^LN|||20260320083000||||A|||||ARZ204^Studer^Werner^^^Dr.^med.
```

---

## 7. ORU^R01 - Laborbefund (laboratory result)

```
MSH|^~\&|LABSYS|LUKS_LUZERN|ISHMED|LUKS_LUZERN|20260320160000||ORU^R01^ORU_R01|LAB20001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT600003^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR||Meier^Thomas^Hans^^Herr||19700905|M|||Birkenstrasse 120^^Basel^^4001^CH||^^CP^0789209747
PV1||I|NEURO^Zimmer 402^Bett A^Neurologie||||ARZ204^Studer^Werner^^^Dr.^med.||||||||||||FALL20003
OBR|1|ORD600^^^ISHMED|RES600^^^LABSYS|24356-8^Liquordiagnostik^LN|||20260320083000|||||||||ARZ204^Studer^Werner^^^Dr.^med.||||||20260320160000|||F
OBX|1|NM|2880-3^Protein im Liquor^LN||450|mg/L|150-450|N|||F
OBX|2|NM|2342-4^Glukose im Liquor^LN||3.2|mmol/L|2.2-3.9|N|||F
OBX|3|NM|26464-8^Leukozyten im Liquor^LN||2|/uL|0-5|N|||F
OBX|4|ST|600-7^Gram-Färbung^LN||Keine Bakterien nachgewiesen||||||F
```

---

## 8. ORU^R01 - Befund mit eingebettetem PDF (result with embedded PDF)

```
MSH|^~\&|LABSYS|LUKS_LUZERN|ISHMED|LUKS_LUZERN|20260321100000||ORU^R01^ORU_R01|LAB20002|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT600004^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR||Meyer^Brigitte^Robert^^Frau||19651130|F|||Bahnhofstrasse 192^^Horgen^^8810^CH||^^PH^0445706100
PV1||I|MED^Zimmer 215^Bett B^Innere Medizin||||ARZ200^Vogel^Heidi^^^Prof.^Dr.^med.||||||||||||FALL20004
OBR|1|ORD601^^^ISHMED|RES601^^^LABSYS|11502-2^Laborbericht^LN|||20260321080000|||||||||ARZ200^Vogel^Heidi^^^Prof.^Dr.^med.||||||20260321100000|||F
OBX|1|ED|11502-2^Laborbericht^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKEJlZnVuZGJlcmljaHQpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAowMDAwMDAwMjQyIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNSAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMzM2CiUlRU9GCg==||||||F
```

---

## 9. MDM^T02 - Arztbrief (medical document with embedded PDF)

```
MSH|^~\&|ISHMED|KSA_AARAU|ARCHIV|KSA_AARAU|20260322140000||MDM^T02^MDM_T02|ISH00009|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|T02|20260322140000
PID|||PAT600002^^^KSA&2.16.756.5.30.1.161.1&ISO^MR||Schneider^Ottilia^Sophie^^Frau||19820614|F|||Dorfstrasse 36^^Chur^^7000^CH||^^CP^0783616590
PV1||O|AMB^Sprechzimmer 5^^Ambulatorium||||ARZ203^Fischer^Petra^^^Dr.^med.||||||||||||FALL20002
TXA|1|AR|AP|20260322140000|ARZ203^Fischer^Petra^^^Dr.^med.||||||||DOC200001||||||AU
OBX|1|ED|18842-5^Arztbrief^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKEFyenRicmllZikgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozMzYKJSVFT0YK||||||F
```

---

## 10. ORM^O01 - Radiologieauftrag (radiology order)

```
MSH|^~\&|ISHMED|KSA_AARAU|RIS|KSA_AARAU|20260402110000||ORM^O01^ORM_O01|ISH00010|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT600005^^^KSA&2.16.756.5.30.1.161.1&ISO^MR||Huber^Rudolf^Otto^^Herr||19750303|M|||Limmatquai 65^^Rorschach^^9400^CH||^^CP^0797962355
PV1||E|NOTFALL^Box 4^^Notfallstation||||ARZ205^Schaerer^Christine^^^Dr.^med.||||||||||||FALL20005
ORC|NW|ORD602^^^ISHMED|||||^^^20260402120000^^S||20260402110000|ARZ205^Schaerer^Christine^^^Dr.^med.
OBR|1|ORD602^^^ISHMED||71020^Thorax 2 Ebenen^CPT|||20260402110000||||A|||||ARZ205^Schaerer^Christine^^^Dr.^med.|||XRAY
```

---

## 11. SIU^S12 - Terminbuchung (appointment scheduling)

```
MSH|^~\&|ISHMED|LUKS_LUZERN|TERMIN|LUKS_LUZERN|20260403090000||SIU^S12^SIU_S12|ISH00011|P|2.5|||AL|NE|CHE|UNICODE UTF-8
SCH|TERM200^^^ISHMED|||||ROUTINE^Routine-Termin^HL70276|NACHKONTROLLE^Nachkontrolle^HL70277|30|MIN|^^30^20260415140000^20260415143000|ARZ202^Walder^Helene^^^Dr.^med.
PID|||PAT600001^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR||Egger^Martin^Erika^^Herr||19580722|M|||Dorfstrasse 118^^Solothurn^^4500^CH||^^PH^0327645608
PV1||O|AMB^Sprechzimmer 3^^Ambulatorium||||ARZ202^Walder^Helene^^^Dr.^med.
RGS|1
AIS|1|A|NACHKONTROLLE^Nachkontrolle|||20260415140000|30|MIN
```

---

## 12. ADT^A40 - Zusammenführung (patient merge)

```
MSH|^~\&|ISHMED|LUKS_LUZERN|MPI|LUKS_LUZERN|20260405080000||ADT^A40^ADT_A39|ISH00012|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A40|20260405080000
PID|||PAT600001^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR||Egger^Martin^Erika^^Herr||19580722|M|||Dorfstrasse 118^^Solothurn^^4500^CH||^^PH^0327645608
MRG|PAT699999^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR
```

---

## 13. ORU^R01 - Hämatologie-Befund (hematology result)

```
MSH|^~\&|HEMATO|LUKS_LUZERN|ISHMED|LUKS_LUZERN|20260406150000||ORU^R01^ORU_R01|HEM20001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT600001^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR||Egger^Martin^Erika^^Herr||19580722|M|||Dorfstrasse 118^^Solothurn^^4500^CH||^^PH^0327645608
PV1||I|KARD^Zimmer 501^Bett B^Kardiologie||||ARZ202^Walder^Helene^^^Dr.^med.||||||||||||FALL20001
OBR|1|ORD603^^^ISHMED|RES603^^^HEMATO|CBC^Blutbild komplett^LN|||20260406080000|||||||||ARZ202^Walder^Helene^^^Dr.^med.||||||20260406150000|||F
OBX|1|NM|718-7^Hämoglobin^LN||132|g/L|135-175|L|||F
OBX|2|NM|6690-2^Leukozyten^LN||5.9|10*9/L|4.0-10.0|N|||F
OBX|3|NM|789-8^Thrombozyten^LN||198|10*9/L|150-400|N|||F
OBX|4|NM|787-2^Erythrozyten^LN||4.2|10*12/L|4.3-5.8|L|||F
```

---

## 14. ADT^A31 - Personendaten-Aktualisierung (update person)

```
MSH|^~\&|ISHMED|LUKS_LUZERN|MPI|LUKS_LUZERN|20260407120000||ADT^A31^ADT_A05|ISH00014|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A31|20260407120000
PID|||PAT600003^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR~7560444555666^^^&2.16.756.5.31&ISO^SS||Meier^Thomas^Hans^^Herr||19700905|M|||Birkenstrasse 120^^Basel^^4001^CH||^^CP^0789209747~^^Internet^thomas.meier@netplus.ch
PV1||N
```

---

## 15. ADT^A11 - Storno Aufnahme (cancel admit)

```
MSH|^~\&|ISHMED|KSA_AARAU|LABOR|KSA_AARAU|20260408070000||ADT^A11^ADT_A09|ISH00015|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A11|20260408070000
PID|||PAT600006^^^KSA&2.16.756.5.30.1.161.1&ISO^MR||Senn^Daniel^Erika^^Herr||19900212|M|||Stauffacherstrasse 8^^Wil^^9500^CH||^^CP^0777677876
PV1||I|CHIR^Zimmer 201^Bett A^Chirurgie||||ARZ206^Marti^Silvia^^^Dr.^med.||||||||||||FALL20006|||||||||||||||||||||||||||20260408070000
```

---

## 16. ORU^R01 - Klinische Chemie (clinical chemistry)

```
MSH|^~\&|CHEMIE|LUKS_LUZERN|ISHMED|LUKS_LUZERN|20260409150000||ORU^R01^ORU_R01|CHEM20001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT600005^^^KSA&2.16.756.5.30.1.161.1&ISO^MR||Huber^Rudolf^Otto^^Herr||19750303|M|||Limmatquai 65^^Rorschach^^9400^CH||^^CP^0797962355
PV1||E|NOTFALL^Box 4^^Notfallstation||||ARZ205^Schaerer^Christine^^^Dr.^med.||||||||||||FALL20005
OBR|1|ORD604^^^ISHMED|RES604^^^CHEMIE|24323-8^Bilan hépatique^LN|||20260409090000|||||||||ARZ205^Schaerer^Christine^^^Dr.^med.||||||20260409150000|||F
OBX|1|NM|1742-6^ALAT (GPT)^LN||125|U/L|7-56|HH|||F
OBX|2|NM|1920-8^ASAT (GOT)^LN||98|U/L|10-40|HH|||F
OBX|3|NM|6768-6^Alkalische Phosphatase^LN||310|U/L|44-147|HH|||F
OBX|4|NM|1975-2^Gesamtbilirubin^LN||45|umol/L|3-22|HH|||F
```

---

## 17. ADT^A28 - Neuanlage Person (add person)

```
MSH|^~\&|ISHMED|LUKS_LUZERN|MPI|LUKS_LUZERN|20260410080000||ADT^A28^ADT_A05|ISH00017|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A28|20260410080000
PID|||PAT600007^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR~7565678901234^^^&2.16.756.5.31&ISO^SS||Berger^Elisabeth^Fritz^^Frau||19950325|F|||Gerechtigkeitsgasse 150^^Koniz^^3098^CH||^^CP^0789585827~^^Internet^elisabeth.berger@sunrise.ch
PV1||N
```

---

## 18. ORU^R01 - Mikrobiologie-Befund (microbiology result)

```
MSH|^~\&|MIKROBIO|LUKS_LUZERN|ISHMED|LUKS_LUZERN|20260411160000||ORU^R01^ORU_R01|MIK20001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT600003^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR||Meier^Thomas^Hans^^Herr||19700905|M|||Birkenstrasse 120^^Basel^^4001^CH||^^CP^0789209747
PV1||I|NEURO^Zimmer 402^Bett A^Neurologie||||ARZ204^Studer^Werner^^^Dr.^med.||||||||||||FALL20003
OBR|1|ORD605^^^ISHMED|RES605^^^MIKROBIO|87040^Blutkultur^LN|||20260411060000|||||||||ARZ204^Studer^Werner^^^Dr.^med.||||||20260411160000|||F
OBX|1|ST|600-7^Bakterien identifiziert^LN||Kein Wachstum nach 5 Tagen||||||F
```

---

## 19. ORU^R01 - Pathologiebefund (pathology result)

```
MSH|^~\&|PATHO|KSA_AARAU|ISHMED|KSA_AARAU|20260412110000||ORU^R01^ORU_R01|PATH20001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT600002^^^KSA&2.16.756.5.30.1.161.1&ISO^MR||Schneider^Ottilia^Sophie^^Frau||19820614|F|||Dorfstrasse 36^^Chur^^7000^CH||^^CP^0783616590
PV1||O|AMB^Sprechzimmer 5^^Ambulatorium||||ARZ203^Fischer^Petra^^^Dr.^med.||||||||||||FALL20002
OBR|1|ORD606^^^ISHMED|RES606^^^PATHO|88305^Histopathologische Untersuchung^CPT|||20260411140000|||||||||ARZ203^Fischer^Petra^^^Dr.^med.||||||20260412110000|||F
OBX|1|FT|22637-3^Pathologiebefund^LN||Makroskopie: Hautexzisat linker Unterarm, 1.5 x 1.2 x 0.8 cm\.br\Mikroskopie: Basalzellkarzinom, nodulär, komplett exzidiert\.br\Resektionsränder allseits frei, minimaler Abstand 3mm\.br\Beurteilung: R0-Resektion||||||F
```

---

## 20. ACK - Bestätigung (acknowledgment)

```
MSH|^~\&|LABOR|LUKS_LUZERN|ISHMED|LUKS_LUZERN|20260413080100||ACK^A01^ACK|ACK20001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
MSA|AA|ISH00001|Nachricht erfolgreich verarbeitet
```
