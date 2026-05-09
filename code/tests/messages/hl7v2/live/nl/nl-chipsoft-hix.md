# ChipSoft HiX - real HL7v2 ER7 messages

---

## 1. ORU^R01 - Lab results (blood count and chemistry)

```
MSH|^~\&|sendFac|SendApp|||20170822095500||ORU^R01|64517000001|P|2.4||
PID|||1234567^^^^PI~999999011^^^NLMINBIZA^NNNLD||van den Berg&&van den Berg&&^Maria^^^^^L~van den Berg&&van den Berg^Maria^^^^^B||19500101|F|||Keizersgracht 42&Keizersgracht&42^^Amsterdam^^1015CS^^M~Keizersgracht 42&Keizersgracht&42^^Amsterdam^^1015CS^^L||020-6234891^PRN^PH~^^^m.vandenberg@ziggo.nl|||M|||||||Nederlandse|Y|2||||""|N|N|||||||
OBX|1|ST|882-1^ABO+Rh group||O pos||||||F
PV1|1|I|0RGC2||||
OBR|1|123|20050701015070^Labosys||||200507010907||||||""|||3004^Brouwer||||200507010907||201708220955||S|F||^^^^^R
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

## 2. ORU^R01 - Diagnostic request with embedded PDF (cardiology referral form)

```
MSH|^_\&|ZorgDomein||||20160324163441+0100||ORU^R01|ZD200046119|P|2.4
PID|1||^^^NLMINBIZA^NNNLD||Jansen&Jansen&Jansen^W^P^^^^L||20000101|M|||Herengracht 88  bis&Herengracht&88^bis^Utrecht^^3511KP^NL^H||030-2314567
PV1|1|O
ORC|NW|ZD200046119|||||||20160324163432+0100|^&&het Verhoeven^D.E.F.||01004567^&&van Willems^H.J.^^^^^^VEKTIS||015-2222222
OBR|1|ZD200046119||CIS^Cardiologie^ZORGDOMEIN|||20160324163432+0100|||||||||01004567^&&van Willems^H.J.^^^^^^VEKTIS
OBX|1|NM|AF^^123||||||||F
OBX|2|ED|CARHAR^Hartfalen^ZORGDOMEIN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUH...||||||F
OBX|3|FT|CARCOA001^consult cardioloog^ZORGDOMEIN||||||||F
```

---

## 3. ORU^R01 - Referral letter with embedded PDF

```
MSH|^_\&|ZorgDomein||||20160324163509+0100||ORU^R01|ZD200046119|P|2.4
PID|1||^^^NLMINBIZA^NNNLD||Jansen&Jansen&Jansen^W^P^^^^L||20000101|M|||Herengracht 88  bis&Herengracht&88^bis^Utrecht^^3511KP^NL^H||030-2314567_^NET^Internet^w.jansen@kpnmail.nl
PV1|1|O
ORC|NW|ZD200046119|||||||20160324163432+0100|^&&het Verhoeven^D.E.F.||01004567^&&van Willems^H.J.^^^^^^VEKTIS||015-2222222
OBR|1|ZD200046119||CIS^Cardiologie^ZORGDOMEIN|||20160324163432+0100|||||||||01004567^&&van Willems^H.J.^^^^^^VEKTIS
OBX|1|NM|VB^^123||||||||F
OBX|2|ED|CARHAR^Hartfalen^ZORGDOMEIN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUH...||||||F
OBX|3|FT|CARCOA001^consult cardioloog^ZORGDOMEIN||||||||F
```

---

## 4. ORU^R01 - Attachment V2 with embedded Word document and PNG image

```
MSH|^_\&|ZorgDomein||||20160324163507+0100||ORU^R01|ZD200046119|P|2.4
PID|1||^^^NLMINBIZA^NNNLD||Jansen&Jansen&Jansen^W^P^^^^L||20000101|M|||Herengracht 88  bis&Herengracht&88^bis^Utrecht^^3511KP^NL^H||030-2314567
PV1|1|O
ORC|XO|ZD200046119|||||||20160324163432+0100|^&&het Verhoeven^D.E.F.||01004567^&&van Willems^H.J.^^^^^^VEKTIS||015-2222222
OBR|1|ZD200046119||CARCOA001^zorgproductcode^ZORGDOMEIN|||20160324163432+0100||||||Mijn toelichting op de bijlagen.|||01004567^&&van Willems^H.J.^^^^^^VEKTIS|||||||||F|||||||||||||||||||||^Overzicht van de bijlagen:\.br\De volgende bijlage(n) behorend bij de verwijzing met ZD200046119 is/zijn verzonden\.br\- HL7.doc\.br\- ZD\R\logo\R\kleur\R\RGB.png\.br\
OBX|1|ED|BLOB^Bijlage^ZORGDOMEIN|1|^application^msword^Base64^0M8R4KGxGuEAAAAAAAAAAAAAAAAAAAAAPgADAP7/CQAGAAAAAAAAAAAAAAABAAAALQAAAAAAAAAAEA...||||||F
NTE|1|P|HL7.doc|RE
OBX|2|ED|BLOB^Bijlage^ZORGDOMEIN|2|^image^png^Base64^iVBORw0KGgoAAAANSUhEUgAABJ0AAAOxCAYAAABfedaEAAAACXBIWXMAAC4jAAAuIwF4pT92AAAA...||||||F
NTE|2|P|ZD\R\logo\R\kleur\R\RGB.png|RE
```

---

## 5. OML^O21 - Lab order, clinical chemistry (diabetes/heart failure workup)

```
MSH|^~\&|ZorgDomein||||20210407153459+0200||OML^O21^OML_O21|23c517a5fc6a437cb05b|P|2.5.1|||||NLD|8859/1
NTE|1|P|KC en MMB|ZD_CLUSTER_NAME^ZorgDomein clusternaam^L
PID|1||287654321^^^NLMINBIZA^NNNLD~ZD234560029^^^ZorgDomein^VN||de Vries - van der Linden&van der Linden&van der Linden&de&Vries^A^M^^^^L||20000101|F|||Dorpsstraat 11 A&Dorpsstraat&11^A^Hilversum^^1211HR^NL^M~Molenweg 22 B&Molenweg&22^B^Hilversum^^1213NB^NL^H||06-23456789^ORN^CP~035-6218344^PRN^PH~^NET^Internet^a.devries@gmail.com||||||||||||||||||Y|NNNLD
PV1|1|O|||||||||||||||||||||||||||||||||||||||||||||||||V
PV2|||LABEDG001^klinische chemie en medische microbiologie onderzoek^L
IN1|1|^null|0102^^^VEKTIS^UZOVI|Menzis||||||||||||||||||||||||||||||||953513
ORC|NW|ZD234560029||ZD234560029|||^^^^^C||20210407153428+0200|^de Graaf^L.M.N.||01004567^van Houten^B.R.^^^^^^VEKTIS|^^^^^^^^Huisartsenpraktijk De Linde, locatie Hilversum^01012340&VEKTIS|0351234562^WPN^PH~0351234563^WPN^FX|||01012341^Huisartsenpraktijk De Linde^VEKTIS||||Huisartsenpraktijk De Linde^^01012341^^^VEKTIS|Stationsstraat 99 A&Stationsstraat&99^A^Hilversum^^1211EX^NL|0351234560^WPN^PH~0351234561^WPN^FX
TQ1|1||||||20210409000000+0200||C^Callback^HL70485||Aanvullende instructies voor materiaalafname
OBR|1|ZD234560029||LABEDG001^klinische chemie en medische microbiologie^L|||||||L|||||01004567^van Houten^B.R.^^^^^^VEKTIS|0351234562^WPN^PH~0351234563^WPN^FX|||||||||||01004568^Dijkstra^F.^^^^^^VEKTIS^^^^^^^Verpleeghuis Het Baken^^^^^Specialisme
OBX|1|ST|AI^opmerkingen / klinische gegevens^L||opmerking van verwijzer||||||F
ORC|NW|FUZDOMBUGYYDCMRV||ZD234560029|||^^^^^C||20210407153428+0200|^de Graaf^L.M.N.||01004567^van Houten^B.R.^^^^^^VEKTIS|^^^^^^^^Huisartsenpraktijk De Linde, locatie Hilversum^01012340&VEKTIS|0351234562^WPN^PH~0351234563^WPN^FX|||01012341^Huisartsenpraktijk De Linde^VEKTIS||||Huisartsenpraktijk De Linde^^01012341^^^VEKTIS|Stationsstraat 99 A&Stationsstraat&99^A^Hilversum^^1211EX^NL|0351234560^WPN^PH~0351234561^WPN^FX
OBR|2|FUZDOMBUGYYDCMRV||KC_DM2RI^Risico-inventarisatie^L|||||||L||Diabetes Mellitus type 2 (DM)|||01004567^van Houten^B.R.^^^^^^VEKTIS|0351234562^WPN^PH~0351234563^WPN^FX|||||||||||01004568^Dijkstra^F.^^^^^^VEKTIS^^^^^^^Verpleeghuis Het Baken^^^^^Specialisme
OBX|1|CE|REQUESTED_TESTS^Aangevraagde onderzoeken^L|1|ALB^Albumine^L||||||O
OBX|2|CE|REQUESTED_TESTS^Aangevraagde onderzoeken^L|2|MALB^Albumine (micro) urine portie^L||||||O
OBX|3|CE|REQUESTED_TESTS^Aangevraagde onderzoeken^L|3|KREA^Kreatinine (serum)^L||||||O
OBX|4|CE|REQUESTED_TESTS^Aangevraagde onderzoeken^L|4|K24^Lipidenspectrum (Chol, HDL.Tri,...)^L||||||O
```

---

## 6. OML^O21 - Lab order, medical microbiology (MRSA screening and respiratory infections)

```
MSH|^~\&|ZorgDomein||||20210407153459+0200||OML^O21^OML_O21|23c517a5fc6a437cb05a|P|2.5.1|||||NLD|8859/1
NTE|1|P|KC en MMB|ZD_CLUSTER_NAME^ZorgDomein clusternaam^L
PID|1||398765432^^^NLMINBIZA^NNNLD~ZD234560019^^^ZorgDomein^VN||Bakker - van Dijk&van Dijk&van Dijk&Bakker&Bakker^E^J^^^^L||20000101|F|||Laan van Meerdervoort 18 A&Laan van Meerdervoort&18^A^Den Haag^^2517AK^NL^M||06-87654321^ORN^CP~070-3456789^PRN^PH~^NET^Internet^e.bakker@hotmail.com||||||||||||||||||Y|NNNLD
PV1|1|O|||||||||||||||||||||||||||||||||||||||||||||||||V
PV2|||LABEDG001^klinische chemie en medische microbiologie^L
IN1|1|^null|0102^^^VEKTIS^UZOVI|CZ||||||||||||||||||||||||||||||||953513
ORC|NW|ZD234560019||ZD234560019|||^^^^^C||20210407153428+0200|^de Boer^G.H.I.||01004567^van Maanen^K.L.^^^^^^VEKTIS|^^^^^^^^Huisartsenpraktijk Duinzicht, locatie Scheveningen^01012340&VEKTIS|0701234562^WPN^PH~0701234563^WPN^FX|||01012341^Huisartsenpraktijk Duinzicht^VEKTIS||||Huisartsenpraktijk Duinzicht^^01012341^^^VEKTIS|Badhuisweg 99 A&Badhuisweg&99^A^Den Haag^^2587CA^NL|0701234560^WPN^PH~0701234561^WPN^FX
TQ1|1||||||||C^Callback^HL70485
OBR|1|ZD234560019||LABEDG001^klinische chemie en medische microbiologie^L||||||01004567^van Maanen^K.L.^^^^^^VEKTIS^^^^^^^&Huisartsenpraktijk Duinzicht, locatie Scheveningen|O|||||01004567^van Maanen^K.L.^^^^^^VEKTIS|0701234562^WPN^PH~0701234563^WPN^FX|||||||||||01004568^Meijer^T.^^^^^^VEKTIS^^^^^^^Verpleeghuis Duinrand^^^^^Specialisme
OBX|1|ST|AI^opmerkingen / klinische gegevens^L||opmerking van verwijzer||||||F
ORC|NW|GQ4TSNZTG4ZTSNT||ZD234560019|||^^^^^C||20210407153428+0200|^de Boer^G.H.I.||01004567^van Maanen^K.L.^^^^^^VEKTIS|^^^^^^^^Huisartsenpraktijk Duinzicht, locatie Scheveningen^01012340&VEKTIS|0701234562^WPN^PH~0701234563^WPN^FX|||01012341^Huisartsenpraktijk Duinzicht^VEKTIS||||Huisartsenpraktijk Duinzicht^^01012341^^^VEKTIS|Badhuisweg 99 A&Badhuisweg&99^A^Den Haag^^2587CA^NL|0701234560^WPN^PH~0701234561^WPN^FX
TQ1|1||||||||C^Callback^HL70485
OBR|2|GQ4TSNZTG4ZTSNT||MMB_LWI^Luchtweginfecties (MMB)^L||||||01004567^van Maanen^K.L.^^^^^^VEKTIS^^^^^^^&Huisartsenpraktijk Duinzicht, locatie Scheveningen|O||Microbiologisch onderzoek|||01004567^van Maanen^K.L.^^^^^^VEKTIS|0701234562^WPN^PH~0701234563^WPN^FX|||||||||||01004568^Meijer^T.^^^^^^VEKTIS^^^^^^^Verpleeghuis Duinrand^^^^^Specialisme
OBX|1|CE|REQUESTED_TESTS^Aangevraagde onderzoeken^L|1|BAN_KWK_SPT^Alg. bacterieel^L||||||O
OBX|2|CE|REQUESTED_TESTS^Aangevraagde onderzoeken^L|2|BRDPER_SER_BLD^Bordetella pertussis (kinkhoest)^L||||||O
OBX|3|CE|REQUESTED_TESTS^Aangevraagde onderzoeken^L|3|INFLRSV_PCR_SPT^Influenza A/B en RSV sputum^L||||||O
OBX|4|CE|REQUESTED_TESTS^Aangevraagde onderzoeken^L|4|RESP_PCR_SPT^Respiratoir pakket sputum (Influenza, RSV+breed pakket LWI verwekkers)^L||||||O
ORC|NW|FUYTMMBVGIYTMOJZHY||ZD234560019|||^^^^^C||20210407153428+0200|^de Boer^G.H.I.||01004567^van Maanen^K.L.^^^^^^VEKTIS|^^^^^^^^Huisartsenpraktijk Duinzicht, locatie Scheveningen^01012340&VEKTIS|0701234562^WPN^PH~0701234563^WPN^FX|||01012341^Huisartsenpraktijk Duinzicht^VEKTIS||||Huisartsenpraktijk Duinzicht^^01012341^^^VEKTIS|Badhuisweg 99 A&Badhuisweg&99^A^Den Haag^^2587CA^NL|0701234560^WPN^PH~0701234561^WPN^FX
TQ1|1||||||||C^Callback^HL70485
OBR|3|FUYTMMBVGIYTMOJZHY||MMB_MRSASCR^Meticilline resistente Staphylococcus aureus MRSA screening (MMB)^L||||||01004567^van Maanen^K.L.^^^^^^VEKTIS^^^^^^^&Huisartsenpraktijk Duinzicht, locatie Scheveningen|O||Microbiologisch onderzoek|||01004567^van Maanen^K.L.^^^^^^VEKTIS|0701234562^WPN^PH~0701234563^WPN^FX|||||||||||01004568^Meijer^T.^^^^^^VEKTIS^^^^^^^Verpleeghuis Duinrand^^^^^Specialisme
OBX|1|CE|REQUESTED_TESTS^Aangevraagde onderzoeken^L|1|MRSA_KWK_SWTASP^Methicilline Resistente Staphylococcus aureus - MRSA^L||||||O
OBX|2|CE|REQUESTED_TESTS^Aangevraagde onderzoeken^L|2|MRSA_KWK_SWNOSE^Methicilline Resistente Staphylococcus aureus - MRSA^L||||||O
OBX|3|CE|REQUESTED_TESTS^Aangevraagde onderzoeken^L|3|MRSA_KWK_SWPRNM^Methicilline Resistente Staphylococcus aureus - MRSA^L||||||O
```

---

## 7. OML^O21 - Lab order, deprecated LFDv2 format (calcium and hemoglobin)

```
MSH|^~\&|ZorgDomein||||20170215153459+0100||OML^O21^OML_O21|23c517a5fc6a437cb05a|P|2.5.1|||||NLD|8859/1
PID|1||456789123^^^NLMINBIZA^NNNLD~ZD200160319^^^ZorgDomein^VN||Mulder - van Leeuwen&van Leeuwen&van Leeuwen&Mulder&Mulder^C^H^^^^L||20000101|F|||Nieuwstraat 18 A&Nieuwstraat&18^A^Deventer^^7411LG^NL^M||06-98765432^ORN^CP~0570-612345^PRN^PH||||||||||||||||||Y|NNNLD
PV1|1|O|||||||||||||||||||||||||||||||||||||||||||||||||V
PV2|||LABEDG001^laboratorium onderzoek^99zda
IN1|1|^null|0102^^^VEKTIS^UZOVI|ONVZ||||||||||||||||||||||||||||||||953513
ORC|NW|ZD200160319_01BLD||ZD200160319|||||20170215153428+0100|^het Vermeer^P.Q.R.||01004567^van Beek^M.N.^^^^^^VEKTIS|^^^IO SWV huisartspraktijk 1&01058765^^^^^IO SWV huisartspraktijk 123||||01058765^IO SWV huisartspraktijk 1^VEKTIS||||IO SWV huisartspraktijk 1^^01058765^^^VEKTIS
TQ1|1||||||||R
OBR|1|ZD200160319_01BLD||CA01^Calcium^99zdl|||||||O|||||01004567^van Beek^M.N.^^^^^^VEKTIS
OBX|1|CE|Vraagcode^^99zda||Code1^Keuze1^99zda||||||F
OBX|2|CE|codeMultiselectVraag123^^99zdl||MultiC22^Multi2^99zdl~MultiC33^Multi3^99zdl||||||F
OBX|3|ST|AI^opmerkingen / klinische gegevens^99zda||opmerking van verwijzer||||||F
SPM|1|||BLD^Bloed^99zda
SAC|||CodeReageerbuis^Reageerbuis
ORC|NW|ZD200160319_02BLD||ZD200160319|||||20170215160258+0100|^het Vermeer^P.Q.R.||01004567^van Beek^M.N.^^^^^^VEKTIS|^^^IO SWV huisartspraktijk 1&01058765^^^^^IO SWV huisartspraktijk 123||||01058765^IO SWV huisartspraktijk 1^VEKTIS||||IO SWV huisartspraktijk 1^^01058765^^^VEKTIS
TQ1|2||||||||R
OBR|2|ZD200160319_02BLD||HE01^Hemoglobine^99zdl|||||||O|||||01004567^van Beek^M.N.^^^^^^VEKTIS
OBX|1|ST|AI^opmerkingen / klinische gegevens^99zda||opmerking van verwijzer||||||F
SPM|1|||BLD^Bloed^99zda
```
