# MCC (Meierhofer AG) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Stationaere Aufnahme (Inpatient admission, standard)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202612151705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/15|DEU^German^HL70296^^deutsch||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO
EVN||202612151705||||202612151645
PID|||3456789^^^Weiden-Klinik^PI||Kirchner^Ännëlïn^^^^^L^A^^^G~Reuter^^^^^^M^A^^^G~Kirchner^^^^Frau^^D^^^^G||19870213|F|||Falkenstr. 10&Falkenstr.&10^^Mannheim^^68159^^H~Drosselweg 22&Drosselweg&22^^Mannheim^^68159^^BDL||^PRN^PH^^49^621^1357924^^^^^0621/1357924|^WPN^PH^^49^621^8024^613^^^^0621/8024-613|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Theresiën-Hospital|||DEU^German^HL70171^^deutsch
PV1|1|I|CHI^302^2^IN^^N^A^4|R|||840601^Groß^Bernhard^^^Dr.^^^Weiden-Klinik^L^^^DN^^^DN^^G||||||||||||5371^^^Weiden-Klinik^VN|||||||||||||||||||||||||202612151645
PV2|||||||||20250405|4
ZBE|8901^KIS|202612151705||INSERT
```

---

## 2. ADT^A01 - Aufnahme fuer DRG (Admission for DRG billing)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.39^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011705||||022604011645
PID|||76543^^^Weiden-Klinik^PI||Stark^Brïgïtte^^^^^L^A^^^G~Wolff^^^^^^M^A^^^G||19850619|F|||Falkenstr. 10&Falkenstr.&10^^Mannheim^^^^H~Drosselweg 22&Drosselweg&22^^Mannheim^^^^BDL||^PRN^PH^^49^621^1357924^^^^^0621/1357924|^WPN^PH^^49^621^8024^613^^^^0621/8024-613|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Theresiën-Hospital|||DEU^^HL70171
PV1|1|I|URO^301^1^IN^^N^A^4|R|||840603^Langer^Bernhard^^^Dr.^^^Weiden-Klinik^L^^^DN|840605^Huber^Haribert^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|5371^^^Weiden-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||0101^vollstationär, Normalfall^GSG0001||||||20260405|4||||||||||||||||||||||||||N|N
ZBE|8901^KIS|202604011705||INSERT
```

---

## 3. ADT^A01 - Aufnahme fuer Abrechnung (Admission for billing)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202606051705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.40^^2.16.840.1.113883.2.6^ISO
EVN||202606051705||||022606051645
PID|||76543^^^Erlen-Krankenhaus^PI||Geiger^Kläus^^^Dr.^^L^A^^^G~Geiger^Kläus^^^Herr Dr.^^D^A^^^G||19740116|F|||Schlossstr. 25&Schlossstr.&25^^Heidelberg^^69115^^H||^PRN^PH^^49^6221^4793582^^^^^06221/4793582|^WPN^PH^^49^6221^83261^^^^^06221/83261|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Theresiën-Hospital|||DEU^^HL70171
PV1|1|I|HNO^201^2^IN^^N^A^4|R|||840603^Langer^Bernhard^^^Dr.^^^Erlen-Krankenhaus^L^^^^^^DN||||||||||||641825^^^Erlen-Krankenhaus^VN|01100000||||C|200301|||||||||||||||||||202606051645
PV2|||||||||20260615|10
ZBE|61728^KIS|202606051705||INSERT
```

---

## 4. ACK^A01 - Transportquittung (Transport acknowledgment for A01)

```
MSH|^~\&|RIS||KIS||202604011706||ACK^A01^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.9^^2.16.840.1.113883.2.6^ISO
SFT|RIS System GmbH^L|3.4|superRIS
MSA|CA|ADT001
```

---

## 5. ADT^A02 - Verlegung Standard (Patient transfer, standard)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.44^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||76543^^^Weiden-Klinik^PI||Stark^Brïgïtte^^^^^L^A^^^G~Wolff^^^^^^M^A^^^G||19850619|F|||Falkenstr. 10&Falkenstr.&10^^Mannheim^^^^H~Drosselweg 22&Drosselweg&22^^Mannheim^^^^BDL||^PRN^PH^^49^621^1357924^^^^^0621/1357924|^WPN^PH^^49^621^8024^613^^^^0621/8024-613|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Theresiën-Hospital|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|840609^Langer^Bernhard^^^Dr.^^^Weiden-Klinik^L^^^DN||||||||||||5371^^^Weiden-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4
ZBE|3456^KIS|202604011935||INSERT
```

---

## 6. ADT^A02 - Verlegung fuer DRG (Patient transfer for DRG)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.45^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||76543^^^Weiden-Klinik^PI||Stark^Brïgïtte^^^^^L^A^^^G~Wolff^^^^^^M^A^^^G||19850619|F|||Falkenstr. 10&Falkenstr.&10^^Mannheim^^^^H~Drosselweg 22&Drosselweg&22^^Mannheim^^^^BDL||^PRN^PH^^49^621^1357924^^^^^0621/1357924|^WPN^PH^^49^621^8024^613^^^^0621/8024-613|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Theresiën-Hospital|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||5371^^^Weiden-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260406|5||||||||||||||||||||||||||N|N
ZBE|3456^KIS|202604011935||INSERT
```

---

## 7. ACK^A02 - Transportquittung Verlegung (Transport acknowledgment for A02)

```
MSH|^~\&|RIS|ADT|KIS|ADT|202604011706||ACK^A02^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.4^^2.16.840.1.113883.2.6^ISO
MSA|CA|ADT002|
```

---

## 8. ADT^A03 - Entlassung Standard (Patient discharge, standard)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.47^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202504011705||||202504011645
PID|||76543^^^Weiden-Klinik^PI||Stark^Brïgïtte^^^^^L^A^^^G~Wolff^^^^^^M^A^^^G||19850619|F|||Falkenstr. 10&Falkenstr.&10^^Mannheim^^^^H~Drosselweg 22&Drosselweg&22^^Mannheim^^^^BDL||^PRN^PH^^49^621^1357924^^^^^0621/1357924|^WPN^PH^^49^621^8024^613^^^^0621/8024-613|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Theresiën-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||840607^Langer^Bernhard^^^Dr.^^^Weiden-Klinik^L^^^DN^^^DN||||||||||||5371^^^Weiden-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
ZBE|8901^KIS|202504011705||REFERENCE
```

---

## 9. ACK^A03 - Transportquittung Entlassung (Transport acknowledgment for A03)

```
MSH|^~\&|RIS|ADT|KIS|ADT|202504011706||ACK^A03^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.15^^2.16.840.1.113883.2.6^ISO|
SFT|KIS System GmbH^L|5.0|A1|
MSA|CA|ADT001|
```

---

## 10. ADT^A03 - Entlassung fuer DRG (Discharge for DRG billing)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.48^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||76543^^^Weiden-Klinik^PI||hinter dem Wald&hinter dem&Wald^Wïlfrïed^^^^^L^A^^^G||19760304|M|||Falkenstr. 10&Falkenstr.&10^^Mannheim^^^^H~Drosselweg 22&Drosselweg&22^^Mannheim^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Theresiën-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||5371^^^Weiden-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2|||0102^vollstationär, Arbeitsunfall^GSG0001|||||||4|4|||||||||||||||||||||||||N|N
ZBE|8901^KIS|202504011705||REFERENCE
```

---

## 11. ADT^A03 - Entlassung fuer Abrechnung (Discharge for billing)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.49^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||76543^^^Weiden-Klinik^PI||hinter dem Wald&hinter dem&Wald^Wïlfrïed^^^^^L^A^^^G||19760304|M|||Falkenstr. 10&Falkenstr.&10^^Mannheim^^^^H~Drosselweg 22&Drosselweg&22^^Mannheim^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Theresiën-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||5371^^^Weiden-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2||||||||||||||||||||||||||||||||||||N|N
ZBE|8901^KIS|202504011705||REFERENCE
```

---

## 12. ADT^A05 - Voraufnahme (Pre-admission)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011935||ADT^A05^ADT_A05|ADT002|P|2.5^DEU|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.42^^2.16.840.1.113883.2.6^ISO
EVN||202504011935||||202504011645
PID|1||76543^^^Weiden-Klinik^PI||Stark^Brïgïtte^^^^^L^A^^^G||19850619|F|||Falkenstr. 10&Falkenstr.&10^^Mannheim^^^^H~Drosselweg 22&Drosselweg&22^^Mannheim^^^^BDL||^PRN^PH^^49^621^1357924^^^^^0621/1357924|^WPN^PH^^49^621^8024^613^^^^0621/8024-613|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Theresiën-Hospital|||DEU^^HL70171
PV1|1|I|||||||||||||||||4711^^^Weiden-Klinik^VN|||||||||||||||||||||||||202504011654
```

---

## 13. ADT^A38 - Stornierung einer Voraufnahme (Cancel pre-admission)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011935||ADT^A38^ADT_A38|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.43^^2.16.840.1.113883.2.6^ISO
EVN||202504011935||||202504011645
PID|1||76543^^^Weiden-Klinik^PI||Stark^Brïgïtte^^^^^L^A^^^G||19850619|F|||Falkenstr. 10&Falkenstr.&10^^Mannheim^^^^H~Drosselweg 22&Drosselweg&22^^Mannheim^^^^BDL||^PRN^PH^^49^621^1357924^^^^^0621/1357924|^WPN^PH^^49^621^8024^613^^^^0621/8024-613|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Theresiën-Hospital|||DEU^^HL70171
PV1|1|P|||||||||||||||||5371^^^Weiden-Klinik^VN|||||||||||||||||||||||||202504011645
```

---

## 14. BAR^P12 - Diagnoseübermittlung (Diagnosis transmission, ICD-10)

```
MSH|^~\&|KIS|ADT|LAB|ADT|202610141345||BAR^P12^BAR_P12|ADT03|P|2.5^DEU&&HL70399|||AL|NE||8859/1|||2.16.840.1.113883.2.6.9.66^^2.16.840.1.113883.2.6^ISO
EVN||202610141345
PID|||654318^^^KIS^PI||Schäfer^Ërnst^^^^^L||19570816|M|||Amselgasse 12&Amselgasse&12^^Karlsruhe^XA-DE-BW^76131^DEU^H
PV1||I|CHI^202^2^CH^^N||||||||||||||||543216^^^KIS^VN||||||||||||||||000000|||||||||202610091820
ZBE|567678^KIS|202610121230||REFERENCE
DG1|1||K35.-^Akute Appendizitis^I10-2005||202610141345|ED|||||||||1.1|840601^^^^^^^^^^^^DN||||56876^KIS|A
DG1|2||K35.-^Akute Appendizitis^I10-2005||202610141345|AD|||||||||1.2|840601^^^^^^^^^^^^DN||||56877^KIS|A
DG1|3||K35.0^Akute Appendizitis mit diffuser Peritonitis^I10-2005||202610141345|BD|||||||||1.2|840601^^^^^^^^^^^^DN||||56878^KIS|A
```

---

## 15. BAR^P12 - Prozeduruebermittlung (Procedure transmission, OPS codes)

```
MSH|^~\&|KIS|ADT|LAB|ADT|202610141345||BAR^P12^BAR_P12|ADT03|P|2.5^DEU&&HL70399|||AL|NE||8859/1|||2.16.840.1.113883.2.6.9.66^^2.16.840.1.113883.2.6^ISO
SFT|KIS Hersteller GmbH^L|5.4.0|KIS System A
EVN||202610141345
PID|||654318^^^KIS^PI||Schäfer^Ërnst^^^^^L||19570816|M|||Amselgasse 12&Amselgasse&12^^Karlsruhe^XA-DE-BW^76131^DEU^H
PV1|1|I|CHI^202^2^CH^^N||||||||||||||||543216^^^KIS^VN|||||||||||||||||||||||||2026100510
ZBE|678678|20261013||REFERENCE
PR1|1||8-901^Inhalationsanästhesie^O301-2005||202610141415||120|||||||1|||||67658^KIS|A
PR1|2||5-470.0^Appendektomie, offen chirurgisch^O301-2005||202610141415||90|||||||2|||||67659^KIS|A
```

---

## 16. BAR^P12 - Diagnose und Prozeduren kombiniert (Combined diagnosis and procedures)

```
MSH|^~\&|KIS|ADT|LAB|ADT|202610141345||BAR^P12^BAR_P12|ADT03|P|2.5^DEU&&HL70399|||AL|NE||8859/1|||2.16.840.1.113883.2.6.9.66^^2.16.840.1.113883.2.6^ISO
EVN||202610141345
PID|||654318^^^KIS^PI||Schäfer^Ërnst^^^^^L||19570816|M|||Amselgasse 12&Amselgasse&12^^Karlsruhe^XA-DE-BW^76131^DEU^H
PV1||I|CHI^202^2^CH^^N||||||||||||||||543216^^^KIS^VN
ZBE|567678^KIS|202610121230||REFERENCE
DG1|1||N26 L V^Verdacht auf Schrumpfniere links^I10-2005||202610141345|AD|||||||||1|840601^^^^^^^^^^^^DN||||56875467^KIS|A
PR1|1||8-901^Inhalationsanästhesie^O301-2004||202610141415||120||||||||||||67658^KIS|A
PR1|2||5-470.0^Appendektomie, offen chirurgisch^O301-2004||202610141415||90||||||||||||67659^KIS|A
```

---

## 17. ADT^A08 - Patient Update (samedi HL7gateway, outbound)

```
MSH|^~\&|samedi-hl7gateway|samedi|APPLICATION|CLINIC|20260403151846+0200||ADT^A08^ADT_A01|113987037376907574|P|2.5||||||UNICODE UTF-8
EVN|A08|202604031516+0200
PID|1|76543|wëa0ddh4d21^^^&www.praxis-wëst.de&DNS^PI~76543^^^^PT||Feldmann^Albrëcht^^^Prof.||19990106|M|||Straßënplatz 48^^Örtlein^^43210^DE||+49154 888 76543^^CP^^^^^^^^^+49154 888 76543~+49 621 888 456^^PH^^^^^^^^^+49 621 888 456~ëmail@mannheim-post.örg^NET^X.400^ëmail@mannheim-post.örg
PV1|1|U
```

---

## 18. ADT^A08 - Patient Update (samedi HL7gateway, inbound from KIS)

```
MSH|^~\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A08|3860292388759|P|2.5|BG84E84I0GI903D||AL|NE||8859/1
EVN|A08|202610260719
PID|1||6788^^^&www.praxis-wëst.de&DNS^PI~409255^^^Rädvis^PI|40000104^^^MÜN^PI|Gerber^Hëlgard||19520624|F|||Prüfplatz 42&Prüfplatz 42^^Lübeck^^23552^DE^L||^^PH^^^^0451-8765432 Büro|^^PH
```

---

## 19. ADT^A40 - Patientenzusammenfuehrung (Patient merge)

```
MSH|^~\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A40|3860292388759|P|2.5|BG84E84I0GI903D||AL|NE||8859/1
EVN|A40|202602041715
PID|1||6788^^^&www.praxis-wëst.de&DNS^PI~409255^^^Rädvis^PI|40000104^^^MÜN^PI|Gerber^Hëlgard||19520624|F|||Prüfplatz 42&Prüfplatz 42^^Lübeck^^23552^DE^L||^^PH^^^^0451-8765432 Büro|^^PH
MRG|6789~y485512gh13^^^&www.praxis-wëst.de&DNS~6679588^^^&1.2.276.0.76.3.1.660.1.1.1.2.1&ISO^PI|
```

---

## 20. ADT^A29 - Patient geloescht (Patient deleted)

```
MSH|^~\&|samedi-hl7gateway|samedi|APPLICATION|CLINIC|20260403152323+0200||ADT^A29^ADT_A21|21583524086395044117|P|2.5||||||UNICODE UTF-8
EVN|A29|202604031523+0200
PID|1|66|x83g67d9c76^^^&www.praxis-wëst.de&DNS^PI~66^^^^PT||Brinkmann^Ëlmar||197810201
PV1|1|U
```
