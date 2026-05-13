# Heilsuvera (Helix Health) - real HL7v2 ER7 messages

---

## 1. ADT^A04 - Patient portal registration

```
MSH|^~\&|HEILSUVERA|IS_NATIONAL_HEALTH|SAGA|LANDSPITALI|20240315091200||ADT^A04^ADT_A01|MSG00001|P|2.5|||AL|NE||IS
EVN|A04|20240315091200|||PORTAL_REG
PID|1||2607861527^^^ISLAND^KT||Bjarnason^Þórmundur^^^Hr||19860726|M|||Suðurmýri 18^^Seltjarnarnes^^170^IS||^PRN^PH^^^354^5610284||IS|S|||||2607861527
PV1|1|O|PORTAL^^^^HLSV|||||||||||||||PORTAL|||||||||||||||||||||||||20240315091200
```

---

## 2. ADT^A08 - Update portal patient info

```
MSH|^~\&|HEILSUVERA|IS_NATIONAL_HEALTH|SAGA|LANDSPITALI|20240318142500||ADT^A08^ADT_A01|MSG00002|P|2.5|||AL|NE||IS
EVN|A08|20240318142500|||PORTAL_UPD
PID|1||1908763912^^^ISLAND^KT||Vésteinsdóttir^Aðalheiður^^^Frú||19760819|F|||Logafold 24^^Reykjavík^^112^IS||^PRN^PH^^^354^5871429||IS|M|||||1908763912
PV1|1|O|PORTAL^^^^HLSV|||||||||||||||PORTAL|||||||||||||||||||||||||20240318142500
```

---

## 3. ADT^A31 - Update demographics from portal

```
MSH|^~\&|HEILSUVERA|IS_NATIONAL_HEALTH|RAFÖRNINN|HEILSUGAESLA_HAMRABORG|20240320103000||ADT^A31^ADT_A05|MSG00003|P|2.5|||AL|NE||IS
EVN|A31|20240320103000|||DEMO_UPD
PID|1||0911952138^^^ISLAND^KT||Ægisson^Ölvir^^^Hr||19951109|M|||Trönuhjalli 7^^Kópavogur^^200^IS||^PRN^PH^^^354^5340972~^PRN^CP^^^354^7621384||IS|S|||||0911952138
PV1|1|O|HAMRABORG^^^^HGS|||||||||||||||PORTAL|||||||||||||||||||||||||20240320103000
```

---

## 4. ORU^R01 - Lab result forwarded to portal

```
MSH|^~\&|FLEXLAB|LANDSPITALI|HEILSUVERA|IS_NATIONAL_HEALTH|20240322080500||ORU^R01^ORU_R01|MSG00004|P|2.5|||AL|NE||IS
PID|1||2503891748^^^ISLAND^KT||Kjartansdóttir^Lóa^^^Frú||19890325|F|||Hellisbraut 9^^Reykjanesbær^^230^IS||^PRN^PH^^^354^4203851||IS|M|||||2503891748
PV1|1|O|LAB^^^^LSH|||||||||||||||REF|||||||||||||||||||||||||20240322080500
ORC|RE|ORD00004|FLX00004||CM||||20240322080500
OBR|1|ORD00004|FLX00004|CBC^Complete Blood Count^LN|||20240321150000|||||||20240321160000||1234^Hróðmarsson^Jökull^^^Dr|||||||20240322080500|||F
OBX|1|NM|WBC^White Blood Cells^LN||6.8|10*9/L|4.0-11.0|N|||F
OBX|2|NM|RBC^Red Blood Cells^LN||4.5|10*12/L|3.8-5.2|N|||F
OBX|3|NM|HGB^Hemoglobin^LN||138|g/L|120-160|N|||F
OBX|4|NM|PLT^Platelets^LN||245|10*9/L|150-400|N|||F
```

---

## 5. ORU^R01 - Radiology result forwarded to portal

```
MSH|^~\&|RAFÖRNINN|LANDSPITALI|HEILSUVERA|IS_NATIONAL_HEALTH|20240325114500||ORU^R01^ORU_R01|MSG00005|P|2.5|||AL|NE||IS
PID|1||1208782451^^^ISLAND^KT||Egilsson^Reynir^^^Hr||19780812|M|||Kópalind 4^^Mosfellsbær^^270^IS||^PRN^PH^^^354^5662014||IS|S|||||1208782451
PV1|1|O|RAD^^^^LSH|||||||||||||||REF|||||||||||||||||||||||||20240325114500
ORC|RE|ORD00005|RAD00005||CM||||20240325114500
OBR|1|ORD00005|RAD00005|71020^Chest X-Ray^CPT|||20240324090000|||||||20240324100000||5678^Marteinsdóttir^Auðbjörg^^^Dr|||||||20240325114500|||F
OBX|1|FT|71020^Chest X-Ray Report^CPT||Lungu hrein. Engin merki um þéttingu eða vökvasöfnun. Hjarta af eðlilegri stærð.||||||F
```

---

## 6. ORU^R01 - Medication list update

```
MSH|^~\&|LYFJAVAKI|IS_NATIONAL_HEALTH|HEILSUVERA|IS_NATIONAL_HEALTH|20240327160000||ORU^R01^ORU_R01|MSG00006|P|2.5|||AL|NE||IS
PID|1||0306923089^^^ISLAND^KT||Friðbjarnarson^Hávarður^^^Hr||19920603|M|||Norðurás 22^^Akureyri^^603^IS||^PRN^PH^^^354^4624715||IS|S|||||0306923089
PV1|1|O|PHARM^^^^LYFJAV|||||||||||||||REF|||||||||||||||||||||||||20240327160000
ORC|RE|ORD00006|LYF00006||CM||||20240327160000
OBR|1|ORD00006|LYF00006|MEDLIST^Medication List^L|||20240327150000|||||||20240327155000||9012^Sturludóttir^Vala^^^Dr|||||||20240327160000|||F
OBX|1|FT|MED1^Active Medication^L||Atorvastatin 20mg, 1 tafla daglega||||||F
OBX|2|FT|MED2^Active Medication^L||Omeprazol 20mg, 1 tafla daglega||||||F
OBX|3|FT|MED3^Active Medication^L||Metformin 500mg, 2 töflur tvisvar á dag||||||F
```

---

## 7. ORM^O01 - Prescription renewal request from portal

```
MSH|^~\&|HEILSUVERA|IS_NATIONAL_HEALTH|LYFJAVAKI|IS_NATIONAL_HEALTH|20240401093000||ORM^O01^ORM_O01|MSG00007|P|2.5|||AL|NE||IS
PID|1||0306923089^^^ISLAND^KT||Friðbjarnarson^Hávarður^^^Hr||19920603|M|||Norðurás 22^^Akureyri^^603^IS||^PRN^PH^^^354^4624715||IS|S|||||0306923089
PV1|1|O|PORTAL^^^^HLSV|||||||||||||||PORTAL|||||||||||||||||||||||||20240401093000
ORC|NW|ORD00007||||||^^^20240401093000^^R||20240401093000|0306923089^Friðbjarnarson^Hávarður|||||9012^Sturludóttir^Vala^^^Dr
OBR|1|ORD00007||RX_RENEW^Prescription Renewal^L|||20240401093000
RXO|1|Atorvastatin^20mg^L|20|mg|TAB|1 tafla daglega||G||90|TAB
```

---

## 8. SIU^S12 - Online appointment booking

```
MSH|^~\&|HEILSUVERA|IS_NATIONAL_HEALTH|SAGA|HEILSUGAESLA_SOLVANGI|20240403101500||SIU^S12^SIU_S12|MSG00008|P|2.5|||AL|NE||IS
SCH|APT00008|APT00008||||ROUTINE^Routine Visit^HL70276|CHECKUP^Annual Checkup^L|NORMAL|30|min|^^30^20240410090000^20240410093000
PID|1||2204833016^^^ISLAND^KT||Þrastardóttir^Sigfríður^^^Frú||19830422|F|||Bjarkargata 12^^Selfoss^^800^IS||^PRN^PH^^^354^4823071||IS|M|||||2204833016
PV1|1|O|SOLVANGI^^^^HGS|||||||||||||||REF|||||||||||||||||||||||||20240403101500
RGS|1|A
AIS|1|A|CHECKUP^Annual Checkup^L|20240410090000|0|min|30|min
AIG|1|A|3456^Vigfúsdóttir^Eyrún^^^Dr|DOCTOR
AIL|1|A|SOLVANGI_RM3^Stofa 3^L
```

---

## 9. SIU^S14 - Modify online appointment

```
MSH|^~\&|HEILSUVERA|IS_NATIONAL_HEALTH|SAGA|HEILSUGAESLA_SOLVANGI|20240405141000||SIU^S14^SIU_S12|MSG00009|P|2.5|||AL|NE||IS
SCH|APT00008|APT00008||||ROUTINE^Routine Visit^HL70276|CHECKUP^Annual Checkup^L|NORMAL|30|min|^^30^20240412140000^20240412143000
PID|1||2204833016^^^ISLAND^KT||Þrastardóttir^Sigfríður^^^Frú||19830422|F|||Bjarkargata 12^^Selfoss^^800^IS||^PRN^PH^^^354^4823071||IS|M|||||2204833016
PV1|1|O|SOLVANGI^^^^HGS|||||||||||||||REF|||||||||||||||||||||||||20240405141000
RGS|1|A
AIS|1|A|CHECKUP^Annual Checkup^L|20240412140000|0|min|30|min
AIG|1|A|3456^Vigfúsdóttir^Eyrún^^^Dr|DOCTOR
AIL|1|A|SOLVANGI_RM3^Stofa 3^L
```

---

## 10. MDM^T02 - Clinical summary for portal

```
MSH|^~\&|SAGA|LANDSPITALI|HEILSUVERA|IS_NATIONAL_HEALTH|20240408153000||MDM^T02^MDM_T02|MSG00010|P|2.5|||AL|NE||IS
EVN|T02|20240408153000
PID|1||2607861527^^^ISLAND^KT||Bjarnason^Þórmundur^^^Hr||19860726|M|||Suðurmýri 18^^Seltjarnarnes^^170^IS||^PRN^PH^^^354^5610284||IS|S|||||2607861527
PV1|1|I|MED3^^^^LSH|||||||||||||||ATT|||||||||||||||||||||||||20240405080000
TXA|1|CN^Clinical Note^L|TX|20240408150000|1234^Hróðmarsson^Jökull^^^Dr||20240408153000||||||DOC00010||AU||AV
OBX|1|FT|CLINSUM^Clinical Summary^L||Sjúklingur kom á bráðamóttöku vegna brjóstverkja. Hjartaþræðing framkvæmd. Engin þrenging greindist. Útskrifaður með ráðleggingum um lífsstílsbreytingar.||||||F
```

---

## 11. ORU^R01 - Vaccination record update

```
MSH|^~\&|SAGA|HEILSUGAESLA_HAMRABORG|HEILSUVERA|IS_NATIONAL_HEALTH|20240410091500||ORU^R01^ORU_R01|MSG00011|P|2.5|||AL|NE||IS
PID|1||1908763912^^^ISLAND^KT||Vésteinsdóttir^Aðalheiður^^^Frú||19760819|F|||Logafold 24^^Reykjavík^^112^IS||^PRN^PH^^^354^5871429||IS|M|||||1908763912
PV1|1|O|HAMRABORG^^^^HGS|||||||||||||||REF|||||||||||||||||||||||||20240410091500
ORC|RE|ORD00011|VAC00011||CM||||20240410091500
OBR|1|ORD00011|VAC00011|VACCINE^Vaccination Record^L|||20240410090000|||||||20240410091000||7890^Hauksson^Arngrímur^^^Dr|||||||20240410091500|||F
OBX|1|CE|30971-6^Vaccine Type^LN||141^Influenza, seasonal^CVX||||||F
OBX|2|TS|30952-6^Vaccination Date^LN||20240410090000||||||F
OBX|3|ST|30959-1^Lot Number^LN||FLU2024A987||||||F
OBX|4|CE|30956-7^Manufacturer^LN||PMC^Pfizer^MVX||||||F
```

---

## 12. ORU^R01 - Allergy list update

```
MSH|^~\&|SAGA|LANDSPITALI|HEILSUVERA|IS_NATIONAL_HEALTH|20240412134500||ORU^R01^ORU_R01|MSG00012|P|2.5|||AL|NE||IS
PID|1||0911952138^^^ISLAND^KT||Ægisson^Ölvir^^^Hr||19951109|M|||Trönuhjalli 7^^Kópavogur^^200^IS||^PRN^PH^^^354^5340972||IS|S|||||0911952138
PV1|1|O|ALLERGY^^^^LSH|||||||||||||||REF|||||||||||||||||||||||||20240412134500
ORC|RE|ORD00012|ALG00012||CM||||20240412134500
OBR|1|ORD00012|ALG00012|ALRGLIST^Allergy List^L|||20240412130000|||||||20240412134000||5678^Marteinsdóttir^Auðbjörg^^^Dr|||||||20240412134500|||F
OBX|1|CE|ALG1^Allergy^L||70618^Penicillin^RxNorm||||||F
OBX|2|ST|ALG1_REACT^Reaction^L||Útbrot og þroti||||||F
OBX|3|CE|ALG1_SEV^Severity^L||MI^Moderate^HL70128||||||F
OBX|4|CE|ALG2^Allergy^L||2670^Codeine^RxNorm||||||F
OBX|5|ST|ALG2_REACT^Reaction^L||Ógleði og sundl||||||F
OBX|6|CE|ALG2_SEV^Severity^L||MI^Moderate^HL70128||||||F
```

---

## 13. ORU^R01 - Health summary with base64 ED OBX (PDF health summary)

```
MSH|^~\&|SAGA|LANDSPITALI|HEILSUVERA|IS_NATIONAL_HEALTH|20240415100000||ORU^R01^ORU_R01|MSG00013|P|2.5|||AL|NE||IS
PID|1||2607861527^^^ISLAND^KT||Bjarnason^Þórmundur^^^Hr||19860726|M|||Suðurmýri 18^^Seltjarnarnes^^170^IS||^PRN^PH^^^354^5610284||IS|S|||||2607861527
PV1|1|O|MED^^^^LSH|||||||||||||||REF|||||||||||||||||||||||||20240415100000
ORC|RE|ORD00013|DOC00013||CM||||20240415100000
OBR|1|ORD00013|DOC00013|HLTHSUM^Health Summary^L|||20240415090000|||||||20240415095000||1234^Hróðmarsson^Jökull^^^Dr|||||||20240415100000|||F
OBX|1|ED|PDF^Health Summary^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCg==||||||F
```

---

## 14. ADT^A40 - Merge portal patient records

```
MSH|^~\&|HEILSUVERA|IS_NATIONAL_HEALTH|SAGA|LANDSPITALI|20240418112000||ADT^A40^ADT_A39|MSG00014|P|2.5|||AL|NE||IS
EVN|A40|20240418112000|||MERGE
PID|1||2503891748^^^ISLAND^KT||Kjartansdóttir^Lóa^^^Frú||19890325|F|||Hellisbraut 9^^Reykjanesbær^^230^IS||^PRN^PH^^^354^4203851||IS|M|||||2503891748
MRG|2503890001^^^ISLAND^KT||||||
PV1|1|O|PORTAL^^^^HLSV|||||||||||||||PORTAL|||||||||||||||||||||||||20240418112000
```

---

## 15. ORU^R01 - Discharge summary for portal

```
MSH|^~\&|SAGA|LANDSPITALI|HEILSUVERA|IS_NATIONAL_HEALTH|20240420163000||ORU^R01^ORU_R01|MSG00015|P|2.5|||AL|NE||IS
PID|1||1208782451^^^ISLAND^KT||Egilsson^Reynir^^^Hr||19780812|M|||Kópalind 4^^Mosfellsbær^^270^IS||^PRN^PH^^^354^5662014||IS|S|||||1208782451
PV1|1|I|SURG2^^^^LSH|||||||||||||||ATT|||||||||||||||||||||||||20240417080000
ORC|RE|ORD00015|DIS00015||CM||||20240420163000
OBR|1|ORD00015|DIS00015|DISCHARGE^Discharge Summary^L|||20240420150000|||||||20240420160000||4321^Þorgeirsson^Bárður^^^Dr|||||||20240420163000|||F
OBX|1|FT|DIAG^Diagnosis^L||Bráð botnlangabólga||||||F
OBX|2|FT|PROC^Procedure^L||Kviðsjáraðgerð til botnlangatöku, framkvæmd 18.04.2024||||||F
OBX|3|FT|PLAN^Follow-up Plan^L||Endurkomuboð eftir 2 vikur. Saumur fjarlægður eftir 10 daga. Verkjalyf: Paracetamol 1g x3 eftir þörfum.||||||F
```

---

## 16. MDM^T02 - Specialist referral letter for portal

```
MSH|^~\&|SAGA|LANDSPITALI|HEILSUVERA|IS_NATIONAL_HEALTH|20240423091000||MDM^T02^MDM_T02|MSG00016|P|2.5|||AL|NE||IS
EVN|T02|20240423091000
PID|1||2204833016^^^ISLAND^KT||Þrastardóttir^Sigfríður^^^Frú||19830422|F|||Bjarkargata 12^^Selfoss^^800^IS||^PRN^PH^^^354^4823071||IS|M|||||2204833016
PV1|1|O|CARDIO^^^^LSH|||||||||||||||REF|||||||||||||||||||||||||20240423091000
TXA|1|REF^Referral Letter^L|TX|20240423090000|5678^Marteinsdóttir^Auðbjörg^^^Dr||20240423091000||||||DOC00016||AU||AV
OBX|1|FT|REFTEXT^Referral Content^L||Tilvísun til hjartalæknis. Sjúklingur með áreynslumæði síðustu 3 mánuði. Áreynslupróf sýnir ST-lægð. Bið um frekari greiningu og hjartaþræðingu ef ástæða þykir til.||||||F
```

---

## 17. ORU^R01 - Screening result for portal

```
MSH|^~\&|FLEXLAB|LANDSPITALI|HEILSUVERA|IS_NATIONAL_HEALTH|20240425143000||ORU^R01^ORU_R01|MSG00017|P|2.5|||AL|NE||IS
PID|1||1908763912^^^ISLAND^KT||Vésteinsdóttir^Aðalheiður^^^Frú||19760819|F|||Logafold 24^^Reykjavík^^112^IS||^PRN^PH^^^354^5871429||IS|M|||||1908763912
PV1|1|O|SCREEN^^^^LSH|||||||||||||||REF|||||||||||||||||||||||||20240425143000
ORC|RE|ORD00017|SCR00017||CM||||20240425143000
OBR|1|ORD00017|SCR00017|77067^Screening Mammography^CPT|||20240424100000|||||||20240424110000||6789^Snorradóttir^Yrsa^^^Dr|||||||20240425143000|||F
OBX|1|CE|77067^Mammography Result^CPT||BI-RADS1^Negative^L||||||F
OBX|2|FT|COMMENT^Clinical Comment^L||Eðlilegt útlit brjóstavefjar beggja vegna. Engin merki um æxlisvöxt. Næsta leitarrannsókn eftir 2 ár.||||||F
```

---

## 18. ORU^R01 - Portal document with base64 ED OBX (PDF care plan)

```
MSH|^~\&|SAGA|HEILSUGAESLA_HAMRABORG|HEILSUVERA|IS_NATIONAL_HEALTH|20240428110000||ORU^R01^ORU_R01|MSG00018|P|2.5|||AL|NE||IS
PID|1||0306923089^^^ISLAND^KT||Friðbjarnarson^Hávarður^^^Hr||19920603|M|||Norðurás 22^^Akureyri^^603^IS||^PRN^PH^^^354^4624715||IS|S|||||0306923089
PV1|1|O|HAMRABORG^^^^HGS|||||||||||||||REF|||||||||||||||||||||||||20240428110000
ORC|RE|ORD00018|DOC00018||CM||||20240428110000
OBR|1|ORD00018|DOC00018|CAREPLAN^Care Plan^L|||20240428100000|||||||20240428105000||9012^Sturludóttir^Vala^^^Dr|||||||20240428110000|||F
OBX|1|ED|PDF^Care Plan^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKE1lZGZlcmRhYWV0bHVuKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCg==||||||F
```

---

## 19. ADT^A01 - Admission notification to portal

```
MSH|^~\&|SAGA|LANDSPITALI|HEILSUVERA|IS_NATIONAL_HEALTH|20240501070000||ADT^A01^ADT_A01|MSG00019|P|2.5|||AL|NE||IS
EVN|A01|20240501070000|||ADM_NOTIFY
PID|1||0911952138^^^ISLAND^KT||Ægisson^Ölvir^^^Hr||19951109|M|||Trönuhjalli 7^^Kópavogur^^200^IS||^PRN^PH^^^354^5340972~^PRN^CP^^^354^7621384||IS|S|||||0911952138
PV1|1|I|ORTH1^^^^LSH|||||||4321^Þorgeirsson^Bárður^^^Dr||||||||INP|||||||||||||||||||||||||20240501070000
DG1|1||S72.0^Fractura colli femoris^ICD10||20240501|A
```

---

## 20. ORU^R01 - Chronic disease monitoring result

```
MSH|^~\&|FLEXLAB|HEILSUGAESLA_HAMRABORG|HEILSUVERA|IS_NATIONAL_HEALTH|20240503090000||ORU^R01^ORU_R01|MSG00020|P|2.5|||AL|NE||IS
PID|1||0306923089^^^ISLAND^KT||Friðbjarnarson^Hávarður^^^Hr||19920603|M|||Norðurás 22^^Akureyri^^603^IS||^PRN^PH^^^354^4624715||IS|S|||||0306923089
PV1|1|O|HAMRABORG^^^^HGS|||||||||||||||REF|||||||||||||||||||||||||20240503090000
ORC|RE|ORD00020|FLX00020||CM||||20240503090000
OBR|1|ORD00020|FLX00020|DM_MONITOR^Diabetes Monitoring^L|||20240502140000|||||||20240502150000||9012^Sturludóttir^Vala^^^Dr|||||||20240503090000|||F
OBX|1|NM|4548-4^HbA1c^LN||52|mmol/mol|<48|H|||F
OBX|2|NM|14749-6^Fasting Glucose^LN||7.2|mmol/L|3.9-5.5|H|||F
OBX|3|NM|2093-3^Total Cholesterol^LN||5.8|mmol/L|<5.0|H|||F
OBX|4|NM|2085-9^HDL Cholesterol^LN||1.1|mmol/L|>1.0|N|||F
OBX|5|NM|13457-7^LDL Cholesterol^LN||3.9|mmol/L|<3.0|H|||F
OBX|6|NM|14937-7^Triglycerides^LN||1.8|mmol/L|<1.7|H|||F
```
