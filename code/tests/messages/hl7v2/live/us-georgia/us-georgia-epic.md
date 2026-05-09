# Epic (Bridges) - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission at Emory University Hospital

```
MSH|^~\&|EPIC|EMORY_UH|LABSYS|EMORY_LAB|20260401083015||ADT^A01^ADT_A01|MSG00001|P|2.5.1|||AL|NE
EVN|A01|20260401083000|||JBRAXTON^Braxton^Janelle^M^^RN
PID|1||E10034829^^^EMORY_MRN^MR||Mabry^Terrence^Lamont^^Mr||19670315|M|||245 Peachtree Center Ave NE^^Atlanta^GA^30303^US||^PRN^PH^^1^404^5551234||||S||E10034829001|418-72-9035
PV1|1|I|4EAST^4102^A^EMORY_UH^^^^NURS|E|||12345^Okafor^Sarah^A^^^MD|67890^Whitfield^Robert^T^^^MD||MED||||A|||12345^Okafor^Sarah^A^^^MD|IN||BCBS|||||||||||||||||||EMORY_UH|||||20260401083000
PV2|||^Chest pain, unspecified^I10
IN1|1|BCBS001^Blue Cross Blue Shield of Georgia|54321|Blue Cross Blue Shield|||||||||||Mabry^Denise^R|SPO|19700812|245 Peachtree Center Ave NE^^Atlanta^GA^30303^US
NK1|1|Mabry^Denise^Renee|SPO^Spouse|245 Peachtree Center Ave NE^^Atlanta^GA^30303^US|^PRN^PH^^1^404^5551235
DG1|1||R07.9^Chest pain, unspecified^ICD10||20260401|A
```

---

## 2. ADT^A02 - Patient transfer at Piedmont Atlanta Hospital

```
MSH|^~\&|EPICADT|PIEDMONT_ATL|TRACKER|PIED_TRACK|20260402140530||ADT^A02^ADT_A02|MSG00002|P|2.5.1|||AL|NE
EVN|A02|20260402140500|||BTHORNTON^Thornton^Barbara^R^^RN
PID|1||P20458193^^^PIEDMONT_MRN^MR||Harrell^Angela^Christine^^Mrs||19820721|F|||1968 Peachtree Rd NW^^Atlanta^GA^30309^US||^PRN^PH^^1^404^5552345||||M||P20458193001|327-48-6190
PV1|1|I|3ICU^3204^B^PIEDMONT_ATL^^^^NURS|U|||23456^Espinoza^Carlos^E^^^MD|34567^Lattimore^Katherine^L^^^MD||ICU||||T|||23456^Espinoza^Carlos^E^^^MD|IN||AETNA|||||||||||||||||||PIEDMONT_ATL|||||20260330120000
PV2|||^Acute respiratory failure^J96.00
```

---

## 3. ADT^A03 - Patient discharge from WellStar Kennestone

```
MSH|^~\&|EPIC|WELLSTAR_KEN|RCMSYS|WS_BILLING|20260403161200||ADT^A03^ADT_A03|MSG00003|P|2.5.1|||AL|NE
EVN|A03|20260403161000|||MLEE^Prescott^Margaret^A^^RN
PID|1||W30582741^^^WELLSTAR_MRN^MR||Strickland^Cedric^William^^Mr||19551108|M|||677 Church St NE^^Marietta^GA^30060^US||^PRN^PH^^1^770^5553456||||W||W30582741001|540-81-7293
PV1|1|I|5MED^5310^A^WS_KENNESTONE^^^^NURS|E|||45678^Mehta^Ravi^K^^^MD|56789^Gresham^Amanda^J^^^MD||MED||||D|||45678^Mehta^Ravi^K^^^MD|IN||HUMANA|||||||||||||||||||WS_KENNESTONE|||||20260401090000|20260403161000
PV2|||^Type 2 diabetes mellitus with hyperglycemia^E11.65
DG1|1||E11.65^Type 2 diabetes mellitus with hyperglycemia^ICD10||20260401|A
DG1|2||I10^Essential hypertension^ICD10||20260401|S
```

---

## 4. ADT^A04 - Patient registration at Children's Healthcare of Atlanta

```
MSH|^~\&|EPICCARE|CHOA_EGLESTON|REGAPP|CHOA_REG|20260404091500||ADT^A04^ADT_A04|MSG00004|P|2.5.1|||AL|NE
EVN|A04|20260404091000|||KWILKINS^Wilkins^Karen^D^^RN
PID|1||C40129384^^^CHOA_MRN^MR||Restrepo^Valentina^Isabel||20180614|F|||2015 Uppergate Dr NE^^Atlanta^GA^30322^US||^PRN^PH^^1^404^5554567||||S||C40129384001
PD1|||Children's Healthcare of Atlanta^^12345|78901^Lockhart^Michelle^L^^^MD
PV1|1|O|PEDCL^EXAM3^^CHOA_EGLESTON^^^^OUTPT|R|||78901^Lockhart^Michelle^L^^^MD|||PED||||N|||78901^Lockhart^Michelle^L^^^MD|OP||PEACHSTATE|||||||||||||||||||CHOA_EGLESTON|||||20260404091000
NK1|1|Restrepo^Lucia^Sofia|MTH^Mother|2015 Uppergate Dr NE^^Atlanta^GA^30322^US|^PRN^PH^^1^404^5554568
IN1|1|PEACH001^PeachState Health Plan|88001|PeachState Health Plan|||||||||||Restrepo^Lucia^Sofia|MTH|19890203|2015 Uppergate Dr NE^^Atlanta^GA^30322^US
```

---

## 5. ADT^A08 - Patient information update at Emory Midtown

```
MSH|^~\&|EPIC|EMORY_MID|MASTERPATIENT|EMORY_MPI|20260405103045||ADT^A08^ADT_A08|MSG00005|P|2.5.1|||AL|NE
EVN|A08|20260405103000|||RJEFFERSON^Jefferson^Rebecca^L^^REG
PID|1||E10098234^^^EMORY_MRN^MR||Quarles^Denise^Monique^^Ms||19740519|F|||550 Peachtree St NE^^Atlanta^GA^30308^US||^PRN^PH^^1^404^5555678~^PRN^CP^^1^678^5559012||||D||E10098234001|613-24-8057
PV1|1|I|6SURG^6201^A^EMORY_MID^^^^NURS|E|||11111^Thornton^David^M^^^MD|||SURG||||A|||11111^Thornton^David^M^^^MD|IN||CIGNA|||||||||||||||||||EMORY_MID|||||20260404070000
NK1|1|Quarles^Reginald^Tyrone|FTH^Father|123 Magnolia St^^Decatur^GA^30030^US|^PRN^PH^^1^404^5555679
```

---

## 6. ADT^A28 - Add person information at Piedmont Columbus

```
MSH|^~\&|EPICADT|PIED_COLUMBUS|MPI_SYS|PIED_MPI|20260406080000||ADT^A28^ADT_A28|MSG00006|P|2.5.1|||AL|NE
EVN|A28|20260406075500|||SYSTEM
PID|1||P30987654^^^PIEDMONT_MRN^MR||Culpepper^Patricia^Elaine^^Mrs||19630227|F|||4501 Veterans Pkwy^^Columbus^GA^31904^US||^PRN^PH^^1^706^5556789||||M||P30987654001|782-15-4093
PD1|||Piedmont Columbus Regional^^23456|22222^Underwood^Thomas^P^^^MD
NK1|1|Culpepper^Leonard^Ray|SPO^Spouse|4501 Veterans Pkwy^^Columbus^GA^31904^US|^PRN^PH^^1^706^5556790
IN1|1|UHC001^UnitedHealthcare|99002|UnitedHealthcare|||||||||||Culpepper^Leonard^Ray|SPO|19600915|4501 Veterans Pkwy^^Columbus^GA^31904^US
```

---

## 7. ADT^A31 - Update person information at WellStar Cobb

```
MSH|^~\&|EPICADT|WELLSTAR_COBB|EMPI|WS_EMPI|20260407142030||ADT^A31^ADT_A31|MSG00007|P|2.5.1|||AL|NE
EVN|A31|20260407142000|||SYSTEM
PID|1||W30234567^^^WELLSTAR_MRN^MR||Bradshaw^Quinton^Lamar^^Mr||19880913|M|||3950 Austell Rd^^Austell^GA^30106^US||^PRN^PH^^1^770^5557890~^PRN^CP^^1^678^5557891||||S||W30234567001|290-56-8174
PD1|||WellStar Cobb Hospital^^34567|33333^Nair^Priya^S^^^MD
```

---

## 8. ORM^O01 - Lab order at Emory University Hospital

```
MSH|^~\&|EPIC|EMORY_UH|LABSYS|EMORY_LAB|20260408071530||ORM^O01^ORM_O01|MSG00008|P|2.5.1|||AL|NE
PID|1||E10045678^^^EMORY_MRN^MR||Blanchard^Derrick^Raymond^^Mr||19710804|M|||1440 Clifton Rd NE^^Atlanta^GA^30322^US||^PRN^PH^^1^404^5558901||||M||E10045678001|805-39-2716
PV1|1|I|7MED^7415^B^EMORY_UH^^^^NURS|E|||44444^Pemberton^Angela^R^^^MD|||MED||||A|||44444^Pemberton^Angela^R^^^MD|IN||BCBS|||||||||||||||||||EMORY_UH|||||20260407210000
ORC|NW|ORD9283741^EPIC|||||^^^20260408080000^^R||20260408071500|JCOLEMAN^Coleman^Janice^R^^RN||44444^Pemberton^Angela^R^^^MD|||||EMORY_UH^Emory University Hospital
OBR|1|ORD9283741^EPIC||CBC^Complete Blood Count^L|||20260408080000||||N|||||44444^Pemberton^Angela^R^^^MD|||||||||||^^^20260408080000^^R
OBR|2|ORD9283741^EPIC||BMP^Basic Metabolic Panel^L|||20260408080000||||N|||||44444^Pemberton^Angela^R^^^MD|||||||||||^^^20260408080000^^R
```

---

## 9. ORU^R01 - Lab results from Piedmont Atlanta Hospital

```
MSH|^~\&|EPICBRIDGES|PIEDMONT_ATL|LABSYS|PIED_LAB|20260409101200||ORU^R01^ORU_R01|MSG00009|P|2.5.1|||AL|NE
PID|1||P20567890^^^PIEDMONT_MRN^MR||Goodwin^Natasha^Chanel^^Ms||19930412|F|||3541 Roswell Rd NE^^Atlanta^GA^30305^US||^PRN^PH^^1^404^5559012||||S||P20567890001|946-28-3051
PV1|1|O|LABDRW^DRAW1^^PIEDMONT_ATL^^^^OUTPT|R|||55555^Cho^James^H^^^MD|||LAB||||N|||55555^Cho^James^H^^^MD|OP||AETNA
ORC|RE|ORD8374625^EPIC|LAB293847^PIED_LAB|||CM||||||55555^Cho^James^H^^^MD
OBR|1|ORD8374625^EPIC|LAB293847^PIED_LAB|CBC^Complete Blood Count^L|||20260409083000|||||||20260409084500||55555^Cho^James^H^^^MD||||||20260409101000||LAB|F
OBX|1|NM|6690-2^WBC^LN||7.2|10*3/uL|4.5-11.0|N|||F|||20260409101000
OBX|2|NM|789-8^RBC^LN||4.85|10*6/uL|4.20-5.40|N|||F|||20260409101000
OBX|3|NM|718-7^Hemoglobin^LN||14.1|g/dL|12.0-16.0|N|||F|||20260409101000
OBX|4|NM|4544-3^Hematocrit^LN||42.3|%|36.0-46.0|N|||F|||20260409101000
OBX|5|NM|787-2^MCV^LN||87.2|fL|80.0-100.0|N|||F|||20260409101000
OBX|6|NM|777-3^Platelets^LN||245|10*3/uL|150-400|N|||F|||20260409101000
```

---

## 10. ORU^R01 - Pathology result with embedded PDF from Emory

```
MSH|^~\&|EPICBRIDGES|EMORY_UH|PATHSYS|EMORY_PATH|20260410143000||ORU^R01^ORU_R01|MSG00010|P|2.5.1|||AL|NE
PID|1||E10067890^^^EMORY_MRN^MR||Stockton^William^Reginald^^Mr||19580216|M|||789 Juniper St NE^^Atlanta^GA^30308^US||^PRN^PH^^1^404^5550123||||M||E10067890001|261-47-8503
PV1|1|I|5ONCO^5108^A^EMORY_UH^^^^NURS|E|||66666^Tran^Thanh^V^^^MD|||ONC||||A|||66666^Tran^Thanh^V^^^MD|IN||MEDICARE
ORC|RE|ORD7463829^EPIC|PATH384756^EMORY_PATH|||CM||||||66666^Tran^Thanh^V^^^MD
OBR|1|ORD7463829^EPIC|PATH384756^EMORY_PATH|11529-5^Surgical Pathology Study^LN|||20260409100000|||||||20260409103000||66666^Tran^Thanh^V^^^MD||||||20260410142500||PATH|F
OBX|1|ED|11529-5^Surgical Pathology Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2Jq||||||F
OBX|2|ST|22637-3^Path report.final diagnosis^LN||Invasive ductal carcinoma, Grade 2||||||F|||20260410142500
```

---

## 11. SIU^S12 - Appointment scheduling at Piedmont Henry

```
MSH|^~\&|EPIC|PIEDMONT_HENRY|SCHEDSYS|PIED_SCHED|20260411091500||SIU^S12^SIU_S12|MSG00011|P|2.5.1|||AL|NE
SCH|APT9384756^EPIC|||||OFFICE^Office Visit|FOLLOWUP^Follow-up|30|MIN|^^30^20260418140000^20260418143000|||||77777^Ellison^Gregory^S^^^MD|^PRN^PH^^1^770^5551111|PIED_HENRY_CARD^^^PIEDMONT_HENRY|77777^Ellison^Gregory^S^^^MD|^PRN^PH^^1^770^5551112|PIED_HENRY_CARD^^^PIEDMONT_HENRY
PID|1||P20789012^^^PIEDMONT_MRN^MR||Upshaw^Stephanie^Louise^^Mrs||19850306|F|||1133 Eagles Landing Pkwy^^Stockbridge^GA^30281^US||^PRN^PH^^1^770^5551234||||M
PV1|1|O|CARD^EXAM2^^PIEDMONT_HENRY^^^^OUTPT|R|||77777^Ellison^Gregory^S^^^MD|||CARD||||N
RGS|1||PIED_HENRY_CARD^^^PIEDMONT_HENRY
AIS|1||CARDFOLLOW^Cardiology Follow-up^L|20260418140000|||30|MIN
AIP|1||77777^Ellison^Gregory^S^^^MD|ATND|20260418140000|||30|MIN
```

---

## 12. MDM^T02 - Document notification with embedded PDF from WellStar

```
MSH|^~\&|EPICCARE|WELLSTAR_KEN|DOCSYS|WS_DOCS|20260412113000||MDM^T02^MDM_T02|MSG00012|P|2.5.1|||AL|NE
EVN|T02|20260412112500
PID|1||W30345678^^^WELLSTAR_MRN^MR||Kingsley^Jerome^Devon^^Mr||19790823|M|||2700 Sandy Plains Rd^^Marietta^GA^30066^US||^PRN^PH^^1^770^5552345||||M||W30345678001|073-51-9284
PV1|1|I|3MED^3218^A^WS_KENNESTONE^^^^NURS|E|||88888^Cordova^Maria^C^^^MD|||MED||||A|||88888^Cordova^Maria^C^^^MD|IN||BCBS
TXA|1|DS^Discharge Summary|TX|20260412112000|88888^Cordova^Maria^C^^^MD||20260412112500||||DOC8374659^EPIC||||AU||AV
OBX|1|ED|18842-5^Discharge Summary^LN||^application^pdf^Base64^JVBERi0xLjQNCjEgMCBvYmoNCjw8IC9UeXBlIC9DYXRhbG9nIC9QYWdlcyAyIDAgUiA+Pg0KZW5kb2JqDQoyIDAgb2JqDQo8PCAvVHlwZSAvUGFnZXMgL0tpZHMgWzMgMCBSXSAvQ291bnQgMSA+Pg0KZW5kb2Jq||||||F
```

---

## 13. ADT^A01 - Admission at Piedmont Athens Regional

```
MSH|^~\&|EPIC|PIED_ATHENS|NURSESYS|PIED_NURS|20260413070000||ADT^A01^ADT_A01|MSG00013|P|2.5.1|||AL|NE
EVN|A01|20260413065500|||LHENDERSON^Henderson^Laura^K^^RN
PID|1||P20890123^^^PIEDMONT_MRN^MR||Copeland^Marcus^Dominique^^Mr||19920107|M|||1199 Prince Ave^^Athens^GA^30606^US||^PRN^PH^^1^706^5553456||||S||P20890123001|175-30-6482
PV1|1|I|2MED^2105^A^PIED_ATHENS^^^^NURS|E|||99999^Bhatt^Arun^P^^^MD|10101^Pressley^Christine^M^^^MD||MED||||A|||99999^Bhatt^Arun^P^^^MD|IN||ANTHEM|||||||||||||||||||PIED_ATHENS|||||20260413065500
PV2|||^Acute appendicitis without peritonitis^K35.80
NK1|1|Copeland^Brenda^Yvette|MTH^Mother|422 Baxter St^^Athens^GA^30601^US|^PRN^PH^^1^706^5553457
DG1|1||K35.80^Acute appendicitis without peritonitis^ICD10||20260413|A
```

---

## 14. ORM^O01 - Radiology order at Emory Saint Joseph's

```
MSH|^~\&|EPICCARE|EMORY_STJ|RADSYS|EMORY_RAD|20260414085000||ORM^O01^ORM_O01|MSG00014|P|2.5.1|||AL|NE
PID|1||E10089012^^^EMORY_MRN^MR||Maddox^Sandra^Elaine^^Mrs||19680930|F|||5665 Peachtree Dunwoody Rd NE^^Atlanta^GA^30342^US||^PRN^PH^^1^404^5554567||||M||E10089012001|408-62-7139
PV1|1|O|RADOL^WAIT1^^EMORY_STJ^^^^OUTPT|R|||20202^Flanagan^Patrick^J^^^MD|||RAD||||N|||20202^Flanagan^Patrick^J^^^MD|OP||CIGNA
ORC|NW|ORD6374859^EPIC|||||^^^20260414100000^^R||20260414084500|ACLERK^Clerk^Admin^A||20202^Flanagan^Patrick^J^^^MD|||||EMORY_STJ^Emory Saint Joseph's Hospital
OBR|1|ORD6374859^EPIC||71260^CT Chest with Contrast^CPT|||20260414100000||||N|||||20202^Flanagan^Patrick^J^^^MD|||||||||||^^^20260414100000^^R
```

---

## 15. ORU^R01 - Chemistry results from WellStar Paulding

```
MSH|^~\&|EPICBRIDGES|WELLSTAR_PAULD|LABSYS|WS_LAB|20260415141500||ORU^R01^ORU_R01|MSG00015|P|2.5.1|||AL|NE
PID|1||W30456789^^^WELLSTAR_MRN^MR||Whitaker^Terrence^Andre^^Mr||19810525|M|||135 Hospital Dr^^Dallas^GA^30132^US||^PRN^PH^^1^770^5555678||||S||W30456789001|642-07-1835
PV1|1|O|LABDRW^DRAW2^^WS_PAULDING^^^^OUTPT|R|||30303^Neville^Janet^E^^^MD|||LAB||||N|||30303^Neville^Janet^E^^^MD|OP||UHC
ORC|RE|ORD5738291^EPIC|LAB394857^WS_LAB|||CM||||||30303^Neville^Janet^E^^^MD
OBR|1|ORD5738291^EPIC|LAB394857^WS_LAB|BMP^Basic Metabolic Panel^L|||20260415120000|||||||20260415121500||30303^Neville^Janet^E^^^MD||||||20260415141000||LAB|F
OBX|1|NM|2345-7^Glucose^LN||98|mg/dL|70-100|N|||F|||20260415141000
OBX|2|NM|3094-0^BUN^LN||16|mg/dL|7-20|N|||F|||20260415141000
OBX|3|NM|2160-0^Creatinine^LN||1.0|mg/dL|0.7-1.3|N|||F|||20260415141000
OBX|4|NM|2951-2^Sodium^LN||140|mmol/L|136-145|N|||F|||20260415141000
OBX|5|NM|2823-3^Potassium^LN||4.2|mmol/L|3.5-5.1|N|||F|||20260415141000
OBX|6|NM|2075-0^Chloride^LN||102|mmol/L|98-106|N|||F|||20260415141000
OBX|7|NM|2028-9^CO2^LN||24|mmol/L|22-29|N|||F|||20260415141000
OBX|8|NM|17861-6^Calcium^LN||9.4|mg/dL|8.5-10.5|N|||F|||20260415141000
```

---

## 16. SIU^S12 - Surgery scheduling at Emory Midtown

```
MSH|^~\&|EPIC|EMORY_MID|ORSCHED|EMORY_OR|20260416100000||SIU^S12^SIU_S12|MSG00016|P|2.5.1|||AL|NE
SCH|APT8293746^EPIC|||||SURGERY^Surgical Procedure|ELECTIVE^Elective|120|MIN|^^120^20260423073000^20260423093000|||||40404^Liang^Wei^L^^^MD|^PRN^PH^^1^404^5556789|EMORY_MID_OR^^^EMORY_MID|40404^Liang^Wei^L^^^MD|^PRN^PH^^1^404^5556790|EMORY_MID_OR^^^EMORY_MID
PID|1||E10012345^^^EMORY_MRN^MR||Cavanaugh^Katherine^Diane^^Mrs||19750218|F|||400 10th St NW^^Atlanta^GA^30318^US||^PRN^PH^^1^404^5556788||||M
PV1|1|P|PREOP^PRE1^^EMORY_MID^^^^OUTPT|E|||40404^Liang^Wei^L^^^MD|||SURG||||P
RGS|1||EMORY_MID_OR^^^EMORY_MID
AIS|1||27447^Total Knee Replacement^CPT|20260423073000|||120|MIN
AIP|1||40404^Liang^Wei^L^^^MD|ATND|20260423073000|||120|MIN
AIL|1||EMORY_MID_OR^OR3^A^EMORY_MID|20260423073000|||120|MIN
```

---

## 17. ADT^A03 - Discharge from Children's Healthcare of Atlanta

```
MSH|^~\&|EPICADT|CHOA_SCOTTISH|BILLING|CHOA_FIN|20260417154500||ADT^A03^ADT_A03|MSG00017|P|2.5.1|||AL|NE
EVN|A03|20260417154000|||NPARKER^Eckert^Nancy^J^^RN
PID|1||C40234567^^^CHOA_MRN^MR||Salazar^Diego^Alejandro||20150922|M|||1001 Johnson Ferry Rd NE^^Atlanta^GA^30342^US||^PRN^PH^^1^404^5557890||||S||C40234567001
PV1|1|I|4PED^4210^B^CHOA_SCOTTISH^^^^NURS|U|||50505^Blackwell^Tonya^M^^^MD|60606^Yoon^Sung^H^^^MD||PED||||D|||50505^Blackwell^Tonya^M^^^MD|IN||PEACHSTATE|||||||||||||||||||CHOA_SCOTTISH|||||20260414110000|20260417154000
PV2|||^Acute lymphoblastic leukemia^C91.00
NK1|1|Salazar^Carmen^Beatriz|MTH^Mother|1001 Johnson Ferry Rd NE^^Atlanta^GA^30342^US|^PRN^PH^^1^404^5557891
DG1|1||C91.00^Acute lymphoblastic leukemia, not having achieved remission^ICD10||20260414|A
```

---

## 18. ORU^R01 - Microbiology results from Piedmont Macon

```
MSH|^~\&|EPICBRIDGES|PIEDMONT_MACON|MICROSYS|PIED_MICRO|20260418120000||ORU^R01^ORU_R01|MSG00018|P|2.5.1|||AL|NE
PID|1||P20901234^^^PIEDMONT_MRN^MR||Lattimore^Dorothy^Evelyn^^Mrs||19490805|F|||777 Hemlock St^^Macon^GA^31201^US||^PRN^PH^^1^478^5558901||||W||P20901234001|531-84-0279
PV1|1|I|3MED^3112^A^PIED_MACON^^^^NURS|U|||70707^Kendall^Mark^A^^^MD|||MED||||A|||70707^Kendall^Mark^A^^^MD|IN||MEDICARE
ORC|RE|ORD4629384^EPIC|MICRO847362^PIED_MICRO|||CM||||||70707^Kendall^Mark^A^^^MD
OBR|1|ORD4629384^EPIC|MICRO847362^PIED_MICRO|87070^Culture, bacterial^CPT|||20260416140000|||||||20260416141500||70707^Kendall^Mark^A^^^MD||||||20260418115500||MICRO|F
OBX|1|ST|11475-1^Microorganism identified^LN||Escherichia coli||||||F|||20260418115500
OBX|2|ST|18907-6^Susceptibility method^LN||Disk diffusion||||||F|||20260418115500
OBX|3|ST|18964-7^Ampicillin susceptibility^LN||Resistant||||||F|||20260418115500
OBX|4|ST|18969-6^Ciprofloxacin susceptibility^LN||Susceptible||||||F|||20260418115500
OBX|5|ST|18993-6^Gentamicin susceptibility^LN||Susceptible||||||F|||20260418115500
```

---

## 19. MDM^T02 - Clinical note from Piedmont Newnan

```
MSH|^~\&|EPICCARE|PIEDMONT_NEWNAN|DOCSYS|PIED_DOCS|20260419093000||MDM^T02^MDM_T02|MSG00019|P|2.5.1|||AL|NE
EVN|T02|20260419092500
PID|1||P20012345^^^PIEDMONT_MRN^MR||Gilstrap^Angela^Yvette^^Ms||19870614|F|||22 Hospital Rd^^Newnan^GA^30263^US||^PRN^PH^^1^770^5559012||||S||P20012345001|714-05-9328
PV1|1|O|CLINIC^EXAM4^^PIED_NEWNAN^^^^OUTPT|R|||80808^Caldwell^Brian^K^^^MD|||FP||||N|||80808^Caldwell^Brian^K^^^MD|OP||ANTHEM
TXA|1|HP^History and Physical|TX|20260419091500|80808^Caldwell^Brian^K^^^MD||20260419092500||||DOC7362948^EPIC||||AU||AV
OBX|1|TX|11506-3^Progress Note^LN||Patient presents with 3-day history of productive cough and low-grade fever. Lungs with bilateral rhonchi. Assessment: Acute bronchitis. Plan: Supportive care, follow-up in 1 week.||||||F
```

---

## 20. ORU^R01 - Cardiology results from Emory Decatur

```
MSH|^~\&|EPICBRIDGES|EMORY_DECATUR|CARDSYS|EMORY_CARD|20260420160000||ORU^R01^ORU_R01|MSG00020|P|2.5.1|||AL|NE
PID|1||E10078901^^^EMORY_MRN^MR||Holbrook^Gregory^Nathan^^Mr||19640319|M|||2701 N Decatur Rd^^Decatur^GA^30033^US||^PRN^PH^^1^404^5550234||||M||E10078901001|829-46-3017
PV1|1|O|CARDLAB^ECHO1^^EMORY_DECATUR^^^^OUTPT|R|||90909^Chandra^Anita^D^^^MD|||CARD||||N|||90909^Chandra^Anita^D^^^MD|OP||HUMANA
ORC|RE|ORD3847562^EPIC|CARD948372^EMORY_CARD|||CM||||||90909^Chandra^Anita^D^^^MD
OBR|1|ORD3847562^EPIC|CARD948372^EMORY_CARD|93306^Echocardiography^CPT|||20260420140000|||||||20260420141000||90909^Chandra^Anita^D^^^MD||||||20260420155500||CARD|F
OBX|1|NM|18043-0^LVEF^LN||55|%|55-70|N|||F|||20260420155500
OBX|2|TX|18044-8^LV wall motion^LN||Normal wall motion, no regional abnormalities||||||F|||20260420155500
OBX|3|NM|18148-7^LV end-diastolic dimension^LN||4.8|cm|3.5-5.6|N|||F|||20260420155500
OBX|4|TX|18145-3^Valve assessment^LN||Mild mitral regurgitation. Aortic valve trileaflet with normal function.||||||F|||20260420155500
OBX|5|TX|18146-1^Overall impression^LN||Normal LV size and systolic function. Mild mitral regurgitation. No pericardial effusion.||||||F|||20260420155500
```
