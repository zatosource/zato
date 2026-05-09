# Epic Systems - real HL7v2 ER7 messages

## 1. ADT^A01 - Inpatient admission at Johns Hopkins Hospital

```
MSH|^~\&|EPIC|JHHOSP|ADT_RECV|JHHOSP|20250815091234||ADT^A01^ADT_A01|JHH20250815091234001|P|2.5.1|||AL|NE
EVN|A01|20250815091200|||PNORRIS^Norris^Patricia^L^^MD|20250815090000
PID|1||E61584844^^^EPIC^MRN~56147537^^^JHHMPI^MR||YAMAMOTO^Ibrahim^Douglas^^^Mr.||19710320|M||2106-3^White^CDCREC|9580 Frankford Ave^^Washington^DC^20032^US^L||^PRN^PH^^^202^2645280~^NET^Internet^ibrahim.yamamoto97@email.com|^WPN^PH^^^202^3571701|eng^English^ISO6392|M^Married^HL70002|||281-67-7086|||H^Hispanic or Latino^HL70189
PD1|||JOHNS HOPKINS HOSPITAL^^10001|8753625751^Southgate^Conrad^W^^MD^^^NPI
NK1|1|BAKARE^Noelia^A|SPO^Spouse^HL70063|9580 Frankford Ave^^Washington^DC^20032^US|^PRN^PH^^^202^4727741||EC^Emergency Contact^HL70131
PV1|1|I|ZION4^4102^A^JHHOSP^^^^ZION4||||8753625751^Southgate^Conrad^W^^MD^^^NPI|3483838721^Fairbanks^Henrietta^G^^MD^^^NPI|CAR^Cardiology^JHSERV|||R^Referral^HL70007|||||V80037291^^^JHENC^VN|||||||||||||||||||||||||20250815091200
PV2|||^Acute myocardial infarction^I21.9
IN1|1|BCMD001^CareFirst BlueCross BlueShield^^CAREFIRST|67890|CAREFIRST BLUECROSS BLUESHIELD|10455 Mill Run Circle^^Owings Mills^MD^21117^US|^PRN^PH^^^410^5812000|GRP77301||JOHNS HOPKINS UNIVERSITY|||||20240101|20251231|||1^Subscriber^HL70072|9580 Frankford Ave^Lamar^Washington|01^Self^HL70063|19710320|2519 Fleet St^^Baltimore^MD^21224^US|||1|||YES||||||||||CFB4408731245
IN1|2|MEDCR001^Medicare^^CMS|00001|MEDICARE|PO Box 1270^^Portland^ME^04104^US||||||||20360320|||YAMAMOTO^Ibrahim^Douglas|DRUMMOND^Lamar^Keith|01^Self^HL70063|9580 Frankford Ave|2519 Fleet St^^Baltimore^MD^21224^US
```

---

## 2. ADT^A04 - Emergency department registration at University of Maryland Medical Center

```
MSH|^~\&|EPIC|UMMC|EDIS|UMMC|20250922143512||ADT^A04^ADT_A01|UMMC20250922143512001|P|2.5.1|||AL|NE
EVN|A04|20250922143500|||ABRYANT^Bryant^Andrea^M^^RN|20250922143000
PID|1||E98597699^^^EPIC^MRN~49615715^^^UMMCMPI^MR||PRESCOTT^Paloma^Irene^^^Ms.||19880714|F||2054-5^Black or African American^CDCREC|3795 Virginia Ave^^Catonsville^MD^21229^US^L||^PRN^PH^^^240^3934253~^NET^Internet^paloma.prescott99@email.com||eng^English^ISO6392|S^Single^HL70002|||156-87-1158|||N^Non-Hispanic^HL70189
PD1|||UNIV OF MARYLAND MEDICAL CENTER^^20001|2871026289^Carmichael^Randolph^R^^MD^^^NPI
NK1|1|PRESCOTT^Tatiana^F|MTH^Mother^HL70063|3795 Virginia Ave^^Catonsville^MD^21229^US|^PRN^PH^^^240^8689688||EC^Emergency Contact^HL70131
PV1|1|E|EDUMMC^ED08^A^UMMC^^^^EDUMMC||||2871026289^Carmichael^Randolph^R^^MD^^^NPI|8926527583^Northcutt^Josephina^M^^MD^^^NPI|EM^Emergency Medicine^UMMCSERV|||E^Emergency^HL70007|||||V80049273^^^UMMCENC^VN|||||||||||||||||||||||||20250922143500
PV2|||^Acute asthma exacerbation^J45.901
IN1|1|MDMC001^Maryland Medicaid^^MDMEDICAID|33201|MARYLAND MEDICAID|201 W Preston St^^Baltimore^MD^21201^US|^PRN^PH^^^410^7673000|||||||||20240101|PRESCOTT|||3795 Virginia Ave^Subscriber^Catonsville|TILLERY^Shanice^Patrice|01^Self^HL70063|19880714|4027 Belair Rd^^Baltimore^MD^21213^US|||1|||YES||||||||||MMA9907382154
```

---

## 3. ADT^A03 - Discharge from Johns Hopkins Bayview Medical Center

```
MSH|^~\&|EPIC|JHBAYVIEW|BILLING|JHBAYVIEW|20250710161530||ADT^A03^ADT_A03|JHB20250710161530001|P|2.5.1|||AL|NE
EVN|A03|20250710161500|||RFIELDS^Fields^Rita^S^^RN|20250710160000
PID|1||E18168989^^^EPIC^MRN~37025013^^^JHHMPI^MR||DURAND^Marcus^Norbert^^^Mr.||19590225|M||2106-3^White^CDCREC|1120 Solomons Island Rd^^Hagerstown^MD^21742^US^L||^PRN^PH^^^443^5665519~^NET^Internet^marcus.durand27@email.com||eng^English^ISO6392|M^Married^HL70002|||204-32-4758|||N^Non-Hispanic^HL70189
PV1|1|I|5SURG^5208^A^JHBAYVIEW^^^^5SURG||||6411732122^Harrington^Breckenridge^P^^MD^^^NPI|5963681289^Pemberton^Dorothea^S^^MD^^^NPI|GS^General Surgery^JHSERV|||R^Referral^HL70007|||||V80061384^^^JHENC^VN||DI^Discharged to Home^HL70112||||||||||||||||||||||||20250707083000|20250710161500
DG1|1||K80.10^Calculus of gallbladder with chronic cholecystitis without obstruction^I10||20250707|A^Admitting^HL70052
DG1|2||K80.10^Calculus of gallbladder with chronic cholecystitis without obstruction^I10||20250710|F^Final^HL70052
PR1|1||0FT44ZZ^Resection of Gallbladder, Percutaneous Endoscopic Approach^ICD10PCS|Laparoscopic cholecystectomy|20250708140000|A^Anesthesia^HL70230||||||6411732122^Harrington^Breckenridge^P^^MD^^^NPI
```

---

## 4. ADT^A08 - Patient information update at Suburban Hospital (Johns Hopkins)

```
MSH|^~\&|EPIC|SUBURBAN|REGUPD|SUBURBAN|20250601102045||ADT^A08^ADT_A01|SUB20250601102045001|P|2.5.1|||AL|NE
EVN|A08|20250601102000|||JKENDALL^Kendall^Judith^N^^REG|20250601101500
PID|1||E24521168^^^EPIC^MRN~13095029^^^JHHMPI^MR||SEVILLA^Preston^Theodore^^^Mr.||19830911|M||2028-9^Asian^CDCREC|4238 Calvert St^^Rockville^MD^20850^US^L||^PRN^PH^^^410^6904782~^NET^Internet^preston.sevilla52@email.com||eng^English^ISO6392|M^Married^HL70002|||803-27-9927|||N^Non-Hispanic^HL70189
PD1|||SUBURBAN HOSPITAL^^30001|7192103760^Radcliffe^Gresham^W^^MD^^^NPI
NK1|1|SEVILLA^Yvette^J|SPO^Spouse^HL70063|4238 Calvert St^^Rockville^MD^20850^US|^PRN^PH^^^410^6821351||EC^Emergency Contact^HL70131
PV1|1|O|SUBCLIN^VIST2^A^SUBURBAN^^^^SUBCLIN||||7192103760^Radcliffe^Gresham^W^^MD^^^NPI||PCP^Primary Care^SUBSERV|||R^Referral^HL70007|||||V80072946^^^SUBENC^VN|||||||||||||||||||||||||20250601102000
IN1|1|UHCMD001^UnitedHealthcare MD^^UHC|44521|UNITEDHEALTHCARE OF MARYLAND|PO Box 740800^^Atlanta^GA^30374^US|^PRN^PH^^^800^3281044|GRP66201||NATIONAL INSTITUTES OF HEALTH|||||20240101|20251231|||1^Subscriber^HL70072|4238 Calvert St^Rohan^Rockville|01^Self^HL70063|19830911|9218 Fernwood Rd^^Bethesda^MD^20817^US|||1|||YES||||||||||UHC3309184572
```

---

## 5. ORU^R01 - Pathology result with embedded PDF report at Johns Hopkins Hospital

```
MSH|^~\&|EPIC|JHHOSP|PATHSYS|JHHOSP|20250903112034||ORU^R01^ORU_R01|JHH20250903112034001|P|2.5.1|||AL|NE
PID|1||E29913745^^^EPIC^MRN~64776997^^^JHHMPI^MR||MERRIWEATHER^Cornelia^Zelda^^^Mrs.||19670508|F||2054-5^Black or African American^CDCREC|3745 Baltimore St^^Wheaton^MD^20902^US^L||^PRN^PH^^^410^2429011||eng^English^ISO6392|M^Married^HL70002|||881-19-6433|||N^Non-Hispanic^HL70189
PV1|1|I|ONCO3^3112^A^JHHOSP^^^^ONCO3||||5228350716^Southgate^Conrad^R^^MD^^^NPI||ONC^Oncology^JHSERV|||||||||V80083917^^^JHENC^VN|||||||||||||||||||||||||20250901093000
ORC|RE|ORD601234^EPIC|PATH901234^PATHSYS||CM||^^^20250903112000^^R||20250903112034|TASHBY^Ashby^Theodora^O^^CT|||20250903112034||JHHOSP
OBR|1|ORD601234^EPIC|PATH901234^PATHSYS|88305^Surgical Pathology^CPT||||20250901150000||||||||5228350716^Southgate^Conrad^R^^MD^^^NPI||||||20250903112000|||F
OBX|1|TX|22637-3^Pathology Report^LN||Specimen: Left breast mass excisional biopsy. Diagnosis: Invasive ductal carcinoma, grade 2, measuring 1.8 cm. Margins: All margins negative, closest margin 0.3 cm (deep). Lymphovascular invasion: Not identified. ER positive (95%), PR positive (80%), HER2 negative (IHC 1+).||||||F|||20250903110000
OBX|2|ED|PDF-PATH^Pathology Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F|||20250903110000
```

---

## 6. ORU^R01 - CBC lab result at University of Maryland Medical Center

```
MSH|^~\&|EPIC|UMMC|LABSYS|UMMC|20250818074530||ORU^R01^ORU_R01|UMMC20250818074530001|P|2.5.1|||AL|NE
PID|1||E75087758^^^EPIC^MRN~15471820^^^UMMCMPI^MR||NWOSU^Emory^Elmer^^^Mr.||19750129|M||2054-5^Black or African American^CDCREC|9105 New Hampshire Ave^^Germantown^MD^20874^US^L||^PRN^PH^^^240^6965432||eng^English^ISO6392|S^Single^HL70002|||537-87-4838|||N^Non-Hispanic^HL70189
PV1|1|I|MED6^6205^A^UMMC^^^^MED6||||3817917234^Carmichael^Randolph^P^^MD^^^NPI||MED^Internal Medicine^UMMCSERV|||||||||V80094538^^^UMMCENC^VN|||||||||||||||||||||||||20250816110000
ORC|RE|ORD701234^EPIC|LAB501234^LABSYS||CM||^^^20250818074500^^R||20250818074530|BHOLBROO^Holbrook^Bernice^H^^MT|||20250818074530||UMMC
OBR|1|ORD701234^EPIC|LAB501234^LABSYS|58410-2^CBC with Differential^LN||||20250818060000||||||||3817917234^Carmichael^Randolph^P^^MD^^^NPI||||||20250818074500|||F
OBX|1|NM|6690-2^Leukocytes^LN||12.8|10*3/uL|4.5-11.0|H|||F|||20250818073000
OBX|2|NM|789-8^Erythrocytes^LN||4.52|10*6/uL|4.50-5.90|N|||F|||20250818073000
OBX|3|NM|718-7^Hemoglobin^LN||13.1|g/dL|13.5-17.5|L|||F|||20250818073000
OBX|4|NM|4544-3^Hematocrit^LN||39.2|%|40.0-52.0|L|||F|||20250818073000
OBX|5|NM|787-2^Mean Corpuscular Volume^LN||86.7|fL|80.0-100.0|N|||F|||20250818073000
OBX|6|NM|785-6^Mean Corpuscular Hemoglobin^LN||29.0|pg|26.0-34.0|N|||F|||20250818073000
OBX|7|NM|786-4^Mean Corpuscular Hemoglobin Concentration^LN||33.4|g/dL|31.0-37.0|N|||F|||20250818073000
OBX|8|NM|777-3^Platelets^LN||198|10*3/uL|150-400|N|||F|||20250818073000
OBX|9|NM|770-8^Neutrophils %^LN||78.2|%|40.0-70.0|H|||F|||20250818073000
OBX|10|NM|736-9^Lymphocytes %^LN||14.5|%|20.0-40.0|L|||F|||20250818073000
```

---

## 7. ORM^O01 - Radiology order at Johns Hopkins Hospital

```
MSH|^~\&|EPIC|JHHOSP|RADRIS|JHHOSP|20250505103045||ORM^O01^ORM_O01|JHH20250505103045001|P|2.5.1|||AL|NE
PID|1||E92148155^^^EPIC^MRN~64890180^^^JHHMPI^MR||FRAZIER^Marguerite^Diane^^^Mrs.||19620818|F||2028-9^Asian^CDCREC|8870 Colesville Rd^^Salisbury^MD^21804^US^L||^PRN^PH^^^443^5299547||eng^English^ISO6392|M^Married^HL70002|||427-97-9389|||N^Non-Hispanic^HL70189
PV1|1|O|RADJHH^RAD3^A^JHHOSP||||6566192831^Harrington^Breckenridge^W^^MD^^^NPI||RAD^Radiology^JHSERV|||R^Referral^HL70007|||||V80107562^^^JHENC^VN|||||||||||||||||||||||||20250505103000
ORC|NW|ORD801234^EPIC|RAD701234^RADRIS||SC||^^^20250505140000^^R||20250505103045|HCALDWEL^Caldwell^Helena^K^^RT|||20250505103045||JHHOSP|^PRN^PH^^^410^9551234||JOHNS HOPKINS HOSPITAL
OBR|1|ORD801234^EPIC|RAD701234^RADRIS|74177^CT Abdomen and Pelvis with Contrast^CPT||||||||||||6566192831^Harrington^Breckenridge^W^^MD^^^NPI||||||20250505140000|||NI^No Information^HL70507|||^^^20250505140000^^R
DG1|1||R10.9^Unspecified abdominal pain^I10||20250505|W^Working^HL70052
```

---

## 8. ORM^O01 - Laboratory order at University of Maryland St. Joseph Medical Center

```
MSH|^~\&|EPIC|UMSJMC|LABLIS|UMSJMC|20250612085215||ORM^O01^ORM_O01|SJMC20250612085215001|P|2.5.1|||AL|NE
PID|1||E21998547^^^EPIC^MRN~42008891^^^UMMCMPI^MR||BELLAMY^Desmond^Isaiah^^^Mr.||19810307|M||2106-3^White^CDCREC|7208 Belair Rd^^Baltimore^MD^21225^US^L||^PRN^PH^^^443^8104004||eng^English^ISO6392|M^Married^HL70002|||734-19-5783|||N^Non-Hispanic^HL70189
PV1|1|O|LABSJMC^LAB1^A^UMSJMC||||6108903932^Radcliffe^Gresham^R^^MD^^^NPI||MED^Internal Medicine^SJMCSERV|||R^Referral^HL70007|||||V80118473^^^SJMCENC^VN|||||||||||||||||||||||||20250612085200
ORC|NW|ORD901234^EPIC|LAB601234^LABLIS||SC||^^^20250612090000^^R||20250612085215|CUNDERWO^Underwood^Claudette^D^^RN|||20250612085215||UMSJMC|^PRN^PH^^^410^4272000||UM ST JOSEPH MEDICAL CENTER
OBR|1|ORD901234^EPIC|LAB601234^LABLIS|80053^Comprehensive Metabolic Panel^CPT||||20250612085000||||||||6108903932^Radcliffe^Gresham^R^^MD^^^NPI||||||20250612090000|||NI^No Information^HL70507
OBR|2|ORD901234^EPIC|LAB601235^LABLIS|85025^CBC with Differential^CPT||||20250612085000||||||||6108903932^Radcliffe^Gresham^R^^MD^^^NPI||||||20250612090000|||NI^No Information^HL70507
```

---

## 9. SIU^S12 - New appointment scheduled at Johns Hopkins Outpatient Center

```
MSH|^~\&|EPIC|JHOPC|SCHEDMGR|JHOPC|20250714093022||SIU^S12^SIU_S12|OPC20250714093022001|P|2.5.1|||AL|NE
SCH|APT40012345^EPIC|||||MOD^Modification^HL70276|FOLLOWUP^Follow-up Visit^EPICAPT|CARDIOLOGY^Cardiology Clinic^JHSERV|30|MIN|^^^20250721100000^20250721103000|4740981754^Southgate^Conrad^P^^MD^^^NPI|^PRN^PH^^^410^9551234|2519 Fleet St^Southgate^Conrad^P^21224^US||4740981754^Southgate^Conrad^P^^MD^^^NPI|CONFIRMED^Confirmed^HL70278
PID|1||E12518285^^^EPIC^MRN~59012330^^^JHHMPI^MR||XIONG^Nathaniel^Norbert^^^Mr.||19710320|M||2106-3^White^CDCREC|7934 Moravia Rd^^Severna Park^MD^21146^US^L||^PRN^PH^^^410^7773476||eng^English^ISO6392|M^Married^HL70002|||797-86-6023|||H^Hispanic or Latino^HL70189
PV1|1|O|CARDOPC^Southgate^Conrad^JHOPC^^^^CARDOPC||||6161351533^Fairbanks^Dorothea^S^^MD^^^NPI||CAR^Cardiology^JHSERV|||R^Referral^HL70007|||||V80129384^^^JHENC^VN|||||||||||||||||||||||||20250721100000
RGS|1||CARDOPC^Cardiology OPC^JHSERV
AIS|1||CARDFOLLOW^Cardiology Follow-up^EPICAPT|20250721100000|||30|MIN
AIP|1||4740981754^Southgate^Conrad^P^^MD^^^NPI|4018732956||20250721100000|||30|MIN
AIL|1||JHOPC^CARD2^A^JHOPC^^^^CARDOPC||20250721100000|||30|MIN
```

---

## 10. SIU^S14 - Appointment modification at Adventist HealthCare Shady Grove

```
MSH|^~\&|EPIC|AHCSG|SCHEDMGR|AHCSG|20250820141530||SIU^S14^SIU_S12|AHSG20250820141530001|P|2.5.1|||AL|NE
SCH|APT50023456^EPIC|||||MOD^Modification^HL70276|ORTHOFU^Orthopedic Follow-up^EPICAPT|ORTHOPEDICS^Orthopedics Clinic^AHCSERV|20|MIN|^^^20250828143000^20250828145000|9160002344^Carmichael^Randolph^W^^MD^^^NPI|^PRN^PH^^^240^8262000|9901 Medical Center Dr^Carmichael^Randolph^W^20850^US||9160002344^Carmichael^Randolph^W^^MD^^^NPI|RESCHEDULED^Rescheduled^HL70278
PID|1||E50117648^^^EPIC^MRN~63336657^^^AHCMPI^MR||PRUITT^Francesca^Theresa^^^Mrs.||19770624|F||2106-3^White^CDCREC|6045 Hillen Rd^^Washington^DC^20008^US^L||^PRN^PH^^^202^7328838||spa^Spanish^ISO6392|M^Married^HL70002|||524-63-4816|||H^Hispanic or Latino^HL70189
PV1|1|O|ORTHOSG^ORT1^A^AHCSG^^^^ORTHOSG||||9160002344^Carmichael^Randolph^W^^MD^^^NPI||ORT^Orthopedics^AHCSERV|||R^Referral^HL70007|||||V80134271^^^AHCENC^VN|||||||||||||||||||||||||20250828143000
RGS|1||ORTHOSG^Orthopedics SG^AHCSERV
AIS|1||ORTHOFU^Orthopedic Follow-up^EPICAPT|20250828143000|||20|MIN
AIP|1||9160002344^Carmichael^Randolph^W^^MD^^^NPI|5263748190||20250828143000|||20|MIN
```

---

## 11. MDM^T02 - Clinical document notification with embedded PDF at UMMC

```
MSH|^~\&|EPIC|UMMC|DOCSYS|UMMC|20250927154022||MDM^T02^MDM_T02|UMMC20250927154022001|P|2.5.1|||AL|NE
EVN|T02|20250927154000
PID|1||E95409113^^^EPIC^MRN~62849391^^^UMMCMPI^MR||MCARTHUR^Ibrahim^Zachary^^^Mr.||19690412|M||2054-5^Black or African American^CDCREC|6319 Loch Raven Blvd^^Bowie^MD^20716^US^L||^PRN^PH^^^443^5584740||eng^English^ISO6392|D^Divorced^HL70002|||602-56-7764|||N^Non-Hispanic^HL70189
PV1|1|I|PULM5^5310^A^UMMC^^^^PULM5||||3143595823^Harrington^Breckenridge^R^^MD^^^NPI||PUL^Pulmonology^UMMCSERV|||||||||V80145923^^^UMMCENC^VN|||||||||||||||||||||||||20250925080000
TXA|1|HP^History and Physical^HL70270|TX^Text^HL70191||20250925120000||||||6374859201^Kessler^Martin^B^^MD^^^NPI|||||AU^Authenticated^HL70271
OBX|1|ED|HP-DOC^History and Physical Document^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F|||20250925120000
```

---

## 12. MDM^T02 - Discharge summary document at Johns Hopkins Hospital

```
MSH|^~\&|EPIC|JHHOSP|DOCSYS|JHHOSP|20250803171245||MDM^T02^MDM_T02|JHH20250803171245001|P|2.5.1|||AL|NE
EVN|T02|20250803171200
PID|1||E83441972^^^EPIC^MRN~87401629^^^JHHMPI^MR||RAMACHANDRAN^Paloma^Ernestine^^^Mrs.||19550915|F||2028-9^Asian^CDCREC|4238 Calvert St^^College Park^MD^20740^US^L||^PRN^PH^^^240^4116976||vie^Vietnamese^ISO6392|W^Widowed^HL70002|||801-27-3992|||N^Non-Hispanic^HL70189
PV1|1|I|GER7^7104^A^JHHOSP^^^^GER7||||2335655644^Radcliffe^Gresham^P^^MD^^^NPI||GER^Geriatrics^JHSERV|||||||||V80156238^^^JHENC^VN||DI^Discharged to Home^HL70112||||||||||||||||||||||||20250730090000|20250803171200
TXA|1|DS^Discharge Summary^HL70270|TX^Text^HL70191||20250803160000||||||7485960312^Livingston^Howard^E^^MD^^^NPI|||||AU^Authenticated^HL70271
OBX|1|TX|18842-5^Discharge Summary^LN||Patient: RAMACHANDRAN, Paloma Ernestine. Admitted 07/30/2025 for community-acquired pneumonia. Treated with IV ceftriaxone and azithromycin, transitioned to oral levofloxacin. Chest X-ray on discharge shows improving bilateral infiltrates. Discharge to home with 7-day course of oral antibiotics and follow-up in 2 weeks.||||||F|||20250803160000
```

---

## 13. VXU^V04 - Immunization record at UM Capital Region Health

```
MSH|^~\&|EPIC|UMCRH|IMMUNET|MDIMMS|20250915101530||VXU^V04^VXU_V04|CRHL20250915101530001|P|2.5.1|||AL|NE
PID|1||E78412125^^^EPIC^MRN~40022956^^^UMMCMPI^MR||KENWORTHY^Monique^Diane^^^Ms.||19960318|F||2106-3^White^CDCREC|3814 Liberty Heights Ave^^Waldorf^MD^20602^US^L||^PRN^PH^^^240^2723214||spa^Spanish^ISO6392|S^Single^HL70002|||473-54-9306|||H^Hispanic or Latino^HL70189
PD1|||UM CAPITAL REGION HEALTH^^40001|7679941602^Fairbanks^Ellsworth^C^^MD^^^NPI
NK1|1|NORWOOD^Preston^I|FTH^Father^HL70063|3814 Liberty Heights Ave^^Waldorf^MD^20602^US|^PRN^PH^^^240^9912200||EC^Emergency Contact^HL70131
PV1|1|O|IMMCRH^IMM1^A^UMCRH^^^^IMMCRH||||7679941602^Fairbanks^Ellsworth^C^^MD^^^NPI||PCP^Primary Care^CRHSERV|||||||||V80167294^^^CRHENC^VN|||||||||||||||||||||||||20250915101500
RXA|0|1|20250915101500|20250915101500|141^Influenza, seasonal, injectable, preservative free^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001||||||M7234AA||SKB^GlaxoSmithKline^MVX|||CP^Complete^HL70322
OBX|1|CE|30956-7^Vaccine Type^LN||141^Influenza, seasonal, injectable, preservative free^CVX||||||F
OBX|2|CE|59779-9^Immunization Schedule Used^LN||VXC16^ACIP^CDCPHINVS||||||F
RXA|0|1|20250315100000|20250315100000|208^SARS-COV-2 (COVID-19) vaccine, mRNA, spike protein, LNP, bivalent, pres free, 30 mcg/0.3 mL dose^CVX|0.3|mL^milliliter^UCUM||00^New immunization record^NIP001||||||FA4582BB||MOD^Moderna US Inc^MVX|||CP^Complete^HL70322
```

---

## 14. ORU^R01 - Comprehensive metabolic panel at Howard County General Hospital

```
MSH|^~\&|EPIC|HCGH|LABSYS|HCGH|20250422081045||ORU^R01^ORU_R01|HCGH20250422081045001|P|2.5.1|||AL|NE
PID|1||E73512337^^^EPIC^MRN~49639577^^^JHHMPI^MR||NAKAMURA^Carlton^Philip^^^Mr.||19780614|M||2106-3^White^CDCREC|4020 Washington Blvd^^Lutherville^MD^21093^US^L||^PRN^PH^^^410^9145429||eng^English^ISO6392|M^Married^HL70002|||263-24-9840|||N^Non-Hispanic^HL70189
PV1|1|O|LABHCGH^LAB2^A^HCGH^^^^LABHCGH||||2911927920^Northcutt^Standford^M^^MD^^^NPI||MED^Internal Medicine^HCGHSERV|||||||||V80178605^^^HCGHENC^VN|||||||||||||||||||||||||20250422080000
ORC|RE|ORD110234^EPIC|LAB710234^LABSYS||CM||^^^20250422081000^^R||20250422081045|SCOVINGT^Covington^Simone^O^^MT|||20250422081045||HCGH
OBR|1|ORD110234^EPIC|LAB710234^LABSYS|80053^Comprehensive Metabolic Panel^CPT||||20250422070000||||||||2911927920^Northcutt^Standford^M^^MD^^^NPI||||||20250422081000|||F
OBX|1|NM|2345-7^Glucose^LN||102|mg/dL|74-106|N|||F|||20250422080000
OBX|2|NM|3094-0^BUN^LN||18|mg/dL|6-24|N|||F|||20250422080000
OBX|3|NM|2160-0^Creatinine^LN||1.1|mg/dL|0.7-1.3|N|||F|||20250422080000
OBX|4|NM|2951-2^Sodium^LN||141|mmol/L|136-145|N|||F|||20250422080000
OBX|5|NM|2823-3^Potassium^LN||4.3|mmol/L|3.5-5.1|N|||F|||20250422080000
OBX|6|NM|2075-0^Chloride^LN||103|mmol/L|98-106|N|||F|||20250422080000
OBX|7|NM|2028-9^CO2^LN||25|mmol/L|21-32|N|||F|||20250422080000
OBX|8|NM|2000-8^Calcium^LN||9.4|mg/dL|8.5-10.5|N|||F|||20250422080000
OBX|9|NM|2885-2^Total Protein^LN||7.1|g/dL|6.0-8.3|N|||F|||20250422080000
OBX|10|NM|1751-7^Albumin^LN||4.2|g/dL|3.5-5.5|N|||F|||20250422080000
OBX|11|NM|1975-2^Total Bilirubin^LN||0.8|mg/dL|0.1-1.2|N|||F|||20250422080000
OBX|12|NM|6768-6^Alkaline Phosphatase^LN||72|U/L|44-147|N|||F|||20250422080000
OBX|13|NM|1742-6^ALT^LN||28|U/L|7-56|N|||F|||20250422080000
OBX|14|NM|1920-8^AST^LN||22|U/L|10-40|N|||F|||20250422080000
```

---

## 15. ORU^R01 - Radiology result with embedded PDF at Johns Hopkins Hospital

```
MSH|^~\&|EPIC|JHHOSP|RADSYS|JHHOSP|20250611152230||ORU^R01^ORU_R01|JHH20250611152230001|P|2.5.1|||AL|NE
PID|1||E53418403^^^EPIC^MRN~19994276^^^JHHMPI^MR||WAVERLY^Dorothea^Wanda^^^Mrs.||19640723|F||2054-5^Black or African American^CDCREC|3770 East-West Hwy^^Temple Hills^MD^20748^US^L||^PRN^PH^^^410^7913017||eng^English^ISO6392|M^Married^HL70002|||354-60-4096|||N^Non-Hispanic^HL70189
PV1|1|O|RADJHH^RAD5^A^JHHOSP||||4265200250^Pemberton^Carleton^L^^MD^^^NPI||RAD^Radiology^JHSERV|||||||||V80189724^^^JHENC^VN|||||||||||||||||||||||||20250611150000
ORC|RE|ORD120234^EPIC|RAD810234^RADSYS||CM||^^^20250611152200^^R||20250611152230|LMARCHAN^Marchand^Lorraine^B^^RT|||20250611152230||JHHOSP
OBR|1|ORD120234^EPIC|RAD810234^RADSYS|71260^CT Chest with Contrast^CPT||||20250611140000||||||||4265200250^Pemberton^Carleton^L^^MD^^^NPI||||||20250611152200|||F
OBX|1|TX|36643-5^Chest CT Report^LN||FINDINGS: No pulmonary embolism identified. Bilateral pleural effusions, small, unchanged. Ground-glass opacities in bilateral lower lobes, improved from prior. Heart size normal. No mediastinal lymphadenopathy. IMPRESSION: 1. No pulmonary embolism. 2. Improving bilateral lower lobe ground-glass opacities. 3. Stable small bilateral pleural effusions.||||||F|||20250611151500
OBX|2|ED|PDF-RAD^Radiology Report PDF^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PCAvRjEgNSAwIFIgPj4KPj4KPj4KZW5kb2Jq||||||F|||20250611151500
```

---

## 16. ORU^R01 - Troponin result at MedStar Union Memorial Hospital

```
MSH|^~\&|EPIC|MSUMH|LABSYS|MSUMH|20250301044530||ORU^R01^ORU_R01|MSUMH20250301044530001|P|2.5.1|||AL|NE
PID|1||E94458806^^^EPIC^MRN~77230079^^^MSMPI^MR||CHEVALIER^Harlan^Brent^^^Mr.||19530908|M||2106-3^White^CDCREC|5721 Frederick Ave^^Pasadena^MD^21122^US^L||^PRN^PH^^^240^2299609||eng^English^ISO6392|M^Married^HL70002|||338-37-6396|||N^Non-Hispanic^HL70189
PV1|1|E|EDMSUMH^ED05^A^MSUMH^^^^EDMSUMH||||8098002448^Remington^Halstead^C^^MD^^^NPI||EM^Emergency Medicine^MSUMHSERV|||||||||V80190836^^^MSUMHENC^VN|||||||||||||||||||||||||20250301040000
ORC|RE|ORD130234^EPIC|LAB810234^LABSYS||CM||^^^20250301044500^^R||20250301044530|PDESAI^Desai^Paloma^G^^MT|||20250301044530||MSUMH
OBR|1|ORD130234^EPIC|LAB810234^LABSYS|49563-0^Troponin I High Sensitivity^LN||||20250301041500||||||||8098002448^Remington^Halstead^C^^MD^^^NPI||||||20250301044500|||F
OBX|1|NM|49563-0^Troponin I High Sensitivity^LN||245|ng/L|0-34|H|||F|||20250301044000
OBX|2|TX|49563-0^Troponin I Interpretation^LN||Elevated troponin I consistent with myocardial injury. Clinical correlation recommended. Serial troponin measurements advised.||||||F|||20250301044000
```

---

## 17. ADT^A02 - Patient transfer at Sinai Hospital (LifeBridge Health)

```
MSH|^~\&|EPIC|SINAIBALT|ADT_RECV|SINAIBALT|20250418112045||ADT^A02^ADT_A02|SIN20250418112045001|P|2.5.1|||AL|NE
EVN|A02|20250418112000|||MHARRIS^Harris^Michelle^D^^RN|20250418111500
PID|1||E53030269^^^EPIC^MRN~21983403^^^LBHMPI^MR||HERRERA^Sterling^Anthony^^^Mr.||19820125|M||2054-5^Black or African American^CDCREC|6829 Gwynns Falls Pkwy^^Annapolis^MD^21401^US^L||^PRN^PH^^^410^5795204||eng^English^ISO6392|S^Single^HL70002|||577-75-5043|||N^Non-Hispanic^HL70189
PV1|1|I|5ICU^5104^A^SINAIBALT^^^^5ICU||||6962552353^Fairbanks^Ellsworth^M^^MD^^^NPI|2004760403^Haverford^Madeleine^V^^MD^^^NPI|MED^Medicine^LBHSERV|||T^Transfer^HL70007|||||V80201537^^^LBHENC^VN|||||||||||||||||3TELE^3208^B^SINAIBALT^^^^3TELE||||||20250418112000
```

---

## 18. ORU^R01 - Microbiology culture result at University of Maryland Medical Center

```
MSH|^~\&|EPIC|UMMC|MICROSYS|UMMC|20251002091530||ORU^R01^ORU_R01|UMMC20251002091530001|P|2.5.1|||AL|NE
PID|1||E54378090^^^EPIC^MRN~49965750^^^UMMCMPI^MR||SUTHERLAND^Theodora^Florence^^^Ms.||19910505|F||2054-5^Black or African American^CDCREC|9100 Jones Bridge Rd^^Frederick^MD^21701^US^L||^PRN^PH^^^301^8778098||eng^English^ISO6392|S^Single^HL70002|||208-74-1753|||N^Non-Hispanic^HL70189
PV1|1|I|MED4^4118^A^UMMC^^^^MED4||||3133636134^Northcutt^Standford^L^^MD^^^NPI||MED^Internal Medicine^UMMCSERV|||||||||V80212648^^^UMMCENC^VN|||||||||||||||||||||||||20250930143000
ORC|RE|ORD140234^EPIC|MICRO910234^MICROSYS||CM||^^^20251002091500^^R||20251002091530|VLEBLANC^Leblanc^Valentina^Z^^MT|||20251002091530||UMMC
OBR|1|ORD140234^EPIC|MICRO910234^MICROSYS|87081^Culture, Urine^CPT||||20250930160000||||||||3133636134^Northcutt^Standford^L^^MD^^^NPI||||||20251002091500|||F
OBX|1|TX|6463-4^Bacteria identified^LN||Escherichia coli >100,000 CFU/mL||||||F|||20251002090000
OBX|2|TX|18907-6^Susceptibility Panel^LN||Ampicillin: R, Ciprofloxacin: S, Nitrofurantoin: S, Trimethoprim/Sulfamethoxazole: R, Ceftriaxone: S, Gentamicin: S||||||F|||20251002090000
```

---

## 19. VXU^V04 - Pediatric immunization at Johns Hopkins Children's Center

```
MSH|^~\&|EPIC|JHCC|IMMUNET|MDIMMS|20250210101000||VXU^V04^VXU_V04|JHCC20250210101000001|P|2.5.1|||AL|NE
PID|1||E25236919^^^EPIC^MRN~61389561^^^JHHMPI^MR||AFOLABI^Percival^Kenneth^^^Master||20230810|M||2106-3^White^CDCREC|3560 Crain Hwy^^Laurel^MD^20707^US^L||^PRN^PH^^^443^4732088||eng^English^ISO6392|S^Single^HL70002|||575-19-1761|||N^Non-Hispanic^HL70189
PD1|||JOHNS HOPKINS CHILDREN'S CENTER^^50001|7455806306^Pemberton^Carleton^C^^MD^^^NPI
NK1|1|WHITFIELD^Estelle^B|MTH^Mother^HL70063|3560 Crain Hwy^^Laurel^MD^20707^US|^PRN^PH^^^443^8614659||EC^Emergency Contact^HL70131
PV1|1|O|PEDJHCC^PED3^A^JHCC^^^^PEDJHCC||||7455806306^Pemberton^Carleton^C^^MD^^^NPI||PED^Pediatrics^JHSERV|||||||||V80223759^^^JHCCENC^VN|||||||||||||||||||||||||20250210101000
RXA|0|1|20250210101000|20250210101000|110^DTaP^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001||||||U8832CC||PMC^sanofi pasteur^MVX|||CP^Complete^HL70322
OBX|1|CE|30956-7^Vaccine Type^LN||110^DTaP^CVX||||||F
OBX|2|CE|59779-9^Immunization Schedule Used^LN||VXC16^ACIP^CDCPHINVS||||||F
RXA|0|1|20250210101500|20250210101500|10^IPV^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001||||||V4455DD||PMC^sanofi pasteur^MVX|||CP^Complete^HL70322
RXA|0|1|20250210102000|20250210102000|03^MMR^CVX|0.5|mL^milliliter^UCUM||00^New immunization record^NIP001||||||K9988EE||MSD^Merck and Co Inc^MVX|||CP^Complete^HL70322
```

---

## 20. ORU^R01 - Echocardiogram result at Johns Hopkins Hospital

```
MSH|^~\&|EPIC|JHHOSP|ECHOSYS|JHHOSP|20250728143045||ORU^R01^ORU_R01|JHH20250728143045001|P|2.5.1|||AL|NE
PID|1||E49062049^^^EPIC^MRN~89474833^^^JHHMPI^MR||WHITFIELD^Alonso^Philip^^^Mr.||19580302|M||2054-5^Black or African American^CDCREC|1423 Harford Rd^^Baltimore^MD^21218^US^L||^PRN^PH^^^410^8392582||eng^English^ISO6392|M^Married^HL70002|||452-57-9059|||N^Non-Hispanic^HL70189
PV1|1|I|CARD3^3206^A^JHHOSP^^^^CARD3||||6836010510^Remington^Halstead^M^^MD^^^NPI||CAR^Cardiology^JHSERV|||||||||V80234860^^^JHENC^VN|||||||||||||||||||||||||20250726093000
ORC|RE|ORD150234^EPIC|ECHO910234^ECHOSYS||CM||^^^20250728143000^^R||20250728143045|BCHANDRA^Chandra^Brianne^T^^RDCS|||20250728143045||JHHOSP
OBR|1|ORD150234^EPIC|ECHO910234^ECHOSYS|93306^Echocardiography, Transthoracic^CPT||||20250728100000||||||||6836010510^Remington^Halstead^M^^MD^^^NPI||||||20250728143000|||F
OBX|1|NM|18043-0^Left Ventricular Ejection Fraction^LN||35|%|55-70|L|||F|||20250728130000
OBX|2|NM|29434-1^Left Ventricular End-Diastolic Diameter^LN||6.2|cm|3.5-5.6|H|||F|||20250728130000
OBX|3|NM|29436-6^Left Ventricular End-Systolic Diameter^LN||4.8|cm|2.0-4.0|H|||F|||20250728130000
OBX|4|TX|59462-2^Echocardiographic Impression^LN||IMPRESSION: 1. Moderate to severe systolic dysfunction with estimated LVEF 35%. 2. Dilated left ventricle. 3. Grade II (moderate) diastolic dysfunction. 4. Mild to moderate mitral regurgitation. 5. Mild tricuspid regurgitation with estimated RVSP 38 mmHg. 6. No pericardial effusion.||||||F|||20250728130000
```
