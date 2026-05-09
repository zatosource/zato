# Kamsoft KS-MEDIS - real HL7v2 ER7 messages

---

## 1. ORM^O01 - new lab order (simple, inpatient)

```
MSH|^~\&|CLININET|UHC|Moduł diagn.||20020603121707||ORM^O01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
PID||73051213886^^^^PESEL|17741||Tomaszewska^Agnieszka||19730512|F|||Zielona&34^^Toruń^^87-100|||||||||
PV1|1|I|12113^^^^^^^^Ginekologia&GIN&HIS||||||||||||||||||||||||||||||||||||||||||||||||||
IN1|||134&HIS|Mazowiecki Oddział NFZ&07R
ORC|NW|17741-1-249^HIS||13235782^HIS|||^^^200110191339^^13&RUTYNOWE&R&HIS^||200110191340|||132^Stefański^Marek^T.^^dr med^^HIS|||||1234^Ginekologia&GIN^HIS|||
OBR|1|17741-1-249^HIS||1234^Badanie moczu&BSPMOCZ^HIS|||20011019||||||Antykoagulanty&NIE~Infuzje&NIE~Went.wspomagana&NIE~Went.kontrolowana&TAK~Tlenoterapia&TAK~Fototerapia&TAK||2323^Krew&KREW^HIS^^^^^SampleID&123456~Comment&komentarz|132^Stefański^Marek^T.^^dr med^^HIS|||||||||||||||
```

---

## 2. ORM^O01 - new lab order (compound profile with tests)

```
MSH|^~\&|CLININET|UHC|Moduł diagn.||20020603121707||ORM^O01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
PID||73051213886^^^^PESEL|17741||Tomaszewska^Agnieszka||19730512|F|||Zielona&34^^Toruń^^87-100|||||||||
PV1|1|O|||||||||||||||||||||||||||||||||||||||||||||||||||
IN1|||134&HIS|Mazowiecki Oddział NFZ&07R
ORC|NW|17741-2-1^HIS||1345782^HIS|||^^^200110041555^^13&RUTYNOWE&R&HIS^||200110041556|||132^Zakrzewski^Piotr^^^^dr med^^HIS|||||1234^Pracownia Pulmonologiczna&P-PA^HIS|||
OBR|1|17741-2-1^HIS||232^Biochemia&BIOCH^HIS|||20011004|||||||||132^Stefański^Marek^T.^^dr med^^HIS||||||||||||||||||||||||||||
ORC|NW|17741-2-2^HIS||1345782^HIS|||^^^200110041555^^13&RUTYNOWE&R&HIS^|17741-2-1&HIS|200110041556|||132^Stefański^Marek^T.^^dr med^^HIS|||||1234^Pracownia Pulmonologiczna&P-PA^HIS|||
OBR|2|17741-2-2^HIS||2323^Alat&ALAT^HIS|||20011004|||||||||132^Stefański^Marek^T.^^dr med^^HIS|||||||||||||17741-2-1&HIS|||||||||||||||
ORC|NW|17741-2-3^HIS||1345782^HIS|||^^^200110041555^^13&RUTYNOWE&R&HIS^|17741-2-1&HIS|200110041556|||132^Stefański^Marek^T.^^dr med^^HIS|||||1234^Pracownia Pulmonologiczna&P-PA^HIS|||
OBR|3|17741-2-3^HIS||2324^Aspat&ASPAT^HIS|||20011004|||||||||132^Stefański^Marek^T.^^dr med^^HIS||||||||||||17741-2-1&HIS||||||||||||||||
ORC|NW|17741-2-4^HIS||1345782^HIS|||^^^200110041555^^13&RUTYNOWE&R&HIS^|17741-2-1&HIS|200110041556|||132^Stefański^Marek^T.^^dr med^^HIS|||||1234^Pracownia Pulmonologiczna&P-PA^HIS|||
OBR|4|17741-2-4^HIS||2345^Krea&KREA^HIS|||20011004|||||||||132^Stefański^Marek^T.^^dr med^^HIS|||||||||||||17741-2-1&HIS|||||||||||||||
```

---

## 3. ORM^O01 - order modification

```
MSH|^~\&|CLININET|UHC|Moduł diagn.||20020603121707||ORM^O01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
PID||73051213886^^^^PESEL|17741||Tomaszewska^Agnieszka||19730512|F|||Zielona&34^^Toruń^^87-100|||||||||
PV1|1|O|||||||||||||||||||||||||||||||||||||||||||||||||||
IN1|||134&HIS|Mazowiecki Oddział NFZ&07R
ORC|XO|23-2-83^HIS||3242232^HIS|||||200109261114|||132^Karpiński^Dariusz^^^^dr med^^HIS|12456^^^^^^^1^Ginekologia&GIN&HIS||||1234^Pracownia 1&ADA^HIS|||
OBR|1|23-2-83^HIS||2324^Aspat&ASPAT^HIS||||||||||||132^Karpiński^Dariusz^^^^dr med^^HIS||||||||||||||||||||||||||||
```

---

## 4. ORM^O01 - order cancellation

```
MSH|^~\&|CLININET|UHC|Moduł diagn.||20020603121707||ORM^O01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
ORC|CA|17770-1-158^HIS|||||||||||
OBR||17770-1-158^HIS||2324^Aspat&ASPAT^HIS|||||||||||||||||||||||||||
NTE|1|P|*** Testowa przyczyna anulowania L1 ***
NTE|2|P|*** Testowa przyczyna anulowania L2 ***
```

---

## 5. ORM^O01 - order from diagnostic module to HIS

```
MSH|^~\&|Moduł diagn.||CLININET|UHC|20020603121707||ORM^O01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
PID||73051213886^^^^PESEL|17741||Tomaszewska^Agnieszka||19730512|F|||Zielona&34^^Toruń^^87-100|||||||||
PV1|1|I|12113^^^^^^^^Ginekologia&GIN&HIS||||||||||||||||||||||||||||||||||||||||||||||||||
IN1|||134&HIS|Mazowiecki Oddział NFZ&07R
ORC|NW||17741-1-249^LAB||||^^^200110191339^^13&RUTYNOWE&R&HIS^||200110191340|||132^Stefański^Marek^T.^^dr med^^HIS|||||1234^Ginekologia&GIN^HIS|||
OBR|1||17741-1-249^LIS|1234^Badanie moczu&BSPMOCZ^HIS|||20011019|||||||200110190900|2323^Krew&KREW^HIS^^^^^SampleID&123456~Comment&krew pobrano po zjedzeniu cukierka|132^Stefański^Marek^T.^^dr med^^HIS||||||||||||||
```

---

## 6. ORM^O01 - order status change (completed)

```
MSH|^~\&|Moduł diagn.||CliniNET|UHC|20020603121707||ORM^O01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
ORC|SC|17770-1-158^HIS|||CM||||||||
OBR||17770-1-158^HIS||2324^Aspat&ASPAT^HIS|||||||||||||||||||||||||||
NTE|1|P|*** Testowa przyczyna zmiany statusu L1 ***
NTE|2|P|*** Testowa przyczyna zmiany statusu L2 ***
```

---

## 7. ORU^R01 - numeric lab results (CBC/morphology)

```
MSH|^~\&|Moduł diagn.||CliniNET|UHC|20020603121707||ORU^R01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
ORC|RE|17578-1-49^HIS|
OBR|1|57520-1-18^HIS||25454^Morfologia&MORF^HIS|||20010925000000|||||||||GIN||||||||||
OBX|1|NM|335^HCT&HCT&LAB|N|39.4|%|(36 - 46)||||F|||20010926240000||132^Stefański^Marek^T.^^dr med.^^HIS
OBX|2|NM|336^HGB&HGB^LAB|N|13.30|g/dl|(11,5 - 15,0)||||F|||20010926240000||132^Stefański^Marek^T.^^dr med.^^HIS
OBX|3|NM|337^MCH&MCH^LAB|N|29.9|pg|(27 - 31)||||F|||20010926240000||132^Stefański^Marek^T.^^dr med.^^HIS
OBX|4|NM|338^MCHC&MCHC^LAB|N|33.8|g/dl|(32 - 36)||||F|||20010926240000||132^Stefański^Marek^T.^^dr med.^^HIS
OBX|5|NM|339^MCV&MCV^LAB|N|88.5|fl|(84 - 98)||||F|||20010926240000||132^Stefański^Marek^T.^^dr med.^^HIS
OBX|6|NM|340^PLT&PLT^LAB|N|239.0|10e3/uL|(130 - 400)||||F|||20010926240000||132^Stefański^Marek^T.^^dr med.^^HIS
OBX|7|NM|341^RBC&RBC^LAB|N|4.45|10e6/uL|(3,7 - 5,0)||||F|||20010926240000||132^Stefański^Marek^T.^^dr med.^^HIS
OBX|8|NM|342^WBC&WBC^LAB|N|9.70|10e3/uL|(4,0 - 10,0)||||F|||20010926240000||132^Stefański^Marek^T.^^dr med.^^HIS
```

---

## 8. ORU^R01 - formatted text result (radiology)

```
MSH|^~\&|Moduł diagn.||CliniNET|UHC|20020603121707||ORU^R01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
ORC|RE|17578-1-49^HIS|
OBR||17578-1-49^HIS||25422^Morfologia&MORF^HIS|||200203061549|||||||||||||||||||
OBX|1|FT|||Wprowadzenie wyników z polskimi znaczkami: żźąęŻŹĄŚĘÓŃóń\.br\--- test 1 ---\.br\radiolog Grzelak||||||F|||200203061549|
```

---

## 9. ORU^R01 - radiology result with text description

```
MSH|^~\&|SYZ1||SZPM||200405261448||ORU^R01|VSZ01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR|1|1115610||RTG|||200405261433||||||||||||||||||F|
OBX|1|FT|||Przełyk w całości poszerzony.\.br\Środek kontrastowy przez wpust przedostaje się wąską strugą.\.br\radiolog Matuszewski Ryszard||||||F|||200305261038|
```

---

## 10. ORU^R01 - coded lab result (ESR/OB)

```
MSH|^~\&|LAB||SZPM||200405261448||ORU^R01|LW01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR||1115610||OB^Odczyn Biernackiego^SZPM|||200405261433||||||||||||||||||F|
OBX|1|CE|OB^Odczyn Biernackiego^SZPM||15|mm/h|0-12|H||||F|||200305261038|
```

---

## 11. ORU^R01 - partial results with CBC components

```
MSH|^~\&|LAB||SZPM||200405261448||ORU^R01|LW01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR|1|1115610||MORF|||200405261433||||||||||||||||||F|
OBX|1|CE|WBC^Leukocyty^SZPM||8.57|m/uL|4.80-10.80|||||F|||200505261038|
OBX|2|CE|RBC^Erytrocyty^SZPM||6.65|m/uL|4.20-5.40|H||||F|||200505261038|
OBX|3|CE|RBC^Erytrocyty^SZPM||6.65|m/uL|4.20-5.40|H||||F|||200505261038|
```

---

## 12. ORU^R01 - result with URL reference link

```
MSH|^~\&|SYZ1||SZPM||200405261448||ORU^R01|VSZ01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR|1|1115610||RTG|||200405261433||||||||||||||||||F|
OBX|1|FT|||Nie stwierdzono zmian||||||F|||200305261038|
OBX|2|RP|URL^Obraz||http:\\xxxxxx|
```

---

## 13. ORU^R01 - full morphology with 17 components

```
MSH|^~\&|LAB||SZPM||20101029092724||ORU^R01|LW20101029|P|2.3|||||PL|CP1250|PL
ORC|RE|82852^HIS|2252825^LIS||||||20101029092724|||-2^Karpińska^Jolanta|||||OIOM
OBR|1|82852^HIS|2252825^LIS|MORF^Morfologia|||20101029092724||||||||KREW||||||||||F
OBX|1|NM|5104^WBC^LIS||9.8|K/uL|3,8 - 9,0|H|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|2|NM|5082^LYM#^LIS||2.5^(25,7 %)|K/uL|0,6- 4,1|N|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|3|NM|5092^MID#^LIS||1.3^(13,7 %)|K/uL|< 1,0|H|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|4|NM|5073^GRAN#^LIS||6.0^(60,6 %)|K/uL|2,0 - 7,8|N|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|5|NM|5084^LYM%^LIS||25.7^( 2,5 )|%|10,0 - 58,0|N|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|6|NM|5094^MID%^LIS||13.7^( 1,3 )|%|0,1 - 15,0|N|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|7|NM|5075^GRAN%^LIS||60.6^( 6,0 )|%|37,0 - 92,0|N|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|8|NM|5100^RBC^LIS||3.36|M/uL|3,50 - 5,50|L|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|9|NM|5079^HGB^LIS||9.5|g/dL|11,5 - 16,5|L|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|10|NM|5077^HCT^LIS||29.2|%|36,0 - 51,0|L|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|11|NM|5090^MCV^LIS||87.1|fL|80,0 - 97,0|N|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|12|NM|5086^MCH^LIS||28.2|pg|26,0 - 34,0|N|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|13|NM|5088^MCHC^LIS||32.5|g/dL|31,0 - 36,0|N|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|14|NM|5107^RDW-CV^LIS||15.2|%|11,5 - 15,5|N|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|15|NM|5098^PLT^LIS||190.0|K/uL|140,0 - 440,0|N|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|16|CE|5096^MPV^LIS||brak|fL|7,0 - 11,0|N|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
OBX|17|TX|5081^Histogram^LIS||(wykres 137656)|||N|||F|||20101029091447||3417^Domański^Krzysztof^^^^LIS
```

---

## 14. ORU^R01 - microbiology result with antibiogram

```
MSH|^~\&|LAB||SZPM||20130321080553||ORU^R01|20130321080553.1|P|2.3|||AL|NE|POL|CP1250|PL
ORC|RE|16259750^ASSECO|100971|||||16259742^ASSECO||||10162^Janik^Tomasz^^^^^ASSECO
OBR|1|16259750^ASSECO|100971|BAPF^Posiew krwi na podłożu pediatrycznym|||20130321080359|||11740^Leszczyński^Andrzej^^^^^ASSECO||||20130318100245|KR||||||||||F
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

## 15. ORU^R01 - SARS-CoV-2 positive result (alarm flag)

```
MSH|^~\&|LAB||SZPM||20200323182400||ORU^R01|LCOV20200323|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|85031512345|4890^^^SZPM||Romanowski^Łukasz||19850315|M|||Krakowska 15^^Kalisz^^62-800
PV1|1|I|WEW1^^^^^^^ODC1||||||||||||||||8821
ORC|RE|2045890|
OBR|1|2045890||SARSCOV2^Test SARS-CoV-2|||20200323182254||||||||&&||||||||||F
OBX|1|NM|SARSCOV2^Koronawirus||1|||H^alarm|||F|||20200323182254||5070883^Kędzierski^Wojciech^^^lek. med.||
```

---

## 16. ORU^R01 - result with embedded PDF attachment (base64)

```
MSH|^~\&|HOLTS|Cardiology|SZPM|TestFacility|20130916142018||ORU^R01|130916092017100035|P|2.5
PV1|||||||11^Nowicka^Beata
OBR|1|||18754-2^LN|||20130916092200||||||||||||||||||F
OBX|1|ED|ZAL||Dokument^dokument.pdf^PDF^Base64^JVBERi0xLjMKJcTl8uXrp6elCjEgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDIgMCBSID4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9QYWdlcyAvS2lkcyBbMyAwIFJdIC9Db3VudCAxID4+CmVuZG9iagozIDAgb2JqCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMiAwIFIgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0gPj4KZW5kb2JqCnhyZWYKMCA0CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxNSAwMDAwMCBuIAowMDAwMDAwMDY4IDAwMDAwIG4gCjAwMDAwMDAxMjUgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA0IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgoyMTYKJSVFT0YK||||||F
```

---

## 17. ORU^R01 - result with embedded JPEG image (base64 thumbnail)

```
MSH|^~\&|RIS||SZPM||20150810093000||ORU^R01|RIS20150810|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|79062312345|3456^^^SZPM||Kubicka^Wioletta||19790623|F|||Lipowa 7^^Olsztyn^^10-500
PV1|1|I|CHIR1^^^^^^^ODC1||||||||||||||||5678
ORC|RE|1567890|
OBR|1|1567890||RTG^RTG klatki piersiowej|||20150810092500||||||||||||||||||F|
OBX|1|FT|||Obraz radiologiczny klatki piersiowej w normie. Serce prawidlowej wielkosci. Pola plucne bez zmian ogniskowych.\.br\Wniosek: Obraz prawidlowy.||||||F|||20150810092500|
OBX|2|RP|URL^Obraz RTG||http://pacs.szpital.pl/wado?studyUID=1.2.840.113619.2.55.3.604688119&requestType=WADO|
OBX|3|ST|MJPG^Miniatura JPG|1|/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DhAQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQU FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAAoACgDASIAAhEBAxEB/8QAGwAAAgIDAQAA AAAAAAAAAAAABQYEBwECAwj/xAAvEAABAwIEBQIFBQEAAAAAAAABAgMEBREABhIhBxMxQVEiYQgUMnGB FRZC0fD/xAAZAQACAwEAAAAAAAAAAAAAAAAEBQIDBgH/xAAjEQABBAICAgIDAAAAAAAAAAA BABECITEDQRJRImFxgfD/2gAMAwEAAhEDEQA/APVGIdfnMU2mzJ8pwNx4jK33VnsEpBJP4GOdeqMel Uw1CfIbYitjU466oJSkdzk/8A7GKu+IXifDoFJdpNPkBNUfTyQUn+lB7n/XfACT4QHHPnmZpeeqnO qk52RPkJddddWSpZKjuSTud8bQXK06FmJc17kC5pvnmfkmX+HMWK2Cmc5I0JSPBWUJ/3jmh0a7o0r5C A/LOxvZlOAnyOYED+sbCE7wvyJPYqSGah8ys3tqQgAAfYAYh8QKdVcp5hnoZmOtwn0PxkJ3V6VhQOn3 t0GNF4xDSzK8t7T0zhfjJmcHa24rXK+VWB6mVqt7ehx0HELI/EvL2f5CjS1hqei2umyR6wPIB6j3HX HCVkrJE8Bt6kTmASN0c4KxFfym7AqcqM45TZ6Uawlfw7kAHp+OuOUEhL1TtWVcvLGYqjVqy7Ua1Mfn Tp7h5kl9Z1LWexJ/odiTi3vg/wCHM6qZgg5pmsqagQiXYxUNlOK7K9gB0+5xVOBOW+J2Ss3w6vRctO PwQ8EympJShLqP5JINxuD+DiYALSVwOJuIWDv/9k=|
```

---

## 18. ORM^O01 - lab order with material collection (KS-MEDIS/InfoMedica)

```
MSH|^~\&|SZPM||LABHL7||20070716112609||ORM^O01|1E273|P|2.3|||AL||PL|CP1250|PL
PID|1|68032000001|2121||Leszczyńska^Dorota||19680320|F|||^^Bydgoszcz
PV1|1|O|PPOB||||||||||||||||4735.5418
IN1|1||12
ORC|NW|54942|||||^^^20070716112602^^R||20070716112504|||49999^Nowicka^Katarzyna|||||PPOB^Punkt pobrań
OBR|1|54942||OB^Odczyn opadania krwinek czerwonych|||20070716112504|||2^PIK^PIK||||20070716112602|KP&Krew pełna&SZPM|49999^Nowicka^Katarzyna||800002981||||||LHL7
```

---

## 19. ADT^A01 - patient admission notification with diagnosis

```
MSH|^~\&|SZPM||LABZ||20070201124042||ADT^A01|1DD47|P|2.3|||AL||PL|CP1250|PL
EVN||20070201124010
PID|1|65012611110|581^^^SZPM||Zając^Tadeusz||19650126|M|||Wiejska 1236^^Elbląg^^82-300
PV1|1|I|WEW1^^^^^^^ODC1||||||||||||||||1/2007^^SZPM^KSG
DG1|1||E10.2^Cukrzyca insulinozależna (z powikłaniami nerkowymi)^ICD10|||F|||||||||||WST
```

---

## 20. ACK - transport-level acknowledgement

```
MSH|^~\&|SZPM|SYS|SYZ1|20040112112303||ACK|SZPM#97347954|T|2.3|||AL|AL|PL|CP1250|PL
MSA|CA|SYZ1#34454|||
```

---
