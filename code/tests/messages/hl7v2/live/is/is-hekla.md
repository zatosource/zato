# Hekla - real HL7v2 ER7 messages

---

## 1. ADT^A01 - Inpatient admission

```
MSH|^~\&|HEKLA|LANDSPITALI|SAGA|LANDSPITALI|20240315091200||ADT^A01^ADT_A01|MSG20240315091200001|P|2.5|||AL|NE||8859/1
EVN|A01|20240315091200|||SVANHILDUR^Svanhildur Þórsdóttir
PID|1||1810912483^^^ISLAND^SS||Vilbergsson^Heiðar^^^Hr||19911018|M|||Lindarbraut 9^^Akureyri^^603^IS||^PRN^PH^^^354^4622917|^WPN^PH^^^354^4625302||IS|S||||||||||IS||||N
PV1|1|I|MED-3^312^1^LANDSPITALI^^^^MED|||||||INT^Internist^Pétursson^Hilmar^^^Dr|||MED||||ADM||||||||||||||||||LANDSPITALI||A|||20240315091200
PV2|||^Pneumonia, unspecified|||||||2||||||||||||||||||||||||N
IN1|1|001^Sjúkratryggingar Íslands|9700|Sjúkratryggingar Íslands|Vínlandsleið 16^^Reykjavík^^105^IS|||||||||||||||||||||||||||||||||1810912483
```

---

## 2. ADT^A03 - Discharge

```
MSH|^~\&|HEKLA|FSA|SAGA|FSA|20240318143000||ADT^A03^ADT_A03|MSG20240318143000002|P|2.5|||AL|NE||8859/1
EVN|A03|20240318143000|||GERDUR^Gerður Ásgrímsdóttir
PID|1||0407854261^^^ISLAND^SS||Friðriksdóttir^Ásthildur^^^Frú||19850704|F|||Ránargata 18^^Reykjanesbær^^230^IS||^PRN^PH^^^354^4204158||||S||||||||||IS||||N
PV1|1|I|SURG-2^205^1^FSA^^^^SURG|||||||SUR^Surgeon^Ægisson^Tryggvi^^^Dr|||SUR||||ADM||||||||||||||||||FSA||A|||20240315100000|||20240318143000
DG1|1|I10|J18.9^Pneumonia, unspecified^I10|||A
```

---

## 3. ADT^A04 - Outpatient registration

```
MSH|^~\&|HEKLA|HEILSUGAESLA_HLIDAR|SAGA|HEILSUGAESLAN|20240320080000||ADT^A04^ADT_A04|MSG20240320080000003|P|2.5|||AL|NE||8859/1
EVN|A04|20240320080000|||SIF^Sif Höskuldsdóttir
PID|1||1410953407^^^ISLAND^SS||Steinarsdóttir^Auður^^^Frú||19951014|F|||Suðurgata 4^^Ísafjörður^^400^IS||^PRN^PH^^^354^4564832||||M||||||||||IS||||N
PV1|1|O|OUT-1^101^1^HEILSUGAESLA_HLIDAR^^^^GEN|||||||GP^General Practitioner^Þorvaldsson^Reynir^^^Dr|||GEN||||REF||||||||||||||||||HEILSUGAESLA_HLIDAR||A|||20240320080000
```

---

## 4. ADT^A08 - Update patient info

```
MSH|^~\&|HEKLA|LANDSPITALI|SAGA|LANDSPITALI|20240321101500||ADT^A08^ADT_A08|MSG20240321101500004|P|2.5|||AL|NE||8859/1
EVN|A08|20240321101500|||SYSTEM^Hekla System
PID|1||1810912483^^^ISLAND^SS||Vilbergsson^Heiðar^^^Hr||19911018|M|||Hraunbær 88^^Reykjavík^^110^IS||^PRN^PH^^^354^5572180|^WPN^PH^^^354^5573925||IS|M||||||||||IS||||N
PV1|1|I|MED-3^312^1^LANDSPITALI^^^^MED|||||||INT^Internist^Pétursson^Hilmar^^^Dr|||MED||||ADM||||||||||||||||||LANDSPITALI||A|||20240315091200
```

---

## 5. ADT^A31 - Update demographics

```
MSH|^~\&|HEKLA|THJODSKRA|SAGA|LANDSPITALI|20240322090000||ADT^A31^ADT_A31|MSG20240322090000005|P|2.5|||AL|NE||8859/1
EVN|A31|20240322090000|||SYSTEM^Þjóðskrá Update
PID|1||0309804719^^^ISLAND^SS||Bárðarson^Þorlákur^^^Hr||19800903|M|||Glerárgata 60^^Akureyri^^600^IS||^PRN^PH^^^354^4631840||||D||||||||||IS||||N
PV1|1|N|||||||||||||||||||||||||||||||||||||||||||||
```

---

## 6. ADT^A02 - Patient transfer

```
MSH|^~\&|HEKLA|FSA|SAGA|FSA|20240323111500||ADT^A02^ADT_A02|MSG20240323111500006|P|2.5|||AL|NE||8859/1
EVN|A02|20240323111500|||MAGNEA^Magnea Þrastardóttir
PID|1||2306905312^^^ISLAND^SS||Klemensdóttir^Snæfríður^^^Frú||19900623|F|||Vestmannabraut 14^^Vestmannaeyjar^^900^IS||^PRN^PH^^^354^4812907||||S||||||||||IS||||N
PV1|1|I|ICU-1^101^1^FSA^^^^ICU|||MED-2^204^1^FSA^^^^MED||||INT^Internist^Sturlaugsson^Bragi^^^Dr|||INT||||TRN||||||||||||||||||FSA||A|||20240320140000
PV2|||^Acute myocardial infarction
```

---

## 7. ORM^O01 - Lab order

```
MSH|^~\&|HEKLA|LANDSPITALI|FLEXLAB|LANDSPITALI|20240325083000||ORM^O01^ORM_O01|MSG20240325083000007|P|2.5|||AL|NE||8859/1
PID|1||0407854261^^^ISLAND^SS||Friðriksdóttir^Ásthildur^^^Frú||19850704|F|||Ránargata 18^^Reykjanesbær^^230^IS||^PRN^PH^^^354^4204158||||S||||||||||IS||||N
PV1|1|O|LAB^100^1^LANDSPITALI||||||||LAB^Laboratory^Þorbergsdóttir^Hjördís^^^Dr|||LAB||||REF
ORC|NW|ORD240325001|||||^^^20240325083000^^R||20240325083000|SIF^Sif Höskuldsdóttir||Pétursson^Hilmar^^^Dr|||||LANDSPITALI
OBR|1|ORD240325001||CBC^Complete Blood Count^L|||20240325083000|||||||||Pétursson^Hilmar^^^Dr||||||||||^^^20240325^^R
OBR|2|ORD240325001||BMP^Basic Metabolic Panel^L|||20240325083000|||||||||Pétursson^Hilmar^^^Dr||||||||||^^^20240325^^R
```

---

## 8. ORM^O01 - Radiology order

```
MSH|^~\&|HEKLA|FSA|RAFÖRNINN|FSA|20240326100000||ORM^O01^ORM_O01|MSG20240326100000008|P|2.5|||AL|NE||8859/1
PID|1||2306905312^^^ISLAND^SS||Klemensdóttir^Snæfríður^^^Frú||19900623|F|||Vestmannabraut 14^^Vestmannaeyjar^^900^IS||^PRN^PH^^^354^4812907||||S||||||||||IS||||N
PV1|1|I|ICU-1^101^1^FSA^^^^ICU|||||||INT^Internist^Sturlaugsson^Bragi^^^Dr|||INT||||ADM
ORC|NW|ORD240326001|||||^^^20240326100000^^S||20240326100000|MAGNEA^Magnea Þrastardóttir||Sturlaugsson^Bragi^^^Dr|||||FSA
OBR|1|ORD240326001||71020^Chest X-ray PA and Lateral^CPT|||20240326100000|||||||^Chest pain, rule out pneumothorax|Sturlaugsson^Bragi^^^Dr||||||||||^^^20240326^^S
```

---

## 9. ORU^R01 - Hematology result

```
MSH|^~\&|HEKLA|LANDSPITALI|SAGA|LANDSPITALI|20240325140000||ORU^R01^ORU_R01|MSG20240325140000009|P|2.5|||AL|NE||8859/1
PID|1||0407854261^^^ISLAND^SS||Friðriksdóttir^Ásthildur^^^Frú||19850704|F|||Ránargata 18^^Reykjanesbær^^230^IS||^PRN^PH^^^354^4204158||||S||||||||||IS||||N
PV1|1|O|LAB^100^1^LANDSPITALI||||||||LAB^Laboratory^Þorbergsdóttir^Hjördís^^^Dr|||LAB||||REF
ORC|RE|ORD240325001||||||^^^20240325083000^^R||20240325140000|||Pétursson^Hilmar^^^Dr|||||LANDSPITALI
OBR|1|ORD240325001||CBC^Complete Blood Count^L|||20240325083000|||||||||||||||20240325140000|||F
OBX|1|NM|WBC^White Blood Cell Count^L||6.8|10*9/L|4.0-11.0||||F|||20240325130000
OBX|2|NM|RBC^Red Blood Cell Count^L||4.52|10*12/L|3.80-5.20||||F|||20240325130000
OBX|3|NM|HGB^Hemoglobin^L||138|g/L|120-160||||F|||20240325130000
OBX|4|NM|HCT^Hematocrit^L||0.41|L/L|0.36-0.46||||F|||20240325130000
OBX|5|NM|PLT^Platelet Count^L||245|10*9/L|150-400||||F|||20240325130000
```

---

## 10. ORU^R01 - Chemistry panel result

```
MSH|^~\&|HEKLA|LANDSPITALI|SAGA|LANDSPITALI|20240325141500||ORU^R01^ORU_R01|MSG20240325141500010|P|2.5|||AL|NE||8859/1
PID|1||0407854261^^^ISLAND^SS||Friðriksdóttir^Ásthildur^^^Frú||19850704|F|||Ránargata 18^^Reykjanesbær^^230^IS||^PRN^PH^^^354^4204158||||S||||||||||IS||||N
PV1|1|O|LAB^100^1^LANDSPITALI||||||||LAB^Laboratory^Þorbergsdóttir^Hjördís^^^Dr|||LAB||||REF
ORC|RE|ORD240325001||||||^^^20240325083000^^R||20240325141500|||Pétursson^Hilmar^^^Dr|||||LANDSPITALI
OBR|1|ORD240325001||BMP^Basic Metabolic Panel^L|||20240325083000|||||||||||||||20240325141500|||F
OBX|1|NM|GLU^Glucose^L||5.4|mmol/L|3.9-6.1||||F|||20240325135000
OBX|2|NM|BUN^Blood Urea Nitrogen^L||5.8|mmol/L|2.5-7.1||||F|||20240325135000
OBX|3|NM|CRE^Creatinine^L||78|umol/L|53-97||||F|||20240325135000
OBX|4|NM|NA^Sodium^L||140|mmol/L|136-145||||F|||20240325135000
OBX|5|NM|K^Potassium^L||4.1|mmol/L|3.5-5.1||||F|||20240325135000
OBX|6|NM|CL^Chloride^L||102|mmol/L|98-107||||F|||20240325135000
OBX|7|NM|CO2^Carbon Dioxide^L||24|mmol/L|22-29||||F|||20240325135000
```

---

## 11. ORU^R01 - Urinalysis result

```
MSH|^~\&|HEKLA|LANDSPITALI|SAGA|LANDSPITALI|20240326110000||ORU^R01^ORU_R01|MSG20240326110000011|P|2.5|||AL|NE||8859/1
PID|1||1810912483^^^ISLAND^SS||Vilbergsson^Heiðar^^^Hr||19911018|M|||Hraunbær 88^^Reykjavík^^110^IS||^PRN^PH^^^354^5572180||||M||||||||||IS||||N
PV1|1|I|MED-3^312^1^LANDSPITALI^^^^MED|||||||INT^Internist^Pétursson^Hilmar^^^Dr|||MED||||ADM
ORC|RE|ORD240326002||||||^^^20240326080000^^R||20240326110000|||Pétursson^Hilmar^^^Dr|||||LANDSPITALI
OBR|1|ORD240326002||UA^Urinalysis^L|||20240326080000|||||||||||||||20240326110000|||F
OBX|1|ST|COLOR^Color^L||Yellow||||||F|||20240326100000
OBX|2|ST|CLARITY^Clarity^L||Clear||||||F|||20240326100000
OBX|3|NM|SPGR^Specific Gravity^L||1.018||1.005-1.030||||F|||20240326100000
OBX|4|NM|PH^pH^L||6.0||5.0-8.0||||F|||20240326100000
OBX|5|ST|PROT^Protein^L||Negative||||||F|||20240326100000
OBX|6|ST|GLUC^Glucose^L||Negative||||||F|||20240326100000
OBX|7|ST|BACT^Bacteria^L||None seen||||||F|||20240326100000
```

---

## 12. SIU^S12 - Schedule new appointment

```
MSH|^~\&|HEKLA|HEILSUGAESLA_HLIDAR|SAGA|HEILSUGAESLAN|20240327090000||SIU^S12^SIU_S12|MSG20240327090000012|P|2.5|||AL|NE||8859/1
SCH|APT240327001||||ROUTINE^Routine^HL70276|FOLLOWUP^Follow-up Visit^L|Normal|30|MIN|^^30^20240402093000^20240402100000||SIF^Sif Höskuldsdóttir|^PRN^PH^^^354^4564832|||||SIF^Sif Höskuldsdóttir|^PRN^PH^^^354^4564832|||BOOKED
PID|1||1410953407^^^ISLAND^SS||Steinarsdóttir^Auður^^^Frú||19951014|F|||Suðurgata 4^^Ísafjörður^^400^IS||^PRN^PH^^^354^4564832||||M||||||||||IS||||N
AIG|1||THORV^Þorvaldsson^Reynir^^^Dr|GP^General Practitioner
AIL|1||HEILSUGAESLA_HLIDAR^Room 3^OUT-1
```

---

## 13. SIU^S14 - Modify appointment

```
MSH|^~\&|HEKLA|HEILSUGAESLA_HLIDAR|SAGA|HEILSUGAESLAN|20240328140000||SIU^S14^SIU_S14|MSG20240328140000013|P|2.5|||AL|NE||8859/1
SCH|APT240327001||||ROUTINE^Routine^HL70276|FOLLOWUP^Follow-up Visit^L|Normal|30|MIN|^^30^20240403100000^20240403103000||SIF^Sif Höskuldsdóttir|^PRN^PH^^^354^4564832|||||SIF^Sif Höskuldsdóttir|^PRN^PH^^^354^4564832|||BOOKED
PID|1||1410953407^^^ISLAND^SS||Steinarsdóttir^Auður^^^Frú||19951014|F|||Suðurgata 4^^Ísafjörður^^400^IS||^PRN^PH^^^354^4564832||||M||||||||||IS||||N
AIG|1||THORV^Þorvaldsson^Reynir^^^Dr|GP^General Practitioner
AIL|1||HEILSUGAESLA_HLIDAR^Room 5^OUT-1
```

---

## 14. MDM^T02 - Clinical document notification

```
MSH|^~\&|HEKLA|LANDSPITALI|SAGA|LANDSPITALI|20240329150000||MDM^T02^MDM_T02|MSG20240329150000014|P|2.5|||AL|NE||8859/1
EVN|T02|20240329150000
PID|1||1810912483^^^ISLAND^SS||Vilbergsson^Heiðar^^^Hr||19911018|M|||Hraunbær 88^^Reykjavík^^110^IS||^PRN^PH^^^354^5572180||||M||||||||||IS||||N
PV1|1|I|MED-3^312^1^LANDSPITALI^^^^MED|||||||INT^Internist^Pétursson^Hilmar^^^Dr|||MED||||ADM
TXA|1|DS^Discharge Summary^L|TX|20240329150000|Pétursson^Hilmar^^^Dr||20240329150000||Pétursson^Hilmar^^^Dr|||||DOC240329001|||AU
OBX|1|TX|18842-5^Discharge Summarization Note^LN||Patient discharged in stable condition following treatment for community-acquired pneumonia. Follow-up appointment in 2 weeks.||||||F
```

---

## 15. ORU^R01 - Microbiology culture result

```
MSH|^~\&|HEKLA|LANDSPITALI|SAGA|LANDSPITALI|20240330160000||ORU^R01^ORU_R01|MSG20240330160000015|P|2.5|||AL|NE||8859/1
PID|1||1810912483^^^ISLAND^SS||Vilbergsson^Heiðar^^^Hr||19911018|M|||Hraunbær 88^^Reykjavík^^110^IS||^PRN^PH^^^354^5572180||||M||||||||||IS||||N
PV1|1|I|MED-3^312^1^LANDSPITALI^^^^MED|||||||INT^Internist^Pétursson^Hilmar^^^Dr|||MED||||ADM
ORC|RE|ORD240328003||||||^^^20240328090000^^R||20240330160000|||Pétursson^Hilmar^^^Dr|||||LANDSPITALI
OBR|1|ORD240328003||BCULT^Blood Culture^L|||20240328090000|||||||||||||||20240330160000|||F
OBX|1|ST|ORGANISM^Organism Identified^L||Streptococcus pneumoniae||||||F|||20240330150000
OBX|2|ST|GRAM^Gram Stain^L||Gram-positive diplococci||||||F|||20240328120000
OBX|3|ST|SUSCEPT^Susceptibility^L||Penicillin: S; Erythromycin: S; Levofloxacin: S||||||F|||20240330150000
OBX|4|NM|MIC_PEN^MIC Penicillin^L||0.03|ug/mL|<=0.06||||F|||20240330150000
```

---

## 16. ADT^A40 - Merge patient identifiers

```
MSH|^~\&|HEKLA|THJODSKRA|SAGA|LANDSPITALI|20240401080000||ADT^A40^ADT_A40|MSG20240401080000016|P|2.5|||AL|NE||8859/1
EVN|A40|20240401080000|||SYSTEM^Þjóðskrá Merge
PID|1||0309804719^^^ISLAND^SS||Bárðarson^Þorlákur^^^Hr||19800903|M|||Glerárgata 60^^Akureyri^^600^IS||^PRN^PH^^^354^4631840||||D||||||||||IS||||N
MRG|0309804500^^^ISLAND^SS||||||
PV1|1|N|||||||||||||||||||||||||||||||||||||||||||||
```

---

## 17. ORU^R01 - Radiology report with base64 ED OBX (PDF)

```
MSH|^~\&|HEKLA|FSA|RAFÖRNINN|FSA|20240402120000||ORU^R01^ORU_R01|MSG20240402120000017|P|2.5|||AL|NE||8859/1
PID|1||2306905312^^^ISLAND^SS||Klemensdóttir^Snæfríður^^^Frú||19900623|F|||Vestmannabraut 14^^Vestmannaeyjar^^900^IS||^PRN^PH^^^354^4812907||||S||||||||||IS||||N
PV1|1|I|ICU-1^101^1^FSA^^^^ICU|||||||INT^Internist^Sturlaugsson^Bragi^^^Dr|||INT||||ADM
ORC|RE|ORD240326001||||||^^^20240326100000^^S||20240402120000|||Sturlaugsson^Bragi^^^Dr|||||FSA
OBR|1|ORD240326001||71020^Chest X-ray PA and Lateral^CPT|||20240326100000|||||||||||||||20240402120000|||F
OBX|1|TX|71020^Chest X-ray Report^CPT||No evidence of pneumothorax. Mild bibasilar atelectasis. Heart size normal.||||||F|||20240402110000
OBX|2|ED|PDF^Radiology Report^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2Jq||||||F|||20240402110000
```

---

## 18. ORM^O01 - Pharmacy order

```
MSH|^~\&|HEKLA|LANDSPITALI|FLEXLAB|LANDSPITALI|20240403090000||ORM^O01^ORM_O01|MSG20240403090000018|P|2.5|||AL|NE||8859/1
PID|1||1810912483^^^ISLAND^SS||Vilbergsson^Heiðar^^^Hr||19911018|M|||Hraunbær 88^^Reykjavík^^110^IS||^PRN^PH^^^354^5572180||||M||||||||||IS||||N
PV1|1|I|MED-3^312^1^LANDSPITALI^^^^MED|||||||INT^Internist^Pétursson^Hilmar^^^Dr|||MED||||ADM
ORC|NW|ORD240403001|||||^^^20240403090000^^R||20240403090000|SVANHILDUR^Svanhildur Þórsdóttir||Pétursson^Hilmar^^^Dr|||||LANDSPITALI
RXO|AMOX^Amoxicillin 500mg^L||500|MG|CAP^Capsule^L|||||||||3||TID^Three times daily
RXR|PO^Oral^HL70162
RXE|^^^20240403090000^^R|AMOX^Amoxicillin 500mg^L|500|MG|CAP^Capsule^L|TID^Three times daily^L|||||||||||||||||||||20240403^20240410
```

---

## 19. ORU^R01 - Discharge summary with base64 ED OBX (PDF)

```
MSH|^~\&|HEKLA|LANDSPITALI|SAGA|LANDSPITALI|20240404100000||ORU^R01^ORU_R01|MSG20240404100000019|P|2.5|||AL|NE||8859/1
PID|1||1810912483^^^ISLAND^SS||Vilbergsson^Heiðar^^^Hr||19911018|M|||Hraunbær 88^^Reykjavík^^110^IS||^PRN^PH^^^354^5572180||||M||||||||||IS||||N
PV1|1|I|MED-3^312^1^LANDSPITALI^^^^MED|||||||INT^Internist^Pétursson^Hilmar^^^Dr|||MED||||ADM||||||||||||||||||LANDSPITALI||A|||20240315091200|||20240404100000
ORC|RE|ORD240404001||||||^^^20240404^^R||20240404100000|||Pétursson^Hilmar^^^Dr|||||LANDSPITALI
OBR|1|ORD240404001||18842-5^Discharge Summarization Note^LN|||20240404080000|||||||||||||||20240404100000|||F
OBX|1|TX|18842-5^Discharge Summary^LN||Patient treated for community-acquired pneumonia. Completed 7-day course of IV antibiotics followed by oral amoxicillin. Discharged in stable condition.||||||F|||20240404090000
OBX|2|ED|PDF^Discharge Summary^L||^application^pdf^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKERpc2NoYXJnZSBTdW1tYXJ5KSBUagpFVApFbmRzdHJlYW0KZW5kb2Jq||||||F|||20240404090000
```

---

## 20. ADT^A01 - Emergency admission

```
MSH|^~\&|HEKLA|LANDSPITALI|SAGA|LANDSPITALI|20240405221500||ADT^A01^ADT_A01|MSG20240405221500020|P|2.5|||AL|NE||8859/1
EVN|A01|20240405221500|||GERDUR^Gerður Ásgrímsdóttir
PID|1||2705772614^^^ISLAND^SS||Hákonarson^Friðmar^^^Hr||19770527|M|||Borgarbraut 32^^Selfoss^^800^IS||^PRN^PH^^^354^4823091|^WPN^PH^^^354^4823092||IS|M||||||||||IS||||N
PV1|1|E|ED-1^103^1^LANDSPITALI^^^^ER|||||||EM^Emergency Medicine^Halldórsdóttir^Þórunn^^^Dr|||EM||||EMR||||||||||||||||||LANDSPITALI||A|||20240405221500
PV2|||^Acute abdominal pain|||||||5||||||||||||||||||||||||Y
DG1|1|I10|R10.0^Acute abdomen^I10|||W
IN1|1|001^Sjúkratryggingar Íslands|9700|Sjúkratryggingar Íslands|Vínlandsleið 16^^Reykjavík^^105^IS|||||||||||||||||||||||||||||||||2705772614
```
