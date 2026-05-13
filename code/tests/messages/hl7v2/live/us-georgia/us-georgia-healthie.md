# HealtHIE Georgia (SunLink Health) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission at Dorminy Medical Center, Fitzgerald

```
MSH|^~\&|HEALTHIE_GA|DORMINY_MC|GA_HIE|HEALTHIE|20260401071500||ADT^A01^ADT_A01|MSG20001|P|2.5.1|||AL|NE
EVN|A01|20260401071000|||JBAKER^Calhoun^Janet^L^^RN
PID|1||DM1001234^^^DORMINY_MRN^MR||Gantt^Larry^Wayne^^Mr||19580412|M|||200 Perry House Rd^^Fitzgerald^GA^31750^US||^PRN^PH^^1^229^5551001||||M||DM1001234001|172-84-3609
PV1|1|I|2MED^201^A^DORMINY_MC^^^^NURS|E|||30001^Whitworth^Roger^H^^^MD|30002^Oglesby^Susan^T^^^MD||MED||||A|||30001^Whitworth^Roger^H^^^MD|IN||MEDICAID|||||||||||||||||||DORMINY_MC|||||20260401071000
PV2|||^Community-acquired pneumonia^J18.9
NK1|1|Gantt^Betty^Faye|SPO^Spouse|200 Perry House Rd^^Fitzgerald^GA^31750^US|^PRN^PH^^1^229^5551002
DG1|1||J18.9^Pneumonia, unspecified organism^ICD10||20260401|A
```

---

## 2. ADT^A03 - Patient discharge from Irwin County Hospital

```
MSH|^~\&|SUNLINK|IRWIN_HOSP|GA_HIE|HEALTHIE|20260402153000||ADT^A03^ADT_A03|MSG20002|P|2.5.1|||AL|NE
EVN|A03|20260402152500|||DMOORE^Steadman^Debra^K^^RN
PID|1||IR2002345^^^IRWIN_MRN^MR||Chesnut^Gladys^Irene^^Mrs||19460823|F|||310 Irwin Ave^^Ocilla^GA^31774^US||^PRN^PH^^1^229^5552001||||W||IR2002345001|284-51-9736
PV1|1|I|1MED^105^A^IRWIN_HOSP^^^^NURS|E|||31001^Cantrell^William^F^^^MD|||MED||||D|||31001^Cantrell^William^F^^^MD|IN||MEDICARE|||||||||||||||||||IRWIN_HOSP|||||20260330100000|20260402152500
DG1|1||N39.0^Urinary tract infection, site not specified^ICD10||20260330|A
```

---

## 3. ADT^A04 - Outpatient registration at East Georgia Regional Medical Center

```
MSH|^~\&|HEALTHIE_GA|EGRMC|GA_HIE|HEALTHIE|20260403082000||ADT^A04^ADT_A04|MSG20003|P|2.5.1|||AL|NE
EVN|A04|20260403081500|||SYSTEM
PID|1||EG3003456^^^EGRMC_MRN^MR||Blackburn^Cynthia^Dawn^^Ms||19850917|F|||1499 Fair Rd^^Statesboro^GA^30458^US||^PRN^PH^^1^912^5553001||||S||EG3003456001|397-62-0148
PV1|1|O|FP^EXAM2^^EGRMC^^^^OUTPT|R|||32001^Ridgeway^Angela^M^^^MD|||FP||||N|||32001^Ridgeway^Angela^M^^^MD|OP||PEACHSTATE|||||||||||||||||||EGRMC|||||20260403082000
```

---

## 4. ORU^R01 - Lab results from South Georgia Medical Center, Valdosta

```
MSH|^~\&|SUNLINK|SGMC|GA_HIE|HEALTHIE|20260404141000||ORU^R01^ORU_R01|MSG20004|P|2.5.1|||AL|NE
PID|1||SG4004567^^^SGMC_MRN^MR||Crenshaw^Reginald^Earl^^Mr||19770306|M|||2501 N Patterson St^^Valdosta^GA^31602^US||^PRN^PH^^1^229^5554001||||M||SG4004567001|510-28-7463
PV1|1|O|LABDRW^DRAW1^^SGMC^^^^OUTPT|R|||33001^Beckett^Robert^D^^^MD|||LAB||||N|||33001^Beckett^Robert^D^^^MD|OP||BCBS
ORC|RE|ORD8374621^SGMC|LAB394827^SGMC_LAB|||CM||||||33001^Beckett^Robert^D^^^MD
OBR|1|ORD8374621^SGMC|LAB394827^SGMC_LAB|80048^Basic Metabolic Panel^CPT|||20260404120000|||||||20260404121500||33001^Beckett^Robert^D^^^MD||||||20260404140500||LAB|F
OBX|1|NM|2345-7^Glucose^LN||205|mg/dL|70-100|H|||F|||20260404140500
OBX|2|NM|3094-0^BUN^LN||32|mg/dL|7-20|H|||F|||20260404140500
OBX|3|NM|2160-0^Creatinine^LN||1.8|mg/dL|0.7-1.3|H|||F|||20260404140500
OBX|4|NM|2951-2^Sodium^LN||136|mmol/L|136-145|N|||F|||20260404140500
OBX|5|NM|2823-3^Potassium^LN||5.3|mmol/L|3.5-5.1|H|||F|||20260404140500
OBX|6|NM|17861-6^Calcium^LN||9.1|mg/dL|8.5-10.5|N|||F|||20260404140500
```

---

## 5. ORU^R01 - HbA1c result from Crisp Regional Hospital

```
MSH|^~\&|HEALTHIE_GA|CRISP_REG|GA_HIE|HEALTHIE|20260405100000||ORU^R01^ORU_R01|MSG20005|P|2.5.1|||AL|NE
PID|1||CR5005678^^^CRISP_MRN^MR||Ogletree^Brenda^Joyce^^Mrs||19620111|F|||502 7th St S^^Cordele^GA^31015^US||^PRN^PH^^1^229^5555001||||M||CR5005678001|693-04-1578
PV1|1|O|DIABCL^EXAM1^^CRISP_REG^^^^OUTPT|R|||34001^Littlefield^James^E^^^MD|||IM||||N|||34001^Littlefield^James^E^^^MD|OP||MEDICAID
ORC|RE|ORD7362948^CRISP|LAB483726^CRISP_LAB|||CM||||||34001^Littlefield^James^E^^^MD
OBR|1|ORD7362948^CRISP|LAB483726^CRISP_LAB|4548-4^Hemoglobin A1c^LN|||20260405083000|||||||20260405084500||34001^Littlefield^James^E^^^MD||||||20260405095500||LAB|F
OBX|1|NM|4548-4^Hemoglobin A1c^LN||8.9|%|4.0-5.6|H|||F|||20260405095500
OBX|2|NM|2345-7^Glucose^LN||187|mg/dL|70-100|H|||F|||20260405095500
```

---

## 6. VXU^V04 - Immunization update from Macon-Bibb County Health Department

```
MSH|^~\&|SUNLINK|MACON_HD|GA_HIE|HEALTHIE|20260406090000||VXU^V04^VXU_V04|MSG20006|P|2.5.1|||AL|NE
PID|1||MH6006789^^^MACON_HD_MRN^MR||Calderon^Sofia^Carmen||20220315|F|||171 Emery Hwy^^Macon^GA^31217^US||^PRN^PH^^1^478^5556001||||S
NK1|1|Calderon^Ana^Beatriz|MTH^Mother|171 Emery Hwy^^Macon^GA^31217^US|^PRN^PH^^1^478^5556002
RXA|0|1|20260406085000|20260406085500|141^Influenza, seasonal, injectable^CVX|0.5|mL||00^New immunization record^NIP001||||||Z3456AA||SKB^GlaxoSmithKline^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|LD^Left Deltoid^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC30^State funds^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine type^LN||141^Influenza, seasonal, injectable^CVX||||||F
```

---

## 7. VXU^V04 - Childhood immunization from Chatham County Health Department

```
MSH|^~\&|HEALTHIE_GA|CHATHAM_HD|GA_HIE|HEALTHIE|20260407101500||VXU^V04^VXU_V04|MSG20007|P|2.5.1|||AL|NE
PID|1||CH7007890^^^CHATHAM_HD_MRN^MR||Rutledge^Jayden^Michael||20240618|M|||412 Montgomery St^^Savannah^GA^31401^US||^PRN^PH^^1^912^5557001||||S
NK1|1|Rutledge^Tasha^Nicole|MTH^Mother|412 Montgomery St^^Savannah^GA^31401^US|^PRN^PH^^1^912^5557002
RXA|0|1|20260407100000|20260407100500|110^DTaP-Hep B-IPV^CVX|0.5|mL||00^New immunization record^NIP001||||||U5678BB||SKB^GlaxoSmithKline^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC1^Private funds^CDCPHINVS||||||F
RXA|0|2|20260407100500|20260407101000|133^PCV13^CVX|0.5|mL||00^New immunization record^NIP001||||||V9012CC||PFR^Pfizer^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|LT^Left Thigh^HL70163
OBX|2|CE|64994-7^Vaccine funding source^LN||VXC1^Private funds^CDCPHINVS||||||F
```

---

## 8. ACK - Acknowledgment for ADT message from HealtHIE

```
MSH|^~\&|GA_HIE|HEALTHIE|SUNLINK|IRWIN_HOSP|20260402153100||ACK^A03^ACK|MSG20008|P|2.5.1|||AL|NE
MSA|AA|MSG20002|Message accepted successfully
```

---

## 9. ACK - Negative acknowledgment for malformed message

```
MSH|^~\&|GA_HIE|HEALTHIE|HEALTHIE_GA|DORMINY_MC|20260408091200||ACK^A01^ACK|MSG20009|P|2.5.1|||AL|NE
MSA|AE|MSG20041|Required field PID-3 (Patient Identifier) is missing
ERR||PID^1^3|101^Required field missing^HL70357|E|||||Missing patient identifier in PID segment
```

---

## 10. ORU^R01 - CCD document exchange with embedded base64 from SGMC

```
MSH|^~\&|SUNLINK|SGMC|GA_HIE|HEALTHIE|20260409153000||ORU^R01^ORU_R01|MSG20010|P|2.5.1|||AL|NE
PID|1||SG4010234^^^SGMC_MRN^MR||Wimberly^Harold^Lamont^^Mr||19690804|M|||1105 N St Augustine Rd^^Valdosta^GA^31602^US||^PRN^PH^^1^229^5550101||||M||SG4010234001|146-73-8205
PV1|1|I|3MED^302^A^SGMC^^^^NURS|E|||35001^Oglesby^Michael^P^^^MD|||MED||||D|||35001^Oglesby^Michael^P^^^MD|IN||MEDICARE
ORC|RE|ORD6483729^SGMC|DOC938472^SGMC_HIE|||CM||||||35001^Oglesby^Michael^P^^^MD
OBR|1|ORD6483729^SGMC|DOC938472^SGMC_HIE|34133-9^Summarization of Episode Note^LN|||20260409140000|||||||20260409141000||35001^Oglesby^Michael^P^^^MD||||||20260409152500||DOC|F
OBX|1|ED|34133-9^CCD Document^LN||^application^xml^Base64^PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIiB4bWxuczp2b2M9InVybjpobDctb3JnOnYzL3ZvYyIgY2xhc3NDb2RlPSJET0NQUk9HIiBtb29kQ29kZT0iRVZOIj4=||||||F
```

---

## 11. ADT^A08 - Patient update from Emanuel Medical Center, Swainsboro

```
MSH|^~\&|HEALTHIE_GA|EMANUEL_MC|GA_HIE|HEALTHIE|20260410093000||ADT^A08^ADT_A08|MSG20011|P|2.5.1|||AL|NE
EVN|A08|20260410092500|||SYSTEM
PID|1||EM1101234^^^EMANUEL_MRN^MR||Gilstrap^Vanessa^Denise^^Ms||19830522|F|||117 Kite Rd^^Swainsboro^GA^30401^US||^PRN^PH^^1^478^5550201~^PRN^CP^^1^478^5550202||||S||EM1101234001|258-03-9174
PV1|1|I|2MED^208^A^EMANUEL_MC^^^^NURS|E|||36001^Cantrell^Robert^A^^^MD|||MED||||A|||36001^Cantrell^Robert^A^^^MD|IN||AMBETTER
```

---

## 12. QBP^Q22 - Patient demographics query from Telfair County Health Dept

```
MSH|^~\&|HEATHIE|TELFAIR_HD|GA_HIE|HEALTHIE|20260411100000||QBP^Q22^QBP_Q21|MSG20012|P|2.5.1|||AL|NE
QPD|Q22^Find Candidates^HL70471|QRY20012|@PID.5.1^Gantt|@PID.7^19580412|@PID.8^M|@PID.11.4^GA
RCP|I|10^RD
```

---

## 13. ORU^R01 - Lipid panel results from Coffee Regional Medical Center

```
MSH|^~\&|SUNLINK|COFFEE_REG|GA_HIE|HEALTHIE|20260412110000||ORU^R01^ORU_R01|MSG20013|P|2.5.1|||AL|NE
PID|1||CF1301234^^^COFFEE_MRN^MR||Strickland^Kenneth^Wayne^^Mr||19710918|M|||1101 Ocilla Rd^^Douglas^GA^31533^US||^PRN^PH^^1^912^5550301||||M||CF1301234001|360-49-7182
PV1|1|O|FP^EXAM1^^COFFEE_REG^^^^OUTPT|R|||37001^Oglesby^Sandra^J^^^MD|||FP||||N|||37001^Oglesby^Sandra^J^^^MD|OP||BCBS
ORC|RE|ORD5849372^COFFEE|LAB847362^COFFEE_LAB|||CM||||||37001^Oglesby^Sandra^J^^^MD
OBR|1|ORD5849372^COFFEE|LAB847362^COFFEE_LAB|57698-3^Lipid Panel^LN|||20260412083000|||||||20260412084000||37001^Oglesby^Sandra^J^^^MD||||||20260412105500||LAB|F
OBX|1|NM|2093-3^Total Cholesterol^LN||248|mg/dL|<200|H|||F|||20260412105500
OBX|2|NM|2571-8^Triglycerides^LN||195|mg/dL|<150|H|||F|||20260412105500
OBX|3|NM|2085-9^HDL Cholesterol^LN||38|mg/dL|>40|L|||F|||20260412105500
OBX|4|NM|13457-7^LDL Cholesterol (Calc)^LN||171|mg/dL|<100|H|||F|||20260412105500
```

---

## 14. MDM^T02 - Discharge summary from Meadows Regional Medical Center

```
MSH|^~\&|HEALTHIE_GA|MEADOWS_REG|GA_HIE|HEALTHIE|20260413150000||MDM^T02^MDM_T02|MSG20014|P|2.5.1|||AL|NE
EVN|T02|20260413145500
PID|1||ME1401234^^^MEADOWS_MRN^MR||Chesnut^Dorothy^Irene^^Mrs||19530701|F|||1 Meadows Ln^^Vidalia^GA^30474^US||^PRN^PH^^1^912^5550401||||W||ME1401234001|471-82-5036
PV1|1|I|1MED^112^A^MEADOWS_REG^^^^NURS|E|||38001^Whitworth^Thomas^C^^^MD|||MED||||D|||38001^Whitworth^Thomas^C^^^MD|IN||MEDICARE
TXA|1|DS^Discharge Summary|TX|20260413143000|38001^Whitworth^Thomas^C^^^MD||20260413145500||||DOC7384629^SUNLINK||||AU||AV
OBX|1|TX|18842-5^Discharge Summary^LN||Admitted for acute exacerbation of COPD. Treated with IV steroids and bronchodilators. Pulmonary function improved. Discharged on home oxygen and prednisone taper. Follow-up in 1 week.||||||F
```

---

## 15. ADT^A01 - Admission at Appling Healthcare, Baxley

```
MSH|^~\&|SUNLINK|APPLING_HC|GA_HIE|HEALTHIE|20260414053000||ADT^A01^ADT_A01|MSG20015|P|2.5.1|||AL|NE
EVN|A01|20260414052500|||PJONES^Steadman^Paulette^F^^RN
PID|1||AP1501234^^^APPLING_MRN^MR||Kincaid^William^Franklin^^Mr||19490319|M|||163 E Tollison St^^Baxley^GA^31513^US||^PRN^PH^^1^912^5550501||||M||AP1501234001|582-30-7149
PV1|1|I|1MED^106^A^APPLING_HC^^^^NURS|E|||39001^Ridgeway^Karen^L^^^MD|||MED||||A|||39001^Ridgeway^Karen^L^^^MD|IN||MEDICARE|||||||||||||||||||APPLING_HC|||||20260414052500
DG1|1||I50.9^Heart failure, unspecified^ICD10||20260414|A
NK1|1|Kincaid^Mary^Louise|SPO^Spouse|163 E Tollison St^^Baxley^GA^31513^US|^PRN^PH^^1^912^5550502
```

---

## 16. MDM^T02 - CCD document with embedded base64 from Tift Regional

```
MSH|^~\&|HEALTHIE_GA|TIFT_REG|GA_HIE|HEALTHIE|20260415113000||MDM^T02^MDM_T02|MSG20016|P|2.5.1|||AL|NE
EVN|T02|20260415112500
PID|1||TF1601234^^^TIFT_MRN^MR||Chesnut^Shirley^Faye^^Mrs||19660504|F|||901 E 18th St^^Tifton^GA^31794^US||^PRN^PH^^1^229^5550601||||M||TF1601234001|649-13-0827
PV1|1|I|2MED^215^A^TIFT_REG^^^^NURS|E|||40001^Littlefield^Dennis^W^^^MD|||MED||||D|||40001^Littlefield^Dennis^W^^^MD|IN||HUMANA
TXA|1|CCD^Continuity of Care Document|TX|20260415110000|40001^Littlefield^Dennis^W^^^MD||20260415112500||||DOC8493726^SUNLINK||||AU||AV
OBX|1|ED|34133-9^CCD Document^LN||^application^xml^Base64^PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48cmVhbG1Db2RlIGNvZGU9IlVTIi8+PGNvbXBvbmVudD48c3RydWN0dXJlZEJvZHk+PC9zdHJ1Y3R1cmVkQm9keT48L2NvbXBvbmVudD4=||||||F
```

---

## 17. VXU^V04 - Adult immunization from Lowndes County Health Department

```
MSH|^~\&|SUNLINK|LOWNDES_HD|GA_HIE|HEALTHIE|20260416083000||VXU^V04^VXU_V04|MSG20017|P|2.5.1|||AL|NE
PID|1||LO1701234^^^LOWNDES_HD_MRN^MR||Wimberly^Gregory^Allen^^Mr||19560712|M|||2205 N Ashley St^^Valdosta^GA^31602^US||^PRN^PH^^1^229^5550701||||M||LO1701234001|730-25-4891
PV1|1|I|SNF^305^A^LOWNDES_HD||||7890123456^Cantrell^Jennifer^R^^^MD||SNF||||R
RXA|0|1|20260416082000|20260416082500|33^Pneumococcal polysaccharide PPV23^CVX|0.5|mL||00^New immunization record^NIP001||||||W1234DD||MSD^Merck^MVX|||CP|A
RXR|IM^Intramuscular^HL70162|LD^Left Deltoid^HL70163
OBX|1|CE|64994-7^Vaccine funding source^LN||VXC2^Federal funds^CDCPHINVS||||||F
```

---

## 18. ACK - Acknowledgment for VXU from HealtHIE

```
MSH|^~\&|GA_HIE|HEALTHIE|SUNLINK|LOWNDES_HD|20260416083100||ACK^V04^ACK|MSG20018|P|2.5.1|||AL|NE
MSA|AA|MSG20017|Immunization record accepted and forwarded to GRITS
```

---

## 19. ADT^A01 - Admission at Bacon County Hospital

```
MSH|^~\&|HEATHIE|BACON_HOSP|GA_HIE|HEALTHIE|20260417061500||ADT^A01^ADT_A01|MSG20019|P|2.5.1|||AL|NE
EVN|A01|20260417061000|||TWADE^Steadman^Teresa^S^^RN
PID|1||BC1901234^^^BACON_MRN^MR||Ogletree^Annie^Pearl^^Mrs||19510214|F|||302 S Dixon St^^Alma^GA^31510^US||^PRN^PH^^1^912^5550801||||W||BC1901234001|814-06-3952
PV1|1|I|1MED^103^A^BACON_HOSP^^^^NURS|E|||41001^Beckett^Daniel^J^^^MD|||MED||||A|||41001^Beckett^Daniel^J^^^MD|IN||MEDICARE|||||||||||||||||||BACON_HOSP|||||20260417061000
DG1|1||K92.0^Hematemesis^ICD10||20260417|A
NK1|1|Ogletree^Ernest^Ray|SPO^Spouse|302 S Dixon St^^Alma^GA^31510^US|^PRN^PH^^1^912^5550802
```

---

## 20. ORU^R01 - Thyroid panel from Colquitt Regional Medical Center

```
MSH|^~\&|HEALTHIE_GA|COLQUITT_REG|GA_HIE|HEALTHIE|20260418143000||ORU^R01^ORU_R01|MSG20020|P|2.5.1|||AL|NE
PID|1||CQ2001234^^^COLQUITT_MRN^MR||Blackburn^Joyce^Elaine^^Mrs||19680827|F|||410 5th Ave SE^^Moultrie^GA^31768^US||^PRN^PH^^1^229^5550901||||M||CQ2001234001|927-58-4013
PV1|1|O|IM^EXAM1^^COLQUITT_REG^^^^OUTPT|R|||42001^Cantrell^Donna^K^^^MD|||IM||||N|||42001^Cantrell^Donna^K^^^MD|OP||ANTHEM
ORC|RE|ORD4938271^COLQUITT|LAB738495^COLQUITT_LAB|||CM||||||42001^Cantrell^Donna^K^^^MD
OBR|1|ORD4938271^COLQUITT|LAB738495^COLQUITT_LAB|80091^Thyroid Panel^CPT|||20260418120000|||||||20260418121500||42001^Cantrell^Donna^K^^^MD||||||20260418142500||LAB|F
OBX|1|NM|3016-3^TSH^LN||6.8|uIU/mL|0.27-4.20|H|||F|||20260418142500
OBX|2|NM|3024-7^Free T4^LN||0.7|ng/dL|0.9-1.7|L|||F|||20260418142500
OBX|3|NM|3053-6^Free T3^LN||2.1|pg/mL|2.0-4.4|N|||F|||20260418142500
```
