# MES (medical equipment HL7v2) - real HL7v2 ER7 messages

---

## 1

```
MSH|^~\&|CLININET|UHC|LUNGTEST|MES|20220315091200||ORM^O01|CN20220315091200|P|2.3|||AL|NE|POL||PL|
PID||82071512345^^^^PESEL|28456||Rogowski^Damian||19820715|M|||Ozimska&15^^Opole^^45-058|||||||||
PV1|1|O|PULM^^^^^^^^Pracownia Pulmonologiczna&PULM&HIS||||||||||||||||||||||||||||||||||||||||||||||||||
IN1|||06&HIS|Mazowiecki Oddział NFZ&07R
ORC|NW|28456-1-100^HIS||5500123^HIS|||^^^20220315091200^^13&RUTYNOWE&R&HIS^||20220315091200|||500^Chmielarz^Rafał^W.^^dr med^^HIS|||||PULM^Pracownia Pulmonologiczna&PULM^HIS|||
OBR|1|28456-1-100^HIS||SPIRO^Spirometria&SPIRO^HIS|||20220315||||||Astma oskrzelowa, podejrzenie||||500^Chmielarz^Rafał^W.^^dr med^^HIS|||||||||||||||
```

---

## 2

```
MSH|^~\&|LUNGTEST|MES|CLININET|UHC|20220315094500||ORU^R01|LT20220315094500|P|2.3|||AL|NE|POL||PL|
ORC|RE|28456-1-100^HIS|LT-2022-0315-001^MES
OBR|1|28456-1-100^HIS|LT-2022-0315-001^MES|SPIRO^Spirometria&SPIRO^HIS|||20220315093000|||||||||PULM||||||||||
OBX|1|NM|FVC^FVC&FVC^MES||4.52|L||N|||F|||20220315093000||101^Piekarska^Halina^^tech.^^MES
OBX|2|NM|FEV1^FEV1&FEV1^MES||3.78|L||N|||F|||20220315093000||101^Piekarska^Halina^^tech.^^MES
OBX|3|NM|FEV1_FVC^FEV1/FVC&FEV1FVC^MES||83.6|%|(>70)||||F|||20220315093000||101^Piekarska^Halina^^tech.^^MES
OBX|4|NM|PEF^PEF&PEF^MES||9.12|L/s||N|||F|||20220315093000||101^Piekarska^Halina^^tech.^^MES
OBX|5|NM|FEF25_75^FEF25-75&FEF2575^MES||3.45|L/s||N|||F|||20220315093000||101^Piekarska^Halina^^tech.^^MES
OBX|6|NM|FVC_PRED^FVC % pred.&FVCPRED^MES||98|%|||||F|||20220315093000||101^Piekarska^Halina^^tech.^^MES
OBX|7|NM|FEV1_PRED^FEV1 % pred.&FEV1PRED^MES||95|%|||||F|||20220315093000||101^Piekarska^Halina^^tech.^^MES
OBX|8|FT|INTERP^Interpretacja||Spirometria prawidłowa. Brak cech obturacji. FVC i FEV1 w normie.||||||F|||20220315093000||101^Piekarska^Halina^^tech.^^MES
```

---

## 3

```
MSH|^~\&|SZPM||LUNGTEST||20220401080000||ORM^O01|SZ_LT_001|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|90050512345|3344^^^SZPM||Bukowska^Sylwia||19900505|F|||Dworcowa&8^^Piła^^^^^6461011
PV1|1|O|PULM^^^^^^^PULM1^Pracownia pulmonologiczna
IN1|1||06
ORC|NW|778899|||||^^^20220401080000^^R||20220401080000|||2000^Żak^Łukasz^^^^^^PRZAW&54321^^^^LEK|||||PULM
OBR|1|778899||SPIRO^Spirometria|||20220401080000|||||||J45.0|20220401080000||2000^Żak^Łukasz||||||||PULM
NTE|1|P|Proszę o próbę rozkurczową z salbutamolem
```

---

## 4

```
MSH|^~\&|LUNGTEST|MES|SZPM||20220401092000||ORU^R01|LT_WYN_001|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|90050512345|3344^^^SZPM||Bukowska^Sylwia||19900505|F|||Dworcowa&8^^Piła
ORC|RE|778899
OBR|1|778899||SPIRO^Spirometria|||20220401090000|20220401091500||||||||&&|||||||||||F
OBX|1|NM|FVC_PRE^FVC przed rozkurczem||3.21|L||N|||F|||20220401090000||50^Wilk^Grzegorz^^tech.
OBX|2|NM|FEV1_PRE^FEV1 przed rozkurczem||2.15|L||(>80% pred.)||||F|||20220401090000||50^Wilk^Grzegorz^^tech.
OBX|3|NM|FEV1FVC_PRE^FEV1/FVC przed rozkurczem||67.0|%|(>70)|L|||F|||20220401090000||50^Wilk^Grzegorz^^tech.
OBX|4|NM|FVC_POST^FVC po rozkurczu||3.45|L||N|||F|||20220401091500||50^Wilk^Grzegorz^^tech.
OBX|5|NM|FEV1_POST^FEV1 po rozkurczu||2.58|L|||||F|||20220401091500||50^Wilk^Grzegorz^^tech.
OBX|6|NM|FEV1FVC_POST^FEV1/FVC po rozkurczu||74.8|%|(>70)||||F|||20220401091500||50^Wilk^Grzegorz^^tech.
OBX|7|NM|FEV1_CHANGE^Zmiana FEV1 po rozkurczu||20.0|%|(>12% = test +)||||F|||20220401091500||50^Wilk^Grzegorz^^tech.
OBX|8|FT|INTERP^Interpretacja||Obturacja lekka (FEV1/FVC 67%).\.br\Próba rozkurczowa DODATNIA (wzrost FEV1 o 20%).\.br\Obraz sugerujący astmę oskrzelową.||||||F|||20220401091500||50^Wilk^Grzegorz^^tech.
```

---

## 5

```
MSH|^~\&|OPTIMED|COMARCH|LUNGTEST|MES|20220510101000||ORM^O01|OPT20220510101000|P|2.3|||AL|NE|POL||PL|
PID||75121098765^^^^PESEL|OPT-45678||Jabłoński^Marek^Tadeusz||19751210|M|||Sikorskiego&22^^Gorzów Wielkopolski^^66-400|||||||||
PV1|1|O|POZ_PULM^^^^^^^^Poradnia Pulmonologiczna&PP&OPTIMED
IN1|||08&OPTIMED|Wielkopolski Oddział NFZ
ORC|NW|OPT-ORD-55123^OPTIMED||GRP-2022-05^OPTIMED|||^^^20220510101000^^13&RUTYNOWE&R&OPTIMED^||20220510101000|||333^Szymczak^Dorota^^dr med^^OPTIMED|||||POZ_PULM^Poradnia Pulmonologiczna^OPTIMED|||
OBR|1|OPT-ORD-55123^OPTIMED||SPIRO^Spirometria&SPIRO^OPTIMED|||20220510||||||POChP podejrzenie||||333^Szymczak^Dorota^^dr med^^OPTIMED|||||||||||||||
```

---

## 6

```
MSH|^~\&|LUNGTEST|MES|OPTIMED|COMARCH|20220510111500||ORU^R01|LT20220510111500|P|2.3|||AL|NE|POL||PL|
ORC|RE|OPT-ORD-55123^OPTIMED|LT-2022-0510-003^MES
OBR|1|OPT-ORD-55123^OPTIMED|LT-2022-0510-003^MES|SPIRO^Spirometria&SPIRO^OPTIMED|||20220510110000|||||||||PP||||||||||
OBX|1|NM|FVC^FVC&FVC^MES||2.89|L|||||F|||20220510110000||75^Bąk^Artur^^tech.^^MES
OBX|2|NM|FEV1^FEV1&FEV1^MES||1.42|L||(>80% pred.)|L|||F|||20220510110000||75^Bąk^Artur^^tech.^^MES
OBX|3|NM|FEV1_FVC^FEV1/FVC&FEV1FVC^MES||49.1|%|(>70)|L|||F|||20220510110000||75^Bąk^Artur^^tech.^^MES
OBX|4|NM|PEF^PEF&PEF^MES||4.21|L/s|||||F|||20220510110000||75^Bąk^Artur^^tech.^^MES
OBX|5|NM|FEF25_75^FEF25-75&FEF2575^MES||0.88|L/s|||||F|||20220510110000||75^Bąk^Artur^^tech.^^MES
OBX|6|NM|FVC_PRED^FVC % pred.&FVCPRED^MES||62|%|||||F|||20220510110000||75^Bąk^Artur^^tech.^^MES
OBX|7|NM|FEV1_PRED^FEV1 % pred.&FEV1PRED^MES||38|%|||||F|||20220510110000||75^Bąk^Artur^^tech.^^MES
OBX|8|FT|INTERP^Interpretacja||Ciężka obturacja (FEV1/FVC 49,1%, FEV1 38% pred.).\.br\Sugerowana POChP w stadium ciężkim (GOLD III).\.br\Zalecenia: próba rozkurczowa, badanie DLCO.||||||F|||20220510110000||75^Bąk^Artur^^tech.^^MES
```

---

## 7

```
MSH|^~\&|CLININET|UHC|LUNGTEST|MES|20220315100000||ORM^O01|CN20220315100000|P|2.3|||AL|NE|POL||PL|
ORC|CA|28456-1-100^HIS|||||||||||
OBR||28456-1-100^HIS||SPIRO^Spirometria&SPIRO^HIS|||||||||||||||||||||||||||
NTE|1|P|Pacjent odmówił wykonania badania
```

---

## 8

```
MSH|^~\&|LUNGTEST|MES|CLININET|UHC|20220315093000||ORM^O01|LT20220315093000|P|2.3|||AL|NE|POL||PL|
ORC|SC|28456-1-100^HIS|LT-2022-0315-001^MES||IP||||||||
OBR||28456-1-100^HIS|LT-2022-0315-001^MES|SPIRO^Spirometria&SPIRO^HIS|||||||||||||||||||||||||||
```

---

## 9

```
MSH|^~\&|LUNGTEST|MES|CLININET|UHC|20220315091201||ACK|LT_ACK_20220315091201|P|2.3|||AL|NE|POL||PL|
MSA|CA|CN20220315091200|||
```

---

## 10

```
MSH|^~\&|LUNGTEST|MES|CLININET|UHC|20220601141500||ORU^R01|LT20220601141500|P|2.3|||AL|NE|POL||PL|
ORC|RE|34567-1-200^HIS|LT-2022-0601-005^MES
OBR|1|34567-1-200^HIS|LT-2022-0601-005^MES|DLCO^DLCO Dyfuzja&DLCO^HIS|||20220601140000|||||||||PULM||||||||||
OBX|1|NM|DLCO^DLCO&DLCO^MES||7.82|mmol/min/kPa||N|||F|||20220601140000||101^Piekarska^Halina^^tech.^^MES
OBX|2|NM|DLCO_PRED^DLCO % pred.&DLCOPRED^MES||85|%|||||F|||20220601140000||101^Piekarska^Halina^^tech.^^MES
OBX|3|NM|KCO^KCO&KCO^MES||1.45|mmol/min/kPa/L||N|||F|||20220601140000||101^Piekarska^Halina^^tech.^^MES
OBX|4|NM|VA^VA (objętość pęcherzykowa)&VA^MES||5.39|L||N|||F|||20220601140000||101^Piekarska^Halina^^tech.^^MES
OBX|5|FT|INTERP^Interpretacja||DLCO w normie (85% pred.). KCO prawidłowe.\.br\Brak cech upośledzenia dyfuzji.||||||F|||20220601140000||101^Piekarska^Halina^^tech.^^MES
```

---

## 11

```
MSH|^~\&|ESCULAP|SZPITAL_KIELCE|LUNGTEST|MES|20220720080500||ORM^O01|ESC20220720080500|P|2.3|||AL|NE|POL||PL|
PID||56030178901^^^^PESEL|ESC-77890||Mucha^Henryk||19560301|M|||Konopnickiej&10^^Konin^^62-510|||||||||
PV1|1|I|PULM^^^^^^^^Oddział Pulmonologiczny&PULM&ESCULAP
IN1|||12&ESCULAP|Świętokrzyski Oddział NFZ
ORC|NW|ESC-ORD-8811^ESCULAP||GRP-ESC-01^ESCULAP|||^^^20220720080500^^12&RUTYNOWE&R&ESCULAP^||20220720080500|||777^Jarosz^Agnieszka^^dr^^ESCULAP|||||PULM^Oddział Pulmonologiczny^ESCULAP|||
OBR|1|ESC-ORD-8811^ESCULAP||SPIRO^Spirometria&SPIRO^ESCULAP|||20220720||||||POChP - kontrola||||777^Jarosz^Agnieszka^^dr^^ESCULAP|||||||||||||||
NTE|1|P|Proszę o pełną spirometrię z próbą rozkurczową
```

---

## 12

```
MSH|^~\&|LUNGTEST|MES|ESCULAP|SZPITAL_KIELCE|20220720100000||ORU^R01|LT20220720100000|P|2.3|||AL|NE|POL||PL|
ORC|RE|ESC-ORD-8811^ESCULAP|LT-2022-0720-002^MES
OBR|1|ESC-ORD-8811^ESCULAP|LT-2022-0720-002^MES|SPIRO^Spirometria&SPIRO^ESCULAP|||20220720093000|||||||||PULM||||||||||
OBX|1|NM|FVC^FVC&FVC^MES||2.10|L||(>80% pred.)|L|||F|||20220720093000||90^Kaczmarczyk^Wioletta^^tech.^^MES
OBX|2|NM|FEV1^FEV1&FEV1^MES||1.85|L||(>80% pred.)|L|||F|||20220720093000||90^Kaczmarczyk^Wioletta^^tech.^^MES
OBX|3|NM|FEV1_FVC^FEV1/FVC&FEV1FVC^MES||88.1|%|(>70)|N|||F|||20220720093000||90^Kaczmarczyk^Wioletta^^tech.^^MES
OBX|4|NM|TLC^TLC&TLC^MES||3.80|L||(>80% pred.)|L|||F|||20220720093000||90^Kaczmarczyk^Wioletta^^tech.^^MES
OBX|5|NM|FVC_PRED^FVC % pred.&FVCPRED^MES||55|%|||||F|||20220720093000||90^Kaczmarczyk^Wioletta^^tech.^^MES
OBX|6|NM|FEV1_PRED^FEV1 % pred.&FEV1PRED^MES||52|%|||||F|||20220720093000||90^Kaczmarczyk^Wioletta^^tech.^^MES
OBX|7|FT|INTERP^Interpretacja||Restrykcja umiarkowana (FVC 55% pred., FEV1/FVC w normie).\.br\TLC obniżone (3,80 L).\.br\Obraz sugerujący chorobę restrykcyjną płuc.||||||F|||20220720093000||90^Kaczmarczyk^Wioletta^^tech.^^MES
```

---

## 13

```
MSH|^~\&|LUNGTEST|MES|SZPM||20220401085000||ORM^O01|LT_STA_001|P|2.3|||AL|AL|PL|CP1250|PL
ORC|SC|778899|||PRZY||^^^20220401090000^^R||20220401085000
OBR|1|778899||SPIRO^Spirometria|||20220401090000
```

---

## 14

```
MSH|^~\&|LUNGTEST|MES|CLININET|UHC|20220801150000||ORU^R01|LT20220801150000|P|2.3|||AL|NE|POL||PL|
ORC|RE|45678-2-300^HIS|LT-2022-0801-007^MES
OBR|1|45678-2-300^HIS|LT-2022-0801-007^MES|PLETHYSM^Pletyzmografia&PLETH^HIS|||20220801143000|||||||||PULM||||||||||
OBX|1|NM|RTOT^Rtot (opór całkowity)&RTOT^MES||0.35|kPa*s/L|(0.1-0.35)|N|||F|||20220801143000||101^Piekarska^Halina^^tech.^^MES
OBX|2|NM|SRTOT^sRtot&SRTOT^MES||1.22|kPa*s|(0.3-1.5)|N|||F|||20220801143000||101^Piekarska^Halina^^tech.^^MES
OBX|3|NM|TGV^TGV (FRC pleth.)&TGV^MES||3.45|L|||||F|||20220801143000||101^Piekarska^Halina^^tech.^^MES
OBX|4|NM|RV^RV (obj. zalegająca)&RV^MES||1.89|L|||||F|||20220801143000||101^Piekarska^Halina^^tech.^^MES
OBX|5|NM|TLC^TLC&TLC^MES||6.21|L|||||F|||20220801143000||101^Piekarska^Halina^^tech.^^MES
OBX|6|NM|RV_TLC^RV/TLC&RVTLC^MES||30.4|%|(20-35)|N|||F|||20220801143000||101^Piekarska^Halina^^tech.^^MES
OBX|7|FT|INTERP^Interpretacja||Pletyzmografia ciała: opory oddechowe prawidłowe.\.br\Rtot 0,35 kPa*s/L (górna granica normy).\.br\Objętości płuc w normie. RV/TLC 30,4%.||||||F|||20220801143000||101^Piekarska^Halina^^tech.^^MES
```

---

## 15

```
MSH|^~\&|LUNGTEST|MES|SZPM||20220901110000||ORU^R01|LT_PED_001|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|15090112345|5566^^^SZPM||Krakowiak^Oskar||20150901|M|||Lipowa&3^^Skierniewice^^^^^1046211|||||||||||||09230379454^^^PESEL^OP
ORC|RE|889900
OBR|1|889900||SPIRO^Spirometria|||20220901105000|20220901105500||||||||&&|||||||||||F
OBX|1|NM|FVC^FVC||1.52|L||N|||F|||20220901105000||50^Wilk^Grzegorz^^tech.
OBX|2|NM|FEV1^FEV1||1.41|L||N|||F|||20220901105000||50^Wilk^Grzegorz^^tech.
OBX|3|NM|FEV1_FVC^FEV1/FVC||92.8|%|(>80)|N|||F|||20220901105000||50^Wilk^Grzegorz^^tech.
OBX|4|FT|INTERP^Interpretacja||Spirometria u dziecka lat 7. Współpraca dobra.\.br\Wartości w normie dla wieku, wzrostu i płci.\.br\Brak cech obturacji.||||||F|||20220901105000||50^Wilk^Grzegorz^^tech.
```

---

## 16

```
MSH|^~\&|LUNGTEST|MES|CLININET|UHC|20221015140000||ORU^R01|LT20221015140000|P|2.3|||AL|NE|POL||PL|
ORC|RE|56789-1-400^HIS|LT-2022-1015-010^MES
OBR|1|56789-1-400^HIS|LT-2022-1015-010^MES|FENO^FeNO pomiar&FENO^HIS|||20221015135000|||||||||PULM||||||||||
OBX|1|NM|FENO^FeNO&FENO^MES||45|ppb|(5-25 norma)|H|||F|||20221015135000||75^Bąk^Artur^^tech.^^MES
OBX|2|FT|INTERP^Interpretacja||FeNO podwyższone (45 ppb, norma <25 ppb).\.br\Wynik wskazuje na eozynofilowe zapalenie dróg oddechowych.\.br\Sugestia: rozważyć astmę lub odpowiedź na GKS wziewne.||||||F|||20221015135000||75^Bąk^Artur^^tech.^^MES
```

---

## 17

```
MSH|^~\&|SZPM||LUNGTEST||20221101070000||ORM^O01|SZ_MP_001|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|70010199999|7788^^^SZPM||Czerwiński^Waldemar||19700101|M|||Fabryczna&5^^Ostrów Wielkopolski^^^^^3017011
PV1|1|O|MED_PRACY^^^^^^^MP1^Medycyna pracy
IN1|1||12
ORC|NW|990011|||||^^^20221101070000^^R||20221101070000|||800^Złotowska^Joanna^^^^LEK|||||MED_PRACY
OBR|1|990011||SPIRO^Spirometria|||20221101070000|||||||Badanie okresowe - narażenie na pyły||||800^Złotowska^Joanna||||||||MED_PRACY
```

---

## 18

```
MSH|^~\&|LUNGTEST|MES|CLININET|UHC|20221015143000||ORU^R01|LT20221015143000|P|2.3|||AL|NE|POL||PL|
ORC|RE|56789-1-400^HIS|LT-2022-1015-010^MES
OBR|1|56789-1-400^HIS|LT-2022-1015-010^MES|SPIRO^Spirometria&SPIRO^HIS|||20221015140000|||||||||PULM||||||||||F
OBX|1|NM|FVC^FVC||3.95|L||N|||F|||20221015140000||75^Bąk^Artur^^tech.^^MES
OBX|2|NM|FEV1^FEV1||3.22|L||N|||F|||20221015140000||75^Bąk^Artur^^tech.^^MES
OBX|3|NM|FEV1_FVC^FEV1/FVC||81.5|%|(>70)|N|||F|||20221015140000||75^Bąk^Artur^^tech.^^MES
OBX|4|FT|INTERP^Interpretacja||Spirometria prawidłowa. FVC i FEV1 w normie.||||||F|||20221015140000||75^Bąk^Artur^^tech.^^MES
OBX|5|ED|PDF^Raport spirometrii PDF||LUNGTEST^application^PDF^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIg MCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFsw IDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAg UgovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAov Rm9udCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA3Mgo+ PgpzdHJlYW0KQlQKL0YxIDE4IFRmCjEwMCA3MDAgVGQKKFNwaXJvbWV0cmlhIC0gUmFwb3J0IE1F UyBMdW5ndGVzdCkgVGoKCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PAovVHlwZSAvRm9u dAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCnhyZWYKMCA2 CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAw IG4gCjAwMDAwMDAxNDEgMDAwMDAgbiAKMDAwMDAwMDMyNCAwMDAwMCBuIAowMDAwMDAwNDQ3IDAw MDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNgovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKNTMyCiUl RU9GCg==||||||F|||20221015140000
```

---

## 19

```
MSH|^~\&|LUNGTEST|MES|SZPM||20221101083000||ORU^R01|LT_MP_WYN_001|P|2.3|||AL|AL|PL|CP1250|PL
PID|1|70010199999|7788^^^SZPM||Czerwiński^Waldemar||19700101|M|||Fabryczna&5^^Ostrów Wielkopolski
ORC|RE|990011
OBR|1|990011||SPIRO^Spirometria|||20221101080000|20221101082500||||||||&&|||||||||||F
OBX|1|NM|FVC^FVC||4.89|L||N|||F|||20221101080000||101^Piekarska^Halina^^tech.
OBX|2|NM|FEV1^FEV1||4.05|L||N|||F|||20221101080000||101^Piekarska^Halina^^tech.
OBX|3|NM|FEV1_FVC^FEV1/FVC||82.8|%|(>70)|N|||F|||20221101080000||101^Piekarska^Halina^^tech.
OBX|4|NM|PEF^PEF||10.2|L/s||N|||F|||20221101080000||101^Piekarska^Halina^^tech.
OBX|5|FT|INTERP^Interpretacja||Spirometria prawidłowa. Badanie okresowe - brak przeciwwskazań do pracy w narażeniu na pyły.||||||F|||20221101080000||101^Piekarska^Halina^^tech.
OBX|6|ED|FV_CURVE^Krzywa przepływ-objętość||LUNGTEST^image^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DhAQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQU FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCACAAIADASIAAhEBAxEB/8QA GAABAAMBAAAAAAAAAAAAAAAAAAcICQr/xAAtEAABAwQBAwIFBAMAAAAAAAAAAAABAgMEBQYHERIhMRNB CCJRYXEUMoGRofD/xAAYAQADAQEAAAAAAAAAAAAAAAABAgMABP/EAB4RAAICAgMBAQAAAAAAAAAAAAAB AgMRIRIxQVFh/9oADAMBAAIRAxEAPwBX1ZZb9k12hs2L2Wr3DfbhL6NGgtNOkq6iRV4RETXBSF2p 4M63+KuxJ2dQ4lBh+nLZLJT2yh9CKorql6fLJPUyNRz1V3PalVPHnnkkz9j+w+m/h/0rcsgv06o yuGaO3WaveyKe5VsnxRU8b+fmXt82ySNb+UqvHBpjf2dj2NRERaHF4qDUcqK2kkxqinqWQTMlWOZ IXRuRr2u5RUciKnKeQFPaGHZ/wDFxu+b8p0jw+hltGr0c172yqj51VVX8pER7WovcjWsRVXx3KJb Bq6HA9fR45RQQwxUsLY0bEiqzwnB1SpkclbPuT7GPMYSpfM9CvkrRxMfz7PcrxDLsHh2W2qppKW0 xS1LZ3QP9TqRkT1SRjUTu/qqiIu/k3Ry2CmuWPz0FfTpNTTcJJGqOVFTuip5QzX0bVLAFJ7cDK/ P80J+L9ZZuP7+GfnEvSf6eRqPpI0RfliRqo1UVU844VE4OhvhC3W/c+wrJhEdqkp6FEWasmqfRSJ aZieeSNdrur/ABRPuzuOhWBXNf1KR3sX5LHhyp3Y/ntuCkuJRbHv6Hp7PZOr9QqJ1cIcXq5usPpf /9k=||||||F|||20221101080000
```

---

## 20

```
MSH|^~\&|LUNGTEST|MES|SZPM||20220401095000||ORM^O01|LT_CM_001|P|2.3|||AL|AL|PL|CP1250|PL
ORC|RF|778899|||CM||^^^20220401090000^^R||20220401095000
OBR|1|778899||SPIRO^Spirometria|||20220401090000||||||||||||||||||PULM
```
