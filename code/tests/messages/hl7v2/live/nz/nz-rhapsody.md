# Rhapsody Integration Engine - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Patient admission at Waikato DHB

```
MSH|^~\&|PAS|WAIKATO_DHB|RHAPSODY|RIE|20250312091500||ADT^A01^ADT_A01|MSG00001|P|2.4|||AL|NE|NZL
EVN|A01|20250312091500|||JCLAYTON^Clayton^Jasmine^^^Dr
PID|1||XKR4128^^^NZ_MOH^NHI||TE WHARE^Aroha^Maraea^^Ms||19870415|F|||38 Boundary Road^^Hamilton^^3204^NZL||^PRN^PH^^64^7^8326184|||||||||21^^^WAIKATO_DHB^DI
NK1|1|TE WHARE^Wiremu^Tane^^Mr|SPO^Spouse||^PRN^PH^^64^7^8326185
PV1|1|I|W4^401^A^^^WAIKATO_DHB||||DRPATEL^Patel^Rajeev^^^Dr^MD|DRMURRAY^Murraysmith^Colin^^^Dr^MD||MED||||7|||DRPATEL^Patel^Rajeev^^^Dr^MD|IP||||||||||||||||||WAIKATO_DHB||ADM|||20250312091500
PV2|||^Chest pain, unspecified|||||20250315|3
IN1|1|SCHI^Southern Cross Health Insurance||Southern Cross Health Insurance^^Auckland^^NZL|||||||||||||TE WHARE^Aroha^Maraea^^Ms|SELF|19870415|38 Boundary Road^^Hamilton^^3204^NZL
```

---

## 2. ADT^A04 - Patient registration at Counties Manukau DHB

```
MSH|^~\&|CONCERTO|CMDHB|RHAPSODY|RIE|20250218143022||ADT^A04^ADT_A01|MSG00002|P|2.4|||AL|NE|NZL
EVN|A04|20250218143022|||ADMIN01^Reception^Main
PID|1||PMB7395^^^NZ_MOH^NHI||KUMARASAMY^Priya^Indira^^Mrs||19920823|F|||94 Chapel Road^^Flat Bush^Auckland^2019^NZL||^PRN^PH^^64^9^2681547|^WPN^PH^^64^9^2681548||||||||21^^^CMDHB^DI
PV1|1|O|ED^MAIN^001^^^CMDHB||||DRCHEN^Chen^Wei Ling^^^Dr^MD|||EMR||||1|||DRCHEN^Chen^Wei Ling^^^Dr^MD|OP||||||||||||||||||CMDHB||REG|||20250218143022
```

---

## 3. ADT^A08 - Patient update with NHI merge at Capital and Coast DHB

```
MSH|^~\&|PAS|CCDHB|RHAPSODY|RIE|20250409155530||ADT^A08^ADT_A01|MSG00003|P|2.4|||AL|NE|NZL
EVN|A08|20250409155530|||SYSADMIN^System^Admin
PID|1||CFL9027^^^NZ_MOH^NHI||WILLIAMSON^James^Reginald^^Mr||19650710|M|||74 Featherston Street^^Wellington^^6011^NZL||^PRN^PH^^64^4^4728136|^WPN^PH^^64^4^4725419||||||||21^^^CCDHB^DI
PV1|1|O|OPD^CLINIC3^002^^^CCDHB||||DRLEE^Leeson^Min^^^Dr^MD|||GEN||||1|||DRLEE^Leeson^Min^^^Dr^MD|OP||||||||||||||||||CCDHB||UPD|||20250409155530
MRG|VWB6391^^^NZ_MOH^NHI
```

---

## 4. ADT^A03 - Patient discharge at Canterbury DHB

```
MSH|^~\&|PAS|CDHB|RHAPSODY|RIE|20250320163000||ADT^A03^ADT_A03|MSG00004|P|2.4|||AL|NE|NZL
EVN|A03|20250320163000|||DRBROWN^Brownlee^Stephen^^^Dr
PID|1||DSE3478^^^NZ_MOH^NHI||HANSEN^Katrina^Birgit^^Ms||19780302|F|||52 Wharenui Road^^Christchurch^^8041^NZL||^PRN^PH^^64^3^3641820|||||||||21^^^CDHB^DI
PV1|1|I|SURG^212^B^^^CDHB||||DRBROWN^Brownlee^Stephen^^^Dr^MD|||SUR||||7|||DRBROWN^Brownlee^Stephen^^^Dr^MD|IP||||||||||||||||||CDHB||DIS|||20250320163000
DG1|1||K80.2^Gallbladder calculus without cholecystitis^I10||20250317|A
```

---

## 5. ORU^R01 - Laboratory result from Canterbury Health Labs

```
MSH|^~\&|CHL_LIS|CDHB|RHAPSODY|RIE|20250401102345||ORU^R01^ORU_R01|MSG00005|P|2.5|||AL|NE|NZL
PID|1||GHN5821^^^NZ_MOH^NHI||JOHNSEN^Mark^Reuben^^Mr||19810519|M|||83 Memorial Avenue^^Christchurch^^8014^NZL||^PRN^PH^^64^3^3526184
PV1|1|O|OUTLAB^MAIN^001^^^CDHB||||DRWRIGHT^Wrightson^Helen^^^Dr^MD
ORC|RE|ORD100234|LAB200567||CM||||20250401090000|||DRWRIGHT^Wrightson^Helen^^^Dr^MD
OBR|1|ORD100234|LAB200567|FBC^Full Blood Count^NZPOCS||20250401080000|20250401090000|||||||20250401090000||DRWRIGHT^Wrightson^Helen^^^Dr^MD||||||20250401102345|||F
OBX|1|NM|HGB^Haemoglobin^NZPOCS||145|g/L|130-175|N|||F|||20250401102345
OBX|2|NM|WBC^White Blood Cell Count^NZPOCS||7.2|x10*9/L|4.0-11.0|N|||F|||20250401102345
OBX|3|NM|PLT^Platelet Count^NZPOCS||230|x10*9/L|150-400|N|||F|||20250401102345
OBX|4|NM|RBC^Red Blood Cell Count^NZPOCS||4.8|x10*12/L|4.5-5.5|N|||F|||20250401102345
OBX|5|NM|HCT^Haematocrit^NZPOCS||0.43|L/L|0.40-0.52|N|||F|||20250401102345
```

---

## 6. ORU^R01 - Radiology report with embedded image from Auckland DHB

```
MSH|^~\&|PACS|ADHB|RHAPSODY|RIE|20250415081200||ORU^R01^ORU_R01|MSG00006|P|2.5|||AL|NE|NZL
PID|1||LRX2087^^^NZ_MOH^NHI||MITCHELLSON^Sarah^Charlotte^^Mrs||19760814|F|||29 Symonds Street^^Auckland^^1010^NZL||^PRN^PH^^64^9^3071856
PV1|1|O|RADIOL^MAIN^001^^^ADHB||||DRPINTO^Pintado^Maria^^^Dr^MD
ORC|RE|RAD300456|IMG400789||CM||||20250415070000|||DRPINTO^Pintado^Maria^^^Dr^MD
OBR|1|RAD300456|IMG400789|XRCXR^Chest X-Ray^RADLEX||20250415070000|20250415073000|||||||20250415073000||DRPINTO^Pintado^Maria^^^Dr^MD||||||20250415081200|||F
OBX|1|FT|RADRPT^Radiology Report^LN||Heart size is normal. Lungs are clear. No pleural effusion. No pneumothorax. Mild degenerative changes of the thoracic spine.||||||F|||20250415081200
OBX|2|ED|IMG^Radiology Image^LN||^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAFBABAAAAAAAAAAAAAAAAAAAACf/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKoA/9k=||||||F
```

---

## 7. ORU^R01 - Microbiology result with embedded PDF from Southern DHB

```
MSH|^~\&|MICRO_LIS|SDHB|RHAPSODY|RIE|20250422134500||ORU^R01^ORU_R01|MSG00007|P|2.5|||AL|NE|NZL
PID|1||PWQ8413^^^NZ_MOH^NHI||NGATA^Hemi^Tane^^Mr||19590127|M|||52 Tay Street^^Invercargill^^9810^NZL||^PRN^PH^^64^3^2148261
PV1|1|I|WARD2^106^A^^^SDHB||||DRJONES^Jonsson^Patricia^^^Dr^MD
ORC|RE|ORD200345|LAB300678||CM||||20250422100000|||DRJONES^Jonsson^Patricia^^^Dr^MD
OBR|1|ORD200345|LAB300678|BCUL^Blood Culture^NZPOCS||20250422090000|20250422100000|||||||20250422100000||DRJONES^Jonsson^Patricia^^^Dr^MD||||||20250422134500|||F
OBX|1|ST|ORGANISM^Organism Identified^NZPOCS||Staphylococcus aureus||||||F|||20250422134500
OBX|2|ST|SUSCEPT^Antibiotic Susceptibility^NZPOCS||Flucloxacillin: Sensitive, Vancomycin: Sensitive, Erythromycin: Resistant||||||F|||20250422134500
OBX|3|ED|PDF^Microbiology Report^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDE1MCAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjIwNAolJUVPRgo=||||||F
```

---

## 8. ORM^O01 - Radiology order from Bay of Plenty DHB

```
MSH|^~\&|CONCERTO|BOPDHB|RHAPSODY|RIE|20250305110000||ORM^O01^ORM_O01|MSG00008|P|2.4|||AL|NE|NZL
PID|1||TBR1064^^^NZ_MOH^NHI||TAITUHA^Rebecca^Annabelle^^Ms||19881103|F|||64 Eleventh Avenue^^Tauranga^^3110^NZL||^PRN^PH^^64^7^5712483
PV1|1|O|ED^BAY1^003^^^BOPDHB||||DRSMITH^Smithson^David^^^Dr^MD|||EMR||||1|||DRSMITH^Smithson^David^^^Dr^MD|OP
ORC|NW|RAD400123||||N||||20250305110000|||DRSMITH^Smithson^David^^^Dr^MD
OBR|1|RAD400123||CTABD^CT Abdomen and Pelvis^RADLEX||20250305110000|||||||||20250305110000||DRSMITH^Smithson^David^^^Dr^MD|||||||||||^Acute abdominal pain, query appendicitis
```

---

## 9. ORM^O01 - Laboratory order from Hawke's Bay DHB

```
MSH|^~\&|PAS|HBDHB|RHAPSODY|RIE|20250228083000||ORM^O01^ORM_O01|MSG00009|P|2.4|||AL|NE|NZL
PID|1||MNV4521^^^NZ_MOH^NHI||MAAKA^Tane^Hone^^Mr||19700605|M|||45 Karamu Road North^^Hastings^^4122^NZL||^PRN^PH^^64^6^8782143
PV1|1|I|WARD5^312^A^^^HBDHB||||DRTAYLOR^Taylorson^Emma^^^Dr^MD|||MED||||7|||DRTAYLOR^Taylorson^Emma^^^Dr^MD|IP
ORC|NW|LAB500234||||N||||20250228083000|||DRTAYLOR^Taylorson^Emma^^^Dr^MD
OBR|1|LAB500234||LIPID^Lipid Panel^NZPOCS||20250228083000|||||||||20250228083000||DRTAYLOR^Taylorson^Emma^^^Dr^MD
OBR|2|LAB500234||HBA1C^Glycated Haemoglobin^NZPOCS||20250228083000|||||||||20250228083000||DRTAYLOR^Taylorson^Emma^^^Dr^MD
OBR|3|LAB500234||TSH^Thyroid Stimulating Hormone^NZPOCS||20250228083000|||||||||20250228083000||DRTAYLOR^Taylorson^Emma^^^Dr^MD
```

---

## 10. SIU^S12 - Outpatient appointment notification at MidCentral DHB

```
MSH|^~\&|BOOKING|MCDHB|RHAPSODY|RIE|20250510094500||SIU^S12^SIU_S12|MSG00010|P|2.5|||AL|NE|NZL
SCH|APT100345||||||ROUTINE^Routine^^^ROUTINE|60|MIN|^^^20250520100000^20250520110000|||||DRFLORES^Florey^Marisol^^^Dr^MD|^PRN^PH^^64^6^3508712|CARDIOL^Cardiology Clinic^^MCDHB|||DRFLORES^Florey^Marisol^^^Dr^MD|^PRN^PH^^64^6^3508712|CARDIOL^Cardiology Clinic^^MCDHB|BOOKED
PID|1||WBJ7028^^^NZ_MOH^NHI||WIREMU^Nikau^Pirimia^^Mr||19550318|M|||27 Russell Street^^Palmerston North^^4410^NZL||^PRN^PH^^64^6^3568241
PV1|1|O|CARDIOL^CLINIC1^001^^^MCDHB||||DRFLORES^Florey^Marisol^^^Dr^MD
AIS|1|APT100345|CARDCON^Cardiology Consultation^LOCAL|20250520100000|60|MIN
AIG|1|APT100345|DRFLORES^Florey^Marisol^^^Dr^MD
AIL|1|APT100345|CARDIOL^CLINIC1^001^^^MCDHB
```

---

## 11. SIU^S14 - Appointment modification at Northland DHB

```
MSH|^~\&|PAS|NDHB|RHAPSODY|RIE|20250425153000||SIU^S14^SIU_S12|MSG00011|P|2.5|||AL|NE|NZL
SCH|APT200456||||||ROUTINE^Routine^^^ROUTINE|30|MIN|^^^20250505140000^20250505143000|||||DRKAUR^Kaur^Manpreet^^^Dr^MD|^PRN^PH^^64^9^4304182|ORTHO^Orthopaedics^^NDHB|||DRKAUR^Kaur^Manpreet^^^Dr^MD|^PRN^PH^^64^9^4304182|ORTHO^Orthopaedics^^NDHB|BOOKED
PID|1||CXP3590^^^NZ_MOH^NHI||EDWARDSON^George^Wilfred^^Mr||19450712|M|||52 Mill Road^^Whangarei^^0110^NZL||^PRN^PH^^64^9^4308217
PV1|1|O|ORTHO^CLINIC2^002^^^NDHB||||DRKAUR^Kaur^Manpreet^^^Dr^MD
AIS|1|APT200456|ORTHFUP^Orthopaedic Follow-Up^LOCAL|20250505140000|30|MIN
```

---

## 12. MDM^T02 - Clinical document notification at Waitemata DHB

```
MSH|^~\&|ECMS|WDHB|RHAPSODY|RIE|20250412091000||MDM^T02^MDM_T02|MSG00012|P|2.5|||AL|NE|NZL
EVN|T02|20250412091000
PID|1||SBR8159^^^NZ_MOH^NHI||HARAWIRA^Mereana^Kahurangi^^Mrs||19680924|F|||74 Lake Road^^Devonport^Auckland^0624^NZL||^PRN^PH^^64^9^4459128
PV1|1|O|RESP^CLINIC1^001^^^WDHB||||DRWONG^Wongsatit^Andrew^^^Dr^MD
TXA|1|CN^Consultation Note^HL7|FT^Formatted Text^HL7|20250412091000||20250412090000|||||DRWONG^Wongsatit^Andrew^^^Dr^MD|||DOC300567||AU^Authenticated^HL7|||AV^Available^HL7
OBX|1|FT|18842-5^Discharge Summary^LN||Patient seen for follow-up of moderate persistent asthma. Spirometry shows FEV1 78% predicted, stable from prior visit. Continue Seretide 250/50 twice daily. Review in 3 months. Referral to pulmonary rehabilitation discussed.||||||F
```

---

## 13. MDM^T06 - Addendum to clinical document at Hutt Valley DHB

```
MSH|^~\&|ECMS|HVDHB|RHAPSODY|RIE|20250418142200||MDM^T06^MDM_T06|MSG00013|P|2.5|||AL|NE|NZL
EVN|T06|20250418142200
PID|1||KFA2647^^^NZ_MOH^NHI||SMITHSON^Daniel^Joel^^Mr||19830216|M|||38 Stokes Valley Road^^Lower Hutt^^5010^NZL||^PRN^PH^^64^4^5605281
PV1|1|I|WARD3^205^B^^^HVDHB||||DRNAIR^Nair^Vikrant^^^Dr^MD
TXA|1|AD^Addendum^HL7|FT^Formatted Text^HL7|20250418142200||20250418140000|||||DRNAIR^Nair^Vikrant^^^Dr^MD|||||AU^Authenticated^HL7|||AV^Available^HL7||DOC400678
OBX|1|FT|ADDENDUM^Clinical Addendum^LN||Addendum: Echocardiogram results now available. LVEF 55%, no valvular abnormalities. Mildly elevated right ventricular systolic pressure at 38 mmHg. No pericardial effusion. Will continue current management plan.||||||F
```

---

## 14. ACK - General acknowledgment from Rhapsody

```
MSH|^~\&|RHAPSODY|RIE|PAS|WAIKATO_DHB|20250312091501||ACK^A01^ACK|ACK00001|P|2.4|||AL|NE|NZL
MSA|AA|MSG00001||
```

---

## 15. ACK - Application reject acknowledgment from Rhapsody

```
MSH|^~\&|RHAPSODY|RIE|CHL_LIS|CDHB|20250401102400||ACK^R01^ACK|ACK00002|P|2.5|||AL|NE|NZL
MSA|AR|MSG99999||Required field PID-3 (NHI number) is missing
ERR|^^^207^Application internal error^HL70357||||E|100^Required field missing^HL70533|||PID-3 NHI identifier is mandatory for all NZ clinical messages
```

---

## 16. QBP^Q22 - Patient demographics query by NHI

```
MSH|^~\&|PAS|ADHB|RHAPSODY|RIE|20250420100000||QBP^Q22^QBP_Q21|MSG00016|P|2.5|||AL|NE|NZL
QPD|Q22^Find Candidates^HL7|QRY100345|@PID.3.1^YHQ4926^NHI
RCP|I|1^RD
```

---

## 17. RSP^K22 - Patient demographics response with NHI match

```
MSH|^~\&|RHAPSODY|RIE|PAS|ADHB|20250420100001||RSP^K22^RSP_K21|MSG00017|P|2.5|||AL|NE|NZL
MSA|AA|MSG00016
QAK|QRY100345|OK|Q22^Find Candidates^HL7|1
QPD|Q22^Find Candidates^HL7|QRY100345|@PID.3.1^YHQ4926^NHI
PID|1||YHQ4926^^^NZ_MOH^NHI||O'BRIEN^Siobhan^Maireed^^Ms||19910601|F|||45 Jervois Road^^Ponsonby^Auckland^1011^NZL||^PRN^PH^^64^9^3781294||||||||||21^^^ADHB^DI
```

---

## 18. ORU^R01 - Histopathology result from Nelson Marlborough DHB

```
MSH|^~\&|HISTOPATH_LIS|NMDHB|RHAPSODY|RIE|20250408160000||ORU^R01^ORU_R01|MSG00018|P|2.5|||AL|NE|NZL
PID|1||DJV5803^^^NZ_MOH^NHI||FRASIER^Colin^Duncan^^Mr||19720830|M|||62 Hampden Street^^Nelson^^7010^NZL||^PRN^PH^^64^3^5462841
PV1|1|O|PATHOL^MAIN^001^^^NMDHB||||DRGARCIA^Garciaparra^Elena^^^Dr^MD
ORC|RE|ORD400567|LAB500890||CM||||20250408120000|||DRGARCIA^Garciaparra^Elena^^^Dr^MD
OBR|1|ORD400567|LAB500890|HISTPATH^Histopathology^NZPOCS||20250405100000|20250405110000|||||||20250405110000||DRGARCIA^Garciaparra^Elena^^^Dr^MD||||||20250408160000|||F
OBX|1|FT|22637-3^Pathology Report^LN||MACROSCOPIC: Skin ellipse 15 x 8 x 5mm with a central pigmented lesion 6mm diameter.~MICROSCOPIC: Sections show a compound melanocytic naevus with regular architecture and uniform cytology. No evidence of dysplasia or malignancy. Margins clear.~DIAGNOSIS: Benign compound melanocytic naevus, completely excised.||||||F|||20250408160000
OBX|2|NM|33882-2^Specimen Size^LN||15|mm|||||F|||20250408160000
```

---

## 19. ADT^A28 - New NHI registration notification from Te Whatu Ora

```
MSH|^~\&|NHI_SYS|NZ_MOH|RHAPSODY|RIE|20250501120000||ADT^A28^ADT_A05|MSG00019|P|2.4|||AL|NE|NZL
EVN|A28|20250501120000|||NHI_SYSTEM^NHI^Registration
PID|1||QSL7290^^^NZ_MOH^NHI||RAUKAWA^Waimarie^Hinerangi^^Ms||20250428|F|||83 Tristram Street^^Hamilton^^3204^NZL||^PRN^PH^^64^7^8385128|||||||||21^^^WAIKATO_DHB^DI
NK1|1|RAUKAWA^Anahera^Whetu^^Mrs|MTH^Mother||^PRN^PH^^64^7^8385128
```

---

## 20. ORU^R01 - Electrocardiogram result from Lakes DHB

```
MSH|^~\&|ECG_SYS|LDHB|RHAPSODY|RIE|20250414090500||ORU^R01^ORU_R01|MSG00020|P|2.5|||AL|NE|NZL
PID|1||TBR8419^^^NZ_MOH^NHI||CAMPBELL^Iain^Robertson^^Mr||19480912|M|||29 Fenton Street^^Rotorua^^3010^NZL||^PRN^PH^^64^7^3482176
PV1|1|I|CCU^102^A^^^LDHB||||DRMORRIS^Morrissey^Thomas^^^Dr^MD|||CAR||||7|||DRMORRIS^Morrissey^Thomas^^^Dr^MD|IP
ORC|RE|ECG500123|ECG600456||CM||||20250414085000|||DRMORRIS^Morrissey^Thomas^^^Dr^MD
OBR|1|ECG500123|ECG600456|93000^Electrocardiogram^CPT||20250414085000|20250414085500|||||||20250414085500||DRMORRIS^Morrissey^Thomas^^^Dr^MD||||||20250414090500|||F
OBX|1|FT|93000^ECG Interpretation^CPT||Sinus rhythm at 72 bpm. Normal axis. PR interval 180ms. QRS duration 90ms. No ST-segment changes. No T-wave abnormalities. Normal ECG.||||||F|||20250414090500
OBX|2|NM|8867-4^Heart Rate^LN||72|bpm|60-100|N|||F|||20250414090500
OBX|3|NM|8625-6^PR Interval^LN||180|ms|120-200|N|||F|||20250414090500
OBX|4|NM|8633-0^QRS Duration^LN||90|ms|60-110|N|||F|||20250414090500
```
