# NEN 7504 (Dutch national standard) - real HL7v2 ER7 messages

## 1. ORU^R01 - full laboratory panel with BSN (HL7 Nederland / NEN 7504)

```
MSH|^~\&|sendFac|SendApp|||20170822095500||ORU^R01|64517000001|P|2.4||
PID|||1234567^^^^PI~328917456^^^NLMINBIZA^NNNLD||Bakker&&Bakker&&^Margaretha^^^^^L~Bakker&&Bakker^Margaretha^^^^^B||19500101|F|||Alderstraat 1&Alderstraat&1^^Jipsinghuizen^^1234AB^^M~Alderstraat 1&Alderstraat&1^^Jipsinghuizen^^1234AB^^L||010-1234567^PRN^PH~^^^Margaretha@example.com|||M|||||||Aalst|Y|2||||""|N|N|||||||
OBX|1|ST|882-1^ABO+Rh group||O pos||||||F
PV1|1|I|0RGC2||||
OBR|1|123|20050701015070^Labosys||||200507010907||||||""|||3004^van den Ende||||200507010907||201708220955||S|F||^^^^^R
OBX|1|ST|266^Bezinking^L^BSE||2|mm/uur|0 - 15|""|||F
OBX|2|ST|325^Leucocyten^L^LEU||6.7|/nl|4.0 - 10.0|""|||F
OBX|3|ST|323^Hemoglobine^L^HB||10.2|mmol/l|8.5 - 11.0|""|||F
OBX|4|ST|324^Hematocriet^L^HT||0.48|l/l|0.41 - 0.51|""|||F
OBX|5|ST|326^Ery's^L^ERY||5.2|/pl|4.4 - 5.8|""|||F
OBX|6|ST|328^MCV^L^MCV1||92|fl|80 - 100|""|||F
OBX|7|ST|329^MCH^L^MCH||1.97|fmol|1.60 - 2.10|""|||F
OBX|8|ST|330^MCHC^L^MCHC||21.3|mmol/l|19.0 - 23.0|""|||F
OBX|9|ST|648^Ureum^L^UR||3.9|mmol/l|2.5 - 7.5|""|||F
OBX|10|ST|630^Kreatinine^L^KR||99|umol/l|70 - 110|""|||F
OBX|11|ST|638^Natrium^L^NA||139|mmol/l|135 - 145|""|||F
OBX|12|ST|628^Kalium^L^K||3.9|mmol/l|3.5 - 5.0|""|||F
OBX|13|ST|2325^Alk.fosf.^L^AF||52|U/l|0 - 120|""|||F
OBX|14|ST|2326^Gamma GT^L^GGT||29|U/l| - 50|""|||F
OBX|15|ST|2327^ASAT^L^ASAT||19|U/l|0 - 40|""|||F
OBX|16|ST|2328^ALAT^L^ALAT||20|U/l|0 - 45|""|||F
OBX|17|ST|614^Glucose^L^GLUS||10.3|mmol/l|4.0 - 7.8|H|||F
OBX|18|ST|34^TSH^L^TSH||0.78|mU/l|0.4 - 4.0|""|||F
```

---

## 2. OML^O21 - Nictiz Lab2Lab outsourced lab order with bacterial susceptibility (NEN 7504)

```
MSH|^~\&|LIMS_SENDER|LAB_UITBESTEDEND|LIMS_RECEIVER|LAB_INBESTEDEND|20220315091200||OML^O21^OML_O21|MSG20220315001|P|2.5.1|||AL|AL|NLD|8859/1|||2.16.840.1.113883.2.4.3.11.60.25.10.1^NICTIZ^ISO
PID|||ANON123^^^^PI~462918375^^^NLMINBIZA^NNNLD||Jansen^Pieter^H||19680312|M|||Oudegracht 45^^Utrecht^^3511AX^NL
PV1|1|O|MICRO^LAB1^01^LAB_UITBESTEDEND
ORC|NW|ORD001^LIMS_SENDER|||||1^^^20220315091200^^R
OBR|1|ORD001^LIMS_SENDER||29576-6^Bacterial susceptibility panel^LN|||20220315080000||||||Urineweginfectie, verdenking ESBL|||1234^de Groot^Willem^^^arts||||||20220315091200
SPM|1|||UR^Urine^HL70487||||||||||||20220314153000
OBR|2|ORD001-P1^LIMS_SENDER||634-6^Bacteria identified^LN|||20220314160000
OBX|1|CWE|634-6^Bacteria identified^LN||112283007^Escherichia coli^SCT||||||F
OBX|2|ST|6652-2^Meropenem Susceptibility by MIC^LN||>=16|mg/L||R|||F
OBX|3|ST|7029-2^Meropenem Susceptibility by Gradient strip^LN||8.0|mg/L||R|||F
OBX|4|CWE|18943-1^Meropenem Susceptibility^LN|||||R|||F
```

---

## 3. OUL^R22 - Nictiz Lab2Lab result with microbiology findings (NEN 7504)

```
MSH|^~\&|LIMS_RECEIVER|LAB_INBESTEDEND|LIMS_SENDER|LAB_UITBESTEDEND|20220316140000||OUL^R22^OUL_R22|MSG20220316001|P|2.5.1|||AL|AL|NLD|8859/1|||2.16.840.1.113883.2.4.3.11.60.25.10.50^NICTIZ^ISO
PID|||ANON123^^^^PI~462918375^^^NLMINBIZA^NNNLD||Jansen^Pieter^H||19680312|M
PV1|1|O|MICRO^LAB1^01^LAB_UITBESTEDEND
SPM|1|||UR^Urine^HL70487||||||||||||20220314153000
OBR|1|ORD001^LIMS_SENDER|FILL001^LIMS_RECEIVER|29576-6^Bacterial susceptibility panel^LN|||20220315080000||||||||||||||20220316133000||LAB|F
ORC|RE|ORD001^LIMS_SENDER|FILL001^LIMS_RECEIVER||CM
OBX|1|CWE|634-6^Bacteria identified^LN||112283007^Escherichia coli^SCT||||||F
OBX|2|ST|6652-2^Meropenem Susceptibility by MIC^LN||>=16|mg/L||R|||F
OBX|3|ST|7029-2^Meropenem Susceptibility by Gradient strip^LN||8.0|mg/L||R|||F
OBX|4|CWE|18943-1^Meropenem Susceptibility^LN|||||R|||F
OBX|5|ST|185-9^Ciprofloxacin Susceptibility by MIC^LN||>4|mg/L||R|||F
OBX|6|ST|141-2^Amoxicillin+Clavulanate Susceptibility by MIC^LN||16|mg/L||I|||F
OBX|7|ST|193-3^Gentamicin Susceptibility by MIC^LN||0.5|mg/L||S|||F
OBX|8|ST|524-9^Trimethoprim+Sulfamethoxazole Susceptibility by MIC^LN||>8|mg/L||R|||F
```

---

## 4. ORM^O01 - ZorgDomein diagnostic request with BSN (NEN 7504 ORM V3)

```
MSH|^~\&|ZorgDomein||||20220410143000+0200||ORM^O01|ZD300012345|P|2.5.1
PID|1||537829146^^^NLMINBIZA^NNNLD||van der Linden&van der&Linden^Johanna^M^^^^L||19751220|F|||Witte de Withstraat 45^^Rotterdam^^3012BM^NL^H||010-4445566^PRN^PH~^^^j.vanderlinden@email.nl^NET^Internet
PV1|1|O
IN1|1|||VGZ^VGZ Zorgverzekeraar||||||537829146
ORC|NW|ZD300012345|||||||20220410143000+0200|^&&van Houten^B.C.||01234567^&&Verhoeven^A.B.^^^^^^VEKTIS||010-7778899
OBR|1|ZD300012345||DER^Dermatologie^ZORGDOMEIN|||20220410143000+0200|||||||||01234567^&&Verhoeven^A.B.^^^^^^VEKTIS
OBX|1|FT|DERMOA001^Consult dermatoloog^ZORGDOMEIN||Verdachte moedervlek rechter schouder, groei in afgelopen 3 maanden||||||||F
```

---

## 5. ORU^R01 - ZorgDomein referral letter with embedded PDF (NEN 7504)

```
MSH|^~\&|ZorgDomein||||20160324163509+0100||ORU^R01|ZD200046119|P|2.4
PID|1||^^^NLMINBIZA^NNNLD||van den Berg&van den&Berg^P^J^^^^L||20000101|M|||Leidsestraat 88  bis&Leidsestraat&88^bis^Eindhoven^^5611AA^NL^H||040-2839174^NET^Internet^p.vandenberg@email.nl
PV1|1|O
ORC|NW|ZD200046119|||||||20160324163432+0100|^&&de Groot^A.B.C.||01004567^&&van der Meer^Z.Z.^^^^^^VEKTIS||015-2222222
OBR|1|ZD200046119||CIS^Cardiologie^ZORGDOMEIN|||20160324163432+0100|||||||||01004567^&&van der Meer^Z.Z.^^^^^^VEKTIS
OBX|1|NM|VB^^123||||||||F
OBX|2|ED|CARHAR^Hartfalen^ZORGDOMEIN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAgADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzUwOCswMScwMCcpCj4+CmVuZG9iag==||||||F
OBX|3|FT|CARCOA001^consult cardioloog^ZORGDOMEIN||||||||F
```

---

## 6. ORU^R01 - ZorgDomein diagnostic request form with embedded PDF (NEN 7504)

```
MSH|^~\&|ZorgDomein||||20160324163441+0100||ORU^R01|ZD200046119|P|2.4
PID|1||^^^NLMINBIZA^NNNLD||van den Berg&van den&Berg^P^J^^^^L||20000101|M|||Leidsestraat 88  bis&Leidsestraat&88^bis^Eindhoven^^5611AA^NL^H||040-2839174
PV1|1|O
ORC|NW|ZD200046119|||||||20160324163432+0100|^&&de Groot^A.B.C.||01004567^&&van der Meer^Z.Z.^^^^^^VEKTIS||015-2222222
OBR|1|ZD200046119||CIS^Cardiologie^ZORGDOMEIN|||20160324163432+0100|||||||||01004567^&&van der Meer^Z.Z.^^^^^^VEKTIS
OBX|1|NM|AF^^123||||||||F
OBX|2|ED|CARHAR^Hartfalen^ZORGDOMEIN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAgADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzQ0MSswMScwMCcpCj4+CmVuZG9iag==||||||F
OBX|3|FT|CARCOA001^consult cardioloog^ZORGDOMEIN||||||||F
```

---

## 7. ADT^A01 - NEN 7504 patient admit with BSN and Dutch address

```
MSH|^~\&|HIS|UMCU|EPD|UMCU|20210315080000||ADT^A01^ADT_A01|ADT20210315001|P|2.4|||AL|NE|NLD
EVN|A01|20210315080000
PID|1||PAT001^^^UMCU^PI~471829365^^^NLMINBIZA^NNNLD||Timmerman^Adriaan^J||19450620|M|||Maliebaan 22^^Utrecht^^3581CR^NL^H||030-2345678^PRN^PH||||M||||||||||N
PV1|1|I|CARD^201^1^UMCU||||12345^Brouwer^Theodora^^^dr.|||CAR||||ADM|||12345^Brouwer^Theodora^^^dr.|IP|||||||||||||||||UMCU||A|||20210315075500
NK1|1|Timmerman^Elisabeth^M|SPO^Echtgenote|Maliebaan 22^^Utrecht^^3581CR^NL|030-2345679
IN1|1|ZILVERK001^Zilveren Kruis|ZK||Postbus 200^^Leiden^^2300AE^NL
```

---

## 8. ADT^A03 - patient discharge (NEN 7504)

```
MSH|^~\&|HIS|UMCU|EPD|UMCU|20210320140000||ADT^A03^ADT_A03|ADT20210320001|P|2.4|||AL|NE|NLD
EVN|A03|20210320140000
PID|1||PAT001^^^UMCU^PI~471829365^^^NLMINBIZA^NNNLD||Timmerman^Adriaan^J||19450620|M
PV1|1|I|CARD^201^1^UMCU||||12345^Brouwer^Theodora^^^dr.|||CAR||||ADM|||12345^Brouwer^Theodora^^^dr.|IP|||||||||||||||||UMCU||D|||20210315075500|||20210320133000
```

---

## 9. ADT^A08 - patient update with Dutch insurance (NEN 7504)

```
MSH|^~\&|HIS|VUMC|EPD|VUMC|20210501093000||ADT^A08^ADT_A08|ADT20210501001|P|2.4|||AL|NE|NLD
EVN|A08|20210501093000
PID|1||PAT002^^^VUMC^PI~639518274^^^NLMINBIZA^NNNLD||Vermeer^Femke^L||19700815|F|||Vondelstraat 25^^Amsterdam^^1054GE^NL^H||020-6234567^PRN^PH~^^^f.vermeer@email.nl||||M
PV1|1|O|POLI^INTERN^01^VUMC||||54321^Wolters^Jacobus^^^dr.
IN1|1|CZ001^CZ Zorgverzekeraar|CZ||Postbus 100^^Tilburg^^5000AC^NL
```

---

## 10. ADT^A02 - patient transfer between wards (NEN 7504)

```
MSH|^~\&|HIS|ERASMUS|EPD|ERASMUS|20210612110000||ADT^A02^ADT_A02|ADT20210612001|P|2.4|||AL|NE|NLD
EVN|A02|20210612110000
PID|1||PAT003^^^ERASMUS^PI~819374625^^^NLMINBIZA^NNNLD||de Jong^Hendrik^P||19800305|M
PV1|1|I|CHIR^401^2^ERASMUS||||67890^Dekker^Saskia^^^dr.|||CHI||||ADM|||67890^Dekker^Saskia^^^dr.|IP||||||||||||||ICU^102^1^ERASMUS|||ERASMUS||A|||20210610080000
```

---

## 11. ORU^R01 - clinical chemistry result with LOINC codes (NEN 7504 Lab2Zorg)

```
MSH|^~\&|LABSYS|STAR_MDC|HIS|UMCU|20220401083000||ORU^R01^ORU_R01|LAB20220401001|P|2.5.1|||AL|AL|NLD|8859/1
PID|1||PAT100^^^UMCU^PI~729461835^^^NLMINBIZA^NNNLD||Mulder^Jacobus^J||19720910|M|||Biltstraat 100^^Utrecht^^3572BH^NL
PV1|1|I|INT^302^1^UMCU||||99001^Visser^Elisabeth^^^dr.
ORC|RE|ORD200^HIS|FILL300^LABSYS||CM
OBR|1|ORD200^HIS|FILL300^LABSYS|24323-8^Comprehensive metabolic panel^LN|||20220401070000|||||||99001^Visser^Elisabeth^^^dr.||||||20220401082500||LAB|F
OBX|1|NM|2345-7^Glucose^LN||6.8|mmol/l|4.0-7.8|N|||F
OBX|2|NM|2160-0^Creatinine^LN||88|umol/l|62-106|N|||F
OBX|3|NM|3094-0^Ureum^LN||5.2|mmol/l|2.5-7.5|N|||F
OBX|4|NM|2951-2^Natrium^LN||141|mmol/l|135-145|N|||F
OBX|5|NM|2823-3^Kalium^LN||4.1|mmol/l|3.5-5.0|N|||F
OBX|6|NM|17861-6^Calcium^LN||2.35|mmol/l|2.20-2.60|N|||F
OBX|7|NM|1742-6^ALAT^LN||25|U/l|0-45|N|||F
OBX|8|NM|1920-8^ASAT^LN||22|U/l|0-40|N|||F
```

---

## 12. OML^O21 - clinical chemistry lab order (NEN 7504 Lab2Lab)

```
MSH|^~\&|LIMS_A|LAB_AMSTERDAM|LIMS_B|LAB_ROTTERDAM|20220510140000||OML^O21^OML_O21|MSG20220510001|P|2.5.1|||AL|AL|NLD|8859/1|||2.16.840.1.113883.2.4.3.11.60.25.10.1^NICTIZ^ISO
PID|||PAT200^^^^PI~846173529^^^NLMINBIZA^NNNLD||Bos^Anneke^L||19850225|F|||Laan van Meerdervoort 200^^Den Haag^^2517BH^NL
PV1|1|O|KLIN_CHEM^01^01^LAB_AMSTERDAM
ORC|NW|ORD300^LIMS_A|||||1^^^20220510140000^^R
OBR|1|ORD300^LIMS_A||24323-8^Comprehensive metabolic panel^LN|||20220510120000||||||Diabetes monitoring, HbA1c niet beschikbaar bij aanvragend lab|||5678^Smit^Maria^^^arts
SPM|1|||BLD^Blood^HL70487||||||||||||20220510115000
```

---

## 13. ACK - acknowledgement response (NEN 7504 Lab2Lab)

```
MSH|^~\&|LIMS_B|LAB_ROTTERDAM|LIMS_A|LAB_AMSTERDAM|20220510140100||ACK^O21^ACK|ACK20220510001|P|2.5.1|||AL|AL|NLD|8859/1
MSA|AA|MSG20220510001
```

---

## 14. ORL^O22 - lab order acknowledgment (NEN 7504 Lab2Lab)

```
MSH|^~\&|LIMS_RECEIVER|LAB_INBESTEDEND|LIMS_SENDER|LAB_UITBESTEDEND|20220315100000||ORL^O22^ORL_O22|ORL20220315001|P|2.5.1|||AL|AL|NLD|8859/1
MSA|AA|MSG20220315001
```

---

## 15. ORU^R01 - hematology with abnormal flags (NEN 7504)

```
MSH|^~\&|LABSYS|ISALA|HIS|ISALA|20220715090000||ORU^R01|LAB20220715001|P|2.4||
PID|||PAT300^^^^PI~513847296^^^NLMINBIZA^NNNLD||Hoekstra^Willem^K||19550120|M|||IJsselkade 10^^Zwolle^^8011AR^NL
PV1|1|I|HEMATO^201^1^ISALA||||11111^Kuipers^Daan^^^dr.
OBR|1|ORD400^HIS|FILL500^LABSYS|57021-8^CBC^LN|||20220715070000||||||""|||11111^Kuipers^Daan^^^dr.||||20220715085500||LAB|F
OBX|1|NM|6690-2^Leucocyten^LN||15.2|10*9/l|4.0-10.0|H|||F
OBX|2|NM|789-8^Erythrocyten^LN||3.2|10*12/l|4.0-5.5|L|||F
OBX|3|NM|718-7^Hemoglobine^LN||7.1|mmol/l|8.5-11.0|L|||F
OBX|4|NM|4544-3^Hematocriet^LN||0.34|l/l|0.41-0.51|L|||F
OBX|5|NM|787-2^MCV^LN||106|fl|80-100|H|||F
OBX|6|NM|777-3^Trombocyten^LN||95|10*9/l|150-400|L|||F
```

---

## 16. ORM^O01 - GP referral for radiology (NEN 7504 via ZorgDomein)

```
MSH|^~\&|ZorgDomein||||20220601101500+0200||ORM^O01|ZD300054321|P|2.5.1
PID|1||945263718^^^NLMINBIZA^NNNLD||de Wit^Lotte^A^^^^L||19830415|F|||Herengracht 100^^Amsterdam^^1015BS^NL^H||020-5551234
PV1|1|O
ORC|NW|ZD300054321|||||||20220601101500+0200|^&&Meijer^C.D.||09876543^&&Bakker^E.F.^^^^^^VEKTIS||020-3334444
OBR|1|ZD300054321||RAD^Radiologie^ZORGDOMEIN|||20220601101500+0200|||||||||09876543^&&Bakker^E.F.^^^^^^VEKTIS
OBX|1|FT|RADMRI001^MRI knie rechts^ZORGDOMEIN||Patiente klaagt over aanhoudende kniepijn rechts na sportblessure. Verdenking meniscusletsel.||||||||F
```

---

## 17. ORU^R01 - pathology report with text result (NEN 7504)

```
MSH|^~\&|PALGA|PATHLAB|HIS|RADBOUDUMC|20220901150000||ORU^R01^ORU_R01|PATH20220901001|P|2.5.1|||AL|AL|NLD
PID|1||PAT400^^^RADBOUDUMC^PI~284619537^^^NLMINBIZA^NNNLD||Wolters^Theodora^B||19700830|F|||Plein 1944 nr 5^^Nijmegen^^6525HP^NL
PV1|1|I|CHIR^501^1^RADBOUDUMC||||22222^Hendriks^Adriaan^^^dr.
ORC|RE|ORD500^HIS|FILL600^PALGA||CM
OBR|1|ORD500^HIS|FILL600^PALGA|22637-3^Pathology report^LN|||20220830100000|||||||22222^Hendriks^Adriaan^^^dr.||||||20220901143000||PATH|F
OBX|1|FT|22637-3^Pathology report^LN||Macroscopie: Huidbiopt rechter schouder, diameter 6mm\.br\Microscopie: Melanocytaire proliferatie met atypische kenmerken\.br\Conclusie: Dysplastische naevus, Clark graad II\.br\Advies: Excisie met 5mm marge.||||||F
```

---

## 18. ORU^R01 with embedded PDF pathology report (NEN 7504)

```
MSH|^~\&|PALGA|PATHLAB|HIS|LUMC|20221015110000||ORU^R01^ORU_R01|PATH20221015001|P|2.5.1|||AL|AL|NLD
PID|1||PAT500^^^LUMC^PI~175293846^^^NLMINBIZA^NNNLD||Smit^Geert^M||19650420|M|||Rapenburg 70^^Leiden^^2311EZ^NL
PV1|1|I|ONCO^302^1^LUMC||||33333^de Jong^Margaretha^^^dr.
ORC|RE|ORD600^HIS|FILL700^PALGA||CM
OBR|1|ORD600^HIS|FILL700^PALGA|22637-3^Pathology report^LN|||20221014090000|||||||33333^de Jong^Margaretha^^^dr.||||||20221015103000||PATH|F
OBX|1|FT|22637-3^Pathology report^LN||Colonbiopt: adenocarcinoom, matig gedifferentieerd.||||||F
OBX|2|ED|PDF^Pathology Report PDF^LOCAL||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFBhdGhvbG9naWUgUmFwcG9ydCkKL0NyZWF0b3IgKFBBTEdBIFN5c3RlZW0pCi9Qcm9kdWNlciAoUEFMR0EgUERGIEdlbmVyYXRvcikKL0NyZWF0aW9uRGF0ZSAoRDoyMDIyMTAxNTExMDAwMCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbNCAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCj4+CmVuZG9iago0IDAgb2JqCjw8Ci9UeXBlIC9QYWdlCi9QYXJlbnQgMyAwIFIKL0NvbnRlbnRzIDUgMCBSCi9SZXNvdXJjZXMgPDwKL0ZvbnQgPDwKL0YxIDYgMCBSCj4+Cj4+Cj4+CmVuZG9iago1IDAgb2JqCjw8Ci9MZW5ndGggNDQKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgo3MiA3MjAgVGQKKENvbG9uYmlvcHQgcGF0aG9sb2dpZSByYXBwb3J0KSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjYgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNwowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDE1OCAwMDAwMCBuIAowMDAwMDAwMjA3IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAgbiAKMDAwMDAwMDQ5OSAwMDAwMCBuIAowMDAwMDAwNTkzIDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNwovUm9vdCAyIDAgUgo+PgpzdGFydHhyZWYKNjcxCiUlRU9GCg==||||||F
```

---

## 19. ORU^R01 with embedded radiology image (NEN 7504)

```
MSH|^~\&|PACS|RADLAB|HIS|MAASTRICHTUMC|20221120140000||ORU^R01^ORU_R01|RAD20221120001|P|2.5.1|||AL|AL|NLD
PID|1||PAT600^^^MUMC^PI~648371925^^^NLMINBIZA^NNNLD||van Dijk^Jan^P||19580712|M|||Debyelaan 25^^Maastricht^^6229HX^NL
PV1|1|O|RAD^MRI1^01^MUMC||||44444^Meijer^Floor^^^dr.
ORC|RE|ORD700^HIS|FILL800^PACS||CM
OBR|1|ORD700^HIS|FILL800^PACS|73221-1^MRI knee^LN|||20221120100000|||||||44444^Meijer^Floor^^^dr.||||||20221120133000||RAD|F
OBX|1|TX|73221-1^MRI knee^LN||MRI rechter knie: mediaal meniscusletsel graad II. Geen kruisbandletsel. Milde artrose.||||||F
OBX|2|ED|IMG^MRI Key Image^LOCAL||^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAyADIDASIAAhEBAxEB/8QAGwABAAMAAwEAAAAAAAAAAAAAAAgFBgcBBAn/xAAzEAABAwIFAgQFAwUAAAAAAAABAgMEAAURBhIhMUFRBxMiYRQycZGhQoGxCBUjcsH/xAAaAQACAwEBAAAAAAAAAAAAAAADBAABAgUG/8QAIhEAAgICAgICAwAAAAAAAAAAAAECEQMhBDESQSJRE2Fx/9oADAMBAAIRAxEAPwCuBpU0qpJ6DKOa8FJSpStAAJJJAAAySSdgO5q30XYpGI73HtMHIZdzzXlYJCGm0gqccVjsEpBJ+lNz4d+F9v0bHZud6bam37RKhnhxPxJP6Ubfbckd+1MRhbJCUpKZnkJBi/hVe+HN1ZgXl+KrnNJfbEV0uFSASlJJxtnvT30c2R/wBvhRorL7kYR2EhDqyVKbwB6T3I71R0r6pCE0VKKUpRilKUApXhSglJKiAAMkk7CufFbU7r/D+7z7K0qXIhstCQ0g+p1tCwHEJA/UQk4x0yKuvAXx3s3iEz8A+kWu/tp+diKczDjvlD+4jueuOo9tcTxBv8u86huE6a88+4p0MhTqws5abAQkcAAYSkdqv/D7SpZ8R4EOe4tMeM0t9xtsEeYpOAACe3qNWi2CUIJxPqpWM0zqGXf7M3CucrHxKVl2C8oCEqW2Ukp0GOmScHritmpSlUKiuNe2qPdrbJt8xAcjSmltOpPdKhgj7GvnJ4laCl+HOsZFin+px1PnQ5JTgSGFk5SrHBIwoEdxX0crHaz0/E1Hp+42SeFGNOYU0sp2UjPCge4OCD7VcJUxeaDSp5nhD4S3nxHuK22T8HaY6stzLkoYbbJGcJA/UsjoK29v/pPcccCJeu4rbR2UmE2VKH+uSM/YVI3TGnIOn7Yw1AhRYraE+nyo6QonqonqfcmuopIQMAY+grmZOT5exzBxy9lNpTwht+go0YWyaJj8/Kp2ROZSpCUo2S2nPdOckn3rZ0pWRilKUApSlAKUpQClKUB/9k=||||||F
```

---

## 20. ADT^A04 - outpatient registration for polyclinic visit (NEN 7504)

```
MSH|^~\&|HIS|UMCG|EPD|UMCG|20220801090000||ADT^A04^ADT_A04|ADT20220801001|P|2.4|||AL|NE|NLD
EVN|A04|20220801090000
PID|1||PAT700^^^UMCG^PI~375816492^^^NLMINBIZA^NNNLD||Brouwer^Saskia^S||19900215|F|||Herestraat 1^^Groningen^^9713GZ^NL^H||050-3612345^PRN^PH~^^^s.brouwer@email.nl||||O
PV1|1|O|POLI^OOG^01^UMCG||||55555^van Dijk^Pieter^^^dr.|||OOG||||REG|||55555^van Dijk^Pieter^^^dr.|OP
```
