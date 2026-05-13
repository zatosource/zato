# SAMIH (ehCOS-based) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to general surgery

```
MSH|^~\&|SAMIH|HGMEL_CDMX|ADT_RCV|HGMEL|20250311073000||ADT^A01^ADT_A01|SAMIH20250311073000001|P|2.5|||AL|NE||8859/1
EVN|A01|20250311072900|||DRMTZ^Fuentes^Tapia^Ernesto^^^DR
PID|1||SAMIH152695133^^^SAMIH^MR~CURP:LOMA850610HDFNRS37^^^CURP^NI||Lopez^Moreno^Arturo^Emilio||19850610|M|||Av Insurgentes Sur 1820 Col Florida^^Ciudad De Mexico^DIF^01030^MX||5527643891^^^arturo.lopez@gmail.com||SPA|M|CAT|||LOMA850610HDFNRS37||||Ciudad de Mexico|MX
PV1|1|I|CIR-GEN^305^A^HGMEL||||23340^Sandoval^Estrada^Patricia^^^DRA|||CIR||||ADM|||23340^Sandoval^Estrada^Patricia^^^DRA|SP||INSABI||||||||||||||||||||20250311072900
IN1|1|SP_INSABI|INSABI|Instituto de Salud para el Bienestar|Blvd Adolfo Lopez Mateos 3370 Col Tec^^Merida^YUC^97130^MX
DG1|1|I10|K35.8^Apendicitis aguda no especificada^I10|||A
```

---

## 2. ADT^A03 - Discharge from pediatrics

```
MSH|^~\&|SAMIH|HGMEL_CDMX|ADT_RCV|HGMEL|20250313152000||ADT^A03^ADT_A03|SAMIH20250313152000002|P|2.5|||AL|NE||8859/1
EVN|A03|20250313151900|||DRACRUZ^Paredes^Villegas^Lorena^^^DRA
PID|1||SAMIH071949346^^^SAMIH^MR~CURP:CAHA180312HDFRRN67^^^CURP^NI||Carrillo^Huerta^Andres^^||20180312|M|||Calle Puebla 1547 Col Roma Sur^^Ciudad De Mexico^DIF^06760^MX||5531874520^^^andres.carrillo@icloud.com||SPA|S|CAT|||CAHA180312HDFRRN67||||Ciudad de Mexico|MX
PV1|1|I|PED^102^A^HGMEL||||68310^Esquivel^Navarro^Claudia^^^DRA|||PED||||ADM|||68310^Esquivel^Navarro^Claudia^^^DRA|SP||INSABI||||||||||||||||||||20250310080000|20250313151900
DG1|1|I10|J12.9^Neumonia viral no especificada^I10|||A
NK1|1|Montes^Aguilar^Teresa^Paulina|MTH|Av Cuauhtemoc 932 Col Narvarte Poniente^^Coyoacan^DIF^04510^MX|5549127863
```

---

## 3. ORM^O01 - Laboratory order for liver function panel

```
MSH|^~\&|SAMIH|HGMEL_CDMX|LAB_SYS|HGMEL|20250315090000||ORM^O01^ORM_O01|SAMIH20250315090000003|P|2.5|||AL|NE||8859/1
PID|1||SAMIH660613773^^^SAMIH^MR~CURP:RAGF680725HGTRMS62^^^CURP^NI||Ramirez^Gutierrez^Fernando^Joaquin||19680725|M|||Av Vallarta 2970 Col Arcos Vallarta^^Guadalajara^JAL^44130^MX||3312584076^^^fernando.ramirez@correo.mx||SPA|M|CAT|||RAGF680725HGTRMS62||||Ciudad de Mexico|MX
PV1|1|I|MED-INT^210^B^HGMEL||||35148^Olvera^Bautista^Alicia^^^DRA|||MED||||ADM
ORC|NW|ORD20250315001|||||^^^20250315100000^^R||20250315090000|DOROZCO^Ibarra^Lozano^Mariana^^^DRA|||||HGMEL
OBR|1|ORD20250315001||24325-3^Hepatic function panel - Serum or Plasma^LN|||20250315090000||||N|||||35148^Olvera^Bautista^Alicia^^^DRA|||||||||||^^^20250315100000^^R
DG1|1|I10|K76.0^Hepatopatia grasa no alcoholica^I10|||A
```

---

## 4. ORU^R01 - Liver function panel results

```
MSH|^~\&|SAMIH|HGMEL_CDMX|LAB_RCV|HGMEL|20250315151000||ORU^R01^ORU_R01|SAMIH20250315151000004|P|2.5|||AL|NE||8859/1
PID|1||SAMIH660613773^^^SAMIH^MR~CURP:RAGF680725HGTRMS62^^^CURP^NI||Ramirez^Gutierrez^Fernando^Joaquin||19680725|M|||Av Vallarta 2970 Col Arcos Vallarta^^Guadalajara^JAL^44130^MX||3312584076^^^fernando.ramirez@correo.mx||SPA|M|CAT|||RAGF680725HGTRMS62||||Ciudad de Mexico|MX
PV1|1|I|MED-INT^210^B^HGMEL||||35148^Olvera^Bautista^Alicia^^^DRA|||MED
ORC|RE|ORD20250315001||||||^^^20250315100000^^R||20250315151000|DOROZCO^Ibarra^Lozano^Mariana^^^DRA
OBR|1|ORD20250315001||24325-3^Hepatic function panel - Serum or Plasma^LN|||20250315100000||||N|||||35148^Olvera^Bautista^Alicia^^^DRA
OBX|1|NM|1742-6^ALT [Enzymatic activity/volume] in Serum or Plasma^LN||68|U/L|7-56|H|||F|||20250315143000
OBX|2|NM|1920-8^AST [Enzymatic activity/volume] in Serum or Plasma^LN||52|U/L|10-40|H|||F|||20250315143000
OBX|3|NM|6768-6^Alkaline phosphatase [Enzymatic activity/volume] in Serum or Plasma^LN||95|U/L|44-147|N|||F|||20250315143000
OBX|4|NM|1975-2^Total Bilirubin [Mass/volume] in Serum or Plasma^LN||1.0|mg/dL|0.1-1.2|N|||F|||20250315143000
OBX|5|NM|2885-2^Protein [Mass/volume] in Serum or Plasma^LN||7.2|g/dL|6.0-8.3|N|||F|||20250315143000
OBX|6|NM|1751-7^Albumin [Mass/volume] in Serum or Plasma^LN||4.1|g/dL|3.5-5.5|N|||F|||20250315143000
```

---

## 5. RDE^O11 - Antibiotic prescription for pneumonia

```
MSH|^~\&|SAMIH|HGMEL_CDMX|FARM_SYS|HGMEL|20250317081500||RDE^O11^RDE_O11|SAMIH20250317081500005|P|2.5|||AL|NE||8859/1
PID|1||SAMIH304009106^^^SAMIH^MR~CURP:TOEL920305HBCRRG81^^^CURP^NI||Torres^Elizondo^Gabriel^Ricardo||19920305|M|||Calle Revolucion 4518 Col Zona Centro^^Tijuana^BC^22000^MX||6641829437^^^gabriel.torres@hotmail.com||SPA|S|CAT|||TOEL920305HBCRRG81||||Ciudad de Mexico|MX
PV1|1|I|MED-INT^315^A^HGMEL||||41814^Cardenas^Villarreal^Hugo^^^DR|||MED||||ADM
ORC|NW|RX20250317001|||||^^^20250317090000^^R||20250317081500|RPINEDA^Duran^Camacho^Silvia^^^DRA|||||HGMEL
RXO|1|J01CR02^Amoxicilina/Acido clavulanico^ATC||875/125|mg||PO|TID|||||||7|TAB
RXR|PO^Oral^HL70162
RXE|^^^20250317090000^^R|J01CR02^Amoxicilina/Acido clavulanico 875/125mg^CB_SAMIH|875/125||mg|TAB|PO|TID^Tres veces al dia||||||21|TAB||||||||||||N
DG1|1|I10|J15.9^Neumonia bacteriana no especificada^I10|||A
```

---

## 6. ADT^A04 - Emergency registration for trauma

```
MSH|^~\&|SAMIH|HGMEL_CDMX|ADT_RCV|HGMEL|20250319222000||ADT^A04^ADT_A04|SAMIH20250319222000006|P|2.5|||AL|NE||8859/1
EVN|A04|20250319221900|||ENFTRIAGE^Cervantes^Rivas^Graciela^^^ENF
PID|1||SAMIH017761689^^^SAMIH^MR~CURP:NAVA880915HBCVRR13^^^CURP^NI||Navarro^Valenzuela^Roberto^Marcos||19880915|M|||Calle Benito Juarez 2745 Col Nueva^^Mexicali^BC^21100^MX||6869234571^^^roberto.navarro@yahoo.com.mx||SPA|S|CAT|||NAVA880915HBCVRR13||||Ciudad de Mexico|MX
PV1|1|E|URG^T2^A^HGMEL||||18095^Coronado^Ponce^Alfredo^^^DR|||URG||||URG|||18095^Coronado^Ponce^Alfredo^^^DR|SP||INSABI||||||||||||||||||||20250319221900
DG1|1|I10|S52.5^Fractura de la extremidad distal del radio^I10|||W
```

---

## 7. ORU^R01 - Blood gas analysis results

```
MSH|^~\&|SAMIH|HGMEL_CDMX|LAB_RCV|HGMEL|20250321060000||ORU^R01^ORU_R01|SAMIH20250321060000007|P|2.5|||AL|NE||8859/1
PID|1||SAMIH912303356^^^SAMIH^MR~CURP:ZACR700420HTCMSL84^^^CURP^NI||Zamora^Castillo^Ricardo^Enrique||19700420|M|||Av Gregorio Mendez 1850 Col Atasta^^Villahermosa^TAB^86100^MX||9934281756^^^ricardo.zamora@prodigy.net.mx||SPA|M|CAT|||ZACR700420HTCMSL84||||Ciudad de Mexico|MX
PV1|1|I|UCI^103^A^HGMEL||||47864^Miranda^Arellano^Victor^^^DR|||UCI
ORC|RE|ORD20250321002||||||^^^20250321053000^^R||20250321060000|HVALENZUELA^Pena^Salgado^Laura^^^DRA
OBR|1|ORD20250321002||24336-0^Gas panel - Arterial blood^LN|||20250321053000||||N|||||47864^Miranda^Arellano^Victor^^^DR
OBX|1|NM|2744-1^pH of Arterial blood^LN||7.32|pH|7.35-7.45|L|||F|||20250321055000
OBX|2|NM|2019-8^pCO2 [Partial pressure] in Arterial blood^LN||48|mmHg|35-45|H|||F|||20250321055000
OBX|3|NM|2703-7^pO2 [Partial pressure] in Arterial blood^LN||72|mmHg|80-100|L|||F|||20250321055000
OBX|4|NM|1959-6^Bicarbonate [Moles/volume] in Arterial blood^LN||24|mmol/L|22-26|N|||F|||20250321055000
OBX|5|NM|2708-6^Base excess in Arterial blood^LN||-2|mmol/L|-2 to +2|N|||F|||20250321055000
```

---

## 8. ORM^O01 - Blood culture order for sepsis workup

```
MSH|^~\&|SAMIH|HGMEL_CDMX|LAB_SYS|HGMEL|20250323043000||ORM^O01^ORM_O01|SAMIH20250323043000008|P|2.5|||AL|NE||8859/1
PID|1||SAMIH912303356^^^SAMIH^MR~CURP:ZACR700420HTCMSL84^^^CURP^NI||Zamora^Castillo^Ricardo^Enrique||19700420|M|||Av Gregorio Mendez 1850 Col Atasta^^Villahermosa^TAB^86100^MX||9934281756^^^ricardo.zamora@prodigy.net.mx||SPA|M|CAT|||ZACR700420HTCMSL84||||Ciudad de Mexico|MX
PV1|1|I|UCI^103^A^HGMEL||||47864^Miranda^Arellano^Victor^^^DR|||UCI
ORC|NW|ORD20250323003|||||^^^20250323050000^^R||20250323043000|HVALENZUELA^Pena^Salgado^Laura^^^DRA|||||HGMEL
OBR|1|ORD20250323003||600-7^Blood culture^LN|||20250323043000||||N|||||47864^Miranda^Arellano^Victor^^^DR|||||||||||^^^20250323050000^^R
DG1|1|I10|A41.9^Sepsis no especificada^I10|||A
```

---

## 9. ORU^R01 - Urinalysis results with scanned order image

```
MSH|^~\&|SAMIH|HGMEL_CDMX|LAB_RCV|HGMEL|20250325113000||ORU^R01^ORU_R01|SAMIH20250325113000009|P|2.5|||AL|NE||8859/1
PID|1||SAMIH702144079^^^SAMIH^MR~CURP:BEGE850220MQTLMN86^^^CURP^NI||Beltran^Guerrero^Elena^Nayeli||19850220|F|||Av Corregidora Norte 520 Col Centro^^Queretaro^QRO^76000^MX||4423916804^^^elena.beltran@gmail.com||SPA|M|CAT|||BEGE850220MQTLMN86||||Ciudad de Mexico|MX
PV1|1|O|LAB^01^A^HGMEL||||08814^Espinoza^Salinas^Veronica^^^DRA|||LAB
ORC|RE|ORD20250325004||||||^^^20250325090000^^R||20250325113000|PDELGADO^Monroy^Figueroa^Isabel^^^DRA
OBR|1|ORD20250325004||24356-8^Urinalysis complete panel - Urine^LN|||20250325090000||||N|||||08814^Espinoza^Salinas^Veronica^^^DRA
OBX|1|NM|5811-5^Specific gravity of Urine^LN||1.020||1.005-1.030|N|||F|||20250325110000
OBX|2|NM|2756-5^pH of Urine^LN||6.0||5.0-8.0|N|||F|||20250325110000
OBX|3|CWE|5770-3^Leukocyte esterase [Presence] in Urine^LN||LA9634-2^Positivo^LOINC||Negativo|A|||F|||20250325110000
OBX|4|CWE|5802-4^Nitrite [Presence] in Urine^LN||LA9634-2^Positivo^LOINC||Negativo|A|||F|||20250325110000
OBX|5|NM|5821-4^Leukocytes [#/area] in Urine sediment by Microscopy^LN||25|/HPF|0-5|H|||F|||20250325110000
OBX|6|ED|IMG^Orden de laboratorio escaneada^LOCAL|1|SAMIH^IMAGE^JPEG^Base64^/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCABAAEADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL||||||F|||20250325112000
```

---

## 10. ADT^A08 - Update patient insurance information

```
MSH|^~\&|SAMIH|HGMEL_CDMX|ADT_RCV|HGMEL|20250327091500||ADT^A08^ADT_A08|SAMIH20250327091500010|P|2.5|||AL|NE||8859/1
EVN|A08|20250327091400|||ADMIN01^Arias^Maldonado^Susana^^^LIC
PID|1||SAMIH418891791^^^SAMIH^MR~CURP:GACM780512HPLRNL40^^^CURP^NI||Garza^Cisneros^Miguel^Humberto||19780512|M|||Av Juarez 1890 Col Centro^^Cholula^PUE^72760^MX||2224631078^^^miguel.garza@yahoo.com.mx||SPA|M|CAT|||GACM780512HPLRNL40||||Ciudad de Mexico|MX
PV1|1|O|ADM^01^A^HGMEL||||73963^Rangel^Dominguez^Felipe^^^DR|||MED||||REF
IN1|1|SP_INSABI|INSABI|Instituto de Salud para el Bienestar|Blvd Adolfo Lopez Mateos 3370 Col Tec^^Merida^YUC^97130^MX|||||||||||||Garza^Cisneros^Miguel^Humberto|TITULAR|19780512|Av Universidad 3245 Col Copilco^^Benito Juarez^DIF^03020^MX
```

---

## 11. ORM^O01 - Coagulation panel order

```
MSH|^~\&|SAMIH|HGMEL_CDMX|LAB_SYS|HGMEL|20250329074500||ORM^O01^ORM_O01|SAMIH20250329074500011|P|2.5|||AL|NE||8859/1
PID|1||SAMIH152695133^^^SAMIH^MR~CURP:LOMA850610HDFNRS37^^^CURP^NI||Lopez^Moreno^Arturo^Emilio||19850610|M|||Av Insurgentes Sur 1820 Col Florida^^Ciudad De Mexico^DIF^01030^MX||5527643891^^^arturo.lopez@gmail.com||SPA|M|CAT|||LOMA850610HDFNRS37||||Ciudad de Mexico|MX
PV1|1|I|CIR-GEN^305^A^HGMEL||||23340^Sandoval^Estrada^Patricia^^^DRA|||CIR
ORC|NW|ORD20250329005|||||^^^20250329090000^^R||20250329074500|CRAMOS^Galvan^Cuevas^Andrea^^^DRA|||||HGMEL
OBR|1|ORD20250329005||34528-8^Coagulation panel^LN|||20250329074500||||N|||||23340^Sandoval^Estrada^Patricia^^^DRA|||||||||||^^^20250329090000^^R
```

---

## 12. ORU^R01 - Coagulation panel results

```
MSH|^~\&|SAMIH|HGMEL_CDMX|LAB_RCV|HGMEL|20250329113000||ORU^R01^ORU_R01|SAMIH20250329113000012|P|2.5|||AL|NE||8859/1
PID|1||SAMIH152695133^^^SAMIH^MR~CURP:LOMA850610HDFNRS37^^^CURP^NI||Lopez^Moreno^Arturo^Emilio||19850610|M|||Av Insurgentes Sur 1820 Col Florida^^Ciudad De Mexico^DIF^01030^MX||5527643891^^^arturo.lopez@gmail.com||SPA|M|CAT|||LOMA850610HDFNRS37||||Ciudad de Mexico|MX
PV1|1|I|CIR-GEN^305^A^HGMEL||||23340^Sandoval^Estrada^Patricia^^^DRA|||CIR
ORC|RE|ORD20250329005||||||^^^20250329090000^^R||20250329113000|CRAMOS^Galvan^Cuevas^Andrea^^^DRA
OBR|1|ORD20250329005||34528-8^Coagulation panel^LN|||20250329090000||||N|||||23340^Sandoval^Estrada^Patricia^^^DRA
OBX|1|NM|5902-2^Prothrombin time (PT)^LN||12.5|s|11.0-13.5|N|||F|||20250329110000
OBX|2|NM|6301-6^INR in Platelet poor plasma^LN||1.05||0.8-1.2|N|||F|||20250329110000
OBX|3|NM|3173-2^aPTT in Platelet poor plasma^LN||28|s|25-35|N|||F|||20250329110000
OBX|4|NM|3255-7^Fibrinogen [Mass/volume] in Platelet poor plasma^LN||320|mg/dL|200-400|N|||F|||20250329110000
```

---

## 13. RDE^O11 - Analgesic prescription post-surgery

```
MSH|^~\&|SAMIH|HGMEL_CDMX|FARM_SYS|HGMEL|20250331101500||RDE^O11^RDE_O11|SAMIH20250331101500013|P|2.5|||AL|NE||8859/1
PID|1||SAMIH152695133^^^SAMIH^MR~CURP:LOMA850610HDFNRS37^^^CURP^NI||Lopez^Moreno^Arturo^Emilio||19850610|M|||Av Insurgentes Sur 1820 Col Florida^^Ciudad De Mexico^DIF^01030^MX||5527643891^^^arturo.lopez@gmail.com||SPA|M|CAT|||LOMA850610HDFNRS37||||Ciudad de Mexico|MX
PV1|1|I|CIR-GEN^305^A^HGMEL||||23340^Sandoval^Estrada^Patricia^^^DRA|||CIR
ORC|NW|RX20250331002|||||^^^20250331110000^^R||20250331101500|CRAMOS^Galvan^Cuevas^Andrea^^^DRA|||||HGMEL
RXO|1|M01AE01^Ibuprofeno^ATC||400|mg||PO|TID|||||||5|TAB
RXR|PO^Oral^HL70162
RXE|^^^20250331110000^^R|M01AE01^Ibuprofeno 400mg^CB_SAMIH|400||mg|TAB|PO|TID^Tres veces al dia||||||15|TAB||||||||||||N
```

---

## 14. ORU^R01 - Blood culture result positive

```
MSH|^~\&|SAMIH|HGMEL_CDMX|LAB_RCV|HGMEL|20250402084500||ORU^R01^ORU_R01|SAMIH20250402084500014|P|2.5|||AL|NE||8859/1
PID|1||SAMIH912303356^^^SAMIH^MR~CURP:ZACR700420HTCMSL84^^^CURP^NI||Zamora^Castillo^Ricardo^Enrique||19700420|M|||Av Gregorio Mendez 1850 Col Atasta^^Villahermosa^TAB^86100^MX||9934281756^^^ricardo.zamora@prodigy.net.mx||SPA|M|CAT|||ZACR700420HTCMSL84||||Ciudad de Mexico|MX
PV1|1|I|UCI^103^A^HGMEL||||47864^Miranda^Arellano^Victor^^^DR|||UCI
ORC|RE|ORD20250323003||||||^^^20250323050000^^R||20250402084500|HVALENZUELA^Pena^Salgado^Laura^^^DRA
OBR|1|ORD20250323003||600-7^Blood culture^LN|||20250323050000||||N|||||47864^Miranda^Arellano^Victor^^^DR
OBX|1|CWE|600-7^Bacteria identified in Blood by Culture^LN||112283005^Escherichia coli^SCT||Negativo|A|||F|||20250402080000
OBX|2|FT|18769-0^Antibiogram^LN||Ampicilina: R, Ceftriaxona: S, Ciprofloxacino: S, Gentamicina: S, Meropenem: S, TMP/SMX: R||||||F|||20250402080000
```

---

## 15. ADT^A02 - Transfer from ICU to general ward

```
MSH|^~\&|SAMIH|HGMEL_CDMX|ADT_RCV|HGMEL|20250404100000||ADT^A02^ADT_A02|SAMIH20250404100000015|P|2.5|||AL|NE||8859/1
EVN|A02|20250404095900|||DRVAL^Herrera^Bravo^Ismael^^^DR
PID|1||SAMIH912303356^^^SAMIH^MR~CURP:ZACR700420HTCMSL84^^^CURP^NI||Zamora^Castillo^Ricardo^Enrique||19700420|M|||Av Gregorio Mendez 1850 Col Atasta^^Villahermosa^TAB^86100^MX||9934281756^^^ricardo.zamora@prodigy.net.mx||SPA|M|CAT|||ZACR700420HTCMSL84||||Ciudad de Mexico|MX
PV1|1|I|MED-INT^210^A^HGMEL||||47864^Miranda^Arellano^Victor^^^DR|||MED||||TRF|||47864^Miranda^Arellano^Victor^^^DR|SP||INSABI||||||||||||||||||||20250319222000
PV2|||UCI^103^A^HGMEL
DG1|1|I10|A41.9^Sepsis no especificada^I10|||A
```

---

## 16. ORU^R01 - Renal function results with PDF

```
MSH|^~\&|SAMIH|HGMEL_CDMX|LAB_RCV|HGMEL|20250406141500||ORU^R01^ORU_R01|SAMIH20250406141500016|P|2.5|||AL|NE||8859/1
PID|1||SAMIH594235883^^^SAMIH^MR~CURP:PAAL730815HQTLVS87^^^CURP^NI||Palacio^Alvarez^Luis^Sebastian||19730815|M|||Calle Ezequiel Montes 480 Col Centro Historico^^Queretaro^QRO^76000^MX||4428173652^^^luis.palacio@live.com.mx||SPA|D|CAT|||PAAL730815HQTLVS87||||Ciudad de Mexico|MX
PV1|1|O|NEFRO^02^A^HGMEL||||91978^Zavala^Hinojosa^Ruben^^^DR|||NEFRO
ORC|RE|ORD20250406006||||||^^^20250406100000^^R||20250406141500|MPADILLA^Orozco^Bermudez^Jorge^^^DR
OBR|1|ORD20250406006||24362-6^Renal function panel - Serum or Plasma^LN|||20250406100000||||N|||||91978^Zavala^Hinojosa^Ruben^^^DR
OBX|1|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||2.8|mg/dL|0.7-1.3|H|||F|||20250406135000
OBX|2|NM|3094-0^Urea nitrogen [Mass/volume] in Serum or Plasma^LN||42|mg/dL|6-20|H|||F|||20250406135000
OBX|3|NM|33914-3^eGFR CKD-EPI^LN||28|mL/min/1.73m2|>60|L|||F|||20250406135000
OBX|4|ED|PDF^Reporte de funcion renal^AUSPDI|1|SAMIH^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA3OCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDUwIDczMCBUZCAoUmVwb3J0ZSBkZSBGdW5jaW9uIFJlbmFsIC0gU0FNSUgpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmo=||||||F|||20250406141000
```

---

## 17. ADT^A01 - Admission to cardiology for heart failure

```
MSH|^~\&|SAMIH|HGMEL_CDMX|ADT_RCV|HGMEL|20250408183000||ADT^A01^ADT_A01|SAMIH20250408183000017|P|2.5|||AL|NE||8859/1
EVN|A01|20250408182900|||DRSERR^Aguirre^Delgado^Patricio^^^DR
PID|1||SAMIH420385418^^^SAMIH^MR~CURP:MALR600325HQRRGN12^^^CURP^NI||Marin^Luna^Ramon^Ignacio||19600325|M|||Calle Nader 1275 Col Cancun Centro^^Cancun^ROO^77500^MX||9982047361^^^ramon.marin@gmail.com||SPA|M|CAT|||MALR600325HQRRGN12||||Ciudad de Mexico|MX
PV1|1|I|CARD^401^A^HGMEL||||79928^Soto^Cornejo^Hector^^^DR|||CARD||||ADM|||79928^Soto^Cornejo^Hector^^^DR|SP||INSABI||||||||||||||||||||20250408182900
DG1|1|I10|I50.0^Insuficiencia cardiaca congestiva^I10|||A
DG1|2|I10|I11.0^Cardiopatia hipertensiva con insuficiencia cardiaca^I10|||A
```

---

## 18. ORM^O01 - BNP and cardiac markers order

```
MSH|^~\&|SAMIH|HGMEL_CDMX|LAB_SYS|HGMEL|20250408190000||ORM^O01^ORM_O01|SAMIH20250408190000018|P|2.5|||AL|NE||8859/1
PID|1||SAMIH420385418^^^SAMIH^MR~CURP:MALR600325HQRRGN12^^^CURP^NI||Marin^Luna^Ramon^Ignacio||19600325|M|||Calle Nader 1275 Col Cancun Centro^^Cancun^ROO^77500^MX||9982047361^^^ramon.marin@gmail.com||SPA|M|CAT|||MALR600325HQRRGN12||||Ciudad de Mexico|MX
PV1|1|I|CARD^401^A^HGMEL||||79928^Soto^Cornejo^Hector^^^DR|||CARD
ORC|NW|ORD20250408007|||||^^^20250408200000^^R||20250408190000|SREYES^Melendez^Portillo^Esteban^^^DR|||||HGMEL
OBR|1|ORD20250408007||30934-4^NT-proBNP [Mass/volume] in Serum or Plasma^LN|||20250408190000||||N|||||79928^Soto^Cornejo^Hector^^^DR|||||||||||^^^20250408200000^^R
DG1|1|I10|I50.0^Insuficiencia cardiaca congestiva^I10|||A
```

---

## 19. ORU^R01 - Cardiac markers results

```
MSH|^~\&|SAMIH|HGMEL_CDMX|LAB_RCV|HGMEL|20250408220000||ORU^R01^ORU_R01|SAMIH20250408220000019|P|2.5|||AL|NE||8859/1
PID|1||SAMIH420385418^^^SAMIH^MR~CURP:MALR600325HQRRGN12^^^CURP^NI||Marin^Luna^Ramon^Ignacio||19600325|M|||Calle Nader 1275 Col Cancun Centro^^Cancun^ROO^77500^MX||9982047361^^^ramon.marin@gmail.com||SPA|M|CAT|||MALR600325HQRRGN12||||Ciudad de Mexico|MX
PV1|1|I|CARD^401^A^HGMEL||||79928^Soto^Cornejo^Hector^^^DR|||CARD
ORC|RE|ORD20250408007||||||^^^20250408200000^^R||20250408220000|SREYES^Melendez^Portillo^Esteban^^^DR
OBR|1|ORD20250408007||30934-4^NT-proBNP [Mass/volume] in Serum or Plasma^LN|||20250408200000||||N|||||79928^Soto^Cornejo^Hector^^^DR
OBX|1|NM|30934-4^NT-proBNP [Mass/volume] in Serum or Plasma^LN||4500|pg/mL|<125|H|||F|||20250408215000
OBX|2|NM|6598-7^Troponin T cardiac [Mass/volume] in Serum or Plasma^LN||0.02|ng/mL|<0.01|H|||F|||20250408215000
```

---

## 20. ADT^A03 - Discharge from cardiology with follow-up

```
MSH|^~\&|SAMIH|HGMEL_CDMX|ADT_RCV|HGMEL|20250412110000||ADT^A03^ADT_A03|SAMIH20250412110000020|P|2.5|||AL|NE||8859/1
EVN|A03|20250412105900|||DRREYES^Vidal^Quintero^Nicolas^^^DR
PID|1||SAMIH420385418^^^SAMIH^MR~CURP:MALR600325HQRRGN12^^^CURP^NI||Marin^Luna^Ramon^Ignacio||19600325|M|||Calle Nader 1275 Col Cancun Centro^^Cancun^ROO^77500^MX||9982047361^^^ramon.marin@gmail.com||SPA|M|CAT|||MALR600325HQRRGN12||||Ciudad de Mexico|MX
PV1|1|I|CARD^401^A^HGMEL||||79928^Soto^Cornejo^Hector^^^DR|||CARD||||ADM|||79928^Soto^Cornejo^Hector^^^DR|SP||INSABI||||||||||||||||||||20250408182900|20250412105900
DG1|1|I10|I50.0^Insuficiencia cardiaca congestiva^I10|||A
DG1|2|I10|I11.0^Cardiopatia hipertensiva con insuficiencia cardiaca^I10|||A
DG1|3|I10|N18.3^Enfermedad renal cronica estadio 3^I10|||A
```
