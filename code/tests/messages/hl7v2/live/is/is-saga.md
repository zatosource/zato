# Saga (Helix Health) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Inpatient admission

```
MSH|^~\&|SAGA|LANDSPITALI|HEILSUVERA|EMBLA|20260301091500||ADT^A01|MSG00001|P|2.4|||AL|NE||8859/1
EVN|A01|20260301091500
PID|1||1102864507^^^SAGA^PI||Vilbergsson^Hákon^^^Hr||19860211|M|||Lautasmári 14^^Kópavogur^^201^IS||^PRN^PH^^354^5671984|^WPN^PH^^354^5672105|||S|||1102864507
NK1|1|Brynjarsdóttir^Ásdís^^|SPO|Lautasmári 14^^Kópavogur^^201^IS|^PRN^PH^^354^5671985
PV1|1|I|12A^201^1^^^LANDSPITALI||||38462^Hróðmarsson^Jökull^^^Dr|||MED||||7|||38462^Hróðmarsson^Jökull^^^Dr|IP||||||||||||||||||LANDSPITALI|||20260301091500
PV2|||^Lungnabólga|||||||1
IN1|1|TR01^Sjúkratryggingar Íslands|SI001|Sjúkratryggingar Íslands|Laugavegur 114^^Reykjavík^^105^IS
```

---

## 2. ADT^A02 - Patient transfer

```
MSH|^~\&|SAGA|LANDSPITALI|RAFÖRNINN|LANDSPITALI|20260302140000||ADT^A02|MSG00002|P|2.4|||AL|NE||8859/1
EVN|A02|20260302140000
PID|1||1102864507^^^SAGA^PI||Vilbergsson^Hákon^^^Hr||19860211|M|||Lautasmári 14^^Kópavogur^^201^IS||^PRN^PH^^354^5671984
PV1|1|I|ICU^305^1^^^LANDSPITALI||||38462^Hróðmarsson^Jökull^^^Dr|||MED||||7|||38462^Hróðmarsson^Jökull^^^Dr|IP||||||||||||||||||LANDSPITALI|||20260301091500
PV2|||^Bráðamóttaka - flutningur á gjörgæslu
```

---

## 3. ADT^A03 - Discharge

```
MSH|^~\&|SAGA|LANDSPITALI|HEILSUVERA|EMBLA|20260310100000||ADT^A03|MSG00003|P|2.4|||AL|NE||8859/1
EVN|A03|20260310100000
PID|1||1102864507^^^SAGA^PI||Vilbergsson^Hákon^^^Hr||19860211|M|||Lautasmári 14^^Kópavogur^^201^IS||^PRN^PH^^354^5671984
PV1|1|I|12A^201^1^^^LANDSPITALI||||38462^Hróðmarsson^Jökull^^^Dr|||MED||||7|||38462^Hróðmarsson^Jökull^^^Dr|IP||||||||||||||||01|LANDSPITALI|||20260301091500|||20260310100000
DG1|1|I10|I10^Háþrýstingur^ICD-10||20260310
```

---

## 4. ADT^A04 - Outpatient registration

```
MSH|^~\&|SAGA|HEILSUG_EFSTALEITI|RAFÖRNINN|EMBLA|20260315083000||ADT^A04|MSG00004|P|2.4|||AL|NE||8859/1
EVN|A04|20260315083000
PID|1||1607912438^^^SAGA^PI||Reynisdóttir^Edda^^^Frú||19910716|F|||Eiðsmýri 6^^Mosfellsbær^^270^IS||^PRN^PH^^354^5663912|^WPN^PH^^354^5663913|||G|||1607912438
PV1|1|O|EFST^102^1^^^HEILSUG_EFSTALEITI||||42781^Marteinsdóttir^Auðbjörg^^^Dr|||GEN||||1|||42781^Marteinsdóttir^Auðbjörg^^^Dr|OP||||||||||||||||||HEILSUG_EFSTALEITI|||20260315083000
PV2|||^Reglulegt eftirlit
```

---

## 5. ADT^A08 - Update patient info

```
MSH|^~\&|SAGA|LANDSPITALI|HEILSUVERA|EMBLA|20260318120000||ADT^A08|MSG00005|P|2.4|||AL|NE||8859/1
EVN|A08|20260318120000
PID|1||2407753912^^^SAGA^PI||Þrastardóttir^Hekla^^^Frú||19750724|F|||Sólvallagata 30^^Reykjavík^^101^IS||^PRN^PH^^354^5614032|^WPN^PH^^354^5614099||M||2407753912
PV1|1|O|OUT^100^1^^^LANDSPITALI||||38462^Hróðmarsson^Jökull^^^Dr|||MED||||1|||38462^Hróðmarsson^Jökull^^^Dr|OP
```

---

## 6. ADT^A31 - Update patient demographics

```
MSH|^~\&|SAGA|THJODSKRA|HEILSUVERA|EMBLA|20260320090000||ADT^A31|MSG00006|P|2.4|||AL|NE||8859/1
EVN|A31|20260320090000
PID|1||0509671382^^^SAGA^PI||Klemensdóttir^Aldís^^^Frú||19670905|F|||Glerárgata 18^^Akureyri^^600^IS||^PRN^PH^^354^4623804|^WPN^PH^^354^4623805||W||0509671382
```

---

## 7. ADT^A40 - Merge patient

```
MSH|^~\&|SAGA|LANDSPITALI|HEILSUVERA|EMBLA|20260322110000||ADT^A40|MSG00007|P|2.4|||AL|NE||8859/1
EVN|A40|20260322110000
PID|1||2407753912^^^SAGA^PI||Þrastardóttir^Hekla^^^Frú||19750724|F|||Sólvallagata 30^^Reykjavík^^101^IS||^PRN^PH^^354^5614032
MRG|9907753500^^^SAGA^PI|
PV1|1|O|OUT^100^1^^^LANDSPITALI
```

---

## 8. ORM^O01 - Lab order

```
MSH|^~\&|SAGA|LANDSPITALI|FLEXLAB|LANDSPITALI_LAB|20260401080000||ORM^O01|MSG00008|P|2.4|||AL|NE||8859/1
PID|1||1810823671^^^SAGA^PI||Egilsdóttir^Bryndís^^^Frú||19821018|F|||Hringbraut 88^^Reykjavík^^107^IS||^PRN^PH^^354^5538204
PV1|1|O|GÖNGU^200^1^^^LANDSPITALI||||51234^Vilhjálmsson^Sturla^^^Dr|||MED||||1|||51234^Vilhjálmsson^Sturla^^^Dr|OP
ORC|NW|ORD20260401001|||||^^^20260401080000^^R||20260401080000|51234^Vilhjálmsson^Sturla^^^Dr||51234^Vilhjálmsson^Sturla^^^Dr|LANDSPITALI
OBR|1|ORD20260401001||CBC^Blóðhagur^L|||20260401080000||||N|||||51234^Vilhjálmsson^Sturla^^^Dr|||||||||||^^^20260401080000^^R
```

---

## 9. ORM^O01 - Radiology order

```
MSH|^~\&|SAGA|LANDSPITALI|RIS_PACS|LANDSPITALI_RAD|20260402093000||ORM^O01|MSG00009|P|2.4|||AL|NE||8859/1
PID|1||1408952378^^^SAGA^PI||Friðriksson^Andri^^^Hr||19950814|M|||Reynimelur 4^^Reykjavík^^107^IS||^PRN^PH^^354^5719306
PV1|1|I|BRÁÐA^401^1^^^LANDSPITALI||||60123^Sturlaugsdóttir^Ragnheiður^^^Dr|||ORT||||7|||60123^Sturlaugsdóttir^Ragnheiður^^^Dr|IP||||||||||||||||||LANDSPITALI|||20260402090000
ORC|NW|RAD20260402001|||||^^^20260402093000^^S||20260402093000|60123^Sturlaugsdóttir^Ragnheiður^^^Dr||60123^Sturlaugsdóttir^Ragnheiður^^^Dr|LANDSPITALI
OBR|1|RAD20260402001||XRCHEST^Röntgenmynd af brjóstkassa^RAD|||20260402093000||||N|||||60123^Sturlaugsdóttir^Ragnheiður^^^Dr||||||||||^^^20260402093000^^S
```

---

## 10. ORU^R01 - Lab result (CBC)

```
MSH|^~\&|FLEXLAB|LANDSPITALI_LAB|SAGA|LANDSPITALI|20260401143000||ORU^R01|MSG00010|P|2.4|||AL|NE||8859/1
PID|1||1810823671^^^SAGA^PI||Egilsdóttir^Bryndís^^^Frú||19821018|F|||Hringbraut 88^^Reykjavík^^107^IS||^PRN^PH^^354^5538204
PV1|1|O|GÖNGU^200^1^^^LANDSPITALI||||51234^Vilhjálmsson^Sturla^^^Dr
ORC|RE|ORD20260401001||||||^^^20260401080000^^R||20260401143000
OBR|1|ORD20260401001||CBC^Blóðhagur^L|||20260401080000|||||||20260401143000|Blood|51234^Vilhjálmsson^Sturla^^^Dr
OBX|1|NM|WBC^Hvít blóðkorn^L||6.8|10*9/L|4.0-11.0|N|||F
OBX|2|NM|RBC^Rauð blóðkorn^L||4.52|10*12/L|3.80-5.50|N|||F
OBX|3|NM|HGB^Blóðrauði^L||138|g/L|115-165|N|||F
OBX|4|NM|HCT^Blóðþurrð^L||0.41|L/L|0.35-0.47|N|||F
OBX|5|NM|PLT^Blóðflögur^L||245|10*9/L|150-400|N|||F
OBX|6|NM|MCV^Meðalrúmmál^L||90.7|fL|80.0-100.0|N|||F
```

---

## 11. ORU^R01 - Chemistry result

```
MSH|^~\&|FLEXLAB|LANDSPITALI_LAB|SAGA|LANDSPITALI|20260403160000||ORU^R01|MSG00011|P|2.4|||AL|NE||8859/1
PID|1||2407753912^^^SAGA^PI||Þrastardóttir^Hekla^^^Frú||19750724|F|||Sólvallagata 30^^Reykjavík^^101^IS||^PRN^PH^^354^5614032
PV1|1|O|GÖNGU^200^1^^^LANDSPITALI||||38462^Hróðmarsson^Jökull^^^Dr
ORC|RE|ORD20260403001||||||^^^20260403080000^^R||20260403160000
OBR|1|ORD20260403001||CHEM^Lífefnafræði^L|||20260403080000|||||||20260403160000|Blood|38462^Hróðmarsson^Jökull^^^Dr
OBX|1|NM|GLU^Glúkósi^L||5.4|mmol/L|3.9-6.1|N|||F
OBX|2|NM|CREA^Kreatínín^L||88|umol/L|60-110|N|||F
OBX|3|NM|UREA^Þvagefni^L||6.2|mmol/L|2.5-7.5|N|||F
OBX|4|NM|NA^Natríum^L||141|mmol/L|136-145|N|||F
OBX|5|NM|K^Kalíum^L||4.3|mmol/L|3.5-5.1|N|||F
OBX|6|NM|ALT^Alanín amínótransferasi^L||28|U/L|10-45|N|||F
OBX|7|NM|CRP^C-reactive prótein^L||3.2|mg/L|0.0-5.0|N|||F
```

---

## 12. ORU^R01 - Microbiology result

```
MSH|^~\&|FLEXLAB|LANDSPITALI_LAB|SAGA|LANDSPITALI|20260405110000||ORU^R01|MSG00012|P|2.4|||AL|NE||8859/1
PID|1||0509671382^^^SAGA^PI||Klemensdóttir^Aldís^^^Frú||19670905|F|||Glerárgata 18^^Akureyri^^600^IS||^PRN^PH^^354^4623804
PV1|1|I|SMIT^502^1^^^SAK||||72345^Bjarnfreðsson^Tómas^^^Dr|||MED||||7|||72345^Bjarnfreðsson^Tómas^^^Dr|IP||||||||||||||||||SAK
ORC|RE|ORD20260404001||||||^^^20260404100000^^R||20260405110000
OBR|1|ORD20260404001||BLDCX^Blóðræktun^L|||20260404100000|||||||20260405110000|Blood|72345^Bjarnfreðsson^Tómas^^^Dr
OBX|1|ST|ORGANISM^Ræktun^L||Staphylococcus aureus||||||F
OBX|2|ST|SUSCEPT^Næmi - Oxacillín^L||S||||||F
OBX|3|ST|SUSCEPT^Næmi - Vancomycín^L||S||||||F
OBX|4|ST|SUSCEPT^Næmi - Gentamycín^L||S||||||F
OBX|5|ST|SUSCEPT^Næmi - Clindamycín^L||S||||||F
OBX|6|NM|MIC^MIC Oxacillín^L||0.5|mg/L|||||F
```

---

## 13. ORU^R01 - Lab result with base64 ED OBX (PDF lab report)

```
MSH|^~\&|FLEXLAB|LANDSPITALI_LAB|SAGA|LANDSPITALI|20260406090000||ORU^R01|MSG00013|P|2.4|||AL|NE||8859/1
PID|1||1607912438^^^SAGA^PI||Reynisdóttir^Edda^^^Frú||19910716|F|||Eiðsmýri 6^^Mosfellsbær^^270^IS||^PRN^PH^^354^5663912
PV1|1|O|GÖNGU^200^1^^^LANDSPITALI||||42781^Marteinsdóttir^Auðbjörg^^^Dr
ORC|RE|ORD20260406001||||||^^^20260406070000^^R||20260406090000
OBR|1|ORD20260406001||CBC^Blóðhagur^L|||20260406070000|||||||20260406090000|Blood|42781^Marteinsdóttir^Auðbjörg^^^Dr
OBX|1|NM|WBC^Hvít blóðkorn^L||7.2|10*9/L|4.0-11.0|N|||F
OBX|2|NM|HGB^Blóðrauði^L||142|g/L|115-165|N|||F
OBX|3|NM|PLT^Blóðflögur^L||198|10*9/L|150-400|N|||F
OBX|4|ED|PDF^Rannsóknaskýrsla||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE3MSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjIyOQolJUVPRgo=||||||F
```

---

## 14. SIU^S12 - Schedule appointment

```
MSH|^~\&|SAGA|LANDSPITALI|RAFÖRNINN|LANDSPITALI|20260410100000||SIU^S12|MSG00014|P|2.4|||AL|NE||8859/1
SCH|APT20260420001|APT20260420001|||ROUTINE|ROUTINE^Reglulegt^HL70276|15^MIN|^^15^20260420093000^20260420094500|||||51234^Vilhjálmsson^Sturla^^^Dr|^PRN^PH^^354^5538204||51234^Vilhjálmsson^Sturla^^^Dr|GÖNGU^200^1^^^LANDSPITALI|ROUTINE|APT20260420001|||BOOKED
PID|1||1810823671^^^SAGA^PI||Egilsdóttir^Bryndís^^^Frú||19821018|F|||Hringbraut 88^^Reykjavík^^107^IS||^PRN^PH^^354^5538204
PV1|1|O|GÖNGU^200^1^^^LANDSPITALI||||51234^Vilhjálmsson^Sturla^^^Dr
RGS|1
AIS|1|A|EFTIRLITSKOMP^Eftirlitskompa^L|20260420093000|15|MIN
AIG|1|A|51234^Vilhjálmsson^Sturla^^^Dr
AIL|1|A|GÖNGU^200^1^^^LANDSPITALI
```

---

## 15. SIU^S14 - Modify appointment

```
MSH|^~\&|SAGA|LANDSPITALI|RAFÖRNINN|LANDSPITALI|20260412140000||SIU^S14|MSG00015|P|2.4|||AL|NE||8859/1
SCH|APT20260420001|APT20260420001|||ROUTINE|ROUTINE^Reglulegt^HL70276|15^MIN|^^15^20260422100000^20260422101500|||||51234^Vilhjálmsson^Sturla^^^Dr|^PRN^PH^^354^5538204||51234^Vilhjálmsson^Sturla^^^Dr|GÖNGU^200^1^^^LANDSPITALI|ROUTINE|APT20260420001|||BOOKED
PID|1||1810823671^^^SAGA^PI||Egilsdóttir^Bryndís^^^Frú||19821018|F|||Hringbraut 88^^Reykjavík^^107^IS||^PRN^PH^^354^5538204
PV1|1|O|GÖNGU^200^1^^^LANDSPITALI||||51234^Vilhjálmsson^Sturla^^^Dr
RGS|1
AIS|1|A|EFTIRLITSKOMP^Eftirlitskompa^L|20260422100000|15|MIN
AIG|1|A|51234^Vilhjálmsson^Sturla^^^Dr
AIL|1|A|GÖNGU^200^1^^^LANDSPITALI
```

---

## 16. MDM^T02 - Document notification with content

```
MSH|^~\&|SAGA|LANDSPITALI|HEILSUVERA|EMBLA|20260415110000||MDM^T02|MSG00016|P|2.4|||AL|NE||8859/1
EVN|T02|20260415110000
PID|1||1102864507^^^SAGA^PI||Vilbergsson^Hákon^^^Hr||19860211|M|||Lautasmári 14^^Kópavogur^^201^IS||^PRN^PH^^354^5671984
PV1|1|I|12A^201^1^^^LANDSPITALI||||38462^Hróðmarsson^Jökull^^^Dr
TXA|1|UT^Útskriftarbréf|TX|20260415110000|38462^Hróðmarsson^Jökull^^^Dr||20260415110000|20260415110000||38462^Hróðmarsson^Jökull^^^Dr|DOC20260415001||||||AU
OBX|1|TX|ÚTSKRIFT^Útskriftarbréf^L||Sjúklingur lagðist inn 01.03.2026 vegna lungnabólgu.~Meðferð: Amoxicillín 500mg x 3 í 7 daga.~Ástand við útskrift: Gott, hitalaus í 48 klst.~Eftirfylgni: Endurkomukompa á göngudeild eftir 2 vikur.||||||F
```

---

## 17. ORU^R01 - Pathology result with base64 ED OBX (PDF pathology report)

```
MSH|^~\&|FLEXLAB|LANDSPITALI_PATH|SAGA|LANDSPITALI|20260418140000||ORU^R01|MSG00017|P|2.4|||AL|NE||8859/1
PID|1||1006701825^^^SAGA^PI||Hauksdóttir^Salka^^^Frú||19700610|F|||Stigahlíð 22^^Reykjavík^^105^IS||^PRN^PH^^354^5589016
PV1|1|O|MEINAF^300^1^^^LANDSPITALI||||83456^Tryggvason^Reynar^^^Dr|||PATH||||1|||83456^Tryggvason^Reynar^^^Dr|OP
ORC|RE|ORD20260416001||||||^^^20260416100000^^R||20260418140000
OBR|1|ORD20260416001||SURG_PATH^Vefjameinafræði^L|||20260416100000|||||||20260418140000|Tissue|83456^Tryggvason^Reynar^^^Dr
OBX|1|TX|MACRO^Stórsýn^L||Húðsýni, 1.2 x 0.8 cm, brúnleitt||||||F
OBX|2|TX|MICRO^Smásjárskoðun^L||Basalfrumukrabbamein, hnútótt gerð, skurðbrúnir fríar||||||F
OBX|3|TX|DIAG^Greining^L||Basalfrumukrabbamein (BCC), hnútótt gerð. Skurðbrúnir fríar.||||||F
OBX|4|ED|PDF^Vefjameinafræðiskýrsla||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSAtPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTcxIDAwMDAwIG4gCjAwMDAwMDAyOTUgMDAwMDAgbiAKdHJhaWxlcgo8PAovU2l6ZSA1Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgozOTAKJSVFT0YK||||||F
```

---

## 18. ADT^A01 - Emergency admission

```
MSH|^~\&|SAGA|LANDSPITALI|HEILSUVERA|EMBLA|20260420223000||ADT^A01|MSG00018|P|2.4|||AL|NE||8859/1
EVN|A01|20260420223000
PID|1||0901002174^^^SAGA^PI||Brandsson^Höður^^^Hr||20000109|M|||Furuhjalli 11^^Kópavogur^^200^IS||^PRN^PH^^354^5429316
NK1|1|Brandsdóttir^Þórgunnur^^|MTH|Furuhjalli 11^^Kópavogur^^200^IS|^PRN^PH^^354^5429317
PV1|1|E|BRÁÐA^ER01^1^^^LANDSPITALI||||91234^Sigtryggsdóttir^Bára^^^Dr|||ER||||7|||91234^Sigtryggsdóttir^Bára^^^Dr|ER||||||||||||||||||LANDSPITALI|||20260420223000
PV2|||^Bráð kviðverkir
DG1|1|I10|R10.0^Bráðir kviðverkir^ICD-10||20260420||A
```

---

## 19. ORM^O01 - Medication order

```
MSH|^~\&|SAGA|LANDSPITALI|LYFJAVAKI|LANDSPITALI_APO|20260421080000||ORM^O01|MSG00019|P|2.4|||AL|NE||8859/1
PID|1||0901002174^^^SAGA^PI||Brandsson^Höður^^^Hr||20000109|M|||Furuhjalli 11^^Kópavogur^^200^IS||^PRN^PH^^354^5429316
PV1|1|I|BRÁÐA^ER01^1^^^LANDSPITALI||||91234^Sigtryggsdóttir^Bára^^^Dr|||ER||||7|||91234^Sigtryggsdóttir^Bára^^^Dr|ER
ORC|NW|RX20260421001|||||^^^20260421080000^^R||20260421080000|91234^Sigtryggsdóttir^Bára^^^Dr||91234^Sigtryggsdóttir^Bára^^^Dr|LANDSPITALI
RXO|PARA500^Paracetamól 500mg^LYFSKRA||500|mg||||||1|tafla||91234^Sigtryggsdóttir^Bára^^^Dr
RXR|PO^Til inntöku^HL70162
RXE|^^^20260421080000^20260423080000^^R|PARA500^Paracetamól 500mg^LYFSKRA|500|mg||||||||1|tafla|6^klst|||||||||||||||91234^Sigtryggsdóttir^Bára^^^Dr
```

---

## 20. ORU^R01 - Blood gas result

```
MSH|^~\&|FLEXLAB|LANDSPITALI_LAB|SAGA|LANDSPITALI|20260421093000||ORU^R01|MSG00020|P|2.4|||AL|NE||8859/1
PID|1||0901002174^^^SAGA^PI||Brandsson^Höður^^^Hr||20000109|M|||Furuhjalli 11^^Kópavogur^^200^IS||^PRN^PH^^354^5429316
PV1|1|E|BRÁÐA^ER01^1^^^LANDSPITALI||||91234^Sigtryggsdóttir^Bára^^^Dr
ORC|RE|ORD20260421002||||||^^^20260421090000^^S||20260421093000
OBR|1|ORD20260421002||ABG^Blóðgas^L|||20260421090000|||||||20260421093000|Arterial Blood|91234^Sigtryggsdóttir^Bára^^^Dr
OBX|1|NM|PH^pH^L||7.38||7.35-7.45|N|||F
OBX|2|NM|PCO2^pCO2^L||5.1|kPa|4.7-6.0|N|||F
OBX|3|NM|PO2^pO2^L||11.2|kPa|10.0-13.3|N|||F
OBX|4|NM|HCO3^Bíkarbónat^L||24.1|mmol/L|22.0-26.0|N|||F
OBX|5|NM|BE^Base excess^L||-0.5|mmol/L|-2.0-2.0|N|||F
OBX|6|NM|LACT^Laktat^L||1.2|mmol/L|0.5-2.2|N|||F
OBX|7|NM|SAO2^Súrefnismettun^L||97.2|%|95.0-99.0|N|||F
```
