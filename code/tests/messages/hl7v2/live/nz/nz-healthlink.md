# HealthLink Messaging - real HL7v2 ER7 messages

---

## 1. ORU^R01 - Full blood count result from Auckland City Hospital laboratory

```
MSH|^~\&|ACHLABS|AUCKLAND_CITY_HOSPITAL|HEALTHLINK|HL_NZ|20250312091500||ORU^R01|ACH20250312001|P|2.4|||AL|NE|NZL
PID|1||ZZZ1234^^^ADHB^MR~PCR8351^^^MOH_NZ^NHI||SEFO^Manase^Tomasi^^Mr||19710822|M|||47 Jervois Road^^Herne Bay^Auckland^^1011^NZ||+6493628714^^^manase.sefo@email.co.nz
PV1|1|O|HAEM^HAEM01^^^AUCKLAND_CITY_HOSPITAL||||62145^XU^Yifan^Mei^^^Dr|||HAE
ORC|RE|ORD20250312-001|ACH-LAB-78432||CM
OBR|1|ORD20250312-001|ACH-LAB-78432|26604007^Full blood count^SCT|||20250312080000|||||||20250312082000||62145^XU^Yifan^Mei^^^Dr||||||20250312091500|||F
OBX|1|NM|718-7^Hemoglobin^LN||148|g/L|130-175|N|||F
OBX|2|NM|789-8^Erythrocytes^LN||5.1|x10*12/L|4.5-6.5|N|||F
OBX|3|NM|6690-2^Leukocytes^LN||7.2|x10*9/L|4.0-11.0|N|||F
OBX|4|NM|777-3^Platelets^LN||245|x10*9/L|150-400|N|||F
OBX|5|NM|4544-3^Hematocrit^LN||0.44|L/L|0.40-0.54|N|||F
OBX|6|NM|787-2^MCV^LN||86.3|fL|80.0-100.0|N|||F
OBX|7|NM|785-6^MCH^LN||29.0|pg|27.0-33.0|N|||F
OBX|8|NM|786-4^MCHC^LN||336|g/L|320-360|N|||F
```

---

## 2. ORU^R01 - Liver function tests with abnormal results from Canterbury Health Laboratories

```
MSH|^~\&|CHL_LIS|CANTERBURY_HEALTH_LABS|HEALTHLINK|HL_NZ|20250218143012||ORU^R01|CHL20250218003|P|2.4|||AL|NE|NZL
PID|1||ZZZ5678^^^CDHB^MR~LDX9472^^^MOH_NZ^NHI||NGATA^Aroha^Hineteiwaiwa^^Mrs||19640517|F|||83 Bealey Avenue^^St Albans^Christchurch^^8014^NZ||+6433716284^^^aroha.ngata@email.co.nz
PV1|1|O|CHEM^CHEM01^^^CHRISTCHURCH_HOSPITAL||||71823^MORROW^Jeremy^David^^^Dr|||GEN
ORC|RE|ORD20250218-003|CHL-LFT-91256||CM
OBR|1|ORD20250218-003|CHL-LFT-91256|24326-1^Hepatic function panel^LN|||20250218110000|||||||20250218112500||71823^MORROW^Jeremy^David^^^Dr||||||20250218143012|||F
OBX|1|NM|1742-6^ALT^LN||87|U/L|0-41|H|||F
OBX|2|NM|1920-8^AST^LN||62|U/L|0-40|H|||F
OBX|3|NM|6768-6^ALP^LN||95|U/L|30-120|N|||F
OBX|4|NM|10834-0^GGT^LN||112|U/L|0-60|H|||F
OBX|5|NM|1975-2^Total Bilirubin^LN||22|umol/L|0-20|H|||F
OBX|6|NM|2885-2^Total Protein^LN||72|g/L|60-83|N|||F
OBX|7|NM|1751-7^Albumin^LN||38|g/L|35-50|N|||F
```

---

## 3. ORU^R01 - Radiology report for chest X-ray from Waikato Hospital

```
MSH|^~\&|WAIKATO_RIS|WAIKATO_HOSPITAL|HEALTHLINK|HL_NZ|20250405101530||ORU^R01|WKO20250405007|P|2.4|||AL|NE|NZL
PID|1||ZZZ9012^^^WDHB^MR~RYV3082^^^MOH_NZ^NHI||TE_PUNI^Wiremu^Hohepa^^Mr||19530910|M|||31 Tristram Street^^Frankton^Hamilton^^3204^NZ||+6478194263
PV1|1|O|RAD^RAD01^^^WAIKATO_HOSPITAL||||83921^BERRYMAN^Sarah^Annette^^^Dr|||RAD
ORC|RE|ORD20250405-007|WKO-RAD-34521||CM
OBR|1|ORD20250405-007|WKO-RAD-34521|71020^Chest X-ray PA and Lateral^CPT|||20250405090000|||||||20250405091500||55234^WALSH^Brendan^Patrick^^^Dr||||||20250405101530|||F
OBX|1|FT|71020^Chest X-ray report^CPT||Indication: Persistent cough 3 weeks\.br\\.br\Findings:\.br\The heart is normal in size and configuration. The mediastinal contour is unremarkable. The lungs are clear with no focal consolidation, mass, or pleural effusion. No pneumothorax. The costophrenic angles are sharp bilaterally. Osseous structures are intact.\.br\\.br\Impression:\.br\Normal chest radiograph. No acute cardiopulmonary abnormality identified.||||||F
```

---

## 4. ORU^R01 - HbA1c result from Taranaki Base Hospital laboratory

```
MSH|^~\&|TDHB_LAB|TARANAKI_BASE_HOSPITAL|HEALTHLINK|HL_NZ|20250127155200||ORU^R01|TDH20250127012|P|2.4|||AL|NE|NZL
PID|1||ZZZ3456^^^TDHB^MR~LBN9437^^^MOH_NZ^NHI||PAEWAI^Hana^Roimata^^Ms||19801103|F|||58 Coronation Avenue^^Welbourn^New Plymouth^^4310^NZ||+6467591238^^^hana.paewai@email.co.nz
PV1|1|O|CHEM^CHEM01^^^TARANAKI_BASE_HOSPITAL||||44287^GUPTA^Priya^Anjali^^^Dr|||GEN
ORC|RE|ORD20250127-012|TDH-LAB-56781||CM
OBR|1|ORD20250127-012|TDH-LAB-56781|4548-4^HbA1c^LN|||20250127140000|||||||20250127142000||44287^GUPTA^Priya^Anjali^^^Dr||||||20250127155200|||F
OBX|1|NM|4548-4^Hemoglobin A1c^LN||58|mmol/mol|20-41|H|||F
OBX|2|NM|17856-6^HbA1c percentage^LN||7.5|%|4.0-6.0|H|||F
NTE|1||Diabetic range. Suggest review of glycaemic management.
```

---

## 5. ORU^R01 - Urine culture and sensitivity from Southern Community Laboratories

```
MSH|^~\&|SCL_LIS|SOUTHERN_COMMUNITY_LABS|HEALTHLINK|HL_NZ|20250309083045||ORU^R01|SCL20250309004|P|2.4|||AL|NE|NZL
PID|1||ZZZ7890^^^SDHB^MR~JFA8125^^^MOH_NZ^NHI||MCKENZIE^Fiona^Catriona^^Mrs||19870625|F|||29 George Street^^North Dunedin^Dunedin^^9016^NZ||+6434591738
PV1|1|O|MICRO^MICRO01^^^DUNEDIN_HOSPITAL||||59312^O_BRIEN^Patrick^Liam^^^Dr|||GEN
ORC|RE|ORD20250309-004|SCL-MIC-72345||CM
OBR|1|ORD20250309-004|SCL-MIC-72345|630-4^Urine culture^LN|||20250308153000|||||||20250308154000||59312^O_BRIEN^Patrick^Liam^^^Dr||||||20250309083045|||F
OBX|1|ST|630-4^Urine culture^LN||Escherichia coli >10^8 CFU/L||||||F
OBX|2|ST|18769-0^Amoxicillin susceptibility^LN||Resistant||||||F
OBX|3|ST|18862-3^Trimethoprim susceptibility^LN||Resistant||||||F
OBX|4|ST|18928-2^Nitrofurantoin susceptibility^LN||Susceptible||||||F
OBX|5|ST|18906-8^Cefalexin susceptibility^LN||Susceptible||||||F
NTE|1||Significant growth of E. coli. Recommend Nitrofurantoin given resistance pattern.
```

---

## 6. REF^I12 - Electronic referral from GP to Middlemore Hospital cardiology

```
MSH|^~\&|MEDTECH32|GREENLANE_MEDICAL|HEALTHLINK|HL_NZ|20250421091200||REF^I12|REF20250421001|P|2.4|||AL|NE|NZL
RF1|SS|OP^Outpatient^HL70336||CAR^Cardiology^L|UR^Urgent^HL70280|20250421
PID|1||ZZZ2345^^^CMDHB^MR~VHC4163^^^MOH_NZ^NHI||LATU^Tanielu^Falani^^Mr||19680314|M|||124 Massey Road^^Otahuhu^Auckland^^1062^NZ||+6492837461^^^tanielu.latu@email.co.nz
NK1|1|LATU^Sina^Mele^^Mrs|SPO|124 Massey Road^^Otahuhu^Auckland^^1062^NZ|+64212983614
PRD|RP|FITZGERALD^Declan^Aidan^^^Dr|Greenlane Medical Centre^^54 Greenlane West^^Auckland^^1051^NZ|||||67823^NZMC
PRD|RT|CARDIOLOGY^Middlemore Hospital||||||MIDDLEMORE_HOSPITAL
DG1|1||I25.1^Ischaemic heart disease^I10
NTE|1||56-year-old Samoan male with recent onset exertional chest pain. ECG shows ST depression in leads V4-V6. Family history of premature CAD. Current medications: aspirin 100mg daily, atorvastatin 40mg. Please review urgently for exercise stress test and consideration of angiography.
```

---

## 7. REF^I12 - GP referral to Wellington Hospital orthopaedics

```
MSH|^~\&|MYPRACTICE|KARORI_MEDICAL|HEALTHLINK|HL_NZ|20250514102300||REF^I12|REF20250514002|P|2.4|||AL|NE|NZL
RF1|SS|OP^Outpatient^HL70336||ORT^Orthopaedics^L|RO^Routine^HL70280|20250514
PID|1||ZZZ4567^^^CCDHB^MR~WSP5128^^^MOH_NZ^NHI||O_DONNELL^Bridget^Saoirse^^Ms||19750208|F|||72 Marsden Avenue^^Karori^Wellington^^6012^NZ||+6449518273
PRD|RP|CHEN^David^Jianjun^^^Dr|Karori Medical Centre^^196 Karori Road^^Wellington^^6012^NZ|||||71456^NZMC
PRD|RT|ORTHOPAEDICS^Wellington Regional Hospital||||||WELLINGTON_HOSPITAL
DG1|1||M17.1^Primary osteoarthritis of knee^I10
NTE|1||49-year-old female with progressive right knee pain over 12 months. BMI 28. Weight-bearing X-ray shows medial joint space narrowing with marginal osteophytes. Failed conservative management with physiotherapy and NSAIDs. Requesting assessment for total knee replacement.
```

---

## 8. ADT^A01 - Admit patient to Christchurch Hospital

```
MSH|^~\&|HEALTHLINK|HL_NZ|HOMER|CHRISTCHURCH_HOSPITAL|20250601141500||ADT^A01|ADT20250601003|P|2.4|||AL|NE|NZL
EVN|A01|20250601141000
PID|1||ZZZ6789^^^CDHB^MR~MRT8027^^^MOH_NZ^NHI||MATIU^Rawiri^Pirimia^^Mr||19460719|M|||38 Innes Road^^St Albans^Christchurch^^8052^NZ||+6433458192
NK1|1|MATIU^Hinerau^Wikitoria^^Mrs|SPO|38 Innes Road^^St Albans^Christchurch^^8052^NZ|+64274182693
PV1|1|I|MED^4W^412^1^^CHRISTCHURCH_HOSPITAL||||82134^TAYLOR^Rebecca^Ann^^^Dr|||GEN||||1|||82134^TAYLOR^Rebecca^Ann^^^Dr|IN||||||||||||||||||CHRISTCHURCH_HOSPITAL|||||20250601141000
DG1|1||J18.9^Pneumonia, unspecified organism^I10|||AD
DG1|2||J44.1^COPD with acute exacerbation^I10|||SD
```

---

## 9. ADT^A03 - Discharge patient from North Shore Hospital

```
MSH|^~\&|HEALTHLINK|HL_NZ|CONCERTO|NORTH_SHORE_HOSPITAL|20250223163000||ADT^A03|ADT20250223008|P|2.4|||AL|NE|NZL
EVN|A03|20250223162500
PID|1||ZZZ8901^^^WDHB^MR~KQE9354^^^MOH_NZ^NHI||KIM^Jiyoung^Hana^^Mrs||19820411|F|||94 Lake Road^^Belmont^Auckland^^0622^NZ||+6494812673^^^jiyoung.kim@email.co.nz
PV1|1|I|SURG^2N^210^1^^NORTH_SHORE_HOSPITAL||||73456^WRIGHT^Michael^Edward^^^Dr|||GEN||||1|||73456^WRIGHT^Michael^Edward^^^Dr|IN||||||||||||||||||NORTH_SHORE_HOSPITAL|||||20250220083000|||20250223162500
DG1|1||K80.2^Calculus of gallbladder without cholecystitis^I10|||AD
PR1|1||51.23^Laparoscopic cholecystectomy^I10|||20250221100000
```

---

## 10. ADT^A08 - Update patient demographics at Hawke's Bay Hospital

```
MSH|^~\&|HEALTHLINK|HL_NZ|WEBPAS|HAWKES_BAY_HOSPITAL|20250710110000||ADT^A08|ADT20250710005|P|2.4|||AL|NE|NZL
EVN|A08|20250710110000
PID|1||ZZZ0123^^^HBDHB^MR~NWG2475^^^MOH_NZ^NHI||NIKORA^Anahera^Whetu^^Ms||19930316|F|||27 Heretaunga Street West^^Hastings^^4122^NZ||+6468791482^^^anahera.nikora@email.co.nz||MAO|S
PD1||||39821^MCKAY^Margaret^Eleanor^^^Dr^Hastings Health Centre
PV1|1|O|GP^GP01^^^HASTINGS_HEALTH_CENTRE||||39821^MCKAY^Margaret^Eleanor^^^Dr
```

---

## 11. ORU^R01 - Thyroid function tests from LabTests Auckland

```
MSH|^~\&|LABTESTS_LIS|LABTESTS_AUCKLAND|HEALTHLINK|HL_NZ|20250503140800||ORU^R01|LTA20250503019|P|2.4|||AL|NE|NZL
PID|1||ZZZ4321^^^ADHB^MR~CRP6280^^^MOH_NZ^NHI||PATEL^Roshni^Kiran^^Mrs||19760901|F|||58 Sandringham Road^^Mount Eden^Auckland^^1024^NZ||+6496183274
PV1|1|O|CHEM^CHEM01^^^LABTESTS_AUCKLAND||||52178^THORNTON^Grace^Eleanor^^^Dr|||GEN
ORC|RE|ORD20250503-019|LTA-THY-88921||CM
OBR|1|ORD20250503-019|LTA-THY-88921|24348-5^Thyroid function tests^LN|||20250503100000|||||||20250503101500||52178^THORNTON^Grace^Eleanor^^^Dr||||||20250503140800|||F
OBX|1|NM|3016-3^TSH^LN||8.72|mIU/L|0.27-4.20|H|||F
OBX|2|NM|3024-7^Free T4^LN||9.8|pmol/L|12.0-22.0|L|||F
OBX|3|NM|3053-6^Free T3^LN||3.2|pmol/L|3.1-6.8|N|||F
NTE|1||TSH elevated with low Free T4 consistent with primary hypothyroidism. Consider thyroid peroxidase antibody testing.
```

---

## 12. ORU^R01 - Lipid panel from Medlab Central

```
MSH|^~\&|MEDLAB_LIS|MEDLAB_CENTRAL|HEALTHLINK|HL_NZ|20250618091230||ORU^R01|MLC20250618022|P|2.4|||AL|NE|NZL
PID|1||ZZZ5432^^^MDHB^MR~DSV7194^^^MOH_NZ^NHI||RAUKAWA^Tamati^Hone^^Mr||19590827|M|||21 Pitt Street^^Hokowhitu^Palmerston North^^4410^NZ||+6463572819
PV1|1|O|CHEM^CHEM01^^^MEDLAB_CENTRAL||||48923^SINGH^Ravinder^Mohan^^^Dr|||GEN
ORC|RE|ORD20250618-022|MLC-LIP-45123||CM
OBR|1|ORD20250618-022|MLC-LIP-45123|24331-1^Lipid panel^LN|||20250618080000|||||||20250618082000||48923^SINGH^Ravinder^Mohan^^^Dr||||||20250618091230|||F
OBX|1|NM|2093-3^Total Cholesterol^LN||6.8|mmol/L|<5.0|H|||F
OBX|2|NM|2571-8^Triglycerides^LN||2.4|mmol/L|<1.7|H|||F
OBX|3|NM|2085-9^HDL Cholesterol^LN||1.0|mmol/L|>1.0|N|||F
OBX|4|NM|13457-7^LDL Cholesterol (calculated)^LN||4.7|mmol/L|<2.0|H|||F
OBX|5|NM|9830-1^Total/HDL Cholesterol Ratio^LN||6.8||<4.5|H|||F
NTE|1||CVD risk assessment recommended. LDL significantly elevated above target for patient age and ethnicity.
```

---

## 13. MDM^T02 - Discharge summary from Middlemore Hospital with embedded PDF

```
MSH|^~\&|CLINICAL_PORTAL|MIDDLEMORE_HOSPITAL|HEALTHLINK|HL_NZ|20250315141200||MDM^T02|MDM20250315001|P|2.4|||AL|NE|NZL
EVN|T02|20250315141200
PID|1||ZZZ6543^^^CMDHB^MR~XKQ8137^^^MOH_NZ^NHI||TUPOU^Mele^Lupe^^Mrs||19700422|F|||63 East Tamaki Road^^Otara^Auckland^^2023^NZ||+6492738614
PV1|1|I|MED^6W^612^1^^MIDDLEMORE_HOSPITAL||||91234^AHMED^Farah^Yasmin^^^Dr|||GEN||||1|||91234^AHMED^Farah^Yasmin^^^Dr|IN||||||||||||||||||MIDDLEMORE_HOSPITAL|||||20250310091500|||20250315130000
TXA|1|DS^Discharge Summary|TX|20250315130000|91234^AHMED^Farah^Yasmin^^^Dr||20250315141200||91234^AHMED^Farah^Yasmin^^^Dr|||MDM20250315001||||AU
OBX|1|ED|PDF^Discharge Summary^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo=||||||F
```

---

## 14. MDM^T02 - Specialist clinic letter from Wellington Hospital with embedded PDF

```
MSH|^~\&|CLINICAL_PORTAL|WELLINGTON_HOSPITAL|HEALTHLINK|HL_NZ|20250428103000||MDM^T02|MDM20250428002|P|2.4|||AL|NE|NZL
EVN|T02|20250428103000
PID|1||ZZZ7654^^^CCDHB^MR~BFY9408^^^MOH_NZ^NHI||WHITAKER^Oliver^Edmund^^Mr||19840616|M|||45 Cuba Street^^Te Aro^Wellington^^6011^NZ||+6449258731^^^oliver.whitaker@email.co.nz
PV1|1|O|NEUR^NEUR01^^^WELLINGTON_HOSPITAL||||87654^PRASAD^Vikram^Anand^^^Dr|||NEU
TXA|1|CL^Clinic Letter|TX|20250428100000|87654^PRASAD^Vikram^Anand^^^Dr||20250428103000||87654^PRASAD^Vikram^Anand^^^Dr|||MDM20250428002||||AU
OBX|1|ED|PDF^Neurology Clinic Letter^LN||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo=||||||F
```

---

## 15. ORU^R01 - Coagulation studies from Waikato Hospital laboratory

```
MSH|^~\&|WAIKATO_LIS|WAIKATO_HOSPITAL|HEALTHLINK|HL_NZ|20250722081500||ORU^R01|WKO20250722015|P|2.4|||AL|NE|NZL
PID|1||ZZZ8765^^^WDHB^MR~VLP4071^^^MOH_NZ^NHI||VAN_DER_BEEK^Johannes^Hendrik^^Mr||19520303|M|||52 Peachgrove Road^^Hamilton East^Hamilton^^3216^NZ||+6478291647
PV1|1|O|HAEM^HAEM01^^^WAIKATO_HOSPITAL||||62891^ROBERTS^Katherine^Louise^^^Dr|||GEN
ORC|RE|ORD20250722-015|WKO-COG-56231||CM
OBR|1|ORD20250722-015|WKO-COG-56231|COAG^Coagulation studies^L|||20250722070000|||||||20250722072000||62891^ROBERTS^Katherine^Louise^^^Dr||||||20250722081500|||F
OBX|1|NM|5902-2^PT^LN||16.2|seconds|11.5-15.5|H|||F
OBX|2|NM|6301-6^INR^LN||1.4||0.9-1.2|H|||F
OBX|3|NM|3173-2^APTT^LN||32|seconds|25-37|N|||F
OBX|4|NM|3255-7^Fibrinogen^LN||3.8|g/L|1.5-4.0|N|||F
NTE|1||INR mildly elevated. Please correlate with clinical context and anticoagulant therapy.
```

---

## 16. REF^I12 - Referral to Starship Children's Hospital paediatric gastroenterology

```
MSH|^~\&|INDICI|REMUERA_DOCTORS|HEALTHLINK|HL_NZ|20250205143000||REF^I12|REF20250205003|P|2.4|||AL|NE|NZL
RF1|SS|OP^Outpatient^HL70336||PGE^Paediatric Gastroenterology^L|UR^Urgent^HL70280|20250205
PID|1||ZZZ9876^^^ADHB^MR~ZTC5294^^^MOH_NZ^NHI||MOALA^Sina^Litia^^Miss||20170803|F|||72 Victoria Avenue^^Remuera^Auckland^^1050^NZ||+6495362718
NK1|1|MOALA^Tevita^Manase^^Mr|FTH|72 Victoria Avenue^^Remuera^Auckland^^1050^NZ|+64211387462
NK1|2|MOALA^Lupe^Talia^^Mrs|MTH|72 Victoria Avenue^^Remuera^Auckland^^1050^NZ|+64219764831
PRD|RP|STEWART^Angela^Helen^^^Dr|Remuera Doctors^^88 Remuera Road^^Auckland^^1050^NZ|||||81234^NZMC
PRD|RT|PAED_GASTRO^Starship Children's Hospital||||||STARSHIP_HOSPITAL
DG1|1||K90.0^Coeliac disease^I10
NTE|1||7-year-old girl with chronic abdominal pain, intermittent diarrhoea, and poor weight gain over 6 months. Dropped from 50th to 15th centile. Tissue transglutaminase antibody strongly positive at 128 U/mL (ref <15). Total IgA normal. Family history of coeliac disease in maternal aunt. Requesting endoscopy and biopsy for confirmation before commencing gluten-free diet.
```

---

## 17. ADT^A04 - Register outpatient at Bay of Plenty DHB

```
MSH|^~\&|HEALTHLINK|HL_NZ|WEBPAS|TAURANGA_HOSPITAL|20250819093000||ADT^A04|ADT20250819002|P|2.4|||AL|NE|NZL
EVN|A04|20250819092500
PID|1||ZZZ1098^^^BOPDHB^MR~YGN3608^^^MOH_NZ^NHI||EDWARDSON^Sarah^Charlotte^^Ms||19900712|F|||64 Eleventh Avenue^^Tauranga^^3110^NZ||+6475718264^^^sarah.edwardson@email.co.nz||EUR|S
PV1|1|O|DERM^DERM01^^^TAURANGA_HOSPITAL||||56712^AHMEDOVA^Leila^Sevda^^^Dr|||DER||||5|||56712^AHMEDOVA^Leila^Sevda^^^Dr|OP||||||||||||||||||TAURANGA_HOSPITAL|||||20250819092500
PV2|||^Dermatology review - suspicious naevi
```

---

## 18. ORU^R01 - CT abdomen report from Hutt Valley DHB radiology

```
MSH|^~\&|HUTT_RIS|HUTT_VALLEY_HOSPITAL|HEALTHLINK|HL_NZ|20250911153000||ORU^R01|HVH20250911009|P|2.4|||AL|NE|NZL
PID|1||ZZZ2109^^^HVDHB^MR~PWF1483^^^MOH_NZ^NHI||PHAM^Linh^Hoa^^Mrs||19681125|F|||38 Stokes Valley Road^^Stokes Valley^Lower Hutt^^5019^NZ||+6445712863
PV1|1|O|RAD^RAD01^^^HUTT_VALLEY_HOSPITAL||||74321^MARTINEZ^Elena^Sofia^^^Dr|||RAD
ORC|RE|ORD20250911-009|HVH-RAD-91234||CM
OBR|1|ORD20250911-009|HVH-RAD-91234|74177^CT Abdomen and Pelvis with contrast^CPT|||20250911130000|||||||20250911132000||43218^LEE^Andrew^Joon^^^Dr||||||20250911153000|||F
OBX|1|FT|74177^CT Abdomen and Pelvis report^CPT||Indication: Abdominal pain, weight loss, elevated LFTs\.br\\.br\Technique: Helical CT abdomen and pelvis with IV contrast (Omnipaque 350, 100mL).\.br\\.br\Findings:\.br\Liver: A 2.3 cm hypodense lesion in segment VI demonstrates peripheral enhancement with centripetal fill-in, consistent with haemangioma. No other focal hepatic lesions.\.br\Gallbladder: Normal, no calculi.\.br\Pancreas: Normal in size and attenuation. No ductal dilatation.\.br\Spleen: Normal.\.br\Kidneys: Bilateral simple cortical cysts, largest 1.8 cm left kidney. No hydronephrosis.\.br\Bowel: No obstruction or wall thickening.\.br\Lymph nodes: No pathological lymphadenopathy.\.br\\.br\Impression:\.br\1. Hepatic haemangioma segment VI, benign appearance.\.br\2. Bilateral simple renal cysts, incidental.\.br\3. No evidence of malignancy or other significant pathology to account for symptoms.||||||F
```

---

## 19. ORU^R01 - Renal function panel from Northland Pathology

```
MSH|^~\&|NPATH_LIS|NORTHLAND_PATHOLOGY|HEALTHLINK|HL_NZ|20250630102000||ORU^R01|NPA20250630011|P|2.4|||AL|NE|NZL
PID|1||ZZZ3210^^^NDHB^MR~SBR7029^^^MOH_NZ^NHI||TURIA^Marama^Wikitoria^^Mrs||19550908|F|||27 Western Hills Drive^^Whangarei^^0112^NZ||+6494261738
PV1|1|O|CHEM^CHEM01^^^WHANGAREI_HOSPITAL||||38765^BRENNAN^Stephen^Patrick^^^Dr|||GEN
ORC|RE|ORD20250630-011|NPA-REN-34567||CM
OBR|1|ORD20250630-011|NPA-REN-34567|24362-6^Renal function panel^LN|||20250630090000|||||||20250630091500||38765^BRENNAN^Stephen^Patrick^^^Dr||||||20250630102000|||F
OBX|1|NM|2160-0^Creatinine^LN||142|umol/L|45-90|H|||F
OBX|2|NM|3094-0^Urea^LN||12.8|mmol/L|2.5-7.1|H|||F
OBX|3|NM|33914-3^eGFR^LN||34|mL/min/1.73m2|>90|L|||F
OBX|4|NM|2951-2^Sodium^LN||139|mmol/L|135-145|N|||F
OBX|5|NM|2823-3^Potassium^LN||5.3|mmol/L|3.5-5.2|H|||F
NTE|1||eGFR 34 mL/min indicates CKD stage 3b. Potassium mildly elevated. Recommend nephrology referral and review of medications.
```

---

## 20. ADT^A08 - Update patient next of kin at Nelson Marlborough DHB

```
MSH|^~\&|HEALTHLINK|HL_NZ|WEBPAS|NELSON_HOSPITAL|20250804150000||ADT^A08|ADT20250804006|P|2.4|||AL|NE|NZL
EVN|A08|20250804150000
PID|1||ZZZ4320^^^NMDHB^MR~JKW6831^^^MOH_NZ^NHI||ANDERSEN^Thomas^Reginald^^Mr||19870119|M|||63 Waimea Road^^Stoke^Nelson^^7011^NZ||+6435472183^^^thomas.andersen@email.co.nz||EUR|M
NK1|1|ANDERSEN^Emma^Charlotte^^Mrs|SPO|63 Waimea Road^^Stoke^Nelson^^7011^NZ|+64274538291
NK1|2|ANDERSEN^Robert^Hugo^^Mr|FTH|41 Hampden Street^^Nelson^^7010^NZ|+6435361827
PV1|1|I|MED^3E^305^1^^NELSON_HOSPITAL||||42187^MCLEOD^Fiona^Catherine^^^Dr|||GEN||||1|||42187^MCLEOD^Fiona^Catherine^^^Dr|IN||||||||||||||||||NELSON_HOSPITAL|||||20250802091000
```
