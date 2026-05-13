# MEDITECH - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Inpatient admission at Erlanger Medical Center

```
MSH|^~\&|MEDITECH|ERLANGER_MC|REGADT|ERLANGER_MC|20260509081500||ADT^A01^ADT_A01|MT000001|P|2.5.1
EVN|A01|20260509081500
PID|1||MRN60012345^^^ERLANGER_MC^MR||Chambers^Denise^Lashawn^^Mrs.||19810623|F||2054-5^Black or African American^HL70005|3417 Brainerd Rd^^Chattanooga^TN^37411||^PRN^PH^^1^423^6819274|^WPN^PH^^1^423^6819830|||M|||401-72-5683
PV1||I|4SOUTH^4S08^01^ERLANGER_MC^^^^4 South Nursing||||1001234^Nagendra^Rajiv^K^^^MD|2002345^Compton^Marcus^D^^^MD|||MED||||ADM|A0||||||||||||||||||||||||||20260509081500
IN1|1|BCBS001|TN44567|BlueCross BlueShield of Tennessee|1 Cameron Hill Cir^^Chattanooga^TN^37402||^PRN^PH^^1^800^5658298|GRPBCBS2026|||||||Chambers^Denise^Lashawn|01|19810623|3417 Brainerd Rd^^Chattanooga^TN^37411
```

## 2. ADT^A02 - Patient transfer at Ballad Health Johnson City

```
MSH|^~\&|MT_EXPANSE|BALLAD_JCMC|NURSING|BALLAD_JCMC|20260508142200||ADT^A02^ADT_A02|MT000002|P|2.5.1
EVN|A02|20260508142200
PID|1||MRN60023456^^^BALLAD_JCMC^MR||Hargrove^William^Preston^^Mr.||19570314|M||2106-3^White^HL70005|2104 Sunset Dr^^Johnson City^TN^37604||^PRN^PH^^1^423^7823491||||M|||512-83-6701
PV1||I|ICU^ICU06^01^BALLAD_JCMC^^^^ICU||||3003456^Okafor^Karen^E^^^MD|4004567^Srinivasan^Deepak^R^^^MD|||CAR||||ADM|A0|||||||||||||||||||3WEST^3W12^02^BALLAD_JCMC^^^^3 West Stepdown|||||20260506093000
```

## 3. ADT^A03 - Discharge from Vanderbilt Wilson County Hospital

```
MSH|^~\&|MEDITECH|VUMC_WILSON|BILLING|VUMC_WILSON|20260507163000||ADT^A03^ADT_A03|MT000003|P|2.5.1
EVN|A03|20260507163000
PID|1||MRN60034567^^^VUMC_WILSON^MR||Satterfield^Deborah^Ann^^Ms.||19690817|F||2106-3^White^HL70005|407 Castle Heights Ave^^Lebanon^TN^37087||^PRN^PH^^1^615^4027891||||D|||623-18-9347
PV1||I|2EAST^2E14^01^VUMC_WILSON^^^^2 East||||5005678^Underwood^Teresa^M^^^MD|6006789^Hatcher^Charles^A^^^MD|||OBS||||ADM|A0||||||||||||||||||||||||||20260504111500|20260507163000
DG1|1||J44.1^Chronic obstructive pulmonary disease with acute exacerbation^I10||20260504|A
```

## 4. ADT^A04 - Outpatient registration at Cookeville Regional

```
MSH|^~\&|MEDEXP|COOKEVILLE_RMC|CLINICS|COOKEVILLE_RMC|20260509073000||ADT^A04^ADT_A01|MT000004|P|2.5.1
EVN|A04|20260509073000
PID|1||MRN60045678^^^COOKEVILLE_RMC^MR||Whitfield^James^Carlton^^Mr.||19820905|M||2106-3^White^HL70005|891 Spring St^^Cookeville^TN^38501||^PRN^PH^^1^931^5284716||||S|||734-41-2059
PV1||O|ORTHO^ORT03^01^COOKEVILLE_RMC^^^^Orthopedics Clinic||||7007890^Lockhart^Steven^W^^^MD|||ORT||||REF|A0||||||||||||||||||||||||||20260509073000
IN1|1|UHCTN01|UHC55678|UnitedHealthcare of Tennessee|10 Cadillac Dr^^Brentwood^TN^37027||^PRN^PH^^1^800^3284344|GRPUHC2026|||||||Whitfield^James^Carlton|01|19820905|891 Spring St^^Cookeville^TN^38501
```

## 5. ADT^A08 - Patient information update at Erlanger East

```
MSH|^~\&|MT_EXPANSE|ERLANGER_EAST|REG|ERLANGER_EAST|20260508104500||ADT^A08^ADT_A01|MT000005|P|2.5.1
EVN|A08|20260508104500
PID|1||MRN60056789^^^ERLANGER_EAST^MR||Fuentes^Maria^Catalina^^Mrs.||19750130|F||2106-3^White^HL70005|6210 Lee Hwy^^Chattanooga^TN^37421||^PRN^PH^^1^423^9047312~^PRN^CP^^1^423^9041587||||M|||845-60-3298
PV1||O|CARDCLN^CARD02^01^ERLANGER_EAST^^^^Cardiology Clinic||||8008901^Blevins^Li^W^^^MD|||CAR||||REF|A0||||||||||||||||||||||||||20260501143000
```

## 6. ADT^A01 - Emergency admission at Blount Memorial Hospital

```
MSH|^~\&|MEDITECH|BLOUNT_MEM|EDIS|BLOUNT_MEM|20260509031500||ADT^A01^ADT_A01|MT000006|P|2.5.1
EVN|A01|20260509031500
PID|1||MRN60067890^^^BLOUNT_MEM^MR||Tipton^Bobby^Wayne^^Mr.||19630412|M||2106-3^White^HL70005|1308 W Broadway Ave^^Maryville^TN^37801||^PRN^PH^^1^865^2194738||||W|||456-31-8724
PV1||E|ED^ED03^01^BLOUNT_MEM^^^^Emergency||||9009012^Pennington^Jessica^L^^^MD|||EM||||ER|A0||||||||||||||||||||||||||20260509031500
DG1|1||I21.3^ST elevation myocardial infarction of unspecified site^I10||20260509|A
IN1|1|AETNA001|AET901234|Aetna Better Health of Tennessee|1 Vantage Way^^Nashville^TN^37228||^PRN^PH^^1^800^2792747|GRPAET2026|||||||Tipton^Bobby^Wayne|01|19630412|1308 W Broadway Ave^^Maryville^TN^37801
```

## 7. ORM^O01 - Lab order from Erlanger Medical Center

```
MSH|^~\&|MT_EXPANSE|ERLANGER_MC|LABCORE|ERLANGER_MC|20260509091500||ORM^O01^ORM_O01|MT000007|P|2.5.1
PID|1||MRN60012345^^^ERLANGER_MC^MR||Chambers^Denise^Lashawn^^Mrs.||19810623|F||2054-5^Black or African American^HL70005|3417 Brainerd Rd^^Chattanooga^TN^37411||^PRN^PH^^1^423^6819274
PV1||I|4SOUTH^4S08^01^ERLANGER_MC||||1001234^Nagendra^Rajiv^K^^^MD
ORC|NW|ORD70100001|||||^^^20260509091500^^R||20260509091500|NURSE010^Yancey^Patricia||1001234^Nagendra^Rajiv^K^^^MD|4SOUTH
OBR|1|ORD70100001||CBC^Complete Blood Count^L|||20260509091500||||A|||||1001234^Nagendra^Rajiv^K^^^MD||||||20260509091500|||F
OBR|2|ORD70100002||CMP^Comprehensive Metabolic Panel^L|||20260509091500||||A|||||1001234^Nagendra^Rajiv^K^^^MD||||||20260509091500|||F
OBR|3|ORD70100003||PROT^Prothrombin Time^L|||20260509091500||||A|||||1001234^Nagendra^Rajiv^K^^^MD||||||20260509091500|||F
```

## 8. ORM^O01 - Radiology order from Ballad Health Bristol

```
MSH|^~\&|MEDEXP|BALLAD_BRMC|RADIS|BALLAD_BRMC|20260508155000||ORM^O01^ORM_O01|MT000008|P|2.5.1
PID|1||MRN60078901^^^BALLAD_BRMC^MR||Bledsoe^Sandra^Michelle^^Ms.||19880221|F||2106-3^White^HL70005|741 Volunteer Pkwy^^Bristol^TN^37620||^PRN^PH^^1^423^8524017
PV1||E|ED^ED07^01^BALLAD_BRMC^^^^Emergency||||1101234^Quillen^Mark^T^^^MD
ORC|NW|ORD70200001|||||^^^20260508155000^^S||20260508155000|NURSE011^Goins^Kelly||1101234^Quillen^Mark^T^^^MD|ED
OBR|1|ORD70200001||71260^CT Chest with contrast^CPT|||20260508155000||||A|||STAT^Stat^HL70078||1101234^Quillen^Mark^T^^^MD||||||20260508155000|||F
```

## 9. ORU^R01 - CBC results from Erlanger Medical Center

```
MSH|^~\&|MT_EXPANSE|ERLANGER_MC|MEDITECH|ERLANGER_MC|20260509112000||ORU^R01^ORU_R01|MT000009|P|2.5.1
PID|1||MRN60012345^^^ERLANGER_MC^MR||Chambers^Denise^Lashawn^^Mrs.||19810623|F||2054-5^Black or African American^HL70005|3417 Brainerd Rd^^Chattanooga^TN^37411||^PRN^PH^^1^423^6819274
PV1||I|4SOUTH^4S08^01^ERLANGER_MC||||1001234^Nagendra^Rajiv^K^^^MD
ORC|RE|ORD70100001||||||^^^20260509091500^^R||20260509112000|LAB010^Velasquez^Roberto||1001234^Nagendra^Rajiv^K^^^MD
OBR|1|ORD70100001||CBC^Complete Blood Count^L|||20260509091500|||||||20260509100000|B^Blood|1001234^Nagendra^Rajiv^K^^^MD||||||20260509112000|||F
OBX|1|NM|6690-2^WBC^LN||11.8|10*3/uL|4.5-11.0|H|||F|||20260509111500
OBX|2|NM|789-8^RBC^LN||4.12|10*6/uL|3.80-5.10|N|||F|||20260509111500
OBX|3|NM|718-7^Hemoglobin^LN||12.1|g/dL|12.0-16.0|N|||F|||20260509111500
OBX|4|NM|4544-3^Hematocrit^LN||36.4|%|36.0-46.0|N|||F|||20260509111500
OBX|5|NM|787-2^MCV^LN||88.3|fL|80.0-100.0|N|||F|||20260509111500
OBX|6|NM|777-3^Platelet Count^LN||198|10*3/uL|150-400|N|||F|||20260509111500
```

## 10. ORU^R01 - Pathology report with encapsulated PDF from Ballad Health

```
MSH|^~\&|MEDITECH|BALLAD_JCMC|MT_EXPANSE|BALLAD_JCMC|20260508171500||ORU^R01^ORU_R01|MT000010|P|2.5.1
PID|1||MRN60023456^^^BALLAD_JCMC^MR||Hargrove^William^Preston^^Mr.||19570314|M||2106-3^White^HL70005|2104 Sunset Dr^^Johnson City^TN^37604||^PRN^PH^^1^423^7823491
PV1||I|ICU^ICU06^01^BALLAD_JCMC||||3003456^Okafor^Karen^E^^^MD
ORC|RE|ORD70300001||||||^^^20260506140000^^R||20260508171500|PATH010^Nakamura^Kenji||3003456^Okafor^Karen^E^^^MD
OBR|1|ORD70300001||11529-5^Surgical Pathology Report^LN|||20260506140000|||||||20260506150000|T^Tissue|3003456^Okafor^Karen^E^^^MD||||||20260508171500|||F
OBX|1|ED|11529-5^Surgical Pathology Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDE1MSAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDQKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjIwMQolJUVPRgo=||||||F|||20260508171500
```

## 11. ORU^R01 - Radiology report with encapsulated PDF from Cookeville Regional

```
MSH|^~\&|MT6X|COOKEVILLE_RMC|MEDEXP|COOKEVILLE_RMC|20260508163000||ORU^R01^ORU_R01|MT000011|P|2.5.1
PID|1||MRN60045678^^^COOKEVILLE_RMC^MR||Whitfield^James^Carlton^^Mr.||19820905|M||2106-3^White^HL70005|891 Spring St^^Cookeville^TN^38501||^PRN^PH^^1^931^5284716
PV1||O|ORTHO^ORT03^01^COOKEVILLE_RMC||||7007890^Lockhart^Steven^W^^^MD
ORC|RE|ORD70400001||||||^^^20260508100000^^R||20260508163000|RAD010^Kapoor^Priya||7007890^Lockhart^Steven^W^^^MD
OBR|1|ORD70400001||73565^Knee X-ray bilateral^CPT|||20260508100000|||||||20260508110000|^Knee|7007890^Lockhart^Steven^W^^^MD||||||20260508163000|||F
OBX|1|ED|73565^Knee X-ray bilateral^CPT||^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCj4+CmVuZG9iagozIDAgb2JqCjw8IC9UeXBlIC9QYWdlCi9QYXJlbnQgMiAwIFIKPj4KZW5kb2JqCnhyZWYKMCA0CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxNTEgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA0Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgoyMDEKJSVFT0YK||||||F|||20260508163000
OBX|2|FT|73565^Knee X-ray bilateral^CPT||IMPRESSION: Bilateral tricompartmental osteoarthritis, moderate. No acute fracture or dislocation. Mild joint effusion on the left.||||||F|||20260508163000
```

## 12. ORU^R01 - Troponin critical result from Erlanger East

```
MSH|^~\&|MEDITECH|ERLANGER_EAST|MT_EXPANSE|ERLANGER_EAST|20260509042000||ORU^R01^ORU_R01|MT000012|P|2.5.1
PID|1||MRN60089012^^^ERLANGER_EAST^MR||Hendon^Earl^Russell^^Mr.||19490822|M||2106-3^White^HL70005|4812 Hixson Pike^^Chattanooga^TN^37343||^PRN^PH^^1^423^8726014
PV1||E|ED^ED09^01^ERLANGER_EAST^^^^Emergency Department||||1201234^Callaway^Rebecca^J^^^MD
ORC|RE|ORD70500001||||||^^^20260509033000^^S||20260509042000|LAB011^Reyes^Maria||1201234^Callaway^Rebecca^J^^^MD
OBR|1|ORD70500001||TROP^Troponin I^L|||20260509033000|||||||20260509034500|B^Blood|1201234^Callaway^Rebecca^J^^^MD||||||20260509042000|||F
OBX|1|NM|10839-9^Troponin I^LN||3.82|ng/mL|0.00-0.04|HH|||F|||20260509041500
NTE|1||CRITICAL VALUE - Physician notified at 0420 by Lab Tech Reyes. Dr. Callaway acknowledged.
```

## 13. ORU^R01 - Metabolic panel results from Blount Memorial

```
MSH|^~\&|MT_EXPANSE|BLOUNT_MEM|MEDITECH|BLOUNT_MEM|20260508183000||ORU^R01^ORU_R01|MT000013|P|2.5.1
PID|1||MRN60067890^^^BLOUNT_MEM^MR||Tipton^Bobby^Wayne^^Mr.||19630412|M||2106-3^White^HL70005|1308 W Broadway Ave^^Maryville^TN^37801||^PRN^PH^^1^865^2194738
PV1||E|ED^ED03^01^BLOUNT_MEM||||9009012^Pennington^Jessica^L^^^MD
ORC|RE|ORD70600001||||||^^^20260509040000^^S||20260508183000|LAB012^Trujillo^Miguel||9009012^Pennington^Jessica^L^^^MD
OBR|1|ORD70600001||CMP^Comprehensive Metabolic Panel^L|||20260509040000|||||||20260509050000|B^Blood|9009012^Pennington^Jessica^L^^^MD||||||20260508183000|||F
OBX|1|NM|2345-7^Glucose^LN||142|mg/dL|74-106|H|||F|||20260508182000
OBX|2|NM|3094-0^BUN^LN||28|mg/dL|6-20|H|||F|||20260508182000
OBX|3|NM|2160-0^Creatinine^LN||1.6|mg/dL|0.7-1.3|H|||F|||20260508182000
OBX|4|NM|2951-2^Sodium^LN||138|mmol/L|136-145|N|||F|||20260508182000
OBX|5|NM|2823-3^Potassium^LN||5.4|mmol/L|3.5-5.1|H|||F|||20260508182000
OBX|6|NM|1742-6^ALT^LN||32|U/L|7-56|N|||F|||20260508182000
OBX|7|NM|1920-8^AST^LN||45|U/L|10-40|H|||F|||20260508182000
```

## 14. MDM^T02 - History and physical document from Ballad Health Kingsport

```
MSH|^~\&|MEDEXP|BALLAD_HVMC|DOCMGMT|BALLAD_HVMC|20260508191500||MDM^T02^MDM_T02|MT000014|P|2.5.1
EVN|T02|20260508191500
PID|1||MRN60090123^^^BALLAD_HVMC^MR||Matney^Linda^Paulette^^Mrs.||19710509|F||2106-3^White^HL70005|2603 Memorial Blvd^^Kingsport^TN^37664||^PRN^PH^^1^423^3461078
PV1||I|3NORTH^3N05^01^BALLAD_HVMC||||1301234^Elswick^Gregory^T^^^MD
TXA|1|HP^History and Physical^HL70270|TX|20260508191500|1301234^Elswick^Gregory^T^^^MD||20260508191500|||||DOC20260508001|||AU||AV||||1301234^Elswick^Gregory^T^^^MD
OBX|1|TX|11488-4^Consultation Note^LN||HISTORY OF PRESENT ILLNESS: 55-year-old female presenting with worsening dyspnea on exertion over two weeks and bilateral lower extremity edema.||||||F
OBX|2|TX|11488-4^Consultation Note^LN||PHYSICAL EXAMINATION: BP 158/94, HR 98, RR 24, SpO2 91% on RA. JVD present. Bilateral basilar crackles. 2+ pitting edema bilaterally.||||||F
OBX|3|TX|11488-4^Consultation Note^LN||ASSESSMENT AND PLAN: Acute on chronic systolic heart failure exacerbation. Start IV furosemide 40mg BID. Obtain echocardiogram and BNP. Cardiology consult.||||||F
```

## 15. MDM^T02 - Discharge summary from Maury Regional Medical Center

```
MSH|^~\&|MT_EXPANSE|MAURY_RMC|DOCMGMT|MAURY_RMC|20260507170000||MDM^T02^MDM_T02|MT000015|P|2.5.1
EVN|T02|20260507170000
PID|1||MRN60101234^^^MAURY_RMC^MR||Grisham^Ernest^Howard^^Mr.||19560728|M||2106-3^White^HL70005|1415 Trotwood Ave^^Columbia^TN^38401||^PRN^PH^^1^931^3814502
PV1||I|5EAST^5E09^01^MAURY_RMC||||1401234^Malone^Carmen^L^^^MD
TXA|1|DS^Discharge Summary^HL70270|TX|20260507170000|1401234^Malone^Carmen^L^^^MD||20260507170000|||||DOC20260507001|||AU||AV||||1401234^Malone^Carmen^L^^^MD
OBX|1|TX|18842-5^Discharge Summary^LN||DISCHARGE DIAGNOSIS: Bilateral pneumonia. Type 2 diabetes mellitus, uncontrolled. HOSPITAL COURSE: Admitted 5/3 with fever, productive cough, hypoxia. CT chest confirmed bilateral infiltrates. Treated with piperacillin-tazobactam and vancomycin IV. Blood cultures negative. Transitioned to oral levofloxacin day 4. Insulin sliding scale adjusted.||||||F
OBX|2|TX|18842-5^Discharge Summary^LN||DISCHARGE MEDICATIONS: Levofloxacin 750mg PO daily x4 days. Metformin 1000mg PO BID. Insulin glargine 24 units SQ at bedtime. Albuterol inhaler 2 puffs Q4-6H PRN.||||||F
OBX|3|TX|18842-5^Discharge Summary^LN||FOLLOW-UP: PCP Dr. Malone in 5 days. Endocrinology in 2 weeks. Return to ED if fever >101.5F, worsening shortness of breath, or hemoptysis.||||||F
```

## 16. DFT^P03 - Charge posting from Erlanger Medical Center

```
MSH|^~\&|MEDITECH|ERLANGER_MC|BILLING|ERLANGER_MC|20260509140000||DFT^P03^DFT_P03|MT000016|P|2.5.1
EVN|P03|20260509140000
PID|1||MRN60012345^^^ERLANGER_MC^MR||Chambers^Denise^Lashawn^^Mrs.||19810623|F||2054-5^Black or African American^HL70005|3417 Brainerd Rd^^Chattanooga^TN^37411||^PRN^PH^^1^423^6819274
PV1||I|4SOUTH^4S08^01^ERLANGER_MC||||1001234^Nagendra^Rajiv^K^^^MD
FT1|1|CHG20260509001||20260509|20260509|CG|99223^Initial hospital care, high severity^CPT||1|||||||4SOUTH|F|||99223^Initial hospital care, high severity^CPT
FT1|2|CHG20260509002||20260509|20260509|CG|36415^Collection of venous blood by venipuncture^CPT||1|||||||4SOUTH|F|||36415^Collection of venous blood by venipuncture^CPT
FT1|3|CHG20260509003||20260509|20260509|CG|85025^Complete blood count with differential^CPT||1|||||||4SOUTH|F|||85025^Complete blood count with differential^CPT
```

## 17. DFT^P03 - ED charge posting from Blount Memorial

```
MSH|^~\&|MT6X|BLOUNT_MEM|BILLING|BLOUNT_MEM|20260509080000||DFT^P03^DFT_P03|MT000017|P|2.5.1
EVN|P03|20260509080000
PID|1||MRN60067890^^^BLOUNT_MEM^MR||Tipton^Bobby^Wayne^^Mr.||19630412|M||2106-3^White^HL70005|1308 W Broadway Ave^^Maryville^TN^37801||^PRN^PH^^1^865^2194738
PV1||E|ED^ED03^01^BLOUNT_MEM||||9009012^Pennington^Jessica^L^^^MD
FT1|1|CHG20260509010||20260509|20260509|CG|99285^Emergency department visit, high severity^CPT||1|||||||ED|F|||99285^Emergency department visit, high severity^CPT
FT1|2|CHG20260509011||20260509|20260509|CG|71260^CT chest with contrast^CPT||1|||||||ED|F|||71260^CT chest with contrast^CPT
FT1|3|CHG20260509012||20260509|20260509|CG|93010^Electrocardiogram, interpretation and report^CPT||1|||||||ED|F|||93010^Electrocardiogram, interpretation and report^CPT
FT1|4|CHG20260509013||20260509|20260509|CG|10839-9^Troponin I, cardiac^CPT||1|||||||ED|F|||10839-9^Troponin I, cardiac^CPT
```

## 18. BAR^P01 - Account billing from Cookeville Regional

```
MSH|^~\&|MEDEXP|COOKEVILLE_RMC|BILLING|COOKEVILLE_RMC|20260508120000||BAR^P01^BAR_P01|MT000018|P|2.5.1
EVN|P01|20260508120000
PID|1||MRN60112345^^^COOKEVILLE_RMC^MR||Birdwell^Dorothy^Elaine^^Mrs.||19480303|F||2106-3^White^HL70005|512 N Dixie Ave^^Cookeville^TN^38501||^PRN^PH^^1^931^5207894||||W|||234-71-6053
PV1||I|2WEST^2W11^01^COOKEVILLE_RMC||||1501234^Farley^Harold^F^^^MD|||MED||||ADM|A0||||||||||||||||||||||||||20260505090000|20260508120000
DG1|1||N17.9^Acute kidney injury, unspecified^I10||20260505|A
DG1|2||E11.65^Type 2 diabetes mellitus with hyperglycemia^I10||20260505|A
IN1|1|MCARETN01|MCARE6789|Medicare Part A|7500 Security Blvd^^Baltimore^MD^21244||^PRN^PH^^1^800^6334227|GRPMCARE2026|||||||Birdwell^Dorothy^Elaine|01|19480303|512 N Dixie Ave^^Cookeville^TN^38501
IN1|2|MSUPP01|MSUPP3456|AARP Medicare Supplement - UnitedHealthcare|PO Box 740819^^Atlanta^GA^30374||^PRN^PH^^1^800^5231899|GRPMSUPP2026|||||||Birdwell^Dorothy^Elaine|01|19480303|512 N Dixie Ave^^Cookeville^TN^38501
```

## 19. BAR^P01 - Outpatient billing from Maury Regional

```
MSH|^~\&|MT_EXPANSE|MAURY_RMC|BILLING|MAURY_RMC|20260509100000||BAR^P01^BAR_P01|MT000019|P|2.5.1
EVN|P01|20260509100000
PID|1||MRN60123456^^^MAURY_RMC^MR||Pickard^Crystal^Monique^^Ms.||19930615|F||2054-5^Black or African American^HL70005|802 Nashville Hwy^^Columbia^TN^38401||^PRN^PH^^1^931^6148205||||S|||567-42-8139
PV1||O|RADCLN^RAD04^01^MAURY_RMC^^^^Radiology||||1601234^Stovall^Barbara^A^^^MD|||RAD||||REF|A0||||||||||||||||||||||||||20260509100000
DG1|1||M54.5^Low back pain^I10||20260509|A
IN1|1|CIGNA001|CIGN8901|Cigna HealthCare of Tennessee|900 Cottage Grove Rd^^Bloomfield^CT^06002||^PRN^PH^^1^800^2446224|GRPCIGN2026|||||||Pickard^Crystal^Monique|01|19930615|802 Nashville Hwy^^Columbia^TN^38401
```

## 20. ADT^A08 - Insurance update at Ballad Health Johnson City

```
MSH|^~\&|MT6X|BALLAD_JCMC|REG|BALLAD_JCMC|20260509113000||ADT^A08^ADT_A01|MT000020|P|2.5.1
EVN|A08|20260509113000
PID|1||MRN60134567^^^BALLAD_JCMC^MR||Ketron^Roger^Mitchell^^Mr.||19680911|M||2106-3^White^HL70005|3008 Fort Henry Dr^^Kingsport^TN^37664||^PRN^PH^^1^423^2459017~^PRN^CP^^1^423^2453389||||M|||678-54-2910
PV1||I|5NORTH^5N03^01^BALLAD_JCMC^^^^5 North||||1701234^Buchanan^Angela^R^^^MD|||MED||||ADM|A0||||||||||||||||||||||||||20260507152000
IN1|1|HUMANA001|HUM23456|Humana Health Plan of Tennessee|500 W Main St^^Louisville^KY^40202||^PRN^PH^^1^800^4484462|GRPHUM2026|||||||Ketron^Roger^Mitchell|01|19680911|3008 Fort Henry Dr^^Kingsport^TN^37664
NK1|1|Ketron^Patricia^Darlene||^PRN^PH^^1^423^2459018|||||||||||||||||||||||||||||F|19700225
```
