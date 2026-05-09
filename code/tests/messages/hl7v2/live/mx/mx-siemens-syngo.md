# Siemens syngo.plaza PACS - real HL7v2 ER7 messages

---

## 1. ORM^O01 - Orden de radiografia de torax PA y lateral

```
MSH|^~\&|SYNGO|PACS_IMSS_CMN_SXXI|RIS_IMSS|IMSS_CDMX|20250501083000||ORM^O01^ORM_O01|SYNGO-20250501-000101|P|2.5|||AL|NE||8859/1|||MEX_NOM024^NOM-024-SSA3^L
PID|1||IMSS-83887655^^^IMSS^MR||PAREDES^ESTRADA^JORGE^MANUEL||19630415|M|||CALLE DURANGO 1808 COL ROMA NORTE^^CIUDAD DE MEXICO^DF^06700^MX||5539127461^^^jorge.paredes@hotmail.com||ESP|C|CAT||||PAEJ630415HDFRRR51|||||N
PV1|1|I|NEUMO-03^301^A^IMSS-CMN-SXXI^^BED|U|||14276^OLMEDO^TRUJILLO^ALICIA^DRA.^^MD|14276^OLMEDO^TRUJILLO^ALICIA^DRA.^^MD||MED||||1|||14276^OLMEDO^TRUJILLO^ALICIA^DRA.^^MD|IP|VIS-20250430-001|||||||||||||||||||IMSS||||20250430200000
ORC|NW|ORD-20250501-0101^SYNGO|FIL-20250501-0101^RIS_IMSS||SC|||1^^^20250501083000^^R||20250501083000|USR-RAD-123^Granados^Pineda^Alejandro^^TEC.RAD.||14276^OLMEDO^TRUJILLO^ALICIA^DRA.^^MD|PNEUMO-03|55 4102 7394|20250501083000||IMSS-CMN-SXXI^IMSS CMN Siglo XXI^L|AV CUAUHTEMOC 330 COL DOCTORES^^CIUDAD DE MEXICO^DF^06720^MX
OBR|1|ORD-20250501-0101^SYNGO|FIL-20250501-0101^RIS_IMSS|71020^Radiografia de torax PA y lateral^LN|||20250501082500||||R||Dx: Neumonia adquirida en comunidad J18.9||||14276^OLMEDO^TRUJILLO^ALICIA^DRA.^^MD||||||20250501083000|||F
```

---

## 2. ORU^R01 - Reporte de radiografia de torax con imagen JPEG

```
MSH|^~\&|SYNGO|PACS_IMSS_CMN_SXXI|HIS_IMSS|IMSS_CDMX|20250501113000||ORU^R01^ORU_R01|SYNGO-20250501-000201|P|2.5|||AL|NE||8859/1|||MEX_NOM024^NOM-024-SSA3^L
PID|1||IMSS-83887655^^^IMSS^MR||PAREDES^ESTRADA^JORGE^MANUEL||19630415|M|||CALLE DURANGO 1808 COL ROMA NORTE^^CIUDAD DE MEXICO^DF^06700^MX||5539127461^^^jorge.paredes@hotmail.com||ESP|C|CAT||||PAEJ630415HDFRRR51|||||N
PV1|1|I|PNEUMO-03^301^A^IMSS-CMN-SXXI^^BED|U|||14276^OLMEDO^TRUJILLO^ALICIA^DRA.^^MD|14276^OLMEDO^TRUJILLO^ALICIA^DRA.^^MD||MED||||1|||14276^OLMEDO^TRUJILLO^ALICIA^DRA.^^MD|IP|VIS-20250430-001|||||||||||||||||||IMSS||||20250430200000
ORC|RE|ORD-20250501-0101^SYNGO|FIL-20250501-0101^RIS_IMSS||CM|||1^^^20250501113000^^R||20250501113000|USR-RAD-219^Landa^Figueroa^Lorena^^MED.RAD.||14276^OLMEDO^TRUJILLO^ALICIA^DRA.^^MD|PNEUMO-03|55 4102 7394|20250501113000||IMSS-CMN-SXXI^IMSS CMN Siglo XXI^L|AV CUAUHTEMOC 330 COL DOCTORES^^CIUDAD DE MEXICO^DF^06720^MX
OBR|1|ORD-20250501-0101^SYNGO|FIL-20250501-0101^RIS_IMSS|71020^Radiografia de torax PA y lateral^LN|||20250501082500||||A|||||14276^OLMEDO^TRUJILLO^ALICIA^DRA.^^MD||||||20250501113000|||F
OBX|1|FT|71020^Hallazgo radiologico^LN|1|Infiltrado alveolar en lobulo inferior derecho con broncograma aereo. Silueta cardiaca normal. Seno costofrenio izquierdo libre, derecho con borramiento parcial. Mediastino centrado sin ensanchamiento. Impresion: Neumonia lobar derecha.||||||F|||20250501110000||USR-RAD-219^Landa^Figueroa^Lorena^^MED.RAD.
OBX|2|ED|IMG^Radiografia torax PA^LOCAL|1|SYNGO^IMAGE^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/4gxYSUNDX1BST0ZJTEUAAQEAAAxITGlubwIQAABtbnRyUkdCIFhZWiAHzgACAAkABgAxAABhY3NwTVNGVAAAAABJRUMgc1JHQgAAAAAAAAAAAAAAAAAA9tYAAQAAAADTLUhQICAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA||||||F
OBX|3|ST|59776-5^Impresion diagnostica^LN|1|Neumonia lobar derecha en fase de consolidacion||||||F|||20250501110000||USR-RAD-219^Landa^Figueroa^Lorena^^MED.RAD.
```

---

## 3. ORM^O01 - Orden de tomografia de craneo simple

```
MSH|^~\&|SYNGO|PACS_ANGELES_PEDREGAL|RIS_ANGELES|ANGELES_CDMX|20250502021500||ORM^O01^ORM_O01|SYNGO-20250502-000301|P|2.5|||AL|NE||8859/1
PID|1||ANG-PED-54994792^^^ANGELES^MR||Villalobos^Cardenas^Adriana^Fernanda||19780612|F|||AV PATRIOTISMO 507 COL NARVARTE PONIENTE^^CIUDAD DE MEXICO^DF^03020^MX||5578320149^^^adriana.villalobos@correo.mx||ESP|M|CAT||||VICA780612MDFLLR19|||||N
PV1|1|E|UR-01^^^^ER|||24511^Sandoval^Becerra^Jose^DR.^^MD|24511^Sandoval^Becerra^Jose^DR.^^MD||ER||||1|||24511^Sandoval^Becerra^Jose^DR.^^MD|ER|VIS-20250502-003|||||||||||||||||||ANGELES||||20250502010000
ORC|NW|ORD-20250502-0301^SYNGO|FIL-20250502-0301^RIS_ANGELES||SC|||1^^^20250502021500^^S||20250502021500|USR-RAD-167^Ponce^Navarro^Carlos^^TEC.RAD.||24511^Sandoval^Becerra^Jose^DR.^^MD|UR-01|55 3291 4058|20250502021500||ANG-PED^Hospital Angeles del Pedregal^L|CAMINO A SANTA TERESA 1055 COL HEROES DE PADIERNA^^CIUDAD DE MEXICO^DF^10700^MX
OBR|1|ORD-20250502-0301^SYNGO|FIL-20250502-0301^RIS_ANGELES|70450^Tomografia computarizada de craneo simple^LN|||20250502014500||||S||Dx: Cefalea subita intensa con nausea R51||||24511^Sandoval^Becerra^Jose^DR.^^MD||||||20250502021500|||F
```

---

## 4. ORU^R01 - Reporte de tomografia de craneo

```
MSH|^~\&|SYNGO|PACS_ANGELES_PEDREGAL|HIS_ANGELES|ANGELES_CDMX|20250502043000||ORU^R01^ORU_R01|SYNGO-20250502-000401|P|2.5|||AL|NE||8859/1
PID|1||ANG-PED-54994792^^^ANGELES^MR||Villalobos^Cardenas^Adriana^Fernanda||19780612|F|||AV PATRIOTISMO 507 COL NARVARTE PONIENTE^^CIUDAD DE MEXICO^DF^03020^MX||5578320149^^^adriana.villalobos@correo.mx||ESP|M|CAT||||VICA780612MDFLLR19|||||N
PV1|1|E|UR-01^^^^ER|||24511^Sandoval^Becerra^Jose^DR.^^MD|24511^Sandoval^Becerra^Jose^DR.^^MD||ER||||1|||24511^Sandoval^Becerra^Jose^DR.^^MD|ER|VIS-20250502-003|||||||||||||||||||ANGELES||||20250502010000
ORC|RE|ORD-20250502-0301^SYNGO|FIL-20250502-0301^RIS_ANGELES||CM|||1^^^20250502043000^^R||20250502043000|USR-RAD-085^Fuentes^Ramos^Lucia^^MED.RAD.||24511^Sandoval^Becerra^Jose^DR.^^MD|UR-01|55 3291 4058|20250502043000||ANG-PED^Hospital Angeles del Pedregal^L|CAMINO A SANTA TERESA 1055 COL HEROES DE PADIERNA^^CIUDAD DE MEXICO^DF^10700^MX
OBR|1|ORD-20250502-0301^SYNGO|FIL-20250502-0301^RIS_ANGELES|70450^Tomografia computarizada de craneo simple^LN|||20250502014500||||A|||||24511^Sandoval^Becerra^Jose^DR.^^MD||||||20250502043000|||F
OBX|1|FT|70450^Hallazgo tomografico^LN|1|TC de craneo simple sin evidencia de hemorragia intracraneana. Sistema ventricular de tamano y morfologia normal. No se observan lesiones ocupantes de espacio. Estructuras de linea media centradas. Fosa posterior sin alteraciones. Base de craneo sin hallazgos patologicos. Conclusion: Estudio tomografico de craneo sin alteraciones agudas.||||||F|||20250502040000||USR-RAD-085^Fuentes^Ramos^Lucia^^MED.RAD.
OBX|2|ST|59776-5^Impresion diagnostica^LN|1|Tomografia de craneo normal, sin evidencia de patologia aguda||||||F|||20250502040000||USR-RAD-085^Fuentes^Ramos^Lucia^^MED.RAD.
```

---

## 5. ORM^O01 - Orden de resonancia magnetica de rodilla

```
MSH|^~\&|SYNGO|PACS_MEDSUR|RIS_MEDSUR|MEDSUR_CDMX|20250503100000||ORM^O01^ORM_O01|SYNGO-20250503-000501|P|2.5|||AL|NE||8859/1
PID|1||MEDSUR-45696404^^^MEDSUR^MR||Aguayo^Montiel^Daniel^Ernesto||19850923|M|||AV UNIVERSIDAD 438 COL DEL VALLE CENTRO^^CIUDAD DE MEXICO^DF^03100^MX||5541827693^^^daniel.aguayo@gmail.com||ESP|S|CAT||||AUMD850923HDFGNT02|||||N
PV1|1|O|RAD-RM-01^^^^RAD|||53087^Coronado^Ibarra^Claudia^DRA.^^MD|53087^Coronado^Ibarra^Claudia^DRA.^^MD||RAD||||1|||53087^Coronado^Ibarra^Claudia^DRA.^^MD|OP|VIS-20250503-005|||||||||||||||||||MEDSUR||||20250503093000
ORC|NW|ORD-20250503-0501^SYNGO|FIL-20250503-0501^RIS_MEDSUR||SC|||1^^^20250503100000^^R||20250503100000|USR-RAD-589^Monroy^Zavala^Tomas^^TEC.RAD.||53087^Coronado^Ibarra^Claudia^DRA.^^MD|RAD-RM-01|55 4719 8350|20250503100000||MEDSUR^Medica Sur^L|PUENTE DE PIEDRA 150 COL TORIELLO GUERRA^^CIUDAD DE MEXICO^DF^14050^MX
OBR|1|ORD-20250503-0501^SYNGO|FIL-20250503-0501^RIS_MEDSUR|73721^Resonancia magnetica de rodilla sin y con contraste^LN|||20250503095000||||R||Dx: Dolor rodilla derecha con limitacion funcional M25.561||||53087^Coronado^Ibarra^Claudia^DRA.^^MD||||||20250503100000|||F
```

---

## 6. ORU^R01 - Reporte de resonancia magnetica de rodilla con PDF

```
MSH|^~\&|SYNGO|PACS_MEDSUR|HIS_MEDSUR|MEDSUR_CDMX|20250503153000||ORU^R01^ORU_R01|SYNGO-20250503-000601|P|2.5|||AL|NE||8859/1
PID|1||MEDSUR-45696404^^^MEDSUR^MR||Aguayo^Montiel^Daniel^Ernesto||19850923|M|||AV UNIVERSIDAD 438 COL DEL VALLE CENTRO^^CIUDAD DE MEXICO^DF^03100^MX||5541827693^^^daniel.aguayo@gmail.com||ESP|S|CAT||||AUMD850923HDFGNT02|||||N
PV1|1|O|RAD-RM-01^^^^RAD|||53087^Coronado^Ibarra^Claudia^DRA.^^MD|53087^Coronado^Ibarra^Claudia^DRA.^^MD||RAD||||1|||53087^Coronado^Ibarra^Claudia^DRA.^^MD|OP|VIS-20250503-005|||||||||||||||||||MEDSUR||||20250503093000
ORC|RE|ORD-20250503-0501^SYNGO|FIL-20250503-0501^RIS_MEDSUR||CM|||1^^^20250503153000^^R||20250503153000|USR-RAD-834^Arellano^Noriega^Cecilia^^MED.RAD.||53087^Coronado^Ibarra^Claudia^DRA.^^MD|RAD-RM-01|55 4719 8350|20250503153000||MEDSUR^Medica Sur^L|PUENTE DE PIEDRA 150 COL TORIELLO GUERRA^^CIUDAD DE MEXICO^DF^14050^MX
OBR|1|ORD-20250503-0501^SYNGO|FIL-20250503-0501^RIS_MEDSUR|73721^Resonancia magnetica de rodilla sin y con contraste^LN|||20250503095000||||A|||||53087^Coronado^Ibarra^Claudia^DRA.^^MD||||||20250503153000|||F
OBX|1|FT|73721^Hallazgo de resonancia^LN|1|Rotura parcial del menisco medial en su cuerno posterior con patron de senal grado III. Ligamentos cruzados anterior y posterior integros con senal normal. Ligamentos colaterales sin alteraciones. Cartilago articular con adelgazamiento focal en compartimiento medial. Derrame articular leve.||||||F|||20250503150000||USR-RAD-834^Arellano^Noriega^Cecilia^^MED.RAD.
OBX|2|ST|59776-5^Impresion diagnostica^LN|1|Rotura meniscal medial grado III, condromalacia medial incipiente||||||F|||20250503150000||USR-RAD-834^Arellano^Noriega^Cecilia^^MED.RAD.
OBX|3|ED|PDF^Reporte RM rodilla completo^AUSPDI|1|SYNGO^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4=||||||F
```

---

## 7. ORM^O01 - Orden de ultrasonido abdominal

```
MSH|^~\&|SYNGO|PACS_IMSS_HGR_110|RIS_IMSS|IMSS_GDL|20250504091000||ORM^O01^ORM_O01|SYNGO-20250504-000701|P|2.5|||AL|NE||8859/1|||MEX_NOM024^NOM-024-SSA3^L
PID|1||IMSS-43224988^^^IMSS^MR||Herrera^Ventura^Ana^Luciana||19720805|F|||AV AMERICAS 2033 COL PROVIDENCIA^^GUADALAJARA^JAL^44630^MX||3318745632^^^ana.herrera@icloud.com||ESP|M|CAT||||HEVA720805MJLRRN73|||||N
PV1|1|O|RAD-US-02^^^^RAD|||37590^Quiroga^Zepeda^Gabriel^DR.^^MD|37590^Quiroga^Zepeda^Gabriel^DR.^^MD||RAD||||1|||37590^Quiroga^Zepeda^Gabriel^DR.^^MD|OP|VIS-20250504-007|||||||||||||||||||IMSS||||20250504083000
ORC|NW|ORD-20250504-0701^SYNGO|FIL-20250504-0701^RIS_IMSS||SC|||1^^^20250504091000^^R||20250504091000|USR-RAD-720^Cisneros^Palomo^Sergio^^TEC.RAD.||37590^Quiroga^Zepeda^Gabriel^DR.^^MD|RAD-US-02|(333)617-0060|20250504091000||IMSS-HGR-110^IMSS HGR 110 Guadalajara^L|AV ALCALDE 1567 COL SANTA MONICA^^GUADALAJARA^JAL^44340^MX
OBR|1|ORD-20250504-0701^SYNGO|FIL-20250504-0701^RIS_IMSS|76700^Ultrasonido abdominal completo^LN|||20250504090000||||R||Dx: Dolor abdominal difuso R10.9||||37590^Quiroga^Zepeda^Gabriel^DR.^^MD||||||20250504091000|||F
```

---

## 8. ORU^R01 - Reporte de ultrasonido abdominal

```
MSH|^~\&|SYNGO|PACS_IMSS_HGR_110|HIS_IMSS|IMSS_GDL|20250504123000||ORU^R01^ORU_R01|SYNGO-20250504-000801|P|2.5|||AL|NE||8859/1|||MEX_NOM024^NOM-024-SSA3^L
PID|1||IMSS-43224988^^^IMSS^MR||Herrera^Ventura^Ana^Luciana||19720805|F|||AV AMERICAS 2033 COL PROVIDENCIA^^GUADALAJARA^JAL^44630^MX||3318745632^^^ana.herrera@icloud.com||ESP|M|CAT||||HEVA720805MJLRRN73|||||N
PV1|1|O|RAD-US-02^^^^RAD|||37590^Quiroga^Zepeda^Gabriel^DR.^^MD|37590^Quiroga^Zepeda^Gabriel^DR.^^MD||RAD||||1|||37590^Quiroga^Zepeda^Gabriel^DR.^^MD|OP|VIS-20250504-007|||||||||||||||||||IMSS||||20250504083000
ORC|RE|ORD-20250504-0701^SYNGO|FIL-20250504-0701^RIS_IMSS||CM|||1^^^20250504123000^^R||20250504123000|USR-RAD-221^Duarte^Balderas^Norma^^MED.RAD.||37590^Quiroga^Zepeda^Gabriel^DR.^^MD|RAD-US-02|(333)617-0060|20250504123000||IMSS-HGR-110^IMSS HGR 110 Guadalajara^L|AV ALCALDE 1567 COL SANTA MONICA^^GUADALAJARA^JAL^44340^MX
OBR|1|ORD-20250504-0701^SYNGO|FIL-20250504-0701^RIS_IMSS|76700^Ultrasonido abdominal completo^LN|||20250504090000||||A|||||37590^Quiroga^Zepeda^Gabriel^DR.^^MD||||||20250504123000|||F
OBX|1|FT|76700^Hallazgo ultrasonografico^LN|1|Higado de tamano normal con ecogenicidad homogenea sin lesiones focales. Vesicula biliar distendida con calculo unico de 12 mm con sombra acustica posterior. Vias biliares sin dilatacion. Pancreas visualizado parcialmente sin alteraciones. Rinones de tamano y ecogenicidad normal, sin ectasia pielocalicial. Bazo homogeneo de tamano normal. Aorta abdominal de calibre normal.||||||F|||20250504120000||USR-RAD-221^Duarte^Balderas^Norma^^MED.RAD.
OBX|2|ST|59776-5^Impresion diagnostica^LN|1|Colelitiasis unica, resto del estudio sin alteraciones||||||F|||20250504120000||USR-RAD-221^Duarte^Balderas^Norma^^MED.RAD.
```

---

## 9. ORM^O01 - Orden de mamografia bilateral

```
MSH|^~\&|SYNGO|PACS_ABC_OBSERVATORIO|RIS_ABC|ABC_CDMX|20250505084500||ORM^O01^ORM_O01|SYNGO-20250505-000901|P|2.5|||AL|NE||8859/1
PID|1||ABC-OBS-10627778^^^ABC^MR||Talavera^Bravo^Teresa^Ines||19680320|F|||CALLE LEIBNITZ 1315 COL ANZURES^^CIUDAD DE MEXICO^DF^11590^MX||5527849610^^^teresa.talavera@prodigy.net.mx||ESP|C|CAT||||TABT680320MDFLLR75|||||N
PV1|1|O|RAD-MAM-01^^^^RAD|||49938^Cuellar^Pantoja^Yolanda^DRA.^^MD|49938^Cuellar^Pantoja^Yolanda^DRA.^^MD||RAD||||1|||49938^Cuellar^Pantoja^Yolanda^DRA.^^MD|OP|VIS-20250505-009|||||||||||||||||||ABC||||20250505080000
ORC|NW|ORD-20250505-0901^SYNGO|FIL-20250505-0901^RIS_ABC||SC|||1^^^20250505084500^^R||20250505084500|USR-RAD-090^Orozco^Villegas^Manuel^^TEC.RAD.||49938^Cuellar^Pantoja^Yolanda^DRA.^^MD|RAD-MAM-01|55 2826 4457|20250505084500||ABC-OBS^Hospital ABC Observatorio^L|AV OBSERVATORIO 136 COL AMERICA^^CIUDAD DE MEXICO^DF^11810^MX
OBR|1|ORD-20250505-0901^SYNGO|FIL-20250505-0901^RIS_ABC|77066^Mamografia bilateral de deteccion^LN|||20250505083000||||R||Deteccion anual, sin antecedentes familiares||||49938^Cuellar^Pantoja^Yolanda^DRA.^^MD||||||20250505084500|||F
```

---

## 10. ORU^R01 - Reporte de mamografia con imagen JPEG

```
MSH|^~\&|SYNGO|PACS_ABC_OBSERVATORIO|HIS_ABC|ABC_CDMX|20250505143000||ORU^R01^ORU_R01|SYNGO-20250505-001001|P|2.5|||AL|NE||8859/1
PID|1||ABC-OBS-10627778^^^ABC^MR||Talavera^Bravo^Teresa^Ines||19680320|F|||CALLE LEIBNITZ 1315 COL ANZURES^^CIUDAD DE MEXICO^DF^11590^MX||5527849610^^^teresa.talavera@prodigy.net.mx||ESP|C|CAT||||TABT680320MDFLLR75|||||N
PV1|1|O|RAD-MAM-01^^^^RAD|||49938^Cuellar^Pantoja^Yolanda^DRA.^^MD|49938^Cuellar^Pantoja^Yolanda^DRA.^^MD||RAD||||1|||49938^Cuellar^Pantoja^Yolanda^DRA.^^MD|OP|VIS-20250505-009|||||||||||||||||||ABC||||20250505080000
ORC|RE|ORD-20250505-0901^SYNGO|FIL-20250505-0901^RIS_ABC||CM|||1^^^20250505143000^^R||20250505143000|USR-RAD-594^Barrera^Lozano^Rosa^^MED.RAD.||49938^Cuellar^Pantoja^Yolanda^DRA.^^MD|RAD-MAM-01|55 2826 4457|20250505143000||ABC-OBS^Hospital ABC Observatorio^L|AV OBSERVATORIO 136 COL AMERICA^^CIUDAD DE MEXICO^DF^11810^MX
OBR|1|ORD-20250505-0901^SYNGO|FIL-20250505-0901^RIS_ABC|77066^Mamografia bilateral de deteccion^LN|||20250505083000||||A|||||49938^Cuellar^Pantoja^Yolanda^DRA.^^MD||||||20250505143000|||F
OBX|1|FT|77066^Hallazgo mamografico^LN|1|Mamas de patron mixto heterogeneamente denso (ACR tipo C). No se identifican masas, distorsiones arquitecturales ni microcalcificaciones sospechosas en ninguna mama. Axilas sin adenopatias. Clasificacion BI-RADS 1: Negativo.||||||F|||20250505140000||USR-RAD-594^Barrera^Lozano^Rosa^^MED.RAD.
OBX|2|ST|59776-5^Impresion diagnostica^LN|1|Mamografia bilateral normal, BI-RADS 1||||||F|||20250505140000||USR-RAD-594^Barrera^Lozano^Rosa^^MED.RAD.
OBX|3|ED|IMG^Mamografia bilateral CC y MLO^LOCAL|1|SYNGO^IMAGE^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsMDhEQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRb/2wBDAQMEBAUEBQkFBQkWDQsNFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhb/wgARCAABAAEDAREAAhEB||||||F
```

---

## 11. ORM^O01 - Orden de angiotomografia coronaria

```
MSH|^~\&|SYNGO|PACS_ANGELES_MTY|RIS_ANGELES|ANGELES_MTY|20250506090000||ORM^O01^ORM_O01|SYNGO-20250506-001101|P|2.5|||AL|NE||8859/1
PID|1||ANG-MTY-73480983^^^ANGELES^MR||Cervera^Hinojosa^Guillermo^Arturo||19550714|M|||AV MORONES PRIETO 3241 COL LOMAS DE SAN FRANCISCO^^MONTERREY^NLE^64710^MX||8112539477^^^guillermo.cervera@prodigy.net.mx||ESP|C|CAT||||CEHG550714HNLRVL46|||||N
PV1|1|I|CARDIO-01^410^B^ANG-MTY^^BED|U|||57944^Espinosa^Palacios^Silvia^DRA.^^MD|57944^Espinosa^Palacios^Silvia^DRA.^^MD||MED||||1|||57944^Espinosa^Palacios^Silvia^DRA.^^MD|IP|VIS-20250505-011|||||||||||||||||||ANGELES||||20250505120000
ORC|NW|ORD-20250506-1101^SYNGO|FIL-20250506-1101^RIS_ANGELES||SC|||1^^^20250506090000^^R||20250506090000|USR-RAD-780^Tellez^Ochoa^Diego^^TEC.RAD.||57944^Espinosa^Palacios^Silvia^DRA.^^MD|CARDIO-01|(818)368-7777|20250506090000||ANG-MTY^Hospital Angeles Valle Oriente^L|AV FRIDA KAHLO 180 COL VALLE ORIENTE^^SAN PEDRO GARZA GARCIA^NLE^66260^MX
OBR|1|ORD-20250506-1101^SYNGO|FIL-20250506-1101^RIS_ANGELES|75574^Angiotomografia coronaria^LN|||20250506085000||||R||Dx: Dolor toracico atipico, factores de riesgo cardiovascular I25.10||||57944^Espinosa^Palacios^Silvia^DRA.^^MD||||||20250506090000|||F
```

---

## 12. ORU^R01 - Reporte de angiotomografia coronaria

```
MSH|^~\&|SYNGO|PACS_ANGELES_MTY|HIS_ANGELES|ANGELES_MTY|20250506150000||ORU^R01^ORU_R01|SYNGO-20250506-001201|P|2.5|||AL|NE||8859/1
PID|1||ANG-MTY-73480983^^^ANGELES^MR||Cervera^Hinojosa^Guillermo^Arturo||19550714|M|||AV MORONES PRIETO 3241 COL LOMAS DE SAN FRANCISCO^^MONTERREY^NLE^64710^MX||8112539477^^^guillermo.cervera@prodigy.net.mx||ESP|C|CAT||||CEHG550714HNLRVL46|||||N
PV1|1|I|CARDIO-01^410^B^ANG-MTY^^BED|U|||57944^Espinosa^Palacios^Silvia^DRA.^^MD|57944^Espinosa^Palacios^Silvia^DRA.^^MD||MED||||1|||57944^Espinosa^Palacios^Silvia^DRA.^^MD|IP|VIS-20250505-011|||||||||||||||||||ANGELES||||20250505120000
ORC|RE|ORD-20250506-1101^SYNGO|FIL-20250506-1101^RIS_ANGELES||CM|||1^^^20250506150000^^R||20250506150000|USR-RAD-219^Salinas^Maldonado^Elena^^MED.RAD.||57944^Espinosa^Palacios^Silvia^DRA.^^MD|CARDIO-01|(818)368-7777|20250506150000||ANG-MTY^Hospital Angeles Valle Oriente^L|AV FRIDA KAHLO 180 COL VALLE ORIENTE^^SAN PEDRO GARZA GARCIA^NLE^66260^MX
OBR|1|ORD-20250506-1101^SYNGO|FIL-20250506-1101^RIS_ANGELES|75574^Angiotomografia coronaria^LN|||20250506085000||||A|||||57944^Espinosa^Palacios^Silvia^DRA.^^MD||||||20250506150000|||F
OBX|1|FT|75574^Hallazgo angiotomografico^LN|1|Arteria descendente anterior con placa calcificada proximal que condiciona estenosis del 40%. Arteria circunfleja sin lesiones significativas. Arteria coronaria derecha con placa mixta en tercio medio con estenosis del 30%. Score de calcio coronario: 185 unidades Agatston. Funcion ventricular izquierda conservada con fraccion de eyeccion estimada en 60%.||||||F|||20250506143000||USR-RAD-219^Salinas^Maldonado^Elena^^MED.RAD.
OBX|2|ST|59776-5^Impresion diagnostica^LN|1|Enfermedad aterosclerotica coronaria leve a moderada, sin estenosis hemodinamicamente significativa||||||F|||20250506143000||USR-RAD-219^Salinas^Maldonado^Elena^^MED.RAD.
```

---

## 13. ORM^O01 - Orden de radiografia de columna lumbar

```
MSH|^~\&|SYNGO|PACS_ISSSTE_PUEBLA|RIS_ISSSTE|ISSSTE_PUE|20250507101500||ORM^O01^ORM_O01|SYNGO-20250507-001301|P|2.5|||AL|NE||8859/1|||MEX_NOM024^NOM-024-SSA3^L
PID|1||ISSSTE-64776830^^^ISSSTE^MR||Rangel^Tovar^Sofia^Rebeca||19660128|F|||BLVD HERMANOS SERDAN 4178 COL LA PAZ^^PUEBLA^PUE^72160^MX||2224891537^^^sofia.rangel@icloud.com||ESP|V|CAT||||RATS660128MPLNVF86|||||N
PV1|1|O|RAD-01^^^^RAD|||94158^Ibarra^Castillo^Miguel^DR.^^MD|94158^Ibarra^Castillo^Miguel^DR.^^MD||RAD||||1|||94158^Ibarra^Castillo^Miguel^DR.^^MD|OP|VIS-20250507-013|||||||||||||||||||ISSSTE||||20250507095000
ORC|NW|ORD-20250507-1301^SYNGO|FIL-20250507-1301^RIS_ISSSTE||SC|||1^^^20250507101500^^R||20250507101500|USR-RAD-860^Medina^Galarza^Ignacio^^TEC.RAD.||94158^Ibarra^Castillo^Miguel^DR.^^MD|RAD-01|(222)309-6200|20250507101500||ISSSTE-PUEBLA^ISSSTE Hospital Regional Puebla^L|14 SUR 4302 COL JARDINES DE SAN MANUEL^^PUEBLA^PUE^72570^MX
OBR|1|ORD-20250507-1301^SYNGO|FIL-20250507-1301^RIS_ISSSTE|72100^Radiografia de columna lumbar AP y lateral^LN|||20250507100000||||R||Dx: Lumbalgia cronica M54.5||||94158^Ibarra^Castillo^Miguel^DR.^^MD||||||20250507101500|||F
```

---

## 14. ORU^R01 - Reporte de radiografia de columna lumbar

```
MSH|^~\&|SYNGO|PACS_ISSSTE_PUEBLA|HIS_ISSSTE|ISSSTE_PUE|20250507133000||ORU^R01^ORU_R01|SYNGO-20250507-001401|P|2.5|||AL|NE||8859/1|||MEX_NOM024^NOM-024-SSA3^L
PID|1||ISSSTE-64776830^^^ISSSTE^MR||Rangel^Tovar^Sofia^Rebeca||19660128|F|||BLVD HERMANOS SERDAN 4178 COL LA PAZ^^PUEBLA^PUE^72160^MX||2224891537^^^sofia.rangel@icloud.com||ESP|V|CAT||||RATS660128MPLNVF86|||||N
PV1|1|O|RAD-01^^^^RAD|||94158^Ibarra^Castillo^Miguel^DR.^^MD|94158^Ibarra^Castillo^Miguel^DR.^^MD||RAD||||1|||94158^Ibarra^Castillo^Miguel^DR.^^MD|OP|VIS-20250507-013|||||||||||||||||||ISSSTE||||20250507095000
ORC|RE|ORD-20250507-1301^SYNGO|FIL-20250507-1301^RIS_ISSSTE||CM|||1^^^20250507133000^^R||20250507133000|USR-RAD-927^Delgadillo^Portillo^Javier^^MED.RAD.||94158^Ibarra^Castillo^Miguel^DR.^^MD|RAD-01|(222)309-6200|20250507133000||ISSSTE-PUEBLA^ISSSTE Hospital Regional Puebla^L|14 SUR 4302 COL JARDINES DE SAN MANUEL^^PUEBLA^PUE^72570^MX
OBR|1|ORD-20250507-1301^SYNGO|FIL-20250507-1301^RIS_ISSSTE|72100^Radiografia de columna lumbar AP y lateral^LN|||20250507100000||||A|||||94158^Ibarra^Castillo^Miguel^DR.^^MD||||||20250507133000|||F
OBX|1|FT|72100^Hallazgo radiologico^LN|1|Rectificacion de la lordosis lumbar fisiologica. Osteofitos marginales anteriores en L3-L4 y L4-L5. Disminucion del espacio intersomatico L4-L5 y L5-S1. Articulaciones sacroiliacas sin alteraciones. No se observan fracturas ni listesis. Conclusion: Cambios degenerativos de columna lumbar.||||||F|||20250507130000||USR-RAD-927^Delgadillo^Portillo^Javier^^MED.RAD.
OBX|2|ST|59776-5^Impresion diagnostica^LN|1|Espondiloartrosis lumbar con predominio en L4-L5 y L5-S1||||||F|||20250507130000||USR-RAD-927^Delgadillo^Portillo^Javier^^MED.RAD.
```

---

## 15. ORM^O01 - Orden de tomografia de abdomen contrastada

```
MSH|^~\&|SYNGO|PACS_IMSS_UMAE_25|RIS_IMSS|IMSS_MTY|20250508070000||ORM^O01^ORM_O01|SYNGO-20250508-001501|P|2.5|||AL|NE||8859/1|||MEX_NOM024^NOM-024-SSA3^L
PID|1||IMSS-70266948^^^IMSS^MR||Orellana^Salgado^Ernesto^Javier||19590627|M|||AV CONSTITUCION 2823 COL CENTRO^^MONTERREY^NLE^64000^MX||8187429315^^^ernesto.orellana@outlook.com||ESP|C|CAT||||OESE590627HNLRLR64|||||N
PV1|1|I|CIR-ONCO-01^505^A^IMSS-UMAE-25^^BED|U|||81480^Bernal^Gaitan^Maria^DRA.^^MD|81480^Bernal^Gaitan^Maria^DRA.^^MD||CIR||||1|||81480^Bernal^Gaitan^Maria^DRA.^^MD|IP|VIS-20250507-015|||||||||||||||||||IMSS||||20250507160000
ORC|NW|ORD-20250508-1501^SYNGO|FIL-20250508-1501^RIS_IMSS||SC|||1^^^20250508070000^^R||20250508070000|USR-RAD-570^Solano^Parra^Martha^^TEC.RAD.||81480^Bernal^Gaitan^Maria^DRA.^^MD|CIR-ONCO-01|(818)348-2828|20250508070000||IMSS-UMAE-25^IMSS UMAE 25 Monterrey^L|AV FIDEL VELAZQUEZ Y AV LINCOLN COL MITRAS NORTE^^MONTERREY^NLE^64320^MX
OBR|1|ORD-20250508-1501^SYNGO|FIL-20250508-1501^RIS_IMSS|74178^Tomografia de abdomen y pelvis con contraste^LN|||20250508065000||||R||Dx: Seguimiento oncologico, masa hepatica C22.0||||81480^Bernal^Gaitan^Maria^DRA.^^MD||||||20250508070000|||F
```

---

## 16. ORU^R01 - Reporte de tomografia abdominal con PDF

```
MSH|^~\&|SYNGO|PACS_IMSS_UMAE_25|HIS_IMSS|IMSS_MTY|20250508140000||ORU^R01^ORU_R01|SYNGO-20250508-001601|P|2.5|||AL|NE||8859/1|||MEX_NOM024^NOM-024-SSA3^L
PID|1||IMSS-70266948^^^IMSS^MR||Orellana^Salgado^Ernesto^Javier||19590627|M|||AV CONSTITUCION 2823 COL CENTRO^^MONTERREY^NLE^64000^MX||8187429315^^^ernesto.orellana@outlook.com||ESP|C|CAT||||OESE590627HNLRLR64|||||N
PV1|1|I|CIR-ONCO-01^505^A^IMSS-UMAE-25^^BED|U|||81480^Bernal^Gaitan^Maria^DRA.^^MD|81480^Bernal^Gaitan^Maria^DRA.^^MD||CIR||||1|||81480^Bernal^Gaitan^Maria^DRA.^^MD|IP|VIS-20250507-015|||||||||||||||||||IMSS||||20250507160000
ORC|RE|ORD-20250508-1501^SYNGO|FIL-20250508-1501^RIS_IMSS||CM|||1^^^20250508140000^^R||20250508140000|USR-RAD-169^Nava^Tirado^Pilar^^MED.RAD.||81480^Bernal^Gaitan^Maria^DRA.^^MD|CIR-ONCO-01|(818)348-2828|20250508140000||IMSS-UMAE-25^IMSS UMAE 25 Monterrey^L|AV FIDEL VELAZQUEZ Y AV LINCOLN COL MITRAS NORTE^^MONTERREY^NLE^64320^MX
OBR|1|ORD-20250508-1501^SYNGO|FIL-20250508-1501^RIS_IMSS|74178^Tomografia de abdomen y pelvis con contraste^LN|||20250508065000||||A|||||81480^Bernal^Gaitan^Maria^DRA.^^MD||||||20250508140000|||F
OBX|1|FT|74178^Hallazgo tomografico^LN|1|Lesion hepatica en segmento VI de 3.2 x 2.8 cm con realce arterial y lavado en fase portal, compatible con hepatocarcinoma segun criterios LI-RADS 5. No se identifican nuevas lesiones hepaticas. Vias biliares no dilatadas. Pancreas sin alteraciones. Rinones con captacion simetrica. No se observa liquido libre ni adenopatias retroperitoneales.||||||F|||20250508133000||USR-RAD-169^Nava^Tirado^Pilar^^MED.RAD.
OBX|2|ST|59776-5^Impresion diagnostica^LN|1|Hepatocarcinoma conocido en segmento VI estable, sin progresion, LI-RADS 5||||||F|||20250508133000||USR-RAD-169^Nava^Tirado^Pilar^^MED.RAD.
OBX|3|ED|PDF^Reporte TC abdomen oncologico^AUSPDI|1|SYNGO^AP^^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjIgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDMgMCBSID4+CmVuZG9iago0IDAgb2JqCjw8IC9UeXBlIC9QYWdlcyAvS2lkcyBbNSAwIFJdIC9Db3VudCAxID4+CmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgNCAwIFIgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0gPj4KZW5kb2Jq||||||F
```

---

## 17. ORM^O01 - Orden de ultrasonido obstetrico

```
MSH|^~\&|SYNGO|PACS_IMSS_HGO_4|RIS_IMSS|IMSS_CDMX|20250509094500||ORM^O01^ORM_O01|SYNGO-20250509-001701|P|2.5|||AL|NE||8859/1|||MEX_NOM024^NOM-024-SSA3^L
PID|1||IMSS-09034321^^^IMSS^MR||Plascencia^Duran^Carmen^Irene||19950118|F|||AV REFORMA 3427 COL JUAREZ^^CIUDAD DE MEXICO^DF^06600^MX||5548271936^^^carmen.plascencia@outlook.com||ESP|C|CAT||||PLDC950118MDFLSR56|||||N
PV1|1|O|RAD-US-OBG-01^^^^RAD|||98243^Guerrero^Solorzano^Guadalupe^DRA.^^MD|98243^Guerrero^Solorzano^Guadalupe^DRA.^^MD||OBG||||1|||98243^Guerrero^Solorzano^Guadalupe^DRA.^^MD|OP|VIS-20250509-017|||||||||||||||||||IMSS||||20250509090000
ORC|NW|ORD-20250509-1701^SYNGO|FIL-20250509-1701^RIS_IMSS||SC|||1^^^20250509094500^^R||20250509094500|USR-RAD-633^Caballero^Rios^Oscar^^TEC.RAD.||98243^Guerrero^Solorzano^Guadalupe^DRA.^^MD|RAD-US-OBG-01|55 7163 4829|20250509094500||IMSS-HGO-4^IMSS HGO 4 Luis Castelazo Ayala^L|RIO MAGDALENA 289 COL TIZAPAN^^CIUDAD DE MEXICO^DF^01090^MX
OBR|1|ORD-20250509-1701^SYNGO|FIL-20250509-1701^RIS_IMSS|76811^Ultrasonido obstetrico anatomico^LN|||20250509093000||||R||Embarazo 20 semanas, control prenatal O80||||98243^Guerrero^Solorzano^Guadalupe^DRA.^^MD||||||20250509094500|||F
```

---

## 18. ORU^R01 - Reporte de ultrasonido obstetrico

```
MSH|^~\&|SYNGO|PACS_IMSS_HGO_4|HIS_IMSS|IMSS_CDMX|20250509130000||ORU^R01^ORU_R01|SYNGO-20250509-001801|P|2.5|||AL|NE||8859/1|||MEX_NOM024^NOM-024-SSA3^L
PID|1||IMSS-09034321^^^IMSS^MR||Plascencia^Duran^Carmen^Irene||19950118|F|||AV REFORMA 3427 COL JUAREZ^^CIUDAD DE MEXICO^DF^06600^MX||5548271936^^^carmen.plascencia@outlook.com||ESP|C|CAT||||PLDC950118MDFLSR56|||||N
PV1|1|O|RAD-US-OBG-01^^^^RAD|||98243^Guerrero^Solorzano^Guadalupe^DRA.^^MD|98243^Guerrero^Solorzano^Guadalupe^DRA.^^MD||OBG||||1|||98243^Guerrero^Solorzano^Guadalupe^DRA.^^MD|OP|VIS-20250509-017|||||||||||||||||||IMSS||||20250509090000
ORC|RE|ORD-20250509-1701^SYNGO|FIL-20250509-1701^RIS_IMSS||CM|||1^^^20250509130000^^R||20250509130000|USR-RAD-630^Balderas^Lugo^Juan^^MED.RAD.||98243^Guerrero^Solorzano^Guadalupe^DRA.^^MD|RAD-US-OBG-01|55 7163 4829|20250509130000||IMSS-HGO-4^IMSS HGO 4 Luis Castelazo Ayala^L|RIO MAGDALENA 289 COL TIZAPAN^^CIUDAD DE MEXICO^DF^01090^MX
OBR|1|ORD-20250509-1701^SYNGO|FIL-20250509-1701^RIS_IMSS|76811^Ultrasonido obstetrico anatomico^LN|||20250509093000||||A|||||98243^Guerrero^Solorzano^Guadalupe^DRA.^^MD||||||20250509130000|||F
OBX|1|FT|76811^Hallazgo ultrasonografico obstetrico^LN|1|Producto unico vivo en presentacion cefalica. Frecuencia cardiaca fetal 145 lpm. Biometria fetal: BPD 48 mm, CC 178 mm, CA 155 mm, LF 33 mm, concordante con 20.2 semanas. Peso fetal estimado 350 g. Indice de liquido amniotico 14 cm. Placenta posterior grado I de Grannum. Cervix cerrado 38 mm. Anatomia fetal sin anomalias estructurales detectadas.||||||F|||20250509123000||USR-RAD-630^Balderas^Lugo^Juan^^MED.RAD.
OBX|2|ST|59776-5^Impresion diagnostica^LN|1|Embarazo de 20 semanas con feto unico vivo, anatomia normal, crecimiento adecuado||||||F|||20250509123000||USR-RAD-630^Balderas^Lugo^Juan^^MED.RAD.
```

---

## 19. ORM^O01 - Orden de resonancia magnetica cerebral

```
MSH|^~\&|SYNGO|PACS_ANGELES_GDL|RIS_ANGELES|ANGELES_GDL|20250510083000||ORM^O01^ORM_O01|SYNGO-20250510-001901|P|2.5|||AL|NE||8859/1
PID|1||ANG-GDL-17520240^^^ANGELES^MR||Garibay^Mena^Eduardo^Patricio||19700302|M|||AV LOPEZ MATEOS SUR 2726 COL CHAPALITA^^GUADALAJARA^JAL^44500^MX||3325917843^^^eduardo.garibay@outlook.com||ESP|C|CAT||||GAME700302HJLRRN77|||||N
PV1|1|I|NEURO-02^403^A^ANG-GDL^^BED|U|||94293^Alvarado^Ontiveros^Ricardo^DR.^^MD|94293^Alvarado^Ontiveros^Ricardo^DR.^^MD||MED||||1|||94293^Alvarado^Ontiveros^Ricardo^DR.^^MD|IP|VIS-20250509-019|||||||||||||||||||ANGELES||||20250509180000
ORC|NW|ORD-20250510-1901^SYNGO|FIL-20250510-1901^RIS_ANGELES||SC|||1^^^20250510083000^^R||20250510083000|USR-RAD-735^Trujillo^Ferrer^Leticia^^TEC.RAD.||94293^Alvarado^Ontiveros^Ricardo^DR.^^MD|NEURO-02|(333)641-5000|20250510083000||ANG-GDL^Hospital Angeles del Carmen^L|AV TAPIA 1435 COL AMERICANA^^GUADALAJARA^JAL^44160^MX
OBR|1|ORD-20250510-1901^SYNGO|FIL-20250510-1901^RIS_ANGELES|70553^Resonancia magnetica de cerebro sin y con contraste^LN|||20250510082000||||R||Dx: Crisis convulsivas de nuevo inicio G40.909||||94293^Alvarado^Ontiveros^Ricardo^DR.^^MD||||||20250510083000|||F
```

---

## 20. ORU^R01 - Reporte de resonancia magnetica cerebral con imagen

```
MSH|^~\&|SYNGO|PACS_ANGELES_GDL|HIS_ANGELES|ANGELES_GDL|20250510163000||ORU^R01^ORU_R01|SYNGO-20250510-002001|P|2.5|||AL|NE||8859/1
PID|1||ANG-GDL-17520240^^^ANGELES^MR||Garibay^Mena^Eduardo^Patricio||19700302|M|||AV LOPEZ MATEOS SUR 2726 COL CHAPALITA^^GUADALAJARA^JAL^44500^MX||3325917843^^^eduardo.garibay@outlook.com||ESP|C|CAT||||GAME700302HJLRRN77|||||N
PV1|1|I|NEURO-02^403^A^ANG-GDL^^BED|U|||94293^Alvarado^Ontiveros^Ricardo^DR.^^MD|94293^Alvarado^Ontiveros^Ricardo^DR.^^MD||MED||||1|||94293^Alvarado^Ontiveros^Ricardo^DR.^^MD|IP|VIS-20250509-019|||||||||||||||||||ANGELES||||20250509180000
ORC|RE|ORD-20250510-1901^SYNGO|FIL-20250510-1901^RIS_ANGELES||CM|||1^^^20250510163000^^R||20250510163000|USR-RAD-953^Peralta^Chavez^Raquel^^MED.RAD.||94293^Alvarado^Ontiveros^Ricardo^DR.^^MD|NEURO-02|(333)641-5000|20250510163000||ANG-GDL^Hospital Angeles del Carmen^L|AV TAPIA 1435 COL AMERICANA^^GUADALAJARA^JAL^44160^MX
OBR|1|ORD-20250510-1901^SYNGO|FIL-20250510-1901^RIS_ANGELES|70553^Resonancia magnetica de cerebro sin y con contraste^LN|||20250510082000||||A|||||94293^Alvarado^Ontiveros^Ricardo^DR.^^MD||||||20250510163000|||F
OBX|1|FT|70553^Hallazgo de resonancia cerebral^LN|1|Parenquima cerebral con intensidad de senal normal en secuencias T1, T2 y FLAIR. No se identifican lesiones ocupantes de espacio ni areas de restriccion en difusion. Sistema ventricular de tamano normal. Estructuras de la fosa posterior sin alteraciones. Espectroscopia por RM sin hallazgos de significado patologico. No se observa realce patologico tras la administracion de gadolinio.||||||F|||20250510160000||USR-RAD-953^Peralta^Chavez^Raquel^^MED.RAD.
OBX|2|ST|59776-5^Impresion diagnostica^LN|1|Resonancia magnetica cerebral sin alteraciones estructurales ni funcionales||||||F|||20250510160000||USR-RAD-953^Peralta^Chavez^Raquel^^MED.RAD.
OBX|3|ED|IMG^Imagen RM cerebral axial FLAIR^LOCAL|1|SYNGO^IMAGE^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsMDhEQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRb/2wBDAQMEBAUEBQkFBQkWDQsNFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhb/wgARCAEAATADASIAAhEBAxEB/8QAGwABAAIDAQE||||||F
```
