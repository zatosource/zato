# Nexus/KIS (Nexus AG) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Admission (standard)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202612151705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/15|DEU^German^HL70296^^deutsch||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO
EVN||202612151705||||202612151645
PID|||4567890^^^Kiefern-Klinik^PI||Adler^Gërtrüd^^^^^L^A^^^G~Steinmëtz^^^^^^M^A^^^G~Adler^^^^Frau^^D^^^^G||19890214|F|||Möwenweg 17&Möwenweg&17^^Bremen^^28195^^H~Störchgasse 3&Störchgasse&3^^Bremen^^28195^^BDL||^PRN^PH^^49^421^2468013^^^^^0421/2468013|^WPN^PH^^49^421^7913^024^^^^0421/7913-024|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Drëifaltigkeits-Hospital|||DEU^German^HL70171^^deutsch
PV1|1|I|CHI^302^2^IN^^N^A^4|R|||160801^Groß^Bernhard^^^Dr.^^^Kiefern-Klinik^L^^^DN^^^DN^^G||||||||||||7539^^^Kiefern-Klinik^VN|||||||||||||||||||||||||202612151645
PV2|||||||||20250405|4
ZBE|9012^KIS|202612151705||INSERT
```

## 2. ADT^A01 - Admission for DRG

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.39^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011705||||022604011645
PID|||98765^^^Kiefern-Klinik^PI||Thieme^Hëdwïg^^^^^L^A^^^G~Wëtzel^^^^^^M^A^^^G||19870721|F|||Möwenweg 17&Möwenweg&17^^Bremen^^^^H~Störchgasse 3&Störchgasse&3^^Bremen^^^^BDL||^PRN^PH^^49^421^2468013^^^^^0421/2468013|^WPN^PH^^49^421^7913^024^^^^0421/7913-024|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Drëifaltigkeits-Hospital|||DEU^^HL70171
PV1|1|I|URO^301^1^IN^^N^A^4|R|||160803^Langer^Bernhard^^^Dr.^^^Kiefern-Klinik^L^^^DN|160805^Huber^Haribert^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|7539^^^Kiefern-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||0101^vollstationär, Normalfall^GSG0001||||||20260405|4||||||||||||||||||||||||||N|N
ZBE|9012^KIS|202604011705||INSERT
```

## 3. ADT^A01 - Admission for billing (Abrechnung)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202606051705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.40^^2.16.840.1.113883.2.6^ISO
EVN||202606051705||||022606051645
PID|||98765^^^Fichten-Krankenhaus^PI||Füchs^Wërnër^^^Dr.^^L^A^^^G~Füchs^Wërnër^^^Herr Dr.^^D^A^^^G||19760508|F|||Schlösslestr. 29&Schlösslestr.&29^^Dortmund^^44135^^H||^PRN^PH^^49^231^5794016^^^^^0231/5794016|^WPN^PH^^49^231^83127^^^^^0231/83127|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Drëifaltigkeits-Hospital|||DEU^^HL70171
PV1|1|I|HNO^201^2^IN^^N^A^4|R|||160803^Langer^Bernhard^^^Dr.^^^Fichten-Krankenhaus^L^^^^^^DN ||||||||||||248163^^^Fichten-Krankenhaus^VN|01100000||||C|200301|||||||||||||||||||202606051645
PV2|||||||||20260615|10
ZBE|72839^KIS|202606051705||INSERT
```

## 4. ACK^A01 - Acknowledgment for admission

```
MSH|^~\&|RIS||KIS||202604011706||ACK^A01^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.9^^2.16.840.1.113883.2.6^ISO
SFT|RIS System GmbH^L|3.4|superRIS
MSA|CA|ADT001
```

## 5. ADT^A02 - Transfer (standard)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.44^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||98765^^^Kiefern-Klinik^PI||Thieme^Hëdwïg^^^^^L^A^^^G~Wëtzel^^^^^^M^A^^^G||19870721|F|||Möwenweg 17&Möwenweg&17^^Bremen^^^^H~Störchgasse 3&Störchgasse&3^^Bremen^^^^BDL||^PRN^PH^^49^421^2468013^^^^^0421/2468013|^WPN^PH^^49^421^7913^024^^^^0421/7913-024|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Drëifaltigkeits-Hospital|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|160809^Langer^Bernhard^^^Dr.^^^Kiefern-Klinik^L^^^DN||||||||||||7539^^^Kiefern-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4
ZBE|3456^KIS|202604011935||INSERT
```

## 6. ADT^A02 - Transfer for DRG

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.45^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||98765^^^Kiefern-Klinik^PI||Thieme^Hëdwïg^^^^^L^A^^^G~Wëtzel^^^^^^M^A^^^G||19870721|F|||Möwenweg 17&Möwenweg&17^^Bremen^^^^H~Störchgasse 3&Störchgasse&3^^Bremen^^^^BDL||^PRN^PH^^49^421^2468013^^^^^0421/2468013|^WPN^PH^^49^421^7913^024^^^^0421/7913-024|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Drëifaltigkeits-Hospital|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||7539^^^Kiefern-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260406|5||||||||||||||||||||||||||N|N
ZBE|3456^KIS|202604011935||INSERT
```

## 7. ACK^A02 - Acknowledgment for transfer

```
MSH|^~\&|RIS|ADT|KIS|ADT|202604011706||ACK^A02^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.4^^2.16.840.1.113883.2.6^ISO
MSA|CA|ADT002
```

## 8. ADT^A03 - Discharge (standard)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.47^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202504011705||||202504011645
PID|||98765^^^Kiefern-Klinik^PI||Thieme^Hëdwïg^^^^^L^A^^^G~Wëtzel^^^^^^M^A^^^G||19870721|F|||Möwenweg 17&Möwenweg&17^^Bremen^^^^H~Störchgasse 3&Störchgasse&3^^Bremen^^^^BDL||^PRN^PH^^49^421^2468013^^^^^0421/2468013|^WPN^PH^^49^421^7913^024^^^^0421/7913-024|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Drëifaltigkeits-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||160807^Langer^Bernhard^^^Dr.^^^Kiefern-Klinik^L^^^DN^^^DN ||||||||||||7539^^^Kiefern-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
ZBE|9012^KIS|202504011705||REFERENCE
```

## 9. ADT^A03 - Discharge for DRG

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.48^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||98765^^^Kiefern-Klinik^PI||neben dem Fluss&neben dem&Fluss^Dïëtrich^^^^^L^A^^^G||19780326|M|||Möwenweg 17&Möwenweg&17^^Bremen^^^^H~Störchgasse 3&Störchgasse&3^^Bremen^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Drëifaltigkeits-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||7539^^^Kiefern-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2|||0102^vollstationär, Arbeitsunfall^GSG0001|||||||4|4|||||||||||||||||||||||||N|N
ZBE|9012^KIS|202504011705||REFERENCE
```

## 10. ADT^A03 - Discharge for billing (Abrechnung)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.49^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||98765^^^Kiefern-Klinik^PI||neben dem Fluss&neben dem&Fluss^Dïëtrich^^^^^L^A^^^G||19780326|M|||Möwenweg 17&Möwenweg&17^^Bremen^^^^H~Störchgasse 3&Störchgasse&3^^Bremen^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Drëifaltigkeits-Hospital|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||7539^^^Kiefern-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2||||||||||||||||||||||||||||||||||||N|N
ZBE|9012^KIS|202504011705||REFERENCE
```

## 11. ACK^A03 - Acknowledgment for discharge

```
MSH|^~\&|RIS|ADT|KIS|ADT|202504011706||ACK^A03^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.15^^2.16.840.1.113883.2.6^ISO|
SFT|KIS System GmbH^L|5.0|A1|
MSA|CA|ADT001|
```

## 12. ADT^A08 - Patient data update (standard)

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A08^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.20^^2.16.840.1.113883.2.6^ISO
EVN||202604011705||||202604011645
PID|||98765^^^Kiefern-Klinik^PI||Thieme^Hëdwïg^^^^^L^A^^^G~Wëtzel^^^^^^B^A^^^G||19870721|F|||Möwenweg 17&Möwenweg&17^^Bremen^^^^H~Störchgasse 3&Störchgasse&3^^Bremen^^^^BDL||^PRN^PH^^49^421^2468013^^^^^0421/2468013|^WPN^PH^^49^421^7913^024^^^^0421/7913-024|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Drëifaltigkeits- Hospital|||DEU^^HL70171
PV1|1|I|CHI^202^1^CH^^N^C^4|R|||160811^Langer^Bernhard^^^Dr.^^^Kiefern-Klinik^L^^^DN||||||||||||7539^^^Kiefern-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4
ZBE|9012^KIS|202604011705||REFERENCE
```

## 13. ADT^A08 - Patient data update for DRG

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A08^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.21^^2.16.840.1.113883.2.6^ISO
EVN||202604011705||||202504011645
PID|||98765^^^Kiefern-Klinik^PI||zwischen den Brücken&zwischen den&Brücken^Hërïbert^^^^^L^A^^^G~zwischen den Brücken&zwischen den&Brücken^Hërïbërt^^^^^M^A^^^G~zwischen den Brücken&zwischen den&Brücken^Hërïbert^^^Herr^^D^A^^^G||19870721|M|||Köllnische Str. 31&Köllnische Str.&31^^Wiesbaden^XA-DE-HE^65183^DEU^H~Büchnerweg 18&Büchnerweg&18^^Göttingen^^37073^DEU^BDL||^PRN^PH^^49^611^3579024^^^^^0611/3579024|^WPN^PH^^49^611^8642^135^^^^0611/8642-135|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Drëifaltigkeits-Hospital|||DEU^^HL70171
PV1|1|I|IN2^202^1^IN^^N^C^4|R|||160811^Langer^Bernhard^^^Dr.^^^Kiefern-Klinik^L^^^DN|160809^^^^^^^^Kiefern-Klinik^^^^DN|||||R||||||8765567^^^Kiefern-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4|||||||||||||||||||||||||||N
ZBE|9012^KIS|202604011705||REFERENCE
```

## 14. ADT^A11 - Cancel admission

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A11^ADT_A09|ADT021|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.41^^2.16.840.1.113883.2.6^ISO
EVN||202604011705||||202604011645
PID|||98765^^^Kiefern-Klinik^PI||Thieme^Hëdwïg^^^^^L^A^^^G||19870721|F|||Möwenweg 17&Möwenweg&17^^Bremen^^^^H~Störchgasse 3&Störchgasse&3^^Bremen^^^^BDL||^PRN^PH^^49^421^2468013^^^^^0421/2468013|^WPN^PH^^49^421^7913^024^^^^0421/7913-024|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Drëifaltigkeits-Hospital|||DEU^^HL70171
PV1|1|I|CHI^202^1^CH^^N^C^4|R|||||||||||||||7539^^^Kiefern-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4|||||||||||||||||||||||||||||||||||||20260403
ZBE|4444444^KIS|202604011705||DELETE
```

## 15. ADT^A47 - Change patient identifier

```
MSH|^~\&|KIS|ADT|RIS|ADT|202603011935||ADT^A47^ADT_A30|ADT002|P|2.5^DEU|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.57^^2.16.840.1.113883.2.6^ISO
EVN||202603011935||||202603011645
PID|2||GHÏJKL^^^Kiefern-Klinik^PI||Thieme^Hëdwïg^^^^^L^A^^^G||19870721|F|||Möwenweg 17&Möwenweg&17^^Bremen^^^^H~Störchgasse 3&Störchgasse&3^^Bremen^^^^BDL||^PRN^PH^^49^421^2468013^^^^^0421/2468013|^WPN^PH^^49^421^7913^024^^^^0421/7913-024|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Drëifaltigkeits-Hospital|||DEU^^HL70171
MRG|98765^^^Kiefern-Klinik^PI|
```

## 16. ADT^A40 - Merge patient records

```
MSH|^~\&|KIS|ADT|RIS|ADT|202603011935||ADT^A40^ADT_A39|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.73^^2.16.840.1.113883.2.6^ISO
EVN||202603011935||||202603011645
PID|1||GHÏJKL^^^Kiefern-Klinik^PI ||Thieme^Hëdwïg^^^^^L^A^^^G||19870721|F|||Möwenweg 17&Möwenweg&17^^Bremen^^^^H~Störchgasse 3&Störchgasse&3^^Bremen^^^^BDL||^PRN^PH^^49^421^2468013^^^^^0421/2468013|^WPN^PH^^49^421^7913^024^^^^0421/7913-024|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Drëifaltigkeits-Hospital|||DEU^^HL70171
MRG|98765^^^Kiefern-Klinik^PI
```

## 17. BAR^P12 - Diagnosis update with ICD-10

```
MSH|^~\&|KIS|ADT|LAB|ADT|202610141345||BAR^P12^BAR_P12|ADT03|P|2.5^DEU&&HL70399|||AL|NE||8859/1|||2.16.840.1.113883.2.6.9.66^^2.16.840.1.113883.2.6^ISO
EVN||202610141345
PID|||756413^^^KIS^PI||Bölling^Ëdmünd^^^^^L||19590820|M|||Mëisenweg 9&Mëisenweg&9^^Würzburg^XA-DE-BY^97070^DEU^H
PV1||I|CHI^202^2^CH^^N||||||||||||||||765436^^^KIS^VN||||||||||||||||000000|||||||||202610091820
ZBE|678912^KIS|202610121230||REFERENCE
DG1|1||K35.-^Akute Appendizitis^I10-2005||202610141345|ED|||||||||1.1|160801^^^^^^^^^^^^DN||||67890^KIS|A
DG1|2||K35.-^Akute Appendizitis^I10-2005||202610141345|AD|||||||||1.2|160801^^^^^^^^^^^^DN||||67891^KIS|A
DG1|3||K35.0^Akute Appendizitis mit diffuser Peritonitis^I10-2005||202610141345|BD|||||||||1.2|160801^^^^^^^^^^^^DN||||67892^KIS|A
```

## 18. BAR^P12 - Procedure update with OPS codes

```
MSH|^~\&|KIS|ADT|LAB|ADT|202610141345||BAR^P12^BAR_P12|ADT03|P|2.5^DEU&&HL70399|||AL|NE||8859/1|||2.16.840.1.113883.2.6.9.66^^2.16.840.1.113883.2.6^ISO
SFT|KIS Hersteller GmbH^L|5.4.0|KIS System A
EVN||202610141345
PID|||756413^^^KIS^PI||Bölling^Ëdmünd^^^^^L||19590820|M|||Mëisenweg 9&Mëisenweg&9^^Würzburg^XA-DE-BY^97070^DEU^H
PV1|1|I|CHI^202^2^CH^^N||||||||||||||||765436^^^KIS^VN|||||||||||||||||||||||||2026100510
ZBE|789123|20261013||REFERENCE
PR1|1||8-901^Inhalationsanästhesie^O301-2005||202610141415||120|||||||1|||||78656^KIS|A
PR1|2||5-470.0^Appendektomie, offen chirurgisch^O301-2005||202610141415||90|||||||2|||||78657^KIS|A
```

## 19. MDM^T02 - Document notification with content

```
MSH|^~\&|HOSPAT|ADT|DATAGATE|ADT|20260516180000||MDM^T02^MDM_T02|102000|D|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|||2.16.840.1.113883.2.6.9.69^^2.16.840.1.1.13883.2.6^ISO
EVN||20260516180000
PID|||409000837^^^Zedern-Klinikum^PI||Steinbach^Güntër^^^^^L ||19740817|M|||Fëldweg 13^^Garmisch^^82467^DEU^H|08821349|08821-6398745|08023-481|DEU||EVC||||||Augsburg|||D
PV1||I|C1^^^CH|N|9705582||||||||||||||9705582^^^Zedern-Klinikum^VN ||K|||||||||||||||E|||6734|||||20260222155500|20261113174000|||518||9705582
TXA|1|CN|application/word|||20260516142700|20260516142700||||nïederli|90785||||90785.doc^HOSPAT|DI
OBX|1|ED|^Document Content|1|^text/plain^^Base64^VGhpcyBpcyBhbiBleGFtcGxlIERvY3VtZW50Lg==||||||F
```

## 20. MDM^T01 - Document notification (pathology request, ORBIS KIS)

```
MSH|^~\&|ORBIS|TEST KH 01|RECAPP|TEST KH 01|202511261036||MDM^T01^MDM_T01|167912|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DE||2.16.840.1.113883.2.6.9.70^^2.16.840.1.1.13883.2.6^ISO
EVN||202511261036|202511261036|
PID|1||520897^^^Zedern-Klinikum^PI ||Naumann^Hëinrïch^^^^^L ||19330615|M|||Römerstr. 6^^Mainz^^55116^DEU^H|||||||||||||||D||
PV1|1|I|ST02^^^ABT01^^1974|01^Normalfall^301||^^^^^||||N||||||N|||3821196^^^Zedern-Klinikum^VN |||||||||||||||||||2400||||||202601101000||
TXA|1|Anforderung Pathologie|application/pdf|||||20251126103606||||896021^ORBIS PRIMITIVUMNUMMER||KLTSTS900008196798^MEDIS_KLTSTS90|PATH-2025-004563^ORBIS AUFTRAGSNUMMER|3204630_5098575_896021_20251126103606.PDF^ORBIS|AU|||||||
```

## 21. ORU^R01 - Clinical observations (DETECT/COPRA, Dresden University Hospital)

```
MSH|^~\&|COPRAdetectapi|001|detectserver||||ORU^R01||P|2.5|||AL|NE|DE|8859/1|||2.16.840.1
PID|1|8901||76543219
PV1|1||SC110|
OBX|1|NM|RASS||-4|||||||||202601010600
OBX|2|ST|PupilleLinks||e+k|||||||||202612301330
OBX|3|ST|PupilleRechts||e+k|||||||||202601010600
```

## 22. MDM^T02 - Document notification (cardiology transfer report)

```
MSH|^~\&|CARDDAS|HZL|DOC|ADT|20260524163405||MDM^T02^MDM_T02|123456|T|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|||v70^^2.16.840.1.1.13883.2.6^ISO
EVN||20260524163405|||||B1
PID|||82695^^^Zedern-Klinikum^PI ||Krebs^Frïëdrich^^^^^L
PV1|||||||||||||||||||62459867^^^Zedern-Klinikum^VN |||||||||||||||||||||||||20250805
TXA||transferReport|text/plain|||20250806|||59764563^Weidner^Ërnëst^^^Dr.^^^^^^^L^HZL|||9174093646^^37459732765491768364593264738293^SHA-1||||Bërïcht01.txt^CARDDAS|AU|U|AV|||^Hecht^Wölfram^^^Prof.^^^^^^^L^HZL^20250807200200
OBX|1|ED|^Document Content|1|^text/plain^^Base64^VGhpcyBpcyBhbiBleGFtcGxlIERvY3VtZW50Lg==||||||F
```

## 23. MDM^T02 - samedi HL7 Gateway (clinic scheduling system)

```
MSH|^~\&|system|clinic|hl7gateway|samedi|2026082011223344||MDM^T02^MDM_T02|16|P|2.5|||NE|AL||||
EVN|T02|2026082011223344||||
PID|1||pät234567||Lindner^Sëbastïan||19810916|M
PV1|1|I|
TXA|1|samediDefaultType|AP|20260801120000||20260802120000|20260803120000|||||döc7891345||||bërïcht.pdf|AU||AV||||||Dökumënt Bëtrëff
OBX|1|ED|||^application/pdf^^Base64^aGVsbG8gd29ybGQ=
```

## 24. MSH segment example (Segment_MSH reference)

```
MSH|^~\&|SUBx||PAT||20250328112408||ADT^A01^ADT_A01|47|P|2.5|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.1^^2.16.840.1.113883.2.6^ISO
```
