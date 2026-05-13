# Epic (EpicCare) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission at NYU Langone

```
MSH|^~\&|EPIC|NYU_LANGONE|DOWNSTREAM|NYU_HIE|20250312143022||ADT^A01^ADT_A01|MSG20250312143022001|P|2.5.1|||AL|NE||ASCII|||
EVN|A01|20250312143022||ADM_TRIGGER|JSMITH^Smith^Jane^M^^^RN|20250312142500|NYU_LANGONE
PID|1||MRN10045223^^^NYU_LANGONE^MR~529-41-7803^^^SSA^SS||Hernandez^Marisol^T^^Mrs.||19790610|F||2106-3^White^CDCREC|310 E 23rd St^^New York^NY^10010^US^H||^PRN^PH^^^212^6618923|^WPN^PH^^^212^6619901||M^Married^HL70002|||529-41-7803|||H^Hispanic^HL70189||||||N
PD1|||NYU LANGONE MEDICAL CENTER^^10065|1890234567^Okafor^Chibueze^N^^^MD^NPI||||||||N
NK1|1|Hernandez^Rafael^J^^Mr.|SPO^Spouse^HL70063||^PRN^PH^^^212^6618924||EC^Emergency Contact^HL70131
NK1|2|Hernandez^Gloria^M^^Mrs.|MTH^Mother^HL70063||^PRN^PH^^^718^4423321||EC^Emergency Contact^HL70131
PV1|1|I|4EAST^4E12^A^NYU_LANGONE^^^^4EAST||||1890234567^Okafor^Chibueze^N^^^MD^NPI|9012345678^Lieberman^Aaron^D^^^MD^NPI|MED||||7|||1890234567^Okafor^Chibueze^N^^^MD^NPI|IN||SELF|||||||||||||||AI|||20250312143000|||||V
PV2|||^Chest pain with shortness of breath||||||||2|||||||||N|||||||||||A|20250312143000
IN1|1|BCBS001^Blue Cross Blue Shield of NY|71412|BCBS New York|PO Box 1407^^New York^NY^10116^US|||GRP123456|||20240101||||Hernandez^Marisol^T|SEL^Self^HL70063|19790610|310 E 23rd St^^New York^NY^10010^US|||||A|||||||F||||||BCN334455667
IN1|2|MDC001^Medicaid NY|99123|NY Medicaid|PO Box 4220^^Albany^NY^12204^US|||||||20240101||||Hernandez^Marisol^T|SEL^Self^HL70063|19790610|310 E 23rd St^^New York^NY^10010^US|||||A|||||||F||||||MCD778899001
DG1|1||I20.0^Unstable angina^ICD10|||A
DG1|2||R06.00^Dyspnea unspecified^ICD10|||A
GT1|1||Hernandez^Marisol^T^^Mrs.||310 E 23rd St^^New York^NY^10010^US|^PRN^PH^^^212^6618923|||||SEL^Self^HL70063
```

---

## 2. ADT^A04 - Emergency registration at Mount Sinai

```
MSH|^~\&|EPIC|MOUNT_SINAI|RADIOLOGY|MOUNT_SINAI_RIS|20250415082145||ADT^A04^ADT_A04|MSG20250415082145002|P|2.5.1|||AL|NE||ASCII|||
EVN|A04|20250415082145||REG_TRIGGER|MJONES^Jones^Michael^^^REG|20250415081900|MOUNT_SINAI
PID|1||MRN20098712^^^MOUNT_SINAI^MR||Thompson^DeShawn^Maurice^^Mr.||19930515|M||2054-5^Black or African American^CDCREC|1422 Grand Concourse^^Bronx^NY^10456^US^H||^PRN^PH^^^718^5934490|||S^Single^HL70002|||281-53-9012|||N^Non-Hispanic^HL70189||||||N
PD1|||MOUNT SINAI HOSPITAL^^10029|5012348976^Krishnamurthy^Priya^S^^^MD^NPI||||||||N
NK1|1|Thompson^Lorraine^D^^Mrs.|MTH^Mother^HL70063||^PRN^PH^^^718^5934491||EC^Emergency Contact^HL70131
PV1|1|E|ED^^^MOUNT_SINAI^^^^ED||||5012348976^Krishnamurthy^Priya^S^^^MD^NPI||EM||||1|||5012348976^Krishnamurthy^Priya^S^^^MD^NPI|EM||SELF|||||||||||||||AI|||20250415082100|||||V
PV2|||^Left ankle injury after fall||||||||3|||||||||N
IN1|1|AETNA001^Aetna|62308|Aetna Inc|151 Farmington Ave^^Hartford^CT^06156^US|||GRP789012|||20240601||||Thompson^DeShawn^Maurice|SEL^Self^HL70063|19930515|1422 Grand Concourse^^Bronx^NY^10456^US|||||A|||||||M||||||AET901234567
DG1|1||S82.001A^Fracture of left patella initial^ICD10|||W
GT1|1||Thompson^DeShawn^Maurice^^Mr.||1422 Grand Concourse^^Bronx^NY^10456^US|^PRN^PH^^^718^5934490|||||SEL^Self^HL70063
```

---

## 3. ADT^A03 - Discharge from NewYork-Presbyterian

```
MSH|^~\&|EPIC|NYP_COLUMBIA|PHARMACY|NYP_PHARM|20250520161530||ADT^A03^ADT_A03|MSG20250520161530003|P|2.5.1|||AL|NE||ASCII|||
EVN|A03|20250520161530||DISCH_TRIGGER|KLEE^Lee^Karen^^^RN|20250520161000|NYP_COLUMBIA
PID|1||MRN30056789^^^NYP^MR~173-48-9012^^^SSA^SS||Cho^Sung-Ho^^^Mr.||19640918|M||2028-9^Asian^CDCREC|88-22 Elmhurst Ave^^Queens^NY^11373^US^H||^PRN^PH^^^718^2218812|^WPN^PH^^^212^5511234||M^Married^HL70002|||173-48-9012|||N^Non-Hispanic^HL70189||||||N
PD1|||NYP COLUMBIA UNIVERSITY MEDICAL CENTER^^10032|7012345689^Volkov^Sergei^M^^^MD^NPI||||||||N
NK1|1|Cho^Eun-Jung^^^Mrs.|SPO^Spouse^HL70063||^PRN^PH^^^718^2218813||EC^Emergency Contact^HL70131
PV1|1|I|6NORTH^6N04^B^NYP_COLUMBIA^^^^6NORTH||||7012345689^Volkov^Sergei^M^^^MD^NPI|2890123456^Baptiste^Claudine^R^^^MD^NPI|SURG||||7|||7012345689^Volkov^Sergei^M^^^MD^NPI|IN||SELF|||||||||||||||AI|||20250517083000||20250520161500|||V
PV2|||^Laparoscopic cholecystectomy||||||||5|||||||||N|||||||||||A|20250520161500
DG1|1||K80.20^Calculus of gallbladder without obstruction^ICD10|||A
DG1|2||K81.0^Acute cholecystitis^ICD10|||A
PR1|1||47562^Laparoscopic cholecystectomy^CPT4|Laparoscopic cholecystectomy|20250518|0
```

---

## 4. ORM^O01 - Lab order from Northwell Health

```
MSH|^~\&|EPIC|NORTHWELL_LIJ|LABCORP|LABCORP_NY|20250601091500||ORM^O01^ORM_O01|MSG20250601091500004|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN40012345^^^NORTHWELL^MR||Sokolova^Tatiana^V^^Ms.||19880205|F||2106-3^White^CDCREC|42-18 Crescent St^^Long Island City^NY^11101^US^H||^PRN^PH^^^718^3893201|||S^Single^HL70002|||410-72-8834|||N^Non-Hispanic^HL70189||||||N
PV1|1|O|LABDRAW^^^NORTHWELL_LIJ^^^^LAB||||3890124567^Adeyemi^Oluwaseun^K^^^MD^NPI||MED||||1|||3890124567^Adeyemi^Oluwaseun^K^^^MD^NPI|OP||SELF|||||||||||||||AI|||20250601091000|||||V
ORC|NW|ORD20250601001^EPIC|LAB20250601001^LABCORP||CM||||20250601091500|JDOE^Doe^Janet^^^RN||3890124567^Adeyemi^Oluwaseun^K^^^MD^NPI|NORTHWELL_LIJ|||20250601091500||NORTHWELL^Northwell Health^L|42-18 Crescent St^^Long Island City^NY^11101^US|^PRN^PH^^^718^3893201
OBR|1|ORD20250601001^EPIC|LAB20250601001^LABCORP|80053^Comprehensive Metabolic Panel^CPT4|||20250601091500|||||||||3890124567^Adeyemi^Oluwaseun^K^^^MD^NPI||||||20250601091500|||F
OBR|2|ORD20250601002^EPIC|LAB20250601002^LABCORP|85025^Complete Blood Count^CPT4|||20250601091500|||||||||3890124567^Adeyemi^Oluwaseun^K^^^MD^NPI||||||20250601091500|||F
OBR|3|ORD20250601003^EPIC|LAB20250601003^LABCORP|84443^TSH^CPT4|||20250601091500|||||||||3890124567^Adeyemi^Oluwaseun^K^^^MD^NPI||||||20250601091500|||F
```

---

## 5. ORU^R01 - Lab results with embedded PDF report

```
MSH|^~\&|EPIC|NYU_LANGONE|LAB_SYS|NYU_LAB|20250610140000||ORU^R01^ORU_R01|MSG20250610140000005|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN10045223^^^NYU_LANGONE^MR||Hernandez^Marisol^T^^Mrs.||19790610|F||2106-3^White^CDCREC|310 E 23rd St^^New York^NY^10010^US^H||^PRN^PH^^^212^6618923|||M^Married^HL70002|||529-41-7803|||H^Hispanic^HL70189||||||N
PV1|1|I|4EAST^4E12^A^NYU_LANGONE^^^^4EAST||||1890234567^Okafor^Chibueze^N^^^MD^NPI||MED||||7|||1890234567^Okafor^Chibueze^N^^^MD^NPI|IN||SELF|||||||||||||||AI|||20250312143000|||||V
ORC|RE|ORD20250610001^EPIC|LAB20250610001^NYU_LAB||CM||||20250610140000|||1890234567^Okafor^Chibueze^N^^^MD^NPI|NYU_LANGONE
OBR|1|ORD20250610001^EPIC|LAB20250610001^NYU_LAB|80053^Comprehensive Metabolic Panel^CPT4|||20250610083000|||||||||1890234567^Okafor^Chibueze^N^^^MD^NPI||||||20250610140000|||F
OBX|1|NM|2345-7^Glucose^LN||98|mg/dL|74-106|N|||F|||20250610120000||AUTOVERIFY
OBX|2|NM|3094-0^BUN^LN||14|mg/dL|7-20|N|||F|||20250610120000||AUTOVERIFY
OBX|3|NM|2160-0^Creatinine^LN||0.9|mg/dL|0.7-1.3|N|||F|||20250610120000||AUTOVERIFY
OBX|4|NM|2951-2^Sodium^LN||140|mmol/L|136-145|N|||F|||20250610120000||AUTOVERIFY
OBX|5|NM|2823-3^Potassium^LN||4.2|mmol/L|3.5-5.1|N|||F|||20250610120000||AUTOVERIFY
OBX|6|NM|2075-0^Chloride^LN||102|mmol/L|98-106|N|||F|||20250610120000||AUTOVERIFY
OBX|7|NM|2028-9^CO2^LN||24|mmol/L|21-32|N|||F|||20250610120000||AUTOVERIFY
OBX|8|NM|17861-6^Calcium^LN||9.4|mg/dL|8.5-10.5|N|||F|||20250610120000||AUTOVERIFY
OBX|9|NM|2885-2^Total Protein^LN||7.1|g/dL|6.0-8.3|N|||F|||20250610120000||AUTOVERIFY
OBX|10|NM|1751-7^Albumin^LN||4.0|g/dL|3.5-5.5|N|||F|||20250610120000||AUTOVERIFY
OBX|11|NM|1975-2^Bilirubin Total^LN||0.8|mg/dL|0.1-1.2|N|||F|||20250610120000||AUTOVERIFY
OBX|12|NM|6768-6^Alkaline Phosphatase^LN||72|U/L|44-147|N|||F|||20250610120000||AUTOVERIFY
OBX|13|NM|1742-6^ALT^LN||28|U/L|7-56|N|||F|||20250610120000||AUTOVERIFY
OBX|14|NM|1920-8^AST^LN||22|U/L|10-40|N|||F|||20250610120000||AUTOVERIFY
OBX|15|ED|PDF_REPORT^Lab Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKENvbXByZWhlbnNpdmUgTWV0YWJvbGljIFBhbmVsIFJlcG9ydCkKL0F1dGhvciAoTllVIExhbmdvbmUgTGFib3JhdG9yeSkKL0NyZWF0b3IgKEVwaWMgTGFiIFN5c3RlbSkKL1Byb2R1Y2VyIChFcGljIFBERiBHZW5lcmF0b3IgdjMuMikKL0NyZWF0aW9uRGF0ZSAoRDoyMDI1MDYxMDE0MDAwMCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbNCAwIFJdCi9Db3VudCAxCj4+CmVuZG9iago=||||||F|||20250610140000||AUTOVERIFY
```

---

## 6. ADT^A08 - Patient update at Mount Sinai

```
MSH|^~\&|EPIC|MOUNT_SINAI|BILLING|MOUNT_SINAI_FIN|20250702101200||ADT^A08^ADT_A08|MSG20250702101200006|P|2.5.1|||AL|NE||ASCII|||
EVN|A08|20250702101200||UPD_TRIGGER|SYSTEM^System^Auto^^^SYS|20250702101200|MOUNT_SINAI
PID|1||MRN20045678^^^MOUNT_SINAI^MR||Flanagan^Seamus^J^^Mr.||19540318|M||2106-3^White^CDCREC|415 W 92nd St^^New York^NY^10025^US^H||^PRN^PH^^^212^7716743|^WPN^PH^^^212^7719876||M^Married^HL70002|||183-45-6712|||N^Non-Hispanic^HL70189||||||N
PD1|||MOUNT SINAI HOSPITAL^^10029|6234567890^Vega^Roberto^A^^^MD^NPI||||||||N
NK1|1|Flanagan^Maureen^P^^Mrs.|SPO^Spouse^HL70063||^PRN^PH^^^212^7716744||EC^Emergency Contact^HL70131
PV1|1|I|ICU3^ICU302^A^MOUNT_SINAI^^^^ICU3||||6234567890^Vega^Roberto^A^^^MD^NPI|4901234567^Chung^Ji-Yeon^H^^^MD^NPI|CARD||||7|||6234567890^Vega^Roberto^A^^^MD^NPI|IN||SELF|||||||||||||||AI|||20250630082000|||||V
PV2|||^Acute myocardial infarction management||||||||4|||||||||N|||||||||||A|20250702101200
IN1|1|UHC001^United Healthcare|87726|UnitedHealth Group|PO Box 30555^^Salt Lake City^UT^84130^US|||GRP654321|||20240101||||Flanagan^Seamus^J|SEL^Self^HL70063|19540318|415 W 92nd St^^New York^NY^10025^US|||||A|||||||M||||||UHC890123456
DG1|1||I21.09^Acute ST elevation MI of unspecified site^ICD10|||A
DG1|2||I25.10^Atherosclerotic heart disease^ICD10|||A
```

---

## 7. ADT^A02 - Patient transfer at NYP Weill Cornell

```
MSH|^~\&|EPIC|NYP_WEILL|ADT_NOTIFY|NYP_HIE|20250718093045||ADT^A02^ADT_A02|MSG20250718093045007|P|2.5.1|||AL|NE||ASCII|||
EVN|A02|20250718093045||TRAN_TRIGGER|BWRIGHT^Wright^Barbara^^^RN|20250718092800|NYP_WEILL
PID|1||MRN30178901^^^NYP^MR||Batista^Isabella^Carmen^^Ms.||20010919|F||2106-3^White^CDCREC|583 W 148th St^^New York^NY^10031^US^H||^PRN^PH^^^212^8811289|||S^Single^HL70002|||714-29-5503|||H^Hispanic^HL70189||||||N
PD1|||NYP WEILL CORNELL MEDICAL CENTER^^10065|8123456790^Kozlov^Anatoly^G^^^MD^NPI||||||||N
PV1|1|I|5SOUTH^5S08^A^NYP_WEILL^^^^5SOUTH||||8123456790^Kozlov^Anatoly^G^^^MD^NPI|1234509876^Chatterjee^Ananya^R^^^MD^NPI|ORT||||7|||8123456790^Kozlov^Anatoly^G^^^MD^NPI|IN||SELF|||||||||||||||AI|||20250716142000|||||V
PV2|||^Post-operative recovery femur fracture repair||||||||3|||||||||N|||||||||||A|20250718093000
DG1|1||S72.001A^Fracture of unspecified part of neck of right femur^ICD10|||A
```

---

## 8. SIU^S12 - Scheduling notification at Northwell

```
MSH|^~\&|EPIC|NORTHWELL_NS|SCHED_SYS|NORTHWELL_SCHED|20250801140000||SIU^S12^SIU_S12|MSG20250801140000008|P|2.5.1|||AL|NE||ASCII|||
SCH|APT20250801001^EPIC||||||FOLLOWUP^Follow-Up Visit^EPIC_APPT|||30|MIN|^^30^20250815100000^20250815103000|||||9234501678^Weiss^David^L^^^MD^NPI|^PRN^PH^^^516^3387890|300 Community Drive^^Manhasset^NY^11030^US||CONFIRMED
PID|1||MRN40023456^^^NORTHWELL^MR||Goldberg^Miriam^S^^Mrs.||19830427|F||2106-3^White^CDCREC|221 Beach 116th St^^Rockaway Park^NY^11694^US^H||^PRN^PH^^^718^6619012|||M^Married^HL70002|||502-83-1247|||N^Non-Hispanic^HL70189||||||N
PV1|1|O|CLINIC4^^^NORTHWELL_NS^^^^CLINIC4||||9234501678^Weiss^David^L^^^MD^NPI||ENDO||||1|||9234501678^Weiss^David^L^^^MD^NPI|OP||SELF|||||||||||||||AI|||20250801140000|||||V
RGS|1||ENDO_SLOT1^Endocrinology Slot
AIS|1||FOLLOWUP^Follow-Up Visit^EPIC_APPT|20250815100000|||30|MIN
AIP|1||9234501678^Weiss^David^L^^^MD^NPI|AD^Admitting^HL70286
AIL|1||CLINIC4^Room 4A^Northwell NS Endocrinology^^NORTHWELL_NS|W
```

---

## 9. ORU^R01 - Radiology report with embedded PDF

```
MSH|^~\&|EPIC|NYP_COLUMBIA|RIS|NYP_RADIOLOGY|20250822163000||ORU^R01^ORU_R01|MSG20250822163000009|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN30089012^^^NYP^MR||Brooks^Terrence^Lamar^^Mr.||19740503|M||2054-5^Black or African American^CDCREC|1540 Flatbush Ave^^Brooklyn^NY^11210^US^H||^PRN^PH^^^718^4423478|||M^Married^HL70002|||612-84-3390|||N^Non-Hispanic^HL70189||||||N
PV1|1|O|RADIOLOGY^^^NYP_COLUMBIA^^^^RAD||||2901234567^Ramachandran^Vikram^P^^^MD^NPI||RAD||||1|||2901234567^Ramachandran^Vikram^P^^^MD^NPI|OP||SELF|||||||||||||||AI|||20250822150000|||||V
ORC|RE|ORD20250822001^EPIC|RAD20250822001^NYP_RADIOLOGY||CM||||20250822163000|||2901234567^Ramachandran^Vikram^P^^^MD^NPI|NYP_COLUMBIA
OBR|1|ORD20250822001^EPIC|RAD20250822001^NYP_RADIOLOGY|71046^Chest X-Ray 2 Views^CPT4|||20250822150000|||||||||2901234567^Ramachandran^Vikram^P^^^MD^NPI||||||20250822163000|||F
OBX|1|TX|71046^Chest X-Ray^CPT4||FINDINGS: The heart is normal in size. The mediastinal contour is within normal limits. The lungs are clear bilaterally without evidence of consolidation, effusion, or pneumothorax. No acute osseous abnormality is identified.||||||F|||20250822160000||RAD_VERIFY
OBX|2|TX|71046^Chest X-Ray^CPT4||IMPRESSION: Normal chest radiograph. No acute cardiopulmonary disease.||||||F|||20250822160000||RAD_VERIFY
OBX|3|ED|RADIOLOGY_PDF^Radiology Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKENoZXN0IFgtUmF5IFJlcG9ydCkKL0F1dGhvciAoRHIuIFJhamVzaCBQLiBTaW5naCkKL0NyZWF0b3IgKEVwaWMgUmFkaW9sb2d5IFN5c3RlbSkKL1Byb2R1Y2VyIChFcGljIFBERiBHZW5lcmF0b3IgdjQuMSkKL0NyZWF0aW9uRGF0ZSAoRDoyMDI1MDgyMjE2MzAwMCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbNCAwIFJdCi9Db3VudCAxCj4+CmVuZG9iago0IDAgb2JqCjw8Ci9UeXBlIC9QYWdlCi9QYXJlbnQgMyAwIFIKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCg==||||||F|||20250822163000||RAD_VERIFY
```

---

## 10. MDM^T02 - Document notification from NYU Langone

```
MSH|^~\&|EPIC|NYU_LANGONE|DOC_REPO|NYU_DOCMGMT|20250905111500||MDM^T02^MDM_T02|MSG20250905111500010|P|2.5.1|||AL|NE||ASCII|||
EVN|T02|20250905111500
PID|1||MRN10067890^^^NYU_LANGONE^MR||Petrosyan^Viktor^A^^Mr.||19600122|M||2106-3^White^CDCREC|172 Henry St^^New York^NY^10002^US^H||^PRN^PH^^^212^3314321|||M^Married^HL70002|||845-12-7709|||N^Non-Hispanic^HL70189||||||N
PV1|1|O|CARDIOLOGY^^^NYU_LANGONE^^^^CARD||||5678901234^Rosenstein^Hannah^M^^^MD^NPI||CARD||||1|||5678901234^Rosenstein^Hannah^M^^^MD^NPI|OP||SELF|||||||||||||||AI|||20250905100000|||||V
TXA|1|HP^History and Physical^HL70270|TX^Text^HL70191||20250905111500|||||5678901234^Rosenstein^Hannah^M^^^MD^NPI||||DOC20250905001|||AU^Authenticated^HL70271||
OBX|1|TX|HP^History and Physical^LN||HISTORY OF PRESENT ILLNESS: Mr. Petrosyan is a 65-year-old male presenting for follow-up of atrial fibrillation. He reports intermittent palpitations, occurring 2-3 times weekly, lasting 5-10 minutes. No syncope or presyncope. Currently on apixaban 5mg BID and metoprolol succinate 50mg daily.~PHYSICAL EXAMINATION: BP 132/78, HR 72 irregular, RR 16, O2 Sat 98% on RA. Cardiac exam reveals irregularly irregular rhythm, no murmurs, rubs, or gallops. Lungs clear to auscultation bilaterally.~ASSESSMENT AND PLAN: 1. Persistent atrial fibrillation - continue current rate control and anticoagulation. Will obtain echocardiogram to reassess LV function. 2. Consider referral to EP for discussion of ablation. Follow up in 3 months.||||||F|||20250905111500
```

---

## 11. ORM^O01 - Radiology order at Mount Sinai

```
MSH|^~\&|EPIC|MOUNT_SINAI|RIS|MOUNT_SINAI_RAD|20250918083000||ORM^O01^ORM_O01|MSG20250918083000011|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN20112233^^^MOUNT_SINAI^MR||Tran^Binh^D^^Mr.||19890112|M||2028-9^Asian^CDCREC|78-20 Broadway^^Elmhurst^NY^11373^US^H||^PRN^PH^^^718^8827654|||M^Married^HL70002|||301-78-4520|||N^Non-Hispanic^HL70189||||||N
PV1|1|I|7WEST^7W14^A^MOUNT_SINAI^^^^7WEST||||3456012789^Eze^Chukwuma^N^^^MD^NPI||PULM||||7|||3456012789^Eze^Chukwuma^N^^^MD^NPI|IN||SELF|||||||||||||||AI|||20250916140000|||||V
ORC|NW|ORD20250918001^EPIC|RAD20250918001^MOUNT_SINAI_RAD||SC||||20250918083000|TNURSE^Nurse^Tanya^^^RN||3456012789^Eze^Chukwuma^N^^^MD^NPI|MOUNT_SINAI|||20250918083000||MOUNT_SINAI^Mount Sinai Hospital^L|1 Gustave L Levy Pl^^New York^NY^10029^US|^PRN^PH^^^212^2416000
OBR|1|ORD20250918001^EPIC|RAD20250918001^MOUNT_SINAI_RAD|71260^CT Chest with Contrast^CPT4|||20250918083000|||||||||3456012789^Eze^Chukwuma^N^^^MD^NPI|||||||20250918083000|||F||||||^Evaluate for pulmonary embolism
DG1|1||I26.99^Other pulmonary embolism without acute cor pulmonale^ICD10|||W
```

---

## 12. ADT^A01 - Admission at NYC Health + Hospitals Bellevue

```
MSH|^~\&|EPIC|BELLEVUE_HHC|ADT_REGISTRY|NYC_HHC_HIE|20251001192000||ADT^A01^ADT_A01|MSG20251001192000012|P|2.5.1|||AL|NE||ASCII|||
EVN|A01|20251001192000||ADM_TRIGGER|RJOHNSON^Johnson^Robert^^^REG|20251001191500|BELLEVUE_HHC
PID|1||MRN50034567^^^BELLEVUE^MR||Rosario^Luis^Enrique^^Mr.||19960303|M||2106-3^White^CDCREC|440 E 14th St Apt 6B^^New York^NY^10009^US^H||^PRN^PH^^^212^3378877|||S^Single^HL70002|||601-84-2390|||H^Hispanic^HL70189||||||N
PD1|||BELLEVUE HOSPITAL CENTER^^10016|4567890123^Abramowitz^Daniel^R^^^MD^NPI||||||||N
NK1|1|Rosario^Carmen^L^^Mrs.|MTH^Mother^HL70063||^PRN^PH^^^212^3378878||EC^Emergency Contact^HL70131
PV1|1|I|PSYCH2^P204^A^BELLEVUE^^^^PSYCH2||||4567890123^Abramowitz^Daniel^R^^^MD^NPI|7890123456^Xu^Jennifer^W^^^MD^NPI|PSY||||7|||4567890123^Abramowitz^Daniel^R^^^MD^NPI|IN||SELF|||||||||||||||AI|||20251001192000|||||V
PV2|||^Acute psychotic episode||||||||1|||||||||N|||||||||||A|20251001192000
IN1|1|MDCNY001^NY Medicaid|99123|NY Medicaid|PO Box 4220^^Albany^NY^12204^US|||||||20250101||||Rosario^Luis^Enrique|SEL^Self^HL70063|19960303|440 E 14th St Apt 6B^^New York^NY^10009^US|||||A|||||||M||||||MCD445566778
DG1|1||F29^Unspecified psychosis not due to a substance^ICD10|||A
GT1|1||Rosario^Luis^Enrique^^Mr.||440 E 14th St Apt 6B^^New York^NY^10009^US|^PRN^PH^^^212^3378877|||||SEL^Self^HL70063
```

---

## 13. ORU^R01 - Microbiology result from NYP

```
MSH|^~\&|EPIC|NYP_WEILL|MICRO_LAB|NYP_MICRO|20251015144500||ORU^R01^ORU_R01|MSG20251015144500013|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN30234567^^^NYP^MR||Jefferson^Aaliyah^Simone^^Ms.||19990302|F||2054-5^Black or African American^CDCREC|2780 Adam Clayton Powell Jr Blvd^^New York^NY^10039^US^H||^PRN^PH^^^212^9913698|||S^Single^HL70002|||734-01-5628|||N^Non-Hispanic^HL70189||||||N
PV1|1|I|3EAST^3E22^A^NYP_WEILL^^^^3EAST||||6789012345^Nguyen^Linh^T^^^MD^NPI||MED||||7|||6789012345^Nguyen^Linh^T^^^MD^NPI|IN||SELF|||||||||||||||AI|||20251012083000|||||V
ORC|RE|ORD20251015001^EPIC|MICRO20251015001^NYP_MICRO||CM||||20251015144500|||6789012345^Nguyen^Linh^T^^^MD^NPI|NYP_WEILL
OBR|1|ORD20251015001^EPIC|MICRO20251015001^NYP_MICRO|87070^Culture Bacterial^CPT4|||20251012100000|||||||||6789012345^Nguyen^Linh^T^^^MD^NPI||||||20251015144500|||F
OBX|1|TX|87070^Bacterial Culture^CPT4||Source: Blood||||||F|||20251015144500||MICRO_TECH
OBX|2|TX|87070^Bacterial Culture^CPT4||Organism: Staphylococcus aureus||||||F|||20251015144500||MICRO_TECH
OBX|3|TX|87070^Bacterial Culture^CPT4||Colony Count: Heavy growth||||||F|||20251015144500||MICRO_TECH
OBX|4|TX|87184^Antibiotic Susceptibility^CPT4||Oxacillin: Resistant (MIC >4)||||||A|||20251015144500||MICRO_TECH
OBX|5|TX|87184^Antibiotic Susceptibility^CPT4||Vancomycin: Susceptible (MIC 1)||||||F|||20251015144500||MICRO_TECH
OBX|6|TX|87184^Antibiotic Susceptibility^CPT4||Linezolid: Susceptible (MIC 2)||||||F|||20251015144500||MICRO_TECH
OBX|7|TX|87184^Antibiotic Susceptibility^CPT4||Daptomycin: Susceptible (MIC 0.5)||||||F|||20251015144500||MICRO_TECH
OBX|8|TX|87184^Antibiotic Susceptibility^CPT4||Trimethoprim-Sulfamethoxazole: Susceptible||||||F|||20251015144500||MICRO_TECH
OBX|9|TX|87070^Bacterial Culture^CPT4||INTERPRETATION: MRSA bacteremia. Recommend infectious disease consultation.||||||F|||20251015144500||MICRO_PATH
```

---

## 14. SIU^S12 - Surgery scheduling at Mount Sinai

```
MSH|^~\&|EPIC|MOUNT_SINAI|OR_SCHED|MOUNT_SINAI_SURG|20251102091500||SIU^S12^SIU_S12|MSG20251102091500014|P|2.5.1|||AL|NE||ASCII|||
SCH|APT20251102001^EPIC||||||SURGERY^Surgical Procedure^EPIC_APPT|||180|MIN|^^180^20251115073000^20251115103000|||||8901234567^Papadakis^Nikolaos^C^^^MD^NPI|^PRN^PH^^^212^4413210|1 Gustave L Levy Pl^^New York^NY^10029^US||CONFIRMED
PID|1||MRN20145678^^^MOUNT_SINAI^MR||Papanikolaou^Eleni^K^^Mrs.||19720815|F||2106-3^White^CDCREC|30-22 Ditmars Blvd^^Astoria^NY^11105^US^H||^PRN^PH^^^718^2214567|||M^Married^HL70002|||823-17-4509|||N^Non-Hispanic^HL70189||||||N
PV1|1|P|OR3^^^MOUNT_SINAI^^^^OR||||8901234567^Papadakis^Nikolaos^C^^^MD^NPI||SURG||||1|||8901234567^Papadakis^Nikolaos^C^^^MD^NPI|PRE||SELF|||||||||||||||AI|||20251102091500|||||V
RGS|1||SURG_SLOT1^General Surgery Slot
AIS|1||27447^Total Knee Arthroplasty^CPT4|20251115073000|||180|MIN
AIP|1||8901234567^Papadakis^Nikolaos^C^^^MD^NPI|PS^Primary Surgeon^HL70286
AIP|2||1234567890^Kaplan^Amy^B^^^MD^NPI|AS^Assistant Surgeon^HL70286
AIL|1||OR3^Operating Room 3^Mount Sinai Main OR^^MOUNT_SINAI|W
DG1|1||M17.11^Primary osteoarthritis right knee^ICD10|||A
```

---

## 15. ADT^A08 - Insurance update at Northwell

```
MSH|^~\&|EPIC|NORTHWELL_LIJ|FIN_SYS|NORTHWELL_BILLING|20251118152000||ADT^A08^ADT_A08|MSG20251118152000015|P|2.5.1|||AL|NE||ASCII|||
EVN|A08|20251118152000||INS_UPD|SYSTEM^System^Auto^^^SYS|20251118152000|NORTHWELL_LIJ
PID|1||MRN40056789^^^NORTHWELL^MR||Sayed^Fatima^Zahra^^Mrs.||19850716|F||2106-3^White^CDCREC|145-28 Northern Blvd^^Flushing^NY^11354^US^H||^PRN^PH^^^718^4399988|||M^Married^HL70002|||390-14-5678|||N^Non-Hispanic^HL70189||||||N
PD1|||NORTHWELL LIJ MEDICAL CENTER^^11040|2345678901^Mehta^Ravi^K^^^MD^NPI||||||||N
NK1|1|Sayed^Ahmed^M^^Mr.|SPO^Spouse^HL70063||^PRN^PH^^^718^4399989||EC^Emergency Contact^HL70131
PV1|1|I|MATERNITY^MAT12^A^NORTHWELL_LIJ^^^^MATERNITY||||2345678901^Mehta^Ravi^K^^^MD^NPI||OB||||7|||2345678901^Mehta^Ravi^K^^^MD^NPI|IN||SELF|||||||||||||||AI|||20251116080000|||||V
PV2|||^Normal spontaneous vaginal delivery||||||||3|||||||||N|||||||||||A|20251118152000
IN1|1|OSCAR001^Oscar Health|16644|Oscar Health|75 Varick St^^New York^NY^10013^US|||GRP111222|||20240801||||Sayed^Fatima^Zahra|SEL^Self^HL70063|19850716|145-28 Northern Blvd^^Flushing^NY^11354^US|||||A|||||||F||||||OSC901234567
IN1|2|MDCNY001^NY Medicaid|99123|NY Medicaid|PO Box 4220^^Albany^NY^12204^US|||||||20250101||||Sayed^Fatima^Zahra|SEL^Self^HL70063|19850716|145-28 Northern Blvd^^Flushing^NY^11354^US|||||A|||||||F||||||MCD223344556
DG1|1||O80^Encounter for full-term uncomplicated delivery^ICD10|||A
```

---

## 16. ORU^R01 - Cardiac catheterization results

```
MSH|^~\&|EPIC|NYU_LANGONE|CATH_LAB|NYU_CARDIOLOGY|20251201161500||ORU^R01^ORU_R01|MSG20251201161500016|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN10089012^^^NYU_LANGONE^MR||Vitale^Giuseppe^R^^Mr.||19570211|M||2106-3^White^CDCREC|2305 Neptune Ave^^Brooklyn^NY^11224^US^H||^PRN^PH^^^718^9921234|||M^Married^HL70002|||167-45-2389|||N^Non-Hispanic^HL70189||||||N
PV1|1|I|CATH_LAB^CL02^A^NYU_LANGONE^^^^CATH||||1234567890^Bernstein^Howard^M^^^MD^NPI||CARD||||7|||1234567890^Bernstein^Howard^M^^^MD^NPI|IN||SELF|||||||||||||||AI|||20251201080000|||||V
ORC|RE|ORD20251201001^EPIC|CATH20251201001^NYU_CARDIOLOGY||CM||||20251201161500|||1234567890^Bernstein^Howard^M^^^MD^NPI|NYU_LANGONE
OBR|1|ORD20251201001^EPIC|CATH20251201001^NYU_CARDIOLOGY|93458^Left Heart Catheterization^CPT4|||20251201100000|||||||||1234567890^Bernstein^Howard^M^^^MD^NPI||||||20251201161500|||F
OBX|1|TX|93458^Cardiac Catheterization^CPT4||LEFT VENTRICULOGRAPHY: LV ejection fraction estimated at 45%. Mild inferior wall hypokinesis.||||||F|||20251201150000||CARDIO_VERIFY
OBX|2|TX|93458^Cardiac Catheterization^CPT4||CORONARY ANGIOGRAPHY: LAD - 70% stenosis in mid-segment. LCx - No significant disease. RCA - 50% stenosis in proximal segment.||||||F|||20251201150000||CARDIO_VERIFY
OBX|3|TX|93458^Cardiac Catheterization^CPT4||HEMODYNAMICS: LVEDP 18 mmHg. Aortic pressure 130/75 mmHg. No significant gradient across aortic valve.||||||F|||20251201150000||CARDIO_VERIFY
OBX|4|TX|93458^Cardiac Catheterization^CPT4||IMPRESSION: Significant LAD disease with mildly reduced LV function. Recommend PCI to LAD vs medical management. Heart team discussion recommended.||||||F|||20251201150000||CARDIO_VERIFY
DG1|1||I25.110^Atherosclerotic heart disease of native coronary artery with unstable angina^ICD10|||A
```

---

## 17. ADT^A04 - Registration at Montefiore

```
MSH|^~\&|EPIC|MONTEFIORE|ED_TRACK|MONTE_ED|20251215204500||ADT^A04^ADT_A04|MSG20251215204500017|P|2.5.1|||AL|NE||ASCII|||
EVN|A04|20251215204500||REG_TRIGGER|ASMITH^Smith^Angela^^^REG|20251215204200|MONTEFIORE
PID|1||MRN60012345^^^MONTEFIORE^MR||Mitchell^Jamal^Kareem^^Mr.||20050813|M||2054-5^Black or African American^CDCREC|3490 White Plains Rd^^Bronx^NY^10467^US^H||^PRN^PH^^^718^2316543|||S^Single^HL70002|||903-27-1456|||N^Non-Hispanic^HL70189||||||N
PD1|||MONTEFIORE MEDICAL CENTER^^10467|5678901234^Santiago^Carmen^M^^^MD^NPI||||||||N
NK1|1|Mitchell^Denise^L^^Mrs.|MTH^Mother^HL70063||^PRN^PH^^^718^2316544||EC^Emergency Contact^HL70131
PV1|1|E|ED^^^MONTEFIORE^^^^ED||||5678901234^Santiago^Carmen^M^^^MD^NPI||EM||||1|||5678901234^Santiago^Carmen^M^^^MD^NPI|EM||SELF|||||||||||||||AI|||20251215204500|||||V
PV2|||^Asthma exacerbation||||||||2|||||||||N
IN1|1|MDCNY001^NY Medicaid|99123|NY Medicaid|PO Box 4220^^Albany^NY^12204^US|||||||20250101||||Mitchell^Denise^L^|GRD^Guardian^HL70063|19810420|3490 White Plains Rd^^Bronx^NY^10467^US|||||A|||||||M||||||MCD667788990
DG1|1||J45.41^Moderate persistent asthma with acute exacerbation^ICD10|||A
GT1|1||Mitchell^Denise^L^^Mrs.||3490 White Plains Rd^^Bronx^NY^10467^US|^PRN^PH^^^718^2316544|||||GRD^Guardian^HL70063
```

---

## 18. ORM^O01 - Medication order at NYP

```
MSH|^~\&|EPIC|NYP_COLUMBIA|PHARMACY|NYP_PHARM|20260105093000||ORM^O01^ORM_O01|MSG20260105093000018|P|2.5.1|||AL|NE||ASCII|||
PID|1||MRN30256789^^^NYP^MR||Hwang^Jae-Won^^^Mr.||19441017|M||2028-9^Asian^CDCREC|61-30 98th St^^Rego Park^NY^11374^US^H||^PRN^PH^^^718^5507890|||W^Widowed^HL70002|||512-90-3478|||N^Non-Hispanic^HL70189||||||N
PV1|1|I|8SOUTH^8S03^A^NYP_COLUMBIA^^^^8SOUTH||||7890123456^Okonkwo^Simone^A^^^MD^NPI||MED||||7|||7890123456^Okonkwo^Simone^A^^^MD^NPI|IN||SELF|||||||||||||||AI|||20260103120000|||||V
ORC|NW|ORD20260105001^EPIC|PHARM20260105001^NYP_PHARM||SC||||20260105093000|MNURSE^Nurse^Maria^^^RN||7890123456^Okonkwo^Simone^A^^^MD^NPI|NYP_COLUMBIA|||20260105093000
OBR|1|ORD20260105001^EPIC|PHARM20260105001^NYP_PHARM|RX001^Medication Order^L|||20260105093000|||||||||7890123456^Okonkwo^Simone^A^^^MD^NPI
RXO|311989^Vancomycin 1000mg IV^RXNORM||1000|mg||IV|Q12H^^^Q12H||G||1000|mg
RXR|IV^Intravenous^HL70162|LA^Left Arm^HL70163
RXE|Q12H&Every 12 Hours&L^^^202601051000^^R|311989^Vancomycin 1000mg^RXNORM|1000|mg||IV|||||||||7890123456^Okonkwo^Simone^A^^^MD^NPI|||||1000|mg
DG1|1||A41.01^Sepsis due to Methicillin susceptible Staphylococcus aureus^ICD10|||A
```

---

## 19. MDM^T02 - Operative report at Mount Sinai

```
MSH|^~\&|EPIC|MOUNT_SINAI|DOC_SYS|MOUNT_SINAI_DOCS|20260120153000||MDM^T02^MDM_T02|MSG20260120153000019|P|2.5.1|||AL|NE||ASCII|||
EVN|T02|20260120153000
PID|1||MRN20178901^^^MOUNT_SINAI^MR||Callahan^Brendan^Patrick^^Mr.||19670524|M||2106-3^White^CDCREC|502 Bay Ridge Ave^^Brooklyn^NY^11220^US^H||^PRN^PH^^^718^8368901|||M^Married^HL70002|||623-14-7890|||N^Non-Hispanic^HL70189||||||N
PV1|1|I|OR5^^^MOUNT_SINAI^^^^OR||||8901234567^Papadakis^Nikolaos^C^^^MD^NPI||SURG||||7|||8901234567^Papadakis^Nikolaos^C^^^MD^NPI|IN||SELF|||||||||||||||AI|||20260118060000|||||V
TXA|1|OP^Operative Note^HL70270|TX^Text^HL70191||20260120153000|||||8901234567^Papadakis^Nikolaos^C^^^MD^NPI||||DOC20260120001|||AU^Authenticated^HL70271||
OBX|1|TX|OP^Operative Note^LN||PROCEDURE: Right total knee arthroplasty~SURGEON: Nikolaos C. Papadakis, MD~ASSISTANT: Amy B. Kaplan, MD~ANESTHESIA: General endotracheal~FINDINGS: Severe tricompartmental osteoarthritis with complete loss of medial joint space, Grade IV chondral damage medial femoral condyle and tibial plateau.~PROCEDURE DETAILS: Standard medial parapatellar approach. Distal femoral cut with 5 degrees of valgus. Tibial cut with 3 degrees of posterior slope. Trial components demonstrated excellent alignment and stability through full range of motion. Final components cemented in place. Patella resurfaced. Wound closed in layers. Estimated blood loss 250mL.~DISPOSITION: Patient to PACU in stable condition.||||||F|||20260120153000
```

---

## 20. ADT^A01 - Admission at NYP with newborn

```
MSH|^~\&|EPIC|NYP_WEILL|NURSERY|NYP_NICU|20260205081500||ADT^A01^ADT_A01|MSG20260205081500020|P|2.5.1|||AL|NE||ASCII|||
EVN|A01|20260205081500||ADM_TRIGGER|LCHEN^Chen^Lisa^^^RN|20260205081000|NYP_WEILL
PID|1||MRN30345678^^^NYP^MR~941-72-5508^^^SSA^SS||Williams^Kiara^Nicole^^Ms.||19930804|F||2054-5^Black or African American^CDCREC|510 W 135th St Apt 4C^^New York^NY^10031^US^H||^PRN^PH^^^212^8811456|||S^Single^HL70002|||941-72-5508|||N^Non-Hispanic^HL70189||||||N
PD1|||NYP WEILL CORNELL MEDICAL CENTER^^10065|3456789012^Wong^Michelle^L^^^MD^NPI||||||||N
NK1|1|Williams^Denise^M^^Mrs.|MTH^Mother^HL70063||^PRN^PH^^^212^8811457||EC^Emergency Contact^HL70131
NK1|2|Harris^Marcus^D^^Mr.|FOB^Father of Baby^HL70063||^PRN^PH^^^212^8811458||EC^Emergency Contact^HL70131
PV1|1|I|L_AND_D^LD05^A^NYP_WEILL^^^^L_AND_D||||3456789012^Wong^Michelle^L^^^MD^NPI|6789012345^Adams^Rachel^S^^^MD^NPI|OB||||7|||3456789012^Wong^Michelle^L^^^MD^NPI|IN||SELF|||||||||||||||AI|||20260205081500|||||V
PV2|||^Active labor term pregnancy||||||||1|||||||||N|||||||||||A|20260205081500
IN1|1|EMPIRE001^EmpireBlue|87726|Empire BlueCross BlueShield|PO Box 1407^^New York^NY^10116^US|||GRP445566|||20250101||||Williams^Kiara^Nicole|SEL^Self^HL70063|19930804|510 W 135th St Apt 4C^^New York^NY^10031^US|||||A|||||||F||||||EMP890123456
DG1|1||O80^Encounter for full-term uncomplicated delivery^ICD10|||A
DG1|2||Z3A.39^39 weeks gestation of pregnancy^ICD10|||A
GT1|1||Williams^Kiara^Nicole^^Ms.||510 W 135th St Apt 4C^^New York^NY^10031^US|^PRN^PH^^^212^8811456|||||SEL^Self^HL70063
```
