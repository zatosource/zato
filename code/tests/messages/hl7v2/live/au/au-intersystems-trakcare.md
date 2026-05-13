# InterSystems TrakCare (Acacia) - real HL7v2 ER7 messages

---

## 1. ADT_A01 - Patient admission to Royal Adelaide Hospital

```
MSH|^~\&|TRAKCARE|RAH^Royal Adelaide Hospital|OACIS|SA_HEALTH|20250314091200||ADT^A01^ADT_A01|MSG00001|P|2.4|||AL|NE|AUS
EVN|A01|20250314091200|||JSMITH^Smith^Jane^^^Dr
PID|1||MRN4401928^^^RAH^MR~8901234567^^^AUSHIC^MC||O'BRIEN^Liam^Patrick^^Mr||19580312|M|||14 Hutt Street^^Adelaide^SA^5000^AUS||^PRN^PH^^^^^0882231456|^WPN^PH^^^^^0884567890|||M|||8901234567||||||||||||N
PV1|1|I|4WEST^412^1^RAH^^^N|E|||CON2345^McGregor^Angus^^^Dr^MBBS|CON2345^McGregor^Angus^^^Dr^MBBS||MED||||1|||CON2345^McGregor^Angus^^^Dr^MBBS|IN||SA_PUB||||||||||||||||||||RAH||A|||20250314091200
PV2|||^Chest pain, ?ACS|||||||2||||||||||||||||||||||||||||||N
NK1|1|O'BRIEN^Mary^Ellen||^PRN^PH^^^^^0882231456|^WPN^PH^^^^^0884567891||NOK
IN1|1|MCARE|MEDICARE_AUS|Medicare Australia||||||||19580312|||||O'BRIEN^Liam^Patrick^^Mr|SELF|19580312||||||||||||||||||8901234567
```

---

## 2. ADT_A02 - Patient transfer within Flinders Medical Centre

```
MSH|^~\&|ACACIA|FMC^Flinders Medical Centre|OACIS|SA_HEALTH|20250314143000||ADT^A02^ADT_A02|MSG00002|P|2.4|||AL|NE|AUS
EVN|A02|20250314143000|||RBROWN^Brown^Robert^^^Nurse
PID|1||MRN5502847^^^FMC^MR~2345678901^^^AUSHIC^MC||NGUYEN^Thi^Mai^^Mrs||19720815|F|||27 Brighton Road^^Glenelg^SA^5045^AUS||^PRN^PH^^^^^0883761234||||M|||2345678901
PV1|1|I|ICU^ICU03^1^FMC^^^N|U|||CON3456^Patel^Rajesh^^^Dr^MBBS|CON3456^Patel^Rajesh^^^Dr^MBBS||ICU||||1|||CON3456^Patel^Rajesh^^^Dr^MBBS|IN||SA_PUB||||||||||||||||||||FMC||T|||20250312080000
PV2|||^Post-operative monitoring
```

---

## 3. ADT_A03 - Patient discharge from The Canberra Hospital

```
MSH|^~\&|TRAKCARE|TCH^The Canberra Hospital|ACTPAS|ACT_HEALTH|20250315101500||ADT^A03^ADT_A03|MSG00003|P|2.4|||AL|NE|AUS
EVN|A03|20250315101500|||KLEE^Lee^Karen^^^RN
PID|1||MRN6603192^^^TCH^MR~3456789012^^^AUSHIC^MC||WILLIAMS^Sarah^Jane^^Ms||19850621|F|||8 Lonsdale Street^^Braddon^ACT^2612^AUS||^PRN^PH^^^^^0262491234||||S|||3456789012
PV1|1|I|5SOUTH^503^1^TCH^^^N|E|||CON4567^Hassan^Fatima^^^Dr^MBBS|CON4567^Hassan^Fatima^^^Dr^MBBS||GEN||||1|||CON4567^Hassan^Fatima^^^Dr^MBBS|IN||ACT_PUB||||||||||||||||||||TCH||A|||20250312143000|||20250315101500
DG1|1||J18.9^Pneumonia, unspecified^I10|||F
```

---

## 4. ADT_A04 - Outpatient registration at Lyell McEwin Hospital

```
MSH|^~\&|ACACIA|LMH^Lyell McEwin Hospital|OACIS|SA_HEALTH|20250316083000||ADT^A04^ADT_A04|MSG00004|P|2.4|||AL|NE|AUS
EVN|A04|20250316083000|||AWHITE^White^Amanda^^^Admin
PID|1||MRN7714003^^^LMH^MR~4567890123^^^AUSHIC^MC||KUMAR^Arun^Raj^^Mr||19900405|M|||3 Peachey Road^^Davoren Park^SA^5113^AUS||^PRN^PH^^^^^0882551234||||S|||4567890123
PV1|1|O|OPD^CLINIC4^1^LMH^^^N|R|||CON5678^Dixon^Michael^^^Dr^MBBS|||||OPD||||1|||CON5678^Dixon^Michael^^^Dr^MBBS|OUT||SA_PUB||||||||||||||||||||LMH||A|||20250316083000
PV2|||^Diabetes follow-up review
```

---

## 5. ADT_A08 - Patient information update at Women's and Children's Hospital

```
MSH|^~\&|TRAKCARE|WCH^Women's and Children's Hospital|OACIS|SA_HEALTH|20250317110000||ADT^A08^ADT_A08|MSG00005|P|2.4|||AL|NE|AUS
EVN|A08|20250317110000|||MCLARK^Clark^Michelle^^^Admin
PID|1||MRN8825614^^^WCH^MR~5678901234^^^AUSHIC^MC||JOHNSON^Emily^Rose^^Miss||20180923|F|||42 King William Road^^Unley^SA^5061^AUS||^PRN^PH^^^^^0883721234||||S|||5678901234||||||||||||N
PD1||||CON6789^Thompson^Laura^^^Dr^MBBS
NK1|1|JOHNSON^David^James||^PRN^PH^^^^^0883721234|||NOK
NK1|2|JOHNSON^Rebecca^Anne||^PRN^PH^^^^^0412345678|||EMC
```

---

## 6. ADT_A28 - Add person information at Calvary Public Hospital Bruce

```
MSH|^~\&|TRAKCARE|CPHB^Calvary Public Hospital Bruce|ACTPAS|ACT_HEALTH|20250318090000||ADT^A28^ADT_A28|MSG00006|P|2.5|||AL|NE|AUS
EVN|A28|20250318090000|||SMORRIS^Morris^Susan^^^Admin
PID|1||MRN9936025^^^CPHB^MR~6789012345^^^AUSHIC^MC||TAYLOR^James^Robert^^Mr||19670214|M|||15 Aspinall Street^^Watson^ACT^2602^AUS||^PRN^PH^^^^^0262411234||||M|||6789012345||||||||||||N
NK1|1|TAYLOR^Wendy^Louise||^PRN^PH^^^^^0412987654|||NOK
```

---

## 7. ADT_A40 - Patient merge at Royal Adelaide Hospital

```
MSH|^~\&|ACACIA|RAH^Royal Adelaide Hospital|OACIS|SA_HEALTH|20250319140000||ADT^A40^ADT_A40|MSG00007|P|2.4|||AL|NE|AUS
EVN|A40|20250319140000|||PJONES^Jones^Peter^^^Admin
PID|1||MRN1047236^^^RAH^MR~7890123456^^^AUSHIC^MC||SMITH^Geoffrey^Allan^^Mr||19450728|M|||9 Prospect Road^^Prospect^SA^5082^AUS||^PRN^PH^^^^^0882691234||||W|||7890123456
MRG|MRN1047237^^^RAH^MR|
```

---

## 8. ORM_O01 - Pathology order from Flinders Medical Centre

```
MSH|^~\&|TRAKCARE|FMC^Flinders Medical Centre|SAPATHOLOGY|SA_PATH|20250320083000||ORM^O01^ORM_O01|MSG00008|P|2.4|||AL|NE|AUS
PID|1||MRN2158347^^^FMC^MR~8901234568^^^AUSHIC^MC||CHEN^Wei^Lin^^Mr||19810917|M|||31 Diagonal Road^^Oaklands Park^SA^5046^AUS||^PRN^PH^^^^^0883741234||||M|||8901234568
PV1|1|I|3EAST^305^1^FMC^^^N|E|||CON7890^Singh^Priya^^^Dr^MBBS|||||MED||||1|||CON7890^Singh^Priya^^^Dr^MBBS|IN||SA_PUB||||||||||||||||||||FMC||A|||20250319200000
ORC|NW|ORD20250320-001^TRAKCARE|||||^^^20250320083000^^R||20250320083000|JNURSE^Reid^Janet^^^RN||CON7890^Singh^Priya^^^Dr^MBBS|FMC
OBR|1|ORD20250320-001^TRAKCARE||FBE^Full Blood Examination^SAPATH|||20250320083000||||||||20250320082500|Blood^Venous^EDTA|CON7890^Singh^Priya^^^Dr^MBBS||||||20250320083000|||F
OBR|2|ORD20250320-001^TRAKCARE||UEC^Urea Electrolytes Creatinine^SAPATH|||20250320083000||||||||20250320082500|Blood^Venous^SST|CON7890^Singh^Priya^^^Dr^MBBS||||||20250320083000|||F
OBR|3|ORD20250320-001^TRAKCARE||CRP^C-Reactive Protein^SAPATH|||20250320083000||||||||20250320082500|Blood^Venous^SST|CON7890^Singh^Priya^^^Dr^MBBS||||||20250320083000|||F
```

---

## 9. ORM_O01 - Radiology order from The Canberra Hospital

```
MSH|^~\&|ACACIA|TCH^The Canberra Hospital|ACTRAD|ACT_RAD|20250320100000||ORM^O01^ORM_O01|MSG00009|P|2.4|||AL|NE|AUS
PID|1||MRN3269458^^^TCH^MR~9012345679^^^AUSHIC^MC||BAKER^Thomas^William^^Mr||19550803|M|||22 Limestone Avenue^^Ainslie^ACT^2602^AUS||^PRN^PH^^^^^0262481234||||M|||9012345679
PV1|1|E|ED^ED05^1^TCH^^^N|E|||CON8901^Wu^David^^^Dr^MBBS|||||ED||||1|||CON8901^Wu^David^^^Dr^MBBS|EM||ACT_PUB||||||||||||||||||||TCH||A|||20250320093000
ORC|NW|ORD20250320-002^ACACIA|||||^^^20250320100000^^S||20250320100000|TNURSE^Allan^Theresa^^^RN||CON8901^Wu^David^^^Dr^MBBS|TCH
OBR|1|ORD20250320-002^ACACIA||CXRAY^Chest X-Ray PA and Lateral^ACTRAD|||20250320100000||||||||20250320095500||CON8901^Wu^David^^^Dr^MBBS|||||||20250320100000|||F|||^SOB and pleuritic chest pain
```

---

## 10. ORU_R01 - Pathology result from SA Pathology to TrakCare

```
MSH|^~\&|SAPATHOLOGY|SAPATH|TRAKCARE|RAH^Royal Adelaide Hospital|20250320141500||ORU^R01^ORU_R01|MSG00010|P|2.4|||AL|NE|AUS
PID|1||MRN4502184^^^RAH^MR~8902345671^^^AUSHIC^MC||VASILEIOU^Dimitri^Konstantinos^^Mr||19620718|M|||58 North Terrace^^Adelaide^SA^5000^AUS||^PRN^PH^^^^^0882234578||||M|||8902345671
PV1|1|I|6EAST^608^2^RAH^^^N||||CON3120^Andersen^Helena^^^Dr^MBBS|||||MED||||||||IN||SA_PUB||||||||||||||||||||RAH||A|||20250314091200
ORC|RE|ORD20250314-198^TRAKCARE|RES20250320-014^SAPATH||||^^^20250314120000^^R||20250320141500|||CON3120^Andersen^Helena^^^Dr^MBBS
OBR|1|ORD20250314-198^TRAKCARE|RES20250320-014^SAPATH|FBE^Full Blood Examination^SAPATH|||20250314120000||||||||20250314115500|Blood^Venous^EDTA|CON3120^Andersen^Helena^^^Dr^MBBS||||||20250320141500|||F
OBX|1|NM|WBC^White Blood Cell Count^SAPATH||11.2|x10\S\9/L|4.0-11.0|H|||F|||20250320140000
OBX|2|NM|RBC^Red Blood Cell Count^SAPATH||4.85|x10\S\12/L|4.50-6.50||||F|||20250320140000
OBX|3|NM|HGB^Haemoglobin^SAPATH||148|g/L|130-180||||F|||20250320140000
OBX|4|NM|HCT^Haematocrit^SAPATH||0.44|L/L|0.40-0.54||||F|||20250320140000
OBX|5|NM|PLT^Platelet Count^SAPATH||245|x10\S\9/L|150-400||||F|||20250320140000
```

---

## 11. ORU_R01 - Biochemistry result with abnormal flags

```
MSH|^~\&|SAPATHOLOGY|SAPATH|ACACIA|FMC^Flinders Medical Centre|20250321091000||ORU^R01^ORU_R01|MSG00011|P|2.4|||AL|NE|AUS
PID|1||MRN2261507^^^FMC^MR~8901456720^^^AUSHIC^MC||TARAKI^Mahmoud^Hassan^^Mr||19590304|M|||7 Halsey Road^^Elizabeth^SA^5112^AUS||^PRN^PH^^^^^0883771409||||M|||8901456720
PV1|1|I|2NORTH^214^1^FMC^^^N||||CON7115^Webster^Charlotte^^^Dr^MBBS|||||REN||||||||IN||SA_PUB||||||||||||||||||||FMC||A|||20250319200000
ORC|RE|ORD20250320-088^TRAKCARE|RES20250321-022^SAPATH||||^^^20250320083000^^R||20250321091000|||CON7115^Webster^Charlotte^^^Dr^MBBS
OBR|1|ORD20250320-088^TRAKCARE|RES20250321-022^SAPATH|UEC^Urea Electrolytes Creatinine^SAPATH|||20250320083000||||||||20250320082500|Blood^Venous^SST|CON7115^Webster^Charlotte^^^Dr^MBBS||||||20250321091000|||F
OBX|1|NM|NA^Sodium^SAPATH||128|mmol/L|135-145|L|||F|||20250321085000
OBX|2|NM|K^Potassium^SAPATH||5.8|mmol/L|3.5-5.2|H|||F|||20250321085000
OBX|3|NM|CL^Chloride^SAPATH||96|mmol/L|95-110||||F|||20250321085000
OBX|4|NM|HCO3^Bicarbonate^SAPATH||18|mmol/L|22-32|L|||F|||20250321085000
OBX|5|NM|UREA^Urea^SAPATH||14.2|mmol/L|2.5-8.0|H|||F|||20250321085000
OBX|6|NM|CREAT^Creatinine^SAPATH||185|umol/L|60-110|H|||F|||20250321085000
OBX|7|NM|EGFR^eGFR^SAPATH||34|mL/min/1.73m2|>90|L|||F|||20250321085000
```

---

## 12. ORU_R01 - Radiology report from ACT Health imaging

```
MSH|^~\&|ACTRAD|ACT_RAD|TRAKCARE|TCH^The Canberra Hospital|20250320153000||ORU^R01^ORU_R01|MSG00012|P|2.4|||AL|NE|AUS
PID|1||MRN3370116^^^TCH^MR~9012678045^^^AUSHIC^MC||MAKERETI^Hineamaru^Kahurangi^^Mrs||19770211|F|||3 Northbourne Avenue^^Civic^ACT^2608^AUS||^PRN^PH^^^^^0262489876||||M|||9012678045
PV1|1|E|ED^ED11^1^TCH^^^N||||CON8245^Hartley^Ruth^^^Dr^MBBS|||||ED||||||||EM||ACT_PUB||||||||||||||||||||TCH||A|||20250320093000
ORC|RE|ORD20250320-104^ACACIA|RES20250320-105^ACTRAD||||^^^20250320100000^^S||20250320153000|||CON8245^Hartley^Ruth^^^Dr^MBBS
OBR|1|ORD20250320-104^ACACIA|RES20250320-105^ACTRAD|CXRAY^Chest X-Ray PA and Lateral^ACTRAD|||20250320100000||||||||20250320103000||CON8245^Hartley^Ruth^^^Dr^MBBS|||RAD9415^Bui^Henry^^^Dr^FRANZCR|20250320153000|||F
OBX|1|FT|CXRAY^Chest X-Ray Report^ACTRAD||CHEST X-RAY PA AND LATERAL\.br\\.br\Clinical Indication: SOB and pleuritic chest pain\.br\\.br\Comparison: Nil prior\.br\\.br\Findings:\.br\Heart size is normal. The mediastinal contour is unremarkable.\.br\There is a small left-sided pleural effusion with associated basal atelectasis.\.br\The right lung is clear. No pneumothorax.\.br\\.br\Impression:\.br\Small left pleural effusion. Clinical correlation recommended.||||||F|||20250320152000
```

---

## 13. ORU_R01 - Pathology result with embedded PDF report

```
MSH|^~\&|SAPATHOLOGY|SAPATH|TRAKCARE|LMH^Lyell McEwin Hospital|20250322110000||ORU^R01^ORU_R01|MSG00013|P|2.5|||AL|NE|AUS
PID|1||MRN7821649^^^LMH^MR~4568123097^^^AUSHIC^MC||MERCURIO^Lorenzo^Antonio^^Mr||19641128|M|||94 John Rice Avenue^^Elizabeth Vale^SA^5112^AUS||^PRN^PH^^^^^0882828105||||M|||4568123097
PV1|1|O|OPD^CLINIC9^1^LMH^^^N||||CON5012^Karageorgis^Stavros^^^Dr^MBBS|||||OPD||||||||OUT||SA_PUB||||||||||||||||||||LMH||A|||20250316083000
ORC|RE|ORD20250316-067^ACACIA|RES20250322-031^SAPATH||||^^^20250316090000^^R||20250322110000|||CON5012^Karageorgis^Stavros^^^Dr^MBBS
OBR|1|ORD20250316-067^ACACIA|RES20250322-031^SAPATH|HBA1C^Glycated Haemoglobin^SAPATH|||20250316090000||||||||20250316085500|Blood^Venous^EDTA|CON5012^Karageorgis^Stavros^^^Dr^MBBS||||||20250322110000|||F
OBX|1|NM|HBA1C^HbA1c^SAPATH||8.2|%|<7.0|H|||F|||20250322100000
OBX|2|NM|EDAG^Estimated Average Glucose^SAPATH||10.2|mmol/L|||||F|||20250322100000
OBX|3|ED|PDF^Clinical Document^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo=||||||F
```

---

## 14. SIU_S12 - Outpatient appointment booking at Royal Adelaide Hospital

```
MSH|^~\&|TRAKCARE|RAH^Royal Adelaide Hospital|OACIS|SA_HEALTH|20250323090000||SIU^S12^SIU_S12|MSG00014|P|2.5|||AL|NE|AUS
SCH|APT20250410-001|APT20250410-001|||||ROUTINE^Routine Appointment^HL70276|FOLLOWUP^Follow-up^HL70277|30|min|^^30^20250410090000^20250410093000||CON3402^Yusuf^Adila^^^Dr^MBBS|^PRN^PH^^^^^0882227891|6EAST_CLINIC^Endocrinology Outpatients^RAH|CON3402^Yusuf^Adila^^^Dr^MBBS||BOOKED
PID|1||MRN4615370^^^RAH^MR~8903127845^^^AUSHIC^MC||CALLAGHAN^Bridget^Imogen^^Mrs||19710602|F|||21 Halifax Street^^Adelaide^SA^5000^AUS||^PRN^PH^^^^^0882236704||||M|||8903127845
PV1|1|O|6EAST_CLINIC^^1^RAH^^^N|R|||CON3402^Yusuf^Adila^^^Dr^MBBS|||||ENDO||||||||OUT||SA_PUB||||||||||||||||||||RAH
RGS|1|A|ENDOCRINOLOGY^Endocrinology^HL70572
AIS|1|A|ENDOCONS^Endocrinology Consultation^RAH_SVC|20250410090000|||30|min
AIP|1|A|CON3402^Yusuf^Adila^^^Dr^MBBS|
```

---

## 15. SIU_S15 - Appointment cancellation at The Canberra Hospital

```
MSH|^~\&|ACACIA|TCH^The Canberra Hospital|ACTPAS|ACT_HEALTH|20250324110000||SIU^S15^SIU_S15|MSG00015|P|2.5|||AL|NE|AUS
SCH|APT20250401-017|APT20250401-017|||||ROUTINE^Routine Appointment^HL70276|FOLLOWUP^Follow-up^HL70277|20|min|^^20^20250401140000^20250401142000||CON4218^Mehrotra^Vikram^^^Dr^MBBS|^PRN^PH^^^^^0262494582|2NORTH_CLINIC^Gastroenterology Outpatients^TCH|CON4218^Mehrotra^Vikram^^^Dr^MBBS||CANCELLED
PID|1||MRN6708425^^^TCH^MR~3457120893^^^AUSHIC^MC||DELACROIX^Solenne^Margaux^^Ms||19940915|F|||16 Currie Crescent^^Kingston^ACT^2604^AUS||^PRN^PH^^^^^0262959087||||S|||3457120893
PV1|1|O|2NORTH_CLINIC^^1^TCH^^^N||||CON4218^Mehrotra^Vikram^^^Dr^MBBS|||||GAST||||||||OUT||ACT_PUB||||||||||||||||||||TCH
```

---

## 16. MDM_T02 - Clinical document notification with embedded PDF from TrakCare

```
MSH|^~\&|TCA|WCH^Women's and Children's Hospital|OACIS|SA_HEALTH|20250325140000||MDM^T02^MDM_T02|MSG00016|P|2.5|||AL|NE|AUS
EVN|T02|20250325140000
PID|1||MRN8930745^^^WCH^MR~5679234608^^^AUSHIC^MC||OKONKWO^Chinaza^Ifeoma^^Miss||20160714|F|||10 Devereux Road^^Beulah Park^SA^5067^AUS||^PRN^PH^^^^^0883310465||||S|||5679234608
PV1|1|O|PAED_OPD^^1^WCH^^^N|R|||CON6210^Marchetti^Sergio^^^Dr^MBBS|||||PAED||||||||OUT||SA_PUB||||||||||||||||||||WCH||A|||20250325130000
TXA|1|DS^Discharge Summary^HL70270|TX|20250325140000|CON6210^Marchetti^Sergio^^^Dr^MBBS||20250325140000||CON6210^Marchetti^Sergio^^^Dr^MBBS||||DOC20250325-001|||AU||AV
OBX|1|ED|PDF^Clinical Document^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo=||||||F
```

---

## 17. ADT_A13 - Cancel discharge at Flinders Medical Centre

```
MSH|^~\&|TRAKCARE|FMC^Flinders Medical Centre|OACIS|SA_HEALTH|20250326160000||ADT^A13^ADT_A13|MSG00017|P|2.4|||AL|NE|AUS
EVN|A13|20250326160000|||CON3456^Patel^Rajesh^^^Dr^MBBS
PID|1||MRN5618934^^^FMC^MR~2346019785^^^AUSHIC^MC||LAZARIDIS^Yannis^Theofanis^^Mr||19481119|M|||5 Kestrel Avenue^^Hallett Cove^SA^5158^AUS||^PRN^PH^^^^^0883815217||||W|||2346019785
PV1|1|I|4WEST^410^1^FMC^^^N|E|||CON3719^Yamamoto^Akiko^^^Dr^MBBS|CON3719^Yamamoto^Akiko^^^Dr^MBBS||GEN||||1|||CON3719^Yamamoto^Akiko^^^Dr^MBBS|IN||SA_PUB||||||||||||||||||||FMC||A|||20250320090000
```

---

## 18. ORM_O01 - Pharmacy order from Royal Adelaide Hospital

```
MSH|^~\&|TRAK_HIS|RAH^Royal Adelaide Hospital|SAPHARMA|SA_PHARMA|20250327083000||ORM^O01^ORM_O01|MSG00018|P|2.4|||AL|NE|AUS
PID|1||MRN4823051^^^RAH^MR~8904718206^^^AUSHIC^MC||PRENDERGAST^Lachlan^Heath^^Mr||19880506|M|||7 Sturt Street^^Adelaide^SA^5000^AUS||^PRN^PH^^^^^0882264913||||S|||8904718206
PV1|1|I|7WEST^709^2^RAH^^^N||||CON2854^Driscoll^Padraig^^^Dr^MBBS|||||CARD||||||||IN||SA_PUB||||||||||||||||||||RAH||A|||20250314091200
ORC|NW|ORD20250327-201^TRAK_HIS|||||^^^20250327083000^^R||20250327083000|RNURSE^Cole^Imogen^^^RN||CON2854^Driscoll^Padraig^^^Dr^MBBS|RAH
OBR|1|ORD20250327-201^TRAK_HIS||RXORD^Pharmacy Order^RAH_PHARMA|||20250327083000||||||||20250327082000||CON2854^Driscoll^Padraig^^^Dr^MBBS||||||20250327083000|||F
RXO|METOP^Metoprolol Tartrate^PBS|25|mg||PO^Oral^HL70162||V||0|TAB^Tablet^HL70235|||||||1|25|mg
RXR|PO^Oral^HL70162
```

---

## 19. ADT_A11 - Cancel admission at Calvary Public Hospital Bruce

```
MSH|^~\&|TRAKCARE|CPHB^Calvary Public Hospital Bruce|ACTPAS|ACT_HEALTH|20250328091500||ADT^A11^ADT_A11|MSG00019|P|2.4|||AL|NE|AUS
EVN|A11|20250328091500|||SMORRIS^Morris^Susan^^^Admin
PID|1||MRN1004217^^^CPHB^MR~6790148532^^^AUSHIC^MC||PEREIRA^Cristiano^Joaquim^^Mr||19590927|M|||31 Hillside Road^^Hawker^ACT^2614^AUS||^PRN^PH^^^^^0262784110||||M|||6790148532
PV1|1|I|3NORTH^307^1^CPHB^^^N|E|||CON1681^Sanders^Geraldine^^^Dr^MBBS|CON1681^Sanders^Geraldine^^^Dr^MBBS||GEN||||1|||CON1681^Sanders^Geraldine^^^Dr^MBBS|IN||ACT_PUB||||||||||||||||||||CPHB||A|||20250327200000
```

---

## 20. MDM_T02 - Discharge summary notification from The Canberra Hospital

```
MSH|^~\&|TRAKCARE|TCH^The Canberra Hospital|ACTPAS|ACT_HEALTH|20250329100000||MDM^T02^MDM_T02|MSG00020|P|2.5|||AL|NE|AUS
EVN|T02|20250329100000
PID|1||MRN3415802^^^TCH^MR~9013561284^^^AUSHIC^MC||CAVANOUGH^Reuben^Xavier^^Mr||19490428|M|||4 Eyre Crescent^^Lyneham^ACT^2602^AUS||^PRN^PH^^^^^0262575039||||W|||9013561284
PV1|1|I|5SOUTH^509^1^TCH^^^N|E|||CON8330^Pavlovic^Mira^^^Dr^MBBS|||||GEN||||||||IN||ACT_PUB||||||||||||||||||||TCH||A|||20250320093000|||20250329090000
TXA|1|DS^Discharge Summary^HL70270|TX|20250329100000|CON8330^Pavlovic^Mira^^^Dr^MBBS||20250329100000||CON8330^Pavlovic^Mira^^^Dr^MBBS||||DOC20250329-001|||AU||AV
OBX|1|FT|DS^Discharge Summary^LN||DISCHARGE SUMMARY\.br\\.br\Patient: CAVANOUGH, Reuben Xavier\.br\MRN: MRN3415802\.br\DOB: 28/04/1949\.br\\.br\Admission Date: 20/03/2025\.br\Discharge Date: 29/03/2025\.br\\.br\Admitting Diagnosis: Shortness of breath, pleuritic chest pain\.br\\.br\Investigations:\.br\- Chest X-Ray: Small left pleural effusion\.br\- CT Pulmonary Angiogram: No pulmonary embolism\.br\- Pleural fluid analysis: Transudative\.br\\.br\Management:\.br\- Diuretic therapy with intravenous frusemide\.br\- Echocardiogram showed preserved LV function, mild diastolic dysfunction\.br\- Transitioned to oral frusemide 40mg daily\.br\\.br\Discharge Medications:\.br\1. Frusemide 40mg PO daily\.br\2. Perindopril 5mg PO daily\.br\3. Atorvastatin 40mg PO nocte\.br\\.br\Follow-up:\.br\- Cardiology outpatients in 4 weeks\.br\- Repeat chest X-ray in 2 weeks\.br\\.br\Prepared by: Dr Mira Pavlovic, MBBS FRACP||||||F
```
