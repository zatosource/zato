# Rhapsody Corepoint - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Admission to labor and delivery

```
MSH|^~\&|COREPOINT|SETON^2.16.840.1.113883.3.4401^ISO|ADT_RECV|TX_HIE|20260401080000||ADT^A01^ADT_A01|RHAP20260401080000001|P|2.5.1|||AL|NE
EVN|A01|20260401075500|||OBRN^Endicott^Lorraine^T^^^RN|20260401075500
PID|1||MRN50001^^^SETON^MR~841-73-2905^^^USSSA^SS||Villegas^Catalina^Renata^^Mrs.^||19940211|F||2106-3^White^CDCREC|2917 Guadalupe St^^Austin^TX^78705^US^H||^PRN^PH^^1^512^5559123|||M^Married^HL70002|||841-73-2905|||H^Hispanic or Latino^CDCREC
PD1|||Ascension Seton Medical Center^^^^NPI|1234500101^Dalrymple^Evelyn^R^^^MD^^^^NPI
NK1|1|Villegas^Marco^Antonio^^Mr.|SPO^Spouse^HL70063|2917 Guadalupe St^^Austin^TX^78705^US|^PRN^PH^^1^512^5559124||EC^Emergency Contact^HL70131
PV1|1|I|OB^2201^01^SETON^^^^N|U^Urgent^HL70007|||1234500101^Dalrymple^Evelyn^R^^^MD^^^^NPI|2345600202^Faulkner^Ingrid^A^^^MD^^^^NPI|OBG^Obstetrics^HL70069||||||R^Referral^HL70007|||||VN20260401001^^^SETON^VN|||||||||||||||||||||||||20260401075500
PV2|||^Active labor, 39 weeks gestational age
DG1|1||O80^Encounter for full-term uncomplicated delivery^I10||20260401|A
IN1|1|AETNA001|80314^Aetna|Aetna^^Dallas^TX^75201|||||AETGRP||||||Villegas^Catalina^Renata|SE^Self^HL70063|19940211|2917 Guadalupe St^^Austin^TX^78705^US|Y||1||||||||||||||AETPOL567890
```

---

## 2. ADT^A03 - Discharge from substance abuse treatment

```
MSH|^~\&|COREPOINT|UTHEALTH^2.16.840.1.113883.3.4402^ISO|ADT_RECV|TX_HIE|20260403141500||ADT^A03^ADT_A03|RHAP20260403141500002|P|2.5.1|||AL|NE
EVN|A03|20260403140000|||BHRN^Goodrich^Tamara^K^^^RN|20260403140000
PID|1||MRN50002^^^UTHEALTH^MR||Pemberton^Cedric^Lamont^^Mr.^||19850610|M||2054-5^Black or African American^CDCREC|4710 Bellaire Blvd^^Houston^TX^77401^US^H||^PRN^PH^^1^713^5553847|||D^Divorced^HL70002|||372-48-6193|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|BH^1205^01^UTHEALTH^^^^N|R^Routine^HL70007|||3456700303^Halstead^Norman^D^^^MD^^^^NPI||PSY^Psychiatry^HL70069||||||R^Referral^HL70007|||||VN20260324002^^^UTHEALTH^VN|||||||||||||||||||01^Discharged to home^HL70112||||20260324100000|20260403140000
DG1|1||F10.20^Alcohol dependence uncomplicated^I10||20260324|A
DG1|2||F32.1^Major depressive disorder single episode moderate^I10||20260324|A
```

---

## 3. ORU^R01 - Lipid panel results

```
MSH|^~\&|COREPOINT|SETON^2.16.840.1.113883.3.4401^ISO|LAB_RECV|TX_HIE|20260404100000||ORU^R01^ORU_R01|RHAP20260404100000003|P|2.5.1|||AL|NE
PID|1||MRN50003^^^SETON^MR||Harrington^Diane^Lucille^^Ms.^||19700815|F||2106-3^White^CDCREC|3200 Red River St^^Austin^TX^78705^US^H||^PRN^PH^^1^512^5554567|||S^Single^HL70002|||517-62-8034|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|LAB^0001^01^SETON^^^^N|R^Routine^HL70007|||4567800404^Kimball^Patricia^B^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260404003^^^SETON^VN
ORC|RE|ORD50003^RHAP|FIL50003^LAB||CM^Complete^HL70038|||20260404070000|||4567800404^Kimball^Patricia^B^^^MD^^^^NPI
OBR|1|ORD50003^RHAP|FIL50003^LAB|57698-3^Lipid panel^LN|||20260404070000|||||||||4567800404^Kimball^Patricia^B^^^MD^^^^NPI||||||20260404093000|||F
OBX|1|NM|2093-3^Total cholesterol [Mass/volume] in Serum or Plasma^LN||238|mg/dL^milligrams per deciliter^UCUM|<200|H|||F|||20260404093000
OBX|2|NM|2571-8^Triglycerides [Mass/volume] in Serum or Plasma^LN||165|mg/dL^milligrams per deciliter^UCUM|<150|H|||F|||20260404093000
OBX|3|NM|2085-9^HDL cholesterol [Mass/volume] in Serum or Plasma^LN||52|mg/dL^milligrams per deciliter^UCUM|>40|N|||F|||20260404093000
OBX|4|NM|13457-7^LDL cholesterol calc [Mass/volume] in Serum or Plasma^LN||153|mg/dL^milligrams per deciliter^UCUM|<100|H|||F|||20260404093000
OBX|5|NM|13458-5^VLDL cholesterol calc [Mass/volume] in Serum or Plasma^LN||33|mg/dL^milligrams per deciliter^UCUM|5-40|N|||F|||20260404093000
```

---

## 4. ORM^O01 - Colonoscopy procedure order

```
MSH|^~\&|COREPOINT|UTHEALTH^2.16.840.1.113883.3.4402^ISO|ENDO_RECV|TX_HIE|20260405100000||ORM^O01^ORM_O01|RHAP20260405100000004|P|2.5.1|||AL|NE
PID|1||MRN50004^^^UTHEALTH^MR||Zarate^Emilio^Ricardo^^Mr.^||19720328|M||2106-3^White^CDCREC|8502 Katy Fwy^^Houston^TX^77024^US^H||^PRN^PH^^1^713^5558901|||M^Married^HL70002|||609-71-4823|||H^Hispanic or Latino^CDCREC
PV1|1|O|GI^0002^01^UTHEALTH^^^^N|R^Routine^HL70007|||5678900505^Lockwood^Sandra^E^^^MD^^^^NPI||GI^Gastroenterology^HL70069||||||||||VN20260405004^^^UTHEALTH^VN
ORC|NW|ORD50004^RHAP||GRP50004^RHAP|||||20260405093000|||5678900505^Lockwood^Sandra^E^^^MD^^^^NPI|||||UTHEALTH^UT Health Houston
OBR|1|ORD50004^RHAP||45378^Colonoscopy diagnostic^CPT4|||20260405093000||||||||5678900505^Lockwood^Sandra^E^^^MD^^^^NPI||||||||||1^Routine^HL70065
DG1|1||Z12.11^Encounter for screening for malignant neoplasm of colon^I10||20260405|A
NTE|1||Age 53, average risk. Family history of colon cancer in father at age 68. Patient completed bowel prep.
```

---

## 5. ORU^R01 - Spirometry results with embedded PDF (ED datatype)

```
MSH|^~\&|COREPOINT|SETON^2.16.840.1.113883.3.4401^ISO|PFT_RECV|TX_HIE|20260406150000||ORU^R01^ORU_R01|RHAP20260406150000005|P|2.5.1|||AL|NE
PID|1||MRN50005^^^SETON^MR||Montague^Russell^Vernon^^Mr.^||19550212|M||2106-3^White^CDCREC|1100 W 34th St^^Austin^TX^78705^US^H||^PRN^PH^^1^512^5553201|||M^Married^HL70002|||734-85-1267|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|PUL^0003^01^SETON^^^^N|R^Routine^HL70007|||6789000606^Prescott^Steven^R^^^MD^^^^NPI||PUL^Pulmonology^HL70069||||||||||VN20260406005^^^SETON^VN
ORC|RE|ORD50005^RHAP|FIL50005^PFT||CM^Complete^HL70038|||20260406130000|||6789000606^Prescott^Steven^R^^^MD^^^^NPI
OBR|1|ORD50005^RHAP|FIL50005^PFT|94010^Spirometry including graphic record^CPT4|||20260406130000|||||||||6789000606^Prescott^Steven^R^^^MD^^^^NPI||||||20260406145000|||F
OBX|1|NM|19868-9^FEV1 measured^LN||2.1|L^liters^UCUM|>2.5|L|||F|||20260406145000
OBX|2|NM|19876-2^FVC measured^LN||3.8|L^liters^UCUM|>3.5|N|||F|||20260406145000
OBX|3|NM|19926-5^FEV1/FVC^LN||55.3|%^percent^UCUM|>70|L|||F|||20260406145000
OBX|4|FT|94010^Spirometry interpretation^L||INTERPRETATION:\.br\Obstructive pattern with reduced FEV1/FVC ratio.\.br\FEV1 at 65% of predicted.\.br\Consistent with moderate COPD.\.br\Recommend post-bronchodilator testing.||||||F|||20260406145000
OBX|5|ED|PDF^Spirometry Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxMzUKPj4Kc3RyZWFtCkJUCi9GMSAxNCBUZgoxMDAgNzAwIFRkCihTcGlyb21ldHJ5IFJlcG9ydCkgVGoKMCAtMjAgVGQKL0YxIDEwIFRmCihBc2NlbnNpb24gU2V0b24gTWVkaWNhbCBDZW50ZXIpIFRqCjAgLTIwIFRkCihQYXRpZW50OiBNb250YWd1ZSwgUnVzc2VsbCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago=||||||F|||20260406145000
```

---

## 6. ADT^A08 - Diagnosis update during inpatient stay

```
MSH|^~\&|COREPOINT|UTHEALTH^2.16.840.1.113883.3.4402^ISO|ADT_RECV|TX_HIE|20260407110000||ADT^A08^ADT_A01|RHAP20260407110000006|P|2.5.1|||AL|NE
EVN|A08|20260407105500|||MEDRN^Thornton^Jeanette^L^^^RN|20260407105500
PID|1||MRN50006^^^UTHEALTH^MR||Stafford^Terrence^Darnell^^Mr.^||19780821|M||2054-5^Black or African American^CDCREC|3400 Elgin St^^Houston^TX^77004^US^H||^PRN^PH^^1^832^5553890|||M^Married^HL70002|||483-96-7210|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|MED^4102^01^UTHEALTH^^^^N|E^Emergency^HL70007|||7890100707^Merriweather^Pamela^C^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260405006^^^UTHEALTH^VN
DG1|1||K85.9^Acute pancreatitis unspecified^I10||20260405|A
DG1|2||F10.20^Alcohol dependence uncomplicated^I10||20260405|A
DG1|3||E87.1^Hypo-osmolality and hyponatremia^I10||20260407|A
```

---

## 7. SIU^S12 - Dermatology appointment

```
MSH|^~\&|COREPOINT|SETON^2.16.840.1.113883.3.4401^ISO|SCHED_RECV|TX_HIE|20260408090000||SIU^S12^SIU_S12|RHAP20260408090000007|P|2.5.1|||AL|NE
SCH|APPT50007^RHAP||||||DERM^Dermatology Consultation^L|30^MIN|MIN^Minutes^ISO+|^^^20260415140000^^30^MIN|||||8901200808^Whitfield^Rebecca^J^^^MD^^^^NPI|^PRN^PH^^1^512^5556789|||||8901200808^Whitfield^Rebecca^J^^^MD^^^^NPI|||||Booked
PID|1||MRN50007^^^SETON^MR||Yoshida^Akiko^Mei^^Ms.^||19850503|F||2028-9^Asian^CDCREC|900 E 30th St^^Austin^TX^78705^US^H||^PRN^PH^^1^512^5554321|||S^Single^HL70002|||256-93-4018|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|DERM^0001^01^SETON^^^^N|R^Routine^HL70007|||8901200808^Whitfield^Rebecca^J^^^MD^^^^NPI||DER^Dermatology^HL70069||||||||||VN20260408007^^^SETON^VN
RGS|1||DERM_CLINIC
AIS|1||99203^Office visit new patient level 3^CPT4|20260415140000|||30^MIN|MIN^Minutes^ISO+||Confirmed
AIG|1||8901200808^Whitfield^Rebecca^J^^^MD^^^^NPI|||||20260415140000|||30^MIN
AIL|1||DERM^0001^01^SETON|||||20260415140000|||30^MIN
NTE|1||New patient. Multiple suspicious moles on back and arms. Family history of melanoma.
```

---

## 8. RDE^O11 - Insulin drip order for DKA

```
MSH|^~\&|COREPOINT|UTHEALTH^2.16.840.1.113883.3.4402^ISO|PHARM_RECV|TX_HIE|20260409020000||RDE^O11^RDE_O11|RHAP20260409020000008|P|2.5.1|||AL|NE
PID|1||MRN50008^^^UTHEALTH^MR||Redmond^Shanice^Elaine^^Ms.^||19910714|F||2054-5^Black or African American^CDCREC|8100 Cambridge St^^Houston^TX^77054^US^H||^PRN^PH^^1^713^5557012|||S^Single^HL70002|||615-28-9347|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|ICU^1003^01^UTHEALTH^^^^N|E^Emergency^HL70007|||9012300909^Ashworth^Marcus^T^^^MD^^^^NPI||CCM^Critical Care^HL70069||||||||||VN20260408008^^^UTHEALTH^VN
ORC|NW|ORD50008^RHAP||GRP50008^RHAP|||||20260409013000|||9012300909^Ashworth^Marcus^T^^^MD^^^^NPI
RXE|1^CONTINUOUS^HL70335|6980^Insulin regular human 100 units/mL^NDC|100|100|units/mL^units per milliliter^ISO+|INJ^Injection^HL70292||||||0|||9012300909^Ashworth^Marcus^T^^^MD^^^^NPI||||||||||||||||0^MIN
RXR|IV^Intravenous^HL70162
RXC|B|0.9% Sodium Chloride|250|mL^milliliters^ISO+
DG1|1||E10.10^Type 1 diabetes mellitus with ketoacidosis without coma^I10||20260408|A
NTE|1||DKA protocol. Start at 0.1 units/kg/hr. Target glucose 150-200 mg/dL. Check BMP and glucose hourly.
```

---

## 9. MDM^T02 - Consultation note from nephrology

```
MSH|^~\&|COREPOINT|SETON^2.16.840.1.113883.3.4401^ISO|DOC_RECV|TX_HIE|20260410160000||MDM^T02^MDM_T02|RHAP20260410160000009|P|2.5.1|||AL|NE
EVN|T02|20260410155500
PID|1||MRN50009^^^SETON^MR||Lockhart^Winston^Barrett^^Mr.^||19500808|M||2106-3^White^CDCREC|2001 S Lamar Blvd^^Austin^TX^78704^US^H||^PRN^PH^^1^512^5558901|||M^Married^HL70002|||927-14-5682|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|MED^3108^01^SETON^^^^N|E^Emergency^HL70007|||0123401010^Bancroft^Gregory^D^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260408009^^^SETON^VN
TXA|1|CN^Consultation Note^HL70270|TX^Text^HL70191||20260410155000||||||DOC50009^SETON|||||AU^Authenticated^HL70271
OBX|1|TX|11488-4^Consult note^LN||NEPHROLOGY CONSULTATION\.br\Patient: Lockhart, Winston Barrett\.br\DOB: 08/08/1950\.br\\.br\REASON FOR CONSULTATION: Acute kidney injury with creatinine 4.2 mg/dL from baseline 1.1\.br\\.br\ASSESSMENT:\.br\1. Acute kidney injury, likely prerenal etiology in setting of sepsis\.br\2. CKD stage 2 at baseline\.br\3. Hyperkalemia 5.8 mEq/L\.br\\.br\RECOMMENDATIONS:\.br\1. Aggressive IV fluid resuscitation with LR at 200 mL/hr\.br\2. Hold ACE inhibitor and NSAIDs\.br\3. Kayexalate 30g for hyperkalemia\.br\4. Monitor urine output closely\.br\5. Recheck BMP in 6 hours||||||F|||20260410155000
```

---

## 10. DFT^P03 - Ambulatory surgery center charges

```
MSH|^~\&|COREPOINT|UTHEALTH^2.16.840.1.113883.3.4402^ISO|FIN_RECV|TX_HIE|20260411170000||DFT^P03^DFT_P03|RHAP20260411170000010|P|2.5.1|||AL|NE
EVN|P03|20260411165500
PID|1||MRN50010^^^UTHEALTH^MR||Cardenas^Dolores^Yolanda^^Mrs.^||19810322|F||2106-3^White^CDCREC|5200 Almeda Rd^^Houston^TX^77004^US^H||^PRN^PH^^1^713^5554567|||M^Married^HL70002|||248-36-7159|||H^Hispanic or Latino^CDCREC
PV1|1|O|ASC^0001^01^UTHEALTH^^^^N|R^Routine^HL70007|||1234501111^Ellsworth^David^C^^^MD^^^^NPI||ORT^Orthopedics^HL70069||||||||||VN20260411010^^^UTHEALTH^VN
FT1|1|||20260411080000|20260411110000|CG^Charge^HL70017|29881^Arthroscopy knee surgical with meniscectomy^CPT4||1|||||||ASC^0001^01^UTHEALTH|||||1234501111^Ellsworth^David^C^^^MD^^^^NPI
FT1|2|||20260411080000|20260411110000|CG^Charge^HL70017|01382^Anesthesia knee arthroscopy^CPT4||1|||||||ANES^0001^01^UTHEALTH
DG1|1||M23.211^Derangement of anterior horn of medial meniscus due to old tear right knee^I10||20260411|A
```

---

## 11. VXU^V04 - Hepatitis B vaccination series

```
MSH|^~\&|COREPOINT|SETON^2.16.840.1.113883.3.4401^ISO|IMMTRAC2|TX_DSHS|20260412100000||VXU^V04^VXU_V04|RHAP20260412100000011|P|2.5.1|||ER|AL
PID|1||MRN50011^^^SETON^MR||Venkataraman^Arun^Suresh^^Mr.^||19950630|M||2028-9^Asian^CDCREC|6100 Airport Blvd^^Austin^TX^78752^US^H||^PRN^PH^^1^512^5553456|||S^Single^HL70002|||368-52-7941|||N^Not Hispanic or Latino^CDCREC
PD1||||2345601212^Osgood^Linda^M^^^MD^^^^NPI
PV1|1|O|CLI^0003^01^SETON^^^^N|R^Routine^HL70007|||2345601212^Osgood^Linda^M^^^MD^^^^NPI||FM^Family Medicine^HL70069||||||||||VN20260412011^^^SETON^VN
ORC|RE|ORD50011^RHAP||GRP50011^RHAP|CM^Complete^HL70038|||20260412093000|||2345601212^Osgood^Linda^M^^^MD^^^^NPI
RXA|0|1|20260412093000||45^Hepatitis B unspecified formulation^CVX|1.0|mL^milliliters^ISO+||00^New immunization record^NIP001||||||58160-0820-11^^NDC|||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|RD^Right Deltoid^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V01^Not VFC eligible^HL70064||||||F
OBX|2|TS|29768-9^Date vaccine information statement published^LN||20231020||||||F
OBX|3|TS|29769-7^Date vaccine information statement presented^LN||20260412||||||F
NTE|1||Dose 2 of 3. First dose given 2026-02-12. Third dose due 2026-08-12.
```

---

## 12. ADT^A04 - Observation unit registration

```
MSH|^~\&|COREPOINT|UTHEALTH^2.16.840.1.113883.3.4402^ISO|ADT_RECV|TX_HIE|20260413060000||ADT^A04^ADT_A01|RHAP20260413060000012|P|2.5.1|||AL|NE
EVN|A04|20260413055500|||EDRN^Rutledge^Amanda^G^^^RN|20260413055500
PID|1||MRN50012^^^UTHEALTH^MR||Kensington^Brenda^Elise^^Ms.^||19790901|F||2106-3^White^CDCREC|3100 Cleburne St^^Houston^TX^77004^US^H||^PRN^PH^^1^832^5557890|||D^Divorced^HL70002|||591-43-8726|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|OBS^0002^01^UTHEALTH^^^^N|U^Urgent^HL70007|||3456701313^Hadley^William^P^^^MD^^^^NPI||EM^Emergency Medicine^HL70069||||||||||VN20260413012^^^UTHEALTH^VN
PV2|||^Chest pain, low risk, observation protocol|||||||||||||||||||3^Urgent^HL70217
DG1|1||R07.9^Chest pain unspecified^I10||20260413|A
```

---

## 13. ORU^R01 - Cardiac catheterization report with embedded PDF (ED datatype)

```
MSH|^~\&|COREPOINT|SETON^2.16.840.1.113883.3.4401^ISO|CARD_RECV|TX_HIE|20260414140000||ORU^R01^ORU_R01|RHAP20260414140000013|P|2.5.1|||AL|NE
PID|1||MRN50013^^^SETON^MR||Fierro^Santiago^Andres^^Mr.^||19620414|M||2106-3^White^CDCREC|2200 S Congress Ave^^Austin^TX^78704^US^H||^PRN^PH^^1^512^5552345|||M^Married^HL70002|||762-53-8194|||H^Hispanic or Latino^CDCREC
PV1|1|I|CARD^4101^01^SETON^^^^N|E^Emergency^HL70007|||4567801414^Caldwell^Kevin^J^^^MD^^^^NPI||CAR^Cardiology^HL70069||||||||||VN20260413013^^^SETON^VN
ORC|RE|ORD50013^RHAP|FIL50013^CATH||CM^Complete^HL70038|||20260413140000|||4567801414^Caldwell^Kevin^J^^^MD^^^^NPI
OBR|1|ORD50013^RHAP|FIL50013^CATH|93458^Cardiac catheterization with left ventriculography^CPT4|||20260413140000|||||||||4567801414^Caldwell^Kevin^J^^^MD^^^^NPI||||||20260414133000|||F
OBX|1|FT|93458^Cardiac catheterization findings^L||CARDIAC CATHETERIZATION REPORT\.br\\.br\HEMODYNAMICS:\.br\LV end-diastolic pressure: 18 mmHg\.br\Cardiac output: 4.8 L/min\.br\Cardiac index: 2.6 L/min/m2\.br\\.br\CORONARY ANGIOGRAPHY:\.br\Left main: Normal\.br\LAD: 70% mid-segment stenosis\.br\LCx: 40% proximal stenosis\.br\RCA: Dominant, 90% proximal stenosis\.br\\.br\LV FUNCTION: EF 45%, inferior hypokinesis\.br\\.br\IMPRESSION: Two-vessel coronary artery disease. Recommend PCI to RCA.||||||F|||20260414133000
OBX|2|ED|PDF^Cardiac Catheterization Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxNjAKPj4Kc3RyZWFtCkJUCi9GMSAxNCBUZgoxMDAgNzAwIFRkCihDYXJkaWFjIENhdGhldGVyaXphdGlvbiBSZXBvcnQpIFRqCjAgLTIwIFRkCi9GMSAxMCBUZgooQXNjZW5zaW9uIFNldG9uIE1lZGljYWwgQ2VudGVyKSBUagowIC0yMCBUZAooUGF0aWVudDogRmllcnJvLCBTYW50aWFnbykgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago=||||||F|||20260414133000
```

---

## 14. ADT^A28 - Newborn registration

```
MSH|^~\&|COREPOINT|UTHEALTH^2.16.840.1.113883.3.4402^ISO|MPI_RECV|TX_HIE|20260415100000||ADT^A28^ADT_A05|RHAP20260415100000014|P|2.5.1|||AL|NE
EVN|A28|20260415095500
PID|1||MRN50014^^^UTHEALTH^MR||Galindo^Baby Girl^^^^^||20260415|F||2106-3^White^CDCREC|7900 Cambridge St^^Houston^TX^77054^US^H||^PRN^PH^^1^713^5559012|||S^Single^HL70002||||||H^Hispanic or Latino^CDCREC
NK1|1|Galindo^Veronica^Isabel^^Mrs.|MTH^Mother^HL70063|7900 Cambridge St^^Houston^TX^77054^US|^PRN^PH^^1^713^5559012||EC^Emergency Contact^HL70131
NK1|2|Galindo^Rafael^Eduardo^^Mr.|FTH^Father^HL70063|7900 Cambridge St^^Houston^TX^77054^US|^PRN^PH^^1^713^5559013||EC^Emergency Contact^HL70131
```

---

## 15. ADT^A02 - Transfer from labor and delivery to postpartum

```
MSH|^~\&|COREPOINT|SETON^2.16.840.1.113883.3.4401^ISO|ADT_RECV|TX_HIE|20260416080000||ADT^A02^ADT_A02|RHAP20260416080000015|P|2.5.1|||AL|NE
EVN|A02|20260416075500|||PPRN^Winslow^Jessica^A^^^RN|20260416075500
PID|1||MRN50015^^^SETON^MR||Villegas^Catalina^Renata^^Mrs.^||19940211|F||2106-3^White^CDCREC|2917 Guadalupe St^^Austin^TX^78705^US^H||^PRN^PH^^1^512^5559123|||M^Married^HL70002|||841-73-2905|||H^Hispanic or Latino^CDCREC
PV1|1|I|PP^2301^01^SETON^^^^N|R^Routine^HL70007|||1234500101^Dalrymple^Evelyn^R^^^MD^^^^NPI||OBG^Obstetrics^HL70069||||||T^Transfer^HL70007|||||VN20260401001^^^SETON^VN
PV2|||^Postpartum care, uncomplicated vaginal delivery
```

---

## 16. ADT^A40 - Patient merge for matched records

```
MSH|^~\&|COREPOINT|UTHEALTH^2.16.840.1.113883.3.4402^ISO|MPI_RECV|TX_HIE|20260417100000||ADT^A40^ADT_A39|RHAP20260417100000016|P|2.5.1|||AL|NE
EVN|A40|20260417095500|||HIM^Sutherland^Janet^M^^^HIM|20260417095500
PID|1||MRN50016^^^UTHEALTH^MR||Galindo^Claudia^Sofia^^Mrs.^||19830512|F||2106-3^White^CDCREC|6200 Hermann Park Dr^^Houston^TX^77030^US^H||^PRN^PH^^1^713^5554321|||M^Married^HL70002|||453-67-2819|||H^Hispanic or Latino^CDCREC
MRG|MRN50016OLD^^^UTHEALTH^MR||||||Galindo^Claudia^S
```

---

## 17. ADT^A31 - Advance directive update

```
MSH|^~\&|COREPOINT|SETON^2.16.840.1.113883.3.4401^ISO|MPI_RECV|TX_HIE|20260418110000||ADT^A31^ADT_A05|RHAP20260418110000017|P|2.5.1|||AL|NE
EVN|A31|20260418105500
PID|1||MRN50017^^^SETON^MR||Norris^Clayton^Walter^^Mr.^||19420305|M||2106-3^White^CDCREC|4500 E 7th St^^Austin^TX^78702^US^H||^PRN^PH^^1^512^5557890|||W^Widowed^HL70002|||819-46-3057|||N^Not Hispanic or Latino^CDCREC
PD1|||Ascension Seton Medical Center^^^^NPI|5678901515^Overstreet^Donna^L^^^MD^^^^NPI||||||||Y^Yes^HL70136
NK1|1|Norris^Kathleen^Marie^^Mrs.|DAU^Daughter^HL70063|8200 Burnet Rd^^Austin^TX^78757^US|^PRN^PH^^1^512^5553210||EC^Emergency Contact^HL70131
```

---

## 18. MFN^M02 - New physician master file entry

```
MSH|^~\&|COREPOINT|UTHEALTH^2.16.840.1.113883.3.4402^ISO|MF_RECV|TX_HIE|20260419090000||MFN^M02^MFN_M02|RHAP20260419090000018|P|2.5.1|||AL|NE
MFI|PRA^Practitioner master file^HL70175||UPD^Update^HL70180|||NE
MFE|MAD^Add record to master file^HL70180|20260419085500||6789011818^Bhandari^Nikhil^Rajan^^MD|CWE
STF|6789011818|U6789011818|Bhandari^Nikhil^Rajan^^MD||M|19820918|A^Active^HL70183|||||^WPN^PH^^1^713^5551234
PRA|6789011818^Bhandari^Nikhil^Rajan^^MD|UTHEALTH^UT Health Houston|I^Institution^HL70186|||||207RN0300X^Nephrology^NUCC
```

---

## 19. ACK - Commit accept acknowledgment

```
MSH|^~\&|ADT_RECV|TX_HIE|COREPOINT|SETON^2.16.840.1.113883.3.4401^ISO|20260420080000||ACK^A01^ACK|RHAP20260420080000019|P|2.5.1|||AL|NE
MSA|CA|RHAP20260401080000001||0
```

---

## 20. ORM^O01 - MRI lumbar spine order

```
MSH|^~\&|COREPOINT|SETON^2.16.840.1.113883.3.4401^ISO|RAD_RECV|TX_HIE|20260421100000||ORM^O01^ORM_O01|RHAP20260421100000020|P|2.5.1|||AL|NE
PID|1||MRN50020^^^SETON^MR||Upshaw^Demetrius^Allen^^Mr.^||19770216|M||2054-5^Black or African American^CDCREC|3800 N Lamar Blvd^^Austin^TX^78756^US^H||^PRN^PH^^1^512^5559876|||M^Married^HL70002|||694-81-5237|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^MRI2^01^SETON^^^^N|R^Routine^HL70007|||7890102020^Langford^Sandra^K^^^MD^^^^NPI||ORT^Orthopedics^HL70069||||||||||VN20260421020^^^SETON^VN
ORC|NW|ORD50020^RHAP||GRP50020^RHAP|||||20260421093000|||7890102020^Langford^Sandra^K^^^MD^^^^NPI|||||SETON^Ascension Seton Medical Center
OBR|1|ORD50020^RHAP||72148^MRI lumbar spine without contrast^CPT4|||20260421093000||||||||7890102020^Langford^Sandra^K^^^MD^^^^NPI||||||||||1^Routine^HL70065
DG1|1||M54.5^Low back pain^I10||20260421|A
NTE|1||Chronic low back pain with left leg radiculopathy. MRI to evaluate for disc herniation or stenosis.
```
