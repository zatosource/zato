# iMedOne (Telekom Healthcare / T-Systems) - real HL7v2 ER7 messages

## 1. ADT^A01 - Admission, standard profile (wiki.hl7.de)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme - HL7 Deutschland ADT admission profile, Ausgabe 2013 -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202612151705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/15|DEU^German^HL70296^^deutsch||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO
EVN||202612151705||||202612151645
PID|||7654321^^^Linden-Klinik^PI||Schubert^Ingëborg^^^^^L^A^^^G~Brandt^^^^^^M^A^^^G~Schubert^^^^Frau^^D^^^^G||19851023|F|||Prager Straße 31&Prager Straße&31^^Dresden^^01069^^H~Bautzner Str. 8&Bautzner Str.&8^^Dresden^^01099^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Universitätsklinikum Dresden|||DEU^German^HL70171^^deutsch
PV1|1|I|CHI^302^2^IN^^N^A^4|R|||620401^Meier^Thëodor^^^Dr.^^^Linden-Klinik^L^^^DN^^^DN^^G||||||||||||3142^^^Linden-Klinik^VN|||||||||||||||||||||||||202612151645
PV2|||||||||20250405|4
ZBE|5678^KIS|202612151705||INSERT
```

## 2. ADT^A01 - Admission for DRG (wiki.hl7.de)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme - HL7 Deutschland ADT admission profile, DRG subprofile -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.39^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011705||||020504011645
PID|||54321^^^Linden-Klinik^PI||Wendt^Liëselotte^^^^^L^A^^^G~Sommer^^^^^^M^A^^^G||19830711|F|||Prager Straße 31&Prager Straße&31^^Dresden^^^^H~Bautzner Str. 8&Bautzner Str.&8^^Dresden^^^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Universitätsklinikum Dresden|||DEU^^HL70171
PV1|1|I|URO^301^1^IN^^N^A^4|R|||620403^Schiller^Frïedhelm^^^Dr.^^^Linden-Klinik^L^^^DN|620405^Naumann^Wïlfried^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|3142^^^Linden-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||0101^vollstationär, Normalfall^GSG0001||||||20260405|4||||||||||||||||||||||||||N|N
ZBE|5678^KIS|202604011705||INSERT
```

## 3. ADT^A01 - Admission for billing (wiki.hl7.de)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme - HL7 Deutschland ADT admission profile, Abrechnung subprofile -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202606051705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.40^^2.16.840.1.113883.2.6^ISO
EVN||202606051705||||020506051645
PID|||54321^^^Eichen-Krankenhaus^PI||Hahn^Hëlmut^^^Dr.^^L^A^^^G~Hahn^Hëlmut^^^Herr Dr.^^D^A^^^G||19720219|F|||Hainstraße 19&Hainstraße&19^^Leipzig^^04109^^H||^PRN^PH^^49^341^4681357^^^^^0341/4681357|^WPN^PH^^49^341^97531^^^^^0341/97531|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Universitätsklinikum Dresden|||DEU^^HL70171
PV1|1|I|HNO^201^2^IN^^N^A^4|R|||620403^Schiller^Frïedhelm^^^Dr.^^^Eichen-Krankenhaus^L^^^^^^DN||||||||||||529814^^^Eichen-Krankenhaus^VN|01100000||||C|202401|||||||||||||||||||200506051645
PV2|||||||||20260615|10
ZBE|82914^KIS|202606051705||INSERT
```

## 4. ACK^A01 - Transport acknowledgment (wiki.hl7.de)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme - ACK response to ADT^A01 -->

```
MSH|^~\&|RIS||KIS||202604011706||ACK^A01^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.9^^2.16.840.1.113883.2.6^ISO
SFT|RIS System GmbH^L|3.4|superRIS
MSA|CA|ADT001
```

## 5. ADT^A02 - Transfer, standard profile (wiki.hl7.de)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Verlegung - HL7 Deutschland ADT transfer profile, Ausgabe 2013 -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.44^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||54321^^^Linden-Klinik^PI||Wendt^Liëselotte^^^^^L^A^^^G~Sommer^^^^^^M^A^^^G||19830711|F|||Prager Straße 31&Prager Straße&31^^Dresden^^^^H~Bautzner Str. 8&Bautzner Str.&8^^Dresden^^^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Universitätsklinikum Dresden|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|620409^Schiller^Frïedhelm^^^Dr.^^^Linden-Klinik^L^^^DN||||||||||||3142^^^Linden-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4
ZBE|1234^KIS|202604011935||INSERT
```

## 6. ADT^A02 - Transfer for DRG (wiki.hl7.de)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Verlegung - HL7 Deutschland ADT transfer profile, DRG subprofile -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.45^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||54321^^^Linden-Klinik^PI||Wendt^Liëselotte^^^^^L^A^^^G~Sommer^^^^^^M^A^^^G||19830711|F|||Prager Straße 31&Prager Straße&31^^Dresden^^^^H~Bautzner Str. 8&Bautzner Str.&8^^Dresden^^^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Universitätsklinikum Dresden|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||3142^^^Linden-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260406|5||||||||||||||||||||||||||N|N
ZBE|1234^KIS|202604011935||INSERT
```

## 7. ADT^A03 - Discharge (wiki.hl7.de)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Entlassung - HL7 Deutschland ADT discharge profile, Ausgabe 2013 -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.47^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202504011705||||202504011645
PID|||54321^^^Linden-Klinik^PI||Wendt^Liëselotte^^^^^L^A^^^G~Sommer^^^^^^M^A^^^G||19830711|F|||Prager Straße 31&Prager Straße&31^^Dresden^^^^H~Bautzner Str. 8&Bautzner Str.&8^^Dresden^^^^BDL||^PRN^PH^^49^351^2468135^^^^^0351/2468135|^WPN^PH^^49^351^9753^246^^^^0351/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Universitätsklinikum Dresden|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||620407^Schiller^Frïedhelm^^^Dr.^^^Linden-Klinik^L^^^DN^^^DN||||||||||||3142^^^Linden-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
ZBE|5678^KIS|202504011705||REFERENCE
```

## 8. ADT^A01 - HL7 v2.5 admission with MEDOS sending application (oemig.de)

<!-- Source: https://www.oemig.de/Frank/phd-anhang2.htm - Frank Oemig PhD thesis, Anhang 2, German HL7 v2.5 example -->

```
MSH|^~\&|MEDOS|RAD|SAP-ISH||20240120116412002||ADT^A01|1325-1|P|2.5|||||DEU|8859/1|DEU
EVN|A01|20240120164122|20240120140000
PID|||8765^^^KIS||Wendt^Liëselotte^^^^^L~Gruber^Liëselotte^^^^^B||19820504|F|||Falkenweg 15&Falkenweg&15^^Dresden-Neustadt^^01099^DEU^H~^^Chemnitz^^^DEU^N||^PRN^PH^^49^351^7823456~^PRN^FX^^49^351^7823457|^WPN^PH^^49^351^9182736||M|CAT||||||Diakonissenkrankenhaus Dresden|||DEU|Bühnentechniker|DEU
NK1|1|Wendt^Wërner|FTH|||||||||||M|M|19540108|||DEU|DEU|||||CAT
PV1|1|I|IN2^4^3^CHI^^^^6||||||||||||||||0712843^^^^VN^KIS^20240120|||||||||||||||||||||||||20240120
PV2|||||||||20240402
```

## 9. ADT^A08 - Patient update, samedi HL7gateway to iMedOne (hl7gateway.samedi.de)

<!-- Source: https://hl7gateway.samedi.de/hl7gateway/messages/adt/ - samedi HL7gateway ADT documentation, outbound ADT^A08 -->

```
MSH|^~\&|samedi-hl7gateway|samedi|APPLICATION|CLINIC|20260403151846+0200||ADT^A08^ADT_A01|991765815154685352|P|2.5||||||UNICODE UTF-8
EVN|A08|202604031516+0200
PID|1|54321|qcë8bbf2b09^^^&www.praxis-öst.de&DNS^PI~54321^^^^PT||Klemm^Rübën^^^Prof.||19970226|M|||Albertstraße 24^^Dresden^^01067^DE||+49152 666 54321^^CP^^^^^^^^^+49152 666 54321~+49 351 666 789^^PH^^^^^^^^^+49 351 666 789~ëmail@dresdner-post.örg^NET^X.400^ëmail@dresdner-post.örg
PV1|1|U
```

## 10. ADT^A29 - Patient deletion, samedi HL7gateway (hl7gateway.samedi.de)

<!-- Source: https://hl7gateway.samedi.de/hl7gateway/messages/adt/ - samedi HL7gateway ADT documentation, outbound ADT^A29 -->

```
MSH|^~\&|samedi-hl7gateway|samedi|APPLICATION|CLINIC|20260403152323+0200||ADT^A29^ADT_A21|21471412864163822995|P|2.5||||||UNICODE UTF-8
EVN|A29|202604031523+0200
PID|1|77|r72f56c8b65^^^&www.praxis-öst.de&DNS^PI~77^^^^PT||Lëhner^Ërika||198510201
PV1|1|U
```

## 11. ADT^A08 - Inbound from KIS to samedi (hl7gateway.samedi.de)

<!-- Source: https://hl7gateway.samedi.de/hl7gateway/messages/adt/ - samedi HL7gateway, inbound ADT from hospital KIS -->

```
MSH|^~\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A08|2638170166537|P|2.5|9E62D52F8DE791B||AL|NE||8859/1
EVN|A08|202610260719
PID|1||4566^^^&www.praxis-öst.de&DNS^PI~287711^^^Rädvis^PI|20000052^^^DRË^PI|Noack^Hëide||19500524|F|||Hauptstraße 30&Hauptstraße 30^^Görlitz^^02826^DE^L||^^PH^^^^03581-7654321 Büro|^^PH
```

## 12. ADT^A40 - Patient merge (hl7gateway.samedi.de)

<!-- Source: https://hl7gateway.samedi.de/hl7gateway/messages/adt/ - samedi HL7gateway, ADT^A40 merge example -->

```
MSH|^~\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A40|2638170166537|P|2.5|9E62D52F8DE791B||AL|NE||8859/1
EVN|A40|202502041715
PID|1||4566^^^&www.praxis-öst.de&DNS^PI~287711^^^Rädvis^PI|20000052^^^DRË^PI|Noack^Hëide||19500524|F|||Hauptstraße 30&Hauptstraße 30^^Görlitz^^02826^DE^L||^^PH^^^^03581-7654321 Büro|^^PH
MRG|4567~u263401ef91^^^&www.praxis-öst.de&DNS~4467533^^^&1.2.276.0.76.3.1.660.1.1.1.2.1&ISO^PI|
```

## 13. SIU^S12 - New appointment booking, samedi to iMedOne (hl7gateway.samedi.de)

<!-- Source: https://hl7gateway.samedi.de/hl7gateway/messages/siu/ - samedi HL7gateway SIU documentation, outbound S12 -->

```
MSH|^~\&|samedi-hl7gateway|samedi|system|clinic|20260207130859+0100||SIU^S12^SIU_S12|8615615175374780398|P|2.5||||||UNICODE UTF-8
SCH||a-ëqcdl7hwscfuze4w||||BOOKED||1^MRT|1800||^^M30^20260516130000+0200^20260516133000+0200||||||||||||||Booked
TQ1|1||||||20260516130000+0200|20260516133000+0200|||||30^min
NTE||_default|Comment
NTE||Affected body parts|arm~left leg~head
NTE||Kommentar zum Patienten|patient comment, patient without external patient number
PID|1||s1299de4014^^^&www.praxis-öst.de&DNS^PI~^^^^PT||Pohl^Stëfan||19820511|M|||Wiener Straße 24^^Dresden^^01069^DE||+49 172 7654321^^CP^^^^^^^^^+49 172 7654321~+49 351 76543-210^^PH^^^^^^^^^+49 351 76543-210~pöst@dresdner-post.örg^NET^X.400^pöst@dresdner-post.örg~+49 351 76543-211^^FX^^^^^^^^^+49 351 76543-211
RGS|1|A
AIG|1|A|2^Stëfan Krebs^99SAMEDI-RESOURCE^radiologist|||||20260516130000+0200|||1800|s
AIG|2|A|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516130000+0200|||1800|s
```

## 14. SIU^S13 - Appointment rescheduling, samedi to iMedOne (hl7gateway.samedi.de)

<!-- Source: https://hl7gateway.samedi.de/hl7gateway/messages/siu/ - samedi HL7gateway SIU documentation, outbound S13 -->

```
MSH|^~\&|samedi-hl7gateway|samedi|system|clinic|20260207131000+0100||SIU^S13^SIU_S12|22310718558850378493|P|2.5||||||UNICODE UTF-8
SCH||a-ëqcdl7hwscfuze4w||||BOOKED||^Test|1800||^^M30^20260410135000+0200^20260410142000+0200||||||||||||||Booked
TQ1|1||||||20260410135000+0200|20260410142000+0200|||||30^min
RGS|1|D
AIG|1|D|1^Sprechzimmer^99SAMEDI-RESOURCE^c2|||||20260410125500+0200|||1800|s
RGS|2|A
AIG|2|A|2^Doc^99SAMEDI-RESOURCE^c1|||||20260410135000+0200|||1800|s
```

## 15. SIU^S14 - Appointment modification, samedi to iMedOne (hl7gateway.samedi.de)

<!-- Source: https://hl7gateway.samedi.de/hl7gateway/messages/siu/ - samedi HL7gateway SIU documentation, outbound S14 -->

```
MSH|^~\&|samedi-hl7gateway|samedi|system|clinic|20260207131202+0100||SIU^S14^SIU_S12|23267051019177332434|P|2.5||||||UNICODE UTF-8
SCH||a-ëqcdl7hwscfuze4w||||BOOKED||1^MRT|1800||^^M30^20260516140000+0200^20260516143000+0200||||||||||||||Booked
TQ1|1||||||20260516140000+0200|20260516143000+0200|||||30^min
NTE||_default|updated comment
NTE||Kommentar zum Patienten|patient comment, patient without external patient number
PID|1||s1299de4014^^^&www.praxis-öst.de&DNS^PI~^^^^PT||Pohl^Stëfan||19820511|M
RGS|1|X
AIG|1|X|2^Stëfan Krebs^99SAMEDI-RESOURCE^radiologist|||||20260516140000+0200|||1800|s
AIG|2|X|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516140000+0200|||1800|s
```

## 16. SIU^S15 - Appointment cancellation, samedi to iMedOne (hl7gateway.samedi.de)

<!-- Source: https://hl7gateway.samedi.de/hl7gateway/messages/siu/ - samedi HL7gateway SIU documentation, outbound S15 -->

```
MSH|^~\&|samedi-hl7gateway|samedi|system|clinic|20260207131507+0100||SIU^S15^SIU_S12|7374561721650221901|P|2.5||||||UNICODE UTF-8
SCH||a-ëqcdl7hwscfuze4w||||BOOKED||1^MRT|1800||^^M30^20260516140000+0200^20260516143000+0200||||||||||||||Deleted
TQ1|1||||||20260516140000+0200|20260516143000+0200|||||30^min
NTE||_default|updated comment
NTE||Kommentar zum Patienten|patient comment, patient without external patient number
PID|1||s1299de4014^^^&www.praxis-öst.de&DNS^PI~^^^^PT||Pohl^Stëfan||19820511|M
RGS|1|D
AIG|1|D|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516140000+0200|||1800|s
```

## 17. SIU^S12 - Appointment with external patient number (hl7gateway.samedi.de)

<!-- Source: https://hl7gateway.samedi.de/hl7gateway/messages/siu/ - samedi HL7gateway, patient with external KIS ID -->

```
MSH|^~\&|samedi-hl7gateway|samedi|system|clinic|20260207124406+0100||SIU^S12^SIU_S12|5027690727398224048|P|2.5||||||UNICODE UTF-8
SCH||b-ëqcdl7hwscfuze4w||||BOOKED||1^MRT|1800||^^M30^20260516100000+0200^20260516103000+0200||||||||||||||Booked
TQ1|1||||||20260516100000+0200|20260516103000+0200|||||30^min
NTE||Kommentar zum Patienten|patient with an external patient ID
PID|1|54321|t4538ef9435^^^&www.praxis-öst.de&DNS^PI~54321^^^^PT||Zander^Ännelïese|||F
RGS|1|A
AIG|1|A|2^Stëfan Krebs^99SAMEDI-RESOURCE^radiologist|||||20260516100000+0200|||1800|s
AIG|2|A|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516100000+0200|||1800|
```

## 18. SIU^S12 - Inbound from KIS to samedi (hl7gateway.samedi.de)

<!-- Source: https://hl7gateway.samedi.de/hl7gateway/messages/siu/ - samedi HL7gateway, inbound SIU from hospital KIS -->

```
MSH|^~\&|system|clinic|samedi-hl7gateway|samedi|20260101000000||SIU^S12^SIU_S12|87654|P|2.5||||||8859/1
SCH||567890^system||||||Sprechstunde, Claudia Brandt|||||||||||||||||Booked
TQ1|1||||||202601150800|202601150830|||||30^min
PID|1|54321|t4538ef9435^^^&www.praxis-öst.de&DNS^PI~54321^^^^PT||Zander^Ännelïese|||F
RGS|1|A
AIL|1||room-1|||202601150800^YYYYLLDDHHMM|||30|min
AIP|1||radiologist|||202601150800^YYYYLLDDHHMM|||30|min
```

## 19. ADT^A01 - E-ConsentPro / Thieme Compliance (support.thieme-compliance.de)

<!-- Source: https://support.thieme-compliance.de/de/ECP/Admin/hl7_adt-nachrichten.html - Thieme E-ConsentPro HL7 ADT documentation -->

```
MSH|^~\&|||||20260912142642||ADT^A01^ADT_A01|MSG00001|P|2.6|
EVN|A01|20260912142642||
PID|0||123456789^^^PVS1||Hagedorn^Sïlke||19670714|F|||Strehlener Str. 789^^Dresden^^01069||0351/54321-0~^NET^Internet^silke.hagedorn@dresdnerpost.com~0351/65432109^^CP
PV1||I|||||||||||||||||8523|
IN1|1|0|BKV2|AOK PLUS SACHSEN|||||||||||||||||||||||||||||||||||||||||||||49
```

## 20. ADT^A02 - Transfer, E-ConsentPro / Thieme Compliance (support.thieme-compliance.de)

<!-- Source: https://support.thieme-compliance.de/de/ECP/Admin/hl7_adt-nachrichten.html - Thieme E-ConsentPro HL7 ADT documentation, A02 -->

```
MSH|^~\&|||||20260912142642||ADT^A02^ADT_A02|MSG00001|P|2.6|
EVN|A02|20260912142642||
PID|0||123456789^^^PVS1||Hagedorn^Sïlke||19670714|F|||Strehlener Str. 789^^Dresden^^01069||0351/54321-0~^NET^X.400^silke.hagedorn@dresdnerpost.com~0351/65432109^^CP
PV1||I|neüStation^neüZimmer^neüBett|||ältStation^ältZimmer^ältBett|0100^GÖTZ,HËINZ|0148^GÖTZ,MÄJA ES||SUR|||||||0148^GÖTZ,HËINZ|S|2800|A|||||||||||||||||||GËNKRH||||||
```
