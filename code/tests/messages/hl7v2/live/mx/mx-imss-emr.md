# IMSS EMR (in-house) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to internal medicine

```
MSH|^~\&|IMSS_ECE|HGZ_32_CDMX|ADT_RCV|HGZ_32|20250312084512||ADT^A01^ADT_A01|IMSS20250312084512001|P|2.5|||AL|NE||8859/1
EVN|A01|20250312084500|||DRMONTALVO^Rios^Cabrera^Hector^^^DR
PID|1||NSS49623878040^^^IMSS^SS~CURP:VELG850312HDFRRN05^^^CURP^NI||Vera^Lopez^Gonzalo^Ernesto||19850312|M|||Calle Durango 1069 Col Roma Norte^^Ciudad De Mexico^DIF^06700^MX||5574140974^^^gonzalo.vera@live.com.mx||SPA|M|CAT|||VELG850312HDFRRN05||||Ciudad de Mexico|MX
PV1|1|I|MED-INT^402^A^HGZ_32||||28195^Paredes^Sandoval^Catalina^^^DRA|||MED||||ADM|||28195^Paredes^Sandoval^Catalina^^^DRA|IN||IMSS||||||||||||||||||||20250312084500
IN1|1|IMSS_ORD|IMSS|Instituto Mexicano del Seguro Social|Calle Morelos 2705 Col Narvarte^^Ciudad De Mexico^DIF^11000^MX|||||||||||||Vera^Lopez^Gonzalo^Ernesto|TITULAR|19850312|Av Tamaulipas 1140 Col Condesa^^Ciudad De Mexico^DIF^06140^MX
DG1|1|I10|I10^Hipertension esencial primaria^I10|||A
```

---

## 2. ADT^A03 - Patient discharge from traumatology

```
MSH|^~\&|IMSS_ECE|HGR_1_GDL|ADT_RCV|HGR_1|20250315163022||ADT^A03^ADT_A03|IMSS20250315163022002|P|2.5|||AL|NE||8859/1
EVN|A03|20250315163000|||DRNAVARRO^Pineda^Escobar^Francisco^^^DR
PID|1||NSS77806846797^^^IMSS^SS~CURP:GORL900415MJCNDR00^^^CURP^NI||Gonzalez^Rocha^Lorena^Patricia||19900415|F|||Calle Lopez Cotilla 4331 Col Americana^^Guadalajara^JAL^44160^MX||3397586542^^^lorena.gonzalez@yahoo.com.mx||SPA|S|CAT|||GORL900415MJCNDR00||||Guadalajara|MX
PV1|1|I|TRAUMA^201^B^HGR_1||||20811^Fuentes^Cardenas^Pedro^^^DR|||TRAUMA||||ADM|||20811^Fuentes^Cardenas^Pedro^^^DR|IN||IMSS||||||||||||||||||||20250310120000|20250315163000
DG1|1|I10|S72.0^Fractura del cuello del femur^I10|||A
DG1|2|I10|W01^Caida en el mismo nivel^I10|||A
```

---

## 3. ORM^O01 - Laboratory order for complete blood count

```
MSH|^~\&|IMSS_ECE|UMAE_25_MTY|LAB_SYS|UMAE_25|20250318091530||ORM^O01^ORM_O01|IMSS20250318091530003|P|2.5|||AL|NE||8859/1
PID|1||NSS94562633754^^^IMSS^SS~CURP:HERM780520HNLRDN27^^^CURP^NI||Herrera^Medina^Nestor^Pablo||19780520|M|||Av Constitucion 2570 Col Centro^^Monterrey^NLE^64000^MX||8132006565^^^nestor.herrera@outlook.com||SPA|M|CAT|||HERM780520HNLRDN27||||Monterrey|MX
PV1|1|O|CONS-EXT^12^A^UMAE_25||||92088^Aguirre^Trejo^Raquel^^^DRA|||MED||||REF|||92088^Aguirre^Trejo^Raquel^^^DRA|IN||IMSS
ORC|NW|ORD20250318001|||||^^^20250318093000^^R||20250318091530|DCORONA^Villegas^Zamora^Elena^^^DRA|||||UMAE_25
OBR|1|ORD20250318001||58410-2^CBC panel - Blood by Automated count^LN|||20250318091530||||N|||||92088^Aguirre^Trejo^Raquel^^^DRA|||||||||||^^^20250318093000^^R
```

---

## 4. ORU^R01 - Lab results for metabolic panel

```
MSH|^~\&|IMSS_ECE|HGZ_48_PUE|LAB_RCV|HGZ_48|20250320143200||ORU^R01^ORU_R01|IMSS20250320143200004|P|2.5|||AL|NE||8859/1
PID|1||NSS22616492266^^^IMSS^SS~CURP:SAMR950630MPLNRN70^^^CURP^NI||Sandoval^Mora^Renata^Estela||19950630|F|||Calle 3 Poniente 469 Col Centro^^Puebla^PUE^72000^MX||2226765142^^^renata.sandoval@yahoo.com.mx||SPA|S|CAT|||SAMR950630MPLNRN70||||Puebla|MX
PV1|1|O|LAB^01^A^HGZ_48||||24679^Ibarra^Dominguez^Leonardo^^^DR|||LAB
ORC|RE|ORD20250320005||||||^^^20250320120000^^R||20250320143200|EVILLAREAL^Negrete^Quiroz^Alejandro^^^DR
OBR|1|ORD20250320005||24323-8^Comprehensive metabolic 2000 panel - Serum or Plasma^LN|||20250320120000||||N|||||24679^Ibarra^Dominguez^Leonardo^^^DR
OBX|1|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||98|mg/dL|74-106|N|||F|||20250320140000
OBX|2|NM|3094-0^Urea nitrogen [Mass/volume] in Serum or Plasma^LN||15|mg/dL|6-20|N|||F|||20250320140000
OBX|3|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||0.9|mg/dL|0.7-1.3|N|||F|||20250320140000
OBX|4|NM|17861-6^Calcium [Mass/volume] in Serum or Plasma^LN||9.5|mg/dL|8.5-10.5|N|||F|||20250320140000
OBX|5|NM|2951-2^Sodium [Moles/volume] in Serum or Plasma^LN||140|mmol/L|136-145|N|||F|||20250320140000
OBX|6|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN||4.2|mmol/L|3.5-5.1|N|||F|||20250320140000
```

---

## 5. RDE^O11 - Pharmacy order for antihypertensive medication

```
MSH|^~\&|IMSS_ECE|HGZ_20_TIJ|FARM_SYS|HGZ_20|20250322101500||RDE^O11^RDE_O11|IMSS20250322101500005|P|2.5|||AL|NE||8859/1
PID|1||NSS50263566997^^^IMSS^SS~CURP:TOGR880215HBCRRB02^^^CURP^NI||Torres^Gastelum^Roberto^Cristobal||19880215|M|||Calle Constitucion 768 Col Zona Centro^^Tijuana^BC^22000^MX||6644462244^^^roberto.torres@outlook.com||SPA|M|CAT|||TOGR880215HBCRRB02||||Tijuana|MX
PV1|1|O|CONS-FAM^05^A^HGZ_20||||05367^Ornelas^Beltran^Alejandra^^^DRA|||MED||||REF
ORC|NW|RX20250322001|||||^^^20250322103000^^R||20250322101500|VMEJIA^Rojas^Garcia^Mariana^^^DRA|||||HGZ_20
RXO|1|C09AA02^Enalapril^ATC||10|mg||PO|BID|||||||30|TAB
RXR|PO^Oral^HL70162
RXE|^^^20250322103000^^R|C09AA02^Enalapril maleato 10mg^IMSS_CB|10||mg|TAB|PO|BID^Dos veces al dia||||||60|TAB||||||||||||N
```

---

## 6. ADT^A08 - Patient information update

```
MSH|^~\&|IMSS_ECE|HGZ_58_LEON|ADT_RCV|HGZ_58|20250325092100||ADT^A08^ADT_A08|IMSS20250325092100006|P|2.5|||AL|NE||8859/1
EVN|A08|20250325092000|||ADMIN01^Ocampo^Trejo^Carmen^^^LIC
PID|1||NSS71822825688^^^IMSS^SS~CURP:MUGB760812MGTRRN00^^^CURP^NI||Munoz^Garcia^Beatriz^Antonieta||19760812|F|||Av Madero 4027 Col Centro^^Leon^GTO^37000^MX||4774189954^^^beatriz.munoz@icloud.com||SPA|C|CAT|||MUGB760812MGTRRN00||||Leon|MX
PV1|1|O|CONS-EXT^08^A^HGZ_58||||48227^Estrada^Guerrero^Daniel^^^DR|||MED||||REF
NK1|1|Leyva^Nunez^Alicia^Susana|HUSB|Calle Obregon 3816 Col San Juan De Dios^^Leon^GTO^37200^MX|4775019376
```

---

## 7. ORM^O01 - Hemoglobin A1c order for diabetes monitoring

```
MSH|^~\&|IMSS_ECE|HGR_46_MER|LAB_SYS|HGR_46|20250327111200||ORM^O01^ORM_O01|IMSS20250327111200007|P|2.5|||AL|NE||8859/1
PID|1||NSS22702078609^^^IMSS^SS~CURP:RIAS700923MYNVLF07^^^CURP^NI||Rivera^Alfaro^Sofia^Guadalupe||19700923|F|||Calle 60 Num 3349 Col Centro^^Merida^YUC^97000^MX||9994258233^^^sofia.rivera@prodigy.net.mx||SPA|M|CAT|||RIAS700923MYNVLF07||||Merida|MX
PV1|1|O|CONS-FAM^03^A^HGR_46||||06226^Bravo^Orozco^Andres^^^DR|||MED||||REF
ORC|NW|ORD20250327002|||||^^^20250327130000^^R||20250327111200|JVARELA^Arroyo^Mora^Ricardo^^^DR|||||HGR_46
OBR|1|ORD20250327002||4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN|||20250327111200||||N|||||06226^Bravo^Orozco^Andres^^^DR|||||||||||^^^20250327130000^^R
DG1|1|I10|E11.9^Diabetes mellitus tipo 2 sin complicaciones^I10|||A
```

---

## 8. ORU^R01 - Lipid panel results with PDF report

```
MSH|^~\&|IMSS_ECE|HGZ_32_CDMX|LAB_RCV|HGZ_32|20250329154500||ORU^R01^ORU_R01|IMSS20250329154500008|P|2.5|||AL|NE||8859/1
PID|1||NSS83136610863^^^IMSS^SS~CURP:CALO820117HAGSNC32^^^CURP^NI||Castro^Leon^Octavio^Ramiro||19820117|M|||Av Aguascalientes 1118 Col Jardin^^Aguascalientes^AGS^20230^MX||4497158226^^^octavio.castro@icloud.com||SPA|M|CAT|||CALO820117HAGSNC32||||Ciudad de Mexico|MX
PV1|1|O|LAB^02^A^HGZ_32||||85679^Duarte^Vega^Valeria^^^DRA|||LAB
ORC|RE|ORD20250329003||||||^^^20250329130000^^R||20250329154500|APORTILLO^Loera^Reyes^Fernanda^^^DRA
OBR|1|ORD20250329003||24331-1^Lipid panel - Serum or Plasma^LN|||20250329130000||||N|||||85679^Duarte^Vega^Valeria^^^DRA
OBX|1|NM|2093-3^Cholesterol [Mass/volume] in Serum or Plasma^LN||210|mg/dL|<200|H|||F|||20250329150000
OBX|2|NM|2571-8^Triglyceride [Mass/volume] in Serum or Plasma^LN||180|mg/dL|<150|H|||F|||20250329150000
OBX|3|NM|2085-9^HDL Cholesterol [Mass/volume] in Serum or Plasma^LN||42|mg/dL|>40|N|||F|||20250329150000
OBX|4|NM|13457-7^LDL Cholesterol [Mass/volume] in Serum or Plasma^LN||132|mg/dL|<100|H|||F|||20250329150000
OBX|5|ED|PDF^Reporte de laboratorio perfil lipidico^AUSPDI|1|IMSS_ECE^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSA+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDQgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjIxMQolJUVPRgo=||||||F|||20250329154000
```

---

## 9. ORU^R01 - Complete blood count results

```
MSH|^~\&|IMSS_ECE|UMAE_25_MTY|LAB_RCV|UMAE_25|20250401083000||ORU^R01^ORU_R01|IMSS20250401083000009|P|2.5|||AL|NE||8859/1
PID|1||NSS94562633754^^^IMSS^SS~CURP:HERM780520HNLRDN27^^^CURP^NI||Herrera^Medina^Nestor^Pablo||19780520|M|||Av Constitucion 2570 Col Centro^^Monterrey^NLE^64000^MX||8132006565^^^nestor.herrera@outlook.com||SPA|M|CAT|||HERM780520HNLRDN27||||Monterrey|MX
PV1|1|O|LAB^01^A^UMAE_25||||92088^Aguirre^Trejo^Raquel^^^DRA|||LAB
ORC|RE|ORD20250318001||||||^^^20250318093000^^R||20250401083000|PCORDOVA^Cordero^Perez^Silvia^^^DRA
OBR|1|ORD20250318001||58410-2^CBC panel - Blood by Automated count^LN|||20250318093000||||N|||||92088^Aguirre^Trejo^Raquel^^^DRA
OBX|1|NM|6690-2^Leukocytes [#/volume] in Blood by Automated count^LN||7.2|10*3/uL|4.5-11.0|N|||F|||20250401080000
OBX|2|NM|789-8^Erythrocytes [#/volume] in Blood by Automated count^LN||4.8|10*6/uL|4.5-5.5|N|||F|||20250401080000
OBX|3|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||14.5|g/dL|13.5-17.5|N|||F|||20250401080000
OBX|4|NM|4544-3^Hematocrit [Volume Fraction] of Blood by Automated count^LN||43.2|%|40-54|N|||F|||20250401080000
OBX|5|NM|777-3^Platelets [#/volume] in Blood by Automated count^LN||245|10*3/uL|150-400|N|||F|||20250401080000
```

---

## 10. ADT^A04 - Outpatient registration for emergency department

```
MSH|^~\&|IMSS_ECE|HGZ_32_CDMX|ADT_RCV|HGZ_32|20250403201500||ADT^A04^ADT_A04|IMSS20250403201500010|P|2.5|||AL|NE||8859/1
EVN|A04|20250403201400|||ENFTRIAGE^Quiroga^Mireles^Gabriela^^^ENF
PID|1||NSS84463941824^^^IMSS^SS~CURP:ZAGM010705HDFVRG53^^^CURP^NI||Zavala^Garza^Miguel^Maximiliano||20010705|M|||Calle Bucareli 972 Col Juarez^^Ciudad De Mexico^DIF^06600^MX||5577714139^^^miguel.zavala@prodigy.net.mx||SPA|S|CAT|||ZAGM010705HDFVRG53||||Ciudad de Mexico|MX
PV1|1|E|URG^T1^A^HGZ_32||||31019^Campos^Acosta^Luis^^^DR|||URG||||URG|||31019^Campos^Acosta^Luis^^^DR|IN||IMSS||||||||||||||||||||20250403201400
DG1|1|I10|R10.4^Dolor abdominal no especificado^I10|||W
```

---

## 11. ORM^O01 - Urinalysis order

```
MSH|^~\&|IMSS_ECE|HGR_1_GDL|LAB_SYS|HGR_1|20250405101800||ORM^O01^ORM_O01|IMSS20250405101800011|P|2.5|||AL|NE||8859/1
PID|1||NSS57978958790^^^IMSS^SS~CURP:MARL860430MJCLDC43^^^CURP^NI||Martinez^Rubio^Lucia^Fernanda||19860430|F|||Av Paseo Tabasco 2302 Col Tabasco 2000^^Villahermosa^TAB^86035^MX||9931848995^^^lucia.martinez@live.com.mx||SPA|M|CAT|||MARL860430MJCLDC43||||Zapopan|MX
PV1|1|O|CONS-FAM^07^A^HGR_1||||94105^Oviedo^Quezada^Tomas^^^DR|||MED||||REF
ORC|NW|ORD20250405003|||||^^^20250405120000^^R||20250405101800|RBECERRA^Alvarez^Inurreta^Rafael^^^DR|||||HGR_1
OBR|1|ORD20250405003||24356-8^Urinalysis complete panel - Urine^LN|||20250405101800||||N|||||94105^Oviedo^Quezada^Tomas^^^DR|||||||||||^^^20250405120000^^R
DG1|1|I10|N39.0^Infeccion de vias urinarias^I10|||A
```

---

## 12. ORU^R01 - Thyroid function test results

```
MSH|^~\&|IMSS_ECE|HGZ_48_PUE|LAB_RCV|HGZ_48|20250408143500||ORU^R01^ORU_R01|IMSS20250408143500012|P|2.5|||AL|NE||8859/1
PID|1||NSS20493458035^^^IMSS^SS~CURP:NAVA750818MJCVRN00^^^CURP^NI||Navarro^Villanueva^Ana^Lucia||19750818|F|||Av Americas 2713 Col Providencia^^Guadalajara^JAL^44630^MX||3348405330^^^ana.navarro@yahoo.com.mx||SPA|D|CAT|||NAVA750818MJCVRN00||||Puebla|MX
PV1|1|O|ENDO^03^A^HGZ_48||||58884^Galvan^Ortiz^Teresa^^^DRA|||ENDO
ORC|RE|ORD20250408004||||||^^^20250408100000^^R||20250408143500|SCERVERA^Henriquez^Estrada^Paola^^^DRA
OBR|1|ORD20250408004||24348-5^Thyroid panel - Serum or Plasma^LN|||20250408100000||||N|||||58884^Galvan^Ortiz^Teresa^^^DRA
OBX|1|NM|3016-3^TSH [Units/volume] in Serum or Plasma^LN||2.8|mIU/L|0.4-4.0|N|||F|||20250408140000
OBX|2|NM|3026-2^T3 Free [Mass/volume] in Serum or Plasma^LN||3.1|pg/mL|2.3-4.2|N|||F|||20250408140000
OBX|3|NM|3024-7^T4 Free [Mass/volume] in Serum or Plasma^LN||1.2|ng/dL|0.8-1.8|N|||F|||20250408140000
```

---

## 13. ADT^A02 - Patient transfer between services

```
MSH|^~\&|IMSS_ECE|UMAE_25_MTY|ADT_RCV|UMAE_25|20250410160000||ADT^A02^ADT_A02|IMSS20250410160000013|P|2.5|||AL|NE||8859/1
EVN|A02|20250410155800|||DRMELENDEZ^Valencia^Jaramillo^Carlos^^^DR
PID|1||NSS26199520806^^^IMSS^SS~CURP:FIGO650310HNLGRM15^^^CURP^NI||Figueroa^Granillo^Oscar^Emiliano||19650310|M|||Av Garza Sada 3495 Col Contry^^Monterrey^NLE^64860^MX||8183781930^^^oscar.figueroa@correo.mx||SPA|M|CAT|||FIGO650310HNLGRM15||||Monterrey|MX
PV1|1|I|UCI^101^A^UMAE_25||||88064^Serrano^Chavez^Juan^^^DR|||UCI||||TRF|||88064^Serrano^Chavez^Juan^^^DR|IN||IMSS||||||||||||||||||||20250408120000
PV2|||MED-INT^402^A^UMAE_25
DG1|1|I10|I21.0^Infarto agudo del miocardio de pared anterior^I10|||A
```

---

## 14. RDE^O11 - Insulin prescription for diabetes patient

```
MSH|^~\&|IMSS_ECE|HGZ_58_LEON|FARM_SYS|HGZ_58|20250412093000||RDE^O11^RDE_O11|IMSS20250412093000014|P|2.5|||AL|NE||8859/1
PID|1||NSS22702078609^^^IMSS^SS~CURP:RIAS700923MYNVLF07^^^CURP^NI||Rivera^Alfaro^Sofia^Guadalupe||19700923|F|||Calle 60 Num 3349 Col Centro^^Merida^YUC^97000^MX||9994258233^^^sofia.rivera@prodigy.net.mx||SPA|M|CAT|||RIAS700923MYNVLF07||||Merida|MX
PV1|1|O|CONS-FAM^03^A^HGZ_58||||06226^Bravo^Orozco^Andres^^^DR|||MED||||REF
ORC|NW|RX20250412002|||||^^^20250412100000^^R||20250412093000|JVARELA^Arroyo^Mora^Ricardo^^^DR|||||HGZ_58
RXO|1|A10AE04^Insulina glargina^ATC||20|UI||SC|QD|||||||90|CART
RXR|SC^Subcutanea^HL70162
RXE|^^^20250412100000^^R|A10AE04^Insulina glargina 100 UI/mL^IMSS_CB|20||UI|CART|SC|QD^Una vez al dia||||||3|CART||||||||||||N
DG1|1|I10|E11.9^Diabetes mellitus tipo 2 sin complicaciones^I10|||A
```

---

## 15. ORU^R01 - HbA1c result with interpretation

```
MSH|^~\&|IMSS_ECE|HGR_46_MER|LAB_RCV|HGR_46|20250414110000||ORU^R01^ORU_R01|IMSS20250414110000015|P|2.5|||AL|NE||8859/1
PID|1||NSS22702078609^^^IMSS^SS~CURP:RIAS700923MYNVLF07^^^CURP^NI||Rivera^Alfaro^Sofia^Guadalupe||19700923|F|||Calle 60 Num 3349 Col Centro^^Merida^YUC^97000^MX||9994258233^^^sofia.rivera@prodigy.net.mx||SPA|M|CAT|||RIAS700923MYNVLF07||||Merida|MX
PV1|1|O|LAB^01^A^HGR_46||||06226^Bravo^Orozco^Andres^^^DR|||LAB
ORC|RE|ORD20250327002||||||^^^20250327130000^^R||20250414110000|JVARELA^Arroyo^Mora^Ricardo^^^DR
OBR|1|ORD20250327002||4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN|||20250327130000||||N|||||06226^Bravo^Orozco^Andres^^^DR
OBX|1|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN||7.8|%|<7.0|H|||F|||20250414100000
NTE|1||Control glucemico por debajo de meta. Se recomienda ajuste terapeutico.
```

---

## 16. ADT^A01 - Obstetric admission

```
MSH|^~\&|IMSS_ECE|HGO_4_CDMX|ADT_RCV|HGO_4|20250416221500||ADT^A01^ADT_A01|IMSS20250416221500016|P|2.5|||AL|NE||8859/1
EVN|A01|20250416221400|||DRACORTES^Anaya^Ochoa^Laura^^^DRA
PID|1||NSS78211796667^^^IMSS^SS~CURP:ROMD950812MSLBRN60^^^CURP^NI||Robledo^Miranda^Diana^Isabela||19950812|F|||Calle Angel Flores 3706 Col Centro^^Culiacan^SIN^80000^MX||6672241668^^^diana.robledo@outlook.com||SPA|M|CAT|||ROMD950812MSLBRN60||||Ciudad de Mexico|MX
PV1|1|I|OBST^301^A^HGO_4||||85436^Lozano^Leyva^Pilar^^^DRA|||OBST||||ADM|||85436^Lozano^Leyva^Pilar^^^DRA|IN||IMSS||||||||||||||||||||20250416221400
DG1|1|I10|O80^Parto unico espontaneo^I10|||A
DG1|2|I10|Z37.0^Nacido vivo unico^I10|||A
```

---

## 17. ORM^O01 - Prenatal screening panel

```
MSH|^~\&|IMSS_ECE|HGO_4_CDMX|LAB_SYS|HGO_4|20250418091000||ORM^O01^ORM_O01|IMSS20250418091000017|P|2.5|||AL|NE||8859/1
PID|1||NSS35425925960^^^IMSS^SS~CURP:GUTA880315MJCRRL87^^^CURP^NI||Guerrero^Tapia^Andrea^Teresa||19880315|F|||Av Vallarta 1817 Col Arcos Vallarta^^Guadalajara^JAL^44130^MX||3399527372^^^andrea.guerrero@hotmail.com||SPA|M|CAT|||GUTA880315MJCRRL87||||Ciudad de Mexico|MX
PV1|1|O|OBST-EXT^02^A^HGO_4||||75184^Cisneros^Barraza^Cecilia^^^DRA|||OBST||||REF
ORC|NW|ORD20250418005|||||^^^20250418120000^^R||20250418091000|CALARCON^Medina^Magana^Martha^^^DRA|||||HGO_4
OBR|1|ORD20250418005||21198-7^Prenatal screening panel^LN|||20250418091000||||N|||||75184^Cisneros^Barraza^Cecilia^^^DRA|||||||||||^^^20250418120000^^R
DG1|1|I10|Z34.0^Supervision de primer embarazo normal^I10|||A
```

---

## 18. ORU^R01 - COVID-19 PCR result

```
MSH|^~\&|IMSS_ECE|HGZ_20_TIJ|LAB_RCV|HGZ_20|20250420153000||ORU^R01^ORU_R01|IMSS20250420153000018|P|2.5|||AL|NE||8859/1
PID|1||NSS04763081676^^^IMSS^SS~CURP:PELG920612HOCRRR17^^^CURP^NI||Perez^Luna^German^Enrique||19920612|M|||Calle Macedonio Alcala 2647 Col Centro^^Oaxaca^OAX^68000^MX||9515163798^^^german.perez@icloud.com||SPA|S|CAT|||PELG920612HOCRRR17||||Tijuana|MX
PV1|1|O|RESP^01^A^HGZ_20||||94575^Villarreal^Velasco^Gabriel^^^DR|||RESP
ORC|RE|ORD20250420006||||||^^^20250420100000^^R||20250420153000|HSALGADO^Cabrera^Sanchez^Jesus^^^DR
OBR|1|ORD20250420006||94500-6^SARS-CoV-2 RNA [Presence] in Respiratory specimen by NAA with probe detection^LN|||20250420100000||||N|||||94575^Villarreal^Velasco^Gabriel^^^DR
OBX|1|CWE|94500-6^SARS-CoV-2 RNA [Presence] in Respiratory specimen^LN||260415000^Not detected^SCT||Negative|N|||F|||20250420150000
```

---

## 19. ORU^R01 - Lab results with scanned requisition image

```
MSH|^~\&|IMSS_ECE|HGZ_32_CDMX|LAB_RCV|HGZ_32|20250422112000||ORU^R01^ORU_R01|IMSS20250422112000019|P|2.5|||AL|NE||8859/1
PID|1||NSS93759830414^^^IMSS^SS~CURP:AGCA770225HMCGRN16^^^CURP^NI||Aguilar^Coronado^Antonio^Rafael||19770225|M|||Av Morelos Sur 2280 Col Chapultepec^^Morelia^MIC^58260^MX||4435882343^^^antonio.aguilar@live.com.mx||SPA|M|CAT|||AGCA770225HMCGRN16||||Ciudad de Mexico|MX
PV1|1|O|LAB^03^A^HGZ_32||||20070^Noriega^Galindo^Veronica^^^DRA|||LAB
ORC|RE|ORD20250422007||||||^^^20250422080000^^R||20250422112000|KACUNA^Rodriguez^Duran^Esther^^^DRA
OBR|1|ORD20250422007||2339-0^Glucose [Mass/volume] in Blood^LN|||20250422080000||||N|||||20070^Noriega^Galindo^Veronica^^^DRA
OBX|1|NM|2339-0^Glucose [Mass/volume] in Blood^LN||112|mg/dL|70-100|H|||F|||20250422110000
OBX|2|ED|IMG^Solicitud de laboratorio escaneada^LOCAL|1|IMSS_ECE^IMAGE^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAyADIDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQ=||||||F|||20250422110000
```

---

## 20. ADT^A28 - New patient registration in IMSS system

```
MSH|^~\&|IMSS_ECE|UMF_12_CDMX|ADT_RCV|UMF_12|20250424080000||ADT^A28^ADT_A28|IMSS20250424080000020|P|2.5|||AL|NE||8859/1
EVN|A28|20250424075900|||ADMIN02^Saucedo^Sotelo^Isabel^^^LIC
PID|1||NSS45404173041^^^IMSS^SS~CURP:BAHJ050910HDFRRV10^^^CURP^NI||Barrera^Huerta^Javier^Nicolas||20050910|M|||Calle Tlalpan 2519 Col Portales^^Ciudad De Mexico^DIF^03300^MX||5546456050^^^javier.barrera@live.com.mx||SPA|S|CAT|||BAHJ050910HDFRRV10||||Ciudad de Mexico|MX
PV1|1|O|REG^01^A^UMF_12||||50190^Cuellar^Luna^Leticia^^^DRA|||MED||||REF
IN1|1|IMSS_ORD|IMSS|Instituto Mexicano del Seguro Social|Calle Morelos 2705 Col Narvarte^^Ciudad De Mexico^DIF^11000^MX|||||||||||||Barrera^Huerta^Javier^Nicolas|BEN_PADRE|20050910|Av Insurgentes Sur 1140 Col Del Valle^^Ciudad De Mexico^DIF^03100^MX
NK1|1|Trujillo^Mendoza^Ignacio^Eduardo|FTH|Av Xola 3265 Col Narvarte^^Ciudad De Mexico^DIF^03020^MX|5547182212
```
