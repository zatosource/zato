# Cloverleaf (Infor / Enovation) - real HL7v2 ER7 messages

## 1. ADT^A01 - admission, standard (HL7-D profile v2.5)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202603151705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/15|DEU^German^HL70296^^deutsch||2.16.840.1.113883.2.6.9.38^^2.16.840.1.113883.2.6^ISO
EVN||202603151705||||202603151645
PID|||8901234^^^Ahorn-Klinik^PI||Hartmann^Monika^^^^^L^A^^^G~Schreiber^^^^^^M^A^^^G~Hartmann^^^^Frau^^D^^^^G||19860419|F|||Königstraße 6&Königstraße&6^^Stuttgart^^70173^^H~Silberburgstr. 21&Silberburgstr.&21^^Stuttgart^^70176^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^German^HL70296^^deutsch|M^married^HL70002^^verheiratet|CAT^catholic^HL70006^^katholisch||||||Katharinenhospital Stuttgart|||DEU^German^HL70171^^deutsch
PV1|1|I|CHI^302^2^IN^^N^A^4|R|||820301^Engel^Thëodor^^^Dr.^^^Ahorn-Klinik^L^^^DN^^^DN^^G||||||||||||2917^^^Ahorn-Klinik^VN|||||||||||||||||||||||||202603151645
PV2|||||||||20250405|4
ZBE|4567^KIS|202603151705||INSERT
```

## 2. ADT^A01 - admission with DRG (HL7-D profile v2.5)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.39^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011705||||022604011645
PID|||34567^^^Ahorn-Klinik^PI||Lorenz^Sïgrid^^^^^L^A^^^G~Hauser^^^^^^M^A^^^G||19810622|F|||Königstraße 6&Königstraße&6^^Stuttgart^^^^H~Silberburgstr. 21&Silberburgstr.&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Katharinenhospital Stuttgart|||DEU^^HL70171
PV1|1|I|URO^301^1^IN^^N^A^4|R|||820303^Pfeiffer^Frïedrich^^^Dr.^^^Ahorn-Klinik^L^^^DN|820311^Schuster^Wïlhelm^^^Dr.^^^^L^^^DN^^A^^^G|||||R|||||E|2917^^^Ahorn-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||0101^vollstationär, Normalfall^GSG0001||||||20260405|4||||||||||||||||||||||||||N|N
ZBE|4567^KIS|202604011705||INSERT
```

## 3. ACK^A01 - transport acknowledgment (HL7-D profile v2.5)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme -->

```
MSH|^~\&|RIS||KIS||202604011706||ACK^A01^ACK|RIS002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.9^^2.16.840.1.113883.2.6^ISO
SFT|RIS System GmbH^L|3.4|superRIS
MSA|CA|ADT001
```

## 4. ADT^A01 - admission with billing (HL7-D profile v2.5)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Aufnahme -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202606051705||ADT^A01^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.40^^2.16.840.1.113883.2.6^ISO
EVN||202606051705||||022606051645
PID|||34567^^^Buchen-Krankenhaus^PI||Franke^Bërndt^^^Dr.^^L^A^^^G~Franke^Bërndt^^^Herr Dr.^^D^A^^^G||19690117|F|||Rotebühlplatz 44&Rotebühlplatz&44^^Stuttgart^^70178^^H||^PRN^PH^^49^711^4681357^^^^^0711/4681357|^WPN^PH^^49^711^97531^^^^^0711/97531|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Katharinenhospital Stuttgart|||DEU^^HL70171
PV1|1|I|HNO^201^2^IN^^N^A^4|R|||820303^Pfeiffer^Frïedrich^^^Dr.^^^Buchen-Krankenhaus^L^^^^^^DN ||||||||||||418263^^^Buchen-Krankenhaus^VN|01100000||||C|202401|||||||||||||||||||202606051645
PV2|||||||||20260615|10
ZBE|71823^KIS|202606051705||INSERT
```

## 5. ADT^A03 - discharge, standard (HL7-D profile v2.5)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Entlassung -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.47^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202504011705||||202504011645
PID|||34567^^^Ahorn-Klinik^PI||Lorenz^Sïgrid^^^^^L^A^^^G~Hauser^^^^^^M^A^^^G||19810622|F|||Königstraße 6&Königstraße&6^^Stuttgart^^^^H~Silberburgstr. 21&Silberburgstr.&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Katharinenhospital Stuttgart|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||820309^Pfeiffer^Frïedrich^^^Dr.^^^Ahorn-Klinik^L^^^DN^^^DN ||||||||||||2917^^^Ahorn-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
ZBE|4567^KIS|202504011705||REFERENCE
```

## 6. ADT^A03 - discharge with DRG (HL7-D profile v2.5)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Entlassung -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.48^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||34567^^^Ahorn-Klinik^PI||am Weiher&am&Weiher^Tïlman^^^^^L^A^^^G||19710803|M|||Königstraße 6&Königstraße&6^^Stuttgart^^^^H~Silberburgstr.  21&Silberburgstr.&21^^Stuttgart^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Katharinenhospital Stuttgart|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||2917^^^Ahorn-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2|||0102^vollstationär, Arbeitsunfall^GSG0001|||||||4|4|||||||||||||||||||||||||N|N
ZBE|4567^KIS|202504011705||REFERENCE
```

## 7. ADT^A03 - discharge with billing (HL7-D profile v2.5)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Entlassung -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202504011705||ADT^A03^ADT_A03|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.49^^2.16.840.1.113883.2.6^ISO
EVN||202504011705||||202504011645
PID|||34567^^^Ahorn-Klinik^PI||am Weiher&am&Weiher^Tïlman^^^^^L^A^^^G||19710803|M|||Königstraße 6&Königstraße&6^^Stuttgart^^^^H~Silberburgstr. 21&Silberburgstr.&21^^Stuttgart^^^^BDL||||DEU^^HL70296|W^widowed^HL70002^^verwitwet|CAT^^HL70006||||||Katharinenhospital Stuttgart|||DEU^^HL70171
PV1|1|I|HNO^311^3^IN^^N^B^4|R|||||||||||||||2917^^^Ahorn-Klinik^VN|||||||||||||||||011||||||||202504011645|202504061100
PV2||||||||||||||||||||||||||||||||||||N|N
ZBE|4567^KIS|202504011705||REFERENCE
```

## 8. ADT^A02 - transfer, standard (HL7-D profile v2.5)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Verlegung -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A02^ADT_A02|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.44^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011935||||202604011645
PID|||34567^^^Ahorn-Klinik^PI||Lorenz^Sïgrid^^^^^L^A^^^G~Hauser^^^^^^M^A^^^G||19810622|F|||Königstraße 6&Königstraße&6^^Stuttgart^^^^H~Silberburgstr. 21&Silberburgstr.&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Katharinenhospital Stuttgart|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||2917^^^Ahorn-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4
ZBE|9012^KIS|202604011935||INSERT
```

## 9. ADT^A12 - cancel transfer (HL7-D profile v2.5)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Verlegung_Storno -->

```
MSH|^~\&|KIS|ADT|RIS|ADT|202604011935||ADT^A12^ADT_A12|ADT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.46^^2.16.840.1.113883.2.6^ISO
EVN||202604011935||||202604011645
PID|||34567^^^Ahorn-Klinik^PI||Lorenz^Sïgrid^^^^^L^A^^^G||19810622|F|||Königstraße 6&Königstraße&6^^Stuttgart^^^^H~Silberburgstr. 21&Silberburgstr.&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Katharinenhospital Stuttgart|||DEU^^HL70171
PV1|1|I|CHI^303^3^CH^^N^D^4|R||IN1^202^1^IN^^N^D^2|||||||||||||2917^^^Ahorn-Klinik^VN|||||||||||||||||||||||||202604011645
PV2|||||||||20260405|4
ZBE|9012^KIS|202604011935||DELETE
```

## 10. ADT^A04 - outpatient registration (HL7-D profile v2.5)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Besuchsmeldung -->

```
MSH|^~\&|KIS|ADT|KIS|ADT|202604011705||ADT^A04^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011705||||202604011645
PID|||34567^^^Ahorn-Klinik^PI||Lorenz^Sïgrid^^^^^L^A^^^G~Hauser^^^^^^M^A^^^G||19810622|F|||Königstraße 6&Königstraße&6^^Stuttgart^^^^H~Silberburgstr. 21&Silberburgstr.&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Katharinenhospital Stuttgart|||DEU^^HL70171
PV1|1|O|^^^AIN^^D^A^1|R|||||||||||||||2917^^^Ahorn-Klinik^VN|||||||||||||||||||||||||202604011645
ZBE|4567^KIS|202604011705||INSERT
```

## 11. ADT^A04 - pre-admission registration (HL7-D profile v2.5)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Besuchsmeldung -->

```
MSH|^~\&|KIS|ADT|KIS|ADT|202604011705||ADT^A04^ADT_A01|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.51^^2.16.840.1.113883.2.6^ISO
EVN||202604011705|20260601|||202604011645
PID|||34567^^^Ahorn-Klinik^PI||Lorenz^Sïgrid^^^^^L^A^^^G~Hauser^^^^^^M^A^^^G||19810622|F|||Königstraße 6&Königstraße&6^^Stuttgart^^^^H~Silberburgstr. 21&Silberburgstr.&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Katharinenhospital Stuttgart|||DEU^^HL70171
PV1|1|I|IN1^^^CH^^N||||||||||||||||2917^^^Ahorn-Klinik^VN|||||||||||||||||||||||||202604011645
PV2||||||||20260601
ZBE|4567^KIS|202604011705||INSERT
```

## 12. ADT^A31 - person update (HL7-D profile v2.5)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_Aenderung_Person -->

```
MSH|^~\&|KIS|ADT|LAB|ADT|202604011705||ADT^A31^ADT_A05|ADT001|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.55^^2.16.840.1.113883.2.6^ISO
SFT|KIS System GmbH^L|5.0|A1
EVN||202604011705||||202604011645
PID|||34567^^^Ahorn-Klinik^PI||Kurz^Rölf^^^^^L^A^^^G~Kurz^Rölfe^^^Herr^^D^A^^^G||19830915|M|||Königstraße 6&Königstraße&6^^Stuttgart^^^^H~Silberburgstr. 21&Silberburgstr.&21^^Stuttgart^^^^BDL||^PRN^PH^^49^711^2468135^^^^^0711/2468135|^WPN^PH^^49^711^9753^246^^^^0711/9753-246|DEU^^HL70296|M^married^HL70002|CAT^^HL70006||||||Katharinenhospital Stuttgart|||DEU^^HL70171
PV1|1|N
```

## 13. ADT^A08 - update with gestational age OBX (HL7-D DRG profile v2.5)

<!-- Source: http://wiki.hl7.de/index.php?title=HL7v2-Profilkomponente_DRG-Rohdaten -->

```
MSH|^~\&|KIS|ADT|LAB|ADT|202609201025||ADT^A08^ADT_A01|00013424|P|2.5^DEU&&HL70399|||AL|NE||8859/1|||2.16.840.1.113883.2.6.9.62^^2.16.840.1.113883.2.6^ISO~2.16.840.1.113883.2.6.9.52^^2.16.840.1.113883.2.6^ISO
EVN||202609201025
PID|||667812^^^KIS^PI||Seidel&&Seidel^Hëlga^^^^^L~Reuter&&Reuter^Hëlga^^^^^B||19780211|F|||||^PRN^PH^^49^711^4582716^^^^^0711/4582716||DEU^German^HL70296^deutsch|M^^HL70002|EVC^^HL70006|||||||Y|2
PV1|1|I|IN1^202^^IN^^N^A||||||||||||||||20267891^^^KIS^VN
OBX|1|NM|11884-4^Gestationsalter^LN||36||1-40|N|||F|||20260920
ZBE|812943|20260920||REFERENCE
```

## 14. ADT^A08 - update with diagnosis DG1 (HL7-D DRG profile v2.5)

<!-- Source: http://wiki.hl7.de/index.php?title=HL7v2-Profilkomponente_DRG-Rohdaten -->

```
MSH|^~\&|KIS|ADT|LAB|ADT|202609201025||ADT^A08^ADT_A01|00013424|P|2.5^DEU&&HL70399|||AL|NE||8859/1|||2.16.840.1.113883.2.6.9.62^^2.16.840.1.113883.2.6^ISO~2.16.840.1.113883.2.6.9.52^^2.16.840.1.113883.2.6^ISO
EVN||202609201025
PID|||667812^^^KIS^PI||Seidel&&Seidel^Hëlga^^^^^L||19780211|F|||||^PRN^PH^^49^711^4582716||DEU^^HL70296|M^^HL70002|EVC^^HL70006|||||||Y|2
PV1|1|I|IN1^202^^IN^^N^A||||||||||||||||202677891^^^KIS^VN|||||||||||||||||||||||||202609161815
DG1|1||P07.1^Neugeborenes mit sonstigem niedrigem Geburtsgewicht^I10-2004||20260920|BD|||||||||1|519834^Brandt&&Brandt^Löthar^^^Dr.^^^^L^^^DN||||518347291^KIS|A
ZBE|671238542^KIS|20260919||REFERENCE
```

## 15. MDM^T02 - document notification with content (HL7-D MDM profile v2.5)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_MDM-Nachrichten -->

```
MSH|^~\&|HOSPAT|ADT|DATAGATE|ADT|20260416180000||MDM^T02^MDM_T02|102000|D|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|||2.16.840.1.113883.2.6.9.69^^2.16.840.1.1.13883.2.6^ISO
EVN||20260416180000
PID|||205000418^^^Kiefer-Klinikum^PI||Dietrich^Gërd^^^^^L||19660514|M|||Herderstr. 11^^Ulm^^89073^DEU^H|073164926|0731-5287634|07323-291|DEU||EVC||||||Stuttgart|||D
PV1||I|C1^^^CH|N|6308714||||||||||||||6308714^^^Kiefer-Klinikum^VN||K|||||||||||||||E|||7823|||||20260122155500|20260813174000|||617||6308714
TXA|1|CN|application/word|||20260416142700|20260416142700||||stöckli|78491||||78491.doc^HOSPAT|DI
OBX|1|ED|^Document Content|1|^text/plain^^Base64^VGhpcyBpcyBhbiBleGFtcGxlIERvY3VtZW50Lg==||||||F
```

## 16. MDM^T08 - document status change (HL7-D MDM profile v2.5)

<!-- Source: https://wiki.hl7.de/index.php/HL7v2-Profile_MDM-Nachrichten -->

```
MSH|^~\&|HOSPAT|ADT|DATAGATE|ADT|20260416181000||MDM^T08^MDM_T02|102001|D|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|||2.16.840.1.113883.2.6.9.69^^2.16.840.1.1.13883.2.6^ISO
EVN||20260416181000
PID|||205000418^^^Kiefer-Klinikum^PI||Dietrich^Gërd^^^^^L||19660514|M|||Herderstr. 11^^Ulm^^89073^DEU^H|073164926|0731-5287634|07323-291|DEU||EVC||||||Stuttgart|||D
PV1||I|C1^^^CH|N|6308714||||||||||||||6308714^^^Kiefer-Klinikum^VN||K|||||||||||||||E|||7823|||||20260122155500|20260813174000|||617||6308714
TXA|1|CN|application/word|||20260416142700|20260416142700|20260416170000|||stöckli|78491||||78491.doc^HOSPAT|AU
OBX|1|ED|^Document Content|1|^text/plain^^Base64^VGhpcyBpcyBhbiBleGFtcGxlIERvY3VtZW50Lg==||||||F
```

## 17. DFT^P03 - financial transaction (Thieme E-ConsentPro)

<!-- Source: https://support.thieme-compliance.de/de/ECP/Admin/hl7-nachrichtenstrukturen.html -->

```
MSH|^~\&|ECONSENTPRO|THIEME|KIS|KRANKENHAUS|20260315144021||DFT^P03|a8274de51943f780|P|2.5|||AL|NE|DEU|UNICODE UTF-8
EVN|P03|20260315144018
PID|||20260315P00289||Roth^Britta||19890327|F|||Neckarstr. 78^^Stuttgart^^70190||0711/12345-0
PV1|1|I|64^6405^3^URO|||||||||||||N|||20260315F00134|||||K||||||||||||||||||||20260315133524
FT1|1|20260315A00078|20260315A00078|20260315143954||CG|D-An1E^Narkose/Regionalanästhesie^com.thieme.ecp|||1||||||||||B000852446^Maier^Rëné^^^Dr. med.|||||D-An1E
```

## 18. MDM^T01 - consent document notification (Thieme E-ConsentPro)

<!-- Source: https://support.thieme-compliance.de/de/ECP/Admin/hl7-nachrichtenstrukturen.html -->

```
MSH|^~\&|ECONSENTPRO|THIEME|KIS|KRANKENHAUS|20260315144121||MDM^T01|b3941ca72856e017|P|2.5|||AL|NE|DEU|UNICODE UTF-8
EVN|T01|20260315144123
PID|||20260315P00289||Roth^Britta||19890327|F|||Neckarstr. 78^^Stuttgart^^70190||0711/12345-0
PV1|1|I|64^6405^3^URO|||||||||||||N|||20260315F00134|||||K||||||||||||||||||||20260315133524
ORC|SC|20260315A00078|20260315A00078~001||CM||||20260315144123
OBR|1|20260315A00078|20260315A00078~001|D-An1E^Narkose/Regionalanästhesie^com.thieme.ecp
NTE|1|L|Maßnahme vom Patienten akzeptiert|RE
TXA|1|HP|AP|20260315144123||20260315140844|||B000852446^Maier^Rëné^^^Dr. med.|||7c29a4e1-83df-41b7-9562-d8ef12345a02^com.thieme.ecp||20260315A00078|20260315A00078~001|I_D-An1E_20260315A00078_20260315144103.pdf|LA|U
```

## 19. ADT^A01 - admission with insurance (Thieme E-ConsentPro)

<!-- Source: https://support.thieme-compliance.de/de/ECP/Admin/hl7_adt-nachrichten.html -->

```
MSH|^~\&|SENDESYSTEM|SENDEKH|EMPFANGSSYSTEM|EMPFANGSKH|20260101120000||ADT^A01^ADT_A01|MSG00001|P|2.6
EVN|A01|20260101120000
PID|||PAT042^^^Robert-Bosch-Krankenhaus||Roth^Britta^Bïrgit^^Frau||20080614|F|||Rotebühlstr. 55^^Stuttgart^^70178||^^PH^07118901234~^^CP^07118901235~^^Internet^britta.roth@stuttgartpost.de
PV1||I|Station A^Zimmer 111^Bett 1^Chirurgie||||ATT001^K.^Falk^^^Dr.^med.|REF001^Ö.^Herbst^^^Dr.^med.|CON001^W.^Hëlmut^^^Dr.^med.||Station B^Zimmer 222^Bett 2^Innere Medizin||||||||FALL042|||||||||||||||||||||||Station C^Zimmer 333^Bett 3^Neurologie||20260101120000
IN1|1|0|BKV1|TK TECHNIKER KRANKENKASSE|Bramfelder Str. 140^^Hamburg^^22305||||||||||||||||||||||||||||||||||||||||||||49
```

## 20. ORU^R01 - ICU observation results (DETECT / UKD Dresden)

<!-- Source: https://detect-docs.zmi.ukdd.de/import/apis/hl7v2.html -->

```
MSH|^~\&|COPRAdetectapi|001|detectserver||||ORU^R01||P|2.5|||AL|NE|DE|8859/1|||2.16.840.1
PID|1|5678||43218765
PV1|1||SC110|
OBX|1|NM|RASS||-4|||||||||202601010600
OBX|2|ST|PupilleLinks||e+k|||||||||202612301330
OBX|3|ST|PupilleRechts||e+k|||||||||202601010600
```
