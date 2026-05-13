# Mirth Connect (NextGen) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - stationäre Aufnahme (inpatient admission)

```
MSH|^~\&|HIS_SRC|SPITAL_THUN|MIRTH|INTEGRATION|20260301080000||ADT^A01^ADT_A01|MC00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A01|20260301080000
PID|||PAT800001^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR~7560444555666^^^&2.16.756.5.31&ISO^SS||Bachmann^Felix^Verena^^Herr||19700310|M|||Junkerngasse 119^^Winterthur^^8400^CH||^^PH^0522459021~^^CP^0793721264
PV1||I|MED^Zimmer 201^Bett A^Innere Medizin||||ARZ400^Schmid^Heinrich^^^Dr.^med.||||||||||||FALL40001|||||||||||||||||||||||||||20260301080000
IN1|1|KVG|SANITAS001|Sanitas Krankenversicherung|Jägergasse 3^^Zürich^^8021^CH||||||||||||||||||||||||||||||||||||||||||||756.3333.4444.55
```

---

## 2. ADT^A03 - Austritt (discharge)

```
MSH|^~\&|HIS_SRC|SPITAL_THUN|MIRTH|INTEGRATION|20260310140000||ADT^A03^ADT_A03|MC00002|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A03|20260310140000
PID|||PAT800001^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Bachmann^Felix^Verena^^Herr||19700310|M|||Junkerngasse 119^^Winterthur^^8400^CH||^^PH^0522459021
PV1||I|MED^Zimmer 201^Bett A^Innere Medizin||||ARZ400^Schmid^Heinrich^^^Dr.^med.||||||||||||FALL40001|||||||||||||||||||||||||||20260310140000
```

---

## 3. ADT^A04 - ambulante Registrierung (outpatient registration)

```
MSH|^~\&|HIS_SRC|SPITAL_THUN|MIRTH|INTEGRATION|20260315100000||ADT^A04^ADT_A01|MC00003|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A04|20260315100000
PID|||PAT800002^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Keller^Petra^Sophie^^Frau||19850712|F|||Gloriastrasse 79^^Baden^^5400^CH||^^CP^0774913565
PV1||O|AMB^Sprechzimmer 3^^Ambulatorium||||ARZ401^Brunner^Monika^^^Dr.^med.||||||||||||FALL40002|||||||||||||||||||||||||||20260315100000
```

---

## 4. ADT^A08 - Patientendaten-Änderung (patient update)

```
MSH|^~\&|HIS_SRC|SPITAL_THUN|MIRTH|INTEGRATION|20260318110000||ADT^A08^ADT_A01|MC00004|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A08|20260318110000
PID|||PAT800001^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Bachmann^Felix^Verena^^Herr||19700310|M|||Junkerngasse 119^^Winterthur^^8400^CH||^^PH^0522459021~^^CP^0793721264~^^Internet^felix.bachmann@gmail.com
PV1||N
```

---

## 5. ORM^O01 - Laborauftrag (laboratory order)

```
MSH|^~\&|HIS_SRC|SPITAL_THUN|MIRTH|INTEGRATION|20260320083000||ORM^O01^ORM_O01|MC00005|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT800003^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Widmer^Otto^Margrit^^Herr||19680425|M|||Kornhausstrasse 185^^Duebendorf^^8600^CH||^^CP^0776531214
PV1||I|CHIR^Zimmer 305^Bett A^Chirurgie||||ARZ402^Hess^Verena^^^Dr.^med.||||||||||||FALL40003
ORC|NW|ORD800^^^HIS_SRC|||||^^^20260320090000^^R||20260320083000|ARZ402^Hess^Verena^^^Dr.^med.
OBR|1|ORD800^^^HIS_SRC||CBC^Blutbild komplett^LN|||20260320083000||||A|||||ARZ402^Hess^Verena^^^Dr.^med.
```

---

## 6. ORU^R01 - Laborbefund (laboratory result)

```
MSH|^~\&|MIRTH|INTEGRATION|HIS_DST|SPITAL_THUN|20260320150000||ORU^R01^ORU_R01|MC00006|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT800003^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Widmer^Otto^Margrit^^Herr||19680425|M|||Kornhausstrasse 185^^Duebendorf^^8600^CH||^^CP^0776531214
PV1||I|CHIR^Zimmer 305^Bett A^Chirurgie||||ARZ402^Hess^Verena^^^Dr.^med.||||||||||||FALL40003
OBR|1|ORD800^^^HIS_SRC|RES800^^^LABSYS|CBC^Blutbild komplett^LN|||20260320083000|||||||||ARZ402^Hess^Verena^^^Dr.^med.||||||20260320150000|||F
OBX|1|NM|718-7^Hämoglobin^LN||155|g/L|135-175|N|||F
OBX|2|NM|6690-2^Leukozyten^LN||11.2|10*9/L|4.0-10.0|H|||F
OBX|3|NM|789-8^Thrombozyten^LN||280|10*9/L|150-400|N|||F
OBX|4|NM|17861-6^CRP^LN||45|mg/L|0-5|HH|||F
```

---

## 7. ORU^R01 - Befund mit eingebettetem PDF (result with embedded PDF)

```
MSH|^~\&|MIRTH|INTEGRATION|HIS_DST|SPITAL_THUN|20260321110000||ORU^R01^ORU_R01|MC00007|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT800001^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Bachmann^Felix^Verena^^Herr||19700310|M|||Junkerngasse 119^^Winterthur^^8400^CH||^^PH^0522459021
PV1||I|MED^Zimmer 201^Bett A^Innere Medizin||||ARZ400^Schmid^Heinrich^^^Dr.^med.||||||||||||FALL40001
OBR|1|ORD801^^^HIS_SRC|RES801^^^LABSYS|11502-2^Laborbericht^LN|||20260321090000|||||||||ARZ400^Schmid^Heinrich^^^Dr.^med.||||||20260321110000|||F
OBX|1|ED|11502-2^Laborbericht^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYmVyaWNodCkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozMzYKJSVFT0YK||||||F
```

---

## 8. MDM^T02 - Arztbrief mit Dokument (document notification with embedded PDF)

```
MSH|^~\&|MIRTH|INTEGRATION|ARCHIV|SPITAL_THUN|20260322140000||MDM^T02^MDM_T02|MC00008|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|T02|20260322140000
PID|||PAT800002^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Keller^Petra^Sophie^^Frau||19850712|F|||Gloriastrasse 79^^Baden^^5400^CH||^^CP^0774913565
PV1||O|AMB^Sprechzimmer 3^^Ambulatorium||||ARZ401^Brunner^Monika^^^Dr.^med.||||||||||||FALL40002
TXA|1|AR|AP|20260322140000|ARZ401^Brunner^Monika^^^Dr.^med.||||||||DOC400001||||||AU
OBX|1|ED|18842-5^Arztbrief^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKEFyenRicmllZikgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozMzYKJSVFT0YK||||||F
```

---

## 9. ORM^O01 - Radiologieauftrag (radiology order)

```
MSH|^~\&|HIS_SRC|SPITAL_THUN|MIRTH|INTEGRATION|20260402110000||ORM^O01^ORM_O01|MC00009|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT800003^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Widmer^Otto^Margrit^^Herr||19680425|M|||Kornhausstrasse 185^^Duebendorf^^8600^CH||^^CP^0776531214
PV1||I|CHIR^Zimmer 305^Bett A^Chirurgie||||ARZ402^Hess^Verena^^^Dr.^med.||||||||||||FALL40003
ORC|NW|ORD802^^^HIS_SRC|||||^^^20260402120000^^S||20260402110000|ARZ402^Hess^Verena^^^Dr.^med.
OBR|1|ORD802^^^HIS_SRC||71020^Thorax 2 Ebenen^CPT|||20260402110000||||A|||||ARZ402^Hess^Verena^^^Dr.^med.|||XRAY
```

---

## 10. ADT^A40 - Zusammenführung (patient merge)

```
MSH|^~\&|HIS_SRC|SPITAL_THUN|MIRTH|INTEGRATION|20260405080000||ADT^A40^ADT_A39|MC00010|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A40|20260405080000
PID|||PAT800001^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Bachmann^Felix^Verena^^Herr||19700310|M|||Junkerngasse 119^^Winterthur^^8400^CH||^^PH^0522459021
MRG|PAT899999^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR
```

---

## 11. SIU^S12 - Terminbuchung (appointment scheduling)

```
MSH|^~\&|HIS_SRC|SPITAL_THUN|MIRTH|INTEGRATION|20260406090000||SIU^S12^SIU_S12|MC00011|P|2.5|||AL|NE|CHE|UNICODE UTF-8
SCH|TERM400^^^HIS_SRC|||||ROUTINE^Routine-Termin^HL70276|KONSULTATION^Konsultation^HL70277|30|MIN|^^30^20260420100000^20260420103000|ARZ401^Brunner^Monika^^^Dr.^med.
PID|||PAT800002^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Keller^Petra^Sophie^^Frau||19850712|F|||Gloriastrasse 79^^Baden^^5400^CH||^^CP^0774913565
PV1||O|AMB^Sprechzimmer 3^^Ambulatorium||||ARZ401^Brunner^Monika^^^Dr.^med.
RGS|1
AIS|1|A|KONSULTATION^Konsultation|||20260420100000|30|MIN
```

---

## 12. ORU^R01 - Klinische Chemie (clinical chemistry result)

```
MSH|^~\&|MIRTH|INTEGRATION|HIS_DST|SPITAL_THUN|20260407150000||ORU^R01^ORU_R01|MC00012|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT800001^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Bachmann^Felix^Verena^^Herr||19700310|M|||Junkerngasse 119^^Winterthur^^8400^CH||^^PH^0522459021
PV1||I|MED^Zimmer 201^Bett A^Innere Medizin||||ARZ400^Schmid^Heinrich^^^Dr.^med.||||||||||||FALL40001
OBR|1|ORD803^^^HIS_SRC|RES803^^^LABSYS|2160-0^Nierenprofil^LN|||20260407090000|||||||||ARZ400^Schmid^Heinrich^^^Dr.^med.||||||20260407150000|||F
OBX|1|NM|2160-0^Kreatinin^LN||105|umol/L|62-106|N|||F
OBX|2|NM|3094-0^Harnstoff^LN||7.0|mmol/L|2.8-7.2|N|||F
OBX|3|NM|2823-3^Kalium^LN||3.8|mmol/L|3.5-5.1|N|||F
OBX|4|NM|2951-2^Natrium^LN||142|mmol/L|136-145|N|||F
```

---

## 13. ADT^A02 - Verlegung (patient transfer)

```
MSH|^~\&|HIS_SRC|SPITAL_THUN|MIRTH|INTEGRATION|20260408090000||ADT^A02^ADT_A02|MC00013|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A02|20260408090000
PID|||PAT800003^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Widmer^Otto^Margrit^^Herr||19680425|M|||Kornhausstrasse 185^^Duebendorf^^8600^CH||^^CP^0776531214
PV1||I|MED^Zimmer 210^Bett B^Innere Medizin||||ARZ400^Schmid^Heinrich^^^Dr.^med.||||||||||||FALL40003||||||||||||||||||||||CHIR^Zimmer 305^Bett A^Chirurgie||20260408090000
```

---

## 14. ADT^A31 - Personendaten-Aktualisierung (update person)

```
MSH|^~\&|HIS_SRC|SPITAL_THUN|MIRTH|INTEGRATION|20260409120000||ADT^A31^ADT_A05|MC00014|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A31|20260409120000
PID|||PAT800002^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR~7560555666777^^^&2.16.756.5.31&ISO^SS||Keller^Petra^Sophie^^Frau||19850712|F|||Gloriastrasse 79^^Baden^^5400^CH||^^CP^0774913565~^^Internet^petra.keller@gmx.ch
PV1||N
```

---

## 15. ORU^R01 - Mikrobiologie-Befund (microbiology result)

```
MSH|^~\&|MIRTH|INTEGRATION|HIS_DST|SPITAL_THUN|20260410160000||ORU^R01^ORU_R01|MC00015|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT800003^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Widmer^Otto^Margrit^^Herr||19680425|M|||Kornhausstrasse 185^^Duebendorf^^8600^CH||^^CP^0776531214
PV1||I|MED^Zimmer 210^Bett B^Innere Medizin||||ARZ400^Schmid^Heinrich^^^Dr.^med.||||||||||||FALL40003
OBR|1|ORD804^^^HIS_SRC|RES804^^^LABSYS|87040^Blutkultur^LN|||20260410060000|||||||||ARZ400^Schmid^Heinrich^^^Dr.^med.||||||20260410160000|||F
OBX|1|ST|600-7^Bakterien identifiziert^LN||Kein Wachstum nach 5 Tagen||||||F
```

---

## 16. ADT^A11 - Storno Aufnahme (cancel admit)

```
MSH|^~\&|HIS_SRC|SPITAL_THUN|MIRTH|INTEGRATION|20260411070000||ADT^A11^ADT_A09|MC00016|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A11|20260411070000
PID|||PAT800004^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Gerber^Sebastian^Rosa^^Herr||19820515|M|||Bahnhofstrasse 143^^Koniz^^3098^CH||^^CP^0771199108
PV1||I|CHIR^Zimmer 202^Bett A^Chirurgie||||ARZ402^Hess^Verena^^^Dr.^med.||||||||||||FALL40004|||||||||||||||||||||||||||20260411070000
```

---

## 17. ADT^A28 - Neuanlage Person (add person)

```
MSH|^~\&|HIS_SRC|SPITAL_THUN|MIRTH|INTEGRATION|20260412080000||ADT^A28^ADT_A05|MC00017|P|2.5|||AL|NE|CHE|UNICODE UTF-8
EVN|A28|20260412080000
PID|||PAT800005^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR~7566789012345^^^&2.16.756.5.31&ISO^SS||Studer^Helene^Heinz^^Frau||19930820|F|||Hauptstrasse 184^^Thalwil^^8800^CH||^^CP^0783553732~^^Internet^helene.studer@bluewin.ch
PV1||N
```

---

## 18. ORU^R01 - Pathologiebefund (pathology result)

```
MSH|^~\&|MIRTH|INTEGRATION|HIS_DST|SPITAL_THUN|20260413110000||ORU^R01^ORU_R01|MC00018|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT800002^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Keller^Petra^Sophie^^Frau||19850712|F|||Gloriastrasse 79^^Baden^^5400^CH||^^CP^0774913565
PV1||O|AMB^Sprechzimmer 3^^Ambulatorium||||ARZ401^Brunner^Monika^^^Dr.^med.||||||||||||FALL40002
OBR|1|ORD805^^^HIS_SRC|RES805^^^PATHO|88305^Histologie^CPT|||20260412140000|||||||||ARZ401^Brunner^Monika^^^Dr.^med.||||||20260413110000|||F
OBX|1|FT|22637-3^Pathologiebefund^LN||Makroskopie: Hautexzisat Rücken, 2.0 x 1.5 x 0.6 cm\.br\Mikroskopie: Benigner melanozytärer Naevus, komplett exzidiert\.br\Kein Anhalt für Malignität\.br\Resektionsränder frei||||||F
```

---

## 19. ORU^R01 - Hämatologie (hematology result)

```
MSH|^~\&|MIRTH|INTEGRATION|HIS_DST|SPITAL_THUN|20260414150000||ORU^R01^ORU_R01|MC00019|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT800001^^^SPITAL_THUN&2.16.756.5.30.1.180.1&ISO^MR||Bachmann^Felix^Verena^^Herr||19700310|M|||Junkerngasse 119^^Winterthur^^8400^CH||^^PH^0522459021
PV1||I|MED^Zimmer 201^Bett A^Innere Medizin||||ARZ400^Schmid^Heinrich^^^Dr.^med.||||||||||||FALL40001
OBR|1|ORD806^^^HIS_SRC|RES806^^^LABSYS|CBC^Blutbild komplett^LN|||20260414080000|||||||||ARZ400^Schmid^Heinrich^^^Dr.^med.||||||20260414150000|||F
OBX|1|NM|718-7^Hämoglobin^LN||138|g/L|135-175|N|||F
OBX|2|NM|6690-2^Leukozyten^LN||7.5|10*9/L|4.0-10.0|N|||F
OBX|3|NM|789-8^Thrombozyten^LN||210|10*9/L|150-400|N|||F
OBX|4|NM|4544-3^Hämatokrit^LN||0.41|L/L|0.40-0.52|N|||F
```

---

## 20. ACK - Bestätigung (acknowledgment)

```
MSH|^~\&|MIRTH|INTEGRATION|HIS_SRC|SPITAL_THUN|20260415080100||ACK^A01^ACK|ACK40001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
MSA|AA|MC00001|Nachricht erfolgreich weitergeleitet
```
