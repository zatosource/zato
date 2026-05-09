# Dorner device interfaces - real HL7v2 ER7 messages

---

## 1. ORU^R01 - Blutgasanalyse ABL90 (blood gas analysis)

```
MSH|^~\&|DORNER_POCT|ABL90_FLEX|KISIM|USZ_ZUERICH|20260301090000||ORU^R01^ORU_R01|DORN00001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101001^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Burgener^Ernst^Fritz^^Herr||19580415|M|||Dorfstrasse 10^^Biel/Bienne^^2502^CH||^^CP^0766503584
PV1||I|IPS^Zimmer 3^Bett 1^Intensivstation||||ARZ700^Egger^Otto^^^Dr.^med.||||||||||||FALL70001
OBR|1|ORD101^^^DORNER_POCT|RES101^^^ABL90|BGA^Blutgasanalyse^LN|||20260301085500|||||||||ARZ700^Egger^Otto^^^Dr.^med.||||||20260301090000|||F
OBX|1|NM|2744-1^pH arteriell^LN||7.35||7.35-7.45|N|||F
OBX|2|NM|2019-8^pCO2 arteriell^LN||5.8|kPa|4.7-6.0|N|||F
OBX|3|NM|2703-7^pO2 arteriell^LN||9.5|kPa|10.0-13.3|L|||F
OBX|4|NM|1960-4^Bicarbonat^LN||22|mmol/L|22-26|N|||F
OBX|5|NM|1925-7^Base Excess^LN||-2.5|mmol/L|-2.0-2.0|L|||F
OBX|6|NM|2713-6^Sauerstoffsättigung^LN||92|%|95-99|L|||F
```

---

## 2. ORU^R01 - Glukosemessung Accu-Chek (glucose measurement)

```
MSH|^~\&|DORNER_POCT|ACCUCHEK_INFORM|KISIM|USZ_ZUERICH|20260301100000||ORU^R01^ORU_R01|DORN00002|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101002^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Stauffer^Johanna^Robert^^Frau||19700622|F|||Marktgasse 177^^Baden^^5400^CH||^^CP^0791602346
PV1||I|MED^Zimmer 310^Bett A^Innere Medizin||||ARZ701^Liechti^Cornelia^^^Dr.^med.||||||||||||FALL70002
OBR|1|ORD102^^^DORNER_POCT|RES102^^^ACCUCHEK|GLU^Glukose POCT^LN|||20260301095500|||||||||ARZ701^Liechti^Cornelia^^^Dr.^med.||||||20260301100000|||F
OBX|1|NM|2345-7^Glukose^LN||12.8|mmol/L|3.9-5.6|HH|||F
```

---

## 3. ORU^R01 - Gerinnungsanalyse CoaguChek (coagulation POC)

```
MSH|^~\&|DORNER_POCT|COAGUCHEK_PRO|KISIM|INSEL_BERN|20260305110000||ORU^R01^ORU_R01|DORN00003|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101003^^^INSEL&2.16.756.5.30.1.128.1&ISO^MR||Schueler^Franz^Verena^^Herr||19480310|M|||Eichenstrasse 133^^Nidau^^2560^CH||^^PH^0325263443
PV1||I|KARD^Zimmer 601^Bett A^Kardiologie||||ARZ702^Frei^Margrit^^^Prof.^Dr.^med.||||||||||||FALL70003
OBR|1|ORD103^^^DORNER_POCT|RES103^^^COAGUCHEK|COAG^Gerinnung POCT^LN|||20260305105500|||||||||ARZ702^Frei^Margrit^^^Prof.^Dr.^med.||||||20260305110000|||F
OBX|1|NM|6301-6^INR^LN||2.8||2.0-3.0|N|||F
OBX|2|NM|5902-2^Prothrombinzeit^LN||32|s|11-15|HH|||F
```

---

## 4. ORU^R01 - Urinstreifentest Clinitek (urinalysis POC)

```
MSH|^~\&|DORNER_POCT|CLINITEK_STATUS|ORBIS|KSSG_STGALLEN|20260310083000||ORU^R01^ORU_R01|DORN00004|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101004^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Widmer^Sandra^Elisabeth^^Frau||19620915|F|||Dorfstrasse 188^^Chur^^7000^CH||^^PH^0817574503
PV1||I|MED^Zimmer 205^Bett B^Innere Medizin||||ARZ703^Wyss^Viktor^^^Dr.^med.||||||||||||FALL70004
OBR|1|ORD104^^^DORNER_POCT|RES104^^^CLINITEK|UA^Urinstreifentest POCT^LN|||20260310082500|||||||||ARZ703^Wyss^Viktor^^^Dr.^med.||||||20260310083000|||F
OBX|1|ST|5811-5^Urin pH^LN||5.5||5.0-8.0|N|||F
OBX|2|ST|2965-2^Spezifisches Gewicht^LN||1.025||1.005-1.030|N|||F
OBX|3|ST|5804-0^Protein^LN||Spur||Negativ|A|||F
OBX|4|ST|5794-3^Glukose^LN||Negativ||Negativ||||F
OBX|5|ST|5802-4^Nitrit^LN||Negativ||Negativ||||F
OBX|6|ST|5799-2^Leukozyten^LN||Negativ||Negativ||||F
OBX|7|ST|5797-6^Blut^LN||Spur||Negativ|A|||F
```

---

## 5. ORU^R01 - Troponin i-STAT (cardiac marker POC)

```
MSH|^~\&|DORNER_POCT|ISTAT_ALINITY|KISIM|USZ_ZUERICH|20260315060000||ORU^R01^ORU_R01|DORN00005|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101005^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Eberle^Bruno^Hans^^Herr||19520810|M|||Spalenberg 20^^Basel^^4001^CH||^^PH^0611064361
PV1||E|NOTFALL^Box 1^^Notfallstation||||ARZ704^Walder^Urs^^^Dr.^med.||||||||||||FALL70005
OBR|1|ORD105^^^DORNER_POCT|RES105^^^ISTAT|CARD^Kardiale Marker POCT^LN|||20260315055500|||||||||ARZ704^Walder^Urs^^^Dr.^med.||||||20260315060000|||F
OBX|1|NM|49563-0^Troponin I hs^LN||85|ng/L|0-14|HH|||F
OBX|2|NM|33762-6^NT-proBNP^LN||1250|pg/mL|0-125|HH|||F
```

---

## 6. ORU^R01 - CRP-Schnelltest (CRP rapid test)

```
MSH|^~\&|DORNER_POCT|EUROLYSER_CUBE|ORBIS|KSSG_STGALLEN|20260320090000||ORU^R01^ORU_R01|DORN00006|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101006^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Marti^Karin^Peter^^Frau||19750505|F|||Eichenstrasse 130^^Koniz^^3098^CH||^^CP^0796682954
PV1||E|NOTFALL^Box 3^^Notfallstation||||ARZ705^Studer^Daniel^^^Dr.^med.||||||||||||FALL70006
OBR|1|ORD106^^^DORNER_POCT|RES106^^^EUROLYSER|CRP^CRP POCT^LN|||20260320085500|||||||||ARZ705^Studer^Daniel^^^Dr.^med.||||||20260320090000|||F
OBX|1|NM|17861-6^CRP^LN||45|mg/L|0-5|HH|||F
```

---

## 7. ORU^R01 - Blutgasanalyse mit Elektrolyte (blood gas with electrolytes)

```
MSH|^~\&|DORNER_POCT|ABL90_FLEX|ISHMED|LUKS_LUZERN|20260322080000||ORU^R01^ORU_R01|DORN00007|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101007^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR||Schaerer^Andreas^Fritz^^Herr||19620318|M|||Tessinerplatz 36^^Thalwil^^8800^CH||^^CP^0795377473
PV1||I|IPS^Zimmer 5^Bett 1^Intensivstation||||ARZ706^Brunner^Jakob^^^Dr.^med.||||||||||||FALL70007
OBR|1|ORD107^^^DORNER_POCT|RES107^^^ABL90|BGA_EXT^Blutgasanalyse erweitert^LN|||20260322075500|||||||||ARZ706^Brunner^Jakob^^^Dr.^med.||||||20260322080000|||F
OBX|1|NM|2744-1^pH arteriell^LN||7.42||7.35-7.45|N|||F
OBX|2|NM|2019-8^pCO2 arteriell^LN||4.8|kPa|4.7-6.0|N|||F
OBX|3|NM|2703-7^pO2 arteriell^LN||12.0|kPa|10.0-13.3|N|||F
OBX|4|NM|2823-3^Kalium^LN||3.8|mmol/L|3.5-5.1|N|||F
OBX|5|NM|2951-2^Natrium^LN||141|mmol/L|136-145|N|||F
OBX|6|NM|17861-4^Ionisiertes Calcium^LN||1.18|mmol/L|1.15-1.30|N|||F
OBX|7|NM|2345-7^Glukose^LN||6.2|mmol/L|3.9-5.6|H|||F
OBX|8|NM|2714-4^Laktat^LN||1.5|mmol/L|0.5-2.0|N|||F
```

---

## 8. ORU^R01 - HbA1c DCA Vantage (glycated hemoglobin)

```
MSH|^~\&|DORNER_POCT|DCA_VANTAGE|KISIM|KSW_WINTERTHUR|20260325100000||ORU^R01^ORU_R01|DORN00008|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101008^^^KSW&2.16.756.5.30.1.129.1&ISO^MR||Roth^Irene^Margrit^^Frau||19550830|F|||Gloriastrasse 52^^Koniz^^3098^CH||^^PH^0315555598
PV1||O|AMB^Sprechzimmer 8^^Diabetologie||||ARZ707^Hess^Silvia^^^Dr.^med.||||||||||||FALL70008
OBR|1|ORD108^^^DORNER_POCT|RES108^^^DCA|HBA1C^HbA1c POCT^LN|||20260325095500|||||||||ARZ707^Hess^Silvia^^^Dr.^med.||||||20260325100000|||F
OBX|1|NM|4548-4^HbA1c^LN||7.2|%|4.0-6.0|HH|||F
OBX|2|NM|59261-8^HbA1c (IFCC)^LN||55|mmol/mol|20-42|HH|||F
```

---

## 9. ORU^R01 - Blutgasprotokoll mit PDF (blood gas report with embedded PDF)

```
MSH|^~\&|DORNER_POCT|ABL90_FLEX|KISIM|USZ_ZUERICH|20260401090000||ORU^R01^ORU_R01|DORN00009|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101001^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Burgener^Ernst^Fritz^^Herr||19580415|M|||Dorfstrasse 10^^Biel/Bienne^^2502^CH||^^CP^0766503584
PV1||I|IPS^Zimmer 3^Bett 1^Intensivstation||||ARZ700^Egger^Otto^^^Dr.^med.||||||||||||FALL70001
OBR|1|ORD109^^^DORNER_POCT|RES109^^^ABL90|11502-2^Blutgasprotokoll^LN|||20260401085500|||||||||ARZ700^Egger^Otto^^^Dr.^med.||||||20260401090000|||F
OBX|1|ED|11502-2^Blutgasprotokoll^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKEJsdXRnYXNwcm90b2tvbGwpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAowMDAwMDAwMjQyIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNSAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMzQ2CiUlRU9GCg==||||||F
```

---

## 10. ORU^R01 - Elektrolyteanalyse Cobas b 221 (electrolyte analysis)

```
MSH|^~\&|DORNER_POCT|COBAS_B221|ORBIS|KSSG_STGALLEN|20260403080000||ORU^R01^ORU_R01|DORN00010|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101009^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Steiner^Christian^Karl^^Herr||19680120|M|||Kornhausstrasse 13^^Solothurn^^4500^CH||^^CP^0763137401
PV1||I|MED^Zimmer 308^Bett A^Innere Medizin||||ARZ703^Wyss^Viktor^^^Dr.^med.||||||||||||FALL70009
OBR|1|ORD110^^^DORNER_POCT|RES110^^^COBAS|ELYTE^Elektrolyte POCT^LN|||20260403075500|||||||||ARZ703^Wyss^Viktor^^^Dr.^med.||||||20260403080000|||F
OBX|1|NM|2823-3^Kalium^LN||5.2|mmol/L|3.5-5.1|H|||F
OBX|2|NM|2951-2^Natrium^LN||132|mmol/L|136-145|L|||F
OBX|3|NM|17861-4^Ionisiertes Calcium^LN||1.22|mmol/L|1.15-1.30|N|||F
OBX|4|NM|2075-0^Chlorid^LN||98|mmol/L|98-107|N|||F
```

---

## 11. ORU^R01 - Schwangerschaftstest POCT (pregnancy test)

```
MSH|^~\&|DORNER_POCT|RAPID_TEST|NEXUS_KIS|SPITAL_FRAUENFELD|20260405100000||ORU^R01^ORU_R01|DORN00011|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101010^^^SPITAL_FRAUENFELD&2.16.756.5.30.1.210.1&ISO^MR||Schmid^Therese^Rosa^^Frau||19920715|F|||Limmatquai 162^^St. Gallen^^9000^CH||^^CP^0785844563
PV1||E|NOTFALL^Box 2^^Notfallstation||||ARZ708^Fischer^Martin^^^Dr.^med.||||||||||||FALL70010
OBR|1|ORD111^^^DORNER_POCT|RES111^^^RAPID|2106-3^beta-HCG POCT^LN|||20260405095500|||||||||ARZ708^Fischer^Martin^^^Dr.^med.||||||20260405100000|||F
OBX|1|ST|2106-3^beta-HCG qualitativ^LN||Positiv||Negativ|A|||F
```

---

## 12. ORU^R01 - Influenza-Schnelltest (influenza rapid test)

```
MSH|^~\&|DORNER_POCT|SOFIA_2|KISIM|USZ_ZUERICH|20260407090000||ORU^R01^ORU_R01|DORN00012|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101011^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Berger^Lisa^Otto^^Frau||19650930|F|||Schulstrasse 106^^Basel^^4001^CH||^^PH^0614587910
PV1||E|NOTFALL^Box 5^^Notfallstation||||ARZ704^Walder^Urs^^^Dr.^med.||||||||||||FALL70011
OBR|1|ORD112^^^DORNER_POCT|RES112^^^SOFIA|FLU^Influenza-Schnelltest POCT^LN|||20260407085500|||||||||ARZ704^Walder^Urs^^^Dr.^med.||||||20260407090000|||F
OBX|1|ST|80382-5^Influenza A Antigen^LN||Positiv||Negativ|A|||F
OBX|2|ST|80383-3^Influenza B Antigen^LN||Negativ||Negativ||||F
```

---

## 13. ORU^R01 - Blutbild pocH-100i (hematology POC)

```
MSH|^~\&|DORNER_POCT|POCH_100I|ISHMED|LUKS_LUZERN|20260409090000||ORU^R01^ORU_R01|DORN00013|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101012^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR||Weber^Stefan^Verena^^Herr||19700505|M|||Stauffacherstrasse 40^^Solothurn^^4500^CH||^^CP^0768262872
PV1||E|NOTFALL^Box 2^^Notfallstation||||ARZ709^Kaufmann^Karl^^^Dr.^med.||||||||||||FALL70012
OBR|1|ORD113^^^DORNER_POCT|RES113^^^POCH|CBC_POCT^Blutbild POCT^LN|||20260409085500|||||||||ARZ709^Kaufmann^Karl^^^Dr.^med.||||||20260409090000|||F
OBX|1|NM|718-7^Hämoglobin^LN||105|g/L|135-175|LL|||F
OBX|2|NM|6690-2^Leukozyten^LN||18.5|10*9/L|4.0-10.0|HH|||F
OBX|3|NM|789-8^Thrombozyten^LN||85|10*9/L|150-400|L|||F
```

---

## 14. ORU^R01 - D-Dimer-Schnelltest (D-dimer rapid test)

```
MSH|^~\&|DORNER_POCT|PATHFAST|KISIM|USZ_ZUERICH|20260410070000||ORU^R01^ORU_R01|DORN00014|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101013^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Suter^Gabriela^Margrit^^Frau||19580220|F|||Junkerngasse 192^^Wil^^9500^CH||^^PH^0714584776
PV1||E|NOTFALL^Box 4^^Notfallstation||||ARZ704^Walder^Urs^^^Dr.^med.||||||||||||FALL70013
OBR|1|ORD114^^^DORNER_POCT|RES114^^^PATHFAST|DDIM^D-Dimer POCT^LN|||20260410065500|||||||||ARZ704^Walder^Urs^^^Dr.^med.||||||20260410070000|||F
OBX|1|NM|48066-5^D-Dimer^LN||2.5|mg/L FEU|0-0.5|HH|||F
```

---

## 15. ORU^R01 - COVID-19-Schnelltest (COVID rapid antigen test)

```
MSH|^~\&|DORNER_POCT|SOFIA_2|ORBIS|KSSG_STGALLEN|20260412090000||ORU^R01^ORU_R01|DORN00015|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101014^^^KSSG&2.16.756.5.30.1.150.1&ISO^MR||Meyer^Sebastian^Maria^^Herr||19750312|M|||Marktgasse 19^^Aarau^^5000^CH||^^CP^0798450862
PV1||E|NOTFALL^Box 1^^Notfallstation||||ARZ705^Studer^Daniel^^^Dr.^med.||||||||||||FALL70014
OBR|1|ORD115^^^DORNER_POCT|RES115^^^SOFIA|COVID^SARS-CoV-2 Antigen POCT^LN|||20260412085500|||||||||ARZ705^Studer^Daniel^^^Dr.^med.||||||20260412090000|||F
OBX|1|ST|94558-4^SARS-CoV-2 Antigen^LN||Negativ||Negativ||||F
```

---

## 16. ORU^R01 - Laktatmessung Lactate Pro 2 (lactate measurement)

```
MSH|^~\&|DORNER_POCT|LACTATE_PRO2|KISIM|USZ_ZUERICH|20260413060000||ORU^R01^ORU_R01|DORN00016|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101001^^^USZ&2.16.756.5.30.1.127.3.1&ISO^MR||Burgener^Ernst^Fritz^^Herr||19580415|M|||Dorfstrasse 10^^Biel/Bienne^^2502^CH||^^CP^0766503584
PV1||I|IPS^Zimmer 3^Bett 1^Intensivstation||||ARZ700^Egger^Otto^^^Dr.^med.||||||||||||FALL70001
OBR|1|ORD116^^^DORNER_POCT|RES116^^^LACTATE|LAC^Laktat POCT^LN|||20260413055500|||||||||ARZ700^Egger^Otto^^^Dr.^med.||||||20260413060000|||F
OBX|1|NM|2714-4^Laktat^LN||4.2|mmol/L|0.5-2.0|HH|||F
```

---

## 17. ORU^R01 - Procalcitonin BRAHMS (procalcitonin POC)

```
MSH|^~\&|DORNER_POCT|BRAHMS_PCT|ISHMED|LUKS_LUZERN|20260414080000||ORU^R01^ORU_R01|DORN00017|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101012^^^LUKS&2.16.756.5.30.1.160.1&ISO^MR||Weber^Stefan^Verena^^Herr||19700505|M|||Stauffacherstrasse 40^^Solothurn^^4500^CH||^^CP^0768262872
PV1||I|IPS^Zimmer 2^Bett 1^Intensivstation||||ARZ706^Brunner^Jakob^^^Dr.^med.||||||||||||FALL70012
OBR|1|ORD117^^^DORNER_POCT|RES117^^^BRAHMS|PCT^Procalcitonin POCT^LN|||20260414075500|||||||||ARZ706^Brunner^Jakob^^^Dr.^med.||||||20260414080000|||F
OBX|1|NM|75241-0^Procalcitonin^LN||8.5|ng/mL|0-0.5|HH|||F
```

---

## 18. ORU^R01 - Gerätequalitätskontrolle mit Protokoll (QC with embedded PDF)

```
MSH|^~\&|DORNER_POCT|QC_MANAGER|KISIM|USZ_ZUERICH|20260415060000||ORU^R01^ORU_R01|DORN00018|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||QC_INTERNAL^^^USZ&2.16.756.5.30.1.127.3.1&ISO^QC
OBR|1|QC001^^^DORNER_POCT|QC001^^^QC_MANAGER|QC^Qualitätskontrolle ABL90^LN|||20260415055500||||||||||||||20260415060000|||F
OBX|1|NM|2744-1^pH QC Level 1^LN||7.382||7.370-7.400|N|||F
OBX|2|NM|2019-8^pCO2 QC Level 1^LN||5.35|kPa|5.10-5.60|N|||F
OBX|3|ED|11502-2^QC-Protokoll^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKFFDLVByb3Rva29sbCBBQkw5MCkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDYKJSVFT0YK||||||F
```

---

## 19. ORU^R01 - Strep-A-Schnelltest (Strep A rapid test)

```
MSH|^~\&|DORNER_POCT|ALERE_I|NEXUS_KIS|SPITAL_FRAUENFELD|20260416090000||ORU^R01^ORU_R01|DORN00019|P|2.5|||AL|NE|CHE|UNICODE UTF-8
PID|||PAT101015^^^SPITAL_FRAUENFELD&2.16.756.5.30.1.210.1&ISO^MR||Glaus^Martha^Heinz^^Frau||20160305|F|||Birkenstrasse 172^^Schaffhausen^^8200^CH||^^CP^0799103301
PV1||E|NOTFALL^Box 1^^Notfallstation||||ARZ708^Fischer^Martin^^^Dr.^med.||||||||||||FALL70015
OBR|1|ORD118^^^DORNER_POCT|RES118^^^ALERE|STREP^Streptococcus A POCT^LN|||20260416085500|||||||||ARZ708^Fischer^Martin^^^Dr.^med.||||||20260416090000|||F
OBX|1|ST|31971-5^Streptococcus Gruppe A Antigen^LN||Positiv||Negativ|A|||F
```

---

## 20. ACK - Bestätigung (acknowledgment)

```
MSH|^~\&|KISIM|USZ_ZUERICH|DORNER_POCT|ABL90_FLEX|20260417080100||ACK^R01^ACK|ACK70001|P|2.5|||AL|NE|CHE|UNICODE UTF-8
MSA|AA|DORN00001|POCT-Ergebnis erfolgreich empfangen
```
