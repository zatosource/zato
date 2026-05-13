# Sectra RIS/PACS - real HL7v2 ER7 messages

---

## 1. ORM^O01 - Chest X-ray order (thorax-röntgentilaus)

```
MSH|^~\&|LIFECARE|TAYS|SECTRA_RIS|TAYS_RAD|20260509080000||ORM^O01|SECTRA000010|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT600001^^^TAYS^MR~120580-234A^^^DVV^NNFIN||Hakkarainen^Jorma^Antero^^Herra||19800512|M|||Hämeenkatu 55^^Tampere^^33200^FIN||^^CP^0401234584
PV1||E|TAYS^PPKL^Triage 2^^PSHP||||DR600^Niemi^Satu^^^LKT^Lääkäri||||||||||||KÄYNTI600001
ORC|NW|ORD600001^LIFECARE|||||^^^20260509080000^^S||20260509080000|DR600^Niemi^Satu^^^LKT^Lääkäri
OBR|1|ORD600001^LIFECARE||71020^Thorax PA+LAT^RADLEX|||20260509080000||||||||DR600^Niemi^Satu^^^LKT^Lääkäri||||||||||HENGENAHDISTUS^Hengenahdistus ja yskä
```

---

## 2. ORM^O01 - CT head order (pään TT-tilaus)

```
MSH|^~\&|LIFECARE|TAYS|SECTRA_RIS|TAYS_RAD|20260509091000||ORM^O01|SECTRA000011|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT600002^^^TAYS^MR~051245+567B^^^DVV^NNFIN||Savinainen^Helmi^Annikki^^Rouva||19450512|F|||Satakunnankatu 18^^Tampere^^33210^FIN||^^PH^0332345679
PV1||E|TAYS^PPKL^Triage 1^^PSHP||||DR601^Mäntylä^Harri^^^LKT^Lääkäri||||||||||||KÄYNTI600002
ORC|NW|ORD600002^LIFECARE|||||^^^20260509091000^^S||20260509091000|DR601^Mäntylä^Harri^^^LKT^Lääkäri
OBR|1|ORD600002^LIFECARE||36554-4^CT pää natiivi^RADLEX|||20260509091000||||||||DR601^Mäntylä^Harri^^^LKT^Lääkäri||||||||||CVA^Äkillinen toispuoleinen heikkous
```

---

## 3. ORM^O01 - MRI knee order (polven MRI-tilaus)

```
MSH|^~\&|APOTTI|HUS_JORVI|SECTRA_RIS|HUS_RAD|20260509100000||ORM^O01|SECTRA000012|P|2.5|||AL|NE||FIN|UTF-8
PID|||PT600003^^^HUS^MR~180295-890C^^^DVV^NNFIN||Virtanen^Olli^Tapani^^Herra||19950218|M|||Leppävaarankatu 30^^Espoo^^02600^FIN||^^CP^0451234574
PV1||O|JORV^ORTPOLI^Vastaanottohuone 4^^HUS||||DR602^Korhonen^Antti^^^LKT^Lääkäri||||||||||||KÄYNTI600003
ORC|NW|ORD600003^APOTTI|||||^^^20260509100000^^R||20260509100000|DR602^Korhonen^Antti^^^LKT^Lääkäri
OBR|1|ORD600003^APOTTI||36109-7^MRI polvi^RADLEX|||20260509100000||||||||DR602^Korhonen^Antti^^^LKT^Lääkäri||||||||||POLVIKIPU^Oikean polven kipu ja turvotus
```

---

## 4. ORU^R01 - Chest X-ray result (thorax-röntgenvastaus)

```
MSH|^~\&|SECTRA_RIS|TAYS_RAD|LIFECARE|TAYS|20260509110000||ORU^R01|SECTRA000013|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT600001^^^TAYS^MR~120580-234A^^^DVV^NNFIN||Hakkarainen^Jorma^Antero^^Herra||19800512|M|||Hämeenkatu 55^^Tampere^^33200^FIN||^^CP^0401234584
PV1||E|TAYS^PPKL^Triage 2^^PSHP||||DR600^Niemi^Satu^^^LKT^Lääkäri||||||||||||KÄYNTI600001
ORC|RE|ORD600001^LIFECARE|RES600001^SECTRA_RIS||||^^^20260509080000^^S||20260509110000
OBR|1|ORD600001^LIFECARE|RES600001^SECTRA_RIS|71020^Thorax PA+LAT^RADLEX|||20260509083000|||||||20260509083000|^^Thorax|DR603^Ikäheimo^Reijo^^^RAD^Radiologi||||||20260509110000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Keuhkokentissä ei infiltraatteja. Sydämen koko normaali. Keuhkovaltimot normaalit. Ei pleuranestettä. Tukiluusto normaalirakenteinen.||||||F|||20260509110000
```

---

## 5. ORU^R01 - CT head result with base64 PDF (pään TT-vastaus PDF-liitteellä)

```
MSH|^~\&|SECTRA_RIS|TAYS_RAD|LIFECARE|TAYS|20260509120000||ORU^R01|SECTRA000014|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT600002^^^TAYS^MR~051245+567B^^^DVV^NNFIN||Savinainen^Helmi^Annikki^^Rouva||19450512|F|||Satakunnankatu 18^^Tampere^^33210^FIN||^^PH^0332345679
PV1||E|TAYS^PPKL^Triage 1^^PSHP||||DR601^Mäntylä^Harri^^^LKT^Lääkäri||||||||||||KÄYNTI600002
ORC|RE|ORD600002^LIFECARE|RES600002^SECTRA_RIS||||^^^20260509091000^^S||20260509120000
OBR|1|ORD600002^LIFECARE|RES600002^SECTRA_RIS|36554-4^CT pää natiivi^RADLEX|||20260509095000|||||||20260509095000|^^CT|DR604^Koskinen^Marja^^^RAD^Radiologi||||||20260509120000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Pään natiivi-TT: Vasemman keskimmäisen aivovaltimon suonitusalueella ei tuoretta infarktia tai verenvuotoa. Vanhat lakunaariset infarktit basaaliganglioissa bilateraalisesti. Ventrikulaarinen järjestelmä normaali.||||||F|||20260509120000
OBX|2|ED|PDF^TT-lausunto^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F|||20260509120000
```

---

## 6. ORU^R01 - MRI knee result with base64 PDF (polven MRI-vastaus PDF-liitteellä)

```
MSH|^~\&|SECTRA_RIS|HUS_RAD|APOTTI|HUS_JORVI|20260512150000||ORU^R01|SECTRA000015|P|2.5|||AL|NE||FIN|UTF-8
PID|||PT600003^^^HUS^MR~180295-890C^^^DVV^NNFIN||Virtanen^Olli^Tapani^^Herra||19950218|M|||Leppävaarankatu 30^^Espoo^^02600^FIN||^^CP^0451234574
PV1||O|JORV^ORTPOLI^Vastaanottohuone 4^^HUS||||DR602^Korhonen^Antti^^^LKT^Lääkäri||||||||||||KÄYNTI600003
ORC|RE|ORD600003^APOTTI|RES600003^SECTRA_RIS||||^^^20260509100000^^R||20260512150000
OBR|1|ORD600003^APOTTI|RES600003^SECTRA_RIS|36109-7^MRI polvi^RADLEX|||20260511090000|||||||20260511090000|^^MRI|DR605^Paavola^Timo^^^RAD^Radiologi||||||20260512150000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Oikean polven MRI: Mediaalisen menisin posteriorisen sarven horisontaalinen repeämä. Eturistiside ehjä. Lateraalinen meniski normaali. Nivelpinnassa ei rustodefektejä. Pieni nivelnesteen lisääntyminen.||||||F|||20260512150000
OBX|2|ED|PDF^MRI-lausunto^L||^application^pdf^Base64^JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8Ci9NYXJrZWQgdHJ1ZQo+PgovTGFuZyAoZmkpCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCj4+CmVuZG9iagoK||||||F|||20260512150000
```

---

## 7. ORM^O01 - Ultrasound abdomen order (vatsan ultraäänitilaus)

```
MSH|^~\&|LIFECARE|TYKS|SECTRA_RIS|VSSHP_RAD|20260509093000||ORM^O01|SECTRA000016|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT600004^^^TYKS^MR~220470-123D^^^DVV^NNFIN||Lehtinen^Matti^Kalevi^^Herra||19700422|M|||Linnankatu 45^^Turku^^20100^FIN||^^CP^0401234585
PV1||O|TYKS^POLI2^Vastaanottohuone 3^^VSSHP||||DR606^Hakala^Sanna^^^LKT^Lääkäri||||||||||||KÄYNTI600004
ORC|NW|ORD600004^LIFECARE|||||^^^20260509093000^^R||20260509093000|DR606^Hakala^Sanna^^^LKT^Lääkäri
OBR|1|ORD600004^LIFECARE||76830-1^UÄ vatsa^RADLEX|||20260509093000||||||||DR606^Hakala^Sanna^^^LKT^Lääkäri||||||||||VATSAKIPU^Ylävatsavaivat
```

---

## 8. ORU^R01 - Ultrasound abdomen result (vatsan ultraäänivastaus)

```
MSH|^~\&|SECTRA_RIS|VSSHP_RAD|LIFECARE|TYKS|20260509133000||ORU^R01|SECTRA000017|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT600004^^^TYKS^MR~220470-123D^^^DVV^NNFIN||Lehtinen^Matti^Kalevi^^Herra||19700422|M|||Linnankatu 45^^Turku^^20100^FIN||^^CP^0401234585
PV1||O|TYKS^POLI2^Vastaanottohuone 3^^VSSHP||||DR606^Hakala^Sanna^^^LKT^Lääkäri||||||||||||KÄYNTI600004
ORC|RE|ORD600004^LIFECARE|RES600004^SECTRA_RIS||||^^^20260509093000^^R||20260509133000
OBR|1|ORD600004^LIFECARE|RES600004^SECTRA_RIS|76830-1^UÄ vatsa^RADLEX|||20260509110000|||||||20260509110000|^^UÄ|DR607^Mattila^Kaisa^^^RAD^Radiologi||||||20260509133000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Vatsan UÄ: Maksa normaalikokoinenn, tasainen. Sappirakko normaali, ei sappikiviä. Haima ja perna normaalit. Munuaiset symmetriset, ei hydronefroosia. Aortta normaalikaliiperinen.||||||F|||20260509133000
```

---

## 9. ORM^O01 - CT chest with contrast order (varjoaine-TT thorax -tilaus)

```
MSH|^~\&|OMNI360|OYS|SECTRA_RIS|OYS_RAD|20260509102000||ORM^O01|SECTRA000018|P|2.3|||AL|NE||FIN
PID|||PT600005^^^OYS^MR~300665-456E^^^DVV^NNFIN||Karhu^Risto^Juhani^^Herra||19650630|M|||Kajaaninkatu 15^^Oulu^^90100^FIN||^^CP^0407654331
PV1||I|OYS^KEUH1^Huone 204^Vuode 1^PPSHP||||DR608^Tolonen^Markku^^^LKT^Lääkäri||||||||||||HOITO600001
ORC|NW|ORD600005^OMNI360|||||^^^20260509102000^^R||20260509102000|DR608^Tolonen^Markku^^^LKT^Lääkäri
OBR|1|ORD600005^OMNI360||71275-2^CT thorax varjoaine^RADLEX|||20260509102000||||||||DR608^Tolonen^Markku^^^LKT^Lääkäri||||||||||KEUHKOSYÖPÄEPÄILY^Keuhkomuutos rtg:ssa
```

---

## 10. ORU^R01 - CT chest with contrast result (varjoaine-TT thorax -vastaus)

```
MSH|^~\&|SECTRA_RIS|OYS_RAD|OMNI360|OYS|20260509160000||ORU^R01|SECTRA000019|P|2.3|||AL|NE||FIN
PID|||PT600005^^^OYS^MR~300665-456E^^^DVV^NNFIN||Karhu^Risto^Juhani^^Herra||19650630|M|||Kajaaninkatu 15^^Oulu^^90100^FIN||^^CP^0407654331
PV1||I|OYS^KEUH1^Huone 204^Vuode 1^PPSHP||||DR608^Tolonen^Markku^^^LKT^Lääkäri||||||||||||HOITO600001
ORC|RE|ORD600005^OMNI360|RES600005^SECTRA_RIS||||^^^20260509102000^^R||20260509160000
OBR|1|ORD600005^OMNI360|RES600005^SECTRA_RIS|71275-2^CT thorax varjoaine^RADLEX|||20260509130000|||||||20260509130000|^^CT|DR609^Mikkonen^Pasi^^^RAD^Radiologi||||||20260509160000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Thoraxin varjoaine-TT: Oikean yläkeuhkon apikaaliosassa 28mm spikuloitunut tuumori. Mediastinaaliset imusolmukkeet ei suurentuneet. Ei pleuranestettä. Suositellaan PET-TT-tutkimusta.||||||F|||20260509160000
```

---

## 11. ORM^O01 - Mammography order (mammografiatilaus)

```
MSH|^~\&|LIFECARE|TAYS|SECTRA_RIS|TAYS_RAD|20260509100000||ORM^O01|SECTRA000020|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT600006^^^TAYS^MR~130370-789F^^^DVV^NNFIN||Kärkkäinen^Marja^Liisa^^Rouva||19700313|F|||Puutarhakatu 22^^Tampere^^33210^FIN||^^CP^0401234586
PV1||O|TAYS^RADPOLI^Mammografiahuone 1^^PSHP||||DR610^Aho^Kristiina^^^LKT^Lääkäri||||||||||||KÄYNTI600005
ORC|NW|ORD600006^LIFECARE|||||^^^20260509100000^^R||20260509100000|DR610^Aho^Kristiina^^^LKT^Lääkäri
OBR|1|ORD600006^LIFECARE||24606-6^Mammografia bilat^RADLEX|||20260509100000||||||||DR610^Aho^Kristiina^^^LKT^Lääkäri||||||||||SEULONTA^Rintasyöpäseulonta
```

---

## 12. ORU^R01 - Mammography result (mammografiavastaus)

```
MSH|^~\&|SECTRA_RIS|TAYS_RAD|LIFECARE|TAYS|20260509143000||ORU^R01|SECTRA000021|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT600006^^^TAYS^MR~130370-789F^^^DVV^NNFIN||Kärkkäinen^Marja^Liisa^^Rouva||19700313|F|||Puutarhakatu 22^^Tampere^^33210^FIN||^^CP^0401234586
PV1||O|TAYS^RADPOLI^Mammografiahuone 1^^PSHP||||DR610^Aho^Kristiina^^^LKT^Lääkäri||||||||||||KÄYNTI600005
ORC|RE|ORD600006^LIFECARE|RES600006^SECTRA_RIS||||^^^20260509100000^^R||20260509143000
OBR|1|ORD600006^LIFECARE|RES600006^SECTRA_RIS|24606-6^Mammografia bilat^RADLEX|||20260509103000|||||||20260509103000|^^MG|DR611^Saarinen^Leena^^^RAD^Radiologi||||||20260509143000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Bilateraalinen mammografia: Rintarauhaskudos ACR B. Ei epäilyttäviä massoja tai mikrokalkkeja. BI-RADS 1, normaali. Seuraava seulonta 2 vuoden kuluttua.||||||F|||20260509143000
```

---

## 13. ORM^O01 - CT abdomen order (vatsan TT-tilaus)

```
MSH|^~\&|ACUTE|KYS|SECTRA_RIS|KYS_RAD|20260509104000||ORM^O01|SECTRA000022|P|2.3|||AL|NE||FIN
PID|||PT600007^^^KYS^MR~080288-234G^^^DVV^NNFIN||Kemppainen^Timo^Sakari^^Herra||19880208|M|||Minna Canthinkatu 9^^Kuopio^^70100^FIN||^^CP^0451234575
PV1||E|KYS^PPKL^Triage 2^^PSSHP||||DR612^Partanen^Esa^^^LKT^Lääkäri||||||||||||KÄYNTI600006
ORC|NW|ORD600007^ACUTE|||||^^^20260509104000^^S||20260509104000|DR612^Partanen^Esa^^^LKT^Lääkäri
OBR|1|ORD600007^ACUTE||36267-3^CT vatsa varjoaine^RADLEX|||20260509104000||||||||DR612^Partanen^Esa^^^LKT^Lääkäri||||||||||VATSAKIPU^Akuutti vatsakipu
```

---

## 14. ORU^R01 - CT abdomen result (vatsan TT-vastaus)

```
MSH|^~\&|SECTRA_RIS|KYS_RAD|ACUTE|KYS|20260509140000||ORU^R01|SECTRA000023|P|2.3|||AL|NE||FIN
PID|||PT600007^^^KYS^MR~080288-234G^^^DVV^NNFIN||Kemppainen^Timo^Sakari^^Herra||19880208|M|||Minna Canthinkatu 9^^Kuopio^^70100^FIN||^^CP^0451234575
PV1||E|KYS^PPKL^Triage 2^^PSSHP||||DR612^Partanen^Esa^^^LKT^Lääkäri||||||||||||KÄYNTI600006
ORC|RE|ORD600007^ACUTE|RES600007^SECTRA_RIS||||^^^20260509104000^^S||20260509140000
OBR|1|ORD600007^ACUTE|RES600007^SECTRA_RIS|36267-3^CT vatsa varjoaine^RADLEX|||20260509113000|||||||20260509113000|^^CT|DR613^Tamminen^Juha^^^RAD^Radiologi||||||20260509140000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Vatsan varjoaine-TT: Umpilisäke turvonnut, halkaisija 12mm. Ympäröivä rasva ödemaattinen. Appendikoliitti havaittavissa. Löydös sopii akuuttiin appendisiittiin. Ei suolentukkeumaa.||||||F|||20260509140000
```

---

## 15. ORM^O01 - Skeletal X-ray order (luuston röntgentilaus)

```
MSH|^~\&|APOTTI|HUS_HELSINKI|SECTRA_RIS|HUS_RAD|20260509114000||ORM^O01|SECTRA000024|P|2.5|||AL|NE||FIN|UTF-8
PID|||PT600008^^^HUS^MR~031002-567H^^^DVV^NNFIN||Tuominen^Nelli^Kristiina^^Neiti||20021003|F|||Fredrikinkatu 42^^Helsinki^^00100^FIN||^^CP^0409876552
PV1||E|MEIL^PPKL^Triage 3^^HUS||||DR614^Salonen^Tero^^^LKT^Lääkäri||||||||||||KÄYNTI600007
ORC|NW|ORD600008^APOTTI|||||^^^20260509114000^^S||20260509114000|DR614^Salonen^Tero^^^LKT^Lääkäri
OBR|1|ORD600008^APOTTI||37534-4^Rtg ranne^RADLEX|||20260509114000||||||||DR614^Salonen^Tero^^^LKT^Lääkäri||||||||||RANNE^Rannevamma, kaatuminen
```

---

## 16. ORU^R01 - Skeletal X-ray result (luuston röntgenvastaus)

```
MSH|^~\&|SECTRA_RIS|HUS_RAD|APOTTI|HUS_HELSINKI|20260509140000||ORU^R01|SECTRA000025|P|2.5|||AL|NE||FIN|UTF-8
PID|||PT600008^^^HUS^MR~031002-567H^^^DVV^NNFIN||Tuominen^Nelli^Kristiina^^Neiti||20021003|F|||Fredrikinkatu 42^^Helsinki^^00100^FIN||^^CP^0409876552
PV1||E|MEIL^PPKL^Triage 3^^HUS||||DR614^Salonen^Tero^^^LKT^Lääkäri||||||||||||KÄYNTI600007
ORC|RE|ORD600008^APOTTI|RES600008^SECTRA_RIS||||^^^20260509114000^^S||20260509140000
OBR|1|ORD600008^APOTTI|RES600008^SECTRA_RIS|37534-4^Rtg ranne^RADLEX|||20260509120000|||||||20260509120000|^^Ranne|DR615^Kallio^Minna^^^RAD^Radiologi||||||20260509140000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Ranteen rtg: Distaalisen radiuksen murtuma (Colles), minimaalinen dislokaatio. Ulnan processus styloideus ehjä. Karpaalilinjat normaalit.||||||F|||20260509140000
```

---

## 17. ADT^A04 - Radiology registration (röntgenrekisteröinti)

```
MSH|^~\&|LIFECARE|TAYS|SECTRA_RIS|TAYS_RAD|20260509101500||ADT^A04|SECTRA000026|P|2.4|||AL|NE||FIN|UTF-8
EVN|A04|20260509101500
PID|||PT600009^^^TAYS^MR~250890-901J^^^DVV^NNFIN||Leppänen^Katri^Maria^^Rouva||19900825|F|||Verkatehtaankatu 10^^Tampere^^33100^FIN||^^CP^0401234587
PV1||O|TAYS^RADPOLI^Odotustila^^PSHP||||DR616^Rantala^Ville^^^LKT^Lääkäri||||||||||||KÄYNTI600008
```

---

## 18. ADT^A03 - Radiology discharge (röntgenkäynnin päättäminen)

```
MSH|^~\&|SECTRA_RIS|TAYS_RAD|LIFECARE|TAYS|20260509113000||ADT^A03|SECTRA000027|P|2.4|||AL|NE||FIN|UTF-8
EVN|A03|20260509113000
PID|||PT600009^^^TAYS^MR~250890-901J^^^DVV^NNFIN||Leppänen^Katri^Maria^^Rouva||19900825|F|||Verkatehtaankatu 10^^Tampere^^33100^FIN||^^CP^0401234587
PV1||O|TAYS^RADPOLI^Tutkimushuone 2^^PSHP||||DR616^Rantala^Ville^^^LKT^Lääkäri||||||||||||KÄYNTI600008|||||||||||||||||||||||20260509101500|20260509113000
```

---

## 19. ORM^O01 - Order cancellation (tilauksen peruutus)

```
MSH|^~\&|LIFECARE|TAYS|SECTRA_RIS|TAYS_RAD|20260509150000||ORM^O01|SECTRA000028|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT600010^^^TAYS^MR~090175-234K^^^DVV^NNFIN||Mäntymäki^Riitta^Anneli^^Rouva||19750109|F|||Koulukatu 8^^Tampere^^33200^FIN||^^CP^0407654332
PV1||O|TAYS^POLI5^Vastaanottohuone 10^^PSHP||||DR617^Ahola^Sami^^^LKT^Lääkäri||||||||||||KÄYNTI600009
ORC|CA|ORD600009^LIFECARE|||||^^^20260509090000^^R||20260509150000|DR617^Ahola^Sami^^^LKT^Lääkäri
OBR|1|ORD600009^LIFECARE||71020^Thorax PA+LAT^RADLEX|||20260509090000||||||||DR617^Ahola^Sami^^^LKT^Lääkäri
```

---

## 20. ORU^R01 - Addendum/correction to report (lausunnon korjaus)

```
MSH|^~\&|SECTRA_RIS|TAYS_RAD|LIFECARE|TAYS|20260509170000||ORU^R01|SECTRA000029|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT600001^^^TAYS^MR~120580-234A^^^DVV^NNFIN||Hakkarainen^Jorma^Antero^^Herra||19800512|M|||Hämeenkatu 55^^Tampere^^33200^FIN||^^CP^0401234584
PV1||E|TAYS^PPKL^Triage 2^^PSHP||||DR600^Niemi^Satu^^^LKT^Lääkäri||||||||||||KÄYNTI600001
ORC|RE|ORD600001^LIFECARE|RES600001^SECTRA_RIS||||^^^20260509080000^^S||20260509170000
OBR|1|ORD600001^LIFECARE|RES600001^SECTRA_RIS|71020^Thorax PA+LAT^RADLEX|||20260509083000|||||||20260509083000|^^Thorax|DR603^Ikäheimo^Reijo^^^RAD^Radiologi||||||20260509170000|||C
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Korjattu lausunto: Keuhkokentissä ei infiltraatteja. Sydämen koko normaali. Vasemmalla puolella pieni atelektaasi alakeuhkossa. Ei pleuranestettä.||||||C|||20260509170000
```
