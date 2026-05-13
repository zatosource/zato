# i.s.h.med (Oracle Cerner / SAP IS-H) - real HL7v2 ER7 messages

---

## ADT messages (Admission / Discharge / Transfer)

<!-- Source: wiki.hl7.de - HL7v2-Profile Aufnahme (ADT A01 Standardnachricht)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme
     Profile OID: 2.16.840.1.113883.2.6.9.38 -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202612151705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/15|DEU^German^HL70296^^deutsch||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO
EVN||202612151705||||202612151645
PID|||9876543^^^Ahorn-Klinik^PI||Richter^Ëlfrïede^^^^^L^A^^^G~Steinmetz^^^^^^M^A^^^G~Richter^^^^Frau^^D^^^^G||19860314|F|||Bonner Talweg 22&Bonner Talweg&22^^Bonn^^53111^^H~Platanenstr. 5&Platanenstr.&5^^Bonn^^53111^^BDL||^PRN^PH^^49^228^3579246^^^^^0228/3579246|^WPN^PH^^49^228^8024^613^^^^0228/8024-613|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Johanniter-Krankenhaus Bonn|||DEU^German^HL70171^^deutsch
PV1|1|I|CHI^302^2^IN^^N^A^4|R|||730501^Groß^Bernhard^^^Dr.^^^Ahorn-Klinik^L^^^DN^^^DN^^G||||||||||||6284^^^Ahorn-Klinik^VN|||||||||||||||||||||||||202612151645
PV2|||||||||20250405|4
ZBE|6789^KIS|202612151705||INSERT
```

<!-- Source: wiki.hl7.de - HL7v2-Profile Aufnahme (ADT A01 DRG-Nachricht)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme
     Profile OID: 2.16.840.1.113883.2.6.9.39 (DRG) -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.39^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011705||||020604011645
PID|||56789^^^Ahorn-Klinik^PI||Hartmann^Gïsëla^^^^^L^A^^^G~Wëißmüller^^^^^^M^A^^^G||19840918|F|||Bonner Talweg 22&Bonner Talweg&22^^Bonn^^^^H~Platanenstr. 5&Platanenstr.&5^^Bonn^^^^BDL||^PRN^PH^^49^228^3579246^^^^^0228/3579246|^WPN^PH^^49^228^8024^613^^^^0228/8024-613|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Johanniter-Krankenhaus Bonn|||DEU^^HL70171
PV1|1|I|URO^301^1^IN^^N^A^4|R|||730503^Langer^Bernhard^^^Dr.^^^Ahorn-Klinik^L^^^DN|730505^Huber^Haribert^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|6284^^^Ahorn-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||0101^vollstationär, Normalfall^GSG0001||||||20260405|4||||||||||||||||||||||||||N|N
ZBE|6789^KIS|202604011705||INSERT
```

<!-- Source: wiki.hl7.de - HL7v2-Profile Aufnahme (ADT A01 Abrechnung)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme
     Profile OID: 2.16.840.1.113883.2.6.9.40 (Abrechnung) -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202606051705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.40^^2.16.840.1.113883.2.6^ISO
EVN||202606051705||||020606051645
PID|||56789^^^Buchen-Krankenhaus^PI||Thürmann^Ëberhard^^^Dr.^^L^A^^^G~Thürmann^Ëberhard^^^Herr Dr.^^D^A^^^G||19730507|F|||Burgstr. 37&Burgstr.&37^^Essen^^45127^^H||^PRN^PH^^49^201^5794682^^^^^0201/5794682|^WPN^PH^^49^201^86243^^^^^0201/86243|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Johanniter-Krankenhaus Bonn|||DEU^^HL70171
PV1|1|I|HNO^201^2^IN^^N^A^4|R|||730503^Langer^Bernhard^^^Dr.^^^Buchen-Krankenhaus^L^^^^^^DN ||||||||||||837261^^^Buchen-Krankenhaus^VN|01100000||||C|202401|||||||||||||||||||202606051645
PV2|||||||||20260615|10
ZBE|93715^KIS|202606051705||INSERT
```

<!-- Source: wiki.hl7.de - HL7v2-Profile Aufnahme (ACK transport acknowledgment)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme
     Profile OID: 2.16.840.1.113883.2.6.9.9 -->

```
MSH|^~\&|RIS||KIS||202604011706||ACK^A01^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.9^^2.16.840.1.113883.2.6^ISO
SFT|RIS System GmbH^L|3.4|superRIS
MSA|CA|ADT001
```

<!-- Source: wiki.hl7.de - HL7v2-Profile Verlegung (ADT A02 Standard)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Verlegung
     Profile OID: 2.16.840.1.113883.2.6.9.44 -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.44^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||56789^^^Ahorn-Klinik^PI||Hartmann^Gïsëla^^^^^L^A^^^G~Wëißmüller^^^^^^M^A^^^G||19840918|F|||Bonner Talweg 22&Bonner Talweg&22^^Bonn^^^^H~Platanenstr. 5&Platanenstr.&5^^Bonn^^^^BDL||^PRN^PH^^49^228^3579246^^^^^0228/3579246|^WPN^PH^^49^228^8024^613^^^^0228/8024-613|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Johanniter-Krankenhaus Bonn|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|730509^Langer^Bernhard^^^Dr.^^^Ahorn-Klinik^L^^^DN||||||||||||6284^^^Ahorn-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4
ZBE|2345^KIS|202604011935||INSERT
```

<!-- Source: wiki.hl7.de - HL7v2-Profile Verlegung (ADT A02 DRG)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Verlegung
     Profile OID: 2.16.840.1.113883.2.6.9.45 -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.45^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||56789^^^Ahorn-Klinik^PI||Hartmann^Gïsëla^^^^^L^A^^^G~Wëißmüller^^^^^^M^A^^^G||19840918|F|||Bonner Talweg 22&Bonner Talweg&22^^Bonn^^^^H~Platanenstr. 5&Platanenstr.&5^^Bonn^^^^BDL||^PRN^PH^^49^228^3579246^^^^^0228/3579246|^WPN^PH^^49^228^8024^613^^^^0228/8024-613|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Johanniter-Krankenhaus Bonn|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||6284^^^Ahorn-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260406|5||||||||||||||||||||||||||N|N
ZBE|2345^KIS|202604011935||INSERT
```

<!-- Source: wiki.hl7.de - HL7v2-Profile Entlassung (ADT A03 Standard)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Entlassung
     Profile OID: 2.16.840.1.113883.2.6.9.47 -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.47^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202504011705||||202504011645
PID|||56789^^^Ahorn-Klinik^PI||Hartmann^Gïsëla^^^^^L^A^^^G~Wëißmüller^^^^^^M^A^^^G||19840918|F|||Bonner Talweg 22&Bonner Talweg&22^^Bonn^^^^H~Platanenstr. 5&Platanenstr.&5^^Bonn^^^^BDL||^PRN^PH^^49^228^3579246^^^^^0228/3579246|^WPN^PH^^49^228^8024^613^^^^0228/8024-613|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Johanniter-Krankenhaus Bonn|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||730507^Langer^Bernhard^^^Dr.^^^Ahorn-Klinik^L^^^DN^^^DN ||||||||||||6284^^^Ahorn-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
ZBE|6789^KIS|202504011705||REFERENCE
```

<!-- Source: wiki.hl7.de - HL7v2-Profile Entlassung (ADT A03 DRG)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Entlassung
     Profile OID: 2.16.840.1.113883.2.6.9.48 -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.48^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||56789^^^Ahorn-Klinik^PI||über dem Stein&über dem&Stein^Fëlix^^^^^L^A^^^G||19750123|M|||Bonner Talweg 22&Bonner Talweg&22^^Bonn^^^^H~Platanenstr.  5&Platanenstr.&5^^Bonn^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Johanniter-Krankenhaus Bonn|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||6284^^^Ahorn-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2|||0102^vollstationär, Arbeitsunfall^GSG0001|||||||4|4|||||||||||||||||||||||||N|N
ZBE|6789^KIS|202504011705||REFERENCE
```

<!-- Source: wiki.hl7.de - HL7v2-Profile Besuchsmeldung (ADT A04 ambulant)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Besuchsmeldung
     Profile OID: 2.16.840.1.113883.2.6.9.51 -->

```
MSH|^~\&|KIS|ADT|KIS|ADT|202604011705||ADT^A04^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011705||||202604011645
PID|||56789^^^Ahorn-Klinik^PI||Hartmann^Gïsëla^^^^^L^A^^^G~Wëißmüller^^^^^^M^A^^^G||19840918|F|||Bonner Talweg 22&Bonner Talweg&22^^Bonn^^^^H~Platanenstr. 5&Platanenstr.&5^^Bonn^^^^BDL||^PRN^PH^^49^228^3579246^^^^^0228/3579246|^WPN^PH^^49^228^8024^613^^^^0228/8024-613|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Johanniter-Krankenhaus Bonn|||DEU^^HL70171
PV1|1|O|^^^AIN^^D^A^1|R|||||||||||||||6284^^^Ahorn-Klinik^VN|||||||||||||||||||||||||202604011645
ZBE|6789^KIS|202604011705||INSERT
```

<!-- Source: wiki.hl7.de - HL7v2-Profile Besuchsmeldung (ADT A04 vorstationaer)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Besuchsmeldung
     Profile OID: 2.16.840.1.113883.2.6.9.51 -->

```
MSH|^~\&|KIS|ADT|KIS|ADT|202604011705||ADT^A04^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO
EVN||202604011705|20260601|||202604011645
PID|||56789^^^Ahorn-Klinik^PI||Hartmann^Gïsëla^^^^^L^A^^^G~Wëißmüller^^^^^^M^A^^^G||19840918|F|||Bonner Talweg 22&Bonner Talweg&22^^Bonn^^^^H~Platanenstr. 5&Platanenstr.&5^^Bonn^^^^BDL||^PRN^PH^^49^228^3579246^^^^^0228/3579246|^WPN^PH^^49^228^8024^613^^^^0228/8024-613|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Johanniter-Krankenhaus Bonn|||DEU^^HL70171
PV1|1|I|IN1^^^CH^^N||||||||||||||||6284^^^Ahorn-Klinik^VN|||||||||||||||||||||||||202604011645
PV2||||||||20260601
ZBE|6789^KIS|202604011705||INSERT
```

<!-- Source: wiki.hl7.de - HL7v2-Profile Aufnahme Storno (ADT A11)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme_Storno
     Profile OID: 2.16.840.1.113883.2.6.9.41 -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A11^ADT_A09|ADT021|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.41^^2.16.840.1.113883.2.6^ISO
EVN||202604011705||||202604011645
PID|||56789^^^Ahorn-Klinik^PI||Hartmann^Gïsëla^^^^^L^A^^^G||19840918|F|||Bonner Talweg 22&Bonner Talweg&22^^Bonn^^^^H~Platanenstr. 5&Platanenstr.&5^^Bonn^^^^BDL||^PRN^PH^^49^228^3579246^^^^^0228/3579246|^WPN^PH^^49^228^8024^613^^^^0228/8024-613|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Johanniter-Krankenhaus Bonn|||DEU^^HL70171
PV1|1|I|CHI^202^1^CH^^N^C^4|R|||||||||||||||6284^^^Ahorn-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4|||||||||||||||||||||||||||||||||||||20260403
ZBE|3333333^KIS|202604011705||DELETE
```

---

## MDM messages (document management)

<!-- Source: wiki.hl7.de - HL7v2-Profile MDM-Nachrichten (MDM T02 with content)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_MDM-Nachrichten
     Profile OID: 2.16.840.1.113883.2.6.9.69 -->

```
MSH|^~\&|HOSPAT|ADT|DATAGATE|ADT|20260516180000||MDM^T02^MDM_T02|102000|D|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|||2.16.840.1.113883.2.6.9.69^^2.16.840.1.1.13883.2.6^ISO
EVN||20260516180000
PID|||308000917^^^Platanen-Klinikum^PI||Trinkwasser^Gëorg^^^^^L ||19710815|M|||Waldweg 7^^Rosenheim^^83022^DEU^H|08031649|08031-6298734|08024-382|DEU||EVC||||||Regensburg|||D
PV1||I|C1^^^CH|N|4809371||||||||||||||4809371^^^Platanen-Klinikum^VN ||K|||||||||||||||E|||8523|||||20260222155500|20261113174000|||716||4809371
TXA|1|CN|application/word|||20260516142700|20260516142700||||stöckli|89674||||89674.doc^HOSPAT|DI
OBX|1|ED|^Document Content|1|^text/plain^^Base64^VGhpcyBpcyBhbiBleGFtcGxlIERvY3VtZW50Lg==||||||F
```

<!-- Source: wiki.hl7.de - HL7v2-Profile MDM-Nachrichten (MDM T01 from ORBIS)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_MDM-Nachrichten
     Profile OID: 2.16.840.1.113883.2.6.9.70 -->

```
MSH|^~\&|ORBIS|TEST KH 01|RECAPP|TEST KH 01|202511261036||MDM^T01^MDM_T01|167912|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DE||2.16.840.1.113883.2.6.9.70^^2.16.840.1.1.13883.2.6^ISO
EVN||202511261036|202511261036|
PID|1||419853^^^Platanen-Klinikum^PI ||Öttinger^Frïtz^^^^^L ||19300609|M|||Möselstr. 8^^Koblenz^^56068^DEU^H|||||||||||||||D||
PV1|1|I|ST02^^^ABT01^^1974|01^Normalfall^301||^^^^^||||N||||||N|||3721186^^^Platanen-Klinikum^VN |||||||||||||||||||2400||||||202601101000||
TXA|1|Anforderung Pathologie|application/pdf|||||20251126103606||||794809^ORBIS PRIMITIVUMNUMMER||KLTSTS900005174698^MEDIS_KLTSTS90|PATH-2025-003452^ORBIS AUFTRAGSNUMMER|2193519_3987464_794809_20251126103606.PDF^ORBIS|AU|||||||
```

<!-- Source: wiki.hl7.de - HL7v2-Profile MDM-Nachrichten (MDM T01 from cardiology)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_MDM-Nachrichten
     Profile OID: 2.16.840.1.113883.2.6.9.70 -->

```
MSH|^~\&|CARDDAS|HZL|DOC|ADT|20260524163405||MDM^T01^MDM_T01|123456|T|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|||2.16.840.1.113883.2.6.9.70^^2.16.840.1.1.13883.2.6^ISO
EVN||20260524163405|||||B1
PID|||61584^^^Platanen-Klinikum^PI ||Bäuerle^Klëmens^^^^^L
PV1|||||||||||||||||||61348756^^^Platanen-Klinikum^VN |||||||||||||||||||||||||20250805
TXA||transferReport|application/pdf|||20250806|||48653452^Glückauf^Rüdïger^^^Dr.^^^^^^^L^HZL|||8063982535^^37459732765491768364593264738293^SHA-1||||8063982535.pdf^CARDDAS|AU|U|AV|||^Fürsting^Albrëcht^^^Prof.^^^^^^^L^HZL^20250807200200
```

<!-- Source: wiki.hl7.de - HL7v2-Profile MDM-Nachrichten (MDM T11 document cancel)
     URL: https://wiki.hl7.de/index.php/HL7v2-Profile_MDM-Nachrichten
     Profile OID: 2.16.840.1.113883.2.6.9.69 -->

```
MSH|^~\&|HOSPAT|ADT|DATAGATE|ADT|20260516190000||MDM^T11^MDM_T01|102001|D|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|||2.16.840.1.113883.2.6.9.69^^2.16.840.1.1.13883.2.6^ISO
EVN||20260516190000
PID|||308000917^^^Platanen-Klinikum^PI ||Trinkwasser^Gëorg^^^^^L ||19710815|M|||Waldweg 7^^Rosenheim^^83022^DEU^H|08031649|08031-6298734|08024-382|DEU||EVC||||||Regensburg|||D
PV1||I|C1^^^CH|N|4809371||||||||||||||4809371^^^Platanen-Klinikum^VN ||K|||||||||||||||E|||8523|||||20260222155500|20261113174000|||716||4809371
TXA|1|CN|application/word|||20260516142700|20260516142700|20260516170000|||stöckli|89674||||89674.doc^HOSPAT|AU
```

---

## DFT messages (billing / financial transaction)

<!-- Source: support.thieme-compliance.de - HL7-Nachrichtenstrukturen (DFT P03)
     URL: https://support.thieme-compliance.de/de/ECP/Admin/hl7-nachrichtenstrukturen.html
     System: E-ConsentPro (Thieme Compliance), used with KIS in German hospitals -->

```
MSH|^~\&|ECONSENTPRO|THIEME|KIS|KRANKENHAUS|20260110144021||DFT^P03|d7243dc43871036f|P|2.5|||AL|NE|DEU|UNICODE UTF-8
EVN|P03|20260110144018
PID|||20260315P00312||Hauser^Sïgrid||19940618|F|||Bergstr. 789^^Heidelberg^^69115||09876/54321-0
PV1|1|I|64^6405^3^URO|||||||||||||N|||20260315F00145|||||K||||||||||||||||||||20260110133524
FT1|1|20260315A00089|20260315A00089|20260110143954||CG|D-An1E^Narkose/Regionalanästhesie^com.thieme.ecp|||1||||||||||C000852447^Kemper^Hëiko^^^Dr. med.|||||D-An1E
```

---

## SIU messages (scheduling)

<!-- Source: hl7gateway.samedi.de - SIU messages (SIU S12 new appointment)
     URL: https://hl7gateway.samedi.de/hl7gateway/messages/siu
     System: samedi HL7gateway, used in German clinics -->

```
MSH|^~\&|samedi-hl7gateway|samedi|system|clinic|20260207130859+0100||SIU^S12^SIU_S12|9726726286485891509|P|2.5||||||UNICODE UTF-8
SCH||c-ërdel8ixteghaf5x||||BOOKED||1^MRT|1800||^^M30^20260516130000+0200^20260516133000+0200||||||||||||||Booked
TQ1|1||||||20260516130000+0200|20260516133000+0200|||||30^min
NTE||_default|Comment
NTE||Affected body parts|arm~left leg~head
NTE||Kommentar zum Patienten|patient comment, patient without external patient number
PID|1||y2199ef5015^^^&www.praxis-nörd.de&DNS^PI~^^^^PT||Kästner^Jöchen||19830817|M|||Glëisstraße 36^^Freiburg^^79098^DE||+49 173 8765432^^CP^^^^^^^^^+49 173 8765432~+49 228 87654-321^^PH^^^^^^^^^+49 228 87654-321~pöst@kästner.de^NET^X.400^pöst@kästner.de~+49 228 87654-322^^FX^^^^^^^^^+49 228 87654-322
RGS|1|A
AIG|1|A|2^Jöchen Brühl^99SAMEDI-RESOURCE^radiologist|||||20260516130000+0200|||1800|s
AIG|2|A|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516130000+0200|||1800|s
```

<!-- Source: hl7gateway.samedi.de - SIU messages (SIU S15 appointment cancellation)
     URL: https://hl7gateway.samedi.de/hl7gateway/messages/siu
     System: samedi HL7gateway -->

```
MSH|^~\&|samedi-hl7gateway|samedi|system|clinic|20260207131507+0100||SIU^S15^SIU_S12|8485672832761332012|P|2.5||||||UNICODE UTF-8
SCH||c-ërdel8ixteghaf5x||||BOOKED||1^MRT|1800||^^M30^20260516140000+0200^20260516143000+0200||||||||||||||Deleted
TQ1|1||||||20260516140000+0200|20260516143000+0200|||||30^min
NTE||_default|updated comment
NTE||Kommentar zum Patienten|patient comment, patient without external patient number
PID|1||y2199ef5015^^^&www.praxis-nörd.de&DNS^PI~^^^^PT||Kästner^Jöchen||19830817|M
RGS|1|D
AIG|1|D|1^Sprechzimmer^99SAMEDI-RESOURCE^room-1|||||20260516140000+0200|||1800|s
```

---

## ADT messages from KIS integration (samedi HL7gateway)

<!-- Source: hl7gateway.samedi.de - ADT messages (outbound A08)
     URL: https://hl7gateway.samedi.de/hl7gateway/messages/adt/
     System: samedi HL7gateway connected to KIS -->

```
MSH|^~\&|samedi-hl7gateway|samedi|APPLICATION|CLINIC|20260403151846+0200||ADT^A08^ADT_A01|002876815265796463|P|2.5||||||UNICODE UTF-8
EVN|A08|202604031516+0200
PID|1|56789|xdë9ccg3c10^^^&www.praxis-nörd.de&DNS^PI~56789^^^^PT||Feldkamp^Albërt^^^Prof.||19980306|M|||Straßënweg 36^^Städtchen^^65432^DE||+49153 777 65432^^CP^^^^^^^^^+49153 777 65432~+49 228 777 456^^PH^^^^^^^^^+49 228 777 456~ëmail@feldkamp.de^NET^X.400^ëmail@feldkamp.de
PV1|1|U
```

<!-- Source: hl7gateway.samedi.de - ADT messages (inbound A08 from KomServer)
     URL: https://hl7gateway.samedi.de/hl7gateway/messages/adt/
     System: KomServer (Kommunikationsserver) sending to samedi -->

```
MSH|^~\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A08|3749281277648|P|2.5|AF73E63G9EF802C||AL|NE||8859/1
EVN|A08|202610260719
PID|1||5677^^^&www.praxis-nörd.de&DNS^PI~398144^^^Rädvis^PI|30000078^^^KÖN^PI|Gerber^Hëidi||19510727|F|||Weender Str. 28&Weender Str. 28^^Göttingen^^37073^DE^L||^^PH^^^^0551-8765432 Büro|^^PH
```

<!-- Source: hl7gateway.samedi.de - ADT messages (A40 patient merge)
     URL: https://hl7gateway.samedi.de/hl7gateway/messages/adt/
     System: KomServer sending patient merge to samedi -->

```
MSH|^~\&|KomServer|KOMSERV|samedi-hl7gateway|samedi|20260523123517||ADT^A40|3749281277648|P|2.5|AF73E63G9EF802C||AL|NE||8859/1
EVN|A40|202502041715
PID|1||5677^^^&www.praxis-nörd.de&DNS^PI~398144^^^Rädvis^PI|30000078^^^KÖN^PI|Gerber^Hëidi||19510727|F|||Weender Str. 28&Weender Str. 28^^Göttingen^^37073^DE^L||^^PH^^^^0551-8765432 Büro|^^PH
MRG|5678~z374401fg02^^^&www.praxis-nörd.de&DNS~5568399^^^&1.2.276.0.76.3.1.660.1.1.1.2.1&ISO^PI|
```
