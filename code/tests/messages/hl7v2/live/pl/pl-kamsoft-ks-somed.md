# Kamsoft KS-SOMED - real HL7v2 ER7 messages

---

## 1. ORM^O01 - outpatient lab order (ESR test)

```
MSH|^~\&|SZPM||LABHL7||20070716112609||ORM^O01|1E273|P|2.3|||AL||PL|CP1250|PL
PID|1|68032000001|2121||Czajkowska^Weronika||19680320|F|||^^Zabrze
PV1|1|O|PPOB||||||||||||||||4735.5418
IN1|1||12
ORC|NW|54942|||||^^^20070716112602^^R||20070716112504|||49999^Grochowska^Jolanta|||||PPOB^Punkt pobrań
OBR|1|54942||OB^Odczyn opadania krwinek czerwonych|||20070716112504|||2^PIK^PIK||||20070716112602|KP&Krew pełna&SZPM|49999^Grochowska^Jolanta||800002981||||||LHL7
```

---

## 2. ORM^O01 - outpatient radiology order

```
MSH|^~\&|SZPM||SYZ1||20030526103638||ORM^O01|SZ01F28|T|2.3|||||PL|CP1250|PL
PID|1||75721||Filipiak^Elżbieta||19850411|F|||,^^Ciechocinek
PV1|1|O|POZ1
IN1|1||02R
ORC|NW|1115610|||||^^^^^R|1115610|20030526103100|||175^Wesołowska Katarzyna|||||POZ1
OBR|1|1115610||RTG||||||||||||175^Cieślak Agnieszka||||||||HL7|||||1115610
NTE|1|P|klatki piersiowej
```

---

## 3. ORM^O01 - outpatient lab order (simple, ambulatory)

```
MSH|^~\&|CLININET|UHC|Moduł diagn.||20020603121707||ORM^O01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
PID||73051213886^^^^PESEL|17741||Konieczna^Franciszka||19730512|F|||Piłsudskiego&34^^Zamość^^22-400|||||||||
PV1|1|O|||||||||||||||||||||||||||||||||||||||||||||||||||
IN1|||134&HIS|Mazowiecki Oddział NFZ&07R
ORC|NW|17741-2-1^HIS||1345782^HIS|||^^^200110041555^^13&RUTYNOWE&R&HIS^||200110041556|||132^Głąb^Tomasz^^^^dr med^^HIS|||||1234^Pracownia Pulmonologiczna&P-PA^HIS|||
OBR|1|17741-2-1^HIS||232^Biochemia&BIOCH^HIS|||20011004|||||||||132^Szulc^Andrzej^W.^^dr med^^HIS||||||||||||||||||||||||||||
```

---

## 4. ORM^O01 - outpatient order cancellation

```
MSH|^~\&|CLININET|UHC|Moduł diagn.||20020603121707||ORM^O01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
ORC|CA|17770-1-158^HIS|||||||||||
OBR||17770-1-158^HIS||2324^Aspat&ASPAT^HIS|||||||||||||||||||||||||||
NTE|1|P|*** Testowa przyczyna anulowania L1 ***
NTE|2|P|*** Testowa przyczyna anulowania L2 ***
```

---

## 5. ORM^O01 - order status change (accepted for execution)

```
MSH|^~\&|RIS||SZPM||20120123125736||ORM^O01|SZ23592|P|2.3|||AL|AL|PL||PL
PID|1||1782^^^SZPM||Kopeć^Roman||19530101|M|||
PV1|1|O|POZ1||||||||||||||||2341.3641
IN1|1||099
ORC|RF|85770|||IP||^^^20120123094200^^R|85770|20120123094200|||2^PIK^PIK^^^^^^^^^^SZPM|ODC2|||WEW1^Oddział wewnętrzny
OBR|1|85770||XA.AORTIC^Angiografia|||20120123094200||||||I20.0|20120123094200|&&|2^PIK^PIK|||5000101|||||ALT|||||85770
```

---

## 6. ORM^O01 - comment exchange on order result

```
MSH|^~\&|RIS||SZPM||20160506130837||ORM^O01|SZSZPM25C52_002|P|2.3|||AL|AL|PL||PL
ORC|KN|75413||||||20160510130827|||1^ADMIN^ADMIN^^^^^^^^^^UZY
OBR|1|75413||XA.AORTIC^Angiografia|||||||||||&&|
NTE|1|P|komentarz|1228109
```

---

## 7. ORU^R01 - outpatient lab result (ESR with abnormal flag)

```
MSH|^~\&|LAB||SZPM||200405261448||ORU^R01|LW01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR||1115610||OB^Odczyn Biernackiego^SZPM|||200405261433||||||||||||||||||F|
OBX|1|CE|OB^Odczyn Biernackiego^SZPM||15|mm/h|0-12|H||||F|||200305261038|
```

---

## 8. ORU^R01 - outpatient radiology result (text description)

```
MSH|^~\&|SYZ1||SZPM||200405261448||ORU^R01|VSZ01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR|1|1115610||RTG|||200405261433||||||||||||||||||F|
OBX|1|FT|||Przełyk w całości poszerzony.\.br\Środek kontrastowy przez wpust przedostaje się wąską strugą.\.br\radiolog Tadeusz Lech||||||F|||200305261038|
```

---

## 9. ORU^R01 - morphology results with partial values

```
MSH|^~\&|LAB||SZPM||200405261448||ORU^R01|LW01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR|1|1115610||MORF|||200405261433||||||||||||||||||F|
OBX|1|CE|WBC^Leukocyty^SZPM||8.57|m/uL|4.80-10.80|||||F|||200505261038|
OBX|2|CE|RBC^Erytrocyty^SZPM||6.65|m/uL|4.20-5.40|H||||F|||200505261038|
OBX|3|CE|RBC^Erytrocyty^SZPM||6.65|m/uL|4.20-5.40|H||||F|||200505261038|
```

---

## 10. ORU^R01 - lab morphology results sent to external system

```
MSH|^~\&|SZPM||PIXEL||20171018111457||ORU^R01|SZSZPM2620B|P|2.3|||AL|AL|PL||PL
PID|1|78010111117|2061^^^SZPM||Konieczny Ąśćńłśęó^Marek||19780101|M|||&&^^Gliwice^^^^^2468011
PV1|1|O|POZ1||||||||||||||||3441
ORC|RE|1251625||||||||||0^^^^^^^^^^^^SZPM
OBR|1|1251625||MORF_Z^Morfologia pełna|||20170512123310||||||||&&|0^^^^^^^^^^^^SZPM
OBX|1|NM|RDW^RDW||1,0|g|11,5-14,5|L|||F|||20170512123300||^Laboratorium Administrator ( ADMIN )
OBX|2|NM|MID^MID||2|g|||||F|||20170512123300||^Laboratorium Administrator ( ADMIN )
OBX|3|NM|MPV^MPV||3|fL|||||F|||20170512123301||^Laboratorium Administrator ( ADMIN )
OBX|4|NM|PDW^PDW||4|10(GSD)|||||F|||20170512123301||^Laboratorium Administrator ( ADMIN )
```

---

## 11. ORU^R01 - result with additional sub-ordered tests

```
MSH|^~\&|LAB||SZPM||200405261448||ORU^R01|LW01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR|1|1115610|L1234405|MORF|||200405261433||||||||||||||||||F|||||
OBX|1|CE|WBC^Leukocyty^SZPM||8.57|m/uL|4.80-10.80|||||F|||200505261038|
OBX|2|CE|RBC^Erytrocyty^SZPM||6.65|m/uL|4.20-5.40|H||||F|||200505261038|
OBX|3|CE|RBC^Erytrocyty^SZPM||6.65|m/uL|4.20-5.40|H||||F|||200505261038|
OBR|2||L1234406|ROZM^Rozmaz mikroskopowy^SZPM|||200405261433||||||||||||||||||F||||1115610^L1234405|
OBX|1|CE|LIM^Limfocyty^SZPM||32|%|19-48|||||F|||200505261038|
OBX|2|CE|MON^Monocyty^SZPM||1|%|3-9|L||||F|||200505261038|
```

---

## 12. ORU^R01 - unsolicited result (no prior order from HIS)

```
MSH|^~\&|DIAG|DIAG|SZPM|HIS|200703011832||ORU^R01|IWM20070301183219183_1|P|2.3.1||||||8859/1
PID|1||581^^^IWM_Issuer||Polak^Zofia||19490201|F|||Kwiatowa 20/1^^Suwałki^^16-400
ORC|RE||LW73786039||||^^^20070131133600^^R|50820|20070131133600|||2^PIK^PIK|||||WEW1^Oddział wewnętrzny
OBR|1||LW73786039|RTG|||200405261433||||||||||||||||||F|
OBX|1|FT|||Przełyk w całości poszerzony.\.br\Środek kontrastowy przez wpust przedostaje się wąską strugą.\.br\radiolog Tadeusz Lech||||||F|||200305261038|
```

---

## 13. ORU^R01 - result with additional procedure execution codes

```
MSH|^~\&|DIAG|DIAG|SZPM|HIS|200703011832||ORU^R01|IWM20070301183219183_1|P|2.3.1||||||8859/1
PID|1||581^^^IWM_Issuer||Wrona^Jadwiga||19490201|F|||Lipowa 8^^Chełm^^22-100
ORC|RE||LW73786039||||^^^20070131133600^^R|50820|20070131133600|||2^PIK^PIK|||||WEW1^Oddział wewnętrzny
OBR|1||LW73786039|RTG|||200405261433||||||||||||||||||F|
OBX|1|FT|||Przełyk w całości poszerzony.\.br\Środek kontrastowy przez wpust przedostaje się wąską strugą.\.br\radiolog Tadeusz Lech||||||F|||200305261038
OBX|2|CE|XXKPM|RT_KNT|||||||F|||200305261038
OBX|3|CE|XXKPM|PRC12|||||||F|||200305261038
```

---

## 14. ORU^R01 - result with radiation exposure parameters

```
MSH|^~\&|DIAG|DIAG|SZPM|HIS|200703011832||ORU^R01|IWM20070301183219183_1|P|2.3.1||||||8859/1
PID|1||581^^^IWM_Issuer||Rak^Teresa||19490201|F|||Słoneczna 15^^Przemyśl^^37-700
ORC|RE||LW73786039||||^^^20070131133600^^R|50820|20070131133600|||2^PIK^PIK|||||WEW1^Oddział wewnętrzny
OBR|1||LW73786039|RTG|||200405261433||||||||||||||||||F|
OBX|1|FT|||Przełyk w całości poszerzony.\.br\Środek kontrastowy przez wpust przedostaje się wąską strugą.\.br\radiolog Tadeusz Lech||||||F|||200305261038
OBX|2|CE|PEKSP^^^CZAS^|1|30||||||F|
OBX|3|CE|PEKSP^^^NAT^|1|120||||||F|
OBX|4|CE|PEKSP^^^CZAS^|2|15||||||F|
OBX|5|CE|PEKSP^^^NAT^|2|150||||||F|
```

---

## 15. ADT^A28 - new patient record in registry

```
MSH|^~\&|SZPM||LABZ||20070201124042||ADT^A28|1DD47|P|2.3|||AL||PL|CP1250|PL
EVN||20070201124010
PID|1|65012611110|581^^^SZPM||Duda^Bartosz||19650126|M|||Wiejska 1236^^Gliwice^^44-100
```

---

## 16. ADT^A31 - patient data modification with measurement

```
MSH|^~\&|SZPM||LABZ||20070201124042||ADT^A31|1DD47|P|2.3|||AL||PL|CP1250|PL
EVN||20070201124010
PID|1|65012611110|581^^^SZPM||Duda^Bartosz||19650126|M|||Wiejska 1236^^Gliwice^^44-100
```

---

## 17. ADT^A13 - visit end cancellation (readmission)

```
MSH|^~\&|SZPM||ECH||20161017085833||ADT^A13|ADTSZPM25F03|P|2.3|||AL|AL|PL||PL
EVN||20161017
PID|1|76120215910|4276^^^SZPM||Grochowski^Stanisław||19761202|M||||||||||||||||||PL
PV1|1|I|WEW1||||||||||||||||13249|||||||||||||||||||||||||20160919074900
```

---

## 18. QRY^A19 - patient data query (by PESEL)

```
MSH|^~\&|ZEWN||SZPM||201404141309282||QRY^A19|1|P|2.3
QRD|20140414130928|R|I|1|||1|#85061478324|DEM|
```

---

## 19. ORU^R01 - result with embedded PDF document (base64)

```
MSH|^~\&|DIAG|DIAG|SZPM|HIS|20210415103000||ORU^R01|DIAG20210415|P|2.3.1||||||CP1250
PID|1|90051512345|8901^^^SZPM||Kaczmarczyk^Alicja||19900515|F|||Polna 22^^Lublin^^20-001
PV1|1|O|POZ1
ORC|RE||DG778899||||^^^20210415100000^^R||20210415100000|||88^Wesołowski^Zbigniew|||||POZ1
OBR|1||DG778899|USG^USG jamy brzusznej|||20210415102500||||||||||||||||||F|
OBX|1|FT|||Watroba prawidlowej wielkosci, jednorodna. Drogi zolciowe nieposzerzone.\.br\Woreczek zolciowy bez zlogow.\.br\Trzustka prawidlowa. Sledziona 11cm.\.br\Nerki prawidlowej wielkosci i echogenicznosci.\.br\Wniosek: Obraz ultrasonograficzny w normie.||||||F|||20210415102500|
OBX|2|ED|ZAL||Wynik USG^wynik_usg.pdf^PDF^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA4NCA+PgpzdHJlYW0KQlQKL0YxIDE0IFRmCjUwIDcwMCBUZAooV3luaWsgYmFkYW5pYSBVU0cgamFteSBicnp1c3puZWopIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNDQyIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTM1CiUlRU9GCg==||||||F
```

---

## 20. ORU^R01 - result with embedded JPEG image (base64 miniature)

```
MSH|^~\&|RIS||SZPM||20180322140000||ORU^R01|RIS20180322|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|82111012345|5567^^^SZPM||Zieliński^Krzysztof||19821110|M|||Długa 3^^Gdańsk^^80-001
PV1|1|O|POZ1
ORC|RE|2089001|
OBR|1|2089001||RTG^RTG zatoki|||20180322135500||||||||||||||||||F|
OBX|1|FT|||Zatoki przynosowe boczne prawidlowo powietrzne. Przegroda nosowa ustawiona posrodkowo. Zatoki czolowe symetryczne. Zatoki szczekowe bez poziomu plynu.\.br\Wniosek: Obraz prawidlowy.||||||F|||20180322135500|
OBX|2|RP|URL^Obraz RTG zatoki||http://pacs.szpital.pl/wado?studyUID=1.2.840.113619.2.55.3.99887766&requestType=WADO|
OBX|3|ST|MJPG^Miniatura JPG|1|/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DhAQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQU FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAAoACgDASIAAhEBAxEB/8QAGwAAAgIDAQAA AAAAAAAAAAAABQYEBwECAwj/xAAvEAABAwIEBQIFBQEAAAAAAAABAgMEBREABhIhBxMxQVEiYQgUMnGB FRZC0fD/xAAZAQACAwEAAAAAAAAAAAAAAAAEBQIDBgH/xAAjEQABBAICAgIDAAAAAAAAAAA BABECITEDQRJRImFxgfD/2gAMAwEAAhEDEQA/APVGIdfnMU2mzJ8pwNx4jK33VnsEpBJP4GOdeqMel Uw1CfIbYitjU466oJSkdzk/8A7GKu+IXifDoFJdpNPkBNUfTyQUn+lB7n/XfACT4QHHPnmZpeeqnO qk52RPkJddddWSpZKjuSTud8bQXK06FmJc17kC5pvnmfkmX+HMWK2Cmc5I0JSPBWUJ/3jmh0a7o0r5C A/LOxvZlOAnyOYED+sbCE7wvyJPYqSGah8ys3tqQgAAfYAYh8QKdVcp5hnoZmOtwn0PxkJ3V6VhQOn3 t0GNF4xDSzK8t7T0zhfjJmcHa24rXK+VWB6mVqt7ehx0HELI/EvL2f5CjS1hqei2umyR6wPIB6j3HX HCVkrJE8Bt6kTmASN0c4KxFfym7AqcqM45TZ6Uawlfw7kAHp+OuOUEhL1TtWVcvLGYqjVqy7Ua1Mfn Tp7h5kl9Z1LWexJ/odiTi3vg/wCHM6qZgg5pmsqagQiXYxUNlOK7K9gB0+5xVOBOW+J2Ss3w6vRctO PwQ8EympJShLqP5JINxuD+DiYALSVwOJuIWDv/9k=|
```

---
