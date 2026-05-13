# CGM NETRAAD - real HL7v2 ER7 messages

---

## 1

```
MSH|^~\&|CLININET|UHC|Moduł diagn.||20020603121707||ORM^O01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
PID||73051213886^^^^PESEL|17741||Grabowska^Katarzyna||19730512|F|||Solna&34^^Białystok^^15-424|||||||||
PV1|1|I|12113^^^^^^^^Ginekologia&GIN&HIS||||||||||||||||||||||||||||||||||||||||||||||||||
IN1|||134&HIS|Mazowiecka Kasa Chorych&07R
ORC|NW|17741-1-249^HIS||13235782^HIS|||^^^200110191339^^13&RUTYNOWE&R&HIS^||200110191340|||132^Stępień^Marek^T.^^dr med^^HIS|||||1234^Ginekologia&GIN^HIS|||
OBR|1|17741-1-249^HIS||1234^Badanie moczu&BSPMOCZ^HIS|||20011019||||||Antykoagulanty&NIE~Infuzje&NIE~Went.wspomagana&NIE~Went.kontrolowana&TAK~Tlenoterapia&TAK~Fototerapia&TAK||2323^Krew&KREW^HIS^^^^^SampleID&123456~Comment&komentarz|132^Stępień^Marek^T.^^dr med^^HIS|||||||||||||||
```

---

## 2

```
MSH|^~\&|CLININET|UHC|Moduł diagn.||20020603121707||ORM^O01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
PID||73051213886^^^^PESEL|17741||Pawłowska^Weronika||19730512|F|||Lipowa&34^^Rzeszów^^35-302|||||||||
PV1|1|O|||||||||||||||||||||||||||||||||||||||||||||||||||
IN1|||134&HIS|Mazowiecka Kasa Chorych&07R
ORC|NW|17741-2-1^HIS||1345782^HIS|||^^^200110041555^^13&RUTYNOWE&R&HIS^||200110041556|||132^Walczak^Ryszard^^^^dr med^^HIS|||||1234^Pracownia Pulmonologiczna&P-PA^HIS|||
OBR|1|17741-2-1^HIS||232^Biochemia&BIOCH^HIS|||20011004|||||||||132^Stępień^Marek^T.^^dr med^^HIS||||||||||||||||||||||||||||
ORC|NW|17741-2-2^HIS||1345782^HIS|||^^^200110041555^^13&RUTYNOWE&R&HIS^|17741-2-1&HIS|200110041556|||132^Stępień^Marek^T.^^dr med^^HIS|||||1234^Pracownia Pulmonologiczna&P-PA^HIS|||
OBR|2|17741-2-2^HIS||2323^Alat&ALAT^HIS|||20011004|||||||||132^Stępień^Marek^T.^^dr med^^HIS|||||||||||||17741-2-1&HIS|||||||||||||||
ORC|NW|17741-2-3^HIS||1345782^HIS|||^^^200110041555^^13&RUTYNOWE&R&HIS^|17741-2-1&HIS|200110041556|||132^Stępień^Marek^T.^^dr med^^HIS|||||1234^Pracownia Pulmonologiczna&P-PA^HIS|||
OBR|3|17741-2-3^HIS||2324^Aspat&ASPAT^HIS|||20011004|||||||||132^Stępień^Marek^T.^^dr med^^HIS||||||||||||17741-2-1&HIS||||||||||||||||
ORC|NW|17741-2-4^HIS||1345782^HIS|||^^^200110041555^^13&RUTYNOWE&R&HIS^|17741-2-1&HIS|200110041556|||132^Stępień^Marek^T.^^dr med^^HIS|||||1234^Pracownia Pulmonologiczna&P-PA^HIS|||
OBR|4|17741-2-4^HIS||2345^Krea&KREA^HIS|||20011004|||||||||132^Stępień^Marek^T.^^dr med^^HIS|||||||||||||17741-2-1&HIS|||||||||||||||
```

---

## 3

```
MSH|^~\&|CLININET|UHC|Moduł diagn.||20020603121707||ORM^O01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
PID||73051213886^^^^PESEL|17741||Michalska^Dorota||19730512|F|||Kolejowa&34^^Toruń^^87-100|||||||||
PV1|1|O|||||||||||||||||||||||||||||||||||||||||||||||||||
IN1|||134&HIS|Mazowiecka Kasa Chorych&07R
ORC|XO|23-2-83^HIS||3242232^HIS|||||200109261114|||132^Borkowski^Jerzy^^^^dr med^^HIS|12456^^^^^^^1^Ginekologia&GIN&HIS||||1234^Pracownia 1&ADA^HIS|||
OBR|1|23-2-83^HIS||2324^Aspat&ASPAT^HIS||||||||||||132^Borkowski^Jerzy^^^^dr med^^HIS||||||||||||||||||||||||||||
```

---

## 4

```
MSH|^~\&|CLININET|UHC|Moduł diagn.||20020603121707||ORM^O01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
ORC|CA|17770-1-158^HIS|||||||||||
OBR||17770-1-158^HIS||2324^Aspat&ASPAT^HIS|||||||||||||||||||||||||||
NTE|1|P|*** Testowa przyczyna anulowania L1 ***
NTE|2|P|*** Testowa przyczyna anulowania L2 ***
```

---

## 5

```
MSH|^~\&|Moduł diagn.||CLININET|UHC|20020603121707||ORM^O01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
PID||73051213886^^^^PESEL|17741||Sikora^Magdalena||19730512|F|||Ogrodowa&34^^Lublin^^20-075|||||||||
PV1|1|I|12113^^^^^^^^Ginekologia&GIN&HIS||||||||||||||||||||||||||||||||||||||||||||||||||
IN1|||134&HIS|Mazowiecka Kasa Chorych&07R
ORC|NW||17741-1-249^LAB||||^^^200110191339^^13&RUTYNOWE&R&HIS^||200110191340|||132^Stępień^Marek^T.^^dr med^^HIS|||||1234^Ginekologia&GIN^HIS|||
OBR|1||17741-1-249^LIS|1234^Badanie moczu&BSPMOCZ^HIS|||20011019|||||||200110190900|2323^Krew&KREW^HIS^^^^^SampleID&123456~Comment&krew pobrano po zjedzeniu cukierka|132^Stępień^Marek^T.^^dr med^^HIS||||||||||||||
```

---

## 6

```
MSH|^~\&|Moduł diagn.||CliniNET|UHC|20020603121707||ORM^O01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
ORC|SC|17770-1-158^HIS|||CM||||||||
OBR||17770-1-158^HIS||2324^Aspat&ASPAT^HIS|||||||||||||||||||||||||||
NTE|1|P|*** Testowa przyczyna zmiany statusu L1 ***
NTE|2|P|*** Testowa przyczyna zmiany statusu L2 ***
```

---

## 7

```
MSH|^~\&|Moduł diagn.||CliniNET|UHC|20020603121707||ORU^R01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
ORC|RE|17578-1-49^HIS|
OBR|1|57520-1-18^HIS||25454^Morfologia&MORF^HIS|||20010925000000|||||||||GIN
OBX|1|NM|335^HCT&HCT^LAB|N|39.4|%|(36 - 46)||||F|||20010926240000||132^Stępień^Marek^T.^^dr med.^^HIS
OBX|2|NM|336^HGB&HGB^LAB|N|13.30|g/dl|(11,5 - 15,0)||||F|||20010926240000||132^Stępień^Marek^T.^^dr med.^^HIS
OBX|3|NM|337^MCH&MCH^LAB|N|29.9|pg|(27 - 31)||||F|||20010926240000||132^Stępień^Marek^T.^^dr med.^^HIS
OBX|4|NM|338^MCHC&MCHC^LAB|N|33.8|g/dl|(32 - 36)||||F|||20010926240000||132^Stępień^Marek^T.^^dr med.^^HIS
OBX|5|NM|339^MCV&MCV^LAB|N|88.5|fl|(84 - 98)||||F|||20010926240000||132^Stępień^Marek^T.^^dr med.^^HIS
OBX|6|NM|340^PLT&PLT^LAB|N|239.0|10e3/uL|(130 - 400)||||F|||20010926240000||132^Stępień^Marek^T.^^dr med.^^HIS
OBX|7|NM|341^RBC&RBC^LAB|N|4.45|10e6/uL|(3,7 - 5,0)||||F|||20010926240000||132^Stępień^Marek^T.^^dr med.^^HIS
OBX|8|NM|342^WBC&WBC^LAB|N|9.70|10e3/uL|(4,0 - 10,0)||||F|||20010926240000||132^Stępień^Marek^T.^^dr med.^^HIS
```

---

## 8

```
MSH|^~\&|Moduł diagn.||CliniNET|UHC|20020603121707||ORU^R01|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
ORC|RE|17578-1-49^HIS|
OBR||17578-1-49^HIS||25422^Morfologia&MORF^HIS|||200203061549|||||||||||||||||||
OBX|1|FT|||Wprowadzenie wyników z polskimi znaczkami: żźąęŻŹĄŚĘÓŃóń\.br\--- test 1 ---\.br\radiolog Jan||||||F|||200203061549|
```

---

## 9

```
MSH|^~\&|CLININET|UHC|Moduł diagn.||20020603121707||ACK|CLININET20020603121707|P|2.3|||AL|NE|POL||PL|
MSA|CA|||
```

---

## 10

```
MSH|^~\&|SZPM||SYZ1||20030526103638||ORM^O01|SZ01F28|T|2.3|||||PL|CP1250|PL
PID|1||75721||Rutkowska^Elżbieta||19850411|F|||,^^Ciechocinek
PV1|1|I|OD13
IN1|1||02R
ORC|NW|1115610|||||^^^^^R|1115610|20030526103100|||175^Chmielewska-Pietrzak Agnieszka|||||OD13
OBR|1|1115610||RTG||||||||||||175^Górska Jolanta||||||||HL7|||||1115610
NTE|1|P|klatki piersiowej
```

---

## 11

```
MSH|^~\&|SZPM||LABHL7||20070716112609||ORM^O01|1E273|P|2.3|||AL||PL|CP1250|PL
PID|1|68032000001|2121||Wysocka^Beata||19680320|F|||^^Zabrze
PV1|1|O|PPOB||||||||||||||||4735.5418
IN1|1||12
ORC|NW|54942|||||^^^20070716112602^^R||20070716112504|||49999^Adamczyk^Joanna|||||PPOB^Punkt pobrań
OBR|1|54942||OB^Odczyn opadania krwinek czerwonych|||20070716112504|||2^PIK^PIK||||20070716112602|KP&Krew pełna&SZPM|49999^Adamczyk^Joanna||800002981||||||LHL7
```

---

## 12

```
MSH|^~\&|SZPM|SYS|SYZ1|20040112112303||ACK|SZPM#97347954|T|2.3|||AL|AL|PL|CP1250|PL
MSA|CA|SYZ1#34454|||
```

---

## 13

```
MSH|^~\&|SZPM|SYS|SYS|SYZ1|20040112112303||ACK|SZPM#103750245|T|2.3|||AL|AL||PL|CP1250|PL
MSA|AA|SYZ1#34454|||
```

---

## 14

```
MSH|^~\&|SZPM||PRDIAG||20120123125736||ORM^O01|SZ23592|P|2.3|||AL|AL|PL||PL
PID|1||1782^^^SZPM||Mazurkiewicz^Roman||19530101|M|||
PV1|1|I|WEW1^^^^^^^ODC2||||||||||||||||2341.3641|||||||||||||||||||||||||20040201232500
IN1|1||099
ORC|RF|85770|||IP||^^^20120123094200^^R|85770|20120123094200|||2^PIK^PIK^^^^^^^^^^SZPM|ODC2||||WEW1^Oddział wewnętrzny
OBR|1|85770||XA.AORTIC^Angiografia|||20120123094200||||||I20.0|20120123094200|&&|2^PIK^PIK|||5000101|||||ALT|||||85770
```

---

## 15

```
MSH|^~\&|SZPM||PIXEL||20171018111457||ORU^R01|SZSZPM2620B|P|2.3|||AL|AL|PL||PL
PID|1|78010111117|2061^^^SZPM||Wróblewski Ąśćńłśęó^Marek||19780101|M|||&&^^Gliwice^^^^^2468011
PV1|1|I|WEW1^^^^^^^ODC1||||||||||||||||3441|||||||||||||||||||||||||20031209165600
ORC|RE|1251625||||||||||0^^^^^^^^^^^^SZPM
OBR|1|1251625||MORF_Z^Morfologia pełna|||20170512123310||||||||&&|0^^^^^^^^^^^^SZPM
OBX|1|NM|RDW^RDW||1,0|g|11,5-14,5|L|||F|||20170512123300||^Laboratorium Administrator ( ADMIN )
OBX|2|NM|MID^MID||2|g|||||F|||20170512123300||^Laboratorium Administrator ( ADMIN )
OBX|3|NM|MPV^MPV||3|fL|||||F|||20170512123301||^Laboratorium Administrator ( ADMIN )
OBX|4|NM|PDW^PDW||4|10(GSD)|||||F|||20170512123301||^Laboratorium Administrator ( ADMIN )
```

---

## 16

```
MSH|^~\&|ENDOBASE|ENDO_FACILITY|CLININET|UHC|20160301143022||ORU^R01|EB_MSG_4501|P|2.3|||AL|NE
PID|1||PAT12345^^^^PI||Dudek^Tomasz||19650215|M|||Krakowska 12^^Warszawa^^00-950
PV1|1|I|ENDO1^^^^^^^Endoskopia||||||||||||||||V20160301-001
OBR|1||RPT-88123|ENDO^Endoscopy Report|||20160301142500|||||||||||||||||||F
OBX|1|FT|RPT^Report Text||Badanie endoskopowe górnego odcinka przewodu pokarmowego.\.br\Przełyk: prawidłowy, bez zmian patologicznych.\.br\Żołądek: błona śluzowa trzonu żołądka różowa, bez nadżerek.\.br\Dwunastnica: opuszka prawidłowa, bez owrzodzeń.\.br\Wniosek: Obraz endoskopowy w granicach normy.\.br\Zalecenia: kontrola za 12 miesięcy.||||||F|||20160301143000||234^Marciniak^Andrzej^^dr med.
```

---

## 17

```
MSH|^~\&|ENDOBASE|ENDO_FACILITY|CLININET|UHC|20160301140000||ORM^O01|EB_ORD_7722|P|2.3|||AL|NE
PID|1||PAT12345^^^^PI||Dudek^Tomasz||19650215|M|||Krakowska 12^^Warszawa^^00-950
PV1|1|I|ENDO1^^^^^^^Endoskopia
ORC|NW|ENDO-ORD-001||||||||20160301140000
OBR|1|ENDO-ORD-001||HPYLORI^Helicobacter pylori test|||20160301140000|||||||||||||||||||||||||||
```

---

## 18

```
MSH|^~\&|ENDOBASE|ENDO_FACILITY|CLININET|UHC|20160301145500||ORU^R01|EB_MSG_4502|P|2.3|||AL|NE
PID|1||PAT67890^^^^PI||Szewczyk^Maria||19720918|F|||Piłsudskiego 5^^Kraków^^31-110
PV1|1|I|ENDO1^^^^^^^Endoskopia||||||||||||||||V20160301-002
OBR|1||RPT-88124|COLON^Kolonoskopia|||20160301144000|||||||||||||||||||F
OBX|1|FT|RPT^Report Text||Kolonoskopia do kątnicy.\.br\Kątnica: ujście wyrostka widoczne, prawidłowe.\.br\Wstępnica: błona śluzowa różowa.\.br\Poprzecznica: prawidłowa.\.br\Zstępnica: polip 5mm na szypule usunięty kleszczami.\.br\Esica i odbytnica: bez zmian.\.br\Wniosek: polip zstępnicy - usunięty, materiał do histopatologii.||||||F|||20160301145400||567^Pietrzak^Paweł^^dr
OBX|2|ED|IMG^Endoscopy Image 1||ENDOBASE^image^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DhAQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQU FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAAQABADASIAAhEBAxEB/8QA FgABAQEAAAAAAAAAAAAAAAAABwgJ/8QAJRAAAgIBAwMFAQAAAAAAAAAAAQIDBAUABhEHEiETMUFRYXH/xAAV AQEBAAAAAAAAAAAAAAAAAAADBf/EABwRAAICAgMAAAAAAAAAAAAAAAECAAMEERIhMf/aAAwDAQACEQMRAD8A yb2zuHK7WzUOXwV+XG5GAnsnhba9PqDyIIIIIBBHBBAI1qHpn190/wBQ9s4zcWIzMMkF6FZfRklQTQsR y0UqE8pIh4ZSPBGsb6Mdadwbe3fj8Y+VuT4G5cIi3Y+Xs2Io2buWYKzjgAjyGBU+efB1d/T7e1vanUH DZjaeSk27m4pz6d2hNKIZkkMbgOQQCVIJVhyp5BBKkAr8jDXSqRUHqb2v//Z||||||F|||20160301145400
OBX|3|ED|IMG^Endoscopy Image 2||ENDOBASE^image^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DhAQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQU FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAAIAAgDASIAAhEBAxEB/8QA FAABBQAAAAAAAAAAAAAAAAAAAAcICf/EACEQAAICAgICAwEAAAAAAAAAAAECAwQFBhEHIQAIEhMi/8QAFQEB AQAAAAAAAAAAAAAAAAAAAAL/xAAYEQEBAQEBAAAAAAAAAAAAAAABAAIREv/aAAwDAQACEQMRAD8Al91d k5namex+awOUnw+XxsyWKt2rIY5YpFPKsp+wR8+R8ggg10R0Z3rnuptlYjd+Enki3PioY5L+jzjkz2EA 5kiY/ckUjlSPIHB1T/fDuXYW5+sGJwG2s3BkamGxKC5JSyKSxLM7gCQAj/ELII3hh44IKkEVfyOxdhb /wCrOSwG6cTFnMHaiBnsWKscUkMiGNwHAIBKkEqw5U/BIJUgGnqGLGU0M//Z||||||F|||20160301145400
```

---

## 19

```
MSH|^~\&|ENDOBASE|ENDO_FACILITY|CLININET|UHC|20160302091000||ORU^R01|EB_MSG_4503|P|2.3|||AL|NE
PID|1||PAT11223^^^^PI||Sokołowski^Adam^Stanisław||19800305|M|||Mickiewicza 22^^Łódź^^90-001
PV1|1|O|ENDO1^^^^^^^Endoskopia||||||||||||||||V20160302-003
OBR|1||RPT-88125|GASTRO^Gastroskopia|||20160302090000|||||||||||||||||||F
OBX|1|FT|RPT^Report Text||Gastroskopia diagnostyczna.\.br\Przełyk: prawidłowy.\.br\Wpust: zamyka się prawidłowo.\.br\Żołądek: w trzonie żołądka 2 nadżerki płaskie do 3mm, lekki rumień błony śluzowej antrum.\.br\Dwunastnica: prawidłowa.\.br\Wniosek: gastropatia nadżerkowa. Pobrano biopsje z antrum na H. pylori.||||||F|||20160302090900||234^Marciniak^Andrzej^^dr med.
OBX|2|ED|PDF^Report PDF||ENDOBASE^application^PDF^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFn ZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0K L0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5 cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMg NCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQg MCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDE4IFRmCjEwMCA3MDAgVGQKKEdh c3Ryb3Nrb3BpYSAtIFd5bmlrKSBUagoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8Ci9U eXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoK eHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMMDQ 4IDAwMDAwIG4gCjAwMDAwMDAxMzEgMDAwMDAgbiAKMDAwMDAwMDMxNCAwMDAwMCBuIAowMDAwMDAw NDA5IDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNgovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYK NDgyCiUlRU9G||||||F|||20160302090900
```

---

## 20

```
MSH|^~\&|RIS_NETRAAD||SZPM||20210315083000||ORU^R01|RIS_WYN_99281|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|85042312345|9921^^^SZPM||Baran^Anna||19850423|F|||Słoneczna 7^^Kraków^^^^^2461011
PV1|1|I|RTGEN^^^^^^^ODC1^Radiologia||||||||||||||||6782.8901
IN1|1||06
ORC|RE|2987345
OBR|1|2987345||RTG_KP^RTG klatki piersiowej PA|||20210315082000|20210315083000||||||||&&|0^^^^^^^^^^^^SZPM||123e4567-e89b-12d3-a456-426614174000||||RTGEN^TK1|F||1
OBX|1|FT|RTG_KP^RTG klatki piersiowej PA||Klatka piersiowa PA.\.br\Płuca rozprężone, bez zmian ogniskowych i naciekowych.\.br\Sylwetka serca w normie.\.br\Przepona gładka.\.br\Kąty przeponowo-żebrowe wolne.\.br\Wniosek: obraz radiologiczny klatki piersiowej w normie.||||||F|||20210315083000||111^Grabowski^Marek^^dr~222^Wróbel^Ewa^^dr
OBX|2|ED|MJPG^Miniatura RTG||RIS_NETRAAD^image^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAoHBwgHBgoICAgLCgoLDhgQDg0NDh0VFhEYIx8lJCIf IiEmKzcvJik0KSEiMEExNDk7Pj4+JS5ESUM8SDc9Pjv/2wBDAQoLCw4NDhwQEBw7KCIoOzs7Ozs7 Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozv/wAARCAAQABADASIA AhEBAxEB/8QAFwAAAwEAAAAAAAAAAAAAAAAABQYHCP/EACUQAAICAgEDBAMAAAAAAAAAAAECAwQFEQYB IUETMWFxBxKR/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAf/xAAcEQACAgIDAAAAAAAAAAAAAAABAgADERIh QfD/2dAMBAQACEQMRAD8Aly3XZ3JYfG5OfPYzF16m7X45I5nkmbnlQdvJHFAO8ADkknkknWuei/U/ Tfe/HPB7kxUWXxskgkMUhZGRwCFdHXlXGiRz4JBBKmoW48HqDqPgM7sPKzbcz9GsSjW6NWSCdJUK OrKQRypBIIPs6kEECx+QPy7u3FdT8bgdr5WSphsYm7EcsyyRSSsyICXIIyqFQBvDD2IBJ+hizHUY OrdT/9k=||||||F|||20210315083000
```
