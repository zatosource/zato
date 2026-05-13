# MEDITECH - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to Cape Cod Hospital

```
MSH|^~\&|MEDITECH|CCH^2001^NPI|ADT_RECV|CCH_HIS|20250310091200||ADT^A01^ADT_A01|MT00001|P|2.3|||AL|NE
EVN|A01|20250310091100|||RWILS^Wilson^Rebecca^A^MD^^NPI
PID|1||CCH30012345^^^CCH^MR~318-42-7156^^^SSA^SS||Harrington^Brendan^Thomas^^Mr.||19560814|M||2106-3^White^HL70005|45 Ocean View Dr^^Hyannis^MA^02601^US||^PRN^PH^^^508^7721001||M||VN30001234|318-42-7156
PV1|1|I|MED^202^A^CCH^^^N|E|||14782^Tavares^Lucia^M^MD^^NPI||26391^Gallagher^Owen^R^MD^^NPI|MED|||1|||14782^Tavares^Lucia^M^MD^^NPI|IN||BCBS|||||||||||||||||||CCH||||20250310091100
PV2|||^Acute exacerbation of COPD
IN1|1|BCBS001^Blue Cross Blue Shield MA|7834|Blue Cross Blue Shield of Massachusetts|101 Huntington Ave^^Boston^MA^02199^US|^PRN^PH^^^800^2628282|GRP34567|||||||Harrington^Brendan^Thomas|SEL|19560814|45 Ocean View Dr^^Hyannis^MA^02601^US
NK1|1|Harrington^Patricia^^Mrs.|SPO|45 Ocean View Dr^^Hyannis^MA^02601^US|^PRN^PH^^^508^7721002||EC
DG1|1||J44.1^COPD with acute exacerbation^ICD10|||A
```

---

## 2. ORU^R01 - CBC results from South Shore Health

```
MSH|^~\&|MEDITECH|SSH^2002^NPI|LAB_RECV|SSH_HIS|20250312143000||ORU^R01^ORU_R01|MT00002|P|2.3|||AL|NE
PID|1||SSH40023456^^^SSH^MR||Fitzgerald^Siobhan^Marie^^Ms.||19780623|F||2106-3^White^HL70005|88 Washington St^^Weymouth^MA^02188^US||^PRN^PH^^^781^9341234||S||VN40002345
PV1|1|O|LAB^DRAW^A^SSH|||38214^Venkatesh^Priya^K^MD^^NPI|||||||||OUT||||||||||||||||||SSH||||20250312140000
ORC|RE|ORD11234|FIL22345||CM||||20250312143000|||38214^Venkatesh^Priya^K^MD^^NPI
OBR|1|ORD11234|FIL22345|85025^Complete Blood Count^CPT|||20250312140000|||||||||38214^Venkatesh^Priya^K^MD^^NPI||||||20250312143000||HM|F
OBX|1|NM|WBC^White Blood Cell Count^L||7.2|x10E3/uL|4.5-11.0||||F|||20250312143000
OBX|2|NM|RBC^Red Blood Cell Count^L||4.5|x10E6/uL|4.0-5.5||||F|||20250312143000
OBX|3|NM|HGB^Hemoglobin^L||13.8|g/dL|12.0-16.0||||F|||20250312143000
OBX|4|NM|HCT^Hematocrit^L||41.2|%|36.0-46.0||||F|||20250312143000
OBX|5|NM|PLT^Platelet Count^L||245|x10E3/uL|150-400||||F|||20250312143000
OBX|6|NM|MCV^Mean Corpuscular Volume^L||91.6|fL|80.0-100.0||||F|||20250312143000
```

---

## 3. ORM^O01 - Radiology order from Lowell General Hospital

```
MSH|^~\&|MEDITECH|LGH^2003^NPI|RAD_RECV|LGH_HIS|20250314080000||ORM^O01^ORM_O01|MT00003|P|2.3|||AL|NE
PID|1||LGH50034567^^^LGH^MR||Tran^Quang^Minh^^Mr.||19650212|M||2028-9^Asian^HL70005|23 Merrimack St^^Lowell^MA^01852^US||^PRN^PH^^^978^4491234||M||VN50003456
PV1|1|E|ED^BED12^A^LGH|||47213^Hennessey^Cormac^P^MD^^NPI|||||||||ER||||||||||||||||||LGH||||20250314073000
ORC|NW|ORD22345||||||^^^20250314083000^^S||20250314080000|||47213^Hennessey^Cormac^P^MD^^NPI
OBR|1|ORD22345||71046^Chest X-Ray 2 Views^CPT|||20250314083000||||||||47213^Hennessey^Cormac^P^MD^^NPI|||||||||||1^^^20250314083000^^S
DG1|1||R06.0^Dyspnea^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||62 yo male presenting with acute dyspnea and productive cough x 3 days. Hx of CHF.||||||F
```

---

## 4. ADT^A03 - Patient discharge from Cape Cod Hospital

```
MSH|^~\&|MEDITECH|CCH^2001^NPI|ADT_RECV|CCH_HIS|20250316110000||ADT^A03^ADT_A03|MT00004|P|2.3|||AL|NE
EVN|A03|20250316105900|||14782^Tavares^Lucia^M^MD^^NPI
PID|1||CCH30012345^^^CCH^MR~318-42-7156^^^SSA^SS||Harrington^Brendan^Thomas^^Mr.||19560814|M||2106-3^White^HL70005|45 Ocean View Dr^^Hyannis^MA^02601^US||^PRN^PH^^^508^7721001||M||VN30001234|318-42-7156
PV1|1|I|MED^202^A^CCH^^^N|U|||14782^Tavares^Lucia^M^MD^^NPI||26391^Gallagher^Owen^R^MD^^NPI|MED|||1|||14782^Tavares^Lucia^M^MD^^NPI|IN||BCBS|||||||||||||||||||CCH||||20250310091100|20250316110000
PV2|||^Acute exacerbation of COPD||||||20250310|20250316
DG1|1||J44.1^COPD with acute exacerbation^ICD10|||A
DG1|2||I10^Essential hypertension^ICD10|||S
```

---

## 5. DFT^P03 - Charge posting from South Shore Health

```
MSH|^~\&|MEDITECH|SSH^2002^NPI|FIN_RECV|SSH_HIS|20250318093000||DFT^P03^DFT_P03|MT00005|P|2.3|||AL|NE
EVN|P03|20250318093000
PID|1||SSH40023456^^^SSH^MR||Fitzgerald^Siobhan^Marie^^Ms.||19780623|F||2106-3^White^HL70005|88 Washington St^^Weymouth^MA^02188^US||^PRN^PH^^^781^9341234||S||VN40002345
PV1|1|O|LAB^DRAW^A^SSH|||38214^Venkatesh^Priya^K^MD^^NPI|||||||||OUT||||||||||||||||||SSH||||20250312140000
FT1|1|20250312|20250312|CG|P|85025^Complete Blood Count^CPT|1|||38214^Venkatesh^Priya^K^MD^^NPI||||||||||||||85025
FT1|2|20250312|20250312|CG|P|80053^Comprehensive Metabolic Panel^CPT|1|||38214^Venkatesh^Priya^K^MD^^NPI||||||||||||||80053
FT1|3|20250312|20250312|CG|P|83036^Hemoglobin A1c^CPT|1|||38214^Venkatesh^Priya^K^MD^^NPI||||||||||||||83036
DG1|1||E11.65^Type 2 DM with hyperglycemia^ICD10
```

---

## 6. ORU^R01 - Urinalysis results from Lowell General

```
MSH|^~\&|MEDITECH|LGH^2003^NPI|LAB_RECV|LGH_HIS|20250320110000||ORU^R01^ORU_R01|MT00006|P|2.3|||AL|NE
PID|1||LGH60045678^^^LGH^MR||Kowalski^Stefan^Adam^^Mr.||19830417|M||2106-3^White^HL70005|156 Westford St^^Lowell^MA^01851^US||^PRN^PH^^^978^6132345||M||VN60004567
PV1|1|O|LAB^DRAW^A^LGH|||51894^Delgado^Carmen^R^MD^^NPI|||||||||OUT||||||||||||||||||LGH||||20250320100000
ORC|RE|ORD33456|FIL44567||CM||||20250320110000|||51894^Delgado^Carmen^R^MD^^NPI
OBR|1|ORD33456|FIL44567|81001^Urinalysis with Microscopy^CPT|||20250320100000|||||||||51894^Delgado^Carmen^R^MD^^NPI||||||20250320110000||UA|F
OBX|1|ST|COLOR^Color^L||Yellow||Yellow||||F|||20250320110000
OBX|2|ST|CLARITY^Clarity^L||Slightly Cloudy||Clear||||F|||20250320110000
OBX|3|NM|SPGR^Specific Gravity^L||1.025||1.005-1.030||||F|||20250320110000
OBX|4|NM|PH^pH^L||6.0||5.0-8.0||||F|||20250320110000
OBX|5|ST|PROT^Protein^L||Trace||Negative|A|||F|||20250320110000
OBX|6|ST|GLUC_UA^Glucose^L||Negative||Negative||||F|||20250320110000
OBX|7|NM|WBC_UA^WBC/HPF^L||5|/HPF|0-5||||F|||20250320110000
OBX|8|NM|RBC_UA^RBC/HPF^L||2|/HPF|0-3||||F|||20250320110000
```

---

## 7. ADT^A08 - Patient update at Milford Regional Medical Center

```
MSH|^~\&|MEDITECH|MRMC^2004^NPI|ADT_RECV|MRMC_HIS|20250322140000||ADT^A08^ADT_A08|MT00007|P|2.3|||AL|NE
EVN|A08|20250322135900|||ADMIN^Admin^System^^^
PID|1||MRMC70056789^^^MRMC^MR~412-53-8914^^^SSA^SS||Pelletier^Danielle^Renee^^Mrs.||19700109|F||2106-3^White^HL70005|12 Main St^^Milford^MA^01757^US||^PRN^PH^^^508^3813456||M||VN70005678|412-53-8914
PV1|1|O|MED^CLINIC^A^MRMC|||63107^Worthington^Douglas^W^MD^^NPI|||||||||OUT||||||||||||||||||MRMC||||20250322133000
IN1|1|TFT001^Tufts Health Plan|8901|Tufts Health Plan|705 Mt Auburn St^^Watertown^MA^02472^US|^PRN^PH^^^800^4624476|GRP67890|||||||Pelletier^Danielle^Renee|SEL|19700109|12 Main St^^Milford^MA^01757^US|||||||||||||||||412538914
```

---

## 8. ORU^R01 - Thyroid panel from Cape Cod Healthcare

```
MSH|^~\&|MEDITECH|CCH^2001^NPI|LAB_RECV|CCH_HIS|20250324091500||ORU^R01^ORU_R01|MT00008|P|2.3|||AL|NE
PID|1||CCH80067890^^^CCH^MR||Almeida^Rosa^Cristina^^Mrs.||19620520|F||2131-1^Hispanic^HL70005|33 Barnstable Rd^^Falmouth^MA^02540^US||^PRN^PH^^^508^2744567||M||VN80006789
PV1|1|O|LAB^DRAW^A^CCH|||72435^Lindstrom^Astrid^E^MD^^NPI|||||||||OUT||||||||||||||||||CCH||||20250324083000
ORC|RE|ORD44567|FIL55678||CM||||20250324091500|||72435^Lindstrom^Astrid^E^MD^^NPI
OBR|1|ORD44567|FIL55678|84443^Thyroid Stimulating Hormone^CPT|||20250324083000|||||||||72435^Lindstrom^Astrid^E^MD^^NPI||||||20250324091500||CH|F
OBX|1|NM|TSH^Thyroid Stimulating Hormone^L||8.7|mIU/L|0.4-4.0|H|||F|||20250324091500
OBX|2|NM|FT4^Free T4^L||0.6|ng/dL|0.8-1.8|L|||F|||20250324091500
OBX|3|NM|FT3^Free T3^L||1.8|pg/mL|2.3-4.2|L|||F|||20250324091500
NTE|1||Results consistent with primary hypothyroidism. Consider thyroid hormone replacement.
```

---

## 9. ORM^O01 - CT abdomen order from South Shore Health

```
MSH|^~\&|MEDITECH|SSH^2002^NPI|RAD_RECV|SSH_HIS|20250326102000||ORM^O01^ORM_O01|MT00009|P|2.3|||AL|NE
PID|1||SSH90078901^^^SSH^MR||Ferreira^Marco^Luis^^Mr.||19710330|M||2106-3^White^HL70005|201 Pleasant St^^Brockton^MA^02301^US||^PRN^PH^^^508^8375678||M||VN90007890
PV1|1|O|SURG^CLINIC^A^SSH|||84529^Donahue^Brian^M^MD^^NPI|||||||||OUT||||||||||||||||||SSH||||20250326100000
ORC|NW|ORD55678||||||^^^20250327080000^^R||20250326102000|||84529^Donahue^Brian^M^MD^^NPI
OBR|1|ORD55678||74178^CT Abdomen and Pelvis with Contrast^CPT|||20250327080000||||||||84529^Donahue^Brian^M^MD^^NPI|||||||||||1^^^20250327080000^^R
DG1|1||K80.20^Calculus of gallbladder without obstruction^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||RUQ pain, elevated LFTs. Evaluate for gallbladder disease and possible biliary obstruction.||||||F
```

---

## 10. ORU^R01 - Coagulation studies with embedded PDF from Lowell General

```
MSH|^~\&|MEDITECH|LGH^2003^NPI|LAB_RECV|LGH_HIS|20250328153000||ORU^R01^ORU_R01|MT00010|P|2.3|||AL|NE
PID|1||LGH01089012^^^LGH^MR||Bouchard^Rene^Armand^^Mr.||19480726|M||2106-3^White^HL70005|78 Pawtucket Blvd^^Lowell^MA^01854^US||^PRN^PH^^^978^8526789||W||VN01008901
PV1|1|I|MED^312^A^LGH|||93748^Prescott^Nathan^E^MD^^NPI|||||||||IN||||||||||||||||||LGH||||20250326140000
ORC|RE|ORD66789|FIL77890||CM||||20250328153000|||93748^Prescott^Nathan^E^MD^^NPI
OBR|1|ORD66789|FIL77890|85610^Prothrombin Time^CPT|||20250328140000|||||||||93748^Prescott^Nathan^E^MD^^NPI||||||20250328153000||HM|F
OBX|1|NM|PT^Prothrombin Time^L||18.5|seconds|11.0-13.5|H|||F|||20250328153000
OBX|2|NM|INR^International Normalized Ratio^L||1.8||0.9-1.1|H|||F|||20250328153000
OBX|3|NM|PTT^Partial Thromboplastin Time^L||42.0|seconds|25.0-35.0|H|||F|||20250328153000
OBX|4|NM|FIBRIN^Fibrinogen^L||185|mg/dL|200-400|L|||F|||20250328153000
OBX|5|ED|COAG_RPT^Coagulation Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
NTE|1||Elevated coagulation times. Patient on warfarin therapy. Recommend dose adjustment.
```

---

## 11. ADT^A04 - ED registration at Falmouth Hospital

```
MSH|^~\&|MEDITECH|FAL^2005^NPI|ADT_RECV|CCH_HIS|20250330190000||ADT^A04^ADT_A04|MT00011|P|2.3|||AL|NE
EVN|A04|20250330185900|||REGNURSE^Triage^Nurse^^^
PID|1||FAL11090123^^^FAL^MR~527-64-8203^^^SSA^SS||Rodrigues^Daniel^Mateus^^Mr.||19870911|M||2131-1^Hispanic^HL70005|56 Main St^^Falmouth^MA^02540^US||^PRN^PH^^^508^3647890||S||VN11009012|527-64-8203
PV1|1|E|ED^BED05^A^FAL^^^N|E|||15672^Ashworth^Melanie^A^MD^^NPI|||||||||ER||||||||||||||||||FAL||||20250330190000
PV2|||^Laceration, right hand
NK1|1|Rodrigues^Lucia^^Mrs.|MTH|56 Main St^^Falmouth^MA^02540^US|^PRN^PH^^^508^3647891||EC
```

---

## 12. ORU^R01 - Lipid panel from Milford Regional

```
MSH|^~\&|MEDITECH|MRMC^2004^NPI|LAB_RECV|MRMC_HIS|20250401100000||ORU^R01^ORU_R01|MT00012|P|2.3|||AL|NE
PID|1||MRMC12001234^^^MRMC^MR||Shaughnessy^Declan^Patrick^^Mr.||19650228|M||2106-3^White^HL70005|45 Congress St^^Milford^MA^01757^US||^PRN^PH^^^508^4738901||M||VN12000123
PV1|1|O|LAB^DRAW^A^MRMC|||63107^Worthington^Douglas^W^MD^^NPI|||||||||OUT||||||||||||||||||MRMC||||20250401083000
ORC|RE|ORD77890|FIL88901||CM||||20250401100000|||63107^Worthington^Douglas^W^MD^^NPI
OBR|1|ORD77890|FIL88901|80061^Lipid Panel^CPT|||20250401083000|||||||||63107^Worthington^Douglas^W^MD^^NPI||||||20250401100000||CH|F
OBX|1|NM|CHOL^Total Cholesterol^L||248|mg/dL|<200|H|||F|||20250401100000
OBX|2|NM|TRIG^Triglycerides^L||195|mg/dL|<150|H|||F|||20250401100000
OBX|3|NM|HDL^HDL Cholesterol^L||38|mg/dL|>40|L|||F|||20250401100000
OBX|4|NM|LDL^LDL Cholesterol^L||171|mg/dL|<100|H|||F|||20250401100000
OBX|5|NM|VLDL^VLDL Cholesterol^L||39|mg/dL|5-40||||F|||20250401100000
NTE|1||Lipid profile significantly elevated. Cardiovascular risk assessment recommended.
```

---

## 13. DFT^P03 - ED charge posting from South Shore Health

```
MSH|^~\&|MEDITECH|SSH^2002^NPI|FIN_RECV|SSH_HIS|20250403141500||DFT^P03^DFT_P03|MT00013|P|2.3|||AL|NE
EVN|P03|20250403141500
PID|1||SSH13012345^^^SSH^MR||Calloway^Maureen^Elaine^^Mrs.||19800115|F||2106-3^White^HL70005|34 Summer St^^Hingham^MA^02043^US||^PRN^PH^^^781^7490123||M||VN13001234
PV1|1|E|ED^BED09^A^SSH|||24861^Hoang^Vinh^H^MD^^NPI|||||||||ER||||||||||||||||||SSH||||20250403080000|20250403140000
FT1|1|20250403|20250403|CG|P|99284^ED Visit Level 4^CPT|1|||24861^Hoang^Vinh^H^MD^^NPI||||||||||||||99284
FT1|2|20250403|20250403|CG|P|71046^Chest X-Ray 2V^CPT|1|||24861^Hoang^Vinh^H^MD^^NPI||||||||||||||71046
FT1|3|20250403|20250403|CG|P|93010^EKG Interpretation^CPT|1|||24861^Hoang^Vinh^H^MD^^NPI||||||||||||||93010
FT1|4|20250403|20250403|CG|P|80048^Basic Metabolic Panel^CPT|1|||24861^Hoang^Vinh^H^MD^^NPI||||||||||||||80048
DG1|1||R07.9^Chest pain, unspecified^ICD10
```

---

## 14. ORM^O01 - MRI brain order from Cape Cod Hospital

```
MSH|^~\&|MEDITECH|CCH^2001^NPI|RAD_RECV|CCH_HIS|20250405111500||ORM^O01^ORM_O01|MT00014|P|2.3|||AL|NE
PID|1||CCH14023456^^^CCH^MR||Pemberton^Vivian^Louise^^Mrs.||19510404|F||2106-3^White^HL70005|78 Sea St^^Barnstable^MA^02630^US||^PRN^PH^^^508^3621567||W||VN14002345
PV1|1|O|NEUR^CLINIC^A^CCH|||36281^Mulcahy^Kieran^T^MD^^NPI|||||||||OUT||||||||||||||||||CCH||||20250405100000
ORC|NW|ORD88901||||||^^^20250407080000^^R||20250405111500|||36281^Mulcahy^Kieran^T^MD^^NPI
OBR|1|ORD88901||70553^MRI Brain with and without Contrast^CPT|||20250407080000||||||||36281^Mulcahy^Kieran^T^MD^^NPI|||||||||||1^^^20250407080000^^R
DG1|1||G43.909^Migraine, unspecified, not intractable^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||74 yo female with new-onset severe headaches and visual disturbance. Rule out mass lesion.||||||F
```

---

## 15. ORU^R01 - Blood bank results with embedded report from South Shore

```
MSH|^~\&|MEDITECH|SSH^2002^NPI|LAB_RECV|SSH_HIS|20250407160000||ORU^R01^ORU_R01|MT00015|P|2.3|||AL|NE
PID|1||SSH15034567^^^SSH^MR||Rahmani^Dariush^Omid^^Mr.||19590118|M||2106-3^White^HL70005|45 Union St^^Quincy^MA^02169^US||^PRN^PH^^^617^8482345||M||VN15003456
PV1|1|I|SURG^4E^B^SSH|||49172^Esposito^Vincent^A^MD^^NPI|||||||||IN||||||||||||||||||SSH||||20250406060000
ORC|RE|ORD99012|BB12345||CM||||20250407160000|||49172^Esposito^Vincent^A^MD^^NPI
OBR|1|ORD99012|BB12345|86900^Blood Type and Screen^CPT|||20250406063000|||||||||49172^Esposito^Vincent^A^MD^^NPI||||||20250407160000||BB|F
OBX|1|ST|ABO^ABO Type^L||A||||||F|||20250407160000
OBX|2|ST|RH^Rh Type^L||Positive||||||F|||20250407160000
OBX|3|ST|SCREEN^Antibody Screen^L||Negative||||||F|||20250407160000
OBX|4|TX|XMATCH^Crossmatch^L||2 units PRBCs crossmatched and compatible. Available for surgery.||||||F|||20250407160000
OBX|5|ED|BB_RPT^Blood Bank Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 16. ADT^A01 - Admission to Nashoba Valley Medical Center

```
MSH|^~\&|MEDITECH|NVMC^2006^NPI|ADT_RECV|NVMC_HIS|20250409201500||ADT^A01^ADT_A01|MT00016|P|2.3|||AL|NE
EVN|A01|20250409201400|||58314^Kirkpatrick^Leonard^L^MD^^NPI
PID|1||NVMC16045678^^^NVMC^MR~631-78-2045^^^SSA^SS||Bergstrom^Viktor^Emil^^Mr.||19730624|M||2106-3^White^HL70005|89 Great Rd^^Ayer^MA^01432^US||^PRN^PH^^^978^7723456||M||VN16004567|631-78-2045
PV1|1|I|MED^104^A^NVMC^^^N|U|||58314^Kirkpatrick^Leonard^L^MD^^NPI||61845^Subramanian^Lakshmi^S^MD^^NPI|MED|||1|||58314^Kirkpatrick^Leonard^L^MD^^NPI|IN||AETNA|||||||||||||||||||NVMC||||20250409201400
PV2|||^Acute pancreatitis
DG1|1||K85.9^Acute pancreatitis, unspecified^ICD10|||A
IN1|1|AET001^Aetna|5678|Aetna|151 Farmington Ave^^Hartford^CT^06156^US|^PRN^PH^^^800^8722862|GRP78901|||||||Bergstrom^Viktor^Emil|SEL|19730624|89 Great Rd^^Ayer^MA^01432^US
NK1|1|Bergstrom^Karin^^Mrs.|SPO|89 Great Rd^^Ayer^MA^01432^US|^PRN^PH^^^978^7723457||EC
```

---

## 17. ORU^R01 - Troponin serial results from Lowell General

```
MSH|^~\&|MEDITECH|LGH^2003^NPI|LAB_RECV|LGH_HIS|20250411043000||ORU^R01^ORU_R01|MT00017|P|2.3|||AL|NE
PID|1||LGH17056789^^^LGH^MR||Cavanaugh^Liam^Xavier^^Mr.||19580903|M||2106-3^White^HL70005|234 Bridge St^^Lowell^MA^01850^US||^PRN^PH^^^978^2614567||M||VN17005678
PV1|1|E|ED^BED02^A^LGH|||71643^Watanabe^Kenji^R^MD^^NPI|||||||||ER||||||||||||||||||LGH||||20250410230000
ORC|RE|ORD10123|FIL21234||CM||||20250411043000|||71643^Watanabe^Kenji^R^MD^^NPI
OBR|1|ORD10123|FIL21234|93971^Troponin I Serial^L|||20250410233000|||||||||71643^Watanabe^Kenji^R^MD^^NPI||||||20250411043000||CH|F
OBX|1|NM|TROP_0^Troponin I (0 hr)^L||0.04|ng/mL|0.00-0.04||||F|||20250410233000
OBX|2|NM|TROP_3^Troponin I (3 hr)^L||0.12|ng/mL|0.00-0.04|H|||F|||20250411023000
OBX|3|NM|TROP_6^Troponin I (6 hr)^L||0.45|ng/mL|0.00-0.04|HH|||F|||20250411043000
NTE|1||Rising troponin trend consistent with acute myocardial injury. Cardiology consultation recommended.
```

---

## 18. ORM^O01 - Ultrasound order from Milford Regional

```
MSH|^~\&|MEDITECH|MRMC^2004^NPI|RAD_RECV|MRMC_HIS|20250413083000||ORM^O01^ORM_O01|MT00018|P|2.3|||AL|NE
PID|1||MRMC18067890^^^MRMC^MR||Gauthier^Annette^Josette^^Ms.||19850712|F||2106-3^White^HL70005|67 Purchase St^^Milford^MA^01757^US||^PRN^PH^^^508^6319012||S||VN18006789
PV1|1|O|OB^CLINIC^A^MRMC|||82756^Wu^Shan^Li^MD^^NPI|||||||||OUT||||||||||||||||||MRMC||||20250413080000
ORC|NW|ORD21234||||||^^^20250415090000^^R||20250413083000|||82756^Wu^Shan^Li^MD^^NPI
OBR|1|ORD21234||76805^OB Ultrasound Complete^CPT|||20250415090000||||||||82756^Wu^Shan^Li^MD^^NPI|||||||||||1^^^20250415090000^^R
DG1|1||Z34.02^Encounter for supervision of normal second pregnancy^ICD10
OBX|1|TX|CLIN_INFO^Clinical Information^L||G2P1, 20 weeks gestation. Routine anatomy scan.||||||F
```

---

## 19. ADT^A02 - Patient transfer at Cape Cod Hospital

```
MSH|^~\&|MEDITECH|CCH^2001^NPI|ADT_RECV|CCH_HIS|20250415063000||ADT^A02^ADT_A02|MT00019|P|2.3|||AL|NE
EVN|A02|20250415062900|||91548^Driscoll^Ronan^P^MD^^NPI
PID|1||CCH19078901^^^CCH^MR||Correia^Augusto^Henrique^^Mr.||19410305|M||2106-3^White^HL70005|23 Old Colony Rd^^Sandwich^MA^02563^US||^PRN^PH^^^508^8830234||W||VN19007890
PV1|1|I|ICU^BED03^A^CCH^^^N|E|||91548^Driscoll^Ronan^P^MD^^NPI||05267^Noonan^Sienna^K^MD^^NPI|MED|||2|||91548^Driscoll^Ronan^P^MD^^NPI|IN||MEDCR|||||||||||||||||||CCH||||20250413180000
PV2|||^Acute respiratory failure with hypoxia
DG1|1||J96.01^Acute respiratory failure with hypoxia^ICD10|||A
```

---

## 20. ORU^R01 - Blood gas results from South Shore Health

```
MSH|^~\&|MEDITECH|SSH^2002^NPI|LAB_RECV|SSH_HIS|20250417082000||ORU^R01^ORU_R01|MT00020|P|2.3|||AL|NE
PID|1||SSH20089012^^^SSH^MR||Connolly^Eileen^Frances^^Mrs.||19550622|F||2106-3^White^HL70005|156 Nantasket Ave^^Hull^MA^02045^US||^PRN^PH^^^781^9251234||W||VN20008901
PV1|1|I|ICU^BED06^A^SSH|||17394^Stanton^Gregory^D^MD^^NPI|||||||||IN||||||||||||||||||SSH||||20250416220000
ORC|RE|ORD32345|FIL43456||CM||||20250417082000|||17394^Stanton^Gregory^D^MD^^NPI
OBR|1|ORD32345|FIL43456|82803^Arterial Blood Gas^CPT|||20250417080000|||||||||17394^Stanton^Gregory^D^MD^^NPI||||||20250417082000||BG|F
OBX|1|NM|PH_ABG^pH^L||7.32||7.35-7.45|L|||F|||20250417082000
OBX|2|NM|PCO2^pCO2^L||48|mmHg|35-45|H|||F|||20250417082000
OBX|3|NM|PO2^pO2^L||68|mmHg|80-100|L|||F|||20250417082000
OBX|4|NM|HCO3^Bicarbonate^L||24|mmol/L|22-26||||F|||20250417082000
OBX|5|NM|O2SAT^Oxygen Saturation^L||92|%|95-99|L|||F|||20250417082000
OBX|6|NM|BE^Base Excess^L||-2.1|mmol/L|-2.0-2.0|L|||F|||20250417082000
NTE|1||Mild respiratory acidosis with hypoxemia. Correlate with clinical status and ventilator settings.
```
