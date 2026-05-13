# Philips Tasy EMR - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission for elective surgery

```
MSH|^~\&|TASY_MX|HOSP_ANG_PUE|ADT_RCV|HANG_PUE|20250310080000||ADT^A01^ADT_A01|TASY20250310080000001|P|2.5|||AL|NE||8859/1
EVN|A01|20250310075900|||DRCAMPOS^Villegas^Paredes^Hector^^^DR
PID|1||TASY91285926^^^TASY^MR~CURP:GALA810314MDFRPN09^^^CURP^NI||Garcia^Lopez^Natalia^Ivonne||19810314|F|||Av Revolucion 2450 Col Del Valle^^Ciudad De Mexico^DF^03100^MX||5547829013^^^natalia.garcia@outlook.com||SPA|M|CAT|||GALA810314MDFRPN09||||Puebla|MX
PV1|1|I|CIR^501^A^HANG_PUE||||22746^Cervantes^Soto^Ricardo^^^DR|||CIR||||ADM|||22746^Cervantes^Soto^Ricardo^^^DR|PRIV||GNP||||||||||||||||||||20250310075900
IN1|1|GNP_PRIVADA|GNP|Grupo Nacional Provincial|Av Insurgentes Sur 3500 Col Pena Pobre^^Ciudad De Mexico^DF^14060^MX|||||||||POL-987654||||||Garcia^Lopez^Natalia^Ivonne|TITULAR|19810314|Calle Roble 178 Col Lomas De Chapultepec^^Ciudad De Mexico^DF^11000^MX
DG1|1|I10|K80.1^Calculo de vesicula biliar con colecistitis^I10|||A
```

---

## 2. ADT^A03 - Discharge after knee arthroscopy

```
MSH|^~\&|TASY_MX|CHRISTUS_MTY|ADT_RCV|CMUG_MTY|20250312163000||ADT^A03^ADT_A03|TASY20250312163000002|P|2.5|||AL|NE||8859/1
EVN|A03|20250312162900|||DRNAVARRO^Ibarra^Castillo^Miguel^^^DR
PID|1||TASY12402607^^^TASY^MR~CURP:ROVH880617HNLDRG05^^^CURP^NI||Rodriguez^Valdez^Hugo^Ernesto||19880617|M|||Blvd Diaz Ordaz 1540 Col Santa Maria^^Monterrey^NL^64650^MX||8183927461^^^hugo.rodriguez@outlook.com||SPA|M|CAT|||ROVH880617HNLDRG05||||Monterrey|MX
PV1|1|I|ORTO^301^B^CMUG_MTY||||82564^Dominguez^Leal^Arturo^^^DR|||ORTO||||ADM|||82564^Dominguez^Leal^Arturo^^^DR|PRIV||METLIFE||||||||||||||||||||20250312060000|20250312162900
IN1|1|METLIFE_PRIVADA|METLIFE|MetLife Mexico|Blvd Manuel Avila Camacho 164 Col Lomas De Chapultepec^^Ciudad De Mexico^DF^11000^MX|||||||||POL-123456
DG1|1|I10|M23.2^Lesion de menisco^I10|||A
```

---

## 3. ORM^O01 - Pre-surgical lab panel order

```
MSH|^~\&|TASY_MX|HOSP_ANG_PUE|LAB_SYS|HANG_PUE|20250309150000||ORM^O01^ORM_O01|TASY20250309150000003|P|2.5|||AL|NE||8859/1
PID|1||TASY91285926^^^TASY^MR~CURP:GALA810314MDFRPN09^^^CURP^NI||Garcia^Lopez^Natalia^Ivonne||19810314|F|||Av Revolucion 2450 Col Del Valle^^Ciudad De Mexico^DF^03100^MX||5547829013^^^natalia.garcia@outlook.com||SPA|M|CAT|||GALA810314MDFRPN09||||Puebla|MX
PV1|1|O|LAB^01^A^HANG_PUE||||22746^Cervantes^Soto^Ricardo^^^DR|||CIR||||PRE
ORC|NW|ORD20250309001|||||^^^20250309160000^^R||20250309150000|OCAMPOS^Rangel^Mora^Sebastian^^^DR|||||HANG_PUE
OBR|1|ORD20250309001||34528-8^Coagulation panel^LN|||20250309150000||||N|||||22746^Cervantes^Soto^Ricardo^^^DR|||||||||||^^^20250309160000^^R
OBR|2|ORD20250309001||58410-2^CBC panel - Blood by Automated count^LN|||20250309150000||||N|||||22746^Cervantes^Soto^Ricardo^^^DR|||||||||||^^^20250309160000^^R
```

---

## 4. ORU^R01 - Pre-surgical lab results

```
MSH|^~\&|TASY_MX|HOSP_ANG_PUE|LAB_RCV|HANG_PUE|20250309183000||ORU^R01^ORU_R01|TASY20250309183000004|P|2.5|||AL|NE||8859/1
PID|1||TASY91285926^^^TASY^MR~CURP:GALA810314MDFRPN09^^^CURP^NI||Garcia^Lopez^Natalia^Ivonne||19810314|F|||Av Revolucion 2450 Col Del Valle^^Ciudad De Mexico^DF^03100^MX||5547829013^^^natalia.garcia@outlook.com||SPA|M|CAT|||GALA810314MDFRPN09||||Puebla|MX
PV1|1|O|LAB^01^A^HANG_PUE||||22746^Cervantes^Soto^Ricardo^^^DR|||LAB
ORC|RE|ORD20250309001||||||^^^20250309160000^^R||20250309183000|OCAMPOS^Rangel^Mora^Sebastian^^^DR
OBR|1|ORD20250309001||34528-8^Coagulation panel^LN|||20250309160000||||N|||||22746^Cervantes^Soto^Ricardo^^^DR
OBX|1|NM|5902-2^Prothrombin time (PT)^LN||12.0|s|11.0-13.5|N|||F|||20250309180000
OBX|2|NM|6301-6^INR in Platelet poor plasma^LN||1.0||0.8-1.2|N|||F|||20250309180000
OBX|3|NM|3173-2^aPTT in Platelet poor plasma^LN||30|s|25-35|N|||F|||20250309180000
OBX|4|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||13.8|g/dL|12.0-16.0|N|||F|||20250309180000
OBX|5|NM|777-3^Platelets [#/volume] in Blood by Automated count^LN||260|10*3/uL|150-400|N|||F|||20250309180000
```

---

## 5. SIU^S12 - Appointment scheduling for follow-up visit

```
MSH|^~\&|TASY_MX|CHRISTUS_MTY|SCH_RCV|CMUG_MTY|20250314090000||SIU^S12^SIU_S12|TASY20250314090000005|P|2.5|||AL|NE||8859/1
SCH|APT20250314001|||||FOLLOWUP^Cita de seguimiento posquirurgico^LOCAL|||||15|min|^^^20250321100000^20250321101500|||||23456^Vega^Coronado^Alejandro^^^DR|||||BOOKED
PID|1||TASY12402607^^^TASY^MR~CURP:ROVH880617HNLDRG05^^^CURP^NI||Rodriguez^Valdez^Hugo^Ernesto||19880617|M|||Blvd Diaz Ordaz 1540 Col Santa Maria^^Monterrey^NL^64650^MX||8183927461^^^hugo.rodriguez@outlook.com||SPA|M|CAT|||ROVH880617HNLDRG05||||Monterrey|MX
PV1|1|O|ORTO-EXT^03^A^CMUG_MTY||||82564^Dominguez^Leal^Arturo^^^DR|||ORTO
AIG|1||23456^Vega^Coronado^Alejandro^^^DR
AIL|1||ORTO-EXT^Consultorio 3^CMUG_MTY
```

---

## 6. ORM^O01 - Metabolic panel for diabetes check-up

```
MSH|^~\&|TASY_MX|STARMED_GDL|LAB_SYS|SMED_GDL|20250316091500||ORM^O01^ORM_O01|TASY20250316091500006|P|2.5|||AL|NE||8859/1
PID|1||TASY69676560^^^TASY^MR~CURP:MEBP740922MJCLRR08^^^CURP^NI||Medina^Barrientos^Patricia^Guadalupe||19740922|F|||Av Lopez Mateos Sur 2375 Col Chapalita^^Guadalajara^JAL^44500^MX||3338195604^^^patricia.medina@hotmail.com||SPA|D|CAT|||MEBP740922MJCLRR08||||Guadalajara|MX
PV1|1|O|MED-EXT^05^A^SMED_GDL||||03937^Aguilar^Fuentes^Enrique^^^DR|||MED||||REF
ORC|NW|ORD20250316002|||||^^^20250316100000^^R||20250316091500|AIBARRA^Montes^Salazar^Daniela^^^DRA|||||SMED_GDL
OBR|1|ORD20250316002||24323-8^Comprehensive metabolic 2000 panel - Serum or Plasma^LN|||20250316091500||||N|||||03937^Aguilar^Fuentes^Enrique^^^DR|||||||||||^^^20250316100000^^R
DG1|1|I10|E11.6^Diabetes mellitus tipo 2 con complicaciones^I10|||A
```

---

## 7. ORU^R01 - Metabolic panel results with PDF report

```
MSH|^~\&|TASY_MX|STARMED_GDL|LAB_RCV|SMED_GDL|20250316150000||ORU^R01^ORU_R01|TASY20250316150000007|P|2.5|||AL|NE||8859/1
PID|1||TASY69676560^^^TASY^MR~CURP:MEBP740922MJCLRR08^^^CURP^NI||Medina^Barrientos^Patricia^Guadalupe||19740922|F|||Av Lopez Mateos Sur 2375 Col Chapalita^^Guadalajara^JAL^44500^MX||3338195604^^^patricia.medina@hotmail.com||SPA|D|CAT|||MEBP740922MJCLRR08||||Guadalajara|MX
PV1|1|O|LAB^01^A^SMED_GDL||||03937^Aguilar^Fuentes^Enrique^^^DR|||LAB
ORC|RE|ORD20250316002||||||^^^20250316100000^^R||20250316150000|AIBARRA^Montes^Salazar^Daniela^^^DRA
OBR|1|ORD20250316002||24323-8^Comprehensive metabolic 2000 panel - Serum or Plasma^LN|||20250316100000||||N|||||03937^Aguilar^Fuentes^Enrique^^^DR
OBX|1|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||145|mg/dL|74-106|H|||F|||20250316143000
OBX|2|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||1.1|mg/dL|0.7-1.3|N|||F|||20250316143000
OBX|3|NM|2951-2^Sodium [Moles/volume] in Serum or Plasma^LN||138|mmol/L|136-145|N|||F|||20250316143000
OBX|4|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN||4.5|mmol/L|3.5-5.1|N|||F|||20250316143000
OBX|5|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN||8.2|%|<7.0|H|||F|||20250316143000
OBX|6|ED|PDF^Reporte panel metabolico completo^AUSPDI|1|TASY_MX^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAxMDIgPj4Kc3RyZWFtCkJUIC9GMSAxMiBUZiA1MCA3MzAgVGQgKFJlcG9ydGUgTGFib3JhdG9yaW8gLSBQYW5lbCBNZXRhYm9saWNvKSBUaiBFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCg==||||||F|||20250316145000
```

---

## 8. ADT^A04 - Emergency registration for chest pain

```
MSH|^~\&|TASY_MX|HOSP_ANG_CDMX|ADT_RCV|HANG_CDMX|20250318194500||ADT^A04^ADT_A04|TASY20250318194500008|P|2.5|||AL|NE||8859/1
EVN|A04|20250318194400|||ENFTRIAGE^Orozco^Bernal^Luciana^^^ENF
PID|1||TASY12052339^^^TASY^MR~CURP:TORJ670803HDFRVR02^^^CURP^NI||Torres^Rivera^Jorge^Armando||19670803|M|||Calle Hamburgo 218 Col Juarez^^Ciudad De Mexico^DF^06600^MX||5531847296^^^jorge.torres@hotmail.com||SPA|M|CAT|||TORJ670803HDFRVR02||||Ciudad de Mexico|MX
PV1|1|E|URG^T1^A^HANG_CDMX||||31877^Solis^Figueroa^Gabriel^^^DR|||URG||||URG|||31877^Solis^Figueroa^Gabriel^^^DR|PRIV||AXA||||||||||||||||||||20250318194400
IN1|1|AXA_PRIVADA|AXA|AXA Seguros|Av Xola 535 Col Del Valle^^Ciudad De Mexico^DF^03100^MX|||||||||POL-456789
DG1|1|I10|R07.9^Dolor toracico no especificado^I10|||W
```

---

## 9. ORM^O01 - Cardiac enzyme panel order

```
MSH|^~\&|TASY_MX|HOSP_ANG_CDMX|LAB_SYS|HANG_CDMX|20250318200000||ORM^O01^ORM_O01|TASY20250318200000009|P|2.5|||AL|NE||8859/1
PID|1||TASY12052339^^^TASY^MR~CURP:TORJ670803HDFRVR02^^^CURP^NI||Torres^Rivera^Jorge^Armando||19670803|M|||Calle Hamburgo 218 Col Juarez^^Ciudad De Mexico^DF^06600^MX||5531847296^^^jorge.torres@hotmail.com||SPA|M|CAT|||TORJ670803HDFRVR02||||Ciudad de Mexico|MX
PV1|1|E|URG^T1^A^HANG_CDMX||||31877^Solis^Figueroa^Gabriel^^^DR|||URG
ORC|NW|ORD20250318003|||||^^^20250318210000^^S||20250318200000|FQUINTERO^Palacios^Zuniga^Omar^^^DR|||||HANG_CDMX
OBR|1|ORD20250318003||89579-7^Troponin I.cardiac panel - Serum or Plasma^LN|||20250318200000||||S|||||31877^Solis^Figueroa^Gabriel^^^DR|||||||||||^^^20250318210000^^S
DG1|1|I10|I21.9^Infarto agudo del miocardio sin especificar^I10|||W
```

---

## 10. ORU^R01 - Cardiac enzymes results

```
MSH|^~\&|TASY_MX|HOSP_ANG_CDMX|LAB_RCV|HANG_CDMX|20250318213000||ORU^R01^ORU_R01|TASY20250318213000010|P|2.5|||AL|NE||8859/1
PID|1||TASY12052339^^^TASY^MR~CURP:TORJ670803HDFRVR02^^^CURP^NI||Torres^Rivera^Jorge^Armando||19670803|M|||Calle Hamburgo 218 Col Juarez^^Ciudad De Mexico^DF^06600^MX||5531847296^^^jorge.torres@hotmail.com||SPA|M|CAT|||TORJ670803HDFRVR02||||Ciudad de Mexico|MX
PV1|1|E|URG^T1^A^HANG_CDMX||||31877^Solis^Figueroa^Gabriel^^^DR|||URG
ORC|RE|ORD20250318003||||||^^^20250318210000^^S||20250318213000|FQUINTERO^Palacios^Zuniga^Omar^^^DR
OBR|1|ORD20250318003||89579-7^Troponin I.cardiac panel - Serum or Plasma^LN|||20250318210000||||N|||||31877^Solis^Figueroa^Gabriel^^^DR
OBX|1|NM|49563-0^Troponin I.cardiac [Mass/volume] in Serum or Plasma by High sensitivity^LN||0.85|ng/mL|<0.04|H|||F|||20250318211500
OBX|2|NM|2157-6^CK-MB [Enzymatic activity/volume] in Serum or Plasma^LN||35|U/L|<25|H|||F|||20250318211500
OBX|3|NM|30934-4^NT-proBNP [Mass/volume] in Serum or Plasma^LN||890|pg/mL|<125|H|||F|||20250318211500
```

---

## 11. ADT^A01 - Admission for acute MI

```
MSH|^~\&|TASY_MX|HOSP_ANG_CDMX|ADT_RCV|HANG_CDMX|20250318223000||ADT^A01^ADT_A01|TASY20250318223000011|P|2.5|||AL|NE||8859/1
EVN|A01|20250318222900|||DRQUINTERO^Cabrera^Navarro^Sergio^^^DR
PID|1||TASY12052339^^^TASY^MR~CURP:TORJ670803HDFRVR02^^^CURP^NI||Torres^Rivera^Jorge^Armando||19670803|M|||Calle Hamburgo 218 Col Juarez^^Ciudad De Mexico^DF^06600^MX||5531847296^^^jorge.torres@hotmail.com||SPA|M|CAT|||TORJ670803HDFRVR02||||Ciudad de Mexico|MX
PV1|1|I|UCC^101^A^HANG_CDMX||||31877^Solis^Figueroa^Gabriel^^^DR|||UCC||||ADM|||31877^Solis^Figueroa^Gabriel^^^DR|PRIV||AXA||||||||||||||||||||20250318222900
IN1|1|AXA_PRIVADA|AXA|AXA Seguros|Av Xola 535 Col Del Valle^^Ciudad De Mexico^DF^03100^MX|||||||||POL-456789
DG1|1|I10|I21.0^Infarto agudo del miocardio de pared anterior^I10|||A
```

---

## 12. RDE^O11 - Anticoagulation therapy for MI

```
MSH|^~\&|TASY_MX|HOSP_ANG_CDMX|FARM_SYS|HANG_CDMX|20250318230000||RDE^O11^RDE_O11|TASY20250318230000012|P|2.5|||AL|NE||8859/1
PID|1||TASY12052339^^^TASY^MR~CURP:TORJ670803HDFRVR02^^^CURP^NI||Torres^Rivera^Jorge^Armando||19670803|M|||Calle Hamburgo 218 Col Juarez^^Ciudad De Mexico^DF^06600^MX||5531847296^^^jorge.torres@hotmail.com||SPA|M|CAT|||TORJ670803HDFRVR02||||Ciudad de Mexico|MX
PV1|1|I|UCC^101^A^HANG_CDMX||||31877^Solis^Figueroa^Gabriel^^^DR|||UCC
ORC|NW|RX20250318003|||||^^^20250318233000^^R||20250318230000|FQUINTERO^Palacios^Zuniga^Omar^^^DR|||||HANG_CDMX
RXO|1|B01AB05^Enoxaparina^ATC||60|mg||SC|BID|||||||5|JER
RXR|SC^Subcutanea^HL70162
RXE|^^^20250318233000^^R|B01AB05^Enoxaparina 60mg jeringa prellenada^CB_TASY|60||mg|JER|SC|BID^Cada 12 horas||||||10|JER||||||||||||N
DG1|1|I10|I21.0^Infarto agudo del miocardio de pared anterior^I10|||A
```

---

## 13. SIU^S12 - Catheterization lab scheduling

```
MSH|^~\&|TASY_MX|HOSP_ANG_CDMX|SCH_RCV|HANG_CDMX|20250319060000||SIU^S12^SIU_S12|TASY20250319060000013|P|2.5|||AL|NE||8859/1
SCH|APT20250319001|||||CATH^Cateterismo cardiaco diagnostico^LOCAL|||||60|min|^^^20250319080000^20250319090000|||||45678^Lozano^Macias^Fernando^^^DR|||||BOOKED
PID|1||TASY12052339^^^TASY^MR~CURP:TORJ670803HDFRVR02^^^CURP^NI||Torres^Rivera^Jorge^Armando||19670803|M|||Calle Hamburgo 218 Col Juarez^^Ciudad De Mexico^DF^06600^MX||5531847296^^^jorge.torres@hotmail.com||SPA|M|CAT|||TORJ670803HDFRVR02||||Ciudad de Mexico|MX
PV1|1|I|UCC^101^A^HANG_CDMX||||31877^Solis^Figueroa^Gabriel^^^DR|||UCC
AIG|1||45678^Lozano^Macias^Fernando^^^DR
AIL|1||HEMO^Sala de hemodinamica^HANG_CDMX
```

---

## 14. ORU^R01 - Pathology report with image

```
MSH|^~\&|TASY_MX|HOSP_ANG_PUE|PATH_RCV|HANG_PUE|20250320143000||ORU^R01^ORU_R01|TASY20250320143000014|P|2.5|||AL|NE||8859/1
PID|1||TASY79853401^^^TASY^MR~CURP:HEVL701105MPLRRZ04^^^CURP^NI||Herrera^Vargas^Luz^Alejandra||19701105|F|||Av Juarez 1890 Col Centro^^Puebla^PUE^72000^MX||2224817563^^^luz.herrera@correo.mx||SPA|M|CAT|||HEVL701105MPLRRZ04||||Puebla|MX
PV1|1|I|CIR^502^A^HANG_PUE||||12501^Estrada^Miranda^Sofia^^^DRA|||CIR
ORC|RE|PATH20250320001||||||^^^20250318120000^^R||20250320143000|DAGUILAR^Rios^Camacho^Mariana^^^DRA
OBR|1|PATH20250320001||22049-4^Surgical pathology report^LN|||20250318120000||||N|||||12501^Estrada^Miranda^Sofia^^^DRA||||||PATH
OBX|1|FT|22049-4^Surgical pathology^LN||Pieza quirurgica: Vesicula biliar de 9x3.5cm. Pared con espesor de 4mm. Mucosa aterciopelada sin lesiones. Contenido: lito unico de 15mm. Diagnostico: Colecistitis cronica litiasica.||||||F|||20250320140000
OBX|2|CWE|59776-5^Diagnostico histopatologico^LN||K80.1^Colecistitis cronica litiasica^I10||||||F|||20250320140000
OBX|3|ED|IMG^Imagen histopatologia vesicula biliar^LOCAL|1|TASY_MX^IMAGE^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAoACgDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQA||||||F|||20250320142000
```

---

## 15. ADT^A08 - Update patient allergy information

```
MSH|^~\&|TASY_MX|CHRISTUS_MTY|ADT_RCV|CMUG_MTY|20250322101000||ADT^A08^ADT_A08|TASY20250322101000015|P|2.5|||AL|NE||8859/1
EVN|A08|20250322100900|||DRIBARRA^Paredes^Trujillo^Eduardo^^^DR
PID|1||TASY91490196^^^TASY^MR~CURP:CARM910428HNLSDN06^^^CURP^NI||Castillo^Ramos^Nelson^Joaquin||19910428|M|||Av Gonzalitos 415 Col Mitras Centro^^Monterrey^NL^64460^MX||8117924583^^^nelson.castillo@gmail.com||SPA|S|CAT|||CARM910428HNLSDN06||||Monterrey|MX
PV1|1|O|ALERG^01^A^CMUG_MTY||||56034^Villarreal^Zuniga^Luis^^^DR|||MED||||REF
AL1|1|DA|C0022192^Penicilina^UMLS|MO|Urticaria y angioedema|20200115
AL1|2|FA|C0004057^Aspirina^UMLS|MI|Broncoespasmo|20190520
```

---

## 16. ORM^O01 - Thyroid panel for follow-up

```
MSH|^~\&|TASY_MX|STARMED_GDL|LAB_SYS|SMED_GDL|20250324083000||ORM^O01^ORM_O01|TASY20250324083000016|P|2.5|||AL|NE||8859/1
PID|1||TASY74546798^^^TASY^MR~CURP:MOGC730620MJCNRR12^^^CURP^NI||Montoya^Guerrero^Carmen^Ximena||19730620|F|||Calle Hidalgo 1547 Col Centro^^Queretaro^QRO^76000^MX||4421836942^^^carmen.montoya@icloud.com||SPA|M|CAT|||MOGC730620MJCNRR12||||Guadalajara|MX
PV1|1|O|ENDO-EXT^02^A^SMED_GDL||||84223^Nunez^Velasco^Daniela^^^DRA|||ENDO||||REF
ORC|NW|ORD20250324004|||||^^^20250324100000^^R||20250324083000|PSERRANO^Duarte^Cisneros^Claudia^^^DRA|||||SMED_GDL
OBR|1|ORD20250324004||24348-5^Thyroid panel - Serum or Plasma^LN|||20250324083000||||N|||||84223^Nunez^Velasco^Daniela^^^DRA|||||||||||^^^20250324100000^^R
DG1|1|I10|E05.0^Tirotoxicosis con bocio difuso^I10|||A
```

---

## 17. ORU^R01 - Thyroid panel results

```
MSH|^~\&|TASY_MX|STARMED_GDL|LAB_RCV|SMED_GDL|20250324150000||ORU^R01^ORU_R01|TASY20250324150000017|P|2.5|||AL|NE||8859/1
PID|1||TASY74546798^^^TASY^MR~CURP:MOGC730620MJCNRR12^^^CURP^NI||Montoya^Guerrero^Carmen^Ximena||19730620|F|||Calle Hidalgo 1547 Col Centro^^Queretaro^QRO^76000^MX||4421836942^^^carmen.montoya@icloud.com||SPA|M|CAT|||MOGC730620MJCNRR12||||Guadalajara|MX
PV1|1|O|LAB^01^A^SMED_GDL||||84223^Nunez^Velasco^Daniela^^^DRA|||LAB
ORC|RE|ORD20250324004||||||^^^20250324100000^^R||20250324150000|PSERRANO^Duarte^Cisneros^Claudia^^^DRA
OBR|1|ORD20250324004||24348-5^Thyroid panel - Serum or Plasma^LN|||20250324100000||||N|||||84223^Nunez^Velasco^Daniela^^^DRA
OBX|1|NM|3016-3^TSH [Units/volume] in Serum or Plasma^LN||0.15|mIU/L|0.4-4.0|L|||F|||20250324143000
OBX|2|NM|3026-2^T3 Free [Mass/volume] in Serum or Plasma^LN||5.8|pg/mL|2.3-4.2|H|||F|||20250324143000
OBX|3|NM|3024-7^T4 Free [Mass/volume] in Serum or Plasma^LN||2.8|ng/dL|0.8-1.8|H|||F|||20250324143000
```

---

## 18. ADT^A28 - New patient registration

```
MSH|^~\&|TASY_MX|CHRISTUS_MTY|ADT_RCV|CMUG_MTY|20250326090000||ADT^A28^ADT_A28|TASY20250326090000018|P|2.5|||AL|NE||8859/1
EVN|A28|20250326085900|||ADMIN01^Olvera^Sandoval^Monica^^^LIC
PID|1||TASY47196667^^^TASY^MR~CURP:LOHD960215HDFPRL03^^^CURP^NI||Lopez^Huerta^Daniel^Emilio||19960215|M|||Calle Durango 240 Col Roma Norte^^Ciudad De Mexico^DF^06700^MX||5520512101^^^daniel.lopez@correo.mx||SPA|S|CAT|||LOHD960215HDFPRL03||||Monterrey|MX
PV1|1|O|REG^01^A^CMUG_MTY||||41539^Campos^Zepeda^Ignacio^^^DR|||MED||||REF
IN1|1|METLIFE_PRIVADA|METLIFE|MetLife Mexico|Blvd Manuel Avila Camacho 164 Col Lomas De Chapultepec^^Ciudad De Mexico^DF^11000^MX|||||||||POL-789012||||||Lopez^Huerta^Daniel^Emilio|TITULAR|19960215|Calle Tamaulipas 95 Col Condesa^^Ciudad De Mexico^DF^06140^MX
NK1|1|Reyes^Gallardo^Antonio^Lorenzo|FTH|Calle Libertad 1221 Col Condesa^^Ciudad De Mexico^DF^06140^MX|5564204798
```

---

## 19. ORU^R01 - Tumor markers results

```
MSH|^~\&|TASY_MX|HOSP_ANG_PUE|LAB_RCV|HANG_PUE|20250328141500||ORU^R01^ORU_R01|TASY20250328141500019|P|2.5|||AL|NE||8859/1
PID|1||TASY79853401^^^TASY^MR~CURP:HEVL701105MPLRRZ04^^^CURP^NI||Herrera^Vargas^Luz^Alejandra||19701105|F|||Av Juarez 1890 Col Centro^^Puebla^PUE^72000^MX||2224817563^^^luz.herrera@correo.mx||SPA|M|CAT|||HEVL701105MPLRRZ04||||Puebla|MX
PV1|1|O|ONC^01^A^HANG_PUE||||95185^Becerra^Jaramillo^Rafael^^^DR|||ONC
ORC|RE|ORD20250328005||||||^^^20250328100000^^R||20250328141500|RDELGADO^Esquivel^Iturbe^Adrian^^^DR
OBR|1|ORD20250328005||55233-1^Tumor marker panel^LN|||20250328100000||||N|||||95185^Becerra^Jaramillo^Rafael^^^DR
OBX|1|NM|2857-1^CA 125 [Units/volume] in Serum or Plasma^LN||18|U/mL|<35|N|||F|||20250328135000
OBX|2|NM|72170-4^CA 19-9 [Units/volume] in Serum or Plasma^LN||12|U/mL|<37|N|||F|||20250328135000
OBX|3|NM|2039-6^CEA [Mass/volume] in Serum or Plasma^LN||2.5|ng/mL|<5.0|N|||F|||20250328135000
```

---

## 20. SIU^S14 - Appointment modification for oncology follow-up

```
MSH|^~\&|TASY_MX|HOSP_ANG_PUE|SCH_RCV|HANG_PUE|20250330091000||SIU^S14^SIU_S14|TASY20250330091000020|P|2.5|||AL|NE||8859/1
SCH|APT20250330002|APT20250325001||||FOLLOWUP^Seguimiento oncologico^LOCAL|||||30|min|^^^20250415100000^20250415103000|||||90123^Quintana^Espinosa^Roberto^^^DR|||||BOOKED
PID|1||TASY79853401^^^TASY^MR~CURP:HEVL701105MPLRRZ04^^^CURP^NI||Herrera^Vargas^Luz^Alejandra||19701105|F|||Av Juarez 1890 Col Centro^^Puebla^PUE^72000^MX||2224817563^^^luz.herrera@correo.mx||SPA|M|CAT|||HEVL701105MPLRRZ04||||Puebla|MX
PV1|1|O|ONC-EXT^02^A^HANG_PUE||||95185^Becerra^Jaramillo^Rafael^^^DR|||ONC
AIG|1||90123^Quintana^Espinosa^Roberto^^^DR
AIL|1||ONC-EXT^Consultorio Oncologia 2^HANG_PUE
```
