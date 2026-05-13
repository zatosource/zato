# NextGen Connect (Mirth Connect) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Inpatient admission at UPMC Presbyterian

```
MSH|^~\&|MIRTH|UPMC_PRESBYTERIAN|STATEREG|PADOH|20260509083022||ADT^A01^ADT_A01|UPMC20260509083022A01|P|2.5.1|||AL|NE||UNICODE UTF-8|||2.16.840.1.113883.3.4881^ISO
EVN|A01|20260509082500|||JTHOMPSON^Thompson^Julia^A^^^RN
PID|1||MRN9928471^^^UPMC^MR~443901287^^^USSSA^SS||Wojciechowski^Irene^Catherine^^Mrs.^^L||19580314|F||2106-3^White^CDCREC|1847 Forbes Ave^^Pittsburgh^PA^15213^USA^H^^Allegheny||^PRN^PH^^^412^6823947~^PRN^CP^^^412^9157328|^WPN^PH^^^412^3825500||M^Married^HL70002|||443-90-1287||||N^Not Hispanic^HL70189||||||N
PD1||||1184790562^Kapoor^Rajesh^K^^^MD^^NPI
NK1|1|Wojciechowski^Edward^J|SPO^Spouse^HL70063|1847 Forbes Ave^^Pittsburgh^PA^15213^USA|^PRN^PH^^^412^6823947||EC^Emergency Contact^HL70131
PV1|1|I|4W^4201^01^UPMC_PRESBYTERIAN^^^^4 WEST MED SURG|E^Emergency||4W^4201^01|1427835910^Delgado^Carlos^M^^^MD^^NPI^^^^^UPMC|1184790562^Kapoor^Rajesh^K^^^MD^^NPI||MED||||7|||1427835910^Delgado^Carlos^M^^^MD^^NPI||29384710^^^UPMC^VN|||||||||||||||||||||||||20260509082500
PV2|||^Acute exacerbation of COPD||||||20260516|7
IN1|1|1|BCBSPA|Blue Cross Blue Shield of PA|||||||PPO||20260101||||Wojciechowski^Irene^Catherine|01^Self^HL70063|19580314|1847 Forbes Ave^^Pittsburgh^PA^15213^USA||||||||||||||||XGP884729105
DG1|1|I10|J44.1^Chronic obstructive pulmonary disease with acute exacerbation^I10||20260509|A
```

---

## 2. ADT^A04 - Emergency registration at Penn Medicine Lancaster General

```
MSH|^~\&|NEXTGEN_CONNECT|LGH_ED|HIE_REPOSITORY|CLINICALCONNECT|20260509101532||ADT^A04^ADT_A01|LGH2026050910153201|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A04|20260509101400|||MDIAZ^Diaz^Maria^L^^^RN
PID|1||MRN7741023^^^LGH^MR||Okafor^David^Jerome^^^^L||19910822|M||2054-5^Black or African American^CDCREC|329 N Queen St^^Lancaster^PA^17603^USA^H^^Lancaster||^PRN^CP^^^717^5529814||S^Single^HL70002|||||||N^Not Hispanic^HL70189
NK1|1|Okafor^Linda^M|MTH^Mother^HL70063|482 Marietta Ave^^Lancaster^PA^17603^USA|^PRN^PH^^^717^3928471||EC^Emergency Contact^HL70131
PV1|1|E|ED^EDBAY12^01^LGH^^^^ED MAIN|U^Urgent|||1538264097^Matsuda^William^S^^^MD^^NPI|||EM||||1|||1538264097^Matsuda^William^S^^^MD^^NPI||48291053^^^LGH^VN|||||||||||||||||||||||||20260509101400
DG1|1|I10|S52.501A^Unspecified fracture of lower end of right radius, initial encounter^I10||20260509|A
```

---

## 3. ADT^A08 - Patient information update at Geisinger Medical Center

```
MSH|^~\&|MIRTH|GEISINGER_MC|PHINMS|PADOH|20260509112045||ADT^A08^ADT_A01|GEI2026050911204501|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A08|20260509112000
PID|1||MRN3382917^^^GEISINGER^MR||Kaczmarek^Teresa^Marie^^Mrs.^^L~Nowak^Teresa^Marie^^^^M||19760519|F||2106-3^White^CDCREC|2714 Bloom Rd^^Danville^PA^17821^USA^H^^Montour~PO Box 187^^Danville^PA^17821^USA^P^^Montour||^PRN^PH^^^570^2758493~^PRN^CP^^^570^8413926|^WPN^PH^^^570^2714000||M^Married^HL70002|||189-44-7823||||N^Not Hispanic^HL70189
PD1||||1609843275^Horowitz^Brian^D^^^MD^^NPI
PV1|1|O|GIM^3012^01^GEISINGER_MC^^^^GENERAL INTERNAL MED|||||||||||||||59281034^^^GEISINGER^VN
IN1|1|1|GHPFAM|Geisinger Health Plan|||||||HMO||20250701||||Kaczmarek^Teresa^Marie|01^Self^HL70063|19760519|2714 Bloom Rd^^Danville^PA^17821^USA||||||||||||||||GHP9928471055
```

---

## 4. ORM^O01 - Radiology order from WellSpan York Hospital

```
MSH|^~\&|MIRTH|WELLSPAN_YORK|RIS|WELLSPAN_RAD|20260509130215||ORM^O01^ORM_O01|WS2026050913021501|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN6617482^^^WELLSPAN^MR||Ramirez^Carmen^Rosa^^^^L||19840723|F||2131-1^Other Race^CDCREC|508 S George St^^York^PA^17401^USA^H^^York||^PRN^CP^^^717^8493021||M^Married^HL70002|||||||H^Hispanic or Latino^HL70189
PV1|1|I|3N^3104^01^WELLSPAN_YORK^^^^3 NORTH|R|||1742938501^Flanagan^Amanda^J^^^MD^^NPI|||RAD||||7|||1742938501^Flanagan^Amanda^J^^^MD^^NPI||73829105^^^WELLSPAN^VN|||||||||||||||||||||||||20260508160000
ORC|NW|ORD88294710^MIRTH|||||^^^20260509133000^^R||20260509130200|JLEE^Lee^Jennifer^A^^^RT||1742938501^Flanagan^Amanda^J^^^MD^^NPI|3N^3104^01^WELLSPAN_YORK|^WPN^PH^^^717^8514000||||||WELLSPAN_YORK^WellSpan York Hospital^HL70362
OBR|1|ORD88294710^MIRTH||71046^Chest X-ray 2 views^CPT4|||20260509133000||||A||^^^20260509133000^^R|||||1742938501^Flanagan^Amanda^J^^^MD^^NPI||||||20260509133000|||1^^^20260509133000^^R||||||71046^Chest X-ray 2 views^CPT4
DG1|1|I10|J18.9^Pneumonia, unspecified organism^I10||20260508|A
```

---

## 5. ORU^R01 - Lab result from Quest Diagnostics routed through Mirth

```
MSH|^~\&|NEXTGEN_CONNECT|QUEST_PA|EHR_REPOSITORY|READING_HOSPITAL|20260509141022||ORU^R01^ORU_R01|QST2026050914102201|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN2294817^^^READING_HOSP^MR||Lombardi^Vincent^Anthony^^^^L||19670411|M||2106-3^White^CDCREC|1125 Perkiomen Ave^^Reading^PA^19602^USA^H^^Berks||^PRN^PH^^^610^3729184|||||||N^Not Hispanic^HL70189
PV1|1|O|LAB||||1893742056^Vasquez^Elena^R^^^MD^^NPI
ORC|RE|ORD33017284^EHR|LAB90284710^QUEST||CM||||20260509060000|||1893742056^Vasquez^Elena^R^^^MD^^NPI
OBR|1|ORD33017284^EHR|LAB90284710^QUEST|80053^Comprehensive Metabolic Panel^CPT4|||20260508143000|||||||||1893742056^Vasquez^Elena^R^^^MD^^NPI||||||20260509130000|||F
OBX|1|NM|2345-7^Glucose^LN||98|mg/dL|74-106|N|||F|||20260509130000||QUEST_PA^Quest Diagnostics^L
OBX|2|NM|3094-0^BUN^LN||22|mg/dL|6-24|N|||F|||20260509130000||QUEST_PA^Quest Diagnostics^L
OBX|3|NM|2160-0^Creatinine^LN||1.1|mg/dL|0.7-1.3|N|||F|||20260509130000||QUEST_PA^Quest Diagnostics^L
OBX|4|NM|17861-6^Calcium^LN||9.4|mg/dL|8.5-10.5|N|||F|||20260509130000||QUEST_PA^Quest Diagnostics^L
OBX|5|NM|2951-2^Sodium^LN||140|mEq/L|136-145|N|||F|||20260509130000||QUEST_PA^Quest Diagnostics^L
OBX|6|NM|2823-3^Potassium^LN||4.2|mEq/L|3.5-5.1|N|||F|||20260509130000||QUEST_PA^Quest Diagnostics^L
OBX|7|NM|2075-0^Chloride^LN||102|mEq/L|98-106|N|||F|||20260509130000||QUEST_PA^Quest Diagnostics^L
OBX|8|NM|2028-9^CO2^LN||24|mEq/L|20-29|N|||F|||20260509130000||QUEST_PA^Quest Diagnostics^L
OBX|9|NM|1742-6^ALT^LN||28|U/L|7-56|N|||F|||20260509130000||QUEST_PA^Quest Diagnostics^L
OBX|10|NM|1920-8^AST^LN||24|U/L|10-40|N|||F|||20260509130000||QUEST_PA^Quest Diagnostics^L
OBX|11|NM|1975-2^Total Bilirubin^LN||0.8|mg/dL|0.1-1.2|N|||F|||20260509130000||QUEST_PA^Quest Diagnostics^L
OBX|12|NM|2885-2^Total Protein^LN||7.1|g/dL|6.0-8.3|N|||F|||20260509130000||QUEST_PA^Quest Diagnostics^L
OBX|13|NM|1751-7^Albumin^LN||4.0|g/dL|3.5-5.5|N|||F|||20260509130000||QUEST_PA^Quest Diagnostics^L
OBX|14|NM|6768-6^Alkaline Phosphatase^LN||72|U/L|44-147|N|||F|||20260509130000||QUEST_PA^Quest Diagnostics^L
```

---

## 6. ORU^R01 - CBC result from Lehigh Valley Health Network

```
MSH|^~\&|MIRTH|LVHN_CC|HEALTHSHARE|HSX_PA|20260509093817||ORU^R01^ORU_R01|LVHN2026050909381701|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN4418293^^^LVHN^MR||Grabowski^Stanley^John^^^^L||19530228|M||2106-3^White^CDCREC|4012 Hamilton Blvd^^Allentown^PA^18103^USA^H^^Lehigh||^PRN^PH^^^610^4329187||W^Widowed^HL70002|||||||N^Not Hispanic^HL70189
PV1|1|I|5S^5208^02^LVHN_CC^^^^5 SOUTH ONCOLOGY|R|||1648293017^Anand^Priya^N^^^MD^^NPI
ORC|RE|ORD72910384^EHR|LAB44829103^LVHN||CM||||20260509060000|||1648293017^Anand^Priya^N^^^MD^^NPI
OBR|1|ORD72910384^EHR|LAB44829103^LVHN|85025^Complete Blood Count with Differential^CPT4|||20260509063000|||||||||1648293017^Anand^Priya^N^^^MD^^NPI||||||20260509091500|||F
OBX|1|NM|6690-2^WBC^LN||3.2|10*3/uL|4.5-11.0|L|||F|||20260509091500||LVHN_LAB^LVHN Core Lab^L
OBX|2|NM|789-8^RBC^LN||3.8|10*6/uL|4.5-5.5|L|||F|||20260509091500||LVHN_LAB^LVHN Core Lab^L
OBX|3|NM|718-7^Hemoglobin^LN||10.2|g/dL|13.5-17.5|L|||F|||20260509091500||LVHN_LAB^LVHN Core Lab^L
OBX|4|NM|4544-3^Hematocrit^LN||31.1|%|38.3-48.6|L|||F|||20260509091500||LVHN_LAB^LVHN Core Lab^L
OBX|5|NM|787-2^MCV^LN||81.8|fL|80.0-100.0|N|||F|||20260509091500||LVHN_LAB^LVHN Core Lab^L
OBX|6|NM|777-3^Platelet Count^LN||145|10*3/uL|150-400|L|||F|||20260509091500||LVHN_LAB^LVHN Core Lab^L
OBX|7|NM|770-8^Neutrophils %^LN||58.3|%|40.0-74.0|N|||F|||20260509091500||LVHN_LAB^LVHN Core Lab^L
OBX|8|NM|736-9^Lymphocytes %^LN||28.1|%|19.0-48.0|N|||F|||20260509091500||LVHN_LAB^LVHN Core Lab^L
```

---

## 7. ORU^R01 - Pathology result with embedded PDF from UPMC Shadyside

```
MSH|^~\&|MIRTH|UPMC_SHADYSIDE|DOCREPO|UPMC_HIE|20260509104530||ORU^R01^ORU_R01|UPMC2026050910453001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN8829471^^^UPMC^MR||Mazurek^Barbara^Marie^^Mrs.^^L||19710609|F||2106-3^White^CDCREC|5831 Walnut St^^Pittsburgh^PA^15232^USA^H^^Allegheny||^PRN^CP^^^412^7291843||M^Married^HL70002|||||||N^Not Hispanic^HL70189
PV1|1|I|SURG^6102^01^UPMC_SHADYSIDE^^^^6TH FL SURGICAL|R|||1293847561^Banerjee^Anita^R^^^MD^^NPI
ORC|RE|ORD55928471^EHR|PATH39281047^UPMC||CM||||20260507100000|||1293847561^Banerjee^Anita^R^^^MD^^NPI
OBR|1|ORD55928471^EHR|PATH39281047^UPMC|88305^Surgical Pathology^CPT4|||20260507100000|||||||||1293847561^Banerjee^Anita^R^^^MD^^NPI||||||20260509100000|||F
OBX|1|ED|60573-3^Surgical Pathology Report^LN||^application/pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyNDQgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihVUE1DIFNoYWR5c2lkZSAtIFN1cmdpY2FsIFBhdGhvbG9neSkgVGoKMCAtMjAgVGQKKFBhdGllbnQ6IEphbmtvd3NraSwgQmFyYmFyYSBNLikgVGoKMCAtMjAgVGQKKFNwZWNpbWVuOiBMZWZ0IGJyZWFzdCBsdW1wZWN0b215KSBUagowIC0yMCBUZAooRGlhZ25vc2lzOiBJbnZhc2l2ZSBkdWN0YWwgY2FyY2lub21hLCBHcmFkZSAyKSBUagowIC0yMCBUZAooTWFyZ2luczogTmVnYXRpdmUpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNjAwIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNjkzCiUlRU9GCg==||||||F|||20260509100000||1382947102^Stein^Jonathan^R^^^MD^^NPI
OBX|2|FT|22634-0^Pathology Report Narrative^LN||SURGICAL PATHOLOGY REPORT\.br\\.br\Patient: Mazurek, Barbara M\.br\DOB: 06/09/1971\.br\MRN: MRN8829471\.br\\.br\SPECIMEN: Left breast lumpectomy\.br\\.br\DIAGNOSIS: Invasive ductal carcinoma, Grade 2\.br\Tumor size: 1.4 cm\.br\Margins: Negative (closest margin 0.3 cm)\.br\Lymphovascular invasion: Not identified\.br\DCIS component: Present, solid and cribriform pattern\.br\\.br\ER: Positive (95%)\.br\PR: Positive (80%)\.br\HER2: Negative (IHC 1+)\.br\Ki-67: 18%||||||F|||20260509100000||1382947102^Stein^Jonathan^R^^^MD^^NPI
```

---

## 8. MDM^T02 - Discharge summary document from St. Luke's University Hospital

```
MSH|^~\&|MIRTH|STLUKES_BETHLEHEM|DOCMGR|STLUKES_HIE|20260509150812||MDM^T02^MDM_T02|SLU2026050915081201|P|2.5.1|||NE|AL||UNICODE UTF-8
EVN|T02|20260509150800
PID|1||MRN1129384^^^STLUKES^MR||Fuentes^Miguel^Antonio^^^^L||19830216|M||2106-3^White^CDCREC|742 Broadway^^Bethlehem^PA^18015^USA^H^^Northampton||^PRN^CP^^^610^8294713||M^Married^HL70002|||||||H^Hispanic or Latino^HL70189
PV1|1|I|CCU^2001^01^STLUKES_BETHLEHEM^^^^CARDIAC CARE UNIT|E|||1947382016^O'Donnell^Sean^P^^^MD^^NPI|||CAR||||7|||1947382016^O'Donnell^Sean^P^^^MD^^NPI||61829304^^^STLUKES^VN|||||||||||||||||||||||||20260505092000|20260509150000
TXA|1|DS^Discharge Summary^HL70270|TX|20260509143000|1947382016^O'Donnell^Sean^P^^^MD^^NPI|20260509150000|20260509150800|||||DOC8829471||||discharge_summary_fuentes.pdf|AU||AV||||||Discharge Summary - Fuentes, Miguel A
OBX|1|ED|18842-5^Discharge Summary^LN||^application/pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAzMjAgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihTdC4gTHVrZSdzIFVuaXZlcnNpdHkgSG9zcGl0YWwgLSBEaXNjaGFyZ2UgU3VtbWFyeSkgVGoKMCAtMjAgVGQKKFBhdGllbnQ6IEhlcm5hbmRleiwgTWlndWVsIEEuKSBUagowIC0yMCBUZAooQWRtaXNzaW9uOiAwNS8wNS8yMDI2ICBEaXNjaGFyZ2U6IDA1LzA5LzIwMjYpIFRqCjAgLTIwIFRkCihEaWFnbm9zaXM6IEFjdXRlIFNULWVsZXZhdGlvbiBteW9jYXJkaWFsIGluZmFyY3Rpb24pIFRqCjAgLTIwIFRkCihQcm9jZWR1cmU6IFBDSSBvZiBMQUQgd2l0aCBERVMgcGxhY2VtZW50KSBUagowIC0yMCBUZAooRGlzY2hhcmdlIHRvOiBIb21lIHdpdGggaG9tZSBoZWFsdGgpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNjc2IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNzY5CiUlRU9GCg==||||||F|||20260509150000||1947382016^O'Donnell^Sean^P^^^MD^^NPI
```

---

## 9. ACK - Positive acknowledgement from ClinicalConnect HIE

```
MSH|^~\&|CLINICALCONNECT|HSX_PA|MIRTH|UPMC_PRESBYTERIAN|20260509083025||ACK^A01^ACK|CC2026050908302501|P|2.5.1|||AL|NE||UNICODE UTF-8
MSA|AA|UPMC20260509083022A01||0
```

---

## 10. ACK - Application error acknowledgement from PA-SIIS

```
MSH|^~\&|PA_SIIS|PADOH|MIRTH|GEISINGER_MC|20260509142233||ACK^V04^ACK|SIIS2026050914223301|P|2.5.1|||AL|NE||UNICODE UTF-8
MSA|AE|GEI2026050914200001||207^Application internal error^HL70357
ERR|||207^Application internal error^HL70357|E||||Patient DOB does not match existing registry record
```

---

## 11. VXU^V04 - Immunization update to PA-SIIS from Geisinger

```
MSH|^~\&|MIRTH|GEISINGER_CLINIC|PA_SIIS|PADOH|20260509142000||VXU^V04^VXU_V04|GEI2026050914200001|P|2.5.1|||ER|AL||UNICODE UTF-8
PID|1||MRN5538291^^^GEISINGER^MR~PA7829410^^^PA_SIIS^SR||Zielinski^Anna^Lynn^^^^L||20210315|F||2106-3^White^CDCREC|89 Mill Rd^^Bloomsburg^PA^17815^USA^H^^Columbia||^PRN^CP^^^570^3849217||||||||||N^Not Hispanic^HL70189
PD1||||1609843275^Horowitz^Brian^D^^^MD^^NPI|||||||02^Reminder/recall - any method^HL70215|N
NK1|1|Zielinski^Mark^J|FTH^Father^HL70063|89 Mill Rd^^Bloomsburg^PA^17815^USA|^PRN^CP^^^570^3849218
ORC|RE|IMM39284710^MIRTH||||||||||1609843275^Horowitz^Brian^D^^^MD^^NPI||||||GEISINGER_CLINIC^Geisinger Bloomsburg Clinic^HL70362
RXA|0|1|20260509100000|20260509100000|94^MMRV^CVX|0.5|mL^Milliliter^UCUM||00^New immunization record^NIP001||||||U7382A|20271231|MSD^Merck Sharp and Dohme^MVX
RXR|SC^Subcutaneous^HL70162|RA^Right arm^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC eligible - Medicaid/Medicaid Managed Care^HL70064||||||F
OBX|2|CE|30956-7^Vaccine type^LN||94^MMRV^CVX||||||F
OBX|3|TS|29768-9^Date vaccine information statement published^LN||20100521||||||F
OBX|4|TS|29769-7^Date vaccine information statement presented^LN||20260509||||||F
```

---

## 12. VXU^V04 - COVID booster immunization from Penn Medicine

```
MSH|^~\&|NEXTGEN_CONNECT|PENNMED_HUP|PA_SIIS|PADOH|20260509110530||VXU^V04^VXU_V04|PM2026050911053001|P|2.5.1|||ER|AL||UNICODE UTF-8
PID|1||MRN9917284^^^PENNMED^MR~PA6829174^^^PA_SIIS^SR||Mabry^Denise^Renee^^^^L||19680720|F||2054-5^Black or African American^CDCREC|2934 Chestnut St^^Philadelphia^PA^19104^USA^H^^Philadelphia||^PRN^CP^^^215^8293741||S^Single^HL70002|||||||N^Not Hispanic^HL70189
PD1||||1847293056^Tanaka^David^H^^^MD^^NPI
NK1|1|Mabry^Robert^L|BRO^Brother^HL70063|3018 Market St^^Philadelphia^PA^19104^USA|^PRN^CP^^^215^7382941
ORC|RE|IMM72938401^NEXTGEN_CONNECT||||||||||1847293056^Tanaka^David^H^^^MD^^NPI||||||PENNMED_HUP^Hospital of the University of Pennsylvania^HL70362
RXA|0|1|20260509103000|20260509103000|308^COVID-19 mRNA, bivalent^CVX|0.5|mL^Milliliter^UCUM||00^New immunization record^NIP001||||||HK4829A|20261231|MOD^Moderna^MVX
RXR|IM^Intramuscular^HL70162|LA^Left arm^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V01^Not VFC eligible^HL70064||||||F
OBX|2|TS|29768-9^Date vaccine information statement published^LN||20240812||||||F
OBX|3|TS|29769-7^Date vaccine information statement presented^LN||20260509||||||F
```

---

## 13. ORM^O01 - Laboratory order from Abington-Jefferson Health

```
MSH|^~\&|MIRTH|ABINGTON_JH|LIS|ABINGTON_LAB|20260509071530||ORM^O01^ORM_O01|AJH2026050907153001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN3819274^^^ABINGTON_JH^MR||Nguyen^Susan^Wei-Lin^^^^L||19920105|F||2028-9^Asian^CDCREC|1528 Old York Rd^^Abington^PA^19001^USA^H^^Montgomery||^PRN^CP^^^267^4829137||S^Single^HL70002|||||||N^Not Hispanic^HL70189
PV1|1|O|PCP^1002^01^ABINGTON_JH^^^^PRIMARY CARE|||||||||||||||84729103^^^ABINGTON_JH^VN
ORC|NW|ORD44829301^MIRTH|||||^^^20260509080000^^R||20260509071500|RSMITH^Smith^Rachel^M^^^MA||1738294017^Gallagher^Christopher^J^^^MD^^NPI|PCP^1002^01^ABINGTON_JH||||||ABINGTON_JH^Abington Hospital - Jefferson Health^HL70362
OBR|1|ORD44829301^MIRTH||85025^Complete Blood Count with Differential^CPT4|||20260509080000||||||^^^20260509080000^^R|^^Blood|1738294017^Gallagher^Christopher^J^^^MD^^NPI||||||20260509080000|||1^^^20260509080000^^R
OBR|2|ORD44829301^MIRTH||80061^Lipid Panel^CPT4|||20260509080000||||||^^^20260509080000^^R|^^Blood|1738294017^Gallagher^Christopher^J^^^MD^^NPI||||||20260509080000|||1^^^20260509080000^^R
OBR|3|ORD44829301^MIRTH||83036^Hemoglobin A1c^CPT4|||20260509080000||||||^^^20260509080000^^R|^^Blood|1738294017^Gallagher^Christopher^J^^^MD^^NPI||||||20260509080000|||1^^^20260509080000^^R
```

---

## 14. ORU^R01 - Microbiology culture result from Hershey Medical Center

```
MSH|^~\&|MIRTH|HERSHEY_MC|HIE_FEED|P3N_REGISTRY|20260509161245||ORU^R01^ORU_R01|HMC2026050916124501|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN6129384^^^HERSHEY_MC^MR||Callahan^Robert^Earl^^Jr.^^L||19450917|M||2106-3^White^CDCREC|3201 Derry St^^Harrisburg^PA^17111^USA^H^^Dauphin||^PRN^PH^^^717^5829471||W^Widowed^HL70002|||||||N^Not Hispanic^HL70189
PV1|1|I|MED^3208^01^HERSHEY_MC^^^^3RD FL MEDICINE|R|||1829374056^Hwang^James^W^^^MD^^NPI
ORC|RE|ORD88293714^EHR|MICRO44829^HERSHEY||CM||||20260507140000|||1829374056^Hwang^James^W^^^MD^^NPI
OBR|1|ORD88293714^EHR|MICRO44829^HERSHEY|87070^Culture, Bacterial^CPT4|||20260507140000||||||^^^20260507140000^^R|^^Urine|1829374056^Hwang^James^W^^^MD^^NPI||||||20260509153000|||F
OBX|1|CE|600-7^Bacteria identified in Blood by Culture^LN||112283007^Escherichia coli^SCT||||||F|||20260509150000
OBX|2|ST|18769-0^Microbial susceptibility comment^LN||Susceptibility results follow||||||F|||20260509153000
OBX|3|ST|18907-6^Ampicillin susceptibility^LN||R||||||F|||20260509153000
OBX|4|ST|18928-2^Ciprofloxacin susceptibility^LN||S||||||F|||20260509153000
OBX|5|ST|18932-4^Ceftriaxone susceptibility^LN||S||||||F|||20260509153000
OBX|6|ST|18961-3^Nitrofurantoin susceptibility^LN||S||||||F|||20260509153000
OBX|7|ST|18993-6^Trimethoprim-Sulfamethoxazole susceptibility^LN||R||||||F|||20260509153000
```

---

## 15. ADT^A01 - Behavioral health admission at UPMC Western Psychiatric

```
MSH|^~\&|MIRTH|UPMC_WESTERN_PSYCH|ADT_FEED|UPMC_HIE|20260509191530||ADT^A01^ADT_A01|UPMCWP2026050919153001|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A01|20260509191000|||KWRIGHT^Wright^Karen^M^^^RN
PID|1||MRN7729381^^^UPMC^MR||Kovacs^Timothy^Alan^^^^L||19950810|M||2106-3^White^CDCREC|2208 Murray Ave^^Pittsburgh^PA^15217^USA^H^^Allegheny||^PRN^CP^^^412^5928174||S^Single^HL70002|||||||N^Not Hispanic^HL70189
PD1||||1748293015^Epstein^Sarah^L^^^MD^^NPI
NK1|1|Kovacs^Patricia^A|MTH^Mother^HL70063|194 Bower Hill Rd^^Pittsburgh^PA^15228^USA|^PRN^PH^^^412^3918274||EC^Emergency Contact^HL70131
PV1|1|I|PSY^BH204^01^UPMC_WESTERN_PSYCH^^^^ADULT INPATIENT PSYCH|U^Urgent|||1748293015^Epstein^Sarah^L^^^MD^^NPI|||PSY||||7|||1748293015^Epstein^Sarah^L^^^MD^^NPI||83729401^^^UPMC^VN|||||||||||||||||||||||||20260509191000
PV2|||^Major depressive disorder, severe with psychotic features
DG1|1|I10|F33.3^Major depressive disorder, recurrent, severe with psychotic symptoms^I10||20260509|A
DG1|2|I10|F10.20^Alcohol dependence, uncomplicated^I10||20260509|A
IN1|1|1|UPMC_HP|UPMC Health Plan|||||||HMO||20260101||||Kovacs^Timothy^Alan|01^Self^HL70063|19950810|2208 Murray Ave^^Pittsburgh^PA^15217^USA||||||||||||||||UPMCHP882941055
```

---

## 16. ADT^A08 - Patient update at Crozer-Chester Medical Center

```
MSH|^~\&|NEXTGEN_CONNECT|CROZER_CHESTER|HEALTHSHARE|HSX_PA|20260509134500||ADT^A08^ADT_A01|CRZ2026050913450001|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A08|20260509134400
PID|1||MRN2938471^^^CROZER^MR||Benson^Jessica^Lynn^^Ms.^^L~Patterson^Jessica^Lynn^^^^M||19880403|F||2054-5^Black or African American^CDCREC|1105 W 9th St^^Chester^PA^19013^USA^H^^Delaware~822 Providence Rd^^Media^PA^19063^USA^P^^Delaware||^PRN^CP^^^610^8294173~^PRN^PH^^^610^3281947|^WPN^PH^^^610^4472000||D^Divorced^HL70002|||||||N^Not Hispanic^HL70189
PD1||||1829374012^Okonkwo^Gregory^S^^^DO^^NPI
PV1|1|O|MED^2104^01^CROZER_CHESTER||||1829374012^Okonkwo^Gregory^S^^^DO^^NPI|||||||||||72839104^^^CROZER^VN
IN1|1|1|AETNA_PA|Aetna Better Health of PA|||||||MANAGED_MEDICAID||20260101||||Benson^Jessica^Lynn|01^Self^HL70063|19880403|1105 W 9th St^^Chester^PA^19013^USA||||||||||||||||W829471023
```

---

## 17. MDM^T02 - Consultation note from Allegheny General Hospital

```
MSH|^~\&|MIRTH|AGH_AHN|DOCREPO|AHN_HIE|20260509163022||MDM^T02^MDM_T02|AGH2026050916302201|P|2.5.1|||NE|AL||UNICODE UTF-8
EVN|T02|20260509163000
PID|1||MRN4429381^^^AHN^MR||Donahue^Kathleen^Marie^^^^L||19620718|F||2106-3^White^CDCREC|3847 California Ave^^Pittsburgh^PA^15212^USA^H^^Allegheny||^PRN^PH^^^412^7391824||M^Married^HL70002|||||||N^Not Hispanic^HL70189
PV1|1|I|CARD^5102^01^AGH^^^^5TH FL CARDIOLOGY|R|||1938274016^DiNardo^Anthony^J^^^MD^^NPI
TXA|1|CN^Consultation Note^HL70270|TX|20260509160000|1938274016^DiNardo^Anthony^J^^^MD^^NPI|20260509162000|20260509163000|||||DOC7829401||||consult_donahue_cardiology.txt|AU||AV||||||Cardiology Consultation - Donahue, Kathleen M
OBX|1|FT|11488-4^Consultation Note^LN||CARDIOLOGY CONSULTATION\.br\\.br\Patient: Donahue, Kathleen M\.br\DOB: 07/18/1962    MRN: MRN4429381\.br\Date of Consultation: 05/09/2026\.br\Requesting Physician: Dr. Robert Ferrante, Internal Medicine\.br\\.br\REASON FOR CONSULTATION: Evaluation of new-onset atrial fibrillation\.br\\.br\HISTORY: 63-year-old female admitted with palpitations and dyspnea on exertion x 3 days. ECG on admission showed atrial fibrillation with rapid ventricular response, rate 142. Initial troponin negative. Echocardiogram: LVEF 55%, mild left atrial dilation, no significant valvular disease.\.br\\.br\ASSESSMENT AND PLAN:\.br\1. New-onset atrial fibrillation - rate control with metoprolol, initiate anticoagulation with apixaban, CHA2DS2-VASc score 3\.br\2. TSH pending to rule out thyroid etiology\.br\3. Consider TEE/cardioversion if no conversion with rate control in 48 hours||||||F|||20260509163000||1938274016^DiNardo^Anthony^J^^^MD^^NPI
```

---

## 18. ORU^R01 - Toxicology screen from Temple University Hospital

```
MSH|^~\&|MIRTH|TEMPLE_UH|LAB_FEED|TEMPLE_HIE|20260509053045||ORU^R01^ORU_R01|TUH2026050905304501|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN8829104^^^TEMPLE^MR||Perkins^Marcus^Dwayne^^^^L||19970302|M||2054-5^Black or African American^CDCREC|4517 N Broad St^^Philadelphia^PA^19140^USA^H^^Philadelphia||^PRN^CP^^^215^6829341||S^Single^HL70002|||||||N^Not Hispanic^HL70189
PV1|1|E|ED^EDBED07^01^TEMPLE_UH^^^^ED MAIN|U|||1829374501^Tran^Thanh^V^^^MD^^NPI|||EM
ORC|RE|ORD33928471^EHR|TOX88291^TEMPLE||CM||||20260509030000|||1829374501^Tran^Thanh^V^^^MD^^NPI
OBR|1|ORD33928471^EHR|TOX88291^TEMPLE|80307^Drug Test, Presumptive^CPT4|||20260509030000|||||||||1829374501^Tran^Thanh^V^^^MD^^NPI||||||20260509050000|||F
OBX|1|CE|3426-4^Amphetamines Screen^LN||NEG^Negative^L||Negative|N|||F|||20260509050000
OBX|2|CE|3397-7^Barbiturates Screen^LN||NEG^Negative^L||Negative|N|||F|||20260509050000
OBX|3|CE|3398-5^Benzodiazepines Screen^LN||POS^Positive^L||Negative|A|||F|||20260509050000
OBX|4|CE|3427-2^Cannabinoids Screen^LN||POS^Positive^L||Negative|A|||F|||20260509050000
OBX|5|CE|3299-1^Cocaine Metabolite Screen^LN||NEG^Negative^L||Negative|N|||F|||20260509050000
OBX|6|CE|19659-2^Fentanyl Screen^LN||POS^Positive^L||Negative|A|||F|||20260509050000
OBX|7|CE|3679-8^Methadone Screen^LN||NEG^Negative^L||Negative|N|||F|||20260509050000
OBX|8|CE|3878-6^Opiates Screen^LN||NEG^Negative^L||Negative|N|||F|||20260509050000
OBX|9|CE|8150-0^PCP Screen^LN||NEG^Negative^L||Negative|N|||F|||20260509050000
```

---

## 19. ADT^A01 - Trauma admission at Thomas Jefferson University Hospital

```
MSH|^~\&|NEXTGEN_CONNECT|TJUH_PHILA|TRAUMA_REG|PA_TRAUMA_REGISTRY|20260509022145||ADT^A01^ADT_A01|TJUH2026050902214501|P|2.5.1|||AL|NE||UNICODE UTF-8
EVN|A01|20260509021500|||BMORGAN^Morgan^Brian^T^^^RN
PID|1||MRN1129384^^^TJUH^MR||Vega^Carlos^Manuel^^^^L||19780614|M||2106-3^White^CDCREC|2631 S 3rd St^^Philadelphia^PA^19148^USA^H^^Philadelphia||^PRN^CP^^^267^8291437||M^Married^HL70002|||||||H^Hispanic or Latino^HL70189
NK1|1|Vega^Maria^Elena|SPO^Spouse^HL70063|2631 S 3rd St^^Philadelphia^PA^19148^USA|^PRN^CP^^^267^3829174||EC^Emergency Contact^HL70131
PV1|1|E|ED^TRAUMA1^01^TJUH^^^^TRAUMA BAY|E^Emergency|||1647382910^Kowalczyk^C^William^^^MD^^NPI|||SUR||||1|||1647382910^Kowalczyk^C^William^^^MD^^NPI||93728401^^^TJUH^VN|||||||||||||||||||||||||20260509021500
PV2|||^Multiple rib fractures with pneumothorax||||||||||||||E^Emergency^HL70007
DG1|1|I10|S22.49XA^Multiple fractures of ribs, unspecified side, initial encounter^I10||20260509|A
DG1|2|I10|J93.0^Spontaneous tension pneumothorax^I10||20260509|A
DG1|3|I10|V43.52XA^Car passenger injured in collision with SUV, initial encounter^I10||20260509|A
```

---

## 20. ORU^R01 - Cardiac catheterization result from Main Line Health Lankenau

```
MSH|^~\&|MIRTH|LANKENAU_MLH|CARDREPO|MLH_HIE|20260509142800||ORU^R01^ORU_R01|MLH2026050914280001|P|2.5.1|||AL|NE||UNICODE UTF-8
PID|1||MRN5529184^^^MLH^MR||McGrath^Patrick^Francis^^^^L||19570823|M||2106-3^White^CDCREC|448 Haverford Ave^^Narberth^PA^19072^USA^H^^Montgomery||^PRN^PH^^^610^6829471~^PRN^CP^^^484^3291847||M^Married^HL70002|||||||N^Not Hispanic^HL70189
PV1|1|I|CATH^CL01^01^LANKENAU^^^^CATH LAB|R|||1829471036^Rosenfeld^Steven^M^^^MD^^NPI|||CAR
ORC|RE|ORD77928310^EHR|CATH44829^LANKENAU||CM||||20260509100000|||1829471036^Rosenfeld^Steven^M^^^MD^^NPI
OBR|1|ORD77928310^EHR|CATH44829^LANKENAU|93458^Left heart catheterization with ventriculography^CPT4|||20260509100000|||||||||1829471036^Rosenfeld^Steven^M^^^MD^^NPI||||||20260509140000|||F
OBX|1|FT|18745-0^Cardiac Catheterization Report^LN||CARDIAC CATHETERIZATION REPORT\.br\\.br\Patient: McGrath, Patrick F\.br\DOB: 08/23/1957    MRN: MRN5529184\.br\Date of Procedure: 05/09/2026\.br\Operator: Steven M. Rosenfeld, MD, FACC\.br\\.br\INDICATION: Unstable angina, positive stress test\.br\\.br\HEMODYNAMICS:\.br\LV end-diastolic pressure: 18 mmHg\.br\Aortic pressure: 132/78 mmHg\.br\Cardiac output: 4.8 L/min\.br\LVEF: 50%\.br\\.br\CORONARY ANGIOGRAPHY:\.br\Left main: Normal\.br\LAD: 80% stenosis mid-segment\.br\LCx: 40% stenosis proximal, nondominant\.br\RCA: Dominant, 50% stenosis mid-segment\.br\\.br\CONCLUSION: Significant single-vessel CAD involving the mid-LAD\.br\RECOMMENDATION: PCI to mid-LAD with drug-eluting stent||||||F|||20260509140000||1829471036^Rosenfeld^Steven^M^^^MD^^NPI
OBX|2|NM|8867-4^Heart rate^LN||72|/min|60-100|N|||F|||20260509100000
OBX|3|NM|18684-1^LVEF by Ventriculography^LN||50|%|55-70|L|||F|||20260509100000
OBX|4|NM|8480-6^Systolic blood pressure^LN||132|mmHg||||F|||20260509100000
OBX|5|NM|8462-4^Diastolic blood pressure^LN||78|mmHg||||F|||20260509100000
```
