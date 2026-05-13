# NEXUS / Nederland - real HL7v2 ER7 messages

## 1. ZorgDomein ORU^R01 - referral letter with embedded PDF (base64)

```
MSH|^_\&|ZorgDomein||||20160324163509+0100||ORU^R01|ZD200046119|P|2.4
PID|1||^^^NLMINBIZA^NNNLD||van Dijk&van&Dijk^J^M^^^^L||20000101|M|||Herengracht 88  hs&Herengracht&88^hs^Amsterdam^^1015BN^NL^H||020-6234871_^NET^Internet^j.vandijk@gmail.nl
PV1|1|O
ORC|NW|ZD200046119|||||||20160324163432+0100|^&&het Wolters^F.G.||01004567^&&van Brouwer^Z.Z.^^^^^^VEKTIS||015-2222222
OBR|1|ZD200046119||CIS^Cardiologie^ZORGDOMEIN|||20160324163432+0100|||||||||01004567^&&van Brouwer^Z.Z.^^^^^^VEKTIS
OBX|1|NM|VB^^123||||||||F
OBX|2|ED|CARHAR^Hartfalen^ZORGDOMEIN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAgADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzUwOCswMScwMCcpCj4+||||||F
OBX|3|FT|CARCOA001^consult cardioloog^ZORGDOMEIN||||||||F
```

---

## 2. ZorgDomein ORU^R01 - diagnostic request with embedded PDF (base64)

```
MSH|^_\&|ZorgDomein||||20160324163441+0100||ORU^R01|ZD200046119|P|2.4
PID|1||^^^NLMINBIZA^NNNLD||Bakker&Bakker^A^H^^^^L||19850722|F|||Keizersgracht 312  II&Keizersgracht&312^II^Utrecht^^3511EX^NL^H||030-2519843
PV1|1|O
ORC|NW|ZD200046119|||||||20160324163432+0100|^&&het Timmerman^R.S.||01004567^&&van Meijer^P.A.^^^^^^VEKTIS||015-2222222
OBR|1|ZD200046119||CIS^Cardiologie^ZORGDOMEIN|||20160324163432+0100|||||||||01004567^&&van Meijer^P.A.^^^^^^VEKTIS
OBX|1|NM|AF^^123||||||||F
OBX|2|ED|CARHAR^Hartfalen^ZORGDOMEIN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAgADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzQ0MSswMScwMCcpCj4+||||||F
OBX|3|FT|CARCOA001^consult cardioloog^ZORGDOMEIN||||||||F
```

---

## 3. German ADT^A01 - patient admission (Aufnahme)

```
MSH|^~\&|SUBx||PAT||20040328112408||ADT^A01^ADT_A01|47|P|2.5|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.1^^2.16.840.1.113883.2.6^ISO
EVN||20040328112408
PID|1||12345^^^YKIS^PI||de Jong^Willem^^^^^L^A^^^G||19610527|M|||Prinsengracht 78&Prinsengracht&78^^Amsterdam^XA-DE-NW^1017KT^NLD^H||^PRN^PH^^31^20^6234567^^^^^020/6234567|^WPN^PH^^31^20^7654321^^^^^020/7654321|NLD^^HL70296|M^married^HL70002|CAT^^HL70006
PV1|1|I|INN^305^1^Erasmus MC^^N||||A1234^Visser^Adriaan|||MED||||N||||||0815^^^Erasmus MC^VN|||||||||||||||||000000|||||||||20040328112400
```

---

## 4. German ADT^A05 - pre-admission (Voraufnahme)

```
MSH|^~\&|KIS|ADT|RIS|ADT|200404011935||ADT^A05^ADT_A05|ADT002|P|2.5^DEU|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.42^^2.16.840.1.113883.2.6^ISO
EVN||200404011935||||200404011645
PID|1||12345^^^Radboudumc^PI||Jansen^Femke^^^^^L^A^^^G||19770325|F|||Mariaplaats 14&Mariaplaats&14^^Utrecht^^^^H~Oudegracht 17&Oudegracht&17^^Utrecht^^^^BDL||^PRN^PH^^31^30^2345678^^^^^030/2345678|^WPN^PH^^31^30^8765432^^^^^030/8765432|NLD^^HL70296|M^married^HL70002|CAT^^HL70006||||||Radboudumc|||NLD^^HL70171
PV1|1|I|||||||||||||||||4711^^^Radboudumc^VN|||||||||||||||||||||||||200404011654
```

---

## 5. German ADT^A38 - cancel pre-admission (Stornierung Voraufnahme)

```
MSH|^~\&|KIS|ADT|RIS|ADT|200404011935||ADT^A38^ADT_A38|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.43^^2.16.840.1.113883.2.6^ISO
EVN||200404011935||||200404011645
PID|1||12345^^^OLVG^PI||Mulder^Theodora^^^^^L^A^^^G||19820914|F|||Westerstraat 55&Westerstraat&55^^Rotterdam^^^^H~Coolsingel 103&Coolsingel&103^^Rotterdam^^^^BDL||^PRN^PH^^31^10^4567890^^^^^010/4567890|^WPN^PH^^31^10^9876543^^^^^010/9876543|NLD^^HL70296|M^married^HL70002|CAT^^HL70006||||||OLVG|||NLD^^HL70171
PV1|1|P|||||||||||||||||0815^^^OLVG^VN|||||||||||||||||||||||||200404011645
```

---

## 6. German BAR^P12 - diagnosis update with ICD-10 codes

```
MSH|^~\&|KIS|ADT|LAB|ADT|200510141345||BAR^P12^BAR_P12|ADT03|P|2.5^DEU&&HL70399|||AL|NE||8859/1|||2.16.840.1.113883.2.6.9.66^^2.16.840.1.113883.2.6^ISO
EVN||200510141345
PID|||943246^^^KIS^PI||Dekker^Jacobus^^^^^L||19480403|M|||Vondelstraat 4&Vondelstraat&4^^Den Haag^XA-DE-BY^2513AC^NLD^H
PV1||I|CHI^202^2^CH^^N||||||||||||||||654325^^^KIS^VN||||||||||||||||000000|||||||||200510091820
ZBE|234345^KIS|200510121230||REFERENCE
DG1|1||K35.-^Akute Appendizitis^I10-2005||200510141345|ED|||||||||1.1|432113^^^^^^^^^^^^DN||||23543^KIS|A
DG1|2||K35.-^Akute Appendizitis^I10-2005||200510141345|AD|||||||||1.2|432113^^^^^^^^^^^^DN||||23544^KIS|A
DG1|3||K35.0^Akute Appendizitis mit diffuser Peritonitis^I10-2005||200510141345|BD|||||||||1.2|432113^^^^^^^^^^^^DN||||23545^KIS|A
```

---

## 7. German BAR^P12 - procedure update with SFT segment and OPS codes

```
MSH|^~\&|KIS|ADT|LAB|ADT|200510141345||BAR^P12^BAR_P12|ADT03|P|2.5^DEU&&HL70399|||AL|NE||8859/1|||2.16.840.1.113883.2.6.9.66^^2.16.840.1.113883.2.6^ISO
SFT|KIS Hersteller GmbH^L|5.4.0|KIS System A
EVN||200510141345
PID|||943246^^^KIS^PI||Bos^Hendrik^^^^^L||19530817|M|||Laan van Meerdervoort 92&Laan van Meerdervoort&92^^Den Haag^XA-DE-BY^2517AR^NLD^H
PV1|1|I|CHI^202^2^CH^^N||||||||||||||||654325^^^KIS^VN|||||||||||||||||||||||||2005100510
ZBE|345345|20051013||REFERENCE
PR1|1||8-901^Inhalationsanästhesie^O301-2005||200510141415||120|||||||1|||||34325^KIS|A
PR1|2||5-470.0^Appendektomie, offen chirurgisch^O301-2005||200510141415||90|||||||2|||||34326^KIS|A
```

---

## 8. German BAR^P12 - combined diagnosis and procedure update

```
MSH|^~\&|KIS|ADT|LAB|ADT|200510141345||BAR^P12^BAR_P12|ADT03|P|2.5^DEU&&HL70399|||AL|NE||8859/1|||2.16.840.1.113883.2.6.9.66^^2.16.840.1.113883.2.6^ISO
EVN||200510141345
PID|||943246^^^KIS^PI||Smit^Geert^^^^^L||19590212|M|||Nassaulaan 28&Nassaulaan&28^^Eindhoven^XA-DE-BY^5611AA^NLD^H
PV1||I|CHI^202^2^CH^^N||||||||||||||||654325^^^KIS^VN
ZBE|234345^KIS|200510121230||REFERENCE
DG1|1||N26 L V^Verdacht auf Schrumpfniere links^I10-2005||200510141345|AD|||||||||1|432113^^^^^^^^^^^^DN||||23542134^KIS|A
PR1|1||8-901^Inhalationsanästhesie^O301-2004||200510141415||120||||||||||||34325^KIS|A
PR1|2||5-470.0^Appendektomie, offen chirurgisch^O301-2004||200510141415||90||||||||||||34326^KIS|A
```

---

## 9. Nictiz Lab2Lab - antimicrobial susceptibility OBX results

```
MSH|^~\&|LAB_SRC|LABFACILITY|LAB_DST|LABFACILITY|20180201120000||ORU^R01^ORU_R01|LAB00042|P|2.5.1|||AL|NE|NLD|8859/1
PID|1||298471536^^^NLMINBIZA^NNNLD||Visser^Maria^^^^^L||19650415|F|||Oudegracht 45^^Utrecht^^3511AB^NL^H
PV1|1|O
ORC|RE|ORD5678^LAB_SRC|FIL9012^LAB_DST||CM
OBR|1|ORD5678^LAB_SRC|FIL9012^LAB_DST|630-4^Bacteria identified^LN|||20180201090000
OBX|1|ST|6652-2^Meropenem [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||>=16|mg/L||null|||F
OBX|2|ST|7029-2^Meropenem [Susceptibility] by Gradient strip^LN||8,0|mg/L||null|||F
OBX|3||18943-1^Meropenem [Susceptibility]^LN|||||R|||F
```

---

## 10. HL7 v2.5.1 ADT^A01 - hospital admission with insurance (IHE PAM profile)

```
MSH|^~\&|EPIC|ISALA|LAB_SYS|PATHOLOGY|202603011430||ADT^A01^ADT_A01|MSG00001|P|2.5.1|||AL|NE
EVN|A01|202603011430|||ADMIN^Bakker^Elisabeth^^^RN
PID|1||MRN12345^^^ISALA^MR||van den Berg^Daan^Willem||19800115|M||2106-3^White^HL70005|Stationsweg 23^^Zwolle^OV^8011CW^NLD
PV1|1|I|ICU^0101^01^ISALA^^^^NURS|E|||ATT1234^Timmerman^Floor^^^MD|||MED||||N||||||0815^^^ISALA^VN|||||||||||||||||000000|||||||||202603011430
IN1|1|ZK001^Zilveren Kruis|ZK|Zilveren Kruis Achmea||||||||||||van den Berg^Daan||19800115|Stationsweg 23^^Zwolle^OV^8011CW|||||||||||||||||ZK87654321
```

---

## 11. HL7 v2.5.1 ORM^O01 - lab order (CMP panel)

```
MSH|^~\&|EPIC|AMPHIA|LAB_SYS|PATHOLOGY|202603011400||ORM^O01^ORM_O01|ORD00123|P|2.5.1|||AL|NE
PID|1||MRN67890^^^AMPHIA^MR||Wolters^Anneke^Margaretha||19751208|F
PV1|1|I|ICU^0201^01^AMPHIA||||ATT5678^de Vries^Pieter^^^MD
ORC|NW|ORD5678^EPIC||||||||||ATT5678^de Vries^Pieter^^^MD
OBR|1|ORD5678^EPIC|FIL9012^LAB_SYS|24323-8^CMP^LN|||202603011400||||||||ATT5678^de Vries^Pieter^^^MD
```

---

## 12. HL7 v2.5.1 ORU^R01 - lab results (glucose, creatinine)

```
MSH|^~\&|LAB_SYS|RIJNSTATE|EPIC|RIJNSTATE|202603011630||ORU^R01^ORU_R01|LAB00042|P|2.5.1|||AL|NE
PID|1||MRN34567^^^RIJNSTATE^MR||Brouwer^Thijs^Jan||19690304|M
PV1|1|I|ICU^0101^01^RIJNSTATE
ORC|RE|ORD5678^EPIC|FIL9012^LAB_SYS||CM
OBR|1|ORD5678^EPIC|FIL9012^LAB_SYS|24323-8^CMP^LN|||202603011445
OBX|1|NM|2345-7^Glucose^LN||98|mg/dL|70-100|N|||F
OBX|2|NM|2160-0^Creatinine^LN||1.1|mg/dL|0.6-1.2|N|||F
```

---

## 13. SIU^S12 - scheduling new appointment booking

```
MSH|^~\&|WCDataSend|handle|wc_hl7d|recv_facil|20210423091057||SIU^S12^SIU_S12|DSD1619205057152978|P|2.5
SCH|2588939|2677255|||||ppd 2nd step|NURS^Nurse Encounter|15|MIN|^^^202104270815^202104270830||||||||||||||BOOKED
PID|1|745832|745832^^^MR&1.2.840.114398.1.5881.2&ISO^MR^1.2.840.114398.1.5881.2&MR&ISO~963258^^^ECW&1.2.840.114398.1.5881.3&ISO^MR^1.2.840.114398.1.5881.3&ECW&ISO~192837465^^^^SS|745832^^^MR&1.2.840.114398.1.5881.1&ISO|de Groot^Saskia^L||19830711000000|F||Asian|Dorpsstraat 17^^Leiden^ZH^2311EA^NL||071-5234567^PRN^PH^s.degroot@email.nl~071-5234568^PRN^CP|071-5234569^WPN^PH|NL|M|||192837465|||Not Hispanic or Latino
PV1|1||^^^handle
RGS|1||
AIL|1||^30^^^^^^^LUMC Polikliniek|||||||||
AIP|1||29384756^van der Linden^Johanna^M^^^MD|RESOURCE|||||||SUBSTITUTE|
```

---

## 14. M-ware ESB ADT^A01 - admission notification (ER7 format)

```
MSH|^~\&|sendingSystemA|senderFacilityA|receivingSystemB|receivingFacilityB|20080925161613||ADT^A01|589888ADT30502184808|P|2.3
EVN|A01|20080925161613
PID|1||MRN900001^^^VUMC^MR||van Dijk^Bram^H||19500101|M|||Kloveniersburgwal 29^^Amsterdam^NH^1011JV^NLD||020-6345678|020-6345679||S|CAT|283746192
PV1|1|I|W^389^1^VUMC||||ATT7654^Mulder^Cornelia||||||ADM||||||VN123456^^^VUMC^VN|||||||||||||||||||||||||20080925161600
```

---

## 15. Microsoft Azure ADT^A01 - hospital admission (FHIR conversion sample)

```
MSH|^~\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII
EVN|A01|20200508130643||ADT_EVENT|C006^Dekker^Lotte^^^Dr^^^DRNBR^PRSNL^^^ORGDR|
PID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||Meijer^Floor^^^Mevr.^^CURRENT||19781020000000|F|||Singel 140^^Amsterdam^NH^1015AE^NL||(020)5551003^^^f.meijer@email.nl||NL|M|CAT|||||A|||||||N
PV1|1|I|WARD^ROOM01^BED01^SFAC||||C006^Dekker^Lotte^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||VIS123456789^^^SFAC^VISITID||||||||||||||||||SF|||||20200508130643
PV2|||Acute MI^Acute Myocardial Infarction^ICD10||||||20200508130643||1|||||||||||||||||||||||||N
OBX|1|NM|0002-4182^Body Weight^LN||78|kg|||||F
DG1|1||I21.9^Acute MI^ICD10|||AD
ZMP|1|20200508130643||PHR-PORTAL
```

---

## 16. HL7 v2.3 ORU^R01 - retinal screening with embedded JPEG image (base64)

```
MSH|^~\&|RS|RetinalScreenings|EMR|CLINIC|20210315143000||ORU^R01|RS20210315001|P|2.3
PID|1||PAT123456^^^CLINIC^MR||Janssen^Margaretha^A||19750820|F|||Nieuwstraat 8^^Nijmegen^GE^6511PP^NL||(024)3561234
PV1|1|O
ORC|RE|ORD789^EMR|FIL456^RS||CM
OBR|1|ORD789^EMR|FIL456^RS|71020^Retinal Image^CPT|||20210315140000||||||||ORD_PROV^Smeets^Adriaan^^^MD
OBX|1|CE|ASSESS^Assessment^RS||NO_DR^No Diabetic Retinopathy^RS||||||F
OBX|2|ED|IMG_OD^Right Eye Image^RS||^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkS||||||F
OBX|3|ED|IMG_OS^Left Eye Image^RS||^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkS||||||F
OBX|4|FT|NOTES^Clinical Notes^RS||Bilateral retinal exam performed. No signs of diabetic retinopathy.||||||F
```

---

## 17. French ANS ORU^R01 - CDA-R2 document transmission (European IHE profile)

```
MSH|^~\&|SRC_APP|SRC_FAC|DST_APP|DST_FAC|20230615120000||ORU^R01^ORU_R01|MSG0001|P|2.5^FRA^2.5||||||UNICODE UTF-8|||1.3.6.1.4.1.21367.2017.2.6.4^^2.16.840.1.113883.2.8.3.6^ISO
PID|1||374829156^^^ASIP^INS-NIR||van der Meer^Elisabeth^^^^^L||19700101|F|||Markt 10^^Groningen^^9711CV^NLD^H
PV1|1|N
OBR|1||ORD123^SRC_APP|11502-2^Laboratory report^LN
OBX|1|ED|11502-2^Laboratory report^LN||^text^xml^Base64^PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIj4=||||||F
```

---

## 18. Dutch ACK - acknowledgment response

```
MSH|^~\&|PAT||SUBx||20040328112410||ACK^A01^ACK|48|P|2.5|||NE|NE|DEU|8859/1|DEU^^HL70296
MSA|AA|47
```

---

## 19. HL7 v2.5 ADT^A08 - patient update (German/IHE PAM structure)

```
MSH|^~\&|KIS|KLINIKUM|RIS|RADIOLOGIE|200611151030||ADT^A08^ADT_A01|MSG99001|P|2.5^DEU|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO
EVN||200611151030||||200611151025
PID|1||78901^^^KLINIKUM^PI||de Vries^Johanna^^^^^L^A^^^G||19550612|F|||Haarlemmerstraat 42&Haarlemmerstraat&42^^Leiden^XA-DE-BE^2312DH^NLD^H||^PRN^PH^^31^71^5123456^^^^^071/5123456
PV1|1|I|CHI^101^1^KLINIKUM^^N||||A2345^Vermeulen^Adriaan^^^Dr.|||CHI||||N||||||99887^^^KLINIKUM^VN|||||||||||||||||||||||||200611151025
IN1|1||109905003|CZ Zorgverzekeringen|||||||||||||||||||||||||||||||||||||||109000018
IN2||78901
```

---

## 20. HL7 v2.5.1 OML^O21 - ZorgDomein lab diagnostic request (NL OML V3)

```
MSH|^~\&|ZorgDomein||LabSysteem|Ziekenhuis|20230915143022+0200||OML^O21^OML_O21|ZD300056789|P|2.5.1|||AL|NE|NLD|8859/1
NTE|1|P|Cluster Laboratorium|ZD_CLUSTER_NAME^ZorgDomein clusternaam^L
PID|1||163895247^^^NLMINBIZA^NNNLD||Timmerman&Timmerman^L^F^^^^L||19850215|F|||Reguliersgracht 12^^Amsterdam^^1017LV^NL^H||020-7891234^PRN^PH
PV1|1|O
PV2|||Bloedonderzoek|||||||||||||||||||||||||
IN1|1||0412^VGZ
ORC|NW|ZD300056789|||||||20230915142500+0200|^&&van Hoekstra^C.||01009876^&&van der Berg^P.J.^^^^^^VEKTIS||010-5559876
TQ1|||||||20230918083000+0200|20230918120000+0200
OBR|1|ZD300056789||CHEMIE^Klinische Chemie^ZORGDOMEIN|||20230915142500+0200|||||||||01009876^&&van der Berg^P.J.^^^^^^VEKTIS
OBX|1|ST|GLUCOSE^Glucose (nuchter)^ZORGDOMEIN||Aangevraagd||||||O
OBX|2|ST|HBA1C^HbA1c^ZORGDOMEIN||Aangevraagd||||||O
OBX|3|ST|TSH^TSH^ZORGDOMEIN||Aangevraagd||||||O
```
