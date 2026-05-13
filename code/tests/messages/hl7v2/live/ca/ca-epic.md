# Epic - real HL7v2 ER7 messages

---

## 1. ADT^A01 - pediatric inpatient admission

```
MSH|^~\&|EPIC|SICKKIDS|ADT_RECV|HIS_SYS|20260509080000||ADT^A01^ADT_A01|EP000001|P|2.5.1
EVN|A01|20260509080000
PID|||3782619054^^^ON_HN^JHN||Lefebvre^Liam^Andre||20190627|M|||628 University Ave^^Toronto^ON^M5G 1Y3^CA||^PRN^PH^^1^416^7234812||||MRN612847
PD1||||45612^Reynolds^Catherine^^^Dr.^^MD
PV1||I|7WEST^710^A^SICKKIDS||||45612^Reynolds^Catherine^^^Dr.^^MD|78923^Mehta^Aarav^^^Dr.^^MD|||PED||||7||VIS2026050901|||||||||||||||||||||||||||20260509080000
NK1|1|Lefebvre^Sophie||^PRN^PH^^1^416^5538291|||||||||||||||||||||||||||||MTH
```

---

## 2. ADT^A03 - pediatric discharge

```
MSH|^~\&|EPIC|SICKKIDS|ADT_RECV|HIS_SYS|20260512140000||ADT^A03^ADT_A03|EP000002|P|2.5.1
EVN|A03|20260512140000
PID|||3782619054^^^ON_HN^JHN||Lefebvre^Liam^Andre||20190627|M|||628 University Ave^^Toronto^ON^M5G 1Y3^CA||^PRN^PH^^1^416^7234812
PV1||I|7WEST^710^A^SICKKIDS||||45612^Reynolds^Catherine^^^Dr.^^MD|78923^Mehta^Aarav^^^Dr.^^MD|||PED||||7||VIS2026050901|||||||||||||||||||||||||||20260512140000
DG1|1||J21.0^Acute bronchiolitis due to RSV^I10||20260509|A
```

---

## 3. ADT^A04 - outpatient registration at CHU Sainte-Justine

```
MSH|^~\&|EPIC|CHU_SJ|ADT_RECV|HIS_SYS|20260510093000||ADT^A04^ADT_A01|EP000003|P|2.5.1
EVN|A04|20260510093000
PID|||GAUT08092312^^^QC_RAMQ^JHN||Gauthier^Florence^Anne-Sophie||20080923|F|||4218 Rue Sainte-Catherine E^^Montreal^QC^H1V 1Y5^CA||^PRN^PH^^1^514^4781923||||MRN612951
PV1||O|ORTHO^CLINIC2^1^CHU_SJ||||23148^Dubois^Pascal^^^Dr.^^MD|||ORTHO||||9||VIS2026051001|||||||||||||||||||||||||||20260510093000
```

---

## 4. ADT^A08 - patient update (bilingual name)

```
MSH|^~\&|EPIC|CHU_SJ|ADT_RECV|HIS_SYS|20260511100000||ADT^A08^ADT_A01|EP000004|P|2.5.1
EVN|A08|20260511100000
PID|||GAUT08092312^^^QC_RAMQ^JHN||Gauthier^Florence^Anne-Sophie||20080923|F|||1875 Boul Rene-Levesque O^^Montreal^QC^H3H 2N6^CA||^PRN^PH^^1^514^9237148||||MRN612951
PV1||O|ORTHO^CLINIC2^1^CHU_SJ||||23148^Dubois^Pascal^^^Dr.^^MD
NK1|1|Gauthier^Pascal||^PRN^PH^^1^514^9237149|||||||||||||||||||||||||||||FTH
```

---

## 5. ADT^A31 - update person information

```
MSH|^~\&|EPIC|SICKKIDS|MPI_SYS|REG_SYS|20260510110000||ADT^A31^ADT_A05|EP000005|P|2.5.1
EVN|A31|20260510110000
PID|||3782619054^^^ON_HN^JHN||Lefebvre^Liam^Andre||20190627|M|||89 Queens Park Cres^^Toronto^ON^M5S 2C7^CA||^PRN^PH^^1^416^4827193||||MRN612847
PV1||N
```

---

## 6. ADT^A40 - patient merge

```
MSH|^~\&|EPIC|SICKKIDS|MPI_SYS|REG_SYS|20260512080000||ADT^A40^ADT_A39|EP000006|P|2.5.1
EVN|A40|20260512080000
PID|||3782619054^^^ON_HN^JHN||Lefebvre^Liam^Andre||20190627|M|||628 University Ave^^Toronto^ON^M5G 1Y3^CA
MRG|6128493075^^^ON_HN^JHN||VIS2025110301
```

---

## 7. ORU^R01 - pediatric blood culture result

```
MSH|^~\&|EPIC|SICKKIDS|LAB_RECV|EMR_SYS|20260511150000||ORU^R01^ORU_R01|EP000007|P|2.5.1
PID|||3782619054^^^ON_HN^JHN||Lefebvre^Liam^Andre||20190627|M|||628 University Ave^^Toronto^ON^M5G 1Y3^CA
ORC|RE|LAB300100|LAB400200||CM||||20260509100000|||45612^Reynolds^Catherine^^^Dr.^^MD
OBR|1|LAB300100|LAB400200|87040-2^Blood culture^LN|||20260509100000|||||||||45612^Reynolds^Catherine^^^Dr.^^MD||||||20260511143000|||F
OBX|1|CWE|600-7^Bacteria identified^LN||No growth^^L||||||F
OBX|2|ST|19146-0^Reference lab comment^LN||No growth after 5 days. Aerobic and anaerobic bottles negative.||||||F
```

---

## 8. ORU^R01 - pediatric CBC with differential

```
MSH|^~\&|EPIC|SICKKIDS|LAB_RECV|EMR_SYS|20260509120000||ORU^R01^ORU_R01|EP000008|P|2.5.1
PID|||3782619054^^^ON_HN^JHN||Lefebvre^Liam^Andre||20190627|M|||628 University Ave^^Toronto^ON^M5G 1Y3^CA
ORC|RE|LAB300200|LAB400300||CM||||20260509083000|||45612^Reynolds^Catherine^^^Dr.^^MD
OBR|1|LAB300200|LAB400300|57021-8^CBC with differential^LN|||20260509080000|||||||||45612^Reynolds^Catherine^^^Dr.^^MD||||||20260509113000|||F
OBX|1|NM|718-7^Hemoglobin^LN||112|g/L|105-135|N|||F
OBX|2|NM|6690-2^Leukocytes^LN||14.2|x10E9/L|5.0-15.5|N|||F
OBX|3|NM|777-3^Platelets^LN||289|x10E9/L|150-400|N|||F
OBX|4|NM|770-8^Neutrophils^LN||8.5|x10E9/L|1.5-8.5|N|||F
OBX|5|NM|731-0^Lymphocytes^LN||4.1|x10E9/L|2.0-8.0|N|||F
OBX|6|NM|742-7^Monocytes^LN||1.2|x10E9/L|0.2-1.0|H|||F
```

---

## 9. ORU^R01 - echocardiogram report with embedded PDF

```
MSH|^~\&|EPIC|SICKKIDS|CARDIO_RECV|EMR_SYS|20260510160000||ORU^R01^ORU_R01|EP000009|P|2.5.1
PID|||3782619054^^^ON_HN^JHN||Lefebvre^Liam^Andre||20190627|M|||628 University Ave^^Toronto^ON^M5G 1Y3^CA
ORC|RE|ECHO300100|ECHO400200||CM||||20260510130000|||67234^Tan^Wei-Ming^^^Dr.^^MD
OBR|1|ECHO300100|ECHO400200|34552-0^Echocardiography^LN|||20260510130000|||||||||67234^Tan^Wei-Ming^^^Dr.^^MD||||||20260510155000|||F
OBX|1|ED|PDF^Echocardiogram Report^EPIC||^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4K||||||F
OBX|2|FT|34552-0^Echo Interpretation^LN||Normal biventricular size and systolic function. No valvular abnormalities. No pericardial effusion. LVEF 65%.||||||F
```

---

## 10. ORU^R01 - fetal ultrasound with JPEG image

```
MSH|^~\&|EPIC|CHU_SJ|OB_RECV|EMR_SYS|20260511110000||ORU^R01^ORU_R01|EP000010|P|2.5.1
PID|||MORI91051803^^^QC_RAMQ^JHN||Morin^Catherine^Josee||19910518|F|||3742 Boul des Laurentides^^Laval^QC^H7K 2J4^CA
ORC|RE|US300200|US400300||CM||||20260511090000|||78451^Pelletier^Sophie^^^Dr.^^MD
OBR|1|US300200|US400300|76811-2^OB Ultrasound^LN|||20260511090000|||||||||78451^Pelletier^Sophie^^^Dr.^^MD||||||20260511103000|||F
OBX|1|ED|IMG^Fetal Ultrasound Image^EPIC||^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDA==||||||F
OBX|2|FT|76811-2^OB US Interpretation^LN||Single viable intrauterine pregnancy. Gestational age 20 weeks 3 days. Normal anatomy survey. EFW 350g (50th percentile). AFI normal.||||||F
```

---

## 11. ORM^O01 - lab order for metabolic screen

```
MSH|^~\&|EPIC|SICKKIDS|LAB_SYS|CORE_LAB|20260509074500||ORM^O01^ORM_O01|EP000011|P|2.5.1
PID|||3782619054^^^ON_HN^JHN||Lefebvre^Liam^Andre||20190627|M|||628 University Ave^^Toronto^ON^M5G 1Y3^CA
PV1||I|7WEST^710^A^SICKKIDS||||45612^Reynolds^Catherine^^^Dr.^^MD
ORC|NW|LAB300300|||||||20260509074000|||45612^Reynolds^Catherine^^^Dr.^^MD
OBR|1|LAB300300||24323-8^CMP^LN|||20260509074500|||||||||45612^Reynolds^Catherine^^^Dr.^^MD
ORC|NW|LAB300301|||||||20260509074000|||45612^Reynolds^Catherine^^^Dr.^^MD
OBR|2|LAB300301||2951-2^Electrolyte panel^LN|||20260509074500|||||||||45612^Reynolds^Catherine^^^Dr.^^MD
```

---

## 12. ORM^O01 - MRI order

```
MSH|^~\&|EPIC|SICKKIDS|RIS_SYS|RAD_DEPT|20260510080000||ORM^O01^ORM_O01|EP000012|P|2.5.1
PID|||3782619054^^^ON_HN^JHN||Lefebvre^Liam^Andre||20190627|M|||628 University Ave^^Toronto^ON^M5G 1Y3^CA
PV1||I|7WEST^710^A^SICKKIDS||||45612^Reynolds^Catherine^^^Dr.^^MD
ORC|NW|RAD300400|||||||20260510075000|||78923^Mehta^Aarav^^^Dr.^^MD
OBR|1|RAD300400||70553-6^MRI Brain without contrast^LN|||20260510080000|||||||||78923^Mehta^Aarav^^^Dr.^^MD||||||||||||ROUTINE
```

---

## 13. SIU^S12 - follow-up appointment scheduled

```
MSH|^~\&|EPIC|SICKKIDS|SCHED_RECV|CLINIC_SYS|20260512090000||SIU^S12^SIU_S12|EP000013|P|2.5.1
SCH|APT20260519001||||||ROUTINE^Routine^HL70276|FOLLOWUP^Follow-up visit^HL70277|20|MIN|^^20^20260519100000^20260519102000|45612^Reynolds^Catherine^^^Dr.^^MD
PID|||3782619054^^^ON_HN^JHN||Lefebvre^Liam^Andre||20190627|M|||628 University Ave^^Toronto^ON^M5G 1Y3^CA
PV1||O|PED^CLINIC1^1^SICKKIDS||||45612^Reynolds^Catherine^^^Dr.^^MD
RGS|1
AIS|1||PED_FOLLOWUP^Pediatric Follow-up^LOCAL|20260519100000|0|MIN|20|MIN
AIP|1||45612^Reynolds^Catherine^^^Dr.^^MD|||||20260519100000|0|MIN|20|MIN
```

---

## 14. MDM^T02 - discharge summary document

```
MSH|^~\&|EPIC|SICKKIDS|DOC_RECV|EMR_SYS|20260512150000||MDM^T02^MDM_T02|EP000014|P|2.5.1
EVN|T02|20260512150000
PID|||3782619054^^^ON_HN^JHN||Lefebvre^Liam^Andre||20190627|M|||628 University Ave^^Toronto^ON^M5G 1Y3^CA
PV1||I|7WEST^710^A^SICKKIDS||||45612^Reynolds^Catherine^^^Dr.^^MD
TXA|1|DS^Discharge Summary^HL70270|TX|20260512140000||20260512150000|||||45612^Reynolds^Catherine^^^Dr.^^MD||DOC7891011||||||AU
OBX|1|FT|DS^Discharge Summary Text^LOCAL||Diagnosis: Acute bronchiolitis (RSV positive). Hospital course: Admitted for oxygen therapy and supportive care. Weaned to room air by day 3. Feeding well at discharge. Follow-up in 1 week.||||||F
```

---

## 15. ORU^R01 - RSV rapid antigen test

```
MSH|^~\&|EPIC|SICKKIDS|LAB_RECV|EMR_SYS|20260509100000||ORU^R01^ORU_R01|EP000015|P|2.5.1
PID|||3782619054^^^ON_HN^JHN||Lefebvre^Liam^Andre||20190627|M|||628 University Ave^^Toronto^ON^M5G 1Y3^CA
ORC|RE|LAB300400|LAB400500||CM||||20260509085000|||45612^Reynolds^Catherine^^^Dr.^^MD
OBR|1|LAB300400|LAB400500|92131-2^RSV Ag rapid^LN|||20260509085000|||||||||45612^Reynolds^Catherine^^^Dr.^^MD||||||20260509095000|||F
OBX|1|CWE|92131-2^RSV antigen^LN||260373001^Detected^SCT||||||F
```

---

## 16. MDM^T02 - consultation letter (French)

```
MSH|^~\&|EPIC|CHU_SJ|DOC_RECV|EMR_SYS|20260510153000||MDM^T02^MDM_T02|EP000016|P|2.5.1
EVN|T02|20260510153000
PID|||GAUT08092312^^^QC_RAMQ^JHN||Gauthier^Florence^Anne-Sophie||20080923|F|||4218 Rue Sainte-Catherine E^^Montreal^QC^H1V 1Y5^CA
PV1||O|ORTHO^CLINIC2^1^CHU_SJ||||23148^Dubois^Pascal^^^Dr.^^MD
TXA|1|CN^Consultation Note^HL70270|TX|20260510150000||20260510153000|||||23148^Dubois^Pascal^^^Dr.^^MD||DOC7891012||||||AU
OBX|1|FT|CN^Consultation Note Text^LOCAL||Consultation en orthopedi pediatrique. Scoliose idiopathique adolescente. Angle de Cobb 22 degres. Observation recommandee avec controle radiologique dans 6 mois.||||||F
```

---

## 17. ORU^R01 - neonatal bilirubin

```
MSH|^~\&|EPIC|CHU_SJ|LAB_RECV|EMR_SYS|20260511080000||ORU^R01^ORU_R01|EP000017|P|2.5.1
PID|||ROY26050412^^^QC_RAMQ^JHN||Roy^Olivia^Marie||20260504|F|||2945 Rue Guy^^Montreal^QC^H3H 2L8^CA
ORC|RE|LAB300500|LAB400600||CM||||20260511070000|||34812^Bouchard^Veronique^^^Dr.^^MD
OBR|1|LAB300500|LAB400600|58941-6^Total bilirubin neonatal^LN|||20260511065000|||||||||34812^Bouchard^Veronique^^^Dr.^^MD||||||20260511075000|||F
OBX|1|NM|58941-6^Total bilirubin^LN||185|umol/L|0-205|N|||F
OBX|2|NM|1971-1^Direct bilirubin^LN||12|umol/L|0-34|N|||F
```

---

## 18. SIU^S12 - surgical scheduling

```
MSH|^~\&|EPIC|CHU_SJ|SCHED_RECV|OR_SYS|20260511140000||SIU^S12^SIU_S12|EP000018|P|2.5.1
SCH|APT20260525001||||||ELECTIVE^Elective^HL70276|SURGERY^Surgical procedure^HL70277|90|MIN|^^90^20260525080000^20260525093000|23148^Dubois^Pascal^^^Dr.^^MD
PID|||GAUT08092312^^^QC_RAMQ^JHN||Gauthier^Florence^Anne-Sophie||20080923|F|||4218 Rue Sainte-Catherine E^^Montreal^QC^H1V 1Y5^CA
PV1||P|SURG^OR2^1^CHU_SJ||||23148^Dubois^Pascal^^^Dr.^^MD
RGS|1
AIS|1||SPINE_BRACE^Spinal bracing procedure^LOCAL|20260525080000|0|MIN|90|MIN
AIP|1||23148^Dubois^Pascal^^^Dr.^^MD|||||20260525080000|0|MIN|90|MIN
```

---

## 19. ORU^R01 - MRI brain report with embedded PDF

```
MSH|^~\&|EPIC|SICKKIDS|RAD_RECV|EMR_SYS|20260510170000||ORU^R01^ORU_R01|EP000019|P|2.5.1
PID|||3782619054^^^ON_HN^JHN||Lefebvre^Liam^Andre||20190627|M|||628 University Ave^^Toronto^ON^M5G 1Y3^CA
ORC|RE|RAD300500|RAD400600||CM||||20260510100000|||78923^Mehta^Aarav^^^Dr.^^MD
OBR|1|RAD300500|RAD400600|70553-6^MRI Brain^LN|||20260510100000|||||||||78923^Mehta^Aarav^^^Dr.^^MD||||||20260510163000|||F
OBX|1|ED|PDF^MRI Brain Report^EPIC||^AP^^Base64^JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFIvTWFya0luZm88PC9UeXBlL01hcmtJbmZvL01hcmtlZCB0cnVlPj4+PgplbmRvYmoKMiAwIG9iago8PC9UeXBl||||||F
OBX|2|FT|70553-6^MRI Brain Impression^LN||Normal MRI brain for age. No intracranial mass, hemorrhage, or hydrocephalus. Myelination pattern appropriate for age.||||||F
```

---

## 20. ORU^R01 - respiratory viral panel

```
MSH|^~\&|EPIC|SICKKIDS|LAB_RECV|EMR_SYS|20260509130000||ORU^R01^ORU_R01|EP000020|P|2.5.1
PID|||3782619054^^^ON_HN^JHN||Lefebvre^Liam^Andre||20190627|M|||628 University Ave^^Toronto^ON^M5G 1Y3^CA
ORC|RE|LAB300600|LAB400700||CM||||20260509085000|||45612^Reynolds^Catherine^^^Dr.^^MD
OBR|1|LAB300600|LAB400700|92143-7^Resp viral panel^LN|||20260509085000|||||||||45612^Reynolds^Catherine^^^Dr.^^MD||||||20260509123000|||F
OBX|1|CWE|92131-2^RSV^LN||260373001^Detected^SCT||||||F
OBX|2|CWE|92142-9^Influenza A^LN||260415000^Not detected^SCT||||||F
OBX|3|CWE|92141-1^Influenza B^LN||260415000^Not detected^SCT||||||F
OBX|4|CWE|94500-6^SARS-CoV-2^LN||260415000^Not detected^SCT||||||F
OBX|5|CWE|88891-7^hMPV^LN||260415000^Not detected^SCT||||||F
OBX|6|CWE|92857-2^Adenovirus^LN||260415000^Not detected^SCT||||||F
```
