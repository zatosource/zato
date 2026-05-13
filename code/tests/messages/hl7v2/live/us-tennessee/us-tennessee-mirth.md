# Mirth Connect (NextGen) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to Vanderbilt University Medical Center

```
MSH|^~\&|MIRTH|VUMC_ADT|EPIC_ADM|VUMC|20250312083022||ADT^A01^ADT_A01|MSG20250312083022001|P|2.5.1|||AL|NE
EVN|A01|20250312082500|||LBRYANT^Bryant^Laura^^^RN
PID|1||MRN9928374^^^VUMC^MR~331-82-4917^^^USSSA^SS||Hawkins^Darnell^Tyrone||19780415|M||2054-5^Black or African American^CDCREC|1422 Music Row^^Nashville^TN^37203^US||^PRN^PH^^1^615^4429187|^WPN^PH^^1^615^4429302||M^Married^HL70002|||331-82-4917|||N^Not Hispanic or Latino^HL70189
PD1|||Vanderbilt University Medical Center^^12345|1938274650^Ellison^Brenda^R^^^MD
NK1|1|Hawkins^Tamara^L|SPO^Spouse^HL70063|1422 Music Row^^Nashville^TN^37203^US|^PRN^PH^^1^615^4429188
PV1|1|I|4NORTH^4012^01^VUMC^^^^4NORTH||||4821937560^Okafor^Chinedu^A^^^MD^^^NPI|4821937560^Okafor^Chinedu^A^^^MD^^^NPI|||MED||||ADM||VIP|||||||||||||||||||VUMC|||20250312082500
PV2|||^Acute exacerbation of congestive heart failure|||||||2||||||||||||N
DG1|1||I5023^Acute on chronic systolic heart failure^ICD10|||A
IN1|1|BCBST001|BlueCross BlueShield of Tennessee|1 Cameron Hill Circle^^Chattanooga^TN^37402|^PRN^PH^^1^423^7710200|||||20240101||||Hawkins^Darnell^Tyrone|SEL^Self^HL70063|19780415|1422 Music Row^^Nashville^TN^37203^US|||1||||||||||||||TNB449218763
AL1|1|DA|70618^Penicillin^RxNorm|MO^Moderate^HL70128|Rash and urticaria
```

---

## 2. ORU^R01 - Lab result with embedded PDF report (base64 ED segment)

```
MSH|^~\&|NEXTGEN_CONNECT|METHODIST_GERMANTOWN|SUNQUEST_LAB|MLH|20250415102233||ORU^R01^ORU_R01|MSG20250415102233445|P|2.5.1|||AL|NE
PID|1||PT443829^^^MLH^MR||Caldwell^Sharon^Renee||19651103|F||2106-3^White^CDCREC|8834 Poplar Ave^^Germantown^TN^38138^US||^PRN^PH^^1^901^6627184||||||||N^Not Hispanic or Latino^HL70189
PV1|1|O|LAB^^^MLH||||2847193056^Yoon^David^H^^^MD^^^NPI||||||||REF||||||||||||||||||||||MLH|||20250415090000
ORC|RE|ORD884721^MIRTH|LAB884721^SUNQUEST||CM||||20250415090000|||2847193056^Yoon^David^H^^^MD^^^NPI
OBR|1|ORD884721^MIRTH|LAB884721^SUNQUEST|24331-1^Comprehensive metabolic panel^LN|||20250415085500|||||||||2847193056^Yoon^David^H^^^MD^^^NPI||||||20250415101500|||F
OBX|1|NM|2345-7^Glucose^LN||142|mg/dL|70-99|HH|||F|||20250415101500
OBX|2|NM|3094-0^BUN^LN||28|mg/dL|7-20|H|||F|||20250415101500
OBX|3|NM|2160-0^Creatinine^LN||1.8|mg/dL|0.7-1.3|H|||F|||20250415101500
OBX|4|NM|2951-2^Sodium^LN||137|mmol/L|136-145||||F|||20250415101500
OBX|5|NM|2823-3^Potassium^LN||4.2|mmol/L|3.5-5.1||||F|||20250415101500
OBX|6|ED|PDF^Lab Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSA+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNjMgMDAwMDAgbiAKMDAwMDAwMDEyMCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDQgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjIxNQolJUVPRgo=|||F|||20250415101500
```

---

## 3. ADT^A04 - Patient registration at Erlanger Health System

```
MSH|^~\&|MIRTH|ERLANGER_REG|CERNER_MIL|ERLANGER|20250508141530||ADT^A04^ADT_A01|MSG20250508141530887|P|2.5.1|||AL|NE
EVN|A04|20250508141500|||KMORRIS^Morris^Karen^^^RN
PID|1||MRN6643201^^^ERL^MR||Tran^Minh^Edward||19900822|M||2028-9^Asian^CDCREC|3301 Broad St^^Chattanooga^TN^37408^US||^PRN^PH^^1^423^9384172||||||||N^Not Hispanic or Latino^HL70189
PD1|||Erlanger Health System^^67890|6193742580^Reeves^Jonathan^P^^^MD
PV1|1|O|ERGEN^EXAM04^01^ERL||||6193742580^Reeves^Jonathan^P^^^MD|||GEN||||WALKIN||||||||||||||||||||||ERL|||20250508141500
PV2|||^Annual physical examination
IN1|1|UHC_TN01|UnitedHealthcare of Tennessee|9900 Brentwood Blvd^^Brentwood^TN^37027|||||||||||||SEL^Self^HL70063|19900822|3301 Broad St^^Chattanooga^TN^37408^US|||1||||||||||||||UHC5538291744
```

---

## 4. ORM^O01 - Radiology order from Baptist Memorial Hospital Memphis

```
MSH|^~\&|NEXTGEN_CONNECT|BAPTIST_MEM|GE_RIS|BAPTIST_RAD|20250221155045||ORM^O01^ORM_O01|MSG20250221155045332|P|2.5.1|||AL|NE
PID|1||PT992104^^^BMH^MR||Gentry^Tamika^Rochelle||19830619|F||2054-5^Black or African American^CDCREC|4455 Elvis Presley Blvd^^Memphis^TN^38116^US||^PRN^PH^^1^901^7743982||||||||N^Not Hispanic or Latino^HL70189
PV1|1|I|3WEST^3201^02^BMH||||3917245680^Whitfield^Daniel^R^^^MD^^^NPI||||||||ADM|||||||||||||||||||||||BMH|||20250220180000
ORC|NW|ORD771234^MIRTH||GRP771234|||||20250221155000|||3917245680^Whitfield^Daniel^R^^^MD^^^NPI
OBR|1|ORD771234^MIRTH||71260^CT Chest with contrast^CPT|||20250221160000||||||||3917245680^Whitfield^Daniel^R^^^MD^^^NPI||||||||||1^^^20250221160000^^R||||||||||||||STAT^Stat^HL70078
DG1|1||J18.9^Pneumonia, unspecified organism^ICD10|||A
```

---

## 5. VXU^V04 - Immunization update to Tennessee Immunization Information System (TennIIS)

```
MSH|^~\&|MIRTH|LECONTE_MED|TENNIIS|TNDOH|20250610093012||VXU^V04^VXU_V04|MSG20250610093012773|P|2.5.1|||ER|AL
PID|1||MRN2234567^^^LMC^MR||Bowman^Ellie^Claire||20230115|F||2106-3^White^CDCREC|1520 Middle Creek Rd^^Sevierville^TN^37862^US||^PRN^PH^^1^865^2214738||||||||N^Not Hispanic or Latino^HL70189
NK1|1|Bowman^Megan^Diane|MTH^Mother^HL70063|1520 Middle Creek Rd^^Sevierville^TN^37862^US|^PRN^PH^^1^865^2214738
PV1|1|R|PED^^^LMC||||7284915360^Hodges^Valerie^N^^^MD^^^NPI
ORC|RE|IMM882341^MIRTH||||||||||7284915360^Hodges^Valerie^N^^^MD^^^NPI
RXA|0|1|20250610091500|20250610091500|21^Varicella^CVX|0.5|mL^milliliter^UCUM||00^New Record^NIP001|8821347^Stanton^Pamela^^^RN|^^^LeConte Medical Center||||M3847K|20260301|MSD^Merck Sharp and Dohme^MVX
RXR|SC^Subcutaneous^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC Eligible - Medicaid/Medicaid Managed Care^HL70064||||||F
OBX|2|DT|29768-9^Date vaccine information statement published^LN||20191022||||||F
OBX|3|DT|29769-7^Date vaccine information statement presented^LN||20250610||||||F
```

---

## 6. SIU^S12 - Appointment notification from Blount Memorial Hospital

```
MSH|^~\&|MIRTH|BLOUNT_MEM|ATHENA_SCHED|BLOUNT|20250718143022||SIU^S12^SIU_S12|MSG20250718143022119|P|2.5.1|||AL|NE
SCH|APT448823^MIRTH|||||FOLLOWUP^Follow-up Visit^LOCAL||30|MIN^Minutes^ISO31||^^^20250725100000^20250725103000|||||1847293650^Kirkland^Nathan^W^^^MD^^^NPI|^PRN^PH^^1^865^9924471|||||BOOKED
PID|1||MRN3378291^^^BMH^MR||Massey^Harold^Eugene||19560412|M||2106-3^White^CDCREC|2208 Tuckaleechee Pike^^Maryville^TN^37803^US||^PRN^PH^^1^865^3381942||||||||N^Not Hispanic or Latino^HL70189
PV1|1|O|CARD^EXAM02^01^BMH||||1847293650^Kirkland^Nathan^W^^^MD^^^NPI|||CAR||||FOLLOWUP
RGS|1||CARDIOLOGY
AIG|1||1847293650^Kirkland^Nathan^W^^^MD^^^NPI
AIL|1||CARD^EXAM02^01^BMH
```

---

## 7. ORU^R01 - Pathology result from UT Medical Center Knoxville

```
MSH|^~\&|NEXTGEN_CONNECT|UTMC_PATH|EPIC_LAB|UTMC|20250303091244||ORU^R01^ORU_R01|MSG20250303091244558|P|2.5.1|||AL|NE
PID|1||PT667234^^^UTMC^MR||Pickett^Virginia^Lorraine||19470916|F||2106-3^White^CDCREC|5501 Kingston Pike^^Knoxville^TN^37919^US||^PRN^PH^^1^865^7743291||||||||N^Not Hispanic or Latino^HL70189
PV1|1|I|SURG^5102^01^UTMC||||5029381746^Hargrove^Mitchell^B^^^MD^^^NPI||||||||ADM|||||||||||||||||||||||UTMC|||20250228100000
ORC|RE|ORD556721^MIRTH|PATH556721^UTMC_PATH||CM||||20250228120000|||5029381746^Hargrove^Mitchell^B^^^MD^^^NPI
OBR|1|ORD556721^MIRTH|PATH556721^UTMC_PATH|88305^Surgical pathology^CPT|||20250228120000|||||||||5029381746^Hargrove^Mitchell^B^^^MD^^^NPI||||||20250303090000|||F
OBX|1|FT|22637-3^Pathology report final diagnosis^LN||FINAL DIAGNOSIS:\.br\\.br\Left breast, excisional biopsy:\.br\- Invasive ductal carcinoma, grade 2\.br\- Tumor size: 1.8 cm\.br\- Margins: Negative (closest margin 0.4 cm, anterior)\.br\- Lymphovascular invasion: Not identified\.br\- ER: Positive (95%), PR: Positive (72%), HER2: Negative (1+)\.br\- Ki-67: 18%\.br\\.br\COMMENT: Recommend sentinel lymph node biopsy and oncology consultation.||||||F|||20250303090000
OBX|2|CE|33731-4^Histology type^LN||8500/3^Infiltrating duct carcinoma NOS^ICD-O-3||||||F|||20250303090000
```

---

## 8. ADT^A08 - Patient information update at Cookeville Regional Medical Center

```
MSH|^~\&|MIRTH|CRMC_REG|MEDITECH|CRMC|20250822160533||ADT^A08^ADT_A01|MSG20250822160533209|P|2.5.1|||AL|NE
EVN|A08|20250822160500|||ABURNS^Burns^Ashley^^^REG
PID|1||MRN1198432^^^CRMC^MR||Ledford^Travis^Wayne||19640730|M||2106-3^White^CDCREC|445 S Walnut Ave^^Cookeville^TN^38501^US||^PRN^PH^^1^931^5478231|^WPN^PH^^1^931^5474410||S^Single^HL70002|||417-63-8295|||N^Not Hispanic or Latino^HL70189
PV1|1|I|ICU^ICU04^01^CRMC||||9384571026^Pham^Lien^T^^^MD^^^NPI||||||||ADM|||||||||||||||||||||||CRMC|||20250820223000
IN1|1|TNCARE01|TennCare (Amerigroup)|22 Century Blvd Ste 220^^Nashville^TN^37214|^PRN^PH^^1^800^5551234|||||20250101||||Ledford^Travis^Wayne|SEL^Self^HL70063|19640730|445 S Walnut Ave^^Cookeville^TN^38501^US|||1||||||||||||||AGP771942038
IN2|||||||||||||||||||||||||||||||||||||||||||||||||||||||AMERIGROUP
```

---

## 9. MDM^T02 - Clinical document notification from Parkwest Medical Center

```
MSH|^~\&|NEXTGEN_CONNECT|PARKWEST|XDS_REPO|COVENANT|20250410122015||MDM^T02^MDM_T02|MSG20250410122015667|P|2.5.1|||AL|NE
EVN|T02|20250410122000
PID|1||PT885512^^^PWMC^MR||Booker^Tanya^Renee||19720308|F||2054-5^Black or African American^CDCREC|7449 Middlebrook Pike^^Knoxville^TN^37909^US||^PRN^PH^^1^865^2219847||||||||N^Not Hispanic or Latino^HL70189
PV1|1|I|TELE^2204^01^PWMC||||8274193056^Kapoor^Rohan^S^^^MD^^^NPI||||||||ADM|||||||||||||||||||||||PWMC|||20250408140000
TXA|1|HP^History and Physical^HL70270|TX^Text^HL70191|20250408160000||20250410120000|||||8274193056^Kapoor^Rohan^S^^^MD^^^NPI||DOC88512^PWMC|||||AU^Authenticated^HL70271
OBX|1|ST|11506-3^Progress note^LN||HISTORY OF PRESENT ILLNESS: 52-year-old female presenting with 3-day history of progressive dyspnea on exertion, orthopnea, and bilateral lower extremity edema. Patient reports medication non-compliance for past 2 weeks.||||||F
OBX|2|ST|11506-3^Progress note^LN||ASSESSMENT AND PLAN: Acute decompensated heart failure, NYHA Class III. Will initiate IV diuresis with furosemide 40mg BID, strict I/Os, daily weights, cardiology consultation, and echocardiogram.||||||F
```

---

## 10. ACK - Acknowledgment from Tennessee Department of Health

```
MSH|^~\&|TENNIIS|TNDOH|MIRTH|LECONTE_MED|20250610093015||ACK^V04^ACK|ACK20250610093015001|P|2.5.1|||AL|NE
MSA|AA|MSG20250610093012773||Message accepted successfully
```

---

## 11. ORU^R01 - Microbiology result from Maury Regional Health

```
MSH|^~\&|MIRTH|MAURY_LAB|CPSI_HIS|MAURY|20250519104522||ORU^R01^ORU_R01|MSG20250519104522884|P|2.5.1|||AL|NE
PID|1||MRN4456712^^^MRH^MR||Sutton^Terrence^Marcus||19850214|M||2054-5^Black or African American^CDCREC|1200 Trotwood Ave^^Columbia^TN^38401^US||^PRN^PH^^1^931^8843291||||||||N^Not Hispanic or Latino^HL70189
PV1|1|I|MED^2108^01^MRH||||6183724950^Kwon^Hye^Jin^^^MD^^^NPI||||||||ADM|||||||||||||||||||||||MRH|||20250517060000
ORC|RE|ORD339421^MIRTH|MICRO339421^MAURY_LAB||CM||||20250517070000|||6183724950^Kwon^Hye^Jin^^^MD^^^NPI
OBR|1|ORD339421^MIRTH|MICRO339421^MAURY_LAB|87040^Blood Culture^CPT|||20250517065500|||||||||6183724950^Kwon^Hye^Jin^^^MD^^^NPI||||||20250519100000|||F
OBX|1|CE|600-7^Bacteria identified^LN||MRSA^Methicillin resistant Staphylococcus aureus^LOCAL||||||F|||20250519100000
OBX|2|ST|18769-0^Microbial susceptibility tests^LN||Vancomycin: S (MIC 1.0 mcg/mL); Linezolid: S (MIC 2.0 mcg/mL); Daptomycin: S (MIC 0.5 mcg/mL); TMP-SMX: S; Doxycycline: S; Clindamycin: R||||||F|||20250519100000
OBX|3|ST|19146-0^Reference lab^LN||Confirmed by Quest Diagnostics Nashville||||||F|||20250519100000
```

---

## 12. ADT^A01 - Admission to Tristar Centennial Medical Center

```
MSH|^~\&|MIRTH|TRISTAR_CENT|MEDITECH|TRISTAR|20250127071845||ADT^A01^ADT_A01|MSG20250127071845442|P|2.5.1|||AL|NE
EVN|A01|20250127071500|||MRODRIGUEZ^Rodriguez^Maria^^^RN
PID|1||MRN7782341^^^TSC^MR||Cantrell^Ashley^Nicole||19910503|F||2106-3^White^CDCREC|2300 Patterson St^^Nashville^TN^37203^US||^PRN^PH^^1^615^8827134|^WPN^PH^^1^629^8821190||M^Married^HL70002|||548-21-7293|||N^Not Hispanic or Latino^HL70189
NK1|1|Cantrell^Brandon^M|SPO^Spouse^HL70063|2300 Patterson St^^Nashville^TN^37203^US|^PRN^PH^^1^615^8827135
PV1|1|I|LDRP^LD02^01^TSC^^^^LDRP||||7391824560^Banks^Keisha^N^^^MD^^^NPI|7391824560^Banks^Keisha^N^^^MD^^^NPI||OBG||||ADM||||||||||||||||||||||TSC|||20250127071500
PV2|||^Term pregnancy in labor
DG1|1||O80^Encounter for full-term uncomplicated delivery^ICD10|||A
IN1|1|AETNA_TN|Aetna Better Health of Tennessee|1 South Wacker Dr^^Chicago^IL^60606|^PRN^PH^^1^800^5552273|||||20240601||||Cantrell^Ashley^Nicole|SEL^Self^HL70063|19910503|2300 Patterson St^^Nashville^TN^37203^US|||1||||||||||||||AET3319427861
```

---

## 13. ORM^O01 - Lab order from Holston Valley Medical Center

```
MSH|^~\&|NEXTGEN_CONNECT|HOLSTON_VAL|SUNQUEST|BALLAD_LAB|20250904081233||ORM^O01^ORM_O01|MSG20250904081233556|P|2.5.1|||AL|NE
PID|1||PT224689^^^HVMC^MR||Hensley^Gerald^Wayne||19530118|M||2106-3^White^CDCREC|1078 W Elk Ave^^Elizabethton^TN^37643^US||^PRN^PH^^1^423^5471829||||||||N^Not Hispanic or Latino^HL70189
PV1|1|O|LAB^^^HVMC||||4928371560^Ballard^Christine^E^^^MD^^^NPI||||||||REF|||||||||||||||||||||||HVMC|||20250904080000
ORC|NW|ORD998132^MIRTH||GRP998132|||||20250904081200|||4928371560^Ballard^Christine^E^^^MD^^^NPI
OBR|1|ORD998132^MIRTH||83036^Hemoglobin A1c^CPT|||20250904083000||||||||4928371560^Ballard^Christine^E^^^MD^^^NPI
OBR|2|ORD998132^MIRTH||80053^Comprehensive metabolic panel^CPT|||20250904083000||||||||4928371560^Ballard^Christine^E^^^MD^^^NPI
OBR|3|ORD998132^MIRTH||85025^Complete blood count with differential^CPT|||20250904083000||||||||4928371560^Ballard^Christine^E^^^MD^^^NPI
DG1|1||E11.65^Type 2 diabetes mellitus with hyperglycemia^ICD10|||A
```

---

## 14. ORU^R01 - Radiology result with embedded DICOM reference from Jackson-Madison County General

```
MSH|^~\&|MIRTH|JMCGH_RAD|PACS_FUJI|WTH|20250613144509||ORU^R01^ORU_R01|MSG20250613144509773|P|2.5.1|||AL|NE
PID|1||MRN8893214^^^JMCGH^MR||Whitmore^Jerome^Lamar||19680721|M||2054-5^Black or African American^CDCREC|332 N Highland Ave^^Jackson^TN^38301^US||^PRN^PH^^1^731^4428193||||||||N^Not Hispanic or Latino^HL70189
PV1|1|E|ER^TRAUMA1^01^JMCGH||||2741938560^Doyle^Patrick^W^^^MD^^^NPI||||||||EMER|||||||||||||||||||||||JMCGH|||20250613130000
ORC|RE|ORD772345^MIRTH|RAD772345^JMCGH_RAD||CM||||20250613130500|||2741938560^Doyle^Patrick^W^^^MD^^^NPI
OBR|1|ORD772345^MIRTH|RAD772345^JMCGH_RAD|71045^Chest X-ray 2 views^CPT|||20250613131500|||||||||2741938560^Doyle^Patrick^W^^^MD^^^NPI||||||20250613143000|||F
OBX|1|FT|18748-4^Diagnostic imaging study^LN||FINDINGS: PA and lateral views of the chest. Heart size is mildly enlarged. Bibasilar atelectasis noted. No acute infiltrate or effusion. Mediastinal contours are normal. No pneumothorax.\.br\\.br\IMPRESSION: Cardiomegaly. No acute cardiopulmonary disease.||||||F|||20250613143000
OBX|2|CE|59776-5^Procedure findings^LN||RID1301^Cardiomegaly^RadLex||||||F|||20250613143000
```

---

## 15. VXU^V04 - Pediatric immunization from East Tennessee Children's Hospital

```
MSH|^~\&|MIRTH|ETCH_IMM|TENNIIS|TNDOH|20250814101522||VXU^V04^VXU_V04|MSG20250814101522334|P|2.5.1|||ER|AL
PID|1||MRN1123789^^^ETCH^MR||Guerrero^Valentina^Isabel||20240305|F||2106-3^White^CDCREC|4412 Chapman Hwy^^Knoxville^TN^37920^US||^PRN^PH^^1^865^9912847||||||||2135-2^Hispanic or Latino^HL70189
NK1|1|Guerrero^Lucia^Maria|MTH^Mother^HL70063|4412 Chapman Hwy^^Knoxville^TN^37920^US|^PRN^PH^^1^865^9912847
PV1|1|R|PED^^^ETCH||||5038274190^Varma^Priya^S^^^MD^^^NPI
ORC|RE|IMM445231^MIRTH||||||||||5038274190^Varma^Priya^S^^^MD^^^NPI
RXA|0|1|20250814100000|20250814100000|110^DTaP-IPV-Hep B^CVX|0.5|mL^milliliter^UCUM||00^New Record^NIP001|7291834^Norris^Beth^^^RN|^^^East Tennessee Childrens Hospital||||U3892A|20260501|GSK^GlaxoSmithKline^MVX
RXR|IM^Intramuscular^HL70162|RT^Right Thigh^HL70163
ORC|RE|IMM445232^MIRTH||||||||||5038274190^Varma^Priya^S^^^MD^^^NPI
RXA|0|1|20250814100200|20250814100200|133^PCV13^CVX|0.5|mL^milliliter^UCUM||00^New Record^NIP001|7291834^Norris^Beth^^^RN|^^^East Tennessee Childrens Hospital||||W2847B|20260215|PFR^Pfizer^MVX
RXR|IM^Intramuscular^HL70162|LT^Left Thigh^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V02^VFC Eligible - Medicaid/Medicaid Managed Care^HL70064||||||F
```

---

## 16. MDM^T02 - Discharge summary with embedded CDA document (base64 ED segment)

```
MSH|^~\&|NEXTGEN_CONNECT|HENDERSON_CTY|XDS_REG|WTN_HIE|20250922153044||MDM^T02^MDM_T02|MSG20250922153044891|P|2.5.1|||AL|NE
EVN|T02|20250922153000
PID|1||PT334587^^^HCMC^MR||Vickers^Opal^Louise||19430525|F||2106-3^White^CDCREC|78 Hospital Dr^^Lexington^TN^38351^US||^PRN^PH^^1^731^6629104||||||||N^Not Hispanic or Latino^HL70189
PV1|1|I|MED^108^01^HCMC||||8193742560^Crowley^Alan^T^^^MD^^^NPI||||||||ADM|||||||||||||||||||||||HCMC|||20250918090000
TXA|1|DS^Discharge Summary^HL70270|AP^Application^HL70191|20250922140000||20250922150000|||||8193742560^Crowley^Alan^T^^^MD^^^NPI||DOC33458^HCMC|||||AU^Authenticated^HL70271
OBX|1|ED|18842-5^Discharge summary^LN||^text^xml^Base64^PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIj4KPHJlYWxtQ29kZSBjb2RlPSJVUyIvPgo8dHlwZUlkIHJvb3Q9IjIuMTYuODQwLjEuMTEzODgzLjEuMyIgZXh0ZW5zaW9uPSJQT0NEX0hEMDAwMDQwIi8+Cjx0ZW1wbGF0ZUlkIHJvb3Q9IjIuMTYuODQwLjEuMTEzODgzLjEwLjIwIi8+CjxpZCByb290PSIxLjIuMy40LjUuNi43Ii8+Cjxjb2RlIGNvZGU9IjE4ODQyLTUiIGNvZGVTeXN0ZW09IjIuMTYuODQwLjEuMTEzODgzLjYuMSIgZGlzcGxheU5hbWU9IkRpc2NoYXJnZSBTdW1tYXJ5Ii8+Cjx0aXRsZT5EaXNjaGFyZ2UgU3VtbWFyeTwvdGl0bGU+CjxlZmZlY3RpdmVUaW1lIHZhbHVlPSIyMDI1MDkyMjE0MDAwMCIvPgo8L0NsaW5pY2FsRG9jdW1lbnQ+|||F|||20250922150000
OBX|2|ST|11506-3^Progress note^LN||DISCHARGE DIAGNOSIS: Community-acquired pneumonia, resolved. Acute kidney injury, resolved. TYPE 2 DM, A1c 7.8%. DISPOSITION: Home with home health. Follow-up with PCP in 7 days.||||||F|||20250922150000
```

---

## 17. ADT^A08 - Insurance update from Williamson Medical Center

```
MSH|^~\&|MIRTH|WMC_REG|CERNER|WMC|20250205111244||ADT^A08^ADT_A01|MSG20250205111244553|P|2.5.1|||AL|NE
EVN|A08|20250205111200|||JHARRIS^Harris^Julie^^^REG
PID|1||MRN5564321^^^WMC^MR||Holcomb^Nathan^Gregory||19770912|M||2106-3^White^CDCREC|1009 Mallory Ln^^Franklin^TN^37067^US||^PRN^PH^^1^615^7724198|^WPN^PH^^1^629^7729012||M^Married^HL70002|||482-37-6194|||N^Not Hispanic or Latino^HL70189
PV1|1|O|ORTH^EXAM01^01^WMC||||3819274560^Chambers^Keith^R^^^MD^^^NPI|||ORT||||FOLLOWUP|||||||||||||||||||||||WMC|||20250205110000
IN1|1|CIGNA_TN|Cigna Healthcare of Tennessee|900 Cottage Grove Rd^^Bloomfield^CT^06002|^PRN^PH^^1^800^5552463|||||20250101||||Holcomb^Nathan^Gregory|SEL^Self^HL70063|19770912|1009 Mallory Ln^^Franklin^TN^37067^US|||1||||||||||||||CIG559284731
IN2|||||||||||||||||||||||||||||||||||||||||||||||||||||||CIGNA HEALTHSPRING
```

---

## 18. ORU^R01 - Cardiac catheterization result from Tennova Healthcare Clarksville

```
MSH|^~\&|NEXTGEN_CONNECT|TENNOVA_CLK|HEMODYNAMICS|TENNOVA|20250729163822||ORU^R01^ORU_R01|MSG20250729163822447|P|2.5.1|||AL|NE
PID|1||PT118923^^^TNVA^MR||Sellers^Bobby^Raymond||19590602|M||2106-3^White^CDCREC|1880 Fort Campbell Blvd^^Clarksville^TN^37042^US||^PRN^PH^^1^931^7724819||||||||N^Not Hispanic or Latino^HL70189
PV1|1|I|CATH^CL01^01^TNVA||||6284193750^Mehta^Sanjay^K^^^MD^^^NPI||||||||ADM|||||||||||||||||||||||TNVA|||20250729080000
ORC|RE|ORD447821^MIRTH|CATH447821^TENNOVA_CLK||CM||||20250729100000|||6284193750^Mehta^Sanjay^K^^^MD^^^NPI
OBR|1|ORD447821^MIRTH|CATH447821^TENNOVA_CLK|93458^Left heart catheterization^CPT|||20250729100000|||||||||6284193750^Mehta^Sanjay^K^^^MD^^^NPI||||||20250729160000|||F
OBX|1|FT|18745-0^Cardiac catheterization study^LN||PROCEDURE: Left heart catheterization with coronary angiography\.br\\.br\FINDINGS:\.br\- Left main: Normal\.br\- LAD: 85% stenosis in mid segment\.br\- LCx: 40% stenosis in proximal segment\.br\- RCA: Normal\.br\- LVEF: 50%\.br\- LVEDP: 18 mmHg\.br\\.br\RECOMMENDATION: PCI to mid-LAD. Patient consents to proceed. Interventional cardiology consulted.||||||F|||20250729160000
OBX|2|NM|8867-4^Heart rate^LN||72|bpm^beats per minute^UCUM|60-100||||F|||20250729160000
OBX|3|NM|8480-6^Systolic blood pressure^LN||148|mm[Hg]^millimeters of mercury^UCUM|<140|H|||F|||20250729160000
```

---

## 19. SIU^S12 - Scheduling notification from Ascension Saint Thomas Rutherford

```
MSH|^~\&|MIRTH|ASTR_SCHED|ALLSCRIPTS|ASCENSION_TN|20250501090112||SIU^S12^SIU_S12|MSG20250501090112883|P|2.5.1|||AL|NE
SCH|APT992341^MIRTH|||||NEWSURG^New Surgical Consult^LOCAL||45|MIN^Minutes^ISO31||^^^20250508140000^20250508144500|||||4918273560^Ortega^Daniela^R^^^MD^^^NPI|^PRN^PH^^1^615^3384712|||||BOOKED
PID|1||MRN6678234^^^ASTR^MR||Fuentes^Andres^Rafael||19820417|M||2106-3^White^CDCREC|3300 Memorial Blvd^^Murfreesboro^TN^37129^US||^PRN^PH^^1^615^9917284||||||||2135-2^Hispanic or Latino^HL70189
PV1|1|O|SURG^CONS02^01^ASTR||||4918273560^Ortega^Daniela^R^^^MD^^^NPI|||GS||||NEWSURG
RGS|1||GENERAL SURGERY
AIG|1||4918273560^Ortega^Daniela^R^^^MD^^^NPI
AIL|1||SURG^CONS02^01^ASTR
AIP|1||4918273560^Ortega^Daniela^R^^^MD^^^NPI
```

---

## 20. ACK - Negative acknowledgment with error from Mirth router

```
MSH|^~\&|MIRTH|TN_ROUTER|ORIGINATING_SYS|JMCGH|20250613145012||ACK^O01^ACK|ACK20250613145012445|P|2.5.1|||AL|NE
MSA|AE|MSG20250613144200881|Required field PID-3 (Patient Identifier List) is empty
ERR||PID^1^3|101^Required field missing^HL70357|E||||Patient identifier is required for order processing
```
