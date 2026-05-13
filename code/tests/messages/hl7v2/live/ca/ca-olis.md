# OLIS (Ontario Laboratories Information System) - real HL7v2 ER7 messages

---

## 1. ORU^R01 - CBC with differential

```
MSH|^~\&|OLIS_LIS|TORONTO_GEN|OLIS|ON_EHIS|20260509100000||ORU^R01^ORU_R01|OL000001|P|2.5
PID|||1234567890^^^ON_HN^JHN||Singh^Amrit^Kaur||19650420|F|||300 Bloor St W^^Toronto^ON^M5S 1W3^CA||^PRN^PH^^1^416^7891234
ORC|RE|OL100001|OL200001||CM||||20260509070000|||88901^Martinez^Carlos^^^Dr.^^MD
OBR|1|OL100001|OL200001|58410-2^CBC panel^LN|||20260509064500|||||||||88901^Martinez^Carlos^^^Dr.^^MD||||||20260509093000|||F
OBX|1|NM|718-7^Hemoglobin^LN||125|g/L|120-160|N|||F
OBX|2|NM|6690-2^Leukocytes^LN||6.8|x10E9/L|4.0-11.0|N|||F
OBX|3|NM|789-8^Erythrocytes^LN||4.22|x10E12/L|3.80-5.20|N|||F
OBX|4|NM|787-2^MCV^LN||86.3|fL|80.0-100.0|N|||F
OBX|5|NM|777-3^Platelets^LN||198|x10E9/L|150-400|N|||F
OBX|6|NM|770-8^Neutrophils^LN||3.9|x10E9/L|2.0-7.5|N|||F
OBX|7|NM|731-0^Lymphocytes^LN||2.1|x10E9/L|1.0-4.0|N|||F
OBX|8|NM|742-7^Monocytes^LN||0.5|x10E9/L|0.2-1.0|N|||F
```

---

## 2. ORU^R01 - comprehensive metabolic panel

```
MSH|^~\&|OLIS_LIS|LIFELABS_ON|OLIS|ON_EHIS|20260509113000||ORU^R01^ORU_R01|OL000002|P|2.5
PID|||9876543210^^^ON_HN^JHN||O'Brien^Seamus^Patrick||19780105|M|||45 Charles St E^^Toronto^ON^M4Y 1S2^CA||^PRN^PH^^1^416^9251234
ORC|RE|OL100002|OL200002||CM||||20260509073000|||99012^Kim^Grace^^^Dr.^^MD
OBR|1|OL100002|OL200002|24323-8^CMP^LN|||20260509070000|||||||||99012^Kim^Grace^^^Dr.^^MD||||||20260509110000|||F
OBX|1|NM|2345-7^Glucose^LN||5.2|mmol/L|3.3-5.5|N|||F
OBX|2|NM|2160-0^Creatinine^LN||88|umol/L|62-115|N|||F
OBX|3|NM|3094-0^Urea^LN||5.8|mmol/L|2.5-8.0|N|||F
OBX|4|NM|17861-6^Calcium^LN||2.42|mmol/L|2.10-2.55|N|||F
OBX|5|NM|2951-2^Sodium^LN||141|mmol/L|136-145|N|||F
OBX|6|NM|2823-3^Potassium^LN||4.0|mmol/L|3.5-5.0|N|||F
OBX|7|NM|2075-0^Chloride^LN||103|mmol/L|98-107|N|||F
OBX|8|NM|1963-8^Bicarbonate^LN||25|mmol/L|22-29|N|||F
OBX|9|NM|1742-6^ALT^LN||22|U/L|7-56|N|||F
OBX|10|NM|1920-8^AST^LN||19|U/L|10-40|N|||F
```

---

## 3. ORU^R01 - urinalysis

```
MSH|^~\&|OLIS_LIS|DYNACARE_ON|OLIS|ON_EHIS|20260509140000||ORU^R01^ORU_R01|OL000003|P|2.5
PID|||5678901234^^^ON_HN^JHN||Patel^Ravi^Kumar||19880912|M|||150 Main St E^^Hamilton^ON^L8N 1G9^CA||^PRN^PH^^1^905^5289876
ORC|RE|OL100003|OL200003||CM||||20260509090000|||77123^Anderson^Michael^^^Dr.^^MD
OBR|1|OL100003|OL200003|24356-8^Urinalysis complete^LN|||20260509084500|||||||||77123^Anderson^Michael^^^Dr.^^MD||||||20260509133000|||F
OBX|1|CWE|5767-9^Appearance^LN||Hazy^^L||||||F
OBX|2|CWE|5778-6^Color^LN||Amber^^L||||||F
OBX|3|NM|2756-5^pH^LN||5.5||5.0-8.0|N|||F
OBX|4|NM|2965-2^Specific gravity^LN||1.025||1.005-1.030|N|||F
OBX|5|CWE|5792-7^Glucose UA^LN||Negative^^L||||||F
OBX|6|CWE|5804-0^Protein UA^LN||Trace^^L||Negative|A|||F
OBX|7|CWE|20405-7^Leukocyte esterase^LN||1+^^L||Negative|A|||F
OBX|8|CWE|5802-4^Nitrite^LN||Positive^^L||Negative|A|||F
NTE|1||Suggest urine culture to rule out UTI.
```

---

## 4. ORU^R01 - urine culture result

```
MSH|^~\&|OLIS_LIS|TORONTO_GEN|OLIS|ON_EHIS|20260511093000||ORU^R01^ORU_R01|OL000004|P|2.5
PID|||5678901234^^^ON_HN^JHN||Patel^Ravi^Kumar||19880912|M|||150 Main St E^^Hamilton^ON^L8N 1G9^CA||^PRN^PH^^1^905^5289876
ORC|RE|OL100004|OL200004||CM||||20260509100000|||77123^Anderson^Michael^^^Dr.^^MD
OBR|1|OL100004|OL200004|630-4^Urine culture^LN|||20260509100000|||||||||77123^Anderson^Michael^^^Dr.^^MD||||||20260511090000|||F
OBX|1|CWE|600-7^Bacteria identified^LN||112283007^Escherichia coli^SCT||||||F
OBX|2|ST|564-5^Colony count^LN||Greater than 100,000 CFU/mL||||||F
OBX|3|ST|18907-6^Susceptibility Ampicillin^LN||Resistant||||||F
OBX|4|ST|18945-6^Susceptibility Ciprofloxacin^LN||Susceptible||||||F
OBX|5|ST|18993-6^Susceptibility Nitrofurantoin^LN||Susceptible||||||F
OBX|6|ST|18961-3^Susceptibility TMP-SMX^LN||Resistant||||||F
```

---

## 5. ORU^R01 - lipid panel

```
MSH|^~\&|OLIS_LIS|LIFELABS_ON|OLIS|ON_EHIS|20260510080000||ORU^R01^ORU_R01|OL000005|P|2.5
PID|||3456789012^^^ON_HN^JHN||Williams^David^Anthony||19550718|M|||88 Dunlop St W^^Barrie^ON^L4N 1A4^CA||^PRN^PH^^1^705^7251234
ORC|RE|OL100005|OL200005||CM||||20260510060000|||66234^Wright^Patricia^^^Dr.^^MD
OBR|1|OL100005|OL200005|24331-1^Lipid panel^LN|||20260510055000|||||||||66234^Wright^Patricia^^^Dr.^^MD||||||20260510073000|||F
OBX|1|NM|2093-3^Cholesterol total^LN||6.2|mmol/L|0.0-5.2|H|||F
OBX|2|NM|2571-8^Triglycerides^LN||2.1|mmol/L|0.0-1.7|H|||F
OBX|3|NM|2085-9^HDL Cholesterol^LN||1.1|mmol/L|1.0-999.0|N|||F
OBX|4|NM|13457-7^LDL Cholesterol calculated^LN||4.1|mmol/L|0.0-3.4|H|||F
OBX|5|NM|9830-1^Total/HDL ratio^LN||5.6||0.0-5.0|H|||F
```

---

## 6. ORU^R01 - HbA1c

```
MSH|^~\&|OLIS_LIS|DYNACARE_ON|OLIS|ON_EHIS|20260510100000||ORU^R01^ORU_R01|OL000006|P|2.5
PID|||3456789012^^^ON_HN^JHN||Williams^David^Anthony||19550718|M|||88 Dunlop St W^^Barrie^ON^L4N 1A4^CA||^PRN^PH^^1^705^7251234
ORC|RE|OL100006|OL200006||CM||||20260510060000|||66234^Wright^Patricia^^^Dr.^^MD
OBR|1|OL100006|OL200006|4548-4^HbA1c^LN|||20260510055000|||||||||66234^Wright^Patricia^^^Dr.^^MD||||||20260510093000|||F
OBX|1|NM|4548-4^Hemoglobin A1c^LN||7.8|%|4.0-6.0|H|||F
OBX|2|NM|59261-8^HbA1c IFCC^LN||62|mmol/mol|20-42|H|||F
NTE|1||Above target. Consider intensification of diabetes management.
```

---

## 7. ORU^R01 - thyroid panel

```
MSH|^~\&|OLIS_LIS|LIFELABS_ON|OLIS|ON_EHIS|20260510143000||ORU^R01^ORU_R01|OL000007|P|2.5
PID|||1234567890^^^ON_HN^JHN||Singh^Amrit^Kaur||19650420|F|||300 Bloor St W^^Toronto^ON^M5S 1W3^CA||^PRN^PH^^1^416^7891234
ORC|RE|OL100007|OL200007||CM||||20260510080000|||88901^Martinez^Carlos^^^Dr.^^MD
OBR|1|OL100007|OL200007|34896-2^Thyroid panel^LN|||20260510074500|||||||||88901^Martinez^Carlos^^^Dr.^^MD||||||20260510140000|||F
OBX|1|NM|3016-3^TSH^LN||2.4|mIU/L|0.4-4.0|N|||F
OBX|2|NM|3024-7^Free T4^LN||15.8|pmol/L|10.0-25.0|N|||F
```

---

## 8. ORU^R01 - prenatal screen (maternal serum)

```
MSH|^~\&|LAB_SYS|MT_SINAI_LAB|OLIS|ON_EHIS|20260511090000||ORU^R01^ORU_R01|OL000008|P|2.3
PID|||7654321098^^^ON_HN^JHN||Chen^Mei^Lin||19920601|F|||52 Gerrard St E^^Toronto^ON^M5B 1G3^CA||^PRN^PH^^1^416^5551234
ORC|RE|OL100008|OL200008||CM||||20260510090000|||44567^Hughes^Jennifer^^^Dr.^^MD
OBR|1|OL100008|OL200008|21482-5^Enhanced FTS^LN|||20260510084500|||||||||44567^Hughes^Jennifer^^^Dr.^^MD||||||20260511083000|||F
OBX|1|NM|33629-2^AFP MoM^LN||1.02|MoM|0.50-2.50|N|||F
OBX|2|NM|19080-1^hCG^LN||45000|IU/L|||||F
OBX|3|NM|49246-2^PAPP-A MoM^LN||0.85|MoM|||||F
OBX|4|ST|99999-9^Risk assessment^LOCAL||Down syndrome risk: 1 in 8500 (screen negative). Trisomy 18 risk: 1 in 25000 (screen negative).||||||F
```

---

## 9. ORU^R01 - COVID-19 PCR result

```
MSH|^~\&|OLIS_LIS|PHO_LAB|OLIS|ON_EHIS|20260509160000||ORU^R01^ORU_R01|OL000009|P|2.5
PID|||2345678901^^^ON_HN^JHN||Fernandez^Maria^Elena||19750314|F|||200 King St W^^Kitchener^ON^N2G 4V2^CA||^PRN^PH^^1^519^5789012
ORC|RE|OL100009|OL200009||CM||||20260509080000|||55678^Brown^Thomas^^^Dr.^^MD
OBR|1|OL100009|OL200009|94500-6^SARS-CoV-2 RNA NAA^LN|||20260509074500|||||||||55678^Brown^Thomas^^^Dr.^^MD||||||20260509153000|||F
OBX|1|CWE|94500-6^SARS-CoV-2 RNA^LN||260415000^Not detected^SCT||||||F
```

---

## 10. ORU^R01 - microbiology blood culture

```
MSH|^~\&|OLIS_LIS|OTTAWA_GEN|OLIS|ON_EHIS|20260511160000||ORU^R01^ORU_R01|OL000010|P|2.5
PID|||8765432109^^^ON_HN^JHN||Lebrun^Jacques^Henri||19450822|M|||101 Rideau St^^Ottawa^ON^K1N 5X1^CA||^PRN^PH^^1^613^5551234
ORC|RE|OL100010|OL200010||CM||||20260509140000|||33789^Nguyen^Thanh^^^Dr.^^MD
OBR|1|OL100010|OL200010|87040-2^Blood culture^LN|||20260509134500|||||||||33789^Nguyen^Thanh^^^Dr.^^MD||||||20260511153000|||F
OBX|1|CWE|600-7^Bacteria identified^LN||3092008^Staphylococcus aureus^SCT||||||F
OBX|2|ST|18900-1^Susceptibility Oxacillin^LN||Susceptible (MSSA)||||||F
OBX|3|ST|18964-7^Susceptibility Vancomycin^LN||Susceptible MIC 1 ug/mL||||||F
OBX|4|ST|18878-9^Susceptibility Clindamycin^LN||Susceptible||||||F
OBX|5|ST|18886-2^Susceptibility Doxycycline^LN||Susceptible||||||F
```

---

## 11. ORU^R01 - coagulation studies

```
MSH|^~\&|OLIS_LIS|TORONTO_GEN|OLIS|ON_EHIS|20260510110000||ORU^R01^ORU_R01|OL000011|P|2.5
PID|||8765432109^^^ON_HN^JHN||Lebrun^Jacques^Henri||19450822|M|||101 Rideau St^^Ottawa^ON^K1N 5X1^CA||^PRN^PH^^1^613^5551234
ORC|RE|OL100011|OL200011||CM||||20260510070000|||33789^Nguyen^Thanh^^^Dr.^^MD
OBR|1|OL100011|OL200011|38875-1^Coagulation panel^LN|||20260510064500|||||||||33789^Nguyen^Thanh^^^Dr.^^MD||||||20260510103000|||F
OBX|1|NM|5902-2^PT^LN||18.5|seconds|11.0-13.5|H|||F
OBX|2|NM|6301-6^INR^LN||2.3||0.9-1.1|H|||F
OBX|3|NM|3173-2^aPTT^LN||32.0|seconds|25.0-35.0|N|||F
OBX|4|NM|3255-7^Fibrinogen^LN||3.8|g/L|2.0-4.0|N|||F
```

---

## 12. ORU^R01 - iron studies

```
MSH|^~\&|OLIS_LIS|LIFELABS_ON|OLIS|ON_EHIS|20260511100000||ORU^R01^ORU_R01|OL000012|P|2.5
PID|||1234567890^^^ON_HN^JHN||Singh^Amrit^Kaur||19650420|F|||300 Bloor St W^^Toronto^ON^M5S 1W3^CA||^PRN^PH^^1^416^7891234
ORC|RE|OL100012|OL200012||CM||||20260511070000|||88901^Martinez^Carlos^^^Dr.^^MD
OBR|1|OL100012|OL200012|2500-7^Iron panel^LN|||20260511064500|||||||||88901^Martinez^Carlos^^^Dr.^^MD||||||20260511093000|||F
OBX|1|NM|2498-4^Iron^LN||8|umol/L|9-30|L|||F
OBX|2|NM|2502-3^Transferrin saturation^LN||12|%|20-50|L|||F
OBX|3|NM|2276-4^Ferritin^LN||10|ug/L|12-150|L|||F
OBX|4|NM|3034-6^TIBC^LN||78|umol/L|45-72|H|||F
NTE|1||Iron deficiency pattern. Correlate clinically.
```

---

## 13. ORU^R01 - PSA result

```
MSH|^~\&|OLIS_LIS|DYNACARE_ON|OLIS|ON_EHIS|20260510153000||ORU^R01^ORU_R01|OL000013|P|2.5
PID|||9876543210^^^ON_HN^JHN||O'Brien^Seamus^Patrick||19780105|M|||45 Charles St E^^Toronto^ON^M4Y 1S2^CA||^PRN^PH^^1^416^9251234
ORC|RE|OL100013|OL200013||CM||||20260510073000|||99012^Kim^Grace^^^Dr.^^MD
OBR|1|OL100013|OL200013|2857-1^PSA^LN|||20260510070000|||||||||99012^Kim^Grace^^^Dr.^^MD||||||20260510150000|||F
OBX|1|NM|2857-1^PSA^LN||1.8|ug/L|0.0-4.0|N|||F
```

---

## 14. ORU^R01 - hepatitis B serology

```
MSH|^~\&|OLIS_LIS|PHO_LAB|OLIS|ON_EHIS|20260511140000||ORU^R01^ORU_R01|OL000014|P|2.5
PID|||2345678901^^^ON_HN^JHN||Fernandez^Maria^Elena||19750314|F|||200 King St W^^Kitchener^ON^N2G 4V2^CA||^PRN^PH^^1^519^5789012
ORC|RE|OL100014|OL200014||CM||||20260511080000|||55678^Brown^Thomas^^^Dr.^^MD
OBR|1|OL100014|OL200014|24360-0^Hepatitis B panel^LN|||20260511074500|||||||||55678^Brown^Thomas^^^Dr.^^MD||||||20260511133000|||F
OBX|1|CWE|5195-3^HBsAg^LN||260385009^Negative^SCT||||||F
OBX|2|CWE|16935-9^Anti-HBs^LN||260373001^Positive^SCT||||||F
OBX|3|NM|16935-9^Anti-HBs quantitative^LN||450|mIU/mL|10-999|N|||F
OBX|4|CWE|22322-2^Anti-HBc total^LN||260385009^Negative^SCT||||||F
```

---

## 15. ORU^R01 - vitamin D

```
MSH|^~\&|OLIS_LIS|LIFELABS_ON|OLIS|ON_EHIS|20260510160000||ORU^R01^ORU_R01|OL000015|P|2.5
PID|||1234567890^^^ON_HN^JHN||Singh^Amrit^Kaur||19650420|F|||300 Bloor St W^^Toronto^ON^M5S 1W3^CA||^PRN^PH^^1^416^7891234
ORC|RE|OL100015|OL200015||CM||||20260510080000|||88901^Martinez^Carlos^^^Dr.^^MD
OBR|1|OL100015|OL200015|1989-3^25-Hydroxyvitamin D^LN|||20260510074500|||||||||88901^Martinez^Carlos^^^Dr.^^MD||||||20260510153000|||F
OBX|1|NM|1989-3^25-OH Vitamin D^LN||42|nmol/L|75-250|L|||F
NTE|1||Insufficiency. Supplementation recommended.
```

---

## 16. ORU^R01 - Pap smear cytology with PDF report

```
MSH|^~\&|LAB_SYS|CML_HEALTHCARE|OLIS|ON_EHIS|20260511150000||ORU^R01^ORU_R01|OL000016|P|2.3
PID|||2345678901^^^ON_HN^JHN||Fernandez^Maria^Elena||19750314|F|||200 King St W^^Kitchener^ON^N2G 4V2^CA||^PRN^PH^^1^519^5789012
ORC|RE|OL100016|OL200016||CM||||20260510100000|||55678^Brown^Thomas^^^Dr.^^MD
OBR|1|OL100016|OL200016|10524-7^Cytology cervical^LN|||20260510094500|||||||||55678^Brown^Thomas^^^Dr.^^MD||||||20260511143000|||F
OBX|1|CWE|10524-7^Cervical cytology^LN||373887005^Negative for intraepithelial lesion or malignancy^SCT||||||F
OBX|2|ED|PDF^Cytology Report^CML||^AP^^Base64^JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEPL01lZGlhQm94IFswIDAgNjEyIDc5Ml0K||||||F
```

---

## 17. ORU^R01 - celiac screen

```
MSH|^~\&|OLIS_LIS|TORONTO_GEN|OLIS|ON_EHIS|20260511170000||ORU^R01^ORU_R01|OL000017|P|2.5
PID|||5678901234^^^ON_HN^JHN||Patel^Ravi^Kumar||19880912|M|||150 Main St E^^Hamilton^ON^L8N 1G9^CA||^PRN^PH^^1^905^5289876
ORC|RE|OL100017|OL200017||CM||||20260511090000|||77123^Anderson^Michael^^^Dr.^^MD
OBR|1|OL100017|OL200017|31017-7^tTG IgA^LN|||20260511084500|||||||||77123^Anderson^Michael^^^Dr.^^MD||||||20260511163000|||F
OBX|1|NM|31017-7^tTG IgA^LN||3.2|U/mL|0.0-20.0|N|||F
OBX|2|NM|2458-8^IgA total^LN||2.5|g/L|0.7-4.0|N|||F
```

---

## 18. ORU^R01 - troponin critical result

```
MSH|^~\&|OLIS_LIS|OTTAWA_GEN|OLIS|ON_EHIS|20260512020000||ORU^R01^ORU_R01|OL000018|P|2.5
PID|||8765432109^^^ON_HN^JHN||Lebrun^Jacques^Henri||19450822|M|||101 Rideau St^^Ottawa^ON^K1N 5X1^CA||^PRN^PH^^1^613^5551234
ORC|RE|OL100018|OL200018||CM||||20260512010000|||33789^Nguyen^Thanh^^^Dr.^^MD
OBR|1|OL100018|OL200018|49563-0^Troponin I hs^LN|||20260512005000|||||||||33789^Nguyen^Thanh^^^Dr.^^MD||||||20260512015000|||F
OBX|1|NM|49563-0^hs-Troponin I^LN||256|ng/L|0-26|HH|||F
NTE|1||Critical value. Physician notified 0155h.
```

---

## 19. ORU^R01 - histopathology with embedded JPEG image

```
MSH|^~\&|LAB_SYS|UHN_PATH_LAB|OLIS|ON_EHIS|20260512100000||ORU^R01^ORU_R01|OL000019|P|2.3
PID|||9876543210^^^ON_HN^JHN||O'Brien^Seamus^Patrick||19780105|M|||45 Charles St E^^Toronto^ON^M4Y 1S2^CA||^PRN^PH^^1^416^9251234
ORC|RE|OL100019|OL200019||CM||||20260510140000|||99012^Kim^Grace^^^Dr.^^MD
OBR|1|OL100019|OL200019|88305-8^Surgical pathology^LN|||20260510134500|||||||||99012^Kim^Grace^^^Dr.^^MD||||||20260512093000|||F
OBX|1|FT|88305-8^Path interpretation^LN||Colon biopsy: Tubular adenoma with low-grade dysplasia. Margins clear. No invasive carcinoma.||||||F
OBX|2|ED|IMG^Histopathology Slide^UHN||^IM^JPEG^Base64^/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgo||||||F
```

---

## 20. ORU^R01 - drug screen panel

```
MSH|^~\&|OLIS_LIS|DYNACARE_ON|OLIS|ON_EHIS|20260512130000||ORU^R01^ORU_R01|OL000020|P|2.5
PID|||5678901234^^^ON_HN^JHN||Patel^Ravi^Kumar||19880912|M|||150 Main St E^^Hamilton^ON^L8N 1G9^CA||^PRN^PH^^1^905^5289876
ORC|RE|OL100020|OL200020||CM||||20260512080000|||77123^Anderson^Michael^^^Dr.^^MD
OBR|1|OL100020|OL200020|3393-5^Urine drug screen^LN|||20260512074500|||||||||77123^Anderson^Michael^^^Dr.^^MD||||||20260512123000|||F
OBX|1|CWE|3397-6^Cocaine metabolites^LN||260385009^Negative^SCT||||||F
OBX|2|CWE|3426-3^Opiates^LN||260385009^Negative^SCT||||||F
OBX|3|CWE|3416-4^THC^LN||260385009^Negative^SCT||||||F
OBX|4|CWE|3390-1^Benzodiazepines^LN||260385009^Negative^SCT||||||F
OBX|5|CWE|3349-7^Amphetamines^LN||260385009^Negative^SCT||||||F
OBX|6|CWE|19659-2^Fentanyl^LN||260385009^Negative^SCT||||||F
```
