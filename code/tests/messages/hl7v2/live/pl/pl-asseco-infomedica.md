# Asseco InfoMedica - real HL7v2 ER7 messages

---

## 1. ACK - transport acknowledgement

```
MSH|^~\&|SZPM|SYS|SYZ1|20040112112303||ACK|SZPM#97347954|T|2.3|||AL|AL|PL|CP1250|PL
MSA|CA|SYZ1#34454|||
```

---

## 2. ACK - application acknowledgement (accepted)

```
MSH|^~\&|SZPM|SYS|SYS|SYZ1|20040112112303||ACK|SZPM#103750245|T|2.3|||AL|AL|PL|CP1250|PL
MSA|AA|SYZ1#34454|||
```

---

## 3. ORM^O01 - new radiology order

```
MSH|^~\&|SZPM||SYZ1||20030526103638||ORM^O01|SZ01F28|T|2.3|||||PL|CP1250|PL
PID|1||75721||Sikora^Jadwiga||19850411|F|||,^^Ciechocinek
PV1|1|I|OD13
IN1|1||02R
ORC|NW|1115610|||||^^^^^R|1115610|20030526103100|||175^Rutkowska Monika|||||OD13
OBR|1|1115610||RTG||||||||||||175^Chmielewska Renata||||||||HL7|||||1115610
NTE|1|P|klatki piersiowej
```

---

## 4. ORM^O01 - laboratory order with specimen data

```
MSH|^~\&|SZPM||LABHL7||20070716112609||ORM^O01|1E273|P|2.3|||AL||PL|CP1250|PL
PID|1|68032000001|2121||Pawłowska^Halina||19680320|F|||^^Zabrze
PV1|1|O|PPOB||||||||||||||||4735.5418
IN1|1||12
ORC|NW|54942|||||^^^20070716112602^^R||20070716112504|||49999^Michalska^Bożena|||||PPOB^Punkt pobrań
OBR|1|54942||OB^Odczyn opadania krwinek czerwonych|||20070716112504|||2^PIK^PIK||||20070716112602|KP&Krew pełna&SZPM|49999^Michalska^Bożena||800002981||||||LHL7
```

---

## 5. ORM^O01 - order comment exchange (custom KN extension)

```
MSH|^~\&|RIS||SZPM||20160506130837||ORM^O01|SZSZPM25C52_002|P|2.3|||AL|AL|PL||PL
ORC|KN|75413||| ||||20160510130827|||1^ADMIN^ADMIN^^^^^^^^^^UZY
OBR|1|75413||XA.AORTIC^Angiografia|||||||||||&&|
NTE|1|P|komentarz|1228109
```

---

## 6. ORU^R01 - radiology result (free text with formatting)

```
MSH|^~\&|SYZ1||SZPM||200405261448||ORU^R01|VSZ01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR|1|1115610||RTG|||200405261433||||||||||||||||||F|
OBX|1|FT|||Przełyk w całości poszerzony.\.br\Środek kontrastowy przez wpust przedostaje się wąską strugą.\.br\radiolog Ryszard Pietrzak||||||F|||200305261038|
```

---

## 7. ORU^R01 - coded Biernacki sedimentation rate result

```
MSH|^~\&|LAB||SZPM||200405261448||ORU^R01|LW01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR||1115610||OB^Odczyn Biernackiego^SZPM|||200405261433||||||||||||||||||F|
OBX|1|CE|OB^Odczyn Biernackiego^SZPM||15|mm/h|0-12|H||||F|||200305261038|
```

---

## 8. ORU^R01 - CBC morphology partial results

```
MSH|^~\&|LAB||SZPM||200405261448||ORU^R01|LW01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR|1|1115610||MORF|||200405261433||||||||||||||||||F|
OBX|1|CE|WBC^Leukocyty^ SZPM ||8.57|m/uL|4.80-10.80|||||F|||200505261038|
OBX|2|CE|RBC^Erytrocyty^ SZPM ||6.65|m/uL|4.20-5.40|H||||F|||200505261038|
OBX|3|CE|RBC^Erytrocyty^ SZPM ||6.65|m/uL|4.20-5.40|H||||F|||200505261038|
```

---

## 9. ORU^R01 - result with URL reference link

```
MSH|^~\&|SYZ1||SZPM||200405261448||ORU^R01|VSZ01F28|T|2.3|||||PL|CP1250|PL
ORC|RE|1115610|
OBR|1|1115610||RTG|||200405261433||||||||||||||||||F|
OBX|1|FT|||Nie stwierdzono zmian ||||||F|||200305261038|
OBX|2|RP|URL^Obraz||http:\\xxxxxx|
```

---

## 10. ORU^R01 - unsolicited result from external diagnostic system

```
MSH|^~\&|DIAG|DIAG|SZPM|HIS|200703011832||ORU^R01|IWM20070301183219183_1|P|2.3.1||||||8859/1
PID|1||581^^^IWM_Issuer||Grabowska^Zofia||19490201|F|||Piłsudskiego 20/1^^Dąbrowa Górnicza^^41-300
ORC|RE||LW73786039||||^^^20070131133600^^R|50820|20070131133600|||2^PIK^PIK|||||WEW1^Oddział wewnętrzny
OBR|1|| LW73786039|RTG|||200405261433||||||||||||||||||F|
OBX|1|FT|||Przełyk w całości poszerzony.\.br\Środek kontrastowy przez wpust przedostaje się wąską strugą.\.br\radiolog Dariusz Walczak||||||F|||200305261038|
```

---

## 11. ORU^R01 - result with additional medical procedures (XXKPM)

```
MSH|^~\&|DIAG|DIAG|SZPM|HIS|200703011832||ORU^R01|IWM20070301183219183_1|P|2.3.1||||||8859/1
PID|1||581^^^IWM_Issuer||Stępień^Teresa||19490201|F|||Kościuszki 14/3^^Katowice^^40-048
ORC|RE||LW73786039||||^^^20070131133600^^R|50820|20070131133600|||2^PIK^PIK|||||WEW1^Oddział wewnętrzny
OBR|1|| LW73786039|RTG|||200405261433||||||||||||||||||F|
OBX|1|FT|||Przełyk w całości poszerzony.\.br\Środek kontrastowy przez wpust przedostaje się wąską strugą.\.br\radiolog Zbigniew Marciniak||||||F|||200305261038
OBX|2|CE|XXKPM|RT_KNT|||||||F|||200305261038
OBX|3|CE|XXKPM|PRC12|||||||F|||200305261038
```

---

## 12. ORU^R01 - result with embedded PDF attachment (Base64-encoded)

```
MSH|^~\&|HOLTS|Cardiology|SZPM|TestFacility|20130916142018||ORU^R01|130916092017100035|P|2.5
PV1|||||||11^Henryk^Adamczyk
OBR|1|||18754-2^LN|||20130916092200||||||||||||||||||F
OBX|1|ED|ZAL||Dokument^dokument.pdf^PDF^Base64^JVBERi0xLjMKJdDolJUVPRg==||||||F
```

---

## 13. ORU^R01 - result with radiation exposure parameters and base64 image miniature

```
MSH|^~\&|DIAG|DIAG|SZPM|HIS|200703011832||ORU^R01|IWM20070301183219183_1|P|2.3.1||||||8859/1
PID|1||581^^^IWM_Issuer||Baran^Danuta||19490201|F|||Słowackiego 7/2^^Łódź^^90-001
ORC|RE||LW73786039||||^^^20070131133600^^R|50820|20070131133600|||2^PIK^PIK|||||WEW1^Oddział wewnętrzny
OBR|1|| LW73786039|RTG|||200405261433||||||||||||||||||F|
OBX|1|FT|||Przełyk w całości poszerzony.\.br\Środek kontrastowy przez wpust przedostaje się wąską strugą.\.br\radiolog Jacek Szewczyk||||||F|||200305261038
OBX|2|CE|PEKSP^^^CZAS^|1|30||||||F|
OBX|2|CE|PEKSP^^^NAT^|1|120||||||F|
OBX|2|CE|PEKSP^^^CZAS^|2|15||||||F|
OBX|2|CE|PEKSP^^^NAT^|2|150||||||F|
```

---

## 14. ADT^A28 - new patient in master patient index

```
MSH|^~\&|SZPM||LABZ||20070201124042||ADT^A28|1DD47|P|2.3|||AL||PL|CP1250|PL
EVN||20070201124010
PID|1|65012611110|581^^^SZPM||Grabowski^Wojciech||19650126|M|||Kopernika 12^^Wrocław^^50-200
```

---

## 15. ADT^A29 - patient record deletion

```
MSH|^~\&|SZPM||LABZ||20070201124042||ADT^A29|1DD47|P|2.3|||AL||PL|CP1250|PL
EVN||20070201124010
PID|1|72081543218|581^^^SZPM||Pawlak^Grzegorz||19720815|M|||Mickiewicza 45^^Poznań^^61-680
```

---

## 16. ADT^A31 - patient demographics modification

```
MSH|^~\&|SZPM||LABZ||20070201124042||ADT^A31|1DD47|P|2.3|||AL||PL|CP1250|PL
EVN||20070201124010
PID|1|80051789234|581^^^SZPM||Dudek^Marcin||19800517|M|||Długa 8^^Gdańsk^^80-831
```

---

## 17. ADT^A30 - patient record merge

```
MSH|^~\&|SZPM||LABZ||20070201124042||ADT^A30|1DD47|P|2.3|||AL||PL|CP1250|PL
EVN||20070201124010
PID|1|58110367845|581^^^SZPM||Walczak^Sławomir||19581103|M|||Nowa 22^^Szczecin^^70-535
MRG|3455~34546~2345
```

---

## 18. ADT^A01 - patient admission with ICD-10 diagnosis

```
MSH|^~\&|SZPM||LABZ||20070201124042||ADT^A01|1DD47|P|2.3|||AL||PL|CP1250|PL
EVN||20070201124010
PID|1|69042156789|581^^^SZPM||Michalski^Rafał||19690421|M|||Zielona 5^^Lublin^^20-082
PV1|1|I|WEW1^^^^^^^ODC1||||||||||||||||1/2007^^SZPM^KSG
DG1|1||E10.2^Cukrzyca insulinozależna (z powikłaniami nerkowymi)^ICD10|||F|||||||||||WST
```

---

## 19. ADT^A13 - discharge cancellation (re-admission)

```
MSH|^~\&|SZPM||ECH||20161017085833||ADT^A13|ADTSZPM25F03|P|2.3|||AL|AL|PL||PL
EVN||20161017
PID|1|76120215910|4276^^^SZPM||Jaworski^Mirosław||19761202|M||||||||||||||||||PL
PV1|1|I|WEW1||||||||||||||||13249|||||||||||||||||||||||||20160919074900
```

---

## 20. QRY^A19 / ADR^A19 - patient data query and response

Query:
```
MSH|^~\&|ZEWN||SZPM||201404141309282||QRY^A19|1|P|2.3
QRD|20140414130928|R|I|1|||1|34011000968|DEM|
```

Response:
```
MSH|^~\&|ZEWN||SZPM||201404141309282||QRY^A19|1|P|2.3
QRD|20140414130928|R|I|1|||1|34011000968|DEM|
PID|1||1181^^^SZPM||Pietrzak^Grażyna|||F|||
PV1|1|I|WEW1||||||||||||||||1562|||||||||||||||||||||||||20030607140700
```
