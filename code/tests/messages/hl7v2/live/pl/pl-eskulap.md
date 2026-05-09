# Eskulap (medhub/RightSoft) - real HL7v2 ER7 messages

---

## 1. ORU^R01 - radiology result from CHAZON RIS (chest X-ray description)

```
MSH|^~\&|2|CHAZON2|1|CHAZON|20081222110953798||ORU^R01|CHAZON220081222110953798|P|2.3|||||POL||PL
PID||46911|7HG2K|03220400779^^^^P|Sobczak^Tomasz||20030204|M|||Spokojna 13^^Wrocław^^|04||||||||||||||||PL
OBR|1|3212|125773|416^Klatka piersiowa bez kontrastu||||||||||||102^Górecki^Andrzej^^^^^^3234569
OBX|1||13MN2AK|1|Opis testowy klatki piersiowej.||||||F|||20081222110953||51^Kalinowski^Jan^^^^^^5555553
```

---

## 2. ORM^O01 - lab order from Eskulap to external LIS (ESR, routine)

```
MSH|^~\&|ESKUL||LIS01||20190415083022||ORM^O01|ESK19041508|P|2.3|||AL||PL|CP1250|PL
PID|1|90060512345|12450^^^ESKUL||Sadowska^Maria^Elżbieta||19900605|F|||Piłsudskiego 22^^Łódź^^90-101^^^^^1061011
PV1|1|I|INT2^^^^^^^ODC1||||||||||||||||7823.9012|||||||||||||||||||||||20190414070000
IN1|1||07
ORC|NW|234567|||||^^^20190415090000^^R||20190415083000|||1045^Szczepańska^Katarzyna^^^^^^PRZAW&7654321^^^^LEK|||||INT2^Oddział internistyczny
OBR|1|234567||OB^Odczyn Biernackiego|||20190415083000|||3^Kubiak^Anna||||20190415083000|KP&Krew pełna&ESKUL|1045^Szczepańska^Katarzyna||800045123||||||LIS01
NTE|1|P|pilne - podejrzenie zapalenia
```

---

## 3. ORM^O01 - radiology order from Eskulap to RIS (CT head)

```
MSH|^~\&|ESKUL||RIS01||20200918140532||ORM^O01|ESK20091814|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|55031200001|8934^^^ESKUL||Wawrzyniak^Tadeusz||19550312|M|||Mickiewicza 8/3^^Poznań^^60-071^^^^^3064011
PV1|1|I|NEUR^^^^^^^ODC1||||||||||||||||5523.8901|||||||||||||||||||||||20200917120000
IN1|1||01
ORC|NW|345678|||||^^^20200918150000^^S||20200918140500|||2089^Tomczak^Piotr^^^^^^PRZAW&9876543^^^^LEK|ODC1|||NEUR^Oddział neurologiczny
OBR|1|345678||TK.GLOWA^Tomografia komputerowa głowy|||20200918140500||||||G45.0|||||2089^Tomczak^Piotr||||||||RIS01|||||345678
NTE|1|P|CITO - podejrzenie udaru
```

---

## 4. ORU^R01 - lab result (morphology) returned to Eskulap

```
MSH|^~\&|LIS01||ESKUL||20190415143022||ORU^R01|LIS190415001|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|90060512345|12450^^^ESKUL||Sadowska^Maria^Elżbieta||19900605|F|||Piłsudskiego 22^^Łódź^^90-101
PV1|1|I|INT2^^^^^^^ODC1||||||||||||||||7823.9012
ORC|RE|234567|LIS789012||||||20190415143000|||-2^Laboratorium^Admin|||||INT2
OBR|1|234567|LIS789012|MORF^Morfologia|||20190415143000||||||||KP||||||||||F
OBX|1|NM|WBC^Leukocyty^LIS01||7.2|K/uL|4.0-10.0|N|||F|||20190415142800||1122^Kucharska^Ewa^^^^LIS01
OBX|2|NM|RBC^Erytrocyty^LIS01||4.45|M/uL|3.80-5.20|N|||F|||20190415142800||1122^Kucharska^Ewa^^^^LIS01
OBX|3|NM|HGB^Hemoglobina^LIS01||13.8|g/dL|12.0-16.0|N|||F|||20190415142800||1122^Kucharska^Ewa^^^^LIS01
OBX|4|NM|HCT^Hematokryt^LIS01||41.2|%|36.0-46.0|N|||F|||20190415142800||1122^Kucharska^Ewa^^^^LIS01
OBX|5|NM|PLT^Płytki krwi^LIS01||245|K/uL|150-400|N|||F|||20190415142800||1122^Kucharska^Ewa^^^^LIS01
```

---

## 5. ORU^R01 - CT result with text description returned to Eskulap

```
MSH|^~\&|RIS01|RIS|ESKUL|HIS|20200918163045||ORU^R01|RIS20200918_002|P|2.3.1||||||8859/2
PID|1||8934^^^ESKUL||Wawrzyniak^Tadeusz||19550312|M|||Mickiewicza 8/3^^Poznań^^60-071
ORC|RE||RIS345678||||^^^20200918150000^^S|345678|20200918163000|||2089^Tomczak^Piotr|||||NEUR^Oddział neurologiczny
OBR|1||RIS345678|TK.GLOWA^Tomografia komputerowa głowy|||20200918163000||||||||||||||||||F|
OBX|1|FT|||Badanie TK głowy bez kontrastu.\.br\Układ komorowy symetryczny, nieposzerzony.\.br\Nie uwidoczniono cech świeżego krwawienia wewnątrzczaszkowego.\.br\Struktury środkowe nieprzesunięte.\.br\Przestrzenie przymózgowe prawidłowej szerokości.\.br\Wniosek: obraz TK mózgowia w granicach normy.\.br\lek. med. Jan Mróz||||||F|||20200918163000||4523^Mróz^Jan^^^^RIS01
```

---

## 6. ADT^A01 - patient admission (Eskulap to external systems)

```
MSH|^~\&|ESKUL||RIS01||20210305081500||ADT^A01|ADTESK001|P|2.3|||AL||PL|CP1250|PL
EVN||20210305081430
PID|1|82071500001|15623^^^ESKUL||Maciejewski^Robert^Stanisław||19820715|M|||Słowackiego 15/4^^Gdańsk^^80-001^^^^^2264011|||||||||||||||||PL
PV1|1|I|CHIR^^^^^^^ODC2||||||||||||||||2021/K/345^^^ESKUL^VN^KSG
DG1|1||K35.0^Ostre zapalenie wyrostka robaczkowego z uogólnionym zapaleniem otrzewnej^ICD10|||A|||||||||||WST
IN1|1||06
```

---

## 7. ADT^A03 - patient discharge from Eskulap

```
MSH|^~\&|ESKUL||RIS01||20210308143000||ADT^A03|ADTESK002|P|2.3|||AL||PL|CP1250|PL
EVN||20210308142900
PID|1|82071500001|15623^^^ESKUL||Maciejewski^Robert^Stanisław||19820715|M|||Słowackiego 15/4^^Gdańsk^^80-001^^^^^2264011
PV1|1|I|CHIR^^^^^^^ODC2||||||||||||||||2021/K/345^^^ESKUL^VN^KSG
DG1|1||K35.0^Ostre zapalenie wyrostka robaczkowego z uogólnionym zapaleniem otrzewnej^ICD10|||F|||||||||||KON
```

---

## 8. ADT^A31 - patient demographic update with vital signs

```
MSH|^~\&|ESKUL||LIS01||20210305090000||ADT^A31|ADTESK003|P|2.3|||AL||PL|CP1250|PL
EVN||20210305085930
PID|1|82071500001|15623^^^ESKUL||Maciejewski^Robert^Stanisław||19820715|M|||Słowackiego 15/4^^Gdańsk^^80-001
OBX|1|ST|WAG^Waga||82|kg|||||F|||20210305085900
OBX|2|ST|WZR^Wzrost||178|cm|||||F|||20210305085900
```

---

## 9. ORM^O01 - pharmacy order to Eskulap Chemotherapy module (ECH)

```
MSH|^~\&|ECH||APTEKA||20141210094500||ORM^O01|ECH141210001|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|75050800001|9234^^^ESKUL||Lis^Andrzej||19750508|M|||Reymonta 7^^Szczecin^^70-001
PV1|1|I|ONKO^^^^^^^ODC1||||||||||||||||2014/O/892
ORC|NW|ECH78901|||||^^^20141210100000^^S||20141210094500|||3045^Baranowska^Maria
OBR|1|ECH78901||CYKL1^Cyklofosfamid 500mg|||20141210094500
```

---

## 10. ORU^R01 - lab result with additional sub-ordered tests (dozlecenia)

```
MSH|^~\&|LIS01||ESKUL||20200115110000||ORU^R01|LIS200115002|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|67042300001|7821^^^ESKUL||Kolasa^Jerzy||19670423|M|||Kopernika 3^^Katowice^^40-001
PV1|1|I|INT1^^^^^^^ODC1||||||||||||||||6234.7890
ORC|RE|567890|
OBR|1|567890|L1234405|MORF^Morfologia|||20200115105500||||||||||||||||||F|||||
OBX|1|CE|WBC^Leukocyty^LIS01||8.57|m/uL|4.80-10.80|||||F|||20200115105500|
OBX|2|CE|RBC^Erytrocyty^LIS01||6.65|m/uL|4.20-5.40|H||||F|||20200115105500|
OBX|3|CE|HGB^Hemoglobina^LIS01||11.2|g/dL|13.5-17.5|L||||F|||20200115105500|
OBR|2||L1234406|ROZM^Rozmaz mikroskopowy^LIS01|||20200115105500||||||||||||||||||F||||567890^L1234405|
OBX|1|CE|LIM^Limfocyty^LIS01||32|%|19-48|||||F|||20200115105500|
OBX|2|CE|MON^Monocyty^LIS01||1|%|3-9|L||||F|||20200115105500|
```

---

## 11. ADT^A30 - patient merge (two records combined)

```
MSH|^~\&|ESKUL||LIS01||20180612100500||ADT^A30|ADTESK004|P|2.3|||AL||PL|CP1250|PL
EVN||20180612100430
PID|1|65012611110|581^^^ESKUL||Czajka^Adam||19650126|M|||Krótka 5^^Opole^^45-100
MRG|3455~34546~2345
```

---

## 12. QRY^A19 - patient demographic query (by PESEL)

```
MSH|^~\&|ESKRIS||ESKUL||20210610143200||QRY^A19|QRY001|P|2.3
QRD|20210610143200|R|I|1|||1|#78051200001|DEM|
```

---

## 13. ADR^A19 - patient demographic query response

```
MSH|^~\&|ESKUL||ESKRIS||20210610143205||ADR^A19|ADR001|P|2.3
QRD|20210610143200|R|I|1|||1|#78051200001|DEM|
PID|1|78051200001|4521^^^ESKUL||Górecka^Agnieszka||19780512|F|||Długa 12^^Lublin^^20-238
PV1|1|O|POZ1||||||||||||||||2021/P/1234
```

---

## 14. ORM^O01 - comment exchange between Eskulap and external system

```
MSH|^~\&|RIS||ESKUL||20160506130837||ORM^O01|ESKRIS25C52_002|P|2.3|||AL|AL|PL||PL
ORC|KN|75413|||||||||20160510130827|||1^ADMIN^ADMIN^^^^^^^^^^UZY
OBR|1|75413||XA.AORTIC^Angiografia|||||||||||&&|
NTE|1|P|Proszę o dodatkowe zdjęcie w projekcji bocznej|1228109
```

---

## 15. ORM^O01 - order cancellation request

```
MSH|^~\&|ESKUL||LIS01||20200220091500||ORM^O01|ESK200220CA|P|2.3|||AL||PL|CP1250|PL
PID|1|80011500001|9876^^^ESKUL||Baranowski^Paweł||19800115|M|||Nowa 3^^Bydgoszcz^^85-001
PV1|1|I|INT1^^^^^^^ODC1||||||||||||||||5678.2345
IN1|1||03
ORC|CA|456789|||||^^^20200220100000^^R||20200220091400|||1234^Kucharski^Jan|||||INT1
OBR|1|456789||MORF^Morfologia|||20200220091400
```

---

## 16. ORU^R01 - result with PDF report attachment (base64-encoded)

```
MSH|^~\&|RIS01||ESKUL||20211103141500||ORU^R01|RIS211103PDF|P|2.5|||AL|AL|PL|CP1250|PL
PID|1|91022300001|18234^^^ESKUL||Maciejewska^Katarzyna||19910223|F|||Kwiatowa 9^^Białystok^^15-001
PV1|1|I|NEUR^^^^^^^ODC1||||||||||||||||2021/N/567
ORC|RE|678901|RIS112233
OBR|1|678901|RIS112233|MRI.GLOWA^Rezonans magnetyczny głowy|||20211103140000||||||||||||||||||F
OBX|1|FT|||Badanie MRI głowy z kontrastem.\.br\Nie uwidoczniono zmian ogniskowych w obrębie mózgowia.\.br\Układ komorowy symetryczny, prawidłowej szerokości.\.br\Przysadka mózgowa prawidłowych wymiarów.\.br\Wniosek: obraz MRI mózgowia prawidłowy.||||||F|||20211103141000||5678^Sadowski^Marek^^^^RIS01
OBX|2|ED|ZAL||Raport MRI^mri_raport_20211103.pdf^PDF^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSAgNCAwIFIKPj4KPj4KL0NvbnRlbnRzIDUgMCBSCj4+CmVuZG9iago0IDAgb2JqCjw8IC9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKNSAwIG9iago8PCAvTGVuZ3RoIDQ0ID4+CnN0cmVhbQpCVAovRjEgMTggVGYKMCAwIFRkCihNUkkgUmVwb3J0KSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZgowMDAwMDAwMDA5IDAwMDAwIG4KMDAwMDAwMDA1OCAwMDAwMCBuCjAwMDAwMDAxMTUgMDAwMDAgbgowMDAwMDAwMjA2IDAwMDAwIG4KMDAwMDAwMDI4NCAwMDAwMCBuCnRyYWlsZXIKPDwgL1NpemUgNgovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKMzc4CiUlRU9GCg==||||||F
```

---

## 17. ORU^R01 - result with JPEG image thumbnail (base64-encoded)

```
MSH|^~\&|RIS01||ESKUL||20210415095500||ORU^R01|RIS210415IMG|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|88030100001|16789^^^ESKUL||Szczepański^Marcin||19880301|M|||Polna 7^^Rzeszów^^35-001
ORC|RE|789012|
OBR|1|789012||RTG.KLP^RTG klatki piersiowej PA|||20210415094500||||||||||||||||||F|
OBX|1|FT|||Obraz radiologiczny klatki piersiowej w normie.\.br\Pola płucne jasne, bez zmian ogniskowych i naciekowych.\.br\Sylwetka serca prawidłowa.\.br\Przepony gładkie, kąty przeponowo-żebrowe wolne.||||||F|||20210415095000|
OBX|2|RP|URL^Obraz DICOM|1|http://pacs.eskulap.local/wado?requestType=WADO&studyUID=2.16.840.1.113669.632.20.121711.10024&seriesUID=1.3.12.2.1107.5.2.6|
OBX|3|ST|MJPG^Miniatura JPG|1|/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsLDA4QDQ4NDAsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAAQABADAREAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABgcI/8QAJBAAAgIBBAEFAQAAAAAAAAAAAQIDBAUABhEhEgcTIjFBUf/EABQBAQAAAAAAAAAAAAAAAAAAAAX/xAAeEQABBAEFAAAAAAAAAAAAAAABAAIDBAURITFBkf/aAAwDAQACEQMRAD8Amm1tq5TdOVhx2MiMs7dswHCqo7LMT0FA+ydV3amyDtnbkWMa2bUyOZZ5F49x2PkxH4PQH4BqN4vI1aVlzXn0DhFDsTDwWV9Tq//2Q==|
```

---

## 18. ORU^R01 - microbiology result with antibiogram (urine culture)

```
MSH|^~\&|MIKRO||ESKUL||20220118090000||ORU^R01|MIKRO220118001|P|2.3|||AL|NE|POL|CP1250|PL
PID|1|70081200001|11234^^^ESKUL||Czajkowska^Barbara||19700812|F|||Lipowa 14^^Olsztyn^^10-001
PV1|1|I|UROL^^^^^^^ODC1||||||||||||||||2022/U/123
ORC|RE|891234^ESKUL|MK556677|||||891234^ESKUL||||8901^Kubiak^Anna^^^^^ESKUL
OBR|1|891234^ESKUL|MK556677|BAMO^Posiew moczu|||20220118085500|||9012^Mróz^Ewa^^^^^ESKUL||||20220115080000|MO||||||||||F
OBX|1|ST|518^Data i godzina pobrania materiału:||15-01-2022\E\08:00||||||F|||20220118085000||4501
OBX|2|ST|510^Data zakończenia badania:||18-01-2022||||||F|||20220118085000||4501
OBX|3|ST|526^Wynik badania:||dodatni||||||F|||20220118085000||4501
OBX|4|ST|2200^Liczba kolonii^^CC^Liczba kolonii^LIONIC|1|>100 000 CFU/ml||||||F|||20220118085200||4501
OBX|5|ST|2419^Identyfikacja^^ID^Identyfikacja^LIONIC|1|Escherichia coli||||||F|||20220118085200||4501
OBR|2||MK556678|4556^Antybiogram automatyczny^^SU^Antybiogram^LIONIC|||||||||||||||||||||F|2419^1^Escherichia coli|||891234&ESKUL^MK556677
OBX|1|ST|101^Ampicylina&AMP|1|R||||||F|||20220118085500||4501
OBX|2|ST|102^Amoksycylina/kw.klawulanowy&AMC|1|S|||<=2|||F|||20220118085500||4501
OBX|3|ST|130^Ciprofloksacyna&CIP|1|S|||<=0.25|||F|||20220118085500||4501
OBX|4|ST|171^Gentamycyna&GM|1|S|||<=1|||F|||20220118085500||4501
OBX|5|ST|216^Trimetoprim/sulfametoksazol&SXT|1|R||||||F|||20220118085500||4501
```

---

## 19. ORM^O01 - drug administration record (from Eskulap to external system)

```
MSH|^~\&|ECH||ESKUL||20141215101000||ORM^O01|ECH141215001|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|75050800001|9234^^^ESKUL||Lis^Andrzej||19750508|M|||Reymonta 7^^Szczecin^^70-001
PV1|1|I|ONKO^^^^^^^ODC1||||||||||||||||2014/O/892
ORC|NW|ECH89012|||||^^^20141215103000^^R||20141215101000|||3045^Baranowska^Maria|||||ONKO^Oddział onkologiczny
OBR|1|ECH89012||DOCETAXEL^Docetaksel 75mg/m2|||20141215101000||||||||||||||||||
NTE|1|P|Cykl 3/6 - schemat TCH
```

---

## 20. ORU^R01 - radiation exposure parameters (X-ray result with exposure data)

```
MSH|^~\&|RIS01|RIS|ESKUL|HIS|20210520113000||ORU^R01|RIS210520EXP|P|2.3.1||||||8859/2
PID|1||8934^^^ESKUL||Wawrzyniak^Tadeusz||19550312|M|||Mickiewicza 8/3^^Poznań^^60-071
ORC|RE||RIS445566||||^^^20210520110000^^R|345678|20210520113000|||2089^Tomczak^Piotr|||||NEUR^Oddział neurologiczny
OBR|1||RIS445566|RTG.KLP^RTG klatki piersiowej|||20210520112500||||||||||||||||||F|
OBX|1|FT|||Obraz radiologiczny klatki piersiowej w projekcji AP.\.br\Bez zmian ogniskowych.\.br\Sylwetka serca w normie.||||||F|||20210520113000
OBX|2|CE|PEKSP^^^CZAS^|1|25||||||F|
OBX|3|CE|PEKSP^^^NAT^|1|100||||||F|
OBX|4|CE|PEKSP^^^NAP^|1|70||||||F|
OBX|5|CE|PEKSP^^^DAWK^|1|0.3||||||F|
```
