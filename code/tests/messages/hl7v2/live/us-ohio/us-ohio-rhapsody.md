# Rhapsody Integration Engine - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Inpatient admission at Cleveland Clinic Main Campus

```
MSH|^~\&|RHAPSODY|CLEVECLINIC_MAIN|ADT_RECV|CLEVECLINIC_MAIN|20260509071500||ADT^A01^ADT_A01|RHP00001|P|2.5.1
EVN|A01|20260509071500
PID|1||MRN90010001^^^CLEVECLINIC^MR||Petrovic^Nathan^Edward^^Mr.||19680214|M||2106-3^White^HL70005|2917 Superior Ave^^Cleveland^OH^44114||^PRN^PH^^1^216^5551023||||M|||298-41-6734
PV1||I|5WEST^5W12^01^CLEVECLINIC_MAIN^^^^5 West Cardiology||||1234567^Iyer^Kavitha^N^^^MD|2345678^Brennan^Scott^T^^^MD|||CAR||||ADM|A0||||||||||||||||||||||||||20260509071500
IN1|1|ANTHEM001|AN890123|Anthem Blue Cross Blue Shield Ohio|4361 Irwin Simpson Rd^^Mason^OH^45040||^PRN^PH^^1^800^3311476|GRPANT001|||||||Petrovic^Nathan^Edward|01|19680214|2917 Superior Ave^^Cleveland^OH^44114
```

## 2. ADT^A04 - Outpatient registration at Ohio State Wexner Medical Center

```
MSH|^~\&|RHAP_ENGINE|OSUWMC_COLUMBUS|REG_SYS|OSUWMC_COLUMBUS|20260509083000||ADT^A04^ADT_A01|RHP00002|P|2.5.1
EVN|A04|20260509083000
PID|1||MRN90010002^^^OSUWMC^MR||Jefferson^Monique^Renee^^Mrs.||19850917|F||2054-5^Black or African American^HL70005|481 E Livingston Ave^^Columbus^OH^43215||^PRN^PH^^1^614^5528741||||M|||407-52-3816
PV1||O|ENDOCR^EN02^01^OSUWMC_COLUMBUS^^^^Endocrinology||||3456789^Chandra^Rohan^S^^^MD|||END||||WALK|A0||||||||||||||||||||||||||20260509083000
```

## 3. ADT^A08 - Patient information update at University Hospitals Cleveland

```
MSH|^~\&|RHAPSODY|UH_CLEVELAND|REG_SYS|UH_CLEVELAND|20260509091200||ADT^A08^ADT_A01|RHP00003|P|2.5.1
EVN|A08|20260509091200
PID|1||MRN90010003^^^UH_CLEVELAND^MR||Okafor^Amara^Ifeyinwa^^Ms.||19920601|F||2054-5^Black or African American^HL70005|3115 Warrensville Center Rd^^Shaker Heights^OH^44120||^PRN^PH^^1^216^5539842~^PRN^CP^^1^216^5536617||||S|||518-63-4279
PV1||O|OBGYN^OB03^01^UH_CLEVELAND^^^^OB/GYN||||4567890^Liang^Grace^M^^^MD
NK1|1|Okafor^Obinna^Ikechukwu|FTH^Father^HL70063|3115 Warrensville Center Rd^^Shaker Heights^OH^44120|^PRN^PH^^1^216^5539843
```

## 4. ADT^A01 - Emergency admission at Mercy Health St. Vincent Medical Center

```
MSH|^~\&|RHAP_ENGINE|MERCY_STVINCENT|ADT_RECV|MERCY_STVINCENT|20260508224500||ADT^A01^ADT_A01|RHP00004|P|2.5.1
EVN|A01|20260508224500
PID|1||MRN90010004^^^MERCY_TOLEDO^MR||Kowalczyk^Brian^Joseph^^Mr.||19750830|M||2106-3^White^HL70005|3827 Secor Rd^^Toledo^OH^43623||^PRN^PH^^1^419^5547183||||M|||631-74-5902
PV1||E|ED^ED07^01^MERCY_STVINCENT^^^^Emergency||||5678901^Vasquez^Elena^R^^^MD|||EM||||ER|A0||||||||||||||||||||||||||20260508224500
DG1|1||I21.09^Acute ST elevation myocardial infarction of unspecified site^I10||20260508|A
IN1|1|MEDCARE001|MC567890|Medicare Part A|7500 Security Blvd^^Baltimore^MD^21244||^PRN^PH^^1^800^6334227|GRPMC003|||||||Kowalczyk^Brian^Joseph|01|19750830|3827 Secor Rd^^Toledo^OH^43623
```

## 5. ADT^A08 - Insurance update at ProMedica Toledo Hospital

```
MSH|^~\&|RHAPSODY|PROMEDICA_TOL|REG_SYS|PROMEDICA_TOL|20260509101500||ADT^A08^ADT_A01|RHP00005|P|2.5.1
EVN|A08|20260509101500
PID|1||MRN90010005^^^PROMEDICA^MR||Nguyen^Mai^Hanh^^Mrs.||19810312|F||2028-9^Asian^HL70005|2204 Albon Rd^^Maumee^OH^43537||^PRN^PH^^1^419^5516294||||M|||742-85-1038
PV1||O|NEURO^NR01^01^PROMEDICA_TOL^^^^Neurology||||6789012^Callahan^Mark^E^^^MD
IN1|1|UNITED001|UH345678|UnitedHealthcare of Ohio|9900 Bren Rd E^^Minnetonka^MN^55343||^PRN^PH^^1^800^3282789|GRPUHO001|||||||Nguyen^Mai^Hanh|01|19810312|2204 Albon Rd^^Maumee^OH^43537
```

## 6. ORM^O01 - Lab order from OhioHealth Riverside Methodist Hospital

```
MSH|^~\&|RHAP_ENGINE|OHIOHLTH_RIVERSIDE|LABSYS|OHIOHLTH_LAB|20260509080000||ORM^O01^ORM_O01|RHP00006|P|2.5.1
PID|1||MRN90010006^^^OHIOHLTH^MR||Hensley^Patricia^Dawn^^Mrs.||19700425|F||2106-3^White^HL70005|2760 Westerville Rd^^Columbus^OH^43224||^PRN^PH^^1^614^5536478
PV1||I|4EAST^4E08^01^OHIOHLTH_RIVERSIDE^^^^4 East||||7890123^Park^Jin^W^^^MD
ORC|NW|ORD90020001|||||^^^20260509080000^^R||20260509080000|LAB101^Diaz^Rachel||7890123^Park^Jin^W^^^MD|4EAST
OBR|1|ORD90020001||80053^Comprehensive Metabolic Panel^CPT|||20260509080000||||A|||||7890123^Park^Jin^W^^^MD||||||20260509080000|||F
OBR|2|ORD90020002||85025^CBC with Differential^CPT|||20260509080000||||A|||||7890123^Park^Jin^W^^^MD||||||20260509080000|||F
OBR|3|ORD90020003||83036^Hemoglobin A1c^CPT|||20260509080000||||A|||||7890123^Park^Jin^W^^^MD||||||20260509080000|||F
```

## 7. ORM^O01 - Radiology order from Kettering Health Main Campus

```
MSH|^~\&|RHAPSODY|KETTERING_MAIN|RADIS|KETTERING_RAD|20260509093000||ORM^O01^ORM_O01|RHP00007|P|2.5.1
PID|1||MRN90010007^^^KETTERING^MR||Strickland^Earl^Vincent^^Mr.||19590708|M||2106-3^White^HL70005|1840 Wilmington Ave^^Dayton^OH^45420||^PRN^PH^^1^937^5547312
PV1||I|ICU^ICU04^01^KETTERING_MAIN^^^^ICU||||8901234^Mehta^Arvind^K^^^MD
ORC|NW|ORD90020004|||||^^^20260509093000^^S||20260509093000|NURSE201^Caldwell^Tanya||8901234^Mehta^Arvind^K^^^MD|ICU
OBR|1|ORD90020004||71275^CT Angiography Chest^CPT|||20260509093000||||A|||STAT^Stat^HL70078||8901234^Mehta^Arvind^K^^^MD||||||20260509093000|||F
```

## 8. ORU^R01 - Comprehensive metabolic panel results at OhioHealth

```
MSH|^~\&|RHAP_ENGINE|OHIOHLTH_LAB|OHIOHLTH_RIVERSIDE|OHIOHLTH_RIVERSIDE|20260509140000||ORU^R01^ORU_R01|RHP00008|P|2.5.1
PID|1||MRN90010006^^^OHIOHLTH^MR||Hensley^Patricia^Dawn^^Mrs.||19700425|F||2106-3^White^HL70005|2760 Westerville Rd^^Columbus^OH^43224||^PRN^PH^^1^614^5536478
ORC|RE|ORD90020001||||||^^^20260509080000^^R||20260509140000|LAB101^Diaz^Rachel||7890123^Park^Jin^W^^^MD
OBR|1|ORD90020001||80053^Comprehensive Metabolic Panel^CPT|||20260509080000|||||||20260509090000|B^Blood|7890123^Park^Jin^W^^^MD||||||20260509140000|||F
OBX|1|NM|2345-7^Glucose^LN||112|mg/dL|74-106|H|||F|||20260509135000
OBX|2|NM|3094-0^BUN^LN||18|mg/dL|7-20|N|||F|||20260509135000
OBX|3|NM|2160-0^Creatinine^LN||0.9|mg/dL|0.6-1.2|N|||F|||20260509135000
OBX|4|NM|2951-2^Sodium^LN||139|mEq/L|136-145|N|||F|||20260509135000
OBX|5|NM|2823-3^Potassium^LN||4.2|mEq/L|3.5-5.0|N|||F|||20260509135000
OBX|6|NM|2075-0^Chloride^LN||102|mEq/L|98-106|N|||F|||20260509135000
OBX|7|NM|1742-6^ALT^LN||34|U/L|7-56|N|||F|||20260509135000
OBX|8|NM|1920-8^AST^LN||28|U/L|10-40|N|||F|||20260509135000
OBX|9|NM|1975-2^Total Bilirubin^LN||0.8|mg/dL|0.1-1.2|N|||F|||20260509135000
OBX|10|NM|17861-6^Calcium^LN||9.4|mg/dL|8.5-10.5|N|||F|||20260509135000
```

## 9. ORU^R01 - Troponin results with encapsulated PDF at Cleveland Clinic

```
MSH|^~\&|RHAPSODY|CLEVECLINIC_LAB|CLEVECLINIC_MAIN|CLEVECLINIC_MAIN|20260509121500||ORU^R01^ORU_R01|RHP00009|P|2.5.1
PID|1||MRN90010001^^^CLEVECLINIC^MR||Petrovic^Nathan^Edward^^Mr.||19680214|M||2106-3^White^HL70005|2917 Superior Ave^^Cleveland^OH^44114||^PRN^PH^^1^216^5551023
PV1||I|5WEST^5W12^01^CLEVECLINIC_MAIN^^^^5 West Cardiology||||1234567^Iyer^Kavitha^N^^^MD
ORC|RE|CLC90030001||||||^^^20260509071500^^S||20260509121500|LAB102^Polanski^Diane||1234567^Iyer^Kavitha^N^^^MD
OBR|1|CLC90030001||49563-0^Troponin I Cardiac^LN|||20260509071500|||||||20260509080000|B^Blood|1234567^Iyer^Kavitha^N^^^MD||||||20260509121500|||F
OBX|1|NM|49563-0^Troponin I Cardiac^LN||0.85|ng/mL|<0.04|H|||F|||20260509120000
OBX|2|NM|49563-0^Troponin I Cardiac (repeat 3h)^LN||2.34|ng/mL|<0.04|H|||F|||20260509120000
OBX|3|ED|49563-0^Troponin I Cardiac Panel Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UK||||||F|||20260509121000
```

## 10. ORU^R01 - Pathology report with encapsulated PDF at University Hospitals

```
MSH|^~\&|RHAP_ENGINE|UH_PATH_LAB|UH_CLEVELAND|UH_CLEVELAND|20260508163000||ORU^R01^ORU_R01|RHP00010|P|2.5.1
PID|1||MRN90010008^^^UH_CLEVELAND^MR||Dalton^Marcus^Ray^^Mr.||19610320|M||2106-3^White^HL70005|4215 Wallings Rd^^Brecksville^OH^44141||^PRN^PH^^1^216^5538207
PV1||I|7NORTH^7N05^01^UH_CLEVELAND^^^^7 North Oncology||||9012345^Rosario^Claudia^H^^^MD
ORC|RE|UHP90030002||||||^^^20260506100000^^R||20260508163000|PATH301^Whitfield^Gerald||9012345^Rosario^Claudia^H^^^MD
OBR|1|UHP90030002||88305^Surgical Pathology^CPT|||20260506100000|||||||20260506110000|T^Tissue|9012345^Rosario^Claudia^H^^^MD||||||20260508163000|||F
OBX|1|ED|88305^Surgical Pathology Report^CPT||^application^pdf^Base64^JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCj4+CmVuZG9iagozIDAgb2JqCjw8IC9UeXBl||||||F|||20260508162000
OBX|2|FT|88305^Surgical Pathology^CPT||DIAGNOSIS: Colon, sigmoid, polypectomy - Tubular adenoma with low-grade dysplasia, 1.3 cm, completely excised. No evidence of malignancy.||||||F|||20260508162000
```

## 11. ORU^R01 - CBC results from Akron Children's Hospital

```
MSH|^~\&|RHAPSODY|AKRONCH_LAB|AKRONCH_MAIN|AKRONCH_MAIN|20260509151000||ORU^R01^ORU_R01|RHP00011|P|2.5.1
PID|1||MRN90010009^^^AKRONCH^MR||Carpenter^Owen^Lucas^^||20190315|M||2106-3^White^HL70005|718 Tallmadge Ave^^Cuyahoga Falls^OH^44221||^PRN^PH^^1^330^5519408
NK1|1|Carpenter^Megan^Ann|MTH^Mother^HL70063|718 Tallmadge Ave^^Cuyahoga Falls^OH^44221|^PRN^PH^^1^330^5519408
ORC|RE|ACH90030003||||||^^^20260509080000^^R||20260509151000|LAB103^Santiago^Victor||0123456^Banerjee^Nila^P^^^MD
OBR|1|ACH90030003||85025^CBC with Differential^CPT|||20260509080000|||||||20260509090000|B^Blood|0123456^Banerjee^Nila^P^^^MD||||||20260509151000|||F
OBX|1|NM|6690-2^WBC^LN||9.8|10*3/uL|5.0-15.5|N|||F|||20260509150000
OBX|2|NM|718-7^Hemoglobin^LN||12.1|g/dL|11.0-14.0|N|||F|||20260509150000
OBX|3|NM|4544-3^Hematocrit^LN||36.5|%|33.0-42.0|N|||F|||20260509150000
OBX|4|NM|777-3^Platelet Count^LN||312|10*3/uL|150-400|N|||F|||20260509150000
OBX|5|NM|770-8^Neutrophils %^LN||42.0|%|20.0-50.0|N|||F|||20260509150000
OBX|6|NM|736-9^Lymphocytes %^LN||48.0|%|40.0-70.0|N|||F|||20260509150000
```

## 12. MDM^T02 - Transcribed operative report at Cleveland Clinic

```
MSH|^~\&|RHAPSODY|CLEVECLINIC_TRANS|CLEVECLINIC_MAIN|CLEVECLINIC_MAIN|20260509160000||MDM^T02^MDM_T02|RHP00012|P|2.5.1
EVN|T02|20260509160000
PID|1||MRN90010001^^^CLEVECLINIC^MR||Petrovic^Nathan^Edward^^Mr.||19680214|M||2106-3^White^HL70005|2917 Superior Ave^^Cleveland^OH^44114||^PRN^PH^^1^216^5551023
PV1||I|5WEST^5W12^01^CLEVECLINIC_MAIN^^^^5 West Cardiology||||1234567^Iyer^Kavitha^N^^^MD
TXA|1|OP^Operative Report^HL70270|TX^Text^HL70191|20260509140000|1234567^Iyer^Kavitha^N^^^MD|20260509160000||||||DOC90040001||AU^Authenticated^HL70271|||LA^Legally Authenticated^HL70271
OBX|1|TX|11504-8^Surgical Operation Note^LN||OPERATIVE REPORT\.br\Patient: Petrovic, Nathan E\.br\Procedure: Left Heart Catheterization with Coronary Angiography\.br\Date: 05/09/2026\.br\Surgeon: Kavitha N. Iyer, MD\.br\\.br\FINDINGS: 90% stenosis of proximal LAD. 70% stenosis of mid-RCA.\.br\PROCEDURE: Percutaneous coronary intervention with drug-eluting stent placement to proximal LAD. Hemostasis achieved with Angioseal device.\.br\ESTIMATED BLOOD LOSS: 50 mL\.br\COMPLICATIONS: None||||||F
```

## 13. MDM^T02 - Discharge summary at Mercy Health St. Vincent

```
MSH|^~\&|RHAP_ENGINE|MERCY_TRANS|MERCY_STVINCENT|MERCY_STVINCENT|20260509170000||MDM^T02^MDM_T02|RHP00013|P|2.5.1
EVN|T02|20260509170000
PID|1||MRN90010004^^^MERCY_TOLEDO^MR||Kowalczyk^Brian^Joseph^^Mr.||19750830|M||2106-3^White^HL70005|3827 Secor Rd^^Toledo^OH^43623||^PRN^PH^^1^419^5547183
PV1||I|CCU^CCU02^01^MERCY_STVINCENT^^^^Coronary Care||||5678901^Vasquez^Elena^R^^^MD
TXA|1|DS^Discharge Summary^HL70270|TX^Text^HL70191|20260509150000|5678901^Vasquez^Elena^R^^^MD|20260509170000||||||DOC90040002||AU^Authenticated^HL70271|||LA^Legally Authenticated^HL70271
OBX|1|TX|28570-0^Discharge Summary Note^LN||DISCHARGE SUMMARY\.br\Patient: Kowalczyk, Brian J\.br\Admission Date: 05/08/2026\.br\Discharge Date: 05/09/2026\.br\\.br\PRINCIPAL DIAGNOSIS: Acute ST-elevation myocardial infarction (I21.09)\.br\\.br\HOSPITAL COURSE: Patient presented to ED with acute chest pain and ST elevation in leads V1-V4. Emergent cardiac catheterization revealed 95% occlusion of proximal LAD. Successful PCI with drug-eluting stent placement. Post-procedure course uncomplicated.\.br\\.br\DISCHARGE MEDICATIONS: Aspirin 81mg daily, Clopidogrel 75mg daily, Atorvastatin 80mg nightly, Metoprolol succinate 50mg daily, Lisinopril 10mg daily\.br\FOLLOW-UP: Cardiology clinic 2 weeks||||||F
```

## 14. SIU^S12 - New appointment at Cincinnati Children's Hospital

```
MSH|^~\&|RHAPSODY|CCHMC_SCHED|SCHED_SYS|CCHMC_COLUMBUS|20260509103000||SIU^S12^SIU_S12|RHP00014|P|2.5.1
SCH|APT2026050901|APT2026050901||||ROUTINE^Routine^HL70276|PEDS_NEURO^Pediatric Neurology^APPTTYPE|||||45|min|^^^20260520100000^20260520104500|||||2345670^Kwan^Michelle^L^^^MD|||||BOOKED
PID|1||MRN90010010^^^CCHMC^MR||Townsend^Aria^Elise^^||20180622|F||2106-3^White^HL70005|6350 Plainfield Rd^^Cincinnati^OH^45236||^PRN^PH^^1^513^5520347
NK1|1|Townsend^Brittany^Marie|MTH^Mother^HL70063|6350 Plainfield Rd^^Cincinnati^OH^45236|^PRN^PH^^1^513^5520347
PV1||O|NEURO^NR04^01^CCHMC_COLUMBUS^^^^Pediatric Neurology||||2345670^Kwan^Michelle^L^^^MD
RGS|1
AIS|1||PEDSNEURO^Pediatric Neurology Consult^L|20260520100000|||45|min
AIP|1||2345670^Kwan^Michelle^L^^^MD|||||20260520100000|||45|min
```

## 15. SIU^S12 - Follow-up appointment at Summa Health Akron

```
MSH|^~\&|RHAP_ENGINE|SUMMA_SCHED|SCHED_SYS|SUMMA_AKRON|20260509111500||SIU^S12^SIU_S12|RHP00015|P|2.5.1
SCH|APT2026050902|APT2026050902||||FOLLOWUP^Follow-Up^HL70276|ORTHO^Orthopedic Follow-Up^APPTTYPE|||||30|min|^^^20260523140000^20260523143000|||||3456701^Fitzgerald^Alan^R^^^MD|||||BOOKED
PID|1||MRN90010011^^^SUMMA^MR||Hostetler^Craig^Allen^^Mr.||19770115|M||2106-3^White^HL70005|890 Grant St^^Akron^OH^44311||^PRN^PH^^1^330^5524617
PV1||O|ORTHO^OR02^01^SUMMA_AKRON^^^^Orthopedics||||3456701^Fitzgerald^Alan^R^^^MD
RGS|1
AIS|1||ORTHOFU^Orthopedic Follow-Up^L|20260523140000|||30|min
AIP|1||3456701^Fitzgerald^Alan^R^^^MD|||||20260523140000|||30|min
```

## 16. ACK - Positive acknowledgment from OhioHealth lab system

```
MSH|^~\&|OHIOHLTH_LAB|OHIOHLTH_LAB|RHAP_ENGINE|OHIOHLTH_RIVERSIDE|20260509080030||ACK^O01^ACK|RHP00016|P|2.5.1
MSA|AA|RHP00006|Message accepted successfully
```

## 17. ACK - Application error from Kettering radiology

```
MSH|^~\&|KETTERING_RAD|KETTERING_RAD|RHAPSODY|KETTERING_MAIN|20260509093500||ACK^O01^ACK|RHP00017|P|2.5.1
MSA|AE|RHP00007|Patient MRN not found in radiology system
ERR||PID^1^3|204^Unknown key identifier^HL70357|E||||Patient identifier MRN90010007 does not match any record in KETTERING_RAD
```

## 18. ORU^R01 - Lipid panel results from LabCorp at ProMedica

```
MSH|^~\&|RHAPSODY|LABCORP_OH|PROMEDICA_TOL|PROMEDICA_TOL|20260509143000||ORU^R01^ORU_R01|RHP00018|P|2.5.1
PID|1||MRN90010005^^^PROMEDICA^MR||Nguyen^Mai^Hanh^^Mrs.||19810312|F||2028-9^Asian^HL70005|2204 Albon Rd^^Maumee^OH^43537||^PRN^PH^^1^419^5516294
ORC|RE|LBC90030004||||||^^^20260509080000^^R||20260509143000|LAB104^Coleman^Travis||6789012^Callahan^Mark^E^^^MD
OBR|1|LBC90030004||80061^Lipid Panel^CPT|||20260509080000|||||||20260509090000|B^Blood|6789012^Callahan^Mark^E^^^MD||||||20260509143000|||F
OBX|1|NM|2093-3^Total Cholesterol^LN||234|mg/dL|<200|H|||F|||20260509142000
OBX|2|NM|2571-8^Triglycerides^LN||178|mg/dL|<150|H|||F|||20260509142000
OBX|3|NM|2085-9^HDL Cholesterol^LN||52|mg/dL|>40|N|||F|||20260509142000
OBX|4|NM|13457-7^LDL Cholesterol Calc^LN||146|mg/dL|<100|H|||F|||20260509142000
OBX|5|NM|13458-5^VLDL Cholesterol Calc^LN||36|mg/dL|5-40|N|||F|||20260509142000
```

## 19. ORU^R01 - Drug screen results at Ohio State Wexner Medical Center

```
MSH|^~\&|RHAP_ENGINE|OSUWMC_LAB|OSUWMC_COLUMBUS|OSUWMC_COLUMBUS|20260509152000||ORU^R01^ORU_R01|RHP00019|P|2.5.1
PID|1||MRN90010012^^^OSUWMC^MR||Brooks^Terrence^Darnell^^Mr.||19880704|M||2054-5^Black or African American^HL70005|1482 Grandview Ave^^Columbus^OH^43212||^PRN^PH^^1^614^5537261
PV1||E|ED^ED11^01^OSUWMC_COLUMBUS^^^^Emergency||||4567802^Tanaka^Allison^K^^^MD
ORC|RE|OSU90030005||||||^^^20260509120000^^R||20260509152000|LAB105^Petrov^Anna||4567802^Tanaka^Allison^K^^^MD
OBR|1|OSU90030005||80307^Drug Test Panel^CPT|||20260509120000|||||||20260509123000|U^Urine|4567802^Tanaka^Allison^K^^^MD||||||20260509152000|||F
OBX|1|ST|19295-5^Amphetamines Screen^LN||Negative||Negative||||F|||20260509151000
OBX|2|ST|19270-8^Barbiturates Screen^LN||Negative||Negative||||F|||20260509151000
OBX|3|ST|19288-0^Benzodiazepines Screen^LN||Negative||Negative||||F|||20260509151000
OBX|4|ST|3397-7^Cocaine Metabolites Screen^LN||Negative||Negative||||F|||20260509151000
OBX|5|ST|19295-5^Opiates Screen^LN||Positive||Negative|A|||F|||20260509151000
OBX|6|ST|18282-4^THC Screen^LN||Negative||Negative||||F|||20260509151000
```

## 20. ORM^O01 - Surgical order from University Hospitals Cleveland

```
MSH|^~\&|RHAPSODY|UH_CLEVELAND|SURGERY_SYS|UH_SURGERY|20260509083000||ORM^O01^ORM_O01|RHP00020|P|2.5.1
PID|1||MRN90010008^^^UH_CLEVELAND^MR||Dalton^Marcus^Ray^^Mr.||19610320|M||2106-3^White^HL70005|4215 Wallings Rd^^Brecksville^OH^44141||^PRN^PH^^1^216^5538207
PV1||I|7NORTH^7N05^01^UH_CLEVELAND^^^^7 North Oncology||||9012345^Rosario^Claudia^H^^^MD
ORC|NW|ORD90020005|||||^^^20260509083000^^R||20260509083000|NURSE301^Hargrove^Denise||9012345^Rosario^Claudia^H^^^MD|7NORTH
OBR|1|ORD90020005||44140^Sigmoid Colectomy^CPT|||20260509083000||||A|||ROUTINE^Routine^HL70078||9012345^Rosario^Claudia^H^^^MD||||||20260509083000|||F
DG1|1||D12.5^Benign neoplasm of sigmoid colon^I10||20260508|A
```
