# Mirth Connect (NextGen Healthcare) - real HL7v2 ER7 messages

## 1. ADT^A01 - Patientenaufnahme (Standard)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202612151705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/15|DEU^German^HL70296^^deutsch||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO
EVN||202612151705||||202612151645
PID|||2345678^^^Pappel-Klinik^PI||Kessler^Rösëmarie^^^^^L^A^^^G~Vogel^^^^^^M^A^^^G~Kessler^^^^Frau^^D^^^^G||19880903|F|||Taubenweg 3&Taubenweg&3^^Düsseldorf^^40210^^H~Rebgasse 14&Rebgasse&14^^Düsseldorf^^40210^^BDL||^PRN^PH^^49^211^3579246^^^^^0211/3579246|^WPN^PH^^49^211^8642^357^^^^0211/8642-357|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Sëbastians-Hospital|||DEU^German^HL70171^^deutsch
PV1|1|I|CHI^302^2^IN^^N^A^4|R|||950701^Groß^Bernhard^^^Dr.^^^Pappel-Klinik^L^^^DN^^^DN^^G||||||||||||4628^^^Pappel-Klinik^VN|||||||||||||||||||||||||202612151645
PV2|||||||||20250405|4
ZBE|7890^KIS|202612151705||INSERT
```

## 2. ADT^A01 - Patientenaufnahme DRG

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.39^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011705||||020604011645
PID|||87654^^^Pappel-Klinik^PI||Baumann^Ännëtte^^^^^L^A^^^G~Dreher^^^^^^M^A^^^G||19860128|F|||Taubenweg 3&Taubenweg&3^^Düsseldorf^^^^H~Rebgasse 14&Rebgasse&14^^Düsseldorf^^^^BDL||^PRN^PH^^49^211^3579246^^^^^0211/3579246|^WPN^PH^^49^211^8642^357^^^^0211/8642-357|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sëbastians-Hospital|||DEU^^HL70171
PV1|1|I|URO^301^1^IN^^N^A^4|R|||950703^Langer^Bernhard^^^Dr.^^^Pappel-Klinik^L^^^DN|950705^Huber^Haribert^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|4628^^^Pappel-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||0101^vollstationär, Normalfall^GSG0001||||||20260405|4||||||||||||||||||||||||||N|N
ZBE|7890^KIS|202604011705||INSERT
```

## 3. ADT^A01 - Patientenaufnahme Abrechnung

```
MSH|^~\&|KIS|ADT|RIS|ADT|202606051705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.40^^2.16.840.1.113883.2.6^ISO
EVN||202606051705||||020606051645
PID|||87654^^^Linden-Krankenhaus^PI||Arndt^Ëdmund^^^Dr.^^L^A^^^G~Arndt^Ëdmund^^^Herr Dr.^^D^A^^^G||19740506|F|||Burgweg 8&Burgweg&8^^Wuppertal^^42103^^H||^PRN^PH^^49^202^5794638^^^^^0202/5794638|^WPN^PH^^49^202^84175^^^^^0202/84175|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sëbastians-Hospital|||DEU^^HL70171
PV1|1|I|HNO^201^2^IN^^N^A^4|R|||950703^Langer^Bernhard^^^Dr.^^^Linden-Krankenhaus^L^^^^^^DN ||||||||||||952714^^^Linden-Krankenhaus^VN|01100000||||C|200301|||||||||||||||||||202606051645
PV2|||||||||20260615|10
ZBE|51627^KIS|202606051705||INSERT
```

## 4. ACK^A01 - Transportquittung

```
MSH|^~\&|RIS||KIS||202604011706||ACK^A01^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.9^^2.16.840.1.113883.2.6^ISO
SFT|RIS System GmbH^L|3.4|superRIS
MSA|CA|ADT001
```

## 5. ADT^A02 - Verlegung (Standard)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.44^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||87654^^^Pappel-Klinik^PI||Baumann^Ännëtte^^^^^L^A^^^G~Dreher^^^^^^M^A^^^G||19860128|F|||Taubenweg 3&Taubenweg&3^^Düsseldorf^^^^H~Rebgasse 14&Rebgasse&14^^Düsseldorf^^^^BDL||^PRN^PH^^49^211^3579246^^^^^0211/3579246|^WPN^PH^^49^211^8642^357^^^^0211/8642-357|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sëbastians-Hospital|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|950709^Langer^Bernhard^^^Dr.^^^Pappel-Klinik^L^^^DN||||||||||||4628^^^Pappel-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4
ZBE|4321^KIS|202604011935||INSERT
```

## 6. ADT^A03 - Entlassung (Standard)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.47^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202504011705||||202504011645
PID|||87654^^^Pappel-Klinik^PI||Baumann^Ännëtte^^^^^L^A^^^G~Dreher^^^^^^M^A^^^G||19860128|F|||Taubenweg 3&Taubenweg&3^^Düsseldorf^^^^H~Rebgasse 14&Rebgasse&14^^Düsseldorf^^^^BDL||^PRN^PH^^49^211^3579246^^^^^0211/3579246|^WPN^PH^^49^211^8642^357^^^^0211/8642-357|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Sëbastians-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||950707^Langer^Bernhard^^^Dr.^^^Pappel-Klinik^L^^^DN^^^DN ||||||||||||4628^^^Pappel-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
ZBE|7890^KIS|202504011705||REFERENCE
```

## 7. ADT^A03 - Entlassung DRG

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.48^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||87654^^^Pappel-Klinik^PI||vor dem Wald&vor dem&Wald^Sïegfrïed^^^^^L^A^^^G||19760324|M|||Taubenweg 3&Taubenweg&3^^Düsseldorf^^^^H~Rebgasse  14&Rebgasse&14^^Düsseldorf^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Sëbastians-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||4628^^^Pappel-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2|||0102^vollstationär, Arbeitsunfall^GSG0001|||||||4|4|||||||||||||||||||||||||N|N
ZBE|7890^KIS|202504011705||REFERENCE
```

## 8. ADT^A03 - Entlassung Abrechnung

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.49^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||87654^^^Pappel-Klinik^PI||vor dem Wald&vor dem&Wald^Sïegfrïed^^^^^L^A^^^G||19760324|M|||Taubenweg 3&Taubenweg&3^^Düsseldorf^^^^H~Rebgasse 14&Rebgasse&14^^Düsseldorf^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Sëbastians-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||4628^^^Pappel-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2||||||||||||||||||||||||||||||||||||N|N
ZBE|7890^KIS|202504011705||REFERENCE
```

## 9. ADT^A08 - Patient-Update (samedi HL7gateway, Mirth Connect)

```
MSH|^~\&|samedi-hl7gateway|samedi|APPLICATION|CLINIC|20260403151846+0200||ADT^A08^ADT_A01|224998048387918585|P|2.5||||||UNICODE UTF-8
EVN|A08|202604031516+0200
PID|1|87654|vfë1eei5e32^^^&www.praxis-süd2.de&DNS^PI~87654^^^^PT||Ebert^Öskar^^^Prof.||20000416|M|||Straßënpfad 6^^Dörfchen^^32100^DE||+49155 999 87654^^CP^^^^^^^^^+49155 999 87654~+49 211 999 654^^PH^^^^^^^^^+49 211 999 654~ëmail@versüch.örg^NET^X.400^ëmail@versüch.örg
PV1|1|U
```

## 10. ADT^A08 - Eingehende Patientenaktualisierung (KIS to samedi)

```
MSH|^~\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A08|4971514499870|P|2.5|CJ17H17L3JL226G||AL|NE||8859/1
EVN|A08|202610260719
PID|1||7899^^^&www.praxis-süd2.de&DNS^PI~510366^^^Rädvis^PI|50000130^^^HBG^PI|Gerber^Hëlëne||19530813|F|||Prüfgässchen 19&Prüfgässchen 19^^Wülfrath^^42489^DE^L||^^PH^^^^02058-8765432 Büro|^^PH
```

## 11. ADT^A40 - Patientenzusammenführung (Merge)

```
MSH|^~\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A40|4971514499870|P|2.5|CJ17H17L3JL226G||AL|NE||8859/1
EVN|A40|202502041715
PID|1||7899^^^&www.praxis-süd2.de&DNS^PI~510366^^^Rädvis^PI|50000130^^^HBG^PI|Gerber^Hëlëne||19530813|F|||Prüfgässchen 19&Prüfgässchen 19^^Wülfrath^^42489^DE^L||^^PH^^^^02058-8765432 Büro|^^PH
MRG|7890~a596623ij24^^^&www.praxis-süd2.de&DNS~7790711^^^&1.2.276.0.76.3.1.660.1.1.1.2.1&ISO^PI|
```

## 12. ORU^R01 - Klinische Beobachtungsergebnisse (DETECT, Universitätsklinikum Dresden)

```
MSH|^~\&|COPRAdetectapi|001|detectserver||||ORU^R01||P|2.5|||AL|NE|DE|8859/1|||2.16.840.1.113883.2.6.9.1
PID|1|7890||65432198
PV1|1||SC110|
OBX|1|NM|RASS||-4|||||||||202601010600
OBX|2|ST|PupilleLinks||e+k|||||||||202612301330
OBX|3|ST|PupilleRechts||e+k|||||||||202601010600
```

## 13. MDM^T02 - Dokumentenübermittlung

```
MSH|^~\&|system|clinic|hl7gateway|samedi|2026082011223344||MDM^T02^MDM_T02|16|P|2.5|||NE|AL||||
EVN|T02|2026082011223344||||
PID|1||pät654321||Lindner^Lëonhard||19800703|M
PV1|1|I|
TXA|1|samediDefaultType|AP|20260801120000||20260802120000|20260803120000|||||döc8912564||||ëndname.pdf|AU||AV||||||Dökument Überschrift
OBX|1|ED|||^application/pdf^^Base64^aGVsbG8gd29ybGQ=
```

## 14. SIU^S12 - Neuer Termin (samedi HL7gateway)

```
MSH|^~\&|samedi-hl7gateway|samedi|system|clinic|20260207130859+0100||SIU^S12^SIU_S12|9948948508708113731|P|2.5||||||UNICODE UTF-8
SCH||d-fsdem8jyufhigb6y||||BOOKED||1^MRT|1800||^^M30^20260516130000+0200^20260516133000+0200||||||||||||||Booked
TQ1|1||||||20260516130000+0200|20260516133000+0200|||||30^min
NTE||_default|Comment
NTE||Affected body parts|arm~left leg~head
NTE||Kommentar zum Patienten|patient comment, patient without external patient number
PID|1||w3300fg6126^^^&www.praxis-süd2.de&DNS^PI~^^^^PT||Koch^Thorsten||19850727|M|||Bahnhofstrasse 12^^Berlin^^12345^DE||+49 171 1234567^^CP^^^^^^^^^+49 171 1234567~+49 89 12345-678^^PH^^^^^^^^^+49 89 12345-678~mail@example.org^NET^X.400^mail@example.org~+49 89 12345-679^^FX^^^^^^^^^+49 89 12345-679
RGS|1|A
AIG|1|A|2^Thomas Brandt^99SAMEDI-RESOURCE^radiologist|||||20260516130000+0200|||1800|s
AIG|2|A|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516130000+0200|||1800|s
```

## 15. SIU^S13 - Terminverschiebung

```
MSH|^~\&|samedi-hl7gateway|samedi|system|clinic|20260207131000+0100||SIU^S13^SIU_S12|11199607447739267382|P|2.5||||||UNICODE UTF-8
SCH||d-fsdem8jyufhigb6y||||BOOKED||^Test|1800||^^M30^20260410135000+0200^20260410142000+0200||||||||||||||Booked
TQ1|1||||||20260410135000+0200|20260410142000+0200|||||30^min
RGS|1|D
AIG|1|D|1^Sprechzimmer^99SAMEDI-RESOURCE^c2|||||20260410125500+0200|||1800|s
RGS|2|A
AIG|2|A|2^Doc^99SAMEDI-RESOURCE^c1|||||20260410135000+0200|||1800|s
```

## 16. SIU^S15 - Terminabsage

```
MSH|^~\&|samedi-hl7gateway|samedi|system|clinic|20260207131507+0100||SIU^S15^SIU_S12|6263450610539110790|P|2.5||||||UNICODE UTF-8
SCH||d-fsdem8jyufhigb6y||||BOOKED||1^MRT|1800||^^M30^20260516140000+0200^20260516143000+0200||||||||||||||Deleted
TQ1|1||||||20260516140000+0200|20260516143000+0200|||||30^min
NTE||_default|updated comment
NTE||Kommentar zum Patienten|patient comment, patient without external patient number
PID|1||w3300fg6126^^^&www.praxis-süd2.de&DNS^PI~^^^^PT||Koch^Thorsten||19850727|M
RGS|1|D
AIG|1|D|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516140000+0200|||1800|s
```

## 17. ADT^A01 - Mirth Connect AWS reference (Mirth Healthcare Hub)

```
MSH|^~\&|SOURCEEHR|HH|MIRTHDST|HH|202611111111||ADT^A01|MSGID20002|P|2.3|
EVN|A01|202611111111||
PID|1|100001^^^1^MRN1|900001||SCHMIDT^THOMAS^^^^||19720123|M||WH|DEICHSTR 14^^HAMBURG^HH^20095^DEU||(040)555-5309|||M|NON|888888888|
NK1|1|SCHMIDT^ANNA^|WIFE||(040)555-5555||||NK^NEXT OF KIN
PV1|1|O|2002^3003^02||||234567^WAGNER^PETER^R^^DR|||||||ADM|A0|
```

## 18. ADT^A01 - Mirth Connect blog (Unofficial Mirth Admin Guide)

```
MSH|^~\&|hmis|1|||20260110045504||ADT^A01|700213|P|2.3|||
EVN|A01|20260110045502|||||
PID|1||20007681^^^1^MRN^1||BRAUN^HEINRICH^H||19340812|M||1|MAINZER LANDSTR 22^^FRANKFURT^HE^60311^DEU^^M|1|0691662323|0691662323|1|2||50008827^^^AccMgr^VN^1|234232345|||||||||||NO
NK1|1|BRAUN^FRIEDRICH|SO|MAINZER LANDSTR 22^^FRANKFURT^HE^60311^DEU|0691663434||Y||||||||||||||
PV1|1|I|PREOP^101^1^1^^^S|3|||48^KLEIN^MICHAEL^^^^^^AccMgr^^^^CI|||01||||1|||48^KLEIN^MICHAEL^^^^^^AccMgr^^^^CI|2|50008827^^^AccMgr^VN|4|||||||||||||||||||1||G|||20260110045253||||||
GT1|1|8291|BRAUN^HEINRICH^H||MAINZER LANDSTR 22^^FRANKFURT^HE^60311^DEU|0691662323||19340812|M||1|234232345||||#Rhein-Main GmbH|MAINZER LANDSTR 22^^FRANKFURT^HE^60311^DEU|0691662323||PT|
DG1|1|I9|71596^OSTEOARTHROS NOS-L/LEG ^I9|OSTEOARTHROS NOS-L/LEG ||A|
IN1|1|AOK|3|AOK|||||||Rhein-Main GmbH|19990804|||4|BRAUN^HEINRICH^H|1|19340812|MAINZER LANDSTR 22^^FRANKFURT^HE^60311^DEU|||||||||||||||||234232345A||||||PT|M|MAINZER LANDSTR 22^^FRANKFURT^HE^60311^DEU|||||8291
IN2|1||234232345|Rhein-Main GmbH|||234232345A|||||||||||||||||||||||||||||||||||||||||||||||||||||||||0691662323
```

## 19. ADT^A02 - Verlegung (Mirth Connect blog)

```
MSH|^~\&|hmis|1|||20260110114442||ADT^A02|70021398|P|2.3|||
EVN|A02|20260110114442|||||
PID|1||20007681^^^1^MRN^1||BRAUN^HEINRICH^H||19340812|M||1|MAINZER LANDSTR 22^^FRANKFURT^HE^60311^DEU^^M|1|0691662323|0691662323|1|2||50008827^^^AccMgr^VN^1|234232345|||||||||||NO
PV1|1|I|IN1^214^1^1^^^S|3||PREOP^101^|48^KLEIN^MICHAEL^^^^^^AccMgr^^^^CI|||01||||1|||48^KLEIN^MICHAEL^^^^^^AccMgr^^^^CI|2|50008827^^^AccMgr^VN|4|||||||||||||||||||1||I|||20260110045253||||||
```

## 20. ADT^A03 - Entlassung (Mirth Connect blog)

```
MSH|^~\&|AccMgr|1|||20260112154645||ADT^A03|70023526|P|2.3|||
EVN|A03|20260112154642|||||
PID|1||20007681^^^1^MRN^1||BRAUN^HEINRICH^H||19340812|M||1|MAINZER LANDSTR 22^^FRANKFURT^HE^60311^DEU^^M|1|0691662323|0691662323|1|2||50008827^^^AccMgr^VN^1|234232345|||||||||||NO
PV1|1|I|IN1^214^1^1^^^S|3||IN1^214^1|48^KLEIN^MICHAEL^^^^^^AccMgr^^^^CI|||01||||1|||48^KLEIN^MICHAEL^^^^^^AccMgr^^^^CI|2|50008827^^^AccMgr^VN|4||||||||||||||||1|||1||P|||20260110045253|20260112152000|3115.89|3115.89|||
```
