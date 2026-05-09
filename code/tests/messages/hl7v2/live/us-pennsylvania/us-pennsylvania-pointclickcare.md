# PointClickCare - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Admission to skilled nursing facility in Philadelphia

```
MSH|^~\&|PCC|STLUKE_QUAKERTOWN_SNF|RECEIVING|STATEHI|20260327081500||ADT^A01^ADT_A01|PCC20260327081500001|P|2.5.1|||AL|NE
EVN|A01|20260327081000|||ADMCLERK
PID|1||MRN100234^^^SLQS^MR~518-44-7263^^^SSA^SS||Wozniak^Irena^Jadwiga^^Mrs.^||19380412|F||2106-3^White^CDCREC|2847 Memphis St^^Philadelphia^PA^19134^US^H||^PRN^PH^^^215^5539481||POL|W|CAT|ACCT700123^^^SLQS^AN|518-44-7263|||N||||20260327
PD1|||St. Luke's Quakertown Skilled Nursing^^^SLQS||||||||N
NK1|1|Wozniak^Marek^T^^Mr.^||1024 Belgrade St^^Philadelphia^PA^19125^US|^PRN^PH^^^215^5537102||SON^Son^HL70063
NK1|2|Kaczmarek^Halina^R^^Mrs.^||3310 Cedar Ave^^Philadelphia^PA^19143^US|^PRN^PH^^^267^5534478||DAU^Daughter^HL70063
PV1|1|I|2NORTH^214^A^SLQS^^^^2NORTH|||1938274650^Lombardi^Vincent^G^^^MD^^^NPI|2847361905^Tran^Bao^H^^^DO^^^NPI||SNF||||7|||1938274650^Lombardi^Vincent^G^^^MD^^^NPI|IN||MCARE|||||||||||||||AI|||20260327081000
PV2|||^Left hip fracture post ORIF, rehabilitation||||||20260327|||||||||||||N
DG1|1|I10|S72.002A^Fracture of unspecified part of neck of left femur, initial encounter^ICD10|||A
DG1|2|I10|Z96.642^Presence of left artificial hip joint^ICD10|||S
DG1|3|I10|E11.9^Type 2 diabetes mellitus without complications^ICD10|||S
AL1|1|DA|7980^Sulfonamide^RxNorm|SV|Rash and hives|20050823
IN1|1|001|MCARE001^Medicare Part A|Centers for Medicare^^Baltimore^MD^21244|^PRN^PH^^^800^6332273|||||||||Wozniak^Irena^Jadwiga|SEL|19380412|2847 Memphis St^^Philadelphia^PA^19134||1|||||||||||||HIC518447263A||||||F
IN1|2|002|AETNA01^Aetna Medicare Advantage|Aetna Insurance^^Hartford^CT^06156|^PRN^PH^^^800^8721862|||||||||Wozniak^Irena^Jadwiga|SEL|19380412|2847 Memphis St^^Philadelphia^PA^19134||2|||||||||||||POL883241||||||F
GT1|1||Wozniak^Irena^Jadwiga^^Mrs.^|2847 Memphis St^^Philadelphia^PA^19134^US|^PRN^PH^^^215^5539481||19380412|F||SEL|518-44-7263
```

---

## 2. ADT^A02 - Patient transfer between units at Pittsburgh SNF

```
MSH|^~\&|POINTCLICKCARE|UPMC_SENIORCARE_HC|RECEIVING|EXTAPP|20260401101230||ADT^A02^ADT_A02|PCC20260401101230002|P|2.5.1|||AL|NE
EVN|A02|20260401101000|||NURSEMGR
PID|1||MRN200456^^^USCH^MR||Jackson^Terrence^Dwayne^^Mr.^||19450719|M||2054-5^Black or African American^CDCREC|4718 Penn Ave^^Pittsburgh^PA^15224^US^H||^PRN^PH^^^412^5536847||ENG|W|BAP|ACCT800234^^^USCH^AN|247-18-9903|||N||||20260315
PV1|1|I|REHAB^108^A^USCH^^^^REHAB|||3057184926^Okonkwo^Chinedu^E^^^MD^^^NPI||||SNF||||7|||3057184926^Okonkwo^Chinedu^E^^^MD^^^NPI|IN||MCARE|||||||||||||||AI|||20260315093000
PV1|2|I|LTCARE^305^B^USCH^^^^LTCARE|||3057184926^Okonkwo^Chinedu^E^^^MD^^^NPI||||SNF||||||||IN||MCARE|||||||||||||||AI|||20260401101000
DG1|1|I10|I63.9^Cerebral infarction, unspecified^ICD10|||A
DG1|2|I10|G81.94^Hemiplegia, unspecified affecting left nondominant side^ICD10|||S
```

---

## 3. ADT^A03 - Discharge from Scranton rehab center to home

```
MSH|^~\&|PCC_EHR|ALLIED_SERVICES_REHAB|RECEIVING|HIE_PA|20260408143022||ADT^A03^ADT_A03|PCC20260408143022003|P|2.5.1|||AL|NE
EVN|A03|20260408142500|||DCPLANNER
PID|1||MRN300789^^^ASRH^MR||Gallagher^Siobhan^Marie^^Mrs.^||19410925|F||2106-3^White^CDCREC|1402 Quincy Ave^^Scranton^PA^18510^US^H||^PRN^PH^^^570^5531294||ENG|W|CAT|ACCT900345^^^ASRH^AN|382-61-4507|||N||||20260301
PV1|1|I|REHAB^202^A^ASRH^^^^REHAB|||4160283795^Yusuf^Nasir^K^^^MD^^^NPI|5271394806^Santiago^Elena^M^^^DO^^^NPI||SNF||||7|||4160283795^Yusuf^Nasir^K^^^MD^^^NPI|IN||MCARE|||||||||||||||AI|||20260301102000||||||20260408142500
PV2|||^Right total knee arthroplasty, rehabilitation||||||||20260301|||||||20260410|||||N
DG1|1|I10|Z96.651^Presence of right artificial knee joint^ICD10|||A
DG1|2|I10|M17.11^Primary osteoarthritis, right knee^ICD10|||S
DG1|3|I10|I10^Essential (primary) hypertension^ICD10|||S
IN1|1|001|MCARE001^Medicare Part A|Centers for Medicare^^Baltimore^MD^21244|^PRN^PH^^^800^6332273|||||||||Gallagher^Siobhan^Marie|SEL|19410925|1402 Quincy Ave^^Scranton^PA^18510||1|||||||||||||HIC382614507A||||||F
```

---

## 4. ADT^A04 - Outpatient registration for wound care at Allentown facility

```
MSH|^~\&|PCC|LEHIGH_VALLEY_SNF|RECEIVING|EXTAPP|20260410091500||ADT^A04^ADT_A04|PCC20260410091500004|P|2.5.1|||AL|NE
EVN|A04|20260410091200|||CLINREG
PID|1||MRN400123^^^LVSN^MR||Krasinski^Zofia^Helena^^Mrs.^||19350618|F||2106-3^White^CDCREC|1455 W Allen St^^Allentown^PA^18104^US^H||^PRN^PH^^^484^5544812||ENG|W|ORT|ACCT110456^^^LVSN^AN|493-72-8156|||N||||20260410
NK1|1|Krasinski^Andrzej^W^^Mr.^||1455 W Allen St^^Allentown^PA^18104^US|^PRN^PH^^^484^5544813||SON^Son^HL70063
PV1|1|O|WOUND^WC01^1^LVSN^^^^WOUND|||6382940175^Kapoor^Sunita^R^^^MD^^^NPI||||SNF||||7|||6382940175^Kapoor^Sunita^R^^^MD^^^NPI|OP||MCARE
PV2|||^Stage 3 pressure ulcer left heel, wound care evaluation||||||||||||||||||||N
DG1|1|I10|L89.622^Pressure ulcer of left heel, stage 2^ICD10|||A
DG1|2|I10|E11.65^Type 2 diabetes mellitus with hyperglycemia^ICD10|||S
IN1|1|001|MCARE001^Medicare Part B|Centers for Medicare^^Baltimore^MD^21244|^PRN^PH^^^800^6332273|||||||||Krasinski^Zofia^Helena|SEL|19350618|1455 W Allen St^^Allentown^PA^18104||1|||||||||||||HIC493728156B||||||F
```

---

## 5. ADT^A08 - Patient information update at Erie nursing home

```
MSH|^~\&|POINTCLICKCARE|BALL_PAVILION_HC|RECEIVING|PHARMACY|20260412153300||ADT^A08^ADT_A08|PCC20260412153300005|P|2.5.1|||AL|NE
EVN|A08|20260412153000|||MEDRECORDS
PID|1||MRN500234^^^BPHC^MR||Mazurek^Stanislaw^Roman^^Mr.^||19310205|M||2106-3^White^CDCREC|1130 E 38th St^^Erie^PA^16504^US^H||^PRN^PH^^^814^5522934||POL|W|CAT|ACCT120567^^^BPHC^AN|604-83-7291|||N||||20251201
NK1|1|Mazurek^Wanda^F^^Mrs.^||1130 E 38th St^^Erie^PA^16504^US|^PRN^PH^^^814^5522934||SPO^Spouse^HL70063
NK1|2|Mazurek^Adam^P^^Mr.^||520 Peach St Apt 7^^Erie^PA^16501^US|^PRN^PH^^^814^5577410||SON^Son^HL70063
PV1|1|I|LTCARE^118^A^BPHC^^^^LTCARE|||7493061285^Ciccone^Dominic^A^^^DO^^^NPI||||SNF||||7|||7493061285^Ciccone^Dominic^A^^^DO^^^NPI|IN||MCARE
AL1|1|DA|3640^Morphine^RxNorm|SV|Respiratory depression|20100514
AL1|2|DA|723^Aspirin^RxNorm|MI|GI bleeding|19980302
AL1|3|FA|291^Eggs^UNII|MO|Hives|20050101
IN1|1|001|MCARE001^Medicare Part A|Centers for Medicare^^Baltimore^MD^21244|^PRN^PH^^^800^6332273|||||||||Mazurek^Stanislaw^Roman|SEL|19310205|1130 E 38th St^^Erie^PA^16504||1|||||||||||||HIC604837291A||||||M
IN1|2|002|GEIS001^Geisinger Health Plan|Geisinger Insurance^^Danville^PA^17822|^PRN^PH^^^800^4474000|||||||||Mazurek^Stanislaw^Roman|SEL|19310205|1130 E 38th St^^Erie^PA^16504||2|||||||||||||POL772918||||||M
```

---

## 6. ORU^R01 - Basic metabolic panel results for Harrisburg SNF resident

```
MSH|^~\&|PCC|GEISINGER_HBURG_SNF|LABCORP|LAB|20260414074500||ORU^R01^ORU_R01|PCC20260414074500006|P|2.5.1|||AL|NE
PID|1||MRN600345^^^GHSN^MR||McFadden^Loretta^Jean^^Mrs.^||19290817|F||2054-5^Black or African American^CDCREC|4302 Londonderry Rd^^Harrisburg^PA^17109^US^H||^PRN^PH^^^717^5533407||ENG|W|BAP|ACCT130678^^^GHSN^AN|715-84-2360|||N
PV1|1|I|LTCARE^224^A^GHSN^^^^LTCARE|||8504172693^Rao^Vikram^S^^^MD^^^NPI||||SNF||||7|||8504172693^Rao^Vikram^S^^^MD^^^NPI|IN||MCARE
ORC|RE|ORD20260413001|FIL20260414001||CM||||20260413150000|||8504172693^Rao^Vikram^S^^^MD^^^NPI
OBR|1|ORD20260413001|FIL20260414001|80048^Basic Metabolic Panel^CPT4|||20260414063000|||||||||8504172693^Rao^Vikram^S^^^MD^^^NPI||||||20260414074000|||F
OBX|1|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||142|mg/dL|70-100|H|||F|||20260414074000
OBX|2|NM|3094-0^Urea nitrogen [Mass/volume] in Serum or Plasma^LN||28|mg/dL|7-20|H|||F|||20260414074000
OBX|3|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||1.4|mg/dL|0.6-1.2|H|||F|||20260414074000
OBX|4|NM|2951-2^Sodium [Moles/volume] in Serum or Plasma^LN||138|mmol/L|136-145|N|||F|||20260414074000
OBX|5|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN||4.8|mmol/L|3.5-5.1|N|||F|||20260414074000
OBX|6|NM|2075-0^Chloride [Moles/volume] in Serum or Plasma^LN||101|mmol/L|98-106|N|||F|||20260414074000
OBX|7|NM|2028-9^Carbon dioxide, total [Moles/volume] in Serum or Plasma^LN||24|mmol/L|22-29|N|||F|||20260414074000
OBX|8|NM|17861-6^Calcium [Mass/volume] in Serum or Plasma^LN||9.1|mg/dL|8.5-10.5|N|||F|||20260414074000
NTE|1|L|BMP ordered for routine monitoring of renal function and diabetes management.
```

---

## 7. ORU^R01 - Urinalysis with culture results at Reading rehab

```
MSH|^~\&|PCC_EHR|PENN_STATE_REHAB_READING|QUEST|LAB|20260416112000||ORU^R01^ORU_R01|PCC20260416112000007|P|2.5.1|||AL|NE
PID|1||MRN700456^^^PSRR^MR||Fuentes^Marisol^Valentina^^Mrs.^||19430311|F||2106-3^White^CDCREC|925 N 5th St^^Reading^PA^19601^US^H||^PRN^PH^^^610^5538290||SPA|W|CAT|ACCT140789^^^PSRR^AN|821-05-4673|||N
PV1|1|I|REHAB^112^A^PSRR^^^^REHAB|||9615037284^Mehta^Arjun^P^^^MD^^^NPI||||SNF||||7|||9615037284^Mehta^Arjun^P^^^MD^^^NPI|IN||MCARE
ORC|RE|ORD20260415002|FIL20260416002||CM||||20260415100000|||9615037284^Mehta^Arjun^P^^^MD^^^NPI
OBR|1|ORD20260415002|FIL20260416002|81001^Urinalysis, automated with microscopy^CPT4|||20260415093000|||||||||9615037284^Mehta^Arjun^P^^^MD^^^NPI||||||20260416110000|||F
OBX|1|ST|5778-6^Color of Urine^LN||Amber||Yellow|A|||F|||20260416110000
OBX|2|ST|5767-9^Appearance of Urine^LN||Cloudy||Clear|A|||F|||20260416110000
OBX|3|NM|5811-5^Specific gravity of Urine by Test strip^LN||1.028||1.005-1.030|N|||F|||20260416110000
OBX|4|NM|5803-2^pH of Urine by Test strip^LN||6.0||5.0-8.0|N|||F|||20260416110000
OBX|5|ST|5802-4^Nitrite [Presence] in Urine by Test strip^LN||Positive||Negative|A|||F|||20260416110000
OBX|6|NM|5821-4^Leukocytes [#/area] in Urine sediment by Microscopy high power field^LN||50|/HPF|0-5|H|||F|||20260416110000
OBX|7|NM|5769-5^Bacteria [#/area] in Urine sediment by Microscopy high power field^LN||Many|/HPF|None|A|||F|||20260416110000
OBR|2|ORD20260415002|FIL20260416003|87086^Urine Culture^CPT4|||20260415093000|||||||||9615037284^Mehta^Arjun^P^^^MD^^^NPI||||||20260416110000|||F
OBX|8|ST|630-4^Bacteria identified in Urine by Culture^LN||Escherichia coli||||||F|||20260416110000
OBX|9|NM|564-5^Colony count [#/volume] in Urine by Culture^LN||>100000|CFU/mL|<10000|H|||F|||20260416110000
OBX|10|ST|18907-6^Ciprofloxacin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||Resistant||||||F|||20260416110000
OBX|11|ST|18964-7^Nitrofurantoin [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||Susceptible||||||F|||20260416110000
OBX|12|ST|18993-6^Trimethoprim+Sulfamethoxazole [Susceptibility] by Minimum inhibitory concentration (MIC)^LN||Susceptible||||||F|||20260416110000
NTE|1|L|UTI confirmed. E. coli >100K CFU/mL. Ciprofloxacin resistant. Recommend Nitrofurantoin or TMP-SMX per sensitivities.
```

---

## 8. ORM^O01 - Medication order for Coumadin therapy at Bethlehem facility

```
MSH|^~\&|PCC|MORAVIAN_HALL_SQUARE|PHARMACY|OMNICARE|20260418161000||ORM^O01^ORM_O01|PCC20260418161000008|P|2.5.1|||AL|NE
PID|1||MRN800567^^^MHSQ^MR||Goldberg^Saul^Nathan^^Mr.^||19360923|M||2106-3^White^CDCREC|1780 Westgate Dr^^Bethlehem^PA^18017^US^H||^PRN^PH^^^610^5577305||ENG|W|JEW|ACCT150890^^^MHSQ^AN|936-17-4582|||N
PV1|1|I|LTCARE^310^A^MHSQ^^^^LTCARE|||1029384756^Shapiro^Deborah^L^^^MD^^^NPI||||SNF||||7|||1029384756^Shapiro^Deborah^L^^^MD^^^NPI|IN||MCARE
ORC|NW|ORD20260418001||||||1^^^20260418180000^^R||20260418160500|RNPHELPS||1029384756^Shapiro^Deborah^L^^^MD^^^NPI|LTCARE|||||||Moravian Hall Square^1780 Westgate Dr^^Bethlehem^PA^18017
OBR|1|ORD20260418001||85610^Prothrombin time (PT/INR)^CPT4|||20260419060000||||N|||||1029384756^Shapiro^Deborah^L^^^MD^^^NPI
DG1|1|I10|I48.91^Unspecified atrial fibrillation^ICD10|||A
RXO|11289^Warfarin Sodium 5 MG Oral Tablet^RxNorm||5|mg|11289^Warfarin Sodium 5 MG Oral Tablet^RxNorm|A||N|1||0|QD^Once Daily^HL70335||||||||||||||INR target 2.0-3.0
```

---

## 9. RDE^O11 - Pharmacy dispense for insulin at Lancaster care center

```
MSH|^~\&|PCC|MENNONITE_HOME_COMM|PHARMSYS|PHARMRX|20260420083000||RDE^O11^RDE_O11|PCC20260420083000009|P|2.5.1|||AL|NE
PID|1||MRN900678^^^MHCM^MR||Stoltzfus^Edna^Louise^^Mrs.^||19340715|F||2106-3^White^CDCREC|1520 Harrisburg Pike^^Lancaster^PA^17601^US^H||^PRN^PH^^^717^5544903||ENG|W|MEN|ACCT160901^^^MHCM^AN|047-29-8134|||N
PV1|1|I|LTCARE^205^B^MHCM^^^^LTCARE|||2148573960^Herr^Douglas^W^^^DO^^^NPI||||SNF||||7|||2148573960^Herr^Douglas^W^^^DO^^^NPI|IN||MCARE
ORC|RE|ORD20260419003|FIL20260420003||CM||||20260419140000|||2148573960^Herr^Douglas^W^^^DO^^^NPI
RXE|1^QAM^HL70335|261551^Insulin Glargine 100 UNT/ML Injectable Solution^RxNorm||22|units|261551^Insulin Glargine 100 UNT/ML Injectable Solution^RxNorm|SC^Subcutaneous^HL70162|||30|units||0|||||||||||||||MHCMPHARM
RXR|SC^Subcutaneous^HL70162|ABD^Abdomen^HL70163
RXC|B|261551^Insulin Glargine 100 UNT/ML Injectable Solution^RxNorm|22|units
NTE|1|P|Administer 22 units subcutaneously every morning before breakfast. Rotate injection sites. Monitor fasting blood glucose.
```

---

## 10. RDE^O11 - Pharmacy dispense for pain management at Wilkes-Barre facility

```
MSH|^~\&|POINTCLICKCARE|LITTLE_FLOWER_MANOR|PHARMSYS|OMNICARE|20260421140000||RDE^O11^RDE_O11|PCC20260421140000010|P|2.5.1|||AL|NE
PID|1||MRN1001234^^^LFMN^MR||Sadowski^Henryk^Tadeusz^^Mr.^||19390402|M||2106-3^White^CDCREC|312 Hazle Ave^^Wilkes-Barre^PA^18702^US^H||^PRN^PH^^^570^5533780||POL|W|CAT|ACCT170012^^^LFMN^AN|158-42-6039|||N
PV1|1|I|LTCARE^402^A^LFMN^^^^LTCARE|||3260481597^Baranov^Nikolai^V^^^MD^^^NPI||||SNF||||7|||3260481597^Baranov^Nikolai^V^^^MD^^^NPI|IN||MCARE
ORC|RE|ORD20260420004|FIL20260421004||CM||||20260420110000|||3260481597^Baranov^Nikolai^V^^^MD^^^NPI
RXE|1^Q8H^HL70335|197696^Acetaminophen 500 MG Oral Tablet^RxNorm||1000|mg|197696^Acetaminophen 500 MG Oral Tablet^RxNorm|PO^Oral^HL70162|||90|tablets||0|||||||||||||||LFMNPHARM
RXR|PO^Oral^HL70162
NTE|1|P|Acetaminophen 1000mg PO every 8 hours for chronic low back pain. Do not exceed 3000mg/day. Monitor hepatic function.
```

---

## 11. ORU^R01 - Chest X-ray report with base64-encoded PDF at York facility

```
MSH|^~\&|PCC_EHR|WELLSPAN_YORK_SNF|RADIS|WELLSPAN|20260423103000||ORU^R01^ORU_R01|PCC20260423103000011|P|2.5.1|||AL|NE
PID|1||MRN1101345^^^WYSN^MR||Pfeiffer^Gladys^Constance^^Mrs.^||19320529|F||2106-3^White^CDCREC|245 Pleasant Acres Rd^^York^PA^17402^US^H||^PRN^PH^^^717^5588140||ENG|W|LUT|ACCT180123^^^WYSN^AN|260-43-9517|||N
PV1|1|I|LTCARE^116^A^WYSN^^^^LTCARE|||4371528069^Obianuju^Kelechi^N^^^MD^^^NPI||||SNF||||7|||4371528069^Obianuju^Kelechi^N^^^MD^^^NPI|IN||MCARE
ORC|RE|ORD20260422005|FIL20260423005||CM||||20260422090000|||4371528069^Obianuju^Kelechi^N^^^MD^^^NPI
OBR|1|ORD20260422005|FIL20260423005|71046^Radiologic examination, chest, 2 views^CPT4|||20260422140000|||||||||4371528069^Obianuju^Kelechi^N^^^MD^^^NPI||||||20260423100000|||F
OBX|1|ST|30746-2^Portable XR Chest Views^LN||See attached report||||||F|||20260423100000
OBX|2|ED|30746-2^Portable XR Chest Views^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSAxMDAgMCBSCj4+Cj4+Ci9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCi9Db250ZW50cyA0IDAgUgo+PgplbmRvYmoKNCAwIG9iago8PAovTGVuZ3RoIDQ0Cj4+CnN0cmVhbQpCVCAvRjEgMTggVGYgMTAwIDcwMCBUZCAoQ2hlc3QgWC1SYXkgUmVwb3J0KSBUaiBFVAplbmRzdHJlYW0KZW5kb2JqCjEwMCAwIG9iago8PAovVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxNSAwMDAwMCBuIAowMDAwMDAwMDY4IDAwMDAwIG4gCjAwMDAwMDAxNzEgMDAwMDAgbiAKMDAwMDAwMDM4NCAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDUKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjQ4MgolJUVPRgo=||||||F|||20260423100000
OBX|3|FT|30746-2^Portable XR Chest Views^LN||FINDINGS: The cardiac silhouette is mildly enlarged. There is bibasilar atelectasis, left greater than right. No focal consolidation, pleural effusion, or pneumothorax identified. Degenerative changes of the thoracic spine are noted. A healed left rib fracture is seen along the posterolateral aspect of the 7th rib.\.br\\.br\IMPRESSION:\.br\1. Mild cardiomegaly, stable.\.br\2. Bibasilar atelectasis, may reflect hypoventilation.\.br\3. No acute cardiopulmonary process.\.br\4. Healed left 7th rib fracture.||||||F|||20260423100000
NTE|1|L|Compared with prior study dated 2025-11-15. Cardiomegaly is unchanged. Atelectasis slightly increased.
```

---

## 12. MDM^T02 - Clinical progress note for Alzheimer's resident at State College facility

```
MSH|^~\&|PCC|JUNIPER_VILLAGE_SC|RECEIVING|DOCMGMT|20260425091500||MDM^T02^MDM_T02|PCC20260425091500012|P|2.5.1|||AL|NE
EVN|T02|20260425091000
PID|1||MRN1201456^^^JVSC^MR||Pham^Duc^Minh^^Mr.^||19370810|M||2028-9^Asian^CDCREC|1026 Benner Pike^^State College^PA^16801^US^H||^PRN^PH^^^814^5533042||VIE|W|BUD|ACCT190234^^^JVSC^AN|371-50-8264|||N
PV1|1|I|MEMORY^MC03^A^JVSC^^^^MEMORY|||5482716039^Hartley^Joanne^R^^^MD^^^NPI||||SNF||||7|||5482716039^Hartley^Joanne^R^^^MD^^^NPI|IN||MCARE
TXA|1|PN^Progress Note^HL70270|TX||20260425090000||||||5482716039^Hartley^Joanne^R^^^MD^^^NPI||||||AU^Authenticated^HL70271
OBX|1|FT|11506-3^Progress Note^LN||SUBJECTIVE: Patient continues to reside in memory care unit. Family reports increased confusion and agitation in the evenings over the past week, consistent with sundowning behavior. Nursing staff notes patient has been wandering from room more frequently. Appetite remains fair. Sleep pattern disrupted with multiple nighttime awakenings.\.br\\.br\OBJECTIVE:\.br\Vitals: BP 128/78, HR 72, RR 16, Temp 97.8F, SpO2 97% on RA\.br\Weight: 162 lbs (stable from last month)\.br\General: Alert, oriented to self only. Pleasant and cooperative during examination.\.br\HEENT: Normocephalic. Pupils equal and reactive.\.br\CV: RRR, no murmurs.\.br\Lungs: CTA bilaterally.\.br\Neuro: MMSE score 12/30 (decline from 15/30 three months ago). Gait steady with rolling walker.\.br\\.br\ASSESSMENT:\.br\1. Alzheimer's disease, moderate stage - progressing. MMSE decline of 3 points over 3 months.\.br\2. Sundowning behavior - worsening.\.br\3. Hypertension - controlled.\.br\4. BPH - stable on current medications.\.br\\.br\PLAN:\.br\1. Continue Donepezil 10mg daily and Memantine 10mg BID.\.br\2. Add Trazodone 25mg QHS for sleep disturbance and sundowning.\.br\3. Increase structured afternoon activities per activity director.\.br\4. Fall risk reassessment by PT/OT.\.br\5. Family conference scheduled for 2026-05-02 to discuss care plan changes.\.br\6. Follow up in 30 days or sooner PRN.||||||F|||20260425090000
```

---

## 13. MDM^T02 - MDS assessment note with base64-encoded document at Altoona facility

```
MSH|^~\&|POINTCLICKCARE|GARVEY_MANOR_SNF|RECEIVING|DOCMGMT|20260427143000||MDM^T02^MDM_T02|PCC20260427143000013|P|2.5.1|||AL|NE
EVN|T02|20260427142500
PID|1||MRN1301567^^^GMSN^MR||Flanagan^Kathleen^Bridget^^Mrs.^||19400103|F||2106-3^White^CDCREC|1037 S Logan Blvd^^Altoona^PA^16602^US^H||^PRN^PH^^^814^5599412||ENG|W|CAT|ACCT200345^^^GMSN^AN|482-61-3907|||N
PV1|1|I|LTCARE^220^A^GMSN^^^^LTCARE|||6593018274^Rivera^Carlos^J^^^MD^^^NPI||||SNF||||7|||6593018274^Rivera^Carlos^J^^^MD^^^NPI|IN||MCARE
TXA|1|DS^Discharge Summary^HL70270|TX||20260427140000||||||6593018274^Rivera^Carlos^J^^^MD^^^NPI||||||AU^Authenticated^HL70271
OBX|1|ED|11502-2^Laboratory report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSAxMDAgMCBSCj4+Cj4+Ci9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCi9Db250ZW50cyA0IDAgUgo+PgplbmRvYmoKNCAwIG9iago8PAovTGVuZ3RoIDUyCj4+CnN0cmVhbQpCVCAvRjEgMTggVGYgMTAwIDcwMCBUZCAoTURTIEFzc2Vzc21lbnQgU3VtbWFyeSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagoxMDAgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMTUgMDAwMDAgbiAKMDAwMDAwMDA2OCAwMDAwMCBuIAowMDAwMDAwMTcxIDAwMDAwIG4gCjAwMDAwMDAzODQgMDAwMDAgbiAKdHJhaWxlcgo8PAovU2l6ZSA1Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgo0OTAKJSVFT0YK||||||F|||20260427140000
OBX|2|FT|11502-2^Laboratory report^LN||MDS 3.0 QUARTERLY ASSESSMENT SUMMARY\.br\\.br\Resident: Flanagan, Kathleen Bridget\.br\Assessment Reference Date: 2026-04-27\.br\Reason for Assessment: Quarterly\.br\\.br\SECTION C - COGNITIVE PATTERNS:\.br\BIMS Score: 7 (Moderately Impaired)\.br\\.br\SECTION G - FUNCTIONAL STATUS:\.br\ADL Self-Performance: Bed mobility 2 (Limited assistance), Transfer 3 (Extensive assistance), Eating 1 (Supervision), Toileting 3 (Extensive assistance), Hygiene 2 (Limited assistance)\.br\\.br\SECTION I - ACTIVE DIAGNOSES:\.br\Alzheimer's disease, Heart failure (NYHA Class II), Osteoporosis, Depression, Hypothyroidism\.br\\.br\SECTION J - HEALTH CONDITIONS:\.br\Pain: Assessed via staff observation. Indicators of pain present 1-2 days.\.br\Falls: No falls since last assessment.\.br\\.br\SECTION N - MEDICATIONS:\.br\Total medications: 14\.br\Antipsychotic use: No\.br\Antianxiety use: Yes (Lorazepam 0.5mg PRN)\.br\\.br\SECTION O - SPECIAL TREATMENTS:\.br\Physical therapy 5x/week. Occupational therapy 3x/week.\.br\\.br\RUG-IV Classification: RHC||||||F|||20260427140000
```

---

## 14. DFT^P03 - Charge posting for physical therapy session at Norristown facility

```
MSH|^~\&|PCC|ELMWOOD_PARK_SNF|BILLING|RCMSYS|20260428160000||DFT^P03^DFT_P03|PCC20260428160000014|P|2.5.1|||AL|NE
EVN|P03|20260428155500
PID|1||MRN1401678^^^EPSN^MR||Cataldi^Rocco^Salvatore^^Mr.^||19450318|M||2106-3^White^CDCREC|440 E Germantown Pike^^Norristown^PA^19401^US^H||^PRN^PH^^^484^5522349||ITA|W|CAT|ACCT210456^^^EPSN^AN|593-74-2018|||N
PV1|1|I|REHAB^104^A^EPSN^^^^REHAB|||7714058293^Gupta^Ananya^M^^^MD^^^NPI||||SNF||||7|||7714058293^Gupta^Ananya^M^^^MD^^^NPI|IN||MCARE
FT1|1|20260428|20260428155000|P|D|1||97110^Therapeutic exercises^CPT4|||1|45.00||97110^Therapeutic exercises^CPT4|7714058293^Gupta^Ananya^M^^^MD^^^NPI|8825169304^Wallace^Brianna^T^^^PT^^^NPI|||||||||97110
FT1|2|20260428|20260428155000|P|D|1||97140^Manual therapy techniques^CPT4|||1|38.00||97140^Manual therapy techniques^CPT4|7714058293^Gupta^Ananya^M^^^MD^^^NPI|8825169304^Wallace^Brianna^T^^^PT^^^NPI|||||||||97140
FT1|3|20260428|20260428155000|P|D|1||97530^Therapeutic activities^CPT4|||1|42.00||97530^Therapeutic activities^CPT4|7714058293^Gupta^Ananya^M^^^MD^^^NPI|8825169304^Wallace^Brianna^T^^^PT^^^NPI|||||||||97530
DG1|1|I10|M54.5^Low back pain^ICD10|||A
DG1|2|I10|M62.81^Muscle weakness (generalized)^ICD10|||S
IN1|1|001|MCARE001^Medicare Part A|Centers for Medicare^^Baltimore^MD^21244|^PRN^PH^^^800^6332273|||||||||Cataldi^Rocco^Salvatore|SEL|19450318|440 E Germantown Pike^^Norristown^PA^19401||1|||||||||||||HIC593742018A||||||M
```

---

## 15. DFT^P03 - Charge posting for occupational therapy at Johnstown facility

```
MSH|^~\&|PCC_EHR|ARBUTUS_PARK_SNF|BILLING|RCMSYS|20260429110000||DFT^P03^DFT_P03|PCC20260429110000015|P|2.5.1|||AL|NE
EVN|P03|20260429105500
PID|1||MRN1501789^^^APSN^MR||Kovalchuk^Nadia^Olena^^Mrs.^||19380622|F||2106-3^White^CDCREC|231 Haynes St^^Johnstown^PA^15906^US^H||^PRN^PH^^^814^5511840||UKR|W|ORT|ACCT220567^^^APSN^AN|704-83-5126|||N
PV1|1|I|REHAB^208^B^APSN^^^^REHAB|||9936024817^Abbas^Farhan^Q^^^DO^^^NPI||||SNF||||7|||9936024817^Abbas^Farhan^Q^^^DO^^^NPI|IN||MCARE
FT1|1|20260429|20260429103000|P|D|1||97165^OT evaluation, low complexity^CPT4|||1|85.00||97165^OT evaluation, low complexity^CPT4|9936024817^Abbas^Farhan^Q^^^DO^^^NPI|1047295836^Thornton^Jessica^A^^^OTR^^^NPI|||||||||97165
FT1|2|20260429|20260429103000|P|D|1||97530^Therapeutic activities^CPT4|||1|42.00||97530^Therapeutic activities^CPT4|9936024817^Abbas^Farhan^Q^^^DO^^^NPI|1047295836^Thornton^Jessica^A^^^OTR^^^NPI|||||||||97530
DG1|1|I10|S72.001D^Fracture of unspecified part of neck of right femur, subsequent encounter^ICD10|||A
DG1|2|I10|R26.81^Unsteadiness on feet^ICD10|||S
IN1|1|001|MCARE001^Medicare Part A|Centers for Medicare^^Baltimore^MD^21244|^PRN^PH^^^800^6332273|||||||||Kovalchuk^Nadia^Olena|SEL|19380622|231 Haynes St^^Johnstown^PA^15906||1|||||||||||||HIC704835126A||||||F
```

---

## 16. ORM^O01 - Lab order for HbA1c and lipid panel at Chester County SNF

```
MSH|^~\&|PCC|BARCLAY_FRIENDS_SNF|LABCORP|LAB|20260501083000||ORM^O01^ORM_O01|PCC20260501083000016|P|2.5.1|||AL|NE
PID|1||MRN1601890^^^BFSN^MR||Cho^Eunice^Soomin^^Mrs.^||19310914|F||2028-9^Asian^CDCREC|700 N Franklin St^^West Chester^PA^19380^US^H||^PRN^PH^^^610^5566241||KOR|W|PRE|ACCT230678^^^BFSN^AN|813-96-4270|||N
PV1|1|I|LTCARE^315^A^BFSN^^^^LTCARE|||1150283746^Donovan^Patrick^E^^^MD^^^NPI||||SNF||||7|||1150283746^Donovan^Patrick^E^^^MD^^^NPI|IN||MCARE
ORC|NW|ORD20260501001||||||1^^^20260502060000^^R||20260501082500|RNCOLEMAN||1150283746^Donovan^Patrick^E^^^MD^^^NPI|LTCARE|||||||Barclay Friends SNF^700 N Franklin St^^West Chester^PA^19380
OBR|1|ORD20260501001||83036^Hemoglobin A1c^CPT4|||20260502060000||||N|||||1150283746^Donovan^Patrick^E^^^MD^^^NPI
OBR|2|ORD20260501002||80061^Lipid Panel^CPT4|||20260502060000||||Y|||||1150283746^Donovan^Patrick^E^^^MD^^^NPI
DG1|1|I10|E11.65^Type 2 diabetes mellitus with hyperglycemia^ICD10|||A
DG1|2|I10|E78.5^Dyslipidemia, unspecified^ICD10|||S
NTE|1|P|Fasting labs. NPO after midnight. Draw at 0600. HbA1c trending up, last value 8.2%.
```

---

## 17. ORU^R01 - INR result for anticoagulation monitoring at Doylestown facility

```
MSH|^~\&|PCC|PINE_RUN_HC|LABCORP|LAB|20260503091200||ORU^R01^ORU_R01|PCC20260503091200017|P|2.5.1|||AL|NE
PID|1||MRN1701901^^^PRHC^MR||Schaeffer^Harold^Eugene^^Mr.^||19280611|M||2106-3^White^CDCREC|777 Ferry Rd^^Doylestown^PA^18901^US^H||^PRN^PH^^^215^5588271||GER|W|LUT|ACCT240789^^^PRHC^AN|924-05-7318|||N
PV1|1|I|LTCARE^106^A^PRHC^^^^LTCARE|||2261493780^Nwosu^Adaeze^C^^^MD^^^NPI||||SNF||||7|||2261493780^Nwosu^Adaeze^C^^^MD^^^NPI|IN||MCARE
ORC|RE|ORD20260502006|FIL20260503006||CM||||20260502140000|||2261493780^Nwosu^Adaeze^C^^^MD^^^NPI
OBR|1|ORD20260502006|FIL20260503006|85610^Prothrombin time (PT/INR)^CPT4|||20260503060000|||||||||2261493780^Nwosu^Adaeze^C^^^MD^^^NPI||||||20260503090000|||F
OBX|1|NM|5902-2^Prothrombin time (PT)^LN||18.5|seconds|11.0-13.5|H|||F|||20260503090000
OBX|2|NM|6301-6^INR in Platelet poor plasma by Coagulation assay^LN||3.4|ratio|2.0-3.0|H|||F|||20260503090000
NTE|1|L|INR supratherapeutic at 3.4 (target 2.0-3.0). Recommend holding Warfarin tonight and rechecking INR in 48 hours. Notify physician immediately.
```

---

## 18. ADT^A08 - Insurance update for Medicaid pending resident at Easton facility

```
MSH|^~\&|POINTCLICKCARE|EASTON_NURSING_CTR|RECEIVING|STATEHI|20260505100000||ADT^A08^ADT_A08|PCC20260505100000018|P|2.5.1|||AL|NE
EVN|A08|20260505095500|||BILLINGCLK
PID|1||MRN1801012^^^ENCR^MR||Delgado^Yolanda^Esperanza^^Mrs.^||19420728|F||2106-3^White^CDCREC|430 Northampton St^^Easton^PA^18042^US^H||^PRN^PH^^^610^5511608||SPA|W|CAT|ACCT250890^^^ENCR^AN|037-18-5924|||H||||20250801
NK1|1|Delgado^Miguel^R^^Mr.^||1220 W Broad St^^Bethlehem^PA^18018^US|^PRN^PH^^^610^5577450||SON^Son^HL70063
PV1|1|I|LTCARE^312^A^ENCR^^^^LTCARE|||3372604918^Kowalewski^Stefan^D^^^MD^^^NPI||||SNF||||7|||3372604918^Kowalewski^Stefan^D^^^MD^^^NPI|IN||MAPDL
IN1|1|001|MCARE001^Medicare Part A|Centers for Medicare^^Baltimore^MD^21244|^PRN^PH^^^800^6332273|||||||||Delgado^Yolanda^Esperanza|SEL|19420728|430 Northampton St^^Easton^PA^18042||1|||||||||||||HIC037185924A||||||F
IN1|2|002|MAPDL001^Pennsylvania Medicaid|PA Dept of Human Services^^Harrisburg^PA^17120|^PRN^PH^^^800^6929745|||||||||Delgado^Yolanda^Esperanza|SEL|19420728|430 Northampton St^^Easton^PA^18042||2|||||||||||||MAID882047613||||||F
IN1|3|003|GEIS001^Geisinger Health Plan|Geisinger Insurance^^Danville^PA^17822|^PRN^PH^^^800^4474000|||||||||Delgado^Yolanda^Esperanza|SEL|19420728|430 Northampton St^^Easton^PA^18042||3|||||||||||||POL661502||||||F
```

---

## 19. ADT^A01 - Admission for respite care at Bucks County facility

```
MSH|^~\&|PCC|CHANDLER_HALL_HC|RECEIVING|STATEHI|20260507141500||ADT^A01^ADT_A01|PCC20260507141500019|P|2.5.1|||AL|NE
EVN|A01|20260507141000|||ADMCOORD
PID|1||MRN1901123^^^CHHC^MR~142-27-6085^^^SSA^SS||Sullivan^Declan^Francis^^Mr.^||19350916|M||2106-3^White^CDCREC|2850 Bristol Rd^^Warrington^PA^18976^US^H||^PRN^PH^^^267^5533190||ENG|W|CAT|ACCT260901^^^CHHC^AN|142-27-6085|||N||||20260507
PD1|||Chandler Hall Health Services^^^CHHC||||||||N
NK1|1|Sullivan^Maureen^Clare^^Mrs.^||2850 Bristol Rd^^Warrington^PA^18976^US|^PRN^PH^^^267^5533190||SPO^Spouse^HL70063
NK1|2|Sullivan^Brendan^P^^Mr.^||1445 County Line Rd^^Chalfont^PA^18914^US|^PRN^PH^^^215^5599720||SON^Son^HL70063
PV1|1|I|RESPITE^RC02^A^CHHC^^^^RESPITE|||4483920167^Brennan^Colleen^T^^^DO^^^NPI||||SNF||||7|||4483920167^Brennan^Colleen^T^^^DO^^^NPI|IN||MCARE|||||||||||||||AI|||20260507141000
PV2|||^Respite care - caregiver relief, 14 day planned stay||||||20260507|||||||||20260521|||||N
DG1|1|I10|G30.1^Alzheimer's disease with late onset^ICD10|||A
DG1|2|I10|F02.80^Dementia in other diseases classified elsewhere without behavioral disturbance^ICD10|||S
DG1|3|I10|I10^Essential (primary) hypertension^ICD10|||S
DG1|4|I10|M81.0^Age-related osteoporosis without current pathological fracture^ICD10|||S
AL1|1|DA|2670^Codeine^RxNorm|SV|Nausea, vomiting, severe constipation|20080301
IN1|1|001|MCARE001^Medicare Part A|Centers for Medicare^^Baltimore^MD^21244|^PRN^PH^^^800^6332273|||||||||Sullivan^Declan^Francis|SEL|19350916|2850 Bristol Rd^^Warrington^PA^18976||1|||||||||||||HIC142276085A||||||M
GT1|1||Sullivan^Declan^Francis^^Mr.^|2850 Bristol Rd^^Warrington^PA^18976^US|^PRN^PH^^^267^5533190||19350916|M||SEL|142-27-6085
```

---

## 20. ORU^R01 - Comprehensive metabolic panel with critical potassium at Chambersburg SNF

```
MSH|^~\&|PCC_EHR|MENNO_HAVEN_SNF|QUEST|LAB|20260509071500||ORU^R01^ORU_R01|PCC20260509071500020|P|2.5.1|||AL|NE
PID|1||MRN2001234^^^MHSN^MR||Hostetter^Naomi^Grace^^Mrs.^||19330420|F||2106-3^White^CDCREC|2075 Scotland Ave^^Chambersburg^PA^17201^US^H||^PRN^PH^^^717^5544180||ENG|W|MEN|ACCT270012^^^MHSN^AN|153-40-7892|||N
PV1|1|I|LTCARE^128^A^MHSN^^^^LTCARE|||5598173042^Zimmerman^Paul^R^^^MD^^^NPI||||SNF||||7|||5598173042^Zimmerman^Paul^R^^^MD^^^NPI|IN||MCARE
ORC|RE|ORD20260508007|FIL20260509007||CM||||20260508150000|||5598173042^Zimmerman^Paul^R^^^MD^^^NPI
OBR|1|ORD20260508007|FIL20260509007|80053^Comprehensive Metabolic Panel^CPT4|||20260509060000|||||||||5598173042^Zimmerman^Paul^R^^^MD^^^NPI||||||20260509071000|||F
OBX|1|NM|2345-7^Glucose [Mass/volume] in Serum or Plasma^LN||98|mg/dL|70-100|N|||F|||20260509071000
OBX|2|NM|3094-0^Urea nitrogen [Mass/volume] in Serum or Plasma^LN||32|mg/dL|7-20|H|||F|||20260509071000
OBX|3|NM|2160-0^Creatinine [Mass/volume] in Serum or Plasma^LN||1.8|mg/dL|0.6-1.2|HH|||F|||20260509071000
OBX|4|NM|3097-3^Urea nitrogen/Creatinine [Mass Ratio] in Serum or Plasma^LN||17.8|ratio|10-20|N|||F|||20260509071000
OBX|5|NM|2951-2^Sodium [Moles/volume] in Serum or Plasma^LN||134|mmol/L|136-145|L|||F|||20260509071000
OBX|6|NM|2823-3^Potassium [Moles/volume] in Serum or Plasma^LN||5.9|mmol/L|3.5-5.1|HH|||F|||20260509071000
OBX|7|NM|2075-0^Chloride [Moles/volume] in Serum or Plasma^LN||99|mmol/L|98-106|N|||F|||20260509071000
OBX|8|NM|2028-9^Carbon dioxide, total [Moles/volume] in Serum or Plasma^LN||19|mmol/L|22-29|L|||F|||20260509071000
OBX|9|NM|17861-6^Calcium [Mass/volume] in Serum or Plasma^LN||8.9|mg/dL|8.5-10.5|N|||F|||20260509071000
OBX|10|NM|2885-2^Protein [Mass/volume] in Serum or Plasma^LN||6.4|g/dL|6.0-8.3|N|||F|||20260509071000
OBX|11|NM|1751-7^Albumin [Mass/volume] in Serum or Plasma^LN||3.1|g/dL|3.5-5.5|L|||F|||20260509071000
OBX|12|NM|1975-2^Bilirubin.total [Mass/volume] in Serum or Plasma^LN||0.8|mg/dL|0.1-1.2|N|||F|||20260509071000
OBX|13|NM|6768-6^Alkaline phosphatase [Enzymatic activity/volume] in Serum or Plasma^LN||88|U/L|44-147|N|||F|||20260509071000
OBX|14|NM|1742-6^Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||22|U/L|7-56|N|||F|||20260509071000
OBX|15|NM|1920-8^Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma^LN||28|U/L|10-40|N|||F|||20260509071000
OBX|16|NM|33914-3^Glomerular filtration rate/1.73 sq M.predicted [Volume Rate/Area] in Serum or Plasma^LN||28|mL/min/1.73m2|>60|L|||F|||20260509071000
NTE|1|L|CRITICAL VALUE: Potassium 5.9 mmol/L. Physician notified at 0720 by RN Martinez. Creatinine elevated at 1.8, eGFR 28 consistent with CKD Stage 4. Hyponatremia 134. Low albumin 3.1 may indicate nutritional deficiency. Recommend nephrology consult and dietary review.
```
