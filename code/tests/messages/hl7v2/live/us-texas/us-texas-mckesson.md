# McKesson Paragon - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Medical admission for diabetic ketoacidosis

```
MSH|^~\&|PARAGON|SHANNONMC^2.16.840.1.113883.3.5501^ISO|ADT_RECV|TX_HIE|20260401110000||ADT^A01^ADT_A01|MCKN20260401110000001|P|2.5.1|||AL|NE
EVN|A01|20260401105500|||EDRN^Pemberton^Rosa^M^^^RN|20260401105500
PID|1||MRN60001^^^SHANNONMC^MR~538-71-4296^^^USSSA^SS||Esparza^Miguel^Renaldo^^Mr.^||19680225|M||2106-3^White^CDCREC|3020 Knickerbocker Rd^^San Angelo^TX^76904^US^H||^PRN^PH^^1^325^5559123|||M^Married^HL70002|||538-71-4296|||H^Hispanic or Latino^CDCREC
PD1|||Shannon Medical Center^^^^NPI|1234560101^Westbrook^Roberto^C^^^MD^^^^NPI
NK1|1|Esparza^Isabel^Rosario^^Mrs.|SPO^Spouse^HL70063|3020 Knickerbocker Rd^^San Angelo^TX^76904^US|^PRN^PH^^1^325^5559124||EC^Emergency Contact^HL70131
PV1|1|I|MED^2104^01^SHANNONMC^^^^N|E^Emergency^HL70007|||1234560101^Westbrook^Roberto^C^^^MD^^^^NPI|2345670202^Fairchild^Diane^L^^^MD^^^^NPI|IM^Internal Medicine^HL70069||||||A^Accident^HL70007|||||VN20260401001^^^SHANNONMC^VN|||||||||||||||||||||||||20260401105500
PV2|||^Diabetic ketoacidosis with glucose 487 mg/dL
DG1|1||E10.10^Type 1 diabetes mellitus with ketoacidosis without coma^I10||20260401|A
DG1|2||E87.2^Acidosis^I10||20260401|A
IN1|1|BCBS001|60054^Blue Cross Blue Shield of Texas|BCBSTX^^Dallas^TX^75201|||||BCBSGRP||||||Esparza^Miguel^Renaldo|SE^Self^HL70063|19680225|3020 Knickerbocker Rd^^San Angelo^TX^76904^US|Y||1||||||||||||||BCBSPOL678901
```

---

## 2. ADT^A03 - Discharge from general surgery

```
MSH|^~\&|PARAGON|CITIZENSMC^2.16.840.1.113883.3.5502^ISO|ADT_RECV|TX_HIE|20260403140000||ADT^A03^ADT_A03|MCKN20260403140000002|P|2.5.1|||AL|NE
EVN|A03|20260403135500|||SURGRN^Lockwood^Janet^R^^^RN|20260403135500
PID|1||MRN60002^^^CITIZENSMC^MR||Ashworth^Dorothy^Elaine^^Mrs.^||19450718|F||2106-3^White^CDCREC|1501 Pine St^^Victoria^TX^77901^US^H||^PRN^PH^^1^361^5558234|||W^Widowed^HL70002|||241-52-8937|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|SURG^3101^01^CITIZENSMC^^^^N|U^Urgent^HL70007|||3456780303^Greenfield^Steven^M^^^MD^^^^NPI|4567890404^Northcutt^Linda^K^^^MD^^^^NPI|GS^General Surgery^HL70069||||||R^Referral^HL70007|||||VN20260401002^^^CITIZENSMC^VN|||||||||||||||||||01^Discharged to home^HL70112||||20260401130000|20260403135500
DG1|1||K35.80^Unspecified acute appendicitis without perforation^I10||20260401|A
PR1|1||44970^Laparoscopic appendectomy^CPT4|^Laparoscopic appendectomy|20260401150000|||||3456780303^Greenfield^Steven^M^^^MD^^^^NPI
```

---

## 3. ORU^R01 - Thyroid function panel results

```
MSH|^~\&|PARAGON|SHANNONMC^2.16.840.1.113883.3.5501^ISO|LAB_RECV|TX_HIE|20260404110000||ORU^R01^ORU_R01|MCKN20260404110000003|P|2.5.1|||AL|NE
PID|1||MRN60003^^^SHANNONMC^MR||Grayson^Gloria^Renee^^Ms.^||19720620|F||2106-3^White^CDCREC|4200 College Hills Blvd^^San Angelo^TX^76904^US^H||^PRN^PH^^1^325^5553456|||D^Divorced^HL70002|||372-84-6153|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|LAB^0001^01^SHANNONMC^^^^N|R^Routine^HL70007|||5678900505^Pemberton^Margaret^A^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260404003^^^SHANNONMC^VN
ORC|RE|ORD60003^MCKN|FIL60003^LAB||CM^Complete^HL70038|||20260404080000|||5678900505^Pemberton^Margaret^A^^^MD^^^^NPI
OBR|1|ORD60003^MCKN|FIL60003^LAB|34015-7^Thyroid function panel^LN|||20260404080000|||||||||5678900505^Pemberton^Margaret^A^^^MD^^^^NPI||||||20260404103000|||F
OBX|1|NM|3016-3^TSH [Units/volume] in Serum or Plasma^LN||8.7|mIU/L^milli-international units per liter^UCUM|0.4-4.0|H|||F|||20260404103000
OBX|2|NM|3024-7^Free T4 [Mass/volume] in Serum or Plasma^LN||0.6|ng/dL^nanograms per deciliter^UCUM|0.8-1.8|L|||F|||20260404103000
OBX|3|NM|3053-6^Free T3 [Mass/volume] in Serum or Plasma^LN||1.8|pg/mL^picograms per milliliter^UCUM|2.3-4.2|L|||F|||20260404103000
OBX|4|NM|5385-0^Thyroid peroxidase Ab [Units/volume] in Serum or Plasma^LN||245|IU/mL^international units per milliliter^UCUM|<9|H|||F|||20260404103000
```

---

## 4. ORM^O01 - Bone density scan order

```
MSH|^~\&|PARAGON|CITIZENSMC^2.16.840.1.113883.3.5502^ISO|RAD_RECV|TX_HIE|20260405090000||ORM^O01^ORM_O01|MCKN20260405090000004|P|2.5.1|||AL|NE
PID|1||MRN60004^^^CITIZENSMC^MR||Bradshaw^Betty^Caroline^^Mrs.^||19520830|F||2106-3^White^CDCREC|302 E Airline Rd^^Victoria^TX^77901^US^H||^PRN^PH^^1^361^5559012|||W^Widowed^HL70002|||483-69-2107|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^0002^01^CITIZENSMC^^^^N|R^Routine^HL70007|||6789010606^Whitfield^Patricia^B^^^MD^^^^NPI||FM^Family Medicine^HL70069||||||||||VN20260405004^^^CITIZENSMC^VN
ORC|NW|ORD60004^MCKN||GRP60004^MCKN|||||20260405083000|||6789010606^Whitfield^Patricia^B^^^MD^^^^NPI|||||CITIZENSMC^Citizens Medical Center
OBR|1|ORD60004^MCKN||77080^DXA bone density axial^CPT4|||20260405083000||||||||6789010606^Whitfield^Patricia^B^^^MD^^^^NPI||||||||||1^Routine^HL70065
DG1|1||M81.0^Age-related osteoporosis without current pathological fracture^I10||20260405|A
NTE|1||Postmenopausal woman age 73. History of wrist fracture 2023. Follow-up DEXA scan.
```

---

## 5. ORU^R01 - Bone density results with embedded PDF (ED datatype)

```
MSH|^~\&|PARAGON|CITIZENSMC^2.16.840.1.113883.3.5502^ISO|RAD_RECV|TX_HIE|20260406140000||ORU^R01^ORU_R01|MCKN20260406140000005|P|2.5.1|||AL|NE
PID|1||MRN60004^^^CITIZENSMC^MR||Bradshaw^Betty^Caroline^^Mrs.^||19520830|F||2106-3^White^CDCREC|302 E Airline Rd^^Victoria^TX^77901^US^H||^PRN^PH^^1^361^5559012|||W^Widowed^HL70002|||483-69-2107|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^0002^01^CITIZENSMC^^^^N|R^Routine^HL70007|||6789010606^Whitfield^Patricia^B^^^MD^^^^NPI||FM^Family Medicine^HL70069||||||||||VN20260406005^^^CITIZENSMC^VN
ORC|RE|ORD60005^MCKN|FIL60005^RAD||CM^Complete^HL70038|||20260405100000|||6789010606^Whitfield^Patricia^B^^^MD^^^^NPI
OBR|1|ORD60005^MCKN|FIL60005^RAD|77080^DXA bone density axial^CPT4|||20260405100000|||||||||6789010606^Whitfield^Patricia^B^^^MD^^^^NPI||||||20260406133000|||F
OBX|1|NM|46278-8^BMD femoral neck T-score^LN||-2.8||>-1.0|L|||F|||20260406133000
OBX|2|NM|46275-4^BMD lumbar spine T-score^LN||-3.1||>-1.0|L|||F|||20260406133000
OBX|3|FT|77080^DXA interpretation^L||DEXA SCAN REPORT\.br\\.br\Femoral Neck: T-score -2.8 (Osteoporosis)\.br\Lumbar Spine L1-L4: T-score -3.1 (Osteoporosis)\.br\\.br\IMPRESSION: Osteoporosis at both sites. Worsened from prior study (2023 T-scores: femoral neck -2.3, lumbar -2.7).\.br\RECOMMENDATION: Continue bisphosphonate therapy. Consider endocrinology referral.||||||F|||20260406133000
OBX|4|ED|PDF^DEXA Scan Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxMjgKPj4Kc3RyZWFtCkJUCi9GMSAxNCBUZgoxMDAgNzAwIFRkCihERVhBIEJvbmUgRGVuc2l0eSBSZXBvcnQpIFRqCjAgLTIwIFRkCi9GMSAxMCBUZgooQ2l0aXplbnMgTWVkaWNhbCBDZW50ZXIpIFRqCjAgLTIwIFRkCihQYXRpZW50OiBCcmFkc2hhdywgQmV0dHkpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoK||||||F|||20260406133000
```

---

## 6. ADT^A08 - Patient allergy information update

```
MSH|^~\&|PARAGON|SHANNONMC^2.16.840.1.113883.3.5501^ISO|ADT_RECV|TX_HIE|20260407100000||ADT^A08^ADT_A01|MCKN20260407100000006|P|2.5.1|||AL|NE
EVN|A08|20260407095500|||PHRN^Lockwood^Amanda^T^^^RN|20260407095500
PID|1||MRN60006^^^SHANNONMC^MR||Saucedo^Carmen^Valentina^^Mrs.^||19830914|F||2106-3^White^CDCREC|1910 Sherwood Way^^San Angelo^TX^76901^US^H||^PRN^PH^^1^325^5554567|||M^Married^HL70002|||591-73-8204|||H^Hispanic or Latino^CDCREC
PV1|1|I|MED^2201^02^SHANNONMC^^^^N|U^Urgent^HL70007|||7890120707^Aldridge^James^B^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260406006^^^SHANNONMC^VN
AL1|1|DA^Drug allergy^HL70127|70618^Penicillin^RxNorm|SV^Severe^HL70128|Anaphylaxis|20150320
AL1|2|DA^Drug allergy^HL70127|2670^Codeine^RxNorm|MO^Moderate^HL70128|Nausea and vomiting|20180115
```

---

## 7. SIU^S12 - Orthopedic follow-up appointment

```
MSH|^~\&|PARAGON|CITIZENSMC^2.16.840.1.113883.3.5502^ISO|SCHED_RECV|TX_HIE|20260408090000||SIU^S12^SIU_S12|MCKN20260408090000007|P|2.5.1|||AL|NE
SCH|APPT60007^MCKN||||||ORTFU^Orthopedic Follow-up^L|20^MIN|MIN^Minutes^ISO+|^^^20260415093000^^20^MIN|||||8901230808^Hargrove^David^W^^^MD^^^^NPI|^PRN^PH^^1^361^5553456|||||8901230808^Hargrove^David^W^^^MD^^^^NPI|||||Booked
PID|1||MRN60007^^^CITIZENSMC^MR||Delaney^William^Patrick^^Mr.^||19610422|M||2106-3^White^CDCREC|601 E Rio Grande St^^Victoria^TX^77901^US^H||^PRN^PH^^1^361^5557890|||M^Married^HL70002|||714-83-9265|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|ORT^0001^01^CITIZENSMC^^^^N|R^Routine^HL70007|||8901230808^Hargrove^David^W^^^MD^^^^NPI||ORT^Orthopedics^HL70069||||||||||VN20260408007^^^CITIZENSMC^VN
RGS|1||ORT_CLINIC
AIS|1||99214^Office visit established level 4^CPT4|20260415093000|||20^MIN|MIN^Minutes^ISO+||Confirmed
AIG|1||8901230808^Hargrove^David^W^^^MD^^^^NPI|||||20260415093000|||20^MIN
AIL|1||ORT^0001^01^CITIZENSMC|||||20260415093000|||20^MIN
NTE|1||6-week follow-up post right hip arthroplasty. Evaluate wound, ROM, and weight-bearing status.
```

---

## 8. RDE^O11 - Heparin drip order

```
MSH|^~\&|PARAGON|SHANNONMC^2.16.840.1.113883.3.5501^ISO|PHARM_RECV|TX_HIE|20260409180000||RDE^O11^RDE_O11|MCKN20260409180000008|P|2.5.1|||AL|NE
PID|1||MRN60008^^^SHANNONMC^MR||Hubbard^Raymond^Curtis^^Mr.^||19570311|M||2106-3^White^CDCREC|2800 Sunset Dr^^San Angelo^TX^76904^US^H||^PRN^PH^^1^325^5558901|||M^Married^HL70002|||804-26-3571|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|MED^2105^01^SHANNONMC^^^^N|E^Emergency^HL70007|||9012340909^Thornton^Linda^A^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260409008^^^SHANNONMC^VN
ORC|NW|ORD60008^MCKN||GRP60008^MCKN|||||20260409173000|||9012340909^Thornton^Linda^A^^^MD^^^^NPI
RXE|1^CONTINUOUS^HL70335|5224^Heparin sodium 25000 units/500 mL^NDC|25000|25000|units^units^ISO+|INJ^Injection^HL70292||||||0|||9012340909^Thornton^Linda^A^^^MD^^^^NPI||||||||||||||||0^MIN
RXR|IV^Intravenous^HL70162
RXC|B|D5W|500|mL^milliliters^ISO+
DG1|1||I26.99^Other pulmonary embolism without acute cor pulmonale^I10||20260409|A
NTE|1||Weight-based heparin protocol. Loading dose 80 units/kg bolus, then 18 units/kg/hr. Target aPTT 60-80 seconds. Check aPTT q6h.
```

---

## 9. MDM^T02 - Operative report for appendectomy

```
MSH|^~\&|PARAGON|CITIZENSMC^2.16.840.1.113883.3.5502^ISO|DOC_RECV|TX_HIE|20260410140000||MDM^T02^MDM_T02|MCKN20260410140000009|P|2.5.1|||AL|NE
EVN|T02|20260410135500
PID|1||MRN60002^^^CITIZENSMC^MR||Ashworth^Dorothy^Elaine^^Mrs.^||19450718|F||2106-3^White^CDCREC|1501 Pine St^^Victoria^TX^77901^US^H||^PRN^PH^^1^361^5558234|||W^Widowed^HL70002|||241-52-8937|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|SURG^3101^01^CITIZENSMC^^^^N|U^Urgent^HL70007|||3456780303^Greenfield^Steven^M^^^MD^^^^NPI||GS^General Surgery^HL70069||||||||||VN20260401002^^^CITIZENSMC^VN
TXA|1|OP^Operative Note^HL70270|TX^Text^HL70191||20260410135000||||||DOC60009^CITIZENSMC|||||AU^Authenticated^HL70271
OBX|1|TX|28572-5^Operative note^LN||OPERATIVE REPORT\.br\Patient: Ashworth, Dorothy Elaine\.br\DOB: 07/18/1945\.br\Procedure Date: 04/01/2026\.br\\.br\PROCEDURE: Laparoscopic appendectomy\.br\SURGEON: Steven M. Greenfield, MD\.br\ANESTHESIA: General endotracheal\.br\\.br\INDICATIONS: 80-year-old female with acute appendicitis confirmed by CT scan\.br\\.br\FINDINGS: Inflamed, non-perforated appendix with surrounding erythema\.br\\.br\TECHNIQUE: Standard 3-port laparoscopic technique. Mesoappendix divided with harmonic scalpel. Appendix base secured with two endoloops and divided. Specimen retrieved in endocatch bag. Hemostasis confirmed.\.br\\.br\ESTIMATED BLOOD LOSS: 15 mL\.br\COMPLICATIONS: None\.br\SPECIMENS: Appendix to pathology||||||F|||20260410135000
```

---

## 10. DFT^P03 - Outpatient clinic visit charges

```
MSH|^~\&|PARAGON|SHANNONMC^2.16.840.1.113883.3.5501^ISO|FIN_RECV|TX_HIE|20260411160000||DFT^P03^DFT_P03|MCKN20260411160000010|P|2.5.1|||AL|NE
EVN|P03|20260411155500
PID|1||MRN60010^^^SHANNONMC^MR||Tovar^Ana^Marisol^^Mrs.^||19750104|F||2106-3^White^CDCREC|1515 S Bryant Blvd^^San Angelo^TX^76903^US^H||^PRN^PH^^1^325^5551234|||M^Married^HL70002|||827-41-5063|||H^Hispanic or Latino^CDCREC
PV1|1|O|CLI^0002^01^SHANNONMC^^^^N|R^Routine^HL70007|||5678900505^Pemberton^Margaret^A^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260411010^^^SHANNONMC^VN
FT1|1|||20260411090000|20260411093000|CG^Charge^HL70017|99215^Office visit established level 5^CPT4||1|||||||CLI^0002^01^SHANNONMC|||||5678900505^Pemberton^Margaret^A^^^MD^^^^NPI
FT1|2|||20260411093000|20260411093000|CG^Charge^HL70017|36415^Venipuncture routine^CPT4||1|||||||LAB^0001^01^SHANNONMC
FT1|3|||20260411094000|20260411094000|CG^Charge^HL70017|93000^ECG routine^CPT4||1|||||||CLI^0002^01^SHANNONMC
DG1|1||I10^Essential primary hypertension^I10||20260411|A
DG1|2||E11.65^Type 2 diabetes mellitus with hyperglycemia^I10||20260411|A
```

---

## 11. VXU^V04 - Tdap vaccination

```
MSH|^~\&|PARAGON|CITIZENSMC^2.16.840.1.113883.3.5502^ISO|IMMTRAC2|TX_DSHS|20260412103000||VXU^V04^VXU_V04|MCKN20260412103000011|P|2.5.1|||ER|AL
PID|1||MRN60011^^^CITIZENSMC^MR||Langston^James^Terrence^^Mr.^||19890228|M||2106-3^White^CDCREC|904 E Mockingbird Ln^^Victoria^TX^77904^US^H||^PRN^PH^^1^361^5553210|||M^Married^HL70002|||946-18-3072|||N^Not Hispanic or Latino^CDCREC
PD1||||0123451111^Caldwell^Sandra^K^^^MD^^^^NPI
PV1|1|O|CLI^0001^01^CITIZENSMC^^^^N|R^Routine^HL70007|||0123451111^Caldwell^Sandra^K^^^MD^^^^NPI||FM^Family Medicine^HL70069||||||||||VN20260412011^^^CITIZENSMC^VN
ORC|RE|ORD60011^MCKN||GRP60011^MCKN|CM^Complete^HL70038|||20260412100000|||0123451111^Caldwell^Sandra^K^^^MD^^^^NPI
RXA|0|1|20260412100000||115^Tdap^CVX|0.5|mL^milliliters^ISO+||00^New immunization record^NIP001||||||49281-0400-15^^NDC|||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|LD^Left Deltoid^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V01^Not VFC eligible^HL70064||||||F
OBX|2|TS|29768-9^Date vaccine information statement published^LN||20240101||||||F
OBX|3|TS|29769-7^Date vaccine information statement presented^LN||20260412||||||F
```

---

## 12. ADT^A04 - Walk-in clinic registration

```
MSH|^~\&|PARAGON|SHANNONMC^2.16.840.1.113883.3.5501^ISO|ADT_RECV|TX_HIE|20260413080000||ADT^A04^ADT_A01|MCKN20260413080000012|P|2.5.1|||AL|NE
EVN|A04|20260413075500|||REG^Montoya^Maria^C^^^ADM|20260413075500
PID|1||MRN60012^^^SHANNONMC^MR||Truong^Lisa^Phuong^^Ms.^||19950312|F||2028-9^Asian^CDCREC|3100 W Beauregard Ave^^San Angelo^TX^76901^US^H||^PRN^PH^^1^325^5557890|||S^Single^HL70002|||147-62-3891|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|CLI^0001^01^SHANNONMC^^^^N|R^Routine^HL70007|||1234561212^Westbrook^Roberto^C^^^MD^^^^NPI||FM^Family Medicine^HL70069||||||||||VN20260413012^^^SHANNONMC^VN
PV2|||^Sore throat and low-grade fever for 3 days
DG1|1||J02.9^Acute pharyngitis unspecified^I10||20260413|A
```

---

## 13. ORU^R01 - Hemoglobin A1c with embedded PDF (ED datatype)

```
MSH|^~\&|PARAGON|SHANNONMC^2.16.840.1.113883.3.5501^ISO|LAB_RECV|TX_HIE|20260414110000||ORU^R01^ORU_R01|MCKN20260414110000013|P|2.5.1|||AL|NE
PID|1||MRN60010^^^SHANNONMC^MR||Tovar^Ana^Marisol^^Mrs.^||19750104|F||2106-3^White^CDCREC|1515 S Bryant Blvd^^San Angelo^TX^76903^US^H||^PRN^PH^^1^325^5551234|||M^Married^HL70002|||827-41-5063|||H^Hispanic or Latino^CDCREC
PV1|1|O|LAB^0001^01^SHANNONMC^^^^N|R^Routine^HL70007|||5678900505^Pemberton^Margaret^A^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260414013^^^SHANNONMC^VN
ORC|RE|ORD60013^MCKN|FIL60013^LAB||CM^Complete^HL70038|||20260414080000|||5678900505^Pemberton^Margaret^A^^^MD^^^^NPI
OBR|1|ORD60013^MCKN|FIL60013^LAB|4548-4^Hemoglobin A1c^LN|||20260414080000|||||||||5678900505^Pemberton^Margaret^A^^^MD^^^^NPI||||||20260414103000|||F
OBX|1|NM|4548-4^Hemoglobin A1c/Hemoglobin.total in Blood^LN||9.2|%^percent^UCUM|<5.7|H|||F|||20260414103000
OBX|2|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||198|mg/dL^milligrams per deciliter^UCUM|74-106|H|||F|||20260414103000
OBX|3|ED|PDF^Lab Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxMTgKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihMYWJvcmF0b3J5IFJlcG9ydCkgVGoKMCAtMjAgVGQKL0YxIDEwIFRmCihTaGFubm9uIE1lZGljYWwgQ2VudGVyKSBUagowIC0yMCBUZAooSGJBMWM6IDkuMiUpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoK||||||F|||20260414103000
```

---

## 14. ADT^A28 - Pre-admission registration for elective surgery

```
MSH|^~\&|PARAGON|CITIZENSMC^2.16.840.1.113883.3.5502^ISO|MPI_RECV|TX_HIE|20260415100000||ADT^A28^ADT_A05|MCKN20260415100000014|P|2.5.1|||AL|NE
EVN|A28|20260415095500
PID|1||MRN60014^^^CITIZENSMC^MR~782-15-4630^^^USSSA^SS||Kapoor^Tiffany^Anisha^^Ms.^||19880107|F||2028-9^Asian^CDCREC|2300 N Navarro St^^Victoria^TX^77901^US^H||^PRN^PH^^1^361^5554567|^WPN^PH^^1^361^5559876||S^Single^HL70002|||782-15-4630|||N^Not Hispanic or Latino^CDCREC
PD1|||Citizens Medical Center^^^^NPI|8901230808^Hargrove^David^W^^^MD^^^^NPI
NK1|1|Kapoor^Priya^Sunita^^Mrs.|MTH^Mother^HL70063|2300 N Navarro St^^Victoria^TX^77901^US|^PRN^PH^^1^361^5554568||EC^Emergency Contact^HL70131
```

---

## 15. ADT^A02 - Transfer from ED to medical floor

```
MSH|^~\&|PARAGON|SHANNONMC^2.16.840.1.113883.3.5501^ISO|ADT_RECV|TX_HIE|20260416200000||ADT^A02^ADT_A02|MCKN20260416200000015|P|2.5.1|||AL|NE
EVN|A02|20260416195500|||MEDRN^Fairchild^Tanya^R^^^RN|20260416195500
PID|1||MRN60015^^^SHANNONMC^MR||Hinojosa^Jose^Alejandro^^Mr.^||19740628|M||2106-3^White^CDCREC|4100 Arden Rd^^San Angelo^TX^76901^US^H||^PRN^PH^^1^325^5553789|||M^Married^HL70002|||362-48-7193|||H^Hispanic or Latino^CDCREC
PV1|1|I|MED^2108^01^SHANNONMC^^^^N|E^Emergency^HL70007|||1234561515^Westbrook^Roberto^C^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||T^Transfer^HL70007|||||VN20260416015^^^SHANNONMC^VN
PV2|||^Chest pain, troponin negative, observation to inpatient conversion
```

---

## 16. ADT^A40 - Patient merge resolving duplicate records

```
MSH|^~\&|PARAGON|CITIZENSMC^2.16.840.1.113883.3.5502^ISO|MPI_RECV|TX_HIE|20260417100000||ADT^A40^ADT_A39|MCKN20260417100000016|P|2.5.1|||AL|NE
EVN|A40|20260417095500|||HIM^Stanfield^Karen^D^^^HIM|20260417095500
PID|1||MRN60016^^^CITIZENSMC^MR||Garibay^Maria^Luciana^^Mrs.^||19830915|F||2106-3^White^CDCREC|1800 E Red River St^^Victoria^TX^77901^US^H||^PRN^PH^^1^361^5558901|||M^Married^HL70002|||473-59-6284|||H^Hispanic or Latino^CDCREC
MRG|MRN60016DUP^^^CITIZENSMC^MR||||||Garibay^Maria^L
```

---

## 17. ADT^A31 - Primary care provider change

```
MSH|^~\&|PARAGON|SHANNONMC^2.16.840.1.113883.3.5501^ISO|MPI_RECV|TX_HIE|20260418110000||ADT^A31^ADT_A05|MCKN20260418110000017|P|2.5.1|||AL|NE
EVN|A31|20260418105500
PID|1||MRN60017^^^SHANNONMC^MR||Forsythe^Brenda^Colleen^^Mrs.^||19600212|F||2106-3^White^CDCREC|2500 Loop 306^^San Angelo^TX^76904^US^H||^PRN^PH^^1^325^5556789|||M^Married^HL70002|||581-64-9037|||N^Not Hispanic or Latino^CDCREC
PD1|||Shannon Medical Center^^^^NPI|2345671717^Stratton^Maria^R^^^MD^^^^NPI
```

---

## 18. MFN^M02 - New hospitalist physician master file

```
MSH|^~\&|PARAGON|CITIZENSMC^2.16.840.1.113883.3.5502^ISO|MF_RECV|TX_HIE|20260419090000||MFN^M02^MFN_M02|MCKN20260419090000018|P|2.5.1|||AL|NE
MFI|PRA^Practitioner master file^HL70175||UPD^Update^HL70180|||NE
MFE|MAD^Add record to master file^HL70180|20260419085500||3456781818^Yamazaki^Daniel^Koji^^MD|CWE
STF|3456781818|U3456781818|Yamazaki^Daniel^Koji^^MD||M|19850314|A^Active^HL70183|||||^WPN^PH^^1^361^5551234
PRA|3456781818^Yamazaki^Daniel^Koji^^MD|CITIZENSMC^Citizens Medical Center|I^Institution^HL70186|||||208M00000X^Hospitalist^NUCC
```

---

## 19. ORM^O01 - Stat blood culture order

```
MSH|^~\&|PARAGON|SHANNONMC^2.16.840.1.113883.3.5501^ISO|LAB_RECV|TX_HIE|20260420020000||ORM^O01^ORM_O01|MCKN20260420020000019|P|2.5.1|||AL|NE
PID|1||MRN60019^^^SHANNONMC^MR||Joiner^Patricia^Elise^^Mrs.^||19780530|F||2106-3^White^CDCREC|3600 N Chadbourne St^^San Angelo^TX^76903^US^H||^PRN^PH^^1^325^5552345|||M^Married^HL70002|||693-82-4150|||H^Hispanic or Latino^CDCREC
PV1|1|I|MED^2103^01^SHANNONMC^^^^N|E^Emergency^HL70007|||4567891919^Wainwright^Kenneth^P^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260419019^^^SHANNONMC^VN
ORC|NW|ORD60019^MCKN||GRP60019^MCKN|||||20260420013000|||4567891919^Wainwright^Kenneth^P^^^MD^^^^NPI|||||SHANNONMC^Shannon Medical Center
OBR|1|ORD60019^MCKN||87040^Blood culture bacterial^CPT4|||20260420013000||||||||4567891919^Wainwright^Kenneth^P^^^MD^^^^NPI||||||||||9^Stat^HL70065
DG1|1||R65.20^Severe sepsis without septic shock^I10||20260419|A
NTE|1||Febrile to 39.4C, WBC 18.2, tachycardic. Collect 2 sets from separate sites before starting antibiotics.
```

---

## 20. ACK - Application accept acknowledgment

```
MSH|^~\&|LAB_RECV|TX_HIE|PARAGON|SHANNONMC^2.16.840.1.113883.3.5501^ISO|20260421080000||ACK^O01^ACK|MCKN20260421080000020|P|2.5.1|||AL|NE
MSA|AA|MCKN20260420020000019||0
```
