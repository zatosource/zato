# P1/EDM Platform (Polish national e-health) - real HL7v2 ER7 messages

---

## 1

```
MSH|^~\&|SZPM||SYZ1||20030526103638||ORM^O01|SZ01F28|T|2.3|||||PL|CP1250|PL
PID|1||75721||Wierzbicka^Elżbieta||19850411|F|||,^^Ciechocinek
PV1|1|I|OD13
IN1|1||02R
ORC|NW|1115610|||||^^^^^R|1115610|20030526103100|||175^Drzewicka-Lisowska Halina|||||OD13
OBR|1|1115610||RTG||||||||||||175^Drzewicka Halina||||||||HL7|||||1115610
NTE|1|P|klatki piersiowej
```

---

## 2

```
MSH|^~\&|SZPM||LABHL7||20070716112609||ORM^O01|1E273|P|2.3|||AL||PL|CP1250|PL
PID|1|68032000001|2121||Sokołowska^Waldemara||19680320|F|||^^Zabrze
PV1|1|O|PPOB||||||||||||||||4735.5418
IN1|1||12
ORC|NW|54942|||||^^^20070716112602^^R||20070716112504|||49999^Krajewska^Janina|||||PPOB^Punkt pobrań
OBR|1|54942||OB^Odczyn opadania krwinek czerwonych|||20070716112504|||2^PIK^PIK||||20070716112602|KP&Krew pełna&SZPM|49999^Krajewska^Janina||800002981||||||LHL7
```

---

## 3

```
MSH|^~\&|SZPM|SYS|SYZ1|20040112112303||ACK|SZPM#97347954|T|2.3|||AL|AL|PL|CP1250|PL
MSA|CA|SYZ1#34454|||
```

---

## 4

```
MSH|^~\&|SZPM|SYS|SYS|SYZ1|20040112112303||ACK|SZPM#103750245|T|2.3|||AL|AL||PL|CP1250|PL
MSA|AA|SYZ1#34454|||
```

---

## 5

```
MSH|^~\&|SZPM||PRDIAG||20120123125736||ORM^O01|SZ23592|P|2.3|||AL|AL|PL||PL
PID|1||1782^^^SZPM||Orzechowski^Romanisko||19530101|M|||
PV1|1|I|WEW1^^^^^^^ODC2||||||||||||||||2341.3641|||||||||||||||||||||||||20040201232500
IN1|1||099
ORC|RF|85770|||IP||^^^20120123094200^^R|85770|20120123094200|||2^PIK^PIK^^^^^^^^^^SZPM|ODC2||||WEW1^Oddział wewnętrzny
OBR|1|85770||XA.AORTIC^Angiografia|||20120123094200||||||I20.0|20120123094200|&&|2^PIK^PIK|||5000101|||||ALT|||||85770
```

---

## 6

```
MSH|^~\&|SZPM||PIXEL||20171018111457||ORU^R01|SZSZPM2620B|P|2.3|||AL|AL|PL||PL
PID|1|78010111117|2061^^^SZPM||Zaręba Ąśćńłśęó^Marek||19780101|M|||&&^^Gliwice^^^^^2468011
PV1|1|I|WEW1^^^^^^^ODC1||||||||||||||||3441|||||||||||||||||||||||||20031209165600
ORC|RE|1251625||||||||||0^^^^^^^^^^^^SZPM
OBR|1|1251625||MORF_Z^Morfologia pełna|||20170512123310||||||||&&|0^^^^^^^^^^^^SZPM
OBX|1|NM|RDW^RDW||1,0|g|11,5-14,5|L|||F|||20170512123300||^Laboratorium Administrator ( ADMIN )
OBX|2|NM|MID^MID||2|g|||||F|||20170512123300||^Laboratorium Administrator ( ADMIN )
OBX|3|NM|MPV^MPV||3|fL|||||F|||20170512123301||^Laboratorium Administrator ( ADMIN )
OBX|4|NM|PDW^PDW||4|10(GSD)|||||F|||20170512123301||^Laboratorium Administrator ( ADMIN )
```

---

## 7

```
MSH|^~\&|RIS||SZPM||20210407100000||ORU^R01|RIS_WYN_P1_001|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|85042312345|9921^^^SZPM||Bogucka^Anna||19850423|F|||Słoneczna 7^^Kraków^^^^^2461011
PV1|1|I|RTGEN^^^^^^^ODC1^Radiologia||||||||||||||||6782.8901
IN1|1||06
ORC|RE|2987345
OBR|1|2987345||TK_GL^TK głowy bez kontrastu|||20210407093000|20210407100000||||||||&&|0^^^^^^^^^^^^SZPM||123e4567-e89b-12d3-a456-426614174000||||RTGEN|F||1
OBX|1|FT|TK_GL^TK głowy||Tomografia komputerowa głowy bez kontrastu.\.br\Układ komorowy symetryczny, nieposzerzony.\.br\Struktury linii środkowej nieprzesunięte.\.br\Przestrzenie płynowe przymózgowe prawidłowe.\.br\Bez cech krwawienia wewnątrzczaszkowego.\.br\Zatoki przynosowe powietrzne.\.br\Wniosek: obraz TK głowy w granicach normy.||||||F|||20210407100000||111^Tomczyk^Marek^^dr~222^Żurek^Ewa^^dr
OBX|2|NM|DLP^DLP (Dose Length Product)||580|mGy*cm|||||F|||20210407100000
OBX|3|NM|CTDI^CTDIvol||45.2|mGy|||||F|||20210407100000
```

---

## 8

```
MSH|^~\&|SZPM||SYZ1||20210510080000||ADT^A28|SZPM_ADT_001|P|2.3|||AL|AL|PL|CP1250|PL
EVN|A28|20210510080000
PID|1|92031567890|12345^^^SZPM||Lisowska^Maria^Grażyna^^||19920315|F|||Słowackiego&12^^Wrocław^^^^^0264011||||||||||||PL
PV1|1|O|POZ1^^^^^^^POZ1^Poradnia ogólna
```

---

## 9

```
MSH|^~\&|SZPM||SYZ1||20210510090000||ADT^A31|SZPM_ADT_002|P|2.3|||AL|AL|PL|CP1250|PL
EVN|A31|20210510090000
PID|1|92031567890|12345^^^SZPM||Nowotna-Lisowska^Maria^Grażyna^^||19920315|F|||Krakowska&25^^Wrocław^^^^^0264011||||||||||||PL
PV1|1|O|POZ1^^^^^^^POZ1^Poradnia ogólna
```

---

## 10

```
MSH|^~\&|SZPM||SYZ1||20210601120000||ADT^A01|SZPM_ADT_003|P|2.3|||AL|AL|PL|CP1250|PL
EVN|A01|20210601120000
PID|1|55010199999|3344^^^SZPM||Rakowski^Jan^Tadeusz^^||19550101|M|||Piłsudskiego&7^^Łódź^^^^^1061011||||||||||||PL
PV1|1|I|WEW1^^^^^^^ODC1^Oddział wewnętrzny||||||||||||||||8901.1234^^^SZPM^VN^KSG|||||||||||||||||||||||||20210601120000
IN1|1||06
DG1|1||I25.0^Miażdżycowa choroba serca||20210601|A
```

---

## 11

```
MSH|^~\&|SZPM||SYZ1||20210608100000||ADT^A03|SZPM_ADT_004|P|2.3|||AL|AL|PL|CP1250|PL
EVN|A03|20210608100000
PID|1|55010199999|3344^^^SZPM||Rakowski^Jan^Tadeusz^^||19550101|M|||Piłsudskiego&7^^Łódź
PV1|1|I|WEW1^^^^^^^ODC1^Oddział wewnętrzny||||||||||||||||8901.1234^^^SZPM^VN^KSG|||||||||||||||||||||||||20210601120000|||20210608100000
```

---

## 12

```
MSH|^~\&|SZPM||SYZ1||20210515140000||ADT^A30|SZPM_ADT_005|P|2.3|||AL|AL|PL|CP1250|PL
EVN|A30|20210515140000
PID|1|92031567890|12345^^^SZPM||Lisowska^Maria^Grażyna||19920315|F
MRG|67890^^^SZPM
```

---

## 13

```
MSH|^~\&|SYZ1||SZPM||20210520090000||QRY^A19|SYZ1_QRY_001|P|2.3|||AL|AL|PL|CP1250|PL
QRD|20210520090000|R|I|SYZ1_QRY_001|||10|92031567890|DEM
```

---

## 14

```
MSH|^~\&|SZPM||SYZ1||20210520090001||ADR^A19|SZPM_ADR_001|P|2.3|||AL|AL|PL|CP1250|PL
MSA|AA|SYZ1_QRY_001
QRD|20210520090000|R|I|SYZ1_QRY_001|||10|92031567890|DEM
PID|1|92031567890|12345^^^SZPM||Lisowska^Maria^Grażyna^^||19920315|F|||Słowackiego&12^^Wrocław^^^^^0264011|||||||||||||PL
PV1|1|O|POZ1^^^^^^^POZ1^Poradnia ogólna
```

---

## 15

```
MSH|^~\&|RIS||SZPM||20210610143000||ORU^R01|RIS_WYN_002|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|55010199999|3344^^^SZPM||Rakowski^Jan^Tadeusz||19550101|M|||Piłsudskiego&7^^Łódź^^^^^1061011
PV1|1|I|WEW1^^^^^^^ODC1^Oddział wewnętrzny||||||||||||||||8901.1234
IN1|1||06
ORC|RE|2987400
OBR|1|2987400||USG_BRZUCH^USG jamy brzusznej|||20210610140000|20210610142500||||||||&&|0^^^^^^^^^^^^SZPM||abc12345-e89b-42d3-a456-111222333444||||USG1|F||1
OBX|1|FT|USG_BRZUCH^USG jamy brzusznej||Badanie USG jamy brzusznej.\.br\Wątroba: jednorodna, o prawidłowej echogeniczności, wielkość prawidłowa.\.br\Pęcherzyk żółciowy: bez złogów, ściana niepoggrubiona.\.br\Drogi żółciowe: nieposzerzony.\.br\Trzustka: prawidłowa, widoczna w całości.\.br\Śledziona: prawidłowa (11cm).\.br\Nerki: prawidłowe, bez cech zastoju.\.br\Wniosek: badanie USG jamy brzusznej w granicach normy.||||||F|||20210610142500||333^Markiewicz^Paweł^^dr
```

---

## 16

```
MSH|^~\&|RIS||SZPM||20210615110000||ORU^R01|RIS_WYN_003|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|55010199999|3344^^^SZPM||Rakowski^Jan^Tadeusz||19550101|M|||Piłsudskiego&7^^Łódź
ORC|RE|2987500
OBR|1|2987500||RTG_KP^RTG klatki piersiowej PA|||20210615103000|20210615110000||||||||&&|||def45678-abcd-1234-5678-999888777666||||RTGEN|F
OBX|1|FT|RTG_KP^RTG klatki piersiowej||Płuca rozprężone. Sylwetka serca prawidłowa. Kąty przeponowo-żebrowe wolne.\.br\Wniosek: prawidłowy obraz RTG klatki piersiowej.||||||F|||20210615110000||111^Tomczyk^Marek^^dr
OBX|2|TX|URL^Link PACS||https://pacs.szpital.krakow.pl/wado?requestType=WADO&studyUID=1.2.826.0.1.3680043.8.1055.1&seriesUID=1.2.826.0.1.3680043.8.1055.1.1&objectUID=1.2.826.0.1.3680043.8.1055.1.1.1||||||F|||20210615110000
```

---

## 17

```
MSH|^~\&|RIS||SZPM||20210615095000||ORM^O01|RIS_STA_001|P|2.3|||AL|AL|PL|CP1250|PL
ORC|SC|2987500|||PRZY||^^^20210615100000^^R||20210615095000
OBR|1|2987500||RTG_KP^RTG klatki piersiowej PA|||20210615100000
```

---

## 18

```
MSH|^~\&|RIS||SZPM||20210701150000||ORU^R01|RIS_WYN_ATT_001|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|80052012345|5566^^^SZPM||Kurek^Adam||19800520|M|||Długa&15^^Poznań^^^^^3064011
PV1|1|I|CHIR1^^^^^^^ODC1^Chirurgia ogólna||||||||||||||||9012.3456
IN1|1||06
ORC|RE|3100200
OBR|1|3100200||TK_BRZUCH^TK jamy brzusznej z kontrastem|||20210701140000|20210701150000||||||||&&|||aaa11111-bbbb-2222-cccc-333344445555||||RTGEN^TK1|F||1
OBX|1|FT|TK_BRZUCH^TK jamy brzusznej||TK jamy brzusznej z dożylnym podaniem kontrastu.\.br\Wątroba: w segmencie VII ognisko hipodensyjne 15mm, wzmacniające się obwodowo po kontraście - charakter naczyniaka.\.br\Trzustka, śledziona, nadnercza: prawidłowe.\.br\Nerki: bez zmian ogniskowych, bez zastoju.\.br\Aorta brzuszna: prawidłowa.\.br\Węzły chłonne: niepowiększone.\.br\Wniosek: naczyniak wątroby segment VII (15mm). Poza tym obraz w normie.||||||F|||20210701150000||444^Kosinski^Tomasz^^dr~555^Sokołowska^Ewa^^dr
OBX|2|NM|DLP^DLP||890|mGy*cm|||||F|||20210701150000
OBX|3|ED|PDF^Raport TK PDF||RIS^application^PDF^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFn ZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0K L0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5 cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMg NCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQg MCBvYmoKPDwKL0xlbmd0aCA1Mgo+PgpzdHJlYW0KQlQKL0YxIDE4IFRmCjEwMCA3MDAgVGQKKFRL IGphbXkgYnJ6dXN6bmVqIC0gUmFwb3J0KSBUagoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2Jq Cjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+Pgpl bmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAw MDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDE0MSAwMDAwMCBuIAowMDAwMDAwMzI0IDAwMDAwIG4g CjAwMDAwMDA0MjcgMDAwMDAgbiAKdHJhaWxlcgo8PAovU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0 YXJ0eHJlZgo1MTIKJSVFbZ==||||||F|||20210701150000
```

---

## 19

```
MSH|^~\&|RIS||SZPM||20210702080000||ORU^R01|RIS_WYN_IMG_001|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|75050512345|7789^^^SZPM||Drzewicka^Katarzyna||19750505|F|||Mickiewicza&8^^Gdańsk^^^^^2264011
PV1|1|O|RTGEN^^^^^^^RTGEN1^Pracownia RTG||||||||||||||||9876.5432
IN1|1||06
ORC|RE|3200100
OBR|1|3200100||MMG^Mammografia|||20210702073000|20210702080000||||||||&&|||bbb22222-cccc-3333-dddd-444455556666||||RTGEN^MMG1|F||1
OBX|1|FT|MMG^Mammografia||Mammografia obu piersi w projekcjach CC i MLO.\.br\Pierś prawa: tkanka gruczołowa typu C wg ACR. Bez zmian ogniskowych podejrzanych.\.br\Pierś lewa: mikrozwapnienia skupione w kwadrancie górnym zewnętrznym - wymagają dalszej diagnostyki (BI-RADS 4A).\.br\Wniosek: BI-RADS 4A strona lewa - zalecana biopsja.||||||F|||20210702080000||666^Bogucka^Agnieszka^^dr
OBX|2|ED|MJPG^Miniatura mammografia||RIS^image^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DhAQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQU FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAAIAAgDASIAAhEBAxEB/8QA FAABBQAAAAAAAAAAAAAAAAAAAAcICf/EACEQAAICAgICAwEAAAAAAAAAAAECAwQFBhEHIQAIEhMi/8QA FQEBAQAAAAAAAAAAAAAAAAAAAAL/xAAYEQEBAQEBAAAAAAAAAAAAAAABAAIREv/aAAwDAQACEQMRAD8A kd1dk5bamXyGax2VnxGXx06WKlyuIY5IpEPKsp+iR8+RIQR7cEEVPRXdm5OptmYfdmHnkit2HxaC 7JSJqRZy7hyY0PvJFI5VlPkDg6Zvvj3JsLc/WDG4DbOZgyNbDYlBckxhFZYlmdwBIAR/iFkEeGHjggqZVf/2Q==||||||F|||20210702080000
```

---

## 20

```
MSH|^~\&|RIS||SZPM||20210703140000||ORU^R01|RIS_WYN_COR_001|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|55010199999|3344^^^SZPM||Rakowski^Jan^Tadeusz||19550101|M|||Piłsudskiego&7^^Łódź
ORC|RE|2987400
OBR|1|2987400||USG_BRZUCH^USG jamy brzusznej|||20210610140000|20210703140000||||||||&&|||abc12345-e89b-42d3-a456-111222333444||||USG1|C||1
OBX|1|FT|USG_BRZUCH^USG jamy brzusznej||KOREKTA WYNIKU.\.br\Badanie USG jamy brzusznej.\.br\Wątroba: jednorodna, prawidłowa echogeniczność. W segmencie VI ognisko hiperechogeniczne 8mm - charakter naczyniaka.\.br\Pęcherzyk żółciowy: bez złogów.\.br\Drogi żółciowe: nieposzerzony.\.br\Trzustka, śledziona, nerki: prawidłowe.\.br\Wniosek: naczyniak wątroby segment VI (8mm). Poza tym badanie w normie.\.br\UWAGA: korekta - w pierwszym opisie nie uwzględniono ogniska w segmencie VI.||||||C|||20210703140000||333^Markiewicz^Paweł^^dr
```
