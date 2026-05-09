# CGM Clinical (CompuGroup Medical) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - stationäre Aufnahme (inpatient admission) with insurance

```
MSH|^~\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260315083000||ADT^A01^ADT_A01|CTL00001|P|2.6
EVN|A01|20260315083000
PID|||PT7890^^^Charité Berlin||Winkler^Sabine^Monika^^Frau||19830214|F|||Prenzlauer Allee 47^^Berlin^^10405||^^PH^03012345678~^^CP^01761234567~^^Internet^sabine.winkler@gëmail.de
PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Hoffmann^Stefan^^^Dr.^med.|ARZ200^Richter^Klaus^^^Dr.^med.|ARZ300^Becker^Thomas^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260315083000
IN1|1|0|KV001|AOK NORDOST|Wilhelmstraße 1^^Berlin^^10963||||||||||||||||||||||||||||||||||||||||||||49
```

## 2. ADT^A02 - Verlegung (patient transfer)

```
MSH|^~\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260315093000||ADT^A02^ADT_A02|CTL00002|P|2.6
EVN|A02|20260315093000
PID|||PT7890^^^Charité Berlin||Winkler^Sabine^Monika^^Frau||19830214|F|||Prenzlauer Allee 47^^Berlin^^10405||^^PH^03012345678~^^CP^01761234567~^^Internet^sabine.winkler@gëmail.de
PV1||I|Nordflügel^Raum 502^Bett 2^Innere Medizin||||ARZ100^Hoffmann^Stefan^^^Dr.^med.|ARZ200^Richter^Klaus^^^Dr.^med.|ARZ300^Becker^Thomas^^^Dr.^med.||Südflügel^Raum 401^Bett 1^Orthopädie||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260315093000
```

## 3. ADT^A03 - Entlassung (discharge)

```
MSH|^~\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260320140000||ADT^A03^ADT_A03|CTL00003|P|2.6
EVN|A03|20260320140000
PID|||PT7890^^^Charité Berlin||Winkler^Sabine^Monika^^Frau||19830214|F|||Prenzlauer Allee 47^^Berlin^^10405||^^PH^03012345678~^^CP^01761234567~^^Internet^sabine.winkler@gëmail.de
PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Hoffmann^Stefan^^^Dr.^med.|ARZ200^Richter^Klaus^^^Dr.^med.|ARZ300^Becker^Thomas^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260320140000
```

## 4. ADT^A04 - ambulante Registrierung (outpatient registration) with insurance

```
MSH|^~\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260321100000||ADT^A04^ADT_A01|CTL00004|P|2.6
EVN|A04|20260321100000
PID|||PT7890^^^Charité Berlin||Winkler^Sabine^Monika^^Frau||19830214|F|||Prenzlauer Allee 47^^Berlin^^10405||^^PH^03012345678~^^CP^01761234567~^^Internet^sabine.winkler@gëmail.de
PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Hoffmann^Stefan^^^Dr.^med.|ARZ200^Richter^Klaus^^^Dr.^med.|ARZ300^Becker^Thomas^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260321100000
IN1|1|0|KV001|AOK NORDOST|Wilhelmstraße 1^^Berlin^^10963||||||||||||||||||||||||||||||||||||||||||||49
```

## 5. ADT^A05 - Voraufnahme (pre-admission) with insurance

```
MSH|^~\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260322080000||ADT^A05^ADT_A05|CTL00005|P|2.6
EVN|A05|20260322080000
PID|||PT7890^^^Charité Berlin||Winkler^Sabine^Monika^^Frau||19830214|F|||Prenzlauer Allee 47^^Berlin^^10405||^^PH^03012345678~^^CP^01761234567~^^Internet^sabine.winkler@gëmail.de
PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Hoffmann^Stefan^^^Dr.^med.|ARZ200^Richter^Klaus^^^Dr.^med.|ARZ300^Becker^Thomas^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260322080000
IN1|1|0|KV001|AOK NORDOST|Wilhelmstraße 1^^Berlin^^10963||||||||||||||||||||||||||||||||||||||||||||49
```

## 6. ADT^A08 - Änderung Patientendaten (update patient) with insurance

```
MSH|^~\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260323090000||ADT^A08^ADT_A01|CTL00006|P|2.6
EVN|A08|20260323090000
PID|||PT7890^^^Charité Berlin||Winkler^Sabine^Petra^^Frau||19820501|F|||Schönhauser Allee 99^^Berlin^^10439||^^PH^03098765432~^^CP^01769876543~^^Internet^petra.winkler@gëmail.de
PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Hoffmann^Stefan^^^Dr.^med.|ARZ200^Richter^Klaus^^^Dr.^med.|ARZ300^Becker^Thomas^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260323090000
IN1|1|0|KV001|AOK NORDOST|Wilhelmstraße 1^^Berlin^^10963||||||||||||||||||||||||||||||||||||||||||||49
```

## 7. ADT^A09 - Patient verlässt Einrichtung (patient departing)

```
MSH|^~\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260324110000||ADT^A09^ADT_A09|CTL00007|P|2.6
EVN|A09|20260324110000
PID|||PT7890^^^Charité Berlin||Winkler^Sabine^Monika^^Frau||19830214|F|||Prenzlauer Allee 47^^Berlin^^10405||^^PH^03012345678~^^CP^01761234567~^^Internet^sabine.winkler@gëmail.de
PV1||I|Nordflügel^Raum 502^Bett 2^Innere Medizin||||ARZ100^Hoffmann^Stefan^^^Dr.^med.|ARZ200^Richter^Klaus^^^Dr.^med.|ARZ300^Becker^Thomas^^^Dr.^med.||Südflügel^Raum 401^Bett 1^Orthopädie||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260324110000
```

## 8. ADT^A10 - Patient erreicht Einrichtung (patient arriving)

```
MSH|^~\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260324113000||ADT^A10^ADT_A09|CTL00008|P|2.6
EVN|A10|20260324113000
PID|||PT7890^^^Charité Berlin||Winkler^Sabine^Monika^^Frau||19830214|F|||Prenzlauer Allee 47^^Berlin^^10405||^^PH^03012345678~^^CP^01761234567~^^Internet^sabine.winkler@gëmail.de
PV1||I|Westflügel^Raum 603^Bett 3^Neurochirurgie||||ARZ100^Hoffmann^Stefan^^^Dr.^med.|ARZ200^Richter^Klaus^^^Dr.^med.|ARZ300^Becker^Thomas^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Südflügel^Raum 401^Bett 1^Orthopädie||20260324113000
```

## 9. ADT^A11 - Stornierung Aufnahme (cancel admit)

```
MSH|^~\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260325070000||ADT^A11^ADT_A09|CTL00009|P|2.6
EVN|A11|20260325070000
PID|||PT7890^^^Charité Berlin||Winkler^Sabine^Monika^^Frau||19830214|F|||Prenzlauer Allee 47^^Berlin^^10405||^^PH^03012345678~^^CP^01761234567~^^Internet^sabine.winkler@gëmail.de
PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Hoffmann^Stefan^^^Dr.^med.|ARZ200^Richter^Klaus^^^Dr.^med.|ARZ300^Becker^Thomas^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260325070000
```

## 10. ADT^A08 - patient update via samedi HL7gateway

```
MSH|^~\&|termin-gw|praxis-süd|PRAXIS_APP|KLINIK_RÖNTGEN|20260401151846+0200||ADT^A08^ADT_A01|740298561038472159|P|2.5||||||UNICODE UTF-8
EVN|A08|202604011516+0200
PID|1|56789|xbc3def912a^^^&www.praxis-süd.de&DNS^PI~56789^^^^PT||Krämer^Wolfgang^^^Prof.||19880913|M|||Kantstraße 42^^Berlin^^10623^DE||+49301234567^^CP^^^^^^^^^+49301234567~+49306789012^^PH^^^^^^^^^+49306789012~wolfgang.kraemer@praxis-süd.de^NET^X.400^wolfgang.kraemer@praxis-süd.de
PV1|1|U
```

## 11. ADT^A29 - patient deleted via samedi HL7gateway

```
MSH|^~\&|termin-gw|praxis-süd|PRAXIS_APP|KLINIK_RÖNTGEN|20260401152323+0200||ADT^A29^ADT_A21|829471036285019374|P|2.5||||||UNICODE UTF-8
EVN|A29|202604011523+0200
PID|1|44|y8a2bc7e31f^^^&www.praxis-süd.de&DNS^PI~44^^^^PT||Yilmaz^Leyla||19751120
PV1|1|U
```

## 12. ADT^A08 - incoming from KIS via KomServer

```
MSH|^~\&|IntSrv|INTSRV_KH|termin-gw|praxis-süd|20260410123517||ADT^A08|2638150947283|P|2.5|9E72B53F8AC791B||AL|NE||8859/1
EVN|A08|202604061019
PID|1||5566^^^&www.praxis-süd.de&DNS^PI~331742^^^Röntgen^PI|20000077^^^KÖL^PI|Schneider^Claudia||19560318|F|||Luisenstraße 23&Luisenstraße 23^^Köln^^50672^DE^L||^^PH^^^^0221-7654321 Büro|^^PH
```

## 13. ADT^A08 - incoming with multiple external identifiers

```
MSH|^~\&|IntSrv|INTSRV_KH|befund-süd|BEFUND_SÜD|20260410123517||ADT^A08|2638150947283|P|2.5|9E72B53F8AC791B||AL|NE||8859/1
EVN|A08|202604061019
PID|1||331742~77777^^^&a1b2c3d4-e5f6-7890-abcd-ef1234567890&UUID^PI~88888^^^baz^PI|20000077^^^KÖL^PI|Schneider^Claudia||19560318|F|||Hohenzollernring 23&Hohenzollernring 23^^Köln^^50672^DE^L||^^PH^^^^0221-7654321 Büro|^^PH
PV1|1|U
```

## 14. ADT^A40 - Zusammenführung Patienten (merge patient)

```
MSH|^~\&|IntSrv|INTSRV_KH|termin-gw|praxis-süd|20260410123517||ADT^A40|2638150947283|P|2.5|9E72B53F8AC791B||AL|NE||8859/1
EVN|A40|202604081715
PID|1||5566^^^&www.praxis-süd.de&DNS^PI~331742^^^Röntgen^PI|20000077^^^KÖL^PI|Schneider^Claudia||19560318|F|||Luisenstraße 23&Luisenstraße 23^^Köln^^50672^DE^L||^^PH^^^^0221-7654321 Büro|^^PH
MRG|9876~q283746bcde^^^&www.praxis-süd.de&DNS~5567823^^^&1.2.276.0.76.3.1.660.1.1.1.2.1&ISO^PI|
```

## 15. ADT^A01 - Aufnahme from MSH segment reference (HL7 DE)

```
MSH|^~\&|KLINx||AUFN||20260401112408||ADT^A01^ADT_A01|77|P|2.5|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.1^^2.16.840.1.113883.2.6^ISO
```

## 16. ADT^A31 - Änderung Personendaten (update person information)

```
MSH|^~\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260401120000||ADT^A31^ADT_A05|CTL00010|P|2.6
EVN|A31|20260401120000
PID|||PT7890^^^Charité Berlin||Winkler^Sabine^Petra^^Frau||19820501|F|||Schönhauser Allee 99^^Berlin^^10439||^^PH^03098765432~^^CP^01769876543~^^Internet^petra.winkler@gëmail.de
PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Hoffmann^Stefan^^^Dr.^med.|ARZ200^Richter^Klaus^^^Dr.^med.|ARZ300^Becker^Thomas^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260401120000
IN1|1|0|KV001|AOK NORDOST|Wilhelmstraße 1^^Berlin^^10963||||||||||||||||||||||||||||||||||||||||||||49
```

## 17. ORU^R01 - Laborbefund (laboratory result)

```
MSH|^~\&|HÄMA LAB|ZLAB-7|BEFUND ÖST|GEBÄUDE9|20260215093000||ORU^R01|STRG-7890|P|2.4
PID|||888-77-6666||SCHRÖDER^ÉVA^M^^^^L|BERGMANN|19750520|F|||Weberstraße 28^^Göttingen^NI^37073||(0551)2345678|(0551)876-543||||AC888776666||89-B5667^NI^20260101
OBR|1|934561^BEFUND ÖST|2078945^HÄMA LAB|17856^HÄMOGLOBIN|||20260215073000|||||||||888-77-6666^KRAUSE^PÀTRÍCIA P^^^^MD^^|||||||||F||||||777-66-5555^HIPPÖKRÄTÉS^HÖRST H^^^^MD
OBX|1|SN|718-7^HÄMOGLOBIN^BLUT:MCNC:PT:BLUT:QN||^145|g/L|120_160|N|||F
```

## 18. ADT^A01 - Aufnahme with Caristix reference encoding

```
MSH|^~\&|GrößeReg|KölnKlinikC|ÜberOE|ZürichBildZ|20260529090131-0500||ADT^A01^ADT_A01|01052901|P|2.5
EVN||200605290901||||200605290900
PID|||78452991^^^Kölnreg^PI||FISCHER^PETRA^Q^JR||19700815|M||2028-9^^HL70005^RA99113^^XYZ|Domplatz 14^^Köln^NW^50667^^M~WEBER'S KONDITOREI^Königsallee 200^^Düsseldorf^NW^40212^^O|||||||0105I30001^^^99DEF^AN
PV1||I|W^389^1^UABH^^^^3||||54321^ENGEL^RÉX^J^^^MD^0010^UAMC^L||98765^VOGT^LÜCIA^X^^^MD^0010^UAMC^L|MED|||||A0||24680^BRANDT^SÖRÉN^T^^^MD^0010^UAMC^L|||||||||||||||||||||||||||200605290900
```

## 19. ACK^A02 - transport acknowledgment for transfer

```
MSH|^~\&|RÖNTGEN|AUFN|KLINIK_ÖST|AUFN|20260401170600||ACK^A02^ACK|RÖNT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.4^^2.16.840.1.113883.2.6^ISO
MSA|CA|AUFN002|
```

## 20. ADT^A04 - registration from ringholm.de reference

```
MSH|^~\&|SENDE_APPLIKATION|SENDE_EINRICHTUNG|EMPFANGS_APPLIKATION|EMPFANGS_EINRICHTUNG|20260613083617||ADT^A04|934576120260613083617|P|2.3||||
EVN|A04|20260613083617|||
PID|1||246813||LEHMANN^THÉODOR^||19550718|M|||Friedrichstraße 5^^Berlin^BE^10117||(030)9391289^^^theodor@berlin-post.de|||||2847|99999999||||||||||||||||||||
PV1|1|O|||||7^Hartmann^Güntér^^MD^^^^|||||||||||||||||||||||||||||||||||||||||||||
```
