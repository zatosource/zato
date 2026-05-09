# Epic (EpicCare) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to cardiology unit

```
MSH|^~\&|EPIC|BSWMC^2.16.840.1.113883.3.787^ISO|ADT_RECV|TX_HIE|20260415093012||ADT^A01^ADT_A01|MSG20260415093012001|P|2.5.1|||AL|NE
EVN|A01|20260415092500|||GALLAGHER^Gallagher^Fiona^R^^^MD|20260415092500
PID|1||MRN10234567^^^BSWMC^MR~471-38-9206^^^USSSA^SS||Sepulveda^Graciela^Yolanda^^Mrs.^||19780514|F||2106-3^White^CDCREC|4521 Bluebonnet Ln^^Dallas^TX^75201^US^H||^PRN^PH^^1^214^5559823|^WPN^PH^^1^214^5550142||M^Married^HL70002|||471-38-9206|||H^Hispanic or Latino^CDCREC
PD1|||Baylor Scott and White Medical Center^^^^NPI|1234567890^Fitzgerald^Owen^A^^^MD^^^^NPI
NK1|1|Sepulveda^Marco^Renaldo^^Mr.|SPO^Spouse^HL70063|4521 Bluebonnet Ln^^Dallas^TX^75201^US|^PRN^PH^^1^214^5559824||EC^Emergency Contact^HL70131
PV1|1|I|CARD^4102^01^BSWMC^^^^N|E^Emergency^HL70007|||9876543210^Drummond^Cedric^K^^^MD^^^^NPI^L^^^EI|5432109876^Whitmore^Leslie^M^^^MD^^^^NPI|CAR^Cardiology^HL70069||||||A^Accident^HL70007|||||VN20260415001^^^BSWMC^VN|||||||||||||||||||||||||20260415092500
PV2|||^Chest pain with shortness of breath||||||20260415|3||||||||||||N
DG1|1||I25.10^Atherosclerotic heart disease of native coronary artery without angina pectoris^I10||20260415|A
GT1|1||Sepulveda^Graciela^Yolanda^^Mrs.||4521 Bluebonnet Ln^^Dallas^TX^75201^US|^PRN^PH^^1^214^5559823|||||SE^Self^HL70063||||||||||||||||||||||||||||||||12345678
IN1|1|BCBS001|60054^Blue Cross Blue Shield of Texas|BCBSTX^^Dallas^TX^75201|||||GRP123456||||||Sepulveda^Graciela^Yolanda|SE^Self^HL70063|19780514|4521 Bluebonnet Ln^^Dallas^TX^75201^US|Y||1||||||||||||||POL998877
```

---

## 2. ADT^A03 - Patient discharge from orthopedic surgery

```
MSH|^~\&|EPIC|UTSW^2.16.840.1.113883.3.8765^ISO|ADT_RECV|TX_HIE|20260418141530||ADT^A03^ADT_A03|MSG20260418141530002|P|2.5.1|||AL|NE
EVN|A03|20260418141000|||ANSWORTH^Answorth^Colleen^L^^^MD|20260418141000
PID|1||MRN20345678^^^UTSW^MR||Mukherjee^Debashis^Arjun^^Mr.^||19650923|M||2028-9^Asian^CDCREC|8712 Preston Rd^^Dallas^TX^75225^US^H||^PRN^PH^^1^469^5553847|||S^Single^HL70002|||632-47-8195|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|ORTH^3201^02^UTSW^^^^N|U^Urgent^HL70007|||2345678901^Blackburn^Howard^F^^^MD^^^^NPI|3456789012^Calderwood^Helen^J^^^MD^^^^NPI|ORT^Orthopedics^HL70069||||||R^Referral^HL70007|||||VN20260414002^^^UTSW^VN|||||||||||||||||||01^Discharged to home^HL70112||||20260414110000|20260418141000
PV2|||^Right total knee arthroplasty recovery
DG1|1||M17.11^Primary osteoarthritis right knee^I10||20260414|A
DG1|2||Z96.651^Presence of right artificial knee joint^I10||20260414|A
PR1|1||27447^Total knee replacement right^CPT4|^Right total knee arthroplasty|20260414130000|||||2345678901^Blackburn^Howard^F^^^MD^^^^NPI
```

---

## 3. ORU^R01 - Complete blood count with differential results

```
MSH|^~\&|EPIC|MHH^2.16.840.1.113883.3.4422^ISO|LAB_RECV|TX_HIE|20260420083045||ORU^R01^ORU_R01|MSG20260420083045003|P|2.5.1|||AL|NE
PID|1||MRN30456789^^^MHH^MR||Lattimore^Shavonne^Denise^^Ms.^||19900217|F||2054-5^Black or African American^CDCREC|1503 Westheimer Rd^^Houston^TX^77006^US^H||^PRN^PH^^1^713^5557261|||M^Married^HL70002|||518-73-2640|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|LAB^0001^01^MHH^^^^N|R^Routine^HL70007|||4567890123^Hargrave^Linh^H^^^MD^^^^NPI||HEM^Hematology^HL70069||||||||||VN20260420003^^^MHH^VN
ORC|RE|ORD40001^EPIC|FIL40001^LAB||CM^Complete^HL70038|||20260420070000|||4567890123^Hargrave^Linh^H^^^MD^^^^NPI
OBR|1|ORD40001^EPIC|FIL40001^LAB|58410-2^CBC with differential^LN|||20260420070000|||||||||4567890123^Hargrave^Linh^H^^^MD^^^^NPI||||||20260420082000|||F
OBX|1|NM|6690-2^Leukocytes [#/volume] in Blood^LN||7.2|10*3/uL^thousand per microliter^UCUM|4.5-11.0|N|||F|||20260420082000
OBX|2|NM|789-8^Erythrocytes [#/volume] in Blood^LN||4.65|10*6/uL^million per microliter^UCUM|4.00-5.50|N|||F|||20260420082000
OBX|3|NM|718-7^Hemoglobin [Mass/volume] in Blood^LN||13.8|g/dL^grams per deciliter^UCUM|12.0-16.0|N|||F|||20260420082000
OBX|4|NM|4544-3^Hematocrit [Volume Fraction] of Blood^LN||41.2|%^percent^UCUM|36.0-46.0|N|||F|||20260420082000
OBX|5|NM|787-2^MCV [Entitic volume]^LN||88.6|fL^femtoliter^UCUM|80.0-100.0|N|||F|||20260420082000
OBX|6|NM|785-6^MCH [Entitic mass]^LN||29.7|pg^picogram^UCUM|27.0-33.0|N|||F|||20260420082000
OBX|7|NM|786-4^MCHC [Mass/volume]^LN||33.5|g/dL^grams per deciliter^UCUM|32.0-36.0|N|||F|||20260420082000
OBX|8|NM|777-3^Platelets [#/volume] in Blood^LN||245|10*3/uL^thousand per microliter^UCUM|150-400|N|||F|||20260420082000
OBX|9|NM|770-8^Neutrophils/100 leukocytes in Blood^LN||58.3|%^percent^UCUM|40.0-70.0|N|||F|||20260420082000
OBX|10|NM|736-9^Lymphocytes/100 leukocytes in Blood^LN||30.1|%^percent^UCUM|20.0-40.0|N|||F|||20260420082000
OBX|11|NM|5905-5^Monocytes/100 leukocytes in Blood^LN||7.4|%^percent^UCUM|2.0-8.0|N|||F|||20260420082000
```

---

## 4. ORM^O01 - CT abdomen with contrast order

```
MSH|^~\&|EPIC|BSWMC^2.16.840.1.113883.3.787^ISO|RAD_RECV|TX_HIE|20260421101500||ORM^O01^ORM_O01|MSG20260421101500004|P|2.5.1|||AL|NE
PID|1||MRN40567890^^^BSWMC^MR||Balderas^Hector^Ernesto^^Mr.^||19820730|M||2106-3^White^CDCREC|2908 Swiss Ave^^Dallas^TX^75204^US^H||^PRN^PH^^1^214^5558193|||M^Married^HL70002|||743-26-8051|||H^Hispanic or Latino^CDCREC
PV1|1|O|RAD^0012^01^BSWMC^^^^N|R^Routine^HL70007|||5678901234^Pemberton^Elena^C^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260421004^^^BSWMC^VN
ORC|NW|ORD50001^EPIC||GRP50001^EPIC|||||20260421100000|||5678901234^Pemberton^Elena^C^^^MD^^^^NPI|||||BSWMC^Baylor Scott and White Medical Center
OBR|1|ORD50001^EPIC||74178^CT abdomen and pelvis with contrast^CPT4|||20260421100000||||||||5678901234^Pemberton^Elena^C^^^MD^^^^NPI||||||||||1^Routine^HL70065
DG1|1||R10.9^Unspecified abdominal pain^I10||20260421|A
NTE|1||Patient reports persistent right lower quadrant pain for 3 days. Rule out appendicitis.
```

---

## 5. ORU^R01 - Pathology report with embedded PDF (ED datatype)

```
MSH|^~\&|EPIC|UTSW^2.16.840.1.113883.3.8765^ISO|PATH_RECV|TX_HIE|20260422160030||ORU^R01^ORU_R01|MSG20260422160030005|P|2.5.1|||AL|NE
PID|1||MRN50678901^^^UTSW^MR||Banerjee^Aditi^Meera^^Ms.^||19730412|F||2028-9^Asian^CDCREC|6201 Harry Hines Blvd^^Dallas^TX^75235^US^H||^PRN^PH^^1^214^5554082|||S^Single^HL70002|||284-59-7103|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|PATH^0005^01^UTSW^^^^N|R^Routine^HL70007|||6789012345^Ashford^Rajiv^K^^^MD^^^^NPI||PAT^Pathology^HL70069||||||||||VN20260422005^^^UTSW^VN
ORC|RE|ORD60001^EPIC|FIL60001^PATH||CM^Complete^HL70038|||20260422120000|||6789012345^Ashford^Rajiv^K^^^MD^^^^NPI
OBR|1|ORD60001^EPIC|FIL60001^PATH|88305^Surgical pathology^CPT4|||20260420090000|||||||||6789012345^Ashford^Rajiv^K^^^MD^^^^NPI||||||20260422155000|||F
OBX|1|ED|PDF^Pathology Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKFBhdGhvbG9neSBSZXBvcnQpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmIAo=||||||F|||20260422155000
OBX|2|FT|22634-0^Pathology report final diagnosis^LN||Specimen: Left breast, excisional biopsy\.br\Diagnosis: Fibroadenoma, benign\.br\Margins: Negative for malignancy\.br\Comment: No evidence of atypia or carcinoma||||||F|||20260422155000
```

---

## 6. ADT^A08 - Patient information update

```
MSH|^~\&|EPIC|MHH^2.16.840.1.113883.3.4422^ISO|ADT_RECV|TX_HIE|20260423110000||ADT^A08^ADT_A01|MSG20260423110000006|P|2.5.1|||AL|NE
EVN|A08|20260423105500|||WAVERLY^Waverly^Corinne^A^^^RN|20260423105500
PID|1||MRN60789012^^^MHH^MR||Quarles^Terrence^Donovan^^Mr.^||19550812|M||2054-5^Black or African American^CDCREC|9422 Main St^^Houston^TX^77030^US^H||^PRN^PH^^1^713^5551894|^WPN^PH^^1^713^5557743||M^Married^HL70002|||360-14-8729|||N^Not Hispanic or Latino^CDCREC
PD1|||Memorial Hermann Hospital^^^^NPI|7890123456^Kensington^Patricia^L^^^MD^^^^NPI
NK1|1|Quarles^Lucille^Yvette^^Mrs.|SPO^Spouse^HL70063|9422 Main St^^Houston^TX^77030^US|^PRN^PH^^1^713^5551895||EC^Emergency Contact^HL70131
PV1|1|I|MED^2304^01^MHH^^^^N|E^Emergency^HL70007|||7890123456^Kensington^Patricia^L^^^MD^^^^NPI||MED^Medicine^HL70069||||||||||VN20260420006^^^MHH^VN|||||||||||||||||||||||||||20260420163000
IN1|1|MCARE001|00451^Medicare|Centers for Medicare^^Baltimore^MD^21244|||||MCAREGRP||||||Quarles^Terrence^Donovan|SE^Self^HL70063|19550812|9422 Main St^^Houston^TX^77030^US|Y||1||||||||||||||MCAREPOL123456
IN2|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||Quarles^Terrence^Donovan
```

---

## 7. SIU^S12 - Appointment scheduling for MRI

```
MSH|^~\&|EPIC|BSWMC^2.16.840.1.113883.3.787^ISO|SCHED_RECV|TX_HIE|20260424091000||SIU^S12^SIU_S12|MSG20260424091000007|P|2.5.1|||AL|NE
SCH|APPT70001^EPIC||||||MRI^MRI Brain with contrast^L|30^MIN|MIN^Minutes^ISO+|^^^20260428140000^^30^MIN|||||8901234567^Forsythe^Terence^T^^^MD^^^^NPI|^PRN^PH^^1^214^5553210|||||8901234567^Forsythe^Terence^T^^^MD^^^^NPI|||||Booked
PID|1||MRN70890123^^^BSWMC^MR||Pennington^Brooke^Elaine^^Ms.^||19880605|F||2106-3^White^CDCREC|3315 Oak Lawn Ave^^Dallas^TX^75219^US^H||^PRN^PH^^1^214^5559471|||S^Single^HL70002|||805-42-6137|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^MRI1^01^BSWMC^^^^N|R^Routine^HL70007|||8901234567^Forsythe^Terence^T^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260424007^^^BSWMC^VN
RGS|1||RAD_MRI
AIS|1||70553^MRI Brain with and without contrast^CPT4|20260428140000|||30^MIN|MIN^Minutes^ISO+||Confirmed
AIG|1||8901234567^Forsythe^Terence^T^^^MD^^^^NPI|||||20260428140000|||30^MIN
AIL|1||RAD^MRI1^01^BSWMC|||||20260428140000|||30^MIN
NTE|1||Patient has history of migraines. No contrast allergy reported.
```

---

## 8. RDE^O11 - Pharmacy order for metformin

```
MSH|^~\&|EPIC|UTSW^2.16.840.1.113883.3.8765^ISO|PHARM_RECV|TX_HIE|20260425143000||RDE^O11^RDE_O11|MSG20260425143000008|P|2.5.1|||AL|NE
PID|1||MRN80901234^^^UTSW^MR||Renteria^Catalina^Ximena^^Mrs.^||19690318|F||2106-3^White^CDCREC|7701 Forest Ln^^Dallas^TX^75230^US^H||^PRN^PH^^1^469^5558342|||M^Married^HL70002|||917-62-3084|||H^Hispanic or Latino^CDCREC
PV1|1|O|ENDO^0003^01^UTSW^^^^N|R^Routine^HL70007|||9012345678^Hargrove^Diego^R^^^MD^^^^NPI||END^Endocrinology^HL70069||||||||||VN20260425008^^^UTSW^VN
ORC|NW|ORD80001^EPIC||GRP80001^EPIC|||||20260425142000|||9012345678^Hargrove^Diego^R^^^MD^^^^NPI
RXE|1^BID^HL70335|6809^Metformin 500mg tablet^NDC|500|500|mg^milligrams^ISO+|TAB^Tablet^HL70292|||||30|EA^each^ISO+||9012345678^Hargrove^Diego^R^^^MD^^^^NPI|||||||||||||2^Refills
RXR|PO^Oral^HL70162
DG1|1||E11.9^Type 2 diabetes mellitus without complications^I10||20260425|A
```

---

## 9. MDM^T02 - Transcribed discharge summary document

```
MSH|^~\&|EPIC|MHH^2.16.840.1.113883.3.4422^ISO|DOC_RECV|TX_HIE|20260426170000||MDM^T02^MDM_T02|MSG20260426170000009|P|2.5.1|||AL|NE
EVN|T02|20260426165500
PID|1||MRN91012345^^^MHH^MR||Hollingsworth^Gerald^Raymond^^Mr.^||19470929|M||2106-3^White^CDCREC|1214 Montrose Blvd^^Houston^TX^77019^US^H||^PRN^PH^^1^713^5556734|||W^Widowed^HL70002|||592-41-7836|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|CARD^5108^01^MHH^^^^N|E^Emergency^HL70007|||0123456789^Maitland^Carmen^A^^^MD^^^^NPI||CAR^Cardiology^HL70069||||||||||VN20260422009^^^MHH^VN|||||||||||||||||||||||||||20260422083000|20260426160000
TXA|1|DS^Discharge Summary^HL70270|TX^Text^HL70191||20260426165000||||||DOC9001^MHH|||||AU^Authenticated^HL70271
OBX|1|TX|11490-0^Discharge summarization note^LN||DISCHARGE SUMMARY\.br\Patient: Hollingsworth, Gerald Raymond\.br\DOB: 09/29/1947\.br\Admission: 04/22/2026\.br\Discharge: 04/26/2026\.br\\.br\PRINCIPAL DIAGNOSIS: Acute myocardial infarction, STEMI, LAD\.br\\.br\HOSPITAL COURSE:\.br\Patient presented to ED with acute substernal chest pain. ECG showed ST elevation in leads V1-V4. Emergent cardiac catheterization revealed 95% LAD stenosis. PCI performed with drug-eluting stent placement. Post-procedure course uncomplicated.\.br\\.br\MEDICATIONS AT DISCHARGE:\.br\1. Aspirin 81mg daily\.br\2. Clopidogrel 75mg daily\.br\3. Atorvastatin 80mg daily\.br\4. Metoprolol succinate 50mg daily\.br\5. Lisinopril 10mg daily\.br\\.br\FOLLOW-UP: Cardiology clinic in 2 weeks.||||||F|||20260426165000
```

---

## 10. DFT^P03 - Emergency department charge posting

```
MSH|^~\&|EPIC|BSWMC^2.16.840.1.113883.3.787^ISO|FIN_RECV|TX_HIE|20260427080000||DFT^P03^DFT_P03|MSG20260427080000010|P|2.5.1|||AL|NE
EVN|P03|20260427075500
PID|1||MRN01123456^^^BSWMC^MR||Trang^Mai^Phuong^^Ms.^||19950114|F||2028-9^Asian^CDCREC|5602 Greenville Ave^^Dallas^TX^75206^US^H||^PRN^PH^^1^469^5551237|||S^Single^HL70002|||426-83-1957|||N^Not Hispanic or Latino^CDCREC
PV1|1|E|ED^0001^T3^BSWMC^^^^N|E^Emergency^HL70007|||1234509876^Stratton^David^W^^^MD^^^^NPI||EM^Emergency Medicine^HL70069||||||||||VN20260426010^^^BSWMC^VN|||||||||||||||||||||||||||20260426221500|20260427040000
FT1|1|||20260426221500|20260427040000|CG^Charge^HL70017|99285^ED visit level 5^CPT4||1|||||||ED^0001^T3^BSWMC|||||1234509876^Stratton^David^W^^^MD^^^^NPI
FT1|2|||20260426230000|20260426230000|CG^Charge^HL70017|71046^Chest X-ray 2 views^CPT4||1|||||||RAD^0001^01^BSWMC
FT1|3|||20260426233000|20260426233000|CG^Charge^HL70017|93010^ECG interpretation^CPT4||1|||||||ED^0001^T3^BSWMC
FT1|4|||20260427010000|20260427010000|CG^Charge^HL70017|36556^Central venous catheter insertion^CPT4||1|||||||ED^0001^T3^BSWMC
DG1|1||J18.9^Pneumonia unspecified organism^I10||20260426|A
DG1|2||J96.01^Acute respiratory failure with hypoxia^I10||20260426|A
```

---

## 11. VXU^V04 - Childhood immunization administration

```
MSH|^~\&|EPIC|UTSW^2.16.840.1.113883.3.8765^ISO|IMMTRAC2|TX_DSHS|20260428103000||VXU^V04^VXU_V04|MSG20260428103000011|P|2.5.1|||ER|AL
PID|1||MRN11234567^^^UTSW^MR||Ishikawa^Kenji^Takeshi^^Master^||20240215|M||2028-9^Asian^CDCREC|4801 Harry Hines Blvd^^Dallas^TX^75235^US^H||^PRN^PH^^1^214^5553890|||S^Single^HL70002||||||N^Not Hispanic or Latino^CDCREC
PD1||||2345670987^Merriweather^Sarah^E^^^MD^^^^NPI
NK1|1|Ishikawa^Yumiko^Harumi^^Mrs.|MTH^Mother^HL70063|4801 Harry Hines Blvd^^Dallas^TX^75235^US|^PRN^PH^^1^214^5553890||EC^Emergency Contact^HL70131
PV1|1|O|PED^0002^01^UTSW^^^^N|R^Routine^HL70007|||2345670987^Merriweather^Sarah^E^^^MD^^^^NPI||PED^Pediatrics^HL70069||||||||||VN20260428011^^^UTSW^VN
ORC|RE|ORD11001^EPIC||GRP11001^EPIC|CM^Complete^HL70038|||20260428102000|||2345670987^Merriweather^Sarah^E^^^MD^^^^NPI
RXA|0|1|20260428102000||141^Influenza injectable preservative free^CVX|0.25|mL^milliliters^ISO+||00^New immunization record^NIP001||||||49281-0421-10^^NDC|||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible Medicaid/Medicaid Managed Care^HL70064||||||F
OBX|2|TS|29768-9^Date vaccine information statement published^LN||20230810||||||F
OBX|3|TS|29769-7^Date vaccine information statement presented^LN||20260428||||||F
```

---

## 12. ADT^A04 - Emergency department registration

```
MSH|^~\&|EPIC|MHH^2.16.840.1.113883.3.4422^ISO|ADT_RECV|TX_HIE|20260429020000||ADT^A04^ADT_A01|MSG20260429020000012|P|2.5.1|||AL|NE
EVN|A04|20260429015500|||LOCKWOOD^Lockwood^Rosa^M^^^RN|20260429015500
PID|1||MRN12345678^^^MHH^MR||Spearman^Devonte^Lamar^^Mr.^||20000601|M||2054-5^Black or African American^CDCREC|3818 Almeda Rd^^Houston^TX^77004^US^H||^PRN^PH^^1^832^5559012|||S^Single^HL70002|||738-21-4056|||N^Not Hispanic or Latino^CDCREC
NK1|1|Spearman^Nadine^Celeste^^Mrs.|MTH^Mother^HL70063|3818 Almeda Rd^^Houston^TX^77004^US|^PRN^PH^^1^832^5559013||EC^Emergency Contact^HL70131
PV1|1|E|ED^0001^T8^MHH^^^^N|E^Emergency^HL70007|||3456780123^Endicott^Chijioke^N^^^MD^^^^NPI||EM^Emergency Medicine^HL70069||||||A^Accident^HL70007|||||VN20260429012^^^MHH^VN|||||||||||||||||||||||||20260429015500
PV2|||^Right ankle injury, possible fracture|||||||||||||||||||3^Urgent^HL70217
DG1|1||S82.891A^Other fracture of right lower leg initial encounter^I10||20260429|A
```

---

## 13. ADT^A28 - Add person information (new patient registration)

```
MSH|^~\&|EPIC|BSWMC^2.16.840.1.113883.3.787^ISO|MPI_RECV|TX_HIE|20260429140000||ADT^A28^ADT_A05|MSG20260429140000013|P|2.5.1|||AL|NE
EVN|A28|20260429135500
PID|1||MRN13456789^^^BSWMC^MR~653-28-9174^^^USSSA^SS||Alaniz^Veronica^Marisol^^Mrs.^||19850224|F||2106-3^White^CDCREC|1122 Elm St^^Fort Worth^TX^76102^US^H||^PRN^PH^^1^817^5554567|^WPN^PH^^1^817^5558890||M^Married^HL70002|||653-28-9174|||H^Hispanic or Latino^CDCREC
PD1|||Baylor Scott and White Fort Worth^^^^NPI|4567801234^Thornbury^Maria^L^^^MD^^^^NPI
NK1|1|Alaniz^Ignacio^Rafael^^Mr.|SPO^Spouse^HL70063|1122 Elm St^^Fort Worth^TX^76102^US|^PRN^PH^^1^817^5554568||EC^Emergency Contact^HL70131
NK1|2|Alaniz^Dolores^Consuelo^^Mrs.|MTH^Mother^HL70063|908 Magnolia Ave^^Fort Worth^TX^76104^US|^PRN^PH^^1^817^5553201||EC^Emergency Contact^HL70131
```

---

## 14. ADT^A40 - Merge patient records

```
MSH|^~\&|EPIC|UTSW^2.16.840.1.113883.3.8765^ISO|MPI_RECV|TX_HIE|20260430093000||ADT^A40^ADT_A39|MSG20260430093000014|P|2.5.1|||AL|NE
EVN|A40|20260430092500|||FAIRCHILD^Fairchild^Barbara^K^^^HIM|20260430092500
PID|1||MRN14567890^^^UTSW^MR||Buckner^Clayton^Everett^^Mr.^||19710808|M||2106-3^White^CDCREC|2501 Inwood Rd^^Dallas^TX^75235^US^H||^PRN^PH^^1^469^5553678|||D^Divorced^HL70002|||841-07-5293|||N^Not Hispanic or Latino^CDCREC
MRG|MRN14567891^^^UTSW^MR||||||Buckner^Clayton^E
```

---

## 15. ORU^R01 - Radiology report with embedded PDF (ED datatype)

```
MSH|^~\&|EPIC|MHH^2.16.840.1.113883.3.4422^ISO|RAD_RECV|TX_HIE|20260501091500||ORU^R01^ORU_R01|MSG20260501091500015|P|2.5.1|||AL|NE
PID|1||MRN15678901^^^MHH^MR||Lim^Soo-Yeon^Grace^^Ms.^||19810320|F||2028-9^Asian^CDCREC|5023 Bellaire Blvd^^Houston^TX^77401^US^H||^PRN^PH^^1^713^5554938|||M^Married^HL70002|||193-76-4028|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^CT01^01^MHH^^^^N|R^Routine^HL70007|||5670123456^Standridge^Arun^S^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260501015^^^MHH^VN
ORC|RE|ORD15001^EPIC|FIL15001^RAD||CM^Complete^HL70038|||20260430160000|||5670123456^Standridge^Arun^S^^^MD^^^^NPI
OBR|1|ORD15001^EPIC|FIL15001^RAD|71260^CT chest with contrast^CPT4|||20260430160000|||||||||5670123456^Standridge^Arun^S^^^MD^^^^NPI||||||20260501090000|||F
OBX|1|TX|36643-5^Chest CT impression^LN||IMPRESSION:\.br\1. No pulmonary embolism identified.\.br\2. Small bilateral pleural effusions.\.br\3. Subcentimeter mediastinal lymph nodes, likely reactive.\.br\4. No suspicious pulmonary nodules.||||||F|||20260501090000
OBX|2|ED|PDF^Radiology Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8Ci9NYXJrZWQgdHJ1ZQo+PgovU3RydWN0VHJlZVJvb3QgMyAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFs0IDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1N0cnVjdFRyZWVSb290Ci9LIFtdCi9QYXJlbnRUcmVlIDUgMCBSCj4+CmVuZG9iago0IDAgb2JqCjw8Ci9UeXBlIC9QYWdlCi9QYXJlbnQgMiAwIFIKL0NvbnRlbnRzIDYgMCBSCi9SZXNvdXJjZXMgPDwKL0ZvbnQgPDwKL0YxIDcgMCBSCj4+Cj4+Cj4+CmVuZG9iago=||||||F|||20260501090000
```

---

## 16. ADT^A02 - Patient transfer from ICU to step-down unit

```
MSH|^~\&|EPIC|BSWMC^2.16.840.1.113883.3.787^ISO|ADT_RECV|TX_HIE|20260501143000||ADT^A02^ADT_A02|MSG20260501143000016|P|2.5.1|||AL|NE
EVN|A02|20260501142500|||STOCKDALE^Stockdale^Brittany^L^^^RN|20260501142500
PID|1||MRN16789012^^^BSWMC^MR||Blackwell^Damien^Chukwudi^^Mr.^||19600115|M||2054-5^Black or African American^CDCREC|9210 White Rock Trail^^Dallas^TX^75238^US^H||^PRN^PH^^1^214^5552847|||M^Married^HL70002|||672-30-8491|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|SDU^2105^01^BSWMC^^^^N|U^Urgent^HL70007|||6781234567^Whitfield^Marco^J^^^MD^^^^NPI||MED^Medicine^HL70069||||||T^Transfer^HL70007|||||VN20260428016^^^BSWMC^VN
PV2|||^Post-cardiac surgery monitoring
```

---

## 17. ADT^A31 - Update person information (address change)

```
MSH|^~\&|EPIC|UTSW^2.16.840.1.113883.3.8765^ISO|MPI_RECV|TX_HIE|20260502100000||ADT^A31^ADT_A05|MSG20260502100000017|P|2.5.1|||AL|NE
EVN|A31|20260502095500
PID|1||MRN17890123^^^UTSW^MR||Ontiveros^Luciana^Pilar^^Mrs.^||19780422|F||2106-3^White^CDCREC|1850 N Beckley Ave^^Dallas^TX^75203^US^H||^PRN^PH^^1^214^5551204|^WPN^PH^^1^469^5557788||M^Married^HL70002|||514-80-3269|||H^Hispanic or Latino^CDCREC
PD1|||UT Southwestern Medical Center^^^^NPI|7892345678^Prescott^Antonio^C^^^MD^^^^NPI
```

---

## 18. MFN^M02 - Staff physician master file update

```
MSH|^~\&|EPIC|BSWMC^2.16.840.1.113883.3.787^ISO|MF_RECV|TX_HIE|20260502160000||MFN^M02^MFN_M02|MSG20260502160000018|P|2.5.1|||AL|NE
MFI|PRA^Practitioner master file^HL70175||UPD^Update^HL70180|||NE
MFE|MAD^Add record to master file^HL70180|20260502155500||8903456789^Beaumont^Patricia^Ann^^MD|CWE
STF|8903456789|U8903456789|Beaumont^Patricia^Ann^^MD||F|19750830|A^Active^HL70183|||||^WPN^PH^^1^214^5559102
PRA|8903456789^Beaumont^Patricia^Ann^^MD|BSWMC^Baylor Scott and White Medical Center|I^Institution^HL70186|||||207RC0000X^Internal Medicine Cardiovascular Disease^NUCC
```

---

## 19. ACK - Acknowledgment for accepted message

```
MSH|^~\&|ADT_RECV|TX_HIE|EPIC|BSWMC^2.16.840.1.113883.3.787^ISO|20260503080000||ACK^A01^ACK|MSG20260503080000019|P|2.5.1|||AL|NE
MSA|AA|MSG20260415093012001||0
```

---

## 20. ORM^O01 - Laboratory panel order for metabolic panel

```
MSH|^~\&|EPIC|MHH^2.16.840.1.113883.3.4422^ISO|LAB_RECV|TX_HIE|20260503110000||ORM^O01^ORM_O01|MSG20260503110000020|P|2.5.1|||AL|NE
PID|1||MRN20012345^^^MHH^MR||Summerfield^Carolyn^Renee^^Ms.^||19830927|F||2106-3^White^CDCREC|2410 Kirby Dr^^Houston^TX^77019^US^H||^PRN^PH^^1^713^5558471|||S^Single^HL70002|||247-58-9013|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|LAB^0003^01^MHH^^^^N|R^Routine^HL70007|||9014567890^Rutherford^Anthony^R^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260503020^^^MHH^VN
ORC|NW|ORD20001^EPIC||GRP20001^EPIC|||||20260503103000|||9014567890^Rutherford^Anthony^R^^^MD^^^^NPI
OBR|1|ORD20001^EPIC||80053^Comprehensive metabolic panel^CPT4|||20260503103000||||||||9014567890^Rutherford^Anthony^R^^^MD^^^^NPI||||||||||1^Routine^HL70065
DG1|1||E11.65^Type 2 diabetes mellitus with hyperglycemia^I10||20260503|A
DG1|2||I10^Essential primary hypertension^I10||20260503|A
NTE|1||Annual wellness visit. Patient fasting since midnight.
```
