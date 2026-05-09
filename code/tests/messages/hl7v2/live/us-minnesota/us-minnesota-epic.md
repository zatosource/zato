# Epic Systems - real HL7v2 ER7 messages

## 1. ADT^A01 - Inpatient admission at Mayo Clinic Rochester

```
MSH|^~\&|EPIC|MAYOCLINIC|LABSYS|MAYOCLINIC|20250312081523||ADT^A01^ADT_A01|MCR20250312081523001|P|2.5.1|||AL|NE
EVN|A01|20250312081500|||RSOLBERG^Solberg^Rachel^E^^MD|20250312080000
PID|1||E10034782^^^EPIC^MRN~500128943^^^MAYOMPI^MR||NYGAARD^Anders^Leif^^^Mr.||19680215|M||2106-3^White^CDCREC|1425 Silver Lake Rd NW^^Rochester^MN^55901^US^L||^PRN^PH^^^507^2885431~^NET^Internet^anders.nygaard@email.com|^WPN^PH^^^507^5553890|eng^English^ISO6392|M^Married^HL70002|||482-31-7259|||N^Non-Hispanic^HL70189
PD1|||MAYO CLINIC ROCHESTER^^10001|3187294560^Reinhardt^Thomas^C^^MD^^^NPI
NK1|1|NYGAARD^Sigrid^Helene|SPO^Spouse^HL70063|1425 Silver Lake Rd NW^^Rochester^MN^55901^US|^PRN^PH^^^507^2885432||EC^Emergency Contact^HL70131
PV1|1|I|5MARY^5102^A^MAYOCLINIC^^^^5MARY||||3187294560^Reinhardt^Thomas^C^^MD^^^NPI|4298305671^Engstrom^Linnea^J^^MD^^^NPI|CAR^Cardiology^MAYOSERV|||R^Referral^HL70007|||||V10029384^^^MAYOENC^VN|||||||||||||||||||||||||20250312081500
PV2|||^Chest pain, unspecified^I20.9
IN1|1|BCMN001^Blue Cross Blue Shield of MN^^BCBSMN|54321|BLUE CROSS BLUE SHIELD OF MINNESOTA|PO Box 64179^^St. Paul^MN^55164^US|^PRN^PH^^^651^6623000|GRP98201||MAYO CLINIC|||||20240101|20251231|||1^Subscriber^HL70072|NYGAARD^Anders^Leif|01^Self^HL70063|19680215|1425 Silver Lake Rd NW^^Rochester^MN^55901^US|||1|||YES||||||||||XHB901234567
IN1|2|MEDCR001^Medicare^^CMS|00001|MEDICARE|PO Box 1270^^Portland^ME^04104^US||||||||20330215|||2^Secondary^HL70072|NYGAARD^Anders^Leif|01^Self^HL70063|19680215|1425 Silver Lake Rd NW^^Rochester^MN^55901^US
```

---

## 2. ADT^A04 - Emergency department registration at Allina Health United Hospital

```
MSH|^~\&|EPIC|ALLINAUH|EDIS|ALLINAUH|20250418143022||ADT^A04^ADT_A01|AUH20250418143022001|P|2.5.1|||AL|NE
EVN|A04|20250418143000|||KFISCHER^Fischer^Karen^D^^RN|20250418142500
PID|1||E20187643^^^EPIC^MRN~700234581^^^ALLINAMPI^MR||HAUGEN^Britta^Solveig^^^Mrs.||19850923|F||2106-3^White^CDCREC|892 Summit Ave^^St. Paul^MN^55105^US^L||^PRN^PH^^^651^2274819~^NET^Internet^b.haugen85@email.com||eng^English^ISO6392|M^Married^HL70002|||591-42-8037|||N^Non-Hispanic^HL70189
PD1|||ALLINA HEALTH UNITED HOSPITAL^^20001|5309812746^Bremer^Kathleen^S^^MD^^^NPI
NK1|1|HAUGEN^Gunnar^Rolf|SPO^Spouse^HL70063|892 Summit Ave^^St. Paul^MN^55105^US|^PRN^PH^^^651^2274820||EC^Emergency Contact^HL70131
PV1|1|E|EDUH^ED12^A^ALLINAUH^^^^EDUH||||5309812746^Bremer^Kathleen^S^^MD^^^NPI|6410923857^Pfeifer^Roland^H^^MD^^^NPI|EM^Emergency Medicine^ALLINASERV|||E^Emergency^HL70007|||||V20050192^^^ALLINAENC^VN|||||||||||||||||||||||||20250418143000
PV2|||^Acute appendicitis^K35.80
IN1|1|UHCMN001^UnitedHealthcare MN^^UHC|88321|UNITEDHEALTHCARE OF MINNESOTA|PO Box 1459^^Minneapolis^MN^55440^US|^PRN^PH^^^800^3281044|GRP44521||TARGET CORPORATION|||||20240601|20251231|||1^Subscriber^HL70072|HAUGEN^Britta^Solveig|01^Self^HL70063|19850923|892 Summit Ave^^St. Paul^MN^55105^US|||1|||YES||||||||||UHC7701234567
```

---

## 3. ADT^A02 - Patient transfer at Fairview Southdale Hospital

```
MSH|^~\&|EPIC|FVWSDALE|ADT_RECV|FVWSDALE|20250505092145||ADT^A02^ADT_A02|FSD20250505092145001|P|2.5.1|||AL|NE
EVN|A02|20250505092100|||MBRAUN^Braun^Monica^L^^RN|20250505091500
PID|1||E30298451^^^EPIC^MRN~800345672^^^FVWMPI^MR||SOLBERG^Kenneth^Otto^^^Mr.||19520714|M||2106-3^White^CDCREC|3301 W 66th St^^Edina^MN^55435^US^L||^PRN^PH^^^952^9293847||eng^English^ISO6392|W^Widowed^HL70002|||718-53-2604|||N^Non-Hispanic^HL70189
PV1|1|I|4ICU^4201^A^FVWSDALE^^^^4ICU||||7521034968^Kirscht^Allen^J^^MD^^^NPI|8632145079^Schultz^Vera^M^^MD^^^NPI|MED^Medicine^FVWSERV|||T^Transfer^HL70007|||||V30061283^^^FVWENC^VN|||||||||||||||||3MEDSURG^3105^B^FVWSDALE^^^^3MEDSURG||||||20250505092100
```

---

## 4. ADT^A03 - Discharge from HealthPartners Regions Hospital

```
MSH|^~\&|EPIC|HPREGIONS|BILLING|HPREGIONS|20250220161030||ADT^A03^ADT_A03|HPR20250220161030001|P|2.5.1|||AL|NE
EVN|A03|20250220161000|||TENGEL^Engel^Tanya^R^^RN|20250220155500
PID|1||E40312987^^^EPIC^MRN~900456783^^^HPMPI^MR||OVERBY^Marlene^Ingrid^^^Mrs.||19711108|F||2106-3^White^CDCREC|7620 Bush Lake Rd^^Bloomington^MN^55438^US^L||^PRN^PH^^^952^8314572~^NET^Internet^marlene.overby71@email.com||eng^English^ISO6392|D^Divorced^HL70002|||803-64-5291|||N^Non-Hispanic^HL70189
PV1|1|I|6ORTHO^6304^A^HPREGIONS^^^^6ORTHO||||9743016825^Storlie^Gregory^T^^MD^^^NPI|1854027936^Ellingson^Renee^E^^MD^^^NPI|ORT^Orthopedics^HPSERV|||R^Referral^HL70007|||||V40072394^^^HPENC^VN||DI^Discharged to Home^HL70112||||||||||||||||||||||||20250218090000|20250220161000
DG1|1||M17.11^Primary osteoarthritis, right knee^I10||20250218|A^Admitting^HL70052
DG1|2||Z96.641^Presence of right artificial knee joint^I10||20250220|F^Final^HL70052
PR1|1||0SRC0J9^Replacement of Right Knee Joint with Synthetic Substitute, Cemented, Open Approach^ICD10PCS|Total right knee arthroplasty|20250219100000|A^Anesthesia^HL70230||||||9743016825^Storlie^Gregory^T^^MD^^^NPI
```

---

## 5. ADT^A08 - Patient information update at Essentia Health Duluth

```
MSH|^~\&|EPIC|ESSENTIADL|REGUPD|ESSENTIADL|20250609140512||ADT^A08^ADT_A01|EDL20250609140512001|P|2.5.1|||AL|NE
EVN|A08|20250609140500|||JRONNING^Ronning^Janelle^K^^REG|20250609140000
PID|1||E50423198^^^EPIC^MRN~100567894^^^ESSMPI^MR||DAHLSTROM^Curtis^Arvid^^^Mr.||19880316|M||2106-3^White^CDCREC|2214 E 4th St^^Duluth^MN^55812^US^L||^PRN^PH^^^218^7264583~^NET^Internet^cdahlstrom88@email.com||eng^English^ISO6392|S^Single^HL70002|||914-67-3582|||N^Non-Hispanic^HL70189
PD1|||ESSENTIA HEALTH DULUTH^^30001|2065138947^Tveit^Henrik^S^^MD^^^NPI
NK1|1|DAHLSTROM^Astrid^Karin|MTH^Mother^HL70063|418 W Skyline Pkwy^^Duluth^MN^55806^US|^PRN^PH^^^218^7265190||EC^Emergency Contact^HL70131
PV1|1|O|ESSCLIN^VIST3^A^ESSENTIADL^^^^ESSCLIN||||2065138947^Tveit^Henrik^S^^MD^^^NPI||PCP^Primary Care^ESSSERV|||R^Referral^HL70007|||||V50083495^^^ESSENC^VN|||||||||||||||||||||||||20250609140000
IN1|1|PERA001^PreferredOne^^PREFONE|77401|PREFERREDONE|PO Box 59052^^Minneapolis^MN^55459^US|^PRN^PH^^^763^8471234|GRP55102||ESSENTIA HEALTH|||||20250101|20251231|||1^Subscriber^HL70072|DAHLSTROM^Curtis^Arvid|01^Self^HL70063|19880316|2214 E 4th St^^Duluth^MN^55812^US|||1|||YES||||||||||PO1890234567
```

---

## 6. ORM^O01 - Radiology order at Mayo Clinic Rochester

```
MSH|^~\&|EPIC|MAYOCLINIC|RADRIS|MAYOCLINIC|20250407103042||ORM^O01^ORM_O01|MCR20250407103042001|P|2.5.1|||AL|NE
PID|1||E10098234^^^EPIC^MRN~500198234^^^MAYOMPI^MR||BJORNSON^Gladys^Ruth^^^Mrs.||19650430|F||2106-3^White^CDCREC|4510 Civic Center Dr NW^^Rochester^MN^55901^US^L||^PRN^PH^^^507^2894531||eng^English^ISO6392|M^Married^HL70002|||375-20-8146|||N^Non-Hispanic^HL70189
PV1|1|O|RADMAYO^RAD2^A^MAYOCLINIC||||6174028395^Thorsgaard^Peter^E^^MD^^^NPI||RAD^Radiology^MAYOSERV|||R^Referral^HL70007|||||V10098765^^^MAYOENC^VN|||||||||||||||||||||||||20250407103000
ORC|NW|ORD501234^EPIC|RAD801234^RADRIS||SC||^^^20250407110000^^R||20250407103042|DSWANBERG^Swanberg^Doris^L^^RT|||20250407103042||MAYOCLINIC|^PRN^PH^^^507^2841234||MAYO CLINIC ROCHESTER
OBR|1|ORD501234^EPIC|RAD801234^RADRIS|71260^CT Chest with Contrast^CPT||||||||||||6174028395^Thorsgaard^Peter^E^^MD^^^NPI||||||20250407110000|||NI^No Information^HL70507|||^^^20250407110000^^R
DG1|1||R91.8^Other nonspecific abnormal finding of lung field^I10||20250407|W^Working^HL70052
```

---

## 7. ORM^O01 - Laboratory order at Allina Health Abbott Northwestern

```
MSH|^~\&|EPIC|ALLINAANW|LABLIS|ALLINAANW|20250519084215||ORM^O01^ORM_O01|ANW20250519084215001|P|2.5.1|||AL|NE
PID|1||E20345678^^^EPIC^MRN~700345678^^^ALLINAMPI^MR||WARSAME^Dalmar^Abshir^^^Mr.||19790622|M||2054-5^Black or African American^CDCREC|5428 Lyndale Ave S^^Minneapolis^MN^55419^US^L||^PRN^PH^^^612^8234567||som^Somali^ISO6392|M^Married^HL70002|||704-31-5928|||N^Non-Hispanic^HL70189
PV1|1|I|7MEDSURG^7208^A^ALLINAANW^^^^7MEDSURG||||2960718345^Harstad^Judith^K^^MD^^^NPI||MED^Medicine^ALLINASERV|||R^Referral^HL70007|||||V20098765^^^ALLINAENC^VN|||||||||||||||||||||||||20250518153000
ORC|NW|ORD602345^EPIC|LAB902345^LABLIS||SC||^^^20250519090000^^R||20250519084215|TOSMAN^Osman^Tahliil^A^^MLT|||20250519084215||ALLINAANW|^PRN^PH^^^612^8636000||ALLINA HEALTH ABBOTT NORTHWESTERN
OBR|1|ORD602345^EPIC|LAB902345^LABLIS|80053^Comprehensive Metabolic Panel^CPT||||||||||||2960718345^Harstad^Judith^K^^MD^^^NPI||||||20250519090000|||NI^No Information^HL70507|||^^^20250519090000^^R
OBR|2|ORD602345^EPIC|LAB902346^LABLIS|85025^CBC with Differential^CPT||||||||||||2960718345^Harstad^Judith^K^^MD^^^NPI||||||20250519090000|||NI^No Information^HL70507|||^^^20250519090000^^R
```

---

## 8. ORU^R01 - Lab result from Mayo Clinic Rochester

```
MSH|^~\&|EPIC|MAYOCLINIC|LABSYS|MAYOCLINIC|20250408141230||ORU^R01^ORU_R01|MCR20250408141230001|P|2.5.1|||AL|NE
PID|1||E10098234^^^EPIC^MRN~500198234^^^MAYOMPI^MR||BJORNSON^Gladys^Ruth^^^Mrs.||19650430|F||2106-3^White^CDCREC|4510 Civic Center Dr NW^^Rochester^MN^55901^US^L||^PRN^PH^^^507^2894531||eng^English^ISO6392|M^Married^HL70002|||375-20-8146|||N^Non-Hispanic^HL70189
PV1|1|O|RADMAYO^RAD2^A^MAYOCLINIC||||6174028395^Thorsgaard^Peter^E^^MD^^^NPI||RAD^Radiology^MAYOSERV|||R^Referral^HL70007|||||V10098765^^^MAYOENC^VN|||||||||||||||||||||||||20250407103000
ORC|RE|ORD501234^EPIC|RAD801234^RADRIS||CM||^^^20250408141200^^R||20250408141230|RADTECH^Technologist^Radiology^^^RT|||20250408141230||MAYOCLINIC
OBR|1|ORD501234^EPIC|RAD801234^RADRIS|71260^CT Chest with Contrast^CPT|||20250407112000||||||||6174028395^Thorsgaard^Peter^E^^MD^^^NPI|||||20250408141200||CT^CT Scan^HL70074|F||^^^20250407110000^^R||||||||5285039164^Ostlund^Freya^M^^MD^^^NPI
OBX|1|TX|71260^CT Chest with Contrast^CPT||FINDINGS: CT chest with IV contrast performed. The lungs are clear bilaterally. No pulmonary nodules or masses identified. No pleural effusion. Mediastinal structures are normal. Heart size is normal. No pericardial effusion. No pathologic lymphadenopathy. Visualized upper abdominal organs are unremarkable.~IMPRESSION: Normal CT chest with contrast. No acute cardiopulmonary process.||||||F|||20250408140000||5285039164^Ostlund^Freya^M^^MD^^^NPI
```

---

## 9. ORU^R01 - Radiology result with embedded PDF report at Allina Health

```
MSH|^~\&|EPIC|ALLINAANW|PACS|ALLINAANW|20250610093045||ORU^R01^ORU_R01|ANW20250610093045001|P|2.5.1|||AL|NE
PID|1||E20456789^^^EPIC^MRN~700456789^^^ALLINAMPI^MR||ENGSTROM^Linnea^Dagny^^^Mrs.||19720815|F||2106-3^White^CDCREC|1245 Nicollet Mall^^Minneapolis^MN^55403^US^L||^PRN^PH^^^612^3395781||eng^English^ISO6392|M^Married^HL70002|||602-43-1897|||N^Non-Hispanic^HL70189
PV1|1|O|RADANW^XRAY1^A^ALLINAANW^^^^RADANW||||8396150274^Kiefer^Roland^J^^MD^^^NPI||RAD^Radiology^ALLINASERV|||||||||V20112345^^^ALLINAENC^VN|||||||||||||||||||||||||20250610090000
ORC|RE|ORD703456^EPIC|RAD903456^PACS||CM||^^^20250610093000^^R||20250610093045|RADTECH^Technologist^Radiology^^^RT|||20250610093045||ALLINAANW
OBR|1|ORD703456^EPIC|RAD903456^PACS|71046^Chest X-Ray 2 Views^CPT|||20250610091500||||||||8396150274^Kiefer^Roland^J^^MD^^^NPI|||||20250610093000||XR^X-Ray^HL70074|F||^^^20250610090000^^R||||||||9407261583^Bauer^Christine^L^^MD^^^NPI
OBX|1|TX|71046^Chest X-Ray 2 Views^CPT|1|FINDINGS: PA and lateral chest radiographs obtained. Heart size is at the upper limits of normal. Lungs are clear. No focal consolidation, pleural effusion, or pneumothorax. Bony structures are intact.~IMPRESSION: Borderline cardiomegaly. No acute pulmonary disease.||||||F|||20250610092800||9407261583^Bauer^Christine^L^^MD^^^NPI
OBX|2|ED|71046^Chest X-Ray Report PDF^CPT|2|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKENoZXN0IFgtUmF5IFJlcG9ydCkKL0F1dGhvciAoRHIuIERpYW5lIEVyaWNrc29uKQovQ3JlYXRvciAoRXBpYyBTeXN0ZW1zIFJhZGlvbG9neSBNb2R1bGUpCi9Qcm9kdWNlciAoRXBpYyBQcmludCBTZXJ2aWNlKQovQ3JlYXRpb25EYXRlIChEOjIwMjUwNjEwMDkzMDAwKQo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvUGFnZQovUGFyZW50IDMgMCBSCi9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCi9Db250ZW50cyA0IDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSAyMCAwIFIKPj4KPj4KPj4KZW5kb2JqCg==||||||F|||20250610093000||9407261583^Bauer^Christine^L^^MD^^^NPI
```

---

## 10. ORU^R01 - Cardiology result with embedded PDF at Mayo Clinic

```
MSH|^~\&|EPIC|MAYOCLINIC|CARDIS|MAYOCLINIC|20250715102215||ORU^R01^ORU_R01|MCR20250715102215001|P|2.5.1|||AL|NE
PID|1||E10145678^^^EPIC^MRN~500245678^^^MAYOMPI^MR||SWANBERG^Harold^Otto^^^Mr.||19550920|M||2106-3^White^CDCREC|2801 Valleyhigh Dr NW^^Rochester^MN^55901^US^L||^PRN^PH^^^507^2821934||eng^English^ISO6392|M^Married^HL70002|||460-53-7812|||N^Non-Hispanic^HL70189
PV1|1|I|3CARDIO^3105^A^MAYOCLINIC^^^^3CARDIO||||1538204769^Stavros^Jonathan^P^^MD^^^NPI|2649315870^Moua^Chue^T^^MD^^^NPI|CAR^Cardiology^MAYOSERV|||R^Referral^HL70007|||||V10134567^^^MAYOENC^VN|||||||||||||||||||||||||20250714080000
ORC|RE|ORD504567^EPIC|CARD804567^CARDIS||CM||^^^20250715102200^^R||20250715102215|CARDTECH^Technologist^Cardiac^^^RT|||20250715102215||MAYOCLINIC
OBR|1|ORD504567^EPIC|CARD804567^CARDIS|93306^Echocardiogram Complete^CPT|||20250715091000||||||||1538204769^Stavros^Jonathan^P^^MD^^^NPI|||||20250715102200||US^Ultrasound^HL70074|F||^^^20250715090000^^R||||||||1538204769^Stavros^Jonathan^P^^MD^^^NPI
OBX|1|NM|8867-4^Heart rate^LN|1|72|/min^beats per minute^UCUM|60-100||||F|||20250715100000||1538204769^Stavros^Jonathan^P^^MD^^^NPI
OBX|2|NM|10230-1^Left ventricular ejection fraction^LN|2|55|%^percent^UCUM|55-70||||F|||20250715100000||1538204769^Stavros^Jonathan^P^^MD^^^NPI
OBX|3|TX|93306^Echocardiogram Interpretation^CPT|3|FINDINGS: Transthoracic echocardiogram performed. Left ventricular cavity size is normal with preserved systolic function, estimated LVEF 55%. No regional wall motion abnormalities. Right ventricular size and function are normal. Valvular function is normal without significant stenosis or regurgitation. No pericardial effusion.~IMPRESSION: Normal transthoracic echocardiogram.||||||F|||20250715101500||1538204769^Stavros^Jonathan^P^^MD^^^NPI
OBX|4|ED|93306^Echocardiogram Report PDF^CPT|4|^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKEVjaG9jYXJkaW9ncmFtIFJlcG9ydCkKL0F1dGhvciAoRHIuIEpvbmF0aGFuIEVpZGUpCi9DcmVhdG9yIChFcGljIENhcmRpb2xvZ3kgTW9kdWxlKQovUHJvZHVjZXIgKEVwaWMgUHJpbnQgU2VydmljZSkKL0NyZWF0aW9uRGF0ZSAoRDoyMDI1MDcxNTEwMjIwMCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAzIDAgUgovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgMjAgMCBSCj4+Cj4+Cj4+CmVuZG9iago=||||||F|||20250715102000||1538204769^Stavros^Jonathan^P^^MD^^^NPI
```

---

## 11. SIU^S12 - New appointment at Fairview Clinics Plymouth

```
MSH|^~\&|EPIC|FVWPLYM|SCHED|FVWPLYM|20250623154530||SIU^S12^SIU_S12|FPL20250623154530001|P|2.5.1|||AL|NE
SCH|APT90123456^EPIC|APT90123456^EPIC|||ROUTINE^Routine^HL70276|FOLLOWUP^Follow-Up Visit^EPICAPPT|NORMAL^Normal^HL70277|30|MIN^Minutes^ISO+|^^^20250710093000^20250710100000|SYSTEM^EPIC^SYSTEM|^PRN^PH^^^763^5874321||SYSTEM^EPIC^SYSTEM|^PRN^PH^^^763^5874321|FVWPLYM|APT90123456|BOOKED^Booked^HL70278
PID|1||E30456123^^^EPIC^MRN~800456123^^^FVWMPI^MR||VANG^Teng^Pao^^^Mr.||19910507|M||2028-9^Asian^CDCREC|3845 Vicksburg Ln^^Plymouth^MN^55447^US^L||^PRN^PH^^^763^5551234~^NET^Internet^t.vang91@email.com||hmn^Hmong^ISO6392|S^Single^HL70002|||623-45-1987|||N^Non-Hispanic^HL70189
PV1|1|O|FVWPLYMCLIN^VIST1^A^FVWPLYM^^^^FVWPLYMCLIN||||3071425986^Engel^Patricia^R^^MD^^^NPI||PCP^Primary Care^FVWSERV|||||||||V30123456^^^FVWENC^VN|||||||||||||||||||||||||20250710093000
RGS|1|A
AIS|1|A|99214^Office Visit Level 4^CPT|20250710093000|||30|MIN^Minutes^ISO+||BOOKED^Booked^HL70278
AIG|1|A|3071425986^Engel^Patricia^R^^MD^^^NPI|FVWPLYM^FVWPLYMCLIN^VIST1
AIL|1|A|FVWPLYMCLIN^VIST1^A^FVWPLYM||||20250710093000|||30|MIN^Minutes^ISO+||BOOKED^Booked^HL70278
```

---

## 12. SIU^S12 - Specialty appointment at HealthPartners

```
MSH|^~\&|EPIC|HPSPECIALTY|SCHED|HPSPECIALTY|20250801112300||SIU^S12^SIU_S12|HPS20250801112300001|P|2.5.1|||AL|NE
SCH|APT91234567^EPIC|APT91234567^EPIC|||ROUTINE^Routine^HL70276|CONSULT^Consultation^EPICAPPT|NORMAL^Normal^HL70277|45|MIN^Minutes^ISO+|^^^20250820140000^20250820144500|SYSTEM^EPIC^SYSTEM|^PRN^PH^^^952^8835000||SYSTEM^EPIC^SYSTEM|^PRN^PH^^^952^8835000|HPSPECIALTY|APT91234567|BOOKED^Booked^HL70278
PID|1||E40567890^^^EPIC^MRN~900567890^^^HPMPI^MR||LINDQUIST^Janet^Elaine^^^Mrs.||19830219|F||2106-3^White^CDCREC|9021 Cedar Lake Rd^^St. Louis Park^MN^55426^US^L||^PRN^PH^^^952^5559012~^NET^Internet^j.lindquist83@email.com||eng^English^ISO6392|M^Married^HL70002|||752-86-3014|||N^Non-Hispanic^HL70189
PV1|1|O|HPDERM^DERM1^A^HPSPECIALTY^^^^HPDERM||||4182536097^Ronning^Andrea^A^^MD^^^NPI||DER^Dermatology^HPSERV|||||||||V40234567^^^HPENC^VN|||||||||||||||||||||||||20250820140000
RGS|1|A
AIS|1|A|99243^Outpatient Consultation Level 3^CPT|20250820140000|||45|MIN^Minutes^ISO+||BOOKED^Booked^HL70278
AIG|1|A|4182536097^Ronning^Andrea^A^^MD^^^NPI|HPSPECIALTY^HPDERM^DERM1
AIL|1|A|HPDERM^DERM1^A^HPSPECIALTY||||20250820140000|||45|MIN^Minutes^ISO+||BOOKED^Booked^HL70278
```

---

## 13. MDM^T02 - Document notification with content at Mayo Clinic

```
MSH|^~\&|EPIC|MAYOCLINIC|DOCSYS|MAYOCLINIC|20250903085430||MDM^T02^MDM_T02|MCR20250903085430001|P|2.5.1|||AL|NE
EVN|T02|20250903085400
PID|1||E10256789^^^EPIC^MRN~500356789^^^MAYOMPI^MR||THORSGAARD^Margit^Astrid^^^Mrs.||19600312|F||2106-3^White^CDCREC|1520 2nd St SW^^Rochester^MN^55902^US^L||^PRN^PH^^^507^2853219||eng^English^ISO6392|M^Married^HL70002|||291-38-6704|||N^Non-Hispanic^HL70189
PV1|1|I|5ONCO^5201^A^MAYOCLINIC^^^^5ONCO||||7850291436^Halvorson^Scott^D^^MD^^^NPI||ONC^Oncology^MAYOSERV|||R^Referral^HL70007|||||V10245678^^^MAYOENC^VN|||||||||||||||||||||||||20250901100000
TXA|1|HP^History and Physical^EPICDOC|TX^Text^HL70191||20250903084500|||||7850291436^Halvorson^Scott^D^^MD^^^NPI|DOC501234^EPIC||||||AU^Authenticated^HL70271||||||
OBX|1|TX|HP^History and Physical^EPICDOC|1|CHIEF COMPLAINT: 60-year-old female presents for evaluation of newly diagnosed right breast mass.~HISTORY OF PRESENT ILLNESS: Patient noted a palpable mass in the right breast approximately 3 weeks ago. Mammography and ultrasound at outside facility demonstrated a 2.1 cm irregular mass at 10 o'clock position. Core needle biopsy performed on 8/28/2025 revealed invasive ductal carcinoma, grade 2, ER+/PR+, HER2 negative.~PAST MEDICAL HISTORY: Hypertension, hypothyroidism, osteopenia.~MEDICATIONS: Lisinopril 10mg daily, levothyroxine 75mcg daily, calcium/vitamin D supplement.~PHYSICAL EXAMINATION: Right breast with palpable 2cm firm mass at 10 o'clock, 4cm from nipple. No skin changes or nipple discharge. Left breast unremarkable. No palpable axillary lymphadenopathy bilaterally.~ASSESSMENT AND PLAN: Stage IIA invasive ductal carcinoma of right breast. Recommend surgical oncology consultation for lumpectomy versus mastectomy. Refer to radiation oncology and medical oncology for multidisciplinary planning.||||||F|||20250903085000||7850291436^Halvorson^Scott^D^^MD^^^NPI
```

---

## 14. ADT^A01 - Inpatient admission at Hennepin Healthcare HCMC

```
MSH|^~\&|EPIC|HCMC|ADMREG|HCMC|20250110072045||ADT^A01^ADT_A01|HCMC20250110072045001|P|2.5.1|||AL|NE
EVN|A01|20250110072000|||ANUR^Nur^Asli^P^^RN|20250110065500
PID|1||E60123456^^^EPIC^MRN~110234567^^^HCMCMPI^MR||XIONG^Tou^Pao^^^Mr.||19750814|M||2028-9^Asian^CDCREC|1814 Central Ave NE^^Minneapolis^MN^55418^US^L||^PRN^PH^^^612^7819234||hmn^Hmong^ISO6392|M^Married^HL70002|||839-07-4261|||N^Non-Hispanic^HL70189
PD1|||HENNEPIN HEALTHCARE^^40001|6928041573^Lor^Pheng^K^^MD^^^NPI
NK1|1|XIONG^Mai^Yer|SPO^Spouse^HL70063|1814 Central Ave NE^^Minneapolis^MN^55418^US|^PRN^PH^^^612^7819235||EC^Emergency Contact^HL70131
NK1|2|XIONG^Chue^||4209 Humboldt Ave N^^Minneapolis^MN^55412^US|^PRN^PH^^^612^5224567||CP^Contact Person^HL70131
PV1|1|E|EDHCMC^ED05^A^HCMC^^^^EDHCMC||||6928041573^Lor^Pheng^K^^MD^^^NPI|7039152684^Isse^Khadra^S^^MD^^^NPI|EM^Emergency Medicine^HCMCSERV|||E^Emergency^HL70007|||||V60012345^^^HCMCENC^VN|||||||||||||||||||||||||20250110072000
PV2|||^Motor vehicle accident^V43.92
DG1|1||S72.001A^Fracture of unspecified part of neck of right femur, initial encounter^I10||20250110|A^Admitting^HL70052
IN1|1|MDMN001^Medical Assistance (Medicaid) MN^^MAMT|99001|MINNESOTA MEDICAL ASSISTANCE|PO Box 64838^^St. Paul^MN^55164^US|^PRN^PH^^^651^4312700||||||||||||||XIONG^Tou^Pao|01^Self^HL70063|19750814|1814 Central Ave NE^^Minneapolis^MN^55418^US|||1|||YES||||||||||MA789012345
```

---

## 15. ORM^O01 - Medication order at Fairview University of Minnesota Medical Center

```
MSH|^~\&|EPIC|FVWUMMC|PHARM|FVWUMMC|20250228163512||ORM^O01^ORM_O01|FUMMC20250228163512001|P|2.5.1|||AL|NE
PID|1||E30567890^^^EPIC^MRN~800567890^^^FVWMPI^MR||HER^Mailee^Song^^^Ms.||19980101|F||2028-9^Asian^CDCREC|520 Delaware St SE^^Minneapolis^MN^55455^US^L||^PRN^PH^^^612^6245678||hmn^Hmong^ISO6392|S^Single^HL70002|||946-08-2713|||N^Non-Hispanic^HL70189
PV1|1|I|8MEDSURG^8312^A^FVWUMMC^^^^8MEDSURG||||4053971826^Swanberg^Eric^L^^MD^^^NPI||MED^Medicine^FVWSERV|||R^Referral^HL70007|||||V30234567^^^FVWENC^VN|||||||||||||||||||||||||20250227120000
ORC|NW|ORD804567^EPIC||RXGRP301234|||^^^20250228170000^^R||20250228163512|PHARMD^Pharmacist^Clinical^^^RPh|||20250228163512||FVWUMMC|^PRN^PH^^^612^2736000||FAIRVIEW UNIVERSITY OF MN MEDICAL CENTER
RXO|204871^Vancomycin^EPIC||1250|mg^milligram^ISO+||||G^Give^HL70292||0|||4053971826^Swanberg^Eric^L^^MD^^^NPI
RXR|IV^Intravenous^HL70162|LA^Left Arm^HL70163
RXE|^^^20250228170000^^R^20250228230000|204871^Vancomycin^EPIC||1250|mg^milligram^ISO+|EA^Each^HL70292|||||||||||||||||IV PIGGYBACK^IV Piggyback^EPICADMIN|LA^Left Arm^HL70163
```

---

## 16. ADT^A04 - Registration at Mankato Clinic

```
MSH|^~\&|EPIC|MCHS_MANKATO|REGUPD|MCHS_MANKATO|20250814091230||ADT^A04^ADT_A01|MNK20250814091230001|P|2.5.1|||AL|NE
EVN|A04|20250814091200|||PHANSEN^Hansen^Priscilla^M^^REG|20250814090500
PID|1||E70234567^^^EPIC^MRN~200345678^^^MCHSMPI^MR||ABDI^Omar^Mahad^^^Mr.||19450627|M||2054-5^Black or African American^CDCREC|201 N Broad St^^Mankato^MN^56001^US^L||^PRN^PH^^^507^3872345||som^Somali^ISO6392|M^Married^HL70002|||158-40-6723|||N^Non-Hispanic^HL70189
PD1|||MAYO CLINIC HEALTH SYSTEM MANKATO^^50001|8160247935^Engstrom^Sandra^A^^MD^^^NPI
NK1|1|ABDI^Halima^Sahra|SPO^Spouse^HL70063|201 N Broad St^^Mankato^MN^56001^US|^PRN^PH^^^507^3872346||EC^Emergency Contact^HL70131
PV1|1|O|MNKCLIN^EXAM4^A^MCHS_MANKATO^^^^MNKCLIN||||8160247935^Engstrom^Sandra^A^^MD^^^NPI||PCP^Primary Care^MCHSSERV|||R^Referral^HL70007|||||V70012345^^^MCHSENC^VN|||||||||||||||||||||||||20250814091200
IN1|1|MEDCR001^Medicare^^CMS|00001|MEDICARE|PO Box 1270^^Portland^ME^04104^US|^PRN^PH^^^800^6334227|||||||||20100627|||1^Primary^HL70072|ABDI^Omar^Mahad|01^Self^HL70063|19450627|201 N Broad St^^Mankato^MN^56001^US|||1|||YES||||||||||1EG4TE5MK72
IN1|2|MEDCR002^Medicare Supplement (Medigap)^^AARP|00002|AARP MEDICARE SUPPLEMENT|PO Box 740819^^Atlanta^GA^30374^US|^PRN^PH^^^800^5237773|||||||||20110101|||2^Secondary^HL70072|ABDI^Omar^Mahad|01^Self^HL70063|19450627|201 N Broad St^^Mankato^MN^56001^US|||2|||YES||||||||||AARP901234567
```

---

## 17. ORU^R01 - Microbiology result at Essentia Health Duluth

```
MSH|^~\&|EPIC|ESSENTIADL|MICROLAB|ESSENTIADL|20250522134500||ORU^R01^ORU_R01|EDL20250522134500001|P|2.5.1|||AL|NE
PID|1||E50534567^^^EPIC^MRN~100634567^^^ESSMPI^MR||ELLINGSON^Donna^Astrid^^^Mrs.||19680901|F||2106-3^White^CDCREC|1028 E 2nd St^^Duluth^MN^55805^US^L||^PRN^PH^^^218^7281456||eng^English^ISO6392|M^Married^HL70002|||504-72-8163|||N^Non-Hispanic^HL70189
PV1|1|I|4MEDSURG^4118^A^ESSENTIADL^^^^4MEDSURG||||2065138947^Tveit^Henrik^S^^MD^^^NPI||MED^Medicine^ESSSERV|||R^Referral^HL70007|||||V50134567^^^ESSENC^VN|||||||||||||||||||||||||20250520150000
ORC|RE|ORD905678^EPIC|MICRO105678^MICROLAB||CM||^^^20250522134400^^R||20250522134500|MICROTECH^Technologist^Micro^^^MT|||20250522134500||ESSENTIADL
OBR|1|ORD905678^EPIC|MICRO105678^MICROLAB|87081^Culture, Urine^CPT|||20250520160000||||||||2065138947^Tveit^Henrik^S^^MD^^^NPI|||||20250522134400||MB^Microbiology^HL70074|F||^^^20250520160000^^R
OBX|1|CE|600-7^Bacteria identified in Urine^LN|1|112283005^Escherichia coli^SCT||||||F|||20250522130000||4176283950^Ronning^Craig^M^^MT^^^NPI
OBX|2|NM|51480-2^Colony count^LN|2|>100000|CFU/mL^colony forming units per milliliter^UCUM|||||F|||20250522130000||4176283950^Ronning^Craig^M^^MT^^^NPI
OBX|3|CE|18769-0^Ampicillin susceptibility^LN|3|R^Resistant^HL70078||||||F|||20250522133000||4176283950^Ronning^Craig^M^^MT^^^NPI
OBX|4|CE|18862-3^Ciprofloxacin susceptibility^LN|4|S^Susceptible^HL70078||||||F|||20250522133000||4176283950^Ronning^Craig^M^^MT^^^NPI
OBX|5|CE|18964-7^Nitrofurantoin susceptibility^LN|5|S^Susceptible^HL70078||||||F|||20250522133000||4176283950^Ronning^Craig^M^^MT^^^NPI
OBX|6|CE|18993-6^Trimethoprim-sulfamethoxazole susceptibility^LN|6|S^Susceptible^HL70078||||||F|||20250522133000||4176283950^Ronning^Craig^M^^MT^^^NPI
```

---

## 18. ADT^A08 - Insurance update at HealthPartners Bloomington

```
MSH|^~\&|EPIC|HPBLOOM|INSURUPD|HPBLOOM|20250401100045||ADT^A08^ADT_A01|HPB20250401100045001|P|2.5.1|||AL|NE
EVN|A08|20250401100000|||LKHANG^Khang^Linda^K^^REG|20250401095500
PID|1||E40678901^^^EPIC^MRN~900678901^^^HPMPI^MR||SAMATAR^Asha^Nimco^^^Mrs.||19790305|F||2054-5^Black or African American^CDCREC|6801 Normandale Rd^^Bloomington^MN^55437^US^L||^PRN^PH^^^952^8831234~^NET^Internet^a.samatar79@email.com||som^Somali^ISO6392|M^Married^HL70002|||937-15-4068|||N^Non-Hispanic^HL70189
PV1|1|O|HPBLMCLIN^VIST2^A^HPBLOOM^^^^HPBLMCLIN||||5287340916^Braun^Lawrence^T^^MD^^^NPI||PCP^Primary Care^HPSERV|||||||||V40345678^^^HPENC^VN|||||||||||||||||||||||||20250401100000
IN1|1|HPMN001^HealthPartners MN^^HEALTHP|66201|HEALTHPARTNERS|PO Box 1309^^Minneapolis^MN^55440^US|^PRN^PH^^^952^8831000|GRP77301||3M COMPANY|||||20250101|20251231|||1^Subscriber^HL70072|SAMATAR^Guled^Abdirahman|04^Spouse^HL70063|19770812|6801 Normandale Rd^^Bloomington^MN^55437^US|||1|||YES||||||||||HP2901234567
```

---

## 19. ADT^A01 - Neonatal admission at Children's Minnesota Minneapolis

```
MSH|^~\&|EPIC|CHILDMNMPLS|NICU|CHILDMNMPLS|20250125031545||ADT^A01^ADT_A01|CMM20250125031545001|P|2.5.1|||AL|NE
EVN|A01|20250125031500|||STHAO^Thao^Sandy^E^^RN|20250125030000
PID|1||E80012345^^^EPIC^MRN~300123456^^^CHILDMPI^MR||YANG^Baby Girl^^^^^Baby||20250125|F||2028-9^Asian^CDCREC|4215 Blaisdell Ave^^Minneapolis^MN^55409^US^L||^PRN^PH^^^612^8254567||hmn^Hmong^ISO6392||||||||||||||||||N
NK1|1|YANG^Pahoua^Lia|MTH^Mother^HL70063|4215 Blaisdell Ave^^Minneapolis^MN^55409^US|^PRN^PH^^^612^8254567||EC^Emergency Contact^HL70131
NK1|2|YANG^Xeng^Tou|FTH^Father^HL70063|4215 Blaisdell Ave^^Minneapolis^MN^55409^US|^PRN^PH^^^612^8254568||EC^Emergency Contact^HL70131
PV1|1|I|NICU^NICU03^A^CHILDMNMPLS^^^^NICU||||3960517284^Vue^Koua^M^^MD^^^NPI|4071628395^Farah^Saida^R^^MD^^^NPI|NEO^Neonatology^CHILDSERV|||B^Birth^HL70007|||||V80012345^^^CHILDENC^VN|||||||||||||||||||||||||20250125031500
DG1|1||P07.18^Other low birth weight newborn, 2000-2499 grams^I10||20250125|A^Admitting^HL70052
DG1|2||P22.0^Respiratory distress syndrome of newborn^I10||20250125|A^Admitting^HL70052
```

---

## 20. ADT^A03 - Discharge from Essentia Health Virginia

```
MSH|^~\&|EPIC|ESSENTIAVIRG|BILLING|ESSENTIAVIRG|20250917151230||ADT^A03^ADT_A03|EVR20250917151230001|P|2.5.1|||AL|NE
EVN|A03|20250917151200|||KVUE^Vue^Kao^J^^RN|20250917150000
PID|1||E50645678^^^EPIC^MRN~100745678^^^ESSMPI^MR||HIRSI^Abdikarim^Maxamed^^^Mr.||19580320|M||2054-5^Black or African American^CDCREC|507 Chestnut St^^Virginia^MN^55792^US^L||^PRN^PH^^^218^7413456||som^Somali^ISO6392|M^Married^HL70002|||631-85-0247|||N^Non-Hispanic^HL70189
PV1|1|I|3MEDSURG^3204^A^ESSENTIAVIRG^^^^3MEDSURG||||6293840517^Ostlund^Craig^J^^MD^^^NPI||MED^Medicine^ESSSERV|||E^Emergency^HL70007|||||V50245678^^^ESSENC^VN||DI^Discharged to Home^HL70112||||||||||||||||||||||||20250915082000|20250917151200
DG1|1||J18.9^Pneumonia, unspecified organism^I10||20250915|A^Admitting^HL70052
DG1|2||J96.00^Acute respiratory failure, unspecified^I10||20250915|A^Admitting^HL70052
DG1|3||E11.9^Type 2 diabetes mellitus without complications^I10||20250915|W^Working^HL70052
PR1|1||0BH17EZ^Insertion of Endotracheal Airway into Trachea, Via Natural or Artificial Opening^ICD10PCS|Endotracheal intubation|20250915093000|A^Anesthesia^HL70230||||||6293840517^Ostlund^Craig^J^^MD^^^NPI
```
