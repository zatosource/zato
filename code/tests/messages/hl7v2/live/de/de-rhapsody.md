# Rhapsody (Rhapsody Health) - real HL7v2 ER7 messages

---

## 1. ADT A01 - standard admission (Standardnachricht Aufnahme)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme - HL7 Deutschland ADT Admission Profile v01, December 2013 -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202612151705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/15|DEU^German^HL70296^^deutsch||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO
EVN||202612151705||||202612151645
PID|||6789012^^^Holunder-Klinik^PI||Spëcht^Gërtrud^^^^^L^A^^^G~Eichhorn^^^^^^M^A^^^G~Spëcht^^^^Frau^^D^^^^G||19910818|F|||Amselweg 21&Amselweg&21^^Rostock^^18055^^H~Finkenstr. 4&Finkenstr.&4^^Rostock^^18055^^BDL||^PRN^PH^^49^381^2468901^^^^^0381/2468901|^WPN^PH^^49^381^7913^802^^^^0381/7913-802|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Jösëfs-Hospital|||DEU^German^HL70171^^deutsch
PV1|1|I|CHI^302^2^IN^^N^A^4|R|||381001^Groß^Bernhard^^^Dr.^^^Holunder-Klinik^L^^^DN^^^DN^^G||||||||||||1739^^^Holunder-Klinik^VN|||||||||||||||||||||||||202612151645
PV2|||||||||20250405|4
ZBE|0123^KIS|202612151705||INSERT
```

## 2. ADT A01 - admission for DRG (Aufnahme für DRG-Übermittlung)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme - HL7 Deutschland ADT Admission Profile, DRG example -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.39^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011705||||022604011645
PID|||21098^^^Holunder-Klinik^PI||Reinhardt^Ännëliëse^^^^^L^A^^^G~Rëhbëin^^^^^^M^A^^^G||19890512|F|||Amselweg 21&Amselweg&21^^Rostock^^^^H~Finkenstr. 4&Finkenstr.&4^^Rostock^^^^BDL||^PRN^PH^^49^381^2468901^^^^^0381/2468901|^WPN^PH^^49^381^7913^802^^^^0381/7913-802|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Jösëfs-Hospital|||DEU^^HL70171
PV1|1|I|URO^301^1^IN^^N^A^4|R|||381003^Langer^Bernhard^^^Dr.^^^Holunder-Klinik^L^^^DN|381005^Huber^Haribert^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|1739^^^Holunder-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||0101^vollstationär, Normalfall^GSG0001||||||20260405|4||||||||||||||||||||||||||N|N
ZBE|0123^KIS|202604011705||INSERT
```

## 3. ACK A01 - transport acknowledgment for admission

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme - HL7 Deutschland ADT Admission Profile, ACK example -->

```
MSH|^~\&|RIS||KIS||202604011706||ACK^A01^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.9^^2.16.840.1.113883.2.6^ISO
SFT|RIS System GmbH^L|3.4|superRIS
MSA|CA|ADT001
```

## 4. ADT A01 - admission for billing (Aufnahme für Abrechnung)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme - HL7 Deutschland ADT Admission Profile, billing example -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202606051705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.40^^2.16.840.1.113883.2.6^ISO
EVN||202606051705||||022606051645
PID|||21098^^^Hagebutten-Krankenhaus^PI||Mardër^Lüdwïg^^^Dr.^^L^A^^^G~Mardër^Lüdwïg^^^Herr Dr.^^D^A^^^G||19780201|F|||Mühlenweg 16&Mühlenweg&16^^Schwerin^^19053^^H||^PRN^PH^^49^385^5794901^^^^^0385/5794901|^WPN^PH^^49^385^83902^^^^^0385/83902|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Jösëfs-Hospital|||DEU^^HL70171
PV1|1|I|HNO^201^2^IN^^N^A^4|R|||381003^Langer^Bernhard^^^Dr.^^^Hagebutten-Krankenhaus^L^^^^^^DN ||||||||||||471936^^^Hagebutten-Krankenhaus^VN|01100000||||C|202401|||||||||||||||||||202606051645
PV2|||||||||20260615|10
ZBE|94827^KIS|202606051705||INSERT
```

## 5. ADT A02 - standard transfer (Verlegung Standardnachricht)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Verlegung - HL7 Deutschland ADT Transfer Profile v01, December 2013 -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.44^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||21098^^^Holunder-Klinik^PI||Reinhardt^Ännëliëse^^^^^L^A^^^G~Rëhbëin^^^^^^M^A^^^G||19890512|F|||Amselweg 21&Amselweg&21^^Rostock^^^^H~Finkenstr. 4&Finkenstr.&4^^Rostock^^^^BDL||^PRN^PH^^49^381^2468901^^^^^0381/2468901|^WPN^PH^^49^381^7913^802^^^^0381/7913-802|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Jösëfs-Hospital|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|381009^Langer^Bernhard^^^Dr.^^^Holunder-Klinik^L^^^DN||||||||||||1739^^^Holunder-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4
ZBE|6789^KIS|202604011935||INSERT
```

## 6. ACK A02 - transport acknowledgment for transfer

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Verlegung - HL7 Deutschland ADT Transfer Profile, ACK example -->

```
MSH|^~\&|RIS|ADT|KIS|ADT|202604011706||ACK^A02^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.4^^2.16.840.1.113883.2.6^ISO
MSA|CA|ADT002
```

## 7. ADT A02 - transfer for DRG (Verlegung für DRG)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Verlegung - HL7 Deutschland ADT Transfer Profile, DRG example -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.45^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||21098^^^Holunder-Klinik^PI||Reinhardt^Ännëliëse^^^^^L^A^^^G~Rëhbëin^^^^^^M^A^^^G||19890512|F|||Amselweg 21&Amselweg&21^^Rostock^^^^H~Finkenstr. 4&Finkenstr.&4^^Rostock^^^^BDL||^PRN^PH^^49^381^2468901^^^^^0381/2468901|^WPN^PH^^49^381^7913^802^^^^0381/7913-802|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Jösëfs-Hospital|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||1739^^^Holunder-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260406|5||||||||||||||||||||||||||N|N
ZBE|6789^KIS|202604011935||INSERT
```

## 8. ADT A03 - standard discharge (Entlassung Standardnachricht)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Entlassung - HL7 Deutschland ADT Discharge Profile v01, December 2013 -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.47^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202504011705||||202504011645
PID|||21098^^^Holunder-Klinik^PI||Reinhardt^Ännëliëse^^^^^L^A^^^G~Rëhbëin^^^^^^M^A^^^G||19890512|F|||Amselweg 21&Amselweg&21^^Rostock^^^^H~Finkenstr. 4&Finkenstr.&4^^Rostock^^^^BDL||^PRN^PH^^49^381^2468901^^^^^0381/2468901|^WPN^PH^^49^381^7913^802^^^^0381/7913-802|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Jösëfs-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||381007^Langer^Bernhard^^^Dr.^^^Holunder-Klinik^L^^^DN^^^DN ||||||||||||1739^^^Holunder-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
ZBE|0123^KIS|202504011705||REFERENCE
```

## 9. ACK A03 - transport acknowledgment for discharge

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Entlassung - HL7 Deutschland ADT Discharge Profile, ACK example -->

```
MSH|^~\&|RIS|ADT|KIS|ADT|202504011706||ACK^A03^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.15^^2.16.840.1.113883.2.6^ISO|
SFT|KIS System GmbH^L|5.0|A1|
MSA|CA|ADT001|
```

## 10. ADT A03 - discharge for DRG (Entlassung für DRG)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Entlassung - HL7 Deutschland ADT Discharge Profile, DRG example -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.48^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||21098^^^Holunder-Klinik^PI||bei der Mühle&bei der&Mühle^Ëdwïn^^^^^L^A^^^G||19800427|M|||Amselweg 21&Amselweg&21^^Rostock^^^^H~Finkenstr.  4&Finkenstr.&4^^Rostock^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Jösëfs-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||1739^^^Holunder-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2|||0102^vollstationär, Arbeitsunfall^GSG0001|||||||4|4|||||||||||||||||||||||||N|N
ZBE|0123^KIS|202504011705||REFERENCE
```

## 11. ADT A03 - discharge for billing (Entlassung für Abrechnung)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Entlassung - HL7 Deutschland ADT Discharge Profile, billing example -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.49^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||21098^^^Holunder-Klinik^PI||bei der Mühle&bei der&Mühle^Ëdwïn^^^^^L^A^^^G||19800427|M|||Amselweg 21&Amselweg&21^^Rostock^^^^H~Finkenstr. 4&Finkenstr.&4^^Rostock^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Jösëfs-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||1739^^^Holunder-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2||||||||||||||||||||||||||||||||||||N|N
ZBE|0123^KIS|202504011705||REFERENCE
```

## 12. MDM T02 - document notification with content (Schlëhen-Klinikum)

<!-- Source: https://wiki.hl7.de/index.php?title=HL7v2-Profile_MDM-Nachrichten - HL7 Deutschland MDM Document Management Profile v01, December 2013 -->

```
MSH|^~\&|HOSPAT|ADT|DATAGATE|ADT|20260516180000||MDM^T02^MDM_T02|102000|D|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|||2.16.840.1.113883.2.6.9.69^^2.16.840.1.1.13883.2.6^ISO
EVN||20260516180000
PID|||611000059^^^Schlëhen-Klinikum^PI||Bëcherreicher^Güstäv^^^^^L||19760609|M|||Brückenweg 8^^Wismar^^23966^DEU^H|03841249|03841-6298734|03842-591|DEU||EVC||||||Stralsund|||D
PV1||I|C1^^^CH|N|6913470||||||||||||||6913470^^^Schlëhen-Klinikum^VN||K|||||||||||||||E|||4512|||||20260222155500|20261113174000|||831||6913470
TXA|1|CN|application/word|||20260516142700|20260516142700||||bächerli|12908||||12908.doc^HOSPAT|DI
OBX|1|ED|^Document Content|1|^text/plain^^Base64^VGhpcyBpcyBhbiBleGFtcGxlIERvY3VtZW50Lg==||||||F
```

## 13. MDM T01 - document notification without content (ORBIS)

<!-- Source: https://wiki.hl7.de/index.php?title=HL7v2-Profile_MDM-Nachrichten - HL7 Deutschland MDM Profile, ORBIS/Schlëhen-Klinikum T01 example -->

```
MSH|^~\&|ORBIS|TEST KH 01|RECAPP|TEST KH 01|202511261036||MDM^T01^MDM_T01|167912|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DE||2.16.840.1.113883.2.6.9.70^^2.16.840.1.1.13883.2.6^ISO
EVN||202511261036|202511261036|
PID|1||742019^^^Schlëhen-Klinikum^PI||Schärfer^Frïëdël^^^^^L||19350725|M|||Hafenstr. 3^^Greifswald^^17489^DEU^H|||||||||||||||D||
PV1|1|I|ST02^^^ABT01^^1974|01^Normalfall^301||^^^^^||||N||||||N|||5043308^^^Schlëhen-Klinikum^VN|||||||||||||||||||2400||||||202601101000||
TXA|1|Anforderung Pathologie|application/pdf|||||20251126103606||||218043^ORBIS PRIMITIVUMNUMMER||KLTSTS900014642164^MEDIS_KLTSTS90|PATH-2025-008907^ORBIS AUFTRAGSNUMMER|5426852_7320975_218043_20251126103606.PDF^ORBIS|AU|||||||
```

## 14. MDM T01 - cardiology transfer report (Herzzentrum Leipzig)

<!-- Source: https://wiki.hl7.de/index.php?title=HL7v2-Profile_MDM-Nachrichten - HL7 Deutschland MDM Profile, CARDDAS/HZL T01 example -->

```
MSH|^~\&|CARDDAS|HZL|DOC|ADT|20260524163405||MDM^T01^MDM_T01|123456|T|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|||2.16.840.1.113883.2.6.9.70^^2.16.840.1.1.13883.2.6^ISO
EVN||20260524163405|||||B1
PID|||04917^^^Schlëhen-Klinikum^PI||Bäumler^Ëlmär^^^^^L
PV1|||||||||||||||||||84571089^^^Schlëhen-Klinikum^VN|||||||||||||||||||||||||20250805
TXA||transferReport|application/pdf|||20250806|||81986785^Glückstein^Rüpërt^^^Dr.^^^^^^^L^HZL|||2396315868^^37459732765491768364593264738293^SHA-1||||2396315868.pdf^CARDDAS|AU|U|AV|||^Barönle^Siegmünd^^^Prof.^^^^^^^L^HZL^20250807200200
```

## 15. MDM T11 - document cancel notification

<!-- Source: https://wiki.hl7.de/index.php?title=HL7v2-Profile_MDM-Nachrichten - HL7 Deutschland MDM Profile, HOSPAT T11 example -->

```
MSH|^~\&|HOSPAT|ADT|DATAGATE|ADT|20260516190000||MDM^T11^MDM_T01|102001|D|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|||2.16.840.1.113883.2.6.9.69^^2.16.840.1.1.13883.2.6^ISO
EVN||20260516190000
PID|||611000059^^^Schlëhen-Klinikum^PI||Bëcherreicher^Güstäv^^^^^L||19760609|M|||Brückenweg 8^^Wismar^^23966^DEU^H|03841249|03841-6298734|03842-591|DEU||EVC||||||Stralsund|||D
PV1||I|C1^^^CH|N|6913470||||||||||||||6913470^^^Schlëhen-Klinikum^VN||K|||||||||||||||E|||4512|||||20260222155500|20261113174000|||831||6913470
TXA|1|CN|application/word|||20260516142700|20260516142700|20260516170000|||bächerli|12908||||12908.doc^HOSPAT|AU
```

## 16. MSH segment example (basic German admission, from wiki.hl7.de Segment_MSH)

<!-- Source: https://wiki.hl7.de/index.php?title=Segment_MSH - HL7 Deutschland common message elements, MSH segment specification -->

```
MSH|^~\&|SUBx||PAT||20250328112408||ADT^A01^ADT_A01|47|P|2.5|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.1^^2.16.840.1.113883.2.6^ISO
```

## 17. ADT A08 - patient update from samedi HL7 gateway (German scheduling platform)

<!-- Source: https://hl7gateway.samedi.de/hl7gateway/messages/adt/ - samedi HL7gateway ADT documentation -->

```
MSH|^~\&|samedi-hl7gateway|samedi|APPLICATION|CLINIC|20260403151846+0200||ADT^A08^ADT_A01|557431481820797018|P|2.5||||||UNICODE UTF-8
EVN|A08|202604031516+0200
PID|1|21098|amï4hhm8h65^^^&www.praxis-öst2.de&DNS^PI~21098^^^^PT||Köhler^Bërnhärd^^^Prof.||20030108|M|||Straßënbögen 7^^Örtschaft^^10987^DE||+49158 333 21098^^CP^^^^^^^^^+49158 333 21098~+49 381 333 210^^PH^^^^^^^^^+49 381 333 210~ëmail@prüfstück.örg^NET^X.400^ëmail@prüfstück.örg
PV1|1|U
```

## 18. SIU S12 - new appointment booking (samedi scheduling)

<!-- Source: https://hl7gateway.samedi.de/hl7gateway/messages/siu - samedi HL7gateway SIU documentation -->

```
MSH|^~\&|samedi-hl7gateway|samedi|system|clinic|20260207130859+0100||SIU^S12^SIU_S12|0059059619819225843|P|2.5||||||UNICODE UTF-8
SCH||e-gufeo9lzvgijhc7z||||BOOKED||1^MRT|1800||^^M30^20260516130000+0200^20260516133000+0200||||||||||||||Booked
TQ1|1||||||20260516130000+0200|20260516133000+0200|||||30^min
NTE||_default|Comment
NTE||Affected body parts|arm~left leg~head
NTE||Kommentar zum Patienten|patient comment, patient without external patient number
PID|1||d829956op57^^^&www.praxis-öst2.de&DNS^PI~^^^^PT||Bäumler^Rüpërt||19840619|M|||Bahnhofstrasse 12^^Berlin^^12345^DE||+49 178 7654321^^CP^^^^^^^^^+49 178 7654321~+49 381 76543-210^^PH^^^^^^^^^+49 381 76543-210~pöst@prüfstück.örg^NET^X.400^pöst@prüfstück.örg~+49 381 76543-211^^FX^^^^^^^^^+49 381 76543-211
RGS|1|A
AIG|1|A|2^Peter Koch^99SAMEDI-RESOURCE^radiologist|||||20260516130000+0200|||1800|s
AIG|2|A|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516130000+0200|||1800|s
```

## 19. ADT A08 - incoming patient update (samedi with Rädvis RIS)

<!-- Source: https://hl7gateway.samedi.de/hl7gateway/messages/adt/ - samedi HL7gateway, incoming ADT example -->

```
MSH|^~\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A08|7304848733204|P|2.5|KQ84N84U2TU004P||AL|NE||8859/1
EVN|A08|202610260719
PID|1||0122^^^&www.praxis-öst2.de&DNS^PI~843699^^^Rädvis^PI|80000208^^^ROS^PI|Gerber^Hëidrun||19570224|F|||Gartenweg 14&Gartenweg 14^^Neubrandenburg^^17033^DE^L||^^PH^^^^0395-8765432 Büro|^^PH
```

## 20. ADT A01 - admission with insurance (Thieme E-ConsentPro, German hospital)

<!-- Source: https://support.thieme-compliance.de/de/ECP/Admin/hl7_adt-nachrichten.html - Thieme Compliance E-ConsentPro HL7 ADT documentation -->

```
MSH|^~\&|||||20260912142642||ADT^A01^ADT_A01|MSG00001|P|2.6|
EVN|A01|20260912142642||
PID|0||357924681^^^PVS1||Siebert^Hëlëna||19730603|F|||Rostocker Str. 789^^Rostock^^18055||03456/78901-0~^NET^Internet^hëlëna.siebert@rostocker-post.com~0345/67890123^^CP
PV1||I|||||||||||||||||6283|
IN1|1|0|BKV3|IKK GESUND PLUS|||||||||||||||||||||||||||||||||||||||||||||49
```
