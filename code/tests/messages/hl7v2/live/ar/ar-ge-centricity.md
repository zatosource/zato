# GE Centricity Clinical Archive - real HL7v2 ER7 messages

## 1. ORM^O01 - CT head trauma at Hospital Italiano de Buenos Aires

```
MSH|^~\&|GE_CENT|HOSP_ITALIANO_BA|RIS|HOSP_ITALIANO_BA|20250303080500||ORM^O01^ORM_O01|HIBA20250303080500001|P|2.5|||AL|NE
PID|1||GE70012345^^^GECENT^MRN~32456789^^^RENAPER^NI||RAMIREZ^Federico^Luis^^^Sr.||19850917|M|||Gascon 450^^Buenos Aires^CABA^C1181ACH^AR^L||^PRN^PH^^^11^49590300||spa^Spanish^ISO6392|C^Casado^HL70002|||32456789
PV1|1|E|RADIMG^CT01^A^HIBA^^^^RADIMG||||1102012345^Colombo^Alejandro^M^^Dr.^^^MN||EME^Emergencias^HIBASERV|||E^Emergency^HL70007|||||V70012345^^^HIBAENC^VN|OSDE^OSDE 410^HL70072||||||||||||||||||||||||20250303080500
ORC|NW|ORD701001^HIS|GE501001^GE_CENT||SC||^^^20250303083000^^R||20250303080500|LMORETTI^Moretti^Lucia^A^^Lic.|||20250303080500||HOSP_ITALIANO_BA
OBR|1|ORD701001^HIS|GE501001^GE_CENT|70450^TC Cerebro sin Contraste^CPT||||||||||||1102012345^Colombo^Alejandro^M^^Dr.^^^MN||||||20250303083000|||NI^No Information^HL70507|||^^^20250303083000^^R
DG1|1||S06.9^Traumatismo intracraneal no especificado^I10||20250303|W^Working^HL70052
```

---

## 2. ORU^R01 - CT head result with embedded JPEG at Hospital Italiano

```
MSH|^~\&|GE_CENT|HOSP_ITALIANO_BA|HIS|HOSP_ITALIANO_BA|20250303103000||ORU^R01^ORU_R01|HIBA20250303103000001|P|2.5|||AL|NE
PID|1||GE70012345^^^GECENT^MRN~32456789^^^RENAPER^NI||RAMIREZ^Federico^Luis^^^Sr.||19850917|M|||Gascon 450^^Buenos Aires^CABA^C1181ACH^AR^L||^PRN^PH^^^11^49590300||spa^Spanish^ISO6392|C^Casado^HL70002|||32456789
PV1|1|E|RADIMG^CT01^A^HIBA^^^^RADIMG||||1102012345^Colombo^Alejandro^M^^Dr.^^^MN||EME^Emergencias^HIBASERV|||E^Emergency^HL70007|||||V70012345^^^HIBAENC^VN|OSDE^OSDE 410^HL70072||||||||||||||||||||||||20250303080500
ORC|RE|ORD701001^HIS|GE501001^GE_CENT||CM||^^^20250303083000^^R||20250303103000|LMORETTI^Moretti^Lucia^A^^Lic.|||20250303103000||HOSP_ITALIANO_BA
OBR|1|ORD701001^HIS|GE501001^GE_CENT|70450^TC Cerebro sin Contraste^CPT|||20250303083500|||||||||1102012345^Colombo^Alejandro^M^^Dr.^^^MN||||||20250303102800||CT|F||^^^20250303083000^^R
OBX|1|FT|70450^TC Cerebro^CPT|1|HALLAZGOS: Estructuras de linea media centradas. Sin colecciones intra ni extraaxiales. Cisterna basal y surcos corticales de amplitud conservada. Fosa posterior sin alteraciones. Calota sin trazos fracturarios. CONCLUSION: TC cerebro sin evidencia de lesion aguda postraumatica.||||||F
OBX|2|ED|IMG^TC Cerebro Imagen Axial^LOCAL|1|GE_CENT^IMAGE^JPEG^Base64^/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCABAAEADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAw||||||F
OBX|3|CE|70450^TC Cerebro^CPT|2|Z03.3^Observacion por sospecha de trastorno del sistema nervioso^I10||||||F
```

---

## 3. ORM^O01 - Cardiac MRI order at Sanatorio de la Trinidad Palermo

```
MSH|^~\&|GE_CENT|SANATORIO_TRINIDAD_P|RIS|SANATORIO_TRINIDAD_P|20250310141500||ORM^O01^ORM_O01|STP20250310141500001|P|2.5|||AL|NE
PID|1||GE70023456^^^GECENT^MRN~28567890^^^RENAPER^NI||HERRERA^Gabriela^Alejandra^^^Sra.||19790405|F|||Cervino 4720^^Buenos Aires^CABA^C1425BEJ^AR^L||^PRN^PH^^^11^52399500||spa^Spanish^ISO6392|C^Casada^HL70002|||28567890
PV1|1|O|RADIMG^MR01^A^STRINIDAD^^^^RADIMG||||1102123456^Ferreyra^Pablo^A^^Dr.^^^MN||CAR^Cardiologia^STPSERV|||R^Referral^HL70007|||||V70023456^^^STPENC^VN|SWISS_MEDICAL^Swiss Medical^HL70072||||||||||||||||||||||||20250310141500
ORC|NW|ORD701002^HIS|GE501002^GE_CENT||SC||^^^20250310150000^^R||20250310141500|NROJAS^Rojas^Natalia^M^^Lic.|||20250310141500||SANATORIO_TRINIDAD_P
OBR|1|ORD701002^HIS|GE501002^GE_CENT|75561^RM Cardiaca con Contraste^CPT||||||||||||1102123456^Ferreyra^Pablo^A^^Dr.^^^MN||||||20250310150000|||NI^No Information^HL70507|||^^^20250310150000^^R
DG1|1||I42.0^Miocardiopatia dilatada^I10||20250310|W^Working^HL70052
```

---

## 4. ORU^R01 - Cardiac MRI result at Sanatorio de la Trinidad Palermo

```
MSH|^~\&|GE_CENT|SANATORIO_TRINIDAD_P|HIS|SANATORIO_TRINIDAD_P|20250312094500||ORU^R01^ORU_R01|STP20250312094500001|P|2.5|||AL|NE
PID|1||GE70023456^^^GECENT^MRN~28567890^^^RENAPER^NI||HERRERA^Gabriela^Alejandra^^^Sra.||19790405|F|||Cervino 4720^^Buenos Aires^CABA^C1425BEJ^AR^L||^PRN^PH^^^11^52399500||spa^Spanish^ISO6392|C^Casada^HL70002|||28567890
PV1|1|O|RADIMG^MR01^A^STRINIDAD^^^^RADIMG||||1102123456^Ferreyra^Pablo^A^^Dr.^^^MN||CAR^Cardiologia^STPSERV|||R^Referral^HL70007|||||V70023456^^^STPENC^VN|SWISS_MEDICAL^Swiss Medical^HL70072||||||||||||||||||||||||20250310141500
ORC|RE|ORD701002^HIS|GE501002^GE_CENT||CM||^^^20250310150000^^R||20250312094500|NROJAS^Rojas^Natalia^M^^Lic.|||20250312094500||SANATORIO_TRINIDAD_P
OBR|1|ORD701002^HIS|GE501002^GE_CENT|75561^RM Cardiaca con Contraste^CPT|||20250310151500|||||||||1102123456^Ferreyra^Pablo^A^^Dr.^^^MN||||||20250312094300||MR|F||^^^20250310150000^^R
OBX|1|FT|75561^RM Cardiaca^CPT|1|HALLAZGOS: VI dilatado con diametro diastolico de 62mm. FEVI 38% por metodo de Simpson. Adelgazamiento de pared inferolateral con realce tardio transmural compatible con fibrosis. Motilidad global reducida. VD de dimensiones conservadas con funcion sistolica normal. Valvulas sin regurgitacion significativa. Sin derrame pericardico. CONCLUSION: Miocardiopatia dilatada con FEVI severamente reducida. Patron de realce tardio compatible con etiologia isquemica.||||||F
OBX|2|NM|8867-4^Frecuencia Cardiaca^LN|1|78|lpm|60-100||||F
OBX|3|NM|75994-4^FEVI RM^LN|1|38|%|55-70|L|||F
```

---

## 5. ADT^A04 - Outpatient registration for PET/CT at FLENI

```
MSH|^~\&|GE_CENT|FLENI|WORKLIST|FLENI|20250318100000||ADT^A04^ADT_A01|FLE20250318100000001|P|2.5|||AL|NE
EVN|A04|20250318100000|||PVILLALBA^Villalba^Paula^S^^Lic.|20250318095000
PID|1||GE70034567^^^GECENT^MRN~23678901^^^RENAPER^NI||CASTRO^Horacio^Nestor^^^Sr.||19640215|M|||Montañeses 2325^^Buenos Aires^CABA^C1428AQK^AR^L||^PRN^PH^^^11^57773200||spa^Spanish^ISO6392|C^Casado^HL70002|||23678901
PV1|1|O|RADIMG^PET1^A^FLENI^^^^RADIMG||||1102234567^Bustamante^Eduardo^R^^Dr.^^^MN||ONC^Oncologia^FLESERV|||R^Referral^HL70007|||||V70034567^^^FLEENC^VN|OSDE^OSDE 510^HL70072||||||||||||||||||||||||20250318100000
```

---

## 6. ORM^O01 - PET/CT order at FLENI

```
MSH|^~\&|GE_CENT|FLENI|RIS|FLENI|20250318101500||ORM^O01^ORM_O01|FLE20250318101500001|P|2.5|||AL|NE
PID|1||GE70034567^^^GECENT^MRN~23678901^^^RENAPER^NI||CASTRO^Horacio^Nestor^^^Sr.||19640215|M|||Montañeses 2325^^Buenos Aires^CABA^C1428AQK^AR^L||^PRN^PH^^^11^57773200||spa^Spanish^ISO6392|C^Casado^HL70002|||23678901
PV1|1|O|RADIMG^PET1^A^FLENI^^^^RADIMG||||1102234567^Bustamante^Eduardo^R^^Dr.^^^MN||ONC^Oncologia^FLESERV|||R^Referral^HL70007|||||V70034567^^^FLEENC^VN|OSDE^OSDE 510^HL70072||||||||||||||||||||||||20250318100000
ORC|NW|ORD701003^HIS|GE501003^GE_CENT||SC||^^^20250318110000^^R||20250318101500|PVILLALBA^Villalba^Paula^S^^Lic.|||20250318101500||FLENI
OBR|1|ORD701003^HIS|GE501003^GE_CENT|78816^PET/CT Cuerpo Entero con FDG^CPT||||||||||||1102234567^Bustamante^Eduardo^R^^Dr.^^^MN||||||20250318110000|||NI^No Information^HL70507|||^^^20250318110000^^R
DG1|1||C34.90^Neoplasia maligna de pulmon no especificada^I10||20250318|W^Working^HL70052
```

---

## 7. ORU^R01 - PET/CT result at FLENI

```
MSH|^~\&|GE_CENT|FLENI|HIS|FLENI|20250320143000||ORU^R01^ORU_R01|FLE20250320143000001|P|2.5|||AL|NE
PID|1||GE70034567^^^GECENT^MRN~23678901^^^RENAPER^NI||CASTRO^Horacio^Nestor^^^Sr.||19640215|M|||Montañeses 2325^^Buenos Aires^CABA^C1428AQK^AR^L||^PRN^PH^^^11^57773200||spa^Spanish^ISO6392|C^Casado^HL70002|||23678901
PV1|1|O|RADIMG^PET1^A^FLENI^^^^RADIMG||||1102234567^Bustamante^Eduardo^R^^Dr.^^^MN||ONC^Oncologia^FLESERV|||R^Referral^HL70007|||||V70034567^^^FLEENC^VN|OSDE^OSDE 510^HL70072||||||||||||||||||||||||20250318100000
ORC|RE|ORD701003^HIS|GE501003^GE_CENT||CM||^^^20250318110000^^R||20250320143000|PVILLALBA^Villalba^Paula^S^^Lic.|||20250320143000||FLENI
OBR|1|ORD701003^HIS|GE501003^GE_CENT|78816^PET/CT Cuerpo Entero con FDG^CPT|||20250318112000|||||||||1102234567^Bustamante^Eduardo^R^^Dr.^^^MN||||||20250320142800||PT|F||^^^20250318110000^^R
OBX|1|FT|78816^PET/CT^CPT|1|HALLAZGOS: Masa pulmonar en lobulo superior derecho de 35x28mm con hipermetabolismo intenso (SUVmax 12.4). Adenopatia mediastinica paratraqueal derecha de 18mm con SUVmax 8.2. Adenopatia subcarinal de 15mm con SUVmax 6.8. Sin captacion patologica hepatica, osea ni suprarrenal. CONCLUSION: Neoplasia pulmonar metabolicamente activa con compromiso ganglionar mediastinico (N2). Estadificacion sugerida: T2aN2M0 (IIIA).||||||F
OBX|2|NM|78816^SUVmax Lesion Primaria^CPT|1|12.4|SUV|||||F
```

---

## 8. ORM^O01 - Spine MRI order at Hospital Austral

```
MSH|^~\&|GE_CENT|HOSP_AUSTRAL|RIS|HOSP_AUSTRAL|20250325093000||ORM^O01^ORM_O01|HAU20250325093000001|P|2.5|||AL|NE
PID|1||GE70045678^^^GECENT^MRN~26789012^^^RENAPER^NI||SILVA^Adriana^Beatriz^^^Sra.||19750130|F|||Los Cardos 287^^Pilar^Buenos Aires^B1629^AR^L||^PRN^PH^^^230^4482000||spa^Spanish^ISO6392|C^Casada^HL70002|||26789012
PV1|1|O|RADIMG^MR02^A^HAUSTRAL^^^^RADIMG||||1102345678^Gallo^Roberto^M^^Dr.^^^MN||NEU^Neurocirugia^HAUSERV|||R^Referral^HL70007|||||V70045678^^^HAUENC^VN|OSDE^OSDE 310^HL70072||||||||||||||||||||||||20250325093000
ORC|NW|ORD701004^HIS|GE501004^GE_CENT||SC||^^^20250325100000^^R||20250325093000|CFIGUEROA^Figueroa^Carolina^L^^Lic.|||20250325093000||HOSP_AUSTRAL
OBR|1|ORD701004^HIS|GE501004^GE_CENT|72148^RM Columna Lumbar sin Contraste^CPT||||||||||||1102345678^Gallo^Roberto^M^^Dr.^^^MN||||||20250325100000|||NI^No Information^HL70507|||^^^20250325100000^^R
DG1|1||M54.5^Lumbago no especificado^I10||20250325|W^Working^HL70052
```

---

## 9. ORU^R01 - Spine MRI result at Hospital Austral

```
MSH|^~\&|GE_CENT|HOSP_AUSTRAL|HIS|HOSP_AUSTRAL|20250326100000||ORU^R01^ORU_R01|HAU20250326100000001|P|2.5|||AL|NE
PID|1||GE70045678^^^GECENT^MRN~26789012^^^RENAPER^NI||SILVA^Adriana^Beatriz^^^Sra.||19750130|F|||Los Cardos 287^^Pilar^Buenos Aires^B1629^AR^L||^PRN^PH^^^230^4482000||spa^Spanish^ISO6392|C^Casada^HL70002|||26789012
PV1|1|O|RADIMG^MR02^A^HAUSTRAL^^^^RADIMG||||1102345678^Gallo^Roberto^M^^Dr.^^^MN||NEU^Neurocirugia^HAUSERV|||R^Referral^HL70007|||||V70045678^^^HAUENC^VN|OSDE^OSDE 310^HL70072||||||||||||||||||||||||20250325093000
ORC|RE|ORD701004^HIS|GE501004^GE_CENT||CM||^^^20250325100000^^R||20250326100000|CFIGUEROA^Figueroa^Carolina^L^^Lic.|||20250326100000||HOSP_AUSTRAL
OBR|1|ORD701004^HIS|GE501004^GE_CENT|72148^RM Columna Lumbar sin Contraste^CPT|||20250325101000|||||||||1102345678^Gallo^Roberto^M^^Dr.^^^MN||||||20250326095800||MR|F||^^^20250325100000^^R
OBX|1|FT|72148^RM Columna Lumbar^CPT|1|HALLAZGOS: Discopatia degenerativa L4-L5 y L5-S1. Hernia discal posterolateral izquierda L5-S1 que contacta raiz S1 homolateral. Estenosis foraminal izquierda L5-S1 moderada. Canal raquideo de calibre conservado. Cono medular de señal normal. CONCLUSION: Hernia discal L5-S1 con compromiso radicular S1 izquierda.||||||F
OBX|2|CE|72148^RM Columna Lumbar^CPT|2|M51.16^Trastorno de disco intervertebral lumbar con radiculopatia^I10||||||F
```

---

## 10. ADT^A01 - Inpatient admission for neurosurgery at Hospital El Cruce

```
MSH|^~\&|GE_CENT|HOSP_EL_CRUCE|ADT_RECV|HOSP_EL_CRUCE|20250401054500||ADT^A01^ADT_A01|HEC20250401054500001|P|2.5|||AL|NE
EVN|A01|20250401054500|||ESUAREZ^Suarez^Esteban^R^^Lic.|20250401050000
PID|1||GE70056789^^^GECENT^MRN~35890123^^^RENAPER^NI||MANSILLA^Esteban^Roberto^^^Sr.||19910822|M|||Av. Calchaqui 5401^^Florencio Varela^Buenos Aires^B1888AAE^AR^L||^PRN^PH^^^11^42109000||spa^Spanish^ISO6392|S^Soltero^HL70002|||35890123
NK1|1|MANSILLA^Estela^Rosa|MTH^Madre^HL70063|Av. Calchaqui 5401^^Florencio Varela^Buenos Aires^B1888AAE^AR^L|^PRN^PH^^^11^42109001||EC^Emergency Contact^HL70131
PV1|1|I|NCIR^N501^A^HELCRUCE^^^^NCIR||||1102456789^Lucero^Damian^G^^Dr.^^^MN|1102456790^Ojeda^Marina^F^^Dra.^^^MN|NCR^Neurocirugia^HECSERV|||R^Referral^HL70007|||||V70056789^^^HECENC^VN|IOMA^IOMA^HL70072||||||||||||||||||||||||20250401054500
IN1|1|IOMA001^IOMA^^IOMA|70001|IOMA|Calle 46 N 886^^La Plata^Buenos Aires^B1900^AR|^PRN^PH^^^221^4211111||||||||||20240101|20251231|||1^Titular^HL70072|MANSILLA^Esteban^Roberto|01^Self^HL70063|19910822
DG1|1||C71.1^Neoplasia maligna del lobulo frontal^I10||20250401|A^Admitting^HL70052
```

---

## 11. ORM^O01 - Post-operative MRI brain at Hospital El Cruce

```
MSH|^~\&|GE_CENT|HOSP_EL_CRUCE|RIS|HOSP_EL_CRUCE|20250404080000||ORM^O01^ORM_O01|HEC20250404080000001|P|2.5|||AL|NE
PID|1||GE70056789^^^GECENT^MRN~35890123^^^RENAPER^NI||MANSILLA^Esteban^Roberto^^^Sr.||19910822|M|||Av. Calchaqui 5401^^Florencio Varela^Buenos Aires^B1888AAE^AR^L||^PRN^PH^^^11^42109000||spa^Spanish^ISO6392|S^Soltero^HL70002|||35890123
PV1|1|I|NCIR^N501^A^HELCRUCE^^^^NCIR||||1102456789^Lucero^Damian^G^^Dr.^^^MN||NCR^Neurocirugia^HECSERV|||R^Referral^HL70007|||||V70056789^^^HECENC^VN|IOMA^IOMA^HL70072||||||||||||||||||||||||20250401054500
ORC|NW|ORD701005^HIS|GE501005^GE_CENT||SC||^^^20250404090000^^R||20250404080000|ESUAREZ^Suarez^Esteban^R^^Lic.|||20250404080000||HOSP_EL_CRUCE
OBR|1|ORD701005^HIS|GE501005^GE_CENT|70553^RM Cerebro con y sin Contraste^CPT||||||||||||1102456789^Lucero^Damian^G^^Dr.^^^MN||||||20250404090000|||NI^No Information^HL70507|||^^^20250404090000^^R
DG1|1||C71.1^Neoplasia maligna del lobulo frontal - control postquirurgico^I10||20250404|W^Working^HL70052
```

---

## 12. ORU^R01 - Post-operative MRI brain result with embedded image at Hospital El Cruce

```
MSH|^~\&|GE_CENT|HOSP_EL_CRUCE|HIS|HOSP_EL_CRUCE|20250404150000||ORU^R01^ORU_R01|HEC20250404150000001|P|2.5|||AL|NE
PID|1||GE70056789^^^GECENT^MRN~35890123^^^RENAPER^NI||MANSILLA^Esteban^Roberto^^^Sr.||19910822|M|||Av. Calchaqui 5401^^Florencio Varela^Buenos Aires^B1888AAE^AR^L||^PRN^PH^^^11^42109000||spa^Spanish^ISO6392|S^Soltero^HL70002|||35890123
PV1|1|I|NCIR^N501^A^HELCRUCE^^^^NCIR||||1102456789^Lucero^Damian^G^^Dr.^^^MN||NCR^Neurocirugia^HECSERV|||R^Referral^HL70007|||||V70056789^^^HECENC^VN|IOMA^IOMA^HL70072||||||||||||||||||||||||20250401054500
ORC|RE|ORD701005^HIS|GE501005^GE_CENT||CM||^^^20250404090000^^R||20250404150000|ESUAREZ^Suarez^Esteban^R^^Lic.|||20250404150000||HOSP_EL_CRUCE
OBR|1|ORD701005^HIS|GE501005^GE_CENT|70553^RM Cerebro con y sin Contraste^CPT|||20250404091500|||||||||1102456789^Lucero^Damian^G^^Dr.^^^MN||||||20250404145800||MR|F||^^^20250404090000^^R
OBX|1|FT|70553^RM Cerebro^CPT|1|HALLAZGOS: Cambios postquirurgicos en lobulo frontal derecho con cavidad quirurgica de 32x25mm. Realce periferico fino sin nodularidad que sugiere cambios postoperatorios esperados. Sin restriccion en difusion. Sin efecto de masa significativo. Linea media centrada. CONCLUSION: Control postquirurgico de reseccion tumoral frontal derecha. Cambios esperables sin signos sugestivos de recidiva tumoral precoz.||||||F
OBX|2|ED|IMG^RM Cerebro Post-Op^LOCAL|1|GE_CENT^IMAGE^JPEG^Base64^/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DQ4SEA8OEQ4LCxAWEBETFBUVFQwPFxgWFBgSFBT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCABAAEADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIh||||||F
OBX|3|CE|70553^RM Cerebro^CPT|2|Z48.89^Cuidados posteriores a otra cirugia especificada^I10||||||F
```

---

## 13. ORM^O01 - CT angiography pulmonary at Hospital de Clinicas

```
MSH|^~\&|GE_CENT|HOSP_CLINICAS|RIS|HOSP_CLINICAS|20250410112000||ORM^O01^ORM_O01|HCL20250410112000001|P|2.5|||AL|NE
PID|1||GE70067890^^^GECENT^MRN~31234567^^^RENAPER^NI||PEREYRA^Daniela^Solange^^^Sra.||19830619|F|||Av. Cordoba 2351^^Buenos Aires^CABA^C1120AAR^AR^L||^PRN^PH^^^11^59508000||spa^Spanish^ISO6392|S^Soltera^HL70002|||31234567
PV1|1|E|RADIMG^CT02^A^HCLINICAS^^^^RADIMG||||1102567890^Mancini^Sergio^F^^Dr.^^^MN||NEU^Neumologia^HCLSERV|||E^Emergency^HL70007|||||V70067890^^^HCLENC^VN|PAMI^PAMI^HL70072||||||||||||||||||||||||20250410112000
ORC|NW|ORD701006^HIS|GE501006^GE_CENT||SC||^^^20250410113000^^R||20250410112000|AGARCIA^Garcia^Alejandra^V^^Lic.|||20250410112000||HOSP_CLINICAS
OBR|1|ORD701006^HIS|GE501006^GE_CENT|71275^Angio TC Torax (TEP)^CPT||||||||||||1102567890^Mancini^Sergio^F^^Dr.^^^MN||||||20250410113000|||NI^No Information^HL70507|||^^^20250410113000^^R
DG1|1||I26.99^Embolia pulmonar sin cor pulmonale agudo^I10||20250410|W^Working^HL70052
```

---

## 14. ORU^R01 - CT angiography pulmonary result at Hospital de Clinicas

```
MSH|^~\&|GE_CENT|HOSP_CLINICAS|HIS|HOSP_CLINICAS|20250410133000||ORU^R01^ORU_R01|HCL20250410133000001|P|2.5|||AL|NE
PID|1||GE70067890^^^GECENT^MRN~31234567^^^RENAPER^NI||PEREYRA^Daniela^Solange^^^Sra.||19830619|F|||Av. Cordoba 2351^^Buenos Aires^CABA^C1120AAR^AR^L||^PRN^PH^^^11^59508000||spa^Spanish^ISO6392|S^Soltera^HL70002|||31234567
PV1|1|E|RADIMG^CT02^A^HCLINICAS^^^^RADIMG||||1102567890^Mancini^Sergio^F^^Dr.^^^MN||NEU^Neumologia^HCLSERV|||E^Emergency^HL70007|||||V70067890^^^HCLENC^VN|PAMI^PAMI^HL70072||||||||||||||||||||||||20250410112000
ORC|RE|ORD701006^HIS|GE501006^GE_CENT||CM||^^^20250410113000^^R||20250410133000|AGARCIA^Garcia^Alejandra^V^^Lic.|||20250410133000||HOSP_CLINICAS
OBR|1|ORD701006^HIS|GE501006^GE_CENT|71275^Angio TC Torax (TEP)^CPT|||20250410113500|||||||||1102567890^Mancini^Sergio^F^^Dr.^^^MN||||||20250410132800||CT|F||^^^20250410113000^^R
OBX|1|FT|71275^Angio TC TEP^CPT|1|HALLAZGOS: Defecto de relleno intraluminal en arteria pulmonar lobar inferior derecha y segmentaria medial del lobulo medio compatible con tromboembolismo pulmonar agudo. Arteria pulmonar principal de calibre conservado. Relacion VD/VI <1. Sin derrame pleural. CONCLUSION: TEP agudo en territorio lobar inferior derecho y segmentario del lobulo medio. Sin signos de sobrecarga de cavidades derechas.||||||F
OBX|2|CE|71275^Angio TC TEP^CPT|2|I26.99^Embolia pulmonar sin cor pulmonale agudo^I10||||||F
```

---

## 15. ORM^O01 - Coronary CT angiography at Fundacion Favaloro

```
MSH|^~\&|GE_CENT|FUND_FAVALORO|RIS|FUND_FAVALORO|20250415140000||ORM^O01^ORM_O01|FFV20250415140000001|P|2.5|||AL|NE
PID|1||GE70078901^^^GECENT^MRN~22345678^^^RENAPER^NI||LUNA^Sergio^Ariel^^^Sr.||19680403|M|||Av. Belgrano 1746^^Buenos Aires^CABA^C1093AAO^AR^L||^PRN^PH^^^11^43781200||spa^Spanish^ISO6392|C^Casado^HL70002|||22345678
PV1|1|O|RADIMG^CT03^A^FFAVALORO^^^^RADIMG||||1102678901^Paredes^Victoria^L^^Dra.^^^MN||CAR^Cardiologia^FFVSERV|||R^Referral^HL70007|||||V70078901^^^FFVENC^VN|SWISS_MEDICAL^Swiss Medical^HL70072||||||||||||||||||||||||20250415140000
ORC|NW|ORD701007^HIS|GE501007^GE_CENT||SC||^^^20250415143000^^R||20250415140000|MMORALES^Morales^Miguel^E^^Lic.|||20250415140000||FUND_FAVALORO
OBR|1|ORD701007^HIS|GE501007^GE_CENT|75574^Angio TC Coronarias con Calcio Score^CPT||||||||||||1102678901^Paredes^Victoria^L^^Dra.^^^MN||||||20250415143000|||NI^No Information^HL70507|||^^^20250415143000^^R
DG1|1||I25.10^Enfermedad cardiaca ateroesclerotica sin angina^I10||20250415|W^Working^HL70052
```

---

## 16. ORU^R01 - Coronary CT angiography result at Fundacion Favaloro

```
MSH|^~\&|GE_CENT|FUND_FAVALORO|HIS|FUND_FAVALORO|20250416091500||ORU^R01^ORU_R01|FFV20250416091500001|P|2.5|||AL|NE
PID|1||GE70078901^^^GECENT^MRN~22345678^^^RENAPER^NI||LUNA^Sergio^Ariel^^^Sr.||19680403|M|||Av. Belgrano 1746^^Buenos Aires^CABA^C1093AAO^AR^L||^PRN^PH^^^11^43781200||spa^Spanish^ISO6392|C^Casado^HL70002|||22345678
PV1|1|O|RADIMG^CT03^A^FFAVALORO^^^^RADIMG||||1102678901^Paredes^Victoria^L^^Dra.^^^MN||CAR^Cardiologia^FFVSERV|||R^Referral^HL70007|||||V70078901^^^FFVENC^VN|SWISS_MEDICAL^Swiss Medical^HL70072||||||||||||||||||||||||20250415140000
ORC|RE|ORD701007^HIS|GE501007^GE_CENT||CM||^^^20250415143000^^R||20250416091500|MMORALES^Morales^Miguel^E^^Lic.|||20250416091500||FUND_FAVALORO
OBR|1|ORD701007^HIS|GE501007^GE_CENT|75574^Angio TC Coronarias con Calcio Score^CPT|||20250415144000|||||||||1102678901^Paredes^Victoria^L^^Dra.^^^MN||||||20250416091300||CT|F||^^^20250415143000^^R
OBX|1|FT|75574^Angio TC Coronaria^CPT|1|HALLAZGOS: Calcium Score Agatston: 185 (percentil alto para edad y sexo). TCI sin lesiones. DA con placa mixta en tercio proximal que genera estenosis moderada (50-69%). Cx sin lesiones significativas. CD con placa calcificada no significativa en tercio medio. CONCLUSION: Enfermedad coronaria aterosclerotica moderada en DA proximal. Score de calcio elevado. Se sugiere evaluacion funcional.||||||F
OBX|2|NM|75574^Calcium Score Agatston^CPT|1|185|AU|||||F
```

---

## 17. ADT^A08 - Patient demographics update at Hospital Britanico

```
MSH|^~\&|GE_CENT|HOSP_BRITANICO|ADT_RECV|HOSP_BRITANICO|20250420090000||ADT^A08^ADT_A01|HBR20250420090000001|P|2.5|||AL|NE
EVN|A08|20250420090000|||JORTEGA^Ortega^Julia^A^^Lic.|20250420085000
PID|1||GE70089012^^^GECENT^MRN~19456789^^^RENAPER^NI||BRANDONI^Oscar^Mario^^^Sr.||19610530|M|||Solis 2081^^Buenos Aires^CABA^C1134ACL^AR^L||^PRN^PH^^^11^43091600||spa^Spanish^ISO6392|C^Casado^HL70002|||19456789
PV1|1|O|RADIMG^CT01^A^HBRITANICO^^^^RADIMG||||1102789012^Guzman^Patricia^R^^Dra.^^^MN||URO^Urologia^HBRSERV|||R^Referral^HL70007|||||V70089012^^^HBRENC^VN|OSDE^OSDE 310^HL70072||||||||||||||||||||||||20250420090000
```

---

## 18. ORM^O01 - CT urography at Hospital Britanico

```
MSH|^~\&|GE_CENT|HOSP_BRITANICO|RIS|HOSP_BRITANICO|20250420093000||ORM^O01^ORM_O01|HBR20250420093000001|P|2.5|||AL|NE
PID|1||GE70089012^^^GECENT^MRN~19456789^^^RENAPER^NI||BRANDONI^Oscar^Mario^^^Sr.||19610530|M|||Solis 2081^^Buenos Aires^CABA^C1134ACL^AR^L||^PRN^PH^^^11^43091600||spa^Spanish^ISO6392|C^Casado^HL70002|||19456789
PV1|1|O|RADIMG^CT01^A^HBRITANICO^^^^RADIMG||||1102789012^Guzman^Patricia^R^^Dra.^^^MN||URO^Urologia^HBRSERV|||R^Referral^HL70007|||||V70089012^^^HBRENC^VN|OSDE^OSDE 310^HL70072||||||||||||||||||||||||20250420090000
ORC|NW|ORD701008^HIS|GE501008^GE_CENT||SC||^^^20250420100000^^R||20250420093000|JORTEGA^Ortega^Julia^A^^Lic.|||20250420093000||HOSP_BRITANICO
OBR|1|ORD701008^HIS|GE501008^GE_CENT|74178^Uro TC con Contraste Trifasica^CPT||||||||||||1102789012^Guzman^Patricia^R^^Dra.^^^MN||||||20250420100000|||NI^No Information^HL70507|||^^^20250420100000^^R
DG1|1||N20.0^Calculo del riñon^I10||20250420|W^Working^HL70052
```

---

## 19. ORU^R01 - CT urography result with embedded PDF at Hospital Britanico

```
MSH|^~\&|GE_CENT|HOSP_BRITANICO|HIS|HOSP_BRITANICO|20250420150000||ORU^R01^ORU_R01|HBR20250420150000001|P|2.5|||AL|NE
PID|1||GE70089012^^^GECENT^MRN~19456789^^^RENAPER^NI||BRANDONI^Oscar^Mario^^^Sr.||19610530|M|||Solis 2081^^Buenos Aires^CABA^C1134ACL^AR^L||^PRN^PH^^^11^43091600||spa^Spanish^ISO6392|C^Casado^HL70002|||19456789
PV1|1|O|RADIMG^CT01^A^HBRITANICO^^^^RADIMG||||1102789012^Guzman^Patricia^R^^Dra.^^^MN||URO^Urologia^HBRSERV|||R^Referral^HL70007|||||V70089012^^^HBRENC^VN|OSDE^OSDE 310^HL70072||||||||||||||||||||||||20250420090000
ORC|RE|ORD701008^HIS|GE501008^GE_CENT||CM||^^^20250420100000^^R||20250420150000|JORTEGA^Ortega^Julia^A^^Lic.|||20250420150000||HOSP_BRITANICO
OBR|1|ORD701008^HIS|GE501008^GE_CENT|74178^Uro TC con Contraste Trifasica^CPT|||20250420101000|||||||||1102789012^Guzman^Patricia^R^^Dra.^^^MN||||||20250420145800||CT|F||^^^20250420100000^^R
OBX|1|FT|74178^Uro TC^CPT|1|HALLAZGOS: Riñon derecho con imagen calicica de 8mm en grupo calicial inferior compatible con litiasis. Leve dilatacion pielo-calicial derecha (grado II). Riñon izquierdo sin alteraciones. Ureteres permeables sin defectos de relleno. Vejiga normodistendida sin alteraciones parietales. CONCLUSION: Litiasis calicial inferior derecha de 8mm con hidronefrosis leve asociada.||||||F
OBX|2|ED|PDF^Informe Uro TC Completo^AUSPDI|1|GE_CENT^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA1IDAgUgo+PgplbmRvYmoKNCAwIG9iago8PAovTGVuZ3RoIDQ4Cj4+CnN0cmVhbQpCVAovRjEgMTggVGYKMTAwIDcwMCBUZAooVXJvIFRDIC0gSW5mb3JtZSBDb21wbGV0bykgVGoKRVQKZW5kc3RyZWFtCg==||||||F
OBX|3|CE|74178^Uro TC^CPT|2|N20.0^Calculo del riñon^I10||||||F
```

---

## 20. ADT^A03 - Discharge from Hospital El Cruce after neurosurgery

```
MSH|^~\&|GE_CENT|HOSP_EL_CRUCE|ADT_RECV|HOSP_EL_CRUCE|20250408151500||ADT^A03^ADT_A03|HEC20250408151500001|P|2.5|||AL|NE
EVN|A03|20250408151500|||ESUAREZ^Suarez^Esteban^R^^Lic.|20250408150000
PID|1||GE70056789^^^GECENT^MRN~35890123^^^RENAPER^NI||MANSILLA^Esteban^Roberto^^^Sr.||19910822|M|||Av. Calchaqui 5401^^Florencio Varela^Buenos Aires^B1888AAE^AR^L||^PRN^PH^^^11^42109000||spa^Spanish^ISO6392|S^Soltero^HL70002|||35890123
PV1|1|I|NCIR^N501^A^HELCRUCE^^^^NCIR||||1102456789^Lucero^Damian^G^^Dr.^^^MN|1102456790^Ojeda^Marina^F^^Dra.^^^MN|NCR^Neurocirugia^HECSERV|||R^Referral^HL70007|||||V70056789^^^HECENC^VN|IOMA^IOMA^HL70072||DI^Alta a Domicilio^HL70112||||||||||||||||||||||||20250401054500|20250408151500
DG1|1||C71.1^Neoplasia maligna del lobulo frontal^I10||20250401|A^Admitting^HL70052
DG1|2||Z48.89^Cuidados posteriores a otra cirugia especificada^I10||20250408|F^Final^HL70052
PR1|1||01N00ZZ^Reseccion de Cerebro, Abordaje Abierto^ICD10PCS|Reseccion tumoral frontal derecha|20250402080000|A^Anesthesia^HL70230||||||1102456789^Lucero^Damian^G^^Dr.^^^MN
```
