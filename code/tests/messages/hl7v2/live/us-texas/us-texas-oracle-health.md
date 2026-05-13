# Oracle Health (Cerner) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Inpatient admission for pneumonia

```
MSH|^~\&|MILLENNIUM|JPSHN^2.16.840.1.113883.3.1901^ISO|ADT_RECV|TX_HIE|20260410081500||ADT^A01^ADT_A01|CERN20260410081500001|P|2.5.1|||AL|NE
EVN|A01|20260410080000|||ADMRN^Carrington^Jolene^T^^^RN|20260410080000
PID|1||MRN30001^^^JPSHN^MR~648-91-3207^^^USSSA^SS||Longoria^Mateo^Alejandro^^Mr.^||19720314|M||2106-3^White^CDCREC|3417 Bluebonnet Cir^^Fort Worth^TX^76109^US^H||^PRN^PH^^1^682^5539247|||M^Married^HL70002|||648-91-3207|||H^Hispanic or Latino^CDCREC
PD1|||JPS Health Network^^^^NPI|1834927561^Danforth^Steven^R^^^MD^^^^NPI
NK1|1|Longoria^Catalina^Sofia^^Mrs.|SPO^Spouse^HL70063|3417 Bluebonnet Cir^^Fort Worth^TX^76109^US|^PRN^PH^^1^682^5539248||EC^Emergency Contact^HL70131
PV1|1|I|PULM^3204^02^JPSHN^^^^N|E^Emergency^HL70007|||1834927561^Danforth^Steven^R^^^MD^^^^NPI|2947183605^Eastman^Rachel^K^^^MD^^^^NPI|PUL^Pulmonology^HL70069||||||A^Accident^HL70007|||||VN20260410001^^^JPSHN^VN|||||||||||||||||||||||||20260410080000
PV2|||^Community acquired pneumonia with hypoxia
DG1|1||J18.1^Lobar pneumonia unspecified organism^I10||20260410|A
DG1|2||J96.01^Acute respiratory failure with hypoxia^I10||20260410|A
IN1|1|MCARE001|00451^Medicare|Centers for Medicare^^Baltimore^MD^21244|||||MCAREGRP||||||Longoria^Mateo^Alejandro|SE^Self^HL70063|19720314|3417 Bluebonnet Cir^^Fort Worth^TX^76109^US|Y||1||||||||||||||MCAREPOL234567
```

---

## 2. ADT^A03 - Discharge from labor and delivery

```
MSH|^~\&|MILLENNIUM|THR^2.16.840.1.113883.3.2102^ISO|ADT_RECV|TX_HIE|20260412153000||ADT^A03^ADT_A03|CERN20260412153000002|P|2.5.1|||AL|NE
EVN|A03|20260412152500|||LDRN^Fulbright^Tamara^N^^^RN|20260412152500
PID|1||MRN30002^^^THR^MR||Gatewood^Tamika^Renee^^Mrs.^||19930818|F||2054-5^Black or African American^CDCREC|4017 W Pioneer Pkwy^^Arlington^TX^76013^US^H||^PRN^PH^^1^817^5538476|||M^Married^HL70002|||314-58-7923|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|OB^2101^01^THR^^^^N|R^Routine^HL70007|||3751842960^Garrison^Michelle^A^^^MD^^^^NPI|4068293175^Blackwood^Sandra^L^^^MD^^^^NPI|OBG^Obstetrics^HL70069||||||R^Referral^HL70007|||||VN20260410002^^^THR^VN|||||||||||||||||||01^Discharged to home^HL70112||||20260410060000|20260412152500
DG1|1||O80^Encounter for full-term uncomplicated delivery^I10||20260411|A
DG1|2||Z37.0^Single live birth^I10||20260411|A
PR1|1||59400^Routine obstetric care^CPT4|^Vaginal delivery|20260411082000|||||3751842960^Garrison^Michelle^A^^^MD^^^^NPI
```

---

## 3. ORU^R01 - Basic metabolic panel results

```
MSH|^~\&|MILLENNIUM|JPSHN^2.16.840.1.113883.3.1901^ISO|LAB_RECV|TX_HIE|20260413101500||ORU^R01^ORU_R01|CERN20260413101500003|P|2.5.1|||AL|NE
PID|1||MRN30003^^^JPSHN^MR||Hutton^Denise^Lorraine^^Ms.^||19680502|F||2054-5^Black or African American^CDCREC|2818 8th Ave^^Fort Worth^TX^76110^US^H||^PRN^PH^^1^682^5537694|||D^Divorced^HL70002|||527-63-8410|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|LAB^0002^01^JPSHN^^^^N|R^Routine^HL70007|||5291740836^Whitmore^Jerome^D^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260413003^^^JPSHN^VN
ORC|RE|ORD30001^CERN|FIL30001^LAB||CM^Complete^HL70038|||20260413080000|||5291740836^Whitmore^Jerome^D^^^MD^^^^NPI
OBR|1|ORD30001^CERN|FIL30001^LAB|80048^Basic metabolic panel^CPT4|||20260413080000|||||||||5291740836^Whitmore^Jerome^D^^^MD^^^^NPI||||||20260413100000|||F
OBX|1|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||142|mg/dL^milligrams per deciliter^UCUM|74-106|H|||F|||20260413100000
OBX|2|NM|3094-0^Urea nitrogen [Mass/volume] in Serum or Plasma^LN||18|mg/dL^milligrams per deciliter^UCUM|6-20|N|||F|||20260413100000
OBX|3|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||0.9|mg/dL^milligrams per deciliter^UCUM|0.7-1.3|N|||F|||20260413100000
OBX|4|NM|2951-2^Sodium [Moles/volume] in Serum or Plasma^LN||139|mmol/L^millimoles per liter^UCUM|136-145|N|||F|||20260413100000
OBX|5|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN||4.1|mmol/L^millimoles per liter^UCUM|3.5-5.1|N|||F|||20260413100000
OBX|6|NM|2075-0^Chloride [Moles/volume] in Serum or Plasma^LN||101|mmol/L^millimoles per liter^UCUM|98-106|N|||F|||20260413100000
OBX|7|NM|1963-8^Bicarbonate [Moles/volume] in Serum or Plasma^LN||24|mmol/L^millimoles per liter^UCUM|21-31|N|||F|||20260413100000
OBX|8|NM|17861-6^Calcium [Mass/volume] in Serum or Plasma^LN||9.4|mg/dL^milligrams per deciliter^UCUM|8.5-10.5|N|||F|||20260413100000
```

---

## 4. ORM^O01 - Echocardiogram order

```
MSH|^~\&|MILLENNIUM|THR^2.16.840.1.113883.3.2102^ISO|CARD_RECV|TX_HIE|20260414090000||ORM^O01^ORM_O01|CERN20260414090000004|P|2.5.1|||AL|NE
PID|1||MRN30004^^^THR^MR||Calhoun^Timothy^Scott^^Mr.^||19580901|M||2106-3^White^CDCREC|7503 Hulen St^^Plano^TX^75024^US^H||^PRN^PH^^1^972^5533946|||M^Married^HL70002|||412-67-8934|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|CARD^0006^01^THR^^^^N|R^Routine^HL70007|||6190482537^Pembrook^Angela^R^^^MD^^^^NPI||CAR^Cardiology^HL70069||||||||||VN20260414004^^^THR^VN
ORC|NW|ORD30004^CERN||GRP30004^CERN|||||20260414085000|||6190482537^Pembrook^Angela^R^^^MD^^^^NPI|||||THR^Texas Health Resources
OBR|1|ORD30004^CERN||93306^Echocardiography transthoracic^CPT4|||20260414085000||||||||6190482537^Pembrook^Angela^R^^^MD^^^^NPI||||||||||1^Routine^HL70065
DG1|1||I50.9^Heart failure unspecified^I10||20260414|A
NTE|1||Evaluate LV function. Patient reports worsening dyspnea on exertion.
```

---

## 5. ORU^R01 - Operative note with embedded PDF (ED datatype)

```
MSH|^~\&|MILLENNIUM|JPSHN^2.16.840.1.113883.3.1901^ISO|DOC_RECV|TX_HIE|20260415140000||ORU^R01^ORU_R01|CERN20260415140000005|P|2.5.1|||AL|NE
PID|1||MRN30005^^^JPSHN^MR||Olivares^Lucia^Marisol^^Mrs.^||19800106|F||2106-3^White^CDCREC|5040 Trail Lake Dr^^Fort Worth^TX^76133^US^H||^PRN^PH^^1^682^5532178|||M^Married^HL70002|||739-24-5618|||H^Hispanic or Latino^CDCREC
PV1|1|I|SURG^4302^01^JPSHN^^^^N|U^Urgent^HL70007|||7204819365^Hargrove^Victor^Charles^^^MD^^^^NPI||GS^General Surgery^HL70069||||||||||VN20260414005^^^JPSHN^VN
ORC|RE|ORD30005^CERN|FIL30005^SURG||CM^Complete^HL70038|||20260414100000|||7204819365^Hargrove^Victor^Charles^^^MD^^^^NPI
OBR|1|ORD30005^CERN|FIL30005^SURG|28272-4^Operative note^LN|||20260414100000|||||||||7204819365^Hargrove^Victor^Charles^^^MD^^^^NPI||||||20260415135000|||F
OBX|1|ED|PDF^Operative Note^AUSPDI||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxMjMKPj4Kc3RyZWFtCkJUCi9GMSAxNCBUZgoxMDAgNzAwIFRkCihPcGVyYXRpdmUgTm90ZSkgVGoKMCAtMjAgVGQKL0YxIDExIFRmCihQcm9jZWR1cmU6IExhcGFyb3Njb3BpYyBDaG9sZWN5c3RlY3RvbXkpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoK||||||F|||20260415135000
OBX|2|FT|28272-4^Operative note narrative^LN||OPERATIVE NOTE\.br\Procedure: Laparoscopic cholecystectomy\.br\Surgeon: Victor Charles Hargrove, MD\.br\Anesthesia: General endotracheal\.br\Findings: Chronically inflamed gallbladder with multiple stones\.br\Estimated Blood Loss: 25 mL\.br\Complications: None\.br\Specimens: Gallbladder sent to pathology||||||F|||20260415135000
```

---

## 6. SIU^S12 - Cardiology follow-up appointment

```
MSH|^~\&|MILLENNIUM|THR^2.16.840.1.113883.3.2102^ISO|SCHED_RECV|TX_HIE|20260416110000||SIU^S12^SIU_S12|CERN20260416110000006|P|2.5.1|||AL|NE
SCH|APPT30006^CERN||||||CARDFU^Cardiology Follow-up^L|20^MIN|MIN^Minutes^ISO+|^^^20260423093000^^20^MIN|||||6190482537^Pembrook^Angela^R^^^MD^^^^NPI|^PRN^PH^^1^817^5537100|||||6190482537^Pembrook^Angela^R^^^MD^^^^NPI|||||Booked
PID|1||MRN30006^^^THR^MR||Eldridge^Dorothy^Christine^^Mrs.^||19510418|F||2106-3^White^CDCREC|3200 W Lancaster Ave^^Fort Worth^TX^76107^US^H||^PRN^PH^^1^817^5534321|||W^Widowed^HL70002|||823-46-9015|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|CARD^0006^01^THR^^^^N|R^Routine^HL70007|||6190482537^Pembrook^Angela^R^^^MD^^^^NPI||CAR^Cardiology^HL70069||||||||||VN20260416006^^^THR^VN
RGS|1||CARD_CLINIC
AIS|1||99214^Office visit established level 4^CPT4|20260423093000|||20^MIN|MIN^Minutes^ISO+||Confirmed
AIG|1||6190482537^Pembrook^Angela^R^^^MD^^^^NPI|||||20260423093000|||20^MIN
AIL|1||CARD^0006^01^THR|||||20260423093000|||20^MIN
```

---

## 7. ADT^A08 - Insurance information update

```
MSH|^~\&|MILLENNIUM|JPSHN^2.16.840.1.113883.3.1901^ISO|ADT_RECV|TX_HIE|20260417140000||ADT^A08^ADT_A01|CERN20260417140000007|P|2.5.1|||AL|NE
EVN|A08|20260417135500|||REGIST^Ashford^Tracy^A^^^ADM|20260417135500
PID|1||MRN30007^^^JPSHN^MR||Menchaca^Ricardo^Fernando^^Mr.^||19850919|M||2106-3^White^CDCREC|6812 Meadowbrook Dr^^Fort Worth^TX^76112^US^H||^PRN^PH^^1^682^5538923|||M^Married^HL70002|||461-82-7039|||H^Hispanic or Latino^CDCREC
PV1|1|O|CLI^0010^01^JPSHN^^^^N|R^Routine^HL70007|||8362015749^Thornton^Patricia^M^^^MD^^^^NPI||FM^Family Medicine^HL70069||||||||||VN20260417007^^^JPSHN^VN
IN1|1|UHC001|87726^UnitedHealthcare|UHC^^Dallas^TX^75201|||||UHCGRP||||||Menchaca^Ricardo^Fernando|SE^Self^HL70063|19850919|6812 Meadowbrook Dr^^Fort Worth^TX^76112^US|Y||1||||||||||||||UHCPOL456789
IN2|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||Menchaca^Ricardo^Fernando
```

---

## 8. RDE^O11 - Antibiotic IV order

```
MSH|^~\&|MILLENNIUM|THR^2.16.840.1.113883.3.2102^ISO|PHARM_RECV|TX_HIE|20260418160000||RDE^O11^RDE_O11|CERN20260418160000008|P|2.5.1|||AL|NE
PID|1||MRN30008^^^THR^MR||Kendricks^Jerome^Darnell^^Mr.^||19480721|M||2054-5^Black or African American^CDCREC|5501 E Lancaster Ave^^Arlington^TX^76014^US^H||^PRN^PH^^1^817^5536234|||W^Widowed^HL70002|||293-57-8146|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|MED^3105^01^THR^^^^N|E^Emergency^HL70007|||9183462057^Lattimore^Denise^K^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260417008^^^THR^VN
ORC|NW|ORD30008^CERN||GRP30008^CERN|||||20260418153000|||9183462057^Lattimore^Denise^K^^^MD^^^^NPI
RXE|1^Q8H^HL70335|3640^Piperacillin-tazobactam 3.375g IV^NDC|3.375|3.375|g^grams^ISO+|INJ^Injection^HL70292||||||0|||9183462057^Lattimore^Denise^K^^^MD^^^^NPI||||||||||||||||30^MIN
RXR|IV^Intravenous^HL70162|LA^Left Arm^HL70163
RXC|B|0.9% Sodium Chloride|100|mL^milliliters^ISO+
DG1|1||J18.1^Lobar pneumonia unspecified organism^I10||20260417|A
```

---

## 9. MDM^T02 - Radiology interpretation transcription

```
MSH|^~\&|MILLENNIUM|JPSHN^2.16.840.1.113883.3.1901^ISO|DOC_RECV|TX_HIE|20260419100000||MDM^T02^MDM_T02|CERN20260419100000009|P|2.5.1|||AL|NE
EVN|T02|20260419095500
PID|1||MRN30009^^^JPSHN^MR||Venkatesh^Rohit^Anand^^Mr.^||19750213|M||2028-9^Asian^CDCREC|3720 E Rosedale St^^Fort Worth^TX^76105^US^H||^PRN^PH^^1^682^5533019|||M^Married^HL70002|||715-38-2964|||N^Not Hispanic or Latino^CDCREC
PV1|1|O|RAD^0005^01^JPSHN^^^^N|R^Routine^HL70007|||0247183956^Caldwell^James^H^^^MD^^^^NPI||RAD^Radiology^HL70069||||||||||VN20260419009^^^JPSHN^VN
TXA|1|RI^Radiology Interpretation^HL70270|TX^Text^HL70191||20260419095000||||||DOC30009^JPSHN|||||AU^Authenticated^HL70271
OBX|1|TX|36643-5^Chest X-ray interpretation^LN||CHEST X-RAY PA AND LATERAL\.br\\.br\CLINICAL INDICATION: Cough and fever\.br\\.br\FINDINGS:\.br\Heart size normal. No cardiomegaly. Lungs are clear bilaterally. No focal consolidation, pleural effusion, or pneumothorax. Mediastinal contour is normal. Bony structures are intact.\.br\\.br\IMPRESSION:\.br\No acute cardiopulmonary abnormality.||||||F|||20260419095000
```

---

## 10. DFT^P03 - Inpatient surgical charge

```
MSH|^~\&|MILLENNIUM|THR^2.16.840.1.113883.3.2102^ISO|FIN_RECV|TX_HIE|20260420140000||DFT^P03^DFT_P03|CERN20260420140000010|P|2.5.1|||AL|NE
EVN|P03|20260420135500
PID|1||MRN30010^^^THR^MR||Farnsworth^Alice^Louise^^Mrs.^||19630711|F||2106-3^White^CDCREC|8900 Camp Bowie Blvd^^Denton^TX^76201^US^H||^PRN^PH^^1^817^5537012|||M^Married^HL70002|||184-53-6729|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|SURG^4201^01^THR^^^^N|U^Urgent^HL70007|||1038274659^Stratton^Robert^W^^^MD^^^^NPI||GS^General Surgery^HL70069||||||||||VN20260419010^^^THR^VN|||||||||||||||||||||||||||20260419070000|20260420130000
FT1|1|||20260419090000|20260419120000|CG^Charge^HL70017|47562^Laparoscopic cholecystectomy^CPT4||1|||||||SURG^4201^01^THR|||||1038274659^Stratton^Robert^W^^^MD^^^^NPI
FT1|2|||20260419090000|20260419120000|CG^Charge^HL70017|00790^Anesthesia intraperitoneal procedures upper abdomen^CPT4||1|||||||ANES^0001^01^THR
FT1|3|||20260419130000|20260419130000|CG^Charge^HL70017|88305^Surgical pathology^CPT4||1|||||||PATH^0001^01^THR
DG1|1||K80.10^Calculus of gallbladder with chronic cholecystitis without obstruction^I10||20260419|A
```

---

## 11. VXU^V04 - Adult influenza vaccination

```
MSH|^~\&|MILLENNIUM|JPSHN^2.16.840.1.113883.3.1901^ISO|IMMTRAC2|TX_DSHS|20260421103000||VXU^V04^VXU_V04|CERN20260421103000011|P|2.5.1|||ER|AL
PID|1||MRN30011^^^JPSHN^MR||Irvine^Brenda^Monique^^Ms.^||19710305|F||2054-5^Black or African American^CDCREC|2001 N Sylvania Ave^^Fort Worth^TX^76111^US^H||^PRN^PH^^1^682^5534890|||D^Divorced^HL70002|||603-49-2187|||N^Not Hispanic or Latino^CDCREC
PD1||||8362015749^Thornton^Patricia^M^^^MD^^^^NPI
NK1|1|Irvine^Marcus^Terrell^^Mr.|SON^Son^HL70063|2001 N Sylvania Ave^^Fort Worth^TX^76111^US|^PRN^PH^^1^682^5534891||EC^Emergency Contact^HL70131
PV1|1|O|CLI^0010^01^JPSHN^^^^N|R^Routine^HL70007|||8362015749^Thornton^Patricia^M^^^MD^^^^NPI||FM^Family Medicine^HL70069||||||||||VN20260421011^^^JPSHN^VN
ORC|RE|ORD30011^CERN||GRP30011^CERN|CM^Complete^HL70038|||20260421100000|||8362015749^Thornton^Patricia^M^^^MD^^^^NPI
RXA|0|1|20260421100000||197^Influenza high-dose injectable^CVX|0.7|mL^milliliters^ISO+||00^New immunization record^NIP001||||||49281-0703-55^^NDC|||||CP^Complete^HL70322
RXR|IM^Intramuscular^HL70162|LD^Left Deltoid^HL70163
OBX|1|CE|64994-7^Vaccine funding program eligibility category^LN||V05^VFC eligible uninsured^HL70064||||||F
OBX|2|TS|29768-9^Date vaccine information statement published^LN||20230810||||||F
OBX|3|TS|29769-7^Date vaccine information statement presented^LN||20260421||||||F
```

---

## 12. ADT^A04 - Outpatient registration for lab work

```
MSH|^~\&|MILLENNIUM|THR^2.16.840.1.113883.3.2102^ISO|ADT_RECV|TX_HIE|20260422070000||ADT^A04^ADT_A01|CERN20260422070000012|P|2.5.1|||AL|NE
EVN|A04|20260422065500|||REG^Waverly^Carol^S^^^ADM|20260422065500
PID|1||MRN30012^^^THR^MR||Palacios^Pedro^Enrique^^Mr.^||19880624|M||2106-3^White^CDCREC|1900 Hemphill St^^Dallas^TX^75208^US^H||^PRN^PH^^1^214^5531789|||S^Single^HL70002|||847-20-6193|||H^Hispanic or Latino^CDCREC
PV1|1|O|LAB^0001^01^THR^^^^N|R^Routine^HL70007|||2059381476^Kingsley^Sandra^L^^^MD^^^^NPI||FM^Family Medicine^HL70069||||||||||VN20260422012^^^THR^VN
PV2|||^Annual lab work, fasting
DG1|1||Z00.00^Encounter for general adult medical examination without abnormal findings^I10||20260422|A
```

---

## 13. ORU^R01 - Microbiology culture with embedded PDF (ED datatype)

```
MSH|^~\&|MILLENNIUM|JPSHN^2.16.840.1.113883.3.1901^ISO|LAB_RECV|TX_HIE|20260423160000||ORU^R01^ORU_R01|CERN20260423160000013|P|2.5.1|||AL|NE
PID|1||MRN30013^^^JPSHN^MR||Agarwal^Priya^Sunita^^Ms.^||19790820|F||2028-9^Asian^CDCREC|4200 South Fwy^^Fort Worth^TX^76115^US^H||^PRN^PH^^1^682^5539567|||M^Married^HL70002|||936-14-5782|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|MED^3201^02^JPSHN^^^^N|E^Emergency^HL70007|||3607294185^Winslow^David^S^^^MD^^^^NPI||IM^Internal Medicine^HL70069||||||||||VN20260421013^^^JPSHN^VN
ORC|RE|ORD30013^CERN|FIL30013^MICRO||CM^Complete^HL70038|||20260421100000|||3607294185^Winslow^David^S^^^MD^^^^NPI
OBR|1|ORD30013^CERN|FIL30013^MICRO|87070^Culture bacterial blood^CPT4|||20260421100000|||||||||3607294185^Winslow^David^S^^^MD^^^^NPI||||||20260423150000|||F
OBX|1|FT|600-7^Bacteria identified in Blood by Culture^LN||Organism: Escherichia coli\.br\Colony count: >100,000 CFU/mL\.br\\.br\Susceptibility Results:\.br\Ampicillin: Resistant (MIC >32)\.br\Ceftriaxone: Susceptible (MIC <=1)\.br\Ciprofloxacin: Susceptible (MIC <=0.25)\.br\Gentamicin: Susceptible (MIC <=1)\.br\Piperacillin-Tazobactam: Susceptible (MIC <=4)\.br\Trimethoprim-Sulfamethoxazole: Susceptible (MIC <=1)||||||F|||20260423150000
OBX|2|ED|PDF^Microbiology Report^AUSPDI||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCAxNTUKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihNaWNyb2Jpb2xvZ3kgQ3VsdHVyZSBSZXBvcnQpIFRqCjAgLTIwIFRkCi9GMSAxMCBUZgooU3BlY2ltZW46IEJsb29kIEN1bHR1cmUpIFRqCjAgLTIwIFRkCihPcmdhbmlzbTogRS4gY29saSkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago=||||||F|||20260423150000
```

---

## 14. ADT^A28 - New patient registration in master patient index

```
MSH|^~\&|MILLENNIUM|THR^2.16.840.1.113883.3.2102^ISO|MPI_RECV|TX_HIE|20260424090000||ADT^A28^ADT_A05|CERN20260424090000014|P|2.5.1|||AL|NE
EVN|A28|20260424085500
PID|1||MRN30014^^^THR^MR~502-71-8364^^^USSSA^SS||Harada^Kenji^Takashi^^Mr.^||19920310|M||2028-9^Asian^CDCREC|2701 W Berry St^^McKinney^TX^75070^US^H||^PRN^PH^^1^469^5532345|^WPN^PH^^1^469^5538901||S^Single^HL70002|||502-71-8364|||N^Not Hispanic or Latino^CDCREC
PD1|||Texas Health Fort Worth^^^^NPI|2059381476^Kingsley^Sandra^L^^^MD^^^^NPI
NK1|1|Harada^Yuki^Emiko^^Mrs.|MTH^Mother^HL70063|2701 W Berry St^^McKinney^TX^75070^US|^PRN^PH^^1^469^5532346||EC^Emergency Contact^HL70131
```

---

## 15. ADT^A02 - Patient transfer to ICU

```
MSH|^~\&|MILLENNIUM|JPSHN^2.16.840.1.113883.3.1901^ISO|ADT_RECV|TX_HIE|20260425020000||ADT^A02^ADT_A02|CERN20260425020000015|P|2.5.1|||AL|NE
EVN|A02|20260425015500|||ICURN^Prescott^Ashley^R^^^RN|20260425015500
PID|1||MRN30015^^^JPSHN^MR||Jarrett^Walter^Terrence^^Mr.^||19530429|M||2054-5^Black or African American^CDCREC|1601 Pennsylvania Ave^^Fort Worth^TX^76104^US^H||^PRN^PH^^1^682^5537821|||M^Married^HL70002|||278-64-9301|||N^Not Hispanic or Latino^CDCREC
PV1|1|I|ICU^1002^01^JPSHN^^^^N|E^Emergency^HL70007|||4081523967^Montague^Denise^M^^^MD^^^^NPI||CCM^Critical Care^HL70069||||||T^Transfer^HL70007|||||VN20260424015^^^JPSHN^VN
PV2|||^Respiratory decompensation requiring intubation
```

---

## 16. ADT^A40 - Patient merge correcting duplicate MRN

```
MSH|^~\&|MILLENNIUM|THR^2.16.840.1.113883.3.2102^ISO|MPI_RECV|TX_HIE|20260425160000||ADT^A40^ADT_A39|CERN20260425160000016|P|2.5.1|||AL|NE
EVN|A40|20260425155500|||HIM^Northcutt^Maria^P^^^HIM|20260425155500
PID|1||MRN30016^^^THR^MR||Dunham^Shannon^Elise^^Ms.^||19870123|F||2106-3^White^CDCREC|4100 McCart Ave^^Fort Worth^TX^76110^US^H||^PRN^PH^^1^817^5533456|||S^Single^HL70002|||581-92-4067|||N^Not Hispanic or Latino^CDCREC
MRG|MRN30016B^^^THR^MR||||||Dunham^Shannon^E
```

---

## 17. ADT^A31 - Patient phone number update

```
MSH|^~\&|MILLENNIUM|JPSHN^2.16.840.1.113883.3.1901^ISO|MPI_RECV|TX_HIE|20260426110000||ADT^A31^ADT_A05|CERN20260426110000017|P|2.5.1|||AL|NE
EVN|A31|20260426105500
PID|1||MRN30017^^^JPSHN^MR||Bartlett^Charles^Raymond^^Mr.^||19600211|M||2106-3^White^CDCREC|7200 Calmont Ave^^Fort Worth^TX^76116^US^H||^PRN^PH^^1^682^5539012|^WPN^PH^^1^817^5533478||M^Married^HL70002|||362-81-4057|||N^Not Hispanic or Latino^CDCREC
PD1|||JPS Health Network^^^^NPI|5174920638^Hensley^Susan^E^^^MD^^^^NPI
```

---

## 18. MFN^M02 - Provider credentialing master file update

```
MSH|^~\&|MILLENNIUM|THR^2.16.840.1.113883.3.2102^ISO|MF_RECV|TX_HIE|20260427090000||MFN^M02^MFN_M02|CERN20260427090000018|P|2.5.1|||AL|NE
MFI|PRA^Practitioner master file^HL70175||UPD^Update^HL70180|||NE
MFE|MAD^Add record to master file^HL70180|20260427085500||6295014738^Villarreal^Maria^Elena^^MD|CWE
STF|6295014738|U6295014738|Villarreal^Maria^Elena^^MD||F|19800515|A^Active^HL70183|||||^WPN^PH^^1^817^5531234
PRA|6295014738^Villarreal^Maria^Elena^^MD|THR^Texas Health Resources|I^Institution^HL70186|||||207Q00000X^Family Medicine^NUCC
```

---

## 19. ORM^O01 - Urinalysis order

```
MSH|^~\&|MILLENNIUM|JPSHN^2.16.840.1.113883.3.1901^ISO|LAB_RECV|TX_HIE|20260428080000||ORM^O01^ORM_O01|CERN20260428080000019|P|2.5.1|||AL|NE
PID|1||MRN30019^^^JPSHN^MR||Quintanilla^Isabella^Carmen^^Mrs.^||19780102|F||2106-3^White^CDCREC|3100 Purington Ave^^Fort Worth^TX^76103^US^H||^PRN^PH^^1^682^5535678|||M^Married^HL70002|||428-60-3917|||H^Hispanic or Latino^CDCREC
PV1|1|O|CLI^0010^01^JPSHN^^^^N|R^Routine^HL70007|||8362015749^Thornton^Patricia^M^^^MD^^^^NPI||FM^Family Medicine^HL70069||||||||||VN20260428019^^^JPSHN^VN
ORC|NW|ORD30019^CERN||GRP30019^CERN|||||20260428075000|||8362015749^Thornton^Patricia^M^^^MD^^^^NPI
OBR|1|ORD30019^CERN||81001^Urinalysis automated with microscopy^CPT4|||20260428075000||||||||8362015749^Thornton^Patricia^M^^^MD^^^^NPI||||||||||1^Routine^HL70065
DG1|1||N39.0^Urinary tract infection site not specified^I10||20260428|A
NTE|1||Patient reports dysuria and frequency for 2 days. No fever.
```

---

## 20. ACK - Negative acknowledgment for rejected message

```
MSH|^~\&|LAB_RECV|TX_HIE|MILLENNIUM|JPSHN^2.16.840.1.113883.3.1901^ISO|20260429080000||ACK^R01^ACK|CERN20260429080000020|P|2.5.1|||AL|NE
MSA|AE|CERN20260413101500003|Unknown patient identifier in PID-3|207
ERR||PID^1^3|204^Unknown key identifier^HL70357|E|||||Patient MRN not found in receiving system
```
