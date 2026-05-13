# Sunquest LIS - real HL7v2 ER7 messages

---

## 1. ORM^O01 - CBC order from emergency department

```
MSH|^~\&|HIS_ED|OTTAWA_CIVIC|SUNQUEST_LIS|TOH_LAB|20260401041500||ORM^O01^ORM_O01|SQ00001|P|2.5
PID|||1234567890^^^ON_HCN^JHN||Bernier^Marc^Andre^^Mr||19680412|M|||22 Carling Ave^^Ottawa^ON^K1S 2E1^CA||^^PH^6135551234
PV1||E|EMERG^BAY3^1^Ottawa Civic||||12345^Lapointe^Julie^^^Dr.^^CPSO|||EMER||||||||VN20260401001|||||||||||||||||||||||||||20260401041500
ORC|NW|ORD20260401001^HIS_ED|||||^^^^^R||20260401041500|||12345^Lapointe^Julie^^^Dr.^^CPSO
OBR|1|ORD20260401001^HIS_ED||CBC^Complete Blood Count^LN|||20260401041500||||S|||||12345^Lapointe^Julie^^^Dr.^^CPSO
```

## 2. ORM^O01 - STAT chemistry panel order

```
MSH|^~\&|HIS_ICU|KINGSTON_GEN|SUNQUEST_LIS|KGH_LAB|20260402060000||ORM^O01^ORM_O01|SQ00002|P|2.5
PID|||2345678901^^^ON_HCN^JHN||Michaud^Sylvie^Helene^^Mme||19750830|F|||88 Princess St^^Kingston^ON^K7L 1A5^CA||^^PH^6135552345
PV1||I|ICU^101^A^Kingston General||||23456^Bhatt^Rajesh^^^Dr.^^CPSO|||IMED||||||||VN20260402001|||||||||||||||||||||||||||20260402060000
ORC|NW|ORD20260402001^HIS_ICU|||||^^^^^S||20260402060000|||23456^Bhatt^Rajesh^^^Dr.^^CPSO
OBR|1|ORD20260402001^HIS_ICU||BMP^Basic Metabolic Panel^LN|||20260402060000||||S|||||23456^Bhatt^Rajesh^^^Dr.^^CPSO
```

## 3. ORU^R01 - CBC result with differential

```
MSH|^~\&|SUNQUEST_LIS|TOH_LAB|HIS_ED|OTTAWA_CIVIC|20260401053000||ORU^R01^ORU_R01|SQ00003|P|2.5
PID|||1234567890^^^ON_HCN^JHN||Bernier^Marc^Andre^^Mr||19680412|M|||22 Carling Ave^^Ottawa^ON^K1S 2E1^CA||^^PH^6135551234
OBR|1|ORD20260401001^HIS_ED|SPE20260401001^TOH_LAB|CBC^Complete Blood Count^LN|||20260401041500|||||||||1234567890^Bernier^Marc A^^^^||||||20260401053000||HEM|F
OBX|1|NM|6690-2^WBC^LN||14.5|x10*9/L|4.0-11.0|H|||F
OBX|2|NM|789-8^RBC^LN||4.82|x10*12/L|4.50-6.00|N|||F
OBX|3|NM|718-7^Hemoglobin^LN||148|g/L|130-170|N|||F
OBX|4|NM|4544-3^Hematocrit^LN||0.44|L/L|0.38-0.52|N|||F
OBX|5|NM|777-3^Platelets^LN||312|x10*9/L|150-400|N|||F
OBX|6|NM|770-8^Neutrophils^LN||82|%|40-70|H|||F
OBX|7|NM|736-9^Lymphocytes^LN||12|%|20-45|L|||F
OBX|8|NM|5905-5^Monocytes^LN||4|%|2-10|N|||F
OBX|9|NM|713-8^Eosinophils^LN||1|%|1-6|N|||F
OBX|10|NM|706-2^Basophils^LN||1|%|0-2|N|||F
```

## 4. ORU^R01 - STAT chemistry result with critical values

```
MSH|^~\&|SUNQUEST_LIS|KGH_LAB|HIS_ICU|KINGSTON_GEN|20260402070000||ORU^R01^ORU_R01|SQ00004|P|2.5
PID|||2345678901^^^ON_HCN^JHN||Michaud^Sylvie^Helene^^Mme||19750830|F|||88 Princess St^^Kingston^ON^K7L 1A5^CA||^^PH^6135552345
OBR|1|ORD20260402001^HIS_ICU|SPE20260402001^KGH_LAB|BMP^Basic Metabolic Panel^LN|||20260402060000|||||||||2345678901^Michaud^Sylvie H^^^^||||||20260402070000||CHEM|F
OBX|1|NM|2345-7^Glucose^LN||2.1|mmol/L|3.3-5.5|LL|||F
OBX|2|NM|2160-0^Creatinine^LN||245|umol/L|50-98|HH|||F
OBX|3|NM|3094-0^Urea^LN||28.5|mmol/L|2.1-8.5|HH|||F
OBX|4|NM|2951-2^Sodium^LN||126|mmol/L|136-145|LL|||F
OBX|5|NM|2823-3^Potassium^LN||6.4|mmol/L|3.5-5.1|HH|||F
OBX|6|NM|2075-0^Chloride^LN||94|mmol/L|98-106|L|||F
OBX|7|NM|1963-8^Bicarbonate^LN||16|mmol/L|22-29|LL|||F
OBX|8|NM|2532-0^Lactate^LN||5.8|mmol/L|0.5-2.2|HH|||F
```

## 5. ORM^O01 - blood culture order from internal medicine

```
MSH|^~\&|HIS_MED|HAMILTON_GEN|SUNQUEST_LIS|HHS_LAB|20260403082000||ORM^O01^ORM_O01|SQ00005|P|2.5
PID|||3456789012^^^ON_HCN^JHN||Caron^Francois^Joseph^^Mr||19800614|M|||14 Main St E^^Hamilton^ON^L8N 1E8^CA||^^PH^9055553456
PV1||I|MED^504^A^Hamilton General||||34567^Okafor^Chidi^^^Dr.^^CPSO|||IMED||||||||VN20260403001|||||||||||||||||||||||||||20260403082000
ORC|NW|ORD20260403001^HIS_MED|||||^^^^^S||20260403082000|||34567^Okafor^Chidi^^^Dr.^^CPSO
OBR|1|ORD20260403001^HIS_MED||BCULT^Blood Culture^LN|||20260403082000||||S|||||34567^Okafor^Chidi^^^Dr.^^CPSO|||||||||||^Fever 39.2C, rigors, suspected bacteremia
```

## 6. ORU^R01 - blood culture preliminary result

```
MSH|^~\&|SUNQUEST_LIS|HHS_LAB|HIS_MED|HAMILTON_GEN|20260404150000||ORU^R01^ORU_R01|SQ00006|P|2.5
PID|||3456789012^^^ON_HCN^JHN||Caron^Francois^Joseph^^Mr||19800614|M|||14 Main St E^^Hamilton^ON^L8N 1E8^CA||^^PH^9055553456
OBR|1|ORD20260403001^HIS_MED|SPE20260403001^HHS_LAB|BCULT^Blood Culture^LN|||20260403082000|||||||||3456789012^Caron^Francois J^^^^||||||20260404150000||MB|P
OBX|1|ST|600-7^Bacteria identified^LN||Gram positive cocci in clusters||||||P
OBX|2|ST|11475-1^Culture status^LN||Growth detected at 18 hours, aerobic bottle||||||P
```

## 7. ORU^R01 - blood culture final with sensitivities

```
MSH|^~\&|SUNQUEST_LIS|HHS_LAB|HIS_MED|HAMILTON_GEN|20260406091500||ORU^R01^ORU_R01|SQ00007|P|2.5
PID|||3456789012^^^ON_HCN^JHN||Caron^Francois^Joseph^^Mr||19800614|M|||14 Main St E^^Hamilton^ON^L8N 1E8^CA||^^PH^9055553456
OBR|1|ORD20260403001^HIS_MED|SPE20260403001^HHS_LAB|BCULT^Blood Culture^LN|||20260403082000|||||||||3456789012^Caron^Francois J^^^^||||||20260406091500||MB|F
OBX|1|ST|600-7^Bacteria identified^LN||Staphylococcus aureus (MSSA)||||||F
OBX|2|ST|18900-1^Colony count^LN||2/2 bottles positive||||||F
OBX|3|ST|18964-0^Oxacillin^LN||Susceptible||||||F
OBX|4|ST|18878-2^Cefazolin^LN||Susceptible||||||F
OBX|5|ST|18993-9^Vancomycin^LN||Susceptible||||||F
OBX|6|ST|18886-5^Clindamycin^LN||Susceptible||||||F
OBX|7|ST|18919-4^Gentamicin^LN||Susceptible||||||F
OBX|8|ST|18996-2^Trimethoprim-Sulfamethoxazole^LN||Susceptible||||||F
```

## 8. ORM^O01 - crossmatch order from blood bank

```
MSH|^~\&|HIS_SURG|SUNNYBROOK_HSC|SUNQUEST_LIS|SBK_BLOODBANK|20260407054500||ORM^O01^ORM_O01|SQ00008|P|2.5
PID|||4567890123^^^ON_HCN^JHN||Nguyen^Thi^Lan^^Ms||19870423|F|||320 Bloor St W^^Toronto^ON^M5S 1W5^CA||^^PH^4165554567
PV1||I|SURG^OR3^1^Sunnybrook HSC||||45678^Desjardins^Francois^^^Dr.^^CPSO|||SURG||||||||VN20260407001|||||||||||||||||||||||||||20260407054500
ORC|NW|ORD20260407001^HIS_SURG|||||^^^^^S||20260407054500|||45678^Desjardins^Francois^^^Dr.^^CPSO
OBR|1|ORD20260407001^HIS_SURG||XMATCH^Crossmatch 2 Units pRBC^LN|||20260407054500||||S|||||45678^Desjardins^Francois^^^Dr.^^CPSO|||||||||||^Pre-op hip arthroplasty, Hgb 98 g/L
```

## 9. ORU^R01 - blood bank type and screen result

```
MSH|^~\&|SUNQUEST_LIS|SBK_BLOODBANK|HIS_SURG|SUNNYBROOK_HSC|20260407063000||ORU^R01^ORU_R01|SQ00009|P|2.5
PID|||4567890123^^^ON_HCN^JHN||Nguyen^Thi^Lan^^Ms||19870423|F|||320 Bloor St W^^Toronto^ON^M5S 1W5^CA||^^PH^4165554567
OBR|1|ORD20260407001^HIS_SURG|SPE20260407001^SBK_BLOODBANK|XMATCH^Crossmatch^LN|||20260407054500|||||||||4567890123^Nguyen^Thi L^^^^||||||20260407063000||BB|F
OBX|1|ST|882-1^ABO Group^LN||A||||||F
OBX|2|ST|10331-7^Rh Type^LN||Positive||||||F
OBX|3|ST|890-4^Antibody Screen^LN||Negative||||||F
OBX|4|ST|50599-1^Crossmatch^LN||Compatible, 2 units pRBC available||||||F
```

## 10. ORU^R01 - coagulation panel pre-surgery

```
MSH|^~\&|SUNQUEST_LIS|TOH_LAB|HIS_SURG|OTTAWA_GENERAL|20260408091000||ORU^R01^ORU_R01|SQ00010|P|2.5
PID|||5678901234^^^ON_HCN^JHN||Pelletier^Martin^Philippe^^Mr||19590827|M|||67 Bank St^^Ottawa^ON^K1P 5N2^CA||^^PH^6135555678
OBR|1|ORD20260408001^HIS_SURG|SPE20260408001^TOH_LAB|COAG^Coagulation Panel^LN|||20260408074500|||||||||5678901234^Pelletier^Martin P^^^^||||||20260408091000||HEM|F
OBX|1|NM|5902-2^PT^LN||12.5|s|11.0-13.5|N|||F
OBX|2|NM|6301-6^INR^LN||1.1||<1.3|N|||F
OBX|3|NM|3173-2^aPTT^LN||30|s|25-38|N|||F
OBX|4|NM|3255-7^Fibrinogen^LN||3.2|g/L|2.0-4.0|N|||F
```

## 11. ORU^R01 - urinalysis with microscopy

```
MSH|^~\&|SUNQUEST_LIS|KGH_LAB|HIS_MED|KINGSTON_GEN|20260409113000||ORU^R01^ORU_R01|SQ00011|P|2.5
PID|||6789012345^^^ON_HCN^JHN||Roy^Genevieve^Marie^^Mme||19910315|F|||22 Clergy St^^Kingston^ON^K7K 3N3^CA||^^PH^6135556789
OBR|1|ORD20260409001^HIS_MED|SPE20260409001^KGH_LAB|UA^Urinalysis with Microscopy^LN|||20260409081000|||||||||6789012345^Roy^Genevieve M^^^^||||||20260409113000||CHEM|F
OBX|1|ST|5778-6^Color^LN||Dark Yellow||||||F
OBX|2|ST|5767-9^Appearance^LN||Hazy||||||F
OBX|3|NM|5803-2^pH^LN||5.5||5.0-8.0|N|||F
OBX|4|NM|5811-5^Specific Gravity^LN||1.028||1.005-1.030|N|||F
OBX|5|ST|20454-5^Leukocyte Esterase^LN||2+||Negative|A|||F
OBX|6|ST|5802-4^Nitrite^LN||Positive||Negative|A|||F
OBX|7|NM|5821-4^WBC Micro^LN||85|/HPF|0-5|HH|||F
OBX|8|NM|13945-1^RBC Micro^LN||15|/HPF|0-3|H|||F
OBX|9|ST|25145-4^Bacteria^LN||Many||||||F
```

## 12. ORM^O01 - microbiology wound culture order

```
MSH|^~\&|HIS_SURG|LHSC_UNIVERSITY|SUNQUEST_LIS|LHSC_LAB|20260410093000||ORM^O01^ORM_O01|SQ00012|P|2.5
PID|||7890123456^^^ON_HCN^JHN||Lavoie^Pierre^Jean^^Mr||19720809|M|||200 Richmond St^^London^ON^N6A 3L4^CA||^^PH^5195557890
PV1||I|SURG^302^A^London Health Sciences University||||56789^Chen^Li^^^Dr.^^CPSO|||SURG||||||||VN20260410001|||||||||||||||||||||||||||20260410093000
ORC|NW|ORD20260410001^HIS_SURG||||||20260410093000|||56789^Chen^Li^^^Dr.^^CPSO
OBR|1|ORD20260410001^HIS_SURG||WCULT^Wound Culture^LN|||20260410093000||||R|||||56789^Chen^Li^^^Dr.^^CPSO|||||||||||^Post-op wound dehiscence, left lower quadrant
```

## 13. ORU^R01 - wound culture result with sensitivities

```
MSH|^~\&|SUNQUEST_LIS|LHSC_LAB|HIS_SURG|LHSC_UNIVERSITY|20260412153000||ORU^R01^ORU_R01|SQ00013|P|2.5
PID|||7890123456^^^ON_HCN^JHN||Lavoie^Pierre^Jean^^Mr||19720809|M|||200 Richmond St^^London^ON^N6A 3L4^CA||^^PH^5195557890
OBR|1|ORD20260410001^HIS_SURG|SPE20260410001^LHSC_LAB|WCULT^Wound Culture^LN|||20260410093000|||||||||7890123456^Lavoie^Pierre J^^^^||||||20260412153000||MB|F
OBX|1|ST|600-7^Bacteria identified^LN||Escherichia coli||||||F
OBX|2|ST|600-7^Bacteria identified^LN||Bacteroides fragilis||||||F
OBX|3|ST|18864-9^Ampicillin (E. coli)^LN||Resistant||||||F
OBX|4|ST|18906-8^Ceftriaxone (E. coli)^LN||Susceptible||||||F
OBX|5|ST|18865-6^Ciprofloxacin (E. coli)^LN||Susceptible||||||F
OBX|6|ST|18928-5^Metronidazole (B. fragilis)^LN||Susceptible||||||F
OBX|7|ST|18943-4^Piperacillin-Tazobactam (B. fragilis)^LN||Susceptible||||||F
```

## 14. ORU^R01 - troponin serial results for chest pain workup

```
MSH|^~\&|SUNQUEST_LIS|TOH_LAB|HIS_ED|OTTAWA_CIVIC|20260413044500||ORU^R01^ORU_R01|SQ00014|P|2.5
PID|||8901234567^^^ON_HCN^JHN||Poirier^Jacques^Philippe^^Mr||19650221|M|||500 University Ave^^Ottawa^ON^K1N 6N5^CA||^^PH^6135558901
OBR|1|ORD20260413001^HIS_ED|SPE20260413001^TOH_LAB|TROP^High-Sensitivity Troponin^LN|||20260413020000|||||||||8901234567^Poirier^Jacques P^^^^||||||20260413044500||CHEM|F
OBX|1|NM|89579-7^hs-Troponin I Baseline^LN||28|ng/L|<26|H||A||F|||20260413023000
OBX|2|NM|89579-7^hs-Troponin I 3hr^LN||145|ng/L|<26|HH||A||F|||20260413050000
```

## 15. ORU^R01 - CSF analysis for meningitis workup

```
MSH|^~\&|SUNQUEST_LIS|HHS_LAB|HIS_MED|HAMILTON_GEN|20260414110000||ORU^R01^ORU_R01|SQ00015|P|2.5
PID|||9012345678^^^ON_HCN^JHN||Desjardins^Amelie^Rose^^Mme||19951118|F|||45 James St N^^Hamilton^ON^L8R 2K5^CA||^^PH^9055559012
OBR|1|ORD20260414001^HIS_MED|SPE20260414001^HHS_LAB|CSF^Cerebrospinal Fluid Analysis^LN|||20260414083000|||||||||9012345678^Desjardins^Amelie R^^^^||||||20260414110000||CHEM|F
OBX|1|NM|26449-9^CSF WBC^LN||850|cells/uL|0-5|HH|||F
OBX|2|NM|26450-7^CSF Neutrophils^LN||90|%|0-6|HH|||F
OBX|3|NM|2342-4^CSF Glucose^LN||1.5|mmol/L|2.5-4.5|LL|||F
OBX|4|NM|2880-3^CSF Protein^LN||2.8|g/L|0.15-0.45|HH|||F
OBX|5|ST|630-4^CSF Gram Stain^LN||Gram negative diplococci||||||F
```

## 16. ORU^R01 - arterial blood gas result

```
MSH|^~\&|SUNQUEST_LIS|KGH_LAB|HIS_ICU|KINGSTON_GEN|20260415063000||ORU^R01^ORU_R01|SQ00016|P|2.5
PID|||0123456789^^^ON_HCN^JHN||Lessard^Bruno^Michel^^Mr||19530718|M|||330 Johnson St^^Kingston^ON^K7L 1Y2^CA||^^PH^6135550123
OBR|1|ORD20260415001^HIS_ICU|SPE20260415001^KGH_LAB|ABG^Arterial Blood Gas^LN|||20260415060000|||||||||0123456789^Lessard^Bruno M^^^^||||||20260415063000||CHEM|F
OBX|1|NM|2744-1^pH^LN||7.28||7.35-7.45|L|||F
OBX|2|NM|2019-8^pCO2^LN||58|mmHg|35-45|H|||F
OBX|3|NM|2703-7^pO2^LN||62|mmHg|80-100|L|||F
OBX|4|NM|1960-4^Bicarbonate^LN||27|mmol/L|22-26|H|||F
OBX|5|NM|2713-6^Base Excess^LN||-1|mmol/L|-2 to +2|N|||F
OBX|6|NM|2708-6^O2 Saturation^LN||89|%|95-100|L|||F
OBX|7|NM|2532-0^Lactate^LN||3.5|mmol/L|0.5-2.2|H|||F
```

## 17. ORU^R01 - histopathology report with embedded PDF

```
MSH|^~\&|SUNQUEST_LIS|TOH_PATH|HIS_SURG|OTTAWA_GENERAL|20260416161500||ORU^R01^ORU_R01|SQ00017|P|2.5
PID|||1122334455^^^ON_HCN^JHN||Girard^Monique^Helene^^Mme||19680910|F|||140 Bay St^^Ottawa^ON^K1R 7S8^CA||^^PH^6135551122
OBR|1|ORD20260416001^HIS_SURG|SPE20260416001^TOH_PATH|PATH^Surgical Pathology^LN|||20260414090000|||||||||1122334455^Girard^Monique H^^^^||||||20260416161500||AP|F
OBX|1|FT|22637-3^Pathology Report^LN||Specimen: Right hemicolectomy. Diagnosis: Moderately differentiated adenocarcinoma of the ascending colon, 4.2 cm. Invasion through muscularis propria into pericolonic fat (pT3). 0 of 22 lymph nodes positive (pN0). Margins clear.||||||F
OBX|2|ED|PDF^Pathology Report PDF^LN||^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2Jq||||||F
```

## 18. ORU^R01 - bone marrow aspirate with embedded microscopy image

```
MSH|^~\&|SUNQUEST_LIS|HHS_LAB|HIS_MED|HAMILTON_GEN|20260417150000||ORU^R01^ORU_R01|SQ00018|P|2.5
PID|||2233445566^^^ON_HCN^JHN||Morin^Catherine^Joanne^^Mme||19780525|F|||85 King St W^^Hamilton^ON^L8P 1A2^CA||^^PH^9055552233
OBR|1|ORD20260417001^HIS_MED|SPE20260417001^HHS_LAB|BMA^Bone Marrow Aspirate^LN|||20260417093000|||||||||2233445566^Morin^Catherine J^^^^||||||20260417150000||HEM|F
OBX|1|FT|33721-2^Bone Marrow Report^LN||Hypercellular marrow (90%) for age. Myeloid to erythroid ratio 8:1. Marked granulocytic hyperplasia. Blast count 2%. Megakaryocytes adequate. Iron stores present. No evidence of lymphoma or metastatic disease.||||||F
OBX|2|ED|IMG^Bone Marrow Aspirate Image^LN||^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL||||||F
```

## 19. ORM^O01 - drug level order for vancomycin trough

```
MSH|^~\&|HIS_MED|LHSC_UNIVERSITY|SUNQUEST_LIS|LHSC_LAB|20260418053000||ORM^O01^ORM_O01|SQ00019|P|2.5
PID|||3344556677^^^ON_HCN^JHN||Gagnon^Pierre^Louis^^Mr||19850617|M|||89 Elgin St^^London^ON^N5Y 3L5^CA||^^PH^5195553344
PV1||I|MED^601^A^London Health Sciences University||||67890^Patel^Ravi^^^Dr.^^CPSO|||IMED||||||||VN20260418001|||||||||||||||||||||||||||20260418053000
ORC|NW|ORD20260418001^HIS_MED||||||20260418053000|||67890^Patel^Ravi^^^Dr.^^CPSO
OBR|1|ORD20260418001^HIS_MED||VANC^Vancomycin Trough Level^LN|||20260418053000||||S|||||67890^Patel^Ravi^^^Dr.^^CPSO|||||||||||^Trough level, next dose at 0600
```

## 20. ORU^R01 - vancomycin trough result with scanned lab worksheet PDF

```
MSH|^~\&|SUNQUEST_LIS|LHSC_LAB|HIS_MED|LHSC_UNIVERSITY|20260418070000||ORU^R01^ORU_R01|SQ00020|P|2.5
PID|||3344556677^^^ON_HCN^JHN||Gagnon^Pierre^Louis^^Mr||19850617|M|||89 Elgin St^^London^ON^N5Y 3L5^CA||^^PH^5195553344
OBR|1|ORD20260418001^HIS_MED|SPE20260418001^LHSC_LAB|VANC^Vancomycin Trough Level^LN|||20260418053000|||||||||3344556677^Gagnon^Pierre L^^^^||||||20260418070000||CHEM|F
OBX|1|NM|4090-7^Vancomycin Trough^LN||22.5|mg/L|15.0-20.0|H|||F
OBX|2|ED|PDF^Lab Worksheet Scan^LN||^AP^^Base64^JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8IC9NYXJrZWQgdHJ1ZSA+PgovU3RydWN0VHJlZVJvb3QgMyAwIFIKPj4KZW5kb2Jq||||||F
```
