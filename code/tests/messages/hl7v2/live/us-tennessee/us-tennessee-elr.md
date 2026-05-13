# Tennessee ELR (electronic lab reporting) - real HL7v2 ER7 messages

---

## 1. ORU^R01 - COVID-19 PCR positive result from Nashville reference lab

```
MSH|^~\&|LabCorpTN|LabCorp Nashville^05D2191065^CLIA|TNDOH|TN_DOH_ELR|20240315083022-0600||ORU^R01^ORU_R01|LC20240315083022001|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|LabCorp|6.4|LabCorp Beacon|Binary ID 20240101||20240101
PID|1||7291843^^^LabCorp Nashville&05D2191065&CLIA^PI||MCBRIDE^THOMAS^WAYNE^^^^L||19780423|M||2106-3^White^CDCREC|1704 SHELBY AVE^^NASHVILLE^TN^37206^USA^^^DAVIDSON||^PRN^PH^^1^615^4829317||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240314
ORC|RE|ORD938271^LabCorp|LC2024031500187^LabCorp Nashville^05D2191065^CLIA|||||||||1632847291^DESAI^PRIYA^N^^^^NPI^L^^^NPI||^WPN^PH^^1^615^4937182|||||||Vanderbilt Primary Care^L^^^^NPI^^^^^1283746509|1301 Medical Center Dr^^NASHVILLE^TN^37232^USA
OBR|1|ORD938271^LabCorp|LC2024031500187^LabCorp Nashville^05D2191065^CLIA|94500-6^SARS-CoV-2 (COVID-19) RNA [Presence] in Respiratory specimen by NAA with probe detection^LN|||20240314120000-0600|||||||||1632847291^DESAI^PRIYA^N^^^^NPI^L^^^NPI|^WPN^PH^^1^615^4937182|||||20240315080000-0600|||F
OBX|1|CWE|94500-6^SARS-CoV-2 (COVID-19) RNA [Presence] in Respiratory specimen by NAA with probe detection^LN|1|260373001^Detected^SCT||Not Detected|260373001^Detected^SCT|||F|||20240314120000-0600|05D2191065^LabCorp Nashville^CLIA||||ThermoFisher TaqPath COVID-19 Combo Kit^ThermoFisher^EUA210052^^20231215||20240315080000-0600||||LabCorp Nashville^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^05D2191065|4020 Wallace Ln^^NASHVILLE^TN^37209^USA
SPM|1|^LC2024031500187||258500001^Nasopharyngeal swab^SCT|||||||||||||20240314120000-0600|20240314131500-0600
```

---

## 2. ORU^R01 - Hepatitis C antibody reactive with reflex RNA from Memphis lab

```
MSH|^~\&|QuestDiagTN|Quest Memphis^44D2033844^CLIA|TNDOH|TN_DOH_ELR|20240412141530-0600||ORU^R01^ORU_R01|QD20240412141530887|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|Quest Diagnostics|8.1|Quest CareEvolve|Binary ID 20240301||20240301
PID|1||QM53917204^^^Quest Memphis&44D2033844&CLIA^PI||FREEMAN^LATOYA^MONIQUE^^^^L||19850912|F||2054-5^Black or African American^CDCREC|4715 POPLAR AVE^^MEMPHIS^TN^38117^USA^^^SHELBY||^PRN^PH^^1^901^6384921||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240411
ORC|RE|QO7729381^Quest|QM2024041200293^Quest Memphis^44D2033844^CLIA|||||||||1748293610^OKONKWO^CHIBUEZE^F^^^^NPI^L^^^NPI||^WPN^PH^^1^901^7184302|||||||Baptist Memorial Hospital Memphis^L^^^^NPI^^^^^1392847561|6019 Walnut Grove Rd^^MEMPHIS^TN^38120^USA
OBR|1|QO7729381^Quest|QM2024041200293^Quest Memphis^44D2033844^CLIA|16128-1^Hepatitis C virus Ab [Presence] in Serum^LN|||20240411093000-0600|||||||||1748293610^OKONKWO^CHIBUEZE^F^^^^NPI^L^^^NPI|^WPN^PH^^1^901^7184302|||||20240412130000-0600|||F
OBX|1|CWE|16128-1^Hepatitis C virus Ab [Presence] in Serum^LN|1|10828004^Positive^SCT||Negative|10828004^Positive^SCT|||F|||20240411093000-0600|44D2033844^Quest Memphis^CLIA||||Abbott ARCHITECT Anti-HCV^Abbott^00N0530^^20230801||20240412110000-0600||||Quest Memphis^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D2033844|5765 Shelby Oaks Dr^^MEMPHIS^TN^38134^USA
OBX|2|NM|11259-9^Hepatitis C virus RNA [Units/volume] (viral load) in Serum or Plasma by NAA with probe detection^LN|1|3250000|[IU]/mL^international unit per milliliter^UCUM|Not Detected|H|||F|||20240411093000-0600|44D2033844^Quest Memphis^CLIA||||Roche cobas HCV^Roche^MOL0010^^20230601||20240412130000-0600||||Quest Memphis^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D2033844|5765 Shelby Oaks Dr^^MEMPHIS^TN^38134^USA
SPM|1|^QM2024041200293||119364003^Serum specimen^SCT|||||||||||||20240411093000-0600|20240411101500-0600
```

---

## 3. ORU^R01 - Chlamydia trachomatis positive NAAT from Knoxville

```
MSH|^~\&|AegisLabSys|Aegis Sciences Knoxville^44D1098776^CLIA|TNDOH|TN_DOH_ELR|20240520163045-0600||ORU^R01^ORU_R01|AG20240520163045442|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|Aegis Sciences|3.2|Aegis LIS|Binary ID 20240401||20240401
PID|1||AG82164390^^^Aegis Sciences Knoxville&44D1098776&CLIA^PI||HENSLEY^BRITTANY^DAWN^^^^L||19990305|F||2106-3^White^CDCREC|5918 KINGSTON PIKE^^KNOXVILLE^TN^37919^USA^^^KNOX||^PRN^PH^^1^865^3294718||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240519
ORC|RE|AO5538291^Aegis|AG2024052000114^Aegis Sciences Knoxville^44D1098776^CLIA|||||||||1594278360^LOCKHART^DIANE^M^^^^NPI^L^^^NPI||^WPN^PH^^1^865^2847193|||||||UT Medical Center Student Health^L^^^^NPI^^^^^1470293856|1818 Andy Holt Ave^^KNOXVILLE^TN^37996^USA
OBR|1|AO5538291^Aegis|AG2024052000114^Aegis Sciences Knoxville^44D1098776^CLIA|21613-5^Chlamydia trachomatis DNA [Presence] in Specimen by NAA with probe detection^LN|||20240519140000-0600|||||||||1594278360^LOCKHART^DIANE^M^^^^NPI^L^^^NPI|^WPN^PH^^1^865^2847193|||||20240520150000-0600|||F
OBX|1|CWE|21613-5^Chlamydia trachomatis DNA [Presence] in Specimen by NAA with probe detection^LN|1|260373001^Detected^SCT||Not Detected|260373001^Detected^SCT|||F|||20240519140000-0600|44D1098776^Aegis Sciences Knoxville^CLIA||||Hologic Aptima Combo 2^Hologic^K080191^^20231101||20240520150000-0600||||Aegis Sciences Knoxville^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D1098776|1423 Weisgarber Rd^^KNOXVILLE^TN^37909^USA
SPM|1|^AG2024052000114||258529004^Throat swab^SCT|||||||||||||20240519140000-0600|20240519151000-0600
```

---

## 4. ORU^R01 - Neisseria gonorrhoeae positive from Chattanooga

```
MSH|^~\&|Erlanger_LIS|Erlanger Medical Center^44D0921553^CLIA|TNDOH|TN_DOH_ELR|20240603091215-0600||ORU^R01^ORU_R01|ERL20240603091215773|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|Erlanger|4.7|Cerner Millennium|Binary ID 20240201||20240201
PID|1||ERL62839174^^^Erlanger Medical Center&44D0921553&CLIA^PI||AGUILAR^JORGE^RAUL^^^^L||19920818|M||2106-3^White^CDCREC|2801 ROSSVILLE BLVD^^CHATTANOOGA^TN^37407^USA^^^HAMILTON||^PRN^PH^^1^423^5912847||||||||||||2135-2^Hispanic or Latino^CDCREC|||||||20240602
ORC|RE|CO8891234^Erlanger|ERL2024060300082^Erlanger Medical Center^44D0921553^CLIA|||||||||1283947560^CALLOWAY^BRENDA^K^^^^NPI^L^^^NPI||^WPN^PH^^1^423^7291034|||||||Erlanger Primary Care Associates^L^^^^NPI^^^^^1509382741|975 E 3rd St^^CHATTANOOGA^TN^37403^USA
OBR|1|CO8891234^Erlanger|ERL2024060300082^Erlanger Medical Center^44D0921553^CLIA|21415-5^Neisseria gonorrhoeae DNA [Presence] in Urethra by NAA with probe detection^LN|||20240602083000-0600|||||||||1283947560^CALLOWAY^BRENDA^K^^^^NPI^L^^^NPI|^WPN^PH^^1^423^7291034|||||20240603085000-0600|||F
OBX|1|CWE|21415-5^Neisseria gonorrhoeae DNA [Presence] in Urethra by NAA with probe detection^LN|1|260373001^Detected^SCT||Not Detected|260373001^Detected^SCT|||F|||20240602083000-0600|44D0921553^Erlanger Medical Center^CLIA||||BD MAX GC^Becton Dickinson^K181518^^20230901||20240603085000-0600||||Erlanger Medical Center^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0921553|975 E 3rd St^^CHATTANOOGA^TN^37403^USA
SPM|1|^ERL2024060300082||258566005^Urethral swab^SCT|||||||||||||20240602083000-0600|20240602091500-0600
```

---

## 5. ORU^R01 - Syphilis RPR reactive with titer from Clarksville

```
MSH|^~\&|Tennova_LIS|Tennova Healthcare Clarksville^44D0918823^CLIA|TNDOH|TN_DOH_ELR|20240718104530-0600||ORU^R01^ORU_R01|TV20240718104530551|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|Tennova Healthcare|5.0|MEDITECH Expanse|Binary ID 20240301||20240301
PID|1||TV41827593^^^Tennova Healthcare Clarksville&44D0918823&CLIA^PI||GAINES^TERRENCE^DARNELL^^^^L||19870613|M||2054-5^Black or African American^CDCREC|2415 FORT CAMPBELL BLVD^^CLARKSVILLE^TN^37042^USA^^^MONTGOMERY||^PRN^PH^^1^931^3847291||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240717
ORC|RE|TO3392817^Tennova|TV2024071800056^Tennova Healthcare Clarksville^44D0918823^CLIA|||||||||1847293016^STANTON^MELINDA^R^^^^NPI^L^^^NPI||^WPN^PH^^1^931^6172843|||||||Gateway Medical Group^L^^^^NPI^^^^^1903847261|651 Dunlop Ln^^CLARKSVILLE^TN^37040^USA
OBR|1|TO3392817^Tennova|TV2024071800056^Tennova Healthcare Clarksville^44D0918823^CLIA|20507-0^Reagin Ab [Presence] in Serum by RPR^LN|||20240717100000-0600|||||||||1847293016^STANTON^MELINDA^R^^^^NPI^L^^^NPI|^WPN^PH^^1^931^6172843|||||20240718100000-0600|||F
OBX|1|CWE|20507-0^Reagin Ab [Presence] in Serum by RPR^LN|1|11214006^Reactive^SCT||Non-Reactive|11214006^Reactive^SCT|||F|||20240717100000-0600|44D0918823^Tennova Healthcare Clarksville^CLIA||||BD Macro-Vue RPR^Becton Dickinson^K940035^^20230601||20240718093000-0600||||Tennova Healthcare Clarksville^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0918823|651 Dunlop Ln^^CLARKSVILLE^TN^37043^USA
OBX|2|SN|22462-8^Reagin Ab [Titer] in Serum by RPR^LN|1|^1^:^32||<1:1||||F|||20240717100000-0600|44D0918823^Tennova Healthcare Clarksville^CLIA||||BD Macro-Vue RPR^Becton Dickinson^K940035^^20230601||20240718100000-0600||||Tennova Healthcare Clarksville^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0918823|651 Dunlop Ln^^CLARKSVILLE^TN^37043^USA
SPM|1|^TV2024071800056||119364003^Serum specimen^SCT|||||||||||||20240717100000-0600|20240717103000-0600
```

---

## 6. ORU^R01 - Influenza A positive rapid molecular from Jackson

```
MSH|^~\&|WestTN_Healthcare_LIS|West TN Healthcare Jackson^44D0509876^CLIA|TNDOH|TN_DOH_ELR|20240122155200-0600||ORU^R01^ORU_R01|WTH20240122155200339|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|West TN Healthcare|2.9|Epic Beaker|Binary ID 20231201||20231201
PID|1||WTH28461739^^^West TN Healthcare Jackson&44D0509876&CLIA^PI||CASTEEL^LINDA^FAYE^^^^L||19650220|F||2106-3^White^CDCREC|312 CAMPBELL ST^^JACKSON^TN^38301^USA^^^MADISON||^PRN^PH^^1^731^5028347||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240121
ORC|RE|WO2293847^West TN|WTH2024012200041^West TN Healthcare Jackson^44D0509876^CLIA|||||||||1293847056^VICKERS^ANTONIO^L^^^^NPI^L^^^NPI||^WPN^PH^^1^731^4918273|||||||Jackson Family Medicine^L^^^^NPI^^^^^1638291047|620 Skyline Dr^^JACKSON^TN^38301^USA
OBR|1|WO2293847^West TN|WTH2024012200041^West TN Healthcare Jackson^44D0509876^CLIA|80382-5^Influenza virus A RNA [Presence] in Nasopharynx by NAA with non-probe detection^LN|||20240121143000-0600|||||||||1293847056^VICKERS^ANTONIO^L^^^^NPI^L^^^NPI|^WPN^PH^^1^731^4918273|||||20240122150000-0600|||F
OBX|1|CWE|80382-5^Influenza virus A RNA [Presence] in Nasopharynx by NAA with non-probe detection^LN|1|260373001^Detected^SCT||Not Detected|260373001^Detected^SCT|||F|||20240121143000-0600|44D0509876^West TN Healthcare Jackson^CLIA||||Cepheid Xpert Xpress Flu^Cepheid^K201495^^20231001||20240122150000-0600||||West TN Healthcare Jackson^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0509876|620 Skyline Dr^^JACKSON^TN^38301^USA
SPM|1|^WTH2024012200041||258500001^Nasopharyngeal swab^SCT|||||||||||||20240121143000-0600|20240121150000-0600
```

---

## 7. ORU^R01 - Tuberculosis culture positive from Nashville state lab

```
MSH|^~\&|TN_State_Lab_LIS|Tennessee State Public Health Lab^44D0512345^CLIA|TNDOH|TN_DOH_ELR|20240830112045-0600||ORU^R01^ORU_R01|TSPH20240830112045887|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|TN State Lab|1.5|StarLIMS|Binary ID 20240601||20240601
PID|1||TSPH38174926^^^Tennessee State Public Health Lab&44D0512345&CLIA^PI||PHAM^QUANG^MINH^^^^L||19510714|M||2028-9^Asian^CDCREC|3218 NOLENSVILLE PIKE^^NASHVILLE^TN^37211^USA^^^DAVIDSON||^PRN^PH^^1^615^7382941||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240715
ORC|RE|SO9918273^TN State Lab|TSPH2024083000019^Tennessee State Public Health Lab^44D0512345^CLIA|||||||||1728394016^SHELTON^HEATHER^D^^^^NPI^L^^^NPI||^WPN^PH^^1^615^2839471|||||||Metro Nashville Public Health Dept^L^^^^NPI^^^^^1847293105|311 23rd Ave N^^NASHVILLE^TN^37203^USA
OBR|1|SO9918273^TN State Lab|TSPH2024083000019^Tennessee State Public Health Lab^44D0512345^CLIA|543-9^Mycobacterium tuberculosis complex rRNA [Presence] in Specimen by NAA with probe detection^LN|||20240715080000-0600|||||||||1728394016^SHELTON^HEATHER^D^^^^NPI^L^^^NPI|^WPN^PH^^1^615^2839471|||||20240830110000-0600|||F
OBX|1|CWE|543-9^Mycobacterium tuberculosis complex rRNA [Presence] in Specimen by NAA with probe detection^LN|1|260373001^Detected^SCT||Not Detected|260373001^Detected^SCT|||F|||20240715080000-0600|44D0512345^Tennessee State Public Health Lab^CLIA||||Hologic Gen-Probe Amplified MTD^Hologic^K970361^^20230301||20240830100000-0600||||Tennessee State Public Health Lab^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0512345|630 Hart Ln^^NASHVILLE^TN^37216^USA
OBX|2|CWE|546-2^Mycobacterium sp identified in Specimen by Organism specific culture^LN|1|113861009^Mycobacterium tuberculosis^SCT||No growth||||F|||20240715080000-0600|44D0512345^Tennessee State Public Health Lab^CLIA||||||20240830110000-0600||||Tennessee State Public Health Lab^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0512345|630 Hart Ln^^NASHVILLE^TN^37216^USA
SPM|1|^TSPH2024083000019||119334006^Sputum specimen^SCT|||||||||||||20240715080000-0600|20240715090000-0600
```

---

## 8. ACK - Acknowledgment for accepted COVID-19 result submission

```
MSH|^~\&|TNDOH|TN_DOH_ELR|LabCorpTN|LabCorp Nashville^05D2191065^CLIA|20240315084500-0600||ACK^R01^ACK|TNDOH20240315084500001|P|2.5.1|||NE|NE
MSA|AA|LC20240315083022001||Message accepted and processed successfully
```

---

## 9. ACK - Acknowledgment with error for rejected message (missing PID)

```
MSH|^~\&|TNDOH|TN_DOH_ELR|QuestDiagTN|Quest Memphis^44D2033844^CLIA|20240413091000-0600||ACK^R01^ACK|TNDOH20240413091000447|P|2.5.1|||NE|NE
MSA|AE|QD20240412183022445||Message rejected - required segment missing
ERR||PID^1|101^Required field missing^HL70357|E|^^^PID-5 Patient Name is required for ELR submission|||Patient name (PID-5) is required per Tennessee ELR Implementation Guide Section 3.2
```

---

## 10. ORU^R01 - Hepatitis B surface antigen positive from Murfreesboro

```
MSH|^~\&|TriStar_LIS|TriStar StoneCrest Medical Center^44D0933218^CLIA|TNDOH|TN_DOH_ELR|20240225134500-0600||ORU^R01^ORU_R01|SC20240225134500221|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|TriStar Medical|3.8|Cerner PathNet|Binary ID 20240101||20240101
PID|1||SC74829316^^^TriStar StoneCrest Medical Center&44D0933218&CLIA^PI||WHITFIELD^CAROL^JEAN^^^^L||19730829|F||2106-3^White^CDCREC|1520 MEMORIAL BLVD^^MURFREESBORO^TN^37129^USA^^^RUTHERFORD||^PRN^PH^^1^629^4182937||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240224
ORC|RE|SO1127384^TriStar|SC2024022500078^TriStar StoneCrest Medical Center^44D0933218^CLIA|||||||||1472839106^CALDWELL^REGINALD^S^^^^NPI^L^^^NPI||^WPN^PH^^1^615^5829314|||||||Murfreesboro Medical Clinic^L^^^^NPI^^^^^1293847506|1272 Garrison Dr^^MURFREESBORO^TN^37129^USA
OBR|1|SO1127384^TriStar|SC2024022500078^TriStar StoneCrest Medical Center^44D0933218^CLIA|5195-3^Hepatitis B virus surface Ag [Presence] in Serum^LN|||20240224110000-0600|||||||||1472839106^CALDWELL^REGINALD^S^^^^NPI^L^^^NPI|^WPN^PH^^1^615^5829314|||||20240225130000-0600|||F
OBX|1|CWE|5195-3^Hepatitis B virus surface Ag [Presence] in Serum^LN|1|10828004^Positive^SCT||Negative|10828004^Positive^SCT|||F|||20240224110000-0600|44D0933218^TriStar StoneCrest Medical Center^CLIA||||Abbott ARCHITECT HBsAg Qualitative II^Abbott^P160035^^20230701||20240225130000-0600||||TriStar StoneCrest Medical Center^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0933218|200 StoneCrest Blvd^^SMYRNA^TN^37167^USA
SPM|1|^SC2024022500078||119364003^Serum specimen^SCT|||||||||||||20240224110000-0600|20240224120000-0600
```

---

## 11. ORU^R01 - Group B Streptococcus positive with encapsulated PDF report from Franklin

```
MSH|^~\&|Williamson_Medical_LIS|Williamson Medical Center^44D0929174^CLIA|TNDOH|TN_DOH_ELR|20240910143322-0600||ORU^R01^ORU_R01|WMC20240910143322109|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|Williamson Medical|2.3|MEDITECH Magic|Binary ID 20240501||20240501
PID|1||WMC61293847^^^Williamson Medical Center&44D0929174&CLIA^PI||LOVELL^STEPHANIE^MARIE^^^^L||19940411|F||2106-3^White^CDCREC|1108 MURFREESBORO RD^^FRANKLIN^TN^37064^USA^^^WILLIAMSON||^PRN^PH^^1^615^9382741||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240909
ORC|RE|WO4412398^Williamson|WMC2024091000033^Williamson Medical Center^44D0929174^CLIA|||||||||1639284710^BOWMAN^RICHARD^C^^^^NPI^L^^^NPI||^WPN^PH^^1^615^2739481|||||||Cool Springs OBGYN^L^^^^NPI^^^^^1482937106|3017 Church St^^FRANKLIN^TN^37064^USA
OBR|1|WO4412398^Williamson|WMC2024091000033^Williamson Medical Center^44D0929174^CLIA|580-1^Streptococcus agalactiae [Presence] in Vagina by Organism specific culture^LN|||20240909150000-0600|||||||||1639284710^BOWMAN^RICHARD^C^^^^NPI^L^^^NPI|^WPN^PH^^1^615^2739481|||||20240910140000-0600|||F
OBX|1|CWE|580-1^Streptococcus agalactiae [Presence] in Vagina by Organism specific culture^LN|1|260373001^Detected^SCT||Not Detected|260373001^Detected^SCT|||F|||20240909150000-0600|44D0929174^Williamson Medical Center^CLIA||||||20240910140000-0600||||Williamson Medical Center^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0929174|4321 Carothers Pkwy^^FRANKLIN^TN^37067^USA
OBX|2|ED|18725-2^Microbiology studies (set)^LN|2|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSAxMCAwIFIKPj4KPj4KL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KL0NvbnRlbnRzIDQgMCBSCj4+CmVuZG9iago=||||||F|||20240909150000-0600|44D0929174^Williamson Medical Center^CLIA||||||20240910140000-0600||||Williamson Medical Center^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0929174|4321 Carothers Pkwy^^FRANKLIN^TN^37067^USA
SPM|1|^WMC2024091000033||258520000^Vaginal swab^SCT|||||||||||||20240909150000-0600|20240909160000-0600
```

---

## 12. ORU^R01 - Lead blood level elevated in pediatric patient from Memphis

```
MSH|^~\&|LeBonheur_LIS|Le Bonheur Children's Hospital^44D0508891^CLIA|TNDOH|TN_DOH_ELR|20240405093012-0600||ORU^R01^ORU_R01|LB20240405093012665|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|Le Bonheur|6.1|Epic Beaker|Binary ID 20240301||20240301
PID|1||LB39471826^^^Le Bonheur Children's Hospital&44D0508891&CLIA^PI||PATTON^ELIJAH^MARCUS^^^^L||20210608|M||2054-5^Black or African American^CDCREC|1592 GETWELL RD^^MEMPHIS^TN^38111^USA^^^SHELBY||^PRN^PH^^1^901^2847193||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240404
ORC|RE|LO8821934^Le Bonheur|LB2024040500091^Le Bonheur Children's Hospital^44D0508891^CLIA|||||||||1849273016^CRAWFORD^TONYA^V^^^^NPI^L^^^NPI||^WPN^PH^^1^901^6392814|||||||Memphis Pediatric Associates^L^^^^NPI^^^^^1538294710|6005 Park Ave^^MEMPHIS^TN^38119^USA
OBR|1|LO8821934^Le Bonheur|LB2024040500091^Le Bonheur Children's Hospital^44D0508891^CLIA|10368-9^Lead [Mass/volume] in Capillary blood^LN|||20240404091500-0600|||||||||1849273016^CRAWFORD^TONYA^V^^^^NPI^L^^^NPI|^WPN^PH^^1^901^6392814|||||20240405090000-0600|||F
OBX|1|NM|10368-9^Lead [Mass/volume] in Capillary blood^LN|1|8.2|ug/dL^microgram per deciliter^UCUM|<3.5|H|||F|||20240404091500-0600|44D0508891^Le Bonheur Children's Hospital^CLIA||||LeadCare II^Magellan^K082381^^20230501||20240405090000-0600||||Le Bonheur Children's Hospital^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0508891|848 Adams Ave^^MEMPHIS^TN^38103^USA
SPM|1|^LB2024040500091||122554006^Capillary blood specimen^SCT|||||||||||||20240404091500-0600|20240404093000-0600
```

---

## 13. OML^O21 - Lab order for HIV confirmatory testing from Johnson City

```
MSH|^~\&|BH_Johnson_City_LIS|Ballad Health Johnson City^44D1055238^CLIA|TNDOH|TN_DOH_ELR|20240801081530-0600||OML^O21^OML_O21|BH20240801081530102|P|2.5.1|||NE|NE|||||LAB_PRU^Lab_Processing^2.16.840.1.113883.9.16^ISO
SFT|Ballad Health|1.8|athenahealth|Binary ID 20240601||20240601
PID|1||BH74829316^^^Ballad Health Johnson City&44D1055238&CLIA^PI||LAWSON^RANDALL^SCOTT^^^^L||19800301|M||2106-3^White^CDCREC|2408 BROWNS MILL RD^^JOHNSON CITY^TN^37604^USA^^^WASHINGTON||^PRN^PH^^1^423^7291483||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240731
ORC|NW|EO5529183^Ballad Health|||||^^^20240801081500-0600||20240801081530-0600|||1382947106^NEWBERRY^PAULA^T^^^^NPI^L^^^NPI||^WPN^PH^^1^423^8291374|||||||Ballad Health Physicians^L^^^^NPI^^^^^1529384710|325 N State of Franklin Rd^^JOHNSON CITY^TN^37604^USA
OBR|1|EO5529183^Ballad Health||56888-1^HIV 1+2 Ab+HIV1 p24 Ag [Presence] in Serum or Plasma by Immunoassay^LN|||20240731140000-0600||||||||||1382947106^NEWBERRY^PAULA^T^^^^NPI^L^^^NPI|^WPN^PH^^1^423^8291374
OBR|2|EO5529183^Ballad Health||30361-0^HIV 2 Ab [Presence] in Serum or Plasma by Immunoassay^LN|||20240731140000-0600||||||||||1382947106^NEWBERRY^PAULA^T^^^^NPI^L^^^NPI|^WPN^PH^^1^423^8291374
SPM|1|||119364003^Serum specimen^SCT|||||||||||||20240731140000-0600|20240731143000-0600
```

---

## 14. ORU^R01 - Salmonella culture positive from Kingsport

```
MSH|^~\&|Holston_Valley_LIS|Holston Valley Medical Center^44D0504432^CLIA|TNDOH|TN_DOH_ELR|20240619171200-0600||ORU^R01^ORU_R01|HV20240619171200448|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|Holston Valley Medical|4.2|Cerner Millennium|Binary ID 20240401||20240401
PID|1||HV62918473^^^Holston Valley Medical Center&44D0504432&CLIA^PI||RAMSEY^MEGAN^BROOKE^^^^L||19880925|F||2106-3^White^CDCREC|3401 MEMORIAL BLVD^^KINGSPORT^TN^37664^USA^^^SULLIVAN||^PRN^PH^^1^423^2938471||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240617
ORC|RE|HO7738291^Holston Valley|HV2024061900027^Holston Valley Medical Center^44D0504432^CLIA|||||||||1947283016^BURRIS^STEPHEN^G^^^^NPI^L^^^NPI||^WPN^PH^^1^423^6182739|||||||Sullivan County Health Dept^L^^^^NPI^^^^^1638472910|154 Blountville Bypass^^BLOUNTVILLE^TN^37617^USA
OBR|1|HO7738291^Holston Valley|HV2024061900027^Holston Valley Medical Center^44D0504432^CLIA|625-4^Bacteria identified in Stool by Culture^LN|||20240617083000-0600|||||||||1947283016^BURRIS^STEPHEN^G^^^^NPI^L^^^NPI|^WPN^PH^^1^423^6182739|||||20240619165000-0600|||F
OBX|1|CWE|625-4^Bacteria identified in Stool by Culture^LN|1|27268008^Genus Salmonella^SCT||No growth|27268008^Genus Salmonella^SCT|||F|||20240617083000-0600|44D0504432^Holston Valley Medical Center^CLIA||||||20240619165000-0600||||Holston Valley Medical Center^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0504432|130 W Ravine Rd^^KINGSPORT^TN^37660^USA
OBX|2|CWE|20951-0^Salmonella sp serotype [Identifier] in Isolate^LN|2|115407004^Salmonella enterica subspecies enterica serovar Typhimurium^SCT||||||F|||20240617083000-0600|44D0504432^Holston Valley Medical Center^CLIA||||||20240619165000-0600||||Holston Valley Medical Center^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0504432|130 W Ravine Rd^^KINGSPORT^TN^37660^USA
SPM|1|^HV2024061900027||119339001^Stool specimen^SCT|||||||||||||20240617083000-0600|20240617091500-0600
```

---

## 15. ORU^R01 - Pertussis PCR positive from Germantown

```
MSH|^~\&|Methodist_Germantown_LIS|Methodist Le Bonheur Germantown^44D0912847^CLIA|TNDOH|TN_DOH_ELR|20240204102245-0600||ORU^R01^ORU_R01|MLG20240204102245993|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|Methodist Le Bonheur|5.5|Epic Beaker|Binary ID 20240101||20240101
PID|1||MLG71829364^^^Methodist Le Bonheur Germantown&44D0912847&CLIA^PI||SUTTON^AMELIA^KATE^^^^L||20180314|F||2106-3^White^CDCREC|1645 FOREST HILL IRENE RD^^GERMANTOWN^TN^38138^USA^^^SHELBY||^PRN^PH^^1^901^4728391||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240203
ORC|RE|MO6629183^Methodist|MLG2024020400058^Methodist Le Bonheur Germantown^44D0912847^CLIA|||||||||1263847291^TRUONG^LINDA^H^^^^NPI^L^^^NPI||^WPN^PH^^1^901^3829174|||||||Germantown Pediatrics^L^^^^NPI^^^^^1748293106|7691 Poplar Ave^^GERMANTOWN^TN^38138^USA
OBR|1|MO6629183^Methodist|MLG2024020400058^Methodist Le Bonheur Germantown^44D0912847^CLIA|23826-1^Bordetella pertussis DNA [Presence] in Specimen by NAA with probe detection^LN|||20240203143000-0600|||||||||1263847291^TRUONG^LINDA^H^^^^NPI^L^^^NPI|^WPN^PH^^1^901^3829174|||||20240204100000-0600|||F
OBX|1|CWE|23826-1^Bordetella pertussis DNA [Presence] in Specimen by NAA with probe detection^LN|1|260373001^Detected^SCT||Not Detected|260373001^Detected^SCT|||F|||20240203143000-0600|44D0912847^Methodist Le Bonheur Germantown^CLIA||||Hologic Panther Fusion Bordetella^Hologic^K190332^^20230801||20240204100000-0600||||Methodist Le Bonheur Germantown^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0912847|7691 Poplar Ave^^GERMANTOWN^TN^38138^USA
SPM|1|^MLG2024020400058||258500001^Nasopharyngeal swab^SCT|||||||||||||20240203143000-0600|20240203150000-0600
```

---

## 16. ORU^R01 - RSV positive in infant from Cookeville

```
MSH|^~\&|Cookeville_Regional_LIS|Cookeville Regional Medical Center^44D0502918^CLIA|TNDOH|TN_DOH_ELR|20240115174530-0600||ORU^R01^ORU_R01|CRMC20240115174530771|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|Cookeville Regional|3.1|MEDITECH Expanse|Binary ID 20231101||20231101
PID|1||CRMC82947316^^^Cookeville Regional Medical Center&44D0502918&CLIA^PI||BREWER^LIAM^COLTON^^^^L||20230918|M||2106-3^White^CDCREC|1025 SOUTH WILLOW AVE^^COOKEVILLE^TN^38501^USA^^^PUTNAM||^PRN^PH^^1^931^8274913||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240114
ORC|RE|CO9918273^Cookeville|CRMC2024011500044^Cookeville Regional Medical Center^44D0502918^CLIA|||||||||1538274910^DOTSON^RACHEL^E^^^^NPI^L^^^NPI||^WPN^PH^^1^931^4819273|||||||Cookeville Pediatric Associates^L^^^^NPI^^^^^1627394810|338 N Washington Ave^^COOKEVILLE^TN^38501^USA
OBR|1|CO9918273^Cookeville|CRMC2024011500044^Cookeville Regional Medical Center^44D0502918^CLIA|92131-2^Respiratory syncytial virus RNA [Presence] in Respiratory specimen by NAA with probe detection^LN|||20240114161500-0600|||||||||1538274910^DOTSON^RACHEL^E^^^^NPI^L^^^NPI|^WPN^PH^^1^931^4819273|||||20240115170000-0600|||F
OBX|1|CWE|92131-2^Respiratory syncytial virus RNA [Presence] in Respiratory specimen by NAA with probe detection^LN|1|260373001^Detected^SCT||Not Detected|260373001^Detected^SCT|||F|||20240114161500-0600|44D0502918^Cookeville Regional Medical Center^CLIA||||BioFire FilmArray Respiratory Panel^bioMerieux^K181214^^20231001||20240115170000-0600||||Cookeville Regional Medical Center^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0502918|1 Medical Center Blvd^^COOKEVILLE^TN^38501^USA
SPM|1|^CRMC2024011500044||258500001^Nasopharyngeal swab^SCT|||||||||||||20240114161500-0600|20240114163000-0600
```

---

## 17. ORU^R01 - Mpox (monkeypox) PCR positive with encapsulated image from Nashville

```
MSH|^~\&|Vanderbilt_LIS|Vanderbilt University Medical Center^44D0505578^CLIA|TNDOH|TN_DOH_ELR|20240923085500-0600||ORU^R01^ORU_R01|VUMC20240923085500334|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|Vanderbilt University Medical Center|7.2|Epic Beaker|Binary ID 20240801||20240801
PID|1||VUMC84729163^^^Vanderbilt University Medical Center&44D0505578&CLIA^PI||HARGROVE^JULIAN^WADE^^^^L||19910507|M||2106-3^White^CDCREC|1814 21ST AVE S^^NASHVILLE^TN^37212^USA^^^DAVIDSON||^PRN^PH^^1^615^3928471||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240921
ORC|RE|VO3318274^Vanderbilt|VUMC2024092300015^Vanderbilt University Medical Center^44D0505578^CLIA|||||||||1472893016^AGRAWAL^SUNITA^P^^^^NPI^L^^^NPI||^WPN^PH^^1^615^6182934|||||||Vanderbilt Infectious Disease Clinic^L^^^^NPI^^^^^1839274106|A-2200 Medical Center North^^NASHVILLE^TN^37232^USA
OBR|1|VO3318274^Vanderbilt|VUMC2024092300015^Vanderbilt University Medical Center^44D0505578^CLIA|100383-5^Monkeypox virus DNA [Presence] in Specimen by NAA with probe detection^LN|||20240921100000-0600|||||||||1472893016^AGRAWAL^SUNITA^P^^^^NPI^L^^^NPI|^WPN^PH^^1^615^6182934|||||20240923083000-0600|||F
OBX|1|CWE|100383-5^Monkeypox virus DNA [Presence] in Specimen by NAA with probe detection^LN|1|260373001^Detected^SCT||Not Detected|260373001^Detected^SCT|||F|||20240921100000-0600|44D0505578^Vanderbilt University Medical Center^CLIA||||CDC Orthopoxvirus Real-Time PCR^CDC^EUA220018^^20230901||20240923083000-0600||||Vanderbilt University Medical Center^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0505578|1211 Medical Center Dr^^NASHVILLE^TN^37232^USA
OBX|2|ED|100383-5^Monkeypox virus DNA [Presence] in Specimen by NAA with probe detection^LN|2|^image^jpeg^Base64^/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAQABADASIAAhEBAxEB/8QAFwAAAwEAAAAAAAAAAAAAAAAABQYHCP/EACYQAAIBAwMDBAMAAAAAAAAAAAECAwQFEQAGIQcSMRMUIkFRYXH/xAAVAQEBAAAAAAAAAAAAAAAAAAADBf/EABwRAAICAgMAAAAAAAAAAAAAAAECABEDIRIxQf/aAAwDAQACEQMRAD8AZ9x7rpNtSRw1tRHDLKcIjNyzfwDzpF3R1gtrRPBZYDcakAhpE4jQ/onnP8Gub9SL/LuPcVXcpPBlbCKeAgRD8aJb36b3bbVm+8q1hEYOJImYupP0MjxnnQMcL2vqb2YMi4l/9k=||||||F|||20240921100000-0600|44D0505578^Vanderbilt University Medical Center^CLIA||||||20240923083000-0600||||Vanderbilt University Medical Center^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0505578|1211 Medical Center Dr^^NASHVILLE^TN^37232^USA
SPM|1|^VUMC2024092300015||258505006^Skin lesion swab^SCT|||||||||||||20240921100000-0600|20240921103000-0600
```

---

## 18. OML^O21 - Lab order for TB Quantiferon testing from Columbia

```
MSH|^~\&|Maury_Regional_LIS|Maury Regional Medical Center^44D0506782^CLIA|TNDOH|TN_DOH_ELR|20240305141000-0600||OML^O21^OML_O21|MRMC20240305141000556|P|2.5.1|||NE|NE|||||LAB_PRU^Lab_Processing^2.16.840.1.113883.9.16^ISO
SFT|Maury Regional|4.0|Cerner Millennium|Binary ID 20240201||20240201
PID|1||MRMC53918247^^^Maury Regional Medical Center&44D0506782&CLIA^PI||GREER^WILLIAM^HAROLD^^^^L||19720116|M||2106-3^White^CDCREC|1205 TROTWOOD AVE^^COLUMBIA^TN^38401^USA^^^MAURY||^PRN^PH^^1^931^7291843||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240304
ORC|NW|MO1129384^Maury Regional|||||^^^20240305140000-0600||20240305141000-0600|||1724839106^PARSONS^DENISE^A^^^^NPI^L^^^NPI||^WPN^PH^^1^931^4829137|||||||Maury County Health Dept^L^^^^NPI^^^^^1382749106|1909 Hampshire Pike^^COLUMBIA^TN^38401^USA
OBR|1|MO1129384^Maury Regional||71774-4^Mycobacterium tuberculosis stimulated gamma interferon [Presence] in Blood^LN|||20240304090000-0600||||||||||1724839106^PARSONS^DENISE^A^^^^NPI^L^^^NPI|^WPN^PH^^1^931^4829137
SPM|1|||119297000^Blood specimen^SCT|||||||||||||20240304090000-0600|20240304093000-0600
```

---

## 19. ORU^R01 - Carbapenem-resistant Enterobacteriaceae (CRE) from Vanderbilt

```
MSH|^~\&|Vanderbilt_LIS|Vanderbilt University Medical Center^44D0505578^CLIA|TNDOH|TN_DOH_ELR|20241002153300-0600||ORU^R01^ORU_R01|VUMC20241002153300882|P|2.5.1|||NE|NE|||||PHLabReport-NoAck^ELR_Receiver^2.16.840.1.113883.9.11^ISO
SFT|Vanderbilt University Medical Center|7.2|Epic Beaker|Binary ID 20240801||20240801
PID|1||VUMC41738296^^^Vanderbilt University Medical Center&44D0505578&CLIA^PI||CANTRELL^DOROTHY^RUTH^^^^L||19451222|F||2106-3^White^CDCREC|4012 CENTRAL PIKE^^HERMITAGE^TN^37076^USA^^^DAVIDSON||^PRN^PH^^1^615^4918273||||||||||||2186-5^Not Hispanic or Latino^CDCREC|||||||20240928
ORC|RE|VO8827361^Vanderbilt|VUMC2024100200038^Vanderbilt University Medical Center^44D0505578^CLIA|||||||||1839274106^FOSTER^DENISE^W^^^^NPI^L^^^NPI||^WPN^PH^^1^615^7291348|||||||Vanderbilt Internal Medicine^L^^^^NPI^^^^^1294738106|2525 West End Ave^^NASHVILLE^TN^37203^USA
OBR|1|VO8827361^Vanderbilt|VUMC2024100200038^Vanderbilt University Medical Center^44D0505578^CLIA|6463-4^Bacteria identified in Blood by Culture^LN|||20240928140000-0600|||||||||1839274106^FOSTER^DENISE^W^^^^NPI^L^^^NPI|^WPN^PH^^1^615^7291348|||||20241002150000-0600|||F
OBX|1|CWE|6463-4^Bacteria identified in Blood by Culture^LN|1|112283007^Klebsiella pneumoniae^SCT||No growth|112283007^Klebsiella pneumoniae^SCT|||F|||20240928140000-0600|44D0505578^Vanderbilt University Medical Center^CLIA||||||20241002150000-0600||||Vanderbilt University Medical Center^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0505578|1211 Medical Center Dr^^NASHVILLE^TN^37232^USA
OBX|2|CWE|18907-6^Meropenem [Susceptibility] by Minimum inhibitory concentration (MIC)^LN|2|30714006^Resistant^SCT||<=1 S|30714006^Resistant^SCT|||F|||20240928140000-0600|44D0505578^Vanderbilt University Medical Center^CLIA||||||20241002150000-0600||||Vanderbilt University Medical Center^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0505578|1211 Medical Center Dr^^NASHVILLE^TN^37232^USA
OBX|3|NM|18907-6^Meropenem [Susceptibility] by Minimum inhibitory concentration (MIC)^LN|3|16|ug/mL^microgram per milliliter^UCUM|<=1||||F|||20240928140000-0600|44D0505578^Vanderbilt University Medical Center^CLIA||||||20241002150000-0600||||Vanderbilt University Medical Center^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0505578|1211 Medical Center Dr^^NASHVILLE^TN^37232^USA
OBX|4|CWE|85827-4^Carbapenemase [Presence] in Isolate^LN|4|260373001^Detected^SCT||Not Detected|260373001^Detected^SCT|||F|||20240928140000-0600|44D0505578^Vanderbilt University Medical Center^CLIA||||Modified Carbapenem Inactivation Method^CLSI^M100-S28^^20231001||20241002150000-0600||||Vanderbilt University Medical Center^^^^^CLIA&2.16.840.1.113883.4.7&ISO^XX^^^44D0505578|1211 Medical Center Dr^^NASHVILLE^TN^37232^USA
SPM|1|^VUMC2024100200038||119297000^Blood specimen^SCT|||||||||||||20240928140000-0600|20240928143000-0600
```

---

## 20. ACK - Application accept acknowledgment for batch ELR submission

```
MSH|^~\&|TNDOH|TN_DOH_ELR|Vanderbilt_LIS|Vanderbilt University Medical Center^44D0505578^CLIA|20241002160000-0600||ACK^R01^ACK|TNDOH20241002160000882|P|2.5.1|||NE|NE
MSA|AA|VUMC20241002153300882||Message accepted - batch of 12 ELR results processed successfully
MSA|AA|VUMC20241002153301001||Message accepted
MSA|AA|VUMC20241002153301002||Message accepted
```
