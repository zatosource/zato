# HL7v2 Imaging messages (Kuvantamisen HL7-sanomat) - real HL7v2 ER7 messages

---

## 1. ORM^O01 - X-ray chest order (thorax-röntgentilaus)

```
MSH|^~\&|EHR_SYSTEM|HOSPITAL_A|RIS_SYSTEM|RAD_A|20260509080000||ORM^O01|IMG000001|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900001^^^HOSP_A^MR~100680-234A^^^DVV^NNFIN||Laaksonen^Jari^Tapani^^Herra||19800610|M|||Mannerheimintie 75^^Helsinki^^00270^FIN||^^CP^0401234598
PV1||E|HOSP_A^PPKL^Triage 2^^SHP_A||||DR900^Virtanen^Elina^^^LKT^Lääkäri||||||||||||KÄYNTI900001
ORC|NW|ORD900001^EHR_SYSTEM|||||^^^20260509080000^^S||20260509080000|DR900^Virtanen^Elina^^^LKT^Lääkäri
OBR|1|ORD900001^EHR_SYSTEM||71020^Thorax PA+LAT^RADLEX|||20260509080000||||||||DR900^Virtanen^Elina^^^LKT^Lääkäri||||||||||KUUME^Kuume ja yskä, pneumoniaepäily
```

---

## 2. ORM^O01 - CT abdomen with contrast order (vatsan varjoaine-TT-tilaus)

```
MSH|^~\&|EHR_SYSTEM|HOSPITAL_B|RIS_SYSTEM|RAD_B|20260509091000||ORM^O01|IMG000002|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900002^^^HOSP_B^MR~220570-567B^^^DVV^NNFIN||Mäkelä^Eila^Marjatta^^Rouva||19700522|F|||Hämeenkatu 60^^Tampere^^33200^FIN||^^PH^0332345681
PV1||I|HOSP_B^KIR1^Huone 304^Vuode 1^SHP_B||||DR901^Korhonen^Juha^^^LKT^Lääkäri||||||||||||HOITO900001
ORC|NW|ORD900002^EHR_SYSTEM|||||^^^20260509091000^^R||20260509091000|DR901^Korhonen^Juha^^^LKT^Lääkäri
OBR|1|ORD900002^EHR_SYSTEM||36267-3^CT vatsa varjoaine^RADLEX|||20260509091000||||||||DR901^Korhonen^Juha^^^LKT^Lääkäri||||||||||KASVAIN^Vatsan alueen kasvainseuranta
```

---

## 3. ORM^O01 - MRI brain order (aivojen MRI-tilaus)

```
MSH|^~\&|EHR_SYSTEM|HOSPITAL_C|RIS_SYSTEM|RAD_C|20260509100000||ORM^O01|IMG000003|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900003^^^HOSP_C^MR~051190-890C^^^DVV^NNFIN||Hämäläinen^Satu^Kristiina^^Rouva||19901105|F|||Kauppakatu 18^^Kuopio^^70100^FIN||^^CP^0509876556
PV1||O|HOSP_C^NEUR1^Vastaanottohuone 2^^SHP_C||||DR902^Mäkinen^Esa^^^LKT^Lääkäri||||||||||||KÄYNTI900002
ORC|NW|ORD900003^EHR_SYSTEM|||||^^^20260509100000^^R||20260509100000|DR902^Mäkinen^Esa^^^LKT^Lääkäri
OBR|1|ORD900003^EHR_SYSTEM||36554-4^MRI aivot^RADLEX|||20260509100000||||||||DR902^Mäkinen^Esa^^^LKT^Lääkäri||||||||||MS^MS-taudin seuranta
```

---

## 4. ORM^O01 - Ultrasound abdomen order (vatsan ultraäänitilaus)

```
MSH|^~\&|EHR_SYSTEM|HOSPITAL_D|RIS_SYSTEM|RAD_D|20260509093000||ORM^O01|IMG000004|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900004^^^HOSP_D^MR~300865-123D^^^DVV^NNFIN||Lehtinen^Pertti^Antero^^Herra||19650830|M|||Isokatu 15^^Oulu^^90100^FIN||^^CP^0401234599
PV1||O|HOSP_D^POLI2^Vastaanottohuone 4^^SHP_D||||DR903^Laine^Minna^^^LKT^Lääkäri||||||||||||KÄYNTI900003
ORC|NW|ORD900004^EHR_SYSTEM|||||^^^20260509093000^^R||20260509093000|DR903^Laine^Minna^^^LKT^Lääkäri
OBR|1|ORD900004^EHR_SYSTEM||76830-1^UÄ vatsa^RADLEX|||20260509093000||||||||DR903^Laine^Minna^^^LKT^Lääkäri||||||||||MAKSA^Kohonneet maksa-arvot
```

---

## 5. ORU^R01 - X-ray chest result (thorax-röntgenvastaus)

```
MSH|^~\&|RIS_SYSTEM|RAD_A|EHR_SYSTEM|HOSPITAL_A|20260509110000||ORU^R01|IMG000005|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900001^^^HOSP_A^MR~100680-234A^^^DVV^NNFIN||Laaksonen^Jari^Tapani^^Herra||19800610|M|||Mannerheimintie 75^^Helsinki^^00270^FIN||^^CP^0401234598
PV1||E|HOSP_A^PPKL^Triage 2^^SHP_A||||DR900^Virtanen^Elina^^^LKT^Lääkäri||||||||||||KÄYNTI900001
ORC|RE|ORD900001^EHR_SYSTEM|RES900001^RIS_SYSTEM||||^^^20260509080000^^S||20260509110000
OBR|1|ORD900001^EHR_SYSTEM|RES900001^RIS_SYSTEM|71020^Thorax PA+LAT^RADLEX|||20260509083000|||||||20260509083000|^^Thorax|DR904^Ikonen^Reijo^^^RAD^Radiologi||||||20260509110000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Thorax PA+LAT: Oikealla alakeuhkossa infiltraatti, sopii pneumoniaan. Sydämen koko normaali. Ei pleuranestettä. Hilus normaalirakenteinen bilateraalisesti.||||||F|||20260509110000
```

---

## 6. ORU^R01 - CT abdomen result with base64 PDF (vatsan TT-vastaus PDF-liitteellä)

```
MSH|^~\&|RIS_SYSTEM|RAD_B|EHR_SYSTEM|HOSPITAL_B|20260509150000||ORU^R01|IMG000006|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900002^^^HOSP_B^MR~220570-567B^^^DVV^NNFIN||Mäkelä^Eila^Marjatta^^Rouva||19700522|F|||Hämeenkatu 60^^Tampere^^33200^FIN||^^PH^0332345681
PV1||I|HOSP_B^KIR1^Huone 304^Vuode 1^SHP_B||||DR901^Korhonen^Juha^^^LKT^Lääkäri||||||||||||HOITO900001
ORC|RE|ORD900002^EHR_SYSTEM|RES900002^RIS_SYSTEM||||^^^20260509091000^^R||20260509150000
OBR|1|ORD900002^EHR_SYSTEM|RES900002^RIS_SYSTEM|36267-3^CT vatsa varjoaine^RADLEX|||20260509120000|||||||20260509120000|^^CT|DR905^Koskinen^Leena^^^RAD^Radiologi||||||20260509150000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Vatsan varjoaine-TT: Maksa-metastaasit pienentyneeet verrattuna aiempaan kuvaukseen. Suurin lesio 18mm (aiemmin 25mm). Ei uusia leesioita. Haima, perna ja munuaiset normaalit. Ei vapaa nestettä.||||||F|||20260509150000
OBX|2|ED|PDF^TT-lausunto^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK||||||F|||20260509150000
```

---

## 7. ORU^R01 - MRI brain result with base64 PDF (aivojen MRI-vastaus PDF-liitteellä)

```
MSH|^~\&|RIS_SYSTEM|RAD_C|EHR_SYSTEM|HOSPITAL_C|20260512140000||ORU^R01|IMG000007|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900003^^^HOSP_C^MR~051190-890C^^^DVV^NNFIN||Hämäläinen^Satu^Kristiina^^Rouva||19901105|F|||Kauppakatu 18^^Kuopio^^70100^FIN||^^CP^0509876556
PV1||O|HOSP_C^NEUR1^Vastaanottohuone 2^^SHP_C||||DR902^Mäkinen^Esa^^^LKT^Lääkäri||||||||||||KÄYNTI900002
ORC|RE|ORD900003^EHR_SYSTEM|RES900003^RIS_SYSTEM||||^^^20260509100000^^R||20260512140000
OBR|1|ORD900003^EHR_SYSTEM|RES900003^RIS_SYSTEM|36554-4^MRI aivot^RADLEX|||20260511090000|||||||20260511090000|^^MRI|DR906^Paavola^Timo^^^RAD^Radiologi||||||20260512140000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Aivojen MRI: Periventrikulaarisesti ja subkortikaalisesti useita T2-hyperintensiivisiä leesioita, joista yksi uusi oikeassa frontaalilohkossa. Löydös sopii MS-taudin aktiivisuuteen. Infratentoriaalisesti ei poikkeavaa.||||||F|||20260512140000
OBX|2|ED|PDF^MRI-lausunto^L||^application^pdf^Base64^JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8Ci9NYXJrZWQgdHJ1ZQo+PgovTGFuZyAoZmkpCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCj4+CmVuZG9iagoK||||||F|||20260512140000
```

---

## 8. ORU^R01 - Ultrasound abdomen result (vatsan ultraäänivastaus)

```
MSH|^~\&|RIS_SYSTEM|RAD_D|EHR_SYSTEM|HOSPITAL_D|20260509130000||ORU^R01|IMG000008|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900004^^^HOSP_D^MR~300865-123D^^^DVV^NNFIN||Lehtinen^Pertti^Antero^^Herra||19650830|M|||Isokatu 15^^Oulu^^90100^FIN||^^CP^0401234599
PV1||O|HOSP_D^POLI2^Vastaanottohuone 4^^SHP_D||||DR903^Laine^Minna^^^LKT^Lääkäri||||||||||||KÄYNTI900003
ORC|RE|ORD900004^EHR_SYSTEM|RES900004^RIS_SYSTEM||||^^^20260509093000^^R||20260509130000
OBR|1|ORD900004^EHR_SYSTEM|RES900004^RIS_SYSTEM|76830-1^UÄ vatsa^RADLEX|||20260509110000|||||||20260509110000|^^UÄ|DR907^Mattila^Sanna^^^RAD^Radiologi||||||20260509130000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Vatsan UÄ: Maksa suurentunut, ekorakenteeltaan tasaisesti tiivistynyt, sopii steatoosiin. Sappirakko normaali, ei konkrementteja. Haima normaali. Munuaiset symmetriset. Aortta normaali.||||||F|||20260509130000
```

---

## 9. ORM^O01 - Nuclear medicine bone scan order (luuston isotooppikuvaus-tilaus)

```
MSH|^~\&|EHR_SYSTEM|HOSPITAL_E|RIS_SYSTEM|RAD_E_NM|20260509102000||ORM^O01|IMG000009|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900005^^^HOSP_E^MR~140565-456E^^^DVV^NNFIN||Korhonen^Raimo^Olavi^^Herra||19650514|M|||Yliopistonkatu 20^^Turku^^20100^FIN||^^CP^0407654337
PV1||I|HOSP_E^ONK1^Huone 205^Vuode 1^SHP_E||||DR908^Ahonen^Tuula^^^LKT^Lääkäri||||||||||||HOITO900002
ORC|NW|ORD900005^EHR_SYSTEM|||||^^^20260509102000^^R||20260509102000|DR908^Ahonen^Tuula^^^LKT^Lääkäri
OBR|1|ORD900005^EHR_SYSTEM||39811-5^Luuston isotooppikuvaus^RADLEX|||20260509102000||||||||DR908^Ahonen^Tuula^^^LKT^Lääkäri||||||||||ETÄPESÄKE^Etäpesäke-epäily, eturauhassyöpä
```

---

## 10. ORU^R01 - Nuclear medicine bone scan result (luuston isotooppikuvaus-vastaus)

```
MSH|^~\&|RIS_SYSTEM|RAD_E_NM|EHR_SYSTEM|HOSPITAL_E|20260510150000||ORU^R01|IMG000010|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900005^^^HOSP_E^MR~140565-456E^^^DVV^NNFIN||Korhonen^Raimo^Olavi^^Herra||19650514|M|||Yliopistonkatu 20^^Turku^^20100^FIN||^^CP^0407654337
PV1||I|HOSP_E^ONK1^Huone 205^Vuode 1^SHP_E||||DR908^Ahonen^Tuula^^^LKT^Lääkäri||||||||||||HOITO900002
ORC|RE|ORD900005^EHR_SYSTEM|RES900005^RIS_SYSTEM||||^^^20260509102000^^R||20260510150000
OBR|1|ORD900005^EHR_SYSTEM|RES900005^RIS_SYSTEM|39811-5^Luuston isotooppikuvaus^RADLEX|||20260510090000|||||||20260510090000|^^NM|DR909^Saarinen^Kari^^^RAD^Radiologi||||||20260510150000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Luuston isotooppikuvaus: Oikealla puolella L3-nikamassa lisääntynyt kertymä, sopii metastaattiseen muutokseen. Vasemman lonkan alueella lievä kertymän lisääntyminen, todennäköisesti degeneratiivinen muutos. Muilta osin normaali kertymäjakauma.||||||F|||20260510150000
```

---

## 11. ORM^O01 - PET-CT order (PET-TT-tilaus)

```
MSH|^~\&|EHR_SYSTEM|HOSPITAL_A|RIS_SYSTEM|RAD_A_PET|20260509110000||ORM^O01|IMG000011|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900006^^^HOSP_A^MR~080375-789F^^^DVV^NNFIN||Salminen^Matti^Juhani^^Herra||19750308|M|||Bulevardi 30^^Helsinki^^00120^FIN||^^CP^0451234580
PV1||I|HOSP_A^KEUH1^Huone 310^Vuode 1^SHP_A||||DR910^Nurmi^Harri^^^LKT^Lääkäri||||||||||||HOITO900003
ORC|NW|ORD900006^EHR_SYSTEM|||||^^^20260509110000^^R||20260509110000|DR910^Nurmi^Harri^^^LKT^Lääkäri
OBR|1|ORD900006^EHR_SYSTEM||44136-0^PET-TT koko keho^RADLEX|||20260509110000||||||||DR910^Nurmi^Harri^^^LKT^Lääkäri||||||||||KEUHKOSYÖPÄ^Keuhkosyövän levinneisyysselvitys
```

---

## 12. ORU^R01 - PET-CT result (PET-TT-vastaus)

```
MSH|^~\&|RIS_SYSTEM|RAD_A_PET|EHR_SYSTEM|HOSPITAL_A|20260512160000||ORU^R01|IMG000012|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900006^^^HOSP_A^MR~080375-789F^^^DVV^NNFIN||Salminen^Matti^Juhani^^Herra||19750308|M|||Bulevardi 30^^Helsinki^^00120^FIN||^^CP^0451234580
PV1||I|HOSP_A^KEUH1^Huone 310^Vuode 1^SHP_A||||DR910^Nurmi^Harri^^^LKT^Lääkäri||||||||||||HOITO900003
ORC|RE|ORD900006^EHR_SYSTEM|RES900006^RIS_SYSTEM||||^^^20260509110000^^R||20260512160000
OBR|1|ORD900006^EHR_SYSTEM|RES900006^RIS_SYSTEM|44136-0^PET-TT koko keho^RADLEX|||20260511080000|||||||20260511080000|^^PET|DR911^Kallio^Minna^^^RAD^Radiologi||||||20260512160000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||PET-TT koko keho: Oikean yläkeuhkon tuumori metabolisesti aktiivinen, SUVmax 12.5. Oikean hilusn imusolmukkeissa metabolista aktiivisuutta, SUVmax 6.2. Ei kaukoetäpesäkkeitä. Maksa, luusto ja aivot normaalit.||||||F|||20260512160000
```

---

## 13. ORM^O01 - Mammography screening order (mammografiaseulontatilaus)

```
MSH|^~\&|EHR_SYSTEM|HOSPITAL_B|RIS_SYSTEM|RAD_B|20260509100000||ORM^O01|IMG000013|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900007^^^HOSP_B^MR~150275-234G^^^DVV^NNFIN||Nieminen^Marja^Helena^^Rouva||19750215|F|||Puutarhakatu 30^^Tampere^^33210^FIN||^^CP^0401234600
PV1||O|HOSP_B^RADPOLI^Mammografiahuone 1^^SHP_B||||DR912^Rantala^Kristiina^^^LKT^Lääkäri||||||||||||KÄYNTI900004
ORC|NW|ORD900007^EHR_SYSTEM|||||^^^20260509100000^^R||20260509100000|DR912^Rantala^Kristiina^^^LKT^Lääkäri
OBR|1|ORD900007^EHR_SYSTEM||24606-6^Mammografia bilat^RADLEX|||20260509100000||||||||DR912^Rantala^Kristiina^^^LKT^Lääkäri||||||||||SEULONTA^Rintasyöpäseulonta
```

---

## 14. ORU^R01 - Mammography screening result (mammografiaseulontatulos)

```
MSH|^~\&|RIS_SYSTEM|RAD_B|EHR_SYSTEM|HOSPITAL_B|20260509143000||ORU^R01|IMG000014|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900007^^^HOSP_B^MR~150275-234G^^^DVV^NNFIN||Nieminen^Marja^Helena^^Rouva||19750215|F|||Puutarhakatu 30^^Tampere^^33210^FIN||^^CP^0401234600
PV1||O|HOSP_B^RADPOLI^Mammografiahuone 1^^SHP_B||||DR912^Rantala^Kristiina^^^LKT^Lääkäri||||||||||||KÄYNTI900004
ORC|RE|ORD900007^EHR_SYSTEM|RES900007^RIS_SYSTEM||||^^^20260509100000^^R||20260509143000
OBR|1|ORD900007^EHR_SYSTEM|RES900007^RIS_SYSTEM|24606-6^Mammografia bilat^RADLEX|||20260509103000|||||||20260509103000|^^MG|DR913^Saarinen^Leena^^^RAD^Radiologi||||||20260509143000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Mammografia bilat: Rintarauhaskudos ACR C. Vasemmassa rinnassa yläulkokvadr. 12mm kokoinen epäsäännöllinen muutos. BI-RADS 4, suositellaan jatkotutkimuksia. Oikeassa rinnassa ei poikkeavaa.||||||F|||20260509143000
```

---

## 15. ORM^O01 - Angiography order (angiografiatilaus)

```
MSH|^~\&|EHR_SYSTEM|HOSPITAL_A|RIS_SYSTEM|RAD_A|20260509113000||ORM^O01|IMG000015|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900008^^^HOSP_A^MR~010555+678H^^^DVV^NNFIN||Tuominen^Veikko^Kalevi^^Herra||19550501|M|||Aleksanterinkatu 48^^Helsinki^^00100^FIN||^^PH^0913456791
PV1||I|HOSP_A^KAR1^Huone 402^Vuode 1^SHP_A||||DR914^Salonen^Matti^^^LKT^Lääkäri||||||||||||HOITO900004
ORC|NW|ORD900008^EHR_SYSTEM|||||^^^20260509113000^^R||20260509113000|DR914^Salonen^Matti^^^LKT^Lääkäri
OBR|1|ORD900008^EHR_SYSTEM||75635-2^Koronaariangiografia^RADLEX|||20260509113000||||||||DR914^Salonen^Matti^^^LKT^Lääkäri||||||||||ANGINA^Stabiili angina pectoris
```

---

## 16. ORU^R01 - Angiography result (angiografiavastaus)

```
MSH|^~\&|RIS_SYSTEM|RAD_A|EHR_SYSTEM|HOSPITAL_A|20260509160000||ORU^R01|IMG000016|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900008^^^HOSP_A^MR~010555+678H^^^DVV^NNFIN||Tuominen^Veikko^Kalevi^^Herra||19550501|M|||Aleksanterinkatu 48^^Helsinki^^00100^FIN||^^PH^0913456791
PV1||I|HOSP_A^KAR1^Huone 402^Vuode 1^SHP_A||||DR914^Salonen^Matti^^^LKT^Lääkäri||||||||||||HOITO900004
ORC|RE|ORD900008^EHR_SYSTEM|RES900008^RIS_SYSTEM||||^^^20260509113000^^R||20260509160000
OBR|1|ORD900008^EHR_SYSTEM|RES900008^RIS_SYSTEM|75635-2^Koronaariangiografia^RADLEX|||20260509130000|||||||20260509130000|^^ANGIO|DR915^Toivonen^Kari^^^RAD^Radiologi||||||20260509160000|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Koronaariangiografia: LAD:ssa proksimaaliosassa 70% ahtauma. RCA ja LCX normaalit. Vasemman kammion toiminta normaali, EF 60%.||||||F|||20260509160000
```

---

## 17. ORM^O01 - Order cancellation (tilauksen peruutus)

```
MSH|^~\&|EHR_SYSTEM|HOSPITAL_D|RIS_SYSTEM|RAD_D|20260509140000||ORM^O01|IMG000017|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900009^^^HOSP_D^MR~200388-901J^^^DVV^NNFIN||Kärkkäinen^Anu^Kristiina^^Rouva||19880320|F|||Albertinkatu 8^^Oulu^^90100^FIN||^^CP^0407654338
PV1||O|HOSP_D^POLI3^Vastaanottohuone 6^^SHP_D||||DR916^Hakala^Vesa^^^LKT^Lääkäri||||||||||||KÄYNTI900005
ORC|CA|ORD900009^EHR_SYSTEM|||||^^^20260509090000^^R||20260509140000|DR916^Hakala^Vesa^^^LKT^Lääkäri
OBR|1|ORD900009^EHR_SYSTEM||71020^Thorax PA+LAT^RADLEX|||20260509090000||||||||DR916^Hakala^Vesa^^^LKT^Lääkäri
```

---

## 18. ADT^A04 - Radiology registration (kuvantamiskäynnin rekisteröinti)

```
MSH|^~\&|EHR_SYSTEM|HOSPITAL_A|RIS_SYSTEM|RAD_A|20260509101000||ADT^A04|IMG000018|P|2.4|||AL|NE||FIN|UTF-8
EVN|A04|20260509101000
PID|||PT900010^^^HOSP_A^MR~260895-234K^^^DVV^NNFIN||Leppänen^Ville^Tapani^^Herra||19950826|M|||Meritullinkatu 5^^Helsinki^^00170^FIN||^^CP^0451234581
PV1||O|HOSP_A^RADPOLI^Odotustila^^SHP_A||||DR917^Mäkinen^Antti^^^LKT^Lääkäri||||||||||||KÄYNTI900006
```

---

## 19. ADT^A03 - Radiology visit discharge (kuvantamiskäynnin päättäminen)

```
MSH|^~\&|RIS_SYSTEM|RAD_A|EHR_SYSTEM|HOSPITAL_A|20260509112000||ADT^A03|IMG000019|P|2.4|||AL|NE||FIN|UTF-8
EVN|A03|20260509112000
PID|||PT900010^^^HOSP_A^MR~260895-234K^^^DVV^NNFIN||Leppänen^Ville^Tapani^^Herra||19950826|M|||Meritullinkatu 5^^Helsinki^^00170^FIN||^^CP^0451234581
PV1||O|HOSP_A^RADPOLI^Tutkimushuone 3^^SHP_A||||DR917^Mäkinen^Antti^^^LKT^Lääkäri||||||||||||KÄYNTI900006|||||||||||||||||||||||20260509101000|20260509112000
```

---

## 20. ORU^R01 - Report addendum (lausunnon lisäys)

```
MSH|^~\&|RIS_SYSTEM|RAD_A|EHR_SYSTEM|HOSPITAL_A|20260509170000||ORU^R01|IMG000020|P|2.4|||AL|NE||FIN|UTF-8
PID|||PT900001^^^HOSP_A^MR~100680-234A^^^DVV^NNFIN||Laaksonen^Jari^Tapani^^Herra||19800610|M|||Mannerheimintie 75^^Helsinki^^00270^FIN||^^CP^0401234598
PV1||E|HOSP_A^PPKL^Triage 2^^SHP_A||||DR900^Virtanen^Elina^^^LKT^Lääkäri||||||||||||KÄYNTI900001
ORC|RE|ORD900001^EHR_SYSTEM|RES900001^RIS_SYSTEM||||^^^20260509080000^^S||20260509170000
OBR|1|ORD900001^EHR_SYSTEM|RES900001^RIS_SYSTEM|71020^Thorax PA+LAT^RADLEX|||20260509083000|||||||20260509083000|^^Thorax|DR904^Ikonen^Reijo^^^RAD^Radiologi||||||20260509170000|||C
OBX|1|TX|18748-4^Diagnostic imaging study^LN||Lisälausunto: Tarkemmassa tarkastelussa infiltraatin yhteydessä nähtävissä pieni bronkogrammi, vahvistaa pneumoniadiagnoosia. Kontrollikuva 2 viikon kuluttua suositeltava.||||||C|||20260509170000
```
