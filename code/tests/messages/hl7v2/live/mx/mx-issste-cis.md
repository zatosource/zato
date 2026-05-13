# ISSSTE CIS (Radiology/RIS/PACS) - real HL7v2 ER7 messages

---

## 1. ORM^O01 - Chest X-ray order

```
MSH|^~\&|ISSSTE_CIS|HRLALM_CDMX|RIS_SYS|HRLALM|20250310091200||ORM^O01^ORM_O01|ISSSTE20250310091200001|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE0849199989^^^ISSSTE^SS~CURP:RAMG720415HSPNDR30^^^CURP^NI||Ramirez^Guerrero^Miguel^Arturo||19720415|M|||Calle Morelos 1842 Col Polanco^^Ciudad De Mexico^DIF^11560^MX||5540389914^^^miguel.ramirez@outlook.com||SPA|M|CAT|||RAMG720415HSPNDR30||||Ciudad de Mexico|MX
PV1|1|O|RAD^01^A^HRLALM||||42197^Barrera^Duarte^Ernesto^^^DR|||RAD||||REF|||42197^Barrera^Duarte^Ernesto^^^DR|IN||ISSSTE
ORC|NW|RAD20250310001|||||^^^20250310100000^^R||20250310091200|ELECHUGA^Villegas^Ornelas^Humberto^^^DR|||||HRLALM
OBR|1|RAD20250310001||71020^Radiografia de torax PA y lateral^LOCAL|||20250310091200||||N|||||42197^Barrera^Duarte^Ernesto^^^DR||||||RAD|||^^^20250310100000^^R||||CHEST
DG1|1|I10|J18.9^Neumonia no especificada^I10|||W
```

---

## 2. ORM^O01 - CT abdomen with contrast

```
MSH|^~\&|ISSSTE_CIS|HRLALM_CDMX|RIS_SYS|HRLALM|20250312104500||ORM^O01^ORM_O01|ISSSTE20250312104500002|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE7540108245^^^ISSSTE^SS~CURP:CALA800630MDFZLN03^^^CURP^NI||Castillo^Lozano^Andrea^Mariana||19800630|F|||Av Reforma 2654 Col Condesa^^Ciudad De Mexico^DIF^06140^MX||5575374230^^^andrea.castillo@correo.mx||SPA|M|CAT|||CALA800630MDFZLN03||||Ciudad de Mexico|MX
PV1|1|I|CIR^205^A^HRLALM||||26524^Espinoza^Talavera^Ricardo^^^DR|||CIR||||ADM
ORC|NW|RAD20250312002|||||^^^20250312130000^^R||20250312104500|AOLIVERA^Pineda^Aguilar^Salvador^^^DR|||||HRLALM
OBR|1|RAD20250312002||74178^TC abdomen y pelvis con contraste^LOCAL|||20250312104500||||N|||||26524^Espinoza^Talavera^Ricardo^^^DR||||||RAD|||^^^20250312130000^^R||||ABDOMEN
DG1|1|I10|K80.2^Calculo de vesicula biliar sin colecistitis^I10|||A
```

---

## 3. ORU^R01 - Chest X-ray report

```
MSH|^~\&|ISSSTE_CIS|HRLALM_CDMX|HIS_RCV|HRLALM|20250310143000||ORU^R01^ORU_R01|ISSSTE20250310143000003|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE0849199989^^^ISSSTE^SS~CURP:RAMG720415HSPNDR30^^^CURP^NI||Ramirez^Guerrero^Miguel^Arturo||19720415|M|||Calle Morelos 1842 Col Polanco^^Ciudad De Mexico^DIF^11560^MX||5540389914^^^miguel.ramirez@outlook.com||SPA|M|CAT|||RAMG720415HSPNDR30||||Ciudad de Mexico|MX
PV1|1|O|RAD^01^A^HRLALM||||42197^Barrera^Duarte^Ernesto^^^DR|||RAD
ORC|RE|RAD20250310001||||||^^^20250310100000^^R||20250310143000|ELECHUGA^Villegas^Ornelas^Humberto^^^DR
OBR|1|RAD20250310001||71020^Radiografia de torax PA y lateral^LOCAL|||20250310100000||||N|||||42197^Barrera^Duarte^Ernesto^^^DR||||||RAD
OBX|1|FT|71020^Radiografia de torax^LOCAL||Campos pulmonares con adecuada expansion. Indice cardiotoracico normal. No se observan infiltrados ni consolidaciones. Senos costofrenicos libres. Sin lesiones oseas.||||||F|||20250310140000
OBX|2|CWE|59776-5^Conclusion del procedimiento^LN||NORMAL^Estudio sin alteraciones^LOCAL||||||F|||20250310140000
```

---

## 4. ORU^R01 - CT abdomen report with PDF

```
MSH|^~\&|ISSSTE_CIS|HRLALM_CDMX|HIS_RCV|HRLALM|20250312171500||ORU^R01^ORU_R01|ISSSTE20250312171500004|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE7540108245^^^ISSSTE^SS~CURP:CALA800630MDFZLN03^^^CURP^NI||Castillo^Lozano^Andrea^Mariana||19800630|F|||Av Reforma 2654 Col Condesa^^Ciudad De Mexico^DIF^06140^MX||5575374230^^^andrea.castillo@correo.mx||SPA|M|CAT|||CALA800630MDFZLN03||||Ciudad de Mexico|MX
PV1|1|I|CIR^205^A^HRLALM||||26524^Espinoza^Talavera^Ricardo^^^DR|||CIR
ORC|RE|RAD20250312002||||||^^^20250312130000^^R||20250312171500|AOLIVERA^Pineda^Aguilar^Salvador^^^DR
OBR|1|RAD20250312002||74178^TC abdomen y pelvis con contraste^LOCAL|||20250312130000||||N|||||26524^Espinoza^Talavera^Ricardo^^^DR||||||RAD
OBX|1|FT|74178^TC abdomen y pelvis^LOCAL||Higado de tamano y morfologia normal. Vesicula biliar con lito unico de 12mm. Via biliar no dilatada. Pancreas sin alteraciones. Rinones de tamano normal sin ectasia. No liquido libre.||||||F|||20250312170000
OBX|2|CWE|59776-5^Conclusion^LN||K80.2^Litiasis vesicular sin colecistitis^I10||||||F|||20250312170000
OBX|3|ED|PDF^Reporte tomografia abdominal^AUSPDI|1|ISSSTE_CIS^AP^^Base64^JVBERi0xLjUKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKFJlcG9ydGUgZGUgVG9tb2dyYWZpYSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAyMDYgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozMDAKJSVFT0YK||||||F|||20250312171000
```

---

## 5. ORM^O01 - MRI brain with gadolinium

```
MSH|^~\&|ISSSTE_CIS|HRCMN_MTY|RIS_SYS|HRCMN|20250315082000||ORM^O01^ORM_O01|ISSSTE20250315082000005|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE7511976537^^^ISSSTE^SS~CURP:GOVP680520HPLRRD28^^^CURP^NI||Gonzalez^Villanueva^Pablo^Enrique||19680520|M|||Av Juarez 2405 Col Del Valle^^Puebla^PUE^72530^MX||2224661005^^^pablo.gonzalez@outlook.com||SPA|M|CAT|||GOVP680520HPLRRD28||||Monterrey|MX
PV1|1|O|NEURO^04^A^HRCMN||||32521^Olvera^Renteria^Daniela^^^DRA|||NEURO||||REF
ORC|NW|RAD20250315003|||||^^^20250315110000^^R||20250315082000|LPAMANES^Camacho^Bravo^Claudia^^^DRA|||||HRCMN
OBR|1|RAD20250315003||70553^RM cerebro con gadolinio^LOCAL|||20250315082000||||N|||||32521^Olvera^Renteria^Daniela^^^DRA||||||RAD|||^^^20250315110000^^R||||BRAIN
DG1|1|I10|G43.9^Migrana no especificada^I10|||A
```

---

## 6. ORU^R01 - MRI brain report

```
MSH|^~\&|ISSSTE_CIS|HRCMN_MTY|HIS_RCV|HRCMN|20250315160000||ORU^R01^ORU_R01|ISSSTE20250315160000006|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE7511976537^^^ISSSTE^SS~CURP:GOVP680520HPLRRD28^^^CURP^NI||Gonzalez^Villanueva^Pablo^Enrique||19680520|M|||Av Juarez 2405 Col Del Valle^^Puebla^PUE^72530^MX||2224661005^^^pablo.gonzalez@outlook.com||SPA|M|CAT|||GOVP680520HPLRRD28||||Monterrey|MX
PV1|1|O|RAD^02^A^HRCMN||||32521^Olvera^Renteria^Daniela^^^DRA|||RAD
ORC|RE|RAD20250315003||||||^^^20250315110000^^R||20250315160000|LPAMANES^Camacho^Bravo^Claudia^^^DRA
OBR|1|RAD20250315003||70553^RM cerebro con gadolinio^LOCAL|||20250315110000||||N|||||32521^Olvera^Renteria^Daniela^^^DRA||||||RAD
OBX|1|FT|70553^RM cerebro con gadolinio^LOCAL||Parenquima cerebral de intensidad de senal normal. Sistema ventricular de tamano y morfologia normal. No se observan lesiones ocupantes de espacio. No realce patologico tras la administracion de gadolinio. Estructuras de fosa posterior sin alteraciones.||||||F|||20250315153000
OBX|2|CWE|59776-5^Conclusion^LN||NORMAL^Resonancia magnetica cerebral sin alteraciones^LOCAL||||||F|||20250315153000
```

---

## 7. ORM^O01 - Mammography screening

```
MSH|^~\&|ISSSTE_CIS|HRLALM_CDMX|RIS_SYS|HRLALM|20250318093000||ORM^O01^ORM_O01|ISSSTE20250318093000007|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE1863563338^^^ISSSTE^SS~CURP:HEMR650812MJCRLS53^^^CURP^NI||Herrera^Montalvo^Rosario^Ines||19650812|F|||Blvd Lopez Mateos 1563 Col Americana^^Guadalajara^JAL^44160^MX||3375237402^^^rosario.herrera@correo.mx||SPA|M|CAT|||HEMR650812MJCRLS53||||Ciudad de Mexico|MX
PV1|1|O|MAM^01^A^HRLALM||||47238^Rivas^Cardenas^Leticia^^^DRA|||RAD||||REF
ORC|NW|RAD20250318004|||||^^^20250318103000^^R||20250318093000|ACARRASCO^Fuentes^Nava^Yolanda^^^DRA|||||HRLALM
OBR|1|RAD20250318004||77067^Mastografia bilateral de deteccion^LOCAL|||20250318093000||||N|||||47238^Rivas^Cardenas^Leticia^^^DRA||||||RAD|||^^^20250318103000^^R||||BREAST
DG1|1|I10|Z12.3^Deteccion de neoplasia maligna de mama^I10|||A
```

---

## 8. ORU^R01 - Mammography report with image

```
MSH|^~\&|ISSSTE_CIS|HRLALM_CDMX|HIS_RCV|HRLALM|20250318153000||ORU^R01^ORU_R01|ISSSTE20250318153000008|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE1863563338^^^ISSSTE^SS~CURP:HEMR650812MJCRLS53^^^CURP^NI||Herrera^Montalvo^Rosario^Ines||19650812|F|||Blvd Lopez Mateos 1563 Col Americana^^Guadalajara^JAL^44160^MX||3375237402^^^rosario.herrera@correo.mx||SPA|M|CAT|||HEMR650812MJCRLS53||||Ciudad de Mexico|MX
PV1|1|O|RAD^01^A^HRLALM||||47238^Rivas^Cardenas^Leticia^^^DRA|||RAD
ORC|RE|RAD20250318004||||||^^^20250318103000^^R||20250318153000|ACARRASCO^Fuentes^Nava^Yolanda^^^DRA
OBR|1|RAD20250318004||77067^Mastografia bilateral de deteccion^LOCAL|||20250318103000||||N|||||47238^Rivas^Cardenas^Leticia^^^DRA||||||RAD
OBX|1|FT|77067^Mastografia bilateral^LOCAL||Mamas de densidad heterogenea (ACR-C). No se observan masas, distorsiones arquitecturales ni microcalcificaciones sospechosas. Ganglios axilares de aspecto normal. BIRADS 1 - Negativo.||||||F|||20250318150000
OBX|2|CWE|36625-2^BIRADS Assessment^LN||1^Negativo^BIRADS||||||F|||20250318150000
OBX|3|ED|IMG^Imagen mastografia MLO derecha^LOCAL|1|ISSSTE_CIS^IMAGE^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DQ4SEA8OEQ4LCxAWEBETFBUVFQwPFxgWFBgSFBT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wgARCABAAEADASIA AhEBAxEB/8QAGwAAAgMBAQEAAAAAAAAAAAAABAUCAwYBBwj/xAAYAQADAQEAAAAAAAAAAAAAAAABAgMABP/aAAwDAQACEAMQAAAB||||||F|||20250318150000
```

---

## 9. ORM^O01 - Ultrasound abdomen order

```
MSH|^~\&|ISSSTE_CIS|HR_CDMX_20NOV|RIS_SYS|HR20NOV|20250320101500||ORM^O01^ORM_O01|ISSSTE20250320101500009|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE1626256021^^^ISSSTE^SS~CURP:MUGR750318HDFNNL95^^^CURP^NI||Munoz^Galvan^Ricardo^Emilio||19750318|M|||Calle Puebla 970 Col Escandon^^Ciudad De Mexico^DIF^03100^MX||5536087567^^^ricardo.munoz@live.com.mx||SPA|D|CAT|||MUGR750318HDFNNL95||||Ciudad de Mexico|MX
PV1|1|O|RAD^03^A^HR20NOV||||95360^Alcantara^Dominguez^Manuel^^^DR|||RAD||||REF
ORC|NW|RAD20250320005|||||^^^20250320130000^^R||20250320101500|JMIRELES^Trujillo^Paredes^Gabriel^^^DR|||||HR20NOV
OBR|1|RAD20250320005||76700^Ultrasonido abdominal completo^LOCAL|||20250320101500||||N|||||95360^Alcantara^Dominguez^Manuel^^^DR||||||RAD|||^^^20250320130000^^R||||ABDOMEN
DG1|1|I10|R10.1^Dolor epigastrico^I10|||W
```

---

## 10. ORU^R01 - Ultrasound abdomen report

```
MSH|^~\&|ISSSTE_CIS|HR_CDMX_20NOV|HIS_RCV|HR20NOV|20250320152000||ORU^R01^ORU_R01|ISSSTE20250320152000010|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE1626256021^^^ISSSTE^SS~CURP:MUGR750318HDFNNL95^^^CURP^NI||Munoz^Galvan^Ricardo^Emilio||19750318|M|||Calle Puebla 970 Col Escandon^^Ciudad De Mexico^DIF^03100^MX||5536087567^^^ricardo.munoz@live.com.mx||SPA|D|CAT|||MUGR750318HDFNNL95||||Ciudad de Mexico|MX
PV1|1|O|RAD^03^A^HR20NOV||||95360^Alcantara^Dominguez^Manuel^^^DR|||RAD
ORC|RE|RAD20250320005||||||^^^20250320130000^^R||20250320152000|JMIRELES^Trujillo^Paredes^Gabriel^^^DR
OBR|1|RAD20250320005||76700^Ultrasonido abdominal completo^LOCAL|||20250320130000||||N|||||95360^Alcantara^Dominguez^Manuel^^^DR||||||RAD
OBX|1|FT|76700^Ultrasonido abdominal^LOCAL||Higado homogeneo sin lesiones focales. Vesicula biliar de paredes delgadas sin litos. Via biliar no dilatada. Pancreas visualizado parcialmente sin alteraciones. Bazo homogeneo de tamano normal. Rinones de tamano normal sin ectasia ni litos.||||||F|||20250320150000
OBX|2|CWE|59776-5^Conclusion^LN||NORMAL^Ultrasonido abdominal normal^LOCAL||||||F|||20250320150000
```

---

## 11. ORM^O01 - Lumbar spine X-ray

```
MSH|^~\&|ISSSTE_CIS|HRCMN_MTY|RIS_SYS|HRCMN|20250322090000||ORM^O01^ORM_O01|ISSSTE20250322090000011|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE0920488979^^^ISSSTE^SS~CURP:NAVJ580612HCHRRS21^^^CURP^NI||Navarro^Velazquez^Jorge^Alberto||19580612|M|||Av Ocampo 1702 Col Centro^^Ciudad Juarez^CHH^32000^MX||6567118826^^^jorge.navarro@icloud.com||SPA|M|CAT|||NAVJ580612HCHRRS21||||Monterrey|MX
PV1|1|O|RAD^01^A^HRCMN||||56957^Sandoval^Cabrera^Guillermo^^^DR|||RAD||||REF
ORC|NW|RAD20250322006|||||^^^20250322100000^^R||20250322090000|MESPARZA^Trevino^Luevano^Jorge^^^DR|||||HRCMN
OBR|1|RAD20250322006||72100^Radiografia columna lumbar AP y lateral^LOCAL|||20250322090000||||N|||||56957^Sandoval^Cabrera^Guillermo^^^DR||||||RAD|||^^^20250322100000^^R||||SPINE
DG1|1|I10|M54.5^Lumbago no especificado^I10|||A
```

---

## 12. ORU^R01 - Lumbar spine report

```
MSH|^~\&|ISSSTE_CIS|HRCMN_MTY|HIS_RCV|HRCMN|20250322141000||ORU^R01^ORU_R01|ISSSTE20250322141000012|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE0920488979^^^ISSSTE^SS~CURP:NAVJ580612HCHRRS21^^^CURP^NI||Navarro^Velazquez^Jorge^Alberto||19580612|M|||Av Ocampo 1702 Col Centro^^Ciudad Juarez^CHH^32000^MX||6567118826^^^jorge.navarro@icloud.com||SPA|M|CAT|||NAVJ580612HCHRRS21||||Monterrey|MX
PV1|1|O|RAD^01^A^HRCMN||||56957^Sandoval^Cabrera^Guillermo^^^DR|||RAD
ORC|RE|RAD20250322006||||||^^^20250322100000^^R||20250322141000|MESPARZA^Trevino^Luevano^Jorge^^^DR
OBR|1|RAD20250322006||72100^Radiografia columna lumbar AP y lateral^LOCAL|||20250322100000||||N|||||56957^Sandoval^Cabrera^Guillermo^^^DR||||||RAD
OBX|1|FT|72100^Radiografia columna lumbar^LOCAL||Disminucion del espacio intervertebral L4-L5 y L5-S1. Osteofitos marginales anteriores en L3 a L5. Esclerosis de las carillas articulares. Lordosis lumbar conservada. Sin listesis.||||||F|||20250322140000
OBX|2|CWE|59776-5^Conclusion^LN||M47.8^Espondilosis lumbar con cambios degenerativos^I10||||||F|||20250322140000
```

---

## 13. ORM^O01 - Doppler ultrasound lower extremities

```
MSH|^~\&|ISSSTE_CIS|HRLALM_CDMX|RIS_SYS|HRLALM|20250325111500||ORM^O01^ORM_O01|ISSSTE20250325111500013|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE0727584656^^^ISSSTE^SS~CURP:MELA690225MYNCNL34^^^CURP^NI||Mendoza^Luna^Adriana^Beatriz||19690225|F|||Calle 50 Norte 1945 Col Garcia Gineres^^Merida^YUC^97070^MX||9996411427^^^adriana.mendoza@correo.mx||SPA|V|CAT|||MELA690225MYNCNL34||||Ciudad de Mexico|MX
PV1|1|O|RAD^02^A^HRLALM||||48645^Cervantes^Ponce^Carlos^^^DR|||RAD||||REF
ORC|NW|RAD20250325007|||||^^^20250325140000^^R||20250325111500|FSOLORZANO^Orozco^Bautista^Andres^^^DR|||||HRLALM
OBR|1|RAD20250325007||93970^Doppler venoso de miembros inferiores bilateral^LOCAL|||20250325111500||||N|||||48645^Cervantes^Ponce^Carlos^^^DR||||||RAD|||^^^20250325140000^^R||||LEGS
DG1|1|I10|I83.9^Varices de miembros inferiores sin ulcera^I10|||A
```

---

## 14. ORU^R01 - Doppler lower extremities report with PDF

```
MSH|^~\&|ISSSTE_CIS|HRLALM_CDMX|HIS_RCV|HRLALM|20250325163000||ORU^R01^ORU_R01|ISSSTE20250325163000014|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE0727584656^^^ISSSTE^SS~CURP:MELA690225MYNCNL34^^^CURP^NI||Mendoza^Luna^Adriana^Beatriz||19690225|F|||Calle 50 Norte 1945 Col Garcia Gineres^^Merida^YUC^97070^MX||9996411427^^^adriana.mendoza@correo.mx||SPA|V|CAT|||MELA690225MYNCNL34||||Ciudad de Mexico|MX
PV1|1|O|RAD^02^A^HRLALM||||48645^Cervantes^Ponce^Carlos^^^DR|||RAD
ORC|RE|RAD20250325007||||||^^^20250325140000^^R||20250325163000|FSOLORZANO^Orozco^Bautista^Andres^^^DR
OBR|1|RAD20250325007||93970^Doppler venoso de miembros inferiores bilateral^LOCAL|||20250325140000||||N|||||48645^Cervantes^Ponce^Carlos^^^DR||||||RAD
OBX|1|FT|93970^Doppler venoso miembros inferiores^LOCAL||Venas femorales comunes, superficiales y popliteas permeables bilateralmente con flujo espontaneo y fasico. No se observa trombosis venosa profunda. Insuficiencia de vena safena mayor derecha con reflujo de 3.2 segundos.||||||F|||20250325160000
OBX|2|CWE|59776-5^Conclusion^LN||I87.1^Insuficiencia venosa cronica de miembro inferior derecho^I10||||||F|||20250325160000
OBX|3|ED|PDF^Reporte Doppler venoso miembros inferiores^AUSPDI|1|ISSSTE_CIS^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA4NiA+PgpzdHJlYW0KQlQgL0YxIDEwIFRmIDUwIDczMCBUZCAoUmVwb3J0ZSBEb3BwbGVyIFZlbm9zbyBkZSBNaWVtYnJvcyBJbmZlcmlvcmVzKSBUaiBFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iago=||||||F|||20250325162000
```

---

## 15. ORM^O01 - Pelvic ultrasound for gynecology

```
MSH|^~\&|ISSSTE_CIS|HR_CDMX_20NOV|RIS_SYS|HR20NOV|20250328084500||ORM^O01^ORM_O01|ISSSTE20250328084500015|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE4954944343^^^ISSSTE^SS~CURP:RUVS810930MNLRZF92^^^CURP^NI||Rubio^Valdes^Sandra^Luciana||19810930|F|||Av Constitucion 3173 Col Mitras Centro^^Monterrey^NLE^64000^MX||8153857984^^^sandra.rubio@icloud.com||SPA|M|CAT|||RUVS810930MNLRZF92||||Ciudad de Mexico|MX
PV1|1|O|GIN^01^A^HR20NOV||||89267^Quintero^Salinas^Fernanda^^^DRA|||GIN||||REF
ORC|NW|RAD20250328008|||||^^^20250328100000^^R||20250328084500|GROBLEDO^Estrada^Coronado^Veronica^^^DRA|||||HR20NOV
OBR|1|RAD20250328008||76856^Ultrasonido pelvico transabdominal^LOCAL|||20250328084500||||N|||||89267^Quintero^Salinas^Fernanda^^^DRA||||||RAD|||^^^20250328100000^^R||||PELVIS
DG1|1|I10|N92.0^Menstruacion excesiva y frecuente^I10|||A
```

---

## 16. ORU^R01 - Pelvic ultrasound report

```
MSH|^~\&|ISSSTE_CIS|HR_CDMX_20NOV|HIS_RCV|HR20NOV|20250328142000||ORU^R01^ORU_R01|ISSSTE20250328142000016|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE4954944343^^^ISSSTE^SS~CURP:RUVS810930MNLRZF92^^^CURP^NI||Rubio^Valdes^Sandra^Luciana||19810930|F|||Av Constitucion 3173 Col Mitras Centro^^Monterrey^NLE^64000^MX||8153857984^^^sandra.rubio@icloud.com||SPA|M|CAT|||RUVS810930MNLRZF92||||Ciudad de Mexico|MX
PV1|1|O|RAD^03^A^HR20NOV||||89267^Quintero^Salinas^Fernanda^^^DRA|||RAD
ORC|RE|RAD20250328008||||||^^^20250328100000^^R||20250328142000|GROBLEDO^Estrada^Coronado^Veronica^^^DRA
OBR|1|RAD20250328008||76856^Ultrasonido pelvico transabdominal^LOCAL|||20250328100000||||N|||||89267^Quintero^Salinas^Fernanda^^^DRA||||||RAD
OBX|1|FT|76856^Ultrasonido pelvico^LOCAL||Utero en anteversion de 95x52x48mm con mioma intramural en pared posterior de 32x28mm. Endometrio de 8mm, homogeneo. Ovario derecho de 28x18mm con foliculos. Ovario izquierdo de 30x20mm sin alteraciones. Fondo de saco libre.||||||F|||20250328140000
OBX|2|CWE|59776-5^Conclusion^LN||D25.1^Leiomioma intramural del utero^I10||||||F|||20250328140000
```

---

## 17. ORM^O01 - Bone densitometry order

```
MSH|^~\&|ISSSTE_CIS|HRLALM_CDMX|RIS_SYS|HRLALM|20250401080000||ORM^O01^ORM_O01|ISSSTE20250401080000017|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE8175836074^^^ISSSTE^SS~CURP:GAMA550115MDFGVD43^^^CURP^NI||Garcia^Macias^Aurora^Francisca||19550115|F|||Calle Xola 2395 Col Narvarte^^Ciudad De Mexico^DIF^03020^MX||5528342600^^^aurora.garcia@prodigy.net.mx||SPA|V|CAT|||GAMA550115MDFGVD43||||Ciudad de Mexico|MX
PV1|1|O|RAD^04^A^HRLALM||||56533^Delgadillo^Ochoa^Laura^^^DRA|||RAD||||REF
ORC|NW|RAD20250401009|||||^^^20250401100000^^R||20250401080000|ADELARBRE^Plascencia^Rocha^Catalina^^^DRA|||||HRLALM
OBR|1|RAD20250401009||77080^Densitometria osea central^LOCAL|||20250401080000||||N|||||56533^Delgadillo^Ochoa^Laura^^^DRA||||||RAD|||^^^20250401100000^^R||||BONE
DG1|1|I10|M81.0^Osteoporosis posmenopausica^I10|||A
```

---

## 18. ORU^R01 - Bone densitometry report

```
MSH|^~\&|ISSSTE_CIS|HRLALM_CDMX|HIS_RCV|HRLALM|20250401143000||ORU^R01^ORU_R01|ISSSTE20250401143000018|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE8175836074^^^ISSSTE^SS~CURP:GAMA550115MDFGVD43^^^CURP^NI||Garcia^Macias^Aurora^Francisca||19550115|F|||Calle Xola 2395 Col Narvarte^^Ciudad De Mexico^DIF^03020^MX||5528342600^^^aurora.garcia@prodigy.net.mx||SPA|V|CAT|||GAMA550115MDFGVD43||||Ciudad de Mexico|MX
PV1|1|O|RAD^04^A^HRLALM||||56533^Delgadillo^Ochoa^Laura^^^DRA|||RAD
ORC|RE|RAD20250401009||||||^^^20250401100000^^R||20250401143000|ADELARBRE^Plascencia^Rocha^Catalina^^^DRA
OBR|1|RAD20250401009||77080^Densitometria osea central^LOCAL|||20250401100000||||N|||||56533^Delgadillo^Ochoa^Laura^^^DRA||||||RAD
OBX|1|NM|46278-8^T-score columna lumbar^LN||-2.8|SD|>-1.0|LL|||F|||20250401140000
OBX|2|NM|46279-6^T-score cuello femoral^LN||-2.3|SD|>-1.0|LL|||F|||20250401140000
OBX|3|FT|77080^Densitometria osea^LOCAL||Columna lumbar L1-L4: DMO 0.782 g/cm2, T-score -2.8. Cuello femoral: DMO 0.654 g/cm2, T-score -2.3. Compatible con osteoporosis en columna lumbar y osteopenia en cuello femoral segun criterios de la OMS.||||||F|||20250401140000
```

---

## 19. ORM^O01 - Echocardiogram order

```
MSH|^~\&|ISSSTE_CIS|HRCMN_MTY|RIS_SYS|HRCMN|20250403091200||ORM^O01^ORM_O01|ISSSTE20250403091200019|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE2040697591^^^ISSSTE^SS~CURP:AGTF700820HMCPLR25^^^CURP^NI||Aguilar^Tovar^Francisco^Eduardo||19700820|M|||Av Venustiano Carranza 3238 Col Cumbres^^Monterrey^NLE^64610^MX||8123518323^^^francisco.aguilar@prodigy.net.mx||SPA|M|CAT|||AGTF700820HMCPLR25||||Monterrey|MX
PV1|1|O|CARD^02^A^HRCMN||||41842^Balderas^Ontiveros^Jesus^^^DR|||CARD||||REF
ORC|NW|RAD20250403010|||||^^^20250403110000^^R||20250403091200|OVILLAVERDE^Cisneros^Magana^Rafael^^^DR|||||HRCMN
OBR|1|RAD20250403010||93306^Ecocardiograma transtorácico^LOCAL|||20250403091200||||N|||||41842^Balderas^Ontiveros^Jesus^^^DR||||||CARD|||^^^20250403110000^^R||||HEART
DG1|1|I10|I50.9^Insuficiencia cardiaca no especificada^I10|||A
```

---

## 20. ORU^R01 - Echocardiogram report with image

```
MSH|^~\&|ISSSTE_CIS|HRCMN_MTY|HIS_RCV|HRCMN|20250403160000||ORU^R01^ORU_R01|ISSSTE20250403160000020|P|2.5|||AL|NE||8859/1
PID|1||ISSSTE2040697591^^^ISSSTE^SS~CURP:AGTF700820HMCPLR25^^^CURP^NI||Aguilar^Tovar^Francisco^Eduardo||19700820|M|||Av Venustiano Carranza 3238 Col Cumbres^^Monterrey^NLE^64610^MX||8123518323^^^francisco.aguilar@prodigy.net.mx||SPA|M|CAT|||AGTF700820HMCPLR25||||Monterrey|MX
PV1|1|O|CARD^02^A^HRCMN||||41842^Balderas^Ontiveros^Jesus^^^DR|||CARD
ORC|RE|RAD20250403010||||||^^^20250403110000^^R||20250403160000|OVILLAVERDE^Cisneros^Magana^Rafael^^^DR
OBR|1|RAD20250403010||93306^Ecocardiograma transtorácico^LOCAL|||20250403110000||||N|||||41842^Balderas^Ontiveros^Jesus^^^DR||||||CARD
OBX|1|NM|10230-1^Fraccion de eyeccion del ventriculo izquierdo^LN||45|%|55-70|L|||F|||20250403153000
OBX|2|NM|29468-6^Diametro diastolico del ventriculo izquierdo^LN||58|mm|35-56|H|||F|||20250403153000
OBX|3|FT|93306^Ecocardiograma transtorácico^LOCAL||Ventriculo izquierdo dilatado con hipocinesia difusa. FEVI 45% por Simpson biplano. Valvulas sin alteraciones significativas. Insuficiencia mitral leve funcional. Presion sistolica de arteria pulmonar estimada en 35 mmHg.||||||F|||20250403153000
OBX|4|ED|IMG^Ecocardiograma vista apical 4 camaras^LOCAL|1|ISSSTE_CIS^IMAGE^JPEG^Base64^/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAyADIDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAgQF||||||F|||20250403155000
```
