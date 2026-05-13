# ORBIS (Dedalus) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Aufnahme (Standard)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202612151705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/15|DEU^German^HL70296^^deutsch||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO
EVN||202612151705||||202612151645
PID|||5678901^^^Kastanien-Klinik^PI||Rëuter^Hïldëgard^^^^^L^A^^^G~Brückner^^^^^^M^A^^^G~Rëuter^^^^Frau^^D^^^^G||19900107|F|||Büchenweg 12&Büchenweg&12^^Lübeck^^23552^^H~Tannenstr. 19&Tannenstr.&19^^Lübeck^^23552^^BDL||^PRN^PH^^49^451^2468013^^^^^0451/2468013|^WPN^PH^^49^451^7913^024^^^^0451/7913-024|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Ëlisabëth-Hospital|||DEU^German^HL70171^^deutsch
PV1|1|I|CHI^302^2^IN^^N^A^4|R|||270901^Groß^Bernhard^^^Dr.^^^Kastanien-Klinik^L^^^DN^^^DN^^G||||||||||||8264^^^Kastanien-Klinik^VN|||||||||||||||||||||||||202612151645
PV2|||||||||20250405|4
ZBE|5678^KIS|202612151705||INSERT
```

---

## 2. ADT^A01 - Aufnahme (DRG-Profil)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.39^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011705||||022604011645
PID|||10987^^^Kastanien-Klinik^PI||Schëffer^Ännëmarie^^^^^L^A^^^G~Plötz^^^^^^M^A^^^G||19880823|F|||Büchenweg 12&Büchenweg&12^^Lübeck^^^^H~Tannenstr. 19&Tannenstr.&19^^Lübeck^^^^BDL||^PRN^PH^^49^451^2468013^^^^^0451/2468013|^WPN^PH^^49^451^7913^024^^^^0451/7913-024|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Ëlisabëth-Hospital|||DEU^^HL70171
PV1|1|I|URO^301^1^IN^^N^A^4|R|||270903^Langer^Bernhard^^^Dr.^^^Kastanien-Klinik^L^^^DN|270905^Huber^Haribert^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|8264^^^Kastanien-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||0101^vollstationär, Normalfall^GSG0001||||||20260405|4||||||||||||||||||||||||||N|N
ZBE|5678^KIS|202604011705||INSERT
```

---

## 3. ADT^A01 - Aufnahme (Abrechnung)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202606051705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.40^^2.16.840.1.113883.2.6^ISO
EVN||202606051705||||022606051645
PID|||10987^^^Platanen-Krankenhaus^PI||Nüßbaum^Ëckehard^^^Dr.^^L^A^^^G~Nüßbaum^Ëckehard^^^Herr Dr.^^D^A^^^G||19770309|F|||Wallstr. 7&Wallstr.&7^^Kiel^^24103^^H||^PRN^PH^^49^431^5794016^^^^^0431/5794016|^WPN^PH^^49^431^83127^^^^^0431/83127|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Ëlisabëth-Hospital|||DEU^^HL70171
PV1|1|I|HNO^201^2^IN^^N^A^4|R|||270903^Langer^Bernhard^^^Dr.^^^Platanen-Krankenhaus^L^^^^^^DN ||||||||||||359748^^^Platanen-Krankenhaus^VN|01100000||||C|202401|||||||||||||||||||202606051645
PV2|||||||||20260615|10
ZBE|83916^KIS|202606051705||INSERT
```

---

## 4. ACK - Transportquittung (response to A01)

```
MSH|^~\&|RIS||KIS||202604011706||ACK^A01^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.9^^2.16.840.1.113883.2.6^ISO
SFT|RIS System GmbH^L|3.4|superRIS
MSA|CA|ADT001
```

---

## 5. ADT^A02 - Verlegung (Standard)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.44^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||10987^^^Kastanien-Klinik^PI||Schëffer^Ännëmarie^^^^^L^A^^^G~Plötz^^^^^^M^A^^^G||19880823|F|||Büchenweg 12&Büchenweg&12^^Lübeck^^^^H~Tannenstr. 19&Tannenstr.&19^^Lübeck^^^^BDL||^PRN^PH^^49^451^2468013^^^^^0451/2468013|^WPN^PH^^49^451^7913^024^^^^0451/7913-024|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Ëlisabëth-Hospital|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|270909^Langer^Bernhard^^^Dr.^^^Kastanien-Klinik^L^^^DN||||||||||||8264^^^Kastanien-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4
ZBE|2345^KIS|202604011935||INSERT
```

---

## 6. ADT^A02 - Verlegung (DRG)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.45^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||10987^^^Kastanien-Klinik^PI||Schëffer^Ännëmarie^^^^^L^A^^^G~Plötz^^^^^^M^A^^^G||19880823|F|||Büchenweg 12&Büchenweg&12^^Lübeck^^^^H~Tannenstr. 19&Tannenstr.&19^^Lübeck^^^^BDL||^PRN^PH^^49^451^2468013^^^^^0451/2468013|^WPN^PH^^49^451^7913^024^^^^0451/7913-024|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Ëlisabëth-Hospital|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||8264^^^Kastanien-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260406|5||||||||||||||||||||||||||N|N
ZBE|2345^KIS|202604011935||INSERT
```

---

## 7. ADT^A03 - Entlassung (Standard)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.47^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202504011705||||202504011645
PID|||10987^^^Kastanien-Klinik^PI||Schëffer^Ännëmarie^^^^^L^A^^^G~Plötz^^^^^^M^A^^^G||19880823|F|||Büchenweg 12&Büchenweg&12^^Lübeck^^^^H~Tannenstr. 19&Tannenstr.&19^^Lübeck^^^^BDL||^PRN^PH^^49^451^2468013^^^^^0451/2468013|^WPN^PH^^49^451^7913^024^^^^0451/7913-024|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Ëlisabëth-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||270907^Langer^Bernhard^^^Dr.^^^Kastanien-Klinik^L^^^DN^^^DN ||||||||||||8264^^^Kastanien-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
ZBE|5678^KIS|202504011705||REFERENCE
```

---

## 8. ADT^A03 - Entlassung (DRG)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.48^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||10987^^^Kastanien-Klinik^PI||unter der Brücke&unter der&Brücke^Ëbërhard^^^^^L^A^^^G||19791014|M|||Büchenweg 12&Büchenweg&12^^Lübeck^^^^H~Tannenstr.  19&Tannenstr.&19^^Lübeck^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Ëlisabëth-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||8264^^^Kastanien-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2|||0102^vollstationär, Arbeitsunfall^GSG0001|||||||4|4|||||||||||||||||||||||||N|N
ZBE|5678^KIS|202504011705||REFERENCE
```

---

## 9. ADT^A03 - Entlassung (Abrechnung)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.49^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||10987^^^Kastanien-Klinik^PI||unter der Brücke&unter der&Brücke^Ëbërhard^^^^^L^A^^^G||19791014|M|||Büchenweg 12&Büchenweg&12^^Lübeck^^^^H~Tannenstr. 19&Tannenstr.&19^^Lübeck^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Ëlisabëth-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||8264^^^Kastanien-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2||||||||||||||||||||||||||||||||||||N|N
ZBE|5678^KIS|202504011705||REFERENCE
```

---

## 10. ACK^A03 - Transportquittung (response to discharge)

```
MSH|^~\&|RIS|ADT|KIS|ADT|202504011706||ACK^A03^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.15^^2.16.840.1.113883.2.6^ISO|
SFT|KIS System GmbH^L|5.0|A1|
MSA|CA|ADT001|
```

---

## 11. ADT^A12 - Stornierung Verlegung (letzte Verlegung)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A12^ADT_A12|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.46^^2.16.840.1.113883.2.6^ISO
EVN||202604011935||||202604011645
PID|||10987^^^Kastanien-Klinik^PI||Schëffer^Ännëmarie^^^^^L^A^^^G||19880823|F|||Büchenweg 12&Büchenweg&12^^Lübeck^^^^H~Tannenstr. 19&Tannenstr.&19^^Lübeck^^^^BDL||^PRN^PH^^49^451^2468013^^^^^0451/2468013|^WPN^PH^^49^451^7913^024^^^^0451/7913-024|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Ëlisabëth-Hospital|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||8264^^^Kastanien-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4
ZBE|2345^KIS|202604011935||DELETE
```

---

## 12. ADT^A12 - Stornierung einer früheren Verlegung (historisch)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A12^ADT_A12|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.46^^2.16.840.1.113883.2.6^ISO
EVN||202604011935||||202604011645
PID|||10987^^^Kastanien-Klinik^PI||Schëffer^Ännëmarie^^^^^L^A^^^G||19880823|F|||Büchenweg 12&Büchenweg&12^^Lübeck^^^^H~Tannenstr. 19&Tannenstr.&19^^Lübeck^^^^BDL||^PRN^PH^^49^451^2468013^^^^^0451/2468013|^WPN^PH^^49^451^7913^024^^^^0451/7913-024|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Ëlisabëth-Hospital|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||8264^^^Kastanien-Klinik^VN|||||||||||||||||||||||||202604011645|||||||H
PV2|||||||||20260405|4
ZBE|2345^KIS|202603301345||DELETE
```

---

## 13. ADT^A01 - Thieme E-ConsentPro (stationäre Aufnahme)

```
MSH|^~\&|||||20260912142642||ADT^A01^ADT_A01|MSG00001|P|2.6|
EVN|A01|20260912142642||
PID|0||246813579^^^PVS1||Brückner^Gïsëla||19720514|F|||Holtenauer Str. 789^^Kiel^^24105||04567/89012-0~^NET^Internet^gisela.brueckner@kielerpost.com~0456/78901234^^CP
PV1||I|||||||||||||||||9352|
IN1|1|0|MKV1|BARMER ERSATZKASSE|||||||||||||||||||||||||||||||||||||||||||||49
```

---

## 14. ADT^A02 - Thieme E-ConsentPro (Verlegung)

```
MSH|^~\&|||||20260912142642||ADT^A02^ADT_A02|MSG00001|P|2.6|
EVN|A02|20260912142642||
PID|0||246813579^^^PVS1||Brückner^Gïsëla||19720514|F|||Holtenauer Str. 789^^Kiel^^24105||04567/89012-0~^NET^X.400^gisela.brueckner@kielerpost.com~0456/78901234^^CP
PV1||I|nëuFlügel^nëuZimmer^nëuBett|||altFlügel^altZimmer^altBett|0100^BRANDT,FRÏTZ|0148^BRANDT,ÄNNA ES||SUR|||||||0148^BRANDT,FRÏTZ|S|3600|A|||||||||||||||||||GËNKHS||||||
```

---

## 15. ADT^A03 - Thieme E-ConsentPro (Entlassung)

```
MSH|^~\&|||||20260912142642||ADT^A03^ADT_A03|MSG00001|P|2.6|
EVN|A03|20260912142642||
PID|0||246813579^^^PVS1||Brückner^Gïsëla||19720514|F|||Holtenauer Str. 789^^Kiel^^24105||04567/89012-0~^NET^X.400^gisela.brueckner@kielerpost.com~0456/78901234^^CP
PV1||I|||||||||||||||||9352|
IN1|1|0|MKV1|BARMER ERSATZKASSE|||||||||||||||||||||||||||||||||||||||||||||49
```

---

## 16. ADT^A08 - samedi HL7gateway (Patient update, outbound)

```
MSH|^~\&|samedi-hl7gateway|samedi|APPLICATION|CLINIC|20260403151846+0200||ADT^A08^ADT_A01|446320370709685907|P|2.5||||||UNICODE UTF-8
EVN|A08|202604031516+0200
PID|1|10987|zjh3ggl7g54^^^&www.praxis-nörd2.de&DNS^PI~10987^^^^PT||Feldkamp^Hëlmüt^^^Prof.||19900107|M|||Straßënwëg 18^^Städtlein^^54310^DE||+49157 222 10987^^CP^^^^^^^^^+49157 222 10987~+49 451 222 109^^PH^^^^^^^^^+49 451 222 109~ëmail@bëispiel2.örg^NET^X.400^ëmail@bëispiel2.örg
PV1|1|U
```

---

## 17. ADT^A08 - samedi HL7gateway (inbound from KIS/Kommunikationsserver)

```
MSH|^~\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A08|6193737622093|P|2.5|HN51K51R9QR771M||AL|NE||8859/1
EVN|A08|202610260719
PID|1||9011^^^&www.praxis-nörd2.de&DNS^PI~732588^^^Rädvis^PI|70000182^^^SHL^PI|Krüger^Hëinrich||19560519|F|||Prüfwëg 35&Prüfwëg 35^^Neumünster^^24534^DE^L||^^PH^^^^04321-8765432 Büro|^^PH
```

---

## 18. ADT^A40 - samedi HL7gateway (Patientenzusammenführung/Merge)

```
MSH|^~\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A40|6193737622093|P|2.5|HN51K51R9QR771M||AL|NE||8859/1
EVN|A40|202602041715
PID|1||9011^^^&www.praxis-nörd2.de&DNS^PI~732588^^^Rädvis^PI|70000182^^^SHL^PI|Krüger^Hëinrich||19560519|F|||Prüfwëg 35&Prüfwëg 35^^Neumünster^^24534^DE^L||^^PH^^^^04321-8765432 Büro|^^PH
MRG|9012~c718845mn46^^^&www.praxis-nörd2.de&DNS~9013944^^^&1.2.276.0.76.3.1.660.1.1.1.2.1&ISO^PI|
```

---

## 19. SIU^S12 - samedi HL7gateway (Neuer Termin mit Patient)

```
MSH|^~\&|samedi-hl7gateway|samedi|system|clinic|20260207130859+0100||SIU^S12^SIU_S12|7504504064263669287|P|2.5||||||UNICODE UTF-8
SCH||9-dpcdk6gvsbetzd3v||||BOOKED||1^MRT|1800||^^M30^20260516130000+0200^20260516133000+0200||||||||||||||Booked
TQ1|1||||||20260516130000+0200|20260516133000+0200|||||30^min
NTE||_default|Comment
NTE||Affected body parts|arm~left leg~head
NTE||Kommentar zum Patienten|patient comment, patient without external patient number
PID|1||p9088cd2903^^^&www.praxis-nörd2.de&DNS^PI~^^^^PT||Wëber^Frïedhelm||19751024|M|||Bahnhofstrasse 12^^Berlin^^12345^DE||+49 171 1234567^^CP^^^^^^^^^+49 171 1234567~+49 89 12345-678^^PH^^^^^^^^^+49 89 12345-678~mail@example.org^NET^X.400^mail@example.org~+49 89 12345-679^^FX^^^^^^^^^+49 89 12345-679
RGS|1|A
AIG|1|A|2^Peter Koch^99SAMEDI-RESOURCE^radiologist|||||20260516130000+0200|||1800|s
AIG|2|A|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516130000+0200|||1800|s
```

---

## 20. ORU^R01 - Laborbefund (from wiki.hl7.de HL7Example template)

```
MSH|^~\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4
PID|||555-44-4444||EVERYWOMAN^EVE^E^^^^L|JONES|19620320|F|||153 FERNWOOD DR.^^STATESVILLE^OH^35292||(206)3345232|(206)752-121||||AC555444444||67-A4335^OH^20030520
OBR|1|845439^GHH OE|1045813^GHH LAB|15545^GLUCOSE|||200202150730|||||||||555-55-5555^PRIMARY^PATRICIA P^^^^MD^^|||||||||F||||||444-44-4444^HIPPOCRATES^HOWARD H^^^^MD
OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F
```
