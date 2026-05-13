# CGM MEDICO (CompuGroup Medical) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Aufnahme (admission), standard profile

```
MSH|^~\&|KIS|ADT|RIS|ADT|202603151705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/15|DEU^German^HL70296^^deutsch||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO
EVN||202603151705||||202603151645
PID|||5678901^^^Tannen-Klinik^PI||Vogt^Renate^^^^^L^A^^^G~Steinbach^^^^^^M^A^^^G~Vogt^^^^Frau^^D^^^^G||19850713|F|||Marktplatz 28&Marktplatz&28^^München^^80331^^H~Gärtnerweg 9&Gärtnerweg&9^^München^^80331^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Klinikum Großhadern|||DEU^German^HL70171^^deutsch
PV1|1|I|CHI^302^2^IN^^N^A^4|R|||710201^Werner^Friedrich^^^Dr.^^^Tannen-Klinik^L^^^DN^^^DN^^G||||||||||||4711^^^Tannen-Klinik^VN|||||||||||||||||||||||||202603151645
PV2|||||||||20250405|4
ZBE|7891^KIS|202603151705||INSERT
```

## 2. ADT^A01 - Aufnahme (admission), DRG profile

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.39^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011705||||022604011645
PID|||67890^^^Tannen-Klinik^PI||Berger^Kornelia^^^^^L^A^^^G~Schwarz^^^^^^M^A^^^G||19840908|F|||Marktplatz 28&Marktplatz&28^^München^^^^H~Gärtnerweg 9&Gärtnerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Klinikum Großhadern|||DEU^^HL70171
PV1|1|I|URO^301^1^IN^^N^A^4|R|||710203^Albrecht^Hëinrich^^^Dr.^^^Tannen-Klinik^L^^^DN|710211^Zimmermann^Markus^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|4711^^^Tannen-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||0101^vollstationär, Normalfall^GSG0001||||||20260405|4||||||||||||||||||||||||||N|N
ZBE|7891^KIS|202604011705||INSERT
```

## 3. ACK^A01 - transport acknowledgment for admission

```
MSH|^~\&|RIS||KIS||202604011706||ACK^A01^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.9^^2.16.840.1.113883.2.6^ISO
SFT|RIS System GmbH^L|3.4|superRIS
MSA|CA|ADT001
```

## 4. ADT^A01 - Aufnahme (admission), billing profile

```
MSH|^~\&|KIS|ADT|RIS|ADT|202606051705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.40^^2.16.840.1.113883.2.6^ISO
EVN||202606051705||||022606051645
PID|||67890^^^Linden-Krankenhaus^PI||Krause^Wolfgang^^^Dr.^^L^A^^^G~Krause^Wolfgang^^^Herr Dr.^^D^A^^^G||19720116|F|||Maximilianstr. 33&Maximilianstr.&33^^München^^80539^^H||^PRN^PH^^49^89^5671234^^^^^089/5671234|^WPN^PH^^49^89^98765^^^^^089/98765|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Klinikum Großhadern|||DEU^^HL70171
PV1|1|I|HNO^201^2^IN^^N^A^4|R|||710203^Albrecht^Hëinrich^^^Dr.^^^Linden-Krankenhaus^L^^^^^^DN ||||||||||||831642^^^Linden-Krankenhaus^VN|01100000||||C|202401|||||||||||||||||||202606051645
PV2|||||||||20260615|10
ZBE|83217^KIS|202606051705||INSERT
```

## 5. ADT^A08 - Änderung Patientendaten (update patient), standard profile

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A08^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.20^^2.16.840.1.113883.2.6^ISO
EVN||202604011705||||202604011645
PID|||67890^^^Tannen-Klinik^PI||Berger^Kornelia^^^^^L^A^^^G~Schwarz^^^^^^B^A^^^G||19840908|F|||Marktplatz 28&Marktplatz&28^^München^^^^H~Gärtnerweg 9&Gärtnerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Klinikum Großhadern|||DEU^^HL70171
PV1|1|I|CHI^202^1^CH^^N^C^4|R|||710207^Albrecht^Hëinrich^^^Dr.^^^Tannen-Klinik^L^^^DN||||||||||||4711^^^Tannen-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4
ZBE|7891^KIS|202604011705||REFERENCE
```

## 6. ACK^A08 - transport acknowledgment for update

```
MSH|^~\&|RIS|ADT|KIS|ADT|202504011706||ACK^A08^ACK|RIS002|P|2.5^DEU|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.5^^2.16.840.1.113883.2.6^ISO|
SFT|KIS System GmbH^L|5.0|A1|
MSA|CA|ADT001|
```

## 7. ADT^A08 - Änderung Patientendaten (update patient), DRG profile

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A08^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.21^^2.16.840.1.113883.2.6^ISO
EVN||202604011705||||202504011645
PID|||67890^^^Tannen-Klinik^PI||von der Heide&von der&Heide^Martin^^^^^L^A^^^G~von der Heide&von der&Heide^Märtin^^^^^M^A^^^G~von der Heide&von der&Heide^Martin^^^Herr^^D^A^^^G||19840908|M|||Leopoldstraße 7&Leopoldstraße&7^^München^XA-DE-BY^80802^DEU^H~Schwanthalerstr. 18&Schwanthalerstr.&18^^München^^80336^DEU^BDL||^PRN^PH^^49^89^2345678^^^^^089/2345678|^WPN^PH^^49^89^7654^321^^^^089/7654-321|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Klinikum Großhadern|||DEU^^HL70171
PV1|1|I|IN2^202^1^IN^^N^C^4|R|||710207^Albrecht^Hëinrich^^^Dr.^^^Tannen-Klinik^L^^^DN|710213^^^^^^^^Tannen-Klinik^^^^DN|||||R||||||9281537^^^Tannen-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4|||||||||||||||||||||||||||N
ZBE|7891^KIS|202604011705||REFERENCE
```

## 8. ADT^A08 - Änderung Patientendaten (update patient), billing profile

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A08^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.22^^2.16.840.1.113883.2.6^ISO
EVN||202604011705||||202504011645
PID|||67890^^^Tannen-Klinik^PI||von der Heide&von der&Heide^Martin^^^^^L^A^^^G~von der Heide&von der&Heide^Märtin^^^^^M^A^^^G~von der Heide&von der&Heide^Martin^^^Herr^^D^A^^^G||19840908|M|||Marktplatz 28&Marktplatz&28^^München^^^^H~Gärtnerweg 9&Gärtnerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Klinikum Großhadern|||DEU^^HL70171
PV1|1|I|IN2^202^1^IN^^N^C^4|R|||710207^Albrecht^Hëinrich^^^Dr.^^^Tannen-Klinik^L^^^DN||||||||||||4711^^^Tannen-Klinik^VN|01100001||||C|20260101|||||||||||||||||||202604011645
PV2|||||||||20260405|4|||||||||||||||||||||||||||N
ZBE|7891^KIS|202604011705||REFERENCE
```

## 9. ADT^A03 - Entlassung (discharge), standard profile

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.47^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202504011705||||202504011645
PID|||67890^^^Tannen-Klinik^PI||Berger^Kornelia^^^^^L^A^^^G~Schwarz^^^^^^M^A^^^G||19840908|F|||Marktplatz 28&Marktplatz&28^^München^^^^H~Gärtnerweg 9&Gärtnerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Klinikum Großhadern|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||710209^Albrecht^Hëinrich^^^Dr.^^^Tannen-Klinik^L^^^DN^^^DN ||||||||||||4711^^^Tannen-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
ZBE|7891^KIS|202504011705||REFERENCE
```

## 10. ADT^A03 - Entlassung (discharge), DRG profile

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.48^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||67890^^^Tannen-Klinik^PI||von der Heide&von der&Heide^Roland^^^^^L^A^^^G||19740205|M|||Marktplatz 28&Marktplatz&28^^München^^^^H~Gärtnerweg  9&Gärtnerweg&9^^München^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Klinikum Großhadern|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||4711^^^Tannen-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2|||0102^vollstationär, Arbeitsunfall^GSG0001|||||||4|4|||||||||||||||||||||||||N|N
ZBE|7891^KIS|202504011705||REFERENCE
```

## 11. ADT^A03 - Entlassung (discharge), billing profile

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.49^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||67890^^^Tannen-Klinik^PI||von der Heide&von der&Heide^Roland^^^^^L^A^^^G||19740205|M|||Marktplatz 28&Marktplatz&28^^München^^^^H~Gärtnerweg 9&Gärtnerweg&9^^München^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Klinikum Großhadern|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||4711^^^Tannen-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2||||||||||||||||||||||||||||||||||||N|N
ZBE|7891^KIS|202504011705||REFERENCE
```

## 12. ACK^A03 - transport acknowledgment for discharge

```
MSH|^~\&|RIS|ADT|KIS|ADT|202504011706||ACK^A03^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.15^^2.16.840.1.113883.2.6^ISO|
SFT|KIS System GmbH^L|5.0|A1|
MSA|CA|ADT001|
```

## 13. ADT^A02 - Verlegung (transfer), standard profile

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.44^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||67890^^^Tannen-Klinik^PI||Berger^Kornelia^^^^^L^A^^^G~Schwarz^^^^^^M^A^^^G||19840908|F|||Marktplatz 28&Marktplatz&28^^München^^^^H~Gärtnerweg 9&Gärtnerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Klinikum Großhadern|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|710213^Albrecht^Hëinrich^^^Dr.^^^Tannen-Klinik^L^^^DN||||||||||||4711^^^Tannen-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4
ZBE|3456^KIS|202604011935||INSERT
```

## 14. ADT^A02 - Verlegung (transfer), DRG profile

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.45^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||67890^^^Tannen-Klinik^PI||Berger^Kornelia^^^^^L^A^^^G~Schwarz^^^^^^M^A^^^G||19840908|F|||Marktplatz 28&Marktplatz&28^^München^^^^H~Gärtnerweg 9&Gärtnerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Klinikum Großhadern|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||4711^^^Tannen-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260406|5||||||||||||||||||||||||||N|N
ZBE|3456^KIS|202604011935||INSERT
```

## 15. ADT^A12 - Stornierung Verlegung (cancel transfer)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A12^ADT_A12|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.46^^2.16.840.1.113883.2.6^ISO
EVN||202604011935||||202604011645
PID|||67890^^^Tannen-Klinik^PI||Berger^Kornelia^^^^^L^A^^^G||19840908|F|||Marktplatz 28&Marktplatz&28^^München^^^^H~Gärtnerweg 9&Gärtnerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Klinikum Großhadern|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||4711^^^Tannen-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4
ZBE|3456^KIS|202604011935||DELETE
```

## 16. ADT^A12 - Stornierung früherer Verlegung (cancel earlier transfer)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A12^ADT_A12|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.46^^2.16.840.1.113883.2.6^ISO
EVN||202604011935||||202604011645
PID|||67890^^^Tannen-Klinik^PI||Berger^Kornelia^^^^^L^A^^^G||19840908|F|||Marktplatz 28&Marktplatz&28^^München^^^^H~Gärtnerweg 9&Gärtnerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Klinikum Großhadern|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||4711^^^Tannen-Klinik^VN|||||||||||||||||||||||||202604011645|||||||H
PV2|||||||||20260405|4
ZBE|3456^KIS|202603301345||DELETE
```

## 17. ADT^A04 - Besuchsmeldung/Registrierung (outpatient registration)

```
MSH|^~\&|KIS|ADT|KIS|ADT|202604011705||ADT^A04^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011705||||202604011645
PID|||67890^^^Tannen-Klinik^PI||Berger^Kornelia^^^^^L^A^^^G~Schwarz^^^^^^M^A^^^G||19840908|F|||Marktplatz 28&Marktplatz&28^^München^^^^H~Gärtnerweg 9&Gärtnerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Klinikum Großhadern|||DEU^^HL70171
PV1|1|O|^^^AIN^^D^A^1|R|||||||||||||||4711^^^Tannen-Klinik^VN|||||||||||||||||||||||||202604011645
ZBE|7891^KIS|202604011705||INSERT
```

## 18. ADT^A04 - Besuchsmeldung/Registrierung (pre-admission with planned date)

```
MSH|^~\&|KIS|ADT|KIS|ADT|202604011705||ADT^A04^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO
EVN||202604011705|20260601|||202604011645
PID|||67890^^^Tannen-Klinik^PI||Berger^Kornelia^^^^^L^A^^^G~Schwarz^^^^^^M^A^^^G||19840908|F|||Marktplatz 28&Marktplatz&28^^München^^^^H~Gärtnerweg 9&Gärtnerweg&9^^München^^^^BDL||^PRN^PH^^49^89^3456789^^^^^089/3456789|^WPN^PH^^49^89^8765^432^^^^089/8765-432|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Klinikum Großhadern|||DEU^^HL70171
PV1|1|I|IN1^^^CH^^N||||||||||||||||4711^^^Tannen-Klinik^VN|||||||||||||||||||||||||202604011645
PV2||||||||20260601
ZBE|7891^KIS|202604011705||INSERT
```

## 19. ACK^A04 - transport acknowledgment for registration

```
MSH|^~\&|RIS|ADT|KIS|ADT|202604011706||ACK^A04^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO|
MSA|CA|ADT001|
```

## 20. ADT^A08 - incoming from KIS via KomServer integration

```
MSH|^~\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260410123517||ADT^A08|2638150947283|P|2.5|9E72B53F8AC791B||AL|NE||8859/1
EVN|A08|202604061019
PID|1||4477^^^&www.praxis-süd.de&DNS^PI~287433^^^Röntgen^PI|20000053^^^KÖL^PI|Lange^Helga||19500327|F|||Sendlinger Str. 41&Sendlinger Str. 41^^München^^80331^DE^L||^^PH^^^^089-9876543 Büro|^^PH
```
