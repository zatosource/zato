# Comarch Optimed NXT - real HL7v2 ER7 messages

---

## 1. ORM^O01 - new radiology order (chest X-ray)

```
MSH|^~\&|SZPM||SYZ1||20030526103638||ORM^O01|SZ01F28|T|2.3|||||PL|CP1250|PL
PID|1||75721||Olejniczak^Katarzyna||19850411|F|||,^^Toruń
PV1|1|I|OD13
IN1|1||02R
ORC|NW|1115610|||||^^^^^R|1115610|20030526103100|||175^Czarnecka Grażyna|||||OD13
OBR|1|1115610||RTG||||||||||||175^Głowacka Halina||||||||HL7|||||1115610
NTE|1|P|klatki piersiowej
```

---

## 2. ORM^O01 - laboratory order with specimen collection

```
MSH|^~\&|SZPM||LABHL7||20070716112609||ORM^O01|1E273|P|2.3|||AL||PL|CP1250|PL
PID|1|68032000001|2121||Jasińska^Weronika||19680320|F|||^^Białystok
PV1|1|O|PPOB||||||||||||||||4735.5418
IN1|1||12
ORC|NW|54942|||||^^^20070716112602^^R||20070716112504|||49999^Zawadzka^Dorota|||||PPOB^Punkt pobrań
OBR|1|54942||OB^Odczyn opadania krwinek czerwonych|||20070716112504|||2^PIK^PIK||||20070716112602|KP&Krew pełna&SZPM|49999^Zawadzka^Dorota||800002981||||||LHL7
```

---

## 3. ORM^O01 - order status update (angiography, in-process)

```
MSH|^~\&|SZPM||PRDIAG||20120123125736||ORM^O01|SZ23592|P|2.3|||AL|AL|PL||PL
PID|1||1782^^^SZPM||Kołodziej^Zbigniew||19530101|M|||
PV1|1|I|WEW1^^^^^^^ODC2||||||||||||||||2341.3641|||||||||||||||||||||||||20040201232500
IN1|1||099
ORC|RF|85770|||IP||^^^20120123094200^^R|85770|20120123094200|||2^PIK^PIK^^^^^^^^^^SZPM|ODC2||||WEW1^Oddział wewnętrzny
OBR|1|85770||XA.AORTIC^Angiografia|||20120123094200||||||I20.0|20120123094200|&&|2^PIK^PIK|||5000101|||||ALT|||||85770
```

---

## 4. ORU^R01 - radiology result (esophageal study, formatted text)

```
MSH|^~\&|SYZ1||SZPM||200405261448||ORU^R01|VSZ01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR|1|1115610||RTG|||200405261433||||||||||||||||||F|
OBX|1|FT|||Przełyk w całości poszerzony.\.br\Środek kontrastowy przez wpust przedostaje się wąską strugą.\.br\radiolog Witkowski Andrzej||||||F|||200305261038|
```

---

## 5. ORU^R01 - laboratory result (ESR, coded numeric)

```
MSH|^~\&|LAB||SZPM||200405261448||ORU^R01|LW01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR||1115610||OB^Odczyn Biernackiego^SZPM|||200405261433||||||||||||||||||F|
OBX|1|CE|OB^Odczyn Biernackiego^SZPM||15|mm/h|0-12|H||||F|||200305261038|
```

---

## 6. ORU^R01 - complete blood count (CBC/morphology, multi-OBX)

```
MSH|^~\&|LAB||SZPM||200405261448||ORU^R01|LW01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR|1|1115610||MORF|||200405261433||||||||||||||||||F|
OBX|1|CE|WBC^Leukocyty^SZPM||8.57|m/uL|4.80-10.80|||||F|||200505261038|
OBX|2|CE|RBC^Erytrocyty^SZPM||6.65|m/uL|4.20-5.40|H||||F|||200505261038|
OBX|3|CE|HGB^Hemoglobina^SZPM||14.2|g/dL|12.0-16.0|||||F|||200505261038|
```

---

## 7. ORU^R01 - lab result with URL reference (image link)

```
MSH|^~\&|SYZ1||SZPM||200405261448||ORU^R01|VSZ01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR|1|1115610||RTG|||200405261433||||||||||||||||||F|
OBX|1|FT|||Nie stwierdzono zmian||||||F|||200305261038|
OBX|2|RP|URL^Obraz||http:\\xxxxxx|
```

---

## 8. ORU^R01 - full morphology result from analyzer (16 parameters)

```
MSH|^~\&|LAB||SZPM||20101029092800||ORU^R01|LABMORF1029|P|2.3|||||PL|CP1250|PL
ORC|RE|82852^HIS|2252825^LIS||||||20101029092724|||-2^Majewska^Beata|||||OIOM
OBR|1|82852^HIS|2252825^LIS|MORF^Morfologia|||20101029092724||||||||KREW||||||||||F
OBX|1|NM|5104^WBC^LIS||9.8|K/uL|3,8 - 9,0|H|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|2|NM|5082^LYM#^LIS||2.5^(25,7 %)|K/uL|0,6- 4,1|N|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|3|NM|5092^MID#^LIS||1.3^(13,7 %)|K/uL|< 1,0|H|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|4|NM|5073^GRAN#^LIS||6.0^(60,6 %)|K/uL|2,0 - 7,8|N|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|5|NM|5084^LYM%^LIS||25.7^( 2,5 )|%|10,0 - 58,0|N|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|6|NM|5094^MID%^LIS||13.7^( 1,3 )|%|0,1 - 15,0|N|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|7|NM|5075^GRAN%^LIS||60.6^( 6,0 )|%|37,0 - 92,0|N|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|8|NM|5100^RBC^LIS||3.36|M/uL|3,50 - 5,50|L|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|9|NM|5079^HGB^LIS||9.5|g/dL|11,5 - 16,5|L|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|10|NM|5077^HCT^LIS||29.2|%|36,0 - 51,0|L|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|11|NM|5090^MCV^LIS||87.1|fL|80,0 - 97,0|N|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|12|NM|5086^MCH^LIS||28.2|pg|26,0 - 34,0|N|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|13|NM|5088^MCHC^LIS||32.5|g/dL|31,0 - 36,0|N|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|14|NM|5107^RDW-CV^LIS||15.2|%|11,5 - 15,5|N|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|15|NM|5098^PLT^LIS||190.0|K/uL|140,0 - 440,0|N|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|16|CE|5096^MPV^LIS||brak|fL|7,0 - 11,0|N|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
OBX|17|TX|5081^Histogram^LIS||(wykres 137656)|||N|||F|||20101029091447||3417^Wieczorek^Paweł^^^^LIS
```

---

## 9. ORU^R01 - lab result broadcast to external system (PIXEL)

```
MSH|^~\&|SZPM||PIXEL||20171018111457||ORU^R01|SZSZPM2620B|P|2.3|||AL|AL|PL||PL
PID|1|78010111117|2061^^^SZPM||Urbański Ąśćńłśęó^Marek||19780101|M|||&&^^Rzeszów^^^^^2468011
PV1|1|I|WEW1^^^^^^^ODC1||||||||||||||||3441|||||||||||||||||||||||||20031209165600
ORC|RE|1251625||||||||||0^^^^^^^^^^^^SZPM
OBR|1|1251625||MORF_Z^Morfologia pełna|||20170512123310||||||||&&|0^^^^^^^^^^^^SZPM
OBX|1|NM|RDW^RDW||1,0|g|11,5-14,5|L|||F|||20170512123300||^Laboratorium Administrator ( ADMIN )
OBX|2|NM|MID^MID||2|g|||||F|||20170512123300||^Laboratorium Administrator ( ADMIN )
OBX|3|NM|MPV^MPV||3|fL|||||F|||20170512123301||^Laboratorium Administrator ( ADMIN )
OBX|4|NM|PDW^PDW||4|10(GSD)|||||F|||20170512123301||^Laboratorium Administrator ( ADMIN )
```

---

## 10. ORU^R01 - radiology result without prior order (unsolicited)

```
MSH|^~\&|DIAG|DIAG|SZPM|HIS|200703011832||ORU^R01|IWM20070301183219183_1|P|2.3.1||||||8859/1
PID|1||581^^^IWM_Issuer||Wasilewski^Tadeusz||19490201|M|||Słowackiego 20/1^^Gdańsk^^80-215
ORC|RE||LW73786039||||^^^20070131133600^^R|50820|20070131133600|||2^PIK^PIK|||||WEW1^Oddział wewnętrzny
OBR|1||LW73786039|RTG|||200405261433||||||||||||||||||F|
OBX|1|FT|||Przełyk w całości poszerzony.\.br\Środek kontrastowy przez wpust przedostaje się wąską strugą.\.br\radiolog Olszewski Krzysztof||||||F|||200305261038|
```

---

## 11. ORU^R01 - microbiology blood culture (positive, with antibiogram)

```
MSH|^~\&|LAB||SZPM||20130321080553||ORU^R01|20130321080553.1|P|2.3|||AL|NE|POL|CP1250|PL
ORC|RE|16259750^ASSECO|100971|||||16259742^ASSECO||||10162^Błaszczyk^Rafał^^^^^ASSECO
OBR|1|16259750^ASSECO|100971|BAPF^Posiew krwi na podłożu pediatrycznym|||20130321080359|||11740^Malinowski^Andrzej^^^^^ASSECO||||20130318100245|KR||||||||||F
OBX|1|ST|518^Data i godzina pobrania materiału:||18-03-2013\E\09:30||||||F|||20130321080231||3970
OBX|2|ST|510^Data zakończenia badania:||21-03-2013||||||F|||20130321080231||3970
OBX|3|ST|526^Wynik badania:||dodatni||||||F|||20130321080231||3970
OBX|4|ST|2419^Identyfikacja^^ID^Identyfikacja^LIONIC|1|Staphylococcus aureus^szczep metycylinowrażliwy MSSA - wrażliwy na cefalosporyny I i II generacji oraz penicyliny z inhibitorami. Lekiem z wyboru jest kloksacylina.||||||F|||20130321080356||3970
OBX|5|ST|2425^Uwaga|1|aminoglikozydy należy stosować tylko w leczeniu skojarzonym z innym lekiem przeciwbakteryjnym, wartości graniczne ustalono dla wysokich dawek aminoglikozydów podawanych raz dziennie||||||F|||20130321080356||3970
OBR|2||101168|4556^Antybiogram automatyczny^^SU^Antybiogram^LIONIC|||||||||||||||||||||F|2419^1^Staphylococcus aureus|||16259750&ASSECO^100971
OBX|1|ST|171^Gentamycyna&GM|1|S|||<=0.5|||F|||20130321080337||3970
OBX|2|ST|196^Netylmycyna&NET|1|S||||||F|||20130321080337||3970
OBX|3|ST|161^Teikoplanina&TEI|1|S||||||F|||20130321080337||3970
OBX|4|ST|160^Wankomycyna&VA|1|S||||||F|||20130321080337||3970
OBX|5|ST|216^Trimetoprim/sulfametoksazol|1|S||||||F|||20130321080337||3970
```

---

## 12. ORU^R01 - SARS-CoV-2 positive result (alarm)

```
MSH|^~\&|LAB||SZPM||20200323182300||ORU^R01|COVIDLAB001|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|85050512345|4521^^^SZPM||Jabłońska^Natalia||19850505|F|||Mickiewicza 10^^Szczecin^^70-383
PV1|1|I|OIOM^^^^^^^ODC1||||||||||||||||8821|||||||||||||||||||||||||20200320100000
ORC|RE|2345678||||||||||0^^^^^^^^^^^^SZPM
OBR|1|2345678||SARSCOV2^SARS-CoV-2 RT-PCR|||20200323182254||||||||&&|0^^^^^^^^^^^^SZPM|||||||||||F
OBX|1|NM|SARSCOV2^Koronawirus||1|||H^alarm|||F|||20200323182254||5070883^Król^Marcin^^^lek. med.||
```

---

## 13. ORU^R01 - result with PDF attachment (base64-encoded)

```
MSH|^~\&|HOLTS|Cardiology|SZPM|TestFacility|20130916142018||ORU^R01|130916092017100035|P|2.5
PV1|||||||11^Urbańska^Jolanta
OBR|1|||18754-2^LN|||20130916092200||||||||||||||||||F
OBX|1|ED|ZAL||Dokument EKG^raport_ekg.pdf^PDF^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSAgNCAwIFIKPj4KPj4KL0NvbnRlbnRzIDUgMCBSCj4+CmVuZG9iago0IDAgb2JqCjw8IC9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKNSAwIG9iago8PCAvTGVuZ3RoIDQ0ID4+CnN0cmVhbQpCVAovRjEgMTggVGYKMCAwIFRkCihFS0cgUmVwb3J0KSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZgowMDAwMDAwMDA5IDAwMDAwIG4KMDAwMDAwMDA1OCAwMDAwMCBuCjAwMDAwMDAxMTUgMDAwMDAgbgowMDAwMDAwMjA2IDAwMDAwIG4KMDAwMDAwMDI4NCAwMDAwMCBuCnRyYWlsZXIKPDwgL1NpemUgNgovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKMzc4CiUlRU9GCg==||||||F
```

---

## 14. ORU^R01 - result with JPEG thumbnail (base64-encoded image)

```
MSH|^~\&|RIS||SZPM||20150714093012||ORU^R01|RIS20150714_001|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|72051400001|3892^^^SZPM||Jasiński^Dariusz||19720514|M|||Piłsudskiego 5^^Lublin^^20-011
ORC|RE|892341|
OBR|1|892341||RTG^RTG klatki piersiowej|||20150714092800||||||||||||||||||F|
OBX|1|FT|||Obraz rtg klatki piersiowej PA. Pola płucne bez zmian ogniskowych. Sylwetka serca w normie. Kąty przeponowo-żebrowe wolne.||||||F|||20150714093000|
OBX|2|RP|URL^Obraz PACS||http://pacs.hospital.local/wado?studyUID=1.2.840.113619.2.55&seriesUID=1.2.840.113619.2.55.1|
OBX|3|ST|MJPG^Miniatura JPG|1|/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsLDA4QDQ4NDAsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAAQABADAREAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABgcI/8QAJBAAAgIBBAEFAQAAAAAAAAAAAQIDBAUABhEhEgcTIjFBUf/EABQBAQAAAAAAAAAAAAAAAAAAAAX/xAAeEQABBAEFAAAAAAAAAAAAAAABAAIDBAURITFBkf/aAAwDAQACEQMRAD8Amm1tq5TdOVhx2MiMs7dswHCqo7LMT0FA+ydV3amyDtnbkWMa2bUyOZZ5F49x2PkxH4PQH4BqN4vI1aVlzXn0DhFDsTDwWV9Tq//2Q==|
```

---

## 15. ACK - transport acknowledgement

```
MSH|^~\&|SZPM|SYS|SYZ1|20040112112303||ACK|SZPM#97347954|T|2.3|||AL|AL|PL|CP1250|PL
MSA|CA|SYZ1#34454|||
```

---

## 16. ACK - application acknowledgement (accepted)

```
MSH|^~\&|SZPM|SYS|SYS|SYZ1|20040112112303||ACK|SZPM#103750245|T|2.3|||AL|AL|PL|CP1250|PL
MSA|AA|SYZ1#34454|||
```

---

## 17. ADT^A28 - new patient registration in master index

```
MSH|^~\&|SZPM||LABZ||20070201124042||ADT^A28|1DD47|P|2.3|||AL||PL|CP1250|PL
EVN||20070201124010
PID|1|65012611110|581^^^SZPM||Wasilewski^Tadeusz||19650126|M|||Norwida 12^^Bydgoszcz^^85-092
```

---

## 18. ADT^A01 - patient admission with diagnosis

```
MSH|^~\&|SZPM||LABZ||20070201124042||ADT^A01|1DD47|P|2.3|||AL||PL|CP1250|PL
EVN||20070201124010
PID|1|65012611110|581^^^SZPM||Wasilewski^Tadeusz||19650126|M|||Norwida 12^^Bydgoszcz^^85-092
PV1|1|I|WEW1^^^^^^^ODC1||||||||||||||||1/2007^^SZPM^KSG
DG1|1||E10.2^Cukrzyca insulinozależna (z powikłaniami nerkowymi)^ICD10|||F|||||||||||WST
```

---

## 19. ADT^A03 - patient discharge

```
MSH|^~\&|SZPM||LABZ||20070201124042||ADT^A03|1DD47|P|2.3|||AL||PL|CP1250|PL
EVN||20070201124010
PID|1|65012611110|581^^^SZPM||Wasilewski^Tadeusz||19650126|M|||Norwida 12^^Bydgoszcz^^85-092
PV1|1|I|WEW1^^^^^^^ODC1||||||||||||||||1/2007^^SZPM^KSG
DG1|1||E10.2^Cukrzyca insulinozależna (z powikłaniami nerkowymi)^ICD10|||F|||||||||||WST
```

---

## 20. ADT^A13 - cancel discharge (readmission)

```
MSH|^~\&|SZPM||ECH||20161017085833||ADT^A13|ADTSZPM25F03|P|2.3|||AL|AL|PL||PL
EVN||20161017
PID|1|76120215910|4276^^^SZPM||Zawadzki^Grzegorz||19761202|M||||||||||||||||||PL
PV1|1|I|WEW1||||||||||||||||13249|||||||||||||||||||||||||20160919074900
```
