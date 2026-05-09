# Epic Systems - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission to IU Health Methodist Hospital

```
MSH|^~\&|EPIC|IUH_METH|ADT_RECV|IHIE|20250312084523||ADT^A01^ADT_A01|MSG00001234|P|2.5.1|||AL|NE
EVN|A01|20250312084500|||TGRAHAM^Graham^Tyler^W^^^MD
PID|1||MRN48291053^^^IUH^MR||Hendricks^Marcus^Lamont||19670423|M|||1847 Capitol Ave^^Indianapolis^IN^46202^US||^PRN^PH^^1^317^5551234|^WPN^PH^^1^317^5559876|ENG|M|CHR|SSN412-63-8907^^^SS|||||||||||N
PD1|||IU HEALTH METHODIST^^48291|TGRAHAM^Graham^Tyler^W^^^MD
NK1|1|Hendricks^Denise^R|SPO|2930 College Ave^^Indianapolis^IN^46220^US|^PRN^PH^^1^317^5554321
PV1|1|I|4WEST^412^A^IUH_METH^^^^4WEST||||TGRAHAM^Graham^Tyler^W^^^MD|NMURPHY^Murphy^Nicole^E^^^MD||MED|||7|||TGRAHAM^Graham^Tyler^W^^^MD|IP||||||||||||||||||IUH_METH|||||20250312084500
PV2|||^Chest pain, unspecified
IN1|1|BC8374^Blue Cross Blue Shield|BCBS001|Blue Cross Blue Shield of Indiana||||||||20240101|20251231|||PPO|Hendricks^Marcus^Lamont|Self|19670423|1847 Capitol Ave^^Indianapolis^IN^46202^US
DG1|1||R07.9^Chest pain, unspecified^ICD10|||A
```

---

## 2. ORU^R01 - Complete blood count results from IU Health

```
MSH|^~\&|EPIC|IUH_LAB|LAB_RECV|IUH|20250314101530||ORU^R01^ORU_R01|MSG00005678|P|2.5.1|||AL|NE
PID|1||MRN48291053^^^IUH^MR||Hendricks^Marcus^Lamont||19670423|M|||1847 Capitol Ave^^Indianapolis^IN^46202^US||^PRN^PH^^1^317^5551234
PV1|1|I|4WEST^412^A^IUH_METH||||TGRAHAM^Graham^Tyler^W^^^MD
ORC|RE|ORD789012|RES789012||CM||||20250314090000|||TGRAHAM^Graham^Tyler^W^^^MD
OBR|1|ORD789012|RES789012|57021-8^CBC with Differential^LN|||20250314083000||||||||TGRAHAM^Graham^Tyler^W^^^MD||||||20250314101500|||F
OBX|1|NM|6690-2^WBC^LN||7.2|10*3/uL|4.5-11.0|N|||F|||20250314101500
OBX|2|NM|789-8^RBC^LN||4.85|10*6/uL|4.50-5.90|N|||F|||20250314101500
OBX|3|NM|718-7^Hemoglobin^LN||14.2|g/dL|13.5-17.5|N|||F|||20250314101500
OBX|4|NM|4544-3^Hematocrit^LN||42.1|%|38.3-48.6|N|||F|||20250314101500
OBX|5|NM|787-2^MCV^LN||86.8|fL|80.0-100.0|N|||F|||20250314101500
OBX|6|NM|777-3^Platelet Count^LN||234|10*3/uL|150-400|N|||F|||20250314101500
OBX|7|NM|770-8^Neutrophils %^LN||62.3|%|40.0-70.0|N|||F|||20250314101500
OBX|8|NM|736-9^Lymphocytes %^LN||28.4|%|20.0-40.0|N|||F|||20250314101500
```

---

## 3. ORM^O01 - CT chest order from Community Health Network

```
MSH|^~\&|EPIC|CHN_EAST|RAD_SYS|CHN|20250315142200||ORM^O01^ORM_O01|MSG00008901|P|2.4|||AL|NE
PID|1||MRN63718290^^^CHN^MR||Lawson^Brianna^Cherie||19820915|F|||452 Virginia Ave^^Indianapolis^IN^46203^US||^PRN^PH^^1^317^5552345||ENG|S|CAT|SSN271-48-9305^^^SS
PV1|1|O|RAD^101^^CHN_EAST||||RDESAI^Desai^Rajesh^N^^^MD|||RAD|||1|||RDESAI^Desai^Rajesh^N^^^MD|OP
ORC|NW|ORD901234||GRP901234|SC||||20250315142000|||RDESAI^Desai^Rajesh^N^^^MD|RAD^101^^CHN_EAST
OBR|1|ORD901234||71260^CT Chest with Contrast^CPT|||20250316080000||||||||RDESAI^Desai^Rajesh^N^^^MD||||||||||1^^^20250316080000^^R
DG1|1||R91.8^Other nonspecific abnormal finding of lung field^ICD10|||A
```

---

## 4. SIU^S12 - Appointment scheduled at IU Health Arnett

```
MSH|^~\&|EPIC|IUH_ARNETT|SCHED_SYS|IUH|20250318093045||SIU^S12^SIU_S12|MSG00012345|P|2.5|||AL|NE
SCH|APT567890|APT567890|||OFFICE^Office Visit|ROUTINE^Routine||30|MIN|^^30^20250325140000^20250325143000|||||AFORD^Ford^Allison^C^^^MD|^WPN^PH^^1^765^5551111|CARDIO^205^^IUH_ARNETT|||||BOOKED
PID|1||MRN75604823^^^IUH^MR||Delgado^Ernesto^Javier||19550712|M|||309 Main St^^Lafayette^IN^47901^US||^PRN^PH^^1^765^5553456||SPA|M|CAT|SSN384-71-2069^^^SS
PV1|1|O|CARDIO^205^^IUH_ARNETT||||AFORD^Ford^Allison^C^^^MD|||CAR|||1|||AFORD^Ford^Allison^C^^^MD|OP
RGS|1||CARDIO^205^^IUH_ARNETT
AIS|1||CARDIO_CONSULT^Cardiology Consultation|20250325140000|||30|MIN
AIP|1||AFORD^Ford^Allison^C^^^MD|ATTENDING
```

---

## 5. MDM^T02 - Discharge summary document at IU Health University Hospital

```
MSH|^~\&|EPIC|IUH_UNIV|DOC_RECV|IHIE|20250320163000||MDM^T02^MDM_T02|MSG00015678|P|2.5|||AL|NE
EVN|T02|20250320163000
PID|1||MRN83946172^^^IUH^MR||Weaver^Donald^Ray||19480301|M|||714 University Blvd^^Indianapolis^IN^46202^US||^PRN^PH^^1^317^5556789||ENG|W|PRO|SSN503-87-6241^^^SS
PV1|1|I|5EAST^503^A^IUH_UNIV||||CBENNETT^Bennett^Carla^S^^^MD|||MED|||7|||CBENNETT^Bennett^Carla^S^^^MD|IP||||||||||||||||||IUH_UNIV|||||20250315090000|||20250320150000
TXA|1|DS^Discharge Summary|TX|20250320150000|CBENNETT^Bennett^Carla^S^^^MD||20250320163000||CBENNETT^Bennett^Carla^S^^^MD|||||DOC12345||AU|||
OBX|1|TX|18842-5^Discharge Summary^LN||Patient discharged in stable condition after treatment for community-acquired pneumonia. Follow-up in 7 days with PCP.||||||F
```

---

## 6. VXU^V04 - Immunization update for pediatric patient at Community Health

```
MSH|^~\&|EPIC|CHN_NORTH|CHIRP|ISDH|20250322111500||VXU^V04^VXU_V04|MSG00019012|P|2.5.1|||AL|NE
PID|1||MRN29481637^^^CHN^MR||Herrera^Valentina^Camila||20220815|F|||518 Keystone Ave^^Indianapolis^IN^46205^US||^PRN^PH^^1^317^5557890||ENG||CHR|SSN618-25-7340^^^SS
PD1|||COMMUNITY HEALTH NORTH^^29481|JPARK^Park^Janet^M^^^MD
NK1|1|Herrera^Luisa^Carmen|MTH|518 Keystone Ave^^Indianapolis^IN^46205^US|^PRN^PH^^1^317^5557890
ORC|RE|IMM345678||||||||||JPARK^Park^Janet^M^^^MD
RXA|0|1|20250322111000|20250322111000|03^MMR^CVX|0.5|mL|IM|LA^^Left Arm||||||Y5432A||MSD^Merck Sharp and Dohme|||||A
RXR|IM^Intramuscular^HL70162|LA^Left Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||VXC1^Medicaid^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||03^MMR^CVX||||||F
OBX|3|TS|29768-9^Date Vaccine Information Statement Published^LN||20200812||||||F
```

---

## 7. ADT^A03 - Patient discharge from Eskenazi Health

```
MSH|^~\&|EPIC|ESKENAZI|ADT_RECV|IHIE|20250323154500||ADT^A03^ADT_A03|MSG00022345|P|2.5.1|||AL|NE
EVN|A03|20250323154500|||MKHAN^Khan^Mohan^V^^^MD
PID|1||MRN50183274^^^ESK^MR||Pratt^Sandra^Louise||19750619|F|||831 West St^^Indianapolis^IN^46222^US||^PRN^PH^^1^317^5550123||ENG|D|BAP|SSN729-04-5183^^^SS
PV1|1|I|3NORTH^305^B^ESKENAZI||||MKHAN^Khan^Mohan^V^^^MD|LHALL^Hall^Laura^P^^^MD||MED|||7|||MKHAN^Khan^Mohan^V^^^MD|IP||||||||||||||||||ESKENAZI|||||20250319120000|||20250323154500
PV2|||^Type 2 diabetes mellitus with hyperglycemia
DG1|1||E11.65^Type 2 diabetes mellitus with hyperglycemia^ICD10|||A
DG1|2||I10^Essential (primary) hypertension^ICD10|||A
```

---

## 8. ORU^R01 - Radiology report with embedded PDF from IU Health

```
MSH|^~\&|EPIC|IUH_METH|RAD_RECV|IUH|20250324091200||ORU^R01^ORU_R01|MSG00025678|P|2.5.1|||AL|NE
PID|1||MRN48291053^^^IUH^MR||Hendricks^Marcus^Lamont||19670423|M|||1847 Capitol Ave^^Indianapolis^IN^46202^US||^PRN^PH^^1^317^5551234
PV1|1|I|4WEST^412^A^IUH_METH||||TGRAHAM^Graham^Tyler^W^^^MD
ORC|RE|ORD901234|RES901234||CM||||20250324090000|||TGRAHAM^Graham^Tyler^W^^^MD
OBR|1|ORD901234|RES901234|71260^CT Chest with Contrast^CPT|||20250316080000||||||||RDESAI^Desai^Rajesh^N^^^MD||||||20250324090000|||F
OBX|1|TX|71260^CT Chest with Contrast^CPT||IMPRESSION: 1. No acute cardiopulmonary process. 2. Stable 4mm right lower lobe pulmonary nodule, recommend follow-up CT in 12 months.||||||F
OBX|2|ED|PDF^Radiology Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 9. ADT^A08 - Patient information update at Community Health Network

```
MSH|^~\&|EPIC|CHN_SOUTH|ADT_RECV|IHIE|20250325103000||ADT^A08^ADT_A08|MSG00028901|P|2.5|||AL|NE
EVN|A08|20250325103000|||REG_CLERK
PID|1||MRN41829507^^^CHN^MR||Stokes^Darnell^Wayne||19900214|M|||720 Emerson Ave^^Indianapolis^IN^46219^US||^PRN^PH^^1^317^5554567|^WPN^PH^^1^317^5559999|ENG|S|NON|SSN847-30-1625^^^SS
PD1|||COMMUNITY HEALTH SOUTH^^41829|EWATERS^Waters^Emily^J^^^MD
PV1|1|O|PCP^201^^CHN_SOUTH||||EWATERS^Waters^Emily^J^^^MD|||PCP|||1|||EWATERS^Waters^Emily^J^^^MD|OP
NK1|1|Stokes^Wanda^Faye|MTH|1405 Rural St^^Indianapolis^IN^46219^US|^PRN^PH^^1^317^5551999
IN1|1|UHC567^United Healthcare|UHC001|United Healthcare||||||||20250101|20251231|||HMO|Stokes^Darnell^Wayne|Self|19900214|720 Emerson Ave^^Indianapolis^IN^46219^US
```

---

## 10. ORU^R01 - Pathology report with embedded PDF from Community Health

```
MSH|^~\&|EPIC|CHN_EAST|PATH_RECV|CHN|20250326142200||ORU^R01^ORU_R01|MSG00031234|P|2.5.1|||AL|NE
PID|1||MRN63718290^^^CHN^MR||Lawson^Brianna^Cherie||19820915|F|||452 Virginia Ave^^Indianapolis^IN^46203^US||^PRN^PH^^1^317^5552345
PV1|1|O|PATH^101^^CHN_EAST||||RDESAI^Desai^Rajesh^N^^^MD
ORC|RE|ORD112233|RES112233||CM||||20250326140000|||SHOWARD^Howard^Steven^B^^^MD
OBR|1|ORD112233|RES112233|88305^Surgical Pathology^CPT|||20250324100000||||||||SHOWARD^Howard^Steven^B^^^MD||||||20250326140000|||F
OBX|1|TX|88305^Surgical Pathology^CPT||DIAGNOSIS: Left breast, core needle biopsy: Fibroadenoma. No evidence of malignancy.||||||F
OBX|2|TX|88305^Surgical Pathology^CPT||MICROSCOPIC: Sections show a well-circumscribed fibroepithelial lesion with intracanalicular and pericanalicular growth patterns.||||||F
OBX|3|ED|PDF^Pathology Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```

---

## 11. ORM^O01 - MRI Brain order from IU Health

```
MSH|^~\&|EPIC|IUH_UNIV|RAD_SYS|IUH|20250327083000||ORM^O01^ORM_O01|MSG00034567|P|2.4|||AL|NE
PID|1||MRN37205814^^^IUH^MR||Caldwell^Jerome^Franklin||19600928|M|||1582 Fall Creek Pkwy^^Indianapolis^IN^46205^US||^PRN^PH^^1^317^5558901||ENG|M|LUT|SSN906-51-3478^^^SS
PV1|1|O|NEURO^301^^IUH_UNIV||||DYAMADA^Yamada^Diane^R^^^MD|||NEU|||1|||DYAMADA^Yamada^Diane^R^^^MD|OP
ORC|NW|ORD445566||GRP445566|SC||||20250327082500|||DYAMADA^Yamada^Diane^R^^^MD|NEURO^301^^IUH_UNIV
OBR|1|ORD445566||70553^MRI Brain with and without Contrast^CPT|||20250328100000||||||||DYAMADA^Yamada^Diane^R^^^MD||||||||||1^^^20250328100000^^R
DG1|1||G43.909^Migraine, unspecified, not intractable^ICD10|||A
```

---

## 12. ADT^A04 - Patient registration at IU Health North

```
MSH|^~\&|EPIC|IUH_NORTH|ADT_RECV|IHIE|20250328074500||ADT^A04^ADT_A04|MSG00037890|P|2.5.1|||AL|NE
EVN|A04|20250328074500|||REG_CLERK
PID|1||MRN60438271^^^IUH^MR||Shepherd^Kendra^Renee||19880503|F|||3281 Michigan Rd^^Indianapolis^IN^46268^US||^PRN^PH^^1^317^5550456|^WPN^PH^^1^317^5550789|ENG|M|MET|SSN058-42-7139^^^SS
PD1|||IU HEALTH NORTH^^60438|BCOLEMAN^Coleman^Brian^D^^^MD
NK1|1|Shepherd^Travis^Allen|SPO|3281 Michigan Rd^^Indianapolis^IN^46268^US|^PRN^PH^^1^317^5550456
PV1|1|O|OBGYN^105^^IUH_NORTH||||BCOLEMAN^Coleman^Brian^D^^^MD|||OBG|||1|||BCOLEMAN^Coleman^Brian^D^^^MD|OP
IN1|1|AETNA23^Aetna|AETNA001|Aetna Health Plans||||||||20250101|20251231|||PPO|Shepherd^Kendra^Renee|Self|19880503|3281 Michigan Rd^^Indianapolis^IN^46268^US
```

---

## 13. ORU^R01 - Comprehensive metabolic panel from IU Health

```
MSH|^~\&|EPIC|IUH_LAB|LAB_RECV|IUH|20250329155000||ORU^R01^ORU_R01|MSG00041234|P|2.5.1|||AL|NE
PID|1||MRN37205814^^^IUH^MR||Caldwell^Jerome^Franklin||19600928|M|||1582 Fall Creek Pkwy^^Indianapolis^IN^46205^US||^PRN^PH^^1^317^5558901
PV1|1|O|NEURO^301^^IUH_UNIV||||DYAMADA^Yamada^Diane^R^^^MD
ORC|RE|ORD556677|RES556677||CM||||20250329150000|||DYAMADA^Yamada^Diane^R^^^MD
OBR|1|ORD556677|RES556677|24323-8^Comprehensive Metabolic Panel^LN|||20250329140000||||||||DYAMADA^Yamada^Diane^R^^^MD||||||20250329155000|||F
OBX|1|NM|2345-7^Glucose^LN||98|mg/dL|70-99|N|||F|||20250329155000
OBX|2|NM|3094-0^BUN^LN||18|mg/dL|7-20|N|||F|||20250329155000
OBX|3|NM|2160-0^Creatinine^LN||1.1|mg/dL|0.7-1.3|N|||F|||20250329155000
OBX|4|NM|2951-2^Sodium^LN||140|mmol/L|136-145|N|||F|||20250329155000
OBX|5|NM|2823-3^Potassium^LN||4.2|mmol/L|3.5-5.1|N|||F|||20250329155000
OBX|6|NM|2075-0^Chloride^LN||102|mmol/L|98-106|N|||F|||20250329155000
OBX|7|NM|2028-9^CO2^LN||25|mmol/L|21-32|N|||F|||20250329155000
OBX|8|NM|17861-6^Calcium^LN||9.4|mg/dL|8.5-10.5|N|||F|||20250329155000
OBX|9|NM|2885-2^Total Protein^LN||7.1|g/dL|6.0-8.3|N|||F|||20250329155000
OBX|10|NM|1751-7^Albumin^LN||4.2|g/dL|3.5-5.5|N|||F|||20250329155000
OBX|11|NM|1975-2^Total Bilirubin^LN||0.8|mg/dL|0.1-1.2|N|||F|||20250329155000
OBX|12|NM|6768-6^Alkaline Phosphatase^LN||72|U/L|44-147|N|||F|||20250329155000
OBX|13|NM|1742-6^ALT^LN||25|U/L|7-56|N|||F|||20250329155000
OBX|14|NM|1920-8^AST^LN||22|U/L|10-40|N|||F|||20250329155000
```

---

## 14. SIU^S14 - Appointment modification at Community Health

```
MSH|^~\&|EPIC|CHN_EAST|SCHED_SYS|CHN|20250330091500||SIU^S14^SIU_S12|MSG00044567|P|2.5|||AL|NE
SCH|APT678901|APT678901|||FOLLOWUP^Follow-up Visit|ROUTINE^Routine||15|MIN|^^15^20250404093000^20250404094500|||||RDESAI^Desai^Rajesh^N^^^MD|^WPN^PH^^1^317^5553333|PULM^110^^CHN_EAST|||||BOOKED
PID|1||MRN63718290^^^CHN^MR||Lawson^Brianna^Cherie||19820915|F|||452 Virginia Ave^^Indianapolis^IN^46203^US||^PRN^PH^^1^317^5552345
PV1|1|O|PULM^110^^CHN_EAST||||RDESAI^Desai^Rajesh^N^^^MD|||PUL|||1|||RDESAI^Desai^Rajesh^N^^^MD|OP
RGS|1||PULM^110^^CHN_EAST
AIS|1||PULM_FOLLOWUP^Pulmonology Follow-up|20250404093000|||15|MIN
AIP|1||RDESAI^Desai^Rajesh^N^^^MD|ATTENDING
```

---

## 15. ADT^A02 - Patient transfer within IU Health Methodist

```
MSH|^~\&|EPIC|IUH_METH|ADT_RECV|IHIE|20250331110000||ADT^A02^ADT_A02|MSG00047890|P|2.5.1|||AL|NE
EVN|A02|20250331110000|||CHARGE_RN
PID|1||MRN48291053^^^IUH^MR||Hendricks^Marcus^Lamont||19670423|M|||1847 Capitol Ave^^Indianapolis^IN^46202^US||^PRN^PH^^1^317^5551234
PV1|1|I|ICU^201^A^IUH_METH^^^^ICU||||TGRAHAM^Graham^Tyler^W^^^MD|NMURPHY^Murphy^Nicole^E^^^MD||MED|||7|||TGRAHAM^Graham^Tyler^W^^^MD|IP||||||||||||||||||IUH_METH|||||20250312084500
PV2|||^Acute respiratory failure
```

---

## 16. MDM^T02 - Operative note at Community Health Network

```
MSH|^~\&|EPIC|CHN_EAST|DOC_RECV|IHIE|20250401143000||MDM^T02^MDM_T02|MSG00051234|P|2.5|||AL|NE
EVN|T02|20250401143000
PID|1||MRN82057413^^^CHN^MR||Pittman^Terrance^Odell||19710808|M|||1463 Shelby St^^Indianapolis^IN^46203^US||^PRN^PH^^1^317^5556543||ENG|M|BAP|SSN163-49-8702^^^SS
PV1|1|I|SURG^401^A^CHN_EAST||||ABANERJEE^Banerjee^Amit^K^^^MD|||SUR|||7|||ABANERJEE^Banerjee^Amit^K^^^MD|IP||||||||||||||||||CHN_EAST|||||20250401070000
TXA|1|OP^Operative Note|TX|20250401120000|ABANERJEE^Banerjee^Amit^K^^^MD||20250401143000||ABANERJEE^Banerjee^Amit^K^^^MD|||||DOC23456||AU|||
OBX|1|TX|28570-0^Operative Note^LN||PROCEDURE: Laparoscopic cholecystectomy. INDICATION: Symptomatic cholelithiasis. FINDINGS: Gallbladder with multiple stones, mild chronic inflammation. COMPLICATIONS: None.||||||F
```

---

## 17. ORU^R01 - Troponin result from IU Health Emergency

```
MSH|^~\&|EPIC|IUH_METH|LAB_RECV|IUH|20250402021500||ORU^R01^ORU_R01|MSG00054567|P|2.5.1|||AL|NE
PID|1||MRN19473826^^^IUH^MR||Osborne^Glenda^Ruth||19580116|F|||940 Pennsylvania St^^Indianapolis^IN^46204^US||^PRN^PH^^1^317^5559012||ENG|W|MET|SSN281-56-4903^^^SS
PV1|1|E|ED^TRIAGE^^IUH_METH||||FMALONE^Malone^Frank^L^^^MD|||EM|||1|||FMALONE^Malone^Frank^L^^^MD|ER
ORC|RE|ORD667788|RES667788||CM||||20250402021000|||FMALONE^Malone^Frank^L^^^MD
OBR|1|ORD667788|RES667788|49563-0^Troponin I^LN|||20250402013000|||||STAT||||||FMALONE^Malone^Frank^L^^^MD||||||20250402021500|||F
OBX|1|NM|49563-0^Troponin I, High Sensitivity^LN||0.045|ng/mL|<0.040|H|||F|||20250402021500
OBX|2|TX|49563-0^Troponin I, High Sensitivity^LN||NOTE: Mildly elevated. Recommend serial troponins q6h and cardiology consultation.||||||F
```

---

## 18. VXU^V04 - Adult flu vaccination at IU Health

```
MSH|^~\&|EPIC|IUH_NORTH|CHIRP|ISDH|20250403101500||VXU^V04^VXU_V04|MSG00057890|P|2.5.1|||AL|NE
PID|1||MRN60438271^^^IUH^MR||Shepherd^Kendra^Renee||19880503|F|||3281 Michigan Rd^^Indianapolis^IN^46268^US||^PRN^PH^^1^317^5550456
PD1|||IU HEALTH NORTH^^60438|BCOLEMAN^Coleman^Brian^D^^^MD
ORC|RE|IMM456789||||||||||BCOLEMAN^Coleman^Brian^D^^^MD
RXA|0|1|20250403101000|20250403101000|141^Influenza, seasonal^CVX|0.5|mL|IM|RA^^Right Arm||||||K8834B||SNF^Sanofi Pasteur|||||A
RXR|IM^Intramuscular^HL70162|RA^Right Arm^HL70163
OBX|1|CE|64994-7^Vaccine Funding Source^LN||V02^Private^CDCPHINVS||||||F
OBX|2|CE|30956-7^Vaccine Type^LN||141^Influenza, seasonal^CVX||||||F
```

---

## 19. ADT^A28 - New person registration at Eskenazi Health

```
MSH|^~\&|EPIC|ESKENAZI|MPI_RECV|IHIE|20250404080000||ADT^A28^ADT_A28|MSG00061234|P|2.5.1|||AL|NE
EVN|A28|20250404080000|||REG_CLERK
PID|1||MRN74029185^^^ESK^MR||Tran^Linh^Ngoc||19950820|F|||2107 East Washington St^^Indianapolis^IN^46201^US||^PRN^PH^^1^317^5553210||VIE|S|BUD|SSN392-74-0518^^^SS
PD1|||ESKENAZI PRIMARY CARE^^74029|MKHAN^Khan^Mohan^V^^^MD
NK1|1|Tran^Quang^Duc|FTH|2107 East Washington St^^Indianapolis^IN^46201^US|^PRN^PH^^1^317^5553211
IN1|1|MDCD01^Indiana Medicaid|MDCD001|Indiana Medicaid||||||||20250101|20251231|||MEDICAID|Tran^Linh^Ngoc|Self|19950820|2107 East Washington St^^Indianapolis^IN^46201^US
```

---

## 20. ORU^R01 - EKG report with embedded PDF from IU Health

```
MSH|^~\&|EPIC|IUH_METH|CARDIO_RECV|IUH|20250405093000||ORU^R01^ORU_R01|MSG00064567|P|2.5.1|||AL|NE
PID|1||MRN19473826^^^IUH^MR||Osborne^Glenda^Ruth||19580116|F|||940 Pennsylvania St^^Indianapolis^IN^46204^US||^PRN^PH^^1^317^5559012
PV1|1|I|CCU^301^A^IUH_METH||||WREYNOLDS^Reynolds^Warren^T^^^MD|||CAR|||7|||WREYNOLDS^Reynolds^Warren^T^^^MD|IP
ORC|RE|ORD778899|RES778899||CM||||20250405092000|||WREYNOLDS^Reynolds^Warren^T^^^MD
OBR|1|ORD778899|RES778899|93000^Electrocardiogram^CPT|||20250405085000||||||||WREYNOLDS^Reynolds^Warren^T^^^MD||||||20250405093000|||F
OBX|1|TX|93000^Electrocardiogram^CPT||INTERPRETATION: Normal sinus rhythm. Rate 72 bpm. Normal axis. No ST-T wave changes. QTc 420ms.||||||F
OBX|2|ED|PDF^EKG Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F
```
