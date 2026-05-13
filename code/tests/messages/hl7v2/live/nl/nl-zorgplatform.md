# Zorgplatform (ChipSoft) - real HL7v2 ER7 messages

## 1. ORU^R01 - ZorgDomein referral letter with embedded PDF via Zorgplatform

```
MSH|^~\&|ZorgDomein||||20160324163509+0100||ORU^R01|ZD200046119|P|2.4
PID|1||^^^NLMINBIZA^NNNLD||van der Berg&van der&Berg^J^M^^^^L||20000101|M|||Keizersgracht 120&Keizersgracht&120^bis^Amsterdam^^1015CZ^NL^H||020-6891345_^NET^Internet^j.vanderberg@voorbeeld.nl
PV1|1|O
ORC|NW|ZD200046119|||||||20160324163432+0100|^&&het Willems^D.E.F.||01004567^&&van Hoekstra^P.Q.^^^^^^VEKTIS||015-2222222
OBR|1|ZD200046119||CIS^Cardiologie^ZORGDOMEIN|||20160324163432+0100|||||||||01004567^&&van Hoekstra^P.Q.^^^^^^VEKTIS
OBX|1|NM|VB^^123||||||||F
OBX|2|ED|CARHAR^Hartfalen^ZORGDOMEIN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAgADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzUwOCswMScwMCcpCj4+CmVuZG9iag==||||||F
OBX|3|FT|CARCOA001^consult cardioloog^ZORGDOMEIN||||||||F
```

---

## 2. ORU^R01 - ZorgDomein diagnostic request with embedded PDF via Zorgplatform

```
MSH|^~\&|ZorgDomein||||20160324163441+0100||ORU^R01|ZD200046119|P|2.4
PID|1||^^^NLMINBIZA^NNNLD||van der Berg&van der&Berg^J^M^^^^L||20000101|M|||Keizersgracht 120&Keizersgracht&120^bis^Amsterdam^^1015CZ^NL^H||020-6891345
PV1|1|O
ORC|NW|ZD200046119|||||||20160324163432+0100|^&&het Willems^D.E.F.||01004567^&&van Hoekstra^P.Q.^^^^^^VEKTIS||015-2222222
OBR|1|ZD200046119||CIS^Cardiologie^ZORGDOMEIN|||20160324163432+0100|||||||||01004567^&&van Hoekstra^P.Q.^^^^^^VEKTIS
OBX|1|NM|AF^^123||||||||F
OBX|2|ED|CARHAR^Hartfalen^ZORGDOMEIN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAgADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzQ0MSswMScwMCcpCj4+CmVuZG9iag==||||||F
OBX|3|FT|CARCOA001^consult cardioloog^ZORGDOMEIN||||||||F
```

---

## 3. ORM^O01 - ZorgDomein V3 diagnostic order via Zorgplatform (dermatology)

```
MSH|^~\&|ZorgDomein||||20220410143000+0200||ORM^O01|ZD300012345|P|2.5.1
PID|1||123456782^^^NLMINBIZA^NNNLD||de Wit&de&Wit^Johanna^M^^^^L||19751220|F|||Kerkstraat 45^^Rotterdam^^3011CD^NL^H||010-4445566^PRN^PH~^^^j.dewit@email.nl^NET^Internet
PV1|1|O
IN1|1|||VGZ^VGZ Zorgverzekeraar||||||123456789
ORC|NW|ZD300012345|||||||20220410143000+0200|^&&van Groenendaal^B.C.||01234567^&&van Leeuwen^A.B.^^^^^^VEKTIS||010-7778899
OBR|1|ZD300012345||DER^Dermatologie^ZORGDOMEIN|||20220410143000+0200|||||||||01234567^&&van Leeuwen^A.B.^^^^^^VEKTIS
OBX|1|FT|DERMOA001^Consult dermatoloog^ZORGDOMEIN||Verdachte moedervlek rechter schouder, groei in afgelopen 3 maanden||||||||F
```

---

## 4. ORM^O01 - ZorgDomein V3 radiology order via Zorgplatform

```
MSH|^~\&|ZorgDomein||||20220601101500+0200||ORM^O01|ZD300054321|P|2.5.1
PID|1||666777888^^^NLMINBIZA^NNNLD||Pietersen^Maria^A^^^^L||19830415|F|||Singel 100^^Amsterdam^^1012AB^NL^H||020-5551234
PV1|1|O
ORC|NW|ZD300054321|||||||20220601101500+0200|^&&van de Broek^C.D.||09876543^&&Evers^E.F.^^^^^^VEKTIS||020-3334444
OBR|1|ZD300054321||RAD^Radiologie^ZORGDOMEIN|||20220601101500+0200|||||||||09876543^&&Evers^E.F.^^^^^^VEKTIS
OBX|1|FT|RADMRI001^MRI knie rechts^ZORGDOMEIN||Patiente klaagt over aanhoudende kniepijn rechts na sportblessure. Verdenking meniscusletsel.||||||||F
```

---

## 5. ADT^A01 - patient admit in ChipSoft HiX via Zorgplatform

```
MSH|^~\&|HIX|OLVG|ZORGPLATFORM|CHIPSOFT|20220115080000||ADT^A01^ADT_A01|HIX20220115001|P|2.4|||AL|NE|NLD
EVN|A01|20220115080000
PID|1||PAT10001^^^OLVG^PI~371926485^^^NLMINBIZA^NNNLD||van der Linden^Cornelis^J||19520310|M|||Oosterpark 50^^Amsterdam^^1091AC^NL^H||020-5993000^PRN^PH||||M
PV1|1|I|CARD^401^2^OLVG||||10001^de Graaf^Floor^^^dr.|||CAR||||ADM|||10001^de Graaf^Floor^^^dr.|IP|||||||||||||||||OLVG||A|||20220115075000
NK1|1|van der Linden^Elisabeth^A|SPO^Echtgenote|Oosterpark 50^^Amsterdam^^1091AC^NL|020-5993001
IN1|1|MENZIS001^Menzis|MENZIS||Postbus 75000^^Enschede^^7500KA^NL
```

---

## 6. ADT^A03 - patient discharge from HiX via Zorgplatform

```
MSH|^~\&|HIX|OLVG|ZORGPLATFORM|CHIPSOFT|20220120140000||ADT^A03^ADT_A03|HIX20220120001|P|2.4|||AL|NE|NLD
EVN|A03|20220120140000
PID|1||PAT10001^^^OLVG^PI~371926485^^^NLMINBIZA^NNNLD||van der Linden^Cornelis^J||19520310|M
PV1|1|I|CARD^401^2^OLVG||||10001^de Graaf^Floor^^^dr.|||CAR||||ADM|||10001^de Graaf^Floor^^^dr.|IP|||||||||||||||||OLVG||D|||20220115075000|||20220120133000
```

---

## 7. ADT^A08 - patient update from HiX via Zorgplatform

```
MSH|^~\&|HIX|OLVG|ZORGPLATFORM|CHIPSOFT|20220201093000||ADT^A08^ADT_A08|HIX20220201001|P|2.4|||AL|NE|NLD
EVN|A08|20220201093000
PID|1||PAT10001^^^OLVG^PI~371926485^^^NLMINBIZA^NNNLD||van der Linden^Cornelis^J||19520310|M|||Waterlooplein 15^^Amsterdam^^1011NZ^NL^H||020-6001234^PRN^PH~^^^c.vanderlinden@email.nl
PV1|1|O|POLI^CARD^01^OLVG||||10001^de Graaf^Floor^^^dr.
```

---

## 8. ADT^A04 - outpatient registration HiX via Zorgplatform

```
MSH|^~\&|HIX|ANTONIUS|ZORGPLATFORM|CHIPSOFT|20220315100000||ADT^A04^ADT_A04|HIX20220315001|P|2.4|||AL|NE|NLD
EVN|A04|20220315100000
PID|1||PAT20001^^^ANTONIUS^PI~482917365^^^NLMINBIZA^NNNLD||Kok^Lisette^M||19880520|F|||Soestdijkseweg Zuid 40^^Bilthoven^^3721AA^NL^H||030-2345678^PRN^PH||||O
PV1|1|O|POLI^GYNA^01^ANTONIUS||||20002^Willems^Anke^^^dr.|||GYN||||REG|||20002^Willems^Anke^^^dr.|OP
```

---

## 9. ADT^A02 - patient transfer from HiX via Zorgplatform

```
MSH|^~\&|HIX|CATHARINA|ZORGPLATFORM|CHIPSOFT|20220420140000||ADT^A02^ADT_A02|HIX20220420001|P|2.4|||AL|NE|NLD
EVN|A02|20220420140000
PID|1||PAT30001^^^CATHARINA^PI~639184275^^^NLMINBIZA^NNNLD||Hermans^Willem^F||19700901|M
PV1|1|I|INT^201^1^CATHARINA||||30003^Jacobs^Martijn^^^dr.|||INT||||ADM|||30003^Jacobs^Martijn^^^dr.|IP||||||||||||||IC^101^1^CATHARINA|||CATHARINA||A|||20220418060000
```

---

## 10. ORU^R01 - lab result from HiX lab module via Zorgplatform

```
MSH|^~\&|HIX_LAB|AMPHIA|HIX_EPD|AMPHIA|20220505080000||ORU^R01^ORU_R01|HLAB20220505001|P|2.4|||AL|NE|NLD
PID|1||PAT40001^^^AMPHIA^PI~724185936^^^NLMINBIZA^NNNLD||Brouwer^Thomas^G||19650415|M|||Molenberg 1^^Breda^^4817JA^NL
PV1|1|I|CHIR^301^1^AMPHIA||||40004^Martens^Pieter^^^dr.
ORC|RE|ORD1001^HIX_EPD|FILL2001^HIX_LAB||CM
OBR|1|ORD1001^HIX_EPD|FILL2001^HIX_LAB|57021-8^CBC^LN|||20220505060000|||||||40004^Martens^Pieter^^^dr.||||||20220505075000||LAB|F
OBX|1|NM|6690-2^Leucocyten^LN||8.5|10*9/l|4.0-10.0|N|||F
OBX|2|NM|718-7^Hemoglobine^LN||9.2|mmol/l|8.5-11.0|N|||F
OBX|3|NM|4544-3^Hematocriet^LN||0.44|l/l|0.41-0.51|N|||F
OBX|4|NM|777-3^Trombocyten^LN||210|10*9/l|150-400|N|||F
OBX|5|NM|2160-0^Kreatinine^LN||95|umol/l|62-106|N|||F
```

---

## 11. ORU^R01 - nutrition questionnaire from HiX via Zorgplatform

```
MSH|^~\&|HIX_DIET|RIJNSTATE|ZORGPLATFORM|CHIPSOFT|20220610120000||ORU^R01^ORU_R01|HDIET20220610001|P|2.4|||AL|NE|NLD
PID|1||PAT50001^^^RIJNSTATE^PI~856349172^^^NLMINBIZA^NNNLD||Smeets^Anna^K||19450320|F|||Velperweg 50^^Arnhem^^6824BM^NL
PV1|1|I|INT^502^1^RIJNSTATE||||50005^Janssen^Erik^^^dr.
ORC|RE|ORD1101^HIX|FILL2101^HIX_DIET||CM
OBR|1|ORD1101^HIX|FILL2101^HIX_DIET|75282-4^Nutrition assessment^LN|||20220610100000|||||||50005^Janssen^Erik^^^dr.||||||20220610115000||DIET|F
OBX|1|NM|29463-7^Body weight^LN||52.3|kg|||||F
OBX|2|NM|8302-2^Body height^LN||1.62|m|||||F
OBX|3|NM|39156-5^BMI^LN||19.9|kg/m2|18.5-25.0|N|||F
OBX|4|ST|75303-8^Nutrition screening status^LN||Score 3: matig risico op ondervoeding||||||F
```

---

## 12. ORU^R01 - function report spirometry from HiX via Zorgplatform

```
MSH|^~\&|HIX_FUNC|DEVENTER_ZH|ZORGPLATFORM|CHIPSOFT|20220720150000||ORU^R01^ORU_R01|HFUNC20220720001|P|2.4|||AL|NE|NLD
PID|1||PAT60001^^^DEVENTER_ZH^PI~913527486^^^NLMINBIZA^NNNLD||Dekker^Robert^H||19580830|M|||Brinkgreverweg 100^^Deventer^^7413AA^NL
PV1|1|O|LONG^FUNC^01^DEVENTER_ZH||||60006^de Boer^Henk^^^dr.
ORC|RE|ORD1201^HIX|FILL2201^HIX_FUNC||CM
OBR|1|ORD1201^HIX|FILL2201^HIX_FUNC|81459-0^Spirometry panel^LN|||20220720130000|||||||60006^de Boer^Henk^^^dr.||||||20220720145000||FUNC|F
OBX|1|NM|19868-9^FEV1^LN||2.45|L|2.80-4.20|L|||F
OBX|2|NM|19870-5^FVC^LN||3.85|L|3.50-5.20|N|||F
OBX|3|NM|19926-5^FEV1/FVC^LN||63.6|%|>70|L|||F
OBX|4|TX|SPIRO_INTERP^Interpretation^LOCAL||Matig obstructief longfunctiepatroon. Advies: bronchusverwijdingstest.||||||F
```

---

## 13. ORM^O01 - ZorgDomein orthopedic referral via Zorgplatform

```
MSH|^~\&|ZorgDomein||||20220801090000+0200||ORM^O01|ZD300098765|P|2.5.1
PID|1||291638574^^^NLMINBIZA^NNNLD||van Dijk^Pieter^M^^^^L||19700620|M|||Stadhouderslaan 20^^Den Haag^^2517HZ^NL^H||070-3456789
PV1|1|O
ORC|NW|ZD300098765|||||||20220801090000+0200|^&&Vermeulen^A.B.||11223344^&&van Kamp^G.H.^^^^^^VEKTIS||070-1112222
OBR|1|ZD300098765||ORT^Orthopedie^ZORGDOMEIN|||20220801090000+0200|||||||||11223344^&&van Kamp^G.H.^^^^^^VEKTIS
OBX|1|FT|ORTCON001^consult orthopeed^ZORGDOMEIN||Patient klaagt over chronische lage rugpijn, uitstralend naar links been. Lasegue positief links. Verdenking HNP L4-L5.||||||||F
```

---

## 14. ORM^O01 - ZorgDomein cardiology echo request via Zorgplatform

```
MSH|^~\&|ZorgDomein||||20220915110000+0200||ORM^O01|ZD300076543|P|2.5.1
PID|1||472816953^^^NLMINBIZA^NNNLD||Hendriks^Gerda^W^^^^L||19500105|F|||Burg. de Monchyplein 10^^Den Haag^^2585BE^NL^H||070-9998877
PV1|1|O
IN1|1|||ONVZ^ONVZ Ziektekostenverzekeraar||||||987654321
ORC|NW|ZD300076543|||||||20220915110000+0200|^&&de Ruiter^I.J.||55667788^&&Kramer^K.L.^^^^^^VEKTIS||070-5556666
OBR|1|ZD300076543||CAR^Cardiologie^ZORGDOMEIN|||20220915110000+0200|||||||||55667788^&&Kramer^K.L.^^^^^^VEKTIS
OBX|1|FT|CARECHO01^Echocardiografie^ZORGDOMEIN||Patiente met dyspnoe d'effort en enkelvocht. Verdenking hartfalen. Graag echocardiografie.||||||||F
```

---

## 15. ORU^R01 - multimedia document result from HiX via Zorgplatform

```
MSH|^~\&|HIX_MULTI|MEANDER_MC|ZORGPLATFORM|CHIPSOFT|20221001090000||ORU^R01^ORU_R01|HMULT20221001001|P|2.4|||AL|NE|NLD
PID|1||PAT70001^^^MEANDER_MC^PI~518462937^^^NLMINBIZA^NNNLD||Bakker^Johannes^L||19750430|M|||Maatweg 3^^Amersfoort^^3813TJ^NL
PV1|1|O|CHIR^WOND^01^MEANDER_MC||||70007^Kuiper^Frank^^^dr.
ORC|RE|ORD1301^HIX|FILL2301^HIX_MULTI||CM
OBR|1|ORD1301^HIX|FILL2301^HIX_MULTI|72170-4^Photo documentation^LN|||20221001083000|||||||70007^Kuiper^Frank^^^dr.||||||20221001085000||DOC|F
OBX|1|TX|72170-4^Photo documentation^LN||Wondcontrole linker onderbeen, 3 weken post-operatief. Goede genezing.||||||F
OBX|2|ED|IMG^Wound Photo^LOCAL||^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAoACgDASIAAhEBAxEB/8QAGAABAAMBAAAAAAAAAAAAAAAAAAUHCAb/xAAsEAABAwIFAgUFAQAAAAAAAAABAgMEAAURBhIhMQdBExQiUWEIFTKBkaH/xAAYAQADAQEAAAAAAAAAAAAAAAACAwQFAf/EAB8RAAICAgIDAQAAAAAAAAAAAAECAAMREgQhIjFBcf/aAAwDAQACEQMRAD8AtGlKVRwmJzxBa0q0bpOdEfQ0jO84R+KR3P8AKy/1I6p3G/XB+1WaU9EtcZxTQDDhQt9YOCVKHYHsBt71Z/VbqPE6f2cvshuXJk+EWYjOBzgEblR7AE/2sZ3G5y7vcZNxnOl2VKdU8+s9yo5NSck6N0mR8OoLYXf2Jjp9cL1a+o9lk2+4SWQmS2l1pt0pQ6gqAKVJzQQRWu6xn0Wsq7x1OsDAOEtSPOOnsCy2VJH9UgVsylFLkQR5FIrsUDUUV56h3tOHMJ3a7LbQ4YMN2QEK2C8iCcH9180bzfJ97uMm5XKQuTNlOKdffdOVLWo7kmpH6g8cm6dMLy0welzFMi3LHqcSFHOP4M1XvSTqld+n16MuCEyYchIRMhOK9LqR2I7EHcGoj3LNtMR8PhJSSNjLrsnUK+3y4T7tfJ781yYcPqkPFRA7J3OEgdgNhVldD+ksjo7Y1F5xqVdZmEyphQcICRulCO+AT+zVK9bupUjqNeRJDbjFrhBSIsJxWepB3Uo+5Nh+q5qjrtyNugVVVBQmX704utq6edRLRL0/MlFMd9K3WG3CG30hQJSpOCD/AKKKNM7zzr+f/9k=||||||F
```

---

## 16. ORU^R01 - pacemaker control report from HiX via Zorgplatform

```
MSH|^~\&|HIX_CARD|ISALA|ZORGPLATFORM|CHIPSOFT|20221110150000||ORU^R01^ORU_R01|HCARD20221110001|P|2.4|||AL|NE|NLD
PID|1||PAT80001^^^ISALA^PI~736291548^^^NLMINBIZA^NNNLD||Bosman^Hendrik^K||19550120|M|||IJsselkade 10^^Zwolle^^8011AR^NL
PV1|1|O|CARD^PACE^01^ISALA||||80008^Verhoeven^Willem^^^dr.
ORC|RE|ORD1401^HIX|FILL2401^HIX_CARD||CM
OBR|1|ORD1401^HIX|FILL2401^HIX_CARD|75042-2^Cardiac device check^LN|||20221110130000|||||||80008^Verhoeven^Willem^^^dr.||||||20221110145000||CARD|F
OBX|1|TX|PACE_REPORT^Pacemaker Report^LOCAL||Medtronic Advisa DR MRI, implantatie 2019-03-15\.br\Batterijstatus: 2.78V, geschatte levensduur >4 jaar\.br\Sensing: A 2.5mV, V 12.0mV\.br\Drempels: A 0.75V/0.4ms, V 1.0V/0.4ms\.br\Modus: DDD 60-130/min\.br\Conclusie: Goede pacemakerfunctie, volgende controle over 6 maanden.||||||F
```

---

## 17. ORU^R01 - pathology report from HiX via Zorgplatform

```
MSH|^~\&|HIX_PATH|ERASMUS|ZORGPLATFORM|CHIPSOFT|20221201110000||ORU^R01^ORU_R01|HPATH20221201001|P|2.5.1|||AL|NE|NLD
PID|1||PAT90001^^^ERASMUS^PI~847261935^^^NLMINBIZA^NNNLD||Mulder^Kees^P||19800305|M|||Westzeedijk 100^^Rotterdam^^3016AH^NL
PV1|1|I|CHIR^601^1^ERASMUS||||90009^van Rijn^Sandra^^^dr.
ORC|RE|ORD1501^HIX|FILL2501^HIX_PATH||CM
OBR|1|ORD1501^HIX|FILL2501^HIX_PATH|22637-3^Pathology report^LN|||20221130090000|||||||90009^van Rijn^Sandra^^^dr.||||||20221201103000||PATH|F
OBX|1|FT|22637-3^Pathology report^LN||Materiaal: Colonbiopt sigmoideum\.br\Macroscopie: 3 biopten, 2-4mm\.br\Microscopie: Slijmvliesfragmenten met actieve chronische ontsteking, cryptabcessen\.br\Conclusie: Colitis ulcerosa, actief.||||||F
```

---

## 18. ORU^R01 with embedded radiology PDF from HiX via Zorgplatform

```
MSH|^~\&|HIX_RAD|REINIER_HAGA|ZORGPLATFORM|CHIPSOFT|20230115090000||ORU^R01^ORU_R01|HRAD20230115001|P|2.5.1|||AL|NE|NLD
PID|1||PAT95001^^^REINIER_HAGA^PI~264918573^^^NLMINBIZA^NNNLD||Janssen^Anna^B||19700830|F|||Sportlaan 600^^Den Haag^^2548NL^NL
PV1|1|O|RAD^CT1^01^REINIER_HAGA||||95009^Vos^Pieter^^^dr.
ORC|RE|ORD1601^HIX|FILL2601^HIX_RAD||CM
OBR|1|ORD1601^HIX|FILL2601^HIX_RAD|24627-2^Chest CT^LN|||20230115080000|||||||95009^Vos^Pieter^^^dr.||||||20230115085500||RAD|F
OBX|1|TX|24627-2^Chest CT^LN||CT thorax: geen longembolie. Bilaterale basale atelectase. Geen pleuravocht.||||||F
OBX|2|ED|PDF^Radiology Report^LOCAL||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFJhZGlvbG9naWUgVmVyc2xhZykKL0NyZWF0b3IgKENoaXBTb2Z0IEhpWCBSYWRpb2xvZ2llKQovUHJvZHVjZXIgKENoaXBTb2Z0IFBERiBHZW5lcmF0b3IpCi9DcmVhdGlvbkRhdGUgKEQ6MjAyMzAxMTUwOTAwMDApCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9DYXRhbG9nCi9QYWdlcyAzIDAgUgo+PgplbmRvYmoKMyAwIG9iago8PAovVHlwZSAvUGFnZXMKL0tpZHMgWzQgMCBSXQovQ291bnQgMQovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQo+PgplbmRvYmoKNCAwIG9iago8PAovVHlwZSAvUGFnZQovUGFyZW50IDMgMCBSCi9Db250ZW50cyA1IDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSA2IDAgUgo+Pgo+Pgo+PgplbmRvYmoKNSAwIG9iago8PAovTGVuZ3RoIDQ0Cj4+CnN0cmVhbQpCVAovRjEgMTIgVGYKNzIgNzIwIFRkCihDVCB0aG9yYXggdmVyc2xhZykgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago2IDAgb2JqCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDcKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAxNTggMDAwMDAgbiAKMDAwMDAwMDIwNyAwMDAwMCBuIAowMDAwMDAwMzA2IDAwMDAwIG4gCjAwMDAwMDA0OTkgMDAwMDAgbiAKMDAwMDAwMDU5MyAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDcKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjY3MQolJUVPRgo=||||||F
```

---

## 19. ORM^O01 - ZorgDomein laboratory order OML V3 via Zorgplatform

```
MSH|^~\&|ZorgDomein||||20221001080000+0200||ORM^O01|ZD400011111|P|2.5.1
PID|1||583719264^^^NLMINBIZA^NNNLD||Kuiper^Frank^J^^^^L||19650210|M|||Lange Voorhout 15^^Den Haag^^2514EA^NL^H||070-1234567
PV1|1|O
ORC|NW|ZD400011111|||||||20221001080000+0200|^&&Scholten^M.N.||22334455^&&Peeters^O.P.^^^^^^VEKTIS||070-2223333
OBR|1|ZD400011111||LAB^Klinische Chemie^ZORGDOMEIN|||20221001080000+0200|||||||||22334455^&&Peeters^O.P.^^^^^^VEKTIS
OBX|1|FT|LABBLOED01^Bloedonderzoek^ZORGDOMEIN||Gaarne volledig bloedbeeld, nierfunctie, leverfunctie, glucose nuchter. Patient gebruikt metformine.||||||||F
```

---

## 20. ADT^A05 - pre-admission from HiX via Zorgplatform

```
MSH|^~\&|HIX|TERGOOI|ZORGPLATFORM|CHIPSOFT|20230201100000||ADT^A05^ADT_A05|HIX20230201001|P|2.4|||AL|NE|NLD
EVN|A05|20230201100000
PID|1||PAT99001^^^TERGOOI^PI~847362915^^^NLMINBIZA^NNNLD||Schouten^Elisabeth^W||19600715|F|||Utrechtseweg 100^^Hilversum^^1213CL^NL^H||035-6012345^PRN^PH||||M
PV1|1|I|ORT^201^1^TERGOOI||||99010^Groen^Adriaan^^^dr.|||ORT||||PREADM|||99010^Groen^Adriaan^^^dr.|IP|||||||||||||||||TERGOOI||P|||20230210080000
NK1|1|Schouten^Jan^J|SPO^Echtgenoot|Utrechtseweg 100^^Hilversum^^1213CL^NL|035-6012346
IN1|1|CZ001^CZ Zorgverzekeraar|CZ||Postbus 100^^Tilburg^^5000AC^NL
```
