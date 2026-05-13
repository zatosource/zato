# Rhapsody Integration Engine - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission at Vanderbilt University Medical Center

```
MSH|^~\&|RHAPSODY|VUMC_ADT|EPIC_ADM|VUMC|20250312084522||ADT^A01^ADT_A01|MSG20250312084522001|P|2.5.1|||AL|NE||ASCII|||
EVN|A01|20250312084500|||KCOLLINS^Collins^Katherine^^^RN
PID|1||MRN998431^^^VUMC^MR||Hargrove^Dolores^Mae^^Mrs.||19580214|F||2106-3^White^CDCREC|1411 Music Row^^Nashville^TN^37203^US||^PRN^PH^^1^615^5559021|^WPN^PH^^1^615^5553847|eng^English^HL70296|M^Married^HL70002|||441-82-6317|||N^Non-Hispanic^HL70189||||||||||
PV1|1|I|4WEST^4W-212^A^VUMC||||1834291^Calloway^Steven^A^^^MD^L^^^NPI|9271458^Zhao^Michelle^Y^^^MD^L^^^NPI||MED||||1|||1834291^Calloway^Steven^A^^^MD^L^^^NPI|IN||||||||||||||||||VUMC||A|||20250312084500||||||
PV2|||CHF^Congestive Heart Failure^I10|||||||2|||||||||||||||||||||||||||||20250312
IN1|1|BCBS_TN^BlueCross BlueShield of Tennessee|12345|BlueCross BlueShield of Tennessee^1 Cameron Hill Circle^^Chattanooga^TN^37402|^PRN^PH^^1^423^5551000|||||GROUP98765|||||||Hargrove^Dolores^Mae|01^Self^HL70063|19580214|1411 Music Row^^Nashville^TN^37203^US|||1||||||||||||||XGP445512001||||||||F
NK1|1|Hargrove^Ronald^T^^Mr.|01^Husband^HL70063|1411 Music Row^^Nashville^TN^37203^US|^PRN^PH^^1^615^5559021||EC^Emergency Contact^HL70131
AL1|1|DA^Drug Allergy^HL70127|70618^Penicillin^RxNorm|MO^Moderate^HL70128|Hives and rash||20100415
DG1|1||I50.9^Heart failure, unspecified^ICD10CM||20250312|A^Admitting^HL70052||||||||||1
GT1|1||Hargrove^Dolores^Mae^^Mrs.||1411 Music Row^^Nashville^TN^37203^US|^PRN^PH^^1^615^5559021||19580214|F||SE^Self^HL70063|441-82-6317
```

---

## 2. ORU^R01 - Lab result from TriStar Centennial Medical Center

```
MSH|^~\&|RHAP_ENGINE|TRISTAR_LAB|CERNER_RES|TRISTAR_CENT|20250415103045||ORU^R01^ORU_R01|MSG20250415103045007|P|2.5.1|||AL|NE||ASCII|||
PID|1||PAT20341987^^^TRISTAR^MR||Townsend^Darius^Lamont||19750819|M||2054-5^Black or African American^CDCREC|2300 Patterson St^^Nashville^TN^37203^US||^PRN^PH^^1^615^5556789||eng^English^HL70296|S^Single^HL70002|||238-51-4790|||N^Non-Hispanic^HL70189
PV1|1|O|LAB_DRAW^LD-3^A^TRISTAR||||7654321^Kapoor^Rajesh^K^^^MD^L^^^NPI|||LAB||||3|||7654321^Kapoor^Rajesh^K^^^MD^L^^^NPI|OP||||||||||||||||||TRISTAR||A|||20250415100000
ORC|RE|ORD9981234^TRISTAR|RES7781234^TRISTAR_LAB||CM||||20250415100000|||7654321^Kapoor^Rajesh^K^^^MD^L^^^NPI||^WPN^PH^^1^615^5552200|||||TRISTAR_CENT^TriStar Centennial Medical Center^L|2300 Patterson St^^Nashville^TN^37203
OBR|1|ORD9981234^TRISTAR|RES7781234^TRISTAR_LAB|24323-8^Comprehensive metabolic panel^LN|||20250415093000||||A|||||7654321^Kapoor^Rajesh^K^^^MD^L^^^NPI||||||20250415103000|||F|||||||||||20250415093000
OBX|1|NM|2345-7^Glucose^LN||98|mg/dL^milligrams per deciliter^UCUM|74-106|N|||F|||20250415100500||AUTO_CHEM7^Automated Chemistry Analyzer
OBX|2|NM|3094-0^Urea nitrogen^LN||18|mg/dL^milligrams per deciliter^UCUM|6-20|N|||F|||20250415100500||AUTO_CHEM7^Automated Chemistry Analyzer
OBX|3|NM|2160-0^Creatinine^LN||1.1|mg/dL^milligrams per deciliter^UCUM|0.7-1.3|N|||F|||20250415100500||AUTO_CHEM7^Automated Chemistry Analyzer
OBX|4|NM|2951-2^Sodium^LN||139|mmol/L^millimoles per liter^UCUM|136-145|N|||F|||20250415100500||AUTO_CHEM7^Automated Chemistry Analyzer
OBX|5|NM|2823-3^Potassium^LN||4.2|mmol/L^millimoles per liter^UCUM|3.5-5.1|N|||F|||20250415100500||AUTO_CHEM7^Automated Chemistry Analyzer
OBX|6|NM|2075-0^Chloride^LN||102|mmol/L^millimoles per liter^UCUM|98-106|N|||F|||20250415100500||AUTO_CHEM7^Automated Chemistry Analyzer
OBX|7|NM|2028-9^Carbon dioxide, total^LN||24|mmol/L^millimoles per liter^UCUM|23-29|N|||F|||20250415100500||AUTO_CHEM7^Automated Chemistry Analyzer
OBX|8|NM|17861-6^Calcium^LN||9.4|mg/dL^milligrams per deciliter^UCUM|8.5-10.5|N|||F|||20250415100500||AUTO_CHEM7^Automated Chemistry Analyzer
OBX|9|NM|2885-2^Protein, total^LN||7.0|g/dL^grams per deciliter^UCUM|6.0-8.3|N|||F|||20250415100500||AUTO_CHEM7^Automated Chemistry Analyzer
OBX|10|NM|1751-7^Albumin^LN||4.1|g/dL^grams per deciliter^UCUM|3.5-5.0|N|||F|||20250415100500||AUTO_CHEM7^Automated Chemistry Analyzer
OBX|11|NM|1975-2^Bilirubin, total^LN||0.8|mg/dL^milligrams per deciliter^UCUM|0.1-1.2|N|||F|||20250415100500||AUTO_CHEM7^Automated Chemistry Analyzer
OBX|12|NM|6768-6^Alkaline phosphatase^LN||72|U/L^units per liter^UCUM|44-147|N|||F|||20250415100500||AUTO_CHEM7^Automated Chemistry Analyzer
OBX|13|NM|1742-6^Alanine aminotransferase^LN||28|U/L^units per liter^UCUM|7-56|N|||F|||20250415100500||AUTO_CHEM7^Automated Chemistry Analyzer
OBX|14|NM|1920-8^Aspartate aminotransferase^LN||22|U/L^units per liter^UCUM|10-40|N|||F|||20250415100500||AUTO_CHEM7^Automated Chemistry Analyzer
```

---

## 3. ORM^O01 - Radiology order from Erlanger Health System

```
MSH|^~\&|RHAPSODY|ERLANGER_RAD|PACS_SYS|ERLANGER|20250508141230||ORM^O01^ORM_O01|MSG20250508141230003|P|2.4|||AL|NE|||
PID|1||ERL4451209^^^ERLANGER^MR||Whitfield^Angela^Renee||19820317|F||2106-3^White^CDCREC|975 East Third St^^Chattanooga^TN^37403^US||^PRN^PH^^1^423^5554102||eng^English^HL70296|M^Married^HL70002|||329-61-4087|||N^Non-Hispanic^HL70189
PV1|1|O|RADOP^RAD-2^A^ERLANGER||||3216540^Obregon^Carlos^E^^^MD^L^^^NPI|||RAD||||5|||3216540^Obregon^Carlos^E^^^MD^L^^^NPI|OP||||||||||||||||||ERLANGER||A|||20250508140000
ORC|NW|RAD20250508001^ERLANGER||GRP20250508001^ERLANGER|||||20250508140000|||3216540^Obregon^Carlos^E^^^MD^L^^^NPI||^WPN^PH^^1^423^5558000|||||ERLANGER^Erlanger Health System^L|975 East Third St^^Chattanooga^TN^37403
OBR|1|RAD20250508001^ERLANGER||71046^XR Chest 2 Views^CPT4|||20250508141000||||A|||||3216540^Obregon^Carlos^E^^^MD^L^^^NPI||||||||||1^^^^^R^^ROUTINE|||||||||20250508141000
DG1|1||R05.9^Cough, unspecified^ICD10CM||20250508|W
OBX|1|TX|NTE_CLIN^Clinical Notes^L||Patient presents with persistent cough for 3 weeks, no fever, non-smoker. Rule out pneumonia.||||||F
```

---

## 4. ADT^A08 - Patient information update at Regional One Health

```
MSH|^~\&|RHAPSODY|REG1_ADT|MEDITECH_HIS|REGIONAL_ONE|20250220162845||ADT^A08^ADT_A01|MSG20250220162845004|P|2.5.1|||AL|NE||ASCII|||
EVN|A08|20250220162800|||MFRANKLIN^Franklin^Monica^^^REG
PID|1||R1MRN776543^^^REGIONAL_ONE^MR||Bledsoe^Terrence^Lamar^^Mr.||19690405|M||2054-5^Black or African American^CDCREC|880 Madison Ave^^Memphis^TN^38103^US||^PRN^PH^^1^901^5553456|^WPN^PH^^1^901^5558790|eng^English^HL70296|M^Married^HL70002|||563-84-2197|||N^Non-Hispanic^HL70189||||||||||
PV1|1|I|6N^6N-401^B^REGIONAL_ONE||||8765432^Kirkland^Sharon^L^^^MD^L^^^NPI|5432109^Yoon^Daniel^H^^^MD^L^^^NPI||SURG||||2|||8765432^Kirkland^Sharon^L^^^MD^L^^^NPI|IN||||||||||||||||||REGIONAL_ONE||A|||20250218100000||||||
NK1|1|Bledsoe^Denise^M^^Mrs.|02^Wife^HL70063|880 Madison Ave^^Memphis^TN^38103^US|^PRN^PH^^1^901^5553456||EC^Emergency Contact^HL70131
IN1|1|CIGNA_TN^Cigna|67890|Cigna^900 Cottage Grove Rd^^Bloomfield^CT^06002|^PRN^PH^^1^800^5551234|||||GRP44321|||||||Bledsoe^Terrence^Lamar|01^Self^HL70063|19690405|880 Madison Ave^^Memphis^TN^38103^US|||1||||||||||||||CIG887654321||||||||M
```

---

## 5. ORU^R01 - Pathology result with embedded PDF from Baptist Memorial Hospital

```
MSH|^~\&|RHAP_ENGINE|BAPTIST_PATH|EPIC_BEAKER|BAPTIST_MEM|20250601091500||ORU^R01^ORU_R01|MSG20250601091500005|P|2.5.1|||AL|NE||ASCII|||
PID|1||BMH3390211^^^BAPTIST^MR||Langston^Cynthia^Elaine||19710922|F||2106-3^White^CDCREC|6019 Walnut Grove Rd^^Memphis^TN^38120^US||^PRN^PH^^1^901^5557623||eng^English^HL70296|D^Divorced^HL70002|||674-18-9352|||N^Non-Hispanic^HL70189
PV1|1|O|PATH^PATH-1^A^BAPTIST||||4321098^Tran^Thanh^V^^^MD^L^^^NPI|||PATH||||1|||4321098^Tran^Thanh^V^^^MD^L^^^NPI|OP||||||||||||||||||BAPTIST||A|||20250530140000
ORC|RE|ORD20250530445^BAPTIST|RES20250601112^BAPTIST_PATH||CM||||20250530140000|||4321098^Tran^Thanh^V^^^MD^L^^^NPI||^WPN^PH^^1^901^5554000|||||BAPTIST_MEM^Baptist Memorial Hospital^L|6019 Walnut Grove Rd^^Memphis^TN^38120
OBR|1|ORD20250530445^BAPTIST|RES20250601112^BAPTIST_PATH|88305^Surgical Pathology^CPT4|||20250530141500||||A|||||4321098^Tran^Thanh^V^^^MD^L^^^NPI||||||20250601091000|||F
OBX|1|TX|22637-3^Pathology report final diagnosis^LN||Specimen: Left breast, lumpectomy~Diagnosis: Invasive ductal carcinoma, grade 2~Tumor size: 1.4 cm~Margins: Negative (closest margin 0.3 cm, anterior)~Lymphovascular invasion: Not identified~DCIS component: Present, comprising approximately 15% of tumor||||||F|||20250601090000||4321098^Tran^Thanh^V^^^MD^L^^^NPI
OBX|2|ED|PDF^Pathology Report PDF^L||^application^pdf^Base64^JVBERi0xLjcKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDcyIDcyMCBUZCAoUGF0aG9sb2d5IFJlcG9ydCAtIEJhcHRpc3QgTWVtb3JpYWwgSG9zcGl0YWwpIFRqIEVUIAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAgbiAKMDAwMDAwMDQwMiAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjQ4NQolJUVPRgo=||||||F|||20250601090000||4321098^Tran^Thanh^V^^^MD^L^^^NPI
```

---

## 6. SIU^S12 - Appointment scheduling at Blount Memorial Hospital

```
MSH|^~\&|RHAPSODY|BLOUNT_SCHED|ALLSCRIPTS|BLOUNT_MEM|20250318094500||SIU^S12^SIU_S12|MSG20250318094500006|P|2.5.1|||AL|NE||ASCII|||
SCH|APT20250320001^BLOUNT|APT20250320001^BLOUNT|||ROUTINE^Routine^HL70276|FOLLOWUP^Follow-up visit^HL70277|30^MIN|^^30^20250320100000^20250320103000|||||6543210^Hamblen^James^W^^^MD^L^^^NPI|^WPN^PH^^1^865^5553100|907 East Lamar Alexander Pkwy^^Maryville^TN^37804||APT20250320001^BLOUNT||BOOKED
PID|1||BLT1198432^^^BLOUNT^MR||Tipton^Harold^Eugene^^Mr.||19550611|M||2106-3^White^CDCREC|217 Court St^^Maryville^TN^37804^US||^PRN^PH^^1^865^5557654||eng^English^HL70296|M^Married^HL70002|||897-14-5263|||N^Non-Hispanic^HL70189
PV1|1|O|CARD_CLINIC^CC-2^A^BLOUNT||||6543210^Hamblen^James^W^^^MD^L^^^NPI|||CARD||||5|||6543210^Hamblen^James^W^^^MD^L^^^NPI|OP||||||||||||||||||BLOUNT||A|||20250320100000
RGS|1|A|CARD_CLINIC^Cardiology Clinic^L
AIS|1|A|CARDFOLLOW^Cardiology Follow-up^L|20250320100000|||30^MIN|30^MIN|||BOOKED
AIG|1|A|6543210^Hamblen^James^W^^^MD^L^^^NPI||||20250320100000|||30^MIN|||BOOKED
AIL|1|A|CARD_CLINIC^CC-2^A^BLOUNT||||20250320100000|||30^MIN|||BOOKED
```

---

## 7. ADT^A04 - Patient registration at LeConte Medical Center

```
MSH|^~\&|RHAPSODY|LECONTE_REG|CPSI_HIS|LECONTE_MC|20250127110200||ADT^A04^ADT_A01|MSG20250127110200007|P|2.5|||AL|NE|||
EVN|A04|20250127110000|||RSHEPHERD^Shepherd^Rebecca^^^REG
PID|1||LMC2287654^^^LECONTE^MR||Ogle^Bobby^Wayne^^Mr.||19480930|M||2106-3^White^CDCREC|445 Middle Creek Rd^^Sevierville^TN^37862^US||^PRN^PH^^1^865^5552198||eng^English^HL70296|W^Widowed^HL70002|||127-43-8651|||N^Non-Hispanic^HL70189
PV1|1|E|ED^ED-12^A^LECONTE||||2109876^Hensley^Deborah^A^^^MD^L^^^NPI|||EM||||1|||2109876^Hensley^Deborah^A^^^MD^L^^^NPI|EM||||||||||||||||||LECONTE||A|||20250127110000
PV2|||R10.9^Abdominal pain, unspecified^ICD10CM
NK1|1|Ogle^Linda^S^^Ms.|09^Daughter^HL70063|221 Maple Lane^^Sevierville^TN^37862^US|^PRN^PH^^1^865^5553321||EC^Emergency Contact^HL70131
IN1|1|MEDICARE^Medicare|CMS001|Centers for Medicare and Medicaid Services^7500 Security Blvd^^Baltimore^MD^21244|^PRN^PH^^1^800^5551234|||||||||||||Ogle^Bobby^Wayne|01^Self^HL70063|19480930|445 Middle Creek Rd^^Sevierville^TN^37862^US|||1||||||||||||||1EG4TE5MK72||||||||M
```

---

## 8. MDM^T02 - Transcription document from Parkwest Medical Center

```
MSH|^~\&|RHAP_ENGINE|PARKWEST_TRANS|MEDITECH_DOC|PARKWEST|20250410153200||MDM^T02^MDM_T02|MSG20250410153200008|P|2.5.1|||AL|NE||ASCII|||
EVN|T02|20250410153000
PID|1||PWM4401987^^^PARKWEST^MR||Crawley^Karen^Elizabeth||19660708|F||2106-3^White^CDCREC|9352 Westland Dr^^Knoxville^TN^37922^US||^PRN^PH^^1^865^5556543||eng^English^HL70296|M^Married^HL70002|||231-69-4870|||N^Non-Hispanic^HL70189
PV1|1|I|3S^3S-315^A^PARKWEST||||1098765^Rutherford^William^T^^^MD^L^^^NPI|||ORTH||||1|||1098765^Rutherford^William^T^^^MD^L^^^NPI|IN||||||||||||||||||PARKWEST||A|||20250408090000
TXA|1|OP^Operative Note^HL70270|TX^Text^HL70191|20250410150000||20250410153000|||||1098765^Rutherford^William^T^^^MD^L^^^NPI|DOC20250410315^PARKWEST|||AU^Authenticated^HL70271||||
OBX|1|TX|11504-8^Surgical operation note^LN||OPERATIVE NOTE~Patient: Crawley, Karen E~DOB: 07/08/1966~MRN: PWM4401987~Date of Surgery: 04/08/2025~Surgeon: William T. Rutherford, MD~Procedure: Right total knee arthroplasty~Anesthesia: Spinal with sedation~Indication: Severe right knee osteoarthritis, failed conservative management~Findings: Grade IV chondromalacia of medial and lateral compartments with significant varus deformity~Implants: Stryker Triathlon size 5 femoral, size 4 tibial, 10mm poly insert~EBL: 150 mL~Complications: None~Disposition: PACU in stable condition||||||F|||20250410150000||1098765^Rutherford^William^T^^^MD^L^^^NPI
```

---

## 9. ACK - Acknowledgment from Tennessee Department of Health immunization registry

```
MSH|^~\&|TENNIIS|TN_DOH|RHAPSODY|VUMC_IMM|20250225134500||ACK^V04^ACK|ACK20250225134500009|P|2.5.1|||AL|NE||ASCII|||
MSA|AA|MSG20250225134200044|Message accepted and processed successfully
ERR||PID^1^3|101^Required field missing^HL70357|W|||||Patient SSN not provided, record accepted without SSN
```

---

## 10. ORU^R01 - Microbiology result from UT Medical Center

```
MSH|^~\&|RHAPSODY|UTMC_MICRO|EPIC_BEAKER|UT_MED_CTR|20250519082200||ORU^R01^ORU_R01|MSG20250519082200010|P|2.5.1|||AL|NE||ASCII|||
PID|1||UTMC6651234^^^UTMC^MR||Buckner^Gregory^Allen||19870314|M||2106-3^White^CDCREC|1924 Alcoa Hwy^^Knoxville^TN^37920^US||^PRN^PH^^1^865^5559087||eng^English^HL70296|S^Single^HL70002|||342-61-5918|||N^Non-Hispanic^HL70189
PV1|1|I|ICU^ICU-8^A^UTMC||||7890123^Norwood^Linda^M^^^MD^L^^^NPI|||MED||||1|||7890123^Norwood^Linda^M^^^MD^L^^^NPI|IN||||||||||||||||||UTMC||A|||20250517060000
ORC|RE|ORD20250517890^UTMC|RES20250519321^UTMC_MICRO||CM||||20250517080000|||7890123^Norwood^Linda^M^^^MD^L^^^NPI||^WPN^PH^^1^865^5551000|||||UT_MED_CTR^University of Tennessee Medical Center^L|1924 Alcoa Hwy^^Knoxville^TN^37920
OBR|1|ORD20250517890^UTMC|RES20250519321^UTMC_MICRO|87040^Blood Culture^CPT4|||20250517081000||||A|||||7890123^Norwood^Linda^M^^^MD^L^^^NPI||||||20250519082000|||F
OBX|1|CWE|600-7^Bacteria identified in Blood by Culture^LN||3092008^Staphylococcus aureus^SCT||||||F|||20250519080000||TECH_MB01^Microbiology Tech
OBX|2|TX|18769-0^Microbial susceptibility tests^LN||Oxacillin: Resistant (MRSA confirmed)~Vancomycin: Susceptible (MIC 1.0 mcg/mL)~Daptomycin: Susceptible (MIC 0.5 mcg/mL)~Linezolid: Susceptible~Trimethoprim/Sulfamethoxazole: Susceptible~Clindamycin: Resistant~Gentamicin: Susceptible||||||F|||20250519081500||TECH_MB01^Microbiology Tech
OBX|3|TX|19156-9^Gram stain^LN||Gram positive cocci in clusters||||||F|||20250517090000||TECH_MB01^Microbiology Tech
```

---

## 11. ADT^A01 - Admission at Johnson City Medical Center

```
MSH|^~\&|RHAPSODY|JCMC_ADT|CERNER_MILLEN|JCMC|20250603072000||ADT^A01^ADT_A01|MSG20250603072000011|P|2.5.1|||AL|NE||ASCII|||
EVN|A01|20250603071500|||DWILBURN^Wilburn^Diane^^^RN
PID|1||JCMC8812345^^^JCMC^MR||Shelton^Donna^Faye^^Mrs.||19610125|F||2106-3^White^CDCREC|1501 Volunteer Pkwy^^Bristol^TN^37620^US||^PRN^PH^^1^423^5554321|^WPN^PH^^1^423^5558901|eng^English^HL70296|M^Married^HL70002|||452-71-6039|||N^Non-Hispanic^HL70189||||||||||
PV1|1|I|CCU^CCU-3^A^JCMC||||4567890^Bowman^Anthony^G^^^MD^L^^^NPI|3456789^Cho^Susan^J^^^MD^L^^^NPI||CARD||||1|||4567890^Bowman^Anthony^G^^^MD^L^^^NPI|IN||||||||||||||||||JCMC||A|||20250603071500||||||
PV2|||I21.0^ST elevation myocardial infarction involving left main coronary artery^ICD10CM|||||||3|||||||||||||||||||||||||||||20250603
IN1|1|AETNA_TN^Aetna|55432|Aetna^151 Farmington Ave^^Hartford^CT^06156|^PRN^PH^^1^800^5554567|||||GRP77654|||||||Shelton^Donna^Faye|01^Self^HL70063|19610125|1501 Volunteer Pkwy^^Bristol^TN^37620^US|||1||||||||||||||AET332145678||||||||F
DG1|1||I21.0^ST elevation myocardial infarction involving left main coronary artery^ICD10CM||20250603|A^Admitting^HL70052||||||||||1
AL1|1|DA^Drug Allergy^HL70127|2670^Codeine^RxNorm|SV^Severe^HL70128|Anaphylaxis||19950812
```

---

## 12. ORM^O01 - Laboratory order from Maury Regional Medical Center

```
MSH|^~\&|RHAPSODY|MAURY_LAB|SUNQUEST_LIS|MAURY_REG|20250714083000||ORM^O01^ORM_O01|MSG20250714083000012|P|2.4|||AL|NE|||
PID|1||MRM5567891^^^MAURY^MR||Gentry^James^Edward^^Mr.||19720418|M||2106-3^White^CDCREC|1224 Trotwood Ave^^Columbia^TN^38401^US||^PRN^PH^^1^931^5556789||eng^English^HL70296|M^Married^HL70002|||564-82-7130|||N^Non-Hispanic^HL70189
PV1|1|O|LABDRW^LD-1^A^MAURY||||8901234^Stokes^Patricia^D^^^MD^L^^^NPI|||MED||||3|||8901234^Stokes^Patricia^D^^^MD^L^^^NPI|OP||||||||||||||||||MAURY||A|||20250714082000
ORC|NW|LAB20250714002^MAURY||GRP20250714002^MAURY|||||20250714082000|||8901234^Stokes^Patricia^D^^^MD^L^^^NPI||^WPN^PH^^1^931^5551000|||||MAURY_REG^Maury Regional Medical Center^L|1224 Trotwood Ave^^Columbia^TN^38401
OBR|1|LAB20250714002^MAURY||85025^CBC with Differential^CPT4|||20250714083000||||A|||||8901234^Stokes^Patricia^D^^^MD^L^^^NPI||||||||1^^^^^R^^ROUTINE
OBR|2|LAB20250714002^MAURY||80053^Comprehensive Metabolic Panel^CPT4|||20250714083000||||A|||||8901234^Stokes^Patricia^D^^^MD^L^^^NPI||||||||1^^^^^R^^ROUTINE
OBR|3|LAB20250714002^MAURY||83036^Hemoglobin A1c^CPT4|||20250714083000||||A|||||8901234^Stokes^Patricia^D^^^MD^L^^^NPI||||||||1^^^^^R^^ROUTINE
DG1|1||E11.65^Type 2 diabetes mellitus with hyperglycemia^ICD10CM||20250714|W
```

---

## 13. ORU^R01 - Radiology report with embedded image from Williamson Medical Center

```
MSH|^~\&|RHAP_ENGINE|WMC_RAD|PACS_STORE|WILLIAMSON_MC|20250822141000||ORU^R01^ORU_R01|MSG20250822141000013|P|2.5.1|||AL|NE||ASCII|||
PID|1||WMC3345678^^^WMC^MR||Pennington^Allison^Grace||19890601|F||2106-3^White^CDCREC|4321 Mallory Lane^^Franklin^TN^37067^US||^PRN^PH^^1^615^5558765||eng^English^HL70296|S^Single^HL70002|||671-93-4128|||N^Non-Hispanic^HL70189
PV1|1|O|RADOP^RAD-1^A^WMC||||5678901^Maddox^Richard^B^^^MD^L^^^NPI|||RAD||||1|||5678901^Maddox^Richard^B^^^MD^L^^^NPI|OP||||||||||||||||||WMC||A|||20250822133000
ORC|RE|RAD20250822010^WMC|RES20250822456^WMC_RAD||CM||||20250822133000|||5678901^Maddox^Richard^B^^^MD^L^^^NPI||^WPN^PH^^1^615^5554500|||||WILLIAMSON_MC^Williamson Medical Center^L|4321 Carothers Pkwy^^Franklin^TN^37067
OBR|1|RAD20250822010^WMC|RES20250822456^WMC_RAD|71260^CT Chest with Contrast^CPT4|||20250822134500||||A|||||5678901^Maddox^Richard^B^^^MD^L^^^NPI||||||20250822140500|||F
OBX|1|TX|18748-4^Diagnostic imaging study^LN||CT CHEST WITH CONTRAST~Clinical History: 35-year-old female with pleuritic chest pain, r/o PE~Technique: Helical CT of the chest with 75 mL Omnipaque 350 IV contrast~Findings: No evidence of pulmonary embolism. Lungs are clear bilaterally. No pleural effusion. Heart size normal. Mediastinal structures unremarkable. No lymphadenopathy. Osseous structures intact.~Impression: 1. No pulmonary embolism. 2. Normal CT chest.||||||F|||20250822140500||5678901^Maddox^Richard^B^^^MD^L^^^NPI
OBX|2|ED|IMG^CT Key Image^L||^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAgACADASIAAhEBAxEB/8QAGAABAQEBAQAAAAAAAAAAAAAAAAUGBAf/xAAqEAABBAEDAwMEAwAAAAAAAAABAAIDEQQFEiExQVETImEGFIGRMnKh/8QAFgEBAQEAAAAAAAAAAAAAAAAAAAEC/8QAFhEBAQEAAAAAAAAAAAAAAAAAAAER/9oADAMBAAIRAxEAPwD0lVdM1TE1aMyaaXJHLE5zJIZIXMcxw6gg/wCLmznZeLr2Bps8hZBlRyuZGT7Wua0EWe3UpOkaNkaVNkyxZkkLpm7ZGBuw1XRw6jwfhBoUREBERAREQf/Z||||||F|||20250822140500||5678901^Maddox^Richard^B^^^MD^L^^^NPI
```

---

## 14. ADT^A04 - Emergency registration at Sumner Regional Medical Center

```
MSH|^~\&|RHAPSODY|SUMNER_REG|MEDHOST_HIS|SUMNER_MC|20250105191500||ADT^A04^ADT_A01|MSG20250105191500014|P|2.5|||AL|NE|||
EVN|A04|20250105191200|||LTAYLOR^Taylor^Lisa^^^REG
PID|1||SRM1123456^^^SUMNER^MR||Kilgore^Walter^Lee^^Mr.||19530218|M||2106-3^White^CDCREC|803 New Shackle Island Rd^^Hendersonville^TN^37075^US||^PRN^PH^^1^615^5551234||eng^English^HL70296|M^Married^HL70002|||783-09-4215|||N^Non-Hispanic^HL70189
PV1|1|E|ED^ED-7^A^SUMNER||||6789012^Whitmore^Christopher^L^^^MD^L^^^NPI|||EM||||1|||6789012^Whitmore^Christopher^L^^^MD^L^^^NPI|EM||||||||||||||||||SUMNER||A|||20250105191200
PV2|||S72.001A^Fracture of unspecified part of neck of right femur, initial encounter^ICD10CM
NK1|1|Kilgore^Margaret^A^^Mrs.|02^Wife^HL70063|803 New Shackle Island Rd^^Hendersonville^TN^37075^US|^PRN^PH^^1^615^5551234||EC^Emergency Contact^HL70131
IN1|1|UHC_TN^UnitedHealthcare|33210|UnitedHealthcare^PO Box 740800^^Atlanta^GA^30374|^PRN^PH^^1^800^5559876|||||GRP22109|||||||Kilgore^Walter^Lee|01^Self^HL70063|19530218|803 New Shackle Island Rd^^Hendersonville^TN^37075^US|||1||||||||||||||UHC556789012||||||||M
```

---

## 15. SIU^S12 - Appointment notification from Tennova Healthcare Clarksville

```
MSH|^~\&|RHAPSODY|TENNOVA_SCHED|ATHENA_PM|TENNOVA_CLK|20250401080000||SIU^S12^SIU_S12|MSG20250401080000015|P|2.5.1|||AL|NE||ASCII|||
SCH|APT20250403001^TENNOVA|APT20250403001^TENNOVA|||ROUTINE^Routine^HL70276|NEWPT^New Patient Visit^HL70277|60^MIN|^^60^20250403140000^20250403150000|||||2345678^Lattimore^Laura^M^^^MD^L^^^NPI|^WPN^PH^^1^931^5551500|651 Dunlop Lane^^Clarksville^TN^37040||APT20250403001^TENNOVA||BOOKED
PID|1||TNC7789012^^^TENNOVA^MR||Fuentes^Sofia^Isabel||19950812|F||2106-3^White^CDCREC|2814 Wilma Rudolph Blvd^^Clarksville^TN^37040^US||^PRN^PH^^1^931^5554567||spa^Spanish^HL70296|S^Single^HL70002|||896-14-7302|||2135-2^Hispanic or Latino^HL70189
PV1|1|O|OBGYN^OB-1^A^TENNOVA||||2345678^Lattimore^Laura^M^^^MD^L^^^NPI|||OBG||||5|||2345678^Lattimore^Laura^M^^^MD^L^^^NPI|OP||||||||||||||||||TENNOVA||A|||20250403140000
RGS|1|A|OBGYN^Obstetrics and Gynecology Clinic^L
AIS|1|A|OBNEW^OB New Patient^L|20250403140000|||60^MIN|60^MIN|||BOOKED
AIG|1|A|2345678^Lattimore^Laura^M^^^MD^L^^^NPI||||20250403140000|||60^MIN|||BOOKED
AIL|1|A|OBGYN^OB-1^A^TENNOVA||||20250403140000|||60^MIN|||BOOKED
```

---

## 16. ORU^R01 - Cardiac catheterization results from Saint Thomas West Hospital

```
MSH|^~\&|RHAPSODY|STW_CATH|EPIC_HAIKU|ST_THOMAS_W|20250211165400||ORU^R01^ORU_R01|MSG20250211165400016|P|2.5.1|||AL|NE||ASCII|||
PID|1||STW2234567^^^STW^MR||Cantrell^Daniel^Joseph^^Mr.||19640329|M||2106-3^White^CDCREC|4220 Harding Pike^^Nashville^TN^37205^US||^PRN^PH^^1^615^5553890||eng^English^HL70296|M^Married^HL70002|||908-21-3574|||N^Non-Hispanic^HL70189
PV1|1|I|CATH^CATH-2^A^STW||||3456781^Aldridge^Mark^S^^^MD^L^^^NPI|||CARD||||1|||3456781^Aldridge^Mark^S^^^MD^L^^^NPI|IN||||||||||||||||||STW||A|||20250211120000
ORC|RE|CATH20250211001^STW|RES20250211789^STW_CATH||CM||||20250211120000|||3456781^Aldridge^Mark^S^^^MD^L^^^NPI||^WPN^PH^^1^615^5552222|||||ST_THOMAS_W^Saint Thomas West Hospital^L|4220 Harding Pike^^Nashville^TN^37205
OBR|1|CATH20250211001^STW|RES20250211789^STW_CATH|93458^Left Heart Catheterization^CPT4|||20250211140000||||A|||||3456781^Aldridge^Mark^S^^^MD^L^^^NPI||||||20250211165000|||F
OBX|1|TX|18745-0^Cardiac catheterization study^LN||LEFT HEART CATHETERIZATION REPORT~Patient: Cantrell, Daniel J~Date: 02/11/2025~Physician: Mark S. Aldridge, MD~Indication: Unstable angina, positive stress test~Access: Right radial artery, 6 French~Hemodynamics: LVEDP 18 mmHg, Aortic pressure 130/75 mmHg, Cardiac output 5.2 L/min~Coronary Angiography:~- Left Main: Normal~- LAD: 80% stenosis in mid-segment~- LCx: 40% stenosis in proximal segment~- RCA: Normal~Left Ventriculography: EF 50%, mild inferior hypokinesis~Impression: Significant single-vessel disease (LAD). Recommend PCI to mid-LAD.~Complications: None||||||F|||20250211165000||3456781^Aldridge^Mark^S^^^MD^L^^^NPI
OBX|2|NM|8867-4^Heart rate^LN||72|/min^beats per minute^UCUM|60-100|N|||F|||20250211140500||3456781^Aldridge^Mark^S^^^MD^L^^^NPI
OBX|3|NM|8480-6^Systolic blood pressure^LN||130|mm[Hg]^millimeters of mercury^UCUM|90-140|N|||F|||20250211140500||3456781^Aldridge^Mark^S^^^MD^L^^^NPI
OBX|4|NM|8462-4^Diastolic blood pressure^LN||75|mm[Hg]^millimeters of mercury^UCUM|60-90|N|||F|||20250211140500||3456781^Aldridge^Mark^S^^^MD^L^^^NPI
```

---

## 17. ADT^A08 - Insurance update at Cookeville Regional Medical Center

```
MSH|^~\&|RHAP_ENGINE|CRMC_ADT|CPSI_HIS|CRMC|20250916104500||ADT^A08^ADT_A01|MSG20250916104500017|P|2.5|||AL|NE|||
EVN|A08|20250916104200|||JBARNES^Barnes^Jessica^^^REG
PID|1||CRMC9945678^^^CRMC^MR||Allison^Timothy^Scott^^Mr.||19780523|M||2106-3^White^CDCREC|155 West 4th St^^Cookeville^TN^38501^US||^PRN^PH^^1^931^5559900||eng^English^HL70296|M^Married^HL70002|||019-37-8564|||N^Non-Hispanic^HL70189
PV1|1|I|MED^MED-210^A^CRMC||||4567812^Hawkins^Rachel^N^^^MD^L^^^NPI|||MED||||2|||4567812^Hawkins^Rachel^N^^^MD^L^^^NPI|IN||||||||||||||||||CRMC||A|||20250914080000
IN1|1|TNCARE^TennCare|TN001|TennCare^310 Great Circle Rd^^Nashville^TN^37243|^PRN^PH^^1^800^5553456|||||||||||||Allison^Timothy^Scott|01^Self^HL70063|19780523|155 West 4th St^^Cookeville^TN^38501^US|||1||||||||||||||TNC445678901||||||||M
IN1|2|BCBS_TN^BlueCross BlueShield of Tennessee|12345|BlueCross BlueShield of Tennessee^1 Cameron Hill Circle^^Chattanooga^TN^37402|^PRN^PH^^1^423^5551000|||||GROUP55421|||||||Allison^Timothy^Scott|01^Self^HL70063|19780523|155 West 4th St^^Cookeville^TN^38501^US|||2||||||||||||||XGP998877001||||||||M
```

---

## 18. ORM^O01 - Pharmacy order from Methodist Le Bonheur Healthcare

```
MSH|^~\&|RHAPSODY|MLB_PHARM|EPIC_WILLOW|METHODIST_LB|20250802093000||ORM^O01^ORM_O01|MSG20250802093000018|P|2.5.1|||AL|NE||ASCII|||
PID|1||MLB7712345^^^MLB^MR||Grandberry^Latoya^Denise||19830916|F||2054-5^Black or African American^CDCREC|1265 Union Ave^^Memphis^TN^38104^US||^PRN^PH^^1^901^5553210||eng^English^HL70296|S^Single^HL70002|||128-94-6753|||N^Non-Hispanic^HL70189
PV1|1|I|5E^5E-512^A^METHODIST||||5678123^Underwood^David^R^^^MD^L^^^NPI|||MED||||1|||5678123^Underwood^David^R^^^MD^L^^^NPI|IN||||||||||||||||||METHODIST||A|||20250801180000
ORC|NW|RX20250802001^MLB||GRP20250802001^MLB|||||20250802092500|||5678123^Underwood^David^R^^^MD^L^^^NPI||^WPN^PH^^1^901^5551600|||||METHODIST_LB^Methodist Le Bonheur Healthcare^L|1265 Union Ave^^Memphis^TN^38104
OBR|1|RX20250802001^MLB||RX^Pharmacy Order^L|||20250802093000||||A|||||5678123^Underwood^David^R^^^MD^L^^^NPI
RXO|313782^Vancomycin 1000 mg IV^RxNorm||1000|mg^milligrams^ISO+|||A|||||1000|mg|||||IVPB^IV Piggyback^HL70162
RXR|IV^Intravenous^HL70162|LA^Left Arm^HL70163
RXO|310429^Piperacillin-tazobactam 3.375g IV^RxNorm||3.375|g^grams^ISO+|||A|||||3375|mg|||||IVPB^IV Piggyback^HL70162
RXR|IV^Intravenous^HL70162|RA^Right Arm^HL70163
```

---

## 19. MDM^T02 - Discharge summary from Ascension Saint Thomas Rutherford

```
MSH|^~\&|RHAPSODY|ASTR_TRANS|MEDITECH_DOC|ASCENSION_STR|20250630112000||MDM^T02^MDM_T02|MSG20250630112000019|P|2.5.1|||AL|NE||ASCII|||
EVN|T02|20250630111500
PID|1||ASTR2256789^^^ASTR^MR||Stafford^Margaret^Ann^^Mrs.||19450712|F||2106-3^White^CDCREC|2089 Medical Center Pkwy^^Murfreesboro^TN^37129^US||^PRN^PH^^1^615^5551876||eng^English^HL70296|W^Widowed^HL70002|||349-16-2780|||N^Non-Hispanic^HL70189
PV1|1|I|MED^MED-108^A^ASTR||||6781234^Desai^Amit^K^^^MD^L^^^NPI|||MED||||1|||6781234^Desai^Amit^K^^^MD^L^^^NPI|IN||||||||||||||||||ASTR||A|||20250625140000
TXA|1|DS^Discharge Summary^HL70270|TX^Text^HL70191|20250630110000||20250630112000|||||6781234^Desai^Amit^K^^^MD^L^^^NPI|DOC20250630108^ASTR|||AU^Authenticated^HL70271||||
OBX|1|TX|18842-5^Discharge summary^LN||DISCHARGE SUMMARY~Patient: Stafford, Margaret A~MRN: ASTR2256789~Admission Date: 06/25/2025~Discharge Date: 06/30/2025~Attending: Amit K. Desai, MD~Admitting Diagnosis: Community-acquired pneumonia~Hospital Course: 80-year-old female admitted with productive cough, fever 101.8F, and right lower lobe infiltrate on CXR. Started on ceftriaxone and azithromycin. Blood cultures negative. Sputum culture grew Streptococcus pneumoniae susceptible to penicillin. Narrowed to amoxicillin on day 3. Oxygen requirement resolved by day 4. Ambulating independently by day 5.~Discharge Diagnosis: Community-acquired pneumonia, Streptococcus pneumoniae~Discharge Medications: Amoxicillin 875mg BID x 5 days, Guaifenesin 600mg BID PRN~Follow-up: PCP in 7 days~Condition at Discharge: Stable, improved||||||F|||20250630110000||6781234^Desai^Amit^K^^^MD^L^^^NPI
```

---

## 20. ACK - Negative acknowledgment from Tennessee Hospital Association data exchange

```
MSH|^~\&|THA_HIE|TN_HOSP_ASSOC|RHAPSODY|ERLANGER_ADT|20250419200100||ACK^A01^ACK|ACK20250419200100020|P|2.5.1|||AL|NE||ASCII|||
MSA|AE|MSG20250419195800033|Message rejected: patient identifier validation failed
ERR||PID^1^3^4|101^Required field missing^HL70357|E|2^Required field^HL70533||||Patient MRN format does not match expected pattern [A-Z]{3}[0-9]{7}
ERR||PV1^1^7^1|103^Table value not found^HL70357|W|1^Informational^HL70533||||Attending physician NPI 9999999 not found in provider registry
```
